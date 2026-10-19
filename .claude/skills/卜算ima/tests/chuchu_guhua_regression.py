# -*- coding: utf-8 -*-
"""出处固化审计：judge/ 断语模块「出处」字段覆盖 + rules.py 规则函数出处固化率。

收口 P2「出处是临时 Grep、非规则固化」——对标 tianzhi-core「每条规则在代码里固化出处，
可机器回查」，而不是「断卦那一刻临时 Grep」。本测试把「出处固化」变成可复核断言：

1. 硬断言：judge/ 的断语模块（断语→判定条件→出处 的链）都带 src/出处/SOURCE 字段。
2. 报告：rules.py 规则函数的出处固化率——「断语类」应带书名出处、「确定性算法类」
   （体用生克/月令旺衰/建除等五行规则）标「规则推演」可无书名，如实列「无出处」清单。

运行: python tests/chuchu_guhua_regression.py
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

# judge/ 断语模块（断语→判定条件→出处 的链），每个应有 src/出处/SOURCE 字段
_DUANYU_MODULES = {
    "liuyao_duanyu.py": "src", "ziwei_geju_data.py": "src",
    "miaogong_shefu.py": "SOURCE", "qimen_keying.py": "SOURCE",
    "ziwei_xian.py": "SRC", "cezi.py": "SOURCE",
    "liuyao_wangshuai.py": "SOURCE",
}


def main():
    judge_dir = os.path.join(LIB, "judge")
    # 1. 断语模块出处字段
    missing = []
    for fname, field in _DUANYU_MODULES.items():
        path = os.path.join(judge_dir, fname)
        if not os.path.exists(path):
            missing.append((fname, "文件不存在"))
            continue
        src = open(path, encoding="utf-8").read()
        if field not in src:
            missing.append((fname, f"缺 {field} 字段"))
    ok_duanyu = not missing

    print(f"[出处固化] 审计：judge/ 断语模块出处字段 + rules.py 规则函数出处固化率\n")
    print(f"  {'✓' if ok_duanyu else '✗'} 断语模块出处字段：{len(_DUANYU_MODULES)} 个模块"
          f"{('；' + str(missing)) if missing else ''}")

    # 2. rules.py 规则函数出处固化率（报告）
    src = open(os.path.join(LIB, "judge", "rules.py"), encoding="utf-8").read()
    blocks = src.split("def ")
    no_chuchu = []
    total_rule = 0
    for b in blocks[1:]:
        name = b.split("(")[0].strip()
        if name.startswith(("meihua", "qimen", "liuyao", "liuren", "bazi",
                            "taiyi", "jinkoujue", "xiaoliuren", "zeri")):
            total_rule += 1
            if "出处" not in b and "《" not in b:
                no_chuchu.append(name)
    rate = 1 - len(no_chuchu) / total_rule if total_rule else 0
    print(f"  rules.py 规则函数 {total_rule} 个，带书名出处 {total_rule - len(no_chuchu)} 个，"
          f"固化率 {rate:.0%}")
    if no_chuchu:
        print(f"    无书名出处（确定性算法类，标规则推演即可）：{'、'.join(no_chuchu)}")

    # 3. 规则编号一致性（文档语义一致：docs/SKILL.md 引用的 R-编号，代码里都有实现）
    import glob
    defined = set()
    for f in glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True):
        try:
            s = open(f, encoding="utf-8").read()
        except Exception:
            continue
        defined |= set(re.findall(r"R-[A-Z]+-[0-9]+", s))
    referenced = set()
    for f in glob.glob(os.path.join(LIB, "..", "..", "docs", "*.md")) + \
                [os.path.join(LIB, "..", "..", "SKILL.md")]:
        try:
            s = open(f, encoding="utf-8").read()
        except Exception:
            continue
        referenced |= set(re.findall(r"R-[A-Z]+-[0-9]+", s))
    dead = referenced - defined
    ok_bianhao = not dead
    print(f"  {'✓' if ok_bianhao else '✗'} 规则编号一致性：docs 引用 {len(referenced)} 个 R-编号，"
          f"代码实现 {len(defined)} 个，死引用 {sorted(dead) if dead else '无'}")

    fail = not (ok_duanyu and ok_bianhao)
    print(f"\n结果: {'失败' if fail else '通过'}（断语模块出处字段 + 规则编号一致性；规则函数固化率仅报告）")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
