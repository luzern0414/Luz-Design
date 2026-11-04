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


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class AuditRenderedTests(unittest.TestCase):
    def test_a_clean_page_passes(self):
        code, out = audit(GOOD)
        self.assertEqual((code, out.strip()), (0, "audit: ok"))

    def test_small_italic_light_and_bold_text_are_found_on_the_rendered_page(self):
        bad = GOOD.replace("<p>正文</p>", "<p style='font-size:12px'>小字</p><p style='font-style:italic'>斜体</p><p style='color:#bbb'>浅色</p><p style='font-weight:700'>粗体</p><script>document.body.append(Object.assign(document.createElement('p'),{textContent:'脚本加的小字',style:'font-size:11px'}))</script>")
        code, out = audit(bad)
        self.assertEqual(code, 1)
        for needle in ("under 14px", "italic", "contrast", "weight outside", "脚本加的小字"):
            self.assertIn(needle, out)

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

    def test_a_page_that_only_loads_the_style_sheet_and_draws_its_own_widgets_fails(self):
        own = "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><style>body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}</style><div class='el-card'><p>正文</p></div>"
        code, out = audit(own, "--library", "element-plus")
        self.assertEqual(code, 1)
        self.assertIn("种组件库", out)

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

    def test_too_few_kinds_of_component_fail_and_the_same_id_twice_is_one_kind(self):
        code, out = audit(kit_page(kit_roots(3)), "--library", "luz-kit")
        self.assertEqual(code, 1)
        self.assertIn("只有 3 种组件库", out)
        code, out = audit(kit_page(kit_roots(8, same=True)), "--library", "luz-kit")
        self.assertEqual(code, 1)
        self.assertIn("只有 1 种组件库", out)
        self.assertEqual(audit(kit_page(kit_roots(3)), "--library", "luz-kit", "--min-components", "3")[1].strip(), "audit: ok")

    def test_the_prototype_shell_is_not_product_interface(self):
        shell = "<aside data-shell><button class='cfg' type='button'>主题色</button><div data-cid='MP-CARD-099'><button type='button'>配置里的</button></div></aside>"
        code, out = audit(kit_page(kit_roots(5), shell=shell), "--library", "luz-kit")
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


# Text fields: a focused field only deepens its 1px border to ink2 (visual-design.html 层级与立体感 › 边缘线条). Anything else that appears on focus is a 聚焦框.
FIELD_CSS = "body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}input,textarea,select,button{font:inherit;min-height:32px}"
QUIET = "input,textarea,select{outline:0;border:1px solid #9aa0a6}input:focus,textarea:focus,select:focus{border-color:#3f4a5a}"
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

    def test_a_field_that_only_deepens_its_border_passes(self):
        body = FIELDS + "<div contenteditable='true' aria-label='正文' style='min-height:32px'>可编辑</div><div role='textbox' tabindex='0' aria-label='标题' style='min-height:32px'>标题</div>"
        code, out = audit(field_page(QUIET + "[contenteditable],[role=textbox]{outline:0;border:1px solid #9aa0a6}[contenteditable]:focus,[role=textbox]:focus{border-color:#3f4a5a}", body))
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)

    def test_a_one_pixel_neutral_ring_in_a_box_shadow_also_passes(self):
        css = "input{outline:0;border:0;box-shadow:0 0 0 1px #9aa0a6}input:focus{box-shadow:0 0 0 1px #3f4a5a}"
        self.assertEqual(audit(field_page(css, "<input aria-label='姓名'>"))[1].strip(), "audit: ok")

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
        quiet = wrap + ".w:focus-within{box-shadow:0 0 0 1px #3f4a5a inset}"
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
