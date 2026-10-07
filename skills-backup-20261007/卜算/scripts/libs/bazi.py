# -*- coding: utf-8 -*-
"""八字排盘（依赖 lunar_python）"""
import datetime
from lunar_python import Solar
import taiyangshi

# —— 命理神煞速查表（以日柱为主，兼看年柱）——
_TIANYI = {
    "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
    "乙": ["子", "申"], "己": ["子", "申"],
    "丙": ["亥", "酉"], "丁": ["亥", "酉"],
    "壬": ["卯", "巳"], "癸": ["卯", "巳"],
    "辛": ["寅", "午"],
}
_TAOHUA = {"申": "酉", "子": "酉", "辰": "酉", "寅": "卯", "午": "卯", "戌": "卯",
           "巳": "午", "酉": "午", "丑": "午", "亥": "子", "卯": "子", "未": "子"}
_YIMA = {"申": "寅", "子": "寅", "辰": "寅", "寅": "申", "午": "申", "戌": "申",
         "巳": "亥", "酉": "亥", "丑": "亥", "亥": "巳", "卯": "巳", "未": "巳"}
_HUAGAI = {"申": "辰", "子": "辰", "辰": "辰", "寅": "戌", "午": "戌", "戌": "戌",
           "巳": "丑", "酉": "丑", "丑": "丑", "亥": "未", "卯": "未", "未": "未"}
_JIANGXING = {"申": "子", "子": "子", "辰": "子", "寅": "午", "午": "午", "戌": "午",
              "巳": "酉", "酉": "酉", "丑": "酉", "亥": "卯", "卯": "卯", "未": "卯"}
_YANGREN = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}
_LUSHEN = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳", "己": "午",
           "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
_SHENSHA_MEANING = {
    "天乙贵人": "逢凶化吉、贵人相助", "桃花": "异性缘、情缘", "驿马": "奔波、出行、变动",
    "华盖": "孤高、才艺、玄学", "将星": "领导、掌权", "羊刃": "刚烈、防血伤", "禄神": "财禄、衣食",
}


def _shensha(b):
    """按日柱(兼年柱)推算常用神煞，返回 [(神煞, 说明)]"""
    day_gan, day_zhi = b.getDayGan(), b.getDayZhi()
    year_gan, year_zhi = b.getYearGan(), b.getYearZhi()
    hits = []

    def has(zhi):
        return zhi in (day_zhi, year_zhi)

    for g in (day_gan, year_gan):
        if any(has(z) for z in _TIANYI.get(g, [])):
            hits.append("天乙贵人")
    for name, table in (("桃花", _TAOHUA), ("驿马", _YIMA), ("华盖", _HUAGAI), ("将星", _JIANGXING)):
        if has(table.get(day_zhi)):
            hits.append(name)
    if has(_YANGREN.get(day_gan)):
        hits.append("羊刃")
    if has(_LUSHEN.get(day_gan)):
        hits.append("禄神")

    seen = []
    for n in hits:
        if n not in seen:
            seen.append(n)
    return [(n, _SHENSHA_MEANING.get(n, "")) for n in seen]


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
    ss = _shensha(b)
    print("神煞: " + ("  ".join(f"{n}({m})" for n, m in ss) if ss else "—"))
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
