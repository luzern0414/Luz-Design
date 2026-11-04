# 组件模板库

303 个带固定编号的交互组件：小程序 MP 160 个、后台 AD 143 个。每个组件是一段完整的源码（样式、结构、交互），凭编号取用；库本身是一个单文件 HTML 页面，可以搜索、换主题色、换图标风格、复制编号。

它是 Luz-Design 的参考与取用库，不是框架：没有依赖，没有运行时包。产品原型里用到的组件，写它的编号，从 `src/` 里把对应源码拿走。

- 编号索引（按编号查名称、风格、适合与避免）：[registry/index.md](registry/index.md)
- 开发规范（怎么写一个组件、CSS 规则、`data-ix` 词汇表、质量线）：[src/SPEC.md](src/SPEC.md)
- 注册表条目：`references/component-libraries.json` 里的 `luz-kit`（供 `audit_rendered.py --library luz-kit` 和 Luz-Project 的原型检查读取）
- 原型怎么用它：`references/prototype-templates/README.md`

## 一、目录

```text
references/component-library/
  README.md            本页
  build.py             重新构建单文件库（只读本目录，输出 dist/，不入库）
  src/                 全部源码
    SPEC.md            开发规范
    taxonomy.js        域与类别表、第一代 52 个模板的编号表
    core-def.js        def() / guide() 登记函数、全局取图标与示例图的函数
    core-ui.js         库页面：类别页、搜索、编号索引、复制编号、每个组件根上的 data-cid
    extras.js          线性图标补充、默认头像 critter()、示例数据（姓名、商品、订单行）
    ix.js  ix.css      交互运行时（事件委托）：块的 HTML 只写 data-ix 属性
    kit.js kit.css     主题令牌（8 套低饱和主题，各有浅色与深色两组值）、外观开关 setAppearance、图标、示例商品、组件基础样式；kit.css 里 tokens 区块与 kit.js 里 themes 区块由 tools/tokens.py 生成
    combo.js           “整页组合”页（换槽位看搭配效果）
    lib.template.html  页面骨架，build.py 把各文件塞进它的槽位
    blocks1-3.js       第一代 52 个模板（写法见“已知限制”）
    blocks-*.js        其余组件，按类别分文件，见下表
  assets/              WebP 素材（合计约 0.4 MB）：icons/{3d,real,flat} 各 10 个入口图标，products/p0-p8 商品图，bg/{silk,interior} 背景
  registry/index.md    编号索引（脚本生成并提交，不手改）
  tools/               深色与浅色回归的工具（见“六、深色”）
    tokens.py          令牌表：浅色值、深色值、8 套主题的深色派生；生成 kit.css 与 kit.js 里的令牌区块
    tokenize_colours.py  把写死的颜色改成令牌的迁移脚本与映射规则，也是静态检查的规则与例外清单（KEEP）
    dark_audit.py      深色逐个文本节点、图标、近白面板的对比度审计
    visual_regression.py  浅色逐像素回归：截图、元素尺寸与计算样式、比对与阈值
  dist/                构建产物（git 忽略；dist/_regression/ 放回归截图，不入库）
scripts/
  build_component_library.py   构建库，生成索引
  check_component_library.py   静态完整性检查
  test_component_library.py    测试（含浏览器）
```

### blocks 文件与类别

| 文件 | 类别 | 个数 |
|---|---|---|
| `blocks-mp-basic.js` | MP 的 FORM FB NAV BTN CARD HDR ENT 补充（接在第一代之后） | 28 |
| `blocks-mp-content.js` | MP-CONT LIST STATE，PRC 补充 | 24 |
| `blocks-mp-grow.js` | MP-MKT 补充，MEM SVC | 24 |
| `blocks-mp-trade.js` | MP-GOODS ORD | 32 |
| `blocks-ad-table.js` | AD-TBL FLT | 28 |
| `blocks-ad-form.js` | AD-FORM CTRL | 27 |
| `blocks-ad-viz.js` | AD-DATA CHART | 23 |
| `blocks-ad-shell.js` | AD-NAV FB STATE | 29 |
| `blocks-ad-biz.js` | AD-FLOW MGMT PAGE | 26 |
| `blocks-ad-comm.js` | AD-COMM | 10 |
| `blocks1.js` `blocks2.js` `blocks3.js` | 第一代：MP 的 CARD BTN ENT HDR PRC MKT NAV FORM FB | 52 |
| `blocks-zz-legacy-ix.js` | 给第一代模板挂交互钩子（不含组件） | 0 |

