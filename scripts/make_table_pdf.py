"""Read the rule card first: py -X utf8 scripts/context.py pdf-markdown

Build a landscape table PDF (a catalogue: industries, products, directions, price lists) from a spec: one title, then
one table per section. It writes a reading HTML source, checks it with check_document.py, prints it to PDF with Edge
(bookmarks, tags, page numbers), checks the PDF with PyMuPDF and saves an overview image of every page.

    py -X utf8 scripts/make_table_pdf.py spec.json out.pdf

spec.json:
{
  "title": "企业 AI 定制服务",            # the only h1; first visible line
  "theme": "ai-agent",                   # required: choose for this topic, not a universal default
  "keep_together": ["资质", "试销"],       # optional domain glossary: prevent ICU from splitting these words
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

Optional per section (for lists whose cells carry sentences, e.g. a feature list with a rules column):
  "heads":  ["功能说明", "业务规则", "使用端", "类型"]   one header per content column instead of the single spanning "head"
  "widths": [3, 4, 2, 1]                               relative widths of the content columns (the first column stays 144px)
  "fill":   true                                       cells use the full column width, long text left-aligned (default: centred 192px blocks)
A cell is a string, or [lead, detail]: write each item for its own context, without a shared character limit.
Column headers and object names are centred; document, section and group headings share a left baseline.
Actual row heights drive pagination. Each physical fragment repeats its table header and has four rounded corners.
Type scale is the reading scale (32/24/20/16/14 px). Review word breaks after rendering; ICU is not a domain glossary.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
THEMES = HERE.parent / "references" / "themes.json"
FONT = '"Microsoft YaHei"'
E = html.escape


def theme_tokens(name: str) -> dict:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    theme, shared = data["themes"][name], data["shared"]
    scale = theme.get("scale")
    return {
        "ink": shared["ink"], "ink2": shared["ink2"], "line": shared["line"],
        "head": scale[1] if scale else theme["actionTint"],
        "headInk": scale[8] if scale else theme["actionPress"],
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
body{{margin:0;background:#fff;color:{t['ink']};font:16px/1.45 {FONT};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
main{{width:269mm;margin:0 auto;padding:0}}
h1{{margin:0 0 18px;font-size:32px;line-height:1.25;font-weight:700}}
h2,.section-heading{{margin:0 0 12px;font-size:24px;line-height:1.3;font-weight:600;text-align:left}}
h3,.group-heading{{margin:0 0 10px;font-size:20px;line-height:1.3;font-weight:600;text-align:left}}
section+section,.catalog-group+.catalog-group{{margin-top:24px}}
.table-frame{{width:100%;border:1px solid {t['line']};border-radius:12px;overflow:hidden}}
table{{width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed}}
col:first-child{{width:144px}}
th,td{{padding:6px 16px;font-size:16px;line-height:1.45;vertical-align:middle;text-align:center}}
thead th{{background:{t['head']};color:{t['headInk']};font-weight:600}}
thead th{{padding-top:10px;padding-bottom:10px}}
td{{border-bottom:1px solid {t['line']}}}
tbody tr:last-child td{{border-bottom:0}}
td.lab{{background:{t['label']};font-weight:600;white-space:normal;word-break:keep-all;text-wrap:balance}}
td.cell .blk{{display:block;width:100%;max-width:192px;margin:0 auto;text-align:left;line-break:strict}}
td.cell .lead,td.cell .det{{word-break:keep-all;text-wrap:balance}}
.fill td.cell{{text-align:left}}
.fill td.cell .lead,.fill td.cell .det{{text-wrap:pretty}}
.fill td.cell .blk{{max-width:none;margin:0}}
.fill td.cell.short{{text-align:center}}
.fill td.cell.short .blk{{text-align:center}}
td.cell .lead{{display:block;color:{t['lead']};font-weight:600;line-height:1.4}}
td.cell .det{{display:block;margin-top:3px}}
tr{{break-inside:avoid}}
.print-page{{width:269mm;height:183.8mm;display:flow-root;break-after:page}}
.print-page:last-child{{break-after:auto}}
.table-part{{break-inside:avoid}}
.table-part+.table-part,.table-part+h2{{margin-top:24px}}
@media screen{{main{{margin:32px auto}}.print-page+.print-page{{margin-top:32px}}}}
@media print{{main{{margin:0;padding:0}}}}
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


def cell(value, fill: bool = False) -> str:
    if not value:
        return '<td class="cell"></td>'
    if fill and isinstance(value, str) and len(value) <= 6:
        return f'<td class="cell short"><span class="blk"><span class="det">{words(value)}</span></span></td>'
    if isinstance(value, (list, tuple)):
        lead, detail = (list(value) + [""])[:2]
        inner = f'<span class="lead">{words(lead)}</span>' + (f'<span class="det">{words(detail)}</span>' if detail else "")
    else:
        inner = f'<span class="det">{words(str(value))}</span>'
    return f'<td class="cell"><span class="blk">{inner}</span></td>'


def rows_html(rows: list[dict], columns: int, fill: bool = False) -> str:
    out = []
    for row in rows:
        cells = list(row.get("cells", []))[:columns]
        cells += [""] * (columns - len(cells))
        out.append(f'<tr><td class="lab">{words(row["label"])}</td>{"".join(cell(c, fill) for c in cells)}</tr>')
    return "".join(out)


def section_html(sec: dict) -> str:
    n = int(sec.get("columns", 4))
    groups = list(sec.get("groups", []))
    if sec.get("rows"):
        groups.append({"name": "", "rows": sec["rows"]})
    heads, widths, fill = sec.get("heads"), sec.get("widths"), bool(sec.get("fill"))
    if heads and len(heads) != n:
        raise ValueError(f'section "{sec.get("heading")}": heads needs {n} entries, got {len(heads)}')
    if widths and len(widths) != n:
        raise ValueError(f'section "{sec.get("heading")}": widths needs {n} entries, got {len(widths)}')
    if widths:
        total = float(sum(widths))
        # percentages of the table (the first column keeps 144px of the 269mm page width, about 14%)
        cols = '<col>' + "".join(f'<col style="width:{85.0 * w / total:.2f}%">' for w in widths)
    else:
        cols = '<col>' + '<col>' * n
    if heads:
        thead = f'<th scope="col">{E(sec.get("label", ""))}</th>' + "".join(f'<th scope="col">{E(h)}</th>' for h in heads)
    else:
        thead = f'<th scope="col">{E(sec.get("label", ""))}</th><th scope="colgroup" colspan="{n}">{E(sec.get("head", ""))}</th>'
    parts = []
    for group in groups:
        heading = f'<h3>{E(group["name"])}</h3>' if group["name"] else ""
        table_tag = '<table class="fill">' if fill else "<table>"
        parts.append(f'<div class="catalog-group">{heading}<div class="wrap table-frame">{table_tag}'
                     f'<colgroup>{cols}</colgroup><thead><tr>{thead}</tr></thead>'
                     f'<tbody>{rows_html(group["rows"], n, fill)}</tbody></table></div></div>')
    return f'<section>\n<h2>{E(sec["heading"])}</h2>\n{"".join(parts)}\n</section>'


def cell_texts(spec: dict) -> list[str]:
    out = []
    for sec in spec["sections"]:
        rows = list(sec.get("rows", [])) + [r for g in sec.get("groups", []) for r in g["rows"]]
        for row in rows:
            for c in row.get("cells", []):
                out += [x for x in (c if isinstance(c, (list, tuple)) else [c]) if x]
    return out


def segment(texts: list[str], protected_terms: list[str] | tuple[str, ...] = ()) -> None:
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
    for text, parts in zip(texts, result):
        boundaries, position = set(), 0
        for part in parts[:-1]:
            position += len(part)
            boundaries.add(position)
        for term in protected_terms:
            if not term:
                continue
            start = text.find(term)
            while start >= 0:
                boundaries.difference_update(range(start + 1, start + len(term)))
                start = text.find(term, start + 1)
        positions = [0, *sorted(boundaries), len(text)]
        WORDS[text] = [text[a:b] for a, b in zip(positions, positions[1:]) if a != b]


def build_html(spec: dict) -> str:
    if not spec.get("theme"):
        raise ValueError("theme is required: choose a palette for the document's topic")
    t = theme_tokens(spec["theme"])
    sections = "\n".join(section_html(s) for s in spec["sections"])
    return (f'<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{E(spec["title"])}</title>\n'
            f'<link rel="icon" href="{icon(t)}">\n<style>{css(t)}</style>\n</head>\n<body>\n<main>\n'
            f'<h1>{E(spec["title"])}</h1>\n{sections}\n</main>\n</body>\n</html>\n')


def paginate_html(src: Path) -> dict:
    """Measure real text with Edge, then save static physical page fragments before PDF export.

    A fragment has a complete rounded frame, a repeated header, and at least two rows when possible.
    Text is never cut to fit; a row taller than a page is a build error that needs an editorial/layout decision.
    """
    from playwright.sync_api import sync_playwright
    js = """() => {
      const main = document.querySelector('main');
      if (!main.querySelector('.print-page')) {
        const title = main.querySelector(':scope > h1');
        const sections = [...main.querySelectorAll(':scope > section')].map(s => ({
          heading:s.querySelector(':scope > h2'),
          groups:[...s.querySelectorAll(':scope > .catalog-group')].map(g => ({
            heading:g.querySelector('h3'), table:g.querySelector('table'),
            rows:[...g.querySelectorAll('tbody > tr')]
          }))
        }));
        main.replaceChildren();
        let page;
        const newPage = () => { page = document.createElement('div'); page.className='print-page'; main.append(page); };
        const fits = () => [...page.children].every(n => n.getBoundingClientRect().bottom <= page.getBoundingClientRect().bottom - 0.5);
        const fragment = (g, continuation, sectionName) => {
          const part=document.createElement('div');part.className='table-part';
          if(g.heading) {
            const h=continuation ? document.createElement('div') : g.heading.cloneNode(true);
            if(continuation){h.className='group-heading';h.textContent=g.heading.textContent;}
            part.append(h);
          } else if(continuation) {
            const h=document.createElement('div');h.className='section-heading';h.textContent=sectionName;part.append(h);
          }
          const frame=document.createElement('div');frame.className='wrap table-frame';
          const table=g.table.cloneNode(false);
          table.append(g.table.querySelector('colgroup').cloneNode(true),g.table.querySelector('thead').cloneNode(true),document.createElement('tbody'));
          frame.append(table);part.append(frame);return part;
        };
        newPage(); if(title) page.append(title);
        for(const section of sections) {
          let sectionPending=true;
          for(const g of section.groups) {
            let offset=0;
            while(offset<g.rows.length) {
              let sectionHeading;
              if(sectionPending){sectionHeading=section.heading.cloneNode(true);page.append(sectionHeading);}
              const part=fragment(g,offset>0,section.heading.textContent);page.append(part);
              const body=part.querySelector('tbody');let count=0;
              while(offset+count<g.rows.length) {
                const row=g.rows[offset+count].cloneNode(true);body.append(row);
                if(!fits()){row.remove();break;}count++;
              }
              const minimum=Math.min(2,g.rows.length-offset);
              if(count<minimum) {
                part.remove();if(sectionHeading)sectionHeading.remove();
                if(!page.children.length || (page.children.length===1 && page.firstElementChild.tagName==='H1'))
                  throw new Error('A row or heading is too tall for the page; revise the layout without truncating text.');
                newPage();continue;
              }
              if(g.rows.length-offset-count===1 && count>2){body.lastElementChild.remove();count--;}
              offset+=count;sectionPending=false;
              if(offset<g.rows.length)newPage();
            }
          }
        }
      }
      const firstPage=main.querySelector('.print-page'),firstTitle=firstPage?.querySelector(':scope > h1');
      if(firstTitle && firstTitle.nextElementSibling?.tagName!=='SECTION') {
        const section=document.createElement('section');
        while(firstTitle.nextElementSibling)section.append(firstTitle.nextElementSibling);
        firstPage.append(section);
      }
      const pages=[...main.querySelectorAll('.print-page')],errors=[],fragments=[],headingOffsets=[];
      pages.forEach((p,i)=>{
        const pr=p.getBoundingClientRect();
        for(const h of p.querySelectorAll('h1,h2,h3,.group-heading,.section-heading'))headingOffsets.push(Math.abs(h.getBoundingClientRect().left-pr.left));
        for(const f of p.querySelectorAll('.table-frame')) {
          const r=f.getBoundingClientRect(),s=getComputedStyle(f);
          fragments.push({page:i+1,rows:f.querySelectorAll('tbody>tr').length,
            radius:[s.borderTopLeftRadius,s.borderTopRightRadius,s.borderBottomRightRadius,s.borderBottomLeftRadius].map(parseFloat),
            box:[r.left-pr.left,r.top-pr.top,r.width,r.height],overflow:s.overflow});
          if(r.bottom>pr.bottom+0.5)errors.push('Frame overflows page '+(i+1));
        }
        for(const el of p.querySelectorAll('.lead,.det,.lab'))
          if(el.scrollWidth>el.clientWidth+1)errors.push('Text overflows its column on page '+(i+1)+': '+el.textContent);
      });
      return {pages:pages.length,rows:main.querySelectorAll('td.lab').length,fragments,heading_offsets:headingOffsets,errors};
    }"""
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1200, "height": 900})
            page.emulate_media(media="print")
            page.goto(src.resolve().as_uri())
            page.evaluate("document.fonts.ready")
            report = page.evaluate(js)
            if report["errors"]:
                raise ValueError("; ".join(report["errors"]))
            src.write_text(page.content(), encoding="utf-8")
            return report
        finally:
            browser.close()


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
    allowed = {"microsoftyahei", "microsoftyaheibold", "microsoftyaheilight", "微软雅黑"}
    unexpected = sorted(f for f in fonts if f.split("+")[-1].replace(" ", "").replace("-", "").lower() not in allowed)
    if unexpected:
        errors.append(f"PDF fonts must be MicrosoftYaHei (微软雅黑); unexpected: {unexpected}")
    xrefs = {f[0] for page in doc for f in page.get_fonts(full=True)}
    missing = [xref for xref in xrefs if not doc.extract_font(xref)[3]]
    if missing:
        errors.append(f"fonts without embedded font data: {missing}")
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
    sheet.close()
    doc.close()
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
        labels = [r["label"] for s in spec["sections"] for r in (list(s.get("rows", [])) + [r for g in s.get("groups", []) for r in g["rows"]])]
        segment(cell_texts(spec) + labels, spec.get("keep_together", []))
    except Exception as exc:          # no browser: cells fall back to ordinary CJK line breaking
        print("word segmentation skipped:", exc)
    src.write_text(build_html(spec), encoding="utf-8")
    pagination = paginate_html(src)
    src.with_suffix(".layout.json").write_text(json.dumps(pagination, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.path.insert(0, str(HERE))
    import check_document
    if check_document.main([str(src)]) != 0:
        return 1
    export_pdf(src, pdf, theme_tokens(spec["theme"])["ink2"])
    errors = check_pdf(pdf, spec.get("max_pages"))
    for e in errors:
        print("ERROR", e)
    print(pdf)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
