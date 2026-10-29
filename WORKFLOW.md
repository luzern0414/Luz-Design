# Luz Design workflow

Sessions live in `D:\Codes\skill输出\Luz-Design\NNN-名称\`: the single final deliverable (HTML, XLSX or DOCX) at the root and every working file under `raw\`. Rules and templates live in `references\`, accumulated knowledge in `experience\`. Luz Design covers visual standards, standalone visual work and document layout. System design, product UI, prototypes and hardware belong to Luz-System; backend to Luz-Dev; the prose itself to Luz-Writing.

## 0 Rule card and experience first

Run `py -X utf8 scripts/context.py <kind>` and read the whole rule card before anything else: it carries the user's preferences, matching lessons, the rule text for this kind of task, the tools and the checks (sessions save it to `raw/00-rules/`). Templates and builders are skeletons; the card decides. Then read `experience/catalog.md` and search it with `scripts/experience.py search`. Stored user preferences and lessons apply without being asked again. Reuse palettes, type scales and visual or document rules that already fit; record in BRIEF which ones the session builds on.

## 1 Brief

Capture only facts supplied by the user: purpose, audience, channel, exact copy, sizes or formats, brand constraints, deadline. Missing exact copy or format stops the session before production.

## 2 Session

Create one numbered session with `scripts/new_session.py`: `--modes visual --standalone-poster` for posters, brand key visuals and campaign images (the title names the task), `--modes document` for reports, spreadsheets, Word documents and slides. The script refuses system, prototype and hardware modes and names Luz-System; visual mode without `--standalone-poster` is refused too. `scripts/validate_session.py <session>` checks the workspace (schema 3.0; older 2.0 ledgers are read with their system stages ignored).

## 3 Research

When colour, type or a document format needs evidence, research official colour scales, design systems or standards with LuzCrawl (`D:\Codes\Luz-Crawl`, one `begin "<主题>" --new` task per request) and record what each choice is based on. Reference images are used only for named structural or stylistic attributes.

## 4 Visual work

Follow `references/visual-design.html`: choose the primary colour from the industry's mood and an official colour scale, keep one font stack, the type scale and type roles of the output (weights 400/600/700), flat graphics (2 px line and duotone icons, layered flat illustrations) with depth only from the five elevation levels, one object one icon. Re-read the rule sections and `themes.json` for each deliverable; templates are skeletons, never the design. Posters keep a safe area, at most four text levels and real or generated photography. Write prompts from `references/prompt-image.txt`, dry-run Imagegen, generate one image at a time and review every output. Assemble the direction, references, outputs and verification in `raw/02-visual/visual-board.html` and stop for human approval.

## 5 Documents

Follow `references/file-design.html`. Spreadsheets are built with `scripts/make_xlsx.py` and Word documents with `scripts/make_docx.py` (contract, proposal, report, minutes, general); reading HTML uses the reading type scale. Decide the document type first, then its structure; the words come from the user or Luz-Writing. Export, reopen and check the actual file.

## 6 Publish and sediment

Publish with `scripts/publish.py <session> <visual | document>` or place the single XLSX or DOCX at the session root named after the folder (`NNN-名称.xlsx`); nothing else sits next to `raw/`. Add judged knowledge in bulk with `experience.py add <file.json>`: palettes, type facts, visual and document rules, research lessons.

## 每次调用后沉淀

Before finishing any call, session or not, run `experience.py note` for (a) every preference the user stated or corrected (`--kind preference`), (b) every palette, type scale, source or parameter that proved effective or failed (`--kind fact`), (c) every rule correction (`--kind lesson`). Use a stable topic `--key`: the same key replaces the old statement and keeps one previous version, so knowledge is updated, not piled up. Write the general principle, never personal data or task trivia. Notes live in `experience/notes.json` (same shape and commands in all four Luz skills; see SKILL.md), capped at 60 preferences, 120 lessons and 120 facts and pruned automatically; curated patterns are capped at 200; `experience.py check` must pass.

## 7 Validate and deliver

~~~powershell
py -X utf8 scripts/validate_skill.py
py -X utf8 scripts/experience.py check
py -X utf8 scripts/check_contrast.py
py -X utf8 scripts/check_document.py "<final file>" [--allow interface | website]
py -X utf8 -m unittest discover -s scripts -p "test_*.py"
~~~

Any artifact change invalidates its approval hash. A preview, fabricated source, unverified export or skipped document check is not a completed deliverable.
