---
name: luz-design
description: Use for visual and layout design — the visual standards every Luz output follows (palette from official colour scales and industry themes, one font stack, type scales and seven type roles, flat line and duotone icons, layered flat illustrations, a five-level elevation system with hairlines, spacing, radii, motion, writing discipline), posters, brand key visuals, campaign images and Imagegen requests, and the layout of reports, reading HTML pages, Excel sheets, Word documents (contracts, proposals, reports, minutes, official documents), PowerPoint and PDF, with document checks and builders. Product system design, UI for admin consoles, mini-programs, agents and websites, interactive prototypes and hardware belong to Luz-System. Start every call with scripts/context.py <kind> — its rule card carries the user's preferences, lessons, the rule text, tools and checks; templates and builders are skeletons only.
---

# Luz Design

Luz Design owns how things look and how pages are laid out: the visual standards shared by every Luz skill, standalone visual work, and the layout of documents and files.

## 调用协议（每次调用都按顺序做，不可跳过）

Templates and builder scripts are the cheap path, and following them alone is how outputs miss the rules. They are skeletons. What a deliverable must look like comes from the rule pages, the user's preferences and past lessons, and the rule card puts all of that in front of you.

1. **Route.** Product screens, prototypes, system design and hardware go to Luz-System; backend to Luz-Dev; prose to Luz-Writing; web research to Luz-Crawl (table below).
2. **Read the rule card before producing anything.** `py -X utf8 scripts/context.py list` shows the task kinds (xlsx, docx, reading-html, slides, pdf-markdown, poster, interface-visual, palette). `py -X utf8 scripts/context.py <kind> [--topic 词 …]` prints the card: the user's preferences (all binding), matching lessons and facts, the rule text cut from the rule pages, the tools to use and the checks to pass. Read all of it. For anything the card does not settle, read the named rule-page section in full.
3. **Produce with the tools the card names.** Where a template or builder default differs from the card, follow the card. Re-read the named rule sections and `themes.json` for every deliverable; never ship a template's default palette and styles (check_document warns) or reuse the last project's look. Sessions get their card automatically: `new_session.py --card <kind>` saves it to `raw/00-rules/<kind>.md`.
4. **Record what you applied.** In the session BRIEF, `## 采用的规则` lists one row per rule section or preference key and how this work applies it; `publish.py` refuses a session without it, and validation flags a delivered file without it. Without a session, name the card you followed in the reply.
5. **Pass the checks on the card.** `make_xlsx.py` and `make_docx.py` run `check_document.py` on what they write and fail on any ERROR; HTML deliverables go through `check_document.py` (interfaces with `--allow interface`) before delivery.
6. **Sediment — mandatory, checked at publish.** Every call writes or confirms at least one note with `experience.py note` and lists its key in BRIEF `## 本次沉淀`; `publish.py` refuses a session whose listed keys are missing from `experience/notes.json` or were last confirmed before the session started. Without a session, run the note command before replying. What to record is in 每次调用后沉淀.

## Not this skill — route instead

| Request | Use |
|---|---|
| System architecture, function list, product UI for admin consoles, mini-programs, agent UIs and websites, interactive prototypes, on-site hardware selection | **Luz-System** (`D:\Codes\Luz-System`) |
| Backend, APIs, databases, deployment, launch | **Luz-Dev** (`D:\Codes\Luz-Dev`) |
| The words themselves: articles, copy, agreements, policies | **Luz-Writing** (`D:\Codes\Luz-Writing`); Luz Design lays the document out |
| Browser search and capture | **Luz-Crawl** (`D:\Codes\Luz-Crawl`) |

