# -*- coding: utf-8 -*-
"""大六壬排盘（引擎: kentang2017/kinliuren，经 engines/taiyi/kinliuren.py 复用）"""
import datetime
from lunar_python import Solar
from engines.taiyi.kinliuren import Liuren


def cast(dt=None):
    dt = dt or datetime.datetime.now()
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    day_gz = lunar.getDayInGanZhi()
    hour_gz = lunar.getTimeInGanZhi()
    jieqi = lunar.getPrevJieQi().getName()
    lr = Liuren(jieqi, lunar.getMonth(), day_gz, hour_gz)
    r = lr.result(1)
    print(f"[大六壬] {lunar.toString()} {jieqi}  {day_gz}日{hour_gz}时")
    print(f"格局: {'、'.join(r.get('格局', []))}")
    print(f"日马: {r.get('日馬', '')}  月将: {lr.moongeneral()}")
    t = r.get('三傳', {})
    print(f"三传: 初传 {t.get('初傳')} -> 中传 {t.get('中傳')} -> 末传 {t.get('末傳')}")
    print(f"四课: {r.get('四課', {})}")
    return r
