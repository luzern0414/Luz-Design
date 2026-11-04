"""make_table_pdf.py builds a reading HTML that passes check_document and keeps the table centred as a whole."""
import sys
import copy
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_document  # noqa: E402
import make_table_pdf as M  # noqa: E402

SPEC = {
    "title": "企业 AI 定制服务",
    "theme": "ai-agent",
    "sections": [
        {"heading": "各行业都用得上的系统", "label": "系统", "head": "能帮你做的判断", "columns": 2,
         "rows": [{"label": "获客", "cells": [["去哪儿找新客户", "从招标公告和展会名单里自动筛"], "只有一句话"]}]},
        {"heading": "按行业定制", "label": "行业", "head": "能帮你做的判断", "columns": 2,
         "groups": [{"name": "零售与消费", "rows": [{"label": "商超与便利店", "cells": [["明天每样货订多少", "看天气和往常销量算出来"]]}]}]},
    ],
}


class MakeTablePdfTest(unittest.TestCase):
    def setUp(self):
        M.WORDS.clear()

    def build(self):
        return M.build_html(SPEC)

    def test_structure(self):
        page = self.build()
        self.assertLess(page.index("<h1>"), page.index("<section>"))
        self.assertEqual(page.count("<h1>"), 1)
        self.assertEqual(page.count("<h2>"), 2)
        self.assertIn('<th scope="colgroup" colspan="2">能帮你做的判断</th>', page)
        self.assertIn('<h3>零售与消费</h3>', page)
        self.assertIn('<span class="lead">去哪儿找新客户</span>', page)
        # a row with fewer cells than columns is padded so every row has the same width
        self.assertEqual(page.count('<td class="cell">'), 4)
        self.assertEqual(page.count('<td class="cell"></td>'), 1)

    def test_centred_layout_tokens(self):
        page = self.build()
        self.assertIn("vertical-align:middle;text-align:center", page)
        self.assertIn("margin:0 auto;text-align:left", page)
        self.assertIn("word-break:keep-all;text-wrap:balance", page)
        self.assertIn("white-space:normal;word-break:keep-all", page)

    def test_word_breaks_only_between_words(self):
        M.WORDS["看天气和往常销量算出来"] = ["看", "天气", "和", "往常", "销量", "算出来"]
        page = self.build()
        self.assertIn("看<wbr>天气<wbr>和<wbr>往常<wbr>销量<wbr>算出来", page)

    def test_passes_check_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "表格.html"
            src.write_text(self.build(), encoding="utf-8")
            self.assertEqual(check_document.main([str(src)]), 0)

    def test_cell_texts_cover_leads_and_details(self):
        texts = M.cell_texts(SPEC)
        self.assertIn("去哪儿找新客户", texts)
        self.assertIn("从招标公告和展会名单里自动筛", texts)
        self.assertIn("看天气和往常销量算出来", texts)

    def test_rejects_embedded_font_that_is_not_microsoft_yahei(self):
        import gc
        import fitz

        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "wrong-font.pdf"
            doc = fitz.open()
            page = doc.new_page(width=842, height=595)
            page.insert_font(fontname="other", fontbuffer=fitz.Font("helv").buffer)
            page.insert_text((40, 60), "This embedded font is not Microsoft YaHei.", fontname="other")
            doc.set_toc([[1, "Font check", 1]])
            doc.subset_fonts()
            doc.save(pdf)
            doc.close()
            errors = M.check_pdf(pdf, 1)
            gc.collect()
            self.assertTrue(any("MicrosoftYaHei" in error for error in errors), errors)

    def test_theme_is_chosen_for_each_document(self):
        spec = copy.deepcopy(SPEC)
        del spec["theme"]
        with self.assertRaisesRegex(ValueError, "theme"):
            M.build_html(spec)
        spec["theme"] = "coffee"
        self.assertNotEqual(M.build_html(spec), M.build_html(SPEC))

    def test_domain_glossary_overrides_browser_word_boundaries(self):
        text = "结合试销走势和用眼记录，核对药师资质"
        terms = ["试销", "走势", "用眼", "药师", "资质"]
        M.segment([text], protected_terms=terms)
        output = M.words(text)
        for term in terms:
            self.assertIn(term, output)
        self.assertEqual(output.replace("<wbr>", ""), text)

    def test_physical_fragments_keep_rows_corners_and_heading_alignment(self):
        import fitz
        spec = copy.deepcopy(SPEC)
        spec["sections"] = [spec["sections"][1]]
        spec["sections"][0]["groups"][0]["rows"] = [
            {"label": f"对象{i}", "cells": [[f"问题{i}", "这段说明足够长，用来核对实际行高和跨页后内容是否完整。"]]}
            for i in range(18)
        ]
        M.segment(M.cell_texts(spec))
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "fragments.html"
            pdf = Path(tmp) / "fragments.pdf"
            src.write_text(M.build_html(spec), encoding="utf-8")
            report = M.paginate_html(src)
            from validate_session import validate_light_html
            html_errors = []
            validate_light_html(src, html_errors)
            self.assertEqual(html_errors, [])
            self.assertGreater(report["pages"], 1)
            self.assertEqual(report["rows"], 18)
            self.assertFalse(report["errors"], report)
            self.assertTrue(all(f["radius"] == [12, 12, 12, 12] for f in report["fragments"]))
            self.assertLess(max(report["heading_offsets"]), 0.5)
            M.export_pdf(src, pdf, M.theme_tokens(spec["theme"])["ink2"])
            with fitz.open(pdf) as doc:
                self.assertEqual(len(doc), report["pages"])
                self.assertTrue(all(len(p.get_text()) > 30 for p in doc))
            content = src.read_text(encoding="utf-8")
            for i in range(18):
                self.assertEqual(content.count(f">对象{i}</td>"), 1)


class SectionOptionsTest(unittest.TestCase):
    """heads / widths / fill are optional: a spec without them renders exactly as before."""

    def setUp(self):
        M.WORDS.clear()

    def spec(self, **extra):
        sec = {"heading": "功能", "label": "功能", "head": "说明", "columns": 2,
               "rows": [{"label": "报餐", "cells": ["员工在截止前选择一个套餐提交，截止后不能再改", "含"]}]}
        sec.update(extra)
        return {"title": "功能清单", "theme": "ai-agent", "sections": [sec]}

    def test_default_keeps_spanning_head(self):
        page = M.build_html(self.spec())
        self.assertIn('colspan="2"', page)
        self.assertNotIn("width:85", page)

    def test_heads_widths_fill(self):
        page = M.build_html(self.spec(heads=["业务规则", "类型"], widths=[3, 1], fill=True))
        self.assertNotIn("colspan", page)
        self.assertIn('<th scope="col">业务规则</th><th scope="col">类型</th>', page)
        self.assertIn("width:63.75%", page)
        self.assertIn('<table class="fill">', page)  # on the table: pagination rebuilds the frame but clones the table
        self.assertIn('class="cell short"', page)

    def test_wrong_head_count_is_rejected(self):
        with self.assertRaises(ValueError):
            M.build_html(self.spec(heads=["只有一个"]))

    def test_passes_check_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "清单.html"
            src.write_text(M.build_html(self.spec(heads=["业务规则", "类型"], widths=[3, 1], fill=True)), encoding="utf-8")
            self.assertEqual(check_document.main([str(src)]), 0)


if __name__ == "__main__":
    unittest.main()
