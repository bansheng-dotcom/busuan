# -*- coding: utf-8 -*-
"""案例库管理：新建案例（分术法子目录）、统计后验命中率、查看 gold 样例、列出各术案例数。

用法:
  python cases/manage.py new "跳槽成不成" 梅花易数   # 在 cases/meihua/ 下建案例文件（自动记 trace）
  python cases/manage.py stats                      # 遍历所有子目录，统计案例数与后验命中率
  python cases/manage.py ls                          # 列出各术案例数
  python cases/manage.py gold 梅花易数               # 打印该术 gold 样例
"""
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 术法 → 子目录（八字/紫微归入 mingli 命理；MingLi-Bench 基准案例也在此目录）
METHOD_DIR = {
    "梅花": "meihua", "梅花易数": "meihua",
    "六爻": "liuyao", "六爻纳甲": "liuyao", "金钱卦": "liuyao",
    "小六壬": "xiaoliuren",
    "大六壬": "liuren", "六壬": "liuren",
    "奇门": "qimen", "奇门遁甲": "qimen",
    "太乙": "taiyi", "太乙神数": "taiyi",
    "八字": "mingli", "四柱": "mingli", "命理": "mingli", "紫微": "mingli", "紫微斗数": "mingli",
    "七政四余": "qizheng", "果老星宗": "qizheng", "星命": "qizheng",
    "风水": "fengshui", "堪舆": "fengshui", "八宅": "fengshui", "玄空": "fengshui",
    "择日": "zeri", "黄历": "zeri", "老黄历": "zeri",
    "相术": "xiangshu", "看相": "xiangshu", "面相": "xiangshu",
    "天文占": "tianwenzhan",
    "测字": "other", "解梦": "other", "灵棋": "other", "易林": "other", "其他": "other",
}

# 所有案例子目录（stats/ls 遍历）
ALL_DIRS = ["meihua", "liuyao", "xiaoliuren", "liuren", "qimen", "taiyi",
            "mingli", "qizheng", "fengshui", "zeri", "xiangshu", "tianwenzhan", "other"]

TEMPLATE = """# 案例：__TITLE__

## 基本信息
- 占期：__NOW__
- 方法：__METHOD__
- 问事：__TITLE__（补充背景与角色）

## 盘面（脚本输出，确定性）
```
{paste cast.py 输出}
```

## 预注册预测（断卦前写死，事后不可改）
- 预测 1：{…}
- 预测 2：{…}
- 应期：{…}
- 置信度：{高/中/低}

## 断语（三层分离 + 三级标注）
- 盘面事实：{…}
- 规则推演：{… [原文]/[规则推演]}
- 现实建议：{… [主观推断]}

## 后验（应期后回填，四态裁决：命中/部分命中/未命中/未知）
- 实际结果：{待验证}
- 命中统计：{待验证}
- 复盘：{…}
"""


def resolve_dir(method):
    key = METHOD_DIR.get(method)
    if not key:
        # 模糊匹配：包含术名关键词即归入
        for k, v in METHOD_DIR.items():
            if k in method or method in k:
                key = v
                break
    return key or "other"


def new(title, method):
    sub = resolve_dir(method)
    date = datetime.date.today().strftime("%Y%m%d")
    fname = f"{date}_{title}.md"
    d = os.path.join(HERE, sub)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, fname)
    if os.path.exists(path):
        print(f"已存在: {sub}/{fname}")
        return
    body = TEMPLATE
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for k, v in (("__TITLE__", title), ("__METHOD__", method), ("__NOW__", now)):
        body = body.replace(k, v)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"已创建案例: {sub}/{fname}")
    # 自动记一条 trace（决策追踪，断卦后补 rules/sources/conclusion）
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "scripts", "libs"))
        import trace
        trace.record(name=title, method=method, question=title, confidence="中",
                     notes=f"案例已建，待断卦后回填 rules/conclusion")
        print("  已记 trace（待断卦后回填结论）")
    except Exception as e:
        print(f"  trace 记录失败（不影响建案例）: {e}")


