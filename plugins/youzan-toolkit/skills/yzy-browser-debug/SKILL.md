---
name: yzy-browser-debug
description: 调试和验证本地运行的有赞云 H5 或商家端页面。用于 Slot 不渲染、Console 报错、Network 请求或响应异常、DOM 状态、热更新、页面连接，以及通过项目内 yzy-debug 完成修改刷新复验闭环。
---

# YZY 浏览器调试

## 定位项目

找到根目录 `package.json` 中安装 `@youzan-cloud/browser-runtime` 的前端工程，记为 `<ui-root>`。Runtime 是根目录开发工具，不应位于 `cloud/client` 或 `cloud/admin`。

始终调用项目内 CLI：

```bash
yarn --cwd <ui-root> yzy-debug <command>
```

不要全局安装 `yzy-debug`，不要读取或输出 Runtime session token。

## 连接检查

```bash
yarn --cwd <ui-root> yzy-debug status
yarn --cwd <ui-root> yzy-debug targets
```

只有目标页面 `connected` 为 `true` 才继续：

- 找不到会话：启动对应 `yarn dev:*`。
- Runtime 失效：停止旧进程并重新启动 dev。
- 页面未连接：打开目标页面，通过 YZY Browser Developer Tool 连接当前页面。
- 多页面并行：使用 `targets` 确认 H5 和商家端目标，不把最后激活的标签页误当成唯一目标。

## 轻量检查

```bash
yarn --cwd <ui-root> yzy-debug console --level error
yarn --cwd <ui-root> yzy-debug dom --contains <visible-text>
```

轻量模式适合已有 Console、DOM 和基础 Network 元数据，不持续接管 Chrome 调试器。

## 完整 Network 证据

```bash
yarn --cwd <ui-root> yzy-debug capture start
yarn --cwd <ui-root> yzy-debug clear
yarn --cwd <ui-root> yzy-debug reload
yarn --cwd <ui-root> yzy-debug network wait --match <keyword> --timeout 15000
yarn --cwd <ui-root> yzy-debug network --match <keyword> --limit 10
yarn --cwd <ui-root> yzy-debug network show <requestId>
yarn --cwd <ui-root> yzy-debug capture stop
```

检查 method、URL、请求体、响应状态、响应体、耗时、failure 和截断标记。响应体不可用时只报告证据边界，不解释为接口没有返回。完成或中断排查后都执行 `capture stop`。

## 修复闭环

1. 保存修改前 Console、Network 或 DOM 证据。
2. 从证据定位源码并做最小修改。
3. 等待终端编译完成。
4. 执行 `yzy-debug reload`，不要随意刷新并销毁用户尚未采集的现场。
5. 重新读取同类证据并检查新增 Console error。
6. 关闭深度采集。

代码修改或编译通过不等于页面验证通过。

## 操作边界

只允许可逆页面操作：

```bash
yarn --cwd <ui-root> yzy-debug click --text <exact-text>
yarn --cwd <ui-root> yzy-debug fill --selector <css> --value <value>
yarn --cwd <ui-root> yzy-debug press --key <key>
```

禁止提交订单、支付、授权、删除、发布或其他不可逆动作。输出 Network 证据前删除 Cookie、Authorization、token、手机号和地址等敏感数据。
