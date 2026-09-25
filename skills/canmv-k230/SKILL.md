---
name: canmv-k230
description: >
  CanMV K230（勘智 K230 / 幻尔 Hiwonder K230 开发板）嵌入式 AI 视觉开发全流程技能。
  覆盖：硬件规格与引脚、CanMV IDE 环境搭建与镜像烧录、MicroPython 基础外设编程
  （GPIO/UART/I2C/SPI/PWM/ADC/RTC/WDT/Timer/FFT/SHA256/AES/多线程/文件读写）、
  摄像头与显示（HDMI/LCD/IDE 三种显示模式）、OpenMV 机器视觉（颜色识别/二维码/条形码/
  DataMatrix/AprilTag/线段/矩形/圆形/边缘检测）、AI 视觉（KPU + kmodel + YOLOv8 检测/分割/
  姿态/人脸/手势/车牌/OCR/目标追踪）、网络通信（WiFi/LAN/TCP/UDP/HTTP）、
  LCD 触摸与 LVGL 图形界面、阿里云百炼大模型（语音唤醒/语音识别/语音合成/文字理解/图片理解）、
  YOLOv8 在线与本地训练、ONNX→kmodel 转换（nncase）与模型部署。
  触发词：K230, CanMV, CanMV IDE, 勘智, 幻尔, Hiwonder, kmodel, nncase, KPU,
  K230开发板, 视觉识别, 摄像头例程, YOLOv8 部署, main.py 脱机运行, Sensor, Display,
  AIBase, PipeLine, Ai2d, aidemo, aicube, 人脸识别, 手势识别, 车牌识别, OCR, 目标追踪。
---

# CanMV K230 开发技能（主技能文件）

> **这是本工作区所有 K230 开发的入口文档。** 任何 agent 在动手写代码前，先读完本文件；
> 需要细节时，按本文件的"导航表"去读 `references/` 下的对应文档和配套资料包中的官方例程。

---

## 0. 如何使用本技能（给 agent 的元指令）

1. **先定位资料包**：本技能配套官方资料位于工作区根目录下 `CanMV K230/`。
   若当前工作区不是 `kaifaban`，请先搜索该目录（特征：含 `1.教程资料`、`5.程序源码`、`3.芯片资料&镜像&AI模型文件` 子目录）。
2. **永远"先抄再改"**：写任何功能前，先到 `references/12-example-index.md` 查有没有官方例程，找到后**读取该例程源码原文**，以它为基础修改。资料包里共有 **174 个官方 .py 例程**，覆盖几乎所有常用功能。不要凭空手写 API 调用。
3. **API 不确认就查**：`references/03` ~ `references/09` 是根据官方教程与全部例程源码整理的 API 参考。遇到文档中没有的 API，标注"未经验证"并给出替代方案，不要臆造。
4. **代码交付形态**：你写出的程序是 **MicroPython 单文件脚本**（跑在 K230 板子的 CanMV 固件上），用户会把它复制进 CanMV IDE 后在线运行、或保存为 `main.py` 脱机运行。你通常无法直接接触硬件，所以：
   - 代码必须能"复制即跑"：路径、引脚、参数都写默认可用值；
   - 关键配置集中放在文件顶部（`select_display`、WiFi 账号、模型路径等），方便用户改；
   - 每段核心逻辑配中文注释。
5. **新项目落盘位置**：约定放在工作区 `projects/<项目名>/`（见 §7）。每个项目至少包含 `main.py`（板端入口）+ `README.md`（接线/烧录/使用说明）。

---

## 1. 30 秒认识这块板子

