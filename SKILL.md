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
5. **Pass the checks on the card.** `make_xlsx.py` and `make_docx.py` run `check_document.py` on what they write and fail on any ERROR; `publish.py` runs it on the HTML it publishes; other files go through `check_document.py` by hand before delivery (PDF is checked as the card says, see Validate).
6. **Sediment — mandatory, checked at publish.** Every call writes or confirms at least one note with `experience.py note` and lists its key in BRIEF `## 本次沉淀`; `publish.py` refuses a session whose listed keys are missing from `experience/notes.json` or were last confirmed before the session started. Without a session, run the note command before replying. What to record is in 每次调用后沉淀.

## Not this skill — route instead

| Request | Use |
|---|---|
| System architecture, function list, product UI for admin consoles, mini-programs, agent UIs and websites, interactive prototypes, on-site hardware selection | **Luz-System** (`D:\Codes\Luz-System`) |
| Backend, APIs, databases, deployment, launch | **Luz-Dev** (`D:\Codes\Luz-Dev`) |
| The words themselves: articles, copy, agreements, policies | **Luz-Writing** (`D:\Codes\Luz-Writing`); Luz Design lays the document out |
| Browser search and capture | **Luz-Crawl** (`D:\Codes\Luz-Crawl`), following its SKILL.md 调用协议: doctor → `begin "<主题>" --new` → `experience --query` → every command with `--out <task folder>` |

