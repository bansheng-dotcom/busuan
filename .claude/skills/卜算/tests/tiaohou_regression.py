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

# 十干 × 十二月「第一用神」golden（据《穷通宝鉴》各月明确表述提取）。
# 每干 12 字，顺序=寅卯辰巳午未申酉戌亥子丑；'?'=原文未明确（合并论述/缺失/并列）。
_FIRST_GOLDEN = {
    "甲": "丙庚庚癸癸丁丁丁丁庚丁庚",
    "乙": "丙丙癸癸癸丙己癸癸丙丙丙",
    "丙": "壬壬壬壬壬壬壬壬甲甲壬壬",
    "丁": "庚庚甲庚?甲甲?甲甲甲甲",
    "戊": "丙丙甲甲壬癸丙丙甲甲丙丙",
    "己": "丙甲丙癸癸癸癸癸甲丙丙丙",
    "庚": "丙丁甲壬壬丁丁丁甲丁丁丙",
    "辛": "己壬壬壬?壬壬壬壬壬丙丙",
    "壬": "庚戊甲壬癸辛戊甲甲戊戊丙",
    "癸": "辛庚丙辛庚庚丁辛辛庚丙丙",
}
# 关键差异格的原文表述（差异报告引用出处，避免「断言无据」）
_NOTE = {
    ("甲", "未"): "六月先丁後庚", ("甲", "申"): "七月丁火为尊",
    ("甲", "戌"): "九月独爱丁火", ("甲", "丑"): "十二月先用庚劈甲",
    ("丁", "寅"): "正月姑用庚金(劈甲)", ("丁", "巳"): "四月必用庚劈甲",
    ("壬", "巳"): "四月专取壬水比肩", ("辛", "寅"): "正月取己土为身之本",
    ("辛", "亥"): "十月先用壬水", ("辛", "子"): "十一月壬丙两透",
    ("己", "申"): "三秋己土癸先丙後", ("庚", "辰"): "三月先甲後丁",
    ("戊", "辰"): "三月先甲後丙", ("乙", "申"): "七月喜己土为用",
}


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

    # —— 差异报告：全量 120 格第一用神（10 干 × 12 月） ——
    print("\n  [差异报告] 全量 120 格：原文第一用神 vs TIAO_HOU 首用神（'?'=原文未明确）")
    diff, weiming = [], []
    for g in _GAN:
        s = _FIRST_GOLDEN[g]
        for i, z in enumerate(_ZHI):
            yuan = s[i]
            if yuan == "?":
                weiming.append((g, z))
                continue
            got = TIAO_HOU[g][z][0]
            if got != yuan:
                note = _NOTE.get((g, z), "")
                diff.append((g, z, yuan, got, note))
    for g, z, yuan, got, note in diff:
        print(f"    ✗ {g}{z}月: 原文「{yuan}」{('（' + note + '）') if note else ''} ≠ TIAO_HOU 首用神「{got}」")
    print(f"\n  差异 {len(diff)} 处（提炼口径差异，非对错，供人工复核）；原文未明确 {len(weiming)} 格：")
    if weiming:
        print("    未明确格：" + "、".join(f"{g}{z}" for g, z in weiming))

    fail = (not ok_count) or (not ok_legal)
    print(f"\n结果: {'失败' if fail else '通过'}（120 完整性 + 合法性硬断言；第一用神差异不判错）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
