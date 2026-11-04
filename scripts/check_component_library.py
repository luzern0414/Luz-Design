#!/usr/bin/env python3
"""Static completeness check of the component template library (references/component-library/src), no browser.

    py -X utf8 scripts/check_component_library.py [--src DIR] [--stats] [--warn-colours]

The library is plain JavaScript: ``def({ id: 'AD-TBL-001', ... })`` registers a component and ``guide('ad', 'TBL', [...])`` the "how to choose" table of
a category (the 52 first-generation templates in blocks1-3.js use ``add(tab, name, ...)`` and take their ids from ``LEGACY`` in taxonomy.js). This script
reads the source with a small JavaScript lexer (strings, template literals, comments, regular expressions) and checks, per component:

  * id ``DOM-CAT-NNN``, unique in the library, its category code is in taxonomy.js, numbers of one category run 1..N without a gap (``KNOWN_GAPS`` lists
    the gaps that exist for a reason; every other gap is an error);
  * every selector of its CSS starts with the block root class ``<dom><cat><NNN>`` in lower case (``adtbl001``): no bare ``.on`` or ``.btn``. A selector
    may also start with the placeholder the CSS helpers expand to the root (``&``, ``§``, ``@@``) or with ``.ixr:has(>root)``; the 52 first-generation
    templates keep their own root classes (``.k1`` ...), which must at least be one root per template (``LEGACY_ROOT``);
  * ``name`` at most 12 Chinese characters, ``style`` at most 6, ``fit`` and ``avoid`` not empty, ``kw`` at least 5 words;
  * no ``position:fixed`` and no ``transition:all`` in any CSS;
  * colours: a hex colour whose HSV saturation is above ``MAX_SATURATION`` and that is not a token or one of the fixed state colours of SPEC.md is
    an error (``--warn-colours`` makes it a warning), see ``SATURATION_NOTE``;
  * hard-coded neutral and status colours (dark appearance, SPEC.md section 4): a white or grey background, border, shadow or svg paint, a near-black or
    grey text colour, a status colour or its tint, ``rgba(31,35,41,.x)``, written as a literal instead of a token (``var(--card)``, ``var(--n6)``,
    ``var(--ink2)``, ``var(--ok-bg)``, ``var(--sh12)`` ...) is an error with its component id and line. What stays literal on purpose is white text
    (``color:#fff``), black shadows, chromatic accent colours and the list ``KEEP`` of ``tools/tokenize_colours.py`` (the exception list of README.md);
  * ``dark`` and ``light`` are the appearance switch (``<html class="dark">``): a component that uses them as a class name collides with it;

and per category: a ``guide(...)`` exists and every component it recommends is a real name of that category.

Prints ``component library: ok`` and exits 0 when nothing is wrong, else lists the ids and the reasons and exits 1.
"""
from __future__ import annotations

import argparse
import colorsys
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "references" / "component-library"
SRC = LIB / "src"
sys.path.insert(0, str(LIB / "tools"))  # tokenize_colours: the colour rules that the migration used are the rules of the check

# ---------------------------------------------------------------------------------------------------------------------------------------------
# What is allowed to differ from the rule, and why. Nothing is let through silently: a number that is not in these tables is an error.
# ---------------------------------------------------------------------------------------------------------------------------------------------

# Gaps in the number run of a category: {"AD-TBL": {numbers}} with the reason in a comment. None today: every category runs 1..N.
KNOWN_GAPS: dict[str, set[int]] = {}

# The 52 first-generation templates (blocks1-3.js, id from LEGACY in taxonomy.js) were written before the root-class rule and carry no ``kw``. They are kept
# as they are because other work refers to them by id; new components follow the rule. Their CSS must still hang off one root class per template.
LEGACY_REASON = "first-generation template (blocks1-3.js): own root class, no kw"

# Hex colours with HSV saturation above this are "loud". The low-saturation rule of SPEC.md applies to what covers an area; tiny accents are allowed to be
# stronger, but a hex colour above the ceiling is not an accent, it is a loud colour: the library has none today (the four hits of the first run were dark brown text,
# which MIN_VALUE now leaves out), so a new one is an error (see SATURATION_NOTE).
MAX_SATURATION = 0.80
MIN_VALUE = 0.45  # darker than this is read as a near-black tone (the 4 hits of #5a4010 on 2026-11-04 were dark brown text on gold), not as a vivid colour
# Fixed state colours of SPEC.md section 4 (and the neutral and price tokens). They are low-saturation by design or documented exceptions.
FIXED_COLOURS = {
    "#3f7d58", "#eaf3ee",  # success, success ground
    "#8a5a00", "#f7eedb",  # warning, warning ground
    "#a8433b", "#f8eceb", "#f8ecea",  # danger, danger ground
    "#6a727d", "#f2f3f5",  # neutral, neutral ground
    "#1f2329", "#5b6470", "#eef0f3", "#f5f6f8", "#b8443c",  # --ink --ink2 --line --bg --price
}
SATURATION_NOTE = ("MAX_SATURATION is a ceiling for the colour of what covers an area; accents (a 14 px badge, a rating star) may be stronger, so the ceiling is "
                   "high (0.80). Do not change 300 components to satisfy a lower number: read the list, fix the large areas, and keep the list short.")