## 二、编号与类别

编号 = `域-类别-三位序号`，如 `MP-CARD-003`、`AD-TBL-001`。一经发出不改、不复用；每个类别的序号从 001 连续排到底，新组件只在自己的类别里顺着往后编。类别表在 `src/taxonomy.js`。

| 域 | 类别（个数） |
|---|---|
| MP 小程序 160 | HDR 头图横幅 8 · ENT 入口与宫格 10 · CARD 卡片 12 · PRC 价格与标签 9 · BTN 按钮 11 · NAV 导航与顶栏 10 · FORM 表单与输入 10 · FB 弹层与反馈 8 · MKT 营销活动 14 · GOODS 商品详情 13 · ORD 购物车与订单 19 · MEM 会员与个人中心 8 · CONT 内容与社区 9 · LIST 列表与筛选 6 · STATE 状态与空态 6 · SVC 服务与预约 7 |
| AD 后台管理 143 | TBL 表格与列表 18 · FLT 筛选与搜索 10 · FORM 表单与输入 11 · CTRL 基础控件 16 · DATA 数据展示 12 · CHART 图表 11 · NAV 导航与页头 13 · FB 弹层与反馈 10 · STATE 状态与结果页 6 · FLOW 流程与协作 9 · COMM 沟通与消息 10 · MGMT 系统管理 8 · PAGE 整页布局 9 |

每个类别都有一张“怎么选”表（`guide('mp', 'CARD', [...])`：场景、推荐的组件、原因），推荐项必须是本类别里真实存在的组件名。

## 三、怎么按编号取用

1. 在 [registry/index.md](registry/index.md) 或构建出来的库页面里选好编号（库页面里点编号即复制，地址栏 `#AD-TBL-001` 直达某个组件）。
2. 找到源码：
   ```text
   grep -n "id: 'AD-TBL-003'" references/component-library/src/blocks-*.js
   ```
   第一代的 52 个模板写法不同（`add('卡片', '标准商品卡', ...)`，编号在 `taxonomy.js` 的 `LEGACY` 里按名称对应），用名称在 `blocks1.js`、`blocks2.js`、`blocks3.js` 里找。
3. 取走从 `def({` 到它收尾 `})` 的整段：`css`（样式）、`html`（结构）、`js`（可选的交互钩子）都在里面。
4. **`blocks-*.js` 的文件头要连同带上。** 每个文件的最上面几段（图标补充 `Object.assign(LINE, {...})`、`B`、`K`、`CSS`、`C`、`cg`、`tag`、`dd`、`ROWS` 这类共用小工具和示例数据）是该文件里各组件共用的，组件的 `html`、`css`、`js` 里直接在用。只拷一个 `def()` 会缺函数。最稳的做法是整个文件头（到第一个 `def(` 之前）加上你要的那几个 `def()` 一起拿；文件整体包在一个块作用域或函数里，局部名字不会和别处冲突。
5. 全局名字来自核心文件，原型里要有（样式连同 `kit.css` 里 tokens 区块的令牌一起带，深色才对）：`def` `guide` `P(i)` `IC(name)` `sv(name)` `ICS()` `critter(i, size)` `LINE` `ASSETS` `NAMES ORDER_ROWS SKUS DEPTS`（`core-def.js`、`kit.js`、`extras.js`）；样式依赖 `kit.css` 的令牌与基础类、`ix.css`；交互依赖 `ix.js`。
6. **块的 CSS 一律以块根类为前缀。** 块根类 = 小写的 `域类别序号`，如 `adtbl001`、`mpgoods004`，每条选择器都以 `.adtbl001 ` 开头，所以一段 CSS 单独拷走也不会串到别的块。文件头的小工具里有的用占位符代表块根：`&` 或 `§` 展开为 `.根类`（`CSS(id, s)`、`C(p, s)`、`K(p, ...)`），拷贝时连小工具一起拿，或者自己把占位符替换成 `.根类`。
7. **`js(root)` 的 `root` 是外层 `.ixr`**，不是块根 `.adtbl001`。库页面（和原型引擎）把每个组件包成 `<div class="ixr" data-id="编号" data-cid="编号">…块 HTML…</div>`，`.ixr` 是 `position:relative` 的块容器，轻提示和弹层挂在它上面；钩子里用 `root.querySelector` 把范围限定在块内。块被重渲染时 DOM 会重建、钩子会重新执行，所以钩子里不要挂全局监听、不要留计时器。
8. 交互分两层：通用的靠 `ix.js` 按 `data-ix` 属性接管（`tabs radio multi toggle stepper carousel acc dd rate like count swipe sort checks pager tree slider steps cal upload search remove`，加 `data-open`/`data-ov` 弹层和 `data-toast` 轻提示，词汇表见 `src/SPEC.md` 第 5 节）；特殊的才写在组件自己的 `js(root)` 里。“选中”一律是 `.on` 类。

