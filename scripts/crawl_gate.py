"""Resolve a Design session and verify the shared Crawl evidence before output.

CLI builders call ``require_session_preflight`` before creating files. Read-only
checks and pure rendering functions do not call it or start new research tasks.
"""
from __future__ import annotations
import importlib.util
import json
import os
import re
from pathlib import Path


def _preflight_module():
    root = Path(os.environ.get("LUZ_CRAWL_ROOT") or Path(__file__).resolve().parents[2] / "Luz-Crawl")
    source = root / "scripts" / "crawl_preflight.py"
    if not source.is_file():
        raise ValueError(f"Crawl 前置检索校验器不存在: {source}")
    spec = importlib.util.spec_from_file_location("_luz_crawl_preflight", source)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法加载 Crawl 前置检索校验器: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"无法读取会话或项目记录 {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"会话或项目记录必须是 JSON 对象: {path}")
    return value


def _session_from(path: Path):
    """Locate the nearest manifest; an invalid inner manifest cannot fall through."""
    path = path.resolve()
    if path.is_file():
        path = path.parent
    for parent in (path, *path.parents):
        current = parent / "raw" / "99-delivery" / "MANIFEST.json"
        legacy = parent / "99-delivery" / "MANIFEST.json"
        if current.is_file():
            return parent, parent / "raw", current, _json(current)
        if legacy.is_file():
            folder = parent.parent if parent.name == "raw" else parent
            return folder, parent, legacy, _json(legacy)
    return None


def _project_context(link, module):
    if not link:
        return None
    if isinstance(link, str):
        value = Path(link).resolve()
    elif isinstance(link, dict):
        reference = link.get("state_root") or link.get("deliver_root")
        if not reference:
            raise ValueError("MANIFEST.json project 缺少项目路径")
        value = Path(str(reference)).resolve()
    else:
        raise ValueError("MANIFEST.json project 必须是项目路径或关联对象")
    state = module.state_root(value)
    if state is None:
        raise ValueError(f"关联项目缺少 project.json: {value}")
    state = Path(state).resolve()
    data = _json(state / "project.json")
    declared = Path(str(data.get("deliver_root") or state))
    deliver = (declared if declared.is_absolute() else state / declared).resolve()
    if isinstance(link, dict) and link.get("deliver_root"):
        stored = Path(str(link["deliver_root"])).resolve()
        if stored != deliver:
            raise ValueError("MANIFEST.json project.deliver_root 与项目状态根不一致")
    stage = link.get("stage") if isinstance(link, dict) else None
    if stage is not None and (not isinstance(stage, str) or not stage.strip()):
        raise ValueError("MANIFEST.json project.stage 必须是非空阶段名称")
    stage = stage or "design"
    stages = data.get("stages")
    if stages:
        owner = next((item.get("owner") for item in stages
                      if isinstance(item, dict) and item.get("id") == stage), None)
        if owner != "luz-design":
            raise ValueError(f"Design 会话关联阶段的负责技能不是 luz-design: {stage}")
    return {"state_root": state, "deliver_root": deliver, "stage": stage}


