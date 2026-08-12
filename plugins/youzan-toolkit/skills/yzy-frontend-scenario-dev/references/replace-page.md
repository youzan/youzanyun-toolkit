# 整页替换 cloudReplacePages

## 快速索引

- 消费者端整页替换：看“消费者端配置入口”“index.js 实现模板”“page.vue 实现模板”。
- PC 商家端整页替换：看“PC 商家端整页替换”。
- 目标页面端支持、页面 key 或页面容器接入不确定：先用有赞云文档检索工具查 `整页替换 cloudReplacePages`。

## 什么时候用

使用整页替换时，用户希望保留有赞原页面的入口、URL 和页面身份，但页面内容整体由三方实现：

- 商品详情、会员中心等原页面入口不变，但视觉和结构整体重做。
- PC 商家后台原页面入口不变，但用三方 React/JSX 页面替换整体内容。
- 不是在 Slot 上追加一块内容，也不是新增一个新 URL。
- 需要承接原页面 query、运行时数据和开放 API，再自行渲染完整页面。

如果只是局部增强，转到 `extend-page.md`；如果是新增页面地址，转到 `create-page.md`。

## 消费者端配置入口

在 `app.json` 中用 `cloudReplacePages` 声明整页替换：

```json
{
  "cloudReplacePages": {
    "goods-detail": "replace-pages/goods-detail/index"
  }
}
```

推荐文件结构与独立页面相同：

```text
cloud/client/src/replace-pages/goods-detail/
├── index.js
└── page.vue
```

从开发者视角看，整页替换可以理解为“命中原页面身份 + 用独立页面结构承载实现”。页面实现结构与新增独立页面一致，但入口仍然是被替换的原页面。

## index.js 实现模板

```js
createPage({
  config: {
    navigationBarTitleText: "商品详情",
  },
  created() {
    yz.console.log("replace goods-detail created");

    if (this.yz.beforeBuy) {
      this.yz.beforeBuy((payload) => {
        yz.console.log("replace page beforeBuy", payload);
        return Promise.resolve(payload);
      });
    }
  },
  // 如果目标工程相邻独立页面保留 render，占位写法按相邻页面保持一致。
  // render: (h) => h(page),
});
```

## page.vue 实现模板

```vue
<template>
  <view class="replace-goods-page">
    <image v-if="cover" class="cover" :src="cover" mode="aspectFill" />
    <view class="content">
      <view class="title">{{ goods.title || "商品详情" }}</view>
      <view class="price-row">
        <text class="price">{{ formatAmount(goods.price) }}</text>
        <text v-if="goods.originPrice" class="origin-price">
          {{ formatAmount(goods.originPrice) }}
        </text>
      </view>
      <view class="actions">
        <t-button type="primary" block @click="handleBuy">立即购买</t-button>
      </view>
    </view>
  </view>
</template>

<script>
import { Button } from "@youzan-cloud/tee-ui";

export default {
  name: "replace-goods-detail-page",
  components: {
    "t-button": Button,
  },
  data() {
    return {
      goods: {},
      cover: "",
    };
  },
  dataReady() {
    const { goodsInfo = {} } = this.yz.data || {};
    this.goods = goodsInfo;
    this.cover =
      goodsInfo.picture ||
      goodsInfo.image ||
      (Array.isArray(goodsInfo.images) ? goodsInfo.images[0] : "");
  },
  methods: {
    formatAmount(value) {
      if (value === undefined || value === null || value === "") return "--";

      const amount = Number(value);
      if (!Number.isFinite(amount)) return String(value);

      return `￥${(amount / 100).toFixed(2)}`;
    },
    handleBuy() {
      if (this.yz.beforeBuy) {
        yz.console.log("buy action should follow original page API contract");
      }
    },
  },
};
</script>

<style>
.replace-goods-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.cover {
  display: block;
  width: 100%;
  height: 375px;
  background: #ebedf0;
}

.content {
  padding: 16px;
  background: #fff;
}

.title {
  color: #323233;
  font-size: 18px;
  font-weight: 600;
  line-height: 26px;
}

.price-row {
  display: flex;
  align-items: baseline;
  margin-top: 12px;
}

.price {
  color: #ee0a24;
  font-size: 26px;
  font-weight: 700;
  line-height: 32px;
}

.origin-price {
  margin-left: 8px;
  color: #969799;
  font-size: 13px;
  text-decoration: line-through;
}

.actions {
  margin-top: 20px;
}
</style>
```

## PC 商家端整页替换

PC 商家端整页替换与 PC 独立页面一样采用 `index.js + page.jsx` 的实现结构，但配置入口使用 `cloudReplacePages`，页面 key 是被替换的原页面身份。

`app.json`：

```json
{
  "cloudReplacePages": {
    "order-manage-list": "replace-pages/order-manage/index"
  }
}
```

推荐文件结构：

```text
cloud/admin/src/replace-pages/order-manage/
├── index.js
└── page.jsx
```

`index.js`：

```js
createPage({
  config: {
    navigationBarTitleText: "订单管理",
  },
  created() {
    yz.console.log("pc replace page created");
  },
  beforeMount() {
    const query = this.yz.getPageQuery ? this.yz.getPageQuery() : {};
    yz.console.log("pc replace page query", query);
  },
  methods: {},
  // 若目标工程相邻 PC 独立页保留 render，按相邻写法保留。
  // render: (h) => h(page),
});
```

`page.jsx`：

```jsx
import React from "react";
import { Button } from "zent";

class ReplaceOrderManagePage extends React.Component {
  componentDidMount() {
    yz.console.log("replace order manage page mounted", this.yz.data);
  }

  render() {
    return (
      <div style={{ padding: 24 }}>
        <h2 style={{ margin: "0 0 16px" }}>订单管理</h2>
        <div style={{ marginBottom: 16 }}>这里渲染三方整页内容。</div>
        <Button type="primary">主要操作</Button>
      </div>
    );
  }
}

export default ReplaceOrderManagePage;
```

落地前仍要确认 PC 端公开支持目标页面整页替换、页面 key 正确、原页面已接入开放页面容器；确认不足时先说明缺少的依据，再评估页面定制或独立页面替代方案。

## 边界提醒

- 整页替换对页面结构影响最大，优先确认目标页面是否支持、目标端是否支持、是否有版本限制。
- PC 侧可按整页替换场景处理，但必须通过 `yzy-knowledge-search` 或目标工程能力配置确认目标页面是否公开支持、是否已接入开放页面容器。
- 小程序端支持范围可能与运行时版本有关，回答时不要省略版本边界。

## 官方资料兜底链接

- 整页替换说明：https://doc.youzanyun.com/v2/doc/client/token/Ek8pwu56fisxsSkDvztcAeMdndg

如果用户需要最新端支持、配置字段或示例结构，用 `yzy-knowledge-search` 搜 `整页替换 cloudReplacePages`。
