# -*- coding: utf-8 -*-
# =============================================================================
# K230 触摸 UI 模板（顶部按钮 + 下方触摸画板）
# 硬件：3.5 寸 LCD（800x480，带触摸）
# 结构参考官方 touch_draw.py：区域命中 + 300ms 防抖 + 单画布分层重绘
# 用法：整段拖入 CanMV IDE → 运行；点击顶部按钮、在下方区域用手指绘制
# 调试：如需确认 event 值，取消注释主循环中的 print 行
# =============================================================================
import time, os
from machine import TOUCH
from media.display import *
from media.media import *
import image

# ------------------------------ 配置区 ---------------------------------------
DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 480
CANVAS_Y = 120          # 画布起始 y（上 120 像素为按钮区）
DEBOUNCE_MS = 300       # 按钮防抖（毫秒）
BRUSH_SIZE = 4
# -----------------------------------------------------------------------------

# 按钮区域: (x, y, w, h)
btn_clear  = (DISPLAY_WIDTH - 130, 0, 130, 50)
btn_color  = (0, 0, 130, 50)
btn_eraser = (DISPLAY_WIDTH // 2 - 80, 0, 220, 50)

current_color = (255, 0, 0)
eraser_mode = False
last_click_time = 0
last_point = None


def is_in_area(x, y, area):
    ax, ay, aw, ah = area
    return ax <= x < ax + aw and ay <= y < ay + ah


def draw_ui(img):
    """只重绘顶部按钮区（画布区保持不动）"""
    img.draw_rectangle(0, 0, DISPLAY_WIDTH, CANVAS_Y, color=(0, 0, 0), fill=True)
    # 清除
    img.draw_rectangle(btn_clear[0], btn_clear[1], btn_clear[2], btn_clear[3],
                       color=(200, 0, 0), fill=True)
    img.draw_string_advanced(btn_clear[0] + 18, btn_clear[1] + 12, 28, "清除",
                             color=(255, 255, 255))
    # 随机颜色
    img.draw_rectangle(btn_color[0], btn_color[1], btn_color[2], btn_color[3],
                       color=(230, 230, 0), fill=True)
    img.draw_string_advanced(btn_color[0] + 18, btn_color[1] + 12, 28, "随机",
                             color=(0, 0, 0))
    img.draw_circle(btn_color[0] + 160, 25, 18, color=current_color, thickness=3, fill=True)
    # 橡皮擦
    bg = (128, 128, 128) if eraser_mode else (0, 180, 180)
    img.draw_rectangle(btn_eraser[0], btn_eraser[1], btn_eraser[2], btn_eraser[3],
                       color=bg, fill=True)
    img.draw_string_advanced(btn_eraser[0] + 18, btn_eraser[1] + 12, 28,
                             "橡皮擦 ON" if eraser_mode else "橡皮擦 OFF",
                             color=(255, 255, 255))


def clear_canvas(img):
    img.draw_rectangle(0, CANVAS_Y, DISPLAY_WIDTH, DISPLAY_HEIGHT - CANVAS_Y,
                       color=(255, 255, 255), fill=True)


def hit_button(img, x, y):
    """按钮命中 + 防抖；命中返回 True"""
    global last_click_time, current_color, eraser_mode
    now = time.ticks_ms()
    if time.ticks_diff(now, last_click_time) < DEBOUNCE_MS:
        return True                                   # 防抖期内的点击忽略

    if is_in_area(x, y, btn_clear):
        clear_canvas(img)
        print("清除画布")
    elif is_in_area(x, y, btn_color):
        t = time.ticks_ms()
        current_color = ((t * 7) % 230 + 25, (t * 13) % 230 + 25, (t * 29) % 230 + 25)
        print("随机颜色:", current_color)
    elif is_in_area(x, y, btn_eraser):
        eraser_mode = not eraser_mode
        print("橡皮擦", "开启" if eraser_mode else "关闭")
    else:
        return False
    last_click_time = now
    return True


# ================================ 主程序 =====================================
try:
    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=False)
    MediaManager.init()

    img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.RGB565)
    img.clear()
    clear_canvas(img)
    draw_ui(img)
    Display.show_image(img)

    tp = TOUCH(0)
    print("触摸 UI 已启动")

    while True:
        os.exitpoint()
        p = tp.read(1)
        changed = False
        if p != ():
            for point in p:
                x, y = point.x, point.y
                # print("x=%d y=%d event=%d" % (x, y, point.event))   # 调 event 时打开
                if y < CANVAS_Y:
                    if hit_button(img, x, y):
                        changed = True
                    last_point = None
                else:
                    # 画布区域：连线
                    cp = (x, y)
                    if last_point:
                        color = (255, 255, 255) if eraser_mode else current_color
                        thick = 20 if eraser_mode else BRUSH_SIZE
                        img.draw_line(last_point[0], last_point[1], cp[0], cp[1],
                                      color=color, thickness=thick)
                        changed = True
                    last_point = cp
        else:
            last_point = None

        if changed:
            draw_ui(img)          # 重绘按钮区（避免笔迹覆盖按钮）
            Display.show_image(img)
        time.sleep_ms(20)

except KeyboardInterrupt:
    print("用户停止")
finally:
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
    print("资源已释放")
