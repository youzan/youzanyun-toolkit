---
name: zancli-bootstrap
description: 安装或校验 zancli 内测版，并在需要时完成浏览器 OAuth 登录。任何需要调用 zancli、访问有赞内部受保护资源、或遇到 UNAUTHENTICATED/登录失效时，必须先使用此 skill。
---

# zancli 环境与登录前置检查

所有调用 `zancli` 的工作都必须先运行本 skill 的 `scripts/ensure_zancli.sh`。不要直接执行 `zancli` 命令，也不要仅根据环境变量或之前的对话判断登录仍然有效。

## 执行方式

需要执行后续命令时，将命令通过检查脚本透传：

```bash
bash <skill-dir>/scripts/ensure_zancli.sh -- zancli <command> [args...]
```

脚本会依次完成：

1. 查找现有 `zancli`；缺失时从受控内测通道安装到 `$HOME/.local/bin/zancli`。
2. 调用 `zancli whoami` 校验登录态。
3. 登录态缺失或失效时，执行 `zancli login` 并等待用户在浏览器完成 OAuth 授权。
4. 再次校验成功后才执行 `--` 后的命令。

只检查环境而不触发安装或登录时，使用：

```bash
bash <skill-dir>/scripts/ensure_zancli.sh --check
```

`--check` 失败时必须停止后续受保护操作，并告知用户需要完成登录；不要尝试绕过认证、复用不明 token，或根据猜测继续执行。

## 失败处理

- 安装、网络、系统架构、完整性校验或目标目录不可写失败时，脚本会非 0 退出；停止后续动作并展示错误。
- OAuth 登录必须由用户在浏览器中完成，不能静默模拟或跳过。
- 任意 `zancli` 命令返回 `UNAUTHENTICATED` 或“登录失效”时，重新运行本脚本，不要直接重试业务命令。
