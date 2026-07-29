---
name: zancli-pipeline
description: 查询有赞应用构建计划、触发 pipeline 构建、查看构建记录状态与步骤日志。用于用户要求发布、部署、构建、重跑构建、查询 pipeline 状态或日志时；触发构建前必须解析应用上下文并取得对应用、环境、计划和分支的明确确认。
---

# zancli 应用发布

所有 `pipeline` 操作都先使用 `zancli-app-context` 解析目标应用；该 skill 会连带完成 `zancli-bootstrap` 的安装和登录校验。不要直接根据当前目录、应用名或上一轮对话执行发布命令。

## 查询构建计划

先解析应用上下文并向用户展示应用 ID、名称、环境与发布目标：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py
```

使用解析结果中的 `appId`、环境和 zone（如有）查询计划。后续命令继续携带同一组选项，避免目录或默认值改变目标：

```bash
bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline plans --app-id 79782 --env dev --output json
```

用户只关心特定技术栈时才追加 `--type`：

```bash
bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline plans --app-id 79782 --env dev --type CLOUD_JAVA --output json
```

从结果中归纳每个计划的 `planId`、名称、类型，以及最近一次构建的状态、分支和 commit。存在多个计划时，要求用户选择具体计划；不要猜测或选择最近一次成功的计划。

## 触发构建

触发构建是写操作。仅在用户明确确认“应用、环境、计划 ID、分支，以及开始构建”后执行：

1. 以确认的 `appId` 和环境再次解析上下文，使用 `--expected-app-id` 与 `--expected-env` 复核。
2. 指定 `--pipeline-id`。应用存在多个计划时，缺少该参数会返回 `PIPELINE_PLAN_AMBIGUOUS`，不得据此重试或改选计划。
3. 用户指定分支时传入 `--branch`；未指定时，说明将使用当前跟踪的远程分支后再执行。
4. 使用 `--confirm --wait --timeout 15m` 启动并等待终态。

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py \
  --app-id 79782 --env dev --expected-app-id 79782 --expected-env dev

bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline trigger \
  --app-id 79782 --env dev \
  --pipeline-id 326 \
  --branch feat/test-rpm \
  --confirm --wait --timeout 15m \
  --output json
```

构建失败时，命令以非 0 退出并返回 `PIPELINE_RECORD_FAILED`。保留返回的 record ID、失败状态和摘要；不要自动重试、切换分支或触发其他计划。

## 状态、记录与日志

读取状态、历史记录或日志前同样先解析应用上下文，并在命令中继续传递相同的应用选择参数：

```bash
bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline status --record-id 727465 --app-id 79782 --env dev --output json
bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline status --record-id 727465 --app-id 79782 --env dev --wait --interval 10s --timeout 15m --output json
bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline records --pipeline-id 326 --app-id 79782 --env dev --page 1 --page-size 20 --output json
bash <bootstrap-skill-dir>/scripts/ensure_zancli.sh -- \
  zancli pipeline logs --step-id 8891234 --app-id 79782 --env dev --output json
```

`--wait` 会前台轮询至终态。`step-id` 从 `pipeline status` 的步骤列表取得。成功步骤返回 `success:true` 与空日志串是正常行为；只在失败步骤存在外部日志时再据此排查，不要将空日志误报为故障。
