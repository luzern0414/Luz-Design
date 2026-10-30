"""Read the rule card first: py -X utf8 scripts/context.py pdf-markdown

Build a landscape table PDF (a catalogue: industries, products, directions, price lists) from a spec: one title, then
one table per section. It writes a reading HTML source, checks it with check_document.py, prints it to PDF with Edge
(bookmarks, tags, page numbers), checks the PDF with PyMuPDF and saves an overview image of every page.

    py -X utf8 scripts/make_table_pdf.py spec.json out.pdf

spec.json:
{
  "title": "企业 AI 定制服务",            # the only h1; first visible line
  "theme": "ai-agent",                   # a theme in references/themes.json (colours come from its scale)
  "max_pages": 20,                       # optional: fail when the PDF is longer
  "sections": [
    {
      "heading": "各行业都用得上的系统",    # h2 above the table
      "label": "系统",                    # header of the first column (the object names)
      "head": "能帮你做的判断",            # header spanning the content columns
      "columns": 4,                       # content cells per row
      "rows": [{"label": "获客", "cells": [["去哪儿找新客户", "从招标公告和展会名单里自动筛"], "纯文字单元格"]}]
    },
    {
      "heading": "按行业定制", "label": "行业", "head": "能帮你做的判断", "columns": 4,
      "groups": [{"name": "零售与消费", "rows": [ ... ]}]   # groups: a full-width light row above their rows
    }
  ]
}

A cell is a string, or [lead, detail]: the lead is the short answer (primary press colour, 600), the detail the
reason under it. Layout follows file-design.html 网页文件 › 组件 › 表格 and the user's table preference
(table-centred): the table is centred as a whole — header, group names and object names centred, every cell centred
vertically, content columns of equal width, and long text left-aligned inside a block that sits in the middle of its
column; the first column shrinks to its longest name. Type scale is the reading scale (32/24/16/14 px).
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
THEMES = HERE.parent / "references" / "themes.json"
FONT = '"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif'
E = html.escape


def theme_tokens(name: str) -> dict:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    theme, shared = data["themes"][name], data["shared"]
    scale = theme["scale"]
    return {
        "ink": shared["ink"], "ink2": shared["ink2"], "line": shared["line"],
        "head": scale[1],                 # 第 2 阶：表头
        "headInk": scale[8],              # 第 9 阶：表头文字
        "group": theme["actionTint"],     # 第 1 阶：分组行
        "groupInk": theme["actionPress"], # 按下阶：分组名
        "label": theme["canvas"],         # 页面极浅底：对象名列
        "lead": theme["actionPress"],     # 按下阶：单元格要点
        "icon": theme["action"], "iconTint": theme["actionTint"],
    }


def css(t: dict) -> str:
    return f"""
