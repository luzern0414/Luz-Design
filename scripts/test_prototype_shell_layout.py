"""原型外壳的三栏排布与设备框：嵌在设计文档的 iframe（约 1050 宽）里、笔记本窗口（1200、1440）和宽屏（1920）都要把舞台留够。

回归的现象（014 项目设计阶段审计 C 的 A-04）：窗口小于约 1200 时，两侧面板各取最大宽度，舞台只剩 306 像素，手机框按高度缩放后仍有 377 像素，
向左右超出舞台、压在面板上；后台舞台被挤到 400 像素，退成窄屏布局，侧栏只剩汉堡按钮。修法：kind 声明 stageMin，引擎放不下“舞台 + 两栏”时
把右栏、再把左栏改成抽屉（浮在舞台上，默认收起），舞台保持设备框应有的宽度。另外：device.capsule 只对小程序有意义，手机浏览器网页写 false。

没有 Playwright 或 Microsoft Edge 时整组跳过并写明，不当作通过。运行：py -X utf8 -m unittest test_prototype_shell_layout -v
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_prototype as bp  # noqa: E402

TEMPLATES = HERE.parent / "references" / "prototype-templates"
MINI = TEMPLATES / "examples" / "generic-mini" / "spec.json"
ADMIN = TEMPLATES / "examples" / "generic-admin" / "spec.json"


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


class StaticTest(unittest.TestCase):
    def test_kinds_declare_the_stage_width_they_need(self) -> None:
        mini = (TEMPLATES / "mini" / "mini.js").read_text(encoding="utf-8")
        admin = (TEMPLATES / "admin" / "js" / "90-register.js").read_text(encoding="utf-8")
        self.assertIn("stageMin: () => device().width + 16", mini)
        self.assertRegex(admin, r"stageMin: \(\) => 96\d")

    def test_engine_documents_stage_min_docking_and_the_capsule_scope(self) -> None:
        engine = (TEMPLATES / "engine" / "ENGINE.md").read_text(encoding="utf-8")
        self.assertIn("stageMin", engine)
        self.assertIn("抽屉", engine)
        # capsule 只属于微信小程序：手机浏览器网页要写 false
        self.assertRegex(engine, r"capsule[^\n]*(仅|只)[^\n]*小程序")
        self.assertIn("手机浏览器", engine)
        ref = (HERE.parent / "references" / "prototype-reference.html").read_text(encoding="utf-8")
        self.assertIn("capsule", ref)
        self.assertIn("手机浏览器网页", ref)
        self.assertIn("不保存外观选择", ref)
        self.assertIn("localStorage", ref)
        schema = json.loads((TEMPLATES / "schema" / "prototype.schema.json").read_text(encoding="utf-8"))
        defs = schema.get("$defs") or schema.get("definitions") or {}
        cap = defs["device"]["properties"]["capsule"]
        self.assertIn("小程序", cap.get("description", ""))

    def test_shell_template_sets_the_dark_scheme_before_first_paint(self) -> None:
        tpl = (TEMPLATES / "engine" / "shell.template.html").read_text(encoding="utf-8")
        head = tpl.split("</head>")[0]
        self.assertIn("prefers-color-scheme: dark", head, "head 里要有同步脚本，首帧就是深色，不先闪一帧浅色底")
        self.assertLess(head.index("prefers-color-scheme"), head.index("<style>"))

    def test_fold_rules_do_not_apply_to_the_stacked_narrow_layout(self) -> None:
        css = (TEMPLATES / "engine" / "engine.css").read_text(encoding="utf-8")
        head, _, tail = css.partition("@media (min-width: 911px)")
        self.assertTrue(tail, "docking rules live in the wide-window media query")
        self.assertNotIn("data-out-left", head, "折叠与抽屉的规则只在宽窗口生效，窄屏上下排时不能把面板藏掉")


@unittest.skipUnless(browser_available(), "需要 playwright 和 Microsoft Edge；没有浏览器时这一组跳过")
class ShellLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from playwright.sync_api import sync_playwright

        cls.tmp = tempfile.TemporaryDirectory()
        cls.url: dict[str, str] = {}
        specs = {"mini": MINI, "admin": ADMIN}
        for name, path in specs.items():
            out = Path(cls.tmp.name) / f"{name}.html"
            assert bp.build(path, out) == 0, name
            cls.url[name] = out.as_uri()
        nocap = json.loads(MINI.read_text(encoding="utf-8"))
        nocap["device"] = {"capsule": False}
        nocap_path = Path(cls.tmp.name) / "nocap.json"
        nocap_path.write_text(json.dumps(nocap, ensure_ascii=False), encoding="utf-8")
        out = Path(cls.tmp.name) / "nocap.html"
        assert bp.build(nocap_path, out) == 0
        cls.url["nocap"] = out.as_uri()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="msedge")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.pw.stop()
        cls.tmp.cleanup()

    def open(self, name: str, width: int, height: int = 900):
        ctx = self.browser.new_context(viewport={"width": width, "height": height}, locale="zh-CN")
        self.addCleanup(ctx.close)
        page = ctx.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        page.goto(self.url[name])
        page.wait_for_function("window.__PT__ && __PT__.cur && __PT__.cur().id")
        page.wait_for_timeout(200)
        page.errors = errors
        return page

    @staticmethod
    def box(page, selector: str):
        return page.evaluate(
            """(s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect();
                 return {left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height, display: getComputedStyle(e).display} }""",
            selector,
        )

    @staticmethod
    def overlap(a, b) -> bool:
        return a["left"] < b["right"] - 0.5 and b["left"] < a["right"] - 0.5

    # ---------------- 手机框
    def test_phone_frame_stays_inside_its_stage_and_clear_of_the_panels_at_1050_and_1440(self) -> None:
        for width in (1050, 1200, 1440, 1920):
            with self.subTest(width=width):
                page = self.open("mini", width, 900)
                stage, phone = self.box(page, "#ptStage"), self.box(page, "#ptPhone")
                self.assertGreaterEqual(stage["width"], 406 - 1, "舞台至少一个设备框宽加边距")
                self.assertGreaterEqual(phone["width"], 389, "设备框保持 390（高度够时不缩）")
                self.assertGreaterEqual(phone["left"], stage["left"] - 0.5)
                self.assertLessEqual(phone["right"], stage["right"] + 0.5)
                for panel in ("#ptLeft", "#ptRight"):
                    pb = self.box(page, panel)
                    if pb and pb["display"] != "none":
                        self.assertFalse(self.overlap(phone, pb), f"手机框压到了 {panel}")
                self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), width, "没有横向滚动")
                self.assertEqual(page.errors, [])

    def test_phone_page_shows_both_panels_side_by_side_at_1050_and_1440(self) -> None:
        for width in (1050, 1440):
            with self.subTest(width=width):
                page = self.open("mini", width, 900)
                self.assertEqual(page.evaluate("[document.documentElement.dataset.dockLeft, document.documentElement.dataset.dockRight]"), ["inline", "inline"])
                left, stage, right = (self.box(page, s) for s in ("#ptLeft", "#ptStage", "#ptRight"))
                self.assertLess(left["right"], stage["left"] + 1)
                self.assertLess(stage["right"], right["left"] + 1)
                self.assertGreaterEqual(left["width"], 240)
                self.assertGreaterEqual(right["width"], 260)

    def test_small_laptop_window_turns_the_logic_panel_into_a_drawer_and_keeps_the_phone_whole(self) -> None:
        page = self.open("mini", 960, 900)  # 240 + 260 + 406 + 64 = 970 > 960：两栏并排放不下，右栏改抽屉，左栏仍并排
        h = page.evaluate("(({dockLeft, dockRight, foldLeft, foldRight}) => ({dockLeft, dockRight, foldLeft, foldRight}))(document.documentElement.dataset)")
        self.assertEqual((h["dockLeft"], h["dockRight"]), ("inline", "float"))
        self.assertEqual((h["foldLeft"], h["foldRight"]), ("0", "1"), "抽屉默认收起")
        stage, phone = self.box(page, "#ptStage"), self.box(page, "#ptPhone")
        self.assertGreaterEqual(stage["width"], 406 - 1)
        self.assertGreaterEqual(phone["width"], 389)
        self.assertFalse(self.overlap(phone, self.box(page, "#ptLeft")))
        page.click("[data-fold=right]")
        right = self.box(page, "#ptRight")
        self.assertNotEqual(right["display"], "none")
        self.assertEqual(page.evaluate("getComputedStyle(document.querySelector('#ptRight')).position"), "fixed", "抽屉浮在舞台上，不占列")
        self.assertAlmostEqual(self.box(page, "#ptStage")["width"], stage["width"], delta=1, msg="打开抽屉不改变舞台宽度")
        self.assertEqual(page.evaluate("document.activeElement && document.activeElement.id"), "ptRight", "打开后焦点进入抽屉")
        page.keyboard.press("Escape")
        self.assertEqual(self.box(page, "#ptRight")["display"], "none", "Esc 收起抽屉")
        self.assertEqual(page.evaluate("document.activeElement.dataset.fold"), "right", "焦点回到页头的按钮")
        self.assertEqual(page.errors, [])

    def test_page_header_stays_on_one_line_at_1050(self) -> None:
        for name in ("mini", "admin"):
            with self.subTest(name=name):
                page = self.open(name, 1050, 760)
                head = self.box(page, ".pt-top")
                self.assertLessEqual(head["height"], 64, "页头一行放下，标题与折叠按钮不折行")
                for sel in (".pt-top h1", ".pt-folds button[data-fold=left]", ".pt-folds button[data-fold=right]"):
                    self.assertLessEqual(self.box(page, sel)["height"], 40, f"{sel} 不折成多行")

    # ---------------- 后台
    def test_admin_keeps_the_desktop_layout_with_a_named_sidebar_at_1050_and_1440(self) -> None:
        for width, docks in ((1050, ("float", "float")), (1440, ("inline", "float")), (1920, ("inline", "inline"))):
            with self.subTest(width=width):
                page = self.open("admin", width, 900)
                got = page.evaluate("[document.documentElement.dataset.dockLeft, document.documentElement.dataset.dockRight]")
                self.assertEqual(tuple(got), docks)
                app = self.box(page, "#adApp")
                self.assertGreaterEqual(app["width"], 960, "舞台 ≥ 960 才是完整侧栏")
                self.assertEqual(page.evaluate("document.querySelector('#adApp').dataset.mode"), "wide")
                labels = page.evaluate("[...document.querySelectorAll('#adSide .ad-ni .lb')].filter(e => e.offsetParent && e.getBoundingClientRect().width > 0 && e.textContent.trim()).length")
                self.assertGreaterEqual(labels, 3, "侧栏带名称，不是只剩图标")
                side = self.box(page, "#adSide")
                self.assertGreaterEqual(side["width"], 200, "侧栏是完整宽度")
                self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), width)
                self.assertEqual(page.errors, [])

    def test_admin_logic_panel_opens_as_a_drawer_without_squeezing_the_stage(self) -> None:
        page = self.open("admin", 1440, 900)
        before = self.box(page, "#adApp")["width"]
        self.assertEqual(self.box(page, "#ptRight")["display"], "none")
        page.click("[data-fold=right]")
        self.assertEqual(page.locator("[data-fold=right]").get_attribute("aria-pressed"), "false")
        right = self.box(page, "#ptRight")
        self.assertEqual(right["display"], "block")
        self.assertGreater(right["width"], 300)
        self.assertAlmostEqual(self.box(page, "#adApp")["width"], before, delta=1)
        self.assertIn("来源", page.locator("#ptRight").inner_text(), "抽屉里是本页逻辑")
        self.assertEqual(page.evaluate("document.documentElement.dataset.floatOpen"), "1")
        # 点遮罩收起
        page.mouse.click(700, 500)
        self.assertEqual(page.evaluate("document.documentElement.dataset.floatOpen"), "0")
        self.assertEqual(self.box(page, "#ptRight")["display"], "none")
        self.assertEqual(page.errors, [])

    def test_resizing_re_docks_the_panels_and_resets_the_folds_of_the_sides_that_changed(self) -> None:
        page = self.open("admin", 1920, 900)
        d = lambda: page.evaluate("(() => { const h = document.documentElement.dataset; return [h.dockLeft, h.dockRight, h.foldLeft, h.foldRight] })()")
        self.assertEqual(d(), ["inline", "inline", "0", "0"])
        page.set_viewport_size({"width": 1050, "height": 900})
        page.wait_for_timeout(150)
        self.assertEqual(d(), ["float", "float", "1", "1"])
        self.assertEqual(page.evaluate("document.querySelector('#adApp').dataset.mode"), "wide")
        page.set_viewport_size({"width": 1920, "height": 900})
        page.wait_for_timeout(150)
        self.assertEqual(d(), ["inline", "inline", "0", "0"])
        # 窄屏上下排：折叠与抽屉的规则不生效，面板仍可见
        page.set_viewport_size({"width": 800, "height": 900})
        page.wait_for_timeout(150)
        self.assertNotEqual(self.box(page, "#ptLeft")["display"], "none")
        self.assertNotEqual(self.box(page, "#ptRight")["display"], "none")
        self.assertEqual(page.errors, [])

    def test_folded_panel_is_still_shown_when_the_window_gets_narrow(self) -> None:
        page = self.open("mini", 1440, 900)
        page.click("[data-fold=left]")
        self.assertEqual(self.box(page, "#ptLeft")["display"], "none")
        page.set_viewport_size({"width": 800, "height": 900})
        page.wait_for_timeout(150)
        self.assertNotEqual(self.box(page, "#ptLeft")["display"], "none", "窄屏上下排时不能因为之前折叠过就看不到面板")

    # ---------------- 胶囊
    def test_capsule_is_drawn_by_default_and_device_capsule_false_removes_it(self) -> None:
        page = self.open("mini", 1440, 900)
        self.assertEqual(page.locator("#ptPhone .pt-cap").count(), 1, "默认（小程序）画微信胶囊")
        page = self.open("nocap", 1440, 900)
        self.assertEqual(page.locator("#ptPhone .pt-cap").count(), 0, "手机浏览器网页写 device.capsule=false")
        self.assertEqual(page.errors, [])


if __name__ == "__main__":
    unittest.main()
