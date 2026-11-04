"""Tears a real page down into a measurable visual fingerprint and checks it against the ranges mature products keep to.

    py -X utf8 teardown.py <url | file.html> [--width 390] [--height 844] [--scheme light|dark] [--out teardown.json] [--lint] [--md report.md] [--shots dir]

Opens the page in a real browser (Microsoft Edge, or LUZ_AUDIT_CHANNEL=chromium; same launch as audit_rendered.py), waits for it to settle (load + 800 ms, one scroll through the
first screens for lazy content) and reads what is on screen, weighted by visual weight (text by characters x font size or ink area, backgrounds by the visible area that is not
covered by a child, borders by length x width), never by element count alone:

    type    font-size histogram (px), weights, line-height / size ratios, font stacks; the effective scale (sizes closer than 1 px merged), the median step ratio and the nearest
            module (1.125 / 1.2 / 1.25 / 1.333 / 1.5), body size, largest / body
    color   text, background and border colours in OKLab clusters (at most 8 chromatic + the neutrals, neutral = OKLCH C < 0.02), the primary colour, mean chroma,
            text / background contrast (WCAG 2.2, 0.04045 threshold): median and lowest
    shape   corner radii (px, 50% / 9999px as pill), share of nested rounded boxes whose inner radius is about outer radius - padding
    depth   box-shadow list (offset / blur / spread / alpha), elevation levels, single light direction
    space   gaps between siblings, container padding, flex / grid gap; base unit 4 or 8 and the values off that grid
    layout  alignment lines of text blocks (2 px tolerance), content width, characters per screen, whitespace share (screenshot scaled to 1/8), image area share, touch target sizes
    motion  transition / animation durations and timing functions in the style sheets, prefers-reduced-motion branch

``token_draft`` turns the numbers into a token draft (type scale, palette, radius, shadow, spacing) to compare against, ``--lint`` adds the check (it only reports: the exit code stays 0),
``--md`` writes a one-screen Chinese summary, ``--shots`` saves the first screen and the full page as PNG. The page is only opened, nothing is fetched, logged in to or paged through.
Pillow is used for the 1/8 downsample when installed; without it the browser canvas does the same. Needs playwright.
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import math
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --------------------------------------------------------------------------------------------------------------------------------------
# Ranges of mature products. These are rule-of-thumb values from reading real product pages (not standards): tune them per product type.
# --------------------------------------------------------------------------------------------------------------------------------------
MAX_TYPE_STEPS = 7             # effective font sizes: more than 7 blurs the hierarchy
MAX_WEIGHTS = 3                # font weights in use: regular 400, semibold 600, bold 700
MAX_TEXT_COLORS = 6            # text colours (ink levels, inverse, brand, status)
MAX_RADII = 4                  # corner radius values (pill counts as one)
MAX_SHADOW_LEVELS = 4          # elevation levels, with one light direction
MAX_OFF_GRID = 0.15            # spacing values off the 4 / 8 grid
MAX_ALIGN_LINES = 6            # alignment lines carrying >= ALIGN_MIN_COVER text blocks
ALIGN_MIN_COVER = 3
WHITESPACE_RANGE = (0.25, 0.65)  # share of the page that looks like background
MIN_CONTRAST_MEDIAN = 7.0      # body text median (Luz rule: AAA for body)
MIN_CONTRAST = 4.5             # no text below AA
MAX_MEAN_CHROMA = 0.12         # OKLCH C averaged over text, background and border colours
TOUCH_PX = 44                  # touch target, phone widths (Apple HIG 44 pt; Luz audits 40, see audit_rendered.py)
POINTER_PX = 24                # pointer target, desktop widths (WCAG 2.5.8)
TOUCH_WIDTH = 700              # viewports narrower than this are touch
MAX_SMALL_TARGETS = 0.20       # share of targets under the limit

# Measuring constants.
PAGE_CAP_SCREENS = 10          # measure at most this many screens of page height
MIN_SHARE = 0.02               # a value used by less than 2% of its kind is a stray, not a design decision
MIN_STEP_SHARE = 0.005         # a font size under 0.5% of the text weight is not an effective step
COLOR_MERGE_DE = 0.015         # OKLab distance under which two colours are one cluster: side by side they are not told apart (a card #fff on #f7f8fa is 0.024, so it stays two)
MAX_CHROMATIC = 8
MAX_NEUTRAL = 8
NEUTRAL_CHROMA = 0.02          # OKLCH C under this is a neutral
PRIMARY_MIN_CHROMA = 0.05      # the primary colour is clearly chromatic
CHANNEL_WEIGHT = {"background": 0.5, "text": 0.3, "border": 0.2}
HAIRLINE_MAX = 2               # 1-2 px spacing is a hairline / half step, not a grid value
ALIGN_TOLERANCE = 2            # px
WS_SCALE = 8                   # screenshot downsample for the whitespace share
WS_DE = 0.03                   # OKLab distance from the main background that still counts as background
MODULES = (1.125, 1.2, 1.25, 1.333, 1.5)
GOTO_TIMEOUT = 45000
SETTLE_MS = 800

# --------------------------------------------------------------------------------------------------------------------------------------
# In-page collectors
# --------------------------------------------------------------------------------------------------------------------------------------
COLLECT = r"""
async (opts) => {
  try { await document.fonts.ready; } catch (e) {}
  const SKIP = new Set(['SCRIPT', 'STYLE', 'LINK', 'META', 'NOSCRIPT', 'TEMPLATE', 'HEAD', 'TITLE', 'BR', 'WBR', 'BASE', 'AREA', 'COL', 'COLGROUP', 'DATALIST', 'OPTION', 'OPTGROUP']);
  const vw = innerWidth, vh = innerHeight, sx = scrollX, sy = scrollY;
  const root = document.documentElement, body = document.body || root;
  const docH = Math.max(root.scrollHeight, body.scrollHeight);
  const pageH = Math.min(docH, opts.pageCap);
  const out = {vw, vh, docH, pageH, truncated: docH > opts.pageCap, elements: 0, texts: [], bgs: [], borders: [], boxes: [], images: [], pads: [], gaps: [], sibs: [], targets: [], shadows: {}, nested: [], page: null};
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', { willReadFrequently: true });
  /* rgb()/rgba() is read as written; oklch(), color-mix(), color(srgb …) go through a canvas pixel (same as audit_rendered.py) */
  const RGB = /^rgba?\(\s*([\d.]+)\s*[,\s]\s*([\d.]+)\s*[,\s]\s*([\d.]+)\s*(?:[,/]\s*([\d.]+)(%?))?\s*\)$/;
  const pcache = new Map();
  const parse = (c) => {
    if (!c) return null; if (pcache.has(c)) return pcache.get(c);
    let v; const m = RGB.exec(c.trim());
    if (m) v = [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : (m[5] ? +m[4] / 100 : +m[4])];
    else if (c === 'transparent') v = [0, 0, 0, 0];
    else { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; v = [d[0], d[1], d[2], d[3] / 255]; }
    pcache.set(c, v); return v;
  };
  const q1 = (n) => Math.round(n * 10) / 10;
  const csMemo = new WeakMap(), rectMemo = new WeakMap();
  const styleOf = (el) => { let s = csMemo.get(el); if (!s) { s = getComputedStyle(el); csMemo.set(el, s); } return s; };
  const rectOf = (el) => { let r = rectMemo.get(el); if (!r) { const b = el.getBoundingClientRect(); r = {l: b.left + sx, t: b.top + sy, r: b.right + sx, b: b.bottom + sy, w: b.width, h: b.height}; rectMemo.set(el, r); } return r; };
  const inter = (a, b) => ({l: Math.max(a.l, b.l), t: Math.max(a.t, b.t), r: Math.min(a.r, b.r), b: Math.min(a.b, b.b)});
  const empty = (a) => a.r <= a.l || a.b <= a.t;
  const full = {l: 0, t: 0, r: vw, b: pageH};
  /* what an element can show: the page, cut by every ancestor that clips (overflow), except under position:fixed */
  const ccMemo = new WeakMap();
  const clipFor = (el) => { if (styleOf(el).position === 'fixed') return full; const p = el.parentElement; return p ? childClip(p) : full; };
  const childClip = (p) => {
    let c = ccMemo.get(p); if (c) return c;
    c = clipFor(p);
    if (p !== body && p !== root) { const s = styleOf(p); if (s.overflowX !== 'visible' || s.overflowY !== 'visible') { const r = rectOf(p); c = inter(c, {l: r.l, t: r.t, r: r.r, b: r.b}); } }
    ccMemo.set(p, c); return c;
  };
  const opMemo = new WeakMap();
  const opacityOf = (el) => { if (!el) return 1; let o = opMemo.get(el); if (o === undefined) { const v = parseFloat(styleOf(el).opacity); o = opacityOf(el.parentElement) * (isNaN(v) ? 1 : v); opMemo.set(el, o); } return o; };
  /* the canvas under a transparent chain: white, or the dark canvas when the page declares color-scheme dark */
  const declared = getComputedStyle(root).colorScheme || 'normal';
  const darkCanvas = /dark/.test(declared) && (!/light/.test(declared) || matchMedia('(prefers-color-scheme: dark)').matches);
  const CANVAS = darkCanvas ? [18, 18, 18] : [255, 255, 255];
  const blend = (t, b) => [t[0] * t[3] + b[0] * (1 - t[3]), t[1] * t[3] + b[1] * (1 - t[3]), t[2] * t[3] + b[2] * (1 - t[3])];
  const effMemo = new WeakMap(), unkMemo = new WeakMap();
  const effOf = (el) => { if (!el) return CANVAS; let v = effMemo.get(el); if (v) return v; const own = parse(styleOf(el).backgroundColor); const up = effOf(el.parentElement); v = own && own[3] > 0 ? blend(own, up) : up; effMemo.set(el, v); return v; };
  /* true when an image or gradient may sit between the text and the colour found: the contrast is then not known */
  const unkOf = (el) => { if (!el) return false; let v = unkMemo.get(el); if (v !== undefined) return v; const s = styleOf(el); if (s.backgroundImage && s.backgroundImage !== 'none') v = true; else { const own = parse(s.backgroundColor); v = own && own[3] >= 0.99 ? false : unkOf(el.parentElement); } unkMemo.set(el, v); return v; };
  const splitTop = (v) => { const parts = []; let depth = 0, cur = ''; for (const ch of v) { if (ch === '(') depth++; if (ch === ')') depth--; if (ch === ',' && depth === 0) { parts.push(cur.trim()); cur = ''; } else cur += ch; } if (cur.trim()) parts.push(cur.trim()); return parts; };
  const shadowDef = (str) => {
    if (out.shadows[str]) return;
    out.shadows[str] = splitTop(str).map((t) => {
      const nums = (t.match(/-?\d*\.?\d+(?:e-?\d+)?px/g) || []).map(parseFloat);
      const col = parse(t.replace(/-?\d*\.?\d+(?:e-?\d+)?px/g, '').replace(/\binset\b/, '').trim()) || [0, 0, 0, 1];
      return {x: nums[0] || 0, y: nums[1] || 0, blur: nums[2] || 0, spread: nums[3] || 0, inset: /\binset\b/.test(t), rgb: [col[0], col[1], col[2]], a: col[3]};
    });
  };
  /* corner radius: the largest corner, in px; a corner as round as half the short side is a pill (50%, 9999px, 20px on a 40px button) */
  const radiusOf = (cs, w, h) => {
    let best = 0;
    for (const p of ['borderTopLeftRadius', 'borderTopRightRadius', 'borderBottomRightRadius', 'borderBottomLeftRadius']) {
      const parts = (cs[p] || '0px').split(/\s+/);
      const res = parts.map((v, i) => v.endsWith('%') ? parseFloat(v) / 100 * (i === 0 ? w : h) : parseFloat(v) || 0);
      best = Math.max(best, Math.min(res[0], res.length > 1 ? res[1] : res[0]));
    }
    const half = Math.min(w, h) / 2;
    return {r: best, pill: best > 0 && half >= 3 && best >= half - 0.5};
  };
  const TARGET = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [role=menuitem], [role=switch], [role=checkbox], [role=radio], [onclick]';
  const rootRec = {c: effOf(body), g: null, e: null, a: vw * pageH, cov: 0};
  const bgList = [rootRec], bgRec = new Map(), boxRec = new Map(), targetSet = new Set();
  const nearestBg = (el) => { for (let n = el.parentElement; n && n !== body && n !== root; n = n.parentElement) { const r = bgRec.get(n); if (r) return r; } return rootRec; };
  const nearestBox = (el) => { for (let n = el.parentElement; n && n !== body && n !== root; n = n.parentElement) { const r = boxRec.get(n); if (r) return r; } return null; };
  const shown = (el) => { const r = rectOf(el); if (r.w < 0.5 || r.h < 0.5) return null; const s = styleOf(el); if (s.visibility !== 'visible' || opacityOf(el) < 0.02) return null; const i = inter(r, clipFor(el)); return empty(i) ? null : i; };
  const siblingGaps = (el, cs) => {
    const kids = [];
    for (const k of el.children) {
      if (SKIP.has(k.tagName)) continue; if (k instanceof SVGElement && k.tagName.toLowerCase() !== 'svg') continue;
      const ks = styleOf(k); if (ks.display === 'none' || ks.display === 'contents' || ks.position === 'absolute' || ks.position === 'fixed') continue;
      if (!shown(k)) continue; kids.push([k, rectOf(k), ks]);
    }
    const flex = /flex|grid/.test(cs.display);
    if (flex && /^space-/.test(cs.justifyContent)) return;      /* the space between is left over room, not a chosen value */
    for (let i = 1; i < kids.length; i++) {
      const [, a, as] = kids[i - 1], [, b, bs] = kids[i];
      if (!flex && (/^inline/.test(as.display) || /^inline/.test(bs.display))) continue;   /* inline boxes are separated by the font's space, not by a design value */
      const ox = Math.min(a.r, b.r) - Math.max(a.l, b.l), oy = Math.min(a.b, b.b) - Math.max(a.t, b.t);
      let g = -1;
      if (oy > 0.5 * Math.min(a.h, b.h) && ox <= 0) g = b.l >= a.r ? b.l - a.r : a.l - b.r;          /* side by side: a horizontal gap */
      else if (ox > 0.5 * Math.min(a.w, b.w) && oy <= 0) g = b.t >= a.b ? b.t - a.b : a.t - b.b;     /* stacked: a vertical gap; neighbours in another row and column of a grid are skipped */
      if (g >= 0.5 && g <= 400) out.sibs.push(Math.round(g));
    }
  };

  for (const el of body.querySelectorAll('*')) {
    if (SKIP.has(el.tagName)) continue;
    if (el instanceof SVGElement && el.tagName.toLowerCase() !== 'svg') continue;
    out.elements++;
    const cs = styleOf(el);
    if (cs.display === 'none' || cs.display === 'contents') continue;
    const ix = shown(el); if (!ix) continue;
    const r = rectOf(el), area = (ix.r - ix.l) * (ix.b - ix.t), tag = el.tagName.toLowerCase();
    const bg = parse(cs.backgroundColor), bgi = cs.backgroundImage, hasImg = bgi && bgi !== 'none';
    const isGrad = hasImg && /gradient\(/.test(bgi) && !/url\(/.test(bgi), isUrl = hasImg && /url\(/.test(bgi);
    const hasBg = !!(bg && bg[3] > 0.01) && !isUrl;
    const media = ['img', 'video', 'canvas', 'iframe', 'embed', 'object'].includes(tag), svgBig = tag === 'svg' && Math.min(r.w, r.h) >= 48;
    if (media || svgBig || isUrl) { out.images.push({k: media ? tag : (isUrl ? 'bg' : 'svg'), a: Math.round(area)}); nearestBg(el).cov += area; }
    else if (tag === 'svg') out.images.push({k: 'icon', a: Math.round(area)});
    /* background colour: the colour that shows, counted on the area no child covers */
    if (hasBg || isGrad) {
      nearestBg(el).cov += area;
      const rec = isGrad ? {c: null, g: (bgi.match(/rgba?\([^)]*\)/g) || []).map(parse).filter(Boolean), e: effOf(el.parentElement), a: area, cov: 0} : {c: effOf(el), g: null, e: null, a: area, cov: 0};
      bgRec.set(el, rec); bgList.push(rec);
    }
    /* border colour: length x width of the visible sides */
    const sides = ['Top', 'Right', 'Bottom', 'Left'].map((s) => ({w: parseFloat(cs['border' + s + 'Width']) || 0, st: cs['border' + s + 'Style'], c: cs['border' + s + 'Color']}));
    const bd = sides.filter((s) => s.w > 0 && s.st !== 'none' && s.st !== 'hidden');
    const bcol = bd.length ? parse(bd.reduce((a, b) => b.w > a.w ? b : a).c) : null;
    const hasBorder = !!(bcol && bcol[3] > 0.05);
    if (hasBorder) out.borders.push({c: bcol, e: effOf(el), w: Math.round(sides.reduce((n, s, i) => n + (s.w > 0 && s.st !== 'none' && s.st !== 'hidden' ? s.w * (i % 2 ? r.h : r.w) : 0), 0))});
    /* boxes: shape and depth */
    const sh = cs.boxShadow && cs.boxShadow !== 'none' ? cs.boxShadow : null;
    if ((hasBg || isGrad || hasBorder || sh || media || svgBig || isUrl) && Math.min(r.w, r.h) >= 4) {
      const rad = radiusOf(cs, r.w, r.h), pb = nearestBox(el);
      if (rad.r > 0 && !rad.pill && pb && pb.r > 0 && !pb.pill) {
        const gap = Math.min(r.l - pb.x, r.t - pb.y, pb.x + pb.w - r.r, pb.y + pb.h - r.b);
        if (gap >= 0 && gap < pb.r) out.nested.push({r: Math.round(rad.r), pr: Math.round(pb.r), g: q1(gap)});
      }
      boxRec.set(el, {x: r.l, y: r.t, w: r.w, h: r.h, r: rad.r, pill: rad.pill});
      out.boxes.push({a: Math.round(area), r: Math.round(rad.r), p: rad.pill ? 1 : 0, sh});
      if (sh) shadowDef(sh);
    }
    /* touch / click targets: the outermost clickable element; a link inside a sentence is exempt (WCAG 2.5.8) */
    if (cs.pointerEvents !== 'none' && !el.disabled && el.getAttribute('aria-disabled') !== 'true' && (el.matches(TARGET) || cs.cursor === 'pointer')) {
      let nested = false; for (let n = el.parentElement; n; n = n.parentElement) if (targetSet.has(n)) { nested = true; break; }
      if (!nested) {
        targetSet.add(el);
        const own = (el.textContent || '').trim().length, par = el.parentElement ? (el.parentElement.textContent || '').trim().length : own;
        if (!(cs.display === 'inline' && par > own + 4)) out.targets.push([Math.round(r.w), Math.round(r.h)]);
      }
    }
    /* spacing */
    if (cs.display !== 'inline') {
      for (const s of ['Top', 'Right', 'Bottom', 'Left']) { const p = parseFloat(cs['padding' + s]); if (p >= 0.5) out.pads.push(Math.round(p)); }
      if (/flex|grid/.test(cs.display)) { const rg = parseFloat(cs.rowGap), cg = parseFloat(cs.columnGap); if (rg >= 0.5) out.gaps.push(Math.round(rg)); if (cg >= 0.5 && cg !== rg) out.gaps.push(Math.round(cg)); }
      if (el.children.length >= 2) siblingGaps(el, cs);
    }
  }
  for (const rec of bgList) out.bgs.push({c: rec.c, g: rec.g, e: rec.e, a: Math.max(0, Math.round(rec.a - rec.cov))});

  /* text: one record per text node, the first node of each block also gives the alignment line */
  const blkSeen = new Set(), range = document.createRange(), tw = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
  for (let t; (t = tw.nextNode());) {
    const raw = t.nodeValue, chars = raw.replace(/\s+/g, '').length; if (!chars) continue;
    const el = t.parentElement; if (!el || SKIP.has(el.tagName)) continue;
    const cs = styleOf(el); if (cs.display === 'none' || cs.visibility !== 'visible') continue;
    const op = opacityOf(el); if (op < 0.02) continue;
    range.selectNodeContents(t);
    const rs = [...range.getClientRects()].filter((q) => q.width >= 0.5 && q.height >= 0.5); if (!rs.length) continue;
    let l = Infinity, tp = Infinity, rr = -Infinity, bb = -Infinity, ar = 0;
    for (const q of rs) { l = Math.min(l, q.left); tp = Math.min(tp, q.top); rr = Math.max(rr, q.right); bb = Math.max(bb, q.bottom); ar += q.width * q.height; }
    l += sx; rr += sx; tp += sy; bb += sy;
    const ix = inter({l, t: tp, r: rr, b: bb}, clipFor(el)); if (empty(ix)) continue;
    const frac = ((ix.r - ix.l) * (ix.b - ix.t)) / ((rr - l) * (bb - tp));
    let col = parse(cs.webkitTextFillColor || cs.color); if (col) col = [col[0], col[1], col[2], col[3] * op]; if (!col || col[3] < 0.05) col = null;
    let b = el; while (b && b !== body && b !== root) { const d = styleOf(b).display; if (d !== 'inline' && d !== 'contents') break; b = b.parentElement; }
    const first = !blkSeen.has(b); blkSeen.add(b);
    const ta = styleOf(b || el).textAlign, al = ta === 'center' ? 'c' : (ta === 'right' || ta === 'end') ? 'r' : 'l';
    const ax = al === 'c' ? (l + rr) / 2 : (al === 'r' ? rs[rs.length - 1].right + sx : rs[0].left + sx);
    out.texts.push({fs: parseFloat(cs.fontSize), fw: parseInt(cs.fontWeight, 10) || 400, lh: cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight), fam: cs.fontFamily, col, bg: effOf(el), unk: unkOf(el),
      n: q1(chars * frac), a: Math.round(ar * frac), l: q1(l), t: q1(tp), r: q1(rr), b: q1(bb), ax: q1(ax), al, first, dis: !!el.closest('[disabled],[aria-disabled="true"]'), s: raw.trim().slice(0, 14)});
  }
  out.page = {color: effOf(body), canvas: CANVAS, title: document.title, lang: root.lang || '', colorScheme: declared, prefersDark: matchMedia('(prefers-color-scheme: dark)').matches};
  return out;
}
"""

PREPARE = r"""
async () => {
  /* content-visibility:auto leaves off-screen blocks empty (and their height a guess) until they are scrolled to: draw them all before anything is measured */
  const lock = document.createElement('style'); lock.textContent = '*,*::before,*::after{content-visibility:visible!important}'; document.head.appendChild(lock);
  await new Promise((done) => { requestAnimationFrame(() => requestAnimationFrame(done)); setTimeout(done, 150); });
}
"""

EXPAND = r"""
() => {
  /* A mini-program or app shell scrolls inside one container while the page itself is one screen high. Measure the whole content instead of the first screen:
     the largest inner scroller (at least 80% of the width, 40% of the height) and every ancestor are let grow to their content. */
  const vw = innerWidth, vh = innerHeight; let best = null, bestArea = 0;
  for (const el of document.body.querySelectorAll('*')) {
    const s = getComputedStyle(el); if (!/(auto|scroll|overlay)/.test(s.overflowY)) continue;
    const r = el.getBoundingClientRect(); if (r.width < vw * 0.8 || r.height < vh * 0.4 || el.scrollHeight <= el.clientHeight + 16) continue;
    if (r.width * r.height > bestArea) { best = el; bestArea = r.width * r.height; }
  }
  if (!best) return null;
  const info = {tag: best.tagName.toLowerCase(), cls: typeof best.className === 'string' ? best.className.trim().split(/\s+/).slice(0, 2).join('.') : '', scrollHeight: best.scrollHeight, clientHeight: best.clientHeight};
  const delta = best.scrollHeight - best.clientHeight;
  /* the scroller shows all its content; every ancestor grows by the same amount, so a header stays on top and a bottom bar moves to the bottom of the long page */
  const rects = []; for (let n = best; n; n = n.parentElement) rects.push([n, n.getBoundingClientRect(), getComputedStyle(n).position]);
  for (const [n, r, pos] of rects) {
    const st = n.style;
    st.setProperty('height', (n === best ? best.scrollHeight : r.height + delta) + 'px', 'important'); st.setProperty('max-height', 'none', 'important');
    st.setProperty('overflow', 'visible', 'important'); st.setProperty('contain', 'none', 'important');   /* contain: layout would keep the overflow out of the page height */
    if (n === best) st.setProperty('flex', '0 0 auto', 'important');
    if (pos === 'fixed') { st.setProperty('position', 'absolute', 'important'); st.setProperty('top', (r.top + scrollY) + 'px', 'important'); st.setProperty('left', (r.left + scrollX) + 'px', 'important'); }
  }
  return info;
}
"""

MOTION = r"""
(extra) => {
  const out = {td: [], tf: [], ad: [], af: [], tp: [], reduced: false, unreadable: [], rules: 0, keyframes: 0, sheets: document.styleSheets.length, running: 0};
  const visit = (rule) => {
    out.rules++;
    if (rule instanceof CSSKeyframesRule) { out.keyframes++; return; }
    if (rule.style && rule.selectorText !== undefined) {
      const s = rule.style;
      if (s.transitionDuration) { out.td.push(s.transitionDuration); out.tf.push(s.transitionTimingFunction || ''); out.tp.push(s.transitionProperty || ''); }
      if (s.animationDuration) { out.ad.push(s.animationDuration); out.af.push(s.animationTimingFunction || ''); }
    }
    if (rule.media && /prefers-reduced-motion/.test(rule.media.mediaText || '')) out.reduced = true;
    if (rule.conditionText && /prefers-reduced-motion/.test(rule.conditionText)) out.reduced = true;
    if (rule.cssRules) for (const r of rule.cssRules) visit(r);
    if (rule.styleSheet) { try { for (const r of rule.styleSheet.cssRules) visit(r); } catch (e) {} }
  };
  const sheets = [...document.styleSheets, ...(document.adoptedStyleSheets || [])];
  for (const sh of sheets) { let rules; try { rules = sh.cssRules; } catch (e) { out.unreadable.push(sh.href || '(inline)'); continue; } for (const r of rules) visit(r); }
  for (const text of extra || []) { try { const sh = new CSSStyleSheet(); sh.replaceSync(text); for (const r of sh.cssRules) visit(r); } catch (e) {} }
  /* style="transition: …" on an element is a declaration too */
  for (const el of (extra && extra.length ? [] : document.querySelectorAll('[style*="transition"], [style*="animation"]'))) {
    const s = el.style;
    if (s.transitionDuration) { out.td.push(s.transitionDuration); out.tf.push(s.transitionTimingFunction || ''); out.tp.push(s.transitionProperty || ''); }
    if (s.animationDuration) { out.ad.push(s.animationDuration); out.af.push(s.animationTimingFunction || ''); }
  }
  try { out.running = document.getAnimations().length; } catch (e) {}
  return out;
}
"""

DOWNSAMPLE = r"""
async ([b64, scale]) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
  let w = img.width, h = img.height, src = img;
  const target = [Math.max(1, Math.floor(w / scale)), Math.max(1, Math.floor(h / scale))];
  while (w > target[0] * 2 || h > target[1] * 2) {   /* halve step by step so the result is an average, not a sample */
    const nw = Math.max(target[0], Math.ceil(w / 2)), nh = Math.max(target[1], Math.ceil(h / 2));
    const c = document.createElement('canvas'); c.width = nw; c.height = nh; const g = c.getContext('2d'); g.imageSmoothingQuality = 'high'; g.drawImage(src, 0, 0, nw, nh); src = c; w = nw; h = nh;
  }
  const c = document.createElement('canvas'); c.width = target[0]; c.height = target[1]; const g = c.getContext('2d', { willReadFrequently: true }); g.imageSmoothingQuality = 'high'; g.drawImage(src, 0, 0, target[0], target[1]);
  const d = g.getImageData(0, 0, target[0], target[1]).data, px = [];
  for (let i = 0; i < d.length; i += 4) px.push([d[i], d[i + 1], d[i + 2]]);
  return {w: target[0], h: target[1], px};
}
"""

# --------------------------------------------------------------------------------------------------------------------------------------
# Colour maths
# --------------------------------------------------------------------------------------------------------------------------------------


def hex_of(rgb) -> str:
    return "#%02x%02x%02x" % tuple(int(round(max(0, min(255, v)))) for v in rgb[:3])


def _lin(v: float) -> float:
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4   # WCAG 2.2: 0.04045 threshold


def luminance(rgb) -> float:
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def contrast(fg, bg) -> float:
    a, b = luminance(fg) + 0.05, luminance(bg) + 0.05
    return max(a, b) / min(a, b)


def oklab(rgb):
    r, g, b = (_lin(v) for v in rgb[:3])
    l = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklch(rgb):
    L, a, b = oklab(rgb)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def lab_distance(p, q) -> float:
    return math.dist(p, q)


def blend(top, bottom):
    a = top[3] if len(top) > 3 else 1.0
    return tuple(top[i] * a + bottom[i] * (1 - a) for i in range(3))


def rgb_key(c) -> tuple:
    return tuple(int(round(max(0, min(255, v)))) for v in c[:3])


def hue_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


# --------------------------------------------------------------------------------------------------------------------------------------
# Clustering helpers
# --------------------------------------------------------------------------------------------------------------------------------------


def cluster_colors(weights: dict, merge: float = COLOR_MERGE_DE) -> list[dict]:
    """Greedy OKLab clustering, heaviest colour first; a cluster is named by its heaviest member. Neutrals (C < 0.02) and chromatics cluster apart,
    at most MAX_CHROMATIC + MAX_NEUTRAL clusters remain (the lightest are folded into the nearest)."""
    groups = {True: [], False: []}
    for rgb, w in sorted(weights.items(), key=lambda kv: -kv[1]):
        if w <= 0:
            continue
        lab = oklab(rgb)
        neutral = math.hypot(lab[1], lab[2]) < NEUTRAL_CHROMA
        best, bd = None, merge
        for c in groups[neutral]:
            d = lab_distance(lab, c["lab"])
            if d < bd:
                best, bd = c, d
        if best:
            best["w"] += w
        else:
            groups[neutral].append({"rgb": rgb, "lab": lab, "w": w, "neutral": neutral})
    for neutral, cap in ((True, MAX_NEUTRAL), (False, MAX_CHROMATIC)):
        cl = groups[neutral]
        while len(cl) > cap:
            cl.sort(key=lambda c: -c["w"])
            small = cl.pop()
            near = min(cl, key=lambda c: lab_distance(c["lab"], small["lab"]))
            near["w"] += small["w"]
    out = groups[True] + groups[False]
    for c in out:
        L, C, h = oklch(c["rgb"])
        c["lch"] = (L, C, h)
    return sorted(out, key=lambda c: -c["w"])


def cluster_1d(items: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """items: (value, weight); returns (centre, weight) pairs, heaviest first. A value joins the first centre within tol."""
    centres: list[list[float]] = []
    for v, w in sorted(items, key=lambda it: -it[1]):
        for c in centres:
            if abs(c[0] - v) <= tol:
                c[1] += w
                break
        else:
            centres.append([v, w])
    return sorted(((c[0], c[1]) for c in centres), key=lambda c: -c[1])


def weighted_quantile(pairs: list[tuple[float, float]], q: float):
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    if not pairs or total <= 0:
        return None
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total * q:
            return v
    return pairs[-1][0]


def r3(v, n=3):
    return None if v is None else round(v, n)


def lch_dict(lch) -> dict:
    return {"l": round(lch[0], 3), "c": round(lch[1], 3), "h": round(lch[2], 1)}


# --------------------------------------------------------------------------------------------------------------------------------------
# Analysis (pure functions of the raw page data, so they run without a browser)
# --------------------------------------------------------------------------------------------------------------------------------------


def norm_stack(fam: str) -> str:
    return re.sub(r"\s*,\s*", ", ", re.sub(r"[\"']", "", fam)).strip()


def analyse_type(texts: list[dict]) -> dict:
    rows = [t for t in texts if t["n"] > 0 and t["fs"] > 0]
    if not rows:
        return {"size_hist": {}, "weights": {}, "line_height": {"hist": {}, "median": None, "normal_share": 0}, "families": [], "scale": [], "minor_sizes": [], "step_ratios": [],
                "ratio": {"median": None, "module": None, "gap": None, "spread": None}, "body_px": None, "max_px": None, "max_over_body": None}
    wt = lambda t: t["n"] * t["fs"]
    total = sum(wt(t) for t in rows)
    size_hist: dict[int, list[float]] = defaultdict(lambda: [0.0, 0.0])
    for t in rows:
        k = int(round(t["fs"]))
        size_hist[k][0] += t["n"]
        size_hist[k][1] += wt(t)
    weights = Counter()
    lh_hist = Counter()
    lh_pairs = []
    stacks = Counter()
    normal_lh = 0.0
    for t in rows:
        weights[t["fw"]] += wt(t)
        stacks[norm_stack(t["fam"])] += wt(t)
        ratio = (t["lh"] / t["fs"]) if t["lh"] else 1.2    # line-height: normal is about 1.2 for most fonts
        if not t["lh"]:
            normal_lh += wt(t)
        lh_hist[round(round(ratio / 0.05) * 0.05, 2)] += wt(t)
        lh_pairs.append((ratio, wt(t)))
    # effective scale: sizes less than 1 px apart are one step, named by the heaviest member
    raw_sizes = Counter()
    for t in rows:
        raw_sizes[round(t["fs"], 1)] += wt(t)
    centres: list[list[float]] = []
    for s, w in sorted(raw_sizes.items(), key=lambda kv: -kv[1]):
        for c in centres:
            if abs(c[0] - s) < 1.0:
                c[1] += w
                break
        else:
            centres.append([s, w])
    steps, minor = [], []
    for c in sorted(centres):
        (steps if c[1] / total >= MIN_STEP_SHARE else minor).append(c)
    centre_of = {}                                    # each raw size belongs to the nearest centre
    for s in raw_sizes:
        centre_of[s] = min(centres, key=lambda c: abs(c[0] - s))[0]
    scale = []
    for size, w in steps:
        fws = Counter()
        lhs = []
        for t in rows:
            if centre_of[round(t["fs"], 1)] == size:
                fws[t["fw"]] += wt(t)
                lhs.append((((t["lh"] / t["fs"]) if t["lh"] else 1.2), wt(t)))
        scale.append({"px": size if size != int(size) else int(size), "share": round(w / total, 4), "weight": fws.most_common(1)[0][0] if fws else 400,
                      "line_height": r3(weighted_quantile(lhs, 0.5), 2)})
    ratios = [scale[i + 1]["px"] / scale[i]["px"] for i in range(len(scale) - 1)]
    median_ratio = statistics.median(ratios) if ratios else None
    module = min(MODULES, key=lambda m: abs(m - median_ratio)) if median_ratio else None
    body = max(scale, key=lambda s: s["share"])["px"] if scale else None
    return {
        "size_hist": {str(k): {"chars": round(v[0], 1), "share": round(v[1] / total, 4)} for k, v in sorted(size_hist.items())},
        "weights": {str(k): round(v / total, 4) for k, v in sorted(weights.items())},
        "line_height": {"hist": {str(k): round(v / total, 4) for k, v in sorted(lh_hist.items())}, "median": r3(weighted_quantile(lh_pairs, 0.5), 2), "normal_share": round(normal_lh / total, 4)},
        "families": [{"stack": k, "share": round(v / total, 4)} for k, v in stacks.most_common()],
        "scale": scale,
        "minor_sizes": [c[0] for c in minor],
        "step_ratios": [round(r, 3) for r in ratios],
        "ratio": {"median": r3(median_ratio), "module": module, "gap": r3(abs(median_ratio - module)) if module else None, "spread": r3(max(ratios) - min(ratios)) if ratios else None},
        "body_px": body,
        "max_px": scale[-1]["px"] if scale else None,
        "max_over_body": r3(scale[-1]["px"] / body, 2) if scale and body else None,
    }


def summarize(clusters: list[dict]) -> list[dict]:
    total = sum(c["w"] for c in clusters) or 1
    return [{"hex": hex_of(c["rgb"]), "share": round(c["w"] / total, 4), "oklch": lch_dict(c["lch"]), "neutral": c["neutral"]} for c in clusters]


def analyse_color(raw: dict) -> dict:
    text, bgw, border = Counter(), Counter(), Counter()
    ratios, unknown, worst = [], 0.0, []
    for t in raw["texts"]:
        if t["col"] is None:
            continue
        fg = blend(t["col"], t["bg"])
        text[rgb_key(fg)] += max(t["a"], 1)
        if t["unk"]:
            unknown += t["n"]
        elif not t["dis"]:
            cr = contrast(rgb_key(fg), rgb_key(t["bg"]))
            ratios.append((cr, t["n"]))
            worst.append((cr, t["s"], hex_of(rgb_key(fg)), hex_of(rgb_key(t["bg"]))))
    for b in raw["bgs"]:
        if b["a"] <= 0:
            continue
        if b["c"] is not None:
            bgw[rgb_key(b["c"])] += b["a"]
        elif b["g"]:
            for s in b["g"]:
                bgw[rgb_key(blend(s, b["e"]))] += b["a"] / len(b["g"])
    for b in raw["borders"]:
        border[rgb_key(blend(b["c"], b["e"]))] += max(b["w"], 1)
    channels = {"text": text, "background": bgw, "border": border}
    clusters = {k: cluster_colors(v) for k, v in channels.items()}
    # one combined weighting (background 0.5, text 0.3, border 0.2; a missing channel gives its weight to the others)
    present = [k for k in channels if sum(channels[k].values()) > 0]
    scale = sum(CHANNEL_WEIGHT[k] for k in present) or 1
    combined: dict = defaultdict(float)
    for k in present:
        tot = sum(channels[k].values())
        for rgb, w in channels[k].items():
            combined[rgb] += CHANNEL_WEIGHT[k] / scale * w / tot
    mean_chroma = sum(oklch(rgb)[1] * w for rgb, w in combined.items()) / (sum(combined.values()) or 1) if combined else None
    comb = cluster_colors(combined)
    ctotal = sum(c["w"] for c in comb) or 1
    for c in comb:
        c["share"] = c["w"] / ctotal
    chromatic = [c for c in comb if c["lch"][1] >= PRIMARY_MIN_CHROMA and 0.2 <= c["lch"][0] <= 0.95]
    chromatic.sort(key=lambda c: -c["share"] * c["lch"][1])        # area-weighted saturation
    primary = chromatic[0] if chromatic else None
    accent = next((c for c in chromatic[1:] if hue_distance(c["lch"][2], primary["lch"][2]) >= 30), None) if primary else None
    ratios.sort()
    worst.sort()
    page_bg = rgb_key(raw["page"]["color"])
    return {
        "text": summarize(clusters["text"]),
        "background": summarize(clusters["background"]),
        "border": summarize(clusters["border"]),
        "primary": ({"hex": hex_of(primary["rgb"]), "oklch": lch_dict(primary["lch"]), "share": round(primary["share"], 4)} if primary else None),
        "accent": ({"hex": hex_of(accent["rgb"]), "oklch": lch_dict(accent["lch"]), "share": round(accent["share"], 4)} if accent else None),
        "mean_chroma": r3(mean_chroma),
        "page_background": hex_of(page_bg),
        "contrast": {
            "median": r3(weighted_quantile(ratios, 0.5), 2), "min": r3(ratios[0][0], 2) if ratios else None, "samples": len(ratios),
            "unknown_background_share": round(unknown / (unknown + sum(w for _, w in ratios)), 4) if unknown else 0,
            "worst": [{"text": s, "ratio": round(cr, 2), "fg": f, "bg": b} for cr, s, f, b in worst[:3]],
        },
        "_combined": comb,
    }


def analyse_shape(raw: dict) -> dict:
    boxes = raw["boxes"]
    count, area = Counter(), Counter()
    for b in boxes:
        key = "pill" if b["p"] else b["r"]
        count[key] += 1
        area[key] += b["a"]
    n, a_total = sum(count.values()) or 1, sum(area.values()) or 1
    rows = [{"px": k, "count": count[k], "count_share": round(count[k] / n, 4), "area_share": round(area[k] / a_total, 4)} for k in count if k != 0]
    rows.sort(key=lambda r: -r["count"])
    kept = [r for r in rows if r["count_share"] >= MIN_SHARE or r["area_share"] >= MIN_SHARE]
    pairs = raw["nested"]          # only boxes closer to the outer edge than the outer radius: further in, any inner radius is free
    ok = sum(1 for p in pairs if abs(p["r"] - max(p["pr"] - p["g"], 0)) <= 2)
    return {
        "radius": rows,
        "radius_values": sorted([r["px"] for r in kept if r["px"] != "pill"]) + (["pill"] if any(r["px"] == "pill" for r in kept) else []),
        "radius_distinct": len(kept),
        "square_share": round(count[0] / n, 4),
        "boxes": len(boxes),
        "nested": {"pairs": len(pairs), "ok": ok, "ratio": r3(ok / len(pairs)) if pairs else None},
    }


def shadow_summary(layers: list[dict]) -> str:
    return ", ".join(f"{'inset ' if l['inset'] else ''}{l['x']:g}px {l['y']:g}px {l['blur']:g}px {l['spread']:g}px rgba({int(round(l['rgb'][0]))}, {int(round(l['rgb'][1]))}, {int(round(l['rgb'][2]))}, {l['a']:.2f})" for l in layers)


def layer_kind(l: dict) -> str:
    if l["a"] < 0.01:
        return "none"
    if l["inset"]:
        return "inset"
    if l["blur"] == 0 and l["x"] == 0 and l["y"] == 0:
        return "ring"            # focus / outline ring, not elevation
    if l["blur"] == 0:
        return "edge"            # hard edge line such as 0 1px 0
    return "elevation"


def analyse_depth(raw: dict) -> dict:
    count, area = Counter(), Counter()
    for b in raw["boxes"]:
        if b["sh"]:
            count[b["sh"]] += 1
            area[b["sh"]] += b["a"]
    total_n = sum(count.values())
    shadows = []
    for css, n in count.most_common():
        layers = raw["shadows"].get(css, [])
        kinds = [layer_kind(l) for l in layers]
        elev = [l for l, k in zip(layers, kinds) if k == "elevation"]
        dom = max(elev, key=lambda l: l["blur"]) if elev else None
        shadows.append({"css": shadow_summary(layers), "count": n, "share": round(n / total_n, 4), "kinds": sorted(set(kinds) - {"none"}),
                        "layers": [{"x": l["x"], "y": l["y"], "blur": l["blur"], "spread": l["spread"], "alpha": round(l["a"], 3), "inset": l["inset"], "kind": k} for l, k in zip(layers, kinds)],
                        "magnitude": (dom["blur"] + abs(dom["y"])) if dom else None, "_dom": dom})
    elevation = [s for s in shadows if s["magnitude"] is not None and s["share"] >= MIN_SHARE]
    # elevation levels: shadows whose blur + |offset| differ by less than a quarter (or 2 px) are one level
    centres: list[dict] = []
    for s in sorted(elevation, key=lambda s: -s["count"]):
        for c in centres:
            if abs(c["magnitude"] - s["magnitude"]) <= max(2, 0.25 * c["magnitude"]):
                c["count"] += s["count"]
                break
        else:
            centres.append({"magnitude": s["magnitude"], "count": s["count"], "css": s["css"]})
    centres.sort(key=lambda c: c["magnitude"])
    ys = [l["y"] for s in elevation for l in s["layers"] if l["kind"] == "elevation" and abs(l["y"]) >= 0.5]
    direction = "none" if not ys else "down" if all(y > 0 for y in ys) else "up" if all(y < 0 for y in ys) else "mixed"
    counts = Counter()
    for s in elevation:
        d = max((l for l in s["layers"] if l["kind"] == "elevation"), key=lambda l: l["blur"])
        counts["down" if d["y"] > 0.5 else "up" if d["y"] < -0.5 else "level"] += s["count"]
    for s in shadows:
        s.pop("_dom", None)
    return {"shadows": shadows[:12], "distinct": len(shadows), "levels": len(centres), "level_list": centres, "direction": direction, "direction_boxes": dict(counts),
            "single_light": direction in ("down", "up", "none"), "boxes_with_shadow": total_n}


def pick_grid(values: Counter) -> dict:
    vals = {v: n for v, n in values.items() if v > HAIRLINE_MAX}
    total = sum(vals.values())
    if not total:
        return {"base_unit": None, "share4": None, "share8": None, "off_grid": [], "off_grid_share": None, "common": []}
    s4 = sum(n for v, n in vals.items() if v % 4 == 0) / total
    s8 = sum(n for v, n in vals.items() if v % 8 == 0) / total
    base = 8 if s8 >= 0.85 else 4 if s4 >= 0.6 else None     # mostly on 8: an 8 grid; else mostly on 4: a 4 grid (the stray values are counted as off grid); else none
    unit = base or 4
    off = {v: n for v, n in vals.items() if v % unit}
    common = sorted(v for v, _ in sorted(vals.items(), key=lambda kv: (-kv[1], kv[0]))[:6])      # the six values the page uses most, on the grid or not
    return {"base_unit": base, "share4": round(s4, 4), "share8": round(s8, 4), "checked_unit": unit,
            "off_grid": [{"px": v, "count": n} for v, n in sorted(off.items(), key=lambda kv: -kv[1])[:12]],
            "off_grid_share": round(sum(off.values()) / total, 4), "common": common}


def analyse_space(raw: dict) -> dict:
    sib, pad, gap = Counter(raw["sibs"]), Counter(raw["pads"]), Counter(raw["gaps"])
    allv = sib + pad + gap
    hist = lambda c: {str(k): v for k, v in sorted(c.items(), key=lambda kv: -kv[1])[:20]}
    out = {"sibling": hist(sib), "padding": hist(pad), "gap": hist(gap), "all": hist(allv), "samples": sum(allv.values())}
    out.update(pick_grid(allv))
    return out


def downsample(png: bytes, fallback: dict | None):
    """The page screenshot at 1/WS_SCALE: (width, height, [(r, g, b)...])."""
    if fallback is not None:
        return fallback["w"], fallback["h"], [tuple(p) for p in fallback["px"]]
    from PIL import Image
    img = Image.open(io.BytesIO(png)).convert("RGB")
    small = img.resize((max(1, img.width // WS_SCALE), max(1, img.height // WS_SCALE)), Image.BOX)
    return small.width, small.height, list(small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata())


def whitespace(png: bytes, fallback: dict | None, viewport_h: int) -> dict:
    w, h, px = downsample(png, fallback)
    if not px:
        return {"ratio": None, "first_screen_ratio": None, "background": None}
    bins = Counter((p[0] >> 3, p[1] >> 3, p[2] >> 3) for p in px)
    top = bins.most_common(1)[0][0]
    members = [p for p in px if (p[0] >> 3, p[1] >> 3, p[2] >> 3) == top]
    bg = tuple(sum(p[i] for p in members) / len(members) for i in range(3))
    bg_lab = oklab(bg)
    cache: dict = {}

    def near(p) -> bool:
        if p not in cache:
            cache[p] = lab_distance(oklab(p), bg_lab) <= WS_DE
        return cache[p]
    flags = [near(p) for p in px]
    rows = min(h, max(1, math.ceil(viewport_h / WS_SCALE)))
    return {"ratio": round(sum(flags) / len(flags), 4), "first_screen_ratio": round(sum(flags[:rows * w]) / max(1, rows * w), 4), "background": hex_of(bg), "grid": f"{w}x{h}"}


def analyse_layout(raw: dict, png_full: bytes | None, fallback: dict | None, width: int, height: int) -> dict:
    texts = [t for t in raw["texts"] if t["n"] > 0]
    lines_by_type = {}
    flat = []
    for kind in ("l", "c", "r"):
        items = [(t["ax"], 1.0) for t in texts if t["first"] and t["al"] == kind]
        cl = [(int(round(x)), int(n)) for x, n in cluster_1d(items, ALIGN_TOLERANCE)]
        lines_by_type[{"l": "left", "c": "center", "r": "right"}[kind]] = [{"x": x, "count": n} for x, n in cl[:8]]
        flat += [{"type": {"l": "left", "c": "center", "r": "right"}[kind], "x": x, "count": n} for x, n in cl]
    flat.sort(key=lambda r: -r["count"])
    strong = [r for r in flat if r["count"] >= ALIGN_MIN_COVER]
    lefts = [(t["l"], t["n"]) for t in texts]
    rights = [(t["r"], t["n"]) for t in texts]
    cl_, cr_ = weighted_quantile(lefts, 0.05), weighted_quantile(rights, 0.95)
    chars = sum(t["n"] for t in texts)
    screens = max(raw["pageH"] / raw["vh"], 1e-9)
    first = sum(t["n"] for t in texts if t["t"] < raw["vh"])
    page_area = raw["vw"] * raw["pageH"]
    img_area = sum(i["a"] for i in raw["images"] if i["k"] != "icon")
    targets = raw["targets"]
    limit = TOUCH_PX if width < TOUCH_WIDTH else POINTER_PX
    sides = [min(t) for t in targets]
    buckets = Counter()
    for s in sides:
        buckets["<24" if s < 24 else "24-31" if s < 32 else "32-39" if s < 40 else "40-43" if s < 44 else ">=44"] += 1
    out = {
        "align": {"tolerance_px": ALIGN_TOLERANCE, "lines": lines_by_type, "top": flat[:8], "strong_lines": len(strong), "min_cover": ALIGN_MIN_COVER},
        "content": {"left": r3(cl_, 1), "right": r3(cr_, 1), "width": r3(cr_ - cl_, 1) if cl_ is not None else None, "viewport": raw["vw"], "ratio": r3((cr_ - cl_) / raw["vw"]) if cl_ is not None else None},
        "density": {"chars": round(chars), "chars_per_screen": round(chars / screens), "chars_first_screen": round(first), "screens": round(screens, 2)},
        "image_area_ratio": round(min(1.0, img_area / page_area), 4) if page_area else 0,
        "touch": {"count": len(targets), "limit_px": limit, "small": sum(1 for s in sides if s < limit), "small_share": r3(sum(1 for s in sides if s < limit) / len(sides)) if sides else None,
                  "min_side_hist": {k: buckets[k] for k in ("<24", "24-31", "32-39", "40-43", ">=44") if buckets[k]}, "smallest": min(sides) if sides else None},
        "whitespace": whitespace(png_full, fallback, height) if (png_full or fallback) else {"ratio": None, "first_screen_ratio": None, "background": None},
    }
    return out


def parse_times(values: list[str]) -> list[float]:
    out = []
    for v in values:
        for part in split_top(v):
            m = re.match(r"^\s*(-?[\d.]+)\s*(ms|s)\s*$", part)
            if m:
                ms = float(m.group(1)) * (1000 if m.group(2) == "s" else 1)
                if ms > 0:
                    out.append(round(ms))
    return out


def split_top(v: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in v:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def analyse_motion(m: dict) -> dict:
    def freq(c: Counter) -> list[dict]:
        return [{"value": k, "count": n} for k, n in c.most_common(10)]
    td, ad = parse_times(m["td"]), parse_times(m["ad"])
    tf = Counter(re.sub(r"\s+", " ", re.sub(r"\s*,\s*", ", ", p)) for v in m["tf"] for p in split_top(v) if p)
    af = Counter(re.sub(r"\s+", " ", re.sub(r"\s*,\s*", ", ", p)) for v in m["af"] for p in split_top(v) if p)
    tp = Counter(p for v in m["tp"] for p in split_top(v) if p)
    return {
        "transition_durations_ms": freq(Counter(td)), "animation_durations_ms": freq(Counter(ad)),
        "transition_timing": freq(tf), "animation_timing": freq(af), "transition_properties": freq(tp),
        "transitions": len(td), "animations": len(ad), "keyframes": m["keyframes"], "reduced_motion_branch": bool(m["reduced"]),
        "running_animations": m["running"], "rules_read": m["rules"], "unreadable_sheets": m["unreadable"],
    }


def analyse(raw: dict, motion: dict, png_full: bytes | None, fallback: dict | None, width: int, height: int) -> dict:
    color = analyse_color(raw)
    report = {
        "type": analyse_type(raw["texts"]),
        "color": color,
        "shape": analyse_shape(raw),
        "depth": analyse_depth(raw),
        "space": analyse_space(raw),
        "layout": analyse_layout(raw, png_full, fallback, width, height),
        "motion": analyse_motion(motion),
    }
    report["token_draft"] = token_draft(report)
    report["color"].pop("_combined", None)
    return report


# --------------------------------------------------------------------------------------------------------------------------------------
# Token draft
# --------------------------------------------------------------------------------------------------------------------------------------


def token_draft(rep: dict) -> dict:
    scale = list(rep["type"]["scale"])
    body = rep["type"]["body_px"]
    if len(scale) > 8:    # at most 8 steps: the heaviest, always with the largest
        keep = sorted(scale, key=lambda s: -s["share"])[:8]
        if scale[-1] not in keep:
            keep[-1] = scale[-1]
        scale = sorted(keep, key=lambda s: s["px"])
    names_down, names_up = ["sm", "xs", "2xs", "3xs"], ["lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl"]
    bi = next((i for i, s in enumerate(scale) if s["px"] == body), 0)
    type_scale = []
    for i, s in enumerate(scale):
        name = "body" if i == bi else (names_down[min(bi - i - 1, 3)] if i < bi else names_up[min(i - bi - 1, 6)])
        type_scale.append({"name": name, "px": s["px"], "weight": s["weight"], "line_height": s["line_height"]})
    comb = rep["color"]["_combined"]
    page_bg = rep["color"]["page_background"]
    bgs = rep["color"]["background"]
    canvas_rgb = tuple(int(page_bg[i:i + 2], 16) for i in (1, 3, 5))
    neutrals = sorted((c for c in comb if c["neutral"]), key=lambda c: -c["lch"][0])
    if len(neutrals) > 6:
        neutrals = [neutrals[round(i * (len(neutrals) - 1) / 5)] for i in range(6)]
    primary = rep["color"]["primary"]
    rgb_of = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    texts = [c for c in rep["color"]["text"] if not (primary and c["hex"] == primary["hex"])]
    inks = [c for c in texts if c["neutral"]] or texts          # the ink levels are the neutral text colours; a coloured price or link is not one of them
    readable = sorted((c for c in inks if contrast(rgb_of(c["hex"]), canvas_rgb) >= 3), key=lambda c: -contrast(rgb_of(c["hex"]), canvas_rgb))[:3]
    inverse = next((c["hex"] for c in texts if contrast(rgb_of(c["hex"]), canvas_rgb) < 3), None)       # white on the brand button, for example
    surface = next((b["hex"] for b in bgs if b["hex"] != page_bg and b["oklch"]["c"] < PRIMARY_MIN_CHROMA), None)   # the card colour: a neutral or a faint tint
    radii = rep["shape"]["radius_values"]
    names = ["sm", "md", "lg", "xl"]
    radius = {}
    for v in [r for r in radii if r != "pill"][:4]:
        radius[names[len(radius)]] = v
    if "pill" in radii:
        radius["pill"] = 9999
    levels = rep["depth"]["level_list"][:4]
    return {
        "type_scale": type_scale,
        "type_module": rep["type"]["ratio"]["module"],
        "font_stack": rep["type"]["families"][0]["stack"] if rep["type"]["families"] else None,
        "palette": {
            "primary": primary["hex"] if primary else None,
            "accent": rep["color"]["accent"]["hex"] if rep["color"]["accent"] else None,
            "neutrals": [hex_of(c["rgb"]) for c in neutrals],
            "text": {**{name: (readable[i]["hex"] if i < len(readable) else None) for i, name in enumerate(("primary", "secondary", "tertiary"))}, "inverse": inverse},
            "background": {"canvas": page_bg, "surface": surface},
        },
        "radius": radius,
        "shadow": {f"e{i + 1}": l["css"] for i, l in enumerate(levels)},
        "spacing": {"base": rep["space"]["base_unit"], "steps": rep["space"]["common"]},
    }


# --------------------------------------------------------------------------------------------------------------------------------------
# Lint
# --------------------------------------------------------------------------------------------------------------------------------------


def item(metric, value, rng, why, fix) -> dict:
    return {"metric": metric, "value": value, "range": rng, "why": why, "fix": fix}


def lint(rep: dict) -> dict:
    out = []
    ty, co, sh, de, sp, ly, mo = (rep[k] for k in ("type", "color", "shape", "depth", "space", "layout", "motion"))
    n = len(ty["scale"])
    if n > MAX_TYPE_STEPS:
        out.append(item("有效字阶", f"{n} 档（{'/'.join(str(s['px']) for s in ty['scale'])}px）", f"≤ {MAX_TYPE_STEPS} 档",
                        "字号档位太多，相邻档只差 1 到 2px 时眼睛分不出层级，页面像是随手调出来的，不像有体系的产品。",
                        f"收敛到 5 到 {MAX_TYPE_STEPS} 档，按 1.2 或 1.25 的比例取阶（正文 {ty['body_px']}px 起算），相邻档至少差 2px，其余字号并入最近一档。"))
    wts = [k for k, v in ty["weights"].items() if v >= MIN_SHARE]
    if len(wts) > MAX_WEIGHTS:
        out.append(item("字重种类", f"{len(wts)} 种（{'/'.join(wts)}）", f"≤ {MAX_WEIGHTS} 种",
                        "字重过多，粗细的差别不再表达层级，反而让版面发花；中文字体的中间字重常常被系统替换成相邻字重，实际渲染也不一致。",
                        "只留常规 400、半粗 600 和（22px 以上的）粗体 700，其余并入相邻档。"))
    tcols = [c for c in co["text"] if c["share"] >= MIN_SHARE]
    if len(tcols) > MAX_TEXT_COLORS:
        out.append(item("文字主色", f"{len(tcols)} 种", f"≤ {MAX_TEXT_COLORS} 种",
                        "文字颜色太多，信息的主次靠颜色而不是靠字号和位置来区分，页面显得花、不沉着。",
                        "文字只留主文字、次文字、辅助文字三级中性色，再加反白、品牌色和状态色；其余并入最近的一级。"))
    if sh["radius_distinct"] > MAX_RADII:
        out.append(item("圆角种类", f"{sh['radius_distinct']} 种（{'/'.join(str(v) for v in sh['radius_values'])}）", f"≤ {MAX_RADII} 种",
                        "圆角大小不统一，卡片、按钮、输入框的形状语言对不上，观感零碎。",
                        "定 3 档加药丸（如 4/8/12/pill），同类组件同一档；嵌套时内层圆角取外层圆角减内边距。"))
    if de["levels"] > MAX_SHADOW_LEVELS:
        out.append(item("阴影层级", f"{de['levels']} 级", f"≤ {MAX_SHADOW_LEVELS} 级",
                        "阴影层级过多，抬起高度的含义被稀释，画面像是每个组件各自飘着。",
                        "按 1 到 4 级定义抬起高度，偏移与模糊随层级递增，其余阴影并入最近一级。"))
    if de["direction"] == "mixed":
        dc = de["direction_boxes"]
        out.append(item("阴影方向", f"向下 {dc.get('down', 0)} 个、向上 {dc.get('up', 0)} 个", "偏移全部向下（或全部向上）",
                        "光源方向不一致，有的投影向上、有的向下，立体感互相矛盾，页面显得不稳。",
                        "统一用向下的偏移（y 为正），不用向上或水平偏移的投影。"))
    if sp["off_grid_share"] is not None and sp["off_grid_share"] > MAX_OFF_GRID:
        offs = "/".join(str(o["px"]) for o in sp["off_grid"][:6])
        out.append(item("离网格间距比例", f"{sp['off_grid_share']:.0%}（{offs}px 等）", f"≤ {MAX_OFF_GRID:.0%}",
                        "间距不落在 4 或 8 的倍数上，元素之间的节奏对不齐，肉眼能感觉到‘松紧不一’。",
                        "选 4 或 8 作基准单位，所有间距、内边距、gap 取其倍数（4/8/12/16/24/32/48），离网格的值并入最近一档。"))
    if ly["align"]["strong_lines"] > MAX_ALIGN_LINES:
        out.append(item("对齐线", f"{ly['align']['strong_lines']} 条（各至少覆盖 {ALIGN_MIN_COVER} 个文本块）", f"≤ {MAX_ALIGN_LINES} 条",
                        "文本块的起点散在很多条竖线上，视线要不停地换位置，版面显得松散。",
                        "把文本起点收敛到页边距线、卡片内边距线等少数几条，同层内容共用同一条左边线。"))
    ws = ly["whitespace"]["ratio"]
    lo, hi = WHITESPACE_RANGE
    if ws is not None and not lo <= ws <= hi:
        tooless = ws < lo
        out.append(item("留白比例", f"{ws:.0%}", f"{lo:.0%} 到 {hi:.0%}",
                        "留白太少，内容挤在一起，没有呼吸感，显得廉价拥挤。" if tooless else "留白太多，画面空、信息密度太低，用户要滚很久才看到内容。",
                        "加大区块间距和卡片内边距，减少同屏模块数量。" if tooless else "收紧区块间距，补充有用内容或缩小占位元素。"))
    cm, cmin = co["contrast"]["median"], co["contrast"]["min"]
    if cm is not None and cm < MIN_CONTRAST_MEDIAN:
        out.append(item("正文对比度中位数", f"{cm}:1", f"≥ {MIN_CONTRAST_MEDIAN:g}:1",
                        "正文颜色偏灰，整体发虚，长时间阅读费眼，也缺少沉着的质感。",
                        "主文字改用接近黑的中性色（对白底 ≥ 7:1，如 #1d2129），灰色只留给次要信息。"))
    if cmin is not None and cmin < MIN_CONTRAST:
        w = co["contrast"]["worst"][0]
        out.append(item("文字对比度最低值", f"{cmin}:1（“{w['text']}” {w['fg']} 在 {w['bg']} 上）", f"≥ {MIN_CONTRAST:g}:1",
                        "有文字低于 WCAG AA，在强光或低端屏上看不清。",
                        "加深文字色或改换底色，让每处文字都达到 4.5:1，大字与图标至少 3:1。"))
    if co["mean_chroma"] is not None and co["mean_chroma"] > MAX_MEAN_CHROMA:
        out.append(item("平均饱和度", f"OKLCH C {co['mean_chroma']}", f"≤ {MAX_MEAN_CHROMA}",
                        "整体饱和度偏高，颜色互相抢眼，缺少让主色发挥作用的安静底色，显得廉价吵闹。",
                        "底色与文字用中性色，主色只放在按钮、选中态和关键数字上，点缀色面积控制在 10% 以内。"))
    t = ly["touch"]
    if t["small_share"] is not None and t["small_share"] > MAX_SMALL_TARGETS:
        out.append(item("触控目标小于 " + str(t["limit_px"]) + "px 的比例", f"{t['small_share']:.0%}（{t['small']}/{t['count']}，最小边最小 {t['smallest']}px）", f"≤ {MAX_SMALL_TARGETS:.0%}",
                        "可点击元素太小，手指容易点错，也让界面看起来局促。",
                        f"可点击元素的最小边做到 {t['limit_px']}px 以上（图标可以小，点击热区要大）。"))
    if (mo["transitions"] or mo["animations"]) and not mo["reduced_motion_branch"]:
        out.append(item("reduced-motion 分支", "没有", "有 prefers-reduced-motion 分支",
                        "页面有过渡或动画，却没有为‘减少动效’偏好准备静态方案，前庭敏感的用户会不适，也是成熟产品的基本功。",
                        "加 @media (prefers-reduced-motion: reduce) 分支，把过渡与动画时长降到 0 或只保留淡入淡出。"))
    return {"checked": 14, "count": len(out), "items": out}


# --------------------------------------------------------------------------------------------------------------------------------------
# Markdown summary
# --------------------------------------------------------------------------------------------------------------------------------------


def pct(v) -> str:
    return "-" if v is None else f"{v:.0%}"


def render_md(rep: dict) -> str:
    m, ty, co, sh, de, sp, ly, mo, td = (rep[k] for k in ("meta", "type", "color", "shape", "depth", "space", "layout", "motion", "token_draft"))
    L = [f"# 参考拆解：{m.get('title') or m['url']}", "",
         f"{m['url']} | {m['width']}x{m['height']} | {m['scheme']} | {m['date'][:10]} | {m['browser']}", ""]
    L += ["## 字阶", "", "| 字号 | 占比 | 字重 | 行高比 |", "|---|---|---|---|"]
    for s in ty["scale"]:
        L.append(f"| {s['px']}px{' 正文' if s['px'] == ty['body_px'] else ''} | {pct(s['share'])} | {s['weight']} | {s['line_height']} |")
    L += ["", f"有效字阶 {len(ty['scale'])} 档；相邻比中位数 {ty['ratio']['median']}，最近模数 {ty['ratio']['module']}；最大/正文 {ty['max_over_body']}；字体 {td['font_stack']}", ""]
    L += ["## 色板", "", "| 角色 | 色值 | 说明 |", "|---|---|---|"]
    pal = td["palette"]
    L.append(f"| 主色 | {pal['primary'] or '-'} | 点缀 {pal['accent'] or '-'} |")
    L.append(f"| 文字 | {' / '.join(v for k, v in pal['text'].items() if v and k != 'inverse') or '-'} | 主/次/辅；反白 {pal['text']['inverse'] or '-'} |")
    L.append(f"| 背景 | {pal['background']['canvas']} / {pal['background']['surface'] or '-'} | 画布/表面 |")
    L.append(f"| 中性 | {' '.join(pal['neutrals'])} | 浅到深 {len(pal['neutrals'])} 阶 |")
    c = co["contrast"]
    L += ["", f"平均饱和度 C={co['mean_chroma']}；文字对比度中位数 {c['median']}:1，最低 {c['min']}:1", ""]
    L += ["## 形状与层级", "", "| 项目 | 值 |", "|---|---|",
          f"| 圆角 | {' / '.join(str(v) for v in sh['radius_values']) or '无'}（{sh['radius_distinct']} 种；嵌套吻合 {pct(sh['nested']['ratio'])}） |",
          f"| 阴影 | {de['levels']} 级，方向 {de['direction']} |"]
    for i, lv in enumerate(de["level_list"][:4]):
        L.append(f"| e{i + 1} | {lv['css']} |")
    L += ["", "## 间距与布局", "", "| 项目 | 值 |", "|---|---|",
          f"| 基准单位 | {sp['base_unit'] or '无明显基准'}（4 的倍数 {pct(sp['share4'])}，8 的倍数 {pct(sp['share8'])}） |",
          f"| 常用间距 | {' / '.join(str(v) for v in sp['common']) or '-'} |",
          f"| 离网格 | {pct(sp['off_grid_share'])} {' '.join(str(o['px']) for o in sp['off_grid'][:6])} |",
          f"| 对齐线 | {ly['align']['strong_lines']} 条（覆盖至少 {ly['align']['min_cover']} 个文本块） |",
          f"| 内容宽度 | {ly['content']['width']}px（占视口 {pct(ly['content']['ratio'])}） |",
          f"| 每屏字数 | {ly['density']['chars_per_screen']}（首屏 {ly['density']['chars_first_screen']}） |",
          f"| 留白比例 | {pct(ly['whitespace']['ratio'])}（首屏 {pct(ly['whitespace']['first_screen_ratio'])}） |",
          f"| 图片面积 | {pct(ly['image_area_ratio'])} |",
          f"| 触控目标 | {ly['touch']['count']} 个，小于 {ly['touch']['limit_px']}px 占 {pct(ly['touch']['small_share'])} |", ""]
    L += ["## 动效", "",
          f"过渡 {mo['transitions']} 条，动画 {mo['animations']} 条，关键帧 {mo['keyframes']} 组；常见时长 "
          f"{', '.join(str(d['value']) + 'ms' for d in mo['transition_durations_ms'][:4]) or '-'}；常见曲线 {', '.join(d['value'] for d in mo['transition_timing'][:3]) or '-'}；"
          f"reduced-motion 分支：{'有' if mo['reduced_motion_branch'] else '无'}", ""]
    if "lint" in rep:
        lt = rep["lint"]
        L += [f"## 审美体检（{lt['count']} 条提示）", ""]
        if lt["items"]:
            L += ["| 指标 | 当前 | 常见范围 | 为什么 | 怎么改 |", "|---|---|---|---|---|"]
            for i in lt["items"]:
                L.append(f"| {i['metric']} | {i['value']} | {i['range']} | {i['why']} | {i['fix']} |")
        else:
            L.append("全部指标在常见范围内。")
        L.append("")
        L.append("常见范围是经验值，只作提示，不作合格线。")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------------------------------------------------------
# Browser
# --------------------------------------------------------------------------------------------------------------------------------------


def have_pil() -> bool:
    if os.environ.get("LUZ_TEARDOWN_NO_PIL"):
        return False
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def to_url(target: str) -> str:
    return target if "://" in target else Path(target).resolve().as_uri()


def collect(target: str, width: int, height: int, scheme: str, shots: str | None, expand: bool = True) -> dict:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright

    url = to_url(target)
    notes = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get("LUZ_AUDIT_CHANNEL", "msedge")) if os.environ.get("LUZ_AUDIT_CHANNEL") != "chromium" else pw.chromium.launch()
        try:
            ctx = browser.new_context(viewport={"width": width, "height": height}, locale="zh-CN", color_scheme=scheme)
            page = ctx.new_page()
            page.set_default_timeout(30000)
            sheets = []
            page.on("response", lambda r: sheets.append(r) if "text/css" in (r.headers.get("content-type") or "") else None)
            try:
                page.goto(url, wait_until="load", timeout=GOTO_TIMEOUT)
            except PlaywrightTimeout:
                notes.append("页面在 45 秒内没有触发 load，按已加载的部分测量")
            except PlaywrightError as e:
                raise SystemExit(f"ERROR cannot open {url}: {str(e).splitlines()[0]}")
            page.wait_for_timeout(SETTLE_MS)
            page.evaluate(PREPARE)
            scroller = page.evaluate(EXPAND) if expand else None
            if scroller:
                notes.append(f"内层滚动容器 {scroller['tag']}{'.' + scroller['cls'] if scroller['cls'] else ''}（内容高 {scroller['scrollHeight']}px，可视 {scroller['clientHeight']}px）已展开成整页高度再测量")
            for i in range(1, PAGE_CAP_SCREENS + 1):                  # scroll through the screens that are measured so lazy content loads
                if (i - 1) * height >= page.evaluate("() => document.documentElement.scrollHeight"):
                    break
                page.evaluate("(y) => scrollTo(0, y)", i * height)
                page.wait_for_timeout(150)
            page.evaluate("() => scrollTo(0, 0)")
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except PlaywrightTimeout:
                pass
            page.wait_for_timeout(300)
            raw = page.evaluate(COLLECT, {"pageCap": PAGE_CAP_SCREENS * height})
            motion = page.evaluate(MOTION, [])
            if motion["unreadable"]:          # cross-origin / file style sheets cannot be read by the page: read their text and parse it in a constructable sheet
                texts, loaded = [], []
                for href in motion["unreadable"]:
                    try:
                        if href.startswith("file:"):
                            from urllib.parse import unquote, urlparse
                            texts.append(Path(unquote(urlparse(href).path.lstrip("/"))).read_text(encoding="utf-8"))
                        else:
                            texts.append(next(r for r in sheets if r.url == href).text())
                        loaded.append(True)
                    except Exception:
                        loaded.append(False)
                        notes.append(f"样式表读不到：{href}")
                again = page.evaluate(MOTION, texts)
                for k in ("td", "tf", "ad", "af", "tp"):
                    motion[k] = motion[k] + again[k]
                motion["rules"] += again["rules"]
                motion["keyframes"] += again["keyframes"]
                motion["reduced"] = motion["reduced"] or again["reduced"]
                motion["unreadable"] = [h for h, ok in zip(motion["unreadable"], loaded) if not ok]
            clip = {"x": 0, "y": 0, "width": width, "height": raw["pageH"]}
            png_full = page.screenshot(full_page=True, clip=clip, animations="disabled", caret="hide")
            png_first = page.screenshot(animations="disabled", caret="hide")
            fallback = None
            if not have_pil():
                scratch = ctx.new_page()
                import base64
                fallback = scratch.evaluate(DOWNSAMPLE, [base64.b64encode(png_full).decode(), WS_SCALE])
                scratch.close()
            version = browser.version
            title = page.title()
            if raw["truncated"]:
                notes.append(f"页面高 {raw['docH']}px，只测量前 {raw['pageH']}px（{PAGE_CAP_SCREENS} 屏）")
        finally:
            browser.close()
    if shots:
        out = Path(shots)
        out.mkdir(parents=True, exist_ok=True)
        (out / "first-screen.png").write_bytes(png_first)
        (out / "full-page.png").write_bytes(png_full)
    channel = "chromium" if os.environ.get("LUZ_AUDIT_CHANNEL") == "chromium" else os.environ.get("LUZ_AUDIT_CHANNEL", "msedge")
    return {"scroller": scroller, "raw": raw, "motion": motion, "png_full": png_full, "fallback": fallback, "url": url, "browser": f"{channel} {version}", "title": title, "notes": notes}


def teardown(target: str, width: int = 390, height: int = 844, scheme: str = "light", shots: str | None = None, with_lint: bool = False, expand: bool = True) -> dict:
    got = collect(target, width, height, scheme, shots, expand)
    rep = analyse(got["raw"], got["motion"], got["png_full"], got["fallback"], width, height)
    meta = {"url": got["url"], "title": got["title"], "width": width, "height": height, "scheme": scheme, "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "browser": got["browser"], "expanded_scroller": got["scroller"], "page_height": got["raw"]["docH"], "measured_height": got["raw"]["pageH"], "elements": got["raw"]["elements"], "notes": got["notes"]}
    report = {"meta": meta, **rep}
    if with_lint:
        report["lint"] = lint(report)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", help="URL or local HTML file")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=844)
    ap.add_argument("--scheme", choices=("light", "dark"), default="light")
    ap.add_argument("--out", help="write the JSON here (default: print it)")
    ap.add_argument("--lint", action="store_true", help="check the numbers against the ranges of mature products (reports only, exit code stays 0)")
    ap.add_argument("--md", help="write a one-screen Chinese summary")
    ap.add_argument("--shots", help="save first-screen.png and full-page.png into this folder")
    ap.add_argument("--no-expand", action="store_true", help="do not let an inner scroll container grow to its content (default: it does, so an app shell is measured whole)")
    a = ap.parse_args(argv)
    rep = teardown(a.target, a.width, a.height, a.scheme, a.shots, a.lint, not a.no_expand)
    text = json.dumps(rep, ensure_ascii=False, indent=2)
    say = print if a.out else (lambda s="": print(s, file=sys.stderr))
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        say(f"teardown: {a.out}")
    else:
        print(text)
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(render_md(rep), encoding="utf-8")
        say(f"summary: {a.md}")
    for n in rep["meta"]["notes"]:
        say(f"note: {n}")
    if a.lint:
        lt = rep["lint"]
        say(f"lint: {lt['count']} 条提示（共 {lt['checked']} 项检查）")
        for i in lt["items"]:
            say(f"  - {i['metric']}：{i['value']}（常见范围 {i['range']}）\n      为什么：{i['why']}\n      怎么改：{i['fix']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