**Interface rules are split between the two skills.** How a product screen behaves is a Luz-System rule (list default views, titles and navigation, filters, pagination behaviour, dashboards, what an export contains): [ui-standards.html](https://github.com/luzern0414/Luz-System/blob/master/references/ui-standards.html) and the four surface pages (local: `D:\Codes\Luz-System\references\`). The numbers of how it looks live here only — type sizes and weights (visual-design.html 七级字体角色 and 小程序紧凑用法), colour, icons, radii, elevation, density and table alignment — and the surface pages point to them. `new_session.py` refuses system, prototype and hardware modes and names Luz-System.

## Layout

```text
D:\Codes\Luz-Design\                   the skill (rules, templates, knowledge, scripts)
  SKILL.md   WORKFLOW.md   README.md   LICENSE   NOTICE
  agents\openai.yaml
  references\
    visual-design.html                 视觉设计规范: 视觉基础 (flat style, palette and theme system, type and seven type roles, icons, illustrations, tab icons, elevation, motion) → 排版基础 (spacing, density and table alignment, hierarchy, writing discipline) → 视觉产出 (posters, Imagegen, references and rights) → visual problem families
    file-design.html                   文件设计规范: reading HTML, Excel, Word by document type (contracts, proposals, reports, minutes, official documents, paper style), PowerPoint, PDF, Markdown
    cards.json                         rule cards: which rule sections, tools and checks each task kind gets
    themes.json                        industry themes and shared tokens (status colours, price colour, elevation)
    guidelines.css  templates.txt  prompt-image.txt
  experience\
    notes.json                         preferences, lessons and facts from every call, upserted by key (caps 60, 120, 120)
    patterns.json  sources.json  catalog.md      curated palettes, type scales, visual and file rules, sources; catalog is generated
  scripts\                             check_document, check_contrast, make_xlsx, make_docx, cut_element_sheet, sessions, publish, experience, validation, tests

D:\Codes\skill输出\Luz-Design\         outputs only
  NNN-名称\
    NNN-名称.html | .xlsx | .docx | .pptx | .pdf | .md | .png | .jpg     the single final deliverable
    raw\                               BRIEF, rule cards, prompts, references, generated images, document sources, approvals, manifest
```

Never write outputs into the skill, and never put rules, templates or scripts into the output folder.

## Route

| Task | Read | Entry condition |
|---|---|---|
| Colour, type, icons, illustrations, spacing, radii, elevation and shadows, motion for any output (including Luz-System interfaces) | [visual-design.html](references/visual-design.html) 一、二 | — |
| Poster, brand key visual, campaign image, Imagegen, reference edit | [visual-design.html](references/visual-design.html) 三 | A standalone visual session whose title names the task (海报, 主视觉, 宣传图 …) |
| Report or reading HTML, Excel, Word, PowerPoint, PDF, Markdown | [file-design.html](references/file-design.html) | Chosen format, complete source, export verification |

The rule pages define standards and judgment, not templates: derive colour, composition and structure from each request. [WORKFLOW.md](WORKFLOW.md) gives the phases.

## 每次调用后沉淀

Mandatory on every call, not only for sessions. Every call leaves at least one note behind — new or confirmed — and a session lists those keys in BRIEF `## 本次沉淀` (| 经验 key | 类型 | 一句话 |); `publish.py` checks them. Record, among others:

- **preference** — what the user stated or corrected this time (a colour, a size, a layout habit, something they dislike).
- **lesson** — a rule correction, a mistake the checks did not catch and the right way, a template default that had to be overridden.
- **fact** — a design approach that worked (palette and the steps used, type scale, layout, which component library and component was referenced), research sources and scope (which sites or documents were useful or useless, the queries used), generation parameters (Imagegen prompt block, sizes).
- **Already known and used again** — write the same key again to confirm it (`uses` +1); when the new finding contradicts it, rewrite the same key and the old text becomes `previous`. Never add a second note on the same topic.

One store, `experience/notes.json`, with the same shape and commands in Luz-System, Luz-Design, Luz-Dev and Luz-Writing:

- **Start:** `py -X utf8 scripts/experience.py search <关键词> [--kind preference|lesson|fact]` and apply what matches.
- **Before finishing:** `py -X utf8 scripts/experience.py note --kind preference|lesson|fact --key <主题> --text "<一句话原则>" [--why "<依据>"]` — the general principle, not task trivia.
- **Fields:** `key`, `kind`, `text`, `why` (optional), `uses`, `first_seen`, `last_confirmed` (YYYY-MM-DD), `previous` (`{text, replaced_at}`, only after a replacement).
- **Replace, never pile up:** the same key replaces the text (one `previous` kept, `uses` +1); the same statement under another key confirms that note. Caps: preference 60, lesson 120, fact 120; over a cap the fewest uses, then the oldest confirmation, go first. `list [--kind]` shows notes; `prune` enforces caps and lists notes unconfirmed for 180 days; `check` fails on duplicate keys or statements, missing fields, overflow and private data.
- **Scope:** a preference prints on every rule card, so a preference that holds only for one kind of product says so in its text and points to the theme or rule that carries the details (for example a theme in `themes.json`).
- **Public repository:** no phone numbers, emails, WeChat IDs, user-home paths, credentials, personal, client or project names; `note` refuses the detectable ones.
- **Tests and rehearsals only:** `LUZ_EXPERIENCE_STORE=<path to a notes.json>` points `note`, `list`, `search`, `prune`, the rule cards and the 本次沉淀 gates at that file for the whole process and leaves the skill's own notes and catalog untouched; the gates print a reminder while it is set. Real deliveries never set it. A program that calls the skill on behalf of clients writes generic notes after approval, searches first and confirms an existing key rather than adding a new one, and never records client context.

Here also: curated palettes, type scales, visual and file rules with sources go to `patterns.json` through `experience.py add <file.json>` (kinds 色彩, 字阶, 视觉规则, 文件规则, 设计理念, 调研经验; cap 200); `catalog.md` is re-rendered after every write.

## Output baseline

Each line is a summary; the rule page section named in brackets is the rule.

- **First line is the title** (visual-design.html 文字纪律 › 第一行就是主标题): no subtitle, summary, tags, timestamps, tool names, source counts, hashes, file paths or design notes; apply the deletion test to every visible element, by problem family, not by word list.
- **Colour** (配色, 主题色系统, 取色依据): light surfaces; one primary from the industry's mood (`themes.json`), taken from one column of an official 10-step palette; 60-30-10 with neutrals dominant; product UI adds at most one marketing accent, one fixed accent per top-level module, the shared price colour and one solid brand card per screen; no gradient buttons; `check_contrast.py` and `check_document.py` enforce it.
- **Type** (字体与字号, 七级字体角色, 小程序紧凑用法): one font stack `"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif` in HTML and Microsoft YaHei in files; weights 400/600/700 with 700 only at 22px and larger; nothing below 12px in HTML (websites and reading pages 14); no italics, letter spacing or rotated text; every size comes from the scale of its product type.
- **Graphics and depth** (扁平线性风格, 图形：一套线性图标, 插画：多层扁平, 层级与立体感): control icons are 2 px line vectors (1.75 at 16 px); entry icons, illustrations and decorative elements are duotone line, layered flat or generated in the one style the user picked; depth belongs to surfaces only, from the five elevation tokens in `themes.json` `shared.elevation`; one object, one icon.
- **Tables** (界面密度与表格对齐; file-design.html 表格文件): header centred, long text left, short values centred, amounts right-aligned with tabular figures — in interfaces, reading pages, Excel and Word alike.
- **Spreadsheets** (file-design.html 表格文件, 导出文件): build with `make_xlsx.py spec.json out.xlsx`; one sheet, title 18 pt and everything else 12 pt, no sequence column, group names merged vertically, one fact per cell, pale tints; system exports are cleaned Chinese data.
- **Word** (file-design.html 文字文档, 按文档类型, 论文版式): build with `make_docx.py spec.json out.docx`; decide the document type first (contract, proposal, report, minutes, general; `"style": "paper"` only when the user asks for the paper text rules; GB/T 9704 only when asked).

## Imagery with the local image service

Use `D:\Codes\Imagegen\src\imagegen.py`; every request is billed (visual-design.html 图像生成).

1. Real photographs come first; without one, generate photos of stores, products and environments (no text, no logos, no identifiable faces). Posters, entry icons, illustrations and decorative elements may be generated in the style the user picks on the visual board (2–3 candidates by industry and scene, one style per product, transparent background, no text). Control icons in navigation, tab bars, menus, buttons, toolbars, tables and forms stay 2 px line vectors; never generate background textures or interface screens.
2. Write one prompt file per image or 4×4 element sheet under `raw/02-visual/prompts/` from `references/prompt-image.txt`; dry-run first; send one request at a time; cut sheets with `py -X utf8 scripts/cut_element_sheet.py <sheet.png> <out_dir> <name1> … <name16>`.
3. A timeout is not retried automatically (a retry may be billed twice): check the service's records for an existing result first; if there is none, fall back to a vector illustration.
4. Review every image before use; record the actual size and format.

## Sessions

~~~powershell
py -X utf8 scripts/new_session.py --name "<活动名>海报" --modes visual --standalone-poster
py -X utf8 scripts/new_session.py --name "<文档名>" --modes document --card xlsx      # or --card docx | reading-html | slides | pdf-markdown
py -X utf8 scripts/add_mode.py "<会话目录>" document                                    # add document mode to a poster session (visual only with --standalone-poster)
py -X utf8 scripts/publish.py "<会话目录>" visual | document
~~~

- **HTML deliverables** (visual board, reading page) are published with `publish.py`: it refuses a session without a current rule card, 采用的规则 or fresh 本次沉淀, runs `check_document.py` on the page (`--allow KIND` passes on extra kinds the user asked for), and publishes the visual stage only when `raw/99-delivery/APPROVALS.json` records it approved by a person with the board's current SHA-256.
- **Spreadsheet, Word, PowerPoint, PDF, Markdown or image deliverables** are copied by hand to the session root as `NNN-名称.<ext>` after their checks pass; their source (`spec.json`, the exported file) stays in `raw/03-documents/`. Validation applies the same rule-card and 本次沉淀 gates to them.
- Every approval records status, artifact path, SHA-256, time, approver and note. Scripts and the model never approve. Ledgers use schema 3.0 with the `visual`, `document` and `standalone_poster` stages; schema 2.0 sessions from before the split are read with their system stages ignored, and an approved system stage, a `01-system/` folder or a system mode is reported as Luz-System work.

## Validate

~~~powershell
py -X utf8 scripts/validate_skill.py [--package-only]
py -X utf8 scripts/experience.py check
py -X utf8 scripts/check_contrast.py
py -X utf8 scripts/check_document.py "<delivered file>" [--allow interface [--allow website]] [--allow KIND]
py -X utf8 scripts/sync_rule_core.py                 # the shared rule-card core in Luz-System, Luz-Dev and Luz-Writing matches this one
py -X utf8 -m pytest -q                              # in scripts\ (or: py -X utf8 -m unittest discover -s scripts -p "test_*.py")
~~~

- `validate_skill.py` prints the package result first, then the sessions in the output root; `--package-only` skips the sessions. It also fails when a rule card of Luz-System cites a heading of these rule pages that no longer exists.
- `scripts/context.py` holds the master copy of the shared rule-card core. Change it here only and copy it with `sync_rule_core.py --write`; without arguments the script only reports SAME or DIFF.
- `check_document.py` is shared with Luz-System, Luz-Dev and Luz-Writing. It reads HTML, XLSX, DOCX, PPTX and Markdown; a PDF is reported as SKIP and checked with PyMuPDF and page renders (file-design.html 便携式文档). Every HTML mode errors on a missing or empty tab icon (`py -X utf8 scripts/new_session.py icon "<page or system name>"` prints one) and on dark fills larger than a line of text (judged by declared size and class: a container stays a container whatever its name; visual-design.html 检查脚本的认定), and warns on browser-default bold, weights outside 400/600/700 and a page that keeps a template's style. `--allow interface` adds the product type scale, the brand card, elevation, icon strokes and fills, 14px body text outside elements whose class has the word meta, hint, time, unit, badge, tag, caption or aux, titles equal to the highlighted nav item, empty columns and pagination; inside it, elements whose class or id has `version` may show version numbers. `--allow website` (implies interface) uses the website scale with a 14px floor. Metadata words that are also topics (提示词, 官方页面, 版本号, SHA-256, 哈希) are reported only in label-and-value lines, footers and short fragments that are not sentences; titles and body sentences may discuss them. Other kinds are only for items the user explicitly requested. Any ERROR blocks delivery; a clean run is necessary, not sufficient.
