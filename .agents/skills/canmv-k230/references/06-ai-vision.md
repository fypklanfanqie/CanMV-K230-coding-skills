# 06 · AI 视觉开发全解（KPU / kmodel / AIBase）

> 来源：教程《5.AI视觉课程》22 大类 30+ 例程 + `5.程序源码/` 全部 AI 例程。
> 这是本资料包**技术含量最高**的部分。AI 程序全部遵循同一套骨架（PipeLine + AIBase + Ai2d），
> 每种任务的区别只在 **预处理参数 / 后处理函数 / 绘制方式**。

---

## 1. 架构总览

```
┌────────────────────────────────────────────────────────────┐
│  你的 MicroPython 脚本 (main.py)                            │
├───────────────┬─────────────────────┬──────────────────────┤
│  libs/        │  nncase_runtime     │  aidemo / aicube     │
│  PipeLine     │  (KPU 推理引擎)      │  (官方后处理库)       │
│  AIBase       │  nn.kpu()           │  face_det_post_process│
│  AI2D (Ai2d)  │  nn.from_numpy()    │  anchorbasedet_...   │
│  Utils        │  nn.ai2d()          │  ocr_post_process    │
│  YOLO         │                     │  segment_postprocess │
├───────────────┴─────────────────────┴──────────────────────┤
│  CanMV 固件 (local nncase v2.9.0)  →  K230 KPU 硬件          │
└────────────────────────────────────────────────────────────┘
```

**关键库位置（板端）**：`/sdcard/libs/` —— `PipeLine.py`、`AIBase.py`、`AI2D.py`、`Utils.py`、`YOLO.py`
（由固件/资料自带；脚本 `from libs.xxx import ...` 即可）

**模型位置**：`/sdcard/examples/kmodel/*.kmodel`；辅助文件（anchors 等）：`/sdcard/examples/utils/`

---

## 2. PipeLine —— 摄像头→AI→显示 的管线

```python
from libs.PipeLine import PipeLine, ScopedTiming

rgb888p_size = [1280, 720]                          # 送给 AI 的图像尺寸（宽16字节对齐）
display_mode = "lcd"                                # "hdmi" / "lcd" / "ide"(或"virtual")
pl = PipeLine(rgb888p_size=rgb888p_size, display_mode=display_mode)
pl.create()                                         # 也可 pl.create(Sensor(width=1920, height=1080))
display_size = pl.get_display_size()                # ★ 必须用这个实际显示尺寸做坐标换算

while True:
    with ScopedTiming("total", 1):
        img = pl.get_frame()                        # 取一帧（numpy，格式 RGB888P）
        res = app.run(img)                          # 你的 AIBase 子类推理
        app.draw_result(pl, res)                    # 画到 pl.osd_img
        pl.show_image()                             # 推屏
        gc.collect()

# 释放
app.deinit()
pl.destroy()
Display.deinit()
```

| 成员 | 说明 |
|---|---|
| `PipeLine(rgb888p_size, display_mode, display_size=?)` | 构造；display_mode 字符串决定输出设备 |
| `pl.create(sensor=None)` | 初始化底层（sensor 可传自定义分辨率实例） |
| `pl.get_frame()` | 取当前帧（numpy 数组，喂给 AIBase.run） |
| `pl.show_image()` | 把 osd 合成并显示 |
| `pl.osd_img` | OSD 图层图像对象（在此画框/文字） |
| `pl.get_display_size()` | 实际显示分辨率（**坐标换算基准**） |
| `pl.destroy()` | 释放管线 |

> **坐标系换算**：模型输出坐标基于 `rgb888p_size`，显示要乘以 `display_size / rgb888p_size`。

---

## 3. AIBase —— 所有 AI 任务的基类

### 3.1 必须实现的四个成员

