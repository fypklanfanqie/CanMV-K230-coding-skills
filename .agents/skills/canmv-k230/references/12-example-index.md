# 12 · 官方例程全量索引

> 用途：**agent 接到需求后，先在这里定位最接近的例程，读取其源码再修改**。
> 路径基准：`CanMV K230/`（工作区内的资料包根目录）。
> 数据：教程源码 78 个 + `5.程序源码/` 96 个文件，共 174 个 .py。

---

## 1. 快速反查表（需求 → 例程）

| 需求关键词 | 例程路径（相对 `CanMV K230/`） |
|---|---|
| 点灯 / LED | `1.教程资料/1.快速使用/02 源码/1.4 运行示例/led.py` |
| 按键 / 中断 | `5.程序源码/self_learning.py`（按键逻辑）、`8.AI大模型课程/02 源码/8.3 语音识别/asr.py`（Button(21)） |
| 串口 UART | `1.教程资料/2.基础课程/02 源码/2.3 UART实验/UART.py` |
| I2C 扫描 | `1.教程资料/2.基础课程/02 源码/2.4 I2C实验/IIC.py` |
| SPI | `1.教程资料/2.基础课程/02 源码/2.5 SPI实验/SPI.py` |
| 蜂鸣器 PWM | `1.教程资料/2.基础课程/02 源码/2.6 PWM实验/PWM.py` |
| ADC 采集 | `1.教程资料/2.基础课程/02 源码/2.7 ADC实验/ADC.py` |
| RTC / 看门狗 / 定时器 | `2.基础课程/02 源码/2.8~2.10` |
| 加密 / 多线程 / 文件 | `2.基础课程/02 源码/2.12~2.15` |
| 摄像头显示 | `1.教程资料/3.多媒体课程/02 源码/3.1 Sensor实验/Sensor.py`、`3.2 Display/Display.py` |
| 录音 / 放音 | `3.多媒体课程/02 源码/3.3 Audio实验/audio.py` |
| 录像 / 播放视频 | `3.多媒体课程/02 源码/3.4 Video实验/Video_Recording.py`、`Video_play.py` |
| LVGL 界面 | `3.多媒体课程/02 源码/3.5 LVGL实验/Lvgl.py` |
| 颜色识别 | `4.OpenMV课程/02 源码/4.1 颜色识别/...` |
| 巡线 | `4.1 颜色识别/4.1.4 视觉巡线/line_patrol.py` |
| 二维码/条形码/DM/AprilTag | `4.2 码类识别/...` |
| 线段/矩形/圆/边缘 | `4.3 图像检测/...` |
| 人脸全套 | `5.AI视觉课程/02 源码/5.1 人脸识别/...` |
| 人体/跌倒 | `5.AI视觉课程/02 源码/5.2 人体检测/...` |
| 手势/猜拳 | `5.AI视觉课程/02 源码/5.3 手部识别/...` |
| 车牌 / OCR | `5.AI视觉课程/02 源码/5.4 车牌检测/`、`5.5 OCR检测/` |
| YOLO 检测/分割/追踪/自学习 | `5.AI视觉课程/02 源码/5.6 YOLOV8/...` |
| WiFi / TCP / UDP / HTTP | `6.网络基础课程/02 源码/...` |
| 触摸交互 | `7.触摸功能课程/02 源码/...` |
| 语音唤醒/ASR/TTS/LLM/VLM | `8.AI大模型课程/02 源码/...` |
| 训练与部署 | `9.在线模型训练/02 源码/`、`10.本地模型训练（YOLOv8）/02 源码/` |

---

## 2. 教程源码逐条清单

### 2.1 基础课程（15）
```
2.基础课程/02 源码/
├── 2.1 FPIOA实验/FPIOA.py
├── 2.2 GPIO实验/GPIO.py
├── 2.3 UART实验/UART.py
├── 2.4 I2C实验/IIC.py
├── 2.5 SPI实验/SPI.py
├── 2.6 PWM实验/PWM.py
├── 2.7 ADC实验/ADC.py
├── 2.8 RTC实验/RTC.py
├── 2.9 WDT实验/WDT.py
├── 2.10 TIMER实验/TIMER.py
├── 2.11 FFT实验/FFT.py
├── 2.12 SHA256 加密实验/SHA256.py
├── 2.13 AES 加密实验/AES_GCM.py
├── 2.14 多线程实验/thread.py
└── 2.15 文件读写/File_read_and_write.py
```

