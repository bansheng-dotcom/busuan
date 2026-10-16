# -*- coding: utf-8 -*-
"""六爻理法知识包原文佐证回归：断语字段完整 + 「原文」可复核性报告。

`util/liuyao_knowledge.py`（王虎应体系离线回退）九类 66 条断语，每条声称含「原文+出处」。
本测试把这条声明变成可复核断言：

1. 硬断言：每条断语字段完整（断语/原文/出处）。
2. 原文可复核性报告：每条「原文」能否在六爻典籍 txt 中 Grep 到。
   「原文」字段现状混了四类——原文逐字 / 章名口诀 / 转写归纳 / 通论，
   能 Grep 的是「原文逐字」，其余是「偏理法」的体现（非手切库原文切片）。

对标 liuyao 参考项目的「6 书手切库 + 原文哈希」：本测试暴露离线回退的「原文」是
转写而非手切原文，作为「补手切库」的缺口清单，不硬断言全部可 Grep。

运行: python tests/liuyao_knowledge_regression.py
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

from util import liuyao_knowledge as lk

_TXT = r"D:\卜算\国学czhengli\txt"
_BOOKS = ["增删卜易", "卜筮正宗", "易冒", "易隐", "火珠林", "黄金策", "断易天机", "卜筮全书"]


def _load_books():
    books = {}
    for name in _BOOKS:
        p = os.path.join(_TXT, f"[易藏] {name}.txt")
        if os.path.exists(p):
            books[name] = open(p, encoding="utf-8").read()
    return books


def main():
    entries = list(lk._all())
    print(f"[六爻] 理法知识包原文佐证：{len(entries)} 条断语\n")

    # 1. 字段完整（硬断言）
    bad = [e["名称"] for e in entries if not e.get("断语") or not e.get("原文") or not e.get("出处")]
    ok_fields = not bad
    print(f"  {'✓' if ok_fields else '✗'} 字段完整：每条有 断语/原文/出处 {('；缺失 ' + str(bad)) if bad else ''}")

    # 2. 原文可复核性
    books = _load_books()
    hit, miss = [], []
    for e in entries:
        yuan, chu = e["原文"], e["出处"]
        found = next((n for n, t in books.items() if yuan in t), None)
        (hit if found else miss).append((e["类型"], e["名称"], yuan, chu, found))

    n = len(entries)
    print(f"\n  原文可复核性：{len(hit)} 条原文能 Grep 到典籍，{len(miss)} 条不能（{n} 条）")
    print(f"  [原文逐字可 Grep] {len(hit)} 条")
    for t, name, yuan, chu, found in hit[:8]:
        print(f"    ✓ {name} → {found}")
    print(f"\n  [不能 Grep] {len(miss)} 条（转写/章名/口诀/通论，补手切库的缺口）：")
    for t, name, yuan, chu, _ in miss:
        print(f"    · [{t}] {name}: 「{yuan}」— {chu}")

    fail = not ok_fields
    print(f"\n结果: {'失败' if fail else '通过'}（字段完整硬断言；原文可复核性仅报告不硬断言）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