# Components that only display (no data-ix / data-open / data-toast in the markup, no js hook): both are first-generation templates whose point is the look
# (a sheet of price styles, corner ribbons). The browser test asserts that exactly these two are idle; every other component has something to click.
KNOWN_STATIC = {"MP-PRC-001", "MP-PRC-003"}

NAME_MAX_CJK, STYLE_MAX_CJK, KW_MIN_WORDS = 12, 6, 5
ROOT_ALIASES = ("&", "§", "@@", ".@@")  # what the CSS helpers of the block files expand to the root class

# ---------------------------------------------------------------------------------------------------------------------------------------------
# A small JavaScript lexer: enough to find calls, split arguments and read string and template literals without being fooled by quotes in comments
# ---------------------------------------------------------------------------------------------------------------------------------------------

REGEX_BEFORE = set("(,=:[!&|?{};+-*%<>~^")


@dataclass
class Lit:
    start: int
    end: int
    kind: str  # 's' quote string, 't' template
    text: str  # cooked text; interpolations of a template are replaced by PLACEHOLDER
    dynamic: bool = False  # a template with interpolations


PLACEHOLDER = "\x00"
ESC = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def cook(raw: str) -> str:
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c != "\\" or i + 1 >= len(raw):
            out.append(c)
            i += 1
            continue
        d = raw[i + 1]
        if d == "u" and raw[i + 2 : i + 3] == "{":
            j = raw.find("}", i)
            out.append(chr(int(raw[i + 3 : j], 16)))
            i = j + 1
        elif d == "u":
            out.append(chr(int(raw[i + 2 : i + 6], 16)))
            i += 6
        elif d == "x":
            out.append(chr(int(raw[i + 2 : i + 4], 16)))
            i += 4
        elif d == "\n":
            i += 2
        else:
            out.append(ESC.get(d, d))
            i += 2
    return "".join(out)


