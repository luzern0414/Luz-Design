"""Build the component template library into one HTML file: every component has a fixed id (MP-CARD-003, AD-TBL-001 ...).

Reads this directory only (``src/`` for the code, ``assets/`` for the WebP images) and writes one self-contained file.

  py -X utf8 references/component-library/build.py [--out FILE] [--files blocks-ad-table.js,blocks-mp-basic.js]

``--out`` defaults to ``dist/component-library.html`` next to this script (git-ignored). ``--files`` builds the library with only the
named ``blocks-*.js`` files (plus the 52 earlier templates in blocks1-3.js); the environment variables ``LIB_OUT`` and ``LIB_FILES`` do the
same for scripts that cannot pass arguments.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
ASSETS = HERE / "assets"
ICON_STYLES = ("3d", "real", "flat")
ICON_NAMES = ("giftbox", "scooter", "coupon", "bag", "heart", "star", "pin", "cart", "giftcard", "wallet")
SLOTS = ("KIT_CSS", "IX_CSS", "ASSETS", "KIT_JS", "TAXONOMY", "CORE_DEF", "IX", "BLOCKS_JS", "COMBO", "CORE_UI")


def data_uri(path: Path) -> str:
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def assets_js() -> str:
    """The ``ASSETS`` constant the library reads: icons by style, nine product pictures, two backgrounds."""
    icons = {style: {name: data_uri(ASSETS / "icons" / style / f"{name}.webp") for name in ICON_NAMES} for style in ICON_STYLES}
    prod = [data_uri(ASSETS / "products" / f"p{i}.webp") for i in range(9)]
    bg = {name: data_uri(ASSETS / "bg" / f"{name}.webp") for name in ("silk", "interior")}
    return "const ASSETS=" + json.dumps({"icons": icons, "prod": prod, "bg": bg}, ensure_ascii=False, separators=(",", ":"))


def read(name: str) -> str:
    return (SRC / name).read_text(encoding="utf-8")


def block_files(only: list[str] | None = None) -> list[Path]:
    return [p for p in sorted(SRC.glob("blocks-*.js")) if not only or p.name in only]


def build(out: Path, only: list[str] | None = None) -> tuple[Path, list[str]]:
    files = block_files(only)
    legacy = "\n".join(read(f) for f in ("blocks1.js", "blocks2.js", "blocks3.js"))
    extra = ";\n".join(p.read_text(encoding="utf-8") for p in files)
    parts = {
        "KIT_CSS": read("kit.css"),
        "IX_CSS": read("ix.css"),
        "ASSETS": assets_js(),
        "KIT_JS": read("kit.js"),
        "TAXONOMY": read("taxonomy.js"),
        "CORE_DEF": read("core-def.js") + "\n" + read("extras.js"),
        "IX": read("ix.js"),
        "BLOCKS_JS": legacy + ";\n" + extra,
        "COMBO": read("combo.js"),
        "CORE_UI": read("core-ui.js"),
    }
    page = read("lib.template.html")
    for slot in SLOTS:
        page = page.replace(f"/*__{slot}__*/", parts[slot])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out, [p.name for p in files]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", help="output file (default dist/component-library.html next to this script)")
    parser.add_argument("--files", help="comma-separated blocks-*.js names to include (default all)")
    args = parser.parse_args(argv)
    out = Path(args.out or os.environ.get("LIB_OUT") or HERE / "dist" / "component-library.html")
    only = [x.strip() for x in (args.files or os.environ.get("LIB_FILES") or "").split(",") if x.strip()]
    target, files = build(out, only)
    print(target, round(target.stat().st_size / 1024), "KB", "blocks files:", files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
