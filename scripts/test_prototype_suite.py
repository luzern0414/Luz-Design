"""多系统外壳（build_prototype_suite.py + shell/README.md + examples/suite-demo）的测试。

    py -X utf8 scripts/test_prototype_suite.py

分三部分：
1. 不要浏览器：生成（iframe 与 --inline 两种）、--check 只校验、坏输入逐类报中文错、规格构建失败时原样带出 build_prototype.py 的报错、
   Luz-Project 的原型校验（dev_documents._prototype_errors 与前端页签校验，没有 Luz-Project 就跳过）、隐私与行业字样。
2. check_document.py --allow interface：外壳自己零错误；内嵌版的错误只能来自内嵌的原型。
3. 要浏览器（Playwright + Microsoft Edge，没有就跳过并写明）：打开无控制台错误、页签名与数量、切页签才加载、重新载入与在新窗口打开、
   键盘左右键、#tab= 直达、每个页签一个原型框、原型能点、390 宽无横向撑破且页签条可横向滚动、打印全部展开、深浅外观、内嵌版同样可用。
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_prototype as bp  # noqa: E402
import build_prototype_suite as su  # noqa: E402

REPO = HERE.parent
TEMPLATES = REPO / "references" / "prototype-templates"
SUITE = TEMPLATES / "examples" / "suite-demo" / "suite.json"
SHELL_README = TEMPLATES / "shell" / "README.md"
PROJECT_SCRIPTS = REPO.parent / "Luz-Project" / "scripts"
PRIVATE = ["Chil" + "th", "skill" + chr(0x8f93) + chr(0x51fa), chr(0x82b1)]            # 隐私与行业字样；用拼接写，免得本文件自己带这些字
SYSTEM_NAMES = ["小程序", "管理后台"]


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


def run_main(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = su.main(argv)
    return code, buf.getvalue()


def load_suite() -> dict:
    return json.loads(SUITE.read_text(encoding="utf-8"))


def write_suite(dest: Path, suite: dict) -> Path:
    """把 suite 写到 dest，规格路径换成绝对路径（suite.json 里的相对路径是相对它自己的目录）。"""
    suite = copy.deepcopy(suite)
    for s in suite.get("systems", []):
        if isinstance(s, dict):
            for key in ("spec", "file"):
                if s.get(key) and not Path(s[key]).is_absolute():
                    s[key] = str((SUITE.parent / s[key]).resolve())
    dest.write_text(json.dumps(suite, ensure_ascii=False), encoding="utf-8")
    return dest


def tab_count(page_html: str) -> int:
    return len(re.findall(r'role="tab"', page_html))


# ------------------------------------------------------------------ 一、不要浏览器

class GenerateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="suite-test-"))
        cls.frame = cls.tmp / "iframe" / "suite.html"
        cls.single = cls.tmp / "inline" / "suite.html"
        cls.code_frame, cls.out_frame = run_main([str(SUITE), "--out", str(cls.frame), "--project-tabs", str(cls.tmp / "tabs.json")])
        cls.code_inline, cls.out_inline = run_main([str(SUITE), "--out", str(cls.single), "--inline"])

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_iframe_build_writes_the_document_and_one_prototype_per_system(self) -> None:
        self.assertEqual(self.code_frame, 0, self.out_frame)
        files = sorted(p.name for p in self.frame.parent.iterdir())
        self.assertEqual(files, ["01-小程序原型.html", "02-管理后台原型.html", "suite.html"])
        page = self.frame.read_text(encoding="utf-8")
        self.assertLess(len(page.encode()), 200_000, "iframe 版的文档只放外壳，原型在旁边的文件里")
        self.assertEqual(tab_count(page), 1 + len(SYSTEM_NAMES))
        self.assertEqual(page.count("data-src="), 2)
        self.assertNotIn("srcdoc", page.split("<script>")[0], "iframe 版不内嵌原型")
        for name in SYSTEM_NAMES:
            self.assertIn(f">{name}</button>", page)

    def test_inline_build_is_a_single_file_with_the_prototypes_embedded(self) -> None:
        self.assertEqual(self.code_inline, 0, self.out_inline)
        self.assertEqual([p.name for p in self.single.parent.iterdir()], ["suite.html"], "--inline 不写原型文件")
        page = self.single.read_text(encoding="utf-8")
        self.assertEqual(page.count("data-srcdoc="), 2)
        self.assertNotIn("data-src=", page)
        self.assertGreater(len(page.encode()), 2_000_000)
        self.assertIn("内嵌（单文件）", page)
        self.assertEqual(tab_count(page), 3)

    def test_the_shell_has_the_parts_of_the_luz_project_document(self) -> None:
        page = self.frame.read_text(encoding="utf-8")
        for part in ("重新载入", "在新窗口打开", "role=\"tablist\"", "role=\"tabpanel\"", "#tab=", "ArrowRight", "beforeprint", "@media print", "prefers-color-scheme:dark", "luz-md-type:start"):
            self.assertIn(part, page, part)
        self.assertEqual(page.count("<h1>"), 1)
        self.assertEqual(len(re.findall(r'class="proto ', page)), 2, "每个系统页签一个原型框")

    def test_check_only_validates_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code, out = run_main([str(SUITE), "--check", "--out", str(Path(tmp) / "x.html")])
            self.assertEqual(code, 0, out)
            self.assertIn("外壳校验通过", out)
            self.assertEqual(set(Path(tmp).iterdir()), before)

    def test_a_checks_tab_is_added_last_when_the_suite_has_one(self) -> None:
        suite = load_suite()
        suite["checks"] = {"sections": [{"title": "原型与真实系统的差异", "blocks": [{"type": "text", "text": "原型比真实系统少了接口，数据是演示数据。"}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = write_suite(Path(tmp) / "s.json", suite)
            code, out = run_main([str(path), "--out", str(Path(tmp) / "o" / "d.html")])
            self.assertEqual(code, 0, out)
            page = (Path(tmp) / "o" / "d.html").read_text(encoding="utf-8")
            self.assertEqual(tab_count(page), 4)
            self.assertLess(page.index(">管理后台</button>"), page.index(">检查与差异</button>"))

    def test_a_prebuilt_file_outside_the_output_folder_is_copied_next_to_the_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            code, out = run_main([str(SUITE), "--out", str(tmp_dir / "first" / "d.html")])
            self.assertEqual(code, 0, out)
            suite = load_suite()
            suite["systems"] = [{"name": "手机页", "surface": "h5", "file": str(tmp_dir / "first" / "01-小程序原型.html")}]
            path = write_suite(tmp_dir / "s.json", suite)
            code, out = run_main([str(path), "--out", str(tmp_dir / "second" / "d.html")])
            self.assertEqual(code, 0, out)
            self.assertTrue((tmp_dir / "second" / "01-小程序原型.html").is_file())
            self.assertIn("01-", unquote((tmp_dir / "second" / "d.html").read_text(encoding="utf-8")))


class BadInputTest(unittest.TestCase):
    """每一类坏输入各报一条中文错并退出 1，不写出文件。"""

    def assert_rejected(self, mutate, expect: str) -> str:
        suite = load_suite()
        mutate(suite)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_suite(Path(tmp) / "s.json", suite)
            out_html = Path(tmp) / "o" / "d.html"
            code, out = run_main([str(path), "--out", str(out_html)])
            self.assertEqual(code, 1, out)
            self.assertIn(expect, out)
            self.assertFalse(out_html.exists(), "校验没通过就不写文档")
            check_code, check_out = run_main([str(path), "--check"])
            self.assertEqual(check_code, 1, check_out)
            self.assertIn(expect, check_out)
        return out

    def test_duplicate_tab_names(self) -> None:
        self.assert_rejected(lambda s: s["systems"][1].update(name="小程序"), "页签重名")

    def test_a_system_cannot_take_the_name_of_the_architecture_tab(self) -> None:
        self.assert_rejected(lambda s: s["systems"][1].update(name="前端架构"), "被前端架构页签占用")

    def test_the_same_spec_in_two_tabs(self) -> None:
        self.assert_rejected(lambda s: s["systems"][1].update(spec=s["systems"][0]["spec"], surface="miniapp", kind="phone"), "用了同一个原型规格")

    def test_the_same_prebuilt_file_in_two_tabs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proto = Path(tmp) / "p.html"
            proto.write_text("<!doctype html><title>x</title>", encoding="utf-8")

            def mutate(s: dict) -> None:
                s["systems"] = [{"name": "手机页一", "surface": "h5", "file": str(proto)}, {"name": "手机页二", "surface": "h5", "file": str(proto)}]

            self.assert_rejected(mutate, "用了同一个原型文件")

    def test_kind_does_not_match_surface(self) -> None:
        out = self.assert_rejected(lambda s: s["systems"][0].update(kind="wide"), "不匹配")
        self.assertIn("小程序的原型只能是 phone", out)
        self.assert_rejected(lambda s: s["systems"][1].update(kind="phone"), "不匹配")

    def test_spec_template_and_kind_disagree(self) -> None:
        self.assert_rejected(lambda s: s["systems"][0].update(surface="admin", kind="wide"), "kind 不能写 wide")

    def test_a_system_without_a_prototype(self) -> None:
        self.assert_rejected(lambda s: s["systems"][1].pop("spec"), "没有原型")

    def test_spec_and_file_together(self) -> None:
        self.assert_rejected(lambda s: s["systems"][1].update(file="x.html"), "同时写了 spec 和 file")

    def test_missing_spec_file(self) -> None:
        self.assert_rejected(lambda s: s["systems"][1].update(spec="no/such/spec.json"), "原型规格不存在")

    def test_unknown_surface_library_and_fields(self) -> None:
        self.assert_rejected(lambda s: s["systems"][0].update(surface="tv"), "surface 要写")
        self.assert_rejected(lambda s: s["systems"][0].update(library="no-such-lib"), "不在组件库注册表")
        self.assert_rejected(lambda s: s["systems"][1].update(library="vant"), "换一个适合这一端的库")
        self.assert_rejected(lambda s: s["systems"][0].update(colour="red"), "多余的字段")
        self.assert_rejected(lambda s: s.update(note="x"), "多余的字段")

    def test_a_failing_spec_brings_out_the_build_prototype_report_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = json.loads((TEMPLATES / "examples" / "generic-mini" / "spec.json").read_text(encoding="utf-8"))
            spec["tabbar"][0]["page"] = "no-such-page"
            bad = Path(tmp) / "bad" / "spec.json"
            bad.parent.mkdir()
            bad.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(bp.build(bad, Path(tmp) / "x.html", None, True), 1)
            own = [line for line in buf.getvalue().splitlines() if line.startswith("错误：")]
            self.assertTrue(own, "build_prototype.py 自己要有报错")
            out = self.assert_rejected(lambda s: s["systems"][0].update(spec=str(bad)), "构建失败")
            for line in own:
                self.assertIn(line, out)

    def test_a_missing_template_is_an_error_not_a_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = json.loads((TEMPLATES / "examples" / "generic-mini" / "spec.json").read_text(encoding="utf-8"))
            spec["kind"] = "tablet"
            bad = Path(tmp) / "spec.json"
            bad.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            self.assert_rejected(lambda s: s["systems"][0].update(spec=str(bad)), "构建失败")

    def test_title_overview_and_architecture(self) -> None:
        self.assert_rejected(lambda s: s.pop("title"), "要写 title")
        self.assert_rejected(lambda s: s.pop("overview"), "要写 overview")
        self.assert_rejected(lambda s: s.update(overview="结论" * 80), "150 字以内")
        self.assert_rejected(lambda s: s.pop("architecture"), "architecture")
        self.assert_rejected(lambda s: s.update(systems=[]), "至少一个系统")

    def test_architecture_blocks(self) -> None:
        def block(s: dict) -> dict:
            return s["architecture"]["sections"][1]["blocks"][0]

        self.assert_rejected(lambda s: block(s).pop("caption"), "没有表题的表")
        self.assert_rejected(lambda s: block(s)["rows"][0].__setitem__(1, ""), "空单元格")
        self.assert_rejected(lambda s: block(s)["rows"][0].pop(), "列数与表头不符")
        self.assert_rejected(lambda s: s["architecture"]["sections"][0]["blocks"][0].update(rows=s["architecture"]["sections"][0]["blocks"][0]["rows"][:1]), "至少两层")
        self.assert_rejected(lambda s: s["architecture"]["sections"][0]["blocks"][0].pop("caption"), "没有图题的分层图")
        self.assert_rejected(lambda s: s["architecture"]["sections"][2]["blocks"].append({"type": "figure", "kind": "sequence", "caption": "x"}), "只支持分层图")
        self.assert_rejected(lambda s: s["architecture"]["sections"][2]["blocks"].append({"type": "image", "file": "x.png"}), "块类型无效")
        self.assert_rejected(lambda s: s["architecture"]["sections"][2]["blocks"].append({"type": "text", "text": "待补充"}), "占位")

    def test_unreadable_suite_exits_with_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.json"
            path.write_text("{not json", encoding="utf-8")
            code, _ = run_main([str(path), "--check"])
            self.assertEqual(code, 2)

    def test_architecture_that_never_names_a_system_is_a_warning_not_an_error(self) -> None:
        suite = load_suite()
        suite["systems"][1]["name"] = "平板页"
        suite["systems"][1].update(surface="admin", kind="wide")
        with tempfile.TemporaryDirectory() as tmp:
            path = write_suite(Path(tmp) / "s.json", suite)
            code, out = run_main([str(path), "--check"])
            self.assertEqual(code, 0, out)
            self.assertIn("警告：前端架构里没有提到「平板页」", out)


class LuzProjectTest(unittest.TestCase):
    """外壳产出的原型文件与页签要通过 Luz-Project 自己的校验器（没有 Luz-Project 就跳过）。"""

    @classmethod
    def setUpClass(cls) -> None:
        if not (PROJECT_SCRIPTS / "dev_documents.py").is_file():
            raise unittest.SkipTest("同级目录没有 Luz-Project，跳过对接校验")
        sys.path.insert(0, str(PROJECT_SCRIPTS))
        import dev_documents  # noqa: PLC0415

        cls.dd = dev_documents
        cls.tmp = Path(tempfile.mkdtemp(prefix="suite-project-"))
        cls.docs = cls.tmp / "docs" / "02-产品开发"
        cls.code, cls.out = run_main([str(SUITE), "--out", str(cls.docs / "doc.html"), "--number-from", "3", "--project-tabs", str(cls.tmp / "tabs.json")])

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)
        if str(PROJECT_SCRIPTS) in sys.path:
            sys.path.remove(str(PROJECT_SCRIPTS))

    def test_every_prototype_passes_prototype_errors(self) -> None:
        self.assertEqual(self.code, 0, self.out)
        tabs = json.loads((self.tmp / "tabs.json").read_text(encoding="utf-8"))
        self.assertEqual([t["title"] for t in tabs], SYSTEM_NAMES)
        for tab in tabs:
            block = tab["sections"][0]["blocks"][0]
            self.assertEqual(set(block), {"type", "file", "title", "kind", "library"}, "prototype 块只写 file、title、kind、library")
            with self.subTest(system=tab["title"]):
                self.assertEqual(self.dd._prototype_errors(f"页签「{tab['title']}」", block, self.tmp), [])

    def test_the_front_end_tabs_pass_the_tab_validator_and_the_frame(self) -> None:
        tabs = json.loads((self.tmp / "tabs.json").read_text(encoding="utf-8"))
        seen: dict[str, str] = {}
        for tab in tabs:
            self.assertEqual(self.dd._frontend_tab_errors(tab, self.tmp, seen), [], tab["title"])
        frame = [{"title": "前端规范"}] + tabs + [{"title": "检查与差异"}]
        self.assertEqual(self.dd._design_frame_errors(frame, None), [])
        self.assertEqual([t["surface"] for t in tabs], ["miniprogram", "web-admin"])
        self.assertEqual([Path(t["sections"][0]["blocks"][0]["file"]).name for t in tabs], ["03-小程序原型.html", "04-管理后台原型.html"])

    def test_the_hard_checks_are_met_by_the_prototype_files(self) -> None:
        for name in ("03-小程序原型.html", "04-管理后台原型.html"):
            text = (self.docs / name).read_text(encoding="utf-8")
            self.assertGreaterEqual(len(text.encode()), self.dd.PROTOTYPE_MIN_BYTES, name)
            for why, options in self.dd.PROTOTYPE_MARKERS.items():
                self.assertTrue(any(o in text for o in options), f"{name}{why}")
            used = self.dd.library_components(text, self.dd.component_libraries()["luz-kit"]["prefix"])
            self.assertGreaterEqual(len(used), self.dd.PROTOTYPE_MIN_COMPONENTS, name)
            self.assertEqual(su.proto_warnings(text), [], name)


class HygieneTest(unittest.TestCase):
    def test_no_private_or_industry_strings_in_the_new_files(self) -> None:
        files = [HERE / "build_prototype_suite.py", HERE / "test_prototype_suite.py", SUITE, SUITE.with_name("README.md"), SHELL_README]
        self.assertTrue(SHELL_README.is_file(), "shell/README.md 要存在")
        for f in files:
            text = f.read_text(encoding="utf-8")
            for word in PRIVATE:
                self.assertNotIn(word, text, f"{f.name} 含 {word!r}")
            self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text), f"{f.name} 含邮箱样式")
            self.assertIsNone(re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", text), f"{f.name} 含手机号样式")

    def test_the_demo_architecture_is_generic(self) -> None:
        text = json.dumps(load_suite()["architecture"], ensure_ascii=False)
        for word in (chr(0x82b1), "预约", "餐", "酒店", "医院"):
            self.assertNotIn(word, text)


# ------------------------------------------------------------------ 二、check_document.py

def check_document(path: Path) -> tuple[int, list[str]]:
    run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "check_document.py"), str(path), "--allow", "interface"], capture_output=True, text=True, encoding="utf-8")
    return run.returncode, [line.strip() for line in run.stdout.splitlines() if line.strip().startswith("ERROR")]


class CheckDocumentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="suite-check-"))
        run_main([str(SUITE), "--out", str(cls.tmp / "frame" / "d.html")])
        run_main([str(SUITE), "--out", str(cls.tmp / "single" / "d.html"), "--inline"])

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_shell_itself_has_no_errors(self) -> None:
        code, errors = check_document(self.tmp / "frame" / "d.html")
        self.assertEqual((code, errors), (0, []))

    def test_inline_errors_can_only_come_from_the_embedded_prototypes(self) -> None:
        page = (self.tmp / "single" / "d.html").read_text(encoding="utf-8")
        stripped = self.tmp / "single" / "stripped.html"
        stripped.write_text(re.sub(r'data-srcdoc="[^"]*"', 'data-srcdoc=""', page), encoding="utf-8")
        code, errors = check_document(stripped)
        self.assertEqual((code, errors), (0, []), "去掉内嵌的原型后，外壳自己零错误")
        _, inline_errors = check_document(self.tmp / "single" / "d.html")
        for line in inline_errors:
            self.assertRegex(line, r"font size 0 below", f"内嵌版多出的错误只应是原型里写的 font-size:0：{line}")


# ------------------------------------------------------------------ 三、浏览器

@unittest.skipUnless(browser_available(), "需要 playwright 和 Microsoft Edge，没有浏览器，跳过浏览器测试")
class BrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415

        cls.t0 = time.time()
        cls.tmp = Path(tempfile.mkdtemp(prefix="suite-browser-"))
        cls.frame = cls.tmp / "frame" / "d.html"
        cls.single = cls.tmp / "single" / "d.html"
        for argv in ([str(SUITE), "--out", str(cls.frame)], [str(SUITE), "--out", str(cls.single), "--inline"]):
            code, out = run_main(argv)
            assert code == 0, out
        # 五个页签的变体：把小程序原型复制成四份不同的文件，用来测 390 宽时页签条横向滚动
        many = cls.tmp / "many"
        many.mkdir()
        suite = load_suite()
        suite["systems"] = []
        for i, label in enumerate("甲乙丙丁"):
            shutil.copyfile(cls.frame.parent / "01-小程序原型.html", many / f"p{i}.html")
            suite["systems"].append({"name": f"小程序{label}", "surface": "miniapp", "file": str(many / f"p{i}.html")})
        suite["architecture"]["sections"][0]["blocks"].append({"type": "text", "text": "小程序甲、小程序乙、小程序丙、小程序丁。"})
        code, out = run_main([str(write_suite(cls.tmp / "many.json", suite)), "--out", str(many / "d.html")])
        assert code == 0, out
        cls.many = many / "d.html"
        cls.mini_tabs = [t["id"] for t in json.loads((TEMPLATES / "examples" / "generic-mini" / "spec.json").read_text(encoding="utf-8"))["tabbar"]]
        def leaves(nodes):          # a menu group (an accordion parent) has children and no page of its own; only a leaf is a page to open
            for t in nodes:
                if t.get("children"):
                    yield from leaves(t["children"])
                elif t.get("page"):
                    yield t
        cls.admin_nav = [t["page"] for t in leaves(json.loads((TEMPLATES / "examples" / "generic-admin" / "spec.json").read_text(encoding="utf-8"))["nav"])]
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="msedge")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.pw.stop()
        shutil.rmtree(cls.tmp, ignore_errors=True)
        print(f"\n[浏览器测试用时 {time.time() - cls.t0:.0f} 秒]", file=sys.stderr)

    def open(self, doc: Path, width: int = 1440, height: int = 900, scheme: str = "light", fragment: str = ""):
        ctx = self.browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
        self.addCleanup(ctx.close)
        page = ctx.new_page()
        page.problems = []
        page.external = []
        page.on("console", lambda m: page.problems.append(f"console {m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: page.problems.append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: page.problems.append(f"requestfailed: {r.url[:80]}"))
        page.on("request", lambda r: page.external.append(r.url[:80]) if r.url.split(":", 1)[0] not in ("file", "data", "blob", "about") else None)
        page.goto(doc.as_uri() + fragment)
        return page

    @staticmethod
    def proto(page, frame_id: str, timeout: float = 15.0):
        """内嵌页面载入完成后的 frame（等到原型的 K 起来）。"""
        end = time.time() + timeout
        while time.time() < end:
            handle = page.locator(f"#{frame_id}").element_handle()
            frame = handle.content_frame() if handle else None
            if frame:
                try:
                    if frame.evaluate("typeof K !== 'undefined' && !!K.S && !!K.cur()"):
                        return frame
                except Exception:  # noqa: BLE001  页面还在跳转
                    pass
            time.sleep(0.15)
        raise AssertionError(f"原型 {frame_id} 没有在 {timeout:.0f} 秒内载入")

    @staticmethod
    def selected(page) -> int:
        return page.evaluate("[].slice.call(document.querySelectorAll('.tabs [role=tab]')).findIndex(t => t.getAttribute('aria-selected') === 'true')")

    def test_opens_clean_with_the_right_tabs_and_loads_a_prototype_only_when_its_tab_is_shown(self) -> None:
        page = self.open(self.frame)
        names = page.locator(".tabs [role=tab]").all_inner_texts()
        self.assertEqual(names, ["前端架构", *SYSTEM_NAMES])
        self.assertEqual(self.selected(page), 0)
        for i in (1, 2):
            self.assertIsNone(page.locator(f"#proto-{i}").get_attribute("src"), "没切到页签之前不载入原型")
        page.get_by_role("tab", name="小程序").click()
        self.proto(page, "proto-1")
        self.assertTrue(page.locator("#proto-1").get_attribute("src"))
        self.assertIsNone(page.locator("#proto-2").get_attribute("src"), "别的页签的原型仍不载入")
        self.assertTrue(page.locator("#st-p1").is_visible())
        self.assertFalse(page.locator("#st-p0").is_visible())
        page.get_by_role("tab", name="管理后台").click()
        self.proto(page, "proto-2")
        self.assertEqual(page.evaluate("location.hash"), "#tab=2")
        self.assertEqual(page.problems, [])
        self.assertEqual(page.external, [], "文档与原型不连网")

    def test_each_system_tab_holds_exactly_one_prototype_and_nothing_else(self) -> None:
        page = self.open(self.frame)
        for i in (1, 2):
            panel = page.locator(f"#st-p{i}")
            self.assertEqual(panel.locator(".proto").count(), 1)
            self.assertEqual(panel.locator("iframe").count(), 1)
            self.assertEqual(panel.locator("table, ul, ol, img, figure, p, h3, pre").count(), 0, "系统页签里不放说明、清单、表和截图")
            self.assertEqual(panel.locator(".proto-bar button, .proto-bar a").all_inner_texts(), ["重新载入", "在新窗口打开"])
        arch = page.locator("#st-p0")
        self.assertEqual(arch.locator(".proto, iframe").count(), 0, "前端架构页签里没有原型")
        self.assertGreaterEqual(arch.locator("table").count(), 4)
        self.assertGreaterEqual(arch.locator("figure.fig").count(), 1)

    def test_the_prototypes_are_operable_inside_the_frames(self) -> None:
        page = self.open(self.frame)
        page.get_by_role("tab", name="小程序").click()
        mini = self.proto(page, "proto-1")
        target = self.mini_tabs[1]
        self.assertNotEqual(mini.evaluate("K.cur().tab"), target)
        mini.locator(f'[data-pt-tab="{target}"]').first.click()
        self.assertEqual(mini.evaluate("K.cur().tab"), target, "点标签栏要切页")
        page.get_by_role("tab", name="管理后台").click()
        admin = self.proto(page, "proto-2")
        nav = self.admin_nav[1]
        if admin.evaluate("document.getElementById('adApp').dataset.mode") != "wide":      # 工作区窄时菜单收进抽屉，先点菜单按钮
            admin.locator('[data-ad-side="toggle"]').first.click()
        admin.locator(f'.ad-ni[data-ad-nav="{nav}"]').first.click(timeout=5000)
        self.assertEqual(admin.evaluate("K.cur().tab"), nav, "点侧栏菜单要切页")
        self.assertEqual(page.problems, [])

    def test_reload_restarts_the_prototype_and_open_in_new_window_opens_it(self) -> None:
        page = self.open(self.frame, fragment="#tab=1")
        mini = self.proto(page, "proto-1")
        mini.evaluate("window.__mark = 1")
        reload = page.locator("#st-p1").get_by_role("button", name="重新载入")
        self.assertEqual(reload.count(), 1)
        reload.click()
        fresh = self.proto(page, "proto-1")
        self.assertIsNone(fresh.evaluate("window.__mark"), "重新载入后是一份新的原型")
        opener = page.locator("#st-p1").get_by_role("link", name="在新窗口打开")
        self.assertEqual(opener.count(), 1)
        with page.context.expect_page() as popup_info:
            opener.click()
        popup = popup_info.value
        popup.wait_for_load_state("load")
        self.assertTrue(unquote(popup.url).split("#")[0].endswith("01-小程序原型.html"), popup.url)
        self.proto_in(popup)
        self.assertEqual(page.problems, [])

    @staticmethod
    def proto_in(popup) -> None:
        end = time.time() + 15
        while time.time() < end:
            try:
                if popup.evaluate("typeof K !== 'undefined' && !!K.S"):
                    return
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.15)
        raise AssertionError("新窗口里的原型没有载入")

    def test_arrow_keys_home_end_and_the_address_hash(self) -> None:
        page = self.open(self.frame)
        page.locator("#st-t0").focus()
        page.keyboard.press("ArrowRight")
        self.assertEqual(self.selected(page), 1)
        self.assertEqual(page.evaluate("location.hash"), "#tab=1")
        page.keyboard.press("ArrowRight")
        self.assertEqual(self.selected(page), 2)
        page.keyboard.press("ArrowRight")
        self.assertEqual(self.selected(page), 0, "到头后回到第一个")
        page.keyboard.press("ArrowLeft")
        self.assertEqual(self.selected(page), 2)
        page.keyboard.press("Home")
        self.assertEqual(self.selected(page), 0)
        page.keyboard.press("End")
        self.assertEqual(self.selected(page), 2)
        direct = self.open(self.frame, fragment="#tab=2")
        self.assertEqual(self.selected(direct), 2, "#tab=2 直达第三个页签")
        self.assertTrue(direct.locator("#st-p2").is_visible())
        self.assertFalse(direct.locator("#st-p0").is_visible())
        self.proto(direct, "proto-2")
        self.assertIsNone(direct.locator("#proto-1").get_attribute("src"))
        direct.evaluate("location.hash = '#tab=1'")
        self.assertEqual(self.selected(direct), 1, "改地址里的井号也跟着切")

    def test_print_shows_every_tab_and_loads_every_prototype(self) -> None:
        page = self.open(self.frame)
        page.emulate_media(media="print")
        self.assertEqual(page.locator(".tabs").evaluate("e => getComputedStyle(e).display"), "none")
        for i in range(3):
            self.assertEqual(page.locator(f"#st-p{i}").evaluate("e => getComputedStyle(e).display"), "block", f"打印时第 {i} 个页签展开")
        self.assertEqual(page.locator(".print-title").first.evaluate("e => getComputedStyle(e).display"), "block", "打印时系统页签要有标题")
        self.assertEqual(page.locator(".proto-act").first.evaluate("e => getComputedStyle(e).display"), "none")
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        for i in (1, 2):
            self.assertTrue(page.locator(f"#proto-{i}").get_attribute("src"), "打印前载入全部原型")

    def test_light_and_dark_follow_the_system(self) -> None:
        shades = {}
        for scheme in ("light", "dark"):
            page = self.open(self.frame, scheme=scheme)
            shades[scheme] = page.evaluate("(() => { const c = getComputedStyle(document.body).backgroundColor.match(/\\d+/g).map(Number); return (c[0] + c[1] + c[2]) / 3 })()")
            self.assertEqual(page.problems, [], scheme)
        self.assertGreater(shades["light"], 220)
        self.assertLess(shades["dark"], 50)

    def test_phone_width_has_no_horizontal_overflow_and_the_tab_strip_scrolls(self) -> None:
        page = self.open(self.many, width=390, height=844)
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390, "前端架构页签（含表格、分层图）不撑破页面")
        strip = page.locator(".tabs")
        self.assertEqual(strip.evaluate("e => getComputedStyle(e).overflowX"), "auto")
        self.assertGreater(strip.evaluate("e => e.scrollWidth - e.clientWidth"), 20, "页签多时，页签条自己横向滚动")
        strip.evaluate("e => { e.scrollLeft = 9999 }")
        self.assertGreater(strip.evaluate("e => e.scrollLeft"), 0)
        strip.evaluate("e => { e.scrollLeft = 0 }")
        page.get_by_role("tab", name="小程序丁").click()
        right = page.locator("#st-t4").evaluate("e => e.getBoundingClientRect().right")
        self.assertLessEqual(right, 391, "选中的页签要滚进视野")
        frame = self.proto(page, "proto-4")
        box = page.locator("#st-p4 .proto").bounding_box()
        self.assertGreaterEqual(box["x"], 0)
        self.assertLessEqual(box["x"] + box["width"], 390.5, "原型框不超出手机宽度")
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        self.assertLessEqual(frame.evaluate("document.documentElement.scrollWidth - window.innerWidth"), 0, "原型自己在 390 宽下没有横向滚动")
        target = self.mini_tabs[1]
        frame.locator(f'[data-pt-tab="{target}"]').first.click()
        self.assertEqual(frame.evaluate("K.cur().tab"), target, "手机宽度下原型照样能点")
        self.assertEqual(page.problems, [])

    def test_the_inline_document_works_like_the_iframe_one(self) -> None:
        page = self.open(self.single)
        self.assertEqual(page.locator(".tabs [role=tab]").all_inner_texts(), ["前端架构", *SYSTEM_NAMES])
        self.assertFalse(page.locator("#proto-1").evaluate("e => e.hasAttribute('srcdoc')"), "没切到页签之前不载入")
        page.get_by_role("tab", name="小程序").click()
        mini = self.proto(page, "proto-1")
        self.assertTrue(page.locator("#proto-1").evaluate("e => e.hasAttribute('srcdoc')"))
        self.assertFalse(page.locator("#proto-2").evaluate("e => e.hasAttribute('srcdoc')"))
        target = self.mini_tabs[1]
        mini.locator(f'[data-pt-tab="{target}"]').first.click()
        self.assertEqual(mini.evaluate("K.cur().tab"), target)
        mini.evaluate("window.__mark = 1")
        page.locator("#st-p1").get_by_role("button", name="重新载入").click()
        self.assertIsNone(self.proto(page, "proto-1").evaluate("window.__mark"))
        with page.context.expect_page() as popup_info:
            page.locator("#st-p1").get_by_role("button", name="在新窗口打开").click()
        popup = popup_info.value
        popup.wait_for_load_state("load")
        self.proto_in(popup)
        page.get_by_role("tab", name="管理后台").click()
        self.proto(page, "proto-2")
        self.assertEqual(page.problems, [])
        self.assertEqual(page.external, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
