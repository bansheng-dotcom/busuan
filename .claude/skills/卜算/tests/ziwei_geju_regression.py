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
    corpus = open(_TXT, encoding="utf-8").read()
    tables = [
        ("格局", ZG.GEJU_RULES, ZG.find_geju),
        ("落宫", ZG.STAR_GONG, ZG.find_star_gong),
    ]
    all_ok = True

    for label, table, finder in tables:
        print(f"[紫微·{label}] {len(table)} 条\n")

        # —— 1. 字段完整性 + id 唯一 + verdict 合法 ——
        bad = []
        ids = set()
        for r in table:
            for f in ("id", "verdict", "text", "note", "cond", "reading"):
                if f not in r or not r[f]:
                    bad.append((r.get("id"), f"缺 {f}"))
            if r["id"] in ids:
                bad.append((r["id"], "重复 id"))
            ids.add(r["id"])
            if r["verdict"] not in ("吉", "凶", "中"):
                bad.append((r["id"], f"非法 verdict {r['verdict']!r}"))
        ok_fields = not bad
        print(f"  {'✓' if ok_fields else '✗'} 字段完整性 {('；违规 ' + str(bad)) if bad else ''}")

        # —— 2. cond 可解析 ——
        charts_ok = True
        try:
            for tc in [(1990, 5, 15, 8, 1), (1984, 2, 4, 12, 0), (2000, 11, 11, 6, 1), (1976, 8, 8, 20, 0)]:
                assert isinstance(finder(zhiwei.cast(*tc)), list)
        except Exception as e:
            charts_ok = False
            print(f"  ✗ cond 解析异常：{type(e).__name__}: {e}")
        print(f"  {'✓' if charts_ok else '✗'} cond 可解析")

        # —— 3. 原文佐证 ——
        no_src = []
        for r in table:
            frags = [s.strip() for s in r["text"].split("；") if s.strip()]
            if not any(f in corpus for f in frags):
                no_src.append((r["id"], frags))
        ok_src = not no_src
        print(f"  {'✓' if ok_src else '✗'} 原文佐证 {('；缺失 ' + str(no_src)) if no_src else ''}")

        all_ok = all_ok and ok_fields and charts_ok and ok_src
        print()

    print(f"结果: {'通过' if all_ok else '失败'}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
