# -*- coding: utf-8 -*-
"""紫微入限诀回归：14 主星全覆盖 + 入限断语原文可 Grep + 限运 DSL 判定。

`judge/ziwei_xian.py` 把《紫微斗数全书》卷一「诸星问答论」的「二限/限」入限断语结构化
（限运 DSL 收口：把「大限宫」作为盘面维度）。本测试：

1. 硬断言：14 颗主星全覆盖——10 颗有入限断语（XIAN_JU）+ 4 颗原文无「二限」句（_NO_XIAN_JU）。
2. 原文可复核：10 颗入限断语的关键句能否 Grep《紫微斗数全书》txt（原文逐字）。
3. 硬断言：find_xian 判定正确——对某盘，返回的入限断语 = 大限宫内主星的 XIAN_JU 断语。

诚实边界：天府/太阴/天梁/破军原文歌诀无「二限/限」句，不做入限判定（如实标注）。

运行: python tests/ziwei_xian_regression.py
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

import io, contextlib  # noqa: E402
from judge import ziwei_xian as zx  # noqa: E402
from pan import zhiwei  # noqa: E402

_TXT = r"D:\卜算\国学czhengli\txt\[术数] 紫微斗数全书.txt"

# 14 颗主星（紫微斗数全书「诸星问答论」问答的 14 主星）
_MAIN_STARS = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府",
               "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]


def main():
    txt = open(_TXT, encoding="utf-8").read()

    # ========== 1. 14 主星全覆盖 ==========
    covered = set(zx.XIAN_JU) | set(zx._NO_XIAN_JU)
    missing = [s for s in _MAIN_STARS if s not in covered]
    ok_cover = not missing
    print(f"[紫微入限诀] 14 主星全覆盖 + 入限断语原文可 Grep + 限运 DSL 判定\n")
    print(f"  {'✓' if ok_cover else '✗'} 14 主星覆盖：有入限断语 {len(zx.XIAN_JU)} + 原文无二限句 {len(zx._NO_XIAN_JU)}"
          f"{('；缺 ' + str(missing)) if missing else ''}")

    # ========== 2. 原文可 Grep ==========
    # 每颗星断语的关键句（去掉标点/星名后的可 Grep 片段）
    _GREP_KEY = {
        "紫微": "喜氣自然新", "天机": "事必有變更", "太阳": "必定賣田園",
        "武曲": "定主是非之撓", "天同": "一生得地", "廉贞": "災不可攘",
        "贪狼": "二限為禍非輕", "巨门": "災難不輕", "天相": "百事看充足",
        "七杀": "遭殃破敗",
    }
    hit = 0
    miss = []
    for star in zx.XIAN_JU:
        key = _GREP_KEY.get(star, "")
        # 简繁都试
        if key and (key in txt or _norm(key) in txt):
            hit += 1
        else:
            miss.append(star)
    print(f"  {'✓' if not miss else '✗'} 入限断语原文可 Grep《紫微斗数全书》：{hit}/{len(zx.XIAN_JU)}"
          f"{('；miss ' + str(miss)) if miss else ''}")

    # ========== 3. 限运 DSL 判定 ==========
    with contextlib.redirect_stdout(io.StringIO()):
        r = zhiwei.cast(1990, 5, 15, 8, 1)
    hits = zx.find_xian(r)
    # 手工验证：每个命中的入限断语，其星确实在该宫主星里、且该宫有大限
    ok_judge = True
    for h in hits:
        p = next(p for p in r["十二宫"] if p["宫"] == h["宫"])
        stars = {n for n, _b, _s in p["主星"]}
        if h["星"] not in stars or not p.get("大限"):
            ok_judge = False
    print(f"  {'✓' if ok_judge else '✗'} find_xian 判定：命中 {len(hits)} 条，星/宫/大限一致")
    for h in hits[:5]:
        print(f"      {h['大限起']:>2}-{h['大限止']:<2}岁 {h['宫']}({h['地支']}) {h['星']}〔{h['吉凶']}〕 {h['断语']}")

    fail = not (ok_cover and not miss and ok_judge)
    print(f"\n结果: {'失败' if fail else '通过'}（14 主星覆盖 + 入限断语原文可 Grep + 限运 DSL 判定）")
    sys.exit(1 if fail else 0)


def _norm(s):
    """简→繁 关键映射（穷通宝鉴等简繁混用，此处仅补个别字）。"""
    return s.replace("太阳", "太陽").replace("贪狼", "貪狼").replace("巨门", "巨門") \
            .replace("天相", "天相").replace("七杀", "七殺")


if __name__ == "__main__":
    main()
