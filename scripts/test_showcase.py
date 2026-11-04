"""Showcase documents: icons, spec validation, per-column alignment, figures, page packing."""
import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_document  # noqa: E402
import make_showcase  # noqa: E402
import showcase  # noqa: E402
import showcase_figures as F  # noqa: E402
import showcase_icons as I  # noqa: E402

ARCH = {"layers": [
    {"name": "使用端", "icon": "phone", "nodes": [{"id": "U1", "name": "小程序", "role": "报餐"}, {"id": "U2", "name": "后台", "role": "管理"}]},
    {"name": "业务", "nodes": [{"id": "S1", "name": "订单", "role": "报餐与取消"}, {"id": "S2", "name": "企业", "role": "员工名单"}]},
    {"name": "基础", "nodes": [{"id": "B1", "name": "数据库", "role": "订单数据"}]}],
    "flows": [{"from": "U1", "to": "S1", "n": 1}, {"from": "U2", "to": "S2", "n": 2}, {"from": "S1", "to": "B1", "n": 3}, {"from": "U1", "to": "B1", "n": 4}]}

SPEC = {"title": "示例方案", "icon": "utensils", "theme": "cantonese-cafe", "orientation": "portrait",
        "hero": {"stats": [{"value": "5 家", "label": "企业", "icon": "building"}, {"value": "18–22 天", "label": "工期", "icon": "calendar"}], "scene": ["users", "list", "scan"]},
        "sections": [
            {"title": "背景", "icon": "flag", "blocks": [{"type": "text", "text": "这是一段说明。"}, {"type": "cards", "items": [{"title": "备餐", "text": "份数不准"}, {"title": "对账", "text": "没有凭证"}]}]},
            {"title": "清单", "blocks": [{"type": "table", "columns": ["名称", "说明", "类型"], "rows": [["登录", "员工用微信一键登录小程序并绑定所属企业", "基础"], ["报餐", "选一个套餐提交", "可选"]]},
                                      {"type": "figure", "figure": "arch_layers", "data": ARCH, "caption": "架构图"}]}]}


class ShowcaseTests(unittest.TestCase):
    def test_icons_are_complete_and_consistent(self):
        for name, (face, lines) in I.ICONS.items():
            self.assertTrue(lines, name)
            svg = I.svg(name, fill="#cccccc")
            self.assertIn('stroke-width="2.0"', svg)
        self.assertEqual(I.pick("员工管理"), "users")

    def test_every_section_title_gets_an_icon_block(self):
        page = showcase.build(SPEC)
        self.assertEqual(page.count('class="sh"'), 2)
        self.assertEqual(len(re.findall(r'<h2 class="sh"[^>]*><span class="ib', page)), 2)
        self.assertIn('<link rel="icon"', page)

    def test_an_atlas_keeps_its_title_in_the_header_only_and_heads_follow_their_columns(self):
        spec = {**SPEC, "style": "atlas", "show_title": False, "hero": {},
                "sections": [{"title": "总体架构", "blocks": [{"type": "table", "columns": ["编号", "链路", "说明"], "caption": "数据流向",
                                                              "rows": [["1", "员工报餐", "员工在截止前选择套餐提交，系统校验企业与员工状态"], ["2", "发布菜单", "平台为企业按日期和餐期发布菜单，发布时复制套餐快照"]]}]}]}
        self.assertEqual(showcase.validate_spec(spec), [])
        page = showcase.build(spec)
        self.assertIn('class="vh"', page)                    # the h1 stays for readers and tabs, hidden from the page
        self.assertNotIn('class="hero-head"', page)
        self.assertEqual(re.findall(r'<th class="(\w)"', page), ["c", "l", "l"])     # 编号 is a marker column, the text columns read from the left
        self.assertIn("编号", page)
        bad = {**SPEC, "show_title": False}
        self.assertTrue(any("show_title" in e for e in showcase.validate_spec(bad)))

    def test_table_alignment_is_decided_per_column(self):
        al = showcase.column_alignments(["名称", "说明", "类型", "数量"], [["登录", "员工用微信一键登录小程序并绑定", "基础", "3"], ["报餐", "短", "可选", "12"]])
        self.assertEqual(al, ["c", "l", "c", "r"])  # 说明 holds a long cell, so every cell of that column is left-aligned
        page = showcase.table_html(["名称", "说明"], [["a", "很长很长很长很长很长很长很长很长"], ["b", "短"]])
        self.assertEqual(page.count('class="l"'), 2)

    def test_validation_names_the_problem(self):
        bad = copy.deepcopy(SPEC)
        bad["sections"][0]["blocks"].append({"type": "cards", "items": [{"title": "x", "text": "y", "icon": "no-such-icon"}]})
        bad["sections"][1]["blocks"][0]["rows"].append(["只有一格"])
        bad["sections"][1]["blocks"][1]["data"]["flows"].append({"from": "U1", "to": "ZZ"})
        errors = "\n".join(showcase.validate_spec(bad))
        self.assertIn("no-such-icon", errors)
        self.assertIn("行列数不一致", errors)
        self.assertIn("连线引用不存在", errors)
        bad2 = copy.deepcopy(SPEC)
        bad2["sections"][0]["blocks"][0]["text"] = "待补充"
        self.assertTrue(any("占位" in e for e in showcase.validate_spec(bad2)))

    def test_figure_text_is_never_below_14px(self):
        t = showcase.tokens("cantonese-cafe")
        for svg in (F.arch_layers(ARCH, t, 1012), F.hero_scene(["users", "scan"], t, 684)):
            sizes = {int(x) for x in re.findall(r'font-size="(\d+)"', svg)}
            self.assertTrue(all(s >= 14 for s in sizes), sizes)

    def test_display_page_passes_the_document_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "方案.html"
            src.write_text(showcase.build(SPEC), encoding="utf-8")
            self.assertEqual(check_document.main([str(src), "--allow", "showcase"]), 0)

    def test_pdf_is_packed_and_fonts_are_embedded(self):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                p.chromium.launch(channel="msedge").close()
        except Exception:
            self.skipTest("Edge is not available")
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "s.json"
            import json
            spec.write_text(json.dumps({**SPEC, "min_fill": 0.1}, ensure_ascii=False), encoding="utf-8")
            pdf = Path(tmp) / "out.pdf"
            self.assertEqual(make_showcase.main([str(spec), str(pdf), "--min-fill", "0.1"]), 0)
            self.assertTrue(pdf.stat().st_size > 5000)


