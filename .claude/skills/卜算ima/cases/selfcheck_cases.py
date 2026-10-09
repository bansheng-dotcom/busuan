# -*- coding: utf-8 -*-
"""古籍案例排盘一致性自检：用古籍记录核对脚本排盘是否正确。

1. 六爻：卦名/变卦 是否匹配标准 64 卦名（找出异写/别名，验证卦名映射完整性）。
2. 六壬：日干支的旬空 vs 古籍记「X空亡」（旬空是确定性算法，可硬核对）。
3. 梅花：观梅占起卦数理复现（辰年5/十二月12/十七日17/申时9 → 泽火革初爻动）。

用法：python cases/selfcheck_cases.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts", "libs"))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from gua import GUA64, YAO

_STD64 = set(GUA64.values())
DIZHI = "子丑寅卯辰巳午未申酉戌亥"
TIANGAN = "甲乙丙丁戊己庚辛壬癸"


def xunkong(day_gz):
    """日干支 → 旬空两字（如 '申酉'）。"""
    gan = day_gz[0]; zhi = day_gz[1]
    g = TIANGAN.index(gan); z = DIZHI.index(zhi)
    # 旬首天干 = 甲；旬首地支 = 从日支往回数 g 位
    xunshou_zhi = (z - g) % 12
    # 旬空 = 旬首前两位（即旬尾后两位）：甲子旬空戌亥 → 旬首地支往前2位
    kong1 = DIZHI[(xunshou_zhi - 2) % 12]
    kong2 = DIZHI[(xunshou_zhi - 1) % 12]
    return kong1 + kong2


def selfcheck_liuyao():
    print("=" * 52)
    print("【自检1】六爻卦名 / 变卦 匹配标准 64 卦名")
    d = json.load(open(os.path.join(HERE, "liuyao", "_tianji_guaili.json"), encoding="utf-8"))
    gl = d["卦例"]
    bad_gua = set(); bad_bian = set()
    for c in gl:
        if c.get("卦名") and c["卦名"] not in _STD64:
            bad_gua.add(c["卦名"])
        if c.get("变卦") and c["变卦"] not in _STD64 and "静" not in c["变卦"]:
            bad_bian.add(c["变卦"])
    print(f"本卦不匹配: {len(bad_gua)} 个异写 → {sorted(bad_gua)}")
    print(f"变卦不匹配: {len(bad_bian)} 个异写 → {sorted(bad_bian)}")
    return bad_gua, bad_bian


def selfcheck_liuren():
    print("=" * 52)
    print("【自检2】六壬日干支旬空 vs 古籍记「X空亡」")
    ok = bad = 0
    bad_cases = []
    for f in sorted(os.listdir(os.path.join(HERE, "liuren"))):
        if not f.endswith(".md") or f.startswith("_"): continue
        txt = open(os.path.join(HERE, "liuren", f), encoding="utf-8").read()
        # 标题：如 "01）韩太守占祈雪...己卯日寅将酉时，（申酉空亡,丑寅落空）..."
        m = re.search(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日[子丑寅卯辰巳午未申酉戌亥]将.*?（([子丑寅卯辰巳午未申酉戌亥]{2})空亡", txt)
        if not m:
            m = re.search(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日", txt)
            if not m:
                continue
            # 无空亡记录，跳过
            continue
        day_gz, guji_kong = m.group(1), m.group(2)
        calc_kong = xunkong(day_gz)
        if set(calc_kong) == set(guji_kong):
            ok += 1
        else:
            bad += 1
            bad_cases.append((f, day_gz, guji_kong, calc_kong))
    print(f"旬空核对: 一致 {ok} · 不一致 {bad}")
    for f, gz, guji, calc in bad_cases[:10]:
        print(f"  ✗ {f}: {gz}日 古籍记{guji}空亡 脚本算{calc}")


def selfcheck_meihua():
    print("=" * 52)
    print("【自检3】梅花易数 观梅占 起卦数理复现")
    # 观梅占：辰年5、十二月12、十七日17、申时9
    # 上卦 = (5+12+17) % 8 = 34 % 8 = 2 → 兑；下卦 = (5+12+17+9) % 8 = 43 % 8 = 3 → 离；动爻 = 43 % 6 = 1
    nian, yue, ri, shi = 5, 12, 17, 9
    shang = (nian + yue + ri) % 8 or 8
    xia = (nian + yue + ri + shi) % 8 or 8
    dong = (nian + yue + ri + shi) % 6 or 6
    from gua import GUA
    gua_name = None
    for (s, x), name in GUA64.items():
        if s == shang and x == xia:
            gua_name = name
            break
    print(f"上卦={GUA[shang]} 下卦={GUA[xia]} 动爻={dong} → 本卦 {gua_name}")
    print(f"古籍记「泽火革，初爻变咸」 → 本卦应为 泽火革，动爻第1爻")
    print(f"核对: 上兑下离={'✓' if shang==2 and xia==3 else '✗'} 动爻1={'✓' if dong==1 else '✗'}")


if __name__ == "__main__":
    selfcheck_liuyao()
    print()
    selfcheck_liuren()
    print()
    selfcheck_meihua()
