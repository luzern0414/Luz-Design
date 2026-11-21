import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


def audit(html: str, *args: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "audit_rendered.py"), str(page), *args], capture_output=True, text=True, encoding="utf-8")
        return run.returncode, run.stdout


GOOD = "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><style>body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}button{min-height:40px;font:inherit}</style><h1 style='font-size:22px;font-weight:700'>标题</h1><p>正文</p><button>确定</button>"


class ReportPolicyTests(unittest.TestCase):
    """通用审计不制造组件配额；明确要求的能力仍须验证。"""

    def data(self, **changes):
        result = {"small": [], "italic": [], "weight": [], "contrast": [],
                  "overflowX": False, "fonts": ["sans-serif"], "targets": [],
                  "foreign": [], "components": [], "pageLum": 1, "centerLum": 1}
        result.update(changes)
        return result

    def test_reading_page_has_no_component_quota_by_default(self):
        sys.path.insert(0, str(HERE))
        from audit_rendered import report
        self.assertEqual(report("initial", self.data(), [], library=["element-plus"]), [])

    def test_explicit_component_minimum_is_still_checked(self):
        from audit_rendered import report
        self.assertTrue(report("initial", self.data(components=["el-button"]), [],
                               library=["element-plus"], min_components=2))

    def test_foreign_control_is_rejected_without_a_component_quota(self):
        from audit_rendered import report
        errors = report("initial", self.data(foreign=["button.handmade"]), [], library=["element-plus"])
        self.assertTrue(any("自造控件" in error for error in errors), errors)

    def test_explicit_dark_request_still_rejects_a_light_result(self):
        from audit_rendered import report
        errors = report("initial", self.data(), [], scheme="dark")
        self.assertTrue(any("scheme dark" in error for error in errors), errors)


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class AuditRenderedTests(unittest.TestCase):
    def test_custom_component_colours_do_not_mask_character_icons(self):
        html = GOOD.replace("<html ", "<html data-ui-surface='app' ").replace("<p>正文</p>", """
        <style>#tint{--brand:green;background:color-mix(in srgb,var(--brand) 4%,white)}
        #chip::before{content:'';position:absolute;width:36px;height:20px;background:linear-gradient(blue,white)}
        #glyph::before{content:'★'}</style>
        <div id="tint">已完成</div><span id="chip">标签</span>
        <button id="warning" style="background:#fff9da">查看提醒</button>
        <span id="person" class="avatar">王</span>
        <button aria-label="收藏"><i id="glyph" class="icon" aria-hidden="true"></i></button>
        <button id="arrow" aria-label="返回">←</button>""")
        code, out = audit(html)
        self.assertEqual(code, 1)
        self.assertIn("green-interface-color at #tint", out)
        for location in ("#chip::before", "#warning"):
            self.assertNotIn(f" at {location}", out)
        for rule, location in (("graphical-avatar-required", "#person"),
                               ("text-icon", "#glyph"), ("text-icon", "#arrow")):
            self.assertIn(f"{rule} at {location}", out)

    def test_pastel_components_on_a_white_canvas(self):
        tokens = (HERE.parent / "kit/frontend/shared/pastel-300.css").read_text(encoding="utf-8")
        names = re.findall(r"(--pastel-[\w-]+-300):", tokens)
        self.assertEqual(len(set(names)), 10)
        buttons = "".join(f'<button style="background:var({name})">选择</button>' for name in names)
        html = GOOD.replace("</style>", tokens + "button{background:white}</style>").replace("<p>正文</p>", buttons + """
        <style>:root{--mauve:#c5a5cf} .card{background:linear-gradient(135deg, #BFA9DD 0%, #E1A8C1 65%, white)}
        .card::before{content:'';display:block;height:12px;background:radial-gradient(circle, var(--mauve), #9fc5e5)}</style>
        <main><article class="card"><h2>待办</h2><button style="background:var(--mauve)">完成</button>
        <span class="icon" style="display:inline-block;background:#ECD77D"><svg width="24" height="24"><circle cx="12" cy="12" r="6"/></svg></span>
        </article></main>""")
        code, out = audit(html, "--frontend-visuals")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_global_surfaces_stay_white_with_custom_local_colours(self):
        html = GOOD.replace("<p>正文</p>", """
        <style>body{background:#9ACFB5} button{background:white} #veil::before{content:'';position:fixed;inset:0;background:#9FC5E5}
        #mixed{background:linear-gradient(to right,#BFA9DD,red 30%,#E1A8C1)}
        #variant{--pastel-mint-300:#bfe4d0;background:var(--pastel-mint-300)}</style>
        <main id="canvas" style="background:linear-gradient(#9FC5E5,#96CDCA)">
        <nav id="navigation" style="background:#ECD77D">导航</nav><button id="veil">保存</button>
        <button id="mixed">打开</button><article id="variant">待办</article></main>""")
        code, out = audit(html, "--frontend-visuals")
        self.assertEqual(code, 1, out)
        for location in ("body", "#canvas", "#navigation", "#veil::before"):
            self.assertIn(f"nonwhite-background at {location}", out)
        self.assertIn("green-interface-color at #variant", out)
        for location in ("#mixed",):
            self.assertNotIn(f" at {location}", out)

    def test_custom_accents_and_multistop_gradients_pass_without_loading_a_palette(self):
        html = GOOD.replace("<p>正文</p>", """
        <style>
          .card { --brand: #48206c; background: rgba(241, 213, 193, .75); }
          .card button { background: linear-gradient(110deg, var(--brand), #15384f 45%, #503213); color: white; }
          .card button:hover { background: #371951; }
          .card .icon { display: inline-block; background: #84a3d5; }
        </style>
        <main><article class="card"><button>保存</button>
        <span class="icon"><svg width="24" height="24"><circle cx="12" cy="12" r="6"/></svg></span>
        </article></main>""")
        code, out = audit(html, "--frontend-visuals")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_white_canvas_in_an_empty_or_dark_viewport(self):
        html = '<!doctype html><html style="color-scheme:dark"><title>界面</title><body></body></html>'
        for fill, expected in (("transparent", "html"), ("#9FC5E5", "body")):
            code, out = audit(html.replace("<body>", f'<body style="background:{fill}">'), "--frontend-visuals", "--scheme", "dark")
            self.assertEqual(code, 1, out)
            self.assertIn(f"nonwhite-background at {expected}", out)
        code, out = audit(html.replace("<body>", '<body style="background:white">'), "--frontend-visuals", "--scheme", "dark")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_frontend_accepts_graphical_icons_labels_and_coloured_foregrounds(self):
        icon = '<svg width="24" height="24" viewBox="0 0 24 24"><title>用户</title><circle cx="12" cy="12" r="6"/></svg>'
        html = GOOD.replace("</style>", "button{background:white}</style>").replace("<p>正文</p>",
            f'<span class="avatar">{icon}</span><span>王女士</span>'
            f'<button class="icon-button">{icon} 保存</button><button aria-label="关闭">{icon}</button>'
            '<span style="color:#13557a">消息</span><button>1</button>')
        code, out = audit(html, "--frontend-visuals")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_a_clean_page_passes(self):
        code, out = audit(GOOD)
        self.assertEqual((code, out.strip()), (0, "audit: ok"))

    def test_explicit_dark_request_is_not_silently_ignored(self):
        code, out = audit(GOOD, "--scheme", "dark")
        self.assertEqual(code, 1, out)
        self.assertIn("scheme dark", out)

    def test_small_italic_light_and_bold_text_are_found_on_the_rendered_page(self):
        bad = GOOD.replace("<p>正文</p>", "<p style='font-size:12px'>小字</p><p style='font-style:italic'>斜体</p><p style='color:#bbb'>浅色</p><p style='font-weight:700'>粗体</p><script>document.body.append(Object.assign(document.createElement('p'),{textContent:'脚本加的小字',style:'font-size:11px'}))</script>")
        code, out = audit(bad)
        self.assertEqual(code, 1)
        for needle in ("under 14px", "italic", "contrast", "weight outside", "脚本加的小字"):
            self.assertIn(needle, out)

    def test_the_simulated_device_chrome_is_not_judged_but_real_text_still_is(self):
        faint = "<p style='color:#fff'>浅色字</p>"
        self.assertEqual(audit(GOOD.replace("<p>正文</p>", faint))[0], 1, "faint text is found")
        shell = "<div data-shell aria-hidden='true'><span style='color:#fff'>9:41</span></div>"
        self.assertEqual(audit(GOOD.replace("<p>正文</p>", shell))[1].strip(), "audit: ok", "a hidden shell element (the status bar clock) is device chrome")
        for attrs in ("data-shell", "aria-hidden='true'"):
            code, out = audit(GOOD.replace("<p>正文</p>", f"<div {attrs}><span style='color:#fff'>9:41</span></div>"))
            self.assertEqual(code, 1, f"{attrs} alone does not exempt a text: it must be both")

    def test_modern_colour_functions_are_measured_too(self):
        light = GOOD.replace("<p>正文</p>", "<p style='color: oklch(0.85 0 0)'>浅色</p><p style='color: color-mix(in oklch, white 80%, black)'>混色</p>")
        code, out = audit(light)
        self.assertEqual(code, 1)
        self.assertIn("contrast", out)
        dark = GOOD.replace("<p>正文</p>", "<p style='color: oklch(0.3 0.02 250)'>深色</p>")
        self.assertEqual(audit(dark)[1].strip(), "audit: ok")

    def test_touch_targets_are_judged_by_the_width_of_the_viewport(self):
        small = GOOD.replace("min-height:40px", "height:30px")
        self.assertEqual(audit(small, "--width", "1280")[0], 0)               # a desktop pointer needs 24 px
        code, out = audit(small, "--width", "390")                           # a phone needs 40 px
        self.assertEqual(code, 1)
        self.assertIn("touch targets", out)

    def test_a_control_extended_by_an_absolutely_positioned_pseudo_element_has_that_hit_area(self):
        extended = GOOD.replace("min-height:40px", "height:30px;position:relative").replace("</style>", "button::after{content:'';position:absolute;inset:-8px 0}</style>")
        self.assertEqual(audit(extended, "--width", "390")[0], 0)            # 30 + 16 = 46 px of hit area
        short = GOOD.replace("min-height:40px", "height:30px;position:relative").replace("</style>", "button::after{content:'';position:absolute;inset:-2px 0}</style>")
        code, out = audit(short, "--width", "390")                          # 34 px is still too small
        self.assertEqual(code, 1)
        self.assertIn("touch targets", out)

    def test_transition_all_and_will_change_are_found_in_the_style_sheet(self):
        code, out = audit(GOOD.replace("</style>", "button{transition:all .2s;will-change:transform}</style>"))
        self.assertEqual(code, 1)
        self.assertIn("transition: all", out)
        self.assertIn("will-change", out)


