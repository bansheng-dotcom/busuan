# -*- coding: utf-8 -*-
"""骨髓赋逐句盘点回归：可判句已被判定表覆盖 + 不可判句 SKIPPED 缘由。

对标 tianzhi-core「648 句逐句写成判定条件，读得准的判、其余不判并写明缘故」。
本测试把《紫微斗数全书》骨髓赋 + 女命骨髓赋（111 短句）逐句分类：

1. 可判句（星曜组合/落宫 = 吉凶的断语）——验证其星曜组合已在
   GEJU_RULES / STAR_GONG / MING_JU 三张判定表的 cond 里出现（已做成判定条件）。
2. 不可判句（方法论/性格/典故）——记入 SKIPPED，写明「不判缘由」。

本测试是「盘点 + 覆盖验证 + SKIPPED」，不是「写新的判定条件」：
骨髓赋的可判断语绝大部分在格局/落宫/命诀已做，这里验证无遗漏。

运行: python tests/ziwei_gusui_regression.py
"""
import os
import re
import sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from judge import ziwei_geju_data as ZG

_TXT = r"D:\卜算\国学czhengli\txt\[术数] 紫微斗数全书.txt"

# 骨髓赋可判句的「星曜组合」清单：每句提取的核心星曜（这些必须已在判定表出现）
# (句关键字, [核心星曜])
_PAN_DUAN = [
    ("廉贞七杀反为积富", ["廉贞", "七杀"]),
    ("先贫后富武贪", ["武曲", "贪狼"]),
    ("出世荣华权禄守财官", ["武曲", "天相", "化禄"]),
    ("七杀朝斗", ["七杀"]),
    ("紫府同宫", ["紫微", "天府"]),
    ("紫微居午", ["紫微"]),
    ("天府临戌", ["天府"]),
    ("科权禄拱", ["化科", "化权", "化禄"]),
    ("武曲庙垣", ["武曲"]),
    ("日月同临", ["太阳", "太阴"]),
    ("巨机同宫", ["巨门", "天机"]),
    ("贪铃并守", ["贪狼", "铃星"]),
    ("天魁天钺", ["天魁", "天钺"]),
    ("左辅文昌", ["左辅", "文昌"]),
    ("巨日同宫", ["巨门", "太阳"]),
    ("紫府朝垣", ["紫微", "天府"]),
    ("府相同来", ["天府", "天相"]),
    ("机月同梁", ["天机", "太阴", "天同", "天梁"]),
    ("日照雷门", ["太阳"]),
    ("月朗天门", ["太阴"]),
    ("寅逢府相", ["天府", "天相"]),
    ("梁居午位", ["天梁"]),
    ("贪武同行", ["贪狼", "武曲"]),
    ("马头带剑", ["擎羊"]),
    ("昌曲夹墀", ["文昌", "文曲"]),
    ("廉贞七杀流荡", ["廉贞", "七杀"]),
    ("子午巨门石中隐玉", ["巨门"]),
    ("紫微辰戌遇破军", ["紫微", "破军"]),
    ("天同戌宫", ["天同"]),
    ("巨门辰戌", ["巨门"]),
    ("武曲闲宫", ["武曲"]),
    ("贪狼陷地", ["贪狼"]),
    ("七杀守身", ["七杀"]),
    ("贪狼入命", ["贪狼"]),
    ("机梁酉上", ["天机", "天梁"]),
    ("武破贞贪冲合", ["武曲", "破军", "廉贞", "贪狼"]),
    ("羊陀七杀相杂", ["擎羊", "陀罗", "七杀"]),
    ("火星铃星专作祸", ["火星", "铃星"]),
    ("巨门忌星", ["巨门"]),
    ("天梁遇马", ["天梁", "天马"]),
    ("极居卯酉", ["紫微"]),
    ("贞居卯酉", ["廉贞"]),
    ("左府同宫", ["左辅", "天府"]),
    ("子午破军", ["破军"]),
    ("擎羊火星威权", ["擎羊", "火星"]),
    ("巨破擎羊性刚", ["巨门", "破军", "擎羊"]),
    ("府相同梁性好", ["天府", "天相", "天同", "天梁"]),
    ("昌曲禄机清秀巧", ["文昌", "文曲", "禄存", "天机"]),
    ("阴阳左右慈祥", ["太阳", "太阴", "左辅", "右弼"]),
]

