#!/usr/bin/env python3
"""Bring icon images that fail check_icon_image.py inside its limits, and keep a set of icons to a few hues, without redrawing them (no image service, nothing billed).

    py -X utf8 scripts/soften_icon_image.py <icon image | folder> [more paths] [-r] [--hues 3] [--margin 0.03] [--write]

Two moves, both at constant lightness and constant alpha (HSB, so shapes, shading, highlights and the transparent edge stay as drawn):

* saturation  S' = k x S, k chosen per image by bisection so the encoded image (what is stored, not the float result) ends ``--margin`` under every limit of
  check_icon_image.py (mean, 90th percentile, share of over-saturated pixels). An image that already passes is left alone.
* hues        with ``--hues N`` (the rule: a screen of icon blocks keeps to 3 hues, references/image-assets.md), the hues of one folder are pooled, N centres are found
  on the hue circle (k-means weighted by how much saturated area each hue has) and every coloured pixel takes the hue of its nearest centre. The set then reads as
  one family told apart by shape, which is what the rule asks for.

Without ``--write`` it only prints the plan and what the result would measure; with it, every file is rewritten in its own format (WebP quality 92, alpha lossless;
PNG as PNG). Calibration of the limits themselves is not done here (references/image-assets.md): this tool only gets images inside the limits that are in force.
"""
from __future__ import annotations

import argparse
import io
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_icon_image as cii  # noqa: E402

QUALITY = 92
WEBP_METHOD_SEARCH = 4          # fast while searching, the final write uses method 6


def rgb_to_hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0.0)
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4))
    return np.where(d == 0, 0.0, h) * 60.0, s, mx


def hsv_to_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    h6 = (h % 360.0) / 60.0
    c = v * s
    x = c * (1 - np.abs(h6 % 2 - 1))
    m = v - c
    z = np.zeros_like(h6)
    i = np.floor(h6).astype(int) % 6
    r = np.choose(i, [c, x, z, z, x, c])
    g = np.choose(i, [x, c, c, x, z, z])
    b = np.choose(i, [z, z, x, c, c, x])
    return np.stack([r + m, g + m, b + m], -1)


def load(path: Path) -> Image.Image:
    im = Image.open(path)
    im.load()
    return im.convert("RGBA")


def transform(im: Image.Image, k: float = 1.0, centres: list[float] | None = None) -> Image.Image:
    """S x k at constant H, V and alpha; with centres, the hue of every coloured pixel moves to the nearest centre."""
    a = np.asarray(im.convert("RGBA")).astype(float)
    h, s, v = rgb_to_hsv(a[..., :3] / 255)
    if centres:
        coloured = (s >= cii.CHROMA_S) & (a[..., 3] >= cii.DEFAULTS["alpha_min"]) & (v > cii.BLACK_V)
        cs = np.array(centres)
        diff = np.abs(((h[..., None] - cs[None, None, :]) + 180) % 360 - 180)
        h = np.where(coloured, cs[diff.argmin(-1)], h)
    out = hsv_to_rgb(h, np.clip(s * k, 0, 1), v)
    rgba = np.concatenate([np.clip(np.round(out * 255), 0, 255), a[..., 3:]], -1).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def encode(im: Image.Image, fmt: str, method: int = 6) -> bytes:
    buf = io.BytesIO()
    if fmt == "WEBP":
        im.save(buf, "WEBP", quality=QUALITY, method=method, alpha_quality=100)
    else:
        im.save(buf, fmt)
    return buf.getvalue()


