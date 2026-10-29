#!/usr/bin/env python3
"""Publish one stage artifact as the session's single final HTML: <session>/<session-folder>.html.

Refuses a session without a current rule card, 采用的规则 or fresh 本次沉淀, a page that fails check_document.py, and a
visual board that a person has not approved in raw/99-delivery/APPROVALS.json with its current SHA-256.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from validate_session import (
    STAGE_PATHS,
    final_html,
    sha256_file,
    validate_approval_record,
    validate_light_html,
    work_dir,
)

# Stages a person approves before they are published (SKILL.md Sessions; visual-design.html 质量门禁).
APPROVED_STAGES = {"visual"}


def approval_errors(work: Path, stage: str, source: Path) -> list[str]:
    """The stage is approved by a person in raw/99-delivery/APPROVALS.json for the artifact as it is now."""
    path = work / "99-delivery" / "APPROVALS.json"
    try:
        item = json.loads(path.read_text(encoding="utf-8")).get(stage)
    except (OSError, ValueError, AttributeError):
        return [f"cannot read {path}"]
    if not isinstance(item, dict) or item.get("status") != "approved":
        return [f"the {stage} stage is not approved by a person in raw/99-delivery/APPROVALS.json; stop and ask for approval"]
    errors: list[str] = []
    validate_approval_record(work, stage, item, errors)
    if item.get("artifact_sha256") != sha256_file(source):
        errors.append(f"the approved {stage} hash differs from {source.name}; the changed artifact needs a new approval")
    return sorted(set(errors))


def document_errors(source: Path, allow: list[str] | None) -> list[str]:
    """check_document.py on the page that is about to be published; --allow passes on what the user asked for."""
    import check_document
    saved = set(check_document.ALLOWED)
    check_document.ALLOWED.clear()
    check_document.ALLOWED.update(kind.strip() for value in (allow or []) for kind in value.split(",") if kind.strip())
    if "website" in check_document.ALLOWED:
        check_document.ALLOWED.add("interface")
    errors: list[str] = []
    try:
        check_document.check_html(source, errors, [])
    finally:
        check_document.ALLOWED.clear()
        check_document.ALLOWED.update(saved)
    return [f"check_document: {e}" for e in errors]


def publish(folder: Path, stage: str, allow: list[str] | None = None) -> Path:
    folder = folder.resolve()
    work = work_dir(folder)
    if stage not in STAGE_PATHS:
        raise ValueError(f"stage must be one of: {', '.join(STAGE_PATHS)}")
    source = work / STAGE_PATHS[stage]
    if not source.is_file():
        raise FileNotFoundError(f"missing stage artifact: raw/{STAGE_PATHS[stage]}")
    errors: list[str] = []
    # Work starts from a current rule card and the BRIEF names the rules it applied (scripts/context.py).
    from validate_session import rule_card_errors, sediment_errors
    errors.extend(rule_card_errors(work, require_adopted=True, check_current=True))
    # Every call leaves experience behind (SKILL.md 每次调用后沉淀): notes written or confirmed for this session.
    created = json.loads((work / "99-delivery" / "MANIFEST.json").read_text(encoding="utf-8")).get("created_at", "")
    errors.extend(sediment_errors(work, str(created)[:10]))
    # Visual boards and reading pages keep the 14px floor (visual-design.html 字体与字号).
    validate_light_html(source, errors)
    # Every delivered HTML carries its own browser-tab icon (visual-design.html 网页图标与品牌标识).
    from check_document import tab_icon_findings
    errors.extend(tab_icon_findings(source.read_text(encoding="utf-8"))[0])
    # The page passes the document checks, and an approval stage is approved for exactly this artifact.
    errors.extend(e for e in document_errors(source, allow) if e not in errors)
    if stage in APPROVED_STAGES:
        errors.extend(approval_errors(work, stage, source))
    if errors:
        raise ValueError("stage artifact fails the HTML contract: " + "; ".join(errors))
    for item in folder.iterdir():
        if item.is_file() and item.suffix.lower() == ".html" and item != final_html(folder):
            raise ValueError(f"unexpected HTML at the session root: {item.name}")
    target = final_html(folder)
    shutil.copyfile(source, target)
    manifest_path = work / "99-delivery" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["final"] = {
        "path": target.name,
        "stage": stage,
        "source": STAGE_PATHS[stage],
        "sha256": sha256_file(target),
        "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", help="Numbered session folder in the output root")
    parser.add_argument("stage", choices=sorted(STAGE_PATHS), help="Stage artifact to publish")
    parser.add_argument("--allow", action="append", default=[], metavar="KIND",
                        help="passed to check_document.py: only kinds the user explicitly asked for (see its --help)")
    args = parser.parse_args(argv)
    try:
        target = publish(Path(args.session), args.stage, args.allow)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PUBLISHED: {target}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
