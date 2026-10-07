# 老师傅 MCP Server

这是一个神奇的skill。不同于大模型的简单算法，双系统交叉验证大幅提高准确率，看命用八字+紫微斗数，看事用六爻+奇门遁甲。命运、婚恋、事业、问事成败与时机；支持公历、农历、四柱反查及时间或三数起卦。先问清资料，调用真实排盘，再把相关依据讲给你听。说话直，但不吓人；需要细讲再展开。

本仓库把这套 Skill 里**真实跑排盘的那部分**做成了 MCP 服务器：任何支持 MCP 的客户端都能直接调用八字紫微双盘、六爻奇门双法同参、标准卦图和四柱反查。盘由本地引擎算出来，不是让大模型"想一想"写一个。

## 工具

| 工具 | 用途 | 关键参数 |
| --- | --- | --- |
| `bazi_ziwei_chart` | 八字+紫微双盘。四柱、十神、长生、纳音、刑冲合害、格局旺衰、十二宫主辅星与四化、大运、流年、可引用证据 | `year/month/day/hour`、`gender`、`calendar`（必须显式指定公历或农历）、`is_leap_month`、`current_year` |
| `liuyao_qimen_fusion` | 六爻+奇门双法同参。两法各自结论、一致/互补/冲突标记、证据编号与强度、成败倾向、时间与条件 | `question`、`method`（`time` 或 `numbers`）、起卦当刻、`category`、`time_zone` |
| `hexagram_diagram` | 固定坐标的标准六爻卦图 PNG（本卦、变卦、六亲、六神、世应、伏神、动爻），同时返回逐爻文字备用 | 同 `liuyao_qimen_fusion` |
| `resolve_pillars` | 只给四柱时反查候选公历年份 | `pillars`、`start_year`、`end_year` |
| `laoshifu_consultation` | 老师傅完整会谈的正式入口 | 无 |

另外提供一个提示词 `laoshifu_reading`，把已经排出的盘讲成一段自然的话，而不是输出字段清单。

## 为什么盘是可信的

排盘、起卦、画图全部调用与 Skill 同源的权威引擎，MCP 层不做任何算术：

- 八字与紫微：`engine/calculator/dist/run-chart.js`
- 六爻与奇门：`scripts/liuyao.cjs`、`scripts/qimen.cjs`、`scripts/qimen_core/`
- 卦图：`scripts/diagram_render.py`（结构直出 PNG，不用 AI 生图重绘）
- 四柱反查：`scripts/resolve-pillars.cjs`

因此工具输出与 Skill 输出不可能漂移。仓库自带回归用例，用固定输入比对四柱，防止引擎被换掉而没人发现。

## 安装

需要 Python 3.10+ 与 Node.js 18+（引擎里的历法与干支换算依赖 Node）。

```bash
# 直接从 GitHub 运行，不需要预先安装
uvx --from git+https://github.com/william22820785-cmyk/laoshifu-mcp laoshifu-mcp
```

已用 `uv tool install --from git+https://github.com/william22820785-cmyk/laoshifu-mcp laoshifu-mcp`
装进本地的，直接运行 `laoshifu-mcp` 即可。

## 客户端配置

```json
{
  "mcpServers": {
    "laoshifu": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/william22820785-cmyk/laoshifu-mcp",
        "laoshifu-mcp"
      ]
    }
  }
}
```

已把包装进某个环境的，把 `args` 换成 `["laoshifu-mcp"]` 即可。

## 输入约定

**看命**用 `bazi_ziwei_chart`。公历与农历必须由调用者明确指定，不能默认按公历处理；农历闰月要显式标记。出生排盘当前只接纳东八区，其他时区需先人工核准出生地。晚子时（23 点）按次日处理。

**问事**用 `liuyao_qimen_fusion`。必须先把事问实再起卦：`method=time` 用确认当刻起卦，`method=numbers` 必须由本人凭第一念报三个正整数，不能代选、不能暗示。同一件事不要因为不喜欢结论而重复起卦。

**只有四柱**时先用 `resolve_pillars` 反查。四柱会重复：0 个候选说明输入有误，多个候选必须让用户确认，唯一候选才继续。

## 输出规模

默认 `detail=summary`，去掉 `bazi`/`ziwei` 里重复的出生信息与四柱块，以及已废弃的旧卦图字段。一次双盘的返回约 6—7 千字符，六爻奇门约 3—4 千字符。需要原始完整 JSON 时传 `detail=full`。

## 边界

- 结果描述的是盘面结构和算法结论，**不等于现实预测，也不代表预测经过科学验证**。两法同向不等于保证应验。
- 健康只谈压力与生活管理，不做疾病诊断，不推断寿命；财富不承诺收益；关系不宣判离婚或复合必然发生；法律与安全不替代专业决策。
- 排盘本地运行不代表对话全程离线。
- 本服务器只排盘。老师傅的会谈断法、口吻与校准问句是 Skill 的另一半，见 `laoshifu_consultation`。

## 开发与验证

```bash
python scripts/sync-runtime.py --force   # 从 Skill 源仓库同步运行时
python scripts/sync-runtime.py --check   # 确认运行时完整且不含会谈断法资料
python scripts/verify-bundle.py          # 只靠打包运行时跑一遍四个引擎并比对已知结果
python -m unittest discover -s tests     # 20 个用例：工具注册、输入校验、引擎回归
python scripts/smoke-stdio.py            # 真实 MCP stdio 契约测试
```

`laoshifu_mcp/_runtime/` 由 `sync-runtime.py` 生成，不进版本库；发布包由构建流程注入。

## 许可

本项目自有部分以 MIT No Attribution 发布，见 [LICENSE](LICENSE)。第三方组件（八字紫微引擎、六爻算法、lunar-typescript、mingyu-core、tyme4ts、卦图字形）的许可与出处见 [NOTICE](NOTICE)。
