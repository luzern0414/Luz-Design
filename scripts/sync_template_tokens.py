#!/usr/bin/env python3
"""Write kit/tokens.css.

One brand colour per theme. Everything that follows the brand (press, tint, edge, neutrals, lines, shadows, accent) is derived in CSS with
color-mix from --action, so a theme is only a hue, a muted chroma and a lightness; the 24 presets below are computed in OKLCH and fitted so
white text on the primary reads at 4.6:1 or more. Custom colours do the same fit in ui.js (Lz.skin({ color })). Status colours (success,
warning, danger, info, price) come from references/themes.json and only ever mean a state.

  py -X utf8 scripts/sync_template_tokens.py          write tokens.css
  py -X utf8 scripts/sync_template_tokens.py --check  exit 1 when tokens.css is stale
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEMES_JSON = ROOT / "references" / "themes.json"
OUT = ROOT / "kit" / "tokens.css"
DEFAULT = "rose"
TARGET = 4.6  # white text on the primary colour

# id, 名称, 色相, 彩度（偏低，简约），亮度上限（深色系用）
THEMES = [
    ("rose", "玫瑰", 8, 0.095, 0.62),
    ("wine", "酒红", 8, 0.115, 0.42),
    ("coral", "珊瑚", 28, 0.100, 0.62),
    ("terracotta", "赤陶", 46, 0.090, 0.62),
    ("amber", "琥珀", 68, 0.095, 0.62),
    ("sand", "沙金", 88, 0.075, 0.62),
    ("olive", "橄榄", 112, 0.080, 0.62),
    ("sage", "鼠尾草", 145, 0.045, 0.62),
    ("green", "草绿", 148, 0.100, 0.62),
    ("pine", "松绿", 168, 0.075, 0.50),
    ("teal", "青碧", 195, 0.080, 0.62),
    ("cyan", "湖蓝", 224, 0.085, 0.62),
    ("sky", "天蓝", 246, 0.100, 0.62),
    ("blue", "靛蓝", 265, 0.120, 0.58),
    ("navy", "藏青", 262, 0.070, 0.40),
    ("indigo", "靛紫", 285, 0.120, 0.58),
    ("purple", "紫藤", 300, 0.100, 0.62),
    ("mauve", "雾紫", 320, 0.060, 0.62),
    ("plum", "梅紫", 340, 0.100, 0.58),
    ("graphite", "石墨", 255, 0.012, 0.44),
    ("slate", "岩灰", 235, 0.030, 0.50),
    ("stone", "暖灰", 75, 0.016, 0.50),
    ("mocha", "摩卡", 55, 0.040, 0.46),
    ("ink", "墨黑", 270, 0.010, 0.26),
]
ACCENT_SHIFT = 38  # the accent is the brand hue turned by this much, only for campaigns, badges and membership


# ---- colour maths -------------------------------------------------------------------------------------------------------------
def _encode(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (abs(c) ** (1 / 2.4)) - 0.055


def oklch_to_rgb(lightness: float, chroma: float, hue: float) -> tuple[float, float, float]:
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    l_, m_, s_ = lightness + 0.3963377774 * a + 0.2158037573 * b, lightness - 0.1055613458 * a - 0.0638541728 * b, lightness - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (_encode(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s), _encode(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
            _encode(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s))


def in_gamut(rgb: tuple[float, float, float]) -> bool:
    return all(-0.0005 <= c <= 1.0005 for c in rgb)


def to_hex(lightness: float, chroma: float, hue: float) -> str:
    while chroma > 0 and not in_gamut(oklch_to_rgb(lightness, chroma, hue)):
        chroma -= 0.002
    rgb = oklch_to_rgb(lightness, max(chroma, 0), hue)
    return "#" + "".join(f"{round(min(max(c, 0), 1) * 255):02X}" for c in rgb)


def luminance(hex_value: str) -> float:
    r, g, b = (int(hex_value.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def fit(chroma: float, hue: float, cap: float, target: float = TARGET) -> str:
    """The lightest colour of this hue and chroma that still reads with white text at the target ratio, never lighter than the cap."""
    lightness = cap
    while lightness > 0.15:
        value = to_hex(lightness, chroma, hue)
        if contrast(value, "#FFFFFF") >= target:
            return value
        lightness -= 0.004
    return to_hex(0.15, chroma, hue)


def css_hue(hex_value: str) -> int:
    """HSL hue of the colour: what the CSS hue-rotate filter that tints the mono icons expects."""
    import colorsys
    r, g, b = (int(hex_value.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return round(colorsys.rgb_to_hls(r, g, b)[0] * 360) % 360


def preset(theme: tuple) -> dict:
    tid, name, hue, chroma, cap = theme
    action = fit(chroma, hue, cap)
    accent_hue = (hue + ACCENT_SHIFT) % 360
    return {
        "id": tid, "name": name, "oklch_hue": hue, "hue": css_hue(action), "chroma": chroma, "action": action,
        "accent": fit(min(chroma + 0.01, 0.1), accent_hue, 0.6),
        "sat": round(min(chroma / 0.10 * 1.5, 1.9), 2),
    }


def presets() -> list[dict]:
    return [preset(t) for t in THEMES]


# ---- tokens ------------------------------------------------------------------------------------------------------------------
HEAD = """/* 令牌文件：由 scripts/sync_template_tokens.py 生成，不手改 */
:root {
  --font: "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;

  /* 字阶：一套字体，字重常用 400、500、600，页面标题与主数值可用 700 */
  --fs-xs: 12px; --fs-sm: 14px; --fs-md: 16px; --fs-lg: 18px; --fs-xl: 22px; --fs-2xl: 28px; --fs-3xl: 32px;
  --lh-tight: 1.3; --lh-body: 1.6;

  /* 间距：4 的倍数 */
  --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px; --s-5: 20px; --s-6: 24px; --s-8: 32px; --s-12: 48px;

  /* 圆角档位：卡片 20，大块 24，控件 12，小件 8，胶囊 999 */
  --r-sm: 8px; --r-md: 12px; --r-lg: 20px; --r-xl: 24px; --r-full: 999px;

  /* 品牌色只有一个：--action。其余随它派生，换主题或自选色时整套跟着变 */
  --action-press: color-mix(in srgb, var(--action) 74%, #000);
  --action-tint: color-mix(in srgb, var(--action) 7%, #fff);
  --action-edge: color-mix(in srgb, var(--action) 20%, #fff);
  --action-soft: color-mix(in srgb, var(--action) 15%, #fff);
  --zone: color-mix(in srgb, var(--action) 11%, #fff);
  --accent-tint: color-mix(in srgb, var(--accent) 11%, #fff);

  /* 底与表面：近白页底带一点主题色，白卡片；文字是带主题色的近黑 */
  --bg: color-mix(in srgb, var(--action) 2.5%, #FAFAF9);
  --surface: #FFFFFF;
  --ink: color-mix(in srgb, var(--action) 6%, #1D1F23);
  --ink-2: color-mix(in srgb, var(--action) 7%, #474A50);
  --ink-3: color-mix(in srgb, var(--action) 7%, #666A71);
  --line: color-mix(in srgb, var(--ink) 9%, transparent);
  --line-strong: color-mix(in srgb, var(--ink) 17%, transparent);
  --scrim: color-mix(in srgb, var(--ink) 48%, transparent);

  /* 语义色：只表达状态，必须配文字 */
  --success: @success@; --success-tint: #E4F3EC;
  --warning: @warning@; --warning-tint: #FBF0DE;
  --danger: @danger@;  --danger-tint: #FBE7E9;
  --info: @info@;    --info-tint: #E6EEF5;
  --price: @price@;   --price-tint: #FFF1F0;

  /* 层级：五级，阴影只向下，颜色取自文字色 */
  --elev-0: none;
  --elev-1: 0 1px 2px color-mix(in srgb, var(--ink) 5%, transparent), 0 3px 10px color-mix(in srgb, var(--ink) 4%, transparent);
  --elev-2: 0 2px 4px color-mix(in srgb, var(--ink) 6%, transparent), 0 8px 20px color-mix(in srgb, var(--ink) 7%, transparent);
  --elev-3: 0 4px 8px color-mix(in srgb, var(--ink) 7%, transparent), 0 14px 28px color-mix(in srgb, var(--ink) 10%, transparent);
  --elev-4: 0 8px 16px color-mix(in srgb, var(--ink) 9%, transparent), 0 26px 52px color-mix(in srgb, var(--ink) 14%, transparent);
  --elev-icon: drop-shadow(0 6px 8px color-mix(in srgb, var(--ink) 12%, transparent));

  /* 动效：时长与曲线（方法参考 transitions.dev 的变量化思路，取值自写） */
  --dur-instant: 90ms; --dur-quick: 150ms; --dur-base: 220ms; --dur-slow: 320ms; --stagger: 40ms;
  --ease-out: cubic-bezier(.22, 1, .36, 1);
  --ease-in-out: cubic-bezier(.65, 0, .35, 1);
  --ease-spring: cubic-bezier(.34, 1.4, .64, 1);

  color-scheme: light;
}
"""


ICON_RULE = """
/* 图标形态：html 的 data-icons，mono 单色（默认，扁平图标集按主题色相单色化）、flat 彩色扁平、3d 立体、real 真实。
   线性图标始终是文字色；换图标集由 ui.js 的 Lz.skin 改 img[data-ic] 的地址，mono 只是同一组扁平图加滤镜（--ic-fx，可与阴影滤镜叠用） */
:root { --ic-fx: opacity(1); }
html:not([data-icons]), html[data-icons="mono"] { --ic-fx: grayscale(1) sepia(1) hue-rotate(calc(var(--hue, 348) * 1deg - 38deg)) saturate(var(--ic-sat, 1.4)) contrast(1.06); }
:is(img[data-ic], img[src*="/icons/"], img[src*="/solid/"]) { filter: var(--ic-fx); }
"""


def block(selector: str, theme: dict) -> str:
    return (f"{selector} {{\n  --action: {theme['action']};\n  --accent: {theme['accent']};\n  --hue: {theme['hue']};\n  --ic-sat: {theme['sat']};\n}}\n")


def render() -> str:
    shared = json.loads(THEMES_JSON.read_text(encoding="utf-8-sig"))["shared"]
    head = HEAD
    for key in ("success", "warning", "danger", "info", "price"):
        head = head.replace(f"@{key}@", shared[key])
    items = presets()
    by_id = {t["id"]: t for t in items}
    parts = [head, "\n/* 主题：24 个预设，默认 " + DEFAULT + "，用 data-theme 切换；自选色由 ui.js 写入 --action 等同名变量 */\n", block(":root", by_id[DEFAULT])]
    for t in items:
        parts.append(f"\n/* {t['name']} */\n" + block(f'[data-theme="{t["id"]}"]', t))
    parts.append(ICON_RULE)
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            print("tokens.css 已过期，运行 scripts/sync_template_tokens.py")
            return 1
        print("tokens.css 与调色板一致")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"写入 {OUT.relative_to(ROOT)}（{len(THEMES)} 个预设）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
