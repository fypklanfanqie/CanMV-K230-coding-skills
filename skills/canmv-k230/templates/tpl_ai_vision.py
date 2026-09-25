# -*- coding: utf-8 -*-
# =============================================================================
# K230 AI 视觉模板（AIBase + PipeLine 标准结构，以「人脸检测」为例）
# 说明：这是所有 kmodel 例程的通用骨架。
#       换任务时：改模型路径/输入尺寸 → 改 postprocess → 改 draw_result
#       （各任务的后处理写法见 references/06-ai-vision.md 或对应官方例程）
# 依赖：官方镜像自带的 /sdcard/libs/ + /sdcard/examples/kmodel/face_detection_320.kmodel
# =============================================================================
from libs.PipeLine import PipeLine
from libs.AIBase import AIBase
from libs.AI2D import Ai2d
from libs.Utils import *
import os, sys, gc
from media.media import *
from media.display import Display
import nncase_runtime as nn
import ulab.numpy as np
import image
import aidemo

# =============================================================================
# == 选择显示模式 (1: HDMI, 2: LCD, 3: IDE虚拟显示) ==
# =============================================================================
select_display = 3

def init_display(select_display, width, height):
    if select_display == 1:
        Display.init(Display.LT9611, width=width, height=height, to_ide=True)
        print("显示：HDMI %dx%d" % (width, height))
    elif select_display == 2:
        Display.init(Display.ST7701, to_ide=True)
        print("显示：LCD 800x480")
    elif select_display == 3:
        Display.init(Display.VIRT, width=width, height=height, fps=100, to_ide=True)
        print("显示：IDE 虚拟 %dx%d" % (width, height))
    else:
        raise ValueError("select_display 参数错误，应为 1、2 或 3")

def deinit_display():
    Display.deinit()
    print("释放显示资源")


# ========================== 人脸检测任务类 ====================================
class FaceDetectionApp(AIBase):
    def __init__(self, kmodel_path, model_input_size, anchors,
                 confidence_threshold=0.5, nms_threshold=0.2,
                 rgb888p_size=[1280, 720], display_size=[800, 480], debug_mode=0):
        super().__init__(kmodel_path, model_input_size, rgb888p_size, debug_mode)
        self.kmodel_path = kmodel_path
        self.model_input_size = model_input_size
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.anchors = anchors
        self.rgb888p_size = [ALIGN_UP(rgb888p_size[0], 16), rgb888p_size[1]]
        self.display_size = [ALIGN_UP(display_size[0], 16), display_size[1]]
        self.debug_mode = debug_mode
        self.ai2d = Ai2d(debug_mode)
        self.ai2d.set_ai2d_dtype(nn.ai2d_format.NCHW_FMT,
                                 nn.ai2d_format.NCHW_FMT,
                                 np.uint8, np.uint8)

    def config_preprocess(self, input_image_size=None):
        with ScopedTiming("set preprocess config", self.debug_mode > 0):
            ai2d_input_size = input_image_size if input_image_size else self.rgb888p_size
            top, bottom, left, right, _ = letterbox_pad_param(self.rgb888p_size,
                                                              self.model_input_size)
            self.ai2d.pad([0, 0, 0, 0, top, bottom, left, right], 0, [104, 117, 123])
            self.ai2d.resize(nn.interp_method.tf_bilinear, nn.interp_mode.half_pixel)
            self.ai2d.build(
                [1, 3, ai2d_input_size[1], ai2d_input_size[0]],
                [1, 3, self.model_input_size[1], self.model_input_size[0]])

    def postprocess(self, results):
        with ScopedTiming("postprocess", self.debug_mode > 0):
            post_ret = aidemo.face_det_post_process(
                self.confidence_threshold,
                self.nms_threshold,
                self.model_input_size[1],
                self.anchors,
                self.rgb888p_size,
                results)
            if len(post_ret) == 0:
                return post_ret
            else:
                return post_ret[0]

    def draw_result(self, pl, dets):
        with ScopedTiming("display_draw", self.debug_mode > 0):
            pl.osd_img.clear()
            if dets:
                for det in dets:
                    x, y, w, h = map(lambda v: int(round(v, 0)), det[:4])
                    x = x * self.display_size[0] // self.rgb888p_size[0]
                    y = y * self.display_size[1] // self.rgb888p_size[1]
                    w = w * self.display_size[0] // self.rgb888p_size[0]
                    h = h * self.display_size[1] // self.rgb888p_size[1]
                    # OSD 图层颜色格式为 ARGB: (A, R, G, B)
                    pl.osd_img.draw_rectangle(x, y, w, h, color=(255, 255, 255, 0), thickness=2)
                    # 如返回的 det 含置信度（det[4]），可改为: "face %.2f" % det[4]
                    pl.osd_img.draw_string_advanced(x, y - 40, 32, "face",
                                                    color=(255, 255, 255, 0))


# ============================== 主程序 =======================================
if __name__ == "__main__":
    display_mode_map = {1: "hdmi", 2: "lcd", 3: "ide"}
    display_mode = display_mode_map.get(select_display, "ide")

    if display_mode == "hdmi":
        display_size = [1920, 1080]
    elif display_mode == "lcd":
        display_size = [800, 480]
    else:
        display_size = [1280, 720]

    rgb888p_size = [1280, 720]                                  # AI 输入分辨率

    # ---- 模型与参数 ----
    kmodel_path = "/sdcard/examples/kmodel/face_detection_320.kmodel"
    confidence_threshold = 0.5
    nms_threshold = 0.2
    anchor_len = 4200
    det_dim = 4
    anchors_path = "/sdcard/examples/utils/prior_data_320.bin"
    anchors = np.fromfile(anchors_path, dtype=np.float)
    anchors = anchors.reshape((anchor_len, det_dim))

    # ---- 初始化显示 ----
    init_display(select_display, width=display_size[0], height=display_size[1])

    # ---- 初始化 PipeLine ----
    pl = PipeLine(rgb888p_size=rgb888p_size, display_mode=display_mode)
    pl.create()
    display_size = pl.get_display_size()

    # ---- 实例化任务并配置预处理 ----
    face_det = FaceDetectionApp(kmodel_path,
                                model_input_size=[320, 320],
                                anchors=anchors,
                                confidence_threshold=confidence_threshold,
                                nms_threshold=nms_threshold,
                                rgb888p_size=rgb888p_size,
                                display_size=display_size,
                                debug_mode=0)
    face_det.config_preprocess()

    try:
        while True:
            os.exitpoint()
            with ScopedTiming("total", 1):
                img = pl.get_frame()          # 取一帧（numpy）
                res = face_det.run(img)       # 推理
                face_det.draw_result(pl, res) # 绘制到 OSD
                pl.show_image()               # 显示
                gc.collect()

    except KeyboardInterrupt:
        print("用户中断退出程序")
    except BaseException as e:
        sys.print_exception(e)
    finally:
        face_det.deinit()
        pl.destroy()
        deinit_display()
        print("程序已退出")

# =============================================================================
# 【换任务指南】
# 1) 换模型：kmodel_path + model_input_size（见 ref/11-model-inventory.md）
# 2) 换预处理：
#    - 人脸/关键点类：letterbox_pad_param + pad + resize / affine
#    - YOLO 类：center_pad_param + pad + resize
# 3) 换后处理：ref/06-ai-vision.md §6 后处理函数清单
# 4) 换绘制：pl.osd_img.draw_*（ARGB 颜色）
# =============================================================================
