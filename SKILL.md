---
name: luz-design
description: Use for visual and layout design — the visual standards every Luz output follows (palette from official colour scales and industry themes, one font stack and type scales, flat line icons, spacing, radii and shadows, motion, writing discipline), posters, brand key visuals, campaign images and Imagegen requests, and the layout of reports, reading HTML pages, Excel sheets, Word documents (contracts, proposals, reports, minutes, official documents), PowerPoint and PDF, with document checks and builders. Product system design, UI for admin consoles, mini-programs, agents and websites, interactive prototypes and hardware belong to Luz-System.
---

# Luz Design

Luz Design owns how things look and how pages are laid out: the visual standards shared by every Luz skill, standalone visual work, and the layout of documents and files.

## Not this skill — route instead

| Request | Use |
|---|---|
| System architecture, function list, product UI for admin consoles, mini-programs, agent UIs and websites, interactive prototypes, on-site hardware selection | **Luz-System** (`D:\Codes\Luz-System`) |
| Backend, APIs, databases, deployment, launch | **Luz-Dev** (`D:\Codes\Luz-Dev`) |
| The words themselves: articles, copy, agreements, policies | **Luz-Writing** (`D:\Codes\Luz-Writing`); Luz Design lays the document out |
| Browser search and capture | **Luz-Crawl** (`D:\Codes\Luz-Crawl`) |

`new_session.py` refuses system, prototype and hardware modes and names Luz-System. Older notes that put system design, the four surface rule pages or prototypes in Luz-Design are out of date.

## Layout

```text
D:\Codes\Luz-Design\                   the skill (rules, templates, knowledge, scripts)
  SKILL.md   WORKFLOW.md   README.md   LICENSE   NOTICE
  agents\openai.yaml
  references\
    visual-design.html                 视觉设计规范: 视觉基础 (flat line style, palette and theme system, sources for colour, type and type scales, one icon set, radii and shadows, motion) → 排版基础 (spacing and grid, hierarchy and separators, writing discipline) → 视觉产出 (posters, Imagegen, references and rights) → visual problem families
    file-design.html                   文件设计规范: reading HTML, Excel, Word by document type (contracts, proposals, reports, minutes, official documents), PowerPoint, PDF, Markdown
    guidelines.css  templates.txt  themes.json  prompt-image.txt
  experience\
    catalog.md  sources.json  patterns.json      palettes, type scales, visual and document rules, research lessons
  scripts\                             check_document, check_contrast, make_xlsx, make_docx, sessions, publish, experience, validation, tests

D:\Codes\skill输出\Luz-Design\         outputs only
  NNN-名称\
    NNN-名称.html | .xlsx | .docx      the single final deliverable
    raw\                               BRIEF, prompts, references, generated images, document sources, approvals, manifest
```

Never write outputs into the skill, and never put rules, templates or scripts into the output folder. `publish.py <session> <visual | document>` copies the chosen artifact to the session root.

## Route

| Task | Read | Entry condition |
|---|---|---|
| Colour, type, icons, spacing, radii, shadows, motion for any output (including Luz-System interfaces) | [visual-design.html](references/visual-design.html) 一、二 | — |
| Poster, brand key visual, campaign image, Imagegen, reference edit | [visual-design.html](references/visual-design.html) 三 | A standalone visual session whose title names the task (海报, 主视觉, 宣传图 …) |
| Report or reading HTML, Excel, Word, PowerPoint, PDF, Markdown | [file-design.html](references/file-design.html) | Chosen format, complete source, export verification |

The rule pages define standards and judgment, not templates: derive colour, composition and structure from each request. Read [WORKFLOW.md](WORKFLOW.md) for phases and [experience/catalog.md](experience/catalog.md) before researching.

## Output baseline

