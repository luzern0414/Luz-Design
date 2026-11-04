#!/usr/bin/env python3
"""Rendered palette audit: the colours a product page really shows must come from its theme.

    py -X utf8 scripts/audit_palette.py <page.html> --theme <theme id> [--width 1440] [--click 登录] [--hash "#/dashboard"] [--max-extra 0]
        [--scheme light|dark [--dark-attr data-theme=dark] [--dark-class dark]]

visual-design.html 组件与组件库 (主题落地): a page keeps the one hue of its theme (the brand step and its tints) plus the shared status hues (success, warning,
danger, info, price); no hue is added for decoration (a purple bar series, teal icon blocks, pink avatars). The audit opens the page in a real
browser, reads the computed text, background, border, fill and stroke colours of every visible element, drops the neutrals, buckets the rest by hue
and reports every hue that is not a hue of the theme's own tokens. It also reports letter avatars (a name's first character in a coloured circle), which
the standard forbids. Canvas charts are not read: their palette comes from the theme in the first place.

Colours are read back through a canvas pixel, so oklch(), color-mix() and color(srgb ...) values count like hex ones.

``--scheme dark`` opens the page with prefers-color-scheme dark (visual-design.html 深色与浅色两套主题: a product front-end has a dark theme with the same hue budget). ``--dark-attr NAME=VALUE`` and
``--dark-class NAME`` (repeatable, only with --scheme dark) switch a page that reads an attribute or a class on <html> instead of the media query, as in audit_rendered.py. In the dark scheme a
colour is judged chromatic from lightness 0.02 up (a dark red ground at lightness 0.1 is a hue, not a neutral; the light scheme starts at 0.06), the neutral test stays the saturation, and the
hue budget is the light one plus the hues of themes.<id>.dark (action, actionPress, actionText, actionTint, accent, accentTint) and of shared.dark (the status colours, their tints and fills).

Exit code 1 when a hue outside the theme is found on more than --max-extra elements, or a letter avatar is found.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

THEMES = Path(__file__).resolve().parents[1] / "references" / "themes.json"
STATUS_KEYS = ("success", "successTint", "warning", "warningTint", "danger", "dangerTint", "info", "infoTint", "price", "priceTint")
THEME_KEYS = ("action", "actionPress", "actionTint", "accent", "accentTint")
CHROMA_MIN = 0.18       # HSL saturation below this is a neutral
HUE_TOLERANCE = 26      # degrees: tints and shades of one hue stay within it
LIGHT_FLOOR = {"light": 0.06, "dark": 0.02}   # HSL lightness above which a saturated colour counts as a hue; dark grounds are tinted at lightness 0.05–0.15
DARK_THEME_KEYS = ("action", "actionPress", "actionText", "actionTint", "accent", "accentTint")

COLLECT = """() => {
  const out = [], initials = [];
  /* any CSS colour (rgb, oklch, color-mix, color(srgb ...)) read back through a canvas pixel */
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = (c) => { if (!c || c === 'none') return null; cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return { r: d[0], g: d[1], b: d[2], a: d[3] / 255 }; };
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    const s = getComputedStyle(el); if (s.visibility === 'hidden' || s.display === 'none') continue;
    const where = el.tagName.toLowerCase() + '.' + [...el.classList].slice(0, 2).join('.');
    const area = r.width * r.height;
    const push = (kind, c) => { const q = parse(c); if (q && q.a > 0.5) out.push([kind, q.r, q.g, q.b, Math.round(area), where]); };
    push('bg', s.backgroundColor);
    if ([...el.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim())) push('text', s.color);
    if (parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none') push('border', s.borderTopColor);
    if (el instanceof SVGElement) { push('fill', s.fill); push('stroke', s.stroke); }
    if (/avatar|face|portrait/i.test(el.className && el.className.toString()) && !el.querySelector('img, svg, image') && !(el.tagName === 'IMG') && !/ghost|icon/i.test(el.className.toString())) {
      const t = (el.innerText || '').trim();
      if (t.length >= 1 && t.length <= 2 && /^[\\u4e00-\\u9fa5A-Za-z]+$/.test(t)) initials.push(where + ' "' + t + '"');
    }
  }
  return { colours: out, initials };
}"""


def hue_of(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    h, light, sat = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    return h * 360, light, sat


def is_chromatic(rgb: tuple[int, int, int], scheme: str = "light") -> bool:
    _, light, sat = hue_of(rgb)
    return sat >= CHROMA_MIN and LIGHT_FLOOR[scheme] < light < 0.97


def hex_rgb(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(value).strip())
    if not match:
        return None
    n = int(match.group(1), 16)
    return (n >> 16) & 255, (n >> 8) & 255, n & 255


def theme_hues(theme_id: str, path: Path = THEMES, scheme: str = "light") -> list[float]:
    """The hues of the theme's own colours: its brand steps and the shared status colours; in the dark scheme also the hues of its dark mapping
    (themes.<id>.dark and shared.dark: the lighter brand step, its dark tint, the status text colours, tints and fills)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if theme_id not in data["themes"]:
        raise SystemExit(f"ERROR unknown theme {theme_id!r}; choose one of {', '.join(data['themes'])}")
    theme, shared = data["themes"][theme_id], data["shared"]
    colours = [theme.get(k) for k in THEME_KEYS] + [shared.get(k) for k in STATUS_KEYS]
    if scheme == "dark":
        dark, shared_dark = theme.get("dark") or {}, shared.get("dark") or {}
        colours += [dark.get(k) for k in DARK_THEME_KEYS] + [shared_dark.get(k) for k in STATUS_KEYS + ("successFill", "warningFill", "dangerFill")]
    hues = []
    for value in colours:
        rgb = hex_rgb(value) if value else None
        if rgb and is_chromatic(rgb, "dark" if scheme == "dark" else "light"):
            hues.append(hue_of(rgb)[0])
    return hues


