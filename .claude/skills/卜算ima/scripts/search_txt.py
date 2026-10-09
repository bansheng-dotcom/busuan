# -*- coding: utf-8 -*-
"""典籍 txt 全文检索（grep 等价，纯离线、零依赖）。

ima 环境无 Grep 工具，用本脚本按关键词检索 `D:\\卜算\\国学czhengli\\txt\\` 全库
（含「案例库」子目录）的原文，输出「文件名:行号: 匹配行」，等价 grep。

用法:
  python scripts/search_txt.py "官讼"                  # 全库关键词检索
  python scripts/search_txt.py "官讼" 大六壬             # 只搜路径含「大六壬」的文件
  python scripts/search_txt.py "体用 生克" --n 50       # 多关键词(任一命中)，限 50 行
  python scripts/search_txt.py "官讼" 案例库/梅花        # 只搜案例库/梅花子目录
  python scripts/search_txt.py --ls 大六壬               # 列出路径含「大六壬」的 txt 文件
  python scripts/search_txt.py --root "D:\\xx\\txt" "词" # 自定义根目录

多关键词用空格分隔 = 任一命中（OR）；匹配按文件分组，每文件最多展示 20 行。
"""
import os
import sys

ROOT = r"D:\卜算\国学czhengli\txt"
PER_FILE = 20
DEFAULT_LIMIT = 200


def _reconf():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _read(path):
    raw = None
    for enc in ("utf-8", "gb18030"):
        try:
            with open(path, "rb") as f:
                raw = f.read()
            return raw.decode(enc)
        except (UnicodeDecodeError, OSError):
            continue
    return raw.decode("utf-8", errors="replace") if raw is not None else ""


def iter_txt(root):
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if fn.lower().endswith((".txt", ".md")):
                yield os.path.join(dirpath, fn)


def rel(path, root):
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def parse(argv):
    root = ROOT
    limit = DEFAULT_LIMIT
    flt = None
    ls = False
    kws = []
    pos = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--ls":
            ls = True
        elif a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
            i += 1
        elif a == "--n" and i + 1 < len(argv):
            limit = int(argv[i + 1])
            i += 1
        elif a.startswith("-"):
            pass
        else:
            pos.append(a)
        i += 1
    if ls:
        # --ls 模式：位置参数 = 路径过滤
        flt = pos[0] if pos else None
    else:
        # 正常模式：第 1 个 = 关键词，第 2 个 = 路径过滤
        if pos:
            kws = pos[0].split()
        if len(pos) > 1:
            flt = pos[1]
    return root, limit, flt, ls, kws


def main():
    _reconf()
    root, limit, flt, ls, kws = parse(sys.argv[1:])

    if not os.path.isdir(root):
        print(f"[search_txt.py] 目录不存在：{root}")
        print("  请用 --root 指定实际 txt 目录，或用 --ls 定位。")
        return

    files = [p for p in iter_txt(root)
             if flt is None or flt.replace("\\", "/") in rel(p, root).replace("\\", "/")]

    if ls:
        for p in files:
            print(rel(p, root))
        print(f"\n共 {len(files)} 个文件")
        return

    if not kws:
        print(__doc__)
        return

    total_hits = 0
    shown = 0
    for p in files:
        text = _read(p)
        if not text:
            continue
        lines = text.splitlines()
        hits = []
        for ln, line in enumerate(lines, 1):
            if any(k in line for k in kws):
                hits.append((ln, line.strip()))
        if not hits:
            continue
        total_hits += len(hits)
        print(f"\n【{rel(p, root)}】命中 {len(hits)} 行")
        for ln, line in hits[:PER_FILE]:
            if shown >= limit:
                break
            line = line if len(line) <= 120 else line[:120] + "…"
            print(f"  {ln}: {line}")
            shown += 1
        if len(hits) > PER_FILE:
            print(f"  …（其余 {len(hits) - PER_FILE} 行省略，--n 可调）")
        if shown >= limit:
            print(f"\n[已截断，命中行过多；用更具体的关键词或 --n 调上限]")
            break

    if total_hits == 0:
        print(f"[search_txt.py] 未命中「{' '.join(kws)}」")
    else:
        print(f"\n—— 合计命中 {total_hits} 行 / {len(files)} 个文件（若被截断以上为部分）——")


if __name__ == "__main__":
    main()
