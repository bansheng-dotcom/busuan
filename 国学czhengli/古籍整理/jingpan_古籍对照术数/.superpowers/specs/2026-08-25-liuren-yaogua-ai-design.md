# 六壬 / 摇卦 AI 解读设计

日期：2026-08-25  
状态：待用户审查  
依据确认：风格 B（解读倾向）+ 问题选填 C + 架构方案 1（共用代理、独立路径）

## 问题与目标

六壬、摇卦目前仅本地起课/摇爻，文案写明「无 AI」。希望补上 **AI 解读**：

- 全白话，可结合选填问题给出倾向说明（顺/滞、宜缓/宜动等）
- 无问题时做课式/卦象总览；有问题则对着问题答
- 禁止开运改命、绝对断语、医疗法律投资指令性建议
- 复用现有 Cloudflare AI 代理运维，不新增第二套密钥服务

## 非目标

- 不改六壬/摇卦起课与摇爻算法
- 不做多轮追问聊天
- 本轮不把排盘迁到新路径（排盘仍用 `/api/chart-ai-reading`）
- 不在前端暴露模型密钥

## 架构

```
六壬/摇卦页 → build*AiPayload → POST /api/divination-ai
                                    ↓
                          spa-server / vite proxy
                                    ↓
                          chart_ai_proxy.py (kind 分支)
                                    ↓
                          Cloudflare Workers AI
```

| 项 | 约定 |
|----|------|
| 新 API | `POST /api/divination-ai` |
| 排盘 API | 保持 `POST /api/chart-ai-reading` |
| 环境变量 | `VITE_DIVINATION_AI_API=/api/divination-ai`（未配时可回退同源相对路径） |
| 代理 | 扩展现有 `server/chart_ai_proxy.py`：增加路径与 `kind` prompt |
| 部署 | `scripts/deploy-chart-ai.sh` + SPA 转发；前端 `build` 后 rsync |

## 请求体

公共字段：

```ts
{
  kind: 'liuren' | 'yaogua'
  question?: string   // 选填，trim 后空则视为无问题
}
```

### kind = liuren

```ts
{
  kind: 'liuren'
  question?: string
  cast: {
    month: number      // 1–12
    day: number        // 1–30
    hour: number       // 1–12
    palaceName: string // 大安/留连/…
    luck: '吉' | '凶'
    summary: string    // 宫位既有摘要
  }
}
```

### kind = yaogua

```ts
{
  kind: 'yaogua'
  question?: string
  cast: {
    primary: { index: number, name: string, overview?: string }
    relating?: { index: number, name: string, overview?: string } | null
    changingPositions: number[]  // 1–6 或 0–5，前后端约定统一为 1–6 爻位
    lines?: Array<{ position: number, label: string, changing: boolean }>
  }
}
```

服务端 `compact`：截断 overview、过滤空 question、限制 lines 长度；不传大段古文。

## 提示词与输出

共用原则：

1. 只用 JSON 内信息，不编造未给出的课式/卦名
2. 现代白话；可写倾向，禁止绝对吉凶口号与开运改命
3. 有 `question` 必须回应所问；无则写「整体倾向」
4. Markdown 固定结构：

```markdown
## 总览
## 对所问事项
（无问题时本节标题改为「整体倾向」或仍用本标题但首句说明未提问）
## 注意点
## 说明
（仅供参考，不作唯一决策依据）
```

六壬 / 摇卦各一份 system prompt（短、分 kind 选择）。

风格校验（轻量）：必须含 `## 总览`；命中开运/改命等硬禁则 502。

## UI

### 六壬（`views/liuren/index.vue`）

出课结果卡片下方：

1. 选填输入：「所问事项（选填）」
2. 按钮「AI 解读」（loading / 防重复点击）
3. 结果区展示 Markdown 纯文本（与排盘 AI 类似用 `pre` 或简单渲染）
4. 未配置 API 时按钮禁用或提示未配置

### 摇卦（`views/yaogua/index.vue`）

本卦/之卦结果区底部：同上交互。

文案免责：结果旁短说明「AI 倾向解读仅供参考，请结合课式/卦象自行判断」。

路由 meta / 站内「无 AI」文案改为「可选用 AI 解读」类表述（仅这两页相关文案）。

## 前端模块

| 文件 | 职责 |
|------|------|
| `src/api/divinationAi.ts` | `isDivinationAiConfigured` / `fetchDivinationAi` |
| `src/utils/liurenAiPayload.ts` | 从 `LiurenResult` + question 组包 |
| `src/utils/yaoguaAiPayload.ts` | 从 `CastResult` + 卦名 overview + question 组包 |
| 两页 vue | 状态：`aiLoading` / `aiError` / `aiContent` / `question` |

## 代理改动要点（`chart_ai_proxy.py`）

- `do_POST` / `do_OPTIONS` 接受 `/api/divination-ai`
- 按 `kind` 选 prompt + compact
- `max_tokens` 约 1200–1800（解读短于排盘人生阶段）
- 超时策略与排盘类似（单次调用，不做双倍重试）
- `/health` 可带版本标记如 `divination-ai-v1`

## SPA / Vite

- `spa-server.py`：转发 `/api/divination-ai` → 上游同机 8787
- `vite.config.ts`：dev 代理同路径
- `.env` / `.env.example`：增加 `VITE_DIVINATION_AI_API`

## 验收

1. 六壬出课后无问题生成：有总览与整体倾向，无开运话术
2. 六壬带问题生成：正文回应问题
3. 摇卦有/无之卦、有/无动爻均可生成；overview 进叙事
4. 未配置 API 时有明确提示
5. 排盘 AI 原路径回归正常
6. 本地与生产 health + 一次真实生成通过

## 风险

| 风险 | 处理 |
|------|------|
| 六壬页面已有吉/凶标签，AI 过激 | prompt 要求「倾向」措辞，禁「必成/必死」 |
| 与「古籍研习」站调冲突 | UI 标明参考；说明段固定 |
| 代理文件膨胀 | kind 分支函数拆开，chart 逻辑不动 |
