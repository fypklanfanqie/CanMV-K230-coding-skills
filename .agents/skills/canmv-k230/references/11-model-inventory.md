# 11 · kmodel 模型清单（53 个）

> 来源：`3.芯片资料&镜像&AI模型文件/02 AI模型文件/` 实际文件 + 例程中的调用参数整理。
> **部署位置**：拷到 `CanMV/sdcard/examples/kmodel/`（例程默认路径）。
> 标记说明：★ = 官方例程直接使用（参数可确认）；☆ = 输入尺寸为推断（未在例程中出现）。

---

## 1. 主模型库（`02 AI模型文件/02 kmodel/`，46 个）

### 1.1 人脸系列
| 模型 | 输入尺寸 | 用途 | 配套例程 |
|---|---|---|---|
| ★ `face_detection_320.kmodel` | 320×320 | 人脸检测（配 anchors `prior_data_320.bin`） | 5.1.x 全部 |
| ★ `face_landmark.kmodel` | 192×192 | 人脸 68 关键点 | 5.1.2 |
| ★ `face_alignment.kmodel` | 120×120 | 人脸 3D 网格对齐 | 5.1.3 |
| ★ `face_alignment_post.kmodel` | 120×120 | 3D 网格后处理网络 | 5.1.3 |
| ★ `face_pose.kmodel` | 120×120 | 人脸姿态（欧拉角） | 5.1.4 |
| ★ `face_recognition.kmodel` | 112×112☆ | 人脸特征提取（128 维） | 5.1.5 注册/识别 |
| `face_recognition_mobile.kmodel` | ☆ | 人脸识别（轻量版） | — |
| `face_liveness_rgb.kmodel` | ☆ | 人脸活体检测 | — |
| `face_parse.kmodel` | ☆ | 人脸解析（面部区域分割） | — |
| ☆ `yunet_640.kmodel` | 640×640 | YuNet 人脸检测（替代方案） | — |
| ☆ `eye_gaze.kmodel` | ☆ | 视线方向估计 | — |

### 1.2 人体系列
| 模型 | 输入尺寸 | 用途 | 配套例程 |
|---|---|---|---|
| ★ `person_detect_yolov5n.kmodel` | 640×640 | 人体检测（YOLOv5n，anchors 见 ref/06 §7.7） | 5.2.1 |
| ★ `yolov8n-pose.kmodel` | 320×320 | 人体 17 关键点姿态 | 5.2.2 |
| ★ `yolov5n-falldown.kmodel` | 640×640 | 跌倒检测（Fall/NoFall） | 5.2.3 |
| ☆ `body_seg.kmodel` | ☆ | 人体分割 | — |

### 1.3 手部/手势系列
| 模型 | 输入尺寸 | 用途 | 配套例程 |
|---|---|---|---|
| ★ `hand_det.kmodel` | 512×512 | 手掌检测 | 5.3.1/2/3/4/5 |
| ★ `handkp_det.kmodel` | 256×256 | 手部 21 关键点 | 5.3.2/3/4/5 |
| ★ `gesture.kmodel` | 224×224 | 动态手势分类 | 5.3.4 |
| `hand_reco.kmodel` | ☆ | 手势识别（分类） | —（可与 handkp 配套） |

### 1.4 车牌/OCR 系列
| 模型 | 输入尺寸 | 用途 | 配套例程 |
|---|---|---|---|
| ★ `LPD_640.kmodel` | 640×640 | 车牌检测（四角点） | 5.4.1 |
| ★ `licence_reco.kmodel` | 220×32 | 车牌字符识别（73 类字典） | 5.4.2 |
| ★ `ocr_det_int16.kmodel` | 640×640☆ | 文字区域检测 | 5.5.1 |
| ★ `ocr_rec_int16.kmodel` | ☆（配 dict.txt） | 文字识别（CTC 解码） | 5.5.2 |

