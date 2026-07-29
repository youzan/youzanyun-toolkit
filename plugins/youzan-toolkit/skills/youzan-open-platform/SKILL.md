---
name: youzan-open-platform
description: 查询有赞云开放平台控制台中的当前应用状态。用于核对当前应用已选类目、能力包、API 权限和控制台只读接口返回，不用于解释平台通用规则。
---

# 有赞云开放平台状态查询

## 边界

读取的是当前登录态、当前应用和当前环境的控制台状态。平台规则和开发契约仍使用 `yzy-knowledge-search` 查询。

## 凭证

设置当前浏览器在 `https://diy.youzanyun.com` 下的 Cookie：

```bash
export YOUZAN_OPEN_PLATFORM_COOKIE='your-cookie'
```

Cookie 只保存在当前用户环境中。不要提交、记录或输出 Cookie、sid、token、`acw_tc` 等凭证。

## 查询

从本 Skill 目录执行：

```bash
node scripts/platform.mjs category-packs
node scripts/platform.mjs abilities
```

按 API Key 过滤或查看原始结果：

```bash
node scripts/platform.mjs category-packs --apiKey youzan.shop.basic.get
node scripts/platform.mjs abilities --raw
```

## 结果使用

1. 说明结果所属的登录态、应用和环境。
2. 只归纳控制台实际返回的状态，不扩展成官方规则。
3. Cookie 失效或权限不足时，提示重新登录并更新环境变量。
4. 保留排查所需字段，避免复制整段敏感 JSON。

脚本只访问以下只读接口：

- `/api/apps/search-app-category-capability-pack`
- `/api/apps/get-all-ability`

新增写操作、发布或权限变更前必须单独获得用户授权。
