# 13 · 故障排查与性能优化手册

> 汇总自官方教程的所有 Note 段落 + 例程实践。
> 使用方式：**按现象查表 → 按顺序排除 → 用最小复现程序验证**。

---

## 1. 连接与烧录

| 现象 | 排查步骤 |
|---|---|
| IDE 连接失败（超过 10s） | ① 换 **数据线**（充电线无数据芯，最常见原因）② 板子烧过其它固件 → 重烧官方镜像 ③ 换 USB 口（主板直出）④ 看设备管理器有无串口/USB 设备 |
| 电脑看不到 CanMV 盘符 | ① SD 卡插紧 ② 换读卡器重烧 ③ 换数据线 ④ 换电脑 USB 口 |
| Rufus 写入失败/镜像损坏 | 重新格式化 SD 卡（SD Card Formatter）后再写；校验 .img 文件完整 |
| 串口助手连不上 | 波特率必须 **115200**；确认 COM 号（拔插对比）；换 PuTTY/串口工具 |
| 板子上电无反应 | 检查 SD 卡（系统在卡里）；Type-C 供电是否足够（5V/2A）；电源灯亮否 |

---

## 2. 显示问题

| 现象 | 原因与处理 |
|---|---|
| 完全黑屏（LCD） | `select_display` 是否= 2；`Display.init(Display.ST7701, ...)` 是否正确；屏幕 FPC 插紧 |
| HDMI 无输出 / 开机跑死 | **分辨率不匹配**：`Display.init(Display.LT9611, width=1920, height=1080, ...)` 必须与显示器匹配；改小分辨率试试 |
| IDE 虚拟显示没画面 | `select_display=3` 且 `Display.init(Display.VIRT, ..., to_ide=True)`；连接是否在线 |
| 画面花屏/撕裂 | 分辨率对齐问题：宽用 `ALIGN_UP(w, 16)` |
| 第二次运行黑屏/报错 | **资源没释放**：按 SKILL §5.3 顺序（sensor.stop→Display.deinit→exitpoint sleep→MediaManager.deinit）；检查是否在 finally 中 |
| 图像颜色不对 | 像素格式不匹配（RGB565 vs RGB888 vs YUV）；AI 用 `RGBP888`，展示用 `RGB565` |
| 画面上下颠倒/镜像 | `sensor.set_hmirror(True)` / `sensor.set_vflip(True)` |

---

## 3. 摄像头

| 现象 | 处理 |
|---|---|
| `snapshot()` 报错/卡住 | 确认 `sensor.reset()` 在最前、`run()` 已调用；是否被第二个程序实例占用（复位板子） |
| 无图像但程序在跑 | FPC 排线方向/接触；断电重插；`sensor.snapshot()` 返回值检查 |
| 帧率极低 | 分辨率太高；RGB888 → RGB565；降 `set_framesize`；GRAYSCALE（视觉算法够用时） |
| 多通道配置报错 | 每个通道独立 `set_framesize/set_pixformat(chn=...)`；宽 16 字节对齐 |

---

## 4. 音频

| 现象 | 处理 |
|---|---|
| 录音全零/噪音 | `p.initialize(CHUNK)` 是否调用；`frames_per_buffer=CHUNK` 一致；麦克风被占用 |
| 播放没声音 | 外设需接 **3.5mm 耳机口**（板载无喇叭）；`output=True`；音量 `stream.volume(vol=85)` |
| 保存 wav 打不开 | 采样参数写入是否与录音一致（channels/sampwidth/rate） |
| 程序结束卡住 | stop_stream→close→terminate→MediaManager.deinit 顺序执行；异常时也要释放 |

---

## 5. 网络

| 现象 | 处理 |
|---|---|
| WiFi 连不上 | **只支持 2.4G**；SSID/密码核对（区分大小写）；超时改成 15s 并打印进度 |
| TCP/UDP 连不上 PC | 同一网段；PC 防火墙临时关闭；SERVER_IP 用 `ipconfig` 查准；端口一致（默认 8080） |
| `s.accept()` 卡死 | 正常（阻塞等待）；加超时或按键打断 |
| `OSError: [Errno 11]` | EAGAIN（数据暂未到达）：非阻塞模式下忽略继续读，例程这么处理的 |
| 端口占用 | `setsockopt(SO_REUSEADDR, 1)` |
| HTTPS 握手失败 | 板载 ussl 极简 TLS：不兼容该服务时用 **PC 中转**（ref/09 §6） |

---

## 6. AI / 模型

