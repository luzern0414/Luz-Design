#!/usr/bin/env python3
"""Export one theme of references/themes.json as W3C design tokens (Design Tokens Format Module 2025.10).

  py -X utf8 scripts/export_tokens.py --list
  py -X utf8 scripts/export_tokens.py <theme> --out <文件>.tokens.json
  py -X utf8 scripts/export_tokens.py --application-themes [--themes <原库>]
  py -X utf8 scripts/export_tokens.py <theme> --surface reference --out <文档色库>.tokens.json
  py -X utf8 scripts/export_tokens.py --check <文件>.tokens.json [--require-dark]

Developers and Luz-Project take colours, type, spacing, radius, elevation and motion from this file instead of copying numbers
from the rule pages (visual-design.html 设计令牌). Colours and elevation come from themes.json; spacing, radius, the seven type
roles and the motion tokens are the values of the rule page, kept here as constants and pinned to the page by test_export_tokens.py.

Format facts (https://www.designtokens.org/tr/2025.10/format/ and /color/): file extension .tokens.json (or .tokens), media type
application/design-tokens+json; reserved properties $value, $type, $description; a colour is {colorSpace, components 0-1, alpha, hex};
a dimension is {value, unit px|rem}; a duration is {value, unit ms|s}; a cubic Bezier is [x1, y1, x2, y2]; a shadow is
{color, offsetX, offsetY, blur, spread, inset}; a typography token is {fontFamily, fontSize, fontWeight, letterSpacing, lineHeight}
with lineHeight a multiplier of fontSize; a reference is "{group.token}"; a name never starts with $ and never holds { } or a dot.
--check validates these facts on any tokens file.

Reference palettes only (--surface reference): $value is always the light value, and the dark value of the same token sits in
``$extensions.mode.dark`` in the shape the token's $type takes (a colour object, or a shadow list for the shadow levels). DTCG 2025.10 does not define
light and dark modes and keeps ``$extensions`` for vendor data, so the dark value sits under the vendor key ``mode``; one file then feeds a CSS
``prefers-color-scheme`` build as well as a design tool. The document root declares ``$extensions["design.luz"].modes`` (light first).
--check then also requires the dark value on every colour token of ``color`` (the ten-step ``scale`` is light-only) and on every ``shadow`` level, and
validates each dark value like a light one; ``--require-dark`` asks for that on a file that does not declare its modes, ``--light-only`` exports without them.
"""
from __future__ import annotations

import argparse
import colorsys
from functools import lru_cache
import json
import re
import sys
from pathlib import Path

import check_contrast
import stage_ramp

THEMES = Path(__file__).resolve().parents[1] / "references" / "themes.json"
FORMAT_VERSION = "2025.10"
MEDIA_TYPE = "application/design-tokens+json"

# visual-design.html 间距与栅格、圆角、字阶与七级字体角色、动效细则: the values below are the rule page's.
SPACING = (4, 8, 12, 16, 20, 24, 32, 48, 64, 96)
RADIUS = {"tag": 4, "control": 8, "card": 12, "panel": 16}
FONT_STACK = ["PingFang SC", "Microsoft YaHei", "Noto Sans SC", "system-ui", "sans-serif"]
WEIGHTS = {"regular": 400, "semibold": 600, "bold": 700}
# role: (font size, line height in px, weight name, description)
TYPE_ROLES = {
    "number": (32, 40, "bold", "大号数字：指标卡与品牌主卡的核心数字、价格、计时，等宽数字"),
    "number-compact": (28, 36, "bold", "并排四张以上指标卡的数字"),
    "page-title": (22, 30, "bold", "页面主标题、空状态与结果页标题"),
    "section-title": (18, 26, "semibold", "区块标题、对象名、对话框标题"),
    "card-title": (16, 24, "semibold", "卡片头、列表项标题、指标名、底部弹层标题"),
    "body": (14, 22, "regular", "正文、表格、表单、按钮文字"),
    "secondary": (14, 22, "regular", "副标题、属性、第二行、来源与时间说明，颜色用次要灰"),
    "caption": (12, 18, "regular", "时间戳、单位、角标、坐标、注释"),
}
DURATIONS = {
    "instant": (100, "按下、焦点环、复选、悬停的颜色变化"),
    "fast": (150, "图标交叉淡化、二态按钮、卡片悬停与回弹、提示出现"),
    "base": (200, "开关与分段控件滑块、标签页下划线、列表项进入与退出"),
    "slow": (250, "卡片展开、面板与抽屉打开、模块显隐；范围 250 到 300，按面积取"),
    "page": (300, "二级页推入与返回，范围 280 到 320"),
}
EASINGS = {
    "standard": ([0.2, 0, 0, 1], "屏幕内的移动、尺寸变化、滑块"),
    "enter": ([0, 0, 0, 1], "元素出现、展开、淡入（减速）"),
    "exit": ([0.3, 0, 1, 1], "元素离开、收起、淡出（加速）"),
}
SHADOW_LEVELS = ("level1", "level2", "level3", "level4")
NAME_BAD = re.compile(r"[{}.]")
TYPES = {"color", "dimension", "duration", "fontFamily", "fontWeight", "cubicBezier", "number", "shadow", "typography",
         "border", "transition", "strokeStyle", "gradient"}
