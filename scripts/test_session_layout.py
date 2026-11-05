"""Session output layout of Luz Design: root = raw\\ + summary page; project tasks keep results in the project; older sessions are only noted."""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_output_layout as layout
import deliver
import make_summary
import new_session
import publish as publisher
import validate_session
import validate_skill
from new_session import create_session
from test_session_flow import adopt_rules, read_json, tool_root, write_json
from validate_session import validate


def quiet(function, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args, **kwargs)


def write_summary(session: Path, shown: list[str], project_linked: bool = False) -> int:
    """Fill the skeleton spec the way an agent does (every result named in the table) and run make_summary.py --check."""
    spec_path = session / "raw" / "03-documents" / "summary.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["sections"][0]["table"]["rows"] = [[name, "对外交付", name] for name in shown]
    for section in spec["sections"][1:]:
        section["table"]["rows"] = [[cell.replace("（填写）", "已写") for cell in row] for row in section["table"]["rows"]]
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return quiet(make_summary.main, [str(spec_path), str(session), "--check"] + (["--project-linked"] if project_linked else []))


def make_project(base: Path, name="014-ProjectX", with_deliver_root=True) -> tuple[Path, Path]:
    """A state root (where project.json is) and the project folder it names in deliver_root."""
    state = base / "state" / name / "raw"
    state.mkdir(parents=True)
    folder = base / name
    (state / "project.json").write_text(json.dumps({"deliver_root": str(folder)} if with_deliver_root else {}), encoding="utf-8")
    return state, folder


class LayoutCase(unittest.TestCase):
    def tearDown(self) -> None:
        validate_session.NOTES_FILE = ROOT / "experience" / "notes.json"   # adopt_rules points it at a temporary store

    def sheet(self, root: Path, name="门店销售表") -> tuple[Path, Path]:
        session = create_session(root, name, ["document"], skill_root=ROOT, cards=["xlsx"])
        made = session / "raw" / "03-documents" / "outputs" / f"{name}.xlsx"
        made.write_bytes(b"xlsx")
        return session, made


