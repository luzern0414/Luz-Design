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
        write_if_missing(base / "visual-board.html", read_template(skill_root, "visual-board.html"))
    elif mode == "document":
        base = session / "03-documents"
        base.mkdir(parents=True, exist_ok=True)
        (base / "outputs").mkdir(parents=True, exist_ok=True)
        write_if_missing(base / "document.html", read_template(skill_root, "document.html"))
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create the next Luz Design session folder.")
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
