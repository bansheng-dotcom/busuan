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


# ---------------------------------------------------------------------------
# 后天起卦（触机）：物数占 / 声音占 / 字占 / 端法（物+方位）
# 据《梅花易数》卷一「物数占例 / 声音占例 / 字占 / 物卦起例(端法)」
# 时数：子=1 ... 亥=12（与年月日时起例同）
# ---------------------------------------------------------------------------
def _shichen(dt=None):
    now = dt or datetime.datetime.now()
    shi = (now.hour + 1) // 2 % 12
    return shi + 1


def _to_gua(x):
    """数字/卦名/方位名/五行名 -> 卦数 1-8（先天数：乾1兑2离3震4巽5坎6艮7坤8）"""
    if isinstance(x, int):
        return gua_num(x)
    s = str(x).strip()
    if s.isdigit():
        return gua_num(int(s))
    m = {"乾": 1, "兑": 2, "离": 3, "震": 4, "巽": 5, "坎": 6, "艮": 7, "坤": 8}
    if s in m:
        return m[s]
    fw = {"南": 3, "北": 6, "东": 4, "西": 2, "东南": 5, "西北": 1, "西南": 8, "东北": 7}
    if s in fw:
        return fw[s]
    wx = {"火": 3, "水": 6, "金": 1, "木": 4, "土": 8}
    if s in wx:
        return wx[s]
    raise ValueError(f"无法识别卦/方位/物象: {x}")


def cast_guanwu(n, dt=None):
    """物数占（后天）：见可数之物，物数为上卦，物数+时数为下卦，总除六取动爻"""
    n = int(n)
    shi = _shichen(dt)
    return _build(gua_num(n), gua_num(n + shi), (n + shi) % 6 or 6,
                  note=f"物数占(后天): 物数{n} 时数{shi}")


def cast_shengyin(n, dt=None):
    """声音占（后天）：闻声几数，声数为上卦，声数+时数为下卦，总除六取动爻"""
    n = int(n)
    shi = _shichen(dt)
    return _build(gua_num(n), gua_num(n + shi), (n + shi) % 6 or 6,
                  note=f"声音占(后天): 声数{n} 时数{shi}")


def cast_zishu(n, dt=None):
    """字占（后天）：字数停匀分半，不匀则少一字为上卦、多一字为下卦，合二卦总数取爻"""
    n = int(n)
    shang = gua_num(n // 2) or 8          # 上卦取少的一边
    xia = gua_num(n - n // 2)             # 下卦取多的一边
    return _build(shang, xia, n % 6 or 6,
                  note=f"字占(后天): {n}字 上{n // 2} 下{n - n // 2}")


def cast_duanfa(wu, fang, dt=None):
    """端法后天起卦：以物为上卦、方位为下卦，合物卦数+方卦数+时数取动爻"""
    wu_n = _to_gua(wu)
    fang_n = _to_gua(fang)
    shi = _shichen(dt)
    return _build(wu_n, fang_n, (wu_n + fang_n + shi) % 6 or 6,
                  note=f"端法后天起卦: 物={GUA[wu_n]}({wu}) 方位={GUA[fang_n]}({fang}) 时数{shi}")


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
    return {
        "note": note,
        "本卦": ben, "互卦": hu, "变卦": bian, "动爻": dong,
        "上卦": GUA[shang], "下卦": GUA[xia],
        "体卦": GUA[ti], "体五行": WX[ti],
        "用卦": GUA[yong], "用五行": WX[yong],
        "体用关系": sheng,
    }
