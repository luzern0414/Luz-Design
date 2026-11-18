# 会话、检查与交付

## 会话与产物

~~~powershell
py -X utf8 scripts/new_session.py --name "<活动名>海报" --modes visual --standalone-poster
py -X utf8 scripts/new_session.py --name "<文档名>" --modes document --card xlsx      # or any kind from context.py list: docx, reading-html, slides, pdf-markdown, showcase, interface-visual …
py -X utf8 scripts/new_session.py --name "<页面名>" --modes document --project <项目目录或状态根>   # project task: results go to the project's docs
py -X utf8 scripts/add_mode.py "<会话目录>" document                                    # add document mode to a poster session (visual only with --standalone-poster)
py -X utf8 scripts/publish.py "<会话目录>" visual | document [--as NN-名称]               # a page: the summary page, or (project task) docs\02-产品开发\NN-名称.html
py -X utf8 scripts/deliver.py "<会话目录>" "<raw 下的成品>" [--as 名称] [--to 01-需求对接|03-验收交付]   # xlsx, docx, pptx, pdf, images: the session root, or (project task) the project's docs
py -X utf8 scripts/make_summary.py "<会话目录>\raw\03-documents\summary.json" "<会话目录>" --check [--project-linked]
py -X utf8 scripts/check_output_layout.py session "<会话目录>" [--project-linked]    # project "<项目目录>" checks that a project folder holds results only
~~~

- **布局。** `NNN-主题\` 根目录只放 `raw\` 和汇总页 `NNN-主题.html`；非项目任务还可放成品。`new_session.py` 在清单中写入 `output_standard`，`validate_session.py` 对此类会话执行布局检查；旧会话（两位序号、根目录多份成果、无汇总页）保持原样，只作提示。
- **UI 过程素材。** document 会话可保存 `raw/02-visual/prompts`、`generated`、令牌、候选记录和资产清单；只有 `visual-board.html` 与 `visual` 模式专用于独立海报任务。
- **生成门禁。** 正式 CLI 和公开 `make_xlsx.build`、`make_docx.build`、`make_docx_paginated.build` API 在输出前验证本阶段 Crawl 与准确模板选择。支持时传 `--session`，或设置 `LUZ_DESIGN_SESSION`，或使用真实会话祖先目录；任意目录不算会话。独立业务输出默认 `design`，独立汇总页默认 `summary`；显式阶段或 `LUZ_CRAWL_STAGE` 选择相应记录。关联项目使用声明的 Design 阶段。上游业务调用方须为所选最终目标及限定 raw 工作文件取得 `design_output_gate.verified_output_context`；传入字典或跳过标记不能授权写入。私有渲染函数只用于合成排版测试，不用于绕过业务门禁。分页 Word 直接生成 DOCX 与 PDF，运行前准确选择两个 raw 目标，两个输出均登记哈希。
- **HTML 成果**（视觉板、阅读页）用 `publish.py` 发布。真实会话模板是 `design-visual-board` 和 `design-document-page`，由 `new_session.py` 从 `references/templates.txt` 加载，不是 `showcase`。源文件与最终目标选择同一模板 ID。发布检查维护中的外壳、源和最终绑定、当前规则卡、采用的规则、新鲜的本次沉淀及 `check_document.py`；视觉批准仍须写明当前视觉板 SHA-256 和真人。内容与主题令牌可按规则卡适配，但换掉外壳只留模板名称会被拒绝。成果页即汇总页，根目录不放其它 HTML。
- **表格、Word、PowerPoint、PDF 或图片成果**检查通过后由 `deliver.py` 放置。raw 源文件须有准确模板输出哈希，最终路径另行选择同一模板；源已过期、未登记或缺最终选择时，在复制前停止。交付登记复制后的实际字节。独立会话的相对选择从会话根开始（`raw/result.xlsx` 与 `result.xlsx` 不同）；项目的 `docs/...` 指向交付目录。源文件、规范数据和过程导出留在 raw。用 `make_summary.py` 和 `raw/03-documents/summary.json` 列出成果、依据、过程文件；校验同时要求采用的规则和本次沉淀。
- **项目任务**通过关联的 Project 上下文取得目标路径。目录和命名读 [Project 项目目录](../../Luz-Project/references/project-structure.md)。Design 接收指定路径，生成并核验成品，制作源稿与检查结果留在 Design 会话 `raw/`。汇总记录项目相对路径并用 `--project-linked` 核对。
- 每项批准记录状态、产物路径、SHA-256、时间、批准人和说明；脚本与模型不得代批。台账使用 schema 3.0，阶段为 `visual`、`document`、`standalone_poster`；读取拆分前 schema 2.0 会话时忽略其 system 阶段，已批准 system 阶段、`01-system/` 目录或 system 模式均提示为 Luz-System 工作。

## 检查入口

界面包使用 `frontend.py` 与 `ui_package.py check/export`，见 [组件复用](component-reuse.md)；旧 `component_ui.py` 只维护已登记产物。

文档：`check_document.py`；PDF：`check_pdf.py` 与逐页渲染；技能包：`validate_skill.py --package-only`；规则卡：`context.py check`；经验：`experience.py check`。生成数据驱动规则页后运行对应 `render --check`。

静态扫描只覆盖它能识别的模式，不能替代真实浏览器或完整任务评审。产品 UI 的具体指标以 Project 的质量规则为准，静态扫描的字阶、圆角配额不能压过当前组件合同。

共享脚本修改前核对调用方；`context.py` 的共享核心由 `sync_rule_core.py` 管理，估价政策副本由 `sync_estimate_terms.py` 管理。没有修改共享核心时不运行跨技能覆盖。
