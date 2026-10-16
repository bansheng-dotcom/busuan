# -*- coding: utf-8 -*-
"""梅花「错综复三观」回归：64 卦全量卦变对拍 + 反对形态分类 + 排盘接入。

把「错/综/复」三观的卦变操作变成可证伪断言（对标 henrryjoke/shefu 的反对体用 + 变复求义）：
1. 硬断言：64 卦全量，错/综/复三观与「独立三爻错综表」推导的结果逐卦一致。
2. 硬断言：反对形态三类（自反对体 8 卦 / 反=对 8 卦 / 标准四卦组 48 卦）覆盖 64 卦无遗漏。
3. 硬断言：已知卦例（乾错坤、泰综否、既济综未济、乾自反、颐自反）。
4. 硬断言：meihua 排盘输出已接入错/综/复字段。

运行: python tests/meihua_cuozongfu_regression.py
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

from gua import YAO, cuo, zong, fu, liu_of, name_of, hexagram_name  # noqa: E402
from judge import meihua_cuozongfu as mcz  # noqa: E402

# —— 独立三爻错/综表（不复用 gua.cuo/zong/fu，独立推导 64 卦卦变） ——
_TRIGRAM_CUO = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}   # 三爻错卦（阴阳全变）
_TRIGRAM_ZONG = {1: 1, 2: 5, 3: 3, 4: 7, 5: 2, 6: 6, 7: 4, 8: 8}   # 三爻综卦（上下颠倒）


def ref_cuo64(shang, xia):
    """错卦 = 上下卦各自错。"""
    return hexagram_name(_TRIGRAM_CUO[shang], _TRIGRAM_CUO[xia])


def ref_zong64(shang, xia):
    """综卦 = 下卦之综为外卦、上卦之综为内卦（六爻上下颠倒）。"""
    return hexagram_name(_TRIGRAM_ZONG[xia], _TRIGRAM_ZONG[shang])


def ref_fu64(shang, xia, which):
    """复卦 = 上体/下体各自翻为错卦（偏变）。"""
    return (hexagram_name(_TRIGRAM_CUO[shang], xia) if which == "上"
            else hexagram_name(shang, _TRIGRAM_CUO[xia]))


# —— 反对形态三类卦名（独立硬编码，玄明《反对篇》） ——
_SELF_FAN = {"乾为天", "坤为地", "坎为水", "离为火", "山雷颐", "泽风大过", "风泽中孚", "雷山小过"}
_FAN_EQ_DUI = {"地天泰", "天地否", "泽雷随", "山风蛊", "风山渐", "雷泽归妹", "水火既济", "火水未济"}


def main():
    # —— 1. 64 卦全量卦变对拍 ——
    cuo_bad = zong_bad = fu_bad = 0
    for shang in range(1, 9):
        for xia in range(1, 9):
            liu = liu_of(shang, xia)
            if name_of(cuo(liu)) != ref_cuo64(shang, xia):
                cuo_bad += 1
            if name_of(zong(liu)) != ref_zong64(shang, xia):
                zong_bad += 1
            if name_of(fu(liu, "上")) != ref_fu64(shang, xia, "上"):
                fu_bad += 1
            if name_of(fu(liu, "下")) != ref_fu64(shang, xia, "下"):
                fu_bad += 1

    # —— 2. 反对形态分类 64 卦全量 ——
    self_fan = fan_eq_dui = standard = 0
    type_bad = []
    for shang in range(1, 9):
        for xia in range(1, 9):
            liu = liu_of(shang, xia)
            kind, _ = mcz.fan_dui_type(liu)
            ben = name_of(liu)
            if kind == "自反对体":
                self_fan += 1
                if ben not in _SELF_FAN:
                    type_bad.append((ben, "误入自反对体"))
            elif kind == "反=对":
                fan_eq_dui += 1
                if ben not in _FAN_EQ_DUI:
                    type_bad.append((ben, "误入反=对"))
            else:
                standard += 1
                if ben in _SELF_FAN or ben in _FAN_EQ_DUI:
                    type_bad.append((ben, "误入标准四卦组"))

    # —— 3. 已知卦例硬断言 ——
    known = [
        ("乾错坤", name_of(cuo(liu_of(1, 1))) == "坤为地"),
        ("乾综乾(自反)", name_of(zong(liu_of(1, 1))) == "乾为天"),
        ("乾复上=泰", name_of(fu(liu_of(1, 1), "上")) == "地天泰"),
        ("乾复下=否", name_of(fu(liu_of(1, 1), "下")) == "天地否"),
        ("泰综否", name_of(zong(liu_of(8, 1))) == "天地否"),
        ("泰错否(反=对)", name_of(cuo(liu_of(8, 1))) == "天地否"),
        ("既济综未济", name_of(zong(liu_of(6, 3))) == "火水未济"),
        ("颐综颐(自反)", name_of(zong(liu_of(7, 4))) == "山雷颐"),
    ]
    known_bad = [n for n, ok in known if not ok]

    # —— 4. 会合参证完整性 ——
    hecan_bad = 0
    for shang in range(1, 9):
        for xia in range(1, 9):
            r = mcz.hecan(shang, xia, 2)
            if len(r["六观"]) != 7 or not r["反对形态"] or not r["参证结论"]:
                hecan_bad += 1

    print("[梅花] 错综复三观回归：64 卦全量卦变对拍 + 反对形态分类 + 排盘接入")
    print(f"  {'✓' if cuo_bad == 0 else '✗'} 错卦 64 卦全量对拍：错 {cuo_bad}")
    print(f"  {'✓' if zong_bad == 0 else '✗'} 综卦 64 卦全量对拍：错 {zong_bad}")
    print(f"  {'✓' if fu_bad == 0 else '✗'} 复卦 64 卦全量对拍：错 {fu_bad}")
    print(f"  {'✓' if not type_bad else '✗'} 反对形态分类：自反{self_fan} / 反=对{fan_eq_dui} / 标准{standard}（应 8/8/48）")
    if type_bad:
        for b in type_bad[:6]:
            print(f"      {b}")
    print(f"  {'✓' if not known_bad else '✗'} 已知卦例 8 则：{'、'.join(n for n, _ in known)}")
    if known_bad:
        print(f"      失败：{known_bad}")
    print(f"  {'✓' if hecan_bad == 0 else '✗'} 会合参证 64 卦全量六观完整：坏 {hecan_bad}")

    # —— 5. 排盘接入（meihua._build 输出含错/综/复） ——
    from pan import meihua as _mh
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = _mh.cast_num([3, 8])
    pan_ok = all(k in r for k in ("错卦", "综卦", "复卦上", "复卦下"))
    print(f"  {'✓' if pan_ok else '✗'} 排盘接入：meihua 输出含 错卦/综卦/复卦上/复卦下")

    fail = (cuo_bad or zong_bad or fu_bad or type_bad or known_bad or hecan_bad or not pan_ok)
    print(f"\n结果: {'失败' if fail else '通过'}（64 卦全量卦变对拍 + 反对形态 8/8/48 + 排盘接入）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
