"""The component library registry (references/component-libraries.json) and what reads it."""
import copy
import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit_rendered  # noqa: E402
import check_component_library  # noqa: E402
import validate_skill  # noqa: E402

REGISTRY = json.loads((HERE.parent / "references" / "component-libraries.json").read_text(encoding="utf-8"))


class RegistryTests(unittest.TestCase):
    def test_the_registry_is_complete(self):
        self.assertEqual(validate_skill.component_library_errors(), [])
        libs = REGISTRY["libraries"]
        for surface in ("admin", "h5", "miniapp"):
            self.assertTrue(any(surface in lib["surfaces"] for lib in libs.values()), surface)

    def test_a_library_without_what_the_checks_read_is_refused(self):
        for field, value, needle in (("prefix", ["el"], "prefix"), ("prefix", [], "prefix"), ("surfaces", ["desktop"], "surfaces"), ("docs", "http://x.test", "docs"),
                                     ("verified", "yesterday", "verified"), ("theme", "", "theme"), ("license", "", "license")):
            data = copy.deepcopy(REGISTRY)
            data["libraries"]["element-plus"][field] = value
            errors = validate_skill.component_library_errors(data)
            self.assertTrue(any(needle in e for e in errors), (field, errors))

    def test_every_library_says_how_it_goes_dark_or_that_this_is_unchecked(self):
        for key, lib in REGISTRY["libraries"].items():
            self.assertIsInstance(lib["dark"], str, key)
            self.assertTrue(lib["darkSource"].strip(), key)
            if not lib["dark"]:
                self.assertIn("未核对", lib["darkSource"], key)
        for field, value in (("dark", None), ("darkSource", "")):
            data = copy.deepcopy(REGISTRY)
            data["libraries"]["vant"][field] = value
            self.assertTrue(any("dark" in e for e in validate_skill.component_library_errors(data)), field)
        # the three mechanisms the user named are registered
        self.assertIn("css-vars", REGISTRY["libraries"]["element-plus"]["dark"])
        self.assertIn("darkAlgorithm", REGISTRY["libraries"]["ant-design"]["dark"])
        self.assertIn("dark", REGISTRY["libraries"]["vant"]["dark"])

    def test_two_libraries_may_not_share_a_prefix_on_one_surface(self):
        data = copy.deepcopy(REGISTRY)
        data["libraries"]["arco-design"]["prefix"] = ["el-"]
        self.assertTrue(any("could not tell" in e for e in validate_skill.component_library_errors(data)))
        data = copy.deepcopy(REGISTRY)                       # the same prefix on different surfaces is allowed: TDesign web and mini program
        self.assertEqual(REGISTRY["libraries"]["tdesign"]["prefix"], REGISTRY["libraries"]["tdesign-miniprogram"]["prefix"])
        self.assertEqual(validate_skill.component_library_errors(data), [])

    def test_the_audit_resolves_ids_and_prefixes(self):
        self.assertEqual(audit_rendered.resolve_library(["element-plus"]), ["el-"])
        self.assertEqual(audit_rendered.resolve_library(["el-", "t-"]), ["el-", "t-"])
        self.assertEqual(audit_rendered.resolve_library([]), [])
        with self.assertRaises(SystemExit):
            audit_rendered.resolve_library(["no-such-library"])

    def test_the_rule_card_for_components_carries_the_rule_the_registry_and_the_check(self):
        import context
        text, _ = context.make_card("interface-components", [])
        for needle in ("组件与组件库", "component-libraries.json", "--library", "自造控件", "浅色"):
            self.assertIn(needle, text)
        self.assertIn("frontend-real-components-light-premium", text)       # the user's preference prints on the card