GROUPED = {"layers": [
    {"name": "使用端", "groups": [{"name": "企业", "nodes": [{"id": "U1", "name": "企业后台", "role": "员工管理"}]},
                                 {"name": "员工", "nodes": [{"id": "U2", "name": "员工小程序", "role": "报餐"}]}]},
    {"name": "业务模块", "groups": [{"name": "菜单与订单", "nodes": [{"id": "S1", "name": "套餐与菜单", "role": "发布"}, {"id": "S2", "name": "报餐与订单", "role": "截止"}]},
                                   {"name": "履约与对账", "nodes": [{"id": "S3", "name": "取餐核销", "role": "防伪"}, {"id": "S4", "name": "汇总与导出", "role": "备餐表"}]}]},
    {"name": "基础保障", "nodes": [{"id": "B1", "name": "数据库", "role": "订单数据"}, {"id": "B2", "name": "图片存储", "role": "套餐图片"}]}],
    "flows": [{"from": "U2", "to": "S2", "n": 1}, {"from": "U1", "to": "S1", "n": 2}, {"from": "S2", "to": "S4", "n": 3}, {"from": "S2", "to": "B1", "n": 4},
              {"from": "S1", "to": "B2", "n": 5}, {"from": "U2", "to": "S3", "n": 6}]}


def _links(svg):
    """The links of a figure as lists of corner points, read from the path data (M, L, H, V)."""
    out = []
    for d in re.findall(r'<path d="([^"]+)" fill="none" stroke="[^"]+" stroke-width="1\.[58]"', svg):
        pts, x, y = [], 0.0, 0.0
        for cmd, val in re.findall(r"([MLHV])([-\d. ]+)", d):
            nums = [float(v) for v in val.split()]
            if cmd in "ML":
                x, y = nums
            elif cmd == "H":
                x = nums[0]
            else:
                y = nums[0]
            pts.append((x, y))
        out.append(pts)
    return out


def _hits(pts, rect, pad=0.0):
    """Whether any segment of the polyline passes through the rectangle (x, y, w, h), grown by ``pad``."""
    rx, ry, rw, rh = rect
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if max(ax, bx) > rx - pad and min(ax, bx) < rx + rw + pad and max(ay, by) > ry - pad and min(ay, by) < ry + rh + pad:
            return True
    return False