class Lexed:
    """``code``: the source with the inside of strings, templates, comments and regular expressions blanked (quotes and back-ticks stay), same offsets.
    ``lits``: start offset -> Lit."""

    def __init__(self, text: str):
        self.text = text
        self.n = len(text)
        self.code = list(text)
        self.lits: dict[int, Lit] = {}
        end = self._code(0, False)
        if end != self.n:
            raise ValueError("lexer stopped before the end of the file")
        self.code = "".join(self.code)

    def _blank(self, a: int, b: int) -> None:
        for k in range(a, b):
            if self.code[k] != "\n":
                self.code[k] = " "

    def _code(self, i: int, until_brace: bool) -> int:
        text, n = self.text, self.n
        depth, prev, word = 0, "", ""
        while i < n:
            c = text[i]
            nxt = text[i + 1] if i + 1 < n else ""
            if c == "/" and nxt == "/":
                j = text.find("\n", i)
                j = n if j < 0 else j
                self._blank(i, j)
                i = j
                continue
            if c == "/" and nxt == "*":
                j = text.find("*/", i + 2)
                j = n if j < 0 else j + 2
                self._blank(i, j)
                i = j
                continue
            if c in "'\"":
                i = self._string(i, c)
                prev, word = "x", ""
                continue
            if c == "`":
                i = self._template(i)
                prev, word = "x", ""
                continue
            if c == "/" and (prev == "" or prev in REGEX_BEFORE or word in ("return", "typeof", "case", "of", "in")):
                i = self._regex(i)
                prev, word = "x", ""
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                if until_brace and depth == 0:
                    return i + 1
                depth -= 1
            if not c.isspace():
                prev = c
                word = word + c if (c.isalnum() or c in "_$") else ""
            else:
                pass
            i += 1
        return i

    def _string(self, i: int, q: str) -> int:
        text, j = self.text, i + 1
        while j < self.n and text[j] != q:
            if text[j] == "\\":
                j += 1
            elif text[j] == "\n":
                raise ValueError(f"unterminated string at {self.line(i)}")
            j += 1
        self._blank(i + 1, j)
        self.lits[i] = Lit(i, j + 1, "s", cook(text[i + 1 : j]))
        return j + 1

    def _template(self, i: int) -> int:
        text, j, chunks, dynamic = self.text, i + 1, [], False
        chunk = j
        while j < self.n and text[j] != "`":
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == "$" and text[j + 1 : j + 2] == "{":
                chunks.append(cook(text[chunk:j]))
                dynamic = True
                j = self._code(j + 2, True)
                chunk = j
                chunks.append(PLACEHOLDER)
                continue
            j += 1
        chunks.append(cook(text[chunk:j]))
        self._blank(i + 1, j)
        self.lits[i] = Lit(i, j + 1, "t", "".join(chunks), dynamic)
        return j + 1

    def _regex(self, i: int) -> int:
        text, j, in_class = self.text, i + 1, False
        while j < self.n:
            c = text[j]
            if c == "\\":
                j += 2
                continue
            if c == "[":
                in_class = True
            elif c == "]":
                in_class = False
            elif c == "/" and not in_class:
                break
            elif c == "\n":
                raise ValueError(f"unterminated regular expression at {self.line(i)}")
            j += 1
        self._blank(i + 1, j)
        return j + 1

    def line(self, i: int) -> int:
        return self.text.count("\n", 0, i) + 1

    # -- structure ------------------------------------------------------------------------------------------------------------------------
    def close(self, i: int) -> int:
        """Offset of the bracket that closes the one at ``i``."""
        pairs, stack = {"(": ")", "[": "]", "{": "}"}, []
        code = self.code
        for k in range(i, self.n):
            c = code[k]
            if c in pairs:
                stack.append(pairs[c])
            elif c in ")]}":
                if not stack or stack.pop() != c:
                    raise ValueError(f"brackets do not match near line {self.line(k)}")
                if not stack:
                    return k
        raise ValueError(f"bracket opened at line {self.line(i)} is never closed")

    def split(self, a: int, b: int, sep: str = ",") -> list[tuple[int, int]]:
        """Spans of the items of ``code[a:b]`` separated by ``sep`` at bracket depth 0."""
        out, depth, start = [], 0, a
        code = self.code
        for k in range(a, b):
            c = code[k]
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            elif c == sep and depth == 0:
                out.append((start, k))
                start = k + 1
        out.append((start, b))
        return [(s, e) for s, e in out if self.code[s:e].strip()]

    def lits_in(self, a: int, b: int) -> list[Lit]:
        return [lit for s, lit in sorted(self.lits.items()) if a <= s and lit.end <= b]

    def string(self, a: int, b: int) -> str | None:
        """The value of a span that is one literal or literals joined by ``+``; None when it is anything else (a call, a variable, an interpolation)."""
        parts = []
        for s, e in self.split(a, b, "+"):
            lead = len(self.code[s:e]) - len(self.code[s:e].lstrip())
            s2 = s + lead
            lit = self.lits.get(s2)
            if lit is None or lit.dynamic or self.code[lit.end : e].strip():
                return None
            parts.append(lit.text)
        return "".join(parts) if parts else None


# ---------------------------------------------------------------------------------------------------------------------------------------------
# Reading the library
# ---------------------------------------------------------------------------------------------------------------------------------------------

ID_RE = re.compile(r"^(MP|AD)-([A-Z]+)-(\d{3})$")
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")


@dataclass
class Comp:
    id: str
    file: str
    line: int
    legacy: bool = False
    name: str | None = ""
    style: str | None = ""
    fit: str | None = ""
    avoid: str | None = ""
    kw: str | None = ""
    css: list[str] = field(default_factory=list)  # CSS-looking literals of this component, interpolations as PLACEHOLDER
    html: list[str] = field(default_factory=list)  # literals of its html property
    has_js: bool = False
    has_html: bool = False
    dynamic_css: bool = False  # the css value is not a literal (a helper call): only its literal parts can be read here

    @property
    def dom(self) -> str:
        return self.id.split("-")[0].lower()

    @property
    def cat(self) -> str:
        return self.id.split("-")[1]

    @property
    def num(self) -> int:
        return int(self.id.split("-")[2])

    @property
    def root(self) -> str:
        return (self.dom + self.cat + f"{self.num:03d}").lower()

    @property
    def html_text(self) -> str:
        return "\n".join(self.html)


@dataclass
class Guide:
    dom: str
    cat: str
    file: str
    line: int
    rows: list[list[str | None]]


@dataclass
class Library:
    cats: dict[str, list[tuple[str, str]]]
    legacy: dict[str, str]
    comps: list[Comp]
    guides: list[Guide]
    helper_css: list[tuple[str, int, str]]  # (file, line, text) CSS-looking literals outside any component
    parse_errors: list[str]
    legacy_hooks: set[str] = field(default_factory=set)  # ids that blocks-zz-legacy-ix.js gives a js hook
    src: Path | None = None  # the directory that was read (the colour check reads the raw text of its files)


CSS_LIKE = re.compile(r"\{[^{}]*:[^{}]*\}")


