# 卜算 · ima 双模版

这是「卜算」术数技能的 ima 适配版：**同一套知识，两套起盘路径**，按 ima 环境有没有代码执行能力自动分档。

## 一句话结论

- 想 **16 术起盘全跑通**（和本地 Claude Code 版一样完整）→ 用 **ima Copilot 助理（有沙箱）**，沙箱里跑 `scripts/cast.py` 起盘 + search 检索典籍断卦。
- 你的 ima **只有 search、没有沙箱** → 自动降级：无盘术法（测字/相术/天文占/解梦）全支持，小六壬/梅花手算，八字/紫微/六壬/奇门/太乙等**需用户自带盘面**。

## 三步上手

1. **导入知识库**：新建 ima 知识库，上传 `D:\卜算\国学czhengli\txt\` 423 份典籍 txt + 案例库 + `references\` 速查表 + `docs\` 分术文档。
2. **（可选，全功能用）装沙箱**：把 `scripts\`（含 `data.pkl`）传进沙箱 `/sandbox/workspace/`，`pip install lunar_python ephem cn2an bidict drawsvg py-iztro`。
3. **提问即断卦**：问「我最近财运如何」「测个「明」字」等，技能先起盘（沙箱）或要求贴盘面（降级），再 search 典籍原文分层断卦。

## 文档

- [SKILL.md](SKILL.md) — 总纲：路由 + 双模起盘策略（§〇）+ 输出/质检/证据规范。
- [docs/ima适配.md](docs/ima适配.md) — 完整迁移手册：三形态对照、知识库导入、沙箱配置、Skill 广场打包合规、已知限制与需实测项。

## 与原版「卜算」的区别

- 原版 `卜算`：本地 Claude Code，`cast.py` 起盘 + `Grep` 本地典籍，未动。
- 本版 `卜算ima`：加 §〇 双模适配、`name` 改为 `busuan`（ima 规范要求小写）、清掉 `__pycache__`（满足 Skill 包 ≤300 文件 + 禁二进制）、检索入口从「Grep 本地路径」改为「search 知识库」。
