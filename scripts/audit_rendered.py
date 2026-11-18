"""Audits a rendered HTML page in a real browser against the Luz interface rules (what is on screen, not the CSS text).

    py -X utf8 audit_rendered.py <file.html | url> [--width 390] [--height 900] [--reduced-motion] [--walk walk.py] [--no-focus-check]
        [--scheme light|dark [--dark-attr data-theme=dark] [--dark-class dark]]

Checks every visible text node: size >= 14 px (``--min-font 12`` for product interfaces: admin, mini-program, agent), weights 400/600/700 (700 only from 22 px), no italics, one font family, text contrast
>= 4.5:1 (3:1 for large text and disabled controls); the page has no horizontal scroll; touch targets >= 40 px (24 px on desktop widths); the style sheets carry no
``transition: all``, ``will-change`` or italic, and no transition on width/left/top/margin/padding. check_document.py reads the CSS text
and cannot see markup that a script builds; this tool reads the computed styles of the real page, so interactive prototypes use both.

``--no-focus-check`` skips the focus-frame probe. Otherwise every text field (input types text, search, tel, email, number, password, url, date and time, textarea, select,
contenteditable, role textbox / combobox / searchbox) is really focused and its computed style read, with the wrappers around it (Element Plus draws the frame on
``el-input__wrapper``): a coloured or default outline, a coloured or thick box-shadow ring or glow, or a thicker or coloured border that appears on focus is reported as "聚焦框"
(visual-design.html 层级与立体感 › 边缘线条: a focused text field only deepens its 1px border to ink2).

``--library <id|prefix>`` (repeatable; ids from references/component-libraries.json) adds the component source check: every control on
screen (button, input, select, textarea, table, dialog, nav and the ARIA control roles) must be, or sit inside, an element of the chosen
component library (its class prefix such as ``el-`` or ``t-``, or a custom element with that prefix); a hand-written control is reported as
"自造控件"。默认不设组件数量配额；仅在本次合同明确规定时传 ``--min-components``。阅读页可以没有控件，
已有控件仍逐项检查来源，不能以数量或只加载样式表代替真实复用证明。
A library with an ``attr`` in the registry (``--library luz-kit``, attr ``data-cid``) is read by that attribute instead of a class prefix: a control must sit
inside an element that carries ``data-cid`` (the component root, value = the component id such as MP-CARD-003), and the components are counted by the number of
different ``data-cid`` values. Whatever sits inside an element marked ``data-shell`` (the config and logic panels of the prototype shell) is not product interface:
its controls are not reported as "自造控件" and its components are not counted.

``--scheme light|dark`` (default light) opens the page with that colour scheme (Playwright ``color_scheme``, so ``prefers-color-scheme`` follows it) and runs every
check above on that rendering: font size, weights, contrast, touch targets, focus frames, the library check and the style sheet rules.
主题范围由功能合同与来源能力决定，不默认增加第二主题；只审计本次目标主题。A page that does not read ``prefers-color-scheme`` but switches
by an attribute or a class on ``<html>`` is told how with ``--dark-attr NAME=VALUE`` (``data-theme=dark``; a bare ``NAME`` sets the value ``dark``) and ``--dark-class NAME`` (``dark``);
both are repeatable, apply only with ``--scheme dark`` and are set right after the page loads, followed by 300 ms for the styles to settle. A page that keeps its theme in localStorage, or
switches with its own control, is switched by the caller in ``--walk`` (``page.evaluate("document.documentElement.dataset.theme = 'dark'")``, ``page.emulate_media(color_scheme="dark")``
or a click on the switch) and the scans after that are audited as they stand. With ``--scheme dark`` the first scan also asks whether the page really is dark: the background of ``<body>``
(or the first opaque background up the ``<html>`` chain; the canvas follows the computed ``color-scheme``, dark canvas only when the page declares a dark scheme) and the element in the middle of
the screen both lighter than luminance 0.3 is reported as "scheme dark: 页面底色仍是浅色，没有深色主题，或要用 --dark-attr / --dark-class 指定切换方式".

Ordered progress states (visual-design.html 有序进度状态的色阶): an element carrying ``data-stage-set="<set name>"`` and ``data-stage="<order position, from 1>"`` (optional
``data-stage-n="<size of the set>"``) is a value of an ordered state set. On such a page, within one set: every one needs its text label (WCAG 1.4.1), one position has one colour,
different positions have different colours that step on in order (chroma never falls; lightness never rises in the light scheme and never falls in the dark one) and neighbouring
positions differ by OKLab ΔE×100 of at least 3; when the page declares ``--stage-1`` to ``--stage-6`` on ``:root`` the colour must be the ramp stop of its position (stage_ramp.positions).
A page without these attributes is not checked for this.

``--walk`` takes a Python file defining ``walk(page, scan)`` that clicks through the page (menus, dialogs, states) and returns
``[(label, scan())]`` pairs (``scan()`` measures what is on screen now); each is audited as well. Touch targets must be 40 px on a phone
width (under 700 px), 24 px on a desktop pointer (WCAG 2.5.8). A control shorter than that counts at the height of its absolutely positioned ::before or ::after when it has one (the transparent hit-area extension the rule allows). Needs playwright and Microsoft Edge (or set LUZ_AUDIT_CHANNEL=chromium).
Exit code 1 when anything is found.
"""
import json
import os
import sys
from pathlib import Path

