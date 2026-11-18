"""Rule cards: every card resolves, carries the user's preferences, and sessions cannot publish without one."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import context  # noqa: E402
import validate_session  # noqa: E402
from validate_session import adopted_rules, rule_card_errors, sediment_errors  # noqa: E402

SECTIONS = ["## 1 用户偏好", "## 2 相关教训与有效做法", "## 3 规则", "## 4 用什么做", "## 5 交付前必须通过", "## 6 收尾"]


class RuleCardTests(unittest.TestCase):
    def test_every_card_resolves_to_rule_sections(self) -> None:
        self.assertEqual(context.check_cards(), [])

    def test_every_card_has_the_six_parts_and_real_rule_text(self) -> None:
        for kind in context.card_kinds():
            text, digest = context.make_card(kind, [])
            for heading in SECTIONS:
                self.assertIn(heading, text, f"{kind}: {heading}")
            self.assertRegex(digest, r"^[0-9a-f]{12}$")
            rules = text.split("## 3 规则", 1)[1].split("## 4 用什么做", 1)[0]
            self.assertIn("### ", rules, f"{kind}: missing resolved rule heading")
            self.assertTrue(any(len(line.strip()) >= 30 for line in rules.splitlines() if not line.startswith("#")), f"{kind}: missing actionable source text")
            # Markup is flattened; only code samples quoted by the rules (icons) may contain tags.
            self.assertNotRegex(rules, r"<(p|td|th|tr|li|ul|div|section|h[1-6])[\s>]", f"{kind}: HTML left in the card")

    def test_preferences_are_limited_to_the_card_scope(self) -> None:
        notes = context.load_json(context.NOTES_FILE, {"notes": []})["notes"]
        cards=context.load_json(context.CARDS_FILE,{})
        prefs = [n["key"] for n in notes if n["kind"] == "preference" and context.note_listed(n) and context.note_in_scope(n,cards['cards']['xlsx'],cards)]
        self.assertTrue(prefs)
        text, _ = context.make_card("xlsx", [])
        for key in prefs:
            self.assertIn(f"（{key}）", text)

    def test_xlsx_card_carries_the_spreadsheet_rules(self) -> None:
        text, _ = context.make_card("xlsx", [])
        for phrase in ("不要序号列", "上下合并", "导出文件", "make_xlsx.py", "check_document.py"):
            self.assertIn(phrase, text)

    def test_section_ends_at_the_next_heading_of_the_same_level(self) -> None:
        page = context.SKILL_ROOT / "references" / "file-design.html"
        table = context.section_text(page, ["核心规则", "表格文件"])
        self.assertIn("导出文件", table)
        self.assertNotIn("页面与字体", table)  # first part of 文字文档, the next h3

    def test_saved_card_records_its_hash_and_goes_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            card = context.save_card(Path(temp), "docx")
            self.assertTrue(context.card_is_current(card))
            first, rest = card.read_text(encoding="utf-8").split("\n", 1)
            card.write_text(first.replace(first[first.index(":") + 2:first.index(":") + 14], "000000000000") + "\n" + rest, encoding="utf-8")
            self.assertFalse(context.card_is_current(card))

    def test_adopted_rules_ignore_header_separator_and_comment(self) -> None:
        brief = "# Brief\n\n## 采用的规则\n\n<!-- | 示例 | 示例 | -->\n\n| 规则（规范页 › 小节 或 偏好 key） | 本次怎么落实 |\n|---|---|\n"
        self.assertEqual(adopted_rules(brief), [])
        self.assertEqual(adopted_rules(brief + "| excel-layout | 无序号列 |\n"), [("excel-layout", "无序号列")])
        self.assertIsNone(adopted_rules("# Brief\n"))

    def test_session_without_card_or_adopted_rules_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            (work / "BRIEF.md").write_text("# Brief\n\n## 采用的规则\n\n| 规则 | 落实 |\n|---|---|\n", encoding="utf-8")
            errors = rule_card_errors(work, require_adopted=True, check_current=True)
            self.assertTrue(any("00-rules" in e for e in errors))
            self.assertTrue(any("采用的规则 is empty" in e for e in errors))
            context.save_card(work, "xlsx")
            (work / "BRIEF.md").write_text("# Brief\n\n## 采用的规则\n\n| excel-layout | 无序号列 |\n", encoding="utf-8")
            self.assertEqual(rule_card_errors(work, require_adopted=True, check_current=True), [])

    def test_every_session_leaves_a_dated_note_behind(self) -> None:
        import json
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            notes = work / "notes.json"
            notes.write_text(json.dumps({"notes": [
                {"key": "fresh", "kind": "fact", "text": "有效做法", "last_confirmed": "2026-10-29"},
                {"key": "old", "kind": "lesson", "text": "旧教训", "last_confirmed": "2026-10-01"},
            ]}, ensure_ascii=False), encoding="utf-8")
            saved = validate_session.NOTES_FILE
            validate_session.NOTES_FILE = notes
            try:
                (work / "BRIEF.md").write_text("# Brief\n", encoding="utf-8")
                self.assertIn("no 本次沉淀", sediment_errors(work, "2026-10-29")[0])
                base = "# Brief\n\n## 本次沉淀\n\n| 经验 key | 类型 | 一句话 |\n|---|---|---|\n"
                (work / "BRIEF.md").write_text(base, encoding="utf-8")
                self.assertIn("is empty", sediment_errors(work, "2026-10-29")[0])
                (work / "BRIEF.md").write_text(base + "| missing | fact | 不存在 |\n", encoding="utf-8")
                self.assertIn("not in experience/notes.json", sediment_errors(work, "2026-10-29")[0])
                (work / "BRIEF.md").write_text(base + "| old | lesson | 旧教训 |\n", encoding="utf-8")
                self.assertIn("before this session", sediment_errors(work, "2026-10-29")[0])
                (work / "BRIEF.md").write_text(base + "| fresh | fact | 有效做法 |\n", encoding="utf-8")
                self.assertEqual(sediment_errors(work, "2026-10-29"), [])
            finally:
                validate_session.NOTES_FILE = saved

    def test_card_tells_what_to_sediment(self) -> None:
        text, _ = context.make_card("xlsx", [])
        for phrase in ("本次沉淀", "preference", "lesson", "fact", "调研来源与范围", "同一 key"):
            self.assertIn(phrase, text)


class ExperienceStoreOverrideTests(unittest.TestCase):
    """LUZ_EXPERIENCE_STORE (tests and rehearsals only) takes note writes and feeds the rule card; the skill's own files stay untouched."""

    def test_override_store_takes_writes_and_feeds_the_card(self) -> None:
        import os
        import subprocess
        skill_root = Path(__file__).resolve().parents[1]
        experience = {p: p.read_bytes() for p in (skill_root / "experience").iterdir() if p.is_file()}
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "notes.json"
            env = {**os.environ, "LUZ_EXPERIENCE_STORE": str(store)}

            def run(*args: str) -> subprocess.CompletedProcess:
                return subprocess.run([sys.executable, "-X", "utf8", *args], cwd=skill_root, env=env, text=True,
                                      capture_output=True, encoding="utf-8", errors="replace", check=False)

            noted = run("scripts/experience.py", "note", "--kind", "preference", "--key", "override-probe", "--scope", "documents", "--text", "探针偏好，只写测试库")
            self.assertEqual(noted.returncode, 0, noted.stderr)
            self.assertTrue(store.is_file())
            card = run("scripts/context.py", "xlsx")
            self.assertEqual(card.returncode, 0, card.stderr)
            self.assertIn("探针偏好", card.stdout)
            self.assertNotIn("探针偏好",run('scripts/context.py','web').stdout)
        self.assertEqual({p: p.read_bytes() for p in (skill_root / "experience").iterdir() if p.is_file()}, experience)