def iter_case_files():
    """遍历所有案例 .md（排除 README/模板/复盘总结/gold）。"""
    for d in ALL_DIRS:
        p = os.path.join(HERE, d)
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            if f.endswith(".md") and not f.startswith(("README", "预注册", "_")):
                yield d, os.path.join(p, f)


def parse_verdict(txt):
    """从后验统计四态。返回 {命中, 未命中, 部分命中, 未知, 待验证}。

    两种格式：
    1. 表格（MingLi-Bench）：每行末单元格为后验（命中/未命中），逐行精确计数。
    2. 段落（预注册模板）：## 后验 段里的「命中/部分命中/未命中/未知/待验证」关键词计数。
    """
    out = {"命中": 0, "未命中": 0, "部分命中": 0, "未知": 0, "待验证": 0}
    # 优先表格格式（行首 ftb_ 编号，末列为后验）
    table_total = 0
    for line in txt.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or not cells[0].startswith("ftb_"):
            continue
        v = cells[-1]
        if v in out:
            out[v] += 1
            table_total += 1
    if table_total:
        return out
    # 段落格式：只看「## 后验」之后的内容
    if "## 后验" in txt:
        tail = txt.split("## 后验", 1)[1]
    else:
        tail = txt
    out["部分命中"] = tail.count("部分命中")
    out["未命中"] = tail.count("未命中")
    out["未知"] = tail.count("未知")
    out["待验证"] = tail.count("待验证")
    out["命中"] = tail.count("命中") - out["未命中"] - out["部分命中"]
    return out


def stats():
    total_files = 0
    agg = {"命中": 0, "未命中": 0, "部分命中": 0, "未知": 0, "待验证": 0}
    rows = []
    for d, path in iter_case_files():
        total_files += 1
        txt = open(path, encoding="utf-8").read()
        v = parse_verdict(txt)
        for k in agg:
            agg[k] += v[k]
        resolved = v["命中"] + v["未命中"] + v["部分命中"]
        rows.append((d, os.path.basename(path), resolved, v["待验证"]))
    print(f"案例文件总数: {total_files}")
    print(f"后验合计: 命中 {agg['命中']} · 未命中 {agg['未命中']} · 部分命中 {agg['部分命中']} · 未知 {agg['未知']} · 待验证 {agg['待验证']}")
    judged = agg["命中"] + agg["未命中"] + agg["部分命中"]
    if judged:
        hit = agg["命中"] + 0.5 * agg["部分命中"]
        print(f"已裁决 {judged} 条，命中率 {agg['命中']}/{judged} = {agg['命中']/judged*100:.1f}%（部分命中按 0.5 计则 {hit/judged*100:.1f}%）")
    print("\n各术案例数（已裁决/待验证）:")
    by_dir = {}
    for d, name, resolved, pending in rows:
        by_dir.setdefault(d, [0, 0, 0])
        by_dir[d][0] += 1
        by_dir[d][1] += resolved
        by_dir[d][2] += pending
    for d in sorted(by_dir):
        n, r, p = by_dir[d]
        print(f"  {d:<12} 文件 {n:>3}  已裁决 {r:>3}  待验证 {p:>3}")


def ls():
    by_dir = {}
    for d, path in iter_case_files():
        by_dir[d] = by_dir.get(d, 0) + 1
    for d in sorted(by_dir):
        print(f"  {d:<12} {by_dir[d]} 个案例")
    if not by_dir:
        print("（无案例）")


def gold(method):
    sub = resolve_dir(method)
    # gold 样例统一放 cases/_gold/ 下，文件名为子目录名
    gp = os.path.join(HERE, "_gold", f"{sub}.md")
    if os.path.isfile(gp):
        print(f"gold 样例: cases/_gold/{sub}.md")
        print(open(gp, encoding="utf-8").read())
    else:
        print(f"该术暂无 gold 样例（{gp} 不存在）")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "new" and len(sys.argv) >= 3:
        new(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "梅花易数")
    elif cmd == "stats":
        stats()
    elif cmd == "ls":
        ls()
    elif cmd == "gold" and len(sys.argv) >= 3:
        gold(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
