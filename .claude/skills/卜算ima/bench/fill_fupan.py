# -*- coding: utf-8 -*-
"""批量补写 32 个 MingLi-Bench 案例的「复盘」段（原为「待总结」）。

依据：每个案例表格里的 类别+后验(命中/未命中)，结合 _复盘总结.md 的系统教训，
生成「命中哪些类别（有信号）、未命中哪些类别（对应哪条教训）」的逐案复盘。

用法: python bench/fill_fupan.py [--write]    # 默认 dry-run 打印，--write 才写回
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "cases", "mingli")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 类别 → 系统教训（与 cases/mingli/_复盘总结.md 一致）
CATEGORY_LESSON = {
    "学业": "学业/学历类不可从八字印星可靠推断（实测 18% 低于随机线），此类应标「不确定」，不硬断。",
    "外貌": "「五行主形」不可靠（实测 33%），外貌取象归 [SUPPLEMENTAL]，不作主断。",
    "运势": "搬迁/某年某事类属「精确年份+具体生平」，八字结构给不出确定性答案，按「不确定+低置信度」输出。",
    "性格": "性格类信号偏弱（实测 29%），宜作弱信号、不作主断。",
    "健康": "健康类相对有信号（实测 53%，含同病根重复题），可给方向但慎断具体病名/年份。",
    "事业": "事业类偏格局吉凶，八字能给出一点方向（实测 40%）。",
    "财运": "财运类偏格局吉凶，八字能给出一点方向（实测 38%）。",
    "婚姻": "婚姻类有信号（实测 34%），但「何年结婚」等精确年份类应标不确定。",
    "家庭": "家庭类（父亡年份/亲人变故）属「精确年份+具体生平」，八字给不出确定性答案。",
    "子女": "子女类样本少（6 题），信号有限，不作普适结论。",
    "灾劫": "灾劫类样本少（2 题），信号有限。",
    "官非": "官非类样本极少（1 题），不作普适结论。",
}

# 题目里含「年」字且问具体时间的，额外挂「精确年份」教训
YEAR_PATTERN = re.compile(r"何年|哪一年|那年|年份|哪年|岁运|哪(?:个|一)岁")


def parse_rows(txt):
    """解析案例表格，返回 [(类别, 题目, 后验), ...]"""
    rows = []
    for line in txt.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 7:
            continue
        if cells[0] in ("题号",) or not cells[0].startswith("ftb_"):
            continue
        cat, q, verdict = cells[1], cells[2], cells[6]
        rows.append((cat, q, verdict))
    return rows


def build_fupan(rows):
    hit_cats, miss_cats = [], []
    hit_n = miss_n = 0
    for cat, q, verdict in rows:
        v = verdict.strip()
        if v == "命中":
            hit_n += 1
            hit_cats.append(cat)
        elif v == "未命中":
            miss_n += 1
            miss_cats.append(cat)

    total = hit_n + miss_n
    rate = f"{hit_n}/{total}" if total else "0/0"

    lines = []
    lines.append(f"本案例 {total} 题：命中 {hit_n}、未命中 {miss_n}。")

    # 命中的类别
    if hit_cats:
        from collections import Counter
        hc = Counter(hit_cats)
        hit_list = "、".join(f"{c}{n}" for c, n in hc.items())
        lines.append(f"- 命中集中在：{hit_list} —— 对应「有信号」类别。")
    # 未命中的类别 + 教训
    if miss_cats:
        from collections import Counter
        mc = Counter(miss_cats)
        seen = set()
        for cat, _ in mc.most_common():
            lesson = CATEGORY_LESSON.get(cat, "该类暂无系统教训，需人工复盘。")
            if lesson in seen:
                continue
            seen.add(lesson)
            lines.append(f"- 未命中集中在「{cat}」：{lesson}")
    # 精确年份题
    year_rows = [q for cat, q, v in rows if YEAR_PATTERN.search(q) and v.strip() == "未命中"]
    if year_rows:
        lines.append("- 含「精确年份+具体生平」的未命中题（如「" + year_rows[0][:18] + "…」）：此类八字结构给不出确定性答案，一律「不确定+低置信度」，禁止硬断。")

    return "\n".join(lines)


def process(write=False):
    files = sorted(f for f in os.listdir(OUT) if f.endswith(".md"))
    changed = 0
    for f in files:
        path = os.path.join(OUT, f)
        txt = open(path, encoding="utf-8").read()
        rows = parse_rows(txt)
        if not rows:
            continue
        fupan = build_fupan(rows)
        marker = "## 复盘"
        if marker not in txt:
            continue
        head = txt.split(marker, 1)[0].rstrip()
        new_txt = head + "\n\n## 复盘\n" + fupan + "\n"
        if write:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_txt)
            changed += 1
            print(f"已写 {f}: {fupan.splitlines()[0]}")
        else:
            print(f"--- {f} ---\n{fupan}\n")
    if write:
        print(f"\n共补写 {changed} 个案例的复盘 → {OUT}")


if __name__ == "__main__":
    process(write="--write" in sys.argv)
