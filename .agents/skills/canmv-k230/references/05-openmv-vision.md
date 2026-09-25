# 05 · OpenMV 机器视觉 API（传统图像算法，不依赖模型）

> 来源：教程《4.OpenMV课程》13 个实验 + `5.程序源码/` 中同名例程。
> 全部 API 挂在 `image.Image` 对象上（`img = sensor.snapshot()` 之后直接调用）。
> 特点：**CPU 计算、无需 kmodel、速度快、调参直观**；适合颜色/形状/码类任务。

---

## 1. 核心对象：image.Image

```python
img = sensor.snapshot()          # 采集一帧（返回 image.Image）
img.width(); img.height()
img.format()                     # 当前像素格式
img.clear()
img.copy_from(other)
img.save("/sdcard/photo.jpg")    # 存图（需 SD 卡）
img.to_numpy_ref()               # 转 numpy 引用（AI 用）
```

---

## 2. 颜色识别（find_blobs）

### 2.1 LAB 阈值（**不是 RGB！**）

阈值格式：`(L_min, L_max, A_min, A_max, B_min, B_max)`，可传多个做多色识别：

```python
thresholds = [
    (0, 100, 29, 127, 3, 127),     # 红
    (30, 100, -64, -8, 50, 70),    # 绿
    (0, 100, -128, -18, 1, 127),   # 蓝
]
```

**如何调**（重要，永远别手填）：
1. 在线运行找色程序 → 画面里放好目标色块；
2. CanMV IDE 菜单 **工具 → 机器视觉 → 阈值编辑器** → 选"帧缓冲区"；
3. 拖滑杆，直到右侧二值图中**只有目标变白**；
4. 复制 6 个数值填回代码（黑色=不识别，白色=识别）。

### 2.2 查找色块

```python
blobs = img.find_blobs(thresholds, roi=(x,y,w,h), merge=True)
for b in blobs:
    img.draw_rectangle(b[0:4], thickness=2)   # 外接矩形
    img.draw_cross(b[5], b[6], thickness=2)   # 中心十字
```

### 2.3 blob 对象取值表（索引 + 方法双写法）

| 索引 | 方法 | 含义 |
|---|---|---|
| `b[0]` | `b.x()` | 外接矩形左上角 x |
| `b[1]` | `b.y()` | 左上角 y |
| `b[2]` | `b.w()` | 宽 |
| `b[3]` | `b.h()` | 高 |
| `b[4]` | `b.pixels()` | 像素数（面积） |
| `b[5]` | `b.cx()` | 质心 x |
| `b[6]` | `b.cy()` | 质心 y |
| `b[7]` | `b.rotation()` | 旋转角（弧度） |
| `b[8]` | `b.code()` | 颜色标签（多阈值时） |

- `roi=(x,y,w,h)`：只在该区域找（**巡线/R 分区的关键**）；
- `merge=True`：合并相邻色块（同色连成一片）；
- `pixels()` 过滤噪点：`if b.pixels() > 100:`。

### 2.4 典型应用
- **单/多色识别**：`4.1.1` / `4.1.2`
- **物体计数**：`len(blobs)` 即个数（`4.1.3`）
- **视觉巡线**（`4.1.4`）：把画面分 3 个 ROI（上/中/下），每区取最大黑色 blob，用权重求中心线偏差：

```python
BLACK_THRESHOLD = [(0, 24, -128, 4, -128, 7)]
ROIS = [(0,200,320,40,0.7), (0,100,320,40,0.3), (0,0,320,40,0.1)]  # (x,y,w,h,权重)
centroid_sum = 0
for r in ROIS:
    blobs = img.find_blobs(BLACK_THRESHOLD, roi=r[0:4], merge=True)
    if blobs:
        largest = max(blobs, key=lambda b: b.pixels())
        img.draw_rectangle(largest[0:4]); img.draw_cross(largest[5], largest[6])
        centroid_sum += largest.cx() * r[4]
# centroid_sum / 权重和 = 线中心 → 与画面中心差即转向偏差
```

---

## 3. 码类识别

| 码型 | API | 对象方法 | 例程 |
|---|---|---|---|
| 二维码 QR | `img.find_qrcodes()` | `code.rect()`, `code.payload()` | `4.2.1 qrcodes.py` |
| 条形码 | `img.find_barcodes()` | `code.type()`（类型枚举）, `.payload()`, `.rotation()`, `.quality()` | `4.2.2 barcode.py` |
| Data Matrix | `img.find_datamatrices()` | `.rows()`, `.columns()`, `.payload()` | `4.2.3 Data Matrix.py` |
| AprilTag | `img.find_apriltags(families=)`, `.id()`, `.family()`, `.cx()/.cy()`, `.rotation()` | 可算 3D 位姿 | `4.2.4 AprilTags.py` |

### 条形码类型枚举（image 常量）
`EAN2 EAN5 EAN8 UPCE ISBN10 UPCA EAN13 ISBN13 I25 DATABAR DATABAR_EXP CODABAR CODE39 PDF417 CODE93 CODE128`
（参考 `barcode_name()` 函数，例程里有完整映射）

