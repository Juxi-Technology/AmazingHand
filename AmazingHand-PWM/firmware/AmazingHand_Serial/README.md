# AmazingHand Serial Control — ESP-IDF 版

基于 **ESP-IDF v6.x + FreeRTOS** 的灵巧手固件，通过串口协议控制 8 路 PWM 舵机执行手势。组件化工程结构。

## 工程结构

```
AmazingHand_Serial/
├── CMakeLists.txt              # 顶层工程配置
├── sdkconfig.defaults          # 默认 Kconfig 配置
├── main/
│   ├── CMakeLists.txt
│   └── main.c                  # FreeRTOS 双任务 + 初始化（胶水层）
└── components/
    ├── hand_servo/             # 舵机驱动（LEDC PWM + 校准数据）
    │   ├── hand_servo.c
    │   └── include/hand_servo.h
    ├── hand_gestures/          # 手势参数宏 + 手势函数 + 左右手控制
    │   ├── hand_gestures.c
    │   └── include/hand_gestures.h
    └── hand_protocol/          # 串口帧解析 + 命令分发
        ├── hand_protocol.c
        └── include/hand_protocol.h
```

### 组件职责

| 组件 | 职责 | 依赖 |
|------|------|------|
| `hand_servo` | 舵机 LEDC 驱动、角度→脉宽映射、`middle_pos` 校准 | `esp_driver_ledc` |
| `hand_gestures` | 手势参数宏（用户可调）、全部手势函数、`abort`/`side` 运行控制 | `hand_servo` |
| `hand_protocol` | 帧解析状态机、校验、命令分发、响应发送 | `hand_gestures`、`hand_servo` |
| `main` | FreeRTOS 双任务（串口接收/手势执行）+ 初始化 | 三个组件 + `esp_timer` |

```
main ──→ hand_protocol ──→ hand_gestures ──→ hand_servo
```

## 构建环境

- ESP-IDF **v6.x**（推荐）或 v5.x
- 目标芯片：**ESP32-S3**
- 已配置 `idf.py` 环境变量

## 构建和烧录

```bash
# 1. 设置目标芯片
idf.py set-target esp32s3

# 2. (可选) 微调配置
idf.py menuconfig

# 3. 编译
idf.py build

# 4. 烧录 + 串口监控 (Windows 用 COM 口, 如 COM3)
idf.py -p COM3 flash monitor
```

## FreeRTOS 任务架构

```
uart_rx_task (prio 2)          gesture_task (prio 1)
      │                              │
  读取 stdin ──帧解析──► Queue ──► 取命令
      │                         (blocking) │
  Stop → abort flag               执行手势函数
  无效命令 → BUSY 响应             完成 → 0x10 响应
```

- `uart_rx_task`：非阻塞读取串口字节，喂给 `hand_protocol` 状态机，完整命令入队列
- `gesture_task`：从队列取命令，调用 `dispatch_command` 执行
- Stop 命令通过 `hand_gestures_set_abort()` 亚毫秒级中断手势

## 协议

115200-8N1，`0xAA` 命令帧 / `0xBB` 响应帧，XOR 校验。详细协议与命令参考见 [用户手册](../../docs/zh-hans/用户手册.md)。

## 手势参数调优

编辑 `components/hand_gestures/hand_gestures.c` 顶部"手势参数（用户可调）"区的 `#define` 宏，重新编译烧录即可。详见用户手册第 7 节。

## 上位机

- **图形界面**：模块的 `tools/hand_gui.py`（可用 PyInstaller 打包 exe）
- **命令行测试**：模块的 `tools/serial_test.py`
- **网页控制**：仓库根目录的 `Amazinghand-web-io/`（静态 Web Serial）或 `Amazinghand-web/server.py`（Python 服务端）
