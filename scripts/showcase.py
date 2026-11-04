"""Showcase documents: proposals, architecture atlases, feature lists and manuals that are read on screen and printed.

One spec -> one display page (HTML, responsive) and one paged PDF. The look comes from the theme and the rules in
file-design.html 系统架构图册; this module only implements them:

* a linear icon block before every section title (visual-design.html 图标底块), one set of icons for all documents;
* components instead of walls of text: stat tiles, cards, steps, callouts, scope columns, gantt, figures;
* layered architecture, swimlane and deployment figures drawn as vector, text never below 14 px;
* tables whose alignment is decided per column, never per cell;
* a packer that fills pages: sections share pages, tall blocks look ahead for a block that fits, tables split by rows with
  a repeated header, figures shrink a little; a page that stays mostly empty is reported as an error.
"""
from __future__ import annotations

import html
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any

import showcase_icons as I

HERE = Path(__file__).resolve().parent
THEMES = HERE.parent / "references" / "themes.json"
FONT = '"Microsoft YaHei"'
E = html.escape

# Page geometry in CSS px (96 dpi). Content box = page minus margins.
PAGE = {
    "portrait": {"size": "A4 portrait", "margin": "16mm 14mm 18mm", "w": 684, "h": 984},
    "landscape": {"size": "A4 landscape", "margin": "12mm 14mm 16mm", "w": 1012, "h": 674},
}


# --------------------------------------------------------------------------------------------- colour
def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def tokens(theme: str) -> dict[str, str]:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    th, sh = data["themes"][theme], data["shared"]
    scale = th.get("scale") or []
    primary, press, tint1 = th["action"], th["actionPress"], th["actionTint"]
    tint2 = scale[1] if len(scale) > 1 else mix(tint1, primary, 0.28)
    tint3 = scale[2] if len(scale) > 2 else mix(tint1, primary, 0.5)
    return {
        "primary": primary, "press": press, "tint1": tint1, "tint2": tint2, "tint3": tint3, "canvas": th["canvas"],
        "accent": th.get("accent", primary), "accentTint": th.get("accentTint", tint1),
        "sage": sh.get("sage", ""), "sageTint": sh.get("sageTint", ""), "info": sh.get("info", ""), "infoTint": sh.get("infoTint", ""),
        "ink": sh["ink"], "ink2": sh["ink2"], "ink3": sh["ink3"], "line": sh["line"], "surface": sh.get("surface", "#FFFFFF"),
        "success": sh["success"], "successTint": sh["successTint"], "warning": sh["warning"], "warningTint": sh["warningTint"],
        "danger": sh["danger"], "dangerTint": sh["dangerTint"],
    }


# --------------------------------------------------------------------------------------------- text helpers
def width(text: Any) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(text))


def wrap(text: str, limit: int) -> list[str]:
    """Hard wrap by display width (CJK 2 units); keeps ASCII words together when possible."""
    lines, cur = [], ""
    for token in re.findall(r"[A-Za-z0-9_.\-/:+%]+|.", str(text)):
        if width(cur + token) > limit and cur:
            lines.append(cur)
            cur = token.lstrip()
        else:
            cur += token
    return lines + ([cur] if cur else [])


def column_alignments(columns: list[str], rows: list[list[Any]], formal: bool = False) -> list[str]:
    """One alignment per column, header included: amounts right, values of at most 6 characters centred, anything longer left. Never per cell.

    A formal document keeps it calmer: text is always left, and only columns of markers (是、—、1、2、3) are centred."""
    out = []
    for i, head in enumerate(columns):
        cells = [str(r[i]) for r in rows if i < len(r) and r[i] not in (None, "")]
        amounts = bool(cells) and all(re.fullmatch(r"[+-]?[\d,]+(\.\d+)?[%元万]?", c) for c in cells)
        if amounts and any(re.search(r"[.,%元万]", c) for c in cells):
            out.append("r")
        elif formal:
            out.append("c" if cells and all(re.fullmatch(r"—|是|否|✓|\d{1,3}", c) for c in cells) else "l")
        elif amounts:
            out.append("r")
        elif max([width(c) for c in cells] + [0]) <= 12:
            out.append("c")
        else:
            out.append("l")
    return out


