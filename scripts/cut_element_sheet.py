#!/usr/bin/env python3
"""Cut a 4×4 transparent element sheet into single objects (visual-design.html 图像生成, 4×4 拼板切图).

  py -X utf8 scripts/cut_element_sheet.py <sheet.png> <out_dir> <name1> … <name16>

Each cell drops faint specks and pieces of neighbouring cells, keeps the object's connected parts, trims with 6% padding,
scales to 240 px (twice a 120 px display) and is saved as <out_dir>/<name>.webp. Names are given in reading order;
fewer than 16 names cut only the first cells. A cell with nothing left after cleaning is reported and skipped.
Requires Pillow and numpy (pip install pillow numpy).
"""
from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

SIZE = 240
PADDING = 0.06
ALPHA_FLOOR = 48
MIN_PART = 0.01


def cut_cell(cell, np, Image):
    """Return the cleaned, padded and scaled object of one cell, or None when the cell is empty."""
    px = np.array(cell)
    alpha = px[:, :, 3].copy()
    alpha[alpha < ALPHA_FLOOR] = 0
    mask = alpha > 0
    if not mask.any():
        return None, 0
    labels = np.zeros(mask.shape, dtype=np.int32)
    sizes = [0]
    current = 0
    for y, x in zip(*np.nonzero(mask)):
        if labels[y, x]:
            continue
        current += 1
        size = 0
        queue = deque([(y, x)])
        labels[y, x] = current
        while queue:
            cy, cx = queue.popleft()
            size += 1
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not labels[ny, nx]:
                    labels[ny, nx] = current
                    queue.append((ny, nx))
        sizes.append(size)
    largest = max(sizes)
    main_part = sizes.index(largest)
    # Pieces cut off a neighbouring object touch the cell edge; only the object itself may.
    edge = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    keep = {i for i, s in enumerate(sizes) if i and s >= largest * MIN_PART and (i == main_part or i not in edge)}
    alpha[~np.isin(labels, list(keep))] = 0
    px[:, :, 3] = alpha
    ys, xs = np.nonzero(alpha)
    if not len(ys):
        return None, 0
    obj = Image.fromarray(px).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    side = max(obj.size)
    pad = round(side * PADDING)
    canvas = Image.new("RGBA", (side + 2 * pad, side + 2 * pad), (0, 0, 0, 0))
    canvas.paste(obj, ((canvas.width - obj.width) // 2, (canvas.height - obj.height) // 2), obj)
    return canvas.resize((SIZE, SIZE), Image.LANCZOS), len(keep)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet", help="the 4×4 element sheet (transparent PNG)")
    parser.add_argument("out_dir", help="folder for the cut WebP files")
    parser.add_argument("names", nargs="+", help="1–16 object names in reading order; each becomes <name>.webp")
    args = parser.parse_args(argv)
    if len(args.names) > 16:
        parser.error("a 4×4 sheet holds at most 16 objects")
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("FAIL: cut_element_sheet.py needs Pillow and numpy: pip install pillow numpy", file=sys.stderr)
        return 1
    sheet = Path(args.sheet)
    if not sheet.is_file():
        print(f"FAIL: sheet not found: {sheet}", file=sys.stderr)
        return 1
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    image = Image.open(sheet).convert("RGBA")
    cw, ch = image.size[0] / 4, image.size[1] / 4
    empty = 0
    for index, name in enumerate(args.names):
        row, col = divmod(index, 4)
        cell = image.crop((round(col * cw), round(row * ch), round((col + 1) * cw), round((row + 1) * ch)))
        result, parts = cut_cell(cell, np, Image)
        if result is None:
            empty += 1
            print(f"EMPTY {name}: cell {index + 1} has no object after cleaning; regenerate it")
            continue
        target = out / f"{name}.webp"
        result.save(target, "WEBP", quality=82, method=6)
        print(name, target.stat().st_size, "bytes", "parts", parts)
    return 1 if empty else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
