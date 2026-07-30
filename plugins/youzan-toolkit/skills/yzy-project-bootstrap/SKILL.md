---
name: yzy-project-bootstrap
description: 初始化有赞云开放项目。用于完成项目获取、登录和选择应用、安装 AI Skills、检查浏览器插件、初始化前端开放 2.0 工程、启动 H5/小程序/商家端 dev，或排查项目首次启动流程。
---

# 有赞云项目初始化

## 目标

使用官方 YZY CLI 完成项目获取和本地开发初始化。不要手工拼装应用上下文、复制 Runtime 源码或绕过插件检测。

## 新项目

在计划存放项目的父目录执行：

```bash
npx --yes --registry=http://registry.npm.qima-inc.com @youzan-cloud/cli@beta
```

按终端交互完成登录、团队和应用选择、代码分支选择、保存目录、AI Skills 安装、开发目标初始化与 dev 启动。

不要在初始化完成后重复运行仓库内底层 `yzc` 命令。开发和构建应使用生成仓库根目录 `package.json` 暴露的命令。

## 已有项目

1. 先阅读仓库根目录的 `AGENTS.md`、`README.md` 和 `package.json`。
2. 如果仓库已有前端开放 2.0 目录和脚本，直接使用其 `dev:*` 或 `build:*` 命令。
3. 如果缺少前端开放 2.0 结构，重新运行 YZY CLI，让 CLI 完成兼容初始化；不要手工复制模板目录。
4. 如果仅需继续开发，不要重新 clone 或覆盖已有业务代码。

## 制品边界

读取相对本 Skill 的 `../../assets/yzy-release.json` 获取当前发布渠道和安装地址：

- `@youzan-cloud/cli`：项目初始化入口，独立 npm 包。
- `@youzan-cloud/browser-runtime`：仓库根目录开发依赖，由模板或 CLI 安装并锁定具体版本。
- YZY Browser Developer Tool：独立 Chrome 扩展，不把扩展源码复制到业务仓库。
- `cloud-ui-v2`：前端开放 2.0 模板，不作为 Skill 内容分发。

不要把 Runtime 加入 `cloud/client`、`cloud/admin` 等业务子项目依赖。

## 启动与排错

- 插件未安装或版本过低：使用版本清单中的下载地址安装或更新，再重新运行 CLI。
- dev 等待应用：优先确认 YZY CLI 是否已经生成应用上下文，不要再次手工选择另一个应用。
- H5、消费者端小程序和商家后台需要并行开发时，使用 CLI 或仓库提供的并行启动流程，不要让多个 Runtime 争用同一固定端口。
- 页面未渲染本地代码：使用 `yzy-browser-debug` 检查 Runtime、页面连接和真实浏览器证据。
- 需要开放能力或 Slot 规则：使用 `yzy-frontend-dev` 并先查询 `yzy-knowledge-search`。

## 安全边界

不得输出或提交登录 Cookie、Authorization、应用密钥、Runtime session token。涉及发布、支付、下单、授权、删除等不可逆操作时，停止自动执行并请求用户明确确认。
