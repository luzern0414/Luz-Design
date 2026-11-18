"""样例表格的后处理：数据验证、填写格底色、条件色块。

make_xlsx.py 目前不支持这三项（规则卡写了：数据验证限制可输入值，需要客户填写的格用极浅米黄 FFF8E1，条件格式只用浅底标识状态）。
本脚本读 spec 里的 "decorate" 键（make_xlsx 会忽略它），在已生成的工作簿上补上，只用于技能自带的版式样例。
正式交付必须把这三项并入 make_xlsx 的渲染函数：生成器在写完文件后登记哈希，事后再改文件会使登记失效。

  py -X utf8 templates/documents/excel/tools/xlsx_decorate.py spec.json 已生成.xlsx

decorate（可放在整份 spec，也可放在 sheets 里的某个工作表）：
  {"input_columns": ["单价（元）"],                                    # 这些列的数据行铺极浅米黄 FFF8E1：需要人填写的格
   "validations": [{"column": "数量", "type": "whole", "min": 0},      # whole 整数、decimal 小数（min、max 可选）
                   {"column": "验收结果", "type": "list", "values": ["通过", "未通过", "待验收"]}],   # list 下拉
   "status_colors": [{"column": "验收结果", "colors": {"通过": "DFF2E4", "未通过": "F9D9D6", "待验收": "FFE699"}}]}   # 条件格式，只改底色，文字仍是黑色；多列同一套色用 "columns": [列名…]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FILL_IN = "FFF8E1"
SUMMARY_WORDS = ("合计", "小计", "总计")


def _columns(ws, header_row: int) -> dict[str, int]:
    return {str(c.value).strip(): c.column for c in ws[header_row] if c.value not in (None, "")}


def _data_range(ws, header_row: int) -> tuple[int, int]:
    first = header_row + 1
    last = ws.max_row
    for r in range(first, ws.max_row + 1):
        value = ws.cell(r, 1).value
        if isinstance(value, str) and any(w in value for w in SUMMARY_WORDS):
            last = r - 1
            break
    return first, last


def decorate_sheet(ws, decorate: dict) -> None:
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    header_row = 3
    cols = _columns(ws, header_row)
    first, last = _data_range(ws, header_row)
    if last < first:
        return
    for name in decorate.get("input_columns", []):
        col = cols[name]
        for r in range(first, last + 1):
            ws.cell(r, col).fill = PatternFill("solid", fgColor=FILL_IN)
    for rule in decorate.get("validations", []):
        col = get_column_letter(cols[rule["column"]])
        ref = f"{col}{first}:{col}{last}"
        kind = rule["type"]
        if kind == "list":
            dv = DataValidation(type="list", formula1='"' + ",".join(rule["values"]) + '"', allow_blank=True)
            dv.errorTitle, dv.error = "不在可选范围", "请从列表中选择"
        elif kind in ("whole", "decimal"):
            lo, hi = rule.get("min"), rule.get("max")
            if lo is not None and hi is not None:
                dv = DataValidation(type=kind, operator="between", formula1=str(lo), formula2=str(hi), allow_blank=True)
            elif lo is not None:
                dv = DataValidation(type=kind, operator="greaterThanOrEqual", formula1=str(lo), allow_blank=True)
            else:
                dv = DataValidation(type=kind, operator="lessThanOrEqual", formula1=str(hi), allow_blank=True)
            dv.errorTitle, dv.error = "数值不合法", "请输入符合范围的数值"
        else:
            raise ValueError(f"unknown validation type {kind!r}")
        dv.showErrorMessage = True
        ws.add_data_validation(dv)
        dv.add(ref)
    for rule in decorate.get("status_colors", []):
        names = rule.get("columns") or [rule["column"]]
        for name in names:
            col = get_column_letter(cols[name])
            ref = f"{col}{first}:{col}{last}"
            for value, color in rule["colors"].items():
                fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
                ws.conditional_formatting.add(ref, CellIsRule(operator="equal", formula=[f'"{value}"'], fill=fill))


def decorate_workbook(spec: dict, path: Path) -> None:
    from openpyxl import load_workbook

    wb = load_workbook(path)
    if spec.get("sheets"):
        for ws, sheet in zip(wb.worksheets, spec["sheets"]):
            if sheet.get("decorate"):
                decorate_sheet(ws, sheet["decorate"])
    elif spec.get("decorate"):
        decorate_sheet(wb.active, spec["decorate"])
    wb.save(path)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    decorate_workbook(json.loads(Path(argv[0]).read_text(encoding="utf-8")), Path(argv[1]))
    print("decorated", argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
