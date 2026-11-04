#!/usr/bin/env python3
"""Build the style lab: one HTML page where a person switches three preset styles and mixes palette, icon style, shape, depth,
type scheme and motion personality, with live contrast and colour-discipline checks and export of the result.

    py -X utf8 scripts/make_style_lab.py --assets <dir with photo.webp, glass.webp, icons/*.webp> --out <style-lab.html> [--themes florist,b2b-graphite,...]

Colours come only from references/themes.json (light and dark), so the lab never invents a palette; the options and their rules are
the ones of references/token-system.md (the combinations the lab marks "待裁定" are the ones the standard does not allow yet).
The page is a single file: styles, scripts and the images (as data URIs) are inline, so it opens by double click.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEMES = ROOT / "references" / "themes.json"
TEMPLATE = ROOT / "references" / "style-lab.template.txt"

SHARED_KEYS = ["ink", "ink2", "ink3", "line", "success", "warning", "danger", "info", "price", "priceTint", "photo", "photo2"]
THEME_KEYS = ["label", "industry", "action", "actionPress", "actionTint", "canvas", "navBg", "accent", "accentTint"]
DARK_KEYS = ["canvas", "navBg", "surface", "action", "actionPress", "onAction", "actionText", "actionTint", "accent", "accentTint", "line"]
ICON_NAMES = ["bouquet", "plant", "giftbox", "vase", "scooter", "coupon", "bag", "heart"]


def data_uri(path: Path) -> str:
    mime = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def build_data(assets: Path, only: list[str] | None) -> dict:
    raw = json.loads(THEMES.read_text(encoding="utf-8"))
    themes = {}
    for tid, t in raw["themes"].items():
        if only and tid not in only:
            continue
        item = {k: t[k] for k in THEME_KEYS if k in t}
        item["dark"] = {k: t["dark"][k] for k in DARK_KEYS if k in t.get("dark", {})}
        themes[tid] = item
    shared = raw["shared"]
    light = {k: shared[k] for k in SHARED_KEYS if k in shared}
    light["surface"] = shared.get("surface", "#FFFFFF")
    dark = {k: shared["dark"][k] for k in SHARED_KEYS if k in shared["dark"]}
    icons = {}
    for name in ICON_NAMES:
        p = assets / "icons" / f"{name}.webp"
        if p.exists():
            icons[name] = data_uri(p)
    return {
        "themes": themes,
        "shared": {"light": light, "dark": dark},
        "assets": {"photo": data_uri(assets / "photo.webp"), "glass": data_uri(assets / "glass.webp"), "icons": icons},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--assets", required=True, help="directory with photo.webp, glass.webp and icons/<name>.webp")
    ap.add_argument("--out", required=True)
    ap.add_argument("--themes", default="", help="comma separated theme ids; default all themes of themes.json")
    a = ap.parse_args()
    data = build_data(Path(a.assets), [x for x in a.themes.split(",") if x] or None)
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB, {len(data['themes'])} themes, {len(data['assets']['icons'])} icons)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