@page{{size:297mm 210mm;margin:12mm 14mm 14mm}}
:root{{color-scheme:light}}
*{{box-sizing:border-box}}
body{{margin:0;background:#fff;color:{t['ink']};font:16px/1.5 {FONT};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
main{{max-width:1120px;margin:0 auto;padding:48px 24px}}
h1{{margin:0 0 28px;font-size:32px;line-height:1.25;font-weight:700}}
h2{{margin:0 0 14px;font-size:24px;line-height:1.3;font-weight:700}}
section+section{{margin-top:40px}}
table{{width:100%;border-collapse:separate;border-spacing:0;table-layout:auto}}
th,td{{padding:12px 16px;font-size:16px;line-height:1.5;vertical-align:middle;text-align:center}}
thead th{{background:{t['head']};color:{t['headInk']};font-weight:600}}
thead th:first-child{{border-top-left-radius:8px}}
thead th:last-child{{border-top-right-radius:8px}}
tr.grp th{{background:{t['group']};color:{t['groupInk']};font-weight:600}}
td{{border-bottom:1px solid {t['line']}}}
td.lab{{background:{t['label']};font-weight:600;white-space:nowrap;width:1%}}
td.cell .blk{{display:inline-block;text-align:left;line-break:strict}}
td.cell .lead,td.cell .det{{word-break:keep-all;text-wrap:balance}}
td.cell .lead{{display:block;color:{t['lead']};font-weight:600}}
td.cell .det{{display:block;margin-top:2px}}
tr{{break-inside:avoid}}
tr.grp{{break-after:avoid}}
@media print{{main{{max-width:none;padding:0}}}}
@media (max-width:768px){{main{{padding:32px 16px}}.wrap{{overflow-x:auto}}table{{min-width:880px}}}}
"""


def icon(t: dict) -> str:
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' "
           f"fill='{t['iconTint']}'/><g fill='none' stroke='{t['icon']}' stroke-width='2.75' stroke-linecap='round' "
           f"stroke-linejoin='round'><path d='M8 10h16M8 16h16M8 22h16'/></g></svg>")
    return "data:image/svg+xml," + svg.replace("#", "%23").replace("<", "%3C").replace(">", "%3E")


WORDS: dict[str, list[str]] = {}


def words(text: str) -> str:
    """Escaped text with a break opportunity between words only (keep-all), so lines never split a word."""
    parts = WORDS.get(text)
    return "<wbr>".join(E(p) for p in parts) if parts else E(text)


def cell(value) -> str:
    if not value:
        return '<td class="cell"></td>'
    if isinstance(value, (list, tuple)):
        lead, detail = (list(value) + [""])[:2]
        inner = f'<span class="lead">{words(lead)}</span>' + (f'<span class="det">{words(detail)}</span>' if detail else "")
    else:
        inner = f'<span class="det">{words(str(value))}</span>'
    return f'<td class="cell"><span class="blk">{inner}</span></td>'


def rows_html(rows: list[dict], columns: int) -> str:
    out = []
    for row in rows:
        cells = list(row.get("cells", []))[:columns]
        cells += [""] * (columns - len(cells))
        out.append(f'<tr><td class="lab">{E(row["label"])}</td>{"".join(cell(c) for c in cells)}</tr>')
    return "".join(out)


def section_html(sec: dict) -> str:
    n = int(sec.get("columns", 4))
    body = []
    for g in sec.get("groups", []):
        body.append(f'<tr class="grp"><th colspan="{n + 1}" scope="colgroup">{E(g["name"])}</th></tr>')
        body.append(rows_html(g["rows"], n))
    if sec.get("rows"):
        body.append(rows_html(sec["rows"], n))
    cols = '<col>' + f'<col style="width:{100 / n:.3f}%">' * n
    return (f'<section>\n<h2>{E(sec["heading"])}</h2>\n<div class="wrap"><table>\n<colgroup>{cols}</colgroup>\n'
            f'<thead><tr><th scope="col">{E(sec.get("label", ""))}</th>'
            f'<th scope="colgroup" colspan="{n}">{E(sec.get("head", ""))}</th></tr></thead>\n'
            f'<tbody>{"".join(body)}</tbody>\n</table></div>\n</section>')


def cell_texts(spec: dict) -> list[str]:
    out = []
    for sec in spec["sections"]:
        rows = list(sec.get("rows", [])) + [r for g in sec.get("groups", []) for r in g["rows"]]
        for row in rows:
            for c in row.get("cells", []):
                out += [x for x in (c if isinstance(c, (list, tuple)) else [c]) if x]
    return out


def segment(texts: list[str]) -> None:
    """Split Chinese text into words with the browser's own segmenter (Intl.Segmenter, ICU dictionary) at build time;
    punctuation stays attached to the word before it. The published HTML carries no script."""
    from playwright.sync_api import sync_playwright
    js = """ts => { const seg = new Intl.Segmenter('zh', {granularity: 'word'});
      return ts.map(t => { const out = [];
        for (const s of seg.segment(t)) {
          if (!s.isWordLike && out.length) out[out.length - 1] += s.segment; else out.push(s.segment); }
        return out; }); }"""
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page()
        result = page.evaluate(js, texts)
        browser.close()
    WORDS.update(zip(texts, result))


def build_html(spec: dict) -> str:
    t = theme_tokens(spec.get("theme", "ai-agent"))
    sections = "\n".join(section_html(s) for s in spec["sections"])
    return (f'<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{E(spec["title"])}</title>\n'
            f'<link rel="icon" href="{icon(t)}">\n<style>{css(t)}</style>\n</head>\n<body>\n<main>\n'
            f'<h1>{E(spec["title"])}</h1>\n{sections}\n</main>\n</body>\n</html>\n')


def export_pdf(src: Path, pdf: Path, ink2: str) -> None:
    from playwright.sync_api import sync_playwright
    footer = (f'<div style="width:100%;padding:0 14mm;text-align:right;font-size:14px;color:{ink2};'
              f'font-family:{FONT.replace(chr(34), chr(39))}"><span class="pageNumber"></span></div>')
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(src.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True, outline=True, tagged=True,
                 display_header_footer=True, header_template="<div></div>", footer_template=footer)
        browser.close()


def check_pdf(pdf: Path, max_pages: int | None) -> list[str]:
    import fitz
    doc = fitz.open(pdf)
    errors = []
    w, h = doc[0].rect.width, doc[0].rect.height
    fonts = {f[3] for page in doc for f in page.get_fonts(full=True)}
    toc = doc.get_toc()
    print(f"pages {len(doc)}  size {w / 72 * 25.4:.0f}x{h / 72 * 25.4:.0f} mm  bookmarks {len(toc)}  fonts {sorted(fonts)}")
    if max_pages and len(doc) > max_pages:
        errors.append(f"{len(doc)} pages, more than max_pages {max_pages}")
    if not toc:
        errors.append("no bookmarks")
    if not fonts or any("+" not in f for f in fonts):
        errors.append(f"fonts not embedded as subsets: {sorted(fonts)}")
    blank = [i + 1 for i, page in enumerate(doc) if len(page.get_text().strip()) < 20]
    if blank:
        errors.append(f"pages without a text layer: {blank}")
    sheet = fitz.open()
    per = 6
    for start in range(0, len(doc), per):
        pg = sheet.new_page(width=w * 2, height=h * 3)
        for k, i in enumerate(range(start, min(start + per, len(doc)))):
            r = fitz.Rect((k % 2) * w, (k // 2) * h, (k % 2 + 1) * w, (k // 2 + 1) * h)
            pg.show_pdf_page(r, doc, i)
            pg.draw_rect(r, color=(0.7, 0.7, 0.7), width=1)
        out = pdf.with_name(f"{pdf.stem}-pages-{start // per + 1}.png")
        pg.get_pixmap(dpi=45).save(out)
    return errors


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    pdf = Path(args[1])
    pdf.parent.mkdir(parents=True, exist_ok=True)
    src = pdf.with_suffix(".html")
    try:
        segment(cell_texts(spec))
    except Exception as exc:          # no browser: cells fall back to ordinary CJK line breaking
        print("word segmentation skipped:", exc)
    src.write_text(build_html(spec), encoding="utf-8")
    sys.path.insert(0, str(HERE))
    import check_document
    if check_document.main([str(src)]) != 0:
        return 1
    export_pdf(src, pdf, theme_tokens(spec.get("theme", "ai-agent"))["ink2"])
    errors = check_pdf(pdf, spec.get("max_pages"))
    for e in errors:
        print("ERROR", e)
    print(pdf)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
