#!/usr/bin/env python3
"""检查 themes.json 中每套主题的关键对比度与配色规则。

规则（对应 references/design-standards.html 第六层“视觉基础”）：
- 白字（surface）在 action / actionPress 上 >= 4.5:1（按钮文字）
- actionPress 文字在 actionTint 上 >= 4.5:1（浅底上的选中态文字用按压档，TDesign 色阶规则）
- 白字在 action 上 >= 4.5:1 同时保证开关、图表用 action 时对白底 >= 3:1（WCAG 1.4.11）
- ink / ink2 在 canvas 上 >= 4.5:1（正文与辅助文字）
- ink 在 navBg 上 >= 4.5:1；ink2 在 navBg 上 >= 3.0:1（导航栏只放 ink 文字与图标）
- ink3 在 surface 上 >= 4.5:1
- success / warning / danger / info 在 surface 上 >= 4.5:1
- ink 在 accentTint 上 >= 4.5:1（accent 只做底色，不做文字）
- canvas 为浅白或极浅灰的中性色（与同明度灰的 RGB 偏差 <= 2，亮度 >= 0.85）；navBg 用白底或主色浅底阶纯色
- dark（可选）：ink(dark) 在 dark.canvas / dark.surface 上 >= 4.5；白字在 dark.action 上 >= 4.5
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
        rules = [
            # 扁平线性风格：页面底用浅白或极浅灰的中性色，低饱和；导航条可用白底或主色浅底阶纯色。
            ("canvas 中性浅灰", chroma(t["canvas"]) <= 2 and luminance(t["canvas"]) >= 0.85, f"chroma {chroma(t['canvas'])}"),
        ]
        for label, ok, note in rules:
            failed = failed or not ok
            print(f"  {'PASS' if ok else 'FAIL'} {label:28} {note}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
