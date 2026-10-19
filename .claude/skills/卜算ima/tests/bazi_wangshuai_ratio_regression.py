# -*- coding: utf-8 -*-
"""八字旺衰连续 ratio 回归：`bazi_liunian.wangshuai_ratio` 的连续性与分档一致性。

收口「旺衰量化暴露连续 ratio（现为离散分）」的差距：`wangshuai_score` 是 0-100 帮身
绝对分（强/中和/弱三档），`wangshuai_ratio` 暴露 `ratio = 同党/(同党+异党)` 的归一化
连续值（身旺/偏旺/中和/偏弱/身弱五档，复用 `bazi_chain.day_master_strength` 成分加权）。

硬断言：
1. ratio 是 0-1 连续 float（批量盘面，非只有离散档位值）。
2. ratio 分档（五档）与 bazi_chain.RATIO_BANDS 阈值一致（机器可复算）。
3. wangshuai_ratio 与 bazi_chain.day_master_strength 结果逐盘一致（同一实现，防脱钩）。

运行: python tests/bazi_wangshuai_ratio_regression.py
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

from lunar_python import Solar  # noqa: E402
from pan import bazi_liunian as bl  # noqa: E402
from judge import bazi_chain as bc  # noqa: E402

# 一批盘面（固定 + 扫描月/日以覆盖不同旺衰档）
_DATES = [
    (2001, 9, 22, 4), (1984, 2, 4, 12), (1990, 5, 15, 8), (1976, 8, 8, 20),
    (2000, 1, 1, 0), (2000, 6, 1, 6), (2000, 12, 1, 12), (1999, 3, 3, 3),
    (1988, 11, 11, 23), (2005, 7, 7, 9), (2010, 10, 10, 15), (2015, 4, 4, 21),
]
# 额外扫描一批日柱（覆盖更多干支组合）
_EXTRA = [(2024, m, d, 12) for m in range(1, 13) for d in (1, 10, 20)]


def _label_of(ratio, bands):
    lo2, lo1, hi1, hi2 = bands
    if ratio >= hi2:
        return "身旺"
    if ratio >= hi1:
        return "偏旺"
    if ratio <= lo2:
        return "身弱"
    if ratio <= lo1:
        return "偏弱"
    return "中和"


def main():
    ratios = set()
    mism_label = []
    mismatch_chain = 0
    n = 0

    for y, mo, d, h in _DATES + _EXTRA:
        ec = Solar.fromYmdHms(y, mo, d, h, 0, 0).getLunar().getEightChar()
        r = bl.wangshuai_ratio(ec)
        n += 1
        ratio = r["ratio"]
        ratios.add(ratio)
        # 1. ratio 连续 float ∈ [0,1]
        if not (0.0 <= ratio <= 1.0):
            return print(f"✗ ratio 越界: {y}-{mo}-{d} {ratio}"), sys.exit(1)
        # 2. 分档与 RATIO_BANDS 一致
        expect = _label_of(ratio, bc.RATIO_BANDS)
        if r["档次"] != expect:
            mism_label.append((y, mo, d, ratio, r["档次"], expect))
        # 3. 与 day_master_strength 一致
        quad = {"year": (ec.getYearGan(), ec.getYearZhi()),
                "month": (ec.getMonthGan(), ec.getMonthZhi()),
                "day": (ec.getDayGan(), ec.getDayZhi()),
                "hour": (ec.getTimeGan(), ec.getTimeZhi())}
        s = bc.day_master_strength(quad)
        if abs(s.ratio - ratio) > 1e-6:
            mismatch_chain += 1

    print(f"[八字] 旺衰连续 ratio 回归：{n} 盘")
    print(f"  {'✓' if len(ratios) > 20 else '✗'} ratio 连续值覆盖 {len(ratios)} 个不同取值（>20 说明非离散档位）")
    print(f"  {'✓' if not mism_label else '✗'} 分档与 RATIO_BANDS 一致：{len(mism_label)} 处不符")
    for m in mism_label[:6]:
        print(f"      {m}")
    print(f"  {'✓' if mismatch_chain == 0 else '✗'} 与 bazi_chain.day_master_strength 逐盘一致：{mismatch_chain} 处脱钩")
    # 五档覆盖度（报告）
    labels = [bl.wangshuai_ratio(Solar.fromYmdHms(*d, 0, 0).getLunar().getEightChar())["档次"] for d in _DATES + _EXTRA]
    print(f"  五档覆盖：{', '.join(f'{x}={labels.count(x)}' for x in ('身旺','偏旺','中和','偏弱','身弱'))}")

    fail = (len(ratios) <= 20) or mism_label or mismatch_chain
    print(f"\n结果: {'失败' if fail else '通过'}（ratio 连续性 + 分档一致性 + 与推演链一致）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
