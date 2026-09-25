# AGENTS.md — K230 开发工作区总入口

> **本文件面向所有 AI 编程助手（CodeBuddy / Claude Code / Cursor / Copilot / Cline / Windsurf / Codex 等）。**
> 无论你是什么 agent，进入本工作区后请先读完本文件，再开始任何 K230 相关的工作。

---

## 1. 这个工作区是做什么的

这里是 **CanMV K230（勘智 K230 / 幻尔 Hiwonder K230 开发板）的 MicroPython 开发工作区**。
用户拿到了一套完整的 K230 官方学习资料，希望用 AI 辅助进行板卡开发
（视觉识别、AI 推理、外设控制、网络通信、大模型接入等）。

**你（agent）的角色**：根据用户需求，参考资料包中的 174 个官方例程与全套教程，
编写可在 K230 上直接运行的 MicroPython 程序，并指导用户完成上板、调试、脱机部署。

---

## 2. 你必须先读的技能文档（按顺序）

| 步骤 | 文件 | 作用 |
|---|---|---|
| ① | `skills/canmv-k230/SKILL.md` | **主技能文件**：工作流、代码骨架、导航表、高频坑 —— 必读 |
| ② | `skills/canmv-k230/references/` | 13 篇深度参考（硬件/环境/外设/视觉/AI/网络/触摸/大模型/训练/模型清单/例程索引/排错） |
| ③ | `skills/canmv-k230/templates/` | 8 个可直接复制修改的代码模板 |
| ④ | `skills/canmv-k230/references/source-docs/` | 全部教程 PDF 的文本提取（深度检索用） |

> 如果本工作区被移动到别处，以上路径均相对于本文件所在目录。

---

## 3. 资料包在哪里

官方资料位于 `CanMV K230/`（与 AGENTS.md 同级）：

```
CanMV K230/
├── 1.教程资料/          # 7 大课程 + 模型训练（含配套 .py 源码 78 个）
├── 2.软件工具/          # CanMV IDE 4.0.9、烧录/格式化/串口/网络调试工具
├── 3.芯片资料&镜像&AI模型文件/  # 系统镜像(.img)、53 个 .kmodel、原理图、引脚图
├── 4.拓展学习资料/      # OpenCV 书籍
└── 5.程序源码/          # 96 个独立示例源码
```

**板端关键路径**：模型 `/sdcard/examples/kmodel/`，AI 库 `/sdcard/libs/`，
资源 `/sdcard/examples/utils/`，脱机入口 `/sdcard/main.py`。

---

## 4. 铁律（违反会造成"看起来能用实际跑不起来"）

1. **先抄再改**：动手写代码前，先在 `references/12-example-index.md` 找最接近的官方例程，
   读原始源码，在此基础上改。**不要凭空手写 K230 API 调用**。
2. **API 以资料为准**：只在 `skills/canmv-k230/references/` 与官方例程中出现过的 API 可直接使用；
   不确定的 API 必须标注"未经验证"。
3. **资源释放契约**：视觉/音频程序必须以
   `sensor.stop() → Display.deinit() → os.exitpoint(EXITPOINT_ENABLE_SLEEP) → sleep_ms(100) → MediaManager.deinit()`
   收尾（放 finally），否则第二次运行必挂。
4. **主循环必须 `os.exitpoint()` + 按需 `gc.collect()`**。
5. **代码是 MicroPython 单文件脚本**：跑在 CanMV 固件上；配置项集中在文件顶部。
6. **交付物**：程序 + 中文注释 + 给用户的"三步操作指引"（拖入 IDE → 连接 → 运行/存 main.py）。

---

## 5. 开发约定的目录结构