| 项目 | 内容 |
|---|---|
| 主控 | 勘智 K230，双核 RISC-V（CPU0 小核 800MHz / CPU1 大核 1.6GHz），内置 KPU（神经网络加速）、VPU（H.264/H.265 编解码）、2D/3D 图形引擎 |
| 系统 | CanMV 固件（RTOS + MicroPython），**不是 Linux**；板子插 SD 卡启动，电脑上会出现 `CanMV` 盘符 |
| 内存/存储 | LPDDR4（1G/2G 版本）+ SD 卡（系统盘 `sdcard` + 用户盘 `data`） |
| 摄像头 | 3 路 MIPI-CSI（CAM0/CAM1/CAM2），套件一般接 1~2 路；`Sensor()` 默认通道即板载摄像头 |
| 显示 | ① HDMI（LT9611，默认 1920×1080）② 3.5 寸 MIPI LCD（ST7701，800×480，带触摸） ③ IDE 虚拟显示（不需要屏幕，直接在 CanMV IDE 里看画面）→ 由脚本顶部的 `select_display = 1/2/3` 切换 |
| 网络 | 板载 WiFi（TL8189，**仅 2.4G**）；有线需外接 USB 转网口（RTL8152B 免驱） |
| 音频 | 板载麦克风、3.5mm 耳机口（外放需自备音箱）、蜂鸣器（GPIO43/PWM1） |
| 交互 | 用户按键 KEY = **GPIO21**（低电平按下）、蓝色 LED = **GPIO52**、LCD 电容触摸（I2C3） |
| 扩展 | 40PIN 排针（3.3V/5V/GND、I2C2、UART1、SPI0、PWM0-3、I2S、ADC0-3 等，见 §4 引脚表） |
| 功耗/供电 | Type-C 5V 供电（同时是调试口）；也可 DC 输入（板载 DCDC，原理图标注 8–24V，实测常用 12V） |

### 显示模式（所有视觉程序的第一行配置）

```python
# ==================================================================
# == 选择显示模式 (1: HDMI, 2: LCD, 3: IDE虚拟显示) ==
# ==================================================================
select_display = 2   # 1=HDMI 1920x1080  2=LCD 800x480  3=IDE虚拟显示
```
- **没接屏幕时用 3**（IDE 虚拟显示）：画面回传到 CanMV IDE 右侧预览区，最省事。
- HDMI 默认 1920×1080，**分辨率不匹配会导致"跑死"**；LCD 固定 800×480。

---

## 2. 开发工作流（人 + agent 协作标准流程）

```
① 写代码（agent 在本工作区写 .py） 
      ↓
② 送进板子：把 .py 拖入 CanMV IDE 代码区（或复制到 CanMV/sdcard 盘符）
      ↓
③ 在线运行：CanMV IDE 连接板子 → 点运行（绿色三角）→ 看 IDE 终端 + 预览区
      ↓
④ 调试迭代：改代码 → 再运行；Ctrl+C 可打断死循环
      ↓
⑤ 脱机运行：CanMV IDE → 工具 → "保存当前打开的脚本为(main.py)到CanMV Cam"
      ↓
⑥ 上电即跑：重新上电后自动执行 main.py（不用连电脑）
```

### 关键操作细节
- **连接板子**：Type-C **数据线**（有些线只能充电！）接板子 → 打开 CanMV IDE → 左下角连接按钮（10 秒内连上，否则失败）。
- **在线运行**：程序不落盘，断电丢失。**脱机运行**：另存为 `main.py` 到板子。
- **REPL 终端**：PuTTY / 串口工具，波特率 **115200**；回车出 `>>>` 即进入交互；死循环卡住时按 **Ctrl+C**。
- **救砖**：如果保存的 `main.py` 是死循环且影响了启动，把 SD 卡插回电脑（或板子当 U 盘），删除 `CanMV/sdcard/main.py`。
- **文件路径映射**：板子内 `/sdcard` ↔ 电脑 `CanMV/sdcard`；板子内 `/data` ↔ 电脑 `CanMV/data`。模型、图片、音频等资源直接放进去。

### agent 写代码的强制约定（重要）
1. 文件顶部集中配置区：`select_display`、WiFi 账号密码、API Key、模型路径、阈值，全部用醒目注释块。
2. 视觉/AI/音频程序必须遵守**资源释放契约**（见 §5.3），否则第二次运行会挂。
3. 主循环里按需 `gc.collect()`；AI 程序建议每帧调用。
4. 打印信息用中文 + 关键数值（FPS、检测数量），方便用户在 IDE 终端看到效果。
5. 不确定的硬件接线，写进 README 并明确标出"需要用户确认"。