**Interface rules are split between the two skills.** How a product screen behaves is a Luz-System rule: list default views (default status, range and sort), page titles that repeat the highlighted menu item, nav groups holding one same-named item, filters, dashboards and what an export contains. Read them in [admin-design.html](https://github.com/luzern0414/Luz-System/blob/master/references/admin-design.html) and [ui-standards.html](https://github.com/luzern0414/Luz-System/blob/master/references/ui-standards.html) (local: `D:\Codes\Luz-System\references\`). How it looks stays here: type sizes (admin body and tables 14/22), density (8 px grid, row heights, first-screen rows), table alignment and cell padding, and the layout of the exported spreadsheet (file-design.html, 导出文件).

**Before any interface or visual work**, research the reference component libraries with Luz-Crawl — Ant Design, TDesign, Arco, Semi, Element Plus, Vant, NutUI, Carbon — for the component's defaults, sizes and states, and name the library and component you followed; the look still comes from visual-design.html.

`new_session.py` refuses system, prototype and hardware modes and names Luz-System. Older notes that put system design, the four surface rule pages or prototypes in Luz-Design are out of date.

## Layout

```text
D:\Codes\Luz-Design\                   the skill (rules, templates, knowledge, scripts)
  SKILL.md   WORKFLOW.md   README.md   LICENSE   NOTICE
  agents\openai.yaml
  references\
    visual-design.html                 视觉设计规范: 视觉基础 (flat style and where depth is allowed, palette and theme system, sources for colour, type, type scales and seven type roles, one icon set, layered flat illustrations, elevation and depth, motion) → 排版基础 (spacing and grid, hierarchy and separators, writing discipline) → 视觉产出 (posters, Imagegen, references and rights) → visual problem families
    file-design.html                   文件设计规范: reading HTML, Excel, Word by document type (contracts, proposals, reports, minutes, official documents), PowerPoint, PDF, Markdown
    guidelines.css  templates.txt  themes.json  prompt-image.txt
  experience\
    notes.json                                   preferences, lessons and facts from every call, upserted by key (caps 60, 120, 120)
    patterns.json  sources.json  catalog.md      curated palettes, type scales, visual and document rules, sources; catalog is generated
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
| Colour, type, icons, illustrations, spacing, radii, elevation and shadows, motion for any output (including Luz-System interfaces) | [visual-design.html](references/visual-design.html) 一、二 | — |
| Poster, brand key visual, campaign image, Imagegen, reference edit | [visual-design.html](references/visual-design.html) 三 | A standalone visual session whose title names the task (海报, 主视觉, 宣传图 …) |
| Report or reading HTML, Excel, Word, PowerPoint, PDF, Markdown | [file-design.html](references/file-design.html) | Chosen format, complete source, export verification |

The rule pages define standards and judgment, not templates: derive colour, composition and structure from each request. Read [WORKFLOW.md](WORKFLOW.md) for phases and [experience/catalog.md](experience/catalog.md) before researching.

## 每次调用后沉淀

Mandatory on every call, not only for sessions. Every call leaves at least one note behind — new or confirmed — and a session lists those keys in BRIEF `## 本次沉淀` (| 经验 key | 类型 | 一句话 |); `publish.py` checks them. Record, among others:

- **preference** — what the user stated or corrected this time (a colour, a size, a layout habit, something they dislike).
- **lesson** — a rule correction, a mistake the checks did not catch and the right way, a template default that had to be overridden.
- **fact** — a design approach that worked (palette and the steps used, type scale, layout, which component library and component was referenced), research sources and scope (which sites or documents were useful or useless, the queries used), generation parameters (Imagegen prompt block, sizes).
- **Already known and used again** — write the same key again to confirm it (`uses` +1); when the new finding contradicts it, rewrite the same key and the old text becomes `previous`. Never add a second note on the same topic.

One store, `experience/notes.json`, with the same shape and commands in Luz-System, Luz-Design, Luz-Dev and Luz-Writing:

- **Start:** `py -X utf8 scripts/experience.py search <关键词> [--kind preference|lesson|fact]` and apply what matches.
- **Before finishing:** `py -X utf8 scripts/experience.py note --kind preference|lesson|fact --key <主题> --text "<一句话原则>" [--why "<依据>"]` — preference: what the user stated or corrected; fact: a route, source or parameter that worked or failed; lesson: a rule correction or fix. The general principle, not task trivia.
- **Fields:** `key`, `kind`, `text`, `why` (optional), `uses`, `first_seen`, `last_confirmed` (YYYY-MM-DD), `previous` (`{text, replaced_at}`, only after a replacement).
- **Replace, never pile up:** the same key replaces the text (one `previous` kept, `uses` +1); the same statement under another key confirms that note. Caps: preference 60, lesson 120, fact 120; over a cap the fewest uses, then the oldest confirmation, go first. `list [--kind]` shows notes; `prune` enforces caps and lists notes unconfirmed for 180 days; `check` fails on duplicate keys or statements, missing fields, overflow and private data.
- **Public repository:** no phone numbers, emails, WeChat IDs, user-home paths, credentials, personal or client names; `note` refuses them.

Here also: curated palettes, type scales and document rules with sources go to `patterns.json` through `experience.py add <file.json>` (cap 200); `catalog.md` is re-rendered after every write.

## Output baseline

- The first visible line of every HTML, Markdown, Word, PDF, spreadsheet or slide deck is the main title; the first section starts directly below it. No subtitle, summary, tags, timestamps, tool names, source counts, hashes, file paths or design-reference notes anywhere.
- Apply the deletion test (visual-design.html, 文字纪律) to every visible element. Problems are families, not word lists: anything about the output itself, reading guidance, repetition, asides, unrequested advice, pleasantries, placeholders and self-evaluation are removed in whatever wording they appear.
- Light surfaces only (one solid brand card per screen is the exception in product UI), one primary colour used in its official steps plus neutrals — product UI may add one marketing accent and one fixed accent hue per top-level module (visual-design.html 配色, 模块点缀色) — and one font family per file. Centre the composition: containers centred with a max width; groups of panels centred as a whole.
- Colour comes from standards, not taste (visual-design.html: 取色依据, 配色和谐; research official palettes with LuzCrawl first): choose the primary from the industry's mood (`references/themes.json`); 60-30-10 with neutrals dominant; brand, hover, pressed and tint steps from one column of an official 10-step palette, the brand step being the first that gives white text 4.5:1; marketing takes an analogous hue in tinted containers; never two saturated hues of similar chroma side by side; active controls and chart series at least 3:1; no gradient buttons. `check_contrast.py` and `check_document.py` enforce it.
- One typeface everywhere (visual-design.html, 字体与字号): every HTML file declares `"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif` in that order; documents, spreadsheets and slides use Microsoft YaHei. Nothing below 12px in HTML (interfaces and agents 12, websites and reading pages 14), including SVG labels, inline styles and text built in scripts. Three weights: 400 body, 600 headings, card titles, table headers, prices and emphasis, 700 only at 22px and larger (page titles and large numbers; reading pages: the 24 and 32 titles) — never 500, 300 or 800, and headings, `th`, `strong` and `b` set to 600 instead of the browser's bold; no letter spacing, no italics, no rotated text. Type scales: reading HTML 14/16/20/24/32; product pages 12/14/16/18/22/28/32 in seven roles (七级字体角色: large number 32/700, page title 22/700, block title 18/600, card title 16/600, body 14/400 — agent messages 16 — in body ink at 7:1, secondary 14 and auxiliary 12 in secondary grey); websites up to 40/48 first-screen titles; spreadsheet 12 with an 18 pt title; Word 10.5/12/14/16/22 pt; slides 16/20/28/40 pt.
- Flat graphics, defined depth (visual-design.html: 扁平线性风格, 图形：一套线性图标, 插画：多层扁平, 层级与立体感): icons, illustrations, avatars and charts stay flat vectors — one set of stroked line icons on a 24 grid, stroke 2 px non-scaling (1.75 for 16 px icons, never thinner), round caps; duotone icon blocks (stroke in the pressed or module step, one shape filled with step 2, on a step-1 block, radius 8) for entries, metrics and empty states, single-colour strokes for navigation and buttons; layered flat illustrations (2 px dark stroke, 2–4 theme-step fills, at most one solid accent, 12–30 shapes); never 3D, glossy, gradient or image-generated icons. Depth belongs to surfaces only, from the five-level tokens in `themes.json` `shared.elevation`: level 0 page, 1 resting card (1 px hairline plus a two-layer neutral shadow), 2 hover and drag, 3 dropdowns and scrolled sticky bars, 4 dialogs over a 45% scrim; shadows fall downward from one light above (bars docked at the bottom mirror upward), neutral or the theme's 10th-step dark tone, never the primary colour; primary buttons take a 1 px pressed-step bottom edge and a 16–24% white inner top line and sink 1 px when pressed; pale cards may take a 60–80% white top line. Page background: very light neutral grey or a very light tint of the primary hue (within 12°, luminance ≥ 0.85, e.g. `#F0F2FC`); white cards; card radius 12 (large cards and dialogs 16), inputs, buttons and icon blocks 8; at most one solid brand card per screen. Reading pages stay on level 0 with hairlines. No decorative gradients, textures, glass, blobs, bevels, glows or coloured shadows — only photo scrims and skeleton shimmer may use a gradient. One object, one icon: different objects never share a pictogram.
- Spreadsheets (file-design.html, 表格文件): build with `make_xlsx.py spec.json out.xlsx`, then `check_document.py`. One worksheet; title, header, data; Microsoft YaHei, title 18 pt and everything else 12 pt; no sequence-number column; repeated group names merged vertically, child groups inside parents; one fact per cell; pale blue header, group cells in rotating step-1 tints, light grey total row. Sheets meant for filtering, import or screen readers stay unmerged. Exports from a system (file-design.html, 导出文件) are cleaned data: Chinese headers, enums and booleans translated, `yyyy-mm-dd HH:mm` dates, two-decimal amounts with the unit in the header, no internal IDs, technical fields or empty columns, scope = the current filter, Chinese file name with the range.
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

Every approval records status, artifact path, SHA-256, time, approver and note in `raw/99-delivery/APPROVALS.json`. Scripts and the model never approve. The ledger and `MANIFEST.json` use schema 3.0 with only the `visual`, `document` and `standalone_poster` stages; schema 2.0 sessions from before the split are still accepted with their unused system stages ignored, and an approved system stage, a `01-system/` folder or a system mode is reported as Luz-System work. A spreadsheet or Word deliverable sits at the session root named after the folder (`NNN-名称.xlsx` or `.docx`).

## Validate

~~~powershell
py -X utf8 scripts/validate_skill.py
py -X utf8 scripts/experience.py check
py -X utf8 scripts/check_contrast.py
py -X utf8 scripts/check_document.py "<delivered file>" [--allow interface | website] [--allow KIND]
py -X utf8 -m unittest discover -s scripts -p "test_*.py"
~~~

`check_document.py` is also used by Luz-System, Luz-Dev and Luz-Writing for their pages. Run it on every final deliverable. In every HTML mode a missing or empty `<link rel="icon">` (or an unfilled `{{TAB_ICON}}`) is an ERROR: each delivered page carries an inline SVG tab icon of its subject (visual-design.html 网页图标与品牌标识; print one with `py -X utf8 scripts/new_session.py icon "<page or system name>"`). Every HTML mode also warns on browser-default bold (`th`, `h3`–`h6`, `strong`, `b` without a weight), weights other than 400/600/700, and a page that keeps a template's default style; reading pages warn on any card shadow. `--allow interface` applies the interface type scales, the three weights (700 below 22px, 500 or thin weights are errors), the brand card (a primary step with white text at 4.5:1, one per screen), the elevation rules (bevels, glows and coloured shadows are errors; shadows beyond the levels, upward shadows outside bottom bars and layers above 20% warn), icon stroke widths (2, or 1.75 for small icons) and theme-step fills, and the static interface checks (body text below 14px outside meta/hint/time/unit/badge/caption/aux elements, a page title equal to the highlighted nav item, a nav group named like its only item, all-empty table columns, and warnings for one-value columns, long-text cells padded under 16px, list tables without pagination, a default page size other than 20, and an admin or website header without a graphic brand mark — script-rendered content is left to the browser tests), `--allow website` adds the website first-screen titles, and other kinds are only for items the user explicitly requested. Any ERROR blocks delivery; a clean run is necessary, not sufficient.
