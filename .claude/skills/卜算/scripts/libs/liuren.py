# -*- coding: utf-8 -*-
"""大六壬排盘（引擎: kentang2017/kinliuren，经 engines/taiyi/kinliuren.py 复用）

在 kinliuren 天地盘/四课/三传基础上，补结构化判定层：
  1. 三传天将吉凶（十二天将，liuren_shensha）
  2. 命中神煞（驿马/桃花/华盖/劫煞/灾煞/岁煞/日德/日禄/羊刃/天乙/月德/天喜/红鸾/旬空）
  3. 毕法赋条目检索建议（liuren_bifa，按格局/神煞关键词）

以上均为「结构化判定层 + 出处指针」，断卦时仍须按条目名/神煞名 Grep 原文佐证（双重保证）。
"""
import datetime
from lunar_python import Solar
from engines.taiyi.kinliuren import Liuren
import liuren_shensha
import liuren_bifa

# 天将简称 -> 完整名（kinliuren 三传/天地盘用简称）
_TIANJIANG_ALIAS = {
    "貴": "贵人", "蛇": "螣蛇", "雀": "朱雀", "合": "六合", "勾": "勾陈",
    "龍": "青龙", "空": "天空", "虎": "白虎", "常": "太常", "玄": "玄武",
    "陰": "太阴", "后": "天后",
}

_ZHI = "子丑寅卯辰巳午未申酉戌亥"
_GAN = "甲乙丙丁戊己庚辛壬癸"

# 课体格局名 -> 毕法赋检索关键词（同义/异名归一，繁体格局名常见）
_JU_ALIAS = {
    "返吟": "伏吟", "反吟": "伏吟", "伏吟": "伏吟",
    "六合": "合", "三合": "合", "六儀": "三六合", "六仪": "三六合",
    "空亡": "空", "旬空": "空", "空上": "空", "空上逢空": "空",
    "財": "财", "財局": "财", "財逢": "财",
    "白虎": "虎", "虎視": "虎", "虎": "虎",
    "貴人": "贵", "貴": "贵", "夜貴": "贵", "晝貴": "贵",
    "螣蛇": "蛇", "蛇": "蛇",
    "玄武": "盗", "玄": "盗",
    "朱雀": "雀", "雀": "雀",
    "墓": "墓", "入墓": "墓", "墓覆": "墓",
    "丁馬": "丁马", "丁馬動": "丁马", "驛馬": "丁马",
    "絶嗣": "绝嗣", "絕嗣": "绝嗣",
    "連茹": "连茹", "進茹": "连茹", "退茹": "连茹",
    "昴星": "昴星",
    "天網": "天网", "羅網": "天网",
}


def cast(dt=None):
    dt = dt or datetime.datetime.now()
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    day_gz = lunar.getDayInGanZhi()
    hour_gz = lunar.getTimeInGanZhi()
    day_gan, day_zhi = day_gz[0], day_gz[1]
    year_zhi = lunar.getYearZhi()
    month_zhi = lunar.getMonthZhi()
    jieqi = lunar.getPrevJieQi().getName()
    lmonth = lunar.getMonth()

    lr = Liuren(jieqi, lmonth, day_gz, hour_gz)
    r = lr.result(1)

    print(f"[大六壬] {lunar.toString()} {jieqi}  {day_gz}日{hour_gz}时")
    print(f"格局: {'、'.join(r.get('格局', []))}")
    t = r.get('三傳', {})
    print(f"三传: 初传 {t.get('初傳')} -> 中传 {t.get('中傳')} -> 末传 {t.get('末傳')}")
    print(f"四课: {r.get('四課', {})}")
    print(f"日马(驿马): {r.get('日馬', '')}  月将: {lr.moongeneral()}")

    # —— 三传天将吉凶（结构化 + 出处）——
    print("\n【三传天将】")
    for label, key in (("初传", "初傳"), ("中传", "中傳"), ("末传", "末傳")):
        chuan = t.get(key)
        if not chuan:
            continue
        jiang = _TIANJIANG_ALIAS.get(chuan[1], chuan[1])
        tj = liuren_shensha.tianjiang(jiang)
        print(f"  {label} {chuan[0]} 乘{jiang}（{tj['吉凶']}，{tj['主事']}）[出处：{tj['出处']}]")

    # —— 命中神煞 ——
    hits = liuren_shensha.compute_shensha(day_gan, day_zhi, year_zhi, month_zhi, lmonth)
    print("\n【命中神煞】")
    print(liuren_shensha.format_shensha(hits))

    # —— 毕法赋检索建议（按格局/神煞关键词，供 Grep 原文佐证）——
    print("\n【毕法赋关联条目】（结构化索引，断卦按条名 Grep 原文佐证）")
    kws = set()
    for ju in r.get('格局', []):
        kws.add(_JU_ALIAS.get(ju, ju))
    kws |= set(hits.keys())
    kws |= {day_zhi}
    related = []
    for kw in kws:
        for h in liuren_bifa.lookup(kw):
            if h["句"] not in [x["句"] for x in related]:
                related.append(h)
    if related:
        for h in related[:6]:
            print(f"  [{h['吉凶']}] {h['句']} —— {h['主断']}（出处：{h['出处']}）")
    else:
        print("  （无直接关联条目，断卦按课体特征在 liuren_bifa.lookup 检索）")

    r["_神煞"] = hits
    r["_天将"] = {k: liuren_shensha.tianjiang(_TIANJIANG_ALIAS.get(v[1], v[1]))
                  for k, v in t.items() if v}
    return r
