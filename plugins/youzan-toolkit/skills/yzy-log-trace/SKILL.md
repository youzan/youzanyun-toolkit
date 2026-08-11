---
name: yzy-log-trace
description: 查询有赞应用日志与链路追踪。用于搜索日志、统计日志、展开日志上下文、按 traceId 汇总链路排障；所有应用级 log / trace 操作前必须先解析应用上下文并使用 zancli 校验登录。
---

# YZY 日志与链路排障

所有 `log` / `trace` 操作都先使用 `yzy-app-context` 解析目标应用；该 skill 会连带完成 `zancli` 的安装和登录校验。不要直接根据当前目录、应用名或上一轮对话执行日志或链路命令。

## 读取上下文

先解析应用上下文并向用户展示应用 ID、名称、环境、应用类型、发布目标、绑定 addon 与开放能力状态：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py
```

用户已指定目标时，完整传递通用选择参数：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py --app-id 79782 --env prod
python3 <app-context-skill-dir>/scripts/resolve_app_context.py --app-name self-container-test --env prod --zone <zone>
```

上下文解析成功后，实际 `zancli log` / `zancli trace` 命令继续携带相同的 `--app-id` 或 `--app-name`、`--env`、`--zone`，防止目标漂移。

## 搜索日志

最近 6 小时最新 50 条：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log search --app-id 79782 --env prod --since 6h --limit 50 --output json
```

按关键词：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log search --app-id 79782 --env prod --since 1h -q "NullPointer" --output json
```

按级别：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log search --app-id 79782 --env prod --since 6h --level ERROR --output json
```

按 traceId：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log search --app-id 79782 --env prod --since 6h --trace-id 8acbf5d682f3 --output json
```

使用 RFC3339 绝对时间窗：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log search --app-id 79782 --env prod \
  --start 2026-07-28T09:00:00+08:00 --end 2026-07-28T10:00:00+08:00 --output json
```

常用参数：

- `--since`：相对窗口，如 `30m` / `2h`，默认 `1h`
- `--start` / `--end`：RFC3339 绝对窗口
- `-q`：消息关键词
- `--level`
- `--trace-id`
- `--host`
- `--thread`
- `--limit`：`1-100`
- `--direction`：`DESC` 默认 / `ASC`
- `--cursor`：翻页游标

## 计数

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log count --app-id 79782 --env prod --since 168h --output json

bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log count --app-id 79782 --env prod --since 6h --trace-id 8acbf5d682f3 --output json
```

## 展开上下文

从 `search` 结果里取一条日志的定位信息，展开它前后的上下文：

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli log scan \
  --app-id 79782 --env prod \
  --host node-xxx --idc idc-a \
  --timestamp 1784641130000 \
  --position-row-key "<search 结果里的 rowKey>" \
  --forward --limit 10 \
  --output json
```

`--forward` 向后展开，不加则向前；`--include-self` 默认包含锚点那条。

## 按 traceId 汇总

```bash
bash <plugin-root>/tools/zancli/ensure_zancli.sh -- \
  zancli trace get 8acbf5d682f3689149d1a63bfe3a0ae7 \
  --app-id 79782 --env prod --since 6h --output json
```

## 空结果与错误

查不到日志是成功结果。没有命中任何日志时返回 `success:true` 和 `resultState:"EMPTY"`，退出码为 `0`，不是错误。

真正的错误会给稳定错误码：

- `INVALID_ARGUMENT`：参数不对
- `LOG_PERMISSION_DENIED`：无权查该应用
- `LOG_QUERY_TIMEOUT`：查询超时
- `LOG_BACKEND_UNAVAILABLE`：后端不可用
