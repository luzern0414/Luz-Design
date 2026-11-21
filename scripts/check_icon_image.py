#!/usr/bin/env python3
"""生成图标的颜色检查：饱和度不过深，主色相不超过两个。只管图标，商品与门店这类配图不检查。

    py -X utf8 scripts/check_icon_image.py <图标.png|webp|jpg|svg | 目录> [更多路径] [--max-mean 0.45] [--p90 0.65]
        [--hot-share 3%] [--hot-s 0.80] [--max-hues 2] [--alpha-min 128] [--kind auto|block|control]
        [--theme <主题 id>] [--dark [--light <浅色版>]] [-r] [--json] [--quiet]
    py -X utf8 scripts/check_icon_image.py --palette <主题 id>      打印这个主题的图标色板（浅色与深色），写进提示词用

度量（本技能取值，待样板图校准；规则见 references/image-assets.md）：
    饱和度用 HSB（HSV）的 S，0 到 1，设计师在取色器里说的饱和度就是它。
    位图：只统计不透明（透明度不低于 --alpha-min）、非近白（V 不低于 0.97 且 S 不高于 0.05）、非近黑（V 不高于 0.12）的像素，按面积加权。
    指标四个：均值 S、第 90 百分位 S（最近秩）、S 大于 --hot-s 的像素占比、主色相个数（S 不低于 0.15 的像素按 10 度分箱，
    一个峰值正负 20 度内的并为同一色相，占彩色像素不足 5% 的不计）。
    默认上限：均值 0.45；P90 0.65；占比 3%；色相 2 个。任何一项超限即退出码 1。
    拼板（4x4 的元素图）里是十几个不同的物体，色相个数没有意义：先用 cut_element_sheet.py 切开，再逐个检查。
SVG：取 fill、stroke、stop-color 的颜色（含内联样式和 style 块），描边按 0.3 的面积权重近似。颜色不超过一个且只用作描边的是线性控件图标，
    不看饱和度，只看是不是令牌色（要 --theme，令牌来自 references/themes.json；建议用 currentColor）；其余是色块图标，
    令牌色不计饱和度（视觉规范的双色入口图标描边取按下阶），令牌以外的自造色按上面的阈值判；没给 --theme 时全部颜色都判。
深色：--dark 把输入当作深色版。深色底色的 S 天生偏高（深红底 V 0.25 时 S 也可到 0.55），所以深色版的度量改用彩度 C = V x S，
    四个上限用同一组数字。--light 给浅色版；目录里 名称-dark.png、名称_dark.png、名称.dark.png 自动对应 名称.png。
    深色版的 P90（图形色）比浅色版（同样按 C）高出容差 0.03 就提示“深色版更饱和”，同样退出码 1。均值不比：深色底块（dark.actionTint）本身是一整块
    深而有色的令牌，会把均值拉高，而刺眼的是图形色。
numpy 可有可无：没有时用 Pillow 的 HSV 转换加纯 Python 统计，结果相同。
退出码：0 通过；1 有图标超限；2 输入有误（路径、主题、图像打不开）。
通过打印 `check icon image: ok`；不通过列出指标和超限的那一条。
"""
from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:  # 可选加速
    import numpy as np
except Exception:  # pragma: no cover - 没装 numpy 时走纯 Python
    np = None

try:
    from PIL import Image, ImageColor
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"需要 Pillow：{exc}")

ROOT = Path(__file__).resolve().parent.parent
THEMES_PATH = ROOT / "references" / "themes.json"