---

## 3. 导航表（想做什么 → 看哪里）

> 路径说明：`ref/` = 本技能 `references/` 目录；`资料/` = 工作区 `CanMV K230/` 目录。

| 我想做… | 首选参考 | 官方例程位置（资料/） |
|---|---|---|
| 认识板子、查引脚、接线 | `ref/01-hardware.md` | `3.芯片资料&镜像&AI模型文件/引脚图定义.png` |
| 装 IDE、烧镜像、连接、脱机运行 | `ref/02-workflow.md` | `1.教程资料/1.快速使用/` |
| 点灯、按键、GPIO、UART、I2C、SPI、PWM、ADC、RTC、看门狗、定时器 | `ref/04-machine-api.md` | `1.教程资料/2.基础课程/02 源码/`（15 个例程） |
| 摄像头采集 + 屏幕显示 + 音频 + 录像 | `ref/03-media.md` | `1.教程资料/3.多媒体课程/02 源码/` |
| 颜色识别、二维码、条形码、AprilTag、线段/矩形/圆检测、巡线 | `ref/05-openmv-vision.md` | `1.教程资料/4.OpenMV课程/02 源码/` |
| 人脸/人体/手势/车牌/OCR/YOLO 检测分割追踪 | `ref/06-ai-vision.md` | `1.教程资料/5.AI视觉课程/02 源码/`（30+ 例程，**重点**） |
| 连 WiFi、TCP/UDP/HTTP 通信 | `ref/07-network.md` | `1.教程资料/6.网络基础课程/02 源码/` |
| LCD 触摸、画板、LVGL 界面 | `ref/08-touch-lvgl.md` | `1.教程资料/7.触摸功能课程/02 源码/` |
| 语音唤醒/识别/合成、大模型对话、图片理解 | `ref/09-ai-llm.md` | `1.教程资料/8.AI大模型课程/02 源码/` |
| 训练自己的模型（在线/本地）、转 kmodel、部署 | `ref/10-model-training.md` | `1.教程资料/9.在线模型训练/`、`10.本地模型训练（YOLOv8）/` |
| 查某个 kmodel 是干什么的 | `ref/11-model-inventory.md` | `3.芯片资料&镜像&AI模型文件/02 AI模型文件/` |
| 找一个功能对应的官方例程文件 | `ref/12-example-index.md` | `5.程序源码/`（96 个）+ 各课程源码 |
| 报错、跑不起来、屏幕不亮、连不上 | `ref/13-troubleshooting.md` | 各教程的 "Note" 段落 |
| 要一份能直接改的代码骨架 | `templates/`（本技能内） | — |
| 需要教程 PDF 原文 | `references/source-docs/`（本技能内，全部 PDF 已提取为 txt） | 原始 PDF 在各教程目录 |

---

## 4. 硬件速查（详见 `ref/01-hardware.md`）

### 4.1 常用片内资源与板载设备

