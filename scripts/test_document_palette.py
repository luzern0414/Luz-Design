"""A topic selected in the spec must reach actual Office table fills."""
import tempfile
import unittest
from pathlib import Path

import docx
import openpyxl
from docx.oxml.ns import qn

import make_docx
import make_xlsx


class DocumentPaletteTest(unittest.TestCase):
    def test_spreadsheet_uses_the_reference_palette_whatever_the_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            fills = []
            for theme in ("coffee", "pharmacy"):
                out = make_xlsx.build({"title": "服务清单", "theme": theme,
                    "columns": [{"name": "类别", "merge": True}, {"name": "项目"}],
                    "rows": [["一类", "甲"], ["一类", "乙"], ["二类", "丙"]]}, Path(tmp) / (theme + ".xlsx"))
                book = openpyxl.load_workbook(out)
                ws = book.active
                fills.append(ws.cell(3, 1).fill.fgColor.rgb)
                self.assertEqual(ws.cell(4, 1).fill.fgColor.rgb, ws.cell(6, 1).fill.fgColor.rgb)
                book.close()
            self.assertEqual(fills, ["00ECF0F6", "00ECF0F6"])      # header: the light blue-grey

    def test_word_uses_selected_topic_in_exported_table_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            fills = []
            for theme in ("coffee", "pharmacy"):
                out = make_docx.build({"type": "report", "title": "服务清单", "theme": theme,
                    "sections": [{"heading": "项目", "table": {"header": ["名称", "内容"],
                        "rows": [["一项", "内容"]]}}]}, Path(tmp) / (theme + ".docx"))
                cell = docx.Document(out).tables[0].cell(0, 0)
                fills.append(cell._tc.get_or_add_tcPr().find(qn("w:shd")).get(qn("w:fill")))
            self.assertNotEqual(*fills)


if __name__ == "__main__":
    unittest.main()
