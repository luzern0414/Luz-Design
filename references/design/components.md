# 组件

App 与 Web 的组件怎么选、怎么取、怎么借鉴参考站。控件的语义与行为优先用成熟实现；布局、内容组件、令牌与业务连接代码可以自写。

## 取用顺序

1. **项目已有的设计系统与组件**：已有产品延续现有框架，不为套本技能换栈。
2. **本库 HTML 模板与编号组件**（`templates/`）：定构图、取现成组件、做原型。
3. **成熟开源组件库**：登记在 `references/component-libraries.json`（Vant、Element Plus、shadcn/ui 注册表项等）。核对当前文档、固定版本、许可后使用；组件的默认弹层、文案、图标不合规时，用公开配置或插槽改成合规。
4. **自写业务组件**：只写布局、内容呈现、令牌、业务事件；复杂行为（键盘导航、表格、日期）确需自研时记录理由并针对性验证。

交付工程时，`component-sources.json` 记录每个来源的名称、固定版本、出处、许可文件、实际使用位置和文件哈希，见 [组件复用](../component-reuse.md)。

## 本库模板

`templates/` 只有四个文件夹，每个文件夹是**一个 html 加一个 `source/`**：用户只打开那一个 html，源文件收在 `source/` 里。公共样式、脚本与素材在仓库根的 `kit/`，仓库根的 `index.html` 是四个入口与全部编号索引。

```
index.html                     模板库首页：四个入口，加全部编号搜索
kit/                           tokens.css  ui.css  kit.css  app.css  web.css  agent.css  ui.js  assets/  frontend/（可运行工程起点）
templates/
  app/    app.html             tab：整页模板 | 组件库      source/pages（5 页）  source/parts（组件库源片段）
  web/    web.html             同上
  poster/ poster.html          tab：海报模板 | 提示词库    source/templates（PS 海报）  source/prompts（PP 提示词）
  documents/ documents.html    文件模板目录                word  excel  slides  pdf  reading（DC 模板、描述文件、样例）
```

`app.html`、`web.html`、`poster.html`、`documents.html` 由 `scripts/build_templates.py` 生成：整页与组件库原样存进同一个文件，按需挂载，页面各自保留自己的样式与脚本。改 `source/` 里的源文件后运行 `py -X utf8 scripts/build_templates.py all`，不手改成品。每个页面都可双击打开，不依赖网络。

新增或改动组件后，用 `py -X utf8 scripts/audit_gallery.py app|web --cats 分类 --width 1440` 与 `--width min` 逐个组件检测越界、重叠、折行、被裁、留白、内距不等、字号下限、含英文、title 属性与内联 svg，末行页面错误必须是 0；再加 `--view` 把分类截成长图，两个宽度各看一遍。检测只给线索，悬浮层、照片底上有意靠左、跑马灯与轮播的有意裁切会被标出，要人工判断。构建后还要过 `template_registry.py check`、`validate_skill.py --package-only` 与 `scripts/test_template_html_library.py`：源码里不得出现 `type="range"` 与原生 `<dialog>`（只读详情用页内居中浮层），脚本里素材路径不要拼进 `src="…"` 字符串。

打开 `app.html` 或 `web.html`，在顶部切换“整页模板”和“组件库”。整页模板左侧选页面，中间看预览，右侧有页面逻辑与组件编号。组件库按分类和搜索浏览，卡片沿网格对齐，组件编号可复制。顶部的主题色、背景和图标选择同时作用在两个页签。

用 `scripts/template_registry.py` 按编号取用，四类编号共用一套：

```
py -X utf8 scripts/template_registry.py list [--kind app|web|poster|prompt|document] [--cat BTN] [--query 词]
py -X utf8 scripts/template_registry.py show AP-BTN-004        组件：取出 HTML 与组件专属样式
py -X utf8 scripts/template_registry.py show PS-003            海报：文件、尺寸、用途、取用方式
py -X utf8 scripts/template_registry.py show PP-012            提示词：完整提示词与复核要点
py -X utf8 scripts/template_registry.py show DC-WD-002         文件模板：描述文件、样例、生成与检查命令
py -X utf8 scripts/template_registry.py check                  编号唯一、格式、同域连续、域与目录一致
py -X utf8 scripts/template_registry.py write                  刷新 references/template-registry.json 与 kit/registry.js
```

编号规则，发出后不改不复用：

| 编号 | 含义 |
|---|---|
| `AP-BTN-001` | 移动端组件。域：`BTN` 按钮、`BGND` 背景（含九种背景效果）、`CARD` 卡片、`ENTR` 入口、`NAVI` 导航、`FORM` 表单、`ROWS` 列表行、`DATA` 数据与图表、`FEED` 反馈与状态、`CHAT` 智能体、`MOTN` 动效 |
| `WB-TABL-001` | 网页后台组件。域同上，另有 `LAYT` 布局壳、`TABL` 表格，没有 `ENTR` `NAVI` `ROWS` |
| `AP-HOME-001` `WB-NAV-001` | 完整页面里的块：`HOME` `LIST` `ORDR` `MINE` `AGNT`；`NAV` 是每页共用的主导航 |
| `PS-001` | 海报模板 |
| `PP-001` | 海报提示词 |
| `DC-WD-001` `DC-WD-P01` | 文件模板与可复用块；`WD` 文字、`XL` 表格、`SL` 幻灯片、`PD` PDF、`RD` 阅读网页 |

组件源片段是 `templates/<端>/source/parts/NN-域.part`（html 片段，开头一行 `<!-- cat: BTN | 按钮 -->`，里面是可选 `<style>`、一个个 `.demo`、可选 `<script>`）；整页源文件是 `source/pages/*.html`，里面写 `../../../../kit/`，打包时自动改成上一级。用户报编号时按编号取用，不凭印象重写。

