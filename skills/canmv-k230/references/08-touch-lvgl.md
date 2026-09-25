# 08 · 触摸交互与 LVGL 图形界面

> 来源：教程《7.触摸功能课程》3 个实验 + 《3.多媒体课程》LVGL 实验。
> 硬件前提：套件的 3.5 寸 LCD（800×480，ST7701）**自带电容触摸**（挂在 I2C3）。

---

## 1. 触摸 API（machine.TOUCH）

```python
from machine import TOUCH
tp = TOUCH(0)             # 触摸设备 0

p = tp.read()             # 读取所有触摸点 → 元组 (TPoint, ...)，无触摸时 ()
p = tp.read(1)            # 最多读 1 个点（做 UI 时用）
for point in p:
    x = point.x
    y = point.y
    event = point.event   # 事件类型（见下）
```

### event 事件值（**先用 print 观察再写逻辑！**）
不同固件/驱动的取值约定可能不同，官方例程中可见：
- `event == 1`：用于"点击按下"判定（触摸画板按钮逻辑）；
- `event == 2`：用于拍照触发（触摸拍照例程）；
- `event == 3`：出现在打印坐标分支（移动/抬起类）。

**保险做法**：第一次开发时先写
```python
p = tp.read(1)
if p != ():
    print(p[0].x, p[0].y, p[0].event)   # 观察实际按下/移动/抬起分别是几
```

### 初始化与主循环（同时显示画面）

```python
DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 480
Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=False)
MediaManager.init()
img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.RGB565)

tp = TOUCH(0)
while True:
    p = tp.read()
    img.clear()
    if p != ():
        for i, point in enumerate(p):
            text = f'x{i}={point.x} y{i}={point.y}'
            img.draw_string_advanced(10, 30 + i*40, 30, text, color=(255,0,0), scale=3)
    Display.show_image(img)
    time.sleep_ms(50)
```

---

## 2. 触摸 UI 的三个官方例程（可直接改造）

| 例程 | 文件 | 学什么 |
|---|---|---|
| 7.1 触摸检测 | `touch.py` | 读数、坐标显示 |
| 7.2 触摸画板 | `touch_draw.py` | **完整的按钮/滑杆/画布 UI 框架** |
| 7.3 触摸拍照 | `touch_photo.py` | 触摸拍照存 SD 卡（也用于收集训练数据集） |

### 2.1 触摸画板的关键模式（值得抄的工程细节）

```python
# ① 区域定义：每个按钮一个 (x, y, w, h)
clear_button_area = (DISPLAY_WIDTH - 130, 0, 130, 50)
save_button_area  = (0, 60, 130, 50)
eraser_button_area = (DISPLAY_WIDTH // 2 - 80, 0, 220, 50)
slider_area = (DISPLAY_WIDTH // 2 - 150, 70, 300, 40)
forbidden_draw_areas = [clear_button_area, color_button_area, save_button_area,
                        eraser_button_area, slider_area]     # 画布区域要排除按钮区

# ② 命中检测
def is_in_area(x, y, area):
    ax, ay, aw, ah = area
    return ax <= x < ax + aw and ay <= y < ay + ah

# ③ 按钮防抖（300ms）
DEBOUNCE_MS = 300
last_click_time = 0
def check_eraser_button_event(x, y, event):
    global eraser_mode, last_click_time
    if is_in_area(x, y, eraser_button_area) and event == 1:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_click_time) > DEBOUNCE_MS:
            eraser_mode = not eraser_mode
            last_click_time = now

# ④ 画线（两点连线段，原点在画布坐标）
def draw_line_between_points(p1, p2):
    if p1 and p2:
        canvas_img.draw_line(p1[0], p1[1], p2[0], p2[1],
                             color=current_color, thickness=brush_size)

# ⑤ 主循环：UI 层与画布层两张图，最后合成到屏幕
while True:
    os.exitpoint()
    p = tp.read(1)
    if p != ():
        for point in p:
            x, y = point.x, point.y
            if y >= CANVAS_Y:                       # 画布区域才画
                cp = (x, y - CANVAS_Y)
                draw_line_between_points(last_point, cp)
                last_point = cp
            else:
                last_point = None                    # 手离开画布断开
    else:
        last_point = None
    # 合成：先重绘 UI，再贴画布，再显示
```