# A page that really uses a component library: six different components, every control inside one of them.
LIBRARY_PAGE = ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><meta name='viewport' content='width=device-width, initial-scale=1'>"
                "<style>body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}button,input,select{min-height:32px;font:inherit}input,select{outline:0}</style>"
                "<div class='el-card'><div class='el-card__header'>订单</div>"
                "<button class='el-button el-button--primary' type='button'>提交</button>"
                "<div class='el-input'><input class='el-input__inner' aria-label='姓名'></div>"
                "<span class='el-tag'>待处理</span><div class='el-switch' role='switch' aria-checked='true'>开</div>"
                "<table class='el-table'><tr><td class='el-table__cell'>甲</td></tr></table>"
                "<dialog open class='el-dialog'><button class='el-button' type='button'>确定</button></dialog></div>")


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class ComponentSourceTests(unittest.TestCase):
    def test_a_page_built_from_the_library_passes_by_id_or_by_prefix(self):
        for library in ("element-plus", "el-"):
            code, out = audit(LIBRARY_PAGE, "--library", library)
            self.assertEqual((code, out.strip()), (0, "audit: ok"), (library, out))

    def test_a_hand_written_control_is_reported(self):
        bad = LIBRARY_PAGE.replace("</div>", "<button class='my-btn' type='button'>自己画的</button><select class='sel'><option>甲</option></select></div>", 1)
        code, out = audit(bad, "--library", "element-plus")
        self.assertEqual(code, 1)
        self.assertIn("自造控件", out)
        self.assertIn("button.my-btn", out)
        self.assertIn("select.sel", out)
        self.assertNotIn("el-button", out.split("自造控件")[1].split("]")[0])        # the library's own buttons are not listed

    def test_a_reading_page_does_not_need_extra_controls(self):
        own = "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><style>body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}</style><div class='el-card'><p>正文</p></div>"
        code, out = audit(own, "--library", "element-plus")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_one_labelled_component_without_an_icon_passes(self):
        page = GOOD.replace("<button>", "<button class='el-button'>")
        code, out = audit(page, "--library", "element-plus")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_the_library_must_be_known(self):
        code, out = audit(LIBRARY_PAGE, "--library", "no-such-library")
        self.assertNotEqual(code, 0)

    def test_a_custom_element_with_the_library_prefix_counts_as_a_component(self):
        page = LIBRARY_PAGE.replace("<span class='el-tag'>待处理</span>", "<t-tag>待处理</t-tag>").replace("el-", "t-")
        code, out = audit(page, "--library", "tdesign")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_without_the_option_nothing_about_components_is_checked(self):
        self.assertEqual(audit(GOOD)[1].strip(), "audit: ok")


