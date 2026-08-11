# Youzanyun Toolkit 使用文档

## 产品定位

Youzanyun Toolkit 是面向有赞云开放开发的 Codex 技能包。除安装和更新外，开发者不需要在终端里手动执行工具命令，日常操作统一在 Codex 操作台中通过自然语言或 slash 入口触发对应 Skill，由 Codex 读取 Skill 说明、查询文档、检查工程并完成必要的开发辅助操作。

## 安装和更新

安装 Youzanyun Toolkit 使用 `codex` 命令完成。安装是一次性环境准备；安装完成后，日常开发和排障统一回到 Codex task 中触发 Skill。

首次安装：

```text
codex plugin marketplace remove youzan
codex plugin marketplace add https://github.com/youzan/youzanyun-toolkit --ref main
codex plugin add youzanyun-toolkit@youzan
```

更新：

```text
codex plugin marketplace upgrade youzan
codex plugin add youzanyun-toolkit@youzan
```

安装或更新完成后，重新打开一个 Codex task，使新安装的 Skills 生效。

## 使用入口

统一入口是 Codex task。

开发者在 Codex 输入需求时，可以通过自然语言显式写出 Skill 名称，也可以直接使用 slash 入口触发 Skill。Codex 会根据 Skill 说明执行后续动作，并在需要登录、选择应用、确认风险操作或补充信息时向开发者询问。

推荐表达格式：

方式一：自然语言触发。

```text
使用 <skill-name>，帮我完成 <具体任务>。
```

```text
使用 yzy-knowledge-search，查询“订单开放消息”相关文档，并总结接入方式。
```

```text
使用 yzy-frontend-dev，帮我开发一个有赞云 H5 页面扩展。先读取工程结构和官方开放能力，再改代码。
```

方式二：slash 触发。

```text
/<skill-name> <具体任务>
```

```text
/yzy-knowledge-search 查询“订单开放消息”相关文档，并总结接入方式。
```

```text
/yzy-frontend-dev 帮我开发一个有赞云 H5 页面扩展。先读取工程结构和官方开放能力，再改代码。
```

如果 Codex 操作台支持 slash 菜单，也可以输入 `/` 后从候选列表中选择对应 Skill，再补充具体任务。

## 前置条件

- 已能正常打开 Codex 操作台。
- 已按“安装和更新”章节安装 Youzanyun Toolkit Skills。
- 已拥有目标有赞云开放平台应用的开发权限。
- 需要应用级操作时，Toolkit 会通过公网 stable 渠道安装或复用本机 `zancli`，当前验证版本为 `1.0.18`。
- 如需本地页面调试，浏览器环境已安装 YZY Browser Developer Tool。（可以在可用Skill-初始化开放工程中安装）
- 目标工程已在 Codex 当前工作区，或开发者能在 Codex 中说明工程位置。

如果 Codex 识别不到相关 Skill，先重新打开一个 Codex task；仍无法识别时，按“安装和更新”章节重新安装或更新 Youzanyun Toolkit。

如需检查 YZY Browser Developer Tool 版本，优先执行官方 YZY CLI 的版本检查或初始化流程。Toolkit 清单只记录发布时验证过的最低版本和下载地址；如果 CLI 提示的最低扩展版本更高，以 CLI 实测门槛为准，不要把版本门禁失败误判为登录失败或工程不兼容。

## 可用 Skill

| Skill | 什么时候使用 |
|---|---|
| `yzy-knowledge-search` | 查询有赞云开放文档、开放 API、扩展点、开放消息、接入方案、工单答疑和错误说明。 |
| `yzy-project-bootstrap` | 初始化有赞云开放工程，或排查工程首次启动流程。 |
| `yzy-frontend-dev` | 开发 H5、小程序、商家端页面扩展，以及 Slot、Data、Method、Hook、Event 等前端开放能力。 |
| `yzy-browser-debug` | 调试本地运行页面，包括 Console 报错、Network 异常、DOM 状态、热更新和页面连接问题。 |
| `yzy-app-context` | 在应用级操作前解析和校验目标应用、环境、发布目标、绑定 addon 和开放能力状态。 |
| `yzy-api-capability` | 设计或调用开放 API 前，查询能力包、能力包详情、目标 API 授权状态，并在明确确认后申请能力包。 |
| `yzy-app-env` | 读取、脱敏查看、受控注入和变更有赞应用环境变量。 |
| `yzy-pipeline` | 查询构建计划、触发构建、查看构建记录状态和步骤日志。 |
| `yzy-log-trace` | 搜索应用日志、统计日志、展开日志上下文、按 traceId 汇总链路排障。 |
| `yzy-rds` | 查询应用绑定数据库、表结构、DDL 预检查、DML 查询和历史记录。 |

