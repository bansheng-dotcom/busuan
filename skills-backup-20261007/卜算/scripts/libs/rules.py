# -*- coding: utf-8 -*-
"""断卦规则引擎：把「断：体用生克」这类开放提示落成可判定、可回归测试的 if-then 规则函数。

每条规则返回结构化判定 dict：
  {judgment: 吉/凶/中, confidence: 高/中/低, evidence: 规则ID, basis: 依据说明}
断卦时优先调用这些规则；规则覆盖不到的再标 [规则推演]，不得凭空 [主观推断]。

规则 ID 即「证据编号」：每条断语可回溯到 R-XX-NN 规则号。
"""
_GAN = "甲乙丙丁戊己庚辛壬癸"
_ZHI = "子丑寅卯辰巳午未申酉戌亥"
_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
_ZHI_WX = {"寅": "木", "卯": "木", "巳": "火", "午": "火", "申": "金", "酉": "金",
           "亥": "水", "子": "水", "辰": "土", "戌": "土", "丑": "土", "未": "土"}


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
