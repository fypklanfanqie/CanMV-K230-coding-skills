# -*- coding: utf-8 -*-
"""
install_skill.py — 把 canmv-k230 技能安装到各 AI agent 的技能目录

支持的 agent（按各自官方规范）：
  codebuddy : ~/.codebuddy/skills/canmv-k230
  claude    : ~/.claude/skills/canmv-k230          (Claude Code)
  codex     : ~/.agents/skills/canmv-k230          (OpenAI Codex 官方用户级技能目录)
  repo      : <仓库根>/.agents/skills/canmv-k230    (Codex 项目级技能，clone 即用)

用法（在任意目录执行）：
  python install_skill.py                     # 安装到所有检测到的用户级目录
  python install_skill.py --target codex      # 只装到 Codex 用户目录
  python install_skill.py --target repo       # 同步到当前技能所在仓库的 .agents/skills（项目级）
  python install_skill.py --target codebuddy,claude,codex,repo
  python install_skill.py --list              # 只显示检测结果，不写文件
  python install_skill.py --uninstall         # 从用户级目录移除

关于 Codex：
  官方文档（developers.openai.com/codex/skills）规定技能从以下位置发现：
    仓库级: $CWD/.agents/skills、$REPO_ROOT/.agents/skills（向上扫描）
    用户级: $HOME/.agents/skills
    管理员: /etc/codex/skills
  触发方式: 隐式（description 语义匹配）或显式 `$canmv-k230` / `/skills` 选择。
  注意：.codex/ 目录用于存放 config.toml 等配置，不是技能目录。
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

# 用户级安装目标（各 agent 官方规范的 skills 目录）
TARGETS = {
    "codebuddy": HOME / ".codebuddy" / "skills",
    "claude": HOME / ".claude" / "skills",
    "codex": HOME / ".agents" / "skills",
}

IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".git", "*.tmp")


def find_workspace_skill():
    """确认技能源目录存在且完整"""
    skill_md = SKILL_ROOT / "SKILL.md"
    if not skill_md.exists():
        print("[错误] 未找到 %s，请在技能目录内运行本脚本" % skill_md)
        sys.exit(1)
    return SKILL_ROOT


def find_repo_root():
    """
    推断当前技能所在的仓库根目录：
    技能应位于 <repo>/skills/canmv-k230，此时仓库根 = SKILL_ROOT 的上两级。
    仅当该结构成立且仓库根存在时返回，否则 None。
    """
    if SKILL_ROOT.parent.name == "skills":
        repo_root = SKILL_ROOT.parent.parent
        if repo_root.exists():
            return repo_root
    return None


def sync_copy(src, dest):
    """覆盖式复制目录"""
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, ignore=IGNORE)


def do_install(targets, list_only=False, uninstall=False):
    src = find_workspace_skill()
    print("技能源目录: %s" % src)
    print("-" * 60)

    installed = 0
    for name in targets:
        # ---- 仓库内项目级镜像（Codex .agents/skills）----
        if name == "repo":
            repo_root = find_repo_root()
            if repo_root is None:
                print("[跳过] repo: 当前技能不在 <仓库>/skills/canmv-k230 结构中")
                continue
            dest = repo_root / ".agents" / "skills" / SKILL_NAME
            if list_only:
                mark = "已存在" if dest.exists() else "不存在"
                print("[repo] %s  (%s)" % (dest, mark))
                continue
            if uninstall:
                if dest.exists():
                    shutil.rmtree(dest)
                    print("[移除] %s" % dest)
                else:
                    print("[跳过] %s 不存在" % dest)
                continue
            sync_copy(src, dest)
            print("[同步] %s   <- Codex 项目级（clone 后在该仓库内直接可用）" % dest)
            installed += 1
            continue

        # ---- 用户级目录 ----
        base = TARGETS.get(name)
        if base is None:
            print("[跳过] 未知目标: %s（可选: %s,repo）" % (name, ",".join(TARGETS)))
            continue

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

        sync_copy(src, dest)
        print("[安装] %s" % dest)
        installed += 1

    if not list_only and not uninstall:
        print("-" * 60)
        if installed:
            print("完成：已处理 %d 个位置。" % installed)
            print("Codex 提示：隐式触发靠 SKILL.md 的 description；也可用 $canmv-k230 显式调用。")
            print("项目内使用无需安装（AGENTS.md + AGENTS.md 指向的技能目录已就绪）。")
        else:
            print("未处理任何位置（可用 --list 查看检测情况）。")


def main():
    parser = argparse.ArgumentParser(description="安装 canmv-k230 技能到各 agent 目录")
    parser.add_argument("--target", default="all",
                        help="目标，逗号分隔: codebuddy,claude,codex,repo 或 all（默认 all，不含 repo）")
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
