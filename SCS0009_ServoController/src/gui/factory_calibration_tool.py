#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCS0009 舵机调试工具 - 主窗口

由 JUXI_Technology 开发（MIT 许可，详见 LICENSE）。
本工具只包含 FT 调试器界面：串口连接、扫描、参数读写、位置控制、
波特率/恢复出厂、xdat 参数备份恢复，以及中英文切换。
"""

import sys
import time
import threading
import subprocess
import os
from typing import List
from queue import Queue

# 添加必要的路径（基于本文件绝对路径，避免依赖 cwd / 启动方式）
# 本文件位于 <root>/src/gui/factory_calibration_tool.py，项目根目录为上三级
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SCSERVO_SDK_DIR = os.path.join(PROJECT_ROOT, "scservo_sdk")
if os.path.isdir(SCSERVO_SDK_DIR) and SCSERVO_SDK_DIR not in sys.path:
    sys.path.insert(0, SCSERVO_SDK_DIR)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QStatusBar, QComboBox,
    QMessageBox, QFrame, QScrollArea,
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

# 引入主题工具，强制浅色主题以避免 Windows 深色模式下文字看不见
try:
    from src.gui.theme_utils import setup_light_theme
    THEME_UTILS_AVAILABLE = True
except ImportError:
    THEME_UTILS_AVAILABLE = False
    print("Warning: theme_utils not found, UI may be unreadable in dark mode")

# 引入端口工具
try:
    from src.port_utils import get_available_ports as _get_ports_util
    PORT_UTILS_AVAILABLE = True
except ImportError:
    PORT_UTILS_AVAILABLE = False
    print("Warning: port_utils not found, using fallback port detection")

# 引入国际化支持
try:
    from src.i18n import tr, set_lang, get_lang
except ImportError:
    def tr(text):
        return text

    def set_lang(lang):
        return lang

    def get_lang():
        return "zh"


# FT 调试器（核心功能面板）
try:
    from src.gui.ft_debugger import FtDebuggerPanel
    FT_DEBUGGER_AVAILABLE = True
except ImportError:
    FtDebuggerPanel = None
    FT_DEBUGGER_AVAILABLE = False


def get_chinese_font(size=10, bold=False):
    """返回跨平台可用的中文字体。

    Ubuntu 下通常有 Noto Sans CJK / WenQuanYi 等回退字体，Qt 能正常显示中文；
    Windows 下如果显式使用西文字体（如 Consolas）显示中文表头，会出现缺字/空白。
    这里按平台选择主字体，并设置 SansSerif 风格提示以便自动回退。
    """
    import platform as _platform
    system = _platform.system()
    if system == "Windows":
        family = "Microsoft YaHei"
    elif system == "Darwin":
        family = "PingFang SC"
    else:
        # Linux / Ubuntu 等
        family = "Noto Sans CJK SC"

    font = QFont(family, size)
    font.setStyleHint(QFont.SansSerif)
    if bold:
        font.setBold(True)
    return font


def get_available_ports():
    """获取可用串口列表"""
    if PORT_UTILS_AVAILABLE:
        return [p.device for p in _get_ports_util()]
    try:
        import serial.tools.list_ports
        import platform as _platform
        ports = []
        for p in serial.tools.list_ports.comports():
            device = p.device
            if _platform.system() == "Linux" and "ttyS" in device:
                continue
            ports.append(device)
        return sorted(ports)
    except ImportError:
        return []


class MainWindow(QMainWindow):
    """SCS0009 舵机调试工具 - 主窗口（FT 调试器）"""

    def __init__(self, port_name: str = None):
        super().__init__()
        self.port_name = port_name
        self.available_ports = []
        self.init_ui()
        self.init_connections()
        self.refresh_ports()

        # 定时刷新串口列表，支持热插拔自动识别
        self.port_refresh_timer = QTimer(self)
        self.port_refresh_timer.timeout.connect(self.refresh_ports)
        self.port_refresh_timer.start(2000)

    # ---------------- UI ----------------
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(tr("SCS0009 舵机调试工具"))
        screen_rect = QApplication.primaryScreen().availableGeometry()
        init_w = min(1500, screen_rect.width() - 40)
        init_h = min(950, screen_rect.height() - 40)
        self.setGeometry(20, 20, init_w, init_h)

        # 设置字体（跨平台）
        font = get_chinese_font(10)
        self.setFont(font)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 顶部标题栏
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # 标题 + 副标题
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_label = QLabel(tr("SCS0009 舵机调试工具"))
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a237e;")
        title_box.addWidget(title_label)
        subtitle_label = QLabel(tr("Feetech STS3215 系列舵机调试 / 参数读写 / xdat 备份"))
        subtitle_label.setStyleSheet("font-size: 12px; color: #546e7a;")
        title_box.addWidget(subtitle_label)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # 语言切换按钮
        self.lang_btn = QPushButton(tr("EN / English"))
        self.lang_btn.setMinimumSize(80, 34)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #26a69a, stop:1 #00897b);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00897b, stop:1 #00796b);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00796b, stop:1 #00695c);
            }
        """)
        self.lang_btn.clicked.connect(self.toggle_language)
        self.lang_btn.setToolTip(tr("切换界面语言 / Toggle UI language"))
        header_layout.addWidget(self.lang_btn)

        self._update_lang_btn_text()

        main_layout.addLayout(header_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("FT 调试器已就绪"), 3000)

        # FT 调试器面板（包进滚动区域：窗口高度不足时出滚动条，最大化时自适应拉伸）
        if FT_DEBUGGER_AVAILABLE:
            self.ft_panel = FtDebuggerPanel(self.port_name)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(self.ft_panel)
            main_layout.addWidget(scroll, 1)
        else:
            err_label = QLabel(tr("❌ FT 调试器模块加载失败，请检查依赖"))
            main_layout.addWidget(err_label)

        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafbfc;
            }
        """)

    def init_connections(self):
        """初始化信号连接"""
        pass

    # ---------------- 语言切换 ----------------
    @staticmethod
    def _get_config_dir():
        """获取配置文件目录（跨平台）"""
        import platform as _platform
        home = os.path.expanduser("~")
        if _platform.system() == "Windows":
            base = os.environ.get("APPDATA") or home
        else:
            base = home
        cfg_dir = os.path.join(base, ".scs0009_servo")
        try:
            os.makedirs(cfg_dir, exist_ok=True)
        except Exception:
            pass
        return cfg_dir

    def toggle_language(self):
        """切换中英文界面语言，并自动重启界面使语言完全生效"""
        current = get_lang()
        new_lang = "en" if current == "zh" else "zh"
        set_lang(new_lang)

        # 持久化语言选择
        try:
            cfg_file = os.path.join(self._get_config_dir(), "settings.json")
            import json as _json
            _cfg = {}
            if os.path.exists(cfg_file):
                with open(cfg_file, "r", encoding="utf-8") as f:
                    _cfg = _json.load(f)
            _cfg["lang"] = new_lang
            with open(cfg_file, "w", encoding="utf-8") as f:
                _json.dump(_cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        target = "English" if new_lang == "en" else "中文"
        QMessageBox.information(
            self,
            tr("语言已切换"),
            tr("界面语言已切换为 {}。\n程序将自动重启以完全应用新语言。").format(target),
        )
        self._restart_app()

    def _restart_app(self):
        """自动重启界面：以相同参数启动新进程，然后走正常关闭流程退出当前进程。

        新进程启动时会读取 settings.json 中已写入的语言配置，
        从而以新语言加载整个界面。

        注意：工作目录固定在项目根目录 PROJECT_ROOT，
        且模块顶部已基于 ``__file__`` 注入项目根 / scservo_sdk 到 sys.path，
        因此无论从哪个目录、以哪种方式（脚本 / -m）启动，新进程都能找到依赖。
        """
        try:
            script = getattr(sys.modules.get("__main__"), "__file__", None)
            if script:
                cmd = [sys.executable, os.path.abspath(script)]
            else:
                # -m 方式启动时 __main__ 没有 __file__，用当前模块的 __file__ 定位脚本
                cmd = [sys.executable, os.path.abspath(__file__)]
            # 保留原有启动参数，但剔除 --lang，让配置文件决定重启后的语言
            skip_next = False
            for arg in sys.argv[1:]:
                if skip_next:
                    skip_next = False
                    continue
                if arg == "--lang":
                    skip_next = True
                    continue
                if arg.startswith("--lang="):
                    continue
                cmd.append(arg)
            subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                close_fds=False,
            )
        except Exception as e:
            print(f"[RESTART] 自动重启失败: {e}")

        # 走正常关闭流程，最后一个窗口关闭后 QApplication 退出事件循环
        try:
            self.close()
        except Exception:
            pass

    def _update_lang_btn_text(self):
        """更新语言按钮文字：显示当前语言，点击切换到另一种"""
        if get_lang() == "en":
            self.lang_btn.setText(tr("中文 / CN"))
        else:
            self.lang_btn.setText(tr("EN / English"))

    # ---------------- 串口刷新 ----------------
    def stop_port_refresh(self):
        """停止串口自动刷新"""
        if hasattr(self, 'port_refresh_timer') and self.port_refresh_timer.isActive():
            self.port_refresh_timer.stop()

    def start_port_refresh(self):
        """恢复串口自动刷新"""
        if hasattr(self, 'port_refresh_timer') and not self.port_refresh_timer.isActive():
            self.port_refresh_timer.start(2000)

    def refresh_ports(self):
        """刷新可用串口列表（供 FT 面板使用）"""
        try:
            self.available_ports = get_available_ports()
        except Exception:
            self.available_ports = []

    # ---------------- 关闭 ----------------
    def closeEvent(self, event):
        """关闭事件：释放 FT 调试器串口与线程"""
        self.stop_port_refresh()
        if hasattr(self, 'ft_panel'):
            try:
                self.ft_panel.shutdown()
            except Exception:
                pass
        super().closeEvent(event)


def main():
    """主函数"""
    import platform
    import argparse

    # Windows 下子进程默认可能使用 GBK 编码，导致脚本里的 emoji 输出报错。
    # 强制子进程使用 utf-8 编码标准输出。
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    # 解析命令行参数
    parser = argparse.ArgumentParser(description=tr('SCS0009 舵机调试工具'))
    parser.add_argument('--port', type=str, help=tr('指定串口 (例如: COM3 或 /dev/ttyUSB0)'))
    parser.add_argument('--list-ports', action='store_true', help=tr('列出可用串口并退出'))
    parser.add_argument('--lang', choices=['zh', 'en'], default=None,
                        help=tr('界面语言 (zh=中文, en=English)，不指定则启动时选择'))
    args = parser.parse_args()

    # 如果只是列出串口
    if args.list_ports:
        try:
            available_ports = get_available_ports()
            print(tr("可用串口列表:"))
            for i, port in enumerate(available_ports, 1):
                print(f"  {i}. {port}")
            if not available_ports:
                print(tr("  未发现可用串口"))
        except Exception as e:
            print(tr("获取串口列表失败: {}").format(e))
        return

    app = QApplication(sys.argv)

    # 设置 Ctrl+C 信号处理，使其能正常关闭 Qt 应用
    import signal

    def handle_sigint(signum, frame):
        print(tr("\n收到 Ctrl+C，正在关闭..."))
        app.quit()

    signal.signal(signal.SIGINT, handle_sigint)

    # 启动定时器让 Python 有机会处理信号
    sig_timer = QTimer()
    sig_timer.start(200)
    sig_timer.timeout.connect(lambda: None)

    if THEME_UTILS_AVAILABLE:
        setup_light_theme(app)
    else:
        app.setStyle('Fusion')

    # 语言选择：--lang > 环境变量 SCS0009_LANG > 配置文件 > 启动对话框
    saved_lang = None
    try:
        cfg_file = os.path.join(MainWindow._get_config_dir(), "settings.json")
        if os.path.exists(cfg_file):
            with open(cfg_file, "r", encoding="utf-8") as f:
                import json as _json
                saved_lang = _json.load(f).get("lang")
    except Exception:
        saved_lang = None

    if args.lang:
        set_lang(args.lang)
    elif saved_lang:
        set_lang(saved_lang)
    else:
        from src.gui.language_dialog import choose_language
        set_lang(choose_language())

    # 持久化语言选择
    try:
        cfg_file = os.path.join(MainWindow._get_config_dir(), "settings.json")
        import json as _json
        _cfg = {}
        if os.path.exists(cfg_file):
            with open(cfg_file, "r", encoding="utf-8") as f:
                _cfg = _json.load(f)
        _cfg["lang"] = get_lang()
        with open(cfg_file, "w", encoding="utf-8") as f:
            _json.dump(_cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 默认端口
    system = platform.system()
    default_port = "COM3" if system == "Windows" else "/dev/ttyUSB0"

    # 自动选择端口
    port_name = args.port
    if not port_name:
        available_ports = get_available_ports()
        if available_ports:
            port_name = available_ports[0]
            print(tr("自动选择串口: {}").format(port_name))
        else:
            port_name = default_port
            print(tr("未发现串口，使用默认: {}").format(port_name))

    print(tr("启动 SCS0009 舵机调试工具"))
    print(tr("系统: {}").format(system))
    print(tr("串口: {}").format(port_name))

    # 创建并显示主窗口
    window = MainWindow(port_name)
    window.show()

    print(tr("UI界面已启动"))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
