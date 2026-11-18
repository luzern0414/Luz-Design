"""把 templates/documents/reading/specs/*.json 渲染成 samples/*.html（技能自带的版式参考，不是客户成品）。

  py -X utf8 templates/documents/reading/tools/build_reading_samples.py [--only DC-RD-001] [--specs <目录>] [--out <目录>] [--no-check]

两种渲染入口：
  * spec 带 "renderer": "make_summary"（阶段汇总页）：直接调用 make_summary.render，spec 同时是 make_summary.py 的合法输入。
  * 其余阅读页：本脚本的 render_page，输入格式见下，样式取 references/md-type.css 的母本（原样夹在 luz-md-type 标记之间）。
样例不走会话与前置检索门禁、也不登记；正式交付必须走正式命令与门禁。

页面 spec：
  {"id": "DC-RD-001", "title": "主标题", "theme": "salon", "icon": "ledger", "toc": false,
   "sections": [{"title": "节名", "blocks": [块…]}], "sources": [{"publisher": "", "title": "", "url": "", "locator": "", "checked": "2026-11-09"}]}
  theme 取 references/themes.json 的行业主题键，icon 取 new_session.py 的标签页图案名。
块（type）：
  paragraph {text}  list {items, ordered}  h3 {text}  table {caption, columns, align, rows}  conclusion {text}  quote {text, lang, cite}
  chart {kind: bar|donut|stack, caption, unit, items|series+rows}  flow {items:[{name, note}]}  layers {layers:[{name, nodes:[{name, note}]}]}
  code {text}  figures {items:[{src, alt, caption}], wide}
行内：**粗体**、`代码`、[^n] 引用锚点（指向 sources 的第 n 条）。
"""
from __future__ import annotations

import argparse
import base64
import contextlib
import html
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # templates/documents/reading/tools
ROOT = HERE.parents[3]                                 # the skill root (Luz-Design)
FALLBACK = Path("D:/Codes/Luz-Design")
SKILL = ROOT if (ROOT / "scripts" / "make_summary.py").is_file() else FALLBACK
sys.path.insert(0, str(SKILL / "scripts"))

import check_document  # noqa: E402
import make_summary  # noqa: E402
import new_session  # noqa: E402

ASSETS = ROOT / "kit" / "assets"
if not ASSETS.is_dir():
    ASSETS = FALLBACK / "kit" / "assets"
THEMES = json.loads((SKILL / "references" / "themes.json").read_text(encoding="utf-8"))["themes"]
MD_TYPE = make_summary.MD_TYPE          # the master block of references/md-type.css, exactly as sync_md_type.py keeps it


# ------------------------------------------------------------------ colour helpers
def rgb(hexv: str) -> tuple[int, int, int]:
    h = hexv.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hx(c) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def mix(a: str, b: str, t: float) -> str:
    """t of a, the rest of b."""
    ca, cb = rgb(a), rgb(b)
    return hx([ca[i] * t + cb[i] * (1 - t) for i in range(3)])


def luminance(hexv: str) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(hexv)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def darken_until(color: str, background: str, ratio: float) -> str:
    while contrast(color, background) < ratio:
        color = mix(color, "#000000", 0.93)
    return color


def tokens(theme: str) -> dict:
    t = THEMES[theme]
    action, press, tint = t["action"], t["actionPress"], t["actionTint"]
    canvas = mix(tint, "#FFFFFF", 0.38)
    if luminance(canvas) < 0.85:
        canvas = "#FFFFFF"
    ink = "#25201F"
    muted = darken_until("#6B6064", canvas, 7.0)
    line = mix(action, canvas, 0.2)
    steps, prev = [], None
    for share_of_action in (1.0, 0.8, 0.62, 0.48, 0.36, 0.26, 0.18, 0.12):       # one hue in steps; every step carries a text colour that reads on it (4.5:1)
        c = mix(action, "#FFFFFF", share_of_action)
        text = "#FFFFFF" if contrast("#FFFFFF", c) >= 4.5 else ("#25201F" if contrast("#25201F", c) >= 4.5 else None)
        if text and (prev is None or abs(luminance(c) - prev) >= 0.07):
            steps.append((c, text))
            prev = luminance(c)
        if len(steps) == 5:
            break
    return {"action": action, "press": press, "tint": tint, "canvas": canvas, "paper": "#FFFFFF", "ink": ink, "muted": muted, "line": line,
            "link": darken_until(press, canvas, 7.0), "steps": steps}


