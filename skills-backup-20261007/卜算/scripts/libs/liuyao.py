# -*- coding: utf-8 -*-
"""六爻纳甲（金钱卦）：铜钱摇卦 + 自动装卦（纳甲/世应/六亲/六神/旬空）"""
import datetime
import random
from gua import hexagram_name, tri_to_num
import najia

NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]


def cast(dt=None):
    dt = dt or datetime.datetime.now()
    from lunar_python import Solar
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    day_gz = lunar.getDayInGanZhi()
    month_gz = lunar.getMonthInGanZhi()

    lines = []
    print("[六爻·铜钱卦] 三枚铜钱摇六次(自下而上):")
    for nm in NAMES:
        backs = sum(random.choice([0, 1]) for _ in range(3))  # 3 枚铜钱，1=背
        if backs == 3:
            r = ("阳(动)", 1)
        elif backs == 2:
            r = ("阴", 0)
        elif backs == 1:
            r = ("阳", 1)
        else:
            r = ("阴(动)", 0)
        lines.append(r)
        print(f"  {nm}: {r[0]}")
    yaos = [l[1] for l in lines]
    ben = hexagram_name(tri_to_num(yaos[3:]), tri_to_num(yaos[:3]))
    bians = [1 - x if "动" in lines[i][0] else x for i, x in enumerate(yaos)]
    bian = hexagram_name(tri_to_num(bians[3:]), tri_to_num(bians[:3]))
    dong = [i + 1 for i, l in enumerate(lines) if "动" in l[0]]
    print(f"本卦: {ben}  变卦: {bian}  动爻: {dong or '无(静卦)'}")
    print(f"占时: {lunar.toString()}  {day_gz}日  月建{month_gz}")
    r = najia.zhuang(ben, bian, dong, day_gz, month_gz)
    najia.print_zhuang(r)
    return ben, bian, dong
