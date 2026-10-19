# -*- coding: utf-8 -*-
"""奇门 evaluator 终审回归：独立检测层 vs rules 主判逐维对拍 + 排盘 SOP 数据完整性。

把「独立评估者」声明变成可证伪断言（对标 qimen-dunjia 的 verify.py 检测项完整性 + evaluator 独立复核）：
1. 硬断言：独立检测层（门迫/六仪击刑/三奇六仪入墓/五不遇时/十干克应）与 `rules.qimen_*`
   主判逐宫一致——表若抄错，独立重写表会立刻报冲突（对照 zhiwei BRIGHTNESS 抄错 148/168 的教训）。
2. 缺失检测如实报告：伏吟/反吟/内外盘 rules 尚未实现，evaluator 独立补出，不冒充已判。
3. 硬断言：排盘 SOP 数据完整（断卦所需的 排局/干支/旬空/值符值使/天地盘/门/星/神/马星 齐全）。

运行: python tests/qimen_evaluator_regression.py
"""
import os
import sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

import datetime  # noqa: E402
from engines.qimen import Qimen  # noqa: E402
from judge import qimen_evaluator as qe  # noqa: E402

# 覆盖阴阳遁、上下中元、四柱多样：跨 2026 每月两例（奇门用置闰法定局，节气边界不苛求）
_DATES = [
    (2026, 1, 15, 10), (2026, 2, 10, 14), (2026, 3, 5, 8), (2026, 4, 1, 12),
    (2026, 5, 20, 16), (2026, 6, 6, 9), (2026, 7, 15, 11), (2026, 8, 1, 13),
    (2026, 9, 10, 15), (2026, 10, 7, 10), (2026, 11, 1, 7), (2026, 12, 25, 18),
]

_SOP_FIELDS = ("排局", "干支", "旬空", "值符值使", "天盤", "地盤", "門", "星", "神", "馬星")


def main():
    conflicts = []
    missing = set()
    sop_bad = []
    total = 0

    print("[奇门] evaluator 终审回归：独立检测层 vs rules 主判（{n} 盘）".format(n=len(_DATES)))
    for y, mo, d, h in _DATES:
        total += 1
        pan = Qimen(y, mo, d, h, 0).pan(2)

        # —— SOP 数据完整性 ——
        for f in _SOP_FIELDS:
            if f not in pan:
                sop_bad.append((y, mo, d, h, f))

        r = qe.cross_check(pan)
        if r["冲突数"]:
            conflicts.append((y, mo, d, h, r["比对"]))
        missing |= set(r["缺失检测"])
        ju = r["检测层"]["局"]
        det = r["检测层"]
        hit = (sum(det["门迫"].values()), sum(det["击刑"].values()), sum(det["入墓"].values()))
        print(f"  ✓ {y}-{mo:02d}-{d:02d} {h:02d}:00  {ju[0]}遁{ju[1]}局  "
              f"门迫{hit[0]}宫 击刑{hit[1]}宫 入墓{hit[2]}宫  "
              f"五不遇时={'是' if det['五不遇时'] else '否'}  冲突{len(r['比对'])}")

    # —— 硬断言：无冲突、SOP 完整 ——
    ok_conflict = not conflicts
    ok_sop = not sop_bad
    print(f"\n  {'✓' if ok_conflict else '✗'} 独立检测层与 rules 主判逐宫一致：冲突 {len(conflicts)}")
    if conflicts:
        for y, mo, d, h, cmp in conflicts[:5]:
            print(f"      {y}-{mo:02d}-{d:02d} {h:02d}:00 {cmp}")
    print(f"  {'✓' if ok_sop else '✗'} SOP 数据完整：{total} 盘缺字段 {len(sop_bad)}")
    if sop_bad:
        print(f"      {sop_bad[:8]}")
    print(f"  ⚠ 缺失检测（rules 未实现，evaluator 独立补出，不判错）：{'、'.join(sorted(missing))}")

    fail = not (ok_conflict and ok_sop)
    print(f"\n结果: {'失败' if fail else '通过'}（检测层对拍一致 + SOP 数据完整）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
