# -*- coding: utf-8 -*-
"""从典籍《奇门遁甲秘笈大全》txt 提取奇门占断条文 → 案例库/奇门/。

《秘笈大全》与《六壬断案》不同，无「某年月日×局×时」的日期占验案例，其占验内容
是「占断条文」：①「奇门占事（计条）」分类断法（占投军/攻城/盗贼/婚姻/求财/失物/
病吉凶/坟墓…约 60 类）；②「八门克应诀」八门静应/动应/占身命。故本库为「占断条文
库」，每条标原文出处，供断卦 search_txt.py 佐证与 case_search 语义检索。

生成 案例库/奇门/*.md（占断 001 起，八门克应 501 起），后验字段标「古籍条文」。

用法：python cases/extract_qimen_cases.py
"""
import os
import re
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
# 典籍 txt 定位：优先 D:\卜算，退化 glob 兜底
_SRC_CAND = [
    r"D:\卜算\国学czhengli\txt\[易藏] 奇门遁甲秘笈大全.txt",
    r"D:\卜算\国学czhengli\txt\奇门遁甲秘笈大全.txt",
]
_DST = r"D:\卜算\国学czhengli\txt\案例库\奇门"


def _find_src():
    for c in _SRC_CAND:
        if os.path.exists(c):
            return c
    for p in glob.glob(r"D:\**\[易藏] 奇门遁甲秘笈大全.txt", recursive=True):
        return p
    for p in glob.glob(r"D:\**\*奇门遁甲秘笈大全*.txt", recursive=True):
        return p
    raise FileNotFoundError("未找到《奇门遁甲秘笈大全》txt")


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def _strip(s):
    """去行首行尾全角/半角空白。"""
    return s.strip(" \t　\u3000\r\n")


# 占断标题：整行 = 占 + 简短名（无标点）
_ZHAN = re.compile(r"^[\s　]*占([^\s　：:。，、；;\?？!！]{1,16})$")
# 八门克应标题
_MEN = re.compile(r"^[\s　]*(开门|休门|生门|伤门|杜门|景门|死门|惊门)[尅克]应[\s　]*$")


def extract_zhan(text):
    """奇门占事分类断法：返回 [(标题, 正文)]。"""
    out = []
    cur = None
    buf = []
    for line in text.splitlines():
        m = _ZHAN.match(line)
        if m:
            if cur is not None:
                out.append((cur, "\n".join(buf).strip()))
            cur = "占" + m.group(1)
            buf = []
        else:
            if cur is not None:
                buf.append(_strip(line))
    if cur is not None:
        out.append((cur, "\n".join(buf).strip()))
    return out


def extract_men(text):
    """八门克应：返回 [(门名, 正文)]。"""
    out = []
    cur = None
    buf = []
    started = False
    for line in text.splitlines():
        if "八门尅应诀总目" in line or "八门克应诀总目" in line:
            started = True
            continue
        if not started:
            continue
        if "三诈法" in line or "三詐法" in line:
            break
        m = _MEN.match(line)
        if m:
            if cur is not None:
                out.append((cur, "\n".join(buf).strip()))
            cur = m.group(1) + "克应"
            buf = []
        else:
            if cur is not None:
                buf.append(_strip(line))
    if cur is not None:
        out.append((cur, "\n".join(buf).strip()))
    return out


def _write(path, title, question, body, src_note):
    md = f"""# 案例：{title}（奇门遁甲）

## 基本信息
- 来源：《奇门遁甲秘笈大全》·{src_note}
- 方法：奇门遁甲
- 问事：{question}

## 断法（原文）
{body}

## 后验
- 实际结果：古籍占断条文（分类断法 / 克应诀）
- 判定：参考（非日期占验，为用神取法与应验条文）
- 复盘：断奇门同类问事时，先按本条文定用神（某星/某门/某干），再查格局生克

## 来源
《奇门遁甲秘笈大全》·{src_note}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)


def main():
    src = _find_src()
    text = open(src, encoding="utf-8").read()
    os.makedirs(_DST, exist_ok=True)

    zhan = extract_zhan(text)
    men = extract_men(text)

    idx = 0
    for title, body in zhan:
        if len(body) < 20:   # 过滤空/过短条目
            continue
        idx += 1
        _write(os.path.join(_DST, f"{idx:03d}_{clean(title)}.md"),
               title, title, body, "奇门占事（计条）")

    for title, body in men:
        if len(body) < 20:
            continue
        idx += 1
        _write(os.path.join(_DST, f"{idx:03d}_{clean(title)}.md"),
               title, title, body, "八门克应诀")

    print(f"已提取 {idx} 条到 {_DST}（占断 {len(zhan)} 类 / 八门克应 {len(men)} 门）")


if __name__ == "__main__":
    main()
