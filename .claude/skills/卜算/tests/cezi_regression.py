# -*- coding: utf-8 -*-
"""测字规则引擎回归：拆字十法/心易六法/六神 数据完整 + 典籍原文可 Grep。

`judge/cezi.py`（测字规则引擎）把 `references/相字术速查.md` 的测字十法/心易六法/六神主事/
六神笔法/起六神卦诀/五行体 结构化进代码。本测试把「出处《测字秘牒》《梅花易数卷四五相字术》」
变成可复核断言：

1. 硬断言：数据结构完整（十法 10、六法 6、六神主事 6、六神笔法 6、起卦 10、五行体 5）。
2. 硬断言：规则函数正确（甲乙起青龙/庚辛起白虎、青龙主喜事/白虎主丧灾）。
3. 原文可复核性：十法名/六神名 能否在典籍 txt Grep 到（原文逐字，非转写）。

测字靠触机、「神而明之存乎其人」，本测试只锁「确定性数据 + 规则」，拆字成何字仍触机而断。

运行: python tests/cezi_regression.py
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

from judge import cezi  # noqa: E402

_SHI_TXT = r"D:\卜算\国学czhengli\txt\[易藏] 测字秘牒.txt"
_XZ_TXT = r"D:\卜算\国学czhengli\txt\[易藏] 梅花易数卷四五相字术.txt"


def main():
    # ========== 1. 数据结构完整 ==========
    struct_ok = True
    bad = []
    if len(cezi.SHIFA) != 10:
        struct_ok = False; bad.append(f"十法 {len(cezi.SHIFA)} != 10")
    if len(cezi.XINYI) != 6:
        struct_ok = False; bad.append(f"六法 {len(cezi.XINYI)} != 6")
    if len(cezi.LIUYAO_ZHUSHI) != 6 or len(cezi.LIUYAO_BIFA) != 6:
        struct_ok = False; bad.append("六神主事/笔法 != 6")
    if len(cezi._QIGUA) != 10 or len(cezi.WUXING_TI) != 5:
        struct_ok = False; bad.append("起卦/五行体 非 10/5")
    print(f"[测字] 规则引擎回归：拆字十法/心易六法/六神/五行体\n")
    print(f"  {'✓' if struct_ok else '✗'} 数据结构完整{'；' + '、'.join(bad) if bad else ''}")

    # ========== 2. 规则函数正确性 ==========
    r_qg_jia = cezi.cezi_qigua("甲")["result"]
    r_qg_geng = cezi.cezi_qigua("庚")["result"]
    r_zs_qing = cezi.cezi_zhushi("青龙")["result"]
    r_zs_bai = cezi.cezi_zhushi("白虎")["result"]
    r_bifa = cezi.cezi_bifa("玄武")["result"]
    ok_rule = ("青龙" in r_qg_jia and "白虎" in r_qg_geng
               and "喜" in r_zs_qing and "凶伤" in r_zs_bai and "三点水" in r_bifa)
    print(f"  {'✓' if ok_rule else '✗'} 规则：甲乙起青龙/庚辛起白虎、青龙主喜事/白虎主凶伤、玄武三点水斜")

    # ========== 3. 原文可复核性（报告） ==========
    shi_txt = open(_SHI_TXT, encoding="utf-8").read()
    xz_txt = open(_XZ_TXT, encoding="utf-8").read()
    shifa_hit = [f for f in cezi.SHIFA if f in shi_txt]
    xinyi_hit = [f for f in cezi.XINYI if f in shi_txt]
    liuyao_hit = [f for f in cezi.LIUYAO_ZHUSHI if f in xz_txt]
    print(f"  十法名可 Grep《测字秘牒》{len(shifa_hit)}/10；六法名 {len(xinyi_hit)}/6；六神名可 Grep《相字术》{len(liuyao_hit)}/6")

    # ========== 4. 聚合画像 ==========
    p = cezi.portrait_cezi("王", "甲", "装头")
    ok_portrait = "拆法" in p["画像"] and "六神主事" in p["画像"]
    print(f"  {'✓' if ok_portrait else '✗'} 聚合画像（拆法 + 起六神 + 主事 + 笔法）")

    fail = not (struct_ok and ok_rule and ok_portrait)
    print(f"\n结果: {'失败' if fail else '通过'}（数据完整 + 规则正确 + 画像聚合；原文可复核仅报告）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
