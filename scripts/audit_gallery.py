"""Audit the App / Web component-library galleries the way a user sees them.

  py -X utf8 scripts/audit_gallery.py app|web [--cats BTN,CARD] [--width min|1440|<px>] [--ids AP-BTN-001,...] [--shots DIR] [--json FILE]
  py -X utf8 scripts/audit_gallery.py app|web --cats BTN --view [--width 1440] [--chunk 1500] [--out DIR]

Audit mode builds the same page that build_templates.components_html() builds (all parts, or only --cats), opens it in Edge through
Playwright and reports per demo: out-of-bounds elements, sibling overlaps, clipped text, wrapped buttons, text touching its box edge,
fonts under the floor (App 10, Web 12), broken images, content hugging one side, uneven vertical alignment, dead height, uneven inner
padding, one-character-per-line columns, Latin words in visible text, title attributes and inline svg. The last line of the header
counts page errors and must be 0. --width min is the narrowest the gallery gets in practice: two columns at the category column width.
View mode screenshots each category as long images (chunks of --chunk px) for eyeballing; run both widths and look at every image.

The detector only gives leads. Floating layers, photos under text and intentional clipping (marquees, carousels) are flagged on
purpose: judge them by eye, and mark real intent with data-allow-clip / data-allow-ellipsis on the element.
Needs: pip install playwright, and Microsoft Edge installed.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import build_templates as bt  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SCRATCH = Path(tempfile.gettempdir()) / "luz-design-gallery-audit"
SCRATCH.mkdir(parents=True, exist_ok=True)
KIT_URI = (REPO / "kit").as_uri() + "/"

JS = r"""
(floor) => {
  const out = [];
  const vis = e => { if (e.tagName === 'COLGROUP' || e.tagName === 'COL') return false; const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const desc = e => { let s = e.tagName.toLowerCase(); if (e.className && typeof e.className === 'string') s += '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.'); const t = (e.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 14); return s + (t ? '「' + t + '」' : ''); };
  const hasOwnText = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  document.querySelectorAll('.demo').forEach(d => {
    if (d.hidden) return;
    const id = d.dataset.cid, issues = [];
    const dr = d.getBoundingClientRect();
    const st = d.querySelector('.demo__stage'); if (!st) { out.push({ id, name: d.dataset.name, issues: ['没有舞台'] }); return; }
    const sr = st.getBoundingClientRect(), scs = getComputedStyle(st);
    const all = [...st.querySelectorAll('*')].filter(vis);
    // scroll / clip ancestors that are meant to hide overflow
    const scrollAncestor = e => { for (let p = e.parentElement; p && p !== st; p = p.parentElement) { const s = getComputedStyle(p); if (/(auto|scroll)/.test(s.overflowX)) return p; } return null; };
    const fixedLike = e => { for (let p = e; p && p !== st; p = p.parentElement) { const s = getComputedStyle(p); if (s.position === 'absolute' || s.position === 'fixed') return true; } return false; };
    // 1 out of bounds (horizontal) against the stage content box
    const padL = parseFloat(scs.paddingLeft), padR = parseFloat(scs.paddingRight);
    const maxR = sr.right, minL = sr.left;
    const seenOut = new Set();
    all.forEach(e => {
      if (scrollAncestor(e)) return;
      const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
      if (r.width < 2 || r.height < 2) return;
      if (r.right > maxR + 1.5 || r.left < minL - 1.5) {
        const p = e.parentElement; if (p && p !== st && seenOut.has(p)) return; seenOut.add(e);
        issues.push('越界 ' + desc(e) + ' 超出舞台 ' + Math.round(Math.max(r.right - maxR, minL - r.left)) + 'px');
      }
    });
    if (st.scrollWidth > st.clientWidth + 2) issues.push('舞台横向溢出 ' + (st.scrollWidth - st.clientWidth) + 'px');
    // 2 clipped text: element with hidden overflow whose content is wider/taller than its box and no ellipsis
    all.forEach(e => {
      const s = getComputedStyle(e);
      if (!hasOwnText(e) && e.children.length) return;
      if (/(hidden|clip)/.test(s.overflowX) && e.scrollWidth > e.clientWidth + 1 && s.textOverflow !== 'ellipsis' && !e.closest('[data-allow-clip]')) issues.push('文字被裁 ' + desc(e));
      if (s.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1 && !e.closest('[data-allow-ellipsis]')) issues.push('省略号截断 ' + desc(e));
      if (/(hidden|clip)/.test(s.overflowY) && e.scrollHeight > e.clientHeight + 2 && !/(auto|scroll)/.test(s.overflowY) && hasOwnText(e) && s.webkitLineClamp === 'none' && !e.closest('[data-allow-clip]')) issues.push('文字上下被裁 ' + desc(e));
    });
    // 3 sibling overlaps
    all.forEach(p => {
      const kids = [...p.children].filter(vis).filter(k => { const s = getComputedStyle(k); return s.position !== 'absolute' && s.position !== 'fixed' && s.transform === 'none' && !/-/.test(s.marginLeft + s.marginTop); });
      if (kids.length < 2 || kids.length > 14) return;
      for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) {
        const a = kids[i].getBoundingClientRect(), b = kids[j].getBoundingClientRect();
        const w = Math.min(a.right, b.right) - Math.max(a.left, b.left), h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (w > 3 && h > 3 && !kids[i].contains(kids[j]) && !kids[j].contains(kids[i])) issues.push('重叠 ' + desc(kids[i]) + ' 与 ' + desc(kids[j]) + ' ' + Math.round(w) + '×' + Math.round(h));
      }
    });
    // 4 wrapped buttons / chips / tabs
    all.forEach(e => {
      if (!e.matches('.btn,.tag,.chip,.pill,.badge,.seg__item,.tabs__item,.nav__item,.tab,.demo__name,.th,th,.row__title,.entry span,.stepper__val')) return;
      const s = getComputedStyle(e); const lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.4;
      const txt = (e.innerText || '').trim(); if (!txt) return;
      const range = document.createRange(); range.selectNodeContents(e); const lines = new Set([...range.getClientRects()].filter(r => r.width > 1).map(r => Math.round(r.top / 4))).size;
      if (lines > 1 && !e.matches('.row__title') && !e.matches('th,.th,.entry span')) issues.push('折行 ' + desc(e) + ' ' + lines + '行');
      if (e.matches('.demo__name') && lines > 1) issues.push('组件名折行');
    });
    // 5 text touching its box edge
    all.forEach(e => {
      if (!hasOwnText(e)) return;
      const s = getComputedStyle(e); const hasBox = (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent') || (parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none');
      if (!hasBox || e.matches('input,select,textarea')) return;
      const r = e.getBoundingClientRect(); const range = document.createRange(); range.selectNodeContents(e); const tr = range.getBoundingClientRect();
      if (tr.width < 2) return;
      const gl = tr.left - r.left, gr = r.right - tr.right;
      if (r.width > 24 && (gl < 3 || gr < 3) && s.textAlign !== 'center') issues.push('文字贴边 ' + desc(e) + ' 左' + Math.round(gl) + '右' + Math.round(gr));
      else if (r.width > 24 && s.textAlign === 'center' && Math.abs(gl - gr) > 8 && tr.height < parseFloat(s.lineHeight || 20) * 1.6 && !/flex/.test(s.display)) issues.push('文字未居中 ' + desc(e) + ' 左' + Math.round(gl) + '右' + Math.round(gr));
    });
    // 6 font floor
    const seenFont = new Set();
    all.forEach(e => {
      if (!hasOwnText(e)) return;
      const fs = parseFloat(getComputedStyle(e).fontSize); if (fs < floor - 0.01 && !seenFont.has(fs + desc(e))) { seenFont.add(fs + desc(e)); issues.push('字号' + fs + '低于下限 ' + desc(e)); }
    });
    // 7 broken images
    st.querySelectorAll('img').forEach(i => { if (i.getAttribute('src') && i.complete && i.naturalWidth === 0 && vis(i)) issues.push('图片失效 ' + (i.getAttribute('src') || '').slice(-40)); });
    // 8 content hugging one side / dead height
    let top = 1e9, bottom = -1e9, left = 1e9, right = -1e9;
    all.forEach(e => { if (e.children.length && !['BUTTON', 'IMG', 'INPUT', 'CANVAS', 'LABEL', 'A'].includes(e.tagName)) return; if (fixedLike(e)) return; const r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return; top = Math.min(top, r.top); bottom = Math.max(bottom, r.bottom); left = Math.min(left, r.left); right = Math.max(right, r.right); });
    let blank = 0, offc = 0, sideBlank = 0;
    if (top < bottom) {
      const innerL = sr.left + padL, innerR = sr.right - padR;
      const gl = left - innerL, gr = innerR - right; sideBlank = gl + gr; offc = gl - gr;
      blank = Math.round(sr.height - (bottom - top) - parseFloat(scs.paddingTop) - parseFloat(scs.paddingBottom));
      if (sideBlank > 40 && Math.abs(offc) > 24) issues.push('内容偏向一侧 左空' + Math.round(gl) + ' 右空' + Math.round(gr));
      if (blank > 56) issues.push('舞台留白 ' + blank + 'px');
    }
    // 9 uneven vertical alignment in short flex rows
    all.forEach(p => {
      const s = getComputedStyle(p); if (!/flex/.test(s.display) || /column/.test(s.flexDirection) || /(stretch|flex-start|flex-end|baseline|start|end)/.test(s.alignItems) && !/center/.test(s.alignItems)) { if (!(s.display.includes('flex') && s.alignItems === 'normal')) return; }
      const kids = [...p.children].filter(vis).filter(k => { const ks = getComputedStyle(k); return ks.position !== 'absolute' && ks.position !== 'fixed'; });
      if (kids.length < 2 || kids.length > 8) return;
      const cs = kids.map(k => { const r = k.getBoundingClientRect(); return r.top + r.height / 2; });
      const hs = kids.map(k => k.getBoundingClientRect().height);
      if (Math.max(...hs) > 64) return;
      if (s.flexWrap !== 'nowrap') { return; }
      const spread = Math.max(...cs) - Math.min(...cs);
      if (spread > 4.5 && s.alignItems === 'center') issues.push('垂直中心不齐 ' + desc(p) + ' 差' + spread.toFixed(1) + 'px');
    });

    // 10 one-character-per-line columns
    all.forEach(e => {
      if (!hasOwnText(e) || e.matches('input,textarea,select')) return;
      const txt = (e.innerText || '').trim().replace(/\s+/g, ''); if (txt.length < 3) return;
      const fs = parseFloat(getComputedStyle(e).fontSize);
      const range = document.createRange(); range.selectNodeContents(e);
      const tops = new Set([...range.getClientRects()].filter(r => r.width > 1).map(r => Math.round(r.top / 3)));
      const w = e.getBoundingClientRect().width;
      if (tops.size >= 3 && w < fs * 3.4 && txt.length / tops.size < 2.6) issues.push('逐字竖排 ' + desc(e) + ' 宽' + Math.round(w));
    });
    // 11 uneven inner padding of boxes (top vs bottom, left vs right)
    all.concat([st]).forEach(e => {
      const s = getComputedStyle(e);
      const boxed = e === st || (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent') || (parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none') || s.boxShadow !== 'none';
      if (!boxed || /(auto|scroll)/.test(s.overflowX + s.overflowY) && e !== st) return;
      const r = e.getBoundingClientRect(); if (r.height < 56 || r.width < 120 || r.height > 520) return;
      const kids = [...e.children].filter(vis).filter(k => { const ks = getComputedStyle(k); return ks.position !== 'absolute' && ks.position !== 'fixed' && !k.matches('.sr-only,.badge'); });
      if (!kids.length) return;
      let t = 1e9, b = -1e9, l = 1e9, rr = -1e9;
      kids.forEach(k => { const kr = k.getBoundingClientRect(); t = Math.min(t, kr.top); b = Math.max(b, kr.bottom); l = Math.min(l, kr.left); rr = Math.max(rr, kr.right); });
      const gt = t - r.top, gb = r.bottom - b, gl = l - r.left, gr = r.right - rr;
      if (e !== st && Math.abs(gt - gb) > 16 && Math.min(gt, gb) >= 0) issues.push('内距上下不等 ' + desc(e) + ' 上' + Math.round(gt) + '下' + Math.round(gb));
      if (e !== st && !e.matches('td,th,tr') && Math.abs(gl - gr) > 16 && gl >= 0 && gr >= 0 && (s.justifyContent === 'center' || s.textAlign === 'center') && !/flex-start|start|end/.test(s.justifyContent)) issues.push('内距左右不等 ' + desc(e) + ' 左' + Math.round(gl) + '右' + Math.round(gr));
    });

    // 12 hard-rule content checks: Latin words in visible text or placeholders, title attributes, inline svg
    const latin = /[A-Za-z]{2,}/;
    const walker = document.createTreeWalker(st, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) { const t = n.textContent.trim(); if (t && latin.test(t) && n.parentElement && vis(n.parentElement) && !n.parentElement.closest('script,style')) issues.push('含英文 「' + t.slice(0, 20) + '」'); }
    st.querySelectorAll('[placeholder]').forEach(i => { if (latin.test(i.getAttribute('placeholder'))) issues.push('占位含英文 ' + i.getAttribute('placeholder').slice(0, 16)); });
    st.querySelectorAll('[title]').forEach(i => issues.push('含 title 属性 ' + desc(i)));
    st.querySelectorAll('svg').forEach(i => { if (!i.closest('[data-allow-svg]')) issues.push('内联 svg'); });
    st.querySelectorAll('[aria-label]').forEach(i => { if (latin.test(i.getAttribute('aria-label'))) issues.push('可访问名含英文 ' + i.getAttribute('aria-label').slice(0, 16)); });
    out.push({ id, name: d.dataset.name, w: Math.round(dr.width), h: Math.round(dr.height), stageH: Math.round(sr.height), blank, issues: [...new Set(issues)] });
  });
  return out;
}
"""


def build_page(end: str, cats: list[str] | None) -> str:
    """The same assembly as build_templates.components_html, optionally limited to some categories."""
    cfg = bt.ENDS[end]
    shell = bt.read(bt.HERE / "components.shell.tpl")
    sections, pills, styles, scripts = [], [], [], []
    for path in sorted((bt.T / end / "source" / "parts").glob("*.part")):
        code, title, body, st, sc = bt.split_part(bt.read(path))
        if cats and code not in cats:
            continue
        ids = bt.CID.findall(body)
        col = cfg.get("cols", {}).get(code)
        style = f' style="--col: {col}px"' if col else ""
        sections.append(f'<section class="cat" id="cat-{code.lower()}" data-cat="{code}"{style}>\n<div class="cat__head"><h2>{title}</h2><span>{len(ids)} 个组件</span></div>\n<div class="gallery">\n{body}\n</div>\n</section>')
        pills.append((code, title, len(ids)))
        styles += st
        scripts += sc
    pill_html = "".join(f'<button class="pill" data-cat="{c}" aria-pressed="false">{t} <small>{n}</small></button>' for c, t, n in pills)
    out = (shell.replace("@TITLE@", "audit").replace("@END_CSS@", cfg["css"]).replace("@BODY_CLASS@", cfg["body"]).replace("@COL@", str(cfg["col"]))
           .replace("@PILLS@", pill_html).replace("@PARTS@", "\n".join(sections)).replace("@PART_STYLES@", "\n".join(styles)).replace("@PART_SCRIPTS@", "\n".join(scripts)))
    out = bt.embed_path(out).replace("../../kit/", KIT_URI)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("end", choices=["app", "web"])
    ap.add_argument("--cats", default="")
    ap.add_argument("--ids", default="")
    ap.add_argument("--width", default="min")
    ap.add_argument("--shots", default="")
    ap.add_argument("--json", default="")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--view", action="store_true", help="screenshot --cats as long images instead of auditing")
    ap.add_argument("--chunk", type=int, default=1500)
    ap.add_argument("--out", default=str(SCRATCH / "view"))
    a = ap.parse_args()
    cats = [c for c in a.cats.split(",") if c] or None
    ids = [c for c in a.ids.split(",") if c]
    html = build_page(a.end, cats)
    page_file = SCRATCH / f"_audit_{a.end}_{'-'.join(cats or ['all'])}.html"
    page_file.write_text(html, encoding="utf-8")
    floor = 10 if a.end == "app" else 12
    if a.width == "min":
        col = bt.ENDS[a.end]["col"]
        width = (2 * col + 12 + 40) if a.end == "web" else (2 * col + 12 + 40)
        if cats and len(cats) == 1 and bt.ENDS[a.end].get("cols", {}).get(cats[0]):
            c = bt.ENDS[a.end]["cols"][cats[0]]
            width = 2 * c + 12 + 40
    else:
        width = int(a.width)
    if a.view:
        if not cats:
            ap.error("--view needs --cats")
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            b = p.chromium.launch(channel="msedge")
            pg = b.new_page(viewport={"width": width, "height": 900})
            pg.goto(page_file.as_uri())
            pg.wait_for_timeout(1800)
            pg.add_style_tag(content=".bar{position:static!important}")
            for c in cats:
                box = pg.locator(f'section.cat[data-cat="{c}"]').bounding_box()
                h, n, y = int(box["height"]), 0, 0
                while y < h:
                    path = out / f"{a.end}-{c}-{width}-{n}.png"
                    pg.screenshot(path=str(path), clip={"x": 0, "y": box["y"] + y, "width": width, "height": min(a.chunk, h - y)}, full_page=True)
                    print(path)
                    n += 1
                    y += a.chunk
            b.close()
        return
    shots = Path(a.shots) if a.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge")
        pg = b.new_page(viewport={"width": width, "height": 1000})
        errs = []
        pg.on("console", lambda m: errs.append(m.text[:140]) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)[:140]))
        pg.goto(page_file.as_uri())
        pg.wait_for_timeout(1800)
        res = pg.evaluate(JS, floor)
        if ids:
            res = [r for r in res if r["id"] in ids]
        if shots:
            for r in res:
                try:
                    pg.locator(f'.demo[data-cid="{r["id"]}"]').screenshot(path=str(shots / f'{r["id"]}.png'))
                except Exception as exc:  # noqa: BLE001
                    r["issues"].append("截图失败 " + str(exc)[:60])
        b.close()
    bad = [r for r in res if r["issues"]]
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.end} width {width}px  demos {len(res)}  with issues {len(bad)}  page errors {len(errs)}")
    for e in errs[:5]:
        print("  console:", e)
    if not a.quiet:
        for r in bad:
            print(f"{r['id']} {r['name']}  ({r['w']}×{r['h']})")
            for i in r["issues"][:8]:
                print("   -", i)


if __name__ == "__main__":
    main()
