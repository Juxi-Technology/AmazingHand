/******************************************************************************
 * hand_protocol — 协议组件
 *
 * 从原单文件 amazing_hand_serial.c 第 2/7 部分 + uart_rx_task 状态机拆分:
 *   - 协议常量 (帧头/命令ID/状态码)
 *   - 帧解析状态机 (protocol_parse_byte / protocol_reset_parser)
 *   - 命令分发 (dispatch_command) + 响应发送
 *
 * 通过 hand_gestures 的 setter 写 abort/side, 通过 find_gesture 查手势。
 ******************************************************************************/

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "hand_gestures.h"
#include "hand_servo.h"
#include "hand_protocol.h"

// ============================================================================
// 协议常量
// ============================================================================

#define FRAME_HEADER        0xAA
#define RESP_HEADER         0xBB

// --- 命令 ID ---
#define CMD_NOP             0x00
#define CMD_DIRECT_DRIVE    0xF0
#define CMD_SET_SIDE        0xF1
#define CMD_REPEAT          0xFE
#define CMD_STOP            0xFF

// --- 响应状态码 ---
#define STATUS_OK            0x00
#define STATUS_INVALID_CMD   0x01
#define STATUS_INVALID_PARAM 0x02
#define STATUS_BUSY          0x03
#define STATUS_COMPLETED     0x10

// --- 帧解析状态 ---
typedef enum {
    WAIT_START,
    WAIT_CMD,
    WAIT_LEN,
    WAIT_PAYLOAD,
    WAIT_CHECKSUM
} parser_state_t;

// ============================================================================
// 全局状态 (组件私有)
// ============================================================================

static parser_state_t g_state = WAIT_START;
static uint8_t g_rx_cmd_id = 0;
static uint8_t g_rx_data_len = 0;
static uint8_t g_rx_data_idx = 0;
static uint8_t g_rx_payload[MAX_PAYLOAD];

static bool g_gesture_running = false;

static uint8_t g_last_cmd = 0x00;
static uint8_t g_last_payload[MAX_PAYLOAD];
static uint8_t g_last_payload_len = 0;

// ============================================================================
// 基础函数
// ============================================================================

// --- 校验和 ---
// CHECKSUM = CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]
static uint8_t calc_checksum(uint8_t cmd, const uint8_t *data, uint8_t len) {
    uint8_t cs = cmd ^ len;
    for (uint8_t i = 0; i < len; i++) {
        cs ^= data[i];
    }
    return cs;
}

// --- 发送响应帧 ---
static void send_response(uint8_t cmd_id, uint8_t status) {
    uint8_t buf[4];
    buf[0] = RESP_HEADER;
    buf[1] = cmd_id;
    buf[2] = status;
    buf[3] = cmd_id ^ status;
    fwrite(buf, 1, 4, stdout);
    fflush(stdout);
}

// ============================================================================
// 帧解析状态机
// ============================================================================

// --- 解析器复位 (帧超时或校验失败后回到 WAIT_START) ---
void protocol_reset_parser(void) {
    g_state = WAIT_START;
}

// --- 逐字节喂入解析器 ---
// 返回 true = 收到一条可执行命令并填充 *out
// 内部处理: checksum 校验失败→复位; STOP→置 abort+响应; 忙碌→BUSY 响应
bool protocol_parse_byte(uint8_t byte, cmd_msg_t *out) {
    switch (g_state) {

        case WAIT_START:
            if (byte == FRAME_HEADER) {
                g_state = WAIT_CMD;
            }
            break;

        case WAIT_CMD:
            g_rx_cmd_id = byte;
            g_state = WAIT_LEN;
            break;

        case WAIT_LEN:
            if (byte > MAX_PAYLOAD) {
                g_state = WAIT_START;
            } else {
                g_rx_data_len = byte;
                g_rx_data_idx = 0;
                g_state = (byte == 0) ? WAIT_CHECKSUM : WAIT_PAYLOAD;
            }
            break;

        case WAIT_PAYLOAD:
            g_rx_payload[g_rx_data_idx++] = byte;
            if (g_rx_data_idx >= g_rx_data_len) {
                g_state = WAIT_CHECKSUM;
            }
            break;

        case WAIT_CHECKSUM: {
            g_state = WAIT_START;

            uint8_t expected = calc_checksum(g_rx_cmd_id, g_rx_payload, g_rx_data_len);
            if (expected != byte) break;

            if (g_rx_cmd_id == CMD_STOP) {
                hand_gestures_set_abort(true);
                send_response(CMD_STOP, STATUS_OK);
                break;
            }

            if (g_gesture_running) {
                send_response(g_rx_cmd_id, STATUS_BUSY);
                break;
            }

            out->cmd_id = g_rx_cmd_id;
            out->payload_len = g_rx_data_len;
            memcpy(out->payload, g_rx_payload, g_rx_data_len);
            return true;
        }
    }
    return false;
}

// ============================================================================
// 命令分发
// ============================================================================

void dispatch_command(uint8_t cmd_id, const uint8_t *payload, uint8_t len) {

    switch (cmd_id) {

        case CMD_NOP:
            send_response(CMD_NOP, STATUS_OK);
            break;

        case CMD_DIRECT_DRIVE:
            if (len != 8) {
                send_response(CMD_DIRECT_DRIVE, STATUS_INVALID_PARAM);
                return;
            }
            send_response(CMD_DIRECT_DRIVE, STATUS_OK);
            for (int i = 0; i < 8; i++) {
                uint8_t angle = payload[i];
                if (angle > 180) angle = 180;
                set_servo_angle(i + 1, angle);
            }
            send_response(CMD_DIRECT_DRIVE, STATUS_COMPLETED);
            break;

        case CMD_SET_SIDE:
            if (len != 1 || (payload[0] != 1 && payload[0] != 2)) {
                send_response(CMD_SET_SIDE, STATUS_INVALID_PARAM);
                return;
            }
            send_response(CMD_SET_SIDE, STATUS_OK);
            hand_gestures_set_side(payload[0]);
            send_response(CMD_SET_SIDE, STATUS_COMPLETED);
            break;

        case CMD_REPEAT:
            if (g_last_cmd == 0x00) {
                send_response(CMD_REPEAT, STATUS_INVALID_CMD);
                return;
            }
            dispatch_command(g_last_cmd, g_last_payload, g_last_payload_len);
            return;

        default: {
            gesture_func_t gesture = find_gesture(cmd_id);
            if (gesture == NULL) {
                send_response(cmd_id, STATUS_INVALID_CMD);
                return;
            }

            send_response(cmd_id, STATUS_OK);
            g_last_cmd = cmd_id;
            g_last_payload_len = len;
            for (uint8_t i = 0; i < len; i++) {
                g_last_payload[i] = payload[i];
            }

            g_gesture_running = true;
            hand_gestures_set_abort(false);
            gesture();
            g_gesture_running = false;

            send_response(cmd_id, STATUS_COMPLETED);
            break;
        }
    }
}
