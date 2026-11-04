"""Contrast and white-panel audit of every component in the dark appearance (and, as a control, in the light one).

    py -X utf8 references/component-library/tools/dark_audit.py --html LIB.html [--width 1500] [--theme rose] [--mode media|class|light] [--json OUT]

For each component the page renders, every visible text node is measured against the background it really sits on (the first opaque background
walking up the ancestors, translucent layers composited, a gradient measured at each of its colour stops, a picture skipped and counted), and every
icon is measured against its background as well. Body text must reach 4.5:1; large text (24 px, or 19 px and bold), icons and placeholders 3:1.
Disabled controls are listed apart (WCAG leaves them out). A panel of a component that is larger than a line of text and lighter than 0.85
luminance in the dark appearance is reported as a white panel unless the component is on ``WHITE_OK`` (a QR code, a ticket stub, a photo frame).

``--mode media`` emulates a dark system appearance and leaves the page alone (follow-the-system); ``class`` calls ``setAppearance('dark')``; ``light`` is
the control. The numbers are the same in all three on a correct build.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Components whose white (or near white) faces are meant to stay white in the dark appearance, and why. Matched against the component id.
WHITE_OK: dict[str, str] = {}

AUDIT_JS = r"""
(opts) => {
  const out = { comps: {}, scanned: 0 };
  const WHITE_OK = opts.whiteOk || {};
  const parse = (s) => {
    s = (s || '').trim();
    let m = /^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.%]+))?\s*\)$/.exec(s);
    if (m) { let a = m[4] === undefined ? 1 : (m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])); return [+m[1], +m[2], +m[3], a]; }
    m = /^color\(srgb\s+([\d.e-]+)\s+([\d.e-]+)\s+([\d.e-]+)(?:\s*\/\s*([\d.%]+))?\s*\)$/.exec(s);
    if (m) { let a = m[4] === undefined ? 1 : (m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4])); return [+m[1] * 255, +m[2] * 255, +m[3] * 255, a]; }
    if (s === 'transparent') return [0, 0, 0, 0];
    return null;
  };
  const over = (f, b) => { const a = f[3] + b[3] * (1 - f[3]); if (a === 0) return [0, 0, 0, 0]; return [0, 1, 2].map((i) => (f[i] * f[3] + b[i] * b[3] * (1 - f[3])) / a).concat([a]); };
  const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const stopsOf = (img) => { const r = []; for (const m of img.matchAll(/rgba?\([^)]*\)|color\(srgb[^)]*\)/g)) { const c = parse(m[0]); if (c) r.push(c); } return r; };
  const PAGE = [255, 255, 255, 1];
  /* the faint text tiers (--ink6, --ink7, --off) are for inactive text and unavailable options: checked at 3:1 instead of 4.5:1 */
  const rootCs = getComputedStyle(document.getElementById('root') || document.documentElement);
  const hexOf = (n) => { const v = rootCs.getPropertyValue(n).trim(); const m = /^#([0-9a-f]{6})$/i.exec(v); return m ? [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16)) : null; };
  const FAINT = ['--ink6', '--ink7', '--off'].map(hexOf).filter(Boolean);
  const isFaint = (c) => FAINT.some((f) => f.every((v, i) => Math.abs(v - c[i]) < 1.5));

  /* candidate backgrounds behind (or, with self, under) an element: list of [r,g,b,1]; null when a picture is in the way */
  function backdrops(el, self) {
    const layers = []; let e = self ? el : el.parentElement, solid = null;
    while (e && e.nodeType === 1) {
      const cs = getComputedStyle(e), c = parse(cs.backgroundColor) || [0, 0, 0, 0], bi = cs.backgroundImage;
      if (bi && bi !== 'none') {
        if (bi.includes('url(')) return { skip: 'image' };
        const st = stopsOf(bi); layers.push({ opts: st.length ? st.concat(c[3] > 0 ? [c] : []) : [c], base: c });
        if (c[3] >= 0.999 && st.every((s) => s[3] >= 0.999)) { solid = true; break; }
      } else if (c[3] > 0) { layers.push({ opts: [c], base: c }); if (c[3] >= 0.999) { solid = true; break; } }
      e = e.parentElement;
    }
    let cands = [solid ? null : PAGE];
    if (solid) { const last = layers.pop(); cands = last.opts.map((o) => over(o, PAGE)); }
    for (let i = layers.length - 1; i >= 0; i--) { cands = cands.flatMap((b) => layers[i].opts.map((o) => over(o, b))); if (cands.length > 8) cands = cands.slice(0, 8); }
    return { list: cands.map((c) => [c[0], c[1], c[2], 1]) };
  }
  /* the paint behind an SVG <text> or icon: the topmost earlier shape of the same svg that covers its centre; else the HTML backdrop */
  function svgBackdrop(el) {
    const svg = el.ownerSVGElement || el.closest('svg'); if (!svg) return backdrops(el, true);
    const b = el.getBoundingClientRect(), cx = b.left + b.width / 2, cy = b.top + b.height / 2;
    let found = null;
    for (const s of svg.querySelectorAll('rect,circle,ellipse,path,polygon')) {
      if (s === el || (s.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) === 0) continue;
      const cs = getComputedStyle(s), f = parse(cs.fill); if (!f || f[3] < 0.5 || cs.fill === 'none') continue;
      const r = s.getBoundingClientRect(); if (cx < r.left || cx > r.right || cy < r.top || cy > r.bottom || r.width * r.height > 40000) continue;
      found = [f[0], f[1], f[2], f[3] * parseFloat(cs.fillOpacity || 1) * parseFloat(cs.opacity || 1)];
    }
    const base = backdrops(svg, true);
    if (!found || base.skip) return base;
    return { list: base.list.map((bg) => over(found, bg)).map((c) => [c[0], c[1], c[2], 1]) };
  }
  const opacityOf = (el, stop) => { let o = 1, e = el; while (e && e !== stop && e.nodeType === 1) { o *= parseFloat(getComputedStyle(e).opacity); e = e.parentElement; } return o; };
  const disabledOf = (el) => !!el.closest('[disabled],[aria-disabled=true],.dis,.disabled,.is-disabled,.off,.ds,.idle');
  const shown = (el) => el.checkVisibility ? el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }) : true;

  const roots = [...document.querySelectorAll('#content .ixr[data-id]')];
  for (const root of roots) {
    const id = root.dataset.id, rec = { text: 0, icons: 0, fails: [], disabled: [], skipped: { image: 0, cliptext: 0 }, white: [], placeholders: 0 };
    out.comps[id] = rec; out.scanned++;
    const judge = (kind, label, fg, bgInfo, min, el, size) => {
      if (bgInfo.skip) { rec.skipped[bgInfo.skip] = (rec.skipped[bgInfo.skip] || 0) + 1; return; }
      if (fg[3] < 0.05) return;
      if (kind === 'text' && min > 3 && isFaint(fg)) min = 3; /* a label that is transparent on purpose (a loading button shows its spinner instead) */
      let worst = 99, wbg = null;
      for (const bg of bgInfo.list) { const f = over(fg, bg); const r = ratio(f, bg); if (r < worst) { worst = r; wbg = bg; } }
      if (worst + 1e-6 >= min) return;
      const item = { kind, label: label.slice(0, 40), ratio: Math.round(worst * 100) / 100, min, fg: fg.slice(0, 3).map(Math.round).join(','), bg: wbg.slice(0, 3).map(Math.round).join(','), size, cls: (el.getAttribute('class') || '').slice(0, 40) };
      (disabledOf(el) || fg[3] <= 0.65 ? rec.disabled : rec.fails).push(item); /* a dimmed element (opacity 0.65 or less) is an inactive look, like a disabled control */
    };
    /* text */
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      const t = n.nodeValue.replace(/\s+/g, ' ').trim(); if (!t) continue;
      const el = n.parentElement; if (!el || el.closest('script,style,noscript')) continue;
      if (!shown(el)) continue;
      const rg = document.createRange(); rg.selectNodeContents(n); const r = rg.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue;
      const cs = getComputedStyle(el), inSvg = !!el.closest('svg');
      if ((cs.webkitBackgroundClip || cs.backgroundClip) === 'text') { rec.skipped.cliptext++; continue; }
      let fgc = parse(inSvg ? cs.fill : cs.color);
      const halo = inSvg && /^stroke/.test(cs.paintOrder || '') && cs.stroke !== 'none' ? parse(cs.stroke) : null; /* a text with a halo is read against its halo */ if (!inSvg) { const tf = parse(cs.webkitTextFillColor); if (tf && tf[3] > 0) fgc = tf; }
      if (!fgc) continue;
      const op = opacityOf(el, root.parentElement); fgc = [fgc[0], fgc[1], fgc[2], fgc[3] * op];
      const size = parseFloat(cs.fontSize), w = parseInt(cs.fontWeight, 10);
      const large = size >= 24 || (size >= 18.66 && w >= 600);
      rec.text++;
      judge('text', t, fgc, halo ? { list: [[halo[0], halo[1], halo[2], 1]] } : inSvg ? svgBackdrop(el) : backdrops(el, true), large ? 3 : 4.5, el, size);
    }
    /* inputs: the typed value and the placeholder */
    for (const el of root.querySelectorAll('input,textarea,select')) {
      if (!shown(el) || ['checkbox', 'radio', 'range', 'hidden', 'file', 'color'].includes(el.type)) continue;
      const cs = getComputedStyle(el), bgi = backdrops(el, true);
      if (el.value) { const fg = parse(cs.color); if (fg) { rec.text++; judge('value', el.value, fg, bgi, 4.5, el, parseFloat(cs.fontSize)); } }
      if (el.placeholder) { const ph = parse(getComputedStyle(el, '::placeholder').color); if (ph) { rec.placeholders++; judge('placeholder', el.placeholder, ph, bgi, 3, el, parseFloat(cs.fontSize)); } }
    }
    /* icons: 24-unit line icons and small svgs */
    for (const svg of root.querySelectorAll('svg')) {
      if (!shown(svg) || svg.closest('defs')) continue;
      const b = svg.getBoundingClientRect(); if (b.width < 6 || b.width > 64) continue;
      const vb = svg.getAttribute('viewBox') || ''; if (!/^0 0 24 24$/.test(vb)) continue;
      const cs = getComputedStyle(svg), paint = parse(cs.stroke.startsWith('none') ? cs.fill : cs.stroke) || parse(cs.color); if (!paint || paint[3] === 0) continue;
      rec.icons++;
      judge('icon', svg.parentElement ? (svg.parentElement.className || 'icon').toString() : 'icon', [paint[0], paint[1], paint[2], paint[3] * opacityOf(svg, root.parentElement)], backdrops(svg, false), 3, svg, 24);
    }
    /* white panels */
    if (!opts.light && !WHITE_OK[id]) {
      for (const el of root.querySelectorAll('*')) {
        if (el instanceof SVGElement || el.tagName === 'IMG' || el.tagName === 'CANVAS') continue;
        const b = el.getBoundingClientRect(); if (b.width * b.height < 2400 || b.width < 36 || b.height < 20 || !shown(el)) continue;
        const cs = getComputedStyle(el), c = parse(cs.backgroundColor), bi = cs.backgroundImage;
        if (bi && bi.includes('url(')) continue;
        let cand = [];
        if (bi && bi !== 'none') { const st = stopsOf(bi); if (st.length && st.every((s) => s[3] > 0.9)) cand = st; }
        else if (c && c[3] > 0.9) cand = [c];
        if (cand.length && cand.every((s) => lum(s) > 0.85)) rec.white.push({ cls: (el.getAttribute('class') || el.tagName).slice(0, 40), w: Math.round(b.width), h: Math.round(b.height), bg: cs.backgroundColor.slice(0, 40) });
      }
    }
  }
  return out;
}
"""

SEED_AND_FREEZE = r"""
(() => {
  let s = 20260304; Math.random = () => { s = (s * 1664525 + 1013904223) % 4294967296; return s / 4294967296; };
  window.__resetSeed = () => { s = 20260304; };
  window.setInterval = () => 0;
  const FIXED = Date.UTC(2026, 10, 4, 10, 30, 0), RealDate = Date;
  window.Date = class extends RealDate { constructor(...a) { if (a.length) super(...a); else super(FIXED); } static now() { return FIXED; } };
  document.addEventListener('DOMContentLoaded', () => { const st = document.createElement('style'); st.textContent = '*,*::before,*::after{animation:none!important;transition:none!important}'; document.head.appendChild(st); });
})();
"""


def audit(browser, html: Path, width: int = 1500, theme: str = "rose", mode: str = "media", categories: list[tuple[str, str]] | None = None,
          icon: str = "3d") -> dict:
    """Audit the given (dom, category) pairs (all when None). Returns {"comps": {id: record}, "errors": [...], "scanned": n}."""
    scheme = "light" if mode == "light" else "dark"
    ctx = browser.new_context(viewport={"width": width, "height": 900}, locale="zh-CN", color_scheme=scheme, has_touch=width < 700)
    ctx.add_init_script(SEED_AND_FREEZE)
    page = ctx.new_page()
    errors: list[str] = []
    page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror " + str(e)[:200]))
    page.goto(html.resolve().as_uri())
    page.wait_for_function("typeof BLOCKS !== 'undefined' && document.querySelectorAll('.tc, .cmbw').length > 0", timeout=20000)
    if mode == "class":
        page.evaluate("window.setAppearance('dark', false)")
    elif mode == "light":
        page.evaluate("window.setAppearance && window.setAppearance('light', false)")
    if categories is None:
        categories = page.evaluate("() => { const out = []; for (const dom of ['mp', 'ad']) for (const [c] of TABS_ALL[dom]) if (c !== 'COMBO' && inCat(dom, c).length) out.push([dom, c]); return out; }")
    result: dict = {"comps": {}, "scanned": 0}
    for dom, cat in categories:
        page.evaluate("([dom, cat, theme, icon]) => { window.__resetSeed && window.__resetSeed(); S.dom = dom; S.cat = cat; S.q = ''; S.theme = theme; S.icon = icon; renderAll(); }", [dom, cat, theme, icon])
        page.wait_for_timeout(1100 if cat in ("CHART", "DATA") else 60)
        part = page.evaluate(AUDIT_JS, {"whiteOk": WHITE_OK, "light": mode == "light"})
        result["comps"].update(part["comps"])
        result["scanned"] += part["scanned"]
    result["errors"] = errors
    ctx.close()
    return result


def summarize(res: dict) -> dict:
    comps = res["comps"]
    bad = {k: v for k, v in comps.items() if v["fails"]}
    white = {k: v for k, v in comps.items() if v["white"]}
    skipped = sum(v["skipped"].get("image", 0) + v["skipped"].get("cliptext", 0) for v in comps.values())
    return {"components": len(comps), "text": sum(v["text"] for v in comps.values()), "icons": sum(v["icons"] for v in comps.values()), "failing_components": len(bad),
            "failing_items": sum(len(v["fails"]) for v in comps.values()), "white_components": len(white), "skipped": skipped,
            "disabled_items": sum(len(v["disabled"]) for v in comps.values()), "errors": len(res.get("errors", []))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html", required=True)
    ap.add_argument("--width", type=int, default=1500)
    ap.add_argument("--theme", default="rose")
    ap.add_argument("--icon", default="3d")
    ap.add_argument("--mode", default="media", choices=["media", "class", "light"])
    ap.add_argument("--json")
    ap.add_argument("--show", type=int, default=25, help="how many failing components to print")
    args = ap.parse_args(argv)
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        res = audit(browser, Path(args.html), args.width, args.theme, args.mode, icon=args.icon)
        browser.close()
    s = summarize(res)
    print(json.dumps(s, ensure_ascii=False))
    shown = 0
    for cid, v in sorted(res["comps"].items()):
        if v["fails"] and shown < args.show:
            shown += 1
            print(cid, len(v["fails"]), "fails:", [(f["kind"], f["label"], f["ratio"], f["fg"], f["bg"]) for f in v["fails"][:3]])
    for cid, v in sorted(res["comps"].items()):
        if v["white"]:
            print("WHITE", cid, v["white"][:3])
    if res.get("errors"):
        print("console errors:", res["errors"][:5])
    if args.json:
        Path(args.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