class FigureColourAndRoutingTests(unittest.TestCase):
    def test_every_theme_gets_distinct_hues_that_hold_their_contrast(self):
        import json
        for name in json.loads((HERE.parent / "references" / "themes.json").read_text(encoding="utf-8"))["themes"]:
            t = showcase.tokens(name)
            pal = F.palette(t)
            self.assertGreaterEqual(len(pal), 3, name)
            for a in range(len(pal)):
                for b in range(a + 1, len(pal)):
                    self.assertTrue(F._apart(pal[a]["base"], pal[b]["base"]), (name, pal[a]["base"], pal[b]["base"]))
            for h in pal:
                self.assertGreaterEqual(F._ratio(h["stroke"], "#FFFFFF"), 3.0, (name, h))
                self.assertGreaterEqual(F._ratio(h["ink"], h["fill"]), 4.5, (name, h))

    def test_layers_have_their_own_hue_and_links_and_badges_are_one_neutral_ink(self):
        t = showcase.tokens("cantonese-cafe")
        svg = F.arch_layers(GROUPED, t, 1012)
        pal = F.palette(t)
        for h in pal[:3]:
            self.assertIn(f'fill="{h["fill"]}" stroke="{h["line"]}"', svg)        # a face of each hue
        links = re.findall(r'<path d="[^"]+" fill="none" stroke="([^"]+)"', svg)
        self.assertEqual(set(links), {t["ink"]})
        self.assertIn(f'<marker id="ar"', svg)
        self.assertIn(f'fill="{t["ink"]}"/></marker>', svg)
        self.assertEqual(set(re.findall(r'<circle [^>]*r="11" fill="#fff" stroke="([^"]+)"', svg)), {t["ink"]})

    def test_links_are_drawn_after_the_group_titles_and_never_enter_one(self):
        t = showcase.tokens("cantonese-cafe")
        svg = F.arch_layers(GROUPED, t, 1012)
        chips = [tuple(map(float, m)) for m in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="20" rx="4"', svg)]
        self.assertEqual(len(chips), 4)
        self.assertLess(svg.rindex('height="20" rx="4"'), re.search(r'<path d="M[\d.]+ [\d.]+ [VH]', svg).start())      # titles first, links over them
        for pts in _links(svg):
            for chip in chips:
                self.assertFalse(_hits(pts, (chip[0], chip[1], chip[2], 20)), (pts, chip))

    def test_a_link_inside_one_layer_runs_in_the_gap_below_it_and_never_through_a_node_or_title(self):
        t = showcase.tokens("cantonese-cafe")
        svg = F.arch_layers(GROUPED, t, 1012)
        nodes = [tuple(map(float, m)) for m in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="10" fill="#fff" stroke="[^"]+" stroke-width="1\.6"', svg)]
        links = _links(svg)
        same = links[2]                                                                   # S2 -> S4, both in the second layer
        bottoms = sorted({round(n[1] + n[3]) for n in nodes})
        self.assertGreater(same[1][1], bottoms[1])                                        # the lane is below the second layer's nodes
        for pts in links:
            for node in nodes:
                inside = [pt for pt in pts if node[0] < pt[0] < node[0] + node[2] and node[1] + 2 < pt[1] < node[1] + node[3] - 2]
                self.assertFalse(inside, (pts, node))
                self.assertFalse(any(abs(ax - bx) < 0.01 and node[0] + 1 < ax < node[0] + node[2] - 1 and min(ay, by) < node[1] + node[3] - 3 and max(ay, by) > node[1] + 3
                                     for (ax, ay), (bx, by) in zip(pts, pts[1:])), (pts, node))

    def test_two_links_leaving_one_side_of_a_node_do_not_cross_each_other(self):
        t = showcase.tokens("cantonese-cafe")
        svg = F.arch_layers(GROUPED, t, 1012)
        links = _links(svg)
        down, sideways = links[3], links[2]                                              # S2 -> database, S2 -> S4: both leave S2's bottom
        self.assertLess(down[0][0], sideways[0][0])                                      # the one going straight down leaves to the left of the one going right

    def test_a_swimlane_link_goes_around_a_box_in_its_way(self):
        t = showcase.tokens("cantonese-cafe")
        data = {"lanes": [{"name": "甲"}, {"name": "乙"}], "stages": ["一", "二", "三", "四"],
                "steps": [{"id": 1, "lane": "甲", "stage": 1, "text": "开始"}, {"id": 2, "lane": "甲", "stage": 2, "text": "中间一步"},
                          {"id": 3, "lane": "甲", "stage": 3, "text": "又一步"}, {"id": 4, "lane": "乙", "stage": 4, "text": "结束"},
                          {"id": 5, "lane": "甲", "stage": 4, "text": "并行"}],
                "links": [{"from": 1, "to": 5}, {"from": 1, "to": 4}, {"from": 1, "to": 2}]}
        svg = F.swimlane(data, t, 1012)
        boxes = {}
        for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="10" fill="#fff" stroke="[^"]+" stroke-width="1\.6"', svg):
            boxes[len(boxes) + 1] = tuple(map(float, m.groups()))
        links = _links(svg)
        self.assertEqual(len(links), 3)
        for (src, dst), pts in zip(((1, 5), (1, 4), (1, 2)), links):
            for sid, rect in boxes.items():
                if sid not in (src, dst):
                    self.assertFalse(_hits(pts, rect, 2), (src, dst, sid, pts))

    def test_the_gap_between_deployment_zones_holds_the_longest_label(self):
        t = showcase.tokens("cantonese-cafe")
        data = {"zones": [{"name": "设备", "col": 0, "nodes": [{"name": "手机", "role": "微信小程序"}]}, {"name": "入口", "col": 1, "nodes": [{"name": "网关", "role": "域名与证书"}]},
                          {"name": "服务器", "col": 2, "nodes": [{"name": "服务", "role": "业务规则"}]}],
                "links": [{"from": 0, "to": 1, "label": "加密访问通道"}, {"from": 1, "to": 2, "label": "转发"}]}
        svg = F.deployment(data, t, 1012)
        zones = [tuple(map(float, m)) for m in re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)" height="[\d.]+" rx="16"', svg)]
        chips = [tuple(map(float, m)) for m in re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)" height="22" rx="6"', svg)]
        self.assertEqual((len(zones), len(chips)), (3, 2))
        for (zx, zw), (cx, cw) in zip(zones, chips):
            self.assertGreater(cx, zx + zw - 0.5)
        self.assertLess(chips[0][0] + chips[0][1], zones[1][0] + 0.5)

    def test_an_atlas_has_no_title_in_the_page_header_but_a_formal_document_keeps_it(self):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                pw.chromium.launch(channel="msedge").close()
        except Exception:
            self.skipTest("Edge is not available")
        import fitz
        spec = {"title": "示例系统架构图册", "theme": "cantonese-cafe", "style": "atlas", "orientation": "landscape", "show_title": False,
                "sections": [{"title": "总体架构", "blocks": [{"type": "figure", "figure": "arch_layers", "data": ARCH, "caption": "总体架构图"}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "a.html"
            html.write_text(showcase.build(spec), encoding="utf-8")
            for header, expect in ((False, False), (True, True)):
                pdf = Path(tmp) / f"a{header}.pdf"
                make_showcase.export_pdf(html, pdf, "landscape", 0.1, spec["title"], False, header=header)
                top = fitz.open(str(pdf))[0].get_text("blocks", clip=fitz.Rect(0, 0, 842, 40))
                self.assertEqual(any("示例系统架构图册" in b[4] for b in top), expect, (header, top))

    def test_the_command_gives_an_atlas_no_title_in_the_header_and_a_formal_document_the_title(self):
        # Audit 014 (A-28 d) took the atlas's missing page-header title for a break of Luz-Project client-documents.md §3. It is the
        # standard: 系统架构图册 "不设页眉标题，第一页也不写大标题，从第一章开始（show_title: false），页脚页码居中"; 方案说明书 "页眉写文档标题".
        import make_table_pdf
        sections = [{"title": "总体架构", "blocks": [{"type": "table", "columns": ["编号", "链路", "说明"], "caption": "数据流向",
                                                      "rows": [["1", "员工报餐", "员工在截止前选择套餐提交，系统校验企业与员工状态"], ["2", "发布菜单", "平台为企业按日期和餐期发布菜单"]]}]}]
        calls = []

        def fake_export(html, pdf, orientation, min_fill, footer_title="", cover=False, header=True):
            calls.append({"footer_title": footer_title, "header": header})
            return [], [], {"pages": []}

        real_export, real_check = make_showcase.export_pdf, make_table_pdf.check_pdf
        make_showcase.export_pdf, make_table_pdf.check_pdf = fake_export, lambda pdf, max_pages=None: []
        try:
            with tempfile.TemporaryDirectory() as tmp:
                for style, extra in (("atlas", {"show_title": False}), ("formal", {})):
                    spec = {"title": "示例系统文档", "theme": "cantonese-cafe", "style": style, "orientation": "landscape", "sections": sections, **extra}
                    path = Path(tmp) / f"{style}.json"
                    path.write_text(__import__("json").dumps(spec, ensure_ascii=False), encoding="utf-8")
                    self.assertEqual(make_showcase.main([str(path), str(Path(tmp) / f"{style}.pdf")]), 0, style)
        finally:
            make_showcase.export_pdf, make_table_pdf.check_pdf = real_export, real_check
        self.assertEqual(calls, [{"footer_title": "示例系统文档", "header": False}, {"footer_title": "示例系统文档", "header": True}])


if __name__ == "__main__":
    unittest.main()
