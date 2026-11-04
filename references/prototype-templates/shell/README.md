# 多系统外壳（shell）：一份文档，一个“前端架构”页签，每个系统一个页签

> **参考实现，不是写死的模板。** 外壳只做一件事：把已经能用的原型装进一份文档里，每个系统或设备端一个页签，页签里只有一个可交互原型。页面清单、架构表格、系统数量都由项目自己决定，示例里的内容（`examples/suite-demo`）只是一种答案。

生成器是 `scripts/build_prototype_suite.py`，测试是 `scripts/test_prototype_suite.py`，示例在 `examples/suite-demo/`。

## 一、怎么用

```
py -X utf8 scripts/build_prototype_suite.py <suite.json> --out <文档.html>            iframe 引用同目录的原型文件
py -X utf8 scripts/build_prototype_suite.py <suite.json> --out <文档.html> --inline   原型以 srcdoc 嵌进文档，真正的单文件
py -X utf8 scripts/build_prototype_suite.py <suite.json> --check                      只校验，不写任何文件
py -X utf8 scripts/build_prototype_suite.py <suite.json> --out <文档.html> --number-from 3 --project-tabs <tabs.json>
```

`suite.json` 的字段：

| 字段 | 含义 |
|---|---|
| `title`、`overview` | 文档标题；结论（一两句话，不超过 150 字，与 Luz-Project 的“开头是结论”一致） |
| `architecture` | “前端架构”页签：`{"sections": [{"title", "blocks": [...]}]}`。块有 `text`、`list`（也认 `bullets`）、`table`（`caption` 表题、`columns`、`rows`，没有内容写“—”）、`layers`（分层图：`caption`、`rows[{label, nodes[{name, note}]}]`、`links[{after, label}]`，也认 Luz-Project 的 `figure` + `kind: layers`）、`sub`、`note`、`code`。写什么由项目定：分层、页面地图、路由与权限、状态放在哪里、响应式断点、组件库与主题是常见的几块，没有必填 |
| `checks` | 可选：再加一个“检查与差异”页签（写法同 `architecture`），放在最后；不写就没有这个页签 |
| `systems[]` | 每个系统或设备端一个页签 |
| `systems[].name` | 页签名，也是前端的名字；不能重复，不能叫“前端架构” |
| `systems[].surface` | `miniapp`、`h5`、`admin`、`website` |
| `systems[].kind` | `phone` 或 `wide`；不写就按 surface 定（miniapp、h5 是 phone，admin、website 是 wide）；写了要与 surface 匹配，小程序只能是 phone |
| `systems[].spec` / `file` | 二选一：`spec` 是原型规格（交给 `build_prototype.py` 构建，路径相对 suite.json），`file` 是已构建好的 html |
| `systems[].library` | 组件库编号，默认 `luz-kit`，要在 `references/component-libraries.json` 里并且适合这一端 |
| `systems[].title`、`height` | 原型框标题栏的名字（默认“名字原型”）；iframe 高度上限（默认 phone 900、wide 860） |

页签 = 前端架构 + 每个系统一个（有 `checks` 时再加最后一个）。系统页签里只有一个原型框：标题栏左边是名字，右边是“重新载入”“在新窗口打开”；路径和页面清单只在“前端架构”里，系统页签里不放说明、清单、截图。“前端架构”页签的最后会自动加一张表，列出每个页签对应的使用端、设备端、组件库和原型文件。

行为：

- 默认 `<iframe>` 引用输出目录里的原型文件（`NN-名字原型.html`，`NN` 从 `--number-from` 起，默认 1），**切到那个页签才加载**；`file` 指向别处的文件会复制到文档旁边。`--inline` 把原型放进 `data-srcdoc`，第一次切到页签时才挂成 `srcdoc`，“在新窗口打开”用 Blob 地址，得到真正的单文件（体积约等于各原型之和）。
- 键盘左右键（也认 Home、End）切换页签，地址 `#tab=1` 直达，改地址里的井号也会跟着切；打印时页签条隐藏、全部页签展开、系统页签有标题，打印前载入全部原型。
- 页面按阅读页写：字阶取 `references/md-type.css`（桌面正文 18、手机 16），一条字体栈，页面最宽 1280 以放下三栏原型；深浅外观随系统（`prefers-color-scheme`，也认 `data-theme`）；手机宽度下左右边距 16，页签条自己横向滚动，表格在自己的框里横向滚动，页面不横向撑破，原型框宽度跟随页面。
- iframe 高度是 `min(height, max(560px, 窗口高度 - 150px))`，一屏里能看到整个原型框的大部分。