### 每个组件根上的 `data-cid`

库页面把每个组件包在 `.ixr` 里，并在这个组件根上写 `data-cid="编号"`。原型里同样：每个组件根都带 `data-cid="编号"`，值就是组件编号。审计用它核对：

```text
py -X utf8 scripts/audit_rendered.py <原型.html> --library luz-kit --min-font 12
```

按钮、表单、表格、对话框等控件必须落在某个带 `data-cid` 的组件根里，否则报“自造控件”；“组件种类”按不同的 `data-cid` 个数计（`--min-components`，默认 6）。原型外壳（配置面板、逻辑面板）标 `data-shell`，落在里面的元素不算自造控件，也不计入种类。注册表里 `luz-kit` 的 `prefix`（`mpcard`、`adtbl` 等）是组件根类的前缀，Luz-Project 的原型检查按“类名以前缀开头”数库的组件种类，所以根类必须是 `域类别序号` 的写法。

## 四、重新构建与检查

全部命令在仓库根目录运行（Windows 用 `py -X utf8`）。

| 做什么 | 命令 |
|---|---|
| 构建完整库 | `py -X utf8 scripts/build_component_library.py`，输出 `references/component-library/dist/component-library.html`（约 2.4 MB，单文件，素材内联）；`--out FILE` 改位置 |
| 只构建某几个文件 | `py -X utf8 scripts/build_component_library.py --files blocks-ad-comm.js --out %TEMP%\small.html`（第一代 52 个模板总是带上；要它们的交互钩子再加 `blocks-zz-legacy-ix.js`） |
| 生成编号索引 | `py -X utf8 scripts/build_component_library.py --index`（写 `registry/index.md`）；`--index --check` 只比对，不一致就退出码 1 |
| 静态完整性检查 | `py -X utf8 scripts/check_component_library.py`（通过时打印 `component library: ok`）；`--stats` 看统计 |
| 测试 | `py -X utf8 scripts/test_component_library.py`（静态、索引、构建，加浏览器测试，约 2 分钟，其中深色全库对比度约 1 分钟；没有 playwright 或 Microsoft Edge 时浏览器部分跳过）。浅色回归另需基线：先用改动前的构建 `tools/visual_regression.py capture` 存一份，再 `LIB_REGRESSION_BASE=<目录> py -X utf8 scripts/test_component_library.py BuiltLibraryTests.test_the_light_appearance_is_unchanged_against_the_baseline` |
| 令牌与深色 | `py -X utf8 references/component-library/tools/tokens.py`（打印令牌表与对比度；`--write` 重新生成 kit.css 与 kit.js 的令牌区块，`--check` 核对）；`py -X utf8 references/component-library/tools/dark_audit.py --html <库页面>`（深色全库对比度） |
| 注册表与审计 | `py -X utf8 scripts/test_component_libraries.py`，`py -X utf8 scripts/test_audit_rendered.py` |

### 静态检查查什么（`check_component_library.py`）

不开浏览器，用一个小的 JavaScript 词法分析读源码：

