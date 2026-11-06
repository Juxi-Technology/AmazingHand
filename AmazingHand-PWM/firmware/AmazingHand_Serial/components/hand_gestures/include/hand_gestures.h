#pragma once

#include <stdbool.h>
#include <stdint.h>

/* 手势组件 — 手势参数宏 + 手势函数 + 运行控制。
 * abort/side 的写入方(协议层)通过 setter 调用, 读取方(手势函数)直接读组件私有 static。
 */

typedef void (*gesture_func_t)(void);

/* 按命令 ID 查手势表, 未命中返回 NULL (协议层调用) */
gesture_func_t find_gesture(uint8_t cmd_id);

/* 运行控制: STOP 命令中断 / 分发前置复位 (协议层调用) */
void hand_gestures_set_abort(bool abort);

/* 左右手: 1=右手 2=左手 (协议层 CMD_SET_SIDE 调用) */
void hand_gestures_set_side(int s);

/* 全部归零 (app_main 初始姿态) */
void zero_hand(void);
