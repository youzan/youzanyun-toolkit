# 页面定制 extendPage

## 快速索引

- 消费者端商品详情页面定制：看“消费者端配置入口”“页面逻辑实现模板”“price-bar slot 实现模板”“after-price-bar slot 实现模板”。
- PC 商家端页面定制：看“PC 商家端配置入口”“PC extendPage 实现模板”“PC Slot 组件模板”“查询 PC 组件实例”。
- 能力字段、Hook 入参或端支持不确定：先用有赞云文档检索工具查精确能力名。

## 什么时候用

使用页面定制时，目标页面已经由有赞提供，三方只需要局部增强：

- 在既有页面的 Slot 位置插入或替换组件，例如商品详情 `price-bar`、`after-price-bar`。
- 在 PC 商家后台既有页面增加表格列、筛选项、表单附加区、工具栏按钮或说明区。
- 读取页面开放 Data，例如商品详情的 `originPrice`、`title`、`price`。
- 调用页面开放 Method，或注册 Hook/Event，例如商品详情购买前 `this.yz.beforeBuy`、PC 表格渲染前 Hook。
- 需求描述是“在商品详情/下单页/待支付页某个位置加一块内容”“读取页面数据展示”“某个动作前做校验”，而不是新增 URL 或整页重做。

如果需求是新增访问地址，转到 `create-page.md`；如果需求是保留原地址但整页重做，转到 `replace-page.md`。

## 消费者端配置入口

在云工程的 `app.json` 中用 `cloudPages` 声明页面定制：

```json
{
  "cloudPages": {
    "goods-detail": "pages/goods-detail/index"
  }
}
```

在对应页面目录下的 `index.json` 声明 Slot 到组件文件的映射。商品详情价格区域示例：

```json
[
  {
    "isEnable": true,
    "name": "商品详情页",
    "cloudSlot": {
      "price-bar": "slot-components/price-bar.vue",
      "after-price-bar": "slot-components/after-price-bar.vue"
    }
  }
]
```

推荐文件结构：

```text
cloud/client/src/pages/goods-detail/
├── index.js
├── index.json
└── slot-components/
    ├── price-bar.vue
    └── after-price-bar.vue
```

## 页面逻辑实现模板

`index.js` 使用全局 `extendPage`，不需要额外 import。落地时先复用目标页面已有 `extendPage` 结构；若文件不存在，再新增。这里注册购买前 Hook，并在页面数据就绪后读取商品数据。

```js
extendPage({
  created() {
    this.yz.beforeBuy((payload) => {
      yz.console.log("beforeBuy payload", payload);

      // 可以在这里做会员、库存、活动资格等自定义校验。
      // 返回 reject 会中断购买；不需要中断时 resolve 原参数或直接 resolve。
      return Promise.resolve(payload);
    });
  },
  dataReady() {
    const { goodsInfo = {} } = this.yz.data || {};
    const { originPrice, title, price } = goodsInfo;

    yz.console.log("goods detail data", {
      originPrice,
      title,
      price,
    });
  },
});
```

## price-bar slot 实现模板

`price-bar` 更适合替换或强化价格主区域。模板只依赖页面 Data 中的 `originPrice`、`title`、`price`；落地时按目标工程的字段格式、样式规范和组件库调整。

```vue
<template>
  <view class="custom-price-bar">
    <view class="goods-title">{{ goods.title || "商品标题" }}</view>
    <view class="price-row">
      <text class="price">{{ formatAmount(goods.price) }}</text>
      <text v-if="goods.originPrice" class="origin-price">
        {{ formatAmount(goods.originPrice) }}
      </text>
    </view>
    <view class="price-tip">开放 2.0 页面定制价格区</view>
  </view>
</template>

<script>
export default {
  name: "goods-detail-price-bar",
  data() {
    return {
      goods: {},
    };
  },
  dataReady() {
    this.syncGoodsInfo();
  },
  methods: {
    syncGoodsInfo() {
      const { goodsInfo = {} } = this.yz.data || {};

      this.goods = {
        title: goodsInfo.title,
        price: goodsInfo.price,
        originPrice: goodsInfo.originPrice,
      };
    },
    formatAmount(value) {
      if (value === undefined || value === null || value === "") return "--";

      const amount = Number(value);
      if (!Number.isFinite(amount)) return String(value);

      // 若目标页面返回值已是元，按目标工程实际字段格式调整这里。
      return `￥${(amount / 100).toFixed(2)}`;
    },
  },
};
</script>

<style>
.custom-price-bar {
  box-sizing: border-box;
  width: 100%;
  padding: 12px 16px;
  background: #fff7f4;
}

.goods-title {
  color: #323233;
  font-size: 15px;
  line-height: 22px;
}

.price-row {
  display: flex;
  align-items: baseline;
  margin-top: 8px;
}

.price {
  color: #ee0a24;
  font-size: 24px;
  font-weight: 700;
  line-height: 30px;
}

.origin-price {
  margin-left: 8px;
  color: #969799;
  font-size: 13px;
  line-height: 18px;
  text-decoration: line-through;
}

.price-tip {
  margin-top: 6px;
  color: #646566;
  font-size: 12px;
  line-height: 18px;
}
</style>
```

