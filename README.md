# Youzan Codex Plugins

有赞内部 Codex 插件市场。Codex marketplace manifest 位于 `.agents/plugins/marketplace.json`，插件源码放在 `plugins/` 下。

## 安装

选择一种安装方式即可：

- 使用发布版：从 Git 仓库添加 marketplace，不需要提前 `git clone`，但需要本机已有访问该仓库的权限。
- 本地测试：先 clone 本仓库，再运行 `./install.sh` 安装当前工作区内容。

### 发布版安装

HTTPS Git 权限可用时：

```bash
codex plugin marketplace add https://gitlab.qima-inc.com/youzanyun/youzan-toolkit --ref main && codex plugin add youzan-toolkit@youzan
```

如果本机只配置了 SSH Git 权限：

```bash
codex plugin marketplace add git@gitlab.qima-inc.com:youzanyun/youzan-toolkit.git --ref main && codex plugin add youzan-toolkit@youzan
```

### 本地测试安装

用于拉取代码后测试本地插件和 skill 改动：

```bash
git clone https://gitlab.qima-inc.com/youzanyun/youzan-toolkit /path/to/youzan-toolkit
cd /path/to/youzan-toolkit
./install.sh
```

安装后新开一个 Codex task，以便加载新插件中的 skills。需要调用 `zancli` 或访问依赖其登录态的内部能力时，`zancli-bootstrap` skill 会先安装内测版、校验登录态，并在需要时提示用户完成浏览器 OAuth 登录。执行 `pipeline`、`capability`、`log`、`trace` 或 `rds` 应用级操作时，`zancli-app-context` skill 会先解析并校验目标应用；发布和数据库写操作还会要求确认应用与环境。`zancli-pipeline` skill 负责查询构建计划、触发发布和查看构建状态或日志。

也可以在使用插件前手动完成安装和登录：

```bash
curl -fsSL https://download.qima-inc.com/files/ops-assets/zancli/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
zancli --version
zancli login
zancli whoami
```

## 更新

发布方修改 `plugins/youzan-toolkit` 后，运行发布脚本刷新插件版本的 Codex cachebuster，并完成校验：

```bash
./scripts/release_youzan_toolkit.sh
git add marketplace.json plugins scripts README.md
git commit -m "Release youzan-toolkit plugin"
git push
```

使用方刷新 marketplace 并重新安装插件：

```bash
codex plugin marketplace upgrade youzan && codex plugin add youzan-toolkit@youzan
```

如果已 clone 本仓库，也可以使用封装脚本：

```bash
./scripts/upgrade_youzan_toolkit.sh
```

更新后新开一个 Codex task，以便加载新版本的 skills。

> Codex Git marketplace 当前是刷新式更新：`marketplace upgrade` 只刷新 marketplace 快照，`plugin add` 才会从快照安装插件版本。Codex CLI 暂未提供“刷新并重新安装”的单个子命令，所以使用方用 shell `&&` 合成一条命令执行。

## 校验

发布前运行：

```bash
./scripts/validate_plugins.sh
```