```python
class MyApp(AIBase):
    def __init__(self, kmodel_path, model_input_size, rgb888p_size, display_size, debug_mode=0):
        super().__init__(kmodel_path, model_input_size, rgb888p_size, debug_mode)
        # 保存自己的参数；初始化 self.ai2d = Ai2d(debug_mode)

    def config_preprocess(self, input_image_size=None):   # 配置 Ai2d 预处理（pad/resize/crop/affine）
        ...

    def postprocess(self, results):                        # 解析模型输出 → 结构化结果
        ...

    def draw_result(self, pl, res):                        # 绘制到 pl.osd_img
        ...
```

### 3.2 基类提供的能力

| 成员 | 说明 |
|---|---|
| `self.inference(input_tensors)` | 底层推理（传 `nn.from_numpy(arr)` 的列表，返回输出列表） |
| `self.run(input_np)` | 标准入口：preprocess → inference → postprocess（**子类重写 preprocess 时才需要自己串**） |
| `self.preprocess(input_np)` | 默认实现用 `self.ai2d` 做预处理（子类可重写，如裁剪类） |
| `self.deinit()` | 释放 kmodel（**必须调用**） |
| `self.kmodel_path / model_input_size / rgb888p_size / display_size / debug_mode` | 通用属性 |

### 3.3 两种典型子类

**A. 单模型（人脸检测/人体检测/分割…）**：只重写 `config_preprocess` + `postprocess` + `draw_result`。

**B. 级联多模型（关键点/车牌识别/追踪…）**：定义多个 App 子类，再包一个"管理类"（如 `FaceLandMark`、`LicenceRec`），在管理类里串联 `det.run() → kp.config_preprocess(det) → kp.run()`。

---

## 4. Ai2d —— 硬件图像预处理

```python
from libs.AI2D import Ai2d
import nncase_runtime as nn
import ulab.numpy as np

ai2d = Ai2d(debug_mode)
ai2d.set_ai2d_dtype(nn.ai2d_format.NCHW_FMT, nn.ai2d_format.NCHW_FMT, np.uint8, np.uint8)

# 组合任意预处理步骤（顺序即执行顺序）：
ai2d.pad([0,0,0,0, top,bottom,left,right], 0, [104,117,123])   # 填充（颜色值）
ai2d.resize(nn.interp_method.tf_bilinear, nn.interp_mode.half_pixel)
ai2d.crop(x, y, w, h)                                          # 裁剪
ai2d.affine(nn.interp_method.cv2_bilinear, 0, 0, 127, 1, matrix) # 仿射（人脸对齐）

ai2d.build([1,3, in_h, in_w], [1,3, out_h, out_w])             # 编译
```

### 填充参数生成函数（libs.Utils）

| 函数 | 用途 | 返回 |
|---|---|---|
| `letterbox_pad_param(rgb888p_size, model_input_size)` | 保持比例填充（人脸类） | `top, bottom, left, right, ratio` |
| `center_pad_param(rgb888p_size, model_input_size)` | 居中填充（YOLO 类） | 同上 |

### 典型配置速查

| 任务类型 | 预处理组合 |
|---|---|
| 人脸检测 | `letterbox_pad_param` + pad + resize |
| 人脸关键点/姿态/注册 | `affine`（按检出的框算仿射矩阵）+ build |
| 手部关键点 | `crop`（按手部框）+ resize |
| YOLO 检测/分割 | `center_pad_param` + pad + resize |
| 追踪裁剪 | pad + crop（两段式，见 NanoTracker） |

---

## 5. Utils / nncase_runtime 工具速查

```python
from libs.Utils import *      # ALIGN_UP, ScopedTiming, letterbox_pad_param, center_pad_param, get_colors

ALIGN_UP(x, 16)               # 16 字节对齐（宽必须对齐，否则硬件异常）
with ScopedTiming("total", 1): ...       # 计时（第二参数>0 时打印耗时）
get_colors(n)                 # 生成 n 个预置颜色（ARGB）
```

```python
import nncase_runtime as nn
nn.from_numpy(np_array)       # numpy → tensor
tensor.to_numpy()             # tensor → numpy
nn.kpu()                      # 低层 KPU（一般不直接用，AIBase 已封装）
nn.shrink_memory_pool()       # 压缩内存池（例程入口处调用）
nn.interp_method.tf_bilinear / cv2_bilinear
nn.interp_mode.half_pixel
```

