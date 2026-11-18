# 文字文档模板（Word）

八个基础模板，覆盖规则卡里的全部文字文档类型：方案书、合同、报告、会议纪要、公文、制度、使用说明、报价函。每个模板有一份描述文件（`specs/`，合法的 `make_docx.py` 输入）和一份由生成器渲染的样例（`samples/`）。样例用“花间集”门店的内容底稿，只作版式参考，不是客户成品。

## 命名规则

- 模板与样例：`DC-WD-三位序号-中文名`，如 `DC-WD-001-方案书.docx`；描述文件同名，扩展名 `.json`。
- 可复用块：`DC-WD-P序号-中文名.json`，放在 `specs/parts/`。
- 编号一经使用不改、不复用；新增模板接着往后排。`manifest.json` 登记全部模板与可复用块，按编号取用。

## 模板一览

| 编号 | 名称 | 用途 | 版式要点 | 样例 |
|---|---|---|---|---|
| DC-WD-001 | 方案书 | 给客户的建设方案：背景、需求、目标、方案、交付 | 封面、目录、页眉标题、页脚页码居中、全黑白、表题在上、跨页续表 | `samples/DC-WD-001-方案书.docx` |
| DC-WD-002 | 合同 | 周期订花服务合同 | 当事人、鉴于条款、第一条起的条款、签署栏、附件，页脚第几页共几页，金额大写 | `samples/DC-WD-002-合同.docx` |
| DC-WD-003 | 报告 | 门店经营分析报告 | 结论与建议在最前，数据表带单位与口径，封面、目录、全黑白 | `samples/DC-WD-003-报告.docx` |
| DC-WD-004 | 会议纪要 | 门店周例会纪要 | 会议信息表、议题、决定事项表（事项、责任人、完成时间） | `samples/DC-WD-004-会议纪要.docx` |
| DC-WD-005 | 公文 | 备货与配送工作通知 | 三号仿宋、黑体楷体分层、主送机关、附件说明、署名与成文日期、一字线页码 | `samples/DC-WD-005-公文.docx` |
| DC-WD-006 | 制度 | 门店会员管理办法 | 第一章、第一条编号，总则、职责、规定、流程、附则 | `samples/DC-WD-006-制度.docx` |
| DC-WD-007 | 使用说明 | 门店收银台使用说明 | 封面、目录、步骤列表、规则表与常见异常表，全黑白 | `samples/DC-WD-007-使用说明.docx` |
| DC-WD-008 | 报价函 | 节日花礼报价函 | 报价明细表金额右对齐并带合计行，商务条款，报价单位 | `samples/DC-WD-008-报价函.docx` |

001、003、007 是客户正式文档，按规则卡“客户正式文档”：封面无页眉页脚页码，目录独立一页用罗马数字，页眉只放文档标题，页脚页码居中，全文黑白，每张表有表题且写在表上方，表跨页时下一页写“续表 N”并重复表头。002、004、006、008 沿用“文字文档”通用版式（微软雅黑，表头浅底取 `florist` 主题浅色）。005 按《党政机关公文格式》。

## 可复用块

每个块是 spec 里的一段 JSON 片段（`specs/parts/`），复制到目标模板的 spec 对应位置即可。

| 编号 | 名称 | 放在 spec 的位置 | 用在 |
|---|---|---|---|
| DC-WD-P01 | 封面样式 | 顶层 `style`、`mono`、`cover` | 001 003 007 |
| DC-WD-P02 | 目录与页眉标题 | 顶层 `toc`、`header_text` | 001 003 007 |
| DC-WD-P03 | 标题层级与编号 | 顶层 `number_format`，`sections[].blocks` 里的 `sub` | 001 003 005 007 |
| DC-WD-P04 | 正文与列点 | `sections[].blocks` 里的 `p`、`items` | 001 003 006 007 008 |
| DC-WD-P05 | 表题与续表 | `sections[].blocks` 里的 `table` | 001 003 007 |
| DC-WD-P06 | 金额表与合计行 | `table` 加 `money_cols` | 002 003 006 008 |
| DC-WD-P07 | 合同页脚 | 顶层 `type: contract`、`number` | 002 |
| DC-WD-P08 | 当事人与鉴于条款 | 合同顶层 `parties`、`preamble` | 002 |
| DC-WD-P09 | 条款编号 | `sections[].heading` 加 `items` | 002 |
| DC-WD-P10 | 签署栏 | 合同顶层 `signature` | 002 |
| DC-WD-P11 | 附件页 | 顶层 `attachments` | 002 005 |
| DC-WD-P12 | 会议信息表 | 纪要顶层 `meta` | 004 |
| DC-WD-P13 | 决定事项表 | 纪要 `sections[]` 的 `table` | 004 |
| DC-WD-P14 | 公文要素 | 公文顶层 `official`，首尾两段 `paragraphs` | 005 |
| DC-WD-P15 | 制度章条 | `sections[].blocks` 里的 `sub`（章）与 `p`（条） | 006 |

## 怎么换内容

只改 spec 里的这些字段，版式由生成器统一决定（`manifest.json` 的 `fields` 列出了每个模板要改的字段）。

