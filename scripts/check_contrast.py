#!/usr/bin/env python3
"""检查 themes.json 中每套主题的关键对比度与配色规则。

规则（对应 references/visual-design.html “一、视觉基础”）：
- 白字（surface）在 action / actionPress 上 >= 4.5:1（按钮文字）
- actionPress 文字在 actionTint 上 >= 4.5:1（浅底上的选中态文字用按压档，TDesign 色阶规则）
- 白字在 action 上 >= 4.5:1 同时保证开关、图表用 action 时对白底 >= 3:1（WCAG 1.4.11）
- ink / ink2 在 canvas 上 >= 4.5:1（正文与辅助文字）
- ink 在 navBg 上 >= 4.5:1；ink2 在 navBg 上 >= 3.0:1（导航栏只放 ink 文字与图标）
- ink3 在 surface 上 >= 4.5:1
- success / warning / danger / info 在 surface 上 >= 4.5:1
- ink 在 accentTint 上 >= 4.5:1（accent 只做底色，不做文字）
- canvas 为浅白、极浅灰的中性色（与同明度灰的 RGB 偏差 <= 2），或与主色同色相（相差 <= 12 度）的极浅底，亮度都 >= 0.85；navBg 用白底或主色浅底阶纯色
- scale（可选，整列 10 阶）：第 1、6、7 阶等于 actionTint / action / actionPress；第 2、3 阶亮度 >= 0.60（可作大面积浅色块）；
  第 9 阶对白 >= 7:1 且对第 1 阶 >= 4.5:1（深色强调文字）；明度逐阶下降
- modules（可选，一级模块点缀色）：tint 亮度 >= 0.80，mid 亮度 >= 0.60，solid 对白与对 tint >= 4.5:1；
  非品牌点缀色的色相与 success / warning / danger 相差 >= 25 度、与主色相差 >= 20 度、彼此相差 >= 25 度；一个颜色只代表一个模块
- 品牌主卡：白字在 action 上 >= 4.5:1（与按钮同一检查）
- dark（可选）：ink(dark) 在 dark.canvas / dark.surface 上 >= 4.5；白字在 dark.action 上 >= 4.5
- shadowTone（可选，阴影换成主题暗调时）：等于 scale 第 10 阶
- shared.elevation（visual-design.html 层级与立体感）：level1–level4 每级两层外阴影，只向下（x = 0、y > 0），
  近处一层的偏移与模糊小于远处一层，颜色为深色（亮度 <= 0.05：中性深色或主题第 10 阶暗调），单层透明度 0–0.2；
  逐级之间远处一层的偏移与模糊增大、近处模糊不减小，远处一层的浓度（透明度 / 模糊）降低（越远越大、越柔、越淡）；
  hairline 透明度 0.06–0.10，hairlineStrong 比 hairline 深且 <= 0.2；highlight 为 1 像素白色内顶边 0.6–0.8，
  highlightSolid 为 0.16–0.24（实色面）；scrim 为深色 0.40–0.50；focusRing 为无偏移无模糊的 2–4 像素环；buttonEdge 为向下 1–2 像素、无模糊的边线
失败时返回非零退出码。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

THEMES = Path(__file__).resolve().parents[1] / "references" / "themes.json"
DARK_INK = "#F5EFEA"


def rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))


def luminance(color: str) -> float:
    values = [v / 255 for v in rgb(color)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def chroma(color: str) -> int:
    r, g, b = rgb(color)
    return max(r, g, b) - min(r, g, b)


def hue(color: str) -> float:
    import colorsys
    r, g, b = (v / 255 for v in rgb(color))
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360


def hue_gap(a: str, b: str) -> float:
    d = abs(hue(a) - hue(b)) % 360
    return min(d, 360 - d)


MIN_STATUS_GAP = 25.0
MIN_ACTION_GAP = 20.0
MIN_MODULE_GAP = 25.0


SHADOW_LEVELS = ("level1", "level2", "level3", "level4")
MAX_LAYER_ALPHA = 0.2


def shadow_layers(value: str) -> list[dict]:
    """Each layer of a CSS box-shadow: inset, x, y, blur, spread, colour (hex) and alpha."""
    import re
    layers = []
    for part in re.split(r",(?![^(]*\))", value or ""):
        if not part.strip():
            continue
        colour, alpha = "#000000", 1.0
        m = re.search(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)(?:[ ,/]+([\d.]+))?\s*\)", part)
        if m:
            colour = "#%02X%02X%02X" % tuple(int(m.group(i)) for i in (1, 2, 3))
            alpha = float(m.group(4)) if m.group(4) else 1.0
        else:
            h = re.search(r"#([0-9a-fA-F]{6})\b", part)
            if h:
                colour = "#" + h.group(1).upper()
        lengths = re.sub(r"rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b|\binset\b", " ", part)
        nums = [float(n) for n in re.findall(r"-?\d*\.?\d+", lengths)] + [0.0] * 4
        layers.append({"inset": "inset" in part, "x": nums[0], "y": nums[1], "blur": nums[2], "spread": nums[3],
                       "colour": colour, "alpha": alpha})
    return layers


def elevation_rules(elevation: dict) -> list[tuple[str, bool, str]]:
    """Shape of the elevation tokens (visual-design.html 层级与立体感; Fluent 2 key + ambient shadows, Ant Design shadow levels)."""
    rules: list[tuple[str, bool, str]] = []
    levels = []
    for level in SHADOW_LEVELS:
        layers = shadow_layers(elevation.get(level, ""))
        alphas = [layer["alpha"] for layer in layers]
        two = len(layers) == 2 and not any(layer["inset"] for layer in layers)
        rules.append((f"{level} 两层外阴影", two, f"{len(layers)} layers"))
        if not two:
            continue
        near, far = sorted(layers, key=lambda layer: layer["blur"])
        rules += [
            (f"{level} 只向下", all(layer["x"] == 0 and layer["y"] > 0 for layer in layers),
             ", ".join(f"{layer['x']:g} {layer['y']:g}" for layer in layers)),
            (f"{level} 近处锐利、远处柔和", near["y"] < far["y"] and near["blur"] < far["blur"],
             f"near {near['y']:g}/{near['blur']:g} far {far['y']:g}/{far['blur']:g}"),
            (f"{level} 深色阴影", all(luminance(layer["colour"]) <= 0.05 for layer in layers),
             " ".join(sorted({layer["colour"] for layer in layers}))),
            (f"{level} 单层透明度 <= {MAX_LAYER_ALPHA:g}", all(0 < a <= MAX_LAYER_ALPHA for a in alphas),
             f"max alpha {max(alphas):g}"),
        ]
        levels.append((level, near, far))
    for (a, near_a, far_a), (b, near_b, far_b) in zip(levels, levels[1:]):
        density_a, density_b = far_a["alpha"] / far_a["blur"], far_b["alpha"] / far_b["blur"]
        rules += [
            (f"{a} → {b} 远处更大更柔", far_b["y"] > far_a["y"] and far_b["blur"] > far_a["blur"] and near_b["blur"] >= near_a["blur"],
             f"far {far_a['y']:g}/{far_a['blur']:g} → {far_b['y']:g}/{far_b['blur']:g}"),
            (f"{a} → {b} 远处更淡", density_b < density_a, f"alpha/blur {density_a:.4f} → {density_b:.4f}"),
        ]

    def alpha_of(token: str) -> tuple[str, float]:
        layers = shadow_layers(token if token.strip().startswith(("0", "inset")) else f"0 0 0 {token}")
        return (layers[0]["colour"], layers[0]["alpha"]) if layers else ("#000000", 0.0)

    if "hairline" in elevation:
        colour, alpha = alpha_of(elevation["hairline"])
        rules.append(("hairline 深色 0.06–0.10", luminance(colour) <= 0.05 and 0.06 <= alpha <= 0.10, f"{alpha:g}"))
        if "hairlineStrong" in elevation:
            strong = alpha_of(elevation["hairlineStrong"])[1]
            rules.append(("hairlineStrong 比 hairline 深", alpha < strong <= MAX_LAYER_ALPHA, f"{strong:g}"))
    for token, low, high in (("highlight", 0.6, 0.8), ("highlightSolid", 0.16, 0.24)):
        if token in elevation:
            layers = shadow_layers(elevation[token])
            layer = layers[0] if len(layers) == 1 else None
            ok = bool(layer) and layer["inset"] and layer["x"] == 0 and layer["y"] == 1 and layer["blur"] == 0                 and layer["colour"] == "#FFFFFF" and low <= layer["alpha"] <= high
            rules.append((f"{token} 白色内顶边 {low:g}–{high:g}", ok, elevation[token]))
    if "scrim" in elevation:
        colour, alpha = alpha_of(elevation["scrim"])
        rules.append(("scrim 深色 0.40–0.50", luminance(colour) <= 0.05 and 0.40 <= alpha <= 0.50, f"{alpha:g}"))
    if "focusRing" in elevation:
        ring = shadow_layers(elevation["focusRing"])
        ok = len(ring) == 1 and ring[0]["x"] == ring[0]["y"] == ring[0]["blur"] == 0 and 2 <= ring[0]["spread"] <= 4
        rules.append(("focusRing 无模糊实色环 2–4", ok, elevation["focusRing"]))
    if "buttonEdge" in elevation:
        edge = shadow_layers(elevation["buttonEdge"])
        ok = len(edge) == 1 and edge[0]["x"] == 0 and 1 <= edge[0]["y"] <= 2 and edge[0]["blur"] == 0
        rules.append(("buttonEdge 向下 1–2 像素无模糊", ok, elevation["buttonEdge"]))
    return rules


def main() -> int:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    shared = data["shared"]
    surface = shared["surface"]
    failed = False
    for name, t in data["themes"].items():
        missing = [k for k in ("action", "actionPress", "actionTint", "canvas", "navBg", "accent", "accentTint") if k not in t]
        print(name + (f"  MISSING {missing}" if missing else ""))
        if missing:
            failed = True
            continue
        checks = [
            ("白字 on action", surface, t["action"], 4.5),
            ("白字 on actionPress", surface, t["actionPress"], 4.5),
            ("actionPress 文字 on actionTint", t["actionPress"], t["actionTint"], 4.5),
            ("ink on canvas", shared["ink"], t["canvas"], 4.5),
            ("ink2 on canvas", shared["ink2"], t["canvas"], 4.5),
            ("ink on navBg", shared["ink"], t["navBg"], 4.5),
            ("ink2 on navBg", shared["ink2"], t["navBg"], 3.0),
            ("ink3 on surface", shared["ink3"], surface, 4.5),
            ("success on surface", shared["success"], surface, 4.5),
            ("warning on surface", shared["warning"], surface, 4.5),
            ("danger on surface", shared["danger"], surface, 4.5),
            # Prices stay one red whatever the brand colour (Luz-System commerce-design.html 价格展示).
            ("price on surface", shared.get("price", "#D9001B"), surface, 4.5),
            ("price on priceTint", shared.get("price", "#D9001B"), shared.get("priceTint", "#FFF1F0"), 4.5),
            ("info on surface", shared.get("info", "#2F5F8A"), surface, 4.5),
            ("ink on accentTint", shared["ink"], t["accentTint"], 4.5),
        ]
        dark = t.get("dark")
        if dark:
            checks += [
                ("dark ink on dark.canvas", DARK_INK, dark["canvas"], 4.5),
                ("dark ink on dark.surface", DARK_INK, dark["surface"], 4.5),
                ("白字 on dark.action", surface, dark["action"], 4.5),
            ]
        for label, fg, bg, minimum in checks:
            value = contrast(fg, bg)
            ok = value >= minimum
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {value:5.2f}:1 (min {minimum})")
        neutral_canvas = chroma(t["canvas"]) <= 2
        tinted_canvas = hue_gap(t["canvas"], t["action"]) <= 12 and chroma(t["canvas"]) <= 16
        rules = [
            # 页面底用浅白、极浅灰的中性色，或主色同色相的极浅底（用户偏好）；导航条可用白底或主色浅底阶纯色。
            ("canvas 中性浅灰或主题极浅底", (neutral_canvas or tinted_canvas) and luminance(t["canvas"]) >= 0.85,
             f"chroma {chroma(t['canvas'])} lum {luminance(t['canvas']):.2f}"),
        ]
        scale = t.get("scale")
        if scale is not None:
            ok_len = len(scale) == 10
            rules.append(("scale 整列 10 阶", ok_len, f"{len(scale)} steps"))
            if ok_len:
                rules += [
                    ("scale 第 1/6/7 阶 = tint/action/press", [scale[0], scale[5], scale[6]] == [t["actionTint"], t["action"], t["actionPress"]],
                     f"{scale[0]} {scale[5]} {scale[6]}"),
                    ("scale 第 2–3 阶亮度 >= 0.60", min(luminance(scale[1]), luminance(scale[2])) >= 0.60,
                     f"{luminance(scale[1]):.2f} {luminance(scale[2]):.2f}"),
                    ("scale 第 9 阶对白 >= 7", contrast(scale[8], surface) >= 7, f"{contrast(scale[8], surface):.2f}:1"),
                    ("scale 第 9 阶对第 1 阶 >= 4.5", contrast(scale[8], scale[0]) >= 4.5, f"{contrast(scale[8], scale[0]):.2f}:1"),
                    ("scale 明度逐阶下降", all(luminance(a) > luminance(b) for a, b in zip(scale, scale[1:])), ""),
                ]
        if t.get("shadowTone"):
            tone_ok = bool(scale) and len(scale) == 10 and t["shadowTone"].upper() == scale[9].upper()
            rules.append(("shadowTone = scale 第 10 阶", tone_ok, t["shadowTone"]))
        modules = t.get("modules") or {}
        accents = {}
        for key, m in modules.items():
            if not all(m.get(k) for k in ("tint", "mid", "solid")):
                rules.append((f"module {key} tint/mid/solid", False, "missing"))
                continue
            rules += [
                (f"module {key} tint 亮度 >= 0.80", luminance(m["tint"]) >= 0.80, f"{luminance(m['tint']):.2f}"),
                (f"module {key} mid 亮度 >= 0.60", luminance(m["mid"]) >= 0.60, f"{luminance(m['mid']):.2f}"),
                (f"module {key} solid 对白 >= 4.5", contrast(m["solid"], surface) >= 4.5, f"{contrast(m['solid'], surface):.2f}:1"),
                (f"module {key} solid 对 tint >= 4.5", contrast(m["solid"], m["tint"]) >= 4.5, f"{contrast(m['solid'], m['tint']):.2f}:1"),
            ]
            if m.get("brand"):
                continue
            accents[key] = m["solid"]
            for status in ("success", "warning", "danger"):
                gap = hue_gap(m["solid"], shared[status])
                rules.append((f"module {key} 与 {status} 色相差 >= {MIN_STATUS_GAP:g}", gap >= MIN_STATUS_GAP, f"{gap:.0f} 度"))
            gap = hue_gap(m["solid"], t["action"])
            rules.append((f"module {key} 与主色色相差 >= {MIN_ACTION_GAP:g}", gap >= MIN_ACTION_GAP, f"{gap:.0f} 度"))
        keys = sorted(accents)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                gap = hue_gap(accents[a], accents[b])
                rules.append((f"module {a} 与 {b} 色相差 >= {MIN_MODULE_GAP:g}", gap >= MIN_MODULE_GAP, f"{gap:.0f} 度"))
        solids = [m.get("solid") for m in modules.values() if m.get("solid") and not m.get("brand")]
        if len(solids) != len(set(solids)):
            rules.append(("modules 一个颜色只代表一个模块", False, "duplicate solid"))
        for label, ok, note in rules:
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {note}")
    elevation = shared.get("elevation")
    if elevation is not None:
        print("shared.elevation")
        for label, ok, note in elevation_rules(elevation):
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {note}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
