# 01 · 硬件规格与引脚（K230 / Hiwonder K230 开发板）

> 来源：官方 PDF《快速使用》《原理图 SCH_K230_DK-board V1.0》《引脚图定义.png》+ 基础课程文档。
> 本文件是硬件事实的唯一依据；接线类问题先查这里。

---

## 1. 主控芯片 K230（勘智 / Canaan）

| 项目 | 规格 |
|---|---|
| CPU | 双核 RISC-V：CPU0（小核，800MHz）+ CPU1（大核，1.6GHz，运行 CanMV RTOS 与 AI 任务） |
| NPU | KPU（神经网络处理器），运行 `.kmodel` 模型；配套 runtime 为 `nncase_runtime` |
| 视频编解码 | 支持 H.264 / H.265 硬件编解码（录制 MP4、播放用） |
| 图形 | 2D/3D 图形引擎（AI 例程里的 `Ai2d` 预处理由它完成） |
| 摄像头输入 | 3 路 MIPI-CSI（3×2 lane 或 1×4 + 1×2 lane），最多 3 路摄像头 |
| 显示输出 | 1 路 MIPI-DSI（驱动 LCD；板上经 LT9611 转 HDMI） |
| 内存 | 外挂 LPDDR4（板卡有 1G / 2G 两个版本） |
| 封装 | BGA256，11×11mm |

**片内外设资源（编程相关）**

| 外设 | 数量/规格 | 说明 |
|---|---|---|
| UART | 5 组 | **UART0/UART3 被系统占用**，用户可用 UART1/2/4 |
| I2C | 5 组 | 标准 100k / 快速 400k / 高速 3.4M |
| SPI | 3 组 | 可配片选极性、可调时钟 |
| PWM | 2 模块 × 3 通道 | 同模块 3 通道共享频率，占空比独立；**通道 0/1/2 一组，3/4/5 一组** |
| ADC | 1 模块 6 通道 | 12bit（0–4095），采样率可达 1MHz；**通道 0/1 量程 0–3.6V，通道 2/3 量程 0–1.8V** |
| RTC | 1 | 可读写日期时间 |
| WDT | 2 | **只有 WDT(1) 可用**（CanMV 只跑 CPU1） |
| Timer | 6 | 最小周期 1us |
| FFT | 硬件 FFT | `machine.FFT` |
| 加密 | SHA256 / AES 硬件加速 | `uhashlib` / `ucryptolib` |
| GPIO | 64+ 个 | 通过 FPIOA 复用配置 |

---

## 2. 开发板外设一览（Hiwonder K230）

| 类别 | 配置 |
|---|---|
| 供电 | Type-C 5V（与调试口共用）；外接 DC 8–24V（板载 DCDC 降压，原理图标注），另有 40PIN 5V 输入/输出 |
| 调试 | Type-C（USB0）连 PC；另有 4PIN 调试串口座（CPU0 Debug：GND/RX0/TX0；CPU1 Debug：TX3/RX3/GND） |
| USB | 2 路 USB-A Host（USB1，可接 U 盘/键鼠/无线网卡）+ 1 路 Type-C（USB0） |
| 存储 | TF 卡槽（系统与用户数据） |
| 显示 | HDMI 接口（LT9611 转换）；3.5 寸 MIPI LCD 800×480（ST7701，带触摸）；另有 LCD FPC 座 |
| 摄像头 | CAM0 / CAM1 / CAM2 三路 MIPI-CSI FPC 座（2 路 22PIN + 1 路 24PIN） |
| 音频 | 板载麦克风（MIC_P/N）+ 3.5mm 耳机输出口 + 蜂鸣器（GPIO43/PWM1，SI2302 驱动） |
| 网络 | WiFi 模组 TL8189（SDIO 接口，2.4G，陶瓷天线 + IPEX 外接天线座） |
| 按键 | KEY（用户按键，GPIO21，按下低电平）、BOOT、RST |
| 指示灯 | 蓝色 LED（LED_GPIO52）+ 电源指示灯 |
| 扩展口 | 40PIN 排针（见 §4） |

### 摄像头接口（FPC）引脚参考（原理图整理）

```
CAM0/CAM1 (22PIN 排线):  SDA, SCL, MDN0, MDP0, MCN, MCP, MDN1, MDP1,
                          GND, ..., MCLK, PCLK, AVDD, DOVDD, DVDD, RESET, VSYNC, HREF, PWDN
CAM2 (24PIN):            含 CAM2_MCLK / CAM2_RST / I2C4
```
> 用户不需要手工接线（FPC 直插）；出问题优先检查排线方向和是否插紧。

---

