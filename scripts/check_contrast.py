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
- dark（每个主题必备，对应 visual-design.html “深色与浅色两套主题”）：键齐全（canvas、navBg、surface、action、actionPress、onAction、actionText、actionTint、accent、accentTint、line；
  shared.dark 的 ink 三档、五个状态色与各自 Tint、successFill / warningFill / dangerFill、sage、elevation）；深色是第二套色板而不是取反：canvas 比 surface 暗、表面逐级变亮（surfaceMix 逐级不减），
  底色与主色同色相或中性；ink 在各层底（canvas、surface、navBg、actionTint、accentTint 与 surface 混入白色 level2–4 的浮起面）上 >= 7，ink2、ink3 >= 4.5；onAction 在 action / actionPress 上 >= 4.5，
  action 对 canvas / surface >= 3（WCAG 1.4.11）；actionText（品牌色文字与图标）在各层底与 actionTint 上 >= 4.5；accent 在 accentTint 与 surface 上 >= 4.5；
  状态色文字在 surface、各浮起面与自己的 Tint 上 >= 4.5，Fill 上的白字 >= 4.5；line 在 surface 上有区分（>= 1.2:1）；品牌色相、点缀色相与浅色映射相差 <= 12 度；
  shared.dark.elevation 五级：阴影只向下、两层、远处更大更柔，hairline 为白色 0.06–0.14，scrim 为黑色 0.55–0.70，焦点环与按钮底边同浅色
- shadowTone（可选，阴影换成主题暗调时）：等于 scale 第 10 阶
- shared.elevation（visual-design.html 层级与立体感）：level1–level4 每级两层外阴影，只向下（x = 0、y > 0），
  近处一层的偏移与模糊小于远处一层，颜色为深色（亮度 <= 0.05：中性深色或主题第 10 阶暗调），单层透明度 0–0.2；
  逐级之间远处一层的偏移与模糊增大、近处模糊不减小，远处一层的浓度（透明度 / 模糊）降低（越远越大、越柔、越淡）；
  hairline 透明度 0.06–0.10，hairlineStrong 比 hairline 深且 <= 0.2；highlight 为 1 像素白色内顶边 0.6–0.8，
  highlightSolid 为 0.16–0.24（实色面）；scrim 为深色 0.40–0.50；focusRing 为无偏移无模糊的 2–4 像素环；buttonEdge 为向下 1–2 像素、无模糊的边线
失败时返回非零退出码。

算法（WCAG 2.2，2024-12-12 正式推荐标准）：相对亮度 L = 0.2126 R + 0.7152 G + 0.0722 B，通道线性化以 0.04045 为界（2021-05 起的值，
原 0.03928；8 位色下两者逐值相同），对比度 (L1 + 0.05) / (L2 + 0.05)，不四舍五入（4.499:1 不达 4.5:1）。APCA 属于 WCAG 3.0 工作草稿，
该草稿写明对比度算法尚未确定，因此不作为通过依据。

