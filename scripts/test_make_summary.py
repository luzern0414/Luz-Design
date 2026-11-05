"""make_summary.py: the summary page is a fixed reading page that passes the layout check and the page checks."""
import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

import check_document
import check_output_layout
import make_summary
import sync_md_type
from validate_session import validate_light_html

ROOT = Path(__file__).resolve().parents[1]
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


def quiet(function, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args)


class RenderTest(unittest.TestCase):
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
        self.assertIn('<link rel="icon" href="data:image/svg+xml,', page)
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
        session = base / name
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
            session.mkdir()
            (session / "门店销售表.xlsx").write_bytes(b"x")
            self.assertEqual(quiet(make_summary.main, [str(spec), str(session), "--check"]), 0)
            self.assertEqual(quiet(make_summary.main, [str(spec), str(session), "--check", "--project-linked"]), 1)


if __name__ == "__main__":
    unittest.main()
