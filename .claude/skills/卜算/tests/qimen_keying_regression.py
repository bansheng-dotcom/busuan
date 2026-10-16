# -*- coding: utf-8 -*-
"""奇门十干克应 81 格局回归：KEYING vs 《奇门遁甲秘笈大全》「十干尅应诀」原文。

把 `judge/qimen_keying.py` 的 KEYING（9 天盘干 × 9 地盘干 = 81 条）逐条对拍原文格局名。
这是数据校对（不是逻辑测试）：KEYING 声称「格局名以原文为准」，本测试把这句话变成可证伪的断言。

原文格式多变（段首「X加Y」、后续「加Y」省略主干、纳甲别名「甲子戊/日奇六乙」等），
解析器在此做归一化；个别条原文诀里未标格局名（如庚加壬「远行失迷道路」），KEYING 从
卷十总论补「小格」，这类条目单独标注不判错。

运行: python tests/qimen_keying_regression.py
"""
import os
import re
import sys

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "libs")
sys.path.insert(0, LIB)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from judge import qimen_keying

_TXT = r"D:\卜算\国学czhengli\txt\[易藏] 奇门遁甲秘笈大全.txt"

# 地盘干别名 -> 干（纳甲六仪 + 三奇别名）
_NAJIA = {"甲子戊": "戊", "甲戌己": "己", "甲申庚": "庚", "甲午辛": "辛",
          "甲辰壬": "壬", "甲寅癸": "癸"}
_QIYI = {"日奇六乙": "乙", "月奇六丙": "丙", "星奇六丁": "丁",
         "日奇": "乙", "月奇": "丙", "星奇": "丁"}
_GAN = "乙丙丁戊己庚辛壬癸"


def _dipan(text):
    """从「加XXX…」提取地盘干——只匹配「加」与「为/曰/名/谓之」之间的子串，避免误配格局名里的字。"""
    m = re.match(r"加(.+?)(?:名曰格名|名曰|名为|名|曰|为|谓之)", text)
    if not m:
        return None
    seg = m.group(1)
    for a, g in _NAJIA.items():
        if a in seg:
            return g
    for a, g in _QIYI.items():
        if a in seg:
            return g
    m2 = re.match(r"([%s])" % _GAN, seg)
    return m2.group(1) if m2 else None


def parse_keying_jue():
    """解析「十干尅应诀」，返回 [(天盘干, 地盘干, 格局名或None), ...]。"""
    lines = open(_TXT, encoding="utf-8").read().splitlines()
    start = next(i for i, l in enumerate(lines) if "十干尅应诀" in l or "十干尅应" in l)
    cur = None
    result = []
    for l in lines[start + 1:]:
        l = l.strip()
        if not l:
            continue
        if "时加六甲" in l:  # 下一个章节，结束
            break
        if "六甲同六戊" in l:  # 说明句，非条目
            continue
        # 段首明确主干「X加…」：记录主干，去掉行首干，使「加Y…」与后续格式统一
        m = re.match(r"^([%s])加" % _GAN, l)
        if m:
            cur = m.group(1)
            l = l[1:]
        d = _dipan(l)
        if not (cur and d):
            continue
        name = None
        m = re.search(r"[“\"]([^”\"]+)[”\"]", l)
        if m:
            name = m.group(1)
        result.append((cur, d, name))
    return result


def main():
    parsed = parse_keying_jue()
    print(f"[奇门] 十干克应 81 格局对拍：KEYING vs 《奇门遁甲秘笈大全》十干尅应诀")
    print(f"  解析出 {len(parsed)} 条（应为 81）\n")

    # 完整性
    n, missing, extra = qimen_keying.completeness()
    ok_complete = (n == 81 and not missing and not extra)
    print(f"  {'✓' if ok_complete else '✗'} KEYING 完整性：{n} 条，缺失 {missing or '无'}，越界 {extra or '无'}")

    # 格局名逐条对拍
    keying = qimen_keying.KEYING
    mism = []
    noparse = []
    checked = 0
    for tian, di, name in parsed:
        if name is None:
            # 原文诀里未标格局名（如庚加壬），KEYING 若有则标注补名
            if (tian, di) in keying:
                noparse.append((tian, di, keying[(tian, di)][0]))
            continue
        checked += 1
        if (tian, di) not in keying:
            mism.append((tian, di, name, "<KEYING 缺失>"))
        elif keying[(tian, di)][0] != name:
            mism.append((tian, di, name, keying[(tian, di)][0]))

    print(f"  ✓ 逐条对拍 {checked} 条（有格局名的）")
    if mism:
        print(f"  ✗ 格局名不一致 {len(mism)} 条：")
        for t, d, yuan, key in mism:
            print(f"      {t}加{d}：原文「{yuan}」≠ KEYING「{key}」")
    else:
        print(f"  ✓ 格局名全部一致")
    if noparse:
        print(f"  ⚠ 原文诀未标格局名、KEYING 补名 {len(noparse)} 条：")
        for t, d, key in noparse:
            print(f"      {t}加{d}：KEYING 补「{key}」")

    fail = (not ok_complete) or len(mism) > 0
    print(f"\n结果: {'失败' if fail else '通过'}（81 完整性 + 格局名对拍）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