| 资源 | 说明 | 例程中的用法 |
|---|---|---|
| 蓝色 LED | GPIO52，**高电平点亮** | `fpioa.set_function(52, FPIOA.GPIO52); Pin(52, Pin.OUT).value(1)` |
| 用户按键 KEY | GPIO21，按下为低电平，需上拉 | `Pin(21, Pin.IN, Pin.PULL_UP)`，`value()==0` 表示按下 |
| 蜂鸣器 | GPIO43 复用 PWM1 | `fpioa.set_function(43, FPIOA.PWM1); PWM(1).freq(200); .duty(50)` |
| 触摸屏 | `TOUCH(0)`，I2C3 总线 | `tp.read()` 返回触摸点列表 `(x, y, event)` |
| 摄像头 | `Sensor()` / `Sensor(width=, height=)`，支持 3 通道输出 | `sensor.reset() → set_framesize → set_pixformat → snapshot()` |
| ADC 通道 | ADC0-3 引出到 40PIN（ADC0/1 量程 0–3.6V，ADC2/3 量程 0–1.8V） | `ADC(0).read_u16()`（12bit，0–4095） |
| UART | 芯片共 5 组，**UART0/UART3 已被系统占用，可用 UART1/2/4** | UART1 例程用引脚 3(TX)/4(RX)，115200 |
| I2C | 5 组硬件模块 | 例程：`I2C(2, scl=11, sda=12, freq=40000)` |
| SPI | 3 组，支持片选极性和可调时钟 | `SPI(1, baudrate=5000000, polarity=0, phase=0, bits=8)` |
| PWM | 2 个模块 × 3 通道；**通道 0/1/2 共享频率，3/4/5 共享频率** | `PWM(1).freq(200).duty(50)` |
| Timer | 6 个，最小周期 1us；软定时器 `Timer(-1)` | `Timer(-1).init(freq=1, mode=Timer.PERIODIC, callback=fn)` |
| 看门狗 | 2 个；**CanMV 只用 CPU1（大核），所以只有 WDT(1) 可用** | `WDT(1, 3)` + `wdt.feed()` |
| 硬件加速 | FFT、SHA256、AES | `uhashlib.sha256()`、`ucryptolib.aes(key, 1, iv)`、`machine.FFT` |

### 4.2 40PIN 排针引脚表（原理图 + 引脚图整理）

| 左列 | | 右列 |
|---|---|---|
| 1: 3.3V | | 2: 5V |
| 3: I2C2_SDA (IO12) | | 4: 5V |
| 5: I2C2_SCL (IO11) | | 6: GND |
| 7: IO2 | | 8: UART1_TX (IO3) |
| 9: GND | | 10: UART1_RX (IO4) |
| 11: IO5 | | 12: IO6 |
| 13: PWM0 (IO42) | | 14: GND |
| 15: PWM1 (IO43) | | 16: PWM2 (IO46) |
| 17: 3.3V | | 18: PWM3 (IO47) |
| 19: SPI0_MOSI (IO16) | | 20: GND |
| 21: SPI0_MISO (IO17) | | 22: IO18 |
| 23: SPI0_CLK (IO15) | | 24: SPI0_CS0 (IO14) |
| 25: GND | | 26: SPI0_CS1 (IO61) |
| 27: IO19 | | 28: IO60 |
| 29: IO20 | | 30: GND |
| 31: IO32 | | 32: ADC0 (0–3.6V) |
| 33: IO33 | | 34: GND |
| 35: IO34 | | 36: ADC1 (0–3.6V) |
| 37: IO35 | | 38: ADC2 (0–1.8V) |
| 39: GND | | 40: ADC3 (0–1.8V) |

> 另有独立 4PIN 调试串口座（CPU0 Debug：GND/RX0/TX0；CPU1 Debug：TX3/RX3/GND）。

**GPIO 复用必读**：任何外设使用前，先看该引脚支持什么功能，再用 FPIOA 切换：
```python
from machine import FPIOA
fpioa = FPIOA()
fpioa.help()              # 打印所有引脚当前功能 —— 不确定时先打印看看
fpioa.help(43)            # 看 43 脚支持哪些功能
fpioa.set_function(43, FPIOA.PWM1)   # 把 43 脚切到 PWM1
```

---

## 5. 代码骨架速查（完整可运行版本见 `templates/`）

### 5.1 基础外设骨架（GPIO / 按键 / PWM / ADC 通用结构）

```python
import time
from machine import Pin, FPIOA

fpioa = FPIOA()
fpioa.set_function(52, FPIOA.GPIO52)          # LED
led = Pin(52, Pin.OUT)

fpioa.set_function(21, FPIOA.GPIO21)          # KEY
key = Pin(21, Pin.IN, Pin.PULL_UP)

while True:
    if key.value() == 0:                      # 按下
        led.value(1)
    else:
        led.value(0)
    time.sleep_ms(10)
```

### 5.2 摄像头 + 显示骨架（不含 AI，最常用）

