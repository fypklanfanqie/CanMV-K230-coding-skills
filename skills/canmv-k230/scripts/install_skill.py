# -*- coding: utf-8 -*-
"""
install_skill.py — 把 canmv-k230 技能安装到各 AI agent 的全局技能目录

为什么需要：
  - CodeBuddy / Claude Code 等支持"用户级 skills 目录自动加载"；
  - 把本技能复制到这些目录后，**任意工作区**打开都能自动识别该技能；
  - 而项目内的 skills/ 目录 + AGENTS.md 则保证"不装也能用"（agent 手动读文件即可）。

用法（在任意目录执行）：
  python install_skill.py                 # 安装到所有检测到的 agent 目录
  python install_skill.py --target codebuddy
  python install_skill.py --target codebuddy,claude
  python install_skill.py --list          # 只显示检测结果，不写文件
  python install_skill.py --uninstall     # 从所有目录移除

安装位置：
  codebuddy : ~/.codebuddy/skills/canmv-k230       (Windows: C:/Users/<你>/.codebuddy/skills/)
  claude    : ~/.claude/skills/canmv-k230
  agents    : ~/.agents/skills/canmv-k230          (通用 AGENTS 风格目录，部分工具使用)
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

SKILL_NAME = "canmv-k230"
# 本脚本位于 <skill_root>/scripts/install_skill.py → skill_root = 上一级
SKILL_ROOT = Path(__file__).resolve().parent.parent

HOME = Path.home()

TARGETS = {
    "codebuddy": HOME / ".codebuddy" / "skills",
    "claude": HOME / ".claude" / "skills",
    "agents": HOME / ".agents" / "skills",
}

IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".git", "*.tmp")


def find_workspace_skill():
    """确认技能源目录存在且完整"""
    skill_md = SKILL_ROOT / "SKILL.md"
    if not skill_md.exists():
        print("[错误] 未找到 %s，请在技能目录内运行本脚本" % skill_md)
        sys.exit(1)
    return SKILL_ROOT


def do_install(targets, list_only=False, uninstall=False):
    src = find_workspace_skill()
    print("技能源目录: %s" % src)
    print("-" * 60)

    installed = 0
    for name in targets:
        base = TARGETS.get(name)
        if base is None:
            print("[跳过] 未知目标: %s" % name)
            continue

        parent_ok = base.parent.exists() or list_only
        dest = base / SKILL_NAME

        if list_only:
            mark = "已安装" if dest.exists() else "未安装"
            print("[%s] %s  (%s)" % (name, dest, mark))
            continue

        if uninstall:
            if dest.exists():
                shutil.rmtree(dest)
                print("[移除] %s" % dest)
            else:
                print("[跳过] %s 不存在" % dest)
            continue

        # 安装（覆盖式更新）
        base.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=IGNORE)
        print("[安装] %s" % dest)
        installed += 1

    if not list_only and not uninstall:
        print("-" * 60)
        if installed:
            print("完成：已安装 %d 个位置。重启 agent 会话后技能将自动加载。" % installed)
            print("提示：项目内使用无需安装（AGENTS.md + skills/ 已就绪）。")
        else:
            print("未安装任何位置（可用 --list 查看检测情况）。")


def main():
    parser = argparse.ArgumentParser(description="安装 canmv-k230 技能到各 agent 目录")
    parser.add_argument("--target", default="all",
                        help="安装目标，逗号分隔: codebuddy,claude,agents 或 all")
    parser.add_argument("--list", action="store_true", help="仅列出检测结果")
    parser.add_argument("--uninstall", action="store_true", help="从目标目录移除")
    args = parser.parse_args()

    if args.target == "all":
        targets = list(TARGETS.keys())
    else:
        targets = [t.strip() for t in args.target.split(",") if t.strip()]

    do_install(targets, list_only=args.list, uninstall=args.uninstall)


if __name__ == "__main__":
    main()
