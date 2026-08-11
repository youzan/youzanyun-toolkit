---
name: yzy-api-capability
description: 查询和预检有赞云开放 API 能力包授权。用于设计或调用有赞云开放 API 前，确认当前应用类目下的 API 能力包、能力包详情、目标 API 是否已授权；所有应用级 capability 操作前必须先解析应用上下文并使用 zancli 校验登录。
---

# YZY API 能力包

在设计或调用有赞云开放 API 前，先确认当前应用有哪些 API 能力包，以及目标 API 是否已授权。能力包只用于 API 授权判断；开放消息和扩展点不通过能力包授权。

所有 `capability` 操作都先使用 `yzy-app-context` 解析目标应用；该 skill 会连带完成 `zancli` 的安装和登录校验。不要直接根据当前目录、应用名或上一轮对话执行 API 能力包命令。

`zancli` 安装校验入口同时提供 Python 和 Bash 两种形式。优先尝试 `python3 <plugin-root>/tools/zancli/ensure_zancli.py`；如果当前环境没有可用 Python 但有 Bash，再尝试 `bash <plugin-root>/tools/zancli/ensure_zancli.sh`。

## 通用前置

先解析应用上下文并向用户展示应用 ID、名称、环境、应用类型、发布目标、绑定 addon 与开放能力状态：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py
```

用户已指定目标时，完整传递通用选择参数：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py --app-id 79782 --env dev
python3 <app-context-skill-dir>/scripts/resolve_app_context.py --app-name self-container-test --env dev
```

上下文解析成功后，实际 `zancli capability` 命令继续携带相同的 `--app-id` 或 `--app-name`、`--env`，防止目标漂移。

## 查询能力包

### 列出 API 能力包

列出当前应用类目下的 API 能力包：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability list --app-name self-container-test --output json
```

按关键字过滤时，`--api`、`--package`、`--status` 三个过滤器互斥，不要同时传多个：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability list --app-name self-container-test --api 交易 --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability list --app-name self-container-test --package 商品 --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability list --app-name self-container-test --status granted --output json
```

`--status` 取值：`all`（默认）| `granted` | `not_granted` | `pending` | `rejected` | `withdrawn` | `unknown`。

### 查看能力包详情

查看某个 API 能力包的详情，包括 API 列表和文档链接：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability get --app-name self-container-test --package-id 1234 --output json
```

## 预检授权

精确预检一个 API 是否已授权：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability check --app-name self-container-test \
  --api youzan.trade.get --no-interactive --output json
```

`--api` 必须传完整的 API name。只匹配到模糊候选时，命令返回候选列表，不会静默当作已授权放行。

`check` 的结果直接看退出码和 JSON 中的 `allowed` 字段，不需要解析文字：

| 情况 | 退出码 | 错误码 |
|------|--------|--------|
| 已授权 | 0 | 无，`allowed:true` |
| 未授权但可申请 | 非 0 | `CAPABILITY_NOT_GRANTED` |
| 申请审核中 | 非 0 | `CAPABILITY_APPLICATION_PENDING` |
| 申请被驳回 | 非 0 | `CAPABILITY_APPLICATION_REJECTED` |
| 当前类目不支持 | 非 0 | `CAPABILITY_API_UNSUPPORTED` |
| 只匹配到模糊候选 | 非 0 | `CAPABILITY_API_AMBIGUOUS` |

## 申请能力包

`capability apply` 是真实提交申请的写操作。只能在以下条件都满足后执行：

- 已先解析目标应用上下文
- 用户明确指定了目标 `package-id`
- 申请理由 `reason` 由用户提供，不能代填或编造
- 用户已对“提交真实申请”做过单独确认

提交前先把应用、环境、能力包 ID 和申请理由展示给用户复核。确认无误后再执行：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli capability apply \
  --app-name self-container-test \
  --env prod \
  --package-id <package-id> \
  --reason '<reason>' \
  --confirm
```

`apply` 成功后表示申请已经提交，后续状态以审核结果为准。可继续用 `capability list --status pending` 或按能力包关键字查询状态；也可进入 [有赞云能力包页面](https://diy.youzanyun.com/application/category/package) 查看审核状态。
