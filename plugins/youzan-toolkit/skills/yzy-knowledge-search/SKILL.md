---
name: yzy-knowledge-search
description: 结合有赞云 llms.txt 文档导航、云文档中心搜索接口和 wiki 关键词搜索接口查询有赞云开放知识。用于回答开放平台、开发者接入、开放 API、开放消息、扩展点、定制需求、集成方案、工单答疑和能力咨询；其他有赞云开发 Skill 需要官方依据时也应使用本 Skill。
---

# YZY 有赞知识库查询

## 概述

结合 `https://doc.youzanyun.com/llms.txt` 文档目录导航、有赞云文档中心搜索接口和 wiki 关键词搜索接口，查询与用户问题相关的开放文档范围、内部知识库内容和 wiki 原文内容。当答案依赖有赞特定文档、内部实现、业务规则或定制需求背景时，优先查询知识库，不要凭通用经验猜测。

## 快速开始

运行内置搜索脚本：

```bash
python3 <skill-dir>/scripts/search_knowledge.py "订单接口" --top-k 3 --no-navigation --format pretty
```

面向单个用户问题时，Agent 先判断检索模式并提炼检索词，再执行单次检索。默认仍可使用原知识库搜索；查询 API 名、字段名、错误码、扩展点、wiki 条目等精确对象时，由 Agent 显式传入 `--mode wiki` 或 `--mode hybrid`，并尽量传入 `--wiki-keywords`。脚本会读取 Markdown 原文或 wiki 完整内容，并提取与问题相关的片段；证据足够时直接回答，不要再手工请求来源 URL，也不要换词重复检索。只有首轮结果为空、报错或明显不相关时，才允许再执行一次更精确的检索。

精确查询 wiki：

```bash
python3 <skill-dir>/scripts/search_knowledge.py "youzan.item.add sku_list 报错" --mode wiki --wiki-keywords 'youzan.item.add|sku_list|报错' --top-k 3 --no-navigation --format pretty
```

wiki 定位 + 原知识库补证据：

```bash
python3 <skill-dir>/scripts/search_knowledge.py "第三方支付通道扩展点 支付" --mode hybrid --wiki-keywords '第三方支付通道扩展点|下单支付|支付' --top-k 3 --no-navigation --format pretty
```

广泛了解某个业务模块时，可去掉 `--no-navigation`，同时读取 `llms.txt` 当前目录导航并返回匹配模块与候选文档。

如果脚本不可用，直接调用接口：

```bash
curl -sS -X POST 'http://doc.youzanyun.com/api/doc/knowledge/search' \
  -H 'Content-Type: application/json' \
  -d '{"query":"订单接口","topK":5}'
```

wiki 关键词搜索接口：

```bash
curl -sS -X POST 'http://doc.youzanyun.com/api/doc/wiki/search' \
  -H 'Content-Type: application/json' \
  -d '{"query":"云函数创建流程|云函数部署|支付","limit":10}'
```

查看有赞云文档目录：

```bash
curl -sS 'https://doc.youzanyun.com/llms.txt'
```

## 工作流程

