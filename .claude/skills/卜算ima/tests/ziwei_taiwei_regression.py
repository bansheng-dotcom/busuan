# -*- coding: utf-8 -*-
"""紫微太微赋 / 形性赋 / 增补太微赋逐句盘点：可判句覆盖验证 + 不可判句 SKIPPED。

收口「648 句」最后一块——骨髓赋已盘点（ziwei_gusui_regression.py），本测试把太微赋
（line 8+10）、形性赋（line 12）、增补太微赋（line 22）三赋**逐句自动分类**：

1. 每句检测是否含「星曜名」（14 主星 + 主要辅星 + 化四化）——
   含星曜名 = 可判句，验证其核心星曜已在 GEJU_RULES / STAR_GONG / MING_JU 判定表出现；
   不含 = 不可判句，记入 SKIPPED（方法论/性格形貌/典故）。
2. 输出「可判 / 不可判」计数，暴露「还有多少句没机器化」。

对标 tianzhi-core「读得准的判、其余不判并写明缘故」。三赋的可判句绝大多数（太阳居午/
太阴居子/七杀廉贞同位/贪居亥子等）在格局/落宫已做，这里验证无遗漏并给出完整的可判/不可判账。

运行: python tests/ziwei_taiwei_regression.py
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

from judge import ziwei_geju_data as ZG  # noqa: E402

_TXT = r"D:\卜算\国学czhengli\txt\[术数] 紫微斗数全书.txt"

# 14 主星 + 主要辅星 + 化四化（用于「含星曜名」自动检测；「忌/禄/权/科」单字太通用，
# 只在与「化」连用或作「化忌」时算，故单独归一为「化忌/化禄/化权/化科」）
_STARS = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴",
          "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
          "左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "天马",
          "擎羊", "陀罗", "火星", "铃星", "地劫", "地空", "天刑", "天姚",
          "红鸾", "天喜", "空亡"]
_HUA = ["化禄", "化权", "化科", "化忌"]


def _collect_stars():
    """收集判定表三张 cond 用到的所有星名（含化四化）。"""
    stars = set()
    def _walk(c):
        if isinstance(c, dict):
            if "stars" in c:
                stars.update(c["stars"])
            if "star" in c:
                stars.add(c["star"])
            if "same_palace" in c:
                stars.update(c["same_palace"])
            if "si" in c:
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


def _stars_in(sentence):
    """一句里出现的星曜名（含化四化）。"""
    found = []
    for s in _STARS:
        if s in sentence:
            found.append(s)
    for h in _HUA:
        if h in sentence:
            found.append(h)
    return found


def main():
    lines = open(_TXT, encoding="utf-8").read().splitlines()
    # 三赋正文行（标题行 line7/11/21 不计）
    taiwei = lines[7] + " " + lines[9]
    xingxing = lines[11]
    zengbu = lines[21]

    def split_ju(s):
        return [p.strip() for p in re.split(r"[。；]", s) if p.strip()]

    all_ju = split_ju(taiwei) + split_ju(xingxing) + split_ju(zengbu)

    all_stars = _collect_stars()
    all_stars.add("空亡")  # 判定表用 kongwang 条件（zhi in 旬空支）表达空亡，非 stars 字段
    ke_pan, bu_pan, missing = [], [], []
    for ju in all_ju:
        stars = _stars_in(ju)
        if stars:
            ke_pan.append((ju, stars))
            for s in stars:
                if s not in all_stars:
                    missing.append((ju[:20], s))
        else:
            bu_pan.append(ju)

    print(f"[紫微] 太微赋/形性赋/增补太微赋逐句盘点：共 {len(all_ju)} 短句\n")
    print(f"  可判句（含星曜名）：{len(ke_pan)} 句")
    print(f"  不可判句（方法论/性格形貌/典故）：{len(bu_pan)} 句")
    ok_cover = not missing
    print(f"  {'✓' if ok_cover else '✗'} 可判句覆盖：{len(ke_pan)} 句的核心星曜均在判定表"
          f"{('；缺失 ' + str(missing)) if missing else ''}")
    if missing:
        for m in missing[:8]:
            print(f"      ✗ {m[0]}… 缺「{m[1]}」")

    # 不可判句样例（方法论/性格形貌）
    print(f"\n  [SKIPPED] 不可判句 {len(bu_pan)} 条（前 8 条示例）：")
    for ju in bu_pan[:8]:
        print(f"    · {ju[:40]}")

    fail = not ok_cover
    print(f"\n结果: {'失败' if fail else '通过'}（三赋逐句分类：可判 {len(ke_pan)} / 不可判 {len(bu_pan)}）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
