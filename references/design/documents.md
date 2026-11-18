# 文件排版

Word、Excel、幻灯片、阅读 HTML、PDF 按各自读者、媒介和内容排版。按 [成品要求](hard-rules.md) 保留必要的文字、数据、依据与可编辑结构。

## 按类型分别处理

| 类型 | 读取 | 生成器 | 布局重点 |
|---|---|---|---|
| Word | `context.py docx` | `make_docx.py`；正式分页版 `make_docx_paginated.py` | 样式、标题级别、段落与表格、页眉页脚、分页 |
| Excel | `context.py xlsx` | `make_xlsx.py` | 字段分组、数据类型、数值格式、可编辑性、打印 |
| 幻灯片 | `context.py slides`、[演示设计](slides.md) | `templates/documents/slides/build_slides.py` 或演示文稿工具 | 每页一个主标题，按用途选多色主题与授权模板 |
| 阅读 HTML | `context.py reading-html` | `make_summary.py` | 版心、行长、章节、带标题的图表、引用 |
| PDF | `context.py pdf-markdown` | `make_table_pdf.py`、`make_showcase.py` 或相应源文件生成器 | 字体、断行、跨页、检索、图像与最终纸面 |

先分类型，读规则卡与真实模板，再生成。模板只是骨架，与规则卡冲突时按规则卡。

## 本库模板

`templates/documents/` 按类型分五个文件夹，每个模板有编号（`DC-WD`、`DC-XL`、`DC-SL`、`DC-PD`、`DC-RD`）、一份描述文件（`specs/`）、一份样例（`samples/`），另有可复用块（`DC-WD-P01` 等，片段在 `specs/parts/`）。

| 文件夹 | 内容 |
|---|---|
| `word/` | 方案书、合同、报告、会议纪要、公文、制度、使用说明、报价函 |
| `excel/` | 报价单、功能清单、确认表、台账、验收表、排期表、预算表、订单导出、可筛选导出、选型清单 |
| `slides/` | 工作汇报、方案提案、培训课件、产品介绍、门店路演、季度复盘；自带 `build_slides.py` |
| `pdf/` | 表格目录、系统图册、方案、报告 |
| `reading/` | 阅读报告、阶段汇总页、方案说明、图文文章、系统架构与技术方案阅读页；`system-architecture.html` `system-design.html` `writing-article.html` 与 `dev/` 是供 System、Writing、Dev 渲染的真实外壳 |

- 打开 `templates/documents/documents.html` 看全部模板；`template_registry.py show DC-WD-002` 取描述文件、样例、生成与检查命令。
- 样例由生成器的内部渲染函数合成，只作版式参考，**不是客户成品**；正式交付必须走正式命令与前置检索、模板选择门禁。样例里的价格、金额一律留空，日期留空，业务条款只是示例。
- 每类文件夹的 `README.md` 写了怎么换内容、已知限制和检查命令。

## 版式原则

- 按信息结构排版：比较才用表格，关系才用图；不把所有段落转成卡片或强制两栏。
- 字体、版心与单位优先现有文件和正式要求；App 控件尺度与海报字级不进入文件默认规则。
- 内容依据与成品检查遵循 [内容依据与成品检查](../document-evidence.md)：每个关键主张有依据，用户事实、外部事实、实测、推导与未知分清。

## 验证

- 读取渲染成品，检查溢出、孤行、标题与正文断开、页码、裁切与导出一致。
- 表格计算、分页、图表口径与来源分别核验；Word、Excel、幻灯片、HTML、PDF 各自渲染检查，不能拿其中一种预览替代其余格式。PDF 再导出后核对实际页面。
- UX 看检索、比较与连续阅读是否清楚；DX 看样式、字段、公式、图表数据和导出链能否维护；AX 看标题结构、真实文本、表头与数据类型能否提取，避免整份文件只剩截图。
- 检查器：`check_document.py`（Word、Excel、HTML）、`check_pdf.py`、`check_contrast.py`。

结合用户原始内容确定信息顺序，复用对应模板与生成器。需要补充外部文件规范或用户要求搜索时，按调用协议用 Luz-Crawl 核对。