# 本技能取值，待样板图校准。改这里或用命令行参数覆盖。
DEFAULTS = {
    "max_mean": 0.45,      # 均值 S 上限
    "p90": 0.65,           # 第 90 百分位 S 上限
    "hot_s": 0.80,         # 高饱和像素的 S 下限（S 大于它算“高饱和”）
    "hot_share": 0.03,     # 高饱和像素占比上限
    "max_hues": 2,         # 主色相个数上限（不含中性色）
    "alpha_min": 128,      # 透明度不低于它才算不透明
}
WHITE_V, WHITE_S = 0.97, 0.05      # 近白：V 不低于、S 不高于
BLACK_V = 0.12                     # 近黑：V 不高于
CHROMA_S = 0.15                    # 度量值不低于它才参与色相统计
HUE_BIN = 10                       # 色相分箱（度）
HUE_MERGE_BINS = 2                 # 峰值正负 2 箱（20 度）并为同一色相
HUE_MIN_SHARE = 0.05               # 占彩色像素不足 5% 的色相不计
SIDE_LIMIT = 512                   # 位图最长边超过它先用最近邻缩小（不产生新颜色）
STROKE_WEIGHT = 0.3                # SVG 描边相对填充的面积权重（近似）
DARK_P90_TOL = 0.03
IMAGE_EXTS = {".png", ".webp", ".jpg", ".jpeg", ".gif", ".bmp"}
DARK_SUFFIX = re.compile(r"^(?P<base>.+?)(?:[-_.]dark)$", re.I)
# 图标色板的推导（本技能取值）：色相取品牌阶的色相，(S, V)；S 不超过品牌阶自己的 S；线稿的 V 从这里往下取到对底块 3:1
PALETTE_SV = {"次层": (0.28, 0.98), "图形": (0.58, 0.88), "线稿": (0.62, 0.60)}


# ---------------------------------------------------------------- 结果

@dataclass
class Metrics:
    mean: float = 0.0
    p90: float = 0.0
    hot_share: float = 0.0
    hues: list[tuple[int, float]] = field(default_factory=list)   # (峰值色相度数, 占彩色像素比例)
    counted: float = 0.0          # 参与统计的权重（位图是像素数）
    total: float = 0.0            # 全部权重
    note: str = ""


@dataclass
class Report:
    path: str
    kind: str                     # block / control
    fmt: str                      # raster / svg
    size: str = ""
    measure: str = "S"            # S 饱和度；深色版用 C 彩度
    metrics: Metrics = field(default_factory=Metrics)
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    dark_of: str = ""

    @property
    def ok(self) -> bool:
        return not self.problems


# ---------------------------------------------------------------- 度量