```
kaifaban/
├── AGENTS.md                     # ← 本文件（所有 agent 的入口）
├── README.md                     # 人类视角的说明
├── skills/canmv-k230/            # ★ 技能包（技能 + 模板 + 脚本 + 教程原文）
├── projects/                     # ★ 所有开发项目放这里（agent 新建）
│   └── <项目名>/
│       ├── main.py               # 板端主程序（脱机运行入口）
│       ├── README.md             # 功能/接线/运行步骤/需拷贝到 SD 卡的资源
│       └── assets/               # 模型、图片、音频等资源
└── CanMV K230/                   # 官方资料包（只读，不修改）
```

**新建项目的标准动作**：
1. `projects/<项目名>/` 下创建 `main.py`（从 `skills/canmv-k230/templates/` 选最接近的模板开始）；
2. 写 `README.md`（含：功能、硬件要求、运行步骤、需要拷贝到板子的资源清单）；
3. 告诉用户如何运行（在线调试 → 存 main.py 脱机）。

---

## 6. 用户的典型操作路径（写指引时用这些原话）

- 在线运行：**把 main.py 拖进 CanMV IDE → 点左下角连接 → 点运行（绿三角）**
- 看输出：**CanMV IDE 右下角终端**（print 信息）、**右侧预览区**（IDE 虚拟显示画面）
- 脱机部署：**CanMV IDE 菜单：工具 → 保存当前打开的脚本为（main.py）到CanMV Cam**
- 传模型/素材：**把文件复制到电脑上的 `CanMV/sdcard/...` 盘符目录**
- 遇到问题时：先看 `skills/canmv-k230/references/13-troubleshooting.md`

---

## 7. 技能安装（可选，让本技能全局可用）

项目内使用**无需安装**（读本文件 + `skills/` 即可）。
若希望在任何工作区都能自动加载本技能：

```bash
python skills/canmv-k230/scripts/install_skill.py                    # 安装到所有用户级目录
python skills/canmv-k230/scripts/install_skill.py --target repo      # 同步到本仓库 .agents/skills（Codex 项目级）
python skills/canmv-k230/scripts/install_skill.py --list             # 查看检测情况
```

安装位置（各 agent 官方规范）：

| Agent | 用户级安装位置 |
|---|---|
| CodeBuddy | `~/.codebuddy/skills/canmv-k230` |
| Claude Code | `~/.claude/skills/canmv-k230` |
| OpenAI Codex | `~/.agents/skills/canmv-k230`（官方规范；`.codex/` 只放 config） |

**OpenAI Codex 说明**（依据官方文档 developers.openai.com/codex/skills）：
- 技能目录是 **`.agents/skills`**：仓库级 `$REPO_ROOT/.agents/skills`（本仓库已内置镜像，clone 即用）、
  用户级 `~/.agents/skills`；
- 隐式触发靠 `SKILL.md` 的 `description` 语义匹配；显式调用用 **`$canmv-k230`** 或 `/skills` 选择器；
- 技能名 `canmv-k230`；可选元数据在 `skills/canmv-k230/agents/openai.yaml`。

---

## 8. 各 agent 的兼容入口（本工作区已全部放置）

| Agent | 自动读取的文件 | 内容 |
|---|---|---|
| 通用（推荐） | `AGENTS.md` | 本文件 |
| Claude Code | `CLAUDE.md` | 指向 AGENTS.md + 技能 |
| **OpenAI Codex** | `AGENTS.md`（原生指令文件）+ `.agents/skills/canmv-k230/`（项目级技能，clone 即用）；用户级 `~/.agents/skills/` | 完整技能（SKILL.md 格式） |
| Cursor | `.cursor/rules/canmv-k230.mdc` | 技能摘要与索引 |
| GitHub Copilot | `.github/copilot-instructions.md` | 技能摘要与索引 |
| Cline / Roo Code | `.clinerules/canmv-k230.md` | 技能摘要与索引 |
| Windsurf | `.windsurfrules` | 技能摘要与索引 |
| CodeBuddy | `.codebuddy/skills/canmv-k230/`（安装后） | 完整技能 |

---

*本工作区由用户与 AI 协作维护。技能版本 v1.0，基于 Hiwonder K230 官方全套资料（CanMV 固件 local nncase v2.9.0）。*