# --------------------------------------------------------------------------------------------- css
def css(t: dict[str, str], orientation: str, formal: bool = False, atlas: bool = False) -> str:
    pg = PAGE[orientation]
    sheet = (f"""
:root{{--primary:{t['primary']};--press:{t['press']};--tint1:{t['tint1']};--tint2:{t['tint2']};--tint3:{t['tint3']};--ink:{t['ink']};--ink2:{t['ink2']};--ink3:{t['ink3']};--line:{t['line']};--canvas:{t['canvas']};--accent-tint:{t['accentTint']}}}
@page{{size:{pg['size']};margin:{pg['margin']}}}
*{{box-sizing:border-box}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{margin:0;background:#fff;color:var(--ink);font:16px/1.75 {FONT},sans-serif}}
.doc{{max-width:{'880px' if orientation == 'portrait' else '1100px'};margin:0 auto;padding:40px 24px 64px}}
.hero{{display:flex;flex-direction:column;gap:18px;margin-bottom:28px}}
.hero-head{{display:flex;align-items:center;gap:16px}}
h1{{margin:0;font-size:32px;line-height:1.25;font-weight:700;color:var(--ink)}}
.ib{{flex:none;display:inline-flex;align-items:center;justify-content:center;background:var(--tint1);border-radius:12px;color:var(--press)}}
.ib-lg{{width:56px;height:56px;border-radius:16px}}.ib-md{{width:40px;height:40px;border-radius:12px}}.ib-sm{{width:32px;height:32px;border-radius:8px}}
.ib svg{{display:block}}
section{{margin:0 0 32px}}
.sh{{display:flex;align-items:center;gap:12px;margin:0 0 12px;font-size:24px;line-height:1.3;font-weight:700}}
.lead{{margin:0 0 14px;color:var(--ink2);font-size:16px}}
p{{margin:0 0 12px}}
.blk{{margin:0 0 16px}}
.stats{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:12px}}
.tile{{background:var(--tint1);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:2px}}
.tile .tv{{font-size:32px;line-height:1.2;font-weight:700;color:var(--press);font-variant-numeric:tabular-nums}}
.tile .tv small{{font-size:16px;font-weight:600;margin-left:4px}}
.tile .tl{{font-size:14px;line-height:1.5;color:var(--ink2)}}
.tile .ti{{margin-bottom:4px}}
.cards{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:12px}}
.card{{border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:8px;break-inside:avoid;background:#fff}}
.card-h{{display:flex;align-items:center;gap:10px}}
.card-t{{font-size:16px;line-height:1.4;font-weight:600}}
.card-x{{font-size:14px;line-height:1.6;color:var(--ink2)}}
.chip{{display:inline-block;font-size:14px;line-height:22px;padding:0 10px;border-radius:999px;background:var(--tint1);color:var(--press);font-weight:600;white-space:nowrap}}
.chip.out{{background:#fff;border:1px solid var(--tint3)}}
.steps{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:12px 0}}
.step{{position:relative;padding:0 10px 0 0;display:flex;flex-direction:column;gap:6px}}
.step .sn{{display:flex;align-items:center;gap:8px}}
.step .num{{flex:none;width:30px;height:30px;border-radius:50%;background:var(--tint1);border:2px solid var(--primary);color:var(--press);font-weight:600;font-size:14px;display:flex;align-items:center;justify-content:center}}
.step .bar{{flex:1;height:2px;background:var(--tint3);border-radius:4px}}
.step:last-child .bar,.step.endrow .bar{{background:transparent}}
.step .st{{font-size:16px;line-height:1.4;font-weight:600}}
.step .sx{{font-size:14px;line-height:1.6;color:var(--ink2)}}
.callout{{background:var(--tint1);border-left:4px solid var(--primary);border-radius:12px;padding:12px 16px;display:flex;gap:12px;align-items:flex-start}}
.callout p{{margin:0}}
.scope{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.scope .col{{border-radius:12px;padding:14px 16px;border:1px solid var(--line)}}
.scope .col.in{{background:var(--tint1);border-color:transparent}}
.scope h3{{margin:0 0 8px;font-size:16px;line-height:1.4;font-weight:600;display:flex;gap:8px;align-items:center}}
.scope ul{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}}
.scope li{{display:flex;gap:8px;align-items:flex-start;font-size:14px;line-height:1.6}}
.scope li svg{{flex:none;margin-top:2px}}
.checks{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:8px 20px;counter-reset:c}}
.check{{display:flex;gap:10px;align-items:flex-start;font-size:14px;line-height:1.6;padding:6px 0;border-bottom:1px solid var(--line)}}
.check .num{{flex:none;width:24px;height:24px;border-radius:50%;background:var(--tint1);border:1.5px solid var(--primary);color:var(--press);font-weight:600;font-size:14px;line-height:21px;text-align:center}}
ul.bul{{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px}}
ul.bul li{{display:flex;gap:8px;align-items:flex-start}}
ul.bul li svg{{flex:none;margin-top:4px}}
.twrap{{border:1px solid var(--line);border-radius:12px;overflow:hidden}}
table.tbl{{width:100%;border-collapse:collapse;table-layout:fixed}}
.tbl th{{background:var(--tint1);color:var(--press);font-weight:600;font-size:14px;line-height:1.5;padding:10px 14px;text-align:center;vertical-align:middle}}
.tbl td{{font-size:14px;line-height:1.6;padding:9px 14px;border-top:1px solid var(--line);vertical-align:middle;word-break:keep-all;overflow-wrap:anywhere}}
.tbl td.c,.tbl th.c{{text-align:center}}.tbl td.l,.tbl th.l{{text-align:left}}.tbl td.r,.tbl th.r{{text-align:right;font-variant-numeric:tabular-nums}}
.tbl td.k{{font-weight:600}}
.tbl tr{{break-inside:avoid}}
.tbl tr.grp td{{background:var(--tint1);border-top:1px solid var(--tint3);padding:8px 14px;text-align:left}}
.grp-in{{display:flex;align-items:center;gap:12px}}.grp-t{{font-size:16px;font-weight:600;color:var(--ink)}}.g-sum{{font-size:14px;color:var(--ink2);font-weight:400}}
.tbl thead{{display:table-header-group}}
.cap{{font-size:14px;line-height:1.5;color:var(--ink2);text-align:center;margin-top:6px}}
.tcap{{font-size:14px;line-height:1.5;font-weight:600;color:var(--ink);text-align:center;margin:0 0 6px}}
figure{{margin:0}}
figure svg{{display:block;width:100%;height:auto;margin:0 auto}}
.gantt{{border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14px}}
.g-head,.g-row{{display:grid;grid-template-columns:150px 1fr;align-items:center}}
.g-head{{background:var(--tint1);color:var(--press);font-weight:600}}
.g-head>div,.g-row>div{{padding:8px 12px}}
.g-row{{border-top:1px solid var(--line)}}
.g-track{{position:relative;height:34px;display:grid;grid-template-columns:repeat(var(--total),1fr)}}.g-track i{{position:absolute;top:0;bottom:0;width:1px;background:var(--line)}}
.g-bar{{align-self:center;position:relative;height:22px;border-radius:8px;background:var(--tint1);border:2px solid var(--primary);margin:0 1px}}
.g-bar.ms{{background:#fff;border-width:2.5px}}
.g-note{{align-self:center;grid-row:1;white-space:nowrap;font-size:14px;line-height:1.4;color:var(--ink2);padding:0 8px}}.g-note.l{{text-align:right}}.g-bar{{grid-row:1}}
.g-scale{{display:grid;grid-template-columns:repeat(var(--total),1fr);color:var(--press);font-weight:600;padding:8px 12px 8px 0;text-align:left}}
.hero-scene svg{{display:block;width:100%;height:auto;border-radius:16px}}
.image img{{display:block;width:100%;height:auto;border-radius:12px}}
@media (max-width:768px){{.doc{{padding:24px 16px 48px}}.stats,.cards,.steps,.checks{{grid-template-columns:1fr 1fr}}.scope{{grid-template-columns:1fr}}.g-head,.g-row{{grid-template-columns:96px 1fr}}h1{{font-size:26px}}}}
@media print{{.doc{{max-width:none;padding:0}}section{{margin-bottom:0}}}}
.page{{width:{pg['w']}px;height:{pg['h']}px;overflow:hidden;break-after:page;break-inside:avoid;position:relative}}
.page:last-child{{break-after:auto}}
.u{{display:flow-root}}
.vh{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}
.hero.nohead{{margin:0}}
""" + (FORMAL_CSS.replace("%H%", str(pg["h"])) if formal else "") + (ATLAS_CSS if atlas else ""))
    if atlas:                                # no bold in an atlas: hierarchy comes from size, colour and the Light title
        sheet = sheet.replace("font-weight:600", "font-weight:400").replace("font-weight:700", "font-weight:400")
    return sheet


