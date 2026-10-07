# -*- coding: utf-8 -*-
"""从典籍《开元占经》txt 提取历史天文占验案例 → 本技能案例库格式。

《开元占经》是「占辞 + 历史应验」结构：每条天象（天鸣/天裂/雨兽/陨石/地燃/彗孛/日食…）
下引历史事件佐证（「某年号某年某月，天象，其后/是时…应验」）。
提取含「X年X月」的历史占验句，过滤纯历法句。

生成 cases/tianwenzhan/*.md，后验标记「命中」（古籍记应验）。

用法：python cases/extract_tianwen_cases.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\daimajieti1\国学czhengli\txt\[易藏] 开元占经.txt"
DST = os.path.join(HERE, "tianwenzhan")

# 天象关键词（用于识别占验句 + 排除纯历法句）
_TIANXIANG = ("天鸣", "天裂", "雨兽", "雨肉", "雨血", "雨骨", "陨石", "地燃", "地动",
              "地震", "彗", "孛", "日食", "月食", "日有", "月有", "星孛", "星陨", "天鼓",
              "天开", "天光", "虹", "白虹", "黑气", "赤气", "天雨", "雨金", "雨粟")


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def main():
    os.makedirs(DST, exist_ok=True)
    text = open(SRC, encoding="utf-8").read()
    # 提取含「X年X月」的历史占验句（去引号内残留）
    pat = re.compile(r"[^。]*?[一二三四五六七八九十百千]+年[一二三四五六七八九十]*月[^。]*[。]")
    raw = pat.findall(text)
    cases = []
    seen = set()
    for s in raw:
        s = s.strip().strip("“”\"'")
        if len(s) < 8 or len(s) > 300:
            continue
        # 过滤：须含天象或应验关键词，排除纯历法/制度句
        if not any(k in s for k in _TIANXIANG) and not any(k in s for k in ("其后", "是时", "应", "验", "灾", "乱")):
            continue
        if s in seen:
            continue
        seen.add(s)
        cases.append(s)

    for idx, s in enumerate(cases, 1):
        # 问事：从句中提取天象词，否则统一
        tian = next((k for k in _TIANXIANG if k in s), "天象")
        fname = f"{idx:03d}_{clean(tian)}.md"
        path = os.path.join(DST, fname)
        md = f"""# 案例：{tian}（天文占）

## 基本信息
- 来源：《开元占经》·历史天文占验
- 方法：天文占
- 问事：{tian}（星象灾异占）

## 占验（历史记录 + 应验）
{s}

## 后验
- 实际结果：古籍记应验（历史事件应于天象）
- 判定：命中
- 复盘：天文占「天人感应」占辞校准案例

## 来源
《开元占经》·{tian}占（历史占验）
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    print(f"已提取 {len(cases)} 则天文占案例到 cases/tianwenzhan/")


if __name__ == "__main__":
    main()
