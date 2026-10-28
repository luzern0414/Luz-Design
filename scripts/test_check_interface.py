"""Interface layout checks in check_document.py (--allow interface) and the field-name warning for exported sheets."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_document as cd  # noqa: E402

from new_session import TAB_ICONS, fill_icon_slots, read_template, tab_icon_href, tab_icon_svg  # noqa: E402

ICON = f'<link rel="icon" href="{tab_icon_href("门店后台")}">'
PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>原型</title>{head}<style>body{{font-size:14px}} {css}</style></head><body><h1>门店后台原型</h1><h2>会员</h2>{body}</body></html>"""


def run(body: str, css: str = "", allow: tuple[str, ...] = ("interface",), head: str = ICON) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "page.html"
        path.write_text(PAGE.format(css=css, body=body, head=head), encoding="utf-8")
        cd.ALLOWED.clear()
        cd.ALLOWED.update(allow)
        errors: list[str] = []
        warnings: list[str] = []
        try:
            cd.check_html(path, errors, warnings)
        finally:
            cd.ALLOWED.clear()
    return errors, warnings


def table(rows: list[list[str]], header: list[str], cls: str = "") -> str:
    head = "".join(f"<th>{h}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


class BodyTextSizeTest(unittest.TestCase):
    def only(self, items: list[str], word: str) -> list[str]:
        return [e for e in items if word in e]

    def test_small_table_cells_are_errors(self) -> None:
        errors, _ = run(table([["张三", "月卡"]] * 3, ["姓名", "卡种"], "grid"), ".grid td{font-size:13px}")
        self.assertEqual(len(self.only(errors, "body text 13px")), 1)

    def test_inherited_size_counts(self) -> None:
        errors, _ = run('<div class="list"><p>本月新增会员</p><label>门店</label></div>', ".list{font-size:12px}")
        self.assertEqual(len(self.only(errors, "body text 12px")), 2)

    def test_em_and_rem_are_computed(self) -> None:
        errors, _ = run('<div class="box"><p>到店人数</p></div>', ".box{font-size:16px}.box p{font-size:.8em}")
        self.assertTrue(self.only(errors, "body text 12.8px"))
        errors, _ = run('<p class="x">到店人数</p>', ".x{font-size:0.875rem}")
        self.assertFalse(self.only(errors, "body text"))

    def test_auxiliary_classes_may_be_small(self) -> None:
        css = ".time{font-size:12px}.unit-cell{font-size:12px}.meta p{font-size:12px}"
        body = '<table><tr><th>时间</th></tr><tr><td class="time">10-28 09:30</td></tr></table>' \
               '<p class="unit-cell">元</p><div class="meta"><p>更新于今天</p></div>'
        errors, _ = run(body, css)
        self.assertFalse(self.only(errors, "body text"))

    def test_fourteen_px_and_state_rules_pass(self) -> None:
        errors, _ = run("<p>会员总数</p><button>新建</button>", "p{font-size:14px} button:hover{font-size:12px}")
        self.assertFalse(self.only(errors, "body text"))

    def test_more_specific_rule_wins(self) -> None:
        errors, _ = run('<p class="lead">会员总数</p>', "p.lead{font-size:14px} p{font-size:12px}")
        self.assertFalse(self.only(errors, "body text"))
        errors, _ = run('<p class="lead">会员总数</p>', "p{font-size:14px} p.lead{font-size:12px}")
        self.assertTrue(self.only(errors, "body text"))

    def test_mobile_media_query_does_not_decide(self) -> None:
        errors, _ = run("<p>会员总数</p>", "p{font-size:14px} @media (max-width:760px){p{font-size:12px}}")
        self.assertFalse(self.only(errors, "body text"))

    def test_reading_pages_are_not_checked(self) -> None:
        errors, _ = run("<p>会员总数</p>", "p{font-size:16px}", allow=())
        self.assertFalse(self.only(errors, "body text"))


class TitleAndNavTest(unittest.TestCase):
    NAV = '<nav class="side"><a href="#" class="{a}">会员管理</a><a href="#">订单管理</a></nav>'

    def test_title_equal_to_active_item_is_an_error(self) -> None:
        body = self.NAV.format(a="active") + '<div class="page-head"><h3>会员管理</h3></div>'
        errors, _ = run(body)
        self.assertTrue([e for e in errors if "repeats the highlighted navigation item" in e])

    def test_aria_current_counts_as_active(self) -> None:
        body = '<aside><button aria-current="page">会员管理</button></aside><div class="page-title">会员管理</div>'
        errors, _ = run(body)
        self.assertTrue([e for e in errors if "repeats the highlighted navigation item" in e])

    def test_different_title_or_inactive_item_passes(self) -> None:
        for body in (self.NAV.format(a="active") + '<div class="page-head"><h3>会员详情</h3></div>',
                     self.NAV.format(a="") + '<div class="page-head"><h3>会员管理</h3></div>'):
            errors, _ = run(body)
            self.assertFalse([e for e in errors if "repeats the highlighted" in e], body)

    def test_mini_program_tab_bar_is_not_navigation_here(self) -> None:
        body = '<div class="tabbar"><button aria-current="page">我的</button></div><div class="page-title">我的</div>'
        errors, _ = run(body)
        self.assertFalse([e for e in errors if "repeats the highlighted" in e])

    def test_group_label_equal_to_only_item(self) -> None:
        body = '<nav class="menu"><div class="group"><div class="group-title">概览</div><a href="#">概览</a></div>' \
               '<div class="group"><div class="group-title">会员</div><a href="#">会员管理</a><a href="#">会员卡</a></div></nav>'
        errors, _ = run(body)
        found = [e for e in errors if "navigation group" in e]
        self.assertEqual(len(found), 1)
        self.assertIn("概览", found[0])

    def test_label_followed_by_single_item_list(self) -> None:
        body = '<aside><h4>概览</h4><ul><li><a href="#">概览</a></li></ul><h4>营销</h4><ul><li><a href="#">优惠券</a></li></ul></aside>'
        errors, _ = run(body)
        self.assertEqual(len([e for e in errors if "navigation group" in e]), 1)

    def test_group_with_different_single_item_passes(self) -> None:
        body = '<nav class="menu"><div class="group"><div class="group-title">概览</div><a href="#">数据驾驶舱</a></div></nav>'
        errors, _ = run(body)
        self.assertFalse([e for e in errors if "navigation group" in e])


class TableColumnTest(unittest.TestCase):
    def test_empty_column_is_an_error(self) -> None:
        errors, _ = run(table([["张三", "—"], ["李四", "-"], ["王五", ""]], ["姓名", "备注"]))
        self.assertTrue([e for e in errors if "'备注' is empty" in e])

    def test_column_with_one_value_or_controls_passes(self) -> None:
        errors, _ = run(table([["张三", "—"], ["李四", "VIP"], ["王五", "—"]], ["姓名", "备注"]))
        self.assertFalse([e for e in errors if "is empty" in e])
        errors, _ = run(table([["张三", '<button aria-label="编辑"><svg></svg></button>']] * 3, ["姓名", "操作"]))
        self.assertFalse([e for e in errors if "is empty" in e])

    def test_two_rows_are_not_enough(self) -> None:
        errors, _ = run(table([["张三", "—"], ["李四", "—"]], ["姓名", "备注"]))
        self.assertFalse([e for e in errors if "is empty" in e])

    def test_identical_column_is_a_warning(self) -> None:
        rows = [[f"会员{i}", "正常"] for i in range(5)]
        _, warnings = run(table(rows, ["姓名", "状态"]))
        self.assertTrue([w for w in warnings if "'状态' holds '正常' in all 5 rows" in w])

    def test_identical_column_needs_five_rows_and_skips_operations(self) -> None:
        _, warnings = run(table([[f"会员{i}", "正常"] for i in range(4)], ["姓名", "状态"]))
        self.assertFalse([w for w in warnings if "holds" in w])
        _, warnings = run(table([[f"会员{i}", "详情"] for i in range(6)], ["姓名", "操作"]))
        self.assertFalse([w for w in warnings if "holds" in w])

    def test_rowspan_group_cells_are_laid_out(self) -> None:
        body = ('<table><thead><tr><th>模块</th><th>功能</th><th>备注</th></tr></thead><tbody>'
                '<tr><td rowspan="3">会员</td><td>办卡</td><td>—</td></tr><tr><td>续卡</td><td>—</td></tr>'
                '<tr><td>退卡</td><td>—</td></tr></tbody></table>')
        errors, _ = run(body)
        self.assertTrue([e for e in errors if "'备注' is empty" in e])
        self.assertFalse([e for e in errors if "'功能' is empty" in e])

    def test_long_text_padding_warning(self) -> None:
        rows = [["门店", "会员到店后在前台核验人脸并领取手环"]] * 3
        _, warnings = run(table(rows, ["对象", "说明"], "t"), ".t td{padding:8px 12px}")
        self.assertTrue([w for w in warnings if "12px side padding" in w])
        _, warnings = run(table(rows, ["对象", "说明"], "t"), ".t td{padding:12px 16px}")
        self.assertFalse([w for w in warnings if "side padding" in w])
        _, warnings = run(table(rows, ["对象", "说明"], "t"))
        self.assertFalse([w for w in warnings if "side padding" in w], "padding not set: not determinable")

    def test_short_cells_are_not_padding_checked(self) -> None:
        _, warnings = run(table([["张三", "月卡"]] * 3, ["姓名", "卡种"], "t"), ".t td{padding:8px}")
        self.assertFalse([w for w in warnings if "side padding" in w])


class TabIconTest(unittest.TestCase):
    """Every HTML mode: a missing, empty or placeholder tab icon is an error."""

    def icon_errors(self, head: str, allow: tuple[str, ...] = ()) -> tuple[list[str], list[str]]:
        errors, warnings = run("<p>正文</p>", allow=allow, head=head)
        return [e for e in errors if "tab icon" in e], [w for w in warnings if "tab icon" in w]

    def test_missing_icon_is_an_error_in_every_mode(self) -> None:
        for allow in ((), ("interface",), ("interface", "website")):
            with self.subTest(allow=allow):
                self.assertTrue(any("no browser-tab icon" in e for e in self.icon_errors("", allow)[0]))

    def test_empty_and_placeholder_icons_are_errors(self) -> None:
        for href in ("", "#", "{{TAB_ICON}}", "data:,", "data:image/svg+xml,", "data:image/svg+xml,%3Csvg%3E%3C/svg%3E"):
            with self.subTest(href=href):
                self.assertTrue(any("empty or an unfilled placeholder" in e for e in self.icon_errors(f'<link rel="icon" href="{href}">')[0]))
        self.assertTrue(self.icon_errors('<link rel="icon">')[0])

    def test_inline_icon_passes_and_rel_may_contain_icon(self) -> None:
        self.assertEqual(self.icon_errors(ICON), ([], []))
        svg = tab_icon_href("门店后台").replace("data:image/svg+xml,", "data:image/svg+xml;utf8,")
        self.assertEqual(self.icon_errors(f'<link rel="shortcut icon" href="{svg}">'), ([], []))
        import base64
        b64 = base64.b64encode(tab_icon_svg("门店后台").encode()).decode()
        self.assertEqual(self.icon_errors(f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{b64}">'), ([], []))

    def test_external_file_and_text_icons_warn(self) -> None:
        errors, warnings = self.icon_errors('<link rel="icon" href="favicon.ico">')
        self.assertEqual(errors, [])
        self.assertTrue(any("external file" in w for w in warnings))
        text_icon = "data:image/svg+xml,%3Csvg%3E%3Crect width='32' height='32'/%3E%3Ctext%3EA%3C/text%3E%3C/svg%3E"
        self.assertTrue(any("contains text" in w for w in self.icon_errors(f'<link rel="icon" href="{text_icon}">')[1]))

    def test_templates_and_icon_set_follow_the_drawing_rules(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for name in ("visual-board.html", "document.html"):
            with self.subTest(template=name):
                text = read_template(root, name)
                self.assertIn('<link rel="icon" href="{{TAB_ICON}}">', text)
                self.assertEqual(cd.tab_icon_findings(fill_icon_slots(text, "健身房会员海报")), ([], []))
        import re
        for key in TAB_ICONS:
            svg = tab_icon_svg("某页面", icon=key)
            self.assertIn('viewBox="0 0 32 32"', svg)
            self.assertIn('rx="8"', svg)
            self.assertNotIn("<text", svg)
            self.assertLessEqual(len(re.findall(r"<(?:path|rect|circle|line|polyline|polygon|ellipse)\b", svg)), 3, key)


PAGER = ('<div class="pagination"><span>共 86 条</span><select>{options}</select>'
         '<button type="button">1</button><button type="button">2</button></div>')
SIZES = '<option value="10"{a}>10 条/页</option><option value="20"{b}>20 条/页</option><option value="50">50 条/页</option>'


class PaginationAndBrandTest(unittest.TestCase):
    def warns(self, body: str, word: str, allow: tuple[str, ...] = ("interface",)) -> list[str]:
        return [w for w in run(body, allow=allow)[1] if word in w]

    def test_list_table_without_pagination_warns(self) -> None:
        self.assertTrue(self.warns(table([["甲", "1"]] * 3, ["客户", "次数"], "member-list"), "without pagination"))
        self.assertTrue(self.warns(table([[f"客户{i}", str(i)] for i in range(10)], ["客户", "次数"]), "without pagination"))

    def test_short_one_page_and_reading_tables_are_exempt(self) -> None:
        self.assertFalse(self.warns(table([["甲", "1"]] * 3, ["客户", "次数"]), "without pagination"))
        self.assertFalse(self.warns(table([[f"档位{i}", str(i)] for i in range(12)], ["档位", "折扣"], 'list" data-pagination="none'), "without pagination"))
        self.assertFalse(self.warns(table([[f"客户{i}", str(i)] for i in range(12)], ["客户", "次数"], "list"), "without pagination", allow=()))

    def test_default_page_size_must_be_20(self) -> None:
        good = table([["甲", "1"]] * 3, ["客户", "次数"], "list") + PAGER.format(options=SIZES.format(a="", b=" selected"))
        self.assertFalse(self.warns(good, "pagination"))
        bad = table([["甲", "1"]] * 3, ["客户", "次数"], "list") + PAGER.format(options=SIZES.format(a=" selected", b=""))
        self.assertTrue(self.warns(bad, "defaults to 10"))
        self.assertTrue(self.warns('<div class="pager" data-page-size="50"></div>', "defaults to 50"))
        text_only = table([["甲", "1"]] * 3, ["客户", "次数"], "list") + "<div>共 86 条 · 10 条/页</div>"
        self.assertFalse(self.warns(text_only, "without pagination"))
        self.assertTrue(self.warns(text_only, "defaults to 10"))

    def test_admin_header_needs_a_graphic_brand_mark(self) -> None:
        self.assertTrue(self.warns('<header class="topbar"><strong>门店后台</strong></header>', "brand mark"))
        self.assertTrue(self.warns('<aside class="sidebar"><div class="logo">店</div></aside>', "brand mark"))
        mark = tab_icon_svg("门店后台", attrs=' class="brand-mark" aria-hidden="true"')
        self.assertFalse(self.warns(f'<header class="topbar"><div class="brand">{mark}门店后台</div></header>', "brand mark"))
        self.assertFalse(self.warns('<div class="phone"><header class="mp-nav">首页</header></div>', "brand mark"))
        self.assertFalse(self.warns("<p>没有页头的原型</p>", "brand mark"))


class ExportHeaderTest(unittest.TestCase):
    def sheet(self, header: list[str]) -> list[str]:
        try:
            import openpyxl
        except ImportError:
            self.skipTest("openpyxl missing")
        book = openpyxl.Workbook()
        ws = book.active
        ws.title = "订单"
        ws["A1"] = "订单导出"
        for k, name in enumerate(header, 1):
            ws.cell(3, k, name)
            ws.cell(4, k, "x")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "订单.xlsx"
            book.save(path)
            errors: list[str] = []
            warnings: list[str] = []
            cd.check_xlsx(path, errors, warnings)
        return [w for w in warnings if "field names" in w]

    def test_snake_and_camel_case_headers_warn(self) -> None:
        self.assertTrue(self.sheet(["order_id", "客户", "金额（元）"]))
        self.assertTrue(self.sheet(["客户", "createdAt"]))
        self.assertTrue(self.sheet(["客户", "status"]))

    def test_chinese_and_business_abbreviations_pass(self) -> None:
        self.assertFalse(self.sheet(["客户", "金额（元）", "SKU", "GMV（元）"]))


if __name__ == "__main__":
    unittest.main()