class RuleSourceTests(unittest.TestCase):
    """A card section can be cut from .md, .txt and .json rule sources as well as .html pages."""

    def write(self, name: str, text: str) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_markdown_cuts_by_heading_path_or_whole_file(self) -> None:
        path = self.write("rules.md", "# 总题\n\n导语。\n\n## 一 甲\n\n甲正文。\n\n```\n# 代码里的井号不是标题\n```\n\n### 子节\n\n子节正文。\n\n## 二 乙\n\n乙正文。\n")
        part = context.section_text(path, ["一 甲"])
        self.assertIn("甲正文。", part)
        self.assertIn("# 代码里的井号不是标题", part)
        self.assertIn("#### 子节", part)  # sub-headings nest under the card's ### label
        self.assertNotIn("乙正文", part)
        whole = context.section_text(path, [])
        self.assertIn("#### 总题", whole)
        self.assertIn("##### 二 乙", whole)
        with self.assertRaises(KeyError):
            context.section_text(path, ["不存在"])

    def test_text_cuts_by_block_title_and_the_preamble_has_the_empty_title(self) -> None:
        path = self.write("prompts.txt", "开头说明。\n\n第二段。\n\n=== Photo (verified) ===\nLine one.\nLine two.\n\n\n=== Sheet ===\nOnly sheet.\n")
        self.assertEqual(context.section_text(path, [""]), "开头说明。\n\n第二段。")
        self.assertEqual(context.section_text(path, ["Photo (verified)"]), "Line one.\nLine two.")
        whole = context.section_text(path, [])
        self.assertTrue(whole.startswith("开头说明。"))
        self.assertIn("#### Photo (verified)\nLine one.\nLine two.\n\n#### Sheet\nOnly sheet.", whole)
        self.assertIn("#### Sheet", whole)
        for missing in (["Photo"], ["Photo (verified)", "Sheet"]):  # titles match exactly; a block has no sub-blocks
            with self.assertRaises(KeyError):
                context.section_text(path, missing)

    def test_json_cuts_by_key_path_into_bullets_and_tables(self) -> None:
        data = {"meta": {"when": "2026-01-01", "values": {"ok": "好", "bad": "坏|差"}}, "tips": ["甲", "乙"],
                "items": [{"id": "a", "kind": "x", "state": "ok", "note": "一"}, {"id": "b", "kind": "y", "state": "bad", "note": "二"},
                          {"id": "c", "kind": "x", "state": "ok", "note": "三"}]}
        path = self.write("data.json", json.dumps(data, ensure_ascii=False))
        meta = context.section_text(path, ["meta"])
        self.assertIn("- when：2026-01-01", meta)
        self.assertIn("  - bad：坏/差", meta)  # nested values indent; a pipe never breaks a cell
        self.assertEqual(context.section_text(path, ["tips"]), "- 甲\n- 乙")
        self.assertEqual(context.section_text(path, ["items", "1", "id"]), "b")  # a digit step indexes a list
        table = context.section_text(path, ["items"], ["id", "state"])
        self.assertEqual(table.splitlines()[:3], ["| id | state |", "|---|---|", "| a | ok |"])
        self.assertNotIn("note", table)
        grouped = context.section_text(path, ["items"], ["id", "kind", "state"], "kind")
        self.assertIn("#### x（2）", grouped)
        self.assertIn("#### y（1）", grouped)
        self.assertIn("| id | state |\n|---|---|\n| a | ok |\n| c | ok |", grouped)  # the group column moves into the heading
        for keys, fields in ((["nope"], None), (["items", "9"], None), (["tips", "x"], None), (["items"], ["id", "missing"])):
            with self.assertRaises(KeyError, msg=f"{keys} {fields}"):
                context.section_text(path, keys, fields)

    def test_a_card_spec_passes_fields_and_group_by_to_the_json_cut(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "reg.json").write_text(json.dumps({"items": [{"id": "a", "kind": "x"}, {"id": "b", "kind": "y"}]}), encoding="utf-8")
            spec = {"page": "reg.json", "root": str(base), "label": "登记表", "path": ["items"], "fields": ["id"], "group_by": "kind"}
            cards = {"skill": "probe", "cards": {"probe": {"title": "t", "summary": "s", "sections": [spec], "tools": ["t"], "checks": ["c"]}}}
            (base / "cards.json").write_text(json.dumps(cards), encoding="utf-8")
            saved = context.CARDS_FILE
            context.CARDS_FILE = base / "cards.json"
            try:
                text, _ = context.make_card("probe", [])
                self.assertEqual(context.check_cards(), [])
                spec["fields"] = ["id", "typo"]
                (base / "cards.json").write_text(json.dumps(cards), encoding="utf-8")
                self.assertTrue(context.check_cards())
            finally:
                context.CARDS_FILE = saved
        self.assertIn("### 登记表", text)
        self.assertIn("#### x（1）", text)
        self.assertNotIn("| kind |", text)

    def test_design_research_and_image_assets_carry_their_rule_sources(self) -> None:
        cards = context.load_json(context.CARDS_FILE, {})["cards"]
        self.assertIn("design/sources.md", {part["page"] for part in cards["design-research"]["sections"]})
        self.assertIn("image-assets.md", {part["page"] for part in cards["image-assets"]["sections"]})
        research, _ = context.make_card("design-research", [])
        assets, _ = context.make_card("image-assets", [])

        def source_rules(card: str) -> str:
            # Preferences and historical notes cannot hide a broken source route.
            return card.split("## 3 规则", 1)[1].split("## 4 用什么做", 1)[0]

        research_rules, asset_rules = source_rules(research), source_rules(assets)
        for page, rules in [('design/sources.md',research_rules),('image-assets.md',asset_rules)]:
            source = context.section_text(context.SKILL_ROOT/'references'/page,[])
            self.assertIn(source,rules)



if __name__ == "__main__":
    unittest.main()
