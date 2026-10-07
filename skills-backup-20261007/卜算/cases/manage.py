# -*- coding: utf-8 -*-
"""案例库管理：新建案例（从模板）、统计命中率。

用法:
  python cases/manage.py new "跳槽成不成" 梅花易数   # 生成一个案例文件
  python cases/manage.py stats                        # 统计案例数与后验命中率
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

TEMPLATE = """# 案例：__DATE___TITLE__

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

## 后验（应期后回填）
- 实际结果：{待验证}
- 命中统计：{待验证}
- 复盘：{…}
"""


def new(title, method):
    date = datetime.date.today().strftime("%Y%m%d")
    fname = f"{date}_{title}.md"
    path = os.path.join(HERE, fname)
    if os.path.exists(path):
        print(f"已存在: {fname}")
        return
    body = TEMPLATE
    for k, v in (("__DATE__", date), ("__TITLE__", title), ("__METHOD__", method),
                 ("__NOW__", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))):
        body = body.replace(k, v)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"已创建案例: {fname}")


def stats():
    files = [f for f in os.listdir(HERE) if f.endswith(".md") and not f.startswith(("README", "预注册", "manage"))]
    done = 0
    for f in files:
        txt = open(os.path.join(HERE, f), encoding="utf-8").read()
        if "待验证" not in txt.split("## 后验")[-1] if "## 后验" in txt else False:
            done += 1
    print(f"案例总数: {len(files)}  已后验: {done}  待验证: {len(files) - done}")
    print("（后验命中率需在后验字段里写「命中/未命中」，由人工复核判定）")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "new":
        new(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "梅花易数")
    elif len(sys.argv) >= 2 and sys.argv[1] == "stats":
        stats()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
