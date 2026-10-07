# -*- coding: utf-8 -*-
"""奇门遁甲排盘（引擎: kentang2017/kinqimen）"""
import datetime
from engines.qimen import Qimen


def cast(dt=None):
    dt = dt or datetime.datetime.now()
    q = Qimen(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    r = q.overall(2)   # 2=置闰法, 1=拆补法
    sj = r.get("時家奇門", {})
    print(f"[奇门遁甲] {dt:%Y-%m-%d %H:%M}")
    print(f"排盘: {sj.get('排盤方式', '')}  局: {sj.get('排局', '')}  节气: {sj.get('節氣', '')}")
    print(f"干支: {sj.get('干支', '')}  旬空: {sj.get('旬空', '')}")
    print(f"值符值使: {sj.get('值符值使', '')}")
    print(f"八门: {sj.get('八門', sj.get('門', ''))}")
    star = sj.get('九星', sj.get('星', '')) or {}
    if isinstance(star, dict):
        # 引擎把天芮与天禽合并为「禽」(天禽寄宫随天芮)，此处显式还原天芮，避免漏断凶星
        star = {k: ("芮·禽" if v == "禽" else v) for k, v in star.items()}
        print(f"九星: {star}（注：天禽寄宫随天芮，「芮·禽」处实为天芮+天禽同宫）")
    else:
        print(f"九星: {star}")
    return r
