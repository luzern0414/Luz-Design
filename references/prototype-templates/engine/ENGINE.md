# 共用引擎契约（ENGINE）

> **参考，不是模板。** 引擎、mini 与 admin 提供的是**机制**，可以整套复用，也可以只取其中一块：页面栈（`go/back/replace/popTo/toTab/jump`）、标签栏与导航栏外壳、配置面板（`K.panel`）、场景与全局项、逻辑面板、弹层（`dialog` + `showModal`）、外观、规格校验与生成器。它们与行业无关。示例里的**页面清单、首页组成、入口、文案、数据**只是某个行业的一种答案（`generic-mini` 是商品商城、`florist-mini` 是带专属页面的垂直电商、`booking-mini` 是到店预约，首页组成各不相同），不是默认值：行业不同，首页的功能、模块和布局就不同，由项目的功能说明（Luz-System 的功能清单与入口表）和行业决定，再用页面范式库（`page_pattern.py plan/check`）选范式。规格里**没有任何必填的页面、模块或入口**，生成器只检查结构与引用关系（页面存在、返回目标存在、标签页不被 `go` 指向、二级页不进标签栏……），不检查行业内容，也不内置“首页应该长这样”的默认。不要因为示例里有购物车和订单就给自己的规格加。

本页是 `mini`（小程序）与 `admin`（后台）两个模板共用的引擎的接口说明。引擎负责外壳、页面栈、配置面板、场景、逻辑面板、弹层、外观；模板（kind）只负责“中间那一块长什么样、怎么画一页”。方案与分工见上一级 `README.md`，职责划线见 `references/ui-ownership.md`：功能规则归 Luz-System，逻辑面板只渲染 System 给的数据，不在这里重写。

引擎文件：`engine/engine.css`、`engine/engine.js`、`engine/shell.template.html`。生成器：`scripts/build_prototype.py`。规格 schema：`schema/prototype.schema.json`。

## 一、总体结构

```
规格 spec.json ──┐
内容模块 content.js ┤→ scripts/build_prototype.py ──→ 单文件 HTML
<kind>/build_kind.py ┘        │
                              ├ 组件库（按用到的编号只带需要的 blocks-*.js 与素材，整体封进 LIB）
                              ├ engine.css / engine.js（本目录）
                              └ <kind> 的 css / js / 中间舞台 HTML
```

生成后的 HTML 的脚本顺序固定：

1. `LIB`：组件库封装（IIFE，里面是 ASSETS、kit.js、taxonomy、core-def、extras、ix.js、blocks1–3、用到的 `blocks-*.js`）。库里的全局名（`CATS`、`THEMES`、`PRODUCTS`、`K`（AD 某些文件里有同名常量）……）全部关在 IIFE 里，**不会**与引擎、模板、内容模块冲突；外面只能通过 `LIB` 拿到下面列的成员。
2. `engine.js`：定义常量 `K`（引擎命名空间）。
3. `<kind>` 的运行时：以 `(function (K, LIB) { … })(K, LIB)` 包裹，里面调用 `K.kind({...})` 注册。
4. `const SPEC = {…规格…}`。
5. 内容模块（可选）：同样包成 `(function (K, LIB) { … })(K, LIB)`，里面调用 `K.content({...})`。
6. `K.boot(SPEC)`。

`LIB` 的成员（生成器写死这份清单）：

| 成员 | 含义 |
|---|---|
| `LIB.BLOCKS` | 已载入的组件定义数组（`id name style fit avoid css html js stage wide bg dom cat`） |
| `LIB.THEMES`、`LIB.themeVars(id, 'light'|'dark')`、`LIB.applyTheme(el, id)`、`LIB.mixc(a, b, t)` | 8 套低饱和主题。`applyTheme` **只写 `data-lt` 属性**（不再写行内样式，行内的浅色值会压住深色）；主题色的浅色与深色两组值写在库的 `[data-lt=…]` 规则里，按元素所在的外观取。引擎对 `#root` 和 `<body>` 下的 `#ptDlg` 都调用它 |
| `LIB.setAppearance(mode, persist)`、`LIB.getAppearance()`、`LIB.isDark(el)`、`LIB.APPEARANCES` | 库的外观开关（`system` / `light` / `dark`）：给 `<html>` 加类 `dark` 或 `light`（同时写同名 `data-theme`），产品区的全部颜色令牌随之换成深色或浅色一套；`isDark` 读元素此刻实际是不是深色 |
| `LIB.ASSETS` | `{icons:{'3d'|'real'|'flat':{名:dataURI}}, prod:[…], bg:{名:dataURI}}`（库素材叠加规格里 `assets.dir` 的素材） |
| `LIB.LINE`、`LIB.sv(name)`、`LIB.lineSvg(name)` | 线性图标（2px 描边）。`sv` 返回宽高 100% 的 svg |
| `LIB.icon(name, style)`、`LIB.tileHTML(name, shape, style)`、`LIB.IC(name)`、`LIB.ICON_STYLES` | 入口图标与图标底 |
| `LIB.setIconStyle(v)` / `LIB.iconStyle` | 切换/读取图标风格（`3d real flat line`） |
| `LIB.critter(i, size)` | 默认卡通动物头像 |
| `LIB.P(i)`、`LIB.prod(i)`、`LIB.priceHTML(p, o)` | 商品图与价格 |
| `LIB.IX` | 组件交互运行时（`IX.init(root)`、`IX.toast(root, msg)`） |
| `LIB.NAMES`、`LIB.ORDER_ROWS` 等示例数据 | 只读 |

## 二、规格 JSON 的共用部分

规格字段的结构以 `schema/prototype.schema.json` 为准；下面按字段说明含义。字段名与 Luz-System 的“界面功能说明”对齐。

