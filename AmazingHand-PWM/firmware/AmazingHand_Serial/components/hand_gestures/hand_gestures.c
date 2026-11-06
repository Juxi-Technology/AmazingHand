/******************************************************************************
 * hand_gestures — 手势组件
 *
 * 从原单文件 amazing_hand_serial.c 第 3/5/6/7 部分拆分:
 *   - 手势参数宏 (用户可调 #define)
 *   - 运行控制 (side / abort / 速度)
 *   - 全部手势函数 + 非阻塞延时
 *   - 手势查找表 + find_gesture
 *
 * abort/side 由协议层通过 setter 写入, 手势函数直接读私有 static。
 * 手势函数通过 move_*(hand_servo) 驱动舵机, 不直接访问 middle_pos。
 ******************************************************************************/

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "hand_servo.h"
#include "hand_gestures.h"

// 命令 ID (与 hand_protocol 保持一致)
#define CMD_ROCK        0x01
#define CMD_SCISSORS    0x02
#define CMD_PAPER       0x03
#define CMD_THUMBS_UP   0x04
#define CMD_TAUNT1      0x05
#define CMD_TAUNT2      0x06
#define CMD_OPEN        0x07
#define CMD_CLOSE       0x08
#define CMD_OK          0x09
#define CMD_PINCH       0x0A
#define CMD_INDEX       0x0C

// ============================================================================
// 手势参数 (用户可调)
// ============================================================================
// 正值 = 弯曲握紧, 负值 = 伸展打开
// 每根手指 2 个偏移量, 相对 middle_pos (90°)

// --- 石头 Rock ---
#define ROCK_IDX_OFF1    70
#define ROCK_IDX_OFF2   -70
#define ROCK_MID_OFF1    70
#define ROCK_MID_OFF2   -70
#define ROCK_RNG_OFF1    70
#define ROCK_RNG_OFF2   -70
#define ROCK_THB_OFF1    70
#define ROCK_THB_OFF2   -70
// 注意: 左手/右手的拇指偏移当前保持一致。
// 实测左手机构在"右手"挡位下动作正确, "左手"挡位对拇指整体取反反而导致伸展/收缩互换。
#define ROCK_THB_L_OFF1    70
#define ROCK_THB_L_OFF2   -70

// --- 剪刀 Scissors ---
#define SCISSORS_IDX_OFF1   -70
#define SCISSORS_IDX_OFF2    70
#define SCISSORS_MID_OFF1   -70
#define SCISSORS_MID_OFF2    70
#define SCISSORS_RNG_OFF1    70
#define SCISSORS_RNG_OFF2   -70
#define SCISSORS_THB_OFF1    70
#define SCISSORS_THB_OFF2   -70
#define SCISSORS_THB_L_OFF1    70
#define SCISSORS_THB_L_OFF2   -70

// --- 布 Paper ---
#define PAPER_IDX_OFF1   -80
#define PAPER_IDX_OFF2    80
#define PAPER_MID_OFF1   -60
#define PAPER_MID_OFF2    60
#define PAPER_RNG_OFF1   -60
#define PAPER_RNG_OFF2    60
#define PAPER_THB_OFF1   -60
#define PAPER_THB_OFF2    60

// --- 真棒 ThumbsUp ---
// 时序: 先全手展开 -> 拇指伸开并略向舵机17偏 -> 其余手指收拢
// 从握拳状态切换时, 拇指会被收拢的食指挡住无法伸出, 故必须先展开
#define THUMBSUP_IDX_OFF1    70
#define THUMBSUP_IDX_OFF2   -70
#define THUMBSUP_MID_OFF1    70
#define THUMBSUP_MID_OFF2   -70
#define THUMBSUP_RNG_OFF1    70
#define THUMBSUP_RNG_OFF2   -70
#define THUMBSUP_THB_OPEN1  -70    // 拇指展开 (全伸展)
#define THUMBSUP_THB_OPEN2  -70
#define THUMBSUP_THB_OFF1    -55   // 右手(side==1): 负偏移落18 (实测直驱170°≈offset-80, 正确)
#define THUMBSUP_THB_OFF2    -80
#define THUMBSUP_THB_L_OFF1   55   // 左手(side==2): 正偏移落17 (实测直驱18°≈offset+72, 正确)
#define THUMBSUP_THB_L_OFF2   80
#define THUMBSUP_EXT_DELAY   400   // 每步停顿 (ms)