### 2.2 触摸拍照（+ 数据集采集）

```python
save_dir = "/sdcard"
while True:
    img = sensor.snapshot()
    img.draw_circle(720, 240, 40, color=(200,200,200), thickness=10)  # 画快门按钮
    p = tp.read(1)
    if p != ():
        x, y, event = p[0].x, p[0].y, p[0].event
        if 720-40 < x < 720+40 and 240-40 < y < 240+40 and event == 2:
            img = sensor.snapshot()
            img.save("{}/photo_{}.jpg".format(save_dir, time.ticks_ms()))
            time.sleep(1)                 # 防连拍
    Display.show_image(img)
```
> 这个例程也是**做数据集**的标准方法：拍够几百张 → 去勘智平台标注训练（见 ref/10）。

---

## 3. LVGL 图形界面

> 官方例程：`3.多媒体课程/02 源码/3.5 LVGL实验/Lvgl.py`
> 用途：需要"现代 UI"（标签/按钮/滑杆/动画/列表）时用 LVGL，比手工 draw 高级但集成稍复杂。

### 3.1 初始化骨架

```python
import lvgl as lv
import image, time, os

select_display = 2      # 1=HDMI 2=LCD 3=IDE虚拟
RESOURCE_PATH = "/sdcard/examples/15-LVGL/data/"   # 字体/图片资源目录

# 显示初始化（同常规）
Display.init(Display.ST7701, width=800, height=480, to_ide=True)
MediaManager.init()

# LVGL 初始化（双缓冲 + flush 回调）
lv.init()
disp_drv = lv.disp_create(800, 480)
disp_img1 = image.Image(800, 480, image.ARGB8888)
disp_img2 = image.Image(800, 480, image.ARGB8888)

def disp_drv_flush_cb(disp_drv, area, color):
    global disp_img1, disp_img2
    if disp_drv.flush_is_last():
        if disp_img1.virtaddr() == uctypes.addressof(color.__dereference__()):
            Display.show_image(disp_img1)
        else:
            Display.show_image(disp_img2)
    disp_drv.flush_ready()

disp_drv.set_flush_cb(disp_drv_flush_cb)
disp_drv.set_draw_buffers(disp_img1.bytearray(), disp_img2.bytearray(),
                          disp_img1.size(), lv.DISP_RENDER_MODE.DIRECT)

# 主循环（注意 sleep 用 LVGL 的建议值）
while True:
    time.sleep_ms(lv.task_handler())
```

### 3.2 常用控件

```python
# 标签
label = lv.label(lv.scr_act())
label.set_text("你好 K230")
label.align(lv.ALIGN.TOP_MID, 0, 20)

# 字体（fnt 文件放 RESOURCE_PATH/font/）
font = lv.font_load("A:" + RESOURCE_PATH + "font/lv_font_simsun_16_cjk.fnt")
label.set_style_text_font(font, 0)

# 动画图片（多帧 png）
anim = lv.animimg(lv.scr_act())
anim.set_src([img_dsc1, img_dsc2, img_dsc3], 3)
anim.set_duration(2000)
anim.set_repeat_count(lv.ANIM_REPEAT_INFINITE)
anim.start()
```

### 3.3 坑点
- 字体/图片资源**必须存在**，缺文件时 UI 空白 → 例程里有 `verify_resources()` 检查函数可借用；
- `lv.font_load` 路径要加 `"A:"` 前缀（表示文件系统）；
- LVGL 较吃内存：800×480 双缓冲 ARGB8888 ≈ 640KB×2，注意剩余内存；
- LVGL + 触摸联动：需注册 indev 设备把 `TOUCH.read()` 事件喂给 LVGL（进阶，必要时手工实现按下/移动/抬起映射）。

---

## 4. 触摸 UI 选型建议

| 需求 | 推荐 |
|---|---|
| 几个按钮 + 简单状态显示 | 直接用 `touch_draw.py` 那套 draw + 区域命中（简单可靠） |
| 复杂界面（多页面/列表/动画） | LVGL |
| 触摸 + 视觉联合（点屏幕选目标/拍照） | 触摸 API + Sensor 混合（见 touch_photo.py） |
| 触摸事件调试 | `print(p)` 打印坐标与 event 值 |
