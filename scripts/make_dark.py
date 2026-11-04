#!/usr/bin/env python3
"""Derive the dark mapping of references/themes.json from the light mapping (visual-design.html 深色与浅色两套主题).

    py -X utf8 scripts/make_dark.py                 print what would change (dry run)
    py -X utf8 scripts/make_dark.py --write         write themes.<id>.dark for every theme and shared.dark into themes.json
    py -X utf8 scripts/make_dark.py --write --keep xiangcai --keep florist     leave those themes' dark maps as they are
    py -X utf8 scripts/make_dark.py --check         the stored dark maps pass check_contrast's dark rules (same as check_contrast.py)

The dark theme is a second set of tokens, not an inversion: a dark ground and a lifted surface that keep the theme's hue at very low chroma,
the brand step at the same hue and a luminance where white text still reaches 4.5:1, a lighter step of the same hue for brand-coloured text and
icons (4.5:1 and more on every dark ground), and dark low-saturation tints under the status and accent colours. Everything is derived in OKLCH
(hue and chroma of the light value, lightness solved against the contrast target) and gamut-clamped to sRGB by lowering chroma only.
The output is a first draft: check_contrast.py judges it and a person may tune any value afterwards (--keep protects the tuned themes).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import check_contrast as cc

THEMES = Path(__file__).resolve().parents[1] / "references" / "themes.json"
WHITE = "#FFFFFF"

# ---- OKLab (Ottosson, 2020) ------------------------------------------------------------------------------------------------------------


def _to_linear(v: float) -> float:
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _to_srgb(v: float) -> float:
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def hex_to_oklch(color: str) -> tuple[float, float, float]:
    r, g, b = (_to_linear(v) for v in cc.rgb(color))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    lightness = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return lightness, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def _oklch_to_linear(lightness: float, chroma: float, hue: float) -> tuple[float, float, float]:
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    l = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def oklch_hex(lightness: float, chroma: float, hue: float) -> str:
    """The sRGB colour of an OKLCH triple; chroma is lowered (lightness and hue kept) until the colour fits the gamut."""
    def inside(c: float) -> bool:
        return all(-1e-4 <= v <= 1 + 1e-4 for v in _oklch_to_linear(lightness, c, hue))

    if not inside(0.0):
        lightness = max(0.0, min(1.0, lightness))
    lo, hi = 0.0, chroma
    if inside(chroma):
        lo = chroma
    else:
        for _ in range(28):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(mid) else (lo, mid)
    rgb = _oklch_to_linear(lightness, lo, hue)
    return "#%02X%02X%02X" % tuple(round(_to_srgb(v) * 255) for v in rgb)


def solve(hue: float, chroma: float, ok, *, highest: bool, lo: float = 0.04, hi: float = 0.98) -> str:
    """The lightest (highest=True) or darkest colour of this hue and chroma for which ok(hex) holds; ok must hold towards one end of lightness."""
    best = None
    for _ in range(40):
        mid = (lo + hi) / 2
        color = oklch_hex(mid, chroma, hue)
        if ok(color):
            best = color
            lo, hi = (mid, hi) if highest else (lo, mid)
        else:
            lo, hi = (lo, mid) if highest else (mid, hi)
    if best is None:
        raise ValueError(f"no colour of hue {hue:.0f} chroma {chroma:.3f} satisfies the target")
    return best


def mix_white(color: str, percent: float) -> str:
    """color-mix(in srgb, color, white percent%)."""
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * percent / 100) for c in cc.rgb(color))


# ---- the dark mapping ------------------------------------------------------------------------------------------------------------------

# Tokens shared by every theme. ink is the warm off-white of the rule page (check_contrast.DARK_INK); the others are solved, not typed.
DARK_INK = "#F5EFEA"
INK2_TARGET, INK3_TARGET = 8.0, 5.2        # against the lightest ground a text sits on (the 4th lift of the darkest tinted surface is checked too)
FILL_TARGET = 4.6                           # white text on a solid fill: 4.5 plus a margin for the 8-bit rounding
SURFACE_MIX = {"level0": 0, "level1": 0, "level2": 5, "level3": 8, "level4": 11}

STATUS = {   # light key -> (tint key, chroma ceiling of the dark text colour, chroma of the dark tint)
    "success": ("successTint", 0.15, 0.045), "warning": ("warningTint", 0.15, 0.05), "danger": ("dangerTint", 0.17, 0.05),
    "info": ("infoTint", 0.12, 0.045), "price": ("priceTint", 0.19, 0.05),
}
# statuses that also carry white text on a solid fill (visual-design.html 配色: white text only on action / success / danger / warning)
FILLED = ("success", "warning", "danger")

DARK_ELEVATION = {
    "note": "深色下阴影几乎看不出，层级主要靠更亮的表面：level0 是页面底（dark.canvas），level1 起是卡片面（dark.surface），surfaceMix 是再往该主题 dark.surface 里混入的白色百分比"
            "（等价于 color-mix(in srgb, 表面色, white 百分比)），level2 悬浮卡片、level3 下拉与吸顶栏、level4 对话框与抽屉，浮起的面比底面更亮；"
            "阴影仍只向下、两层、远处更大更柔，但颜色为黑、透明度可到 0.5，只作辅助；hairline 是白色发丝线（卡片边、分隔线），hairlineStrong 是可点击卡片悬停时的边线；"
            "highlight 是浅底卡的内顶部淡高光，highlightSolid 是品牌主卡与主按钮等实色面的内顶部高光（白 16%–24%）；scrim 为黑色 60% 的遮罩；"
            "focusRing 是键盘焦点轮廓的宽度（2 像素），色取正文色 dark ink 或 ink2、外移 2 像素，不用主色。",
    "surfaceMix": dict(SURFACE_MIX),
    "level1": "0 1px 2px rgba(0,0,0,.40), 0 2px 6px rgba(0,0,0,.28)",
    "level2": "0 2px 4px rgba(0,0,0,.40), 0 8px 16px rgba(0,0,0,.32)",
    "level3": "0 4px 8px rgba(0,0,0,.40), 0 12px 24px rgba(0,0,0,.36)",
    "level4": "0 8px 16px rgba(0,0,0,.44), 0 24px 48px rgba(0,0,0,.40)",
    "hairline": "rgba(255,255,255,.10)",
    "hairlineStrong": "rgba(255,255,255,.18)",
    "highlight": "inset 0 1px 0 rgba(255,255,255,.06)",
    "highlightSolid": "inset 0 1px 0 rgba(255,255,255,.2)",
    "scrim": "rgba(0,0,0,.6)",
    "focusRing": "0 0 0 2px",
    "buttonEdge": "0 1px 0",
}

# Hand-set maps (Tailwind CSS zinc steps, which the light graphite theme is already built from): a light neutral button with dark text is how a
# neutral theme reads in the dark; deriving it would give a mid-grey button.
OVERRIDES: dict[str, dict] = {
    "b2b-graphite": {
        "canvas": "#09090B", "navBg": "#18181B", "surface": "#18181B", "action": "#E4E4E7", "actionPress": "#D4D4D8",
        "onAction": "#18181B", "actionText": "#E4E4E7", "actionTint": "#27272A", "accent": "#60A5FA", "accentTint": "#172554",
        "line": "#3F3F46",
    },
}


def hue_chroma(color: str) -> tuple[float, float, float]:
    lightness, chroma, hue = hex_to_oklch(color)
    return hue, chroma, lightness


def derive_shared(shared: dict, surfaces: list[str]) -> dict:
    """shared.dark: ink tones solved against the lightest dark ground, status text colours and fills, tints, sage, photo placeholders, elevation."""
    # the lightest ground any text sits on: a theme's dark surface lifted to level4
    grounds = [mix_white(surface, SURFACE_MIX["level4"]) for surface in surfaces]
    ink2 = solve(30, 0.012, lambda c: min(cc.contrast(c, g) for g in grounds) >= INK2_TARGET, highest=False)
    ink3 = solve(30, 0.010, lambda c: min(cc.contrast(c, g) for g in grounds) >= INK3_TARGET, highest=False)
    out: dict = {"ink": DARK_INK, "ink2": ink2, "ink3": ink3}
    tint_grounds = {}
    for key, (tint_key, ceiling, tint_chroma) in STATUS.items():
        hue, chroma, _ = hue_chroma(shared[key])
        tint = oklch_hex(0.27, tint_chroma, hue)
        tint_grounds[key] = tint
        text = solve(hue, min(chroma, ceiling), lambda c, tint=tint: cc.contrast(c, tint) >= 5.5 and min(cc.contrast(c, g) for g in grounds) >= 5.5,
                     highest=False)
        out[key] = text
        out[tint_key] = tint
        if key in FILLED:
            out[key + "Fill"] = solve(hue, chroma * 0.95, lambda c: cc.contrast(WHITE, c) >= FILL_TARGET, highest=True)
    hue, chroma, _ = hue_chroma(shared["sage"])
    out["sageTint"] = oklch_hex(0.27, 0.03, hue)
    out["sage"] = solve(hue, max(chroma, 0.05), lambda c: cc.contrast(c, out["sageTint"]) >= 5.5 and min(cc.contrast(c, g) for g in grounds) >= 5.5,
                        highest=False)
    for key, level in (("photo", 0.30), ("photo2", 0.27)):
        hue, chroma, _ = hue_chroma(shared[key])
        out[key] = oklch_hex(level, min(chroma, 0.03), hue)
    out["elevation"] = json.loads(json.dumps(DARK_ELEVATION))
    # keep the dict order of the rule page: colours first, elevation last
    return {k: out[k] for k in ("ink", "ink2", "ink3", "success", "successTint", "successFill", "warning", "warningTint", "warningFill",
                                "danger", "dangerTint", "dangerFill", "info", "infoTint", "price", "priceTint", "sage", "sageTint", "photo", "photo2", "elevation")}


def derive_theme(theme_id: str, t: dict, shared: dict) -> dict:
    """themes.<id>.dark: the keys canvas, navBg, surface, action, actionPress, actionTint, accent, accentTint, line plus onAction and actionText."""
    if theme_id in OVERRIDES:
        return dict(OVERRIDES[theme_id])
    hue, chroma, _ = hue_chroma(t["action"])
    canvas_chroma = 0.012 if cc.chroma(t["canvas"]) <= 2 else 0.022
    canvas = oklch_hex(0.175, canvas_chroma, hue)
    surface = oklch_hex(0.23, canvas_chroma + 0.002, hue)
    nav = oklch_hex(0.22, 0.022, hue)
    line = oklch_hex(0.345, canvas_chroma + 0.004, hue)
    tint = oklch_hex(0.29, 0.05, hue)
    action = solve(hue, chroma * 0.96, lambda c: cc.contrast(WHITE, c) >= FILL_TARGET, highest=True)
    if cc.contrast(action, surface) < 3.0:      # the lightest step white text still reads on must also stand out from the surface (WCAG 1.4.11)
        raise ValueError(f"{theme_id}: action {action} is under 3:1 on the dark surface {surface}")
    press = solve(hue, chroma * 0.9, lambda c: cc.contrast(WHITE, c) >= 6.5, highest=True)
    text = solve(hue, min(chroma, 0.16) * 0.85, lambda c: min(cc.contrast(c, g) for g in (canvas, surface, nav, tint, mix_white(surface, SURFACE_MIX["level4"]))) >= 6.5,
                 highest=False)
    a_hue, a_chroma, _ = hue_chroma(t["accent"])
    accent_tint = oklch_hex(0.28, 0.045, a_hue)
    accent = solve(a_hue, min(a_chroma, 0.16) * 0.9, lambda c: min(cc.contrast(c, g) for g in (accent_tint, surface, mix_white(surface, SURFACE_MIX["level4"]))) >= 6.5,
                   highest=False)
    return {"canvas": canvas, "navBg": nav, "surface": surface, "action": action, "actionPress": press, "onAction": WHITE, "actionText": text,
            "actionTint": tint, "accent": accent, "accentTint": accent_tint, "line": line}


def derive_modules(t: dict, dark: dict) -> dict:
    """dark.modules for a theme that has light modules (tint / mid / solid): a dark tint, a mid tone and a light solid for text and icons."""
    out = {}
    for key, m in (t.get("modules") or {}).items():
        base = m["solid"]
        hue, chroma, _ = hue_chroma(base)
        if m.get("brand"):
            out[key] = {"tint": dark["actionTint"], "mid": oklch_hex(0.36, 0.06, hue), "solid": dark["actionText"]}
            continue
        tint = oklch_hex(0.27, 0.045, hue)
        mid = oklch_hex(0.36, 0.06, hue)
        solid = solve(hue, min(chroma, 0.16) * 0.9, lambda c: min(cc.contrast(c, g) for g in (tint, mid, dark["surface"])) >= 5.0, highest=False)
        out[key] = {"tint": tint, "mid": mid, "solid": solid}
    return out


def derive_all(data: dict, keep: set[str] = frozenset()) -> tuple[dict, dict]:
    themes, shared = data["themes"], data["shared"]
    per_theme = {}
    for key, t in themes.items():
        if key in keep and t.get("dark"):
            per_theme[key] = t["dark"]
            continue
        dark = derive_theme(key, t, shared)
        if t.get("modules"):
            dark["modules"] = derive_modules(t, dark)
        per_theme[key] = dark
    return per_theme, derive_shared(shared, [dark["surface"] for dark in per_theme.values()])


def write_themes(path: Path, data: dict, per_theme: dict, shared_dark: dict) -> None:
    ordered = ("canvas", "navBg", "surface", "action", "actionPress", "onAction", "actionText", "actionTint", "accent", "accentTint", "line", "modules")
    for key, t in data["themes"].items():
        dark = per_theme[key]
        t["dark"] = {k: dark[k] for k in ordered if k in dark} | {k: v for k, v in dark.items() if k not in ordered}
    data["shared"]["dark"] = shared_dark
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    path.write_text(text, encoding="utf-8", newline="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the derived maps into themes.json")
    parser.add_argument("--keep", action="append", default=[], metavar="THEME", help="leave this theme's stored dark map untouched (repeatable)")
    parser.add_argument("--check", action="store_true", help="run check_contrast on the stored maps")
    parser.add_argument("--themes", type=Path, default=THEMES)
    args = parser.parse_args(argv)
    if args.check:
        return cc.main([])
    data = json.loads(args.themes.read_text(encoding="utf-8"))
    per_theme, shared_dark = derive_all(data, set(args.keep))
    if args.write:
        write_themes(args.themes, data, per_theme, shared_dark)
        print(f"wrote dark maps for {len(per_theme)} themes and shared.dark to {args.themes}")
        return 0
    print(json.dumps({"shared.dark": shared_dark, "themes": per_theme}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
