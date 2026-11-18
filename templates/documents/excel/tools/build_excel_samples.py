"""把 templates/documents/excel/specs/*.json 渲染成 samples/*.xlsx（技能自带的版式参考，不是客户成品）。

  py -X utf8 templates/documents/excel/tools/build_excel_samples.py [--only DC-XL-001] [--specs <目录>] [--out <目录>]

样例直接调用 make_xlsx 的内部渲染函数 _render_workbook（正式命令 make_xlsx.py 与公开 build 需要会话与前置检索门禁，样例不走门禁也不登记），
再用 xlsx_decorate.py 补数据验证、填写格底色、条件色块，最后跑 check_document。正式交付必须走 make_xlsx.py 与门禁。
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # templates/documents/excel/tools
ROOT = HERE.parents[3]                                 # the skill root (Luz-Design)
DESIGN_SCRIPTS = ROOT / "scripts" if (ROOT / "scripts" / "make_xlsx.py").is_file() else Path("D:/Codes/Luz-Design/scripts")
sys.path.insert(0, str(DESIGN_SCRIPTS))
sys.path.insert(0, str(HERE))

import check_document  # noqa: E402
import make_xlsx  # noqa: E402
import xlsx_decorate  # noqa: E402


def build_one(spec_path: Path, out_dir: Path) -> tuple[Path, int, str]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = out_dir / (spec_path.stem + ".xlsx")
    make_xlsx._render_workbook(spec, out)
    xlsx_decorate.decorate_workbook(spec, out)
    allow = make_xlsx.estimate_allow(spec)
    argv = [str(out)] + (["--allow", "multi-sheet"] if spec.get("sheets") else [])
    for kind in allow:
        argv += ["--allow", kind]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = check_document.main(argv)
    return out, code, buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只做某个编号，如 DC-XL-001")
    ap.add_argument("--specs", default=str(HERE.parent / "specs"))
    ap.add_argument("--out", default=str(HERE.parent / "samples"))
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    failed = 0
    for path in sorted(Path(args.specs).glob("DC-XL-*.json")):
        if args.only and not path.stem.startswith(args.only):
            continue
        out, code, report = build_one(path, out_dir)
        print(report.strip().splitlines()[0] if report.strip() else f"{out.name}: no output")
        for line in report.strip().splitlines()[1:]:
            if line.strip().startswith(("ERROR", "WARN")):
                print(line)
        failed += code
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