def hue_gap(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def off_theme(colours: list[list], allowed: list[float], scheme: str = "light") -> dict[int, dict]:
    """Chromatic colours of the page that are further than HUE_TOLERANCE from every hue of the theme, grouped by 30-degree hue bucket."""
    found: dict[int, dict] = {}
    for kind, r, g, b, area, where in colours:
        rgb = (int(r), int(g), int(b))
        if not is_chromatic(rgb, scheme):
            continue
        hue = hue_of(rgb)[0]
        if allowed and min(hue_gap(hue, h) for h in allowed) <= HUE_TOLERANCE:
            continue
        bucket = int(round(hue / 30)) % 12 * 30
        entry = found.setdefault(bucket, {"count": 0, "area": 0, "where": {}})
        entry["count"] += 1
        entry["area"] += area if kind in ("bg", "fill") else 0
        key = f"{kind} #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x} {where}"
        entry["where"][key] = entry["where"].get(key, 0) + 1
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="a local .html file or a file:// / http:// URL")
    ap.add_argument("--theme", required=True, help="theme id of references/themes.json")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--click", default="", help="button to click first (a login button)")
    ap.add_argument("--hash", default="", help="route to open, e.g. '#/dashboard'")
    ap.add_argument("--max-extra", type=int, default=0, help="elements allowed in a hue outside the theme (default 0)")
    ap.add_argument("--scheme", choices=("light", "dark"), default="light", help="colour scheme the page is opened with (prefers-color-scheme); a product front-end is audited in both")
    ap.add_argument("--dark-attr", action="append", default=[], metavar="NAME=VALUE", help="with --scheme dark: set this attribute on <html> after load (data-theme=dark)")
    ap.add_argument("--dark-class", action="append", default=[], metavar="NAME", help="with --scheme dark: add this class to <html> after load (dark)")
    args = ap.parse_args(argv)

    from playwright.sync_api import sync_playwright

    allowed = theme_hues(args.theme, scheme=args.scheme)
    url = args.page if re.match(r"^(file|https?)://", args.page) else Path(args.page).resolve().as_uri()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": args.width, "height": 900 if args.width > 700 else 844}, locale="zh-CN", color_scheme=args.scheme)
        page.goto(url + ("?skip-login" if args.hash else "") + args.hash)
        page.wait_for_timeout(1800)
        if args.scheme == "dark" and (args.dark_attr or args.dark_class):
            for item in args.dark_attr:
                name, _, value = item.partition("=")
                page.evaluate("([n, v]) => document.documentElement.setAttribute(n, v)", [name.strip(), value.strip().strip("\"'") or "dark"])
            for name in args.dark_class:
                page.evaluate("(c) => document.documentElement.classList.add(c)", name.strip())
            page.wait_for_timeout(300)
        if args.click:
            page.get_by_role("button", name=args.click).first.click()
            page.wait_for_timeout(1800)
        got = page.evaluate(COLLECT)
        browser.close()

    extra = off_theme(got["colours"], allowed, args.scheme)
    count = sum(e["count"] for e in extra.values())
    problems = []
    if count > args.max_extra:
        for bucket in sorted(extra):
            top = sorted(extra[bucket]["where"].items(), key=lambda kv: -kv[1])[:3]
            problems.append(f"hue near {bucket} degrees is not a hue of theme {args.theme}: {extra[bucket]['count']} places, e.g. " + "; ".join(k for k, _ in top))
    if got["initials"]:
        problems.append("letter avatar (a name's first character in a circle) is not allowed: " + "; ".join(got["initials"][:4]))
    if problems:
        print(json.dumps(problems, ensure_ascii=False, indent=1))
        return 1
    print("audit palette: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
