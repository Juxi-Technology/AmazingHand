---
title: "PWM 手勢追蹤（GUI 內建 MediaPipe）"
description: "AmazingHand PWM 伺服馬達版手勢追蹤：GUI 內建 MediaPipe、相依套件安裝、執行、原理與限制、常見問題。"
version: pwm
---

# PWM 手勢追蹤（GUI 內建 MediaPipe）

> 以下命令在儲存庫的 `AmazingHand-PWM/` 目錄下執行。

本頁介紹 **PWM 伺服馬達版**的手勢追蹤：GUI 內建 MediaPipe，攝影機辨識手部關鍵點，即時映射到 8 路 PWM 伺服馬達。完整的 dora + MuJoCo IK 鏈路屬於 SCS0009 官方 Demo，見 [SCS0009 手勢追蹤](scs0009.md)。

> 鏈路：攝影機 → MediaPipe 手部骨架 → 四指彎曲/伸直角度 → ESP32 → PWM 伺服馬達
>
> 適用：ESP32-S3 + 8 路 PWM 伺服馬達。韌體燒錄見 [PWM 快速上手](../02-quick-start/pwm.md)，協定見 [PWM 協定與標定](../06-servo-tuning/pwm.md)。

> 需要完整 IK（MuJoCo + dora + Rust）的官方 Demo 不隨本模組分發；本教學只介紹模組自帶的 GUI 內建追蹤。

## 一、前置條件

1. **硬體**：ESP32-S3 + 8 路 PWM 伺服馬達通電、USB 接好、攝影機可用。
2. **韌體**：已燒錄（見 [PWM 快速上手](../02-quick-start/pwm.md)）。
3. **Python**：64 位 Python 3.12（mediapipe 0.10.14 只提供 64 位 wheel）。

## 二、安裝追蹤相依套件

在模組根目錄（`AmazingHand-PWM/`）執行：

```bash
tools/setup_tracking.bat
```

腳本會自動：尋找 64 位 Python → 建立 `tools/tracking_env` 虛擬環境 → 安裝 `tools/requirements-tracking.txt`（mediapipe 0.10.14、numpy<2、scipy、opencv、Pillow、pyserial）→ 驗證 mediapipe。

> 也可以手動安裝（用 64 位 Python 3.12）：
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 三、執行

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. 頂部選 ESP32 的 COM 埠 → 點「連線」。
2. 捲動到「手勢追蹤 (MediaPipe 攝影機)」面板。
3. 選攝影機號（預設 0）→ 點「開始追蹤」。
4. 把手放進畫面，靈巧手跟隨彎曲/伸直；點「停止追蹤」結束。

![GUI 內建手勢追蹤面板：攝影機選擇、開始追蹤與狀態提示](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 四、原理與限制

- MediaPipe 0.10.14 提取 4 指指尖的 3D 向量（手部座標系）。
- `hand_tracking.py` 的 `tips_to_angles()` 把每指映射為差動角度：
  - flex（彎曲/伸直）：三指用 z 分量，拇指用 y 分量；
  - base（左右擺）：固定 90（暫未實作左右擺）。
- 這些是**控制軸**；下發時程式再把它們合成為每根手指兩個伺服馬達的角度（同向=側擺，反向=屈伸）。
- GUI 內建 EMA 平滑（alpha=0.4）+ 60 ms 節流，減少抖動。

限制：沒有 IK，精度不如完整的 MuJoCo + dora 鏈路；適合演示和快速上手。

### 參數標定

- `hand_tracking.py` 底部的 `FLEX_SCALE` / `THUMB_FLEX_GAIN` 控制屈伸幅度和方向（目前程式碼取值以檔案為準）。
- 左右擺暫未實作，`base` 固定 90；需要左右擺請使用 SCS0009 官方 dora Demo。
- 修改後重新啟動 GUI 生效。

## 五、切換左右手

在 GUI 頂部勾選「右手」/「左手」。切換後拇指鏡像方向會不同，如果發現反了，勾選另一側測試。

## 六、常見問題

| 現象 | 處理 |
|------|------|
| 伺服馬達完全不動 | 查供電（5V 3A）、COM 埠、接線；確認韌體已燒錄 |
| 攝影機沒畫面 | 允許攝影機權限（設定→隱私→相機） |
| 手不跟隨 / 遲鈍 | 光線充足、手完整入畫、動作慢一點幅度大一點 |
| 手型反了 / 拇指方向反 | 勾選相反的左右手 |
| 換了 USB 埠找不到序列埠 | 在 GUI 裡重新選 COM 埠 |
| 啟動就報 mediapipe 缺失 | 用 `tools\tracking_env\Scripts\python` 啟動，或重跑 `tools/setup_tracking.bat` |

## 七、完整 IK / SCS0009 匯流排伺服馬達

- 完整 IK 鏈路（攝影機 → MediaPipe → MuJoCo + mink IK → AHControl → ESP32）來自獨立的 dora Demo 專案，不在本模組內；需要時請使用原始交付包或 MediaPipe 專案。
- SCS0009 匯流排伺服馬達由儲存庫的 `Amazinghand-web/` 與 `AmazingHandControl/` 支援。

## 目錄說明

| 路徑 | 內容 |
|------|------|
| `tools/hand_gui.py` | Tkinter 上位機（手勢、直驅、差動、內建追蹤） |
| `tools/hand_tracking.py` | MediaPipe 手部追蹤與角度映射 |
| `tools/setup_tracking.bat` | 建立 `tools/tracking_env` 並安裝追蹤相依套件 |
| `tools/requirements-tracking.txt` | 追蹤相依套件清單 |
| `tools/serial_test.py` | 命令列序列埠測試 |