---

## 6. 后处理库（aidemo / aicube）函数清单

| 函数 | 用于 | 说明 |
|---|---|---|
| `aidemo.face_det_post_process(conf, nms, input_h, anchors, rgb888p_size, results)` | 人脸检测 | 返回 `[boxes...]` 或 `(boxes, landmarks)` |
| `aidemo.invert_affine_transform(matrix)` | 关键点 | 仿射逆变换 |
| `aidemo.face_mesh_post_process(roi, result)` | 3D 人脸 | 网格后处理 |
| `aidemo.face_draw_mesh(np_img, vertices)` | 3D 人脸 | 画网格 |
| `aidemo.polylines(np_img, points, closed, color, thickness, lineType, shift)` | 画多边形 | 关键点连线 |
| `aidemo.contours(np_img, points, mode, color, thickness, lineType)` | 画轮廓 | 关键点区域 |
| `aicube.anchorbasedet_post_process(out0,out1,out2, model_size, frame_size, strides, num_classes, conf, nms, anchors, nms_option)` | YOLOv5 系 | 锚框式检测后处理 |
| `aidemo.segment_postprocess(results, frame_size, model_size, display_size, conf, nms, mask_th, masks)` | YOLOv8-seg | 分割（掩码写入 masks 数组） |
| `aidemo.ocr_rec_preprocess(img, size, boxes)` | 车牌/OCR | 按检测框裁字 |
| `aicube.ocr_post_process(...)` | OCR 检测 | 文字区域检测后处理 |
| `aidemo.nanotracker_postprocess(out0, out1, frame_hw, thresh, center_xy_wh, crop_size, context)` | 目标追踪 | 返回新框 |
| `aidemo.kws_fp_create()` / `aidemo.kws_preprocess(fp, pcm)` | 语音唤醒 | 特征提取 |

---

## 7. 各任务实现要点（按官方例程）

> 路径基准：`1.教程资料/5.AI视觉课程/02 源码/`

### 7.1 人脸检测（5.1.1）
- 模型：`face_detection_320.kmodel`（输入 320×320）；anchors：`prior_data_320.bin`（4200×4）
- 预处理：letterbox pad（灰边 104,117,123）+ resize
- 后处理：`aidemo.face_det_post_process(0.5, 0.2, 320, anchors, rgb888p_size, results)`
- 绘制：`pl.osd_img.draw_rectangle(x,y,w,h, color=(255,255,0,255), thickness=2)`

### 7.2 人脸关键点（5.1.2）
- 级联：`face_detection_320` → `face_landmark.kmodel`（192×192）
- 关键点：人脸框 → 仿射矩阵（scale = model_in/(max(w,h)*1.5)）→ `ai2d.affine`
- 反变换回原图坐标：`aidemo.invert_affine_transform`
- 部位索引表 `dict_kp_seq`（眉/眼/鼻/唇/轮廓），用 `aidemo.polylines/contours` 画

### 7.3 人脸 3D 网格（5.1.3）
- 级联：det → `face_alignment.kmodel`(120×120) → `face_alignment_post.kmodel`(后处理网络)
- 后处理含 `param_mean/param_std`（例程里是长数组，直接复制）
- 画法：`aidemo.face_draw_mesh(draw_img_np, vertices)`

### 7.4 人脸姿态（5.1.4）
- 级联：det → `face_pose.kmodel`(120×120)
- 后处理：旋转矩阵 → 欧拉角（pitch/yaw/roll，例程有 `rotation_matrix_to_euler_angles`）
- 绘制：3D 框投影（`build_projection_matrix` + 8 点连线）

### 7.5 人脸注册（5.1.5/01）
- 流程：读取 `/sdcard/examples/utils/db_img/` 下的人脸图片 → 检测 → 关键点 → 特征提取（`face_recognition.kmodel`）→ 特征存到 `/sdcard/examples/utils/db/`
- 关键点对齐用标准 5 官坐标 `umeyama_args_112`（例程常量）

