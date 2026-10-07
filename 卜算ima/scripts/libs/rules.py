# -*- coding: utf-8 -*-
"""断卦规则引擎：把「断：体用生克」这类开放提示落成可判定、可回归测试的 if-then 规则函数。

每条规则返回结构化判定 dict：
  {judgment: 吉/凶/中, confidence: 高/中/低, evidence: 规则ID, basis: 依据说明}
断卦时优先调用这些规则；规则覆盖不到的再标 [规则推演]，不得凭空 [主观推断]。

规则 ID 即「证据编号」：每条断语可回溯到 R-XX-NN 规则号。
"""
import qimen_keying
import liuren_shensha
import liuren_bifa

_GAN = "甲乙丙丁戊己庚辛壬癸"
_ZHI = "子丑寅卯辰巳午未申酉戌亥"
_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
_ZHI_WX = {"寅": "木", "卯": "木", "巳": "火", "午": "火", "申": "金", "酉": "金",
           "亥": "水", "子": "水", "辰": "土", "戌": "土", "丑": "土", "未": "土"}

# 典籍出处指针（断卦时仍须按此 Grep 原文佐证，双重保证）
_SRC_XJBFS = "《钦定协纪辨方书》"
_SRC_XLK = "《御定星历考原》"


def _r(j, conf, ev, basis):
    return {"judgment": j, "confidence": conf, "evidence": ev, "basis": basis}


# —— 小六壬 ——
_LIU_GONG_JI_XIONG = {"大安": ("吉", "安稳顺遂"), "留连": ("中", "拖延纠缠"),
                      "速喜": ("吉", "快速喜庆"), "赤口": ("凶", "口舌官非"),
                      "小吉": ("吉", "和合小吉"), "空亡": ("凶", "落空无果")}


def xiaoliuren(gong):
    """小六壬六宫吉凶。R-XLR-01"""
    j, m = _LIU_GONG_JI_XIONG.get(gong, ("中", "未明"))
    return _r(j, "高", "R-XLR-01", f"落宫「{gong}」主{m}")


# —— 梅花易数 ——
def meihua(wx_body, wx_yong):
    """梅花体用生克。R-MH-01"""
    if wx_yong == wx_body:
        return _r("吉", "高", "R-MH-01", f"体用比和（{wx_body}）同心可成")
    if _KE.get(wx_yong) == wx_body:
        return _r("凶", "高", "R-MH-01", f"用克体（{wx_yong}克{wx_body}）对方压制，宜避缓")
    if _SHENG.get(wx_yong) == wx_body:
        return _r("吉", "高", "R-MH-01", f"用生体（{wx_yong}生{wx_body}）有助力")
    if _KE.get(wx_body) == wx_yong:
        return _r("中", "中", "R-MH-01", f"体克用（{wx_body}克{wx_yong}）费力可成")
    if _SHENG.get(wx_body) == wx_yong:
        return _r("中", "中", "R-MH-01", f"体生用（{wx_body}生{wx_yong}）泄气，付出多回报少")
    return _r("中", "低", "R-MH-01", "生克关系未明")


# —— 八字旺衰（第一维：得令） ——
def bazi_deling(day_gan, month_zhi):
    """八字旺衰·得令。R-BZ-01"""
    day_wx = _WX.get(day_gan, "")
    ling = _ZHI_WX.get(month_zhi, "")
    if day_wx == ling:
        return _r("旺", "高", "R-BZ-01", f"日主{day_wx}得月令{ling}（比劫）")
    if _SHENG.get(ling) == day_wx:
        return _r("旺", "高", "R-BZ-01", f"月令{ling}生日主{day_wx}（印）")
    if _KE.get(ling) == day_wx:
        return _r("弱", "高", "R-BZ-01", f"月令{ling}克日主{day_wx}（官杀）")
    return _r("弱", "中", "R-BZ-01", f"日主{day_wx}失令于月令{ling}（食伤/财）")


# —— 择日 ——
_JIANCHU = {"建": "小吉", "除": "吉", "满": "吉", "平": "平", "定": "吉", "执": "吉",
            "破": "大凶", "危": "小凶", "成": "大吉", "收": "吉", "开": "大吉", "闭": "凶"}
