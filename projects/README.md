# projects — 开发项目目录

所有基于 K230 的开发项目都放在这里（AI 助手也在此开工）。

## 命名建议

```
projects/
├── 01-led-blink/            # 序号 + 简短英文名
├── 02-color-tracking/
├── 03-license-plate-rec/
└── ...
```

## 每个项目的标准结构

```
<项目名>/
├── main.py          # 板端主程序（脱机运行入口，就这个名字）
├── README.md        # 必填：功能 / 硬件要求 / 运行步骤 / 需拷贝到 SD 卡的资源
└── assets/          # （可选）模型、图片、音频等要拷到板子的文件
```

## README.md 模板

```markdown
# 项目名

## 功能
一句话说明 + 运行效果。

## 硬件要求
- [ ] 3.5 寸 LCD / HDMI / 无屏（IDE 虚拟显示）
- [ ] 摄像头
- [ ] 其它外设与接线（对照 references/01-hardware.md 的 40PIN 表）

## 运行步骤
1. 把 main.py 拖入 CanMV IDE → 连接 → 运行
2. （无屏幕时）确认脚本顶部 select_display = 3
3. 调试通过后：工具 → 保存当前打开的脚本为（main.py）到CanMV Cam

## 需要拷贝到板子的资源
| 文件 | 板端路径 |
|---|---|
| xxx.kmodel | /sdcard/examples/kmodel/ |
| ... | ... |

## 已知问题 / 备注
```

## 起步模板

从 `../skills/canmv-k230/templates/` 挑一个最接近的复制过来改：

| 模板 | 用途 |
|---|---|
| `tpl_basic_peripheral.py` | GPIO / 按键 / PWM / ADC |
| `tpl_camera_display.py` | 摄像头 + 显示（三模式） |
| `tpl_openmv_vision.py` | 颜色 / 二维码 / 形状识别 |
| `tpl_ai_vision.py` | AI 推理骨架（AIBase+PipeLine，人脸检测示例） |
| `tpl_yolov8_object_detect.py` | YOLOv8 物体检测（80 类，可直接跑） |
| `tpl_network_wifi.py` | WiFi + TCP/UDP/HTTP |
| `tpl_llm_dashscope.py` | 阿里云大模型调用 |
| `tpl_touch_ui.py` | 触摸按钮 + 画板 |
