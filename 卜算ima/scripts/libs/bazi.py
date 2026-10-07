# -*- coding: utf-8 -*-
"""八字排盘（依赖 lunar_python）"""
import datetime
from lunar_python import Solar
import taiyangshi
import shensha
import xingchong


def cast(y=None, mo=None, d=None, hh=0, mi=0, ss=0, gender=1, lon=None, dst=False):
    now = datetime.datetime.now()
    if y is None:
        y, mo, d, hh, mi, ss = now.year, now.month, now.day, now.hour, now.minute, now.second
    if lon is not None or dst:
        _dt0 = datetime.datetime(y, mo, d, hh, mi, ss)
        _dt0, _notes = taiyangshi.correct(_dt0, lon, dst)
        if _notes:
            print(f"[时间校正] {'；'.join(_notes)}")
        y, mo, d, hh, mi, ss = _dt0.year, _dt0.month, _dt0.day, _dt0.hour, _dt0.minute, _dt0.second
    solar = Solar.fromYmdHms(y, mo, d, hh, mi, ss)
    lunar = solar.getLunar()
    b = lunar.getEightChar()
    print(f"[八字] 公历{solar.toYmdHms()} 农历{lunar.toString()} 性别{'男' if gender else '女'}")
    print(f"四柱: {b.getYear()}  {b.getMonth()}  {b.getDay()}  {b.getTime()}")
    print(f"十神: {b.getYearShiShenGan()}  {b.getMonthShiShenGan()}  {b.getDayShiShenGan()}  {b.getTimeShiShenGan()}")
    print(f"五行: {b.getYearWuXing()}  {b.getMonthWuXing()}  {b.getDayWuXing()}  {b.getTimeWuXing()}")
    print(f"纳音: {b.getYearNaYin()}  {b.getMonthNaYin()}  {b.getDayNaYin()}  {b.getTimeNaYin()}")
    print(f"日主: {b.getDayGan()}{b.getDayZhi()}  命宫: {b.getMingGong()}  胎元: {b.getTaiYuan()}")
    print(f"日主长生: {b.getDayDiShi()}  日柱旬空: {b.getDayXunKong()}")
    print("神煞:")
    print(shensha.format_output(shensha.analyze(b, "男" if gender else "女")))
    print("刑冲合害:")
    print(xingchong.format_output(xingchong.analyze(xingchong.from_eightchar(b))))
    try:
        yun = b.getYun(gender)
        dy = yun.getDaYun()
        print(f"起运: {yun.getStartYear()}年{yun.getStartMonth()}月{yun.getStartDay()}天")
        seq = [x.getGanZhi() for x in dy if x.getGanZhi()][:8]
        print(f"大运: {' -> '.join(seq)}")
    except Exception as e:
        print(f"大运: (计算异常 {e})")
    _warn = taiyangshi.jieqi_warning(solar)
    if _warn:
        print(_warn)
    return b


# —— 流年聚合 ——
_GAN = "甲乙丙丁戊己庚辛壬癸"
_ZHI = "子丑寅卯辰巳午未申酉戌亥"
_SX = "鼠牛虎兔龙蛇马羊猴鸡狗猪"
_WX5 = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
_SHENG5 = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_KE5 = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def _ganzhi_year(year):
    return _GAN[(year - 4) % 10] + _ZHI[(year - 4) % 12]


def _liunian_rel(day_wx, year_wx):
    if day_wx == year_wx:
        return "比和·比劫"
    if _SHENG5.get(year_wx) == day_wx:
        return "生我·印"
    if _SHENG5.get(day_wx) == year_wx:
        return "我生·食伤泄"
    if _KE5.get(year_wx) == day_wx:
        return "克我·官杀"
    if _KE5.get(day_wx) == year_wx:
        return "我克·财"
    return "?"


def liunian(y=None, mo=None, d=None, gender=1, start=None, n=10):
    """流年聚合：列出 start 起 n 年的流年干支、生肖、纳音、与日主五行关系。"""
    now = datetime.datetime.now()
    if y is None:
        y, mo, d = now.year, now.month, now.day
    b = Solar.fromYmdHms(y, mo, d, 12, 0, 0).getLunar().getEightChar()
    day_gan, day_zhi = b.getDayGan(), b.getDayZhi()
    wx_day = _WX5[day_gan]
    start = start or now.year
    print(f"[八字流年] 日主 {day_gan}{day_zhi}({wx_day})  {start}~{start + n - 1} 年")
    for yr in range(start, start + n):
        gz = _ganzhi_year(yr)
        g, z = gz[0], gz[1]
        ny = Solar.fromYmdHms(yr, 7, 1, 12, 0, 0).getLunar().getYearNaYin()
        rel = _liunian_rel(wx_day, _WX5[g])
        print(f"  {yr} {gz}  生肖{_SX[_ZHI.index(z)]}  纳音{ny}  五行{_WX5[g]}  {rel}")
    return b


def liuyue(y=None, mo=None, d=None, gender=1, year=None):
    """流月聚合：列出某流年 12 个月的流月干支、纳音、与日主五行关系。"""
    now = datetime.datetime.now()
    if y is None:
        y, mo, d = now.year, now.month, now.day
    year = year or now.year
    b = Solar.fromYmdHms(y, mo, d, 12, 0, 0).getLunar().getEightChar()
    day_gan, day_zhi = b.getDayGan(), b.getDayZhi()
    wx_day = _WX5[day_gan]
    print(f"[八字流月] 日主 {day_gan}{day_zhi}({wx_day})  {year} 年流月")
    for m in range(1, 13):
        l = Solar.fromYmd(year, m, 15).getLunar()
        gz = l.getMonthInGanZhi()
        g = gz[0]
        rel = _liunian_rel(wx_day, _WX5[g])
        print(f"  {m:>2}月 {gz}  纳音{l.getMonthNaYin()}  五行{_WX5[g]}  {rel}")
    return b
