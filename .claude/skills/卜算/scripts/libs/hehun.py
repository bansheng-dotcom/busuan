# -*- coding: utf-8 -*-
"""八字合婚（生肖 · 日主五行 · 纳音 · 夫妻宫）"""
import datetime
from lunar_python import Solar

_GAN = "甲乙丙丁戊己庚辛壬癸"
_ZHI = "子丑寅卯辰巳午未申酉戌亥"
_SHENGXIAO = "鼠牛虎兔龙蛇马羊猴鸡狗猪"

_HE = {frozenset("子丑"), frozenset("寅亥"), frozenset("卯戌"), frozenset("辰酉"), frozenset("巳申"), frozenset("午未")}
_CHONG = {frozenset("子午"), frozenset("丑未"), frozenset("寅申"), frozenset("卯酉"), frozenset("辰戌"), frozenset("巳亥")}
_HAI = {frozenset("子未"), frozenset("丑午"), frozenset("寅巳"), frozenset("卯辰"), frozenset("申亥"), frozenset("酉戌")}
_XING = {frozenset("子卯"), frozenset("寅巳"), frozenset("巳申"), frozenset("申寅"), frozenset("丑戌"), frozenset("戌未"), frozenset("未丑")}
_SANHE = [set("申子辰"), set("寅午戌"), set("巳酉丑"), set("亥卯未")]

_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def _shengxiao_rel(z1, z2):
    """生肖关系 -> (关系, 分)"""
    if z1 == z2:
        return "同肖", 0
    for s in _SANHE:
        if {z1, z2} <= s:
            return "三合", 3
    p = frozenset((z1, z2))
    if p in _HE:
        return "六合", 3
    if p in _CHONG:
        return "六冲", -3
    if p in _HAI:
        return "六害", -2
    if p in _XING:
        return "相刑", -2
    return "平", 0


def _wx_rel(w1, w2):
    """五行关系 -> (关系, 分)。w1 为男方日主五行。"""
    if w1 == w2:
        return "比和", 1
    if _SHENG[w1] == w2:
        return f"{w1}生{w2}(我生)", 1
    if _SHENG[w2] == w1:
        return f"{w2}生{w1}(生我)", 2
    if _KE[w1] == w2:
        return f"{w1}克{w2}(我克)", -1
    return f"{w2}克{w1}(克我)", -2


def cast(y1, m1, d1, y2, m2, d2):
    """合婚。y1/m1/d1 男方，y2/m2/d2 女方。"""
    b1 = Solar.fromYmdHms(y1, m1, d1, 12, 0, 0).getLunar().getEightChar()
    b2 = Solar.fromYmdHms(y2, m2, d2, 12, 0, 0).getLunar().getEightChar()

    z1, z2 = b1.getYearZhi(), b2.getYearZhi()
    g1, g2 = b1.getDayGan(), b2.getDayGan()
    dz1, dz2 = b1.getDayZhi(), b2.getDayZhi()
    w1, w2 = _WX[g1], _WX[g2]
    ny1, ny2 = b1.getYearNaYin(), b2.getYearNaYin()

    sx_rel, sx_score = _shengxiao_rel(z1, z2)
    wx_rel, wx_score = _wx_rel(w1, w2)
    gz_rel, gz_score = _shengxiao_rel(dz1, dz2)  # 夫妻宫(日支)关系

    # 纳音五行（取末字判断粗略五行）
    ny_w1 = ny1[-1] if ny1 else "土"
    ny_w2 = ny2[-1] if ny2 else "土"
    if ny_w1 == ny_w2:
        ny_rel, ny_score = "比和", 0
    elif ny_w1 in _SHENG and _SHENG[ny_w1] == ny_w2:
        ny_rel, ny_score = "相生", 1
    elif ny_w2 in _SHENG and _SHENG[ny_w2] == ny_w1:
        ny_rel, ny_score = "相生", 1
    elif ny_w1 in _KE and _KE[ny_w1] == ny_w2:
        ny_rel, ny_score = "相克", -1
    else:
        ny_rel, ny_score = "相克", -1

    total = sx_score + wx_score + gz_score + ny_score + 6  # 基准6分，映射0~16
    if total >= 10:
        grade = "上婚(大吉)"
    elif total >= 7:
        grade = "中婚(吉)"
    elif total >= 4:
        grade = "下婚(平)"
    else:
        grade = "不宜(凶)"

    print(f"[八字合婚]")
    print(f"男方: {b1.getYear()} 日主{b1.getDay()}({w1}) 纳音{ny1}  生肖{_SHENGXIAO[_ZHI.index(z1)]}({z1})")
    print(f"女方: {b2.getYear()} 日主{b2.getDay()}({w2}) 纳音{ny2}  生肖{_SHENGXIAO[_ZHI.index(z2)]}({z2})")
    print(f"生肖: {sx_rel}({sx_score:+d})  日主五行: {wx_rel}({wx_score:+d})  夫妻宫: {gz_rel}({gz_score:+d})  纳音: {ny_rel}({ny_score:+d})")
    print(f"综合: {total} 分 → {grade}")
    print(f"提示: 生肖六合/三合、日主相生为吉；六冲/相刑、日主相克、夫妻宫相冲宜留意。")
    return total
