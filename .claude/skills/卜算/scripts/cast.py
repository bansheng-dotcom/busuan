# -*- coding: utf-8 -*-
"""
bushu 起盘统一入口 —— 确定性排盘，避免手工算错。

用法:
  python cast.py meihua-time                         梅花易数·时间起卦
  python cast.py meihua-num <a> [<b> [<c>]]          梅花易数·数字起卦
  python cast.py xiaoliuren                          小六壬·月日时
  python cast.py liuyao                              六爻·铜钱摇卦(含纳甲装卦)
  python cast.py bazi [年 月 日 时 分 秒 性别]        八字(默认当前, 性别1男0女)
  python cast.py liuren                              大六壬
  python cast.py qimen                               奇门遁甲
  python cast.py taiyi                               太乙神数
  python cast.py zhiwei <年 月 日 时 [性别]>           紫微斗数(公历, 性别1男0女)
  python cast.py qizheng                             七政四余·果老星宗(可 --time)
  python cast.py qizheng-liunian <出生年> <命宫地支> [流年年份]  七政四余·流年大限小限
  python cast.py fengshui [出生年] [坐向] [性别]       风水·八宅/玄空飞星
  python cast.py zeri [事项]                          择日·建除黄道神煞(可 --time)
  python cast.py zeri-month 2026-10 婚嫁 [数量]       择日·按月推荐吉日(月份 事项)
  python cast.py hehun 1990 5 15 1992 8 20          八字合婚(男女各年 月 日)
  python cast.py bazi-liunian 2000 1 1 1 2026 10    八字·流年聚合(出生年 月 日 性别 起始年 年数)
  python cast.py liuyue 2000 1 1 1 2026             八字·流月聚合(出生年 月 日 性别 流年)

  所有时间起盘的方法均可加 --time "YYYY-MM-DD HH:MM" 指定占时，缺省用当前系统时间。
"""
import os
import sys
import json
import datetime as _dt

# Windows 控制台默认 GBK，遇到 ·•→ 等符号会 UnicodeEncodeError；统一转 UTF-8 输出
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 让 libs/ 下的模块(sxtwl 垫片、engines 引擎、各排盘方法)可导入
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
sys.path.insert(0, LIB)

import meihua
import xiaoliuren
import liuyao
import bazi
import liuren
import qimen
import taiyi
import zhiwei
import qizheng
import liunian
import fengshui
import zeri
import hehun
import htmlpan
import almanac
import ziwei_horoscope
import trend


