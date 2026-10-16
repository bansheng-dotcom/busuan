# -*- coding: utf-8 -*-
"""八字调候 120 格回归：TIAO_HOU 数据完整性/合法性 + 原文第一用神差异报告。

`judge/tiaohou.py` 的 TIAO_HOU（借自 yueyuan-bazi，MIT）是 10 天干 × 12 月令 = 120 格
调候用神数据，提炼自《穷通宝鉴》。与六壬（逻辑 bug）/ 奇门（格局名逐字对拍）不同，
调候原文是**论述体**（用神散在文言，且 yueyuan-bazi 综合了《穷通宝鉴》《栏江网》等多版本），
无法像奇门那样逐字机器对拍。故本测试分两层：

1. **硬断言**（确定可靠）：120 条齐全、每条用神合法（在十干内）且非空无重复。
2. **差异报告**（不判错）：甲木 12 月的原文「第一用神」（先X / X为尊 / 专用X 等明确表述）
   与 TIAO_HOU 第一用神对比，不一致的列出供人工复核——这是「提炼差异」不是「对错」，
   不能拿原文硬改 TIAO_HOU（调候有多版本口径，见 SKILL.md 流派分歧纪律）。

运行: python tests/tiaohou_regression.py
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

from judge.tiaohou import TIAO_HOU

_GAN = "甲乙丙丁戊己庚辛壬癸"
_ZHI = "寅卯辰巳午未申酉戌亥子丑"

# 甲木 12 月：原文「第一用神」golden（据《穷通宝鉴》各月明确表述提取）
_JIA_FIRST = [
    ("寅", "丙", "正月得丙癸逢"),
    ("卯", "庚", "二月庚金得所"),
    ("辰", "庚", "三月先取庚金"),
    ("巳", "癸", "四月先癸後丁"),
    ("午", "癸", "五月先癸後丁"),
    ("未", "丁", "六月先丁後庚"),
    ("申", "丁", "七月丁火为尊"),
    ("酉", "丁", "八月丁火为先"),
    ("戌", "丁", "九月独爱丁火"),
    ("亥", "庚", "十月庚丁为要"),
    ("子", "丁", "十一月丁先庚後"),
    ("丑", "庚", "十二月先用庚劈甲"),
]


def main():
    print("[八字] 调候 120 格：TIAO_HOU 完整性/合法性 + 原文第一用神差异报告\n")

    # —— 硬断言 1：120 条齐全 ——
    total = sum(len(v) for v in TIAO_HOU.values())
    missing_gan = [g for g in _GAN if g not in TIAO_HOU]
    missing_zhi = [(g, z) for g in _GAN for z in _ZHI if z not in TIAO_HOU.get(g, {})]
    ok_count = total == 120 and not missing_gan and not missing_zhi
    print(f"  {'✓' if ok_count else '✗'} 完整性：{total} 条（应为 120）；缺干 {missing_gan or '无'}；缺月 {missing_zhi or '无'}")

    # —— 硬断言 2：用神合法且非空无重复 ——
    bad = []
    for g in _GAN:
        for z in _ZHI:
            ys = TIAO_HOU.get(g, {}).get(z, [])
            if not ys:
                bad.append((g, z, "空"))
                continue
            for y in ys:
                if y not in _GAN:
                    bad.append((g, z, f"非法用神 {y}"))
            if len(ys) != len(set(ys)):
                bad.append((g, z, f"重复 {ys}"))
    ok_legal = not bad
    print(f"  {'✓' if ok_legal else '✗'} 合法性：每条用神在十干内、非空、无重复 {('；违规 ' + str(bad)) if bad else ''}")

    # —— 差异报告：甲木 12 月第一用神 ——
    print("\n  [差异报告] 甲木 12 月：原文第一用神 vs TIAO_HOU 第一用神")
    diff = []
    for z, yuan_first, note in _JIA_FIRST:
        got = TIAO_HOU["甲"][z]
        mark = "✓" if got[0] == yuan_first else "✗"
        if got[0] != yuan_first:
            diff.append((z, yuan_first, got, note))
        print(f"    {mark} 甲{('寅卯辰巳午未申酉戌亥子丑'.index(z)+1)}月({z}): 原文「{yuan_first}」vs TIAO_HOU {got}  [{note}]")

    print(f"\n  差异 {len(diff)} 处（提炼口径差异，非对错，供人工复核）：")
    for z, yuan_first, got, note in diff:
        print(f"    甲{('寅卯辰巳午未申酉戌亥子丑'.index(z)+1)}月({z}): 原文「{yuan_first}」≠ TIAO_HOU 首用神「{got[0]}」")

    fail = (not ok_count) or (not ok_legal)
    print(f"\n结果: {'失败' if fail else '通过'}（120 完整性 + 合法性硬断言；第一用神差异不判错）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
