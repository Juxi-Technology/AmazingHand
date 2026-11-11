---
title: "AmazingHand 网页控制"
description: "AmazingHand 网页控制总览：启动方式、驱动切换、串口栏、手动控制、摄像头遥操作与安全设计。"
version: both
---

# AmazingHand 网页控制

用浏览器控制 AmazingHand 灵巧手，**左手 / 右手两种模式**，两种操作方式：

- **手动控制** —— 8 个舵机滑块 + 19 个预设姿态 + 一键回中位
- **摄像头互动遥控** —— 浏览器本地 MediaPipe 识别手部动作，实时映射到手指（画面不出本机）
- **中英文切换** —— 右上角切换，选择记在浏览器里，下次打开还是上次那门语言

> 本页是**通用网页控制说明**。SCS0009 专用映射/换算见 [SCS0009 网页控制](scs0009.md)；PWM 专用接线/烧录/标定见 [PWM 网页控制](pwm.md)。

## 快速开始

打开终端，进入到Amazinghand-web目录下：

```bash
pip install -r requirements.txt

python server.py --no-connect   # 推荐：先起服务，串口在网页里选（不碰舵机）

# python server.py                # 自动探测串口并连接
# python server.py --port COM9    # 指定串口
# python server.py --hand left    # 只启用左手
# python server.py --driver pwm   # 使用 ESP32-S3 PWM 舵机版本
# python server.py --dry-run      # 完全不开串口，只验证界面
```

浏览器打开 **http://localhost:8000** 。

也可以直接用静态前端（Web Serial，不需要 Python 服务端）：

- 在线：<https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/>（Chrome / Edge）
- 本地：在仓库根目录运行 `python -m http.server 8099`，打开 <http://localhost:8099/Amazinghand-web-io/>

### 在网页里选串口

页面顶部有一排工具条，先选驱动，再选串口：

```
驱动  [SCS0009 总线 ▾]  串口  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [刷新]  [连接]  [断开]  已连接 COM3
```

- 驱动下拉：**SCS0009 总线**（官方总线舵机，默认）或 **PWM（ESP32-S3）**（见 [PWM 网页控制](pwm.md)）
- 下拉框列出本机所有串口，常见 USB 转串口芯片（CH34x / CP210x / FTDI 等）标 **★** 并排在最前
- 点 **刷新** 重新扫描（插拔板子后用）
- 点 **连接** 连接选中的串口；连上后会自动回中位
- 点 **断开** 先松开力矩再断开，舵机不会僵在原位（PWM 版没有力矩命令，见下文说明）
- 换串口直接选新的点「连接」即可，旧口会自动关掉

> **静态部署（GitHub Pages）没有 Python 服务端**：浏览器出于隐私不能静默枚举串口，只能看到你授权过的设备。此时点 **添加串口…**，在浏览器弹窗里选择控制板；上面“列出本机所有串口”的行为仅适用于 `server.py` 服务端模式。