| 字段 | 必填 | 含义 |
|---|---|---|
| `schema` | 是 | 固定 `"luz-prototype/1"` |
| `kind` | 是 | `"mini"` 或 `"admin"`，决定用哪个模板 |
| `meta` | 是 | `title`（必填，页头与标签页标题）、`subtitle`、`brand`（品牌名）、`version`、`mark`（页头与标签页图标的 svg 内部图形，32×32 栅格，描边 `currentColor`，不写则用 kind 默认图形） |
| `theme` | 否 | 配置面板各组的**默认值**：`id`（主题色 id，默认 `rose`）、`appearance`（`auto`/`light`/`dark`）、`themes`（可选主题色子集），以及各 kind 自己的组（mini：`header` `bgImage` `iconStyle` `iconTile`；admin：`sidebar`（`light`/`dark`）、`density`（`compact`/`standard`）、`iconStyle`）。键名 = 配置组 id，除 `id`（= 组 `theme`）外 |
| `config` | 否 | `groups`（配置面板里出现哪些组、顺序；默认取 kind 的默认清单）、`extra`（规格自带的额外组，见第五节） |
| `assets` | 否 | `dir`：相对规格文件的素材目录，结构同组件库 `assets/`：`icons/{3d,real,flat}/<名>.webp`、`products/p0..pN.webp`、`bg/<名>.webp`；与库素材合并，同名覆盖，多出的追加 |
| `device` | 否 | 仅 mini：`width`（默认 390）、`height`（默认 800）、`time`（状态栏时间）、`capsule`（默认 true）。**`capsule` 是微信小程序右上角的菜单按钮胶囊，只对小程序有意义**：做小程序留默认；做**手机浏览器网页**（H5、销售在手机上用的网页）一律写 `"capsule": false`，网页里没有这个胶囊，画出来是错的。手机框只是设备框，是不是小程序由项目的前端类型决定，引擎不猜 |
| `pages[]` | 是 | 页面清单，见下。页面有哪些、首页放什么由项目决定，规格不要求任何固定页面 |
| `tabbar[]` | mini 必填 | 标签栏：`id`、`name`、`icon`（`LIB.LINE` 里的名字）、`page`（对应的一级页 id）、`badge`（可选，`K.data` 里的路径，数字大于 0 时显示角标） |
| `nav[]` | admin 必填 | 侧栏菜单：每项 `id`、`name`；带 `page` 的是标签（一级页），**不带 `page` 的是分组节点**（只管展开收起，必须有 `children`，可以多级）；还有 `icon`、`group`（扁平分组标题）、`hidden`、`badge`。引擎的 `K.tabs` 只含带 `page` 的节点 |
| `shell` | 否 | admin 外壳用的数据：`today` `now` `version` `env` `account` `notices` `noticePage` `profilePage` `readonlyRoles` `versionInfo`。生成器把它并进 `data.shell`（同名键以 `data.shell` 为准），`noticePage`、`profilePage` 会检查页面存在 |
| `flows[]` | 否 | 流程：`id`、`name`、`start`（入口页 id）、`steps`（页面 id 顺序，右栏用来画流程条）、`done`（完成后去哪：`origin` 回发起处 / 页面 id）、`note` |
| `rules[]` | 否 | 业务规则分组：`{title, items[]}`，右栏“业务规则” |
| `statuses[]` | 否 | 状态机：`{id, name, tone, trigger, ops, to}`，右栏“状态流转”。`tone` 取 `ok warn danger info mute` |
| `scenes[]` | 否 | 业务场景开关，见第六节 |
| `roles[]` | 否 | 角色：`{id, name, note, deniedGo, deniedLabel, readonly}`，第一个是默认角色。`deniedGo` 是无权限状态下“去登录/去申请”按钮的目标页；`readonly: true` 是只读角色（admin：改数据的动作置灰并写原因） |
| `actions{}` | 否 | 声明式动作表，见第四节 |
| `data{}` | 否 | 演示数据（初始值）。`K.data` 是它的深拷贝，“重置演示数据”会还原 |
| `directory[]` | 否 | 左栏页面目录的分组：`{group, pages[]}`，页面可带进入参数写成 `id:参数`（同一页的不同状态变体）；不写则按所属标签与类型自动分组 |
| `content` | 否 | 内容模块文件名（相对规格文件）；命令行 `--content` 优先 |

### 页面 `pages[]`（共用部分）

| 字段 | 含义 |
|---|---|
| `id` | 页面唯一 id（字母数字与连字符），是 `go()` 的参数与 `#/id` 路由 |
| `name` | 页面名（目录、右栏标题） |
| `type` | `tab` 一级页 / `sub` 二级页 / `sheet` 弹层 / `result` 结果页。后台的居中面板就是 `sheet` 加 `layout: center`（schema 里没有 `panel` 类型） |
| `tab` | 所属标签（mini：`tabbar[].id`；admin：`nav` 的 id）。`tab` 类型的页面必须出现在 `tabbar`/`nav` 里 |
| `roles` | 可见角色 id 列表；当前角色不在其中时该页显示“无权限”状态 |
| `scenes` | 与本页相关的场景 id 列表（场景面板里把它们排在最前） |
| `base` / `baseArg` | 仅弹层页：目录直达时它压在哪一页上（默认所属标签的根页） |
| `maskClose` | 仅弹层页：`false` 时点遮罩或面板外不关闭 |
| `offline` | `true` 表示断网时该页仍可用（默认断网显示“失败·网络不可用”） |
| `links` | 自定义渲染里产生的跳转目标（页面 id 或 `id:参数`），只给生成器做可达性与孤岛检查 |
| `logic` | 本页逻辑，见下 |

内容字段（`blocks`、`custom`、`header`、`footer`……）属于各 kind，见各 kind 的 README。

### 本页逻辑 `pages[].logic`（右栏“本页逻辑”读它）