SHARED_COLORS = {
    "text": (("ink", "ink"), ("secondary", "ink2"), ("tertiary", "ink3")),
    "status": (("success", "success"), ("success-tint", "successTint"), ("warning", "warning"), ("warning-tint", "warningTint"),
               ("danger", "danger"), ("danger-tint", "dangerTint"), ("info", "info"), ("info-tint", "infoTint"),
               ("price", "price"), ("price-tint", "priceTint"),
               # on a dark ground a status text colour is light, so a solid fill that carries white text is its own, darker value (light: the same colour)
               ("success-fill", "success", "successFill"), ("warning-fill", "warning", "warningFill"), ("danger-fill", "danger", "dangerFill")),
}


def to_color(value: str, alpha: float | None = None) -> dict:
    rgb = check_contrast.rgb(value)
    out = {"colorSpace": "srgb", "components": [round(c / 255, 6) for c in rgb]}
    if alpha is not None and alpha < 1:
        out["alpha"] = round(alpha, 4)
    out["hex"] = "#%02x%02x%02x" % rgb
    return out


def token(value, type_: str | None = None, description: str | None = None, dark=None) -> dict:
    out: dict = {}
    if type_:
        out["$type"] = type_
    out["$value"] = value
    if description:
        out["$description"] = description
    if dark is not None:
        out["$extensions"] = {"mode": {"dark": dark}}
    return out


def px(value: float) -> dict:
    return {"value": int(value) if float(value).is_integer() else value, "unit": "px"}


def shadow_value(css: str) -> list[dict]:
    layers = check_contrast.shadow_layers(css)
    return [{"color": to_color(layer["colour"], layer["alpha"]), "offsetX": px(layer["x"]), "offsetY": px(layer["y"]),
             "blur": px(layer["blur"]), "spread": px(layer["spread"]), "inset": layer["inset"]} for layer in layers]


def line_alpha(css: str) -> tuple[str, float]:
    layers = check_contrast.shadow_layers(f"0 0 0 {css}")
    return layers[0]["colour"], layers[0]["alpha"]


def load_themes() -> dict:
    return json.loads(THEMES.read_text(encoding="utf-8"))


@lru_cache(maxsize=1024)
def application_color(value: str) -> str:
    """Replace green/teal interface paint with a blue of comparable relative luminance."""
    rgb = check_contrast.rgb(value)
    hue, _, saturation = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    if max(rgb) - min(rgb) < 3 or not 65 <= hue * 360 <= 185:
        return value
    target = check_contrast.luminance(value)
    low, high = 0.0, 1.0
    for _ in range(13):
        lightness = (low + high) / 2
        result = "#%02X%02X%02X" % tuple(round(c * 255) for c in colorsys.hls_to_rgb(218 / 360, lightness, saturation))
        if check_contrast.luminance(result) < target:
            low = lightness
        else:
            high = lightness
    return result


def _application_values(value):
    if isinstance(value, dict):
        return {key: _application_values(child) for key, child in value.items() if key != "dark"}
    if isinstance(value, list):
        return [_application_values(item) for item in value]
    if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return application_color(value)
    if isinstance(value, str) and "rgb" in value:
        def paint(match):
            channels = tuple(int(match[i]) for i in range(2,5))
            if max(channels)>255:
                return match[0]
            original = "#%02X%02X%02X" % channels
            adjusted = application_color(original)
            if adjusted == original:
                return match[0]
            return match[1] + "(" + ", ".join(str(c) for c in check_contrast.rgb(adjusted)) + (match[5] or "") + ")"
        return re.sub(r"\b(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(\s*,\s*[.\d]+)?\s*\)",paint,value)
    return value