```python
import time, os
from media.sensor import *
from media.display import *
from media.media import *

# select_display: 1=HDMI  2=LCD  3=IDE虚拟显示
select_display = 3

sensor = Sensor()
sensor.reset()
sensor.set_framesize(width=800, height=480)
sensor.set_pixformat(Sensor.RGB565)

if select_display == 1:
    Display.init(Display.LT9611, to_ide=True)
elif select_display == 2:
    Display.init(Display.ST7701, to_ide=True)
else:
    Display.init(Display.VIRT, width=800, height=480, fps=60, to_ide=True)

MediaManager.init()
sensor.run()
clock = time.clock()

try:
    while True:
        os.exitpoint()                       # 允许 IDE 停止按钮生效
        clock.tick()
        img = sensor.snapshot()
        img.draw_string_advanced(0, 0, 30, 'FPS: %.2f' % clock.fps(), color=(255, 255, 255))
        Display.show_image(img)
except KeyboardInterrupt:
    print("用户停止")
finally:
    sensor.stop()
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
```

### 5.3 资源释放契约（**所有视觉程序必须遵守**，顺序不能错）

```
sensor.stop()                        # 1. 停摄像头
Display.deinit()                     # 2. 释放显示
os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
time.sleep_ms(100)                   # 3. 等待硬件真正释放
MediaManager.deinit()                # 4. 释放媒体缓冲
```
放在 `finally:` 里；**少一步就会导致下一次运行黑屏/报错**。

### 5.4 OpenMV 视觉骨架（找色块示例）

```python
import time
from media.sensor import *
from media.display import *
from media.media import *

thresholds = [(0, 100, 29, 127, 3, 127)]     # LAB 阈值（红色），用 IDE 阈值编辑器调

sensor = Sensor(); sensor.reset()
sensor.set_framesize(width=800, height=480)
sensor.set_pixformat(Sensor.RGB565)
Display.init(Display.ST7701, to_ide=True)    # 按需切模式
MediaManager.init(); sensor.run()
clock = time.clock()

try:
    while True:
        img = sensor.snapshot()
        for b in img.find_blobs(thresholds):         # b: [x,y,w,h,pixels,cx,cy,...]
            img.draw_rectangle(b[0:4], thickness=2)
            img.draw_cross(b[5], b[6])
        Display.show_image(img)
except KeyboardInterrupt:
    pass
finally:
    sensor.stop(); Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP); time.sleep_ms(100)
    MediaManager.deinit()
```

> **调阈值不用猜**：CanMV IDE → 工具 → 机器视觉 → 阈值编辑器 → 选"帧缓冲区"，拖滑杆直到目标变白，复制数值。

### 5.5 AI 视觉骨架（AIBase + PipeLine 模式，所有 kmodel 例程都是这个结构）

