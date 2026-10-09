# -*- coding: utf-8 -*-
"""奇门遁甲排盘（引擎: kentang2017/kinqimen）"""
import datetime
from engines.qimen import Qimen
from qimen_angan import angan_from_sj

_GONG_GUA = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "中", 6: "乾", 7: "兌", 8: "艮", 9: "離"}


def cast(dt=None):
    dt = dt or datetime.datetime.now()
    q = Qimen(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    r = q.overall(2)   # 2=置闰法, 1=拆补法
    sj = r.get("時家奇門", {})
    print(f"[奇门遁甲] {dt:%Y-%m-%d %H:%M}")
    print(f"排盘: {sj.get('排盤方式', '')}  局: {sj.get('排局', '')}  节气: {sj.get('節氣', '')}")
    print(f"干支: {sj.get('干支', '')}  旬空: {sj.get('旬空', '')}")
    print(f"值符值使: {sj.get('值符值使', '')}")
    print(f"八门: {sj.get('八門', sj.get('門', ''))}")
    star = sj.get('九星', sj.get('星', '')) or {}
    if isinstance(star, dict):
        # 引擎把天芮与天禽合并为「禽」(天禽寄宫随天芮)，此处显式还原天芮，避免漏断凶星
        star = {k: ("芮·禽" if v == "禽" else v) for k, v in star.items()}
        print(f"九星: {star}（注：天禽寄宫随天芮，「芮·禽」处实为天芮+天禽同宫）")
    else:
        print(f"九星: {star}")
    # 暗干（飞干）：值使加时干，阳顺阴逆飞九宫（洛书展示序：巽离坤/震中兑/艮坎乾）
    ag = angan_from_sj(sj)
    if ag:
        pan, shi_gan = ag
        s = "  ".join(f"{_GONG_GUA[g]}{pan.get(g, '')}" for g in (4, 9, 2, 3, 5, 7, 8, 1, 6))
        print(f"暗干: {s}（值使加时干「{shi_gan}」阳顺阴逆飞九宫）")
    return r
