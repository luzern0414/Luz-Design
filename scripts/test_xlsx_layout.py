"""Spreadsheets: nothing clipped, one font, one alignment per column (the first things that look ugly in Excel)."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_document  # noqa: E402
import make_xlsx  # noqa: E402
import xlsx_metrics as M  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

SPEC = {
    "title": "客户信息表", "theme": "coffee", "sheet": "客户信息",
    "columns": [{"name": "分类", "merge": True}, {"name": "信息项"}, {"name": "说明", "type": "longtext"}, {"name": "可选项", "type": "longtext"}, {"name": "优先级"}],
    "rows": [
        ["账号", "「撤回未产生订单的菜单」是否包括已取消的订单", "需要停止供应时，由平台逐笔取消订单，并把原因写进备注，方便之后对账和追溯。", "A. 有过任何订单都不能撤回\nB. 只要没有有效订单就能撤回\nC. 其他", "必须"],
        ["账号", "AppID", "wx 开头的 18 位字符", "—", "建议"],
        ["规则", "对账周期", "按自然月结算", "A. 月结\nB. 半月结", "必须"],
    ],
}


class XlsxLayoutTests(unittest.TestCase):
    def build(self, tmp):
        out = Path(tmp) / "t.xlsx"
        make_xlsx.build(SPEC, out)
        return out

    def test_built_sheet_passes_and_text_is_not_clipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            self.assertEqual(check_document.main([str(out)]), 0)
            ws = load_workbook(out).active
            # the row holding four lines of options must be at least four lines tall
            self.assertGreaterEqual(ws.row_dimensions[4].height, M.row_height(3))

    def test_long_text_column_is_left_aligned_for_every_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = load_workbook(self.build(tmp)).active
            kinds = {ws.cell(r, 2).alignment.horizontal for r in (4, 5, 6)}
            self.assertEqual(kinds, {"left"})  # 信息项 holds a long name, so the whole column is left-aligned, not a mix

    def test_default_look_is_the_reference_workbook_song_black_pale_fills(self):
        with tempfile.TemporaryDirectory() as tmp:
            wb = load_workbook(self.build(tmp))
            ws = wb.active
            self.assertEqual(wb._named_styles["Normal"].font.name, "宋体")
            cells = [c for row in ws.iter_rows(min_row=1, max_row=6) for c in row if type(c).__name__ != "MergedCell" and c.value not in (None, "")]
            self.assertTrue(all(c.font.name == "宋体" for c in cells))
            self.assertTrue(all((c.font.color.rgb or "")[-6:] == "000000" for c in cells), "every text is black: colour is only the fill")
            self.assertEqual(ws["A1"].font.sz, 16)                                      # the title is body + 4 pt
            self.assertEqual({c.font.sz for c in cells if c.row > 1}, {12})              # one body size, headers included
            self.assertEqual(ws["A1"].alignment.horizontal, "center")
            self.assertEqual(ws["A1"].fill.fgColor.rgb[-6:], make_xlsx.HEAD_FILL)
            self.assertEqual(ws.cell(3, 1).fill.fgColor.rgb[-6:], make_xlsx.HEAD_FILL)    # the header row
            self.assertEqual(ws.cell(4, 1).border.left.color.rgb[-6:], "000000")         # thin black borders
            self.assertEqual(ws.cell(4, 1).alignment.horizontal, "center")              # the biggest group reads centred
            self.assertTrue(ws.cell(4, 1).font.b)

    def test_a_workbook_keeps_one_family_and_yahei_is_available_on_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "yahei.xlsx"
            make_xlsx.build({**SPEC, "font": "微软雅黑"}, out)
            wb = load_workbook(out)
            self.assertEqual(wb._named_styles["Normal"].font.name, "微软雅黑")
            self.assertEqual(check_document.main([str(out)]), 0)
            with self.assertRaises(ValueError):
                make_xlsx.build({**SPEC, "font": "Arial"}, Path(tmp) / "bad.xlsx")
            wb.active["C4"].font = __import__("openpyxl").styles.Font(name="宋体", size=12)       # a second family in one workbook
            mixed = Path(tmp) / "mixed.xlsx"
            wb.save(mixed)
            self.assertEqual(check_document.main([str(mixed)]), 1)

    def test_categories_get_their_own_pale_colour_and_special_rows_the_highlight(self):
        spec = {"title": "功能清单", "sheet": "功能清单", "tint_by": "功能模块", "highlight": {"column": "类型", "values": ["可选"]},
                "columns": [{"name": "使用端", "merge": True}, {"name": "功能模块", "merge": True}, {"name": "功能"}, {"name": "类型", "tags": ["基础", "可选"]}],
                "rows": [["小程序", "登录", "微信登录", "基础"], ["小程序", "登录", "绑定企业", "基础"], ["小程序", "订单", "我的订单", "基础"], ["小程序", "订单", "导出订单", "可选"],
                         ["小程序", "统计", "经营概览", "基础"], ["后台", "员工", "员工管理", "基础"]]}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.xlsx"
            make_xlsx.build(spec, out)
            self.assertEqual(check_document.main([str(out)]), 0)
            ws = load_workbook(out).active
            fill = lambda r, c: ws.cell(r, c).fill.fgColor.rgb[-6:]
            self.assertEqual(fill(4, 3), make_xlsx.TINTS[0])                              # 登录
            self.assertEqual(fill(5, 3), make_xlsx.TINTS[0])
            self.assertEqual(fill(6, 3), make_xlsx.TINTS[1])                              # 订单: the next colour
            self.assertEqual(fill(8, 3), make_xlsx.TINTS[2])                              # 统计
            self.assertEqual(fill(9, 3), make_xlsx.TINTS[3])                              # 员工
            self.assertEqual(len({fill(4, 3), fill(6, 3), fill(8, 3), fill(9, 3)}), 4, "neighbouring categories never share a colour")
            self.assertEqual(fill(7, 3), make_xlsx.HIGHLIGHT_FILL)                        # 可选 is highlighted on its data cells ...
            self.assertEqual(fill(7, 4), make_xlsx.HIGHLIGHT_FILL)
            self.assertEqual(fill(6, 2), make_xlsx.TINTS[1])                              # ... the merged module cell keeps its category colour
            self.assertEqual(fill(4, 1), make_xlsx.BAND_FILL)                             # 使用端 spans several categories: the band colour
            self.assertTrue(ws.cell(7, 4).font.b and not ws.cell(7, 3).font.b)            # the tag value reads bold
            self.assertEqual(ws.page_setup.orientation, "portrait")                      # a narrow table stays portrait
            wide = Path(tmp) / "wide.xlsx"
            make_xlsx.build(SPEC, wide)
            self.assertEqual(load_workbook(wide).active.page_setup.orientation, "landscape")   # a wide one prints landscape like the reference

    def test_checker_rejects_clipping_and_foreign_fonts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            wb = load_workbook(out)
            ws = wb.active
            ws.row_dimensions[4].height = 20
            from openpyxl.styles import Font
            ws["E5"].font = Font(name="Calibri", size=12)
            bad = Path(tmp) / "bad.xlsx"
            wb.save(bad)
            self.assertEqual(check_document.main([str(bad)]), 1)

    def test_mixed_alignment_in_one_column_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            wb = load_workbook(out)
            ws = wb.active
            from openpyxl.styles import Alignment
            ws["B5"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            bad = Path(tmp) / "mixed.xlsx"
            wb.save(bad)
            self.assertEqual(check_document.main([str(bad)]), 1)


class GroupOrderTests(unittest.TestCase):
    ROWS = [["FN-%02d" % i, "功能%d" % i, "端A" if i < 5 else "端B", "角色甲" if i < 3 else ("角色乙" if i < 5 else "角色丙"), "模块1" if i % 2 else "模块2", "说明%d" % i] for i in range(10)]

    def spec(self, columns, rows, **extra):
        return {"title": "清单", "theme": "coffee", "sheet": "清单", "columns": columns, "rows": rows, **extra}

    def test_group_by_moves_big_groups_first_sorts_and_merges(self):
        cols = [{"name": "编号"}, {"name": "功能"}, {"name": "使用端"}, {"name": "使用角色"}, {"name": "模块"}, {"name": "说明", "type": "longtext"}]
        arranged = make_xlsx.arrange_groups(self.spec(cols, self.ROWS, group_by=["使用端", "使用角色", "模块"]))
        self.assertEqual([c["name"] for c in arranged["columns"]][:4], ["使用端", "使用角色", "模块", "编号"])
        self.assertTrue(all(c.get("merge") for c in arranged["columns"][:3]))
        ends = [r[0] for r in arranged["rows"]]
        self.assertEqual(ends, sorted(ends, key=lambda v: ["端A", "端B"].index(v)))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "g.xlsx"
            make_xlsx.build(self.spec(cols, self.ROWS, group_by=["使用端", "使用角色", "模块"]), out)
            self.assertEqual(check_document.main([str(out)]), 0)

    def test_identifier_before_group_is_an_error(self):
        cols = [{"name": "编号"}, {"name": "功能"}, {"name": "使用端"}, {"name": "说明", "type": "longtext"}]
        rows = [["FN-%02d" % i, "功能%d" % i, "端A" if i < 6 else "端B", "说明%d" % i] for i in range(12)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bad.xlsx"
            make_xlsx.build(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 1)   # 使用端 follows the identifying column and is not merged

    def test_bigger_group_must_come_first(self):
        rows = [["端A", "角色%d" % (i // 2), "FN-%02d" % i, "说明%d" % i] for i in range(6)] + [["端B", "角色%d" % (3 + i // 2), "FN-%02d" % (6 + i), "说明%d" % (6 + i)] for i in range(6)]
        small_first = [[r[1], r[0], r[2], r[3]] for r in rows]
        cols = [{"name": "使用角色", "merge": True}, {"name": "使用端", "merge": True}, {"name": "编号"}, {"name": "说明", "type": "longtext"}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "order.xlsx"
            make_xlsx.build(self.spec(cols, small_first), out)
            self.assertEqual(check_document.main([str(out)]), 1)   # 6 role groups sit before 2 surface groups

    def test_change_ledger_in_time_order_has_no_grouping_column(self):
        # A ledger lists records by 变更编号; type, category and requester come in runs only because changes arrive in batches.
        cols = [{"name": "变更编号"}, {"name": "提出日期", "type": "date"}, {"name": "变更类型"}, {"name": "分类"}, {"name": "变更标题", "type": "longtext"},
                {"name": "提出人"}, {"name": "涉及阶段", "type": "longtext"}, {"name": "状态"}]
        rows = [["CHG-%03d" % (i + 1), "2026-11-03", "修改" if i < 3 else "新增", "规则" if i < 3 else "范围", "变更%d" % (i + 1),
                 "内部" if i < 3 else "客户", "client-intake" if i < 3 else "architecture", "待确认" if i < 3 else "已确认"] for i in range(8)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ledger.xlsx"
            make_xlsx.build(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 0)

    def test_identifier_first_table_that_is_not_a_ledger_still_fails(self):
        cols = [{"name": "编号"}, {"name": "提出日期", "type": "date"}, {"name": "变更类型"}, {"name": "分类"}, {"name": "变更标题", "type": "longtext"}]
        rows = [["CHG-%03d" % (i + 1), "2026-11-03", "修改" if i < 3 else "新增", "规则" if i < 3 else "范围", "变更%d" % (i + 1)] for i in range(8)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "notledger.xlsx"
            make_xlsx.build(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 1)

    def test_a_result_or_status_column_is_a_row_attribute_not_a_grouping_column(self):
        # Audit 014 (A-28): the 审核结果 column of a fill-in workbook (确认 / 需修改, in runs) was taken for a grouping column
        # after the identifying column. file-design.html: 类型、状态、优先级、必填、结果 describe one row and are never grouping columns.
        cols = [{"name": "分类", "merge": True}, {"name": "子类", "merge": True}, {"name": "业务逻辑"}, {"name": "拟定逻辑", "type": "longtext"}, {"name": "审核结果"}, {"name": "修改后的逻辑", "type": "longtext"}]
        rows = [["店长" if i < 6 else "收银员", "模块甲" if i < 3 else "模块乙" if i < 6 else "模块丙" if i < 9 else "模块丁", f"业务逻辑{i}", f"拟定逻辑{i}",
                 "确认" if i < 7 else "需修改", "" if i < 7 else f"修改后{i}"] for i in range(12)]
        for header in ("审核结果", "确认结果", "验收结果", "处理状态", "风险级别", "是否必填", "结果"):
            with self.subTest(header=header), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "fill.xlsx"
                make_xlsx.build(self.spec([*cols[:4], {**cols[4], "name": header}, cols[5]], rows), out)
                self.assertEqual(check_document.main([str(out)]), 0)

    def test_a_column_that_only_looks_like_a_result_is_still_a_grouping_column(self):
        # The exemption is the header's meaning, not the data: a group name that happens to sit after an identifier still fails.
        cols = [{"name": "编号"}, {"name": "功能"}, {"name": "结果页面"}, {"name": "说明", "type": "longtext"}]
        rows = [["FN-%02d" % i, "功能%d" % i, "页面A" if i < 6 else "页面B", "说明%d" % i] for i in range(12)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pages.xlsx"
            make_xlsx.build(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 1)

    def test_equal_text_across_a_parent_boundary_is_not_an_error(self):
        rows = [["端A", "角色甲", "模块1", "FN-1", "x"], ["端A", "角色甲", "模块1", "FN-2", "x"], ["端A", "角色乙", "模块1", "FN-3", "x"], ["端B", "角色丙", "模块1", "FN-4", "x"]]
        cols = [{"name": "使用端", "merge": True}, {"name": "使用角色", "merge": True}, {"name": "模块", "merge": True}, {"name": "编号"}, {"name": "说明"}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "boundary.xlsx"
            make_xlsx.build(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 0)


class MultiSheetTests(unittest.TestCase):
    """Two worksheets are for what the user or the document standard asks for (Luz-Project client documents 04 and 05)."""

    def build(self, tmp: str) -> Path:
        sheet = lambda name, col: {"sheet": name, "columns": [{"name": "功能"}, {"name": col, "type": "longtext"}], "rows": [[f"功能{i}", f"说明{i}"] for i in range(3)]}
        out = Path(tmp) / "two.xlsx"
        make_xlsx.build({"title": "功能清单", "theme": "coffee", "sheets": [sheet("功能清单", "功能说明"), sheet("报价清单", "报价说明")]}, out)
        return out

    def run_check(self, *argv: str) -> tuple[int, str]:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = check_document.main(list(argv))
        return code, buf.getvalue()

    def test_a_second_sheet_is_an_error_that_says_how_to_allow_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.run_check(str(self.build(tmp)))
            self.assertEqual(code, 1)
            self.assertIn("2 worksheets", out)
            self.assertIn("--allow-multi-sheet", out, "the message names the switch")
            self.assertIn("document standard prescribes", out, "and says that a standard-prescribed pair of sheets is the other reason besides the user's request")

    def test_the_switch_lets_the_two_sheet_client_workbook_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            self.assertEqual(self.run_check(str(out), "--allow-multi-sheet")[0], 0)
            self.assertEqual(self.run_check(str(out), "--allow", "multi-sheet")[0], 0)

    def test_one_sheet_workbooks_need_no_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "one.xlsx"
            make_xlsx.build({"title": "清单", "theme": "coffee", "sheet": "清单", "columns": [{"name": "功能"}, {"name": "说明", "type": "longtext"}], "rows": [["甲", "说明甲"], ["乙", "说明乙"]]}, out)
            self.assertEqual(self.run_check(str(out))[0], 0)


if __name__ == "__main__":
    unittest.main()
