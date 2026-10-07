# 排盘「AI 研习」：基于本盘原文的白话整理

日期：2026-08-24  
状态：已批准（对话确认）

## 背景

用户希望在排盘结果中增加 AI 读取命盘并给出说明的能力，且**保证解释正确、不随意发挥**。站点既有定位为古籍对照研习，**不编吉凶断语**；排盘页已能匹配卷一摘句、格局与宫位白话选句（均带出处）。

## 目标

1. 在排盘结果 `ChartResultTabs` 新增页签「AI 研习」。
2. 用户点击「生成研习说明」后，基于**本盘已命中的材料**生成结构化白话整理。
3. AI 只能解释投喂材料中的原句/格局；材料没有的写「原文未载」，禁止吉凶决策建议。
4. Cloudflare AI（OpenAI 兼容）经**服务器薄代理**调用；API Key 不进前端、不进 Git。

## 非目标

- 不做自由批命、吉凶祸福、宜忌行事建议。
- 不做全书向量检索（RAG 向量库）本期范围外。
- 不把 API Key / Account Token 写入仓库或浏览器打包产物。
- 不自动在排盘成功时调用 AI（须用户点击生成）。

## 方案选定

**结构化投喂 + 硬约束提示词（方案 1）**：前端组装本盘已有数据 → `POST` 同源/配置的代理 → 代理调用 `@cf/zai-org/glm-4.7-flash` → 返回 Markdown。

## 交互（§1）

### 页签

- 名称：`AI 研习`（繁简随站点 script）。
- 位置：`ChartResultTabs` 现有页签之后。

### 状态

| 状态 | 行为 |
|------|------|
| 无命盘 | 提示先完成排盘 |
| 有命盘、未生成 | 说明文案 + 按钮「生成研习说明」 |
| 生成中 | 按钮 loading，禁止重复点 |
| 成功 | 展示 Markdown（或分段渲染）；可复制全文 |
| 失败 | 错误提示 + 重试 |

### 清空

- 重置表单、重新排盘成功、或 chart 被清空时，清空 AI 结果与错误态。

### 声明文案（页签内常驻）

强调：仅整理本盘命中的卷一原文/格局之白话对照，不构成吉凶裁决；请点出处核对站内原文。

## 数据投喂

请求体由前端从现有排盘结果组装，字段示意：

```ts
{
  meta: {
    solarDate?: string;
    gender?: string;
    // 仅标识，不作发挥依据
  },
  palaces: Array<{
    name: string;
    stars: string[];
  }>,
  patterns: Array<{
    name: string;
    text: string;       // 歌诀原文
    source?: string;
  }>,
  excerpts: Array<{
    chapterTitle: string;
    chapterId?: string;
    text: string;
  }>,
  palaceReadings?: Array<{
    palace: string;
    classic: string;
    vernacular?: string;
    source?: string;
  }>
}
```

**原则**：未进入请求体的文献，模型不得当作依据。

## 代理与模型（§2）

### 接口

- `POST /api/chart-ai-reading`
- 部署在与静态站同机的薄服务（Node 推荐 `server/chart-ai-proxy.mjs`，或等价 Python）。
- 环境变量（示例名）：
  - `CF_ACCOUNT_ID`
  - `CF_API_TOKEN`（**须使用新 token；对话中曾出现的密钥视为已泄露，必须作废**）
  - `CF_AI_MODEL` 默认 `@cf/zai-org/glm-4.7-flash`
  - `CF_AI_BASE_URL` 默认 `https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1`
  - `PORT`（如 `8787`）
- 前端：`VITE_CHART_AI_API`（如 `http://38.55.194.234:8787/api/chart-ai-reading` 或经反代的 `/api/chart-ai-reading`）

### 系统提示硬规则

1. 只能使用用户消息中的 JSON 材料。  
2. 禁止吉凶、祸福、命运好坏、开运改命等建议。  
3. 每段白话须标明对应出处（章节名/格局名）。  
4. 材料不足处写「原文未载」，不得编造。  
5. 输出结构固定：
   - 总览（仅复述本盘已提供的星象/命中条目规模，不作断语）
   - 分宫整理
   - 格局整理
   - 研习提示（仅提醒对照站内原文）

### 服务端校验（最低）

- 拒绝空 body / 无任何 excerpts·patterns·palaceReadings 时返回 400，提示材料不足。  
- 可选：对模型输出做简单违禁词扫描（吉凶、大吉、大凶等）失败则重试一次或返回友好错误。

## 文件（§3）

```
src/views/chart/components/ChartResultTabs.vue
src/views/chart/index.vue
src/api/chartAi.ts          # 或 utils/chartAi.ts
.env.example                # VITE_CHART_AI_API=

server/chart-ai-proxy.mjs
server/.env.example         # CF_* 变量说明（不含真实密钥）
```

README 增加一小节：如何配置代理与环境变量、如何 systemd/nohup 常驻（简述）。

## 验收标准

1. 无命盘时页签有引导；有命盘可点生成。  
2. 成功结果含出处；故意空材料时不胡编（400 或「原文未载」）。  
3. 浏览器网络面板看不到 Cloudflare Token。  
4. 重置/换盘后旧 AI 文清空。  
5. 页内声明仍为研习对照、非吉凶裁决。

## 安全备注

- 对话中粘贴过的 `cfut_…` **必须轮换**。  
- `.env` / 服务器环境变量加入 `.gitignore`（确认未跟踪）。  
- 生产建议后续用 Nginx 反代 `/api/` 到代理端口，避免前端跨域；本期允许 CORS 仅限站点 Origin。
