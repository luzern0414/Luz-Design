"""Visual rules of visual-design.html in check_document.py and check_contrast.py: three weights, the brand card,
elevation and shadows, icon stroke widths and fills, template defaults, one object one icon, and the elevation tokens."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_contrast as cc  # noqa: E402
import check_document as cd  # noqa: E402

from new_session import fill_icon_slots, read_template, tab_icon_href  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ELEVATION = json.loads((ROOT / "references" / "themes.json").read_text(encoding="utf-8"))["shared"]["elevation"]
ICON = f'<link rel="icon" href="{tab_icon_href("会议助手")}">'
PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>原型</title>{icon}<style>body{{font-size:14px;color:#2B2326}} {css}</style></head><body><h1>会议助手原型</h1><h2>首页</h2>{body}</body></html>"""
MEETING = ('<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
           '<rect x="4" y="5" width="16" height="12" rx="2"/><path d="M8 21h8M12 17v4M8 9h8M8 13h5"/></svg>')
GIFT = ('<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        '<rect x="3" y="8" width="18" height="5" rx="1"/><path d="M5 13v8h14v-8M12 8v13M12 8c-2-4-6-3-5 0M12 8c2-4 6-3 5 0"/></svg>')


def run(body: str = "<p>本周会议</p>", css: str = "", allow: tuple[str, ...] = ("interface",), page: str | None = None):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "page.html"
        path.write_text(page or PAGE.format(icon=ICON, css=css, body=body), encoding="utf-8")
        cd.ALLOWED.clear()
        cd.ALLOWED.update(allow)
        errors: list[str] = []
        warnings: list[str] = []
        try:
            cd.check_html(path, errors, warnings)
        finally:
            cd.ALLOWED.clear()
    return errors, warnings


def having(items: list[str], word: str) -> list[str]:
    return [i for i in items if word in i]


class WeightTest(unittest.TestCase):
    def test_700_at_32px_passes_and_at_16px_fails(self) -> None:
        errors, _ = run('<div class="num">128</div>', ".num{font-size:32px;font-weight:700}")
        self.assertFalse(having(errors, "font weight"))
        errors, _ = run('<div class="title">今日待办</div>', ".title{font-size:16px;font-weight:700}")
        self.assertTrue(having(errors, "font weight 700 at 16px"))

    def test_700_without_size_is_judged_by_the_matched_elements(self) -> None:
        errors, _ = run('<div class="kpi"><b>128</b></div>', ".kpi{font-size:32px} .kpi b{font-weight:700}")
        self.assertFalse(having(errors, "font weight"))
        errors, _ = run('<div class="list"><b>客户周会</b></div>', ".list b{font-weight:700}")
        self.assertTrue(having(errors, "font weight 700 in '.list b' on 14px"))
        errors, _ = run("<p>本周会议</p>", ".nowhere{font-weight:bold}")
        self.assertTrue(having(errors, "without a font size"))

    def test_500_and_thin_weights_are_errors(self) -> None:
        for weight in ("500", "300", "800"):
            with self.subTest(weight=weight):
                errors, _ = run('<p class="x">本周会议</p>', f".x{{font-weight:{weight}}}")
                self.assertTrue(having(errors, "outside 400/600/700"))

    def test_inline_700_on_small_text_is_an_error(self) -> None:
        errors, _ = run('<p style="font-weight:700">本周会议</p>')
        self.assertTrue(having(errors, "inline font weight 700"))

    def test_made_by_credit_is_metadata_but_content_is_not(self) -> None:
        for credit in ("本页由 Luz 生成", "本报告由市场部编制", "内容由 AI 整理", "由Claude生成", "由运营组整理"):
            with self.subTest(credit=credit):
                errors, _ = run(f"<p>{credit}</p>")
                self.assertTrue(having(errors, "production metadata"), errors)
        for content in ("这次改版的缘由是旧报表生成太慢", "理由很简单：系统生成编号更可靠", "订单号由系统自动生成，无需手填",
                        "由于数据由门店系统生成，月底统一对账", "会员自由选择课程后生成预约单"):
            with self.subTest(content=content):
                errors, _ = run(f"<p>{content}</p>")
                self.assertFalse(having(errors, "production metadata"), errors)

    def test_interface_pages_keep_their_application_shell(self) -> None:
        # The Luz-System prototype skeleton puts its menu in <nav>; documents still refuse a shell.
        shell = '<nav><a href="#members">会员列表</a></nav><p>共 32 位会员</p>'
        errors, _ = run(shell)
        self.assertFalse(having(errors, "application shell"))
        errors, _ = run(shell, allow=())
        self.assertTrue(having(errors, "application shell <nav>"))

    def test_interface_version_information_is_not_metadata(self) -> None:
        # Admin consoles show their version (Luz-System admin-design.html 版本信息); documents still may not.
        version = '<div class="app-version"><h3>版本信息</h3><p>版本号：1.4.2</p><p>发布时间 2026-10-29 10:00</p></div><p>今日订单 32 笔</p>'
        errors, _ = run(version)
        self.assertFalse(having(errors, "production metadata") + having(errors, "timestamp") + having(errors, "accessory"), errors)
        errors, _ = run(version.replace('class="app-version"', 'class="footer"'))
        self.assertTrue(having(errors, "production metadata"), errors)
        errors, _ = run(version, allow=())
        self.assertTrue(having(errors, "production metadata"), errors)

    def test_default_bold_tags_must_be_set_to_600(self) -> None:
        table = "<table><tr><th>客户</th></tr><tr><td>甲</td></tr></table><h3>本周</h3><p><strong>重点</strong></p>"
        _, warnings = run(table, allow=())
        self.assertEqual(sorted(w.split(">")[0] for w in having(warnings, "renders 700 by default")), ["<h3", "<strong", "<th"])
        _, warnings = run(table, "th,h3,strong{font-weight:600}", allow=())
        self.assertFalse(having(warnings, "renders 700 by default"))
        # Inline weight decides the occurrence (pasted pages keep only inline styles); one bare occurrence still warns.
        _, warnings = run('<p><strong style="font-weight:600">重点</strong></p>', allow=())
        self.assertFalse(having(warnings, "renders 700 by default"))
        _, warnings = run('<p><strong style="font-weight:600">重点</strong><strong>次要</strong></p>', allow=())
        self.assertTrue(having(warnings, "<strong> renders 700 by default"))

    def test_reading_pages_warn_on_small_700(self) -> None:
        _, warnings = run("<h3>本周</h3>", "h3{font-size:20px;font-weight:700}", allow=())
        self.assertTrue(having(warnings, "font weight 700 at 20px"))
        _, warnings = run("<h2>本周</h2>", "h2{font-size:24px;font-weight:700}", allow=())
        self.assertFalse(having(warnings, "font weight"))


class BrandCardTest(unittest.TestCase):
    def test_primary_brand_step_passes(self) -> None:
        errors, _ = run('<div class="brand-card">本月新增 128</div>', ".brand-card{background:#4A5BD6;color:#fff}")
        self.assertFalse(having(errors, "brand card") + having(errors, "dark or saturated"))

    def test_light_step_dark_neutral_and_reading_pages_fail(self) -> None:
        errors, _ = run('<div class="brand-card">本月新增</div>', ".brand-card{background:#7782E3;color:#fff}")
        self.assertTrue(having(errors, "brand card '.brand-card': text on #7782E3"))
        errors, _ = run('<div class="brand-card">本月新增</div>', ".brand-card{background:#333333;color:#fff}")
        self.assertTrue(having(errors, "dark neutral"))
        for neutral in ("#2B2326", "#3A3F44"):
            errors, _ = run('<div class="brand-card">本月新增</div>', ".brand-card{background:%s;color:#fff}" % neutral)
            self.assertTrue(having(errors, "dark neutral"), neutral)

    def test_deep_theme_primaries_are_hues(self) -> None:
        # Coffee, salon, cantonese-cafe and western-light primaries in themes.json (deep brown, slate, green).
        for hue in ("#6B4A34", "#573B2A", "#35546E", "#25594A", "#4F6E55"):
            errors, _ = run('<div class="brand-card">本月新增</div>', ".brand-card{background:%s;color:#fff}" % hue)
            self.assertFalse(having(errors, "dark neutral"), hue)
        errors, _ = run('<div class="brand-card">本月新增</div>', ".brand-card{background:#4A5BD6;color:#fff}", allow=())
        self.assertTrue(having(errors, "dark or saturated fill"))

    def test_one_brand_card_per_screen(self) -> None:
        css = ".brand-card{background:#4A5BD6;color:#fff}"
        two = '<div data-page-id="P-001"><div class="brand-card">录音</div><div class="brand-card">指标</div></div>'
        self.assertTrue(having(run(two, css)[0], "2 brand cards on one screen (P-001)"))
        apart = '<div class="phone"><div class="brand-card">录音</div></div><div class="phone"><div class="brand-card">指标</div></div>'
        self.assertFalse(having(run(apart, css)[0], "brand cards on one screen"))

    def test_translucent_white_text_inside_the_card_is_measured_on_the_card(self) -> None:
        body = '<div class="brand-card">本月新增<span class="sub">较上周</span></div>'
        for fill, alpha, ok in (("#3A48B0", ".8", True), ("#4A5BD6", ".9", True), ("#4A5BD6", ".6", False)):
            with self.subTest(fill=fill, alpha=alpha):
                css = f".brand-card{{background:{fill};color:#fff}} .brand-card .sub{{color:rgba(255,255,255,{alpha})}}"
                self.assertEqual(not having(run(body, css)[0], "color too light"), ok)

    def test_a_brand_card_is_not_the_header_brand_mark(self) -> None:
        body = f'<aside class="sidebar"><div class="brand-card">{MEETING}本月会议</div></aside>'
        _, warnings = run(body, ".brand-card{background:#4A5BD6;color:#fff}")
        self.assertTrue(having(warnings, "brand mark"))


class ElevationTest(unittest.TestCase):
    def card_css(self, shadow: str, selector: str = ".card") -> str:
        return f"{selector}{{background:#fff;box-shadow:{shadow}}}"

    def test_the_five_level_tokens_pass(self) -> None:
        css = (self.card_css(ELEVATION["level1"]) + self.card_css(ELEVATION["level2"], ".card:hover")
               + self.card_css(ELEVATION["level3"], ".dropdown") + self.card_css(ELEVATION["level4"], ".modal"))
        errors, warnings = run('<div class="card">客户周会</div>', css)
        self.assertFalse(having(errors, "shadow") + having(errors, "glow") + having(errors, "bevel"))
        self.assertFalse(having(warnings, "shadow"))

    def test_edges_highlights_and_rings_are_lines(self) -> None:
        for shadow in (ELEVATION["highlight"], ELEVATION["highlightSolid"], "0 1px 0 #3A48B0", "0 0 0 3px rgba(74,91,214,.24)",
                       f"{ELEVATION['highlightSolid']}, 0 1px 0 #3A48B0"):
            with self.subTest(shadow=shadow):
                errors, warnings = run('<button class="primary">保存</button>', self.card_css(shadow, ".primary"))
                self.assertFalse(having(errors, "shadow") + having(errors, "glow") + having(errors, "bevel"))
                self.assertFalse(having(warnings, "shadow"))

    def test_bevels_glows_and_primary_shadows_are_errors(self) -> None:
        self.assertTrue(having(run(css=self.card_css("inset 0 -4px 0 rgba(0,0,0,.2)", "p"))[0], "bevel shadow"))
        self.assertTrue(having(run(css=self.card_css("0 8px 16px rgba(74,91,214,.3)", "p"))[0], "coloured shadow"))
        self.assertTrue(having(run(css=self.card_css("0 0 16px rgba(255,255,255,.8)", "p"))[0], "glow"))

    def test_a_dark_theme_tint_is_allowed(self) -> None:
        errors, _ = run(css=self.card_css("0 2px 4px rgba(11,27,88,.06), 0 8px 16px rgba(11,27,88,.08)", ".card"))
        self.assertFalse(having(errors, "shadow"))

    def test_shadows_beyond_the_levels_and_upward_shadows_warn(self) -> None:
        _, warnings = run(css=self.card_css("0 12px 40px rgba(16,24,40,.08)", ".card"))
        self.assertTrue(having(warnings, "beyond the elevation levels"))
        _, warnings = run(css=self.card_css("0 -4px 8px rgba(16,24,40,.06)", ".card"))
        self.assertTrue(having(warnings, "upward shadow"))
        _, warnings = run(css=self.card_css("0 -4px 8px rgba(16,24,40,.06)", ".bottom-bar"))
        self.assertFalse(having(warnings, "upward shadow"))

    def test_reading_pages_have_no_card_shadows(self) -> None:
        _, warnings = run(css=self.card_css(ELEVATION["level1"], ".card"), allow=())
        self.assertTrue(having(warnings, "shadow in a reading page"))
        _, warnings = run(css="p{border-bottom:1px solid #EEE}", allow=())
        self.assertFalse(having(warnings, "shadow"))


class IconAndFillTest(unittest.TestCase):
    def icon(self, width: str) -> str:
        return MEETING.replace('stroke-width="2"', f'stroke-width="{width}"')

    def test_stroke_widths(self) -> None:
        errors, warnings = run(self.icon("1.5") + "<p>会议</p>")
        self.assertTrue(having(warnings, "icon stroke width 1.5"))
        errors, warnings = run(self.icon("2") + "<p>会议</p>" + GIFT.replace('stroke-width="2"', 'stroke-width="1.75"') + "<p>礼券</p>")
        self.assertFalse(having(errors, "mixed icon stroke widths") + having(warnings, "icon stroke width"))
        errors, _ = run(self.icon("1.5") + "<p>会议</p>" + GIFT + "<p>礼券</p>")
        self.assertTrue(having(errors, "mixed icon stroke widths"))

    def test_fills_come_from_the_theme_steps(self) -> None:
        art = '<svg class="ill" viewBox="0 0 160 120"><rect width="40" height="30" fill="{a}"/><circle r="9" fill="{b}"/></svg>'
        _, warnings = run(art.format(a="#123456", b="#E6E9FA"))
        self.assertTrue(having(warnings, "#123456"))
        _, warnings = run(art.format(a="#E6E9FA", b="#F2F2F2"))
        self.assertFalse(having(warnings, "fills outside the theme"))

    def test_template_default_style_warns(self) -> None:
        page = fill_icon_slots(read_template(ROOT, "document.html"), "会议纪要")
        _, warnings = run(page=page, allow=())
        self.assertTrue(having(warnings, "default style of template document.html"))


class ControlFillTest(unittest.TestCase):
    """Controls take a solid fill whatever their class is called; containers do not (visual-design.html 配色)."""

    FILL = "{{background:#0958d9;color:#fff}}"

    def fill_errors(self, body: str, selector: str) -> list[str]:
        errors, _ = run(body, selector + self.FILL.format())
        return having(errors, "dark or saturated fill")

    def test_controls_by_element(self) -> None:
        for body, selector in (('<button class="btn-primary" type="button">保存</button>', ".btn-primary"),
                               ('<button class="ok" type="button">确认</button>', ".ok"),
                               ('<button class="ok" type="button">确认</button>', ".ok:hover"),
                               ('<div role="dialog"><a class="confirm" role="button">删除</a></div>', '[role=dialog] .confirm'),
                               ('<a class="cta-btn" href="#book">立即预约</a>', ".cta-btn"),
                               ('<input class="go" type="submit" value="提交">', ".go"),
                               ('<div role="tablist"><span class="seg on" role="tab">本周</span></div>', ".seg.on"),
                               ('<dialog><button class="ok" type="button" data-control="confirm">确认</button></dialog>', "dialog .ok")):
            with self.subTest(selector=selector):
                self.assertEqual(self.fill_errors(body, selector), [])

    def test_containers_and_mixed_selectors_still_fail(self) -> None:
        for body, selector in (('<section class="hero"><p>本周新品</p></section>', ".hero"),
                               ('<button class="ok" type="button">确认</button><div class="ok"><p>已完成</p></div>', ".ok"),
                               ('<button class="ok" type="button">确认</button><section class="hero"><p>新品</p></section>', ".ok, .hero"),
                               ('<a class="more" href="#all">全部</a>', ".more"),
                               ('<p>没有元素用这个类</p>', ".ghost")):
            with self.subTest(selector=selector):
                self.assertTrue(self.fill_errors(body, selector))

class GeneratedIconTest(unittest.TestCase):
    """Generated icons may stand in entries and illustrations; control icons stay line vectors (visual-design.html 图像生成)."""

    IMG = '<img class="icon" src="data:image/png;base64,iVBORw0KGgo=" alt="">'

    def test_entries_and_illustrations_may_use_generated_images(self) -> None:
        for body in (f'<section><h2>常用</h2><div class="grid"><a class="entry" href="#card">{self.IMG}<span>会员卡</span></a></div></section>',
                     f'<section><h2>入口</h2><button class="tile" type="button">{self.IMG}<span>领取礼券</span></button></section>',
                     f'<section><h2>暂无会议</h2><img class="ill" src="data:image/png;base64,iVBORw0KGgo=" alt=""><p>还没有会议</p></section>'):
            with self.subTest(body=body[:40]):
                errors, _ = run(body)
                self.assertFalse(having(errors, "raster icon"), errors)

    def test_control_areas_keep_line_vectors(self) -> None:
        for body in (f'<nav><a href="#home">{self.IMG}首页</a></nav><p>首页内容</p>',
                     f'<div role="tablist"><span role="tab">{self.IMG}我的</span></div><p>内容</p>',
                     f'<div role="toolbar"><button type="button">{self.IMG}导出</button></div><p>内容</p>',
                     f'<table><tr><th>状态</th></tr><tr><td>{self.IMG}已完成</td></tr></table>'):
            with self.subTest(body=body[:40]):
                errors, _ = run(body)
                self.assertTrue(having(errors, "raster icon in a control area"), errors)

class LocalLinkTest(unittest.TestCase):
    def test_script_brackets_are_not_links(self) -> None:
        import validate_session
        import validate_skill
        html = '<a href="a.html">A</a><script>const r = map[key](event);</script><p>[x](y.md)</p>'
        markdown = "[方案](plan.md) 与 `arr[0](x)`"
        for find in (validate_session.local_links, validate_skill.local_targets):
            with self.subTest(find=find.__module__):
                self.assertEqual(find(html, html=True), ["a.html"])
                self.assertEqual(find(markdown), ["plan.md"])

class OneObjectOneIconTest(unittest.TestCase):
    def test_list_rows_of_one_kind_share_the_object_icon(self) -> None:
        rows = "".join(f'<li class="row">{MEETING}<span>{t}</span><span class="time">10-2{i} 09:30</span></li>'
                       for i, t in enumerate(("客户周会", "产品评审", "季度复盘")))
        errors, _ = run(f'<ul class="meetings">{rows}</ul>')
        self.assertFalse(having(errors, "one icon labels different things"))

    def test_entries_sharing_a_pictogram_are_still_errors(self) -> None:
        grid = f'<div class="grid"><a class="entry">{GIFT}<span>新人礼券</span></a><a class="entry">{GIFT}<span>每日抽奖</span></a></div>'
        self.assertTrue(having(run(grid)[0], "one icon labels different things"))
        mixed = "".join(f'<li class="row">{icon}<span>{t}</span><span>本周 3 次</span></li>'
                        for icon, t in ((GIFT, "新人礼券"), (GIFT, "每日抽奖"), (MEETING, "客户周会")))
        self.assertTrue(having(run(f"<ul>{mixed}</ul>")[0], "one icon labels different things"))
        features = "".join(f'<li class="feature">{GIFT}<b>{t}</b><span>自动完成，减少人工操作</span></li>'
                           for t in ("智能排班", "自动对账", "会员提醒"))
        self.assertTrue(having(run(f"<ul>{features}</ul>", "b{font-weight:600}")[0], "one icon labels different things"))


class ElevationTokenTest(unittest.TestCase):
    def failing(self, **changes: str) -> list[str]:
        tokens = {**ELEVATION, **changes}
        return [label for label, ok, _ in cc.elevation_rules(tokens) if not ok]

    def test_shared_tokens_pass(self) -> None:
        self.assertEqual(self.failing(), [])

    def test_layer_count_direction_and_alpha(self) -> None:
        self.assertIn("level1 两层外阴影", self.failing(level1="0 1px 2px rgba(16,24,40,.06)"))
        self.assertIn("level2 只向下", self.failing(level2="0 -2px 4px rgba(16,24,40,.06), 0 8px 16px rgba(16,24,40,.08)"))
        self.assertIn("level3 单层透明度 <= 0.2", self.failing(level3="0 4px 8px rgba(16,24,40,.06), 0 12px 24px rgba(16,24,40,.3)"))
        self.assertIn("level4 深色阴影", self.failing(level4="0 8px 16px rgba(74,91,214,.08), 0 24px 48px rgba(74,91,214,.14)"))

    def test_levels_grow_softer_and_lighter(self) -> None:
        self.assertIn("level2 → level3 远处更大更柔",
                      self.failing(level3="0 4px 8px rgba(16,24,40,.06), 0 6px 12px rgba(16,24,40,.04)"))
        self.assertIn("level3 → level4 远处更淡",
                      self.failing(level4="0 8px 16px rgba(16,24,40,.08), 0 24px 30px rgba(16,24,40,.2)"))

    def test_line_tokens(self) -> None:
        self.assertIn("highlightSolid 白色内顶边 0.16–0.24", self.failing(highlightSolid="inset 0 1px 0 rgba(255,255,255,.7)"))
        self.assertIn("scrim 深色 0.40–0.50", self.failing(scrim="rgba(16,24,40,.7)"))
        self.assertIn("hairline 深色 0.06–0.10", self.failing(hairline="rgba(16,24,40,.2)"))
        self.assertIn("buttonEdge 向下 1–2 像素无模糊", self.failing(buttonEdge="0 3px 0"))


if __name__ == "__main__":
    unittest.main()
