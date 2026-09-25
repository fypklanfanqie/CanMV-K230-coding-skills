# 03 · 多媒体 API（Sensor / Display / Audio / Video）

> 来源：教程《3.多媒体课程》全文 + 例程源码（Sensor.py / Display.py / audio.py / Video_*.py / Lvgl.py）。
> 所有视觉程序的地基：**摄像头采集 → 图像处理 → 显示**，以及衍生出的音频与视频能力。

---

## 1. 摄像头（media.sensor）

### 1.1 标准初始化流程（背下来）

```python
import time, os
from media.sensor import *
from media.display import *
from media.media import *

sensor = Sensor()                       # 或 Sensor(width=W, height=H)
sensor.reset()                          # ① 必须最先调用
sensor.set_framesize(width=800, height=480)   # ② 分辨率
sensor.set_pixformat(Sensor.RGB565)     # ③ 像素格式
                                        # ④ 初始化显示（略）
MediaManager.init()                     # ⑤ 媒体缓冲初始化
sensor.run()                            # ⑥ 启动采集
```

### 1.2 常用方法

| 方法 | 说明 |
|---|---|
| `Sensor()` / `Sensor(width=, height=)` | 构造。不传参用默认配置 |
| `reset()` | 复位初始化（必须） |
| `set_framesize(width=, height=, chn=CAM_CHN_ID_x)` | 设置**指定通道**分辨率 |
| `set_pixformat(格式, chn=...)` | 设置**指定通道**像素格式 |
| `snapshot(chn=CAM_CHN_ID_x)` | 抓一帧（返回 `image.Image`） |
| `run()` / `stop()` | 启动/停止采集 |
| `bind_info(x=, y=, chn=...)` | 取绑定信息，配合 `Display.bind_layer(**bind_info, layer=...)` 把摄像头画面**直通**显示层（零拷贝） |
| `set_hmirror(bool)` / `set_vflip(bool)` | 水平镜像 / 垂直翻转 |
| `width()` / `height()` | 当前分辨率 |

### 1.3 像素格式

| 格式常量 | 用途 |
|---|---|
| `Sensor.RGB565` | 彩色图像处理（最常用） |
| `Sensor.RGB888` / `Sensor.RGBP888`(`RGB888P`) | 三通道分离格式，**AI 模型预处理常用**（RGBP888 = Planar） |
| `Sensor.GRAYSCALE` | 灰度（边缘检测、找线更快更省内存） |
| `Sensor.YUV420SP` | 视频编码/直通显示（配合 `PIXEL_FORMAT_YUV_SEMIPLANAR_420`） |

### 1.4 多通道输出（一枚摄像头同时出 3 路流）

```python
sensor = Sensor()
sensor.reset()
sensor.set_framesize(Sensor.FHD)                  # 通道0：1920x1080
sensor.set_pixformat(Sensor.YUV420SP)
bind_info = sensor.bind_info()
Display.bind_layer(**bind_info, layer=Display.LAYER_VIDEO1)   # 通道0直通显示

sensor.set_framesize(width=640, height=480, chn=CAM_CHN_ID_1)  # 通道1：640x480
sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_1)

sensor.set_framesize(width=640, height=480, chn=CAM_CHN_ID_2)  # 通道2：640x480
sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_2)

Display.init(Display.LT9611, to_ide=True, osd_num=2)
MediaManager.init(); sensor.run()

while True:
    os.exitpoint()
    img = sensor.snapshot(chn=CAM_CHN_ID_1)
    Display.show_image(img, alpha=128)                             # OSD0 半透明叠加
    img = sensor.snapshot(chn=CAM_CHN_ID_2)
    Display.show_image(img, x=1920-640, layer=Display.LAYER_OSD1)  # 右下角小窗
```
> AI 例程套路：通道 0 大分辨率直通显示，通道 2（`rgb888p_size`）给 AI 推理。

### 1.5 关键常量
- 通道：`CAM_CHN_ID_0` / `CAM_CHN_ID_1` / `CAM_CHN_ID_2`
- 分辨率别名：`Sensor.FHD`(1920×1080) 等
- 在旧例程中见到的 `PIXEL_FORMAT_YUV_SEMIPLANAR_420` / `PIXEL_FORMAT_RGB_888_PLANAR` 为等价常量。