def application_themes(data: dict | None = None) -> dict:
    """Return a white, green-free product palette with the source schema and IDs."""
    result = _application_values(data if data is not None else load_themes())
    result["note"] = "应用主题。页面与导航恒为纯白。界面色值均来自当前应用档。"
    result["shared"].update(surface="#FFFFFF", success="#28599B", successTint="#E8EFFA")
    for theme in result["themes"].values():
        theme.pop("source", None)  # Source prose describes the unmodified document palette.
        theme.update(canvas="#FFFFFF", navBg="#FFFFFF")
    return result


def application_theme(theme_id: str, data: dict | None = None) -> dict:
    return application_themes(data)["themes"][theme_id]


def build(theme_id: str, data: dict | None = None, *, with_dark: bool = True, surface: str = "application") -> dict:
    data = data or load_themes()
    if surface == "application":
        data = application_themes(data)
    elif surface != "reference":
        raise ValueError(f"Unknown surface {surface!r}")
    if theme_id not in data["themes"]:
        raise KeyError(f"unknown theme {theme_id!r}; themes: {', '.join(data['themes'])}")
    theme, shared = data["themes"][theme_id], data["shared"]
    elevation = shared["elevation"]
    dk, sd = (theme.get("dark"), shared.get("dark")) if with_dark else (None, None)
    if not (dk and sd):
        dk = sd = None
    delev = sd["elevation"] if sd else None

    def dark_color(source: dict | None, key: str):
        """The dark value of a colour token, or None when the file carries the light mode only."""
        return to_color(source[key]) if source else None

    def dark_line(name: str):
        return to_color(*line_alpha(delev[name])) if delev else None

    def lifted(level: str):
        return to_color(check_contrast.mix_white(dk["surface"], delev["surfaceMix"][level])) if dk else None

    brand = {"action": token(to_color(theme["action"]), None, "品牌阶：主按钮、开关、品牌主卡；浅色里白字达 4.5:1，深色里 on-action 文字达 4.5:1", dark_color(dk, "action")),
             "action-press": token(to_color(theme["actionPress"]), None, "按下阶：按下态", dark_color(dk, "actionPress")),
             "on-action": token(to_color(shared["surface"]), None, "品牌阶与按下阶上的文字色：浅色是白色；深色里多数主题仍是白色，中性的石墨主题是深色", dark_color(dk, "onAction")),
             "action-text": token(to_color(theme["actionPress"]), None, "品牌色文字与图标（链接、选中的标签与菜单文字）：浅色取按压阶，深色取更亮一阶，在各层深色底与浅底上不低于 4.5:1", dark_color(dk, "actionText")),
             "action-tint": token(to_color(theme["actionTint"]), None, "第 1 阶浅底：图标块、选中项、头部；深色里是深而低饱和的同色相底", dark_color(dk, "actionTint")),
             "accent": token(to_color(theme["accent"]), None, "营销辅色", dark_color(dk, "accent")),
             "accent-tint": token(to_color(theme["accentTint"]), None, "营销辅色浅底", dark_color(dk, "accentTint"))}
    surfaces = {"canvas": token(to_color(theme["canvas"]), None, "页面底色；浅色里卡片仍为纯白，深色里页面底是最暗的一层", dark_color(dk, "canvas")),
               "card": token(to_color(shared["surface"]), None, "卡片白底（层级 1）；深色里是比页面底更亮的卡片面", dark_color(dk, "surface")),
               "raised-2": token(to_color(shared["surface"]), None, "悬浮卡片（层级 2）；浅色同卡片白底，深色里再亮一阶", lifted("level2") if dk else None),
               "raised-3": token(to_color(shared["surface"]), None, "下拉、提示与吸顶栏（层级 3）；深色里更亮", lifted("level3") if dk else None),
               "raised-4": token(to_color(shared["surface"]), None, "对话框、底部弹层与抽屉（层级 4）；深色里最亮", lifted("level4") if dk else None),
               "nav": token(to_color(theme["navBg"]), None, "导航栏底色，只放正文色的文字与图标", dark_color(dk, "navBg"))}
    color: dict = {"$type": "color", "brand": brand, "surface": surfaces}
    for group, items in SHARED_COLORS.items():
        color[group] = {item[0]: token(to_color(shared[item[1]]), None, None, dark_color(sd, item[2] if len(item) > 2 else item[1]))
                        for item in items}
    color["line"] = {"divider": token(to_color(shared["line"]), None, "静止的分隔与描边；深色取该主题的 dark.line", dark_color(dk, "line")),
                     "hairline": token(to_color(*line_alpha(elevation["hairline"])), None, "卡片边、表格横线、列表分隔；深色里是白色发丝线", dark_line("hairline")),
                     "hairline-strong": token(to_color(*line_alpha(elevation["hairlineStrong"])), None, "可点击卡片悬停时的边线", dark_line("hairlineStrong")),
                     "scrim": token(to_color(*line_alpha(elevation["scrim"])), None, "对话框与抽屉的遮罩", dark_line("scrim"))}
    if theme.get("scale"):
        color["scale"] = {str(i + 1): token(to_color(value), None, "主色整列 10 阶，阶数从最浅的第 1 阶数起；只有浅色") if i == 0
                          else token(to_color(value)) for i, value in enumerate(theme["scale"])}
    dark_modules = (dk or {}).get("modules") or {}
    modules = {key: {part: token(to_color(m[part]), None, None, to_color(dark_modules[key][part]) if key in dark_modules else None)
                     for part in ("tint", "mid", "solid")}
               for key, m in (theme.get("modules") or {}).items()}
    if modules:
        color["module"] = modules
    stage = theme.get("stage")
    if stage:
        # 有序进度状态的色阶（visual-design.html 有序进度状态的色阶）：6 级文字色，深色另有一套；浅底标签是本色混入卡片面（浅色 10%，深色 16%）
        def tint(value):
            mixed = stage_ramp.tint_of(value, "light", shared["surface"])
            return application_color(mixed) if surface == "application" else mixed
        sd_surface = dk["surface"] if dk else None
        color["stage"] = {str(i + 1): token(to_color(stage["light"][i]), None,
                                            "有序进度状态的色阶 stage-1 到 stage-6：同一页面里有先后顺序的状态集合，文字按顺序位置取色，越靠后越深越实（浅色）或越亮越醒目（深色）；"
                                            "N 个状态取其中等间隔的 N 级（stage_ramp.py positions）；必须同时写出文字标签；与成功、警告、危险状态色是两套，终态的成交与流失用状态色" if i == 0 else None,
                                            to_color(stage["dark"][i]) if dk else None) for i in range(stage_ramp.STOPS)}
        color["stage-tint"] = {str(i + 1): token(to_color(tint(stage["light"][i])),
                                                 None, "色阶某一级的浅底标签底色（本色混入卡片面：浅色 10%，深色 16%），文字用同级 stage 色，对比度不低于 4.5:1；主题 avoid 禁止彩色底块时不用" if i == 0 else None,
                                                 to_color(stage_ramp.tint_of(stage["dark"][i], "dark", sd_surface)) if dk else None) for i in range(stage_ramp.STOPS)}

    typography = {"$type": "typography"}
    for role, (size, line, weight, description) in TYPE_ROLES.items():
        typography[role] = token({"fontFamily": "{font.family.base}", "fontSize": px(size), "fontWeight": f"{{font.weight.{weight}}}",
                                  "letterSpacing": px(0), "lineHeight": line / size}, None, description)

    doc = {
        "$description": f"Luz Design 令牌：{theme['label']}（{theme_id}），主题库版本 {data['version']}；格式 Design Tokens Format Module {FORMAT_VERSION}"
                        + ("；浅色与深色两套，$value 是浅色，深色在 $extensions.mode.dark" if dk else ""),
        **({"$extensions": {"design.luz": {"modes": ["light", "dark"], "default": "light", "darkValue": "$extensions.mode.dark"}}} if dk else {}),
        "color": color,
        "space": {"$type": "dimension", **{str(v): token(px(v)) for v in SPACING}},
        "radius": {"$type": "dimension", **{name: token(px(v)) for name, v in RADIUS.items()}, "full": token(px(9999), None, "头像、开关、胶囊分段")},
        "font": {"family": {"$type": "fontFamily", "base": token(FONT_STACK, None, "全站唯一字体栈；文件里用微软雅黑")},
                 "weight": {"$type": "fontWeight", **{name: token(v) for name, v in WEIGHTS.items()}}},
        "typography": typography,
        "shadow": {"$type": "shadow", **{f"level-{i + 1}": token(shadow_value(elevation[name]),
                                                                  dark=shadow_value(sd["elevation"][name]) if dk else None)
                                          for i, name in enumerate(SHADOW_LEVELS)}},
        "duration": {"$type": "duration", **{name: token({"value": ms, "unit": "ms"}, None, d) for name, (ms, d) in DURATIONS.items()}},
        "easing": {"$type": "cubicBezier", **{name: token(curve, None, d) for name, (curve, d) in EASINGS.items()}},
    }
    if surface == "application":
        for key in ("canvas","nav"):
            doc["color"]["surface"][key]["$description"] = "全局纯白界面"
        doc["color"]["surface"]["raised-4"]["$description"] = "通知与警告"
        doc["$description"] += "；应用界面，白色画布与导航"
    return doc