## 3. GPIO 复用表（FPIOA，原理图整理）

> `fpioa.help()` 可打印全部当前映射；`fpioa.set_function(pin, FPIOA.功能名)` 切换。
> 下面列出各 GPIO 的可选功能（节选最常用），**斜体为板卡默认用途**。

### BANK0（GPIO2–13）
| GPIO | 可复用功能 |
|---|---|
| GPIO2 | JTAG_TCK / PULSE_CNTR0 / *排针* |
| GPIO3 | JTAG_TCK / PULSE_CNTR1 / UART1_TXD / *排针 UART1_TX* |
| GPIO4 | JTAG_TCK / PULSE_CNTR2 / UART1_RXD / *排针 UART1_RX* |
| GPIO5 | UART2_TXD / 排针 |
| GPIO6 | UART2_RXD / 排针 |
| GPIO7 | PWM2 / IIC4_SCL |
| GPIO8 | PWM3 / IIC4_SDA |
| GPIO9 | PWM4 / UART1_TXD / IIC1_SCL / *CAM0_GPIO9* |
| GPIO10 | 3D_CTRL / UART1_RXD / IIC1_SDA / *CAM0_GPIO10* |
| GPIO11 | UART2_TXD / IIC2_SCL / *排针 I2C2_SCL* |
| GPIO12 | UART2_RXD / IIC2_SDA / *排针 I2C2_SDA* |
| GPIO13 | M_CLK |

### BANK1（GPIO14–25）—— QSPI / PWM
| GPIO | 可复用功能 |
|---|---|
| GPIO14 | QSPI0_CS0（*SPI0_CS0 排针*） |
| GPIO15 | QSPI0_CLK（*SPI0_CLK 排针*） |
| GPIO16 | QSPI0_D0（*SPI0_MOSI 排针*） |
| GPIO17 | QSPI0_D1（*SPI0_MISO 排针*） |
| GPIO18–25 | QSPI1 系列 / PWM5(GPIO25) |

### BANK2（GPIO26–37）
| GPIO | 可复用功能 |
|---|---|
| GPIO26 | MMC1_CLK / PDM_CLK / *排针* |
| GPIO27–31 | MMC1 数据 / UART3（勿用，系统占用） |
| GPIO32 | IIC0_SCL / IIS_CLK / UART3_TXD / *排针* |
| GPIO33 | IIC0_SDA / IIS_WS / UART3_RXD / *排针*（**触摸屏 I2C3 复用区**） |
| GPIO34 | IIC1_SCL / IIS_D_IN0 / *排针* |
| GPIO35 | IIC1_SDA / IIS_D_OUT0 / *排针* |
| GPIO36/37 | IIC3 / IIS（触摸屏 I2C3 相关） |

### BANK3（GPIO38–49）
| GPIO | 可复用功能 |
|---|---|
| GPIO38/39 | UART0_TXD/RXD（**系统占用**，CPU0 调试） |
| GPIO40/41 | UART1 / IIC1 |
| GPIO42 | UART1_RTS / **PWM0** |
| GPIO43 | UART1_CTS / **PWM1**（*蜂鸣器*）/ QSPI1_D3 |
| GPIO44/45 | UART2 / IIC3 / *CAM1_GPIO44/45* |
| GPIO46 | UART2_RTS / **PWM2** / IIC4_SCL |
| GPIO47 | UART2_CTS / **PWM3** / IIC4_SDA |
| GPIO48/49 | UART4 / IIC0 |

### BANK4（GPIO50–61）
| GPIO | 可复用功能 |
|---|---|
| GPIO50/51 | UART3 / IIC2（**系统/UART3 占用**） |
| GPIO52 | UART3_RTS / **PWM4** / IIC3_SCL / ***LED_GPIO52*** |
| GPIO53 | UART3_CTS / PWM5 / IIC3_SDA |
| GPIO54–59 | QSPI0 / MMC1 / PWM0-5（SPI1 复用区） |
| GPIO60 | **PWM0** / IIC0_SCL / QSPI0_CS2 / *排针 IO60* |
| GPIO61 | **PWM1** / IIC0_SDA / QSPI0_CS1 / *SPI0_CS1 排针* |

### BANK5（GPIO62/63）
| GPIO | 可复用功能 |
|---|---|
| GPIO62/63 | M_CLK2 / M_CLK3 / UART3_DE / UART3_RE |

> **注意**：这是芯片侧复用能力表；**实际板卡哪些引脚引到排针、排针脚位号请以 §4 为准**。

---

## 4. 40PIN 排针（板卡实际引出，优先使用此表）

