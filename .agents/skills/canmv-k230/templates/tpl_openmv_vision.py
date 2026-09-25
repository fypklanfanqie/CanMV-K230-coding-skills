# -*- coding: utf-8 -*-
# =============================================================================
# K230 OpenMV 视觉模板（颜色识别 + 二维码 + 线段检测，多算法演示）
# 用途：不依赖 AI 模型的传统视觉任务
# 提示：阈值请用 CanMV IDE「工具 → 机器视觉 → 阈值编辑器」调好再填入
# =============================================================================
import time, os, math
from media.sensor import *
from media.display import *
from media.media import *

# =============================================================================
# == 选择显示模式 (1: HDMI, 2: LCD, 3: IDE虚拟显示) ==
# =============================================================================
select_display = 3

# ------------------------------ 配置区 ---------------------------------------
# LAB 颜色阈值：(L_min, L_max, A_min, A_max, B_min, B_max)
# 以下为出厂默认红/绿/蓝示例值，务必用阈值编辑器按你的实物调优！
COLOR_THRESHOLDS = [
    (0, 100, 29, 127, 3, 127),      # 红
    (30, 100, -64, -8, 50, 70),     # 绿
    (0, 100, -128, -18, 1, 127),    # 蓝
]
COLOR_NAMES  = ["RED", "GREEN", "BLUE"]
COLOR_DRAWS  = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]   # 绘制颜色(RGB)

ENABLE_BLOB   = True      # 颜色识别
ENABLE_QR     = True      # 二维码
ENABLE_LINE   = False     # 线段检测（灰度更快）
MIN_BLOB_PIX  = 100       # 色块最小像素（过滤噪点）
# -----------------------------------------------------------------------------

sensor = None
try:
    # 显示
    if select_display == 1:
        Display.init(Display.LT9611, width=1280, height=720, to_ide=True)
    elif select_display == 2:
        Display.init(Display.ST7701, to_ide=True)
    else:
        Display.init(Display.VIRT, width=800, height=480, fps=60, to_ide=True)

    # 摄像头
    sensor = Sensor()
    sensor.reset()
    sensor.set_framesize(width=800, height=480)
    sensor.set_pixformat(Sensor.RGB565)
    MediaManager.init()
    sensor.run()

    clock = time.clock()

    while True:
        os.exitpoint()
        clock.tick()
        img = sensor.snapshot()

        # ---------------- 1) 多颜色识别 ----------------
        if ENABLE_BLOB:
            for i, th in enumerate(COLOR_THRESHOLDS):
                blobs = img.find_blobs([th], merge=True)
                for b in blobs:
                    if b.pixels() < MIN_BLOB_PIX:
                        continue
                    img.draw_rectangle(b[0:4], color=COLOR_DRAWS[i], thickness=2)
                    img.draw_cross(b[5], b[6], color=COLOR_DRAWS[i], thickness=2)
                    img.draw_string_advanced(b[0], b[1] - 30, 24, COLOR_NAMES[i],
                                             color=COLOR_DRAWS[i])

        # ---------------- 2) 二维码识别 ----------------
        if ENABLE_QR:
            for code in img.find_qrcodes():
                rect = code.rect()
                img.draw_rectangle(rect, color=(255, 0, 0), thickness=3)
                img.draw_string_advanced(rect[0], rect[1] - 32, 24,
                                         code.payload(), color=(255, 0, 0))
                print("二维码内容:", code.payload())

        # ---------------- 3) 线段检测（灰度图像更快） ----------------
        if ENABLE_LINE:
            for l in img.find_line_segments(merge_distance=0, max_theta_diff=5):
                img.draw_line(l.line(), color=(255, 0, 0), thickness=2)

        img.draw_string_advanced(0, 0, 30, 'FPS: %.2f' % clock.fps(),
                                 color=(255, 255, 255))
        Display.show_image(img)
        print("FPS: %.2f" % clock.fps())

except KeyboardInterrupt:
    print("用户停止")
except BaseException as e:
    print("异常: %s" % e)
finally:
    if isinstance(sensor, Sensor):
        sensor.stop()
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
    print("资源已释放")