def decode(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGBA")


def targets(margin: float, limits: dict | None = None) -> dict:
    lim = dict(cii.DEFAULTS if limits is None else limits)
    return {"mean": lim["max_mean"] - margin, "p90": lim["p90"] - margin, "hot": lim["hot_share"] / 3, "hues": lim["max_hues"]}


def inside(m: cii.Metrics, tgt: dict) -> bool:
    return m.mean <= tgt["mean"] and m.p90 <= tgt["p90"] and m.hot_share <= tgt["hot"] and len(m.hues) <= tgt["hues"]


def fit(im: Image.Image, fmt: str, tgt: dict, centres: list[float] | None = None) -> float:
    """The largest k (closest to the original) whose *encoded* result is inside the targets; 1.0 when the image needs nothing."""
    base = decode(encode(transform(im, 1.0, centres), fmt, WEBP_METHOD_SEARCH))
    if inside(cii.analyze_image(base), tgt):
        return 1.0
    lo, hi = 0.05, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        if inside(cii.analyze_image(decode(encode(transform(im, mid, centres), fmt, WEBP_METHOD_SEARCH))), tgt):
            lo = mid
        else:
            hi = mid
    k = round(lo, 3)
    while k > 0.05 and not inside(cii.analyze_image(decode(encode(transform(im, k, centres), fmt))), tgt):
        k = round(k - 0.005, 3)         # the final write encodes with method 6: re-check on that
    return k


def hue_histogram(im: Image.Image) -> np.ndarray:
    """36 bins of coloured area, with the same pixels check_icon_image counts."""
    a = np.asarray(im.convert("RGBA")).astype(float)
    h, s, v = rgb_to_hsv(a[..., :3] / 255)
    keep = (a[..., 3] >= cii.DEFAULTS["alpha_min"]) & (v > cii.BLACK_V) & (s >= cii.CHROMA_S) & ~((v >= cii.WHITE_V) & (s <= cii.WHITE_S))
    counts = np.bincount((h[keep] // cii.HUE_BIN).astype(int) % (360 // cii.HUE_BIN), minlength=360 // cii.HUE_BIN)
    return counts.astype(float)


def set_hue_families(images: list[Image.Image]) -> list[tuple[int, float]]:
    """The hue families of a set of icons shown together (check_icon_image's grouping on the pooled histogram)."""
    pooled = sum(hue_histogram(im) for im in images) if images else np.zeros(360 // cii.HUE_BIN)
    return cii.hue_families([float(x) for x in pooled])


def hue_centres(images: list[Image.Image], n: int) -> list[float]:
    """n centres on the hue circle for the pooled coloured area (weighted circular k-means, farthest-point start)."""
    hist = sum(hue_histogram(im) for im in images)
    degs = (np.arange(len(hist)) + 0.5) * cii.HUE_BIN
    if hist.sum() <= 0:
        return []
    centres = [float(degs[int(hist.argmax())])]
    while len(centres) < min(n, int((hist > 0).sum())):
        dist = np.min(np.abs(((degs[:, None] - np.array(centres)[None, :]) + 180) % 360 - 180), axis=1) * (hist > 0)
        centres.append(float(degs[int((dist * np.sqrt(hist)).argmax())]))
    for _ in range(40):
        diff = ((degs[:, None] - np.array(centres)[None, :]) + 180) % 360 - 180
        owner = np.abs(diff).argmin(1)
        moved = []
        for j, c in enumerate(centres):
            w = hist * (owner == j)
            if w.sum() <= 0:
                moved.append(c)
                continue
            moved.append(float((c + (w * diff[:, j]).sum() / w.sum()) % 360))
        if max(abs(((a - b) + 180) % 360 - 180) for a, b in zip(moved, centres)) < 0.2:
            centres = moved
            break
        centres = moved
    return sorted(centres)


def plan(paths: list[Path], hues: int | None, margin: float) -> list[dict]:
    """Per folder: pool the hues, then per file the k. Returns one record per file."""
    out: list[dict] = []
    by_dir: dict[Path, list[Path]] = {}
    for p in paths:
        by_dir.setdefault(p.parent, []).append(p)
    tgt = targets(margin)
    for folder, files in sorted(by_dir.items()):
        ims = {f: load(f) for f in files}
        before_set = set_hue_families(list(ims.values()))
        centres = hue_centres(list(ims.values()), hues) if hues and len(before_set) > hues else None
        for f in files:
            fmt = "WEBP" if f.suffix.lower() == ".webp" else "PNG"
            k = fit(ims[f], fmt, tgt, centres)
            out.append({"path": f, "format": fmt, "k": k, "centres": centres, "before_set": before_set, "image": ims[f]})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-r", "--recursive", action="store_true")
    ap.add_argument("--hues", type=int, help="keep every folder of icons to this many hues (the rule is 3)")
    ap.add_argument("--margin", type=float, default=0.03, help="stay this far under the mean and 90th percentile limits (default 0.03)")
    ap.add_argument("--write", action="store_true", help="rewrite the files (default: print the plan)")
    args = ap.parse_args(argv)
    files = [p for p in cii.collect(args.paths, args.recursive) if p.suffix.lower() in {".webp", ".png"}]
    if not files:
        print("no webp or png images found", file=sys.stderr)
        return 2
    rows = plan(files, args.hues, args.margin)
    for r in rows:
        data = encode(transform(r["image"], r["k"], r["centres"]), r["format"])
        m = cii.analyze_image(decode(data))
        note = f"k {r['k']:.3f}" + ("  hues snapped to " + "/".join(f"{c:.0f}" for c in r["centres"]) if r["centres"] else "")
        print(f"{r['path']}  {note}  -> mean {m.mean:.2f} p90 {m.p90:.2f} hot {m.hot_share:.1%} hues {len(m.hues)}")
        if args.write and (r["k"] != 1.0 or r["centres"]):
            r["path"].write_bytes(data)
    print("written" if args.write else "dry run (add --write to rewrite the files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
