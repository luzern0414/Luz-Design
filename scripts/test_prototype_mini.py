"""原型模板（引擎 + mini 模板 + 生成器 + 规格 schema + 示例）的测试。

    py -X utf8 scripts/test_prototype_mini.py

分两部分：
1. 不要浏览器：生成器能构建、坏规格逐类报中文错、schema 自身有效、通用部分没有行业字样、Luz-Project 的原型硬检查。
2. 要浏览器（Playwright + Microsoft Edge，没有就跳过并写明）：对每个示例（通用商城、花店、到店预约；某个示例不在时跳过）打开、标签栏、返回、
   流程完成回到发起处、弹层与焦点陷阱、表单校验、配置面板、场景、逻辑面板、减少动态、重置演示数据、390 手机与 1500 桌面布局、深浅外观。
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_prototype as bp  # noqa: E402

TEMPLATES = HERE.parent / "references" / "prototype-templates"
EXAMPLES = {name: TEMPLATES / "examples" / name / "spec.json" for name in ("generic-mini", "florist-mini", "booking-mini")}
INDUSTRY = "\u82b1"  # 通用部分不许出现的行业字；用转义写，免得本文件自己带这个字


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


def per_example(fn):
    """对每个已构建的示例各跑一遍测试方法，每个示例一个 subTest，互不牵连。"""

    def wrapper(self):
        for name in self.built:
            with self.subTest(example=name):
                fn(self, name, self.specs[name])

    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def errors_of(spec: dict, content: str = "") -> list[str]:
    import importlib.util

    kind_path = TEMPLATES / spec["kind"] / "build_kind.py"
    mod_spec = importlib.util.spec_from_file_location("kind_under_test", kind_path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    ctx = bp.Ctx(spec, EXAMPLES["generic-mini"], TEMPLATES / spec["kind"], bp.component_index())
    errs, _ = bp.check_spec(spec, content, mod, ctx)
    return errs


def page_of(spec: dict, pid: str) -> dict:
    return next(p for p in spec["pages"] if p["id"] == pid)


# ------------------------------------------------------------------ 一、不要浏览器

class SchemaTest(unittest.TestCase):
    def test_schema_is_a_valid_json_schema(self) -> None:
        schema = bp.load_schema()
        try:
            import jsonschema  # noqa: PLC0415

            jsonschema.Draft202012Validator.check_schema(schema)
        except ImportError:
            pass
        defs = schema["$defs"]

        def walk(node, path="$"):
            if isinstance(node, dict):
                if "$ref" in node:
                    target = schema
                    for part in node["$ref"].lstrip("#/").split("/"):
                        self.assertIn(part, target, f"{path}: $ref {node['$ref']} 指向不存在的定义")
                        target = target[part]
                if "properties" in node:
                    for r in node.get("required", []):
                        self.assertIn(r, node["properties"], f"{path}: required 里的 {r} 不在 properties 里")
                if "enum" in node:
                    self.assertTrue(node["enum"], f"{path}: enum 不能为空")
                for k, v in node.items():
                    walk(v, f"{path}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")

        walk(schema)
        for needed in ("page", "logic", "blockItem", "flow", "scene", "step"):
            self.assertIn(needed, defs)

    def test_validator_reports_chinese_errors(self) -> None:
        schema = bp.load_schema()
        errs = bp.validate_schema({"schema": "x", "kind": "web", "meta": {}, "pages": []}, schema, schema)
        text = "\n".join(errs)
        self.assertIn("固定值", text)
        self.assertIn("不在允许的取值里", text)
        self.assertIn("缺少必填字段「title」", text)
        self.assertIn("至少 1 项", text)

    def test_examples_validate(self) -> None:
        schema = bp.load_schema()
        for name, path in EXAMPLES.items():
            if path.is_file():
                self.assertEqual(bp.validate_schema(load(path), schema, schema), [], name)


class GeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = load(EXAMPLES["generic-mini"])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def spec(self) -> dict:
        return copy.deepcopy(self.base)

    def test_generic_example_builds_a_single_file_within_the_size_budget(self) -> None:
        out = Path(self.tmp.name) / "generic.html"
        self.assertEqual(bp.build(EXAMPLES["generic-mini"], out), 0)
        text = out.read_text(encoding="utf-8")
        size = out.stat().st_size
        self.assertGreater(size, 120_000)
        self.assertLess(size, 2 * 1024 * 1024)
        for marker in ("K.panel(", "showModal", "prefers-reduced-motion", "data-cid=", "data-shell"):
            self.assertIn(marker, text, marker)
        self.assertNotRegex(text, r'<(?:script|link)[^>]+(?:src|href)="https?://')  # 单文件，不加载外部资源

    def test_only_used_block_files_are_embedded(self) -> None:
        spec = self.spec()
        spec["pages"] = [p for p in spec["pages"] if p["id"] in ("home", "cart", "me", "cat")]
        for p in spec["pages"]:
            p["blocks"] = [{"cid": "MP-CARD-001"}]
            p.pop("links", None)
            p.pop("footer", None)
            p.pop("roles", None)
        spec["tabbar"] = [t for t in spec["tabbar"] if t["page"] in {p["id"] for p in spec["pages"]}]
        spec["flows"], spec["scenes"], spec["actions"], spec["roles"] = [], [], {}, []
        for p in spec["pages"]:
            p.pop("scenes", None)
        path = Path(self.tmp.name) / "small" / "spec.json"
        path.parent.mkdir()
        path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        out = Path(self.tmp.name) / "small.html"
        self.assertEqual(bp.build(path, out), 0)
        text = out.read_text(encoding="utf-8")
        self.assertIn("MP-CARD-001", text)
        self.assertNotIn("MP-GOODS-001", text)  # 没用到的 blocks 文件不带
        self.assertNotIn("adtbl001", text)  # 后台组件的 blocks 文件也不带

    def test_bad_specs_are_reported_one_class_at_a_time(self) -> None:
        cases = {
            "标签栏页面不存在": (lambda s: s["tabbar"][0].update(page="nope"), "「nope」不存在"),
            "页面引用不存在": (lambda s: page_of(s, "home")["blocks"][3].update(go={".c@0": "ghost"}), "指向的页面「ghost」不存在"),
            "go 指向标签栏页面": (lambda s: page_of(s, "home")["blocks"][3].update(go={".c@0": "cart"}), "是标签栏页面"),
            "二级页放进标签栏": (lambda s: s["tabbar"].append({"id": "x", "name": "列表", "icon": "grid", "page": "list"}), "二级页不能出现在标签栏里"),
            "一级页不在标签栏": (lambda s: s["tabbar"].pop(), "不在标签栏里"),
            "孤岛页面": (lambda s: s["pages"].append({"id": "island", "name": "孤岛", "type": "sub", "tab": "home", "blocks": [{"cid": "MP-CARD-001"}], "logic": copy.deepcopy(page_of(s, "list")["logic"])}), "孤岛页面「island」"),
            "重复入口": (lambda s: page_of(s, "home")["blocks"][3].update(go={".c@0": "detail:1", ".c@1": "detail:1"}), "同一目的地"),
            "标签栏已有入口在页内重复": (lambda s: page_of(s, "home")["blocks"][3].update(tab={".c@0": "cart"}), "标签栏已经有"),
            "组件编号不在库里": (lambda s: page_of(s, "home")["blocks"].append({"cid": "MP-NOPE-999"}), "不在组件库里"),
            "流程引用不存在的页面": (lambda s: s["flows"][0]["steps"].append("ghost"), "流程「browse」引用的页面「ghost」不存在"),
            "back 指向不存在的页面": (lambda s: page_of(s, "detail")["logic"].update(back={"to": "ghost", "text": "x"}), "logic.back.to 指向的页面「ghost」不存在"),
            "done 指向不存在的页面": (lambda s: page_of(s, "detail")["logic"].update(done={"to": "ghost", "text": "x"}), "logic.done.to 指向的页面「ghost」不存在"),
            "缺逻辑字段": (lambda s: page_of(s, "detail")["logic"].pop("primary"), "缺逻辑字段：logic.primary"),
            "动作里的跳转不存在": (lambda s: s["actions"]["search"].append({"go": "ghost"}), "动作「search」"),
            "页面没有内容": (lambda s: (page_of(s, "cat").pop("blocks")), "没有内容"),
            "页面 id 重复": (lambda s: s["pages"].append(copy.deepcopy(page_of(s, "cat"))), "重复"),
            "模块标识重复": (lambda s: [b.update(id="same") for b in page_of(s, "home")["blocks"][:2]], "模块标识「same」重复"),
            "字段拼错": (lambda s: page_of(s, "home")["blocks"][0].update(gogo={".x": "list"}), "多余的字段「gogo」"),
        }
        for name, (mutate, expect) in cases.items():
            with self.subTest(name):
                spec = self.spec()
                mutate(spec)
                errs = errors_of(spec)
                self.assertTrue(any(expect in e for e in errs), f"{name}：期望报错里有「{expect}」，实际：{errs[:5]}")

    def test_check_flag_exits_nonzero_on_a_bad_spec_and_zero_on_a_good_one(self) -> None:
        bad = self.spec()
        bad["tabbar"][0]["page"] = "nope"
        path = Path(self.tmp.name) / "bad" / "spec.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "build_prototype.py"), str(path), "--check"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 1)
        self.assertIn("错误：", run.stdout)
        good = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "build_prototype.py"), str(EXAMPLES["generic-mini"]), "--check"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)

    def test_component_index_covers_the_library(self) -> None:
        index = bp.component_index()
        self.assertGreaterEqual(len(index), 300)
        self.assertEqual(index["MP-CARD-001"], "blocks1.js")
        self.assertTrue(index["MP-GOODS-001"].startswith("blocks-mp-"))
        self.assertTrue(index["AD-TBL-001"].startswith("blocks-ad-"))

    def test_generic_home_follows_the_page_pattern_rules(self) -> None:
        """首页范式：门店与配送在顶部、金刚区只放高频核心入口、不放账户类与订单类、也不重复标签栏。"""
        import page_pattern as pp

        spec = load(EXAMPLES["generic-mini"])
        home = page_of(spec, "home")
        dock = next(b for b in home["blocks"] if b["cid"] == "MP-ENT-001")
        names = [dock.get("text", {}).get(f".i1>div@{i}") for i in range(6)]
        labels = ["新品", "热销", "礼品", "极速达", "同城", "礼卡"]
        self.assertEqual(len([n for n in names if n]), 1)
        words = pp.ACCOUNT_WORDS + pp.ORDER_WORDS + pp.CONTEXT_WORDS
        for label in labels:
            self.assertFalse(any(w in label for w in words), label)
        self.assertNotIn(set(labels) & {t["name"] for t in spec["tabbar"]}, [{"首页"}])
        self.assertEqual(len({v for v in dock["go"].values()}), 6)  # 同一页同一目的地不重复
        self.assertIn("望京店", json.dumps(home["blocks"][0], ensure_ascii=False))  # 门店在顶部


    def test_examples_show_different_home_compositions_from_the_same_mechanism(self) -> None:
        """同一套机制长出不同的首页：商城首页有搜索与金刚区，预约首页是门店上下文栏 + 入口大卡 + 单列预约列表，且没有购物车与交易页面。"""
        generic, booking = load(EXAMPLES["generic-mini"]), load(EXAMPLES["booking-mini"])
        g_home = {b["cid"] for b in page_of(generic, "home")["blocks"] if "cid" in b}
        b_home = {b["cid"] for b in page_of(booking, "home")["blocks"] if "cid" in b}
        self.assertIn("MP-ENT-001", g_home)
        self.assertNotIn("MP-ENT-001", b_home)
        self.assertEqual(b_home, {"MP-SVC-001", "MP-ENT-003", "MP-SVC-005"})
        ids = {p["id"] for p in booking["pages"]}
        self.assertFalse(ids & {"cart", "checkout", "orders", "order", "pay", "coupons", "addresses"}, "预约示例里没有商品交易页面")
        self.assertEqual([t["name"] for t in booking["tabbar"]], ["首页", "预约", "我的"])
        self.assertNotEqual([t["id"] for t in generic["tabbar"]], [t["id"] for t in booking["tabbar"]])
        self.assertTrue(8 <= len(booking["pages"]) <= 11)
        text = json.dumps(booking, ensure_ascii=False)
        for word in ("购物车", "加入购物车", "优惠券", "收银台", "订单"):
            self.assertNotIn(word, text.replace("订单", "") if word == "订单" else text)

    def test_checker_does_not_demand_industry_pages(self) -> None:
        """校验只查结构与引用：没有购物车、订单、搜索，也没有搜索页的规格照样通过。"""
        for name in ("booking-mini",):
            self.assertEqual(errors_of(load(EXAMPLES[name])), [], name)
        spec = {"schema": "luz-prototype/1", "kind": "mini", "meta": {"title": "单页"}, "tabbar": [{"id": "a", "name": "唯一", "icon": "home", "page": "a"}],
                "pages": [{"id": "a", "name": "唯一的页", "type": "tab", "tab": "a", "blocks": [{"cid": "MP-CARD-001"}], "logic": {"from": "启动", "back": "无", "done": "无", "primary": "无", "rules": ["无"]}}]}
        self.assertEqual(errors_of(spec), [])

    def test_help_and_messages_speak_of_references_not_required_templates(self) -> None:
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "build_prototype.py"), "--help"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0)
        self.assertNotIn("模板必须", run.stdout)
        self.assertIn("不查行业内容", run.stdout)
        errs = errors_of(self.spec() | {"tabbar": []})
        self.assertTrue(any("规格里没有" in e for e in errs), errs)
        for e in errors_of({**self.spec(), "tabbar": [{"id": "x", "name": "x", "icon": "home", "page": "ghost"}]}):
            self.assertNotIn("必须包含", e)


class EngineRequestsTest(unittest.TestCase):
    """后台模板向引擎提的请求里属于生成器与 schema 的部分：R1 分组节点、R2 kind 报边、R7 后台字段。"""

    def mini(self) -> dict:
        return copy.deepcopy(load(EXAMPLES["booking-mini"]))

    def test_r7_schema_accepts_admin_fields_and_rejects_the_unused_panel_type(self) -> None:
        schema = bp.load_schema()
        spec = self.mini()
        spec["theme"].update(sidebar="dark", density="compact")
        spec["shell"] = {"today": "2026-11-04", "version": "v1.2", "env": "测试环境", "account": {"name": "管理员", "av": 1}, "notices": [{"id": "n1", "title": "x", "read": False}],
                         "noticePage": "home", "profilePage": "me", "readonlyRoles": ["viewer"], "versionInfo": [["版本", "1.2"]]}
        spec["roles"] = [{"id": "viewer", "name": "只读", "readonly": True}]
        spec["pages"][0].update(list={"columns": []}, actions=[{"id": "a"}], crumb="x", titleNew="新建")
        self.assertEqual(bp.validate_schema(spec, schema, schema), [])
        spec["pages"][0]["type"] = "panel"
        self.assertTrue(any("panel" in e for e in bp.validate_schema(spec, schema, schema)), "schema 里没有 panel 类型了")
        spec["pages"][0]["type"] = "tab"
        spec["theme"]["sidebar"] = "blue"
        self.assertTrue(any("sidebar" in e for e in bp.validate_schema(spec, schema, schema)))

    def test_r7_top_level_shell_is_merged_into_data_shell_and_its_pages_are_checked(self) -> None:
        spec = self.mini()
        spec["shell"] = {"today": "2026-11-04", "noticePage": "ghost"}
        self.assertTrue(any("shell.noticePage" in e for e in errors_of(spec)))
        spec["shell"]["noticePage"] = "home"
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(bp.build(d / "spec.json", d / "x.html"), 0)
            html = (d / "x.html").read_text(encoding="utf-8")
        built = json.loads(re.search(r"const SPEC = (\{.*?\});\n", html, re.S).group(1).replace("<\\/", "</"))
        self.assertEqual(built["data"]["shell"]["today"], "2026-11-04")

    def test_r1_nav_group_nodes_need_children_and_are_not_tabs(self) -> None:
        pages = [{"id": p, "name": p, "type": "tab", "tab": p, "blocks": [{"cid": "MP-CARD-001"}], "logic": {"from": "x", "back": "无", "done": "无", "primary": "无", "rules": ["x"]}} for p in ("a", "b")]
        spec = {"schema": "luz-prototype/1", "kind": "admin", "meta": {"title": "t"}, "pages": pages,
                "nav": [{"id": "g", "name": "业务", "children": [{"id": "a", "name": "A", "page": "a", "icon": "home"}, {"id": "b", "name": "B", "page": "b", "icon": "home"}]}]}
        errs, _ = bp.check_spec(spec)
        self.assertEqual(errs, [], "分组节点没有 page 不报错，子项照常检查")
        spec["nav"][0]["children"] = []
        errs, _ = bp.check_spec(spec)
        self.assertTrue(any("既没有 page 也没有 children" in e for e in errs), errs)
        spec["nav"] = [{"id": "g", "name": "业务", "children": [{"id": "a", "name": "A", "page": "ghost", "icon": "home"}]}] + [{"id": "b", "name": "B", "page": "b", "icon": "home"}]
        errs, _ = bp.check_spec(spec)
        self.assertTrue(any("指向的页面「ghost」不存在" in e for e in errs))

    def test_r2_kind_edges_hook_feeds_the_orphan_and_duplicate_checks(self) -> None:
        import types

        spec = self.mini()
        isle = {"id": "isle", "name": "只由行操作到达", "type": "sub", "tab": "home", "blocks": [{"cid": "MP-CARD-001"}], "logic": copy.deepcopy(page_of(spec, "store")["logic"])}
        spec["pages"].append(isle)
        errs, _ = bp.check_spec(spec)
        self.assertTrue(any("孤岛页面「isle」" in e for e in errs))
        kind = types.SimpleNamespace(edges=lambda page, s: ["isle"] if page["id"] == "home" else [])
        errs, _ = bp.check_spec(spec, kind_mod=kind)
        self.assertFalse(any("孤岛页面「isle」" in e for e in errs), "kind 报出的边让它可达")
        kind = types.SimpleNamespace(edges=lambda page, s: [{"target": "isle", "name": "行操作 A", "dup": True}, {"target": "isle", "name": "行操作 B", "dup": True}] if page["id"] == "home" else [])
        errs, _ = bp.check_spec(spec, kind_mod=kind)
        self.assertTrue(any("同一目的地「isle」有 2 个入口" in e for e in errs))
        kind = types.SimpleNamespace(edges=lambda page, s: ["ghost"] if page["id"] == "home" else [])
        errs, _ = bp.check_spec(spec, kind_mod=kind)
        self.assertTrue(any("kind 报出的跳转目标「ghost」不存在" in e for e in errs))


class OneH1Test(unittest.TestCase):
    """同一时刻整个文档只有一个 h1（外壳里的产品名）：内容模块、库、kind 里写的 <h1> 在生成时降成 <h2 data-h1>，运行时塞进来的也降。"""

    def test_demotion_rewrites_markup_and_selectors_without_touching_class_names(self) -> None:
        text, n = bp.demote_h1_markup('<h1 class="t">a</h1> x <h1>b</h1> <h10>y</h10> `<h1 \\n id="z">`')
        self.assertEqual(n, 3)
        self.assertNotRegex(text, r"<h1[\s>/]")
        self.assertIn('<h2 data-h1 class="t">a</h2>', text)
        self.assertIn("<h10>", text)
        css, k = bp.demote_h1_css("/* h1 注释 */ h1{a:1} .x h1, h1::before, .h1, #h1, .a-h1{b:2} h1.t > h1:hover{c:3}")
        self.assertEqual(k, 5)
        self.assertIn("/* h1 注释 */", css)
        self.assertIn(".h1, #h1, .a-h1{b:2}", css)
        self.assertIn(".x h2:where([data-h1]), h2:where([data-h1])::before", css)

    def test_every_example_has_one_h1_in_the_source_and_check_document_has_no_h1_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for name, spec_path in EXAMPLES.items():
                if not spec_path.is_file():
                    continue
                with self.subTest(example=name):
                    out = Path(tmp) / f"{name}.html"
                    self.assertEqual(bp.build(spec_path, out), 0)
                    self.assertEqual(len(re.findall(r"<h1[\s>]", out.read_text(encoding="utf-8"), re.I)), 1, "整个文件只有外壳里的一个 h1")
                    run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "check_document.py"), str(out), "--allow", "interface"], capture_output=True, text=True, encoding="utf-8")
                    h1_lines = [ln for ln in (run.stdout + run.stderr).splitlines() if re.search(r"\bh1\b", ln, re.I)]
                    self.assertEqual(h1_lines, [], "check_document 不应再报 h1 相关的错")


class TokensAndMotionTest(unittest.TestCase):
    """深色走真令牌（不再有滤镜）、外壳令牌名不与库重名、引擎动效只有四档时长、示例页面不写工具话。"""

    def css(self, *names: str) -> str:
        return "\n".join((TEMPLATES / n).read_text(encoding="utf-8") for n in names)

    def test_no_invert_filter_and_dark_stage_is_night(self) -> None:
        for name in ("engine/engine.css", "mini/mini.css", "engine/engine.js", "mini/mini.js"):
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            self.assertNotIn("invert(", text, name)
            self.assertNotRegex(text, r'class="[^"]*\bst dark\b', name)
        self.assertIn("'night'", (TEMPLATES / "engine" / "engine.js").read_text(encoding="utf-8"))
        self.assertIn('[data-stage="night"]', self.css("engine/engine.css"))

    def test_generated_page_is_token_dark_and_exports_the_library_appearance_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "x.html"
            self.assertEqual(bp.build(EXAMPLES["booking-mini"], out), 0)
            text = out.read_text(encoding="utf-8")
        self.assertIn('data-dark-mode="tokens"', text)
        self.assertIn("setAppearance, getAppearance, isDark, APPEARANCES", text)

    def test_shell_variable_names_do_not_collide_with_the_library_tokens(self) -> None:
        kit = (bp.LIBRARY / "src" / "kit.css").read_text(encoding="utf-8")
        library = set(re.findall(r"(?<![\w-])(--[\w-]+)\s*:", kit))
        self.assertGreater(len(library), 100)
        mine = set(re.findall(r"(?<![\w-])(--[\w-]+)\s*:", self.css("engine/engine.css", "mini/mini.css")))
        self.assertTrue(mine, "外壳应该有自己的变量")
        self.assertEqual(sorted(mine & library), [], "外壳变量要加前缀，不能与库的令牌同名")

    def test_engine_motion_uses_only_four_durations_and_never_transition_all(self) -> None:
        css = re.sub(r"/\*.*?\*/", "", self.css("engine/engine.css", "mini/mini.css"), flags=re.S)  # 注释里可以写“不用 transition: all”
        self.assertNotRegex(css, r"transition\s*:\s*all")
        tokens = {"100ms", "150ms", "200ms", "300ms"}
        declared = re.findall(r"(--mo-\d+)\s*:\s*(\d+ms)", css)
        self.assertEqual(sorted(d for _, d in declared), sorted(tokens))
        # transition 与 animation（不含循环的骨架闪动）里直接写的时长也要在四档里
        for decl in re.findall(r"(?:transition|animation)\s*:[^;}]+", css):
            if "infinite" in decl:
                continue
            for dur in re.findall(r"(?<![\w.-])(\d*\.?\d+m?s)\b", decl):
                if dur in ("0s", ".001ms"):
                    continue
                ms = float(dur[:-2]) if dur.endswith("ms") else float(dur[:-1]) * 1000
                self.assertIn(f"{int(ms)}ms", tokens, f"{decl.strip()}：时长要用 100/150/200/300 毫秒四档")
        js = (TEMPLATES / "engine" / "engine.js").read_text(encoding="utf-8")
        self.assertIn("150)", js[js.index("function closeDialog"):js.index("function syncSheet")], "退出动画取进入 200ms 的 75%")

    def test_examples_carry_no_tool_talk_in_the_page_header(self) -> None:
        tool_words = ("模板", "规格", "组件库", "拼装", "生成", "示例")
        for name, path in EXAMPLES.items():
            if not path.is_file():
                continue
            meta = load(path)["meta"]
            for key in ("title", "subtitle", "brand"):
                for w in tool_words:
                    self.assertNotIn(w, meta.get(key, ""), f"{name} 的 meta.{key} 不要写工具话（说明放示例 README）")


class IndustryWordsTest(unittest.TestCase):
    def test_generic_template_and_code_carry_no_industry_words(self) -> None:
        roots = [TEMPLATES / "engine", TEMPLATES / "mini", TEMPLATES / "schema", TEMPLATES / "examples" / "generic-mini", HERE / "build_prototype.py"]
        hits = []
        for root in roots:
            files = [root] if root.is_file() else [f for f in root.rglob("*") if f.is_file() and f.suffix in {".md", ".js", ".css", ".html", ".json", ".py", ".txt"} and "dist" not in f.parts and "__pycache__" not in f.parts]
            for f in files:
                text = f.read_text(encoding="utf-8", errors="replace")
                if INDUSTRY in text:
                    hits.append(f"{f.relative_to(HERE.parent)}：{text[max(0, text.index(INDUSTRY) - 10):text.index(INDUSTRY) + 12]!r}")
                if re.search(r"florist|flower|bouquet", text.replace("florist-mini", ""), re.I):  # 只许提到示例目录名
                    hits.append(f"{f.relative_to(HERE.parent)}：英文行业词")
        self.assertEqual(hits, [])

    def test_template_files_carry_no_private_paths(self) -> None:
        bad = ("Users\\", "skill\u8f93\u51fa", "@gmail", "@qq.com")
        hits = []
        for root in (TEMPLATES / "engine", TEMPLATES / "mini", TEMPLATES / "schema", TEMPLATES / "examples", HERE / "build_prototype.py", HERE / "test_prototype_mini.py"):
            files = [root] if root.is_file() else [f for f in root.rglob("*") if f.is_file() and f.suffix in {".md", ".js", ".css", ".html", ".json", ".py"} and "dist" not in f.parts]
            for f in files:
                text = f.read_text(encoding="utf-8", errors="replace")
                hits += [f"{f.name}:{w}" for w in bad if w in text and f.name != "test_prototype_mini.py"]
                hits += [f"{f.name}:手机号" for _ in re.findall(r"(?<!\d)1[3-9]\d{9}(?!\d)", text)]
        self.assertEqual(hits, [])


class LuzProjectCompatTest(unittest.TestCase):
    def test_built_prototype_passes_the_luz_project_checks(self) -> None:
        sys.path.insert(0, r"D:\Codes\Luz-Project\scripts")
        try:
            import dev_documents  # noqa: PLC0415
        except Exception as exc:  # noqa: BLE001
            self.skipTest(f"读不到 Luz-Project 的 dev_documents：{exc}")
        if "luz-kit" not in dev_documents.component_libraries():
            self.skipTest("Luz-Project 的库登记里还没有 luz-kit")
        with tempfile.TemporaryDirectory() as tmp:
            for name, spec_path in EXAMPLES.items():
                if not spec_path.is_file():
                    continue
                out = Path(tmp) / name / "x.html"
                self.assertEqual(bp.build(spec_path, out), 0, name)
                errs = dev_documents._prototype_errors("测试", {"title": "原型", "kind": "phone", "file": "x.html", "library": "luz-kit"}, out.parent)
                self.assertEqual(errs, [], name)


# ------------------------------------------------------------------ 二、要浏览器

@unittest.skipUnless(browser_available(), "需要 playwright 和 Microsoft Edge；没有浏览器时这一组跳过")
class BrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from playwright.sync_api import sync_playwright

        cls.tmp = tempfile.TemporaryDirectory()
        cls.built: dict[str, Path] = {}
        cls.specs: dict[str, dict] = {}
        for name, path in EXAMPLES.items():
            if path.is_file():
                out = Path(cls.tmp.name) / name / "x.html"
                assert bp.build(path, out) == 0, name
                cls.built[name] = out
                cls.specs[name] = load(path)
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="msedge")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.pw.stop()
        cls.tmp.cleanup()

    # -- 工具
    def open(self, name: str, width: int = 1500, height: int = 900, **ctx_args):
        context = self.browser.new_context(viewport={"width": width, "height": height}, locale="zh-CN", **ctx_args)
        page = context.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(f"{m.type}: {m.text[:200]}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"pageerror: {str(e)[:200]}"))
        page.goto(self.built[name].as_uri())
        page.wait_for_function("window.__PT__ && __PT__.cur && __PT__.cur().id")
        self.addCleanup(context.close)
        return page, errors

    @staticmethod
    def page_with(page, spec, selector):
        """依次打开各页（不含弹层），返回第一个含 selector 的页面 id（停在那一页）。"""
        for p in spec["pages"]:
            if p["type"] == "sheet" or p.get("roles"):
                continue
            page.evaluate(f"__PT__.jump('{p['id']}')")
            if page.locator(selector).count():
                return p["id"]
        return None

    @staticmethod
    def cur(page) -> dict:
        return page.evaluate("(() => { const c = __PT__.cur(); return {id: c.id, a: c.a, tab: c.tab, depth: c.depth, sheet: __PT__.S.sheet && __PT__.S.sheet.id, dlg: (d => d.open && !d.classList.contains('closing'))(document.getElementById('ptDlg'))} })()")

    # -- 打开、标签栏、返回、流程
    @per_example
    def test_opens_without_console_errors_and_tabbar_switches(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        self.assertTrue(page.locator("#ptScreen .pt-tabbar").is_visible())
        for t in spec["tabbar"]:
            page.locator(f'#ptScreen .pt-tabbar [data-pt-tab="{t["id"]}"]').click()
            c = self.cur(page)
            self.assertEqual((c["tab"], c["id"], c["depth"]), (t["id"], t["page"], 0), t["id"])
            self.assertEqual(page.locator(f'#ptScreen .pt-tabbar button.on').get_attribute("data-pt-tab"), t["id"])
        self.assertEqual(errors, [])

    @per_example
    def test_sub_page_hides_tabbar_back_returns_to_source_and_flow_done_returns_to_origin(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        pages = {p["id"]: p for p in spec["pages"]}
        subs = [p["id"] for p in spec["pages"] if p["type"] == "sub" and not p.get("roles")]
        root = spec["tabbar"][0]
        base = subs[0]
        page.evaluate(f"__PT__.toTab('{root['id']}')")
        self.assertTrue(page.evaluate(f"__PT__.go('{base}')"))
        self.assertEqual(self.cur(page)["depth"], 1)
        self.assertEqual(page.locator("#ptScreen .pt-tabbar").count(), 0, "二级页要隐藏标签栏")
        # 标签页不能用 go（微信 navigateTo 语义）
        self.assertFalse(page.evaluate(f"__PT__.go('{root['page']}')"))
        errors.clear()  # 上一句是故意的错误用法，引擎会在控制台报错
        # 界面上的返回键回到来源
        page.locator("#ptScreen .pt-nav [data-pt-back]").click()
        c = self.cur(page)
        self.assertEqual((c["id"], c["depth"]), (root["page"], 0))
        self.assertTrue(page.locator("#ptScreen .pt-tabbar").is_visible())
        self.assertFalse(page.evaluate("__PT__.back()"), "栈底不能再返回")
        # 每个“回发起处”的流程：从二级页发起，完成后回到发起它的那个二级页
        for f in spec.get("flows", []):
            if f.get("done") != "origin" or pages[f["start"]]["type"] == "tab" or f["start"] == base:
                continue
            with self.subTest(flow=f["id"]):
                page.evaluate(f"__PT__.toTab('{root['id']}')")
                page.evaluate(f"__PT__.go('{base}')")
                page.evaluate(f"__PT__.go('{f['start']}')")
                self.assertEqual(self.cur(page)["depth"], 2)
                page.evaluate(f"__PT__.done('{f['id']}')")
                c = self.cur(page)
                self.assertEqual((c["id"], c["depth"]), (base, 1), f"流程 {f['id']} 完成后应回到发起处")
        self.assertEqual(errors, [])

    @per_example
    def test_hash_routes_jump_to_pages(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        pid = next(p["id"] for p in spec["pages"] if p["type"] == "sub")
        page.evaluate(f"location.hash = '#/{pid}'")
        page.wait_for_timeout(150)
        self.assertEqual(self.cur(page)["id"], pid)
        self.assertEqual(page.evaluate("location.hash"), f"#/{pid}")
        self.assertEqual(errors, [])

    # -- 弹层
    @per_example
    def test_sheet_is_a_native_modal_dialog_with_focus_trap(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        sheets = [p["id"] for p in spec["pages"] if p["type"] == "sheet"]
        # 示例里没有弹层页（如到店预约）时，用引擎的 K.confirm 测同一套对话框机制
        opener = (lambda: page.evaluate(f"__PT__.openSheet('{sheets[0]}')")) if sheets else (lambda: page.evaluate("__PT__.confirm({title: '确认', text: '测试用的确认框', ok: '好'})"))
        opener()
        page.wait_for_timeout(250)
        dlg = page.locator("#ptDlg")
        self.assertTrue(dlg.evaluate("d => d.open && d.matches(':modal')"), "要用 showModal()")
        self.assertEqual(dlg.get_attribute("role"), "dialog")
        self.assertEqual(dlg.get_attribute("aria-modal"), "true")
        self.assertTrue(page.locator("#ptDlgT").inner_text().strip())
        for _ in range(14):
            page.keyboard.press("Tab")
            self.assertTrue(page.evaluate("document.getElementById('ptDlg').contains(document.activeElement)"), "Tab 不能把焦点带出对话框")
        for _ in range(6):
            page.keyboard.press("Shift+Tab")
            self.assertTrue(page.evaluate("document.getElementById('ptDlg').contains(document.activeElement)"))
        self.assertLessEqual(page.locator("#ptDlg .pt-sheet").evaluate("e => e.getBoundingClientRect().height / document.querySelector('#ptPhone').getBoundingClientRect().height"), 0.81, "弹层高度不超过 80%")
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        c = self.cur(page)
        self.assertFalse(c["dlg"])
        self.assertIsNone(c["sheet"])
        opener()
        page.wait_for_timeout(200)
        page.locator("#ptDlg .pt-sheet .x").click()
        self.assertFalse(self.cur(page)["dlg"])
        opener()
        page.wait_for_timeout(200)
        page.locator("#ptDlg .pt-mask").click(position={"x": 80, "y": 100})
        self.assertFalse(self.cur(page)["dlg"])
        self.assertEqual(errors, [])

    # -- 表单校验（声明式 validate 步骤）
    def test_form_validation_blocks_and_explains(self) -> None:
        spec = self.specs.get("generic-mini")
        if spec is None:
            self.skipTest("没有通用示例")
        page, errors = self.open("generic-mini")
        page.evaluate("__PT__.jump('login')")
        page.wait_for_timeout(200)
        page.locator("#ptScreen .mpform004 [data-f=code] input").fill("")
        page.locator("#ptScreen .mpform004 .go").click()
        page.wait_for_timeout(150)
        self.assertIn("请输入验证码", page.locator("#ptToasts").inner_text())
        self.assertEqual(page.locator("#ptScreen .mpform004 [data-f=code] input").get_attribute("aria-invalid"), "true")
        self.assertEqual(self.cur(page)["id"], "login")
        page.locator("#ptScreen .mpform004 [data-f=phone] input").fill("123")
        page.locator("#ptScreen .mpform004 [data-f=code] input").fill("123456")
        page.locator("#ptScreen .mpform004 .go").click()
        page.wait_for_timeout(150)
        self.assertIn("11 位手机号", page.locator("#ptToasts").inner_text())
        self.assertEqual(self.cur(page)["id"], "login")
        page.locator("#ptScreen .mpform004 [data-f=phone] input").fill("138 0013 8000")
        page.locator("#ptScreen .mpform004 .go").click()
        page.wait_for_timeout(200)
        self.assertEqual(page.evaluate("__PT__.S.role"), "member")
        self.assertEqual(self.cur(page)["id"], "me", "登录成功后回到发起处")
        self.assertEqual(errors, [])

    # -- 配置面板
    @per_example
    def test_config_panel_changes_theme_header_icon_style_and_tile(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        page.locator("#ptLeft [data-lt=look]").click()
        tile_page = self.page_with(page, spec, "#ptScreen .tile")
        self.assertIsNotNone(tile_page, "示例里应该有带图标底的组件")
        # 主题色
        for theme in ("blue", "green"):
            page.locator(f'#ptLeft [data-g="theme"][data-v="{theme}"]').click()
            want = page.evaluate(f"__PT__.LIB.THEMES.find(t => t.id === '{theme}').p").lower()
            got = page.evaluate("getComputedStyle(document.getElementById('root')).getPropertyValue('--p').trim().toLowerCase()")
            self.assertEqual(got, want)
            self.assertEqual(page.locator('#ptLeft [data-g="theme"][aria-pressed="true"]').get_attribute("data-v"), theme)
        # 图标风格：线性时入口图标变成 svg，没有 img.ico
        page.locator('#ptLeft [data-g="iconStyle"][data-v="line"]').click()
        self.assertEqual(page.locator("#ptScreen img.ico").count(), 0)
        self.assertGreater(page.locator("#ptScreen svg.ico-line").count(), 0)
        page.locator('#ptLeft [data-g="iconStyle"][data-v="3d"]').click()
        self.assertGreater(page.locator("#ptScreen img.ico").count(), 0)
        # 图标底
        for shape, probe in (("ci", lambda r: "50%" in r), ("sq", lambda r: "18px" in r or "50%" not in r)):
            page.locator(f'#ptLeft [data-g="iconTile"][data-v="{shape}"]').click()
            radius = page.locator("#ptScreen .tile").first.evaluate("e => getComputedStyle(e).borderRadius")
            self.assertTrue(probe(radius), (shape, radius))
        page.locator('#ptLeft [data-g="iconTile"][data-v="no"]').click()
        self.assertEqual(page.locator("#ptScreen .tile").first.evaluate("e => getComputedStyle(e).backgroundColor"), "rgba(0, 0, 0, 0)")
        # 头部背景：渐变 / 浅色 / 图片
        hb = next((p["id"] for p in spec["pages"] if p.get("headerBg")), None)
        if hb:
            page.evaluate(f"__PT__.jump('{hb}')")
            for mode in ("light", "image", "gradient"):
                page.locator(f'#ptLeft [data-g="header"][data-v="{mode}"]').click()
                self.assertEqual(page.locator("#ptScreen .pt-hbg").get_attribute("data-bg"), mode)
            page.locator('#ptLeft [data-g="header"][data-v="image"]').click()
            bg_keys = page.evaluate("Object.keys(__PT__.LIB.ASSETS.bg)")
            self.assertTrue(bg_keys)
            self.assertTrue(page.evaluate("getComputedStyle(document.querySelector('#ptScreen .pt-hbg')).backgroundImage").startswith("url("))
            self.assertEqual(page.locator('#ptLeft [data-g="bgImage"]').count(), len(bg_keys))
        self.assertEqual(errors, [])

    # -- 场景
    @per_example
    def test_scene_switches_change_page_state_and_business_outcomes(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        page.locator("#ptLeft [data-lt=scene]").click()
        lab = {"loading": ".pt-sk", "empty": '[data-cid="MP-STATE-001"]', "fail-network": '[data-cid="MP-STATE-003"]', "fail-timeout": '[data-cid="MP-STATE-003"]',
               "fail-server": '[data-cid="MP-STATE-003"]', "fail-expired": '[data-cid="MP-STATE-003"]', "denied": '[data-cid="MP-STATE-001"]'}
        for view, selector in lab.items():
            page.locator(f'#ptLeft [data-scn="view:{view}"]').click()
            self.assertGreater(page.locator(f"#ptScreen .pt-body {selector}").count(), 0, view)
            self.assertEqual(page.locator("#ptScreen .pt-body .ixr, #ptScreen .pt-body .pt-custom").count(), 0, f"{view} 状态下不画正常内容")
        page.locator('#ptLeft [data-scn="view:disabled"]').click()
        self.assertGreater(page.locator("#ptScreen .pt-banner").count(), 0)
        page.locator('#ptLeft [data-scn="view:ok"]').click()
        self.assertGreater(page.locator("#ptScreen .pt-body .ixr, #ptScreen .pt-body .pt-custom").count(), 0)
        self.assertEqual(page.locator("#ptScreen .pt-body .pt-state, #ptScreen .pt-body .pt-sk").count(), 0)
        # 失败态的重试回到正常
        page.locator('#ptLeft [data-scn="view:fail-timeout"]').click()
        page.locator("#ptScreen [data-pt-act=retry]").click()
        self.assertEqual(page.evaluate("__PT__.S.view"), "ok")
        # 每个声明的场景都能切到每个选项
        for sc in spec.get("scenes", []):
            for o in sc["options"]:
                page.locator(f'#ptLeft [data-scn="{sc["id"]}:{o["v"]}"]').click()
                self.assertEqual(page.evaluate(f"__PT__.scene('{sc['id']}')"), o["v"])
        # 网络与角色
        page.locator('#ptLeft [data-net="offline"]').click()
        self.assertGreater(page.locator('#ptScreen [data-cid="MP-STATE-003"]').count(), 0, "断网时普通页显示失败态")
        page.locator('#ptLeft [data-net="online"]').click()
        if len(spec.get("roles", [])) > 1:
            guest = spec["roles"][1]["id"]
            restricted = next((p["id"] for p in spec["pages"] if p.get("roles") and p["type"] != "sheet"), None)
            page.locator(f'#ptLeft [data-role="{guest}"]').click()
            if restricted:
                page.evaluate(f"__PT__.jump('{restricted}')")
                self.assertGreater(page.locator("#ptScreen .pt-state h3").filter(has_text="暂无权限").count(), 0, "角色不在 roles 里时是无权限态")
            page.locator(f'#ptLeft [data-role="{spec["roles"][0]["id"]}"]').click()
        self.assertEqual(errors, [])

    def test_business_scene_decides_the_pay_result(self) -> None:
        spec = self.specs.get("generic-mini")
        if spec is None:
            self.skipTest("没有通用示例")
        page, errors = self.open("generic-mini")
        reasons = {"fail-limit": "超出银行单笔限额", "fail-balance": "银行卡余额不足", "fail-timeout": "支付超时"}
        for scene, text in reasons.items():
            page.evaluate(f"__PT__.setScene('pay', '{scene}')")
            page.evaluate("__PT__.jump('pay')")
            page.wait_for_timeout(250)
            page.locator("#ptDlg .ft .btn-p").click()
            page.wait_for_timeout(250)
            self.assertEqual(self.cur(page)["id"], "result-fail")
            self.assertIn(text, page.locator("#ptScreen .why").inner_text())
        page.evaluate("__PT__.setScene('pay', 'processing')")
        page.evaluate("__PT__.jump('pay')")
        page.wait_for_timeout(250)
        page.locator("#ptDlg .ft .btn-p").click()
        page.wait_for_timeout(250)
        self.assertEqual(self.cur(page)["id"], "result-wait")
        # 断网时支付被拦住并提示，订单仍待付款
        page.evaluate("__PT__.setScene('pay', 'ok'); __PT__.jump('pay'); __PT__.setNet('offline')")
        page.wait_for_timeout(200)
        self.assertEqual(errors, [])

    def test_generic_flow_browse_to_pay_and_back_to_origin(self) -> None:
        spec = self.specs.get("generic-mini")
        if spec is None:
            self.skipTest("没有通用示例")
        page, errors = self.open("generic-mini")
        s = "#ptScreen"
        page.locator(f"{s} .i1 > div").nth(0).click()
        self.assertEqual(self.cur(page)["id"], "list")
        page.locator(f"{s} .mplist003 .it").nth(0).click()
        self.assertEqual(self.cur(page)["id"], "detail")
        before = page.evaluate("__PT__.data.cart.count")
        page.locator(f"{s} .mpgoods010 [data-add]").click()
        self.assertEqual(page.evaluate("__PT__.data.cart.count"), before + 1)
        page.locator(f"{s} .mpgoods010 .btn-p").click()
        page.wait_for_timeout(250)
        self.assertEqual(self.cur(page)["sheet"], "spec")
        page.locator("#ptDlg [data-buy]").click()
        self.assertEqual(self.cur(page)["id"], "checkout")
        page.locator(f"{s} .mpord018 [data-submit]").click()
        page.wait_for_timeout(250)
        self.assertEqual(self.cur(page)["sheet"], "pay")
        page.locator("#ptDlg .ft .btn-p").click()
        page.wait_for_timeout(250)
        self.assertEqual(self.cur(page)["id"], "result")
        page.locator(f"{s} .ln2").first.click()
        c = self.cur(page)
        self.assertEqual((c["id"], c["depth"]), ("detail", 2), "继续逛逛回到发起结算的详情页（栈：列表、详情）")
        # 缺货时加购被拦，提示原因
        page.evaluate("__PT__.setScene('stock', 'out')")
        before = page.evaluate("__PT__.data.cart.count")
        page.locator(f"{s} .mpgoods010 [data-add]").click()
        self.assertEqual(page.evaluate("__PT__.data.cart.count"), before)
        self.assertIn("已售罄", page.locator("#ptToasts").inner_text())
        self.assertEqual(errors, [])

    # -- 逻辑面板
    @per_example
    def test_logic_panel_follows_the_page_and_renders_spec_data(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        for p in spec["pages"][:8]:
            page.evaluate(f"__PT__.jump('{p['id']}')")
            page.wait_for_timeout(120)
            self.assertTrue(page.locator("#ptRight .pt-title").inner_text().startswith(p["name"]), p["id"])
            lg = p["logic"]
            right = page.locator("#ptRight").inner_text()
            prim = lg["primary"]
            self.assertIn(prim.split("（")[0][:6], right)
            for r in lg["rules"][:1]:
                self.assertIn(r[:8], right)
        page.locator("#ptRight [data-rt=rules]").click()
        self.assertIn(spec["rules"][0]["title"], page.locator("#ptRight").inner_text())
        page.locator("#ptRight [data-rt=status]").click()
        self.assertIn(spec["statuses"][0]["name"], page.locator("#ptRight").inner_text())
        page.locator("#ptRight [data-rt=logic]").click()
        self.assertEqual(errors, [])

    # -- 减少动态
    @per_example
    def test_reduce_motion_switch_and_system_setting_both_work(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        self.assertEqual(page.evaluate("document.documentElement.dataset.reduce"), "0")
        page.locator("#ptLeft [data-lt=scene]").click()
        page.locator("#ptLeft [data-reduce]").click()
        self.assertEqual(page.evaluate("document.documentElement.dataset.reduce"), "1")
        page.locator('#ptLeft [data-scn="view:loading"]').click()
        dur = page.locator("#ptScreen .pt-sk i").first.evaluate("e => getComputedStyle(e).animationDuration")
        self.assertTrue(dur in ("1e-06s", "0.000001s", "0s") or float(dur.rstrip("s")) < 0.001, dur)
        page.locator("#ptLeft [data-reduce]").click()
        self.assertEqual(page.evaluate("document.documentElement.dataset.reduce"), "0")
        self.assertEqual(errors, [])
        page2, _ = self.open(name, reduced_motion="reduce")
        self.assertEqual(page2.evaluate("document.documentElement.dataset.reduce"), "1", "系统开了减少动态时初值也是开")

    # -- 重置演示数据
    @per_example
    def test_reset_restores_demo_data_stack_scene_and_role(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        sub = next(p["id"] for p in spec["pages"] if p["type"] == "sub" and not p.get("roles"))
        page.evaluate(f"__PT__.data.__probe = 1; __PT__.go('{sub}'); __PT__.setScene('view', 'empty')")
        if spec.get("roles"):
            page.evaluate(f"__PT__.setRole('{spec['roles'][-1]['id']}')")
        page.locator("#ptLeft [data-lt=scene]").click()
        page.locator("#ptLeft [data-reset]").click()
        self.assertIsNone(page.evaluate("__PT__.data.__probe ?? null"))
        c = self.cur(page)
        self.assertEqual((c["depth"], c["tab"]), (0, spec["tabbar"][0]["id"]))
        self.assertEqual(page.evaluate("__PT__.S.view"), "ok")
        if spec.get("roles"):
            self.assertEqual(page.evaluate("__PT__.S.role"), spec["roles"][0]["id"])
        self.assertEqual(errors, [])

    # -- 布局
    @per_example
    def test_phone_390_is_operable_without_horizontal_overflow(self, name: str, spec: dict) -> None:
        page, errors = self.open(name, 390, 844, has_touch=True, is_mobile=True)
        page.wait_for_timeout(200)
        ids = [p["id"] for p in spec["pages"]]
        for pid in ids[:: max(1, len(ids) // 8)]:
            page.evaluate(f"__PT__.jump('{pid}')")
            page.wait_for_timeout(120)
            self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390, f"{pid} 横向撑破")
            self.assertLessEqual(page.evaluate("document.body.scrollWidth"), 390)
        page.evaluate(f"__PT__.jump('{spec['tabbar'][0]['page']}')")
        box = page.locator("#ptPhone").bounding_box()
        self.assertAlmostEqual(box["width"], 390, delta=1)
        self.assertAlmostEqual(box["x"], 0, delta=1)
        for b in page.locator("#ptScreen .pt-tabbar button").all():
            bb = b.bounding_box()
            self.assertGreaterEqual(bb["height"], 44)
            self.assertGreaterEqual(bb["width"], 44)
        page.locator(f"#ptScreen .pt-tabbar [data-pt-tab='{spec['tabbar'][-1]['id']}']").tap()
        self.assertEqual(self.cur(page)["tab"], spec["tabbar"][-1]["id"])
        sid = next((p["id"] for p in spec["pages"] if p["type"] == "sheet"), None)
        page.evaluate(f"__PT__.jump('{sid}')" if sid else "__PT__.confirm({title: '确认', text: '测试', ok: '好'})")
        page.wait_for_timeout(250)
        sheet = page.locator("#ptDlg .pt-sheet").bounding_box()
        self.assertLessEqual(sheet["x"] + sheet["width"], 391)
        self.assertGreaterEqual(sheet["x"], -1)
        page.keyboard.press("Escape")
        # 面板排在手机下方
        tops = page.evaluate("({left: document.querySelector('#ptLeft').getBoundingClientRect().top + scrollY, phone: document.querySelector('#ptPhone').getBoundingClientRect().bottom + scrollY})")
        self.assertGreater(tops["left"], tops["phone"] - 2, "面板排在手机下面（用页面坐标比，滚动不影响）")
        for panel in ("#ptLeft", "#ptRight"):
            self.assertGreaterEqual(page.locator(panel).bounding_box()["width"], 340, "窄屏下面板占满宽度")
        self.assertEqual(errors, [])

    @per_example
    def test_desktop_1500_has_three_columns_with_dense_first_screen(self, name: str, spec: dict) -> None:
        page, errors = self.open(name, 1500, 900)
        left, stage, right = (page.locator(s).bounding_box() for s in ("#ptLeft", "#ptStage", "#ptRight"))
        self.assertLess(left["x"] + left["width"], stage["x"] + 1)
        self.assertLess(stage["x"] + stage["width"], right["x"] + 1)
        self.assertLess(abs(left["y"] - right["y"]), 4)
        phone = page.locator("#ptPhone").bounding_box()
        self.assertGreaterEqual(phone["width"], 340)
        self.assertLessEqual(phone["y"] + phone["height"], 900)
        self.assertGreater(phone["x"], left["x"] + left["width"])
        # 外壳文字不小于 14px（说明 12px 除外）
        small = page.evaluate("""() => [...document.querySelectorAll('#ptLeft button, #ptLeft h3, #ptRight button, #ptRight h3, #ptRight .pt-kv, #ptRight .pt-list li, #ptLeft .pt-dir span')]
            .filter(e => e.offsetParent && parseFloat(getComputedStyle(e).fontSize) < 14).map(e => e.className + ':' + getComputedStyle(e).fontSize)""")
        self.assertEqual(small, [])
        self.assertEqual(errors, [])

    # -- 深浅外观
    @per_example
    def test_every_page_opens_in_light_and_dark_appearance(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        for mode in ("light", "dark"):
            page.evaluate(f"__PT__.setAppearance('{mode}')")
            self.assertEqual(page.evaluate("document.documentElement.dataset.theme"), mode)
            for p in spec["pages"]:
                page.evaluate(f"__PT__.jump('{p['id']}')")
                opened = page.evaluate("__PT__.S.sheet && __PT__.S.sheet.id") if p["type"] == "sheet" else self.cur(page)["id"]
                self.assertEqual(opened, p["id"])
                self.assertEqual(page.locator("#ptScreen .pt-page").count(), 1, p["id"])
        page.evaluate("__PT__.closeSheet()")
        self.assertEqual(errors, [], "深浅两种外观下每一页都应能打开且无控制台错误")
        # 跟随系统
        page.evaluate("__PT__.setAppearance('auto')")
        page.emulate_media(color_scheme="dark")
        page.wait_for_timeout(100)
        self.assertEqual(page.evaluate("document.documentElement.dataset.theme"), "dark")
        page.emulate_media(color_scheme="light")
        page.wait_for_timeout(100)
        self.assertEqual(page.evaluate("document.documentElement.dataset.theme"), "light")

    @per_example
    def test_shell_controls_are_marked_data_shell_and_product_controls_carry_cid(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        bad = page.evaluate("""() => [...document.querySelectorAll('#ptLeft button, #ptRight button, .pt-top')].filter(e => !e.closest('[data-shell]')).length""")
        self.assertEqual(bad, 0)
        stray = page.evaluate("""() => [...document.querySelectorAll('#ptScreen button, #ptScreen input, #ptScreen [role=button]')]
            .filter(e => !e.closest('[data-cid]') && !e.closest('[data-shell]')).map(e => e.outerHTML.slice(0, 80))""")
        self.assertEqual(stray, [], "产品界面里的控件必须落在带 data-cid 的组件里")
        self.assertEqual(errors, [])

    def test_booking_flow_validates_the_phone_and_returns_to_origin(self) -> None:
        spec = self.specs.get("booking-mini")
        if spec is None:
            self.skipTest("没有预约示例")
        page, errors = self.open("booking-mini")
        s = "#ptScreen"
        page.locator(f"{s} .mpsvc005 .pk").nth(1).click()
        self.assertEqual((self.cur(page)["id"], self.cur(page)["a"]), ("slot", "standard"))
        page.locator(f"{s} .pt-foot .bt.lg").click()
        self.assertEqual(self.cur(page)["id"], "confirm")
        page.locator(f"{s} .f3 input.in").first.fill("123")
        page.locator(f"{s} .pt-foot .bt.lg").click()
        page.wait_for_timeout(150)
        self.assertIn("11 位手机号", page.locator("#ptToasts").inner_text())
        self.assertEqual(self.cur(page)["id"], "confirm")
        page.evaluate("__PT__.setScene('booking', 'fail-full')")
        page.locator(f"{s} .f3 input.in").first.fill("138 0013 8000")
        page.locator(f"{s} .pt-foot .bt.lg").click()
        page.wait_for_timeout(200)
        self.assertEqual(self.cur(page)["id"], "result-fail")
        self.assertIn("约满", page.locator(f"{s} .why").inner_text())
        page.locator(f"{s} [data-p=no] .rp").click()
        self.assertEqual(self.cur(page)["id"], "slot", "重新选择时间回到选人员与时间")
        page.evaluate("__PT__.setScene('booking', 'ok')")
        page.locator(f"{s} .pt-foot .bt.lg").click()
        page.locator(f"{s} .f3 input.in").first.fill("138 0013 8000")
        page.locator(f"{s} .pt-foot .bt.lg").click()
        page.wait_for_timeout(200)
        self.assertEqual(self.cur(page)["id"], "result")
        page.locator(f"{s} [data-p=ok] .ln2").click()
        c = self.cur(page)
        self.assertEqual((c["id"], c["depth"]), ("home", 0), "预约完成回到发起处（首页）")
        self.assertEqual(errors, [])

    def test_page_options_title_arg_no_back_fixed_scroll_and_directory_with_args(self) -> None:
        spec = copy.deepcopy(load(EXAMPLES["booking-mini"]))
        page_of(spec, "slot")["title"] = "预约：{{arg}}"
        page_of(spec, "result")["noBack"] = True
        page_of(spec, "queue")["scroll"] = False
        spec["directory"] = [{"group": "变体", "pages": ["home", "slot:basic", "slot:premium", "result", "queue"]}]
        out_dir = Path(self.tmp.name) / "options"
        out_dir.mkdir(exist_ok=True)
        (out_dir / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(bp.build(out_dir / "spec.json", out_dir / "x.html"), 0)
        context = self.browser.new_context(viewport={"width": 1500, "height": 900})
        self.addCleanup(context.close)
        page = context.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto((out_dir / "x.html").as_uri())
        page.wait_for_function("window.__PT__ && __PT__.cur().id")
        self.assertEqual(page.locator("#ptLeft .pt-dir button").count(), 5)
        page.locator("#ptLeft [data-jump='slot:premium']").click()
        self.assertEqual(self.cur(page)["a"], "premium")
        self.assertEqual(page.locator("#ptScreen .pt-nav h2").inner_text(), "预约：premium")
        self.assertEqual(page.locator("#ptLeft [data-jump='slot:premium']").get_attribute("aria-current"), "page")
        page.locator("#ptLeft [data-jump='result']").click()
        self.assertEqual(page.locator("#ptScreen .pt-nav .rb").count(), 0, "noBack 的页面没有返回键")
        page.locator("#ptLeft [data-jump='queue']").click()
        self.assertEqual(page.locator("#ptScreen .pt-scroll").evaluate("e => getComputedStyle(e).overflowY"), "hidden")
        self.assertEqual(errors, [])

    # -- 深色：真令牌，三种方式
    TOKENS = {"light": {"--card": "#ffffff", "--bg": "#f5f6f8", "--ink": "#1f2329"}, "dark": {"--card": "#191d24", "--bg": "#0d1116", "--ink": "#e7eaee"}}

    def token(self, page, name: str) -> str:
        return page.evaluate(f"getComputedStyle(document.documentElement).getPropertyValue('{name}').trim().toLowerCase()")

    @per_example
    def test_dark_appearance_uses_library_tokens_in_all_three_ways(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        self.assertTrue(page.evaluate("typeof __PT__.LIB.setAppearance === 'function' && typeof __PT__.LIB.isDark === 'function' && __PT__.LIB.APPEARANCES.length === 3"))
        # 1) 显式深色 / 显式浅色：产品区与外壳的令牌都换，没有滤镜
        for mode in ("dark", "light"):
            page.evaluate(f"__PT__.setAppearance('{mode}')")
            for tok, want in self.TOKENS[mode].items():
                self.assertEqual(self.token(page, tok), want, f"{mode} {tok}")
            self.assertEqual(page.evaluate("document.documentElement.classList.contains('dark')"), mode == "dark")
            self.assertEqual(page.evaluate("getComputedStyle(document.getElementById('ptScreen')).filter"), "none")
            self.assertEqual(page.evaluate("__PT__.LIB.isDark()"), mode == "dark")
            nav = page.evaluate("getComputedStyle(document.querySelector('#ptScreen .pt-tabbar, #ptScreen .pt-nav')).backgroundColor")
            self.assertEqual(nav, "rgb(25, 29, 36)" if mode == "dark" else "rgb(255, 255, 255)")
        # 2) 显式浅色压过系统深色；显式深色压过系统浅色
        page.emulate_media(color_scheme="dark")
        page.evaluate("__PT__.setAppearance('light')")
        self.assertEqual(self.token(page, "--card"), "#ffffff")
        page.emulate_media(color_scheme="light")
        page.evaluate("__PT__.setAppearance('dark')")
        self.assertEqual(self.token(page, "--card"), "#191d24")
        # 3) 跟随系统：系统深色用深色令牌，系统浅色用浅色令牌，运行中切换系统外观也跟着变
        page.evaluate("__PT__.setAppearance('auto')")
        for scheme, mode in (("dark", "dark"), ("light", "light"), ("dark", "dark")):
            page.emulate_media(color_scheme=scheme)
            page.wait_for_timeout(80)
            self.assertEqual(self.token(page, "--card"), self.TOKENS[mode]["--card"], f"跟随系统（{scheme}）")
            self.assertEqual(page.evaluate("document.documentElement.dataset.theme"), mode)
        # 弹层（body 下的 dialog）也拿到主题色与深色令牌
        sheet = next((p["id"] for p in spec["pages"] if p["type"] == "sheet"), None)
        if sheet:
            page.evaluate(f"__PT__.jump('{sheet}')")
            page.wait_for_timeout(250)
            self.assertEqual(page.evaluate("getComputedStyle(document.querySelector('#ptDlg .pt-sheet')).backgroundColor"), "rgb(25, 29, 36)")
            theme = page.evaluate("__PT__.cfg.theme")
            self.assertEqual(page.evaluate("document.getElementById('ptDlg').getAttribute('data-lt')"), theme)
        # 打开页面时系统本来就是深色：不用点任何东西，一开始就是深色
        dark_page, dark_errors = self.open(name, color_scheme="dark")
        self.assertEqual(self.token(dark_page, "--card"), "#191d24")
        self.assertEqual(errors + dark_errors, [])

    CONTRAST_JS = r"""(scope) => {
      const parse = (c) => { let m = c.match(/color\(srgb ([^)]+)\)/); if (m) { const p = m[1].split(/[ \/]+/).filter(Boolean).map(Number); return { r: p[0] * 255, g: p[1] * 255, b: p[2] * 255, a: p.length > 3 ? p[3] : 1 } }
        m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const q = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: q[0], g: q[1], b: q[2], a: q.length > 3 ? q[3] : 1 } }
      const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4 }
      const lum = (c) => 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b)
      const over = (t, b) => ({ r: t.r * t.a + b.r * (1 - t.a), g: t.g * t.a + b.g * (1 - t.a), b: t.b * t.a + b.b * (1 - t.a), a: 1 })
      const root = document.querySelector(scope); if (!root) return { total: 0, bad: [] }
      let total = 0; const bad = []; const seen = new Set()
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        const el = n.parentElement; if (!n.nodeValue.trim() || seen.has(el) || el.closest('[data-shell]')) continue; seen.add(el)
        const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue
        const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue
        let op = 1, skip = false, layers = []
        for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
          const c = getComputedStyle(e); op *= parseFloat(c.opacity)
          if (e.hasAttribute('hidden') || c.display === 'none') { skip = true; break }
          if (c.backgroundImage !== 'none') { skip = true; break }   // 图片或渐变底：对比度由图片决定，跳过
          const bg = parse(c.backgroundColor); if (bg && bg.a > 0) { layers.push(bg); if (bg.a >= 0.99) break }
        }
        if (skip || op < 0.99 || el.closest('[disabled],[aria-disabled=true],.pt-dis,.dis,.off,.full')) continue
        let base = { r: 255, g: 255, b: 255, a: 1 }
        for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base)
        const fg = parse(cs.color); if (!fg) continue
        const f = over(fg, base), L1 = lum(f), L2 = lum(base), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05)
        const size = parseFloat(cs.fontSize), need = size >= 24 || (size >= 18.66 && parseInt(cs.fontWeight) >= 600) ? 3 : 4.5
        total++; if (ratio < need) bad.push({ text: n.nodeValue.trim().slice(0, 16), ratio: Math.round(ratio * 100) / 100 })
      }
      return { total, bad } }"""

    @per_example
    def test_dark_text_contrast_sampled_and_light_unchanged(self, name: str, spec: dict) -> None:
        """抽样：每个示例的前几页（不含用头部背景的页面，那里的文字压在渐变或图片上）加一个弹层，量产品区每段文字对真实底色的对比度。"""
        page, errors = self.open(name)
        ids = [p["id"] for p in spec["pages"] if p["type"] != "sheet" and not p.get("headerBg")][:7]
        sheet = next((p["id"] for p in spec["pages"] if p["type"] == "sheet"), None)
        stats = {}
        for mode in ("light", "dark"):
            page.evaluate(f"__PT__.setAppearance('{mode}')")
            total, bad = 0, []
            for pid in ids + ([sheet] if sheet else []):
                page.evaluate(f"__PT__.jump('{pid}')")
                page.wait_for_timeout(150)
                for scope in ("#ptScreen", "#ptDlg .pt-sheet"):
                    r = page.evaluate(self.CONTRAST_JS, scope)
                    total += r["total"]
                    bad += [(pid, b["text"], b["ratio"]) for b in r["bad"]]
            stats[mode] = (total, bad)
            self.assertGreater(total, 60, f"{mode} 抽到的文字太少")
        light_total, light_bad = stats["light"]
        dark_total, dark_bad = stats["dark"]
        self.assertLessEqual(len(dark_bad) / dark_total, 0.02, f"深色下低于 4.5:1 的文字不超过 2%：{dark_bad[:6]}")
        self.assertGreaterEqual(min([r for _, _, r in dark_bad] + [9]), 3.5, f"深色下最差的也要有 3.5:1：{sorted(dark_bad, key=lambda x: x[2])[:4]}")
        self.assertLessEqual(len(light_bad) / light_total, 0.10, f"浅色不变：库里浅色原本就略低于 4.5 的少数文字（4.2–4.5）不超过 10%：{light_bad[:6]}")
        self.assertGreaterEqual(min([r for _, _, r in light_bad] + [9]), 4.0, f"浅色最差也要有 4:1：{sorted(light_bad, key=lambda x: x[2])[:4]}")
        self.assertEqual(errors, [])

    # -- 模块显示
    @per_example
    def test_module_display_switches_hide_and_restore_modules(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        pid = next(p["id"] for p in spec["pages"] if p["type"] == "tab" and (p.get("blocks") or p.get("custom")))
        page.evaluate(f"__PT__.jump('{pid}')")
        page.locator("#ptLeft [data-lt=scene]").click()
        switches = page.locator("#ptLeft [data-mod]")
        n = switches.count()
        self.assertGreaterEqual(n, 1, "场景面板里要有“模块显示”开关")
        for i in range(n):
            self.assertEqual(switches.nth(i).get_attribute("role"), "switch")
            self.assertEqual(switches.nth(i).get_attribute("aria-checked"), "true")
        key = switches.first.get_attribute("data-mod")
        before = page.evaluate("document.querySelector('#ptScreen .pt-body').innerHTML.length")
        switches.first.click()
        self.assertEqual(page.locator(f'#ptLeft [data-mod="{key}"]').get_attribute("aria-checked"), "false")
        self.assertLess(page.evaluate("document.querySelector('#ptScreen .pt-body').innerHTML.length"), before, "关掉模块后正文变短")
        # 换页再回来，状态还在；开回去恢复；重置演示数据全部恢复
        other = next(p["id"] for p in spec["pages"] if p["type"] == "sub" and not p.get("roles"))
        page.evaluate(f"__PT__.jump('{other}'); __PT__.jump('{pid}')")
        self.assertTrue(page.evaluate(f"__PT__.moduleHidden('{pid}', '{key}')"))
        page.locator("#ptLeft [data-lt=scene]").click()
        page.locator(f'#ptLeft [data-mod="{key}"]').click()
        self.assertEqual(page.evaluate("document.querySelector('#ptScreen .pt-body').innerHTML.length"), before)
        page.locator(f'#ptLeft [data-mod="{key}"]').click()
        page.locator("#ptLeft [data-reset]").click()
        self.assertFalse(page.evaluate(f"__PT__.moduleHidden('{pid}', '{key}')"))
        self.assertEqual(errors, [])

    def test_module_display_names_use_the_spec_ids_and_names(self) -> None:
        if "generic-mini" not in self.built:
            self.skipTest("没有通用示例")
        page, errors = self.open("generic-mini")
        page.locator("#ptLeft [data-lt=scene]").click()
        labels = page.locator("#ptLeft .pt-mods .pt-switch span").all_inner_texts()
        self.assertIn("正文 · 金刚区", labels)
        page.locator("#ptLeft .pt-mods .pt-switch", has_text="金刚区").click()
        self.assertEqual(page.locator("#ptScreen .i1").count(), 0, "关掉金刚区模块")
        self.assertGreater(page.locator("#ptScreen .m3").count(), 0, "其余模块还在")
        self.assertEqual(errors, [])

    def test_dialog_has_an_exit_animation_and_closes_at_once_with_reduced_motion(self) -> None:
        if "booking-mini" not in self.built:
            self.skipTest("没有预约示例")
        page, errors = self.open("booking-mini")
        page.evaluate("__PT__.confirm({title: '确认', text: '测试', ok: '好'})")
        page.wait_for_timeout(300)
        page.keyboard.press("Escape")
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').classList.contains('closing')"), "关闭前有 150ms 的退出动画")
        page.wait_for_function("!document.getElementById('ptDlg').open", timeout=1500)
        page.evaluate("__PT__.setReduce(true); __PT__.confirm({title: '确认', text: '测试', ok: '好'})")
        page.wait_for_timeout(100)
        page.keyboard.press("Escape")
        page.wait_for_timeout(20)
        self.assertFalse(page.evaluate("document.getElementById('ptDlg').open"), "减少动态时直接关闭")
        self.assertEqual(errors, [])

    # -- R3 切标签的页面栈语义
    @per_example
    def test_r3_to_tab_clears_sub_pages_by_default_and_keeps_them_when_asked(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        tabs = [t["id"] for t in spec["tabbar"]]
        sub = next(p["id"] for p in spec["pages"] if p["type"] == "sub" and not p.get("roles"))
        a, b = tabs[0], tabs[1]
        page.evaluate(f"__PT__.toTab('{a}'); __PT__.go('{sub}')")
        # 默认（微信 switchTab）：弹掉所有二级页
        page.evaluate(f"__PT__.toTab('{b}'); __PT__.toTab('{a}')")
        self.assertEqual(self.cur(page)["depth"], 0)
        # keep：各标签保留自己的栈
        page.evaluate(f"__PT__.go('{sub}'); __PT__.toTab('{b}', {{keep: true}})")
        self.assertEqual((self.cur(page)["tab"], self.cur(page)["depth"]), (b, 0))
        page.evaluate(f"__PT__.toTab('{a}', {{keep: true}})")
        c = self.cur(page)
        self.assertEqual((c["tab"], c["id"], c["depth"]), (a, sub, 1), "keep 时回到标签 A 还停在二级页")
        # 再点当前标签（保留模式）：回到它的根页
        page.evaluate(f"__PT__.toTab('{a}', {{keep: true}})")
        self.assertEqual(self.cur(page)["depth"], 0)
        # kind 声明 keepTabStacks 后，不传参数也保留
        page.evaluate(f"__PT__.kindDef.keepTabStacks = true; __PT__.go('{sub}'); __PT__.toTab('{b}'); __PT__.toTab('{a}')")
        self.assertEqual(self.cur(page)["depth"], 1)
        self.assertEqual(errors, [])

    # -- R4 / R8 / R12 弹层
    def test_r4_sheet_close_controls_nested_confirm_and_fields(self) -> None:
        page, errors = self.open("booking-mini")
        # maskClose:false 与 onBeforeClose
        page.evaluate("""() => { window.__log = []; __PT__.sheet.open({title: '编辑', layout: 'center', cid: 'MP-FB-002', maskClose: false, body: '<p>表单</p>', foot: '',
            onBeforeClose: (why) => { window.__log.push(why); return window.__allow === true } }) }""")
        page.wait_for_timeout(250)
        self.assertEqual(page.evaluate("document.getElementById('ptDlg').getAttribute('data-cid')"), "MP-FB-002", "dialog 元素自己带 data-cid")
        self.assertEqual(page.locator("#ptDlg .pt-mask[data-pt-close]").count(), 0, "maskClose:false 的遮罩不带 data-pt-close")
        page.locator("#ptDlg .pt-mask").click(position={"x": 80, "y": 100})
        page.mouse.click(5, 5)  # 对话框外
        page.keyboard.press("Escape")
        page.locator("#ptDlg .pt-sheet .x").click()
        page.wait_for_timeout(250)
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').open"), "onBeforeClose 返回 false 时不关闭")
        self.assertEqual(page.evaluate("window.__log"), ["esc", "click"], "遮罩与面板外不触发关闭请求，Esc 与 × 会")
        page.evaluate("window.__allow = true")
        page.keyboard.press("Escape")
        page.wait_for_function("!document.getElementById('ptDlg').open", timeout=1500)
        # 嵌套确认：先开弹层，再叠确认；Esc 只关最上面一层
        page.evaluate("__PT__.sheet.open({title: '详情', layout: 'center', cid: 'MP-FB-002', body: '<button type=button id=inner>内部</button>', foot: ''})")
        page.wait_for_timeout(250)
        page.evaluate("window.__ok = []; __PT__.confirm({stack: true, title: '确认丢弃', text: '确定吗', ok: '丢弃', danger: true, onOk: (v) => window.__ok.push(v || 'ok')})")
        page.wait_for_timeout(250)
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').open && document.getElementById('ptDlg2').open"), "两层 dialog 同时打开")
        self.assertEqual(page.evaluate("document.getElementById('ptDlg2').getAttribute('data-cid')"), "MP-FB-002")
        for _ in range(8):
            page.keyboard.press("Tab")
            self.assertTrue(page.evaluate("document.getElementById('ptDlg2').contains(document.activeElement)"), "焦点陷阱在最上面一层")
        page.keyboard.press("Escape")
        page.wait_for_function("!document.getElementById('ptDlg2').open", timeout=1500)
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').open"), "Esc 只关最上面的确认框")
        self.assertEqual(page.evaluate("window.__ok"), [])
        page.evaluate("__PT__.confirm({stack: true, title: '确认丢弃', text: '确定吗', ok: '丢弃', onOk: (v) => window.__ok.push('ok')})")
        page.wait_for_timeout(250)
        page.locator("#ptDlg2 [data-confirm-ok]").click()
        page.wait_for_function("!document.getElementById('ptDlg2').open", timeout=1500)
        self.assertEqual(page.evaluate("window.__ok"), ["ok"])
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').open"), "确认后下面那层还在")
        page.keyboard.press("Escape")
        page.wait_for_function("!document.getElementById('ptDlg').open", timeout=1500)
        # 不写 stack：已有弹层时确认框替换它（旧行为，后台模板依赖它）
        page.evaluate("__PT__.sheet.open({title: '详情', layout: 'center', cid: 'MP-FB-002', body: '<p>详情</p>', foot: ''})")
        page.wait_for_timeout(250)
        page.evaluate("__PT__.confirm({title: '确认', text: '替换', ok: '好'})")
        page.wait_for_timeout(250)
        self.assertEqual(page.locator("#ptDlg .pt-confirm").count(), 1)
        self.assertEqual(page.evaluate("!!document.getElementById('ptDlg2') && document.getElementById('ptDlg2').open"), False)
        page.keyboard.press("Escape")
        page.wait_for_function("!document.getElementById('ptDlg').open", timeout=1500)
        # K.confirm 带字段：必填与格式不通过不关闭，错误写在字段下面；通过后回调带值
        page.evaluate("""window.__vals = null; __PT__.confirm({title: '改价', text: '改后立即生效', ok: '确认', fields: [
            {name: 'reason', label: '原因', type: 'textarea', required: true, msg: '请填写修改原因'},
            {name: 'phone', label: '手机号', type: 'text', required: true, pattern: '^1\\\\d{10}$', msg: '手机号要 11 位'}], onOk: (v) => { window.__vals = v } })""")
        page.wait_for_timeout(250)
        page.locator("#ptDlg [data-confirm-ok]").click()
        self.assertTrue(page.evaluate("document.getElementById('ptDlg').open"), "必填没填不关闭")
        self.assertEqual(page.locator("#ptDlg .pt-ferr").first.inner_text(), "请填写修改原因")
        self.assertEqual(page.locator("#ptDlg [name=reason]").get_attribute("aria-invalid"), "true")
        page.locator("#ptDlg [name=reason]").fill("定价错误")
        page.locator("#ptDlg [name=phone]").fill("123")
        page.locator("#ptDlg [data-confirm-ok]").click()
        self.assertEqual(page.locator("#ptDlg .pt-ferr").nth(1).inner_text(), "手机号要 11 位")
        page.locator("#ptDlg [name=phone]").fill("10000000000")
        page.locator("#ptDlg [data-confirm-ok]").click()
        page.wait_for_function("!document.getElementById('ptDlg').open", timeout=1500)
        self.assertEqual(page.evaluate("window.__vals"), {"reason": "定价错误", "phone": "10000000000"})
        # 页面弹层的 maskClose 来自规格字段
        self.assertEqual(errors, [])

    # -- R5 / R10 外壳
    @per_example
    def test_r5_r10_theme_reaches_the_dialog_and_shell_contrast_holds(self, name: str, spec: dict) -> None:
        page, errors = self.open(name)
        page.locator("#ptLeft [data-lt=look]").click()
        page.locator('#ptLeft [data-g="theme"][data-v="blue"]').click()
        page.evaluate("__PT__.confirm({title: '确认', text: '测试', ok: '好'})")
        page.wait_for_timeout(250)
        self.assertEqual(page.evaluate("document.getElementById('ptDlg').getAttribute('data-lt')"), "blue", "换主题色时弹层也跟着换")
        self.assertEqual(page.evaluate("getComputedStyle(document.querySelector('#ptDlg .pt-confirm-row .ok')).backgroundColor"), "rgb(85, 119, 164)", "弹层里的主按钮用蓝色主题的 --p")
        page.keyboard.press("Escape")
        page.wait_for_function("!document.getElementById('ptDlg').open", timeout=1500)
        js = """() => { const q = (s) => document.querySelector(s); const lin = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4 }
          const rgb = (c) => c.match(/[\\d.]+/g).slice(0, 3).map(Number); const L = (c) => { const [r, g, b] = rgb(c); return .2126 * lin(r) + .7152 * lin(g) + .0722 * lin(b) }
          const ratio = (a, b) => { const x = L(a), y = L(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05) }
          const bg = (e) => { for (; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; if (c !== 'rgba(0, 0, 0, 0)') return c } return 'rgb(255,255,255)' }
          const out = {}
          const ver = q('.pt-top .ver'); out.ver = ver && ver.textContent.trim() ? ratio(getComputedStyle(ver).color, bg(ver)) : 9
          const cur = q('#ptLeft .pt-dir button[aria-current] em'); out.cur = cur ? ratio(getComputedStyle(cur).color, bg(cur)) : 9
          const note = q('#ptLeft .pt-note, #ptRight .pt-note'); out.note = note ? ratio(getComputedStyle(note).color, bg(note)) : 9
          return out }"""
        for mode in ("light", "dark"):
            page.evaluate(f"__PT__.setAppearance('{mode}')")
            page.locator("#ptLeft [data-lt=pages]").click()
            r = page.evaluate(js)
            for k, v in r.items():
                self.assertGreaterEqual(v, 4.5, f"{mode} 外壳 {k} 的对比度 {v:.2f}")
        self.assertEqual(errors, [])

    # -- R6 三栏宽度与折叠
    def test_r6_panels_fold_and_columns_follow_the_width_variables(self) -> None:
        page, errors = self.open("generic-mini")
        stage = lambda: page.locator("#ptStage").bounding_box()["width"]
        base = stage()
        page.locator("[data-fold=left]").click()
        self.assertEqual(page.locator("[data-fold=left]").get_attribute("aria-pressed"), "true")
        self.assertGreater(stage(), base + 250, "折叠左栏后舞台变宽")
        page.locator("[data-fold=right]").click()
        self.assertGreater(stage(), base + 550, "两栏都折叠就是只看舞台")
        page.locator("[data-fold=left]").click()
        page.locator("[data-fold=right]").click()
        self.assertAlmostEqual(stage(), base, delta=2)
        page.evaluate("document.querySelector('.pt-app').style.setProperty('--sh-left', '264px'); document.querySelector('.pt-app').style.setProperty('--sh-right', '320px')")
        cols = page.evaluate("getComputedStyle(document.querySelector('.pt-layout')).gridTemplateColumns").split()
        self.assertEqual((cols[0], cols[2]), ("264px", "320px"), "栏宽读 --sh-left / --sh-right")
        self.assertEqual(errors, [])

    # -- R9 局部重画
    def test_r9_render_part_keeps_focus_and_caret(self) -> None:
        page, errors = self.open("generic-mini")
        page.evaluate("""() => {
          const body = document.querySelector('#ptScreen .pt-body'); body.insertAdjacentHTML('afterbegin', '<div id="pp"><input id="q" data-fk="q" value=""></div>')
          __PT__.kindDef.renderPart = (part) => { const pp = document.getElementById('pp'); const v = document.getElementById('q').value; pp.innerHTML = `<input id="q" data-fk="q" value="${v}"><span id="n">${v.length}</span>`; return pp }
        }""")
        page.locator("#q").click()
        page.keyboard.type("abcdef")
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowLeft")
        page.evaluate("__PT__.render({part: 'list'})")
        self.assertEqual(page.evaluate("document.activeElement.id"), "q", "局部重画后焦点还在输入框")
        self.assertEqual(page.evaluate("document.activeElement.selectionStart"), 4, "光标位置也恢复")
        self.assertEqual(page.locator("#n").inner_text(), "6")
        # 批处理里的局部渲染合并成一次
        page.evaluate("window.__n = 0; const f = __PT__.kindDef.renderPart; __PT__.kindDef.renderPart = (p) => { window.__n++; return f(p) }; __PT__.batch(() => { __PT__.render({part: 'a'}); __PT__.render({part: 'a'}); __PT__.render({part: 'b'}) })")
        self.assertEqual(page.evaluate("window.__n"), 2, "同名局部只画一次")
        self.assertEqual(errors, [])

    # -- R11 目录自动分组
    def test_r11_directory_groups_a_tab_page_without_tab_under_its_own_tab(self) -> None:
        spec = copy.deepcopy(load(EXAMPLES["booking-mini"]))
        spec.pop("directory", None)
        page_of(spec, "bookings").pop("tab", None)
        out_dir = Path(self.tmp.name) / "r11"
        out_dir.mkdir(exist_ok=True)
        (out_dir / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(bp.build(out_dir / "spec.json", out_dir / "x.html"), 0)
        context = self.browser.new_context(viewport={"width": 1500, "height": 900})
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto((out_dir / "x.html").as_uri())
        page.wait_for_function("window.__PT__ && __PT__.cur().id")
        groups = page.locator("#ptLeft h3").all_inner_texts()
        self.assertNotIn("其他", groups)
        self.assertIn("预约", groups, "没写 tab 的一级页归到它自己的标签名下")

    # -- 只有一个 h1
    VISIBLE_H1 = "() => [...document.querySelectorAll('h1')].filter((e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' }).length"

    @per_example
    def test_exactly_one_visible_h1_in_every_state(self, name: str, spec: dict) -> None:
        """每个标签页、二级页、弹层、各种页面状态与确认框打开时，页面里可见的 h1 都只有外壳里的那一个。"""
        page, errors = self.open(name)
        seen = []
        ids = [p["id"] for p in spec["pages"]]
        for pid in ids:
            page.evaluate(f"__PT__.jump('{pid}')")
            page.wait_for_timeout(100)
            seen.append((pid, page.evaluate(self.VISIBLE_H1)))
        for pid, n in seen:
            self.assertEqual(n, 1, f"页面 {pid}（含弹层）可见的 h1 个数")
        tab = spec["tabbar"][0]["page"]
        page.evaluate(f"__PT__.jump('{tab}')")
        for view in ("loading", "empty", "fail-network", "denied", "disabled", "ok"):
            page.evaluate(f"__PT__.setScene('view', '{view}')")
            self.assertEqual(page.evaluate(self.VISIBLE_H1), 1, f"状态 {view}")
        page.evaluate("__PT__.confirm({title: '确认', text: '测试', ok: '好'})")
        page.wait_for_timeout(250)
        self.assertEqual(page.evaluate(self.VISIBLE_H1), 1, "确认框打开时")
        self.assertEqual(page.evaluate("document.querySelectorAll('h1').length"), 1, "整个文档里也只有一个 h1（不管可不可见）")
        self.assertEqual(errors, [])

    def test_h1_in_content_is_demoted_at_build_time_and_at_run_time_with_the_same_look(self) -> None:
        spec = copy.deepcopy(load(EXAMPLES["booking-mini"]))
        page_of(spec, "home")["blocks"].insert(0, {"custom": "bigtitle"})
        page_of(spec, "home")["blocks"].insert(1, {"custom": "bigtitle2"})
        out_dir = Path(self.tmp.name) / "h1"
        out_dir.mkdir(exist_ok=True)
        (out_dir / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        (out_dir / "content.js").write_text("""K.content({ pages: {
          bigtitle: () => `<h1 class="demo-t">页面标题</h1><section><h1>另一个标题</h1></section>`,
          bigtitle2: () => `<div class="demo-w"><h1 class="demo-sized">带自己字号的标题</h1></div>`,
        } })""", encoding="utf-8")
        (out_dir / "content.css").write_text(".demo-t{color:#123456}.demo-w h1{letter-spacing:0;font-size:22px}h1.demo-sized{font-weight:600}", encoding="utf-8")
        spec["content"] = "content.js"
        (out_dir / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(bp.build(out_dir / "spec.json", out_dir / "x.html"), 0)
        html = (out_dir / "x.html").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"<h1[\s>]", html)), 1, "内容模块里的 <h1> 在生成时就降了")
        self.assertIn(".demo-w h2:where([data-h1])", html, "内容样式里的 h1 选择器同步改写")
        context = self.browser.new_context(viewport={"width": 1500, "height": 900})
        self.addCleanup(context.close)
        page = context.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto((out_dir / "x.html").as_uri())
        page.wait_for_function("window.__PT__ && __PT__.cur().id")
        self.assertEqual(page.evaluate("document.querySelectorAll('h1').length"), 1)
        self.assertEqual(page.locator("#ptScreen h2[data-h1]").count(), 3)
        # 外观与真 h1 一样：默认字号 2em；作者的类选择器、改写后的 h1 选择器照常生效（特异性不变）
        look = page.evaluate("""() => { const probe = document.createElement('h1'); probe.textContent = 'x'; document.querySelector('#ptScreen .pt-body').appendChild(probe)
          const cs = (e) => { const s = getComputedStyle(e); return [s.fontSize, s.fontWeight, s.marginTop].join('|') }
          const bare = [...document.querySelectorAll('#ptScreen h2[data-h1]')].find((e) => !e.className)
          const out = { real: cs(probe), bare: cs(bare), sized: getComputedStyle(document.querySelector('.demo-sized')).fontSize, w: getComputedStyle(document.querySelector('.demo-sized')).fontWeight, color: getComputedStyle(document.querySelector('.demo-t')).color }
          probe.remove(); return out }""")
        self.assertEqual(look["bare"], look["real"], "降级后的默认外观与 h1 相同")
        self.assertEqual(look["sized"], "22px", "改写后的 `.demo-w h1` 规则仍然生效")
        self.assertEqual(look["w"], "600")
        self.assertEqual(look["color"], "rgb(18, 52, 86)")
        # 运行时塞进来的 h1（组件钩子、动态拼的 HTML）也降级
        page.evaluate("""() => { const d = document.createElement('div'); d.innerHTML = '<h1 id="late" class="x">晚到的标题<b>粗</b></h1>'; document.querySelector('#ptScreen .pt-body').appendChild(d); __PT__.mount(d) }""")
        self.assertEqual(page.evaluate("document.querySelectorAll('h1').length"), 1)
        self.assertEqual(page.evaluate("document.querySelector('#late').tagName + ':' + document.querySelector('#late b').textContent"), "H2:粗")
        self.assertEqual(errors, [])

    # -- 页面范式审计
    def test_page_pattern_check_page_on_the_homes(self) -> None:
        for name in ("generic-mini", "booking-mini"):
            if name not in self.built:
                continue
            with self.subTest(example=name):
                run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "page_pattern.py"), "check-page", str(self.built[name]), "--hash", "#/home", "--width", "390"],
                                     capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