def hsv_of(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """(h 度数, s, v)，s、v 为 0 到 1。"""
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return h * 360, s, v


def is_near_white(s: float, v: float) -> bool:
    return v >= WHITE_V and s <= WHITE_S


def is_near_black(v: float) -> bool:
    return v <= BLACK_V


def measure_value(s: float, v: float, measure: str) -> float:
    return s * v if measure == "C" else s


def hue_families(hist: list[float]) -> list[tuple[int, float]]:
    """把 36 箱色相直方图归并成色相家族：最大的箱做峰值，正负 HUE_MERGE_BINS 箱内的并入，重复到没有剩余。
    返回 [(峰值度数, 占比)]，占比不足 HUE_MIN_SHARE 的丢掉。不沿链条合并，所以一道彩虹不会被并成一个色相。"""
    total = sum(hist)
    if total <= 0:
        return []
    left = list(hist)
    n = len(left)
    families: list[tuple[int, float]] = []
    while True:
        peak = max(range(n), key=lambda i: left[i])
        if left[peak] <= 0:
            break
        share = 0.0
        for d in range(-HUE_MERGE_BINS, HUE_MERGE_BINS + 1):
            j = (peak + d) % n
            share += left[j]
            left[j] = 0.0
        if share / total >= HUE_MIN_SHARE:
            families.append((peak * HUE_BIN + HUE_BIN // 2, share / total))
    return families


NEUTRAL_NOTE = "没有可统计的像素（全透明、近白或近黑）：中性色图标，不涉及饱和度"


def metrics_from_samples(samples: list[tuple[float, float, float]], hot_s: float = DEFAULTS["hot_s"]) -> Metrics:
    """samples：[(色相度数, 度量值, 权重)]，已经去掉了透明、近白、近黑；度量值是 S（深色版是 C）。"""
    total = sum(w for _, _, w in samples)
    if total <= 0:
        return Metrics(note=NEUTRAL_NOTE)
    ordered = sorted(samples, key=lambda t: t[1])
    mean = sum(s * w for _, s, w in samples) / total
    cum, p90 = 0.0, ordered[-1][1]
    for _, s, w in ordered:
        cum += w
        if cum >= 0.9 * total:
            p90 = s
            break
    hot = sum(w for _, s, w in samples if s > hot_s) / total
    hist = [0.0] * (360 // HUE_BIN)
    for h, s, w in samples:
        if s >= CHROMA_S:
            hist[int(h // HUE_BIN) % len(hist)] += w
    return Metrics(mean=mean, p90=p90, hot_share=hot, hues=hue_families(hist), counted=total, total=total)


def analyze_image(img: Image.Image, alpha_min: int = DEFAULTS["alpha_min"], hot_s: float = DEFAULTS["hot_s"],
                  use_numpy: bool = True, measure: str = "S") -> Metrics:
    """位图的四个指标。透明、近白、近黑像素不计，其余按面积加权（每个像素一份）。"""
    if max(img.size) > SIDE_LIMIT:
        k = SIDE_LIMIT / max(img.size)
        img = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), Image.NEAREST)
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    h_b, s_b, v_b = rgba.convert("RGB").convert("HSV").split()
    total = rgba.width * rgba.height
    if use_numpy and np is not None:
        a = np.frombuffer(alpha.tobytes(), dtype=np.uint8)
        h = np.frombuffer(h_b.tobytes(), dtype=np.uint8).astype(np.float64) * 360 / 255
        s = np.frombuffer(s_b.tobytes(), dtype=np.uint8).astype(np.float64) / 255
        v = np.frombuffer(v_b.tobytes(), dtype=np.uint8).astype(np.float64) / 255
        keep = (a >= alpha_min) & ~((v >= WHITE_V) & (s <= WHITE_S)) & ~(v <= BLACK_V)
        n = int(keep.sum())
        if n == 0:
            return Metrics(note=NEUTRAL_NOTE, total=float(total))
        m_all = s * v if measure == "C" else s
        vals = np.sort(m_all[keep])
        rank = max(1, math.ceil(0.9 * n))
        hist = [0.0] * (360 // HUE_BIN)
        chroma = keep & (m_all >= CHROMA_S)
        if chroma.any():
            counts = np.bincount((h[chroma] // HUE_BIN).astype(int) % len(hist), minlength=len(hist))
            hist = [float(c) for c in counts]
        return Metrics(mean=float(vals.mean()), p90=float(vals[rank - 1]), hot_share=float((vals > hot_s).sum()) / n,
                       hues=hue_families(hist), counted=float(n), total=float(total))
    # 纯 Python：同一份 HSV 字节
    a_data, h_data, s_data, v_data = alpha.tobytes(), h_b.tobytes(), s_b.tobytes(), v_b.tobytes()
    samples = []
    for i in range(total):
        if a_data[i] < alpha_min:
            continue
        s, v = s_data[i] / 255, v_data[i] / 255
        if is_near_white(s, v) or is_near_black(v):
            continue
        samples.append((h_data[i] * 360 / 255, measure_value(s, v, measure), 1.0))
    m = metrics_from_samples(samples, hot_s)
    m.total = float(total)
    return m


# ---------------------------------------------------------------- SVG

COLOR_ATTR = re.compile(r"""(?P<prop>fill|stroke|stop-color|flood-color)\s*[:=]\s*(?P<q>["']?)(?P<val>[^"';}>]+?)(?P=q)\s*(?=[;"'}/>\s])""", re.I)


def parse_color(text: str) -> tuple[int, int, int] | None:
    t = text.strip()
    if not t or t.lower() in {"none", "currentcolor", "transparent", "inherit", "context-fill", "context-stroke"} or t.lower().startswith("url("):
        return None
    try:
        r = ImageColor.getrgb(t)
    except ValueError:
        return None
    return (r[0], r[1], r[2])


def svg_colors(text: str) -> list[tuple[str, tuple[int, int, int]]]:
    """[(角色 fill 或 stroke, (r, g, b))]，每出现一次一项；stop-color 与 flood-color 按 fill 计。"""
    out = []
    for m in COLOR_ATTR.finditer(text):
        rgb = parse_color(m.group("val"))
        if rgb is None:
            continue
        prop = m.group("prop").lower()
        out.append(("stroke" if prop == "stroke" else "fill", rgb))
    return out


def hex_of(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % tuple(rgb)


def analyze_svg(text: str, token_rgbs: set[tuple[int, int, int]] | None = None, hot_s: float = DEFAULTS["hot_s"],
                measure: str = "S") -> tuple[Metrics, dict]:
    """返回 (指标, 详情)。详情含 colors（去重后的颜色与度量值）、tokens、custom、roles。
    token_rgbs 给出时令牌色不参与饱和度判定（仍计入色相个数）。"""
    weights: dict[tuple[int, int, int], float] = {}
    roles: dict[tuple[int, int, int], set[str]] = {}
    for role, rgb in svg_colors(text):
        _, s, v = hsv_of(rgb)
        if is_near_white(s, v) or is_near_black(v):
            continue
        weights[rgb] = weights.get(rgb, 0.0) + (STROKE_WEIGHT if role == "stroke" else 1.0)
        roles.setdefault(rgb, set()).add(role)
    tokens = token_rgbs or set()
    all_samples, judged = [], []
    for c, w in weights.items():
        h, s, v = hsv_of(c)
        sample = (h, measure_value(s, v, measure), w)
        all_samples.append(sample)
        if c not in tokens:
            judged.append(sample)
    m = metrics_from_samples(judged, hot_s) if judged else Metrics(note="没有需要判定的颜色")
    m.hues = metrics_from_samples(all_samples, hot_s).hues if all_samples else []
    detail = {
        "colors": {hex_of(c): round(measure_value(hsv_of(c)[1], hsv_of(c)[2], measure), 2) for c in weights},
        "tokens": sorted(hex_of(c) for c in weights if c in tokens),
        "custom": sorted(hex_of(c) for c in weights if c not in tokens),
        "roles": {hex_of(c): sorted(r) for c, r in roles.items()},
        "has_image": bool(re.search(r"<image\b", text, re.I)),
    }
    return m, detail


# ---------------------------------------------------------------- 主题令牌与图标色板

def load_themes() -> dict:
    return json.loads(THEMES_PATH.read_text(encoding="utf-8"))


def rgb_of_hex(value: str) -> tuple[int, int, int]:
    return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16))


def load_theme_colors(theme_id: str) -> set[tuple[int, int, int]]:
    """主题 theme_id 的全部颜色令牌（浅色加深色，含 shared），用于判断“是不是令牌色”。"""
    data = load_themes()
    if theme_id not in data["themes"]:
        raise KeyError(theme_id)
    found: set[tuple[int, int, int]] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in {"note", "source", "label", "industry", "subtype", "positioning", "imageStyle", "avoid", "hue"}:
                    continue
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", node):
            found.add(rgb_of_hex(node))

    from export_tokens import application_themes
    projected = application_themes(data)
    walk(projected["themes"][theme_id])
    walk(projected["shared"])
    # Also accept non-green paint from secondary icon variants on coloured controls.
    from export_tokens import application_color
    for mapping in (data["themes"][theme_id].get("dark", {}), data["shared"].get("dark", {})):
        for value in mapping.values():
            if isinstance(value,str) and re.fullmatch(r"#[0-9a-fA-F]{6}",value):
                found.add(rgb_of_hex(application_color(value)))
    return found


def luminance(rgb: tuple[int, int, int]) -> float:
    def lin(c: int) -> float:
        x = c / 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def from_hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
    return (round(r * 255), round(g * 255), round(b * 255))


def icon_palette(theme_id: str) -> dict:
    """图标色板（生成图标的颜色约束，写进提示词）：浅色四色，深色四色。
    浅色：底块 = 主题 actionTint（令牌）；次层、图形、线稿 = 品牌阶的色相，S 与 V 取 PALETTE_SV，S 不超过品牌阶自己的 S；线稿的 V 往下取到对底块 3:1。
    深色：底块 = dark.actionTint，图形与线稿 = dark.actionText（令牌），次层 = 底块与图形 35% 的混合。"""
    data = load_themes()
    from export_tokens import application_theme, application_color
    t = application_theme(theme_id, data)
    h, s_action, _ = hsv_of(rgb_of_hex(t["action"]))
    base = rgb_of_hex(t["actionTint"])
    light = [{"role": "底块", "hex": t["actionTint"], "source": "令牌 actionTint"}]
    for role in ("次层", "图形", "线稿"):
        s_t, v_t = PALETTE_SV[role]
        s_use = min(s_t, s_action)
        rgb = from_hsv(h, s_use, v_t)
        if role == "线稿":
            v = v_t
            while contrast(rgb, base) < 3.0 and v > 0.2:
                v -= 0.02
                rgb = from_hsv(h, s_use, v)
        light.append({"role": role, "hex": hex_of(rgb), "source": f"推导 S 不超过 {s_t}，V {v_t}" + ("，往下取到对底块 3:1" if role == "线稿" else "")})
    dk = data["themes"][theme_id]["dark"]
    d_base, d_fig = rgb_of_hex(application_color(dk["actionTint"])), rgb_of_hex(application_color(dk["actionText"]))
    if any(application_color(dk[key]) != dk[key] for key in ("actionTint","actionText")):
        # Keep dark artwork within the chroma of the light variant's secondary fill.
        light_fill = rgb_of_hex(light[1]["hex"])
        limit = (max(light_fill) - min(light_fill)) / 255
        def bounded(rgb):
            hue, saturation, value = hsv_of(rgb)
            return from_hsv(hue,min(saturation,limit/value if value else 0),value)
        d_base, d_fig = bounded(d_base), bounded(d_fig)
    mix = tuple(round(d_base[i] * 0.65 + d_fig[i] * 0.35) for i in range(3))
    dark = [
        {"role": "底块", "hex": hex_of(d_base), "source": "令牌 dark.actionTint"},
        {"role": "次层", "hex": hex_of(mix), "source": "底块与图形 35% 混合"},
        {"role": "图形", "hex": hex_of(d_fig), "source": "令牌 dark.actionText"},
        {"role": "线稿", "hex": hex_of(d_fig), "source": "令牌 dark.actionText"},
    ]
    for rows, b in ((light, base), (dark, d_base)):
        for row in rows:
            r = rgb_of_hex(row["hex"])
            _, s, v = hsv_of(r)
            row["s"], row["v"], row["c"] = round(s, 2), round(v, 2), round(s * v, 2)
            row["contrast_to_base"] = round(contrast(r, b), 2)
    return {"theme": theme_id, "hue": round(h), "action_s": round(s_action, 2), "light": light, "dark": dark}


def print_palette(theme_id: str) -> int:
    try:
        p = icon_palette(theme_id)
    except KeyError:
        names = ", ".join(load_themes()["themes"])
        print(f"错误：主题 {theme_id} 不在 themes.json 里；可用：{names}", file=sys.stderr)
        return 2
    print(f"主题 {p['theme']}：品牌阶色相 {p['hue']} 度，品牌阶 S {p['action_s']}（生成图标的图形色比它浅，S 不超过 0.65）")
    for name, rows, key in (("浅色", p["light"], "s"), ("深色", p["dark"], "c")):
        label = "S" if key == "s" else "C"
        print(f"{name}（{label} 是{'饱和度' if key == 's' else '彩度 V x S，深色版按它度量'}）")
        for r in rows:
            print(f"  {r['role']}  {r['hex']}  {label} {r[key]:.2f}  V {r['v']:.2f}  对底块 {r['contrast_to_base']:.2f}:1  {r['source']}")
    print("提示词里只写这几个十六进制色，并写“只有这几种色，饱和度不超过 0.65，无渐变高光”；出图后切开逐个用 check_icon_image.py 验收。")
    return 0


# ---------------------------------------------------------------- 判定

def judge(rep: Report, m: Metrics, limits: dict) -> None:
    if not m.counted:
        return
    label = "彩度 C" if rep.measure == "C" else "S"
    if m.mean > limits["max_mean"]:
        rep.problems.append(f"均值 {label} {m.mean:.2f} 超过上限 {limits['max_mean']:.2f}（--max-mean）：整体偏艳，把图形色换成主色更浅的一阶")
    if m.p90 > limits["p90"]:
        rep.problems.append(f"P90 {label} {m.p90:.2f} 超过上限 {limits['p90']:.2f}（--p90）：有一大片颜色太深，降低它的饱和度")
    if m.hot_share > limits["hot_share"]:
        rep.problems.append(f"高饱和像素（{label} 大于 {limits['hot_s']:.2f}）占 {m.hot_share:.1%}，超过上限 {limits['hot_share']:.1%}（--hot-share）：去掉纯色高光和荧光色")
    if len(m.hues) > limits["max_hues"]:
        names = "、".join(f"{h}度" for h, _ in m.hues)
        rep.problems.append(f"主色相 {len(m.hues)} 个（{names}），超过上限 {limits['max_hues']} 个（--max-hues）：同一图标只留主色相和一个邻近色")


def fmt_metrics(m: Metrics, measure: str = "S") -> str:
    if not m.counted:
        return m.note or "无统计像素"
    label = "C" if measure == "C" else "S"
    hues = "、".join(f"{h}度({sh:.0%})" for h, sh in m.hues) or "无彩色"
    return f"均值{label} {m.mean:.2f}  P90 {m.p90:.2f}  高饱和 {m.hot_share:.1%}  色相 {len(m.hues)}（{hues}）  统计 {m.counted:,.0f}/{m.total:,.0f}"


def light_twin(path: Path) -> Path | None:
    m = DARK_SUFFIX.match(path.stem)
    if not m:
        return None
    for ext in [path.suffix, *sorted(IMAGE_EXTS | {".svg"})]:
        cand = path.with_name(m.group("base") + ext)
        if cand.is_file() and cand != path:
            return cand
    return None


def check_file(path: Path, limits: dict, kind: str, token_rgbs: set | None, theme: str | None,
               dark: bool, light_ref: Path | None, use_numpy: bool = True, compare: bool = True) -> Report:
    measure = "C" if dark else "S"
    suffix = path.suffix.lower()
    if suffix == ".svg":
        text = path.read_text(encoding="utf-8", errors="replace")
        m, detail = analyze_svg(text, token_rgbs, limits["hot_s"], measure)
        chromatic = list(detail["colors"])
        only_strokes = all(r == ["stroke"] for r in detail["roles"].values())     # 线稿：颜色只用作描边，没有填充面
        actual = kind if kind != "auto" else ("control" if len(chromatic) <= 1 and only_strokes else "block")
        rep = Report(str(path), actual, "svg", measure=measure, metrics=m)
        if detail["has_image"]:
            rep.notes.append("含内嵌位图 <image>，位图部分另用本脚本检查")
        if actual == "control":
            if len(chromatic) > 1:
                rep.problems.append(f"控件图标是单色：用了 {len(chromatic)} 种颜色（{'、'.join(chromatic)}）；多色请按色块图标处理（--kind block）")
            if theme is None:
                rep.notes.append("线性控件图标不看饱和度，只看是不是令牌色；加 --theme <主题 id> 核对")
            elif detail["custom"]:
                rep.problems.append(f"控件图标用了令牌以外的颜色 {'、'.join(detail['custom'])}（主题 {theme}）：只用文字色或主色线稿，取令牌")
            if chromatic:
                rep.notes.append("颜色写死在文件里：控件图标建议 fill/stroke 用 currentColor，随文字色、状态与深浅色变化")
            rep.metrics = Metrics(note="线性控件图标：不看饱和度，只看令牌色")
        else:
            if detail["tokens"]:
                rep.notes.append(f"令牌色 {len(detail['tokens'])} 个不计饱和度：{'、'.join(detail['tokens'])}")
            judge(rep, m, limits)
        rep.size = f"{len(chromatic)} 种颜色"
    else:
        try:
            with Image.open(path) as im:
                im.load()
                size = f"{im.width}x{im.height}"
                m = analyze_image(im, limits["alpha_min"], limits["hot_s"], use_numpy, measure)
        except Exception as exc:
            raise OSError(f"{path}：打不开图像（{exc}）") from exc
        actual = "block" if kind == "auto" else kind
        rep = Report(str(path), actual, "raster", size, measure, m)
        if actual == "control":
            rep.problems.append("控件图标是 SVG 矢量（2 像素线性，随文字色变化），不用位图；位图只给入口图标块和装饰")
        else:
            judge(rep, m, limits)
    if dark and compare:
        if light_ref is not None:
            compare_dark(rep, light_ref, limits, kind, token_rgbs, use_numpy)
        else:
            rep.notes.append("深色版没有找到对应的浅色版：只按阈值判；要比较请用 --light <浅色版> 或 名称-dark.png 对应 名称.png")
    return rep


def compare_dark(rep: Report, light_ref: Path, limits: dict, kind: str, token_rgbs: set | None, use_numpy: bool) -> None:
    """深色版与浅色版都按彩度 C 度量后比较：深色版不得比浅色版更艳。"""
    try:
        light = check_file(light_ref, limits, kind, token_rgbs, None, True, None, use_numpy, compare=False)
    except OSError as exc:
        rep.problems.append(f"浅色版读取失败：{exc}")
        return
    rep.dark_of = str(light_ref)
    a, b = rep.metrics, light.metrics
    if not a.counted or not b.counted:
        return
    if a.p90 > b.p90 + DARK_P90_TOL:
        rep.problems.append(f"深色版比浅色版更饱和：P90 彩度 C {a.p90:.2f} 高于浅色版 {b.p90:.2f}（容差 {DARK_P90_TOL}）。深色底上的图形色应更柔和，取 dark 映射里的 actionText，不是浅色版整体提亮")


# ---------------------------------------------------------------- 命令行

def collect(paths: list[str], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            pattern = "**/*" if recursive else "*"
            files += sorted(f for f in path.glob(pattern) if f.is_file() and f.suffix.lower() in IMAGE_EXTS | {".svg"})
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(p)
    return files


def parse_share(text: str) -> float:
    t = text.strip()
    value = float(t[:-1]) / 100 if t.endswith("%") else float(t)
    if not 0 <= value <= 1:
        raise argparse.ArgumentTypeError(f"占比要在 0 到 1 之间或写成百分数：{text}")
    return value


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="图标文件或目录")
    ap.add_argument("--max-mean", type=float, default=DEFAULTS["max_mean"], help=f"均值 S 上限，默认 {DEFAULTS['max_mean']}")
    ap.add_argument("--p90", type=float, default=DEFAULTS["p90"], help=f"第 90 百分位 S 上限，默认 {DEFAULTS['p90']}")
    ap.add_argument("--hot-share", type=parse_share, default=DEFAULTS["hot_share"], help="高饱和像素占比上限，0.03 或 3%%")
    ap.add_argument("--hot-s", type=float, default=DEFAULTS["hot_s"], help=f"S 大于它算高饱和，默认 {DEFAULTS['hot_s']}")
    ap.add_argument("--max-hues", type=int, default=DEFAULTS["max_hues"], help=f"主色相个数上限，默认 {DEFAULTS['max_hues']}")
    ap.add_argument("--alpha-min", type=int, default=DEFAULTS["alpha_min"], help="透明度（0 到 255）不低于它才算不透明，默认 128")
    ap.add_argument("--kind", choices=["auto", "block", "control"], default="auto", help="block 色块图标，control 线性控件图标；auto 位图按 block，SVG 按颜色数")
    ap.add_argument("--theme", help="主题 id（references/themes.json），SVG 用它核对令牌色")
    ap.add_argument("--dark", action="store_true", help="把输入当作深色版（按彩度 C 度量）")
    ap.add_argument("--light", help="与 --dark 配合：对应的浅色版文件")
    ap.add_argument("--palette", metavar="THEME", help="打印该主题的图标色板（浅色与深色）后退出")
    ap.add_argument("-r", "--recursive", action="store_true", help="目录递归")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--quiet", action="store_true", help="只打印不通过的文件和最后一行")
    ap.add_argument("--no-numpy", action="store_true", help="不用 numpy（校验两条路径一致）")
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if args.palette:
        return print_palette(args.palette)
    if not args.paths:
        ap.error("需要至少一个图标文件或目录（或用 --palette 主题）")
    limits = {"max_mean": args.max_mean, "p90": args.p90, "hot_share": args.hot_share, "hot_s": args.hot_s,
              "max_hues": args.max_hues, "alpha_min": args.alpha_min}
    try:
        files = collect(args.paths, args.recursive)
    except FileNotFoundError as exc:
        print(f"错误：找不到 {exc}", file=sys.stderr)
        return 2
    if not files:
        print("错误：没有找到图标文件（png、webp、jpg、svg）", file=sys.stderr)
        return 2
    token_rgbs = None
    if args.theme:
        try:
            token_rgbs = load_theme_colors(args.theme)
        except KeyError:
            names = ", ".join(load_themes()["themes"])
            print(f"错误：主题 {args.theme} 不在 themes.json 里；可用：{names}", file=sys.stderr)
            return 2
    if args.light and len(files) != 1:
        print("错误：--light 只能配一个深色版文件", file=sys.stderr)
        return 2
    reports: list[Report] = []
    for f in files:
        ref = Path(args.light) if args.light else light_twin(f)
        if ref is not None and not ref.is_file():
            print(f"错误：找不到浅色版 {ref}", file=sys.stderr)
            return 2
        is_dark = args.dark or ref is not None
        try:
            reports.append(check_file(f, limits, args.kind, token_rgbs, args.theme, is_dark, ref, not args.no_numpy))
        except OSError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 2
    bad = [r for r in reports if not r.ok]
    if args.json:
        print(json.dumps([{
            "path": r.path, "kind": r.kind, "format": r.fmt, "size": r.size, "measure": r.measure, "ok": r.ok, "problems": r.problems, "notes": r.notes,
            "mean": round(r.metrics.mean, 4), "p90": round(r.metrics.p90, 4), "hot_share": round(r.metrics.hot_share, 4),
            "hues": [{"deg": h, "share": round(s, 3)} for h, s in r.metrics.hues], "counted": r.metrics.counted, "total": r.metrics.total,
        } for r in reports], ensure_ascii=False, indent=2))
    else:
        for r in reports:
            if args.quiet and r.ok:
                continue
            label = "色块图标" if r.kind == "block" else "控件图标"
            fmt = "SVG" if r.fmt == "svg" else "位图"
            tag = f"{label} {fmt} {r.size}".strip() + ("，深色版按彩度 C" if r.measure == "C" else "")
            print(f"{r.path}  [{tag}]")
            print("  " + fmt_metrics(r.metrics, r.measure))
            for p in r.problems:
                print(f"  超限：{p}")
            for n in r.notes:
                print(f"  注：{n}")
            if r.dark_of:
                print(f"  对照浅色版：{r.dark_of}")
    if bad:
        print(f"check icon image: failed, {len(bad)} of {len(reports)} files over the limits")
        return 1
    print("check icon image: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