- 编号：格式 `域-类别-三位序号`；全库唯一；类别码在 `taxonomy.js`；每个类别从 001 连续（有原因的空号才能列进脚本里的 `KNOWN_GAPS`，现在没有）。
- CSS：每条选择器都以块根类开头（禁止裸写 `.on`、`.btn`）；没有 `position:fixed`、没有 `transition:all`；十六进制色值的 HSV 饱和度不超过 0.80（亮度太低的深褐不算鲜艳；主题令牌与 SPEC 里的固定状态色放行；现状 0 处）。
- 颜色是令牌：写死的白与灰的背景、边框、阴影、svg 填充，灰色与近黑的文字色，状态色及其浅底，`rgba(31,35,41,.x)`，用 `--pd` 或 `--p` 当文字色，用状态文字色当底，都报错，给出编号、行号和该写的令牌；白字 `color:#fff`、纯黑阴影、彩色点缀色和 `tools/tokenize_colours.py` 里 `KEEP` 的例外放行（现状 0 处）。组件不能把 `dark`、`light` 当类名（它们是外观开关）。
- 字段：`name` 不超过 12 个汉字、`style` 不超过 6 个、`fit` 与 `avoid` 非空、`kw` 至少 5 个词；同一类别不重名。
- “怎么选”：每个类别都有 `guide`，3 到 10 行，每行三格都填，推荐的组件名是本类别里真实存在的名字。

浏览器测试另外在运行时核对：303 个组件、每个类别在 1500 与 390 宽度下渲染且每个组件根带 `data-cid`、页面无横向撑破、8 个主题色与 4 种图标风格依次切换无报错、每个块的 CSS 在真实样式表里都以块根类开头、每个组件按它带的控件种类点一遍并断言状态变化、控制台零错误；深色：303 个组件的每个可见文本节点与图标对比度（桌面与手机，8 套主题，跟随系统与类两种触发）、没有大面积近白面板、外观开关的契约（系统、类、`data-theme`、嵌套、主题色跟着外观、记住选择）。

## 五、怎么新增组件

1. 选类别，按类别里最后一个编号顺着往后编（`registry/index.md` 看现有最大号）。新类别要同时改 `taxonomy.js` 的 `CATS`、`component-libraries.json` 里 `luz-kit` 的 `prefix`，并更新 `test_component_library.py` 里的总数。
2. 写进该类别所在的 `blocks-*.js`（见上表），或新建一个 `blocks-<名称>.js`（构建会按文件名顺序全部载入，文件整体包在一个块作用域或函数里，图标补充放文件顶部、图标名加你的前缀）。**不要改核心文件的行为**（`taxonomy.js` 除外：只加类别）。
3. 用 `def({ id, name, style, fit, avoid, kw, css, html, js })` 登记，写法、CSS 规则、交互词汇表、后台与小程序专项规则都在 [src/SPEC.md](src/SPEC.md)。颜色一律写令牌（“六、深色”末尾有怎么选）。
4. 在该类别的 `guide(...)` 里加一行，推荐项用组件的真实名字。
5. 跑检查与测试：`check_component_library.py`、`build_component_library.py --index`（更新并提交索引）、`test_component_library.py`。
6. 在 1500 与 390 宽度、8 个主题色、4 种图标风格、浅色与深色两种外观下看过，交互每个都点过。

## 六、深色

库有两套外观：浅色是默认，设计与验收的基准；深色是第二套配色，取 `themes.json` 的 `shared.dark` 与各主题 `dark` 映射的取值思路（同色相、明度按对比度目标求解），不是把浅色取反。浅色与改造前逐像素一致（见“浅色回归”）。

### 开关契约（给原型模板和任何嵌入方）

一句话：**给 `<html>`（或组件所在的任意祖先）加类 `dark` 就是深色，加类 `light` 就是浅色，都不加就跟随系统；也可以调用 `setAppearance('system'|'light'|'dark')`。**

| 写法 | 效果 |
|---|---|
| 没有类，系统是深色 | 深色（`@media (prefers-color-scheme: dark)`，在没有 `light` 类时生效） |
| `<html class="dark">` 或舞台容器 `<div class="dark">` | 这个元素以内是深色 |
| `<html class="light">` 或容器 `<div class="light">` | 强制浅色，系统是深色也不变 |
| `data-theme="dark"` / `data-theme="light"` | 与同名类等价（原型引擎现在写的就是 `html[data-theme]`，不用改） |
| 嵌套 | 颜色令牌：离元素最近的一层 `dark` / `light` 生效。主题色（带 `data-lt` 的元素）：同样看最近一层，只有 `light` 在外、`dark` 在中间、`data-lt` 在最里面这一种写法，浅色那份优先（不要这样嵌） |
| `color-scheme` | 同步声明：深色块里是 `dark`（表单控件、滚动条、系统色一起变），浅色块里是 `light` |