// --- 嘲讽1 Taunt1 (摇食指) ---
#define TAUNT1_CYCLES      3
#define TAUNT1_WAG_DELAY   300
#define TAUNT1_WAG_AMP     70

// --- 嘲讽2 Taunt2 (无名指伸展+晃动 替代小拇指) ---
// 食指/中指/拇指收缩, 无名指伸展并左右晃动
// 差动规律: 收缩=(+,-), 伸展=(-,+)
#define TAUNT2_IDX_OFF1    70
#define TAUNT2_IDX_OFF2   -70
#define TAUNT2_MID_OFF1    70
#define TAUNT2_MID_OFF2   -70
#define TAUNT2_THB_OFF1    70
#define TAUNT2_THB_OFF2   -70
#define TAUNT2_RNG_EXT1   -60
#define TAUNT2_RNG_EXT2    60
#define TAUNT2_RNG_WAG1_A -35   // 晃动 A: 伸展 + 向左偏 (同差动, 横向摆动)
#define TAUNT2_RNG_WAG2_A  85
#define TAUNT2_RNG_WAG1_B -85   // 晃动 B: 伸展 + 向右偏
#define TAUNT2_RNG_WAG2_B  35
#define TAUNT2_CYCLES      3
#define TAUNT2_WAG_DELAY   300

// --- 捏合 Pinch ---
// 直驱实测: 食指/中指/无名指 40°/140° => 偏移 (50,-50); 左右手一致
// 拇指: 左手直驱116° => 偏移 -26 (90-116); 右手直驱64° => 偏移 +26 (90-64)
#define PINCH_IDX_OFF1    50
#define PINCH_IDX_OFF2   -50
#define PINCH_MID_OFF1    50
#define PINCH_MID_OFF2   -50
#define PINCH_RNG_OFF1    50
#define PINCH_RNG_OFF2   -50
#define PINCH_THB_OFF1    26    // 右手(side==1): 直驱64° => 偏移 +26
#define PINCH_THB_OFF2    26
#define PINCH_THB_L_OFF1 -26    // 左手(side==2): 直驱116° => 偏移 -26
#define PINCH_THB_L_OFF2 -26

// --- 基本角度 ---
#define OPEN_ANGLE   60
#define CLOSE_ANGLE  60

// ============================================================================
// 运行控制 (组件私有)
// ============================================================================

static volatile bool g_abort_flag = false;
static int side = 1;  // 1=右手, 2=左手

// --- 速度 (PWM 舵机无实际作用, 保留接口兼容) ---
static int max_speed   = 1500;
static int close_speed = 750;

