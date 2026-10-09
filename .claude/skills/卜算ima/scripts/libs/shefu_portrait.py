# -*- coding: utf-8 -*-
"""射覆·特征画像引擎（借鉴 henrryjoke/shefu）——从卦象/课式信号生成「特征画像」。

原则：「AI 是画师不是鉴定师——刻画特征，命名权交给玩家。」

用法:
  python libs/shefu_portrait.py liuren 青龙 朱雀 天后     # 大六壬：传天将名
  python libs/shefu_portrait.py meihua 离 兑             # 梅花：传八卦名
  python libs/shefu_portrait.py update '{"命中":[...],"错误":[...]}'  # 后验回填

核心函数:
  portrait(signals)      -> 特征画像（6维度 × 置信度🟢🟡🔴）
  portrait_liuren(list)  -> 大六壬信号 -> 画像
  portrait_meihua(list)  -> 梅花信号 -> 画像
  update_kb(round_json)  -> 回填 类象库.json 的 confidence + validations
"""
import os
import json
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(HERE, "..", "..", "data", "类象库.json")

_DIMS = ["颜色", "材质", "形态", "功能", "结构", "性质"]


def _load():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


def _conf_level(c):
    if c >= 0.7:
        return "🟢"
    if c >= 0.4:
        return "🟡"
    return "🔴"


def portrait(signals):
    """signals: [(名称, 权重), ...]（天将名或八卦名）。返回特征画像 dict。"""
    kb = _load()
    tianjiang = kb.get("天将", {})
    bagua = kb.get("八卦", {})
    agg = {d: {} for d in _DIMS}
    used = 0
    for name, w in signals:
        node = tianjiang.get(name) or bagua.get(name)
        if not node:
            continue
        used += 1
        for dim, vals in node.get("dimensions", {}).items():
            if dim not in agg:
                continue
            for v in vals:
                score = v["confidence"] * w
                agg[dim][v["value"]] = max(agg[dim].get(v["value"], 0.0), score)
    out = {}
    for dim in _DIMS:
        items = sorted(agg[dim].items(), key=lambda x: -x[1])
        if not items:
            out[dim] = [("—", "🔴", "需类象库")]
            continue
        out[dim] = [(val, _conf_level(sc), round(sc, 2)) for val, sc in items[:2]]
    return {"signals": [s[0] for s in signals], "used": used, "dimensions": out}


def portrait_liuren(tianjiang_list):
    """大六壬：天将名列表（初传在前、权重高）。"""
    w = {tianjiang_list[0]: 1.0} if tianjiang_list else {}
    sig = []
    for i, t in enumerate(tianjiang_list):
        weight = 1.0 if i == 0 else 0.6
        sig.append((t, weight))
    return portrait(sig)


def portrait_meihua(gua_list):
    """梅花：八卦名列表（用卦在前、权重高）。"""
    sig = [(g, 1.0 if i == 0 else 0.7) for i, g in enumerate(gua_list)]
    return portrait(sig)


def update_kb(round_json):
    """后验回填：round_json = {"命中":[{"类":"天将/八卦","名":"朱雀","维度":"颜色","值":"红"}],
       "错误":[...]}。命中 confidence+0.1(上限1)、validations+1；错误 confidence-0.1(下限0)。"""
    kb = _load()
    for tag in ("命中", "错误"):
        delta = 0.1 if tag == "命中" else -0.1
        for item in round_json.get(tag, []):
            kind = item.get("类", "天将")
            name = item.get("名")
            dim = item.get("维度")
            val = item.get("值")
            if name not in kb.get(kind, {}):
                continue
            for v in kb[kind][name].get("dimensions", {}).get(dim, []):
                if v["value"] == val:
                    v["confidence"] = round(max(0.0, min(1.0, v["confidence"] + delta)), 2)
                    v["validations"] = v.get("validations", 0) + 1
    kb["_meta"]["total_validations"] = kb["_meta"].get("total_validations", 0) + 1
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    return {"updated": True, "total_validations": kb["_meta"]["total_validations"]}


def _fmt(p):
    lines = [f"🔬 特征画像（命中信号 {p['used']}/{len(p['signals'])}）"]
    for dim in _DIMS:
        vals = p["dimensions"][dim]
        s = " / ".join(f"{v[1]} {v[0]}" for v in vals)
        lines.append(f"  {dim}  {s}")
    return "\n".join(lines)


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    if cmd == "liuren":
        print(_fmt(portrait_liuren(a[1:])))
    elif cmd == "meihua":
        print(_fmt(portrait_meihua(a[1:])))
    elif cmd == "update":
        data = json.loads(a[1] if len(a) > 1 else "{}")
        print(update_kb(data))
    else:
        print(_fmt(portrait([(x, 1.0) for x in a])))


if __name__ == "__main__":
    main()