`kit.js` 里的对外函数：

- `setAppearance(mode, persist = true)`：给 `<html>` 设类与 `data-theme`（`system` 时两者都去掉），把选择记到 `localStorage['luz-theme']`（读写包 try，`persist=false` 不记），并发出 `appearancechange` 事件；返回生效的 mode。`getAppearance()` 读当前的 mode。`isDark(el)` 读某个元素此刻实际是不是深色。三个函数都挂在 `window` 上。
- `applyTheme(el, id)`：签名不变，**只写 `data-lt` 属性**，不再写行内样式（行内的浅色值会压住深色）。主题色的两组值写在 `kit.css` 的 `[data-lt=…]` 里，按这个元素所在的外观取浅色或深色。`themeVars(id, 'light'|'dark')` 返回对应那一组变量（含新增的 `--p-text`、`--p-fg`）。
- 库页面的工具栏有“外观：跟随系统 / 浅色 / 深色”三选一，选择记在本机，页面加载前先读（不闪）。
- 舞台类型 `stage: 'dark'`（深底舞台，只有两个第一代模板用）现在渲染成 `.st.night`，因为类名 `dark` 已是外观开关。**原型引擎自己拼 `class="st dark"` 的要改成 `night`**；组件源码里不要把 `dark`、`light` 当类名（静态检查会报）。

### 令牌与取值（摘要）

浅色值就是组件原来写死的值；深色值在 `kit.css` 的“tokens”区块里，**由 `tools/tokens.py` 生成**，改值改它再运行 `--write`，不要手改。深色底是蓝灰（不用纯黑）：页面底 `#0D1116`，卡片面 `#191D24`，浮起的面比卡片面依次亮 5%、8%、11%（`--card2 --card3 --card4`，对应 `themes.json` 的 `surfaceMix`）。

| 令牌 | 浅色 | 深色 | 用在 |
|---|---|---|---|
| `--bg` | `#F5F6F8` | `#0D1116` | 页面底、舞台 |
| `--card` | `#FFFFFF` | `#191D24` | 卡片面、输入框 |
| `--card2` `--card3` `--card4` | 白 | `#24282F` `#2B2F36` `#32363C` | 悬浮卡、下拉与弹层、对话框 |
| `--paper` | 白 | `#F2F4F7` | 刻意保持白的面（二维码） |
| `--lift` | 白 | `#36393F` | 软底轨道里选中的那一块（分段控件） |
| `--soft` `--n3` … `--n12` | `#F2F3F5` `#F5F6F8` … `#98A0AA` | 卡片面混入 6.5% … 52% 的白 | 填充、边线、轨道；12 阶，按浅色下的灰选最近的 |
| `--line` `--line2` | `#EEF0F3` `#E6E8EC` | `#2B2F36` `#36393F` | 分隔线、边框 |
| `--ink` | `#1F2329` | `#E7EAEE`（不是纯白，对填充面 11:1） | 正文 |
| `--ink1` … `--ink7` | `#3B424C` … `#C4C9D0` | `#CFD4DA` … `#75797E`（对 `--n4` 填充面：`--ink1` 9:1，`--ink2` 7:1，`--ink3` 6:1，`--ink4` 5.2:1，`--ink5` 4.6:1，`--ink6` 3.4:1，`--ink7` 3.1:1；后两阶给不可用的字） | 逐级变浅的文字 |
| `--ok` `--warn` `--danger` | `#3F7D58` `#8A5A00` `#A8433B` | `#7EBE95` `#DBA760` `#FF9285`（较浅一阶，在各层深色面与自己的浅底上 ≥ 5.6:1） | 状态文字与图标 |
| `--ok-bg` `--warn-bg` `--danger-bg` | `#EAF3EE` `#F7EEDB` `#F8ECEA` | `#152C1E` `#32230F` `#381F1C`（低亮度同色相） | 状态浅底 |
| `--ok-fill` `--warn-fill` `--danger-fill` `--price-fill` | 同文字色 | 同色相，白字 4.6:1 | 载白字的实色底 |
| `--neutral` `--neutral-bg` | `#6A727D` `#F2F3F5` | `#A3A8AE`、`--soft` 的深色值 | 中性状态 |
| `--price` | `#B8443C` | `#FF8E81` | 价格字 |
| `--sh04` … `--sh28` | `rgba(31,35,41,.04…)` | 黑，不透明度约三倍（上限 .6） | 阴影的颜色（形状留在组件里） |
| `--veil04` … `--veil12`、`--mask` `--mask2`、`--glass` `--glass0` `--glass2`、`--hi` `--hi2`、`--scrim` | 墨色或白的半透明 | 白的半透明、黑、卡片面的半透明 | 半透明填充、遮罩、磨砂、内高光 |
| `--inv` `--inv-a` | `#1F2329` | 卡片面混 20% 白 | 轻提示、气泡这类载白字的反色面 |
| `--ph` | `#EDE7E4` | `#332C29` | 商品图加载前的占位底 |
| `--off` | `#D5D9DF` | `#75797E`（对 `--soft` 3.2:1） | 不可用的图形（空星） |
| `--p` `--pd` `--pt` `--pm` `--ga` `--gb` `--p-rgb` | 8 套主题的浅色值 | 见下表 | 主题色（`--p` 配白字） |
| `--p-text`（浅色 = `--pd`） `--p-fg`（浅色 = `--p`） | 深一阶、主色 | 较浅一阶，在深色面上 ≥ 4.5:1 | 主题色当文字与图标用 |
| `--acc-*`、`--tint-*`、`--gold-ink*`、`--ok-ink*`、`--danger-ink`、`--hot-ink`、`--bronze` | 组件里原有的点缀色与浅底 | 同色相、白字或深色面上够对比度的一阶 | 金色、沙色、青灰的实色底（载白字），金色、薄荷等浅底，棕色与深绿文字 |