---

## 2. 显示（media.display）

### 2.1 初始化矩阵

```python
# HDMI（LT9611）
Display.init(Display.LT9611, width=1920, height=1080, to_ide=True)
# LCD（ST7701，800x480，参数可省）
Display.init(Display.ST7701, to_ide=True)
# IDE 虚拟显示（推荐无屏调试）
Display.init(Display.VIRT, width=1280, height=720, fps=100, to_ide=True)
```
- `to_ide=True`：把画面同时回传到 CanMV IDE 预览区。
- `osd_num=N`：需要叠加 OSD 图层时指定数量。

### 2.2 图层与显示

| 图层 | 说明 |
|---|---|
| `Display.LAYER_VIDEO1` | 视频直通层（`bind_layer` 绑定摄像头用） |
| `Display.LAYER_OSD0` / `LAYER_OSD1` / ... | 叠加层（画框、文字、小窗） |

```python
Display.show_image(img)                              # 显示一帧
Display.show_image(img, x=, y=)                      # 指定位置
Display.show_image(img, alpha=128)                   # 半透明
Display.show_image(img, layer=Display.LAYER_OSD1)    # 指定图层
Display.deinit()                                     # 释放（必须）
```

### 2.3 内存画布（image.Image，无需摄像头也能画）

```python
import image
img = image.Image(800, 480, image.RGB565)     # 或 image.ARGB8888（支持透明度）
img.clear()
img.draw_rectangle(0, 0, 800, 480, color=(255,255,255), fill=True)
img.draw_string_advanced(x, y, size, "文字", color=(255,255,255), scale=2)
Display.show_image(img)
```
> `draw_string_advanced(x, y, 字号, 文本, color=(r,g,b), scale=倍数)` 支持**中英文字符串**。

### 2.4 显示刷新机制
"内存中画好 → `Display.show_image()` 一次性推送"（双缓冲），避免画面撕裂。

---

## 3. 图像对象通用方法（image.Image 概览，详见 ref/05）

```python
img.width(); img.height(); img.format()
img.clear(); img.copy_from(other)
img.save("/sdcard/photo.jpg")            # 需 SD 卡；jpg/png 由扩展名决定
img.draw_rectangle / draw_line / draw_circle / draw_cross / draw_string_advanced ...
img.find_blobs / find_qrcodes / ...      # OpenMV 视觉 API
img.to_numpy_ref()                       # 转 numpy（AI 用，RGBP888 时）
```

---

## 4. 音频（media.pyaudio + media.wave）

> 需要 SD 卡（保存/读取 wav）；外放需 3.5mm 耳机口接音箱。

### 4.1 录音（保存 wav）

```python
from media.media import *
from media.pyaudio import *
import media.wave as wave

def record_audio(filename, duration):
    CHUNK = 44100 // 25       # 每块采样数
    FORMAT = paInt16          # 16bit（还支持 paInt24 / paInt32）
    CHANNELS = 2              # 1=单声道 2=立体声
    RATE = 44100

    p = PyAudio()
    p.initialize(CHUNK)
    MediaManager.init()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    stream.volume(vol=70, channel=LEFT)     # 输入增益
    stream.volume(vol=85, channel=RIGHT)
    stream.enable_audio3a(AUDIO_3A_ENABLE_ANS)   # 3A 降噪

    frames = []
    for i in range(0, int(RATE / CHUNK * duration)):
        frames.append(stream.read())
    wf = wave.open(filename, 'wb')
    wf.set_channels(CHANNELS)
    wf.set_sampwidth(p.get_sample_size(FORMAT))
    wf.set_framerate(RATE)
    wf.write_frames(b''.join(frames))
    wf.close()
    stream.stop_stream(); stream.close()
    p.terminate()
    MediaManager.deinit()
```

### 4.2 播放 wav

