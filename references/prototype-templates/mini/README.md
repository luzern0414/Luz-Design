# 小程序模板（mini）

> **参考，不是模板。** 这里提供的是**机制**：手机框、状态栏与胶囊、导航栏、标签栏、页面栈、弹层、状态页、头部背景，加上引擎的配置面板、场景、逻辑面板。机制与行业无关，可以整套复用。页面清单、首页组成、入口、文案、数据**不在这里**：它们由项目的功能说明和行业决定，示例（`examples/` 下三份行业各不相同的规格）只是各自行业的一种答案，不是默认值。规格里没有任何必填的页面、模块或入口，也不需要购物车和订单。

共用引擎的接口见 [`engine/ENGINE.md`](../engine/ENGINE.md)；规格结构见 [`schema/prototype.schema.json`](../schema/prototype.schema.json)；生成器是 `scripts/build_prototype.py`。

## 文件

| 文件 | 作用 |
|---|---|
| `stage.html` | 中间舞台：手机框（尺寸来自规格 `device`，默认 390×800）、屏幕、轻提示容器 |
| `mini.css` | 手机框、状态栏与胶囊、导航栏、标签栏、头部背景、状态页、图标底 |
| `mini.js` | 运行时：用 `K.kind({...})` 注册 `render / mounted / sheet` 与配置组 `header`、`bgImage` |
| `build_kind.py` | 生成器插件：`TABS_KEY`、`check(spec, ctx)`、`build(spec, ctx)` |

## 页面类型与页面栈

`type` 取 `tab` 一级页、`sub` 二级页、`sheet` 弹层、`result` 结果页。路由语义对应微信小程序的页面路由：`go` = navigateTo（目标不能是标签栏页面）、`replace` = redirectTo、`back` = navigateBack、`toTab` = switchTab（清空二级页）、`jump` = reLaunch。一级页只出现在标签栏里；二级页隐藏标签栏，左上角返回到来源；流程完成用 `done` 回到发起处。页面栈上限 10 层是本技能的取值。

## 页面字段（mini 专属，共用字段见 ENGINE.md）

| 字段 | 含义 |
|---|---|
| `title` | 导航栏标题，默认取 `name`；可含 `{{arg}}`（进入参数）与 `{{数据路径}}`（页面标题不要重复导航栏上的文字） |
| `noBack` | `true` 时不画导航栏返回键（支付结果这类页面，用页内按钮离开） |
| `scroll` | `false` 时滚动区不滚动、正文铺满，页内自己管滚动（分类页的左右两栏） |
| `nav` | `bar` 实色导航栏（二级页默认）/ `overlay` 透明叠在首屏大图上，下滑变实色 / `none` 没有导航栏（一级页默认）/ `space` 只留出导航栏那一行（让内容躲开右上角的胶囊） |
| `light` | `true` 时状态栏与胶囊用白字（头部是深色背景时）；有 `headerBg` 的页面按“头部背景”配置自动判断 |
| `headerBg` | `true` 时滚动区顶部铺“头部背景”（渐变 / 浅色 / 图片，由配置面板切换） |
| `blocks[]` | 页面正文，一项一个积木，见下 |
| `header[]` | 导航栏下面、不随滚动的区域（吸顶的搜索条、分段控件） |
| `footer[]` | 底部固定区（购买栏、提交栏），在标签栏之上 |
| `custom` + `args` | 整页由内容模块里的渲染函数画（见下） |
| `layout` | 仅弹层：`bottom` 底部弹层（高度不超过 80%，底部按钮固定）/ `center` 居中面板 |
| `maskClose` | 仅弹层：`false` 时点遮罩或面板外不关闭（表单、确认面板，免得丢已填内容） |
| `empty` | “空”状态的配图图标、标题、文案、按钮（`{icon,title,text,button,go}`） |
| `tabbar` | 一级页可写 `false` 隐藏标签栏 |

## 页面内容：`blocks` 与 `custom` 可以混用

`blocks[]` 的每一项是下面四种之一：

- `{"cid": "MP-CARD-001", …覆盖}`：库组件，按编号取。组件是库里的积木和参照写法，挑与你的场景最贴近的，不必每页都用。
- `{"custom": "名", "args": {…}}`：内容模块里的渲染函数，用于库里没有的专属页面或片段。渲染里仍用库的组件当积木，并保留 `data-cid`。
- `{"gap": 12}`：间距。
- `{"heading": "标题"}`：小标题（纯文字，不含控件）。

**覆盖**在组件挂载之后应用，键：`text`（改文字）、`img`（改图片：整数 = 库商品图序号，`"bg:名"` = 背景图，其余 = 地址）、`go`（`id` 或 `id:参数`）、`back`（层数）、`tab`（标签 id）、`sheet`、`act`（命名动作）、`toast`、`attrs`（`{选择器:{属性:值}}`，值为 `null` 移除属性）、`class`、`hide`（选择器数组）。值是 `{选择器: 值}`；选择器是 CSS 选择器，`@n` 取第 n 个匹配（从 0 起）、`@*` 取全部，`@n` 后面还可以接后代选择器（`.row@2 .name`）；`text` 的选择器以 `!` 结尾表示整体替换。