| 字段 | 对应 System 的 | 渲染到 |
|---|---|---|
| `from` | 进入来源 | “来源”。字符串，或 `{pages:[页面 id], text}`（`pages` 用于可达性检查） |
| `back` | 返回目标 | “返回”。字符串，或 `{to:页面 id|"origin"|"tab", text}` |
| `done` | 流程完成后去哪 | “完成后”。同 `back` |
| `primary` | 本页主操作 | “主操作”（一页一个） |
| `rules[]` | 业务规则 | “业务规则”列表 |
| `states[]` | 页面状态（加载/空/失败/无权限/禁用等） | “状态”列表 |
| `backend[]` | 后台维护项（这页的内容和规则由后台哪里维护） | “后台维护”列表 |
| `actions[]` | 动作表 | “动作”：`{id, label, when, result}`，对应 System 的动作编号、按钮文案、触发/禁用条件、结果 |
| `data[]` | 数据需求 | “数据”列表 |

缺 `from`/`back`/`done`/`primary`/`rules` 之一，生成器的 `--check` 报“缺逻辑字段”（一级页的 `back`、结果页的 `back` 允许写“无”）。引擎还会自动列出本页用到的组件编号与名称（来自 `data-cid`）。

## 三、运行时 API（`K`）

```
K.spec        冻结的规格
K.S           状态：{cfg, tab, stacks, sheet, scene, role, net, view, flowOrigin}
K.cfg         配置值（= K.S.cfg），键是配置组 id
K.data        演示数据（可变；K.reset() 还原）
K.LIB         = LIB
```

### 页面栈

路由语义对应微信小程序的页面路由（微信开放文档“页面路由”）：`go` = navigateTo，`replace` = redirectTo，`back` = navigateBack，`toTab` = switchTab，`jump` = reLaunch。标签栏页面出现在栈里时必为栈底，所以引擎的栈只放二级页和结果页；栈空表示停在标签的一级页。

| 函数 | 微信对应 | 作用 |
|---|---|---|
| `K.go(id, a)` | navigateTo | 压栈并渲染，`a` 是字符串参数。**目标不能是标签栏页面**（报错并提示，返回 false）；目标是 `sheet` 页时等同 `openSheet`。若 `id` 是某个流程的 `start`，记下发起处（压栈前的栈深）到 `S.flowOrigin[流程 id]`。页面栈上限 10 层是**本技能的取值**，不是微信的规定；超过时替换栈顶 |
| `K.replace(id, a)` | redirectTo | 替换栈顶（如支付成功后替换成结果页）。目标同样不能是标签栏页面 |
| `K.back(delta = 1)` | navigateBack | 弹出 `delta` 层并回到来源，`delta` 超过栈深就弹到只剩根页；栈里只有根页时无操作，返回 false 并发出 `back-denied` 事件（kind 此时不画返回键） |
| `K.toTab(id, {keep})` | switchTab | 目标必须是标签栏页面；**默认弹掉所有二级页**（微信 switchTab 的语义）；再点当前标签（栈空时）回到顶部。标签**只**由标签栏/侧栏切换，二级页隐藏标签栏。`keep: true`（或 kind 声明 `keepTabStacks: true`）时各标签保留自己停在的二级页，只有“再点当前标签”才回到它的根页。这不是 bug 而是两种约定：小程序的标签栏只有一级页，对应 switchTab；侧栏菜单式的后台切换不对应 switchTab，要“切换保持各自状态” |
| `K.jump(id, a)` | reLaunch | 左栏目录直达与 `#/id` 路由：销毁所有页面，落到该页所属标签；`sheet` 页先落到它的底页（`page.base`，默认标签根页）再打开 |
| `K.popTo(n)` | — | 把当前栈截到前 n 层 |
| `K.done(flowId)` | — | 流程完成：`popTo(S.flowOrigin[流程 id])`，即回到发起处；流程的 `done` 写了页面 id 时去那里（标签栏页面用 `toTab`）；没有记录时回标签根 |
| `K.openSheet(id, a)` / `K.closeSheet()` | — | 打开/关闭弹层页 |
| `K.cur()` | — | 当前帧 `{id, a, page, tab, depth}` |
| `K.canBack()` | — | 栈里是否有二级页 |

规格校验（生成器）与此对应：`go`、`replace` 的目标不能是标签栏页面；标签栏（`tabbar`/`nav`）里的页面必须是一级页（`type: "tab"`），二级页不能出现在标签栏里。

路由：地址栏 `#/<页面 id>` 或 `#/<页面 id>:<参数>` 与 `K.jump` 等价；导航后引擎用 `history.replaceState` 同步 hash（不增加历史）；`hashchange` 触发直达。

### 渲染钩子

- `K.render({fresh, restore})`：重画屏幕与打开中的弹层，再刷新左右面板。默认保留滚动位置；`fresh` 表示换了页（回到顶部），`fresh + restore` 表示返回或切标签（恢复该页上次的滚动位置）。`K.batch(fn)` 把一次动作里的多次 `render` 合并成一次，轻提示等到画完再弹（`K.act`、点击委托、`K.run` 都已包在里面）。
- **只重画一部分**：`K.render({part: '名'})` 调 kind 的 `renderPart(part, frame, ctx)`，由 kind 自己替换那一块 DOM 并返回被替换的元素；引擎对它做 `mountIn`，并按元素上的 `data-fk` 属性恢复焦点与光标（即输即查的搜索框、表单输入不丢焦点）。批处理里同时有整页渲染时整页优先。`K.keepFocus(fn)` 是同一套焦点恢复，给 kind 自己局部更新时用。kind 没有 `renderPart` 时 `part` 被忽略，退回整页渲染。
- `K.on(evt, fn)` / `K.emit(evt, payload)`：事件 `nav`、`render`、`config`、`scene`、`role`、`net`、`reset`、`sheet`。
- 页面状态 `K.S.view` 取 `ok loading empty fail-network fail-timeout fail-server fail-expired denied disabled`；导航时复位为 `ok`。kind 的 `render` 要处理它（见第七节）。

### 模块显示

`K.modules(page)`（kind 提供 `modules(page) -> [{key, label}]`，mini 把 `header` / `blocks` / `footer` 的每一项当一个模块）、`K.moduleHidden(pageId, key)`、`K.setModule(pageId, key, hidden)`。状态在 `K.S.hidden[页面 id][模块键]`，kind 的 `render` 读 `K.moduleHidden` 跳过被关掉的模块；换页后保留，“重置演示数据”清空。场景面板里的“模块显示”就是这些开关。