# Atlas (系统架构图册): the formal document with a calm, refined look: the theme's own light tints for table heads and rules, hairlines
# instead of boxes. One ink for every word (titles, captions, table heads), one weight (400), one alignment rule: the hierarchy comes from size alone.
ATLAS_CSS = """
body{color:var(--ink)}
h1{font-size:30px;font-weight:400;color:var(--ink)}
.sh{font-size:20px;font-weight:400;color:var(--ink);margin:0 0 14px;padding:0 0 8px;border-bottom:1px solid var(--line)}
.sub{color:var(--ink)}
.tcap{color:var(--ink2);text-align:center;margin:0 0 8px}
.cap{color:var(--ink2)}
.twrap{border:1px solid var(--line);border-radius:8px;overflow:hidden}
.tbl th{background:var(--tint1);color:var(--ink);padding:10px 14px}
.tbl td{color:var(--ink);padding:10px 14px;border-top:1px solid var(--line)}
.tbl td.k{color:var(--ink);background:none}
"""


# Formal documents (proposals sent to a client, architecture books): text and tables only. No icon before any title, no stat
# tiles, cover scene or card icons; chapters are numbered, titles carry a hairline, a contents list opens a proposal.
FORMAL_CSS = """
body{color:#000}
h1{font-size:30px;color:#000}
.hero{gap:0;margin-bottom:18px}.hero-head{gap:0}
.sh{font-size:22px;gap:0;margin:0 0 10px;padding:0;border:0;color:#000}
section{margin:0 0 22px}
.sub{margin:8px 0 8px;padding:0;border:0;font-size:17px;line-height:1.4;font-weight:600;color:#000}
.dot{flex:none;width:6px;height:6px;border-radius:50%;background:#000;margin-top:11px}
.tcap,.cap{color:#000}
.card-h{gap:0}
.card{border-color:#999}
.callout{background:none;border:1px solid #000;border-radius:0}
.step .num,.check .num{background:none;border-color:#000;color:#000}
.step .bar{background:#999}
.cover{height:%H%px;display:flex;align-items:center;justify-content:center;text-align:center}
.cover-in{padding-bottom:10%}
.cover h1{font-size:38px;line-height:1.4;margin:0 0 16px}
.cover-sub{font-size:22px;margin:0 0 64px}
.cover-info{display:inline-flex;flex-direction:column;gap:10px;font-size:16px;text-align:left}
.ci{display:flex;gap:14px}.cl{min-width:5em;font-weight:700}
.toc{height:%H%px}
.toc-h{display:flex;justify-content:center;margin:0 0 26px;font-size:26px;line-height:1.3;font-weight:700;color:#000}
.toc a{display:flex;align-items:center;gap:6px;text-decoration:none;color:#000;font-size:17px;line-height:2.4}
.toc .tn{flex:none;min-width:2.4em}
.toc .tl{flex:1;align-self:flex-end;margin-bottom:12px;border-bottom:1.5px dotted #000}
.toc .tp{flex:none;min-width:2em;text-align:right;font-variant-numeric:tabular-nums}
"""


