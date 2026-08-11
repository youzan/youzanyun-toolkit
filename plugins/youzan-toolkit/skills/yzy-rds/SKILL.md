---
name: yzy-rds
description: 查询和操作有赞应用绑定的 RDS 数据库。用于查库、查表、查表结构、DDL 预检查、DML 查询与历史查看时；所有应用级操作前必须先解析应用上下文并使用 zancli 校验登录。不能直接操作线上数据库。
---

# YZY RDS

所有 `rds` 操作都先使用 `yzy-app-context` 解析目标应用；该 skill 会连带完成 `zancli` 的安装和登录校验。不要直接根据当前目录、应用名或上一轮对话执行数据库命令。

`zancli` 安装校验入口同时提供 Python 和 Bash 两种形式。优先尝试 `python3 <plugin-root>/tools/zancli/ensure_zancli.py`；如果当前环境没有可用 Python 但有 Bash，再尝试 `bash <plugin-root>/tools/zancli/ensure_zancli.sh`。

## 注意事项

- `yzy-rds` 只能用于应用绑定数据库的查询、结构查看和受控的预检查，不允许直接操作线上数据库。
- 默认只做只读排查；如果任务目标只是定位问题，优先使用查询、结构查看、日志和链路信息，不要直接改数据。
- 涉及 `prod` 环境、生产表、写操作、DDL、删除、批量更新、清库等动作时，必须先展示应用、环境、数据库、表和语句，并获得开发者明确确认。
- 涉及敏感信息时，输出结果要先脱敏，再给到开发者。
- 如果无法确认应用、环境、数据库或语句的真实目标，必须停下来询问开发者，不能猜测后继续。

## 读取上下文

先解析应用上下文并向用户展示应用 ID、名称、环境与绑定信息：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py
```

用户已指定目标时，完整传递通用选择参数：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py --app-id 79782 --env dev
python3 <app-context-skill-dir>/scripts/resolve_app_context.py --app-name self-container-test --env dev --zone <zone>
```

读取类操作在上下文解析成功后，再透传相同的 `--app-id` 或 `--app-name`、`--env`、`--zone` 到实际 `zancli rds` 命令，防止目标漂移。

## 查库 / 查表 / 查结构

应用只有一个库时可以省略 `--db`，zancli 会自动选中。
应用有多个库时，命令返回 `RDS_DATABASE_AMBIGUOUS` 并列出候选；这时用 `--db` 指定库名。
同名库存在于多个实例时，再加 `--instance` 收窄。
`--instance` 也可以单独用来把候选收窄到单库，从而继续省略 `--db`。

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds db list --app-name self-container-test --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds table list --app-name self-container-test --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds table list --app-name self-container-test --table cobuild --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds table schema --app-name self-container-test --table cobuild_user --output json
```

## DDL

DDL 是写操作。先做预检查，不改动任何东西：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds ddl prepare \
  --app-name self-container-test \
  --table cobuild_user \
  --statement "ALTER TABLE cobuild_user ADD COLUMN nickname VARCHAR(64)" \
  --output json
```

提交 DDL 计划前，必须获得用户对应用、数据库、表、语句和开始执行的明确确认：

```bash
python3 <app-context-skill-dir>/scripts/resolve_app_context.py \
  --app-id 79782 --env dev --expected-app-id 79782 --expected-env dev

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds ddl exec \
  --app-name self-container-test \
  --type alter --table cobuild_user \
  --title "cobuild_user 增加 nickname" \
  --statement "ALTER TABLE cobuild_user ADD COLUMN nickname VARCHAR(64)" \
  --confirm --output json
```

`--type` 取值 `create` | `alter` | `drop`；`--type drop` 时 `--table` 必填。

跟踪计划：

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds ddl status --plan-id 123456 --app-name self-container-test --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds ddl plans --app-name self-container-test --table cobuild_user --output json
```

## DML

DML `exec` 即使是 `SELECT` 也走确认门禁，因为同一个入口可以执行 `UPDATE` / `DELETE`。
不加 `--confirm` 会停在 `Proceed? [y/n]`；`-y` 不是有效选项。
命令末尾不要加分号，分号会被 shell 当成命令分隔符。

```bash
python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds dml exec \
  --app-name self-container-test \
  --statement "select count(1) cnt from cobuild_user" \
  --confirm --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds dml exec \
  --app-name self-container-test \
  --statement "select * from cobuild_user" \
  --limit 100 --confirm --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds dml history --app-name self-container-test --output json

python3 <plugin-root>/tools/zancli/ensure_zancli.py -- \
  zancli rds dml history --app-name self-container-test --table cobuild_user --type SELECT --output json
```

`--limit` 默认 200，对没有自带 `LIMIT` 的语句生效；传 `0` 关闭。
