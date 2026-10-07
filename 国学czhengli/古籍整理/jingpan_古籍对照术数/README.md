# 经盘

古籍对照的术数研习站：斗数排盘、《紫微斗数全书》卷一至卷三、罗盘与老黄历、纳音起名、六壬法。命盘摘句与格局仍只取卷一；所有命理文字均取自底本，不生成白话吉凶断语。起名用字为站内精选研习表（非全书原文），纳音依据可跳转卷二歌诀。

## 本地运行

```bash
npm install
npm run dev
```

浏览器打开终端提示的本地地址（默认 `http://localhost:5173`）。

生产构建：

```bash
npm run build
npm run preview
```

SEO：构建时会生成 `public/sitemap.xml`；站点源地址可用环境变量 `VITE_SITE_ORIGIN`（默认 `http://38.55.194.234`）覆盖，影响 canonical / OG / sitemap。

重新生成古籍 JSON（含卷二、卷三切章）：

```bash
npm run build:data
```

## 页面

| 路由 | 说明 |
|------|------|
| `/` | 首页 |
| `/chart` | 排盘（点击星曜弹出《诸星问答论》原文） |
| `/book` | 卷一／卷二／卷三全文，侧边目录锚点 |
| `/yijing` | 易经64卦（断易天机，倪海厦天纪公开整理） |
| `/star-dict` | 诸星问答论词典（卷一） |
| `/pattern-dict` | 格局歌诀词典（卷一） |
| `/luopan` | 罗盘 |
| `/almanac` | 老黄历 |
| `/naming` | 纳音起名（日柱纳音喜用 + 精选字库，可跳转卷二纳音歌） |
| `/liuren` | 六壬法（农历月日时六宫，倪海厦天纪算法本地推算） |
| `/yaogua` | 摇卦（三钱起卦六爻，可跳转易经原文） |
| `/about` | 来源与免责声明 |

## 数据

| 文件 | 说明 |
|------|------|
| `scripts/raw/ms261794.html` | 卷一底本（国学典籍网） |
| `scripts/raw/ms261795.html` | 卷二底本（国学典籍网） |
| `scripts/raw/ms261796.txt` | 卷三底本（国学典籍网） |
| `src/data/bookJuan1.json` 等 | 切章后繁体章节 |
| `src/data/bookSources.json` | 三卷底本链接 |
| `scripts/ingest-juan23.mjs` | 三卷切章 + 简转繁（不校改） |
| `scripts/build-data.mjs` | 星曜／格局词典切条，并合并三卷 TOC |
| `src/data/yijingIntro.json` 等 | 易经64卦总论与各卦正文（来源见 about） |
| `scripts/ingest-yijing.mjs` | 抓取断易天机64卦索引与各卦页 |

底本链接：

- 卷一：http://ab.newdu.com/book/ms261794.html
- 卷二：http://ab.newdu.com/book/ms261795.html
- 卷三：http://ab.newdu.com/book/ms261796.html

## 约束

命盘只展示古籍原文与格局原始歌诀；庙旺落陷、四化、大限流年由公开安星算法计算。卷二、卷三仅供站内阅读，不参与排盘摘句匹配。

## 排盘 AI 解读（可选）

「AI 解读」页签经薄代理调用 Cloudflare Workers AI，生成**全息诊断**（验盘、命格、四化、六维、时空战略等），语气偏硬，仅供参考。

### 前端

复制 `.env.example` 为 `.env`，设置：

```bash
VITE_CHART_AI_HOLOGRAPHIC_API=/api/chart-ai-holographic
```

生产环境经 SPA 服务把 `/api/chart-ai-holographic` 反代到本机 `8787` 端口，无需跨域。本地 `yarn dev` 时 Vite 同样把该路径代理到 `127.0.0.1:8787`。

### 服务端代理

```bash
cp server/.env.example server/.env
# 填入 CF_ACCOUNT_ID、CF_API_TOKEN（勿提交 Git）
bash scripts/deploy-chart-ai.sh
```

或本地开发：

```bash
python3 server/chart_ai_proxy.py   # 默认 127.0.0.1:8787
# 另开终端
yarn dev
```

生产使用 `scripts/chart-ai-proxy.service`（Python，无需 Node）。`scripts/spa-server.py` 已支持同源 API 转发。
