# 成熟组件优先的前端实现

App 与 Web 前端默认直接构建完整成品：先检查现有工程、依赖、品牌与用户要求，已有合适组件继续使用；需要新依赖时读官方文档与许可并固定版本。按能力选组件，按内容设计完整页面；组件本身不是整页构图。组件与模板怎么选见 [组件](design/components.md)。

## 起点

复用前按已确认的页面模块和功能控件逐项对照。框架可以决定组件的实现形式，业务含义、选项、目的地和语义阅读顺序来自功能说明。对带有 `page_structure_version` 的需求包沿用 System 的检查器。对照成品检查每组的动作和可见结果，纯视觉替换也保留键盘及触屏操作。

| 起点 | 命令 | 说明 |
|---|---|---|
| 本库 HTML 模板 | 复制 `templates/app` 或 `templates/web` 的页面与 `kit`，按编号取组件 | 定构图与组件；交付运行成品时随工程一起纳入下面的检查 |
| 零工程 | `scripts/frontend.py init app-task --session <会话> --stage <阶段>`（Vue 与 Vant）；`init web-workspace`（Vue 与 Element Plus） | 可运行的起点，不是强制技术栈；所选模板及其依赖写入会话 raw |
| 已有工程 | `frontend.py init existing --source <构建目录> --sources <组件来源清单> --entry <入口>` | 导入完整交付目录，沿用工程自己的构建链 |

可自由实现视觉布局、文字槽位样式、令牌与响应式 CSS。业务事件按已确认的按钮语义、数据和结果连接。成熟控件可组合、适配样式与插槽。界面必须遵守 [成品硬性规定](design/hard-rules.md)：业务弹层、抽屉与弹出选择器改为页内结构；纯信息提示按悬浮说明条款，支持悬浮、焦点、移入阅读与 Escape，不含交互控件。键盘导航与复杂行为优先成熟实现，确需自研时记录理由和针对性验证。

使用本库模板时，把所用页面与 `kit/` 里的文件复制进工程，并在 `component-sources.json` 登记：名称 `luz-design-templates`，版本取 `references/template-registry.json` 的哈希，来源为本仓库路径，许可为仓库 LICENSE，`files` 给出所用文件的 SHA-256。模板里的素材清单在 `kit/assets/manifest.json`。

## 来源与包

组件来源记录名称、固定版本或提交、官方出处、许可文件、实际代码与使用位置。源码复用、基于组件的原创组合、视觉参考分别标明；引用库名或加载一个未使用的脚本不能证明复用，审阅实际调用与页面控件。保持可复现：保留源文件、锁文件或本地运行时与运行方式，打包版使用本地依赖，离线演示不临时依赖 CDN。第三方字节变化需重新核实来源，原创组合变化可更新封存与审阅。

`component-sources.json` 是数组，每项含 `name`、固定 `version`、官方 `source`、实际 `usage`、`license` 文件路径，以及 `files`（包内相对路径到 SHA-256）。许可证与实际采用的代码都在包中。

复用 Vant、Element Plus 等组件时核对默认、悬停和选中底色。页面使用白色，组件可沿用库的品牌配色，或按项目调整纯色与渐变。头像槽与错误回退传入图形图标，图标字体替换为图形组件。检查计算样式及实际图片，见[前端背景、头像与图标](design/hard-rules.md#前端背景头像与图标)。

已有工程先准备完整交付目录：构建结果、`project-source/` 中的可编辑源码与锁文件、原始构建日志和 `build-record.json`（含 `command`、`toolchain`、`exit_code`、`source_files`、`lockfile` 与 `log: {path, sha256}`）。不复制密钥、`.env` 与 `node_modules`；仅有 dist 的压缩包不算源码交付。

## 封存、审阅与检查

1. `frontend.py seal <包> --session <会话>` 更新成品字节，清除旧审阅绑定。
2. 实际查看页面并操作后写 `review.json`，`frontend.py review <包> --file <审阅>` 绑定当前包、截图与行为记录；`frontend.py check` 复核。修改后旧截图不能给新文件背书。
3. 完成包由 `ui_package.py check|export` 统一检查与导出，源码与许可随包保留。

审阅输入：`bundle_sha256`、`reviewer`、`component_usage`、`limitations`、`blocking_findings`，以及 `observations: [{viewport, finding, screenshot:{path,sha256}}]` 与 `interactions: [{action, result, evidence:{path,sha256}}]`。证据先存于会话 raw，再由 review 命令复制入包。必须实际看图与操作后填写，脚本不生成“审美通过”，审阅的检查字段描述真实行为。

另需：
- `generated-assets.json` 记录原图指纹、派生步骤及实际用图指纹。起步工程携带清单与使用的素材。原图、请求和回执保存在制作会话。已有工程采用生成素材时登记相同信息，`loaded_assets` 记录浏览器实际加载的图。
- `hard_rules: {sha256, reviewed, violations}`：`reviewed` 取 `frontend.py` 的 `REVIEW_RULES` 全部机器标识，`violations` 必须为空；规则哈希或素材字节变化会使旧审阅失效。
- `experience_axes`：UX、AX、DX 三个独立对象，各含 `status: verified`、真实 `observed`、`limitations` 与 `evidence: [{path,sha256}]`，缺一不可。具体指标另执行中央 `quality_rules.py`，不在本技能复制阈值。
- `browser_report` 与 `quality_assessment` 两个 path 与 SHA-256 引用：浏览器报告记录当前 `bundle_sha256`、实际 `observations` 与 `limitations`；中央评估 scope 对独立设计与设计阶段为 `luz-design/design`；商业项目第二批编制工程设计说明，第三批运行原型的评估为 `luz-design/demo`，沿用 Design 的界面指标，绑定封存后 `luz-frontend.json` 的 `receipt_sha256` 与浏览器报告的 `browser_report_sha256`。缺失、陈旧或阶段错误的评估不能通过；旧包须重新封存与审阅。

字段细节见 `frontend.py` 的 `validate_review`；脚本检查不能代替实际看图。完整审阅方法见 [审阅](design/review.md)。

## 项目与独立调用

项目已有 `ui-requirements.json` 时，用 `--requirements` 绑定它，逐项覆盖页面、数据、动作、权限与恢复；交互记录另给 `covers: {page_ids, action_ids, journey_ids}`。视觉实现不得静默改变业务。独立 UI 任务从当前请求形成简短需求即可，不必先建完整项目或调用 System。

缺服务端的前端演示用明确的本地数据，不伪造上线能力；主要操作真实改变演示状态，错误、无结果、恢复与响应式按任务检验。

UX 看任务结果，DX 看复现与维护，AX（Agent Experience）看可观察的动作与数据；无障碍独立检查。

旧 `component_ui.py` 的 HTML 片段与 vue-vant 计划格式只用于维护已登记的产物，其 hashes、source、mounts、browser、review 字段保持兼容；新工作走上面的默认流程。
