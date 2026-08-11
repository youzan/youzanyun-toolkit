---
name: yzy-app-env
description: 管理有赞应用环境变量。用于通过 zancli app env list/get/exec/create/update/delete 读取、脱敏查看、受控注入子进程，以及在明确授权后创建、更新或删除应用环境变量。
---

# YZY 应用环境变量

本 skill 用于读取、注入和变更有赞应用环境变量。所有操作都必须使用 `zancli app env ...`，并先确认当前 `zancli` 可用和已登录。

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py --check
```

`zancli` 安装校验入口同时提供 PowerShell、Python 和 Bash 三种形式。Windows 原生优先尝试 `powershell -ExecutionPolicy Bypass -File <plugin-root>/tools/zancli/ensure_zancli.ps1`；通用环境优先尝试 `python3 <plugin-root>/tools/zancli/ensure_zancli.py`；如果当前环境没有可用 PowerShell/Python 但有 Bash，再尝试 `bash <plugin-root>/tools/zancli/ensure_zancli.sh`。

## 目标与环境

`list`、`get`、`exec`、`create`、`update`、`delete` 都必须显式传入 `--env`；缺失时 CLI 会在网络请求前返回 `APP_CONTEXT_ENVIRONMENT_REQUIRED`。不要默认环境，不要用目录名猜测生产或 QA。

需要应用选择参数时，优先使用用户给出的 `--app-id` 或 `--app-name`。目标不明确时，先使用 `yzy-app-context` 解析应用上下文，再把相同的应用与环境参数传给 `app env` 命令。

示例：

```bash
zancli app env list --app-name self-container-test --env dev
zancli app env list --app-name self-container-test --env dev --output json
```

## 读取与脱敏

默认读取必须依赖 CLI 展示层脱敏。包含 `password`、`secret`、`token`、`auth`、`key`、`cert`、`credential`、`DSN` 或连接 URL 等敏感含义的键，值应显示为 `***`。

单键查询：

```bash
zancli app env get --app-name self-container-test --env prod --key opensdk.clientSecret
```

读取不套用写入键名规则，因此可以查询带下划线、数字等既有键。回答中不要输出敏感变量原值；只说明是否存在、是否脱敏、类型化现象和下一步建议。

## 明文边界

`--unmask` 只允许用于 `get`，且必须有用户明确授权或命令中带 `--confirm`。明文只允许进入文本输出，禁止与 `--output json` 同用。

```bash
zancli app env get --app-name self-container-test --env prod \
  --key opensdk.clientSecret --unmask --confirm
```

不得把明文值写入日志、CI 输出、文档、提交信息或最终回复。若用户要求展示明文，拒绝直接复述，改为说明命令已由 CLI 输出到本地终端或让用户在本机自行查看。

以下命令预期失败，机器可读输出禁止明文：

```bash
zancli app env get --app-name self-container-test --env prod \
  --key opensdk.clientSecret --unmask --confirm --output json
```

## 受控进程注入

`exec` 仅把远端变量注入指定子进程，不修改父 shell，也不由 `zancli` 回显变量值。始终把命令放在 `--` 后：

```bash
zancli app env exec --app-name self-container-test --env dev -- printenv tenant_2E_id
```

键名会转换成合法且无冲突的 shell 变量名，例如 `tenant.id` 转为 `tenant_2E_id`。子进程退出码原样透传；命令无法启动时返回 `127`。不要用 `exec` 运行会批量打印全部环境的命令，除非用户明确需要且已经确认不会泄漏敏感信息。

## 写入规则

`create`、`update`、`delete` 都会通过通用应用变量服务执行真实写操作，必须带 `--confirm`。生产环境只有在用户明确说明已取得写入授权时才能使用 `--env prod`；QA/回归默认使用 `--env dev`。

写入键名仅允许字母与点，最长 128 个字符。`update` 必须显式提供 `--description`，避免无意覆盖已有描述。服务端即使 HTTP 200 返回业务错误，CLI 也应非零退出，并且不会输出 `complete` 或传入值；遇到非零退出不得声称写入成功。

CRUD 示例：

```bash
zancli app env create --app-name self-container-test --env dev \
  --key ops.e2e.example --value test-value-v1 \
  --description 'temporary CRUD test' --confirm

zancli app env update --app-name self-container-test --env dev \
  --key ops.e2e.example --value test-value-v2 \
  --description 'temporary CRUD test updated' --confirm

zancli app env delete --app-name self-container-test --env dev \
  --key ops.e2e.example --confirm
```

## 调试与验证

内部 `--debug` 不采集环境变量读写请求或响应 body，防止 trace 绕过脱敏。验证 CLI 行为时使用：

```bash
go test ./pkg/cmd/app ./pkg/client/typed/environment
go test -tags zancli_internal_debug ./pkg/client/typed/environment -run TestEnvironmentReadsDoNotCaptureSensitiveDebugBodies
```

重点回归：默认脱敏、`--unmask` 确认门槛、显式 `--env`、表格左对齐、debug body 抑制、服务端业务错误非零退出。
