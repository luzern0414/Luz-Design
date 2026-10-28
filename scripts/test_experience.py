"""Unit tests for the experience store: notes upsert by key, bounded stores, duplicate detection, shared notes shape."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experience as exp  # noqa: E402


class ExperienceStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.saved = {name: getattr(exp, name) for name in ("EXP", "SOURCES", "PATTERNS", "NOTES", "CATALOG", "PATTERN_CAP")}
        exp.EXP = root
        exp.SOURCES = root / "sources.json"
        exp.PATTERNS = root / "patterns.json"
        exp.NOTES = root / "notes.json"
        exp.CATALOG = root / "catalog.md"

    def tearDown(self) -> None:
        for name, value in self.saved.items():
            setattr(exp, name, value)
        self.tmp.cleanup()

    def run_cli(self, *argv: str) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exp.main(list(argv))
        return out.getvalue()

    def notes(self, kind: str | None = None) -> list[dict]:
        return [n for n in exp.load_notes(exp.NOTES)["notes"] if not kind or n["kind"] == kind]

    def test_same_key_replaces_in_place(self) -> None:
        self.run_cli("note", "--kind", "preference", "--key", "表头对齐", "--text", "表头左对齐")
        self.run_cli("note", "--kind", "preference", "--key", "表头对齐", "--text", "表头与数据居中", "--why", "用户纠正")
        prefs = self.notes()
        self.assertEqual(len(prefs), 1)
        self.assertEqual(prefs[0]["text"], "表头与数据居中")
        self.assertEqual(prefs[0]["previous"]["text"], "表头左对齐")
        self.assertEqual(prefs[0]["uses"], 2)
        self.assertEqual(prefs[0]["why"], "用户纠正")

    def test_previous_keeps_only_the_last_replaced_statement(self) -> None:
        for text in ("一", "二", "三"):
            self.run_cli("note", "--kind", "lesson", "--key", "k-1", "--text", f"规则{text}")
        lessons = self.notes("lesson")
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0]["previous"]["text"], "规则二")

    def test_fact_goes_to_notes_not_patterns_and_catalog_is_rendered(self) -> None:
        self.run_cli("note", "--kind", "fact", "--key", "ant-palette", "--text", "官方色板第六阶")
        self.run_cli("note", "--kind", "fact", "--key", "ant-palette", "--text", "官方色板按白字 4.5:1 取阶")
        facts = self.notes("fact")
        self.assertEqual([(n["key"], n["text"], n["previous"]["text"]) for n in facts],
                         [("ant-palette", "官方色板按白字 4.5:1 取阶", "官方色板第六阶")])
        self.assertFalse(exp.PATTERNS.exists())
        self.assertIn("官方色板按白字", exp.CATALOG.read_text(encoding="utf-8"))

    def test_same_statement_under_new_key_confirms(self) -> None:
        self.run_cli("note", "--kind", "lesson", "--key", "drawer", "--text", "详情用居中悬浮面板。")
        out = self.run_cli("note", "--kind", "lesson", "--key", "panel", "--text", "详情用 居中悬浮面板")
        self.assertIn("confirmed lesson drawer", out)
        self.assertEqual([(n["key"], n["uses"]) for n in self.notes()], [("drawer", 2)])

    def test_cap_prunes_fewest_uses_then_oldest(self) -> None:
        items = [
            {"key": "old-rare", "kind": "preference", "text": "甲", "uses": 1, "first_seen": "2025-01-01", "last_confirmed": "2025-01-01"},
            {"key": "old-often", "kind": "preference", "text": "乙", "uses": 5, "first_seen": "2025-01-01", "last_confirmed": "2025-01-01"},
            {"key": "new-rare", "kind": "preference", "text": "丙", "uses": 1, "first_seen": "2026-01-01", "last_confirmed": "2026-01-01"},
        ]
        exp.save_notes(exp.NOTES, {**exp.new_notes_doc(), "notes": items})
        with mock.patch.dict(exp.NOTE_CAPS, {"preference": 3}):
            out = self.run_cli("note", "--kind", "preference", "--key", "fresh", "--text", "丁")
        self.assertEqual({n["key"] for n in self.notes()}, {"old-often", "new-rare", "fresh"})
        self.assertIn("pruned preference old-rare", out)

    def test_prune_command_enforces_caps_and_lists_stale(self) -> None:
        items = [{"key": f"k-{i}", "kind": "lesson", "text": f"教训{i}", "uses": 1, "first_seen": "2020-01-01",
                  "last_confirmed": f"2020-01-0{i}"} for i in range(1, 5)]
        exp.save_notes(exp.NOTES, {**exp.new_notes_doc(), "notes": items})
        with mock.patch.dict(exp.NOTE_CAPS, {"lesson": 2}):
            self.assertTrue(any("exceed the cap 2" in e for e in exp.check_notes(exp.load_notes(exp.NOTES))))
            out = self.run_cli("prune")
        self.assertEqual([n["key"] for n in self.notes()], ["k-3", "k-4"])
        self.assertIn("not confirmed for 180 days", out)
        exp.save_notes(exp.NOTES, exp.load_notes(exp.NOTES))  # rewrite with the real caps
        self.assertEqual(exp.check(), [])

    def test_check_flags_duplicate_keys_statements_shape_and_privacy(self) -> None:
        base = {"kind": "preference", "uses": 1, "first_seen": "2026-01-01", "last_confirmed": "2026-01-01"}
        items = [{**base, "key": "a-key", "text": "表头居中。"}, {**base, "key": "a-key", "text": "禁用斜体"},
                 {**base, "key": "b-key", "text": " 表头 居中 "}, {**base, "key": "c-key", "text": "联系 13800138000"},
                 {**base, "key": "d-key", "text": "多余字段", "id": "PREF-001"}]
        exp.NOTES.write_text(json.dumps({"schema_version": "1.0", "preferences": items}, ensure_ascii=False), encoding="utf-8")
        errors = " | ".join(exp.check())
        self.assertIn("top-level fields must be schema_version, caps, notes", errors)
        exp.NOTES.write_text(json.dumps({**exp.new_notes_doc(), "notes": items}, ensure_ascii=False), encoding="utf-8")
        errors = " | ".join(exp.check())
        self.assertIn("duplicate note key a-key", errors)
        self.assertIn("note b-key repeats the statement of a-key", errors)
        self.assertIn("phone number", errors)
        self.assertIn("unknown fields id", errors)

    def test_check_flags_duplicate_pattern_titles(self) -> None:
        pats = [{"id": f"PAT-00{i}", "kind": "色彩", "title": "同名", "summary": f"要点{i}"} for i in (1, 2)]
        exp.save(exp.PATTERNS, {"schema_version": "1.0", "patterns": pats})
        self.assertTrue(any("duplicates the title" in e for e in exp.check()))

    def test_note_refuses_personal_data_and_bad_keys(self) -> None:
        for text in ("联系 13800138000", "邮件 someone@example.com", "微信号：abc_12345", r"放在 C:\Users\me\x.html",
                     "api_key=abcd1234"):
            with self.assertRaises(SystemExit, msg=text):
                self.run_cli("note", "--kind", "preference", "--key", "contact", "--text", text)
        with self.assertRaises(SystemExit):
            self.run_cli("note", "--kind", "preference", "--key", "Bad Key!", "--text", "任意")
        self.assertFalse(exp.NOTES.exists())


class SharedNotesSpecTest(unittest.TestCase):
    """experience/notes.json has the shape shared by Luz-System, Luz-Design, Luz-Dev and Luz-Writing."""

    def test_committed_notes_file_matches_shared_spec(self) -> None:
        path = Path(__file__).resolve().parents[1] / "experience" / "notes.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(list(doc), ["schema_version", "caps", "notes"])
        self.assertEqual(doc["schema_version"], "1.0")
        self.assertEqual(doc["caps"], {"preference": 60, "lesson": 120, "fact": 120})
        allowed = {"key", "kind", "text", "why", "uses", "first_seen", "last_confirmed", "previous"}
        for n in doc["notes"]:
            self.assertLessEqual({"key", "kind", "text", "uses", "first_seen", "last_confirmed"}, set(n), n.get("key"))
            self.assertLessEqual(set(n), allowed, n.get("key"))
            self.assertIn(n["kind"], ("preference", "lesson", "fact"))
            self.assertRegex(n["first_seen"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertRegex(n["last_confirmed"], r"^\d{4}-\d{2}-\d{2}$")
            if "previous" in n:
                self.assertEqual(set(n["previous"]), {"text", "replaced_at"})
        self.assertEqual(len({n["key"] for n in doc["notes"]}), len(doc["notes"]))
        self.assertEqual(exp.check_notes(doc), [])
        self.assertFalse((path.parent / "preferences.json").exists() or (path.parent / "lessons.json").exists()
                         or (path.parent / "experience.json").exists())


if __name__ == "__main__":
    unittest.main()
