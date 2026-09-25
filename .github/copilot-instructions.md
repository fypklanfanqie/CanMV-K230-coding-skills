# Copilot 指令 — K230 开发工作区

本工作区是 **CanMV K230（勘智 K230 / 幻尔 Hiwonder K230）开发板 MicroPython 开发工作区**。

## 先读的文档

1. `AGENTS.md` — 工作区总入口
2. `skills/canmv-k230/SKILL.md` — 主技能文件（工作流 / 代码骨架 / 导航表 / 高频坑）
3. `skills/canmv-k230/references/` — 13 篇深度参考（硬件、外设、视觉、AI、网络、大模型等）

## 代码规则

1. 生成的是 **MicroPython 单文件脚本**（运行在 K230 板子的 CanMV 固件上，非 CPython 桌面环境）。
2. **先抄再改**：参考资料包 `CanMV K230/` 中的 174 个官方例程 + 技能 references，
   不要臆造 API；示例结构（Sensor/Display/MediaManager 初始化顺序、AIBase+PipeLine 骨架）必须与官方一致。
3. 视觉/音频程序资源释放（finally 中，顺序固定）：
   `sensor.stop() → Display.deinit() → os.exitpoint(os.EXITPOINT_ENABLE_SLEEP) → time.sleep_ms(100) → MediaManager.deinit()`
4. 显示模式：`select_display` 1=HDMI(1920×1080) / 2=LCD(800×480) / 3=IDE虚拟显示。
5. 主循环内 `os.exitpoint()`；按需 `gc.collect()`；异常用 try/except/finally 包裹。
6. 配置项（WiFi、API Key、阈值、模型路径）集中放文件顶部并加中文注释。
7. 新项目放 `projects/<项目名>/`：`main.py` + `README.md`（功能/接线/运行步骤/资源清单）。
8. 关键 API 速查见 `skills/canmv-k230/references/04-machine-api.md`（外设）、
   `06-ai-vision.md`（AI）、`05-openmv-vision.md`（视觉）、`03-media.md`（多媒体）。