def walk(node: dict, path: tuple[str, ...] = (), inherited: str | None = None):
    """Yield (path, token, effective type) for every token of a tokens document."""
    group_type = node.get("$type") or inherited
    for name, child in node.items():
        if name.startswith("$"):
            continue
        if isinstance(child, dict) and "$value" in child:
            yield path + (name,), child, child.get("$type", group_type)
        elif isinstance(child, dict):
            yield from walk(child, path + (name,), group_type)


def resolve(doc: dict, reference: str):
    node = doc
    for part in reference.strip("{}").split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, dict) and "$value" in node else None


def references(value):
    """Every "{group.token}" reference inside a token value, composite fields included."""
    if isinstance(value, str):
        if value.startswith("{") and value.endswith("}"):
            yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def check_color(value, where: str, errors: list[str]) -> None:
    if not isinstance(value, dict) or value.get("colorSpace") != "srgb":
        errors.append(f"{where}: colour needs colorSpace srgb")
        return
    components = value.get("components")
    if not (isinstance(components, list) and len(components) == 3 and all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in components)):
        errors.append(f"{where}: srgb components are three numbers from 0 to 1")
    if "alpha" in value and not (isinstance(value["alpha"], (int, float)) and 0 <= value["alpha"] <= 1):
        errors.append(f"{where}: alpha is a number from 0 to 1")
    if "hex" in value:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(value["hex"])):
            errors.append(f"{where}: hex is 6-digit CSS hex")
        elif isinstance(components, list) and len(components) == 3:
            expected = "#%02x%02x%02x" % tuple(round(c * 255) for c in components)
            if expected != value["hex"].lower():
                errors.append(f"{where}: hex {value['hex']} does not match components {expected}")


