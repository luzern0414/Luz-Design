import tempfile
import unittest
from pathlib import Path

import check_output_layout as col

PAGE = '<!doctype html><html lang="zh-CN"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><h1>标题</h1><h2>成果</h2></body></html>'


def make_session(base: Path, name="001-需求说明书", extra=(), html=PAGE, raw=True):
    s = base / name
    s.mkdir()
    if raw:
        (s / "raw").mkdir()
    (s / f"{name}.html").write_text(html, encoding="utf-8")
    for e in extra:
        (s / e).write_text("x", encoding="utf-8")
    return s


class SessionTest(unittest.TestCase):
    def check(self, s, linked=False):
        return col.check_session(s, linked)

    def test_clean_session_passes(self):
        with tempfile.TemporaryDirectory() as t:
            errors, _ = self.check(make_session(Path(t)))
            self.assertEqual(errors, [])

    def test_standalone_deliverable_allowed_but_not_when_project_linked(self):
        with tempfile.TemporaryDirectory() as t:
            s = make_session(Path(t), extra=["报价.xlsx"])
            self.assertEqual(self.check(s)[0], [])
            self.assertTrue(any("项目目录" in e for e in self.check(s, linked=True)[0]))

    def test_process_files_must_stay_in_raw(self):
        with tempfile.TemporaryDirectory() as t:
            s = make_session(Path(t), extra=["BRIEF.md", "spec.json", "MANIFEST.json"])
            msgs = " ".join(self.check(s)[0])
            for word in ("BRIEF.md", "spec.json", "MANIFEST.json"):
                self.assertIn(word, msgs)

    def test_name_rules(self):
        with tempfile.TemporaryDirectory() as t:
            bad = make_session(Path(t), name="需求说明书")
            self.assertTrue(any("三位序号" in e for e in self.check(bad)[0]))
            legacy = make_session(Path(t), name="12-旧会话")
            errors, notes = self.check(legacy)
            self.assertEqual(errors, [])
            self.assertTrue(any("旧格式" in n for n in notes))

    def test_missing_raw_summary_and_extra_dir(self):
        with tempfile.TemporaryDirectory() as t:
            s = make_session(Path(t), raw=False)
            self.assertTrue(any("raw" in e for e in self.check(s)[0]))
            s2 = make_session(Path(t), name="002-甲")
            (s2 / f"{s2.name}.html").unlink()
            (s2 / "scripts").mkdir()
            msgs = " ".join(self.check(s2)[0])
            self.assertIn("汇总页", msgs)
            self.assertIn("scripts", msgs)

    def test_summary_html_rules(self):
        with tempfile.TemporaryDirectory() as t:
            s = make_session(Path(t), html=PAGE.replace("<h1>标题</h1><h2>成果</h2>", "<h2>成果</h2><h1>标题</h1>"))
            self.assertTrue(any("h1" in e for e in self.check(s)[0]))
            s2 = make_session(Path(t), name="003-乙", html=PAGE.replace("initial-scale=1", "user-scalable=no"))
            self.assertTrue(any("缩放" in e for e in self.check(s2)[0]))


class ProjectTest(unittest.TestCase):
    def build(self, base: Path, files):
        p = base / "014-CustomerEntry"
        for rel in files:
            f = p / rel
            if rel.endswith("/"):
                f.mkdir(parents=True, exist_ok=True)
            else:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("x", encoding="utf-8")
        return p

    def test_clean_project_passes(self):
        with tempfile.TemporaryDirectory() as t:
            p = self.build(Path(t), ["docs/01-需求对接/01-需求说明书.pdf", "docs/02-产品开发/01-系统架构.html", "docs/03-验收交付/01-使用说明.xlsx", "src/app.py", "test/test_app.py"])
            self.assertEqual(col.check_project(p)[0], [])

    def test_state_and_raw_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p = self.build(Path(t), ["raw/00-crawl/x.json", "project.json", "data/client/features.json", "config/paths.json", "docs/01-需求对接/01-需求说明书.pdf"])
            msgs = " ".join(col.check_project(p)[0])
            for word in ("raw", "project.json", "data" + chr(92) + "client", "config" + chr(92) + "paths.json"):
                self.assertIn(word, msgs)

    def test_docs_rules(self):
        with tempfile.TemporaryDirectory() as t:
            p = self.build(Path(t), ["docs/01-需求对接/需求说明书.pdf", "docs/01-需求对接/源文件.docx", "docs/02-产品开发/01-原型.pdf", "docs/04-其他/a.pdf", "docs/03-验收交付/子/01-a.pdf", "docs/说明.md"])
            msgs = " ".join(col.check_project(p)[0])
            for word in ("两位序号", "源文件.docx", "01-原型.pdf", "04-其他", "子", "说明.md"):
                self.assertIn(word, msgs)


if __name__ == "__main__":
    unittest.main()