_HUANGDAO = {"明堂": "吉", "玉堂": "吉", "青龙": "吉", "金匮": "吉", "天德": "吉", "司命": "吉",
             "天刑": "凶", "朱雀": "凶", "白虎": "凶", "天牢": "凶", "玄武": "凶", "勾陈": "凶"}


def zeri_jianchu(jianchu):
    """择日·建除十二神。R-ZR-01"""
    g = _JIANCHU.get(jianchu, "平")
    j = "吉" if "吉" in g and "凶" not in g else ("凶" if "凶" in g else "中")
    return _r(j, "高", "R-ZR-01", f"建除「{jianchu}」为{g}")


def zeri_huangdao(huangdao):
    """择日·黄道黑道。R-ZR-02"""
    g = _HUANGDAO.get(huangdao)
    if g == "吉":
        return _r("吉", "高", "R-ZR-02", f"黄道「{huangdao}」吉")
    if g == "凶":
        return _r("凶", "高", "R-ZR-02", f"黑道「{huangdao}」凶")
    return _r("中", "低", "R-ZR-02", f"「{huangdao}」未明")


# —— 老黄历补全（结构化判定层：给出方向 + 出处指针，原文仍由 Grep 检索佐证） ——
def zeri_zhishen(zhi_shen):
    """老黄历·十二值神吉凶（协纪辨方书精确起法）。R-ZR-03"""
    g = _HUANGDAO.get(zhi_shen)
    if g == "吉":
        return _r("吉", "高", "R-ZR-03",
                  f"值神「{zhi_shen}」黄道吉神（出处：{_SRC_XJBFS}·十二值神，断卦按值神名 Grep 原文佐证）")
    if g == "凶":
        return _r("凶", "高", "R-ZR-03",
                  f"值神「{zhi_shen}」黑道凶神（出处：{_SRC_XJBFS}·十二值神，断卦按值神名 Grep 原文佐证）")
    return _r("中", "低", "R-ZR-03", f"值神「{zhi_shen}」未明")


def zeri_pengzu(gan_ji, zhi_ji):
    """老黄历·彭祖百忌（当日禁忌，非吉凶定档，标「避」）。R-ZR-04"""
    return _r("中", "高", "R-ZR-04",
              f"彭祖百忌：{gan_ji}；{zhi_ji}——当日所忌之事宜避（出处：{_SRC_XJBFS}·彭祖百忌，断卦 Grep「彭祖百忌」原文佐证）")


def zeri_fangwei(fw):
    """老黄历·吉神方位（喜神/财神/福神/阳贵/阴贵，供趋吉择向）。R-ZR-05"""
    parts = " ".join(f"{k}{fw.get(k, '')}" for k in ("喜神", "财神", "福神", "阳贵", "阴贵") if fw.get(k))
    return _r("吉", "高", "R-ZR-05",
              f"吉神方位：{parts}——求财谒贵宜向财神/贵人方（出处：{_SRC_XJBFS}·吉神方位，断卦按「喜神/财神/福神/贵人」Grep 原文佐证）")


# —— 奇门遁甲（结构化规则：判定 + 典籍出处指针，原文仍由 Grep 检索佐证） ——
_QIMEN_MEN = {"开": ("吉", "宜开创、出行、远行"), "休": ("吉", "宜休养、求财、交易"),
              "生": ("吉", "宜求财、经营、种植"), "伤": ("凶", "宜捕猎、讨债，余事忌"),
              "杜": ("中", "宜藏形、躲避，主阻隔"), "景": ("中", "宜上书、考试、广告"),
              "死": ("凶", "宜吊丧、行刑，余事大凶"), "惊": ("凶", "主惊恐、口舌、官司")}
_QIMEN_STAR = {"天心": ("吉", "宜疗病、求谋"), "天任": ("吉", "宜求财、婚嫁"),
               "天辅": ("吉", "宜求学、文书"), "天禽": ("吉", "宜祭祀、祈福"),
               "天冲": ("中", "宜出师、报仇"), "天蓬": ("凶", "宜守不宜动"),
               "天芮": ("凶", "宜求医（主疾病）"), "天柱": ("凶", "宜守、忌争讼"),
               "天英": ("凶", "宜文书、忌远行")}
