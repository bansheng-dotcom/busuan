# -*- coding: utf-8 -*-
"""架构测试：依赖只向内（借鉴 mingli/crates/mingli-registry/tests/architecture.rs）。

层（从下到上）：lifa(历法·Det) < pan(排盘·Det) < judge(判断·Und/Int) < gate(质检)。
规则：低层不得 import 高层。违规会暴露「排盘与判断混在一起」的架构债务。

运行: python tests/architecture_test.py
"""
import re
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "scripts", "libs")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 模块 → 层
_LAYER = {}
for m in ["taiyangshi", "almanac"]:
    _LAYER[m] = "lifa"
for m in ["meihua", "xiaoliuren", "liuyao", "liuren", "jinkoujue", "qimen", "taiyi",
          "bazi", "zhiwei", "qizheng", "fengshui", "zeri", "najia", "hehun",
          "liunian", "bazi_liunian", "bazi_json"]:
    _LAYER[m] = "pan"
for m in ["rules", "tiaohou", "bazi_evaluator", "liuren_bifa", "liuren_shensha",
          "qimen_keying", "qimen_angan", "adversarial", "trend", "shefu_portrait",
          "miaogong_shefu", "shiwu_xunren"]:
    _LAYER[m] = "judge"
for m in ["review", "precheck"]:
    _LAYER[m] = "gate"

_LEVEL = {"lifa": 0, "pan": 1, "judge": 2, "gate": 3}


def _file_layer(fp):
    p = fp.replace("\\", "/")
    for l in ("lifa", "pan", "judge", "gate"):
        if f"/libs/{l}/" in p:
            return l
    return "util"


def scan_violations():
    """扫描 scripts/libs 下各 .py 的跨层 import，返回 [(文件层, 目标层, 模块, 文件名)]。"""
    viol = []
    for fp in glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True):
        fl = _file_layer(fp)
        if fl == "util":
            continue
        src = open(fp, encoding="utf-8").read()
        # from pan.X import / from lifa.X import / ...
        for m in re.finditer(r"from (pan|lifa|judge|gate)\.(\w+) import", src):
            mod = m.group(2)
            if mod in _LAYER and _LEVEL[_LAYER[mod]] > _LEVEL[fl]:
                viol.append((fl, _LAYER[mod], mod, os.path.basename(fp)))
        # from judge import rules 形式（顶层 from X import 模块）
        for m in re.finditer(r"from (pan|lifa|judge|gate) import (\w+)", src):
            mod = m.group(2)
            if mod in _LAYER and _LEVEL[_LAYER[mod]] > _LEVEL[fl]:
                viol.append((fl, _LAYER[mod], mod, os.path.basename(fp)))
    return viol


def main():
    viol = scan_violations()
    by_kind = {}
    for fl, tl, mod, fn in viol:
        by_kind.setdefault((fl, tl), []).append((mod, fn))

    _PASS = _FAIL = 0

    def check(name, got, want):
        nonlocal _PASS, _FAIL
        ok = got == want
        _PASS += ok
        _FAIL += (not ok)
        print(f"  {'✓' if ok else '✗'} {name}: {got}" + ("" if ok else f"，期望 {want}"))

    print("[架构] 依赖只向内（低层不得 import 高层）")

    # lifa（历法）是地基，必须 0 违规
    lifa_up = sum(len(v) for k, v in by_kind.items() if k[0] == "lifa")
    check("lifa→上层违规数", lifa_up, 0)

    # pan 不得 import gate（质检是最高层）
    pan_gate = sum(len(v) for k, v in by_kind.items() if k == ("pan", "gate"))
    check("pan→gate违规数", pan_gate, 0)

    # judge 不得 import gate
    judge_gate = sum(len(v) for k, v in by_kind.items() if k == ("judge", "gate"))
    check("judge→gate违规数", judge_gate, 0)

    # pan→judge 是「排盘内联断卦」的已知债务，登记基线、不许再涨
    pan_judge = sum(len(v) for k, v in by_kind.items() if k == ("pan", "judge"))
    print(f"  · pan→judge 已知债务 {pan_judge} 处（排盘 cast() 内联调 rules 断卦，待拆分）")
    check("pan→judge不超过基线(19)", pan_judge <= 19, True)

    if _FAIL:
        print("\n越层详情：")
        for (fl, tl), items in sorted(by_kind.items()):
            for mod, fn in items:
                print(f"  {fl} → {tl}: {fn} import {mod}")
    print(f"\n结果: {_PASS} 通过 / {_FAIL} 失败")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()