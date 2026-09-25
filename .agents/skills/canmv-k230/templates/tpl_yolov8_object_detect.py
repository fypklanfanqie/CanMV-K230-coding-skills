# -*- coding: utf-8 -*-
# =============================================================================
# K230 YOLOv8 物体检测模板（80 类 COCO，手写后处理版）
# 基于官方例程 Item_detection.py 整理，可直接运行 / 训练自己的模型后替换参数
# 模型：/sdcard/examples/kmodel/yolov8n_320.kmodel
# 自定义模型：把 kmodel 拷到板子，改 KMODEL_PATH / LABELS / MODEL_INPUT_SIZE
# =============================================================================
from libs.PipeLine import PipeLine, ScopedTiming
from libs.AIBase import AIBase
from libs.AI2D import Ai2d
from libs.Utils import *
import os, sys, gc, time
from media.media import *
from media.sensor import *
from media.display import Display
import nncase_runtime as nn
import ulab.numpy as np
import image

# =============================================================================
# == 选择显示模式 (1: HDMI, 2: LCD, 3: IDE虚拟显示) ==
# =============================================================================
select_display = 3

# ------------------------------ 配置区 ---------------------------------------
KMODEL_PATH = "/sdcard/examples/kmodel/yolov8n_320.kmodel"
MODEL_INPUT_SIZE = [320, 320]          # 必须与模型一致
RGB888P_SIZE = [320, 320]              # 送给 AI 的图像尺寸
CONF_THRESHOLD = 0.2
NMS_THRESHOLD  = 0.2
MAX_BOXES      = 50

# 80 类 COCO 标签（自定义模型请替换为你的标签）
LABELS = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
          "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
          "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
          "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
          "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
          "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
          "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
          "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
          "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
          "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
# -----------------------------------------------------------------------------