def check_dimension(value, where: str, errors: list[str], units=("px", "rem")) -> None:
    if not (isinstance(value, dict) and isinstance(value.get("value"), (int, float)) and value.get("unit") in units):
        errors.append(f"{where}: needs {{value, unit}} with unit {'/'.join(units)}")


def declared_modes(doc: dict) -> list[str]:
    ext = doc.get("$extensions")
    modes = ext.get("design.luz", {}).get("modes") if isinstance(ext, dict) and isinstance(ext.get("design.luz"), dict) else None
    return [m for m in modes if isinstance(m, str)] if isinstance(modes, list) else []


def check_tokens(doc: dict, require_dark: bool | None = None) -> list[str]:
    """Structural check of the facts listed in the module docstring; the dark value is required on colour and shadow tokens when the file declares
    the dark mode (``$extensions["design.luz"].modes``) or ``require_dark`` is True."""
    errors: list[str] = []
    need_dark = require_dark if require_dark is not None else "dark" in declared_modes(doc)

    def names(node: dict, path: tuple[str, ...]) -> None:
        for name, child in node.items():
            if name.startswith("$"):
                continue
            if NAME_BAD.search(name):
                errors.append(f"{'.'.join(path + (name,))}: a name never holds {{ }} or a dot")
            if isinstance(child, dict) and "$value" not in child:
                names(child, path + (name,))

    def check_value(value, type_, where: str) -> None:
        for reference in references(value):
            if resolve(doc, reference) is None:
                errors.append(f"{where}: reference {reference} does not resolve")
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            return
        if type_ not in TYPES:
            errors.append(f"{where}: unknown or missing $type {type_!r}")
        elif type_ == "color":
            check_color(value, where, errors)
        elif type_ == "dimension":
            check_dimension(value, where, errors)
        elif type_ == "duration":
            check_dimension(value, where, errors, units=("ms", "s"))
        elif type_ == "cubicBezier":
            if not (isinstance(value, list) and len(value) == 4 and all(isinstance(v, (int, float)) for v in value)
                    and 0 <= value[0] <= 1 and 0 <= value[2] <= 1):
                errors.append(f"{where}: four numbers, x values from 0 to 1")
        elif type_ == "fontWeight":
            if not (isinstance(value, (int, float)) and 1 <= value <= 1000):
                errors.append(f"{where}: weight from 1 to 1000")
        elif type_ == "fontFamily":
            if not (isinstance(value, str) or (isinstance(value, list) and value and all(isinstance(v, str) for v in value))):
                errors.append(f"{where}: a name or a list of names")
        elif type_ == "shadow":
            layers = value if isinstance(value, list) else [value]
            for index, layer in enumerate(layers):
                if not isinstance(layer, dict) or not {"color", "offsetX", "offsetY", "blur", "spread"} <= set(layer):
                    errors.append(f"{where}[{index}]: shadow needs color, offsetX, offsetY, blur, spread")
                    continue
                check_color(layer["color"], f"{where}[{index}].color", errors)
                for key in ("offsetX", "offsetY", "blur", "spread"):
                    check_dimension(layer[key], f"{where}[{index}].{key}", errors)
        elif type_ == "typography":
            needed = {"fontFamily", "fontSize", "fontWeight", "letterSpacing", "lineHeight"}
            if not isinstance(value, dict) or not needed <= set(value):
                errors.append(f"{where}: typography needs {', '.join(sorted(needed))}")
            elif not isinstance(value["lineHeight"], (int, float)):
                errors.append(f"{where}: lineHeight is a multiplier of the font size")

    names(doc, ())
    for path, tok, type_ in walk(doc):
        where = ".".join(path)
        check_value(tok["$value"], type_, where)
        modes = (tok.get("$extensions") or {}).get("mode")
        if modes is not None and not isinstance(modes, dict):
            errors.append(f"{where}: $extensions.mode is an object of mode name to value")
            modes = None
        for mode_name, mode_value in (modes or {}).items():
            check_value(mode_value, type_, f"{where} [{mode_name}]")
        # the ten-step scale is a light-only ramp; every other colour and every shadow level has a dark value
        wants_dark = need_dark and ((path[0] == "color" and path[1] != "scale" and type_ == "color") or (path[0] == "shadow" and type_ == "shadow"))
        if wants_dark and "dark" not in (modes or {}):
            errors.append(f"{where}: no dark value ($extensions.mode.dark); the file declares light and dark")
    errors += check_stage(doc)
    return errors


