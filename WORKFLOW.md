# Luz Design workflow

Sessions live in `D:\Codes\skill输出\Luz-Design\NNN-名称\`: the single final deliverable at the root and every working file under `raw\`. Rules and templates live in `references\`, accumulated knowledge in `experience\`. Luz Design covers visual standards, the whole look of product front ends and their prototypes (composition, the look of components, icons, images, motion, themes), standalone visual work and document layout. System design, the functional structure of product UI (pages, entrances, tab bar items, component list, button actions, flows, states), the behaviour and data of prototypes and hardware belong to Luz-System; backend to Luz-Dev; the prose itself to Luz-Writing. `references/ui-ownership.md` draws the line between System and Design.

## 0 Rule card and experience first

Run `py -X utf8 scripts/context.py <kind>` and read the whole rule card before anything else: it carries the user's preferences, matching lessons, the rule text for this kind of task, the tools and the checks (sessions save it to `raw/00-rules/`). Templates and builders are skeletons; the card decides. Then search the experience library with `scripts/experience.py search <关键词>` for palettes, type scales and visual or file rules that already fit, and record in BRIEF which ones the session builds on.

## 1 Brief

Capture only facts supplied by the user: purpose, audience, channel, exact copy, sizes or formats, brand constraints, deadline. Missing exact copy or format stops the session before production.

## 2 Session

Create one numbered session with `scripts/new_session.py`: `--modes visual --standalone-poster` for posters, brand key visuals and campaign images (the title names the task), `--modes document --card <kind>` for reports (`reading-html`), spreadsheets (`xlsx`), Word documents (`docx`), slides (`slides`) and PDF or Markdown (`pdf-markdown`); without `--card` a document session gets the reading-html card. `scripts/add_mode.py <session> document` adds document work to a poster session. The scripts refuse the system, prototype and hardware session modes (their session engine is Luz-System's); interface and prototype looks are worked from the interface rule cards. `scripts/validate_session.py <session>` checks the workspace.

## 3 Research

Every business task completes the Luz-Crawl preflight before a proposal or implementation: run → read source bodies → conclude with applied findings and gaps → check. Follow `D:/Codes/Luz-Crawl/references/preflight.md`, reusing the same request's task directory. Research scope follows the actual colour, layout, accessibility, icon or format questions. Reference images supply named structural or stylistic attributes.

For design direction work (anything where look and feel matters) the research is specific: follow `references/reference-research.md` (reference pyramid of specs, real products, inspiration and material sources; sites and their verified status in `references/reference-sites.json`), capture 3–5 same-industry products with Luz-Crawl, measure each with `scripts/teardown.py --lint`, put the fingerprints in one comparison table and write down the attributes borrowed and the ones refused. Never replace a capture with remembered knowledge; blocked sites are not bypassed.

## 3a Direction (before any drawing)

1. Write three personality adjectives and three anti-goals (`references/design-craft.md` §2), then pick 2–3 style boards from `references/style-boards.json` and say why each was chosen and what each would risk.
2. Let the person see and mix the options: `scripts/make_style_lab.py` builds the style lab (three presets, free mixing of palette, icon style, shape, depth, type scheme and motion personality, live contrast and colour-discipline checks, export of CSS variables, tokens and a brief). The person's choices go into BRIEF; everything outside the current rules is listed as "待裁定" and decided by the person (`references/token-system.md` §8).
3. Derive tokens and run the discipline checks: `scripts/check_contrast.py`, `scripts/audit_theme_discipline.py --theme <id>` and `--combo …`, then `scripts/export_tokens.py`.
4. Materials: read `references/imagegen-playbook.md`; eight-slot prompts in `raw/02-visual/prompts/`, dry run, one request at a time, review each image (a transparent image on a light and a dark background). Real photographs first; a style sample budget of three requests unless the person says otherwise.
5. Motion: pick recipes from `references/motion-recipes.md`, tokens only, each with a reduced-motion fallback and a measurement plan.
6. Stage prompts for every step above are in `references/design-prompts.md`.
7. Direction concerns looks only. Never change what the functional spec lists (pages, entrances, tab bar items, components, buttons, flows, states, copy keys); an option that needs such a change goes back to Luz-System as a change request (project mode: the requirement-change ledger), and the function stays as specified until System changes it.

## 3b Critique loop (before delivery)

Score the 390 and desktop, light and dark screenshots with the ten-item rubric of `references/design-craft.md` §10 and run `scripts/teardown.py --lint` on the page; fix the lowest items only and score again. A zero on any item, or a total under 20 of 30, is not delivered. Record scores and the before and after lint counts in BRIEF `## 采用的规则`.

## 3c The design path (interface projects)

An admin console, mini-program, website, agent UI or interactive prototype follows one ordered path, `references/design-path.html` (rule card `design-path`): P0 intake and judgement, P1 references and research, P2 entrance and information-architecture check, P3 page list and paradigm choice, P4 visual direction and tokens, P5 component library and module mapping, P6 detail system, P7 motion and states, P8 prototype and verification, P9 handoff and sediment. Each stage names what it produces, which check it passes and which rule cards to read, and the page gives the thinking tools (first landing, entrance ownership three questions, five questions, paradigm four questions, deletion test, conflict order) and the shape of a deviation note. The phases of this file sit on it: 0 is P0, 3 is P1, the page decisions in 4 are P2 and P3, 3a is P4, the rest of 4 is P5 to P8, 6 is P9. Because P2 and P3 need only the functional spec, run them before 3a whenever the spec is in hand.

At P0 paste the checklist into the session BRIEF: `py -X utf8 scripts/design_path.py checklist --surface miniprogram|admin|website|agent`. Tick a stage only when its output exists and its check passes. When a `default` or `hint` rule is not followed, write the deviation note with `design_path.py deviation <rule id> --why … --risk … --verify …`; a `must` rule is never deviated from, and a function problem goes back to Luz-System instead. Show a stage's detail with `design_path.py show P3` (and so on).

