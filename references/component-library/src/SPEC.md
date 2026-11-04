# 组件模板库 · 开发规范（加组件、改组件前先读这份）

成品是一个单文件 HTML，里面每个组件都有编号（如 `MP-CARD-010`、`AD-TBL-003`），使用者只复制编号，凭编号从本目录的源码里取用。所以：**编号稳定、源码完整、组件能点能滑。** 取用方法、目录结构、构建与检查命令见上一级的 [README](../README.md)，本页只讲怎么写组件。

## 1. 文件与边界

- 新组件写进它所在类别的 `blocks-*.js`（类别与文件的对应见 README），或新建 `blocks-<名称>.js`（构建按文件名顺序载入全部）。文件整体包在一个块作用域或函数里，局部常量不外泄。
- **不要改核心文件的行为**：`core-def.js` `core-ui.js` `ix.js` `ix.css` `extras.js` `kit.js` `kit.css` `combo.js` `lib.template.html` `blocks1-3.js`。别的东西按“文件级”引用这些源码，改了行为会连带坏。`taxonomy.js` 只用于加类别。需要的新交互，写在自己组件的 `js(root)` 钩子里；需要的新图标，在自己文件顶部 `Object.assign(LINE, {...})` 补（图标名加文件前缀防冲突）。
- 构建（仓库根目录，Windows 用 `py -X utf8`）：
  ```
  py -X utf8 scripts/build_component_library.py                       # 完整库 → references/component-library/dist/component-library.html
  py -X utf8 scripts/build_component_library.py --files blocks-ad-comm.js --out %TEMP%\small.html   # 只含第一代 52 个模板加你列出的文件
  ```
  环境变量 `LIB_OUT`、`LIB_FILES` 对直接运行 `references/component-library/build.py` 的脚本同样有效。
- 检查与测试：`py -X utf8 scripts/check_component_library.py`（静态，通过时打印 `component library: ok`）、`py -X utf8 scripts/test_component_library.py`（含 Playwright 浏览器测试）。看效果用 Playwright 逐类别截图，截完逐张看，不合格就改。

## 2. 编号与类别

编号 = `域-类别-三位序号`，在 `def()` 的 `id` 里写死，**一经写入不改、不复用、不重排**。类别表在 `taxonomy.js`：

| 域 | 类别码 | 含义 |
|---|---|---|
| MP 小程序 | HDR 头图横幅 · ENT 入口与宫格 · CARD 卡片 · PRC 价格与标签 · BTN 按钮 · NAV 导航与顶栏 · FORM 表单与输入 · FB 弹层与反馈 · MKT 营销活动 · GOODS 商品详情 · ORD 购物车与订单 · MEM 会员与个人中心 · CONT 内容与社区 · LIST 列表与筛选 · STATE 状态与空态 · SVC 服务与预约 | |
| AD 后台管理 | TBL 表格与列表 · FLT 筛选与搜索 · FORM 表单与输入 · CTRL 基础控件 · DATA 数据展示 · CHART 图表 · NAV 导航与页头 · FB 弹层与反馈 · STATE 状态与结果页 · FLOW 流程与协作 · COMM 沟通与消息 · MGMT 系统管理 · PAGE 整页布局 | |

在自己的类别里顺着往后编，序号连续、不留空号（脚本 `check_component_library.py` 查）。第一代 52 个模板占用的号：CARD 001–009、BTN 001–008、ENT 001–007、HDR 001–006、PRC 001–006、MKT 001–005、NAV 001–005、FORM 001–003、FB 001–003。

## 3. 写一个组件：`def()`

```js
def({
  id: 'AD-TBL-001',            // 必填
  name: '基础数据表',           // ≤12 个汉字，名词性，写清是什么；同一类别不重名
  style: '排序+分页',           // ≤6 个汉字的风格或特征标签
  fit: '一句话：什么场景用',
  avoid: '一句话：什么场景别用 / 常见坑',
  kw: 'table 表格 排序 分页 订单列表',   // 搜索关键词，至少 5 个，含近义词和英文
  stage: '', wide: true, bg: null,        // stage: ''|'tint'|'dark'|'white'|'photo'；wide=占满一行；bg: 'silk'|'interior'（配 stage:'photo'）
  css: `.adtbl001{...} .adtbl001 .h{...}`, // 见 §4
  html: () => `<div class="adtbl001">…</div>`,
  js: (root) => { /* 可选：渲染后执行，root 是外层 .ixr（库自动包的容器），不是块根 .adtbl001；只在需要特殊交互时写 */ },
})
guide('ad', 'TBL', [['场景', '推荐的组件名', '原因'], …])   // 每个类别一次，5–7 行，推荐项必须是本类别里真实存在的组件名
```

