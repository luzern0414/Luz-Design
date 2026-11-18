"""Spreadsheets: nothing clipped, one font, one alignment per column (the first things that look ugly in Excel)."""
import sys
import json
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
        make_xlsx._render_workbook(SPEC, out)
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
            make_xlsx._render_workbook({**SPEC, "font": "微软雅黑"}, out)
            wb = load_workbook(out)
            self.assertEqual(wb._named_styles["Normal"].font.name, "微软雅黑")
            self.assertEqual(check_document.main([str(out)]), 0)
            with self.assertRaises(ValueError):
                make_xlsx._render_workbook({**SPEC, "font": "Arial"}, Path(tmp) / "bad.xlsx")
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
            make_xlsx._render_workbook(spec, out)
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
            make_xlsx._render_workbook(SPEC, wide)
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
            make_xlsx._render_workbook(self.spec(cols, self.ROWS, group_by=["使用端", "使用角色", "模块"]), out)
            self.assertEqual(check_document.main([str(out)]), 0)

    def test_identifier_before_group_is_an_error(self):
        cols = [{"name": "编号"}, {"name": "功能"}, {"name": "使用端"}, {"name": "说明", "type": "longtext"}]
        rows = [["FN-%02d" % i, "功能%d" % i, "端A" if i < 6 else "端B", "说明%d" % i] for i in range(12)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bad.xlsx"
            make_xlsx._render_workbook(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 1)   # 使用端 follows the identifying column and is not merged

    def test_bigger_group_must_come_first(self):
        rows = [["端A", "角色%d" % (i // 2), "FN-%02d" % i, "说明%d" % i] for i in range(6)] + [["端B", "角色%d" % (3 + i // 2), "FN-%02d" % (6 + i), "说明%d" % (6 + i)] for i in range(6)]
        small_first = [[r[1], r[0], r[2], r[3]] for r in rows]
        cols = [{"name": "使用角色", "merge": True}, {"name": "使用端", "merge": True}, {"name": "编号"}, {"name": "说明", "type": "longtext"}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "order.xlsx"
            make_xlsx._render_workbook(self.spec(cols, small_first), out)
            self.assertEqual(check_document.main([str(out)]), 1)   # 6 role groups sit before 2 surface groups

    def test_change_ledger_in_time_order_has_no_grouping_column(self):
        # A ledger lists records by 变更编号; type, category and requester come in runs only because changes arrive in batches.
        cols = [{"name": "变更编号"}, {"name": "提出日期", "type": "date"}, {"name": "变更类型"}, {"name": "分类"}, {"name": "变更标题", "type": "longtext"},
                {"name": "提出人"}, {"name": "涉及阶段", "type": "longtext"}, {"name": "状态"}]
        rows = [["CHG-%03d" % (i + 1), "2026-11-03", "修改" if i < 3 else "新增", "规则" if i < 3 else "范围", "变更%d" % (i + 1),
                 "内部" if i < 3 else "客户", "client-intake" if i < 3 else "architecture", "待确认" if i < 3 else "已确认"] for i in range(8)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ledger.xlsx"
            make_xlsx._render_workbook(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 0)

    def test_identifier_first_table_that_is_not_a_ledger_still_fails(self):
        cols = [{"name": "编号"}, {"name": "提出日期", "type": "date"}, {"name": "变更类型"}, {"name": "分类"}, {"name": "变更标题", "type": "longtext"}]
        rows = [["CHG-%03d" % (i + 1), "2026-11-03", "修改" if i < 3 else "新增", "规则" if i < 3 else "范围", "变更%d" % (i + 1)] for i in range(8)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "notledger.xlsx"
            make_xlsx._render_workbook(self.spec(cols, rows), out)
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
                make_xlsx._render_workbook(self.spec([*cols[:4], {**cols[4], "name": header}, cols[5]], rows), out)
                self.assertEqual(check_document.main([str(out)]), 0)

    def test_a_column_that_only_looks_like_a_result_is_still_a_grouping_column(self):
        # The exemption is the header's meaning, not the data: a group name that happens to sit after an identifier still fails.
        cols = [{"name": "编号"}, {"name": "功能"}, {"name": "结果页面"}, {"name": "说明", "type": "longtext"}]
        rows = [["FN-%02d" % i, "功能%d" % i, "页面A" if i < 6 else "页面B", "说明%d" % i] for i in range(12)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pages.xlsx"
            make_xlsx._render_workbook(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 1)

    def test_equal_text_across_a_parent_boundary_is_not_an_error(self):
        rows = [["端A", "角色甲", "模块1", "FN-1", "x"], ["端A", "角色甲", "模块1", "FN-2", "x"], ["端A", "角色乙", "模块1", "FN-3", "x"], ["端B", "角色丙", "模块1", "FN-4", "x"]]
        cols = [{"name": "使用端", "merge": True}, {"name": "使用角色", "merge": True}, {"name": "模块", "merge": True}, {"name": "编号"}, {"name": "说明"}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "boundary.xlsx"
            make_xlsx._render_workbook(self.spec(cols, rows), out)
            self.assertEqual(check_document.main([str(out)]), 0)


class MultiSheetTests(unittest.TestCase):
    """Two worksheets are for what the user or the document standard asks for (Luz-Project client documents 04 and 05)."""

    def build(self, tmp: str) -> Path:
        sheet = lambda name, col: {"sheet": name, "columns": [{"name": "功能"}, {"name": col, "type": "longtext"}], "rows": [[f"功能{i}", f"说明{i}"] for i in range(3)]}
        out = Path(tmp) / "two.xlsx"
        make_xlsx._render_workbook({"title": "功能清单", "theme": "coffee", "sheets": [sheet("功能清单", "功能说明"), sheet("资料清单", "资料说明")]}, out)
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
            make_xlsx._render_workbook({"title": "清单", "theme": "coffee", "sheet": "清单", "columns": [{"name": "功能"}, {"name": "说明", "type": "longtext"}], "rows": [["甲", "说明甲"], ["乙", "说明乙"]]}, out)
            self.assertEqual(self.run_check(str(out))[0], 0)


class EstimatePolicyTests(unittest.TestCase):
    """预算、人日与报价政策: no workdays, amounts, totals or quotation in a spreadsheet unless the project asked, and a price only from a person."""

    # Fixture numbers are obviously not prices: 1, 2, 3.
    ASKED = {"requested_by": "客户方负责人", "request_note": "请按人天报价"}
    QUOTED = {"workdays": True, "quote": True, **ASKED, "provided_by": "销售负责人", "evidence": "uploads/客户报价单.xlsx"}

    def sheet(self, header: list[str], rows: list[list], **extra) -> dict:
        numeric = ("数量", "工时（人天）", "单价（元）", "金额（元）", "电流（A）", "功率（W）", "报价（元）")
        return {"title": "功能清单", "theme": "coffee", "sheet": "功能清单",
                "columns": [{"name": h, "type": "number"} if h in numeric else {"name": h, "type": "longtext" if h == "说明" else "text"} for h in header],
                "rows": rows, **extra}

    def check(self, spec: dict, *allow: str) -> tuple[int, str]:
        import contextlib
        import io
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            out = make_xlsx._render_workbook(spec, Path(tmp) / "a.xlsx")
            argv = [str(out)]
            for kind in allow:
                argv += ["--allow", kind]
            with contextlib.redirect_stdout(buf):
                code = check_document.main(argv)
        return code, buf.getvalue()

    def test_a_function_list_without_numbers_passes(self):
        spec = self.sheet(["功能", "说明", "类型"], [["功能甲", "说明甲", "基础"], ["功能乙", "说明乙", "可选"]])
        self.assertEqual(self.check(spec)[0], 0)

    def test_amount_words_in_a_header_or_a_summary_label_are_errors_by_default(self):
        for header in ("金额（元）", "单价（元）", "报价（元）", "预算（元）", "总价（元）"):
            with self.subTest(header=header):
                code, out = self.check(self.sheet(["功能", header], [["功能甲", 1], ["功能乙", 2]]))
                self.assertEqual(code, 1)
                self.assertIn("no quotation was asked for", out)

    def test_a_total_of_money_is_an_error_but_a_total_of_current_or_devices_is_not(self):
        money = self.sheet(["功能", "金额（元）"], [["功能甲", 1], ["功能乙", 2]], total={"label": "合计", "sum": ["金额（元）"]})
        code, out = self.check(money)
        self.assertEqual(code, 1)
        self.assertIn("no quotation was asked for", out)
        amps = self.sheet(["设备", "电流（A）"], [["设备甲", 1], ["设备乙", 2]], total={"label": "合计", "sum": ["电流（A）"]})
        self.assertEqual(self.check(amps)[0], 0, "a sum of amperes is not an amount")
        watts = self.sheet(["设备", "功率（W）"], [["设备甲", 1], ["设备乙", 2]], total={"label": "合计", "sum": ["功率（W）"]})
        self.assertEqual(self.check(watts)[0], 0)
        count = self.sheet(["设备", "数量"], [["设备甲", 1], ["设备乙", 2]], total={"label": "合计", "sum": ["数量"]})
        self.assertEqual(self.check(count)[0], 0, "a count of devices is not an amount")

    def test_a_total_cell_that_names_its_unit_is_read_by_the_unit(self):
        cur = self.sheet(["项目", "现场条件"], [["配电", "三相"], ["合计", "合计约 6.5 A"]])
        self.assertEqual(self.check(cur)[0], 0, "合计约 6.5 A is a current")
        yuan = self.sheet(["项目", "现场条件"], [["配电", "三相"], ["合计", "合计约 6.5 元"]])
        self.assertEqual(self.check(yuan)[0], 1, "a total in 元 is money")

    def test_workday_columns_are_errors_by_default_and_released_by_workdays_or_quote(self):
        spec = self.sheet(["功能", "工时（人天）"], [["功能甲", 1], ["功能乙", 2]])
        code, out = self.check(spec)
        self.assertEqual(code, 1)
        self.assertIn("did not ask for workdays", out)
        self.assertEqual(self.check({**spec, "estimate": {"workdays": True, **self.ASKED}}, "workdays")[0], 0)
        self.assertEqual(self.check({**spec, "estimate": self.QUOTED}, "quote")[0], 0, "a quotation is built on workdays: quote implies workdays")

    def test_quote_releases_amounts_but_workdays_alone_does_not(self):
        spec = self.sheet(["功能", "工时（人天）", "金额（元）"], [["功能甲", 1, 3], ["功能乙", 2, 6]])
        self.assertEqual(self.check({**spec, "estimate": {"workdays": True, **self.ASKED}}, "workdays")[0], 1)
        self.assertEqual(self.check({**spec, "estimate": self.QUOTED}, "quote")[0], 0)

    def test_the_switch_without_evidence_in_the_file_is_still_an_error(self):
        spec = self.sheet(["功能", "金额（元）"], [["功能甲", 1], ["功能乙", 2]])
        code, out = self.check(spec, "quote")
        self.assertEqual(code, 1)
        self.assertIn("carries no evidence", out)
        code, out = self.check({**spec, "estimate": self.QUOTED}, "quote")
        self.assertEqual(code, 0, out)

    def test_a_sentence_that_mentions_an_amount_is_content_not_a_column(self):
        spec = self.sheet(["功能", "说明"], [["订单筛选", "按订单金额和下单时间筛选，支持导出"], ["退款", "退款金额原路返回，合计不超过实付"]])
        self.assertEqual(self.check(spec)[0], 0)

    def test_the_builder_needs_evidence_before_it_lets_a_price_through(self):
        good = self.QUOTED
        self.assertEqual(make_xlsx.estimate_allow({"estimate": good}), ["quote"])
        self.assertEqual(make_xlsx.estimate_allow({"estimate": {**good, "quote": False}}), ["workdays"])
        self.assertEqual(make_xlsx.estimate_allow({}), [])
        self.assertEqual(make_xlsx.estimate_allow({"estimate": {"workdays": False, "quote": False}}), [])
        for broken, why in (({**good, "requested_by": ""}, "requested_by"), ({**good, "request_note": ""}, "request_note"),
                            ({**good, "evidence": ""}, "evidence"), ({**good, "provided_by": ""}, "provided_by"),
                            ({**good, "workdays": False}, "workdays")):
            with self.subTest(missing=why), self.assertRaises(ValueError) as caught:
                make_xlsx.estimate_allow({"estimate": broken})
            self.assertIn(why, str(caught.exception))
        for who in ("agent", "Claude", "技能", "示例", "暂估", "系统", "default sample", "待定", "AI"):
            with self.subTest(provided_by=who), self.assertRaises(ValueError):
                make_xlsx.estimate_allow({"estimate": {**good, "provided_by": who}})
            with self.subTest(requested_by=who), self.assertRaises(ValueError):
                make_xlsx.estimate_allow({"estimate": {**good, "requested_by": who}})

    def test_allow_quote_with_quote_evidence_is_the_form_the_hardware_list_uses(self):
        spec = {"allow_quote": True, "quote_evidence": {"requested_by": "客户方负责人", "request_note": "请列出参考价"}}
        self.assertEqual(make_xlsx.estimate_allow(spec), ["quote"])
        self.assertIn("要求人：客户方负责人", make_xlsx.estimate_evidence(spec))
        for broken in ({"allow_quote": True}, {"allow_quote": True, "quote_evidence": "客户要求"}, {"allow_quote": True, "quote_evidence": {"requested_by": "客户"}},
                       {"allow_quote": True, "quote_evidence": {"requested_by": "agent", "request_note": "x"}}):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                make_xlsx.estimate_allow(broken)
        self.assertEqual(make_xlsx.estimate_allow({"allow_quote": False}), [], "allow_quote defaults to false")
        sheet = self.sheet(["设备", "单价（元）"], [["设备甲", 1], ["设备乙", 2]], **spec)
        self.assertEqual(self.check(sheet, "quote")[0], 0)

    def test_build_refuses_an_estimate_block_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            make_xlsx._render_workbook(self.sheet(["功能", "说明"], [["功能甲", "说明甲"]], estimate={"workdays": True}), Path(tmp) / "a.xlsx")

    def test_the_command_line_stops_without_evidence_and_passes_the_switch_with_it(self):
        import contextlib
        import io
        spec = self.sheet(["功能", "工时（人天）", "金额（元）"], [["功能甲", 1, 3], ["功能乙", 2, 6]])
        with tempfile.TemporaryDirectory() as tmp:
            from new_session import create_session
            from test_crawl_gate import complete_fixture
            session = create_session(Path(tmp) / "sessions", "表格命令测试", ["document"], cards=["xlsx"])
            complete_fixture(session, "luz-design", "design")
            out = session / "raw" / "a.xlsx"
            from template_library import select
            select(session, "luz-design", "design", "xlsx", out.relative_to(session).as_posix())
            for estimate, expected in (({}, 1), (self.QUOTED, 0), ({**self.QUOTED, "evidence": ""}, 2)):
                spec_path = session / "raw" / "spec.json"
                spec_path.write_text(json.dumps({**spec, **({"estimate": estimate} if estimate else {})}, ensure_ascii=False), encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(make_xlsx.main([str(spec_path), str(out)]), expected, estimate)

    def test_no_shipped_example_carries_a_default_price(self):
        root = Path(__file__).resolve().parent.parent
        for name in ("scripts/make_xlsx.py", "scripts/make_docx.py"):
            doc = (root / name).read_text(encoding="utf-8").split('"""')[1]
            self.assertNotRegex(doc, r"1680|128000|500 ?元|单价（元）", name)


class EstimateTermsTests(unittest.TestCase):
    """estimate_terms.py is the one list of words; the skills that copy it keep it identical (the digest)."""

    def test_the_lists_are_data_and_the_digest_is_stable(self):
        import estimate_terms as et
        self.assertTrue(all(isinstance(v, (list, str, int)) and v for v in et.TERMS.values()))
        self.assertEqual(et.terms_digest(), et.terms_digest())
        self.assertEqual(len(et.terms_digest()), 16)

    def test_not_a_person(self):
        import estimate_terms as et
        non_people = ["agent", "Claude", "智能体", "AI 助手", "系统", "技能", "示例", "暂估", "默认值", "n/a", "未知", "空", "无", "TBD", "Claude（自动生成）", "assistant-generated", "模板",
                      "AI", "claude code", "ai assistant", "default", "待定", "", "  ", "luz-design", "系统生成", "模板填写", "示例代填", "default sample", "ChatGPT", "机器人", "大模型"]
        for bad in non_people:
            with self.subTest(bad=bad):
                self.assertTrue(et.not_a_person(bad), bad)
        people = ["系统管理员", "空调公司张工", "无锡客户采购", "程序员王工", "Na", "商务经理", "客户采购负责人", "张三（客户方负责人）", "销售负责人", "客户方采购经理", "Mr. Li", "王经理",
                  "Maintainer", "Ai Wang", "Nakamura", "无人机公司李工", "自动化部赵工", "模型师陈工", "工具库管理员"]
        for good in people:
            with self.subTest(good=good):
                self.assertFalse(et.not_a_person(good), good)

    def test_a_self_drafted_value_is_not_a_person_but_a_name_that_contains_the_word_is(self):
        import estimate_terms as et
        for bad in ("自拟", "自拟生成", "客户（自拟）", "自拟 填写"):
            with self.subTest(bad=bad):
                self.assertTrue(et.not_a_person(bad), bad)
        for good in ("自拟人", "张自拟", "自拟科技公司采购"):
            with self.subTest(good=good):
                self.assertFalse(et.not_a_person(good), good)

    def test_says_made_up_looks_for_the_words_anywhere_in_the_text(self):
        import estimate_terms as et
        for bad in ("暂估，先按这个算", "按默认值 800", "自拟的价格", "这是占位数据", "示例数据，仅供参考", "样例数据", "Placeholder price", "assumed 800", "estimated by the team", "TBD，等客户确认"):
            with self.subTest(bad=bad):
                self.assertTrue(et.says_made_up(bad), bad)
        for good in ("客户邮件确认单价 1200 元/人天（见附件）", "uploads/客户报价单.xlsx", "销售负责人微信确认", "请按人天报价", "", None):
            with self.subTest(good=good):
                self.assertFalse(et.says_made_up(good), good)

    def test_the_length_constants_are_exported_with_their_use(self):
        import estimate_terms as et
        self.assertEqual((et.MIN_NOTE, et.EVIDENCE_MIN), (4, 6))
        self.assertEqual(et.TERMS["min_note"], 4)
        self.assertEqual(et.TERMS["evidence_min"], 6)
        self.assertEqual(et.read_evidence(et.EVIDENCE_PREFIX + "x" * (et.EVIDENCE_MIN - 1)), "")
        self.assertTrue(et.read_evidence(et.EVIDENCE_PREFIX + "x" * et.EVIDENCE_MIN))

    def test_the_builder_refuses_an_evidence_that_calls_the_figures_an_estimate(self):
        good = {"workdays": True, "quote": True, "requested_by": "客户方负责人", "request_note": "请按人天报价", "provided_by": "销售负责人", "evidence": "uploads/客户报价单.xlsx"}
        for evidence in ("暂估，先按这个算", "按默认值 800", "自拟"):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                make_xlsx.estimate_allow({"estimate": {**good, "evidence": evidence}})

    def test_is_not_evidence(self):
        import estimate_terms as et
        for bad in ("", "  ", "暂估", "示例", "默认值", "示例、默认值", "TBD", "n/a", "无", "待定 占位", "示例数据", "placeholder"):
            with self.subTest(bad=bad):
                self.assertTrue(et.is_not_evidence(bad), bad)
        for good in ("客户原话：请按人天报价", "uploads/客户报价单.xlsx", "微信聊天 2026-11-05：按这个价格报", "请按 500 个工作日的口径列预算，示例我们不要", "销售负责人口头确认"):
            with self.subTest(good=good):
                self.assertFalse(et.is_not_evidence(good), good)

    def test_the_builder_refuses_a_placeholder_for_the_words_or_the_source(self):
        good = {"workdays": True, "quote": True, "requested_by": "客户方负责人", "request_note": "请按人天报价", "provided_by": "销售负责人", "evidence": "uploads/客户报价单.xlsx"}
        for key, value in (("request_note", "暂估"), ("evidence", "示例数据"), ("request_note", "TBD")):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                make_xlsx.estimate_allow({"estimate": {**good, key: value}})
        self.assertEqual(make_xlsx.estimate_allow({"estimate": {**good, "provided_by": "系统管理员"}}), ["quote"], "a legitimate role is accepted")

    def test_money_is_read_beside_its_unit(self):
        import estimate_terms as et
        self.assertTrue(et.is_money_text("金额（元）"))
        self.assertTrue(et.is_money_text("合计", row_text="3 元"))
        self.assertTrue(et.is_money_text("小计", column_text="金额（元）"))
        self.assertFalse(et.is_money_text("合计", row_text="6.5 A", column_text="电流（A）"))
        self.assertFalse(et.is_money_text("合计约 6.5 A"))
        self.assertFalse(et.is_money_text("合计 12 台"))
        self.assertFalse(et.is_money_text("合计", row_text="3.2 kW"))
        self.assertTrue(et.is_money_text("合计约 6.5 元"))
        self.assertFalse(et.is_money_text("功能说明"))

    def test_evidence_round_trip(self):
        import estimate_terms as et
        text = et.evidence_text("客户方负责人", "请按人天报价", "销售负责人", "uploads/报价单.xlsx")
        self.assertIn("要求人：客户方负责人", text)
        self.assertTrue(et.read_evidence(text))
        self.assertEqual(et.read_evidence(None), "")
        self.assertEqual(et.read_evidence("报价依据：无"), "")


if __name__ == "__main__":
    unittest.main()
