"""Read the rule card first: py -X utf8 scripts/context.py xlsx

Build a styled single-sheet spreadsheet that follows file-design.html (表格文件).

    py -X utf8 scripts/make_xlsx.py spec.json out.xlsx

spec.json:
{
  "title": "门店月度销售",                 # row 1, the only text outside the table
  "sheet": "月度销售",                     # optional, defaults to the title (max 12 chars)
  "columns": [
    {"name": "区域", "merge": true},       # merge: equal consecutive values merge vertically
    {"name": "门店", "merge": true},       # a child column only merges inside its parent's group
    {"name": "月份", "type": "text"},
    {"name": "销售额（元）", "type": "money"},
    {"name": "环比", "type": "percent"},
    {"name": "备注", "type": "longtext"}
  ],
  "rows": [["华南", "科技园店", "9 月", 128000, 0.052, ""], ...],
  "total": {"label": "合计", "sum": ["销售额（元）"]}   # optional, formulas
  "freeze": 3                                # optional: columns to freeze; default = leading group-name columns
}

Column types: text (default, centred), longtext (left, wraps), money (#,##0.00), number (#,##0),
decimal (#,##0.00), percent (0.0%), date (yyyy-mm-dd). Leading text columns that repeat are merged
automatically when "merge" is not given. No sequence-number column is ever added.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

FONT = "微软雅黑"
INK = "262626"
LINE = "E8E8E8"
HEADER_FILL = "E6F4FF"          # 拂晓蓝第 1 阶：表头浅底
TOTAL_FILL = "F5F5F5"           # 中性灰第 2 阶：合计行
BAND_FILL = "FAFAFA"            # 中性灰第 1 阶：相邻分组交替底色
GROUP_FILLS = ["E6F4FF", "F6FFED", "FFF7E6", "F9F0FF", "E6FFFB", "FFF0F6"]  # 官方色板各色第 1 阶，分组单元格轮换
SIZES = {"title": 18, "header": 12, "body": 12}
FORMATS = {"money": "#,##0.00", "number": "#,##0", "decimal": "#,##0.00", "percent": "0.0%", "date": "yyyy-mm-dd"}
SEQ_NAMES = {"序号", "编号序号", "行号", "#", "no", "no.", "序"}


# Width of a formula cell is the width of what it shows, not of the formula text.
FORMULA_SAMPLE = {"percent": "100.0%", "money": 999999.99, "decimal": 9999.99, "number": "99,999", "date": "2026-10-29", "text": "—"}


def display_width(value) -> int:
    text = "" if value is None else str(value)
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def merge_runs(rows: list[list], col: int, parent_bounds: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Runs of equal non-empty values in one column, never crossing a parent group's boundary."""
    runs = []
    for start, end in parent_bounds:
        i = start
        while i <= end:
            j = i
            while j + 1 <= end and rows[j + 1][col] == rows[i][col] and rows[i][col] not in (None, ""):
                j += 1
            runs.append((i, j))
            i = j + 1
    return runs


