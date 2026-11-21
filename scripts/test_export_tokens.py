"""export_tokens.py: every theme exports to a valid W3C design tokens file whose constants match the rule page."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import export_tokens as et  # noqa: E402

PAGE = (Path(__file__).resolve().parents[1] / "references" / "visual-design.html").read_text(encoding="utf-8")
DATA = et.load_themes()


def quiet(func, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        return func(*args), out.getvalue()


class ExportTest(unittest.TestCase):
    def test_every_theme_exports_a_valid_file(self) -> None:
        for theme_id in DATA["themes"]:
            with self.subTest(theme=theme_id):
                self.assertEqual(et.check_tokens(et.build(theme_id, DATA, surface='reference')), [])

    def test_colours_round_trip_to_the_theme(self) -> None:
        doc = et.build('ai-agent', DATA, surface='reference')
        theme = DATA["themes"]["ai-agent"]
        self.assertEqual(doc["color"]["brand"]["action"]["$value"]["hex"].upper(), theme["action"].upper())
        self.assertEqual(doc["color"]["surface"]["canvas"]["$value"]["hex"].upper(), theme["canvas"].upper())
        self.assertEqual(doc["color"]["scale"]["6"]["$value"]["hex"].upper(), theme["action"].upper())
        self.assertEqual(doc["color"]["module"]["demo"]["solid"]["$value"]["hex"].upper(), theme["modules"]["demo"]["solid"].upper())
        self.assertEqual(doc["color"]["text"]["ink"]["$value"]["hex"].upper(), DATA["shared"]["ink"].upper())

    def test_shadows_keep_the_two_layers_of_each_level(self) -> None:
        doc = et.build('xiangcai', DATA, surface='reference')
        for level in ("level-1", "level-2", "level-3", "level-4"):
            layers = doc["shadow"][level]["$value"]
            self.assertEqual(len(layers), 2)
            self.assertTrue(all(layer["offsetX"]["value"] == 0 and layer["offsetY"]["value"] > 0 for layer in layers))
        self.assertEqual(doc["shadow"]["level-1"]["$value"][0]["offsetY"], {"value": 1, "unit": "px"})

    def test_typography_roles_reference_the_font_tokens(self) -> None:
        doc = et.build('xiangcai', DATA, surface='reference')
        body = doc["typography"]["body"]["$value"]
        self.assertEqual(body["fontFamily"], "{font.family.base}")
        self.assertEqual(body["fontWeight"], "{font.weight.regular}")
        self.assertAlmostEqual(body["lineHeight"] * body["fontSize"]["value"], 22)
        self.assertEqual(len(doc["typography"]) - 1, len(et.TYPE_ROLES))

    def test_every_theme_exports_light_and_dark_in_extensions_mode(self) -> None:
        for theme_id, theme in DATA["themes"].items():
            with self.subTest(theme=theme_id):
                doc = et.build(theme_id, DATA, surface='reference')
                self.assertEqual(doc["$extensions"]["design.luz"]["modes"], ["light", "dark"])
                action = doc["color"]["brand"]["action"]
                self.assertEqual(action["$value"]["hex"].upper(), theme["action"].upper())
                self.assertEqual(action["$extensions"]["mode"]["dark"]["hex"].upper(), theme["dark"]["action"].upper())
                self.assertEqual(doc["color"]["text"]["ink"]["$extensions"]["mode"]["dark"]["hex"].upper(), DATA["shared"]["dark"]["ink"].upper())
                self.assertEqual(doc["color"]["brand"]["on-action"]["$extensions"]["mode"]["dark"]["hex"].upper(), theme["dark"]["onAction"].upper())
                self.assertEqual(et.check_tokens(doc), [])

    def test_dark_values_cover_surfaces_status_lines_and_shadows(self) -> None:
        doc = et.build('ai-agent', DATA, surface='reference')
        dark = DATA["themes"]["ai-agent"]["dark"]
        raised = [doc["color"]["surface"][k]["$extensions"]["mode"]["dark"]["hex"] for k in ("card", "raised-2", "raised-3", "raised-4")]
        self.assertEqual(raised[0].upper(), dark["surface"].upper())
        self.assertEqual(len(set(raised)), 4, "each dark level is a lighter surface")
        self.assertEqual(doc["color"]["status"]["danger-fill"]["$value"]["hex"].upper(), DATA["shared"]["danger"].upper())
        self.assertEqual(doc["color"]["status"]["danger-fill"]["$extensions"]["mode"]["dark"]["hex"].upper(), DATA["shared"]["dark"]["dangerFill"].upper())
        self.assertEqual(doc["color"]["line"]["hairline"]["$extensions"]["mode"]["dark"]["hex"], "#ffffff")
        self.assertEqual(doc["color"]["module"]["demo"]["solid"]["$extensions"]["mode"]["dark"]["hex"].upper(), dark["modules"]["demo"]["solid"].upper())
        for level in ("level-1", "level-2", "level-3", "level-4"):
            layers = doc["shadow"][level]["$extensions"]["mode"]["dark"]
            self.assertEqual(len(layers), 2)
        self.assertNotIn("$extensions", doc["color"]["scale"]["6"], "the ten-step scale is light-only")

    def test_light_only_export_has_no_modes_and_still_validates(self) -> None:
        doc = et.build("xiangcai", DATA, with_dark=False,surface='reference')
        self.assertNotIn("$extensions", doc)
        self.assertNotIn("$extensions", doc["color"]["brand"]["action"])
        self.assertEqual(et.check_tokens(doc), [])
        self.assertTrue(et.check_tokens(doc, require_dark=True), "--require-dark asks for the dark values")

    def test_check_requires_both_modes_of_a_file_that_declares_them(self) -> None:
        doc = et.build('xiangcai', DATA, surface='reference')
        del doc["color"]["brand"]["action"]["$extensions"]
        errors = et.check_tokens(doc)
        self.assertTrue(any("color.brand.action: no dark value" in e for e in errors), errors)
        doc = et.build('xiangcai', DATA, surface='reference')
        doc["shadow"]["level-2"].pop("$extensions")
        self.assertTrue(any("shadow.level-2" in e for e in et.check_tokens(doc)))

    def test_a_malformed_dark_value_is_reported_like_a_light_one(self) -> None:
        doc = et.build('xiangcai', DATA, surface='reference')
        doc["color"]["brand"]["action"]["$extensions"]["mode"]["dark"]["components"] = [2, 0, 0]
        self.assertTrue(any("[dark]" in e for e in et.check_tokens(doc)))

    def test_unknown_theme_is_refused(self) -> None:
        with self.assertRaises(KeyError):
            et.build("no-such-theme", DATA)


class RulePageTest(unittest.TestCase):
    """The constants are the rule page's values; a change on one side fails here."""

    def test_spacing_scale(self) -> None:
        numbers = "、".join(str(v) for v in et.SPACING)
        self.assertIn(f"间距只取 4 的倍数：{numbers}", PAGE)

    def test_type_roles(self) -> None:
        for role, (size, line, _, _) in et.TYPE_ROLES.items():
            self.assertIn(f"{size} / {line}", PAGE, role)

    def test_radius_steps(self) -> None:
        for name, value in et.RADIUS.items():
            self.assertRegex(PAGE, rf"<tr><td>[^<]*</td><td>[^<]*\b{value}\b[^<]*</td></tr>", name)

    def test_motion_tokens(self) -> None:
        for name, (curve, _) in et.EASINGS.items():
            self.assertIn("cubic-bezier(" + ", ".join(f"{v:g}" for v in curve) + ")", PAGE, name)
        for name, (ms, _) in et.DURATIONS.items():
            self.assertRegex(PAGE, rf"<td>(?:{ms}|{ms}–\d+|\d+–{ms})</td>", name)

    def test_font_stack_matches_the_page(self) -> None:
        self.assertIn("苹方、微软雅黑、思源黑体依次回退", PAGE)
        self.assertEqual(et.FONT_STACK[:3], ["PingFang SC", "Microsoft YaHei", "Noto Sans SC"])