## 基本使用方式

### 1. 查询开放文档

适用于以下问题：

- 某个开放能力怎么用。
- 某个开放 API 有哪些参数。
- 某个扩展点、Slot、事件或开放消息是否存在。
- 某个错误码或接入失败原因如何处理。

在 Codex 输入：

```text
使用 yzy-knowledge-search，查询“应用授权失败”的有赞云开放文档，并给出处理建议。
```

```text
使用 yzy-knowledge-search，查询“订单开放消息”的接入方式，回答时列出依据来源。
```

```text
使用 yzy-knowledge-search，查询 youzan.item.get 的文档和 schema，说明请求参数和响应字段。
```

使用要求：

- 查询词尽量短而明确。
- API 名、错误码、字段名、方法名保持原样。
- 让 Codex 基于检索结果回答，不要接受没有来源依据的猜测。

### 2. 初始化开放工程

适用于新建有赞云开放工程、首次接入已有应用，或补齐已有工程缺失的前端开放 2.0 开发结构。

在 Codex 输入：

```text
使用 yzy-project-bootstrap，帮我初始化一个有赞云开放工程。请按当前 Skill 说明执行，并在需要我登录、选择团队、选择应用或确认目录时停下来问我。
```

也可以明确开发目标：

```text
使用 yzy-project-bootstrap，初始化一个有赞云开放工程。这次需要 H5 端开发，并检查浏览器插件是否已安装。
```

```text
使用 yzy-project-bootstrap，初始化当前应用的前端开放开发环境。我需要同时支持 H5 和商家端页面开发。
```

如果已有工程但无法启动：

```text
使用 yzy-project-bootstrap，排查这个有赞云开放工程为什么首次启动失败。先读取 README、AGENTS.md 和 package.json，再给出处理步骤。
```

新工程初始化通常会经过以下环节：

1. 确认工程保存位置。Codex 会先确认当前目录是否适合创建工程，避免覆盖已有业务代码。
2. 登录有赞云账号。若需要扫码、浏览器登录或选择账号，Codex 会停下来等待开发者完成。
3. 选择团队和应用。Codex 会引导选择目标团队、目标应用和代码分支；应用不明确时不会自行猜测。
4. 确认开发目标。Codex 会询问本次是否涉及 H5、消费者端小程序、商家端页面等开发目标，并按选择初始化对应结构。
5. 安装或检查 AI Skills。Codex 会确认 Youzanyun Toolkit Skills 是否已安装；缺失时提示按本文“安装和更新”章节处理。
6. 检查浏览器插件。若涉及 H5 或商家端页面调试，Codex 会先执行 CLI 版本检查，再提示是否需要安装或更新 YZY Browser Developer Tool。
7. 初始化前端开放 2.0 工程。Codex 会通过官方初始化流程生成或补齐前端开放开发目录、配置和根目录脚本。
8. 安装开发依赖。Codex 会按工程约定安装依赖；开发 Runtime 只应位于前端工程根目录开发依赖中。
9. 启动本地 dev。Codex 会按开发目标启动对应本地开发流程，并说明需要开发者在浏览器中打开或连接的页面。
10. 交接下一步。Codex 会说明后续应使用哪个工程目录、哪个 dev 入口，以及如果页面未渲染本地代码应继续使用 `yzy-browser-debug`。

开发目标选择说明：

- H5 端：适用于消费者端 H5、商家 App H5、企业微信助手 App H5 等页面扩展；通常需要浏览器插件配合调试。
- 消费者端小程序：适用于小程序开放页面或能力接入；初始化时应确认对应端和页面入口。
- 商家端页面：适用于商家后台页面扩展；通常需要确认页面模块、开放能力和本地调试连接。
- 多端并行：如果同时涉及 H5、小程序和商家端，Codex 会优先确认端类型和启动方式，避免多个 Runtime 争用同一固定端口。

