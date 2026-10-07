# 卜算ima —— ima 知识库接入版

本目录是「卜算」技能的 ima 适配版：**典籍检索从本地 Grep 改为调腾讯 ima 知识库 OpenAPI**，其余（起盘脚本、断卦流程）不变。

## 接入步骤（3 步）

### 1. 拿凭证
打开 <https://ima.qq.com/agent-interface>，复制你的 **Client ID** 和 **API Key**。

### 2. 上传典籍 + 找知识库 ID
把 `D:\daimajieti1\国学czhengli\txt\` 下的 423 个 txt（含 `案例库/`）上传到 ima 知识库，然后查知识库 ID：

```bash
python scripts/search.py --list-kb --clientid <你的ClientID> --apikey <你的APIKey>
```

输出里每条的 `id=` 就是 `knowledge_base_id`。

### 3. 配置
把凭证和知识库 ID 写入 `scripts/ima_config.json`（复制 `ima_config.example.json` 改名填写），或设环境变量：

```
IMA_CLIENT_ID   = 你的 Client ID
IMA_API_KEY     = 你的 API Key
IMA_KB_ID       = 典籍知识库的 knowledge_base_id
```

## 检索（两种模式）

### 本地精确检索（推荐，等同 Grep，支持正则 + 繁简）
```bash
python scripts/search.py "妻财" --local --txt "D:\daimajieti1\国学czhengli\txt"
python scripts/search.py "青龙.{0,4}返首" --local --regex --txt "D:\daimajieti1\国学czhengli\txt"
```
首次运行自动建字级索引（缓存 `scripts/.index/`），之后毫秒级精确匹配；本地找不到会自动 fallback 到 ima。

### ima 知识库检索（语义兜底）
```bash
python scripts/search.py "妻财"            # 默认走 ima API（IMA_KB_ID）
python scripts/search.py "三命通会 疾病"   # 书名 + 关键词
```

> 可选：`pip install opencc-python-reimplemented` 启用繁简自动转换（不装也能用，仅影响繁简召回）。

## 起盘（不变，仍用 cast.py）

```bash
python scripts/cast.py bazi 2004 2 23 3 40 0 0
python scripts/cast.py zhiwei 2004 2 23 3 0
python scripts/cast.py qizheng --time "2004-02-23 03:40"
```

## 注意事项

- ima 检索是全文检索，**无相关性打分**；`search_knowledge` 单次最多约 100 命中。
- 古文（繁体）检索建议用**繁体、短词**做关键词（如「妻财」「官讼」「青龙返首」）；长句/白话分词对古文召回较差。
- 原 Grep 是精确子串匹配，ima 是语义/关键词检索，两者行为不同：**找不到时按 SKILL.md 要求明说「依 XX 法推演，非直接引文」，不编造经文**。
