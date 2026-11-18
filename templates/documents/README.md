# 文件模板库

文字文档、表格文件、幻灯片、PDF、阅读网页五类文件的模板与可复用块。每个模板有编号、一份描述文件和一份用生成器做出的样例；每类还登记了可复用块，可以只取局部。视觉与 `../../kit/` 同一套：暖灰米底、雾粉主色、大圆角白卡、花卉实拍，主题色取 `../../kit/tokens.css`。

模板是骨架。具体成品先读对应规则卡，规则卡与模板冲突时按规则卡改。

## 目录结构

```
templates/documents/
  documents.html      目录页：按类型、搜索、复制编号、样例与描述文件、命令
  documents.html      目录页（单文件，数据内嵌），由 scripts/build_documents_index.py 生成，不手改
  README.md
  word/  excel/  slides/  pdf/  reading/
    README.md         这一类的用途、字段、生成与检查
    manifest.json     登记表：模板 items 与可复用块 parts
    specs/            描述文件，specs/parts/ 放可复用块
    samples/          样例文件（slides 另有 samples/previews/ 预览图）
    tools/            样例补充脚本（有的类才有）
```

## 命名总规则

| 类型 | 目录 | 代码 | 模板编号与文件名 |
|---|---|---|---|
| 文字文档 | `word/` | WD | `DC-WD-001-中文名.docx` |
| 表格文件 | `excel/` | XL | `DC-XL-001-中文名.xlsx` |
| 幻灯片 | `slides/` | SL | `DC-SL-001-中文名.pptx` |
| PDF | `pdf/` | PD | `DC-PD-001-中文名.pdf` |
| 阅读网页 | `reading/` | RD | `DC-RD-001-中文名.html` |

- 模板编号 `DC-<代码>-<三位序号>`，序号从 001 起连续，类内不重号；编号用过就不改、不复用。
- 可复用块编号 `DC-<代码>-P<两位序号>`，从 P01 起，文件放 `specs/parts/`，文件名 `DC-SL-P01-封面.json`。
- 样例文件 `samples/<编号>-<中文名>.<扩展名>`，描述文件 `specs/<编号>-<中文名>.json`，同名同编号。
- 中文名简短，不含空格和 `\ / : * ? " < > |`，是文件名的一部分，改名要同时改文件、描述文件和 `manifest.json`。

## manifest.json

```
{"type": "slides", "title": "幻灯片", "naming": "DC-SL-三位序号-中文名.pptx",
 "items": [{"id", "name", "use", "file", "spec", "generator", "checks", "fields", ("preview")}],
 "parts": [{"id", "name", "file", "used_in": ["DC-SL-001", ...]}]}
```

`use` 一句话写用途；`generator` 是生成命令或说明；`checks` 是检查命令列表；`fields` 是描述文件里要改的字段；`preview` 是目录页显示的预览图，可省略；`used_in` 列出用到这个块的模板编号。路径都相对这一类的目录。

## 按编号选用

1. 打开 `documents.html`，按类型标签或搜索（编号、名称、用途）找到模板，点编号复制。
2. 点“样例文件”看版式，点“描述文件”看内容结构；复制描述文件，改名并换上自己的内容。
3. 只要局部时，按块编号去 `specs/parts/` 取片段，放进自己的描述文件；块表里的“用于哪些模板”指向已经用到它的样例。
4. 按“生成与检查命令”重新生成并检查。交付说明里写明采用的编号，如“按 DC-SL-003 排版”。

## 索引与目录页

```
py -X utf8 scripts/build_documents_index.py            检查并写 documents.html
py -X utf8 scripts/build_documents_index.py --check    只检查
py -X utf8 scripts/build_documents_index.py --partial  某类还没有 manifest 时跳过（编写途中用）
```

检查项：五类各有 `manifest.json` 且 `type` 与目录一致；`naming` 与扩展名一致；模板和块的编号格式正确、全库唯一，序号缺号会提醒；`file`、`spec`、块的 `file`、`preview` 都存在且在本类目录内；`file` 与 `spec` 的名字是 `<编号>-<中文名>`；`use`、`generator` 非空，`checks`、`fields` 是列表；`used_in` 里的编号存在且同类。有任何错误就不写 `registry.js`。新增、改名或删除模板后必须重跑，目录页只读 `registry.js`。

## 门禁与检查

样例是模板的演示，不是可交付成品。正式交付走正式命令：

- 先读规则卡：`py -X utf8 scripts/context.py docx`（Word）、`xlsx`、`slides`、`reading-html`、`pdf-markdown`。
- 生成器：Word `make_docx.py`（正式分页版 `make_docx_paginated.py`），Excel `make_xlsx.py`，幻灯片 `slides/build_slides.py`，阅读网页 `make_summary.py`，PDF `make_table_pdf.py`、`make_showcase.py` 或相应源文件生成器；各类细节见本类 `README.md`。
- 检查：`py -X utf8 scripts/check_document.py <文件>`（Word、Excel、幻灯片、阅读网页），PDF 用 `check_pdf.py`，配色用 `check_contrast.py`；零错误才算通过，再按规则卡的清单逐页目检。
- 交付：`new_session.py` 建会话，`deliver.py` 把成品放进会话根目录，`make_summary.py` 生成汇总页；有项目的任务只把成品写进项目目录。
- 检查工具只能发现一部分问题；溢出、断行、图表口径和内容依据仍须人工看渲染结果。

目录页本身的机器检查：`py -X utf8 scripts/frontend_rules.py templates/documents` 必须 `"ok": true`。
