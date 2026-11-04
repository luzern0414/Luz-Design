"""Replace the hard-coded neutral and status colours of the component sources with the colour tokens (kit.css, tools/tokens.py).

    py -X utf8 references/component-library/tools/tokenize.py --report          what would change, grouped (nothing is written)
    py -X utf8 references/component-library/tools/tokenize.py --write           rewrite src/*.js, src/*.css and src/lib.template.html in place
    py -X utf8 references/component-library/tools/tokenize.py --left            list every colour literal that is still hard-coded after the pass

The light theme must not change: the light value of every token is the colour it replaces (tools/tokens.py), and a grey that has no token of its own is
written as the token it is nearest to (when the two are within ``NEAR`` levels in every channel) or as a ``color-mix`` of the two neighbouring steps that
reproduces it. ``tools/visual_regression.py`` proves the result.

The pass reads every ``property: value`` it can find in the source text (CSS strings of the ``def()`` calls and of the helper functions, ``style=""``
attributes in the markup, JS strings that carry a declaration). ``${...}`` interpolations are masked, so code inside them is never touched. A colour is
replaced according to the property it is the value of (background, text, border, shadow, svg paint) and the literal; where a rule needs the surroundings
(a white face that sits on a soft track, a popover, a switch knob) the selector and the other declarations of the same rule decide, and a few components
are listed by hand in ``OVERRIDES`` / ``KEEP``. Everything that is deliberately left white or dark is in ``KEEP`` with the reason: the exception list
that README.md prints.
"""
from __future__ import annotations

import argparse
import collections
import colorsys
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parent
SRC = LIB / "src"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LIB.parents[1] / "scripts"))

import tokens as tk  # noqa: E402

NEAR = 6  # a grey within this many levels (every channel) of a token is written as that token

FILES = sorted(SRC.glob("*.js")) + [SRC / "kit.css", SRC / "ix.css", SRC / "lib.template.html"]
SKIP_FILES = {"taxonomy.js"}

# ------------------------------------------------------------------------------------------------------------------------------------------
# Colours
# ------------------------------------------------------------------------------------------------------------------------------------------

HEX = re.compile(r"(?<![\w&#/])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![\w-])")
RGBA = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([\d.]+)\s*)?\)")
WORD = re.compile(r"(?<![\w-])white(?![\w-])")


