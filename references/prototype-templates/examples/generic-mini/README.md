# generic-mini：通用商品商城小程序（示例，行业参考之一）

> 这是**某个行业的一种答案**，不是默认值。页面清单、首页组成、入口、文案都只对“百货类商品商城”成立；别的行业的首页功能、模块和布局不同，由项目的功能说明和页面范式库决定。可复用的是机制（引擎与 mini 模板），不是这份页面清单。

由规格 + 组件库编号拼出来，没有内容模块、没有自写 CSS：24 个页面与弹层全部是库的 MP 组件，覆盖 HDR、ENT、CARD、PRC、BTN、NAV、FORM、FB、MKT、GOODS、ORD、MEM、LIST、STATE、CONT 等类别。内容通用（百货商品），图片只用库里的 Imagegen 素材。

## 文件

| 文件 | 作用 |
|---|---|
| `spec.json` | 规格：页面（每页的组件编号与覆盖、来源/返回/完成后/主操作/规则/状态/后台维护）、流程、业务规则、订单状态机、场景、角色、声明式动作、演示数据 |
| `entrances.json` | Luz-System 的入口表格式：首页要承载的功能与去重依据（给页面范式库用） |
| `home-plan.json` | `page_pattern.py plan` 对入口表给出的首页方案，规格里的首页按它排 |

## 重新构建

```
py -X utf8 scripts/build_prototype.py references/prototype-templates/examples/generic-mini/spec.json --out <输出.html>
py -X utf8 scripts/build_prototype.py references/prototype-templates/examples/generic-mini/spec.json --check
```

## 页面（24 个）

- 一级页：首页、分类、购物车、我的
- 浏览：商品列表与搜索结果、商品详情、选择规格（弹层）、搜索无结果、加载失败
- 交易：确认订单、选择优惠券（弹层）、收银台（弹层）、支付成功、支付处理中、支付失败
- 订单与售后：全部订单、订单详情、申请售后
- 账户：收货地址、编辑地址、我的优惠券、消息通知、登录、设置

## 流程（左栏“场景”里的“流程直达”）

浏览到加购（首页入口 → 列表 → 详情 → 规格弹层）、结算到支付（购物车或详情 → 确认订单 → 收银台 → 支付结果 → 回到发起结算的页面）、订单到售后（订单列表 → 订单详情 → 申请售后 → 回到订单详情）、登录（游客被拦截 → 登录 → 回到发起处）。

场景：支付结果（成功、处理中、失败：余额不足 / 超出银行限额 / 支付超时）、搜索结果（有、无、请求失败）、商品库存（有货、库存紧张、已售罄）；角色：会员 / 游客（游客进入需要登录的页面显示无权限并给“去登录”）。

## 首页组成（按页面范式库做）

顶部是搜索栏加门店与配送时效（只有一个定位入口）→ 轮播活动 → 金刚区（6 个高频核心入口：新品、热销、礼品、极速达、同城、礼卡；不放账户类与订单类，也不重复标签栏已有的分类与购物车）→ 限时秒杀 → 商品卡。首屏营销模块不超过 2 个。用 `page_pattern.py` 验证：

```
py -X utf8 scripts/page_pattern.py brief --entrances entrances.json --type ecommerce --width 390 --out brief.json
py -X utf8 scripts/page_pattern.py plan --brief brief.json --out home-plan.json
py -X utf8 scripts/page_pattern.py check home-plan.json
py -X utf8 scripts/page_pattern.py check-page <生成物> --hash "#/home" --width 390
```

## 用到的库组件的边界

库的组件是带自己演示数据的积木：同一页里的商品、价格、订单号来自各组件自带的演示数据，彼此不一定一致（例如购物车里的商品与详情页的商品不是同一件）。这是组件库的性质，不是规格的问题；真实项目里用 `custom` 页面或后台数据替换。