# --------------------------------------------------------------------------------------------- icon helpers
def iblock(name: str, t: dict[str, str], size: str = "md") -> str:
    px = {"lg": 30, "md": 22, "sm": 18}[size]
    return f'<span class="ib ib-{size}">{I.svg(name, size=px, color=t["press"], fill=t["tint3"])}</span>'


def icon_inline(name: str, t: dict[str, str], size: int = 16, color: str | None = None) -> str:
    return I.svg(name, size=size, color=color or t["press"])


def favicon(t: dict[str, str], name: str) -> str:
    face, lines = I.ICONS[name]
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='{t['tint1']}'/>"
           f"<g transform='translate(4 4)' fill='none' stroke='{t['press']}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>{lines}</g></svg>")
    return "data:image/svg+xml," + svg.replace("#", "%23").replace("<", "%3C").replace(">", "%3E")


# --------------------------------------------------------------------------------------------- blocks
class Ctx:
    def __init__(self, t: dict[str, str], orientation: str, formal: bool = False, atlas: bool = False) -> None:
        self.t, self.orientation, self.formal, self.atlas = t, orientation, formal, atlas
        self.fig = 0
        self.tbl = 0


def b_text(b: dict, ctx: Ctx) -> str:
    return f'<div class="blk" data-flex="1"><p>{E(b["text"])}</p></div>'


def b_bullets(b: dict, ctx: Ctx) -> str:
    mark = '<i class="dot"></i>' if ctx.formal else icon_inline('check', ctx.t, 16)
    items = "".join(f"<li>{mark}<span>{E(i)}</span></li>" for i in b["items"])
    return f'<div class="blk" data-flex="1"><ul class="bul">{items}</ul></div>'


def b_stats(b: dict, ctx: Ctx) -> str:
    items = b["items"]
    def value(v: Any) -> str:
        m = re.fullmatch(r"([\d.,–\-+%/]+)\s*(\D.*)?", str(v))
        return f'{E(m.group(1))}<small>{E(m.group(2))}</small>' if m and m.group(2) else E(str(v))

    def ico(i: dict) -> str:
        return "" if ctx.formal else f'<span class="ti">{icon_inline(i.get("icon", "target"), ctx.t, 20)}</span>'

    tiles = "".join(f'<div class="tile">{ico(i)}<span class="tv">{value(i["value"])}</span><span class="tl">{E(i["label"])}</span></div>' for i in items)
    return f'<div class="blk" data-flex="1"><div class="stats" style="--n:{min(len(items), 4)}">{tiles}</div></div>'


def b_cards(b: dict, ctx: Ctx) -> str:
    cols = int(b.get("cols", min(3, len(b["items"]))))
    out = []
    for i in b["items"]:
        tag = f'<span class="chip">{E(i["tag"])}</span>' if i.get("tag") else ""
        icon = "" if ctx.formal else iblock(i.get("icon") or I.pick(i["title"]), ctx.t, "sm")
        out.append(f'<div class="card"><div class="card-h">{icon}<span class="card-t">{E(i["title"])}</span>{tag}</div><div class="card-x">{E(i["text"])}</div></div>')
    return f'<div class="blk" data-split="grid"><div class="cards" style="--n:{cols}">{"".join(out)}</div></div>'


def b_steps(b: dict, ctx: Ctx) -> str:
    items = b["items"]
    cols = int(b.get("cols", min(4, len(items))))
    out = []
    for k, i in enumerate(items, 1):
        end = " endrow" if k % cols == 0 else ""
        out.append(f'<div class="step{end}"><div class="sn"><span class="num">{k}</span><span class="bar"></span></div><div class="st">{E(i["title"])}</div><div class="sx">{E(i["text"])}</div></div>')
    return f'<div class="blk" data-split="grid"><div class="steps" style="--n:{cols}">{"".join(out)}</div></div>'


def b_callout(b: dict, ctx: Ctx) -> str:
    icon = "" if ctx.formal else icon_inline(b.get("icon", "info"), ctx.t, 22)
    return f'<div class="blk" data-flex="1"><div class="callout">{icon}<p>{E(b["text"])}</p></div></div>'


def b_scope(b: dict, ctx: Ctx) -> str:
    def col(kind: str, spec: dict, icon: str, color: str) -> str:
        items = "".join(f"<li>{I.svg(icon, size=16, color=color)}<span>{E(x)}</span></li>" for x in spec["items"])
        return f'<div class="col {kind}"><h3>{icon_inline("check" if kind == "in" else "close", ctx.t, 18, color)}{E(spec["title"])}</h3><ul>{items}</ul></div>'
    return f'<div class="blk" data-flex="1"><div class="scope">{col("in", b["in"], "check", ctx.t["press"])}{col("out", b["out"], "close", ctx.t["ink3"])}</div></div>'