# ------------------------------------------------------------------ inline markup
def esc(text) -> str:
    return html.escape(str(text), quote=False)


def inline(text, nrefs: int) -> str:
    out = esc(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`(.+?)`", r"<code>\1</code>", out)

    def cite(m):
        n = int(m.group(1))
        if not 1 <= n <= nrefs:
            raise ValueError(f"引用锚点 [^{n}] 指向不存在的来源")
        return f'<a class="cite" href="#ref-{n}" aria-label="参考来源 {n}">[{n}]</a>'
    return re.sub(r"\[\^(\d+)\]", cite, out)


# ------------------------------------------------------------------ blocks
def photo(src: str, width: int) -> str:
    from PIL import Image
    im = Image.open(ASSETS / src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=80)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def text_on(fill: str) -> str:
    return "#FFFFFF" if contrast("#FFFFFF", fill) >= 4.5 and contrast("#FFFFFF", fill) > contrast("#25201F", fill) else "#25201F"


def r_table(b: dict, n: int) -> str:
    cols = b["columns"]
    align = list(b.get("align") or []) + ["left"] * len(cols)
    head = "".join(f'<th scope="col">{esc(c)}</th>' for c in cols)
    body = ""
    for row in b["rows"]:
        if len(row) != len(cols):
            raise ValueError(f"表“{b.get('caption')}”有一行列数与表头不一致: {row}")
        body += "<tr>" + "".join(f'<td class="{align[i]}">{inline(v, n)}</td>' for i, v in enumerate(row)) + "</tr>"
    cap = f"<caption>{esc(b['caption'])}</caption>" if b.get("caption") else ""
    return f'<div class="table-wrap"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def r_chart(b: dict, tk: dict) -> str:
    kind, unit = b["kind"], b.get("unit", "")
    steps = tk["steps"]
    cap = f"<figcaption>{esc(b['caption'])}</figcaption>" if b.get("caption") else ""
    label = esc(b.get("label") or b.get("caption") or "图表")
    if kind == "bar":
        items = b["items"]
        top = b.get("max") or max(i["value"] for i in items)
        lis = "".join(
            f'<li><span class="bar-name">{esc(i["name"])}</span><span class="bar-track"><span class="bar-fill" style="width:{i["value"] / top * 100:.1f}%"></span></span>'
            f'<span class="bar-value">{i["value"]} {esc(unit)}</span></li>' for i in items)
        return f'<figure class="chart" role="group" aria-label="{label}"><ul class="bars">{lis}</ul>{cap}</figure>'
    if kind == "donut":
        items = [i for i in b["items"]]
        total = sum(i["value"] for i in items)
        legend = "".join(
            f'<li><span class="swatch s{k % len(steps) + 1}"></span><span class="lg-name">{esc(i["name"])}</span>'
            f'<span class="lg-value">{i["value"]} {esc(unit)}</span><span class="lg-share">{i["value"] / total * 100:.1f}%</span></li>' for k, i in enumerate(items))
        values = ",".join(str(i["value"]) for i in items)
        return (f'<figure class="chart" role="group" aria-label="{label}"><div class="donut-row"><div class="donut-wrap">'
                f'<canvas class="donut" width="440" height="440" data-values="{values}" role="img" aria-label="{label}，合计 {total} {esc(unit)}，各项数值见右侧列表"></canvas>'
                f'<div class="donut-center"><strong>{total}</strong><span>{esc(unit)}</span></div></div>'
                f'<ul class="legend">{legend}</ul></div>{cap}</figure>')
    if kind == "stack":
        series = b["series"]
        rows = ""
        for r in b["rows"]:
            segs = ""
            for k, v in enumerate(r["values"]):
                if v:
                    segs += (f'<span class="fill s{k % len(steps) + 1}" style="flex:{v} 1 0" role="img" '
                             f'aria-label="{esc(r["name"])}{esc(series[k])}{v} {esc(unit)}">{esc(series[k])} {v}</span>')
            rows += f'<li><span class="bar-name">{esc(r["name"])}</span><span class="stack">{segs}</span><span class="bar-value">{sum(r["values"])} {esc(unit)}</span></li>'
        return f'<figure class="chart" role="group" aria-label="{label}"><ul class="bars stacks">{rows}</ul>{cap}</figure>'
    raise ValueError(f"unknown chart kind {kind!r}")


def r_block(b: dict, tk: dict, n: int) -> str:
    t = b["type"]
    if t == "paragraph":
        return f"<p>{inline(b['text'], n)}</p>"
    if t == "h3":
        return f"<h3>{esc(b['text'])}</h3>"
    if t == "list":
        tag = "ol" if b.get("ordered") else "ul"
        return f"<{tag}>" + "".join(f"<li>{inline(i, n)}</li>" for i in b["items"]) + f"</{tag}>"
    if t == "table":
        return r_table(b, n)
    if t == "conclusion":
        return f'<div class="conclusion"><p>{inline(b["text"], n)}</p></div>'
    if t == "quote":
        lang = f' lang="{b["lang"]}"' if b.get("lang") else ""
        cite = f'<p class="src">{inline(b["cite"], n)}</p>' if b.get("cite") else ""
        return f"<blockquote{lang}><p>{esc(b['text'])}</p>{cite}</blockquote>"
    if t == "chart":
        return r_chart(b, tk)
    if t == "flow":
        lis = "".join(f'<li><strong>{esc(i["name"])}</strong>' + (f'<span>{esc(i["note"])}</span>' if i.get("note") else "") + "</li>" for i in b["items"])
        return f'<ol class="flow">{lis}</ol>'
    if t == "layers":
        out = ""
        for layer in b["layers"]:
            nodes = "".join(f'<li><strong>{esc(x["name"])}</strong>' + (f'<span>{esc(x["note"])}</span>' if x.get("note") else "") + "</li>" for x in layer["nodes"])
            out += f'<div class="layer"><p class="layer-name">{esc(layer["name"])}</p><ul>{nodes}</ul></div>'
        return f'<div class="layers" role="group" aria-label="{esc(b.get("label", "分层结构"))}">{out}</div>'
    if t == "code":
        return f"<pre><code>{esc(b['text'])}</code></pre>"
    if t == "figures":
        figs = ""
        for it in b["items"]:
            figs += (f'<figure><img src="{photo(it["src"], 1200 if b.get("wide") else 640)}" alt="{esc(it["alt"])}" width="{1200 if b.get("wide") else 640}">'
                     + (f"<figcaption>{esc(it['caption'])}</figcaption>" if it.get("caption") else "") + "</figure>")
        return f'<div class="figures{" figures-wide" if b.get("wide") else ""}">{figs}</div>'
    raise ValueError(f"unknown block type {t!r}")


DONUT_JS = """<script>
(function () {
  document.querySelectorAll("canvas.donut").forEach(function (c) {
    var v = c.getAttribute("data-values").split(",").map(Number), total = v.reduce(function (a, b) { return a + b; }, 0);
    var ctx = c.getContext("2d"), cs = getComputedStyle(c), r = c.width / 2, inner = r * 0.66, at = -Math.PI / 2, gap = 0.03;
    v.forEach(function (x, i) {
      var span = x / total * Math.PI * 2;
      ctx.beginPath();
      ctx.arc(r, r, r - 2, at + gap / 2, at + span - gap / 2);
      ctx.arc(r, r, inner, at + span - gap / 2, at + gap / 2, true);
      ctx.closePath();
      ctx.fillStyle = cs.getPropertyValue("--s" + (i + 1)).trim();
      ctx.fill();
      at += span;
    });
  });
})();
</script>
"""

CSS = """
:root { color-scheme: light; --canvas: __CANVAS__; --paper: __PAPER__; --ink: __INK__; --muted: __MUTED__; --line: __LINE__; --tint: __TINT__; --action: __ACTION__; --press: __PRESS__; --link: __LINK__; --radius: 8px; }
* { box-sizing: border-box; }
html { background: var(--canvas); }
body { margin: 0; background: var(--canvas); color: var(--ink); font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif; }
main { width: min(880px, calc(100% - 32px)); margin: 0 auto; padding: 72px 0 112px; }
h1 + section > h2:first-child { margin-top: 40px; }
h2[id] { scroll-margin-top: 24px; }
h2:focus-visible, a:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; border-radius: 4px; }
a { color: var(--link); text-underline-offset: 3px; }
a.cite { margin-left: 2px; font-size: var(--md-aux); font-weight: 600; text-decoration: none; }
section > p, section > ul, section > ol { max-width: var(--md-measure); }
.table-wrap { margin: 24px 0 36px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 11px 16px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: middle; }
thead th { background: var(--tint); text-align: center; }
thead th:first-child { border-radius: var(--radius) 0 0 var(--radius); }
thead th:last-child { border-radius: 0 var(--radius) var(--radius) 0; }
td:first-child { font-weight: 600; white-space: nowrap; }
th, td.center, td.right { white-space: nowrap; }
td.center { text-align: center; } td.right { text-align: right; }
caption { text-align: left; }
.conclusion { max-width: var(--md-measure); margin: 0 0 28px; padding: 16px 22px; border-left: 4px solid var(--action); border-radius: 0 var(--radius) var(--radius) 0; background: var(--tint); }
.conclusion p { margin: 0; }
blockquote { border-left-color: var(--action); }
blockquote .src { margin: 8px 0 0; color: var(--muted); }
.chart { margin: 8px 0 36px; }
.chart figcaption { margin-top: 14px; text-align: left; }
.bars { max-width: none; margin: 0; padding: 0; list-style: none; }
.bars li { display: grid; grid-template-columns: 8.5em 1fr 4.5em; gap: 16px; align-items: center; margin: 0; padding: 7px 0; }
.bars li + li { margin-top: 0; }
.bar-name { font-size: var(--md-table); }
.bar-track { display: block; height: 20px; border-radius: var(--radius); background: var(--tint); overflow: hidden; }
.bar-fill { display: block; height: 20px; border-radius: var(--radius); background: var(--action); }
.bar-value { font-size: var(--md-table); font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.stacks li { padding: 6px 0; }
.stack { display: flex; gap: 2px; min-width: 0; }
.fill { display: block; height: 20px; min-width: 0; overflow: hidden; border-radius: 4px; font-size: var(--md-aux); font-weight: 600; line-height: 20px; text-align: center; white-space: nowrap; }
.legend { max-width: none; margin: 0; padding: 0; list-style: none; }
.legend li { display: grid; grid-template-columns: 14px 1fr auto 4.5em; gap: 12px; align-items: center; margin: 0; padding: 7px 0; border-bottom: 1px solid var(--line); font-size: var(--md-table); }
.legend li:last-child { border-bottom: 0; }
.legend-inline { display: flex; flex-wrap: wrap; gap: 8px 24px; margin-bottom: 12px; }
.legend-inline li { display: flex; gap: 8px; padding: 0; border: 0; }
.lg-value, .lg-share { text-align: right; font-variant-numeric: tabular-nums; }
.lg-value { font-weight: 600; }
.swatch { width: 14px; height: 14px; border-radius: 4px; }
__SERIES__
.donut-row { display: grid; grid-template-columns: 220px 1fr; gap: 48px; align-items: center; }
.donut-wrap { position: relative; width: 220px; height: 220px; }
.donut { display: block; width: 220px; height: 220px; }
.donut-center { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; line-height: 1.2; }
.donut-center strong { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
.donut-center span { font-size: var(--md-aux); color: var(--muted); }
.flow { display: flex; max-width: none; margin: 8px 0 36px; padding: 0; list-style: none; gap: 28px; }
.flow li { position: relative; flex: 1 1 0; margin: 0; padding: 14px 14px 14px; border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper); font-size: var(--md-table); line-height: 1.5; }
.flow li + li { margin: 0; }
.flow strong, .layer strong { display: block; font-weight: 600; }
.flow span, .layer li span { display: block; margin-top: 2px; color: var(--muted); font-size: var(--md-aux); }
.flow li:not(:last-child)::after { content: ""; position: absolute; top: 50%; right: -19px; width: 9px; height: 9px; border-top: 2px solid var(--action); border-right: 2px solid var(--action); transform: translateY(-50%) rotate(45deg); }
.layers { margin: 8px 0 36px; }
.layer { position: relative; display: grid; grid-template-columns: 7.5em 1fr; gap: 20px; align-items: center; padding: 16px 20px; border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper); }
.layer + .layer { margin-top: 30px; }
.layer + .layer::before { content: ""; position: absolute; top: -20px; left: 50%; width: 9px; height: 9px; border-right: 2px solid var(--action); border-bottom: 2px solid var(--action); transform: translateX(-50%) rotate(45deg); }
.layer .layer-name { margin: 0; font-size: var(--md-h4); font-weight: 600; }
.layer ul { display: flex; flex-wrap: wrap; gap: 10px; max-width: none; margin: 0; padding: 0; list-style: none; }
.layer li { margin: 0; padding: 8px 14px; border-radius: var(--radius); background: var(--tint); font-size: var(--md-table); line-height: 1.5; }
.layer li + li { margin-top: 0; }
.figures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin: 8px 0 32px; }
.figures-wide { grid-template-columns: 1fr; }
.figures figure { margin: 0; }
.figures img { display: block; width: 100%; height: auto; border-radius: var(--radius); }
.figures figcaption { padding: 10px 0 0; }
.toc { margin: 36px 0 0; padding: 18px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.toc ul { columns: 2; column-gap: 40px; max-width: none; margin: 0; padding: 0; list-style: none; font-size: var(--md-table); }
.toc li { break-inside: avoid; margin: 0; padding: 4px 0; }
.toc li + li { margin-top: 0; }
.sources { max-width: none; margin: 0; padding: 0; list-style: none; font-size: var(--md-table); }
.sources li { display: grid; grid-template-columns: 2.6em 1fr; margin: 0 0 14px; }
.sources li + li { margin-top: 0; }
.sources .no { color: var(--muted); font-weight: 600; }
pre { max-width: 100%; background: var(--paper); }
@media (max-width: 767px) {
  main { padding: 40px 0 72px; }
  h1 + section > h2:first-child { margin-top: 32px; }
  .bars li { grid-template-columns: 6.5em 1fr 4em; gap: 10px; }
  .donut-row { grid-template-columns: 1fr; justify-items: center; gap: 28px; }
  .donut-row .legend { width: 100%; }
  .flow { flex-direction: column; gap: 26px; }
  .flow li:not(:last-child)::after { top: auto; bottom: -19px; right: auto; left: 50%; transform: translateX(-50%) rotate(135deg); }
  .layer { grid-template-columns: 1fr; gap: 10px; }
  .figures { grid-template-columns: 1fr; }
  .toc ul { columns: 1; }
  th, td { padding: 10px 8px; }
  .stacks li { grid-template-columns: 1fr auto; gap: 6px 10px; }
  .stacks .bar-name { grid-column: 1; grid-row: 1; }
  .stacks .bar-value { grid-column: 2; grid-row: 1; }
  .stacks .stack { grid-column: 1 / -1; grid-row: 2; }
}
@media print {
  html, body { background: #FFFFFF; }
  main { width: auto; padding: 0; }
  .toc { display: none; }
  table, figure, pre, .flow, .layers, blockquote, .conclusion { break-inside: avoid; }
  h2 { break-after: avoid; }
}
"""


def render_page(spec: dict) -> str:
    title = spec["title"].strip()
    tk = tokens(spec["theme"])
    sources = spec.get("sources") or []
    n = len(sources)
    sections = spec["sections"]
    toc = bool(spec.get("toc")) or len(sections) + (1 if sources else 0) > 8
    all_sections = list(sections) + ([{"title": spec.get("sources_title", "参考来源"), "sources": True}] if sources else [])
    parts = [f"<h1>{esc(title)}</h1>"]
    nav = ""
    if toc:
        nav = '<nav class="toc" aria-label="章节"><ul>' + "".join(f'<li><a href="#section-{i}">{esc(s["title"])}</a></li>' for i, s in enumerate(all_sections, 1)) + "</ul></nav>"
    for i, sec in enumerate(all_sections, 1):
        anchor = f' id="section-{i}" tabindex="-1"' if toc else ""
        body = [f"<h2{anchor}>{esc(sec['title'])}</h2>"]
        if sec.get("sources"):
            items = ""
            for k, s in enumerate(sources, 1):
                link = f'<a href="{html.escape(s["url"], quote=True)}" rel="noreferrer">{esc(s["title"])}</a>'
                detail = "。".join(x for x in (esc(s["publisher"]), link, esc(s["locator"]) if s.get("locator") else "", f"核对于 {esc(s['checked'])}" if s.get("checked") else "") if x)
                items += f'<li id="ref-{k}"><span class="no">[{k}]</span><span>{detail}</span></li>'
            body.append(f'<ol class="sources">{items}</ol>')
        else:
            body.extend(r_block(b, tk, n) for b in sec["blocks"])
        parts.append("<section>" + "".join(body) + "</section>")
        if i == 1 and nav:
            parts.append(nav)
    icon = new_session.tab_icon_href(spec.get("icon_subject", title), icon=spec.get("icon"), theme=spec["theme"])
    css = CSS.replace("__SERIES__", "".join(
        f".fill.s{k}, .swatch.s{k} {{ background: var(--s{k}); color: var(--t{k}); }}\n" for k in range(1, len(tk["steps"]) + 1)))
    css = css.replace(":root { color-scheme: light;", ":root { color-scheme: light; " + " ".join(f"--s{k}: {c}; --t{k}: {t};" for k, (c, t) in enumerate(tk["steps"], 1)), 1)
    for key, value in (("CANVAS", tk["canvas"]), ("PAPER", tk["paper"]), ("INK", tk["ink"]), ("MUTED", tk["muted"]), ("LINE", tk["line"]), ("TINT", tk["tint"]),
                       ("ACTION", tk["action"]), ("PRESS", tk["press"]), ("LINK", tk["link"])):
        css = css.replace(f"__{key}__", value)
    return ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n<link rel="icon" href="{icon}">\n<style>\n{MD_TYPE}\n{css}</style>\n</head>\n<body>\n<main>\n'
            + "\n".join(parts) + "\n</main>\n" + (DONUT_JS if 'canvas class="donut"' in "".join(parts) else "") + "</body>\n</html>\n")


def build_one(spec_path: Path, out_dir: Path, check: bool = True) -> tuple[Path, int, str]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = out_dir / (spec_path.stem + ".html")
    out.write_text(make_summary.render(spec) if spec.get("renderer") == "make_summary" else render_page(spec), encoding="utf-8")
    if not check:
        return out, 0, ""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = check_document.main([str(out)])
    return out, code, buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--specs", default=str(HERE.parent / "specs"))
    ap.add_argument("--out", default=str(HERE.parent / "samples"))
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    failed = 0
    for path in sorted(Path(args.specs).glob("DC-RD-*.json")):
        if args.only and not path.stem.startswith(args.only):
            continue
        out, code, report = build_one(path, out_dir, not args.no_check)
        print(f"wrote {out.name}")
        for line in report.strip().splitlines():
            if line.startswith(("FAIL", "PASS")) or line.strip().startswith(("ERROR", "WARN")):
                print(" ", line.replace(str(out_dir), "").strip())
        failed += code
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
