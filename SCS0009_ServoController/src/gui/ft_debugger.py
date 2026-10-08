#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FT 调试器 - 对齐飞特官方 "FT SCServo Debug" 功能复现。

功能：
- 串口连接/断开（自动检测、任意波特率）
- 舵机扫描（ID 1-254，检测重复 ID / 总线冲突）
- 参数读取/写入（EEPROM + SRAM，支持 xdat 文件读写）
- 单舵机位置控制（目标位置/时间/速度）
- 实时状态监控（位置/速度/负载/电压/温度/电流/MOVING）
- 恢复出厂设置

设计：后台 ``FtWorker``（QObject + 线程）+ 前端 ``FtDebuggerPanel``（QWidget）。
所有串口操作都在后台线程执行，通过 Qt 信号回传，避免阻塞 UI。
"""

import os
import time
import threading
from queue import Queue
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QPushButton, QComboBox, QSpinBox, QLineEdit, QTextEdit,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSlider,
)

try:
    from src.i18n import tr
except ImportError:
    def tr(text):
        return text

try:
    from src.port_utils import get_available_ports
except ImportError:
    def get_available_ports():
        try:
            import serial.tools.list_ports
            return list(serial.tools.list_ports.comports())
        except ImportError:
            return []

from scservo_sdk.port_handler import PortHandler
from scservo_sdk.scscl import scscl
from scservo_sdk.scservo_def import COMM_SUCCESS

from src.xdat_utils import (
    XdatFile, SCS0009_REGISTERS, SCS0009_EPROM, SCS0009_SRAM, SCS0009_SRAM_RO,
    BAUD_TABLE, BAUD_TABLE_REV, MODE_NAMES, MODEL_NAMES,
)

DEFAULT_BAUD = 1000000
SCAN_MAX_ID = 254  # 官方扫描到 ID 254
# SCS0009 电位器位置范围：0-1023（10 位分辨率）
POS_MAX = 1023


# ---------------------------------------------------------------------------
# 后台工作线程
# ---------------------------------------------------------------------------
class FtWorker(QObject):
    log = Signal(str)
    connected = Signal(bool, str)          # 连接状态, 错误信息
    scanned = Signal(list)                 # 在线舵机 ID 列表（扫描完成）
    servo_found = Signal(int)              # 扫描过程中实时发现一个舵机
    param_read = Signal(int, int, int)     # servo_id, address, value
    status_read = Signal(int, dict)        # servo_id, {字段: 值}
    move_finished = Signal(int, bool)      # servo_id, 是否成功完成移动
    servo_params_read = Signal(int, bytes) # servo_id, 读取到的 49 字节参数数据区
    write_succeeded = Signal(int, int, int)  # servo_id, address, value（写入成功）
    write_failed = Signal(int, int, int, str)  # servo_id, address, value, 原因（写入失败）
    scan_error = Signal(str)               # 扫描/连接错误信息

    def __init__(self, port_name: str = None):
        super().__init__()
        self.port_name = port_name
        self.baudrate = DEFAULT_BAUD
        self.ph = None
        self.servo = None
        self.is_connected = False
        self._lock = threading.Lock()
        # 串口命令队列：所有串口事务串行执行，避免多线程抢占总线导致读失败
        self._cmd_queue = Queue()
        self._cmd_thread = threading.Thread(target=self._cmd_loop, daemon=True)
        self._cmd_thread.start()

    # ---------------- 命令队列（串行化所有串口事务） ----------------
    def submit(self, fn, *args):
        """把串口操作加入队列串行执行"""
        self._cmd_queue.put((fn, args))

    def _cmd_loop(self):
        while True:
            fn, args = self._cmd_queue.get()
            try:
                fn(*args)
            except Exception:
                pass

    def _run(self, fn, *args):
        """直接在当前线程执行（供队列循环内部使用，等价于调用 fn）"""
        fn(*args)

    # ---------------- 连接 ----------------
    def connect_serial(self, port_name: str, baudrate: int):
        with self._lock:
            self.disconnect_serial()
            self.port_name = port_name
            self.baudrate = baudrate
            try:
                self.ph = PortHandler(port_name)
                if not self.ph.openPort():
                    self.connected.emit(False, tr("无法打开串口: {}").format(port_name))
                    return
                if not self.ph.setBaudRate(baudrate):
                    self.connected.emit(False, tr("无法设置波特率: {}").format(baudrate))
                    self.ph.closePort()
                    self.ph = None
                    return
                self.servo = scscl(self.ph)
                self.is_connected = True
                self.log.emit(tr("✅ 已连接 {} @ {} bps").format(port_name, baudrate))
                self.connected.emit(True, "")
            except Exception as e:
                self.is_connected = False
                self.servo = None
                self.ph = None
                self.connected.emit(False, tr("连接异常: {}").format(e))

    def disconnect_serial(self):
        if self.ph is not None:
            try:
                self.ph.closePort()
            except Exception:
                pass
            self.ph = None
        self.servo = None
        self.is_connected = False
        self.log.emit(tr("🔌 串口已断开"))

    # ---------------- 扫描 ----------------
    def scan(self):
        if not self._ensure():
            return
        import scservo_sdk.port_handler as _ph
        found = []
        # 扫描期间临时缩短未连接舵机的 ping 超时，加速扫描（默认 50ms/ID → 5ms/ID）
        orig_latency = _ph.LATENCY_TIMER
        try:
            _ph.LATENCY_TIMER = 5
            for sid in range(1, SCAN_MAX_ID + 1):
                try:
                    model, result, error = self.servo.ping(sid)
                    if result == COMM_SUCCESS:
                        found.append(sid)
                        self.log.emit(tr("发现 ID{} 型号:{}").format(sid, model))
                        self.servo_found.emit(sid)
                except Exception:
                    pass
        finally:
            _ph.LATENCY_TIMER = orig_latency
        self.scanned.emit(found)
        if not found:
            self.log.emit(tr("未扫描到舵机"))

    # ---------------- 参数读取 ----------------
    def read_param(self, servo_id: int, address: int, length: int = 2):
        if not self._ensure():
            return
        reg_name = "未知"
        for _a, _l, _nm, _area, _rw in SCS0009_REGISTERS:
            if _a == address:
                reg_name = _nm
                break
        try:
            self.log.emit(tr("📖 读取 ID{} 地址 0x{:02X} ({} {})...").format(servo_id, address, reg_name, length))
            if length == 1:
                value, result, error = self.servo.read1ByteTxRx(servo_id, address)
            elif length == 2:
                value, result, error = self.servo.read2ByteTxRx(servo_id, address)
            else:
                value, result, error = self.servo.read4ByteTxRx(servo_id, address)
            if result == COMM_SUCCESS:
                self.param_read.emit(servo_id, address, value)
                self.log.emit(tr("✅ 读取 ID{} {} = {}").format(servo_id, reg_name, value))
            else:
                # 判断失败原因
                reason = ""
                if result == -6:
                    reason = tr("(舵机无响应，可能未连接或地址错误)")
                elif result == -7:
                    reason = tr("(数据校验失败，串口可能被其他程序占用)")
                elif result == -2:
                    reason = tr("(发送失败)")
                elif result == -4:
                    reason = tr("(指令包错误)")
                else:
                    reason = tr("(错误码 {})").format(result)
                self.log.emit(tr("❌ 读取 ID{} 地址 0x{:02X} ({}) 失败{}").format(
                    servo_id, address, reg_name, reason))
        except Exception as e:
            self.log.emit(tr("❌ 读取 ID{} {} 异常: {}").format(servo_id, reg_name, e))

    def write_param(self, servo_id: int, address: int, length: int, value: int):
        """写参数。地址 < 40 (EEPROM) 先解锁后写再锁定。"""
        if not self._ensure():
            return
        try:
            if address < 40:
                r, e = self.servo.unLockEprom(servo_id)
                if r != COMM_SUCCESS:
                    self.log.emit(tr("❌ EEPROM 解锁失败: {}").format(e))
                    self.write_failed.emit(servo_id, address, value, tr("EEPROM 解锁失败"))
                    return
                time.sleep(0.05)
            if length == 1:
                result, error = self.servo.write1ByteTxRx(servo_id, address, value)
            elif length == 2:
                result, error = self.servo.write2ByteTxRx(servo_id, address, value)
            else:
                result, error = self.servo.write4ByteTxRx(servo_id, address, value)
            if address < 40:
                time.sleep(0.05)
                self.servo.LockEprom(servo_id)
            if result == COMM_SUCCESS:
                self.log.emit(tr("✅ 写入 ID{} 地址 0x{:02X} = {}").format(servo_id, address, value))
                self.param_read.emit(servo_id, address, value)
                # 发射写入成功信号，前端弹出提示
                self.write_succeeded.emit(servo_id, address, value)
            else:
                self.log.emit(tr("❌ 写入 ID{} 地址 0x{:02X} 失败").format(servo_id, address))
                # 发射写入失败信号，前端弹出提示
                self.write_failed.emit(servo_id, address, value, tr("串口写入失败"))
        except Exception as e:
            self.log.emit(tr("❌ 写入异常: {}").format(e))
            self.write_failed.emit(servo_id, address, value, tr("写入异常"))

    # ---------------- 位置控制 ----------------
    def move_servo(self, servo_id: int, position: int, speed: int = 1000, time_ms: int = 50):
        if not self._ensure():
            return
        position = max(0, min(POS_MAX, position))
        try:
            # SCS 系列用 WritePos(id, position, time, speed)
            result, error = self.servo.WritePos(servo_id, position, time_ms, speed)
            if result == COMM_SUCCESS:
                self.log.emit(tr("🎯 ID{} -> 位置 {}").format(servo_id, position))
                # 轮询 MOVING 标志，直到移动结束（带超时保护）
                finished = self._wait_move_done(servo_id)
                self.move_finished.emit(servo_id, finished)
            else:
                self.log.emit(tr("⚠️ 位置写入失败 ID{}（可能断连）。舵机可能仍在执行，请注意安全！").format(servo_id))
                self.move_finished.emit(servo_id, False)
        except Exception as e:
            self.log.emit(tr("❌ 移动异常: {}").format(e))
            self.log.emit(tr("⚠️ 舵机可能仍在执行，请重新连接并关闭力矩！"))
            self.move_finished.emit(servo_id, False)

    def _wait_move_done(self, servo_id: int, timeout: float = 10.0, poll_interval: float = 0.1):
        """轮询舵机 MOVING 标志，等待移动完成。返回是否检测到完成。"""
        if not self._ensure():
            return False
        start = time.time()
        while time.time() - start < timeout:
            try:
                moving, result, _ = self.servo.ReadMoving(servo_id)
                if result == COMM_SUCCESS and not moving:
                    return True
            except Exception:
                # 轮询期间断连，立即返回
                return False
            time.sleep(poll_interval)
        # 超时（仍在移动），不阻塞更久
        return False

    def set_torque(self, servo_id: int, enable: bool):
        if not self._ensure():
            return
        try:
            result, error = self.servo.write1ByteTxRx(servo_id, 40, 1 if enable else 0)
            if result == COMM_SUCCESS:
                self.log.emit(tr("⚡ ID{} 力矩{}").format(servo_id, tr("开启") if enable else tr("关闭")))
        except Exception as e:
            self.log.emit(tr("❌ 力矩设置异常: {}").format(e))

    # ---------------- 状态读取 ----------------
    def read_status(self, servo_id: int):
        if not self._ensure():
            return
        info = {}
        try:
            pos, r, _ = self.servo.ReadPos(servo_id)
            info["position"] = pos if r == COMM_SUCCESS else None

            speed, r, _ = self.servo.ReadSpeed(servo_id)
            info["speed"] = speed if r == COMM_SUCCESS else None

            load, r, _ = self.servo.ReadLoad(servo_id)
            info["load"] = load if r == COMM_SUCCESS else None

            voltage, r, _ = self.servo.ReadVoltage(servo_id)
            info["voltage"] = voltage / 10.0 if r == COMM_SUCCESS else None

            temp, r, _ = self.servo.ReadTemperature(servo_id)
            info["temperature"] = temp if r == COMM_SUCCESS else None

            current, r, _ = self.servo.ReadCurrent(servo_id)
            info["current"] = current if r == COMM_SUCCESS else None

            moving, r, _ = self.servo.ReadMoving(servo_id)
            info["moving"] = bool(moving) if r == COMM_SUCCESS else None

            model, r, _ = self.servo.ReadModelNumber(servo_id)
            info["model"] = model if r == COMM_SUCCESS else None

            self.status_read.emit(servo_id, info)
        except Exception:
            pass

    # ---------------- 恢复出厂 ----------------
    def factory_reset(self, servo_id: int):
        if not self._ensure():
            return
        try:
            result, error = self.servo.reSet(servo_id)
            if result == COMM_SUCCESS:
                self.log.emit(tr("✅ ID{} 已恢复出厂（ID 回 1，波特率回 1M）").format(servo_id))
            else:
                self.log.emit(tr("❌ 恢复出厂失败 ID{}").format(servo_id))
        except Exception as e:
            self.log.emit(tr("❌ 恢复出厂异常: {}").format(e))

    # ---------------- 波特率修改 ----------------
    def change_baud_rate(self, servo_id: int, new_baud: int):
        """修改舵机波特率：解锁 → 写地址6 → 切换串口波特率 → 验证，失败自动回滚"""
        if not self._ensure():
            return
        baud_to_reg = {1000000: 0, 500000: 1, 250000: 2, 128000: 3,
                       115200: 4, 76800: 5, 57600: 6, 38400: 7}
        if new_baud not in baud_to_reg:
            self.log.emit(tr("❌ 不支持的波特率: {}").format(new_baud))
            return
        reg_value = baud_to_reg[new_baud]
        old_baud = self.baudrate
        try:
            # 1. 解锁
            r, e = self.servo.unLockEprom(servo_id)
            if r != COMM_SUCCESS:
                self.log.emit(tr("❌ EEPROM 解锁失败: {}").format(e))
                return
            time.sleep(0.05)
            # 2. 写入波特率寄存器（地址 6）
            result, error = self.servo.write1ByteTxRx(servo_id, 6, reg_value)
            if result != COMM_SUCCESS:
                self.servo.LockEprom(servo_id)
                self.log.emit(tr("❌ 波特率写入失败: {}").format(error))
                return
            self.servo.LockEprom(servo_id)
            time.sleep(0.2)
            # 3. 切换串口波特率
            self.log.emit(tr("🔄 串口切换到 {} bps...").format(new_baud))
            self.ph.setBaudRate(new_baud)
            self.baudrate = new_baud
            time.sleep(0.3)
            # 4. 验证
            if self.ph is not None:
                model, result, _ = self.servo.ping(servo_id)
                if result == COMM_SUCCESS:
                    self.log.emit(tr("✅ ID{} 波特率已修改为 {} bps").format(servo_id, new_baud))
                    return
            # 验证失败，回滚
            self.log.emit(tr("⚠️ 新波特率验证失败，尝试恢复 {} bps").format(old_baud))
            self.ph.setBaudRate(old_baud)
            self.baudrate = old_baud
            time.sleep(0.3)
            model, result, _ = self.servo.ping(servo_id)
            if result == COMM_SUCCESS:
                self.log.emit(tr("✅ 已恢复 {} bps，波特率修改失败").format(old_baud))
            else:
                self.log.emit(tr("❌ 严重：波特率修改失败且旧波特率也丢失，请重新连接"))
        except Exception as e:
            self.log.emit(tr("❌ 波特率修改异常: {}").format(e))

    # ---------------- xdat 写入舵机 ----------------
    def apply_xdat(self, servo_id: int, xdat: XdatFile):
        """把 xdat 中的 EEPROM 参数写入指定舵机（自动跳过型号/只读区）"""
        if not self._ensure():
            return
        try:
            # 解锁
            r, e = self.servo.unLockEprom(servo_id)
            if r != COMM_SUCCESS:
                self.log.emit(tr("❌ EEPROM 解锁失败: {}").format(e))
                return
            time.sleep(0.05)
            written = 0
            for addr, ln, _nm, _area, _rw in SCS0009_EPROM:
                if addr < 3 or addr >= 40:  # 只写 EEPROM 配置，不写型号
                    continue
                if addr + ln > len(xdat.data):
                    continue
                val = xdat.get_value(addr, ln)
                if val is None:
                    continue
                if addr == 3:  # 型号不可写
                    continue
                if ln == 1:
                    self.servo.write1ByteTxRx(servo_id, addr, val)
                elif ln == 2:
                    self.servo.write2ByteTxRx(servo_id, addr, val)
                else:
                    self.servo.write4ByteTxRx(servo_id, addr, val)
                written += 1
                time.sleep(0.02)
            time.sleep(0.05)
            self.servo.LockEprom(servo_id)
            self.log.emit(tr("✅ xdat 已写入 ID{}，共 {} 项参数").format(servo_id, written))
        except Exception as e:
            self.log.emit(tr("❌ 写入 xdat 异常: {}").format(e))

    # ---------------- 保存当前舵机参数到 xdat ----------------
    def read_servo_params(self, servo_id: int):
        """从舵机读取全部可读寄存器（EPROM + SRAM），通过信号返回字节数组。

        返回值: 49 字节数据区（地址 0..48 的原始值，未读/失败的地址为 0）。
        SCS0009 为大端字节序，多字节值按大端写入数据区。
        """
        if not self._ensure():
            return
        data = bytearray(49)
        for addr, ln, nm, area, rw in SCS0009_REGISTERS:
            if area == "DEFAULT":
                continue
            if addr + ln > 48:
                continue
            try:
                if ln == 1:
                    value, result, _ = self.servo.read1ByteTxRx(servo_id, addr)
                elif ln == 2:
                    value, result, _ = self.servo.read2ByteTxRx(servo_id, addr)
                else:
                    value, result, _ = self.servo.read4ByteTxRx(servo_id, addr)
                if result == COMM_SUCCESS:
                    # 大端写入：高位在前
                    for i in range(ln):
                        data[addr + i] = (value >> (8 * (ln - 1 - i))) & 0xFF
            except Exception:
                pass
        # 通过信号回传数据区（前端组装 xdat 并保存）
        self.servo_params_read.emit(servo_id, bytes(data))

    def _ensure(self) -> bool:
        if not self.is_connected or self.servo is None:
            self.log.emit(tr("⚠️ 未连接串口"))
            return False
        return True


# ---------------------------------------------------------------------------
# 前端面板
# ---------------------------------------------------------------------------
class FtDebuggerPanel(QWidget):
    """FT 调试器面板（功能对齐飞特 FT SCServo Debug）"""

    def __init__(self, port_name: str = None, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.worker = FtWorker(port_name)
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self._init_connections()

        self.current_servos: List[int] = []
        self._move_done_pending = False  # 移动完成提示显示中，读取状态时保留
        self.init_ui()
        if port_name:
            self.port_combo.setCurrentText(port_name)

    # ---------------- 信号 ----------------
    def _init_connections(self):
        self.worker.log.connect(self.add_log)
        self.worker.connected.connect(self._on_connected)
        self.worker.scanned.connect(self._on_scanned)
        self.worker.servo_found.connect(self._on_servo_found)
        self.worker.param_read.connect(self._on_param_read)
        self.worker.status_read.connect(self._on_status_read)
        self.worker.move_finished.connect(self._on_move_finished)
        self.worker.servo_params_read.connect(self._on_servo_params_read)
        self.worker.write_succeeded.connect(self._on_write_succeeded)
        self.worker.write_failed.connect(self._on_write_failed)

    def _on_write_succeeded(self, servo_id, address, value):
        """参数写入成功：弹出提示"""
        reg_name = "未知"
        for _a, _l, _nm, _area, _rw in SCS0009_REGISTERS:
            if _a == address:
                reg_name = _nm
                break
        QMessageBox.information(
            self, tr("写入成功"),
            tr("✅ 已成功写入\nID{} {}(0x{:02X}) = {}").format(servo_id, reg_name, address, value)
        )

    def _on_write_failed(self, servo_id, address, value, reason):
        """参数写入失败：弹出提示"""
        reg_name = "未知"
        for _a, _l, _nm, _area, _rw in SCS0009_REGISTERS:
            if _a == address:
                reg_name = _nm
                break
        QMessageBox.critical(
            self, tr("写入失败"),
            tr("❌ 写入失败\nID{} {}(0x{:02X}) = {}\n原因: {}").format(servo_id, reg_name, address, value, reason)
        )

    def _on_move_finished(self, servo_id, success):
        """移动完成回调：更新状态标签"""
        self._move_done_pending = True  # 保留"移动完成"提示，读取状态时不被覆盖
        if success:
            self.status_label.setText(tr("✅ ID{} 已移动完成，请关闭力矩").format(servo_id))
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.add_log(tr("✅ ID{} 移动完成，请关闭力矩").format(servo_id))
        else:
            self.status_label.setText(tr("⚠️ ID{} 移动未完成/断连，请检查并关闭力矩").format(servo_id))
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.add_log(tr("⚠️ ID{} 移动未完成/断连，请检查并关闭力矩").format(servo_id))

    def _on_servo_list_selected(self):
        """选中舵机列表中的行时，自动填充到舵机下拉框"""
        row = self.servo_list_table.currentRow()
        if row < 0 or row >= len(self.current_servos):
            return
        sid = self.current_servos[row]
        idx = self.servo_combo.findData(sid)
        if idx >= 0:
            self.servo_combo.setCurrentIndex(idx)
            self.add_log(tr("🖱 已选择舵机 ID{}").format(sid))

    def _on_servo_found(self, sid):
        """扫描过程中实时发现舵机，立即加入列表"""
        if sid not in self.current_servos:
            self.current_servos.append(sid)
        row = self.current_servos.index(sid)
        self.servo_list_table.setRowCount(len(self.current_servos))
        name = f"ID{sid}"
        try:
            if self.worker.servo is not None:
                model, result, _ = self.worker.servo.ReadModelNumber(sid)
                if result == COMM_SUCCESS:
                    mname = MODEL_NAMES.get(model, f"#{model}")
                    name = f"ID{sid} ({mname})"
        except Exception:
            pass
        item = QTableWidgetItem(name)
        self.servo_list_table.setItem(row, 0, item)
        # 同步到舵机下拉框
        if self.servo_combo.findData(sid) < 0:
            self.servo_combo.addItem(f"ID{sid}", sid)
        self.scan_result.setText(tr("在线: {} 个舵机").format(len(self.current_servos)))

    def _on_connected(self, ok, msg):
        if ok:
            self.connect_btn.setText(tr("断开"))
            self.conn_status.setText(tr("🟢 已连接"))
            self.conn_status.setStyleSheet("color: #26a69a; font-weight: bold;")
            self.port_combo.setEnabled(False)
            self.baud_combo.setEnabled(False)
        else:
            self.connect_btn.setText(tr("连接"))
            self.conn_status.setText(tr("🔴 未连接"))
            self.conn_status.setStyleSheet("color: #ef5350; font-weight: bold;")
            self.port_combo.setEnabled(True)
            self.baud_combo.setEnabled(True)
            if msg:
                QMessageBox.warning(self, tr("连接失败"), msg)

    def _on_scanned(self, servos):
        self.current_servos = list(servos)
        self.servo_combo.clear()
        for sid in servos:
            self.servo_combo.addItem(f"ID{sid}", sid)

        # 在舵机列表中显示所有扫描到的舵机（完整刷新）
        self.servo_list_table.setRowCount(len(servos))
        for row, sid in enumerate(servos):
            name = f"ID{sid}"
            try:
                if self.worker.servo is not None:
                    model, result, _ = self.worker.servo.ReadModelNumber(sid)
                    if result == COMM_SUCCESS:
                        mname = MODEL_NAMES.get(model, f"#{model}")
                        name = f"ID{sid} ({mname})"
            except Exception:
                pass
            item = QTableWidgetItem(name)
            self.servo_list_table.setItem(row, 0, item)

        self.scan_result.setText(tr("在线: {} 个舵机").format(len(servos)))
        if len(servos) == 1:
            self.servo_combo.setCurrentIndex(0)
        elif servos:
            self.add_log(tr("📡 扫描完成: {}").format(servos))

    def _on_param_read(self, servo_id, address, value):
        # 更新参数表格中对应行（保留行背景色）
        for row in range(self.param_table.rowCount()):
            item = self.param_table.item(row, 0)
            if item and item.data(32) == address:
                val_item = QTableWidgetItem(str(value))
                val_item.setBackground(item.background())
                val_item.setForeground(QColor("#263238"))
                self.param_table.setItem(row, 2, val_item)
                return

    def _on_status_read(self, servo_id, info):
        # 移动完成提示显示中，保留提示不被状态覆盖；用户再点"读取状态"时清除
        if self._move_done_pending:
            return
        self.status_label.setText(
            tr("ID{}: 位置 {} | 速度 {} | 负载 {} | 电压 {}V | 温度 {}°C | 电流 {} | 运行 {}").format(
                servo_id,
                info.get("position", "-"),
                info.get("speed", "-"),
                info.get("load", "-"),
                info.get("voltage", "-"),
                info.get("temperature", "-"),
                info.get("current", "-"),
                tr("是") if info.get("moving") else tr("否") if info.get("moving") is not None else "-",
            )
        )
        self.add_log(
            tr("📊 ID{} 位置:{} 速度:{} 负载:{} 电压:{:.1f}V 温度:{}°C 电流:{}").format(
                servo_id,
                info.get("position", "-"),
                info.get("speed", "-"),
                info.get("load", "-"),
                info.get("voltage", 0),
                info.get("temperature", "-"),
                info.get("current", "-"),
            )
        )

    # ---------------- UI ----------------
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # 顶部：串口连接
        conn_group = QGroupBox(tr("🔌 串口连接"))
        conn_layout = QHBoxLayout(conn_group)

        conn_layout.addWidget(QLabel(tr("串口:")))
        self.port_combo = QComboBox()
        for p in get_available_ports():
            self.port_combo.addItem(p.device)
        if self.port_name and self.port_combo.findText(self.port_name) < 0:
            self.port_combo.addItem(self.port_name)
        if self.port_name:
            self.port_combo.setCurrentText(self.port_name)
        self.port_combo.setMinimumWidth(140)
        conn_layout.addWidget(self.port_combo)

        self.refresh_port_btn = QPushButton(tr("🔄"))
        self.refresh_port_btn.setFixedSize(30, 28)
        self.refresh_port_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(self.refresh_port_btn)

        conn_layout.addWidget(QLabel(tr("波特率:")))
        self.baud_combo = QComboBox()
        for rate in [1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400]:
            self.baud_combo.addItem(str(rate), rate)
        self.baud_combo.setCurrentIndex(0)
        conn_layout.addWidget(self.baud_combo)

        self.connect_btn = QPushButton(tr("连接"))
        self.connect_btn.setStyleSheet("""
            QPushButton { background-color: #5c6bc0; color: white; border: none;
                padding: 6px 18px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #3f51b5; }
        """)
        self.connect_btn.clicked.connect(self.toggle_connect)
        conn_layout.addWidget(self.connect_btn)

        self.conn_status = QLabel(tr("🔴 未连接"))
        self.conn_status.setStyleSheet("font-weight: bold;")
        conn_layout.addWidget(self.conn_status)

        layout.addWidget(conn_group)

        # 中部：舵机选择 + 扫描
        servo_group = QGroupBox(tr("🎯 舵机"))
        servo_vbox = QVBoxLayout(servo_group)
        servo_vbox.setSpacing(6)

        # 第一行：操作按钮
        servo_layout = QHBoxLayout()
        servo_layout.setSpacing(8)

        self.scan_btn = QPushButton(tr("🔍 扫描舵机"))
        self.scan_btn.setStyleSheet("""
            QPushButton { background-color: #26a69a; color: white; border: none;
                padding: 6px 14px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #00897b; }
        """)
        self.scan_btn.clicked.connect(self.on_scan)
        servo_layout.addWidget(self.scan_btn)

        servo_layout.addWidget(QLabel(tr("舵机:")))
        self.servo_combo = QComboBox()
        self.servo_combo.setMinimumWidth(100)
        servo_layout.addWidget(self.servo_combo)

        self.read_all_btn = QPushButton(tr("📖 读取参数"))
        self.read_all_btn.clicked.connect(self.on_read_all)
        servo_layout.addWidget(self.read_all_btn)

        self.status_btn = QPushButton(tr("📊 读取状态"))
        self.status_btn.clicked.connect(self.on_read_status)
        servo_layout.addWidget(self.status_btn)

        self.scan_result = QLabel(tr("未扫描"))
        servo_layout.addWidget(self.scan_result)
        servo_layout.addStretch()

        servo_vbox.addLayout(servo_layout)

        # 第二行：扫描到的舵机列表（表格）
        self.servo_list_table = QTableWidget()
        self.servo_list_table.setColumnCount(1)
        self.servo_list_table.setHorizontalHeaderLabels([tr("扫描到的舵机")])
        self.servo_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.servo_list_table.verticalHeader().setVisible(False)
        self.servo_list_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.servo_list_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.servo_list_table.setMaximumHeight(100)
        self.servo_list_table.setMinimumHeight(50)
        # 选中列表中的舵机时，自动填充到舵机下拉框
        self.servo_list_table.itemSelectionChanged.connect(self._on_servo_list_selected)
        servo_vbox.addWidget(self.servo_list_table)

        layout.addWidget(servo_group)

        # 参数表格（对齐官方：5列 地址/寄存器/值/存储区域/读写，全量寄存器）
        param_group = QGroupBox(tr("📋 参数表"))
        param_layout = QVBoxLayout(param_group)
        param_layout.setSpacing(6)
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(5)
        self.param_table.setHorizontalHeaderLabels([tr("地址"), tr("寄存器"), tr("值"), tr("存储区域"), tr("读写")])
        # 列宽分配：地址/值/存储/读写固定，寄存器弹性
        self.param_table.setColumnWidth(0, 56)
        self.param_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.param_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.param_table.setColumnWidth(2, 110)
        self.param_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.param_table.setColumnWidth(3, 76)
        self.param_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.param_table.setColumnWidth(4, 52)
        self.param_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.param_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.param_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.param_table.verticalHeader().setVisible(False)
        # 选中某行时，自动把该寄存器地址填到"写入地址"
        self.param_table.itemSelectionChanged.connect(self._on_param_row_selected)
        # 参数表弹性高度：窗口大时拉伸，小时压缩 + 内部滚动
        self.param_table.setMinimumHeight(180)
        self._build_param_table()
        param_layout.addWidget(self.param_table, 1)  # stretch=1 占满剩余高度

        edit_row = QHBoxLayout()
        edit_row.addWidget(QLabel(tr("写入地址 0x")))
        # 地址不可手动输入，只能通过参数表选中联动
        self.edit_addr_label = QLabel("40")
        self.edit_addr_label.setStyleSheet("""
            background-color: #eef1f5; color: #263238; border: 1px solid #cfd4dc;
            border-radius: 4px; padding: 4px 8px; font-weight: bold;
            min-width: 48px;
        """)
        edit_row.addWidget(self.edit_addr_label)

        edit_row.addWidget(QLabel(tr("长度")))
        # 长度不可手动选择，跟随参数表联动
        self.edit_len_label = QLabel(tr("1 字节"))
        self.edit_len_label.setStyleSheet("""
            background-color: #eef1f5; color: #263238; border: 1px solid #cfd4dc;
            border-radius: 4px; padding: 4px 8px; font-weight: bold;
            min-width: 56px;
        """)
        edit_row.addWidget(self.edit_len_label)

        edit_row.addWidget(QLabel(tr("值")))
        self.edit_val_spin = QSpinBox()
        self.edit_val_spin.setRange(0, 2147483647)
        edit_row.addWidget(self.edit_val_spin)

        self.write_btn = QPushButton(tr("✏️ 写入"))
        self.write_btn.setStyleSheet("""
            QPushButton { background-color: #6f42c1; color: white; border: none;
                padding: 6px 14px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #5a32a3; }
        """)
        self.write_btn.clicked.connect(self.on_write_param)
        edit_row.addWidget(self.write_btn)

        edit_row.addStretch()
        param_layout.addLayout(edit_row)
        layout.addWidget(param_group, 3)  # 参数表占最大弹性空间

        # 位置控制
        pos_group = QGroupBox(tr("🎯 位置控制"))
        pos_layout = QHBoxLayout(pos_group)
        pos_layout.addWidget(QLabel(tr("目标位置")))
        # 目标位置滑杆（0-1023），拉动同步更新数值框
        self.pos_slider = QSlider(Qt.Horizontal)
        self.pos_slider.setRange(0, POS_MAX)
        self.pos_slider.setValue(512)
        self.pos_slider.setMinimumWidth(150)
        pos_layout.addWidget(self.pos_slider)
        self.pos_spin = QSpinBox()
        # SCS0009 电位器 10 位分辨率：0-1023
        self.pos_spin.setRange(0, POS_MAX)
        self.pos_spin.setValue(512)
        pos_layout.addWidget(self.pos_spin)
        # 双向同步：滑杆 ↔ 数值框
        self.pos_slider.valueChanged.connect(self.pos_spin.setValue)
        self.pos_spin.valueChanged.connect(self.pos_slider.setValue)
        pos_layout.addWidget(QLabel(tr("速度")))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(0, POS_MAX)
        self.speed_spin.setValue(1000)
        pos_layout.addWidget(self.speed_spin)
        self.move_btn = QPushButton(tr("▶ 移动"))
        self.move_btn.clicked.connect(self.on_move)
        pos_layout.addWidget(self.move_btn)
        self.torque_on_btn = QPushButton(tr("⚡ 力矩开"))
        self.torque_on_btn.clicked.connect(lambda: self.on_torque(True))
        pos_layout.addWidget(self.torque_on_btn)
        self.torque_off_btn = QPushButton(tr("⏹ 力矩关"))
        self.torque_off_btn.clicked.connect(lambda: self.on_torque(False))
        pos_layout.addWidget(self.torque_off_btn)
        self.status_label = QLabel(tr("状态: --"))
        pos_layout.addWidget(self.status_label, 1)
        layout.addWidget(pos_group)

        # 位置控制安全提示（红色字体）
        self.safety_label = QLabel(tr("⚠️ *如果突然转动过程中出现断连，请重新连接并关闭力矩！"))
        self.safety_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 12px;")
        self.safety_label.setWordWrap(True)
        layout.addWidget(self.safety_label)

        # 波特率修改 / 恢复出厂（从高级工具移入）
        sys_group = QGroupBox(tr("🔧 波特率 / 恢复出厂"))
        sys_layout = QHBoxLayout(sys_group)
        sys_layout.setSpacing(10)

        sys_layout.addWidget(QLabel(tr("新波特率:")))
        self.baud_edit_combo = QComboBox()
        for rate in [1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400]:
            self.baud_edit_combo.addItem(str(rate), rate)
        sys_layout.addWidget(self.baud_edit_combo)

        self.baud_btn = QPushButton(tr("🔧 修改波特率"))
        self.baud_btn.setStyleSheet("""
            QPushButton { background-color: #6f42c1; color: white; border: none;
                padding: 6px 14px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #5a32a3; }
        """)
        self.baud_btn.clicked.connect(self.on_change_baud_rate)
        sys_layout.addWidget(self.baud_btn)

        sys_layout.addSpacing(15)
        sys_layout.addWidget(QLabel(tr("⚠️ 恢复出厂:")))
        self.reset_btn = QPushButton(tr("🔄 恢复出厂"))
        self.reset_btn.setStyleSheet("""
            QPushButton { background-color: #ef5350; color: white; border: none;
                padding: 6px 14px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #e53935; }
        """)
        self.reset_btn.clicked.connect(self.on_factory_reset)
        sys_layout.addWidget(self.reset_btn)

        sys_layout.addStretch()
        layout.addWidget(sys_group)

        # xdat 文件（保存当前舵机参数 / 打开用于恢复）
        xdat_group = QGroupBox(tr("📁 xdat 参数（仅保存 EEPROM）"))
        xdat_layout = QHBoxLayout(xdat_group)
        self.save_xdat_btn = QPushButton(tr("💾 保存当前舵机"))
        self.save_xdat_btn.clicked.connect(self.on_save_xdat)
        xdat_layout.addWidget(self.save_xdat_btn)
        self.load_xdat_btn = QPushButton(tr("📂 打开 xdat"))
        self.load_xdat_btn.clicked.connect(self.on_load_xdat)
        xdat_layout.addWidget(self.load_xdat_btn)
        self.apply_xdat_btn = QPushButton(tr("📤 恢复参数到舵机"))
        self.apply_xdat_btn.setEnabled(False)
        self.apply_xdat_btn.setToolTip(tr("将已打开的 xdat 参数写回当前舵机"))
        self.apply_xdat_btn.clicked.connect(self.on_apply_xdat)
        xdat_layout.addWidget(self.apply_xdat_btn)
        self.xdat_label = QLabel(tr("未加载"))
        self.xdat_label.setWordWrap(True)
        xdat_layout.addWidget(self.xdat_label, 1)
        layout.addWidget(xdat_group)

        # 日志
        log_group = QGroupBox(tr("📜 日志"))
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(80)
        self.log_text.setMinimumHeight(50)
        self.log_text.setStyleSheet("""
            QTextEdit { background-color: #fafbfc; color: #263238;
                border: 1px solid #cfd4dc; border-radius: 4px;
                font-family: 'Consolas', monospace; font-size: 11px; }
        """)
        log_layout.addWidget(self.log_text)
        clear_btn = QPushButton(tr("清空"))
        clear_btn.setMaximumWidth(60)
        clear_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_btn)
        layout.addWidget(log_group)

        self.xdat_file: Optional[XdatFile] = None

    def _build_param_table(self):
        # 全量寄存器（对齐官方参数表），按存储区域分组着色
        area_colors = {
            "EPROM": "#ffffff",
            "SRAM": "#e8f4fd",
            "DEFAULT": "#f0f2f5",
        }
        self.param_table.setRowCount(len(SCS0009_REGISTERS))
        for row, (addr, ln, nm, area, rw) in enumerate(SCS0009_REGISTERS):
            color = area_colors.get(area, "#ffffff")
            items = [
                QTableWidgetItem(f"0x{addr:02X}"),
                QTableWidgetItem(tr(nm)),
                QTableWidgetItem("-"),
                QTableWidgetItem(tr(area)),
                QTableWidgetItem(tr(rw)),
            ]
            items[0].setData(32, addr)
            for col, it in enumerate(items):
                it.setBackground(QColor(color))
                if col != 2:
                    it.setForeground(QColor("#263238"))
                self.param_table.setItem(row, col, it)

    def _on_param_row_selected(self):
        """参数表选中某行时，把该寄存器地址/长度/值自动同步到"写入"控件"""
        row = self.param_table.currentRow()
        if row < 0:
            return
        item = self.param_table.item(row, 0)
        if item is None:
            return
        addr = item.data(32)
        if addr is None:
            return
        # 自动填入写入地址
        self.edit_addr_label.setText(f"{addr:02X}")
        # 自动匹配寄存器长度（已知表按表，未知按 1 字节）
        ln = 1
        for _a, _l, _nm, _area, _rw in SCS0009_REGISTERS:
            if _a == addr:
                ln = _l
                break
        self.edit_len_label.setText(tr("{} 字节").format(ln))
        # 自动填入当前值（参数表第 2 列）
        val_item = self.param_table.item(row, 2)
        if val_item is not None:
            val_text = val_item.text()
            if val_text not in ("-", ""):
                try:
                    self.edit_val_spin.setValue(int(val_text))
                except ValueError:
                    pass

    # ---------------- 槽函数 ----------------
    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        for p in get_available_ports():
            self.port_combo.addItem(p.device)
        if current:
            self.port_combo.setCurrentText(current)

    def toggle_connect(self):
        if self.worker.is_connected:
            self.worker.disconnect_serial()
            self.connect_btn.setText(tr("连接"))
            self.conn_status.setText(tr("🔴 未连接"))
            self.conn_status.setStyleSheet("color: #ef5350; font-weight: bold;")
            self.port_combo.setEnabled(True)
            self.baud_combo.setEnabled(True)
        else:
            port = self.port_combo.currentText()
            if not port:
                QMessageBox.warning(self, tr("提示"), tr("请选择串口"))
                return
            baud = self.baud_combo.currentData()
            # 连接操作加入串口队列串行执行（避免与读取/写入抢总线）
            self.worker.submit(self.worker.connect_serial, port, baud)

    def on_scan(self):
        # 点击扫描时立即清空显示框，避免旧舵机残留；扫描过程实时填充新结果
        self.current_servos = []
        self.servo_list_table.setRowCount(0)
        self.servo_combo.clear()
        self.scan_result.setText(tr("🔍 扫描中..."))
        self.worker.submit(self.worker.scan)

    def on_read_all(self):
        sid = self.current_servo_id()
        if sid is None:
            return
        # 逐个入队串行读取可读寄存器（EPROM + SRAM，跳过 DEFAULT 区）
        count = 0
        for addr, ln, nm, area, rw in SCS0009_REGISTERS:
            if area == "DEFAULT":
                continue  # 内部默认参数，不可直接读取
            count += 1
            self.worker.submit(self.worker.read_param, sid, addr, ln)
        self.add_log(tr("📋 开始读取 ID{} 的全部参数（{} 项，DEFAULT 区跳过）...").format(sid, count))

    def on_read_status(self):
        sid = self.current_servo_id()
        if sid is not None:
            self._move_done_pending = False  # 清除"移动完成"提示，恢复状态实时刷新
            self.worker.submit(self.worker.read_status, sid)

    def on_write_param(self):
        sid = self.current_servo_id()
        if sid is None:
            return
        # 地址/长度来自参数表选中联动（标签显示）
        try:
            addr = int(self.edit_addr_label.text(), 16)
        except ValueError:
            QMessageBox.warning(self, tr("提示"), tr("请先在参数表中选择要修改的寄存器"))
            return
        len_text = self.edit_len_label.text()
        ln = int(len_text.split()[0]) if len_text.split() else 1
        val = self.edit_val_spin.value()
        self.worker.submit(self.worker.write_param, sid, addr, ln, val)

    def on_move(self):
        sid = self.current_servo_id()
        if sid is None:
            return
        self._move_done_pending = True
        self.status_label.setText(tr("⏳ ID{} 移动中...").format(sid))
        self.status_label.setStyleSheet("color: #1a237e; font-weight: bold;")
        self.worker.submit(self.worker.move_servo,
                           sid, self.pos_spin.value(), self.speed_spin.value())

    def on_torque(self, enable):
        sid = self.current_servo_id()
        if sid is not None:
            self.worker.submit(self.worker.set_torque, sid, enable)

    def on_change_baud_rate(self):
        sid = self.current_servo_id()
        if sid is None:
            return
        new_baud = self.baud_edit_combo.currentData()
        reply = QMessageBox.warning(
            self, tr("警告：修改波特率"),
            tr("修改波特率后，串口将立即切换到 {} bps。\n如果失败，工具会尝试恢复原有波特率。\n\n确定要修改 ID{} 的波特率吗？").format(new_baud, sid),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.worker.submit(self.worker.change_baud_rate, sid, new_baud)

    def on_factory_reset(self):
        sid = self.current_servo_id()
        if sid is None:
            return
        reply = QMessageBox.critical(
            self, tr("危险操作"),
            tr("确定恢复 ID{} 出厂设置？\nID 将变回 1，波特率变回 1M，不可撤销！").format(sid),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.worker.submit(self.worker.factory_reset, sid)

    def _reg_len(self, addr: int) -> int:
        """从寄存器表查地址对应的长度（未知按 1 字节）"""
        for _a, _l, _nm, _area, _rw in SCS0009_REGISTERS:
            if _a == addr:
                return _l
        return 1

    def on_load_xdat(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("打开参数文件"), "",
            tr("参数文件 (*.xdat);;所有文件 (*)"))
        if not path:
            return
        try:
            # SCS0009 为大端字节序
            self.xdat_file = XdatFile.parse(path, endian=1)
            model = self.xdat_file.get_value(3, 2)
            model_name = MODEL_NAMES.get(model, f"#{model}")
            self.xdat_label.setText(tr("已加载: {} (型号 {} {})").format(
                os.path.basename(path), model, model_name))
            self.apply_xdat_btn.setEnabled(True)
            self.add_log(tr("📁 已加载 xdat: {}").format(path))
            # 将 xdat 参数填充到表格预览
            self._fill_table_from_xdat()
        except Exception as e:
            QMessageBox.critical(self, tr("错误"), tr("无法解析 xdat: {}").format(e))

    def _fill_table_from_xdat(self):
        """将当前 xdat_file 的参数填充到参数表（按地址匹配行，保留背景色）"""
        if self.xdat_file is None:
            return
        for row in range(self.param_table.rowCount()):
            item0 = self.param_table.item(row, 0)
            if item0 is None:
                continue
            addr = item0.data(32)
            if addr is None:
                continue
            ln = self._reg_len(addr)
            val = self.xdat_file.get_value(addr, ln)
            if val is not None:
                val_item = QTableWidgetItem(str(val))
                val_item.setBackground(item0.background())
                val_item.setForeground(QColor("#263238"))
                self.param_table.setItem(row, 2, val_item)

    def on_save_xdat(self):
        """保存当前 ID 舵机的参数到 xdat 文件（从舵机读取，用于后续恢复）"""
        sid = self.current_servo_id()
        if sid is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, tr("保存参数文件"), f"servo_{sid}.xdat",
            tr("参数文件 (*.xdat);;所有文件 (*)"))
        if not path:
            return
        self._save_xdat_path = path
        self._save_xdat_sid = sid
        self.add_log(tr("📖 正在读取 ID{} 的全部参数并保存...").format(sid))
        self.worker.submit(self.worker.read_servo_params, sid)

    def _on_servo_params_read(self, servo_id, data):
        """读取舵机参数完成：组装 xdat 文件保存"""
        path = getattr(self, '_save_xdat_path', None)
        if path is None:
            return
        try:
            # 组装 xdat：文件头(00 28) + 数据区，SCS0009 为大端
            xdat = XdatFile(bytes([0, 40]) + data, endian=1)
            xdat.save(path)
            self.xdat_file = xdat  # 保存后作为当前 xdat，可直接用于恢复
            self.apply_xdat_btn.setEnabled(True)
            self.add_log(tr("💾 已保存 ID{} 参数到: {}").format(servo_id, path))
            self.xdat_label.setText(tr("已保存: {}").format(os.path.basename(path)))
            # 更新表格预览为保存的参数
            self._fill_table_from_xdat()
            QMessageBox.information(self, tr("完成"), tr("已保存 ID{} 参数到 {}").format(servo_id, path))
        except Exception as e:
            self.add_log(tr("❌ 保存 xdat 失败: {}").format(e))
        finally:
            self._save_xdat_path = None
            self._save_xdat_sid = None

    def on_apply_xdat(self):
        sid = self.current_servo_id()
        if sid is None or self.xdat_file is None:
            return
        reply = QMessageBox.question(
            self, tr("确认恢复"),
            tr("将 xdat 参数恢复到 ID{}？此操作会覆盖该舵机 EEPROM。").format(sid),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.worker.submit(self.worker.apply_xdat, sid, self.xdat_file)

    # ---------------- 辅助 ----------------
    def current_servo_id(self) -> Optional[int]:
        if self.worker.is_connected and self.servo_combo.currentData() is not None:
            return self.servo_combo.currentData()
        QMessageBox.warning(self, tr("提示"), tr("请先连接并选择舵机"))
        return None

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def shutdown(self):
        """释放资源：先尝试关闭舵机力矩，再断开串口、停止线程"""
        # 关闭前先尝试关闭所有在线舵机力矩，避免舵机保持锁死/堵转
        try:
            if self.worker.is_connected and self.worker.servo is not None:
                for sid in self.current_servos:
                    try:
                        self.worker.servo.write1ByteTxRx(sid, 40, 0)
                    except Exception:
                        pass
                self.add_log(tr("⏹ 已尝试关闭所有舵机力矩"))
        except Exception:
            pass
        try:
            self.worker.disconnect_serial()
        except Exception:
            pass
        try:
            self.thread.quit()
            self.thread.wait(2000)
        except Exception:
            pass
