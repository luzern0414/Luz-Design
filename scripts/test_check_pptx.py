"""check_document.py on .pptx: 16:9, 5% margins, scale, titles, alternate text and table headers (file-design.html 演示文稿)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_document as cd  # noqa: E402

from pptx import Presentation  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000002000001e221bc330000000049454e44ae426082")


def deck(widescreen: bool = True) -> Presentation:
    d = Presentation()
    if widescreen:
        d.slide_width, d.slide_height = Inches(13.333), Inches(7.5)
    return d


def cover(d, title: str = "二季度经营汇报"):
    s = d.slides.add_slide(d.slide_layouts[5])
    s.shapes.title.text_frame.text = title
    s.shapes.title.left, s.shapes.title.top = Inches(1), Inches(2.5)
    s.shapes.title.width, s.shapes.title.height = Inches(11), Inches(1.5)
    return s


def slide(d, title: str = "结论一", body: str | None = None, size: float | None = None):
    s = d.slides.add_slide(d.slide_layouts[5])  # title only
    s.shapes.title.text_frame.text = title
    s.shapes.title.left, s.shapes.title.top = Inches(1), Inches(0.9)
    s.shapes.title.width, s.shapes.title.height = Inches(11), Inches(1)
    if body is not None:
        box = s.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(2))
        box.text_frame.text = body
        if size:
            box.text_frame.paragraphs[0].runs[0].font.size = Pt(size)
    return s


def run(d, allow: tuple[str, ...] = ()) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "deck.pptx"
        d.save(str(path))
        cd.ALLOWED.clear()
        cd.ALLOWED.update(allow)
        errors: list[str] = []
        warnings: list[str] = []
        try:
            cd.check_pptx(path, errors, warnings)
        finally:
            cd.ALLOWED.clear()
    return errors, warnings


def having(items: list[str], word: str) -> list[str]:
    return [i for i in items if word in i]


class DeckTest(unittest.TestCase):
    def test_a_clean_widescreen_deck_has_no_errors(self) -> None:
        d = deck()
        cover(d)
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        errors, warnings = run(d)
        self.assertEqual(errors, [], errors)
        self.assertEqual(having(warnings, "title"), [])

    def test_other_aspect_ratios_are_errors_unless_asked_for(self) -> None:
        d = deck(widescreen=False)  # python-pptx default is 4:3
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        self.assertTrue(having(run(d)[0], "not 16:9"))
        self.assertEqual(having(run(d, allow=("ratio",))[0], "not 16:9"), [])

    def test_text_inside_the_five_percent_margin_is_an_error(self) -> None:
        d = deck()
        s = slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        box = s.shapes.add_textbox(Inches(0.2), Inches(2.5), Inches(5), Inches(1))
        box.text_frame.text = "贴边的文字"
        errors, _ = run(d)
        self.assertTrue(having(errors, "5% page margin"))

    def test_full_bleed_backgrounds_and_page_numbers_may_sit_in_the_margin(self) -> None:
        d = deck()
        s = slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        s.shapes.add_shape(1, 0, 0, d.slide_width, d.slide_height)
        number = s.shapes.add_textbox(Inches(12.4), Inches(7.0), Inches(0.8), Inches(0.4))
        number.text_frame.text = "3"
        errors, _ = run(d)
        self.assertEqual(having(errors, "page margin"), [])

    def test_sizes_under_18_are_errors_and_off_scale_sizes_warn(self) -> None:
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 16)
        self.assertTrue(having(run(d)[0], "below 18pt"))
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 18)
        errors, warnings = run(d)
        self.assertEqual(having(errors, "below 18pt"), [])
        self.assertEqual(having(warnings, "off the scale"), [])
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 22)
        errors, warnings = run(d)
        self.assertEqual(having(errors, "below 18pt"), [])
        self.assertTrue(having(warnings, "off the scale"))

    def test_duplicate_titles_warn(self) -> None:
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        slide(d, "销售增长两成", "第三季度订单继续增长", 20)
        self.assertTrue(having(run(d)[1], "title repeats"))

    def test_slides_without_a_title_placeholder_warn(self) -> None:
        d = deck()
        s = d.slides.add_slide(d.slide_layouts[6])  # blank
        box = s.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
        box.text_frame.text = "销售增长两成"
        box.text_frame.paragraphs[0].runs[0].font.size = Pt(28)
        self.assertTrue(having(run(d)[1], "no title placeholder"))

    def test_pictures_need_alternate_text(self) -> None:
        d = deck()
        s = slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "dot.png"
            image.write_bytes(PNG)
            pic = s.shapes.add_picture(str(image), Inches(1), Inches(4.8), Inches(1), Inches(1))
        self.assertTrue(having(run(d)[1], "no alternate text"))
        pic._element.xpath(".//p:cNvPr")[0].set("descr", "订单增长示意")
        self.assertEqual(having(run(d)[1], "no alternate text"), [])

    def test_tables_need_a_header_row_flag(self) -> None:
        d = deck()
        s = slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        frame = s.shapes.add_table(2, 2, Inches(1), Inches(4.5), Inches(6), Inches(1.2))
        frame.table.first_row = False
        self.assertTrue(having(run(d)[1], "header row"))
        frame.table.first_row = True
        self.assertEqual(having(run(d)[1], "header row"), [])


if __name__ == "__main__":
    unittest.main()
