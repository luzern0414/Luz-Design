"""make_table_pdf.py builds a reading HTML that passes check_document and keeps the table centred as a whole."""
import sys
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
        self.assertIn('<tr class="grp"><th colspan="3" scope="colgroup">零售与消费</th></tr>', page)
        self.assertIn('<span class="lead">去哪儿找新客户</span>', page)
        # a row with fewer cells than columns is padded so every row has the same width
        self.assertEqual(page.count('<td class="cell">'), 4)
        self.assertEqual(page.count('<td class="cell"></td>'), 1)

    def test_centred_layout_tokens(self):
        page = self.build()
        self.assertIn("vertical-align:middle;text-align:center", page)
        self.assertIn("display:inline-block;text-align:left", page)
        self.assertIn("word-break:keep-all;text-wrap:balance", page)
        self.assertIn("white-space:nowrap;width:1%", page)

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


if __name__ == "__main__":
    unittest.main()
