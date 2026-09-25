# 04 · 基础外设 API（machine 模块 + 系统工具）

> 来源：教程《2.基础课程》15 个实验 + 全部对应例程源码。
> 覆盖：FPIOA / Pin(GPIO) / UART / I2C / SPI / PWM / ADC / RTC / WDT / Timer / FFT / SHA256 / AES / 多线程 / 文件读写。

---

## 1. FPIOA（引脚复用配置器）

```python
from machine import FPIOA
fpioa = FPIOA()

fpioa.help()                          # 打印所有引脚当前功能
fpioa.help(0)                         # 打印引脚0的配置
fpioa.help(FPIOA.IIC0_SDA, func=True) # 查哪些引脚支持 IIC0_SDA

fpioa.set_function(0, FPIOA.GPIO0)                       # 引脚0 → GPIO0
fpioa.set_function(2, FPIOA.GPIO2, ie=1, oe=1, pu=0, pd=0, st=1, ds=7)
fpioa.set_function(43, FPIOA.PWM1)                       # 引脚43 → PWM1
fpioa.set_function(3, FPIOA.UART1_TXD, oe=1)             # 输出使能
fpioa.set_function(4, FPIOA.UART1_RXD, ie=1)             # 输入使能

fpioa.get_pin_num(FPIOA.UART0_TXD)    # 功能 → 引脚号
fpioa.get_pin_func(0)                 # 引脚 → 当前功能
```

**set_function 参数**：
| 参数 | 含义 |
|---|---|
| `ie` | 输入使能 |
| `oe` | 输出使能 |
| `pu` | 上拉 |
| `pd` | 下拉 |
| `st` | 初始电平 |
| `ds` | 驱动能力（0–7，7 最强） |

> **口诀**：外设（UART/I2C/SPI/PWM/I2S…）使用前**必须先 set_function** 把引脚切到对应功能。

---

## 2. GPIO（machine.Pin）

```python
from machine import Pin, FPIOA
fpioa = FPIOA()
fpioa.set_function(52, FPIOA.GPIO52)

led = Pin(52, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
led.value(1)      # 高电平
led.value(0)      # 低电平

key = Pin(21, Pin.IN, Pin.PULL_UP)   # 按键（板载 KEY=GPIO21）
if key.value() == 0:                 # 按下（低电平）
    ...
```

### 常量表
| 类型 | 常量 | 说明 |
|---|---|---|
| 模式 | `Pin.IN` / `Pin.OUT` | 输入 / 输出 |
| 上下拉 | `PULL_NONE` / `PULL_UP` / `PULL_DOWN` | 无 / 上拉 / 下拉 |
| 中断 | `IRQ_FALLING` `IRQ_RISING` `IRQ_LOW_LEVEL` `IRQ_HIGH_LEVEL` `IRQ_BOTH` | 下降沿/上升沿/低电平/高电平/双边沿 |

**构造函数**：`Pin(index, mode, pull=Pin.PULL_NONE, drive=7)`，index 范围 0–63。

---

## 3. UART

> **芯片共 5 组 UART，UART0/UART3 被系统占用**；用户可用 **UART1/2/4**。
> 板载排针：TX1 = 引脚 3，RX1 = 引脚 4（40PIN 8/10 脚）。

```python
from machine import UART, Pin, FPIOA
import time

fpioa = FPIOA()
fpioa.set_function(3, FPIOA.UART1_TXD, oe=1)
fpioa.set_function(4, FPIOA.UART1_RXD, ie=1)

uart = UART(UART.UART1, 115200)       # 默认 8N1
uart.write(b'hello\r\n')
data = uart.read(1)                   # 返回 bytes；无数据返回 None
if data == b'1':
    ...
uart.deinit()
```
- 通讯调试：配合 USB 转串口模块（TX↔RX 交叉 + 共地），PC 端用串口助手。
- 完整例程：`1.教程资料/2.基础课程/02 源码/2.3 UART实验/UART.py`（串口收 1/0 控制 LED）。

---

## 4. I2C

> 芯片集成 5 组硬件 I2C，支持 100k/400k/3.4M。引脚可 IOMUX 配置。

```python
from machine import I2C
i2c = I2C(2, scl=11, sda=12, freq=40000)   # 例程默认 100kHz；可 40000/400000
print(i2c.scan())                          # 扫描从机地址（十进制列表，如 [59]）
print([hex(d) for d in i2c.scan()])        # 十六进制显示

# 常规读写（I2C 设备的通用写法）
buf = bytearray(2)
i2c.readfrom_mem(0x3C, 0x00, buf)          # 读寄存器
i2c.writeto_mem(0x3C, 0x00, b'\x01')       # 写寄存器
i2c.readfrom(0x3C, 2)                      # 直接读
i2c.writeto(0x3C, b'\x01')                 # 直接写
```
> 触摸屏挂在 I2C3（系统内部使用）；外接传感器建议用排针 I2C2（SDA=IO12 / SCL=IO11 或按 ref/01 §3 复用）。