![网页顶部：驱动选择、串口工具条与左右手切换](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **`--no-connect` 是配合这个流程用的**：启动时只起服务、完全不碰串口，
> 所以不会因为自动连错口而让手乱动。想让它启动就自动连，去掉这个参数。

串口日志写在 `server.log`（双击 .bat 启动时窗口一闪而过，看这个文件）。

### 接线检查

列出扫到的舵机 ID，并和 `config.json` 逐只手核对。

```bash
python tools/scan_servos.py --port COM9
```

COM9改为自己实际的端口号

> 这个工具只适用于 **SCS0009 总线舵机**。PWM 版本的接线检查见 [PWM 网页控制](pwm.md)，或用 `AmazingHand-PWM/tools/serial_test.py`。

---

## 预设姿态（19 个）

![手动控制面板：四指滑块、19 个预设姿态与操作按钮](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| 姿态 | 说明 | 姿态 | 说明 |
|---|---|---|---|
| `open` | 张开 | `wave1` | 挥手 |
| `close` / `stone` | 握拳 | `wave_r` / `wave_l` | 左右摆 |
| `ok` | OK | `ring_close` | 仅无名指握 |
| `greeting` | 打招呼 | `middle_close` | 仅中指握 |
| `victory` / `two` / `scissors` | 剪刀手 / 二 | `pointer_close` | 仅食指握 |
| `paper` | 布 | `thumb_close` | 仅拇指握 |
| `one` / `three` | 一 / 三 | `hifive` | 击掌 |

要自行修改姿态的话，编辑 `config.json` 的 `poses` 段；键名对应官方 YAML 里的名字。

### 左右手可以是不同的姿态值

每条姿态里的 `positions` 是**左右手共用**的。如果哪只手因为机械装配差异需要另一套值，
在同一条里加一个 `right` 或 `left` 键即可，它会覆盖 `positions`：

```jsonc
"close": {
  "label": "握拳",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // 两只手共用
  "right":     [ ... 8 个值 ... ]                   // 可选：只给右手用
}
```

---

## 两种模式

| 模式 | 行为 |
|---|---|
| **右手** | 只下发右手 8 个舵机 |
| **左手** | 只下发左手 8 个舵机（SCS0009 自动应用镜像和 −35.16° 偏移；PWM 使用左手通道映射）|

一次只控制一只手，用顶部「控制对象」切换；切换不影响另一只手，它保持当前姿态停在原地。SCS0009 双手可以接在同一根总线上；PWM 每只手各由一块 ESP32-S3 控制。

---

## 摄像头互动遥控

浏览器本地跑 MediaPipe 手部关键点（资源在 `Amazinghand-web/web/mediapipe/`，离线可用；页面也会优先探测 `Amazinghand-web-io/mediapipe/`），
把 21 个关键点换算成 4 根手指的姿态值，实时下发给当前选中的手。

![摄像头面板：启动、骨骼显示、三步姿势采集与状态区](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 一、先采三个姿势

启动摄像头后，摆好一个姿势、点对应的按钮采一次（约 1 秒取平均）。
顺序随意，采错了点同一个按钮重采。**三个都采完状态才会变绿**；
采完之前不下发，机械手保持在中位姿态不动。

| 按钮 | 姿势 | 给出什么 |
|---|---|---|
| ① 伸直张开 | 手指伸直张开，大拇指向外 | 屈伸的「伸直」端 + 侧摆的「张开」端 |
| ② 伸直合拢 | 手指伸直合拢，大拇指贴合食指 | 侧摆的「合拢」端 |
| ③ 握拳 | 握拳，大拇指贴近掌心 | 屈伸的「握拳」端 |

### 二、两根轴各自两点实测

屈伸和侧摆都用**两个实测端点定一条直线**：

```
t    = (测量值 − 端点A) / (端点B − 端点A)        // 钳在 0~1
目标 = A的目标值 + (B的目标值 − A的目标值) × t
```

好处是**各手指测量值的正负方向被自动吸收** —— 所以不需要「某根手指要勾反向」
这类开关（食指和无名指分处中轴两侧、拇指关节链又不同，方向本来就是反的，
但两个实测端点一夹就自动对上了）。

端点目标值在 `config.json` 的 `camera` 段：

| 轴 | 端点 | 无名指 | 中指 | 食指 |
|---|---|---|---|---|
| 屈伸 | 伸直 → 握拳 | −50 → 90 | −50 → 90 | −50 → 90 |
| 侧摆 | 合拢 → 张开 | −45 → +45 | 0 → 0 | +45 → −45 |

中指侧摆两端都是 0（它不左右摆）。

### 三、大拇指只做屈伸 ⚠️

大拇指的 CMC 是**对掌关节**，弯曲和左右摆耦合得很紧 —— 拇指贴着食指时它已经在
侧摆位上了，那一刻量到的"屈伸零点"是被污染的。硬拆成两根轴，结果是两根都不准。

所以大拇指**只做屈伸、侧摆恒为 0**（两个舵机的侧摆差动量为 0）。它要的两个参考姿势就是
①（指外）和 ③（指向掌心），不用额外采。

### 四、侧摆会随弯曲衰减

最终侧摆按下式收放：

```
side = side_measured × (1 − curl)
```

`splayDeg` 取的是 MCP→PIP 方向在掌面横轴上的投影，而手指弯曲**正是绕这根轴转的** ——
弯到一定程度这个投影会翻向，"张开度"突然甩到另一头。

不衰减的话，这个突跳会顺着 `servo2 = 屈伸 − 侧摆` 把**偶数 ID 舵机**带着反向掉头
（奇数 ID 拿到的是 `屈伸 + 侧摆`，变化方向相反，所以不那么明显）。
现象就是「握拳握到一半，12 和 16 号舵机猛地反转」—— 12 是左手无名指的第二个舵机、
16 是左手食指的第二个舵机，正好是侧摆分量非零时被差动带走的那两根。

加上衰减后，握紧时侧摆**恒为 0**，跟测量值多离谱无关。而且握拳本来就该是并拢的。

### 五、骨骼配色

| 手指 | 颜色 |
|---|---|
| 大拇指 | 橙 |
| 食指 | 红 |
| 中指 | 蓝 |
| 无名指 | 黄 |
| 小拇指 | 暗灰 |
| 掌骨 | 中性灰 |

小拇指不参与手势映射，但它的**根部 MCP（17 号点）用来定右手的手掌坐标系**，所以不能删。

### 调参速查

| 想改什么 | 改哪儿 |
|---|---|
| 各轴目标值 | `config.json` 的 `camera` 段 |
| **左右手侧摆方向相反** | `camera.side_sign` 里那只手改成 `-1`（`1` = 原样）|
| 平滑程度 | `tracking.js` 的 `SMOOTH`（默认 0.35；越小越稳但越迟钝） |
| 手指弯曲的判定快慢 | 重新采一次三个姿势 |

`side_sign` 是按**「控制对象」选的那只手**生效的，改完刷新页面即可，不用重启服务：

```jsonc
"side_sign": { "right": 1, "left": -1 }   // 左手把整根侧摆轴取反
```

屈伸（flexion）不受 `side_sign` 影响。

---

## 项目结构

```
Amazinghand-web-io/          前端（静态，可单独部署）
├── index.html
├── app.js                   界面、驱动切换、姿态与摄像头 UI
├── io.js                    SCS0009 Web Serial 后端
├── pwm.js                   PWM Web Serial 后端
├── common.js                共享配置、姿态换算与限位
├── ws.js                    WebSocket 后端（Python 服务端模式）
├── tracking.js              MediaPipe 摄像头追踪
├── i18n.js                  中英文文案
├── config.json              驱动、舵机映射、姿态库、相机参数
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                HTTP + WebSocket + 串口服务端
├── requirements.txt
├── tools/scan_servos.py     扫描 SCS0009 总线并核对 ID
└── web/mediapipe/           MediaPipe 资源（离线，约 42MB）
```

前后端协议：

```jsonc
// 前端 → 后端   target: "left" | "right"
{ "cmd": "ports" }                                  // 重新扫描串口
{ "cmd": "driver", "driver": "pwm" }                // scs0009 | pwm
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }   // 仅 SCS0009
{ "cmd": "stop" }

// 后端 → 前端
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left", "driver": "scs0009",
  "capabilities": { "torque": true, "speed": true }, "pwm": {...},
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "连接 COM_FAKE 失败：系统找不到指定的文件。" }
```

---

## 安全设计

| 项 | 说明 |
|---|---|
| **姿态限位** | 姿态值 ±120°（`config.json` 的 `limits`），所有 19 个姿态已核对不超限 |
| **变化去重** | 变化 < 0.5° 不下发，避免总线被噪声占满 |
| **写入限流** | SCS0009 最小间隔 20ms；PWM 直驱约 30ms |
| **急停** | SCS0009：松开全部力矩；PWM：发送 `0xFF` 中止手势，舵机仍通电保持位置 |
| **退出保护** | SCS0009：Ctrl+C 关闭力矩；PWM：断开串口后舵机保持位置 |
| **单手调试** | `--hand left/right` |

---

## 常见问题

**摄像头识别不准** → 光线均匀、手掌正对镜头。`tracking.js` 里 `SMOOTH`（默认 0.35）越大越平滑但越迟钝。

**摄像头手势不对、某根手指不跟手** → 先确认三个姿势都采完（状态变绿）；方向反了就重采对应姿势；大拇指只做屈伸，不参与侧摆。

**握拳握到一半某舵机猛地反转** → 检查侧摆是否随弯曲衰减到 0（`side *= (1 - curl)`），以及侧摆控制量的符号/大小是否异常。

**SCS0009 方向/ID/中位问题** → 见 [SCS0009 网页控制](scs0009.md) 和 [SCS0009 调试与标定](../06-servo-tuning/scs0009.md)。

**PWM 连接/波特率/标定问题** → 见 [PWM 网页控制](pwm.md)。

**更多问题** → [FAQ](../08-faq/faq.md)。
