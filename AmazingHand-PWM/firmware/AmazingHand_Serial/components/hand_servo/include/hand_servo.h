#pragma once

/* 舵机驱动组件 (LEDC PWM)。
 * 只包含硬件驱动与校准数据, 不含任何手势/协议语义。
 * middle_pos/min_pw/mid_pw/max_pw 均为组件私有, 通过 move_* 间接使用。
 */

/* 初始化 8 路 LEDC 通道 (app_main 调用) */
void servo_init(void);

/* 设置单个舵机角度。servo_id: 1-8, angle: 0-180 (自动 clamp) */
void set_servo_angle(int servo_id, int angle);

/* 手指差动运动。pos_1/pos_2 为相对 middle_pos 的偏移, speed 保留接口兼容。 */
void move_index(int pos_1, int pos_2, int speed);
void move_middle(int pos_1, int pos_2, int speed);
void move_ring(int pos_1, int pos_2, int speed);
void move_thumb(int pos_1, int pos_2, int speed);
