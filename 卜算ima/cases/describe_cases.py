# -*- coding: utf-8 -*-
"""全案例库描述性统计：占事分布 / 课体分布 / 卦象分布 / 天象分布 / 类别分布。

覆盖：六爻 381 / 六壬 218 / 天文占 120 / 梅花 10 / 八字(紫微) 160 题。
用法：python cases/describe_cases.py
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

GUA = ["", "乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
GUA64 = {
    (1,1):"乾为天",(2,2):"兑为泽",(3,3):"离为火",(4,4):"震为雷",(5,5):"巽为风",(6,6):"坎为水",(7,7):"艮为山",(8,8):"坤为地",
    (6,4):"水雷屯",(7,6):"山水蒙",(6,1):"水天需",(1,6):"天水讼",(8,6):"地水师",(6,8):"水地比",(5,1):"风天小畜",(1,5):"天风姤",
    (2,8):"泽地萃",(8,2):"地泽临",(3,1):"火天大有",(1,3):"天火同人",(4,8):"雷地豫",(8,4):"地雷复",(7,5):"山风蛊",(5,7):"风山渐",
    (1,8):"天地否",(8,1):"地天泰",(7,1):"山天大畜",(1,7):"天山遁",(4,3):"雷火丰",(3,4):"火雷噬嗑",(5,3):"风火家人",(3,5):"火风鼎",
    (4,1):"雷天大壮",(1,4):"天雷无妄",(6,3):"水火既济",(3,6):"火水未济",(2,1):"泽天夬",(1,2):"天泽履",(5,6):"风水涣",(6,5):"水风井",
    (7,3):"山火贲",(3,7):"火山旅",(4,7):"雷山小过",(7,4):"山雷颐",(2,3):"泽火革",(3,2):"火泽睽",(5,4):"风雷益",(4,5):"雷风恒",
    (6,2):"水泽节",(2,6):"泽水困",(8,5):"地风升",(5,8):"风地观",(7,2):"山泽损",(2,7):"泽山咸",(8,3):"地火明夷",(3,8):"火地晋",
    (4,6):"雷水解",(6,7):"水山蹇",(8,7):"地山谦",(7,8):"山地剥",(4,2):"雷泽归妹",(2,4):"泽雷随",(5,2):"风泽中孚",(2,5):"泽风大过",
}


def classify_zhanshi(z):
    if any(k in z for k in ("病","疾","医")): return "病"
    if any(k in z for k in ("财","店","求","卖","买","钱")): return "财求"
    if any(k in z for k in ("婚","妻","夫","嫁","娶")): return "婚姻"
    if any(k in z for k in ("官","讼","刑","狱","词")): return "官讼"
    if any(k in z for k in ("出","行","归","逃","走")): return "出行"
    if any(k in z for k in ("宅","家","屋","迁")): return "宅"
    if any(k in z for k in ("雨","晴","雪","风","天")): return "天时"
    if any(k in z for k in ("子","孕","产","胎","嗣","生")): return "子息"
    return "其他"


def stat_liuyao():
    d = json.load(open(os.path.join(HERE, "liuyao", "_tianji_guaili.json"), encoding="utf-8"))
    gl = d["卦例"]
    print("=" * 46)
    print(f"六爻 {len(gl)} 例")
    print("占事类别:", dict(Counter(classify_zhanshi(c.get('占事','')) for c in gl)))
    print("书号: 增删卜易(4)=", sum(1 for c in gl if c.get('书号')==4), " 卜筮正宗(6)=", sum(1 for c in gl if c.get('书号')==6))
    print("本卦 top10:", Counter(c.get('卦名','') for c in gl).most_common(10))
    print("变卦 top10:", Counter(c.get('变卦','') for c in gl).most_common(10))


def stat_liuren():
    zhan = Counter()
    keti = Counter()
    for f in os.listdir(os.path.join(HERE, "liuren")):
        if not f.endswith(".md") or f.startswith("_"): continue
        txt = open(os.path.join(HERE, "liuren", f), encoding="utf-8").read()
        m = re.search(r"问事：(.+)", txt)
        z = m.group(1) if m else ""
        if any(k in z for k in ("宅","屋")): zhan["宅墓"] += 1
        elif any(k in z for k in ("雨","晴","雪")): zhan["天时"] += 1
        elif any(k in z for k in ("病","疾")): zhan["病症"] += 1
        elif any(k in z for k in ("官","讼","刑")): zhan["官讼"] += 1
        elif any(k in z for k in ("财","店","求")): zhan["财"] += 1
        elif any(k in z for k in ("出","行","归")): zhan["出行"] += 1
        elif any(k in z for k in ("婚","妻","夫")): zhan["婚姻"] += 1
        elif any(k in z for k in ("子","孕","产")): zhan["子息"] += 1
        elif any(k in z for k in ("命","前程","仕","终身")): zhan["前程/终身"] += 1
        else: zhan["其他"] += 1
        m2 = re.search(r"盘面（课式）\n(.+)", txt)
        if m2:
            for k in ["元首","重审","知一","涉害","遥克","昴星","别责","八专","伏吟","返吟","反吟","铸印","乘轩","励德","乱首","不备","斫轮","间传","游子","稼穑","绝嗣","六仪","润下","炎上","从革","曲直","天网","闭口","度厄"]:
                if k in m2.group(1): keti[k] += 1
    print("=" * 46)
    print(f"六壬 {sum(zhan.values())} 例")
    print("占事分布:", dict(zhan))
    print("课体 top15:", keti.most_common(15))


def stat_tianwen():
    tian = Counter()
    for f in os.listdir(os.path.join(HERE, "tianwenzhan")):
        if f.endswith(".md"):
            tian[f.split("_", 1)[-1].replace(".md", "")] += 1
    print("=" * 46)
    print(f"天文占 {sum(tian.values())} 例")
    print("天象分布 top15:", tian.most_common(15))


def stat_meihua():
    print("=" * 46)
    files = sorted(f for f in os.listdir(os.path.join(HERE, "meihua")) if f.endswith(".md"))
    print(f"梅花 {len(files)} 例")
    for f in files:
        txt = open(os.path.join(HERE, "meihua", f), encoding="utf-8").read()
        # 提取卦名（"得天风姤"、"泽火革" 等）
        guas = re.findall(r"得([乾兑离震巽坎艮坤]{3,6})卦?|为([乾兑离震巽坎艮坤]+)卦", txt)
        print(f"  {f.split('_',1)[-1].replace('.md','')}: ", end="")
        m = re.search(r"盘面（起卦过程 \+ 卦象）\n(.{0,80})", txt)
        print(m.group(1)[:60] if m else "")


def stat_mingli():
    cats = Counter()
    for f in os.listdir(os.path.join(HERE, "mingli")):
        if not f.startswith("case_") or not f.endswith(".md"): continue
        txt = open(os.path.join(HERE, "mingli", f), encoding="utf-8").read()
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("|") and "ftb_" in s:
                cells = [c.strip() for c in s.strip("|").split("|")]
                if len(cells) >= 7: cats[cells[1]] += 1
    print("=" * 46)
    print(f"八字/紫微 MingLi-Bench {sum(cats.values())} 题")
    print("类别分布:", dict(cats))


if __name__ == "__main__":
    stat_liuyao()
    print()
    stat_liuren()
    print()
    stat_tianwen()
    print()
    stat_meihua()
    print()
    stat_mingli()
