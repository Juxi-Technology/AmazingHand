#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FTServo 参数文件 (xdat) 读写模块。

兼容飞特官方上位机 "FT SCServo Debug" 导出的 xdat 文件格式。

实测官方 xdat 为**扁平内存映射**结构（以 STS3215 参数文件为例，51 字节）：

    文件布局：
        [0:2]   文件头（小端 u16，官方文件值为 40，通常原样保留）
        [2:2+N] 数据区，按寄存器地址从 0 连续存放（地址 A -> 偏移 A+2）
                数据区长度为 49 字节，覆盖寄存器地址 0..48

用法::

    from src.xdat_utils import XdatFile, STS3215_EPROM

    x = XdatFile.parse(path)          # 读取
    x.set_value(5, 3)                 # 改 ID
    x.save(path)                      # 写回（保持原始布局）
    print(x)
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 可查询的寄存器定义（对齐飞特官方 FT SCServo Debug 的 STS 系列参数表）
# ---------------------------------------------------------------------------
# (地址, 长度, 显示名, 存储区域, 读写属性)
# 地址/长度/名称 以官方上位机显示为准，并经 C044/C046 两个 xdat 文件逐字节校验。
# 存储区域: EPROM(掉电保存) / SRAM(运行时) / DEFAULT(内部默认)
# 读写属性: 只读 / 读写 / 默认
STS3215_REGISTERS = [
    # ---- 固件/版本（只读） ----
    (0, 1, "固件主版本号", "EPROM", "只读"),
    (1, 1, "固件次版本号", "EPROM", "只读"),
    (3, 1, "舵机主版本号", "EPROM", "只读"),
    (4, 1, "舵机次版本号", "EPROM", "只读"),

    # ---- 基本设置 ----
    (5, 1, "舵机 ID", "EPROM", "读写"),
    (6, 1, "波特率", "EPROM", "读写"),
    (7, 1, "保留地址", "EPROM", "读写"),
    (8, 1, "应答状态级别", "EPROM", "读写"),

    # ---- 限值设置 ----
    (9, 2, "最小角度限制", "EPROM", "读写"),
    (11, 2, "最大角度限制", "EPROM", "读写"),
    (13, 1, "最高温度上限", "EPROM", "读写"),
    (14, 1, "最高输入电压", "EPROM", "读写"),
    (15, 1, "最低输入电压", "EPROM", "读写"),
    (16, 2, "最大扭矩", "EPROM", "读写"),

    # ---- 控制系数 / 报警 ----
    (18, 1, "相位", "EPROM", "读写"),
    (19, 1, "卸载条件", "EPROM", "读写"),
    (20, 1, "LED报警条件", "EPROM", "读写"),
    (21, 1, "P比例系数", "EPROM", "读写"),
    (22, 1, "D微分系数", "EPROM", "读写"),
    (23, 1, "I积分系数", "EPROM", "读写"),
    (24, 1, "最小启动力", "EPROM", "读写"),
    (25, 1, "积分限制", "EPROM", "读写"),
    (26, 1, "顺时针不灵敏区", "EPROM", "读写"),
    (27, 1, "逆时针不灵敏区", "EPROM", "读写"),

    # ---- 保护 / 模式 ----
    (28, 2, "保护电流", "EPROM", "读写"),
    (30, 1, "角度分辨率", "EPROM", "读写"),
    (31, 2, "位置偏移", "EPROM", "读写"),
    (33, 1, "运行模式", "EPROM", "读写"),
    (34, 1, "保护扭矩", "EPROM", "读写"),
    (35, 1, "保护时间", "EPROM", "读写"),
    (36, 1, "过载扭矩", "EPROM", "读写"),
    (37, 1, "速度闭环P比例系数", "EPROM", "读写"),
    (38, 1, "过流保护时间", "EPROM", "读写"),
    (39, 1, "速度闭环I积分系数", "EPROM", "读写"),

    # ---- SRAM 可写（实时控制） ----
    (40, 1, "扭矩开关", "SRAM", "读写"),
    (41, 1, "加速度", "SRAM", "读写"),
    (42, 2, "目标位置", "SRAM", "读写"),
    (44, 2, "PWM开环速度", "SRAM", "读写"),
    (46, 2, "运行速度", "SRAM", "读写"),
    (48, 2, "转矩限制", "SRAM", "读写"),
    (55, 1, "锁标志", "SRAM", "读写"),

    # ---- SRAM 只读（实时状态） ----
    (56, 2, "当前位置", "SRAM", "只读"),
    (58, 2, "当前速度", "SRAM", "只读"),
    (60, 2, "当前负载", "SRAM", "只读"),
    (62, 1, "当前电压", "SRAM", "只读"),
    (63, 1, "当前温度", "SRAM", "只读"),
    (64, 1, "异步写标志", "SRAM", "只读"),
    (65, 1, "舵机状态", "SRAM", "只读"),
    (66, 1, "移动标志", "SRAM", "只读"),
    (69, 2, "当前电流", "SRAM", "只读"),

    # ---- DEFAULT（出厂默认，只读） ----
    (80, 1, "移动速度阈值", "DEFAULT", "默认"),
    (81, 1, "DTS(ms)", "DEFAULT", "默认"),
    (82, 1, "速度单位系数", "DEFAULT", "默认"),
    (83, 1, "最小速度限制", "DEFAULT", "默认"),
    (84, 1, "最大速度限制", "DEFAULT", "默认"),
    (85, 1, "加速度限制", "DEFAULT", "默认"),
    (86, 1, "加速度倍数", "DEFAULT", "默认"),
]