库的组件是带自己演示数据的积木，有的是一整块页面区（购物车、结算栏、地址表单），有的是“几种形态并排”的对照块，拼页面时挑前者，用 `hide` 去掉演示用的切换条（如 `.demo`、`.sg`），用 `text` / `img` 换成你的内容。覆盖不能改组件内部随状态重新生成的节点（比如组件自己重绘的按钮），遇到这种情况换一个组件或写 `custom`。

## 内容模块（可选）

`content.js`（规格 `content` 字段或命令行 `--content` 指定，旁边的同名 `.css` 会一并内嵌）运行在 `(function (K, LIB) {…})(K, LIB)` 里，调用 `K.content({css, init, pages, sheets, acts})`，接口见 ENGINE.md 第十节。内容模块里的行业专属渲染、文案、数据都留在示例目录，不进模板。

## 状态页与全局项

引擎的“本页状态”和全局场景会让 `render` 画出加载（骨架）、空、失败（网络、超时、服务繁忙、数据已失效，带重试）、无权限（按 `roles[].deniedGo` 给去登录按钮）、禁用（主按钮置灰并写原因）。断网时非 `offline` 页面走失败态，弱网时切页先显示骨架。

## 配置组

默认 `appearance theme header bgImage iconStyle iconTile`。`header`（渐变 / 浅色 / 图片）与 `bgImage`（背景图）只作用于声明了 `headerBg` 的页面；`iconTile` 通过 `#root[data-cfg-iconTile]` 作用于库组件里所有 `.tile`。规格 `config.groups` 可以改清单（比如不要头部背景就去掉 `header` 与 `bgImage`），`config.extra` 追加自己的组。

## 深色

深色走真令牌：库组件的颜色全部是令牌，`<html>` 的 `data-theme="dark|light"`（或类 `dark` / `light`，不写就跟随系统）一变，产品区整组换掉，不再有滤镜近似。mini 自己的 CSS 里的颜色也都写库的令牌（`--bg --card --ink --line --warn --danger --hot --veil* --sh*` 等），外壳用 `--sh-*`。头部背景的渐变、浅色、图片三种底也取主题令牌（`--ga --gb --pm --pt`），深色下自动换成深色那一组。写自己的 `custom` 渲染与内容模块 CSS 时同样写令牌，不要写死 `#fff`、`#6B7480` 这类颜色；库自带的迁移脚本 `references/component-library/tools/tokenize_colours.py`（`--src` 指向一个放着 `.css`/`.js` 的目录）可以按同一套规则把写死的颜色改成令牌。库里有意保持原样的例外（白字压在实色底上、二维码白底、深底舞台等）见库 README 第六节。

## 只有一个 h1

整个文档只有外壳页头里的一个 h1（产品名）。mini 画的导航栏标题是 h2，弹层标题、状态页标题是 h3；`custom` 渲染、内容模块、组件库里写的 h1 在生成时自动降成 `<h2 data-h1>`，CSS 里的 `h1` 选择器同步改写，外观不变；运行时才塞进来的 h1 由引擎兜底降级（见 ENGINE.md 第十二节）。所以页面标题写 h1 不会让 `check_document.py` 报“应只有一个 h1”，但写成 h2 更干净。

## 模块显示

场景面板里“模块显示”按页面列出这一页的每个模块（`header[]`、`blocks[]`、`footer[]` 的项，`custom` 整页内容算一个），一个开关一个模块，关掉就不画。名字取该项的 `name`，没有就取 `id`，再没有就用组件编号加组件名。`blocks[]` 的项因此多了两个可选字段：`id`（模块标识，同一页内不能重复）和 `name`（显示名）。它们不影响页面本身，只用来在原型里验证“这页少了某个模块还成不成立”。

## 动效与库的已知差异

mini 自己的动效（弹层进入 200 毫秒、退出 150 毫秒，轻提示 150 毫秒，导航栏变实色 200 毫秒）只用 100、150、200、300 毫秒四档，退出取进入的 75%，不用 `transition: all`，减少动态时直接关闭。**库组件自己的动效时长不在这套里**（库里有 .15s、.25s、.3s、.4s、1.2s 等写法），页面里的组件交互动画与上面的四档不一致，这是库的已知差异，不是模板的问题。

## 生成与检查

```
py -X utf8 scripts/build_prototype.py <规格.json> --out <输出.html> [--content content.js]
py -X utf8 scripts/build_prototype.py <规格.json> --check      只校验不构建
py -X utf8 scripts/test_prototype_mini.py                      测试
```

校验只查结构与引用关系：页面存在、标签栏页面存在且是一级页、`go`/`replace` 不指向标签栏页面、`back`/`done`/`go` 指向存在的页面、孤岛页面、同一页同一目的地多个入口、组件编号在库里、流程引用的页面存在、缺逻辑字段。它不检查行业内容。首页怎么排由页面范式库决定：`py -X utf8 scripts/page_pattern.py brief|plan|check`，生成后用 `page_pattern.py check-page <生成物> --hash "#/home" --width 390` 做渲染检查。

## 示例

| 示例 | 行业 | 首页组成 |
|---|---|---|
| `examples/generic-mini` | 通用商品商城 | 搜索与门店配送在顶部、轮播、金刚区（6 个高频入口）、限时秒杀、商品卡 |
| `examples/florist-mini` | 垂直电商（专属页面走内容模块，行业专属内容只在它自己的目录里） | 见该目录 README |
| `examples/booking-mini` | 到店预约与会员 | 门店上下文栏、入口大卡（现场取号、会员签到）、单列预约服务列表；没有购物车与商品交易 |
