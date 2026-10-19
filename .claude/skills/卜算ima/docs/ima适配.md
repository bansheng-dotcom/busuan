# ima 适配指南（双模）

本技能在 ima 里按「有没有代码执行能力」分两档运行。本文是**从本地 Claude Code 版迁移到 ima 的完整操作手册**，含三形态对照、知识库导入、沙箱配置、Skill 广场打包、已知限制。

## 0. 结论先行：ima 三形态对照

| ima 形态 | 能干什么 | 能跑 `scripts/cast.py` 起盘吗 | 对应本技能模式 |
|---|---|---|---|
| ① 普通知识库问答 | 只有 search（检索知识库 + 全网），不跑代码 | ❌ 不能 | **模式 B（降级）** |
| ② Copilot 助理（知识 Agent） | 云端沙箱 `/sandbox/workspace/`：跑 Python/Shell、`pip install`、读写文件，同时检索导入的知识库 | ✅ 能 | **模式 A（全功能）** |
| ③ ima OpenAPI Skill（ima-skill） | 通过 HTTP API 操作笔记 + 知识库（`search_knowledge` 等），可被 Claude Code/Codex 桥接调用 | 代码跑在本地 Claude Code | 桥接变体（起盘留本地） |

> 你观察到的「ima 里只能用 search」是形态 ①。要「16 术起盘全跑通」，必须用形态 ② 的沙箱。

## 1. 双模判定

- **模式 A（沙箱）**：环境能执行 Python/Shell → 起盘跑 `scripts/cast.py`，16 术全量、确定性全保。
- **模式 B（search-only）**：只有 search → 起盘降级：无盘术法（测字/相术/天文占/解梦·灵棋·易林）全支持；小六壬/梅花手算（简单取模）；八字/紫微/七政/六爻/六壬/金口诀/奇门/太乙/风水/择日**需用户自带盘面**。

## 2. 知识库导入（两模式都要做，一次性）

检索典籍原文是断卦的地基，无论哪种模式都要把典籍送进 ima 知识库：

1. 在 ima 新建一个知识库（建议命名「卜算典籍库」）。
2. 上传三块内容：
   - **典籍 txt**：`D:\卜算\国学czhengli\txt\` 下 423 份 txt（**排除 `_去重备份\`** 繁简重复目录）。
   - **案例库**：`D:\卜算\国学czhengli\txt\案例库\`（1300 则古籍占验案例 + 现代补充层）。
   - **速查表 + 分术文档**：`references\`（23 个速查表）+ `docs\`（20 个分术文档）。
3. 若 ima 不接受 `.md`，先转成 txt/PDF 再传。
4. 检索时：search 按关键词（卦名/爻辞/口诀/神煞/格局/断语）命中，引用注明出处书名。

> 已知：ima 的 `search_knowledge` 单次只搜**一个**知识库、每库最多返回 100 条、无相关度评分。建议典籍 + 案例 + 速查集中放**同一个知识库**，避免跨库检索不到。

## 3. 沙箱模式（模式 A）配置

1. 把 `scripts\` 整个目录（**含 `scripts\libs\engines\taiyi\data.pkl`**，太乙引擎硬依赖）上传到沙箱 `/sandbox/workspace/`；典籍 txt 也一并上传，便于 `Grep`/`scripts/classical_search.py` 精确复核行号。
2. 装依赖（一次性）：
   ```bash
   pip install lunar_python ephem cn2an bidict drawsvg py-iztro
   # 太乙博弈分析（可选）：pip install numpy
   ```
3. 起盘照跑（示例）：
   ```bash
   python scripts/cast.py meihua            # 梅花时间起卦
   python scripts/cast.py bazi --time "1990-05-20 08:30" --lon 116.4
   python scripts/cast.py liuyao --html
   ```
4. 断卦检索：优先 search 知识库；沙箱内 txt 在 workspace 时可用 `Grep` 或 `scripts/classical_search.py --search 关键词` 复核原文行号。

## 4. Skill 广场 ZIP 打包合规（可选路线，上传 Skills 广场用）

若走「上传 Skill 包」而非沙箱直接拷贝，须满足 ima 的 SKILL.md 规范：

- `name`：已改为 `busuan`（小写字母/数字/连字符，原中文 `卜算` 不合规）。
- **文件数 ≤300**：已清理全部 `__pycache__/*.pyc`，现 213 个文件 ✅。
- **禁二进制**：`data.pkl`（78KB，太乙硬依赖）是唯一二进制，**ZIP 上传须排除**——后果是太乙引擎导入即报错，见 §5。
- `SKILL.md` 必须在 ZIP 根目录。
- 只允许 .md/.py/.js/.txt/.json/.yaml 等纯文本。

## 5. 已知限制与需实测项（诚实清单）

| 项 | 状态 | 说明 / 应对 |
|---|---|---|
| 沙箱能否 `pip install ephem`（含 C 扩展）等全部依赖 | ⚠️ 需实测 | 若个别包装不上，对应术法降级为「自带盘面」 |
| `data.pkl` 二进制在 ZIP 路线被禁 | ⚠️ 已知限制 | 沙箱路线保留即可；ZIP 路线太乙起盘不可用，需本地起盘后贴盘面 |
| 沙箱文件是否跨会话持久 | ⚠️ 需实测 | 若每次重置，依赖与 txt 需重装/重传 |
| ima search 命中质量（无相关度分、单库 100 条上限） | ⚠️ 需实测 | 关键词检索 + 段落 ID 回查补强；检索不到原文就明说「依 XX 法推演，非直接引文」 |
| 典籍 423 份 txt 全部导入后的检索效率 | ⚠️ 需实测 | 必要时按术拆分知识库 |

**底线**：无论哪种模式，「起盘用脚本算（不许心算）、断卦用原文（不许杜撰）」不变——模式 B 对复杂术法宁可降级成「需自带盘面」，也不心算硬排。