已有工程处理规则：

- 如果仓库已经包含前端开放 2.0 结构和根目录脚本，Codex 会优先使用现有脚本继续开发。
- 如果仓库缺少必要结构，Codex 会通过官方初始化流程补齐，不手工复制模板目录。
- 如果只是继续开发已有代码，Codex 不会重新 clone 或覆盖业务代码。
- 初始化完成后，开发和构建应使用生成工程根目录暴露的脚本，不重复调用底层工具。

开发者不需要自己复制执行初始化命令。

### 3. 管理应用环境变量

适用于读取、脱敏查看、受控注入或变更有赞应用环境变量。

在 Codex 输入：

```text
使用 yzy-app-env，查看当前应用 dev 环境有哪些环境变量。
```

```text
使用 yzy-app-env，读取当前应用 prod 环境的 opensdk.clientSecret。只给我脱敏后的结果。
```

```text
使用 yzy-app-env，给当前应用 dev 环境新增一个临时环境变量，先确认应用和环境再执行。
```

Codex 应完成的动作：

- 先确认 `zancli` 可用且已登录。
- 读取或修改前先确认目标应用和环境。
- 默认按 CLI 脱敏展示敏感键值。
- `exec` 仅向指定子进程注入环境变量，不修改父 shell。
- `create`、`update`、`delete` 都属于写操作，需要开发者明确确认。

### 4. 开发前端开放页面

适用于 H5、小程序、商家端页面扩展或开放能力接入。

在 Codex 输入：

```text
使用 yzy-frontend-dev，帮我实现这个有赞云 H5 页面扩展：<描述需求>。先确认目标端、开放能力和现有代码模式，再做最小代码修改。
```

```text
使用 yzy-frontend-dev，帮我判断这个需求应该用 Slot、Data、Method、Hook、Event 还是整页替换。请先查询官方开放能力依据。
```

```text
使用 yzy-frontend-dev，检查当前工程里已有的商家端页面扩展实现，并按相同模式新增一个入口。
```

Codex 应完成的动作：

- 读取目标工程的 `README.md`、`AGENTS.md`、`package.json` 和相邻实现。
- 确认目标端和页面。
- 查询官方开放能力依据。
- 判断可用能力边界。
- 修改代码并说明改动范围。
- 使用工程已有验证方式检查结果。

开发者需要提供的信息：

- 目标页面或业务场景。
- 目标端，例如 H5、小程序或商家后台。
- 期望交互、展示内容或接口行为。
- 如有设计稿、接口文档或错误截图，在 Codex 中一并提供。

### 5. 调试本地页面

适用于本地页面没有渲染、热更新不生效、接口异常、Console 报错或页面元素缺失。

在 Codex 输入：

```text
使用 yzy-browser-debug，检查当前页面为什么没有渲染本地代码。请先确认页面连接状态，再采集 Console、Network 和 DOM 证据。
```

```text
使用 yzy-browser-debug，排查这个接口请求为什么失败。请采集 Network 证据，注意隐藏敏感信息。
```

```text
使用 yzy-browser-debug，验证我刚才的页面修改是否已经生效，并检查是否有新增 Console error。
```

Codex 应完成的动作：

- 定位目标工程和本地开发服务。
- 检查页面是否已连接到 YZY Browser Developer Tool。
- 读取 Console、Network、DOM 等证据。
- 根据证据定位源码问题。
- 修改后刷新页面并复验。

开发者需要配合的动作：

- 确保本地页面已打开。
- 按 Codex 提示完成浏览器插件连接。
- 对登录、授权、删除、提交订单、支付等不可逆操作进行明确确认或拒绝。

### 5. 解析应用上下文

适用于能力包、构建、日志、链路、数据库等应用级操作前，先确认 Codex 当前要操作的是哪个应用和环境。

在 Codex 输入：

```text
使用 yzy-app-context，解析当前工程对应的有赞云应用上下文，并告诉我应用 ID、应用名称、环境、应用类型和开放能力状态。
```

```text
使用 yzy-app-context，校验目标应用是否是 <应用名称或应用 ID> 的 <环境> 环境。若无法确认，请先停下来问我。
```

