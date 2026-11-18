"""make_summary.py: the summary page is a fixed reading page that passes the layout check and the page checks."""
import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

import check_document
import check_output_layout
import make_summary
import new_session
import sync_md_type
from validate_session import validate_light_html

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT.parent / "Luz-Crawl" / "scripts"))
from test_crawl_preflight import complete_fixture
from test_summary_entry_gates import design_manifest
import pytest
SPEC = {
    "title": "门店销售表",
    "sections": [
        {"title": "成果", "text": "本次交付一份表格。", "table": {
            "caption": "表 1 成果清单", "columns": ["名称", "用途", "金额"],
            "rows": [["门店销售表.xlsx", "给店长对账", "1,200.00"], ["门店销售表.pdf", "存档", "—"]],
            "align": ["left", "left", "right"]}},
        {"title": "依据", "table": {"caption": "表 2 依据", "columns": ["规则", "落实"], "rows": [["文件设计规范 › 表格文件", "无序号列"]]}},
        {"title": "过程文件", "table": {"caption": "表 3 过程文件", "columns": ["文件", "用途"], "rows": [["raw\\03-documents\\summary.json", "本页的描述文件"]]}},
    ],
}


@pytest.mark.parametrize("existing", [False, True])
def test_design_summary_stage_override_cannot_write_or_replace_output(tmp_path, existing):
    """The audit reproducer had only architecture evidence for a design link."""
    session, state, deliver = tmp_path / "001-design", tmp_path / "state", tmp_path / "deliver"
    state.mkdir()
    (state / "project.json").write_text(json.dumps({
        "deliver_root": str(deliver), "current_stage": "design",
        "stages": [{"id": "design", "owner": "luz-design"},
                   {"id": "architecture", "owner": "luz-system"}],
        "crawl": {"evidence_index": "00-crawl"},
    }), encoding="utf-8")
    design_manifest(session, {"state_root": str(state), "deliver_root": str(deliver), "stage": "design"})
    complete_fixture(state, "luz-design", "architecture")
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps(SPEC), encoding="utf-8")
    output = session / f"{session.name}.html"
    if existing:
        output.write_bytes(b"previous approved summary")
    before = {path: path.read_bytes() for path in session.rglob("*") if path.is_file()}
    assert make_summary.main([str(spec), str(session)]) != 0
    assert make_summary.main([str(spec), str(session), "--stage", "architecture"]) != 0
    assert {path: path.read_bytes() for path in session.rglob("*") if path.is_file()} == before


def quiet(function, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args)