```python
def play_audio(filename):
    wf = wave.open(filename, 'rb')
    CHUNK = int(wf.get_framerate() / 25)
    p = PyAudio(); p.initialize(CHUNK); MediaManager.init()
    stream = p.open(format=p.get_format_from_width(wf.get_sampwidth()),
                    channels=wf.get_channels(), rate=wf.get_framerate(),
                    output=True, frames_per_buffer=CHUNK)
    stream.volume(vol=85)
    data = wf.read_frames(CHUNK)
    while data:
        stream.write(data)
        data = wf.read_frames(CHUNK)
    stream.stop_stream(); stream.close(); p.terminate()
    wf.close(); MediaManager.deinit()
```

### 4.3 回环（麦克风→喇叭）
输入流 `read()` 后直接 `output_stream.write(data)` 即可（KWS 例程就是这么循环的）。

### 4.4 要点
- `p.initialize(CHUNK)` 的 CHUNK 与 `frames_per_buffer` 保持一致；
- 结束时顺序：`stop_stream → close → p.terminate → MediaManager.deinit`；
- 关键词唤醒/语音识别例程都基于这套接口做**实时小片段**采集（CHUNK = 0.3s × 16000 等）。

---

## 5. 视频（media.mp4format + media.player）

### 5.1 录制 MP4（H.265 + G711U 音频）

```python
from media.mp4format import *
import os

width, height = 1280, 720
mp4_muxer = Mp4Container()
mp4_cfg = Mp4CfgStr(mp4_muxer.MP4_CONFIG_TYPE_MUXER)
if mp4_cfg.type == mp4_muxer.MP4_CONFIG_TYPE_MUXER:
    mp4_cfg.SetMuxerCfg("/sdcard/test.mp4", mp4_muxer.MP4_CODEC_ID_H265,
                        width, height, mp4_muxer.MP4_CODEC_ID_G711U)
mp4_muxer.Create(mp4_cfg)
mp4_muxer.Start()

frame_count = 0
while True:
    os.exitpoint()
    mp4_muxer.Process()          # 处理音视频数据并封装
    frame_count += 1
    if frame_count >= 200:       # 录 200 帧
        break
mp4_muxer.Stop()
mp4_muxer.Destroy()
```
> 录制内容来自**已启动的 Sensor 通道流**（需先按 §1 初始化 sensor）；分辨率为输出视频尺寸（例程 1280×720 或 640×480）。

### 5.2 播放 MP4

```python
from media.player import *

start_play = False
def player_event(event, data):
    global start_play
    if event == K_PLAYER_EVENT_EOF:     # 播放结束
        start_play = False

player = Player()
player.load("/sdcard/test.mp4")
player.set_event_callback(player_event)
player.start()
start_play = True
while start_play:
    time.sleep(0.1)
    os.exitpoint()
player.stop()
```
> 通常"录制"和"播放"是两个独立程序（先跑录制、再跑播放）；播放依赖已存在的 mp4 文件。

---

## 6. LVGL 图形界面（概览，细节见 ref/08）

LVGL 是在 LCD 上做**按钮/滑杆/动画/中文界面**的方案，要点：
- 初始化：`lv.init()` → `disp_create(w, h)` → `set_flush_cb(回调)` → `set_draw_buffers(双缓冲)`；
- 主循环：`time.sleep_ms(lv.task_handler())`；
- 资源（字体/图片）放 `/sdcard/examples/15-LVGL/data/`，字体用 `lv.font_load("A:" + 路径)` 加载；
- 刷新回调里用 `Display.show_image(buf)` 推送，`flush_ready()` 通知 LVGL；
- LVGL + 触摸需要把 `TOUCH(0).read()` 的事件喂给 LVGL 的 indev（进阶，先参考官方例程）。

---

## 7. 最小可用组合（agent 常写的三种程序）

| 目标 | 组合 | 模板 |
|---|---|---|
| 纯显示/界面 | Display + image.Image 画布 | `templates/tpl_camera_display.py` |
| 摄像头 + 处理 | Sensor + Display + image | `templates/tpl_openmv_vision.py` |
| AI 推理 | Sensor(通道2) + PipeLine + kmodel | `templates/tpl_ai_vision.py` |