- 第一代类别（CARD/BTN/ENT/HDR/PRC/MKT/NAV/FORM/FB）的“怎么选”表已合并进各自的 `guide('mp', 'CARD', …)`，新增组件时在那一行表里加一行。
- 库页面和原型引擎把每个组件包成 `<div class="ixr" data-id="编号" data-cid="编号">…</div>`。**`data-cid` 是组件根的标记，值是组件编号**，审计（`audit_rendered.py --library luz-kit`）按它判断一个控件是不是库里的真实组件；组件自己的 HTML 里不用写它。
- 可用的全局：`P(i)` 商品图 0–8；`IC(name)` 入口图标（跟随“图标风格”，只有 giftbox scooter coupon bag heart star pin cart giftcard wallet 十个）；`sv(name)` 线性图标（`LINE` 里的名字，见 `kit.js`、`extras.js`，宽高 100%，用在你自己定尺寸的容器里）；`ICS()` 当前图标风格类；`critter(i, size)` 默认卡通动物头像；`NAMES ORDER_ROWS SKUS DEPTS` 示例数据；`ASSETS.bg.silk/interior`。**内容通用化**：电商、会员、运营、订单、用户、内容，不出现某个具体行业或客户；中文真实、数值合理、有长短差异（含一条较长文案，测溢出）；示例人名、手机号、订单号都是虚构的。

## 4. CSS 规则（硬性）

- **作用域前缀**：块的根元素类名固定为 `小写域类别+序号`，如 `adtbl001`、`mpgoods004`；所有选择器都以 `.adtbl001 ` 开头。禁止裸写 `.on` `.btn` `.card` 之类会串到别的块的选择器。文件里的 CSS 小工具可以用占位符代表块根（`&`、`§`，由 `CSS()`、`C()`、`K()` 展开成 `.根类`）；改选库自带的基础类时用自己的前缀覆盖。可复用库里的基础类：`.btn .btn-p .btn-s .btn-sm`（按钮）、`.price .strike`（价格）、`.tg .tg-hot .tg-soft .tg-red`（标签）、`.tile .tile-sq .tile-ci .tile-no .ico`（图标块，入口图标用）——它们已带主题色。
- **颜色一律用令牌**：背景、文字、边框、阴影、遮罩、状态色**不写死** `#fff`、`#fafafa` 一类的白与灰、近黑与灰的文字色、状态色及其浅底、`rgba(31,35,41,.x)`，只写 `var(--…)`。`scripts/check_component_library.py` 对每一处写死的中性色与状态色报错（给出编号、行号和该写的令牌），例外清单见 README“深色”一节（白字 `color:#fff`、纯黑阴影、彩色点缀色、二维码与深底卡片等）。取值与每个令牌的浅深两组值见 README“深色”一节，生成在 `kit.css` 里，源表是 `tools/tokens.py`：
  - **主题色**（切换主题色自动生效，禁止写死主色）：`--p`（主色，填充，配白字≥4.5:1）`--pd`（深一阶，作填充）`--pt`（极浅底）`--pm`（浅底边）`--ga --gb`（渐变两端，幅度很小）`--p-rgb`；**文字与图标用** `--p-text`（浅色=`--pd`）与 `--p-fg`（浅色=`--p`），不要把填充用的 `--pd`、`--p` 当文字色：深色下它们是填充阶，文字要用较浅的一阶。
  - **面**：`--bg` 页面底、`--card` 卡片面（浮起的面用 `--card2` 悬浮卡、`--card3` 下拉与弹层、`--card4` 对话框）、`--soft` 浅灰填充、`--n1…--n12` 中性色阶（填充、边线、轨道，按浅色下的灰选最近的一阶）、`--line` `--line2` 分隔线、`--lift`（软底轨道里被选中的那一块，如分段控件的选中项）、`--paper`（刻意保持白的面）。
  - **文字**：`--ink`（正文）`--ink1…--ink7`（逐级变浅：`--ink2` 次要、`--ink3` 辅助、`--ink4` 提示、`--ink5` 占位，`--ink6` `--ink7` 只给不可用与失效的字）。
  - **状态**：`--ok --warn --danger --neutral`（文字与图标）、`--ok-bg --warn-bg --danger-bg --neutral-bg`（浅底）、`--ok-fill --warn-fill --danger-fill --price-fill`（载白字的实色底）、`--ok-line --warn-line --danger-line`（边）、`--price`（价格字）、`--info` 用 `--p-text`、`--info-bg` 用 `--pt`。
  - **阴影与遮罩**：阴影的形状留在组件里，颜色写 `var(--sh06)`（墨色 6%，数字是不透明度）；半透明填充 `--veil06`；遮罩 `--mask` `--mask2`，磨砂 `--glass`；一般的半透明遮罩用 `color-mix(in srgb,var(--scrim) 45%,transparent)`。
  - 现有令牌没有的灰，按浅色下的值选最近的一阶，差得多就用 `color-mix(in srgb,var(--a) 47%,var(--b))` 夹在相邻两阶之间；不要自己加十六进制。新组件的卡片底用 `var(--card)`、页面底 `var(--bg)`、分隔线 `var(--line)`。