8 套主题的深色值（`--p` 配白字 5.3:1 以上，这样 85% 不透明的白字也够 4.5:1，同时对卡片面还有 3:1 以上；`--ga` 在深色下取同色，不做渐变）：

| 主题 | `--p` | `--pd` | `--pt` | `--pm` | `--p-text` |
|---|---|---|---|---|---|
| 雾粉 rose | `#9C5570` | `#8B4962` | `#38252B` | `#4D353D` | `#FBB4CC` |
| 珊瑚 coral | `#9B5A4A` | `#894E40` | `#382622` | `#4D3731` | `#FABAA9` |
| 暖橙 orange | `#8F6136` | `#7E552C` | `#35291E` | `#493A2C` | `#EEC198` |
| 草绿 green | `#487647` | `#3E673C` | `#232F22` | `#334232` | `#ABD7A8` |
| 青碧 teal | `#3E7377` | `#346569` | `#212E2F` | `#304142` | `#A3D4D7` |
| 天蓝 blue | `#4D6D98` | `#425F86` | `#232C37` | `#333E4C` | `#ADCDF7` |
| 紫藤 purple | `#736298` | `#645687` | `#2D2937` | `#3F3A4C` | `#D0C2F7` |
| 石墨 graphite | `#656C75` | `#595E67` | `#292B2F` | `#3A3D42` | `#C4CAD3` |

（表里的值以 `py -X utf8 references/component-library/tools/tokens.py` 的输出为准，它同时核对每一对的对比度：正文 4.5:1，白字在 `--p` 与 `--pd` 上 4.5:1，`--p` 对卡片面 3:1。）

图标：3D、真实、扁平的入口图标是图片，不处理；它们的底块（`.tile`）用 `--pm`、`--pt`、`--card` 的渐变，深色下自动换成深色版的底；线性图标用 `currentColor` 或 `--ink`，跟着变。商品图不处理。

### 例外清单（有理由地保持原样，静态检查放行）

