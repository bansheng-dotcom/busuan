# -*- coding: utf-8 -*-
"""紫微逐星对拍回归：zhiwei.py 排盘 vs py-iztro。

逐星对拍三硬维度——主星名、四化（mutagen）、庙旺（brightness）——必须与 iztro 一致。
辅星（天刑/红鸾/天喜等杂曜）iztro 分类在 adjective_stars/boshi12 等字段、不在 minor_stars，
属「分类口径」差异，不硬断言，仅报告。

背景：zhiwei.py 声称「算法移植自 iztro」，但 BRIGHTNESS 表曾抄错 148/168 处
（原书落宫断语「紫微午宫入庙/寅申旺地/丑未入庙」印证 iztro 对），已对齐 iztro。

运行: python tests/ziwei_iztro_regression.py
"""
import os
import sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from py_iztro import Astro
from pan import zhiwei

_ZHI = "子丑寅卯辰巳午未申酉戌亥"

_TEST = [
    (1990, 5, 15, 8, 1), (1984, 2, 4, 12, 0), (2000, 11, 11, 6, 1),
    (1976, 8, 8, 20, 0), (1965, 3, 3, 3, 0), (1955, 1, 1, 11, 1),
    (1999, 9, 9, 9, 0), (1988, 12, 12, 23, 0),
]


def _norm_sihua(m):
    return (m or "") if m is not None else ""


def main():
    diff_name = diff_sihua = diff_bright = 0
    detail = []
    for sy, sm, sd, hour, gender in _TEST:
        iz = Astro().by_solar(f"{sy}-{sm:02d}-{sd:02d}", (hour + 1) // 2 % 12,
                              "男" if gender else "女").palaces
        zw = zhiwei.cast(sy, sm, sd, hour, gender)["十二宫"]
        iz_by = {p.earthly_branch: p for p in iz}
        zw_by = {p["支"]: p for p in zw}
        for z in _ZHI:
            ip, zp = iz_by[z], zw_by[z]
            ims = [(s.name, s.brightness, _norm_sihua(s.mutagen)) for s in ip.major_stars]
            zms = [(n, b, _norm_sihua(m)) for n, b, m in zp["主星"]]
            if [n for n, b, m in ims] != [n for n, b, m in zms]:
                diff_name += 1
                detail.append((sy, z, "主星名", [n for n, b, m in ims], [n for n, b, m in zms]))
            if [m for n, b, m in ims] != [m for n, b, m in zms]:
                diff_sihua += 1
                detail.append((sy, z, "四化", ims, zms))
            if [b for n, b, m in ims] != [b for n, b, m in zms]:
                diff_bright += 1
                detail.append((sy, z, "庙旺", ims, zms))

    print(f"[紫微] 逐星对拍 {len(_TEST)} 盘 × 12 宫：zhiwei vs py-iztro")
    print(f"  主星名差异: {diff_name}")
    print(f"  四化差异:   {diff_sihua}")
    print(f"  庙旺差异:   {diff_bright}")
    if detail:
        print(f"\n  差异明细（前 6 条）：")
        for sy, z, kind, iz, zw in detail[:6]:
            print(f"    {sy} {z}宫 {kind}: iztro={iz} zhiwei={zw}")

    fail = diff_name or diff_sihua or diff_bright
    print(f"\n结果: {'失败' if fail else '通过'}（主星名/四化/庙旺 三硬维度与 iztro 一致）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