- The first visible line of every HTML, Markdown, Word, PDF, spreadsheet or slide deck is the main title; the first section starts directly below it. No subtitle, summary, tags, timestamps, tool names, source counts, hashes, file paths or design-reference notes anywhere.
- Apply the deletion test (visual-design.html, 文字纪律) to every visible element. Problems are families, not word lists: anything about the output itself, reading guidance, repetition, asides, unrequested advice, pleasantries, placeholders and self-evaluation are removed in whatever wording they appear.
- Light surfaces only, one accent colour plus neutrals, one font family per file. Centre the composition: containers centred with a max width; groups of panels centred as a whole.
- Colour comes from standards, not taste (visual-design.html: 取色依据, 配色和谐; research official palettes with LuzCrawl first): choose the primary from the industry's mood (`references/themes.json`); 60-30-10 with neutrals dominant; brand, hover, pressed and tint steps from one column of an official 10-step palette, the brand step being the first that gives white text 4.5:1; marketing takes an analogous hue in tinted containers; never two saturated hues of similar chroma side by side; active controls and chart series at least 3:1; no gradient buttons. `check_contrast.py` and `check_document.py` enforce it.
- One typeface everywhere (visual-design.html, 字体与字号): every HTML file declares `"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif` in that order; documents, spreadsheets and slides use Microsoft YaHei. Nothing below 12px in HTML (interfaces and agents 12, websites and reading pages 14), including SVG labels, inline styles and text built in scripts. Two weights only (400, 600), no letter spacing, no italics, no rotated text. Type scales: reading HTML 14/16/20/24/32; product pages 12/14/16/18/22/28 with page title 32; websites up to 40/48 first-screen titles; spreadsheet 12 with an 18 pt title; Word 10.5/12/14/16/22 pt; slides 16/20/28/40 pt.
- Flat and line-based (visual-design.html: 扁平线性风格, 图形：一套线性图标): one set of stroked line icons on a 24 grid, one stroke width (1.5 px, non-scaling), round caps; emphasis from a tinted rounded block, never 3D, glossy, multi-colour or image-generated icons; illustrations are dark-grey line drawings with at most one accent; very light neutral page background, white cards with the lowest shadow; card radius 12, inputs and buttons 8; no decorative gradients, textures, glass, blobs, bevels or glows — only photo scrims and skeleton shimmer may use a gradient. One object, one icon: different objects never share a pictogram.
- Spreadsheets (file-design.html, 表格文件): build with `make_xlsx.py spec.json out.xlsx`, then `check_document.py`. One worksheet; title, header, data; Microsoft YaHei, title 18 pt and everything else 12 pt; no sequence-number column; repeated group names merged vertically, child groups inside parents; one fact per cell; pale blue header, group cells in rotating step-1 tints, light grey total row. Sheets meant for filtering, import or screen readers stay unmerged.
- Word documents (file-design.html, 文字文档, 按文档类型): build with `make_docx.py spec.json out.docx`, then `check_document.py`. A4, Microsoft YaHei, title 22 pt, headings 16/14/12, body 12 pt at 1.5 lines, tables 10.5 pt with a repeating pale header. Contracts: number, each party's details, preamble, clauses 第一条 / 1.1 / 1.1.1 covering the Civil Code Article 470 terms, money in figures and capitals, “（以下无正文）” then a two-column signature block, footer 第 X 页 共 Y 页, no placeholders. Proposals: 一、（一）1.（1）, plans, roles, budget and acceptance as tables, totals that agree. Reports lead with conclusions; minutes end with a decisions table; official documents follow GB/T 9704 only when asked.

## Imagery with the local image service

Use `D:\Codes\Imagegen\src\imagegen.py`; every request is billed.

1. Write one prompt file per image under `raw/02-visual/prompts/` from `references/prompt-image.txt`, sharing a style block (light, theme colours, no text, no logos, no identifiable faces); dry-run first.
2. Send one request at a time; a timeout gets one retry, then fall back to a vector illustration.
3. Use the image service only for photos of stores, products and environments and for posters. Icons and illustrations are flat line vectors; never generate 3D icon sheets or background textures.
4. Review every image before use; record the actual size and format.

## Sessions

~~~powershell
py -X utf8 scripts/new_session.py --name "<活动名>海报" --modes visual --standalone-poster
py -X utf8 scripts/new_session.py --name "<文档名>" --modes document
py -X utf8 scripts/publish.py "<会话目录>" document
~~~

Every approval records status, artifact path, SHA-256, time, approver and note in `raw/99-delivery/APPROVALS.json`. Scripts and the model never approve.

## Validate

~~~powershell
py -X utf8 scripts/validate_skill.py
py -X utf8 scripts/experience.py check
py -X utf8 scripts/check_contrast.py
py -X utf8 scripts/check_document.py "<delivered file>" [--allow interface | website] [--allow KIND]
py -X utf8 -m unittest discover -s scripts -p "test_*.py"
~~~

`check_document.py` is also used by Luz-System, Luz-Dev and Luz-Writing for their pages. Run it on every final deliverable; `--allow interface` applies the interface type scales, `--allow website` adds the website first-screen titles, and other kinds are only for items the user explicitly requested. Any ERROR blocks delivery; a clean run is necessary, not sufficient.
