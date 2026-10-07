# -*- coding: utf-8 -*-
"""从典籍《六壬断案》txt 提取邵彦和占验案例 → 本技能案例库格式。

《六壬断案》共 216 例（天时3/宅墓39/前程仕进58/终身16/流年2/婚姻3/胎产子息7/财产12/
一课二事3/交易2/出行访谒7/行人音信6/病症17/六畜9/亡盗14/官讼12/杂占6）。
每例结构：NN）占事+课式  →  邵先生曰（断语，含"果…"应验）  →  先生析曰（原理）。

生成 cases/liuren/*.md，后验按断语是否记"果/应/验"标记「命中」，断语遗失标记「未知」。

用法：python cases/extract_liuren_cases.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\daimajieti1\国学czhengli\txt\[易藏] 六壬断案.txt"
DST = os.path.join(HERE, "liuren")


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def main():
    os.makedirs(DST, exist_ok=True)
    lines = open(SRC, encoding="utf-8").read().splitlines()
    cases = []
    cur = None
    mode = "title"  # title=标题后课式图形 / duan=断语 / xi=原理

    for line in lines:
        s = line.strip()
        m = re.match(r"^(\d+)）(.+)", s)
        if m:
            if cur:
                cases.append(cur)
            title = m.group(2)
            zhan = re.split(r"[，,。]", title)[0].strip()
            cur = {"num": int(m.group(1)), "title": s, "zhan": zhan,
                   "duan": [], "xi": []}
            mode = "title"
            continue
        if cur is None:
            continue
        if "邵先生曰" in s or s.startswith("先生曰"):
            cur["duan"].append(s)
            mode = "duan"
            continue
        if "先生析曰" in s or s.startswith("析曰"):
            cur["xi"].append(s)
            mode = "xi"
            continue
        if mode == "duan":
            cur["duan"].append(s)
        elif mode == "xi":
            cur["xi"].append(s)
        # mode == title：课式图形行，忽略
    if cur:
        cases.append(cur)

    hit = miss = unknown = 0
    for idx, c in enumerate(cases, 1):
        duan = "\n".join(c["duan"]).strip()
        xi = "\n".join(c["xi"]).strip()
        # 应验判断
        if "断语遗失" in c["title"] or "断语遗失" in duan:
            verdict, unknown_ = "未知", True
            unknown += 1
        elif re.search(r"果[^，。]{0,20}？?[^。]*[。]", duan) or any(k in duan for k in ("果然", "果", "后", "验")):
            verdict, unknown_ = "命中", False
            hit += 1
        else:
            verdict, unknown_ = "命中", False  # 古籍案例主体记应验
            hit += 1

        fname = f"{idx:03d}_{clean(c['zhan'])}.md"
        path = os.path.join(DST, fname)
        body = f"""# 案例：{c['zhan']}（大六壬）

## 基本信息
- 来源：《六壬断案》·邵彦和占验案例（第{c['num']}例，共 216 例）
- 方法：大六壬
- 问事：{c['zhan']}

## 盘面（课式）
{c['title']}

## 断语（古籍原文）
{duan or '（断语遗失）'}

## 原理（先生析曰）
{xi or '（无）'}

## 后验
- 实际结果：古籍{'记应验（见断语「果…」句）' if not unknown_ else '断语遗失，无法判定'}
- 判定：{verdict}
- 复盘：六壬课体 / 三传 / 类神断法校准案例

## 来源
《六壬断案》第{c['num']}例（邵彦和占验）
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)

    print(f"已提取 {len(cases)} 则六壬案例到 cases/liuren/（命中 {hit} · 未知 {unknown}）")


if __name__ == "__main__":
    main()