SCAN = r"""
(args) => {
  const minTarget = args.minTarget, prefixes = args.prefixes || [], attrs = args.attrs || [], minFont = args.minFont || 14;
  const out = {small: [], italic: [], weight: [], fonts: new Set(), contrast: [], targets: [], foreign: [], components: [], overflowX: document.documentElement.scrollWidth > innerWidth + 1};
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', { willReadFrequently: true });
  /* any CSS colour (rgb, oklch, color-mix, color(srgb …)) read back through a canvas pixel */
  const parse = (c) => { if (!c) return null; cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return { r: d[0], g: d[1], b: d[2], a: d[3] / 255 }; };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, bot) => ({r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1});
  /* the canvas under a transparent chain is the browser's: white, or the dark canvas when the page declares color-scheme dark (and the system scheme is dark when it declares both) */
  const declared = getComputedStyle(document.documentElement).colorScheme || 'normal';
  const darkCanvas = /dark/.test(declared) && (!/light/.test(declared) || matchMedia('(prefers-color-scheme: dark)').matches);
  const canvas = darkCanvas ? {r: 18, g: 18, b: 18, a: 1} : {r: 255, g: 255, b: 255, a: 1};
  const bgOf = (el) => { let stack = []; for (let n = el; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; } } let base = canvas; for (let i = stack.length - 1; i >= 0; i--) base = blend(stack[i], base); return base; };
  out.pageLum = lum(bgOf(document.body));
  const middle = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
  out.centerLum = middle ? lum(bgOf(middle)) : out.pageLum;
  const seen = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t; (t = walker.nextNode());) {
    const txt = t.nodeValue.trim(); if (!txt) continue;
    /* the simulated device chrome of a prototype (status bar clock, capsule): marked data-shell and aria-hidden, it is not product interface and a reader never meets it */
    if (t.parentElement && t.parentElement.closest('[data-shell][aria-hidden="true"]')) continue;
    const el = t.parentElement; if (!el || ['SCRIPT', 'STYLE', 'TITLE'].includes(el.tagName)) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    let hidden = false; for (let n = el; n; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden') { hidden = true; break; } if (n.hasAttribute && n.hasAttribute('hidden')) { hidden = true; break; } }
    if (hidden) continue;
    const id = el.tagName + '|' + (el.className && el.className.baseVal === undefined ? el.className : '') + '|' + txt.slice(0, 12); if (seen.has(id)) continue; seen.add(id);
    const size = parseFloat(cs.fontSize), w = parseInt(cs.fontWeight, 10);
    const label = (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : el.tagName) + ' "' + txt.slice(0, 16) + '"';
    if (size < minFont && !el.closest('svg')) out.small.push(label + ' ' + size + 'px');
    if (cs.fontStyle === 'italic') out.italic.push(label);
    if (![400, 600, 700].includes(w) || (w === 700 && size < 22)) out.weight.push(label + ' ' + w + '/' + size + 'px');
    out.fonts.add(cs.fontFamily.split(',')[0].trim());
    const fg = parse(cs.color), bg = bgOf(el);
    if (fg) { const f = blend(fg, bg), a = lum(f) + 0.05, b = lum(bg) + 0.05, ratio = (Math.max(a, b)) / Math.min(a, b); const large = size >= 24 || (size >= 18.66 && w >= 600); const dis = el.closest('[disabled],[aria-disabled="true"]'); if (ratio < (large || dis ? 3 : 4.5)) out.contrast.push(label + ' ' + ratio.toFixed(2) + ':1 on ' + Math.round(bg.r) + ',' + Math.round(bg.g) + ',' + Math.round(bg.b)); }
  }
  document.querySelectorAll('button, a[href], [role=button], input:not([type=hidden]):not([type=radio]):not([type=checkbox]), select, [role=tab]').forEach((el) => {
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return; const cs = getComputedStyle(el); if (cs.visibility === 'hidden') return;
    let hid = false; for (let n = el; n; n = n.parentElement) { if (getComputedStyle(n).display === 'none') { hid = true; break; } } if (hid) return;
    /* the tap area of a field is its library wrapper (el-input__wrapper, van-field, van-cell), not the bare <input> inside it */
    let height = r.height;
    if (prefixes.length && /^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName)) { let n = el.parentElement; for (let i = 0; n && i < 5; i++, n = n.parentElement) { const cl = n.getAttribute('class'); if (cl && cl.split(/\s+/).some((t) => prefixes.some((p) => t.startsWith(p)) && /(__wrapper|-field|-cell)$/.test(t))) { height = Math.max(height, n.getBoundingClientRect().height); break; } } }
    /* visual-design.html 点击区域与触控目标: a graphic smaller than the hit area may be extended with transparent padding or an absolutely positioned pseudo-element */
    if (height < minTarget) for (const pe of ['::before', '::after']) { const ps = getComputedStyle(el, pe); if (ps.content !== 'none' && ps.position === 'absolute') height = Math.max(height, parseFloat(ps.height) || 0); }
    if (height < minTarget) out.targets.push((el.className || el.tagName) + ' ' + Math.round(r.width) + '×' + Math.round(r.height));
  });
  if (prefixes.length || attrs.length) {
    const hasPrefix = (t) => prefixes.some((p) => t.startsWith(p));
    /* a library that names its component roots by an attribute (luz-kit: data-cid="MP-CARD-003") is read by that attribute: a control belongs to it when it sits inside an
       element that carries the attribute. The prototype's own shell (config and logic panels, marked data-shell) is not product interface: its controls are not checked
       against the library and its components are not counted. */
    const inShell = (el) => attrs.length > 0 && !!el.closest('[data-shell]');
    const inRoot = (el) => attrs.some((a) => !!el.closest('[' + a + ']'));
    /* a control is the library's own when it carries a library class (or is a library custom element, or sits inside one); a <table> may be the
       unclassed table inside a library table. A hand-written control inside a library card or dialog is still hand-written. */
    const fromLibrary = (el) => {
      if (inRoot(el)) return true;
      const own = (n) => { const cl = n.getAttribute('class'); return (cl && cl.split(/\s+/).some(hasPrefix)) || (n.tagName.includes('-') && hasPrefix(n.tagName.toLowerCase())); };
      if (own(el)) return true;
      /* the library's pagination draws its previous / next buttons as unclassed-by-prefix <button class="btn-prev">; they sit inside the library's pagination root */
      if (/(^|\s)btn-(prev|next)(\s|$)/.test(el.getAttribute('class') || '') && el.closest(prefixes.map((p) => '[class*="' + p + 'pagination"]').join(','))) return true;
      for (let n = el.parentElement; n && n.nodeType === 1; n = n.parentElement) if (n.tagName.includes('-') && hasPrefix(n.tagName.toLowerCase())) return true;
      if (el.tagName === 'TABLE') { let n = el.parentElement; for (let i = 0; n && i < 4; i++, n = n.parentElement) { const cl = n.getAttribute('class'); if (cl && cl.split(/\s+/).some((t) => hasPrefix(t) && t.includes('table'))) return true; } }
      return false;
    };
    const visible = (el) => { const r = el.getBoundingClientRect(); if (!r.width || !r.height) return false; for (let n = el; n; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden') return false; } return true; };
    document.querySelectorAll('button, select, textarea, input:not([type=hidden]), table, dialog, nav, [role=button], [role=tab], [role=switch], [role=dialog], [role=alertdialog], [role=menu], [role=menuitem], [role=listbox], [role=combobox], [role=checkbox], [role=radio], [role=slider], [role=tooltip]').forEach((el) => {
      if (el.closest('svg') || !visible(el) || inShell(el) || fromLibrary(el)) return;
      out.foreign.push(el.tagName.toLowerCase() + (el.getAttribute('class') ? '.' + el.getAttribute('class').split(/\s+/)[0] : '') + ' "' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 12) + '"');
    });
    const blocks = new Set();
    document.querySelectorAll('[class]').forEach((el) => { if (typeof el.className !== 'string') return; el.className.split(/\s+/).forEach((t) => { if (hasPrefix(t)) blocks.add(t.split('__')[0].split('--')[0]); }); });
    document.querySelectorAll('*').forEach((el) => { if (el.tagName.includes('-') && hasPrefix(el.tagName.toLowerCase())) blocks.add(el.tagName.toLowerCase()); });
    /* one component = one distinct value of the attribute (the same data-cid twice is one kind) */
    attrs.forEach((a) => document.querySelectorAll('[' + a + ']').forEach((el) => { if (!inShell(el) && el.getAttribute(a)) blocks.add(a + '=' + el.getAttribute(a)); }));
    out.components = [...blocks];
  }
  /* 有序进度状态（visual-design.html 有序进度状态的色阶）：带 data-stage-set 与 data-stage 的可见元素，读它们的计算色；页面根上的 --stage-1…6 一并读出 */
  const hex = (c) => '#' + [c.r, c.g, c.b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  out.stages = [];
  document.querySelectorAll('[data-stage-set][data-stage]').forEach((el) => {
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    for (let n = el; n; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden') return; }
    const fg = parse(getComputedStyle(el).color); if (!fg) return;
    /* the label is the element's own text or accessible name, or (for a colour dot drawn as an empty element) the text of the row it sits in */
    const text = (el.innerText || el.textContent || '').trim() || el.getAttribute('aria-label') || (el.parentElement ? (el.parentElement.innerText || '').trim() : '');
    out.stages.push({set: el.getAttribute('data-stage-set'), pos: parseInt(el.getAttribute('data-stage'), 10), n: el.hasAttribute('data-stage-n') ? parseInt(el.getAttribute('data-stage-n'), 10) : null, color: hex(fg), text: text,
                     label: '[' + el.getAttribute('data-stage-set') + ' ' + el.getAttribute('data-stage') + '] "' + text.slice(0, 12) + '"'});
  });
  out.stageTokens = [1, 2, 3, 4, 5, 6].map((i) => { const v = getComputedStyle(document.documentElement).getPropertyValue('--stage-' + i).trim(); const c = v ? parse(v) : null; return c ? hex(c) : null; });
  out.fonts = [...out.fonts];
  return out;
}
"""

