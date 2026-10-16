# -*- coding: utf-8 -*-
"""大六壬课经起例回归测试（第一刀：九宗门边界课型）。

数据源：《六壬大全》卷七~卷十「课经集」起例（`[易藏] 六壬大全.txt`）。
每条例 =「月将 + 日干支 + 时辰 + 发用（初传地支）」，原文格式「如X月X日X时X将占，Y加Z为用」。

断言：底层引擎 `engines/taiyi/kinliuren.Liuren(节气, 月, 日干支, 时干支)` 算出的
「三传·初传」地支 == 原文发用地支。这是纯排盘对拍，不涉及断语语义。

为什么先做这一刀：涉害/比用/昴星/八专/伏吟/返吟 是六壬九宗门选初传最容易误判的边界，
`SKILL.md` 已知「涉害/比用/返吟/八专边界易误判，命中存疑课时断卦须降级」。
本测试把「降级靠自觉」变成「逐课对拍可证伪」。

运行: python tests/liuren_kejing_regression.py
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

from engines.taiyi.kinliuren import Liuren
from pan import liuren as _liuren

_GAN = "甲乙丙丁戊己庚辛壬癸"
_ZHI = "子丑寅卯辰巳午未申酉戌亥"

# 五鼠遁：日干 -> 子时天干（甲己起甲子、乙庚起丙子、丙辛起戊子、丁壬起庚子、戊癸起壬子）
_WUSHUDUN = {"甲": "甲", "己": "甲", "乙": "丙", "庚": "丙", "丙": "戊",
             "辛": "戊", "丁": "庚", "壬": "庚", "戊": "壬", "癸": "壬"}

# 月将地支 -> 节气（取该月将区间首个节气，与 kinliuren moon_general_dict 对齐）
_YUEJIANG2JIEQI = {"亥": "雨水", "戌": "春分", "酉": "穀雨", "申": "小滿",
                   "未": "夏至", "午": "大暑", "巳": "處暑", "辰": "秋分",
                   "卯": "霜降", "寅": "小雪", "丑": "冬至", "子": "大寒"}


def shi_ganzhi(day_gan, hour_zhi):
    """五鼠遁：日干 + 时支 -> 时干支。"""
    zi_gan = _WUSHUDUN[day_gan]
    idx = (_GAN.index(zi_gan) + _ZHI.index(hour_zhi)) % 10
    return _GAN[idx] + hour_zhi


# (月将地支, 日干支, 时支, 期望初传地支, 课体名, 出处行号)
_CASES = [
    ("子", "甲子", "卯", "午", "元首", "3520"),
    ("申", "丁丑", "子", "巳", "元首", "3539"),
    ("申", "丙戌", "巳", "申", "重审", "3567"),
    ("酉", "乙亥", "辰", "寅", "重审", "3578"),
    ("辰", "壬辰", "巳", "戌", "知一", "3601"),
    ("亥", "丁卯", "丑", "亥", "涉害", "3642"),
    ("申", "庚子", "戌", "午", "涉害·见机", "3658"),
    ("申", "庚戌", "辰", "辰", "涉害·察微", "3672"),
    ("子", "乙卯", "寅", "亥", "比用", "3698"),
    ("申", "壬辰", "巳", "戌", "遥克·蒿矢", "3739"),
    ("亥", "壬申", "申", "巳", "遥克·弹射", "3752"),
    ("辰", "戊申", "卯", "戌", "昴星·虎视", "3810"),
    ("丑", "丁丑", "辰", "子", "昴星", "3823"),
    ("辰", "丙辰", "卯", "亥", "别责", "3862"),
    ("丑", "甲寅", "辰", "丑", "八专", "3883"),
    ("午", "癸丑", "午", "丑", "伏吟", "3953"),
    ("申", "丙辰", "申", "巳", "伏吟·自任", "3966"),
    ("未", "丁丑", "未", "丑", "伏吟·自信", "3979"),
    ("亥", "辛丑", "巳", "亥", "返吟·井栏射", "4055"),
]


def main():
    passed = failed = 0
    fails = []
    print("[大六壬] 课经起例回归：九宗门边界课型对拍（初传 == 原文发用）\n")
    for yuejiang, day_gz, hour_zhi, want, keti, line in _CASES:
        jieqi = _YUEJIANG2JIEQI[yuejiang]
        hour_gz = shi_ganzhi(day_gz[0], hour_zhi)
        lr = Liuren(jieqi, 0, day_gz, hour_gz)
        r = lr.result(1)
        # 生产路径同款交叉修正：以独立九宗门规则推导兜底 kinliuren 边界课型误判
        _liuren.correct_three_pass(r, lr, day_gz[0], day_gz[1], hour_zhi, yuejiang)
        got = r["三傳"]["初傳"][0]
        ok = got == want
        mark = "✓" if ok else "✗"
        if ok:
            passed += 1
        else:
            failed += 1
            fails.append((keti, line, day_gz, hour_gz, yuejiang, want, got))
        print(f"  {mark} {keti:12s} {day_gz}日{hour_gz}时 {yuejiang}将 初传={got}（原文{want}）")
    print(f"\n结果: {passed} 通过 / {failed} 失败（共 {len(_CASES)} 课）")
    if fails:
        print("\n失败明细（引擎初传与原文发用不一致，需复核涉害/昴星/八专/返吟选初传逻辑）：")
        for keti, line, d, h, yj, want, got in fails:
            print(f"  ✗ {keti}（行{line}）{d}日{h}时{yj}将：引擎{got} ≠ 原文{want}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
