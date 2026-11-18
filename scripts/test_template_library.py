"""The mandatory template inventory must describe real Design files."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import template_library as library


class TemplateLibraryTests(unittest.TestCase):
    def test_registered_document_templates_have_existing_files(self):
        for identifier in ("reading-html", "docx", "docx-paginated", "xlsx", "table-pdf", "showcase", "html-templates-app",
                           "design-visual-board", "design-document-page"):
            ref = library.reference(identifier, "raw/deliverable")
            self.assertEqual(library.validate_references([ref]), [])
            self.assertTrue(ref["files"])

    def test_missing_forged_and_partial_template_references_fail(self):
        self.assertTrue(library.validate_references([]))
        valid = library.reference("reading-html", "raw/report.html")
        for changed in ([], [{"path": "../outside.py", "sha256": "0" * 64}],
                        [{**valid["files"][0], "sha256": "0" * 64}]):
            ref = copy.deepcopy(valid)
            ref["files"] = changed
            self.assertTrue(library.validate_references([ref]))

    def test_unknown_template_cannot_be_self_registered_in_a_record(self):
        with self.assertRaises(ValueError):
            library.reference("my-model-layout", "UI")

    def test_selection_is_bound_to_caller_stage_and_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = library.select(root, "luz-dev", "technical-plan", "reading-html", "docs/backend.html")
            value = library.read(path)
            self.assertEqual(value["caller"], "luz-dev")
            self.assertEqual(value["stage"], "technical-plan")
            self.assertEqual(value["template_uses"][0]["applies_to"], "docs/backend.html")
            self.assertEqual(library.validate_references(value["template_uses"]), [])

    def test_one_output_keeps_one_selection_however_its_path_is_spelt(self):
        """A relative and an absolute path of the same file replace each other; two entries would leave the writer unable to
        tell the original selection. Another file of the same name elsewhere keeps its own entry."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            library.select(root, "luz-dev", "technical-plan", "reading-html", "docs/backend.html")
            path = library.select(root, "luz-dev", "technical-plan", "reading-html", str(root / "docs" / "backend.html"))
            self.assertEqual(len(library.read(path)["template_uses"]), 1)
            library.require_selected(root, "luz-dev", "technical-plan", root / "docs" / "backend.html", "reading-html")
            library.select(root, "luz-dev", "technical-plan", "reading-html", r"docs\backend.html")
            library.select(root, "luz-dev", "technical-plan", "reading-html", "raw/docs/backend.html")
            self.assertEqual(sorted(item["applies_to"] for item in library.read(path)["template_uses"]), [r"docs\backend.html", "raw/docs/backend.html"])
            library.require_selected(root, "luz-dev", "technical-plan", root / "docs" / "backend.html", "reading-html")

    def test_research_renderer_reuses_the_existing_reading_template(self):
        document = library.render_reading("A < B", "<section><h2>Evidence</h2></section>")
        self.assertIn("<h1>A &lt; B</h1>", document)
        self.assertIn("<section><h2>Evidence</h2></section>", document)
        self.assertIn("--md-body: 18px", document)
        self.assertNotIn("{{", document)

    def test_formal_output_requires_a_selection_for_the_exact_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "docs" / "report.html"
            with self.assertRaises(ValueError):
                library.require_selected(root, "luz-dev", "technical-plan", target, "reading-html")
            library.select(root, "luz-dev", "technical-plan", "reading-html", "docs/report.html")
            selected = library.require_selected(root, "luz-dev", "technical-plan", target, "reading-html")
            self.assertEqual(selected["id"], "reading-html")

    def test_selection_cannot_be_claimed_for_a_different_target_or_reference_only_ui(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library.select(root, "luz-design", "design", "html-templates-app", "docs/02-产品开发/02-前端界面设计.html")
            with self.assertRaises(ValueError):
                library.require_selected(root, "luz-design", "design", root / "docs/02-产品开发/03-手机原型.html", "html-templates-app")
            with self.assertRaises(ValueError):
                library.require_selected(root, "luz-design", "design", root / "docs/02-产品开发/02-前端界面设计.html", "html-templates-web")

    def test_raw_source_and_final_file_with_the_same_name_need_distinct_selections(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "raw" / "report.xlsx"
            final = root / "report.xlsx"
            library.select(root, "luz-design", "design", "xlsx", final.name)
            with self.assertRaisesRegex(ValueError, "准确输出位置"):
                library.require_selected(root, "luz-design", "design", raw, "xlsx")
            library.select(root, "luz-design", "design", "xlsx", "raw/report.xlsx")
            raw.parent.mkdir(exist_ok=True)
            raw.write_bytes(b"OFFLINE_SOURCE")
            library.record_output(root, "luz-design", "design", raw, "xlsx", generator="offline test fixture")
            library.require_selected(root, "luz-design", "design", raw, "xlsx", phase="post")
            with self.assertRaisesRegex(ValueError, "产出不存在"):
                library.require_selected(root, "luz-design", "design", final, "xlsx", phase="post")

    def test_project_docs_selection_cannot_authorize_a_state_working_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state, project = root / "state", root / "deliver"
            state.mkdir()
            (state / "project.json").write_text(json.dumps({"deliver_root": str(project)}), encoding="utf-8")
            library.select(state, "luz-design", "design", "xlsx", "docs/01-需求对接/01-report.xlsx")
            final = project / "docs" / "01-需求对接" / "01-report.xlsx"
            library.require_selected(state, "luz-design", "design", final, "xlsx")
            with self.assertRaisesRegex(ValueError, "准确输出位置"):
                library.require_selected(state, "luz-design", "design", state / "docs" / "01-需求对接" / final.name, "xlsx")


if __name__ == "__main__":
    unittest.main()