### 2.2 多媒体（5）
```
3.多媒体课程/02 源码/
├── 3.1 Sensor实验/Sensor.py
├── 3.2 Display/Display.py
├── 3.3 Audio实验/audio.py
├── 3.4 Video实验/Video_play.py、Video_Recording.py
└── 3.5 LVGL实验/Lvgl.py
```

### 2.3 OpenMV（13）
```
4.OpenMV课程/02 源码/
├── 4.1 颜色识别/{4.1.1 单一颜色识别实验/Single_color_recognition.py,
│                4.1.2 多种颜色识别实验/Multiple color recognition.py,
│                4.1.3 物体计数实验/object_counting.py,
│                4.1.4 视觉巡线/line_patrol.py}
├── 4.2 码类识别/{4.2.1 QR码识别实验/qrcodes.py,
│                4.2.2 条形码识别实验/barcode.py,
│                4.2.3 DM 码识别实验/Data Matrix.py,
│                4.2.4 AprilTags识别实验/AprilTags.py}
└── 4.3 图像检测/{4.3.1 线段检测实验/Line_segment_detection.py,
                 4.3.2 矩形检测实验/rectangular_detection.py,
                 4.3.3 圆形检测实验/circular_detection.py,
                 4.3.4 特征值检测实验/Eigenvalue_detection.py,
                 4.3.5 物体边缘检测/edge_detection.py}
```

### 2.4 AI 视觉（30+，重点目录）
```
5.AI视觉课程/02 源码/
├── 5.1 人脸识别/
│   ├── 5.1.1 人脸检测/face_detection.py
│   ├── 5.1.2 人脸关键部位检测/face_landmark.py
│   ├── 5.1.3 人脸3D网络/face_mesh.py
│   ├── 5.1.4 人脸姿态/face_pose.py
│   └── 5.1.5 人脸注册以及识别/
│       ├── 01人脸注册/face_registration.py
│       └── 02人脸识别/face_recognition.py
├── 5.2 人体检测/
│   ├── 5.2.1 人体检测/person_detection.py
│   ├── 5.2.2 人体关键点检测/person_kp_detect.py
│   └── 5.2.3 跌倒检测/falldown_detection.py
├── 5.3 手部识别/
│   ├── 5.3.1 手掌识别/hand_detection.py
│   ├── 5.3.2 手掌关键点检测/hand_keypoint_detection.py
│   ├── 5.3.3 手掌关键点分类/hand_keypoint_class.py
│   ├── 5.3.4 动态手势识别实验/dynamic_gesture.py
│   └── 5.3.5 剪头石头布实验/finger_guessing.py
├── 5.4 车牌检测/{5.4.1 车牌检测/licence_det.py, 5.4.2 车牌识别/licence_det_rec.py}
├── 5.5 OCR检测/{5.5.1 字符检测/ocr_det.py, 5.5.2 字符识别/ocr_rec.py}
└── 5.6 YOLOV8/
    ├── 5.6.1 自学习/self_learning.py
    ├── 5.6.2 物体检测/Item_detection.py（+ c.py 分步版）
    ├── 5.6.3 物体分割实验/Item_segmentation.py
    └── 5.6.4 目标追踪玩法/object_detection.py
```

### 2.5 网络（8）
```
6.网络基础课程/02 源码/
├── 6.1 有线连接实验/LAN.py
├── 6.2 无线连接实验/WIFI.py
├── 6.3 TCP_Client实验/TCP-Client.py
├── 6.4 TCP_Server实验/TCP-Server.py
├── 6.5 UDP_Client实验/UDP-Client.py
├── 6.6 UDP_Server实验/UDP-Server.py
├── 6.7 HTTP‑Client实验/HTTP-Client.py
└── 6.8 HTTP_Server实验/HTTP-Server.py
```

### 2.6 触摸（3）
```
7.触摸功能课程/02 源码/
├── 7.1 触摸检测/touch.py
├── 7.2 触摸画板/touch_draw.py
└── 7.3 触摸拍照/touch_photo.py
```

