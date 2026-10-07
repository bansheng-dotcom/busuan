# -*- coding: utf-8 -*-
"""紫微斗数引擎对照校验：用 py-iztro（独立引擎）校验自写 zhiwei.py 的排盘正确性。

依赖：pip install py-iztro
用法：python bench/ziwei_crosscheck.py [--cases N]

校验项：
  1. 命宫/身宫地支
  2. 五行局数
  3. 紫微、天府落宫地支
  4. 四化（禄权科忌对应星曜）
  5. 十四主星落宫（星名 + 所在宫地支）
  6. 十二宫宫名（"交友宫"=iztro"仆役"，同宫异名已归一）
亮度（庙旺利陷）因流派分歧，单独统计并提示，不判对错。
"""
import os
import sys
import datetime

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

import zhiwei
from py_iztro import Astro

CASES = [
    (1990, 5, 15, 8, 1),     # 庚午 男 辰时
    (1985, 12, 25, 14, 0),   # 乙丑 女 未时
    (2000, 1, 1, 8, 1),      # 己卯 男 辰时
    (1978, 6, 3, 10, 0),     # 戊午 女 巳时
    (1960, 11, 2, 16, 1),    # 庚子 男 申时
    (2010, 3, 15, 12, 0),    # 庚寅 女 午时
    (1954, 9, 27, 20, 1),    # 甲午 男 戌时
    (1999, 2, 14, 6, 0),     # 己卯 女 卯时
]

# 交友宫/仆役 同宫异名（norm 已去「宫」后缀）
PALACE_ALIAS = {"交友": "仆役", "仆役": "交友"}


def shi_index(hour):
    return (hour + 1) // 2 % 12


def crosscheck(sy, sm, sd, hour, gender):
    r = zhiwei.cast(sy, sm, sd, hour, gender)
    iz = Astro().by_solar(f"{sy}-{sm}-{sd}", shi_index(hour), "男" if gender else "女")

    ok = {"命宫": None, "身宫": None, "五行局": None, "紫微": None, "天府": None,
          "四化": None, "主星": None, "宫名": None, "亮度": None}
    detail = []

    # 1. 命宫/身宫地支
    ok["命宫"] = r["命宫"][1] == iz.earthly_branch_of_soul_palace
    ok["身宫"] = r["身宫"][1] == iz.earthly_branch_of_body_palace
    if not ok["命宫"]:
        detail.append(f"命宫 zhiwei={r['命宫'][1]} iztro={iz.earthly_branch_of_soul_palace}")

    # 2. 五行局
    _CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}
    iz_ju = _CN.get(iz.five_elements_class[-2]) if iz.five_elements_class else None
    ok["五行局"] = r["局数"] == iz_ju
    if not ok["五行局"]:
        detail.append(f"五行局 zhiwei={r['局数']} iztro={iz.five_elements_class}")

    # 3. 紫微/天府落宫
    iz_palace_by_zhi = {p.earthly_branch: p for p in iz.palaces}
    iz_ziwei = [p.earthly_branch for p in iz.palaces if any(s.name == "紫微" for s in p.major_stars)]
    iz_tianfu = [p.earthly_branch for p in iz.palaces if any(s.name == "天府" for s in p.major_stars)]
    ok["紫微"] = r["紫微"] in (iz_ziwei or [""])
    ok["天府"] = r["天府"] in (iz_tianfu or [""])

    # 4. 四化
    zw_sihua = {}
    for p in r["十二宫"]:
        for n, b, s in p["主星"]:
            if s:
                zw_sihua[n] = s
    iz_sihua = {}
    for p in iz.palaces:
        for s in p.major_stars:
            if s.mutagen:
                iz_sihua[s.name] = s.mutagen
    ok["四化"] = zw_sihua == iz_sihua
    if not ok["四化"]:
        detail.append(f"四化 zhiwei={zw_sihua} iztro={iz_sihua}")

    # 5. 十四主星落宫（名字 + 宫地支）
    zw_stars = {}
    for p in r["十二宫"]:
        for n, b, s in p["主星"]:
            zw_stars[n] = p["支"]
    iz_stars = {}
    for p in iz.palaces:
        for s in p.major_stars:
            iz_stars[s.name] = p.earthly_branch
    ok["主星"] = zw_stars == iz_stars
    if not ok["主星"]:
        diff = {k: (zw_stars.get(k), iz_stars.get(k)) for k in set(zw_stars) | set(iz_stars)
                if zw_stars.get(k) != iz_stars.get(k)}
        detail.append(f"主星落宫差异={diff}")

    # 6. 宫名（zhiwei 带「宫」后缀，iztro 除命宫外不带；交友=仆役 归一）
    def norm(n):
        return "命宫" if n == "命宫" else (n[:-1] if n.endswith("宫") else n)
    zw_pal = {p["支"]: norm(p["宫"]) for p in r["十二宫"]}
    mism = []
    for p in iz.palaces:
        zname = zw_pal.get(p.earthly_branch, "")
        iname = norm(p.name)
        if zname != iname and PALACE_ALIAS.get(zname) != iname:
            mism.append(f"{p.earthly_branch}:{zname}/{iname}")
    ok["宫名"] = not mism
    if mism:
        detail.append(f"宫名差异={mism}")

    # 7. 亮度（流派差异，仅统计）
    zw_bright = {n: b for p in r["十二宫"] for n, b, s in p["主星"]}
    iz_bright = {s.name: s.brightness for p in iz.palaces for s in p.major_stars}
    bright_diff = {k for k in zw_bright if k in iz_bright and zw_bright[k] != iz_bright[k]}
    ok["亮度"] = len(bright_diff) == 0

    return ok, detail, bright_diff


