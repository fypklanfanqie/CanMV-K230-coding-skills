# CanMV-K230-coding-skills
写在前面已经获得店家同意，然后后面会不断更新

> 给 AI 编程助手用的 **CanMV K230（勘智 K230 / 幻尔 Hiwonder K230 开发板）开发技能包**
> —— 让 CodeBuddy / Claude Code / Cursor / Copilot / Cline / Windsurf 等任何 agent
> 都能"看懂"这块板子，按官方例程的方法论帮你写代码。

[![Skill](https://img.shields.io/badge/Agent%20Skills-canmv--k230-blue)](skills/canmv-k230/SKILL.md)
[![Docs](https://img.shields.io/badge/reference-13%20docs-green)](skills/canmv-k230/references/)
[![Templates](https://img.shields.io/badge/templates-8-orange)](skills/canmv-k230/templates/)

---

> ⚠️ **重要说明**
> 本仓库**不包含** K230 官方硬件资料包（教程 PDF、系统镜像、kmodel 模型、官方示例源码、
> CanMV IDE 等），这些资料的版权归**幻尔科技 / 勘智（Canaan）**所有。
> 使用本技能前请自备 K230 官方资料包，放到工作区 `CanMV K230/` 目录下即可
> （技能文档中所有 `CanMV K230/...` 路径均指你本地的资料包）。
> 教程原文的文本提取（`references/source-docs/`）仅供学习检索，版权归原作者所有。

---

## 这是什么

一套**"资料 + 技能"二合一**的 K230 开发工作区：

| 目录 | 说明 |
|---|---|
| `CanMV K230/` | 官方全套资料（教程 PDF + 174 个例程源码 + 镜像 + 53 个 AI 模型 + 工具） |
| `skills/canmv-k230/` | **AI 开发技能包**：主技能 + 13 篇深度文档 + 8 个代码模板 + 教程全文提取 |
| `projects/` | 你自己的开发项目（AI 助手会在这里开工） |
| `AGENTS.md` | 所有 AI 助手的入口说明（CodeBuddy/Claude/Cursor/Copilot/Cline/Windsurf 通用） |

## 快速开始

### 1. 板子到手第一步（人类操作）

1. 资料 `canmv-ide-windows-4.0.9.exe` 安装 CanMV IDE；
2. SD 卡格式化（SD Card Formatter）→ Rufus 烧录镜像
   `CanMV K230/3.芯片资料&镜像&AI模型文件/01 镜像/CanMV_K230_Hiwonder_..._v2.9.0.img`；
3. SD 卡插入开发板，Type-C 数据线连接电脑；
4. 打开 CanMV IDE → 左下角连接 → 拖入一个例程 → 运行。

> 教程：`CanMV K230/1.教程资料/1.快速使用/1.快速使用.pdf`（图文）或
> `skills/canmv-k230/references/02-workflow.md`（速查版）

### 2. 让 AI 助手帮你开发

直接把需求告诉 AI 助手（任何支持读文件的 agent），例如：

- "帮我做一个车牌识别，结果显示在 LCD 上"
- "帮我写一个 WiFi 连接 + TCP 上传识别结果的小程序"
- "帮我把这几张照片训练成模型并部署到 K230"

AI 助手会自动读取 `AGENTS.md` → 技能文档 → 找到最接近的官方例程改造。

### 3. （可选）安装技能到 AI 助手

项目内使用不需要安装。若想让技能在任何工作区都能被自动加载：

```bash
python skills/canmv-k230/scripts/install_skill.py          # 安装/同步到所有检测到的 agent
python skills/canmv-k230/scripts/install_skill.py --list   # 查看安装状态
```

> 已安装的位置：`~/.codebuddy/skills/canmv-k230`、`~/.claude/skills/canmv-k230`。
> 每次修改 `skills/canmv-k230/` 里的内容后，重新运行一次上面的命令即可同步。

## 技能包结构

```
skills/canmv-k230/
├── SKILL.md                # ★ 主技能：工作流 / 骨架 / 导航 / 高频坑
├── references/             # 13 篇深度参考
│   ├── 01-hardware.md      #   硬件 / 引脚 / 40PIN
│   ├── 02-workflow.md      #   烧录 / IDE / 运行 / 脱机
│   ├── 03-media.md         #   摄像头 / 显示 / 音频 / 视频
│   ├── 04-machine-api.md   #   GPIO/UART/I2C/SPI/PWM/ADC/…
│   ├── 05-openmv-vision.md #   颜色 / 码类 / 形状 / 巡线
│   ├── 06-ai-vision.md     #   ★ kmodel / AIBase / YOLO 全解
│   ├── 07-network.md       #   WiFi / TCP / UDP / HTTP
│   ├── 08-touch-lvgl.md    #   触摸 / LVGL 界面
│   ├── 09-ai-llm.md        #   语音唤醒/ASR/TTS/LLM/VLM
│   ├── 10-model-training.md#   训练（在线+本地）/ kmodel 转换部署
│   ├── 11-model-inventory.md # 53 个模型清单
│   ├── 12-example-index.md #   官方例程全量索引
│   ├── 13-troubleshooting.md # 排错 + 性能优化
│   └── source-docs/        #   全部教程 PDF 文本提取
├── templates/              # 8 个可运行模板（外设/视觉/AI/网络/大模型/触摸）
└── scripts/
    ├── install_skill.py    # 安装技能到各 agent
    └── extract_pdfs.py     # 重新提取教程 PDF 文本
```

## 硬件参数一句话版

K230 双核 RISC-V + KPU（AI 加速）· 板载 WiFi(2.4G) / 麦克风 / 蜂鸣器 / LED / 按键 ·
支持 HDMI + 3.5" 触摸 LCD + IDE 虚拟显示三模式 · 3 路 MIPI 摄像头接口 ·
40PIN 扩展（I2C/UART/SPI/PWM/ADC）· Type-C 供电调试一体。

---

*技能版本 v1.0 · 固件基准：CanMV_K230_Hiwonder（local nncase v2.9.0）*
