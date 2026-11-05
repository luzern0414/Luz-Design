"""Vector figures for showcase documents: cover scene, layered architecture, swimlane flow, deployment map.

All text is at least 14 px at the size the figure is printed (the figure width is the page's content width, so there is no
scaling). Lines are 1.5–2 px.

Colour: every layer, lane or zone has its own hue (``palette``: the theme's action colour, then its accent, then the shared sage and
info colours, hues at least 40° apart), a light face with a deeper stroke of the same hue; links and number badges are one neutral ink,
so a link is never mistaken for a node border. Links are drawn last, over every face and title, and never cross a node: they leave a
node vertically, turn inside the gap between two layers (one lane per link, same-layer links too) and arrive from above or below,
away from the group title; in a swimlane they turn in the gap after the source column and take the channel above the lane when a
box is in the way.
"""
from __future__ import annotations

import colorsys
import html
import math
from typing import Any

import showcase_icons as I
from showcase import E, _rgb, mix, width, wrap

FS = 14
F_NAME = 16


def _text(x: float, y: float, s: str, *, size: int = FS, weight: int = 400, fill: str = "#222", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{E(s)}</text>'


def _chars(px: float, size: int = FS) -> int:
    return max(2, int(px // size))  # CJK characters per line


def _lines(s: str, px: float, size: int = FS) -> list[str]:
    return wrap(s, _chars(px, size) * 2)


def _svg(w: float, h: float, body: str, label: str, t: dict[str, str]) -> str:
    return (f'<svg role="img" aria-label="{E(label)}" viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="Microsoft YaHei, sans-serif">'
            f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{_link(t)}"/></marker></defs>{body}</svg>')


# --- colour: one hue per layer, lane or zone; links and badges in one neutral ink
def _link(t: dict[str, str]) -> str:
    return t["ink"]


def _lum(c: str) -> float:
    r, g, b = (v / 255 for v in _rgb(c))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _ratio(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _deepen(c: str, floor: float, bg: str = "#FFFFFF") -> str:
    """The colour pulled towards black until it holds ``floor``:1 against ``bg``: strokes (3:1) and small text (4.5:1)."""
    for k in range(21):
        out = mix(c, "#000000", 0.05 * k)
        if _ratio(out, bg) >= floor:
            return out
    return "#000000"


def _apart(a: str, b: str, gap: float = 40) -> bool:
    (ha, sa, _), (hb, sb, _) = (colorsys.rgb_to_hsv(*(v / 255 for v in _rgb(c))) for c in (a, b))
    if min(sa, sb) < 0.15:                      # a grey is told apart by its lightness, not its hue
        return True
    d = abs(ha - hb) * 360
    return min(d, 360 - d) >= gap


def _hue(base: str, fill: str | None = None) -> dict[str, str]:
    """One hue of a figure: ``fill`` the light face, ``stroke`` the node border (3:1 on white), ``ink`` text on the face (4.5:1),
    ``line`` the hairline of the face and its dashed group borders."""
    face = fill if fill and _lum(fill) > 0.8 else mix(base, "#FFFFFF", 0.88)
    return {"base": base, "fill": face, "stroke": _deepen(base, 3.2), "ink": _deepen(base, 4.8, face), "line": mix(base, "#FFFFFF", 0.55)}


SLATE = ("#5B6B7B", "#EEF1F4")
EXTRA_HUES = (("#6A4FA0", "#EFEAF8"), ("#9A5A2A", "#F7EBDD"), SLATE)


def palette(t: dict[str, str]) -> list[dict[str, str]]:
    """Up to four hues for the layers of a figure, the theme's own action colour first, none within 40° of another."""
    named = [(t[k], t[f]) for k, f in (("primary", "tint1"), ("accent", "accentTint"), ("sage", "sageTint"), ("info", "infoTint")) if t.get(k) and t.get(f)]
    picks: list[dict[str, str]] = []
    for base, fill in named + list(EXTRA_HUES):
        if len(picks) < 4 and all(_apart(base, p["base"]) for p in picks):
            picks.append(_hue(base, fill))
    return picks


def _badge(x: float, y: float, n: Any, t: dict[str, str]) -> str:
    ink = _link(t)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#fff" stroke="{ink}" stroke-width="1.5"/>'
            f'<text x="{x:.1f}" y="{y + 5:.1f}" font-size="14" font-weight="700" fill="{ink}" text-anchor="middle">{E(str(n))}</text>')


def _tag(x_right: float, y_top: float, label: str, h: dict[str, str]) -> str:
    w = width(label) * 7 + 14
    return (f'<rect x="{x_right - w - 8:.1f}" y="{y_top - 10:.1f}" width="{w:.1f}" height="20" rx="10" fill="#fff" stroke="{h["line"]}"/>'
            f'<text x="{x_right - 8 - w / 2:.1f}" y="{y_top + 5:.1f}" font-size="14" font-weight="600" fill="{h["ink"]}" text-anchor="middle">{E(label)}</text>')


# ----------------------------------------------------------------------------------------------- cover scene
def hero_scene(icons: list[str], t: dict[str, str], w: int) -> str:
    h = 150 if w < 800 else 168
    n = len(icons)
    body = [f'<rect width="{w}" height="{h}" rx="16" fill="{t["tint1"]}"/>']
    body.append(f'<circle cx="{w * 0.86:.0f}" cy="{h * 0.2:.0f}" r="{h * 0.62:.0f}" fill="{t["tint2"]}" opacity="0.55"/>')
    body.append(f'<circle cx="{w * 0.08:.0f}" cy="{h * 0.95:.0f}" r="{h * 0.42:.0f}" fill="{t["tint3"]}" opacity="0.45"/>')
    body.append(f'<rect x="{w * 0.42:.0f}" y="{h * 0.62:.0f}" width="{w * 0.26:.0f}" height="{h * 0.5:.0f}" rx="22" fill="{t["tint2"]}" opacity="0.5"/>')
    m, size = 60, 66
    xs = [m + i * (w - 2 * m - size) / max(1, n - 1) for i in range(n)]
    ys = [h * 0.52 - size / 2 + (-12 if i % 2 else 14) for i in range(n)]
    path = "M" + " L".join(f"{x + size / 2:.0f} {y + size / 2:.0f}" for x, y in zip(xs, ys))
    body.append(f'<path d="{path}" fill="none" stroke="{t["primary"]}" stroke-width="2" stroke-dasharray="3 8" stroke-linecap="round"/>')
    for i, (x, y, name) in enumerate(zip(xs, ys, icons)):
        body.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{size}" height="{size}" rx="18" fill="#fff" stroke="{t["primary"]}" stroke-width="2"/>')
        body.append(I.inner(name, x + (size - 32) / 2, y + (size - 32) / 2, 32, color=t["press"], fill=t["tint3"]))
    for cx, cy, r in ((w * 0.30, h * 0.2, 5), (w * 0.62, h * 0.86, 6), (w * 0.93, h * 0.78, 4), (w * 0.17, h * 0.3, 4)):
        body.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="none" stroke="{t["primary"]}" stroke-width="2"/>')
    return _svg(w, h, "".join(body), "封面插画", t)


# ----------------------------------------------------------------------------------------------- layered architecture
def arch_layers(data: dict[str, Any], t: dict[str, str], w: int) -> str:
    plain = bool(data.get("plain"))        # formal documents: no icons inside the figure, text only
    off = 24 if plain else 46              # room the node name leaves for an icon
    layers = data["layers"]
    ext = data.get("external")
    flows = data.get("flows", [])
    cross = data.get("cross", [])
    pad, lw = 4, 108 if w > 800 else 84
    ext_w = 200 if ext else 0
    skip = [f for f in flows if abs(_layer_of(layers, f["from"]) - _layer_of(layers, f["to"])) > 1]
    ext_flows = [f for f in flows if ext and (_ext_node(ext, f["from"]) or _ext_node(ext, f["to"]))]
    inner_flows = [f for f in flows if f not in ext_flows]
    lane_zone = 18 * (len([f for f in skip if f not in ext_flows]) + len(ext_flows)) + (10 if (skip or ext_flows) else 0)
    x0 = pad + lw + 10
    x1 = w - pad - (ext_w + 14 if ext else 0) - lane_zone
    inner_w = x1 - x0
    P = palette(t)
    S = _hue(*SLATE)                       # the external column and the cross-cutting guarantees: no layer hue

    # --- node geometry per layer
    geo: dict[str, dict[str, float]] = {}
    layer_boxes = []
    crossings = [0] * len(layers)
    for f in inner_flows:
        la_, lb2 = _layer_of(layers, f["from"]), _layer_of(layers, f["to"])
        a, b = sorted((la_, lb2))
        if b - a <= 1:
            crossings[a] += 1           # between two layers, or inside one (those run in the gap below the layer)
        else:                       # a link that skips layers runs in the right margin: one lane beside each end only
            crossings[(la_ if la_ < lb2 else la_ - 1)] += 1
            crossings[(lb2 - 1 if la_ < lb2 else lb2)] += 1
    for f in ext_flows:
        src = _ext_node(ext, f["from"]) or _ext_node(ext, f["to"])
        other = f["to"] if _ext_node(ext, f["from"]) else f["from"]
        li = _layer_of(layers, other)
        crossings[max(li - 1, 0) if li > 0 else 0] += 1
    top_lanes = sum(1 for f in ext_flows if _layer_of(layers, f["to"] if _ext_node(ext, f["from"]) else f["from"]) == 0)
    y = 18 + 18 * top_lanes
    for li, layer in enumerate(layers):
        groups = layer.get("groups") or [{"nodes": layer["nodes"]}]
        count = sum(len(g["nodes"]) for g in groups)
        named = any(g.get("name") for g in groups)
        gaps = 10 * (count - len(groups)) + sum(16 if g.get("name") else 0 for g in groups) + 14 * (len(groups) - 1) + 24
        node_w = min(210, (inner_w - gaps) / count)
        cpl = _chars(node_w - 22)
        role_lines = max(len(_lines(n.get("role", ""), node_w - 22)) for g in groups for n in g["nodes"])
        name_lines = max(len(_lines(n["name"], node_w - off, F_NAME)) for g in groups for n in g["nodes"])
        node_h = 12 + 24 + 19 * (name_lines - 1) + 19 * role_lines + 8
        band_h = 10 + (24 if named else 0) + node_h + 10
        total = sum(len(g["nodes"]) * node_w + 10 * (len(g["nodes"]) - 1) + (16 if g.get("name") else 0) for g in groups) + 14 * (len(groups) - 1)
        x = x0 + (inner_w - total) / 2
        gx = []
        for g in groups:
            gw = len(g["nodes"]) * node_w + 10 * (len(g["nodes"]) - 1) + (16 if g.get("name") else 0)
            gx.append((g, x, gw))
            nx = x + (8 if g.get("name") else 0)
            for n in g["nodes"]:
                geo[n["id"]] = {"x": nx, "y": y + 10 + (24 if named else 0), "w": node_w, "h": node_h, "layer": li, "mid": nx + node_w / 2}
                nx += node_w + 10
            x += gw + 14
        layer_boxes.append({"y": y, "h": band_h, "groups": gx, "named": named, "layer": layer, "li": li})
        y += band_h + 16 + 15 * crossings[li]
    bottom_layers = y - 16            # includes the lanes below the last layer, which only same-layer links use

    # --- external column
    ext_boxes = []
    if ext:
        ex = w - pad - ext_w
        used = None
        for n in ext["nodes"]:
            li = min(int(n.get("layer", 1)), len(layers) - 1)
            lb = layer_boxes[li]
            lines = len(_lines(n.get("role", ""), ext_w - 24))
            nh = 14 + 24 + 19 * lines + 12
            ny = lb["y"] + (lb["h"] - nh) / 2
            if used is not None and ny < used + 12:
                ny = used + 12
            geo[n["id"]] = {"x": ex + 12, "y": ny, "w": ext_w - 24, "h": nh, "layer": li, "mid": ex + 12 + (ext_w - 24) / 2, "ext": 1}
            used = ny + nh
            ext_boxes.append((n, geo[n["id"]]))
        ext_top = min(g["y"] for _, g in ext_boxes) - 40
        ext_bot = max(g["y"] + g["h"] for _, g in ext_boxes) + 12
        bottom_layers = max(bottom_layers, ext_bot)

    # --- cross-cutting guarantees
    cross_h = 0
    cross_svg = ""
    if cross:
        cy = bottom_layers + 22
        per = 3 if w > 800 else 2
        cw = (x1 + (ext_w + 14 if ext else 0) + lane_zone - x0) / per
        rows = math.ceil(len(cross) / per)
        for k, c in enumerate(cross):
            cx = x0 + (k % per) * cw
            cyk = cy + (k // per) * 70
            tl = _lines(c["text"], cw - (34 if plain else 70))
            tx = cx + (14 if plain else 50)
            cross_svg += (f'<rect x="{cx:.1f}" y="{cyk:.1f}" width="{cw - 10:.1f}" height="62" rx="12" fill="{S["fill"]}" stroke="{S["line"]}" stroke-dasharray="4 4"/>'
                          + ("" if plain else I.inner(c.get("icon", "shield"), cx + 12, cyk + 14, 28, color=S["ink"], fill=S["line"]))
                          + _text(tx, cyk + 26, c["name"], size=F_NAME, weight=600, fill=t["ink"])
                          + _text(tx, cyk + 48, tl[0] + ("…" if len(tl) > 1 else ""), fill=t["ink2"]))
        cross_svg = (f'<text x="{pad + lw / 2:.1f}" y="{cy + 38:.1f}" font-size="14" font-weight="600" fill="{S["ink"]}" text-anchor="middle">横向保障</text>' + cross_svg)
        cross_h = 22 + rows * 70
    height = bottom_layers + cross_h + 8

    # --- draw: faces, group borders, nodes, then group titles, then every link on top of them
    body = []
    titles: list[str] = []
    chip_of: dict[str, tuple[float, float]] = {}      # horizontal span of the group title above each node: no link enters there
    hue_of: dict[int, dict[str, str]] = {}
    for lb in layer_boxes:
        h = hue_of[lb["li"]] = P[lb["li"] % len(P)]
        body.append(f'<rect x="{x0 - 6:.1f}" y="{lb["y"]:.1f}" width="{inner_w + 12:.1f}" height="{lb["h"]:.1f}" rx="14" fill="{h["fill"]}" stroke="{h["line"]}"/>')
        layer = lb["layer"]
        ly = lb["y"] + lb["h"] / 2
        layer_lines = _lines(layer["name"], lw - 8, F_NAME)
        if not plain:
            body.append(f'<rect x="{pad + lw / 2 - 18:.1f}" y="{ly - 40:.1f}" width="36" height="36" rx="10" fill="{h["fill"]}" stroke="{h["line"]}"/>')
            body.append(I.inner(layer.get("icon") or I.pick(layer["name"]), pad + lw / 2 - 12, ly - 34, 24, color=h["ink"], fill=h["line"]))
        first = ly + 5 - 10 * (len(layer_lines) - 1) if plain else ly + 14
        for k, line in enumerate(layer_lines):
            body.append(_text(pad + lw / 2, first + k * 20, line, size=F_NAME, weight=600, fill=h["ink"], anchor="middle"))
        for g, gx, gw in lb["groups"]:
            if g.get("name"):
                body.append(f'<rect x="{gx:.1f}" y="{lb["y"] + 8:.1f}" width="{gw:.1f}" height="{lb["h"] - 16:.1f}" rx="10" fill="none" stroke="{h["line"]}" stroke-dasharray="4 4"/>')
                cw_ = width(g["name"]) * 7.2 + 10
                titles.append(f'<rect x="{gx + 6:.1f}" y="{lb["y"] + 11:.1f}" width="{cw_:.1f}" height="20" rx="4" fill="{h["fill"]}"/>'
                              f'<text x="{gx + 10:.1f}" y="{lb["y"] + 27:.1f}" font-size="14" font-weight="600" fill="{h["ink"]}">{E(g["name"])}</text>')
                for n in g["nodes"]:
                    chip_of[n["id"]] = (gx + 6, gx + 6 + cw_)
    for li, layer in enumerate(layers):
        for g in layer.get("groups") or [{"nodes": layer["nodes"]}]:
            for n in g["nodes"]:
                body.append(_node(n, geo[n["id"]], t, plain, hue_of[li]))
    if ext:
        body.append(f'<rect x="{w - pad - ext_w:.1f}" y="{ext_top:.1f}" width="{ext_w:.1f}" height="{ext_bot - ext_top:.1f}" rx="14" fill="#fff" stroke="{S["line"]}" stroke-width="1.5" stroke-dasharray="6 5"/>')
        if not plain:
            body.append(I.inner(ext.get("icon", "cloud"), w - pad - ext_w + 14, ext_top + 10, 22, color=S["ink"], fill=S["line"]))
        body.append(_text(w - pad - ext_w + (14 if plain else 44), ext_top + 28, ext.get("title", "外部系统"), size=F_NAME, weight=600, fill=t["ink"]))
        for n, g in ext_boxes:
            body.append(_node(n, g, t, plain, S))
    # --- flows. A node has its links on two sides (top, bottom); on each side they leave in the order of where they go, left to right
    # (a link to the right margin or the external column last), so that a link going straight down never crosses the lane of one going sideways.
    used_lane = [0] * (len(layers) + 1)
    used_top = [0] * (len(layers) + 1)      # lanes of the gap ABOVE a layer, taken by the links to the external column; used_lane counts those below it
    buckets: dict[tuple[str, bool], list[tuple[float, int, str]]] = {}
    for k, f in enumerate(flows):
        a, b = f["from"], f["to"]
        if ext and (geo[a].get("ext") or geo[b].get("ext")):
            inner = b if geo[a].get("ext") else a
            buckets.setdefault((inner, True), []).append((1e9, k, "i"))
            continue
        la, lb_ = geo[a]["layer"], geo[b]["layer"]
        far = abs(la - lb_) > 1
        buckets.setdefault((a, la > lb_), []).append((1e9 if far else geo[b]["mid"], k, "a"))
        buckets.setdefault((b, la < lb_), []).append((1e9 if far else geo[a]["mid"], k, "b"))
    portx: dict[tuple[int, str], float] = {}
    for (nid, top), items in buckets.items():
        items.sort()
        g_ = geo[nid]
        lo, hi = g_["x"] + 8, g_["x"] + g_["w"] - 8
        xs = [g_["mid"] + (r - (len(items) - 1) / 2) * 14 for r in range(len(items))]
        if top and nid in chip_of:                      # a link entering from above keeps clear of the group title
            cl, cr = chip_of[nid]
            xs = [cr + 10 if cl - 4 <= x <= cr + 4 else x for x in xs]
        out: list[float] = []
        for x in xs:
            x = min(max(x, lo), hi)
            out.append(max(x, out[-1] + 12) if out else x)      # at least 12 px between two links of one side, in the order of their targets
        shift = max(0.0, out[-1] - hi)
        for (_, k, role), x in zip(items, out):
            portx[(k, role)] = x - shift

    def px(nid: str, top: bool, k: int, role: str) -> float:
        return portx[(k, role)]

    skip_x = x1 + 12
    arrows, badges = [], []
    stroke = f'fill="none" stroke="{_link(t)}" stroke-width="1.5" stroke-linejoin="round" marker-end="url(#ar)"'
    for k, f in enumerate(flows):
        n = f.get("n", k + 1)
        a, b = f["from"], f["to"]
        ga, gb = geo[a], geo[b]
        if ext and (ga.get("ext") or gb.get("ext")):
            inner_id, ext_id = (b, a) if ga.get("ext") else (a, b)
            gi, ge = geo[inner_id], geo[ext_id]
            li = gi["layer"]
            lane = (lb_y := layer_boxes[li]["y"]) - 12 - 18 * used_top[li]
            used_top[li] += 1
            xi = px(inner_id, True, k, "i")
            lane_x = x1 + lane_zone - 18 * (k % max(1, len(ext_flows))) - 8
            ye = ge["y"] + ge["h"] / 2
            d = f"M{xi:.1f} {gi['y']:.1f} V{lane:.1f} H{lane_x:.1f} V{ye:.1f} H{ge['x'] - 2:.1f}"
            if ga.get("ext"):
                d = f"M{ga['x']:.1f} {ye:.1f} H{lane_x:.1f} V{lane:.1f} H{xi:.1f} V{gi['y'] - 2:.1f}"
            arrows.append(f'<path d="{d}" {stroke}/>')
            badges.append(_badge((xi + lane_x) / 2, lane, n, t))
            continue
        la, lb_ = ga["layer"], gb["layer"]
        xa, xb = px(a, la > lb_, k, "a"), px(b, la < lb_, k, "b")     # a link leaves a node at the bottom going down, at the top going up; inside one layer at the bottom
        if abs(la - lb_) == 1:
            g = min(la, lb_)
            ly = layer_boxes[g]["y"] + layer_boxes[g]["h"] + 11 + 15 * used_lane[g]
            used_lane[g] += 1
            if la < lb_:
                d = f"M{xa:.1f} {ga['y'] + ga['h']:.1f} V{ly:.1f} H{xb:.1f} V{gb['y'] - 2:.1f}"
            else:
                d = f"M{xa:.1f} {ga['y']:.1f} V{ly:.1f} H{xb:.1f} V{gb['y'] + gb['h'] + 2:.1f}"
            arrows.append(f'<path d="{d}" {stroke}/>')
            badges.append(_badge((xa + xb) / 2 if abs(xa - xb) > 30 else xa + 20, ly, n, t))
        elif la == lb_:
            ly = layer_boxes[la]["y"] + layer_boxes[la]["h"] + 11 + 15 * used_lane[la]      # the gap below the layer, like every other link
            used_lane[la] += 1
            d = f"M{xa:.1f} {ga['y'] + ga['h']:.1f} V{ly:.1f} H{xb:.1f} V{gb['y'] + gb['h'] + 2:.1f}"
            arrows.append(f'<path d="{d}" {stroke}/>')
            badges.append(_badge((xa + xb) / 2 if abs(xa - xb) > 30 else xa + (24 if xb >= xa else -24), ly, n, t))
        else:
            lo, hi = sorted((la, lb_))
            sx = skip_x + 18 * (len([1 for z in arrows if "skip" in z]))
            gs = la if la < lb_ else la - 1
            gt = lb_ - 1 if la < lb_ else lb_
            ys = layer_boxes[gs]["y"] + layer_boxes[gs]["h"] + 11 + 15 * used_lane[gs]
            used_lane[gs] += 1
            yt = layer_boxes[gt]["y"] + layer_boxes[gt]["h"] + 11 + 15 * used_lane[gt]
            used_lane[gt] += 1
            if la < lb_:
                d = f"M{xa:.1f} {ga['y'] + ga['h']:.1f} V{ys:.1f} H{sx:.1f} V{yt:.1f} H{xb:.1f} V{gb['y'] - 2:.1f}"
            else:
                d = f"M{xa:.1f} {ga['y']:.1f} V{ys:.1f} H{sx:.1f} V{yt:.1f} H{xb:.1f} V{gb['y'] + gb['h'] + 2:.1f}"
            arrows.append(f'<path d="{d}" {stroke} data-skip="1"/>')
            badges.append(_badge(sx, (ys + yt) / 2, n, t))
    return _svg(w, height, "".join(body) + "".join(titles) + "".join(arrows) + "".join(badges) + cross_svg, data.get("title", "系统架构图"), t)


def _layer_of(layers: list[dict], nid: str) -> int:
    for i, layer in enumerate(layers):
        for g in layer.get("groups") or [{"nodes": layer["nodes"]}]:
            if any(n["id"] == nid for n in g["nodes"]):
                return i
    return -1


def _ext_node(ext: dict | None, nid: str) -> bool:
    return bool(ext) and any(n["id"] == nid for n in ext["nodes"])


def _node(n: dict, g: dict, t: dict[str, str], plain: bool = False, h: dict[str, str] | None = None) -> str:
    h = h or _hue(t["primary"], t["tint1"])
    x, y, w_, hh = g["x"], g["y"], g["w"], g["h"]
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w_:.1f}" height="{hh:.1f}" rx="10" fill="#fff" stroke="{h["stroke"]}" stroke-width="1.6"/>']
    if not plain:
        out.append(I.inner(n.get("icon") or I.pick(n["name"]), x + 10, y + 11, 22, color=h["ink"], fill=h["line"]))
    name_lines = _lines(n["name"], w_ - (24 if plain else 46), F_NAME)
    for k, line in enumerate(name_lines):
        out.append(_text(x + (12 if plain else 38), y + 28 + k * 19, line, size=F_NAME, weight=600, fill=t["ink"]))
    base = y + 28 + 19 * (len(name_lines) - 1)
    for k, line in enumerate(_lines(n.get("role", ""), w_ - 22)):
        out.append(_text(x + 12, base + 22 + k * 19, line, fill=t["ink2"]))
    if n.get("tag"):
        out.append(_tag(x + w_, y, n["tag"], h))
    return "".join(out)


# ----------------------------------------------------------------------------------------------- swimlane
GUTTER_OFFSETS = (0, 5, -5)      # links that share a gutter between two columns turn 5 px apart (the gutter is 26 px, a box is 13 px from its middle)


def swimlane(data: dict[str, Any], t: dict[str, str], w: int) -> str:
    plain = bool(data.get("plain"))
    lanes, stages, steps = data["lanes"], data["stages"], data["steps"]
    pad, lw, head_h = 4, 96 if w > 800 else 76, 36
    col_w = (w - 2 * pad - lw) / len(stages)
    box_w = col_w - 26          # a 26 px gutter between columns: the link turns in its middle, 13 px from either box
    lines_max = max(len(_lines(s["text"], box_w - 16)) for s in steps)
    box_h = 18 + 18 * lines_max + 6
    lane_h = box_h + 24
    height = pad + head_h + lane_h * len(lanes) + 8
    P = palette(t)
    hues = [P[i % len(P)] for i in range(len(lanes))]
    N = _hue(*SLATE)
    ink = _link(t)
    body = []
    for i, lane in enumerate(lanes):
        y = pad + head_h + i * lane_h
        h = hues[i]
        body.append(f'<rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="{lane_h}" fill="{mix(h["fill"], "#FFFFFF", 0.55)}" stroke="{h["line"]}"/>')
        body.append(f'<rect x="{pad}" y="{y}" width="{lw}" height="{lane_h}" fill="{h["fill"]}" stroke="{h["line"]}"/>')
        lane_lines = _lines(lane["name"], lw - 10, F_NAME)
        if not plain:
            body.append(I.inner(lane.get("icon") or I.pick(lane["name"]), pad + lw / 2 - 12, y + lane_h / 2 - 28, 24, color=h["ink"], fill=h["line"]))
        first = y + lane_h / 2 + 5 - 9.5 * (len(lane_lines) - 1) if plain else y + lane_h / 2 + 10
        for k, line in enumerate(lane_lines):
            body.append(_text(pad + lw / 2, first + k * 19, line, size=F_NAME, weight=600, fill=h["ink"], anchor="middle"))
    for j, s in enumerate(stages):
        x = pad + lw + j * col_w
        body.append(f'<rect x="{x + 4:.1f}" y="{pad + 4}" width="{col_w - 8:.1f}" height="{head_h - 10}" rx="8" fill="{N["fill"]}" stroke="{N["line"]}"/>')
        body.append(_text(x + col_w / 2, pad + 4 + 20, f"{j + 1} {s}", weight=600, fill=t["ink"], anchor="middle"))
    pos, lane_of, stage_of = {}, {}, {}
    for s in steps:
        li = next(i for i, l in enumerate(lanes) if l["name"] == s["lane"])
        j = int(s["stage"]) - 1
        pos[s["id"]] = (pad + lw + j * col_w + 13, pad + head_h + li * lane_h + 12)
        lane_of[s["id"]], stage_of[s["id"]] = li, j

    def blocked(points: list[tuple[float, float]], ignore: set[str]) -> bool:
        """Whether a polyline passes through (or within 3 px of) a step box other than the ones it joins."""
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            xl, xr, yt, yb = min(ax, bx), max(ax, bx), min(ay, by), max(ay, by)
            for sid, (rx, ry) in pos.items():
                if sid not in ignore and xr > rx - 3 and xl < rx + box_w + 3 and yb > ry - 3 and yt < ry + box_h + 3:
                    return True
        return False

    used_gutter: dict[int, int] = {}
    paths, labels = [], []
    for lk in data.get("links", []):
        a, b = lk["from"], lk["to"]
        (xa, ya), (xb, yb) = pos[a], pos[b]
        x1, y1, x2, y2 = xa + box_w, ya + box_h / 2, xb, yb + box_h / 2
        ja, jb = stage_of[a], stage_of[b]
        off = GUTTER_OFFSETS[used_gutter.get(ja, 0) % len(GUTTER_OFFSETS)]
        used_gutter[ja] = used_gutter.get(ja, 0) + 1
        g_out = x1 + 13 + off              # the gutter after the source column
        g_in = x2 - 13 + (off if jb == ja + 1 else 0)     # the gutter before the target column
        ch = pos[b][1] - 6                 # the channel above the target's row, clear of every box
        ends = {a, b}
        straight = [(x1, y1), (x2 - 2, y2)]
        options = ([straight] if abs(y1 - y2) < 1 else []) + [
            [(x1, y1), (g_out, y1), (g_out, y2), (x2 - 2, y2)],
            [(x1, y1), (g_in, y1), (g_in, y2), (x2 - 2, y2)],
            [(x1, y1), (g_out, y1), (g_out, ch), (g_in, ch), (g_in, y2), (x2 - 2, y2)]]
        pts = next((o for o in options if not blocked(o, ends)), options[-1])
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        paths.append(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="1.5" stroke-linejoin="round" marker-end="url(#ar)"/>')
        if lk.get("label"):
            run = max(zip(pts, pts[1:]), key=lambda s: abs(s[0][0] - s[1][0]) if abs(s[0][1] - s[1][1]) < 1 else 0)
            cx, cy = (run[0][0] + run[1][0]) / 2, run[0][1]
            labels.append(f'<rect x="{cx - width(lk["label"]) * 3.6 - 6:.1f}" y="{cy - 11:.1f}" width="{width(lk["label"]) * 7.2 + 12:.1f}" height="22" rx="6" fill="#fff" stroke="{N["line"]}"/>'
                          + _text(cx, cy + 5, lk["label"], fill=t["ink"], anchor="middle"))
    body.extend(paths)
    for s in steps:
        x, y = pos[s["id"]]
        h = hues[lane_of[s["id"]]]
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{box_w:.1f}" height="{box_h}" rx="10" fill="#fff" stroke="{h["stroke"]}" stroke-width="1.6"/>')
        body.append(_badge(x + 2, y + 2, s["id"], t))
        for k, line in enumerate(_lines(s["text"], box_w - 16)):
            body.append(_text(x + box_w / 2, y + 26 + k * 18, line, fill=t["ink"], anchor="middle"))
        if s.get("tag"):
            body.append(_tag(x + box_w + 6, y + box_h, s["tag"], h))
    body.extend(labels)
    return _svg(w, height, "".join(body), data.get("title", "业务流程泳道图"), t)


# ----------------------------------------------------------------------------------------------- deployment
def deployment(data: dict[str, Any], t: dict[str, str], w: int) -> str:
    plain = bool(data.get("plain"))
    zones = data["zones"]
    pad = 4
    cols = max(z.get("col", i) for i, z in enumerate(zones)) + 1
    rows = max(z.get("row", 0) for z in zones) + 1
    # the gap between two zones holds the arrow and its label: wide enough for the longest label, but a zone keeps at least 150 px
    side_labels = [width(lk["label"]) * 7.2 + 12 + 20 for lk in data.get("links", []) if lk.get("label") and zones[lk["from"]].get("row", 0) == zones[lk["to"]].get("row", 0)]
    gap = max(56.0, max(side_labels, default=0))
    if cols > 1:
        gap = min(gap, (w - 2 * pad - 150 * cols) / (cols - 1))
    zw = (w - 2 * pad - gap * (cols - 1)) / cols
    sizes = []
    for z in zones:
        hh = 46
        for n in z["nodes"]:
            hh += 10 + 22 + 18 * len(_lines(n.get("role", ""), zw - 40)) + 8 + 8
        sizes.append(hh + 8)
    row_h = [max(sizes[i] for i, z in enumerate(zones) if z.get("row", 0) == r) for r in range(rows)]
    ys = [pad + sum(row_h[:r]) + 44 * r for r in range(rows)]
    height = pad + sum(row_h) + 44 * (rows - 1) + 8
    P = palette(t)
    S = _hue(*SLATE)
    body, geo = [], {}
    for i, z in enumerate(zones):
        c, r = z.get("col", i), z.get("row", 0)
        x, y, h = pad + c * (zw + gap), ys[r], row_h[r]
        geo[i] = (x, y, zw, h)
        external = z.get("kind") == "external"
        hue = S if external else P[c % len(P)]
        dash = ' stroke-dasharray="6 5"' if external else ""
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{zw:.1f}" height="{h:.1f}" rx="16" fill="{"#fff" if external else hue["fill"]}" stroke="{hue["line"]}" stroke-width="1.5"{dash}/>')
        if not plain:
            body.append(I.inner(z.get("icon") or I.pick(z["name"]), x + 14, y + 12, 24, color=hue["ink"], fill=hue["line"]))
        body.append(_text(x + (16 if plain else 46), y + 31, z["name"], size=F_NAME, weight=600, fill=hue["ink"]))
        ny = y + 44
        for n in z["nodes"]:
            lines = _lines(n.get("role", ""), zw - 40)
            nh = 10 + 22 + 18 * len(lines) + 8
            body.append(f'<rect x="{x + 12:.1f}" y="{ny:.1f}" width="{zw - 24:.1f}" height="{nh}" rx="10" fill="#fff" stroke="{hue["stroke"]}" stroke-width="1.5"/>')
            if not plain:
                body.append(I.inner(n.get("icon") or I.pick(n["name"]), x + 22, ny + 9, 22, color=hue["ink"], fill=hue["line"]))
            body.append(_text(x + (24 if plain else 50), ny + 26, n["name"], size=F_NAME, weight=600, fill=t["ink"]))
            for k, line in enumerate(lines):
                body.append(_text(x + 24, ny + 26 + 22 + k * 18, line, fill=t["ink2"]))
            if n.get("tag"):
                body.append(_tag(x + zw - 12, ny, n["tag"], hue))
            ny += nh + 8
    for lk in data.get("links", []):
        xa, ya, wa, ha = geo[lk["from"]]
        xb, yb, wb, hb = geo[lk["to"]]
        stroke = f'fill="none" stroke="{_link(t)}" stroke-width="1.8" marker-end="url(#ar)"'
        if abs(ya - yb) < 1:
            y_mid = ya + 70
            x1, x2 = (xa + wa, xb) if xa < xb else (xa, xb + wb)
            body.append(f'<path d="M{x1:.1f} {y_mid:.1f} H{x2 + (-3 if xa < xb else 3):.1f}" {stroke}/>')
            if lk.get("label"):
                lbl = lk["label"]
                body.append(f'<rect x="{(x1 + x2) / 2 - width(lbl) * 3.6 - 6:.1f}" y="{y_mid - 38:.1f}" width="{width(lbl) * 7.2 + 12:.1f}" height="22" rx="6" fill="#fff" stroke="{S["line"]}"/>')
                body.append(_text((x1 + x2) / 2, y_mid - 22, lbl, fill=t["ink"], anchor="middle"))
        else:
            xm = xa + wa / 2
            y1, y2 = (ya + ha, yb - 3) if ya < yb else (ya, yb + hb + 3)
            body.append(f'<path d="M{xm:.1f} {y1:.1f} V{y2:.1f}" {stroke}/>')
            if lk.get("label"):
                lbl = lk["label"]
                body.append(f'<rect x="{xm + 8:.1f}" y="{(y1 + y2) / 2 - 11:.1f}" width="{width(lbl) * 7.2 + 12:.1f}" height="22" rx="6" fill="#fff" stroke="{S["line"]}"/>')
                body.append(_text(xm + 14, (y1 + y2) / 2 + 5, lbl, fill=t["ink"]))
    return _svg(w, height, "".join(body), data.get("title", "部署与数据流"), t)
