# -*- coding: utf-8 -*-
"""紫微格局判定回归：规则表字段完整性 + cond 可解析 + 原文佐证。

`judge/ziwei_geju_data.py` 的 GEJU_RULES 是 tianzhi-core 式的 JSON 规则表
（id/name/verdict/text/note/cond/reading），本测试三道 gate：
1. 字段完整性：每条格局字段齐全、id 唯一、verdict 合法。
2. cond 可解析：多张测试盘跑 find_geju 不抛异常（cond DSL 能被 GejuAdapter 解释）。
3. 原文佐证：每条格局的 text 至少一个片段能在《紫微斗数全书》txt 中 Grep 到（防 text 抄错）。

这是「判定条件正确性」的结构守卫，不是「格局判定准不准」的后验判断——
后者要看命中格局是否符合盘面（盘面事实层），属断卦语义，不在此机器 gate 内。

运行: python tests/ziwei_geju_regression.py
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

from judge import ziwei_geju_data as ZG
from pan import zhiwei

_TXT = r"D:\卜算\国学czhengli\txt\[术数] 紫微斗数全书.txt"

_REQUIRED = ["id", "name", "verdict", "text", "note", "cond", "reading"]


def main():
    rules = ZG.GEJU_RULES
    print(f"[紫微] 格局判定回归：{len(rules)} 格局规则表\n")

    # —— 1. 字段完整性 + id 唯一 + verdict 合法 ——
    bad = []
    ids = set()
    for r in rules:
        for f in _REQUIRED:
            if f not in r or not r[f]:
                bad.append((r.get("id"), f"缺 {f}"))
        if r["id"] in ids:
            bad.append((r["id"], "重复 id"))
        ids.add(r["id"])
        if r["verdict"] not in ("吉", "凶", "中"):
            bad.append((r["id"], f"非法 verdict {r['verdict']!r}"))
    ok_fields = not bad
    print(f"  {'✓' if ok_fields else '✗'} 字段完整性：{len(rules)} 条 id 唯一、字段齐全 {('；违规 ' + str(bad)) if bad else ''}")

    # —— 2. cond 可解析：多张盘跑 find_geju 不抛异常 ——
    #    找几张不同命宫的盘（不同生辰），确保覆盖面广
    charts_ok = True
    try:
        test_cases = [
            (1990, 5, 15, 8, 1),
            (1984, 2, 4, 12, 0),
            (2000, 11, 11, 6, 1),
            (1976, 8, 8, 20, 0),
        ]
        for tc in test_cases:
            chart = zhiwei.cast(*tc)
            hits = ZG.find_geju(chart)
            assert isinstance(hits, list)
    except Exception as e:
        charts_ok = False
        print(f"  ✗ cond 解析异常：{type(e).__name__}: {e}")
    print(f"  {'✓' if charts_ok else '✗'} cond 可解析：{len(test_cases)} 张盘跑 find_geju 无异常")

    # —— 3. 原文佐证：每条 text 至少一个片段能在《全书》Grep 到 ——
    corpus = open(_TXT, encoding="utf-8").read()
    no_src = []
    for r in rules:
        frags = [s.strip() for s in r["text"].split("；") if s.strip()]
        if not any(f in corpus for f in frags):
            no_src.append((r["id"], r["name"], frags))
    ok_src = not no_src
    print(f"  {'✓' if ok_src else '✗'} 原文佐证：每条格局 text 至少一片段见于《全书》txt {('；缺失 ' + str(no_src)) if no_src else ''}")

    fail = (not ok_fields) or (not charts_ok) or (not ok_src)
    print(f"\n结果: {'失败' if fail else '通过'}（字段完整性 + cond 可解析 + 原文佐证）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