### AprilTag 家族常量
`image.TAG16H5 TAG25H7 TAG25H9 TAG36H10 TAG36H11 ARTOOLKIT`
```python
tag_families = 0
tag_families |= image.TAG36H11
for tag in img.find_apriltags(families=tag_families):
    img.draw_rectangle(tag.rect(), color=(255,0,0))
    img.draw_cross(tag.cx(), tag.cy(), color=(0,255,0))
    print("ID", tag.id(), "rot", (180 * tag.rotation()) / math.pi)
```
**生成标签**：CanMV IDE → 工具 → 机器视觉 → AprilTag 生成器 → 选 TAG36H11 → 填 ID 范围 → 输出文件夹 → 打印。

---

## 4. 几何检测

| 检测 | API | 常用参数 | 结果对象 |
|---|---|---|---|
| 线段 | `img.find_line_segments(merge_distance=0, max_theta_diff=5)` | 合并距离/角度差 | `l.line()`, `l.magnitude()`, `l.theta()` |
| 直线 | `img.find_lines(threshold=1000, theta_margin=25, rho_margin=25)` | 霍夫变换阈值 | `l.line()`, `l.theta()` |
| 矩形 | `img.find_rects(threshold=10000)` | 阈值越大越严格 | `r.rect()`, `r.corners()`（4 角） |
| 圆形 | `img.find_circles(threshold=2000, x_margin=10, y_margin=10, r_margin=10, r_min=2, r_max=100, r_step=2)` | 合并参数 | `c.x() c.y() c.r() c.magnitude()` |
| 边缘 | `img.find_edges(image.EDGE_CANNY, threshold=(50,80))` 或 `EDGE_SIMPLE` | Canny 双阈值 | 直接改写图像 |
| 特征点 | `img.find_keypoints()`（旧版）/ 角点检测 | — | — |

**性能提示**：
- 边缘/直线类建议 `Sensor.GRAYSCALE` + 320×240，帧率能到几十 FPS；
- `find_line_segments` 前可 `img.lens_corr(1.8)` 做镜头畸变校正（鱼眼/广角镜头）。

---

## 5. 绘制 API（都画在 img 上，直接随图显示）

```python
img.draw_rectangle(x, y, w, h, color=(255,0,0), thickness=2)    # 或传 (x,y,w,h)
img.draw_rectangle(rect_tuple, thickness=2, fill=False)
img.draw_line(x0, y0, x1, y1, color=(255,0,0), thickness=2)     # 或 l.line()
img.draw_circle(x, y, r, color=(0,255,0), thickness=2, fill=False)
img.draw_cross(x, y, color=(0,255,0), size=5, thickness=1)
img.draw_string_advanced(x, y, size, "中文OK", color=(255,255,255), scale=2)
img.draw_arrow(...)   # 部分固件支持
```

> **颜色格式差异**（易搞混）：
> - `img.draw_*`（画在摄像头图上）：RGB 元组 `(r,g,b)`；
> - `pl.osd_img.draw_*`（AI 例程 OSD 层）：ARGB 元组 `(255,r,g,b)`。

---

## 6. 完整例程索引（`1.教程资料/4.OpenMV课程/02 源码/`）

```
4.1 颜色识别/
├── 4.1.1 单一颜色识别实验/Single_color_recognition.py
├── 4.1.2 多种颜色识别实验/Multiple color recognition.py
├── 4.1.3 物体计数实验/object_counting.py
└── 4.1.4 视觉巡线/line_patrol.py
4.2 码类识别/
├── 4.2.1 QR码识别实验/qrcodes.py
├── 4.2.2 条形码识别实验/barcode.py
├── 4.2.3 DM 码识别实验/Data Matrix.py
└── 4.2.4 AprilTags识别实验/AprilTags.py
4.3 图像检测/
├── 4.3.1 线段检测实验/Line_segment_detection.py
├── 4.3.2 矩形检测实验/rectangular_detection.py
├── 4.3.3 圆形检测实验/circular_detection.py
├── 4.3.4 特征值检测实验/Eigenvalue_detection.py
└── 4.3.5 物体边缘检测/edge_detection.py
```

**改编套路**：这些例程结构完全一致 —— ① `select_display` 初始化显示 ② `Sensor` 初始化 ③ `while True: snapshot → find_xxx → draw_xxx → show_image`。改需求 = 换 `find_*` 算法 + 换绘制/逻辑。

---

## 7. 与 AI 视觉的选型建议

| 需求 | 推荐方案 | 理由 |
|---|---|---|
| 找特定颜色/色块、计数 | find_blobs（本文件） | 零模型、几十 FPS |
| QR/条形码/AprilTag | find_qrcodes 等（本文件） | 专用解码头，秒级 |
| 巡线/直线/圆/矩形 | find_lines 等（本文件） | 灰度下极快 |
| 识别人脸/人/手势/车牌/通用物体 | AI 模型（ref/06） | 传统算法做不了 |
| 颜色+AI 混合（如"红色交通灯"） | 先 YOLO 检测区，再 ROI 内 find_blobs 二次确认 | 提高准确率 |
