# SCS0009_ServoController

飞特 **SCS0009** 串行总线舵机调试工具（PySide6）：扫描总线、读写全部 44 个寄存器、位置控制、修改波特率、恢复出厂、以 `.xdat` 备份/恢复 EEPROM 参数。

## 安装与运行

```bash
pip install -r requirements.txt
python -m src.gui.factory_calibration_tool
```

连接 USB 转串口适配器，选择串口，扫描舵机 ID 后使用寄存器/位置面板。

## 教程

完整用户教程已迁移到仓库总教程：

- [SCS0009 舵机调试与标定](../tutorials/zh-hans/06-servo-tuning/scs0009.md)
- [SCS0009 接线与 ID](../tutorials/zh-hans/01-hardware/scs0009.md)

各系统旧版安装说明保留在 [`docs/`](docs/) 供参考；zh-hans 页面已改为指向中央教程的跳转页。

## 许可

MIT，见 [LICENSE](LICENSE)。