def _context(session=None, output=None, *, caller="luz-design", stage=None, require_session=True):
    module = _preflight_module()
    seed = session or os.environ.get("LUZ_DESIGN_SESSION") or output
    if seed is None:
        raise ValueError("正式输出需要 --session、LUZ_DESIGN_SESSION 或输出祖先中的真实 Design 会话；先运行 new_session.py")
    found = _session_from(Path(seed))
    if found is None:
        # Read-only callers may check a project state root directly. Builders
        # still need the numbered Design session that owns their source files.
        state = module.state_root(Path(seed).resolve())
        if require_session or state is None:
            raise ValueError(f"未找到真实 Design 会话 MANIFEST.json: {seed}；先运行 new_session.py")
        project = _project_context(str(state), module)
        evidence_root = project["state_root"]
        actual_stage = stage or "design"
        return module, {"session": None, "raw": None, "project": project["deliver_root"],
                        "evidence_root": evidence_root, "template_root": evidence_root,
                        "caller": caller, "stage": actual_stage,
                        "record": module.record_path(evidence_root, caller, actual_stage)}
    folder, raw, manifest_file, manifest = found
    if caller != "luz-design":
        raise ValueError("Design 会话的负责技能 caller 固定为 luz-design")
    if (manifest.get("schema_version") not in {"2.0", "3.0"}
            or not re.fullmatch(r"SES-\d{2,}", str(manifest.get("session_id", "")))
            or manifest.get("folder") != folder.name
            or not manifest.get("title") or not manifest.get("created_at")
            or not isinstance(manifest.get("modes"), list)
            or not set(manifest["modes"]) <= {"visual", "document"}
            or manifest.get("session_kind") not in {"general", "standalone_poster"}
            or not (raw / "BRIEF.md").is_file()
            or not any((raw / "00-rules").glob("*.md"))):
        raise ValueError(f"无效 Design 会话，不能用临时目录代替 new_session.py 会话: {manifest_file}")
    project = _project_context(manifest.get("project"), module)
    evidence_root = project["state_root"] if project else folder
    linked_stage = project["stage"] if project else None
    if stage is not None and linked_stage is not None and stage != linked_stage:
        raise ValueError("--stage 与会话关联的项目阶段不一致")
    actual_stage = linked_stage if project else (stage or os.environ.get("LUZ_CRAWL_STAGE") or "design")
    project_output = (project is not None and output is not None
                      and Path(output).resolve().is_relative_to(project["deliver_root"] / "docs"))
    return module, {"session": folder, "raw": raw,
                    "project": project["deliver_root"] if project else None,
                    "evidence_root": evidence_root,
                    # Raw drafts and the session summary remain owned by the
                    # Design session. Only project docs bind templates there.
                    "template_root": evidence_root if project_output else folder,
                    "caller": caller, "stage": actual_stage,
                    "record": module.record_path(evidence_root, caller, actual_stage)}


def _output_errors(context: dict, output) -> list[str]:
    if output is None:
        return []
    import check_output_layout as layout
    target = Path(output).resolve()
    raw, folder, project = context["raw"], context["session"], context["project"]
    if target != raw and target.is_relative_to(raw):
        return []
    if target.parent == folder and target.name == f"{folder.name}.html":
        return []
    if project is None:
        if target.parent == folder and target.suffix.lower() in layout.DELIVERABLE_EXT:
            return []
    else:
        for name, extensions in layout.DOC_DIRS.items():
            if (target.parent == project / "docs" / name and target.suffix.lower() in extensions
                    and layout.DOC_FILE.fullmatch(target.stem)):
                return []
    return [f"输出超出会话 raw 或合法成果路径: {target}；源文件与过程文件必须留在会话 raw，项目成果只进入规定 docs 目录"]


def require_session_preflight(session=None, output=None, caller="luz-design", stage=None, template_id=None) -> dict:
    """Return resolved Paths only after current body evidence and boundaries pass.

    Never creates a session, runs Crawl, records approval or writes an output.
    The returned ``record`` is the exact validated research record for provenance.
    """
    module, context = _context(session, output, caller=caller, stage=stage)
    errors = _output_errors(context, output)
    errors.extend(module.validate_preflight(context["evidence_root"], caller, context["stage"]))
    if errors:
        raise ValueError("; ".join(errors))
    if template_id and output is not None:
        from template_library import require_selected
        require_selected(context["template_root"], caller, context["stage"], Path(output), template_id)
    return context


def record_template_output(context: dict, output, template_id: str, *, generator: str = ""):
    """Record the bytes written by a Design generator after its checks pass."""
    if not template_id:
        return None
    from template_library import record_output
    return record_output(context["template_root"], context["caller"], context["stage"], Path(output), template_id,
                         generator=generator or "Luz-Design generator")


def crawl_errors(session, stage=None, caller=None):
    """Read-only gate, including sessions linked to a project's state directory."""
    caller = caller or Path(__file__).resolve().parents[1].name.lower()
    try:
        module, context = _context(session, caller=caller, stage=stage, require_session=False)
        return module.validate_preflight(context["evidence_root"], caller, context["stage"])
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [str(exc)]