| 例外 | 保持什么 | 理由 |
|---|---|---|
| 白字 `color:#fff`，以及半透明白字 | 白 | 它们压在主色、状态色、点缀色的实色底上，底在两种外观下都保证白字对比度（`--p`、`--ok-fill`、`--acc-*` 的深色版就是为此求解的） |
| 登录二维码（AD-PAGE 的扫码登录） | 白底 `--paper` 加深色码点 | 扫码器读不了反色码 |
| 后台深色侧栏（`sideCSS(…, dark)` 里 `dark ? '#1E2329' : …` 的分支，AD-NAV 的深色侧栏变体） | 深色 | 组件本来就是深色侧栏，浅色里也是深的 |
| 深底舞台（`stage: 'dark'`，即 `.st.night`）与第一代的暗金奢品卡、大图沉浸卡 | 深色 | 内容是深底设计，两种外观下一样 |
| 照片舞台的遮罩与压图文字、玻璃块上的白字 | 黑或白的半透明 | 压在图片上，底色由图片决定 |
| 纯黑阴影 `rgba(0,0,0,.x)`、白色高光 `rgba(255,255,255,.x)` 作文字色或边线色 | 黑、白 | 两种外观下都成立 |
| 金、沙、棕、青灰等彩色点缀（渐变按钮、角标、横幅、图表系列、默认头像的配色） | 原色 | 彩色不是中性色；载白字的几块有深色版令牌 |
| 默认头像 `critter()` 与空状态插画的内部色 | 原色 | 图片的一部分 |
| 对比度：AD-STATE-002 的 100 像素幽灵数字 `403` | `--pm` 色，浅色下同样是 1.4:1 | 装饰性的底纹字，页面标题用文字说了同一件事 |

### 怎么给新组件写令牌

1. 颜色一律写令牌（`check_component_library.py` 会报错并指出该写哪个）；浅色下的灰，按最近的一阶选：背景与填充 `--soft`（`#F2F3F5`）、`--n1…--n12`，边框 `--line` `--line2` 与 `--n7…`，文字 `--ink` … `--ink5`，阴影颜色 `--shNN`（数字是墨色的不透明度），遮罩 `--mask`。
2. 主色当填充（按钮、徽标、选中底）用 `--p`、`--pd`，白字放上去；主色当文字或图标用 `--p-text`（深一阶）、`--p-fg`（主色）。
3. 状态：文字与图标 `--ok --warn --danger`，浅底 `--ok-bg …`，载白字的实色底 `--ok-fill …`（不要拿文字色当底）。
4. 软底轨道里选中的白块 `--lift`；浮起的面（下拉、弹层）`--card3`、`--card2`；需要一直是白的 `--paper`，并加进这里的例外清单。
5. 文字压在图片或渐变上：自己保证对比度（深色测试跳过图片底并计数）。
6. 不要把 `dark`、`light` 当类名。
7. 写完跑 `check_component_library.py`，再在库页面切到“深色”逐个看；全库对比度由 `test_component_library.py` 兜底。

### 工具与验证

| 工具 | 做什么 |
|---|---|
| `tools/tokens.py` | 令牌表的唯一来源：浅色值、深色值、8 套主题的深色派生；`--write` 生成 `kit.css` 的令牌区块与 `kit.js` 的 `DARK_THEMES`，`--check` 核对源码与表一致并复核对比度 |
| `tools/tokenize_colours.py` | 把写死的颜色改成令牌的迁移脚本和映射规则（按属性上下文判断：`background:#fff` → `var(--card)`，`color:#fff` 不动，灰按最近一阶，差得多的用 `color-mix` 夹在两阶之间）；`--src DIR` 指向一份未改的源码可以重放统计；静态检查直接用它的规则，`KEEP` 是例外清单的机器可读版 |
| `tools/dark_audit.py` | 逐个组件量深色：每个可见文本节点对它真实背景的对比度（沿祖先找第一个不透明背景，半透明层合成，渐变逐个色标量，图片底跳过并计数，SVG 文字取它下面的图形与描边），图标、占位文字，近白大面板；停用与半透明变暗的元素单列 |
| `tools/visual_regression.py` | 浅色回归：`capture` 给每个组件的卡片截图并记录每个元素的尺寸与计算样式（固定随机数与时间、关掉动画），`compare` 逐张比像素与样式，阈值写在文件头 |

**映射规则**（`tokenize_colours.py` 按属性上下文判断，不是逐个值替换；迁移时的结果：约 2300 处，287 个带编号的组件（238 个加 49 个第一代模板）和共用工具、页面样式）：