### 弹层、对话框、提示

- `K.sheet.open({title, body, foot, layout, label, onClose})`：用原生 `<dialog>` 的 `showModal()`，带 `role="dialog"`、`aria-modal="true"`、`aria-labelledby`；**焦点陷阱**（Tab/Shift+Tab 在对话框内循环，Esc 关闭，关闭后焦点还给打开它的元素）。`layout` 取 `bottom`（底部弹层，高度 ≤80%，底部按钮固定）或 `center`（居中面板）。弹层被裁在 kind 的 `clip` 元素范围内（手机屏幕或后台工作区），遮罩只盖这个范围。
- `K.sheet.close()`。
- **关闭控制**：`K.sheet.open({…, maskClose: false, onBeforeClose(reason)})`，页面弹层写 `maskClose: false`（规格 `pages[].maskClose`）、内容模块的 `sheets[id]` 返回 `onBeforeClose`。`maskClose: false` 时遮罩不带 `data-pt-close`，点遮罩或面板外都不关闭（表单与确认面板用，免得丢已填内容）。用户发起的关闭（Esc、右上角 ×、点遮罩、点面板外、内容里的 `data-pt-close` 按钮）统一走 `K.requestClose(reason)`，先问 `onBeforeClose(reason)`（`reason` 取 `esc` / `click` / `outside`），返回 `false` 就不关；程序里的 `K.closeSheet()` 和导航（`go` `back` `toTab`……）不问，直接关。弹层的 `<dialog>` 元素本身也带 `data-cid`（取面板的 `cid`）。
- `K.confirm({title, text, ok, cancel, danger, maskClose, stack, fields, onOk(values)})`：居中确认框（同样走 `showModal()`）。默认行为不变：已有弹层打开时，确认框**替换**当前弹层的内容。`stack: true` 且已有弹层打开时，确认框**叠在它上面**（第二个 `<dialog id="ptDlg2">`，Esc 先关最上面一层，下面那层保持，焦点陷阱在最上面一层；`data-cid`、主题色、退出动画与第一层一致）。`fields` 是 `[{name, label, type: text|password|textarea|select, required, placeholder, hint, pattern, min, msg, options}]`：必填或格式不通过时不关闭，错误写在字段下面（`aria-invalid="true"` + `.pt-ferr`），通过后先关闭再回调 `onOk(values)`。
- `K.toast(msg, tone)`：轻提示，`tone` 取 `ok info warn danger`；对话框打开时提示画在对话框里。

### 动作与事件（点击委托，写在 HTML 属性里）

组件库自己已经在用 `data-go`、`data-back`、`data-act`、`data-close`、`data-open`、`data-add`、`data-tab`、`data-done` 等属性（一个库文件里就有上百处），所以引擎的属性一律带 `data-pt-` 前缀，避免把库组件内部的按钮当成跳转。规格 `blocks[]` 的覆盖键（`go`、`act`……）不带前缀，挂载后引擎翻译成带前缀的属性。

| 属性 | 含义 |
|---|---|
| `data-pt-go="id[:参数]"` | `K.go` |
| `data-pt-back[=层数]` | `K.back` |
| `data-pt-tab="标签 id"` | `K.toTab` |
| `data-pt-sheet="id[:参数]"` | `K.openSheet` |
| `data-pt-close` | 关闭弹层 |
| `data-pt-done[="流程 id"]` | `K.done` |
| `data-pt-act="名[:参数…]"` | 调动作：先找内容模块的 `acts[名]`，再找规格 `actions[名]`（参数以 `:` 分隔，作为字符串传入） |
| `data-pt-inp="名"` / `data-pt-enter="名"` | 输入框的 `input` 事件 / 回车调用动作，输入值作为最后一个参数 |
| `data-pt-say="文字"` | 轻提示 |
| `data-pt-scene="场景 id:值"` | 切换场景 |
| `data-pt-primary` | 本页主按钮标记（“禁用”状态会把它禁用并说明原因） |

引擎会给所有 `[data-pt-go]`、`[data-pt-tab]` 补上 `data-route="#/…"`，供 `page_pattern.py check-page` 这类审计读目的地。

## 四、声明式动作（规格 `actions`）

`actions` 是 `{名: 步骤数组}`。步骤是单键对象，按顺序执行，遇到 `stop` 或校验失败即中止；有数据变化时执行完统一重画一次。

| 步骤 | 例 | 含义 |
|---|---|---|
| `go` / `replace` / `tab` / `sheet` | `{"go":"detail:3"}` | 导航 |
| `back` / `popTo` / `close` / `done` | `{"done":"order"}` | 返回、截栈、关弹层、完成流程 |
| `toast` | `{"toast":"已加入购物车"}`；`{"toast":{"text":"…","tone":"warn"}}` | 轻提示（文字里可用 `{{路径}}` 引用 `K.data`） |
| `set` | `{"set":{"path":"cart.count","value":0}}` | 写数据 |
| `inc` | `{"inc":{"path":"cart.count","by":1,"max":99}}` | 数据加减 |
| `push` | `{"push":{"path":"orders","value":{…}}}` | 追加到数组头部 |
| `role` | `{"role":"member"}` | 切换角色 |
| `scene` | `{"scene":{"id":"pay","value":"ok"}}` | 设置场景 |
| `branch` | `{"branch":{"scene":"pay","cases":{"ok":[…],"fail-balance":[…]},"default":[…]}}`，也可用 `"path"` | 按场景值或数据值分支 |
| `validate` | `{"validate":[{"sel":"input[type=tel]","required":true,"pattern":"^1\\d{10}$","msg":"请输入 11 位手机号"}]}` | 表单校验：在当前页/弹层里找 `sel`，不通过则给该控件加 `aria-invalid="true"`、弹提示并中止 |
| `net` | `{"net":true}` | 需要网络：断网时提示并中止 |
| `act` | `{"act":"submit"}` | 调内容模块里的动作 |
| `stop` | `{"stop":true}` | 中止 |