FOCUS = r"""
async () => {
  /* Every text field is focused for real and its computed style read back (the field and the wrappers around it: Element Plus draws the frame on
     el-input__wrapper, not on the <input>). visual-design.html 层级与立体感 › 边缘线条: a focused text field only deepens its 1px border to ink2;
     no blue or primary frame, glow, thick outline or browser default outline. */
  const FIELD = 'input:not([type]), input[type=text], input[type=search], input[type=tel], input[type=email], input[type=number], input[type=password], input[type=url], input[type=date], input[type=time], input[type=datetime-local], input[type=month], input[type=week], textarea, select, [contenteditable=""], [contenteditable=true], [contenteditable=plaintext-only], [role=textbox], [role=combobox], [role=searchbox], [role=spinbutton]';
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = (c) => { if (!c) return null; cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return { r: d[0], g: d[1], b: d[2], a: d[3] / 255 }; };
  const chroma = (c) => Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b);
  const splitTop = (v) => { const parts = []; let depth = 0, cur = ''; for (const ch of v) { if (ch === '(') depth++; if (ch === ')') depth--; if (ch === ',' && depth === 0) { parts.push(cur.trim()); cur = ''; } else cur += ch; } if (cur.trim()) parts.push(cur.trim()); return parts; };
  const layersOf = (v) => (!v || v === 'none') ? [] : splitTop(v).map((t) => { const nums = (t.match(/-?\d*\.?\d+px/g) || []).map(parseFloat); return { text: t, inset: /\binset\b/.test(t), x: nums[0] || 0, y: nums[1] || 0, blur: nums[2] || 0, spread: nums[3] || 0, color: parse(t.replace(/-?\d*\.?\d+px/g, '').replace(/\binset\b/, '').trim()) }; });
  const snap = (n) => { const s = getComputedStyle(n); return { os: s.outlineStyle, ow: parseFloat(s.outlineWidth) || 0, oc: s.outlineColor, oo: parseFloat(s.outlineOffset) || 0, bs: s.boxShadow, bc: s.borderTopColor, bw: parseFloat(s.borderTopWidth) || 0 }; };
  const shown = (el) => { const r = el.getBoundingClientRect(); if (!r.width || !r.height) return false; for (let n = el; n; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || n.hasAttribute('inert')) return false; } return true; };
  const name = (n) => n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (typeof n.className === 'string' && n.className.trim() ? '.' + n.className.trim().split(/\s+/)[0] : '');
  const seen = (window.__luzFocusSeen = window.__luzFocusSeen || new Set());
  const fields = []; const sigs = new Set();
  document.querySelectorAll(FIELD).forEach((el) => {
    if (el.disabled || !shown(el)) return;
    const sig = name(el) + '|' + (el.getAttribute('type') || '') + '|' + (el.getAttribute('role') || '') + '|' + (el.parentElement ? name(el.parentElement) : '');
    if (seen.has(sig) || sigs.has(sig)) return; sigs.add(sig); fields.push([el, sig]);
  });
  const found = [];
  if (!fields.length) return found;
  const lock = document.createElement('style'); lock.textContent = '*,*::before,*::after{transition:none!important;animation:none!important}'; document.head.appendChild(lock);
  const prev = document.activeElement; if (prev && prev !== document.body && prev.blur) prev.blur();
  const frames = () => new Promise((done) => { let end = false; const fin = () => { if (!end) { end = true; done(); } }; requestAnimationFrame(() => requestAnimationFrame(fin)); setTimeout(fin, 120); });
  await frames();
  for (const [el, sig] of fields.slice(0, 40)) {
    seen.add(sig);
    const fr = el.getBoundingClientRect(); const chain = [el];
    for (let n = el.parentElement, i = 0; n && n !== document.body && n !== document.documentElement && i < 5; n = n.parentElement, i++) { if (n.getBoundingClientRect().height > Math.max(fr.height * 1.8, fr.height + 24)) break; chain.push(n); }
    const before = chain.map(snap);
    el.focus({ preventScroll: true });
    if (!el.matches(':focus')) continue;
    await frames();
    const issues = [];
    chain.forEach((n, i) => {
      const b = before[i], a = snap(n), who = (i ? '外层 ' : '') + name(n);
      if (a.os !== 'none' && a.os !== 'hidden' && a.ow > 0 && (a.os !== b.os || a.ow !== b.ow || a.oc !== b.oc)) {
        const c = parse(a.oc);
        if (a.os === 'auto') issues.push(who + ' 浏览器默认轮廓');
        else if (c && c.a >= 0.05 && chroma(c) > 40) issues.push(who + ' 彩色轮廓 ' + a.oc);
        else if (c && c.a >= 0.05 && (a.ow > 1 || a.oo > 0)) issues.push(who + ' 粗轮廓或外扩轮廓 ' + a.ow + 'px/偏移' + a.oo + 'px');
      }
      const old = new Set(layersOf(b.bs).map((l) => l.text));
      for (const l of layersOf(a.bs)) {
        if (old.has(l.text) || !l.color || l.color.a < 0.05) continue;
        if (chroma(l.color) > 40 && (l.blur > 0 || l.spread !== 0 || l.x !== 0 || l.y !== 0)) issues.push(who + ' 彩色框或光晕 ' + l.text);
        else if (!(l.x || l.y) && (l.spread > 1 || l.blur >= 4)) issues.push(who + ' 变粗的框或光晕 ' + l.text);
      }
      if (a.bw > b.bw + 0.01) issues.push(who + ' 边框变粗 ' + b.bw + 'px→' + a.bw + 'px');
      if (a.bw > 0 && a.bc !== b.bc) { const c = parse(a.bc); if (c && c.a >= 0.05 && chroma(c) > 40) issues.push(who + ' 边框变彩色 ' + a.bc); }
    });
    if (issues.length) found.push(name(el) + (el.getAttribute('type') ? '[' + el.getAttribute('type') + ']' : '') + '：' + issues.join('，'));
    el.blur();
  }
  if (prev && prev !== document.body && document.contains(prev) && prev.focus) prev.focus({ preventScroll: true });
  lock.remove();
  return found;
}
"""