def b_checks(b: dict, ctx: Ctx) -> str:
    cols = int(b.get("cols", 2))
    items = "".join(f'<div class="check"><span class="num">{k}</span><span>{E(x)}</span></div>' for k, x in enumerate(b["items"], 1))
    return f'<div class="blk" data-split="grid"><div class="checks" style="--n:{cols}">{items}</div></div>'


def table_html(columns: list[str], rows: list[Any], *, widths: list[float] | None = None, first_key: bool = True, t: dict[str, str] | None = None, formal: bool = False) -> str:
    """Rows are lists of cells, or ``{"group": name, "icon": icon, "text": summary}`` which draws a full-width band (a module
    heading inside one continuous table, so the table can break anywhere without wasting a page)."""
    data_rows = [r for r in rows if not isinstance(r, dict)]
    al = column_alignments(columns, data_rows, formal)
    if widths:
        total = float(sum(widths))
        ws = [w / total * 100 for w in widths]
    else:
        weights = []
        for i, h in enumerate(columns):
            longest = max([width(h)] + [width(r[i]) for r in data_rows if i < len(r)])
            weights.append(min(max(longest, 10), 56) + 6)
        total = sum(weights)
        ws = [w / total * 100 for w in weights]
    cols = "".join(f'<col style="width:{w:.1f}%">' for w in ws)
    head = "".join(f'<th class="{al[i] if formal else "c"}">{E(h)}</th>' for i, h in enumerate(columns))     # a formal head sits over its column
    body = []
    for r in rows:
        if isinstance(r, dict):
            icon = iblock(r.get("icon") or I.pick(r["group"]), t, "sm") if t else ""
            text = f'<span class="g-sum">{E(r["text"])}</span>' if r.get("text") else ""
            body.append(f'<tr class="grp"><td colspan="{len(columns)}"><div class="grp-in">{icon}<span class="grp-t">{E(r["group"])}</span>{text}</div></td></tr>')
            continue
        tds = []
        for i, _ in enumerate(columns):
            v = r[i] if i < len(r) else ""
            text = "—" if v in (None, "") else str(v)
            cls = al[i] + (" k" if first_key and i == 0 else "")
            if text in {"基础", "可选"} and al[i] == "c":
                text_html = f'<span class="chip{"" if text == "基础" else " out"}">{E(text)}</span>'
            else:
                text_html = E(text).replace("\n", "<br>")
            tds.append(f'<td class="{cls}">{text_html}</td>')
        body.append("<tr>" + "".join(tds) + "</tr>")
    return f'<div class="twrap"><table class="tbl"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _table_caption(b: dict, ctx: Ctx) -> str:
    """The title above a table: 表 N　name. A table that runs over a page break gets the same line with （续） on the next page."""
    if not b.get("caption"):
        return ""
    ctx.tbl += 1
    return f'<div class="tcap">表 {ctx.tbl}　{E(b["caption"])}</div>'


def b_table(b: dict, ctx: Ctx) -> str:
    return f'<div class="blk" data-split="rows">{_table_caption(b, ctx)}{table_html(b["columns"], b["rows"], widths=b.get("widths"), first_key=b.get("first_key", True), t=None if ctx.formal else ctx.t, formal=ctx.formal)}</div>'


def b_matrix(b: dict, ctx: Ctx) -> str:
    yes = "是" if ctx.formal else "✓"      # formal documents write the word, others draw a check mark
    rows = [[r[0]] + [(yes if v in (True, "✓", "y", "是") else "—" if v in (False, "", None, "—") else v) for v in r[1:]] for r in b["rows"]]
    html_t = table_html(b["columns"], rows, widths=b.get("widths"), t=None if ctx.formal else ctx.t, formal=ctx.formal)
    if not ctx.formal:
        html_t = html_t.replace("✓", I.svg("check", size=18, color=ctx.t["press"]))
    return f'<div class="blk" data-split="rows">{_table_caption(b, ctx)}{html_t}</div>'


def b_gantt(b: dict, ctx: Ctx) -> str:
    total = int(b["total"])
    unit = b.get("unit", "天")
    ticks = "".join(f'<span>{d}</span>' if d % 5 == 0 or d == 1 else "<span></span>" for d in range(1, total + 1))
    grid = "".join(f'<i style="left:{d / total * 100:.2f}%"></i>' for d in range(5, total, 5))
    rows = []
    for r in b["rows"]:
        s, e = int(r["start"]), int(r["end"])
        ms = " ms" if r.get("milestone") else ""
        note = ""
        if r.get("note"):
            side = "r" if (total - e) >= 6 or (total - e) >= s else "l"
            span = f"{e + 1}/{total + 1}" if side == "r" else f"1/{s}"
            note = f'<span class="g-note {side}" style="grid-column:{span}">{E(r["note"])}</span>'
        rows.append(f'<div class="g-row"><div>{E(r["label"])}</div><div class="g-track" style="--total:{total}">{grid}<div class="g-bar{ms}" style="grid-column:{s}/{e + 1}"></div>{note}</div></div>')
    head = f'<div class="g-head"><div>阶段（第几个{E(unit)}）</div><div class="g-scale" style="--total:{total}">{ticks}</div></div>'
    return f'<div class="blk" data-split="gantt"><div class="gantt">{head}{"".join(rows)}</div></div>'


