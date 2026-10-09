[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | 繁體中文

# AmazingHand 控制程式 · 最佳化說明

本文記錄本專案在原始版本基礎上做了哪些變更、為什麼改、以及改完後的實際效果。

原始版本：`Betatester777/AmazingHandControl`（AmazingHand 的 Python GUI + CLI 工具）
適用硬體：JuxiTechnology 靈巧手（Feetech SCS0009 舵機 × 8，電位器回饋）—— **左右手均支援**，啟動時選擇

---

## 目錄

1. [角度體系重新標定](#一角度體系重新標定)
2. [全域按鈕：改用舵機原始值精確控制](#二全域按鈕改用舵機原始值精確控制)
3. [新增 Middle position 按鈕](#三新增-middle-position-按鈕)
4. [修復 GUI 與 CLI 動作不一致](#四修復-gui-與-cli-動作不一致核心問題)
5. [Pose 資料修正](#五pose-資料修正)
6. [序列播放器：時序與診斷修復](#六序列播放器時序與診斷修復)
7. [Servo Feedback 新增原始位置行](#七servo-feedback-新增原始位置行)
8. [**左右手支援**](#八左右手支援)
9. [序列埠連接埠自動偵測](#九序列埠連接埠自動偵測)
10. [設定項速查](#十設定項速查)
11. [實機驗證資料](#十一實機驗證資料)
12. [檔案變更清單](#十二檔案變更清單)

---

## 一、角度體系重新標定

### 1.1 角度限位：`0..110` → `-75..75`

原版按 `0° = 張開，110° = 握緊` 標定。實測本機行程落在 `-75..75`，因此重新標定。

**`data/config.yaml`**

| 設定項 | 原值 | 新值 |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**19 個 pose 全部按新尺度重新標定**，例如 `open` 由 `[0]*8` 改為 `[-35]*8`，`close` 由 `[110]*8` 改為 `[75]*8`。

### 1.2 左右擺幅：`±40°` → `±35°`

左右滑桿的歸一化因子是 `u = |side_offset| / |side_min|`，只改限位不會改變實際張開幅度，必須**同時**改 `auto_extremes` 裡的極值。兩者一起改後：

| | 原（±40） | 現（±35） |
|---|---|---|
| 滑桿範圍 | −40 … +40 | −35 … +35 |
| 全開時左右擺到極限 | `(32, -40)`，開合差 **72°** | `(32, -35)`，開合差 **67°** |

### 1.3 統一至廠商基準

廠商 Arduino 演示程式（`Amazing_RHand_Demo.ino`）的換算為：

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

驗證 rustypot 1.4.2 原始碼（`src/servo/feetech/scs0009.rs`）：

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**結論：兩邊的「度」是同一個刻度（0.29297°/step，300° 滿量程，raw 0–1023），不存在比例錯誤。** 唯一的系統性差異是零點：

- rustypot 固定以 raw **511** 為中心
- 廠商韌體用每軸標定值 `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

兩者相差 **±60 raw = ±17.6°**。這正是下面「Middle position」按鈕要處理的問題。

---

## 二、全域按鈕：改用舵機原始值精確控制

### 2.1 問題

原版 `open_all()` / `close_all()` 裡寫死了角度值：

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # 写死的 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # 写死的 110
```

這兩個值來自**舊標定尺度**（0=張開、110=握緊）。重新標定到 `-35 / 75` 之後：

- `open_all` 設 0° → 換算後 raw = **511**，也就是**機械中位附近**，手指根本沒張開
- `close_all` 設 110° → 被 `base_max = 75` 夾住，實際只到 75；而介面標籤仍顯示 110°

### 2.2 方案：新增原始值直發通道

角度通道要經過 `base/side` 插值模型，無法精確命中指定的 raw 值（後面第四節會詳細說明）。因此為全域按鈕新增一條**直接寫舵機原始值**的通道。

**關鍵實作細節**：沒有使用 rustypot 的 `sync_write_raw_goal_position`。檢視巨集生成原始碼後發現，原始值介面直接 `values.to_le_bytes()` 上線，而轉換介面的 `to_raw()` 先做了 `to_be()`：

```rust
fn to_raw(value: f64) -> i16 { let a = (... ) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- 没有 to_be
```

直接傳 `451` 會發出 `0xC301`（即 49921）。因此改用 `sync_write_goal_position`（弧度），反推出**能精確落在目標 raw 上**的弧度值，取每個 raw 階梯的中點以規避截斷誤差。

### 2.3 三個按鈕的原始值目標

新增 `data/config.yaml` → `raw_positions`（下標 0 → 舵機 ID 1）：

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| 按鈕 | 行為 | 舵機 ID 1–8 原始位置 |
|---|---|---|
| ✋ Open All | 完全伸直 | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | 完全握緊 | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | 左右回正（不改開合） | — |
| **Middle position** | **回到標定中位** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` 是**每隻手需要標定的值**。廠商對 `MiddlePos` 的原話是 "replace values by your calibration results"，換手或換舵機後需重新量測。

### 2.4 滑桿同步的取捨

原始值繞過了 `base/side` 插值模型，沒有精確對應值，因此按鈕執行後滑桿會被設到**最接近的整數**：

| 位置 | 滑桿顯示 |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

代價是：之後再碰滑桿，手會跳到差約 1 個原始單位（0.3°）的位置。這是刻意的取捨 —— 優先保證按鈕命中的精確性。

---

## 三、新增 Middle position 按鈕

在 `✋ Open All` / `✊ Close All` / `⊙ Center All` 右側新增 **Middle position** 按鈕，功能是回到**廠商標定的機械中位**（raw 451/571）。

**為什麼需要它**：`open_all` 到 `close_all` 的中點並不是機械中位。廠商的中位是 `MiddlePos`，相對 raw 511 偏了 ±60 raw（±17.6°）。上電後需要有一個明確的、可重現的歸零位置。

---

## 四、修復 GUI 與 CLI 動作不一致（核心問題）

### 4.1 現象

**同一個 pose，在 GUI 裡點 `✓ Apply` 和用 CLI `--pose` 執行，手會做出不同的動作。**

### 4.2 根因

GUI 的 pose 下發走的是：

```
set_positions(p1, p2)  →  decompose 拆成 (base, side) 存进滑块
                       →  get_positions() 在 Auto 模式下用 compute_auto_positions() 重算
```

而 `compute_auto_positions` **不是** `decompose_servo_positions` 的精確逆運算（中心與極值都是經驗值）。CLI 的 `apply_pose()` 則是直接下發。

實測 **19 個 pose 裡有 12 個失真**，偏差最大到 32°：

| pose | 儲存值 | GUI 實際發出 | 偏差 |
|---|---|---|---|
| `ring_close` | Ring `(75, -35)` | Ring `(43, -5)` | **32° / 30°** |
| `middle_close` | Middle `(75, -35)` | Middle `(43, -5)` | **32° / 30°** |
| `pointer_close` | Pointer `(75, -35)` | Pointer `(43, -5)` | **32° / 30°** |
| `thumb_close` | Thumb `(75, -35)` | Thumb `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Thumb `(-75, -3)` | Thumb `(-75, 9)` | 12° |
| `greeting` | Ring `(-18, -57)` | Ring `(-10, -68)` | 8° / 11° |
| `victory` | Middle `(-68, -9)` | Middle `(-75, 1)` | 7° / 10° |
| `paper` | Pointer `(-52, -22)` | Pointer `(-59, -16)` | 7° / 6° |
| `ok` | Pointer `(36, 46)` | Pointer `(38, 43)` | 2° / 3° |

**規律：凡是每根手指 `pos1 == pos2` 的對稱 pose（`open` `close` `stone` `two` `scissors` `one` `three`）都能精確還原；凡是帶左右張開的非對稱 pose 都會走形。**

### 4.3 方案

新增 `_send_exact_positions()`，按 `SERVO_PAIRS` 順序把角度直接發給 8 個舵機（等價於 CLI 的 `apply_pose`）。兩個 pose 入口都改用它：

- Pose Management 的 `✓ Apply` 按鈕
- `_apply_pose_from_config()` —— 序列播放器與 pose 列表

滑桿仍由 `set_positions()` 更新（僅作顯示），但**不再由滑桿決定下發值**。

### 4.4 效果

修復後，**19 個 pose 全部滿足 `儲存值 == GUI 下發值 == CLI 下發值`**。

**副作用**：GUI 裡這些手勢的實際動作會變化（尤其是非對稱姿勢），這正是修復的預期效果。

---

## 五、Pose 資料修正

### 5.1 四個 `*_close` 姿勢的寫法錯誤

```yaml
# 修正前 —— 目标手指 (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` 拆解後是 `base = 20, side = -55`（超範圍）→ 意思是**「只屈了 27%，同時往左甩到極限」**，並不是「閉合這根手指」。對照 `close` 和 `one` 裡的正確寫法應為 `(75, 75)`：

```yaml
# 修正后 —— 目标手指全闭 (75, 75)，其余保持张开 (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

拆解驗證：目標手指 `base = 75`（全閉）、`side = 0`（不左右偏）。

**影響**：使用這四個姿勢的 `finger_roll` 序列，現在才是真正的「逐指捲曲」。

### 5.2 `greeting` / `paper` 的拇指

兩者原本的拇指是 `(75, 75)`（完全閉合）。`paper`（布，攤開手掌）拇指閉合明顯不對。

`greeting` 先改為 `(-75, -3)`（沿用 `hifive` 的拇指外展值），但實機測試發現該步拇指要跑 **150°**，在 1.0s 內跑不完（詳見 6.3）。最終：

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # 拇指改为 (-35, -35)，与 open 一致
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # 保持拇指外展（平摊手掌）
```

兩個 pose 的語意由此分開：`greeting` 是打招呼，拇指自然張開即可；`paper` 是平攤手掌，拇指外展。

---

## 六、序列播放器：時序與診斷修復

### 6.1 修復「未到位」誤報（索引順序 bug）

實機跑 `demo` 時出現三條誤報：

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**根因**：`_log_pose_completion` 把兩組**順序不同**的陣列按下標直接相減。

- `monitor_servos()` 按**舵機 ID 順序**寫快取：`latest_actual_positions[servo_id - 1] = ...`（下標 0 = ID1 = Pointer）
- 但傳入的 `target_positions` 是 pose 陣列，按**控件順序** Ring / Middle / Pointer / Thumb（下標 0 = Ring = ID5）

等於拿 Ring 的目標去減 Pointer 的實測。

**證據**（用實測日誌裡的 `greeting` 資料複算）：

```
目标(控件序)    : [-18, -57, -32, -32, -70, -7, -75, -3]
实测(舵机序)    : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
按同序直接比    -> 最大误差 52°      <-- 修复前的算法
目标重排为舵机序: [-70, -7, -32, -32, -18, -57, -75, -3]
按舵机序比      -> 最大误差 2.21°    <-- 其实完美到位
```

**修復**：新增 `pose_to_servo_order()` / `servo_to_pose_order()` 兩個轉換函式，比對前對齊；列印時再轉回同一順序，使日誌裡 `target` 與 `current` 逐欄可比。

### 6.2 修復完成檢查的時機

原版在 pose 下發後**固定等 2000ms** 就做檢查：

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

但序列的延時只有 1.0s，於是檢查時下一步已經在執行，讀到的必然是下一步運動途中的位置：

```
25.388  Pose #40 'ok'      下发
26.782  Pose #41 'victory' 下发        <- 已经切走
27.742  Pose #40 'ok'      检查 -> 读的是走向 victory 途中的位置
```

**修復**：

1. `_apply_pose_from_config` 新增 `check_after` 參數。點 `✓ Apply` 單一 pose 時行為不變（2.0s + 等運動停止）；序列播放時傳入**該步自己的延時**，檢查落在步邊界上（延時 − 100ms），且不再用「等運動停止」邏輯。
2. 新增**取代守衛**：`_log_pose_start` 記錄 `current_pose_id`，檢查時若已被更新的命令取代，則跳過到位判定，只列印 `current=<superseded>`。

### 6.3 序列延時調整

從實機日誌反推出**真實有效速度**（speed 3 標稱 172°/s）：

| pose | 行程 | 0.9s 時的誤差 | 反推有效速度 |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s（71% 標稱） |
| `victory` | 110° | 1.0° | 121.1°/s（70%） |
| `greeting` | 132° | 7.0° | 138.9°/s（81%） |

> 帶載後實際速度約為標稱的 **七成**。這是選擇延時時的重要依據。

**`demo` 序列調整**：

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # 由 1.0s 延长
    - close:6,6,6,6,6,6,6,6|2.0s         # 新增：末尾回归握紧
```

- `greeting` 延時 1.0s → **1.5s**：該步最大行程 132°（Ring 第 2 軸），1.0s 內跑不完
- **末尾新增一步 `close`**：讓 `demo` 結束時手回到握緊狀態，循環播放時銜接乾淨
- `demo` 總時長 7.0s → **9.5s**

### 6.4 `wave` 序列：左右擺幅限制到 ±30°

原 `wave_r` / `wave_l` 隱含的 `side` 達到 **±36**（超出 ±35 限位被裁到 35）。

按 `side = base − pos1`、`base = (pos1 + pos2) / 2` 反解得 `pos1 = base − side`、`pos2 = base + side`，保持 `base = −39` 不變、把 `side` 收到 ±30：

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # 原 [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # 原 [-75, -3, -75, -3, -75, -3, -3, -75]
```

驗證：`wave_r` 的 side = `[-30, -30, -30, +30]`，`wave_l` 是它的逐指鏡像。

**副作用（預期內）**：單次揮動的行程也從 40°/72° 降到 **34°/60°**，揮手幅度整體收窄，時序餘量反而更寬。

---

## 七、Servo Feedback 新增原始位置行

在 `Position (°)` 正下方新增一行 **`Current (0-1023)`**，即時顯示舵機原始位置。

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== 新增
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**實作取捨**：不做額外的序列埠讀取，原始值從監控執行緒**已經讀到**的當前位置換算，避免每個輪詢週期序列埠往返翻倍。換算精度經全量驗證：**2048 個組合（raw 0–1023 × 奇/偶軸）往返零誤差**。

**用途**：可以直接對照廠商標定值核對 —— `open` 時看到 `260 / 760` 交替，`middle` 時是 `451 / 571`。

> 行名加了量程前綴以區別於已有的 `Current (mA)`（電流估算行）。

---

## 八、左右手支援

### 8.1 廠商的兩套韌體

廠商為左右手各提供一個 Arduino 演示程式，兩者參數完全不同：

| 項目 | 右手 `Amazing_RHand_Demo` | 左手 `Amazing_LHand_Demo` |
|---|---|---|
| 舵機 ID | **1–8** | **11–18** |
| 手指 → ID | 食指 `1,2` / 中指 `3,4` / 無名指 `5,6` / 拇指 `7,8` | **無名指 `11,12` / 中指 `13,14` / 食指 `15,16` / 拇指 `17,18`** |
| 中位 `MiddlePos` | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

除錯教學原文：**「單個靈巧手共使用了 8 個舵機，右手 ID 需要設定為 1-8，左手 ID 需要設定為 11-18」**。

注意左手的編號順序是**反的**（無名指在前）—— 和鏡像的機械結構對應。

### 8.2 為什麼不能只改 ID

ID 只是第一層。左右手之間還有兩處物理差異，漏掉任何一處手勢都會走形。

#### 差異一：安裝偏移 35.16°

兩邊用的是**同一個手勢值 + 各自的 `MiddlePos`**：

```c
// 右手
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// 左手
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

同一個「張開」動作，左右手到達的 raw 值不同。換算到本程式的角度空間，兩者相差 **120 raw = 35.16°**。

#### 差異二：同指雙舵機互換

```c
// 右手 Victory                      // 左手 Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

每根手指的 `(a, b) → (-b, -a)`，換算成姿勢值就是**把每根手指的兩個數對調**。

漏掉這一步，**張開方向會整個反過來** —— 症狀是 V 字手勢的兩指併攏、該併攏的三指反而張開。

> 一個容易看錯的點：`Perfect` 裡食指/中指的值左右手**完全相同**（`(50,-50)`、`(0,0)`），只有拇指不同。所以這不是「食指中指互換」，而是每指獨立的 `(-b,-a)` —— 對稱的數對做這個變換等於不變。

### 8.3 實作

**兩隻手共用同一份 `hand_config.yaml`。** 檔案裡存的姿勢始終是**右手序**，左手只在讀取和寫回時做轉換，所以不需要維護兩套姿勢庫。

轉換集中在 `hand_logic.py`：

| 函式 | 作用 |
|---|---|
| `resolve_hand_config(app_config, hand)` | 把 `hands.<name>` 的覆寫項合併到頂層（右手）設定上 |
| `servo_pairs()` / `servo_ids()` | 該手各手指的 `(servo1_id, servo2_id)` / 全部舵機 ID（升序） |
| `hand_angle_offset()` / `hand_mirrors_pose()` | 讀取該手的兩個差異參數 |
| `adapt_pose_for_hand(positions, mirror)` | 對每根手指做 `(pos1, pos2)` 對調。**交換是自逆運算**，所以同一個函式既用於「應用時轉換」也用於「儲存時轉回」 |

**接入的路徑：**

- GUI：pose 應用（`✓ Apply` 與序列播放）、儲存 pose
- CLI：`--pose` / `--sequence`

**三個全域按鈕的原始值**是每隻手各自設定的，不走這套轉換（`raw_positions` 已寫在 `hands.left` 裡）。

### 8.4 使用方法

啟動 GUI 時先選：

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

選完才彈出介面；直接按 Enter 使用 `config.yaml` 裡的 `hand` 值。跳過提問：

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 左手首次標定核對

`hands.left.raw_positions` 裡只有 **middle 是廠商預設值**（`571, 451`），`open` / `close` 是從廠商演示程式推導的：

| 按鈕 | 左手 raw | 來源 |
|---|---|---|
| Middle position | `571, 451, …` | 廠商預設值 |
| Open All | `380, 642, …` | 推導：右手 Open All 的同一手勢，套到左手 `MiddlePos` |
| Close All | `880, 142, …` | 同上 |

**第一次接上左手時按這個順序核對：**

1. 按 **Middle position**，看 Servo Feedback 的 `Current (0-1023)` 行是否讀到 `571, 451, 571, 451, …`
2. 按 **Open All** / **Close All**，確認行程到位且不頂限位
3. 逐個試 `victory`（食指中指分開成 V）、`greeting`（三指併攏）、`ok`（拇指食指指尖相觸）

哪一項不對：

| 現象 | 改哪裡 |
|---|---|
| Middle position 讀數不對 | `hands.left.raw_positions.middle` |
| 張開方向反了 | `hands.left.mirror_pose` 改成 `false` |
| 行程不夠或過頭 | `hands.left.raw_positions.open` / `close` |

### 8.6 如果左手被編號成 1-8

有些人會把左手的舵機重新編號成 1–8。那樣只需改 `hands.left.servos`：

```yaml
hands:
  left:
    servos:
      # 按厂商左手顺序重编：无名指在前
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset` 和 `mirror_pose` **不用改** —— 它們是機械安裝的屬性，與 ID 編號無關。偶數 ID 取反的規則也仍然成立，因為每對手指都保持「奇數在前」。

---

## 九、序列埠連接埠自動偵測

### 9.1 問題

原版在 Windows 上把連接埠清單寫死成 `COM1`–`COM20`：

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

而實際板子可能落在任意連接埠號上（本機實測是 `COM243`）。結果是**下拉式選單裡根本沒有你的連接埠**，自動連接又去連設定裡不存在的預設值，報「系統找不到指定的檔案」。

### 9.2 方案

新增 `available_serial_ports()`，逐級回退：

1. `pyserial` 的 `list_ports.comports()`（裝了就用，資訊最完整）
2. Windows 且無 pyserial 時，讀登錄檔 `HARDWARE\DEVICEMAP\SERIALCOMM`（**純標準庫**，不引入相依性）
3. Linux/macOS 用 glob 掃 `/dev/ttyACM*`、`/dev/ttyUSB*`、`/dev/ttyAMA*`、`/dev/cu.usb*`
4. 都失敗才退回原來的候選清單

連接埠按**自然順序**排序，`COM2` 排在 `COM10` 前面。

### 9.3 配套調整

- 下拉式選單從 `readonly` 改為**可編輯** —— 偵測不到時可以直接手動輸入連接埠號
- 設定裡的預設連接埠不存在時，**自動回退到偵測到的第一個真實連接埠**，不再拿不存在的預設值去連
- **顯式傳入 `--port` 時不會被自動回退覆蓋**（用 `port_was_explicit` 標記區分）

---

## 十、設定項速查

### `data/config.yaml`

頂層（`servos` / `auto_extremes` / `raw_positions`）描述**右手**，也是預設值；`hands.<名稱>` 按 key 覆寫它們。

```yaml
hand: right           # 当前使用的手：right | left（GUI 启动时会问，--hand 可跳过）

limits:
  servo_min: -75      # 舵机角度绝对下限
  servo_max: 75       # 舵机角度绝对上限
  base_min: -75       # 开合滑块范围（-75 = 全开）
  base_max: 75        #                （ 75 = 全握）
  side_min: -35       # 左右滑块范围
  side_max: 35

auto_extremes:        # 左右极限处的舵机位置 —— 右手
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # 全局按钮的原始值目标 —— 右手（下标 0 → 舵机 ID 1）
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # 左手覆盖项，只需写与右手不同的部分
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # 下标 0 → 舵机 ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # 安装偏移（见 8.2）
    mirror_pose: true      # 同指双舵机互换（见 8.2）
```

`auto_extremes` 左右手**共用** —— 左右滑桿在姿勢空間裡的行為一致，鏡像手只是物理上朝相反方向張開。

### `data/hand_config.yaml`

pose 的 8 個值按 **Ring, Middle, Pointer, Thumb** 順序排列（對應舵機對 `(5,6) (3,4) (1,2) (7,8)`），**不是**舵機 ID 順序。

**這個檔案左右手共用，儲存的永遠是右手序。** 左手在應用時做同指互換，儲存時再換回來。

> ⚠️ `amazing_hand_cmd.py` 的 docstring 寫作 "index 0→servo1 … 7→servo8"，**該註解是錯的**，請勿照它修改。

---

## 十一、實機驗證資料

### 到位精度（修復後）

| pose | 目標 | 實測 | 最大誤差 |
|---|---|---|---|
| `open` | 全 −35 | −36.6 ~ −33.4 | ≤1.6° |
| `close` | 全 75 | 74.7 ~ 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### 換算校驗

```
raw -> degrees -> raw 往返 2048 个组合，零误差
open    原始值 [260, 760] -> 反算 [260, 760]
middle  原始值 [451, 571] -> 反算 [451, 571]
close   原始值 [760, 260] -> 反算 [760, 260]
```

### 已知殘留問題

- **`demo` 裡 `ok` 和 `victory` 兩步的時序餘量接近零**（按實測速度算 +0.01s）。目前靠「誤差 < 5° 容差」通過。電池電壓下降、溫度變化或手指變緊都可能把它們推過閾值。建議把這兩個的延時從 1.0s 提到 1.2s。
- **`scissors` 與 `two` 逐位元組相同**、**`stone` 與 `close` 逐位元組相同**。語意上說得通（剪刀手 = 比二，石頭 = 拳），屬字面重複，未清理。
- **滑桿與原始值之間仍有約 0.3° 的表示誤差**（見 2.4）。
- **`config.yaml` 與 `hand_logic.py` 的 `default_config` 已不同步**。後者仍是原版值（`servo_min: -40` 等），只在 `config.yaml` 缺失時用作遞補。測試 `test_hand_logic.py::TestAngleLimits::test_defaults` 斷言的正是這套舊預設值。

---

## 十二、檔案變更清單

| 檔案 | 變更 |
|---|---|
| `hand_logic.py` | 新增 SCS0009 換算常數；`raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`；`raw_position` 顯示格式；`raw_positions` 預設值；**左右手支援**（`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`）；**`available_serial_ports()`**；設定檔讀寫改用 **UTF-8**（原本走 Windows GBK 預設值，遇非 ASCII 註解會崩潰） |
| `amazing_hand_gui.py` | 新增 `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`；重寫 `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion`；新增 **Middle position** 按鈕；Servo Feedback 新增原始位置行；`self.app_config` 提升為實例屬性；移除無人讀取的 `latest_goal_positions` 並統一 `feedback_data['goal']` 的寫入順序；**啟動選擇左右手 + `--hand`**；**8 處硬編碼 `range(1,9)` 改為依手部實際 ID**；視窗標題顯示當前手；角度偏移與鏡像轉換接入所有 pose 路徑；**連接埠下拉式選單改用真實偵測結果並允許手動輸入** |
| `amazing_hand_cmd.py` | 新增 `--hand`；`connect` / `apply_pose` / `wait_for_motion` / 結束關力矩改用實際舵機 ID；pose 與序列應用接入角度偏移與鏡像轉換；設定檔讀取改用 UTF-8 |
| `data/config.yaml` | 重新標定 `limits` / `auto_extremes`；新增 `raw_positions`；新增 `hand` 與 `hands.left` 覆寫區塊 |
| `data/hand_config.yaml` | 19 個 pose 重新標定；四個 `*_close` 修正；`greeting` / `paper` 拇指修正；`wave_r` / `wave_l` 擺幅收到 ±30；`demo` 延長 `greeting` 延時並新增末尾 `close` |
| `pyproject.toml` | 修正 `build-backend`（`setuptools.backends.legacy:build` → `setuptools.build_meta`） |

### 術語對照

| 介面用語 | 含義 |
|---|---|
| **Auto 模式** | 用「開合 base + 左右 side」兩個滑桿間接控制一根手指的兩個舵機 |
| **Raw 模式** | 直接控制一根手指的兩個舵機角度 |
| **base** | 開合程度，`(pos1 + pos2) / 2` |
| **side** | 左右偏移，`base − pos1` |
| **原始值 / raw** | 舵機內部位置單位，0–1023 對應 300° 行程，中位 511 |
| **MiddlePos** | 廠商韌體裡的每舵機中位標定值，左右手不同（見 8.1） |
| **angle_offset** | 左右手的安裝偏移，35.16°（見 8.2） |
| **mirror_pose** | 左手特有的同指雙舵機互換（見 8.2） |
