---
name: luz-design
description: 设计、实现或改进 App、Web 前端界面，制作海报和 PowerPoint 演示文稿，也处理 Word、Excel、PDF 与阅读网页的排版。提供整页与组件模板、图标排布建议和可商用演示模板来源。已有产品优先延续现有设计系统。
---

# Luz Design

App 与 Web 从已确认的逐页功能说明开始。System 规定业务模块、页内分组与上下阅读顺序、首要信息以及每个控件的用途、数据和结果。Design 将它们落实为构图、成熟组件、字阶、颜色、图标、间距、圆角与各端的状态反馈。依据不足时先核对用户简报或现有产品，涉及新的业务决定交回 System。见[逐页视觉交接](references/ui-ownership.md#逐页视觉交接)和[界面视觉规范](references/visual-design.html)。

把真实内容做成可用的界面、海报或文档。App 和 Web 默认交付可运行的界面及源码。前端页面底色固定为纯白 `#FFFFFF`。图标、按钮和卡片的纯色或渐变按项目品牌、内容和状态选择，避开绿色及青绿色。独立填写页承接业务表单，边缘抽屉、底部面板和居中业务弹窗均禁止。头像及其回退使用图形图标，所有图标遵守[前端背景、头像与图标](references/design/hard-rules.md#前端背景头像与图标)。

[Pastel 300 色卡](references/design/foundation.md#pastel-300-强调色)和[花瓣配色示例](references/design/huaban-palettes.html)仅供参考。可以取用其中的搭配思路，也可在界面允许的色系内组合或调整渐变。

## 调用协议

商业项目的 `design` 阶段由 System 主持。Design 与 Dev 共同编制前端开发说明。第二批确认后，用 `new_session.py --project <状态根> --stage demo` 关联原型阶段，带用户走查可操作的 HTML。走查与变更回交见[商业项目交接](references/ui-ownership.md#商业项目交接)。

按入口核对该角色会经过哪些真实页面，以及每页从上到下的内容、控件、反馈与返回落点。页数和上游状态按[界面交接](references/ui-ownership.md#逐模块核对与经验)，实际构图与窄屏排列随内容选择。

承接功能设计后，按模块核对五项并落实视觉。先查[模块经验](experience/catalog.md#按模块查经验)，再按[逐模块核对与经验](references/ui-ownership.md#逐模块核对与经验)结合已确认的功能、业务字段、语义顺序、交互及流程设计各状态。五项中有参考缺口均可调用 Luz-Crawl，业务决定交 System，视觉实测与采用依据用 `experience.py note` 写回本技能的经验 Markdown。

独立任务用 [会话与交付](references/session-delivery.md)。有项目上下文时接入[项目流程](../Luz-Project/references/skill-architecture.md)。

1. 运行 `python -X utf8 scripts/context.py list`，读所选规则卡和[成品要求](references/design/hard-rules.md)。`new_session.py` 按所选类别开会话，海报使用 `--standalone-poster`。在简报写使用者、主任务、内容和要检查的状态。
2. 按原始请求选择[阶段依据](../Luz-Crawl/references/evidence-policy.md)。项目或生成器需要记录时依[前置检索](../Luz-Crawl/references/preflight.md)完成 `run` 与 `check`，联网先核对实际正文或图像再 `conclude`。
3. `template_library.py list/select` 将模板绑定到实际路径。按所选类别的生成器制作，登记最终哈希，`deliver.py` 或 `publish.py` 复核。正式文档按[内容依据与成品验收](references/document-evidence.md)。
4. 用真实内容和目标尺寸检查成品。前端逐个点击标签，核对落地页首屏从业务内容开始，按[界面导航](references/design/hard-rules.md#界面导航)删除标签名称及介绍。继续走主要流程、状态与无障碍检查，项目的 UX、AX 和 DX 规则用 `quality_rules.py list/plan` 选取并 `check`。
5. BRIEF 写“采用的规则”和“本次沉淀”，用 `experience.py note` 更新同键经验。只适用于项目、技能维护或已写入规范的经验分别用 `--scope project`、`--scope maintenance`、`--codified`。

## 按产出选规则

- **App** 读 [移动端](references/design/app.md)和 [App 端设计规范 PDF](references/design/handbooks/App端设计规范.pdf)，**Web** 读 [网页](references/design/web.md)和 [Web 端设计规范 PDF](references/design/handbooks/Web端设计规范.pdf)。按[界面分工](references/ui-ownership.md)承接 System 的页面与动作。先看 `index.html` 和页面示例，再按[组件复用](references/component-reuse.md)和[交互合同](references/design/interaction-contract.md)做到代表任务可操作。素材许可见[图像与素材](references/image-assets.md)。新工程可用 `frontend.py init app-task|web-workspace`，已有工程沿用原构建链。用[审阅](references/design/review.md)记录实际成品。
- **数据范围与动效**。按[界面导航](references/design/hard-rules.md#界面导航)把账号、时间和类别切换放在受控数据上方。文本框、可点击卡片与悬浮数据提示按[焦点与可访问性](references/design/foundation.md#焦点与可访问性)处理。需要空间层次时可复用 [Three.js 示例](references/design/motion.md#threejs-空间动效)。
- **数据看板** 读 [数据看板的图表、配色与版式](references/design/patterns.md#数据看板)。在整页核对指标与业务入口的唯一性。
- **海报** 读[构图与传播尺寸](references/design/poster.md)。
- **Word、Excel、PDF、阅读页** 读[文件排版](references/design/documents.md)。**PPT** 读[演示设计](references/design/slides.md)和 [PPT 演示设计规范 PDF](references/design/handbooks/PPT演示设计规范.pdf)，在[文件模板库的 PPT 分类](templates/documents/documents.html#ppt)打开精选的中文商务原版。

修改技能后运行 `validate_skill.py --package-only`。
