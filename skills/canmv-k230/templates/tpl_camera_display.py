# -*- coding: utf-8 -*-
# =============================================================================
# K230 摄像头 + 显示 基础模板（三种显示模式）
# 用途：任何视觉程序的起点 —— 采集、绘制信息、显示、完整释放
# 用法：选择 select_display 后整段拖入 CanMV IDE 运行
# =============================================================================
import time, os
from media.sensor import *
from media.display import *
from media.media import *

# =============================================================================
# == 选择显示模式 (1: HDMI, 2: LCD, 3: IDE虚拟显示) ==
# =============================================================================
select_display = 3      # 没接屏幕时用 3，画面回传到 CanMV IDE 预览区

# 分辨率配置
if select_display == 1:
    DISPLAY_WIDTH, DISPLAY_HEIGHT = 1920, 1080     # 按你的显示器调整！
elif select_display == 2:
    DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 480       # 3.5 寸 LCD 固定
else:
    DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 480       # IDE 虚拟显示，可改

CAM_WIDTH, CAM_HEIGHT = 800, 480                   # 摄像头采集分辨率

sensor = None
try:
    # ---------- 显示初始化 ----------
    if select_display == 1:
        Display.init(Display.LT9611, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
        print("显示：HDMI %dx%d" % (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    elif select_display == 2:
        Display.init(Display.ST7701, to_ide=True)
        print("显示：LCD 800x480")
    else:
        Display.init(Display.VIRT, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, fps=60, to_ide=True)
        print("显示：IDE 虚拟 %dx%d" % (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # ---------- 摄像头初始化 ----------
    sensor = Sensor()
    sensor.reset()
    sensor.set_framesize(width=CAM_WIDTH, height=CAM_HEIGHT)
    sensor.set_pixformat(Sensor.RGB565)

    # ---------- 媒体管理器 & 启动 ----------
    MediaManager.init()
    sensor.run()

    clock = time.clock()

    # ---------- 主循环 ----------
    while True:
        os.exitpoint()                       # 让 IDE 停止按钮生效
        clock.tick()
        img = sensor.snapshot()

        # ======== 你的图像处理逻辑写在这里（示例：画帧率 + 时间戳） ========
        img.draw_string_advanced(0, 0, 30,
                                 'FPS: %.2f' % clock.fps(),
                                 color=(255, 255, 0))
        img.draw_string_advanced(0, 36, 24,
                                 'K230 camera template',
                                 color=(255, 255, 255))
        # ==================================================================

        Display.show_image(img)

except KeyboardInterrupt:
    print("用户停止")
except BaseException as e:
    print("异常: %s" % e)
finally:
    # ---------- 资源释放（顺序不可改） ----------
    if isinstance(sensor, Sensor):
        sensor.stop()
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
    print("资源已释放")
