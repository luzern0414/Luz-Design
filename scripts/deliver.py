#!/usr/bin/env python3
"""Place a checked deliverable that is not a page: in the session root, or in the project's docs for a project task.

  py -X utf8 scripts/deliver.py <会话目录> <成品文件> [--as <名称>] [--to 01-需求对接|03-验收交付] [--replace]

No project: the file is copied into the session root next to raw\\ and the summary page, under the name it should have
(门店销售表.xlsx); the summary page lists it (make_summary.py).
A project (new_session.py --project): --to and --as NN-名称 are required; the file is written to
docs\\<--to>\\NN-名称.<扩展名> of the project folder, the session root keeps no copy, and the summary page names the path.
Pages (HTML) go through publish.py, which checks them first; the checks of other formats (check_document.py, check_pdf.py)
run before this script.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import check_output_layout as layout
from validate_session import project_link, sha256_file, work_dir

PROJECT_DIRS = ("01-需求对接", "03-验收交付")   # 02-产品开发 takes pages only, through publish.py
BAD_NAME = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def _stem(name: str, ext: str) -> str:
    return name[: -len(ext)] if name.lower().endswith(ext) else name


def deliver(folder: Path, source: Path, *, as_name: str | None = None, to: str | None = None, replace: bool = False) -> Path:
    folder = folder.resolve()
    source = Path(source).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"deliverable not found: {source}")
    ext = source.suffix.lower()
    if ext == ".html":
        raise ValueError("a page is published with scripts/publish.py (it checks the page first); deliver.py places files of other formats")
    manifest_path = work_dir(folder) / "99-delivery" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    link = project_link(manifest)
    from crawl_gate import require_session_preflight, record_template_output
    from template_library import require_selected
    context = require_session_preflight(folder, source)
    if not source.is_relative_to(context["raw"]):
        raise ValueError("deliver.py 的源文件必须在本会话 raw 中；先将待检查的成品放入会话")
    from ui_entry_policy import check_nonpage_delivery
    check_nonpage_delivery(source, folder)
    source_selection = require_selected(context["template_root"], context["caller"], context["stage"], source, phase="post")
    template_id = source_selection["id"]
    if link is None:
        if to:
            raise ValueError("--to is for a session made with --project; this session keeps its deliverables in the root")
        if ext not in layout.DELIVERABLE_EXT:
            raise ValueError(f"{ext or 'a file without extension'} is not a deliverable format ({', '.join(sorted(layout.DELIVERABLE_EXT))})")
        name = as_name or source.name
        name = name if Path(name).suffix.lower() == ext else name + ext
        if BAD_NAME.search(name):
            raise ValueError(f"{name} cannot be the name of a deliverable (no \\ / : * ? \" < > |)")
        target = folder / name
        if target.exists() and target != source and not replace:
            raise FileExistsError(f"{name} is already in the session root; use --replace to overwrite it")
        target_context = require_session_preflight(folder, target, template_id=template_id)
        if target != source:
            shutil.copyfile(source, target)
        record_template_output(target_context, target, template_id, generator="Luz-Design/scripts/deliver.py")
        return target
    commercial = link.get("workflow") == "commercial-v1"
    choices = ("02-对接资料",) if commercial else PROJECT_DIRS
    dirs = layout.COMMERCIAL_DOC_DIRS if commercial else layout.DOC_DIRS
    if to not in choices:
        raise ValueError(f"this session is for a project: pass --to {' or '.join(choices)} (pages go through publish.py --as)")
    if ext not in dirs[to]:
        raise ValueError(f"docs/{to} takes {', '.join(sorted(e[1:].upper() for e in dirs[to]))} only, not {ext}")
    stem = _stem(as_name or "", ext)
    if not layout.DOC_FILE.match(stem) or BAD_NAME.search(stem):
        raise ValueError(f"--as must look like NN-名称 (two-digit number, hyphen, name), got {as_name!r}")
    deliver_root = Path(str(link.get("deliver_root") or ""))
    target = deliver_root / "docs" / to / f"{stem}{ext}"
    relative = target.relative_to(deliver_root).as_posix()
    delivered = [entry for entry in link.get("delivered", []) if isinstance(entry, dict)]
    if target.exists() and not replace and not any(entry.get("path") == relative for entry in delivered):
        raise FileExistsError(f"{relative} already exists in the project and was not written by this session; choose another number or use --replace")
    target_context = require_session_preflight(folder, target, template_id=template_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    link["delivered"] = [entry for entry in delivered if entry.get("path") != relative] + [{
        "path": relative,
        "sha256": sha256_file(target),
        "delivered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }]
    manifest["project"] = link
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record_template_output(target_context, target, template_id, generator="Luz-Design/scripts/deliver.py")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session", help="Numbered session folder")
    parser.add_argument("file", help="The checked deliverable (usually under raw\\03-documents\\outputs\\)")
    parser.add_argument("--as", dest="as_name", metavar="NAME", help="Name in the root (default: the file's own name); NN-名称 for a project")
    parser.add_argument("--to", choices=(*PROJECT_DIRS, "02-对接资料"), help="Project sessions: the docs folder")
    parser.add_argument("--replace", action="store_true", help="Overwrite a file of the same name")
    args = parser.parse_args(argv)
    try:
        target = deliver(Path(args.session), Path(args.file), as_name=args.as_name, to=args.to, replace=args.replace)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"DELIVERED: {target}")
    shown = target.name if target.parent == Path(args.session).resolve() else "docs\\" + args.to + "\\" + target.name
    print(f"LIST IN SUMMARY (位置): {shown}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
