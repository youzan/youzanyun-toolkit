# 下单/支付流程 Hook

## 什么时候用

用户提到下单页 `trade-buy`、待支付页 `trade-pay`，并且需要在提交订单、创建订单、支付前后执行校验、弹窗确认、补充字段、埋点或中断流程时，使用本场景。

这类能力的参数和中断契约依赖官方开放文档，必须优先用 `yzy-knowledge-search` 搜精确能力名，例如 `创建订单前触发`。固定链接只作为兜底。

## 能力路由

下单页 `trade-buy`：

| 用户说法 | 建议先搜的能力名 | 常见 this.yz 写法 | 兜底链接 |
| --- | --- | --- | --- |
| 提交订单前触发 | 提交订单前触发 | `this.yz.beforeSubmitOrder` | https://doc.youzanyun.com/v2/doc/client/token/Q48gwjuT7ih8AEkBYjFcKORGnUb |
| 创建订单前触发 | 创建订单前触发 | `this.yz.beforeCreateOrder` | https://doc.youzanyun.com/v2/doc/client/token/XaoswcIL2iudawkMZZYc7oi6n5g |
| 创建订单后触发 | 创建订单后触发 | `this.yz.afterCreateOrder` | https://doc.youzanyun.com/v2/doc/client/token/JQ9uwRZmjiakQjk6juTcRDMKnhc |
| 订单支付后触发 | 订单支付后触发 | `this.yz.afterOrderPay` | https://doc.youzanyun.com/v2/doc/client/token/UuhSwhdmViD7a1kvlQzcFtCGnVg |

待支付页 `trade-pay`：

| 用户说法 | 建议先搜的能力名 | 常见 this.yz 写法 | 兜底链接 |
| --- | --- | --- | --- |
| 订单支付前触发 | 订单支付前触发 | `this.yz.beforeOrderPay` | https://doc.youzanyun.com/v2/doc/client/token/Jilewb3hPiwOsZkilBBcL0DPnTd |
| 订单支付后触发 | 订单支付后触发 | `this.yz.afterOrderPay` | https://doc.youzanyun.com/v2/doc/client/token/UMibwllKAi6LBfkjBtmcAlahn2c |

注意：目标需求到底是“提交订单前”还是“创建订单前”，要以官方知识库和目标页面开放能力配置为准，不要只按方法名相似度判断。

## 页面配置

`app.json`：

```json
{
  "cloudPages": {
    "trade-buy": "pages/trade-buy/index",
    "trade-pay": "pages/trade-pay/index"
  }
}
```

只注册 Hook 不一定需要 Slot；如果还要展示弹窗挂载节点，可以给页面增加一个轻量 Slot 组件。以 `trade-buy` 为例：

```json
[
  {
    "isEnable": true,
    "name": "下单页",
    "cloudSlot": {
      "after-item-info": "slot-components/order-confirm-guard.vue"
    }
  }
]
```

## trade-buy: 创建订单前确认实现模板

在精确能力确认是“创建订单前触发”后，可在页面 `index.js` 中注册：

```js
extendPage({
  created() {
    this.yz.beforeCreateOrder((payload) => {
      yz.console.log("beforeCreateOrder payload", payload);

      return new Promise((resolve, reject) => {
        yz.showModal({
          title: "确认提交订单",
          content: "请确认订单信息无误，继续后将创建订单。",
          showCancel: true,
          success: (res) => {
            if (res && res.confirm) {
              resolve(payload);
              return;
            }

            reject("用户取消创建订单");
          },
          fail: reject,
        });
      });
    });
  },
});
```

如果目标工程没有 `yz.showModal`，消费者端 H5 可使用目标工程已有 UI 库的 Dialog。若已接入 `@youzan-cloud/tee-ui`，可参考下面写法：

```vue
<template>
  <view>
    <t-dialog />
  </view>
</template>

<script>
import { Dialog as TDialog } from "@youzan-cloud/tee-ui";
import Dialog from "@youzan-cloud/tee-ui/dist/dialog/dialog";

export default {
  name: "order-confirm-guard",
  components: {
    "t-dialog": TDialog,
  },
  created() {
    this.yz.beforeSubmitOrder((payload) => {
      return new Promise((resolve, reject) => {
        Dialog.confirm({
          title: "确认提交订单",
          message: "继续后将提交订单，不同意则中断流程。",
          theme: "round-button",
        })
          .then(() => resolve(payload))
          .catch(() => reject("用户取消提交订单"));
      });
    });
  },
};
</script>
```

## trade-pay: 支付前中断实现模板

```js
extendPage({
  created() {
    this.yz.beforeOrderPay((payload) => {
      yz.console.log("beforeOrderPay payload", payload);

      if (!this.canPay(payload)) {
        return Promise.reject("当前订单不满足支付条件");
      }

      return Promise.resolve(payload);
    });
  },
  methods: {
    canPay(payload) {
      // 按业务规则判断，例如支付渠道、订单金额、会员状态等。
      return Boolean(payload);
    },
  },
});
```

## 使用 yzy-knowledge-search 的建议

面向具体需求时，先执行一次精确搜索：

```bash
python3 plugins/youzan-toolkit/skills/yzy-knowledge-search/scripts/search_knowledge.py "创建订单前触发" --top-k 3 --no-navigation --format pretty
```

只有首轮结果为空、明显不相关或报错时，再换成页面加能力名，例如 `trade-buy 创建订单前触发`。不要为了找更多摘要循环搜索。
