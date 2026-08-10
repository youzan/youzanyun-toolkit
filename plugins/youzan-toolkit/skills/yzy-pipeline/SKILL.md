---
name: yzy-pipeline
description: 查询有赞应用构建计划、触发 pipeline 构建、查看构建记录状态与步骤日志。用于用户要求发布、部署、构建、重跑构建、查询 pipeline 状态或日志时；触发构建前必须解析应用上下文并取得对应用、环境、计划和分支的明确确认。
---

# YZY 应用发布

所有 `pipeline` 操作都先使用 `yzy-app-context` 解析目标应用；该 skill 会连带完成内部 CLI 工具的安装和登录校验。不要直接根据当前目录、应用名或上一轮对话执行发布命令。

## 1. 前置检查

先解析应用上下文，并向用户展示应用 ID、名称、环境、发布目标与已知状态：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py
```

用户明确指定目标时，完整传递选择参数：

```bash
bash <plugin-root>/tools/zancli/app_context.sh --app-id 79782 --env dev
bash <plugin-root>/tools/zancli/app_context.sh --app-name self-container-test --env dev --zone <zone>
```

解析成功后，后续所有 `zancli` 命令继续携带相同的 `--app-id` / `--app-name`、`--env`、`--zone`，避免目标漂移。

## 2. 查询构建计划

先用解析结果查询计划，再根据计划类型筛选。

通用查询：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline plans --app-id <app-id> --env <env> --output json
```

仅当用户只关心特定技术栈时追加 `--type`：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline plans --app-id <app-id> --env <env> --type CLOUD_FRONTEND --output json
```

从结果中归纳每个计划的 `planId`、名称、类型，以及最近一次构建的状态、分支和 commit。存在多个计划时，要求用户选择具体计划；不要猜测或选择最近一次成功的计划。

前端构建发布时，按下面顺序执行：

1. 先解析应用上下文，确认 `appId`、`appName`、`env` 和 `zone`。
2. 用解析结果查询 `CLOUD_FRONTEND` 计划，不要手填或沿用旧的 `planId`。
3. 从查询结果里选出目标计划，并向用户回显 `planId`、名称、最近一次分支和 commit。
4. 只有在用户确认“应用、环境、计划 ID、分支，以及开始构建”后，才进入触发阶段。
5. 触发前再次解析上下文，带上 `--expected-app-id` 和 `--expected-env` 复核。
6. 使用确认过的 `--pipeline-id` 和 `--branch` 执行触发。

## 3. 触发构建

触发构建是写操作。仅在用户明确确认“应用、环境、计划 ID、分支，以及开始构建”后执行：

1. 以确认的 `appId` 和环境再次解析上下文，使用 `--expected-app-id` 与 `--expected-env` 复核。
2. 指定 `--pipeline-id`。应用存在多个计划时，缺少该参数会返回 `PIPELINE_PLAN_AMBIGUOUS`，不得据此重试或改选计划。
3. 用户指定分支时传入 `--branch`；未指定时，说明将使用当前跟踪的远程分支后再执行。
4. 使用 `--confirm --wait --timeout 15m` 启动并等待终态。

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py \
  --app-id 79782 --env dev --expected-app-id 79782 --expected-env dev

bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline trigger \
  --app-id 79782 --env dev \
  --pipeline-id 326 \
  --branch feat/test-rpm \
  --confirm --wait --timeout 15m \
  --output json
```

构建失败时，命令以非 0 退出并返回 `PIPELINE_RECORD_FAILED`。保留返回的 record ID、失败状态和摘要；不要自动重试、切换分支或触发其他计划。

## 4. 状态、记录与日志

读取状态、历史记录或日志前，同样先解析应用上下文，并在命令中继续传递相同的应用选择参数：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline status --record-id 727465 --app-id 79782 --env dev --output json
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline status --record-id 727465 --app-id 79782 --env dev --wait --interval 10s --timeout 15m --output json
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline records --pipeline-id 326 --app-id 79782 --env dev --page 1 --page-size 20 --output json
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli pipeline logs --step-id 8891234 --app-id 79782 --env dev --output json
```

`--wait` 会前台轮询至终态。`step-id` 从 `pipeline status` 的步骤列表取得。成功步骤返回 `success:true` 与空日志串是正常行为；只在失败步骤存在外部日志时再据此排查，不要将空日志误报为故障。
