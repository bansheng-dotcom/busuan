# -*- coding: utf-8 -*-
"""苗公射覆鬼撮脚·原文佐证回归：射覆类象数据的「出处」可复核性。

`judge/miaogong_shefu.py`（大六壬射覆规则引擎）声称数据出自《六壬苗公射覆鬼撮脚》
（[易藏] 六壬苗公射覆鬼撮脚.txt）。本测试把这句话变成可复核断言：

1. 硬断言：数据结构完整——天将临辰矩阵 12 天将 × 12 辰、地支物象 12 支、五行物类 5×5、
   十干物色 10 干、课体物性 6 条；天空临戌/临亥的「（缺）」与原文缺漏一致。
2. 原文可复核性报告：每条「物类值」的片段能否在典籍 txt 中 Grep 到。
   「原文逐字/校订可追溯」能 Grep；「转写归纳」不能 Grep，作为补手切库的缺口清单。
   （典籍本身有 OCR 错字，如「临酉为自破哭用等物」应为「自破器用」，故 Grep 用片段容错，
   不硬断言每条完整值逐字可 Grep。）

对标六爻 liuyao_knowledge_regression 的「原文佐证」：暴露射覆类象里「转写 vs 原文」的病灶。

运行: python tests/miaogong_shefu_regression.py
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

from judge import miaogong_shefu as ms  # noqa: E402

_TXT = r"D:\卜算\国学czhengli\txt\[易藏] 六壬苗公射覆鬼撮脚.txt"

_ZHI = "子丑寅卯辰巳午未申酉戌亥"
# 通用后缀（拆分后剥离，避免「等物/之物」这类通用词误判为可 Grep）
_SUFFIX = ("等物", "之物", "等类", "物类", "之类", "之物类", "等", "物")


def _fragments(val):
    """物类值 → 可 Grep 片段（去括号、顿号/逗号/空格拆分、剥通用后缀）。"""
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


def main():
    txt = open(_TXT, encoding="utf-8").read()

    # ========== 1. 数据结构完整（硬断言） ==========
    tianjiang = list(ms._TIANJIANG_SHEFU.keys())
    struct_ok = True
    bad = []
    if len(tianjiang) != 12:
        struct_ok = False
        bad.append(f"天将数 {len(tianjiang)} != 12")
    for jiang in tianjiang:
        for zhi in _ZHI:
            if zhi not in ms._TIANJIANG_SHEFU[jiang]:
                struct_ok = False
                bad.append(f"{jiang}缺临{zhi}")
    if len(ms._ZHI_BAGUA_WUXIANG) != 12:
        struct_ok = False
        bad.append(f"地支物象 {len(ms._ZHI_BAGUA_WUXIANG)} != 12")
    if len(ms._WX_WULEI) != 5 or any(len(v) != 5 for v in ms._WX_WULEI.values()):
        struct_ok = False
        bad.append("五行物类非 5×5")
    if len(ms._SHIGAN_WUSE) != 10:
        struct_ok = False
        bad.append(f"十干物色 {len(ms._SHIGAN_WUSE)} != 10")
    if len(ms._KETI_WUXING) != 6:
        struct_ok = False
        bad.append(f"课体物性 {len(ms._KETI_WUXING)} != 6")
    # 天空临戌/临亥「（缺）」与原文缺漏一致（原文天空段只到临酉）
    sky_missing_ok = (ms._TIANJIANG_SHEFU["天空"]["戌"] == "（缺）"
                      and ms._TIANJIANG_SHEFU["天空"]["亥"] == "（缺）")

    print(f"[六壬射覆] 苗公射覆鬼撮脚原文佐证：天将临辰 {len(tianjiang)}×12 + 地支12 + 五行5×5 + 十干10 + 课体6\n")
    print(f"  {'✓' if struct_ok else '✗'} 数据结构完整{'；' + '、'.join(bad) if bad else ''}")
    print(f"  {'✓' if sky_missing_ok else '✗'} 天空临戌/临亥「（缺）」标注与原文缺漏一致")

    # ========== 2. 原文可复核性（报告，不硬断言） ==========
    # 2a. 天将临辰矩阵（核心，最高价值）
    hit, miss = [], []
    for jiang, node in ms._TIANJIANG_SHEFU.items():
        for zhi, val in node.items():
            if val == "（缺）":
                continue
            frags = _fragments(val)
            found = any(f in txt for f in frags) if frags else False
            (hit if found else miss).append((jiang, zhi, val))
    n = len(hit) + len(miss)
    print(f"\n  天将临辰矩阵可复核性：{len(hit)} 条可 Grep / {len(miss)} 条不能（{n} 条有效）")
    for jiang, zhi, val in miss:
        print(f"    · {jiang}临{zhi}: 「{val}」")

    # 2b. 地支物象
    zhi_hit, zhi_miss = 0, []
    for zhi, node in ms._ZHI_BAGUA_WUXIANG.items():
        frags = _fragments(node["物"])
        if any(f in txt for f in frags):
            zhi_hit += 1
        else:
            zhi_miss.append((zhi, node["物"]))
    print(f"\n  地支物象可复核性：{zhi_hit} 支可 Grep / {len(zhi_miss)} 支不能")
    for zhi, val in zhi_miss:
        print(f"    · {zhi}: 「{val}」")

    # 2c. 五行物类
    wx_hit, wx_miss = 0, []
    for wx, d in ms._WX_WULEI.items():
        for qi, val in d.items():
            if val in txt:
                wx_hit += 1
            else:
                wx_miss.append((wx, qi, val))
    print(f"  五行物类可复核性：{wx_hit} 条可 Grep / {len(wx_miss)} 条不能（25 条）")
    for wx, qi, val in wx_miss:
        print(f"    · {wx}·{qi}: 「{val}」")

    # ========== 结论 ==========
    # 硬断言只有「数据结构完整」；原文可复核性仅报告（典籍 OCR 错字 + 校订转写并存，不硬卡）
    fail = not (struct_ok and sky_missing_ok)
    print(f"\n结果: {'失败' if fail else '通过'}（数据结构完整硬断言；原文可复核性仅报告）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