- **状态色（低饱和，固定）**：成功 `#3F7D58`（底 `#EAF3EE`）、警告 `#8A5A00`（底 `#F7EEDB`）、危险 `#A8433B`（底 `#F8ECEA`）、信息用主题色、中性 `#6A727D`（底 `#F2F3F5`），这是**浅色下的值，写在组件里时只写令牌**（`--ok --ok-bg --warn …`）；深色下是较浅的文字色阶配低亮度同色相的底，不是这几个十六进制。**整体饱和度要低**（被反复指出过“饱和度太深”）：不用纯红纯蓝纯橙，大面积用中性色加主题浅底，强调色只在小面积。渐变只用 `var(--ga)→var(--gb)` 这种很小幅度的，不另造鲜艳渐变；阴影中性、不带彩色大光晕。检查脚本对十六进制色值做饱和度上限检查（HSV 饱和度 > 0.80 且不太暗的非状态色会被报出）。
- **字体**：只用继承的字体栈；不斜体、不加字距、不旋转文字；字重只用 400/600/700，700 只给 ≥22px 的大数字或页面标题。小程序字号 12/14/16/18/22（大数 28/32），正文 14–16，不小于 12；后台正文 14、辅助 12，表格 14，不小于 12。
- **图标**：控件图标用线性 `sv()`（线宽 2）；一个对象一个图标，不同对象不共用；入口/营销装饰图标用 `IC()`；头像用 `critter()`，**绝不用文字或首字母头像**。
- **形态**：小程序按钮最小点击区 44×44，后台控件高 32/36/40；圆角 4/8/12/16/22 里选，同一块内统一；不用 `position:fixed`（检查脚本会报）；`backdrop-filter` 只允许玻璃类块并配照片底（`stage:'photo'`）。
- **宽度**：小程序块总宽 ≤ 358px（居中），后台块宽度写 `width:100%`（整行用 `wide:true`，宽约 1400px；非 wide 约 600px）。
- **焦点**：文本框聚焦只把 1px 边框加深到 `--ink2`，不要主色外框、发光、粗描边；按钮/链接鼠标点击不出现焦点框。
- **深色**：库有浅色（默认，设计与验收的基准）和深色两套外观，深色是第二套配色，不是浅色取反。触发：`<html>` 或任意祖先带类 `dark` 时深色，`prefers-color-scheme: dark` 且没有 `light` 类时（跟随系统）也是深色，带类 `light` 强制浅色；同时认 `data-theme="dark"`、`data-theme="light"`；离得最近的一层生效。`kit.js` 提供 `setAppearance('system'|'light'|'dark')`。写组件时：颜色全用令牌（上一条）；白字只给实色填充（`--p --pd --ok-fill --danger-fill --price-fill --inv --acc-*`）；文字压在图片或渐变上要自己保证对比度；线性图标用 `currentColor`；阴影在深色下会变成黑色弱阴影，层级靠更亮的面（`--card2…4`），不要靠阴影；**不要把 `dark`、`light` 当类名用**（`stage: 'dark'` 渲染成 `.night`）；需要一直是白的面（二维码）用 `--paper`，并写进 README 的例外清单。验收：`tools/dark_audit.py` 逐个文本节点与图标量对比度（正文 4.5、大字与图标与占位 3），`test_component_library.py` 全库跑。
- **动效**：位移/缩放 100–300ms，`cubic-bezier(.2,0,0,1)`；不用 `transition:all`（检查脚本会报）；不超过必要的弹跳。