```python
from libs.PipeLine import PipeLine
from libs.AIBase import AIBase
from libs.AI2D import Ai2d
from libs.Utils import *                     # ALIGN_UP, ScopedTiming, center_pad_param 等
import os, gc
import nncase_runtime as nn
import ulab.numpy as np
import image
import aidemo                                # 或 import aicube

class MyApp(AIBase):
    def __init__(self, kmodel_path, model_input_size,
                 rgb888p_size=[1280,720], display_size=[800,480], debug_mode=0):
        super().__init__(kmodel_path, model_input_size, rgb888p_size, debug_mode)
        self.model_input_size = model_input_size
        self.rgb888p_size = [ALIGN_UP(rgb888p_size[0],16), rgb888p_size[1]]
        self.display_size = [ALIGN_UP(display_size[0],16), display_size[1]]
        self.ai2d = Ai2d(debug_mode)
        self.ai2d.set_ai2d_dtype(nn.ai2d_format.NCHW_FMT, nn.ai2d_format.NCHW_FMT,
                                 np.uint8, np.uint8)

    def config_preprocess(self, input_image_size=None):
        with ScopedTiming("set preprocess config", 0):
            ai2d_input_size = input_image_size if input_image_size else self.rgb888p_size
            top, bottom, left, right, _ = center_pad_param(self.rgb888p_size, self.model_input_size)
            self.ai2d.pad([0,0,0,0, top, bottom, left, right], 0, [114,114,114])
            self.ai2d.resize(nn.interp_method.tf_bilinear, nn.interp_mode.half_pixel)
            self.ai2d.build([1,3,ai2d_input_size[1],ai2d_input_size[0]],
                            [1,3,self.model_input_size[1],self.model_input_size[0]])

    def postprocess(self, results):
        # TODO: 按模型输出结构解析（参考 ref/06-ai-vision.md 中对应模型的例程）
        return results

    def draw_result(self, pl, res):
        pl.osd_img.clear()
        # TODO: 用 pl.osd_img.draw_* 画框/文字（注意 ARGB 颜色 (255,r,g,b)）

if __name__ == "__main__":
    select_display = 2                                  # 1=HDMI 2=LCD 3=IDE
    display_mode_map = {1: "hdmi", 2: "lcd", 3: "ide"}
    display_mode = display_mode_map[select_display]
    display_size = [1920,1080] if select_display == 1 else ([800,480] if select_display == 2 else [1280,720])

    # 初始化显示（三种模式）
    if select_display == 1:
        Display.init(Display.LT9611, width=display_size[0], height=display_size[1], to_ide=True)
    elif select_display == 2:
        Display.init(Display.ST7701, to_ide=True)
    else:
        Display.init(Display.VIRT, width=display_size[0], height=display_size[1], fps=100, to_ide=True)

    rgb888p_size = [1280, 720]
    pl = PipeLine(rgb888p_size=rgb888p_size, display_mode=display_mode)
    pl.create()
    display_size = pl.get_display_size()

    app = MyApp("/sdcard/examples/kmodel/xxx.kmodel", model_input_size=[320,320],
                rgb888p_size=rgb888p_size, display_size=display_size)
    app.config_preprocess()

    try:
        while True:
            with ScopedTiming("total", 1):
                img = pl.get_frame()
                res = app.run(img)
                app.draw_result(pl, res)
                pl.show_image()
                gc.collect()
    except KeyboardInterrupt:
        print("用户中断")
    finally:
        app.deinit()
        pl.destroy()
        Display.deinit()
```

> 上例是最小结构。**每种模型的 `postprocess`/`draw_result` 都能在 `ref/06-ai-vision.md` 或对应官方例程里找到现成写法——务必对照抄。**

### 5.6 WiFi + 云服务骨架

```python
import network, time, ujson, usocket, ussl

def connect_wifi(ssid, pwd, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, pwd)
        t0 = time.time()
        while not wlan.isconnected():
            if time.time() - t0 > timeout:
                return False
            time.sleep(1)
    print("WiFi已连接:", wlan.ifconfig())
    return True
```
- 只能连 **2.4GHz** 热点。
- HTTPS 用 `ussl.wrap_socket(sock, server_hostname=host)`；**注意**：板载 ussl 是极简 TLS，连不上阿里云 DashScope 的 HTTPS 时走 PC 中转（见 `ref/09-ai-llm.md` §图片理解）。

---

## 6. 资料包地图（工作区 `CanMV K230/`）