RULES = r"""
() => {
  const bad = [];
  const unreadable = [];
  for (const sheet of document.styleSheets) { let rules; try { rules = sheet.cssRules; } catch (e) { if (sheet.href) unreadable.push(sheet.href); continue; } for (const rule of rules) {
    const walk = (r) => { if (r.style) { const t = r.style.transitionProperty, d = r.style.getPropertyValue('transition'); if (/(^|\s|,)all(\s|,|$)/.test(t || '') || /(^|\s)all\s/.test(d || '')) bad.push('transition: all in ' + r.selectorText); if (r.style.willChange && r.style.willChange !== 'auto') bad.push('will-change in ' + r.selectorText); for (const p of ['width', 'left', 'top', 'margin', 'padding']) { if ((t || '').split(',').map(s => s.trim()).includes(p)) bad.push('transition on layout property ' + p + ' in ' + r.selectorText); } if (/italic/.test(r.style.fontStyle || '')) bad.push('italic in ' + r.selectorText); } if (r.cssRules) for (const c of r.cssRules) walk(c); };
    walk(rule); } }
  return { bad, unreadable };
}
"""




def css_text_findings(href):
    """A linked style sheet on file:// cannot be read from the page: read the file and check the same rules on its text."""
    import re
    from urllib.parse import unquote, urlparse

    if not href.startswith("file:"):
        return []
    path = Path(unquote(urlparse(href).path.lstrip("/")))
    if not path.is_file():
        return []
    text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    out = []
    if re.search(r"transition\s*:[^;{}]*all", text):
        out.append(f"transition: all in {path.name}")
    if re.search(r"will-change\s*:\s*(?!auto)", text):
        out.append(f"will-change in {path.name}")
    if re.search(r"font-style\s*:\s*italic", text):
        out.append(f"italic in {path.name}")
    if re.search(r"transition(?:-property)?\s*:[^;{}]*(?:width|left|top|margin|padding)", text):
        out.append(f"transition on a layout property in {path.name}")
    return out