### 后台专项（做 AD 类必须照做）

- 表头居中；列内容：短值（状态、数字、日期）居中，长文本左对齐并留缩进，金额右对齐；行高 44–48；正文 14。
- 分页默认每页 20 条，可选 10/20/50/100；筛选默认只显示重要的几项，其余收进“更多筛选”。
- 详情、编辑、确认一律**居中悬浮面板**（有遮罩，可关闭），**不用右侧抽屉**；列表行内的开关直接生效（成功轻提示，失败回滚并在原位写原因），只有重要修改才二次确认。
- 页面标题不重复导航文字；空列不要；导出和展示里不出现英文字段名。
- 同一页同一目的地只一个入口；不放“策略建议”之类不属于系统功能的文字。

### 小程序专项（做 MP 类必须照做）

- 首屏营销模块不超过 2 个；同一活动只占一个位置；整张卡片可点时，卡内不再放指向同一目的地的按钮；一张卡片只有一个主按钮；同一信息在一张卡里只说一次。
- 列表不用页码（滚动加载，“没有更多了”）；二级页有返回；弹层可关闭、高度 ≤80%、底部按钮固定。
- 有加载/空/失败的组件要把这些状态做进交互（比如点“重试”）。

## 5. 交互：`data-ix` 词汇表

块的 HTML 只写属性，交互由 `ix.js` 统一处理；块根是 `<div class="ixr">`（库自动包，`position:relative`）。**“选中”一律是 `.on` 类**，自己的 CSS 写 `.前缀 .xxx.on{…}`。

| 属性 | 结构 | 行为 |
|---|---|---|
| `data-ix="tabs"` | 容器内按钮 `[data-t="键"]`；面板 `[data-p="键"]`（可选，同一 `data-g` 分组）；可有 `<i class="ink">` 滑动下划线；`data-list="选择器"` 时按 `data-k` 过滤列表 | 切换 `.on`，显示对应面板，下划线滑动 |
| `data-ix="radio"` | 子项 `[data-o]`；`data-bind=".选择器"` 把选中文字写到目标 | 单选 |
| `data-ix="multi"` | 子项 `[data-o]`；`data-max` | 多选（可限数量） |
| `data-ix="toggle"` | 元素自身 | 开关，切换 `.on` 与 `aria-checked` |
| `data-ix="stepper"` | 按钮 `[data-d="-1"]` `[data-d="1"]`，数值 `[data-val]`；`data-min/max/step`；`data-price` + `data-sum=".选择器"` 联动合计 | 步进，到边界按钮加 `.dis` |
| `data-ix="carousel"` | 内含 `<div class="ix-track">` 轨道（子项为幻灯片），可选 `<div class="dots"><i>…`、箭头 `[data-d="±1"]`；`data-auto="3000"` 自动轮播 | 触屏手指滑、鼠标拖动、圆点/箭头跳转、自动轮播 |
| `.ix-track` / `data-ix="drag"` | 任何横向 overflow 容器 | 鼠标按住拖动滚动（触屏本来就能滑） |
| `data-ix="acc"` | 项 `.ix-ai` > 头 `[data-h]` + `.ix-ab`（里面再包一层 `<div>`）；`data-single` 只展开一项 | 手风琴展开/收起 |
| `data-open="名"` / `data-ov="名"` | 触发器带 `data-open`；覆盖层 `<div class="ix-ov" data-ov="名"><div class="ix-mask"></div>…内容…<button data-close>` | 弹层打开/关闭（遮罩、关闭键） |
| `data-ix="dd"` | `[data-tg]` 触发器 + `.menu`（里面项 `[data-o]`）+ `[data-label]` 显示选中 | 下拉选择 |
| `data-toast="文字"` | 任意元素 | 点击在块内弹出轻提示 |
| `data-ix="rate"` | 子项 `[data-n="1..5"]` | 评分点选 |
| `data-ix="like"` | 元素 + 内含 `[data-n]` 数字 | 点赞/收藏切换与计数 |
| `data-ix="count" data-sec="秒"` | 内含 `[data-h][data-m][data-s]` | 倒计时 |
| `data-ix="swipe" data-w="宽"` | `.sf`（前景）+ `.sa`（右侧操作区，里面按钮 `[data-del]` 删除） | 左滑露出操作、点删除折叠消失 |
| `data-ix="sort"` | `<table>`，表头 `th[data-sort="n或s"]`，单元格可带 `data-v` | 点表头升降序重排行 |
| `data-ix="checks"` | `[data-all]` 全选框 + `[data-c]` 行选框；任意处 `[data-count]` 显示数量、`[data-bar]` 批量条（无选中时隐藏） | 全选/半选/批量条 |
| `data-ix="pager"` | `[data-pg="页文案"]` 页码按钮 + `[data-d="±1"]` 上下页；`[data-info]` 显示当前 | 翻页高亮 |
| `data-ix="tree"` | `li > [data-x]` 展开键 | 树节点展开/收起（`li.open`） |
| `data-ix="slider"` | `.rt` > `.rf` + `.th`；`data-min/max/value`；`data-bind=".选择器"` | 拖动滑块（鼠标/触屏） |
| `data-ix="range"` | `<input type="range">`；`data-bind=".选择器"` | 拖动时把值写到目标 |
| `data-ix="steps"` | `.sp` 步骤项 + `[data-d="±1"]` 上下一步 + `[data-s]` 面板 | 步骤前进后退（`.on` 当前、`.done` 已完成） |
| `data-ix="cal"` | 日期格 `[data-day]`；`data-range` 为区间选择 | 点选日期/区间（`.on`、`.in`） |
| `data-ix="upload"` | `[data-add]` 添加键；`data-max` | 点击添加缩略图、点 × 删除 |
| `data-ix="search"` | `<input data-list=".列表选择器">`，列表子项文本可被过滤 | 输入即过滤 |
| `data-ix="remove"` | 按钮，所在 `[data-row]` 行 | 删除一行 |

