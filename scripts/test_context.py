"""Rule cards: every card resolves, carries the user's preferences, and sessions cannot publish without one."""
from __future__ import annotations

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
            self.assertGreater(len(rules), 800, f"{kind}: rule text too short")
            # Markup is flattened; only code samples quoted by the rules (icons) may contain tags.
            self.assertNotRegex(rules, r"<(p|td|th|tr|li|ul|div|section|h[1-6])[\s>]", f"{kind}: HTML left in the card")

    def test_preferences_are_always_on_the_card(self) -> None:
        notes = context.load_json(context.NOTES_FILE, {"notes": []})["notes"]
        prefs = [n["key"] for n in notes if n["kind"] == "preference"]
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

            noted = run("scripts/experience.py", "note", "--kind", "preference", "--key", "override-probe", "--text", "探针偏好，只写测试库")
            self.assertEqual(noted.returncode, 0, noted.stderr)
            self.assertTrue(store.is_file())
            card = run("scripts/context.py", "xlsx")
            self.assertEqual(card.returncode, 0, card.stderr)
            self.assertIn("探针偏好", card.stdout)
        self.assertEqual({p: p.read_bytes() for p in (skill_root / "experience").iterdir() if p.is_file()}, experience)


if __name__ == "__main__":
    unittest.main()
