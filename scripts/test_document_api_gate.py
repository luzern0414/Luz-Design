"""Direct Python writers obey the same evidence and template gates as CLIs."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Luz-Crawl" / "scripts"))
from test_crawl_preflight import complete_fixture
from test_summary_entry_gates import design_manifest


SPEC = {"title": "OFFLINE_API_FIXTURE", "theme": "coffee",
        "columns": [{"name": "Item"}], "rows": [["TEST_FIXTURE"]],
        "sections": [{"heading": "Test", "blocks": [{"p": "OFFLINE_FIXTURE"}]}]}


@pytest.mark.parametrize("module_name,extension", [
    ("make_xlsx", ".xlsx"), ("make_docx", ".docx"), ("make_docx_paginated", ".docx"),
])
def test_direct_api_cannot_write_without_evidence(tmp_path, monkeypatch, module_name, extension):
    module = importlib.import_module(module_name)
    monkeypatch.delenv("LUZ_DESIGN_SESSION", raising=False)
    monkeypatch.setattr(module, "layout", lambda *a, **k: pytest.fail("Office layout entered before gate"), raising=False)
    target = tmp_path / "never-created" / f"result{extension}"
    with pytest.raises(ValueError, match="Design|Crawl"):
        module.build(SPEC, target)
    assert not target.parent.exists()


def ready(tmp_path, template="xlsx"):
    import template_library
    root = tmp_path / "001-offline-api"
    design_manifest(root)
    complete_fixture(root, "luz-design", "document")
    target = root / "raw" / "result" / ("fixture.docx" if template.startswith("docx") else "fixture.xlsx")
    template_library.select(root, "luz-design", "document", template, target.relative_to(root).as_posix())
    return root, target


@pytest.mark.parametrize("module_name,template", [("make_xlsx", "xlsx"), ("make_docx", "docx")])
def test_direct_api_with_verified_design_context_records_bytes(tmp_path, module_name, template):
    import design_output_gate
    import template_library
    root, target = ready(tmp_path, template)
    context = design_output_gate.verified_output_context(root, "luz-design", "document", target, template)
    assert importlib.import_module(module_name).build(SPEC, target, context=context) == target
    assert target.is_file()
    template_library.require_selected(root, "luz-design", "document", target, template, phase="post")


def test_a_passed_dictionary_cannot_authorize_a_write(tmp_path):
    import make_xlsx
    target = tmp_path / "never-created" / "bad.xlsx"
    with pytest.raises(ValueError, match="context|上下文"):
        make_xlsx.build(SPEC, target, context={"passed": True})
    assert not target.parent.exists()


def test_default_api_context_uses_its_own_design_gate_even_with_module_collision(tmp_path, monkeypatch):
    import make_xlsx
    import template_library
    root, target = ready(tmp_path)
    monkeypatch.setitem(sys.modules, "crawl_gate", object())
    assert make_xlsx.build(SPEC, target, session=root, stage="document") == target
    template_library.require_selected(root, "luz-design", "document", target, "xlsx", phase="post")


def test_evidence_alone_cannot_authorize_a_template(tmp_path):
    import design_output_gate
    root = tmp_path / "001-evidence-only"
    complete_fixture(root, "luz-dev", "implementation")
    target = root / "result.pdf"
    with pytest.raises(ValueError, match="模板选择"):
        design_output_gate.verified_output_context(root, "luz-dev", "implementation", target, "docx-paginated")
    assert not target.exists()


def test_context_cannot_be_reused_for_another_output(tmp_path):
    import design_output_gate
    import make_xlsx
    root, target = ready(tmp_path)
    context = design_output_gate.verified_output_context(root, "luz-design", "document", target, "xlsx")
    other = target.with_name("other.xlsx")
    with pytest.raises(ValueError, match="输出|output"):
        make_xlsx.build(SPEC, other, context=context)
    assert not other.exists()


def test_existing_context_rechecks_body_drift(tmp_path):
    import design_output_gate
    import make_xlsx
    root, target = ready(tmp_path)
    context = design_output_gate.verified_output_context(root, "luz-design", "document", target, "xlsx")
    record = json.loads((root / "raw" / "00-crawl" / "luz-design-document.json").read_text(encoding="utf-8"))
    content = Path(record["sources"][0]["archive"]) / "content.json"
    content.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Crawl|哈希|正文"):
        make_xlsx.build(SPEC, target, context=context)
    assert not target.exists()


def test_upstream_context_binds_selected_final_pdf_and_raw_working_docx(tmp_path, monkeypatch):
    import design_output_gate
    import make_docx_paginated
    import template_library
    root = tmp_path / "001-upstream"
    complete_fixture(root, "luz-dev", "implementation")
    final = root / "report.pdf"
    working = root / "raw" / "formal-docs" / "report.docx"
    template_library.select(root, "luz-dev", "implementation", "docx-paginated", final.name)
    context = design_output_gate.verified_output_context(root, "luz-dev", "implementation", final,
                                                         "docx-paginated", working_output=working)
    def render(spec, out, max_passes=5):
        out.parent.mkdir(parents=True)
        out.write_bytes(b"OFFLINE_WORKING_DOCX")
        out.with_suffix(".pdf").write_bytes(b"OFFLINE_WORKING_PDF")
        return {"pages": 1}
    monkeypatch.setattr(make_docx_paginated, "_render_paginated", render)
    assert make_docx_paginated.build(SPEC, working, context=context) == {"pages": 1}
    assert working.is_file() and not final.exists()
    with pytest.raises(ValueError, match="raw|过程"):
        design_output_gate.verified_output_context(root, "luz-dev", "implementation", final,
                                                    "docx-paginated", working_output=root.parent / "escaped.docx")


def _offline_paginated(spec, out, max_passes=5):
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b"OFFLINE_WORKING_DOCX")
    out.with_suffix(".pdf").write_bytes(b"OFFLINE_WORKING_PDF")
    return {"pages": 1}


def test_direct_paginated_api_requires_pdf_selection_before_entering_office(tmp_path, monkeypatch):
    import design_output_gate
    import make_docx_paginated
    root, target = ready(tmp_path, "docx-paginated")
    context = design_output_gate.verified_output_context(root, "luz-design", "document", target, "docx-paginated")
    monkeypatch.setattr(make_docx_paginated, "_render_paginated", lambda *a: pytest.fail("Office entered before PDF gate"))
    with pytest.raises(ValueError, match="准确输出位置"):
        make_docx_paginated.build(SPEC, target, context=context)
    assert not target.exists() and not target.with_suffix(".pdf").exists()


def test_direct_paginated_api_records_both_exact_outputs(tmp_path, monkeypatch):
    import make_docx_paginated
    import template_library
    root, target = ready(tmp_path, "docx-paginated")
    pdf = target.with_suffix(".pdf")
    template_library.select(root, "luz-design", "document", "docx-paginated", pdf.relative_to(root).as_posix())
    monkeypatch.setattr(make_docx_paginated, "_render_paginated", _offline_paginated)
    assert make_docx_paginated.build(SPEC, target, session=root, stage="document") == {"pages": 1}
    for output in (target, pdf):
        template_library.require_selected(root, "luz-design", "document", output, "docx-paginated", phase="post")


def test_paginated_cli_reports_missing_pdf_selection_before_any_office_call(tmp_path, monkeypatch, capsys):
    import make_docx_paginated
    root, target = ready(tmp_path, "docx-paginated")
    monkeypatch.setenv("LUZ_CRAWL_STAGE", "document")
    source = root / "raw" / "spec.json"
    source.write_text(json.dumps(SPEC), encoding="utf-8")
    monkeypatch.setattr(make_docx_paginated, "_render_paginated", lambda *a: pytest.fail("Office entered before PDF gate"))
    assert make_docx_paginated.main([str(source), str(target), "--session", str(root)]) == 2
    assert "准确输出位置" in capsys.readouterr().err
    assert not target.exists() and not target.with_suffix(".pdf").exists()


def test_upstream_pdf_target_generated_beside_working_docx_records_final_bytes(tmp_path, monkeypatch):
    import design_output_gate
    import make_docx_paginated
    import template_library
    root = tmp_path / "001-upstream-sidecar"
    complete_fixture(root, "luz-dev", "implementation")
    working = root / "raw" / "formal-docs" / "report.docx"
    pdf = working.with_suffix(".pdf")
    template_library.select(root, "luz-dev", "implementation", "docx-paginated", pdf.relative_to(root).as_posix())
    context = design_output_gate.verified_output_context(root, "luz-dev", "implementation", pdf,
                                                         "docx-paginated", working_output=working)
    monkeypatch.setattr(make_docx_paginated, "_render_paginated", _offline_paginated)
    make_docx_paginated.build(SPEC, working, context=context)
    template_library.require_selected(root, "luz-dev", "implementation", pdf, "docx-paginated", phase="post")


def test_linked_design_raw_output_uses_project_evidence_and_its_own_template_record(tmp_path):
    import design_output_gate
    import make_xlsx
    import template_library
    state = tmp_path / "project-state"
    state.mkdir()
    project = tmp_path / "019-project"
    (state / "project.json").write_text(json.dumps({"deliver_root": str(project),
        "stages": [{"id": "design", "owner": "luz-design", "status": "pending"}]}), encoding="utf-8")
    root = tmp_path / "001-linked-design"
    design_manifest(root, project={"state_root": str(state), "deliver_root": str(project), "stage": "design"})
    complete_fixture(state, "luz-design", "design")
    target = root / "raw" / "result.xlsx"
    template_library.select(root, "luz-design", "design", "xlsx", target.relative_to(root).as_posix())
    context = design_output_gate.verified_output_context(state, "luz-design", "design", target,
                                                         "xlsx", template_root=root)
    make_xlsx.build(SPEC, target, context=context)
    template_library.require_selected(root, "luz-design", "design", target, "xlsx", phase="post")
