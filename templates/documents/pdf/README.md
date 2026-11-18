# 便携式文档模板（PDF）

四个基础模板：表格目录、系统图册、方案、报告。每个模板有一份描述文件（`specs/`）和一份样例 PDF（`samples/`）。样例用“花间集”门店的内容底稿，只作版式参考，不是客户成品。

## 命名规则

- 模板与样例：`DC-PD-三位序号-中文名`，如 `DC-PD-001-表格目录.pdf`；描述文件同名，扩展名 `.json`（报告另有同名 `.md` 正文）。
- 可复用块：`DC-PD-P序号-中文名`，放在 `specs/parts/`，JSON 片段或 Markdown 片段。
- 编号一经使用不改、不复用；新增模板接着往后排。`manifest.json` 登记全部模板与可复用块。

## 模板一览

| 编号 | 名称 | 用途 | 生成器 | 样例 |
|---|---|---|---|---|
| DC-PD-001 | 表格目录 | 横版表格目录：商品分类清单、业务线与门店清单、会员等级 | `make_table_pdf.py` | `samples/DC-PD-001-表格目录.pdf` |
| DC-PD-002 | 系统图册 | 总体架构、功能模块、依赖矩阵、订单泳道、部署架构，图加说明表 | `make_showcase.py`（atlas） | `samples/DC-PD-002-系统图册.pdf` |
| DC-PD-003 | 方案 | Word 排版后导出的建设方案：封面、目录、页眉标题、页脚页码居中、全黑白 | `make_docx_paginated.py` | `samples/DC-PD-003-方案.pdf` |
| DC-PD-004 | 报告 | Markdown 来源的活动复盘报告：结论在前，表题在上，金额右对齐 | `tools/md_to_pdf.py`（库内工具） | `samples/DC-PD-004-报告.pdf` |

版式要点：

- 001 横版 A4，整张表四角 12 像素圆角，每个续页片段也独立圆角；表头与对象名列用 `florist` 主题浅色；主标题、章节标题与分组标题共用版心左边线；中文只在词间换行，`keep_together` 保护行业词。
- 002 页面顶部不放标题，章节编号“一、总体架构”，字重只用常规；每层、每条泳道、每个区域一种色相，连线统一深色；表头浅底、外框发丝线加圆角，表头与本列同向。
- 003 与 Word 客户正式文档同一版式，见 `../word/README.md`；PDF 是这份 Word 导出的，不手工拼接。
- 004 阅读型版式：字阶取 `references/md-type.css` 母本的打印档（正文 11 磅，一级标题 22 磅），二级标题下一道细线，三级标题用主题按下阶，表头浅底，页脚页码居中。

## 可复用块

| 编号 | 名称 | 放在 spec 的位置 | 用在 |
|---|---|---|---|
| DC-PD-P01 | 分组目录表 | `sections[]`，带 `groups` 的目录章 | 001 |
| DC-PD-P02 | 句子型清单表 | `sections[]`，带 `heads`、`widths`、`fill` 的清单章 | 001 |
| DC-PD-P03 | 分词保护词表 | 顶层 `keep_together` | 001 004 |
| DC-PD-P04 | 分层架构图 | `sections[].blocks`，`figure: arch_layers` | 002 |
| DC-PD-P05 | 泳道图 | `sections[].blocks`，`figure: swimlane` | 002 |
| DC-PD-P06 | 部署图 | `sections[].blocks`，`figure: deployment` | 002 |
| DC-PD-P07 | 图册表格 | `sections[].blocks`，`type: table` | 002 |
| DC-PD-P08 | 依赖矩阵 | `sections[].blocks`，`type: matrix` | 002 |
| DC-PD-P09 | 封面与目录 | 顶层 `cover`、`toc`（Word 导出方案） | 003 |
| DC-PD-P10 | 方案规则表 | `sections[].blocks` 里的 `table` | 003 |
| DC-PD-P11 | 结论要点 | Markdown，第一个二级章节 | 004 |
| DC-PD-P12 | 表题与表格 | Markdown，表前一行写“表 N　标题” | 004 |

## 怎么换内容

| 模板 | 改什么 |
|---|---|
| 001 表格目录 | `title`、`theme`（按主题与行业从 `references/themes.json` 选，不套同一种颜色）；`sections` 的 `heading`、`label`、`heads`、`widths`、`groups[].rows[].cells`；`keep_together` 写要保护的行业词；每格文案逐项写，不设统一字数 |
| 002 系统图册 | `title`、`theme`；`figure` 的 `data`（层、节点、连线、泳道、步骤、区域）；表的 `columns`、`rows`、`widths`；数据来自项目事实，不手画 |
| 003 方案 | 同 Word 方案书：`title`、`cover.info`、`sections` 的 `blocks` |
| 004 报告 | 改 `specs/DC-PD-004-报告.md` 的正文与表格，`title`、`theme`、`keep_together` 在同名 JSON；第一行写 `# 主标题`，随后直接是 `## 章节`，标题最多三级，表格不超过六列，列表不超过两层 |

