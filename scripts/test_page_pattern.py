"""页面范式库：数据完整性、规则页与数据一致、首页方案分配与检查、渲染检查。

    py -X utf8 scripts/test_page_pattern.py
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import page_pattern as pp  # noqa: E402
from style_match import dock_grid  # noqa: E402

ROOT = HERE.parent
DATA = pp.load()
KINDS = {"rule", "example", "user", "convention", "skill"}
LIBS = ["vant4", "vant-weapp", "tdesign-miniprogram", "weui", "wechat-native"]
PIXEL = re.compile(r"\d+(?:\.\d+)?\s*(?:px|rpx|像素)", re.I)

REQUIRED_PARADIGMS = ["dock-grid", "single-column-list", "two-column-card-grid", "masonry", "feed", "bento", "top-tabs", "side-category",
                      "immersive-hero", "modular-sections", "banner-carousel", "horizontal-scroller", "search-header", "notice-bar", "ranking-list",
                      "member-card-hero", "workbench", "status-card", "equal-grid", "flex-grid"]
REQUIRED_TYPES = ["food-chain", "ecommerce", "local-booking", "b2b-quote-ticket", "content-community", "brand-campaign", "enterprise-internal",
                  "course-education", "membership-benefits"]
REQUIRED_PAGES = ["home", "category", "product-list-search", "product-detail", "cart-checkout", "order-list", "order-detail", "mine", "store-select",
                  "booking", "activity-seckill", "activity-group-buy", "activity-lottery", "activity-coupon-center", "member-benefits",
                  "message-center", "login-auth", "result-empty-error"]
REQUIRED_ZONES = ["header-context", "search", "banner", "dock", "status-card", "marketing", "feed", "tabbar", "mine-list", "in-page"]
REQUIRED_RULES = ["context-in-header-only", "search-top-not-dock", "account-in-mine-only", "order-home-state-card-only", "dock-core-parallel-only",
                  "dock-no-tabbar-dup", "one-destination-once", "marketing-max-two", "no-fill-dock", "first-module-answers-return-task", "five-questions",
                  "modules-backend-switchable"]
LOW_PAGES = ["order-detail", "activity-seckill", "activity-lottery", "activity-coupon-center"]


def run(argv: list[str]) -> tuple[int, str]:
    buf, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        try:
            code = pp.main(argv)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 2
            if isinstance(exc.code, str):
                err.write(exc.code)
    return code, buf.getvalue() + err.getvalue()


def ent(fn: str, name: str, type_: str, entry: str, dest: str, freq: str = "high", category: str = "core", **extra) -> dict:
    return {"fn": fn, "name": name, "type": type_, "category": category, "entry": entry, "destination": dest, "freq": freq, **extra}


def plan_of(rows: list[dict], type_id: str = "food-chain", tabbar: list[dict] | None = None, width: int = 375) -> dict:
    doc = {"entrances": rows, "tabbar": tabbar if tabbar is not None else [{"name": "首页", "destination": "home"}, {"name": "点单", "destination": "P03"}, {"name": "订单", "destination": "P04"}, {"name": "我的", "destination": "P10"}]}
    return pp.make_plan(pp.make_brief(None, doc, type_id, DATA, width), DATA)


def mods(spec: dict) -> dict:
    return {m["id"]: m for m in spec["modules"]}


def rejected(spec: dict) -> dict:
    return {r["fn"]: r for r in spec["rejected"]}


def errors_of(spec: dict) -> list[dict]:
    return [f for f in pp.check_spec(spec, DATA) if f["level"] == "error"]


def test_explicit_settings_and_sidebar_homes_stay_out_of_homepage():
    spec = plan_of([
        ent("FN-001", "修改密码", "account", "in-page", "/settings/account"),
        ent("FN-002", "员工管理", "task", "sidebar", "/staff"),
    ])
    assert rejected(spec)["FN-001"]["goes_to"] == "in-page"
    assert rejected(spec)["FN-002"]["goes_to"] == "sidebar"


# ---------------------------------------------------------------- 数据完整性

class DataTest(unittest.TestCase):
    def test_top_level_and_strength_tiers(self) -> None:
        self.assertEqual(DATA["version"], 1)
        self.assertEqual(set(DATA["strength"]), {"must", "default", "hint"})
        for key in ("paradigms", "app_types", "entry_zones", "function_types", "pages", "rules", "density", "sources", "method"):
            self.assertIn(key, DATA)

    def test_ids_are_unique_in_each_collection(self) -> None:
        for key in ("paradigms", "app_types", "entry_zones", "function_types", "pages", "rules"):
            ids = [i["id"] for i in DATA[key]]
            self.assertEqual(len(ids), len(set(ids)), key)

    def test_required_members_exist(self) -> None:
        have = {k: {i["id"] for i in DATA[k]} for k in ("paradigms", "app_types", "entry_zones", "pages", "rules")}
        for want, key in ((REQUIRED_PARADIGMS, "paradigms"), (REQUIRED_TYPES, "app_types"), (REQUIRED_PAGES, "pages"), (REQUIRED_ZONES, "entry_zones"), (REQUIRED_RULES, "rules")):
            self.assertEqual(set(want) - have[key], set(), key)
        self.assertEqual({f["id"] for f in DATA["function_types"]}, set(pp.entrances_contract().schema()["enums"]["type"]))

    def test_paradigm_shape_and_references(self) -> None:
        ptypes, pids = {t["id"] for t in DATA["app_types"]}, {p["id"] for p in DATA["paradigms"]}
        for p in DATA["paradigms"]:
            self.assertIn(p["role"], {"page-skeleton", "module"}, p["id"])
            self.assertIn(p["confidence"], {"high", "medium", "low"}, p["id"])
            self.assertTrue(p["summary"] and p["structure"] and p["tagline"] and p["watch"], p["id"])
            self.assertTrue(3 <= len(p["think"]) <= 6, f"{p['id']} think {len(p['think'])}")
            self.assertTrue(len(p["innovation_room"]) > 20, p["id"])
            self.assertEqual(set(p["components"]), set(LIBS), p["id"])
            self.assertTrue(all(p["components"][lib] for lib in LIBS), p["id"])
            self.assertTrue(set(p["fits"]) <= ptypes, p["id"])
            self.assertTrue(set(p["combine_with"]) <= pids, p["id"])
            self.assertTrue(p["params"] and p["avoid"] and p["evidence"], p["id"])
            for q in p["params"]:
                self.assertIn(q["strength"], DATA["strength"], f"{p['id']} {q['name']}")
                self.assertTrue(q["evidence"], f"{p['id']} {q['name']}")
        self.assertEqual([p["role"] for p in DATA["paradigms"] if p["role"] == "page-skeleton"], ["page-skeleton"])

    def test_app_types_and_pages_reference_known_ids(self) -> None:
        pids = {p["id"] for p in DATA["paradigms"]}
        types = {t["id"] for t in DATA["app_types"]}
        for t in DATA["app_types"]:
            self.assertTrue(set(t["home"]["modules"]) <= pids, t["id"])
            self.assertTrue(set(t["home"]["optional"]) <= set(t["home"]["modules"]), t["id"])
            self.assertTrue(t["tab_bar"]["count_hint"] and t["tab_bar"]["typical"] and t["avoid"] and t["variations"] and t["evidence"], t["id"])
            self.assertIsInstance(t["home"]["first_screen_max"], int)
            self.assertIn(t["home"]["dock_policy"], {"optional", "avoid"}, t["id"])
        for p in DATA["pages"]:
            self.assertTrue(set(p["applies_to"]) <= types, p["id"])
            self.assertTrue(p["blocks"] and p["choose_rules"] and p["dedup_rules"] and p["think"] and p["needs_from_system"], p["id"])
            self.assertTrue(3 <= len(p["think"]) <= 6, p["id"])
            self.assertTrue(len(p["innovation_room"]) > 20, p["id"])
            self.assertEqual(set(p["states"]), {"loading", "empty", "error", "other"}, p["id"])
            orders = [b["order"] for b in p["blocks"]]
            self.assertEqual(orders, sorted(orders), p["id"])
            for b in p["blocks"]:
                self.assertIn(b["paradigm"], pids, f"{p['id']} {b['id']}")
                self.assertIsInstance(b["required"], bool)
                self.assertTrue(set(b["components"]) <= set(LIBS) | {"vant4", "vant-weapp"}, p["id"])
            for r in p["choose_rules"]:
                self.assertIn(r["strength"], DATA["strength"], p["id"])

    def test_thin_pages_are_marked_low_and_say_the_order_is_inferred(self) -> None:
        pages = {p["id"]: p for p in DATA["pages"]}
        for pid in LOW_PAGES:
            self.assertEqual(pages[pid]["confidence"], "low", pid)
        for p in DATA["pages"]:
            if p["confidence"] == "low":
                self.assertTrue("推演" in p["order_basis"] or "资料未覆盖" in p["order_basis"], f"{p['id']} 低置信页要写明区块顺序是推演")
        self.assertEqual(pages["order-detail"]["order_basis"], "推演自状态机或惯例，待样板页验证")

    def test_rules_and_zones(self) -> None:
        rules = {r["id"] for r in DATA["rules"]}
        for r in DATA["rules"]:
            self.assertIn(r["strength"], DATA["strength"], r["id"])
            self.assertIn(r["check"], {"script", "rendered", "manual"}, r["id"])
            self.assertTrue(r["evidence"] and r["text"] and r["scope"], r["id"])
            self.assertTrue(set(r.get("check_also", [])) <= {"script", "rendered", "manual"}, r["id"])
        musts = {r["id"]: r for r in DATA["rules"]}
        for rid in ("context-in-header-only", "search-top-not-dock", "account-in-mine-only", "order-home-state-card-only", "dock-core-parallel-only", "dock-no-tabbar-dup",
                    "one-destination-once", "marketing-max-two"):
            self.assertEqual(musts[rid]["strength"], "must", rid)
        for rid in ("no-fill-dock", "first-module-answers-return-task", "five-questions", "modules-backend-switchable"):
            self.assertEqual(musts[rid]["strength"], "default", rid)
        for z in DATA["entry_zones"]:
            self.assertTrue(set(z["allowed_function_types"]) <= set(pp.entrances_contract().schema()["enums"]["type"]), z["id"])
            self.assertTrue(set(z["rules"]) <= rules, z["id"])

    def test_every_evidence_entry_resolves_and_is_honest(self) -> None:
        sources = DATA["sources"]
        seen = 0

        def walk(node, where):
            nonlocal seen
            if isinstance(node, dict):
                if "kind" in node and "ref" in node and "note" in node:
                    seen += 1
                    self.assertIn(node["kind"], KINDS, where)
                    base = node["ref"].split("#")[0]
                    self.assertIn(base, sources, f"{where}: {node['ref']}")
                    grade = sources[base]["grade"]
                    self.assertNotEqual(grade, "shell", f"{where}: 空壳或离题来源不能当证据 {node['ref']}")
                    expect = {"rule": "rule", "example": "example", "user": "user", "convention": "convention", "skill": "skill"}[node["kind"]]
                    self.assertEqual(grade, expect, f"{where}: kind {node['kind']} 与来源等级 {grade} 不符 {node['ref']}")
                    if node["kind"] == "convention":
                        self.assertIn("惯例，资料未核对", node["note"], where)
                    if node["kind"] in ("rule", "example"):
                        self.assertTrue(sources[base]["url"].startswith("http"), where)
                for k, v in node.items():
                    walk(v, f"{where}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{where}[{i}]")

        for key in ("paradigms", "app_types", "pages", "rules", "density", "function_types"):
            walk(DATA[key], key)
        self.assertGreater(seen, 200)

    def test_no_pixel_numbers_without_a_source(self) -> None:
        """数值要么有规则或公式或本技能取值作依据，要么不写；只有实例做依据的像素数不得写成规则。"""
        def ok(evidence: list[dict]) -> bool:
            return any(e["kind"] in ("rule", "skill") for e in evidence)

        for p in DATA["paradigms"]:
            for q in p["params"]:
                if PIXEL.search(q["value"]):
                    self.assertTrue(ok(q["evidence"]), f"{p['id']} {q['name']}: {q['value']}")
            self.assertIsNone(PIXEL.search(p["summary"] + p["structure"] + p["innovation_room"]), p["id"])
        for r in DATA["rules"]:
            if PIXEL.search(r["text"]):
                self.assertTrue(ok(r["evidence"]), r["id"])
        for p in DATA["pages"]:
            blob = json.dumps([p["blocks"], p["adaptive"], p["antipatterns"], p["states"], p["choose_rules"], p["innovation_room"]], ensure_ascii=False)
            self.assertIsNone(PIXEL.search(blob), p["id"])
        for t in DATA["app_types"]:
            self.assertIsNone(PIXEL.search(json.dumps(t, ensure_ascii=False)), t["id"])

    def test_density_values_have_a_basis(self) -> None:
        for group in ("home", "tabbar"):
            for key, item in DATA["density"][group].items():
                self.assertIn(item["strength"], DATA["strength"], key)
                self.assertTrue(item["basis"] and item["evidence"], key)
        self.assertEqual(DATA["density"]["home"]["marketing_modules_max"]["value"], 2)
        self.assertEqual(DATA["density"]["home"]["marketing_modules_max"]["strength"], "must")

    def test_schema_command_uses_system_contract(self) -> None:
        code, out = run(["show", "entrances"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), pp.entrances_contract().schema())


# ---------------------------------------------------------------- 规则页

class RulePageTest(unittest.TestCase):
    PAGE = ROOT / "references" / "page-patterns.html"

    def test_every_paradigm_and_page_id_appears_in_the_page(self) -> None:
        text = self.PAGE.read_text(encoding="utf-8")
        for item in DATA["paradigms"] + DATA["pages"]:
            self.assertIn(f"<code>{item['id']}</code>", text, item["id"])
        for r in DATA["rules"]:
            self.assertIn(f"<code>{r['id']}</code>", text, r["id"])
        for t in DATA["app_types"]:
            self.assertIn(f"<code>{t['id']}</code>", text, t["id"])

    def test_page_passes_the_rule_page_contract(self) -> None:
        import validate_skill as vs
        errors: list[str] = []
        vs.validate_rule_page(self.PAGE, "patterns", 0, "页面范式库", errors)
        self.assertEqual(errors, [])

    def test_rendered_rule_text_fits_a_rule_card(self) -> None:
        import context
        total = sum(len(context.section_text(self.PAGE, [h]).encode("utf-8")) for h in ("适用范围", "工作流程", "核心规则", "平台矩阵", "案例样本", "输出契约", "质量门禁", "交接规则"))
        self.assertLess(total, 35 * 1024, f"规则文本 {total} 字节，超过规则卡的 35 KB")
        self.assertGreater(total, 20 * 1024)


# ---------------------------------------------------------------- 查询

class QueryTest(unittest.TestCase):
    def test_list_and_show(self) -> None:
        for what in ("paradigms", "types", "pages", "rules", "zones"):
            code, out = run(["list", what])
            self.assertEqual(code, 0, what)
            self.assertTrue(out.strip())
        code, out = run(["show", "dock-grid"])
        self.assertEqual(code, 0)
        for needle in ("选它前要问的问题", "给创新留的空间", "金刚栅格"):
            self.assertIn(needle, out)
        code, out = run(["show", "order-detail"])
        self.assertIn("推演自状态机或惯例，待样板页验证", out)
        self.assertIn("设计这一页前要问", out)
        self.assertEqual(run(["show", "method"])[0], 0)
        self.assertEqual(run(["show", "entrances"])[0], 0)
        self.assertEqual(run(["show", "no-such-id"])[0], 2)

    def test_show_by_alias_and_prefixed_id(self) -> None:
        self.assertIn("masonry", run(["show", "流式不等高"])[1])
        code, out = run(["show", "zone:feed"])
        self.assertIn("区域 feed", out)
        self.assertNotIn("范式 feed", out)

    def test_recommend_uses_dock_grid(self) -> None:
        code, out = run(["recommend", "--type", "ecommerce", "--functions", "9", "--tabs", "4", "--width", "375"])
        self.assertEqual(code, 0)
        want = dock_grid(9, 4, 375)
        self.assertIn(f"{want['columns']} 列 {want['rows']} 行", out)
        code, out = run(["recommend", "--type", "ecommerce", "--functions", "3"])
        self.assertIn("不用金刚栅格", out)
        self.assertIn("entry-cards", out)
        code, out = run(["recommend", "--type", "enterprise-internal", "--functions", "8"])
        self.assertIn("通常不用金刚栅格", out)
        code, out = run(["recommend", "--type", "ecommerce", "--tabs", "6"])
        self.assertIn("退回 System", out)
        self.assertEqual(run(["recommend", "--type", "nope"])[0], 2)


# ---------------------------------------------------------------- 入口表与简报

class BriefTest(unittest.TestCase):
    def test_brief_refuses_a_wallet_misplaced_in_system_home_definition(self) -> None:
        rows = [ent("FN-001", "我的优惠券", "account", "home", "P01", summary=True)]
        with self.assertRaisesRegex(SystemExit, "我的优惠券.*摘要"):
            pp.make_brief(None, {"entrances": rows}, "ecommerce", DATA)

    def test_brief_flags_unmapped_features_and_unknown_rows(self) -> None:
        features = {"modules": [{"id": "M01", "name": "报餐"}], "features": [
            {"id": "FN-001", "module": "M01", "name": "提交报餐", "surface": "miniprogram"},
            {"id": "FN-002", "module": "M01", "name": "取消报餐", "surface": "miniprogram"},
            {"id": "FN-003", "module": "M01", "name": "员工管理", "surface": "web-admin"}]}
        brief = pp.make_brief(features, {"entrances": [ent("FN-001", "去报餐", "task", "home", "P03"), ent("FN-099", "幽灵", "task", "home", "P99")]}, "enterprise-internal", DATA)
        self.assertEqual([u["fn"] for u in brief["unmapped_features"]], ["FN-002"])
        text = "\n".join(brief["warnings"])
        self.assertIn("FN-099", text)
        self.assertIn("没有入口行", text)
        self.assertEqual(brief["features"]["frontend"], 2)

    def test_brief_command_writes_file_and_derives_tabbar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            e = Path(tmp) / "e.json"
            e.write_text(json.dumps({"entrances": [ent("FN-1", "点单", "task", "tab", "P03"), ent("FN-2", "我的", "account", "tab", "P10")]}, ensure_ascii=False), encoding="utf-8")
            out = Path(tmp) / "brief.json"
            code, _ = run(["brief", "--entrances", str(e), "--type", "food-chain", "--out", str(out)])
            self.assertEqual(code, 0)
            brief = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(brief["tab_count"], 2)
            self.assertIn("think", brief)
            code, text = run(["plan", "--brief", str(out), "--out", str(Path(tmp) / "spec.json")])
            self.assertEqual(code, 0)
            self.assertTrue((Path(tmp) / "spec.json").is_file())


# ---------------------------------------------------------------- plan

BASE_ROWS = [
    ent("FN-001", "选择门店", "context", "context", "P20", category="info"),
    ent("FN-002", "同城配送切换", "context", "context", "P21", category="info"),
    ent("FN-003", "搜索商品", "search", "home", "P22"),
    ent("FN-004", "去点单", "task", "tab", "P03"),
    ent("FN-005", "我的订单", "order", "tab", "P04"),
    ent("FN-006", "进行中订单", "status", "home", "P05", category="info"),
    ent("FN-007", "新人礼券", "marketing", "home", "P40", "mid", "marketing", image=True, limited=True),
    ent("FN-008", "限时折扣", "marketing", "home", "P41", "mid", "marketing", image=True),
    ent("FN-009", "新品专场", "marketing", "home", "P42", "mid", "marketing"),
    ent("FN-010", "我的会员", "account", "mine", "P50", "mid", "info", summary=True),
    ent("FN-011", "我的收藏", "account", "mine", "P51", "low", "aux"),
    ent("FN-012", "优惠券", "account", "mine", "P52", "mid", "aux"),
    ent("FN-013", "门店公告", "content", "home", "P60", "mid", "info"),
    ent("FN-014", "新品推荐", "content", "home", "P61", "mid", "info"),
    ent("FN-015", "预约点餐", "task", "home", "P70"),
    ent("FN-016", "拼单", "task", "home", "P71"),
    ent("FN-017", "团餐", "task", "home", "P72", "mid"),
    ent("FN-018", "礼品卡", "task", "home", "P73", "mid"),
    ent("FN-019", "外卖专送", "task", "home", "P74"),
    ent("FN-020", "开发票", "tool", "mine", "P80", "low", "aux"),
    ent("FN-021", "新人礼券入口", "marketing", "home", "P40", "mid", "marketing"),
    ent("FN-022", "点单", "task", "home", "P03"),
]


class PlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = plan_of(copy.deepcopy(BASE_ROWS))
        self.mods = mods(self.spec)
        self.rej = rejected(self.spec)

    def test_account_functions_go_to_mine_and_home_keeps_one_summary(self) -> None:
        for fn in ("FN-010", "FN-011", "FN-012"):
            self.assertEqual(self.rej[fn]["goes_to"], "mine-list", fn)
            self.assertEqual(self.rej[fn]["code"], "account")
        self.assertIn("归我的", self.rej["FN-011"]["reason"])
        summary = [i for i in self.mods["status-card"]["items"] if i.get("summary")]
        self.assertEqual(len(summary), 1)
        self.assertIs(summary[0]["entrance"], False)
        self.assertEqual(summary[0]["destination"], "")
        placed = {i["fn"] for m in self.spec["modules"] for i in m["items"] if not i.get("summary")}
        self.assertFalse({"FN-010", "FN-011", "FN-012", "FN-020"} & placed)
        self.assertEqual(self.rej["FN-020"]["goes_to"], "mine-list")

    def test_store_and_delivery_are_in_the_header_and_never_in_the_dock(self) -> None:
        header = self.mods["search-header"]
        self.assertEqual(self.spec["modules"][0]["id"], "search-header")
        self.assertEqual({i["name"] for i in header["items"]}, {"选择门店", "同城配送切换", "搜索商品"})
        self.assertEqual({i["zone"] for i in header["items"]}, {"header-context", "search"})
        for i in self.mods["dock-grid"]["items"]:
            self.assertEqual(i["type"], "task")

    def test_orders_appear_only_as_the_in_progress_state_card(self) -> None:
        self.assertEqual(self.rej["FN-005"]["code"], "tab-duplicate")
        order_like = [i for m in self.spec["modules"] for i in m["items"] if i["type"] == "order"]
        self.assertEqual(order_like, [])
        card = [i for i in self.mods["status-card"]["items"] if i["fn"] == "FN-006"]
        self.assertEqual(len(card), 1)
        self.assertTrue(card[0]["state_card"])
        spec = plan_of([ent("FN-1", "全部订单", "order", "mine", "P90")], tabbar=[{"name": "首页", "destination": "home"}, {"name": "我的", "destination": "P10"}])
        self.assertNotIn("status-card", mods(spec))
        self.assertEqual(rejected(spec)["FN-1"]["code"], "order")

    def test_duplicates_and_tabbar_repeats_are_removed(self) -> None:
        for fn in ("FN-004", "FN-022"):
            self.assertEqual(self.rej[fn]["code"], "tab-duplicate", fn)
        self.assertEqual(self.rej["FN-021"]["code"], "duplicate-destination")
        self.assertEqual(self.rej["FN-021"]["kind"], "dropped")
        dests = [pp.norm_dest(i["destination"]) for m in self.spec["modules"] for i in m["items"] if i["destination"]]
        self.assertEqual(len(dests), len(set(dests)))
        self.assertEqual(errors_of(self.spec), [])

    def test_marketing_is_at_most_two_modules_and_dock_layout_follows_the_formula(self) -> None:
        marketing = [m for m in self.spec["modules"] if m["zone"] in ("banner", "marketing")]
        self.assertLessEqual(len(marketing), 2)
        dock = self.mods["dock-grid"]
        want = dock_grid(len(dock["items"]), dock["longest_label"], 375)
        self.assertEqual((dock["layout"]["columns"], dock["layout"]["rows"], dock["layout"]["pages"]), (want["columns"], want["rows"], want["pages"]))
        many = [ent(f"FN-{i:03d}", f"活动{i}", "marketing", "home", f"M{i}", "mid", "marketing", image=True) for i in range(12)]
        spec = plan_of(many, tabbar=[{"name": "首页", "destination": "home"}, {"name": "我的", "destination": "P10"}])
        self.assertLessEqual(len([m for m in spec["modules"] if m["zone"] in ("banner", "marketing")]), 2)
        self.assertEqual(len(mods(spec)["banner-carousel"]["items"]), 3)
        self.assertTrue(any(r["code"] == "marketing-overflow" for r in spec["rejected"]))
        self.assertTrue(any("marketing-max-two" in w for w in spec["warnings"]))

    def test_dock_is_not_padded_when_there_are_few_entrances(self) -> None:
        rows = [ent("FN-1", "预约", "task", "home", "P1"), ent("FN-2", "拼单", "task", "home", "P2"), ent("FN-3", "团餐", "task", "home", "P3")]
        spec = plan_of(rows)
        self.assertNotIn("dock-grid", mods(spec))
        self.assertIn("entry-cards", mods(spec))
        self.assertTrue(any("no-fill-dock" in w for w in spec["warnings"]))
        self.assertEqual(errors_of(spec), [])

    def test_low_frequency_entrances_do_not_get_the_dock_and_raise_a_warning(self) -> None:
        rows = [ent(f"FN-{i}", f"业务{i}", "task", "home", f"P{i}") for i in range(5)] + [ent("FN-9", "冷门", "task", "home", "P9", "low", "aux")]
        spec = plan_of(rows)
        self.assertNotIn("冷门", [i["name"] for i in mods(spec)["dock-grid"]["items"]])
        self.assertTrue(any("低频入口上首页" in w for w in spec["warnings"]))

    def test_workbench_types_put_quick_entries_in_the_workbench(self) -> None:
        rows = [ent("FN-1", "新建工单", "task", "home", "P1"), ent("FN-2", "报价", "task", "home", "P2"), ent("FN-3", "待办", "status", "home", "P3", category="info")]
        spec = plan_of(rows, "b2b-quote-ticket", tabbar=[{"name": "工作台", "destination": "home"}, {"name": "我的", "destination": "P10"}])
        self.assertIn("workbench", mods(spec))
        self.assertNotIn("dock-grid", mods(spec))

    def test_ledger_says_where_every_function_went_and_why(self) -> None:
        ledger = {r["fn"]: r for r in self.spec["ledger"]}
        self.assertEqual(len(ledger), len(BASE_ROWS))
        self.assertEqual((ledger["FN-001"]["to"], ledger["FN-001"]["kind"]), ("search-header", "placed"))
        self.assertIn("全局上下文", ledger["FN-001"]["reason"])
        self.assertIn("归我的", ledger["FN-011"]["reason"])
        self.assertEqual(ledger["FN-021"]["kind"], "dropped")
        self.assertEqual(ledger["FN-004"]["to"], "标签栏")

    def test_membership_types_show_the_account_summary_as_the_member_card(self) -> None:
        rows = [ent("FN-1", "我的会员", "account", "mine", "P50", "mid", "info", summary=True), ent("FN-2", "购卡", "task", "home", "P2"), ent("FN-3", "续卡", "task", "home", "P3")]
        spec = plan_of(rows, "membership-benefits", tabbar=[{"name": "首页", "destination": "home"}, {"name": "我的", "destination": "P10"}])
        first = spec["modules"][0]
        self.assertEqual(first["id"], "member-card-hero")
        self.assertTrue(first["items"][0]["summary"])
        self.assertEqual(errors_of(spec), [])

    def test_first_screen_limit_and_order(self) -> None:
        ids = [m["id"] for m in self.spec["modules"]]
        self.assertLess(ids.index("search-header"), ids.index("status-card"))
        self.assertLess(ids.index("status-card"), ids.index("banner-carousel"))
        self.assertLess(ids.index("dock-grid"), ids.index("banner-carousel"))
        self.assertEqual(ids[-1], "feed")
        self.assertEqual(sum(1 for m in self.spec["modules"] if m["first_screen"]), self.spec["first_screen_max"])


# ---------------------------------------------------------------- check

def clean_spec() -> dict:
    return copy.deepcopy(plan_of(copy.deepcopy(BASE_ROWS)))


def item(fn: str, name: str, type_: str, zone: str, dest: str, **extra) -> dict:
    return {"fn": fn, "name": name, "type": type_, "zone": zone, "destination": dest, "freq": "high", **extra}


class CheckTest(unittest.TestCase):
    def test_a_planned_spec_passes_and_the_command_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            path.write_text(json.dumps(clean_spec(), ensure_ascii=False), encoding="utf-8")
            code, out = run(["check", str(path)])
            self.assertEqual(code, 0, out)
            self.assertIn("page pattern check: ok", out)

    def rules_hit(self, spec: dict) -> set[str]:
        return {f["rule"] for f in errors_of(spec)}

    def test_duplicate_destinations_are_reported_across_modules_and_the_tabbar(self) -> None:
        spec = clean_spec()
        spec["modules"].append({"id": "horizontal-scroller", "zone": "marketing", "items": [item("FN-90", "再来一个", "marketing", "marketing", "P70")], "first_screen": False})
        self.assertIn("one-destination-once", self.rules_hit(spec))
        spec = clean_spec()
        spec["modules"][1]["items"].append(item("FN-91", "回首页点单", "task", "feed", "P03"))
        self.assertIn("one-destination-once", self.rules_hit(spec))

    def test_forbidden_types_in_the_dock_are_reported(self) -> None:
        for type_, name, rule in (("account", "我的收藏", "dock-core-parallel-only"), ("context", "选择门店", "context-in-header-only"),
                                  ("order", "全部订单", "order-home-state-card-only"), ("search", "搜索", "search-top-not-dock")):
            spec = clean_spec()
            dock = next(m for m in spec["modules"] if m["id"] == "dock-grid")
            dock["items"].append(item("FN-99", name, type_, "dock", "P99"))
            self.assertIn(rule, self.rules_hit(spec), type_)

    def test_account_entrance_on_home_is_reported_but_the_summary_is_fine(self) -> None:
        spec = clean_spec()
        spec["modules"][2]["items"].append(item("FN-98", "我的会员", "account", "status-card", "P50"))
        self.assertIn("account-in-mine-only", self.rules_hit(spec))
        self.assertEqual(errors_of(clean_spec()), [])

    def test_dock_that_repeats_a_tab_is_reported(self) -> None:
        spec = clean_spec()
        dock = next(m for m in spec["modules"] if m["id"] == "dock-grid")
        dock["items"][0]["destination"] = "P04"
        self.assertIn("dock-no-tabbar-dup", self.rules_hit(spec))
        spec = clean_spec()
        dock = next(m for m in spec["modules"] if m["id"] == "dock-grid")
        dock["items"][0]["name"] = "订单"
        self.assertIn("dock-no-tabbar-dup", self.rules_hit(spec))

    def test_marketing_over_two_modules_and_too_many_banner_frames(self) -> None:
        spec = clean_spec()
        spec["modules"].append({"id": "horizontal-scroller", "zone": "marketing", "items": [item("FN-80", "秒杀", "marketing", "marketing", "P81")], "first_screen": False})
        self.assertIn("marketing-max-two", self.rules_hit(spec))
        spec = clean_spec()
        banner = next(m for m in spec["modules"] if m["id"] == "banner-carousel")
        banner["items"] += [item(f"FN-7{i}", f"帧{i}", "marketing", "banner", f"B{i}") for i in range(3)]
        self.assertIn("carousel-frames-and-pause", self.rules_hit(spec))

    def test_dock_formula_count_and_fill_rules(self) -> None:
        spec = clean_spec()
        dock = next(m for m in spec["modules"] if m["id"] == "dock-grid")
        dock["layout"] = {"columns": 5, "rows": 2, "pages": 1}
        self.assertIn("dock-layout-by-formula", self.rules_hit(spec))
        spec = clean_spec()
        dock = next(m for m in spec["modules"] if m["id"] == "dock-grid")
        dock["items"] = dock["items"][:3]
        dock.pop("layout", None)
        self.assertIn("no-fill-dock", self.rules_hit(spec))
        spec = clean_spec()
        dock = next(m for m in spec["modules"] if m["id"] == "dock-grid")
        dock["items"] += [item(f"FN-6{i}", f"业务{i}", "task", "dock", f"D{i}") for i in range(8)]
        dock.pop("layout", None)
        self.assertIn("dock-count-cap", self.rules_hit(spec))

    def test_module_count_limits_and_tabbar_range(self) -> None:
        spec = clean_spec()
        for m in spec["modules"]:
            m["first_screen"] = True
        self.assertIn("first-screen-modules-max", self.rules_hit(spec))
        spec = clean_spec()
        spec["tabbar"]["count"] = 6
        self.assertIn("tabbar-count-2-to-5", self.rules_hit(spec))
        spec = clean_spec()
        spec["tabbar"]["count"] = 5
        findings = pp.check_spec(spec, DATA)
        self.assertIn("tabbar-prefer-4", {f["rule"] for f in findings if f["level"] == "warn"})
        self.assertEqual(errors_of(spec), [])

    def test_deviation_notes_downgrade_default_rules_only_when_complete(self) -> None:
        spec = clean_spec()
        for m in spec["modules"]:
            m["first_screen"] = True
        spec["deviations"] = [{"rule": "first-screen-modules-max", "why": "首页就是点单页", "risk": "首屏拥挤", "verify": "样板页 375 宽截图"}]
        findings = pp.check_spec(spec, DATA)
        self.assertEqual([f for f in findings if f["level"] == "error"], [])
        self.assertTrue([f for f in findings if f["level"] == "deviated"])
        spec["deviations"][0]["risk"] = ""
        self.assertIn("first-screen-modules-max", self.rules_hit(spec))
        spec = clean_spec()
        spec["modules"].append({"id": "horizontal-scroller", "zone": "marketing", "items": [], "first_screen": False})
        spec["modules"].append({"id": "feed2", "zone": "marketing", "items": [], "first_screen": False})
        spec["deviations"] = [{"rule": "marketing-max-two", "why": "大促", "risk": "无", "verify": "无"}]
        hit = self.rules_hit(spec)
        self.assertIn("deviation-note-required", hit)
        self.assertIn("marketing-max-two", hit)

    def test_check_command_exit_code_is_one_on_violation(self) -> None:
        spec = clean_spec()
        spec["modules"][2]["items"].append(item("FN-98", "我的会员", "account", "status-card", "P50"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            code, out = run(["check", str(path)])
            self.assertEqual(code, 1)
            self.assertIn("ERROR [account-in-mine-only]", out)


# ---------------------------------------------------------------- check-page

def snap_item(i: int, name: str, target: str, zone: str = "other", nested: bool = False, row: int = 0, row_text: str = "", crumb: bool = False) -> dict:
    return {"id": i, "tag": "a", "role": "", "name": name, "target": target, "cls": "", "nested": nested, "isRow": False, "rowParent": 1 if nested else 0,
            "rowId": row, "rowText": row_text, "x": 0, "y": i * 10, "w": 80, "h": 40, "zone": zone, "crumb": crumb}


class PageLogicTest(unittest.TestCase):
    def test_same_destination_twice_is_reported_with_both_names(self) -> None:
        items = [snap_item(1, "立即点餐", "#/order"), snap_item(2, "点餐", "#/order", "dock"), snap_item(3, "我的", "#/mine", "tabbar")]
        dups, ignored = pp.find_duplicates(items)
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0]["names"], ["点餐", "立即点餐"])
        self.assertEqual(ignored, 0)

    def test_the_same_action_inside_repeated_list_rows_is_not_a_duplicate(self) -> None:
        items = [snap_item(i, "加入购物车", "", nested=True, row=100 + i, row_text=f"商品{i} 价格 加入购物车") for i in range(1, 4)]
        dups, ignored = pp.find_duplicates(items)
        self.assertEqual(dups, [])
        self.assertEqual(ignored, 3)

    def test_repeated_rows_that_hold_nothing_but_the_action_are_still_duplicates(self) -> None:
        items = [snap_item(i, "点餐", "#/order", nested=True, row=100 + i, row_text="点餐") for i in (1, 2)]
        dups, _ = pp.find_duplicates(items)
        self.assertEqual(len(dups), 1)

    def test_a_breadcrumb_is_a_path_not_an_entrance(self) -> None:
        # Audit 014 (A-09): the detail page's breadcrumb 全部客户 and the sidebar item 全部客户 were reported as one entrance twice.
        sidebar_and_crumb = [snap_item(1, "全部客户", "", crumb=False), snap_item(2, "全部客户", "", crumb=True)]
        self.assertEqual(pp.find_duplicates(sidebar_and_crumb), ([], 0))
        same_target = [snap_item(1, "全部客户", "#/customers"), snap_item(2, "全部客户", "#/customers", crumb=True)]
        self.assertEqual(pp.find_duplicates(same_target), ([], 0))
        self.assertEqual(pp.find_duplicates([snap_item(1, "全部客户", "", crumb=True), snap_item(2, "全部客户", "", crumb=True)]), ([], 0), "a path is never counted")

    def test_a_card_or_button_in_the_page_that_repeats_the_sidebar_item_is_still_reported(self) -> None:
        items = [snap_item(1, "全部客户", "#/customers", "other"), snap_item(2, "全部客户", "#/customers", crumb=True), snap_item(3, "全部客户", "#/customers")]
        dups, _ = pp.find_duplicates(items)
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0]["count"], 2, "the sidebar item and the in-page card; the breadcrumb is not one of them")
        named = [snap_item(1, "全部客户", ""), snap_item(2, "全部客户", "", crumb=True), snap_item(3, "全部客户", "")]
        self.assertEqual(pp.find_duplicates(named)[0][0]["kind"], "重复的同名入口")

    def test_dock_with_tab_names_and_account_words_is_reported_on_home_only(self) -> None:
        items = [snap_item(1, "点餐", "#/order", "dock"), snap_item(2, "会员", "#/member", "dock"), snap_item(3, "全部订单", "#/orders", "dock"),
                 snap_item(4, "选择门店", "#/shop", "dock"), snap_item(5, "预约", "#/book", "dock"), snap_item(6, "点餐", "#/order", "tabbar")]
        found = pp.dock_findings(items, "home")
        kinds = " ".join(f["kind"] for f in found)
        self.assertIn("标签栏同名项", kinds)
        self.assertIn("账户类", kinds)
        self.assertIn("订单类", kinds)
        self.assertIn("上下文类", kinds)
        self.assertEqual(len(pp.dock_findings(items, "mine")), 1)
        for word in ("会员", "收藏", "优惠券", "积分", "储值", "地址", "设置", "客服"):
            self.assertTrue(pp.dock_findings([snap_item(1, f"我的{word}", "#/x", "dock")], "home"), word)


def browser_ready() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pp.open_browser(pw).close()
        return True
    except Exception:  # noqa: BLE001
        return False


HAS_BROWSER = browser_ready()
STYLE = ("<style>body{margin:0;font:14px sans-serif}.dock{display:grid;grid-template-columns:repeat(4,1fr)}.dock a{display:block;text-align:center;padding:8px}"
         ".tabbar{position:fixed;bottom:0;left:0;right:0;display:flex;background:#fff;border-top:1px solid #ccc}.tabbar a{flex:1;text-align:center;padding:10px}"
         ".card{border:1px solid #ddd;margin:8px;padding:8px}</style>")
ICON = '<svg width="20" height="20"><circle cx="10" cy="10" r="8"/></svg><br>'
CARDS = '<div class="list">' + "".join(f'<div class="card"><b>{n}</b> {p}元 <button>加入购物车</button></div>' for n, p in (("拿铁", 18), ("美式", 15), ("摩卡", 20))) + "</div>"
TABBAR = '<nav class="tabbar"><a href="#/home">首页</a><a href="#/order">点餐</a><a href="#/mine">我的</a></nav>'


def page(banner: str, dock: list[tuple[str, str]]) -> str:
    cells = "".join(f'<a href="{href}">{ICON}{name}</a>' for name, href in dock)
    return (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{STYLE}</head>'
            f'<body><main><div class="banner">{banner}</div><div class="dock">{cells}</div>{CARDS}</main>{TABBAR}</body></html>')


def admin_page(side_item: str, crumb: str, body: str = "") -> str:
    """后台详情页：左侧栏一项、内容区顶部面包屑、一个页内按钮。"""
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>body{margin:0;font:14px sans-serif;display:flex}aside{width:200px}main{flex:1}.card{border:1px solid #ddd;margin:8px;padding:8px}</style></head>'
            f'<body><aside><nav class="ad-nav" aria-label="主菜单">{side_item}<a class="ad-ni" href="#/orders">订单</a></nav></aside>'
            f'<main>{crumb}<h1>客户档案</h1><button>编辑</button>{body}</main></body></html>')


@unittest.skipUnless(HAS_BROWSER, "没有可用的浏览器（Edge 或 Playwright 的 Chromium），跳过渲染检查")
class CheckPageTest(unittest.TestCase):
    def check(self, html: str, *extra: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            path.write_text(html, encoding="utf-8")
            return run(["check-page", str(path), "--settle", "200", *extra])

    def test_a_page_with_repeated_entrances_is_reported(self) -> None:
        html = page('<a href="#/order">立即点餐</a>', [("点餐", "#/order"), ("预约", "#/book"), ("会员", "#/member"), ("优惠券", "#/coupon"), ("我的", "#/mine")])
        code, out = self.check(html)
        self.assertEqual(code, 1, out)
        problems = json.loads(out)
        kinds = {p["kind"] for p in problems}
        self.assertIn("重复目的地", kinds)
        self.assertTrue(any("标签栏同名项" in k for k in kinds))
        self.assertTrue(any("账户类" in k for k in kinds))
        dup = next(p for p in problems if p["kind"] == "重复目的地" and p["target"] == "#/order")
        self.assertEqual(dup["count"], 3)

    def test_a_clean_page_passes_and_list_rows_do_not_count(self) -> None:
        html = page('<a href="#/promo">新人礼券</a>', [("预约", "#/book"), ("拼单", "#/group"), ("外卖", "#/ship"), ("团餐", "#/team")])
        code, out = self.check(html)
        self.assertEqual(code, 0, out)
        self.assertIn("check page: ok", out)

    def test_a_breadcrumb_that_names_the_sidebar_item_is_not_a_duplicate_entrance(self) -> None:
        for crumb in ('<div class="ad-crumb" id="adCrumb"><button type="button" data-pt-back="1">全部客户</button> / <b aria-current="page">客户档案</b></div>',
                      '<nav aria-label="面包屑"><a href="#/customers">全部客户</a> / <span>客户档案</span></nav>',
                      '<ol class="el-breadcrumb"><li><a href="#/customers">全部客户</a></li><li>客户档案</li></ol>'):
            for side in ('<button class="ad-ni" aria-label="全部客户">全部客户</button>', '<a class="ad-ni" href="#/customers">全部客户</a>'):
                with self.subTest(crumb=crumb[:30], side=side[:30]):
                    code, out = self.check(admin_page(side, crumb))
                    self.assertEqual(code, 0, out)

    def test_a_card_in_the_page_that_repeats_the_sidebar_item_is_still_reported_with_a_breadcrumb_present(self) -> None:
        crumb = '<nav aria-label="面包屑"><a href="#/customers">全部客户</a> / <span>客户档案</span></nav>'
        side = '<a class="ad-ni" href="#/customers">全部客户</a>'
        code, out = self.check(admin_page(side, crumb, '<div class="card"><a href="#/customers">全部客户</a></div>'))
        self.assertEqual(code, 1, out)
        problem = json.loads(out)[0]
        self.assertEqual((problem["kind"], problem["target"], problem["count"]), ("重复目的地", "#/customers", 2))
        side_name = '<button class="ad-ni">全部客户</button>'
        code, out = self.check(admin_page(side_name, crumb, '<div class="card"><button>全部客户</button></div>'))
        self.assertEqual(code, 1, out)
        self.assertEqual(json.loads(out)[0]["kind"], "重复的同名入口")

    def test_mine_role_allows_account_words_in_a_grid(self) -> None:
        html = page('<a href="#/promo">新人礼券</a>', [("优惠券", "#/coupon"), ("积分", "#/points"), ("收藏", "#/fav"), ("地址", "#/addr")])
        self.assertEqual(self.check(html, "--role", "mine")[0], 0)
        self.assertEqual(self.check(html)[0], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
