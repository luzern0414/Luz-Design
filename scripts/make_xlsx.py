"""Read the rule card first: py -X utf8 scripts/context.py xlsx

Build a styled single-sheet spreadsheet that follows file-design.html (表格文件).

    py -X utf8 scripts/make_xlsx.py spec.json out.xlsx

spec.json:
{
  "title": "门店月度客流",                 # row 1, the only text outside the table: black, bold, centred on the header colour, body + 4 pt (16 pt)
  "subtitle": "",                          # retained for empty legacy specifications only; no explanatory subtitle
  "theme": "coffee",                       # accepted for compatibility; every sheet uses the standard look (宋体, black text, pale fills, thin black borders)
  "font": "宋体",                          # optional: 宋体 (default) or 微软雅黑; one family for the whole workbook
  "font_size": 12,                         # optional body size, 10-14 pt (default 12); the title is body + 4 pt
  "tint_by": "功能模块",                   # optional: every value of this column gets one of six pale fills, in order of first appearance, over the whole row
  "highlight": {"column": "类型", "values": ["可选"]},   # optional: rows whose value is listed get the amber highlight on their data cells
  "group_by": ["区域", "门店"],            # optional: grouping columns, biggest group first; moved to the front, rows sorted, cells merged
  "sheet": "月度客流",                     # optional, defaults to the title (max 12 chars)
  "columns": [
    {"name": "区域", "merge": true},       # merge: equal consecutive values merge vertically
    {"name": "门店", "merge": true},       # a child column only merges inside its parent's group
    {"name": "月份", "type": "text"},
    {"name": "到店人次", "type": "number"},
    {"name": "环比", "type": "percent"},
    {"name": "备注", "type": "longtext"},
    {"name": "类型", "tags": ["基础", "可选"]}   # tags: these values are shown bold; their colour is the row fill (tint_by, highlight), text stays black
  ],
  "rows": [["区域甲", "门店甲", "9 月", "<人次>", "<环比>", ""], ...],      # your own data; the builder never supplies a number
  "total": {"label": "到店人次合计", "sum": ["到店人次"]}   # optional, formulas; a summary row is a 合计/小计/总计 label, which --allow quote releases (see estimate)
  "footer": [{"label": "基础功能小计", "values": {"<列名>": "<人工提供的数>"}}]   # optional summary rows under the table: the label
                                             # (it must say 合计, 小计 or 总计) spans the columns left of the first value
  "freeze": 3,                               # optional: columns to freeze; default = leading group-name columns
  "estimate": {                              # optional and OFF by default: workday columns and amounts exist only when the project asked for them in words
    "workdays": true, "quote": true,         # quote needs workdays; both need the evidence below, a missing field stops the build
    "requested_by": "<谁要求的>", "request_note": "<要求的原话>",
    "provided_by": "<提供数字的人：姓名或角色>", "evidence": "<提供数字的原话或来源文件，如 uploads/客户报价单.xlsx>"   # provided_by / evidence: quote only
  },
  "allow_quote": false,                      # the short form (the hardware list exporter): true needs "quote_evidence": {"requested_by": "<谁要求的>", "request_note": "<原话>"}
                                             # (optionally provided_by / evidence: a person, or the source link of a reference price); without evidence nothing is released
}

Estimate policy (预算、人日与报价政策; file-design.html 表格文件 › 工时、金额与报价): a spreadsheet lists functions and facts. Columns, rows or sheets for
工时 / 人天 / 金额 / 单价 / 小计 / 合计 / 报价 exist only when "estimate" turns them on with evidence; every price, discount and amount is typed by a person (the
quotation they supplied), never filled in by the agent, never an example or a 暂估, and nothing in this skill ships a default one. Without "estimate" (or allow_quote with its evidence), the
document checker reports any such header or summary label as an error; a 合计 counts as money only beside a currency (a sum of amperes or devices does not),
and the evidence is written into the workbook's description ("报价依据：…") because the checker, which only sees the file, asks for it. The words are data in estimate_terms.py. Workdays an agent estimates are marked 拟定 until the person approves the file.

Column types: text (default; the first one that names the row is bold and left, other short columns are centred; a column whose
longest value is over 16 units, 8 Chinese characters, is treated as longtext so one column never mixes centred and left-aligned text),
longtext (left with one indent, wraps), money (#,##0.00, right), days (0.0, right), number (#,##0), decimal (#,##0.00), percent (0.0%),
date (yyyy-mm-dd); numbers sit right with one indent so they line up by digit; the
header is always centred (file-design.html 表格文件 › 列宽、对齐与格式). Leading text columns that repeat are merged
automatically when "merge" is not given. No sequence-number column is ever added.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from document_palette import table_tint
import xlsx_metrics as M

FONTS = ("宋体", "微软雅黑")
FONT = FONTS[0]
# The look: 宋体, every text black, colour only as pale fills, thin black borders.
INK = "000000"
LINE = "000000"
HEAD_FILL = "ECF0F6"            # title and header rows: a clear blue-grey
BAND_FILL = "F4F7FA"            # section bands, sub-totals and groups that span several categories
GRAND_FILL = "ECF0F6"           # the grand total row
HIGHLIGHT_FILL = "FFE699"       # what needs a second look: optional or new items
TINTS = ("EEF4FB", "EFF8F1", "FEF7EC", "F4F0FA", "FDF1F0", "F8F8F8")      # blue, green, orange, purple, pink, grey: one per category, in turn
SIZES = {"title": 16, "subtitle": 12, "header": 12, "body": 12}
FORMATS = {"money": "#,##0.00", "number": "#,##0", "decimal": "#,##0.00", "days": "0.0", "percent": "0.0%", "date": "yyyy-mm-dd"}
# Names and long text read from the left, numbers compare by digit from the right, short values centre (visual-design.html 表格对齐).
HORIZONTAL = {"longtext": "left", "money": "right", "decimal": "right", "days": "right", "number": "right", "percent": "right"}
INDENTED = {"longtext", "money", "decimal", "days", "number", "percent"}
SEQ_NAMES = {"序号", "编号序号", "行号", "#", "no", "no.", "序"}


# Width of a formula cell is the width of what it shows, not of the formula text.
FORMULA_SAMPLE = {"percent": "100.0%", "money": 999999.99, "decimal": 9999.99, "days": 999.9, "number": "99,999", "date": "2026-10-29", "text": "—"}


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


def arrange_groups(spec: dict) -> dict:
    """``"group_by": ["使用端", "使用角色", "功能模块"]``: those columns move to the front in that order (biggest group first), rows are
    sorted so every group is one contiguous block (groups keep the order in which they first appear), and the columns are merged."""
    names = list(spec.get("group_by") or [])
    if not names:
        return spec
    cols = spec["columns"]
    index = {c["name"]: i for i, c in enumerate(cols)}
    missing = [n for n in names if n not in index]
    if missing:
        raise ValueError(f"group_by names columns that do not exist: {missing}")
    order = [index[n] for n in names] + [i for i in range(len(cols)) if i not in {index[n] for n in names}]
    ranks = []
    for n in names:
        first: dict = {}
        for row in spec["rows"]:
            first.setdefault(row[index[n]], len(first))
        ranks.append(first)
    keyed = sorted(range(len(spec["rows"])), key=lambda r: tuple(ranks[k][spec["rows"][r][index[n]]] for k, n in enumerate(names)))
    out = dict(spec)
    out["columns"] = [dict(cols[i], **({"merge": True} if i in {index[n] for n in names} else {})) for i in order]
    out["rows"] = [[spec["rows"][r][i] if i < len(spec["rows"][r]) else None for i in order] for r in keyed]
    out.pop("group_by", None)
    return out


def build(spec: dict, out: Path, *, context=None, session=None, stage=None) -> Path:
    """Business writer: validate evidence and the exact template before bytes."""
    from design_output_gate import require_output_context, record_rendered_output
    out = Path(out)
    context = require_output_context(out, "xlsx", context=context, session=session, stage=stage)
    result = _render_workbook(spec, out)
    record_rendered_output(context, out, "xlsx", generator="Luz-Design/scripts/make_xlsx.py")
    return result


def _render_workbook(spec: dict, out: Path) -> Path:
    """One sheet from ``spec``; or several when ``spec["sheets"]`` lists them (each sheet spec adds to the shared title, theme,
    font_size). Several sheets are only for content the user asked to split by purpose; each one is a complete table."""
    from openpyxl import Workbook

    evidence = estimate_evidence(spec)           # a switch without its evidence stops here, before any file is written
    wb = Workbook()
    if evidence:
        wb.properties.description = evidence
    if spec.get("sheets"):
        shared = {k: v for k, v in spec.items() if k != "sheets"}
        for k, sheet in enumerate(spec["sheets"]):
            _build_one({**shared, **sheet}, wb, k == 0)
    else:
        _build_one(spec, wb, True)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def _build_one(spec: dict, wb, first: bool) -> None:
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    spec = arrange_groups(spec)
    if spec.get("subtitle"):
        raise ValueError("表格标题下禁止说明性副标题；请将真实业务字段放入数据区")
    body_pt = float(spec.get("font_size", SIZES["body"]))
    if not 10 <= body_pt <= 14:
        raise ValueError("font_size must be 10-14 pt")
    family = spec.get("font", FONT)
    if family not in FONTS:
        raise ValueError(f"font must be one of {FONTS}")
    sizes = {"title": body_pt + 4, "subtitle": body_pt, "header": body_pt, "body": body_pt}

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
    for k in range(n):  # one alignment per column: long values anywhere make the whole column long text
        if types[k] == "text" and k not in merge_cols and max([M.display_width(r[k]) for r in rows if k < len(r) and not str(r[k] or "").startswith("=")] + [0]) > 16:
            types[k] = "longtext"

    wb._named_styles["Normal"].font = Font(name=family, size=sizes["body"], color=INK)
    ws = wb.active if first else wb.create_sheet()
    ws.title = (spec.get("sheet") or spec["title"])[:12]
    thin = Side(style="thin", color=LINE)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def font(size, bold=False, color=INK):
        return Font(name=family, size=size, bold=bold, color=color)

    def fill(color):
        return PatternFill("solid", fgColor=color)

    ws.cell(1, 1, spec["title"]).font = font(sizes["title"], True)
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(1, 1).fill = fill(HEAD_FILL)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
    ws.row_dimensions[1].height = round(sizes["title"] * 2.4)
    ws.row_dimensions[2].height = 8
    hr = 3
    for k, c in enumerate(columns, 1):
        cell = ws.cell(hr, k, c["name"])
        cell.font = font(sizes["header"], True)
        cell.fill = fill(HEAD_FILL)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    ws.row_dimensions[hr].height = 24

    name_col = next((k for k in range(n) if k not in merge_cols and types[k] in ("text", "longtext")), None)     # the column that names the row reads from the left
    names_all = [c["name"] for c in columns]
    tint_col = names_all.index(spec["tint_by"]) if spec.get("tint_by") in names_all else None
    tints: dict = {}
    if tint_col is not None:
        for r in rows:
            tints.setdefault(r[tint_col], TINTS[len(tints) % len(TINTS)])       # each category its own pale colour, in turn
    light = spec.get("highlight") or {}
    light_col = names_all.index(light["column"]) if light.get("column") in names_all else None
    first = hr + 1
    for i, r in enumerate(rows):
        for k, v in enumerate(r):
            if isinstance(v, str) and types[k] == "date":
                try:
                    v = datetime.strptime(v, "%Y-%m-%d").date()
                except ValueError:
                    pass
            cell = ws.cell(first + i, k + 1, v)
            tag = isinstance(v, str) and v in (columns[k].get("tags") or ())                    # a tag value reads bold; its colour is the row fill
            cell.font = font(sizes["body"], bool(tag))
            cell.border = border
            if tint_col is not None:
                cell.fill = fill(tints[r[tint_col]])
            if light_col is not None and r[light_col] in (light.get("values") or ()) and k not in merge_cols:
                cell.fill = fill(HIGHLIGHT_FILL)
            if types[k] in FORMATS:
                cell.number_format = FORMATS[types[k]]
            wraps = not M.is_numeric_type(types[k])
            left = k == name_col                                                         # the name column reads from the left like the long text
            cell.alignment = Alignment(horizontal="left" if left else HORIZONTAL.get(types[k], "center"), vertical="center", wrap_text=wraps,
                                       indent=1 if (left or types[k] in INDENTED) else 0)

    # Vertical merges, hierarchical: a child column merges only inside its parent's run.
    bounds = [(0, len(rows) - 1)] if rows else []
    top_groups: list[tuple[int, int]] = []
    for depth, k in enumerate(merge_cols):
        runs = merge_runs(rows, k, bounds)
        if depth == 0:
            top_groups = runs
        for g, (a, b) in enumerate(runs):
            cell = ws.cell(first + a, k + 1)
            span = {tints[r[tint_col]] for r in rows[a:b + 1]} if tint_col is not None else set()
            color = next(iter(span)) if len(span) == 1 else BAND_FILL        # a group inside one category takes its colour, a bigger group the band colour
            for rr in range(first + a, first + b + 1):
                ws.cell(rr, k + 1).fill = fill(color)
                ws.cell(rr, k + 1).border = border
            cell.font = font(sizes["body"], depth == 0)                      # the biggest group reads bold, centred, merged down its rows
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            if b > a:
                ws.merge_cells(start_row=first + a, start_column=k + 1, end_row=first + b, end_column=k + 1)
        bounds = runs

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
            cell.font = font(sizes["body"], True)
            cell.fill = fill(GRAND_FILL)
            cell.border = border
            numeric = k - 1 < len(types) and M.is_numeric_type(types[k - 1]) and k > len(merge_cols)
            cell.alignment = Alignment(horizontal="right" if numeric else "left", vertical="center", indent=1)
        if merge_cols:
            ws.merge_cells(start_row=tr, start_column=1, end_row=tr, end_column=len(merge_cols))
        last = tr

    names = [c["name"] for c in columns]
    for item in spec.get("footer", []):
        if not any(word in item["label"] for word in ("合计", "小计", "总计")):
            raise ValueError(f"footer label must say 合计, 小计 or 总计: {item['label']!r}")
        tr = last + 1
        values = {names.index(name): v for name, v in item["values"].items()}
        span = min(values) if values else n          # the label runs across every column left of the first value
        ws.cell(tr, 1, item["label"])
        for k, v in values.items():
            cell = ws.cell(tr, k + 1, v)
            if types[k] in FORMATS:
                cell.number_format = FORMATS[types[k]]
        grand = any(word in item["label"] for word in ("合计", "总计"))        # 小计 sits on the band colour, the grand total on the header colour
        for k in range(n):
            cell = ws.cell(tr, k + 1)
            cell.font = font(sizes["body"], True)
            cell.fill = fill(GRAND_FILL if grand else BAND_FILL)
            cell.border = border
            if k == 0 or types[k] not in HORIZONTAL:
                cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            else:
                cell.alignment = Alignment(horizontal=HORIZONTAL[types[k]], vertical="center", indent=1)
        if span > 1:
            ws.merge_cells(start_row=tr, start_column=1, end_row=tr, end_column=span)
        ws.row_dimensions[tr].height = M.row_height(1, sizes["body"])
        last = tr

    # Column widths from content (CJK counts double); row heights from the same metrics the checker uses.
    for k in range(n):
        values = [columns[k]["name"]] + [FORMULA_SAMPLE.get(types[k], "99,999") if isinstance(v, str) and v.startswith("=") else v for v in (r[k] for r in rows)]
        widest = max(M.display_width(v if types[k] not in ("money", "decimal") else f"{v:,.2f}" if isinstance(v, (int, float)) else v) for v in (str(x).split("\n")[0] if isinstance(x, str) else x for x in values))
        longest_line = max((max(M.display_width(part) for part in str(v).split("\n")) for v in values if v not in (None, "")), default=0)
        width = max(widest, longest_line) + 4
        width += 2 if (types[k] in INDENTED or k == name_col) else 0  # one indent level
        cap = 54 if types[k] == "longtext" else 30
        ws.column_dimensions[get_column_letter(k + 1)].width = max(10, min(cap, width))
    widths = [ws.column_dimensions[get_column_letter(k + 1)].width for k in range(n)]
    header_lines = max(M.wrapped_lines(c["name"], widths[k]) for k, c in enumerate(columns))
    ws.row_dimensions[hr].height = M.row_height(header_lines, sizes["header"])
    spanned = {(rng.min_row, rng.min_col) for rng in ws.merged_cells.ranges if rng.max_row > rng.min_row}      # group cells merged down several rows
    inside = {(r, rng.min_col) for rng in ws.merged_cells.ranges if rng.max_row > rng.min_row for r in range(rng.min_row, rng.max_row + 1)}
    for i, r in enumerate(rows):
        lines = 1
        for k, v in enumerate(r):
            if k in merge_cols and (first + i, k + 1) in inside:
                continue   # a group name merged over several rows is sized by the whole span below, not by each row
            if v and not M.is_numeric_type(types[k]) and not (isinstance(v, str) and v.startswith("=")):
                lines = max(lines, M.wrapped_lines(v, widths[k], 1 if (types[k] in INDENTED or k == name_col or k in merge_cols) else 0))
        ws.row_dimensions[first + i].height = M.row_height(lines, sizes["body"])
    # A vertically merged group cell must fit in the rows it spans.
    for rng in list(ws.merged_cells.ranges):
        if rng.max_row > rng.min_row and rng.min_row >= first and rng.min_col == rng.max_col:
            text = ws.cell(rng.min_row, rng.min_col).value
            need = M.row_height(M.wrapped_lines(text, widths[rng.min_col - 1], 1), sizes["body"])
            have = sum(ws.row_dimensions[r].height or 0 for r in range(rng.min_row, rng.max_row + 1))
            if have < need:
                ws.row_dimensions[rng.max_row].height = (ws.row_dimensions[rng.max_row].height or 0) + (need - have)

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
    total_width = sum(ws.column_dimensions[get_column_letter(k + 1)].width or 10 for k in range(n))
    ws.page_setup.orientation = "landscape" if total_width > 100 else "portrait"      # the reference prints landscape: wide tables stay readable at 12 pt
    ws.page_setup.paperSize = 9                                      # A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.6
    ws.oddFooter.center.text = "第 &P 页 / 共 &N 页"
    ws.oddFooter.center.size = 9


def estimate_block(spec: dict) -> dict:
    """The switch of the 预算、人日与报价政策 in a spec, in one shape. Two ways to write it: ``estimate`` (workdays, quote, requested_by, request_note, provided_by, evidence),
    or ``allow_quote: true`` with ``quote_evidence: {requested_by, request_note[, provided_by, evidence]}`` (the form the hardware list exporter uses)."""
    est = dict(spec.get("estimate") or {})
    if spec.get("allow_quote"):
        proof = spec.get("quote_evidence")
        if not isinstance(proof, dict):
            raise ValueError("allow_quote needs quote_evidence: {requested_by: who asked, request_note: their words}; without evidence nothing is released")
        est = {**proof, "workdays": True, "quote": True, **{k: v for k, v in est.items() if k not in ("workdays", "quote")}}
    return est


def estimate_allow(spec: dict) -> list[str]:
    """The ``--allow`` kinds the spec earns (预算、人日与报价政策). Off by default; on only with the evidence, and a price only from a person."""
    import estimate_terms as et
    est = estimate_block(spec)
    if not est or not (est.get("workdays") or est.get("quote")):
        return []
    missing = [k for k in ("requested_by", "request_note") if not str(est.get(k) or "").strip()]
    if missing:
        raise ValueError(f"estimate is switched on without its evidence: {', '.join(missing)} (who asked, and their words); workdays and amounts stay off until someone asked")
    if et.not_a_person(str(est["requested_by"])):
        raise ValueError(f"estimate.requested_by {est['requested_by']!r} is not a person: the agent, a skill, a tool or an example cannot be the one who asked")
    if et.is_not_evidence(str(est["request_note"])):
        raise ValueError(f"estimate.request_note {est['request_note']!r} is no evidence: write the words of the person who asked, not a placeholder")
    if est.get("quote") and not est.get("workdays"):
        raise ValueError("estimate.quote needs estimate.workdays: a quotation is built on workdays")
    if est.get("quote"):
        strict = bool(spec.get("estimate"))        # the estimate block names the figures' source; allow_quote with quote_evidence may carry reference prices with a source link
        for key in (("provided_by", "evidence") if strict else ()):
            if not str(est.get(key) or "").strip():
                raise ValueError(f"estimate.quote needs {key}: the figures must come from a quotation a person supplied (who, and where it is written down)")
        if est.get("evidence") and et.says_made_up(str(est["evidence"])):
            raise ValueError(f"estimate.evidence {est['evidence']!r} says the figures are an estimate, made up or a default: they must come from a quotation a person supplied")
        if est.get("evidence") and et.is_not_evidence(str(est["evidence"])):
            raise ValueError(f"estimate.evidence {est['evidence']!r} is no evidence: write what the person said or where the quotation is written down")
        if est.get("provided_by") and et.not_a_person(str(est["provided_by"])):
            raise ValueError(f"estimate.provided_by {est['provided_by']!r} is not a person: the agent, a skill, a tool, an example or an estimate cannot supply a price")
        return ["quote"]
    return ["workdays"]


def estimate_evidence(spec: dict) -> str:
    """The text the workbook carries for its switch ('' when the switch is off)."""
    import estimate_terms as et
    if not estimate_allow(spec):
        return ""
    est = estimate_block(spec)
    return et.evidence_text(str(est["requested_by"]), str(est["request_note"]), str(est.get("provided_by") or ""), str(est.get("evidence") or ""))


def verify_output(out: Path, kind: str, multi: bool = False, allow: list[str] | None = None) -> int:
    """Run the document checker on what was just written; a builder never hands over a file that fails it."""
    import check_document
    print(f"rule card for this file: py -X utf8 scripts/context.py {kind}  (read it before writing the spec)", file=sys.stderr)
    argv = [str(out)] + (["--allow", "multi-sheet"] if multi else [])
    for kind_allowed in allow or []:
        argv += ["--allow", kind_allowed]
    code = check_document.main(argv)
    if code:
        print(f"FAIL: {out.name} does not meet the {kind} rules above; fix the spec and build again", file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("spec")
    parser.add_argument("output")
    parser.add_argument("--session", help="Design session; otherwise inferred from environment or output path")
    args = parser.parse_args(argv)
    from design_output_gate import require_output_context, record_rendered_output
    try:
        context = require_output_context(args.output, "xlsx", session=args.session)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    try:
        allow = estimate_allow(spec)
    except ValueError as err:
        print(f"ERROR {err}", file=sys.stderr)
        return 2
    out = build(spec, Path(args.output), context=context)
    print("wrote", out)
    code = verify_output(out, "xlsx", bool(spec.get("sheets")), allow)
    if code == 0:
        record_rendered_output(context, out, "xlsx", generator="Luz-Design/scripts/make_xlsx.py")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
