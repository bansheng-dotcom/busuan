# -*- coding: utf-8 -*-
"""把 natural-flow-ima 打包成腾讯 ima 可导入的 Skill ZIP。

ima Skills 硬性要求:
  - 仅 .zip，最大 10 MB，文件总数 <= 300
  - 只允许纯文本文件（.md/.txt/.json/.yaml/.csv/.py），不允许二进制
  - SKILL.md 必须位于 ZIP 根目录（不能嵌套在子文件夹）
"""
import os
import shutil
import zipfile

SRC = r"D:\cc\natural-flow-ima"      # 源 skill 目录
IMA_SKILL = r"D:\cc\_ima\ima_SKILL.md"  # ima 适配版 SKILL.md（稳定源）
PKG = r"D:\cc\_ima\skill-package"    # 暂存目录（脚本重建）
OUT = r"D:\cc\_ima\natural-flow-mikey.zip"

# 要带进 ima 的子目录（知识层），逐字复制
INCLUDE_DIRS = [
    "modules",
    "references",
    "decision_trees",
    "templates",
    "index",
]

# 不带的文件（Claude Code 专属路由 / 开发工件）
EXCLUDE_FILES = {
    "skill.yaml",       # 主路由表，ima 不执行，RAG 自动检索替代
    "README.md",
    "AUDIT.md",
    "CHANGELOG.md",
    "split_cases.py",
}

def main():
    if os.path.exists(PKG):
        shutil.rmtree(PKG)
    os.makedirs(PKG)

    # 1) 复制 ima 版 SKILL.md 到暂存目录根
    shutil.copy(IMA_SKILL, os.path.join(PKG, "SKILL.md"))
    print("[copy] SKILL.md (ima 版)")

    # 2) 复制知识层子目录
    for d in INCLUDE_DIRS:
        src_dir = os.path.join(SRC, d)
        dst_dir = os.path.join(PKG, d)
        if os.path.isdir(src_dir):
            shutil.copytree(src_dir, dst_dir)
            print(f"[copy] {d}/")

    # 3) 打包 ZIP（SKILL.md 在根目录）
    file_count = 0
    total_bytes = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        # SKILL.md 必须在根
        zf.write(os.path.join(PKG, "SKILL.md"), "SKILL.md")
        file_count += 1
        total_bytes += os.path.getsize(os.path.join(PKG, "SKILL.md"))

        for root, dirs, files in os.walk(PKG):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f == "SKILL.md":
                    continue
                full = os.path.join(root, f)
                rel = os.path.relpath(full, PKG)
                zf.write(full, rel)
                file_count += 1
                total_bytes += os.path.getsize(full)

    size_mb = total_bytes / 1024 / 1024
    print(f"\n[ok] {OUT}")
    print(f"     文件数: {file_count} / 300")
    print(f"     大小:   {size_mb:.2f} MB / 10 MB")
    assert file_count <= 300, "文件数超限!"
    assert total_bytes <= 10 * 1024 * 1024, "大小超限!"

if __name__ == "__main__":
    main()