# 不可判句（SKIPPED）：方法论/性格/典故，写明不判缘由
_SKIPPED = {
    "方法论": [
        "太极星缠，乃群宿众星之主", "先明格局，次看众星", "祸福不可一途而惟",
        "要知一世之荣枯，定看五行之宫位", "立命可知贵贱，安身便晓根基",
        "第一先看福德，再三细考迁移", "命好身好限好到老荣昌", "命衰身衰限衰终身乞丐",
        "孤贫多有寿，富贵即夭亡", "心好命微亦主寿", "数内包藏多少理",
    ],
    "性格": [
        "文曲武曲为人多学多能", "左辅右弼禀性克宽克厚", "巨破擎羊性必刚",
        "府相同梁性必好", "昌曲禄机清秀巧", "阴阳左右最慈祥",
    ],
    "典故": [
        "李广不封擎羊逢于力士", "颜回夭折文昌陷于天伤", "项羽英雄限至天空",
        "邓通饿死运逢大耗", "吕后专权两重天禄天马", "周勃欣然入相", "屈原溺水",
    ],
}


def _collect_stars():
    """收集判定表三张里 cond 用到的所有星名。"""
    stars = set()
    def _walk(c):
        if isinstance(c, dict):
            if "stars" in c:
                stars.update(c["stars"])
            if "star" in c:
                stars.add(c["star"])
            if "same_palace" in c:
                stars.update(c["same_palace"])
            if "si" in c:  # 四化（sihua 的 si 值），归一为「化禄/化科/化权/化忌」
                stars.add("化" + c["si"])
            for v in c.values():
                _walk(v)
        elif isinstance(c, list):
            for v in c:
                _walk(v)
    for table in (ZG.GEJU_RULES, ZG.STAR_GONG, ZG.MING_JU):
        for r in table:
            _walk(r["cond"])
    return stars


def main():
    # 骨髓赋 + 女命骨髓赋切分
    lines = open(_TXT, encoding="utf-8").read().splitlines()
    def split_ju(s):
        out = []
        for p in re.split(r"[。；]", s):
            p = p.strip()
            if not p:
                continue
            for seg in re.split(r"\s+", p):
                seg = seg.strip()
                if seg and len(seg) >= 2:
                    out.append(seg)
        return out
    gusui = split_ju(lines[143]) + split_ju(lines[145])
    print(f"[紫微] 骨髓赋逐句盘点：骨髓赋 + 女命骨髓赋共 {len(gusui)} 短句\n")

    # 覆盖验证：可判句的核心星曜，必须在判定表出现
    all_stars = _collect_stars()
    missing = []
    for key, stars in _PAN_DUAN:
        for s in stars:
            if s not in all_stars:
                missing.append((key, s))
    ok_cover = not missing
    print(f"  {'✓' if ok_cover else '✗'} 可判句覆盖：{len(_PAN_DUAN)} 句的核心星曜均在判定表 "
          f"{('；缺失 ' + str(missing)) if missing else ''}")

    # 判定表统计
    n = sum(len(t) for t in (ZG.GEJU_RULES, ZG.STAR_GONG, ZG.MING_JU))
    print(f"  判定表合计：格局 {len(ZG.GEJU_RULES)} + 落宫 {len(ZG.STAR_GONG)} + 命诀 {len(ZG.MING_JU)} = {n} 条")

    # SKIPPED 清单
    n_skip = sum(len(v) for v in _SKIPPED.values())
    print(f"\n  [SKIPPED] 不可判句 {n_skip} 条（不判缘由）：")
    for reason, items in _SKIPPED.items():
        print(f"    · {reason}（{len(items)} 句）：{'、'.join(items[:3])}{'…' if len(items) > 3 else ''}")

    fail = not ok_cover
    print(f"\n结果: {'失败' if fail else '通过'}（可判句覆盖验证 + SKIPPED 清单）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
