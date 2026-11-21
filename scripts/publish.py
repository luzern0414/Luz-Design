#!/usr/bin/env python3
"""Publish one stage artifact (an HTML page) as the deliverable of the session.

A task without a project: the page becomes the summary page <session>/<session-folder>.html, the only HTML in the root next
to raw/. A task for a project (new_session.py --project): the page is written to the project's docs/02-产品开发/NN-名称.html
(--as NN-名称) and the root keeps raw/ and a summary page made with make_summary.py.

Refuses a session without a current rule card, 采用的规则 or fresh 本次沉淀, a page that fails check_document.py, a page that
fails the layout check (check_output_layout.py session) and a visual board that a person has not approved in
raw/99-delivery/APPROVALS.json with its current SHA-256.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from validate_session import (
    STAGE_PATHS,
    final_html,
    project_link,
    read_manifest,
    sha256_file,
    uses_output_standard,
    validate_approval_record,
    validate_light_html,
    work_dir,
)

PROJECT_PAGE_DIR = "02-产品开发"   # docs folder of the pages that development produces; its files are named NN-名称.html

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


def document_errors(source: Path, allow: list[str] | None, *, session=None, delivery_target=None) -> list[str]:
    """check_document.py on the page that is about to be published; --allow passes on what the user asked for."""
    import check_document
    from ui_entry_policy import html_delivery_contract
    try:
        contract = html_delivery_contract(source, session=session, allow=allow, delivery_target=delivery_target)
    except (OSError, ValueError) as exc:
        return [f'UI admission: {exc}']
    if contract['kind'] in {'frontend-ui', 'component-ui'}:
        return []  # Deterministic reconstruction and current browser proof are required.
    saved = set(check_document.ALLOWED)
    check_document.ALLOWED.clear()
    check_document.ALLOWED.update(kind.strip() for value in (allow or []) for kind in value.split(",") if kind.strip())
    if "website" in check_document.ALLOWED:
        check_document.ALLOWED.add("interface")
    errors: list[str] = []
    try:
        check_document.check_html(source, errors, [], session=session)
    finally:
        check_document.ALLOWED.clear()
        check_document.ALLOWED.update(saved)
    return [f"check_document: {e}" for e in errors]


def project_page_target(link: dict, as_name: str | None) -> Path:
    """Resolve a numbered HTML page in the linked project's development documents."""
    import check_output_layout
    area = "03-开发资料" if link.get("workflow") == "commercial-v1" else PROJECT_PAGE_DIR
    if not as_name:
        raise ValueError(f"name the project page with --as NN-名称 to write it to docs/{area}/")
    name = as_name[:-5] if as_name.lower().endswith(".html") else as_name
    if not check_output_layout.DOC_FILE.match(name) or re.search(r'[\\/:*?"<>|]', name):
        raise ValueError(f"--as must look like NN-名称 (two-digit number, hyphen, name), got {as_name}")
    return Path(str(link.get("deliver_root") or "")) / "docs" / area / f"{name}.html"