HEAD = "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><meta name='viewport' content='width=device-width, initial-scale=1'>"
BASE = "<style>body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}button,input{font:inherit}input{outline:0}%s</style>"


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class ProductInterfaceTests(unittest.TestCase):
    """Product interfaces (admin, mini-program, agent) may use 12 px for time, unit and badge text; websites and reading pages may not."""

    def test_min_font_moves_the_smallest_size_and_defaults_to_14(self):
        small = GOOD.replace("<p>正文</p>", "<p style='font-size:12px'>辅助</p>")
        code, out = audit(small)
        self.assertEqual(code, 1)
        self.assertIn("font size under 14px", out)
        self.assertEqual(audit(small, "--min-font", "12")[1].strip(), "audit: ok")
        code, out = audit(GOOD.replace("<p>正文</p>", "<p style='font-size:11px'>太小</p>"), "--min-font", "12")
        self.assertEqual(code, 1)
        self.assertIn("font size under 12px", out)

    def test_a_field_is_judged_by_its_library_wrapper_not_by_the_bare_input(self):
        wrapped = HEAD + BASE % ".el-input__wrapper{display:flex;height:44px}.el-input__inner{height:30px;border:0}" + "<div class='el-input'><div class='el-input__wrapper'><input class='el-input__inner' aria-label='姓名'></div></div>"
        args = ("--width", "390", "--library", "el-", "--min-components", "1")
        self.assertEqual(audit(wrapped, *args)[1].strip(), "audit: ok")
        bare = HEAD + BASE % ".el-input__inner{height:30px;border:0}" + "<div class='el-input'><input class='el-input__inner' aria-label='姓名'></div>"
        code, out = audit(bare, *args)
        self.assertEqual(code, 1)
        self.assertIn("touch targets", out)

    def test_the_library_pagination_buttons_are_its_own_but_the_same_class_elsewhere_is_not(self):
        pager = HEAD + BASE % "button{min-height:32px}" + "<div class='el-pagination'><button class='btn-prev' type='button'>上一页</button><button class='btn-next' type='button'>下一页</button></div>"
        args = ("--library", "el-", "--min-components", "1")
        self.assertEqual(audit(pager, *args)[1].strip(), "audit: ok")
        elsewhere = HEAD + BASE % "button{min-height:32px}" + "<div class='el-card'><button class='btn-prev' type='button'>上一页</button></div>"
        code, out = audit(elsewhere, *args)
        self.assertEqual(code, 1)
        self.assertIn("button.btn-prev", out)


