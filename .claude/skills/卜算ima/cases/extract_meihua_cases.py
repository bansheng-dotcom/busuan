# -*- coding: utf-8 -*-
"""从典籍《梅花易数》txt 提取经典占验案例 → 本技能案例库格式。

提取观梅占/牡丹占/邻夜叩门借物占/今日动静如何/西林寺牌额占/老人有忧色占/
少年有喜色占/牛哀鸣占/鸡悲鸣占/枯枝坠地占 共 10 则康节先生占验案例。
每则含：起卦过程 + 断语（断曰/断之曰）+ 应验（果…）。

生成 cases/meihua/*.md，后验按正文是否记「果/果然/验」标记「命中」。

用法：python cases/extract_meihua_cases.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\daimajieti1\国学czhengli\txt\[易藏] 梅花易数.txt"
DST = os.path.join(HERE, "meihua")

# 案例标题（正文部分，按 txt 顺序）
TITLES = ["观梅占", "牡丹占", "邻夜叩门借物占", "今日动静如何", "西林寺牌额占",
          "老人有忧色占", "少年有喜色占", "牛哀鸣占", "鸡悲鸣占", "枯枝坠地占"]


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def main():
    os.makedirs(DST, exist_ok=True)
    text = open(SRC, encoding="utf-8").read()
    lines = text.splitlines()

    # 定位每个标题的行号
    positions = []
    for i, line in enumerate(lines):
        s = line.strip().lstrip("\u3000").strip()
        for t in TITLES:
            if s == t:
                positions.append((i, t))
                break

    # 去重（同一标题可能目录+正文各一次，取后一次即正文）
    seen = {}
    for i, t in positions:
        seen[t] = i  # 后出现覆盖前出现（正文在目录之后）
    ordered = sorted(seen.items(), key=lambda x: x[1])

    hit = 0
    for idx, (t, start) in enumerate(ordered, 1):
        # 正文：从标题行到下一个标题行
        end = len(lines)
        for _, j_line in ordered:
            if j_line > start:
                end = j_line
                break
        body = "\n".join(lines[start:end]).strip()
        is_hit = any(k in body for k in ("果", "果然", "验", "应"))
        if is_hit:
            hit += 1
        verdict = "命中" if is_hit else "未知"

        fname = f"{idx:02d}_{clean(t)}.md"
        path = os.path.join(DST, fname)
        md = f"""# 案例：{t}（梅花易数）

## 基本信息
- 来源：《梅花易数》·康节先生占验案例（观梅占系列）
- 方法：梅花易数
- 问事：{t}

## 盘面（起卦过程 + 卦象）
{body}

## 断语
{body}

## 后验
- 实际结果：古籍{'记应验（见正文「果…」句）' if is_hit else '未明记应验'}
- 判定：{verdict}
- 复盘：梅花易数体用生克 / 起卦数理 / 应期断法校准案例

## 来源
《梅花易数》·{t}（康节先生占验）
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    print(f"已提取 {len(ordered)} 则梅花案例到 cases/meihua/（命中 {hit}）")


if __name__ == "__main__":
    main()
