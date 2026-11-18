"""Actual Design output bindings survive delivery and reject stale sources."""
from __future__ import annotations

import pytest

import deliver
import make_xlsx
import new_session
import publish
import template_library
from test_crawl_gate import ready_session
from test_session_flow import adopt_rules


@pytest.fixture(autouse=True)
def restore_experience_store():
    import validate_session
    original = validate_session.NOTES_FILE
    yield
    validate_session.NOTES_FILE = original


SPEC = {"title": "OFFLINE_DELIVERY_FIXTURE", "theme": "coffee", "columns": [{"name": "Item"}],
        "rows": [["Synthetic test row"]]}


def prepared(tmp_path, *, final=True):
    session = ready_session(tmp_path)
    source = session / "raw" / "result.xlsx"
    target = session / "result.xlsx"
    template_library.select(session, "luz-design", "design", "xlsx", source.relative_to(session).as_posix())
    make_xlsx.build(SPEC, source, session=session)
    if final:
        template_library.select(session, "luz-design", "design", "xlsx", target.name)
    return session, source, target


def test_delivery_requires_the_exact_final_selection_before_copy(tmp_path):
    session, source, target = prepared(tmp_path, final=False)
    with pytest.raises(ValueError, match="准确输出位置"):
        deliver.deliver(session, source)
    assert not target.exists()


def test_delivery_requires_a_matching_template_for_source_and_final(tmp_path):
    session, source, target = prepared(tmp_path)
    template_library.select(session, "luz-design", "design", "docx", target.name)
    with pytest.raises(ValueError, match="必须使用.*xlsx"):
        deliver.deliver(session, source)
    assert not target.exists()


def test_delivery_cannot_copy_a_source_without_a_generation_receipt(tmp_path):
    session, source, target = prepared(tmp_path)
    template_library.select(session, "luz-design", "design", "xlsx", source.relative_to(session).as_posix())
    with pytest.raises(ValueError, match="未登记或哈希不符"):
        deliver.deliver(session, source)
    assert not target.exists()


def test_stale_source_does_not_replace_an_existing_deliverable(tmp_path):
    session, source, target = prepared(tmp_path)
    deliver.deliver(session, source)
    original = target.read_bytes()
    source.write_bytes(source.read_bytes() + b"OFFLINE_TAMPER")
    with pytest.raises(ValueError, match="未登记或哈希不符"):
        deliver.deliver(session, source, replace=True)
    assert target.read_bytes() == original


def test_delivery_records_the_real_copied_bytes(tmp_path):
    session, source, target = prepared(tmp_path)
    assert deliver.deliver(session, source) == target
    assert target.read_bytes() == source.read_bytes()
    template_library.require_selected(session, "luz-design", "design", target, "xlsx", phase="post")


def test_page_publish_uses_the_actual_registered_session_shell(tmp_path):
    session = ready_session(tmp_path)
    adopt_rules(session)
    target = publish.publish(session, "document")
    selected = template_library.require_selected(session, "luz-design", "design", target,
                                                  "design-document-page", phase="post")
    paths = {item["path"] for item in selected["files"]}
    assert "references/templates.txt" in paths and "scripts/new_session.py" in paths
    assert 'data-luz-template="design-document-page"' in target.read_text(encoding="utf-8")


@pytest.mark.parametrize("mutation", ["marker", "layout"])
def test_page_cannot_claim_the_session_template_after_replacing_its_shell(tmp_path, mutation):
    session = ready_session(tmp_path)
    adopt_rules(session)
    source = session / "raw" / "03-documents" / "document.html"
    text = source.read_text(encoding="utf-8")
    if mutation == "marker":
        text = text.replace('data-luz-template="design-document-page"', '')
    else:
        text = text.replace("</style>", "main{max-width:1300px}</style>")
    source.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="真实 Luz-Design|布局样式"):
        publish.publish(session, "document")
    assert not (session / f"{session.name}.html").exists()


def test_session_template_allows_content_and_explicit_theme_tokens(tmp_path):
    session = ready_session(tmp_path)
    source = session / "raw" / "03-documents" / "document.html"
    source.write_text(source.read_text(encoding="utf-8").replace("#2B5F73", "#0958D9")
                      .replace("文件设计", "OFFLINE_CONTENT_FIXTURE"), encoding="utf-8")
    assert new_session.session_page_template_errors(source, "design-document-page") == []