def kit_page(roots: str, extra: str = "", shell: str = "") -> str:
    return HEAD + BASE % "button{min-height:32px}" + shell + roots + extra


def kit_roots(n: int = 6, same: bool = False) -> str:
    """n component roots as the luz-kit prototypes draw them: the id of the component in data-cid, a real control inside."""
    return "".join(f"<div class='mpcard00{i}' data-cid='MP-CARD-{1 if same else i:03d}'><button type='button'>按钮{i}</button></div>" for i in range(1, n + 1))


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class ComponentRootAttributeTests(unittest.TestCase):
    """--library luz-kit: a library with an ``attr`` is read by data-cid on the component root, not by class prefix."""

    def test_the_registry_names_the_attribute_and_no_class_prefix_is_used_for_it(self):
        sys.path.insert(0, str(HERE))
        import audit_rendered

        self.assertEqual(audit_rendered.resolve_library_attrs(["luz-kit"]), ["data-cid"])
        self.assertEqual(audit_rendered.resolve_library(["luz-kit"]), [])
        self.assertEqual(audit_rendered.resolve_library_attrs(["element-plus", "el-"]), [])

    def test_controls_inside_component_roots_pass_and_six_kinds_are_counted(self):
        code, out = audit(kit_page(kit_roots()), "--library", "luz-kit")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_a_hand_written_control_outside_a_component_root_is_reported(self):
        bad = kit_page(kit_roots(), "<button class='my-btn' type='button'>自己画的</button>")
        code, out = audit(bad, "--library", "luz-kit")
        self.assertEqual(code, 1)
        self.assertIn("自造控件", out)
        self.assertIn("button.my-btn", out)
        self.assertNotIn("按钮1", out)                                          # the buttons inside the roots are the library's own

    def test_a_select_next_to_the_component_roots_is_reported_while_the_ones_inside_are_not(self):
        page = kit_page(kit_roots(5) + "<div class='mpcard006' data-cid='MP-CARD-006'><button type='button'>按钮6</button></div><select class='sel'><option>甲</option></select>")
        code, out = audit(page, "--library", "luz-kit")
        self.assertEqual(code, 1)
        self.assertIn("select.sel", out)

    def test_only_an_explicit_minimum_rejects_fewer_kinds_and_counts_distinct_ids(self):
        self.assertEqual(audit(kit_page(kit_roots(1)), "--library", "luz-kit")[0], 0)
        code, out = audit(kit_page(kit_roots(3)), "--library", "luz-kit", "--min-components", "6")
        self.assertEqual(code, 1)
        self.assertIn("只有 3 种组件库", out)
        code, out = audit(kit_page(kit_roots(8, same=True)), "--library", "luz-kit", "--min-components", "6")
        self.assertEqual(code, 1)
        self.assertIn("只有 1 种组件库", out)
        self.assertEqual(audit(kit_page(kit_roots(3)), "--library", "luz-kit", "--min-components", "3")[1].strip(), "audit: ok")

    def test_the_prototype_shell_is_not_product_interface(self):
        shell = "<aside data-shell><button class='cfg' type='button'>主题色</button><div data-cid='MP-CARD-099'><button type='button'>配置里的</button></div></aside>"
        code, out = audit(kit_page(kit_roots(5), shell=shell), "--library", "luz-kit", "--min-components", "6")
        self.assertEqual(code, 1)                                              # the shell's data-cid is not counted: five kinds, six needed
        self.assertIn("只有 5 种组件库", out)
        self.assertNotIn("button.cfg", out)                                    # and its hand-written button is not reported
        self.assertEqual(audit(kit_page(kit_roots(6), shell=shell), "--library", "luz-kit")[1].strip(), "audit: ok")
        in_product = kit_page(kit_roots(6) + "<button class='mine' type='button'>产品区里的</button>", shell=shell)
        code, out = audit(in_product, "--library", "luz-kit")
        self.assertEqual(code, 1)
        self.assertIn("button.mine", out)
        self.assertNotIn("button.cfg", out)

    def test_other_libraries_are_still_read_by_prefix(self):
        code, out = audit(LIBRARY_PAGE, "--library", "element-plus")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)


