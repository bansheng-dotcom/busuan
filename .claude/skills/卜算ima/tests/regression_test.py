# -*- coding: utf-8 -*-
"""排盘确定性回归测试。

只测「排盘是否算对」（脚本层、可机器验证），不测「断卦是否断准」（推理层，见 ../cases/）。

运行: python tests/regression_test.py
"""
import os
import sys
import io
import contextlib
import datetime

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

_PASS = 0
_FAIL = 0


def check(name, got, want):
    global _PASS, _FAIL
    if got == want:
        _PASS += 1
        print(f"  ✓ {name}: {got}")
    else:
        _FAIL += 1
        print(f"  ✗ {name}: 得 {got!r}，期望 {want!r}")


def test_bazi():
    print("[八字] 四柱确定性")
    from lunar_python import Solar
    b = Solar.fromYmdHms(2000, 1, 1, 8, 0, 0).getLunar().getEightChar()
    check("年柱", b.getYear(), "己卯")
    check("月柱", b.getMonth(), "丙子")
    check("日柱", b.getDay(), "戊午")
    check("时柱", b.getTime(), "丙辰")


def test_zhiwei():
    print("[紫微斗数] 命宫身宫五行局")
    import zhiwei
    r = zhiwei.cast(1990, 5, 15, 8, 1)
    check("命宫", r["命宫"], "己丑")
    check("身宫", r["身宫"], "乙酉")
    check("五行局", r["五行局"], "火6局")


def test_zhiwei_palaces():
    print("[紫微] 十二宫逆时针方向（命宫丑起）")
    import zhiwei
    r = zhiwei.cast(1990, 5, 15, 8, 1)
    by_zhi = {p["支"]: p["宫"] for p in r["十二宫"]}
    check("命宫在丑", by_zhi["丑"], "命宫")
    check("兄弟在子", by_zhi["子"], "兄弟宫")
    check("夫妻在亥", by_zhi["亥"], "夫妻宫")
    check("子女在戌", by_zhi["戌"], "子女宫")
    check("财帛在酉", by_zhi["酉"], "财帛宫")
    check("疾厄在申", by_zhi["申"], "疾厄宫")
    check("迁移在未", by_zhi["未"], "迁移宫")
    check("交友在午", by_zhi["午"], "交友宫")
    check("官禄在巳", by_zhi["巳"], "官禄宫")
    check("田宅在辰", by_zhi["辰"], "田宅宫")
    check("福德在卯", by_zhi["卯"], "福德宫")
    check("父母在寅", by_zhi["寅"], "父母宫")


def test_zhiwei_flystar():
    print("[紫微] 四化飞星（庚午年 1990-5-15）")
    import zhiwei
    r = zhiwei.cast(1990, 5, 15, 8, 1)
    fly = {f["四化"]: (f["星"], f["宫"]) for f in r["四化飞星"]}
    check("飞星·禄=太阳", fly["禄"][0], "太阳")
    check("飞星·权=武曲", fly["权"][0], "武曲")
    check("飞星·科=太阴", fly["科"][0], "太阴")
    check("飞星·忌=天同", fly["忌"][0], "天同")
    check("飞星·四化齐全", len(r["四化飞星"]), 4)


def test_ziwei_horoscope():
    print("[紫微] 运限（流年/流月/流日/流时，py-iztro）")
    import ziwei_horoscope
    h = ziwei_horoscope.horoscope(1990, 5, 15, 8, 1, target="2026-10-07")
    check("运限·可用", h.get("可用"), True)
    check("运限·流年命宫午", h["yearly"]["命宫"], "午")
    check("运限·流年干支丙午", h["yearly"]["干支"], "丙午")
    check("运限·流年四化", h["yearly"]["四化"], ["天同", "天机", "文昌", "廉贞"])
    check("运限·流月有值", bool(h["monthly"]["命宫"]), True)
    check("运限·流日有值", bool(h["daily"]["命宫"]), True)
    check("运限·流时有值", bool(h["hourly"]["命宫"]), True)
    check("运限·出处带书名", "紫微斗数全书" in h["出处"], True)


def test_bazi_shensha():
    print("[八字] 神煞（己卯 丙子 戊午 丙辰，31 神煞全量）")
    from lunar_python import Solar
    import shensha
    b = Solar.fromYmdHms(2000, 1, 1, 8, 0, 0).getLunar().getEightChar()
    r = shensha.analyze(b, "男")
    names = [it["神煞"] for cat in ("贵人吉神", "文星学业", "禄财", "婚姻感情",
                                     "动迁出行", "特殊格局", "凶煞") for it in r.get(cat, [])]
    check("命中太极贵人", "太极贵人" in names, True)
    check("命中桃花", "桃花" in names, True)
    check("命中羊刃", "羊刃" in names, True)
    check("命中空亡", "空亡" in names, True)
    check("神煞总数", r["总数"], 9)


