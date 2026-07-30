---
name: yzy-app-context
description: 在执行有赞应用级发布、能力、日志、链路追踪或 RDS 操作前，解析并校验目标应用上下文。适用于 pipeline、capability、log、trace、rds 命令；不适用于账号或不关联应用的通用命令。
---

# YZY 应用上下文前置检查

执行 `pipeline`、`capability`、`log`、`trace` 或 `rds` 组的任何命令前，必须先运行本 skill 的上下文解析脚本。该脚本会通过 内部 CLI 工具自动完成 `zancli` 安装与登录校验；不要绕过它直接执行应用级命令。

## 解析上下文

在目标应用仓库目录中，优先让 `zancli` 按当前目录推断：

```bash
bash <plugin-root>/tools/zancli/app_context.sh
```

用户已经指定目标时，完整传递通用选择参数：

```bash
bash <plugin-root>/tools/zancli/app_context.sh --app-id 79782 --env dev
bash <plugin-root>/tools/zancli/app_context.sh --app-name self-container-test --env dev --zone <zone>
```

脚本输出 `zancli app context --output json` 的完整 JSON，并至少校验 `appId`、`appName` 和环境。调用后先向用户说明解析到的应用 ID、名称、应用类型、环境、发布目标、绑定 addon 与开放能力状态；不要只依据目录名或用户口述推断。

## 操作规则

- 日志、链路追踪与只读查询：上下文解析成功后，向实际 `zancli` 命令传入相同的 `--app-id` 或 `--app-name`、`--env`、`--zone`，防止当前目录变化导致目标漂移。
- 发布、能力变更、数据库写操作：先展示解析结果，并取得用户对应用和环境的明确确认；随后使用 `--expected-app-id` 和 `--expected-env` 再解析一次，匹配后才执行操作。
- `appId` 或环境不匹配、当前目录无法推断、返回不完整或存在歧义时，停止后续操作，要求用户显式提供 `--app-id` 或 `--app-name` 与 `--env`。
- 账号、登录、帮助等不关联应用的命令无需使用本 skill。

## 确认后的示例

用户确认“对应用 79782 的 dev 环境执行”后：

```bash
bash <plugin-root>/tools/zancli/app_context.sh \
  --app-id 79782 --env dev --expected-app-id 79782 --expected-env dev
```

校验成功后，实际命令必须继续携带相同选择参数。若业务命令返回 `UNAUTHENTICATED` 或“登录失效”，重新运行本 skill，不要直接重试业务命令。