def _parse_time(args):
    """提取 --time/-t 占时、--lon 经度、--dst 夏令时回拨、--html 可视化，返回(剩余参数, dt|None, lon|None, dst_bool, html_bool)"""
    dt, lon, dst, html = None, None, False, False
    out = []
    i = 0
    while i < len(args):
        if args[i] in ("--time", "-t") and i + 1 < len(args):
            s = args[i + 1]
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = _dt.datetime.strptime(s, fmt)
                    break
                except ValueError:
                    continue
            i += 2
        elif args[i] == "--lon" and i + 1 < len(args):
            try:
                lon = float(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif args[i] in ("--dst", "-dst"):
            dst = True
            i += 1
        elif args[i] == "--html":
            html = True
            i += 1
        else:
            out.append(args[i])
            i += 1
    return out, dt, lon, dst, html


def main():
    a, dt, lon, dst, html = _parse_time(sys.argv[1:])
    cmd = a[0] if a else "meihua-time"
    if cmd in ("meihua-time", "meihua"):
        r = meihua.cast_time(dt)
        if html:
            htmlpan.meihua_html(r, f"梅花易数_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "meihua-num":
        r = meihua.cast_num(a[1:])
        if html:
            htmlpan.meihua_html(r, f"梅花易数_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "xiaoliuren":
        xiaoliuren.cast(dt)
    elif cmd == "liuyao":
        ben, bian, dong, r = liuyao.cast(dt)
        if html:
            htmlpan.liuyao_html(r, ben, bian, dong,
                                f"六爻卦图_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "bazi":
        args = [int(x) for x in a[1:]]
        gender = args[6] if len(args) > 6 else 1
        if args:
            b = bazi.cast(*args, lon=lon, dst=dst)
        else:
            b = bazi.cast(lon=lon, dst=dst)
        if html:
            htmlpan.bazi_html(b, gender, f"八字命盘_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "liuren":
        r = liuren.cast(dt)
        if html:
            htmlpan.liuren_html(r, f"大六壬_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "qimen":
        r = qimen.cast(dt)
        if html:
            htmlpan.qimen_html(r.get("時家奇門", {}), f"奇门遁甲_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "taiyi":
        taiyi.cast(dt)
    elif cmd == "zhiwei":
        args = [int(x) for x in a[1:]]
        r = zhiwei.cast(args[0], args[1], args[2], args[3], args[4] if len(args) > 4 else 1, lon=lon, dst=dst)
        zhiwei.print_pan(r)
        # 运限（大限已随命盘输出；此处补流年/流月/流日/流时四化+流曜，引擎 py-iztro）
        _target = dt.strftime("%Y-%m-%d") if dt else None
        _gender = args[4] if len(args) > 4 else 1
        print()
        print(ziwei_horoscope.format_horoscope(
            ziwei_horoscope.horoscope(args[0], args[1], args[2], args[3], _gender, target=_target)))
        if html:
            htmlpan.zhiwei_html(r, f"紫微斗数命盘_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "qizheng":
        # 七政四余·果老星宗（可 --time 指定占时）
        s = dt.strftime("%Y-%m-%d %H:%M") if dt else None
        r = qizheng.qizheng_pan(s, lon=lon) if lon is not None else qizheng.qizheng_pan(s)
        print(qizheng.format_output(r))
    elif cmd == "qizheng-liunian":
        # 七政四余·流年大限小限：<出生年> <命宫地支> [流年年份]
        birth_year = int(a[1]) if len(a) > 1 else _dt.datetime.now().year
        ming_gong = a[2] if len(a) > 2 else "子"
        ln_year = int(a[3]) if len(a) > 3 else _dt.datetime.now().year
        calc = liunian.LiuNianCalculator()
        birth_data = {"出生年份": birth_year, "命宫地支": ming_gong, "星曜位置": {}}
        print(json.dumps(calc.analyze_liu_nian(birth_data, ln_year), ensure_ascii=False, indent=2))
    elif cmd == "fengshui":
        # 风水·八宅/玄空飞星：<出生年> [坐向] [性别男/女]
        year = int(a[1]) if len(a) > 1 else _dt.datetime.now().year
        direction = a[2] if len(a) > 2 else None
        gender = a[3] if len(a) > 3 else "男"
        r = fengshui.fengshui_pan(year, direction, gender)
        print(fengshui.format_output(r))
    elif cmd == "zeri":
        # 择日·建除黄道神煞（可 --time 指定查询日；[事项] 婚嫁/开业/动土/出行/搬家/考试/求医/祭祀）
        event = a[1] if len(a) > 1 else "general"
        if dt:
            y, m, d, h = dt.year, dt.month, dt.day, dt.hour
        else:
            now = _dt.datetime.now()
            y, m, d, h = now.year, now.month, now.day, now.hour
        r = zeri.get_day_summary(y, m, d, event, h)
        print(zeri.format_output(r, event))
        # 老黄历补全（彭祖百忌/值神/吉神方位/胎神/冲煞/宜忌，出处《协纪辨方书》）
        print()
        print(almanac.format_almanac(almanac.almanac(y, m, d)))
    elif cmd == "zeri-month":
        # 择日·按月推荐吉日：zeri-month <YYYY-MM> [事项] [数量]
        if dt:
            y, m = dt.year, dt.month
            event = a[1] if len(a) > 1 else "general"
            limit = int(a[2]) if len(a) > 2 else 10
        else:
            y, m = map(int, a[1].split("-")) if len(a) > 1 else (_dt.datetime.now().year, _dt.datetime.now().month)
            event = a[2] if len(a) > 2 else "general"
            limit = int(a[3]) if len(a) > 3 else 10
        ji = zeri.tui_jian_ji_ri(y, m, event, limit)
        print(f"【{y}年{m}月吉日推荐】（{event}）")
        for i, jr in enumerate(ji, 1):
            print(f"  {i}. {jr['日期']}  评分 {jr['综合评分']}/100（{jr['等级']}）建除:{jr['建除']} 黄道:{jr['黄道']}")
        if not ji:
            print("  本月无吉日推荐")
    elif cmd == "hehun":
        # 八字合婚：hehun <男年 男月 男日 女年 女月 女日>
        args = [int(x) for x in a[1:7]]
        if len(args) < 6:
            print("用法: hehun <男年 男月 男日 女年 女月 女日>")
        else:
            hehun.cast(args[0], args[1], args[2], args[3], args[4], args[5])
    elif cmd == "bazi-liunian":
        # 八字·流年聚合：bazi-liunian <出生年 月 日 性别> [起始年] [年数]
        args = [int(x) for x in a[1:]]
        y = args[0] if len(args) > 0 else None
        mo = args[1] if len(args) > 1 else None
        d = args[2] if len(args) > 2 else None
        gender = args[3] if len(args) > 3 else 1
        start = args[4] if len(args) > 4 else None
        n = args[5] if len(args) > 5 else 10
        bazi.liunian(y, mo, d, gender, start, n)
        if html and y is not None:
            t = trend.liunian_trend(y, mo, d, gender, start, n)
            htmlpan.liunian_trend_html(t, f"八字流年趋势_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    elif cmd == "liuyue":
        # 八字·流月聚合：liuyue <出生年 月 日 性别> [流年]
        args = [int(x) for x in a[1:]]
        y = args[0] if len(args) > 0 else None
        mo = args[1] if len(args) > 1 else None
        d = args[2] if len(args) > 2 else None
        gender = args[3] if len(args) > 3 else 1
        year = args[4] if len(args) > 4 else None
        bazi.liuyue(y, mo, d, gender, year)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
