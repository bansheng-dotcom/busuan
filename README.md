# 卜算 · busuan

中国传统术数占卜的一体化工程：**确定性起盘引擎** + **古籍术数语料库** + **案例库** + **结构化断卦流程**（四层证据来源 / 三级结论标注 / 双轨白话输出）。

> ⚠️ **免责声明**：本项目仅供传统文化研究与学习参考，所有占卜结论不构成任何现实决策依据，切勿用于医疗、投资、法律等重要事项。

## 仓库结构

| 目录 | 说明 |
| --- | --- |
| `.claude/skills/卜算/` | 技能本体：起盘引擎、典籍检索、断卦规则、案例库、测试与评测（`SKILL.md` 总纲 + `docs/` 分术文档 + `references/` 速查层） |
| `国学czhengli/` | 古籍术数语料库（425 份干净 txt + 案例库），断卦「回溯原文佐证」的数据底座 |
| `卜算技能升级方案.md` | 确定性架构升级方案（DET/STO/UND 三档 + 文件分层 + 依赖只向内） |

> 参考项目（mingli / tianzhi-core / mingyu / liuren-skill 等开源术数工程）在仓库外 `D:\术数参考\`。

## 支持的术数

**有独立起盘引擎**（位于 `.claude/skills/卜算/scripts/libs/pan/`，统一入口 `scripts/cast.py`）：

| 类别 | 引擎 |
| --- | --- |
| 命理 | 八字/四柱（`bazi.py`）、紫微斗数（`zhiwei.py`）、合婚（`hehun.py`） |
| 三式 | 大六壬（`liuren.py`）、奇门遁甲（`qimen.py`）、太乙神数（`taiyi.py`） |
| 占卜 | 梅花易数（`meihua.py`）、六爻/纳甲（`liuyao.py` / `najia.py`）、小六壬（`xiaoliuren.py`） |
| 星命 | 七政四余（`qizheng.py`） |
| 风水 | 风水/堪舆（`fengshui.py`） |
| 择日 | 择日/黄历（`zeri.py` + `almanac.py`：彭祖百忌、值神、宜忌等） |

代码按三段流水线分层：`lifa/`（历法·Det）→ `pan/`（排盘·Det）→ `judge/`（判断·Und/Int）→ `gate/`（质检），另有 `regress/`（独立交叉校验）、`util/`（案例检索/决策追踪/反馈）、`engines/`（kentang2017 奇门/太乙引擎）。

**断卦质量双 gate**：排盘前 `gate/precheck.py` + 断卦后 `gate/review.py`（七项强制检查），配套 `judge/adversarial.py`（对抗性第二意见）、`util/trace.py`（决策追踪）、`util/feedback.py`（反馈契约）、`util/htmlpan.py`（可视化排盘）。

## 快速开始

```bash
# 起盘（八字 / 紫微 / 七政）
python .claude/skills/卜算/scripts/cast.py bazi 2004 2 23 3 40 0 0
python .claude/skills/卜算/scripts/cast.py zhiwei 2004 2 23 3 0
python .claude/skills/卜算/scripts/cast.py qizheng --time "2004-02-23 03:40"

# 六爻可视化卦图
python .claude/skills/卜算/scripts/cast.py liuyao --html

# 典籍检索（段落 ID 全文检索 + 原样复核，纯离线）
python .claude/skills/卜算/scripts/classical_search.py --build-index
python .claude/skills/卜算/scripts/classical_search.py --search 伤官佩印 --book 子平真诠 --limit 5
python .claude/skills/卜算/scripts/classical_search.py --passage-id 三命通会:1009

# 案例语义检索（TF-IDF + 字符 n-gram，纯离线）
python .claude/skills/卜算/scripts/libs/util/case_search.py "求财" 六爻 3

# 回归测试
python .claude/skills/卜算/tests/regression_test.py
```

## 语料库（国学czhengli/）

古籍术数原文语料，是断卦「回溯原文佐证」的数据底座：

- `txt/`（425 份干净 txt，命名 `[术数]/[易藏]/[道藏]/[其他] 书名.txt`；繁简重复备份至 `_去重备份/`）
- `txt/案例库/`（1490 则占验案例，按术分类：六爻 381 / 大六壬 757 / 天文占 120 / 奇门 117 / 梅花 79 / 八字·紫微 33 / 太乙 1 / 小六壬 1）

## 案例库与评测

- **案例库**：1490 则，见 `国学czhengli/txt/案例库/`，语义检索走 `scripts/libs/util/case_search.py`
- **测试**：回归测试 331 项 + 架构测试 4 项（依赖只向内）+ 文档路径守护 1 项（防文档/代码路径漂移），全部通过
- **紫微对照**：108 命例与 iztro 独立引擎对照校验，见 `bench/ziwei_crosscheck.py`
- **能力边界**：MingLi-Bench 160 题评测，有信号组（健康/事业/财运/家庭/婚姻）与无信号组（学业/性格/外貌）已在 `SKILL.md` 标注

## 详细文档

| 文档 | 说明 |
| --- | --- |
| `.claude/skills/卜算/SKILL.md` | 技能总纲（路由 → 选术 → 起盘 → 分层断卦 → 质检完整流程） |
| `.claude/skills/卜算/docs/` | 16 术法分文档（起盘命令 / 断卦流程 / 排盘自检 / 输出格式） |
| `.claude/skills/卜算/references/` | 结构化速查层（紫微庙旺四化 / 奇门格局 / 六爻用神 / 射覆画像 / 术语百科等） |

## 代码来源与许可

引擎部分代码改编自以下 MIT 开源项目（详见 `卜算技能升级方案.md` 参考项目节）：

- kentang2017/kinliuren、kintaiyi（MIT）
- dglijin-oss/chinese-metaphysics-skills（MIT）
- yueyuan-bazi（MIT）
- iztro / py-iztro（MIT，用于对照校验）

其余为自写；典籍原文版权归原始文献所有。

## 免责声明

本项目为传统文化研究工具，占卜结果仅供参考，不构成医疗、投资、法律等任何现实决策建议。