`K.get(path)`、`K.set(path, v)`、`K.inc(path, by)`、`K.tpl(text)` 是对应的函数；路径用点号，`orders.0.status` 可取数组项。

## 五、配置面板

配置面板由 `K.panel(opts)` 构造（Luz-Project 的校验器认这个标记）：

```js
K.panel({ mount: element, groups: [组…], cfg: K.cfg, onChange(id, value, cfg) {} }) // 返回 {update()}
```

一个“组”的声明：

| 字段 | 含义 |
|---|---|
| `id` | 组 id，也是 `K.cfg[id]` 的键与 `data-cfg-<id>` 属性名（引擎把每个值同步到 `#root` 的 `data-cfg-<id>`，样式可直接用属性选择器） |
| `title` | 组标题（≥14px） |
| `type` | `swatch`（色板）、`seg`（分段）、`cards`（带缩略图的卡片）、`switch`（开关）、`select` |
| `options` | `[{v, label, hint, swatch, thumb}]`，或返回数组的函数 `(cfg) => […]` |
| `default` | 默认值（`spec.theme[id]` 优先） |
| `cols` | 卡片/分段的列数 |
| `note` | 12px 说明 |
| `when` | `(cfg) => bool`，不满足时整组隐藏（如“背景图”只在头部背景 = 图片时出现） |
| `apply` | `(value, cfg) => void` 副作用（如 `LIB.setIconStyle`） |
| `var` | 把 `option.css || value` 写到 `#root` 的 CSS 变量 |
| `render` | 值变后是否重画屏幕，默认 true |

**引擎内置的组**（kind 可在 `config.groups` 里引用，不必重复声明）：`appearance`（跟随系统/浅色/深色）、`theme`（`LIB.THEMES` 8 套低饱和色，选中时 `LIB.applyTheme('#root')`）、`iconStyle`（3D/真实/扁平/线性，缩略图取库素材）、`iconTile`（圆角方块 `sq`/圆形 `ci`/无底 `no`，写到 `data-cfg-iconTile`，样式由 `.tile-*` 决定）。**kind 自己的组**由 `K.kind({config:[…]})` 提供（mini：`header`、`bgImage`；admin：自行定义，如侧栏深浅、密度）。**规格自带的组**写在 `config.extra[]`，形状同上，只能用 `var`/`attr` 绑定，不含函数。

默认清单：mini = `appearance theme header bgImage iconStyle iconTile`；admin 由 admin 的 `K.kind` 给出。

## 六、场景面板与全局项

左栏“场景”页签自上而下：

1. **本页状态**（引擎内置，作用于当前页，换页复位）：正常 / 加载中 / 空 / 失败·网络不可用 / 失败·请求超时 / 失败·服务繁忙 / 失败·数据已失效 / 无权限 / 禁用。
2. **业务场景**（规格 `scenes[]`）：与当前页相关的（`pages` 含当前页或页面的 `scenes` 含它）排在前面并标“本页”。每个场景：

```json
{ "id": "pay", "label": "支付结果", "pages": ["pay", "result"], "default": "ok",
  "options": [
    {"v": "ok", "label": "成功", "kind": "ok"},
    {"v": "processing", "label": "处理中", "kind": "busy"},
    {"v": "fail-balance", "label": "失败：余额不足", "kind": "fail"} ] }
```

`kind` 取 `ok busy fail loading empty disabled denied`，决定选项前的小标记；每种失败原因各列一项。页面代码用 `K.scene('pay')` 读值，也可用 `data-pt-scene` 或声明式 `scene` 步骤改值。

3. **模块显示**（kind 的 `modules(page)`）：当前页面的每个模块一个开关，关掉就不画这个模块。名字取规格里该模块的 `name`，没有就取 `id`，再没有就用组件编号加组件名（mini：`blocks[]` 项的可选字段 `id`、`name`；同一页内 `id` 不能重复）。
4. **流程直达**（规格 `flows[]`）：点一项跳到该流程的 `start` 页，并从那里计起发起处。
5. **全局**：网络（正常 / 弱网 / 断网）、减少动态（开关）、角色（`roles[]`）、重置演示数据（`K.reset()`：还原 `K.data`、清栈、清场景、角色回默认，配置面板的选择不变）。

网络与角色的效果由引擎统一落到页面状态：断网 → 非 `page.offline===true` 的页面显示“失败·网络不可用”，`net` 步骤会提示并中止；弱网 → 每次切页先显示约 0.9 秒加载骨架；角色不在 `page.roles` 里 → “无权限”。**减少动态**：开关写 `html[data-reduce="1"]`，样式里 `@media (prefers-reduced-motion: reduce)` 与 `html[data-reduce="1"]` 两条分支等价（动画与过渡时长降到近 0，保留最终状态）；初值取系统设置。

页头右侧有“左栏”“右栏”两个折叠按钮（`K.setFold('left'|'right', on)`，`html[data-fold-left|right]`），折叠后舞台变宽；两栏都折叠就是“只看舞台”。kind 可用 `layout(spec) -> {left, right}` 改两栏宽度（写 `--sh-left`、`--sh-right`，外壳的三栏网格读这两个变量）；后台这类流式舞台应该用它，而不是覆盖 `.pt-layout` 的列宽（覆盖会让折叠失效）。

## 七、逻辑面板

右栏三个页签：**本页逻辑**（第二节 `logic` + 流程条 + 本页组件编号）、**业务规则**（`rules[]`）、**状态流转**（`statuses[]`，每行：状态名、触发、可做、去向）。引擎只渲染规格里的数据，不补规则；`logic` 缺项就不显示该行。页面类型标签：`tab`→一级页、`sub`→二级页、`sheet`→弹层、`result`→结果页。

## 八、外观（跟随系统/浅色/深色）

