# Luz Design workflow

Sessions live in `D:\Codes\skill输出\Luz-Design\NNN-名称\`: the single final deliverable at the root and every working file under `raw\`. Rules and templates live in `references\`, accumulated knowledge in `experience\`. Luz Design covers visual standards, standalone visual work and document layout. System design, product UI, prototypes and hardware belong to Luz-System; backend to Luz-Dev; the prose itself to Luz-Writing.

## 0 Rule card and experience first

Run `py -X utf8 scripts/context.py <kind>` and read the whole rule card before anything else: it carries the user's preferences, matching lessons, the rule text for this kind of task, the tools and the checks (sessions save it to `raw/00-rules/`). Templates and builders are skeletons; the card decides. Then search the experience library with `scripts/experience.py search <关键词>` for palettes, type scales and visual or file rules that already fit, and record in BRIEF which ones the session builds on.

## 1 Brief

Capture only facts supplied by the user: purpose, audience, channel, exact copy, sizes or formats, brand constraints, deadline. Missing exact copy or format stops the session before production.

## 2 Session

Create one numbered session with `scripts/new_session.py`: `--modes visual --standalone-poster` for posters, brand key visuals and campaign images (the title names the task), `--modes document --card <kind>` for reports (`reading-html`), spreadsheets (`xlsx`), Word documents (`docx`), slides (`slides`) and PDF or Markdown (`pdf-markdown`); without `--card` a document session gets the reading-html card. `scripts/add_mode.py <session> document` adds document work to a poster session. The scripts refuse system, prototype and hardware modes and name Luz-System. `scripts/validate_session.py <session>` checks the workspace.

## 3 Research

When colour, type or a document format needs evidence, research official colour scales, design systems or standards with Luz-Crawl, following its SKILL.md 调用协议 (doctor → `begin "<主题>" --new` → `experience --query` → every command with `--out <task folder>`), and record what each choice is based on. Reference images are used only for named structural or stylistic attributes.

## 4 Visual work

Follow `references/visual-design.html` and the poster card; templates are skeletons, never the design. Posters keep a safe area, at most four text levels and real or generated photography. Imagegen requests follow SKILL.md 'Imagery with the local image service' (dry run, one request at a time, no automatic retry on a timeout). Assemble the direction, references, outputs and verification in `raw/02-visual/visual-board.html` and stop for human approval: the person records it in `raw/99-delivery/APPROVALS.json`.

## 5 Documents

Follow `references/file-design.html`. Decide the document type first, then its structure; the words come from the user or Luz-Writing. Spreadsheets are built with `scripts/make_xlsx.py` and Word documents with `scripts/make_docx.py` (contract, proposal, report, minutes, general), both from a `spec.json` kept in `raw/03-documents/`; reading HTML uses the reading type scale. Export, reopen and check the actual file.

## 6 Publish and sediment

HTML deliverables go out with `scripts/publish.py <session> <visual | document>`, which runs the checks and the approval gate. Other formats are copied to the session root as `NNN-名称.<ext>` after their checks pass; nothing else sits next to `raw/`. Before finishing any call, write or confirm notes as SKILL.md 每次调用后沉淀 says and list their keys in BRIEF `## 本次沉淀`; add judged palettes, type facts and visual or file rules in bulk with `experience.py add <file.json>`.

## 7 Validate and deliver

Run the commands in SKILL.md 'Validate'. Any artifact change invalidates its approval hash. A preview, fabricated source, unverified export or skipped document check is not a completed deliverable.
