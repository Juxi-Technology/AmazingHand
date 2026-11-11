# AmazingHandControl

AmazingHand **SCS0009 串口总线舵机版**的 Python 上位机：图形界面与命令行，支持标定、姿态预设、序列、实时控制和遥测。

## 安装与运行

```bash
pip install -r requirements.txt
python amazing_hand_gui.py        # GUI
python amazing_hand_cmd.py --help # CLI
```

GUI 提供逐指控制、Open/Close/Center All、速度、姿态管理、序列、遥测曲线和舵机反馈表；CLI 可列出/应用姿态、播放序列。

## 教程

完整用户教程已迁移到仓库总教程：

- [SCS0009 桌面上位机（GUI 与 CLI）](../tutorials/zh-hans/04-desktop/scs0009.md)
- [SCS0009 接线与 ID](../tutorials/zh-hans/01-hardware/scs0009.md)
- [SCS0009 舵机调试与标定](../tutorials/zh-hans/06-servo-tuning/scs0009.md)

开发/参考文档仍保留在本模块：

- [配置文件格式](docs/zh-hans/CONFIG_FORMAT.md)
- [SCS0009 协议内存表](docs/zh-hans/scs_servo_protocol.md)
- [设计变更与标定说明](docs/zh-hans/CHANGES.md)
- [需求与验收测试](docs/zh-hans/REQUIREMENTS.md)

## 语言

模块参考文档提供 11 种语言，见 [`docs/`](docs/)。