深色是真令牌，不再有滤镜近似。组件库有两套外观，契约是：**给 `<html>`（或组件所在的任意祖先）加类 `dark` 就是深色，加类 `light` 就是浅色，都不加就跟随系统；`data-theme="dark|light"` 与同名类等价；嵌套时最近一层生效**。库的颜色令牌（`--bg --card --ink --line --ok --warn --danger` 等 100 多个，名字见库的 `kit.css`，取值表见库 README 第六节）在深色下整组换掉，所以产品区里凡是用令牌写的颜色都自动跟着变。

引擎怎么接：

- `html[data-appearance]` 取 `auto|light|dark`。`K.setAppearance(mode)` 先调库的 `LIB.setAppearance('system'|'light'|'dark', false)`（给 `<html>` 设类与 `data-theme`，不记 localStorage），再把“跟随系统”按 `matchMedia('(prefers-color-scheme: dark)')` 算成具体的深或浅写回 `html[data-theme]`（系统外观在运行中变化时也跟着重算）。所以 `html` 上永远有明确的 `data-theme="dark|light"`，外壳的 `:root[data-theme="dark"]` 规则与库的 `[data-theme=dark]` 令牌用同一个开关（这个写法 `check_document.py` 才认得是深色主题块）。
- 外壳用自己的两套令牌 `--sh-*`；**外壳变量一律带前缀（`--sh-`、`--mo-`），不与库的令牌重名**（测试会比对 `kit.css`）。引擎与 kind 自己的 CSS 里的产品区颜色一律写库的令牌，不写死颜色，不用 `invert()` 滤镜。
- 库里的深底舞台 `stage:'dark'` 现在渲染成 `.st.night`（因为 `dark` 已经是外观开关）；引擎把组件的深底舞台标成 `data-stage="night"`，用 `var(--night)`。引擎与 kind 不要再拼 `class="… dark"`、`class="… light"`。
- `html[data-dark-mode]` 固定为 `tokens`（kind 的 `darkMode` 字段已无作用，后台模板的样式仍以它为选择器前缀，所以属性保留）。
- 弹层 `#ptDlg` 在 `<body>` 下、不在 `#root` 里：引擎对它也调用 `LIB.applyTheme`，主题色才会进弹层。

测试要求：浅色与深色下每页都能打开且无控制台错误；显式深色、显式浅色、跟随系统（系统深色与系统浅色）三种方式的令牌都对；抽样断言产品区文字对真实底色的对比度（深色下低于 4.5:1 的不超过 2%，最差不低于 3.5:1），浅色保持库原来的取值。

## 九、组件库嵌入与 `data-cid`

- 库是单一来源：`references/component-library/src/`。生成器用**静态索引**把组件编号映射到源文件：扫描 `blocks-*.js` 里的 `id: 'XX-YYY-NNN'`；`blocks1-3.js` 里的旧 52 个编号由 `taxonomy.js` 的 `LEGACY` 表给出，它们总是被带上（并且带上 `blocks-zz-legacy-ix.js`，它给旧编号补交互）。规格里实际用到的编号（`blocks[].cid`、内容模块里 `K.block('…')`/`cids` 声明、kind 要求的编号）决定带哪些 `blocks-*.js`；**整个文件连文件头（图标补丁 `Object.assign(LINE, …)`）一起带**，不拆单个组件。生成器还会扫描内容模块里所有形如 `MP-CARD-001`、`AD-TBL-001` 的字面量，当作该模块用到的编号，不需要另外声明。素材只带库素材 + 规格 `assets` 里的。
- `K.block(cid, ov)` 返回一个带 `data-cid` 的组件根：`<div class="ixr" data-cid="MP-CARD-001" data-id="MP-CARD-001" data-ov="…">…</div>`，并按需注入该组件的 CSS。挂载后引擎统一做三件事：`IX.init(根)`、执行组件自带的 `js(root)`、应用 `ov`（覆盖）。
- **覆盖 `ov`**（在挂载后应用）：键为 `text`、`img`、`go`、`back`、`tab`、`sheet`、`act`、`toast`（= `data-say`）、`attrs`、`hide`、`class`；值是 `{选择器: 值}`。选择器是 CSS 选择器，`@n` 取第 n 个匹配（从 0 起），`@*` 取全部，不写取第一个；`@n` 后面还可以接后代选择器，如 `.row@2 .name` = 第 3 个 `.row` 里的 `.name`；`text` 的选择器以 `!` 结尾表示整体替换元素的文字（默认只替换第一段文字、保留子元素）。`img` 的值：整数 = 库商品图序号；`"bg:名"` = 背景图；其余 = 图片地址或 data URI（`<img>` 改 `src`，其他元素改 `background-image`）。`attrs` 的值是 `{属性: 值}`。`hide` 的值是选择器数组。
- 专属页面的**自定义渲染**里也要用库的组件当积木，并保留 `data-cid`（用 `K.block()`，或者自己的元素上标注最接近的库编号）。
- **`data-cid`**：产品界面里每个控件都必须落在带 `data-cid` 的元素里（`audit_rendered.py --library` 的口径）。kind 自己画的控件（标签栏、导航栏、状态页、提示、弹层）标最接近的库编号（mini：标签栏 `MP-NAV-002`、顶栏 `MP-NAV-001`、弹层 `MP-FB-003`、对话框 `MP-FB-002`、轻提示 `MP-FB-001`、空/失败/无权限 `MP-STATE-001`、骨架 `MP-STATE-002`、断网 `MP-STATE-004`、结果 `MP-STATE-005`）。
- **`data-shell`**：原型外壳的控件（页头、左右面板、配置面板、场景开关、设备状态栏与胶囊）标 `data-shell`，它们不是产品界面，审计脚本忽略。

## 十、kind 运行时接口（`K.kind`）