| 模板 | 改什么 |
|---|---|
| 001 方案书 | `title`；`cover.subtitle` 与 `cover.info`（项目名称、客户名称、版本，需要日期时在封面信息里加一行）；`sections` 的章标题与 `blocks`（段落 `p`、列点 `items`、二级标题 `sub`、表 `table`）；`toc` 保持 `true` |
| 002 合同 | `title`、`number`；`parties[].fields`（甲乙方信息，空位用全角下划线）；`preamble`；各条 `heading` 与 `items`；金额写成 `{{money:数字}}`，大写由生成器算出；`signature`；`attachments` |
| 003 报告 | `title`、`cover.info`；`sections`；表里金额列写在 `money_cols`，数字用数值不用字符串 |
| 004 会议纪要 | `title`、`meta`；议题 `items`；决定事项 `table.rows` |
| 005 公文 | `title`；`official.addressee`、`official.attachment_line`、`official.signature`，并保证 `sections` 里有同样的主送机关、附件说明与署名段；`attachments` |
| 006 制度 | `title`；`blocks` 里 `sub` 写章、`p` 写条，流程步骤用 `items` |
| 007 使用说明 | `title`、`cover.info`；`sections` 的步骤 `items` 与规则表 |
| 008 报价函 | `title`；`table.rows`（商品、规格、数量、单价、小计，合计行第一格写“合计”）；`items` 商务条款；报价单位表 |

内容约束：标题单行、无标点；客户正式文档的标题不写括号说明；不写摘要、前言、编写说明、免责声明和下一步建议；金额与日期由人提供，样例里的日期一律留空（全角空格），商品价格取自内容底稿。

## 怎么生成

**正式交付**必须走生成器的正式命令，它们要求会话与“前置检索与模板选择”门禁，并登记模板选择与产物哈希：

```
py -X utf8 scripts/make_docx.py templates/documents/word/specs/DC-WD-002-合同.json out.docx
py -X utf8 scripts/make_docx_paginated.py templates/documents/word/specs/DC-WD-001-方案书.json out.docx
```

后者先用生成器排版，再经本机 WPS 文字或 Word 取回每个标题的页码和每张表的跨页位置，写入目录页码与“续表 N”，并导出同名 PDF；交给客户的是 PDF，Word 源文件留在会话 `raw`。公文版式生成器暂无，需在输出上再运行 `tools/official_post.py`。

**库内样例**由 `tools/render_samples.py` 重新生成：它直接调用生成器的内部渲染函数（`make_docx._render_document`、`make_docx_paginated._render_paginated`），不经过门禁、不写任何门禁记录，所以样例只是版式参考，不能当客户成品交付。

```
py -X utf8 templates/documents/word/tools/render_samples.py --check            # 全部重新生成并检查
py -X utf8 templates/documents/word/tools/render_samples.py DC-WD-004 --out 目录
```

## 怎么检查

```
py -X utf8 scripts/check_document.py templates/documents/word/samples/DC-WD-001-方案书.docx --allow paper --allow cover --allow header
py -X utf8 scripts/check_document.py templates/documents/word/samples/DC-WD-002-合同.docx
py -X utf8 scripts/check_document.py templates/documents/word/samples/DC-WD-005-公文.docx --allow official --allow cover
py -X utf8 scripts/check_pdf.py <导出的 PDF>
```

客户正式文档导出 PDF 后逐页看：封面无页码、目录页码与标题所在页一致、每张表有表题、跨页表上方有续表且表头重复、页眉是文档标题、页脚页码居中（目录页罗马数字，正文从 1）、全文黑白。合同核对分页、页脚、签署栏与金额大写。

## 检查结果

八份样例 `check_document.py` 零错误零警告（001、003、007 用 `--allow paper --allow cover --allow header`；005 用 `--allow official --allow cover`；其余不加参数）。001、003、007 导出的 PDF 经 `check_pdf.py` 零错误，两条警告见下。001 的功能与业务逻辑表跨页，下一页写“续表 5”并重复表头。每页已转图逐页看过。

## 已知限制

- 公文：生成器没有公文版式，样例在 `make_docx` 输出上用 `tools/official_post.py` 调整（版心、三号仿宋、黑体与楷体层次、固定行距、一字线页码、单页居右双页居左）。标题用宋体二号，未用方正小标宋（本机没有）；不含发文机关标志与发文字号（版头需套红与分隔线，规则卡要求文字全黑，未做）。主送机关紧跟标题，`check_document.py` 的“标题后须直接是标题”会误报，检查时需再加 `--allow cover`。
- 制度：生成器没有“第一章、第一条”的自动编号，样例的章用二级标题、条用正文段落手写条号；其余文档的标题编号都是 Word 自动编号。
- 页码与续表由 WPS 排版得出，用 Word 打开后版面可能略有出入，右键更新域即可刷新目录。WPS 导出的 PDF 没有标签与结构树，`check_pdf.py` 给两条警告；声明可访问时需另行处理。
- 表格列对齐由生成器按内容判断：整列不超过二十二字且不换行的文字列居中，换行的列左对齐，金额列右对齐；句子型短列因此可能居中。需要左对齐时给 `widths` 让该列变窄到换行。
- `make_docx.py` 命令内置的检查对有封面的文档只带 `--allow paper`，封面信息行（版本）和页眉标题会被误报；客户正式文档检查要自己加 `--allow cover --allow header`。`make_docx_paginated.py` 命令本身不运行检查。
- 一张表在 WPS 里分成两次以上续页时，后续页偶尔出现只有一行的续表；样例的表格已避开，长表自测时看一眼。
- 合同条款、违约金比例、会员权益、报价单价都只是版式示例，正式使用前必须由业务与法务按真实内容改写和确认。