LIBRARIES = Path(__file__).resolve().parents[1] / "references" / "component-libraries.json"


def resolve_library(items):
    """Class prefixes of the chosen component libraries: registry ids, or a prefix written out (``el-``)."""
    if not items:
        return []
    known = json.loads(LIBRARIES.read_text(encoding="utf-8"))["libraries"]
    prefixes = []
    for item in items:
        if item in known:
            if not known[item].get("attr"):  # a library with attr (luz-kit) is read by that attribute, not by class prefix: see resolve_library_attrs
                prefixes += known[item]["prefix"]
        elif item.endswith("-") and len(item) > 1:
            prefixes.append(item)
        else:
            raise SystemExit(f"ERROR unknown component library {item!r}: use an id of references/component-libraries.json ({', '.join(known)}) or a prefix such as el-")
    return prefixes


def resolve_library_attrs(items):
    """Attributes that mark the component roots of the chosen libraries that have an ``attr`` in the registry (luz-kit: ``data-cid``); [] for all others."""
    if not items:
        return []
    known = json.loads(LIBRARIES.read_text(encoding="utf-8"))["libraries"]
    attrs = []
    for item in items:
        attr = known.get(item, {}).get("attr")
        if attr and attr not in attrs:
            attrs.append(attr)
    return attrs