class NewSessionTest(LayoutCase):
    def test_root_is_raw_only_and_the_manifest_marks_the_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, _ = self.sheet(tool_root(temp))
            self.assertEqual(session.name, "001-门店销售表")
            self.assertEqual([item.name for item in session.iterdir()], ["raw"])
            manifest = read_json(session / "raw" / "99-delivery" / "MANIFEST.json")
            self.assertEqual(manifest["output_standard"], validate_session.OUTPUT_STANDARD)
            self.assertIsNone(manifest["project"])
            raw = session / "raw"
            for child in ("BRIEF.md", "00-rules/xlsx.md", "03-documents/summary.json", "99-delivery/MANIFEST.json", "99-delivery/APPROVALS.json"):
                self.assertTrue((raw / child).is_file(), child)
            spec = json.loads((raw / "03-documents" / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(spec["title"], "门店销售表")
            self.assertEqual([section["title"] for section in spec["sections"]], ["成果", "依据", "过程文件"])
            make_summary.render(spec)                      # the skeleton is a valid spec
            self.assertEqual(validate(session), [])        # nothing delivered yet
            self.assertTrue(any("汇总页" in error for error in layout.check_session(session, False)[0]))

    def test_a_poster_session_has_no_summary_spec_because_its_board_is_the_summary_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session = create_session(tool_root(temp), "秋季海报", ["visual"], skill_root=ROOT, session_kind="standalone_poster")
            self.assertEqual([item.name for item in session.iterdir()], ["raw"])
            self.assertFalse((session / "raw" / "03-documents").exists())

    def test_numbers_continue_after_older_sessions_and_are_never_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = tool_root(temp)
            for name in ("012-旧会话", "05_old", "7-短号", "杂项"):
                (root / name).mkdir()
            self.assertTrue(create_session(root, "新会话", ["document"], skill_root=ROOT).name.startswith("013-"))
            self.assertTrue(create_session(root, "再一个", ["document"], skill_root=ROOT).name.startswith("014-"))

    def test_command_line_takes_a_project_and_says_where_results_go(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            state, folder = make_project(base)
            root = tool_root(temp)
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                code = new_session.main(["--name", "前端界面设计", "--modes", "document", "--root", str(root), "--project", str(state)])
            self.assertEqual(code, 0)
            self.assertIn("project's docs", stderr.getvalue())
            self.assertEqual(read_json(next(root.iterdir()) / "raw" / "99-delivery" / "MANIFEST.json")["project"]["deliver_root"], str(folder))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = new_session.main(["--name", "别的", "--root", str(root), "--project", str(base / "没有这个项目")])
            self.assertEqual(code, 1)


class StandaloneDeliveryTest(LayoutCase):
    def test_spreadsheet_sits_in_the_root_and_the_summary_page_lists_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, made = self.sheet(tool_root(temp))
            placed = deliver.deliver(session, made, as_name="门店销售表")
            self.assertEqual(placed, session / "门店销售表.xlsx")
            self.assertTrue(made.is_file(), "the source stays in raw")
            errors = validate(session)
            self.assertTrue(any("汇总页" in error for error in errors), errors)
            adopt_rules(session, "文件设计规范 › 核心规则 › 表格文件", "无序号列，分组名纵向合并")
            self.assertEqual(write_summary(session, ["门店销售表.xlsx"]), 0)
            self.assertEqual(validate(session), [])
            self.assertEqual(sorted(item.name for item in session.iterdir()), sorted(["raw", "001-门店销售表.html", "门店销售表.xlsx"]))
            (session / "对账.pdf").write_bytes(b"pdf")
            self.assertTrue(any("does not list 对账.pdf" in error for error in validate(session)))
            (session / "对账.pdf").unlink()
            (session / "run.exe").write_bytes(b"x")
            (session / "build").mkdir()
            joined = " ".join(validate(session))
            self.assertIn("run.exe", joined)
            self.assertIn("build", joined)

    def test_summary_page_with_template_placeholders_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, made = self.sheet(tool_root(temp))
            deliver.deliver(session, made)
            adopt_rules(session)
            spec = session / "raw" / "03-documents" / "summary.json"
            quiet(make_summary.main, [str(spec), str(session)])
            self.assertTrue(any(validate_session.SUMMARY_PLACEHOLDER in error for error in validate(session)))

    def test_deliver_refuses_what_belongs_elsewhere(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, made = self.sheet(tool_root(temp))
            page = session / "raw" / "x.html"
            page.write_text("<p>x</p>", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                deliver.deliver(session, page)
            self.assertIn("publish.py", str(caught.exception))
            with self.assertRaises(ValueError):
                deliver.deliver(session, made, to="01-需求对接")                       # --to is for project sessions
            program = session / "raw" / "tool.exe"
            program.write_bytes(b"x")
            with self.assertRaises(ValueError):
                deliver.deliver(session, program)
            with self.assertRaises(ValueError):
                deliver.deliver(session, made, as_name="a/b")
            deliver.deliver(session, made)
            with self.assertRaises(FileExistsError):
                deliver.deliver(session, made)
            self.assertEqual(deliver.deliver(session, made, replace=True), session / made.name)

    def test_cli_names_the_text_for_the_summary_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, made = self.sheet(tool_root(temp))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(deliver.main([str(session), str(made), "--as", "销售明细"]), 0)
            self.assertIn("LIST IN SUMMARY (位置): 销售明细.xlsx", out.getvalue())


class PagePublishTest(LayoutCase):
    def test_page_becomes_the_summary_page_and_a_layout_failure_rolls_it_back(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session = create_session(tool_root(temp), "门店月度报告", ["document"], skill_root=ROOT)
            adopt_rules(session)
            with mock.patch.object(layout, "check_session", return_value=(["boom"], [])):
                with self.assertRaises(ValueError) as caught:
                    publisher.publish(session, "document")
            self.assertIn("boom", str(caught.exception))
            self.assertEqual([item.name for item in session.iterdir()], ["raw"])
            self.assertNotIn("final", read_json(session / "raw" / "99-delivery" / "MANIFEST.json"))
            page = publisher.publish(session, "document")
            self.assertEqual(sorted(item.name for item in session.iterdir()), sorted(["raw", page.name]))
            self.assertEqual(layout.check_session(session, False), ([], []))
            self.assertEqual(validate(session), [])
            (session / "别的.html").write_text("<p>x</p>", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                publisher.publish(session, "document")
            self.assertIn("unexpected HTML", str(caught.exception))

    def test_older_session_is_published_with_notes_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session = create_session(tool_root(temp), "门店月度报告", ["document"], skill_root=ROOT)
            adopt_rules(session)
            path = session / "raw" / "99-delivery" / "MANIFEST.json"
            manifest = read_json(path)
            del manifest["output_standard"]
            write_json(path, manifest)
            stderr = io.StringIO()
            with mock.patch.object(layout, "check_session", return_value=(["旧的布局问题"], [])), contextlib.redirect_stderr(stderr):
                page = publisher.publish(session, "document")
            self.assertTrue(page.is_file())
            self.assertIn("旧的布局问题", stderr.getvalue())


class ProjectTaskTest(LayoutCase):
    def test_project_is_found_from_the_state_root_or_from_the_project_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            state, folder = make_project(base)
            link = new_session.resolve_project(state)
            self.assertEqual((Path(link["state_root"]), Path(link["deliver_root"]), link["delivered"]), (state, folder, []))
            with mock.patch.object(new_session, "PROJECT_OUTPUT_ROOT", base / "state"):
                self.assertEqual(new_session.resolve_project(folder), link)
            old_state, _ = make_project(base, "009-OldProject", with_deliver_root=False)
            self.assertEqual(Path(new_session.resolve_project(old_state)["deliver_root"]), old_state, "a project made before the split keeps results at its root")
            with self.assertRaises(ValueError):
                new_session.resolve_project(base / "不存在")

    def test_results_go_to_the_project_docs_and_the_root_keeps_raw_and_the_summary_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            state, folder = make_project(base)
            session = create_session(tool_root(temp), "前端界面设计", ["document"], skill_root=ROOT, project=state)
            self.assertEqual(read_json(session / "raw" / "99-delivery" / "MANIFEST.json")["project"]["deliver_root"], str(folder))
            adopt_rules(session)
            with self.assertRaises(ValueError):
                publisher.publish(session, "document")                                       # a project page needs --as
            with self.assertRaises(ValueError):
                publisher.publish(session, "document", as_name="前端界面设计")                  # NN-名称
            page = publisher.publish(session, "document", as_name="03-前端界面设计")
            self.assertEqual(page, folder / "docs" / "02-产品开发" / "03-前端界面设计.html")
            sheet = session / "raw" / "03-documents" / "outputs" / "需求清单.xlsx"
            sheet.write_bytes(b"xlsx")
            with self.assertRaises(ValueError):
                deliver.deliver(session, sheet, as_name="01-需求清单")                         # --to is required
            with self.assertRaises(ValueError):
                deliver.deliver(session, sheet, as_name="需求清单", to="01-需求对接")           # NN- is required
            word = session / "raw" / "03-documents" / "outputs" / "说明.docx"
            word.write_bytes(b"docx")
            with self.assertRaises(ValueError):
                deliver.deliver(session, word, as_name="01-说明", to="01-需求对接")             # clients get PDF or XLSX
            written = deliver.deliver(session, sheet, as_name="01-需求清单", to="01-需求对接")
            self.assertEqual(written, folder / "docs" / "01-需求对接" / "01-需求清单.xlsx")
            self.assertEqual([item.name for item in session.iterdir()], ["raw"])
            self.assertTrue(any("汇总页" in error for error in validate(session)))
            shown = [r"docs\01-需求对接\01-需求清单.xlsx", r"docs\02-产品开发\03-前端界面设计.html"]
            self.assertEqual(write_summary(session, shown, project_linked=True), 0)
            self.assertEqual(validate(session), [])
            self.assertEqual(sorted(item.name for item in session.iterdir()), sorted(["raw", f"{session.name}.html"]))
            self.assertEqual(layout.check_project(folder)[0], [], "the project folder holds results only")
            delivered = read_json(session / "raw" / "99-delivery" / "MANIFEST.json")["project"]["delivered"]
            self.assertEqual(sorted(entry["path"] for entry in delivered), ["docs/01-需求对接/01-需求清单.xlsx", "docs/02-产品开发/03-前端界面设计.html"])
            # a copy left in the root, a result the summary page does not name and a result changed afterwards are all reported
            (session / "需求清单.xlsx").write_bytes(b"x")
            self.assertTrue(any("项目目录" in error for error in validate(session)))
            (session / "需求清单.xlsx").unlink()
            write_summary(session, shown[:1], project_linked=True)
            self.assertTrue(any("does not list docs/02-产品开发/03-前端界面设计.html" in error for error in validate(session)))
            write_summary(session, shown, project_linked=True)
            written.write_bytes(b"changed")
            self.assertTrue(any("differs from the hash" in error for error in validate(session)))
            self.assertEqual(deliver.deliver(session, sheet, as_name="01-需求清单", to="01-需求对接"), written)   # written again by this session
            self.assertEqual(validate(session), [])
            (folder / "docs" / "01-需求对接" / "02-别人写的.xlsx").write_bytes(b"x")
            with self.assertRaises(FileExistsError):
                deliver.deliver(session, sheet, as_name="02-别人写的", to="01-需求对接")


class OlderSessionTest(LayoutCase):
    def strip_marker(self, session: Path) -> None:
        path = session / "raw" / "99-delivery" / "MANIFEST.json"
        manifest = read_json(path)
        del manifest["output_standard"]
        write_json(path, manifest)

    def test_layout_findings_of_an_older_session_are_notes_and_a_new_one_gets_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, made = self.sheet(tool_root(temp))
            for name in ("一期需求与报价.xlsx", "二期需求与报价.xlsx", "index.html"):
                (session / name).write_bytes(b"x")
            (session / "scripts").mkdir()
            new_errors = validate(session)
            self.assertTrue(any("scripts" in error for error in new_errors), new_errors)
            self.strip_marker(session)
            notes: list[str] = []
            errors = validate(session, notes=notes)
            layout_words = ("汇总页", "根目录", "scripts", "多出", "does not list")
            self.assertFalse([error for error in errors if any(word in error for word in layout_words)], errors)
            self.assertTrue(any("旧会话布局" in note and "scripts" in note for note in notes), notes)
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                self.assertEqual(validate_session.main([str(session)]), 0)
            self.assertIn("NOTE 旧会话布局", printed.getvalue())

    def test_two_digit_folder_name_is_a_note(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = tool_root(temp)
            session = create_session(root, "旧式命名", ["document"], skill_root=ROOT)
            older = root / "12-旧式命名"
            session.rename(older)
            self.strip_marker(older)
            notes: list[str] = []
            errors = validate(older, notes=notes)
            self.assertFalse([error for error in errors if "zero-padded" in error], errors)
            self.assertTrue(any("旧会话目录名" in note for note in notes), notes)

    def test_sweep_fails_only_for_sessions_made_under_the_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = tool_root(temp)
            create_session(out, "新甲", ["document"], skill_root=ROOT)
            bad = create_session(out, "新乙", ["document"], skill_root=ROOT)
            (bad / "run.exe").write_bytes(b"x")
            old = create_session(out, "旧丙", ["document"], skill_root=ROOT)
            (old / "a.xlsx").write_bytes(b"x")
            (old / "scripts").mkdir()
            self.strip_marker(old)
            (out / "_work").mkdir()
            errors, notes, count = validate_skill.session_sweep(out)
            self.assertEqual(count, 3)
            self.assertTrue(errors)
            self.assertTrue(all(error.startswith(bad.name + ":") for error in errors), errors)
            self.assertTrue(any(note.startswith("1 older session(s) kept as they are") for note in notes), notes)
            self.assertTrue(any("_work" in note and "not validated" in note for note in notes), notes)
            self.assertFalse(any(note.startswith(old.name) for note in notes))
            _, detailed, _ = validate_skill.session_sweep(out, details=True)
            self.assertTrue(any(note.startswith(old.name) and "scripts" in note for note in detailed), detailed)

    def test_build_trees_and_review_pages_in_raw_are_not_judged_as_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            session, _ = self.sheet(tool_root(temp))
            site = session / "raw" / "build" / "site"
            site.mkdir(parents=True)
            (site / "index.html").write_text("<!doctype html><style>body{background:#000;font-size:10px}</style><p>框架构建产物</p><a href=\"missing.html\">x</a>", encoding="utf-8")
            (session / "raw" / "00-rules" / "extra.md").write_text("[断链](nothing.md)", encoding="utf-8")
            self.assertEqual(validate(session), [])


class ShippedFilesTest(unittest.TestCase):
    def test_summary_spec_template_and_manifest_template_follow_the_layout(self) -> None:
        spec = json.loads(new_session.read_template(ROOT, "summary.json"))
        page = make_summary.render(spec)
        self.assertEqual(len(re.findall(r"<h2>", page)), 3)
        manifest = json.loads(new_session.read_template(ROOT, "manifest.json"))
        self.assertEqual(manifest["output_standard"], validate_session.OUTPUT_STANDARD)
        self.assertIsNone(manifest["project"])

    def test_shared_layout_scripts_are_required_files(self) -> None:
        for name in ("scripts/check_output_layout.py", "scripts/make_summary.py", "scripts/deliver.py", "scripts/test_session_layout.py"):
            self.assertIn(name, validate_skill.REQUIRED)
            self.assertTrue((ROOT / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
