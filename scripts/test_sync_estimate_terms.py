"""sync_estimate_terms.py: the copies of estimate_terms.py in the other skills are checked, and only copied when asked. The tests work on a temporary skills root:
nothing here touches Luz-System, Luz-Writing or Luz-Project."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import estimate_terms  # noqa: E402
import sync_estimate_terms as sync  # noqa: E402


def run(root: Path, *argv: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = sync.main(list(argv), skills_root=root)
    return code, buf.getvalue()


class SyncEstimateTermsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.master = (HERE / "estimate_terms.py").read_bytes()
        for skill, rel in sync.TARGETS.items():
            (self.root / skill / Path(rel).parent).mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def target(self, skill: str) -> Path:
        return self.root / skill / sync.TARGETS[skill]

    def test_missing_copies_are_reported_and_not_created_by_the_default_mode(self) -> None:
        code, out = run(self.root)
        self.assertEqual(code, 1)
        for skill in sync.TARGETS:
            self.assertIn(f"MISSING {skill}", out)
            self.assertFalse(self.target(skill).exists(), "the default mode writes nothing")

    def test_identical_copies_are_same(self) -> None:
        for skill in sync.TARGETS:
            self.target(skill).write_bytes(self.master)
        code, out = run(self.root)
        self.assertEqual(code, 0)
        self.assertEqual(out.count("SAME"), 3)

    def test_an_edited_copy_is_a_diff_until_write_replaces_it(self) -> None:
        for skill in sync.TARGETS:
            self.target(skill).write_bytes(self.master)
        self.target("Luz-Writing").write_bytes(self.master + b"\n# a hand edit\n")
        code, out = run(self.root, "--check")
        self.assertEqual(code, 1)
        self.assertIn("DIFF Luz-Writing", out)
        self.assertIn("SAME Luz-System", out)
        self.assertNotEqual(self.target("Luz-Writing").read_bytes(), self.master, "--check does not write")
        code, out = run(self.root, "--write")
        self.assertEqual(code, 0)
        self.assertIn("SYNCED Luz-Writing", out)
        self.assertEqual(self.target("Luz-Writing").read_bytes(), self.master)

    def test_only_limits_both_modes_to_the_named_skills(self) -> None:
        code, out = run(self.root, "--write", "--only", "Luz-System")
        self.assertEqual(code, 0)
        self.assertEqual(self.target("Luz-System").read_bytes(), self.master)
        self.assertFalse(self.target("Luz-Writing").exists())
        self.assertFalse(self.target("Luz-Project").exists())
        self.assertNotIn("Luz-Project", out)
        code, out = run(self.root, "--check", "--only", "Luz-Project")
        self.assertEqual(code, 1)
        self.assertIn("MISSING Luz-Project", out)

    def test_write_skips_a_skill_whose_folder_is_not_there(self) -> None:
        (self.root / "Luz-Project" / "scripts").rmdir()
        (self.root / "Luz-Project").rmdir()
        code, out = run(self.root, "--write")
        self.assertIn("SKIP Luz-Project", out)
        self.assertEqual(self.target("Luz-System").read_bytes(), self.master)

    def test_the_digest_of_the_master_is_what_a_copy_must_report(self) -> None:
        namespace: dict = {}
        exec(compile(self.master.decode("utf-8"), "estimate_terms.py", "exec"), namespace)
        self.assertEqual(namespace["terms_digest"](), estimate_terms.terms_digest())


if __name__ == "__main__":
    unittest.main()