def norm(h: str) -> str:
    h = h.upper()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def rgb(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def lum(h: str) -> float:
    return tk.cc.luminance(h)


def is_greyish(h: str) -> bool:
    r, g, b = rgb(h)
    return max(r, g, b) - min(r, g, b) <= 26 and (b >= r - 2)  # the blue-grey family of the library (ink #5B6470 has a spread of 21); warm greys are not ours


# neutral steps: fills / lines (surface ladder) and texts (ink ladder), light value -> token name
def ladders():
    steps = {"card": "#FFFFFF"}
    for n, light, _ in tk.STEPS:
        steps[n] = light
    ink = {"ink": "#1F2329"}
    for n, light, _ in tk.INK_STEPS:
        ink[n] = light
    ink["ink3"] = "#6A727D"
    return steps, ink


STEPS, INKS = ladders()


def dist(a: str, b: str) -> int:
    return max(abs(x - y) for x, y in zip(rgb(a), rgb(b)))


def nearest(h: str, ladder: dict[str, str]) -> tuple[str, int]:
    name = min(ladder, key=lambda n: (dist(h, ladder[n]), n))
    return name, dist(h, ladder[name])


def mix_between(h: str, ladder: dict[str, str]) -> str | None:
    """``color-mix`` of the two ladder steps whose luminance brackets h, with the share that reproduces h (error under 3 levels), or None."""
    order = sorted(ladder, key=lambda n: -lum(ladder[n]))
    lh = lum(h)
    for a, b in zip(order, order[1:]):
        la, lb = lum(ladder[a]), lum(ladder[b])
        if la >= lh >= lb:
            ra, rb, rh = rgb(ladder[a]), rgb(ladder[b]), rgb(h)
            best = None
            for pct in range(1, 100):
                m = tuple(round(x * pct / 100 + y * (100 - pct) / 100) for x, y in zip(ra, rb))
                err = max(abs(p - q) for p, q in zip(m, rh))
                if best is None or err < best[0]:
                    best = (err, pct)
            if best and best[0] <= 3:
                return f"color-mix(in srgb,var(--{a}) {best[1]}%,var(--{b}))"
    return None


EXACT_TEXT = {"#9C4137": "danger-ink", "#A9574C": "hot-ink", "#7A6232": "gold-ink3", "#43683A": "ok-ink2"}  # slightly different reds, browns and greens used as text
GOLD_INK = {"#5A4010", "#5E4210"}
GOLD_INK2 = {"#6F5521", "#7A5C1E", "#7A5A1E"}
OK_INK = {"#2F6B47", "#2F6A47", "#2D5A40"}
STATUS_TEXT = {"#3F7D58": "ok", "#8A5A00": "warn", "#A8433B": "danger"}
STATUS_BG = {"#EAF3EE": "ok-bg", "#F7EEDB": "warn-bg", "#F8ECEA": "danger-bg", "#F8ECEB": "danger-bg"}
STATUS_LINE = {"#CFE3D7": "ok-line", "#EBDDB8": "warn-line", "#E6C4C0": "danger-line"}
STATUS_FILL = {"#3F7D58": "ok-fill", "#8A5A00": "warn-fill", "#A8433B": "danger-fill", "#A9574C": "hot"}
# reds used as pressed / darker fills of the danger colour: danger-fill with a little black, the way they were made
DANGER_DARK = {"#8F3830": 0.85, "#8A352E": 0.84}
# pastel tints of other hues used as backgrounds: nearest status tint by hue (light value changes by a few levels at most; listed in the report)
HUE_TINT = {"danger-bg": (0, 25), "warn-bg": (25, 70), "ok-bg": (70, 170)}

# ------------------------------------------------------------------------------------------------------------------------------------------
# Context
# ------------------------------------------------------------------------------------------------------------------------------------------


def mask_interpolations(text: str) -> str:
    """Blank the delimiters of every ${...} (the two characters of ``${`` and the closing brace, balanced) so brace scans see plain CSS; the text inside stays,
    because the strings of an interpolation (``${bare ? '' : ';background:#fff'}``) are CSS too."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        if text[i] == "$" and i + 1 < n and text[i + 1] == "{":
            depth, j = 1, i + 2
            while j < n and depth:
                c = text[j]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                j += 1
            out[i] = out[i + 1] = " "
            out[j - 1] = " "
            i += 2
        else:
            i += 1
    return "".join(out)


PROP_FAMILY = {
    "background": "bg", "background-color": "bg", "background-image": "bg",
    "color": "text", "caret-color": "text", "text-decoration-color": "text", "-webkit-text-fill-color": "text",
    "border": "border", "border-top": "border", "border-bottom": "border", "border-left": "border", "border-right": "border",
    "border-color": "border", "border-top-color": "border", "border-bottom-color": "border", "border-left-color": "border", "border-right-color": "border",
    "outline": "border", "outline-color": "border", "column-rule": "border",
    "box-shadow": "shadow", "text-shadow": "shadow", "filter": "shadow", "drop-shadow": "shadow",
    "fill": "svg", "stroke": "svg", "stop-color": "svg", "flood-color": "svg",
    "scrollbar-color": "bg", "accent-color": "text",
}
# local custom properties of the component CSS that hold a colour: the family says how its value is read
CUSTOM_FAMILY = {"--bd": "border", "--bd0": "border", "--bd2": "border", "--sln": "border", "--sf": "bg", "--okb": "bg", "--wnb": "bg", "--dgb": "bg", "--mub": "bg",
                 "--ok": "text", "--wn": "text", "--dg": "text", "--mu": "text", "--sh": "shadow", "--sh1": "shadow", "--sh2": "shadow", "--sh3": "shadow",
                 "--gold0": "bg"}
CUSTOM_TOKEN = {"--ok": None, "--okb": "ok-bg", "--wn": "warn", "--wnb": "warn-bg", "--dg": "danger", "--dgb": "danger-bg", "--mu": "neutral", "--mub": "neutral-bg"}
DECL = re.compile(r"(?<![\w\-$.#])((?:--)?[a-zA-Z][\w-]*|-webkit-text-fill-color)\s*:\s*([^;{}`\"'\n]*)")


JS_ATTR = re.compile(r"(?<![\w-])(?P<k>fill|stroke|stop-color|'stop-color')\s*:\s*['\"](?P<lit>#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})['\"]")


HTML_ATTR = re.compile(r"(?<![\w-])(?P<k>fill|stroke|stop-color)=(?P<q>[\"'])(?P<lit>#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})(?P=q)")
ILLUSTRATION_FILES = {"extras.js"}  # the default cartoon avatars: their colours are part of the picture, not of the interface


class Hit:
    __slots__ = ("file", "start", "end", "lit", "prop", "family", "selector", "decls", "cid", "inline", "before", "value", "dstart", "dend")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def component_ids(raw: str) -> list[tuple[int, str]]:
    return [(m.start(), m.group(1)) for m in re.finditer(r"\bid:\s*'((?:MP|AD)-[A-Z]+-\d{3})'", raw)] + [
        (m.start(), "LEGACY:" + m.group(1)) for m in re.finditer(r"\badd\(\s*'[^']*'\s*,\s*'([^']+)'", raw)]


def enclosing_rule(masked: str, pos: int) -> tuple[str, dict[str, str]] | None:
    """The selector and declarations of the {...} block around pos, or None when pos is not inside a plain CSS block."""
    depth, i = 0, pos
    while i > 0:
        i -= 1
        c = masked[i]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                break
            depth -= 1
        elif c in "`\n" and depth == 0 and c == "`":
            return None
    else:
        return None
    open_i = i
    j = open_i
    while j > 0 and masked[j - 1] not in "{};`":
        j -= 1
    selector = masked[j:open_i].strip()
    end = masked.find("}", open_i)
    body = masked[open_i + 1:end if end > 0 else len(masked)]
    decls = {}
    for m in DECL.finditer(body):
        decls[m.group(1).lower()] = m.group(2).strip()
    return selector, decls


def scan(path: Path) -> tuple[str, list[Hit]]:
    raw = path.read_bytes().decode("utf-8")  # keeps CRLF files as they are
    masked = mask_interpolations(raw)
    if path.name == "kit.css" and "tokens:begin" in raw:  # the generated token table is the source of the colours, not a user of them
        a, b = raw.index("tokens:begin"), raw.index("tokens:end")
        masked = masked[:a] + " " * (b - a) + masked[b:]
    ids = component_ids(raw)
    hits: list[Hit] = []
    for m in (HTML_ATTR.finditer(masked) if path.name not in ILLUSTRATION_FILES else []):  # SVG attributes in the markup: stroke="#E3E6EA"
        cid = None
        for pos, i in ids:
            if pos <= m.start():
                cid = i
            else:
                break
        hits.append(Hit(file=path.name, start=m.start("lit"), end=m.end("lit"), lit=m.group("lit"), prop=m.group("k").lower(), family="svg", selector="", decls={}, cid=cid,
                        inline=True, before="", value=m.group("lit"), dstart=m.start(), dend=m.end()))
    for m in JS_ATTR.finditer(masked):  # SVG attributes written as a JS object: { stroke: '#EEF0F3', fill: '#fff' }
        cid = None
        for pos, i in ids:
            if pos <= m.start():
                cid = i
            else:
                break
        hits.append(Hit(file=path.name, start=m.start("lit"), end=m.end("lit"), lit=m.group("lit"), prop=m.group("k").lower(), family="svg", selector="", decls={}, cid=cid,
                        inline=True, before="", value=m.group("lit"), dstart=m.start(), dend=m.end()))
    for m in DECL.finditer(masked):
        prop = m.group(1).lower()
        value = m.group(2)
        family = PROP_FAMILY.get(prop) or CUSTOM_FAMILY.get(prop)
        if not family:
            continue
        vstart = m.start(2)
        found = []
        for rx in (HEX, RGBA, WORD):
            for c in rx.finditer(value):
                found.append((c.start(), c.end(), c.group(0)))
        if not found:
            continue
        before = masked[max(0, m.start() - 160):m.start()]
        inline = bool(re.search(r"style=[\"'][^\"'<>{}]*$", before)) or ("<" in before and re.search(r"<\w+[^<>{}]*\bstyle=[\"'][^\"'<>{}]*$", before) is not None)
        rule = None if inline else enclosing_rule(masked, m.start())
        selector, decls = rule if rule else ("", {})
        cid = None
        for pos, i in ids:
            if pos <= m.start():
                cid = i
            else:
                break
        for s, e, lit in found:
            hits.append(Hit(file=path.name, start=vstart + s, end=vstart + e, lit=lit, prop=prop, family=family, selector=selector, decls=decls, cid=cid,
                            inline=inline, before=before, value=value, dstart=m.start(), dend=m.end()))
    return raw, hits


# ------------------------------------------------------------------------------------------------------------------------------------------
# Rules
# ------------------------------------------------------------------------------------------------------------------------------------------

# Deliberately kept: (component id or file, selector regex, literal) -> reason. Each entry stays white / dark in both appearances.
KEEP: list[tuple[str, str, str]] = [  # (file, text around the literal, reason): left exactly as written
    ("blocks-ad-viz.js", "font-size:12px;fill:#fff", "label of the chart mark: white text on the --inv chip, white in both appearances"),
    ("blocks-ad-biz.js", 'aria-label="登录二维码"><g fill="#1F2329"', "QR modules stay dark on the --paper ground in both appearances, so a scanner can read them"),
]

# Hand decisions for the white faces: component id -> {selector substring: token}; applied to background: #fff.
OVERRIDES: dict[str, dict[str, str]] = {}

ROOT_SELECTOR = re.compile(r"^(?:\.[a-z]+\d{3}|\.(?:k|b|i|h|p|m|n|f|o|c|s|t|r|g|l|e)\d+)(?:\s*,\s*[^,]+)*$")


def is_canvas(selector: str) -> bool:
    """A rule that paints the ground of a component or a page (the block root, a page / screen / app wrapper) rather than a fill inside a card."""
    parts = [x.strip() for x in selector.split(",")]
    for part in parts:
        last = part.split()[-1] if part.split() else ""
        if re.fullmatch(r"\.(?:[a-z]+\d{3}|[kbihpmnfocstrgle]\d+)", last) or re.search(r"\.(?:page|pg|screen|app|wrap|shell|stage|phone|canvas)(?![\w-])", part):
            return True
    return False


def tint_of(c: str) -> str | None:
    """A pale tint used as a background: its own token when tools/tokens.py lists it (PASTELS), else the status tint when it is within 4 levels of one."""
    if c in tk.PASTELS:
        return "tint-" + c[1:].lower()
    for lit, name in STATUS_BG.items():
        if dist(c, lit) <= 4:
            return name
    return None


def white_background(h: Hit) -> str:
    sel, d = h.selector, h.decls
    s = sel.lower()
    shadows = d.get("box-shadow", "")
    blur_big = bool(re.search(r"\d+px\s+(\d+)px\s+(\d+)px", shadows)) and any(int(x) >= 16 for x in re.findall(r"\d+px\s+\d+px\s+(\d+)px", shadows))
    # a face lifted above a soft track: the selected pill of a segmented control or a tab
    if re.search(r"(\.on|\.sel|\.act|\.active|\.cur|\[aria-(?:pressed|selected|checked)=true\]|\.picked|\.chosen)(?![\w-])", s) and not re.search(r"(menu|pop|panel|sheet|dlg|modal)", s):
        return "var(--lift)"
    if re.search(r"(menu|popover|\.pop\b|\.pp\b|\.dd\b|dropdown|tooltip|\.tip\b|toast|\.dlg|dialog|modal|sheet|\.drawer|\.panel|\.pn\b|\.float)", s) or blur_big:
        return "var(--card3)" if blur_big else "var(--card2)"
    return "var(--card)"


TEXT_PASS = [
    (re.compile(r"(?<![\w-])(?:color|fill)\s*:\s*(?P<v>var\(--pd\))"), "var(--p-text)"),
    (re.compile(r"(?<![\w-])color\s*:\s*(?P<v>var\(--p\))(?![\w-])"), "var(--p-fg)"),
]
# a text colour used as a background (a badge, a danger button) is a fill: it carries white text, so it asks for the -fill token (the text token is a light step in the dark)
FILL_PASS = re.compile(r"(?P<head>(?<![\w-])background(?:-color|-image)?\s*:)(?P<v>[^;{}`\"'\n]*)")
FILL_OF = {"price": "price-fill", "dg": "danger-fill", "danger": "danger-fill", "ok": "ok-fill", "wn": "warn-fill", "warn": "warn-fill"}
DELETE = "<delete>"  # the whole declaration goes (a local --ok that only repeated the global token)


def map_hit(h: Hit) -> str | None:
    """The replacement for one colour literal, or None to leave it."""
    lit = h.lit
    fam = h.family
    low = lit.lower()
    if h.prop in CUSTOM_TOKEN:
        return DELETE if CUSTOM_TOKEN[h.prop] is None else f"var(--{CUSTOM_TOKEN[h.prop]})"
    if low.startswith("rgb"):
        m = RGBA.fullmatch(lit)
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        ap = round(a * 100)
        if (r, g, b) == (31, 35, 41):
            if a == 0:
                return "transparent"
            if fam == "shadow":
                return f"var(--sh{ap:02d})" if ap in tk.SHADOW_ALPHAS else None
            if fam in ("bg", "border"):
                if ap in tk.VEIL_ALPHAS:
                    return f"var(--veil{ap:02d})"
                if ap == 38:
                    return "var(--mask)"
                if ap == 58:
                    return "var(--mask2)"
                if ap == 88:
                    return "var(--inv-a)"
                if ap == 92 and fam == "bg":
                    return "color-mix(in srgb,var(--inv) 92%,transparent)"
                return f"color-mix(in srgb,var(--scrim) {ap}%,transparent)"
            return None
        if (r, g, b) == (255, 255, 255):
            if a == 0:
                return "transparent"
            if fam == "bg":
                return {85: "var(--glass)", 92: "var(--glass2)", 70: "var(--glass0)"}.get(ap, f"color-mix(in srgb,var(--card) {ap}%,transparent)")
            if fam == "shadow" and "inset" in h.value:
                return {85: "var(--hi)", 55: "var(--hi2)"}.get(ap)
            return None
        if (r, g, b) == (244, 241, 238):
            return "var(--page-glass)" if ap == 94 else None
        return None
    if low == "white":
        low = "#ffffff"
    c = norm(low)
    if c == "#FFFFFF":
        if fam == "text":
            return None
        if fam == "bg":
            return white_background(h)
        if fam in ("border", "shadow", "svg"):
            return "var(--card)"
        return None
    # --- chromatic exact values with a token
    if fam == "text" or (fam == "svg" and h.prop in ("fill", "stroke") and False):
        if c in STATUS_TEXT:
            return f"var(--{STATUS_TEXT[c]})"
        if c == "#B8443C":
            return "var(--price)"
    if fam in ("svg",):
        if c in STATUS_TEXT:
            return f"var(--{STATUS_TEXT[c]})"
        if c == "#B8443C":
            return "var(--price)"
    if fam in ("bg", "border") and c in DANGER_DARK:
        return f"color-mix(in srgb,var(--danger-fill) {round(DANGER_DARK[c] * 100)}%,#000)"
    if fam == "bg" and c == "#F5F6F8":
        return "var(--bg)" if is_canvas(h.selector) else "var(--n3)"
    if fam == "text" and (c in GOLD_INK or c in GOLD_INK2 or c in OK_INK):
        own_bg = h.decls.get("background", "") + h.decls.get("background-color", "")
        if re.search(r"#[0-9A-Fa-f]{3,6}", own_bg):  # brown text on a gold fill that stays gold in both appearances
            return None
        return "var(--gold-ink)" if c in GOLD_INK else "var(--gold-ink2)" if c in GOLD_INK2 else "var(--ok-ink)"
    if fam == "text" and c in EXACT_TEXT:
        return f"var(--{EXACT_TEXT[c]})"
    if fam == "text" and c not in STATUS_TEXT:
        for k, name in STATUS_TEXT.items():
            if dist(c, k) <= 22:
                return f"var(--{name})"
    if fam == "bg":
        t = tint_of(c)
        if t and "gradient(" in h.value and len(HEX.findall(h.value)) > 1:  # a pastel start of a gold / coloured gradient stays a literal
            t = None
        if t and c not in STATUS_BG:
            return f"var(--{t})"
        if c in STATUS_BG:
            return f"var(--{STATUS_BG[c]})"
        if c in STATUS_FILL:
            return f"var(--{STATUS_FILL[c]})"
        if c in DANGER_DARK:
            return f"color-mix(in srgb,var(--danger-fill) {round(DANGER_DARK[c] * 100)}%,#000)"
        if c == "#EDE7E4":
            return "var(--ph)"
        if c == "#1F2329":
            return "var(--inv)"
        if c == "#B8443C":
            return "var(--price-fill)"
    if fam == "border":
        if c in STATUS_LINE:
            return f"var(--{STATUS_LINE[c]})"
        if c in STATUS_TEXT:
            return f"var(--{STATUS_TEXT[c]})"
    if fam == "svg" and c == "#1F2329":
        return "var(--ink)"
    # --- greys
    if not is_greyish(c):
        return None
    if fam == "text" or (fam in ("svg", "shadow", "border") and lum(c) < 0.45):
        ladder = INKS if lum(c) < 0.6 else STEPS
    elif fam == "border":
        ladder = dict(STEPS)
        ladder["line"] = "#EEF0F3"
        ladder["line2"] = "#E6E8EC"
    else:
        ladder = STEPS
    if fam == "text" and lum(c) >= 0.6:  # a pale glyph colour (an empty star, a ghost number): the inactive-glyph token
        return "var(--off)"
    name, d = nearest(c, ladder)
    if name == "n4" and fam == "border":
        name = "line"
    if d <= NEAR:
        return f"var(--{name})"
    mixed = mix_between(c, ladder)
    return mixed


# ------------------------------------------------------------------------------------------------------------------------------------------
# The check: what the pass would still replace is a violation of "colours are tokens" (scripts/check_component_library.py calls this)
# ------------------------------------------------------------------------------------------------------------------------------------------


def source_files(src: Path) -> list[Path]:
    return sorted(p for p in list(src.glob("*.js")) + list(src.glob("*.css")) + list(src.glob("lib.template.html")) if p.name not in SKIP_FILES)


def violations(src: Path = SRC) -> list[dict]:
    """Every colour literal (and every theme-colour or status-colour var used the wrong way) that the pass would rewrite, outside KEEP.

    Each item: ``file``, ``line``, ``cid`` (component id or None), ``prop``, ``lit``, ``want`` (the token the pass would write)."""
    out: list[dict] = []
    for path in source_files(src):
        raw, hits = scan(path)
        line_of = lambda pos: raw.count("\n", 0, pos) + 1  # noqa: E731
        for h in hits:
            if any(f == path.name and snip in raw[max(0, h.start - 60):h.end + 20] for f, snip, _ in KEEP):
                continue
            new = map_hit(h)
            if new is None:
                continue
            out.append({"file": path.name, "line": line_of(h.start), "cid": h.cid, "prop": h.prop, "lit": h.lit, "want": "remove the declaration" if new == DELETE else new})
        masked = mask_interpolations(raw)
        ids = component_ids(raw)

        def cid_at(pos: int):
            found = None
            for at, i in ids:
                if at <= pos:
                    found = i
                else:
                    break
            return found

        for m in FILL_PASS.finditer(masked):
            for t in re.finditer(r"var\(--(price|dg|danger|ok|wn|warn)\)", m.group("v")):
                out.append({"file": path.name, "line": line_of(m.start("v")), "cid": cid_at(m.start("v")), "prop": "background", "lit": t.group(0), "want": f"var(--{FILL_OF[t.group(1)]})"})
        for rx, new in TEXT_PASS:
            for m in rx.finditer(masked):
                out.append({"file": path.name, "line": line_of(m.start("v")), "cid": cid_at(m.start("v")), "prop": "color", "lit": m.group("v"), "want": new})
    return out


# ------------------------------------------------------------------------------------------------------------------------------------------
# Driver
# ------------------------------------------------------------------------------------------------------------------------------------------


def run(write: bool, report: bool, left: bool, src: Path = SRC) -> int:
    total = collections.Counter()
    by_file = collections.Counter()
    by_comp = collections.defaultdict(int)
    table = collections.defaultdict(collections.Counter)
    unmapped = collections.defaultdict(collections.Counter)
    drift: list[str] = []
    for path in source_files(src):
        raw, hits = scan(path)
        edits = []
        for h in hits:
            if any(f == path.name and snip in raw[max(0, h.start - 60):h.end + 20] for f, snip, _ in KEEP):
                continue
            new = map_hit(h)
            key = (h.family, h.lit.upper() if h.lit.startswith("#") else h.lit.lower())
            if new is None:
                unmapped[key][(path.name, h.cid or "")] += 1
                continue
            if new == DELETE:
                end = h.dend + 1 if raw[h.dend:h.dend + 1] == ";" else h.dend
                edits.append((h.dstart, end, ""))
                table[key]["(declaration removed)"] += 1
                continue
            edits.append((h.start, h.end, new))
            table[key][new] += 1
            total[h.family] += 1
            by_file[path.name] += 1
            by_comp[h.cid or path.name] += 1
            if h.lit.startswith("#") and new.startswith("var(--") and new[6:-1] in {**STEPS, **INKS}:
                ladder = {**STEPS, **INKS}
                d = dist(norm(h.lit), ladder[new[6:-1]])
                if d:
                    drift.append(f"{path.name} {h.cid} {h.lit} -> {new} (max channel {d})")
        for m in FILL_PASS.finditer(mask_interpolations(raw)):
            for t in re.finditer(r"var\(--(price|dg|danger|ok|wn|warn)\)", m.group("v")):
                edits.append((m.start("v") + t.start(), m.start("v") + t.end(), f"var(--{FILL_OF[t.group(1)]})"))
                total["bg"] += 1
                table[("bg", t.group(0))][f"var(--{FILL_OF[t.group(1)]})"] += 1
        # theme colours used as text: the deep step and the main colour change meaning in the dark (a lighter step), so text asks for --p-text / --p-fg
        masked_all = mask_interpolations(raw)
        for rx, new in TEXT_PASS:
            for m in rx.finditer(masked_all):
                edits.append((m.start("v"), m.end("v"), new))
                total["text"] += 1
                table[("text", m.group("v"))][new] += 1
        if write and edits:
            edits.sort()
            out, last = [], 0
            for s, e, new in edits:
                if s < last:
                    raise SystemExit(f"overlap in {path.name} at {s}")
                out.append(raw[last:s])
                out.append(new)
                last = e
            out.append(raw[last:])
            path.write_bytes("".join(out).encode("utf-8"))
    if report or left:
        print("replaced:", dict(total), "in", len(by_comp), "components/files;", sum(by_file.values()), "literals")
        if report:
            for key, counter in sorted(table.items(), key=lambda kv: -sum(kv[1].values()))[:80]:
                print(f"  {key[0]:6s} {key[1]:24s} {dict(counter)}")
            print("drift (not exact):", len(drift))
            for d in drift[:40]:
                print("   ", d)
        print("left hard-coded:")
        for key, counter in sorted(unmapped.items(), key=lambda kv: -sum(kv[1].values()))[:120]:
            print(f"  {key[0]:6s} {key[1]:24s} {sum(counter.values()):4d}  {list(counter)[:3]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--left", action="store_true")
    ap.add_argument("--src", default=str(SRC), help="source directory (default src/); point it at an untouched copy to count what the pass changed")
    args = ap.parse_args(argv)
    return run(args.write, args.report or not args.write, args.left or not args.write, Path(args.src))


if __name__ == "__main__":
    raise SystemExit(main())