---

## 5. SPI

> 3 组硬件 SPI；例程演示 QSPI0（GPIO14–17）读 Flash ID。

```python
from machine import SPI, FPIOA
a = FPIOA()
a.set_function(14, a.QSPI0_CS0)
a.set_function(15, a.QSPI0_CLK)
a.set_function(16, a.QSPI0_D0)   # MOSI
a.set_function(17, a.QSPI0_D1)   # MISO

spi = SPI(1, baudrate=5000000, polarity=0, phase=0, bits=8)
spi.write(bytes([0x9F]))                       # 写
buf = bytearray(4)
spi.write_readinto(bytes([0x9F,0,0,0]), buf)   # 全双工读写
```
- 40PIN 上 SPI0：CLK=IO15(23脚) / MOSI=IO16(19脚) / MISO=IO17(21脚) / CS0=IO14(24脚) / CS1=IO61(26脚)。
- 标准 `SPI(id, baudrate, polarity, phase, bits)`；无自动 CS 时用 `Pin` 手动控制片选。

---

## 6. PWM

> 2 个模块 × 3 通道；**同模块三通道共享频率**（通道 0/1/2 一组、3/4/5 一组），占空比独立。

```python
from machine import Pin, PWM, FPIOA
import time

fpioa = FPIOA()
fpioa.set_function(43, FPIOA.PWM1)     # 板载蜂鸣器

Beep = PWM(1)          # 创建 PWM 通道 1
Beep.freq(200)         # 频率 Hz
Beep.duty(50)          # 占空比 0-100（百分比）
time.sleep(1)
Beep.duty(0)           # 关
```
- 也可 `PWM(1, 200, 50, enable=True)` 一步构造。
- 排针可用 PWM0(IO42,13脚) / PWM1(IO43,15脚) / PWM2(IO46,16脚) / PWM3(IO47,18脚)。

---

## 7. ADC

> 1 个模块 6 通道；12bit（0–4095）；**ADC0/1 量程 0–3.6V，ADC2/3 量程 0–1.8V**。

```python
from machine import ADC
adc = ADC(0)
val = adc.read_u16()        # 0-4095
uv = adc.read_uv()          # 微伏
voltage = val / 4095 * 3.6  # 通道0/1换算示例
```
- 排针：ADC0=32脚 / ADC1=36脚（0–3.6V）；ADC2=38脚 / ADC3=40脚（0–1.8V）。
- ⚠️ 超量程可能损坏芯片，测量前确认信号范围（>3.6V 需分压）。

---

## 8. RTC（实时时钟）

```python
from machine import RTC
rtc = RTC()
print(rtc.datetime())                    # (年, 月, 日, 星期, 时, 分, 秒, 微秒)
rtc.init((2024, 2, 28, 2, 23, 59, 0, 0)) # 设置时间（星期=第几个，2=周二）
```
- 返回值顺序注意：**第 4 位是星期**，不是时。

---

## 9. WDT（看门狗）

```python
from machine import WDT
import time
wdt = WDT(1, 3)          # id=1（唯一可用），3 秒超时
for i in range(3):
    time.sleep(1)
    wdt.feed()           # 喂狗，超时不喂 → 系统复位
while True:
    time.sleep(0.01)
```
- **只有 WDT(1) 可用**（CPU1/大核）。

---

## 10. Timer（定时器）

```python
from machine import Pin, Timer, FPIOA

fpioa = FPIOA(); fpioa.set_function(52, FPIOA.GPIO52)
LED = Pin(52, Pin.OUT)
led_state = False

def led_toggle(timer):
    global led_state
    led_state = not led_state
    LED.value(1 if led_state else 0)

tim = Timer(-1)          # -1 = 虚拟软件定时器
tim.init(freq=1, mode=Timer.PERIODIC, callback=led_toggle)   # 1Hz 周期
while True:
    pass
```
- 构造：`Timer(-1)` 软定时器；`init(freq=, mode=Timer.PERIODIC/ONE_SHOT, callback=)`。
- 硬件 Timer 共 6 个，最小周期 1us。

---

## 11. FFT（硬件傅里叶变换）

```python
from machine import FFT
import math
from ulab import numpy as np

PI = math.pi
rx = []
for i in range(64):
    rx.append(int(10*math.cos(2*PI*i/64) + 20*math.cos(2*2*PI*i/64) + 1000*math.cos(5*2*PI*i/64)))

data = np.array(rx, dtype=np.uint16)
fft1 = FFT(data, 64, 0x555)     # (数据, 点数, 偏移)
res = fft1.run()                # 复数结果
res = fft1.amplitude(res)       # 各频率点幅值
res = fft1.freq(64, 38400)      # (点数, 采样率) → 频率轴
```
- 用途：音频频谱分析、振动分析。

---

## 12. 加密（uhashlib / ucryptolib）

