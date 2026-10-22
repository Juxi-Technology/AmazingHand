# Amazinghand-web-io

**TL;DR** — this is the **only** front-end in the repository. By default the serial backend runs **inside the browser** (Web Serial API); when the page is served by [`../Amazinghand-web/server.py`](../Amazinghand-web/server.py) it switches to WebSocket automatically (the server injects `AH_BACKEND = "ws"`). No Python and no install are needed for the static mode: publish this folder and anyone with the board plugged in can open the link, grant port access once, and drive the hand.

用浏览器**直接**控制 AmazingHand。前端只有这一份：默认由页面内的 `io.js` 走 Web Serial；页面如果由 [`../Amazinghand-web/server.py`](../Amazinghand-web/server.py) 提供，则自动改用 WebSocket（服务端会在页面里注入 `AH_BACKEND = "ws"`），串口交给 Python 端。静态模式不需要 Python、不需要 WebSocket、不用在本机装任何东西。

> 需要 **Chrome / Edge**（桌面版）。Firefox 和 Safari 没有 Web Serial，打开后会进入只读模式：界面和摄像头可用，但舵机不动。

## 和 Python 版的区别

| | `Amazinghand-web/`（Python 服务端） | `Amazinghand-web-io/`（本目录，静态） |
|---|---|---|
| 前端 | **同一个目录**（server.py 把它当静态根） | 本目录 |
| 后端 | `server.py`：HTTP + WebSocket + rustypot | 页面内的 `io.js`，直连串口 |
| 运行方式 | 本机装 Python 依赖后跑脚本 | 打开网页即可（HTTPS 或 localhost） |
| 串口选择 | 列出本机所有串口 | 浏览器弹窗授权（只会记得授权过的设备） |
| 浏览器支持 | 任意现代浏览器 | **仅 Chromium 系**（Chrome / Edge） |
| 硬件要求 | 无 | 必须是安全上下文：`https://` 或 `localhost` |

界面、`config.json`、姿态库、换算公式、限位与急停逻辑只有一份实现，两种后端共用。

## 本地运行

在**仓库根目录**起一个静态服务（必须从仓库根起，下面资源路径才不会断）：

```bash
python -m http.server 8099
```

浏览器打开 <http://localhost:8099/Amazinghand-web-io/>，然后：

1. 点 **添加串口…** → 在浏览器弹窗里选中控制板（CH343 / CH340 等）
2. 点 **连接** —— 连上会自动开力矩并回中位
3. 用滑块 / 预设姿态 / 摄像头互动遥控控制；**急停**按钮一次松开全部舵机

> CH340/CH343 驱动：Windows 10/11 一般自动装好；如果弹窗里看不到设备，先确认设备管理器里出现了 COM 口。

## 在线地址

<https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/>

发布由仓库根的 [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) 负责，它把本目录与共用的 MediaPipe 资源一起上传。

MediaPipe 资源（约 42 MB）没有在仓库里存第二份：`tracking.js` 会先找 `./mediapipe/`，找不到再用 `../Amazinghand-web/web/mediapipe/`。

## 串口协议（为什么能直接驱动舵机）

和 Python 版一致，`io.js` 按 Feetech SCS 的 protocol v1 帧直接与 SCS0009 通讯：

```
FF FF ID LEN INST PARAM... CHECKSUM            # LEN = 参数长度 + 2
CHECKSUM = ~(ID + LEN + INST + ΣPARAM) & 0xFF
```

- 同步写（`INST=0x83`，广播 ID `0xFE`）：`goal_position` 地址 **42**、`goal_speed` **46**、`torque_enable` **40**
- SCS0009 是**大端**、**1024 步 / 300°**、中位 **511**（与 rustypot 的 `servo/feetech/scs0009.rs` 一致）
- 角度换算：`raw = trunc(rad × 1024 ÷ (300°)) + 511`；速度单位为 rad/s，`raw = trunc(v ÷ (300° ÷ 1024))`
- 姿态值 → 舵机角度：先按 `mirror_pose` 交换每根手指的两个值，再 `− angle_offset_deg`，偶数 ID 取负

安全策略沿用 Python 版：姿态限位 ±120°、变化 < 0.5° 不下发、写入间隔 ≥ 20 ms、Ctrl+C/急停即松开力矩。

## 已知限制

- **只支持 Chromium 系浏览器**；没有 Web Serial 时自动降级为只读模式（界面可用、舵机不动）
- 浏览器出于隐私**不允许网页静默枚举串口**，所以只能看到你授权过的设备；换电脑或换浏览器要重新授权一次
- 同一时间只有一个标签页能占用串口
- 页面关闭/刷新会释放串口，舵机保持最后位置（力矩仍开着）；重新连接会自动回中位

## 文件

| 文件 | 作用 |
|---|---|
| `io.js` | 页面内后端：配置加载、姿态换算、SCS0009 协议、Web Serial 串口管理、命令集 |
| `ws.js` | 传输层：页面由 `server.py` 提供时改走 WebSocket（接口与 `io.js` 相同） |
| `app.js` | 界面逻辑（两种后端共用，不区分串口在哪一端） |
| `tracking.js` | 摄像头互动遥控：MediaPipe 手部关键点 → 4 根手指（资源路径可解析） |
| `i18n.js` | 中英文案 |
| `config.json` | 舵机映射 / 姿态库 / 限位 / 摄像头参数（与 Python 版同一个文件） |
| `index.html` · `style.css` | 界面 |
