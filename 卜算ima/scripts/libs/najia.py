# -*- coding: utf-8 -*-
"""六爻纳甲装卦：纳甲配干支、安世应、配六亲、定六神、旬空（自写，可复用）"""

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"

ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
          "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

# 八卦纳甲：卦号(1~8) -> (内卦(天干, 地支串), 外卦(天干, 地支串))
NAJIA = {
    1: (("甲", "子寅辰"), ("壬", "午申戌")),  # 乾
    2: (("丁", "巳卯丑"), ("丁", "亥酉未")),  # 兑
    3: (("己", "卯丑亥"), ("己", "酉未巳")),  # 离
    4: (("庚", "子寅辰"), ("庚", "午申戌")),  # 震
    5: (("辛", "丑亥酉"), ("辛", "未巳卯")),  # 巽
    6: (("戊", "寅辰午"), ("戊", "申戌子")),  # 坎
    7: (("丙", "辰午申"), ("丙", "戌子寅")),  # 艮
    8: (("乙", "未巳卯"), ("癸", "丑亥酉")),  # 坤
}

# 八宫：宫首 -> (宫五行, [本/一/二/三/四/五/游魂/归魂 八卦名])
GONG = {
    "乾": ("金", ["乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有"]),
    "兑": ("金", ["兑为泽", "泽水困", "泽地萃", "泽山咸", "水山蹇", "地山谦", "雷山小过", "雷泽归妹"]),
    "离": ("火", ["离为火", "火山旅", "火风鼎", "火水未济", "山水蒙", "风水涣", "天水讼", "天火同人"]),
    "震": ("木", ["震为雷", "雷地豫", "雷水解", "雷风恒", "地风升", "水风井", "泽风大过", "泽雷随"]),
    "巽": ("木", ["巽为风", "风天小畜", "风火家人", "风雷益", "天雷无妄", "火雷噬嗑", "山雷颐", "山风蛊"]),
    "坎": ("水", ["坎为水", "水泽节", "水雷屯", "水火既济", "泽火革", "雷火丰", "地火明夷", "地水师"]),
    "艮": ("土", ["艮为山", "山火贲", "山天大畜", "山泽损", "火泽睽", "天泽履", "风泽中孚", "风山渐"]),
    "坤": ("土", ["坤为地", "地雷复", "地泽临", "地天泰", "雷天大壮", "泽天夬", "水天需", "水地比"]),
}

# 世爻位置（对应八宫卦序 本/一/二/三/四/五/游魂/归魂）
SHI_POS = [6, 1, 2, 3, 4, 5, 4, 3]

SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

LIUSHEN = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]
# 日干 -> 初爻六神起始索引
LIUSHEN_START = {"甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5}

_GUA64_REV = None
_GONG_MAP = None


def _gua64_rev():
    global _GUA64_REV
    if _GUA64_REV is None:
        from gua import GUA64
        _GUA64_REV = {name: (u, d) for (u, d), name in GUA64.items()}
    return _GUA64_REV


def _gong_map():
    global _GONG_MAP
    if _GONG_MAP is None:
        m = {}
        for gong, (wx, guas) in GONG.items():
            for i, name in enumerate(guas):
                m[name] = (gong, wx, SHI_POS[i])
        _GONG_MAP = m
    return _GONG_MAP


def najia_lines(name):
    """卦名 -> 六爻干支列表（自下而上 初~上）"""
    u, d = _gua64_rev()[name]
    inner_gan, inner_zhi = NAJIA[d][0]
    outer_gan, outer_zhi = NAJIA[u][1]
    return [inner_gan + inner_zhi[0], inner_gan + inner_zhi[1], inner_gan + inner_zhi[2],
            outer_gan + outer_zhi[0], outer_gan + outer_zhi[1], outer_gan + outer_zhi[2]]


def liuqin(gong_wx, zhi):
    """以宫五行为我，地支定六亲"""
    z_wx = ZHI_WX[zhi]
    if z_wx == gong_wx:
        return "兄弟"
    if SHENG.get(z_wx) == gong_wx:
        return "父母"   # 爻生宫 = 生我
    if SHENG.get(gong_wx) == z_wx:
        return "子孙"   # 宫生爻 = 我生
    if KE.get(z_wx) == gong_wx:
        return "官鬼"   # 爻克宫 = 克我
    if KE.get(gong_wx) == z_wx:
        return "妻财"   # 宫克爻 = 我克
    return "?"


def xunkong(day_gz):
    """日柱干支 -> 旬空地支两字"""
    gan, zhi = day_gz[0], day_gz[1]
    g = GAN.index(gan)
    z = ZHI.index(zhi)
    xun_shou = (z - g) % 12
    return ZHI[(xun_shou - 2) % 12] + ZHI[(xun_shou - 1) % 12]


def zhuang(ben_name, bian_name, dong, day_gz, month_gz=""):
    """完整装卦。day_gz 如 '壬子'，month_gz 如 '丁酉'（可空）。"""
    gm = _gong_map()
    gong, gong_wx, shi = gm[ben_name]
    ying = ((shi - 1 + 3) % 6) + 1

    ben_lines = najia_lines(ben_name)
    bian_lines = najia_lines(bian_name)

    start = LIUSHEN_START[day_gz[0]]
    shen = [LIUSHEN[(start + i) % 6] for i in range(6)]

    ben_qin = [liuqin(gong_wx, x[-1]) for x in ben_lines]
    bian_qin = [liuqin(gong_wx, x[-1]) for x in bian_lines]

    dong = set(dong or [])
    kong = xunkong(day_gz)
    kong_set = set(kong)

    return {
        "宫": f"{gong}宫({gong_wx})",
        "宫五行": gong_wx,
        "世爻": shi,
        "应爻": ying,
        "日辰": day_gz[1],
        "月建": month_gz[-1] if month_gz else "",
        "旬空": kong,
        "六爻": [
            {
                "爻": ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"][i],
                "六神": shen[i],
                "本卦": f"{ben_qin[i]} {ben_lines[i]}",
                "变卦": f"{bian_qin[i]} {bian_lines[i]}" if (i + 1) in dong else "",
                "世应": ("世" if (i + 1) == shi else ("应" if (i + 1) == ying else "")),
                "动": "动" if (i + 1) in dong else "",
                "空": "空" if ben_lines[i][-1] in kong_set else "",
            }
            for i in range(6)
        ],
    }


def print_zhuang(r):
    """打印装卦表"""
    print(f"[装卦] {r['宫']}  月建:{r['月建'] or '—'}  日辰:{r['日辰']}  旬空:{r['旬空']}")
    print(f"       世爻:第{r['世爻']}爻  应爻:第{r['应爻']}爻")
    print(f"{'六神':<6}{'爻位':<5}{'本卦(六亲 干支)':<16}{'变卦(六亲 干支)':<16}{'标'}")
    for x in r["六爻"]:
        b = x["本卦"]
        v = x["变卦"] or "—"
        tag = x["世应"] + x["动"] + x["空"]
        print(f"{x['六神']:<6}{x['爻']:<5}{b:<16}{v:<16}{tag}")
