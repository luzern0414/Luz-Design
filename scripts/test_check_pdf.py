"""check_pdf.py: fonts, text layer, bookmarks, accessibility items and print boxes of a PDF."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fitz  # noqa: E402

import check_pdf  # noqa: E402

TEXT = "这是一页用于检查的正文，文字层必须存在，字体必须嵌入。" * 2
MM = 72 / 25.4


def make_pdf(folder: Path, name: str = "a.pdf", *, pages: int = 1, embed: bool = True, text: bool = True, toc: bool = False,
             tagged: bool = False, lang: str | None = None, title: str | None = None, display_title: bool = False,
             bleed_mm: float | None = None, width: float = 595, height: float = 842) -> Path:
    doc = fitz.open()
    buffer = fitz.Font("cjk").buffer
    for _ in range(pages):
        page = doc.new_page(width=width, height=height)
        if text and embed:
            page.insert_font(fontname="F0", fontbuffer=buffer)
            page.insert_text((72, 100), TEXT, fontname="F0", fontsize=14)
        elif text:
            page.insert_text((72, 100), "Plain body text that is long enough to count as a text layer.", fontname="helv", fontsize=14)
        if bleed_mm is not None:
            b = bleed_mm * MM
            page.set_trimbox(fitz.Rect(b, b, width - b, height - b))
            page.set_bleedbox(fitz.Rect(0, 0, width, height))
    catalog = doc.pdf_catalog()
    if title:
        doc.set_metadata({"title": title})
    if tagged:
        doc.xref_set_key(catalog, "MarkInfo", "<</Marked true>>")
        doc.xref_set_key(catalog, "StructTreeRoot", "<</Type/StructTreeRoot>>")
    if lang:
        doc.xref_set_key(catalog, "Lang", f"({lang})")
    if display_title:
        doc.xref_set_key(catalog, "ViewerPreferences", "<</DisplayDocTitle true>>")
    if toc:
        doc.set_toc([[1, "一、标题", 1]])
    path = folder / name
    doc.save(str(path))
    doc.close()
    return path


def run(path: Path, **options):
    return check_pdf.check_pdf(path, **options)


def having(items: list[str], word: str) -> list[str]:
    return [item for item in items if word in item]


class PdfCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_family_names_ignore_subset_prefix_and_separators(self) -> None:
        self.assertEqual(check_pdf.family_key("ABCDEF+Microsoft YaHei-Bold"), "microsoftyaheibold")
        self.assertIn(check_pdf.family_key("MicrosoftYaHei"), check_pdf.allowed_families("yahei"))
        self.assertIsNone(check_pdf.allowed_families("any"))
        self.assertEqual(check_pdf.allowed_families("SimSun, Arial"), {"simsun", "arial"})

    def test_unembedded_fonts_are_errors(self) -> None:
        errors, _ = run(make_pdf(self.folder, embed=False), fonts="any")
        self.assertTrue(having(errors, "without embedded font data"))

    def test_font_family_follows_the_document_and_refuses_a_fallback(self) -> None:
        pdf = make_pdf(self.folder)                       # a generic CJK fallback face is neither YaHei nor a formal face
        errors, _ = run(pdf)
        self.assertTrue(having(errors, "outside the allowed family"))
        errors, _ = run(pdf, fonts="any")
        self.assertEqual(errors, [])
        errors, _ = run(pdf, fonts="Droid Sans Fallback Regular")
        self.assertEqual(errors, [])

    def test_each_family_is_accepted_for_what_it_is_and_mixing_is_refused(self) -> None:
        check = check_pdf.font_family_errors
        yahei = ["ABCDEF+MicrosoftYaHei", "GHIJKL+MicrosoftYaHei-Bold"]
        formal = ["AUWCNV+TimesNewRomanPSMT", "LNUHNF+SimSun", "XEKKFX+SimHei", "ZZZZZZ+TimesNewRomanPS-BoldMT", "QQQQQQ+FangSong"]
        self.assertEqual(check("auto", yahei), [])
        self.assertEqual(check("auto", formal), [])
        self.assertEqual(check("auto", yahei + ["LNUHNF+SimSun"])[0].split(":")[0], "a document keeps one font family")
        self.assertTrue(check("auto", yahei + ["ABCDEF+ArialMT"]))              # a Latin fallback inside a YaHei document
        self.assertTrue(check("auto", yahei + ["ABCDEF+TimesNewRomanPSMT"]))     # Times New Roman belongs to the formal family only
        self.assertTrue(check("auto", formal + ["ABCDEF+ArialMT"]))
        self.assertTrue(check("auto", formal + ["ABCDEF+Calibri"]))
        self.assertTrue(check("yahei", formal))                                  # pinned: the old behaviour
        self.assertEqual(check("formal", formal), [])
        self.assertTrue(check("formal", yahei))
        self.assertEqual(check("any", formal + ["ArialMT"]), [])
        self.assertEqual(check("SimSun,Arial", ["LNUHNF+SimSun", "Arial"]), [])

    def test_real_embedded_faces_of_both_families_pass_when_they_are_installed(self) -> None:
        fonts = Path(r"C:/Windows/Fonts")
        files = {"yahei": fonts / "msyh.ttc", "song": fonts / "simsun.ttc", "hei": fonts / "simhei.ttf", "latin": fonts / "times.ttf"}
        if not all(f.is_file() for f in files.values()):
            self.skipTest("the Windows fonts are not installed")

        def pdf_with(name: str, faces: list[Path]) -> Path:
            doc = fitz.open()
            page = doc.new_page()
            for i, face in enumerate(faces):
                page.insert_font(fontname=f"F{i}", fontfile=str(face))
                page.insert_text((72, 100 + 30 * i), TEXT, fontname=f"F{i}", fontsize=14)
            path = self.folder / name
            doc.save(str(path), garbage=3)
            doc.close()
            return path

        errors, _ = run(pdf_with("yahei.pdf", [files["yahei"]]), bookmarks=False)
        self.assertEqual(having(errors, "font"), [], errors)
        errors, _ = run(pdf_with("formal.pdf", [files["song"], files["hei"], files["latin"]]), bookmarks=False)
        self.assertEqual(having(errors, "font"), [], errors)
        errors, _ = run(pdf_with("mixed.pdf", [files["yahei"], files["song"]]), bookmarks=False)
        self.assertTrue(having(errors, "one font family"), errors)

    def test_pages_without_text_need_the_artwork_flag(self) -> None:
        pdf = make_pdf(self.folder, text=False)
        errors, _ = run(pdf, fonts="any")
        self.assertTrue(having(errors, "without a text layer"))
        errors, _ = run(pdf, fonts="any", allow_image_pages=True)
        self.assertEqual(errors, [])

    def test_a_multi_page_document_needs_bookmarks(self) -> None:
        errors, _ = run(make_pdf(self.folder, "two.pdf", pages=2), fonts="any")
        self.assertTrue(having(errors, "bookmarks"))
        errors, _ = run(make_pdf(self.folder, "two-toc.pdf", pages=2, toc=True), fonts="any")
        self.assertEqual(errors, [])
        errors, _ = run(make_pdf(self.folder, "two-waived.pdf", pages=2), fonts="any", bookmarks=False)
        self.assertEqual(errors, [])
        errors, _ = run(make_pdf(self.folder, "one.pdf", pages=1), fonts="any")
        self.assertEqual(errors, [])

    def test_page_limit_and_mixed_sizes(self) -> None:
        errors, _ = run(make_pdf(self.folder, pages=3, toc=True), fonts="any", max_pages=2)
        self.assertTrue(having(errors, "more than the limit"))
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        doc.new_page(width=842, height=595)
        mixed = self.folder / "mixed.pdf"
        doc.save(str(mixed))
        _, warnings = run(mixed, fonts="any", allow_image_pages=True, bookmarks=False)
        self.assertTrue(having(warnings, "page sizes differ"))

    def test_accessibility_items_are_warnings_until_asked_for(self) -> None:
        pdf = make_pdf(self.folder)
        errors, warnings = run(pdf, fonts="any")
        self.assertEqual(errors, [])
        for word in ("tagged", "structure tree", "natural language", "title (", "title bar"):
            self.assertTrue(having(warnings, word), word)
        errors, _ = run(pdf, fonts="any", accessible=True)
        for word in ("tagged", "structure tree", "natural language", "title (", "title bar"):
            self.assertTrue(having(errors, word), word)

    def test_a_tagged_titled_pdf_passes_the_accessible_check(self) -> None:
        pdf = make_pdf(self.folder, tagged=True, lang="zh-CN", title="检查用文档", display_title=True)
        errors, warnings = run(pdf, fonts="any", accessible=True)
        self.assertEqual(errors, [])
        self.assertTrue(having(warnings, "by hand"))  # reading order and alternate text stay with a person

    def test_print_pdf_needs_boxes_and_three_millimetres_of_bleed(self) -> None:
        errors, _ = run(make_pdf(self.folder, "plain.pdf"), fonts="any", print_ready=True)
        self.assertTrue(having(errors, "TrimBox"))
        errors, _ = run(make_pdf(self.folder, "short.pdf", bleed_mm=2), fonts="any", print_ready=True)
        self.assertTrue(having(errors, "bleed under 3 mm"))
        errors, _ = run(make_pdf(self.folder, "ok.pdf", bleed_mm=3), fonts="any", print_ready=True)
        self.assertEqual(errors, [])

    def test_low_resolution_and_rgb_images_are_reported_for_print(self) -> None:
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_font(fontname="F0", fontbuffer=fitz.Font("cjk").buffer)
        page.insert_text((72, 100), TEXT, fontname="F0", fontsize=14)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 100, 100), False)
        pix.clear_with(200)
        page.insert_image(fitz.Rect(72, 150, 372, 450), pixmap=pix)  # 100 px over 300 pt: 24 ppi
        page.set_trimbox(fitz.Rect(9, 9, 586, 833))
        page.set_bleedbox(fitz.Rect(0, 0, 595, 842))
        path = self.folder / "image.pdf"
        doc.save(str(path))
        _, warnings = run(path, fonts="any", print_ready=True)
        self.assertTrue(having(warnings, "ppi"))
        self.assertTrue(having(warnings, "RGB images"))

    def test_cli_exit_codes(self) -> None:
        good = make_pdf(self.folder, "good.pdf")
        bad = make_pdf(self.folder, "bad.pdf", embed=False)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_pdf.main([str(good), "--fonts", "any"]), 0)
            self.assertEqual(check_pdf.main([str(bad), "--fonts", "any"]), 1)
            self.assertEqual(check_pdf.main([str(self.folder / "missing.pdf")]), 1)

    def test_unreadable_files_are_errors(self) -> None:
        broken = self.folder / "broken.pdf"
        broken.write_bytes(b"not a pdf")
        errors, _ = run(broken)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