class ObjectDetectionApp(AIBase):
    def __init__(self, kmodel_path, labels, model_input_size, max_boxes_num,
                 confidence_threshold=0.5, nms_threshold=0.2,
                 rgb888p_size=[224, 224], display_size=[800, 480], debug_mode=0):
        super().__init__(kmodel_path, model_input_size, rgb888p_size, debug_mode)
        self.kmodel_path = kmodel_path
        self.labels = labels
        self.model_input_size = model_input_size
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.max_boxes_num = max_boxes_num
        self.rgb888p_size = [ALIGN_UP(rgb888p_size[0], 16), rgb888p_size[1]]
        self.display_size = [ALIGN_UP(display_size[0], 16), display_size[1]]
        self.debug_mode = debug_mode
        # 预置颜色（ARGB）
        self.color_four = [(255, 220, 20, 60), (255, 119, 11, 32), (255, 0, 0, 142), (255, 0, 0, 230),
                           (255, 106, 0, 228), (255, 0, 60, 100), (255, 0, 80, 100), (255, 0, 0, 70),
                           (255, 0, 0, 192), (255, 250, 170, 30), (255, 100, 170, 30), (255, 220, 220, 0),
                           (255, 175, 116, 175), (255, 250, 0, 30), (255, 165, 42, 42), (255, 255, 77, 255),
                           (255, 0, 226, 252), (255, 182, 182, 255), (255, 0, 82, 0), (255, 120, 166, 157)]
        self.x_factor = float(self.rgb888p_size[0]) / self.model_input_size[0]
        self.y_factor = float(self.rgb888p_size[1]) / self.model_input_size[1]
        self.ai2d = Ai2d(debug_mode)
        self.ai2d.set_ai2d_dtype(nn.ai2d_format.NCHW_FMT, nn.ai2d_format.NCHW_FMT,
                                 np.uint8, np.uint8)

    def config_preprocess(self, input_image_size=None):
        with ScopedTiming("set preprocess config", self.debug_mode > 0):
            ai2d_input_size = input_image_size if input_image_size else self.rgb888p_size
            self.ai2d.resize(nn.interp_method.tf_bilinear, nn.interp_mode.half_pixel)
            self.ai2d.build([1, 3, ai2d_input_size[1], ai2d_input_size[0]],
                            [1, 3, self.model_input_size[1], self.model_input_size[0]])

    def postprocess(self, results):
        with ScopedTiming("postprocess", self.debug_mode > 0):
            result = results[0]
            result = result.reshape((result.shape[0] * result.shape[1], result.shape[2]))
            output_data = result.transpose()
            boxes_ori = output_data[:, 0:4]
            scores_ori = output_data[:, 4:]
            confs_ori = np.max(scores_ori, axis=-1)
            inds_ori = np.argmax(scores_ori, axis=-1)
            boxes, scores, inds = [], [], []
            for i in range(len(boxes_ori)):
                if confs_ori[i] > self.confidence_threshold:
                    scores.append(confs_ori[i])
                    inds.append(inds_ori[i])
                    x, y, w, h = boxes_ori[i, 0], boxes_ori[i, 1], boxes_ori[i, 2], boxes_ori[i, 3]
                    left = int((x - 0.5 * w) * self.x_factor)
                    top = int((y - 0.5 * h) * self.y_factor)
                    right = int((x + 0.5 * w) * self.x_factor)
                    bottom = int((y + 0.5 * h) * self.y_factor)
                    boxes.append([left, top, right, bottom])
            if len(boxes) == 0:
                return []
            boxes = np.array(boxes)
            scores = np.array(scores)
            inds = np.array(inds)
            keep = self.nms(boxes, scores, self.nms_threshold)
            dets = np.concatenate((boxes, scores.reshape((len(boxes), 1)),
                                   inds.reshape((len(boxes), 1))), axis=1)
            dets_out = []
            for keep_i in keep:
                dets_out.append(dets[keep_i])
            dets_out = np.array(dets_out)
            dets_out = dets_out[:self.max_boxes_num, :]
            return dets_out

    def nms(self, boxes, scores, thresh):
        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = np.argsort(scores, axis=0)[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            new_x1, new_y1, new_x2, new_y2, new_areas = [], [], [], [], []
            for order_i in order:
                new_x1.append(x1[order_i]); new_x2.append(x2[order_i])
                new_y1.append(y1[order_i]); new_y2.append(y2[order_i])
                new_areas.append(areas[order_i])
            new_x1 = np.array(new_x1); new_x2 = np.array(new_x2)
            new_y1 = np.array(new_y1); new_y2 = np.array(new_y2)
            xx1 = np.maximum(x1[i], new_x1); yy1 = np.maximum(y1[i], new_y1)
            xx2 = np.minimum(x2[i], new_x2); yy2 = np.minimum(y2[i], new_y2)
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            new_areas = np.array(new_areas)
            ovr = inter / (areas[i] + new_areas - inter)
            new_order = []
            for ovr_i, ind in enumerate(ovr):
                if ind < thresh:
                    new_order.append(order[ovr_i])
            order = np.array(new_order, dtype=np.uint8)
        return keep

    def draw_result(self, pl, dets):
        with ScopedTiming("display_draw", self.debug_mode > 0):
            if dets:
                pl.osd_img.clear()
                for det in dets:
                    x1, y1, x2, y2 = map(lambda v: int(round(v, 0)), det[:4])
                    x = x1 * self.display_size[0] // self.rgb888p_size[0]
                    y = y1 * self.display_size[1] // self.rgb888p_size[1]
                    w = (x2 - x1) * self.display_size[0] // self.rgb888p_size[0]
                    h = (y2 - y1) * self.display_size[1] // self.rgb888p_size[1]
                    color = self.get_color(int(det[5]))
                    pl.osd_img.draw_rectangle(x, y, w, h, color=color, thickness=4)
                    pl.osd_img.draw_string_advanced(x, y - 50, 32,
                                                    " " + self.labels[int(det[5])] + " " +
                                                    str(round(det[4], 2)), color=color)
            else:
                pl.osd_img.clear()

    def get_color(self, x):
        return self.color_four[x % len(self.color_four)]


# ============================== 主程序 =======================================
if __name__ == "__main__":
    display_mode_map = {1: "hdmi", 2: "lcd", 3: "ide"}
    display_mode = display_mode_map.get(select_display, "ide")

    if display_mode == "hdmi":
        display_size = [1920, 1080]
        sensor_w, sensor_h = 1920, 1080
    elif display_mode == "lcd":
        display_size = [800, 480]
        sensor_w, sensor_h = 1280, 960
    else:
        display_size = [800, 480]
        sensor_w, sensor_h = 1280, 720

    # 显示初始化
    if select_display == 1:
        Display.init(Display.LT9611, width=display_size[0], height=display_size[1], to_ide=True)
    elif select_display == 2:
        Display.init(Display.ST7701, to_ide=True)
    else:
        Display.init(Display.VIRT, width=display_size[0], height=display_size[1],
                     fps=100, to_ide=True)

    pl = PipeLine(rgb888p_size=RGB888P_SIZE, display_size=display_size,
                  display_mode=display_mode)
    pl.create(Sensor(width=sensor_w, height=sensor_h))
    display_size = pl.get_display_size()

    ob_det = ObjectDetectionApp(KMODEL_PATH,
                                labels=LABELS,
                                model_input_size=MODEL_INPUT_SIZE,
                                max_boxes_num=MAX_BOXES,
                                confidence_threshold=CONF_THRESHOLD,
                                nms_threshold=NMS_THRESHOLD,
                                rgb888p_size=RGB888P_SIZE,
                                display_size=display_size,
                                debug_mode=0)
    ob_det.config_preprocess()

    clock = time.clock()
    try:
        while True:
            clock.tick()
            with ScopedTiming("total", 0):
                img = pl.get_frame()
                res = ob_det.run(img)
                ob_det.draw_result(pl, res)
                pl.show_image()
                gc.collect()
            print("FPS:", clock.fps())
    except KeyboardInterrupt:
        print("用户中断")
    finally:
        ob_det.deinit()
        pl.destroy()
        Display.deinit()
        print("程序结束")
