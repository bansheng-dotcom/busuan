# -*- coding: utf-8 -*-
"""把盲答结果回填案例库（预注册预测 + 后验四态），并生成复盘总结。"""
import os
import sys
import json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
OUT = os.path.join(SKILL, "cases", "mingli")
DATA = os.path.join(HERE, "mingli_bench_data.json")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 我的盲答（160 题）
MY = {
 'ftb_0001':'C','ftb_0002':'D','ftb_0003':'C','ftb_0004':'B','ftb_0005':'B',
 'ftb_0006':'C','ftb_0007':'D','ftb_0008':'B','ftb_0009':'A','ftb_0010':'B',
 'ftb_0011':'B','ftb_0012':'C','ftb_0013':'A','ftb_0014':'B','ftb_0015':'C',
 'ftb_0016':'C','ftb_0017':'A','ftb_0018':'C','ftb_0019':'A','ftb_0020':'D',
 'ftb_0021':'C','ftb_0022':'D','ftb_0023':'B','ftb_0024':'B','ftb_0025':'A',
 'ftb_0026':'A','ftb_0027':'B','ftb_0028':'C','ftb_0029':'C','ftb_0030':'B',
 'ftb_0031':'A','ftb_0032':'B','ftb_0033':'A','ftb_0034':'B','ftb_0035':'B',
 'ftb_0036':'C','ftb_0037':'C','ftb_0038':'A','ftb_0039':'A','ftb_0040':'C',
 'ftb_0041':'C','ftb_0042':'A','ftb_0043':'B','ftb_0044':'C','ftb_0045':'D',
 'ftb_0046':'C','ftb_0047':'A','ftb_0048':'A','ftb_0049':'C','ftb_0050':'D',
 'ftb_0051':'C','ftb_0052':'C','ftb_0053':'C','ftb_0054':'C','ftb_0055':'A',
 'ftb_0056':'D','ftb_0057':'C','ftb_0058':'B','ftb_0059':'D','ftb_0060':'A',
 'ftb_0061':'A','ftb_0062':'A','ftb_0063':'C','ftb_0064':'A','ftb_0065':'B',
 'ftb_0066':'C','ftb_0067':'B','ftb_0068':'C','ftb_0069':'C','ftb_0070':'B',
 'ftb_0071':'B','ftb_0072':'A','ftb_0073':'A','ftb_0074':'D','ftb_0075':'C',
 'ftb_0076':'D','ftb_0077':'C','ftb_0078':'B','ftb_0079':'C','ftb_0080':'D',
 'ftb_0081':'C','ftb_0082':'C','ftb_0083':'D','ftb_0084':'C','ftb_0085':'B',
 'ftb_0086':'D','ftb_0087':'D','ftb_0088':'B','ftb_0089':'C','ftb_0090':'C',
 'ftb_0091':'D','ftb_0092':'D','ftb_0093':'B','ftb_0094':'A','ftb_0095':'A','ftb_0096':'D',
 'ftb_0097':'C','ftb_0098':'A','ftb_0099':'C','ftb_0100':'C',
 'ftb_0101':'C','ftb_0102':'B','ftb_0103':'B','ftb_0104':'A','ftb_0105':'C',
 'ftb_0106':'C','ftb_0107':'D','ftb_0108':'B','ftb_0109':'B','ftb_0110':'A',
 'ftb_0111':'C','ftb_0112':'D','ftb_0113':'D','ftb_0114':'C','ftb_0115':'D',
 'ftb_0116':'B','ftb_0117':'B','ftb_0118':'A','ftb_0119':'C','ftb_0120':'B',
 'ftb_0121':'C','ftb_0122':'B','ftb_0123':'C','ftb_0124':'A','ftb_0125':'B',
 'ftb_0126':'A','ftb_0127':'A','ftb_0128':'D','ftb_0129':'C','ftb_0130':'D',
 'ftb_0131':'B','ftb_0132':'C','ftb_0133':'B','ftb_0134':'B','ftb_0135':'C',
 'ftb_0136':'B','ftb_0137':'C','ftb_0138':'D','ftb_0139':'A','ftb_0140':'B',
 'ftb_0141':'D','ftb_0142':'D','ftb_0143':'A','ftb_0144':'A','ftb_0145':'B',
 'ftb_0146':'C','ftb_0147':'C','ftb_0148':'A','ftb_0149':'A','ftb_0150':'D',
 'ftb_0151':'B','ftb_0152':'B','ftb_0153':'A','ftb_0154':'C','ftb_0155':'A',
 'ftb_0156':'C','ftb_0157':'A','ftb_0158':'B','ftb_0159':'C','ftb_0160':'A',
}


