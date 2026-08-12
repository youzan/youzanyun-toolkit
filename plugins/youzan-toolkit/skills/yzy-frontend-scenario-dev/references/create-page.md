# 新增独立页面 createPage

## 快速索引

- 消费者端 H5/小程序独立页面：看“消费者端配置入口”“index.js 实现模板”“page.vue 实现模板”。
- PC 商家端独立页面：看“PC 商家端独立页面”。
- 跳转 URL、生命周期、分享配置或端支持不确定：先用有赞云文档检索工具查 `独立页面 createPage`。

## 什么时候用

使用新增独立页面时，需求需要一个新的页面地址或新的业务流程：

- 新增预下单确认页、活动落地页、表单页、结果页、授权页等。
- 新增 PC 商家后台工具页、配置页、结果页或跳转承接页。
- 页面不是某个已有有赞页面的局部 Slot，也不是保留原链接的整页替换。
- 需要从其他页面跳转过来，并通过 query 传递上下文。

如果用户只是想在已有页面位置加内容，转到 `extend-page.md`；如果要保持原页面链接但内容整体重做，转到 `replace-page.md`。

## 消费者端配置入口

在云工程的 `app.json` 中用 `cloudCustomPages` 声明独立页面。key 是开放页面访问路径，value 是本地实现入口：

```json
{
  "cloudCustomPages": {
    "packages/example-app/pre-order-confirm/index": "custom-pages/pre-order-confirm/index"
  }
}
```

常见文件结构：

```text
cloud/client/src/custom-pages/pre-order-confirm/
├── index.js
└── page.vue
```

落地规则：独立页 UI 优先放在同目录 `page.vue`，这是开放 2.0 工程的约定结构。`createPage` 的 `index.js` 负责页面配置、生命周期和方法注册；不要为了 `render` 额外引入一个新的根组件写法。若目标工程已有脚手架或相邻页面保留 `render` 字段，沿用相邻页面写法即可。

页面跳转时通常先拿开放页面 URL，再用运行时跳转能力打开：

```js
const url = yz.getCustomPageUrl(
  "packages/example-app/pre-order-confirm/index"
);

yz.navigateTo({ url });
```

具体跳转 API 和跨端差异需要用 `yzy-knowledge-search` 查 `独立页面 createPage` 或目标工程现有示例。

## index.js 实现模板

`createPage` 只能在 `index.js` 中调用一次。`index.js` 中优先写页面配置、生命周期和方法；`render` 不作为选择页面根组件文件的依据。新增代码时先看目标工程相邻独立页面：已有 `render` 就保留同类占位写法，没有就不要为了模板强行新增。

```js
createPage({
  config: {
    navigationBarTitleText: "预下单确认",
  },
  created() {
    yz.console.log("pre-order confirm created");
  },
  beforeMount() {
    const query = this.yz.getPageQuery ? this.yz.getPageQuery() : {};
    yz.console.log("pre-order confirm query", query);
  },
  mounted() {},
  destroyed() {},
  methods: {
    confirm() {
      yz.console.log("confirm pre-order");
    },
  }
});
```

## page.vue 实现模板

消费者端 H5 示例优先使用目标工程已有依赖。若目标工程已接入 `@youzan-cloud/tee-ui`，可以保持同类写法。

```vue
<template>
  <view class="pre-order-page">
    <view class="title">预下单确认</view>
    <view class="summary">
      <view class="summary-row">
        <text class="label">商品</text>
        <text class="value">{{ query.title || "未传入" }}</text>
      </view>
      <view class="summary-row">
        <text class="label">数量</text>
        <text class="value">{{ query.num || 1 }}</text>
      </view>
    </view>
    <t-button type="primary" block @click="goBack">确认并返回</t-button>
  </view>
</template>

<script>
import { Button } from "@youzan-cloud/tee-ui";

export default {
  name: "pre-order-confirm-page",
  components: {
    "t-button": Button,
  },
  data() {
    return {
      query: {},
    };
  },
  mounted() {
    this.query = this.yz.getPageQuery ? this.yz.getPageQuery() : {};
  },
  methods: {
    goBack() {
      if (yz.navigateBack) {
        yz.navigateBack();
        return;
      }

      yz.console.log("navigateBack is unavailable in current runtime");
    },
  },
};
</script>

<style>
.pre-order-page {
  box-sizing: border-box;
  min-height: 100vh;
  padding: 16px;
  background: #f7f8fa;
}

.title {
  color: #323233;
  font-size: 20px;
  font-weight: 600;
  line-height: 28px;
}

.summary {
  margin: 16px 0;
  padding: 12px;
  border-radius: 6px;
  background: #fff;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  color: #323233;
  font-size: 14px;
  line-height: 20px;
}

.label {
  color: #969799;
}

.value {
  max-width: 70%;
  text-align: right;
  word-break: break-all;
}
</style>
```

## PC 商家端独立页面

PC 商家端独立页面同样使用 `cloudCustomPages`，常见结构是 `index.js + page.jsx`。落地时优先沿用目标工程相邻 PC 独立页写法和 UI 库。

`app.json`：

```json
{
  "cloudCustomPages": {
    "packages/example-app/order-tool/index": "custom-pages/order-tool/index"
  }
}
```

推荐文件结构：

```text
cloud/admin/src/custom-pages/order-tool/
├── index.js
└── page.jsx
```

`index.js`：

```js
createPage({
  config: {
    navigationBarTitleText: "订单工具",
  },
  created() {
    yz.console.log("pc custom page created");
  },
  beforeMount() {
    const query = this.yz.getPageQuery ? this.yz.getPageQuery() : {};
    yz.console.log("pc custom page query", query);
  },
  methods: {},
  // 若目标工程相邻 PC 独立页保留 render，按相邻写法保留。
  // render: (h) => h(page),
});
```

`page.jsx`：

```jsx
import React from "react";
import { Button, Notify } from "zent";

class OrderToolPage extends React.Component {
  state = {
    query: {},
  };

  componentDidMount() {
    const query = this.yz.getPageQuery ? this.yz.getPageQuery() : {};
    this.setState({ query });
  }

  handleSubmit = () => {
    Notify.success("已提交");
  };

  render() {
    const { query } = this.state;

    return (
      <div style={{ padding: 24 }}>
        <h2 style={{ margin: "0 0 16px" }}>订单工具</h2>
        <div style={{ marginBottom: 16 }}>订单号：{query.orderNo || "未传入"}</div>
        <Button type="primary" onClick={this.handleSubmit}>
          提交
        </Button>
      </div>
    );
  }
}

export default OrderToolPage;
```

跳转到 PC 独立页面时，优先查目标工程相邻页面；没有示例时，用有赞云文档检索工具确认 `getCustomPageUrl` 和当前端跳转方式。

## 官方资料兜底链接

- 独立页面说明：https://doc.youzanyun.com/v2/doc/client/token/Go8VwSl3yisfMPk6V7RchyOgn3e
- 独立页面配置说明：https://doc.youzanyun.com/v2/doc/client/token/EPRsw4I1OiOKqhksaP4cATr7nKd

如果用户需要最新生命周期、分享配置、跳转 API 或端支持，用 `yzy-knowledge-search` 搜 `独立页面 createPage`。