def test_xingchong():
    print("[八字] 刑冲合害（卯子午辰）")
    import xingchong
    r = xingchong.analyze(["卯", "子", "午", "辰"])
    chong = [it["关系"] for it in r["六冲"]]
    he = [it["关系"] for it in r["六害"]]
    xing = [it["关系"] for it in r["三刑"]]
    po = [it["关系"] for it in r["相破"]]
    banhe = [it["关系"] for it in r["半三合"]]
    check("六冲·子午", any("子午" in x for x in chong), True)
    check("六害·卯辰", any("卯辰" in x for x in he), True)
    check("三刑·子卯", any("子卯" in x for x in xing), True)
    check("相破·卯午", any("卯午" in x for x in po), True)
    check("半三合·子辰", any("子辰" in x for x in banhe), True)


def test_qimen_keying():
    print("[奇门] 十干克应 81 格局")
    import qimen_keying
    n, missing, extra = qimen_keying.completeness()
    check("克应总数 81", n, 81)
    check("无遗漏", missing, [])
    check("无越界", extra, [])
    check("青龙返首大吉", qimen_keying.KEYING[("戊", "丙")][1], "大吉")
    check("飞鸟跌穴大吉", qimen_keying.KEYING[("丙", "戊")][1], "大吉")
    check("青龙逃走大凶", qimen_keying.KEYING[("乙", "辛")][1], "大凶")
    check("朱雀投江大凶", qimen_keying.KEYING[("丁", "癸")][1], "大凶")
    check("出处带书名", "秘笈大全" in qimen_keying.lookup("戊", "丙")["出处"], True)
    check("半吉半凶→中", qimen_keying.jx_to_judgment("半吉半凶"), "中")
    check("大吉→吉", qimen_keying.jx_to_judgment("大吉"), "吉")
    check("大凶→凶", qimen_keying.jx_to_judgment("大凶"), "凶")


def test_hehun():
    print("[合婚] 评分确定性")
    import hehun
    z1 = frozenset(("午", "申"))
    from hehun import _shengxiao_rel, _wx_rel
    check("生肖午申", _shengxiao_rel("午", "申"), ("平", 0))
    check("五行金(日)见土", _wx_rel("金", "土"), ("土生金(生我)", 2))


def test_liunian():
    print("[流年] 干支周期")
    from bazi import _ganzhi_year
    check("2026 干支", _ganzhi_year(2026), "丙午")
    check("1984 干支", _ganzhi_year(1984), "甲子")


def test_liuyue():
    print("[八字] 流月聚合")
    import bazi
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b = bazi.liuyue(2000, 1, 1, 1, 2026)
    out = buf.getvalue()
    check("流月返回日主戊", b.getDayGan(), "戊")
    check("流月含1月", "1月" in out, True)
    check("流月含12月", "12月" in out, True)


def test_rules():
    print("[规则引擎] 断卦规则")
    import rules
    check("小六壬·赤口", rules.xiaoliuren("赤口")["judgment"], "凶")
    check("梅花·用克体(金克木)", rules.meihua("木", "金")["judgment"], "凶")
    check("梅花·用生体(水生木)", rules.meihua("木", "水")["judgment"], "吉")
    check("八字·戊土生子月失令", rules.bazi_deling("戊", "子")["judgment"], "弱")
    check("八字·甲木生寅月得令", rules.bazi_deling("甲", "寅")["judgment"], "旺")
    check("择日·成日", rules.zeri_jianchu("成")["judgment"], "吉")
    check("择日·破日", rules.zeri_jianchu("破")["judgment"], "凶")
    check("交叉·双吉一致", rules.cross_validate([("A", "吉"), ("B", "吉")])["verdict"], "吉")
    check("交叉·吉凶冲突", rules.cross_validate([("A", "吉"), ("B", "凶")])["verdict"], "信号冲突")
    check("融合·一致", rules.fusion_mark("吉", "吉")[0], "一致")
    check("融合·冲突", rules.fusion_mark("吉", "凶")[0], "冲突")
    check("融合·互补", rules.fusion_mark("吉", "凶", same_aspect=False)[0], "互补")
    check("奇门·开门吉", rules.qimen_men("开")["judgment"], "吉")
    check("奇门·死门凶", rules.qimen_men("死")["judgment"], "凶")
    check("奇门·青龙返首吉", rules.qimen_geju("戊", "丙")["judgment"], "吉")
    check("奇门·白虎猖狂凶", rules.qimen_geju("辛", "乙")["judgment"], "凶")
    check("奇门·五不遇时凶", rules.qimen_wubuyushi("甲", "庚")["judgment"], "凶")
    check("奇门·门迫凶", rules.qimen_menpo("开", "震")["judgment"], "凶")