def b_image(b: dict, ctx: Ctx) -> str:
    ctx.fig += 1
    cap = f'<div class="cap">图 {ctx.fig}　{E(b["caption"])}</div>' if b.get("caption") else ""
    return f'<div class="blk image" data-scale="1"><figure><img src="{E(b["src"])}" alt="{E(b.get("alt", b.get("caption", "")))}">{cap}</figure></div>'


def b_figure(b: dict, ctx: Ctx) -> str:
    import showcase_figures as F

    ctx.fig += 1
    kind = b["figure"]
    w = PAGE[ctx.orientation]["w"] if not b.get("width") else int(b["width"])
    svg = getattr(F, kind)({**b["data"], "plain": ctx.formal}, ctx.t, w)
    if ctx.atlas:
        svg = svg.replace('font-weight="600"', 'font-weight="400"').replace('font-weight="700"', 'font-weight="400"')
    cap = f'<div class="cap">图 {ctx.fig}　{E(b["caption"])}</div>' if b.get("caption") else ""
    return f'<div class="blk figure" data-scale="1"><figure>{svg}{cap}</figure></div>'


def b_sub(b: dict, ctx: Ctx) -> str:
    return f'<h3 class="sub" data-unit="sub">{E(b["text"])}</h3>'


BLOCKS = {"text": b_text, "p": b_text, "bullets": b_bullets, "stats": b_stats, "cards": b_cards, "steps": b_steps, "callout": b_callout,
          "scope": b_scope, "checks": b_checks, "table": b_table, "matrix": b_matrix, "gantt": b_gantt, "figure": b_figure, "image": b_image, "sub": b_sub}


# --------------------------------------------------------------------------------------------- page
def build(spec: dict[str, Any]) -> str:
    """Display page (also the source of the PDF)."""
    orientation = spec.get("orientation", "portrait")
    t = tokens(spec["theme"])
    atlas = spec.get("style") == "atlas"
    formal = spec.get("style") in ("formal", "atlas")
    ctx = Ctx(t, orientation, formal, atlas)
    icon = spec.get("icon", "file")
    hero = spec.get("hero", {})
    head_mark = "" if formal else iblock(icon, t, "lg")
    numbered = spec.get("numbered", formal)
    labels = [f'{CJK_NUM[k - 1]}、' if numbered and k <= len(CJK_NUM) else "" for k in range(1, len(spec["sections"]) + 1)]
    if formal and spec.get("cover"):
        lines = "".join(f'<div class="ci"><span class="cl">{E(a)}</span><span>{E(v)}</span></div>' for a, v in hero.get("info", []))
        sub = f'<div class="cover-sub">{E(spec["subtitle"])}</div>' if spec.get("subtitle") else ""
        parts = [f'<div class="hero" data-unit="hero"><div class="cover" data-solo="1"><div class="cover-in"><h1>{E(spec["title"])}</h1>{sub}<div class="cover-info">{lines}</div></div></div>']
    else:
        shown = spec.get("show_title", True)                  # false: the title is in the page header, not repeated on the first page (h1 stays for readers and tabs)
        head = f'<div class="hero-head">{head_mark}<h1>{E(spec["title"])}</h1></div>' if shown else f'<h1 class="vh">{E(spec["title"])}</h1>'
        parts = [f'<div class="hero{"" if shown else " nohead"}" data-unit="hero">{head}']
        if hero.get("stats"):
            parts.append(b_stats({"items": hero["stats"]}, ctx))
        if hero.get("scene"):
            import showcase_figures as F

            parts.append(f'<div class="blk hero-scene" data-scale="1">{F.hero_scene(hero["scene"], t, PAGE[orientation]["w"])}</div>')
        if hero.get("info"):
            parts.append(b_info(hero["info"]))
    if spec.get("toc"):
        rows = "".join(f'<a href="#h{k}"><span class="tn">{E(labels[k - 1])}</span><span class="tt">{E(sec["title"])}</span><span class="tl"></span><span class="tp">0</span></a>'
                       for k, sec in enumerate(spec["sections"], 1))
        parts.append(f'<div class="toc" data-unit="toc" data-solo="1"><div class="toc-h">{"" if formal else iblock("list", t, "sm")}<span>目录</span></div>{rows}</div>')
    parts.append("</div>")
    for k, sec in enumerate(spec["sections"], 1):
        head_icon = sec.get("icon") or I.pick(sec["title"])
        lead = f'<p class="lead">{E(sec["lead"])}</p>' if sec.get("lead") else ""
        blocks = []
        for b in sec["blocks"]:
            blocks.append(BLOCKS[b["type"]](b, ctx))
        mark = "" if formal else iblock(head_icon, t, "md")
        brk = " brk" if spec.get("chapter_breaks") else ""
        parts.append(f'<section id="s{k}"><h2 class="sh{brk}" id="h{k}" data-unit="head">{mark}<span>{E(labels[k - 1])}{E(sec["title"])}</span></h2>{lead}{"".join(blocks)}</section>')
    body = "\n".join(parts)
    return (f'<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(spec["title"])}</title><link rel="icon" href="{favicon(t, icon)}"><style>{css(t, orientation, formal, atlas)}</style></head>'
            f'<body><main class="doc">{body}</main></body></html>\n')