def css_like(text: str) -> bool:
    return "{" in text and "}" in text and bool(CSS_LIKE.search(text.replace(PLACEHOLDER, "x")))


def read_taxonomy(src: Path) -> tuple[dict[str, list[tuple[str, str]]], dict[str, str]]:
    text = (src / "taxonomy.js").read_text(encoding="utf-8")
    cats: dict[str, list[tuple[str, str]]] = {}
    block = re.search(r"const CATS = \{(.*?)\n\}", text, re.S)
    if not block:
        raise ValueError("taxonomy.js: CATS not found")
    for dom in ("mp", "ad"):
        m = re.search(dom + r":\s*\[(.*?)\n\s*\],", block.group(1), re.S)
        if not m:
            raise ValueError(f"taxonomy.js: CATS.{dom} not found")
        cats[dom] = re.findall(r"\[\s*'([A-Z]+)'\s*,\s*'([^']*)'\s*\]", m.group(1))
    legacy_block = re.search(r"const LEGACY = \{(.*?)\n\}", text, re.S)
    legacy = dict(re.findall(r"'([^']+)'\s*:\s*'((?:MP|AD)-[A-Z]+-\d{3})'", legacy_block.group(1))) if legacy_block else {}
    return cats, legacy


def calls(lx: Lexed, names: tuple[str, ...]):
    """(name, start of the name, span of the argument list) of every call ``name(`` at code level."""
    pat = re.compile(r"(?<![\w$.])(" + "|".join(names) + r")\s*\(")
    for m in pat.finditer(lx.code):
        before = lx.code[max(0, m.start() - 9) : m.start()]
        if before.rstrip().endswith("function"):
            continue
        open_ = m.end() - 1
        yield m.group(1), m.start(), (open_ + 1, lx.close(open_))


def read_library(src: Path = SRC) -> Library:
    cats, legacy = read_taxonomy(src)
    comps: list[Comp] = []
    guides: list[Guide] = []
    helpers: list[tuple[str, int, str]] = []
    errors: list[str] = []
    hooks: set[str] = set()
    for path in sorted(src.glob("blocks*.js")):
        try:
            lx = Lexed(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.name}: cannot read the file: {exc}")
            continue
        taken: list[tuple[int, int]] = []
        try:
            for name, pos, (a, b) in calls(lx, ("def", "defx", "add", "guide", "L")):
                if name == "L" and path.name == "blocks-zz-legacy-ix.js":
                    first = lx.split(a, b)[0]
                    value = lx.string(*first)
                    if value:
                        hooks.add(value)
                elif name in ("def", "defx"):
                    comp = read_def(lx, path.name, a, b)
                    if comp:
                        comps.append(comp)
                        taken.append((pos, b + 1))
                elif name == "add" and path.name.startswith("blocks") and re.fullmatch(r"blocks[123]\.js", path.name):
                    comp = read_add(lx, path.name, a, b, legacy, errors)
                    if comp:
                        comps.append(comp)
                        taken.append((pos, b + 1))
                elif name == "guide":
                    g = read_guide(lx, path.name, a, b)
                    if g:
                        guides.append(g)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
        for lit in lx.lits.values():
            if css_like(lit.text) and not any(p <= lit.start < q for p, q in taken):
                helpers.append((path.name, lx.line(lit.start), lit.text))
    return Library(cats, legacy, comps, guides, helpers, errors, hooks, src)


def read_def(lx: Lexed, file: str, a: int, b: int) -> Comp | None:
    items = lx.split(a, b)
    if not items:
        return None
    s, e = items[0]
    obj = lx.code[s:e].strip()
    if not obj.startswith("{"):
        return None
    ob = s + lx.code[s:e].index("{")
    props = lx.split(ob + 1, lx.close(ob))
    fields: dict[str, tuple[int, int]] = {}
    for ps, pe in props:
        m = re.match(r"\s*([A-Za-z_$][\w$]*)\s*:", lx.code[ps:pe])
        if m:
            fields[m.group(1)] = (ps + m.end(), pe)
    if "id" not in fields:
        return None  # a wrapper that passes ``...o`` on
    cid = lx.string(*fields["id"])
    comp = Comp(id=cid or "?", file=file, line=lx.line(a))
    for key in ("name", "style", "fit", "avoid", "kw"):
        setattr(comp, key, lx.string(*fields[key]) if key in fields else "")
    comp.has_js = "js" in fields
    comp.has_html = "html" in fields
    if "css" in fields:
        cs, ce = fields["css"]
        comp.dynamic_css = lx.string(cs, ce) is None
        comp.css = [lit.text for lit in lx.lits_in(cs, ce) if css_like(lit.text)]
    if "html" in fields:
        comp.html = [lit.text for lit in lx.lits_in(*fields["html"])]
    return comp


