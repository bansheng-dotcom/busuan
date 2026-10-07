# -*- coding: utf-8 -*-
"""梅花易数：时间起卦 / 数字起卦"""
import datetime
from gua import GUA, YAO, WX, gua_num, hexagram_name, tri_to_num, wx_rel

DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


def cast_time(dt=None):
    now = dt or datetime.datetime.now()
    try:
        from lunardate import LunarDate
        l = LunarDate.from_solar_date(now.year, now.month, now.day)
        m, d = l.month, l.day
    except Exception:
        m, d = now.month, now.day
    shi = (now.hour + 1) // 2 % 12
    n_year = (now.year - 4) % 12 + 1       # 年支数(子1...亥12)
    n_shi = shi + 1
    return _calc(n_year, m, d, n_shi,
                 note=f"公历{now:%Y-%m-%d %H:%M} 农历{now.year}年{m}月{d}日 {DIZHI[shi]}时")


def cast_num(nums):
    nums = [int(x) for x in nums]
    if len(nums) == 1:
        return _calc(nums[0], 0, 0, 0, note=f"单数起卦: {nums[0]}")
    if len(nums) == 2:
        a, b = nums
        return _build(gua_num(a), gua_num(b), gua_num(a + b) % 6 or 6,
                      note=f"数字起卦: {a},{b}")
    a, b, c = nums
    return _build(gua_num(a), gua_num(b), c % 6 or 6,
                  note=f"数字起卦: {a},{b},{c}")


def _calc(n_year, m, d, n_shi, note=""):
    shang = gua_num(n_year + m + d)
    xia = gua_num(n_year + m + d + n_shi)
    dong = (n_year + m + d + n_shi) % 6 or 6
    return _build(shang, xia, dong, note=note)


def _build(shang, xia, dong, note=""):
    ben = hexagram_name(shang, xia)
    liu = YAO[xia] + YAO[shang]                  # 本卦六爻(自下而上)
    hu_xia = tri_to_num(liu[1:4])                # 下互=二三四
    hu_shang = tri_to_num(liu[2:5])              # 上互=三四五
    hu = hexagram_name(hu_shang, hu_xia)
    liu2 = list(liu); liu2[dong - 1] ^= 1        # 动爻变
    bian_xia = tri_to_num(tuple(liu2[:3]))
    bian_shang = tri_to_num(tuple(liu2[3:]))
    bian = hexagram_name(bian_shang, bian_xia)
    yong, ti = (xia, shang) if dong <= 3 else (shang, xia)  # 动为用、静为体
    sheng = wx_rel(WX[yong], WX[ti])
    print(f"[梅花易数] {note}")
    print(f"本卦: {ben}（{GUA[shang]}上 {GUA[xia]}下）")
    print(f"动爻: 第{dong}爻")
    print(f"互卦: {hu}")
    print(f"变卦: {bian}")
    print(f"体用: 体={GUA[ti]}({WX[ti]}) 用={GUA[yong]}({WX[yong]})  -> {sheng}")
    return ben, hu, bian, dong
