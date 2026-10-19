# -*- coding: utf-8 -*-
"""把 MingLi-Bench 全部 160 题生成案例库文件（按 case 分文件，32 个）。

每文件含：盘面（脚本起盘）+ 5 题的题目/选项/标准答案 + 预注册预测(留空待填) + 后验(四态)。

用法: python bench/gen_casebook.py   # 生成 cases/mingli/ 下 32 个文件
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
LIB = os.path.join(SKILL, "scripts", "libs")
OUT = os.path.join(SKILL, "cases", "mingli")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


def bazi_summary(y, m, d, h, mi, g):
    from lunar_python import Solar
    b = Solar.fromYmdHms(y, m, d, h, mi, 0).getLunar().getEightChar()
    yun = b.getYun(g)
    dy = yun.getDaYun()
    seq = [x.getGanZhi() for x in dy if x.getGanZhi()][:6]
    return (f"{b.getYear()} {b.getMonth()} {b.getDay()} {b.getTime()}  "
            f"十神:{b.getYearShiShenGan()}/{b.getMonthShiShenGan()}/{b.getDayShiShenGan()}/{b.getTimeShiShenGan()}  "
            f"日主{b.getDayGan()}{b.getDayZhi()}({b.getDayWuXing()})  "
            f"起运{yun.getStartYear()}年  大运{'→'.join(seq)}")


def zhiwei_summary(y, m, d, h, g):
    import zhiwei
    r = zhiwei.cast(y, m, d, h, g)
    fq = next((p for p in r["十二宫"] if p["宫"] == "夫妻宫"), None)
    fq_txt = ""
    if fq:
        mains = " ".join(n for n, b, s in fq["主星"]) or "空"
        fus = " ".join(fq["辅星"]) or "—"
        fq_txt = f"夫妻宫{fq['干']}{fq['支']}: {mains} / {fus}"
    return (f"命宫{r['命宫']} 身宫{r['身宫']} {r['五行局']} 紫微在{r['紫微']}天府在{r['天府']}  "
            f"四化{r['四化']}  {fq_txt}")


def main():
    with open(os.path.join(HERE, "mingli_bench_data.json"), encoding="utf-8") as f:
        qs = json.load(f)["questions"]
    os.makedirs(OUT, exist_ok=True)

    cases = {}
    for q in qs:
        cases.setdefault(q["case_id"], []).append(q)

    for cid in sorted(cases):
        cqs = cases[cid]
        bi = cqs[0]["birth_info"]
        y, m, d, h, mi = bi["year"], bi["month"], bi["day"], bi["hour"], bi["minute"]
        g = 1 if bi.get("gender") == "男" else 0
        lines = [f"# 案例：MingLi-Bench {cid}", ""]
        lines.append(f"- 出生：{bi.get('raw')}  性别：{bi.get('gender')}")
        lines.append(f"- 盘面（八字）：{bazi_summary(y, m, d, h, mi, g)}")
        lines.append(f"- 盘面（紫微）：{zhiwei_summary(y, m, d, h, g)}")
        lines.append("")
        lines.append("| 题号 | 类别 | 题目 | 选项 | 预注册预测 | 标准答案 | 后验 |")
        lines.append("|---|---|---|---|---|---|---|")
        for q in cqs:
            opts = " ".join(f"{o['letter']}.{o['text']}" for o in q["options"])
            q_text = q["question"].replace("|", "｜")
            lines.append(f"| {q['id']} | {q['category']} | {q_text} | {opts} | 待填 | **{q['answer']}** | 待填 |")
        lines.append("")
        lines.append("## 复盘")
        lines.append("- 待总结")
        with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"生成 {cid}.md ({len(cqs)} 题)")

    print(f"\n共 {len(cases)} case / {len(qs)} 题 → {OUT}")


if __name__ == "__main__":
    main()