CJK_NUM = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
           "二十一", "二十二", "二十三", "二十四", "二十五", "二十六", "二十七", "二十八", "二十九", "三十"]


def b_info(pairs: list[list[str]]) -> str:
    """Document facts under the title: label and value pairs, two pairs per row (项目名称 / 客户 / 版本 / 日期 …)."""
    rows = []
    padded = list(pairs) + ([["", ""]] if len(pairs) % 2 else [])
    for i in range(0, len(padded), 2):
        cells = "".join(f"<th>{E(label)}</th><td>{E(value)}</td>" for label, value in padded[i:i + 2])
        rows.append(f"<tr>{cells}</tr>")
    return f'<div class="blk" data-flex="1"><div class="twrap"><table class="info">{"".join(rows)}</table></div></div>'


# --------------------------------------------------------------------------------------------- validation
_REQUIRED = {"text": ("text",), "p": ("text",), "bullets": ("items",), "stats": ("items",), "cards": ("items",), "steps": ("items",), "callout": ("text",),
             "scope": ("in", "out"), "checks": ("items",), "table": ("columns", "rows"), "matrix": ("columns", "rows"), "gantt": ("total", "rows"),
             "figure": ("figure", "data"), "image": ("src",), "sub": ("text",)}
_PLACEHOLDER = re.compile(r"待补充|TODO|TBD|占位符|占位文字|xxx|lorem ipsum", re.I)


def validate_spec(spec: dict[str, Any]) -> list[str]:
    """Errors a person can fix in the spec before anything is rendered."""
    errors: list[str] = []
    if not spec.get("title"):
        errors.append("缺少 title")
    try:
        tokens(spec.get("theme", ""))
    except Exception:
        errors.append(f"theme 无效: {spec.get('theme')!r}（见 themes.json）")
    if spec.get("icon") and spec["icon"] not in I.ICONS:
        errors.append(f"未知图标 {spec['icon']!r}")
    if spec.get("style") not in (None, "rich", "formal", "atlas"):
        errors.append(f"style 只能是 formal（正式版）、atlas（架构图册）或 rich（展示版）: {spec.get('style')!r}")
    if (spec.get("cover") or spec.get("toc")) and spec.get("style") not in ("formal", "atlas"):
        errors.append("封面和目录（cover、toc）只用于正式版（style: formal）")
    if spec.get("show_title") is False and spec.get("style") not in ("formal", "atlas"):
        errors.append("show_title: false 只用于有页眉标题的正式版或架构图册（style: formal / atlas）")
    hero_spec = spec.get("hero") or {}
    if spec.get("style") in ("formal", "atlas") and (hero_spec.get("stats") or hero_spec.get("scene")):
        errors.append("正式版（style: formal）不放封面统计块和插画；项目信息写在 hero.info")
    for pair in (spec.get("hero") or {}).get("info", []):
        if not (isinstance(pair, list) and len(pair) == 2):
            errors.append(f"hero.info 每项是 [名称, 内容]: {pair!r}")
    sections = spec.get("sections")
    if not sections:
        errors.append("sections 为空")
        return errors

    def icon_ok(name: Any, where: str) -> None:
        if name and name not in I.ICONS:
            errors.append(f"{where}: 未知图标 {name!r}")

    for si, sec in enumerate(sections, 1):
        where = f"第 {si} 节「{sec.get('title', '')}」"
        if not sec.get("title") or not sec.get("blocks"):
            errors.append(f"{where}: 需要 title 和 blocks")
            continue
        icon_ok(sec.get("icon"), where)
        for bi, b in enumerate(sec["blocks"], 1):
            kind = b.get("type")
            if kind not in BLOCKS:
                errors.append(f"{where} 块 {bi}: 未知类型 {kind!r}")
                continue
            for key in _REQUIRED[kind]:
                if b.get(key) in (None, "", [], {}):
                    errors.append(f"{where} 块 {bi}（{kind}）: 缺少 {key}")
            for item in b.get("items", []) if isinstance(b.get("items"), list) else []:
                if isinstance(item, dict):
                    icon_ok(item.get("icon"), where)
            if kind in {"table", "matrix"}:
                if spec.get("style") in ("formal", "atlas") and not b.get("caption"):
                    errors.append(f"{where} 块 {bi}（{kind}）: 表格必须有标题（caption），分页时自动写“表 N　标题（续）”")
                n = len(b.get("columns", []))
                if any((len(r) != n) for r in b.get("rows", []) if not isinstance(r, dict)):
                    errors.append(f"{where} 块 {bi}（{kind}）: 行列数不一致")
            if kind == "figure":
                errors.extend(f"{where} 块 {bi}: {e}" for e in _figure_errors(b))
    if _PLACEHOLDER.search(json.dumps(spec, ensure_ascii=False)):
        errors.append("含占位文字（待补充/TODO 等）")
    return errors