class CheckerTest(unittest.TestCase):
    def errors(self, mutate) -> list[str]:
        doc = et.build('ai-agent', DATA, surface='reference')
        mutate(doc)
        return et.check_tokens(doc)

    def test_names_never_hold_braces_or_dots(self) -> None:
        self.assertTrue(self.errors(lambda d: d["space"].update({"a.b": et.token(et.px(4))})))

    def test_colour_components_and_hex_must_agree(self) -> None:
        def mismatch(doc):
            doc["color"]["brand"]["action"]["$value"]["hex"] = "#000000"

        def over(doc):
            doc["color"]["brand"]["action"]["$value"]["components"] = [0.5, 1.2, 0]

        self.assertTrue(any("does not match" in e for e in self.errors(mismatch)))
        self.assertTrue(any("0 to 1" in e for e in self.errors(over)))

    def test_dimension_needs_a_unit(self) -> None:
        def mutate(doc):
            doc["space"]["4"]["$value"] = {"value": 4}

        self.assertTrue(any("unit" in e for e in self.errors(mutate)))

    def test_references_must_resolve(self) -> None:
        def mutate(doc):
            doc["typography"]["body"]["$value"]["fontFamily"] = "{font.family.missing}"

        self.assertTrue(any("does not resolve" in e for e in self.errors(mutate)))

    def test_cubic_bezier_x_values_stay_in_range(self) -> None:
        def mutate(doc):
            doc["easing"]["standard"]["$value"] = [1.5, 0, 0, 1]

        self.assertTrue(self.errors(mutate))