### 7.6 人脸识别（5.1.5/02）
- 加载 db → 摄像头实时检测 → 提特征 → 与库计算**余弦相似度** → 超过 `face_recognition_threshold=0.75` 判定同一人
- 库容量：100 张、特征维度 128

### 7.7 人体检测（5.2.1）
- 模型：`person_detect_yolov5n.kmodel`（640×640）；anchors 18 个：`[10,13,16,30,33,23,30,61,62,45,59,119,116,90,156,198,373,326]`
- 后处理：`aicube.anchorbasedet_post_process(..., strides=[8,16,32], ...)`
- 预处理：`center_pad_param`

### 7.8 人体关键点（5.2.2）
- 模型：`yolov8n-pose.kmodel`（320×320）
- 骨架连接 `SKELETON`（17 点 COCO 格式）+ 肢体颜色 `LIMB_COLORS`（例程常量，直接抄）
- 用 `aidemo.polylines` 画骨架

### 7.9 跌倒检测（5.2.3）
- 模型：`yolov5n-falldown.kmodel`（640×640），labels `["Fall","NoFall"]`
- 结构 = 7.7 换模型/标签

### 7.10 手掌识别（5.3.1）
- 模型：`hand_det.kmodel`（512×512），labels `["hand"]`
- anchors：`[26,27, 53,52, 75,71, 80,99, 106,82, 99,134, 140,113, 161,172, 245,276]`（9 对）

### 7.11 手掌关键点（5.3.2）
- 级联：`hand_det` → `handkp_det.kmodel`（256×256）
- 关键点后处理要**反裁剪映射**：`results*crop_w + crop_x`，再乘 display/rgb 比例

### 7.12 手掌关键点分类（5.3.3）
- 在 7.11 基础上，按关键点几何分类手势（例程有 `hk_gesture` 判定逻辑）

### 7.13 动态手势（5.3.4）
- 三级级联：`hand_det` → `handkp_det` → `gesture.kmodel`(224×224)
- 识别上下左右等动态手势（含滑动轨迹判定）

### 7.14 剪刀石头布（5.3.5）
- 在 7.12 基础上加 `random.randint` 出拳与比分逻辑（`guess_mode` 参数）

### 7.15 车牌检测（5.4.1）
- 模型：`LPD_640.kmodel`（640×640）；输出 4 角点（8 个数）→ 用 `draw_line` 连四边
- ⚠️ 注意：点序 x,y 与 crop 映射（例程 `point_8` 逻辑）

### 7.16 车牌识别（5.4.2）
- 级联：`LPD_640` → `licence_reco.kmodel`（220×32）
- 字符字典 `dict_rec`（73 类：省份简称+数字+字母+特殊）→ `np.argmax` + CTC 去重去空 → 字符串
- 用 `aidemo.ocr_rec_preprocess(input_np, size, det_boxes)` 裁框

### 7.17 字符检测 OCR（5.5.1）
- 模型：`ocr_det_int16.kmodel`；后处理 `aicube.ocr_post_process`
- 返回 `[裁剪图, 坐标列表]`，绘制 4 点框

### 7.18 字符识别 OCR（5.5.2）
- 级联 det → `ocr_rec_int16.kmodel`
- 字典文件 `dict.txt`（gb2312 编码）→ 建立 label→字符映射
- CTC 解码（忽略 blank 与连续重复）

### 7.19 YOLOv8 自学习（5.6.1）
- 模型：`yolov8n_224.kmodel` 的特征提取能力 + 自建特征库
- 按键（GPIO21）控制采样 → 特征存 `/sdcard/.../features/*.bin` → 余弦相似度匹配
- 最多 4 类、每类若干样本（`features=[2,2]`）

### 7.20 YOLOv8 物体检测（5.6.2）
- 模型：`yolov8n_320.kmodel`（320）；**后处理为手写**（`postprocess` 里 reshape/transpose/阈值/NMS，见 `Item_detection.py`）
- 80 类 COCO 标签（例程 labels 列表直接抄）
- 绘制：`pl.osd_img.draw_rectangle + draw_string_advanced`（含类别+置信度）

