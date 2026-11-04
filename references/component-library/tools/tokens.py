"""The colour tokens of the component library: light values, dark values, and the CSS / JS that carries them.

    py -X utf8 references/component-library/tools/tokens.py            print the token table and the contrast report
    py -X utf8 references/component-library/tools/tokens.py --write    rewrite the generated regions of src/kit.css and src/kit.js
    py -X utf8 references/component-library/tools/tokens.py --check    exit 1 if the sources differ from what this file generates, or a contrast target fails

This file is the one source of the token values. The light value of every neutral and status token is the colour the components used to hard-code
(so the light theme does not change); the dark value is a second set (not the light one inverted): a dark blue-grey ground that is not black, a card
face one step lighter, raised faces lighter again, fills and lines that step up from the card face by a white mix, text from a near-white downwards in
contrast steps, status text in a lighter step of its hue over a low-lightness tint of the same hue, and the eight theme colours re-derived the way
``scripts/make_dark.py`` derives ``themes.json`` (same hue, lightness solved against a contrast target).

Generated regions (do not edit by hand, run ``--write``)::

    src/kit.css   /* tokens:begin */ ... /* tokens:end */      the :root, .light, media and .dark blocks
    src/kit.js    /* themes:begin */ ... /* themes:end */      DARK_THEMES (the dark colours of the 8 themes)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parent
SRC = LIB / "src"
SCRIPTS = LIB.parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_contrast as cc  # noqa: E402
import make_dark as md  # noqa: E402

WHITE = "#FFFFFF"

# ----------------------------------------------------------------------------------------------------------------------------------------------
# The hue the neutrals lean to: the library's light ink (#1F2329) is a blue-grey, so the dark ground is too.
# ----------------------------------------------------------------------------------------------------------------------------------------------
HUE, _CHROMA, _L = md.hue_chroma("#1F2329")
GROUND_CHROMA = 0.012

CANVAS = md.oklch_hex(0.175, GROUND_CHROMA, HUE)       # dark page ground (not black)
CARD = md.oklch_hex(0.23, GROUND_CHROMA + 0.002, HUE)  # dark card face: one step lighter than the page ground
RAISED = {2: md.mix_white(CARD, 5), 3: md.mix_white(CARD, 8), 4: md.mix_white(CARD, 11)}  # elevation steps of themes.json shared.dark.elevation.surfaceMix


def card_mix(pct: float) -> str:
    return md.mix_white(CARD, pct)


# ----------------------------------------------------------------------------------------------------------------------------------------------
# Neutral steps: fills and lines. Light value = the grey the components hard-coded; dark value = the card face with this much white mixed in.
# ----------------------------------------------------------------------------------------------------------------------------------------------
STEPS = [  # name, light, dark white-mix percent over the card face, used for
    ("n1", "#FAFBFC", 2.5),    # faintest wash: zebra rows, expanded rows
    ("n2", "#F7F8FA", 4.0),    # faint fill
    ("n3", "#F5F6F8", 5.2),    # the page grey used as a fill inside a card
    ("soft", "#F2F3F5", 6.5),  # the common soft fill: inputs, chips, secondary buttons, skeleton blocks
    ("n4", "#EEF0F3", 8.0),    # hairline-strength fill
    ("n5", "#E9EBEF", 10.0),   # hover / pressed fill
    ("n6", "#E5E7EB", 12.5),   # track, divider fill
    ("n7", "#DDE0E5", 16.0),   # border
    ("n8", "#D5D9DF", 20.0),   # strong border, off-state switch track
    ("n9", "#C9CED6", 27.0),   # control border, scrollbar thumb
    ("n10", "#B9BFC7", 36.0),  # strong control border
    ("n11", "#AEB4BD", 42.0),  # separator dots, handles
    ("n12", "#98A0AA", 52.0),  # icon grey, large handles
]
LINES = [  # the hairline names; the dark value is the step with the same mix
    ("line", "#EEF0F3", 8.0),
    ("line2", "#E6E8EC", 12.5),
]

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Text steps: light = the greys of the components; dark = solved against the lightest fill a text of that step sits on.
# ----------------------------------------------------------------------------------------------------------------------------------------------
INK_STEPS = [  # name, light, minimum contrast over the dark ground (n4: the card face with 8 % white)
    ("ink1", "#3B424C", 9.0),
    ("ink2", "#5B6470", 7.0),
    ("ink3", "#6A727D", 6.0),
    ("ink4", "#8A919B", 5.2),
    ("ink5", "#98A0AA", 4.6),
    ("ink6", "#B4BAC4", 3.4),
    ("ink7", "#C4C9D0", 3.05),
]
DARK_INK = md.oklch_hex(0.935, 0.006, HUE)  # near-white, not white

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Status colours (SPEC.md section 4): text, tint ground, solid fill (carries white text), border.
# ----------------------------------------------------------------------------------------------------------------------------------------------
STATUS = [  # key, light text, light tint, light line
    ("ok", "#3F7D58", "#EAF3EE", "#CFE3D7"),
    ("warn", "#8A5A00", "#F7EEDB", "#EBDDB8"),
    ("danger", "#A8433B", "#F8ECEA", "#E6C4C0"),
]
NEUTRAL, NEUTRAL_BG = "#6A727D", "#F2F3F5"
PRICE = "#B8443C"
HOT = "#A9574C"          # the filled hot tag (white text)
PASTELS = ["#F3E6BF", "#F3E9D2", "#F4E6CF", "#F4E8E1", "#F6E3D4", "#FFF1E0", "#E3EEDC", "#F2DAD7"]  # pale tints of gold, peach, orange and green that are not one of the status tints
ACCENTS = [("acc-sand", "#B8957A"), ("acc-sand2", "#9C7A5F"), ("acc-slate", "#7E94B4"), ("acc-slate2", "#5F7799"), ("acc-gold", "#B58A5E"), ("acc-gold2", "#9C7448"),
           ("acc-green", "#6B9A63"), ("acc-green2", "#5A8955")]
PH = "#EDE7E4"           # photo placeholder under product images
FILL_TARGET = 4.6        # white text on a solid fill: 4.5 plus a margin for 8-bit rounding
BRAND_FILL_TARGET = 5.3  # the brand fill in the dark: white text at 85 % opacity (a sub-title on a banner) must still reach 4.5

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Shadows are colours only (the shape stays in the component). Light: the ink at an alpha; dark: black at a stronger alpha, which is all a shadow can do
# on a dark face; the lift there comes from the raised faces above.
# ----------------------------------------------------------------------------------------------------------------------------------------------
SHADOW_ALPHAS = [4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 28]  # percent
VEIL_ALPHAS = [4, 5, 6, 8, 10, 12]


def shadow_dark(alpha: int) -> float:
    return min(0.6, round(alpha / 100 * 3.0 + 0.06, 2))


# ----------------------------------------------------------------------------------------------------------------------------------------------
# The eight themes: light values are kit.js THEMES; dark values are derived here.
# ----------------------------------------------------------------------------------------------------------------------------------------------
THEMES_LIGHT = [  # id, name, p, pd, pt, pm (kit.js THEMES)
    ("rose", "雾粉", "#A85D79", "#723F52", "#F7F0F3", "#E9D6DE"),
    ("coral", "珊瑚", "#A76352", "#724338", "#F7F1EF", "#E9D8D4"),
    ("orange", "暖橙", "#9A6A3C", "#6A4A2A", "#F6F1EC", "#E7DACB"),
    ("green", "草绿", "#50804E", "#365735", "#EFF4EF", "#D3DFD3"),
    ("teal", "青碧", "#457D81", "#2F5558", "#EEF3F4", "#D0DEE0"),
    ("blue", "天蓝", "#5577A4", "#3A5170", "#F0F3F7", "#D4DDE8"),
    ("purple", "紫藤", "#7D6CA5", "#554970", "#F3F2F7", "#DEDAE8"),
    ("graphite", "石墨", "#4B515A", "#34393F", "#EFEFF0", "#D1D2D5"),
]


def theme_dark(p: str, pt: str) -> dict:
    """Dark values of one theme: p (fill, white text 4.6:1), pd (pressed fill, white text 6.5:1), pt / pm (tints), ptext (text and icons), pfg (p as text)."""
    h, c, _ = md.hue_chroma(p)
    tint_c = max(0.008, min(0.04, c * 0.30))
    pdk = md.solve(h, c * 0.96, lambda x: cc.contrast(WHITE, x) >= BRAND_FILL_TARGET, highest=True)
    pdd = md.solve(h, c * 0.9, lambda x: cc.contrast(WHITE, x) >= 6.5, highest=True)
    ptd = md.oklch_hex(0.29, tint_c, h)
    pmd = md.oklch_hex(0.36, tint_c * 1.2, h)
    grounds = [CANVAS, CARD, RAISED[4], card_mix(10), ptd, pmd]
    ptext = md.solve(h, min(c, 0.16) * 0.85, lambda x: min(cc.contrast(x, g) for g in grounds) >= 6.6, highest=False)
    return {"p": pdk, "pd": pdd, "pt": ptd, "pm": pmd, "text": ptext}


def ink_dark(min_contrast: float) -> str:
    ground = card_mix(8.0)
    return md.solve(HUE, 0.01, lambda x: cc.contrast(x, ground) >= min_contrast, highest=False)


def status_dark(text: str, tint: str, line: str) -> dict:
    h, c, _ = md.hue_chroma(text)
    tint_d = md.oklch_hex(0.27, 0.04, h)
    grounds = [CANVAS, CARD, RAISED[4], card_mix(10), tint_d]
    txt = md.solve(h, min(c, 0.14), lambda x: min(cc.contrast(x, g) for g in grounds) >= 5.6, highest=False)
    fill = md.solve(h, c * 0.95, lambda x: cc.contrast(WHITE, x) >= FILL_TARGET, highest=True)
    line_d = md.oklch_hex(0.38, 0.05, h)
    return {"text": txt, "bg": tint_d, "fill": fill, "line": line_d}


# ----------------------------------------------------------------------------------------------------------------------------------------------
# The token table: name -> (light, dark)
# ----------------------------------------------------------------------------------------------------------------------------------------------


def table() -> list[tuple[str, str, str, str]]:
    """(group, name, light, dark) in the order they are written."""
    rows: list[tuple[str, str, str, str]] = []
    add = lambda g, n, light, dark: rows.append((g, n, light, dark))  # noqa: E731
    add("surface", "bg", "#F5F6F8", CANVAS)
    add("surface", "page", "#F4F1EE", CANVAS)
    add("surface", "card", "#FFFFFF", CARD)
    add("surface", "card2", "#FFFFFF", RAISED[2])
    add("surface", "card3", "#FFFFFF", RAISED[3])
    add("surface", "card4", "#FFFFFF", RAISED[4])
    add("surface", "paper", "#FFFFFF", "#F2F4F7")
    for name, light, pct in STEPS:
        add("step", name, light, card_mix(pct))
    for name, light, pct in LINES:
        add("line", name, light, card_mix(pct))
    add("text", "off", "#D5D9DF", md.solve(HUE, 0.01, lambda x: cc.contrast(x, card_mix(6.5)) >= 3.2, highest=False))  # an inactive glyph (empty star): faint in the light, 3:1 in the dark
    add("text", "ink", "#1F2329", DARK_INK)
    for name, light, target in INK_STEPS:
        add("text", name, light, ink_dark(target))
    add("status", "price-fill", PRICE, md.solve(*md.hue_chroma(PRICE)[:2], lambda x: cc.contrast(WHITE, x) >= FILL_TARGET, highest=True))
    add("text", "price", PRICE, md.solve(*md.hue_chroma(PRICE)[:2], lambda x: min(cc.contrast(x, g) for g in (CARD, card_mix(10), md.oklch_hex(0.27, 0.04, md.hue_chroma(PRICE)[0]))) >= 5.6, highest=False))
    for key, text, tint, line in STATUS:
        d = status_dark(text, tint, line)
        add("status", key, text, d["text"])
        add("status", key + "-bg", tint, d["bg"])
        add("status", key + "-fill", text, d["fill"])
        add("status", key + "-line", line, d["line"])
    for key, text, tint in (("fit", "#14793F", "#E6F7EE"), ("avoid", "#8A4600", "#FFF1E0")):  # the 适合 / 避免 labels of the library page
        d = status_dark(text, tint, tint)
        add("page", key, text, d["text"])
        add("page", key + "-bg", tint, d["bg"])
    ok_dark = status_dark("#3F7D58", "#EAF3EE", "#CFE3D7")["text"]
    add("status", "ok-ink", "#2F6B47", ok_dark)           # the darker green of text on the success tint
    gold_dark = status_dark("#8A5A00", "#F7EEDB", "#EBDDB8")["text"]
    add("status", "gold-ink", "#5A4010", gold_dark)       # brown text on a pale gold tint (member and gold marketing styles)
    add("status", "gold-ink2", "#6F5521", gold_dark)
    add("status", "gold-ink3", "#7A6232", gold_dark)
    add("status", "ok-ink2", "#43683A", ok_dark)
    danger_dark = status_dark("#A8433B", "#F8ECEA", "#E6C4C0")["text"]
    add("status", "danger-ink", "#9C4137", danger_dark)   # a slightly deeper red text on the pale red tint
    add("status", "hot-ink", "#A9574C", danger_dark)      # the hot-tag red as text
    bronze_h = md.hue_chroma("#8C5A43")
    add("status", "bronze", "#8C5A43", md.solve(bronze_h[0], min(bronze_h[1], 0.09), lambda x: min(cc.contrast(x, g) for g in (CARD, md.oklch_hex(0.27, 0.04, md.hue_chroma("#A8433B")[0]))) >= 5.6, highest=False))  # third place of a ranking
    add("overlay", "dim80", "0.8", "0.9")                 # opacity of a struck-through price or a note on the brand fill: lighter text on the (darker) dark brand fill needs less fading
    add("overlay", "dim85", "0.85", "0.93")
    for name, light in ACCENTS:  # solid accent fills that carry white text (banners, gold and green buttons): the dark twin is the same hue with white text at 4.6:1
        ah, ac, _ = md.hue_chroma(light)
        add("accent", name, light, md.solve(ah, ac * 0.95, lambda x: cc.contrast(WHITE, x) >= 5.4, highest=True))
    for lit in PASTELS:  # exact light value; the dark value is a low-lightness tint of the same hue
        ph_, pc_, _ = md.hue_chroma(lit)
        add("tint", "tint-" + lit[1:].lower(), lit, md.oklch_hex(0.27, min(0.045, pc_ * 0.9), ph_))
    add("status", "neutral", NEUTRAL, ink_dark(5.6))
    add("status", "neutral-bg", NEUTRAL_BG, card_mix(6.5))
    hot_h, hot_c, _ = md.hue_chroma(HOT)
    add("status", "hot", HOT, md.solve(hot_h, hot_c * 0.95, lambda x: cc.contrast(WHITE, x) >= FILL_TARGET, highest=True))
    add("surface", "ph", PH, md.oklch_hex(0.30, 0.012, md.hue_chroma(PH)[0]))
    add("surface", "inv", "#1F2329", card_mix(20))        # solid inverse face that carries white text: tooltips, dark badges, the toast
    add("surface", "inv-a", "rgba(31,35,41,.88)", "rgba(%d,%d,%d,.94)" % cc.rgb(card_mix(20)))
    add("surface", "lift", "#FFFFFF", card_mix(12.5))      # a face lifted above a soft track: the selected pill of a segmented control or tab bar
    add("surface", "night", "#17171B", md.oklch_hex(0.15, 0.01, HUE))  # the stage for components that are drawn on a dark ground in both appearances
    for a in VEIL_ALPHAS:  # translucent fills: counts, chips, hovers. light: the ink at an alpha; dark: white at a slightly higher alpha
        add("overlay", f"veil{a:02d}", f"rgba(31,35,41,.{a:02d})", "rgba(255,255,255,%s)" % f"{a / 100 * 1.4:.2f}".lstrip("0"))
    add("overlay", "scrim", "#1F2329", "#000000")          # the colour of image overlays and masks; used with color-mix at the alpha the component had
    add("overlay", "mask", "rgba(31,35,41,.38)", "rgba(0,0,0,.60)")
    add("overlay", "mask2", "rgba(31,35,41,.58)", "rgba(0,0,0,.72)")
    add("overlay", "glass", "rgba(255,255,255,.85)", "rgba(%d,%d,%d,.80)" % cc.rgb(CARD))
    add("overlay", "glass2", "rgba(255,255,255,.92)", "rgba(%d,%d,%d,.90)" % cc.rgb(CARD))
    add("overlay", "glass0", "rgba(255,255,255,.7)", "rgba(%d,%d,%d,.62)" % cc.rgb(CARD))
    add("overlay", "hi", "rgba(255,255,255,.85)", "rgba(255,255,255,.07)")
    add("overlay", "hi2", "rgba(255,255,255,.55)", "rgba(255,255,255,.05)")
    add("overlay", "page-glass", "rgba(244,241,238,.94)", "rgba(%d,%d,%d,.92)" % cc.rgb(CANVAS))
    for a in SHADOW_ALPHAS:
        add("shadow", f"sh{a:02d}", f"rgba(31,35,41,.{a:02d})", "rgba(0,0,0,%s)" % (f"{shadow_dark(a):.2f}".rstrip("0").rstrip(".") or "0"))
    return rows


def theme_rows() -> list[dict]:
    out = []
    for tid, name, p, pd, pt, pm in THEMES_LIGHT:
        d = theme_dark(p, pt)
        out.append({"id": tid, "name": name, "light": {"p": p, "pd": pd, "pt": pt, "pm": pm, "text": pd, "fg": p}, "dark": d})
    return out


def hex_rgb(color: str) -> str:
    return ",".join(str(v) for v in cc.rgb(color))


def mixc(a: str, b: str, t: float) -> str:
    return "#" + "".join(f"{round(x * t + y * (1 - t)):02X}" for x, y in zip(cc.rgb(a), cc.rgb(b)))


# ----------------------------------------------------------------------------------------------------------------------------------------------
# CSS and JS generation
# ----------------------------------------------------------------------------------------------------------------------------------------------


def decls(rows, dark: bool) -> str:
    out = []
    for _, name, light, dk in rows:
        out.append(f"--{name}:{dk if dark else light}")
    return ";".join(out)


def theme_data(t: dict) -> str:
    """The data of one theme as plain custom properties (--t-*): both schemes, so a nested .dark / .light container can pick its own."""
    lt, dk = t["light"], t["dark"]
    return ";".join([
        f"--t-p-l:{lt['p']}", f"--t-pd-l:{lt['pd']}", f"--t-pt-l:{lt['pt']}", f"--t-pm-l:{lt['pm']}", f"--t-ga-l:{mixc(lt['p'], WHITE, 0.95)}", f"--t-rgb-l:{hex_rgb(lt['p'])}",
        f"--t-p-d:{dk['p']}", f"--t-pd-d:{dk['pd']}", f"--t-pt-d:{dk['pt']}", f"--t-pm-d:{dk['pm']}", f"--t-ga-d:{dk['p']}", f"--t-rgb-d:{hex_rgb(dk['p'])}",
        f"--t-text-d:{dk['text']}",
    ])


MAP_LIGHT = ("--p:var(--t-p-l);--pd:var(--t-pd-l);--pt:var(--t-pt-l);--pm:var(--t-pm-l);--ga:var(--t-ga-l);--gb:var(--t-p-l);--p-rgb:var(--t-rgb-l);"
             "--p-text:var(--t-pd-l);--p-fg:var(--t-p-l)")
MAP_DARK = ("--p:var(--t-p-d);--pd:var(--t-pd-d);--pt:var(--t-pt-d);--pm:var(--t-pm-d);--ga:var(--t-ga-d);--gb:var(--t-p-d);--p-rgb:var(--t-rgb-d);"
            "--p-text:var(--t-text-d);--p-fg:var(--t-text-d)")


def css() -> str:
    rows = table()
    light, dark = decls(rows, False), decls(rows, True)
    themes = theme_rows()
    sys_dark = ":root:not(.light):not([data-theme=light])"
    is_dark = ".dark,[data-theme=dark]"
    is_light = ".light,[data-theme=light]"
    parts = [
        "/* tokens:begin  (generated by tools/tokens.py --write; edit the table there, not here) */",
        "/* theme data: both schemes of each theme as plain custom properties; the rules below pick one by the scheme of the element */",
        f":root{{{theme_data(themes[0])}}}",
    ]
    parts += [f"[data-lt={t['id']}]{{{theme_data(t)}}}" for t in themes]
    parts += [
        "/* a themed element follows the scheme: light first, system dark, a dark ancestor or itself, a light ancestor or itself (light wins a tie) */",
        f"[data-lt]{{{MAP_LIGHT}}}",
        f"@media (prefers-color-scheme:dark){{:where({sys_dark}) [data-lt]{{{MAP_DARK}}}}}",
        f":where({is_dark}) [data-lt],[data-lt]:where({is_dark}){{{MAP_DARK}}}",
        f":where({is_light}) [data-lt],[data-lt]:where({is_light}){{{MAP_LIGHT}}}",
        "/* neutrals and status colours, and the theme colours of the element that declares the scheme */",
        f":root,{is_light}{{color-scheme:light;{light};{MAP_LIGHT}}}",
        f"@media (prefers-color-scheme:dark){{{sys_dark}{{color-scheme:dark;{dark};{MAP_DARK}}}}}",
        f"{is_dark}{{color-scheme:dark;{dark};{MAP_DARK}}}",
        "/* tokens:end */",
    ]
    return "\n".join(parts)


def js() -> str:
    lines = ["/* themes:begin  (generated by tools/tokens.py --write) */", "const DARK_THEMES = {"]
    for t in theme_rows():
        d = t["dark"]
        lines.append(f"  {t['id']}: {{ p: '{d['p']}', pd: '{d['pd']}', pt: '{d['pt']}', pm: '{d['pm']}', text: '{d['text']}' }},")
    lines += ["}", "/* themes:end */"]
    return "\n".join(lines)


def splice(text: str, begin: str, end: str, new: str) -> str:
    a, b = text.index(begin), text.index(end)
    return text[:a] + new + text[b + len(end):]


def render_sources() -> dict[Path, str]:
    kit_css = (SRC / "kit.css").read_text(encoding="utf-8")
    kit_js = (SRC / "kit.js").read_text(encoding="utf-8")
    return {
        SRC / "kit.css": splice(kit_css, "/* tokens:begin", "/* tokens:end */", css()),
        SRC / "kit.js": splice(kit_js, "/* themes:begin", "/* themes:end */", js()),
    }


# ----------------------------------------------------------------------------------------------------------------------------------------------
# Contrast report
# ----------------------------------------------------------------------------------------------------------------------------------------------


def report() -> list[str]:
    """The dark pairs that must hold; returns the failures."""
    rows = {name: (light, dark) for _, name, light, dark in table()}
    d = {name: dark for name, (light, dark) in rows.items() if dark.startswith("#")}
    fails: list[str] = []

    def need(fg: str, bg: str, minimum: float, label: str):
        r = cc.contrast(fg, bg)
        if r < minimum:
            fails.append(f"{label}: {fg} on {bg} = {r:.2f} < {minimum}")

    grounds = {k: d[k] for k in ("bg", "card", "card2", "card3", "card4", "soft", "n4", "n5")}
    for g, gc in grounds.items():
        need(d["ink"], gc, 10 if g != "n5" else 9, f"ink on {g}")
        for name, minimum in (("ink1", 8), ("ink2", 6), ("ink3", 4.9), ("ink4", 4.5), ("ink5", 3.4), ("ink6", 3.0), ("ink7", 3.0)):
            if g in ("bg", "card", "soft", "n4"):
                need(d[name], gc, minimum, f"{name} on {g}")
    for key in ("ok", "warn", "danger"):
        for g in ("bg", "card", "card4"):
            need(d[key], d[g], 5.0, f"{key} text on {g}")
        need(d[key], d[key + "-bg"], 5.0, f"{key} text on its tint")
        need(WHITE, d[key + "-fill"], 4.5, f"white on {key}-fill")
        need(d[key + "-fill"], d["card"], 2.6, f"{key}-fill on card (non-text)")
    need(d["price"], d["card"], 5.0, "price on card")
    need(WHITE, d["hot"], 4.5, "white on hot")
    need(WHITE, d["inv"], 7.0, "white on inv")
    need(d["neutral"], d["card"], 5.0, "neutral on card")
    need(d["neutral"], d["neutral-bg"], 4.5, "neutral on neutral-bg")
    for t in theme_rows():
        td = t["dark"]
        need(WHITE, td["p"], 4.5, f"{t['id']}: white on p")
        need(WHITE, td["pd"], 4.5, f"{t['id']}: white on pd")
        need(td["p"], d["card"], 3.0, f"{t['id']}: p on card (non-text, 1.4.11)")
        for g in ("bg", "card", "card4"):
            need(td["text"], d[g], 4.5, f"{t['id']}: p-text on {g}")
        need(td["text"], td["pt"], 4.5, f"{t['id']}: p-text on pt")
        need(td["text"], td["pm"], 4.5, f"{t['id']}: p-text on pm")
    need(d["line"], d["card"], 1.15, "line on card")
    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    fails = report()
    if args.write or args.check:
        want = render_sources()
        stale = [str(p.relative_to(LIB)) for p, text in want.items() if p.read_text(encoding="utf-8") != text]
        if args.write:
            for p, text in want.items():
                p.write_text(text, encoding="utf-8", newline="")
            print("written:", ", ".join(str(p.relative_to(LIB)) for p in want))
        elif stale:
            print("tokens out of date (run --write):", ", ".join(stale))
            return 1
    else:
        print(f"canvas {CANVAS}  card {CARD}  raised {RAISED}  ink {DARK_INK}")
        for g, n, light, dark in table():
            print(f"{g:8s} --{n:12s} {light:24s} {dark}")
        for t in theme_rows():
            print(t["id"], t["light"], "->", t["dark"])
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    if args.check:
        print("tokens: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
