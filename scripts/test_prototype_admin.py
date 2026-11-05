"""后台模板（admin：外壳 + 列表 / 表单 / 设置 / 工作台 + 示例）的测试。

    py -X utf8 scripts/test_prototype_admin.py

分两部分：
1. 不要浏览器：生成器能构建两个示例、坏规格逐类报中文错、规格里没有任何必填的菜单或页面、通用部分没有行业字样与私人路径、
   Luz-Project 的原型硬检查。
2. 要浏览器（Playwright + Microsoft Edge，没有就跳过并写明）：打开无报错、侧栏分组与折叠、多标签页保持各自状态、面包屑只在二级页、
   表格排序 / 筛选 / 分页（默认 20）、批量栏原位替换、行内开关成功与失败回滚、居中面板与焦点陷阱、表单校验、经营设置闭环、配置面板、
   场景、逻辑面板、减少动态、重置、只读角色、390 手机与桌面布局、深浅外观、渲染审计（audit_rendered.py --library luz-kit）。
"""
from __future__ import annotations

import copy
import importlib.util
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
ADMIN = TEMPLATES / "admin"
EXAMPLES = {"generic-admin": TEMPLATES / "examples" / "generic-admin" / "spec.json", "service-admin": TEMPLATES / "examples" / "service-admin" / "spec.json"}
INDUSTRY = "\u82b1"  # 通用部分不许出现的行业字；用转义写，免得本文件自己带这个字
PRIVATE = ("Chil" + "th", "skill" + "输出", "@" + "gmail")
LOCAL_PATH = "D:" + "\\Codes"
CJK = re.compile(r"[\u4e00-\u9fff]")


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def kind_mod():
    mod_spec = importlib.util.spec_from_file_location("admin_kind_under_test", ADMIN / "build_kind.py")
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return mod


def check_of(spec: dict, content: str = "x") -> tuple[list[str], list[str]]:
    ctx = bp.Ctx(spec, EXAMPLES["generic-admin"], ADMIN, bp.component_index())
    return bp.check_spec(spec, content, kind_mod(), ctx)


def page_of(spec: dict, pid: str) -> dict:
    return next(p for p in spec["pages"] if p["id"] == pid)


def nav_leaves(nodes: list, out: list | None = None) -> list:
    out = [] if out is None else out
    for n in nodes:
        if n.get("page"):
            out.append(n)
        nav_leaves(n.get("children") or [], out)
    return out


def minimal_spec() -> dict:
    """一个页面、一个菜单项、没有工作台、没有订单商品：规格里除了引用关系，没有任何必填的菜单或页面。"""
    return {
        "schema": "luz-prototype/1", "kind": "admin", "meta": {"title": "最小后台"},
        "nav": [{"id": "notes", "name": "记录", "icon": "list", "page": "notes"}],
        "data": {"maps": {"st": {"a": {"label": "进行中", "tone": "in"}, "b": {"label": "已结束", "tone": "mu"}}}, "notes": [{"id": "1", "title": "第一条", "st": "a"}, {"id": "2", "title": "第二条", "st": "b"}]},
        "pages": [{"id": "notes", "name": "记录", "type": "tab", "tab": "notes", "logic": {"from": "侧栏", "back": "无", "done": "无", "primary": "查看", "rules": ["示例"]},
                   "list": {"data": "notes", "noun": "记录", "columns": [{"key": "title", "label": "标题", "type": "long"}, {"key": "st", "label": "状态", "type": "status", "map": "st"}]}}],
    }


# ------------------------------------------------------------------ 一、不要浏览器

class GeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out: dict[str, Path] = {}
        for name, spec_path in EXAMPLES.items():
            out = Path(cls.tmp.name) / f"{name}.html"
            code = bp.build(spec_path, out)
            assert code == 0, name
            cls.out[name] = out
        cls.base = load(EXAMPLES["generic-admin"])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_examples_validate_and_build_single_files(self) -> None:
        schema = bp.load_schema()
        for name, spec_path in EXAMPLES.items():
            self.assertEqual(bp.validate_schema(load(spec_path), schema, schema), [], name)
            text = self.out[name].read_text(encoding="utf-8")
            self.assertGreater(len(text.encode("utf-8")), 120_000, name)
            self.assertLess(len(text.encode("utf-8")), 4_000_000, name)
            for marker in ("prefers-reduced-motion", "showModal", "K.panel(", "role=\"dialog\"", "data-dark-mode=\"tokens\""):
                self.assertIn(marker, text, f"{name}: {marker}")
            self.assertEqual(len(re.findall(r"<script src=", text)), 0, "单文件：没有外链脚本")

    def test_generic_example_page_counts_and_coverage(self) -> None:
        spec = self.base
        self.assertGreaterEqual(len(spec["pages"]), 12)
        kinds = {k for p in spec["pages"] for k in ("list", "dashboard", "form", "settings", "detail", "result", "blocks", "custom") if p.get(k)}
        self.assertEqual(kinds, {"list", "dashboard", "form", "settings", "detail", "result", "blocks", "custom"})
        self.assertEqual({p["type"] for p in spec["pages"]}, {"tab", "sub", "sheet", "result"})
        svc = load(EXAMPLES["service-admin"])
        self.assertTrue(8 <= len(svc["pages"]) <= 12, len(svc["pages"]))

    def test_two_examples_show_different_menus_and_dashboards_from_the_same_mechanism(self) -> None:
        a, b = load(EXAMPLES["generic-admin"]), load(EXAMPLES["service-admin"])
        names_a, names_b = {n["name"] for n in nav_leaves(a["nav"])}, {n["name"] for n in nav_leaves(b["nav"])}
        self.assertFalse({"订单", "商品"} & names_b, "到店服务示例没有商品和订单")
        self.assertLessEqual(len(names_a & names_b), 1, "两份示例的菜单明显不同")
        sec_a = {s["kind"] for s in page_of(a, "dash")["dashboard"]["sections"]}
        sec_b = {s["kind"] for s in page_of(b, "today")["dashboard"]["sections"]}
        self.assertIn("agenda", sec_b)
        self.assertNotIn("agenda", sec_a)
        self.assertEqual(a["kind"], b["kind"])

    def test_minimal_spec_builds_without_any_required_menu_page_or_component(self) -> None:
        errs, _ = check_of(minimal_spec(), "")
        self.assertEqual(errs, [], errs)
        with tempfile.TemporaryDirectory() as tmp:
            sp = Path(tmp) / "spec.json"
            sp.write_text(json.dumps(minimal_spec(), ensure_ascii=False), encoding="utf-8")
            self.assertEqual(bp.build(sp, Path(tmp) / "min.html"), 0)

    def test_bad_specs_are_reported_in_chinese_one_class_at_a_time(self) -> None:
        base = self.base

        def mut(fn):
            s = copy.deepcopy(base)
            fn(s)
            return check_of(s)[0]

        cases = {
            "缺页面（菜单指向不存在的页面）": (lambda s: s["nav"][1]["children"][0].update(page="ghost"), "不存在"),
            "孤岛页面": (lambda s: (page_of(s, "products").update(actions=[]), page_of(s, "products")["list"].update(rowActions=[])), "孤岛页面"),
            "坏组件编号": (lambda s: page_of(s, "roles")["blocks"].__setitem__(0, {"cid": "AD-XXX-999"}), "组件编号"),
            "重复入口": (lambda s: page_of(s, "roles").update(blocks=[{"cid": "AD-MGMT-001", "go": {".a@0": "res-denied", ".b@0": "res-denied"}}]), "同一目的地"),
            "分组只有一项且同名": (lambda s: s["nav"].__setitem__(1, {"id": "g-x", "name": "订单", "children": [s["nav"][1]["children"][0]]}), "同名"),
            "分组只有一项": (lambda s: s["nav"][1]["children"].pop(), "只有 1 项"),
            "扁平的 group 字段": (lambda s: s["nav"][0].update(group="概览"), "group"),
            "二三级项放图标": (lambda s: s["nav"][3]["children"][0].update(icon="box"), "不放图标"),
            "超过三级": (lambda s: s["nav"].__setitem__(1, {"id": "a", "name": "一", "icon": "box", "children": [{"id": "b", "name": "二", "icon": "box", "children": [{"id": "c", "name": "三", "icon": "box", "children": s["nav"][1]["children"]}]}]}), "超过三级"),
            "有 page 又有 children": (lambda s: s["nav"][0].update(children=[{"id": "z", "name": "子", "page": "orders"}]), "既有 page 又有 children"),
            "面包屑出现在一级页": (lambda s: page_of(s, "orders").update(crumb="订单"), "面包屑"),
            "标题与高亮菜单同名": (lambda s: page_of(s, "orders").update(title="订单"), "同名"),
            "类型 panel": (lambda s: page_of(s, "order-detail").update(type="panel"), "居中面板"),
            "面板从底部弹出": (lambda s: page_of(s, "order-detail").update(layout="bottom"), "不从底部"),
            "菜单缺图标": (lambda s: s["nav"][0].pop("icon"), "没写 icon"),
            "页面操作缺图标": (lambda s: page_of(s, "products")["actions"][0].pop("icon"), "没写 icon"),
            "外露筛选超过 4 个": (lambda s: page_of(s, "orders")["list"]["filters"]["primary"].extend([{"key": "pay", "label": "支付", "options": "pay"}, {"key": "x", "label": "二", "options": "pay"}]), "外露筛选"),
            "行内操作带图标": (lambda s: page_of(s, "products")["list"]["rowActions"][0].update(icon="edit"), "不加图标"),
            "表头是英文字段名": (lambda s: page_of(s, "orders")["list"]["columns"][0].update(label="order_no"), "英文字段名"),
            "引用不存在的状态映射": (lambda s: page_of(s, "orders")["list"]["columns"][3].update(map="ghostMap"), "状态映射"),
            "每页条数档位不对": (lambda s: page_of(s, "orders")["list"].update(pageSize=15), "10 / 20 / 50 / 100"),
            "go 指向侧栏一级页": (lambda s: page_of(s, "res-saved")["result"]["actions"].__setitem__(1, {"label": "回", "icon": "list", "go": "products"}), "改用 tab"),
            "sheet 指向非面板": (lambda s: page_of(s, "orders")["list"]["rowActions"][0].update(sheet="products"), "不是居中面板"),
            "详情放在非面板页": (lambda s: page_of(s, "products").update(detail={"data": "products"}), "居中面板"),
            "结果页没有去处": (lambda s: page_of(s, "res-saved")["result"].update(actions=[]), "无路可走"),
            "设置项缺影响说明": (lambda s: page_of(s, "settings")["settings"]["groups"][0]["sections"][0]["items"][0].pop("impact"), "影响说明"),
            "表单没有保存": (lambda s: page_of(s, "product-edit")["form"].pop("submit"), "submit"),
            "模块 id 重复": (lambda s: page_of(s, "dash")["dashboard"]["sections"][1].update(id="trend"), "模块 id"),
            "通知跳转到不存在的页面": (lambda s: s["shell"]["notices"][0].update(go="ghost"), "不存在"),
        }
        for name, (fn, needle) in cases.items():
            with self.subTest(name):
                errs = mut(fn)
                hit = [e for e in errs if needle in e]
                self.assertTrue(hit, f"{name}：应报含「{needle}」的错，实际：{errs[:4]}")
                for e in errs:
                    self.assertRegex(e, CJK, f"错误信息要用中文：{e}")

    def test_example_meta_has_no_tool_words(self) -> None:
        for name, path in EXAMPLES.items():
            meta = load(path)["meta"]
            for key in ("title", "subtitle", "brand", "version"):
                for w in ("模板", "规格", "组件库", "拼装", "生成", "示例"):
                    self.assertNotIn(w, meta.get(key, ""), f"{name} 的 meta.{key} 不要写工具话（说明放示例 README）")

    def test_role_notes_match_the_pages_that_deny_them(self) -> None:
        expected = {
            "generic-admin": {"operator": {"roles"}, "viewer": {"roles"}},
            "service-admin": {"front": {"shop-settings"}},
        }
        for name, per_role in expected.items():
            spec = load(EXAMPLES[name])
            leaf = {n["page"]: n["name"] for n in nav_leaves(spec["nav"])}
            for role in spec["roles"]:
                denied = {p["id"] for p in spec["pages"] if p.get("roles") and role["id"] not in p["roles"]}
                self.assertEqual(denied, per_role.get(role["id"], set()), f"{name}：角色「{role['name']}」被拒绝的页面与说明对不上")
                for pid in denied:
                    self.assertIn(leaf[pid], role["note"], f"{name}：角色说明要点名被拒绝的页面「{leaf[pid]}」")
            readonly = [r["id"] for r in spec["roles"] if r.get("readonly")]
            self.assertEqual(readonly, ["viewer"] if name == "generic-admin" else [])

    def test_workarounds_for_old_engine_gaps_are_gone(self) -> None:
        js = "\n".join(f.read_text(encoding="utf-8") for f in (ADMIN / "js").glob("*.js"))
        css = (ADMIN / "admin.css").read_text(encoding="utf-8")
        for dead in ("tagDialog", "lockMask", "guardDialog", "closedby", "clearStacks", "readonlyRoles"):
            self.assertNotIn(dead, js, f"绕法「{dead}」应已去掉")
        self.assertNotIn(".pt-layout", css, "不再覆盖外壳三栏的列宽（用 K.kind 的 layout）")
        self.assertIn("keepTabStacks: true", js)
        self.assertIn("layout: () =>", js)
        for spec_path in EXAMPLES.values():
            spec = load(spec_path)
            self.assertFalse([p["id"] for p in spec["pages"] if p.get("links")], "示例不再手写 links（kind 的 edges 钩子自动报出）")
            self.assertFalse([n["id"] for n in nav_leaves(spec["nav"]) if n.get("group")], "分组写成分组节点，不用扁平的 group 字段")
            self.assertIn("shell", spec)
            self.assertNotIn("shell", spec.get("data", {}))
        for name, path in EXAMPLES.items():
            css_all = (ADMIN / "admin.css").read_text(encoding="utf-8")
            body = re.sub(r"/\*.*?\*/", "", css_all, flags=re.S)
            for m in re.finditer(r"(?:transition|animation)\s*:[^;{}]*", body):
                for d in re.findall(r"(?<![\w.-])(\d*\.?\d+)(ms|s)\b", m.group(0)):
                    ms = float(d[0]) * (1000 if d[1] == "s" else 1)
                    loop = "infinite" in m.group(0)
                    self.assertTrue(loop or ms in (0, 100, 150, 200, 300), f"动效时长只用 100/150/200/300 毫秒（--mo-*）：{m.group(0)}")
            break

    def test_checker_messages_speak_of_references_not_required_templates(self) -> None:
        text = (ADMIN / "build_kind.py").read_text(encoding="utf-8")
        self.assertNotIn("必须包含", text)
        self.assertNotIn("模板必须", text)
        errs = check_of(self.base | {"nav": [dict(self.base["nav"][0], page="ghost")] + self.base["nav"][1:]})[0]
        self.assertTrue(any("不存在" in e for e in errs))

    def test_checker_does_not_demand_industry_pages(self) -> None:
        s = minimal_spec()
        errs, warns = check_of(s, "")
        self.assertEqual([e for e in errs if "工作台" in e or "订单" in e or "商品" in e or "首页" in e], [])

    def test_template_example_and_docs_carry_no_industry_words_or_private_paths(self) -> None:
        roots = [ADMIN, TEMPLATES / "examples" / "generic-admin", TEMPLATES / "examples" / "service-admin", HERE / "test_prototype_admin.py"]
        for root in roots:
            files = [root] if root.is_file() else [f for f in root.rglob("*") if f.is_file() and f.suffix in {".py", ".js", ".css", ".html", ".json", ".md"} and "__pycache__" not in f.parts]
            for f in files:
                text = f.read_text(encoding="utf-8")
                self.assertNotIn(INDUSTRY, text, f"{f.relative_to(HERE.parent)} 里出现了行业专属字样")
                for p in PRIVATE:
                    self.assertNotIn(p, text, f"{f.relative_to(HERE.parent)} 里出现了私人信息：{p}")
                if f.name != "test_prototype_admin.py":
                    self.assertNotIn(LOCAL_PATH, text, f"{f.relative_to(HERE.parent)} 里写了本机路径")

    def test_template_css_and_scripts_follow_the_visual_rules(self) -> None:
        css = re.sub(r"/\*.*?\*/", "", (ADMIN / "admin.css").read_text(encoding="utf-8"), flags=re.S)
        js ="\n".join(f.read_text(encoding="utf-8") for f in (ADMIN / "js").glob("*.js"))
        for text, name in ((css, "admin.css"), (js, "js")):
            self.assertNotRegex(text, r"transition\s*:\s*all", f"{name}: 不用 transition: all")
            self.assertNotRegex(text, r"font-style\s*:\s*italic", f"{name}: 不斜体")
            self.assertNotRegex(text, r"letter-spacing\s*:\s*[^0n]", f"{name}: 不加字距")
        self.assertNotRegex(css, r"position\s*:\s*fixed", "后台模板没有 position: fixed 的块")
        weights = set(re.findall(r"font-weight\s*:\s*(\d+)", css))
        self.assertTrue(weights <= {"400", "600", "700"}, weights)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn('html[data-reduce="1"]', css)
        self.assertNotRegex(css, r"transition\s*:[^;{}]*\b(width|left|top|margin|padding)\b", "过渡不写在布局属性上")

    def test_built_prototype_passes_the_luz_project_checks(self) -> None:
        sys.path.insert(0, r"D:\Codes\Luz-Project\scripts")
        try:
            import dev_documents  # noqa: PLC0415
        except Exception as exc:  # noqa: BLE001
            self.skipTest(f"没有 Luz-Project：{exc}")
        for name, out in self.out.items():
            root = out.parent
            errs = dev_documents._prototype_errors("测试", {"title": "原型", "kind": "wide", "file": out.name, "library": "luz-kit"}, root)
            self.assertEqual(errs, [], f"{name}: {errs}")