| 现象 | 处理 |
|---|---|
| 打开 kmodel 失败（Errno 2） | 模型不在 `/sdcard/examples/kmodel/`；检查文件名大小写 |
| 模型加载报格式错误 | nncase 版本不匹配（固件 local nncase v2.9.0）；重烧官方镜像或重转模型 |
| 检测框全错位 | `display_size` 必须取 `pl.get_display_size()`；坐标换算 `× display/rgb888p` |
| 输出 shape 不符 | print 输出的 shape，对照例程 reshape/transpose 顺序 |
| MemoryError / 跑一会崩 | 降 `rgb888p_size`（1280×720→640×360→320×320）；换小模型；每帧 `gc.collect()`；`nn.shrink_memory_pool()`；及时 `del` |
| FPS 太低 | 同上 + 减少后处理计算 + 只在需要时画图 |
| `ImportError: libs.PipeLine` | 固件不对（无 /sdcard/libs）→ 重烧官方镜像 |
| 级联模型第二级无结果 | 传参（检测框/关键点）格式不对；对照例程的 `config_preprocess(det)` |
| 阈值太松/太紧 | 调 `confidence_threshold` / `nms_threshold`（0.2~0.5 常用） |

---

## 7. 触摸 / LVGL

| 现象 | 处理 |
|---|---|
| 触摸无反应 | 屏幕是否带触摸（3.5 寸款）；`TOUCH(0)` 实例；`read()` 是否返回空 |
| 点击不灵敏/连击 | 加防抖（`ticks_diff > 300ms`） |
| 坐标偏移 | 触摸坐标是屏幕坐标（800×480），注意画布偏移（如减去 CANVAS_Y） |
| LVGL 白屏 | 资源文件缺失（字体/图片）→ 检查 `/sdcard/examples/15-LVGL/data/` |
| LVGL 卡顿 | 降低刷新需求；减少动画；确认双缓冲配置正确 |

---

## 8. 大模型

| 现象 | 处理 |
|---|---|
| 401/403 | API Key 错/未开通服务/额度耗尽 |
| TLS 握手失败 | 该接口不支持板端直连 → PC 中转（VLLM 方案） |
| 唤醒不触发 | 阈值高 → 降到 0.05；麦克风音量（`volume(vol=100)`）；环境噪音大 |
| WebSocket 无响应 | 握手头（Authorization: bearer xxx）、任务顺序（run→continue→finish）核对 |

---

## 9. 系统级 / 急救

| 场景 | 操作 |
|---|---|
| main.py 死循环，板子"变砖" | ① 上电瞬间连 PuTTY 按 Ctrl+C ② 或 SD 卡插电脑删 `sdcard/main.py` |
| 程序跑飞、REPL 无响应 | 按板载 RST 键；或将 SD 卡重烧 |
| 想看精细日志 | IDE 终端长期开启；关键路径加 `print`；异常处 `sys.print_exception(e)` |
| 断电后时间复位 | RTC 无电池，正常；联网后可用 NTP/手动 `rtc.init` |
| 发热严重 | 停止高负载程序；避免多模型并发；检查供电 |

---

## 10. 性能优化清单（AI 视觉）

```
□ rgb888p_size: 1280x720 → 640x360 → 320x320  （先砍这个，效果最明显）
□ kmodel: 640 → 320 → 224
□ 显示: HDMI 1920x1080 → LCD 800x480（或 IDE 虚拟）
□ 通道分工: 通道0 直通显示(bind_layer)，通道2 只给 AI
□ 每帧 gc.collect()；大对象 del；nn.shrink_memory_pool()
□ 只在有目标时绘制/处理（减少 OSD 与后处理开销）
□ 多模型按需触发（有脸才跑关键点）
□ debug_mode=0（关闭 ScopedTiming 打印）
□ 视觉算法优先 GRAYSCALE + 320x240（OpenMV 路线）
□ 用 time.clock().fps() 实测，不做无数据优化
```

---

## 11. 调试方法论（给 agent）

1. **最小复现**：怀疑哪块，就写 10 行只测那块（例：只点灯、只 snapshot 显示）。
2. **二分定位**：注释掉一半逻辑，看错误是否出现。
3. **打印一切**：路径存在性、shape、FPS、返回码、异常 `sys.print_exception`。
4. **对照例程**：同一个 API 在本技能 ref 的示例里怎么用 → 逐字对比。
5. **问用户要三样**：终端完整输出（含异常栈）、`select_display` 值、硬件连接情况（屏幕/摄像头/外设）。
