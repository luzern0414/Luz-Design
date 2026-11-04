"""Client formal documents (make_docx.py): cover, clickable contents, Chinese heading numbers, header and footer, black and white, titled tables."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import check_document
import make_docx
import make_xlsx

TABLE = {"header": ["项", "内容"], "rows": [[f"项目{i}", f"内容{i}"] for i in range(1, 7)], "caption": "示例表"}


def spec(**extra) -> dict:
    return {"type": "proposal", "title": "示例建设方案", "style": "paper", "mono": True, "toc": True,
            "cover": {"subtitle": "建设方案", "info": [["项目名称", "示例"], ["版本", "V1.0"]]},
            "sections": [{"heading": "项目背景", "blocks": [{"p": "现状说明。"}, {"table": TABLE}]},
                         {"heading": "业务流程", "blocks": [{"sub": "总体流程"}, {"items": ["第一步", "第二步"]}, {"table": {**TABLE, "caption": "流程表"}}]}], **extra}


class FormalDocx(unittest.TestCase):
    def build(self, **extra):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        out = Path(self.tmp.name) / "a.docx"
        make_docx.build(spec(**extra), out)
        import docx
        return docx.Document(str(out)), out

    def test_three_sections_with_their_own_page_numbers(self):
        doc, _ = self.build()
        self.assertEqual(len(doc.sections), 3)
        from docx.oxml.ns import qn
        formats = [s._sectPr.find(qn("w:pgNumType")) for s in doc.sections]
        self.assertIsNone(formats[0], "the cover has no page number")
        self.assertEqual(formats[1].get(qn("w:fmt")), "lowerRoman")
        self.assertEqual(formats[2].get(qn("w:fmt")), "decimal")
        self.assertEqual(doc.sections[2].header.paragraphs[0].text, "示例建设方案")
        self.assertIn("PAGE", doc.sections[2].footer.paragraphs[0]._p.xml)

    def test_level_one_headings_number_in_chinese_and_the_contents_links_to_them(self):
        doc, _ = self.build()
        xml = doc.part.numbering_part.element.xml
        self.assertIn("chineseCountingThousand", xml)
        self.assertIn("（%2）", xml)
        body = doc.element.body.xml
        self.assertEqual(body.count("w:hyperlink w:anchor"), 3)           # 一、二、and （一）
        self.assertEqual(body.count("w:bookmarkStart"), 3)
        texts = [p.text for p in doc.paragraphs]
        self.assertIn("一、项目背景", "".join(texts), "the contents list writes the Chinese number")

    def test_tables_are_titled_above_and_black_and_white(self):
        doc, _ = self.build()
        body = doc.element.body
        captions = [p.text for p in doc.paragraphs if p.style.name == "Caption"]
        self.assertEqual(captions, ["表 1　示例表", "表 2　流程表"])
        self.assertNotIn("w:shd", body.xml.replace('w:shd w:val="clear" w:color="auto" w:fill="auto"', ""), "no table shading")
        self.assertNotIn("D9D9D9", body.xml)

    def test_a_table_over_a_page_break_continues_under_a_numbered_caption(self):
        table = {**TABLE, "breaks": [3]}
        out = Path(tempfile.mkdtemp()) / "b.docx"
        make_docx.build({**spec(), "sections": [{"heading": "项目背景", "blocks": [{"table": table}]}]}, out)
        import docx
        doc = docx.Document(str(out))
        self.assertEqual([p.text for p in doc.paragraphs if p.style.name == "Caption"], ["表 1　示例表", "续表 1"])
        self.assertEqual([len(t.rows) for t in doc.tables], [1 + 3, 1 + 3], "the header row is repeated in each piece")

    def test_a_continued_table_takes_no_number_so_the_next_titles_do_not_skip(self):
        # Audit 014 (A-03): 表1 2 3 4 续表4 续表4 表6 续表6 表8 - the pieces of a broken table used up numbers, so the SEQ
        # fields (which count 表 only) and the cached values written beside them disagreed.
        def titled(caption, **extra):
            return {"table": {**TABLE, "caption": caption, **extra}}
        blocks = [titled("甲"), titled("乙"), titled("丙", breaks=[2, 4]), titled("丁"), titled("戊", breaks=[3]), titled("己")]
        out = Path(tempfile.mkdtemp()) / "seq.docx"
        make_docx.build({**spec(), "sections": [{"heading": "项目背景", "blocks": blocks}]}, out)
        import re

        import docx
        import make_docx_paginated as paginated
        doc = docx.Document(str(out))
        self.assertEqual([p.text for p in doc.paragraphs if p.style.name == "Caption"],
                         ["表 1　甲", "表 2　乙", "表 3　丙", "续表 3", "续表 3", "表 4　丁", "表 5　戊", "续表 5", "表 6　己"])
        seq = re.findall(r"SEQ 表.*?</w:instrText>.*?<w:t[^>]*>(\d+)</w:t>", doc.element.body.xml, flags=re.S)
        self.assertEqual(seq, ["1", "2", "3", "4", "5", "6"], "one SEQ field per titled table; its cached value is the number Word computes")
        self.assertEqual(paginated.caption_errors(paginated.docx_captions(out)), [])

    def test_a_broken_table_without_a_title_does_not_take_a_number(self):
        untitled = {"header": ["项", "内容"], "rows": TABLE["rows"], "breaks": [3]}
        out = Path(tempfile.mkdtemp()) / "untitled.docx"
        make_docx.build({**spec(), "sections": [{"heading": "项目背景", "blocks": [{"table": untitled}, {"table": TABLE}]}]}, out)
        import docx
        doc = docx.Document(str(out))
        self.assertEqual([p.text for p in doc.paragraphs if p.style.name == "Caption"], ["表 1　示例表"])

    def test_a_heading_carries_no_parenthesised_explanation(self):
        bad = spec()
        bad["sections"][0]["heading"] = "项目背景（现状）"
        with self.assertRaises(ValueError):
            make_docx.build(bad, Path(tempfile.mkdtemp()) / "c.docx")

    def test_the_document_check_accepts_a_requested_cover_and_header(self):
        _, out = self.build()
        self.assertEqual(check_document.main(["--allow", "paper", "--allow", "cover", "--allow", "header", str(out)]), 0)


class PdfLabels(unittest.TestCase):
    def test_the_exported_pdf_gets_a_title_a_language_and_keeps_its_bookmarks(self):
        import fitz
        import make_docx_paginated
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "a.pdf"
            doc = fitz.open()
            doc.new_page().insert_text((72, 72), "x")
            doc.set_toc([[1, "一、项目背景", 1]])
            doc.save(str(pdf))
            doc.close()
            make_docx_paginated.label_pdf(pdf, "示例建设方案")
            labelled = fitz.open(str(pdf))
            self.assertEqual(labelled.metadata["title"], "示例建设方案")
            self.assertEqual(labelled.get_toc(), [[1, "一、项目背景", 1]])
            catalog = labelled.xref_object(labelled.pdf_catalog())
            self.assertIn("/Lang(zh-CN)", catalog.replace(" ", ""))
            self.assertIn("DisplayDocTitle true", catalog)
            labelled.close()


class CaptionNumbers(unittest.TestCase):
    """make_docx_paginated checks the table numbers of what it exported: consecutive, and the PDF shows the cached values."""

    def test_gaps_and_misnumbered_continuations_are_reported(self):
        import make_docx_paginated as paginated
        good = [("表", 1), ("表", 2), ("续表", 2), ("续表", 2), ("表", 3)]
        self.assertEqual(paginated.caption_errors(good), [])
        skipped = [("表", 1), ("表", 2), ("续表", 2), ("续表", 2), ("表", 4)]
        self.assertTrue(any("表 4" in e for e in paginated.caption_errors(skipped)))
        self.assertTrue(any("续表 3" in e for e in paginated.caption_errors([("表", 1), ("续表", 3)])))

    def pdf(self, lines: list[str]) -> Path:
        import fitz
        path = Path(tempfile.mkdtemp()) / "c.pdf"
        doc = fitz.open()
        page = doc.new_page()
        for i, text in enumerate(lines):
            page.insert_text((72, 72 + 24 * i), text, fontname="china-s", fontsize=11)
        doc.save(str(path))
        doc.close()
        return path

    def test_the_pdf_must_show_the_numbers_the_document_holds(self):
        import make_docx_paginated as paginated
        out = Path(tempfile.mkdtemp()) / "v.docx"
        blocks = [{"table": {**TABLE, "caption": "甲", "breaks": [3]}}, {"table": {**TABLE, "caption": "乙"}}]
        make_docx.build({**spec(), "sections": [{"heading": "项目背景", "blocks": blocks}]}, out)
        shown = self.pdf(["表1　甲", "续表1", "表2　乙", "表 3 显示了合计，不是表题"])
        self.assertEqual(paginated.pdf_captions(shown), [("表", 1), ("续表", 1), ("表", 2)], "a sentence that starts with 表 is no title")
        self.assertEqual(paginated.verify_captions(out, shown), [])
        drifted = self.pdf(["表1　甲", "续表1", "表3　乙"])           # the exporter showed the numbers of an older layout
        self.assertEqual(len(paginated.verify_captions(out, drifted)), 1)
        split = self.pdf(["表1", "甲", "续表1", "表2", "乙"])                         # the exporter put each title on a line of its own
        self.assertEqual(paginated.verify_captions(out, split), [])
        trap = self.pdf(["表1　甲", "续表1", "表3　乙", "表 2 显示了合计"])      # 表 2 inside a sentence is not the title of 乙
        self.assertEqual(len(paginated.verify_captions(out, trap)), 1)

    @unittest.skipUnless(sys.platform == "win32" and shutil.which("powershell"), "the Word-compatible application is driven through PowerShell")
    def test_the_exported_pdf_of_a_document_with_continued_tables_shows_consecutive_numbers(self):
        try:
            import winreg
            winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "KWPS.Application"))
        except OSError:
            self.skipTest("WPS Writer is not installed")
        import make_docx_paginated as paginated
        rows = lambda n: [[f"项目{i}", f"内容{i}"] for i in range(n)]
        table = lambda caption, n: {"table": {"header": ["项", "内容"], "rows": rows(n), "caption": caption}}
        blocks = [table("甲", 5), table("乙", 45), table("丙", 5), table("丁", 50), table("戊", 5)]
        out = Path(tempfile.mkdtemp()) / "e2e.docx"
        paginated.build({**spec(), "sections": [{"heading": "项目背景", "blocks": blocks}]}, out)       # raises when the numbers drift
        captions = paginated.docx_captions(out)
        self.assertEqual([n for kind, n in captions if kind == "表"], [1, 2, 3, 4, 5])
        self.assertTrue(any(kind == "续表" for kind, _ in captions), "the sample must run over a page break")
        self.assertEqual(paginated.pdf_captions(out.with_suffix(".pdf")), captions)


class QuoteSheetFooter(unittest.TestCase):
    def test_summary_rows_under_the_table_pass_the_checks(self):
        rows = [["端A", "角色甲", f"功能{i}", 1.0, 500.0] for i in range(8)]
        sheet = {"title": "报价", "theme": "japanese-sushi", "sheet": "报价清单",
                 "columns": [{"name": "使用端", "merge": True}, {"name": "使用角色", "merge": True}, {"name": "功能"}, {"name": "工时（人天）", "type": "decimal"}, {"name": "报价（元）", "type": "money"}],
                 "rows": rows, "footer": [{"label": "基础功能小计", "values": {"工时（人天）": 8, "报价（元）": 4000}}, {"label": "报价合计", "values": {"报价（元）": 4000}}]}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "q.xlsx"
            make_xlsx.build(sheet, out)
            self.assertEqual(check_document.main([str(out)]), 0)
            from openpyxl import load_workbook
            ws = load_workbook(out).active
            self.assertEqual([c.value for c in ws[ws.max_row]][-1], 4000)
            self.assertEqual(ws.cell(ws.max_row - 1, 1).value, "基础功能小计")

    def test_tag_values_read_bold_and_the_colour_is_the_row_fill(self):
        sheet = {"title": "清单", "highlight": {"column": "类型", "values": ["可选"]}, "columns": [{"name": "功能"}, {"name": "类型", "tags": ["基础", "可选"]}], "rows": [["甲", "基础"], ["乙", "可选"]]}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.xlsx"
            make_xlsx.build(sheet, out)
            from openpyxl import load_workbook
            ws = load_workbook(out).active
            self.assertEqual(ws["B4"].font.color.rgb, "00000000")           # text is black; the colour is the fill
            self.assertEqual(ws["B5"].font.color.rgb, "00000000")
            self.assertTrue(ws["B5"].font.b)
            self.assertEqual(ws["B5"].fill.fgColor.rgb, "00FFE699")         # the highlighted row
            self.assertNotEqual(ws["B4"].fill.fgColor.rgb, "00FFE699")
            self.assertEqual(ws["A3"].fill.fgColor.rgb, "00ECF0F6")          # header
            self.assertEqual(check_document.main([str(out)]), 0)

    def test_a_footer_label_must_say_what_it_totals(self):
        with self.assertRaises(ValueError):
            make_xlsx.build({"title": "x", "theme": "coffee", "columns": [{"name": "甲"}, {"name": "数", "type": "number"}], "rows": [["a", 1]],
                             "footer": [{"label": "说明", "values": {"数": 1}}]}, Path(tempfile.mkdtemp()) / "x.xlsx")


if __name__ == "__main__":
    unittest.main()