# 兼容旧引用：按存储区域拆分
STS3215_EPROM = [r for r in STS3215_REGISTERS if r[3] == "EPROM"]
STS3215_SRAM = [r for r in STS3215_REGISTERS if r[3] == "SRAM" and r[4] == "读写"]
STS3215_SRAM_RO = [r for r in STS3215_REGISTERS if r[3] == "SRAM" and r[4] == "只读"]
STS3215_DEFAULT = [r for r in STS3215_REGISTERS if r[3] == "DEFAULT"]

# 可写寄存器（EPROM 读写 + SRAM 读写）
STS3215_WRITABLE = [r for r in STS3215_REGISTERS if r[4] == "读写"]

# ---------------------------------------------------------------------------
# SCS0009 寄存器定义（SCS 系列，电位器反馈）
# ---------------------------------------------------------------------------
# SCS0009 采用电位器（Potentiometer）位置反馈，非磁编码器：
#   - 分辨率：10 位（0–1023 步），对应 0°–300° 有效行程
#   - 字节序：大端（SCS 协议，endian=1）
#   - 协议类：scscl
# 寄存器地址基于 scscl.py 内存表，并经飞特上位机 SCS0009 参数展示截图校验。
SCS0009_REGISTERS = [
    # ---- 固件/版本（只读） ----
    (0, 1, "固件主版本号", "EPROM", "只读"),
    (1, 1, "固件次版本号", "EPROM", "只读"),
    (3, 1, "舵机主版本号", "EPROM", "只读"),
    (4, 1, "舵机次版本号", "EPROM", "只读"),

    # ---- 基本设置 ----
    (5, 1, "舵机 ID", "EPROM", "读写"),
    (6, 1, "波特率", "EPROM", "读写"),
    (7, 1, "预留地址", "EPROM", "读写"),
    (8, 1, "应答状态级别", "EPROM", "读写"),

    # ---- 限值设置（电位器 0-1023） ----
    (9, 2, "最小角度限制", "EPROM", "读写"),
    (11, 2, "最大角度限制", "EPROM", "读写"),
    (13, 1, "最高温度上限", "EPROM", "读写"),
    (14, 1, "最高输入电压", "EPROM", "读写"),
    (15, 1, "最低输入电压", "EPROM", "读写"),
    (16, 2, "最大扭矩", "EPROM", "读写"),

    # ---- 控制参数 ----
    (18, 1, "相位", "EPROM", "读写"),
    (19, 1, "卸载条件", "EPROM", "读写"),
    (20, 1, "LED报警条件", "EPROM", "读写"),
    (21, 1, "P比例系数", "EPROM", "读写"),
    (22, 1, "D微分系数", "EPROM", "读写"),
    (25, 1, "最小启动力", "EPROM", "读写"),
    (26, 1, "顺时针不灵敏区", "EPROM", "读写"),
    (27, 1, "逆时针不灵敏区", "EPROM", "读写"),

    # ---- 保护参数 ----
    (37, 1, "保护扭矩", "EPROM", "读写"),
    (38, 1, "保护时间", "EPROM", "读写"),
    (39, 1, "过载扭矩", "EPROM", "读写"),

    # ---- SRAM 可写（实时控制） ----
    (40, 1, "扭矩开关", "SRAM", "读写"),
    (42, 2, "目标位置", "SRAM", "读写"),
    (44, 2, "运行时间", "SRAM", "读写"),
    (46, 2, "运行速度", "SRAM", "读写"),
    (48, 1, "锁标志", "SRAM", "读写"),

    # ---- SRAM 只读（实时状态） ----
    (56, 2, "当前位置", "SRAM", "只读"),
    (58, 2, "当前速度", "SRAM", "只读"),
    (60, 2, "当前负载", "SRAM", "只读"),
    (62, 1, "当前电压", "SRAM", "只读"),
    (63, 1, "当前温度", "SRAM", "只读"),
    (64, 1, "异步写标志", "SRAM", "只读"),
    (65, 1, "舵机状态", "SRAM", "只读"),
    (66, 1, "移动标志", "SRAM", "只读"),

    # ---- DEFAULT（出厂默认，只读） ----
    (78, 1, "PWM模式最大步进", "DEFAULT", "默认"),
    (79, 1, "移动速度阈值*50", "DEFAULT", "默认"),
    (80, 1, "DTs(ms)", "DEFAULT", "默认"),
    (81, 1, "最小速度限制*50", "DEFAULT", "默认"),
    (82, 1, "最大速度限制*50", "DEFAULT", "默认"),
    (83, 1, "加速度", "DEFAULT", "默认"),
]

