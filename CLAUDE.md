# CLAUDE.md

本工作区是 **CanMV K230（勘智 K230 / 幻尔 Hiwonder K230 开发板）MicroPython 开发工作区**。

## 首先阅读

1. `AGENTS.md` —— 工作区总入口与开发铁律
2. `skills/canmv-k230/SKILL.md` —— **主技能文件**（工作流 / 代码骨架 / 导航表 / 高频坑）
3. 按需深入 `skills/canmv-k230/references/`（13 篇深度参考）与 `templates/`（8 个代码模板）

## 核心约束（详情见 SKILL.md）

- 代码形态：跑在 K230 板子 CanMV 固件上的 **MicroPython 单文件脚本**
- **先抄再改**：先到 `references/12-example-index.md` 找官方例程（资料包 `CanMV K230/` 内共 174 个 .py），读源码再改
- 视觉/音频程序必须遵守资源释放契约（`sensor.stop → Display.deinit → exitpoint sleep → MediaManager.deinit`）
- 主循环要有 `os.exitpoint()` 和按需 `gc.collect()`
- 新项目放 `projects/<项目名>/`，含 `main.py` + `README.md`

## 技能安装（可选）

```bash
python skills/canmv-k230/scripts/install_skill.py --target claude
```
