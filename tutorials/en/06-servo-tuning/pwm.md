---
title: "PWM Servo Protocol, Commands and Calibration"
description: "AmazingHand PWM version: supported gestures, firmware calibration, serial protocol, command reference, gesture parameter fine-tuning and FAQ."
version: pwm
---

# PWM Servo Protocol, Commands and Calibration

This page covers the PWM firmware's serial protocol, commands, calibration and parameter fine-tuning. For wiring, see [PWM wiring](../01-hardware/pwm.md); for flashing, see [PWM quick start](../02-quick-start/pwm.md); for desktop/web control, see [PWM desktop host software](../04-desktop/pwm.md) / [PWM web control](../03-web-control/pwm.md).

> Run the following commands in the repository's `AmazingHand-PWM/` directory. Firmware source: [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Command and gesture overview

The first 11 rows are gesture commands; the rest are direct drive, side selection, repeat, stop and link test commands.

| Gesture/command | Command | Description |
|------|------|------|
| Rock | 0x01 | Rock-paper-scissors: all fingers clenched |
| Scissors | 0x02 | Rock-paper-scissors: index + middle fingers extended in a V shape |
| Paper | 0x03 | Rock-paper-scissors: all fingers extended |
| Thumbs Up | 0x04 | Thumb raised, the other fingers clenched |
| Taunt 1 | 0x05 | Wag the index finger ("no, no, no")|
| Taunt 2 | 0x06 | Ring finger extended and wiggled (in place of the little finger)|
| Open | 0x07 | All fingers extended |
| Fist | 0x08 | All fingers closed |
| OK | 0x09 | OK gesture |
| Pinch | 0x0A | Pinch gesture |
| Point | 0x0C | Index finger extended in a pointing motion |
| Direct drive | 0xF0 | Directly control the angles of the 8 servos |
| Set left/right hand | 0xF1 | Switch between left-hand and right-hand modes |
| Repeat | 0xFE | Repeat the previous gesture |
| Stop | 0xFF | Immediately abort the current gesture |
| NOP | 0x00 | Link test |

> Note: command 0x0B is disabled (the former "Thumbs Down" gesture duplicated Thumbs Up and has been removed).

---

## 2. Firmware calibration (optional, recommended for first use)

The servo centre positions and pulse widths must be calibrated for the actual mechanism; they can be edited directly in the firmware source:

- Edit `middle_pos[8]` and `min_pw/mid_pw/max_pw[8]` at the top of `components/hand_servo/hand_servo.c`.

After calibration, rebuild and re-flash.

---

## 3. Serial communication protocol

### 3.1 Physical layer

| Parameter | Value |
|------|-----|
| Interface | USB Serial (UART0) |
| Baud rate | **115200** |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |

### 3.2 Frame format

#### Host → ESP32 (command frame)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
 Header   Cmd ID   Data Len      Payload       Checksum
```

- **Frame header**: fixed `0xAA`, marks the start of a frame
- **CMD_ID**: command number (see [Command reference](#4-command-reference))
- **DATA_LEN**: number of bytes in the data payload (0-8; frames longer than 8 bytes are invalid)
- **DATA**: data payload; its length is determined by DATA_LEN
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (XOR checksum)

> If DATA_LEN = 0, then CHECKSUM = CMD_ID.

#### ESP32 → Host (response frame)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
 Header   Cmd ID   Status   Checksum
```

- **Frame header**: fixed `0xBB`
- **CMD_ID**: original command number
- **STATUS**: status code (see the table below)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Status codes

| STATUS | Meaning | Description |
|--------|------|------|
| 0x00 | OK | Command accepted; execution started |
| 0x01 | Invalid command | CMD_ID is not in the command table |
| 0x02 | Parameter error | Data length or content is incorrect |
| 0x03 | Busy | A gesture is executing; new commands are temporarily rejected |
| 0x10 | Complete | Gesture execution finished |

### 3.3 Communication timing