单对颜色：py -X utf8 scripts/check_contrast.py --pair <前景> <背景> 打印比值，并按 4.5（正文）、3（大字与非文本）、7（本规范正文）逐档判定。
"""
from __future__ import annotations

import argparse
import json
import re
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
MAX_DARK_LAYER_ALPHA = 0.5   # 深色下阴影本来就看不出，黑色阴影可以浓一些，层级主要靠更亮的表面


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


def elevation_rules(elevation: dict, dark: bool = False) -> list[tuple[str, bool, str]]:
    """Shape of the elevation tokens (visual-design.html 层级与立体感; Fluent 2 key + ambient shadows, Ant Design shadow levels)."""
    rules: list[tuple[str, bool, str]] = []
    levels = []
    cap = MAX_DARK_LAYER_ALPHA if dark else MAX_LAYER_ALPHA
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
            (f"{level} 单层透明度 <= {cap:g}", all(0 < a <= cap for a in alphas),
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

    if "hairline" in elevation and dark:
        colour, alpha = alpha_of(elevation["hairline"])
        rules.append(("hairline 白色 0.06–0.14", colour == "#FFFFFF" and 0.06 <= alpha <= 0.14, f"{alpha:g}"))
        if "hairlineStrong" in elevation:
            strong = alpha_of(elevation["hairlineStrong"])[1]
            rules.append(("hairlineStrong 比 hairline 亮", alpha < strong <= 0.24, f"{strong:g}"))
    elif "hairline" in elevation:
        colour, alpha = alpha_of(elevation["hairline"])
        rules.append(("hairline 深色 0.06–0.10", luminance(colour) <= 0.05 and 0.06 <= alpha <= 0.10, f"{alpha:g}"))
        if "hairlineStrong" in elevation:
            strong = alpha_of(elevation["hairlineStrong"])[1]
            rules.append(("hairlineStrong 比 hairline 深", alpha < strong <= MAX_LAYER_ALPHA, f"{strong:g}"))
    for token, low, high in ((("highlight", 0.03, 0.12) if dark else ("highlight", 0.6, 0.8)), ("highlightSolid", 0.16, 0.24)):
        if token in elevation:
            layers = shadow_layers(elevation[token])
            layer = layers[0] if len(layers) == 1 else None
            ok = bool(layer) and layer["inset"] and layer["x"] == 0 and layer["y"] == 1 and layer["blur"] == 0                 and layer["colour"] == "#FFFFFF" and low <= layer["alpha"] <= high
            rules.append((f"{token} 白色内顶边 {low:g}–{high:g}", ok, elevation[token]))
    if "scrim" in elevation:
        colour, alpha = alpha_of(elevation["scrim"])
        low, high = (0.55, 0.70) if dark else (0.40, 0.50)
        rules.append((f"scrim 深色 {low:.2f}–{high:.2f}", luminance(colour) <= 0.05 and low <= alpha <= high, f"{alpha:g}"))
    if "focusRing" in elevation:
        ring = shadow_layers(elevation["focusRing"])
        ok = len(ring) == 1 and ring[0]["x"] == ring[0]["y"] == ring[0]["blur"] == 0 and 2 <= ring[0]["spread"] <= 4
        rules.append(("focusRing 无模糊实色环 2–4", ok, elevation["focusRing"]))
    if "buttonEdge" in elevation:
        edge = shadow_layers(elevation["buttonEdge"])
        ok = len(edge) == 1 and edge[0]["x"] == 0 and 1 <= edge[0]["y"] <= 2 and edge[0]["blur"] == 0
        rules.append(("buttonEdge 向下 1–2 像素无模糊", ok, elevation["buttonEdge"]))
    if dark:
        mix = elevation.get("surfaceMix") or {}
        steps = [mix.get(f"level{i}") for i in range(5)]
        numeric = all(isinstance(v, (int, float)) for v in steps)
        rules.append(("surfaceMix 五级齐全且逐级不减", numeric and all(a <= b for a, b in zip(steps, steps[1:])) and steps[0] == 0
                      and steps[-1] > steps[1], str(steps)))
        if numeric:
            rules.append(("surfaceMix 第 2–4 级逐级变亮且 <= 20%", steps[1] < steps[2] < steps[3] < steps[4] <= 20, str(steps)))
    return rules


DARK_THEME_KEYS = ("canvas", "navBg", "surface", "action", "actionPress", "onAction", "actionText", "actionTint", "accent", "accentTint", "line")
DARK_SHARED_KEYS = ("ink", "ink2", "ink3", "success", "successTint", "successFill", "warning", "warningTint", "warningFill", "danger", "dangerTint", "dangerFill",
                    "info", "infoTint", "price", "priceTint", "sage", "sageTint", "photo", "photo2", "elevation")
DARK_STATUS = (("success", "successTint"), ("warning", "warningTint"), ("danger", "dangerTint"), ("info", "infoTint"), ("price", "priceTint"))
DARK_FILLED = ("success", "warning", "danger")
MAX_DARK_HUE_DRIFT = 12.0


def mix_white(color: str, percent: float) -> str:
    """color-mix(in srgb, color, white percent%): the lifted surface of a dark elevation level."""
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * percent / 100) for c in rgb(color))


def dark_grounds(dark: dict, elevation: dict) -> dict[str, str]:
    """Every dark ground a text can sit on: the page, the surface, the navigation bar, the two tints and the surface lifted to levels 2–4."""
    mix = elevation.get("surfaceMix") or {}
    grounds = {name: dark[name] for name in ("canvas", "surface", "navBg", "actionTint", "accentTint")}
    for level in ("level2", "level3", "level4"):
        if isinstance(mix.get(level), (int, float)):
            grounds[f"surface+{mix[level]:g}%"] = mix_white(dark["surface"], mix[level])
    return grounds


def dark_rules(theme_id: str, t: dict, shared: dict) -> list[tuple[str, bool, str]]:
    """visual-design.html 深色与浅色两套主题: the dark mapping of one theme (themes.<id>.dark with shared.dark) judged rule by rule."""
    dark, sdark = t.get("dark"), shared.get("dark")
    if not dark or not sdark:
        return [("dark 映射存在", False, "missing themes.%s.dark or shared.dark" % theme_id)]
    missing = [f"dark.{k}" for k in DARK_THEME_KEYS if k not in dark] + [f"shared.dark.{k}" for k in DARK_SHARED_KEYS if k not in sdark]
    if missing:
        return [("dark 键齐全", False, "MISSING " + ", ".join(missing))]
    try:
        for value in [dark[k] for k in DARK_THEME_KEYS] + [sdark[k] for k in DARK_SHARED_KEYS if k != "elevation"]:
            normalize_hex(value)
    except ValueError as exc:
        return [("dark 取值是十六进制色", False, str(exc))]
    elevation = sdark["elevation"]
    grounds = dark_grounds(dark, elevation)
    text_grounds = {k: v for k, v in grounds.items() if k not in ("actionTint", "accentTint")}
    ink, ink2, ink3 = sdark["ink"], sdark["ink2"], sdark["ink3"]

    def worst(fg: str, backgrounds: dict[str, str]) -> tuple[float, str]:
        name = min(backgrounds, key=lambda k: contrast(fg, backgrounds[k]))
        return contrast(fg, backgrounds[name]), name

    def at_least(label: str, fg: str, backgrounds: dict[str, str], minimum: float) -> tuple[str, bool, str]:
        value, name = worst(fg, backgrounds)
        return (label, value >= minimum, f"{value:.2f}:1 on {name} (min {minimum:g})")

    rules: list[tuple[str, bool, str]] = [
        at_least("dark ink 在各层底上 >= 7", ink, grounds, 7.0),
        at_least("dark ink2 在各层底上 >= 4.5", ink2, text_grounds, 4.5),
        at_least("dark ink3 在各层底上 >= 4.5", ink3, text_grounds, 4.5),
        at_least("dark onAction 在 action 上 >= 4.5", dark["onAction"], {"action": dark["action"]}, 4.5),
        at_least("dark onAction 在 actionPress 上 >= 4.5", dark["onAction"], {"actionPress": dark["actionPress"]}, 4.5),
        at_least("dark action 对 canvas / surface >= 3", dark["action"], {k: grounds[k] for k in ("canvas", "surface")}, 3.0),
        at_least("dark actionText 在各层底上 >= 4.5", dark["actionText"], grounds, 4.5),
        at_least("dark accent 在各层底上 >= 4.5", dark["accent"], grounds, 4.5),
        at_least("dark line 在 surface 上有区分 >= 1.2", dark["line"], {"surface": dark["surface"]}, 1.2),
    ]
    for key, tint_key in DARK_STATUS:
        rules.append(at_least(f"dark {key} 在底与浮起面上 >= 4.5", sdark[key], text_grounds, 4.5))
        rules.append(at_least(f"dark {key} 在 {tint_key} 上 >= 4.5", sdark[key], {tint_key: sdark[tint_key]}, 4.5))
    for key in DARK_FILLED:
        rules.append(at_least(f"dark 白字在 {key}Fill 上 >= 4.5", "#FFFFFF", {f"{key}Fill": sdark[f"{key}Fill"]}, 4.5))
    rules.append(at_least("dark sage 在 sageTint 与 surface 上 >= 4.5", sdark["sage"], {"sageTint": sdark["sageTint"], "surface": dark["surface"]}, 4.5))
    # a second palette, not an inversion: the page is the darkest ground, grounds get lighter with height, the theme keeps its hue
    lum = {name: luminance(value) for name, value in grounds.items()}
    rules.append(("dark canvas 暗于 surface，且 canvas <= 0.02、surface <= 0.05", lum["canvas"] < lum["surface"] and lum["canvas"] <= 0.02 and lum["surface"] <= 0.05,
                  f"canvas {lum['canvas']:.4f} surface {lum['surface']:.4f}"))
    lifts = [grounds[k] for k in grounds if k.startswith("surface+")]
    rules.append(("dark 浮起的面逐级比底面更亮", bool(lifts) and all(luminance(a) < luminance(b) for a, b in zip([dark["surface"]] + lifts, lifts)),
                  " < ".join(f"{luminance(c):.4f}" for c in [dark["surface"]] + lifts)))
    chromatic = chroma(t["action"]) >= 20
    if chromatic:
        for name in ("canvas", "surface"):
            if chroma(dark[name]) >= 3:
                rules.append((f"dark {name} 与主色同色相 <= 30 度", hue_gap(dark[name], t["action"]) <= 30, f"{hue_gap(dark[name], t['action']):.0f} 度"))
        for name in ("action", "actionPress", "actionText"):
            rules.append((f"dark {name} 保持主色色相 <= {MAX_DARK_HUE_DRIFT:g} 度", hue_gap(dark[name], t["action"]) <= MAX_DARK_HUE_DRIFT,
                          f"{hue_gap(dark[name], t['action']):.0f} 度"))
    if chroma(t["accent"]) >= 20:
        rules.append((f"dark accent 保持辅色色相 <= {MAX_DARK_HUE_DRIFT:g} 度", hue_gap(dark["accent"], t["accent"]) <= MAX_DARK_HUE_DRIFT,
                      f"{hue_gap(dark['accent'], t['accent']):.0f} 度"))
    rules.append(("dark action 比浅色 action 亮或相同", luminance(dark["action"]) >= luminance(t["action"]) - 1e-9 or dark.get("onAction") != "#FFFFFF",
                  f"{luminance(dark['action']):.3f} vs {luminance(t['action']):.3f}"))
    for key, m in (dark.get("modules") or {}).items():
        if not all(m.get(k) for k in ("tint", "mid", "solid")):
            rules.append((f"dark module {key} tint/mid/solid", False, "missing"))
            continue
        rules.append(at_least(f"dark module {key} solid 在 tint / mid / surface 上 >= 4.5", m["solid"], {"tint": m["tint"], "mid": m["mid"], "surface": dark["surface"]}, 4.5))
        rules.append((f"dark module {key} tint 亮度 <= 0.08", luminance(m["tint"]) <= 0.08, f"{luminance(m['tint']):.3f}"))
    for light_key in (m for m in (t.get("modules") or {})):
        if light_key not in (dark.get("modules") or {}):
            rules.append((f"dark module {light_key} 存在", False, "light module has no dark module"))
    return rules


PAIR_LEVELS = (
    (4.5, "正文与按钮文字（WCAG 1.4.3 AA）"),
    (3.0, "大字、控件与图形（WCAG 1.4.3 大字、1.4.11）"),
    (7.0, "本规范的正文深色（WCAG 1.4.6 AAA）"),
)


def normalize_hex(color: str) -> str:
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", c):
        raise ValueError(f"not a hex colour: {color!r}")
    return "#" + c.upper()


def describe_pair(fg: str, bg: str) -> tuple[float, list[tuple[float, str, bool]]]:
    """Contrast of one colour pair and the verdict on each level; the ratio is compared unrounded."""
    ratio = contrast(normalize_hex(fg), normalize_hex(bg))
    return ratio, [(minimum, label, ratio >= minimum) for minimum, label in PAIR_LEVELS]


def pair_main(fg: str, bg: str) -> int:
    ratio, verdicts = describe_pair(fg, bg)
    # Shown cut, not rounded: 4.499 prints as 4.49 and does not pass 4.5.
    print(f"{normalize_hex(fg)} on {normalize_hex(bg)}  {int(ratio * 100) / 100:.2f}:1")
    for minimum, label, ok in verdicts:
        print(f"  {'PASS' if ok else 'FAIL'} >= {minimum:g}:1  {label}")
    return 0 if verdicts[0][2] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pair", nargs=2, metavar=("FG", "BG"), help="judge one pair of hex colours instead of the theme library")
    args = parser.parse_args(argv)
    if args.pair:
        try:
            return pair_main(*args.pair)
        except ValueError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            return 2
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
        rules += dark_rules(name, t, shared)
        for label, ok, note in rules:
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {note}")
    elevation = shared.get("elevation")
    if elevation is not None:
        print("shared.elevation")
        for label, ok, note in elevation_rules(elevation):
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {note}")
    dark_elevation = (shared.get("dark") or {}).get("elevation")
    print("shared.dark.elevation")
    if dark_elevation is None:
        failed = True
        print("  FAIL shared.dark.elevation       MISSING")
    else:
        for label, ok, note in elevation_rules(dark_elevation, dark=True):
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {note}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
