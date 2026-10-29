"""usage: py -X utf8 scripts/cut_element_sheet.py <sheet.png> <out_dir> <name1> … <name16>

Cut a 4x4 transparent element sheet into single objects: drop faint specks, keep the object's connected parts,
trim with 6% padding, scale to 240 px and save WebP (Luz-Design visual-design.html 图像生成, 4×4 拼板切图)."""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

sheet, out_dir, *names = sys.argv[1:]
out = Path(out_dir)
out.mkdir(parents=True, exist_ok=True)
image = Image.open(sheet).convert("RGBA")
w, h = image.size
cw, ch = w / 4, h / 4
for index, name in enumerate(names):
    row, col = divmod(index, 4)
    cell = image.crop((round(col * cw), round(row * ch), round((col + 1) * cw), round((row + 1) * ch)))
    px = np.array(cell)
    alpha = px[:, :, 3].copy()
    alpha[alpha < 48] = 0
    mask = alpha > 0
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
    main = sizes.index(largest)
    # Pieces cut off a neighbouring object touch the cell edge; only the object itself may.
    edge = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    keep = {i for i, s in enumerate(sizes) if i and s >= largest * 0.01 and (i == main or i not in edge)}
    keep_mask = np.isin(labels, list(keep))
    alpha[~keep_mask] = 0
    px[:, :, 3] = alpha
    ys, xs = np.nonzero(alpha)
    top, bottom, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    obj = Image.fromarray(px).crop((left, top, right + 1, bottom + 1))
    side = max(obj.size)
    pad = round(side * 0.06)
    canvas = Image.new("RGBA", (side + 2 * pad, side + 2 * pad), (0, 0, 0, 0))
    canvas.paste(obj, ((canvas.width - obj.width) // 2, (canvas.height - obj.height) // 2), obj)
    canvas = canvas.resize((240, 240), Image.LANCZOS)
    target = out / f"{name}.webp"
    canvas.save(target, "WEBP", quality=82, method=6)
    print(name, target.stat().st_size, "bytes", "parts", len(keep))