| 脚位 | 功能 |  | 脚位 | 功能 |
|---|---|---|---|---|
| 1 | **3.3V** | | 2 | **5V** |
| 3 | I2C2_SDA (IO12) | | 4 | 5V |
| 5 | I2C2_SCL (IO11) | | 6 | GND |
| 7 | IO2 | | 8 | **UART1_TX (IO3)** |
| 9 | GND | | 10 | **UART1_RX (IO4)** |
| 11 | IO5 | | 12 | IO6 |
| 13 | **PWM0 (IO42)** | | 14 | GND |
| 15 | **PWM1 (IO43)** | | 16 | **PWM2 (IO46)** |
| 17 | 3.3V | | 18 | **PWM3 (IO47)** |
| 19 | **SPI0_MOSI (IO16)** | | 20 | GND |
| 21 | **SPI0_MISO (IO17)** | | 22 | IO18 |
| 23 | **SPI0_CLK (IO15)** | | 24 | **SPI0_CS0 (IO14)** |
| 25 | GND | | 26 | **SPI0_CS1 (IO61)** |
| 27 | IO19 | | 28 | IO60 |
| 29 | IO20 | | 30 | GND |
| 31 | IO32 | | 32 | **ADC0 (0–3.6V)** |
| 33 | IO33 | | 34 | GND |
| 35 | IO34 | | 36 | **ADC1 (0–3.6V)** |
| 37 | IO35 | | 38 | **ADC2 (0–1.8V)** |
| 39 | GND | | 40 | **ADC3 (0–1.8V)** |

**典型接线速查**
- 外接串口模块调试：模块 TX ↔ 排针 10(RX1)，模块 RX ↔ 排针 8(TX1)，GND 共地。
- I2C 传感器：SDA→3，SCL→5（I2C2）；供电 3.3V(1) 或 5V(2)。
- 舵机/电机 PWM 控制：PWM0–3（13/15/16/18 脚）。
- 模拟量采集：ADC0/1（32/36 脚，0–3.6V）；低压信号用 ADC2/3（38/40 脚，0–1.8V）。

---

## 5. 板载固定外设（写代码直接用，不需接线）

| 设备 | 引脚/接口 | 编程方式 | 例程 |
|---|---|---|---|
| 蓝色 LED | GPIO52，高电平点亮 | `Pin(52, Pin.OUT)` | `led.py` |
| 用户按键 KEY | GPIO21，按下=0 | `Pin(21, Pin.IN, Pin.PULL_UP)` | `asr.py`（Button(21)）、`object_detection.py` |
| 蜂鸣器 | GPIO43 → PWM1 | `FPIOA().set_function(43, FPIOA.PWM1); PWM(1)` | `PWM.py` |
| 触摸屏 | `TOUCH(0)`（I2C3） | `tp.read()` | `touch*.py` |
| 摄像头 | `Sensor()`（默认板载 CSI） | `Sensor/reset/set_framesize/...` | 多媒体/AI 全部例程 |
| LCD | `Display.ST7701`（800×480） | `Display.init(...)` | 全部例程 |
| HDMI | `Display.LT9611`（1920×1080） | `Display.init(...)` | 全部例程 |
| 麦克风/耳机 | `media.pyaudio` | `PyAudio()` | `audio.py`、`kws/asr/tts` |
| WiFi | `network.WLAN(STA_IF)` | 见 ref/07 | `WIFI.py` |
| ADC | ADC0–3（排针） | `ADC(n).read_u16()` | `ADC.py` |

---

## 6. 电源与安全

- **Type-C 与 DC 可同时接**（原理图有 MT9700 电源切换/防倒灌设计），但建议只用其一。
- 排针 5V（2/4 脚）：既是**输出**（USB 供电时），也可作为**输入**（不接 USB 时由它供电）——带大负载（舵机）时建议外部 5V 供电并在排针输入。
- 3.3V 排针（1/17 脚）为板载 LDO 输出，**不要**接入外部电源。
- 摄像头/屏幕 FPC 排线**断电插拔**，注意金手指方向。
- 大电流外设（电机等）必须独立供电、共地，不要从板子取电。

---

## 7. 常见硬件疑问

**Q：摄像头到底接哪一路？**
套件出厂已把摄像头接好（通常 CAM2）。代码里 `Sensor()` 不传参即为默认摄像头；如需明确指定再研究 `Sensor(width=, height=)` 与 `CAM_CHN_ID_x`（多路同时用时才需要）。遇到"没图像"优先检查排线，而不是改代码。