At P8, when the deliverable is the front-end interface HTML of product development (a clickable single-file prototype, one tab per system when there are several), read the rule card `prototype-reference` (`references/prototype-reference.html`): when to use the reference implementation whole, take one block or write your own; the shape of the deliverable (three-column file with page directory, appearance config, scene switches, logic panel and page-stack navigation, complete interaction, operable at 390 px, one tab per system); taking components from the numbered library by number with `data-cid`; light and dark; the spec and `scripts/build_prototype.py` / `build_prototype_suite.py`; acceptance and known limits. The reference implementation (`references/prototype-templates/`) and the component template library (`references/component-library/`) are references, not templates: the page list, the home page and the entrances come from Luz-System's function list and `page-patterns`, never from the examples.

## 4 Visual work

Product interface visuals and the look of prototypes start from the functional spec Luz-System writes (page list and routes, entrances, tab bar items and names, the component list with its purposes, the action table, states, data needs, copy keys). That spec carries no colours, sizes, radii, shadows, icon glyphs, image content, grid values or animation timings - this skill supplies all of them from the rule pages and `themes.json`, and adds, removes or re-orders nothing the spec lists. For interface work, run the adaptive matching stage before drawing or coding: read `references/layout-inference.md` and `references/interface-style-matrix.json`, then run `py -X utf8 scripts/style_match.py --brief "..." --input <brief.json> --output <match.json>`. Keep the output's evidence, semantic relationships, decisions and adaptation in the session BRIEF. Treat example counts and arrangements as signals; only explicit mandatory language becomes a hard constraint. When the brief names an asymmetric dashboard, preserve its required relationships while deriving spans, rail position and mobile collapse from content and viewport. Show the user 2–3 candidates and the exact asset scope. Stop at `approval.status = "pending"` until the user selects a direction. Do not call Imagegen, generate assets, change page code or publish before approval; after approval, retain line-vector controls and use the selected style only in its confirmed scope.

Pages and entrances come first (P2 and P3 of the path, before style matching and drawing). With Luz-System's entrance table `entrances.json` (one row per function: `fn`, `name`, `type`, `category`, `entry`, `destination`, `freq`; the format is `page_pattern.py show entrances`) and the function list in hand, run in this order: `py -X utf8 scripts/page_pattern.py brief --features features.json --entrances entrances.json --type <app type> --out brief.json`, `plan --brief brief.json --out spec.json`, build the pages, `check spec.json`, then `check-page <page.html> --hash "#/home" --width 390` on the built page. `recommend`, `list` and `show` look up paradigms, app types, pages and rules; the rule card `page-patterns` carries the text. The tool decides modules, order and de-duplication on the home page only; it never adds or removes a function or an entrance. What it rejects, and any function that cannot be placed, goes into BRIEF as a return list for Luz-System.

When the interface goes to Luz-Dev or into a Luz-Project handoff, export the approved theme with `py -X utf8 scripts/export_tokens.py <theme> --out <name>.tokens.json` and check it with `--check`; developers take values from that file.

For posters and standalone visual work, follow `references/visual-design.html` and the poster card; templates are skeletons, never the design. Posters keep a safe area (a printed poster also gets 3 mm of bleed, see the rule page 屏幕渠道与印刷渠道), at most four text levels and real or generated photography. Imagegen requests follow SKILL.md 'Imagery with the local image service' (dry run, one request at a time, no automatic retry on a timeout). Assemble the direction, references, outputs and verification in `raw/02-visual/visual-board.html` and stop for human approval: the person records it in `raw/99-delivery/APPROVALS.json`.

## 5 Documents

Follow `references/file-design.html`. Decide the document type first, then its structure; the words come from the user or Luz-Writing. Spreadsheets are built with `scripts/make_xlsx.py`, Word documents with `scripts/make_docx.py` (contract, proposal, report, minutes, general) and landscape table PDFs (catalogues and lists) with `scripts/make_table_pdf.py`, all from a `spec.json` kept in `raw/03-documents/`; reading HTML uses the reading type scale. Export, reopen and check the actual file; a PDF goes through `scripts/check_pdf.py`, a deck through `check_document.py` (16:9, margins, titles, alternate text).

## 6 Publish and sediment

HTML deliverables go out with `scripts/publish.py <session> <visual | document>`, which runs the checks and the approval gate. Other formats are copied to the session root as `NNN-名称.<ext>` after their checks pass; nothing else sits next to `raw/`. Before finishing any call, write or confirm notes as SKILL.md 每次调用后沉淀 says and list their keys in BRIEF `## 本次沉淀`; add judged palettes, type facts and visual or file rules in bulk with `experience.py add <file.json>`.

## 7 Validate and deliver

Run the commands in SKILL.md 'Validate'. Any artifact change invalidates its approval hash. A preview, fabricated source, unverified export or skipped document check is not a completed deliverable.


## Luz project handoff

Project mode begins only when `luz-project` supplies a project root. Reuse the project's Luz-Crawl task, inspect the System frontend routes and states, select an adaptive layout and visual language, and write the approved UI handoff to the project docs. Keep System responsible for information architecture and function (pages, entrances, tab bar items, components, button actions, flows) and Design responsible for the whole look (composition, component looks, icons, images, motion, themes, the prototype's appearance); pass stable page, component, action, token, and asset IDs to Luz-Dev. A standalone Design call continues to use its own numbered output folder. In project mode the design stage reads the rule cards `design-path` and `page-patterns`; `py -X utf8 scripts/design_path.py show project` lists what the stage reads, writes and when to stop and ask.