```js
K.kind({
  id: 'mini',
  tabsKey: 'tabbar',                      // 规格里标签/菜单数组的键
  size(spec) { return {w: 390, h: 800} }, // 舞台固定尺寸；窗口放不下时按比例缩放（transform）。返回 null 表示舞台是流式的（后台），不缩放
  defaultGroups: ['appearance', 'theme'],// 配置面板默认出现的组
  toasts: '#ptToasts',                    // 轻提示容器（舞台里、和 screen 同级，重画屏幕时不会被清掉）
  confirmCid: 'MP-FB-002',                // K.confirm 的 data-cid
  screen: '#ptScreen',                    // 引擎把 render() 的返回值写进它的 innerHTML
  clip: '#ptScreen',                      // 弹层与提示被裁在它的范围内
  typeLabel: {tab: '一级页', sub: '二级页', sheet: '弹层', result: '结果页'},
  config: [组…],                           // kind 自己的配置组（第五节）
  render(frame, ctx) { return html },     // 一页的完整内部 HTML；frame={id,a,page,tab,depth}；ctx={view,cfg,scene,role,net}
  mounted(root, frame, ctx) {},           // innerHTML 写入、IX.init、覆盖应用之后
  sheet(page, a) { return {title, body, foot, layout} },  // 弹层页内容
  modules(page) { return [{key, label}] },                // 可选：本页有哪些可开关的模块（场景面板的“模块显示”）
  renderPart(part, frame, ctx) { return element },        // 可选：只重画一块（K.render({part})），返回被替换的元素
  keepTabStacks: false,                   // 可选：true 时 K.toTab 默认保留各标签的页面栈（侧栏菜单式的后台）
  layout(spec) { return {left: 264, right: 320} },        // 可选：左右栏宽度（像素）；页头有“左栏”“右栏”折叠按钮
  stageMin(spec) { return 406 },                          // 可选：舞台至少要多宽（像素）：手机框 = 设备宽度 + 16，后台 = 964（应用框内宽 ≥ 960 才是完整侧栏）。窗口放不下“舞台 + 两栏”时，右栏、再左栏改成抽屉
  onConfig(id, value) {},                 // 可选：配置值变化
  fit(zoom) {},                           // 可选：舞台缩放后的回调
})
```

kind 画出的可滚动区域要带类名 `pt-scroll`，引擎靠它保存与恢复每页的滚动位置（再点当前标签回到顶部也用它）；弹层与轻提示的容器、`#ptLeft` / `#ptRight` / `#ptStage` / `#ptDlg` 这些 id 由引擎与外壳模板提供，kind 不要占用。

kind 的 `render` 必须处理 `ctx.view`：`loading`（骨架）、`empty`、`fail-*`（带“重试”按钮，重试 = 回到 `ok`，断网时仍失败并提示）、`denied`（说明缺什么角色，给 `roles[].deniedGo` 的按钮）、`disabled`（主按钮禁用并写原因）。

内容模块接口：

```js
K.content({
  css: '…',                                // 内容专属样式（运行时注入 <style>；也可以放在内容模块旁边的 content.css，由生成器内嵌）
  init(data) {},                           // 每次“重置演示数据”后调用，可往 data 里补派生数据
  pages: {名: (frame, ctx) => html},        // 页面 custom 引用；blocks[].custom 引用的片段也放这里
  sheets: {页面 id: (a, ctx) => ({title, body, foot, layout})},
  acts: {名: (...args) => {}},              // data-pt-act 调用
})
```

## 十一、生成器与 kind 的插入点

`scripts/build_prototype.py <spec.json> --out <html> [--content <content.js>] [--check]`：

1. 读规格 → 用 `schema/prototype.schema.json` 校验（装了 `jsonschema` 用它，否则用内置的子集校验器）→ 引擎共用检查（中文报错）：页面 id 唯一；`tabbar`/`nav` 引用的页面存在且是一级页；一级页都在标签栏里；`blocks[].cid` 在库里；所有跳转目标（`go/replace/tab/sheet`、`actions` 里的导航、`flows`、`logic.back/done.to`、`links`、`directory`、`roles.deniedGo`）指向存在的页面；孤岛页面（从标签栏出发到不了）；同一页同一目的地多个入口（复用 `page_pattern.find_duplicates`）；流程引用的页面存在；缺逻辑字段。
2. 加载 `references/prototype-templates/<kind>/build_kind.py`，约定：

```python
TABS_KEY = "tabbar"                  # 规格里标签/菜单数组的键（生成器据此做检查）
def check(spec, ctx) -> list[str]:   # 可选：kind 自己的规格检查（返回中文错误；以 "警告：" 开头的算警告）
def edges(page, spec) -> list:       # 可选：这一页产生、但不在 blocks 覆盖里的跳转（list 行操作、工作台待办、表单 thenNew……）。
    ...                              # 返回目标页面 id（或 "id:参数"）的列表，生成器并进孤岛检查；元素写成 {target, name, dup: True}
                                     # 时还参与“同一页同一目的地多个入口”判定（列表每行的同名操作不要标 dup）
def build(spec, ctx) -> dict:        # 必须
    return {
        "css": "…",                  # kind 样式
        "js": "…",                   # kind 运行时（会被包进 (function (K, LIB) {…})(K, LIB)）
        "stage_html": "…",           # 放进 <main id="ptStage"> 的 HTML
        "cids": ["MP-NAV-002", …],   # kind 运行时要求带上的组件编号
        "head": "",                  # 可选：额外 <head> 内容
    }
```

`ctx` 含 `spec`、`spec_path`、`kind_dir`、`engine_dir`、`library_dir`、`warn(msg)`、`index`（组件编号 → 源文件的静态索引）。

3. 共用的 `engine/shell.template.html` 提供：`<head>`（标题、标签页图标）、`<style>` 槽、页头（品牌图形 + 名称）、三栏骨架（`#ptLeft` / `#ptStage` / `#ptRight`）、`<script>` 槽。槽名：`/*__KIT_CSS__*/ /*__IX_CSS__*/ /*__ENGINE_CSS__*/ /*__KIND_CSS__*/ /*__CONTENT_CSS__*/ /*__STAGE_HTML__*/ /*__LIB_JS__*/ /*__ENGINE_JS__*/ /*__KIND_JS__*/ /*__SPEC_JSON__*/ /*__CONTENT_JS__*/`。
4. 输出默认 `dist/<规格名>.html`（仓库 `.gitignore` 已忽略 `references/**/dist/`，生成物不入库）。

