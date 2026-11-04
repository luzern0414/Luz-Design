"""设计路径与思考链：数据完整性、引用的规则卡与脚本真实存在、规则页由数据渲染且与数据一致、命令行输出。

    py -X utf8 scripts/test_design_path.py
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import design_path as dp  # noqa: E402

ROOT = HERE.parent
DATA = dp.load()
PATTERNS = dp.load(dp.PATTERNS_PATH)
CARDS = json.loads((ROOT / "references" / "cards.json").read_text(encoding="utf-8"))["cards"]
PAGE = ROOT / "references" / "design-path.html"
PHASE_IDS = [f"P{i}" for i in range(10)]
REQUIRED_TOOLS = ["positioning", "first-landing", "entry-ownership", "five-questions", "paradigm-four", "density-test", "deletion-test",
                  "three-second", "conflict-order", "deviation-note", "signature-budget", "reverse-check", "when-to-innovate"]
EXTERNAL_SCRIPTS = {"crawl_preflight.py", "project.py", "luz-crawl.mjs"}
BACKTICK = re.compile(r"`([^`]+)`")


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = dp.main(argv)
        except SystemExit as e:  # argparse 报错
            code = int(e.code or 0)
    return code, out.getvalue(), err.getvalue()


def strings(node, path=""):
    """数据里的所有字符串及其位置。"""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


# ---------------------------------------------------------------- 数据

class DataTest(unittest.TestCase):
    def test_top_level_fields(self) -> None:
        for key in ("version", "principles", "hard_floor", "decision_order", "phases", "thinking_tools", "deviation_template", "signature_budget",
                    "worked_example", "surfaces", "project_mode", "page", "basis"):
            self.assertIn(key, DATA, key)
        self.assertEqual(DATA["version"], 1)

    def test_phase_ids_are_consecutive(self) -> None:
        self.assertEqual([p["id"] for p in DATA["phases"]], PHASE_IDS)

    def test_every_phase_is_complete(self) -> None:
        for p in DATA["phases"]:
            with self.subTest(phase=p["id"]):
                for field in ("name", "purpose", "inputs", "chain", "actions", "outputs", "checks", "commands", "may_deviate", "handoff", "pitfalls"):
                    self.assertTrue(p.get(field), f"{p['id']} 缺 {field}")
                self.assertGreaterEqual(len(p["chain"]), 5, "思考链不少于 5 条")
                for c in p["chain"]:
                    self.assertGreaterEqual(len(c), 14, f"思考链条目太短：{c}")
                self.assertGreaterEqual(sum(1 for c in p["chain"] if "？" in c), 3, "思考链要以可回答的问题为主")
                for a in p["actions"]:
                    self.assertTrue(a["do"].strip() and a["tool"].strip(), a)
                for o in p["outputs"]:
                    self.assertTrue(o["file"].strip() and o["what"].strip(), o)
                for x in p["pitfalls"]:
                    self.assertTrue(x["symptom"].strip() and x["cause"].strip() and x["fix"].strip(), x)
                self.assertGreaterEqual(len(p["checks"]), 2)

    def test_chain_mentions_only_existing_tools(self) -> None:
        tool_ids = {t["id"] for t in DATA["thinking_tools"]}
        for p in DATA["phases"]:
            for c in p["chain"]:
                for ref in BACKTICK.findall(c):
                    if ref.endswith(".py"):
                        self.assertTrue((Path(__file__).resolve().parent / ref).is_file(), f"{p['id']} 思考链引用了不存在的脚本 {ref}")
                        continue
                    self.assertIn(ref, tool_ids, f"{p['id']} 思考链引用了不存在的工具 {ref}")

    def test_thinking_tools(self) -> None:
        ids = [t["id"] for t in DATA["thinking_tools"]]
        self.assertEqual(len(ids), len(set(ids)))
        for need in REQUIRED_TOOLS:
            self.assertIn(need, ids)
        for t in DATA["thinking_tools"]:
            with self.subTest(tool=t["id"]):
                self.assertTrue(t["name"].strip() and t["when"].strip() and t["example"] is not None)
                self.assertGreaterEqual(len(dp.steps_of(t)), 2)
        self.assertGreaterEqual(sum(1 for t in DATA["thinking_tools"] if t.get("show_example") and t["example"]), 4)

    def test_five_questions_follow_the_pattern_library(self) -> None:
        tool = next(t for t in DATA["thinking_tools"] if t["id"] == "five-questions")
        canonical = dp.resolve_pp(tool["canonical"])
        self.assertEqual(len(tool["steps"]), len(canonical))

    def test_ids_are_unique_across_kinds(self) -> None:
        ids = [x["id"] for kind in ("phases", "thinking_tools", "principles", "hard_floor") for x in DATA[kind]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_principles_use_the_three_tiers(self) -> None:
        tiers = {p["strength"] for p in DATA["principles"]}
        self.assertEqual(tiers, set(PATTERNS["strength"]))
        by_id = {p["id"]: p for p in DATA["principles"]}
        for must in ("function-first", "hard-floor", "approval-gates", "tiers-and-deviation"):
            self.assertEqual(by_id[must]["strength"], "must")
        self.assertEqual(len(DATA["hard_floor"]), 7)

    def test_decision_order_is_the_agreed_one(self) -> None:
        self.assertEqual(DATA["decision_order"], ["功能", "无障碍与稳定", "一致", "清晰与密度", "美观", "个性"])
        self.assertEqual(set(DATA["decision_notes"]), set(DATA["decision_order"]))

    def test_deviation_template_matches_the_pattern_library_fields(self) -> None:
        self.assertEqual(DATA["deviation_template"]["fields"], ["规则", "为什么偏离", "风险", "怎么验证"])
        self.assertEqual(set(PATTERNS["method"]["deviation_format"]), {"rule", "why", "risk", "verify"})

    def test_signature_budget(self) -> None:
        s = DATA["signature_budget"]
        self.assertIn("1–3", s["rule"])
        self.assertGreaterEqual(len(s["examples"]), 2)

    def test_worked_example_walks_every_phase_and_deviates_with_a_real_rule(self) -> None:
        steps = DATA["worked_example"]["steps"]
        self.assertEqual([s["phase"] for s in steps], PHASE_IDS)
        for s in steps:
            self.assertTrue(s["ask"].strip() and s["answer"].strip() and s["deviation"].strip())
        deviated = [s for s in steps if s["deviation"] != "—"]
        self.assertGreaterEqual(len(deviated), 1)
        rules = {r["id"]: r for r in PATTERNS["rules"]}
        for s in deviated:
            named = [rid for rid in rules if rid in s["deviation"]]
            self.assertTrue(named, f"{s['phase']} 的偏离没有写规则 id")
            for rid in named:
                self.assertEqual(rules[rid]["strength"], "default", f"{rid} 不是 default，不许偏离")
                for word in ("为什么", "风险", "验证"):
                    self.assertIn(word, s["deviation"])

    def test_example_names_resolve(self) -> None:
        text = " ".join(s["answer"] for s in DATA["worked_example"]["steps"])
        boards = {b["id"] for b in json.loads((ROOT / "references" / "style-boards.json").read_text(encoding="utf-8"))["boards"]}
        themes = json.loads((ROOT / "references" / "themes.json").read_text(encoding="utf-8"))["themes"]
        libs = json.loads((ROOT / "references" / "component-libraries.json").read_text(encoding="utf-8"))["libraries"]
        self.assertIn("fresh-organic", boards)
        self.assertIn("fresh-organic", text)
        self.assertIn("milk-tea", themes)
        self.assertIn("tdesign-miniprogram", libs)

    def test_surfaces(self) -> None:
        self.assertEqual(set(DATA["surfaces"]), set(dp.SURFACES))
        for sid, s in DATA["surfaces"].items():
            self.assertTrue(s["name"].strip())
            self.assertGreaterEqual(len(s["phase_notes"]), 4, sid)
            for ph in s["phase_notes"]:
                self.assertIn(ph, PHASE_IDS)

    def test_surface_libraries_exist(self) -> None:
        libs = json.loads((ROOT / "references" / "component-libraries.json").read_text(encoding="utf-8"))["libraries"]
        for sid in ("miniprogram", "admin"):
            note = DATA["surfaces"][sid]["phase_notes"]["P5"]
            names = [x for x in re.split(r"[、；\s]+", note) if re.fullmatch(r"[a-z]+(-[a-z]+)*", x) and x != "vant"]
            self.assertTrue(names)
            for n in names:
                self.assertTrue(n in libs or any(n == lib_id.split("-")[0] for lib_id in libs), f"{n} 不在组件库登记表里")

    def test_project_mode(self) -> None:
        m = DATA["project_mode"]
        self.assertEqual(m["stage"], "design")
        for field in ("reads", "writes", "stop_points", "phase_to_doc"):
            self.assertTrue(m[field])
        self.assertGreaterEqual(len(m["stop_points"]), 3)

    def test_basis_is_honest(self) -> None:
        kinds = {b["kind"] for b in DATA["basis"]}
        self.assertEqual(kinds, set(dp.BASIS_KIND))
        for b in DATA["basis"]:
            self.assertTrue(b["item"].strip() and b["note"].strip())

    def test_detail_system_leaves_the_numbers_to_the_visual_rules(self) -> None:
        p6 = DATA["phases"][6]
        self.assertEqual({r["slot"] for r in p6["pending_refs"]}, {"图标颜色饱和度上限", "背景分层", "卡片家族"})
        text = " ".join(p6["chain"])
        self.assertEqual(text.count("见界面细节规范"), 3)
        self.assertEqual(text.count("细则待补"), 0)
        self.assertNotRegex(text, r"\d+\s*%")


# ---------------------------------------------------------------- 引用

class ReferenceTest(unittest.TestCase):
    def pattern_ids(self) -> set[str]:
        ids: set[str] = set()
        for key in ("paradigms", "app_types", "pages", "rules", "entry_zones", "function_types"):
            ids |= {x["id"] for x in PATTERNS.get(key, [])}
        return ids

    def check_ref(self, ref: str) -> None:
        kind, _, val = ref.partition(":")
        self.assertIn(kind, {"card", "script", "file", "pp", "ext", "out"}, ref)
        if kind == "card":
            self.assertIn(val, CARDS, ref)
        elif kind == "script":
            name = val.split()[0]
            self.assertTrue((HERE / name).is_file(), f"scripts/{name} 不存在")
        elif kind == "file":
            self.assertTrue((ROOT / val).is_file(), f"{val} 不存在")
        elif kind == "pp":
            dp.resolve_pp(ref)
        elif kind == "ext":
            first = val.split(" ")[0]
            if Path(first).anchor and Path(first).parent.parent.exists():
                self.assertTrue(Path(first).is_file(), f"{first} 不存在")
            self.assertIn(Path(first).name, EXTERNAL_SCRIPTS)
        elif kind == "out":
            self.assertTrue(val.startswith("raw/"), ref)

    def test_every_action_tool_resolves(self) -> None:
        for p in DATA["phases"]:
            for a in p["actions"]:
                with self.subTest(phase=p["id"], tool=a["tool"]):
                    self.check_ref(a["tool"])

    def test_every_command_names_a_real_script(self) -> None:
        for p in DATA["phases"]:
            for cmd in p["commands"]:
                with self.subTest(phase=p["id"], cmd=cmd):
                    m = re.match(r"(?:py|python) -X utf8 (\S+\.py)", cmd)
                    self.assertTrue(m, cmd)
                    path = m.group(1)
                    if path.startswith("scripts/"):
                        self.assertTrue((ROOT / path).is_file(), path)
                    elif Path(path).anchor and Path(path).parent.parent.exists():
                        self.assertTrue(Path(path).is_file(), path)

    def test_backticked_scripts_and_cards_in_text_exist(self) -> None:
        for where, text in strings(DATA):
            for ref in BACKTICK.findall(text):
                for token in re.findall(r"[A-Za-z_]+\.py", ref):
                    self.assertTrue((HERE / token).is_file() or token in EXTERNAL_SCRIPTS, f"{where}: {token}")
                if ref.startswith("interface-"):
                    self.assertIn(ref, CARDS, where)
        for where, text in strings(DATA["phases"]):
            for token in re.findall(r"规则卡 ([a-z-]+)", text):
                self.assertIn(token, CARDS, where)

    def test_the_interface_cards_named_in_the_path_are_in_the_card_list(self) -> None:
        used = {a["tool"].split(":", 1)[1] for p in DATA["phases"] for a in p["actions"] if a["tool"].startswith("card:")}
        for need in ("interface-pattern", "interface-components", "interface-icons", "interface-layout", "interface-motion", "interface-recipes", "design-direction"):
            self.assertIn(need, used)
            self.assertIn(need, CARDS)

    def test_page_pattern_rule_ids_in_text_exist(self) -> None:
        known = self.pattern_ids()
        ours = {x["id"] for kind in ("phases", "thinking_tools", "principles", "hard_floor") for x in DATA[kind]}
        boards = {b["id"] for b in json.loads((ROOT / "references" / "style-boards.json").read_text(encoding="utf-8"))["boards"]}
        libs = set(json.loads((ROOT / "references" / "component-libraries.json").read_text(encoding="utf-8"))["libraries"])
        for where, text in strings(DATA):
            if where.startswith("/phases") and "/pitfalls" in where:
                continue
            for token in re.findall(r"(?<![0-9A-Za-z/_-])[a-z][a-z0-9]*(?:-[a-z0-9]+){2,}(?![0-9A-Za-z/._-])", text):
                if token in ours or token in boards or token in libs or token in {"tdesign-miniprogram", "check-page"}:
                    continue
                self.assertIn(token, known, f"{where}: {token} 不在页面范式库里")

    def test_pending_slots_are_pointers_not_numbers(self) -> None:
        for p in DATA["phases"]:
            for r in p.get("pending_refs", []):
                self.assertTrue(r["ref"].startswith(("见视觉设计规范", "见界面细节规范")))


# ---------------------------------------------------------------- 规则页

class RulePageTest(unittest.TestCase):
    def test_page_is_the_render_of_the_data(self) -> None:
        self.assertEqual(PAGE.read_text(encoding="utf-8"), dp.render_html(), "规则页与 design-path.json 不一致：运行 design_path.py render --write")

    def test_ids_in_page_match_the_data(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        for kind in ("phases", "thinking_tools", "principles"):
            for item in DATA[kind]:
                self.assertIn(f"<code>{item['id']}</code>", text, item["id"])
        self.assertEqual(text.count("<h4>"), len(DATA["phases"]))

    def test_page_passes_the_rule_page_contract(self) -> None:
        import validate_skill as vs
        errors: list[str] = []
        vs.validate_rule_page(PAGE, "path", 0, DATA["title"], errors)
        self.assertEqual(errors, [])

    def test_page_passes_check_document(self) -> None:
        r = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "check_document.py"), str(PAGE)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("ERROR", r.stdout)

    def test_rendered_rule_text_fits_a_rule_card(self) -> None:
        import context
        total = sum(len(context.section_text(PAGE, [h]).encode("utf-8")) for h in
                    ("适用范围", "工作流程", "核心规则", "平台矩阵", "案例样本", "输出契约", "质量门禁", "交接规则"))
        self.assertLess(total, 35 * 1000, f"规则文本 {total} 字节，超过规则卡的 35 KB")
        self.assertGreater(total, 20 * 1000)

    def test_core_rules_have_the_agreed_sections(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        for h in ("一、怎么用这条路径", "二、十个阶段", "三、思考工具", "四、常见失误", "五、方法依据"):
            self.assertEqual(text.count(f"<h3>{h}</h3>"), 1, h)
        self.assertIn("<h3>项目模式（阶段 <code>design</code>）</h3>", text)
        self.assertEqual(text.count("细则待补"), 0)
        self.assertGreaterEqual(text.count("界面细节规范"), 3)

    def test_the_first_section_avoids_the_banned_words(self) -> None:
        scope = DATA["page"]["scope"]
        for word in ("日期", "无需构建", "可直接编辑", "入口", "说明"):
            self.assertNotIn(word, scope)

    def test_page_does_not_name_session_paths_the_checker_bans(self) -> None:
        self.assertNotIn("raw/", re.sub(r"<[^>]+>", "", PAGE.read_text(encoding="utf-8")))

    def test_inline_wraps_latin_and_refuses_nothing_else(self) -> None:
        self.assertEqual(dp.inline("用 `a.py` 和 BRIEF"), "用 <code>a.py</code> 和 <code>BRIEF</code>")
        self.assertEqual(dp.inline("P2 之后 <规则 id>"), "<code>P2</code> 之后 &lt;规则 <code>id</code>&gt;")


# ---------------------------------------------------------------- 命令行

class CliTest(unittest.TestCase):
    def test_list_shows_phases_tools_and_pending_slots(self) -> None:
        code, out, _ = run(["list"])
        self.assertEqual(code, 0)
        for pid in PHASE_IDS + REQUIRED_TOOLS:
            self.assertIn(pid, out)
        self.assertIn("待补位置", out)

    def test_show_every_id(self) -> None:
        for item in DATA["phases"] + DATA["thinking_tools"] + DATA["principles"]:
            code, out, _ = run(["show", item["id"]])
            self.assertEqual(code, 0, item["id"])
            self.assertTrue(out.strip())
        for key in ("order", "floor", "deviation", "signature", "example", "surfaces", "project", "basis"):
            self.assertEqual(run(["show", key])[0], 0, key)
        self.assertIn("思考链", run(["show", "P3"])[1])
        self.assertEqual(run(["show", "no-such-id"])[0], 2)

    def test_show_resolves_steps_and_names(self) -> None:
        self.assertIn("删除测试", run(["show", "five-questions"])[1])
        self.assertIn("positioning", run(["show", "一句话定位"])[1])

    def test_checklist_contains_every_phase_and_the_reminder(self) -> None:
        code, out, _ = run(["checklist"])
        self.assertEqual(code, 0)
        rows = [line for line in out.splitlines() if re.match(r"\| P\d ", line)]
        self.assertEqual(len(rows), 10)
        for p in DATA["phases"]:
            self.assertTrue(any(line.startswith(f"| {p['id']} {p['name']} |") for line in rows), p["id"])
        for line in rows:
            self.assertIn("[ ]", line)
            self.assertTrue(line.rstrip().endswith("| — |"))
        self.assertIn("本次沉淀", out)

    def test_checklist_by_surface_and_detail(self) -> None:
        for sid, s in DATA["surfaces"].items():
            code, out, _ = run(["checklist", "--surface", sid])
            self.assertEqual(code, 0)
            self.assertIn(f"（{s['name']}）", out)
            self.assertIn("本端注意", out)
        code, out, _ = run(["checklist", "--detail"])
        self.assertEqual(sum(1 for line in out.splitlines() if line.startswith("- [ ] P")), sum(len(p["checks"]) for p in DATA["phases"]))
        self.assertEqual(run(["checklist", "--surface", "nope"])[0], 2)

    def test_checklist_json(self) -> None:
        code, out, _ = run(["checklist", "--format", "json", "--surface", "admin"])
        data = json.loads(out)
        self.assertEqual([r["phase"] for r in data["rows"]], PHASE_IDS)
        self.assertIn("P2", data["surface_notes"])

    def test_deviation_format(self) -> None:
        code, out, err = run(["deviation", "first-module-answers-return-task", "--why", "首发周回访多为尝新", "--risk", "常客多滑一屏", "--verify", "两种账号状态各截图"])
        self.assertEqual(code, 0, err)
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], "偏离说明")
        self.assertTrue(lines[1].startswith("- 规则：first-module-answers-return-task（default）"))
        self.assertEqual(lines[2], "- 为什么偏离：首发周回访多为尝新")
        self.assertEqual(lines[3], "- 风险：常客多滑一屏")
        self.assertEqual(lines[4], "- 怎么验证：两种账号状态各截图")

    def test_deviation_refuses_must_rules(self) -> None:
        must = next(r["id"] for r in PATTERNS["rules"] if r["strength"] == "must")
        for rule in (must, "hard-floor", "function-first", "contrast-touch"):
            code, out, err = run(["deviation", rule, "--why", "a", "--risk", "b", "--verify", "c"])
            self.assertEqual(code, 2, rule)
            self.assertIn("must", err)
            self.assertEqual(out, "")

    def test_deviation_requires_all_fields(self) -> None:
        self.assertEqual(run(["deviation", "five-questions", "--why", "a", "--risk", "b"])[0], 2)
        code, _, err = run(["deviation", "first-module-answers-return-task", "--why", " ", "--risk", "b", "--verify", "c"])
        self.assertEqual(code, 2)
        self.assertIn("why", err)

    def test_deviation_hint_unknown_and_json(self) -> None:
        hint = next(r["id"] for r in PATTERNS["rules"] if r["strength"] == "hint")
        code, out, err = run(["deviation", hint, "--why", "a", "--risk", "b", "--verify", "c"])
        self.assertEqual(code, 0)
        self.assertIn("hint", err)
        code, out, err = run(["deviation", "my-own-rule", "--why", "a", "--risk", "b", "--verify", "c", "--json"])
        self.assertEqual(code, 0)
        self.assertIn("不在页面范式库", err)
        self.assertEqual(set(json.loads(out)), {"rule", "why", "risk", "verify"})

    def test_deviation_json_is_accepted_by_the_pattern_library_check(self) -> None:
        import page_pattern as pp
        _, out, _ = run(["deviation", "first-module-answers-return-task", "--why", "a", "--risk", "b", "--verify", "c", "--json"])
        dev = json.loads(out)
        spec = {"modules": [], "tabbar": {"items": []}, "deviations": [dev]}
        findings = pp.check_spec(spec, PATTERNS)
        self.assertFalse([f for f in findings if f["rule"] == "deviation-note-required"])

    def test_render_check(self) -> None:
        code, out, _ = run(["render", "--check"])
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
