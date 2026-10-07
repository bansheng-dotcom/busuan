# 案例库（预注册预测 + 后验验证）

参照 yueyuan-bazi 的「预注册预测 + 后验验证」思路：**断卦不是一次性空推，而是先写可证伪的预测，事后对照实际结果，用案例库校准。**

## 目录结构

```
cases/
├── _gold/            # 每术 1 份 gold 标准样例（三层分离+三级标注模板，断卦前先看）
├── meihua/           # 梅花易数案例
├── liuyao/           # 六爻纳甲案例
├── xiaoliuren/       # 小六壬案例
├── liuren/           # 大六壬案例
├── qimen/            # 奇门遁甲案例
├── taiyi/            # 太乙神数案例
├── mingli/           # 八字/紫微案例（含 MingLi-Bench 32 基准案例）
├── qizheng/          # 七政四余案例
├── fengshui/         # 风水案例
├── zeri/             # 择日案例
├── xiangshu/         # 相术案例
├── tianwenzhan/      # 天文占案例
├── other/            # 测字/解梦/灵棋/易林等
├── traces/trace.jsonl      # 断卦决策追踪（记录规则命中/出处/结论/置信度）
├── feedback/feedback.jsonl # 结构化反馈（五类问题，用于校准规则）
├── manage.py         # 案例库管理
└── 预注册模板.md      # 案例模板
```

## 工作流

1. **起盘**：跑 `scripts/cast.py`，记录盘面（确定性、可复现）。
2. **预注册预测**：断卦前，先按 `预注册模板.md` 写下**可证伪的断言**（谁、什么事、什么结果、什么应期），写死，事后不可改。
3. **断卦**：按 SKILL.md 十节的三层分离 + 三级标注出断语（先看 `_gold/` 对应术的样例）。
4. **后验**：到应期后，回填实际结果，判定每条预测「命中 / 未命中 / 部分命中 / 未知」。
5. **入档**：每个案例存一个 `.md` 文件，命名 `YYYYMMDD_所问之事.md`，放在对应术的子目录下。

## manage.py 用法

```bash
python cases/manage.py new "跳槽成不成" 梅花易数   # 在 cases/meihua/ 下建案例文件（自动记 trace）
python cases/manage.py stats                      # 遍历所有子目录，统计案例数与后验命中率
python cases/manage.py ls                          # 列出各术案例数
python cases/manage.py gold 梅花易数               # 打印该术 gold 样例
```

- `new` 会把术名自动映射到子目录（`梅花易数→meihua`、`八字/紫微→mingli` 等），并自动记一条 trace。
- `stats` 会统计各子目录的「已裁决/待验证」与真实命中率（命中/未命中/部分命中/未知 四态）。

## 决策追踪（trace）与结构化反馈（feedback）

- `../scripts/libs/trace.py`：断卦**决策追踪**。`record` 记每次断卦的规则命中（R-XX-NN）、引文出处、结论、置信度到 `traces/trace.jsonl`；`feedback` 回填后验；`analyze` 统计复盘。
- `../scripts/libs/feedback.py`：**结构化反馈契约 feedback-v1**。`record` 采集问题（error/gap/conflict/friction/clarity 五类）到 `feedback/feedback.jsonl`；隐私边界：不采集出生数据、卦题、命盘、对话原文。
- 三者分工：案例库（`*.md`）记「预注册预测 + 后验」；trace 记「过程」；feedback 记「问题」。

## 与排盘回归的区别

- `../tests/regression_test.py`：测**排盘是否算对**（确定性，脚本层，机器可自动验证）。已覆盖全部术法的 golden 断言（固定输入 → 已知答案），当前 **190 项全过**。
- `../bench/ziwei_crosscheck.py`：紫微斗数对照 iztro 校验，**108 例**（8 手选 + 100 生成），核心排盘一致 104、不一致 0（另有年界差异 3、iztro 闰月日界差异 1）。
- 本案例库：测**断卦是否断准**（推理层面，靠事后对照实际结果校准，无法机器自动判准）。

## 古籍案例库（已引入 609 则，覆盖 3 术）

**六爻（381 则）**
- **来源**：[opencode-tianji](https://www.npmjs.com/package/opencode-tianji)（MIT），从《增删卜易》全四卷 +《卜筮正宗》十八问答全量提取的占验卦例。
- **存放**：`cases/liuyao/` 381 个 `.md`；原始数据 `_tianji_guaili.json` + 金标准 `_tianji_gold.json` + 许可 `_tianji_LICENSE.txt`。**导入**：`cases/import_tianji.py`。

**大六壬（755 则）**
- **来源**：《六壬断案》（邵彦和 218 则）+《壬占汇选》（诸家占案 444 则）+《六壬指南》卷三占验（93 则），均本技能典籍 txt 内。
- **存放**：`cases/liuren/` 755 个 `.md`（每则含占事 + 课式 + 断语含应验）。**提取**：`cases/extract_liuren_cases.py`（断案）+ `cases/extract_renzhan_cases.py`（壬占汇选）+ `cases/extract_zhinan_cases.py`（六壬指南）。

**梅花易数（10 则）**
- **来源**：《梅花易数》（康节先生观梅占系列，本技能典籍 txt 内）。
- **存放**：`cases/meihua/` 10 个 `.md`（观梅占 / 牡丹占 / 邻夜叩门借物占 / 西林寺牌额占 / 老人有忧色占 / 少年有喜色占 / 牛哀鸣占 / 鸡悲鸣占 / 枯枝坠地占）。**提取**：`cases/extract_meihua_cases.py`。

**天文占（120 则）**
- **来源**：《开元占经》（「占辞 + 历史占验」结构，本技能典籍 txt 内）。
- **存放**：`cases/tianwenzhan/` 120 个 `.md`（天鸣 / 天裂 / 雨兽 / 陨石 / 地燃 / 彗孛 等历史占验）。**提取**：`cases/extract_tianwen_cases.py`。

**价值**：这些是「真实占卜 + 古籍已记应验」的案例，用于各术断法校准——是各术的「古籍答案库」。

> **评测 vs 参照**：古籍案例是「只记应验、不记不应验」的占验记录，**没有「吉凶/标准答案」标签**，故只能作「断卦参照库」（Grep 相似卦例看古人怎么断），**不能作「准确率评测集」**。唯一有标准答案、能评测断卦准确率的，是 `mingli/` 的 MingLi-Bench 160 题（四选一，实测 36.2%，随机 25%）。

**无「占→验」案例的术**（典籍为方法论，非案例集）：奇门（断法规则）、太乙（纯推算法）、七政（星命理论）、风水（理论 + 名地图）、择日（官方历书考订）、相术（相法理论）。这些术的古籍里没有「某人占某事→应验」的结构，案例需靠真实使用累积，或按各自形态另立（风水布局案例 / 择日宜忌案例 / 看相断例）。

## 基准参考

断卦准确率可参照 [MingLi-Bench](https://github.com/DestinyLinker/MingLi-Bench)（全球算命师大赛 2022–2025 真题 160 题）。诚实参照系：四选一随机线 25%，人类 Top-20 约 53.5%，当前顶尖工程化 Agent 约 45–50%。排盘确定性是本技能能保证的；断卦准确率只能力求「可追溯、可后验、可校准」，不宣称「保证准」。