### 1.5 YOLO 通用检测/分割/旋转框
| 模型 | 输入尺寸 | 用途 | 配套例程 |
|---|---|---|---|
| ★ `yolov8n_320.kmodel` | 320×320 | YOLOv8 通用物体检测（80 类 COCO） | 5.6.2（手写后处理） |
| `yolov8n_224.kmodel` | 224×224 | YOLOv8 检测（轻量） | 5.6.1 自学习（特征） |
| ★ `yolov8n_seg_320.kmodel` | 320×320 | YOLOv8 实例分割 | 5.6.3 |
| `yolov8n-obb.kmodel` | ☆ | YOLOv8 旋转目标框 | — |
| `yolo11n-obb.kmodel` | ☆ | YOLO11 旋转目标框 | — |

### 1.6 目标追踪（NanoTracker 三件套，5.6.4）
| 模型 | 输入尺寸 | 用途 |
|---|---|---|
| ★ `cropped_test127.kmodel` | 127×127 | 模板裁剪 |
| ★ `nanotrack_backbone_sim.kmodel` | 255×255 | 搜索区骨干特征 |
| ★ `nanotracker_head_calib_k230.kmodel` | — | 追踪头（输出新框） |

### 1.7 语音系列（KWS/TTS，8.2 与扩展）
| 模型 | 用途 |
|---|---|
| ★ `kws.kmodel` | 关键词唤醒（"小南小南"） |
| `multi_kws.kmodel` | 多关键词唤醒 |
| `hifigan.kmodel` | HiFiGAN 声码器（TTS 波形生成） |
| `zh_fastspeech_1_f32.kmodel` / `zh_fastspeech_2.kmodel` | 中文 FastSpeech 声学模型（本地 TTS 链路） |

### 1.8 水果系列（教学/示例，yolo11n/yolov5n/yolov8n × 检测/分类/分割）
| 模型 | 输入尺寸 | 用途 |
|---|---|---|
| `fruit_det_yolov5n_320.kmodel` / `fruit_det_yolov8n_320.kmodel` / `fruit_det_yolo11n_320.kmodel` | 320×320 | 水果检测 |
| `fruit_cls_yolov5n_224.kmodel` / `fruit_cls_yolov8n_224.kmodel` / `fruit_cls_yolo11n_224.kmodel` | 224×224 | 水果分类 |
| `fruit_seg_yolov5n_320.kmodel` / `fruit_seg_yolov8n_320.kmodel` / `fruit_seg_yolo11n_320.kmodel` | 320×320 | 水果分割 |

### 1.9 其它
| 模型 | 用途 |
|---|---|
| `recognition.kmodel` | 识别模型（用途以实际调用为准，未在教程中出现） |

---

## 2. 测试模型库（`02 AI模型文件/01 ai_test_kmodel/`，7 个）

| 模型 | 可能用途（测试集，用于验证环境/扩展玩法） |
|---|---|
| `embedding.kmodel` | 通用特征嵌入（检索/相似度） |
| `insect_det.kmodel` | 昆虫检测 |
| `landscape_multilabel.kmodel` | 风景多标签分类 |
| `ocular_seg.kmodel` | 眼部区域分割 |
| `veg_cls.kmodel` | 蔬菜分类 |
| `ocr_det_int16.kmodel` / `ocr_rec_int16.kmodel` | OCR 检测/识别（与主库同源） |

---

## 3. 使用指引

1. **选模型 = 选任务**：先在本表找到任务 → 看配套例程 → 复制例程 → 只改参数。
2. **输入尺寸必须与模型一致**：`model_input_size` 填错 → 推理结果乱/报错。
3. **anchors 文件**：人脸/手部/人体等锚框式模型需要 `/sdcard/examples/utils/prior_data_320.bin`（人脸系）或例程内嵌的 anchors 列表（手/人体系，见 ref/06）。
4. **没有例程的新模型**（如 fruit 系列）：按模型类型套用同类后处理：
   - YOLOv5 系 → `aicube.anchorbasedet_post_process`
   - YOLOv8/V11 系 → 手写后处理（ref/06 §7.20）或 `libs.YOLO`
   - 分类 → `np.argmax(output)`
   - 分割 → `aidemo.segment_postprocess`
   - 特征 → 直接取输出向量算余弦相似度
5. **部署位置**：`CanMV/sdcard/examples/kmodel/`；自定义模型可放 `/sdcard/` 根并在代码里写明路径。

> ⚠️ 模型文件较大（几 MB～十几 MB），全部拷贝耗时较长属正常；只拷需要的即可。