### 7.21 物体分割（5.6.3）
- 模型：`yolov8n_seg_320.kmodel`
- `aidemo.segment_postprocess(...)` 输出掩码到 `self.masks`（`np.zeros((1,H,W,4), np.uint8)`）
- 绘制：`image.Image(..., alloc=image.ALLOC_REF, data=self.masks)` + `copy_from`

### 7.22 目标追踪 NanoTracker（5.6.4）
- 三模型：`cropped_test127.kmodel`(127) + `nanotrack_backbone_sim.kmodel`(255) + `nanotracker_head_calib_k230.kmodel`
- 流程：按键启动 → 8 秒倒计时用当前画面建立模板 → 追踪输出新框
- 关键类：`TrackCropApp` / `TrackSrcApp` / `TrackerApp` / `NanoTracker`（可整体复用，见 `object_detection.py`）

---

## 8. 高级封装：libs.YOLO（推荐做检测任务时使用）

`10.本地模型训练` 的部署例程展示了官方 `libs.YOLO` 封装（比手写 postprocess 省事）：

```python
from libs.PipeLine import PipeLine, ScopedTiming
from libs.YOLO import YOLOv8

yolo = YOLOv8(task_type="detect",              # detect / segment / obb / classify
              mode="video",
              kmodel_path="/sdcard/pet_cat_dog_norm.kmodel",
              labels=["cat", "dog"],
              rgb888p_size=[1280,720],
              model_input_size=[320,320],
              display_size=[800,480],
              conf_thresh=0.7, nms_thresh=0.7,
              debug_mode=0)
yolo.config_preprocess()
while True:
    img = pl.get_frame()
    res = yolo.run(img)
    yolo.draw_result(res, pl.osd_img)
    pl.show_image()
    gc.collect()
# finally: yolo.deinit(); pl.destroy()
```
> ⚠️ 该封装在部分旧固件上可能不存在；若 `from libs.YOLO import YOLOv8` 报错，退回"AIBase + 手写后处理"方案（5.6.2 例程）。

---

## 9. 性能与内存工程实践

| 手段 | 效果 |
|---|---|
| `rgb888p_size` 降到 `[640,360]` / `[320,320]` | 显著提速（显示分辨率不变） |
| kmodel 从 640 → 320 → 224 | 推理耗时近线性下降 |
| `if (clock.fps())` 或用 `ScopedTiming` 定位瓶颈 | 先测量再优化 |
| 每帧 `gc.collect()` | 防止内存碎片导致的卡顿 |
| `del tensor/numpy` 大对象、`nn.shrink_memory_pool()` | 释放 KPU 内存池 |
| 只在检测到目标时才绘制/处理 | 减少 OSD 开销 |
| 用"通道2 给 AI、通道0 直通显示"（bind_layer） | 避免 CPU 拷贝大图 |
| 多模型级联时按需触发（如只在有检测框时跑关键点） | 省算力 |

**内存红线**：1G 版内存跑大模型（640 输入 + 1080p 显示 + 多模型级联）容易 OOM。遇到 `MemoryError` / 莫名卡死：
降低一切分辨率 → 换小模型 → 单模型方案。

---

## 10. 常见 AI 开发错误对照

| 现象 | 原因 | 解决 |
|---|---|---|
| `OSError: [Errno 2]` 打开 kmodel 失败 | 模型不在 `/sdcard/examples/kmodel/` | 拷贝模型 |
| 检测框位置全错 | `display_size` 没用 `pl.get_display_size()` / 忘了乘比例 | 检查坐标换算 |
| 推理输出形状对不上 | `postprocess` 的 reshape 不符合该模型输出 | 对照例程；print 输出 shape |
| 画面有框但卡顿 | 分辨率/模型过大 | §9 优化 |
| `ImportError: libs` | 固件不是官方镜像（没有 /sdcard/libs） | 重烧官方镜像 |
| 运行一会就崩 | 没 `gc.collect()` / 没释放 tensor | 按 §9 |
| 重复运行黑屏 | 没 deinit/destroy | 检查 finally |