1. Agent 将用户意图提炼成简洁的中文查询词。产品名、API 名、标识符、错误信息要保持原样；不要把整段闲聊式用户问题直接作为检索词。
2. Agent 根据意图选择检索模式：普通语义问答使用 `rag`；API、字段、错误码、扩展点、wiki 条目等精确对象使用 `wiki`；需要 wiki 精确定位并结合文档中心证据时使用 `hybrid`；模块探索才启用 `llms.txt` 导航。
3. Agent 为 wiki 查询提炼 1 到 3 个关键词，并通过 `--wiki-keywords 'kw1|kw2|kw3'` 显式传给脚本。`wiki` 和 `hybrid` 模式下该参数必填；脚本不做复杂语义路由和关键词规划。
4. 单点问答默认使用 `--top-k 3 --no-navigation` 完成一次查询；模块探索类问题才同时使用 `llms.txt` 导航。
5. wiki 搜索返回完整 `content` 时，脚本会按 Markdown 标题切片、按关键词打分、提取 `matchedSections` 和 `sourceExcerpt`，不要把完整 content 原样作为最终回答。
6. 优先使用脚本返回的 `sourceExcerpt` 回答具体字段、参数和规则问题。它来自首条结果的 Markdown 原文或 wiki 相关章节，避免因为搜索摘要截断而重复检索。
7. 先观察接口响应结构，再做总结。未知字段只能当作来源元信息，不要假设其业务含义。
8. 先基于检索结果给出结论，不要只贴接口 JSON。
9. 归纳关键依据；`llms.txt` 模块和文档链接可用于说明来源范围，知识库和 wiki 结果用于支撑结论。
10. 回答接口、扩展点、消息、方案类问题时必须有据可循，优先引用原始链接；缺少链接的 wiki 或知识库结果只能作为弱依据。
11. 只基于返回的知识库内容、wiki 内容和目录导航回答，不编造三者没有返回的事实。
12. 首轮结果为空、报错或明显不相关时，可再执行一次更精确的查询；一次用户问题最多执行两次知识检索。
13. 结果仍然含糊或接口不可用时，明确说明，并建议用户补充信息，不要继续循环调用工具。
14. 如果响应中包含标题、URL、文档 ID、slug 或其他来源标识，回答时一并标注。

## 内容有效性与时效判断

检索结果不是都能直接作为最终推荐方案，必须先做内容有效性筛选，并在同一章内处理输出内容和格式要求。

### 内容有效性规则

1. 如果结果中出现以下标记，不可作为最终推荐方案：
   - 已弃用
   - 已废弃
   - 已下线
   - 即将下线
   - 不推荐使用
   - 不推荐新接入使用
   - 仅历史兼容
   - 只维护不迭代
   - 不再维护
   - 请改用 xxx
   - 推荐使用 xxx
   - 已迁移至 xxx
   - 新接入开发者请使用 xxx
2. 如果结果明确给出了替代方案，应继续检索替代方案，并优先用替代方案文档回答。
3. 回答中的能力名称、接口名称、参数、示例、限制条件、操作步骤和参考文档，都必须以替代方案文档为准。
4. 历史兼容或背景说明可以简述，但不能作为新接入推荐。

### 公告时效规则

公告、通知、上线说明、变更通知、临时说明、活动说明、维护通知等内容，必须额外判断时效：

1. 默认只在发布时间起 2 个月内视为可作为当前结论依据。
2. 超过 2 个月且没有明确长期有效说明的公告，只能作为历史背景。
3. 当前问题必须依赖公告判断，但只检索到过期公告时，应继续查正式文档或更新说明。

### 输出内容要求

1. 回答中返回 `sourceUrl` 前必须先访问验证；只有 HTTP 状态为 2xx 时，才返回该 `sourceUrl`。
2. 默认面向人类输出归纳后的结论、操作步骤、关键依据和来源链接，不只返回接口原始 JSON。
3. 内部整理证据时，每条知识库结果必须尽量保留 `sourceType`、`sourceUrl`、`url`、`docId` 等来源字段；最终回答可按自然语言或列表呈现。
4. 内部追踪时，应汇总知识库原始链接、`llms.txt` 目录链接、模块链接和 Markdown 文档链接；最终回答优先引用已验证可访问的来源链接。
5. 缺少原始链接的条目只能作为弱依据，不能单独支撑关键结论；如引用此类条目，应明确说明缺少可验证链接。
6. 不要根据字段名猜测知识库未返回的事实；脚本只能抽取标题、摘要、类目路径、URL、文档 ID 等可见信息。

### 输出格式要求

1. 面向人类展示时，调用脚本使用 `--format pretty`，最终回答也默认使用自然语言、列表或表格等人类可读格式。
2. 只有用户明确要求 JSON、结构化输出、机器可读结果或需要沉淀为程序输入时，才输出归纳后的 JSON；JSON 中可包含 `originalQuery`、`usedQuery`、`conclusion`、`evidence`、`sources`、`navigation`、`traceability` 等字段。
3. 用户明确要求原始结果时使用 `--full-response`，在输出中附带完整接口响应。

