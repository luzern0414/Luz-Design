"""Visual regression of the component library: screenshots and computed styles of every component, then a comparison.

    py -X utf8 references/component-library/tools/visual_regression.py capture --html LIB.html --out DIR [--scheme light|dark] [--widths 1500,390]
    py -X utf8 references/component-library/tools/visual_regression.py compare BASE_DIR NEW_DIR [--report FILE]

``capture`` opens the built library in Microsoft Edge (Playwright) at each width, walks every category of both domains and saves, per width:

  * ``<id>.png``  a screenshot of the whole card of each component (stage and caption), plus ``_guide-<dom>-<cat>.png`` for the "怎么选" table of
    each category and a few pieces of the page itself (``_bar``, ``_index``, ``_combo``);
  * ``styles.json.gz``  size and the main computed styles (colours, borders, shadows, fills, fonts) of every element of every card.

The page is made deterministic first: a seeded ``Math.random``, a frozen ``Date``, no timers that keep running, no CSS animation or transition. The same
build captured twice must compare as identical (that is the first thing to check about a baseline).

``compare`` reads two capture directories and judges each file against the thresholds below. The light theme must stay as it was before the dark layer
was added, so the thresholds are set for "no difference to the eye": a handful of anti-aliasing pixels at most. A component that is over a threshold, or
whose element boxes moved, is listed with the reason; ``compare`` exits 1 if there is any.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------------------------------------
# Thresholds ("no difference to the eye"). Pixel differences are measured per channel on 0..255, after the screenshots are decoded.
# ----------------------------------------------------------------------------------------------------------------------------------------
MEAN_DIFF_MAX = 0.35        # mean absolute difference over all pixels and channels
CHANGED_SHARE_MAX = 0.004   # share of pixels whose largest channel difference is above CHANGED_LEVEL (0.4 %)
CHANGED_LEVEL = 6           # a difference of 6/255 in one channel is below what the eye sees on a flat area
BOX_TOLERANCE = 0.6         # px: an element box that moved or grew by more than this is a layout change

WIDTHS = (1500, 390)
SEED_AND_FREEZE = r"""
(() => {
  let s = 20260304;
  const rnd = () => { s = (s * 1664525 + 1013904223) % 4294967296; return s / 4294967296; };
  Math.random = rnd;
  window.__resetSeed = () => { s = 20260304; };
  const FIXED = Date.UTC(2026, 10, 4, 10, 30, 0);
  const RealDate = Date;
  class FakeDate extends RealDate {
    constructor(...a) { if (a.length) super(...a); else super(FIXED); }
    static now() { return FIXED; }
  }
  window.Date = FakeDate;
  window.setInterval = () => 0;
  const style = document.createElement('style');
  style.textContent = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important;scroll-behavior:auto!important}.bar{position:static!important;backdrop-filter:none!important}';
  document.addEventListener('DOMContentLoaded', () => document.head.appendChild(style));
})();
"""

PROPS = ["color", "backgroundColor", "backgroundImage", "borderTopColor", "borderRightColor", "borderBottomColor", "borderLeftColor",
         "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth", "boxShadow", "outlineColor", "textShadow", "fill", "stroke",
         "opacity", "filter", "fontSize", "fontWeight", "lineHeight", "display", "textDecorationColor", "caretColor"]

SNAPSHOT = r"""
(props) => {
  const hash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return (h >>> 0).toString(36); };
  const clean = (v) => (v || '').replace(/url\("?data:[^)]*\)/g, (m) => 'url(data:' + hash(m) + ')');
  const out = {};
  for (const tc of document.querySelectorAll('#content .tc')) {
    const box = tc.getBoundingClientRect(), els = [];
    for (const e of [tc, ...tc.querySelectorAll('*')]) {
      const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      els.push([e.tagName.toLowerCase() + '.' + String(e.getAttribute('class') || '').split(/\s+/).slice(0, 2).join('.'),
        Math.round((r.left - box.left) * 10) / 10, Math.round((r.top - box.top) * 10) / 10, Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10,
        ...props.map((p) => clean(cs[p]))]);
    }
    out[tc.id] = els;
  }
  return out;
}
"""

SLOW_CATEGORIES = {"CHART", "DATA"}


def categories(page) -> list[tuple[str, str]]:
    return page.evaluate("() => { const out = []; for (const dom of ['mp', 'ad']) for (const [c] of TABS_ALL[dom]) if (c !== 'COMBO' && inCat(dom, c).length) out.push([dom, c]); return out; }")


def render(page, dom: str, cat: str) -> None:
    page.evaluate("([dom, cat]) => { window.__resetSeed && window.__resetSeed(); S.dom = dom; S.cat = cat; S.q = ''; renderAll(); window.scrollTo(0, 0); }", [dom, cat])
    page.wait_for_timeout(1100 if cat in SLOW_CATEGORIES else 80)  # charts tween with requestAnimationFrame for about a second


def capture(html: Path, out: Path, scheme: str = "light", widths=WIDTHS, appearance: str | None = None) -> dict:
    """Capture every card at each width. ``appearance`` ('light', 'dark' or None) calls ``setAppearance`` of a build that has it."""
    from playwright.sync_api import sync_playwright

    html, out = Path(html).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        for width in widths:
            wdir = out / str(width)
            wdir.mkdir(parents=True, exist_ok=True)
            ctx = browser.new_context(viewport={"width": width, "height": 900}, locale="zh-CN", color_scheme=scheme, has_touch=width < 700, device_scale_factor=1)
            ctx.add_init_script(SEED_AND_FREEZE)
            page = ctx.new_page()
            errors: list[str] = []
            page.on("console", lambda m, errors=errors: errors.append(m.text[:200]) if m.type == "error" else None)
            page.on("pageerror", lambda e, errors=errors: errors.append("pageerror " + str(e)[:200]))
            page.goto(html.as_uri())
            page.wait_for_function("typeof BLOCKS !== 'undefined' && document.querySelectorAll('.tc, .cmbw').length > 0", timeout=20000)
            if appearance:
                page.evaluate("(m) => window.setAppearance(m)", appearance)
            styles: dict = {}
            shots = 0
            for dom, cat in categories(page):
                render(page, dom, cat)
                guide = page.locator("#content .guide").first
                if guide.count():
                    guide.screenshot(path=str(wdir / f"_guide-{dom}-{cat}.png"))
                    shots += 1
                for tc in page.locator("#content .tc").all():
                    cid = tc.get_attribute("id")
                    tc.screenshot(path=str(wdir / f"{cid}.png"))
                    shots += 1
                styles.update(page.evaluate(SNAPSHOT, PROPS))
            # a few pieces of the page itself
            S_keys = [("INDEX", "mp"), ("COMBO", "mp")]
            for cat, dom in S_keys:
                page.evaluate("([dom, cat]) => { window.__resetSeed && window.__resetSeed(); S.dom = dom; S.cat = cat; S.q = ''; renderAll(); window.scrollTo(0, 0); }", [dom, cat])
                page.wait_for_timeout(60)
                sel = "#content .cmbw" if cat == "COMBO" else "#content .guide"
                loc = page.locator(sel).first
                if loc.count():
                    loc.screenshot(path=str(wdir / f"_{cat.lower()}.png"))
                    shots += 1
            page.evaluate("() => { S.dom = 'mp'; S.cat = 'ENT'; S.q = ''; renderAll(); window.scrollTo(0, 0); }")
            page.locator(".bar").first.screenshot(path=str(wdir / "_bar.png"))
            shots += 1
            with gzip.open(wdir / "styles.json.gz", "wt", encoding="utf-8") as f:
                json.dump({"props": PROPS, "cards": styles}, f, ensure_ascii=False, separators=(",", ":"))
            (wdir / "errors.json").write_text(json.dumps(errors, ensure_ascii=False), encoding="utf-8")
            summary[width] = {"cards": len(styles), "screenshots": shots, "errors": errors}
            ctx.close()
        browser.close()
    return summary


# ----------------------------------------------------------------------------------------------------------------------------------------
# Compare
# ----------------------------------------------------------------------------------------------------------------------------------------


def image_diff(a: Path, b: Path) -> dict:
    import numpy as np
    from PIL import Image

    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return {"size": [ia.size, ib.size], "mean": 255.0, "share": 1.0, "worst": 255}
    xa, xb = np.asarray(ia, dtype=np.int16), np.asarray(ib, dtype=np.int16)
    d = np.abs(xa - xb)
    return {"mean": float(d.mean()), "share": float((d.max(axis=2) > CHANGED_LEVEL).mean()), "worst": int(d.max())}


def judge(diff: dict) -> bool:
    return "size" not in diff and diff["mean"] <= MEAN_DIFF_MAX and diff["share"] <= CHANGED_SHARE_MAX


def load_styles(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


COLOUR_RX = re.compile(r"rgba?\(([^)]*)\)|color\(srgb ([^)]*)\)")
COLOUR_TOL = 6      # levels per channel: a computed colour that differs by less is the same colour to the eye (a grey merged into the nearest token; the largest in the library is 6)
ALPHA_TOL = 0.03


def parse_colour(m) -> tuple[float, float, float, float]:
    if m.group(1) is not None:
        parts = [x.strip() for x in re.split(r"[,/\s]+", m.group(1).strip()) if x.strip()]
        r, g, b = (float(x) for x in parts[:3])
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return r, g, b, a
    parts = [x for x in re.split(r"[/\s]+", m.group(2).strip()) if x]
    r, g, b = (float(x) * 255 for x in parts[:3])
    a = float(parts[3]) if len(parts) > 3 else 1.0
    return r, g, b, a


def split_colours(value: str) -> tuple[str, list]:
    cols: list = []

    def sub(m):
        cols.append(parse_colour(m))
        return "\u0001"

    return re.sub(r"\s+", " ", COLOUR_RX.sub(sub, value)), cols


def same_value(a: str, b: str) -> bool:
    """Computed values are the same when their text is the same once colours are set aside and the colours are within the tolerance."""
    if a == b:
        return True
    ta, ca = split_colours(a)
    tb, cb = split_colours(b)
    if ta != tb or len(ca) != len(cb):
        return False
    return all((x[3] < 0.01 and y[3] < 0.01) or (max(abs(x[0] - y[0]), abs(x[1] - y[1]), abs(x[2] - y[2])) <= COLOUR_TOL and abs(x[3] - y[3]) <= ALPHA_TOL) for x, y in zip(ca, cb))


def compare_styles(base: dict, new: dict, limit: int = 6) -> dict:
    """Per card: element count, boxes that moved, and the computed values that differ (grouped, with a few examples)."""
    props = base["props"]
    result = {}
    for cid, old_els in base["cards"].items():
        new_els = new["cards"].get(cid)
        if new_els is None:
            result[cid] = {"missing": True}
            continue
        if len(new_els) != len(old_els):
            result[cid] = {"count": [len(old_els), len(new_els)]}
            continue
        moved, changed = [], {}
        for i, (o, n) in enumerate(zip(old_els, new_els)):
            if any(abs(o[k] - n[k]) > BOX_TOLERANCE for k in (1, 2, 3, 4)):
                moved.append((i, o[0], o[1:5], n[1:5]))
            for j, p in enumerate(props):
                if not same_value(o[5 + j], n[5 + j]):
                    changed.setdefault(p, []).append((i, o[0], o[5 + j], n[5 + j]))
        if moved or changed:
            result[cid] = {"moved": moved[:limit], "moved_n": len(moved), "changed": {p: {"n": len(v), "e": v[:limit]} for p, v in changed.items()}}
    return result


def compare(base_dir: Path, new_dir: Path, report: Path | None = None) -> dict:
    out = {"images": {}, "styles": {}, "bad_images": [], "bad_styles": [], "files": 0, "worst_mean": 0.0, "worst_share": 0.0, "missing": []}
    for wdir in sorted(p for p in base_dir.iterdir() if p.is_dir()):
        width = wdir.name
        ndir = new_dir / width
        for png in sorted(wdir.glob("*.png")):
            other = ndir / png.name
            key = f"{width}/{png.stem}"
            if not other.exists():
                out["missing"].append(key)
                continue
            d = image_diff(png, other)
            out["files"] += 1
            if "size" not in d:
                out["worst_mean"] = max(out["worst_mean"], d["mean"])
                out["worst_share"] = max(out["worst_share"], d["share"])
            if not judge(d):
                out["bad_images"].append((key, d))
            out["images"][key] = d
        if (wdir / "styles.json.gz").exists() and (ndir / "styles.json.gz").exists():
            s = compare_styles(load_styles(wdir / "styles.json.gz"), load_styles(ndir / "styles.json.gz"))
            out["styles"][width] = s
            out["bad_styles"] += [(f"{width}/{cid}", v) for cid, v in s.items()]
    if report:
        report.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--html", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--scheme", default="light", choices=["light", "dark", "no-preference"])
    c.add_argument("--widths", default="1500,390")
    c.add_argument("--appearance", choices=["light", "dark", "system"])
    k = sub.add_parser("compare")
    k.add_argument("base")
    k.add_argument("new")
    k.add_argument("--report")
    args = ap.parse_args(argv)
    if args.cmd == "capture":
        s = capture(Path(args.html), Path(args.out), args.scheme, tuple(int(x) for x in args.widths.split(",")), args.appearance)
        for w, v in s.items():
            print(w, v["cards"], "cards", v["screenshots"], "screenshots", "errors:", v["errors"][:3])
        return 0
    r = compare(Path(args.base).resolve(), Path(args.new).resolve(), Path(args.report).resolve() if args.report else None)
    print(f"{r['files']} images compared; worst mean diff {r['worst_mean']:.3f}, worst changed share {r['worst_share']:.4f}; missing {len(r['missing'])}")
    print(f"images over threshold: {len(r['bad_images'])}; cards with computed-style changes: {len(r['bad_styles'])}")
    for key, d in r["bad_images"][:30]:
        print("  image", key, d)
    for key, v in r["bad_styles"][:30]:
        print("  style", key, {k2: (v2 if k2 in ('missing', 'count', 'moved_n') else {p: x['n'] for p, x in v2.items()}) for k2, v2 in v.items() if k2 != 'moved'})
    return 1 if r["bad_images"] or r["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
