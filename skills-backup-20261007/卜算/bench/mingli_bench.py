# -*- coding: utf-8 -*-
"""MingLi-Bench 断卦自测 harness。

数据源: https://github.com/DestinyLinker/MingLi-Bench （全球算命师大赛 2022-2025 真题 160 题，四选一）
说明: 该基准只测「推理」不测「排盘」——排盘由本技能 cast.py 自行起盘，再作答。

用法:
  python bench/mingli_bench.py --summary            # 类别/题量总览
  python bench/mingli_bench.py --dump 5             # 打印前 5 题的出生信息+题目+选项(供作答)
  python bench/mingli_bench.py --score answers.json # 按提供的答案算准确率
"""
import json
import os
import sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mingli_bench_data.json")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)["questions"]


def summary(qs):
    from collections import Counter
    cats = Counter(q["category"] for q in qs)
    has = sum(1 for q in qs if q.get("has_answer"))
    print(f"总题数: {len(qs)}  有标准答案: {has}")
    print("类别分布:")
    for c, n in cats.most_common():
        print(f"  {c}: {n}")


def dump(qs, n):
    for q in qs[:n]:
        bi = q["birth_info"]
        print(f"\n【{q['id']}】 {q['question']}  (类别:{q['category']}, 答案:{q.get('answer','?')})")
        print(f"  出生: {bi.get('raw')}  性别:{bi.get('gender')}")
        print(f"  排盘参数: {bi.get('year')}/{bi.get('month')}/{bi.get('day')} {bi.get('hour')}:{bi.get('minute')}")
        for o in q["options"]:
            print(f"    {o['letter']}. {o['text']}")


def score(qs, answers):
    correct = 0
    total = 0
    detail = []
    for q in qs:
        if not q.get("has_answer"):
            continue
        a = answers.get(q["id"])
        if a is None:
            continue
        total += 1
        if a.upper() == q["answer"]:
            correct += 1
        else:
            detail.append((q["id"], q["category"], q["answer"], a))
    print(f"答对 {correct}/{total} = {correct/total*100:.1f}%（随机线约 25%）")
    if detail:
        print("答错明细:")
        for i, c, g, a in detail:
            print(f"  {i} [{c}] 标准={g} 你的={a}")


def main():
    qs = load()
    if "--summary" in sys.argv:
        summary(qs)
    elif "--dump" in sys.argv:
        n = int(sys.argv[sys.argv.index("--dump") + 1])
        dump(qs, n)
    elif "--score" in sys.argv:
        with open(sys.argv[sys.argv.index("--score") + 1], encoding="utf-8") as f:
            score(qs, json.load(f))
    else:
        summary(qs)


if __name__ == "__main__":
    main()