# ------------------------------------------------------------------ 二、要浏览器

@unittest.skipUnless(browser_available(), "需要 playwright 和 Microsoft Edge；没有时这一部分跳过")
class BrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from playwright.sync_api import sync_playwright

        cls.tmp = tempfile.TemporaryDirectory()
        cls.url = {}
        cls.path = {}
        for name, sp in EXAMPLES.items():
            out = Path(cls.tmp.name) / f"{name}.html"
            assert bp.build(sp, out) == 0
            cls.url[name] = out.as_uri()
            cls.path[name] = out
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="msedge")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.pw.stop()
        cls.tmp.cleanup()

    def open(self, name="generic-admin", w=1440, h=900, scheme="light"):
        ctx = self.browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme)
        self.addCleanup(ctx.close)
        pg = ctx.new_page()
        pg.errors = []
        pg.on("console", lambda m: pg.errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: pg.errors.append("PAGEERROR " + str(e)))
        pg.goto(self.url[name])
        pg.wait_for_selector("#adScreen .ad-scroll")
        return pg

    def is_open(self, pg, sel="#ptDlg"):
        """对话框是否开着：关闭前有 150 毫秒的退出动画（.closing），退出中算已关闭"""
        return pg.evaluate("(s) => { const d = document.querySelector(s); return !!d && d.open && !d.classList.contains('closing') }", sel)

    def nav(self, pg, tab):
        pg.evaluate("(t) => window.__PT__.ad.activate(t)", tab)
        pg.wait_for_timeout(120)

    def rows(self, pg):
        return pg.locator(".ad-list tbody tr[data-id]")

    def toasts(self, pg):
        return " ".join(pg.locator(".pt-toast").all_inner_texts())

    # ---------- 打开与外壳
    def test_every_page_opens_without_errors_in_light_and_dark_and_each_example(self):
        for name in EXAMPLES:
            for scheme in ("light", "dark"):
                with self.subTest(name=name, scheme=scheme):
                    pg = self.open(name, scheme=scheme)
                    if scheme == "dark":
                        pg.evaluate("window.__PT__.setCfg('appearance', 'dark')")
                        self.assertEqual(pg.evaluate("document.documentElement.dataset.theme"), "dark")
                    ids = pg.evaluate("window.__PT__.spec.pages.map(p => p.id)")
                    for pid in ids:
                        pg.evaluate("(i) => { const K = window.__PT__; K.jump(i) }", pid)
                        pg.wait_for_timeout(60)
                        self.assertTrue(pg.locator("#adScreen .ad-scroll").count() == 1, pid)
                        self.assertEqual(pg.locator("#adScreen .pt-miss").count(), 0, f"{pid} 渲染出错")
                        pg.evaluate("window.__PT__.sheet.close()")
                    self.assertEqual(pg.errors, [])

    def test_sidebar_groups_collapse_and_workspace_has_no_page_level_duplicate_title(self):
        pg = self.open(w=1920, h=1000)
        self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.mode"), "wide")
        groups = pg.locator("#adSide .ad-ngt").all_inner_texts()
        self.assertEqual(groups, ["交易", "会员与营销"], "没有图标的分组节点是分组标题")
        self.assertEqual(pg.locator("#adSide .ad-ni:not(.sub) .ad-ic:not(.chev)").count(), pg.locator("#adSide .ad-ni:not(.sub)").count(), "每个一级菜单项都有线性图标")
        par = pg.locator("#adSide .ad-ni.parent")
        self.assertEqual(par.get_attribute("aria-expanded"), "false")
        par.click()
        self.assertEqual(par.get_attribute("aria-expanded"), "true", "手风琴父项只管展开收起")
        self.assertEqual(pg.locator("#adSide .ad-ni.sub").count(), 3)
        self.assertEqual(pg.locator("#adSide .ad-ni.sub .ad-ic").count(), 0, "手风琴的子项不放图标")
        self.nav(pg, "audit")
        self.assertEqual(pg.locator("#adSide .ad-ni[aria-current=page]").inner_text().strip(), "操作日志")
        self.assertEqual(pg.locator("#adSide .ad-ni.parent").get_attribute("data-anc"), "1", "祖先项用较弱的方式高亮")
        self.assertGreater(pg.evaluate("document.querySelector('#adSide').offsetWidth"), 200)
        pg.click(".menu-btn")
        pg.wait_for_timeout(150)
        self.assertEqual(pg.evaluate("document.querySelector('#adSide').offsetWidth"), 64, "折叠成图标栏")
        self.assertFalse(pg.locator("#adSide .ad-ni .lb").first.is_visible())
        self.assertEqual(pg.evaluate("document.querySelector('#adTop .tbrand b').textContent.length > 0"), True, "顶栏有品牌标识与系统名")
        self.nav(pg, "orders")
        h2 = pg.locator("#adScreen .ad-h2").count()
        self.assertEqual(h2, 0, "一级页内容区顶部不放与高亮菜单同名的大标题")

    def test_multi_tabs_keep_their_own_state_and_close(self):
        pg = self.open()
        self.assertEqual(pg.locator("#adTabs .ad-tab").count(), 1)
        self.assertEqual(pg.locator("#adTabs .ad-tab .tx").count(), 0, "首页标签固定，不能关闭")
        pg.click("#adSide [data-ad-nav=orders]")
        pg.fill(".ad-list input[type=search]", "林小满")
        pg.wait_for_timeout(150)
        shown = self.rows(pg).count()
        pg.click("#adSide [data-ad-nav=products]")
        pg.click("tr[data-id] [data-ad-ra=edit]")
        pg.wait_for_selector("#adCrumb:not([hidden])")
        self.assertEqual(pg.locator("#adTabs .ad-tab").count(), 3)
        pg.click("#adTabs [data-ad-nav=orders]")
        self.assertEqual(pg.input_value(".ad-list input[type=search]"), "林小满", "切回订单标签，搜索条件还在")
        self.assertEqual(self.rows(pg).count(), shown)
        self.assertTrue(pg.locator("#adCrumb").is_hidden(), "订单是一级页，不放面包屑")
        pg.click("#adTabs [data-ad-nav=products]")
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "product-edit", "商品标签仍停在编辑子页")
        pg.click("#adTabs [data-ad-close=orders]")
        self.assertEqual(pg.locator("#adTabs .ad-tab").count(), 2)
        pg.click("[data-ad-pop=tabs]")
        pg.click("[data-ad-tabsop=others]")
        self.assertEqual(pg.locator("#adTabs .ad-tab").count(), 2, "关闭其他后保留首页与当前标签")
        self.assertEqual(pg.errors, [])

    def test_breadcrumb_only_on_sub_pages_and_links_back(self):
        pg = self.open()
        for tab in ("dash", "orders", "products", "settings"):
            self.nav(pg, tab)
            self.assertTrue(pg.locator("#adCrumb").is_hidden(), f"一级页「{tab}」不放面包屑")
        self.nav(pg, "products")
        pg.click(".ad-ph [data-pt-go], .ad-lbar [data-pt-go]")
        pg.wait_for_selector("#adCrumb:not([hidden])")
        self.assertEqual(pg.locator("#adCrumb button").first.inner_text(), "商品")
        self.assertEqual(pg.locator("#adCrumb b").inner_text(), "商品编辑")
        self.assertEqual(pg.locator("#adScreen .ad-h2").inner_text(), "新建商品")
        pg.click("#adCrumb button")
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "products")

    # ---------- 列表
    def test_table_default_view_sort_filter_pagination_and_alignment(self):
        pg = self.open()
        self.nav(pg, "orders")
        self.assertEqual(pg.locator(".ad-stabs [aria-selected=true]").first.inner_text().split()[0], "待发货", "打开即是默认视图：待发货")
        ids = pg.evaluate("[...document.querySelectorAll('.ad-list tbody tr[data-id]')].map(r => window.__PT__.data.orders.find(o => o.id === r.dataset.id).createdAt)")
        self.assertEqual(ids, sorted(ids), "待发货：等得最久的在前")
        pg.click(".ad-stabs [data-v=__all]")
        self.assertEqual(self.rows(pg).count(), 20, "默认每页 20 条")
        self.assertEqual(pg.input_value(".ad-pg select"), "20")
        self.assertEqual(pg.locator(".ad-pg select option").all_inner_texts(), ["10 条/页", "20 条/页", "50 条/页", "100 条/页"])
        total = int(re.search(r"共 (\d+) 条", pg.locator(".ad-pg").inner_text()).group(1))
        self.assertGreater(total, 50)
        pg.select_option(".ad-pg select", "50")
        self.assertEqual(self.rows(pg).count(), 50, "可切到每页 50 条")
        pg.select_option(".ad-pg select", "20")
        pg.click(".ad-pg [data-v='2']")
        self.assertEqual(pg.evaluate("window.__PT__.ad.lstate('orders').page"), 2)
        pg.fill(".ad-list input[type=search]", "林小满")
        pg.wait_for_timeout(150)
        self.assertEqual(pg.evaluate("window.__PT__.ad.lstate('orders').page"), 1, "改筛选后回到第 1 页")
        self.assertLess(self.rows(pg).count(), 20)
        pg.fill(".ad-list input[type=search]", "")
        pg.click("[data-ad-l=sort][data-k=amount]")
        amts = pg.evaluate("[...document.querySelectorAll('.ad-list tbody tr[data-id]')].map(r => window.__PT__.data.orders.find(o => o.id === r.dataset.id).amount)")
        self.assertEqual(amts, sorted(amts), "点表头升序")
        pg.click("[data-ad-l=sort][data-k=amount]")
        amts = pg.evaluate("[...document.querySelectorAll('.ad-list tbody tr[data-id]')].map(r => window.__PT__.data.orders.find(o => o.id === r.dataset.id).amount)")
        self.assertEqual(amts, sorted(amts, reverse=True), "再点降序")
        pg.select_option("[data-ad-f=channel]", "web")
        self.assertTrue(all(c == "网页" for c in pg.locator("td[data-label=渠道]").all_inner_texts()))
        pg.click("[data-ad-l=more]")
        self.assertTrue(pg.locator(".ad-more").is_visible(), "更多筛选展开")
        pg.click("[data-ad-l=clear]")
        self.assertEqual(pg.locator(".ad-chips").count(), 0)

    def test_table_alignment_row_height_and_density(self):
        pg = self.open()
        self.nav(pg, "finance")
        al = pg.evaluate("""(() => {
          const g = (s) => getComputedStyle(document.querySelector(s)).textAlign
          return {th: g('.ad-tbl thead th:nth-child(3)'), date: g('td[data-label=日期]'), money: g('td[data-label="交易额（元）"]'), status: g('td[data-label=状态]')}
        })()""")
        self.assertEqual(al["th"], "center", "表头居中")
        self.assertEqual(al["money"], "right", "金额右对齐")
        self.assertEqual(al["date"], "center", "短值居中")
        self.assertEqual(pg.evaluate("getComputedStyle(document.querySelector('td[data-label=\"交易额（元）\"]')).fontVariantNumeric"), "tabular-nums")
        h = pg.evaluate("document.querySelector('.ad-tbl tbody tr[data-id]').getBoundingClientRect().height")
        self.assertTrue(44 <= h <= 48.6, f"标准行高 48：{h}")
        self.assertEqual(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.ad-tbl td')).fontSize)"), 14)
        self.assertGreater(pg.locator(".ad-tbl tr.sumrow").count(), 1, "表尾合计行（本页合计 + 全部筛选结果合计）")
        pg.evaluate("window.__PT__.setCfg('density', 'compact')")
        h = pg.evaluate("document.querySelector('.ad-tbl tbody tr[data-id]').getBoundingClientRect().height")
        self.assertTrue(43.5 <= h <= 45.6, f"紧凑行高 44：{h}")
        self.assertEqual(pg.locator(".ad-tbl th").count(), pg.locator(".ad-tbl thead th").count())
        heads = pg.locator(".ad-tbl thead th").all_inner_texts()
        self.assertFalse([t for t in heads if re.fullmatch(r"[A-Za-z_]+", t.strip())], "表头没有英文字段名")

    def test_bulk_bar_replaces_the_toolbar_in_place_without_pushing_the_table(self):
        pg = self.open()
        self.nav(pg, "orders")
        top0 = pg.evaluate("document.querySelector('.ad-tw').getBoundingClientRect().top")
        bar0 = pg.evaluate("document.querySelector('.ad-lbar').getBoundingClientRect().top")
        pg.locator(".ad-list tbody tr[data-id] input[type=checkbox]").nth(0).check()
        pg.locator(".ad-list tbody tr[data-id] input[type=checkbox]").nth(1).check()
        self.assertIn("已选 2 项", pg.locator(".ad-lbar.bulk").inner_text())
        self.assertEqual(pg.evaluate("document.querySelector('.ad-lbar').getBoundingClientRect().top"), bar0, "批量栏在工具栏原位置")
        self.assertAlmostEqual(pg.evaluate("document.querySelector('.ad-tw').getBoundingClientRect().top"), top0, delta=14, msg="不把表格向下推")
        ids = pg.evaluate("[...document.querySelectorAll('.ad-list tbody tr.sel')].map(r => r.dataset.id)")
        pg.click("[data-ad-ba=ship]")
        pg.wait_for_timeout(700)
        self.assertEqual(pg.evaluate("(ids) => ids.map(i => window.__PT__.data.orders.find(o => o.id === i).status)", ids), ["shipped", "shipped"])
        self.assertIn("已发货 2 单", self.toasts(pg))
        self.assertEqual(pg.locator(".ad-lbar.bulk").count(), 0, "处理完批量栏还原")
        self.assertEqual(pg.evaluate("window.__PT__.data.audit[0].what.includes('批量发货')"), True, "操作写进日志")

    def test_inline_switch_succeeds_and_rolls_back_with_reason_in_place(self):
        pg = self.open()
        self.nav(pg, "products")
        sw = pg.locator("[data-ad-sw]").first
        on0 = sw.get_attribute("aria-checked")
        sw.click()
        self.assertEqual(pg.locator("[data-ad-sw]").first.get_attribute("aria-busy"), "true", "点击后进入处理中")
        pg.wait_for_timeout(750)
        self.assertNotEqual(pg.locator("[data-ad-sw]").first.get_attribute("aria-checked"), on0, "成功才切换")
        self.assertIn("已", self.toasts(pg))
        pg.evaluate("window.__PT__.setScene('switch', 'fail-busy')")
        before = pg.locator("[data-ad-sw]").first.get_attribute("aria-checked")
        pg.locator("[data-ad-sw]").first.click()
        pg.wait_for_timeout(750)
        self.assertEqual(pg.locator("[data-ad-sw]").first.get_attribute("aria-checked"), before, "失败回滚")
        self.assertIn("服务繁忙", pg.locator(".ad-swerr").first.inner_text(), "失败原因写在原位")
        pg.evaluate("window.__PT__.setScene('switch', 'ok')")
        pg.evaluate("window.__PT__.data.products[0].stock = 0; window.__PT__.data.products[0].on = false")
        pg.evaluate("window.__PT__.ad.activate('products', {tab: null})")
        pg.evaluate("window.__PT__.render()")
        first_on = pg.locator("[data-ad-sw]").first
        pg.evaluate("document.querySelector('.ad-list')")  # 保持列表在页
        row_id = pg.locator("tr[data-id]").first.get_attribute("data-id")
        pg.evaluate("(id) => { const r = window.__PT__.data.products.find(p => p.id === id); r.stock = 0; r.on = false; window.__PT__.render() }", row_id)
        pg.locator("tr[data-id]").first.locator("[data-ad-sw]").click()
        pg.wait_for_timeout(750)
        self.assertIn("库存为 0", pg.locator(".ad-swerr").first.inner_text(), "库存为 0 不能上架，规则给出原因")

    def test_export_preview_has_chinese_headers_and_scope(self):
        pg = self.open()
        self.nav(pg, "orders")
        pg.click("[data-ad-export]")
        pg.wait_for_selector("#ptDlg[open] [data-export-preview]")
        heads = pg.locator("#ptDlg [data-export-preview] th").all_inner_texts()
        self.assertTrue(heads and all(re.search(CJK, h) for h in heads), heads)
        self.assertIn("订单_待发货_2026-11-04.xlsx", pg.locator("#ptDlg").inner_text())
        self.assertIn("导出筛选结果", pg.locator("[data-ad-export]").inner_text() if pg.locator("[data-ad-export]").count() else "导出筛选结果")
        pg.keyboard.press("Escape")

    def test_search_keeps_focus_and_caret_while_typing_via_partial_rerender(self):
        pg = self.open()
        self.nav(pg, "orders")
        pg.click(".ad-list input[type=search]")
        pg.keyboard.type("林小")
        pg.wait_for_timeout(150)
        self.assertEqual(pg.evaluate("document.activeElement.dataset.fk"), "q", "即输即查：局部重画后焦点还在搜索框")
        self.assertEqual(pg.input_value(".ad-list input[type=search]"), "林小")
        pg.keyboard.type("满")
        self.assertEqual(pg.input_value(".ad-list input[type=search]"), "林小满", "光标位置保留，继续输入接在后面")
        self.assertGreater(pg.evaluate("window.__PT__.ad.lstate('orders').q.length"), 1)

    def test_module_display_switches_hide_dashboard_modules_and_blocks_and_reset_clears_them(self):
        for name, page, key, label, selector in (
            ("generic-admin", "dash", "trend", "趋势", ".ad-dc[data-module=trend]"),
            ("generic-admin", "roles", "role-matrix", "角色权限矩阵", "[data-cid='AD-MGMT-001']"),
            ("service-admin", "today", "agenda", "今天的预约", ".ad-dc[data-module=agenda]"),
            ("service-admin", "calendar", "week-calendar", "日程周视图", "[data-cid='AD-FLOW-005']"),
        ):
            with self.subTest(name=name, page=page):
                pg = self.open(name)
                pg.evaluate("(i) => window.__PT__.jump(i)", page)
                pg.wait_for_timeout(200)
                pg.click("[data-lt=scene]")
                self.assertIn("模块显示", pg.locator("#ptLeft").inner_text())
                sw = pg.locator(f"button[data-mod='{key}']")
                self.assertIn(label, sw.inner_text(), "模块名取规格里的 name")
                self.assertEqual(sw.get_attribute("aria-checked"), "true")
                self.assertGreater(pg.locator(f"#adScreen {selector}").count(), 0)
                sw.click()
                self.assertEqual(pg.locator(f"#adScreen {selector}").count(), 0, "关掉就不画这个模块")
                pg.evaluate("(i) => window.__PT__.jump(i)", "res-denied" if name == "generic-admin" else "res-lock")
                pg.evaluate("(i) => window.__PT__.jump(i)", page)
                pg.wait_for_timeout(150)
                self.assertEqual(pg.locator(f"#adScreen {selector}").count(), 0, "换页回来仍是关的")
                pg.click("[data-lt=scene]")
                pg.click("[data-reset]")
                pg.evaluate("(i) => window.__PT__.jump(i)", page)
                pg.wait_for_timeout(150)
                self.assertGreater(pg.locator(f"#adScreen {selector}").count(), 0, "重置演示数据清空模块开关")
                self.assertEqual(pg.errors, [])

    def test_stage_width_follows_the_layout_hook_and_fold_buttons_widen_it(self):
        pg = self.open(w=1920, h=1000)
        left = pg.evaluate("document.querySelector('.pt-left').getBoundingClientRect().width")
        right = pg.evaluate("document.querySelector('.pt-right').getBoundingClientRect().width")
        self.assertAlmostEqual(left, 264, delta=2)
        self.assertAlmostEqual(right, 320, delta=2)
        w0 = pg.evaluate("document.querySelector('#adApp').getBoundingClientRect().width")
        pg.click("[data-fold=left]")
        pg.click("[data-fold=right]")
        pg.wait_for_timeout(250)
        w1 = pg.evaluate("document.querySelector('#adApp').getBoundingClientRect().width")
        self.assertGreater(w1, w0 + 400, "两栏都折叠就是只看舞台")
        pg.click("[data-fold=left]")
        pg.click("[data-fold=right]")
        pg.wait_for_timeout(250)
        self.assertAlmostEqual(pg.evaluate("document.querySelector('#adApp').getBoundingClientRect().width"), w0, delta=2)

    def test_accordion_parent_in_icon_rail_opens_a_floating_menu(self):
        pg = self.open(w=1440)
        self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.mode"), "wide", "舞台优先：1440 宽也是完整侧栏")
        pg.click("[data-ad-w='820']")  # 图标栏用“预览宽度”工具到达（以前靠两侧面板把舞台挤窄，那是缺陷）
        self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.mode"), "mid")
        pg.click("#adSide .ad-ni.parent")
        self.assertTrue(pg.locator(".ad-menu").is_visible(), "图标栏下点手风琴父项出悬浮菜单")
        self.assertEqual(pg.locator(".ad-menu button").all_inner_texts(), ["财务对账", "角色权限", "操作日志"])
        pg.click(".ad-menu button >> nth=2")
        self.assertEqual(pg.evaluate("window.__PT__.S.tab"), "audit")
        pg.click("[data-ad-pop=pal]")
        pg.keyboard.type("日志")
        self.assertIn("财务与权限", pg.locator("#adPalList").inner_text(), "命令面板结果带层级路径")

    def test_tab_stacks_are_kept_by_the_engine_and_clicking_the_current_tab_goes_to_its_root(self):
        pg = self.open()
        self.nav(pg, "products")
        pg.click(".ad-lbar [data-pt-go]")
        pg.wait_for_selector("#adCrumb:not([hidden])")
        pg.click("#adSide [data-ad-nav=orders]")
        pg.click("#adSide [data-ad-nav=products]")
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "product-edit", "切回来还停在二级页（引擎 keepTabStacks）")
        pg.click("#adSide [data-ad-nav=products]")
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "products", "再点当前标签回到它的根页")
        self.assertTrue(pg.locator("#adCrumb").is_hidden())

    # ---------- 居中面板
    def test_detail_is_a_centered_modal_with_focus_trap_esc_and_mask(self):
        pg = self.open()
        self.nav(pg, "orders")
        pg.evaluate("document.querySelector('.ad-tw').scrollTop = 0")
        pg.click("tr[data-id] [data-ad-ra=view]")
        pg.wait_for_selector("#ptDlg[open]")
        pg.wait_for_timeout(450)
        self.assertEqual(pg.evaluate("document.querySelector('#ptDlg').getAttribute('role')"), "dialog")
        self.assertEqual(pg.evaluate("document.querySelector('#ptDlg').getAttribute('aria-modal')"), "true")
        off = pg.evaluate("""(() => { const s = document.querySelector('#ptDlg .pt-sheet').getBoundingClientRect(), c = document.querySelector('#ptDlg #ptClip').getBoundingClientRect(); return [(s.left + s.right) / 2 - (c.left + c.right) / 2, (s.top + s.bottom) / 2 - (c.top + c.bottom) / 2] })()""")
        self.assertTrue(abs(off[0]) < 3 and abs(off[1]) < 3, f"居中：{off}")
        self.assertTrue(pg.locator("#ptDlg .pt-mask").is_visible(), "有遮罩")
        for _ in range(14):
            pg.keyboard.press("Tab")
            self.assertTrue(pg.evaluate("document.querySelector('#ptDlg').contains(document.activeElement)"), "焦点陷阱")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(150)
        self.assertFalse(self.is_open(pg))
        pg.click("tr[data-id] [data-ad-ra=view]")
        pg.wait_for_selector("#ptDlg[open]")
        pg.wait_for_timeout(450)
        pg.mouse.click(*pg.evaluate("(() => { const r = document.querySelector('#ptDlg .pt-mask').getBoundingClientRect(); return [r.left + 6, r.top + 6] })()"))
        pg.wait_for_timeout(200)
        self.assertFalse(self.is_open(pg), "详情点遮罩可关闭")
        self.assertEqual(pg.locator(".ad-stabs [aria-selected=true]").first.inner_text().split()[0], "待发货", "关闭后回到列表原位置，状态标签保留")

    def test_detail_action_patches_the_row_and_confirm_is_a_centered_dialog(self):
        pg = self.open()
        self.nav(pg, "orders")
        row = pg.locator("tr[data-id]").first
        oid = row.get_attribute("data-id")
        row.locator("[data-ad-ra=view]").click()
        pg.click("#ptDlg [data-ad-da=close]")
        pg.wait_for_selector("#ptDlg2[open] .pt-confirm")
        self.assertIn("关闭订单", pg.locator("#ptDlg2 h3").inner_text())
        self.assertTrue(self.is_open(pg), "确认框叠在详情面板上，详情还在下面")
        self.assertEqual(pg.evaluate("document.querySelector('#ptDlg2').getAttribute('data-cid')"), "AD-FB-002")
        pg.wait_for_timeout(300)
        pg.mouse.click(*pg.evaluate("(() => { const r = document.querySelector('#ptDlg2 .pt-mask').getBoundingClientRect(); return [r.left + 6, r.top + 6] })()"))
        pg.wait_for_timeout(250)
        self.assertTrue(self.is_open(pg, "#ptDlg2"), "确认框点遮罩不关闭")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(300)
        self.assertFalse(self.is_open(pg, "#ptDlg2"), "Esc 先关最上面一层")
        self.assertTrue(self.is_open(pg), "详情那层保持")
        pg.click("#ptDlg [data-ad-da=close]")
        pg.wait_for_selector("#ptDlg2[open] .pt-confirm")
        pg.click("#ptDlg2 [data-confirm-ok]")
        pg.wait_for_timeout(700)
        self.assertEqual(pg.evaluate("(i) => window.__PT__.data.orders.find(o => o.id === i).status", oid), "closed")

    # ---------- 表单
    def test_form_page_validates_on_submit_saves_and_shows_the_result_page(self):
        pg = self.open()
        self.nav(pg, "products")
        n0 = pg.evaluate("window.__PT__.data.products.length")
        pg.click(".ad-lbar [data-pt-go]")
        pg.wait_for_selector(".ad-form")
        pg.click("[data-ad-fsubmit]")
        self.assertEqual(pg.evaluate("document.activeElement.dataset.adIn"), "name", "定位到第一个错误")
        self.assertEqual(pg.locator("[data-field=name] .err").inner_text(), "请填写商品名称")
        self.assertEqual(pg.locator("[data-field=name] [aria-invalid=true]").count(), 1)
        self.assertIn("还有", pg.locator(".ad-ferr").inner_text())
        pg.fill("[data-ad-in=name]", "测试水杯")
        pg.select_option("[data-ad-in=cat]", "家居")
        pg.fill("[data-ad-in=price]", "88")
        pg.press("[data-ad-in=price]", "Tab")
        self.assertEqual(pg.input_value("[data-ad-in=price]"), "88.00", "金额失焦补两位小数")
        pg.evaluate("window.__PT__.setScene('submit', 'fail-busy')")
        pg.click("[data-ad-fsubmit]")
        pg.wait_for_timeout(700)
        self.assertIn("保存失败：服务繁忙", pg.locator(".ad-ferr").inner_text())
        self.assertEqual(pg.input_value("[data-ad-in=name]"), "测试水杯", "失败保留输入")
        pg.evaluate("window.__PT__.setScene('submit', 'ok')")
        pg.click("[data-ad-fsubmit]")
        pg.wait_for_timeout(700)
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "res-saved")
        self.assertEqual(pg.evaluate("window.__PT__.data.products.length"), n0 + 1)
        self.assertEqual(pg.evaluate("window.__PT__.data.products[0].name"), "测试水杯")
        pg.click("#adScreen [data-ad-nav=products]")
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "products")

    def test_panel_form_blocks_mask_close_asks_before_discarding_and_saves_back_to_the_list(self):
        pg = self.open()
        self.nav(pg, "promo")
        pg.click(".ad-lbar [data-pt-sheet]")
        pg.wait_for_selector("#ptDlg[open] .ad-form")
        pg.wait_for_timeout(300)
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(300)
        self.assertFalse(self.is_open(pg), "没改过的表单直接关闭")
        pg.click(".ad-lbar [data-pt-sheet]")
        pg.wait_for_selector("#ptDlg[open] .ad-form")
        pg.wait_for_timeout(300)
        pg.fill("[data-ad-in=name]", "测试活动")
        pg.mouse.click(*pg.evaluate("(() => { const r = document.querySelector('#ptDlg .pt-mask').getBoundingClientRect(); return [r.left + 6, r.top + 6] })()"))
        pg.wait_for_timeout(250)
        self.assertTrue(self.is_open(pg), "表单面板点遮罩不关闭")
        self.assertFalse(self.is_open(pg, "#ptDlg2"), "点遮罩连确认也不弹")
        pg.click("[data-ad-fsubmit]")
        self.assertEqual(pg.locator("[data-field=start] .err").inner_text(), "请填写开始日期")
        pg.fill("[data-ad-in=start]", "2026-11-10")
        pg.fill("[data-ad-in=end]", "2026-11-20")
        pg.keyboard.press("Escape")
        pg.wait_for_selector("#ptDlg2[open]")
        self.assertIn("放弃未保存的修改", pg.locator("#ptDlg2").inner_text(), "有未保存内容时关闭先确认")
        pg.click("#ptDlg2 [data-confirm-cancel]")
        pg.wait_for_timeout(300)
        self.assertTrue(self.is_open(pg), "选“继续编辑”表单还在")
        self.assertEqual(pg.input_value("[data-ad-in=name]"), "测试活动")
        pg.click("[data-ad-fsubmit]")
        pg.wait_for_timeout(700)
        self.assertFalse(self.is_open(pg))
        self.assertEqual(pg.evaluate("window.__PT__.data.promos[0].name"), "测试活动")
        pg.click(".ad-lbar [data-pt-sheet]")
        pg.wait_for_selector("#ptDlg[open] .ad-form")
        pg.wait_for_timeout(300)
        pg.fill("[data-ad-in=name]", "另一个")
        pg.click("[data-ad-fcancel]")
        pg.wait_for_timeout(300)
        self.assertFalse(self.is_open(pg), "取消按钮直接关闭并丢弃草稿")
        pg.click(".ad-lbar [data-pt-sheet]")
        pg.wait_for_selector("#ptDlg[open] .ad-form")
        self.assertEqual(pg.input_value("[data-ad-in=name]"), "", "丢弃后重新打开是空表单")

    # ---------- 设置闭环
    def test_settings_money_item_needs_reason_and_identity_and_writes_the_audit_log(self):
        pg = self.open()
        self.nav(pg, "settings")
        pg.click("[data-skey=refundFee] [data-ad-sedit]")
        pg.fill("[data-ad-sin]", "9")
        pg.click("[data-ad-sok=refundFee]")
        self.assertIn("超出范围", pg.locator(".why").inner_text())
        pg.fill("[data-ad-sin]", "3")
        pg.click("[data-ad-sok=refundFee]")
        pg.wait_for_selector("#ptDlg[open] .pt-fields")
        self.assertIn("1.5%", pg.locator("#ptDlg").inner_text())
        self.assertIn("3%", pg.locator("#ptDlg").inner_text())
        pg.click("#ptDlg [data-confirm-ok]")
        self.assertIn("原因", pg.locator("#ptDlg .pt-ferr").first.inner_text())
        self.assertTrue(self.is_open(pg), "必填不通过不关闭")
        pg.fill("#ptDlg [name=reason]", "对齐新的结算协议")
        pg.click("#ptDlg [data-confirm-ok]")
        self.assertIn("登录密码", pg.locator("#ptDlg .pt-ferr").nth(1).inner_text())
        pg.fill("#ptDlg [name=password]", "x")
        pg.click("#ptDlg [data-confirm-ok]")
        pg.wait_for_timeout(500)
        self.assertEqual(pg.evaluate("window.__PT__.data.settings.refundFee"), 3)
        self.assertIn("只影响之后的业务", self.toasts(pg))
        self.assertIn("本店", pg.locator("[data-skey=refundFee]").inner_text())
        self.assertIn("退款手续费", pg.evaluate("window.__PT__.data.audit[0].what"))
        self.assertIn("对齐新的结算协议", pg.evaluate("window.__PT__.data.audit[0].what"))
        pg.click("[data-skey=refundFee] [data-ad-sreset]")
        pg.wait_for_selector("#ptDlg[open] .pt-fields")
        pg.fill("#ptDlg [name=reason]", "恢复")
        pg.fill("#ptDlg [name=password]", "x")
        pg.click("#ptDlg [data-confirm-ok]")
        pg.wait_for_timeout(500)
        self.assertEqual(pg.evaluate("window.__PT__.data.settings.refundFee"), 1)
        pg.click("[data-ad-scat=coupon]")
        pg.click("[data-ad-sset=stackable]")
        pg.wait_for_timeout(500)
        self.assertEqual(pg.evaluate("window.__PT__.data.settings.stackable"), True, "开关直接生效，不放保存按钮")
        self.assertFalse(self.is_open(pg))
        self.assertEqual(pg.locator("#adScreen button:has-text('保存')").count(), 0)

    # ---------- 配置、场景、逻辑面板、减少动态、重置
    def test_config_panel_changes_theme_icon_style_sidebar_and_density(self):
        pg = self.open()
        pg.click("[data-lt=look]")
        self.assertTrue(pg.locator("#ptCfg").is_visible())
        titles = pg.locator("#ptCfg h3").all_inner_texts()
        for need in ("外观", "主题色", "侧栏深浅", "密度", "图标风格"):
            self.assertIn(need, titles)
        pg.click("[data-g=theme][data-v=blue]")
        self.assertEqual(pg.evaluate("document.querySelector('#root').getAttribute('data-lt')"), "blue")
        self.assertEqual(pg.evaluate("getComputedStyle(document.querySelector('#root')).getPropertyValue('--p').trim().toUpperCase()"), "#5577A4")
        self.assertEqual(pg.evaluate("getComputedStyle(document.querySelector('.ad-ni[aria-current=page]')).backgroundColor"), "rgb(240, 243, 247)", "派生令牌（侧栏高亮底）跟随主题色")
        pg.click("[data-g=iconStyle][data-v=line]")
        self.assertIn("ics-line", pg.evaluate("document.querySelector('#adScreen').className"))
        self.assertEqual(pg.locator(".ad-kpi img.ico").count(), 0, "线性风格不再出现图片图标")
        pg.click("[data-g=iconStyle][data-v='3d']")
        self.assertGreater(pg.locator(".ad-kpi img.ico").count(), 0, "3D 风格用库里的图标素材")
        pg.click("[data-g=sidebar][data-v=dark]")
        lum = pg.evaluate("(() => { const m = getComputedStyle(document.querySelector('#adSide')).backgroundColor.match(/\\d+/g).map(Number); return (m[0] + m[1] + m[2]) / 3 })()")
        self.assertLess(lum, 80, "深色侧栏")
        self.assertEqual(pg.evaluate("document.querySelector('#adSide').dataset.cid"), "AD-NAV-002")
        pg.click("[data-g=density][data-v=compact]")
        self.assertEqual(pg.evaluate("document.querySelector('#root').dataset.cfgDensity"), "compact")
        pg.click("[data-g=appearance][data-v=dark]")
        self.assertEqual(pg.evaluate("document.documentElement.dataset.theme"), "dark")
        pg.click("[data-g=appearance][data-v=light]")
        self.assertEqual(pg.evaluate("document.documentElement.dataset.theme"), "light")
        self.assertEqual(pg.errors, [])

    def test_scene_panel_lists_every_state_and_switches_the_page(self):
        pg = self.open()
        self.nav(pg, "orders")
        pg.click("[data-lt=scene]")
        panel = pg.locator("#ptLeft").inner_text()
        for need in ("正常", "加载中", "空", "失败：网络不可用", "失败：请求超时", "失败：服务繁忙", "失败：数据已失效", "无权限", "禁用", "行内开关结果", "保存与操作结果", "成功", "处理中", "失败：服务繁忙", "网络", "减少动态", "角色", "重置演示数据"):
            self.assertIn(need, panel)
        for scn, sel in (("view:loading", ".ad-sk"), ("view:empty", ".ad-empty"), ("view:fail-timeout", ".ad-empty [data-pt-act=retry]"), ("view:denied", ".ad-empty"), ("view:disabled", ".ad-banner")):
            pg.click(f"[data-scn='{scn}']")
            self.assertGreater(pg.locator(f"#adScreen {sel}").count(), 0, scn)
        pg.click("[data-scn='view:disabled']")
        self.assertGreater(pg.locator("#adScreen [aria-disabled=true][data-write]").count(), 0, "禁用：写操作灰掉")
        pg.locator("#adScreen [aria-disabled=true][data-write]").first.click(force=True)
        self.assertTrue(self.toasts(pg), "点禁用项说明原因")
        pg.click("[data-scn='view:ok']")
        pg.click("[data-net=offline]")
        self.assertGreater(pg.locator("#adScreen [data-pt-act=retry]").count(), 0, "断网：失败页带重试")
        pg.click("[data-net=online]")

    def test_logic_panel_follows_the_page(self):
        pg = self.open(w=1920, h=1000)  # 1440 宽时右栏是抽屉（默认收起），并排要 1612 以上
        for tab, name in (("orders", "订单"), ("products", "商品"), ("settings", "系统设置")):
            self.nav(pg, tab)
            txt = pg.locator("#ptRight").inner_text()
            self.assertIn(name, txt)
            for need in ("来源", "返回", "完成后", "主操作", "业务规则"):
                self.assertIn(need, txt)
        pg.click("[data-rt=status]")
        self.assertIn("待发货", pg.locator("#ptRight").inner_text())
        pg.click("[data-rt=logic]")
        self.nav(pg, "orders")
        pg.click("tr[data-id] [data-ad-ra=view]")
        pg.wait_for_selector("#ptDlg[open]")
        self.assertIn("订单详情", pg.locator("#ptRight").inner_text())
        self.assertIn("居中面板", pg.locator("#ptRight").inner_text())

    def test_reduce_motion_switch_reset_and_readonly_role(self):
        pg = self.open()
        pg.click("[data-lt=scene]")
        pg.click("button[data-reduce]")
        self.assertEqual(pg.evaluate("document.documentElement.dataset.reduce"), "1")
        self.assertLess(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.ad-ni')).transitionDuration)"), 0.01)
        self.nav(pg, "orders")
        pg.evaluate("window.__PT__.data.orders[0].status = 'closed'; window.__PT__.data.settings.fee = 9")
        pg.click("[data-reset]")
        self.assertEqual(pg.evaluate("window.__PT__.data.orders[0].status !== 'closed'"), True, "重置还原演示数据")
        self.assertEqual(pg.evaluate("window.__PT__.S.tab"), "dash")
        self.assertEqual(pg.locator("#adTabs .ad-tab").count(), 1, "重置后标签页回到首页")
        pg.click("[data-role=viewer]")
        self.nav(pg, "orders")
        self.assertIn("只读", pg.locator("#adScreen .ad-banner").first.inner_text())
        dis = pg.locator("#adScreen [aria-disabled=true][data-reason]")
        self.assertGreater(dis.count(), 0, "只读角色写操作禁用")
        self.assertTrue(dis.first.get_attribute("data-reason"))
        dis.first.click(force=True)
        self.assertIn("只读", self.toasts(pg), "点按时说明原因")
        self.nav(pg, "roles")
        self.assertIn("暂无权限", pg.locator("#adScreen").inner_text())
        pg.click("#adScreen [data-pt-go]")
        self.assertEqual(pg.evaluate("window.__PT__.cur().id"), "res-denied")
        self.assertIn("需要的角色", pg.locator("#adScreen").inner_text())

    def test_account_menu_notice_dropdown_and_palette(self):
        pg = self.open()
        n0 = pg.evaluate("document.querySelector('#adTop .dot').textContent")
        pg.click("[data-ad-pop=bell]")
        pg.click("[data-ad-notice=all]")
        self.assertEqual(pg.locator("#adTop .dot").count(), 0, "全部已读后红点消失")
        pg.keyboard.press("Escape")
        pg.click("[data-ad-pop=acct]")
        self.assertEqual(pg.locator(".ad-pop [data-ad-appear]").count(), 3, "外观三选在账号菜单里")
        pg.click("[data-ad-appear=dark]")
        self.assertEqual(pg.evaluate("document.documentElement.dataset.theme"), "dark")
        pg.click("[data-ad-appear=light]")
        pg.keyboard.press("Escape")
        pg.keyboard.press("Control+k")
        pg.wait_for_selector("#adPalIn")
        pg.keyboard.type("订单")
        pg.keyboard.press("Enter")
        self.assertEqual(pg.evaluate("window.__PT__.S.tab"), "orders")
        self.assertTrue(int(n0) > 0)

    def test_dashboard_computes_metrics_charts_hover_and_todo_links(self):
        pg = self.open()
        self.assertEqual(pg.locator(".ad-kpi").count(), 5)
        self.assertGreater(pg.locator(".ad-kpi .dl b").count(), 3, "指标卡带较上期变化")
        self.assertRegex(pg.locator(".ad-kpi .vl").first.inner_text(), r"^[\d,]+\.\d{2}")
        v7 = pg.locator(".ad-kpi .vl").first.inner_text()
        pg.click("[data-ad-dr='30']")
        self.assertNotEqual(pg.locator(".ad-kpi .vl").first.inner_text(), v7, "时间范围统一控制所有卡片")
        self.assertNotIn("近 30 天", pg.locator(".ad-dc").first.inner_text(), "卡片上不再写时间范围")
        pg.hover(".ad-chart svg rect.hit", position={"x": 200, "y": 40})
        self.assertTrue(pg.locator(".ad-tip").first.is_visible(), "图表悬停提示")
        pg.click("[data-ad-dl]")
        self.assertEqual(pg.locator(".ad-legend [aria-pressed=false]").count(), 1, "点图例显隐")
        pg.click(".ad-todo button.rw >> nth=0")
        self.assertEqual(pg.evaluate("window.__PT__.S.tab"), "orders")
        self.assertEqual(pg.evaluate("window.__PT__.ad.lstate('orders').tab"), "pending", "待办直达已筛选好的列表")

    # ---------- 布局
    def test_phone_390_is_operable_without_horizontal_overflow(self):
        pg = self.open(w=390, h=844)
        self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.mode"), "narrow")
        self.assertFalse(pg.locator("#adSide .ad-ni").first.is_visible(), "侧栏收进抽屉")
        pg.click(".menu-btn")
        pg.wait_for_timeout(300)
        self.assertTrue(pg.locator("#adSide .ad-ni").first.is_visible())
        pg.click("#adSide [data-ad-nav=orders]")
        pg.wait_for_timeout(300)
        self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.side"), "closed", "选了菜单抽屉收起")
        self.assertEqual(pg.evaluate("getComputedStyle(document.querySelector('.ad-tbl thead')).display"), "none", "表格转卡片")
        self.assertEqual(pg.evaluate("getComputedStyle(document.querySelector('.ad-tbl tbody td:nth-child(2)')).display"), "flex")
        self.assertFalse(pg.evaluate("document.documentElement.scrollWidth > innerWidth + 1"))
        pg.click("tr[data-id] [data-ad-ra=view]")
        pg.wait_for_selector("#ptDlg[open]")
        self.assertLessEqual(pg.evaluate("document.querySelector('#ptDlg .pt-sheet').getBoundingClientRect().width"), 390)
        pg.keyboard.press("Escape")
        for pid in ("dash", "orders", "products", "members", "promo", "reviews", "finance", "settings", "roles", "notice", "profile", "product-edit", "res-saved"):
            pg.evaluate("(i) => window.__PT__.jump(i)", pid)
            pg.wait_for_timeout(80)
            self.assertFalse(pg.evaluate("document.documentElement.scrollWidth > innerWidth + 1"), f"{pid} 手机宽度横向撑破")
            self.assertFalse(pg.evaluate("document.querySelector('#adApp').scrollWidth > document.querySelector('#adApp').clientWidth + 1"), f"{pid} 应用框内横向撑破")
            pg.evaluate("window.__PT__.sheet.close()")
        self.assertEqual(pg.errors, [])

    def test_desktop_1440_and_1920_layout(self):
        for w, mode, columns in ((1050, "wide", 1), (1440, "wide", 2), (1920, "wide", 3)):
            pg = self.open(w=w, h=900)
            self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.mode"), mode, w)
            self.assertFalse(pg.evaluate("document.documentElement.scrollWidth > innerWidth + 1"), w)
            box = pg.evaluate("(() => { const r = document.querySelector('#adApp').getBoundingClientRect(); return [r.left, r.right, r.height] })()")
            self.assertTrue(box[0] >= 0 and box[1] <= w and box[2] >= 560, box)
            cols = pg.evaluate("getComputedStyle(document.querySelector('.pt-layout')).gridTemplateColumns.split(' ').length")
            self.assertEqual(cols, columns, f"{w} 宽：放不下的侧栏改成抽屉，不占列，舞台保持 ≥ 960")
            for tab in ("dash", "orders", "finance"):
                self.nav(pg, tab)
                self.assertFalse(pg.evaluate("document.querySelector('#adScreen .ad-scroll').scrollWidth > document.querySelector('#adScreen .ad-scroll').clientWidth + 1"), f"{tab}@{w}：内容超出右边界")
        pg.click("[data-ad-w='390']")
        self.assertEqual(pg.evaluate("document.querySelector('#adApp').dataset.mode"), "narrow", "预览宽度工具可切到手机宽度")

    # ---------- 第二个示例：同一套机制长出不同的后台
    def test_service_example_has_its_own_menu_dashboard_and_flows(self):
        pg = self.open("service-admin")
        side = pg.locator("#adSide").text_content()
        for need in ("今日台", "预约日历", "员工排班", "客户档案", "服务项目", "核销记录", "门店设置"):
            self.assertIn(need, side)
        for no in ("订单", "商品", "购物车"):
            self.assertNotIn(no, side)
        self.assertGreater(pg.locator(".ad-feed li").count(), 2, "今天的预约日程")
        self.assertEqual(pg.evaluate("document.querySelector('#adSide').dataset.cid"), "AD-NAV-002", "示例默认深色侧栏")
        self.nav(pg, "redeem")
        self.assertEqual(self.rows(pg).count(), 20)
        pg.click(".ad-lbar [data-pt-sheet]")
        pg.wait_for_selector("#ptDlg[open] .ad-form")
        pg.fill("[data-ad-in=code]", "12ab")
        pg.fill("[data-ad-in=customer]", "测试客户")
        pg.select_option("[data-ad-in=service]", "体验课")
        pg.click("[data-ad-fsubmit]")
        self.assertEqual(pg.locator("[data-field=code] .err").inner_text(), "核销码是 6 位数字")
        pg.fill("[data-ad-in=code]", "123456")
        pg.click("[data-ad-fsubmit]")
        pg.wait_for_timeout(700)
        self.assertEqual(pg.evaluate("window.__PT__.data.redeems[0].customer"), "测试客户")
        self.assertEqual(pg.evaluate("window.__PT__.data.audit[0].what.includes('核销')"), True)
        pg.click("[data-role=front]") if pg.locator("[data-role=front]").count() else pg.evaluate("window.__PT__.setRole('front')")
        self.nav(pg, "shop-settings")
        self.assertIn("暂无权限", pg.locator("#adScreen").inner_text())
        self.assertEqual(pg.errors, [])

    # ---------- 渲染审计
    WALK = """\ndef walk(page, scan):
    out = []
    for pid in page.evaluate("window.__PT__.spec.pages.map(p => p.id)"):
        page.evaluate("(i) => window.__PT__.jump(i)", pid)
        page.wait_for_timeout(450)
        out.append((pid, scan()))
        page.evaluate("window.__PT__.sheet.close()")
    return out
"""

    @staticmethod
    def clean(items, lib_pages=()):
        """去掉不属于后台模板的已知项：组件库自己的状态色对比度（库的已知差距），以及整页都是库组件（blocks）的页面里的对比度、触控目标。其余一律算（外壳也算）。"""
        out = []
        for i in items:
            if i.split(":", 1)[0] in lib_pages:
                continue  # 整页都是库组件：对比度、触控目标、字重是组件库自己的（库的已知差距），不算后台模板
            m = re.match(r"^([\w-]+): text contrast too low: (.*)$", i)
            if not m:
                out.append(i)
                continue
            parts = [p.strip() for p in m.group(2).split(";")]
            parts = [p for p in parts if not re.fullmatch(r'\.(z-)?tag "[^"]*" 4\.[34]\d:1 on \d+,\d+,\d+', p)]
            if parts:
                out.append(f"{m.group(1)}: text contrast too low: " + "; ".join(parts))
        return out

    def run_audit(self, name, width, walk=True):
        cmd = [sys.executable, "-X", "utf8", str(HERE / "audit_rendered.py"), str(self.path[name]), "--library", "luz-kit", "--min-font", "12", "--width", str(width), "--height", "900"]
        if walk:
            wf = Path(self.tmp.name) / "walk_all_pages.py"
            wf.write_text(self.WALK, encoding="utf-8")
            cmd += ["--walk", str(wf)]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        out = r.stdout.strip()
        try:
            items = json.loads(out[out.index("["):]) if "[" in out else []
        except ValueError:
            items = [out]
        spec = load(EXAMPLES[name])
        lib_pages = {p["id"] for p in spec["pages"] if p.get("blocks") and not any(p.get(k) for k in ("list", "dashboard", "form", "settings", "detail", "result"))}
        return self.clean(items, lib_pages)

    def test_audit_rendered_passes_on_every_page_on_desktop_and_phone(self):
        for name, width in (("generic-admin", 1440), ("generic-admin", 390), ("service-admin", 1440), ("service-admin", 390)):
            with self.subTest(name=name, width=width):
                self.assertEqual(self.run_audit(name, width), [], f"{name}@{width}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
