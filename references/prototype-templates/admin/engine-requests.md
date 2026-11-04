# 后台模板向引擎提过的请求（已全部落地）

后台模板（`admin/`）只读 `engine/`、`schema/`、`scripts/build_prototype.py`，不改它们。第一轮交付时提了 12 条请求，并在 `admin/` 里写了绕法；引擎代理已全部实现。这一页记录“要什么、引擎怎么给、后台现在怎么用”，绕法都已删除（测试 `test_workarounds_for_old_engine_gaps_are_gone` 守着）。引擎细节见 `engine/ENGINE.md`。

| 编号 | 请求 | 引擎现在怎么给 | 后台现在怎么用 |
|---|---|---|---|
| R1 | 侧栏分组节点与多级菜单 | `nav` 里不带 `page`、带 `children` 的是分组节点，可嵌套；`K.tabs` 只含标签；生成器检查“既没有 page 也没有 children” | 菜单写成分组节点：没有图标 = 分组标题，有图标 = 手风琴父项；删掉扁平的 `group` 字段，`build_kind.py` 检查分组规则与三级上限 |
| R2 | kind 自己报出页面之间的跳转边 | kind 的 `edges(page, spec)` 钩子，生成器并进孤岛检查 | `build_kind.py` 的 `edges()` 报出行操作、批量、页面操作、待办、预警、表单 `thenNew` / `go`、详情动作、结果页按钮；规格不再手写 `links` |
| R3 | 切标签不清其他标签的页面栈 | `K.toTab(id, {keep})`，kind 声明 `keepTabStacks: true` | 后台声明 `keepTabStacks: true`；删掉“切换前存栈、切换后放回”；再点当前标签回到它的根页 |
| R4 | 弹层关闭控制与叠一层确认 | `maskClose: false`（规格 `pages[].maskClose`、`K.confirm`）、`onBeforeClose(reason)`、`K.requestClose`、`K.confirm({stack: true})` | 表单面板写 `maskClose: false` 并用 `onBeforeClose` 做“未保存先确认”；详情里的二次确认用 `stack: true` 叠在详情上；删掉摘遮罩 `data-pt-close` 与 `#ptDlg` 捕获拦截 |
| R5 | 主题色用到弹层 | 引擎应用主题时对 `#ptDlg`（及叠层的 `#ptDlg2`）也调用 `LIB.applyTheme` | 删掉 `mounted` 里给弹层补主题的代码；派生令牌仍声明在 `#root` 与 `.pt-dlg` 上 |
| R6 | 三栏宽度可配或可折叠 | `K.kind({layout(spec)})` 写 `--sh-left`、`--sh-right`；页头“左栏”“右栏”折叠按钮 | `layout: () => ({left: 264, right: 320})`；删掉自己对 `.pt-layout` 列宽的覆盖（覆盖会让折叠失效）；“预览宽度”工具保留 |
| R7 | schema 的后台字段 | 顶层 `shell`（并进 `data.shell`）、`roles[].readonly`、`navItem` 的 `children` / `group` / `hidden` / `badge`、`blocks` 项的 `id` / `name`、`pages[].maskClose`；去掉 `panel` 类型 | 外壳数据写顶层 `shell`；只读角色写 `roles[].readonly`；`readonlyRoles` 已删 |
| R8 | `K.confirm` 带字段 | `K.confirm({fields, onOk(values)})`，必填不通过不关闭，错误写在字段下 | 经营设置影响资金的修改用它（原因、验证身份）；删掉自己画的对话框 |
| R9 | 只重画一部分 | `K.render({part})` → kind 的 `renderPart(part, frame, ctx)`；元素上的 `data-fk` 恢复焦点与光标；`K.keepFocus(fn)` | 列表（`list:页面 id`）、设置（`settings`）、工作台（`dash`）走 `renderPart`；输入框与按钮写 `data-fk`；删掉自己恢复焦点与光标的代码 |
| R10 | 外壳的对比度 | `--sh-ink3` 加深到 `#5F6670`；深色目录当前项对比度修正 | 渲染审计不再有外壳项，测试里去掉对 `.ver` 的排除 |
| R11 | 目录自动分组 | 一级页没写 `tab` 也能归到自己的标签下 | 示例仍写 `tab` 和显式的 `directory`（按侧栏分组） |
| R12 | `<dialog>` 元素带组件编号 | `#ptDlg`、`#ptDlg2` 自己带 `data-cid`（取面板的 `cid`） | 删掉 `AD.tagDialog` |

另外引擎新增、后台已接入：**模块显示**（场景面板每个模块一个开关，kind 提供 `modules(page)`；后台的模块是工作台的指标卡与各模块、`blocks` 的每一项、`custom` 内容）；弹层关闭前 150 毫秒的退出动画（`.closing` 类）；动效时长四档（`--mo-100 --mo-150 --mo-200 --mo-300`）；深色是真令牌，不再用滤镜。

## 还留在后台这边的东西（不需要引擎）

- 列设置、列宽拖拽、地址栏参数（`page`、`page_size`、状态标签）、删除后的 5 秒撤销：没做，引擎路由只同步页面 id。
- 库里整页组件（日程周视图、员工排班表）自带示例数据，只能用 `blocks` 覆盖改文字，不接 `K.data`。
- 组件库的状态色对比度（ok 色压在 ok 浅底上 4.33:1）与日程块 20px 的触控目标，是库的已知差距，后台测试对整页都是库组件的页面不计。
