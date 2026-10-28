#!/usr/bin/env python3
"""Create the next immutable-numbered Luz Design session workspace."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
# The skill holds rules, templates and scripts; every session it creates is an output and lives here.
OUTPUT_ROOT = Path(r"D:\Codes\skill输出\Luz-Design")
SESSION_RE = re.compile(r"^(\d{3,})-(.+)$")
INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
# Luz-Design owns standalone visual work (posters, brand key visuals, campaign images) and document layout.
# System design, product UI, interactive prototypes and hardware belong to Luz-System (D:\Codes\Luz-System).
MODE_NAMES = ("visual", "document")
OTHER_SKILL_MODES = {"system": "Luz-System", "prototype": "Luz-System", "hardware": "Luz-System"}
POSTER_TASK_RE = re.compile(r"海报|poster|主视觉|品牌视觉|宣传图|视觉方向|活动视觉|封面|KV", re.I)
SESSION_KINDS = ("general", "standalone_poster")

# Tab icon (references/visual-design.html 网页图标与品牌标识): every delivered HTML carries one flat line pictogram of its
# subject, primary-colour strokes on a rounded square in the theme's lightest tint, 32×32, at most three shapes, no text.
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
}
# First match wins; the subject (system name or page title) is matched case-insensitively.
ICON_KEYWORDS = (
    (("健身", "gym", "运动馆"), "dumbbell"),
    (("采购", "招标", "投标", "公告"), "megaphone"),
    (("获客", "线索", "商机", "雷达"), "radar"),
    (("硬件", "芯片", "物联", "设备"), "chip"),
    (("财务", "账本", "账务", "记账", "会计", "发票"), "ledger"),
    (("门店", "零售", "店铺", "商城"), "store"),
    (("调研", "研究", "竞品", "分析"), "magnifier"),
    (("海报", "主视觉", "视觉", "宣传图", "封面"), "palette"),
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
    primary, tint = theme_colors(subject, theme)
    shapes = TAB_ICONS[icon or pick_icon(subject, default)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"{attrs}><rect width="32" height="32" rx="8" fill="{tint}"/>'
            f'<g fill="none" stroke="{primary}" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round">{shapes}</g></svg>')


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
    return body + "\n"


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
        raise ValueError("visual mode is standalone visual work: pass --standalone-poster and name the task in the title; product visuals belong to Luz-System")


def create_session(
    root: Path,
    title: str,
    modes: list[str],
    *,
    skill_root: Path = SKILL_ROOT,
    session_kind: str = "general",
) -> Path:
    validate_creation(modes, session_kind)
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    clean = clean_title(title)
    if session_kind == "standalone_poster" and not POSTER_TASK_RE.search(clean):
        raise ValueError("standalone poster session title must explicitly describe a poster task")
    sequences = []
    for item in root.iterdir():
        match = SESSION_RE.match(item.name)
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
        })
        (delivery / "MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for mode in modes:
            init_mode(skill_root, work, mode)
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
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else OUTPUT_ROOT
    kind = "standalone_poster" if args.standalone_poster else args.session_kind
    try:
        folder = create_session(root, args.name, parse_modes(args.modes), session_kind=kind)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(str(folder))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
