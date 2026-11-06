/******************************************************************************
 * hand_servo — 舵机驱动组件 (LEDC PWM)
 *
 * 从原单文件 amazing_hand_serial.c 第 1/5 部分拆分:
 *   - 硬件配置 (servo_gpio / LEDC / 校准数组)
 *   - set_servo_angle / move_* / servo_init
 *
 * middle_pos 等校准数据保持组件私有, 手势通过 move_* 间接使用。
 ******************************************************************************/

#include <string.h>
#include <stdio.h>
#include "driver/ledc.h"

#include "hand_servo.h"

// ============================================================================
// 第 1 部分: 硬件配置
// ============================================================================

// --- 舵机引脚 (ESP32-S3) ---
// 食指 1,2→4,5  中指 3,4→6,7  无名指 5,6→15,16  拇指 7,8→17,18
static const int servo_gpio[8] = {4, 5, 6, 7, 15, 16, 17, 18};

// --- LEDC 配置 ---
#define LEDC_MODE       LEDC_LOW_SPEED_MODE
#define LEDC_TIMER      LEDC_TIMER_0
#define LEDC_FREQ       333     // 333Hz (PTK 7452 MG-D 数字舵机)
#define LEDC_RESOLUTION LEDC_TIMER_12_BIT  // 12-bit (0-4095)

static const ledc_channel_t ledc_ch[8] = {
    LEDC_CHANNEL_0, LEDC_CHANNEL_1, LEDC_CHANNEL_2, LEDC_CHANNEL_3,
    LEDC_CHANNEL_4, LEDC_CHANNEL_5, LEDC_CHANNEL_6, LEDC_CHANNEL_7
};

// --- 中位校准 ---
static int middle_pos[8] = {90, 90, 90, 90, 90, 90, 90, 90};

// --- 脉宽校准 (500-2500μs 对应 0-180°, 333Hz 数字舵机) ---
static const int min_pw[8] = {500, 500, 500, 500, 500, 500, 500, 500};
static const int mid_pw[8] = {1520, 1520, 1520, 1520, 1520, 1520, 1520, 1520};
static const int max_pw[8] = {2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500};


// ============================================================================
// 基础函数
// ============================================================================

// --- 约束宏 ---
#define CONSTRAIN(x, lo, hi)  (((x) < (lo)) ? (lo) : (((x) > (hi)) ? (hi) : (x)))

// --- 线性映射函数 ---
static long map_long(long x, long in_min, long in_max, long out_min, long out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// --- 设置舵机角度 ---
// servo_id: 1-8
// angle: 0-180
void set_servo_angle(int servo_id, int angle) {
    int idx = servo_id - 1;
    int pulse_us;

    angle = CONSTRAIN(angle, 0, 180);

    if (angle <= 90) {
        pulse_us = (int)map_long(angle, 0, 90, min_pw[idx], mid_pw[idx]);
    } else {
        pulse_us = (int)map_long(angle, 90, 180, mid_pw[idx], max_pw[idx]);
    }

    // duty = (pulse_us * freq * 2^resolution) / 10^6
    //      = (pulse_us * 333 * 4096) / 1000000
    uint32_t duty = (uint32_t)(((uint64_t)pulse_us * LEDC_FREQ * (1ULL << 12)) / 1000000ULL);

    ledc_set_duty(LEDC_MODE, ledc_ch[idx], duty);
    ledc_update_duty(LEDC_MODE, ledc_ch[idx]);
}

// --- 手指差动运动函数 ---
// 差动结构: 两个舵机偏移差值 = 伸展/收缩, 同向分量 = 左右偏
void move_index(int pos_1, int pos_2, int speed) {
    (void)speed;
    set_servo_angle(1, middle_pos[0] - pos_1);
    set_servo_angle(2, middle_pos[1] - pos_2);
}
void move_middle(int pos_1, int pos_2, int speed) {
    (void)speed;
    set_servo_angle(3, middle_pos[2] - pos_1);
    set_servo_angle(4, middle_pos[3] - pos_2);
}
void move_ring(int pos_1, int pos_2, int speed) {
    (void)speed;
    set_servo_angle(5, middle_pos[4] - pos_1);
    set_servo_angle(6, middle_pos[5] - pos_2);
}
void move_thumb(int pos_1, int pos_2, int speed) {
    (void)speed;
    set_servo_angle(7, middle_pos[6] - pos_1);
    set_servo_angle(8, middle_pos[7] - pos_2);
}

// --- 初始化舵机 (LEDC 定时器 + 8 通道) ---
void servo_init(void) {
    ledc_timer_config_t ledc_timer = {
        .speed_mode      = LEDC_MODE,
        .duty_resolution = LEDC_RESOLUTION,
        .timer_num       = LEDC_TIMER,
        .freq_hz         = LEDC_FREQ,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ledc_timer_config(&ledc_timer);

    for (int i = 0; i < 8; i++) {
        ledc_channel_config_t ch_conf = {
            .gpio_num   = servo_gpio[i],
            .speed_mode = LEDC_MODE,
            .channel    = ledc_ch[i],
            .intr_type  = LEDC_INTR_DISABLE,
            .timer_sel  = LEDC_TIMER,
            .duty       = 0,
            .hpoint     = 0,
        };
        ledc_channel_config(&ch_conf);
    }
}