class ApplicationExportTest(unittest.TestCase):
    def test_all_application_themes_match_the_rendering_contract(self):
        for theme_id in DATA["themes"]:
            doc=et.build(theme_id,DATA)
            self.assertEqual(et.application_token_errors(doc),[],theme_id)
            self.assertEqual(doc["color"]["status"]["success"]["$value"]["hex"],"#28599b")
            self.assertNotIn("dark",et.declared_modes(doc))

    def test_custom_theme_input_and_reference_are_distinct(self):
        code,stdout=quiet(et.main,["--application-themes","--themes",str(et.THEMES)])
        self.assertEqual(code,0)
        data=json.loads(stdout)
        self.assertEqual(data["themes"]["enterprise-navy"]["navBg"],"#FFFFFF")
        self.assertNotIn("source",data["themes"]["enterprise-navy"])
        original=et.build("enterprise-navy",DATA,surface="reference")
        self.assertTrue(et.application_token_errors(original))
        product=et.build("enterprise-navy",DATA)
        product["color"]["brand"]["accent"]["$value"]=et.to_color("#00AA70")
        self.assertTrue(any("绿色" in msg for msg in et.application_token_errors(product)))


class CliTest(unittest.TestCase):
    def test_list_write_and_check(self) -> None:
        code, out = quiet(et.main, ["--list"])
        self.assertEqual(code, 0)
        self.assertIn("ai-agent", out)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "design-tokens.tokens.json"
            code, _ = quiet(et.main, ["ai-agent", "--out", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["color"]["$type"], "color")
            code, _ = quiet(et.main, ["--check", str(target)])
            self.assertEqual(code, 0)
            broken = json.loads(target.read_text(encoding="utf-8"))
            broken["space"]["4"]["$value"] = 4
            target.write_text(json.dumps(broken), encoding="utf-8")
            code, _ = quiet(et.main, ["--check", str(target)])
            self.assertEqual(code, 1)

    def test_file_name_and_theme_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            code, _ = quiet(et.main, ["ai-agent", "--out", str(Path(temp) / "tokens.json")])
            self.assertEqual(code, 2)
        code, _ = quiet(et.main, ["nope", "--out", "x.tokens.json"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
