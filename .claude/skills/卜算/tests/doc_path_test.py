# -*- coding: utf-8 -*-
"""文档路径守护测试：SKILL.md / docs / references 里引用的 libs 模块路径必须真实存在。

背景：文件分层重构（libs 扁平 → pan/judge/gate/lifa/regress/util 子目录）后，
文档引用一度大量漂移成死路径（如 libs/case_search.py 实为 libs/util/case_search.py），
且回归测试直接 import 新路径、完全拦不住文档腐烂。本测试把「文档引用的每个
libs/xxx.py 都必须能在 scripts/libs 树下按精确相对路径找到」固化成硬 gate。

规则：
  1. `scripts/libs/<mod>.py` 与 `libs/<mod>.py` 都解析到 scripts/libs/<mod>.py，须存在；
  2. `libs/<mod>.方法`（如 libs/pan/bazi_json.enumerate_range）解析到 scripts/libs/<mod>.py；
  3. 顶层非 .py 文件（README / LICENSE，全大写）不参与校验。

运行: python tests/doc_path_test.py
"""
import re
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, ".."))
SCRIPTS = os.path.join(SKILL, "scripts")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 模块路径：小写字母/下划线开头，可多级（pan/bazi_json）。全大写的 README/LICENSE 天然被排除。
_PAT = re.compile(r"(?:scripts/)?libs/([a-z_][a-z_0-9]*(?:/[a-z_][a-z_0-9]*)*)")
# scripts/ 顶层脚本（cast.py、classical_search.py 等）
_TOP = re.compile(r"scripts/([a-z_][a-z_0-9]*\.py)")


def _doc_files():
    fps = [os.path.join(SKILL, "SKILL.md")]
    fps += glob.glob(os.path.join(SKILL, "docs", "*.md"))
    fps += glob.glob(os.path.join(SKILL, "references", "*.md"))
    return fps


def scan_dead_refs():
    """返回死引用列表 [(来源文件, 引用原文, 期望路径)]。"""
    dead = []
    for fp in _doc_files():
        txt = open(fp, encoding="utf-8").read()
        for m in _PAT.finditer(txt):
            mod = m.group(1)
            target = os.path.join(SCRIPTS, "libs", *mod.split("/")) + ".py"
            if not os.path.exists(target):
                dead.append((os.path.basename(fp), m.group(0), os.path.relpath(target, SKILL)))
        for m in _TOP.finditer(txt):
            name = m.group(1)
            target = os.path.join(SCRIPTS, name)
            if not os.path.exists(target):
                dead.append((os.path.basename(fp), m.group(0), os.path.relpath(target, SKILL)))
    return dead


def main():
    dead = scan_dead_refs()

    _PASS = _FAIL = 0
    print("[文档] libs 路径引用必须真实存在（防文档/代码漂移）")

    total_refs = 0
    for fp in _doc_files():
        txt = open(fp, encoding="utf-8").read()
        total_refs += len(_PAT.findall(txt)) + len(_TOP.findall(txt))

    ok = len(dead) == 0
    _PASS += ok
    _FAIL += (not ok)
    print(f"  {'✓' if ok else '✗'} 死引用数: {len(dead)}（共扫描 {total_refs} 处引用 / {len(_doc_files())} 个文档）")

    if dead:
        print("\n死引用详情（文档里的路径指向不存在的文件）：")
        for fn, ref, want in sorted(dead):
            print(f"  {fn}: {ref}  → 期望 {want}")
    print(f"\n结果: {_PASS} 通过 / {_FAIL} 失败")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
