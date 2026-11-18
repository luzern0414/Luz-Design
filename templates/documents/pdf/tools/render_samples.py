"""重新生成 samples 里的 PDF 样例（模板库内部用，只作版式参考）。

    py -X utf8 tools/render_samples.py [编号 …] [--out 目录] [--work 过程目录]

样例由技能生成器的内部函数合成：
  DC-PD-001 表格目录   make_table_pdf 的分词、分页、导出与检查函数（Edge 导出）
  DC-PD-002 系统图册   showcase.build + make_showcase.export_pdf（Edge 导出，逐页占满率检查）
  DC-PD-003 方案       make_docx_paginated._render_paginated（WPS 文字或 Word 排版并导出 PDF）
  DC-PD-004 报告       tools/md_to_pdf.py（Markdown 来源，阅读页样式，Edge 导出）
它们不经过正式命令的“前置检索与模板选择”门禁，也不写门禁记录：样例只是版式参考，不是客户成品。
正式交付必须走 make_table_pdf.py、make_showcase.py、make_docx_paginated.py 的正式命令与门禁，再用 check_pdf.py 核对。
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
import make_docx_paginated as paginated  # noqa: E402
import make_showcase  # noqa: E402
import make_table_pdf as table_pdf  # noqa: E402
import md_to_pdf  # noqa: E402
import showcase  # noqa: E402


def render_table(spec: dict, pdf: Path, work: Path) -> int:
    src = work / (pdf.stem + ".html")
    labels = [r["label"] for s in spec["sections"] for r in (list(s.get("rows", [])) + [r for g in s.get("groups", []) for r in g["rows"]])]
    table_pdf.WORDS.clear()
    table_pdf.segment(table_pdf.cell_texts(spec) + labels, spec.get("keep_together", []))
    src.write_text(table_pdf.build_html(spec), encoding="utf-8")
    table_pdf.paginate_html(src)
    rc = check_document.main([str(src)])
    table_pdf.export_pdf(src, pdf, table_pdf.theme_tokens(spec["theme"])["ink2"])
    errors = table_pdf.check_pdf(pdf, spec.get("max_pages"))
    for e in errors:
        print("ERROR", e)
    return int(bool(rc or errors))


def render_atlas(spec: dict, pdf: Path, work: Path) -> int:
    problems = showcase.validate_spec(spec)
    for p in problems:
        print("SPEC", p)
    html_path = work / (pdf.stem + ".html")
    html_path.write_text(showcase.build(spec), encoding="utf-8")
    rc = check_document.main([str(html_path), "--allow", "showcase"])
    errors, warnings, report = make_showcase.export_pdf(html_path, pdf, spec.get("orientation", "portrait"), 0.75,
                                                        spec["title"], bool(spec.get("cover")), header=False)
    errors += table_pdf.check_pdf(pdf, None)
    print("page fill:", ", ".join(f"{p['page']}:{p['fill']:.0%}" for p in report["pages"]))
    for e in errors:
        print("ERROR", e)
    return int(bool(rc or errors or problems))


def render_word_pdf(spec: dict, pdf: Path, work: Path) -> int:
    docx = work / (pdf.stem + ".docx")
    paginated._render_paginated(spec, docx)         # writes the PDF next to the .docx, which is the file the sample keeps
    return 0


def render(spec_path: Path, out_dir: Path, work: Path) -> int:
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    out_dir.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    pdf = work / (spec_path.stem + ".pdf")          # the generators leave HTML and overview images beside the PDF: keep them in the work folder
    if spec.get("source"):
        rc = md_to_pdf.build(spec_path, pdf, work)
    elif spec.get("style") == "atlas":
        rc = render_atlas(spec, pdf, work)
    elif spec.get("type") == "proposal":
        rc = render_word_pdf(spec, pdf, work)
    else:
        rc = render_table(spec, pdf, work)
    if pdf.is_file():
        import check_pdf
        final = out_dir / pdf.name
        shutil.copy2(pdf, final)
        print("wrote", final)
        rc |= check_pdf.main([str(final)])
    return int(bool(rc))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*", help="编号，如 DC-PD-001；不写则全部")
    ap.add_argument("--out", type=Path, default=ROOT / "samples")
    ap.add_argument("--work", type=Path, help="过程文件目录，默认用临时目录")
    args = ap.parse_args(argv)
    rc = 0
    with tempfile.TemporaryDirectory() as tmp:
        work = args.work or Path(tmp)
        for spec_path in sorted((ROOT / "specs").glob("DC-PD-0*.json")):
            if args.ids and not any(spec_path.name.startswith(i) for i in args.ids):
                continue
            rc |= render(spec_path, args.out, work)
    return rc


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
