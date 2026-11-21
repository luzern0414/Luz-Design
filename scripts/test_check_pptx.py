"""check_document.py on .pptx: 16:9, 5% margins, scale, titles, alternate text and table headers (file-design.html 演示文稿)."""
from __future__ import annotations

import sys
import json
import subprocess
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
    def test_builtin_template_builds_with_derived_colors_and_a_single_title(self) -> None:
        root = Path(__file__).resolve().parents[1]
        generator = root / "templates/documents/slides/build_slides.py"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deck.pptx"
            spec = Path(tmp) / "spec.json"
            title = "项目提案：季度增长"
            spec.write_text(json.dumps({"layout": "cover", "title": title}), encoding="utf-8")
            build = subprocess.run([sys.executable, "-X", "utf8", str(generator), str(spec), str(path),
                                    "--theme", "teal"], capture_output=True, encoding="utf-8")
            self.assertEqual(build.returncode, 0, build.stderr + build.stdout)
            first = Presentation(str(path)).slides[0]
            self.assertEqual([shape.text for shape in first.placeholders if cd.is_title_shape(shape)], [title])
            self.assertFalse(first.shapes.title.text_frame.word_wrap)
            from zipfile import ZipFile
            from lxml import etree
            with ZipFile(path) as package:
                theme = etree.fromstring(package.read("ppt/theme/theme1.xml"))
                self.assertEqual(theme.xpath("string(//*[local-name()='clrScheme']/*[local-name()='lt2']/*/@val)"), "FFFFFF")
            spec.write_text(json.dumps({"layout": "cover", "title": "项目提案\n季度增长"}), encoding="utf-8")
            build = subprocess.run([sys.executable, "-X", "utf8", str(generator), str(spec), str(Path(tmp) / "invalid.pptx")],
                                   capture_output=True, encoding="utf-8")
            self.assertEqual(build.returncode, 1)
            self.assertIn("主标题须按放映字号排成一行", build.stdout)

    def test_a_clean_widescreen_deck_has_no_errors(self) -> None:
        d = deck()
        cover(d)
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        errors, warnings = run(d)
        self.assertEqual(errors, [], errors)
        self.assertEqual(having(warnings, "title"), [])

    def test_other_aspect_ratios_are_advisory(self) -> None:
        d = deck(widescreen=False)  # python-pptx default is 4:3
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        errors, warnings = run(d)
        self.assertEqual(errors, [])
        self.assertTrue(having(warnings, "not 16:9"))
        self.assertEqual(having(run(d, allow=("ratio",))[1], "not 16:9"), [])

    def test_text_inside_the_five_percent_margin_warns(self) -> None:
        d = deck()
        s = slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        box = s.shapes.add_textbox(Inches(0.2), Inches(2.5), Inches(5), Inches(1))
        box.text_frame.text = "贴边的文字"
        errors, warnings = run(d)
        self.assertEqual(errors, [])
        self.assertTrue(having(warnings, "5% page margin"))

    def test_full_bleed_backgrounds_and_page_numbers_may_sit_in_the_margin(self) -> None:
        d = deck()
        s = slide(d, "销售增长两成", "第二季度订单较上季增长两成", 20)
        s.shapes.add_shape(1, 0, 0, d.slide_width, d.slide_height)
        number = s.shapes.add_textbox(Inches(12.4), Inches(7.0), Inches(0.8), Inches(0.4))
        number.text_frame.text = "3"
        _, warnings = run(d)
        self.assertEqual(having(warnings, "page margin"), [])

    def test_small_and_off_scale_sizes_are_advisory(self) -> None:
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 16)
        errors, warnings = run(d)
        self.assertEqual(errors, [])
        self.assertTrue(having(warnings, "below 18pt"))
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 18)
        errors, warnings = run(d)
        self.assertEqual(errors, [])
        self.assertEqual(having(warnings, "below 18pt"), [])
        self.assertEqual(having(warnings, "off the scale"), [])
        d = deck()
        slide(d, "销售增长两成", "第二季度订单较上季增长两成", 22)
        errors, warnings = run(d)
        self.assertEqual(having(errors, "below 18pt"), [])
        self.assertTrue(having(warnings, "off the scale"))

    def test_dark_cover_can_keep_visible_attribution(self) -> None:
        from pptx.dml.color import RGBColor

        d = deck()
        s = cover(d)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = RGBColor.from_string("15375A")
        credit = s.shapes.add_textbox(Inches(1), Inches(6), Inches(9), Inches(.4))
        credit.text_frame.text = "Design by PresentationGO (www.presentationgo.com)"
        credit.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
        errors, warnings = run(d)
        self.assertEqual(errors, [])
        self.assertTrue(having(warnings, "below 18pt"))

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
