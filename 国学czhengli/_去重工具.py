# -*- coding: utf-8 -*-
"""知识库去重：按「书名（繁转简）」分组，同书多份时保留简体/易藏，其余移到备份目录（不删除）。"""
import os
import re
import shutil

TXT = r"D:\daimajieti1\国学czhengli\txt"
BAK = r"D:\daimajieti1\国学czhengli\_去重备份"

F2J = {
    '會': '会', '賦': '赋', '傳': '传', '倫': '伦', '統': '统', '詳': '详',
    '鏡': '镜', '經': '经', '開': '开', '書': '书', '潛': '潜', '虛': '虚',
    '龍': '龙', '極': '极', '觀': '观', '義': '义', '隱': '隐', '靈': '灵',
    '臺': '台', '祕': '秘', '學': '学', '記': '记', '鑑': '鉴', '奧': '奥',
    '語': '语', '曆': '历', '見': '见', '發': '发', '論': '论', '範': '范',
    '內': '内', '戶': '户', '術': '术', '數': '数', '雜': '杂', '總': '总',
    '諱': '讳', '釋': '释', '解': '解', '繹': '绎', '讖': '谶', '遺': '遗',
}


def jian(s):
    return ''.join(F2J.get(c, c) for c in s)


def strip_cat(f):
    """去掉 [分类] 前缀与 .txt 后缀"""
    s = re.sub(r'^\[[^\]]*\]\s*', '', f)
    return s[:-4] if s.endswith('.txt') else s


def cat_of(f):
    m = re.match(r'^\[([^\]]*)\]', f)
    return m.group(1) if m else ''


CAT_ORDER = {'易藏': 0, '其他': 1, '术数': 2, '道藏': 3}


def keep_priority(f):
    t = strip_cat(f)
    is_jian = (t == jian(t))
    return (0 if is_jian else 1, CAT_ORDER.get(cat_of(f), 9), len(f), f)


def main(dry=True):
    files = [f for f in os.listdir(TXT) if f.endswith('.txt')]
    by_key = {}
    for f in files:
        by_key.setdefault(jian(strip_cat(f)), []).append(f)
    dup_groups = {k: g for k, g in by_key.items() if len(g) > 1}

    keep, move = set(), []
    for k, g in dup_groups.items():
        cand = sorted(g, key=keep_priority)
        keep.add(cand[0])
        for x in cand[1:]:
            move.append(x)

    move = sorted(set(move))
    print(f"总文件 {len(files)}；重复书名 {len(dup_groups)} 种；将移走 {len(move)} 个")
    print("=== 重复组明细（保留 → 移走）===")
    for k, g in sorted(dup_groups.items()):
        c = sorted(g, key=keep_priority)
        print(f"\n[{k}]")
        print(f"  保留: {c[0]}")
        for x in c[1:]:
            print(f"  移走: {x}")

    if dry:
        print("\n[干跑] 未实际移动。")
        return move
    os.makedirs(BAK, exist_ok=True)
    for x in move:
        shutil.move(os.path.join(TXT, x), os.path.join(BAK, x))
    print(f"\n已移动 {len(move)} 个到 {BAK}")
    return move


if __name__ == '__main__':
    import sys
    dry = '--go' not in sys.argv
    main(dry)
