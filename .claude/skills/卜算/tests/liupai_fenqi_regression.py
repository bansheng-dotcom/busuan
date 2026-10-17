# -*- coding: utf-8 -*-
"""流派分歧显式化回归：`rules._DETERMINISM` 12 术全覆盖 + 每术有 Und + pan_json 接入。

收口「流派分歧显式化只覆盖 6/16 术」的差距——`judge/rules.py::_DETERMINISM` 是「术法
各计算方面 → Det/Sto/Und + note」的确定性标注骨架（借鉴 mingli declare.rs），`pan_meta(shufa)`
把它 + limitation 接进各术 pan_json。本测试把「显式化」变成可复核断言：

1. 硬断言：12 个有盘计算的术全覆盖（八字/紫微/六爻/大六壬/梅花/奇门/小六壬/金口诀/
   七政四余/风水/择日/太乙），每术至少有 Det（确定性）+ Und（流派分歧显式化）。
2. 硬断言：各术 pan_json 调用了 pan_meta（确定性标注真正接进盘面事实层，非只在 rules 定义）。
3. 报告：每术的 Und 项（流派分歧点）清单。

无盘术法（相术/天文占/测字/其他）无 Det 计算层，`determinism` 返回 []，不在 12 术内。

运行: python tests/liupai_fenqi_regression.py
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

from judge import rules  # noqa: E402

# 有盘计算的 12 术（无盘的相术/天文占/测字/其他 除外）
_SHUFAS = ["八字", "紫微", "六爻", "大六壬", "梅花", "奇门", "小六壬",
           "金口诀", "七政四余", "风水", "择日", "太乙"]

# pan 模块 → 术法（pan_json 应调用 pan_meta 接确定性标注）
_PAN_TO_SHU = {
    "pan/meihua.py": "梅花", "pan/qimen.py": "奇门", "pan/qizheng.py": "七政四余",
    "pan/zhiwei.py": "紫微", "pan/fengshui.py": "风水", "pan/zeri.py": "择日",
    "pan/jinkoujue.py": "金口诀", "pan/taiyi.py": "太乙", "pan/xiaoliuren.py": "小六壬",
    "pan/liuyao.py": "六爻", "pan/liuren.py": "大六壬",
}


def main():
    d = rules._DETERMINISM
    # 1. 12 术全覆盖 + 每术有 Det/Und
    missing_shu = [s for s in _SHUFAS if s not in d]
    no_und = [s for s in _SHUFAS if s in d and not any(st == "Und" for _, st, _ in d[s])]
    no_det = [s for s in _SHUFAS if s in d and not any(st == "Det" for _, st, _ in d[s])]
    ok_cover = not missing_shu and not no_und and not no_det

    print(f"[流派分歧] 显式化回归：12 术 Det/Und 标注 + pan_json 接入\n")
    print(f"  {'✓' if ok_cover else '✗'} 12 术全覆盖（缺 {missing_shu or '无'}）；"
          f"每术有 Det（缺 {no_det or '无'}）；每术有 Und（缺 {no_und or '无'}）")

    # 2. pan_json 接入 pan_meta
    not_wired = []
    for path, shu in _PAN_TO_SHU.items():
        full = os.path.join(LIB, path)
        if not os.path.exists(full):
            not_wired.append((shu, "文件不存在"))
            continue
        src = open(full, encoding="utf-8").read()
        if "pan_meta" not in src:
            not_wired.append((shu, "pan_json 未调 pan_meta"))
    ok_wired = not not_wired
    print(f"  {'✓' if ok_wired else '✗'} pan_json 接入 pan_meta：{len(_PAN_TO_SHU)} 个模块"
          f"{('；' + str(not_wired)) if not_wired else ''}")

    # 3. 报告每术 Und 项（流派分歧点）
    print(f"\n  [Und 清单] 每术的流派分歧点：")
    for s in _SHUFAS:
        und = [f"{a}（{n}）" for a, st, n in d[s] if st == "Und"]
        print(f"    {s}: {'、'.join(und)}")

    fail = not (ok_cover and ok_wired)
    print(f"\n结果: {'失败' if fail else '通过'}（12 术 Det/Und 全覆盖 + pan_json 接入）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
