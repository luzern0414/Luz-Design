"""Unit tests for the experience store: upsert by key, bounded stores, duplicate detection."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experience as exp  # noqa: E402


class ExperienceStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.saved = {name: getattr(exp, name) for name in ("EXP", "SOURCES", "PATTERNS", "PREFERENCES", "LESSONS", "CATALOG", "CAPS")}
        exp.EXP = root
        exp.SOURCES = root / "sources.json"
        exp.PATTERNS = root / "patterns.json"
        exp.PREFERENCES = root / "preferences.json"
        exp.LESSONS = root / "lessons.json"
        exp.CATALOG = root / "catalog.md"
        exp.CAPS = dict(exp.CAPS)

    def tearDown(self) -> None:
        for name, value in self.saved.items():
            setattr(exp, name, value)
        self.tmp.cleanup()

    def run_cli(self, *argv: str) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exp.main(list(argv))
        return out.getvalue()

    def prefs(self) -> list[dict]:
        return json.loads(exp.PREFERENCES.read_text(encoding="utf-8"))["preferences"]

    def test_same_key_replaces_in_place(self) -> None:
        self.run_cli("note", "--kind", "preference", "--key", "表头对齐", "--text", "表头左对齐")
        self.run_cli("note", "--kind", "preference", "--key", "表头对齐", "--text", "表头与数据居中", "--why", "用户纠正")
        prefs = self.prefs()
        self.assertEqual(len(prefs), 1)
        self.assertEqual(prefs[0]["text"], "表头与数据居中")
        self.assertEqual(prefs[0]["previous"]["text"], "表头左对齐")
        self.assertEqual(prefs[0]["uses"], 2)
        self.assertEqual(prefs[0]["why"], "用户纠正")

    def test_previous_keeps_only_the_last_replaced_statement(self) -> None:
        for text in ("一", "二", "三"):
            self.run_cli("note", "--kind", "lesson", "--key", "k-1", "--text", f"规则{text}")
        lessons = json.loads(exp.LESSONS.read_text(encoding="utf-8"))["lessons"]
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0]["previous"]["text"], "规则二")

    def test_fact_upserts_into_patterns_and_catalog_is_rendered(self) -> None:
        self.run_cli("note", "--kind", "fact", "--key", "ant-palette", "--text", "官方色板第六阶", "--category", "色彩")
        self.run_cli("note", "--kind", "fact", "--key", "ant-palette", "--text", "官方色板按白字 4.5:1 取阶", "--category", "色彩")
        patterns = json.loads(exp.PATTERNS.read_text(encoding="utf-8"))["patterns"]
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]["summary"], "官方色板按白字 4.5:1 取阶")
        self.assertEqual(patterns[0]["previous"]["summary"], "官方色板第六阶")
        self.assertIn("官方色板按白字", exp.CATALOG.read_text(encoding="utf-8"))

    def test_cap_prunes_least_used_and_oldest_first(self) -> None:
        exp.CAPS["preference"] = 3
        items = [
            {"id": "PREF-001", "key": "old-rare", "text": "甲", "first_seen": "2025-01-01", "last_confirmed": "2025-01-01", "uses": 1},
            {"id": "PREF-002", "key": "old-often", "text": "乙", "first_seen": "2025-01-01", "last_confirmed": "2025-01-01", "uses": 5},
            {"id": "PREF-003", "key": "new-rare", "text": "丙", "first_seen": "2026-01-01", "last_confirmed": "2026-01-01", "uses": 1},
        ]
        exp.save(exp.PREFERENCES, {"schema_version": "1.0", "preferences": items})
        out = self.run_cli("note", "--kind", "preference", "--key", "fresh", "--text", "丁")
        keys = {e["key"] for e in self.prefs()}
        self.assertEqual(keys, {"old-often", "new-rare", "fresh"})
        self.assertIn("pruned PREF-001", out)

    def test_prune_command_enforces_caps(self) -> None:
        exp.CAPS["lesson"] = 2
        items = [{"id": f"LES-00{i}", "key": f"k-{i}", "text": f"教训{i}", "first_seen": "2026-01-01",
                  "last_confirmed": f"2026-01-0{i}", "uses": 1} for i in range(1, 5)]
        exp.save(exp.LESSONS, {"schema_version": "1.0", "lessons": items})
        self.assertIn("cap is 2", " ".join(exp.check()))
        self.run_cli("prune")
        left = json.loads(exp.LESSONS.read_text(encoding="utf-8"))["lessons"]
        self.assertEqual([e["key"] for e in left], ["k-3", "k-4"])
        self.assertEqual(exp.check(), [])

    def test_check_flags_duplicate_keys_and_near_duplicate_statements(self) -> None:
        items = [
            {"id": "PREF-001", "key": "a-key", "text": "表头居中。", "first_seen": "2026-01-01", "last_confirmed": "2026-01-01"},
            {"id": "PREF-002", "key": "a-key", "text": "禁用斜体", "first_seen": "2026-01-01", "last_confirmed": "2026-01-01"},
            {"id": "PREF-003", "key": "b-key", "text": " 表头 居中 ", "first_seen": "2026-01-01", "last_confirmed": "2026-01-01"},
        ]
        exp.save(exp.PREFERENCES, {"schema_version": "1.0", "preferences": items})
        errors = " | ".join(exp.check())
        self.assertIn("PREF-002 duplicates key a-key", errors)
        self.assertIn("PREF-003 repeats the statement of PREF-001", errors)

    def test_check_flags_duplicate_pattern_titles(self) -> None:
        pats = [{"id": f"PAT-00{i}", "kind": "色彩", "title": "同名", "summary": f"要点{i}"} for i in (1, 2)]
        exp.save(exp.PATTERNS, {"schema_version": "1.0", "patterns": pats})
        self.assertTrue(any("duplicates the title" in e for e in exp.check()))

    def test_note_refuses_personal_data_and_bad_keys(self) -> None:
        with self.assertRaises(SystemExit):
            self.run_cli("note", "--kind", "preference", "--key", "contact", "--text", "联系 13800138000")
        with self.assertRaises(SystemExit):
            self.run_cli("note", "--kind", "preference", "--key", "Bad Key!", "--text", "任意")
        self.assertFalse(exp.PREFERENCES.exists())


if __name__ == "__main__":
    unittest.main()
