# 文件模板库

在 [文件模板库](documents.html)查找文字文档、表格、PPT、PDF 和阅读网页的模板与可复用块。生成模板附带描述文件和示例。[PPT 分类](documents.html#ppt)展示中文商务原件，可预览内页、下载和查看授权。

[PPT 页面布局图谱](slides/PPT页面布局图谱.pdf)可按标题、封面、双层布局、圆形排列、架构图、图表和收尾等任务查看完整示例。

模板是骨架。具体成品先读对应规则卡，规则卡与模板冲突时按规则卡改。

## 目录结构

```
templates/documents/
  documents.html      按类型浏览、搜索与下载，由 scripts/build_documents_index.py 生成
  README.md
  word/  excel/  slides/  pdf/  reading/
    README.md         这一类的用途、字段、生成与检查
    manifest.json     登记表：模板 items 与可复用块 parts
    specs/            描述文件，specs/parts/ 放可复用块
    samples/          样例文件（slides 另有 samples/previews/ 预览图）
    tools/            样例补充脚本（有的类才有）
  slides/originals/
    manifest.json     PPT 原版编号、来源、授权、版式和校验值
    files/            按发布方存放本地 PPTX 与 POTX 原件
    待筛选/           集中存放按编号命名的候选原件
    previews/         从对应原件渲染的页面预览
```

## 命名总规则

| 类型 | 目录 | 代码 | 模板编号与文件名 |
|---|---|---|---|
| 文字文档 | `word/` | WD | `DC-WD-001-中文名.docx` |
| 表格文件 | `excel/` | XL | `DC-XL-001-中文名.xlsx` |
| PPT 生成样例 | `slides/` | SL | `DC-SL-001-中文名.pptx` |
| PPT 原版 | `slides/originals/` | SL | 编号如 `DC-SL-O001`，沿用发布方文件名 |
| PDF | `pdf/` | PD | `DC-PD-001-中文名.pdf` |
| 阅读网页 | `reading/` | RD | `DC-RD-001-中文名.html` |

- 模板编号 `DC-<代码>-<三位序号>`，序号从 001 起连续，类内不重号；编号用过就不改、不复用。
- 可复用块编号 `DC-<代码>-P<两位序号>`，从 P01 起，文件放 `specs/parts/`，文件名 `DC-SL-P01-封面.json`。
- 样例文件 `samples/<编号>-<中文名>.<扩展名>`，描述文件 `specs/<编号>-<中文名>.json`，同名同编号。
- 中文名简短，不含空格和 `\ / : * ? " < > |`，是文件名的一部分，改名要同时改文件、描述文件和 `manifest.json`。

## manifest.json

```
{"type": "slides", "title": "PPT", "naming": "DC-SL-三位序号-中文名.pptx",
 "items": [{"id", "name", "use", "file", "spec", "generator", "checks", "fields", ("preview")}],
 "parts": [{"id", "name", "file", "used_in": ["DC-SL-001", ...]}]}
```

`use` 一句话写用途；`generator` 是生成命令或说明；`checks` 是检查命令列表；`fields` 是描述文件里要改的字段；`preview` 是目录页显示的预览图，可省略；`used_in` 列出用到这个块的模板编号。路径都相对这一类的目录。

## 按编号选用

1. 打开 `documents.html`，按类型标签或搜索（编号、名称、用途）找到模板，点编号复制。
2. 点“样例文件”看版式，点“描述文件”看内容结构；复制描述文件，改名并换上自己的内容。
3. 只要局部时，按块编号去 `specs/parts/` 取片段，放进自己的描述文件；块表里的“用于哪些模板”指向已经用到它的样例。
4. 按“生成与检查命令”重新生成并检查。交付说明里写明采用的编号，如“按 DC-SL-003 排版”。

采用 PPT 原版时，打开卡片上的“下载原版”，按授权保留版权与许可声明，再另存项目演示稿。也可从卡片上的发布页取得原件。见 [PPT 原版与授权](slides/commercial-sources.md)。

## 索引与目录页

```
py -X utf8 scripts/build_documents_index.py            检查并写 documents.html
py -X utf8 scripts/build_documents_index.py --check    只检查
py -X utf8 scripts/build_documents_index.py --partial  某类还没有 manifest 时跳过（编写途中用）
```

生成器检查五类模板的编号、文件、字段及复用关系，也核验 PPT 原版的发布页、授权信息和本机原件的大小与 SHA-256。新增、改名或同步本机原件后重新生成 `documents.html`。编号总表由 `py -X utf8 scripts/template_registry.py write` 更新。

## 门禁与检查

样例是模板的演示，不是可交付成品。正式交付走正式命令：

- 先读规则卡：`py -X utf8 scripts/context.py docx`（Word）、`xlsx`、`slides`、`reading-html`、`pdf-markdown`。
- 生成器：Word `make_docx.py`（正式分页版 `make_docx_paginated.py`），Excel `make_xlsx.py`，幻灯片 `slides/build_slides.py`，阅读网页 `make_summary.py`，PDF `make_table_pdf.py`、`make_showcase.py` 或相应源文件生成器；各类细节见本类 `README.md`。
- 检查：`py -X utf8 scripts/check_document.py <文件>`（Word、Excel、幻灯片、阅读网页），PDF 用 `check_pdf.py`，配色用 `check_contrast.py`；零错误才算通过，再按规则卡的清单逐页目检。
- 交付：`new_session.py` 建会话，`deliver.py` 把成品放进会话根目录，`make_summary.py` 生成汇总页；有项目的任务只把成品写进项目目录。
- 检查工具只能发现一部分问题；溢出、断行、图表口径和内容依据仍须人工看渲染结果。

目录页本身的机器检查：`py -X utf8 scripts/frontend_rules.py templates/documents` 必须 `"ok": true`。
