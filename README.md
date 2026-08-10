# Youzan Codex Plugins

有赞 Codex 插件市场。Marketplace 清单位于 `.agents/plugins/marketplace.json`，插件源码位于 `plugins/`。

对外开发者安装和使用流程见 [Youzanyun Toolkit 对外开发者使用文档](docs/youzan-toolkit-install-usage.md)。

## 能力

### 有赞云开放开发与工程工具

- `yzy-project-bootstrap`：初始化有赞云开放工程和本地开发环境。
- `yzy-frontend-dev`：按开放能力约束开发 H5、小程序和商家端页面。
- `yzy-browser-debug`：通过项目内 `yzy-debug` 读取 Console、Network 和 DOM。
- `yzy-knowledge-search`：检索有赞云文档目录与知识库。
- `yzy-app-context`：解析应用上下文。
- `yzy-pipeline`：查询和触发构建计划。
- `yzy-log-trace`：查询日志和 Trace。
- `yzy-rds`：查询和操作应用绑定的 RDS。
- `yzy-api-capability`：查询开放 API 能力包授权。

## 制品边界

Youzanyun Toolkit 是 AI 开发入口，不承载其他产品源码：

| 制品 | 发布方式 | Toolkit 的职责 |
|---|---|---|
| Codex 插件包 `youzanyun-toolkit` | 本仓库 Git marketplace | 分发 Skills、工具脚本和发布版本信息 |
| `@youzan-cloud/cli` | 内部 npm | 提供有赞云开放工程初始化流程；Toolkit 只记录已验证版本和调用方式 |
| `zancli` | 内部安装脚本 | 提供应用上下文、能力包、发布、日志、Trace、RDS 等内部操作命令；Toolkit 只提供安装校验入口和使用约束 |
| `@youzan-cloud/browser-runtime` | 内部 npm | 提供调试规则，不复制 Runtime 源码 |
| YZY Browser Developer Tool | Chrome 扩展 ZIP/后续扩展市场 | 提供最低版本和下载信息 |
| `cloud-ui-v2` | Git 模板仓库 | 提供工程规范，不复制模板源码 |
| Codex Skills | Codex 插件包内置内容 | 提供 AI 可读取的场景化操作说明 |

当前发布渠道记录在 `plugins/youzan-toolkit/assets/yzy-release.json`。版本清单只描述已验证的组合，不替代 npm dist-tag、内部 CLI 安装渠道、扩展发布系统或 Codex marketplace。

## 安装

使用 Git marketplace 安装，需要本机能够访问本仓库。

HTTPS：

```bash
codex plugin marketplace add https://gitlab.qima-inc.com/youzanyun/youzan-toolkit --ref main
codex plugin add youzanyun-toolkit@youzan
```

SSH：

```bash
codex plugin marketplace add git@gitlab.qima-inc.com:youzanyun/youzan-toolkit.git --ref main
codex plugin add youzanyun-toolkit@youzan
```

本地开发：

```bash
git clone https://gitlab.qima-inc.com/youzanyun/youzan-toolkit /path/to/youzan-toolkit
cd /path/to/youzan-toolkit
./install.sh
```

安装或更新后新开 Codex task，使 Skills 重新加载。

> 当前仓库是内部 Git marketplace。面向外部开发者分发时，需要公开镜像或独立插件分发服务；不能假设外部用户拥有内部 GitLab 权限。

## 更新

发布方修改插件后，在合并到 `master` 前刷新 cachebuster 并校验：

```bash
./scripts/release_youzan_toolkit.sh
git add marketplace.json plugins scripts README.md
git commit -m "Release youzanyun-toolkit plugin"
git push
```

这一步应在功能分支完成，并把刷新后的插件版本、cachebuster 和校验相关变更随 MR 一起提交。合并后，使用方从 `master` 安装或更新时才能拿到新的插件内容。

使用方更新：

```bash
codex plugin marketplace upgrade youzan && codex plugin add youzanyun-toolkit@youzan
```

已 clone 仓库时也可以运行：

```bash
./scripts/upgrade_youzan_toolkit.sh
```

## 校验

```bash
./scripts/validate_plugins.sh
```

校验包含插件 manifest 和每个 Skill 的结构检查。
