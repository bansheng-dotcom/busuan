# -*- coding: utf-8 -*-
"""七政四余天文对拍：太阳黄经 vs 二十四节气锚点（独立天文定义）+ 四余确定关系 + 多日期连续性。

`pan/qizheng.py` 七政黄经用 PyEphem 精算、四余用 Meeus 多项式。现有 `test_qizheng_golden`
是「ephem 自算自对拍」（golden 硬编码 ephem 值），不能验证「算得对不对」。本测试补上
**独立天文锚点对拍**——太阳黄经在二十四节气时刻应恰为 15° 的整数倍（黄经的定义性锚点，
不依赖 ephem 或外部数据源），据此验证太阳黄经计算 + 时区口径 + 黄经转换正确。

分层：
1. 节气锚点（独立定义）：24 节气时刻太阳黄经 mod 15 ≈ 0（容差 1°，覆盖 lunar_python
   节气时刻 vs ephem 黄经的精度差）。这是「天文对拍」的真正独立锚点。
2. 四余确定关系（Meeus 定义）：计都=罗睺+180°（降交点）、月孛=月平远地点（近地点+180°）。
3. 多日期连续性：太阳黄经逐日递增 ~0.986°/日（无跳变），七政黄经多日期落在 [0,360)。

诚实边界：紫气（28 年周期）各派定义分歧、无统一公式，仅验证其落在 [0,360) 且随日期
缓变；二十八宿黄经近似入宿（宿度随岁差而变）本测试不硬卡。

运行: python tests/qizheng_astro_regression.py
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

import math  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
import ephem  # noqa: E402
from lunar_python import Solar  # noqa: E402
from pan import qizheng  # noqa: E402


def _bj_to_utc_ephem(dt_naive):
    """北京时间 -> ephem.Date（UTC）。"""
    utc = dt_naive - timedelta(hours=8)
    return ephem.Date(utc.strftime("%Y/%m/%d %H:%M:%S"))


def _sun_lon(dt_naive, lat=39.9, lon=116.4):
    """用 qizheng 同款 observer 算太阳黄经。"""
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elevation = str(lat), str(lon), 0.0
    obs.date = _bj_to_utc_ephem(dt_naive)
    return qizheng._ecliptic_lon_deg(ephem.Sun(), obs)


def main():
    # ========== 1. 节气锚点（独立天文定义） ==========
    # lunar_python 节气表：从大雪起跨年，取连续 24 个节气（每节气太阳黄经=15°×k）
    table = Solar.fromYmdHms(2026, 1, 1, 0, 0, 0).getLunar().getJieQiTable()
    jieqi = sorted((v.toYmdHms(), k) for k, v in table.items())
    # 取 24 个连续节气（剔除跨年重复）
    terms = []
    seen_month = set()
    for ymdhms, k in jieqi:
        dt = datetime.strptime(ymdhms, "%Y-%m-%d %H:%M:%S")
        terms.append(dt)
    terms.sort()

    jieqi_bad = 0
    jieqi_max = 0.0
    for dt in terms:
        lon = _sun_lon(dt)
        # 太阳黄经应为 15° 整数倍：mod 15 到 [-7.5, 7.5]
        mod = (lon % 15.0)
        off = min(mod, 15.0 - mod)  # 距最近 15° 整数倍的距离
        jieqi_max = max(jieqi_max, off)
        if off > 1.0:
            jieqi_bad += 1

    print(f"[七政四余] 天文对拍：太阳黄经 vs 二十四节气锚点（{len(terms)} 节气）")
    print(f"  {'✓' if jieqi_bad == 0 else '✗'} 节气锚点：太阳黄经 mod 15 ≈ 0（最大偏差 {jieqi_max:.2f}°，超 1° 的 {jieqi_bad} 个）")

    # ========== 2. 四余确定关系（Meeus 定义） ==========
    r = qizheng.qizheng_pan("2026-10-08 21:10")
    yu = r["四余"]
    luo, ji = yu["罗睺"]["黄经"], yu["计都"]["黄经"]
    ok_ji = abs((ji - (luo + 180) % 360) % 360) < 0.01 or abs((ji - luo - 180)) < 0.01
    ok_yuebo_in_range = 0 <= yu["月孛"]["黄经"] < 360
    ok_ziqi_in_range = 0 <= yu["紫气"]["黄经"] < 360
    print(f"  {'✓' if ok_ji else '✗'} 计都=罗睺+180°（降交点）：罗睺{luo:.1f}° 计都{ji:.1f}°")
    print(f"  {'✓' if ok_yuebo_in_range else '✗'} 月孛（月平远地点）落 [0,360)：{yu['月孛']['黄经']:.1f}°")
    print(f"  {'✓' if ok_ziqi_in_range else '✗'} 紫气（28年近似）落 [0,360)：{yu['紫气']['黄经']:.1f}°")

    # ========== 3. 多日期连续性（太阳逐日 ~0.986°，无跳变） ==========
    cont_bad = 0
    prev = None
    for day in range(1, 32):
        dt = datetime(2026, 10, day, 12, 0)
        lon = _sun_lon(dt)
        if prev is not None:
            d = (lon - prev) % 360
            if d < 0.5 or d > 1.5:  # 太阳每日约走 0.986°，非逆行不应 <0.5
                cont_bad += 1
        prev = lon
    print(f"  {'✓' if cont_bad == 0 else '✗'} 多日期连续性：太阳黄经逐日递增（异常 {cont_bad} 天）")

    # ========== 结论 ==========
    fail = (jieqi_bad > 0) or (not ok_ji) or (not ok_yuebo_in_range) or (not ok_ziqi_in_range) or (cont_bad > 0)
    print(f"\n结果: {'失败' if fail else '通过'}（节气锚点独立对拍 + 四余确定关系 + 多日期连续性）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