## 十二、引擎自带、kind 不能覆盖的硬要求

- 脚本里要有字面量 `K.panel(`（配置面板构造）；弹层只用原生 `<dialog>` 的 `showModal()` 并带 `role="dialog"` 与焦点陷阱；样式里要有 `@media (prefers-reduced-motion: reduce)`，并且面板里的“减少动态”开关同样生效。
- 场景面板按第六节列全：成功、处理中、每种失败原因、加载、空、禁用、无权限；全局含网络、减少动态、角色、重置演示数据。
- 视觉线（沿用组件库 `src/SPEC.md` §4）：低饱和；一条字体栈；字重只用 400/600/700（700 仅 ≥22px）；不斜体、不加字距；控件图标线性 2px；头像用卡通动物；详情与编辑用居中面板，不用右侧抽屉；文本框聚焦只把 1px 边框加深，不出现蓝色或主色选中框；手机内点击区 ≥44；不用 `transition: all`。外壳左右面板文字不小于 14px（说明可用 12px）。
- 动效：引擎自己的动效时长只用四档 100、150、200、300 毫秒（变量 `--mo-100 --mo-150 --mo-200 --mo-300`），退出取进入的 75%（弹层进入 200 毫秒、退出 150 毫秒：关闭前先加 `.closing` 放退出动画，减少动态时直接关闭）；只动 `transform`、`opacity`、`background-color`，不用 `transition: all`；循环的骨架闪动不算进入退出。**库组件自己的时长不在这套里**（库里有 .15s、.25s、.3s、.4s、1.2s 等写法），这是库的已知差异，见 `mini/README.md`。
- **整个文档只有一个 h1**（外壳页头里的产品名；`check_document.py` 查源码里 `<h1` 的个数，必须是 1）。页面里的标题不是 h1：导航栏标题、弹层标题、状态页标题都是 h2 或 h3。内容模块、组件库、kind 运行时里写的 `<h1 …>…</h1>` 在**生成时**降成 `<h2 data-h1 …>…</h2>`（CSS 里的 `h1` 选择器同步改成 `h2:where([data-h1])`，`:where` 的特异性为 0，层叠结果不变），引擎 CSS 里 `:where(h2[data-h1])` 沿用 h1 的默认字号，所以外观不变；组件的 js 钩子或内容模块运行时才塞进来的 h1，由 `mountIn` 兜底降成同样的 h2。页面栈里同一时刻只有栈顶那一页在 DOM 里，弹层在 `<dialog>` 里，所以任何状态下可见的 h1 都只有外壳那一个。生成器会提示“已降为 h2[data-h1]”并给出个数。
- 最小窗口：窗口宽度不超过 910 时去掉三栏，改为手机在上、面板顺序排在下方；手机宽度（390）下可完整操作，无横向撑破。
- **舞台优先于面板**（嵌在设计文档的 iframe 里约 1050 宽、笔记本 1200、1440 都要成立）：kind 用 `stageMin(spec)` 声明舞台至少多宽，引擎在启动和每次改变窗口大小时按 `窗口宽 − 32 ≥ 左栏 + 右栏 + 舞台下限 + 32` 判断两栏能不能并排。放得下：两栏并排（`data-dock-left/right=inline`），按钮 = 折叠。放不下：先把右栏、再把左栏改成**抽屉**（`data-dock-*=float`，`position: fixed` 浮在舞台上，不占列，默认收起；点页头的“左栏”“右栏”打开，焦点进入抽屉；点遮罩、按 Esc 或再点按钮收起），舞台保持设备框应有的宽度。结果：手机框（390）在 1050 宽时也完整、不压到面板；后台在 1050 与 1440 宽时舞台 ≥ 964，侧栏带名称，不退成图标栏或汉堡按钮。停靠方式变了的那一栏重置折叠（抽屉收起、并排展开），没变的保持用户选的；上下排时折叠与抽屉规则都不生效。设备框也不会比舞台宽：宽度放不下时等比缩小（`fit()` 取高度与舞台宽度里更小的比例）。不写 `stageMin` 的 kind 保持原来的三栏（两栏始终并排）。
- 体积：只内嵌实际用到的 blocks 文件与素材。

## 十三、多个系统怎么共用同一份演示数据

一份文档里常有多个系统（小程序、后台……），它们演示的是同一批对象：同一个商品、同一张订单、同一个会员。机制先不做，约定做法是**把共同的数据放进一个独立的 JSON 文件，由各份规格引用同一个文件**，而不是在每份规格的 `data` 里各抄一遍：

1. 在项目的原型目录里放一个 `shared-data.json`（例如 `{"products": […], "orders": […], "members": […]}`），键名在所有系统里含义一致，字段名按 Luz-System 的数据需求写。
2. 每份规格的 `data` 只写本系统自己的状态（购物车数量、列表筛选、草稿……）；共用的部分由构建前的一步把 `shared-data.json` 合并进去：`data = {…shared, …local}`（本系统的同名键优先）。合并可以是项目里一个几行的脚本，也可以由多系统外壳（`build_prototype_suite.py`）在构建每份规格之前做；生成器本身不改。
3. 各系统读到的是同一份对象，页面上的数字、名称、状态才对得上；状态机（订单状态）的名称与流转也放在共用文件里，两边的 `statuses[]` 从它生成。
4. 系统之间不共享运行时状态：每个原型是独立的单文件，“重置演示数据”只还原本系统的 `K.data`。需要演示“小程序下单、后台看到订单”时，把对应的订单作为共用数据里的一条已存在的记录，而不是靠跨页面通信。

这是写法约定，不是引擎的功能；如果以后要做成机制，入口是生成器在读规格时多读一个 `dataFrom` 字段（文件路径列表）。