## 查询建议

- 优先使用短查询词和核心名词：`订单接口`、`优惠券叠加`、`定制需求 购物车`、`商品同步 API`、`开放消息`、`扩展点`、`集成方案`。
- 查询代码或 API 问题时，保留用户给出的稳定名称：方法名、接口路径、类名、字段名、活动 ID。
- 排查问题时，先搜索完整错误信息；结果不足时，再扩大到模块名或业务词。
- 知识库查询失败时，不要用通用知识编造有赞内部结论。

### FAQ 与运营类问题检索词改写

FAQ、运营规则、控制台操作、价格政策、App 开店支持范围等问题，不要把整句口语问题原样传给脚本。Agent 应先改写为“最像文档标题或 FAQ 标题”的短查询词，再调用脚本；如需保留原始问法，用 `--original-query` 传入。

改写原则：

- 一次只使用 1 到 4 个高置信关键词，不要把同一领域的整组同义词全部拼进查询。
- 优先使用知识库里可能存在的标题式表达，例如 `有赞云API服务费规则`、`AppSDK方案能实现哪些功能`。
- 首轮为空或明显不相关时，第二次再换一个更具体的标题式查询；一次用户问题最多两次检索。
- `--original-query` 保留用户原始问题，最终回答必须回到原始问题。

常见改写口径：

- API 套餐、服务费、最低多少钱、是否需要购买：优先查 `有赞云API服务费规则`；若问套餐包发放，再查 `套餐包是什么`。
- 服务商入驻、应用市场：查 `服务商入驻应用市场` 或 `应用市场入驻指南`。
- 保证金、发票、收据：查 `保证金退还`、`保证金收据`、`服务商开发票`，按问题只选一个。
- App 开店是什么、能实现什么：查 `AppSDK方案能实现哪些功能`；问装修查 `如何装修App开店的商城页面`；问 H5 接入查 `H5 与 App 集成`；问登录态查 `如何调用登录态API`。
- 消息推送、消息订阅、监听：查 `消息推送接入说明` 或 `消息订阅接入指南`；若问题给出消息名或 topic，必须原样保留。
- 商品上下架、商品变更监听：查 `商品事件 ITEM_STATE ITEM_INFO`。
- 电子面单、隐私面单、跨店铺取单：查 `电子面单 跨店铺取单`；问接口参数时查 `youzan.logistics.waybill.apply order_kdt_id`。
- QPS、限流、额度提升：查 `QPS 调用频率 控制台`。

改写只改变检索词，不改变最终回答语义；最终回答仍必须回到用户原始问题，并基于脚本返回的证据说明结论。

## 入参关键词解析

关键词规整应由调用 skill 的 Agent 负责，脚本只执行最终检索词。

解析规则：

- 优先提取引号、反引号、书名号中的显式检索词。
- 保留接口路径、开放 API 名、类名、方法名、字段名、错误码、英文标识符等稳定 token。
- 移除“帮我查一下”“知识库里有没有”“怎么处理”等检索话术。
- 保留有赞业务核心词，例如订单、商品、营销、优惠券、支付、退款、会员、店铺、库存、物流、开放 API、开放消息、扩展点、开发者、定制需求、集成方案等。
- 解析后的检索词过短或为空时，回退使用原始问题。
- 用户要求精确按输入查询时，直接把原始问题作为最终检索词。
- 如需留存原始问题，调用脚本时额外传入 `--original-query` 记录上下文。

## 接口约定

文档目录：

```text
GET https://doc.youzanyun.com/llms.txt
```

目录用途：

- 一级 `llms.txt` 按开发目标和业务领域列出模块。
- 模块链接指向领域内的 Markdown 摘要目录。
- 目录导航只用于定位来源范围和候选文档，不替代知识库检索结论。

接口：

