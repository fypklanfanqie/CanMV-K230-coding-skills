# -*- coding: utf-8 -*-
"""
extract_pdfs.py — 从 K230 资料包提取全部 PDF 教程为 txt（供 agent 深度检索）

用途：
  资料包里有 16 个 PDF 教程（基础课程、AI视觉、大模型等）。
  本脚本把它们逐页提取为纯文本，保存到 references/source-docs/。

依赖：
  pip install pymupdf

用法：
  # 默认：自动在工作区里找 "CanMV K230" 目录，输出到本技能 references/source-docs/
  python extract_pdfs.py

  # 指定资料包目录 / 输出目录
  python extract_pdfs.py --src "d:/ai/cc Programm/kaifaban/CanMV K230" --out ./references/source-docs
"""
import argparse
import os
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[错误] 需要 PyMuPDF：pip install pymupdf")
    sys.exit(1)

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = SKILL_ROOT / "references" / "source-docs"

# 输出文件名映射（资料包内相对路径 → 友好文件名），未命中则采用原文件名
NAME_MAP = {
    "快速使用向导(必看).pdf": "00-快速使用向导.txt",
    "1.快速使用.pdf": "01-快速使用.txt",
    "01 基础课程.pdf": "02-基础课程.txt",
    "01 多媒体课程.pdf": "03-多媒体课程.txt",
    "01 OpenMV课程.pdf": "04-OpenMV课程.txt",
    "01 AI视觉课程.pdf": "05-AI视觉课程.txt",
    "01 网络基础课程.pdf": "06-网络基础课程.txt",
    "01 触摸功能课程.pdf": "07-触摸功能课程.txt",
    "01 AI大模型课程.pdf": "08-AI大模型课程.txt",
    "01 在线模型训练.pdf": "09-在线模型训练.txt",
    "01 本地模型训练（YOLOv8）.pdf": "10-本地模型训练-YOLOv8.txt",
    "02 SCH_K230_DK-board V1.0.pdf": "11-原理图SCH_K230_DK.txt",
    "01 K230 Product Full Datasheet — K230 Linux+RT-Smart SDK.pdf": "12-芯片数据手册.txt",
}


def find_pdf_root(explicit=None):
    if explicit:
        return Path(explicit)
    # 从工作区里找资料包目录
    for base in [Path.cwd(), SKILL_ROOT.parent.parent]:
        cand = base / "CanMV K230"
        if cand.exists():
            return cand
    print("[错误] 未找到 'CanMV K230' 资料包目录，请用 --src 指定")
    sys.exit(1)


def extract(pdf_path, out_path):
    doc = fitz.open(pdf_path)
    n = doc.page_count
    parts = []
    for i, page in enumerate(doc):
        txt = page.get_text("text")
        parts.append("\n\n===== PAGE %d/%d =====\n\n" % (i + 1, n) + txt)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    doc.close()
    return n, len("".join(parts))


def main():
    parser = argparse.ArgumentParser(description="提取 K230 资料包 PDF 文本")
    parser.add_argument("--src", default=None, help="资料包根目录（含 CanMV K230）")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="输出目录")
    args = parser.parse_args()

    src = find_pdf_root(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(src.rglob("*.pdf"))
    # 跳过重复副本（(1) 后缀）和超大的 OpenCV 书籍
    pdfs = [p for p in pdfs if "(1)" not in p.name and "OpenCV" not in p.name]

    print("资料包: %s" % src)
    print("输出到: %s" % out)
    print("找到 %d 个 PDF" % len(pdfs))
    print("-" * 60)

    for p in pdfs:
        fname = NAME_MAP.get(p.name, p.name.replace(".pdf", "") + ".txt")
        out_path = out / fname
        try:
            n, chars = extract(p, out_path)
            print("[OK] %-40s %3d 页  %7d 字符" % (fname, n, chars))
        except Exception as e:
            print("[失败] %s: %s" % (p, e))

    print("-" * 60)
    print("完成。agent 可直接读取这些 txt 做全文检索。")


if __name__ == "__main__":
    main()