```
Host                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  Send "Rock" command
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: command accepted
 │                              │
 │                      (executing gesture)
 │                              │
 │←─── [BB 01 10 11] ─────────│  Complete: gesture finished
 │                              │
 │──── [AA 02 00 02] ────────→│  Send "Scissors" command
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Stopping gestures and frame timeout

- Sending `[AA FF 00 FF]` can interrupt the currently executing gesture at any time
- If the ESP32 does not receive a complete frame within 200ms, it automatically discards it (preventing a lost byte from causing permanent desynchronization)
- Frames with a mismatched checksum are silently discarded; the host should implement timeout-based retransmission

### 3.5 Left/right hand mode

Right-hand mode is the default. Send `[AA F1 01 02 F2]` to switch to the left hand, and `[AA F1 01 01 F1]` to switch back to the right hand. The hand side affects the thumb's direction of motion (in gestures that involve the thumb, such as Rock/Scissors/Thumbs Up/OK/Pinch).

---

## 4. Command reference

### 4.1 Gesture commands (0x01–0x0A, 0x0C)

These commands require no data payload (DATA_LEN=0); the ESP32 executes the corresponding gesture immediately upon receipt.

| Command | HEX frame | Response | Description |
|------|--------|------|------|
| Rock | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | All fingers clenched |
| Scissors | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Index + middle fingers extended |
| Paper | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | All fingers extended |
| Thumbs Up | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Thumb raised |
| Taunt 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Wag the index finger (about 2.5s) |
| Taunt 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Wiggle the ring finger (about 2.5s) |
| Open | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | All fingers extended |
| Fist | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | All fingers closed |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | OK gesture |
| Pinch | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Pinch gesture |
| Point | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | Index finger extended in a pointing motion |

### 4.2 Direct drive command (0xF0)

Directly control the angles of the 8 servos; the 8 data bytes correspond to servos 1-8 respectively, each byte ranging from 0 to 180.

**Example: center all servos (90°)**

```
Send: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 × 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── Frame header
```

Checksum = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> The eight identical 0x5A bytes XOR in pairs to 0x00; the final result is `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Example: index finger extended (servo 1 = 170°, servo 2 = 10°), all others centered (90°)**

```
Send: AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 4.3 Set left/right hand (0xF1)

One data byte: `0x01` = right hand, `0x02` = left hand.

```
Set right hand: AA F1 01 01 F1
Set left hand: AA F1 01 02 F2
```

### 4.4 Control commands

| Command | HEX frame | Description |
|------|--------|------|
| NOP | `AA 00 00 00` | Link test; returns `BB 00 00 00` immediately |
| Repeat | `AA FE 00 FE` | Repeat the previous gesture |
| Stop | `AA FF 00 FF` | Immediately abort the current gesture |

### 4.5 Response quick reference

When an invalid command is received (using the nonexistent command 0xFC as an example):

```
Send: AA FC 00 FC
Response: BB FC 01 FD    (STATUS=0x01 invalid command)
```

> Checksum verification: `FC ^ 00 = FC`; for the response, `FC ^ 01 = FD`

---

## 5. Gesture parameter fine-tuning

### 5.1 Where the parameters are

Each gesture's angle offsets are defined with `#define` macros, so **there is no need to change the logic code** — just tune the numbers.

- **ESP-IDF edition**: the "gesture parameters (user-adjustable)" section at the top of `components/hand_gestures/hand_gestures.c`

### 5.2 What the parameters mean

```c
// Example: Rock gesture
#define ROCK_IDX_OFF1    70    // Index finger joint 1 offset
#define ROCK_IDX_OFF2   -70    // Index finger joint 2 offset
```

- **Positive = bend/close**, **negative = extend/open**
- Each finger has 2 offsets, relative to `middle_pos` (default 90°)
- Differential structure: the two servos sit side by side with collinear axes; same-direction rotation produces left/right splay, opposite-direction rotation produces flexion/extension; the sum of the two offsets corresponds to splay, the difference to flexion/extension.

### 5.3 Tuning steps

1. Find the `#define` macros for the corresponding gesture
2. Change the values (larger → greater amplitude; smaller → smaller amplitude)
3. Rebuild and re-flash, then test the result with the host software
4. Fine-tune repeatedly until the motion looks natural

---

## 6. FAQ

### Q1: The host software cannot connect to the serial port?

1. Confirm the ESP32 is connected to the computer via Type-C
2. Check that the COM port number in Device Manager matches the one selected in the GUI
3. Confirm the baud rate is 115200
4. Disconnect other software that is occupying the serial port

### Q2: No response after sending a command?

1. First send `AA 00 00 00` (NOP); you should receive `BB 00 00 00`
2. Confirm the firmware is flashed and the target chip is the ESP32-S3
3. Check the wiring (is GND common-grounded)

### Q3: The gesture amplitude is wrong or the direction is reversed?

Go to gesture parameter fine-tuning (see [Section 5](#5-gesture-parameter-fine-tuning)) and adjust the corresponding macro.

### Q4: Which gestures does left/right hand mode affect?

Gestures that **involve the thumb**, such as Rock/Scissors/Thumbs Up/OK/Pinch: after switching hands, the thumb's mirror direction changes.

### Q5: Fingers get stuck and cannot extend?

Before executing, all closing gestures automatically "open the whole hand first, then close", so fingers are not blocked by the previous gesture. If they still get stuck, check the mechanical assembly or reduce the closing amplitude.

## Related pages

- [PWM wiring, GPIO and power](../01-hardware/pwm.md)
- [PWM quick start](../02-quick-start/pwm.md)
- [PWM desktop host software](../04-desktop/pwm.md)
- [PWM hand tracking](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