# Focused fields use a new fill or a short internal marker.
FIELD_CSS = "body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}input,textarea,select,button{font:inherit;min-height:32px}"
QUIET = "input,textarea,select{outline:0;border:1px solid #9aa0a6;background:#f3f4f5}input:focus,textarea:focus,select:focus{background-color:#e3e5e7}"
FIELDS = "<input aria-label='姓名'><textarea aria-label='备注'></textarea><select aria-label='状态'><option>甲</option></select>"


def field_page(css: str, body: str = FIELDS) -> str:
    return HEAD + f"<style>{FIELD_CSS}{css}</style>" + body


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class FocusFrameTests(unittest.TestCase):
    def found(self, css: str, body: str = FIELDS, *args: str) -> str:
        code, out = audit(field_page(css, body), *args)
        self.assertEqual(code, 1, out)
        self.assertIn("聚焦框", out)
        return out

    def test_a_field_that_changes_fill_and_adds_a_marker_passes(self):
        body = FIELDS + "<div contenteditable='true' aria-label='正文' style='min-height:32px'>可编辑</div><div role='textbox' tabindex='0' aria-label='标题' style='min-height:32px'>标题</div>"
        code, out = audit(field_page(QUIET + "[contenteditable],[role=textbox]{outline:0;border:0;background:#f3f4f5}[contenteditable]:focus,[role=textbox]:focus{background:#e3e5e7 linear-gradient(#242c36,#242c36) 8px bottom/16px 2px no-repeat}", body))
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_a_one_pixel_neutral_ring_in_a_box_shadow_is_reported(self):
        css = "input{outline:0;border:0;box-shadow:0 0 0 1px #9aa0a6}input:focus{box-shadow:0 0 0 1px #3f4a5a}"
        self.assertIn("聚焦阴影", self.found(css, "<input aria-label='姓名'>"))

    def test_a_neutral_bottom_border_that_darkens_on_focus_is_reported(self):
        css = "input{outline:0;border:0;border-bottom:1px solid #9aa0a6}input:focus{border-bottom-color:#3f4a5a}"
        self.assertIn("聚焦边框", self.found(css, "<input aria-label='姓名'>"))

    def test_a_blue_or_primary_outline_is_reported(self):
        out = self.found(QUIET + "input:focus{outline:2px solid #2563eb}")
        self.assertIn("彩色轮廓", out)
        self.assertIn("input", out)

    def test_a_primary_glow_around_the_field_is_reported(self):
        out = self.found(QUIET + "input:focus{box-shadow:0 0 0 3px rgba(37,99,235,.25)}")
        self.assertIn("彩色框或光晕", out)

    def test_an_inset_blue_frame_is_reported_too(self):
        out = self.found("input{outline:0;border:0;box-shadow:0 0 0 1px #9aa0a6 inset}input:focus{box-shadow:0 0 0 1px #2563eb inset}", "<input aria-label='姓名'>")
        self.assertIn("彩色框或光晕", out)

    def test_the_browser_default_outline_is_reported(self):
        out = self.found("", "<input aria-label='姓名'>")                           # no outline reset: the browser draws its own ring
        self.assertIn("浏览器默认轮廓", out)

    def test_a_thick_neutral_ring_or_a_thicker_border_is_reported(self):
        self.assertIn("变粗的框或光晕", self.found(QUIET + "input:focus{box-shadow:0 0 0 3px #555}", "<input aria-label='姓名'>"))
        self.assertIn("边框变粗", self.found(QUIET + "input:focus{border-width:2px}", "<input aria-label='姓名'>"))
        self.assertIn("粗轮廓或外扩轮廓", self.found(QUIET + "input:focus{outline:2px solid #1d2129;outline-offset:2px}", "<input aria-label='姓名'>"))

    def test_a_border_that_turns_blue_is_reported(self):
        self.assertIn("边框变彩色", self.found(QUIET + "input:focus{border-color:#2563eb}", "<input aria-label='姓名'>"))

    def test_the_frame_drawn_by_a_wrapper_is_found_like_the_one_element_plus_draws(self):
        wrap = ".w{display:inline-flex;align-items:center;min-height:32px;padding:0 8px;border-radius:4px;box-shadow:0 0 0 1px #d0d5dd inset}.w input{outline:0;border:0}"
        body = "<div class='w'><input aria-label='姓名'></div>"
        out = self.found(wrap + ".w:focus-within{box-shadow:0 0 0 1px #2563eb inset}", body)
        self.assertIn("外层 div.w", out)
        quiet = wrap + ".w{box-shadow:none;background:#f3f4f5}.w:focus-within{background-color:#e3e5e7}"
        self.assertEqual(audit(field_page(quiet, body))[1].strip(), "audit: ok")

    def test_a_class_added_by_a_script_and_a_slow_transition_do_not_hide_the_frame(self):
        body = "<input id='f' aria-label='姓名'><script>f.addEventListener('focus',()=>Promise.resolve().then(()=>f.classList.add('on')))</script>"
        self.found(QUIET + "input{transition:box-shadow 2s,border-color 2s}.on{box-shadow:0 0 0 3px rgba(37,99,235,.3)}", body)

    def test_select_textarea_contenteditable_and_text_roles_are_all_focused(self):
        body = ("<textarea aria-label='备注'></textarea><select aria-label='状态'><option>甲</option></select>"
                "<div contenteditable='true' aria-label='正文' style='min-height:32px'>可编辑</div><div role='combobox' tabindex='0' aria-label='城市' style='min-height:32px'>城市</div>"
                "<input type='search' aria-label='搜索'><input type='tel' aria-label='电话'><input type='date' aria-label='日期'>")
        out = self.found("*:focus{outline:2px solid #2563eb}", body)
        for name in ("textarea", "select", "div", "input[search]", "input[tel]", "input[date]"):
            self.assertIn(name + "：", out)

    def test_buttons_links_checkboxes_hidden_and_disabled_fields_are_not_probed(self):
        body = ("<button>确定</button><a href='#x'>链接</a><input type='checkbox' aria-label='同意'><input type='radio' aria-label='选项'><input type='hidden'>"
                "<input disabled aria-label='停用'><input style='display:none' aria-label='隐藏'>")
        code, out = audit(field_page("a{display:inline-block;min-height:32px}*:focus,*:focus-visible{outline:2px solid #2563eb}", body))
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_the_probe_can_be_switched_off(self):
        code, out = audit(field_page("", "<input aria-label='姓名'>"), "--no-focus-check")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)


if __name__ == "__main__":
    unittest.main()