def _figure_errors(b: dict[str, Any]) -> list[str]:
    kind, data = b["figure"], b["data"]
    errs = []
    if kind not in {"arch_layers", "swimlane", "deployment"}:
        return [f"未知图 {kind!r}"]
    if kind == "arch_layers":
        ids = {n["id"] for layer in data.get("layers", []) for g in (layer.get("groups") or [{"nodes": layer.get("nodes", [])}]) for n in g["nodes"]}
        ids |= {n["id"] for n in (data.get("external") or {}).get("nodes", [])}
        for f in data.get("flows", []):
            if f.get("from") not in ids or f.get("to") not in ids:
                errs.append(f"连线引用不存在的节点: {f}")
    if kind == "swimlane":
        lanes = {l["name"] for l in data.get("lanes", [])}
        ids = {s["id"] for s in data.get("steps", [])}
        errs += [f"步骤 {s['id']} 的泳道 {s['lane']!r} 不存在" for s in data.get("steps", []) if s["lane"] not in lanes]
        errs += [f"连线引用不存在的步骤: {lk}" for lk in data.get("links", []) if lk["from"] not in ids or lk["to"] not in ids]
        errs += [f"泳道连线不写标签（列间距只有 26 px，标签会被方框遮住），把说明写进步骤文字: {lk}" for lk in data.get("links", []) if lk.get("label")]
    return errs


# --------------------------------------------------------------------------------------------- plain pages (project review pages)
LEGACY_CSS = """
.meta{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 20px;font-size:14px;line-height:1.5;color:var(--ink2)}
.chip-s{display:inline-block;font-size:14px;line-height:22px;padding:0 10px;border-radius:999px;background:var(--tint1);color:var(--press);font-weight:600}
main.doc h3{margin:20px 0 8px;font-size:20px;line-height:1.4;font-weight:600}
main.doc table:not(.tbl){width:100%;border-collapse:collapse;margin:0 0 16px}
main.doc table:not(.tbl) th{background:var(--tint1);color:var(--press);font-weight:600;font-size:14px;line-height:1.5;padding:10px 14px;text-align:center;vertical-align:middle}
main.doc table:not(.tbl) td{font-size:14px;line-height:1.6;padding:9px 14px;border-top:1px solid var(--line);vertical-align:middle;text-align:left;overflow-wrap:anywhere}
.table-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin:0 0 16px}.table-scroll table{margin:0!important}
.notice{background:var(--tint1);border-left:4px solid var(--primary);border-radius:12px;padding:12px 16px;margin:0 0 16px;font-size:16px}
a{color:var(--press)}
.tabs{margin-top:8px}[role=tablist]{display:flex;gap:8px;border-bottom:1px solid var(--line);margin-bottom:12px}
[role=tab]{appearance:none;border:0;background:transparent;padding:10px 14px;cursor:pointer;color:var(--ink2);font:inherit;font-size:16px;font-weight:600}
[role=tab][aria-selected=true]{color:var(--press);border-bottom:3px solid var(--primary)}
[role=tabpanel]{padding:8px 0}
svg{max-width:100%;height:auto}
"""


FORMAL_PAGE_CSS = """
main.doc table:not(.tbl) th{background:var(--tint1);color:var(--ink);text-align:left}
main.doc table:not(.tbl) td{color:var(--ink);border-top:1px solid var(--line)}
.table-scroll{border-radius:8px}
.notice{background:var(--tint1);border-left:0;border-radius:8px;color:var(--ink)}
.chip-s{background:var(--tint1);color:var(--ink)}
main.doc h3{color:var(--ink)}
a{color:var(--ink)}
"""


def page(title: str, theme: str, body: str, *, icon: str = "file", html_attrs: str = "", wide: bool = True, formal: bool = False) -> str:
    """A plain review page: theme tokens, one font, tab icon. ``body`` is ordinary HTML (h2/h3/p/ul/table).

    The default look puts an icon block before the title and every section title. ``formal=True`` is the look of the client documents:
    no icon blocks, one ink and one regular weight for titles, heads and text, a pale table head with hairlines, heads that sit over
    their own (left-aligned) column."""
    t = tokens(theme)
    ctx = Ctx(t, "landscape" if wide else "portrait")

    def add_icon(m: re.Match[str]) -> str:
        inner_text = re.sub(r"<[^>]+>", "", m.group(1))
        return f'<h2 class="sh">{iblock(I.pick(inner_text), t, "md")}<span>{m.group(1)}</span></h2>'

    if formal:
        body = re.sub(r"<h2>(.*?)</h2>", lambda m: f'<h2 class="sh">{m.group(1)}</h2>', body, flags=re.S)
    else:
        body = re.sub(r"<h2>(.*?)</h2>", add_icon, body, flags=re.S)
    style = css(t, "landscape" if wide else "portrait", formal, formal) + LEGACY_CSS
    if formal:
        style += FORMAL_PAGE_CSS.replace("font-weight:600", "font-weight:400").replace("font-weight:700", "font-weight:400")
        style = style.replace("font-weight:600", "font-weight:400").replace("font-weight:700", "font-weight:400")
    hero = f"<h1>{E(title)}</h1>" if formal else f'<div class="hero-head">{iblock(icon, t, "lg")}<h1>{E(title)}</h1></div>'
    return (f'<!doctype html>\n<html lang="zh-CN"{(" " + html_attrs) if html_attrs else ""}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><link rel="icon" href="{favicon(t, icon)}"><style>{style}</style></head>'
            f'<body><main class="doc"><div class="hero">{hero}</div>{body}</main></body></html>\n')