## after-price-bar slot 实现模板

`after-price-bar` 更适合追加说明、权益、活动提示，不建议承载整页主流程。

```vue
<template>
  <view v-if="goods.title" class="after-price-card">
    <text class="after-price-title">专属权益</text>
    <text class="after-price-desc">
      {{ goods.title }} 可参与定制活动，下单前会执行购买校验。
    </text>
  </view>
</template>

<script>
export default {
  name: "goods-detail-after-price-bar",
  data() {
    return {
      goods: {},
    };
  },
  dataReady() {
    const { goodsInfo = {} } = this.yz.data || {};
    this.goods = {
      title: goodsInfo.title,
      price: goodsInfo.price,
      originPrice: goodsInfo.originPrice,
    };
  },
};
</script>

<style>
.after-price-card {
  box-sizing: border-box;
  margin: 8px 12px 0;
  padding: 10px 12px;
  border: 1px solid #ffd6cc;
  border-radius: 6px;
  background: #fff;
}

.after-price-title {
  display: block;
  color: #ee0a24;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
}

.after-price-desc {
  display: block;
  margin-top: 4px;
  color: #646566;
  font-size: 12px;
  line-height: 18px;
}
</style>
```

## PC 商家端配置入口

PC 商家端页面定制同样用 `cloudPages`，开发形态通常是 React/JSX。落地前先读取目标工程 `package.json`、相邻页面和 Slot 组件，确认 UI 库、页面 key、Slot 名和 props。

`app.json`：

```json
{
  "cloudPages": {
    "order-manage-list": "pages/order-manage/index"
  }
}
```

页面目录：

```text
cloud/admin/src/pages/order-manage/
├── index.js
├── index.json
└── slot-components/
    ├── after-order-filter-form.jsx
    └── table-column.jsx
```

`index.json`：

```json
[
  {
    "isEnable": true,
    "name": "订单管理页",
    "cloudSlot": {
      "after-filter": "slot-components/after-order-filter-form.jsx",
      "table-column": "slot-components/table-column.jsx"
    }
  }
]
```

## PC extendPage 实现模板

```js
extendPage({
  created() {
    this.yz.beforeTableRender((payload) => {
      const { columns = [] } = payload || {};

      return Promise.resolve({
        columns: [
          ...columns,
          {
            name: "customRemark",
            title: "定制信息",
            width: 140,
          },
        ],
      });
    });
  },
  dataReady() {
    yz.console.log("pc page data", this.yz.data);
  },
  methods: {},
});
```

## PC Slot 组件模板

表格列 Slot 通常由页面把行数据通过 props 传给组件。具体 props 名称必须以目标页面文档或相邻实现为准。

```jsx
import React from "react";

class TableColumn extends React.Component {
  static name = "TableColumn";

  render() {
    const { data = {} } = this.props;

    return (
      <td
        style={{
          minWidth: 140,
          paddingLeft: 16,
          textAlign: "left",
        }}
      >
        {data.customRemark || "定制内容"}
      </td>
    );
  }
}

export default TableColumn;
```

筛选区、表单附加区或工具栏 Slot 可以渲染普通 React 内容，也可以使用目标工程已有组件库：

```jsx
import React from "react";
import { Button, Notify } from "zent";

class AfterFilter extends React.Component {
  static name = "AfterFilter";

  dataReady() {
    yz.console.log("after-filter data", this.yz.data);
  }

  handleClick = () => {
    Notify.success("已触发定制操作");
  };

  render() {
    return (
      <div style={{ margin: "12px 0" }}>
        <Button onClick={this.handleClick}>定制操作</Button>
      </div>
    );
  }
}

export default AfterFilter;
```

## 查询 PC 组件实例

当页面开放了组件实例，可以先查询实例再注册组件级 Hook 或调用组件方法：

```js
extendPage({
  mounted() {
    this.yz.queryComponentById("table-card").then((tableCard) => {
      if (!tableCard) return;

      tableCard.beforeLogsGet((payload) => {
        yz.console.log("beforeLogsGet payload", payload);
        return Promise.resolve(payload);
      });

      if (tableCard.refreshSkill) {
        tableCard.refreshSkill();
      }
    });
  },
});
```

## 官方资料兜底链接

- 页面定制说明：https://doc.youzanyun.com/v2/doc/client/token/Xpv8wZA5niRQgLk83FfccuvOnxc
- 页面配置说明：https://doc.youzanyun.com/v2/doc/client/token/Jcf0wcJBiiKYwpk9Oy2ceo3cnff
- 商品详情 Data 说明：https://doc.youzanyun.com/v2/doc/client/token/JmRIw9L2aiEYpjkDqrTcahebnue
- 商品详情购买 API 说明：https://doc.youzanyun.com/v2/doc/client/token/Gs2gwzvUsiOQFpkYKHecfmotnzg

如果用户需要最新字段、Hook 入参或端支持，用 `yzy-knowledge-search` 搜 `页面定制 extendPage`、`商品详情 数据 originPrice price title`、`beforeBuy`。
