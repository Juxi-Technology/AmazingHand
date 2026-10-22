AmazingHand 网页控制 —— 第三方组件与署名
Third-party components and attribution

本仓库的原创代码（server.py、Amazinghand-web-io/ 下的前端 app.js、
tracking.js、index.html、style.css、io.js、ws.js、i18n.js、tools/）由
Juxi Technology 编写。前端只有一份，Python 服务端直接复用它。

本仓库另外包含或派生了以下第三方作品。它们的版权归各自权利人所有，
按各自的许可条款使用。

======================================================================
1. MediaPipe —— web/mediapipe/
======================================================================

  权利方   : Google LLC
  来源     : @mediapipe/tasks-vision
             https://www.npmjs.com/package/@mediapipe/tasks-vision
  许可     : Apache License, Version 2.0

包含的文件：

  web/mediapipe/vision_bundle.mjs                   MediaPipe 官方 JS 发行包
  web/mediapipe/wasm/vision_wasm_internal.js        Emscripten 编译产物
  web/mediapipe/wasm/vision_wasm_internal.wasm
  web/mediapipe/wasm/vision_wasm_module_internal.js
  web/mediapipe/wasm/vision_wasm_module_internal.wasm
  web/mediapipe/wasm/vision_wasm_nosimd_internal.js
  web/mediapipe/wasm/vision_wasm_nosimd_internal.wasm
  web/mediapipe/hand_landmarker.task                模型包，内含
                                                    hand_detector.tflite
                                                    hand_landmarks_detector.tflite

这些是 Google 发行的 MediaPipe 运行时与模型文件，不是本项目编写的。
它们被打包进来是为了让手势识别功能可以在**不连外网**的情况下使用
（国内访问 Google CDN 不稳定）。

出处核验（2026-10-14）：从官方源下载 @mediapipe/tasks-vision@1.0.1
与 storage.googleapis.com/mediapipe-models 对应文件逐一比对——

  hand_landmarker.task                    MD5 一致
  wasm/vision_wasm_internal.wasm          MD5 一致
  wasm/vision_wasm_internal.js            内容一致（仅行尾 CRLF/LF 不同）
  vision_bundle.mjs                       内容一致（仅行尾 CRLF/LF 不同）

即这些文件是 Google 官方发行物的原样拷贝，未经修改。

如需改用官方 CDN，删除 web/mediapipe/ 并把 Amazinghand-web-io/tracking.js 里的路径改回：

    https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm
    https://storage.googleapis.com/mediapipe-models/hand_landmarker/...

Apache License 2.0 全文见 LICENSE（若本仓库未附，可从上面链接获取）。

======================================================================
2. AmazingHand —— 舵机映射与姿态库
======================================================================

  权利方   : Pollen Robotics
  来源     : https://github.com/pollen-robotics/AmazingHand
             其中的 AmazingHandControl 子项目
  许可     : 代码 Apache License 2.0
             机械设计 CC BY 4.0

本仓库**未复制**该项目的源代码文件。派生的内容来自其公开的配置数据：

  数据来源 : AmazingHandControl/data/config.yaml
             AmazingHandControl/data/hand_config.yaml
  参考实现 : AmazingHandControl/hand_logic.py
             （DEFAULT_HAND_SERVOS、angle_rad()、adapt_pose_for_hand()）

  派生到   : config.json —— 舵机 ID 映射、19 个预设姿态、中位值、
             左右手的 angle_offset_deg / mirror_pose / 换算规则

换算公式与官方的 apply_pose() 等价：

    servo_deg = (ID 奇数 ? +1 : -1) × (姿态值 − angle_offset_deg)

本项目只是换了运行方式（浏览器网页而非 PyQt 桌面程序），
舵机控制逻辑与官方保持一致。

======================================================================
3. rustypot —— 运行时依赖
======================================================================

  SCS0009 舵机驱动库，由 pip 安装，不在本仓库内分发。
  见 requirements.txt。

======================================================================
备注
======================================================================

本仓库不分发任何机械设计文件（CAD/STL）。若后续加入，需同时遵守
Pollen Robotics 机械设计的 CC BY 4.0 条款（署名）。

本文件是技术性的出处说明，不构成法律意见。
