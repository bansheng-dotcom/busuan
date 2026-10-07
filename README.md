# 卜算 · busuan

中国传统术数占卜的一体化工程：**确定性起盘引擎** + **古籍术数语料库** + **案例库** + **结构化断卦流程**（三层分离 / 三级标注 / 双轨白话输出）。

> ⚠️ **免责声明**：本项目仅供传统文化研究与学习参考，所有占卜结论不构成任何现实决策依据，切勿用于医疗、投资、法律等重要事项。

## 仓库结构

| 目录 | 说明 |
| --- | --- |
| `卜算ima/` | 核心技能项目：起盘引擎、典籍检索、断卦规则、案例库、测试与评测 |
| `国学czhengli/` | 古籍术数语料库（PDF / txt / 易藏 / 四库 / 道藏等） |
| `参考项目/` | 同类开源项目参考（传统智慧、命理、八字等） |
| `skills-backup-20261007/` | 技能历史备份 |
| `.claude/` | Claude 技能目录 |

## 支持的术数

**有独立起盘引擎**（位于 `卜算ima/scripts/libs/`）：

| 类别 | 引擎 |
| --- | --- |
| 命理 | 八字/四柱（`bazi.py`）、紫微斗数（`zhiwei.py`）、合婚（`hehun.py`） |
| 三式 | 大六壬（`liuren.py`）、奇门遁甲（`qimen.py`）、太乙神数（`taiyi.py`） |
| 占卜 | 梅花易数（`meihua.py`）、六爻/纳甲（`liuyao.py` / `najia.py`）、小六壬（`xiaoliuren.py`） |
| 星命 | 七政四余（`qizheng.py`） |
| 风水 | 风水/堪舆（`fengshui.py`） |
| 择日 | 择日/黄历（`zeri.py` + `almanac.py`：彭祖百忌、值神、宜忌等） |

**辅助模块**：神煞（`shensha.py`）、刑冲合害（`xingchong.py`）、调候（`tiaohou.py`）、流年（`liunian.py`）、毕法赋（`liuren_bifa.py`）、奇门十干克应（`qimen_keying.py`）、紫微运限（`ziwei_horoscope.py`）、流年趋势（`trend.py`）、真太阳时（`taiyangshi.py`）、寿星天文历（`sxtwl.py`）。

**断卦质量双 gate**：排盘前 `precheck.py` + 断卦后 `review.py`（七项强制检查），配套决策追踪 `trace.py`、反馈契约 `feedback.py`、可视化排盘 `htmlpan.py`。

## 快速开始

```bash
# 起盘（八字 / 紫微 / 七政）
python 卜算ima/scripts/cast.py bazi 2004 2 23 3 40 0 0
python 卜算ima/scripts/cast.py zhiwei 2004 2 23 3 0
python 卜算ima/scripts/cast.py qizheng --time "2004-02-23 03:40"

# 六爻可视化卦图
python 卜算ima/scripts/cast.py liuyao --html

# 典籍检索（本地精确检索，支持正则 + 繁简）
python 卜算ima/scripts/search.py "妻财" --local --txt 国学czhengli/txt
python 卜算ima/scripts/search.py "青龙.{0,4}返首" --local --regex --txt 国学czhengli/txt

# 回归测试
python 卜算ima/tests/regression_test.py
```

> 检索默认走本地字级索引（毫秒级精确匹配），可选接腾讯 ima 知识库做语义兜底（见 `卜算ima/README-ima.md`）。

## 语料库（国学czhengli/）

古籍术数原文语料，是断卦「回溯原文佐证」的数据底座：

- `txt/`、`PDF/` — 文本与 PDF 双格式
- `易藏术数/`、`道藏术数/`、`四库全书-子部术数/`、`古籍整理/`、`其他术数/` — 分藏整理

## 案例库与评测

- **案例库**：763 案例（六爻 381 / 大六壬 218 / 天文占 120 / 梅花 10 / 八字·紫微 33 / 小六壬 1），见 `卜算ima/cases/`
- **回归测试**：190 项全部通过（后续持续扩充，详见 `升级记录.md`）
- **紫微对照**：108 命例与 iztro 独立引擎对照校验，见 `卜算ima/bench/ziwei_crosscheck.py`
- **能力边界**：MingLi-Bench 160 题评测，有信号组（健康/事业/财运/家庭/婚姻）与无信号组（学业/性格/外貌）已在 `SKILL.md` 标注

## 详细文档

| 文档 | 说明 |
| --- | --- |
| `卜算ima/SKILL.md` | 技能总纲（起盘 → 检索 → 分层断卦 → 质检完整流程） |
| `卜算ima/README-ima.md` | ima 知识库接入说明 |
| `卜算ima/XUANXUE-LINKAGE.md` | 跨术数联动接口 |
| `卜算ima/升级记录.md` | 分阶段工程化升级与一致性校验记录 |

## 代码来源与许可

引擎部分代码改编自以下 MIT 开源项目，详见 `卜算ima/升级记录.md` 第三节：

- kentang2017/kinliuren、kintaiyi（MIT）
- dglijin-oss/chinese-metaphysics-skills（MIT）
- yueyuan-bazi（MIT）
- iztro / py-iztro（MIT，用于对照校验）

其余为自写；典籍原文版权归原始文献所有。

## 免责声明

本项目为传统文化研究工具，占卜结果仅供参考，不构成医疗、投资、法律等任何现实决策建议。
