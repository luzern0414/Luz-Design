"""Read the rule card first: py -X utf8 scripts/context.py showcase

Build a showcase document (proposal, architecture atlas, feature list, manual) from a spec: a responsive display page (HTML) and
a paged PDF. Both come from the same source; the PDF is packed so that sections share pages and no page is left mostly empty.

    py -X utf8 scripts/make_showcase.py spec.json out.pdf [--html out.html] [--min-fill 0.8]

spec.json
{
  "title": "企业团餐报餐系统建设方案",          # the only h1; an icon block sits in front of it
  "icon": "utensils",                            # icons: showcase_icons.ICONS (one set for every document)
  "style": "formal",                             # formal: text and tables only: no icons before titles, numbered chapters, no stat tiles / cover scene / card icons
  "show_title": false,                           # atlas: no page header and no heading; the first page starts with chapter one (the title stays in the file name and the PDF properties)
  "toc": true,                                   # contents under the title, page numbers filled in after packing (proposals; not for architecture books)
  "theme": "cantonese-cafe",                     # required, chosen for this document's subject
  "orientation": "portrait" | "landscape",
  "hero": {"stats": [...], "scene": [...]} (rich only) | {"info": [["项目名称", "…"], ["版本", "V1.0"]]} (document facts, two pairs per row)
  "sections": [{"title": "项目背景", "icon": "flag", "lead": "一句话结论（可选）", "blocks": [ ... ]}]
}

blocks (type): text{text} · bullets{items} · stats{items[{value,label,icon}]} · cards{cols,items[{icon,title,text,tag}]} ·
steps{cols,items[{title,text}]} · callout{text} · scope{in{title,items},out{title,items}} · checks{cols,items} ·
sub{text} (小标题) · table{columns,rows,widths?,caption?} · matrix{columns,rows} · gantt{total,unit,rows[{label,start,end,note,milestone}]} ·
figure{figure: arch_layers|swimlane|deployment, data, caption} · image{src,alt,caption}

Tables decide alignment per column (numbers right, values of at most 6 characters centred, anything longer left), never per cell.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import showcase  # noqa: E402

PACKER = r"""
(opts) => {
  const W = opts.w, H = opts.h;
  const doc = document.querySelector('main.doc');
  doc.style.cssText = 'max-width:none;padding:0;margin:0;width:' + W + 'px';
  const probe = document.createElement('div');
  probe.style.cssText = 'position:absolute;left:-99999px;top:0;width:' + W + 'px';
  document.body.appendChild(probe);
  const wrapU = el => { const u = document.createElement('div'); u.className = 'u'; if (el.classList.contains('sh') || el.classList.contains('sub')) u.dataset.k = 'head'; else if (el.classList.contains('lead')) u.dataset.k = 'lead'; u.appendChild(el); return u; };
  const height = el => { const u = wrapU(el.cloneNode(true)); probe.appendChild(u); const h = u.getBoundingClientRect().height; probe.removeChild(u); return h; };

  // ---- splittable blocks: tables by rows, gantt by rows, card/step/check grids by rows of items
  const parts = el => {
    const kind = el.dataset.split;
    if (kind === 'rows') return { items: [...el.querySelectorAll('tbody > tr')], per: 1, min: 2, holder: c => c.querySelector('tbody') };
    if (kind === 'gantt') return { items: [...el.querySelectorAll('.g-row')], per: 1, min: 2, holder: c => c.querySelector('.gantt'), keep: '.g-head' };
    if (kind === 'grid') {
      const grid = el.querySelector('.cards,.steps,.checks');
      const n = parseInt(grid.style.getPropertyValue('--n')) || 1;
      return { items: [...grid.children], per: n, min: n, holder: c => c.querySelector('.cards,.steps,.checks') };
    }
    return null;
  };
  const pieceWith = (el, from, to, withCap) => {
    const c = el.cloneNode(true);
    const p = parts(el), pc = parts(c);
    const holder = p.holder(c);
    pc.items.forEach((n, i) => { if (i < from || i >= to) n.remove(); });
    const cap = c.querySelector('.cap'); if (cap && !withCap) cap.remove();
    const tcap = c.querySelector('.tcap');                      // a table's title comes back on every page: 表 N　标题（续）
    if (tcap && from > 0 && !tcap.textContent.endsWith('（续）')) tcap.textContent += '（续）';
    return c;
  };
  const units = [];
  const hero = doc.querySelector('.hero');
  if (hero) for (const c of [...hero.children]) units.push({ el: c, sec: 'hero', head: false, solo: c.dataset.solo === '1' });
  for (const sec of doc.querySelectorAll(':scope > section')) {
    for (const c of [...sec.children]) units.push({ el: c, sec: sec.id, brk: c.classList.contains('brk'), head: c.classList.contains('sh') || c.classList.contains('sub'), lead: c.classList.contains('lead'),
      split: !!c.dataset.split, scale: c.dataset.scale === '1' });
  }
  for (const u of units) u.h = height(u.el);
  const pages = []; let cur = null;
  const newPage = () => { const el = document.createElement('div'); el.className = 'page'; cur = { el, used: 0 }; pages.push(cur); };
  const put = (u, h) => { cur.el.appendChild(wrapU(u.el)); cur.used += (h === undefined ? u.h : h); };
  const rest = () => H - cur.used;
  const notes = [];
  const minNext = (q, i) => {
    let need = 0, k = i;
    while (k < q.length && (q[k].head || q[k].lead)) { need += q[k].h; k++; }
    if (k < q.length) {
      const n = q[k];
      if (n.split) { const p = parts(n.el); need += Math.min(n.h, height(pieceWith(n.el, 0, Math.min(p.items.length, p.min), false))); }
      else if (n.scale) {          // a figure may shrink to 88% (see below); it needs its caption and 30 px of air as well
        const media = n.el.querySelector('svg,img'), capH = n.el.querySelector('.cap') ? 30 : 0;
        const natural = media ? (media.getBoundingClientRect().height || n.h - capH) : n.h;
        need += Math.min(n.h, natural * 0.88 + capH + 30);
      } else need += n.h;
    }
    return need;
  };
  newPage();
  const q = units.slice();
  let guard = 0;
  while (q.length && guard++ < 8000) {
    const u = q[0];
    if (u.solo) { if (cur.used > 0) { newPage(); } put(u, H); q.shift(); continue; }   // cover and contents: a page of their own
    if (u.brk && cur.used > 0) { newPage(); continue; }                                  // chapter_breaks: every chapter starts a page
    if (u.head && cur.used > 0 && minNext(q, 0) > rest()) { newPage(); continue; }
    if (u.h <= rest()) { put(u); q.shift(); continue; }
    if (u.split) {
      const p = parts(u.el), total = p.items.length;
      let best = 0;
      for (let n = p.min; n <= total; n += p.per) { if (height(pieceWith(u.el, 0, n, n >= total)) <= rest()) best = n; else break; }
      while (best > p.min && u.el.dataset.split === 'rows' && p.items[best - 1].classList.contains('grp')) best--;   // never end a page on a group band
      if (best >= p.min && best < total) {
        if (total - best < Math.min(p.min, total) && best - p.per >= p.min) best -= p.per;   // never leave a one-row tail
        const first = pieceWith(u.el, 0, best, false);
        put({ el: first }, height(first));
        const tail = pieceWith(u.el, best, total, true);
        q[0] = { ...u, el: tail, h: height(tail) };
        newPage(); continue;
      }
    }
    let pulled = -1;
    for (let j = 1; j < Math.min(q.length, 6); j++) {
      if (u.scale || q[j].sec !== u.sec || q[j].head) break;     // a figure is never overtaken: its caption and legend follow it
      if (q[j].h <= rest() && !q[j].lead) { pulled = j; break; }
    }
    if (pulled > 0 && !u.head) { const [m] = q.splice(pulled, 1); put(m); notes.push('moved up'); continue; }
    if (u.scale && rest() > H * 0.3) {
      const media = u.el.querySelector('svg,img');
      const capH = u.el.querySelector('.cap') ? 30 : 0;
      const target = rest() - capH - 30;
      const natural = media.getBoundingClientRect().height || (u.h - capH);
      if (target >= natural * 0.88) { media.style.maxHeight = target + 'px'; const h = height(u.el); if (h <= rest()) { put(u, h); q.shift(); notes.push('figure shrunk'); continue; } }
    }
    if (cur.used === 0) {
      if (u.scale) { const media = u.el.querySelector('svg,img'); media.style.maxHeight = (H - 60) + 'px'; put(u, height(u.el)); q.shift(); continue; }
      put(u); q.shift(); notes.push('block taller than a page'); continue;
    }
    newPage();
  }
  // Spread a page's slack over the gaps between blocks (never between a heading and what follows it), at most 18 px per gap.
  for (const p of pages.slice(0, -1)) {
    const kids = [...p.el.children];
    const gaps = kids.slice(0, -1).filter(k => k.dataset.k !== 'head' && k.dataset.k !== 'lead');
    const slack = H - p.used;
    if (gaps.length && slack > 0) { const extra = Math.min(18, slack / gaps.length); gaps.forEach(k => { k.style.marginBottom = extra.toFixed(1) + 'px'; }); }
  }
  // Contents: each entry shows the page its chapter heading landed on.
  const where = {};
  pages.forEach((p, i) => p.el.querySelectorAll('.sh[id]').forEach(h => { where[h.id] = i + 1; }));
  pages.forEach(p => p.el.querySelectorAll('.toc a').forEach(a => { const n = where[a.getAttribute('href').slice(1)]; if (n) a.querySelector('.tp').textContent = n; }));
  doc.replaceChildren(...pages.map(p => p.el));
  document.body.removeChild(probe);
  return { pages: pages.map((p, i) => ({ page: i + 1, used: Math.round(p.used), fill: +(p.used / H).toFixed(3) })), notes };
}
"""


def export_pdf(html_path: Path, pdf_path: Path, orientation: str, min_fill: float, footer_title: str = "", cover: bool = False,
               header: bool = True) -> tuple[list[str], list[str], dict]:
    """``footer_title`` (formal documents): the document title in the page header, the page number centred in the footer; ``header=False``
    (architecture atlas) keeps the centred page number and leaves the page top empty; with ``cover`` the first page is exported
    without either, like a Word cover page."""
    import html as _html
    from playwright.sync_api import sync_playwright

    geo = showcase.PAGE[orientation]
    face = "font-size:14px;color:#000;font-family:\'Microsoft YaHei\'"
    if footer_title:
        header = f'<div style="width:100%;padding:0 14mm;text-align:center;{face}">{_html.escape(footer_title)}</div>' if header else "<div></div>"
        footer = f'<div style="width:100%;text-align:center;{face}"><span class="pageNumber"></span></div>'
    else:
        header = "<div></div>"
        footer = ('<div style="width:100%;padding:0 14mm;text-align:right;font-size:14px;color:#555;font-family:\'Microsoft YaHei\'">'
                  '<span class="pageNumber"></span></div>')
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})  # wider than any responsive breakpoint: packing must see the print layout
        page.emulate_media(media="print")
        page.goto(html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        report = page.evaluate(PACKER, {"w": geo["w"], "h": geo["h"]})
        page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True, outline=True, tagged=True,
                 display_header_footer=True, header_template=header, footer_template=footer)
        if cover:
            bare = pdf_path.with_name(pdf_path.stem + ".cover.pdf")
            page.pdf(path=str(bare), prefer_css_page_size=True, print_background=True, outline=True, tagged=True, display_header_footer=False)
        browser.close()
    if cover:
        import fitz
        doc = fitz.open(str(pdf_path))
        toc = doc.get_toc()
        first = fitz.open(str(bare))
        doc.insert_pdf(first, from_page=0, to_page=0, start_at=0)   # the cover page without header and footer
        doc.delete_page(1)
        doc.set_toc(toc)
        merged = pdf_path.with_name(pdf_path.stem + ".merged.pdf")
        doc.save(str(merged), garbage=3, deflate=True)
        doc.close(), first.close()
        merged.replace(pdf_path)
        bare.unlink()
    errors, warnings = [], []
    pages = report["pages"]
    for item in pages[:-1]:
        if item["fill"] < min_fill:
            errors.append(f"page {item['page']} is only {item['fill']:.0%} full (minimum {min_fill:.0%}): reorder blocks or add content so sections share pages")
    if pages and pages[-1]["fill"] < 0.3 and len(pages) > 1:
        warnings.append(f"the last page is only {pages[-1]['fill']:.0%} full")
    return errors, warnings, report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--html", type=Path)
    ap.add_argument("--min-fill", type=float, default=0.75)
    ap.add_argument("--max-pages", type=int)
    args = ap.parse_args(argv)
    spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
    args.pdf.parent.mkdir(parents=True, exist_ok=True)
    html_path = args.html or args.pdf.with_suffix(".html")
    html_path.write_text(showcase.build(spec), encoding="utf-8")
    import check_document
    if check_document.main([str(html_path), "--allow", "showcase"]) != 0:
        return 1
    errors, warnings, report = export_pdf(html_path, args.pdf, spec.get("orientation", "portrait"), args.min_fill,
                                          spec["title"] if spec.get("style") in ("formal", "atlas") else "", bool(spec.get("cover")),
                                          header=spec.get("style") != "atlas")
    import make_table_pdf
    errors += make_table_pdf.check_pdf(args.pdf, args.max_pages)
    print("page fill:", ", ".join(f"{p['page']}:{p['fill']:.0%}" for p in report["pages"]))
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print(args.pdf)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