def publish(folder: Path, stage: str, allow: list[str] | None = None, as_name: str | None = None) -> Path:
    folder = folder.resolve()
    work = work_dir(folder)
    if stage not in STAGE_PATHS:
        raise ValueError(f"stage must be one of: {', '.join(STAGE_PATHS)}")
    source = work / STAGE_PATHS[stage]
    if not source.is_file():
        raise FileNotFoundError(f"missing stage artifact: raw/{STAGE_PATHS[stage]}")
    link = project_link(read_manifest(folder))
    project_target = project_page_target(link, as_name) if link else None
    errors: list[str] = []
    # Work starts from a current rule card and the BRIEF names the rules it applied (scripts/context.py).
    from crawl_gate import require_session_preflight, record_template_output
    from template_library import require_selected
    from new_session import session_page_template_errors
    from style_match import session_style_errors
    template_id = {"visual": "design-visual-board", "document": "design-document-page"}.get(stage, "reading-html")
    try:
        source_context = require_session_preflight(folder, source)
        session_template = template_id in {"design-visual-board", "design-document-page"}
        require_selected(source_context["template_root"], source_context["caller"], source_context["stage"], source,
                         template_id, phase="pre" if session_template else "post")
        if session_template:
            errors.extend(session_page_template_errors(source, template_id))
        context = require_session_preflight(folder, project_target or final_html(folder), template_id=template_id)
    except ValueError as exc:
        errors.append(str(exc))
    from ui_entry_policy import html_delivery_contract
    try:
        contract = html_delivery_contract(source, session=folder, allow=allow,
                                          delivery_target=project_target or final_html(folder))
        if contract['kind'] in {'frontend-ui', 'component-ui'}:
            errors.append('界面包必须保持完整文件树；通过普通汇总页链接界面包，不能只复制入口 HTML')
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    allowed = {kind.strip() for value in (allow or []) for kind in value.split(",") if kind.strip()}
    errors.extend(session_style_errors(folder, required=bool(allowed & {"interface", "website"})))
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
    errors.extend(e for e in document_errors(source, allow, session=folder,
                  delivery_target=project_target or final_html(folder)) if e not in errors)
    if stage in APPROVED_STAGES:
        errors.extend(approval_errors(work, stage, source))
    if errors:
        raise ValueError("stage artifact fails the HTML contract: " + "; ".join(errors))
    record_template_output(source_context, source, template_id,
                           generator=f"Luz-Design/scripts/new_session.py:{stage}; publish.py shell/document checks")
    manifest_path = work / "99-delivery" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = {
        "stage": stage,
        "source": STAGE_PATHS[stage],
        "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "allowed": sorted(allowed),
    }
    if project_target is not None:
        relative = project_target.relative_to(Path(str(link.get("deliver_root")))).as_posix()
        delivered = [entry for entry in link.get("delivered", []) if isinstance(entry, dict)]
        if project_target.exists() and not any(entry.get("path") == relative for entry in delivered):
            raise ValueError(f"{relative} already exists in the project and was not written by this session; choose another number or name")
        project_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, project_target)
        link["delivered"] = [entry for entry in delivered if entry.get("path") != relative] + [
            {"path": relative, "sha256": sha256_file(project_target), **record}]
        manifest["project"] = link
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        record_template_output(context, project_target, template_id, generator=f"Luz-Design/scripts/publish.py:{stage}")
        return project_target
    for item in folder.iterdir():
        if item.is_file() and item.suffix.lower() == ".html" and item != final_html(folder):
            raise ValueError(f"unexpected HTML at the session root: {item.name}")
    target = final_html(folder)
    previous = target.read_bytes() if target.is_file() else None
    shutil.copyfile(source, target)
    # The page is the summary page: the session root is checked as a whole (an older session is only given notes).
    import check_output_layout
    problems, hints = check_output_layout.check_session(folder, False)
    if problems and uses_output_standard(manifest):
        if previous is None:
            target.unlink()
        else:
            target.write_bytes(previous)
        raise ValueError("the page does not fit the session layout: " + "; ".join(problems))
    for message in problems + hints:
        print(f"NOTE {message}", file=sys.stderr)
    manifest["final"] = {"path": target.name, "sha256": sha256_file(target), **record}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record_template_output(context, target, template_id, generator=f"Luz-Design/scripts/publish.py:{stage}")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", help="Numbered session folder in the output root")
    parser.add_argument("stage", choices=sorted(STAGE_PATHS), help="Stage artifact to publish")
    parser.add_argument("--allow", action="append", default=[], metavar="KIND",
                        help="passed to check_document.py: only kinds the user explicitly asked for (see its --help)")
    parser.add_argument("--as", dest="as_name", metavar="NN-名称",
                        help="project sessions only: the file name in the project's development document folder (two-digit number, hyphen, name)")
    args = parser.parse_args(argv)
    try:
        target = publish(Path(args.session), args.stage, args.allow, args.as_name)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PUBLISHED: {target}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
