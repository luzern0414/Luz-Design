#!/usr/bin/env python3
"""Build the component template library, and write its id index.

    py -X utf8 scripts/build_component_library.py [--out FILE] [--files blocks-ad-table.js,blocks-mp-basic.js]
    py -X utf8 scripts/build_component_library.py --index            # write references/component-library/registry/index.md
    py -X utf8 scripts/build_component_library.py --index --check    # exit 1 when the committed index differs from the source

Without ``--index`` this wraps ``references/component-library/build.py`` (one self-contained HTML file, default ``references/component-library/dist/component-library.html``).
``--index`` reads the source statically (the same reader as check_component_library.py, no browser): one table per category with id, name, style, fit and avoid,
sections in the order of taxonomy.js. The file is committed, so it is generated and never edited by hand.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_component_library as lib  # noqa: E402

LIB_DIR = lib.LIB
INDEX = LIB_DIR / "registry" / "index.md"
DOMAIN = {"mp": ("MP", "小程序"), "ad": ("AD", "后台管理")}


def load_builder():
    spec = importlib.util.spec_from_file_location("component_library_build", LIB_DIR / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cell(text: str | None) -> str:
    return " ".join((text or "").split()).replace("|", "\\|")


def render_index(src: Path = lib.SRC) -> str:
    """The Markdown index of every component, from the source."""
    library = lib.read_library(src)
    comps = sorted(library.comps, key=lambda c: (c.dom, c.cat, c.num))
    total = len(comps)
    counts = {dom: sum(1 for c in comps if c.dom == dom) for dom in DOMAIN}
    out = [
        "# 组件编号索引",
        "",
        f"由 `scripts/build_component_library.py --index` 从 `references/component-library/src/` 生成，不要手改。共 {total} 个：" + "，".join(f"{DOMAIN[d][1]} {counts[d]}" for d in DOMAIN) + "。",
        "",
        "编号写法 `域-类别-三位序号`，如 `MP-CARD-003`、`AD-TBL-001`，一经发出不改、不复用。用法、取用要点和新增规则见 [README](../README.md)，开发规范见 [SPEC](../src/SPEC.md)。",
        "",
    ]
    for dom, (code, title) in DOMAIN.items():
        out += [f"## {title} {code}（{counts[dom]}）", ""]
        for cat, cat_title in library.cats[dom]:
            rows = [c for c in comps if c.dom == dom and c.cat == cat]
            if not rows:
                continue
            out += [f"### {code}-{cat} {cat_title}（{len(rows)}）", "", "| 编号 | 名称 | 风格 | 适合 | 避免 |", "|---|---|---|---|---|"]
            out += [f"| {c.id} | {cell(c.name)} | {cell(c.style)} | {cell(c.fit)} | {cell(c.avoid)} |" for c in rows]
            out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def write_index(path: Path = INDEX) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_index())
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", help="output HTML (default references/component-library/dist/component-library.html)")
    ap.add_argument("--files", help="comma-separated blocks-*.js names to include (default all)")
    ap.add_argument("--index", action="store_true", help="write registry/index.md instead of building the HTML")
    ap.add_argument("--check", action="store_true", help="with --index: do not write, exit 1 when the committed index is out of date")
    a = ap.parse_args(argv)
    if a.index:
        if a.check:
            current = INDEX.read_bytes().decode("utf-8") if INDEX.is_file() else ""
            if current != render_index():
                print("registry/index.md is out of date: run scripts/build_component_library.py --index")
                return 1
            print("registry/index.md: up to date")
            return 0
        print(write_index())
        return 0
    builder = load_builder()
    out = Path(a.out) if a.out else LIB_DIR / "dist" / "component-library.html"
    only = [x.strip() for x in (a.files or "").split(",") if x.strip()]
    target, files = builder.build(out, only)
    print(target, round(target.stat().st_size / 1024), "KB", "blocks files:", files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
