# -*- coding: utf-8 -*-
"""太乙神数排盘（引擎: kentang2017/kintaiyi）"""
import datetime
from engines.taiyi.kintaiyi import Taiyi


def cast(dt=None):
    dt = dt or datetime.datetime.now()
    t = Taiyi(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    r = t.pan(0, 0)   # 年计 + 太乙统宗积年
    print(f"[太乙神数] {dt:%Y-%m-%d %H:%M}  {r.get('太乙計', '')} / {r.get('太乙公式類別', '')}")
    print(f"干支: {' '.join(r.get('干支', []))}")
    ju = r.get('局式', {})
    print(f"局式: {ju.get('文', '')}  积年数: {ju.get('積年數', '')}")
    print(f"太乙落宫: {r.get('太乙落宮', '')}({r.get('太乙', '')})  天乙: {r.get('天乙', '')}  地乙: {r.get('地乙', '')}")
    print(f"四神: {r.get('四神', '')}  直符: {r.get('直符', '')}  文昌: {r.get('文昌', '')}  始击: {r.get('始擊', '')}")
    print(f"主算: {r.get('主算', '')}  客算: {r.get('客算', '')}")
    return r