### SHA256
```python
import uhashlib
obj = uhashlib.sha256()
obj.update(b'hello')
obj.update(b'world')       # 支持多次 update
dgst = obj.digest()        # bytes 摘要
```

### AES（示例为 ECB 模式 = 1）
```python
import ucryptolib

def pad(data):
    n = 16 - (len(data) % 16)      # AES 需要 16 字节对齐
    return data + bytes([0]*n)

key = b'\xb5\x2c\x50\x5a\x37\xd7\x8e\xda\x5d\xd3\x4f\x20\xc2\x25\x40\xea'
iv  = b'\x51\x6c\x33\x92\x9d\xf5\xa3\x28\x4f\xf4\x63\xd7\x00\x00\x00\x00'
crypto = ucryptolib.aes(key, 1, iv)     # 模式 1 = ECB，iv 可传
ct = crypto.encrypt(pad(b'Hello'))
crypto_dec = ucryptolib.aes(key, 1, iv) # 解密要重新构造
pt = crypto_dec.decrypt(ct).rstrip(b'\x00')
```
> 硬件加速 SHA256/AES，适合通信加密/校验。

---

## 13. 多线程（_thread）

```python
import _thread
import time

def func(name):
    while True:
        print("hello {}".format(name))
        time.sleep(1)

_thread.start_new_thread(func, ("1",))   # 参数必须是元组！
_thread.start_new_thread(func, ("2",))
while True:
    time.sleep(0.01)                     # 主线程保活
```
> 用途：网络接收 + 界面/视觉并行。注意 MicroPython 无 GIL 保护细节，共享资源加简单锁或约定单一写入者。

---

## 14. 文件读写与目录（/sdcard）

```python
import uos

# 写 + 读（with 自动关闭）
with open('/sdcard/data_log.txt', 'w') as f:
    f.write('hello hiwonder')
with open('/sdcard/data_log.txt', 'r') as f:
    print(f.read())

# 目录操作
try:
    uos.listdir('/sdcard/photo')     # 存在性检查
except OSError:
    uos.mkdir('/sdcard/photo')       # 不存在则创建

# 二进制（保存图片/模型）
with open('/sdcard/x.bin', 'wb') as f:
    f.write(b'\x01\x02')
```
- 支持任意后缀：txt/json/csv/自定义。
- 大文件分块读写，避免一次性读入大文件占内存。

---

## 15. 时间与系统工具

```python
import time
time.sleep(1)              # 秒
time.sleep_ms(100)         # 毫秒
time.ticks_ms()            # 毫秒计数
time.ticks_diff(a, b)      # 安全求差
clock = time.clock()       # FPS 计时器
clock.tick(); clock.fps()

import os, sys, gc
os.exitpoint()                                    # 检查 IDE 停止请求（循环里必调）
os.exitpoint(os.EXITPOINT_ENABLE)                 # 程序入口启用
os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)           # 释放阶段
gc.collect()                                      # 手动垃圾回收
sys.print_exception(e)                            # 打印异常栈

import urandom
urandom.getrandbits(8)                            # 随机数
```

`os.exitpoint()` 的意义：让"IDE 停止按钮 / Ctrl+C"能在长循环中生效，**每个 while True 循环里都要调用**。

---

## 16. 外设例程对照表（`1.教程资料/2.基础课程/02 源码/`）

| 实验 | 文件 | 关键 API |
|---|---|---|
| 2.1 FPIOA | `2.1 FPIOA实验/FPIOA.py` | help / set_function / get_pin_num |
| 2.2 GPIO | `2.2 GPIO实验/GPIO.py` | Pin |
| 2.3 UART | `2.3 UART实验/UART.py` | UART + FPIOA |
| 2.4 I2C | `2.4 I2C实验/IIC.py` | I2C.scan |
| 2.5 SPI | `2.5 SPI实验/SPI.py` | SPI + QSPI0 复用 |
| 2.6 PWM | `2.6 PWM实验/PWM.py` | PWM 蜂鸣器 |
| 2.7 ADC | `2.7 ADC实验/ADC.py` | ADC.read_u16 / read_uv |
| 2.8 RTC | `2.8 RTC实验/RTC.py` | RTC.datetime / init |
| 2.9 WDT | `2.9 WDT实验/WDT.py` | WDT(1) + feed |
| 2.10 TIMER | `2.10 TIMER实验/TIMER.py` | Timer(-1) 回调 |
| 2.11 FFT | `2.11 FFT实验/FFT.py` | FFT + ulab.numpy |
| 2.12 SHA256 | `2.12 SHA256 加密实验/SHA256.py` | uhashlib |
| 2.13 AES | `2.13 AES 加密实验/AES_GCM.py` | ucryptolib |
| 2.14 多线程 | `2.14 多线程实验/thread.py` | _thread |
| 2.15 文件读写 | `2.15 文件读写/File_read_and_write.py` | open / uos |
