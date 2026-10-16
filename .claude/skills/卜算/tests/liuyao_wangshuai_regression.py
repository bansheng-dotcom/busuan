# -*- coding: utf-8 -*-
"""六爻「用神旺衰七查」+「吉凶判断矩阵」回归：docs/六爻纳甲.md 样例盘 golden 对拍。

`judge/liuyao_wangshuai.py` 把 docs/六爻纳甲.md 的「旺衰七查表」规范（用神/原神/忌神/
仇神/世爻 × 月令旺衰+月建日辰作用+空亡+月破+入墓+综合）与「吉凶判断矩阵」做成独立函数，
收口「六爻用神旺衰七查未代码化」的缺口。本测试用 docs 已手核的样例盘（乾为天→天泽履，
动爻3，己未日戊戌月旬空子丑）逐列对拍。

硬断言：
1. 五爻七查的月令旺衰/月破/入墓/综合 与 docs golden 一致（确定性生克冲墓表）。
2. 吉凶判断矩阵六档正确（用神休囚+忌神克+原神无力=大凶）。
3. 数据结构完整（五爻齐全 + 用神定位）。

运行: python tests/liuyao_wangshuai_regression.py
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

from pan import najia  # noqa: E402
from judge import liuyao_wangshuai as lw  # noqa: E402

# docs/六爻纳甲.md 样例盘 golden：乾为天→天泽履，动爻3，己未日戊戌月旬空子丑
# 五爻七查的确定性列（月令旺衰/月破/入墓/综合）
_GOLDEN = {
    "用神": {"六亲": "妻财", "月令": "囚", "月破": "否", "入墓": "日墓", "综合": "休囚入墓"},
    "原神": {"六亲": "子孙", "月令": "死", "月破": "否", "入墓": "否", "综合": "真空"},
    "忌神": {"六亲": "兄弟", "月令": "相", "月破": "否", "入墓": "否", "综合": "克用"},
    "仇神": {"六亲": "父母", "月令": "旺", "月破": "月破", "入墓": "否", "综合": "月破"},
    "世爻": {"六亲": "父母", "月令": "旺", "月破": "否", "入墓": "否", "综合": "旺相"},
}


def main():
    r = najia.zhuang("乾为天", "天泽履", [3], "己未", "戊戌")
    q = lw.wangshuai_qicha(r, "求财")
    rows = {row["爻名"]: row for row in q["表"]}

    print(f"[六爻] 用神旺衰七查 + 吉凶判断矩阵回归（docs 样例盘 golden 对拍）\n")
    bad = []
    for name, g in _GOLDEN.items():
        row = rows.get(name)
        if not row:
            bad.append((name, "缺行", g))
            continue
        # 月令/月破/入墓/综合 逐列对拍
        for col in ("月令", "月破", "入墓", "综合"):
            got = row.get(col, "")
            want = g[col]
            if col == "综合":
                ok = want in got
            elif col == "入墓":
                ok = (want in got) if want != "否" else (got == "否")
            elif col == "月破":
                ok = (got == want) if want == "否" else (want in got)
            else:
                ok = got == want
            if not ok:
                bad.append((name, col, got, want))

    print(f"  {'✓' if not bad else '✗'} 五爻七查对拍（月令/月破/入墓/综合）")
    for name, col, got, want in bad:
        print(f"      ✗ {name}.{col}: 得「{got}」≠ 期望「{want}」")
    for name, g in _GOLDEN.items():
        row = rows[name]
        print(f"      {name:3s}{row['六亲'] or '—':4s} 落{row['落']:>4s} 月令{row['月令']:2s} "
              f"破{row['月破']:2s} 墓{row['入墓']:4s} | {row['综合']}")

    # 吉凶判断矩阵
    jz = lw.jixiong_juzhen(r, "求财")
    ok_jz = jz["档"] == "大凶" and jz["用神状态"] in ("衰", "死")
    print(f"\n  {'✓' if ok_jz else '✗'} 吉凶判断矩阵：{jz['档']}（用神{jz['用神状态']}，原神{jz['原神']}，忌神{jz['忌神']}）")

    # 数据结构完整
    ok_struct = len(rows) == 5 and all(n in rows for n in ("用神", "原神", "忌神", "仇神", "世爻"))
    print(f"  {'✓' if ok_struct else '✗'} 数据结构完整（五爻齐全 + 用神定位）")

    fail = bool(bad) or (not ok_jz) or (not ok_struct)
    print(f"\n结果: {'失败' if fail else '通过'}（五爻七查 golden 对拍 + 判断矩阵六档 + 结构完整）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
