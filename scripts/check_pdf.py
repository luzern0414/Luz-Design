#!/usr/bin/env python3
"""Check a PDF the way file-design.html 便携式文档 and visual-design.html 海报、品牌主视觉与产品宣传 describe it.

  py -X utf8 scripts/check_pdf.py <文件.pdf> [--fonts auto|yahei|formal|any|NAME[,NAME]] [--accessible] [--print] [--max-pages N]
                                           [--allow-image-pages] [--no-bookmarks]

Always checked (ERROR): the file opens; every font is embedded; fonts are one allowed family; every page has a text layer (--allow-image-pages waives it for artwork); a document
of more than one page carries bookmarks (--no-bookmarks waives it). Mixed page sizes are reported as a warning.

Fonts adapt to the document (--fonts auto, the default). A document set in Microsoft YaHei (MicrosoftYaHei, -Bold, -Light) is a
yahei document; a formal Word document (client proposals, manuals, contracts, official papers) is set in 宋体 or 仿宋 and 黑体 or 楷体
for Chinese and Times New Roman for letters and digits, and is a formal document. Each family is accepted for what it is. What is
refused: a document that mixes the two, and any font outside the family it uses (an exporter fallback such as Arial, Calibri or
a generic CJK font). --fonts yahei or formal pins one family, --fonts any skips the check, a list of names allows exactly those.

--accessible turns the accessibility items into ERRORs (without it they are warnings): tagged (MarkInfo Marked and a structure
tree), natural language (/Lang), a title (/Title in the information dictionary, WCAG technique PDF18) shown in the title bar
(ViewerPreferences DisplayDocTitle true). The XMP dc:title that PDF/UA-1 asks for (Matterhorn 06-003) is a warning.
Reading order, alternate text and table headers need a person (Matterhorn 09-001, 13-004, 15-001): this script lists them, it
cannot judge them, and passing it does not make a PDF conform to PDF/UA.

--print checks a print-ready PDF: each page has a TrimBox and a BleedBox, the bleed is at least 3 mm on every side, raster
images reach 300 ppi at the size they are placed (warning) and RGB images are reported (warning: printers ask for CMYK).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MM = 72 / 25.4
MIN_BLEED_MM = 3.0
MIN_PPI = 300
YAHEI = {"microsoftyahei", "microsoftyaheibold", "microsoftyaheilight", "微软雅黑"}
# The formal family: Chinese in a Song or Fangsong face and a Hei or Kai face (Windows and macOS names), letters and digits in Times New Roman.
FORMAL_CJK = ("simsun", "nsimsun", "simhei", "simfang", "fangsong", "simkai", "kaiti", "stsong", "stheiti", "stfangsong", "stkaiti", "songti", "heiti",
              "宋体", "黑体", "仿宋", "楷体")
FORMAL_LATIN = ("timesnewroman",)
HUMAN_ITEMS = "reading order, alternate text of figures and table header cells still need a person (Matterhorn 09-001, 13-004, 15-001)"


def family_key(name: str) -> str:
    return name.split("+")[-1].replace(" ", "").replace("-", "").replace("_", "").lower()


def is_yahei(key: str) -> bool:
    return key in YAHEI or key.startswith("microsoftyahei")


def is_formal_cjk(key: str) -> bool:
    return key.startswith(FORMAL_CJK)


def is_formal(key: str) -> bool:
    return is_formal_cjk(key) or key.startswith(FORMAL_LATIN)


def allowed_families(option: str) -> set[str] | None:
    """None means any family (or, for auto, that the family is decided from the fonts the document uses)."""
    if option in ("any", "auto"):
        return None
    if option == "yahei":
        return set(YAHEI)
    return {family_key(item) for item in option.split(",") if item.strip()}


def font_family_errors(fonts: str, names: list[str]) -> list[str]:
    """Fonts outside the allowed family. With ``auto`` the family follows the document: formal when it uses a Song or Hei face, else YaHei."""
    keys = {name: family_key(name) for name in names}
    if fonts == "any":
        return []
    if fonts == "auto":
        yahei = sorted(n for n, k in keys.items() if is_yahei(k))
        formal = sorted(n for n, k in keys.items() if is_formal_cjk(k))
        if yahei and formal:
            return [f"a document keeps one font family: it mixes Microsoft YaHei {yahei} with the formal faces {formal}; export again from one source with one family"]
        style = "formal" if formal else "yahei"
    else:
        style = fonts
    if style == "formal":
        unexpected = sorted(n for n, k in keys.items() if not is_formal(k))
    elif style == "yahei":
        unexpected = sorted(n for n, k in keys.items() if not is_yahei(k))
    else:
        allowed = allowed_families(style) or set()
        unexpected = sorted(n for n, k in keys.items() if k not in allowed)
    if not unexpected:
        return []
    return [f"fonts outside the allowed family ({style}): {unexpected}; export again, a fallback font was used"]


def catalog_value(doc, key: str) -> str | None:
    kind, value = doc.xref_get_key(doc.pdf_catalog(), key)
    return None if kind == "null" else value


def check_pdf(path: Path, *, fonts: str = "auto", accessible: bool = False, print_ready: bool = False,
              max_pages: int | None = None, allow_image_pages: bool = False, bookmarks: bool = True) -> tuple[list[str], list[str]]:
    import fitz

    errors: list[str] = []
    warnings: list[str] = []
    try:
        doc = fitz.open(str(path))
    except Exception as exc:  # corrupt or not a PDF
        return [f"cannot open: {exc}"], []
    if not doc.is_pdf or doc.page_count == 0:
        return ["not a PDF or no pages"], []
    if doc.needs_pass:
        return ["encrypted: assistive technology needs access (PDF/UA, Matterhorn 26-001)"], []

    pages = doc.page_count
    if max_pages and pages > max_pages:
        errors.append(f"{pages} pages, more than the limit {max_pages}")

    sizes = {(round(p.rect.width), round(p.rect.height)) for p in doc}
    if len(sizes) > 1:
        warnings.append("page sizes differ: " + ", ".join(f"{w / MM:.0f}x{h / MM:.0f} mm" for w, h in sorted(sizes)))

    # Fonts: embedded, in the allowed family.
    font_rows = {f[0]: f for page in doc for f in page.get_fonts(full=True)}
    missing = [row[3] for xref, row in font_rows.items() if not doc.extract_font(xref)[3]]
    if missing:
        errors.append(f"fonts without embedded font data: {sorted(set(missing))}")
    errors.extend(font_family_errors(fonts, sorted({row[3] for row in font_rows.values()})))

    # Text layer.
    if not allow_image_pages:
        blank = [i + 1 for i, page in enumerate(doc) if len(page.get_text().strip()) < 20]
        if blank:
            errors.append(f"pages without a text layer: {blank} (scanned or outlined text is not searchable; --allow-image-pages for artwork)")

    # Bookmarks.
    toc = doc.get_toc()
    if bookmarks and pages > 1 and not toc:
        errors.append("no bookmarks: export with the heading outline (Word: create bookmarks from headings; browser: outline on)")
    if bookmarks:
        for index, (_level, title, destination) in enumerate(toc, 1):
            if not title.strip() or not 1 <= destination <= pages:
                errors.append(f"invalid bookmark destination at outline item {index}: {title!r}, page {destination}; verify the actual heading page")

    # Accessibility.
    problems: list[str] = []
    mark_info = catalog_value(doc, "MarkInfo") or ""
    if not re.search(r"/Marked\s+true", mark_info) and not re.search(r"Marked\s+true", mark_info):
        problems.append("not marked as tagged (MarkInfo Marked is not true)")
    if catalog_value(doc, "StructTreeRoot") is None:
        problems.append("no structure tree (StructTreeRoot): headings, lists and tables are not tagged")
    if not (catalog_value(doc, "Lang") or "").strip("() "):
        problems.append("no natural language (/Lang in the catalog; WCAG technique PDF16)")
    if not (doc.metadata or {}).get("title", "").strip():
        problems.append("no title (/Title in the information dictionary; WCAG technique PDF18)")
    prefs = catalog_value(doc, "ViewerPreferences") or ""
    if "DisplayDocTitle" not in prefs:
        # The preferences may be an indirect object.
        kind, value = doc.xref_get_key(doc.pdf_catalog(), "ViewerPreferences")
        if kind == "xref":
            prefs = doc.xref_object(int(value.split()[0]), compressed=False)
    if not re.search(r"DisplayDocTitle\s+true", prefs):
        problems.append("the title bar shows the file name (ViewerPreferences DisplayDocTitle is not true)")
    (errors if accessible else warnings).extend(problems)
    xmp = doc.get_xml_metadata() or ""
    if accessible and not re.search(r"<dc:title", xmp):
        warnings.append("no XMP dc:title (PDF/UA-1, Matterhorn 06-003)")
    if accessible:
        warnings.append("by hand: " + HUMAN_ITEMS)

    if print_ready:
        for number, page in enumerate(doc, 1):
            trim, bleed = page.trimbox, page.bleedbox
            if trim == page.mediabox and bleed == page.mediabox:
                errors.append(f"page {number}: no TrimBox/BleedBox set, so the printer cannot see the trim size")
                continue
            sides = (trim.x0 - bleed.x0, trim.y0 - bleed.y0, bleed.x1 - trim.x1, bleed.y1 - trim.y1)
            short = [f"{side / MM:.1f}" for side in sides if side / MM < MIN_BLEED_MM - 0.05]
            if short:
                errors.append(f"page {number}: bleed under {MIN_BLEED_MM:g} mm on a side ({', '.join(short)} mm)")
        low, rgb = [], []
        for number, page in enumerate(doc, 1):
            for info in page.get_image_info(xrefs=True):
                width_in = (info["bbox"][2] - info["bbox"][0]) / 72
                if width_in > 0 and info["width"] / width_in < MIN_PPI - 1:
                    low.append(f"page {number}: {info['width'] / width_in:.0f} ppi")
                if info.get("xref") and info.get("colorspace") == 3:
                    rgb.append(number)
        if low:
            warnings.append(f"images under {MIN_PPI} ppi at the placed size: {low[:5]}")
        if rgb:
            warnings.append(f"RGB images on pages {sorted(set(rgb))}: printers ask for CMYK; convert and look at the result again")
    doc.close()
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--fonts", default="auto", help="auto (default: follows the document, YaHei or the formal faces), yahei, formal, any, or a comma-separated list of font names")
    parser.add_argument("--accessible", action="store_true", help="accessibility items are errors")
    parser.add_argument("--print", dest="print_ready", action="store_true", help="print-ready PDF: bleed boxes, ppi, colour")
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--allow-image-pages", action="store_true")
    parser.add_argument("--no-bookmarks", action="store_true")
    args = parser.parse_args(argv)
    failed = False
    for path in args.files:
        if not path.is_file():
            errors, warnings = ["file not found"], []
        else:
            errors, warnings = check_pdf(path, fonts=args.fonts, accessible=args.accessible, print_ready=args.print_ready,
                                         max_pages=args.max_pages, allow_image_pages=args.allow_image_pages,
                                         bookmarks=not args.no_bookmarks)
        print(f"{'FAIL' if errors else 'PASS'}: {path} ({len(errors)} error(s), {len(warnings)} warning(s))")
        for item in errors:
            print("  ERROR", item)
        for item in warnings:
            print("  WARN ", item)
        failed |= bool(errors)
    if not failed:
        print("Automated checks passed. Render every page and look at it: title left edge, table fragments, line breaks, orphan headers.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
