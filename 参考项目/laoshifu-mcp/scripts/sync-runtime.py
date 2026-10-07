#!/usr/bin/env python3
"""Vendor the Laoshifu compute runtime into the MCP package.

Only the deterministic engines ship here: the bazi/ziwei chart engine, the
liuyao/qimen fusion engines, the diagram renderer and the four-pillar lookup.
The consultation references, voice guide and paid client stay out of the
published MCP package.

Usage:
    python scripts/sync-runtime.py            # refresh laoshifu_mcp/_runtime
    python scripts/sync-runtime.py --check    # verify an existing bundle
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
BUNDLE = PACKAGE_ROOT / "laoshifu_mcp" / "_runtime"

SCRIPT_FILES = (
    "chart_bazi_ziwei.py",
    "liuyao_qimen_fusion.py",
    "diagram_render.py",
    "resolve-pillars.cjs",
    "liuyao.cjs",
    "qimen.cjs",
)
SCRIPT_TREES = (
    "node_modules",
    "qimen_core",
    "diagram-assets",
)
ENGINE_TREES = ("calculator",)
# 奇门断局要读的九星/八门/八神/格局数据表。这是算法用数据，不是断法文稿；
# references/ 下的会谈规范、口吻与详解标准一律不进包。
DATA_TREES = (("references/qimen", "references/qimen"),)
ROOT_FILES = ("LICENSE", "NOTICE")

SKIP_DIRS = {"__pycache__", ".pytest_cache", ".venv", ".git"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".log"}

REQUIRED = (
    "scripts/chart_bazi_ziwei.py",
    "scripts/liuyao_qimen_fusion.py",
    "scripts/diagram_render.py",
    "scripts/resolve-pillars.cjs",
    "scripts/liuyao.cjs",
    "scripts/qimen.cjs",
    "scripts/diagram-assets/glyphs.json",
    "engine/calculator/dist/run-chart.js",
)


def _copy_tree(src: Path, dst: Path) -> None:
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        if set(rel.parts) & SKIP_DIRS:
            continue
        if item.is_dir() or item.suffix in SKIP_SUFFIXES:
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def build(force: bool) -> int:
    missing = [rel for rel in REQUIRED if not (REPO_ROOT / rel).is_file()]
    for tree in ("scripts/node_modules", "engine/calculator/node_modules", "scripts/qimen_core"):
        if not (REPO_ROOT / tree).is_dir():
            missing.append(tree + "/")
    if not (REPO_ROOT / "references/qimen").is_dir():
        missing.append("references/qimen/")
    if missing:
        print("[STOP] 源仓库缺少运行时文件：" + ", ".join(missing), file=sys.stderr)
        return 1

    if BUNDLE.exists():
        if not force:
            print(f"[STOP] {BUNDLE} 已存在，加 --force 才会覆盖。", file=sys.stderr)
            return 1
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir(parents=True)

    for name in ROOT_FILES:
        src = REPO_ROOT / name
        if src.is_file():
            shutil.copy2(src, BUNDLE / name)

    scripts_dst = BUNDLE / "scripts"
    scripts_dst.mkdir(parents=True, exist_ok=True)
    for name in SCRIPT_FILES:
        shutil.copy2(REPO_ROOT / "scripts" / name, scripts_dst / name)
    for tree in SCRIPT_TREES:
        _copy_tree(REPO_ROOT / "scripts" / tree, scripts_dst / tree)

    for tree in ENGINE_TREES:
        _copy_tree(REPO_ROOT / "engine" / tree, BUNDLE / "engine" / tree)

    for src_rel, dst_rel in DATA_TREES:
        _copy_tree(REPO_ROOT / src_rel, BUNDLE / dst_rel)

    total = sum(p.stat().st_size for p in BUNDLE.rglob("*") if p.is_file())
    count = sum(1 for p in BUNDLE.rglob("*") if p.is_file())
    print(f"[OK] 运行时已同步：{count} 个文件，{total / 1048576:.1f} MB -> {BUNDLE}")
    print("     下一步：python scripts/verify-bundle.py")
    return 0


def check() -> int:
    problems = [rel for rel in REQUIRED if not (BUNDLE / rel).is_file()]
    if problems:
        print("[STOP] 打包运行时缺少：" + ", ".join(problems), file=sys.stderr)
        return 1
    for leak in (
        "SKILL.md",
        "VOICE-SAMPLES.md",
        "PRODUCT-COPY.md",
        "scripts/paid_client.py",
    ):
        if (BUNDLE / leak).exists():
            print(f"[STOP] 运行时不应包含断法资料：{leak}", file=sys.stderr)
            return 1
    references = BUNDLE / "references"
    if references.is_dir():
        allowed = {"qimen"}
        unexpected = {p.name for p in references.iterdir()} - allowed
        if unexpected:
            print(f"[STOP] references/ 只允许 qimen 数据表，发现：{sorted(unexpected)}", file=sys.stderr)
            return 1
    print("[OK] 打包运行时完整，且不含会谈断法资料。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="覆盖已有 _runtime 目录")
    parser.add_argument("--check", action="store_true", help="只校验现有运行时")
    args = parser.parse_args()
    return check() if args.check else build(args.force)


if __name__ == "__main__":
    raise SystemExit(main())