DARK_PAGE_LUM = 0.3


def report(name, data, rules, library=None, min_components=0, min_font=14, scheme="light"):
    errors = []
    if scheme == "dark" and name == "initial" and data.get("pageLum", 0) > DARK_PAGE_LUM and data.get("centerLum", 0) > DARK_PAGE_LUM:
        errors.append(f"{name}: scheme dark: 页面底色仍是浅色，没有深色主题，或要用 --dark-attr / --dark-class 指定切换方式"
                      f"（body 背景亮度 {data['pageLum']:.2f}，屏幕中间 {data['centerLum']:.2f}，深色底应低于 {DARK_PAGE_LUM:g}）")
    for key, label in (("small", f"font size under {min_font}px"), ("italic", "italic text"), ("weight", "weight outside 400/600/700 (700 needs 22px+)"), ("contrast", "text contrast too low")):
        if data[key]:
            errors.append(f"{name}: {label}: " + "; ".join(data[key][:8]) + (f" ...{len(data[key])} in all" if len(data[key]) > 8 else ""))
    if data.get("stages"):
        import stage_ramp
        # the direction of the ramp is judged on the scheme this scan really shows: a walk may switch the theme (the page's own appearance control) after the page was opened
        really_dark = data.get("pageLum", 1) <= DARK_PAGE_LUM            # the page background (body, or the first opaque one up the chain) is a dark ground
        errors += [f"{name}: {e}" for e in stage_ramp.audit_items(data["stages"], data.get("stageTokens"), "dark" if really_dark else "light")]
    if data["overflowX"]:
        errors.append(f"{name}: horizontal page scroll")
    if len(data["fonts"]) > 1:
        errors.append(f"{name}: more than one font family: {data['fonts']}")
    if data["targets"]:
        errors.append(f"{name}: touch targets too small: " + "; ".join(data["targets"][:8]))
    if data.get("focusFrames"):
        errors.append(f"{name}: 聚焦框（文本框获得焦点时不得出现蓝色或主色框、光晕、粗描边、浏览器默认轮廓，聚焦只把 1 像素边加深到次要文字色）: " + "; ".join(data["focusFrames"][:8])
                      + (f" ...共 {len(data['focusFrames'])} 个" if len(data["focusFrames"]) > 8 else ""))
    if library:
        if data["foreign"]:
            errors.append(f"{name}: 自造控件（不来自组件库 {'、'.join(library)}）: " + "; ".join(data["foreign"][:8]) + (f" ...共 {len(data['foreign'])} 个" if len(data["foreign"]) > 8 else ""))
        if min_components and len(data["components"]) < min_components:
            errors.append(f"{name}: 页面里只有 {len(data['components'])} 种组件库（{'、'.join(library)}）的组件，"
                          f"本次显式要求至少 {min_components} 种；数量不代替逐控件来源核验")
    return errors + [f"{name}: {r}" for r in rules]