// ============================================================================
// 非阻塞延时
// ============================================================================
// 替代 vTaskDelay, 每 10ms 检查一次 abort 标志
static void delay_non_blocking(uint32_t ms) {
    TickType_t start = xTaskGetTickCount();
    while ((xTaskGetTickCount() - start) * portTICK_PERIOD_MS < ms) {
        if (g_abort_flag) return;
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// ============================================================================
// 手势函数
// ============================================================================

void zero_hand(void) {
    move_index(0, 0, max_speed);
    move_middle(0, 0, max_speed);
    move_ring(0, 0, max_speed);
    move_thumb(0, 0, max_speed);
}

// --- 手势前置: 全手展开 ---
// 所有需要手指收缩的手势, 执行前先展开全手, 避免从上一手势直接收缩被挡住
#define PRE_OPEN_DELAY_MS   400

static void open_hand(void);   // 前向声明 (定义在下方)

static void pre_open_hand(void) {
    open_hand();
    delay_non_blocking(PRE_OPEN_DELAY_MS);
}

// --- 6.1 石头 ---
static void gesture_rock(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    move_index(ROCK_IDX_OFF1, ROCK_IDX_OFF2, max_speed);
    move_middle(ROCK_MID_OFF1, ROCK_MID_OFF2, max_speed);
    move_ring(ROCK_RNG_OFF1, ROCK_RNG_OFF2, max_speed);
    if (side == 2)
        move_thumb(ROCK_THB_L_OFF1, ROCK_THB_L_OFF2, max_speed);
    else
        move_thumb(ROCK_THB_OFF1, ROCK_THB_OFF2, max_speed);
}

// --- 6.2 剪刀 ---
static void gesture_scissors(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    move_index(SCISSORS_IDX_OFF1, SCISSORS_IDX_OFF2, max_speed);
    move_middle(SCISSORS_MID_OFF1, SCISSORS_MID_OFF2, max_speed);
    move_ring(SCISSORS_RNG_OFF1, SCISSORS_RNG_OFF2, max_speed);
    if (side == 2)
        move_thumb(SCISSORS_THB_L_OFF1, SCISSORS_THB_L_OFF2, max_speed);
    else
        move_thumb(SCISSORS_THB_OFF1, SCISSORS_THB_OFF2, max_speed);
}

// --- 6.3 布 ---
static void gesture_paper(void) {
    move_index(PAPER_IDX_OFF1, PAPER_IDX_OFF2, max_speed);
    move_middle(PAPER_MID_OFF1, PAPER_MID_OFF2, max_speed);
    move_ring(PAPER_RNG_OFF1, PAPER_RNG_OFF2, max_speed);
    move_thumb(PAPER_THB_OFF1, PAPER_THB_OFF2, max_speed);
}

// --- 6.4 真棒 ---
// 步骤: 1) 全手展开 2) 拇指伸开并略向17偏 3) 其余手指收拢
static void gesture_thumbs_up(void) {
    // 1) 先全手展开, 腾出拇指伸展空间 (从握拳态切入时必需)
    move_index(-(OPEN_ANGLE + 20), (OPEN_ANGLE + 20), max_speed);  // -80,80 张开
    move_middle(-OPEN_ANGLE, OPEN_ANGLE, max_speed);                // -60,60 张开
    move_ring(-OPEN_ANGLE, OPEN_ANGLE, max_speed);                  // -60,60 张开
    move_thumb(THUMBSUP_THB_OPEN1, THUMBSUP_THB_OPEN2, max_speed); // -70,-70 拇指全伸展
    delay_non_blocking(THUMBSUP_EXT_DELAY);
    if (g_abort_flag) return;
    // 2) 拇指伸开并偏转: 左手落17, 右手落18 (视角对称)
    if (side == 2)
        move_thumb(THUMBSUP_THB_L_OFF1, THUMBSUP_THB_L_OFF2, max_speed);  // (55,80) 落17
    else
        move_thumb(THUMBSUP_THB_OFF1, THUMBSUP_THB_OFF2, max_speed);      // (-55,-80) 落18
    delay_non_blocking(THUMBSUP_EXT_DELAY);
    if (g_abort_flag) return;
    // 3) 其余手指收拢 (70,-70 = 握拳式收缩)
    move_middle(THUMBSUP_MID_OFF1, THUMBSUP_MID_OFF2, close_speed);
    move_ring(THUMBSUP_RNG_OFF1, THUMBSUP_RNG_OFF2, close_speed);
    move_index(THUMBSUP_IDX_OFF1, THUMBSUP_IDX_OFF2, close_speed);
}

// --- 6.5 嘲讽1: 摇食指 ---
static void gesture_taunt1(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    move_index(-80, 80, max_speed);
    move_middle(70, -70, max_speed);
    move_ring(70, -70, max_speed);
    move_thumb(70, -70, max_speed);
    delay_non_blocking(400);
    if (g_abort_flag) return;

    for (int i = 0; i < TAUNT1_CYCLES; i++) {
        if (g_abort_flag) return;
        move_index(-10, TAUNT1_WAG_AMP, max_speed);
        delay_non_blocking(TAUNT1_WAG_DELAY);
        if (g_abort_flag) return;
        move_index(-TAUNT1_WAG_AMP, 10, max_speed);
        delay_non_blocking(TAUNT1_WAG_DELAY);
    }
    move_index(-35, 35, max_speed);
    delay_non_blocking(400);
}

// --- 6.6 嘲讽2: 无名指伸展+晃动 (替代小拇指) ---
static void gesture_taunt2(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    move_index(TAUNT2_IDX_OFF1, TAUNT2_IDX_OFF2, max_speed);
    move_middle(TAUNT2_MID_OFF1, TAUNT2_MID_OFF2, max_speed);
    move_thumb(TAUNT2_THB_OFF1, TAUNT2_THB_OFF2, max_speed);
    move_ring(TAUNT2_RNG_EXT1, TAUNT2_RNG_EXT2, max_speed);
    delay_non_blocking(500);
    if (g_abort_flag) return;

    for (int i = 0; i < TAUNT2_CYCLES; i++) {
        if (g_abort_flag) return;
        move_ring(TAUNT2_RNG_WAG1_A, TAUNT2_RNG_WAG2_A, max_speed);
        delay_non_blocking(TAUNT2_WAG_DELAY);
        if (g_abort_flag) return;
        move_ring(TAUNT2_RNG_WAG1_B, TAUNT2_RNG_WAG2_B, max_speed);
        delay_non_blocking(TAUNT2_WAG_DELAY);
    }
    move_ring(-45, 45, max_speed);
    delay_non_blocking(400);
}

// --- 6.7 张开 ---
static void open_hand(void) {
    move_index(-(OPEN_ANGLE + 20), (OPEN_ANGLE + 20), max_speed);
    move_middle(-OPEN_ANGLE, OPEN_ANGLE, max_speed);
    move_ring(-OPEN_ANGLE, OPEN_ANGLE, max_speed);
    move_thumb(-OPEN_ANGLE, OPEN_ANGLE, max_speed);
}

// --- 6.8 闭合 ---
static void close_hand(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    move_thumb(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed + 200);
    delay_non_blocking(100);
    if (g_abort_flag) return;
    move_index(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed);
    move_middle(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed);
    move_ring(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed);
}

// --- 6.9 食指指向 ---
static void index_pointing(void) {
    move_index(-OPEN_ANGLE, OPEN_ANGLE, max_speed);
    move_middle(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed);
    move_ring(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed);
    move_thumb(CLOSE_ANGLE, -CLOSE_ANGLE, close_speed + 200);
    delay_non_blocking(1000);
    if (g_abort_flag) return;
    move_index(0, 0, max_speed);
    delay_non_blocking(1000);
    if (g_abort_flag) return;
    move_index(-OPEN_ANGLE, OPEN_ANGLE, max_speed);
}

// --- 6.10 摇食指 Nonono ---
static void nonono(void) {
    index_pointing();
    if (g_abort_flag) return;
    for (int i = 0; i < 3; i++) {
        if (g_abort_flag) return;
        delay_non_blocking(300);
        move_index(-10, 80, max_speed);
        delay_non_blocking(300);
        if (g_abort_flag) return;
        move_index(-80, 10, max_speed);
    }
    move_index(-35, 35, max_speed);
    delay_non_blocking(400);
}

// --- 6.11 OK 手势 ---
static void perfect(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    if (side == 1) {
        move_index(50, -50, max_speed);
        move_middle(0, 0, max_speed);
        move_ring(-20, 20, max_speed);
        move_thumb(65, 12, max_speed);
    } else {
        // 左手: 拇指方向与右手一致 (实测右手值在左手机构上正确), 其余手指不变
        move_index(50, -50, max_speed);
        move_middle(0, 0, max_speed);
        move_ring(-20, 20, max_speed);
        move_thumb(65, 12, max_speed);
    }
}

// --- 6.12 捏合 ---
static void pinched(void) {
    pre_open_hand();
    if (g_abort_flag) return;
    move_index(PINCH_IDX_OFF1, PINCH_IDX_OFF2, max_speed);
    move_middle(PINCH_MID_OFF1, PINCH_MID_OFF2, max_speed);
    move_ring(PINCH_RNG_OFF1, PINCH_RNG_OFF2, max_speed);
    if (side == 2)
        move_thumb(PINCH_THB_L_OFF1, PINCH_THB_L_OFF2, max_speed);  // 左手: -26 (直驱116°)
    else
        move_thumb(PINCH_THB_OFF1, PINCH_THB_OFF2, max_speed);      // 右手: +26 (直驱64°)
}

// --- 6.13 逐指缓慢展开 ---
static void open_hand_progressive(void) {
    uint8_t i, j, step = 10;
    uint16_t ms = 100;
    uint8_t n = 13;

    for (i = 0; i < n + 2; i++) {
        if (g_abort_flag) return;
        j = i * step;
        move_index(OPEN_ANGLE - j, j - OPEN_ANGLE, max_speed);
        delay_non_blocking(ms);
    }
    delay_non_blocking(100);
    if (g_abort_flag) return;

    for (i = 0; i < n; i++) {
        if (g_abort_flag) return;
        j = i * step;
        move_middle(OPEN_ANGLE - j, j - OPEN_ANGLE, max_speed);
        delay_non_blocking(ms);
    }
    delay_non_blocking(100);
    if (g_abort_flag) return;

    for (i = 0; i < n; i++) {
        if (g_abort_flag) return;
        j = i * step;
        move_ring(OPEN_ANGLE - j, j - OPEN_ANGLE, max_speed);
        delay_non_blocking(ms);
    }
    delay_non_blocking(100);
    if (g_abort_flag) return;

    for (i = 0; i < n; i++) {
        if (g_abort_flag) return;
        j = i * step;
        move_thumb(OPEN_ANGLE - j, j - OPEN_ANGLE, max_speed);
        delay_non_blocking(ms);
    }
}

// ============================================================================
// 手势查找表
// ============================================================================

typedef struct {
    uint8_t        cmd_id;
    gesture_func_t func;
} gesture_entry_t;

static const gesture_entry_t gesture_table[] = {
    {CMD_ROCK,       gesture_rock},
    {CMD_SCISSORS,   gesture_scissors},
    {CMD_PAPER,      gesture_paper},
    {CMD_THUMBS_UP,  gesture_thumbs_up},
    {CMD_TAUNT1,     gesture_taunt1},
    {CMD_TAUNT2,     gesture_taunt2},
    {CMD_OPEN,       open_hand},
    {CMD_CLOSE,      close_hand},
    {CMD_OK,         perfect},
    {CMD_PINCH,      pinched},
    {CMD_INDEX,      index_pointing},
};
#define GESTURE_TABLE_SIZE  (sizeof(gesture_table) / sizeof(gesture_table[0]))

gesture_func_t find_gesture(uint8_t cmd_id) {
    for (size_t i = 0; i < GESTURE_TABLE_SIZE; i++) {
        if (gesture_table[i].cmd_id == cmd_id) {
            return gesture_table[i].func;
        }
    }
    return NULL;
}

// ============================================================================
// 运行控制 setter (协议层调用)
// ============================================================================

void hand_gestures_set_abort(bool abort) {
    g_abort_flag = abort;
}

void hand_gestures_set_side(int s) {
    side = s;
}
