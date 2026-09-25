# Cline 规则 — K230 开发工作区

本工作区是 **CanMV K230（勘智 K230 / 幻尔 Hiwonder K230）开发板 MicroPython 开发工作区**。

## 必读

1. `AGENTS.md` — 工作区总入口
2. `skills/canmv-k230/SKILL.md` — **主技能**：工作流、代码骨架、导航表、高频坑 Top15
3. `skills/canmv-k230/references/12-example-index.md` — 官方例程全量索引（先找到再改）

## 硬性规则

1. **先抄再改**：资料包 `CanMV K230/` 有 174 个官方例程；写新功能前先读最接近的例程源码。
2. 输出 **MicroPython 单文件脚本**（K230 CanMV 固件运行环境），顶部集中配置。
3. 视觉/音频程序 finally 中固定顺序释放资源：
   `sensor.stop → Display.deinit → os.exitpoint(EXITPOINT_ENABLE_SLEEP) → sleep_ms(100) → MediaManager.deinit`
4. `select_display`：1=HDMI / 2=LCD(800×480) / 3=IDE 虚拟显示（无屏幕首选）。
5. 主循环加 `os.exitpoint()`；按需 `gc.collect()`。
6. 新项目：`projects/<项目名>/main.py` + `README.md`。
7. 交付给用户的指引：拖入 CanMV IDE → 连接 → 运行；调通后"工具 → 保存为 main.py 到 CanMV Cam"脱机。

## 参考文件地图

| 主题 | 文件 |
|---|---|
| 硬件/引脚 | `skills/canmv-k230/references/01-hardware.md` |
| 环境/烧录/运行 | `skills/canmv-k230/references/02-workflow.md` |
| 摄像头/显示/音频 | `skills/canmv-k230/references/03-media.md` |
| 外设 API（GPIO/UART/…） | `skills/canmv-k230/references/04-machine-api.md` |
| 传统视觉 | `skills/canmv-k230/references/05-openmv-vision.md` |
| AI 视觉（kmodel） | `skills/canmv-k230/references/06-ai-vision.md` |
| 网络 | `skills/canmv-k230/references/07-network.md` |
| 触摸/LVGL | `skills/canmv-k230/references/08-touch-lvgl.md` |
| 语音/大模型 | `skills/canmv-k230/references/09-ai-llm.md` |
| 训练/部署 | `skills/canmv-k230/references/10-model-training.md` |
| 模型清单 | `skills/canmv-k230/references/11-model-inventory.md` |
| 排错 | `skills/canmv-k230/references/13-troubleshooting.md` |
| 代码模板 | `skills/canmv-k230/templates/` |
