[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | 繁體中文

# AmazingHand 控制器 – 使用者手冊

> **版本：** 2026-03-22  
> **適用對象：** `amazing_hand_gui.py`（GUI）、`amazing_hand_cmd.py`（CLI）

---

## 一、簡介

AmazingHand 控制器 GUI 為使用 Feetech SCS0009 舵機驅動的八舵機機械手提供即時監控與手動控制。介面劃分為手指控制、全域管理、遙測視覺化和活動日誌等面板。本指南將帶你了解安裝、介面導覽和常見工作流程。

> **提示：** 操作 GUI 時請保持本手冊開啟。應用程式內嵌的工具提示會在你將游標懸停於控件上時複述相同的說明。

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 二、快速上手清單

1. **安裝相依套件**（每個環境一次）：
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **為硬體上電：** 將 5 V 電源接到舵機鏈，並插上 USB 序列埠轉接器。
3. **啟動 GUI：**
   ```bash
   python amazing_hand_gui.py
   ```
4. **連線到控制器：** 選擇序列埠 **Port**（例如 `COM9`）並點擊 **▶ Connect**。
5. **驗證遙測：** 查看圖表和回饋表中的即時更新。

---

## 三、介面概覽

```
+--------------------------------------------------------------------------------+
|                              AmazingHand Controller                            |
+---------------------------+-----------------------------------------------+----+
| Finger Controls           | Chart Controls & Telemetry Plot                    |
| (Ring – Middle – Pointer) | (Display menu, chart canvas)                       |
+---------------------------+-----------------------------------------------+----+
| Control Stack             | Thumb finger   | Feedback Table (Servo Metrics)    |
| (Connection, Global, Pose,| control        | (Goal, Position, Load, etc.)      |
|  Sequence)                |                |                                   |
+---------------------------+                                                    |
| Execution Log & Status    |                                                    |
+--------------------------------------------------------------------------------+
```

![Main window overview highlighting the major panels](../en/screenshots/mainscreen.png)

### 3.1 面板一覽

| 面板 | 位置 | 用途 |
|-------|----------|---------|
| **Finger Controls** | 左側，上部（3 指）+ 右下（拇指） | 每個手指對的獨立滑桿與速度選擇器。包含 mimic 指示與逐手指狀態 LED。 |
| **Right Control Stack** | 左側，右下 | 連線設定、全域控制、姿態管理和序列播放器。 |
| **Telemetry Panel** | 右側 | 帶縮放/平移滑桿的即時圖表，以及可設定的回饋表。 |
| **Execution Log** | 底部 | 狀態訊息、警告和序列進度的訊息流。 |

---

## 四、面板詳解

### 4.1 手指控制面板（左欄）

每個手指控件控制一對舵機（位置 + 左右偏移）：

- **模式切換：** 在 **Auto**（base + offset 滑桿）與 **Raw**（直接舵機目標）之間切換。
- **狀態 LED：** 灰色（閒置）、綠色（運動）、紅色（可能阻塞，依據負載與目標比較）。
- **位置滑桿：** 0–110°（張開到握緊）。滑鼠滾輪以 1° 調整；拖曳會快速跟隨。
- **左右滑桿：** ±40°，用於橫向調整。拇指的左右滑桿是**反向**的，使物理方向與手的解剖朝向一致 —— 向右拖曳時，拇指按其硬體安裝方向朝正方向移動。
- **速度選擇器：** 1–6 下拉式選單，控制該手指對兩個舵機的運動速度。
- **Mimic 核取方塊：** 在 Auto 模式下鏡像來自源手指的開合運動，實現協同運動。

**手指模式：Auto 與 Raw**

- **Auto 模式**（預設）顯示開合滑桿、橫向偏移滑桿、速度下拉式選單和 center 按鈕。GUI 使用儲存在 `data/hand_config.yaml` 中的標定極值，將這兩個滑桿的值混合成舵機指令，因此該手指對能跟隨自然的手指標定姿態，無需手動做舵機數學換算。Mimic 在此保持可用 —— 在多根手指上啟用它，即可讓它們與你當前正在調整的那根手指同步運動。
- **Raw 模式**用兩個按舵機標註的垂直滑桿替換 Auto 控件。在測試限位、驗證標定或診斷連桿問題時，移動它們可直接控制底層舵機角度。center 按鈕和 mimic 核取方塊被停用，因為 Raw 繞過了自動混合邏輯；鍵盤快速鍵仍然有效，上/下驅動舵機 1，左/右驅動舵機 2。Raw 使用最後選擇的速度值，因此如果需要特定運動速率，請在切換前設定好速度。

**Auto 模式如何計算舵機目標**

- 開合滑桿值被夾到 `limits.base_min/base_max`，然後歸一化（`t = base / base_max`），在手指每一側的 `auto_extremes` 張開與握緊姿態之間插值。
- 左右偏移滑桿被夾到 `limits.side_min/side_max` 並轉換為混合因子（`u`）。負偏移從中心姿態向 `left_open`/`left_closed` 線性插值；正偏移向右側極值線性插值。
- 無橫向偏移時，兩個舵機直接接收 base 滑桿值。最終舵機目標在下發前被夾到 `limits.servo_min/servo_max`，使運動保持在標定的安全範圍內。

鍵盤快速鍵是對滑桿的補充（見 §5.2）。

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 全域控制堆疊（手指面板右側）

1. **Connection：** 連接埠與鮑率選擇（連線時兩個下拉式選單均被停用）、連線/中斷連線按鈕。底部狀態列報告成功或錯誤。
2. **Global Controls：**
   - **Open All / Close All / Center All** —— 立即套用於每根手指。
   - **Global Speed 下拉式選單** —— 將逐手指速度選擇器設為同一個值（1–6）。
3. **Pose Management：** 儲存、載入、套用和刪除 `data/hand_config.yaml` 中儲存的姿態。
   - 版面配置：`Pose: [dropdown]  ✓ Apply  🗑 Delete  Name: [entry]  ➕ Add New`
   - **🗑 Delete** 永久移除所選姿態（會顯示確認對話方塊）。
4. **Sequence Player：** 選擇並執行多步動畫，可選迴圈。透過 **🔧 Manage** 存取序列管理員對話方塊。

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 遙測與回饋面板（右欄）

- **控件列：**
  - 暫停/恢復圖表更新。
  - 滾動視窗開關。
  - 指標選擇（位置、負載、速度、溫度、電壓、運動標誌）。
  - 模式切換（Multi-Servo 與 Scope），後者帶舵機選擇器。
  - 舵機可見性下拉式選單，帶 "All/None/Clear" 輔助項。
  

![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### 圖表模式

- **Multi-Servo**（預設）在圖表上保留每條已啟用的舵機曲線。用 **Servos** 下拉式選單快速開關分組，比較各手指的運動或負載。
- **Scope** 啟用 **Scope Servo** 選擇器，讓你聚焦單一通道，同時仍使用相同的指標核取方塊。將此模式與舵機可見性選單搭配（例如先全部隱藏，再重新啟用該 scope 舵機），即可獲得不受其他曲線干擾的示波器式檢視。
- 無論何種模式，遙測表始終呈現所有舵機，便於你將聚焦的圖表與更全面的資料快照相互對照。
- **圖表區：** 顯示所選遙測的 Matplotlib 圖。透過滑桿縮放：
  - **Y Zoom / Pan：** 垂直方向的縮放與平移。
  - **Time Zoom / Pan：** 聚焦近期歷史或更早的樣本。
- **回饋表：** 可捲動的網格，彙總每個舵機的 Goal、Position、Speed、Load、Voltage、Temperature、Status 和 Moving 標誌。

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 執行日誌與狀態列

日誌位於手指面板下方，按時間順序記錄操作。狀態列顯示最新操作或警告。

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 五、操作機械手

### 5.1 連線硬體

1. 為舵機上電並連接 USB 轉接器。
2. 啟動 GUI 並確認自動選取了正確的 **Port**（Windows 上為 `COM*`，Linux/macOS 上為 `/dev/tty*`）。
3. 點擊 **▶ Connect**。成功後會改變按鈕狀態並更新狀態列。
4. 若連線失敗，請檢查線纜、電源和連接埠分配。

### 5.2 手動控制與快速鍵

- 用按鍵 **1–4** 選擇手指（1 = Ring，2 = Middle，3 = Pointer，4 = Thumb）。
- **方向鍵：** 上/下調整位置；左/右調整橫向偏移。
- 按住 **Shift** 使步長乘以 5；**Ctrl** 乘以 10。
- **Q / E：** 將所選手指完全握緊 / 張開。
- **C：** 將橫向偏移回正。
- 螢幕上的滑桿即時反映鍵盤輸入。

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 設定速度

- 逐手指速度下拉式選單（1 = 慢，6 = 快）控制舵機速度。
- **Global Speed** 選擇器同步所有手指的速度。
- 運動過程中在回饋表（`Speed` 列）觀察速度變化。

### 5.4 套用與刪除姿態

1. 用滑桿或鍵盤快速鍵擺放手指位置。
2. 在 **Pose Management** 中輸入唯一名稱並點擊 **➕ Add New**。
3. 要套用，從下拉式選單選擇該姿態並點擊 **✓ Apply**。
4. 要刪除，從下拉式選單選擇該姿態並點擊 **🗑 Delete**。確認對話方塊可防止誤刪。

> 姿態僅儲存舵機位置；速度由 GUI 設定在執行時決定。

### 5.5 建構與執行序列

1. 在 Sequence Player 中點擊 **🔧 Manage**。
2. 在對話方塊中：
   - 用 **Available Poses** 清單新增步驟（雙擊或按 **➕ Add**）。
   - 透過微調框調整逐手指速度，並設定可選的步驟延時。
   - 用 **⏱ Delay** 插入專門的休眠間隔。
   - 用 ↑/↓ 按鈕調整步驟順序。
   - 輸入名稱並點擊 **💾 Save Sequence**。
   - 點擊 **▶ Execute** 可在不儲存的情況下測試。
3. 回到主視窗，選擇該序列並按 **▶ Play**。啟用 **Loop** 可連續播放。

> 序列定義位於 `data/hand_config.yaml` 的 `sequences` 鍵下。迴圈由執行端控制，而非 YAML。

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 監控遙測

- 確保在 **Display** 選單中勾選了所需指標。
- 用縮放/平移滑桿聚焦感興趣的區段。
- 將游標懸停在圖表元素上（Matplotlib 標準互動）即可查看數值。
- 回饋表非同步更新；高亮的儲存格表示最近發生的變化。
- 若圖表變得雜亂，點擊 **⌫ Clear** 重設已擷取的資料。

---

## 六、命令列介面（`amazing_hand_cmd.py`）

CLI 讓你無需啟動 GUI，即可直接從終端機套用姿態和播放序列。它讀取同一個 `data/hand_config.yaml` 檔案。

### 6.1 基本用法

```bash
# List all saved poses and sequences
python amazing_hand_cmd.py --list

# Apply a single pose
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close

# Play a sequence once
python amazing_hand_cmd.py --sequence demo

# Play a sequence in a loop (Ctrl+C to stop)
python amazing_hand_cmd.py --sequence wave --loop
```

### 6.2 選項

| 選項 | 預設值 | 說明 |
|--------|---------|-------------|
| `--pose NAME` | – | 套用指定名稱的姿態後結束 |
| `--sequence NAME` | – | 播放指定名稱的序列後結束 |
| `--list` | – | 列出所有姿態與序列 |
| `--loop` | off | 連續迴圈播放序列，直到 Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | 序列埠覆寫 |
| `--baudrate N` | `1000000` | 鮑率覆寫 |
| `--config PATH` | `data/hand_config.yaml` | 其他設定檔的路徑 |

### 6.3 說明

- 連線時**啟用**力矩，結束時**停用**力矩，使舵機在指令碼結束後放鬆。
- 每步的速度與延時行為與 GUI 序列播放器完全一致。
- `--loop` 旗標只能與 `--sequence` 一起使用。

---

## 七、故障排除

| 現象 | 建議操作 |
|---------|-----------------| 
| **未列出序列埠** | 重新插拔 USB 轉接器、安裝驅動程式，或重新啟動 GUI。 |
| **Connect 按鈕變灰** | 已連線；請先點擊 **⏹ Disconnect**。 |
| **調整視窗大小時介面卡頓** | 效能最佳化（防抖 resize、限流重繪）已將影響降到最低，但關閉不必要的視窗也有幫助。 |
| **序列未能驅動所有手指** | 檢查每步速度，並確保每個姿態都包含全部 8 個舵機值。 |
| **阻塞指示持續存在** | 檢查機械卡阻；當目標與實際位置差異顯著且無運動時，會觸發阻塞狀態。 |

---

## 八、附錄

### 8.1 檔案結構

```
AmazingHandControl/
├── amazing_hand_gui.py          # GUI application
├── amazing_hand_cmd.py          # CLI tool
├── data/hand_config.yaml        # Poses & sequences
├── data/config.yaml             # Application settings
├── docs/<lang>/user_manual.md        # This document
├── docs/<lang>/CONFIG_FORMAT.md      # YAML config file reference
├── docs/en/screenshots/              # PNG captures embedded in this manual
├── docs/<lang>/scs_servo_protocol.md # SCS servo protocol reference
└── README.md                    # Quick reference
```

### 8.2 實用連結

- [AmazingHand（官方專案）](https://github.com/pollen-robotics/AmazingHand)
- [Feetech 舵機除錯工具](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [舵機識別教學](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 九、修訂歷史

| 日期 | 作者 | 說明 |
|------|--------|-------|
| 2026-03-22 | Ingo | 新增 CLI（`amazing_hand_cmd.py`）章節；手冊版本提升。 |
| 2026-03-21 | Ingo | 面板版面更新：Ring/Pointer 互換，拇指移到右側，控制堆疊移到左側。拇指左右滑桿改為反向。在 Apply 與 Name 之間新增刪除姿態按鈕。連線時連接埠與鮑率下拉式選單現在被鎖定。鍵盤快速鍵 1–4 現在對應為 Ring/Middle/Pointer/Thumb。 |
| 2025-11-25 | Ingo | 新增擴充截圖庫、圖表模式說明，並更新了面板講解。 |
| 2025-11-25 | Ingo | 初始手冊，涵蓋 UI 面板、工作流程和遙測用法。 |
