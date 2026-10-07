#!/usr/bin/env python3
"""Prove the packaged runtime stands alone: no repo checkout, no author paths.

Points the engine resolver at laoshifu_mcp/_runtime, then runs every engine the
MCP tools depend on and checks the results against known-good values.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
BUNDLE = PACKAGE_ROOT / "laoshifu_mcp" / "_runtime"

if not BUNDLE.is_dir():
    print("[STOP] 先运行 python scripts/sync-runtime.py", file=sys.stderr)
    raise SystemExit(1)

os.environ["LAOSHIFU_ENGINE_ROOT"] = str(BUNDLE)
sys.path.insert(0, str(PACKAGE_ROOT))

from laoshifu_mcp import runtime  # noqa: E402


def main() -> int:
    root = runtime.engine_root()
    assert root == BUNDLE.resolve(), f"引擎根目录未指向打包运行时：{root}"
    print(f"[1/5] 引擎根目录 {root}")

    node = runtime.node_binary()
    print(f"[2/5] Node 运行时 {node}")

    chart = runtime.bazi_ziwei_chart(
        year=2000,
        month=1,
        day=1,
        hour=12,
        minute=0,
        gender="male",
        calendar="solar",
        is_leap_month=False,
        time_zone=8,
        current_year=2026,
    )
    pillars = chart["pillars"]["formatted"]
    assert pillars == "己卯 丙子 戊午 戊午", f"八字回归不一致：{pillars}"
    assert len(chart["ziwei"]["gongs"]) == 12, "紫微十二宫缺失"
    print(f"[3/5] 八字紫微 {pillars} / 十二宫 {len(chart['ziwei']['gongs'])}")

    fusion = runtime.liuyao_qimen_fusion(
        question="打包校验用固定问题",
        category="career",
        method="numbers",
        numbers=[12, 35, 8],
        year=2026,
        month=9,
        day=17,
        hour=10,
        minute=30,
        time_zone=8,
    )
    assert fusion["conclusions"], "六爻奇门结论为空"
    assert "liuyao" in fusion["methods"] and "qimen" in fusion["methods"], "双法未同时出结果"
    print(f"[4/5] 六爻+奇门 结论 {len(fusion['conclusions'])} 条 / {fusion['agreement']['overall']}")

    rendered = runtime.hexagram_diagram(fusion)
    assert rendered["image"].startswith(b"\x89PNG\r\n\x1a\n"), "卦图不是合法 PNG"
    assert rendered["fallback_text"].strip(), "逐爻备用文本为空"
    candidates = runtime.resolve_pillars(
        pillars="己卯 丙子 戊午 戊午", start_year=1999, end_year=2000
    )
    assert candidates["count"] == 1, "四柱反查候选数异常"
    print(
        f"[5/5] 卦图 {len(rendered['image']) // 1024} KB / 逐爻 {len(rendered['fallback_text'])} 字"
        f" / 四柱反查 {candidates['candidates'][0]['date']}"
    )

    # A published bundle must not carry the consultation method.
    for leak in ("SKILL.md", "VOICE-SAMPLES.md", "PRODUCT-COPY.md"):
        assert not (BUNDLE / leak).exists(), f"运行时泄漏断法资料：{leak}"
    references = BUNDLE / "references"
    if references.is_dir():
        unexpected = {p.name for p in references.iterdir()} - {"qimen"}
        assert not unexpected, f"references/ 出现非算法资料：{sorted(unexpected)}"
    print("[OK] 打包运行时自足、可复现，且不含断法资料。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
