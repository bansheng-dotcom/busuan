# -*- coding: utf-8 -*-
"""导入 opencode-tianji（MIT）六爻占验卦例库 → 本技能案例库格式。

数据源：cases/liuyao/_tianji_guaili.json（381 则，从《增删卜易》全四卷 +《卜筮正宗》十八问答提取）。
每条卦例含：占事 / 卦名·变卦 / 干支 / 古籍断语（含应验）/ 应期原理 / 白话 / 来源行号。
生成 cases/liuyao/*.md 案例文件，后验按古籍是否记应验标记「命中/未命中」（「诸书之谬」类记为未命中）。

用法：python cases/import_tianji.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "liuyao", "_tianji_guaili.json")
DST = os.path.join(HERE, "liuyao")

BOOK_NAMES = {4: "增删卜易", 6: "卜筮正宗"}


def clean(s):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", str(s))


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    cases = d.get("卦例", [])
    hit = miss = 0
    for i, c in enumerate(cases, 1):
        shu = c.get("书号", 0)
        shu_name = BOOK_NAMES.get(shu, str(shu))
        zhan = c.get("占事", "")
        gua = c.get("卦名", "")
        bian = c.get("变卦", "")
        ganzhi = c.get("干支", "")
        juan = c.get("卷", "")
        zhang = c.get("章节", "")
        duanyu = c.get("卦象与断语", "")
        yingqi = c.get("应期原理", "")
        baihua = c.get("白话", "")
        src_list = c.get("来源", [])
        hang = src_list[0].get("行", "") if src_list else ""

        # 判后验：古籍「诸书之谬」类（批驳错误断法）记为未命中，其余记应验（命中）
        is_miu = "谬" in (zhan + zhang + duanyu[:80])
        verdict = "未命中" if is_miu else "命中"
        if is_miu:
            miss += 1
        else:
            hit += 1

        fname = f"{i:03d}_{clean(zhan)}.md"
        path = os.path.join(DST, fname)
        body = f"""# 案例：{zhan}（{gua}变{bian}）

## 基本信息
- 来源：{shu_name}·{juan}·{zhang}（古籍占验卦例）
- 方法：六爻纳甲
- 问事：{zhan}（{ganzhi}）

## 盘面
本卦 {gua}　变卦 {bian}　干支 {ganzhi}

## 断语（古籍原文）
{duanyu}

## 应期原理
{yingqi}

## 白话
{baihua}

## 后验
- 实际结果：古籍{'记应验' if not is_miu else '记「诸书之谬」（批驳错断）'}（见断语原文）
- 判定：{verdict}
- 复盘：六爻用神 / 应期断法校准案例

## 来源
{shu_name}·{juan}·{zhang}·行{hang}（opencode-tianji 提取，MIT）
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)

    print(f"已生成 {len(cases)} 个六爻案例到 cases/liuyao/（命中 {hit} · 未命中 {miss}）")


if __name__ == "__main__":
    main()
