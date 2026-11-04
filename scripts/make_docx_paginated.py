"""Read the rule card first: py -X utf8 scripts/context.py docx

Build a formal Word document and settle what only a rendering can tell: which page each heading lands on (the contents list)
and where a table runs over a page break (it then continues under 续表 N with its header row repeated).

    py -X utf8 scripts/make_docx_paginated.py spec.json out.docx      (spec: make_docx.py, with "cover", "toc", "mono")

The document is laid out through the Word-compatible application installed on this machine (WPS Writer or Word, driven by
docx_layout.ps1), which also writes ``out.pdf`` next to the .docx: that PDF is the Word document as Word prints it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_docx  # noqa: E402


def layout(docx: Path, pdf: Path, report: Path) -> dict:
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "docx_layout.ps1"),
                    "-In", str(docx.resolve()), "-Pdf", str(pdf.resolve()), "-Json", str(report.resolve())], check=True, capture_output=True)
    return json.loads(report.read_text(encoding="utf-8-sig"))


def label_pdf(pdf: Path, title: str, language: str = "zh-CN") -> None:
    """The Word application's PDF carries bookmarks but no title or language: add the document title (WCAG PDF18), the
    language (PDF16) and show the title, not the file name, in the viewer's title bar. Tagging is not offered by WPS."""
    import fitz
    doc = fitz.open(str(pdf))
    doc.set_metadata({**(doc.metadata or {}), "title": title})
    catalog = doc.pdf_catalog()
    doc.xref_set_key(catalog, "Lang", f"({language})")
    doc.xref_set_key(catalog, "ViewerPreferences", "<</DisplayDocTitle true>>")
    tmp = pdf.with_name(pdf.stem + ".labelled.pdf")
    doc.save(str(tmp), garbage=0, deflate=True)
    doc.close()
    tmp.replace(pdf)


WHITESPACE = re.compile(r"\s+")
# A title line starts "表 N" and goes on after the full-width space (or ends there); "表 3 shows …" in running text has an ASCII space.
CAPTION_LINE = re.compile(r"^\s*(续表|表)\s*(\d+)(?:[^\S ]|\s*$)")


def docx_captions(docx: Path) -> list[tuple[str, int]]:
    """The table titles of a built document as written into the file: [("表", 1), ("续表", 1), ("表", 2) …].
    The number of a 表 is the cached value of its SEQ field, which is what the PDF shows (the exporter does not
    update fields); 续表 is plain text and repeats the number of the table it continues."""
    import docx as python_docx
    found = []
    for p in python_docx.Document(str(docx)).paragraphs:
        m = CAPTION_LINE.match(p.text) if p.style.name == "Caption" else None
        if m:
            found.append((m.group(1), int(m.group(2))))
    return found


def caption_errors(captions: list[tuple[str, int]]) -> list[str]:
    """Table numbers run 1, 2, 3 … without a gap (a SEQ field counts the 表 captions only, so 续表 must not take a
    number), and every 续表 carries the number of the table above it."""
    errors, last = [], 0
    for kind, number in captions:
        if kind == "表":
            if number != last + 1:
                errors.append(f"表 {number} follows 表 {last}: table numbers must run 1, 2, 3 … (Word would renumber the SEQ fields)")
            last = number
        elif number != last:
            errors.append(f"续表 {number} sits under 表 {last}: a continued table repeats the number of its table")
    return errors


def pdf_captions(pdf: Path) -> list[tuple[str, int]]:
    """The table titles as the exported PDF shows them, in reading order."""
    import fitz
    found = []
    with fitz.open(str(pdf)) as doc:
        for page in doc:
            for line in page.get_text().splitlines():
                m = CAPTION_LINE.match(line)
                if m:
                    found.append((m.group(1), int(m.group(2))))
    return found


def docx_caption_titles(docx: Path) -> list[tuple[str, int, str]]:
    """Like docx_captions, with the title after the number: ("表", 3, "丙"); a 续表 has none."""
    import docx as python_docx
    found = []
    for p in python_docx.Document(str(docx)).paragraphs:
        m = CAPTION_LINE.match(p.text) if p.style.name == "Caption" else None
        if m:
            found.append((m.group(1), int(m.group(2)), p.text[m.end():].strip()))
    return found


def verify_captions(docx: Path, pdf: Path) -> list[str]:
    """Errors when the table numbers are not consecutive, or the PDF does not show each title with the number the document's
    field holds. The PDF is searched with every kind of whitespace taken out, in the order of the document, so it does not matter
    how the exporter breaks the line between the number and the title; a sentence that starts with 表 3 cannot be taken for a title
    because the title text has to follow the number."""
    import fitz
    written = docx_caption_titles(docx)
    errors = caption_errors([(kind, number) for kind, number, _ in written])
    with fitz.open(str(pdf)) as doc:
        flat = WHITESPACE.sub("", "".join(page.get_text() for page in doc))
    at = 0
    for kind, number, title in written:
        want = f"{kind}{number}{WHITESPACE.sub('', title)}"
        found = flat.find(want, at)
        if found < 0:
            errors.append(f"the PDF does not show {kind} {number}{'　' + title if title else ''} where the document has it: the exporter drew other numbers than the fields hold")
            continue
        at = found + len(want)
    return errors


def build(spec: dict, out: Path, max_passes: int = 5) -> dict:
    spec = json.loads(json.dumps(spec))
    out = Path(out)
    pdf, report = out.with_suffix(".pdf"), Path(tempfile.gettempdir()) / (out.stem + ".layout.json")
    tables = [b["table"] for s in spec["sections"] for b in s.get("blocks", []) if "table" in b]
    for t in tables:
        t["breaks"] = []
    lay: dict = {}
    for n in range(max_passes):
        make_docx.build(spec, out)
        lay = layout(out, pdf, report)
        changed, at = False, 0
        for t in tables:
            cuts = [0] + sorted(t["breaks"]) + [len(t["rows"])]
            found = set(t["breaks"])
            for k in range(len(cuts) - 1):                      # each piece of a logical table is one Word table
                data_pages = lay["tables"][at][1:]
                at += 1
                found |= {cuts[k] + i for i in range(1, len(data_pages)) if data_pages[i] != data_pages[i - 1]}
            if sorted(found) != sorted(t["breaks"]):
                t["breaks"], changed = sorted(found), True
        print(f"pass {n + 1}: {lay['pages']} pages, tables continued at rows {[t['breaks'] for t in tables if t['breaks']]}")
        if not changed:
            break
    heads = lay["headings"]
    if heads:
        spec["toc_pages"] = [h[2] - heads[0][2] + 1 for h in heads]   # the page numbers the body shows (it restarts at 1)
    make_docx.build(spec, out)
    lay = layout(out, pdf, report)
    label_pdf(pdf, str(spec.get("title") or out.stem))
    errors = verify_captions(out, pdf)
    if errors:
        raise RuntimeError("table captions: " + "; ".join(errors))
    return lay


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    lay = build(json.loads(Path(argv[0]).read_text(encoding="utf-8-sig")), Path(argv[1]))
    print("wrote", argv[1], f"({lay['pages']} pages) and", Path(argv[1]).with_suffix(".pdf"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