def test_precheck():
    print("[gate] 排盘预检")
    import precheck
    ok, msg = precheck.check("八字", {"四柱", "十神", "五行", "纳音", "大运"})
    check("八字·齐全", ok, True)
    ok, msg = precheck.check("八字", {"四柱", "十神"})
    check("八字·缺项", ok, False)
    ok, msg = precheck.check("奇门遁甲", {"排局", "三奇六仪", "九星", "八门", "八神"})
    check("奇门·齐全", ok, True)


def test_tiaohou():
    print("[八字] 调候/旺衰/格局（借自 yueyuan-bazi）")
    import tiaohou
    check("调候·甲生寅月", tiaohou.tiao_hou_yongshen("甲", "寅"), ["丙", "癸"])
    check("调候表 120 条", sum(len(v) for v in tiaohou.TIAO_HOU.values()), 120)
    w = tiaohou.analyze_wangshuai(2000, 1, 1, 8, 1)
    check("旺衰·日主", w["日主"], "戊")
    g = tiaohou.ding_ge(2000, 1, 1, 8, 1)
    check("格局·有值", bool(g["格局"]), True)
    check("格局表 10 条", len(tiaohou.GE_JU_JIU_YING), 10)


# —— golden 测试：对三式/七政/风水/择日用固定输入断言确定性输出 ——
def _quiet(fn):
    """静默执行：丢弃 cast 打印，返回其返回值，便于 golden 断言只看结构。"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn()


def test_meihua_golden():
    print("[梅花易数] golden（数字起卦，无 lunardate 依赖）")
    import meihua
    # cast_num 纯数学起卦，确定性，不受农历库影响
    r = _quiet(lambda: meihua.cast_num([12, 34]))
    check("数字起卦·本卦", r["本卦"], "雷泽归妹")
    check("数字起卦·互卦", r["互卦"], "水火既济")
    check("数字起卦·变卦", r["变卦"], "火泽睽")
    check("数字起卦·动爻", r["动爻"], 6)
    r2 = _quiet(lambda: meihua.cast_num([7]))
    check("单数起卦·本卦", r2["本卦"], "艮为山")
    check("单数起卦·动爻", r2["动爻"], 1)


def test_xiaoliuren_golden():
    print("[小六壬] golden（显式月日时，无 lunardate 依赖）")
    import xiaoliuren
    # 显式传 y/m/d/h 绕开 lunardate 分支，纯掌诀确定性
    check("2026 八月初七巳时·落速喜", _quiet(lambda: xiaoliuren.cast(None, y=2026, m=8, d=27, h=5)), "速喜")
    check("月 1 日 1 子时·落大安", _quiet(lambda: xiaoliuren.cast(None, y=2026, m=1, d=1, h=0)), "大安")


def test_liuyao_najia():
    print("[六爻纳甲] golden（装卦确定性，绕开摇卦随机）")
    import najia
    z = najia.zhuang("风雷益", "水风井", [1, 2, 3, 6], "甲寅", "丁酉")
    check("宫·巽宫木", z["宫"], "巽宫(木)")
    check("世爻·3", z["世爻"], 3)
    check("应爻·6", z["应爻"], 6)
    check("旬空·子丑", z["旬空"], "子丑")
    check("初爻·父母庚子", z["六爻"][0]["本卦"], "父母 庚子")
    check("初爻·青龙", z["六爻"][0]["六神"], "青龙")
    check("初爻·动空", z["六爻"][0]["动"] + z["六爻"][0]["空"], "动空")
    check("三爻·妻财庚辰", z["六爻"][2]["本卦"], "妻财 庚辰")
    check("三爻·世动", z["六爻"][2]["世应"] + z["六爻"][2]["动"], "世动")
    # 新增机械字段：伏神 / 月破 / 化进退（风雷益缺官鬼→伏官鬼辛酉三爻；酉月冲卯→上爻月破；初爻子化丑=进神）
    check("伏神·官鬼辛酉伏三爻", z["伏神"][0]["六亲"] + z["伏神"][0]["干支"] + "伏" + z["伏神"][0]["伏爻"], "官鬼辛酉伏三爻")
    check("上爻·月破", z["六爻"][5]["破"], "破")
    check("初爻·化进神", z["六爻"][0]["化"], "进神")
    check("上爻·无化", z["六爻"][5]["化"], "")


def test_zhiwei_leapmonth():
    print("[紫微] 闰月作本月（lunar_python 负月归一）")
    import zhiwei
    # 1968 闰七月廿一 → 作七月；1947 闰二月初一 → 作二月。对照 iztro 47 例闰月均作本月
    r = _quiet(lambda: zhiwei.cast(1968, 9, 13, 8, 0))
    check("闰七月·命宫丙辰", r["命宫"], "丙辰")
    check("闰七月·身宫甲子", r["身宫"], "甲子")
    check("闰七月·五行局土5", r["五行局"], "土5局")
    r2 = _quiet(lambda: zhiwei.cast(1947, 3, 23, 20, 0))
    check("闰二月·命宫乙巳", r2["命宫"], "乙巳")
    check("闰二月·身宫癸丑", r2["身宫"], "癸丑")
    check("闰二月·五行局火6", r2["五行局"], "火6局")


def test_liuren_golden():
    print("[大六壬] golden（2026-10-07 10:00）")
    import liuren
    r = _quiet(lambda: liuren.cast(datetime.datetime(2026, 10, 7, 10, 0)))
    check("格局·返吟", "返吟" in r.get("格局", []), True)
    check("格局·絕嗣", "絕嗣" in r.get("格局", []), True)
    check("三传·初传", r.get("三傳", {}).get("初傳"), ["子", "虎", "父", "空"])


def test_liuren_struct():
    print("[大六壬] 毕法赋/天将/神煞结构化")
    import liuren_bifa
    import liuren_shensha
    import rules
    n, dup, empty = liuren_bifa.completeness()
    check("毕法赋条目 94", n, 94)
    check("毕法赋无重复", dup, [])
    check("毕法赋无空字段", empty, [])
    check("毕法赋·伏吟条目", liuren_bifa.lookup("伏吟")[0]["吉凶"], "中")
    check("毕法赋·出处带书名", "毕法赋" in liuren_bifa.lookup("财")[0]["出处"], True)
    check("天将·青龙吉", liuren_shensha.tianjiang("青龙")["吉凶"], "吉")
    check("天将·白虎凶", liuren_shensha.tianjiang("白虎")["吉凶"], "凶")
    check("神煞·午年午日羊刃", liuren_shensha.compute_shensha("戊", "午", "午", "寅", 1).get("羊刃", {}).get("地支"), "午")
    check("神煞·驿马申子辰在寅", liuren_shensha.compute_shensha("甲", "寅", "申", "寅", 1).get("驿马", {}).get("地支"), "寅")
    # 规则函数
    check("规则·天将白虎凶", rules.liuren_tianjiang("白虎")["judgment"], "凶")
    check("规则·神煞羊刃凶", rules.liuren_shensha_rule("羊刃", "午")["judgment"], "凶")
    check("规则·毕法赋财旺反亏凶", rules.liuren_bifa_rule("财")["judgment"], "凶")


def test_liuren_regress():
    print("[大六壬] 720 课结构回归（四课/三传/初传不变量）")
    import liuren_regress
    stats = liuren_regress.sweep(subset=("秋分",))   # 辰将，60 甲子日 × 12 时 = 720 课
    check("720 课四课全部正确", len(stats["结构四课错"]), 0)
    # 以下为已知 bug 基线（kinliuren 冷门宗门边界有误判/崩溃），只报告不阻塞，
    # 若未来改动使其恶化，从这里能看到数字变化。
    print(f"  · 崩溃 {len(stats['crash'])} / 三传递进错 {len(stats['结构三传错'])} / "
          f"初传不在上神 {len(stats['结构初传不在上神'])}（基线，非阻塞）")
    check("720 课总数", stats["total"], 720)


def test_jinkoujue_golden():
    print("[金口诀] golden（2026-04-22 12:00 丙寅日午时 申地）")
    import jinkoujue
    import rules
    r = _quiet(lambda: jinkoujue.cast(datetime.datetime(2026, 4, 22, 12, 0), "申"))
    check("月将·从魁酉", r["月将"], "从魁（酉）")
    check("四位·人元丙", r["四位"]["人元"]["符号"], "丙")
    check("四位·贵神玄武", r["四位"]["贵神"]["名"], "玄武")
    check("四位·将神登明亥", r["四位"]["将神"]["名"], "登明（亥）")
    check("四位·地分申", r["四位"]["地分"]["符号"], "申")
    # 五动爻：丙火（干）克申金（方）→ 妻动；玄武水（神）克丙火（干）→ 官动
    check("五动·妻动命中", any(w[0] == "妻动" for w in r["五动"]), True)
    check("五动·官动命中", any(w[0] == "官动" for w in r["五动"]), True)
    check("规则·鬼动凶", rules.jinkoujue_wudong("木", "土", "土", "金")["judgment"], "凶")
    check("规则·四位无克从旺", rules.jinkoujue_wudong("水", "木", "木", "水")["judgment"], "中")

    # —— 古本原文例复算（二月戌将·丙寅日·午时·申地 → 神后/玄武/丙）——
    print("[金口诀] 古本原文例复算")
    _Z, _ZD = jinkoujue._ZHI, jinkoujue._ZHIDX
    step = (_ZD["申"] - _ZD["午"]) % 12
    jiang = _Z[(_ZD["戌"] + step) % 12]
    check("原文例·将神神后", jinkoujue._JIANGSHEN[jiang][0], "神后")
    gr = jinkoujue._GUIREN["丙"][0]  # 昼贵人亥，亥在顺行段
    gs = (_ZD["申"] - _ZD["亥"]) % 12
    check("原文例·贵神玄武", jinkoujue._GUISHEN[gs][0], "玄武")
    dun = jinkoujue._DUNSHOU["丙"]
    ry = jinkoujue._GAN[(jinkoujue._GANDX[dun] + _ZD["申"]) % 10]
    check("原文例·人元丙", ry, "丙")
    # 核心规则数据（原文例依赖，锁定不得改坏）
    check("数据·春分戌将", jinkoujue._YUEJIANG["春分"], "戌")
    check("数据·谷雨酉将", jinkoujue._YUEJIANG["谷雨"], "酉")
    check("数据·丙日昼贵亥", jinkoujue._GUIREN["丙"][0], "亥")
    check("数据·丙辛遁首戊", jinkoujue._DUNSHOU["丙"], "戊")
    check("数据·子将神后", jinkoujue._JIANGSHEN["子"][0], "神后")


def test_liuren_ref():
    print("[大六壬] --ref 独立九宗门交叉校验")
    import liuren_regress
    cc = liuren_regress.cross_check_ref(datetime.datetime(2026, 4, 25, 12, 0))
    check("交叉校验·字段齐全", all(k in cc for k in ("引擎宗门", "独立宗门", "宗门一致", "三传一致")), True)
    check("交叉校验·谷雨贼克重审一致", cc["宗门一致"] and cc["三传一致"], True)
    cc2 = liuren_regress.cross_check_ref(datetime.datetime(2026, 10, 7, 10, 0))
    check("交叉校验·golden课可复核", ("独立宗门" in cc2 and "引擎宗门" in cc2), True)


def test_qimen_golden():
    print("[奇门遁甲] golden（2026-10-07 10:00）")
    import qimen
    q = _quiet(lambda: qimen.cast(datetime.datetime(2026, 10, 7, 10, 0)))
    sj = q.get("時家奇門", {})
    check("排盘·置闰", sj.get("排盤方式"), "置閏")
    check("排局·阴遁九局", sj.get("排局"), "陰遁九局中元")
    check("八门·坎宫生门", sj.get("門", {}).get("坎"), "生")


def test_taiyi_golden():
    print("[太乙神数] golden（2026-10-07 10:00，年计/统宗）")
    import taiyi
    t = _quiet(lambda: taiyi.cast(datetime.datetime(2026, 10, 7, 10, 0)))
    check("太乙落宫", t.get("太乙落宮"), 3)
    check("主算", t.get("主算", [None])[0], 16)
    check("客算", t.get("客算", [None])[0], 3)
    check("积年数", t.get("局式", {}).get("積年數"), 10155943)
    # 接线后新增字段（原只打印 8 个，现 pan() 全量返回）
    check("计神", t.get("計神"), "申")
    check("君基", t.get("君基"), "子")
    check("臣基", t.get("臣基"), "亥")
    check("民基", t.get("民基"), "寅")
    check("定算", t.get("定算", [None])[0], 22)
    check("阳九", t.get("陽九"), "午")
    check("百六", t.get("百六"), "未")
    check("八门值事", t.get("八門值事"), "傷")
    check("二十八宿值日", t.get("二十八宿值日"), "角")
    check("太乙九星·直符九星", t.get("太乙九星", {}).get("直符九星"), "天任")
    check("五运六气·五运", t.get("五運六氣", {}).get("五運"), "水運")
    check("八宫旺衰·落宫3", t.get("八宮旺衰", {}).get(3), "死")


def test_taiyi_rules():
    print("[太乙神数] 规则函数 R-TY-01~04")
    import taiyi, rules
    t = _quiet(lambda: taiyi.cast(datetime.datetime(2026, 10, 7, 10, 0)))
    check("主算吉", rules.taiyi_suan(t["主算"])["judgment"], "吉")
    check("客算凶", rules.taiyi_suan(t["客算"])["judgment"], "凶")
    check("主客主利", rules.taiyi_zhuke(t["主算"], t["客算"])["judgment"], "吉")
    check("文昌带掩格凶", rules.taiyi_geju(str(t["文昌"]))["judgment"], "凶")
    check("落宫死凶", rules.taiyi_luogong_wangshuai("死")["judgment"], "凶")
    check("落宫旺吉", rules.taiyi_luogong_wangshuai("旺")["judgment"], "吉")
    check("三才足数吉", rules.taiyi_suan([16, ["三才足數", "下和"]])["judgment"], "吉")


def test_taiyi_modes():
    print("[太乙神数] 多计式/多积年法 + 引擎边界守卫")
    import taiyi
    dt = datetime.datetime(2026, 10, 7, 10, 0)
    m = _quiet(lambda: taiyi.cast(dt, ji_style=1))
    check("月计", m.get("太乙計"), "月計")
    jj = _quiet(lambda: taiyi.cast(dt, method=1))
    check("金镜积年", jj.get("局式", {}).get("積年數"), 1938583)
    check("命法拒绝", _quiet(lambda: taiyi.cast(dt, ji_style=5)), {})
    check("日计×太乙局拒绝", _quiet(lambda: taiyi.cast(dt, ji_style=2, method=3)), {})
    check("非法参数拒绝", _quiet(lambda: taiyi.cast(dt, ji_style=9)), {})


def test_taiyi_regress():
    print("[太乙神数] 回归不变量（结构校验 + 积年独立重算）")
    import taiyi, taiyi_regress
    dt = datetime.datetime(2026, 10, 7, 10, 0)
    t = _quiet(lambda: taiyi.cast(dt))
    # 结构不变量：合法盘应无错
    check("合法盘结构无错", taiyi_regress.check_structural(t, 0), None)
    # 结构不变量：篡改盘应被抓出
    bad = dict(t)
    bad["局式"] = {"文": "x", "數": 999}
    check("局式数越界被抓", taiyi_regress.check_structural(bad, 0), "局式数越界")
    bad2 = dict(t)
    bad2["太乙落宮"] = 99
    check("落宫越界被抓", taiyi_regress.check_structural(bad2, 0), "太乙落宫越界")
    # 积年独立重算：4 法引擎 vs lunar_python 全一致
    jn = taiyi_regress.check_jinian(dt)
    check("积年独立重算 4/4 一致", sum(1 for _, _, _, ok in jn if ok), 4)


def test_taiyi_jieqi():
    print("[太乙神数] 冬至/年界节气回归（2026-10-08 修复 sxtwl 垫片）")
    from engines.taiyi.kintaiyi import Taiyi
    # 修复前这些日期 pan 崩溃（大雪~小寒约 30 天），修复后应全通过
    for d in [(2024, 12, 15), (2024, 12, 22), (2024, 12, 25), (2025, 1, 1), (2000, 1, 1)]:
        try:
            r = Taiyi(*d, 10, 0).pan(0, 0)
            check(f"冬至窗口 {d[0]}-{d[1]:02d}-{d[2]:02d} 不崩", r.get("太乙落宮") is not None, True)
        except Exception as e:
            check(f"冬至窗口 {d[0]}-{d[1]:02d}-{d[2]:02d} 不崩", f"崩 {type(e).__name__}", True)


def test_taiyi_html():
    print("[太乙神数] HTML 盘图")
    import taiyi, htmlpan, tempfile, os
    t = _quiet(lambda: taiyi.cast(datetime.datetime(2026, 10, 7, 10, 0)))
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.html")
    htmlpan.taiyi_html(t, p)
    txt = open(p, encoding="utf-8").read()
    check("盘图文件生成", os.path.isfile(p), True)
    check("盘图含主客算", "主客算" in txt, True)
    check("盘图含太乙九宫", "太乙九宫" in txt, True)
    check("盘图含落宫高亮", "palace ming" in txt, True)


def test_qizheng_golden():
    print("[七政四余] golden（2026-10-08 21:10，ephem 精算 + Meeus 四余）")
    import qizheng
    r = qizheng.qizheng_pan("2026-10-08 21:10")
    check("命宫·地支申", r.get("命宫", {}).get("地支"), "申")
    check("七政·七曜齐全", len(r.get("七政", {})), 7)
    check("四余·四余齐全", len(r.get("四余", {})), 4)

    # 七政黄经（ephem 地心黄经，比对已知参考值，容差 ±0.5°）
    _want = {'太阳': 194.9, '太阴': 169.0, '水星': 219.6, '金星': 217.6,
             '火星': 125.7, '木星': 140.5, '土星': 10.6}
    for _s, _v in _want.items():
        _got = r['七政'][_s]['黄经']
        check(f"七政·{_s}黄经≈{_v}°", abs(_got - _v) < 0.5, True)

    # 四余（Meeus 多项式；月孛=月平远地点、紫气=28 年周期，不再「月亮±90°」）
    _yu = r['四余']
    _moon = r['七政']['太阴']['黄经']
    check("罗睺≈327.3°", abs(_yu['罗睺']['黄经'] - 327.3) < 0.5, True)
    check("计都=罗睺+180°", abs(_yu['计都']['黄经'] - (_yu['罗睺']['黄经'] + 180) % 360) < 0.5, True)
    check("月孛≈272.6°", abs(_yu['月孛']['黄经'] - 272.6) < 0.5, True)
    check("紫气≈345.2°", abs(_yu['紫气']['黄经'] - 345.2) < 0.5, True)
    check("月孛≠月亮+90°", abs(_yu['月孛']['黄经'] - (_moon + 90) % 360) > 5, True)
    check("紫气≠月亮-90°", abs(_yu['紫气']['黄经'] - (_moon - 90) % 360) > 5, True)

    # 二十八宿真实距度（角宿一锚点，非 28 等分）
    check("太阳·宿轸", r['七政']['太阳']['宿'], "轸")
    check("太阴·宿翼", r['七政']['太阴']['宿'], "翼")


def test_fengshui_golden():
    print("[风水] golden（1990 坐北朝南 男）")
    import fengshui
    r = fengshui.fengshui_pan(1990, "坐北朝南", "男")
    check("命卦·坎", r.get("命卦"), "坎")
    check("东四命", r.get("东西命"), "东四命")
    check("宅命相配", r.get("宅命相配"), "相配")


def test_zeri_golden():
    print("[择日] golden（2026-10-07 婚嫁）")
    import zeri
    r = zeri.get_day_summary(2026, 10, 7, "婚嫁", 10)
    check("建除·平", r.get("建除"), "平")
    check("黄道·天刑", r.get("黄道"), "天刑")
    check("综合评分", r.get("综合评分"), 55)
    check("等级·中平", r.get("等级"), "中平")


def test_almanac():
    print("[老黄历] 补全字段（2026-10-07）")
    import almanac
    import rules
    a = almanac.almanac(2026, 10, 7)
    check("可用", a.get("可用"), True)
    check("农历非空", bool(a.get("农历")), True)
    check("值神·青龙", a["值神"]["值神"], "青龙")
    check("值神在十二值神内", a["值神"]["值神"] in
          "青龙明堂天刑朱雀金匮天德白虎玉堂天牢玄武司命勾陈", True)
    check("彭祖百忌·日干非空", bool(a["彭祖百忌"]["日干"]), True)
    check("彭祖百忌·日支非空", bool(a["彭祖百忌"]["日支"]), True)
    check("吉神方位·五方齐全", all(a["吉神方位"][k] for k in
          ("喜神", "财神", "福神", "阳贵", "阴贵")), True)
    check("胎神·非空", bool(a["胎神"]["方位"]), True)
    check("冲煞·冲非空", bool(a["冲煞"]["冲"]), True)
    check("宜忌·有值", bool(a["宜"]["事项"]) and bool(a["忌"]["事项"]), True)
    check("出处·带书名", "协纪辨方书" in a["值神"]["出处"], True)
    # 规则函数判定
    check("规则·值神青龙吉", rules.zeri_zhishen("青龙")["judgment"], "吉")
    check("规则·值神白虎凶", rules.zeri_zhishen("白虎")["judgment"], "凶")
    check("规则·彭祖百忌", rules.zeri_pengzu("甲不开仓", "寅不祭祀")["evidence"], "R-ZR-04")
    check("规则·吉神方位", rules.zeri_fangwei(a["吉神方位"])["evidence"], "R-ZR-05")


def test_review():
    print("[review] 断卦后质检（三层分离/三级标注/免责/应期/趋避/冲突降级）")
    import review
    good = ("盘面事实：本卦泽地萃，动爻6。规则推演：体生用泄气。[规则推演] "
            "现实建议：宜小步试错。[主观推断] 应期难定。趋吉：宜缓进。避凶：勿大额投入。"
            "术语解读：体生用是泄气之象。问事解读：能成但费劲。今日可行的一小步：先小成本试三天。"
            "以上仅供娱乐参考，不构成任何决策依据。")
    r = review.review(good, "梅花易数")
    check("合规断语通过", r["pass"], True)
    check("合规断语满分", r["score"], 100)
    # 缺白话层 → R-RV-07 失败
    no_baihua = good.replace("术语解读：体生用是泄气之象。问事解读：能成但费劲。", "")
    r5 = review.review(no_baihua)
    check("缺白话层不过", r5["pass"], False)
    check("缺白话层标R-RV-07", any(i["id"] == "R-RV-07" for i in r5["issues"]), True)
    # 有白话但缺「今日可行的一小步」→ 仍不过
    no_step = good.replace("今日可行的一小步：先小成本试三天。", "")
    r6 = review.review(no_step)
    check("缺一小步不过", r6["pass"], False)
    check("缺一小步标R-RV-07", any(i["id"] == "R-RV-07" for i in r6["issues"]), True)

    bad = "此卦大凶，不宜投资。"
    r2 = review.review(bad, "六爻纳甲")
    check("残缺断语不过", r2["pass"], False)
    check("残缺·缺三层", any(i["id"] == "R-RV-01" for i in r2["issues"]), True)
    check("残缺·缺三级标注", any(i["id"] == "R-RV-02" for i in r2["issues"]), True)
    check("残缺·缺免责", any(i["id"] == "R-RV-03" for i in r2["issues"]), True)

    # 冲突未降级 → R-RV-06 失败
    c = ("盘面事实：x。规则推演：吉。[规则推演] 现实建议：信号冲突。[主观推断] "
         "应期难定。趋吉：a。避凶：b。不构成决策依据。")
    r3 = review.review(c)
    check("冲突未降级不过", r3["pass"], False)
    check("冲突未降级标R-RV-06", any(i["id"] == "R-RV-06" for i in r3["issues"]), True)

    # 空文本
    r4 = review.review("")
    check("空文本不过", r4["pass"], False)
    check("空文本0分", r4["score"], 0)


def test_trend():
    print("[八字] 流年趋势评分（扶抑·得令简化模型）")
    import trend
    t = trend.liunian_trend(2000, 1, 1, 1, 2026, 6)
    check("趋势·日主戊", t["day_gan"], "戊")
    check("趋势·旺弱为弱", t["wang"], "弱")  # 戊土生子月失令
    check("趋势·2026丙午90", t["data"][0]["score"], 90)  # 丙午 印+印 皆喜
    check("趋势·2031辛亥10", t["data"][5]["score"], 10)  # 辛亥 食伤+财 皆忌


def test_liuyao_html():
    print("[六爻] 卦图 + 装卦辅助")
    import htmlpan
    import najia
    check("风雷益六爻", htmlpan._hexagram_lines("风雷益"), [1, 0, 0, 0, 1, 1])
    check("水风井六爻", htmlpan._hexagram_lines("水风井"), [0, 1, 1, 0, 1, 0])
    r = najia.zhuang("风雷益", "水风井", [1, 2, 3, 6], "甲寅", "丁酉")
    import tempfile
    import os
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.html")
    htmlpan.liuyao_html(r, "风雷益", "水风井", [1, 2, 3, 6], p)
    txt = open(p, encoding="utf-8").read()
    check("卦图文件生成", os.path.isfile(p), True)
    check("卦图含本卦", "风雷益" in txt, True)
    check("卦图含六神", "青龙" in txt, True)
    check("卦图含动爻标记", ("○" in txt) or ("×" in txt), True)


def test_trend_html():
    print("[八字] 流年趋势曲线")
    import htmlpan
    import trend
    import tempfile
    import os
    t = trend.liunian_trend(2000, 1, 1, 1, 2026, 6)
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.html")
    htmlpan.liunian_trend_html(t, p)
    txt = open(p, encoding="utf-8").read()
    check("曲线文件生成", os.path.isfile(p), True)
    check("曲线含svg", "<svg" in txt, True)
    check("曲线含折线", "<polyline" in txt, True)


def test_trace():
    print("[trace] 决策追踪")
    import tempfile
    import trace
    d = tempfile.mkdtemp()
    trace.record("跳槽", "梅花易数", "跳槽成不成", rules_hit=["R-MH-01"],
                 sources=["梅花易数"], conclusion="吉", confidence="中", dir_path=d)
    trace.record("求财", "六爻纳甲", "求财", rules_hit=["R-MH-01"],
                 sources=["增删卜易"], conclusion="凶", confidence="低", dir_path=d)
    trace.feedback("跳槽", "命中", "应期偏差2月", dir_path=d)
    stats = trace.analyze([os.path.join(d, "trace.jsonl")])
    check("trace 总数", stats["total"], 2)
    check("trace 方法数", stats["methods"]["梅花易数"], 1)
    check("trace 规则命中", stats["rules_hit"]["R-MH-01"], 2)
    check("trace 后验", stats["feedback_verdict"]["命中"], 1)


def test_feedback():
    print("[feedback] 反馈契约")
    import tempfile
    import feedback
    d = tempfile.mkdtemp()
    feedback.record("gap", "medium", "奇门缺XX规则", tool="rules.qimen_geju", dir_path=d)
    feedback.record("clarity", "low", "字段语义歧义", dir_path=d)
    try:
        feedback.record("bogus", "medium", "x", dir_path=d)
        check("非法类型被拒", False, True)
    except ValueError:
        check("非法类型被拒", True, True)
    stats = feedback.analyze([os.path.join(d, "feedback.jsonl")])
    check("feedback 总数", stats["total"], 2)
    check("feedback 类型", stats["types"]["gap"], 1)
    check("feedback 工具", stats["tools"]["rules.qimen_geju"], 1)


def main():
    test_bazi()
    test_zhiwei()
    test_zhiwei_palaces()
    test_zhiwei_flystar()
    test_ziwei_horoscope()
    test_bazi_shensha()
    test_xingchong()
    test_qimen_keying()
    test_hehun()
    test_liunian()
    test_liuyue()
    test_rules()
    test_precheck()
    test_tiaohou()
    test_meihua_golden()
    test_xiaoliuren_golden()
    test_liuyao_najia()
    test_zhiwei_leapmonth()
    test_liuren_golden()
    test_liuren_struct()
    test_liuren_regress()
    test_liuren_ref()
    test_jinkoujue_golden()
    test_qimen_golden()
    test_taiyi_golden()
    test_taiyi_rules()
    test_taiyi_modes()
    test_taiyi_regress()
    test_taiyi_jieqi()
    test_taiyi_html()
    test_qizheng_golden()
    test_fengshui_golden()
    test_zeri_golden()
    test_almanac()
    test_review()
    test_trend()
    test_liuyao_html()
    test_trend_html()
    test_trace()
    test_feedback()
    print(f"\n结果: {_PASS} 通过 / {_FAIL} 失败")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
