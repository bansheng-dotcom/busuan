# -*- coding: utf-8 -*-
"""MingLi-Bench 本地评测 runner。

解析案例库 `八字紫微/` 下的 benchmark 表（题号/类别/题目/选项/预注册预测/标准答案/后验），
算「我们记录的预测」分品类/总体命中率，并对照随机基线(25%)与众数基线，把 SKILL.md 里
引用的「MingLi-Bench 160 题 36.2%」变成一个本地可复现、可回填的活数字。

用法:
  python libs/mingli_eval.py                  # 评测全部案例
  python libs/mingli_eval.py --cat 健康       # 只看某类
  import mingli_eval; mingli_eval.analyze()

诚实边界：本 runner 只统计「已填写的预注册预测 vs 标准答案」，不代答；预测为空则计「未预测」。
"""
import os
import sys
from collections import Counter, defaultdict

CASE_DIR = r"D:\卜算\国学czhengli\txt\案例库"
BAZI_DIR = os.path.join(CASE_DIR, "八字紫微")

# 有信号 / 无信号 分类（据 SKILL.md 第十五节 MingLi-Bench 实测）
_SIGNAL = {
    "健康": True, "事业": True, "财运": True, "家庭": True, "婚姻": True,
    "学历": False, "学业": False, "性格": False, "外貌": False, "精确年份": False,
}


def parse_cases(case_dir=None):
    """解析 benchmark 表，返回 [{题号,类别,题目,选项,预测,答案,后验,命中,案例}]。"""
    base = case_dir or BAZI_DIR
    rows = []
    if not os.path.isdir(base):
        print(f"[mingli_eval] 案例目录不存在：{base}")
        return rows
    for f in sorted(os.listdir(base)):
        if not f.endswith(".md"):
            continue
        try:
            txt = open(os.path.join(base, f), encoding="utf-8").read()
        except Exception:
            continue
        for line in txt.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 7 or cells[0] in ("题号",):
                continue
            qid = cells[0]
            if not (qid.startswith(("ftb", "mlb", "mb")) or qid[0].isdigit()):
                continue
            cat, q, opts, pred, ans, houyan = cells[1], cells[2], cells[3], cells[4], cells[5], cells[6]
            ans = ans.strip("*")
            rows.append({
                "题号": qid, "类别": cat, "题目": q, "选项": opts,
                "预测": pred, "答案": ans, "后验": houyan,
                "命中": (pred and pred == ans),
                "未预测": not pred,
                "案例": f,
            })
    return rows


def evaluate(rows):
    """分品类/总体命中率 + 随机/众数基线。返回 dict。"""
    total = len(rows)
    if total == 0:
        return {"总题数": 0, "命中": 0, "未预测": 0, "总体命中率": 0.0, "类别": {}, "随机基线": 0.25, "众数基线": 0.0}
    hit = sum(1 for r in rows if r["命中"])
    unpred = sum(1 for r in rows if r["未预测"])
    # 分品类
    cat_rows = defaultdict(list)
    for r in rows:
        cat_rows[r["类别"]].append(r)
    cat_stat = {}
    for cat, rs in sorted(cat_rows.items()):
        cat_stat[cat] = {
            "题数": len(rs),
            "命中": sum(1 for r in rs if r["命中"]),
            "命中率": round(sum(1 for r in rs if r["命中"]) / len(rs), 3),
            "有信号": _SIGNAL.get(cat, None),
        }
    # 众数基线：每品类恒猜该品类众数答案
    cat_mode = {}
    for cat, rs in cat_rows.items():
        cat_mode[cat] = Counter(r["答案"] for r in rs).most_common(1)[0][0]
    mode_hit = sum(1 for r in rows if cat_mode[r["类别"]] == r["答案"])
    # 有信号组 / 无信号组
    sig_hit = sum(1 for r in rows if r["命中"] and _SIGNAL.get(r["类别"]) is True)
    sig_total = sum(1 for r in rows if _SIGNAL.get(r["类别"]) is True)
    nosig_hit = sum(1 for r in rows if r["命中"] and _SIGNAL.get(r["类别"]) is False)
    nosig_total = sum(1 for r in rows if _SIGNAL.get(r["类别"]) is False)
    return {
        "总题数": total, "命中": hit, "未预测": unpred,
        "总体命中率": round(hit / max(total - unpred, 1), 3) if total else 0.0,
        "类别": cat_stat,
        "随机基线": 0.25,
        "众数基线": round(mode_hit / total, 3) if total else 0.0,
        "有信号组": {"命中": sig_hit, "题数": sig_total,
                     "命中率": round(sig_hit / sig_total, 3) if sig_total else 0.0},
        "无信号组": {"命中": nosig_hit, "题数": nosig_total,
                     "命中率": round(nosig_hit / nosig_total, 3) if nosig_total else 0.0},
    }


def analyze(case_dir=None, cat_filter=None):
    """评测并打印报告。返回 (rows, stat)。"""
    rows = parse_cases(case_dir)
    if cat_filter:
        rows = [r for r in rows if r["类别"] == cat_filter]
    stat = evaluate(rows)
    print(f"[MingLi-Bench 本地评测] 共 {stat['总题数']} 题（未预测 {stat['未预测']} 题不计入命中率）")
    print(f"  总体命中率 {stat['总体命中率']:.1%}  | 随机基线 {stat['随机基线']:.0%}  | 众数基线 {stat['众数基线']:.1%}")
    if stat.get("有信号组", {}).get("题数"):
        g = stat["有信号组"]
        print(f"  有信号组（健康/事业/财运/家庭/婚姻）：{g['命中']}/{g['题数']} = {g['命中率']:.1%}")
    if stat.get("无信号组", {}).get("题数"):
        g = stat["无信号组"]
        print(f"  无信号组（学历/性格/外貌/精确年份）：{g['命中']}/{g['题数']} = {g['命中率']:.1%}")
    print("  分品类：")
    for cat, s in sorted(stat["类别"].items()):
        tag = "有信号" if s["有信号"] else ("无信号" if s["有信号"] is False else "未标")
        print(f"    {cat:<6} {s['命中']}/{s['题数']} = {s['命中率']:.0%}  [{tag}]")
    return rows, stat


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    _filter = None
    args = sys.argv[1:]
    if "--cat" in args:
        i = args.index("--cat")
        if i + 1 < len(args):
            _filter = args[i + 1]
    analyze(cat_filter=_filter)