Codex 应完成的动作：

- 从当前工程或开发者提供的信息解析目标应用。
- 展示解析到的应用 ID、名称、环境、应用类型和相关状态。
- 发现目标不明确、环境不匹配或权限异常时停止后续操作。

### 6. 查询和申请开放 API 能力包

适用于调用开放 API 前确认当前应用是否具备 API 授权，或在确认缺少授权后提交能力包申请。

在 Codex 输入：

```text
使用 yzy-api-capability，检查当前应用是否已授权开放 API youzan.trade.get。请先解析应用上下文，再给出结论和依据。
```

```text
使用 yzy-api-capability，查询当前应用类目下和“商品”相关的 API 能力包，并说明哪些已授权、哪些未授权。
```

```text
使用 yzy-api-capability，帮我申请 package-id 为 <package-id> 的能力包。申请理由是：<reason>。请先展示应用、环境、能力包 ID 和申请理由，等我确认后再提交。
```

Codex 应完成的动作：

- 先使用 `yzy-app-context` 确认目标应用。
- 查询能力包列表、能力包详情或目标 API 授权状态。
- 明确区分已授权、未授权、审核中、被驳回、类目不支持等状态。
- 申请能力包前，要求开发者明确提供 `package-id` 和申请理由。
- 提交申请前，展示应用、环境、能力包 ID 和申请理由，并取得“提交真实申请”的单独确认。

注意：能力包用于开放 API 授权判断；开放消息和扩展点不通过能力包授权。

### 7. 查询或触发构建

适用于查询构建计划、查看构建记录、查看步骤日志，或在明确确认后触发构建。

在 Codex 输入：

```text
使用 yzy-pipeline，查询当前应用 dev 环境的构建计划和最近一次构建状态。请先解析应用上下文。
```

```text
使用 yzy-pipeline，查看构建记录 <recordId> 的状态和失败步骤日志。
```

```text
使用 yzy-pipeline，准备触发 <应用名称> 的 <环境> 环境构建，分支是 <branch>。请先展示应用、环境、计划和分支，等我确认后再继续。
```

Codex 应完成的动作：

- 先使用 `yzy-app-context` 确认应用和环境。
- 查询计划、记录、状态或步骤日志。
- 多个构建计划存在时让开发者选择，不自动猜测。
- 触发构建前必须获得开发者对应用、环境、计划和分支的明确确认。

### 8. 查询日志和链路

适用于排查线上或测试环境问题，按关键词、级别、traceId 或时间窗口查看证据。

在 Codex 输入：

```text
使用 yzy-log-trace，查询当前应用 prod 环境最近 1 小时包含“NullPointer”的错误日志。请先解析应用上下文。
```

```text
使用 yzy-log-trace，按 traceId <traceId> 汇总链路，并结合相关日志说明失败原因。
```

```text
使用 yzy-log-trace，统计当前应用最近 6 小时 ERROR 日志数量，并列出主要错误摘要。
```

Codex 应完成的动作：

- 先使用 `yzy-app-context` 确认应用和环境。
- 查询日志、计数、上下文或 trace 汇总。
- 对空结果明确说明“未命中”，不当作系统故障。
- 输出日志证据前隐藏敏感字段。

### 9. 查询和操作数据库

不支持直接操作生产数据库写入。

适用于查看应用绑定数据库、表列表、表结构、DDL 预检查、DML 查询和历史记录。

在 Codex 输入：

```text
使用 yzy-rds，查询当前应用绑定了哪些数据库和表。请先解析应用上下文。
```

```text
使用 yzy-rds，查看表 <tableName> 的表结构，并说明关键字段含义。
```

```text
使用 yzy-rds，预检查这条 DDL 是否可执行：<DDL 语句>。只做预检查，不要真正执行。
```

```text
使用 yzy-rds，查询表 <tableName> 最近 20 条记录。请先展示查询语句，等我确认后再执行。
```

Codex 应完成的动作：

- 先使用 `yzy-app-context` 确认应用和环境。
- 查询数据库、表、表结构或历史记录。
- DDL/DML 操作前展示应用、环境、数据库、表和语句。
- 写操作或可能影响数据的操作必须等待开发者明确确认。
