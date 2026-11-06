/******************************************************************************
 * AmazingHand Serial Control — main (胶水层)
 *
 * 职责: FreeRTOS 双任务 + 命令队列 + app_main 初始化顺序。
 * 协议解析/手势/舵机驱动分别由 hand_protocol / hand_gestures / hand_servo 组件提供。
 ******************************************************************************/

#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_timer.h"

#include "hand_servo.h"
#include "hand_gestures.h"
#include "hand_protocol.h"

// --- 命令队列 ---
static QueueHandle_t g_cmd_queue = NULL;

// --- 串口接收任务 (从 stdin 读取, 带噪声过滤) ---
static void uart_rx_task(void *arg) {
    (void)arg;

    // 设置 stdin 为非阻塞
    int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);

    int64_t last_byte_time = 0;

    while (1) {
        uint8_t b;
        int64_t now = esp_timer_get_time();  // μs
        int len = read(STDIN_FILENO, &b, 1);

        if (len <= 0) {
            // 检查帧超时
            int64_t now_ms = now / 1000;
            int64_t last_ms = last_byte_time / 1000;
            if (now_ms - last_ms > FRAME_TIMEOUT_MS) {
                protocol_reset_parser();
            }
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }
        last_byte_time = now;

        cmd_msg_t msg;
        if (protocol_parse_byte(b, &msg)) {
            xQueueSend(g_cmd_queue, &msg, 0);
        }
    }
}

// --- 手势执行任务 ---
static void gesture_task(void *arg) {
    (void)arg;

    while (1) {
        cmd_msg_t msg;
        if (xQueueReceive(g_cmd_queue, &msg, portMAX_DELAY) == pdTRUE) {
            dispatch_command(msg.cmd_id, msg.payload, msg.payload_len);
        }
    }
}

void app_main(void) {
    // 1. 创建命令队列
    g_cmd_queue = xQueueCreate(4, sizeof(cmd_msg_t));

    // 2. 初始化舵机
    servo_init();

    // 3. 初始姿态: 归零
    zero_hand();

    // 4. 启动任务
    xTaskCreate(uart_rx_task, "uart_rx", 2560, NULL, 2, NULL);
    xTaskCreate(gesture_task, "gesture", 4096, NULL, 1, NULL);

    // 5. 启动消息
    printf("\nAmazingHand Serial Control Ready (ESP-IDF)\n");
    printf("Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]\n");
    fflush(stdout);
}
