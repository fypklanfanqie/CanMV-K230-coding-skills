# -*- coding: utf-8 -*-
# =============================================================================
# K230 基础外设演示模板（GPIO / 按键 / 蜂鸣器 / ADC）
# 平台：CanMV K230 (Hiwonder) + CanMV IDE
# 用法：整段拖入 CanMV IDE → 连接板子 → 运行
# 硬件：无需外接，使用板载 LED(GPIO52)、按键(GPIO21)、蜂鸣器(GPIO43/PWM1)
# =============================================================================
import time
from machine import Pin, PWM, ADC, FPIOA

# ------------------------------ 配置区 ---------------------------------------
LED_PIN   = 52          # 板载蓝色 LED，高电平点亮
KEY_PIN   = 21          # 板载按键，按下为低电平
BEEP_PIN  = 43          # 蜂鸣器（复用 PWM1）
ADC_CH    = 0           # ADC 通道 0（外接信号时用 40PIN 的 32 脚）
LOOP_MS   = 10          # 主循环间隔
# -----------------------------------------------------------------------------

fpioa = FPIOA()

# LED
fpioa.set_function(LED_PIN, FPIOA.GPIO52)
led = Pin(LED_PIN, Pin.OUT)

# 按键（内部上拉）
fpioa.set_function(KEY_PIN, FPIOA.GPIO21)
key = Pin(KEY_PIN, Pin.IN, Pin.PULL_UP)

# 蜂鸣器（PWM1）
fpioa.set_function(BEEP_PIN, FPIOA.PWM1)
beep = PWM(1)
beep.duty(0)                       # 先关

# ADC
adc = ADC(ADC_CH)

led_state = 0
last_key = 1
beep_countdown = 0

print("基础外设演示：按 KEY 切换 LED，同时蜂鸣器短鸣一声")
print("ADC 值每秒打印一次")

tick = 0
while True:
    # ---- 按键检测（带去抖）----
    k = key.value()
    if last_key == 1 and k == 0:                 # 下降沿：按下
        led_state = 0 if led_state else 1
        led.value(led_state)
        beep.freq(1000)
        beep.duty(50)
        beep_countdown = 5                        # 蜂鸣 5*10ms
        print("按键按下 -> LED", "亮" if led_state else "灭")
    last_key = k

    # ---- 蜂鸣器计时关闭 ----
    if beep_countdown > 0:
        beep_countdown -= 1
        if beep_countdown == 0:
            beep.duty(0)

    # ---- 每秒打印 ADC ----
    tick += 1
    if tick * LOOP_MS >= 1000:
        tick = 0
        raw = adc.read_u16()                      # 0-4095
        # 通道0/1 量程 0-3.6V；通道2/3 为 0-1.8V，按实际修改
        voltage = raw / 4095 * 3.6
        print("ADC%d raw=%d  voltage=%.3fV" % (ADC_CH, raw, voltage))

    time.sleep_ms(LOOP_MS)
