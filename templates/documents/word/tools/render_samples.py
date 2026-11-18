"""重新生成 samples 里的 Word 样例（模板库内部用，只作版式参考）。

    py -X utf8 tools/render_samples.py [编号 …] [--out 目录] [--check]

样例由技能生成器的内部渲染函数合成：
  带封面与目录的客户正式文档  make_docx_paginated._render_paginated（WPS 文字或 Word 排版，回填目录页码与续表，并导出同名 PDF）
  合同、纪要、制度、报价函      make_docx._render_document
  公文                         make_docx._render_document，再用 tools/official_post.py 调整公文版式
它们不经过正式命令的“前置检索与模板选择”门禁，也不写门禁记录：样例只是版式参考，不是客户成品。
正式交付必须走 py -X utf8 scripts/make_docx.py 或 make_docx_paginated.py 的正式命令与门禁。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
_CANDIDATES = [Path(os.environ["LUZ_DESIGN_SCRIPTS"])] if os.environ.get("LUZ_DESIGN_SCRIPTS") else []
_CANDIDATES += [HERE.parents[3] / "scripts", Path(r"D:/Codes/Luz-Design/scripts")]
SCRIPTS = next(p for p in _CANDIDATES if (p / "make_docx.py").is_file())
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))

import check_document  # noqa: E402
import make_docx  # noqa: E402
import make_docx_paginated as paginated  # noqa: E402
from official_post import apply_official  # noqa: E402


def render(spec_path: Path, out_dir: Path, check: bool) -> int:
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        docx = Path(tmp) / (spec_path.stem + ".docx")
        if spec.get("cover") or spec.get("toc"):
            paginated._render_paginated(spec, docx)
        else:
            make_docx._render_document(spec, docx)
            if spec.get("official"):
                apply_official(docx, spec)
        final = out_dir / docx.name
        shutil.copy2(docx, final)
    print("wrote", final)
    if not check:
        return 0
    allow: list[str] = []
    if spec.get("style") == "paper" and spec.get("type") != "contract":
        allow = ["--allow", "paper"]
    if spec.get("official"):
        allow = ["--allow", "official", "--allow", "cover"]
    if spec.get("cover"):
        allow += ["--allow", "cover", "--allow", "header"]
    return check_document.main(allow + [str(final)])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*", help="编号，如 DC-WD-001；不写则全部")
    ap.add_argument("--out", type=Path, default=ROOT / "samples")
    ap.add_argument("--check", action="store_true", help="生成后运行 check_document.py")
    args = ap.parse_args(argv)
    rc = 0
    for spec_path in sorted((ROOT / "specs").glob("DC-WD-0*.json")):
        if args.ids and not any(spec_path.name.startswith(i) for i in args.ids):
            continue
        rc |= render(spec_path, args.out, args.check)
    return rc


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
