# -*- coding: utf-8 -*-
"""从典籍《六壬指南注解》txt 提取占验案例 → 本技能案例库格式。

《六壬指南》卷三「六壬会纂占验指南」共 127 则占验案例。
案例格式：占验X、日期 占事 课体 空亡  +  课式图形  +  断曰（断语含应验）。

生成 cases/liuren/ 下（文件名 g_ 前缀，与断案/壬占汇选合并），后验按断语是否记「果/应/验」标记「命中」。

用法：python cases/extract_zhinan_cases.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\daimajieti1\国学czhengli\txt\[易藏] 六壬指南注解.txt"
DST = os.path.join(HERE, "liuren")

_TITLE = re.compile(r"占验[一二三四五六七八九十百]+[、，]")


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def main():
    os.makedirs(DST, exist_ok=True)
    lines = open(SRC, encoding="utf-8").read().splitlines()
    cases = []
    cur = None
    mode = "title"

    for line in lines:
        s = line.strip()
        if _TITLE.search(s) and len(s) < 120:
            if cur:
                cases.append(cur)
            # 占事：标题里「占X」或「问X」之后，或逗号后
            m = re.search(r"(?:占|问)([^，。]*?)(?:，|$)", s)
            zhan = m.group(1).strip() if m else "占验"
            cur = {"title": s, "zhan": zhan[:20], "duan": []}
            mode = "title"
            continue
        if cur is None:
            continue
        if "断曰" in s or (len(s) > 25 and "曰" in s):
            cur["duan"].append(s)
            mode = "duan"
            continue
        if mode == "duan" and len(s) > 10:
            cur["duan"].append(s)
        # mode == title：课式图形行，忽略
    if cur:
        cases.append(cur)

    hit = 0
    n = 0
    for c in cases:
        duan = "\n".join(c["duan"]).strip()
        if not duan or len(duan) < 15:
            continue
        n += 1
        is_hit = any(k in duan for k in ("果", "应", "验", "果验", "后果"))
        if is_hit:
            hit += 1
        fname = f"g_{n:03d}_{clean(c['zhan'][:12])}.md"
        path = os.path.join(DST, fname)
        md = f"""# 案例：{c['zhan'][:20]}（大六壬）

## 基本信息
- 来源：《六壬指南》·卷三占验指南
- 方法：大六壬
- 问事：{c['zhan'][:30]}

## 盘面（课式）
{c['title']}

## 断语（古籍原文）
{duan}

## 原理
（断语内含断卦依据）

## 后验
- 实际结果：古籍{'记应验（见断语「果/应」句）' if is_hit else '未明记应验'}
- 判定：{'命中' if is_hit else '未知'}
- 复盘：六壬课体 / 三传 / 类神断法校准案例

## 来源
《六壬指南》·占验指南·{c['zhan'][:20]}
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    print(f"已提取 {n} 则《六壬指南》占验案例到 cases/liuren/（命中 {hit}）")


if __name__ == "__main__":
    main()
