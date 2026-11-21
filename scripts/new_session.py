#!/usr/bin/env python3
"""Create the next numbered Luz Design session: NNN-主题\\ with raw\\ for every source and working file.

The root of a session holds only raw\\ and the summary page NNN-主题.html (publish.py or make_summary.py writes it);
a task without a project may also keep its deliverables there (deliver.py), a task for a project (--project) keeps them
in the project's docs. The layout check is check_output_layout.py session.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

from validate_session import OUTPUT_STANDARD

SKILL_ROOT = Path(__file__).resolve().parents[1]
# The skill holds rules, templates and scripts; every session it creates is an output and lives here.
OUTPUT_ROOT = Path(r"E:\Skill输出\Luz-Design")
# A project's state root is the raw\ of its session in the Luz-Project output root (the project folder keeps results only).
PROJECT_OUTPUT_ROOT = Path(os.environ.get("LUZ_PROJECT_OUTPUT") or r"E:\Skill输出\Luz-Project")
SESSION_RE = re.compile(r"^(\d{3,})-(.+)$")
# Sessions made before the output layout used two-digit numbers or underscores; their numbers are never reused.
LEGACY_SESSION_RE = re.compile(r"^(\d{2,})[-_].+$")
INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
# Luz-Design owns standalone visual work (posters, brand key visuals, campaign images) and document layout.
# System design, the functional structure of product UI, the behaviour of interactive prototypes and hardware belong to Luz-System (D:\Codes\Luz-System); the look of product UI is worked here from the interface rule cards.
MODE_NAMES = ("visual", "document")
OTHER_SKILL_MODES = {"system": "Luz-System", "prototype": "Luz-System", "hardware": "Luz-System"}
POSTER_TASK_RE = re.compile(r"海报|poster|主视觉|品牌视觉|宣传图|视觉方向|活动视觉|封面|KV", re.I)
SESSION_KINDS = ("general", "standalone_poster")
# Rule card written into raw/00-rules/ when a mode starts (scripts/context.py; references/cards.json).
DEFAULT_CARDS = {"visual": "poster", "document": "reading-html"}
PAGE_TEMPLATES = {"visual-board.html": "design-visual-board", "document.html": "design-document-page"}

# Tab icon (references/visual-design.html 网页图标与品牌标识): every delivered HTML carries one solid mark of its subject:
# a white pictogram on a rounded square in the theme's primary colour (colour plus white), 32×32, at most three shapes, no text.
# The rule asks for a solid mark and does not prescribe the colour.
TAB_ICONS = {
    "dumbbell": '<path d="M9 11v10M23 11v10M6 14v4M26 14v4M9 16h14"/>',
    "megaphone": '<path d="M8 13v6h4l8 5V8l-8 5z"/><path d="M24 13a4 4 0 0 1 0 6"/>',
    "radar": '<circle cx="16" cy="16" r="8.5"/><path d="M16 16l5.5-5.5M16 11.5a4.5 4.5 0 1 0 4.5 4.5"/>',
    "chip": '<rect x="10" y="10" width="12" height="12" rx="2"/><path d="M13.5 7v3M18.5 7v3M13.5 22v3M18.5 22v3M7 13.5h3M7 18.5h3M22 13.5h3M22 18.5h3"/>',
    "ledger": '<rect x="9" y="7" width="14" height="18" rx="2"/><path d="M13 12h6M13 16h6M13 20h3"/>',
    "store": '<path d="M7.5 13l2-5h13l2 5zM9 13v11h14V13"/><path d="M14 24v-5h4v5"/>',
    "document": '<path d="M10 7h8l5 5v13H10z"/><path d="M18 7v5h5M13.5 17h6M13.5 21h4"/>',
    "magnifier": '<circle cx="14.5" cy="14.5" r="6.5"/><path d="M19.5 19.5l5 5"/>',
    "palette": '<path d="M16 7a9 9 0 1 0 0 18c1.4 0 2.2-.9 2.2-2s-.9-1.6-.9-2.6.8-1.6 1.9-1.6H22a3 3 0 0 0 3-3c0-4.8-4-8.8-9-8.8z"/><path d="M11.5 15h.01M14 11h.01M19 11h.01"/>',
    "grid": '<path d="M9 9h5v5H9zM18 9h5v5h-5zM9 18h5v5H9zM18 18h5v5h-5z"/>',
    "bowl": '<path d="M7 15h18a9 9 0 0 1-18 0z"/><path d="M12 25h8M13 8c0 1.6 1.6 1.6 1.6 3.2M17.6 8c0 1.6 1.6 1.6 1.6 3.2"/>',
    "plane": '<path d="M7 15.5 25 8l-6 17-4.2-6.8z"/><path d="M14.8 18.2 25 8"/>',
    "book": '<path d="M16 10.5c-2.2-1.6-5-2.2-8-2.2v14.4c3 0 5.8.6 8 2.2 2.2-1.6 5-2.2 8-2.2V8.3c-3 0-5.8.6-8 2.2z"/><path d="M16 10.5v14.4"/>',
}
# First match wins; the subject (system name or page title) is matched case-insensitively.
ICON_KEYWORDS = (
    (("健身", "gym", "运动馆"), "dumbbell"),
    (("采购", "招标", "投标", "公告"), "megaphone"),
    (("获客", "线索", "商机", "雷达"), "radar"),
    (("硬件", "芯片", "物联", "设备"), "chip"),
    (("财务", "账本", "账务", "记账", "会计", "发票"), "ledger"),
    (("餐饮", "餐厅", "点餐", "外卖", "美食", "菜谱", "面馆", "火锅", "烧烤", "小吃"), "bowl"),
    (("门店", "零售", "店铺", "商城"), "store"),
    (("调研", "研究", "竞品", "分析"), "magnifier"),
    (("海报", "主视觉", "视觉", "宣传图", "封面"), "palette"),
    (("教程", "读书", "书单", "手册", "课程", "学习", "知识库"), "book"),
    (("投递", "发送", "邮件", "推送", "分发", "传播"), "plane"),
    (("报告", "方案", "合同", "纪要", "公文", "文章", "文档", "清单"), "document"),
)
THEME_KEYWORDS = ((("健身", "gym", "运动馆"), "fitness-gym"),)
THEMES_JSON = SKILL_ROOT / "references" / "themes.json"
# Ant Design blue-7 on blue-1: the neutral fallback when no industry theme matches.
FALLBACK_COLORS = ("#0958D9", "#E6F4FF")


def pick_icon(subject: str, default: str = "grid") -> str:
    lowered = subject.casefold()
    return next((icon for words, icon in ICON_KEYWORDS if any(w in lowered for w in words)), default)


def theme_colors(subject: str, theme: str | None = None, themes_json: Path = THEMES_JSON) -> tuple[str, str]:
    """(primary, lightest tint) of the theme named or matched from the subject; neutral blue when none matches."""
    try:
        themes = json.loads(themes_json.read_text(encoding="utf-8")).get("themes", {})
    except (OSError, ValueError):
        return FALLBACK_COLORS
    lowered = subject.casefold()
    key = theme or next((k for words, k in THEME_KEYWORDS if any(w in lowered for w in words)), None)
    if key is None:
        for name, data in themes.items():
            tokens = re.split(r"[\s/、，,]+", f"{data.get('label', '')}、{data.get('subtype', '')}")
            if any(len(t) >= 2 and t.casefold() in lowered for t in tokens):
                key = name
                break
    data = themes.get(key or "", {})
    if data.get("action") and data.get("actionTint"):
        return data["action"], data["actionTint"]
    return FALLBACK_COLORS


def tab_icon_svg(subject: str, *, icon: str | None = None, theme: str | None = None, default: str = "grid", attrs: str = "") -> str:
    primary, _tint = theme_colors(subject, theme)
    shapes = TAB_ICONS[icon or pick_icon(subject, default)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"{attrs}><rect width="32" height="32" rx="8" fill="{primary}"/>'
            f'<g fill="none" stroke="#FFFFFF" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round">{shapes}</g></svg>')


def tab_icon_href(subject: str, **options) -> str:
    from urllib.parse import quote
    return "data:image/svg+xml," + quote(tab_icon_svg(subject, **options).replace('"', "'"), safe=" =:/,;'.-")


def brand_mark_svg(subject: str, **options) -> str:
    return tab_icon_svg(subject, attrs=' class="brand-mark" width="28" height="28" aria-hidden="true" focusable="false"', **options)


def fill_icon_slots(text: str, subject: str, **options) -> str:
    """Fill {{TAB_ICON}} (the href of <link rel="icon">) and {{BRAND_MARK}} (an inline header mark) in a template."""
    return text.replace("{{TAB_ICON}}", tab_icon_href(subject, **options)).replace("{{BRAND_MARK}}", brand_mark_svg(subject, **options))


def session_subject(session: Path) -> str:
    try:
        manifest = json.loads((session / "99-delivery" / "MANIFEST.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        manifest = {}
    return str(manifest.get("title") or session.parent.name.split("-", 1)[-1])


def clean_title(value: str) -> str:
    value = unicodedata.normalize("NFC", value).strip()
    value = re.sub(r"^\d{3,}[-_\s]+", "", value)
    value = INVALID.sub("-", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"-{2,}", "-", value).strip(" .-")
    value = value[:60].rstrip(" .")
    return value or "未命名会话"


def parse_modes(value: str | None) -> list[str]:
    if not value or value == "none":
        return []
    if value == "all":
        modes = list(MODE_NAMES)
    else:
        modes = [item.strip() for item in value.split(",") if item.strip()]
    elsewhere = [m for m in modes if m in OTHER_SKILL_MODES]
    if elsewhere:
        raise ValueError(f"{', '.join(elsewhere)} belongs to {OTHER_SKILL_MODES[elsewhere[0]]}, not Luz-Design; use that skill")
    unknown = sorted(set(modes) - set(MODE_NAMES))
    if unknown:
        raise ValueError(f"unknown modes: {', '.join(unknown)}")
    return [mode for mode in MODE_NAMES if mode in modes]


def read_template(skill_root: Path, name: str) -> str:
    """Return one block of references/templates.txt (all session templates live in that single file)."""
    text = (skill_root / "references" / "templates.txt").read_text(encoding="utf-8")
    start = f"=== template: {name} ===\n"
    if start not in text:
        raise KeyError(f"template not found in references/templates.txt: {name}")
    body = text.split(start, 1)[1].split("\n=== end ===", 1)[0]
    if name in PAGE_TEMPLATES:
        body = body.replace('<html ', f'<html data-luz-template="{PAGE_TEMPLATES[name]}" ', 1)
    return body + "\n"


def session_page_template_errors(source: Path, template_id: str) -> list[str]:
    """Check the real session shell while allowing its text and theme tokens."""
    name = next((name for name, identifier in PAGE_TEMPLATES.items() if identifier == template_id), None)
    if name is None:
        return [f"不是会话页面模板: {template_id}"]
    text = Path(source).read_text(encoding="utf-8-sig")
    expected = read_template(SKILL_ROOT, name)
    if not re.search(r'<html\b[^>]*\bdata-luz-template=[\"\']' + re.escape(template_id) + r'[\"\']', text, re.I):
        return [f"页面未使用真实 Luz-Design 会话模板 {template_id}；请从 new_session.py 的模板生成页面"]
    def layout_css(value):
        css = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", value, re.I | re.S))
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        # The maintained template explicitly permits changing theme tokens.
        css = re.sub(r":root\s*\{[^}]*\}", "", css)
        return re.sub(r"\s+", "", css)
    if layout_css(text) != layout_css(expected):
        return [f"页面布局样式与真实 Luz-Design 模板 {template_id} 不一致；不能只登记模板名或自写外壳"]
    return []


def write_if_missing(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def init_mode(skill_root: Path, session: Path, mode: str) -> None:
    if mode == "visual":
        base = session / "02-visual"
        for child in ("prompts", "references", "generated"):
            (base / child).mkdir(parents=True, exist_ok=True)
        board = fill_icon_slots(read_template(skill_root, "visual-board.html"), session_subject(session), default="palette")
        write_if_missing(base / "visual-board.html", board)
    elif mode == "document":
        base = session / "03-documents"
        base.mkdir(parents=True, exist_ok=True)
        (base / "outputs").mkdir(parents=True, exist_ok=True)
        document = fill_icon_slots(read_template(skill_root, "document.html"), session_subject(session), default="document")
        write_if_missing(base / "document.html", document)
        # Spec of the summary page for a deliverable that is not a page (make_summary.py); a page deliverable is its own summary page.
        spec = json.loads(read_template(skill_root, "summary.json"))
        spec["title"] = session_subject(session)
        write_if_missing(base / "summary.json", json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    elif mode in OTHER_SKILL_MODES:
        raise ValueError(f"{mode} belongs to {OTHER_SKILL_MODES[mode]}, not Luz-Design; use that skill")
    else:
        raise ValueError(f"unknown mode: {mode}")


def render_brief(skill_root: Path, title: str, session_kind: str) -> str:
    text = read_template(skill_root, "brief.md")
    if session_kind == "standalone_poster":
        text = text.replace("- Session:", f"- Session: {title}", 1)
        text = text.replace("- Request summary:", f"- Request summary: {title}", 1)
    return text


def validate_creation(modes: list[str], session_kind: str) -> None:
    if session_kind in OTHER_SKILL_MODES:
        raise ValueError(f"{session_kind} sessions belong to {OTHER_SKILL_MODES[session_kind]}, not Luz-Design; use that skill")
    if session_kind not in SESSION_KINDS:
        raise ValueError(f"unknown session kind: {session_kind}")
    elsewhere = [mode for mode in modes if mode in OTHER_SKILL_MODES]
    if elsewhere:
        raise ValueError(f"{', '.join(elsewhere)} belongs to {OTHER_SKILL_MODES[elsewhere[0]]}, not Luz-Design; use that skill")
    unknown = sorted(set(modes) - set(MODE_NAMES))
    if unknown:
        raise ValueError(f"unknown modes: {', '.join(unknown)}")
    if "visual" in modes and session_kind != "standalone_poster":
        raise ValueError("visual mode is standalone visual work: pass --standalone-poster and name the task in the title; the functional structure of a product interface belongs to Luz-System and its look is worked from the interface rule cards (context.py interface-visual) in a document session")


def resolve_project(value: str | Path, stage: str | None = None) -> dict:
    """The project a session is made for: its state root (where project.json is) and the folder that keeps the results.

    A path with project.json is the state root; any other path is the project folder, whose state root is the raw\\ of its
    session in the Luz-Project output root. deliver_root of project.json is the project folder; a project without it
    (made before the split) keeps its results at the state root."""
    path = Path(value).resolve()
    state = path
    if not (state / "project.json").is_file():
        state = path / "raw" if (path / "raw" / "project.json").is_file() else PROJECT_OUTPUT_ROOT / path.name / "raw"
    try:
        data = json.loads((state / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"no readable project.json for {value} (looked in {state})") from exc
    deliver = Path(data["deliver_root"]) if isinstance(data, dict) and data.get("deliver_root") else state
    link = {"state_root": str(state), "deliver_root": str(deliver), "delivered": []}
    if data.get("workflow") == "commercial-v1":
        link["workflow"] = data["workflow"]
        link["stage"] = stage or data.get("current_stage") or "design"
    elif stage:
        link["stage"] = stage
    return link


def create_session(
    root: Path,
    title: str,
    modes: list[str],
    *,
    skill_root: Path = SKILL_ROOT,
    session_kind: str = "general",
    cards: list[str] | None = None,
    project: str | Path | None = None,
    project_stage: str | None = None,
) -> Path:
    validate_creation(modes, session_kind)
    project = project or os.environ.get("LUZ_PROJECT_ROOT")
    if project_stage and not project:
        raise ValueError("--stage 需要关联项目上下文")
    project_link = resolve_project(project, project_stage) if project else None
    import context
    kinds = list(dict.fromkeys(cards or [DEFAULT_CARDS[m] for m in modes if m in DEFAULT_CARDS]))
    unknown_cards = sorted(set(kinds) - set(context.card_kinds()))
    if unknown_cards:
        raise ValueError(f"unknown rule card: {', '.join(unknown_cards)}; see scripts/context.py list")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    clean = clean_title(title)
    if session_kind == "standalone_poster" and not POSTER_TASK_RE.search(clean):
        raise ValueError("standalone poster session title must explicitly describe a poster task")
    sequences = []
    for item in root.iterdir():
        match = SESSION_RE.match(item.name) or LEGACY_SESSION_RE.match(item.name)
        if item.is_dir() and match:
            sequences.append(int(match.group(1)))
    next_sequence = max(sequences, default=0) + 1

    while True:
        folder = root / f"{next_sequence:03d}-{clean}"
        try:
            folder.mkdir()
            break
        except FileExistsError:
            next_sequence += 1

    try:
        created = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
        session_id = f"SES-{next_sequence:03d}"
        work = folder / "raw"
        work.mkdir()
        (work / "BRIEF.md").write_text(render_brief(skill_root, clean, session_kind), encoding="utf-8")

        delivery = work / "99-delivery"
        delivery.mkdir()
        approvals = json.loads(read_template(skill_root, "approvals.json"))
        if session_kind == "standalone_poster":
            approvals["standalone_poster"]["status"] = "requested"
        (delivery / "APPROVALS.json").write_text(
            json.dumps(approvals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        manifest = json.loads(read_template(skill_root, "manifest.json"))
        manifest.update({
            "session_id": session_id,
            "sequence": next_sequence,
            "folder": folder.name,
            "title": clean,
            "created_at": created,
            "session_kind": session_kind,
            "modes": modes,
            "output_standard": OUTPUT_STANDARD,
            "project": project_link,
        })
        (delivery / "MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for mode in modes:
            init_mode(skill_root, work, mode)
        # The rules, preferences, lessons, tools and checks for this task, cut from the rule pages (read before producing).
        for kind in kinds:
            context.save_card(work, kind)
        # Reserve exact, real template sources. Scaffold creation is internal;
        # business generators/publish still require their own stage evidence.
        from template_library import select as select_design_template
        business_stage = (project_link.get("stage") or "design") if project_link else os.environ.get("LUZ_CRAWL_STAGE") or "design"
        summary_stage = business_stage if project_link else os.environ.get("LUZ_CRAWL_STAGE") or "summary"
        select_design_template(folder, "luz-design", summary_stage, "reading-html", f"{folder.name}.html")
        for mode in modes:
            filename = "visual-board.html" if mode == "visual" else "document.html"
            subfolder = "02-visual" if mode == "visual" else "03-documents"
            select_design_template(folder, "luz-design", business_stage, PAGE_TEMPLATES[filename], f"raw/{subfolder}/{filename}")
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return folder


def print_icon(argv: list[str]) -> int:
    """`new_session.py icon NAME [--icon KEY] [--theme KEY]`: print the tab-icon link and an inline brand mark."""
    parser = argparse.ArgumentParser(prog="new_session.py icon", description="Print the tab icon and brand mark for a page or system name.")
    parser.add_argument("name", help="Page or system name; the pictogram and theme colour are chosen from its keywords")
    parser.add_argument("--icon", choices=sorted(TAB_ICONS), help="Override the pictogram")
    parser.add_argument("--theme", help="Override the theme key in references/themes.json")
    args = parser.parse_args(argv)
    options = {"icon": args.icon, "theme": args.theme}
    print(f'<link rel="icon" href="{tab_icon_href(args.name, **options)}">')
    print(brand_mark_svg(args.name, **options))
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["icon"]:
        return print_icon(argv[1:])
    parser = argparse.ArgumentParser(description="Create the next Luz Design session folder; `icon NAME` prints the tab icon and brand mark.")
    parser.add_argument("--name", required=True, help="Readable session title")
    parser.add_argument("--modes", default="", help="visual (with --standalone-poster) or document; system design and prototypes belong to Luz-System")
    parser.add_argument("--session-kind", choices=SESSION_KINDS, default="general")
    parser.add_argument("--standalone-poster", action="store_true", help="Standalone visual work (poster, brand key visual, campaign image); required for visual mode")
    parser.add_argument("--root", help="Output root override, primarily for tests")
    parser.add_argument("--card", action="append", help="Rule card kind for this task (repeatable); the kinds are listed by scripts/context.py list; default from the mode")
    parser.add_argument("--stage", help="项目矩阵当前协作阶段，如 design 或 demo")
    parser.add_argument("--project", help="The project this task is for (its project folder, or the state root that holds project.json): deliverables are written into the project's docs and the session root keeps only raw\\ and the summary page")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else OUTPUT_ROOT
    kind = "standalone_poster" if args.standalone_poster else args.session_kind
    try:
        folder = create_session(root, args.name, parse_modes(args.modes), session_kind=kind, cards=args.card, project=args.project, project_stage=args.stage)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(str(folder))
    cards = sorted((folder / "raw" / "00-rules").glob("*.md"))
    if cards:
        print("NEXT: read the rule card(s) before producing anything, then fill BRIEF 采用的规则:", file=sys.stderr)
        for card in cards:
            print(f"  {card}", file=sys.stderr)
    print("LAYOUT: root = raw\\ + summary page " + folder.name + ".html; " + (
        "deliverables go to the project's docs (publish.py --as, deliver.py --to)" if (args.project or os.environ.get("LUZ_PROJECT_ROOT")) else
        "a page deliverable is published as the summary page (publish.py), other files are placed with deliver.py and listed in a summary page made with make_summary.py"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