class RenderTest(unittest.TestCase):
    def test_long_document_navigation_reaches_every_heading_and_escapes_titles(self):
        page = make_summary.render({'title': '审计', 'sections': [
            {'title': title, 'text': '已核对。'} for title in ['总结', '问题', '依据', '<原文>', '限制', '验证', '范围', '参考', '后续']]})
        self.assertIn('<nav aria-label="本页目录">', page)
        for index in range(1, 10):
            self.assertIn(f'href="#section-{index}"', page)
            self.assertIn(f'id="section-{index}" tabindex="-1"', page)
        self.assertIn('&lt;原文&gt;</a>', page)
        self.assertNotIn('<原文>', page)
        self.assertLess(page.index('</section>'), page.index('<nav'))
        self.assertEqual(check_document.document_navigation_errors(page), [])

    def test_navigation_cannot_hide_application_links_controls_or_missing_targets(self):
        sections = [{'title': f'章节 {index}', 'text': '已核对。'} for index in range(9)]
        page = make_summary.render({'title': '审计', 'sections': sections})
        for changed in [
            page.replace('href="#section-1"', 'href="https://example.org/settings"', 1),
            page.replace('href="#section-1"', 'href="#missing"', 1),
            page.replace('</nav>', '<button>保存</button></nav>', 1),
            page.replace('aria-label="本页目录"', '', 1),
            page.replace('id="section-2"', 'id="section-1"', 1),
        ]:
            with self.subTest(changed=changed[:40]):
                self.assertTrue(check_document.document_navigation_errors(changed))

    def test_a_nav_label_alone_does_not_allow_a_short_application_menu(self):
        page = '<h1>任务</h1><h2 id="settings">设置</h2><nav aria-label="本页目录"><a href="#settings">设置</a></nav>'
        self.assertTrue(check_document.document_navigation_errors(page))

    def test_reference_links_are_real_escaped_links(self):
        page = make_summary.render({'title': '依据', 'sections': [{'title': '来源', 'table': {
            'columns': ['原文'], 'rows': [[{'text': '<官方文档>', 'href': 'https://example.org/doc?a=1&b=2'}]],
            'caption': '表 1 原文'}}]})
        self.assertIn('href="https://example.org/doc?a=1&amp;b=2"', page)
        self.assertIn('&lt;官方文档&gt;</a>', page)
        self.assertNotIn('<官方文档>', page)

    def test_links_cannot_execute_code_or_escape_the_task_tree(self):
        for url in ['javascript:alert(1)', 'data:text/html,hello', '//evil.example/path', '../private.txt',
                    'https://user:secret@example.org', 'https://example.org/\ncontrol']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                make_summary.render({'title': '依据', 'sections': [{'title': '来源', 'text': {'text': 'open', 'href': url}}]})

    def test_narrative_sections_can_use_paragraphs_without_forced_tables(self):
        page = make_summary.render({'title': '决定', 'sections': [{'title': '采用理由', 'paragraphs': ['前提。', '取舍。']}]})
        self.assertIn('<p>前提。</p><p>取舍。</p>', page)
        self.assertNotIn('<table>', page)

    def test_first_line_is_the_one_title_and_each_section_has_one_titled_table(self):
        page = make_summary.render(SPEC)
        self.assertEqual(len(re.findall(r"<h1\b", page)), 1)
        self.assertLess(page.index("<h1>"), page.index("<h2>"))
        sections = re.findall(r"<section>.*?</section>", page, re.S)
        self.assertEqual(len(sections), 3)
        for section in sections:
            self.assertEqual(section.count("<table>"), 1)
            self.assertEqual(section.count("<caption>"), 1)
        self.assertNotRegex(page.split("<main>", 1)[1], r"<(h[3-6]|time|footer|header|nav)\b")

    def test_page_head_follows_the_reading_page_contract(self):
        page = make_summary.render(SPEC)
        self.assertIn('<html lang="zh-CN">', page)
        self.assertIn('<link rel="icon" href="data:image/webp;base64,', page)
        self.assertIn("<title>门店销售表</title>", page)
        self.assertNotRegex(page, r"(?i)user-scalable|maximum-scale")
        self.assertIn("color-scheme: light", page)
        families = [value.strip() for value in re.findall(r"font-family\s*:\s*([^;]+);", page) if value.strip() != "inherit"]
        self.assertEqual(len(families), 2, families)   # the page's one family, and the code face of the type block
        self.assertIn('"Microsoft YaHei"', families[0])
        self.assertEqual(sum(1 for family in families if "monospace" in family), 1)

    def test_type_block_is_the_shared_master(self):
        master, _ = sync_md_type.read(sync_md_type.MASTER)
        start, end = sync_md_type.blocks_of(master)[0]
        self.assertEqual(make_summary.MD_TYPE.strip(), master[start:end].strip())

    def test_alignment_follows_the_spec_and_text_is_escaped(self):
        spec = {"title": "甲 & 乙", "sections": [{"title": "成果", "table": {"columns": ["名称", "数量", "备注"], "rows": [["<b>x</b>", "3", "a & b"]], "align": ["left", "right", "center"]}}]}
        page = make_summary.render(spec)
        self.assertIn('<td class="left">&lt;b&gt;x&lt;/b&gt;</td>', page)
        self.assertIn('<td class="right">3</td>', page)
        self.assertIn('<td class="center">a &amp; b</td>', page)
        self.assertIn("<h1>甲 &amp; 乙</h1>", page)
        self.assertNotIn("<caption>", page)

    def test_bad_specs_are_refused(self):
        with self.assertRaises(ValueError):
            make_summary.render({"sections": []})
        with self.assertRaises(ValueError) as caught:
            make_summary.render({"title": "甲", "sections": [{"title": "成果", "table": {"columns": ["a", "b"], "rows": [["只有一列"]]}}]})
        self.assertIn("列数", str(caught.exception))

    def test_a_section_may_be_text_only(self):
        page = make_summary.render({"title": "甲", "sections": [{"title": "成果", "text": "一段话。"}]})
        self.assertIn("<p>一段话。</p>", page)
        self.assertNotIn("<table>", page)


class WrittenPageTest(unittest.TestCase):
    def make(self, base: Path, name="001-门店销售表") -> tuple[Path, Path]:
        session = new_session.create_session(base, name.split("-", 1)[1], ["document"], cards=["reading-html"])
        complete_fixture(session, "luz-design", "summary")
        spec = base / "spec.json"
        spec.write_text(json.dumps(SPEC, ensure_ascii=False), encoding="utf-8")
        return session, spec

    def test_command_writes_the_page_next_to_raw_and_the_layout_check_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            session, spec = self.make(Path(temp))
            self.assertEqual(quiet(make_summary.main, [str(spec), str(session), "--check"]), 0)
            self.assertEqual(sorted(item.name for item in session.iterdir()), ["001-门店销售表.html", "raw"])
            self.assertEqual(check_output_layout.check_session(session, False), ([], []))

    def test_the_page_passes_the_light_page_and_document_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            session, spec = self.make(Path(temp))
            quiet(make_summary.main, [str(spec), str(session)])
            page = session / "001-门店销售表.html"
            errors: list[str] = []
            validate_light_html(page, errors)
            check_document.check_html(page, errors, [])
            self.assertEqual(errors, [])

    def test_check_with_project_link_refuses_a_deliverable_left_in_the_root(self):
        with tempfile.TemporaryDirectory() as temp:
            session, spec = self.make(Path(temp))
            session.mkdir(exist_ok=True)
            (session / "门店销售表.xlsx").write_bytes(b"x")
            self.assertEqual(quiet(make_summary.main, [str(spec), str(session), "--check"]), 0)
            self.assertEqual(quiet(make_summary.main, [str(spec), str(session), "--check", "--project-linked"]), 1)


if __name__ == "__main__":
    unittest.main()
