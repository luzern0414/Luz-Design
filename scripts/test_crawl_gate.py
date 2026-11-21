"""Output entry points validate evidence before writing, with offline test fixtures."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

import crawl_gate
import new_session
import style_match
import validate_session

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "Luz-Crawl" / "scripts"))
from test_crawl_preflight import complete_fixture
from test_summary_entry_gates import design_manifest


def session_at(base, *, project=None):
    return new_session.create_session(base / "sessions", "门禁夹具", ["document"],
                                      cards=["interface-visual"], project=project)


def ready_session(base):
    folder = session_at(base)
    complete_fixture(folder, "luz-design", "design")
    return folder


def test_missing_evidence_stops_before_output_directory_creation(tmp_path):
    folder = session_at(tmp_path)
    output = folder / "raw" / "not-created" / "page.html"
    with pytest.raises(ValueError, match="缺少记录"):
        crawl_gate.require_session_preflight(folder, output)
    assert not output.parent.exists()


def test_invalid_nested_manifest_cannot_borrow_an_outer_sessions_evidence(tmp_path):
    outer = ready_session(tmp_path)
    invalid = outer / "raw" / "fake-session"
    manifest = invalid / "raw" / "99-delivery" / "MANIFEST.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="无效 Design 会话"):
        crawl_gate.require_session_preflight(invalid, invalid / "raw" / "page.html")


def test_no_context_does_not_use_an_arbitrary_current_directory(monkeypatch):
    monkeypatch.delenv("LUZ_DESIGN_SESSION", raising=False)
    with pytest.raises(ValueError, match="正式输出需要"):
        crawl_gate.require_session_preflight()


def test_default_business_stage_cannot_borrow_generic_evidence(tmp_path, monkeypatch):
    monkeypatch.delenv("LUZ_CRAWL_STAGE", raising=False)
    folder = session_at(tmp_path)
    complete_fixture(folder, "luz-design")
    with pytest.raises(ValueError, match="luz-design/design"):
        crawl_gate.require_session_preflight(folder)
    complete_fixture(folder, "luz-design", "design")
    assert crawl_gate.require_session_preflight(folder)["stage"] == "design"


def test_standalone_explicit_stage_and_environment_keep_separate_records(tmp_path, monkeypatch):
    folder = session_at(tmp_path)
    complete_fixture(folder, "luz-design", "prototype")
    monkeypatch.setenv("LUZ_CRAWL_STAGE", "prototype")
    assert crawl_gate.require_session_preflight(folder)["stage"] == "prototype"
    with pytest.raises(ValueError, match="luz-design/design"):
        crawl_gate.require_session_preflight(folder, stage="design")


def test_gate_resolves_environment_and_output_ancestor_to_the_same_session(tmp_path, monkeypatch):
    folder = ready_session(tmp_path)
    output = folder / "raw" / "preview" / "page.html"
    monkeypatch.delenv("LUZ_DESIGN_SESSION", raising=False)
    found = crawl_gate.require_session_preflight(output=output)
    assert found["session"] == folder
    assert found["raw"] == folder / "raw"
    assert found["record"] == folder / "raw" / "00-crawl" / "luz-design-design.json"
    assert found["project"] is None and found["stage"] == "design"
    monkeypatch.setenv("LUZ_DESIGN_SESSION", str(folder))
    assert crawl_gate.require_session_preflight()["record"] == found["record"]


def test_output_cannot_escape_its_session(tmp_path):
    folder = ready_session(tmp_path)
    with pytest.raises(ValueError, match="输出超出"):
        crawl_gate.require_session_preflight(folder, folder.parent / "escaped.html")
    assert crawl_gate.require_session_preflight(folder, folder / f"{folder.name}.html")["session"] == folder


def test_linked_project_uses_state_root_and_design_stage(tmp_path):
    state = tmp_path / "project-state"
    state.mkdir()
    project = tmp_path / "019-结果项目"
    (state / "project.json").write_text(json.dumps({"deliver_root": str(project), "crawl": {"evidence_index": "evidence"}}), encoding="utf-8")
    folder = session_at(tmp_path, project=state)
    complete_fixture(state, "luz-design", "design")
    output = project / "docs" / "02-产品开发" / "02-前端界面设计.html"
    found = crawl_gate.require_session_preflight(folder, output)
    assert found["project"] == project
    assert found["evidence_root"] == state
    assert found["stage"] == "design"
    assert found["record"] == state / "evidence" / "luz-design-design.json"
    assert found["template_root"] == state
    assert crawl_gate.require_session_preflight(folder, folder / "raw" / "preview.docx")["template_root"] == folder
    assert crawl_gate.require_session_preflight(folder, folder / f"{folder.name}.html")["template_root"] == folder
    assert crawl_gate.crawl_errors(folder, caller="luz-design") == []
    with pytest.raises(ValueError, match="输出超出"):
        crawl_gate.require_session_preflight(folder, project / "spec.json")


def test_project_cannot_borrow_a_standalone_record(tmp_path):
    state = tmp_path / "state"
    state.mkdir()
    (state / "project.json").write_text("{}", encoding="utf-8")
    folder = session_at(tmp_path, project=state)
    complete_fixture(folder, "luz-design", "design")
    with pytest.raises(ValueError, match="luz-design/design"):
        crawl_gate.require_session_preflight(folder)


def linked_fixture(tmp_path, stage="design", owner="luz-design", current_stage="design"):
    state = tmp_path / "state"
    state.mkdir()
    deliver = tmp_path / "deliver"
    (state / "project.json").write_text(json.dumps({
        "deliver_root": str(deliver), "current_stage": current_stage,
        "stages": [{"id": stage, "owner": owner, "status": "approved"}],
        "crawl": {"evidence_index": "00-crawl"},
    }), encoding="utf-8")
    folder = tmp_path / "001-linked-design"
    design_manifest(folder, {"state_root": str(state), "deliver_root": str(deliver), "stage": stage})
    return folder, state


def test_linked_design_cannot_override_stage_to_borrow_other_evidence(tmp_path):
    folder, state = linked_fixture(tmp_path)
    complete_fixture(state, "luz-design", "architecture")
    with pytest.raises(ValueError, match="缺少记录"):
        crawl_gate.require_session_preflight(folder)
    with pytest.raises(ValueError, match="阶段不一致"):
        crawl_gate.require_session_preflight(folder, stage="architecture")
    assert any("阶段不一致" in error for error in crawl_gate.crawl_errors(folder, stage="architecture"))


def test_design_session_cannot_borrow_another_callers_record(tmp_path):
    folder, state = linked_fixture(tmp_path)
    complete_fixture(state, "luz-system", "design")
    with pytest.raises(ValueError, match="负责技能|caller"):
        crawl_gate.require_session_preflight(folder, caller="luz-system")
    assert any("负责技能" in error or "caller" in error
               for error in crawl_gate.crawl_errors(folder, caller="luz-system"))


def test_design_session_rejects_a_link_to_another_owners_stage(tmp_path):
    folder, state = linked_fixture(tmp_path, stage="architecture", owner="luz-system")
    complete_fixture(state, "luz-design", "architecture")
    with pytest.raises(ValueError, match="负责技能"):
        crawl_gate.require_session_preflight(folder, stage="architecture")


def test_approved_historical_design_keeps_its_linked_stage(tmp_path):
    folder, state = linked_fixture(tmp_path, current_stage="implementation")
    complete_fixture(state, "luz-design", "design")
    context = crawl_gate.require_session_preflight(folder, stage="design")
    assert context["stage"] == "design"
    assert context["caller"] == "luz-design"
    assert crawl_gate.crawl_errors(folder) == []


def test_drift_in_recorded_body_is_rejected(tmp_path):
    folder = ready_session(tmp_path)
    context = crawl_gate.require_session_preflight(folder)
    record = json.loads(context["record"].read_text(encoding="utf-8"))
    content = Path(record["sources"][0]["archive"]) / "content.json"
    changed = json.loads(content.read_text(encoding="utf-8"))
    changed["text"] = "Body modified after the research record was concluded"
    content.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="哈希|正文"):
        crawl_gate.require_session_preflight(folder)


@pytest.mark.parametrize("module_name,extension", [
    ("make_xlsx", ".xlsx"), ("make_docx", ".docx"),
    ("make_docx_paginated", ".docx"), ("make_table_pdf", ".pdf"),
    ("make_showcase", ".pdf"),
])
def test_document_cli_checks_before_any_file_or_renderer(tmp_path, module_name, extension):
    folder = session_at(tmp_path)
    spec = folder / "raw" / "input.json"
    spec.write_text("{}", encoding="utf-8")
    output = folder / "raw" / "new-build" / ("result" + extension)
    module = importlib.import_module(module_name)
    assert module.main([str(spec), str(output), "--session", str(folder)]) == 2
    assert not output.parent.exists()


def test_style_match_output_is_gated_but_check_is_read_only(tmp_path):
    folder = session_at(tmp_path)
    output = folder / "raw" / "candidate.json"
    args = ["--brief", "服务入口与商品列表", "--session", str(folder), "--output", str(output)]
    assert style_match.main(args) == 2
    assert not output.exists()
    assert style_match.main([*args, "--check-design"]) == 0
    assert not output.exists()


def test_document_ui_assets_and_pending_configuration_are_valid(tmp_path):
    folder = session_at(tmp_path)
    assets = folder / "raw" / "02-visual"
    assets.mkdir()
    (assets / "prompts").mkdir()
    (assets / "generated").mkdir()
    (assets / "style-match.json").write_text(json.dumps(style_match.build_match("服务入口")), encoding="utf-8")
    assert style_match.session_style_errors(folder, required=True) == []
    assert validate_session.validate(folder) == []
    manifest = json.loads((folder / "raw" / "99-delivery" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["session_kind"] == "general" and manifest["status"] == "draft"
    assert manifest["modes"] == ["document"]


def test_document_ui_assets_do_not_authorize_a_standalone_poster(tmp_path):
    folder = session_at(tmp_path)
    visual = folder / "raw" / "02-visual"
    visual.mkdir()
    (visual / "visual-board.html").write_text("<!doctype html><html><body><h1>海报</h1></body></html>", encoding="utf-8")
    assert any("standalone poster" in e for e in validate_session.validate(folder))


def test_deliver_stops_before_copying_without_research(tmp_path):
    import deliver
    folder = session_at(tmp_path)
    source = folder / "raw" / "result.pdf"
    source.write_bytes(b"test fixture")
    with pytest.raises(ValueError, match="缺少记录"):
        deliver.deliver(folder, source)
    assert not (folder / source.name).exists()


def test_joint_design_reads_same_stage_owner_with_its_own_template_identity(tmp_path):
    import crawl_preflight
    folder, state = linked_fixture(tmp_path, owner="luz-system")
    path = state / "project.json"
    project = json.loads(path.read_text(encoding="utf-8"))
    project.update(workflow="commercial-v1")
    project["stages"][0]["contributors"] = ["luz-design"]
    path.write_text(json.dumps(project), encoding="utf-8")
    crawl_preflight.run(state, "luz-system", "已确认合同", research="local", stage="design")
    target = Path(project["deliver_root"]) / "docs" / "03-开发资料" / "03-前端开发说明.html"
    context = crawl_gate.require_session_preflight(folder, output=target)
    assert context["caller"] == "luz-design" and context["evidence_caller"] == "luz-system"
    assert context["record"].name == "luz-system-design.json"
    with pytest.raises(ValueError, match="输出超出"):
        crawl_gate.require_session_preflight(folder, output=target.parents[1] / "01-原始资料" / target.name)