def check_stage(doc: dict) -> list[str]:
    """``color.stage``（有序进度状态的色阶）：6 级，每一级对文件里的各层底和自己的浅底标签不低于 4.5:1，相邻两级色差、彩度与明度走向合格；浅色和深色各查一遍。"""
    group = (doc.get("color") or {}).get("stage")
    if group is None:
        return []
    errors: list[str] = []
    items = {k: v for k, v in group.items() if not k.startswith("$")}
    if sorted(items) != [str(i) for i in range(1, stage_ramp.STOPS + 1)]:
        return [f"color.stage: 需要 1 到 {stage_ramp.STOPS} 共 {stage_ramp.STOPS} 级，现在是 {', '.join(sorted(items))}"]
    surface = (doc.get("color") or {}).get("surface") or {}
    for mode in ("light", "dark"):
        def pick(tok):
            if mode == "light":
                return tok.get("$value")
            return ((tok.get("$extensions") or {}).get("mode") or {}).get("dark")
        colours, bad = [], False
        for i in range(1, stage_ramp.STOPS + 1):
            value = pick(items[str(i)])
            if not isinstance(value, dict) or "hex" not in value:
                if mode == "dark" and value is None:
                    bad = True      # 缺深色值已由通用检查报告
                    break
                errors.append(f"color.stage.{i} [{mode}]: needs a colour with hex")
                bad = True
                break
            colours.append(value["hex"])
        if bad:
            continue
        names = ("canvas", "card") if mode == "light" else ("canvas", "card", "raised-2", "raised-3", "raised-4", "nav")
        grounds = []
        for name in names:
            tok = surface.get(name)
            value = pick(tok) if isinstance(tok, dict) else None
            if isinstance(value, dict) and "hex" in value:
                grounds.append(value["hex"])
        if not grounds:
            errors.append(f"color.stage [{mode}]: 文件里没有可对照的底色（color.surface）")
            continue
        card = pick(surface.get("card", {})) if isinstance(surface.get("card"), dict) else None
        tint_surface = card["hex"] if isinstance(card, dict) and "hex" in card else grounds[0]
        for label, ok, note in stage_ramp.check(colours, grounds, mode, tint_surface=tint_surface, label=f"color.stage [{mode}]"):
            if not ok:
                errors.append(f"{label}: {note}")
    return errors