```text
POST http://doc.youzanyun.com/api/doc/knowledge/search
Content-Type: application/json
```

请求体：

```json
{
  "query": "订单接口",
  "topK": 5
}
```

wiki 关键词搜索接口：

```text
POST http://doc.youzanyun.com/api/doc/wiki/search
Content-Type: application/json
```

请求体：

```json
{
  "query": "云函数创建流程|云函数部署|支付",
  "limit": 10
}
```

wiki 响应约定：

- 外层通常为 `{"code":0,"msg":"success","data":[...]}`。
- `data` 中每条结果至少关注 `title`、`slug`、`content`。
- `content` 是完整 Markdown 原文，脚本会在本地切片、打分、提取相关章节，不直接把完整原文当作最终答案。

## 脚本

使用 `scripts/search_knowledge.py` 执行可复用查询。脚本接收最终检索词，复杂模式选择和 wiki 关键词规划由 Agent 完成；`wiki` 和 `hybrid` 模式必须显式传入 `--wiki-keywords`。脚本默认返回 3 条结果，并自动读取首条结果的 Markdown 原文相关片段。默认输出 JSON，便于 Agent 组合调用；遇到 HTTP 或 JSON 错误时以非 0 状态退出。内部服务响应慢时，使用 `--timeout <秒数>` 调整超时时间。

职责边界：

- Agent 负责：判断用户意图、选择 `--mode`、提炼 RAG 查询词、提炼 1 到 3 个 wiki 关键词、判断是否需要二次检索。
- 脚本负责：调用接口、参数校验、解析响应、wiki content 切片、本地打分、风险标记、证据融合、统一输出。
- 脚本不负责：复杂语义路由、同义词扩展、业务判断、替用户生成最终结论。

模式参数：

- `--mode rag`：默认值。只调用原知识库搜索接口，保持历史行为。
- `--mode wiki`：只调用 wiki 关键词搜索接口，并对完整 `content` 做 Markdown 章节切片和本地打分。
- `--mode hybrid`：同时调用 wiki 关键词搜索和原知识库搜索，统一合并 evidence。
- `--mode nav`：只读取 `llms.txt` 导航，用于模块探索。

wiki 参数：

- `--wiki-endpoint <url>`：覆盖默认 wiki 搜索接口。
- `--wiki-limit <数量>`：wiki 搜索返回数量，默认 5。
- `--wiki-keywords <kw1|kw2|kw3>`：手工指定 wiki 关键词，最多 3 个；`wiki` 和 `hybrid` 模式必填。
- `--wiki-section-limit <数量>`：每条 wiki 结果保留的相关章节数量，默认 4。

wiki evidence 输出：

- `sourceType=wiki`
- `title`、`slug`、`docId`
- `matchedKeywords`
- `matchedSections`
- `sourceExcerpt`
- `riskFlags`

原文参数：

- `--source-depth <数量>`：读取前 N 条结果的 Markdown 原文，默认 1。
- `--source-timeout <秒数>`：单次原文请求超时，默认 5 秒。
- `--source-excerpt-limit <字符数>`：每条原文相关片段的最大字符数，默认 2500。
- `--no-source-hydration`：不读取 Markdown 原文，仅保留搜索摘要。

脚本会对结果做基础筛选：

- 命中弃用/废弃/下线/不推荐/只维护不迭代等标记的结果会被排除出最终推荐。
- 如果结果包含明确替代方案，脚本会优先尝试继续检索替代方案。
- 过期公告只保留为背景线索，不进入最终推荐集。

导航参数：

- 默认读取 `https://doc.youzanyun.com/llms.txt`，输出 `navigation.modules` 和模块下 `documents` 候选。
- 使用 `--no-navigation` 跳过目录导航。
- 使用 `--navigation-url <url>` 覆盖目录地址。
- 使用 `--navigation-top-n <数量>` 调整导航候选数量，默认 5。
- 使用 `--navigation-module-depth <数量>` 控制读取前几个模块的二级目录，默认 3。
