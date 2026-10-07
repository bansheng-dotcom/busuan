# -*- coding: utf-8 -*-
"""小六壬：月日时掌诀"""
import datetime

GONG = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def cast(dt=None, y=None, m=None, d=None, h=None):
    now = dt or datetime.datetime.now()
    if y is None or m is None or d is None:
        try:
            from lunardate import LunarDate
            l = LunarDate.from_solar_date(now.year, now.month, now.day)
            y, m, d = l.year, l.month, l.day
        except Exception:
            y, m, d = now.year, now.month, now.day
    if h is None:
        h = (now.hour + 1) // 2 % 12    # 时辰 0子...11亥
    pos = 0
    pos = (pos + (m - 1)) % 6
    pos = (pos + (d - 1)) % 6
    pos = (pos + h) % 6
    print(f"[小六壬] 农历{y}年{m}月{d}日 {DIZHI[h]}时")
    print(f"月->{GONG[(m - 1) % 6]}  日->{GONG[(m - 1 + d - 1) % 6]}  时->{GONG[pos]}")
    print(f"落宫: {GONG[pos]}")
    return GONG[pos]