def main():
    with open(DATA, encoding="utf-8") as f:
        qs = json.load(f)["questions"]
    by_id = {q["id"]: q for q in qs}
    cases = {}
    for q in qs:
        cases.setdefault(q["case_id"], []).append(q)

    right = 0
    total = 0
    by_cat = Counter()
    by_cat_r = Counter()

    for cid in sorted(cases):
        path = os.path.join(OUT, f"{cid}.md")
        with open(path, encoding="utf-8") as f:
            txt = f.read()
        for q in cases[cid]:
            mine = MY.get(q["id"], "?")
            ok = mine == q["answer"]
            total += 1
            right += ok
            by_cat[q["category"]] += 1
            by_cat_r[q["category"]] += ok
            verdict = "命中" if ok else "未命中"
            # 替换该行的 预注册预测(待填) 与 后验(待填)
            txt = txt.replace(f"| {q['id']} | {q['category']} |", f"| {q['id']} | {q['category']} |", 1)
            # 预注册预测列：第6列；后验列：第8列。用题目行内「待填」定位
            row = next((l for l in txt.split("\n") if l.startswith(f"| {q['id']} |")), None)
            if row:
                cells = row.split("|")
                # cells: ['', ' ftb_x ', ' 类别 ', ' 题目 ', ' 选项 ', ' 待填 ', ' **答案** ', ' 待填 ', '']
                if len(cells) >= 9:
                    cells[5] = f" {mine} "
                    cells[7] = f" {verdict} "
                    new_row = "|".join(cells)
                    txt = txt.replace(row, new_row, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)

    # 复盘总结
    summary = [f"# MingLi-Bench 全量盲测复盘", ""]
    summary.append(f"- 总成绩：{right}/{total} = {right/total*100:.1f}%（随机线 25%，人类 Top-20 约 53.5%）")
    summary.append(f"- 样本：{len(cases)} case / {total} 题，盲答后回填后验")
    summary.append("")
    summary.append("## 分类别命中率")
    summary.append("| 类别 | 命中 | 有信号？ |")
    summary.append("|---|---|---|")
    for c, n in by_cat.most_common():
        r = by_cat_r[c]
        signal = "有" if r/n > 0.33 else ("弱" if r/n > 0.25 else "无/负")
        summary.append(f"| {c} | {r}/{n} = {r/n*100:.0f}% | {signal} |")
    summary.append("")
    summary.append("## 系统教训（写进规则的）")
    summary.append("1. 排盘是确定可靠的（32 项回归全过）；「断具体某年何事/何年结婚/父亡年份」的推理上限约 36%，接近强模型天花板，任何八字结构都给不出确定性答案。")
    summary.append("2. **学历（学业 18%）不可从八字印星可靠推断**——低于随机，此类题应标「不确定」，不得硬断。")
    summary.append("3. **「五行主形」（如甲木主高挑）不可靠**——外貌类取象应归 `[SUPPLEMENTAL]`，不作主断。")
    summary.append("4. 夫妻宫单一化忌（如太阳化忌）≠ 不婚/单身，只主迟婚波折。")
    summary.append("5. 有相对信号的类别仅「健康」（53%，但含同病根重复题）与「事业/财运」（38-40%）——偏格局吉凶，八字能给出一点方向。")
    summary.append("6. 结论口径：凡「精确年份+具体生平」类问题，一律按『不确定 + 置信度低』输出，禁止装作有把握。")
    with open(os.path.join(OUT, "_复盘总结.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")

    print(f"回填完成：{right}/{total} = {right/total*100:.1f}%")
    print(f"复盘总结已写：{os.path.join(OUT, '_复盘总结.md')}")


if __name__ == "__main__":
    main()