class LuzKitTests(unittest.TestCase):
    """luz-kit is the library of this repository: found by the attribute data-cid on the component root, prefixes are root classes (mpcard003, adtbl001)."""

    kit = REGISTRY["libraries"]["luz-kit"]

    def test_it_is_registered_with_what_the_audit_and_the_prototype_check_read(self):
        kit = self.kit
        self.assertEqual(validate_skill.component_library_errors(), [])
        self.assertEqual(kit["attr"], "data-cid")
        self.assertEqual(set(kit["surfaces"]), {"miniapp", "h5", "admin"})
        self.assertEqual(kit["verified"], "2026-11-04")
        self.assertEqual(kit["license"], "项目自有")
        self.assertTrue((HERE.parent / kit["docs"]).is_file(), kit["docs"])
        for token in ("--p ", "--pd", "--pt", "--pm", "--ga", "--gb", "--p-rgb"):
            self.assertIn(token, kit["theme"])
        for token in ("--p", "--pd", "--pt", "--pm", "--ga", "--gb", "--p-rgb"):
            self.assertIn(f"'{token}'", (check_component_library.SRC / "kit.js").read_text(encoding="utf-8"))   # the tokens themeVars() sets
        self.assertEqual(len(re.findall(r"\{ id: '[a-z]+', name: '", (check_component_library.SRC / "kit.js").read_text(encoding="utf-8"))), 8)   # eight themes

    def test_it_describes_the_dark_appearance_it_has(self):
        dark = self.kit["dark"]
        self.assertFalse(dark.startswith("无"), "the library has a dark appearance now")
        for word in ("dark", "light", "prefers-color-scheme", "data-theme", "setAppearance", "令牌", "README", "例外"):
            self.assertIn(word, dark)
        self.assertTrue(self.kit["darkSource"].strip())
        self.assertIn("setAppearance", (check_component_library.SRC / "kit.js").read_text(encoding="utf-8"))   # what the field promises is in the source

    def test_the_prefixes_are_exactly_the_domain_and_category_codes_of_the_taxonomy(self):
        cats, _ = check_component_library.read_taxonomy(check_component_library.SRC)
        want = {dom + code.lower() for dom, rows in cats.items() for code, _ in rows}
        self.assertEqual(set(self.kit["prefix"]), want)
        self.assertEqual(len(self.kit["prefix"]), len(want))

    def test_every_component_root_class_starts_with_a_registered_prefix(self):
        lib = check_component_library.read_library()
        prefixes = tuple(self.kit["prefix"])
        for comp in lib.comps:
            if not comp.legacy:
                self.assertTrue(comp.root.startswith(prefixes), comp.id)
                self.assertTrue(re.fullmatch(r"(mp|ad)[a-z]+\d{3}", comp.root), comp.id)

    def test_the_prototype_check_of_luz_project_counts_kinds_by_those_prefixes(self):
        # Luz-Project counts library components as class names that start with a prefix: the root classes must be found, and nothing but them
        pattern = r"(?<![\w-])((?:" + "|".join(self.kit["prefix"]) + r")[a-z0-9]+(?:-[a-z0-9]+)*)"
        found = set(re.findall(pattern, '<div class="mpcard003 adtbl001 mphdr001-x"><b class="button primary">'))
        self.assertEqual(found, {"mpcard003", "adtbl001", "mphdr001-x"})

    def test_the_audit_reads_it_by_attribute(self):
        self.assertEqual(audit_rendered.resolve_library(["luz-kit"]), [])
        self.assertEqual(audit_rendered.resolve_library_attrs(["luz-kit"]), ["data-cid"])
        self.assertEqual(audit_rendered.resolve_library_attrs(["element-plus", "el-"]), [])

    def test_a_library_with_attr_follows_its_own_rules_and_the_others_keep_theirs(self):
        def errors(change):
            data = copy.deepcopy(REGISTRY)
            change(data["libraries"]["luz-kit"])
            return validate_skill.component_library_errors(data)

        self.assertEqual(errors(lambda k: None), [])
        self.assertTrue(any("prefix" in e for e in errors(lambda k: k.update(prefix=["mp-card"]))))
        self.assertTrue(any("prefix" in e for e in errors(lambda k: k.update(prefix=["MPCARD"]))))
        self.assertTrue(any("docs" in e for e in errors(lambda k: k.update(docs="references/component-library/NOPE.md"))))
        self.assertTrue(any("docs" in e for e in errors(lambda k: k.update(docs="http://x.test"))))
        self.assertTrue(any("attr" in e for e in errors(lambda k: k.update(attr="cid"))))
        data = copy.deepcopy(REGISTRY)                         # without attr the old rules apply: a hyphenated prefix and an https link
        for field, value in (("prefix", ["mpcard"]), ("docs", "references/component-library/README.md")):
            broken = copy.deepcopy(data)
            del broken["libraries"]["luz-kit"]["attr"]
            broken["libraries"]["luz-kit"][field] = value
            self.assertTrue(any(field in e for e in validate_skill.component_library_errors(broken)), field)
        data["libraries"]["element-plus"]["docs"] = "references/component-library/README.md"
        self.assertTrue(any("docs" in e for e in validate_skill.component_library_errors(data)))


if __name__ == "__main__":
    unittest.main()
