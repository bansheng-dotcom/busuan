# -*- coding: utf-8 -*-
"""生成 ima 上传用的精简技能包。

案例库已移到 D:/daimajieti1/国学czhengli/txt/案例库/（技能目录外），本脚本只需排除：
  - __pycache__/*.pyc 缓存、*.pkl 二进制、_tianji_*.json 原始数据、bench/tests/traces/feedback 开发数据。

用法：python make_upload_pkg.py
输出：卜算_upload.zip（约 5.5MB / 100 文件，可上传 ima）
"""
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "卜算"

EXCLUDE_DIRS = {"__pycache__", "bench", "tests", "traces", "feedback"}
EXCLUDE_SUFFIX = {".pyc", ".pkl"}
EXCLUDE_FILES = {"_tianji_guaili.json", "_tianji_gold.json", "_tianji_LICENSE.txt"}


def should_keep(path):
    rel = os.path.relpath(path, HERE)
    parts = rel.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return False
    if os.path.splitext(path)[1].lower() in EXCLUDE_SUFFIX:
        return False
    if os.path.basename(path) in EXCLUDE_FILES:
        return False
    if "upload" in os.path.basename(path) and path.endswith(".zip"):
        return False
    return True


def main():
    out = os.path.join(HERE, f"{NAME}_upload.zip")
    if os.path.exists(out):
        os.remove(out)
    files = []
    for root, dirs, fnames in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for fn in fnames:
            fp = os.path.join(root, fn)
            if should_keep(fp):
                files.append(fp)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for fp in sorted(files):
            rel = os.path.relpath(fp, HERE)
            z.write(fp, os.path.join(NAME, rel))
    print(f"已生成 {out}")
    print(f"  文件数: {len(files)}  大小: {os.path.getsize(out)/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
