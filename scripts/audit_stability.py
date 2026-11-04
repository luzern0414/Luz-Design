#!/usr/bin/env python3
"""Stable display audit: a page must not jump, flash or reflow while it loads and while the person moves through it.

    py -X utf8 scripts/audit_stability.py <page.html or URL> [--width 1440] [--scheme light|dark] [--hash "#/orders" ...] [--click 登录] [--settle 2500] [--max-cls 0.05]

visual-design.html 稳定显示. The audit opens the page in a real browser and measures what the person would see:
  1. Layout shift: the Layout Instability API (`layout-shift` entries that are not caused by input), summed per page load and per route (--hash, repeatable); the
     elements that moved most are named. More than --max-cls (default 0.05, the "good" bound of Web Vitals is 0.1) is reported.
  2. Flash: the colour of the ground (the first non-transparent background of <html> or <body>) is sampled on every animation frame from the first paint; a
     jump of lightness of 0.3 or more after the first painted frame (a white flash before the dark scheme is applied, or the reverse) is reported.
  3. Scroll-bar jump: the width of the viewport content area (`documentElement.clientWidth`) must not change after the first painted frame, which it does
     when a scroll bar appears once the content has loaded (`scrollbar-gutter: stable` or a reserved gutter prevents it).
  4. Web fonts: a page that loads web fonts reports each `@font-face` whose text swapped after first paint without a fallback metric match (`size-adjust`
     or `font-display: optional`); the standard uses the system font stack, so a page without web fonts passes this at once.
Exit code 1 when anything is reported.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INIT = """
(() => {
  const state = window.__stab = { shifts: [], frames: [], widths: [], t0: performance.now() };
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        if (e.hadRecentInput) continue;
        const src = (e.sources || []).map((s) => { const n = s.node; return n && n.nodeType === 1 ? (n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + '.' + [...n.classList].slice(0, 2).join('.')) : 'text'; });
        state.shifts.push({ t: Math.round(e.startTime), value: e.value, src });
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (err) { state.noObserver = true; }
  const parse = (c) => { const m = c && c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lightness = (q) => { const f = (x) => { x /= 255; return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(q.r) + 0.7152 * f(q.g) + 0.0722 * f(q.b); };
  const ground = () => {
    for (const el of [document.body, document.documentElement]) {
      if (!el) continue;
      const q = parse(getComputedStyle(el).backgroundColor);
      if (q && q.a > 0.5) return lightness(q);
    }
    return null;
  };
  const tick = () => {
    const t = Math.round(performance.now() - state.t0);
    const root = document.documentElement;
    state.frames.push({ t, ground: ground(), width: root ? root.clientWidth : 0, dark: root ? root.classList.contains('dark') || root.dataset.theme === 'dark' : false });
    if (t < 6000) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
})();
"""

TOP = """() => { const s = window.__stab; return { shifts: s.shifts.map((x) => ({ ...x })), frames: s.frames.slice(), noObserver: !!s.noObserver } }"""
FONTS = """() => [...document.fonts].map((f) => ({ family: f.family, status: f.status, display: f.display }))"""
SIZE_ADJUST = re.compile(r"size-adjust|font-display\s*:\s*optional", re.I)


def summarise(shifts: list[dict], since: int = 0) -> tuple[float, list[str]]:
    items = [s for s in shifts if s["t"] >= since]
    total = sum(s["value"] for s in items)
    names: dict[str, float] = {}
    for s in items:
        for name in s["src"] or ["unknown"]:
            names[name] = names.get(name, 0) + s["value"]
    top = [f"{n} ({v:.3f})" for n, v in sorted(names.items(), key=lambda kv: -kv[1])[:4]]
    return total, top


def ground_flash(frames: list[dict]) -> str | None:
    seen = [f for f in frames if f["ground"] is not None]
    for a, b in zip(seen, seen[1:]):
        if abs(a["ground"] - b["ground"]) >= 0.3:
            return f"the ground changes from lightness {a['ground']:.2f} to {b['ground']:.2f} at {b['t']} ms (a flash before the scheme is applied)"
    return None


def width_jump(frames: list[dict]) -> str | None:
    widths = [(f["t"], f["width"]) for f in frames if f["width"]]
    for (t0, w0), (t1, w1) in zip(widths, widths[1:]):
        if w0 != w1:
            return f"the width of the content area changes from {w0} to {w1} px at {t1} ms (a scroll bar appears after the first frame; reserve it with scrollbar-gutter: stable)"
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--scheme", choices=("light", "dark"), default="light")
    ap.add_argument("--hash", action="append", default=[], help="routes to open one after the other (each measured on its own)")
    ap.add_argument("--click", default="", help="a button to click first, e.g. a login button")
    ap.add_argument("--settle", type=int, default=2500, help="milliseconds to wait after each load")
    ap.add_argument("--max-cls", type=float, default=0.05)
    args = ap.parse_args(argv)

    from playwright.sync_api import sync_playwright

    url = args.page if re.match(r"^(file|https?)://", args.page) else Path(args.page).resolve().as_uri()
    problems: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", ignore_default_args=["--hide-scrollbars"])   # a scroll bar takes room, as it does for a person
        context = browser.new_context(viewport={"width": args.width, "height": 900 if args.width > 700 else 844}, color_scheme=args.scheme, locale="zh-CN")
        page = context.new_page()
        page.add_init_script(INIT)
        page.goto(url + ("?skip-login" if args.hash else ""))
        page.wait_for_timeout(args.settle)
        if args.click:
            page.get_by_role("button", name=args.click).first.click()
            page.wait_for_timeout(args.settle)
        data = page.evaluate(TOP)
        if data["noObserver"]:
            problems.append("this browser has no Layout Instability API: layout shift could not be measured")
        total, top = summarise(data["shifts"])
        if total > args.max_cls:
            problems.append(f"layout shift {total:.3f} on load is above {args.max_cls}: " + "; ".join(top))
        flash = ground_flash(data["frames"])
        if flash:
            problems.append(flash)
        jump = width_jump(data["frames"])
        if jump:
            problems.append(jump)
        for route in args.hash:
            before = len(data["shifts"])
            now = page.evaluate("Math.round(performance.now() - window.__stab.t0)")
            page.evaluate("(h) => { location.hash = h }", route)
            page.wait_for_timeout(args.settle)
            after = page.evaluate(TOP)
            total, top = summarise(after["shifts"], since=now)
            if total > args.max_cls:
                problems.append(f"layout shift {total:.3f} when opening {route} is above {args.max_cls}: " + "; ".join(top))
        fonts = page.evaluate(FONTS)
        web = [f for f in fonts if f["status"] != "unloaded"]
        if web and not SIZE_ADJUST.search(page.content()):
            problems.append("web fonts load on this page (" + ", ".join(sorted({f["family"] for f in web})[:3]) + ") without size-adjust or font-display: optional; the standard uses the system font stack")
        browser.close()
    if problems:
        print(json.dumps(problems, ensure_ascii=False, indent=1))
        return 1
    print("audit stability: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