def main(argv):
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--reduced-motion", action="store_true")
    ap.add_argument("--walk")
    ap.add_argument("--library", action="append", default=[], metavar="ID|PREFIX", help="component library id from references/component-libraries.json, or a class prefix ending in '-'")
    ap.add_argument("--min-components", type=int, default=0, help="仅在本次合同明确要求时设置组件种类下限；默认不设配额")
    ap.add_argument("--no-focus-check", action="store_true", help="do not focus the text fields to look for a focus frame")
    ap.add_argument("--min-font", type=int, default=14, help="smallest text size in px; 14 for websites and reading pages (default), 12 for product interfaces (admin, mini-program, agent)")
    ap.add_argument("--scheme", choices=("light", "dark"), default="light", help="本次要验证的目标主题（prefers-color-scheme）；按功能合同选择，不默认要求双主题")
    ap.add_argument("--dark-attr", action="append", default=[], metavar="NAME=VALUE", help="with --scheme dark: set this attribute on <html> after load, for a page that switches by attribute (data-theme=dark)")
    ap.add_argument("--dark-class", action="append", default=[], metavar="NAME", help="with --scheme dark: add this class to <html> after load, for a page that switches by class (dark)")
    a = ap.parse_args(argv)
    prefixes = resolve_library(a.library)
    attrs = resolve_library_attrs(a.library)
    from playwright.sync_api import sync_playwright

    target = a.target if "://" in a.target else Path(a.target).resolve().as_uri()
    errors, found = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get("LUZ_AUDIT_CHANNEL", "msedge")) if os.environ.get("LUZ_AUDIT_CHANNEL") != "chromium" else pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": a.width, "height": a.height}, locale="zh-CN", reduced_motion="reduce" if a.reduced_motion else "no-preference",
                                  color_scheme=a.scheme)
        page = ctx.new_page()
        page.on("console", lambda m: found.append("console error: " + m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: found.append(f"page error: {e}"))
        page.goto(target)
        page.wait_for_load_state("load")
        page.wait_for_timeout(1500)
        if a.scheme == "dark" and (a.dark_attr or a.dark_class):
            for item in a.dark_attr:
                name, _, value = item.partition("=")
                page.evaluate("([n, v]) => document.documentElement.setAttribute(n, v)", [name.strip(), value.strip().strip("\"'") or "dark"])
            for name in a.dark_class:
                page.evaluate("(c) => document.documentElement.classList.add(c)", name.strip())
            page.wait_for_timeout(300)
        found_rules = page.evaluate(RULES)
        rules = list(found_rules['bad'])
        for href in found_rules['unreadable']:
            rules += css_text_findings(href)
        min_target = 40 if a.width < 700 else 24
        def scan():
            data = page.evaluate(SCAN, {"minTarget": min_target, "prefixes": prefixes, "attrs": attrs, "minFont": a.min_font})
            data["focusFrames"] = [] if a.no_focus_check else page.evaluate(FOCUS)
            return data

        errors += report("initial", scan(), rules, a.library, a.min_components, a.min_font, a.scheme)
        if a.walk:
            ns = {}
            exec(compile(Path(a.walk).read_text(encoding="utf-8"), a.walk, "exec"), ns)
            for label, data in ns["walk"](page, scan):
                errors += report(label, data, [], a.library, 0, a.min_font, a.scheme)
        ctx.close()
        browser.close()
    errors += found
    print(json.dumps(errors, ensure_ascii=False, indent=1) if errors else "audit: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