_QIMEN_SHEN = {"值符": ("吉", "百恶消散"), "太阴": ("吉", "宜密谋、藏避"),
               "六合": ("吉", "宜婚嫁、交易"), "九地": ("吉", "宜屯守、埋藏"),
               "九天": ("吉", "宜扬兵、出行"), "腾蛇": ("凶", "主虚惊、怪异"),
               "白虎": ("凶", "主血光、杀伤"), "玄武": ("凶", "主盗骗、暗昧")}
_QIMEN_MEN_WX = {"开": "金", "休": "水", "生": "土", "伤": "木", "杜": "木", "景": "火", "死": "土", "惊": "金"}
_QIMEN_GONG_WX = {"坎": "水", "坤": "土", "震": "木", "巽": "木", "中": "土", "乾": "金", "兑": "金", "艮": "土", "离": "火"}
_WUBUYUSHI = {"甲": "庚", "乙": "辛", "丙": "壬", "丁": "癸", "戊": "甲",
              "己": "乙", "庚": "丙", "辛": "丁", "壬": "戊", "癸": "己"}


def qimen_men(men):
    """奇门八门吉凶。R-QM-01"""
    j, m = _QIMEN_MEN.get(men, ("中", "未明"))
    return _r(j, "高", "R-QM-01", f"八门「{men}」{m}（出处：《奇门遁甲统宗》《奇门遁甲秘笈大全》）")


def qimen_star(star):
    """奇门九星吉凶。R-QM-02"""
    j, m = _QIMEN_STAR.get(star, ("中", "未明"))
    return _r(j, "高", "R-QM-02", f"九星「{star}」{m}（出处：《奇门遁甲统宗》）")


def qimen_shen(shen):
    """奇门八神吉凶。R-QM-03"""
    j, m = _QIMEN_SHEN.get(shen, ("中", "未明"))
    return _r(j, "高", "R-QM-03", f"八神「{shen}」{m}（出处：《奇门遁甲统宗》《烟波钓叟歌》）")


def qimen_menpo(men, gong):
    """奇门门迫：门克宫。R-QM-04"""
    mw, gw = _QIMEN_MEN_WX.get(men), _QIMEN_GONG_WX.get(gong)
    if mw and gw and _KE.get(mw) == gw:
        return _r("凶", "高", "R-QM-04",
                  f"门迫（{men}门{mw}克{gong}宫{gw}），百事不利宜改期换方（出处：《奇门遁甲统宗》）")
    return _r("中", "中", "R-QM-04", "无门迫")


def qimen_geju(tianpan, dipan):
    """奇门十干克应（81 格局，天盘干+地盘干）。R-QM-05"""
    r = qimen_keying.lookup(tianpan, dipan)
    if r["格局"]:
        j = qimen_keying.jx_to_judgment(r["吉凶"])
        return _r(j, "高", "R-QM-05",
                  f"「{r['格局']}」（天盘{tianpan}加地盘{dipan}）：{r['含义']}（出处：{r['出处']}）")
    return _r("中", "低", "R-QM-05", f"天盘{tianpan}加地盘{dipan}非具名格局，依门星神宫生克参断")


def qimen_wubuyushi(day_gan, hour_gan):
    """奇门五不遇时：时干克日干。R-QM-06"""
    if _WUBUYUSHI.get(day_gan) == hour_gan:
        return _r("凶", "高", "R-QM-06",
                  f"五不遇时（{day_gan}日{hour_gan}时，时干克日干），百事不利宜改期（出处：《奇门遁甲统宗》）")
    return _r("中", "中", "R-QM-06", "非五不遇时")


