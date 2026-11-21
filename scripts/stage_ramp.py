#!/usr/bin/env python3
"""有序进度状态的色阶：生成与校验（visual-design.html 有序进度状态的色阶）。

  py -X utf8 scripts/stage_ramp.py make --theme b2b-graphite --n 5 [--mode light|dark] [--json]
  py -X utf8 scripts/stage_ramp.py check --colors "#6B6F7A,#4A5A86,#4B4C8C" --bg "#FFFFFF[,#FAFAFA]" [--mode light|dark] [--tint] [--cvd]
  py -X utf8 scripts/stage_ramp.py themes [--theme <主题 id>] [--write | --check]     themes.json 里每个主题的 stage 与本算法逐项核对

同一个页面里出现一个有先后顺序的状态集合的多个取值（沟通深度、轮次、订单进度、审批环节）时，文字用一条随顺序递进的色阶区分。
色阶是一条 6 级的序列色（stage-1 到 stage-6），颜色按顺序位置取，不按名字写死；N 个状态（2 到 6）按等间隔取其中 N 级，超过 6 个分档。

算法（OKLCH，Ottosson 2020；数值是本技能取值，依据与取值理由见规则页）：
  - 6 级沿同一条短弧走：色相从起点色相（主色，彩度不足时取辅色的色相，钳进 210–230 度的窗口）起，共转 ARC = 70 度（终点 280–300 度，青蓝经蓝到蓝紫）；
    原始文档色库按自身语义色核验；应用端使用 export_tokens.py 的白色与非绿色投影，终态显示文字和图形；
  - 彩度 C 从 0.03 逐级增加到 0.12（深色到 0.10，高明度处色域装不下更多）；不超过成功、警告状态文字色的彩度（0.110、0.124），更不及危险红 0.183；
  - 明度 L：浅色从 0.53 逐级降到 0.34（越靠后越深越实），深色从 0.71 逐级升到 0.84（越靠后越亮越醒目）；
  - 6 个点沿这条路径按等 OKLab 距离取，不按等间距取（低彩度的头几级不会挤在一起）；
  - 每一级对所在各层底（浅色：卡片白底、页面底；深色：页面底、卡片面、导航底和浮起的面）和自己的浅底标签（本色混入卡片面：浅色 10%，深色 16%）
    都不低于 4.5:1（求解目标 4.6，留 8 位取整的余量），不够就沿明度挪，色相与彩度不动；
  - 相邻两级的 OKLab 距离 ΔE（×100）不低于 3.0，彩度不递减，明度浅色不增、深色不减，彩度不超过 0.12（容差 0.004）。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_contrast as cc  # noqa: E402
import make_dark as md  # noqa: E402

THEMES = HERE.parent / "references" / "themes.json"

STOPS = 6                       # 色阶级数，也是同一集合的上限
ARC = 70.0                      # 6 级走过的色相角度
HUE_WINDOW = (210.0, 230.0)     # 起点色相的窗口
CHROMA = {"light": (0.03, 0.12), "dark": (0.03, 0.10)}   # stage-1 到 stage-6 的彩度；深色在高明度处色域装不下更多
LIGHTNESS = {"light": (0.53, 0.34), "dark": (0.71, 0.84)}
TARGET_CONTRAST = 4.6           # 求解目标；检查的下限是 4.5
MIN_CONTRAST = 4.5
MIN_DE = 3.0                    # 相邻两级 OKLab ΔE×100 的下限：本技能取值（行内常说最小可觉差约 2，本次检索的资料没有证实）；25 个主题实测浅色最小 4.36、深色最小 3.16
MAX_CHROMA = 0.12
CHROMA_TOLERANCE = 0.004        # 8 位取整与进出色域造成的偏差
MONOTONE_TOLERANCE = 0.006
TINT_MIX = {"light": 0.10, "dark": 0.16}
CVD_MIN_DE = 1.0                # 色觉缺陷模拟下相邻两级仍应有的 OKLab ΔE×100（只在 check --cvd 时核对，不是主题库的硬规则）


# ---------------------------------------------------------------- 取位：N 个状态取哪几级

def positions(n: int) -> list[int]:
    """N 个有序状态（2 到 6）取的色阶级序（1 到 6）：等间隔，floor(i×5/(N−1)+0.5)。N=1 不上色，返回空。
    N 大于 6 时用 tiers() 分档。"""
    if n < 1:
        raise ValueError("n 至少是 1")
    if n == 1:
        return []
    if n > STOPS:
        raise ValueError(f"{n} 个状态超过 {STOPS} 级，用 tiers() 分档")
    return [math.floor(i * (STOPS - 1) / (n - 1) + 0.5) + 1 for i in range(n)]


def tiers(n: int) -> list[int]:
    """N 个有序状态（大于 6）分成 6 档：第 i 个状态（从 0 数）落在档 floor(i×6/N)+1，每档同一种颜色，状态仍靠文字区分。N 不大于 6 时等同 positions()。"""
    if n <= STOPS:
        return positions(n)
    return [i * STOPS // n + 1 for i in range(n)]


# ---------------------------------------------------------------- 颜色小工具

def oklch(color: str) -> tuple[float, float, float]:
    return md.hex_to_oklch(cc.normalize_hex(color))


def oklab(color: str) -> tuple[float, float, float]:
    lightness, chroma, hue = oklch(color)
    return lightness, chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))


def delta_e(a: str, b: str) -> float:
    """OKLab 距离 × 100（与 audit_theme_discipline 同一口径）。"""
    return 100 * math.dist(oklab(a), oklab(b))


def tint_of(color: str, mode: str, surface: str) -> str:
    """色阶某一级的浅底标签：本色按 TINT_MIX 混入卡片面（color-mix(in srgb, 本色 10%, 卡片面)）。"""
    k = TINT_MIX[mode]
    return "#%02X%02X%02X" % tuple(round(c * k + s * (1 - k)) for c, s in zip(cc.rgb(color), cc.rgb(surface)))


def circular_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def start_hue(theme: dict) -> float:
    """起点色相：主色（彩度不足时用辅色）的 OKLCH 色相，钳到离它最近的窗口边界或窗口内原值。"""
    source = theme["action"] if oklch(theme["action"])[1] >= 0.04 else theme["accent"]
    hue = oklch(source)[2]
    lo, hi = HUE_WINDOW
    if lo <= hue <= hi:
        return round(hue, 1)
    return lo if circular_distance(hue, lo) <= circular_distance(hue, hi) else hi


# ---------------------------------------------------------------- 底色

def grounds(theme_id: str, data: dict, mode: str) -> dict[str, str]:
    """色阶文字会落在的各层底。浅色：卡片白底和页面底；深色：页面底、卡片面、导航底和浮起的面（不含品牌浅底）。"""
    shared, theme = data["shared"], data["themes"][theme_id]
    if mode == "light":
        return {"surface": shared["surface"], "canvas": theme["canvas"]}
    dark = theme["dark"]
    out = cc.dark_grounds(dark, shared["dark"]["elevation"])
    return {k: v for k, v in out.items() if k not in ("actionTint", "accentTint")}


def surface_of(theme_id: str, data: dict, mode: str) -> str:
    return data["shared"]["surface"] if mode == "light" else data["themes"][theme_id]["dark"]["surface"]


# ---------------------------------------------------------------- 生成

def worst_contrast(color: str, backgrounds: list[str]) -> float:
    return min(cc.contrast(color, bg) for bg in backgrounds)


def fit(lightness: float, chroma: float, hue: float) -> tuple[float, float, float]:
    """(L, C, H)，彩度降到装得进 sRGB 色域为止（明度与色相不动），不取整到 8 位。"""
    def inside(c: float) -> bool:
        return all(-1e-4 <= v <= 1 + 1e-4 for v in md._oklch_to_linear(lightness, c, hue))
    if inside(chroma):
        return lightness, chroma, hue
    lo, hi = 0.0, chroma
    for _ in range(28):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if inside(mid) else (lo, mid)
    return lightness, lo, hue


def path(hue0: float, mode: str, t: float) -> tuple[float, float, float]:
    """色阶的路径：明度、彩度、色相都随 t（0 到 1）线性走，彩度被色域截到装得下为止。"""
    l0, l1 = LIGHTNESS[mode]
    c0, c1 = CHROMA[mode]
    return fit(l0 + (l1 - l0) * t, c0 + (c1 - c0) * t, (hue0 + ARC * t) % 360)


def lab_of(lch: tuple[float, float, float]) -> tuple[float, float, float]:
    lightness, chroma, hue = lch
    return lightness, chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))


def equal_steps(hue0: float, mode: str, samples: int = 600) -> list[tuple[float, float, float]]:
    """沿路径按等 OKLab 距离取 6 个点：相邻两级的色差相等，不让低彩度的起点几级挤在一起。"""
    pts = [path(hue0, mode, k / samples) for k in range(samples + 1)]
    cumulative = [0.0]
    for p, q in zip(pts, pts[1:]):
        cumulative.append(cumulative[-1] + math.dist(lab_of(p), lab_of(q)))
    total = cumulative[-1]
    stops: list[tuple[float, float, float]] = []
    k = 0
    for i in range(STOPS):
        goal = total * i / (STOPS - 1)
        while k < samples and cumulative[k] < goal - 1e-12:
            k += 1
        stops.append(pts[k])
    return stops


def make(hue0: float, mode: str, backgrounds: list[str], surface: str) -> list[str]:
    """6 级色阶（stage-1 到 stage-6）。backgrounds 是文字会落在的各层底，surface 是浅底标签混入的卡片面。"""
    step = -0.002 if mode == "light" else 0.002
    out: list[str] = []
    for lightness, chroma, hue in equal_steps(hue0, mode):
        # 沿明度挪到所有底与自己的浅底标签都达标：浅色往深挪，深色往亮挪
        for _ in range(400):
            color = md.oklch_hex(lightness, chroma, hue)
            if worst_contrast(color, backgrounds + [tint_of(color, mode, surface)]) >= TARGET_CONTRAST:
                break
            lightness += step
        # 明度单向：不让后一级比前一级更靠近底
        if out:
            previous = oklch(out[-1])[0]
            lightness = min(lightness, previous) if mode == "light" else max(lightness, previous)
            color = md.oklch_hex(lightness, chroma, hue)
        out.append(color)
    return out


def theme_ramp(theme_id: str, data: dict | None = None) -> dict:
    """一个主题的 stage 数据：起点色相、浅色与深色各 6 级。themes.json 里存的就是这个。"""
    data = data or json.loads(THEMES.read_text(encoding="utf-8"))
    theme = data["themes"][theme_id]
    hue0 = start_hue(theme)
    result: dict = {"hue": hue0}
    for mode in ("light", "dark"):
        backgrounds = list(grounds(theme_id, data, mode).values())
        result[mode] = make(hue0, mode, backgrounds, surface_of(theme_id, data, mode))
    return result


# ---------------------------------------------------------------- 校验

def cvd_delta_e(a: str, b: str, kind: str) -> float:
    import audit_theme_discipline as atd
    return atd.cvd_delta_e(a, b, kind)


def check(colors: list[str], backgrounds: list[str], mode: str = "light", *, tint_surface: str | None = None, cvd: bool = False,
          label: str = "") -> list[tuple[str, bool, str]]:
    """一组有序颜色（先到后）的逐项核对，返回 (规则, 是否通过, 说明)。
    逐级：对每层底（和自己的浅底标签，给了 tint_surface 时）的对比度不低于 4.5；相邻两级 ΔE×100 不低于 3.5；彩度不递减；明度浅色不增、深色不减；彩度不超过 0.12。"""
    rules: list[tuple[str, bool, str]] = []
    colors = [cc.normalize_hex(c) for c in colors]
    backgrounds = [cc.normalize_hex(b) for b in backgrounds]
    p = f"{label} " if label else ""
    for i, c in enumerate(colors, 1):
        bgs = list(backgrounds)
        names = [f"底 {b}" for b in bgs]
        if tint_surface:
            bgs.append(tint_of(c, mode, cc.normalize_hex(tint_surface)))
            names.append("自己的浅底标签")
        ratios = [cc.contrast(c, b) for b in bgs]
        worst = min(range(len(ratios)), key=lambda k: ratios[k])
        rules.append((f"{p}stage-{i} {c} 对比度 >= {MIN_CONTRAST:g}", ratios[worst] >= MIN_CONTRAST, f"{ratios[worst]:.2f}:1 on {names[worst]}"))
    lch = [oklch(c) for c in colors]
    for i in range(1, len(colors)):
        d = delta_e(colors[i - 1], colors[i])
        rules.append((f"{p}第 {i} 与 {i + 1} 级相邻色差 ΔE×100 >= {MIN_DE:g}", d >= MIN_DE, f"{d:.2f}"))
        dc = lch[i][1] - lch[i - 1][1]
        rules.append((f"{p}第 {i} 到 {i + 1} 级彩度不递减", dc >= -MONOTONE_TOLERANCE, f"{lch[i - 1][1]:.3f} -> {lch[i][1]:.3f}"))
        dl = lch[i][0] - lch[i - 1][0]
        ok = dl <= MONOTONE_TOLERANCE if mode == "light" else dl >= -MONOTONE_TOLERANCE
        rules.append((f"{p}第 {i} 到 {i + 1} 级明度{'不增' if mode == 'light' else '不减'}", ok, f"{lch[i - 1][0]:.3f} -> {lch[i][0]:.3f}"))
        if cvd:
            for kind in ("protan", "deut", "tritan"):
                dv = cvd_delta_e(colors[i - 1], colors[i], kind)
                rules.append((f"{p}第 {i} 与 {i + 1} 级在 {kind} 下 ΔE×100 >= {CVD_MIN_DE:g}", dv >= CVD_MIN_DE, f"{dv:.2f}"))
    top = max(c[1] for c in lch) if lch else 0
    rules.append((f"{p}彩度不超过 {MAX_CHROMA:g}", top <= MAX_CHROMA + CHROMA_TOLERANCE, f"最大 {top:.3f}"))
    return rules


def theme_rules(theme_id: str, t: dict, shared: dict, data: dict | None = None) -> list[tuple[str, bool, str]]:
    """themes.json 里一个主题的 stage：键齐全，与算法一致，浅色与深色各自过 check。给 check_contrast 与 export_tokens 用。"""
    data = data or {"shared": shared, "themes": {theme_id: t}}
    stage = t.get("stage")
    if not isinstance(stage, dict) or not all(k in stage for k in ("hue", "light", "dark")):
        return [("stage 色阶存在", False, f"missing themes.{theme_id}.stage (hue, light, dark)")]
    rules: list[tuple[str, bool, str]] = []
    for mode in ("light", "dark"):
        colors = stage[mode]
        if not (isinstance(colors, list) and len(colors) == STOPS):
            rules.append((f"stage {mode} 共 {STOPS} 级", False, f"{len(colors) if isinstance(colors, list) else colors}"))
            continue
        try:
            for c in colors:
                cc.normalize_hex(c)
        except ValueError as exc:
            rules.append((f"stage {mode} 取值是十六进制色", False, str(exc)))
            continue
        bgs = list(grounds(theme_id, data, mode).values())
        rules += check(colors, bgs, mode, tint_surface=surface_of(theme_id, data, mode), label=f"stage {mode}")
    rules.append(("stage 起点色相在窗口内", HUE_WINDOW[0] <= stage["hue"] <= HUE_WINDOW[1], f"{stage['hue']}"))
    return rules


# ---------------------------------------------------------------- 渲染后的页面（audit_rendered.py 调用）

def audit_items(items: list[dict], tokens: list[str | None] | None = None, scheme: str = "light") -> list[str]:
    """渲染后页面里带 data-stage-set 与 data-stage 的元素（先后顺序的状态集合）逐项核对，返回问题清单；页面里没有这类元素就返回空。

    items 的每一项：set（集合名）、pos（顺序位，从 1 数）、n（集合的状态个数，可为 None 表示直接按色阶级序取）、color（计算后的文字色，十六进制）、
    text（元素的文字或无障碍名称）、label（报告里用来指认元素的短名）。tokens 是页面根元素上 --stage-1 到 --stage-6 的计算值（没有的写 None）。
    核对的事：状态不能只靠颜色（有文字标签）；同一集合里同一顺序位颜色一致；同一集合里不同顺序位颜色不同，相邻的两个顺序位相差不低于 MIN_DE，
    且逐级递进（彩度不递减，明度浅色不增、深色不减）；页面声明了六级令牌时，颜色要正是顺序位对应的那一级。
    """
    errors: list[str] = []
    by_set: dict[str, list[dict]] = {}
    for item in items:
        by_set.setdefault(item["set"], []).append(item)
    declared = tokens if tokens and all(tokens) else None
    for name, members in by_set.items():
        unlabeled = [m["label"] for m in members if not (m.get("text") or "").strip()]
        if unlabeled:
            errors.append(f"有序状态 {name}: 只有颜色没有文字标签（WCAG 1.4.1 不能只靠颜色）: " + "; ".join(unlabeled[:6]))
        bad_pos = [m["label"] for m in members if not isinstance(m["pos"], int) or m["pos"] < 1]
        if bad_pos:
            errors.append(f"有序状态 {name}: data-stage 要从 1 起的整数顺序位: " + "; ".join(bad_pos[:6]))
            continue
        by_pos: dict[int, list[dict]] = {}
        for m in members:
            by_pos.setdefault(m["pos"], []).append(m)
        colours: dict[int, str] = {}
        for pos, group in sorted(by_pos.items()):
            seen = {cc.normalize_hex(g["color"]) for g in group}
            if len(seen) > 1:
                errors.append(f"有序状态 {name}: 顺序位 {pos} 在页面里有 {len(seen)} 种颜色 {', '.join(sorted(seen))}，同一取值同一颜色")
            colours[pos] = cc.normalize_hex(group[0]["color"])
        if declared:
            ramp = [cc.normalize_hex(t) for t in declared]
            for pos, group in sorted(by_pos.items()):
                n = group[0].get("n") or STOPS
                try:
                    want = ramp[(positions(n)[pos - 1] if n > 1 else 1) - 1] if n <= STOPS else ramp[tiers(n)[pos - 1] - 1]
                except (ValueError, IndexError):
                    errors.append(f"有序状态 {name}: 顺序位 {pos} 超出集合个数 {n}")
                    continue
                if colours[pos] != want:
                    errors.append(f"有序状态 {name}: 顺序位 {pos}（共 {n} 个）的颜色 {colours[pos]} 不是色阶令牌的对应一级 {want}")
        ordered = sorted(colours)
        for a, b in zip(ordered, ordered[1:]):
            ca, cb = colours[a], colours[b]
            if ca == cb:
                errors.append(f"有序状态 {name}: 顺序位 {a} 与 {b} 颜色相同（{ca}），同页不同进度要用不同颜色")
                continue
            d = delta_e(ca, cb)
            if d < MIN_DE:
                errors.append(f"有序状态 {name}: 顺序位 {a} 与 {b} 的颜色太接近（ΔE×100 {d:.2f}，至少 {MIN_DE:g}）")
            la, lb = oklch(ca), oklch(cb)
            if lb[1] < la[1] - MONOTONE_TOLERANCE:
                errors.append(f"有序状态 {name}: 顺序位 {a} 到 {b} 彩度反而下降（{la[1]:.3f} 到 {lb[1]:.3f}），颜色要随进度递进")
            lightness_ok = (lb[0] <= la[0] + MONOTONE_TOLERANCE) if scheme == "light" else (lb[0] >= la[0] - MONOTONE_TOLERANCE)
            if not lightness_ok:
                errors.append(f"有序状态 {name}: 顺序位 {a} 到 {b} 明度走向反了（{la[0]:.3f} 到 {lb[0]:.3f}，{'浅色越靠后越深' if scheme == 'light' else '深色越靠后越亮'}）")
    return errors


# ---------------------------------------------------------------- 命令行

def pick(colors: list[str], n: int) -> list[str]:
    return [colors[p - 1] for p in positions(n)] if n > 1 else []


def cmd_make(args) -> int:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    if args.theme not in data["themes"]:
        print(f"错误：主题 {args.theme} 不在 themes.json 里；可用：{', '.join(data['themes'])}", file=sys.stderr)
        return 2
    ramp = theme_ramp(args.theme, data)
    modes = [args.mode] if args.mode else ["light", "dark"]
    n = args.n
    out: dict = {"theme": args.theme, "n": n, "hue": ramp["hue"]}
    try:
        idx = positions(n) if n <= STOPS else tiers(n)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    out["positions"] = idx
    for mode in modes:
        colors = [ramp[mode][p - 1] for p in idx]
        surface = surface_of(args.theme, data, mode)
        out[mode] = [{"stage": p, "color": c, "tint": tint_of(c, mode, surface)} for p, c in zip(idx, colors)]
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    print(f"{args.theme}  起点色相 {ramp['hue']}°  {n} 个状态取第 {', '.join(map(str, idx)) or '（不上色）'} 级")
    for mode in modes:
        bgs = list(grounds(args.theme, data, mode).values())
        print(f"  {mode}  底 {' '.join(f'{k}={v}' for k, v in grounds(args.theme, data, mode).items())}")
        prev = None
        for item in out[mode]:
            c = item["color"]
            ratio = worst_contrast(c, bgs)
            l, ch, h = oklch(c)
            d = f"  ΔE×100 {delta_e(prev, c):.2f}" if prev else ""
            print(f"    stage-{item['stage']}  {c}  标签底 {item['tint']}  最低对比 {ratio:.2f}:1  L {l:.3f} C {ch:.3f} H {h:.0f}{d}")
            prev = c
    return 0


def cmd_check(args) -> int:
    colors = [c.strip() for c in args.colors.split(",") if c.strip()]
    bgs = [c.strip() for c in args.bg.split(",") if c.strip()]
    if len(colors) < 2:
        print("错误：至少两个颜色才谈得上色阶", file=sys.stderr)
        return 2
    try:
        rules = check(colors, bgs, args.mode, tint_surface=bgs[0] if args.tint else None, cvd=args.cvd)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    failed = False
    for label, ok, note in rules:
        failed = failed or not ok
        print(f"  {'PASS' if ok else 'FAIL'} {label:44} {note}")
    print("FAIL" if failed else "PASS")
    return 1 if failed else 0


def cmd_themes(args) -> int:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    ids = [args.theme] if args.theme else list(data["themes"])
    changed = 0
    for tid in ids:
        if tid not in data["themes"]:
            print(f"错误：主题 {tid} 不在 themes.json 里", file=sys.stderr)
            return 2
        want = theme_ramp(tid, data)
        have = data["themes"][tid].get("stage")
        if have != want:
            changed += 1
            print(f"{'更新' if args.write else '不一致'} {tid}")
            if args.write:
                data["themes"][tid]["stage"] = want
        else:
            print(f"一致 {tid}")
    if args.write and changed:
        write_stage(data)
        print(f"已写 {THEMES}")
    return 1 if (changed and not args.write and args.check) else 0


def write_stage(data: dict) -> None:
    """themes.json 按它现有的换行方式（与 make_dark 一致：缩进 2，CRLF）整份重写，每个主题的 stage 排在 dark 之后。"""
    crlf = b"\r\n" in THEMES.read_bytes()
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if crlf:
        text = text.replace("\n", "\r\n")
    THEMES.write_bytes(text.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="输出一个主题 N 级的色阶（浅色与深色）")
    m.add_argument("--theme", required=True)
    m.add_argument("--n", type=int, default=STOPS, help="有序状态的个数；2 到 6 取等间隔的 N 级，大于 6 分成 6 档")
    m.add_argument("--mode", choices=("light", "dark"))
    m.add_argument("--json", action="store_true")
    c = sub.add_parser("check", help="校验一组有序颜色")
    c.add_argument("--colors", required=True, help="先到后的十六进制色，逗号分隔")
    c.add_argument("--bg", required=True, help="文字会落在的底色，逗号分隔（浅色：卡片与页面底；深色：各层深色底）")
    c.add_argument("--mode", choices=("light", "dark"), default="light")
    c.add_argument("--tint", action="store_true", help="同时核对自己的浅底标签（本色混入第一个底色）")
    c.add_argument("--cvd", action="store_true", help="同时核对色觉缺陷模拟下相邻两级仍可分辨")
    t = sub.add_parser("themes", help="themes.json 的 stage 与算法逐项核对")
    t.add_argument("--theme")
    t.add_argument("--write", action="store_true", help="把算法结果写进 themes.json")
    t.add_argument("--check", action="store_true", help="不一致时退出码 1")
    args = ap.parse_args(argv)
    return {"make": cmd_make, "check": cmd_check, "themes": cmd_themes}[args.cmd](args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
