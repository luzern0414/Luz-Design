"""界面细节规范：数据完整性、引用的范式与令牌真实存在、阈值与检查脚本一致、规则页由数据渲染且与数据一致、命令行输出。

    py -X utf8 scripts/test_ui_details.py
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_icon_image as cii  # noqa: E402
import context as ctx  # noqa: E402
import ui_details as ud  # noqa: E402

ROOT = HERE.parent
REFS = ROOT / "references"
DATA = ud.load()
PATTERNS = json.loads((REFS / "page-patterns.json").read_text(encoding="utf-8"))
PATH_DATA = json.loads((REFS / "design-path.json").read_text(encoding="utf-8"))
THEMES = json.loads((REFS / "themes.json").read_text(encoding="utf-8"))
PAGE = REFS / "ui-details.html"
SCOPES = {"method", "icons", "backgrounds", "cards"}
KEBAB = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
EXTERNAL_SCRIPTS = {"crawl_preflight.py"}


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = ud.main(argv)
        except SystemExit as e:  # argparse 报错
            code = int(e.code or 0)
    return code, out.getvalue(), err.getvalue()


def walk(node, path=""):
    """数据里的所有字符串及其位置。"""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def token_names() -> set[str]:
    """themes.json 里出现过的全部键名（任意层级），加上分组名。"""
    names: set[str] = {"dark", "elevation", "shared", "modules", "scale"}

    def collect(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                names.add(k)
                collect(v)
    collect(THEMES)
    return names


def page_text_sections() -> dict[str, int]:
    out = {}
    for lv, title, _ in ctx.headings(PAGE):
        if lv == 2:
            out[title] = len(ctx.section_text(PAGE, [title]).encode("utf-8"))
    return out


# ---------------------------------------------------------------- 数据

class DataTest(unittest.TestCase):
    def test_top_level_fields(self) -> None:
        for key in ("version", "title", "updated", "owner", "scope", "method_ref", "ownership", "think_chains", "icons", "backgrounds",
                    "cards", "rules", "sources", "basis", "page"):
            self.assertIn(key, DATA)
        self.assertEqual(DATA["title"], "界面细节规范")
        self.assertTrue((ROOT / DATA["method_ref"].split("#")[0]).is_file())

    def test_ids_are_unique_kebab_and_do_not_collide_with_the_pattern_library(self) -> None:
        ids = [r["id"] for r in DATA["rules"]]
        ids += [s["id"] for s in DATA["icons"]["systems"]] + [b["id"] for b in DATA["backgrounds"]["layers"]]
        ids += [b["id"] for b in DATA["backgrounds"]["items"]] + [f["id"] for f in DATA["cards"]["families"]]
        self.assertEqual(len(ids), len(set(ids)), [i for i in ids if ids.count(i) > 1])
        for i in ids:
            self.assertRegex(i, KEBAB)
        pattern_ids = {r["id"] for r in PATTERNS["rules"]} | {p["id"] for p in PATTERNS["paradigms"]} | {p["id"] for p in PATTERNS["pages"]}
        self.assertFalse(set(ids) & pattern_ids, set(ids) & pattern_ids)
        for i in ids:      # 检查文档的“生成时间”类元数据词会误伤标识符
            self.assertNotIn("generated", i.lower())

    def test_rule_shape_and_the_three_tiers(self) -> None:
        method = PATTERNS["method"]
        self.assertEqual(set(method["strength"]), {"must", "default", "hint"})
        self.assertEqual(set(method["deviation_format"]), {"rule", "why", "risk", "verify"})
        for r in DATA["rules"]:
            with self.subTest(rule=r["id"]):
                self.assertEqual(set(r) - {"tool"}, {"id", "scope", "text", "strength", "check", "evidence"})
                self.assertIn(r["scope"], SCOPES)
                self.assertIn(r["strength"], method["strength"])
                self.assertIn(r["check"], ud.CHECK_LABEL)
                self.assertTrue(r["text"].strip())
                self.assertTrue(r["evidence"], "每条规则至少一条证据")
                if r["check"] == "script":
                    self.assertTrue(r.get("tool"), "检查是脚本的规则要写明哪个脚本")
                if r.get("tool"):
                    self.assertTrue((HERE / r["tool"]).is_file(), r["tool"])
        by_scope = {s: [r for r in DATA["rules"] if r["scope"] == s] for s in SCOPES}
        for scope, rules in by_scope.items():
            self.assertTrue(any(r["strength"] == "must" for r in rules), scope)
            self.assertTrue(any(r["strength"] == "default" for r in rules), scope)

    def test_evidence_kinds_and_refs_resolve(self) -> None:
        kinds = set(PATTERNS["method"]["evidence_kinds"])
        vd_headings = {t for _, t, _ in ctx.headings(REFS / "visual-design.html")}
        pp_ids = {r["id"] for r in PATTERNS["rules"]} | {p["id"] for p in PATTERNS["paradigms"]} | {p["id"] for p in PATTERNS["pages"]} | {"method"}
        dp_ids = {p["id"] for p in PATH_DATA["phases"]} | {p["id"] for p in PATH_DATA["principles"]}
        playbook = (REFS / "imagegen-playbook.md").read_text(encoding="utf-8")
        skill_files = {"themes.json": REFS / "themes.json", "ui-ownership": REFS / "ui-ownership.md", "layout-inference": REFS / "layout-inference.md"}
        sys_standards = Path(r"D:\Codes\Luz-System\references\ui-standards.html")
        sys_headings = {t for _, t, _ in ctx.headings(sys_standards)} if sys_standards.is_file() else None
        seen = 0
        for r in DATA["rules"]:
            for e in r["evidence"]:
                seen += 1
                with self.subTest(rule=r["id"], ref=e["ref"]):
                    self.assertIn(e["kind"], kinds)
                    ref = e["ref"]
                    if e["kind"] == "user":
                        self.assertRegex(ref, r"^user:\d{4}-\d{2}-\d{2}$")
                    elif e["kind"] in ("rule", "example"):
                        self.assertIn(ref, DATA["sources"])
                        self.assertEqual(DATA["sources"][ref]["grade"], e["kind"])
                    else:   # skill
                        if ref == "skill:default":
                            continue
                        head, _, frag = ref.partition("#")
                        if head == "design:visual-design":
                            self.assertIn(frag, vd_headings)
                        elif head == "design:page-patterns":
                            self.assertIn(frag, pp_ids)
                        elif head == "design:design-path":
                            self.assertIn(frag, dp_ids)
                        elif head == "design:imagegen-playbook":
                            self.assertRegex(playbook, r"(?m)^#+ .*" + re.escape(frag))
                        elif head.startswith("design:"):
                            self.assertIn(head.removeprefix("design:"), skill_files)
                            self.assertTrue(skill_files[head.removeprefix("design:")].is_file())
                        elif head == "system:interaction-patterns":
                            if sys_headings is not None:
                                self.assertIn(frag, sys_headings)
                        else:
                            self.fail(f"未知的证据引用：{ref}")
        self.assertGreater(seen, 60)

    def test_sources_are_real_and_graded_honestly(self) -> None:
        for key, s in DATA["sources"].items():
            self.assertRegex(key, r"^icons-[abc]:SRC-\d{3}$")
            self.assertTrue(s["url"].startswith("https://"))
            self.assertIn(s["grade"], ("rule", "example"))
            self.assertTrue(s["title"] and s["caution"])
        # 只有 NN/g 的两篇是规则级证据
        rules = {k for k, s in DATA["sources"].items() if s["grade"] == "rule"}
        self.assertTrue(all("nngroup.com" in DATA["sources"][k]["url"] for k in rules), rules)
        self.assertEqual(len(rules), 2)
        used = {e["ref"] for r in DATA["rules"] for e in r["evidence"] if e["ref"].startswith("icons-")}
        self.assertFalse(used - set(DATA["sources"]))

    def test_sources_are_registered_in_the_experience_library(self) -> None:
        sources = {s["id"]: s for s in json.loads((ROOT / "experience" / "sources.json").read_text(encoding="utf-8"))["sources"]}
        for key, s in DATA["sources"].items():
            self.assertIn(s["experience"], sources, key)
            self.assertEqual(sources[s["experience"]]["url"].rstrip("/"), s["url"].rstrip("/"), key)
        used = {e["ref"] for r in DATA["rules"] for e in r["evidence"] if e["ref"].startswith("icons-")}
        self.assertEqual(used, set(DATA["sources"]), "每个登记的来源都被某条规则引用，没有孤儿")

    def test_basis_is_honest_about_what_the_sources_did_not_cover(self) -> None:
        text = json.dumps(DATA["basis"], ensure_ascii=False)
        for must_say in ("16 份资料没有一份给出数值", "本技能取值", "均未覆盖"):
            self.assertIn(must_say, text)
        for b in DATA["basis"]:
            self.assertIn(b["kind"], ud.BASIS_KIND)
        # 本技能取值的规则要在证据里带上 skill:default
        for rid in ("icon-gen-saturation", "icon-gen-palette", "bg-canvas-vs-surface", "card-columns-by-min-width"):
            rule = next(r for r in DATA["rules"] if r["id"] == rid)
            self.assertIn("skill:default", [e["ref"] for e in rule["evidence"]], rid)

    def test_referenced_paradigms_pages_and_tokens_exist(self) -> None:
        paradigms = {p["id"] for p in PATTERNS["paradigms"]}
        pages = {p["id"] for p in PATTERNS["pages"]}
        names = token_names()
        for f in DATA["cards"]["families"]:
            self.assertTrue(f["paradigms"], f["id"])
            for pid in f["paradigms"]:
                self.assertIn(pid, paradigms, f["id"])
            for pg in f["pages"]:
                self.assertIn(pg, pages, f["id"])
        holders = DATA["cards"]["families"] + DATA["backgrounds"]["layers"] + DATA["icons"]["systems"]
        count = 0
        for h in holders:
            for tok in h["tokens"]:
                count += 1
                self.assertIn(tok.split(".")[-1], names, f"{h['id']} 引用了 themes.json 里没有的令牌 {tok}")
                self.assertIn(tok.split(".")[0], names, tok)
        self.assertGreater(count, 40)

    def test_scripts_named_in_the_text_exist(self) -> None:
        text = "\n".join(s for _, s in walk({k: v for k, v in DATA.items() if k != "sources"}))
        for name in set(re.findall(r"[A-Za-z_]+\.py", text)):
            self.assertTrue((HERE / name).is_file() or name in EXTERNAL_SCRIPTS, name)


class IconColourTest(unittest.TestCase):
    def test_thresholds_match_the_checking_script(self) -> None:
        by_id = {t["id"]: t for t in DATA["icons"]["colour"]["thresholds"]}
        self.assertEqual(by_id["mean"]["limit"], cii.DEFAULTS["max_mean"])
        self.assertEqual(by_id["p90"]["limit"], cii.DEFAULTS["p90"])
        self.assertEqual(by_id["hot_share"]["limit"], cii.DEFAULTS["hot_share"])
        self.assertEqual(by_id["max_hues"]["limit"], cii.DEFAULTS["max_hues"])
        self.assertEqual(DATA["icons"]["colour"]["hot_s"], cii.DEFAULTS["hot_s"])
        self.assertEqual(set(by_id), {"mean", "p90", "hot_share", "max_hues"})
        for t in by_id.values():
            self.assertTrue(t["flag"].startswith("--"))

    def test_numbers_in_the_prose_match_the_thresholds(self) -> None:
        rule = next(r for r in DATA["rules"] if r["id"] == "icon-gen-saturation")["text"]
        for fragment in ("0.45", "0.65", "0.80", "3%", "2 个"):
            self.assertIn(fragment, rule)
        self.assertIn("本技能取值", DATA["icons"]["colour"]["metric"]["status"])
        self.assertIn("待样板图校准", DATA["icons"]["colour"]["metric"]["status"])

    def test_palette_numbers_match_the_script(self) -> None:
        rows = {r["role"]: r["light"] for r in DATA["icons"]["colour"]["palette"]["rows"]}
        for role, (s, v) in cii.PALETTE_SV.items():
            self.assertIn(f"S {s:.2f}", rows[role], role)
            self.assertIn(f"{v:.2f}", rows[role], role)
        figure = next(r for r in DATA["rules"] if r["id"] == "icon-gen-palette")["text"]
        self.assertIn(f"{cii.PALETTE_SV['图形'][0]}", figure)

    def test_prompt_block_is_pasteable(self) -> None:
        text = DATA["icons"]["colour"]["prompt"]["text"]
        for placeholder in ("{base}", "{mid}", "{figure}", "{line}"):
            self.assertIn(placeholder, text)
        for phrase in ("low-saturation", "65% HSB saturation", "no gradient highlights", "No text", "Transparent background", "clean anti-aliased edges"):
            self.assertIn(phrase, text)
        self.assertNotRegex(text, r"[\u4e00-\u9fff]")      # 整段是英文，可直接粘进提示词文件
        self.assertIn("验收", DATA["icons"]["colour"]["prompt"]["note"])

    def test_the_example_sample_is_flagged_as_unlabelled(self) -> None:
        self.assertIn("未经用户标注", DATA["icons"]["colour"]["sample"])
        self.assertTrue(DATA["icons"]["colour"]["calibration"])
        self.assertTrue(DATA["icons"]["colour"]["tuning"])


class BackgroundTest(unittest.TestCase):
    def test_every_theme_passes_the_layer_check(self) -> None:
        for tid in THEMES["themes"]:
            r = ud.layer_report(tid, DATA)
            self.assertFalse(r["problems"], (tid, r["problems"]))

    def test_the_observed_range_in_the_text_is_the_real_range(self) -> None:
        light, dark = [], []
        for tid in THEMES["themes"]:
            r = ud.layer_report(tid, DATA)
            light.append(r["light"]["delta"])
            dark.append(r["dark"]["delta"])
        observed = DATA["backgrounds"]["layer_check"]["observed"]
        self.assertIn(f"{min(light):.1f}–{max(light):.1f}", observed)
        self.assertIn(f"{min(dark):.1f}–{max(dark):.1f}", observed)

    def test_thresholds_in_the_text_match_the_data(self) -> None:
        lim = DATA["backgrounds"]["layer_check"]["thresholds"]
        rule = next(r for r in DATA["rules"] if r["id"] == "bg-canvas-vs-surface")["text"]
        self.assertIn(f"{lim['light_min']}", rule)
        self.assertIn(f"{lim['dark_min']:g}", rule)
        self.assertIn(f"{lim['hairline_below']:g}", rule)
        self.assertGreater(lim["dark_min"], lim["light_min"])

    def test_lstar_is_cie_lightness(self) -> None:
        self.assertAlmostEqual(ud.srgb_to_lstar("#FFFFFF"), 100.0, places=1)
        self.assertAlmostEqual(ud.srgb_to_lstar("#000000"), 0.0, places=1)
        self.assertAlmostEqual(ud.srgb_to_lstar("#777777"), 50.0, delta=0.6)

    def test_layers_and_items_have_what_the_brief_asks_for(self) -> None:
        self.assertEqual(len(DATA["backgrounds"]["layers"]), 4)
        for it in DATA["backgrounds"]["items"]:
            self.assertGreaterEqual(len(it["think"]), 2, it["id"])
            self.assertIn("不动", it["innovation_room"], it["id"])
            self.assertIn(it["strength"], ("must", "default", "hint"))


class CardTest(unittest.TestCase):
    def test_nine_families_with_every_field(self) -> None:
        fams = DATA["cards"]["families"]
        self.assertEqual([f["id"] for f in fams], ["card-product", "card-store", "card-member", "card-coupon", "card-order", "card-metric",
                                                   "card-content", "card-campaign", "card-entry"])
        for f in fams:
            with self.subTest(family=f["id"]):
                for key in ("name", "role", "purpose", "paradigms", "pages", "fields", "dedup", "image", "actions", "states", "min_width",
                            "avoid", "think", "innovation_room", "tokens"):
                    self.assertIn(key, f)
                self.assertGreaterEqual(len(f["think"]), 2)
                self.assertIn("不动", f["innovation_room"])
                self.assertGreater(f["min_width"]["web"], 0)
                self.assertTrue(f["min_width"]["mini"] is None or f["min_width"]["mini"] > 0)
                self.assertGreaterEqual(len(f["fields"]), 3)
                self.assertTrue(f["states"])

    def test_icon_systems_have_the_three_categories(self) -> None:
        systems = DATA["icons"]["systems"]
        self.assertEqual([s["id"] for s in systems], ["icon-control", "icon-entry-block", "icon-gen-deco"])
        for s in systems:
            for key in ("where", "grid", "colour", "tone", "count", "produce", "check", "think", "innovation_room"):
                self.assertTrue(s[key], (s["id"], key))
            self.assertGreaterEqual(len(s["think"]), 2)

    def test_grid_examples_follow_the_formula(self) -> None:
        self.assertEqual(ud.columns(351, 12, 136), 2)       # 小程序 375 宽，边距 12
        self.assertEqual(ud.columns(296, 8, 136), 2)        # 320 宽：最小宽 136 仍是两列
        self.assertEqual(ud.columns(296, 8, 160), 1)        # 取 160 会掉成一列：本页取 136 的理由
        self.assertEqual(ud.columns(1152, 16, 180), 5)      # 后台 1440 宽、侧栏 240：一行 5 张指标卡
        self.assertEqual(ud.columns(1152, 16, 320), 3)
        self.assertEqual(ud.columns(1200, 24, 280), 4)
        self.assertEqual(ud.columns(100, 16, 320), 1)
        for ex in DATA["cards"]["grid"]["examples"]:
            g = ud.grid_example(ex)
            self.assertGreaterEqual(g["columns"], 1)
            self.assertGreaterEqual(g["card_width"], g["min"] if g["columns"] > 1 or g["container"] >= g["min"] else 0)
        mini = DATA["cards"]["grid"]["mini_note"]
        self.assertIn("144", mini)
        self.assertEqual((320 - 2 * 12 - 8) // 2, 144)
        self.assertLessEqual(136, 144)
        # 小程序 320–430 宽、边距 12–16、间距 8–12：最小宽 136 恒为两列，不会掉成一列也不会变三列
        for width in range(320, 431, 10):
            for margin, gap in ((12, 8), (12, 12), (16, 8), (16, 12)):
                self.assertEqual(ud.columns(width - 2 * margin, gap, 136), 2, (width, margin, gap))

    def test_rules_cover_the_nng_boundaries(self) -> None:
        text = " ".join(r["text"] for r in DATA["rules"] if r["scope"] == "cards")
        for phrase in ("浏览", "异质", "列表", "整卡可点", "圆角", "等高", "最小卡宽", "状态"):
            self.assertIn(phrase, text)
        self.assertIn("icons-a:SRC-005", json.dumps(DATA["rules"], ensure_ascii=False))

    def test_the_numbers_the_page_shares_with_the_visual_spec_agree(self) -> None:
        # 以视觉设计规范为准：卡片圆角 12、大卡 16、内层块 8、标签 4；内边距 16；卡间距 16
        rule = next(r for r in DATA["rules"] if r["id"] == "card-radius-shadow-padding")["text"]
        for fragment in ("圆角 12", "大卡 16", "内层块 8", "标签 4", "内边距 16", "卡间距 16"):
            self.assertIn(fragment, rule)
        vd = (REFS / "visual-design.html").read_text(encoding="utf-8")
        self.assertIn("圆角 12", vd)
        self.assertIn("线宽 2", vd)
        control = next(r for r in DATA["rules"] if r["id"] == "icon-control-svg-token")["text"]
        for fragment in ("24 栅格", "线宽 2", "16 像素 1.75"):
            self.assertIn(fragment, control)
        hard_floor = " ".join(f["text"] for f in PATH_DATA["hard_floor"])
        self.assertIn("2 像素线性", hard_floor)       # 设计路径的底线：控件图标 2 像素线性矢量


# ---------------------------------------------------------------- 规则页

class PageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_page_is_rendered_from_the_data(self) -> None:
        self.assertEqual(self.html, ud.render_html(DATA))
        code, out, _ = run(["render", "--check"])
        self.assertEqual(code, 0, out)

    def test_contract_of_a_rule_page(self) -> None:
        self.assertRegex(self.html, r"<title>界面细节规范</title>")
        self.assertEqual(self.html.count("<h1>"), 1)
        self.assertIn('href="guidelines.css"', self.html)
        for sid in ("scope", "workflow", "rules", "platform-matrix", "examples", "output-contract", "quality-gates", "handoff"):
            self.assertIn(f'<section id="{sid}" data-rule-id="details-{sid}"', self.html)
            self.assertIn(f"<!-- SECTION:{sid}:START", self.html)
            self.assertIn(f"<!-- SECTION:{sid}:END -->", self.html)
        self.assertNotIn("raw/", self.html)
        self.assertEqual(len(re.findall(r"<h2 ", self.html)), 8)

    def test_passes_the_skills_rule_page_validator(self) -> None:
        import validate_skill as vs
        errors: list[str] = []
        vs.validate_rule_page(PAGE, "details", 0, "界面细节规范", errors)
        self.assertEqual(errors, [])

    def test_scope_section_avoids_the_banned_words(self) -> None:
        scope = ctx.section_text(PAGE, ["适用范围"])
        for banned in ("日期", "无需构建", "可直接编辑", "入口", "说明"):
            self.assertNotIn(banned, scope)

    def test_every_id_in_the_data_is_on_the_page(self) -> None:
        for r in DATA["rules"]:
            self.assertIn(f"<code>{r['id']}</code>", self.html, r["id"])
        for f in DATA["cards"]["families"]:
            self.assertIn(f"<code>{f['id']}</code>", self.html, f["id"])
        for s in DATA["icons"]["systems"]:
            self.assertIn(f"<code>{s['id']}</code>", self.html, s["id"])
        for i in DATA["backgrounds"]["items"]:
            self.assertIn(f"<code>{i['id']}</code>", self.html, i["id"])
        for pid in {p for f in DATA["cards"]["families"] for p in f["paradigms"]}:
            self.assertIn(f"<code>{pid}</code>", self.html, pid)

    def test_thresholds_and_prompt_are_on_the_page(self) -> None:
        text = ctx.section_text(PAGE, ["核心规则"])
        for t in DATA["icons"]["colour"]["thresholds"]:
            self.assertIn(t["flag"].split("，")[0].split(" ")[0], text)
        self.assertIn("{base}", text)
        self.assertIn("65% HSB saturation", text)
        self.assertIn("check_icon_image.py", text)
        for q in [q for f in DATA["cards"]["families"] for q in f["think"]]:
            self.assertIn(q, text)
        for f in DATA["cards"]["families"]:
            self.assertIn(f["innovation_room"], text)

    def test_text_size_fits_one_rule_card(self) -> None:
        sizes = page_text_sections()
        total = sum(sizes.values())
        self.assertGreater(total, 8 * 1024)
        self.assertLessEqual(total, 35 * 1024, sizes)
        self.assertLessEqual(sizes["核心规则"], 31 * 1024, sizes)

    def test_no_stray_latin_letters_in_prose(self) -> None:
        # 规则页正文的拉丁字母只许出现在 <code>、<kbd> 里（渲染函数已经保证，这里再核一遍）
        body = re.sub(r"<(code|kbd)>.*?</\1>", "", self.html, flags=re.S)
        body = re.sub(r"<(script|style|svg)\b.*?</\1>", "", body, flags=re.S)
        body = re.sub(r"<!--.*?-->|<[^>]+>", "", body, flags=re.S)
        self.assertNotRegex(body, r"[A-Za-z]")


# ---------------------------------------------------------------- 命令行

class CommandTest(unittest.TestCase):
    def test_list_and_show(self) -> None:
        code, out, _ = run(["list"])
        self.assertEqual(code, 0)
        for token in ("card-product", "icon-control", "bg-layers", "icon-gen-saturation"):
            self.assertIn(token, out)
        for key, expect in (("icon-gen-saturation", "0.45"), ("card-order", "订单卡"), ("icon-entry-block", "入口图标块"), ("bg-dark", "dark 映射"),
                            ("thresholds", "--max-mean"), ("palette", "底块"), ("basis", "本技能取值"), ("method", "范式是词汇")):
            code, out, _ = run(["show", key])
            self.assertEqual(code, 0, key)
            self.assertIn(expect, out, key)
            self.assertNotIn("`", out)
        self.assertEqual(run(["show", "no-such-id"])[0], 2)

    def test_layers_command(self) -> None:
        code, out, _ = run(["layers", "--all"])
        self.assertEqual(code, 0, out)
        self.assertIn("ui details layers: ok", out)
        self.assertIn("b2b-graphite", out)
        code, out, _ = run(["layers", "--theme", "xiangcai"])
        self.assertEqual(code, 0)
        self.assertEqual(run(["layers", "--theme", "nope"])[0], 2)

    def test_layers_command_flags_a_theme_with_no_separation(self) -> None:
        bad = dict(THEMES["themes"]["xiangcai"], canvas="#FFFFFF")
        original = ud.THEMES_PATH
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            doc = {"themes": {"xiangcai": bad}, "shared": THEMES["shared"]}
            path = Path(tmp) / "themes.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            ud.THEMES_PATH = path
            try:
                r = ud.layer_report("xiangcai", DATA)
            finally:
                ud.THEMES_PATH = original
        self.assertTrue(r["problems"])
        self.assertIn("ΔL*", r["problems"][0])

    def test_grid_command(self) -> None:
        code, out, _ = run(["grid", "--min", "136", "--gap", "12", "--width", "375", "--margin", "12"])
        self.assertEqual(code, 0)
        self.assertIn("2 列", out)
        code, out, _ = run(["grid", "--min", "180", "--gap", "16", "--content", "1152"])
        self.assertIn("5 列", out)
        code, out, _ = run(["grid"])
        self.assertEqual(code, 0)
        self.assertIn("1 列", out)       # 示例里最小宽取 160 的那一行

    def test_deviation_follows_the_pattern_library_format(self) -> None:
        must = next(r["id"] for r in DATA["rules"] if r["strength"] == "must")
        code, _, err = run(["deviation", must, "--why", "a", "--risk", "b", "--verify", "c"])
        self.assertEqual(code, 2)
        self.assertIn("must", err)
        default = next(r["id"] for r in DATA["rules"] if r["strength"] == "default")
        code, out, _ = run(["deviation", default, "--why", "品牌要求", "--risk", "饱和度偏高", "--verify", "check_icon_image.py"])
        self.assertEqual(code, 0)
        for label in ("偏离说明", "为什么偏离", "风险", "怎么验证"):
            self.assertIn(label, out)
        code, out, _ = run(["deviation", default, "--why", "a", "--risk", "b", "--verify", "c", "--json"])
        self.assertEqual(set(json.loads(out)), set(PATTERNS["method"]["deviation_format"]))
        hint = next(r["id"] for r in DATA["rules"] if r["strength"] == "hint")
        code, _, err = run(["deviation", hint, "--why", "a", "--risk", "b", "--verify", "c"])
        self.assertEqual(code, 0)
        self.assertIn("hint", err)
        code, _, err = run(["deviation", "my-own-rule", "--why", "a", "--risk", "b", "--verify", "c"])
        self.assertEqual(code, 0)
        self.assertIn("不在", err)
        self.assertEqual(run(["deviation", default, "--why", " ", "--risk", "b", "--verify", "c"])[0], 2)
        # 页面范式库的规则也认得
        pp_must = next(r["id"] for r in PATTERNS["rules"] if r["strength"] == "must")
        self.assertEqual(run(["deviation", pp_must, "--why", "a", "--risk", "b", "--verify", "c"])[0], 2)

    def test_render_without_flags_prints_the_page(self) -> None:
        code, out, _ = run(["render"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("<!doctype html>"))


if __name__ == "__main__":
    unittest.main()
