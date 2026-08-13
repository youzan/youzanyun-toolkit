# Youzan Codex Plugins

有赞 Codex 插件市场。Codex Git marketplace 清单位于 `.agents/plugins/marketplace.json`，插件源码位于 `plugins/`。

对外开发者安装和使用流程见 [Youzanyun Toolkit 对外开发者使用文档](docs/youzan-toolkit-install-usage.md)。

## 能力

### 有赞云开放开发与工程工具

- `yzy-project-bootstrap`：初始化有赞云开放工程和本地开发环境。
- `yzy-frontend-dev`：按开放能力约束开发 H5、小程序和商家端页面。
- `yzy-frontend-scenario-dev`：识别开放 2.0 前端定制场景并完成最小必要代码落地。
- `yzy-knowledge-search`：结合文档目录导航、知识库和 wiki 搜索查询有赞云开放知识。
- `yzy-browser-debug`：通过项目内 `yzy-debug` 读取 Console、Network 和 DOM。
- `yzy-knowledge-search`：检索有赞云文档目录与知识库。
- `yzy-app-context`：解析应用上下文。
- `yzy-frontend-scenario-dev`：识别开放 2.0 前端定制场景并完成页面定制、独立页面、整页替换和下单/支付 Hook 落地。
- `yzy-pipeline`：查询和触发构建计划。
- `yzy-log-trace`：查询日志和 Trace。
- `yzy-rds`：查询和操作应用绑定的 RDS。
- `yzy-api-capability`：查询、预检和申请开放 API 能力包授权。
- `yzy-app-env`：管理应用环境变量，支持读取、脱敏查看、受控注入子进程，以及在明确授权后创建、更新和删除变量。

## 制品边界

Youzanyun Toolkit 是 AI 开发入口，不承载其他产品源码：

| 制品 | 发布方式 | Toolkit 的职责 |
|---|---|---|
| Codex 插件包 `youzanyun-toolkit` | 本仓库 Git marketplace | 分发 Skills、工具脚本和发布版本信息 |
| `@youzan-cloud/cli` | 内部 npm | 提供有赞云开放工程初始化流程；Toolkit 只记录已验证版本和调用方式 |
| `zancli` | 公网 stable 安装脚本 | 提供应用上下文、能力包、发布、日志、Trace、RDS、环境变量等应用操作命令；Toolkit 负责在使用前安装或升级到 stable 版本，并提供登录校验和使用约束 |
| `@youzan-cloud/browser-runtime` | 内部 npm | 提供调试规则，不复制 Runtime 源码 |
| YZY Browser Developer Tool | Chrome 扩展 ZIP/后续扩展市场 | 提供最低版本和下载信息 |
| `cloud-ui-v2` | Git 模板仓库 | 提供工程规范，不复制模板源码 |
| Codex Skills | Codex 插件包内置内容 | 提供 AI 可读取的场景化操作说明 |

当前发布渠道记录在 `plugins/youzan-toolkit/assets/yzy-release.json`。版本清单描述已验证的组合；`zancli` 会在使用前按公网 stable 渠道强制对齐版本，支持 Linux AMD64、macOS Intel/Apple Silicon 和 Windows AMD64。

## 安装

使用 Git marketplace 安装，需要本机能够访问本仓库。

HTTPS：

```bash
codex plugin marketplace remove youzan
codex plugin marketplace add https://github.com/youzan/youzanyun-toolkit --ref main
codex plugin add youzanyun-toolkit@youzan
```

SSH：

```bash
codex plugin marketplace remove youzan
codex plugin marketplace add git@github.com:youzan/youzanyun-toolkit.git --ref main
codex plugin add youzanyun-toolkit@youzan
```

本地开发：

```bash
git clone https://github.com/youzan/youzanyun-toolkit /path/to/youzanyun-toolkit
cd /path/to/youzanyun-toolkit
./install.sh
```

安装或更新后新开 Codex task，使 Skills 重新加载。

> 如果本机从旧地址安装过名为 `youzan` 的 marketplace，先执行 `codex plugin marketplace remove youzan`，避免继续命中旧缓存。

## 更新

使用方从 marketplace 更新插件：

```bash
codex plugin marketplace upgrade youzan && codex plugin add youzanyun-toolkit@youzan
```

使用方已 clone 本仓库时，也可以在仓库目录运行：

```bash
./scripts/upgrade_youzan_toolkit.sh
```

## 发布正式版

发布方修改插件后，在合并到 `main` 前刷新 cachebuster 并校验：

```bash
./scripts/release_youzan_toolkit.sh
git add .agents plugins scripts README.md docs install.sh
git commit -m "Release youzanyun-toolkit plugin"
git push
```

这一步应在功能分支完成，并把刷新后的插件版本、cachebuster 和校验相关变更随 MR 一起提交。合并后，使用方从 `main` 更新时才能拿到新的插件内容。

## 校验

```bash
./scripts/validate_plugins.sh
```

校验包含插件 manifest 和每个 Skill 的结构检查。
