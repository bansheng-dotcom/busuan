# -*- coding: utf-8 -*-
"""从典籍《壬占汇选》txt 提取六壬占验案例 → 本技能案例库格式。

《壬占汇选》是六壬占验案例汇编（徐次宾/邵彦和/范蠡等诸家占案）。
案例格式：标题「X月X日X将X时占X」+ 课式图形 + 断语「XX曰：…」+ 应验「果/应…」。

生成 cases/liuren/ 下（与六壬断案合并），后验按断语是否记「果/应/验」标记「命中」。

用法：python cases/extract_renzhan_cases.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\daimajieti1\国学czhengli\txt\[易藏] 壬占汇选.txt"
DST = os.path.join(HERE, "liuren")

# 案例标题：含「日X将X时」+「占」
_TITLE = re.compile(r"日[子丑寅卯辰巳午未申酉戌亥]将[子丑寅卯辰巳午未申酉戌亥]时[^。\n]{0,40}?占")


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def main():
    os.makedirs(DST, exist_ok=True)
    lines = open(SRC, encoding="utf-8").read().splitlines()
    cases = []
    cur = None
    mode = "title"  # title=课式图形 / duan=断语

    for line in lines:
        s = line.strip()
        if _TITLE.search(s) and len(s) < 80 and "占" in s:
            if cur:
                cases.append(cur)
            # 占事 = 标题里「占」之后
            zhan = s.split("占", 1)[-1].split("。")[0].strip() or "占来意"
            cur = {"title": s, "zhan": zhan, "duan": []}
            mode = "title"
            continue
        if cur is None:
            continue
        if ("曰" in s or "断" in s) and len(s) > 20:
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
            continue  # 跳过无断语的残案
        n += 1
        is_hit = any(k in duan for k in ("果", "应", "验", "卒", "遂"))
        if is_hit:
            hit += 1
        # 文件名用自增序号，避免与断案案例冲突（用 r_ 前缀）
        fname = f"r_{n:03d}_{clean(c['zhan'][:12])}.md"
        path = os.path.join(DST, fname)
        md = f"""# 案例：{c['zhan'][:20]}（大六壬）

## 基本信息
- 来源：《壬占汇选》·六壬占验案例
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
《壬占汇选》·{c['zhan'][:20]}
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    print(f"已提取 {n} 则《壬占汇选》案例到 cases/liuren/（命中 {hit}）")


if __name__ == "__main__":
    main()