```
CanMV K230/
├── 快速使用向导(必看).pdf            # 总览：资料结构与学习路线
├── 1.教程资料/                       # ★ 全部图文教程 + 配套源码
│   ├── 1.快速使用/                    #   烧镜像、装 IDE、连接、REPL、显示模式（含 led.py）
│   ├── 2.基础课程/                    #   15 个外设例程（FPIOA~文件读写）
│   ├── 3.多媒体课程/                  #   Sensor/Display/Audio/Video/LVGL（5 个）
│   ├── 4.OpenMV课程/                  #   颜色/码类/图像检测（13 个）
│   ├── 5.AI视觉课程/                  #   ★ AI 视觉 22 大类 30+ 例程
│   ├── 6.网络基础课程/                #   LAN/WiFi/TCP/UDP/HTTP（8 个）
│   ├── 7.触摸功能课程/                #   触摸检测/画板/拍照（3 个）
│   ├── 8.AI大模型课程/                #   唤醒/ASR/TTS/LLM/VLM（5 个）
│   ├── 9.在线模型训练/                #   勘智云平台训练 + 部署模板
│   └── 10.本地模型训练（YOLOv8）/      #   本地 YOLOv8 训练 + ONNX→kmodel + 部署
├── 2.软件工具/                        # CanMV IDE 4.0.9 / SD格式化 / Rufus / PuTTY / NetAssist
├── 3.芯片资料&镜像&AI模型文件/
│   ├── 01 镜像/                       #   CanMV_K230_Hiwonder_micropython_local_nncase_v2.9.0.img ★烧录用
│   ├── 02 AI模型文件/                 #   53 个 .kmodel（02 kmodel 46 个 + 01 ai_test 7 个）
│   └── 03 芯片资料/                   #   数据手册 + 开发板原理图 PDF
├── 4.拓展学习资料/                    # OpenCV3 编程入门
└── 5.程序源码/                        # 96 个独立示例源码（含(1)重复副本）
```

**板端文件系统（SD 卡）对应关系**：
```
/sdcard/examples/kmodel/     # 所有 kmodel 模型（例程默认路径）
/sdcard/examples/utils/      # anchors、字体、图片、db 等资源（如 prior_data_320.bin）
/sdcard/libs/                # PipeLine.py / AIBase.py / AI2D.py / Utils.py / YOLO.py（AI 例程依赖库，固件自带）
/sdcard/examples/            # 官方示例脚本目录
/sdcard/                     # 用户文件（音频、照片、模型部署包等）
```

---

## 7. 项目约定（本工作区）

用户后续开发全部放在本工作区。建议结构：

```
kaifaban/
├── AGENTS.md                     # 所有 agent 的入口（指向本技能）
├── skills/canmv-k230/            # ★ 本技能（资料、模板、脚本）
├── projects/                     # 所有自研项目
│   ├── 01-led-blink/
│   │   ├── main.py               # 板端主程序（脱机运行用这个名字）
│   │   ├── README.md             # 功能 + 接线 + 运行方法 + 依赖（模型/素材）
│   │   └── assets/               # (可选) 模型、图片等需拷到 SD 卡的文件
│   └── ...
└── CanMV K230/                   # 官方资料包（只读，不要修改）
```

**每个项目 README 必须写清**：① 功能描述 ② 硬件要求（是否需要 LCD/摄像头/外设接线）③ 运行步骤（IDE 在线 or 存 main.py）④ 需要拷贝到 SD 卡的资源及路径 ⑤ 已知问题。

---

## 8. 高频坑 Top 15（详见 `ref/13-troubleshooting.md`）

1. **显示模式选错**：没屏幕还用 `select_display=2` → 看不到画面；HDMI 分辨率与显示器不符 → 跑死。
2. **忘记资源释放** → 第二次运行黑屏。见 §5.3 契约。
3. **`Sensor()` 前少了 `reset()`**；`set_framesize/set_pixformat` 必须在 `run()` 之前。
4. **内存不足（MemoryError / 卡死）**：降低 `rgb888p_size`、模型换 320 甚至 224、每帧 `gc.collect()`、及时 `del` 大对象。
5. **UART0/UART3 不能用于用户串口**（系统占用）；用 UART1/2/4。
6. **PWM 频率耦合**：同一模块三个通道频率相同，占空比独立。
7. **WDT 只有 1 号能用**（CanMV 只跑 CPU1）。
8. **阈值是 LAB 不是 RGB**：用 IDE 阈值编辑器调，不要手填 RGB 数值。
9. **AI 例程找不到模型**：kmodel 必须在 `/sdcard/examples/kmodel/`，anchors 在 `utils/`；新版部署包路径在脚本顶部改。
10. **`nncase` 版本要与固件匹配**：本资料镜像是 **local nncase v2.9.0**；训练导出/转换时注意（见 `ref/10`）。
11. **TLS 不兼容**：K230 直连部分云服务（如 DashScope 某些接口）会握手失败 → 用 PC 中转（`ref/09` §6）。
12. **WiFi 只支持 2.4G**；5G 热点连不上不是板子坏了。
13. **触摸事件值**：先 `print(p)` 观察 `event` 字段实际值再写逻辑（不同固件版本可能不同）。
14. **`main.py` 死循环上不了手**：断电→SD 卡删 `sdcard/main.py`→重新插入。
15. **拍照/录像要 SD 卡**；无卡时 `img.save()`/`wave.open('wb')` 类操作会失败。