def read_add(lx: Lexed, file: str, a: int, b: int, legacy: dict[str, str], errors: list[str]) -> Comp | None:
    args = lx.split(a, b)
    if len(args) < 7:
        return None
    name = lx.string(*args[1])
    cid = legacy.get(name or "")
    if not cid:
        errors.append(f"{file}:{lx.line(a)}: add() of a template that is not in LEGACY: {name!r}")
        return None
    comp = Comp(id=cid, file=file, line=lx.line(a), legacy=True, name=name, style=lx.string(*args[2]), fit=lx.string(*args[3]), avoid=lx.string(*args[4]), kw="")
    comp.css = [lit.text for lit in lx.lits_in(*args[5]) if css_like(lit.text)]
    comp.dynamic_css = lx.string(*args[5]) is None
    comp.has_html = True
    comp.html = [lit.text for lit in lx.lits_in(*args[6])]
    return comp


def read_guide(lx: Lexed, file: str, a: int, b: int) -> Guide | None:
    args = lx.split(a, b)
    if len(args) != 3:
        return None
    dom, cat = lx.string(*args[0]), lx.string(*args[1])
    rows_s, rows_e = args[2]
    code = lx.code[rows_s:rows_e]
    if dom not in ("mp", "ad") or not cat or "[" not in code:
        return None
    ob = rows_s + code.index("[")
    rows = []
    for rs, re_ in lx.split(ob + 1, lx.close(ob)):
        inner = lx.code[rs:re_]
        if "[" not in inner:
            continue
        rb = rs + inner.index("[")
        rows.append([lx.string(*cell) for cell in lx.split(rb + 1, lx.close(rb))])
    return Guide(dom, cat, file, lx.line(a), rows)


# ---------------------------------------------------------------------------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------------------------------------------------------------------------