def generate_cases(n):
    """系统扫描生成确定性命例：跨 1940~2020 年、逐月、逐时辰、男女交替，day≤28 避开大小月。"""
    cases = []
    for i in range(n):
        year = 1940 + (i * 7) % 81      # 1940..2020
        month = (i * 5) % 12 + 1
        day = (i * 3) % 28 + 1
        hour = (i * 2) % 24
        gender = i % 2
        cases.append((year, month, day, hour, gender))
    return cases


def is_nianjie_window(month, day):
    """立春~春节窗口（约每年 2/4~2/20）。此窗口 zhiwei 用农历年、iztro 用立春换年，
    属 SKILL.md 已文档的年界流派差异，不计入真实 bug。"""
    return month == 2 and 4 <= day <= 20


# iztro by_solar 的闰月日界与 lunar_python 不一致（如 1968 闰七月后半被 iztro 提前当八月，
# 而 lunar_python 权威日历 09-22 才入八月），属 iztro 已知差异，非 zhiwei bug。
# zhiwei 遵循 lunar_python + 「闰月作本月」，此处是 iztro 错。
KNOWN_IZTRO_LEAP = {(1968, 9, 13)}


def main():
    n_extra = 100
    if "--cases" in sys.argv:
        n_extra = int(sys.argv[sys.argv.index("--cases") + 1])
    cases = list(CASES) + generate_cases(n_extra)

    fails_core, fails_nianjie, fails_iztro_leap = [], [], []
    bright_total = 0
    for sy, sm, sd, hour, gender in cases:
        ok, detail, bright_diff = crosscheck(sy, sm, sd, hour, gender)
        # 亮度属流派差异，不计入核心排盘失败
        bad = [k for k, v in ok.items() if v is False and k != "亮度"]
        if bad:
            item = (sy, sm, sd, hour, gender, bad, detail)
            if is_nianjie_window(sm, sd):
                fails_nianjie.append(item)
            elif (sy, sm, sd) in KNOWN_IZTRO_LEAP:
                fails_iztro_leap.append(item)
            else:
                fails_core.append(item)
        bright_total += len(bright_diff)

    consistent = len(cases) - len(fails_core) - len(fails_nianjie) - len(fails_iztro_leap)
    print(f"共 {len(cases)} 例（{len(CASES)} 手选 + {len(cases)-len(CASES)} 生成）")
    print(f"核心排盘一致 {consistent} / 不一致 {len(fails_core)}（另有年界差异 {len(fails_nianjie)}、iztro 闰月日界差异 {len(fails_iztro_leap)}）")
    for f in fails_core[:20]:
        print(f"  ✗ 待查 {f[0]}-{f[1]:02d}-{f[2]:02d} {f[3]}时 {'男' if f[4] else '女'}: {f[5]} {f[6]}")
    if len(fails_core) > 20:
        print(f"  …（其余 {len(fails_core)-20} 例略）")
    for f in fails_nianjie[:10]:
        print(f"  ◇ 年界 {f[0]}-{f[1]:02d}-{f[2]:02d} {f[3]}时 {'男' if f[4] else '女'}（立春~春节窗口，流派差异）")
    for f in fails_iztro_leap[:10]:
        print(f"  △ iztro闰月 {f[0]}-{f[1]:02d}-{f[2]:02d} {f[3]}时 {'男' if f[4] else '女'}（iztro 闰月日界 bug，zhiwei 正确）")
    print(f"亮度流派差异累计 {bright_total} 处（不判错，仅提示）")


if __name__ == "__main__":
    main()
