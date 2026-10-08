#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""src/gui/factory_calibration_tool.py 的英文翻译表（key 为中文原文）。

仅保留 FT 调试器主窗口实际用到的翻译。
"""

TRANSLATIONS = {
    # 主窗口
    "SCS0009 舵机调试工具": "SCS0009 Servo Debug Tool",
    "Feetech STS3215 系列舵机调试 / 参数读写 / xdat 备份": "Feetech STS3215 servo debug / param read-write / xdat backup",
    "FT 调试器已就绪": "FT Debugger ready",
    "❌ FT 调试器模块加载失败，请检查依赖": "❌ FT Debugger module failed to load, please check dependencies",
    "切换界面语言 / Toggle UI language": "切换界面语言 / Toggle UI language",
    "EN / English": "EN / English",
    "中文 / CN": "中文 / CN",
    "语言已切换": "Language switched",
    "界面语言已切换为 {}。\n程序将自动重启以完全应用新语言。": "UI language switched to {}.\nThe application will restart automatically to fully apply the new language.",
    "系统: {}": "System: {}",
    "串口: {}": "Port: {}",
    "启动 SCS0009 舵机调试工具": "Starting SCS0009 Servo Debug Tool",
    "自动选择串口: {}": "Auto-selected port: {}",
    "未发现串口，使用默认: {}": "No ports found, using default: {}",
    "可用串口列表:": "Available serial ports:",
    "  未发现可用串口": "  No available serial ports found",
    "获取串口列表失败: {}": "Failed to get serial port list: {}",
    "列出可用串口并退出": "List available serial ports and exit",
    "指定串口 (例如: COM3 或 /dev/ttyUSB0)": "Specify serial port (e.g. COM3 or /dev/ttyUSB0)",
    "界面语言 (zh=中文, en=English)，不指定则启动时选择": "UI language (zh=Chinese, en=English); prompt at startup if not specified",
    "\n收到 Ctrl+C，正在关闭...": "\nCtrl+C received, shutting down...",
    "UI界面已启动": "UI started",

    # FT 调试器（与 ft_debugger.py 共用的一部分）
    "🔴 未连接": "🔴 Not connected",
    "🟢 已连接": "🟢 Connected",
    "❌ 无法打开串口: {}": "❌ Cannot open serial port: {}",
    "❌ 连接失败: {}": "❌ Connection failed: {}",
    "警告": "Warning",
    "提示": "Notice",
    "关闭": "OFF",
    "开启": "ON",
    "是": "Yes",
    "否": "No",
    "清空": "Clear",
    "1 字节": "1 byte",
    "✏️ 写入": "✏️ Write",
    "确认写入": "Confirm Write",

    # FT 调试器 - 波特率 / 恢复出厂
    "新波特率:": "New Baud Rate:",
    "🔧 修改波特率": "🔧 Change Baud Rate",
    "🔄 恢复出厂": "🔄 Factory Reset",
    "警告：修改波特率": "Warning: Change Baud Rate",
    "修改波特率后，串口将立即切换到 {} bps。\n如果失败，工具会尝试恢复原有波特率。\n\n确定要修改 ID{} 的波特率吗？": "After changing the baud rate, the serial port will switch to {} bps immediately.\nIf it fails, the tool will try to restore the original baud rate.\n\nChange the baud rate of ID{}?",
    "🔄 串口切换到 {} bps...": "🔄 Switching serial port to {} bps...",
    "⚠️ 新波特率验证失败，尝试恢复 {} bps": "⚠️ New baud rate verification failed, restoring {} bps",

    # port_utils 交互式选择
    '请选择串口 / Select serial port': 'Select serial port',
    '发现 {} 个可用串口 / Found {} available serial port(s):': 'Found {} available serial port(s):',
    '❌ 未发现可用串口 / No serial ports found': '❌ No serial ports found',
    '   请检查 USB 转串口适配器是否已连接\n   Please ensure USB-to-Serial adapter is connected': '   Please ensure USB-to-Serial adapter is connected',
    '🔌 自动选择唯一端口 / Auto-select only port: {}': '🔌 Auto-selected the only port: {}',
    '   描述 / Description: {}': '   Description: {}',
    '      描述 / Description: {}': '      Description: {}',
    '      制造商 / Manufacturer: {}': '      Manufacturer: {}',
    '\n{} [0-{}] (直接回车选择第一个 / Enter for first): ': '\n{} [0-{}] (Enter for first): ',
    '✅ 已选择 / Selected: {}': '✅ Selected: {}',
    '❌ 无效选择，请输入 0-{} 之间的数字\n   Invalid selection, please enter 0-{}': '❌ Invalid selection, please enter 0-{}',
    '❌ 无效输入，请输入数字\n   Invalid input, please enter a number': '❌ Invalid input, please enter a number',
    '\n❌ 用户取消 / User cancelled': '\n❌ User cancelled',
    '测试交互式端口选择 / Testing interactive port selection': 'Testing interactive port selection',
    '\n最终选择 / Final selection: {}': '\nFinal selection: {}',
}
