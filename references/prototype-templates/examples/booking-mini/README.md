# booking-mini：到店预约与会员小程序（示例，行业参考之一）

> 这是**另一个行业的一种答案**，用来和 `generic-mini`（商品商城）、`florist-mini`（垂直电商）对照：**同一套机制长出不同的首页**。这里没有搜索、没有金刚栅格、没有购物车、没有商品交易流程；首页是门店上下文栏 + 入口大卡 + 单列预约服务列表。页面清单和首页组成由项目的功能说明与行业决定，不是从示例继承。

10 个页面，规格全部由库的 MP 组件按编号拼成（SVC、ENT、MEM、MKT、FORM、BTN、STATE），没有内容模块。

## 文件

| 文件 | 作用 |
|---|---|
| `spec.json` | 规格：页面与逻辑、流程、预约规则、预约状态机、场景（预约结果）、声明式动作（含手机号校验）、演示数据 |
| `entrances.json` | 入口表（Luz-System 格式），应用类型 `local-booking` |
| `home-plan.json` | `page_pattern.py plan` 给出的首页方案：门店上下文栏、入口大卡、列表 |

## 重新构建与验证

```
py -X utf8 scripts/build_prototype.py references/prototype-templates/examples/booking-mini/spec.json --out <输出.html>
py -X utf8 scripts/page_pattern.py brief --entrances entrances.json --type local-booking --width 390 --out brief.json
py -X utf8 scripts/page_pattern.py plan --brief brief.json --out home-plan.json
py -X utf8 scripts/page_pattern.py check home-plan.json
py -X utf8 scripts/page_pattern.py check-page <生成物> --hash "#/home" --width 390
```

## 页面与流程

- 一级页：首页、预约（我的预约与核销券码）、我的
- 二级页：选择门店、选择人员与时间、确认预约（手机号校验）、现场取号、会员签到
- 结果页：预约成功、预约失败（原因随“预约结果”场景：时段已约满 / 门店已休息）
- 流程：预约到店（首页服务列表 → 选人员与时间 → 确认 → 成功，完成回到发起处）、现场取号、会员签到

## 首页组成

1. 顶部：当前门店上下文栏（门店、营业状态、距离），点它切换门店，只有这一个门店入口
2. 入口大卡：现场取号、会员签到（并列高频核心入口只有 2–3 个，不凑金刚栅格）
3. 单列预约服务列表：每项一个入口，点进去选人员与时间
4. 没有搜索、没有营销轮播、没有购物车；“我的预约”在标签栏，首页不重复；账户类入口只放“我的”