---

## 9. references 索引

| 文件 | 内容 |
|---|---|
| `ref/01-hardware.md` | 芯片/开发板规格、引脚复用表、40PIN、外设电路、电源 |
| `ref/02-workflow.md` | 镜像烧录、IDE 使用、在线/脱机运行、REPL、文件传输、目录映射 |
| `ref/03-media.md` | Sensor 多通道、Display 图层、Audio（PyAudio/wave）、Video（录制/播放）、LVGL 基础 |
| `ref/04-machine-api.md` | FPIOA/Pin/UART/I2C/SPI/PWM/ADC/RTC/WDT/Timer/FFT/uhashlib/ucryptolib/_thread/uos/time |
| `ref/05-openmv-vision.md` | image 模块全部 find_* API、blob 对象、draw_* API、LAB 阈值、巡线算法 |
| `ref/06-ai-vision.md` | KPU/nncase_runtime/AIBase/Ai2d/PipeLine/aidemo/aicube 全解 + 各模型后处理代码 |
| `ref/07-network.md` | WLAN/LAN、socket TCP/UDP 四种模式、HTTP client/server、与 PC 调试工具对接 |
| `ref/08-touch-lvgl.md` | TOUCH API、触摸画板/拍照、LVGL 集成（disp_create/flush 回调/字体） |
| `ref/09-ai-llm.md` | 百炼 API Key、语音唤醒、ASR、TTS(WebSocket)、LLM、VLM(中转方案) |
| `ref/10-model-training.md` | 在线训练平台流程、本地 YOLOv8 训练、pt→onnx→kmodel、部署脚本结构 |
| `ref/11-model-inventory.md` | 53 个 kmodel 的用途/输入尺寸/配套例程 |
| `ref/12-example-index.md` | 全部官方例程 → 文件路径索引（教程 ↔ 源码 ↔ 板端） |
| `ref/13-troubleshooting.md` | 故障速查表 + 性能优化清单 |
| `references/source-docs/` | 16 个教程 PDF 的全文提取（txt），深度检索用 |

---

## 10. 模板与脚本

| 文件 | 用途 |
|---|---|
| `templates/tpl_basic_peripheral.py` | 外设类（GPIO/按键/PWM/ADC/UART 演示） |
| `templates/tpl_camera_display.py` | 摄像头 + 显示（三模式）基础 |
| `templates/tpl_openmv_vision.py` | OpenMV 视觉（找色块/码/图形） |
| `templates/tpl_ai_vision.py` | AI 视觉（AIBase+PipeLine 完整骨架） |
| `templates/tpl_yolov8_object_detect.py` | YOLOv8 物体检测（自实现后处理版） |
| `templates/tpl_network_wifi.py` | WiFi + TCP/UDP/HTTP 通信 |
| `templates/tpl_llm_dashscope.py` | 阿里云百炼 LLM/ASR/TTS 调用 |
| `templates/tpl_touch_ui.py` | 触摸屏 UI 交互（按钮/滑杆/画板） |
| `scripts/install_skill.py` | 把本技能安装到各 agent（CodeBuddy/Claude/Cursor…）的 skills 目录 |
| `scripts/extract_pdfs.py` | 重新从资料包 PDF 提取全文（资料更新后重建 source-docs） |

---

*技能版本 v1.0 · 基于 Hiwonder K230 全套官方资料整理 · 固化硬件：CanMV_K230_Hiwonder 镜像（local nncase v2.9.0）*