**Q：要给板子配屏幕，买什么样的？（购买指南）**
1. **首选——幻尔官方 3.5 寸 MIPI 触摸屏**：ST7701 驱动 / 800×480 / 带电容触摸（I2C3）/ 31PIN FPC 排线。
   全套教程与例程均基于此屏，`select_display=2` 即插即用，触摸课程（画板/拍照）也依赖它。
   购买时可直接搜索"Hiwonder K230 3.5寸屏"，或向卖家确认：**适用于幻尔 K230 开发板、ST7701、800×480、带触摸**。
2. **替代——任意 HDMI 显示器/电视/便携屏**：走 HDMI 口（板载 LT9611 转换），无触摸；
   代码里把分辨率改成你显示器的实际分辨率（默认 1920×1080），否则可能跑死。
3. **不买屏也能开发**：`select_display = 3`（IDE 虚拟显示），画面直接回传到 CanMV IDE 预览区。
4. **不要买**：SPI 小屏（ILI9341/ST7789 等）、RGB 并口屏——接口与驱动均不匹配，本固件无对应支持。
5. **第三方 MIPI 屏（高风险，先看下面的核对清单）**：固件 `display_mode_map` 中出现过 `hx8399`
   （另一种 MIPI 驱动 IC，勘智 SDK 亦有 hx8399 驱动样例），但本资料没有任何 HX8399 例程；
   其他驱动 IC（ILI9881C、JD9365 等）本固件未验证。

### 第三方屏购买/适配核对清单（必须逐条确认）

**MIPI 屏能不能用 = 三个"对得上"，缺一不可：**

| 维度 | 要求 | 怎么确认 |
|---|---|---|
| ① 驱动 IC | **首选 ST7701**（本固件实测支持，800×480）；hx8399 次之（固件有映射但无例程）；其他 IC 不要碰 | 问卖家驱动 IC 型号；要求演示"在 CanMV K230 上点亮" |
| ② 排线接口 | **31PIN FPC**，引脚定义与板载 LCD 座一致（4 lane MIPI + 3.3V/5V + GND + LCD_EN/LCD_RST + 背光 + 触摸）；**排线方向不能插反** | 要卖家的 FPC 引脚定义表，对照本资料原理图 PDF 逐脚核对 |
| ③ 触摸（如需） | 触摸 IC 必须是固件支持型号（如 GT911/gt9xx 系列电容触摸，走 I2C3）；无触摸屏则只影响触摸例程 | 问触摸 IC 型号；确认触摸信号在同一根 31PIN 排线上 |

**买前必问卖家的 5 个问题：**
1. 驱动 IC 是什么？是否有 **CanMV K230（幻尔/01Studio 同款）适配**？能提供点亮 demo 吗？
2. 提供 FPC 引脚定义表（31PIN）——用来和原理图对照，防止插错烧屏/烧板。
3. 触摸 IC 型号是什么？（要触摸功能时必问）
4. 分辨率与接口 lane 数？（800×480 / MIPI DSI，最稳）
5. 背光供电要求？（部分屏需额外升压/限流，直接接 5V 可能烧背光）

**到货后 3 步验证：**
1. 断电插排线（注意方向）→ 上电，跑最小程序（纯色画布 + `Display.init(Display.ST7701, to_ide=True)`）；
2. 黑屏 → 查排线方向/座子是否压紧；花屏/颜色异常 → 初始化序列不匹配，找卖家要 K230 配置；
3. 触摸不灵 → 写 2 行测试 `TOUCH(0).read()` 并 `print`（见 ref/08），仍无响应则是触摸 IC 未被固件支持。

**风险提示：**
- 卖家说"就是个标准 MIPI 屏，插上就行"——**大概率点不亮**（MIPI 屏必须匹配初始化序列）。
- 让屏厂提供 K230 适配需要改固件（C 驱动）时，MicroPython 层面做不了，只能依赖屏厂/生态已有的适配。
- 优先选"已被 K230 生态验证过的屏"（01Studio、立创庐山派、正点原子等同规格屏），且仍要核对 FPC 定义。
- 优先买支持 7 天无理由的店铺，保留退路。
- 💡 如果只是要"能显示"，买个 **HDMI 便携显示器**是零适配方案（改分辨率即可）。

**Q：为什么 ADC 读数换算不对？**
注意量程：ADC0/1 是 0–3.6V，ADC2/3 是 0–1.8V；`read_u16()` 返回 0–4095 原始值，`read_uv()` 返回微伏（注意例程注释中 read_uv 的输出范围说明）。换算电压 = 4095 值 × 量程 ÷ 4095。

**Q：能不能外接 USB 摄像头？**
不支持（MIPI 摄像头专用）。USB Host 口用于 U 盘/键鼠/USB 网卡等。