def rule_preludes(css: str) -> list[str]:
    """Selector lists of every style rule of a CSS text (inside @media and @supports too; @keyframes and @font-face bodies are skipped)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out: list[str] = []

    def match(i: int) -> int:
        depth = 0
        for j in range(i, len(css)):
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
                if depth == 0:
                    return j
        return len(css) - 1

    def walk(text_start: int, text_end: int) -> None:
        i, start = text_start, text_start
        while i < text_end:
            c = css[i]
            if c == "{":
                j = match(i)
                prelude = re.sub(r"^(?:\x00+\s*\n\s*)+", "", css[start:i].strip())  # an interpolated block of rules in front of this one
                body = (i + 1, j)
                if prelude.startswith("@"):
                    if re.match(r"@(media|supports|container|layer)\b", prelude):
                        walk(*body)
                else:
                    out.append(prelude)
                i = start = j + 1
            elif c in ";}":
                i = start = i + 1
            else:
                i += 1

    walk(0, len(css))
    return out


def selectors_of(prelude: str) -> list[str]:
    out, depth, cur = [], 0, []
    for c in prelude:
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        if c == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    out.append("".join(cur).strip())
    return [s for s in out if s]


def selector_problem(sel: str, root: str | None) -> str | None:
    """None when the selector is anchored on the block root, else why not. ``root`` None: a shared helper, any root-shaped literal class is accepted."""
    sel = sel.lstrip(PLACEHOLDER + " \n\t") if re.match(PLACEHOLDER + r"+\s*\n", sel) else sel.strip()
    if not sel:
        return None
    if sel.startswith(ROOT_ALIASES) or sel.startswith(PLACEHOLDER) or sel.startswith(".%s" % PLACEHOLDER):
        return None
    if root:
        if re.match(r"\.%s(?![\w-])" % re.escape(root), sel):
            return None
        if re.match(r"\.ixr:has\(\s*>\s*(\.%s|§|&)" % re.escape(root), sel):
            return None
    elif re.match(r"\.[a-z]{3,}\d{3}(?![\w-])", sel) or re.match(r"\.ixr:has\(", sel):
        return None
    if sel.startswith(".ixr[data-id="):
        return None  # the library wrapper of this very component, selected by its id
    return f"selector not anchored on the block root: {sel[:60]}"


LEGACY_ROOT = re.compile(r"^\.([a-z]\d+)(?![\w-])")
LEGACY_FILES = {"blocks1.js", "blocks2.js", "blocks3.js", "blocks-zz-legacy-ix.js"}  # the first-generation templates and the hooks that add behaviour to them


def hex_colours(css: str) -> list[str]:
    out = []
    for m in re.finditer(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-fA-F\w-])", css):
        h = m.group(1).lower()
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h[:3])
        out.append("#" + h[:6])
    return out


def hardcoded_colours(src: Path) -> list[dict]:
    """Colour literals the token pass would still rewrite (white or grey faces and borders, status colours and tints, ink-coloured shadows ...), with the
    token each should be. The rules and the list of deliberate exceptions (KEEP) live in references/component-library/tools/tokenize_colours.py."""
    import tokenize_colours as rules  # noqa: PLC0415

    return rules.violations(src)


def is_loud(hex6: str) -> bool:
    """Saturated and bright enough to look vivid: HSV saturation above MAX_SATURATION and value at least MIN_VALUE (a near-black brown is not loud)."""
    r, g, b = (int(hex6[i : i + 2], 16) / 255 for i in (1, 3, 5))
    _, s, v = colorsys.rgb_to_hsv(r, g, b)
    return s > MAX_SATURATION and v >= MIN_VALUE


# ---------------------------------------------------------------------------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------------------------------------------------------------------------


def unknown_in_recommendation(cell: str, names: set[str]) -> str:
    """What is left of a guide's 推荐 cell after every real component name of the category (longest first) and the joiners ``/ + →`` are taken out."""
    rest = cell
    for name in sorted((n for n in names if n), key=len, reverse=True):
        rest = rest.replace(name, "\x01")
    return re.sub(r"[\s\x01/+→、，,；;()（）]+", " ", rest).strip()


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def check(lib: Library, strict_colours: bool = True) -> Report:
    rep = Report()
    err = rep.errors.append
    for e in lib.parse_errors:
        err(e)
    by_id: dict[str, list[Comp]] = {}
    for c in lib.comps:
        by_id.setdefault(c.id, []).append(c)
    cat_codes = {dom: {c for c, _ in rows} for dom, rows in lib.cats.items()}

    # --- ids ------------------------------------------------------------------------------------------------------------------------------
    for cid, items in by_id.items():
        if len(items) > 1:
            err(f"{cid}: id used {len(items)} times ({', '.join(f'{c.file}:{c.line}' for c in items)})")
    for c in lib.comps:
        m = ID_RE.match(c.id)
        if not m:
            err(f"{c.id} ({c.file}:{c.line}): id must look like MP-CARD-001 (DOM-CAT-three digits)")
            continue
        dom = m.group(1).lower()
        if m.group(2) not in cat_codes.get(dom, set()):
            err(f"{c.id}: category {m.group(2)} is not in taxonomy.js for {dom}")
    runs: dict[tuple[str, str], list[int]] = {}
    for c in lib.comps:
        if ID_RE.match(c.id):
            runs.setdefault((c.dom, c.cat), []).append(c.num)
    for (dom, cat), nums in sorted(runs.items()):
        have = set(nums)
        missing = set(range(1, max(have) + 1)) - have
        known = KNOWN_GAPS.get(f"{dom.upper()}-{cat}", set())
        if missing - known:
            err(f"{dom.upper()}-{cat}: numbers not continuous, missing {', '.join(f'{n:03d}' for n in sorted(missing - known))} (run is 001..{max(have):03d})")
        if known - missing:
            err(f"{dom.upper()}-{cat}: KNOWN_GAPS lists {sorted(known - missing)} but those numbers exist: update the table")

    # --- fields ---------------------------------------------------------------------------------------------------------------------------
    for c in lib.comps:
        for key, limit in (("name", NAME_MAX_CJK), ("style", STYLE_MAX_CJK)):
            value = getattr(c, key)
            if value is None:
                err(f"{c.id}: {key} is not a plain string, the check cannot read it")
            elif not value.strip():
                err(f"{c.id}: {key} is empty")
            elif len(CJK.findall(value)) > limit:
                err(f"{c.id}: {key} has {len(CJK.findall(value))} Chinese characters, at most {limit}: {value}")
        for key in ("fit", "avoid"):
            value = getattr(c, key)
            if value is None or not value.strip():
                err(f"{c.id}: {key} is empty or not a plain string")
        if not c.legacy:
            words = (c.kw or "").split()
            if len(words) < KW_MIN_WORDS:
                err(f"{c.id}: kw has {len(words)} words, at least {KW_MIN_WORDS}")
        if not c.has_html:
            err(f"{c.id}: no html")
    names: dict[tuple[str, str, str], str] = {}
    for c in lib.comps:
        key = (c.dom, c.cat, c.name or "")
        if key in names:
            err(f"{c.id}: name {c.name!r} is also the name of {names[key]} in the same category")
        names.setdefault(key, c.id)

    # --- css scope ------------------------------------------------------------------------------------------------------------------------
    unresolved = 0
    legacy_roots: dict[str, str] = {}
    for c in lib.comps:
        problems: list[str] = []
        roots_seen: set[str] = set()
        for text in c.css:
            for prelude in rule_preludes(text):
                for sel in selectors_of(prelude):
                    if c.legacy:
                        stripped = sel.strip()
                        m = LEGACY_ROOT.match(stripped)
                        if m:
                            roots_seen.add(m.group(1))
                        elif not (stripped.startswith(ROOT_ALIASES) or stripped.startswith(PLACEHOLDER)):
                            problems.append(f"legacy selector without its root class: {stripped[:50]}")
                    else:
                        bad = selector_problem(sel, c.root)
                        if bad:
                            problems.append(bad)
                        elif sel.strip().startswith(PLACEHOLDER):
                            unresolved += 1
        if c.legacy:
            if len(roots_seen) > 1:
                problems.append(f"more than one root class in a legacy template: {sorted(roots_seen)}")
            for r in roots_seen:
                if legacy_roots.setdefault(r, c.id) != c.id:
                    problems.append(f"root class .{r} is also used by {legacy_roots[r]}")
        elif not c.dynamic_css and not c.css:
            problems.append("no css")
        elif c.css and not any(c.root in t or "§" in t or "&" in t for t in c.css) and not c.dynamic_css:
            problems.append("css never mentions the block root class")
        for p in sorted(set(problems))[:6]:
            err(f"{c.id}: css: {p}")
    for file, line, text in lib.helper_css:
        for prelude in rule_preludes(text):
            for sel in selectors_of(prelude):
                if file in LEGACY_FILES:  # CSS that a first-generation file adds: it must hang off the root class of one of the templates
                    m = re.match(r"^\.([a-z]\d+)[a-z]?(?![\w-])", sel.strip())
                    bad = None if m and m.group(1) in legacy_roots else f"selector not anchored on the root class of a first-generation template: {sel.strip()[:60]}"
                else:
                    bad = selector_problem(sel, None)
                if bad:
                    err(f"{file}:{line}: shared css helper: {bad}")
    rep.stats["selectors starting with an interpolation (root given by a helper)"] = unresolved

    # --- css content ----------------------------------------------------------------------------------------------------------------------
    loud: dict[str, set[str]] = {}
    for c in lib.comps:
        text = "\n".join(c.css)
        if re.search(r"position\s*:\s*fixed", text) or re.search(r"position\s*:\s*fixed", c.html_text):
            err(f"{c.id}: position:fixed (a component is drawn inside its stage, not on the viewport)")
        if re.search(r"transition(?:-property)?\s*:[^;{}]*\ball\b", text):
            err(f"{c.id}: transition:all (list the properties)")
        for h in hex_colours(text):
            if h not in FIXED_COLOURS and is_loud(h):
                loud.setdefault(c.id, set()).add(h)
    for file, line, text in lib.helper_css:
        if re.search(r"position\s*:\s*fixed", text):
            err(f"{file}:{line}: shared css helper: position:fixed")
        if re.search(r"transition(?:-property)?\s*:[^;{}]*\ball\b", text):
            err(f"{file}:{line}: shared css helper: transition:all")
    # --- colours are tokens (the dark appearance needs every neutral and status colour to come from a variable) -----------------------------------
    hard = hardcoded_colours(lib.src) if lib.src else []
    rep.stats["hard-coded neutral or status colours"] = len(hard)
    rep.stats["hard-coded colours: ids"] = sorted({v["cid"] or v["file"] for v in hard})
    for v in hard[:60]:
        where = f"{v['cid']} ({v['file']}:{v['line']})" if v["cid"] else f"{v['file']}:{v['line']}"
        err(f"{where}: {v['prop']}: {v['lit']} is a hard-coded neutral or status colour, write {v['want']} (SPEC.md section 4: colours are tokens)")
    if len(hard) > 60:
        err(f"... and {len(hard) - 60} more hard-coded colours (py -X utf8 references/component-library/tools/tokenize_colours.py lists them with the token each one becomes)")
    for c in lib.comps:
        if re.search(r"class=[\"'][^\"']*\b(?:dark|light)\b", c.html_text) or re.search(r"\.(?:dark|light)(?![\w-])", "\n".join(c.css)):
            err(f"{c.id}: uses dark or light as a class name; they are the appearance switch (<html class=\"dark\">), pick another name (a dark stage is stage: 'dark', rendered as .night)")
    rep.stats["loud colours: components"] = len(loud)
    rep.stats["loud colours: hits"] = sum(len(v) for v in loud.values())
    rep.stats["loud colours: ids"] = {k: sorted(v) for k, v in sorted(loud.items())}
    if loud:
        msg = (f"{len(loud)} components use a hex colour with HSV saturation above {MAX_SATURATION:g} that is not a token or a fixed state colour "
               f"({sum(len(v) for v in loud.values())} hits; run with --stats to list them). {SATURATION_NOTE}")
        (err if strict_colours else rep.warnings.append)(msg)
    # What audit_rendered.py reports on a built page that uses the components: counted here so that the maintainer sees it before a prototype does. Warnings, not errors:
    # the components predate the rule, and changing them changes how they look.
    weights = [c.id for c in lib.comps if re.search(r"font-weight\s*:\s*(?!400\b|600\b|700\b)[\w.]+", "\n".join(c.css))]
    moving = [c.id for c in lib.comps if re.search(r"transition(?:-property)?\s*:[^;{}]*\b(?:width|left|top|margin|padding)\b", "\n".join(c.css))]
    rep.stats["font weights outside 400/600/700"] = weights
    rep.stats["transitions on layout properties"] = moving
    for found, what in ((weights, "a font-weight outside 400/600/700"), (moving, "a transition on width, left, top, margin or padding")):
        if found:
            rep.warnings.append(f"{len(found)} components use {what} (audit_rendered.py reports it on a page built from them): " + ", ".join(found[:8]) + (" ..." if len(found) > 8 else ""))

    # --- guides ---------------------------------------------------------------------------------------------------------------------------
    names_of: dict[tuple[str, str], set[str]] = {}
    for c in lib.comps:
        names_of.setdefault((c.dom, c.cat), set()).add(c.name or "")
    guide_of: dict[tuple[str, str], Guide] = {}
    for g in lib.guides:
        guide_of[(g.dom, g.cat)] = g  # the last one wins, like GUIDES[...] = rows
    for dom, rows in lib.cats.items():
        for code, title in rows:
            if (dom, code) not in names_of:
                continue  # a category without components needs no guide (and shows no tab)
            g = guide_of.get((dom, code))
            if not g:
                err(f"{dom.upper()}-{code}: no guide('{dom}', '{code}', [...]) (the 怎么选 table of the category)")
                continue
            if not 3 <= len(g.rows) <= 10:
                err(f"{dom.upper()}-{code}: guide has {len(g.rows)} rows, expected 3 to 10 ({g.file}:{g.line})")
            for row in g.rows:
                if len(row) != 3 or any(not (cell or "").strip() for cell in row):
                    err(f"{dom.upper()}-{code}: guide row is not [场景, 推荐, 原因] with three filled cells ({g.file}:{g.line}): {row}")
                    continue
                left = unknown_in_recommendation(row[1] or "", names_of[(dom, code)])
                if left:
                    err(f"{dom.upper()}-{code}: guide recommends 「{row[1]}」 but 「{left}」 is not a component name of the category ({g.file}:{g.line})")
    for (dom, code) in guide_of:
        if code not in cat_codes.get(dom, set()):
            err(f"guide('{dom}', '{code}'): category not in taxonomy.js")

    # --- stats ----------------------------------------------------------------------------------------------------------------------------
    total = len(lib.comps)
    rep.stats["total"] = total
    for dom in ("mp", "ad"):
        rep.stats[dom.upper()] = sum(1 for c in lib.comps if c.dom == dom)
    rep.stats["by category"] = {f"{dom.upper()}-{code}": sum(1 for c in lib.comps if c.dom == dom and c.cat == code) for dom, rows in lib.cats.items() for code, _ in rows}
    rep.stats["legacy templates"] = sum(1 for c in lib.comps if c.legacy)
    rep.stats["known gaps"] = {k: sorted(v) for k, v in KNOWN_GAPS.items()}
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", default=str(SRC), help="source directory (default references/component-library/src)")
    ap.add_argument("--stats", action="store_true", help="print the statistics, the list of loud colours included")
    ap.add_argument("--warn-colours", action="store_true", help="report loud colours as a warning instead of an error")
    a = ap.parse_args(argv)
    try:
        lib = read_library(Path(a.src))
    except (ValueError, OSError) as exc:
        print(f"component library: cannot read the source: {exc}")
        return 1
    rep = check(lib, not a.warn_colours)
    if a.stats or rep.errors:
        s = rep.stats
        print(f"components: {s['total']} (MP {s['MP']}, AD {s['AD']}; first-generation {s['legacy templates']})")
        print("by category: " + ", ".join(f"{k} {v}" for k, v in s["by category"].items() if v))
        print("known gaps: " + (", ".join(f"{k} {v}" for k, v in s["known gaps"].items()) or "none"))
        print(f"selectors rooted by a helper placeholder: {s['selectors starting with an interpolation (root given by a helper)']}")
        print(f"loud colours: {s['loud colours: hits']} hits in {s['loud colours: components']} components (HSV saturation > {MAX_SATURATION:g})")
        print(f"hard-coded neutral or status colours (should be tokens): {s['hard-coded neutral or status colours']}")
        if a.stats:
            for cid, colours in s["loud colours: ids"].items():
                print(f"  {cid}: {' '.join(colours)}")
    for w in rep.warnings:
        print("warning: " + w)
    if rep.errors:
        print(f"component library: {len(rep.errors)} problems")
        for e in rep.errors:
            print("  " + e)
        return 1
    print("component library: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