### 2.7 AI 大模型（6）
```
8.AI大模型课程/02 源码/
├── 8.2 语音唤醒/keyword_spotting.py
├── 8.3 语音识别/asr.py（完整版）
├── 8.4 语音合成/tts.py
├── 8.5 文字理解/llm.py
└── 8.6 图片理解/VLLM_Image_Understanding.py
（另有 5.程序源码/ 下的简化版 asr.py / VLLM_demo.py / vllm_understand.py）
```

### 2.8 模型训练
```
9.在线模型训练/02 源码/
├── 01 程序案例代码/det_video_1_2_2.py     # 低层推理模板（nn.kpu + nn.ai2d）
├── 02 模型文件/Hiwonder_Traffic_ight_recogni.zip
└── 03 数据集/
10.本地模型训练（YOLOv8）/02 源码/
├── 01 数据集处理/dataset.py
├── 02 ONNX转kmodel/convert_to_kmodel.py
└── 03 K230部署/Cat_and_dog_detection.py   # libs.YOLO 封装用法
```

---

## 3. `5.程序源码/` 独立源码包（96 个文件）

> 与教程源码基本同源（部分为简化版/变体），文件名直接对应功能；含 `(1)` 后缀的为重复副本。
> 板端通常位于 `/sdcard/examples/`（官方示例集合）。

| 分类 | 文件 |
|---|---|
| **基础外设** | `GPIO.py` `led.py` `PWM.py` `ADC.py` `IIC.py` `SPI.py` `UART.py` `RTC.py` `WDT.py` `TIMER.py` `FPIOA.py` `FFT.py` `SHA256.py` `AES_GCM.py` `thread.py` `File_read_and_write.py` |
| **多媒体** | `Sensor.py` `Display.py` `audio.py` `Video_play.py` `Video_Recording.py` `Lvgl.py` |
| **OpenMV** | `Single_color_recognition.py` `Multiple color recognition.py` `object_counting.py` `line_patrol.py` `qrcodes.py` `barcode.py` `Data Matrix.py` `AprilTags.py` `Line_segment_detection.py` `rectangular_detection.py` `circular_detection.py` `Eigenvalue_detection.py` `edge_detection.py` |
| **AI 视觉** | `face_detection.py` `face_landmark.py` `face_mesh.py` `face_pose.py` `face_registration.py` `face_recognition.py` `person_detection.py` `person_kp_detect.py` `falldown_detection.py` `hand_detection.py` `hand_keypoint_detection.py` `hand_keypoint_class.py` `dynamic_gesture.py` `finger_guessing.py` `licence_det.py` `licence_det_rec.py` `ocr_det.py` `ocr_rec.py` `self_learning.py` `Item_detection.py` `Item_segmentation.py` `object_detection.py` |
| **网络** | `LAN.py` `WIFI.py` `TCP-Client.py` `TCP-Server.py` `UDP-Client.py` `UDP-Server.py` `HTTP-Client.py` `HTTP-Server.py` |
| **触摸** | `touch.py` `touch_draw.py` `touch_photo.py` |
| **大模型** | `asr.py` `tts.py` `llm.py` `keyword_spotting.py` `vllm_understand.py` `VLLM_demo.py` |
| **其它** | `Item_detection.py` 等 |

---

## 4. 板端示例路径（对照）

| 电脑路径 | 板内路径 |
|---|---|
| `CanMV K230/5.程序源码/xxx.py` | `/sdcard/examples/xxx.py`（官方合集） |
| 你的项目 `projects/xxx/main.py` | `/sdcard/main.py`（脱机入口） |
| `02 AI模型文件/02 kmodel/*.kmodel` | `/sdcard/examples/kmodel/` |
| anchors、字体、人脸库 | `/sdcard/examples/utils/` |
| LVGL 资源 | `/sdcard/examples/15-LVGL/data/` |

---

## 5. 例程复用方法论（给 agent 的四步法）

1. **搜**：用本文档反查表 / 直接搜索资料包（关键词：`find_`、`kmodel`、`PipeLine`）。
2. **读**：完整读目标例程源码（不只看片段），确认：显示初始化顺序、预处理参数、后处理函数签名、资源释放。
3. **改**：
   - 换模型 → 改 `kmodel_path` + `model_input_size` + `postprocess`
   - 换任务 → 换 `postprocess` 与 `draw_result`
   - 换输入源 → 保持 PipeLine 不变（它是标准管线）
4. **验证**：把改动点写清注释，让用户在线运行后回报终端输出，再迭代。
