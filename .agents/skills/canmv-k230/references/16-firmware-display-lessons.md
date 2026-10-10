# 16 · 固件、启动链与显示排障经验

> 2026-10-10 更新。本文记录 K230 CanMV 项目中已经核对过的事实，以及明确标注的代码审查发现。
> 版本差异很大时，以板上 `revision.txt`、`os.uname()`、`sys.version` 和官方同版本源码为准。

## 1. 先建立可复现的固件基线

本项目使用厂商提供的 `k230_canmv_hiwonder` 镜像验证了 LCD：用户确认烧录后屏幕可以正常显示，之前的条纹现象消失。这个结果只证明该镜像和该板屏组合工作，不能证明旧镜像一定是硬件损坏、缓冲区未初始化或某个单独的 DSI 寄存器错误。

该镜像为 620 MiB，SHA256 为 `c530f3b89a3e01c88a1d7f42e4dbfdd57e0e66dfface4f27a695868238bb9be6`。板端版本为 `v1.5-legacy-f57cc2c`，2026-03-18 构建。测试日志只记录到至少 5 帧提交，约 7.4 秒停止且没有结束标记；用户的正常显示确认不能扩大为完整 30 秒或长期稳定性验收。

验证新镜像时记录了以下精确版本：

| 组件 | revision |
|---|---|
| SDK | `44b88b30f3c0dc418c146346e292e5ef7334a7c9` |
| CanMV | `f57cc2c426e92d21f96623116db4d5edec169b00` |
| MicroPython | `0295137e60c0de862c8ee72d81c88d9e57e3973b` |
| MPP | `a7cde9c66e3647d333cf4ecdb2f86e8db704142e` |
| RT-Smart | `e6dc5d30528168ebc55840e4b15aaf5383c5daeb` |
| RT-Smart libs | `f38b53083ea1518af468d871a079ca00f7703472` |
| U-Boot | `d4a377f8ca6c788ca98a0ca24a4d1f4d881914a4` |

记录版本时不要只看模型转换器或 nncase 标签；它们不是固件 API 版本。用户态扩展、内核和 `libvo` 的 enum/ioctl 结构必须按同一源码提交匹配，静态链接并不能修复 ABI 不匹配。

## 2. 启动链与镜像写入

- Fastboot 运行的是裸区里的 `rtapp`，把文件复制到 FAT 分区或覆盖 FAT 中的 `micropython` 不会替换正在运行的固件。
- 此厂商镜像采用 A/B 启动槽：TOC `0xE0000`、OTA 元数据 `0xF0000`；RTT A/B 分别从 10/60 MiB 开始，每槽 20 MiB；RTAPP A/B 从 30/80 MiB 开始，每槽 30 MiB；BIN FAT 从 110 MiB 开始、10 MiB，SDCARD FAT 从 120 MiB 开始、500 MiB。这些偏移只用于识别本例，写入时仍以实际解析为准。
- 解析实际 MBR、TOC、OTA 元数据和包头后再写入；不要复用针对旧单槽镜像的固定偏移脚本。
- 本例需要校验 K230 外层 SHA256、uImage 头/数据 CRC 和私有 gzip 方法字节 `0x09`。裸区搜不到明文 ELF/CanMV 字符串不能证明没有固件。缺少配置/文件时 `gen_image_rtapp.py` 可能生成 fake RTAPP；必须检查日志、解包并比对目标 ELF，不能只看打包命令成功。
- 精确厂商版的预载进程名为 `/bin/preload &`；不同树可能使用不同名字。
- 本例 CanMV 在 IDE 未附着、REPL 未中断时依次执行 `/sdcard/boot.py`、`/sdcard/main.py`。自动启动验收要断电重上电；所查版本中 `machine.reset()`/IDE 状态可能抑制 main 自动运行。改名为 `_boot.py` 不是通用自动启动配置方法。
- 本例读卡器的 SDCARD 卷根目录对应板内 `/sdcard`；盘符会变，USB 导出视图也可能不同。先确认挂载映射，不要盲目再创建嵌套的 `sdcard` 目录。

## 3. 条纹、滚动刷新与显示 API

### 3.1 先区分测试图案和真实故障

旧 DSI 测试曾使用 `VID_MODE_CFG | 0x01110000` 的 BER 模式；细条纹可能就是测试内容。确认发送的模式、完整初始化序列和显示时长后，再判断是否异常。

本项目的 27 MHz 时序尝试没有消除条纹，并出现肉眼可见的 CRT 式滚动刷新。这是该次参数测试的结果，不是对所有面板或所有 27 MHz 配置的普遍结论。频率、porch、PHY 或面板寄存器不要在没有官方匹配基线时随意改动。

接口返回成功、`FRAME_SUBMITTED` 或少量帧日志只表示 API 调用返回；它们不能替代实屏观察。失败或跳过的测试也不能拿上一帧来解释。应先用官方同版本例程和厂商镜像建立基线，再一次只改一个变量。

### 3.2 版本范围内的 Python API

厂商 `f57cc2c` 树采用 C 实现的 `media.display`：

```python
Display.init(Display.ST7701, width=800, height=480, to_ide=True)
```

