# -*- coding: utf-8 -*-
"""排盘确定性回归测试。

只测「排盘是否算对」（脚本层、可机器验证），不测「断卦是否断准」（推理层，见 ../cases/）。

运行: python tests/regression_test.py
"""
import os
import sys

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


def test_bazi_shensha():
    print("[八字] 神煞（戊午日主）")
    from lunar_python import Solar
    from bazi import _shensha
    b = Solar.fromYmdHms(2000, 1, 1, 8, 0, 0).getLunar().getEightChar()
    names = [n for n, _ in _shensha(b)]
    check("神煞", ",".join(names), "桃花,将星,羊刃")


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


def main():
    test_bazi()
    test_zhiwei()
    test_bazi_shensha()
    test_hehun()
    test_liunian()
    test_rules()
    test_precheck()
    test_tiaohou()
    print(f"\n结果: {_PASS} 通过 / {_FAIL} 失败")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
