"""Describe and bind real Luz-Design templates; declarations cannot register new layouts.

list / describe are read-only. select writes only to the caller's process directory.
A UI package is verified by ui_package.py check with the current Crawl evidence of its stage.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "template-library.json"
CALLERS = {"luz-project", "luz-system", "luz-design", "luz-dev", "luz-ops", "luz-writing", "luz-crawl"}
STAGE_RE = re.compile(r"[a-z0-9][a-z0-9-]*\Z")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def reference(identifier, applies_to):
    entries = read(CATALOG)["templates"]
    if identifier not in entries:
        raise ValueError(f"未登记的 Luz-Design 模板：{identifier}；先运行 template_library.py list")
    if not isinstance(applies_to, str) or not applies_to.strip():
        raise ValueError("模板必须绑定具体的输出位置 applies_to")
    files = []
    for relative in entries[identifier]["files"]:
        file = (ROOT / relative).resolve()
        if not file.is_relative_to(ROOT.resolve()) or not file.is_file():
            raise ValueError(f"Design 模板文件不存在或越界：{relative}")
        files.append({"path": relative, "sha256": digest(file)})
    return {"id": identifier, "applies_to": applies_to.strip(), "files": files}


def validate_references(values):
    if not isinstance(values, list) or not values:
        return ["缺少实际选择的 Luz-Design template_uses"]
    errors = []
    seen = set()
    for item in values:
        try:
            expected = reference(item["id"], item["applies_to"])
            key = (item["id"], item["applies_to"])
            if key in seen:
                raise ValueError("重复模板选择")
            seen.add(key)
            if item.get("files") != expected["files"]:
                raise ValueError("模板文件集合或 SHA-256 不符；重新读取真实模板并登记")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            errors.append(f"Luz-Design 模板依据无效：{exc}")
    return errors


def _record_path(session, caller, stage):
    """Return the process record for one caller/stage without creating it."""
    if caller not in CALLERS:
        raise ValueError("未知 caller")
    if not isinstance(stage, str) or not STAGE_RE.fullmatch(stage):
        raise ValueError("正式输出必须绑定具体 stage（小写字母、数字与短横线）")
    session = Path(session).resolve()
    raw = session if (session / "project.json").is_file() else session / "raw"
    suffix = f"-{stage}" if stage else ""
    return raw / "00-design" / f"{caller}{suffix}.json"


def _snapshot_errors(record_path, value):
    """Verify that a selection kept a local snapshot of every catalog file.

    The catalog hash alone proves the current checkout, while the snapshot
    makes a selection independently auditable after the checkout changes.
    ``select`` always writes this field; old hand-written records are refused
    by the formal-output gate rather than silently upgraded.
    """
    errors = []
    if not isinstance(value, dict):
        return ["模板选择记录必须是 JSON 对象"]
    for item in value.get("template_uses") or []:
        identifier = item.get("id") if isinstance(item, dict) else None
        files = item.get("files") if isinstance(item, dict) else None
        snapshots = item.get("snapshots") if isinstance(item, dict) else None
        if (not isinstance(files, list) or not files
                or any(not isinstance(f, dict) or not isinstance(f.get("path"), str)
                       or not f["path"].strip() or Path(f["path"]).is_absolute()
                       or ".." in Path(f["path"]).parts
                       or not re.fullmatch(r"[0-9a-f]{64}", str(f.get("sha256", ""))) for f in files)
                or len({f["path"] for f in files}) != len(files)):
            errors.append(f"模板 {identifier} 的文件集合或 SHA-256 无效")
            continue
        if not isinstance(snapshots, list) or len(snapshots) != len(files or []):
            errors.append(f"模板 {identifier} 缺少真实文件快照；请重新运行 template_library.py select")
            continue
        for file_item, snap in zip(files, snapshots):
            if not isinstance(snap, dict) or not snap.get("path") or not re.fullmatch(r"[0-9a-f]{64}", str(snap.get("sha256", ""))):
                errors.append(f"模板 {identifier} 的快照记录无效")
                continue
            path = (Path(record_path).parent / str(snap["path"])).resolve()
            if not path.is_file() or not path.is_relative_to(Path(record_path).parent.resolve()):
                errors.append(f"模板 {identifier} 的真实文件快照不存在或越界：{snap.get('path')}")
                continue
            if digest(path) != snap["sha256"]:
                errors.append(f"模板 {identifier} 的真实文件快照 SHA-256 不符：{snap.get('path')}")
            if (snap["sha256"] != file_item.get("sha256")
                    or not path.as_posix().endswith('/' + str(file_item.get("path", "")).replace(chr(92), '/'))):
                errors.append(f"模板 {identifier} 的快照与所选文件不对应")
    return errors


def _target_keys(session, target):
    """Stable keys accepted for an ``applies_to`` value.

    A selection is made before a file exists, so the check uses the project
    deliver root (when linked) and the session root.  Absolute selections are
    also accepted, but a path outside either root never matches.
    """
    session = Path(session).resolve()
    target = Path(target).resolve()
    # A standalone selection is relative to the session root. Treating raw/
    # as a second implicit root would let raw/report.xlsx borrow report.xlsx's
    # final-deliverable selection (and vice versa).
    roots = [session]
    project_state = (session / "project.json").is_file()
    deliver = session
    if project_state:
        try:
            project = read(session / "project.json")
            deliver = Path(str(project.get("deliver_root") or session)).resolve()
            roots.insert(0, deliver)
        except (OSError, ValueError, TypeError):
            pass
    keys = set()
    for root in roots:
        try:
            relative = target.relative_to(root)
            # In a project state, docs/... always means the real deliver
            # tree. Other relative working paths belong to the state root.
            base = deliver if project_state and relative.parts and relative.parts[0].lower() == "docs" else session
            if (base / relative).resolve() == target:
                keys.add(relative.as_posix().lower())
            keys.add(target.as_posix().lower())
        except ValueError:
            continue
    return keys


def _applies_key(value):
    value = str(value or "").replace(chr(92), "/").strip().lower()
    while value.startswith("./"):
        value = value[2:]
    return value


def _migration_map(path, moves):
    path = Path(path).resolve()
    candidates = [(Path(item["source"]), Path(item["destination"])) for item in moves
                  if path == Path(item["source"]) or path.is_relative_to(Path(item["source"]))]
    if not candidates:
        return path
    source, destination = max(candidates, key=lambda pair: len(pair[0].parts))
    return (destination / path.relative_to(source)).resolve()


def _migration_moves(source, destination, deliver, moves):
    result, seen_source, seen_destination = [], set(), set()
    for pair in moves:
        if isinstance(pair, dict):
            old, new = pair.get("source"), pair.get("destination")
        else:
            old, new = pair
        if not old or not new or not Path(old).is_absolute() or not Path(new).is_absolute():
            raise ValueError("模板迁移必须提供准确的绝对路径")
        old, new = Path(old).resolve(), Path(new).resolve()
        if not any(old.is_relative_to(root) for root in (source, deliver)):
            raise ValueError("模板迁移来源越出原项目")
        if not any(new.is_relative_to(root) for root in (destination, deliver)):
            raise ValueError("模板迁移目标越出状态根或项目成果目录")
        if old in seen_source or new in seen_destination:
            raise ValueError("模板迁移路径重复或冲突")
        seen_source.add(old)
        seen_destination.add(new)
        result.append({"source": str(old), "destination": str(new)})
    return result


def _verify_migration_binding(value, binding):
    if value.get("schema_version") != 1 or value.get("kind") != "luz-design-byte-migration" or value.get("read_only") is not True:
        raise ValueError("模板同字节迁移凭据格式不符")
    source, destination, deliver = (Path(value[key]).resolve() for key in ("source_session", "destination_session", "deliver_root"))
    moves = _migration_moves(source, destination, deliver, value["moves"])
    record = _record_path(destination, binding["caller"], binding["stage"])
    old_record, old_target, target = (Path(binding[key]).resolve() for key in ("source_record", "source_target", "destination_target"))
    if (old_record != source / "00-design" / record.name
            or Path(binding["destination_record"]).resolve() != record
            or _migration_map(old_record, moves) != record
            or _migration_map(old_target, moves) != target or old_target == target
            or not _target_keys(destination, target)):
        raise ValueError("模板迁移凭据未绑定准确原记录与迁移路径")
    if not record.is_file() or digest(record) != binding["record_sha256"]:
        raise ValueError("模板迁移的原选择记录已变更或丢失")
    project = read(destination / "project.json")
    if Path(str(project.get("deliver_root") or destination)).resolve() != deliver:
        raise ValueError("模板迁移的项目成果根不符")
    selected = read(record)
    if selected.get("caller") != binding["caller"] or selected.get("stage") != binding["stage"]:
        raise ValueError("模板迁移 caller/stage 不符")
    errors = validate_references(selected.get("template_uses")) + _snapshot_errors(record, selected)
    if errors:
        raise ValueError("模板迁移的原模板或快照无效：" + "; ".join(errors))
    for item in selected["template_uses"]:
        output = item.get("output") or {}
        if (item.get("id") == binding["template_id"] and item.get("applies_to") == binding["applies_to"]
                and output.get("path") and Path(output["path"]).resolve() == old_target
                and output.get("sha256") == binding["output_sha256"]
                and output.get("generator") == binding["generator"] and str(binding["generator"]).strip()):
            if not target.is_file() or digest(target) != binding["output_sha256"]:
                raise ValueError("模板迁移产物缺失或与原产物字节不符")
            return item
    raise ValueError("模板迁移未找到原先登记的准确产物")


def prepare_output_migration(source_session, destination_session, moves):
    """Read-only pre-move verification; never reselect, rerender or rewrite evidence.

    Project passes its exact absolute move plan. Only produced outputs with a
    successful original post-check can acquire a byte-preserving read alias.
    """
    source, destination = Path(source_session).resolve(), Path(destination_session).resolve()
    project = read(source / "project.json")
    deliver = Path(str(project.get("deliver_root") or source)).resolve()
    normalized = _migration_moves(source, destination, deliver, moves)
    result = {"schema_version": 1, "kind": "luz-design-byte-migration", "read_only": True,
              "source_session": str(source), "destination_session": str(destination),
              "deliver_root": str(deliver), "moves": normalized, "bindings": []}
    for record in sorted((source / "00-design").glob("*.json")):
        selected = read(record)
        caller, stage = selected.get("caller"), selected.get("stage")
        if record.resolve() != _record_path(source, caller, stage):
            raise ValueError("模板迁移的选择记录位置不符")
        for item in selected.get("template_uses") or []:
            output = item.get("output") or {}
            if not output.get("path"):
                continue
            target = Path(output["path"]).resolve()
            moved = _migration_map(target, normalized)
            if moved == target:
                continue
            require_selected(source, caller, stage, target, item.get("id"), phase="post")
            destination_record = destination / "00-design" / record.name
            if _migration_map(record, normalized) != destination_record:
                raise ValueError("模板迁移未包含原选择记录及快照目录")
            result["bindings"].append({"caller": caller, "stage": stage, "template_id": item["id"],
                                       "applies_to": item["applies_to"], "source_record": str(record.resolve()),
                                       "destination_record": str(destination_record), "record_sha256": digest(record),
                                       "source_target": str(target), "destination_target": str(moved),
                                       "output_sha256": output["sha256"], "generator": output["generator"]})
    return result


def record_output_migration(prepared):
    """After actual moves, verify unchanged bytes and save a separate read-only receipt."""
    if not prepared.get("bindings"):
        return None
    for binding in prepared["bindings"]:
        _verify_migration_binding(prepared, binding)
    body = json.dumps(prepared, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    identifier = hashlib.sha256(body.encode("utf-8")).hexdigest()
    receipt = Path(prepared["destination_session"]).resolve() / "00-design" / "migrations" / f"{identifier}.json"
    if receipt.exists():
        if receipt.read_text(encoding="utf-8") != body:
            raise ValueError("已有模板迁移凭据内容不符")
        return receipt
    receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipt.with_suffix(".tmp")
    temporary.write_bytes(body.encode("utf-8"))
    temporary.replace(receipt)
    return receipt


def _migration_receipts(session):
    root = Path(session).resolve()
    for receipt in sorted((root / "00-design" / "migrations").glob("*.json")):
        if digest(receipt) != receipt.stem:
            raise ValueError("模板迁移凭据 SHA-256 不符")
        value = read(receipt)
        if Path(value["destination_session"]).resolve() != root:
            raise ValueError("模板迁移凭据属于其他状态根")
        yield value


def _migrated_selection(session, caller, stage, target):
    target = Path(target).resolve()
    for value in _migration_receipts(session):
        for binding in value.get("bindings") or []:
            if (binding.get("caller") == caller and binding.get("stage") == stage
                    and Path(binding["destination_target"]).resolve() == target):
                return _verify_migration_binding(value, binding)
    return None


def _relocated_output(session, caller, stage, target):
    """Find only a verified exact alias for the record-oriented check CLI."""
    target = Path(target).resolve()
    for value in _migration_receipts(session):
        for binding in value.get("bindings") or []:
            if (binding.get("caller") == caller and binding.get("stage") == stage
                    and Path(binding["source_target"]).resolve() == target):
                _verify_migration_binding(value, binding)
                return Path(binding["destination_target"]).resolve()
    return None


def _output_binding_matches(item, output):
    binding = item.get("output") if isinstance(item, dict) else None
    return (output.is_file() and isinstance(binding, dict) and binding.get("path")
            and Path(binding["path"]).resolve() == output
            and binding.get("sha256") == digest(output)
            and bool(str(binding.get("generator") or "").strip()))


def validate_selected_references(session, caller, stage, values):
    """Audit concluded references against current files or their original selection.

    A reference may describe an output that another writer will produce. This
    read-only check proves its saved template bytes, never its generation or
    approval. Writers and new conclusions must use ``validate_references``.
    """
    current_errors = validate_references(values)
    if not current_errors:
        return []
    try:
        path = _record_path(session, caller, stage)
        selected = read(path)
        if (not isinstance(values, list) or not values or not isinstance(selected, dict)
                or selected.get("caller") != caller or selected.get("stage") != stage
                or not isinstance(selected.get("template_uses"), list)):
            raise ValueError("历史模板引用缺少准确调用者、阶段与选择记录")
        seen = set()
        for reference_item in values:
            key = (reference_item["id"], _applies_key(reference_item["applies_to"]))
            if key[0] not in read(CATALOG)["templates"]:
                raise ValueError("历史模板引用的模板 ID 未登记")
            if key in seen:
                raise ValueError("重复模板引用")
            seen.add(key)
            if not validate_references([reference_item]):
                continue
            matches = [item for item in selected["template_uses"] if isinstance(item, dict)
                       and (item.get("id"), _applies_key(item.get("applies_to"))) == key]
            if len(matches) != 1 or matches[0].get("files") != reference_item.get("files"):
                raise ValueError("历史模板引用没有绑定原先选择的准确目标与文件 SHA-256")
            errors = _snapshot_errors(path, {"template_uses": matches})
            if errors:
                raise ValueError("; ".join(errors))
        return []
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [f"Luz-Design 历史模板引用无效：{exc}"]


def _require_approved_history(session, caller, stage, output, item):
    """Use Project's read-only ledger proof, never a caller-supplied bypass flag."""
    scripts = Path(__file__).resolve().parents[2] / "Luz-Project" / "scripts"
    file = scripts / "project_template_history.py"
    if str(scripts) not in sys.path:
        sys.path.append(str(scripts))
    spec = importlib.util.spec_from_file_location("_luz_project_template_history", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.require_approved_output(session, caller, stage, output, item)


def require_selected(session, caller, stage, target, expected_id=None, *, phase="pre"):
    """Require a real Design template selection bound to ``target``.

    ``phase=pre`` is used immediately before a writer runs and therefore does
    not require the target to exist.  ``phase=post`` requires the writer to
    record a hash for the produced file; this is how a selection becomes an
    auditable binding instead of a free-standing claim. After a template
    update, post may read unchanged approved Project output only when its
    original snapshots, writer receipt and effective approval still agree.
    """
    if caller not in CALLERS:
        raise ValueError("未知 caller")
    if not isinstance(stage, str) or not STAGE_RE.fullmatch(stage):
        raise ValueError("正式输出必须绑定具体 stage（小写字母、数字与短横线）")
    path = _record_path(session, caller, stage)
    if not path.is_file():
        raise ValueError(f"缺少 Luz-Design 模板选择记录：{path}；先运行 template_library.py select")
    value = read(path)
    if not isinstance(value, dict) or value.get("caller") != caller or value.get("stage") != stage:
        raise ValueError("模板选择记录的 caller/stage 不匹配")
    if phase not in {"pre", "post"}:
        raise ValueError("模板校验 phase 必须是 pre 或 post")
    if not isinstance(value.get("template_uses"), list) or not value["template_uses"]:
        raise ValueError("缺少实际选择的 Luz-Design template_uses")
    keys = _target_keys(session, target)
    matches = [item for item in value["template_uses"] if isinstance(item, dict) and _applies_key(item.get("applies_to")) in keys]
    if len(matches) > 1:
        raise ValueError("准确输出位置存在重复模板选择，无法确定原模板")
    output = Path(target).resolve()
    direct_post = matches and _output_binding_matches(matches[-1], output)
    migrated = _migrated_selection(session, caller, stage, target) if phase == "post" and not direct_post else None
    if not matches and migrated is not None:
        matches = [migrated]
    if not matches:
        raise ValueError(f"模板选择没有绑定准确输出位置：{Path(target).resolve()}；当前记录只有 "
                         + ", ".join(str(item.get("applies_to")) for item in value["template_uses"] if isinstance(item, dict)))
    item = matches[-1]
    binding = item.get("output")
    if phase == "pre" and isinstance(binding, dict) and binding.get("path") and Path(binding["path"]).resolve() != output:
        raise ValueError("模板原产物路径已迁移；新生成必须重新 select，迁移凭据只供读取原字节")
    if expected_id and item.get("id") != expected_id:
        raise ValueError(f"输出 {Path(target).resolve()} 必须使用 Luz-Design 模板 {expected_id}，实际为 {item.get('id')}")
    entry = read(CATALOG)["templates"].get(item.get("id"), {})
    if not entry:
        raise ValueError(f"未登记的 Luz-Design 模板：{item.get('id')}")
    if entry.get("kind") in {"reference-only", "source-catalog"}:
        raise ValueError(f"{item.get('id')} 只是参考/来源目录，不能作为正式产出的模板")
    snapshot_errors = _snapshot_errors(path, {"template_uses": [item]})
    if snapshot_errors:
        raise ValueError("Luz-Design 模板真实文件快照无效：" + "; ".join(snapshot_errors))
    if phase == "post":
        if not output.is_file():
            raise ValueError(f"模板产出不存在：{output}")
        if migrated is None and not _output_binding_matches(item, output):
            raise ValueError(f"模板产出未登记或哈希不符：{output}；必须调用 record_output")
    errors = validate_references([item])
    if errors:
        if phase == "pre" or migrated is not None:
            raise ValueError("Luz-Design 模板选择记录无效：" + "; ".join(errors))
        try:
            _require_approved_history(session, caller, stage, output, item)
        except (ImportError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError("Luz-Design 历史模板产物未通过有效批准核验：" + str(exc)) from exc
    return item


def record_output(session, caller, stage, target, expected_id=None, *, generator=""):
    """Bind the bytes produced by a selected template to its selection record."""
    target = Path(target).resolve()
    if not str(generator).strip() or generator == "unknown":
        raise ValueError("必须登记实际调用的模板生成器")
    item = require_selected(session, caller, stage, target, expected_id, phase="pre")
    path = _record_path(session, caller, stage)
    value = read(path)
    for current in value["template_uses"]:
        if current is item or _applies_key(current.get("applies_to")) == _applies_key(item.get("applies_to")):
            current["output"] = {"path": str(target), "sha256": digest(target), "generator": generator}
            break
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return require_selected(session, caller, stage, target, expected_id, phase="post")


def select(session, caller, stage, identifier, applies_to):
    if caller not in CALLERS:
        raise ValueError("未知 caller")
    if not isinstance(stage, str) or not STAGE_RE.fullmatch(stage):
        raise ValueError("阶段名称只能使用小写字母、数字与短横线")
    session = Path(session).resolve()
    text_target = str(applies_to).strip()
    if not text_target:
        raise ValueError("模板必须绑定具体的输出位置 applies_to")
    pure = text_target.replace(chr(92), "/")
    if any(part == ".." for part in Path(pure).parts):
        raise ValueError("模板输出位置不能越出会话或项目目录")
    if Path(text_target).is_absolute():
        candidate = Path(text_target).resolve()
        allowed = [session]
        try:
            project = read(session / "project.json")
            allowed.append(Path(str(project.get("deliver_root") or session)).resolve())
        except (OSError, ValueError, TypeError):
            pass
        if not any(candidate == root or candidate.is_relative_to(root) for root in allowed):
            raise ValueError("模板输出位置必须在当前会话或项目 deliver_root 内")
    # A project state root already is raw; a standalone session owns raw/.
    raw = session if (session / "project.json").is_file() else session / "raw"
    path = raw / "00-design" / f"{caller}{'-' + stage if stage else ''}.json"
    value = read(path) if path.is_file() else {"caller": caller, "stage": stage, "template_uses": []}
    if value.get("caller") != caller or value.get("stage") != stage:
        raise ValueError("模板记录调用者或阶段不符")
    item = reference(identifier, applies_to)
    # Keep a byte-for-byte copy inside the process record.  A catalog entry
    # can be changed later; a formal output must still be reviewable against
    # the exact template selected when it was generated.
    revision = hashlib.sha256(json.dumps(item["files"], sort_keys=True).encode("utf-8")).hexdigest()
    # Keep Windows paths short even for a long numbered session/test folder.
    snapshot_root = raw / "00-design" / "t" / revision[:16]
    snapshots = []
    for file_item in item["files"]:
        source = (ROOT / file_item["path"]).resolve()
        relative = Path(file_item["path"])
        snapshot = (snapshot_root / relative).resolve()
        if not snapshot.is_relative_to((raw / "00-design").resolve()):
            raise ValueError("模板真实文件快照越出当前记录目录")
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if snapshot.exists():
            if digest(snapshot) != file_item["sha256"]:
                raise ValueError("已有模板快照内容不符；保留原记录并检查损坏原因")
        else:
            shutil.copyfile(source, snapshot)
        snapshots.append({"path": str(snapshot.relative_to(raw / "00-design")).replace(chr(92), "/"), "sha256": digest(snapshot)})
    item["snapshots"] = snapshots
    # One output has one selection, however it was spelt: a relative and an absolute path of the same file replace each
    # other, otherwise the writer could not tell which of the two is the original (require_selected refuses two matches).
    same = {_applies_key(applies_to)}
    if Path(text_target).is_absolute():
        same |= _target_keys(session, text_target)
    else:
        project_state = (session / "project.json").is_file()
        base = session
        if project_state and Path(pure).parts and Path(pure).parts[0].lower() == "docs":
            try:
                base = Path(str(read(session / "project.json").get("deliver_root") or session)).resolve()
            except (OSError, ValueError, TypeError):
                base = session
        same |= _target_keys(session, base / pure)
    value["template_uses"] = [entry for entry in value["template_uses"]
                              if _applies_key(entry.get("applies_to")) not in same] + [item]
    # An update of one exact target must not rewrite or invalidate the saved
    # history of unrelated outputs. Every writer checks its own target again.
    errors = validate_references([item])
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return path


def render_reading(title, body, *, style=None):
    """Reuse the existing Design reading shell. body is already escaped trusted renderer output."""
    file = ROOT / "scripts" / "make_summary.py"
    spec = importlib.util.spec_from_file_location("_luz_design_reading_template", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    page = module.render({"title": title, "sections": []})
    marker = f"<h1>{module.esc(title)}</h1>"
    page = page.replace(marker, marker + body, 1)
    if style is not None:
        # Crawl retains its existing formal-report stylesheet; the document shell is Design's.
        start, end = page.index("<style>"), page.index("</style>")
        page = page[:start] + "<style>" + style + page[end:]
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--include-legacy", action="store_true", help="Include historical maintenance templates")
    describe = sub.add_parser("describe")
    describe.add_argument("template")
    describe.add_argument("--applies-to", required=True)
    choose = sub.add_parser("select")
    choose.add_argument("template")
    choose.add_argument("--session", type=Path, required=True)
    choose.add_argument("--caller", required=True)
    choose.add_argument("--stage")
    choose.add_argument("--applies-to", required=True)
    check = sub.add_parser("check")
    check.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = read(CATALOG)
            if not args.include_legacy:
                result['templates'] = {k:v for k,v in result['templates'].items() if v.get('status') != 'legacy'}
        elif args.command == "describe":
            result = reference(args.template, args.applies_to)
        elif args.command == "select":
            file = select(args.session, args.caller, args.stage, args.template, args.applies_to)
            result = {"record": str(file), **read(file)}
        else:
            value = read(args.file)
            errors = validate_references(value.get("template_uses") if isinstance(value, dict) else value)
            if isinstance(value, dict):
                errors += _snapshot_errors(args.file, value)
                for item in value.get("template_uses") or []:
                    output = item.get("output") if isinstance(item, dict) else None
                    if output:
                        target = Path(str(output.get("path", "")))
                        owner = args.file.resolve().parent.parent
                        if ((owner / "project.json").is_file()
                                and _record_path(owner, value.get("caller"), value.get("stage")) == args.file.resolve()):
                            target = _relocated_output(owner, value["caller"], value["stage"], target) or target
                        if not target.is_file() or digest(target) != output.get("sha256"):
                            errors.append(f"模板产出不存在或已变更：{target}")
            result = {"ok": not errors, "errors": errors}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return int(bool(errors))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