内容约束：标题单行、无标点；每张表有表题；不写摘要、前言、阅读指引、说明与建议；日期与金额由人提供，样例里不放日期。

## 怎么生成

**正式交付**走生成器的正式命令，它们要求会话与“前置检索与模板选择”门禁，并登记模板选择与产物哈希，产物写到会话 `raw`，再用 `deliver.py` 放置成品：

```
py -X utf8 scripts/make_table_pdf.py templates/documents/pdf/specs/DC-PD-001-表格目录.json out.pdf
py -X utf8 scripts/make_showcase.py templates/documents/pdf/specs/DC-PD-002-系统图册.json out.pdf --html out.html
py -X utf8 scripts/make_docx_paginated.py templates/documents/pdf/specs/DC-PD-003-方案.json out.docx
```

003 先生成 Word，再经本机 WPS 文字或 Word 排版并导出同名 PDF，交给客户的是这份 PDF。004 目前技能没有 Markdown 到 PDF 的生成器，`tools/md_to_pdf.py` 是库内工具：Markdown 先过 `check_document.py`，转成阅读页 HTML（取 `md-type.css` 母本与主题浅色），Edge 导出带书签与页码的 PDF，再用 `make_table_pdf.check_pdf` 核对。它不经过门禁，正式交付仍要按规则卡完成前置检索与模板选择登记。

**库内样例**由 `tools/render_samples.py` 重新生成：它直接调用生成器的内部函数（`make_table_pdf` 的分词、分页、导出与检查，`showcase.build` 与 `make_showcase.export_pdf`，`make_docx_paginated._render_paginated`），不经过门禁、不写任何门禁记录，所以样例只是版式参考，不能当客户成品交付。

```
py -X utf8 templates/documents/pdf/tools/render_samples.py              # 全部重新生成并检查
py -X utf8 templates/documents/pdf/tools/render_samples.py DC-PD-002 --out 目录 --work 过程目录
```

## 怎么检查

```
py -X utf8 scripts/check_pdf.py templates/documents/pdf/samples/DC-PD-001-表格目录.pdf
py -X utf8 scripts/check_document.py templates/documents/pdf/specs/DC-PD-004-报告.md
```

`check_pdf.py` 核对嵌入字体、字体族（微软雅黑文档只许微软雅黑，Word 导出的正式文档许宋体、黑体加 Times New Roman）、每页文字层、书签与页面尺寸；声明可访问时加 `--accessible`。脚本判断不了的要逐页看：001 看标题左边线、每个表格片段的四角、行业术语断行与单字末行；002 看连线是否穿过节点、编号圆标是否压住组名、同一列对齐、大块空白；003 看封面无页码、目录页码与标题所在页一致；004 看分页、单字末行与表格对齐。

## 检查结果

四份样例 `check_pdf.py` 零错误；001、002、004 零警告，003 两条警告（见下）。001 的 HTML 过 `check_document.py` 零错误一条警告（生成器自带的阅读页只有 16 像素正文、没有桌面字号），002 的展示页零错误零警告，004 的 Markdown 与 HTML 都零错误零警告，003 的 Word 零错误。002 的非末页占满率 78% 至 98%，末页 39%。每页已转图逐页看过。

## 已知限制

- 003 与 Word 客户正式文档相同：页码与续表由 WPS 排版得出，PDF 没有标签与结构树（WPS 不提供），`check_pdf.py` 给两条警告；声明可访问时需另行处理。
- 004 的生成工具不是技能的生成器，是本库为样例写的一个小转换器，只支持标题、段落、一至两层列表和竖线表格；复杂 Markdown 需要先在这里补。样例的 PDF 由 Edge 导出，带标签与书签。
- 001 的分页由 `make_table_pdf` 按实际行高决定，分组较多时可能在页面之间留出空白或出现只有两行的续页片段；调整分组顺序或每格文字长短可以改善，样例已调到均衡。
- 002 的图由生成器按数据自动排版：每层节点不超过六个，节点名宜四个汉字以内、作用句宜六个汉字以内，否则文字会折行；连线较多时先减少连线再看图。
- 001、002 的表格列宽与对齐按内容判断，句子型短列可能居中；用 `widths` 与 `fill` 调整。
- 样例里的价格、会员等级、营业时间、统计数字只是内容底稿，正式使用前由业务提供真实内容。