特殊交互（拖拽排序、图表悬停提示、看板拖卡片、内联编辑、级联选择、日期面板翻月……）写在 `js: (root) => {}`，用 `root.querySelector` 限定在块内，监听事件即可。块被重渲染时 DOM 会重建，钩子会重新执行，所以不要挂全局监听，计时器要在 `root.isConnected` 为假时清掉。

**每个组件至少有一个有意义的交互**（不是为交互而交互）：能点的点了有反馈，能滑的能滑，能选的能选，能展开的能展开，状态变化要看得见（含禁用、加载、成功、失败）。

## 6. 质量线与自检

1. 每个组件独立放进 `.st` 舞台里，在 1500 宽桌面和 390 宽手机下都看一遍：无文字溢出、无错位、无横向撑破（后台宽块在手机上允许舞台内横向滚动）。
2. 切换 8 个主题色和 4 种图标风格各看一遍（尤其是带 `IC()` 的）：对比度够，不出现写死的鲜艳色。
3. 交互逐个点：对每个组件执行点击/拖动并断言状态（例如点了第 2 个标签后 `.on` 在第 2 个；步进器到上限后按钮 `.dis`；排序后第一行变了）。无控制台报错。`test_component_library.py` 已按 `data-ix` 的种类把全库点了一遍；组件自己的 `js(root)` 里的特殊交互，要自己补用例。
4. 编号：`BLOCKS` 里无重复、类别正确（`def()` 已校验，报错会让页面白屏，先修）；序号连续。
5. 命名：名称见名知意，同类别里不重名；`fit`/`avoid` 各一句话，不空话；`kw` 写 5–10 个词。
6. 画面要好看：留白、层级、对齐、一致的圆角与阴影；不是把控件堆在一起。商用级，参照主流产品的做法（微信支付页、淘宝/京东/拼多多小程序、美团、瑞幸、Ant Design Pro、Element Plus 后台、TDesign、Arco Design）。
7. 提交前跑：
   ```
   py -X utf8 scripts/check_component_library.py
   py -X utf8 scripts/build_component_library.py --index       # 索引随源码更新，一并提交
   py -X utf8 scripts/test_component_library.py
   ```
