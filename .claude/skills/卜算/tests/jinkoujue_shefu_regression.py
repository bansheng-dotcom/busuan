# -*- coding: utf-8 -*-
"""金口诀射覆门·原文佐证回归：射覆歌数据的「出处」可复核性。

`rules.jinkoujue_shefu_*`（金口诀射覆门）声称数据出自《六壬神课金口诀古本》·射覆门
（射覆歌/十干颜色/支干数目/五行数目/射物所在）。本测试把这句话变成可复核断言：

1. 硬断言：数据结构完整——地支物类 12 支、贵神物类 12 神、十干颜色 10 干、
   干支数目 10 干、支数目 12 支、五行数目 5 行。
2. 原文可复核性报告：每条「物类值」能否在《六壬神课金口诀古本》txt 中 Grep 到。

⚠️ 关键如实边界（测试会暴露）：金口诀古本 txt（2353 行）的「射覆门」**只有目录标题
（line 126-136：射覆歌/十干颜色/支干数目/五行数目/射物所在/占来意歌/都解歌），正文缺失**。
故 `_JK_SHEFU_ZHILEI`/`_JK_SHEFU_GUISHEN` 的地支/贵神物类值在本 txt 几乎 Grep 不到，
说明其出处是「另一金口诀版本」或「转写归纳」，而非本典籍原文逐字。这与大六壬苗公射覆
（141/142 原文逐字可 Grep）形成对照：金口诀射覆门数据出处存疑，须补典籍或标注转写。

运行: python tests/jinkoujue_shefu_regression.py
"""
import os
import re
import sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from judge import rules  # noqa: E402

_TXT = r"D:\卜算\国学czhengli\txt\[易藏] 六壬神课金口诀古本.txt"

_ZHI = "子丑寅卯辰巳午未申酉戌亥"
# 十二贵神（去别名后的标准名）
_GUISHEN = ["青龙", "螣蛇", "朱雀", "六合", "勾陈", "天空",
            "贵人", "天后", "太阴", "玄武", "太常", "白虎"]
_SUFFIX = ("等物", "之物", "等类", "物类", "之类", "等", "物", "类")


def _fragments(val):
    """物类值 → 可 Grep 片段（去括号、顿号/逗号拆分、剥通用后缀）。"""
    val = re.sub(r"[（）()【】]", " ", val)
    frags = []
    for f in re.split(r"[、，,；; /]", val):
        f = f.strip()
        for suf in _SUFFIX:
            if f.endswith(suf) and len(f) > len(suf):
                f = f[: -len(suf)]
        f = f.strip("。；;，, ")
        if len(f) >= 2:
            frags.append(f)
    return frags


def _grep_ratio(d, txt):
    """{key: val} -> (命中数, 总有效数, miss 清单)。"""
    hit, miss = 0, []
    for k, val in d.items():
        if val in ("（缺）", None, ""):
            continue
        frags = _fragments(val)
        if any(f in txt for f in frags):
            hit += 1
        else:
            miss.append((k, val))
    return hit, len([1 for k, v in d.items() if v not in ("（缺）", None, "")]), miss


def main():
    txt = open(_TXT, encoding="utf-8").read()

    # ========== 1. 数据结构完整（硬断言） ==========
    struct_ok = True
    bad = []
    if len(rules._JK_SHEFU_ZHILEI) != 12 or any(z not in rules._JK_SHEFU_ZHILEI for z in _ZHI):
        struct_ok = False
        bad.append(f"地支物类 {len(rules._JK_SHEFU_ZHILEI)} != 12 或缺支")
    gui_norm = {k: v for k, v in rules._JK_SHEFU_GUISHEN.items()
                if k in _GUISHEN}  # 别名（腾蛇/贵神/天乙）不计入标准 12
    if len(gui_norm) != 12:
        struct_ok = False
        bad.append(f"贵神物类标准名 {len(gui_norm)} != 12")
    if len(rules._JK_SHIGAN_YANSE) != 10:
        struct_ok = False
        bad.append(f"十干颜色 {len(rules._JK_SHIGAN_YANSE)} != 10")
    if len(rules._JK_GANZHI_SHU) != 10 or len(rules._JK_ZHI_SHU) != 12 or len(rules._JK_WX_SHU) != 5:
        struct_ok = False
        bad.append("数目表非 10/12/5")

    # 射覆门正文缺失判断：目录有「射覆门」标题（line 126），但正文（>200 行）无对应章节标题
    lines = txt.splitlines()
    body_shefu_men = sum(1 for i, l in enumerate(lines) if i >= 200 and l.strip() in ("射覆门", "射覆歌"))

    print(f"[金口诀射覆] 射覆门原文佐证：地支12 + 贵神12 + 十干颜色10 + 数目表 10/12/5\n")
    print(f"  {'✓' if struct_ok else '✗'} 数据结构完整{'；' + '、'.join(bad) if bad else ''}")
    print(f"  ⚠ 射覆门正文：目录有「射覆门」标题（line 126），正文无对应章节标题（{body_shefu_men} 处）")

    # ========== 2. 原文可复核性（报告，不硬断言） ==========
    h1, n1, m1 = _grep_ratio(rules._JK_SHEFU_ZHILEI, txt)
    h2, n2, m2 = _grep_ratio(gui_norm, txt)

    print(f"\n  地支物类可复核性：{h1} 支可 Grep / {n1 - h1} 支不能（{n1} 支）")
    for k, v in m1:
        print(f"    · {k}: 「{v}」")
    print(f"  贵神物类可复核性：{h2} 神可 Grep / {n2 - h2} 神不能（{n2} 神）")
    for k, v in m2:
        print(f"    · {k}: 「{v}」")

    # 十干颜色（单字色，用「{干}...{色}」不可靠，仅报告映射本身）
    print(f"\n  十干颜色映射（10 干）：{' '.join(f'{k}={v}' for k, v in rules._JK_SHIGAN_YANSE.items())}")

    # ========== 结论 ==========
    # 硬断言只有「数据结构完整」；原文可复核性仅报告。
    # 如实边界：射覆门正文在 txt 缺失，地支/贵神物类 Grep 率低 = 出处存疑（另一版本/转写），不判错但必须标注。
    fail = not struct_ok
    print(f"\n  如实边界：金口诀古本 txt「射覆门」仅目录无正文，地支/贵神物类在本 txt Grep 率 "
          f"{h1 + h2}/{n1 + n2}，出处存疑（可能为另一金口诀版本/转写归纳），待补典籍佐证。")
    print(f"\n结果: {'失败' if fail else '通过'}（数据结构完整硬断言；出处存疑如实标注）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
