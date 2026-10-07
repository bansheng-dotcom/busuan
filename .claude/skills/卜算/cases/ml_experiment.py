# -*- coding: utf-8 -*-
"""六爻卦例机器学习实验：卦象特征 → 占事类别（多分类）。

数据：cases/liuyao/_tianji_guaili.json（381 则《增删卜易》《卜筮正宗》占验卦例）。
特征：本卦上下卦 / 变卦上下卦 / 月建地支 / 日辰地支 / 日干 / 书号。
标签：占事类别（9 类：病/财求/天时/子息/官讼/出行/婚姻/宅/其他）。
算法：逻辑回归 / 决策树 / 随机森林 / SVM / 朴素贝叶斯 / KNN / 梯度提升。
评估：分层 5 折交叉验证，对比随机基线（多数类占比）。

诚实目标：看「卦象是否携带占事信息」。若准确率 ≈ 随机基线，说明卦象本身不编码占事类别。
用法：python cases/ml_experiment.py
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 卦名 → (上卦, 下卦)
GUA64 = {
    (1, 1): "乾为天", (2, 2): "兑为泽", (3, 3): "离为火", (4, 4): "震为雷",
    (5, 5): "巽为风", (6, 6): "坎为水", (7, 7): "艮为山", (8, 8): "坤为地",
    (6, 4): "水雷屯", (7, 6): "山水蒙", (6, 1): "水天需", (1, 6): "天水讼",
    (8, 6): "地水师", (6, 8): "水地比", (5, 1): "风天小畜", (1, 5): "天风姤",
    (2, 8): "泽地萃", (8, 2): "地泽临", (3, 1): "火天大有", (1, 3): "天火同人",
    (4, 8): "雷地豫", (8, 4): "地雷复", (7, 5): "山风蛊", (5, 7): "风山渐",
    (1, 8): "天地否", (8, 1): "地天泰", (7, 1): "山天大畜", (1, 7): "天山遁",
    (4, 3): "雷火丰", (3, 4): "火雷噬嗑", (5, 3): "风火家人", (3, 5): "火风鼎",
    (4, 1): "雷天大壮", (1, 4): "天雷无妄", (6, 3): "水火既济", (3, 6): "火水未济",
    (2, 1): "泽天夬", (1, 2): "天泽履", (5, 6): "风水涣", (6, 5): "水风井",
    (7, 3): "山火贲", (3, 7): "火山旅", (4, 7): "雷山小过", (7, 4): "山雷颐",
    (2, 3): "泽火革", (3, 2): "火泽睽", (5, 4): "风雷益", (4, 5): "雷风恒",
    (6, 2): "水泽节", (2, 6): "泽水困", (8, 5): "地风升", (5, 8): "风地观",
    (7, 2): "山泽损", (2, 7): "泽山咸", (8, 3): "地火明夷", (3, 8): "火地晋",
    (4, 6): "雷水解", (6, 7): "水山蹇", (8, 7): "地山谦", (7, 8): "山地剥",
    (4, 2): "雷泽归妹", (2, 4): "泽雷随", (5, 2): "风泽中孚", (2, 5): "泽风大过",
    (6, 1): "水天需", (1, 6): "天水讼", (5, 6): "风水涣", (6, 5): "水风井",
}
# 补齐可能的卦名异写（去重后 64 卦）
_GUA_TO_TRI = {name: (s, x) for (s, x), name in GUA64.items()}

DIZHI = "子丑寅卯辰巳午未申酉戌亥"
TIANGAN = "甲乙丙丁戊己庚辛壬癸"


def parse_ganzhi(gz):
    """'辰月戊申日' → (月建地支, 日干, 日支)"""
    m = re.search(r"([子丑寅卯辰巳午未申酉戌亥])月([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])日", gz)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None, None, None


def classify_zhanshi(z):
    if any(k in z for k in ("病", "疾", "医")):
        return "病"
    if any(k in z for k in ("财", "店", "求", "卖", "买", "钱")):
        return "财求"
    if any(k in z for k in ("婚", "妻", "夫", "嫁", "娶")):
        return "婚姻"
    if any(k in z for k in ("官", "讼", "刑", "狱", "词")):
        return "官讼"
    if any(k in z for k in ("出", "行", "归", "逃", "走")):
        return "出行"
    if any(k in z for k in ("宅", "家", "屋", "迁")):
        return "宅"
    if any(k in z for k in ("雨", "晴", "雪", "风", "天")):
        return "天时"
    if any(k in z for k in ("子", "孕", "产", "胎", "嗣", "生")):
        return "子息"
    return "其他"


def load_data():
    d = json.load(open(os.path.join(HERE, "liuyao", "_tianji_guaili.json"), encoding="utf-8"))
    rows = []
    for c in d["卦例"]:
        gua = c.get("卦名", "")
        bian = c.get("变卦", "")
        yz, rg, rz = parse_ganzhi(c.get("干支", ""))
        s, x = _GUA_TO_TRI.get(gua, (None, None))
        bs, bx = _GUA_TO_TRI.get(bian, (None, None))
        if s is None or bs is None:
            continue
        rows.append({
            "本上": s, "本下": x, "变上": bs, "变下": bx,
            "月建": DIZHI.index(yz) + 1 if yz else 0,
            "日支": DIZHI.index(rz) + 1 if rz else 0,
            "日干": TIANGAN.index(rg) + 1 if rg else 0,
            "书号": c.get("书号", 0),
            "类别": classify_zhanshi(c.get("占事", "")),
        })
    df = pd.DataFrame(rows)
    return df


def main():
    df = load_data()
    print(f"样本数: {len(df)}")
    print("类别分布:")
    print(df["类别"].value_counts().to_string())
    print()

    X = pd.get_dummies(df.drop(columns=["类别"]))
    y = df["类别"]

    # 随机基线 = 多数类占比
    baseline = df["类别"].value_counts(normalize=True).max()
    print(f"随机基线（多数类占比）: {baseline:.1%}\n")

    models = {
        "逻辑回归": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "决策树": DecisionTreeClassifier(max_depth=5, random_state=0),
        "随机森林": RandomForestClassifier(n_estimators=200, random_state=0),
        "SVM": make_pipeline(StandardScaler(), SVC()),
        "朴素贝叶斯": GaussianNB(),
        "KNN": KNeighborsClassifier(n_neighbors=7),
        "梯度提升": GradientBoostingClassifier(random_state=0),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    print(f"{'算法':<10} {'5折准确率':>12} {'相对基线':>12}")
    print("-" * 40)
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
        results[name] = scores.mean()
        print(f"{name:<10} {scores.mean():>11.1%} {scores.mean()/baseline:>11.2f}×")

    best = max(results, key=results.get)
    print(f"\n最佳算法: {best}（{results[best]:.1%}），基线 {baseline:.1%}")
    print("结论：若各算法准确率 ≈ 基线，说明卦象结构本身不编码「占事类别」信息。")

    # 随机森林特征重要性（可解释性）
    rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X, y)
    imp = sorted(zip(X.columns, rf.feature_importances_), key=lambda t: -t[1])
    print("\n特征重要性 Top 10:")
    for name, v in imp[:10]:
        print(f"  {name}: {v:.3f}")


if __name__ == "__main__":
    main()