| 写死的 | 写成 |
|---|---|
| `background:#fff` | `--card`；选中的块 `--lift`；下拉、弹层 `--card2`、`--card3`；刻意的白 `--paper` |
| 边框、阴影环、svg 描边与填充里的 `#fff` | `--card` |
| `color:#fff`、半透明白字 | 不动（白字压在实色底上） |
| 背景与边框里的灰（`#F2F3F5`、`#E6E8EC`、`#D5D9DF` …） | 最近的一阶 `--soft`、`--n1…--n12`、`--line`、`--line2`；相差 6 级以上的用 `color-mix` 夹在相邻两阶之间 |
| 文字里的灰（`#5B6470`、`#98A0AA` …） | `--ink2`、`--ink5` 等最近的一阶；很浅的字形灰 `--off` |
| `rgba(31,35,41,.12)` 做阴影 | `--sh12`；做背景 `--veil08`、`--mask`、`--mask2`、`--inv-a` 或 `color-mix(in srgb,var(--scrim) 45%,transparent)` |
| `rgba(255,255,255,.7)` 做背景 | `--glass0`、`--glass`、`--glass2`，其余 `color-mix(in srgb,var(--card) a%,transparent)`；白色内高光 `--hi` |
| `#3F7D58`、`#8A5A00`、`#A8433B` 做文字与图标 | `--ok`、`--warn`、`--danger`；做底（载白字）`--ok-fill`、`--warn-fill`、`--danger-fill`；它们的浅底 `--ok-bg` … |
| `color:var(--pd)`、`color:var(--p)` | `--p-text`、`--p-fg` |
| 价格红做底 | `--price-fill` |
| 个别浅底、棕色与深绿文字、金色与沙色的实色底 | `--tint-xxxxxx`、`--gold-ink*`、`--ok-ink*`、`--acc-*` |

`py -X utf8 scripts/audit_rendered.py <库页面> --library luz-kit --scheme dark` 可以另外量整页（参考用，库页面本身不是产品页）。

### 浅色回归

基线是改造前的构建：1500 与 390 宽度下每个组件的卡片（含标题与说明）各一张图，加每类的“怎么选”表、索引页、整页组合与工具栏，共 670 张，另有每个元素的尺寸和计算样式。阈值（`tools/visual_regression.py`）：平均像素差 ≤ 0.35（0–255），差 6 级以上的像素占比 ≤ 0.4%，元素框偏移 ≤ 0.6 像素，计算颜色每通道相差 ≤ 6 级。同一构建截两次是逐像素一致的，所以差异都来自改造。结果见最近一次汇报：没有超过阈值的图；全库计算样式里最大的颜色差异是 6 级（把相近的灰并进最近一阶造成的，共 15 处，都是边框与填充）；元素框一个都没有偏移。库页面工具栏新增了“外观”开关（放在标题行右侧，不改工具栏高度）。

## 七、已知限制

### 第一代的 52 个模板

`blocks1.js`、`blocks2.js`、`blocks3.js` 里的 52 个模板写在块作用域规则之前：它们用 `add(页签, 名称, 风格, 适合, 避免, css, html)` 登记，编号由 `taxonomy.js` 的 `LEGACY` 按名称对应；样式的根类是 `.k1`、`.b1`、`.i1` 这样的单个字母加数字（每个模板一个，不重复），不是 `mpcard001` 那种写法，也没有 `kw`。检查脚本对它们放宽这两条，其余条款照查。它们的交互钩子在 `blocks-zz-legacy-ix.js`。取用时它们同样凭编号，原型里同样包 `data-cid`。

### 与审计脚本的已知差距

`audit_rendered.py` 会在用这些组件搭出的页面上报两类问题，现状是：5 个组件用了 400/600/700 以外的字重（`MP-ENT-001`、`MP-ENT-002`、`MP-ENT-004`、`MP-ENT-005`、`MP-NAV-002`），35 个组件的过渡写在 width、left、top、margin 或 padding 上（`check_component_library.py` 把它们列成警告）。改它们会改变外观，没有顺手改；要让原型通过审计，取用这些组件时按审计规则改成 transform 与 opacity、字重改 600。

### 其他

- “整页组合”页（换槽位看搭配）直接拼第一代模板，不带 `data-cid`；它是演示页，不是组件舞台。
- 示例数据（姓名、手机号、订单号、门店）全部虚构。
- 静态展示、没有交互的组件只有两个：`MP-PRC-001` 价格样式集、`MP-PRC-003` 角标与丝带，在检查脚本的 `KNOWN_STATIC` 里。
- 源码里留有几处 `/*__END__*/`、`/*__MORE__*/` 注释，是当初分文件编写时的插入标记，不影响构建。