# —— 大六壬（结构化判定：十二天将/神煞/毕法赋，原文仍由 Grep 佐证） ——
def liuren_tianjiang(name):
    """大六壬十二天将吉凶。R-LR-01"""
    r = liuren_shensha.tianjiang(name)
    j = "吉" if r["吉凶"] == "吉" else ("凶" if r["吉凶"] == "凶" else "中")
    return _r(j, "高", "R-LR-01",
              f"天将「{name}」{r['主事']}（出处：{r['出处']}，断卦 Grep 天将名原文佐证）")


def liuren_shensha_rule(name, zhi=""):
    """大六壬神煞吉凶。R-LR-02"""
    jx = {"驿马": "中", "桃花": "中", "华盖": "中", "劫煞": "凶", "灾煞": "凶", "岁煞": "凶",
          "日德": "吉", "日禄": "吉", "羊刃": "凶", "天乙贵人": "吉", "月德": "吉",
          "天喜": "吉", "红鸾": "吉", "旬空": "凶"}.get(name, "中")
    where = f"临{zhi}" if zhi else ""
    return _r(jx, "高", "R-LR-02",
              f"神煞「{name}」{where}（{jx}，出处《六壬大全》《六壬指南》，断卦 Grep 神煞名原文佐证）")


def liuren_bifa_rule(ju):
    """大六壬毕法赋句吉凶。R-LR-03"""
    hits = liuren_bifa.lookup(ju)
    if not hits:
        return _r("中", "低", "R-LR-03",
                  f"毕法赋无「{ju}」直接条目，按课体推演并标 [规则推演]")
    h = hits[0]
    return _r(h["吉凶"], "高", "R-LR-03",
              f"毕法赋「{h['句']}」主{h['主断']}（出处：{h['出处']}，断卦 Grep 条名原文佐证）")


# —— 多维交叉验证 ——
def cross_validate(dimensions):
    """dimensions: [(维度名, judgment), ...]。多维一致才定论，不一致返回「信号冲突」。

    返回 dict: {verdict: 吉/凶/中/信号冲突, consistent: bool, detail: [...]}
    """
    if not dimensions:
        return {"verdict": "中", "consistent": False, "detail": [], "evidence": "R-XV-01"}
    names = [n for n, _ in dimensions]
    js = [j for _, j in dimensions]
    detail = [f"{n}={j}" for n, j in dimensions]
    uniq = set(js)
    if len(uniq) == 1:
        return {"verdict": js[0], "consistent": True, "detail": detail, "evidence": "R-XV-01",
                "basis": f"{'、'.join(names)} 一致"}
    # 吉/中 与 凶 并存 → 冲突
    if "吉" in uniq and "凶" in uniq:
        return {"verdict": "信号冲突", "consistent": False, "detail": detail, "evidence": "R-XV-01",
                "basis": f"{'、'.join(names)} 吉凶矛盾，仅供参考并降级"}
    if uniq <= {"吉", "中"}:
        return {"verdict": "中", "consistent": False, "detail": detail, "evidence": "R-XV-01",
                "basis": f"{'、'.join(names)} 偏吉但不一致"}
    return {"verdict": "中", "consistent": False, "detail": detail, "evidence": "R-XV-01",
            "basis": f"{'、'.join(names)} 偏凶但不一致"}


# —— 双法同参融合标记（借鉴 laoshifu-mcp） ——
def fusion_mark(verdict_a, verdict_b, same_aspect=True):
    """双法同参三态标记：一致 / 冲突 / 互补。

    - 一致：两法同断同方向；
    - 冲突：两法回答同一侧面（same_aspect=True）但吉凶相反；
    - 互补：两法回答不同侧面（same_aspect=False，如六爻断成败、奇门断时机方位）。
    返回 (标记, 说明)。
    """
    if not same_aspect:
        return "互补", "两法分答不同侧面（成败 vs 时机方位），互相补充不冲突"
    if verdict_a == verdict_b:
        return "一致", f"两法同断「{verdict_a}」"
    if {verdict_a, verdict_b} == {"吉", "凶"}:
        return "冲突", f"两法吉凶相反（{verdict_a} vs {verdict_b}），须降级并说明分歧"
    return "互补", f"两法结论不同但非直接矛盾（{verdict_a} vs {verdict_b}）"
