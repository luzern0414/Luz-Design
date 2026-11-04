# Luz UI kit

视觉实现底座：令牌、组件、六种页面布局，原生 CSS 与 JS，不依赖任何库。项目在它上面改色相和少量令牌，不改组件；页面按业务优先级选布局，规则见 `../visual-design.html` 的“页面布局模式”。

| 文件 | 内容 |
|---|---|
| `ui.css` | 令牌（`oklch` 颜色、八像素栅格、圆角、五级层级、字阶、动效，浅色一套、深色一套）、基础、六种布局（`l-hero`、`l-bands`、`l-rail`、`l-canvas`、`l-kanban`、`l-lanes`）、组件（按钮、表单、卡片、指标、标签、标签页、分段、表格、原生 `dialog`、`popover` 菜单、提示、骨架、空状态、图表样式）；分在 `@layer reset, tokens, base, layout, components, utilities, project` |
| `ui.js` | `UI.dialog`、`UI.confirm`、`UI.sheet`、`UI.toast`、`UI.menu`、`UI.tabs`、`UI.count`、`UI.spark`、`UI.line`、`UI.bars`、`UI.donut`、`UI.kanban`、`UI.lanes`、`UI.brand`、`UI.go`（视图过渡）、`UI.setReduced`、`UI.theme`（跟随系统 / 浅色 / 深色）、`UI.appearance`（三选一外观控件） |
| `layouts/*.html` | 六种布局各一个可运行页面，`layouts/_make.py` 重新生成 |
| `react/Layouts.jsx` | 六种布局的 React 写法（同一套类名；参照写法，未在本仓库运行） |
| `commerce-kit/` | 交易与营销界面的完整示例：`index.html` 演示首页与营销区、菜单页、规格弹层、券面缺口、结算明细、领券弹窗、强公告与取餐号，`assets/` 是生成的透明底元素，`screenshot-home.png` 是手机宽度的首屏截图；画法见 `../ui-recipes.html`，可换主题色取用的骨架是 `../templates.txt` 的 `commerce-kit.html` |

## 项目怎么用

1. `<link rel="stylesheet" href="ui.css">`，`<script src="ui.js">`。
2. 改主色：`UI.brand(色相, 彩度)` 或在 `@layer project` 里写 `:root { --brand-h: 250; --brand-c: 0.1; }`；亮度台阶固定，白字在主色上始终不低于 4.5:1。
3. 页面外层是 `<section class="page">`（容器查询的容器），里面放一种主布局；断点按容器宽度，不按视口宽度。
4. 页面第一个可见元素是唯一的 `<h1 class="page-title">`，紧跟 `<section>`。
5. 检查：`py -X utf8 ../../scripts/audit_rendered.py <页面.html> [--width 390]`（字号、字重、对比度、触控尺寸、`transition: all`、文本框聚焦框），浅色与深色各跑一遍（`--scheme light`、`--scheme dark`；用 `data-theme` 切换的页面深色加 `--dark-attr data-theme=dark`），再用 `check_document.py --allow interface`。
6. 深色与浅色两套主题（`../visual-design.html` 的“深色与浅色两套主题”）：`ui.css` 的令牌在 `:root` 里是浅色，深色在 `@media (prefers-color-scheme: dark)`（选择器 `:root:not([data-theme="light"])`）与 `:root[data-theme="dark"]` 里重定义，两处声明一致；`:root[data-theme="light"]` 强制浅色。页面 `<head>` 里在样式表之前放一段内联脚本（见 `layouts/_make.py` 的 `THEME_HEAD`）读 `localStorage` 的 `luz-theme` 并设 `<html data-theme>`；页面里用 `UI.appearance(挂载点)` 放“跟随系统 / 浅色 / 深色”三选一控件，`UI.demo` 的演示控制面板里已有“外观”一组。深色里品牌色只改色相与彩度的方式不变（`UI.brand`）；浮起的面用 `--raise-2`、`--raise-3`、`--raise-4`（浅色里同为白色卡片面，深色里逐级更亮）。

## 用到的新技术与降级

| 技术 | 用在哪里 | 不支持时 |
|---|---|---|
| `@layer`、`:has()`、嵌套容器查询 `@container` | 层次、标签页选中态、布局折叠 | 容器查询是基线能力；`:has()` 不支持时选中态靠 `aria-selected` |
| `oklch()`、`color-mix()` | 令牌与悬停色 | 基线能力 |
| 原生 `<dialog>` 与 `@starting-style`、`transition-behavior: allow-discrete` | 对话框、底部弹层的入场与退出 | 无 `@starting-style` 时直接显示，无退出动画 |
| Popover API | 菜单、提示 | 2024 年起主流浏览器都支持；更早的浏览器里菜单打不开，需要的项目另行降级 |
| CSS anchor 定位 | 菜单贴着触发器 | 无则 `ui.js` 按触发器位置放 |
| View Transition API | 标签与页面切换的交叉淡化 | 无则直接切换 |
| `prefers-color-scheme`、`color-scheme` | 跟随系统的深色主题；表单控件与滚动条随主题变深（浮起的面用上面的 `color-mix()`） | 基线能力 |
| `field-sizing: content` | 文本域随内容增高 | 无则固定最小高度，可手动拉伸 |

## 写页面时已经由组件处理的几件事

| 问题 | 组件怎么处理 |
|---|---|
| 对话框被推到左上角 | `dialog.dlg` 自带 `margin: auto`（重置层的 `margin: 0` 会盖掉浏览器默认的居中）；底部弹层 `dialog.sheet` 贴底 |
| 窄屏整页横向滚动 | `.l-bands`、`.stack`、`.stack-lg`、`.app-main` 的单列轨道是 `minmax(0, 1fr)`，里面的宽表格和长文本在自己的容器里滚动，不再撑开页面 |
| 点文本框出现蓝色选中框、光晕或默认轮廓 | 输入框、选择、多行输入聚焦只把 1 像素边加深到 `--text-2`；其余控件鼠标点击没有焦点框，键盘到达（`:focus-visible`）才显示 2 像素深色轮廓；全局关掉点按高亮 |
| 手机上按钮、分段控件太矮 | 触屏或视口不超过 700 像素时，`.btn--sm` 和 `.seg` 的按钮至少 40 像素高 |
| 同时开几个对话框，标题 id 重复 | `UI.dialog` 给每个对话框一个唯一的标题 id；确认框用 `size: 'sm'`（`dlg--sm`，400 像素） |
| 重复调用 `UI.menu` 后旧菜单留在页面里 | 同一个触发器重建菜单、或触发器已被移出页面时，旧菜单自动清掉 |
| 菜单项不能用时怎么写 | `{label, disabled: true}` 或 `disabled: '原因'`：置灰、不响应点击、原因显示在右侧并随菜单项读出 |
| 看板拒绝某次移动 | `onMove(cardId, from, to)` 返回 `false`（或解析为 `false` 的 Promise），卡片放回原列原位 |
| 柱图只有纵向 | `UI.bars` 画纵向柱；横向条用 `.progress` 或表格里的条形，不再有 `horizontal` 选项 |
| 地图图钉太小 | 画地图时给每个图钉加一个透明的点击圈（见 `layouts/4-*.html`），手机宽度下也不小于 40 像素 |

## 用它做出来的完整原型

Luz-System 仓库的 `examples/base-prototype/` 是用这套套件做出的完整原型：后台 17 页、小程序 25 页，六种布局都用到，在真实浏览器里逐页走过。它只是参考，不是模板：新项目的页面与入口由功能清单决定。