校验只查结构与引用关系，中文报错：页签重名、同一原型文件（或规格）被两个页签用、`kind` 与 `surface` 不匹配、规格的模板（mini 或 admin）与 `kind` 不一致、系统没有原型、规格或文件不存在、组件库未登记或不适合这一端、规格构建失败（**原样带出 `build_prototype.py` 的报错**）、表没有表题、空单元格、分层图不足两层、占位字样、多余字段。前端架构里没有提到某个系统只是警告。

## 二、与 Luz-Project 的 02-前端界面设计 的关系

- **项目模式**：用 `project.py document <项目> design --file spec.json` 生成 `docs/02-产品开发/02-前端界面设计.html`，用 Luz-Project 自己的生成器、校验器和审批，前端规范有 13 类底座对照和“页面与路径”，页签是 前端规范 + 每个前端 + 检查与差异。**不要用外壳代替它。**
- **独立使用**（不走项目流程，只要一份“能点的多系统文档”）：用外壳。它的页签结构与 02 文档一致：先是说明页（前端架构，对应前端规范），再是每个系统或设备端一个页签，页签里只有一个原型框、两个按钮；同一系统的手机页与电脑页各开一个页签。区别是外壳的“前端架构”是轻量版（没有 13 类底座对照），“检查与差异”只在写了 `checks` 时才有。
- 两边的原型框、标题栏按钮、`#tab=`、左右键、打印展开、“切到页签才加载”做法相同，方便把外壳的页签直接搬回项目文档。

## 三、把模板产出的原型放进 Luz-Project 的 `prototype` 块

1. 用 `build_prototype.py <规格> --out <文件>` 构建（或让外壳用 `spec` 字段构建），文件放进项目的 `docs/02-产品开发/`，与文档同一层，名字是“序号 + 前端名称 + 原型”，如 `03-小程序原型.html`。外壳的 `--number-from 3 --project-tabs tabs.json` 会按这个命名写文件，并写出前端页签的 JSON。
2. `prototype` 块只写 `file`（项目根起的路径，如 `docs/02-产品开发/03-小程序原型.html`）、`title`（原型框顶栏的名字）、`kind`（`phone` 或 `wide`）、`library`（**`luz-kit`**，可选 `height`）；不写 `caption`、`try`、`source`。不同前端不能用同一个原型文件。
3. 页签的 `surface` 取 Luz-Project 的使用端。`--project-tabs` 的映射是：`miniapp` → `miniprogram`，`admin` → `web-admin`，`website` → `website`，`h5` → `web-admin`（02 文档里手机页挂在后台使用端下；项目的使用端不同就改生成的 JSON）。
4. 路径、导航结构、页面清单写进“前端规范”的“页面与路径”，不写进前端页签。
5. 用 `dev_documents._prototype_errors` 校验每个原型文件；构建后用 `audit_rendered.py --library luz-kit` 在真实浏览器里逐页核对控件都落在带 `data-cid` 的库组件里。`test_prototype_suite.py` 对示例的两个原型跑了前者和 Luz-Project 的前端页签校验。

## 四、Luz-Project 对原型的硬检查与本参考实现的对应

| Luz-Project 的要求（`dev_documents.py`） | 本参考实现怎么满足 | 验证 |
|---|---|---|
| 文件不小于 120 KB | 引擎、组件库、模板封成一个文件，示例 1.4 到 2.1 MB | `test_prototype_suite.py` 的 LuzProjectTest；外壳对 `file` 系统不足时警告 |
| 减少动态效果分支（`prefers-reduced-motion`） | 引擎样式里 `@media (prefers-reduced-motion: reduce)` 与 `html[data-reduce="1"]` 两条分支等价，系统偏好与面板开关都生效 | 同上；`test_prototype_mini.py` 测开关 |
| 对话框角色（`showModal` 或 `role: 'dialog'`） | 弹层与确认框用原生 `<dialog>` 的 `showModal()`，带 `role="dialog"`、`aria-modal` 和焦点陷阱 | 同上；`test_prototype_mini.py` 测焦点陷阱 |
| 场景配置面板（`UI.demo(` 或 `K.panel(`） | 引擎里有字面量 `K.panel(`，左栏有页面目录、外观配置、场景（本页状态、业务场景、流程直达、全局：网络、减少动态、角色、重置演示数据） | 同上 |
| 库组件种类数不少于 6（按 `luz-kit` 的类名前缀数） | 页面由带编号的库组件拼装，示例里是小程序 120 种、后台 170 种 | 同上 |
| 手机宽度可完整操作，无横向页面滚动 | 引擎在窗口小于约 910 时去掉三栏，手机框按比例缩放，后台菜单收进抽屉；390 宽下可点 | Luz-Project 没有自动检查；本测试在 390 宽的 iframe 里量横向滚动并点标签栏，`test_prototype_mini.py` 另有 390 与桌面宽度 |
| 文件不连网、没有外部字体和网络请求 | 素材全部 data URI，字体用系统字体 | 浏览器测试里记录全部请求，只允许 file、data、blob、about |
| 不同前端不能用同一个原型文件；页签名不能重复；小程序 `kind` 只能是 `phone` | 外壳逐条校验，报错用中文 | `BadInputTest` |
| `library` 必须登记且适合这一端 | 默认 `luz-kit`，校验与 Luz-Project 同口径（库的 surfaces 与 kind 对应） | `BadInputTest` |
| 演示时钟固定 | 状态栏时间来自规格的 `device.time`，库里的日期写死 | 未单独测 |