组件库按设计宽度设置列宽，App 从 380 像素起，Web 从 520 像素起。每排卡片上下齐边，纵向行间距为 0，宽组件占整行。舞台内边距 12，组件高度由其内容和必要操作决定。

### 共用类名与脚本

| 类别 | 类名 |
|---|---|
| 布局 | `.app` `.page` `.top`；`.web` `.rail` `.main` `.head` `.grid` `.cols-*` `.split` |
| 表面与模块 | `.card` `.card-stack` `.card-grid` `.card--tint` `.card--press` `.section` `.section__head` `.section__body` |
| 列表 | `.list` `.row` `.row--link` `.expand` `.table` `.kv` `.tl` |
| 操作 | `.btn` `.btn--primary` `.btn--soft` `.btn--secondary` `.btn--outline` `.btn--pill` `.btn--tint` `.btn--ghost` `.btn--danger` `.ibtn` |
| 切换与筛选 | `.seg` `.seg__item` `.drop` `.filter` `.toolbar` `.pager` |
| 表单 | `.field` `.input` `.textarea` `.search` `.switch` `.check` `.wheel` |
| 反馈 | `.tag` `.badge` `.skel` `.empty` `.progress` |
| 数据 | `.stat` `.stats` `.bars` `.donut` `.legend` `.chart` |
| 智能体 | `.chat` `.msg` `.bubble` `.think` `.tools` `.tool` `.approval` `.task` `.artifact` `.prompt` |
| 页面与浮层 | `.view` `.subbar` `.tabbar` `.actionbar` `.toast` `dialog.dialog` `.tip` |

`ui.js` 导出 `Lz`：`initSeg` 分段筛选、`initExpand` 就近展开、`view`/`back` 独立页面与返回、`initDrop` 下拉、`initToggles` 开关勾选、`initWheels` 纵向滚轮、`toast`、`confirm`、`line` 折线图、`stream` 流式文字、`count` 数字入场、`syncWheels` 提交前同步。页面通过 `data-seg`、`data-expand`、`data-open`、`data-back`、`data-tip` 等属性接入。`data-count` 与 `data-to`、`data-reveal` 已被数字入场与错峰出现占用，组件自己的计数、标记属性不要用这些名字；`data-copy` 只在组件头部的“复制编号”钮上由壳处理，组件内的复制按钮自己绑定事件。

### 素材

`kit/assets/` 的线性图标、三套入口图标（立体、真实、扁平；单色模式用扁平集加滤镜）、彩色实心业务图标、花卉商品实拍、背景图案与对象标识都是已生成素材，清单与哈希见 `kit/assets/manifest.json`，只用于起步和演示。新设计与实质改版要按主题重新生成并替换，不能把它们当最终品牌资产；对象标识按不可变对象 ID 持久分配，不在渲染时随机。

## 借鉴参考站

只借鉴结构、方法与版式，不复制代码与品牌。使用前读当前文档与许可，细节见 [参考来源](sources.md)。

| 参考 | 是什么 | 借鉴到本库 |
|---|---|---|
| EasyUI（easyui.site） | React 加 Tailwind 的复制式组件库，132 个组件，经 shadcn 注册表分发，MIT | 画廊版式：分类标签、搜索、每项实时演示与编号；组件清单与分类 |
| Beautiful UI（beautifului.dev） | 面向智能体界面的 21 个原语，MIT | 智能体页的思考、流式、工具调用、审批、任务行、输入栏 |
| Transitions.dev | 43 个以上的过渡效果，变量化、可重放预览 | 动效令牌与“播放”预览的做法；其库许可禁止再分发，不复制代码 |
| Vercel AI Elements | 基于 shadcn 的智能体界面组件（对话、消息、推理、工具） | 智能体消息的分块结构 |
| Vant、Element Plus | 移动与桌面的 Vue 组件库 | `frontend.py` 的两个工程起点 |

### 参考组件与本库对应

用 `template_registry.py list --query <中文名>` 查编号。

| 参考组件 | 本库组件 |
|---|---|
| Stat Card、Earnings、Money Card、Wallet Balance | 指标卡、余额卡 |
| Bar Chart、Donut Chart、Funnel Chart、Activity Heatmap、Live Line Chart | 条形图、环形占比、漏斗图、热力图、折线图 |
| Smooth Accordion、Expandable Data Row | 展开收起、行内展开 |
| Skeleton、Loader | 骨架屏、思考点 |
| Notification Stack、Undo Toast、Alert | 通知堆叠、轻提示、确认框 |
| Pricing、Stepper、Breadcrumb、SlidePagination | 价格方案卡、步骤条、面包屑、分页器 |
| Avatar Stack、Profile Card | 头像堆叠、用户资料卡 |
| Advanced Data Table、Smart Comparison | 可排序表格、对比表 |
| Interactive Timeline、Activity Feed | 动态时间线、物流时间线 |
| Chat、AI Response、Thinking Orb | 智能体对话、流式文字、思考过程 |
| Approval Card、Tool Chips、Task Rows、Prompt Bar | 审批卡、工具调用、任务行、输入栏 |
| Animated Number Morph、Morphing Dialog、Error state shake | 数字入场、确认框、输入抖动 |

### 不采用的内容

- 背景粒子、流星、故障文字、鼠标跟随、磁吸按钮等装饰特效：违反“不堆装饰、动效必须有目的”的要求。
- 毛玻璃导航、浮岛式底栏：底栏必须全宽贴底、不透明。
- 弹窗表单、侧滑面板、边缘滑出选择器：硬规则禁止，对应场景改为独立页面或就近展开。
- 暗色整页主题：卡片不做深色底，需要例外须用户确认。
