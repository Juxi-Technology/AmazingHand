#pragma once

#include <stdbool.h>
#include <stdint.h>

/* 协议组件 — 串口帧解析 + 命令分发。
 * 解析状态机、校验、响应发送均为组件私有; 对外暴露逐字节喂入接口。
 */

#define MAX_PAYLOAD 8

/* 帧超时 (ms): main 的 uart_rx_task 用 esp_timer 判断 */
#define FRAME_TIMEOUT_MS 200

typedef struct {
    uint8_t cmd_id;
    uint8_t payload[MAX_PAYLOAD];
    uint8_t payload_len;
} cmd_msg_t;

/* 逐字节喂入解析器。返回 true = 收到一条可执行命令并填充 *out。
 * 内部处理: checksum 校验失败复位 / STOP(置 abort+响应) / 忙碌(BUSY 响应)。 */
bool protocol_parse_byte(uint8_t byte, cmd_msg_t *out);

/* 帧超时(FRAME_TIMEOUT_MS 内无新字节)时由调用方调用, 复位解析状态 */
void protocol_reset_parser(void);

/* 执行命令 (gesture_task 中调用)。逻辑与原 dispatch_command 完全一致。 */
void dispatch_command(uint8_t cmd_id, const uint8_t *payload, uint8_t len);