# 按存储区域拆分
SCS0009_EPROM = [r for r in SCS0009_REGISTERS if r[3] == "EPROM"]
SCS0009_SRAM = [r for r in SCS0009_REGISTERS if r[3] == "SRAM" and r[4] == "读写"]
SCS0009_SRAM_RO = [r for r in SCS0009_REGISTERS if r[3] == "SRAM" and r[4] == "只读"]

# 波特率表：寄存器值 -> 波特率
BAUD_TABLE = {
    0: 1000000, 1: 500000, 2: 250000, 3: 128000,
    4: 115200, 5: 76800, 6: 57600, 7: 38400,
}
BAUD_TABLE_REV = {v: k for k, v in BAUD_TABLE.items()}

# 运行模式
MODE_NAMES = {0: "舵机模式 (Position)", 1: "轮式模式 (Wheel)"}

# 常用舵机型号
MODEL_NAMES = {
    777: "STS3215", 521: "STS3032", 3032: "STS3032", 3046: "STS3046",
    15: "SCS15", 25: "SCS25", 45: "SCS45", 115: "SCS115", 215: "SCS215",
    9: "SCS0009", 2304: "SCS0009",
}


class XdatFile:
    """解析 / 生成 xdat 参数文件（扁平内存映射）

    Args:
        raw: 原始文件字节
        endian: 字节序，0=小端(LSB first, STS/SMS 系列)，1=大端(MSB first, SCS 系列)
    """

    def __init__(self, raw: bytes, endian: int = 0):
        self.raw = raw
        self.endian = endian
        self.count = raw[0] | (raw[1] << 8) if len(raw) >= 2 else 0
        # 保留原始文件头字节（飞特工具为 00 28，即大端 40；重新生成时原样写回避免字节序差异）
        self._header = raw[0:2] if len(raw) >= 2 else bytes([0, 40])
        # 数据区：地址 A -> 偏移 A+2
        self.data = bytearray(raw[2:]) if len(raw) > 2 else bytearray()

    # ------------------------------------------------------------------
    # 解析 / 序列化
    # ------------------------------------------------------------------
    @staticmethod
    def parse(path_or_bytes, endian: int = 0) -> "XdatFile":
        if isinstance(path_or_bytes, (bytes, bytearray)):
            data = bytes(path_or_bytes)
        else:
            with open(path_or_bytes, "rb") as f:
                data = f.read()
        return XdatFile(data, endian)

    def to_bytes(self) -> bytes:
        return self._header + bytes(self.data)

    def save(self, path: str):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.to_bytes())

    # ------------------------------------------------------------------
    # 便捷访问
    # ------------------------------------------------------------------
    def _ensure(self, address: int, length: int):
        """确保数据区扩展到能容纳 地址+长度"""
        need = address + length - len(self.data)
        if need > 0:
            self.data.extend(b"\x00" * need)

    def get_value(self, address: int, length: int = None, default: Optional[int] = None):
        """读取寄存器值。length 缺省时按地址自动匹配（未知地址按 2 字节）"""
        if length is None:
            for ln in (2, 1):
                if address + ln <= len(self.data):
                    return self._read(address, ln)
            return default
        if address + length > len(self.data):
            return default
        return self._read(address, length)

    def _read(self, address: int, length: int) -> int:
        """按字节序读取多字节值。endian=0 小端，endian=1 大端"""
        raw = self.data[address: address + length]
        v = 0
        if self.endian == 1:
            # 大端：高位在前
            for b in raw:
                v = (v << 8) | b
        else:
            # 小端：低位在前
            for i, b in enumerate(raw):
                v |= b << (8 * i)
        return v

    def set_value(self, address: int, value: int, length: int):
        """写入寄存器值（按字节序）"""
        self._ensure(address, length)
        if self.endian == 1:
            # 大端：高位在前
            for i in range(length):
                shift = 8 * (length - 1 - i)
                self.data[address + i] = (value >> shift) & 0xFF
        else:
            # 小端：低位在前
            for i in range(length):
                self.data[address + i] = (value >> (8 * i)) & 0xFF

    def name_of(self, address: int) -> str:
        for _tbl in (SCS0009_REGISTERS, STS3215_REGISTERS):
            for addr, ln, nm, _area, _rw in _tbl:
                if addr == address:
                    return nm
        return "保留/未知"

    def __str__(self):
        lines = [f"XdatFile: count={self.count} 数据区={len(self.data)} 字节 (地址 0..{max(0, len(self.data)-1)})"]
        # 逐寄存器展示（优先 SCS0009 表，其次 STS3215）
        for tbl in (SCS0009_REGISTERS, STS3215_REGISTERS):
            for addr, ln, nm, area, rw in tbl:
                if addr >= len(self.data):
                    break
                v = self._read(addr, ln) if addr + ln <= len(self.data) else self._read(addr, max(1, len(self.data)-addr))
                lines.append(f"  地址 {addr:#04x} ({ln}B) {nm:<28} = {v}  [{area}/{rw}]")
        return "\n".join(lines)



# ---------------------------------------------------------------------------
# 演示/自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        x = XdatFile.parse(path)
        print(f"=== {path} ===")
        print(x)
        print()