def application_token_errors(doc: dict) -> list[str]:
    errors = []
    for name in ("canvas", "nav"):
        value = resolve(doc, "{color.surface." + name + "}")
        if not value or not isinstance(value["$value"], dict) or value["$value"].get("hex", "").upper() != "#FFFFFF":
            errors.append(f"color.surface.{name}: 应用画布与导航应为纯白")
    if "dark" in declared_modes(doc):
        errors.append("应用主题应在不同系统外观下保持白色")
    def validate_paint(value, where):
        if isinstance(value, dict):
            if value.get("colorSpace") == "srgb":
                paint = value.get("hex") or "#%02X%02X%02X" % tuple(round(255*c) for c in value["components"])
                if application_color(paint).upper() != paint.upper():
                    errors.append(f"{where}: 应用令牌含绿色或青绿色 {paint}")
            else:
                for child in value.values():
                    validate_paint(child, where)
        elif isinstance(value, list):
            for child in value:
                validate_paint(child, where)
    for path, value, _ in walk(doc):
        validate_paint(value, ".".join(path))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("theme", nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--surface", choices=("application","reference"), default="application", help="应用界面默认使用纯白与禁绿规则；reference 导出文档色库")
    parser.add_argument("--themes", type=Path, help="可选同结构的原始主题库")
    parser.add_argument("--application-themes", action="store_true", help="输出应用专用的 shared/themes JSON，供系统生成器使用")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--light-only", action="store_true", help="export light values only for a reference palette")
    parser.add_argument("--with-dark", action="store_true", help=argparse.SUPPRESS)   # retained for reference palettes
    parser.add_argument("--check", type=Path, help="validate a tokens file")
    parser.add_argument("--require-dark", action="store_true", help="with --check: demand a dark value on every colour and shadow token even if the file does not declare its modes")
    args = parser.parse_args(argv)
    if args.check:
        document = json.loads(args.check.read_text(encoding="utf-8"))
        errors = check_tokens(document, True if args.require_dark else None)
        if args.surface == "application" and not errors:
            errors.extend(application_token_errors(document))
        print(f"{'FAIL' if errors else 'PASS'}: {args.check} ({len(errors)} error(s))")
        for item in errors:
            print("  ERROR", item)
        return 1 if errors else 0
    data = json.loads(args.themes.read_text(encoding="utf-8")) if args.themes else load_themes()
    if args.application_themes:
        print(json.dumps(application_themes(data),ensure_ascii=False))
        return 0
    if args.list or not args.theme:
        for key, theme in (application_themes(data) if args.surface=="application" else data)["themes"].items():
            print(f"{key}\t{theme['label']}\t{theme['action']}")
        return 0
    try:
        doc = build(args.theme, data, with_dark=not args.light_only,surface=args.surface)
    except KeyError as exc:
        print(f"ERROR {exc.args[0]}", file=sys.stderr)
        return 2
    errors = check_tokens(doc)
    if args.surface == "application" and not errors:
        errors.extend(application_token_errors(doc))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        if not args.out.name.endswith((".tokens.json", ".tokens")):
            print(f"ERROR the file name ends in .tokens.json or .tokens: {args.out.name}", file=sys.stderr)
            return 2
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({MEDIA_TYPE}, {sum(1 for _ in walk(doc))} tokens)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