该版本的 `show_image` 没有 `direct_show` 参数，旧 `mpp.vo`/`mpp.connector` Python 绑定也已移除。先查板上版本和官方例程，不能按“新/旧”二分猜 API。该版本 `MediaManager.init/deinit` 是 deprecated 的兼容空壳，显示资源由 `Display.deinit()` 管理；仍保留对应官方例程的清理调用，初始化失败也应清理已成功申请的资源。

`image.Image(width, height, format)` 必须提供格式。外部缓冲区包装还要核对构造函数、长度、宽度、像素格式和对象生命周期；普通堆内存不自动等于可供 VB/直通显示使用的缓冲区。ARGB8888 的 `get_pixel()` 返回 `None` 也不能单独证明像素未初始化。

背光 PWM 和 ioctl 也有版本差异。旧树里的手写 ioctl 不能直接复制到厂商镜像；先查精确源码和官方例程。

## 4. 触摸、ADC 和音频的边界

- 精确厂商触摸驱动返回点对象，使用 `point.x`、`point.y`、`point.event`；先查是否提供 `TOUCH.EVENT_NONE/UP/DOWN/MOVE` 和旋转常量，再写事件判断。不要把数字 1/2 固定解释成按下或拍照，也不要假设坐标无需旋转。
- CanMV `f57cc2c` 的 ADC `read_u16()` 源码返回 `drv_adc_read(channel) & 0xFFFF`；名字不保证返回值已经归一化到 0–65535。量程、分辨率和摇杆阈值要以精确固件和实测校准为准。
- 官方音频接口是 `media.pyaudio.PyAudio`；没有证据时不要臆造 `Audio(0)` 之类的构造器。音频流必须按官方顺序停止、关闭、终止并释放媒体资源。

## 5. 原生扩展审查时的高风险点

下列项目来自 mGBA/CanMV 原生扩展代码审查，属于“待修复/待上板验证”的发现，不是已经证明的运行时故障：

1. mGBA 默认 `color_t` 宽度与绑定按 16 位强转可能不一致；统一 `COLOR_16_BIT`/RGB565 或显式转换，并实测红、绿、蓝通道顺序。
2. 初始化 core config、core 初始化失败路径和 config/core 的释放必须分开处理。
3. `blip_read_samples(..., 512, 1)` 的步长参数会交错写入；用正确的目标布局并检查实际读取数，避免越界。
4. blip 输出率必须与 Python 端假设统一；静音时仍要消费缓冲，避免积压。
5. 存档优先使用 `savedataClone`/`savedataRestore`，检查尺寸、短读写和失败；快速存档大小应来自 `core->stateSize()`，不要固定写死 1 MiB。
6. ELF 能链接、map 文件存在或内置模块注册成功，都不能等同于板上游戏、输入、音频和存档已经可用。必须做实际导入、ROM 启动、帧、输入释放、音频和重启存档验收。

本轮编译曾停在 `gb/audio.c:625` 的 `lsb may be used uninitialized`（`-Werror`）。先读取对应函数和分支，决定实际修复或有依据的局部处理；不要照搬其他版本的全局警告豁免并称为构建通过。

同名 `.py` 与内置模块的优先级要查匹配版本的导入实现。验收实际模块 API，并在存在时查看 `__file__`；不要把“文件模块总遮蔽内置模块”当作通用事实，也不要部署历史 stub 来冒充 C 扩展。

## 6. 推荐排障顺序

1. 保存镜像 SHA256、`revision.txt`、`os.uname()`、`sys.version` 和实际 MBR/分区布局。
2. 用官方同版本 LCD 例程验证纯显示，记录初始化返回值、提交帧数、清理和实屏照片；不要先加入 GBA 或自定义面板命令。
3. 若画面异常，先确认是否 BER/测试图案、分辨率/像素格式/方向不匹配，再核对缓冲区生命周期和资源释放。
4. 只有基线稳定后才替换用户态扩展；保留已验证的厂商 RTT、显示驱动和启动链，并逐项验收内置模块、ROM、输入、音频和存档。

启动早期串口打印可能先于 USB 枚举。可将短日志用 `open/write/close` 及时落盘，记录版本、阶段、异常和失败档，避免只靠易丢失的 print。MicroPython 不应默认具有 CPython 的 `os.path`/`traceback`；按板上 API 用 `os.stat`、`sys.print_exception`。

## 7. 复核源码的入口

按第 1 节精确 revision 查以下路径；当前开发分支的同名文件不能代替这些版本：

| 检查内容 | 源码入口（相对组件仓库根目录） |
|---|---|
| 显示参数与清理 | CanMV `port/modules/modmedia.display.c`、`port/builtin_py/media/media.py` |
| 自动执行脚本 | CanMV `port/core/main.c` |
| 触摸、ADC | CanMV `port/machine/machine_touch.c`、`port/machine/machine_adc.c` |
| 图像/外部缓冲构造 | CanMV `port/omv/modules/py_image.c` |
| 面板序列与显示框架 | MPP `kernel/connector/src/st7701.c`、`userapps/src/connector/mpi_connector.c`、`userapps/src/framework/kd_display.c` |
| RTAPP 打包 | SDK `tools/gen_image_rtapp.py` |