def build(spec: dict, out: Path) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    columns = [c for c in spec["columns"] if str(c["name"]).strip().lower() not in SEQ_NAMES]
    keep = [i for i, c in enumerate(spec["columns"]) if str(c["name"]).strip().lower() not in SEQ_NAMES]
    rows = [[r[i] if i < len(r) else None for i in keep] for r in spec["rows"]]
    n = len(columns)
    types = [c.get("type", "text") for c in columns]

    # Columns to merge: explicit flags, otherwise the leading text columns that repeat.
    flags = [c.get("merge") for c in columns]
    if not any(f is not None for f in flags):
        flags = []
        for k, t in enumerate(types):
            repeats = any(rows[i][k] == rows[i + 1][k] and rows[i][k] not in (None, "") for i in range(len(rows) - 1))
            if t in ("text",) and repeats and (k == 0 or flags[-1]):
                flags.append(True)
            else:
                break
        flags += [False] * (n - len(flags))
    merge_cols = [k for k in range(n) if flags[k]]

    wb = Workbook()
    ws = wb.active
    ws.title = (spec.get("sheet") or spec["title"])[:12]
    thin = Side(style="thin", color=LINE)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def font(size, bold=False):
        return Font(name=FONT, size=size, bold=bold, color=INK)

    ws.cell(1, 1, spec["title"]).font = font(SIZES["title"], True)
    ws.cell(1, 1).alignment = Alignment(horizontal="left", vertical="center")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
    ws.row_dimensions[1].height = 36
    ws.row_dimensions[2].height = 10
    hr = 3
    for k, c in enumerate(columns, 1):
        cell = ws.cell(hr, k, c["name"])
        cell.font = font(SIZES["header"], True)
        cell.fill = PatternFill("solid", fgColor=HEADER_FILL)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    ws.row_dimensions[hr].height = 30

    first = hr + 1
    for i, r in enumerate(rows):
        for k, v in enumerate(r):
            if isinstance(v, str) and types[k] == "date":
                try:
                    v = datetime.strptime(v, "%Y-%m-%d").date()
                except ValueError:
                    pass
            cell = ws.cell(first + i, k + 1, v)
            cell.font = font(SIZES["body"])
            cell.border = border
            if types[k] in FORMATS:
                cell.number_format = FORMATS[types[k]]
            long = types[k] == "longtext"
            cell.alignment = Alignment(horizontal="left" if long else "center", vertical="center", wrap_text=long, indent=1 if long else 0)

    # Vertical merges, hierarchical: a child column merges only inside its parent's run.
    bounds = [(0, len(rows) - 1)] if rows else []
    top_groups: list[tuple[int, int]] = []
    for depth, k in enumerate(merge_cols):
        runs = merge_runs(rows, k, bounds)
        if depth == 0:
            top_groups = runs
        for g, (a, b) in enumerate(runs):
            cell = ws.cell(first + a, k + 1)
            if depth == 0:
                cell.fill = PatternFill("solid", fgColor=GROUP_FILLS[g % len(GROUP_FILLS)])
            cell.font = font(SIZES["body"], depth == 0)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            if b > a:
                ws.merge_cells(start_row=first + a, start_column=k + 1, end_row=first + b, end_column=k + 1)
        bounds = runs
    # Light banding by top-level group so each group reads as one block.
    for g, (a, b) in enumerate(top_groups):
        if g % 2:
            for i in range(a, b + 1):
                for k in range(n):
                    if k not in merge_cols[:1]:
                        ws.cell(first + i, k + 1).fill = PatternFill("solid", fgColor=BAND_FILL)

    last = first + len(rows) - 1
    total = spec.get("total")
    if total and rows:
        tr = last + 1
        label_col = 1
        ws.cell(tr, label_col, total.get("label", "合计"))
        for name in total.get("sum", []):
            k = [c["name"] for c in columns].index(name) + 1
            letter = get_column_letter(k)
            ws.cell(tr, k, f"=SUM({letter}{first}:{letter}{last})").number_format = FORMATS.get(types[k - 1], "#,##0.00")
        for k in range(1, n + 1):
            cell = ws.cell(tr, k)
            cell.font = font(SIZES["body"], True)
            cell.fill = PatternFill("solid", fgColor=TOTAL_FILL)
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
        if merge_cols:
            ws.merge_cells(start_row=tr, start_column=1, end_row=tr, end_column=len(merge_cols))
        last = tr

    # Column widths from content (CJK counts double), row heights for wrapped text.
    for k in range(n):
        values = [columns[k]["name"]] + [FORMULA_SAMPLE.get(types[k], "99,999") if isinstance(v, str) and v.startswith("=") else v for v in (r[k] for r in rows)]
        width = max(display_width(v if types[k] not in ("money", "decimal") else f"{v:,.2f}" if isinstance(v, (int, float)) else v) for v in values) + 4
        width += 2 if types[k] == "longtext" else 0  # one indent level
        cap = 40 if types[k] == "longtext" else 30
        ws.column_dimensions[get_column_letter(k + 1)].width = max(10, min(cap, width))
    for i, r in enumerate(rows):
        lines = 1
        for k, v in enumerate(r):
            if types[k] == "longtext" and v:
                cap = ws.column_dimensions[get_column_letter(k + 1)].width - 4  # padding and indent
                lines = max(lines, -(-display_width(v) // max(cap, 1)))
        ws.row_dimensions[first + i].height = max(24, 18 * lines + 6)

    ws.sheet_view.showGridLines = False
    freeze = spec.get("freeze")
    if freeze is None:
        freeze = 0
        while freeze in merge_cols and types[freeze] == "text":
            freeze += 1  # group names only; merged group-level numbers scroll with the data
    ws.freeze_panes = ws.cell(first, int(freeze) + 1)
    if len(rows) > 20 and not merge_cols:
        ws.auto_filter.ref = f"A{hr}:{get_column_letter(n)}{first + len(rows) - 1}"
    ws.print_area = f"A1:{get_column_letter(n)}{last}"
    ws.print_title_rows = f"{hr}:{hr}"
    ws.page_setup.orientation = "landscape" if n > 8 else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def verify_output(out: Path, kind: str) -> int:
    """Run the document checker on what was just written; a builder never hands over a file that fails it."""
    import check_document
    print(f"rule card for this file: py -X utf8 scripts/context.py {kind}  (read it before writing the spec)", file=sys.stderr)
    code = check_document.main([str(out)])
    if code:
        print(f"FAIL: {out.name} does not meet the {kind} rules above; fix the spec and build again", file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out = build(spec, Path(argv[1]))
    print("wrote", out)
    return verify_output(out, "xlsx")


if __name__ == "__main__":
    raise SystemExit(main())