## 五、不满足的，和需要 Luz-Project 一侧改的

**本参考实现不满足（要么补，要么放宽 Luz-Project 的措辞）**

1. 动效时长档：Luz-Project 要求 100、150、200、300 毫秒四档、退出取进入的 70% 到 80%。原型里实际用了 .12、.15、.18、.2、.22、.25、.28、.3、.32、.35、.4、.5 秒等（组件库与引擎的取值），退出时长没有逐项核对。Luz-Project 的校验器不查这一条，所以不会拦，但文档措辞与实际不一致，二选一。
2. 场景面板的“模块显示”：Luz-Project 要求每类含页面直达、模块显示、场景；引擎有页面目录和场景，没有按模块显示或隐藏的开关。
3. 各前端的原型共用同一份演示数据：两个示例各有自己的数据，引擎和外壳都没有跨原型共享的机制。
4. 示例的页头副标题写着“由模板、规格与组件库编号拼装的示例”，项目里要换成产品自己的说明或留空（规格的 `meta.subtitle`），Luz-Project 要求成品页面不写工具名。
5. 原型文件自己过不了 `check_document.py --allow interface`（小程序 18 项、后台 30 项，类别是装饰渐变、深色或饱和填充、状态栏对比度等）。它们是原型外壳与引擎的外观取舍，与 `check_document` 的界面规则不一致；Luz-Project 目前只对文档跑这个检查，不挡。要不要让两边一致，需要决定。外壳文档本身零错误；`--inline` 版多出的一类错误（`font-size:0`）来自内嵌的原型文本，不是文档自己的。
6. 表格转卡片：Luz-Project 要求窄屏表格转卡片，后台模板是否都做到，本测试没有逐项验证。

**需要 Luz-Project 一侧改（本任务不改，由你统一处理）**

1. `references/dev-documents.md` 原型做法的最后一条还写着“现有的两个底座原型是上一代手写套件做的……待用组件库重做”：现在有 `luz-kit` 的模板和生成器，改成指向 `prototype-templates` 与本页。
2. `scripts/dev_tabs.py` 的 `TAB_JS` 没有 `beforeprint`：打印时没访问过的页签里是空的 iframe，建议像外壳一样在打印前载入全部原型。
3. `TAB_CSS` 的 `.tabs` 用 `flex-wrap: wrap`：手机宽度下页签多了换成好几行，外壳改成横向滚动；iframe 高度 Luz-Project 固定 900 与 860，外壳随窗口取 `min(height, max(560px, 窗口高度 - 150px))`。可选。
4. “手机宽度可完整操作”只写在文档里，校验器不查；可加一项：真实浏览器 390 宽打开每个原型，页面无横向滚动、标签栏可点（`test_prototype_suite.py` 的 390 宽测试可以直接借用）。
5. `UI_SURFACES` 里没有手机网页（h5）这一类使用端：外壳的 `h5` 页签只能挂到 `web-admin`；如果项目里有独立的手机网页使用端，要加。
6. 如果要交付单文件的 02 文档，`prototype_html` 要支持把原型放进 `srcdoc`；现在只支持 iframe 同目录引用。可选。

## 六、测试

`py -X utf8 scripts/test_prototype_suite.py`：生成（iframe 与 `--inline`）、`--check`、坏输入逐类报错、规格构建失败原样带出报错、Luz-Project 的原型校验与前端页签校验（没有 Luz-Project 就跳过）、`check_document.py --allow interface`、隐私与行业字样；浏览器部分用 Playwright 加 Microsoft Edge（没有就跳过并写明）：无控制台错误、页签数量与名称、切页签才加载、重新载入与在新窗口打开、键盘与 `#tab=` 直达、每个页签一个原型框、原型能点、390 宽页签条横向滚动且不撑破、打印展开、深浅外观、内嵌版同样可用。
