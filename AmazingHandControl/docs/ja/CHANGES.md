[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | 日本語 | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · 変更履歴と根拠

元のプロジェクトと比べて何を変更したか、なぜ変更したか、そしてその結果が実際にどうなったかをまとめます。

元のプロジェクト：`Betatester777/AmazingHandControl`（AmazingHand 用の Python GUI + CLI）
ハードウェア：JuxiTechnology AmazingHand（Feetech SCS0009 サーボ ×8、ポテンショメータフィードバック）—— **左右両手に対応**、起動時に選択

---

## 目次

1. [角度体系の再キャリブレーション](#1-角度体系の再キャリブレーション)
2. [グローバルボタン：正確な raw 位置の駆動](#2-グローバルボタン正確な-raw-位置の駆動)
3. [新しい Middle position ボタン](#3-新しい-middle-position-ボタン)
4. [GUI と CLI の不一致（核心バグ）](#4-gui-と-cli-の不一致核心バグ)
5. [Pose データの修正](#5-pose-データの修正)
6. [シーケンスプレイヤー：タイミングと診断](#6-シーケンスプレイヤータイミングと診断)
7. [Servo Feedback に raw 位置の行を追加](#7-servo-feedback-に-raw-位置の行を追加)
8. [**左右両手のサポート**](#8-左右両手のサポート)
9. [シリアルポートの自動検出](#9-シリアルポートの自動検出)
10. [設定リファレンス](#10-設定リファレンス)
11. [測定結果](#11-測定結果)
12. [ファイル別サマリー](#12-ファイル別サマリー)

---

## 1. 角度体系の再キャリブレーション

### 1.1 角度限界：`0..110` → `-75..75`

元のバージョンは `0° = 開く、110° = 閉じる` としてキャリブレーションされていました。このハンドの実際の可動範囲は `-75..75` に収まるため、すべてを再キャリブレーションしました。

**`data/config.yaml`**

| キー | 変更前 | 変更後 |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**19 個のポーズをすべて再スケーリングしました**。たとえば `open` は `[0]*8` から `[-35]*8` へ、`close` は `[110]*8` から `[75]*8` へ変更しています。

### 1.2 左右の開き幅：`±40°` → `±35°`

サイドスライダーは `u = |side_offset| / |side_min|` で正規化するため、限界値だけを変更しても指が実際に開く幅は**変わりません**——スライダーが再スケーリングされるだけです。物理的な開き幅を変えるには `auto_extremes` も併せて変更する必要があります。両方を変更すると：

| | 変更前（±40） | 変更後（±35） |
|---|---|---|
| スライダー範囲 | −40 … +40 | −35 … +35 |
| 全開、左右に振り切ったとき | `(32, -40)`、開き幅 **72°** | `(32, -35)`、開き幅 **67°** |

### 1.3 ベンダーの基準に合わせる

ベンダーの Arduino デモ（`Amazing_RHand_Demo.ino`）は次のように変換します：

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

また rustypot 1.4.2（`src/servo/feetech/scs0009.rs`）：

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**結論：どちらも同じ度数スケールを使用しています**（0.29297°/ステップ、フルスケール 300°、raw 0–1023）——比率の誤差はありません。唯一の体系的な違いはゼロ点です：

- rustypot は常に raw **511** を中心とする
- ベンダーのファームウェアはサーボごとのキャリブレーション値 `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}` を使用する

両者は **±60 raw = ±17.6°** 異なります。これが後述の「Middle position」ボタンで対処している点です。

---

## 2. グローバルボタン：正確な raw 位置の駆動

### 2.1 問題

元の `open_all()` / `close_all()` は角度がハードコードされていました：

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # hard-coded 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # hard-coded 110
```

これらの値は**旧キャリブレーションスケール**（0 = 開く、110 = 閉じる）に基づいています。`-35 / 75` に再キャリブレーションした後では：

- `open_all` は 0° を設定 → raw **511** に変換され、ほぼ機械的な中央になる——指はまったく開かなかった
- `close_all` は 110° を設定 → `base_max = 75` でクランプされ、75 までしか到達しないのに、ラベルは依然として 110° と表示されていた

### 2.2 修正：raw 位置を直接指定する経路

角度の経路は `base/side` 補間モデルを通るため、任意の raw 値を正確に再現できません（セクション 4 参照）。そこでグローバルボタンには、raw サーボ位置を直接書き込む経路を用意しました。

**重要な実装上のポイントが 1 つあります：**これは rustypot の `sync_write_raw_goal_position` を*使用していません*。マクロ生成されたソースを読むと、raw API は `values.to_le_bytes()` をそのままワイヤに書き出す一方、変換 API は先に `to_be()` を適用します：

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

したがって `451` を渡すと `0xC301`（49921）が出力されてしまいます。そこでコードは `sync_write_goal_position`（ラジアン）を使用し、目標の raw 値に**正確に**一致するラジアンを逆算します。その際、切り捨て誤差を避けるため各 raw ステップの中点を取ります。

### 2.3 3 つのボタンの raw 目標値

`data/config.yaml` に `raw_positions` を追加しました（インデックス 0 → サーボ ID 1）：

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| ボタン | 動作 | サーボ ID 1–8 の raw |
|---|---|---|
| ✋ Open All | 完全に伸展 | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | 完全に閉じる | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | 左右を中央へ戻す（開閉は変更なし） | — |
| **Middle position** | **キャリブレーション済みの中間位置へ戻す** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` は**ハンドごとのキャリブレーション値**です。ベンダー自身のコメントも*「replace values by your calibration results」*（値はご自身のキャリブレーション結果に置き換えてください）としています——ハンドやサーボを交換したら再測定してください。

### 2.4 スライダー同期のトレードオフ

raw の目標値は `base/side` モデルを経由しないため、正確に対応するスライダー値が存在しません。ボタン実行後、スライダーは最も近い整数値に設定されます：

| 位置 | スライダー表示 |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

その代償：その後スライダーに触れると、ハンドは目標から最大で約 1 raw 単位（0.3°）ずれます。これは意図的なもので、キャリブレーション済みの位置に正確に到達することのほうが重要だからです。

---

## 3. 新しい Middle position ボタン

`✋ Open All` / `✊ Close All` / `⊙ Center All` の右側に配置されています。ハンドを**ベンダーがキャリブレーションした機械的な中間位置**（raw 451/571）に戻します。

**なぜ必要か：**`open_all` と `close_all` の中点は機械的な中間位置では*ありません*。ベンダーの中間位置は `MiddlePos` であり、raw 511 から ±60 raw（±17.6°）離れています。電源投入後は、明確に定義され再現可能なゼロ点が必要です。

---

## 4. GUI と CLI の不一致（核心バグ）

### 4.1 症状

**同じポーズでも、GUI の `✓ Apply` で適用した場合と CLI の `--pose` で適用した場合とで、ハンドの動きが異なります。**

### 4.2 根本原因

GUI は次の経路でポーズを適用していました：

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

しかし `compute_auto_positions` は `decompose_servo_positions` の**正確な逆関数ではありません**（その中心と極値は経験値です）。CLI の `apply_pose()` は値を直接送信します。

実測では、**19 個のポーズのうち 12 個が歪み**、最大 32° に達しました：

| ポーズ | 保存値 | GUI が実際に送信した値 | ずれ |
|---|---|---|---|
| `ring_close` | 薬指 `(75, -35)` | 薬指 `(43, -5)` | **32° / 30°** |
| `middle_close` | 中指 `(75, -35)` | 中指 `(43, -5)` | **32° / 30°** |
| `pointer_close` | 人差し指 `(75, -35)` | 人差し指 `(43, -5)` | **32° / 30°** |
| `thumb_close` | 親指 `(75, -35)` | 親指 `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | 親指 `(-75, -3)` | 親指 `(-75, 9)` | 12° |
| `greeting` | 薬指 `(-18, -57)` | 薬指 `(-10, -68)` | 8° / 11° |
| `victory` | 中指 `(-68, -9)` | 中指 `(-75, 1)` | 7° / 10° |
| `paper` | 人差し指 `(-52, -22)` | 人差し指 `(-59, -16)` | 7° / 6° |
| `ok` | 人差し指 `(36, 46)` | 人差し指 `(38, 43)` | 2° / 3° |

**パターン：**各指で `pos1 == pos2` となる対称なポーズ（`open` `close` `stone` `two` `scissors` `one` `three`）は正確に往復します。左右の開きを含む非対称なポーズはすべてずれます。

### 4.3 修正

`_send_exact_positions()` を追加し、角度を `SERVO_PAIRS` の順序でサーボへ直接送信するようにしました（CLI の `apply_pose` と等価です）。両方のポーズ適用経路がこれを使用するようになりました：

- Pose Management の `✓ Apply` ボタン
- `_apply_pose_from_config()`——シーケンスプレイヤーとポーズリスト

スライダーは表示のために `set_positions()` で引き続き更新されますが、**何が送信されるかを決めることはなくなりました**。

### 4.4 結果

修正後、**19 個のポーズすべてが `stored == GUI-sent == CLI-sent` を満たします**。

**副作用：**GUI 上の実際のジェスチャーが、とくに非対称なものが変わります。これは修正の意図された効果です。

---

## 5. Pose データの修正

### 5.1 4 つの `*_close` ポーズが誤って記述されていた

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` は `base = 20, side = -55`（範囲外）に分解されます——これは*「27% しか曲がっておらず、左に大きく振れている」*という意味であり、「この指を閉じる」ではありません。`close` と `one` に合わせると、正しい形は `(75, 75)` です：

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

分解による検証：対象の指は `base = 75`（完全に閉じる）、`side = 0`（左右どちらにも寄らない）。

**影響：**これら 4 つを使用する `finger_roll` シーケンスは、ここにきて初めて本当の「各指を順にロールさせる」動作になりました。

### 5.2 `greeting` / `paper` の親指

どちらも元は親指が `(75, 75)`（完全に閉じる）でした。`paper`（布、開いた平手）では、閉じた親指は明らかに誤りです。

`greeting` はまず `(-75, -3)` に変更されました（`hifive` の開いた親指を再利用）。しかしハードウェアでのテストにより、このステップでは親指が **150°** 移動する必要があり、1.0 s には収まらないことが判明しました（6.3 参照）。最終的な状態：

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

これで 2 つのジェスチャーが区別されます。`greeting` は手を振る動作で、親指は自然に開くだけです。`paper` は平手で、親指は開きます。

---

## 6. シーケンスプレイヤー：タイミングと診断

### 6.1 「目標に到達しなかった」という誤警告の修正

実機で `demo` を実行すると、3 件の誤警告が出ました：

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**根本原因：**`_log_pose_completion` が、**順序の異なる**2 つの配列を減算していました。

- `monitor_servos()` はキャッシュを**サーボ ID 順**で書き込みます：`latest_actual_positions[servo_id - 1] = ...`（インデックス 0 = ID1 = 人差し指）
- 渡された `target_positions` はポーズ配列で、**ウィジェット順**の 薬指 / 中指 / 人差し指 / 親指（インデックス 0 = 薬指 = ID5）です

つまり、薬指の目標値から人差し指の測定値を引いていました。

**根拠**（測定ログから再計算）：

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**修正：**`pose_to_servo_order()` / `servo_to_pose_order()` を追加し、比較前に適用しました。出力される `current` は逆変換されるため、ログ内で `target` と `current` が列ごとに揃います。

### 6.2 到達チェックの実行タイミングの修正

元のコードは送信後**固定の 2000 ms** でチェックしていました：

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

しかしシーケンスのステップは 1.0 s しか待たないため、チェックが実行される頃には次のステップがすでに送信されています——測定値は必然的に*次*の動作に属します：

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**修正：**

1. `_apply_pose_from_config` に `check_after` パラメータを追加しました。単一ポーズで `✓ Apply` をクリックした場合の動作は従来どおりです（2.0 s 待ってから動作停止を待つ）。シーケンス再生時は**そのステップ自身の遅延**を渡すため、チェックはステップの境界（遅延 − 100 ms）で行われ、動作停止を待たなくなります。
2. **上書きガード**を追加しました：`_log_pose_start` が `current_pose_id` を記録し、より新しいコマンドに切り替わっている場合は到達チェックをスキップし、ログに `current=<superseded>` と表示します。

### 6.3 シーケンス遅延の調整

ハードウェアログから**実効速度**を逆算しました（速度 3 は公称 172°/s）：

| ポーズ | 移動量 | 0.9 s 時点の誤差 | 推定実効速度 |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s（公称の 71%） |
| `victory` | 110° | 1.0° | 121.1°/s（70%） |
| `greeting` | 132° | 7.0° | 138.9°/s（81%） |

> 負荷がかかると、実際の速度は公称の約 **70%** にしかなりません。遅延を決めるときに重要なのはこの数値です。

**`demo` の変更：**

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # was 1.0s
    - close:6,6,6,6,6,6,6,6|2.0s         # new: settle back into a fist
```

- `greeting` 1.0 s → **1.5 s**：このステップは 132°（薬指の 2 番目のサーボ）移動するため、1.0 s では完了できません
- **最後に新しい `close` を追加**：これにより `demo` はハンドが閉じた状態で終わり、ループもきれいになります
- 総実行時間 7.0 s → **9.5 s**

### 6.4 `wave`：左右の振れ幅を ±30° に制限

元の `wave_r` / `wave_l` は `side` が **±36** を意味していました（±35 の限界を超えるため、35 にクランプされていました）。

`side = base − pos1`、`base = (pos1 + pos2) / 2` を解くと `pos1 = base − side`、`pos2 = base + side` が得られます。`base = −39` を保ちつつ `side` を ±30 に減らすと：

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

検証済み：`wave_r` の side は `[-30, -30, -30, +30]` で、`wave_l` はその指ごとのミラーです。

**副作用（想定内）：**各スイングの移動量も 40°/72° から **34°/60°** に減少します。波は全体として狭くなり、タイミングの余裕はむしろ広がります。

---

## 7. Servo Feedback に raw 位置の行を追加

**`Current (0-1023)`** という行が `Position (°)` のすぐ下にあり、ライブの raw サーボ位置を表示します。

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== new
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**トレードオフ：**追加のシリアル読み取りはありません。raw 値は監視スレッドが**すでに**読み取った位置から導出されるため、ポーリングループのシリアル通信量は倍増しません。精度は網羅的に検証済みです：**2048 通りの組み合わせ（raw 0–1023 × 奇数/偶数サーボ）が誤差ゼロで往復変換できます**。

**用途：**ベンダーのキャリブレーションと直接比較できます——`open` は `260 / 760` の交互、`middle` は `451 / 571` を読み取るはずです。

> この行名は範囲の接頭辞を持ち、既存の `Current (mA)`（推定消費電流）と区別できるようにしています。

---

## 8. 左右両手のサポート

### 8.1 ベンダーは 2 つのファームウェアを提供

ベンダーはハンドごとに別々の Arduino デモを提供しており、パラメータがまったく異なります：

| | 右手 `Amazing_RHand_Demo` | 左手 `Amazing_LHand_Demo` |
|---|---|---|
| サーボ ID | **1–8** | **11–18** |
| 指 → ID | 人差し指 `1,2` / 中指 `3,4` / 薬指 `5,6` / 親指 `7,8` | **薬指 `11,12` / 中指 `13,14` / 人差し指 `15,16` / 親指 `17,18`** |
| 中間 `MiddlePos` | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

デバッグチュートリアルには明快にこう書かれています：*「1 本のハンドは 8 個のサーボを使う。右手の ID は 1-8、左手の ID は 11-18 に設定する必要がある。」*

左手の番号付けは**逆順**（薬指が先頭）である点に注意してください——これはミラーされた機械的レイアウトに対応しています。

### 8.2 ID を変えるだけでは不十分な理由

ID は最初の層にすぎません。両手の間にはさらに 2 つの物理的な違いが残っており、どちらか一方でも見落とすとジェスチャーが歪みます。

#### 違い 1：35.16° の取り付けオフセット

両手とも**同じジェスチャー値に自身の `MiddlePos` を加えたもの**を使用します：

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

同じ「open」ジェスチャーでも、両手では異なる raw 値になります。このプログラムの角度空間に換算すると、**120 raw = 35.16°** 異なります。

#### 違い 2：指の 2 つのサーボが入れ替わっている

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

指ごとに `(a, b) → (-b, -a)` です。ポーズ値では、**各指の 2 つの数値を入れ替える**ことを意味します。

これを見落とすと**開く方向が反転**します——症状としては、V サインが 2 本の指を閉じてしまい、逆に揃っているべき指が開いてしまいます。

> ありがちな誤読：`Perfect` では人差し指と中指の値が両手で**同一**（`(50,-50)`、`(0,0)`）で、異なるのは親指だけです。したがってルールは「人差し指と中指を入れ替える」ではなく、指ごとの `(-b,-a)` です——これは対称なペアでは恒等変換になります。

### 8.3 実装

**両手は 1 つの `hand_config.yaml` を共有します。**保存されるポーズは常に**右手の順序**で、左手は出力時と復元時に変換するため、2 つ目のポーズライブラリを維持する必要はありません。

変換は `hand_logic.py` にあります：

| 関数 | 目的 |
|---|---|
| `resolve_hand_config(app_config, hand)` | トップレベル（右手）の設定に `hands.<name>` を重ね合わせる |
| `servo_pairs()` / `servo_ids()` | そのハンドの指ごとの `(servo1_id, servo2_id)` / 全サーボ ID を昇順に |
| `hand_angle_offset()` / `hand_mirrors_pose()` | そのハンドの 2 つの差分パラメータを読み取る |
| `adapt_pose_for_hand(positions, mirror)` | 各指の `(pos1, pos2)` を入れ替える。**入れ替えはそれ自身が逆変換**なので、同じ関数が適用時の変換と保存時の逆変換の両方に使える |

**組み込み先：**

- GUI：ポーズの適用（`✓ Apply` ボタンとシーケンス再生）、およびポーズの保存
- CLI：`--pose` / `--sequence`

**3 つのグローバルボタンの raw 目標値**はハンドごとに設定され、この変換を経由しません（`raw_positions` は `hands.left` の下に書き出されます）。

### 8.4 使用方法

GUI は起動前に確認します：

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Enter を押すと `config.yaml` の `hand:` の値が使用されます。プロンプトをスキップするには：

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 左手の初回チェックリスト

`hands.left.raw_positions` のうち、ベンダーの既定値（`571, 451`）なのは **middle** だけです。`open` と `close` はベンダーのデモから導出しました：

| ボタン | 左手の raw | 出典 |
|---|---|---|
| Middle position | `571, 451, …` | ベンダー既定 |
| Open All | `380, 642, …` | 導出：右手の Open All と同じジェスチャーを左手の `MiddlePos` に適用 |
| Close All | `880, 142, …` | 同上 |

**左手を初めて接続するときは、次の順序で確認してください：**

1. **Middle position** を押し、`Current (0-1023)` の行が `571, 451, 571, 451, …` を読み取ることを確認します
2. **Open All** / **Close All** を押します——ストールせずに可動端まで到達するはずです
3. `victory`（人差し指と中指が V の字に開く）、`greeting`（3 本の指が揃う）、`ok`（親指と人差し指の先端が触れ合う）を試します

問題がある場合：

| 症状 | 変更箇所 |
|---|---|
| Middle position の読み取りが誤っている | `hands.left.raw_positions.middle` |
| 開く方向が反転している | `hands.left.mirror_pose` を `false` に設定 |
| 移動量が短すぎる、または長すぎる | `hands.left.raw_positions.open` / `close` |

### 8.6 左手のサーボが 1-8 で番号付けされている場合

左手のサーボを 1–8 に番号付けし直す人もいます。その場合は `hands.left.servos` だけを変更すれば済みます：

```yaml
hands:
  left:
    servos:
      # Renumbered following the vendor's left-hand order: ring first
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset` と `mirror_pose` は**変更しません**——これらは機械的な構造を表すもので、ID の番号付けとは関係ありません。偶数サーボの反転も引き続き適用されます。各指のペアが「奇数 ID が先」を保つためです。

---

## 9. シリアルポートの自動検出

### 9.1 問題

元のコードは Windows のポート一覧を `COM1`–`COM20` にハードコードしていました：

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

しかしアダプタは任意のポート番号に割り当てられることがあります（このマシンでは `COM243` を計測）。その結果、**あなたのポートがドロップダウンに存在しなくなり**、自動接続は存在しない設定既定値にフォールバックし、「the system cannot find the file specified」で失敗します。

### 9.2 修正

`available_serial_ports()` を追加し、段階的にフォールバックします：

1. pyserial の `list_ports.comports()`（インストールされていれば使用——最も情報が豊富）
2. pyserial のない Windows：レジストリキー `HARDWARE\DEVICEMAP\SERIALCOMM` を読み取る（**標準ライブラリのみ**、新しい依存関係なし）
3. Linux/macOS：`/dev/ttyACM*`、`/dev/ttyUSB*`、`/dev/ttyAMA*`、`/dev/cu.usb*` を glob
4. 上記がすべて失敗した場合にのみ、元の候補リストにフォールバックする

ポートは**自然順**でソートされるため、`COM2` が `COM10` より先に来ます。

### 9.3 付随する変更

- ドロップダウンが `readonly` から**編集可能**に変更されました——検出が漏れたポートを手入力できます
- 設定された既定値が存在しない場合、GUI は存在しない既定値を試す代わりに、**実際に存在する最初のポートで起動します**
- **明示的な `--port` は決して上書きされません**（`port_was_explicit` で追跡）

---

## 10. 設定リファレンス

### `data/config.yaml`

トップレベルの `servos` / `auto_extremes` / `raw_positions` は**右手**を記述し、既定値として機能します。`hands.<name>` はキーごとにそれらを重ね合わせます。

```yaml
hand: right           # active hand: right | left (the GUI asks; --hand skips it)

limits:
  servo_min: -75      # absolute lower travel limit
  servo_max: 75       # absolute upper travel limit
  base_min: -75       # open/close slider range (-75 = fully open)
  base_max: 75        #                          ( 75 = fully closed)
  side_min: -35       # left/right slider range
  side_max: 35

auto_extremes:        # servo positions at the side slider's extremes — right hand
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # global buttons' raw targets — right hand (index 0 → servo ID 1)
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # overrides for the left hand; only list what differs
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # index 0 → servo ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # mounting offset (see 8.2)
    mirror_pose: true      # per-finger servo swap (see 8.2)
```

`auto_extremes` は両手で**共有**されます——サイドスライダーはポーズ空間では同じように動作し、ミラーされたハンドは物理的に逆方向に開くだけです。

### `data/hand_config.yaml`

ポーズの 8 つの値は**薬指、中指、人差し指、親指**の順（サーボペア `(5,6) (3,4) (1,2) (7,8)`）であり、サーボ ID 順では**ありません**。

**このファイルは両手で共有され、常に右手の順序で保存されます。**左手は適用時に各指のペアを入れ替え、保存時に元に戻します。

> ⚠️ `amazing_hand_cmd.py` の先頭の docstring は「index 0→servo1 … 7→servo8」と主張しています。このコメントは**誤り**で、実際のコードは上記の順序で動作します。

---

## 11. 測定結果

### 到達精度（修正後）

| ポーズ | 目標 | 実測 | 最大誤差 |
|---|---|---|---|
| `open` | すべて −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | すべて 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### 変換チェック

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### 既知の残存問題

- **`demo` 内の `ok` と `victory` にはタイミングの余裕がほとんどありません**（実測速度で +0.01 s）。現在通っているのは、< 5° の許容範囲が拾っているからにすぎません。バッテリー電圧の低下、温度変化、あるいはわずかに硬いハンドでも、これを超えてしまう可能性があります。両方の遅延を 1.0 s から 1.2 s に引き上げるのが明らかな次の一手です。
- **`scissors` は `two` とバイト単位で同一**で、**`stone` は `close` とバイト単位で同一**です。意味上は問題ありません（scissors = 2 本指、stone = 握り拳）が、文字どおり重複しており、整理されていません。
- **スライダーには raw 目標値に対して約 0.3° の表現誤差が残っています**（2.4 参照）。
- **`config.yaml` と `hand_logic.py` の `default_config` は同期していません。**後者は依然として元のスケール（`servo_min: -40` など）を持っており、`config.yaml` が欠落している場合にのみ使用されます。テスト `test_hand_logic.py::TestAngleLimits::test_defaults` はまさにその古い既定値をアサートしています。

---

## 12. ファイル別サマリー

| ファイル | 変更内容 |
|---|---|
| `hand_logic.py` | 新しい SCS0009 変換定数；`raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`；`raw_position` 表示フォーマット；`raw_positions` の既定値；**ハンド対応**（`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`）；**`available_serial_ports()`**；設定ファイル I/O を **UTF-8** に変更（Windows の既定 GBK を使用しており、非 ASCII のコメントでクラッシュしていた） |
| `amazing_hand_gui.py` | 新しい `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`；`open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion` を書き直し；新しい **Middle position** ボタン；Servo Feedback に raw 位置の行を追加；`self.app_config` をインスタンス属性に昇格；未使用の `latest_goal_positions` を削除し、`feedback_data['goal']` の書き込み順序を統一；**起動時のハンド選択 + `--hand`**；**8 か所のハードコードされた `range(1,9)` をハンドの実際の ID に置き換え**；ウィンドウタイトルにアクティブなハンドを表示；角度オフセットとミラー変換をすべてのポーズ経路に組み込み；**ポートドロップダウンが検出したポートを一覧表示し、手入力も受け付けるように** |
| `amazing_hand_cmd.py` | 新しい `--hand`；`connect` / `apply_pose` / `wait_for_motion` / 終了時のトルクオフがハンドの実際の ID を使用するように；ポーズとシーケンスの経路で角度オフセットとミラー変換を適用；設定の読み取りを UTF-8 に変更 |
| `data/config.yaml` | `limits` / `auto_extremes` を再キャリブレーション；`raw_positions` を追加；`hand` と `hands.left` のオーバーライドブロックを追加 |
| `data/hand_config.yaml` | 19 個のポーズをすべて再スケーリング；4 つの `*_close` ポーズを修正；`greeting` / `paper` の親指を修正；`wave_r` / `wave_l` の振れ幅を ±30 に狭めた；`demo` は `greeting` の遅延を延ばし、新しい閉じるステップを追加 |
| `pyproject.toml` | `build-backend` を修正（`setuptools.backends.legacy:build` → `setuptools.build_meta`） |

### 用語集

| 用語 | 意味 |
|---|---|
| **Auto モード** | 「base」（開閉）と「side」（左右）の 2 つのスライダーで、1 本の指の 2 つのサーボを間接的に駆動する |
| **Raw モード** | 指の 2 つのサーボ角度を直接制御する |
| **base** | 開閉量、`(pos1 + pos2) / 2` |
| **side** | 左右オフセット、`base − pos1` |
| **raw** | サーボ内部の位置単位：300° で 0–1023、中心 511 |
| **MiddlePos** | ベンダーファームウェアのサーボごとの中間キャリブレーション；両手で異なる（8.1 参照） |
| **angle_offset** | 両手間の 35.16° の取り付けオフセット（8.2 参照） |
| **mirror_pose** | 左手の指ごとのサーボペア入れ替え（8.2 参照） |
