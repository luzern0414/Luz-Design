"""花店示例（examples/florist-mini）的流程测试：用 mini 模板 + 规格 + 内容模块生成后，在真实浏览器里把 016 花店的业务流程点通。

流程来自 016 的流程脚本：浏览 → 下单 → 支付成功（完成回到发起处）、购物车结算、取消订单、申请售后、支付失败后重新支付，
外加 30 个页面与弹层逐个打开。需要 Playwright 与 Microsoft Edge，没有就跳过（unittest.skip 里写明原因）。
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_prototype as bp  # noqa: E402

SPEC = HERE.parent / "references" / "prototype-templates" / "examples" / "florist-mini" / "spec.json"
OID = {"pay": "HJ2026110400128", "make": "HJ2026110400097", "ship": "HJ2026110300215", "done": "HJ2026110200643", "refund": "HJ2026102600052"}
ENGINE_CLASSES = {"danger"}  # 引擎确认框按钮的类名（.pt-confirm-row button.danger）
SHARED = {"btn", "btn-p", "btn-s", "btn-sm", "price", "strike", "tg", "tg-hot", "tg-soft", "tg-red", "tile", "tile-sq", "tile-ci", "tile-no", "ico", "ico-line", "av"}


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


class BuildTest(unittest.TestCase):
    def test_spec_passes_the_generator_checks(self) -> None:
        self.assertEqual(bp.build(SPEC, Path(tempfile.gettempdir()) / "florist-check.html", check_only=True), 0)

    def test_florist_words_stay_in_the_example_directory(self) -> None:
        """花店专属的东西只在示例目录里：通用模板、引擎、schema 里没有。"""
        root = HERE.parent / "references" / "prototype-templates"
        words = ("花店", "花间集", "玫瑰", "芍药", "鲜花")
        for d in ("engine", "mini", "schema"):
            for f in (root / d).rglob("*"):
                if f.is_file() and f.suffix in {".js", ".css", ".html", ".json", ".py"}:
                    text = f.read_text(encoding="utf-8")
                    self.assertFalse([w for w in words if w in text], f"{f} 里有行业词")

    def test_no_private_strings_in_the_example(self) -> None:
        for f in SPEC.parent.rglob("*"):
            if f.is_file() and f.suffix in {".js", ".css", ".json", ".md"}:
                text = f.read_text(encoding="utf-8")
                for bad in ("Chil" + "th", "skill" + "输出", "@gm" + "ail", "D:" + chr(92) + "Codes"):
                    self.assertNotIn(bad, text, f"{f.name} 里有 {bad}")


@unittest.skipUnless(browser_available(), "需要 playwright 与 Microsoft Edge；没有浏览器时跳过花店流程测试")
class FlowTest(unittest.TestCase):
    pw = browser = tmp = None
    html: Path

    @classmethod
    def setUpClass(cls) -> None:
        from playwright.sync_api import sync_playwright

        cls.tmp = tempfile.TemporaryDirectory()
        cls.html = Path(cls.tmp.name) / "florist.html"
        assert bp.build(SPEC, cls.html) == 0
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="msedge")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.pw.stop()
        cls.tmp.cleanup()

    def open(self, width: int = 1500, height: int = 1000):
        ctx = self.browser.new_context(viewport={"width": width, "height": height})
        page = ctx.new_page()
        self.errors: list[str] = []
        page.on("console", lambda m: self.errors.append(m.text[:300]) if m.type == "error" else None)
        page.on("pageerror", lambda e: self.errors.append(str(e)[:300]))
        page.goto(self.html.as_uri())
        page.wait_for_selector("#ptScreen .pt-page")
        return page

    def st(self, page) -> dict:
        return page.evaluate("""(() => { const K = __PT__, c = K.cur(); return { tab: K.S.tab, id: c.id, a: c.a, depth: c.depth, sheet: K.S.sheet && K.S.sheet.id,
            tabbar: !!document.querySelector('#ptScreen .pt-tabbar'), cart: K.data.cartCount, dialog: (d => d.open && !d.classList.contains('closing'))(document.getElementById('ptDlg')) } })()""")

    def click(self, page, sel: str, nth: int = 0) -> None:
        page.locator(sel).nth(nth).click()
        page.wait_for_timeout(110)

    def order_status(self, page, oid: str) -> str:
        return page.evaluate("(id) => __PT__.data.S.orders.find((o) => o.id === id).st", oid)

    # ------------------------------------------------------------------ 流程
    def test_a_browse_buy_pay_and_done_returns_to_the_starting_page(self) -> None:
        page = self.open()
        self.click(page, "#ptScreen .fl-entry button")
        s = self.st(page)
        self.assertEqual((s["id"], s["tabbar"]), ("list", False), "A1 宫格进商品列表，标签栏隐藏")
        self.click(page, "#ptScreen .fl-pcard")
        s = self.st(page)
        self.assertEqual((s["id"], s["depth"]), ("detail", 2), "A2 进详情，栈深 2")
        self.click(page, "#ptScreen .fl-dbar .fl-split .fl-b")
        self.assertEqual(self.st(page)["sheet"], "sheet-spec", "A3 立即购买先开规格弹层")
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').getAttribute('role') === 'dialog'"), "弹层带 role=dialog")
        self.click(page, "#ptDlg .fl-chips2 button", 1)
        self.click(page, "#ptDlg .pt-sfoot .btn")
        s = self.st(page)
        self.assertEqual((s["id"], s["depth"], s["dialog"]), ("checkout", 3, False), "A4 规格确认后进确认订单，弹层关闭")
        self.assertIn("228", page.locator("#ptScreen .fl-fbar .fl-tot .price b").inner_text(), "A4 选了 19 枝（258）后自动用满减券 30，应付 228")
        self.click(page, "#ptScreen .fl-cells .fl-cell", 0)
        self.assertEqual(self.st(page)["sheet"], "sheet-time", "A5 送达时间弹层")
        self.click(page, "#ptDlg .fl-slots button:not([disabled])", 1)
        self.click(page, "#ptDlg .pt-sfoot .btn")
        self.click(page, "#ptScreen .fl-cells >> nth=1 >> .fl-cell >> nth=0")
        self.assertEqual(self.st(page)["sheet"], "sheet-coupon", "A6 优惠券弹层")
        self.click(page, "#ptDlg .fl-tick.fl-small", 1)
        self.click(page, "#ptDlg .pt-sfoot .btn")
        self.click(page, "#ptScreen .fl-fbar .btn-p")
        self.assertEqual(self.st(page)["sheet"], "sheet-pay", "A7 提交订单开收银台")
        self.click(page, "#ptDlg .pt-sfoot .btn")
        s = self.st(page)
        self.assertEqual((s["id"], s["depth"]), ("result", 3), "A8 支付成功进结果页（替换确认订单这一步）")
        self.assertFalse(page.locator("#ptScreen .pt-nav .rb").is_visible(), "结果页没有返回键")
        self.assertIn("支付结果", page.locator("#ptRight .pt-title").inner_text(), "右栏逻辑面板显示结果页")
        self.click(page, "#ptScreen .fl-fbar .btn-s")
        s = self.st(page)
        self.assertEqual((s["id"], s["depth"]), ("detail", 2), "A9 完成回到发起结算的详情页")
        self.click(page, "#ptScreen .pt-nav .rb")
        self.click(page, "#ptScreen .pt-nav .rb")
        s = self.st(page)
        self.assertEqual((s["id"], s["tabbar"], s["depth"]), ("home", True, 0), "A10 连续返回回到首页，标签栏出现")
        self.assertEqual(self.errors, [])

    def test_b_cart_checkout_done_does_not_switch_the_tab(self) -> None:
        page = self.open()
        self.click(page, "#ptScreen .pt-tabbar button[data-pt-tab=cart]")
        self.assertEqual(self.st(page)["id"], "cart")
        page.locator("#ptScreen .pt-foot .fl-sbar .btn-p").click()
        page.wait_for_timeout(120)
        s = self.st(page)
        self.assertEqual((s["id"], s["tab"]), ("checkout", "cart"), "B1 购物车去结算")
        self.click(page, "#ptScreen .fl-fbar .btn-p")
        self.click(page, "#ptDlg .pt-sfoot .btn")
        self.assertEqual(self.st(page)["id"], "result", "B2 支付成功")
        self.click(page, "#ptScreen .fl-fbar .btn-s")
        s = self.st(page)
        self.assertEqual((s["id"], s["tabbar"], s["depth"]), ("cart", True, 0), "B3 完成回到购物车（不切标签）")
        self.assertEqual(page.locator("#ptScreen .fl-crow").count(), 2, "已结算的两件从购物车移除，只剩没勾选的（含失效的为 1 件另组）")
        self.assertEqual(self.errors, [])

    def test_c_cancel_an_order_needs_a_second_confirmation(self) -> None:
        page = self.open()
        self.click(page, "#ptScreen .pt-tabbar button[data-pt-tab=me]")
        self.click(page, "#ptScreen .fl-ord .fl-more")
        s = self.st(page)
        self.assertEqual((s["id"], s["depth"]), ("orders", 1), "C1 我的 → 全部订单")
        self.click(page, "#ptScreen .fl-utabs button", 1)
        n = page.locator("#ptScreen .fl-ocard").count()
        self.assertGreaterEqual(n, 1, "C2 待付款有订单")
        self.assertIn("pay", page.evaluate("location.hash"), "标签选择写进地址栏 hash")
        self.click(page, "#ptScreen .fl-ocard .fl-oact .btn-s")
        self.assertEqual(self.st(page)["sheet"], "sheet-cancel", "C3 取消先二次确认")
        self.assertTrue(page.locator("#ptDlg .pt-sheet.center").count() == 1, "确认框是居中面板")
        self.click(page, "#ptDlg .pt-confirm-row .danger")
        self.assertEqual(page.locator("#ptScreen .fl-ocard").count(), n - 1, "C4 取消后待付款少一单")
        self.assertEqual(self.order_status(page, OID["pay"]), "cancel", "订单状态机：待付款 → 已取消")
        self.assertEqual(self.errors, [])

    def test_d_after_sale_returns_to_the_orders_and_the_order_becomes_refund(self) -> None:
        page = self.open()
        self.click(page, "#ptScreen .pt-tabbar button[data-pt-tab=me]")
        self.click(page, "#ptScreen .fl-ord .fl-more")
        self.click(page, "#ptScreen .fl-utabs button", 4)
        self.click(page, "#ptScreen .fl-ocard .fl-oact .btn-s")
        self.assertEqual(self.st(page)["id"], "service", "D1 待评价 → 申请售后")
        self.click(page, "#ptScreen .mpord014 .dd [data-tg]")
        self.click(page, "#ptScreen .mpord014 .dd .menu [data-o]", 0)
        self.click(page, "#ptScreen .mpord014 [data-submit]")
        page.wait_for_function("__PT__.cur().id === 'orders'", timeout=4000)
        self.assertEqual(self.order_status(page, OID["done"]), "refund", "D2 提交后订单变退款中，回到订单列表")
        self.click(page, "#ptScreen .fl-utabs button", 5)
        self.assertGreaterEqual(page.locator("#ptScreen .fl-ocard").count(), 2, "D3 售后标签下出现退款中订单")
        self.assertEqual(self.errors, [])

    def test_f_payment_failure_then_repay_returns_to_the_starting_page(self) -> None:
        page = self.open()
        self.click(page, "#ptScreen .pt-tabbar button[data-pt-tab=cart]")
        page.locator("#ptScreen .pt-foot .fl-sbar .btn-p").click()
        page.wait_for_timeout(120)
        self.click(page, "[data-lt=scene]")
        self.click(page, '[data-scn="pay:fail-balance"]')
        self.click(page, "#ptScreen .fl-fbar .btn-p")
        self.click(page, "#ptDlg .pt-sfoot .btn")
        s = self.st(page)
        self.assertEqual(s["id"], "result-fail", "F1 支付失败页")
        self.assertEqual(page.locator("#ptScreen .fl-ring.fl-bad").count(), 1)
        self.assertIn("余额不足", page.locator("#ptScreen .fl-why").inner_text(), "失败原因随场景变化")
        self.assertEqual(self.order_status(page, page.evaluate("__PT__.data.S.co.oid")), "pay", "失败后订单仍是待付款")
        self.click(page, "#ptScreen .fl-fbar .btn-p")
        self.assertEqual(self.st(page)["sheet"], "sheet-pay", "F2 失败页可重新支付")
        page.evaluate("__PT__.setScene('pay', 'ok')")
        self.click(page, "#ptDlg .pt-sfoot .btn")
        self.assertEqual(self.st(page)["id"], "result", "F3 改成成功后重新支付成功")
        self.click(page, "#ptScreen .fl-fbar .btn-s")
        s = self.st(page)
        self.assertEqual((s["id"], s["depth"], s["tab"]), ("cart", 0, "cart"), "F4 完成回到发起结算的购物车")
        self.assertEqual(self.errors, [])

    def test_g_processing_scene_shows_the_waiting_page(self) -> None:
        page = self.open()
        page.evaluate("__PT__.setScene('pay', 'processing'); __PT__.jump('sheet-pay', '%s')" % OID["pay"])
        page.wait_for_timeout(200)
        self.click(page, "#ptDlg .pt-sfoot .btn")
        self.assertIn("确认中", page.locator("#ptScreen .fl-res h2").inner_text(), "处理中：支付结果确认中")
        self.assertEqual(self.errors, [])

    # ------------------------------------------------------------------ 页面、逻辑面板、类名
    def test_all_thirty_pages_and_sheets_open_without_console_errors(self) -> None:
        page = self.open()
        ids = page.evaluate("Object.keys(__PT__.pages)")
        self.assertEqual(len(ids), 30)
        for pid in ids:
            page.evaluate("(id) => __PT__.jump(id)", pid)
            page.wait_for_timeout(60)
            s = self.st(page)
            self.assertEqual(s["sheet"] or s["id"], pid, f"{pid} 打开")
            name = page.evaluate("(id) => __PT__.pages[id].name", pid)
            self.assertEqual(page.locator("#ptRight .pt-title").inner_text().split("\n")[0].strip(), name, f"{pid} 右栏逻辑面板跟着换页")
        self.assertEqual(self.errors, [])

    def test_custom_markup_uses_only_prefixed_or_shared_classes(self) -> None:
        page = self.open()
        bad: dict[str, set] = {}
        for pid in page.evaluate("Object.keys(__PT__.pages)"):
            page.evaluate("(id) => __PT__.jump(id)", pid)
            page.wait_for_timeout(40)
            tokens = page.evaluate("""() => [...document.querySelectorAll('#ptScreen .pt-custom *, #ptDlg .pt-custom *')]
                .filter((e) => !e.closest('.pt-blk, .ixr')).flatMap((e) => (typeof e.className === 'string' ? e.className : e.className.baseVal || '').split(/\\s+/)).filter(Boolean)""")
            for t in set(tokens):
                if not (t.startswith(("fl-", "pt-", "ics-")) or t in SHARED or t in ENGINE_CLASSES):
                    bad.setdefault(pid, set()).add(t)
        self.assertEqual(bad, {}, "内容模块里有没带前缀的类名，会和组件库冲突")

    def test_every_control_sits_inside_a_numbered_component_or_the_shell(self) -> None:
        """审计口径：#ptScreen 与弹层里的每个 button / input / [role=button] 都要有带 data-cid 的祖先（库组件编号）或 data-shell。"""
        page = self.open()
        orphans: dict[str, list[str]] = {}
        for pid in page.evaluate("Object.keys(__PT__.pages)"):
            page.evaluate("(id) => __PT__.jump(id)", pid)
            page.wait_for_timeout(50)
            found = page.evaluate("""() => [...document.querySelectorAll('#ptScreen button, #ptScreen input, #ptScreen textarea, #ptScreen [role=button], #ptDlg button, #ptDlg input')]
                .filter((e) => !e.closest('[data-cid], [data-shell]')).map((e) => e.tagName.toLowerCase() + '.' + String(e.className).slice(0, 40))""")
            if found:
                orphans[pid] = found[:4]
        self.assertEqual(orphans, {}, "这些控件不在带 data-cid 的组件里")

    def test_library_components_are_used_with_data_cid(self) -> None:
        page = self.open()
        cids: set[str] = set()
        for pid in ("search", "reviews", "cart", "service", "review", "addredit"):
            page.evaluate("(id) => __PT__.jump(id)", pid)
            page.wait_for_timeout(60)
            cids |= set(page.evaluate("[...document.querySelectorAll('#ptScreen .ixr[data-cid]')].map((e) => e.dataset.cid)"))
        self.assertGreaterEqual(len(cids), 6, f"至少用 6 种库组件，现在 {sorted(cids)}")

    def test_config_changes_apply_to_the_custom_pages(self) -> None:
        page = self.open()
        self.click(page, "[data-lt=look]")
        self.click(page, "[data-g=theme][data-v=teal]")
        self.assertEqual(page.evaluate("getComputedStyle(document.getElementById('root')).getPropertyValue('--p').trim()").lower(), "#457d81")
        self.click(page, "[data-g=header][data-v=light]")
        self.assertEqual(page.locator("#ptScreen .pt-hbg").get_attribute("data-bg"), "light")
        self.click(page, "[data-g=header][data-v=image]")
        self.assertIn("url(", page.locator("#ptScreen .pt-hbg").get_attribute("style"))
        before = page.locator("#ptScreen .fl-entry .ico").first.get_attribute("src")
        self.click(page, "[data-g=iconStyle][data-v=flat]")
        self.assertEqual(page.evaluate("document.getElementById('ptScreen').classList.contains('ics-flat')"), True)
        self.assertNotEqual(page.locator("#ptScreen .fl-entry .ico").first.get_attribute("src"), before, "入口图标换成扁平的那一张")
        self.click(page, "[data-g=iconStyle][data-v=line]")
        self.assertGreaterEqual(page.locator("#ptScreen .fl-entry .ico-line").count(), 5, "线性风格用线性图标（含花店专属的 6 个）")
        self.click(page, "[data-g=iconTile][data-v=ci]")
        self.assertEqual(page.evaluate("getComputedStyle(document.querySelector('#ptScreen .fl-entry .tile')).borderRadius"), "50%")
        self.assertEqual(self.errors, [])

    def test_phone_width_390_works_without_horizontal_overflow(self) -> None:
        page = self.open(390, 844)
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        self.click(page, "#ptScreen .fl-pcard")
        self.assertEqual(self.st(page)["id"], "detail")
        self.click(page, "#ptScreen .fl-dbar .fl-split .fl-a")
        self.assertEqual(self.st(page)["sheet"], "sheet-spec")
        self.click(page, "#ptDlg .pt-sfoot .btn")
        self.assertGreater(page.evaluate("__PT__.data.cartCount"), 4, "加入购物车后角标数变大")
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        self.assertEqual(self.errors, [])

    def test_reset_demo_data_restores_the_cart_and_orders(self) -> None:
        page = self.open()
        page.evaluate("__PT__.act('cartDel', 0); __PT__.act('cancelOk', '%s')" % OID["pay"])
        self.assertEqual(self.order_status(page, OID["pay"]), "cancel")
        self.click(page, "[data-lt=scene]")
        self.click(page, "[data-reset]")
        self.assertEqual(self.order_status(page, OID["pay"]), "pay", "重置后订单状态还原")
        self.assertEqual(page.evaluate("__PT__.data.cartCount"), 4)
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
