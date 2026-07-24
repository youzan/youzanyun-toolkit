# Youzan Codex Plugins

有赞内部 Codex 插件市场。Codex marketplace manifest 位于 `.agents/plugins/marketplace.json`，插件源码放在 `plugins/` 下。

## 安装

从 Git 仓库添加 marketplace，使用方不需要提前 `git clone`，但需要本机已有访问该仓库的权限：

```bash
codex plugin marketplace add https://gitlab.qima-inc.com/youzanyun/youzan-toolkit --ref main && codex plugin add youzan-toolkit@youzan
```

如果使用本地路径安装，才需要先把仓库拉到本机：

```bash
git clone https://gitlab.qima-inc.com/youzanyun/youzan-toolkit /path/to/youzan-toolkit
codex plugin marketplace add /path/to/youzan-toolkit && codex plugin add youzan-toolkit@youzan
```

如果本机只配置了 SSH Git 权限，也可以使用：

```bash
codex plugin marketplace add git@gitlab.qima-inc.com:youzanyun/youzan-toolkit.git --ref main && codex plugin add youzan-toolkit@youzan
```

安装后新开一个 Codex task，以便加载新插件中的 skills。

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
