"""The dark mapping of the theme library (visual-design.html 深色与浅色两套主题): every theme has one, it passes the contrast rules,
make_dark.py derives it from the light mapping, and check_contrast.py rejects a broken one."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_contrast as cc  # noqa: E402
import make_dark as md  # noqa: E402

DATA = json.loads(md.THEMES.read_text(encoding="utf-8"))


def failing(theme_id: str, data: dict) -> list[str]:
    return [label for label, ok, _ in cc.dark_rules(theme_id, data["themes"][theme_id], data["shared"]) if not ok]


class LibraryTest(unittest.TestCase):
    def test_every_theme_has_a_complete_dark_mapping_that_passes(self) -> None:
        self.assertGreaterEqual(len(DATA["themes"]), 25)
        for theme_id in DATA["themes"]:
            with self.subTest(theme=theme_id):
                dark = DATA["themes"][theme_id]["dark"]
                self.assertTrue(set(cc.DARK_THEME_KEYS) <= set(dark), set(cc.DARK_THEME_KEYS) - set(dark))
                self.assertEqual(failing(theme_id, DATA), [])
        self.assertTrue(set(cc.DARK_SHARED_KEYS) <= set(DATA["shared"]["dark"]))

    def test_check_contrast_passes_the_whole_library(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = cc.main([])
        self.assertEqual(code, 0, out.getvalue()[-2000:])

    def test_dark_is_a_second_palette_not_an_inversion(self) -> None:
        for theme_id, theme in DATA["themes"].items():
            dark = theme["dark"]
            with self.subTest(theme=theme_id):
                self.assertLess(cc.luminance(dark["canvas"]), cc.luminance(dark["surface"]))
                self.assertLess(cc.luminance(dark["surface"]), 0.05)
                self.assertGreater(cc.luminance(DATA["shared"]["dark"]["ink"]), 0.7)
        # the light ink is not the dark ink turned round: the dark ink is its own warm off-white
        self.assertNotEqual(DATA["shared"]["dark"]["ink"], DATA["shared"]["ink"])

    def test_each_theme_keeps_its_own_hue(self) -> None:
        for theme_id, theme in DATA["themes"].items():
            if cc.chroma(theme["action"]) < 20:
                continue
            with self.subTest(theme=theme_id):
                self.assertLessEqual(cc.hue_gap(theme["dark"]["action"], theme["action"]), 12)
                self.assertLessEqual(cc.hue_gap(theme["dark"]["actionText"], theme["action"]), 12)

    def test_five_levels_get_lighter_surfaces(self) -> None:
        mix = DATA["shared"]["dark"]["elevation"]["surfaceMix"]
        self.assertEqual(sorted(mix), ["level0", "level1", "level2", "level3", "level4"])
        values = [mix[f"level{i}"] for i in range(5)]
        self.assertEqual(values[:2], [0, 0])
        self.assertTrue(values[1] < values[2] < values[3] < values[4])

    def test_modules_of_a_light_theme_have_a_dark_version(self) -> None:
        theme = DATA["themes"]["ai-agent"]
        self.assertEqual(set(theme["dark"]["modules"]), set(theme["modules"]))


class RuleTest(unittest.TestCase):
    """A broken mapping is refused, one rule at a time."""

    def broken(self, mutate, theme_id: str = "xiangcai") -> list[str]:
        data = copy.deepcopy(DATA)
        mutate(data)
        return failing(theme_id, data)

    def test_missing_dark_or_missing_key(self) -> None:
        self.assertTrue(self.broken(lambda d: d["themes"]["xiangcai"].pop("dark")))
        self.assertTrue(self.broken(lambda d: d["themes"]["xiangcai"]["dark"].pop("actionText")))
        self.assertTrue(self.broken(lambda d: d["shared"]["dark"].pop("dangerFill")))

    def test_text_contrast_floors(self) -> None:
        self.assertIn("dark ink 在各层底上 >= 7", self.broken(lambda d: d["shared"]["dark"].update(ink="#8A8080")))
        self.assertIn("dark ink3 在各层底上 >= 4.5", self.broken(lambda d: d["shared"]["dark"].update(ink3="#5A5252")))
        self.assertIn("dark actionText 在各层底上 >= 4.5", self.broken(lambda d: d["themes"]["xiangcai"]["dark"].update(actionText="#7A3A36")))

    def test_action_needs_text_and_a_edge_against_the_surface(self) -> None:
        self.assertIn("dark onAction 在 action 上 >= 4.5", self.broken(lambda d: d["themes"]["xiangcai"]["dark"].update(action="#F08A84")))
        self.assertIn("dark action 对 canvas / surface >= 3", self.broken(lambda d: d["themes"]["xiangcai"]["dark"].update(action="#5A2A27")))

    def test_status_colours_and_fills(self) -> None:
        self.assertTrue(self.broken(lambda d: d["shared"]["dark"].update(danger="#7A2A2A")))
        self.assertIn("dark 白字在 dangerFill 上 >= 4.5", self.broken(lambda d: d["shared"]["dark"].update(dangerFill="#FF8A8A")))

    def test_a_light_surface_is_not_a_dark_theme(self) -> None:
        self.assertTrue(self.broken(lambda d: d["themes"]["xiangcai"]["dark"].update(canvas="#F5F5F5", surface="#FFFFFF")))
        self.assertTrue(self.broken(lambda d: d["themes"]["xiangcai"]["dark"].update(canvas="#2A2020", surface="#201818")))

    def test_hue_drift_is_refused(self) -> None:
        self.assertTrue(self.broken(lambda d: d["themes"]["xiangcai"]["dark"].update(action="#3B6FCB")))

    def test_elevation_ladder_and_shadows(self) -> None:
        def flat(d):
            d["shared"]["dark"]["elevation"]["surfaceMix"].update(level3=5, level4=5)

        def blue_ring(d):
            d["shared"]["dark"]["elevation"]["hairline"] = "rgba(0,0,0,.10)"

        def upward(d):
            d["shared"]["dark"]["elevation"]["level2"] = "0 -2px 4px rgba(0,0,0,.4), 0 -8px 16px rgba(0,0,0,.3)"

        for mutate in (flat, blue_ring, upward):
            data = copy.deepcopy(DATA)
            mutate(data)
            failed = [label for label, ok, _ in cc.elevation_rules(data["shared"]["dark"]["elevation"], dark=True) if not ok]
            self.assertTrue(failed, mutate.__name__)
        self.assertEqual([label for label, ok, _ in cc.elevation_rules(DATA["shared"]["dark"]["elevation"], dark=True) if not ok], [])

    def test_light_elevation_rules_are_unchanged(self) -> None:
        self.assertEqual([label for label, ok, _ in cc.elevation_rules(DATA["shared"]["elevation"]) if not ok], [])
        loud = dict(DATA["shared"]["elevation"], level1="0 1px 2px rgba(0,0,0,.4), 0 2px 6px rgba(0,0,0,.3)")
        self.assertTrue([label for label, ok, _ in cc.elevation_rules(loud) if not ok], "0.4 alpha is for dark only")


class GeneratorTest(unittest.TestCase):
    def test_oklch_round_trip(self) -> None:
        for color in ("#A8322D", "#4A5BD6", "#18794E", "#876800", "#808080", "#FFFFFF"):
            lightness, chroma, hue = md.hex_to_oklch(color)
            back = md.oklch_hex(lightness, chroma, hue)
            self.assertLessEqual(max(abs(a - b) for a, b in zip(cc.rgb(color), cc.rgb(back))), 1, color)

    def test_gamut_clamp_lowers_chroma_only(self) -> None:
        color = md.oklch_hex(0.3, 0.4, 265)
        self.assertRegex(color, r"^#[0-9A-F]{6}$")
        self.assertAlmostEqual(md.hex_to_oklch(color)[2], 265, delta=8)

    def test_solve_reaches_the_contrast_target_from_the_right_side(self) -> None:
        action = md.solve(30, 0.15, lambda c: cc.contrast("#FFFFFF", c) >= 4.6, highest=True)
        self.assertGreaterEqual(cc.contrast("#FFFFFF", action), 4.6)
        self.assertLess(cc.contrast("#FFFFFF", action), 4.9, "the lightest colour that still carries white text")
        text = md.solve(30, 0.12, lambda c: cc.contrast(c, "#201716") >= 6.5, highest=False)
        self.assertGreaterEqual(cc.contrast(text, "#201716"), 6.5)
        with self.assertRaises(ValueError):
            md.solve(30, 0.15, lambda c: False, highest=True)

    def test_derivation_is_deterministic_and_passes_for_every_theme(self) -> None:
        per_theme, shared_dark = md.derive_all(DATA)
        again, _ = md.derive_all(DATA)
        self.assertEqual(per_theme, again)
        data = copy.deepcopy(DATA)
        for theme_id, dark in per_theme.items():
            data["themes"][theme_id]["dark"] = dark
        data["shared"]["dark"] = shared_dark
        for theme_id in data["themes"]:
            with self.subTest(theme=theme_id):
                self.assertEqual(failing(theme_id, data), [])

    def test_stored_maps_are_what_the_generator_writes_unless_tuned(self) -> None:
        per_theme, _ = md.derive_all(DATA)
        same = [k for k, v in per_theme.items() if v == DATA["themes"][k]["dark"]]
        self.assertGreaterEqual(len(same), len(per_theme) // 2, "most stored maps are still the generator's own output")

    def test_keep_leaves_a_tuned_theme_alone(self) -> None:
        data = copy.deepcopy(DATA)
        data["themes"]["xiangcai"]["dark"]["line"] = "#444444"
        per_theme, _ = md.derive_all(data, {"xiangcai"})
        self.assertEqual(per_theme["xiangcai"]["line"], "#444444")

    def test_neutral_theme_keeps_a_light_button_with_dark_text(self) -> None:
        dark = DATA["themes"]["b2b-graphite"]["dark"]
        self.assertGreater(cc.luminance(dark["action"]), 0.6)
        self.assertLess(cc.luminance(dark["onAction"]), 0.05)

    def test_mix_white_matches_color_mix(self) -> None:
        self.assertEqual(md.mix_white("#000000", 50), "#808080")
        self.assertEqual(md.mix_white("#202020", 0), "#202020")


class PackageRuleTest(unittest.TestCase):
    def test_the_rule_pages_may_name_the_media_query_but_not_declare_a_dark_scheme(self) -> None:
        import validate_skill
        source = Path(validate_skill.__file__).read_text(encoding="utf-8")
        self.assertIn("(?<!prefers-)color-scheme", source)
        pattern = re.compile(r"(?<!prefers-)color-scheme\s*:\s*dark", re.I)
        self.assertIsNone(pattern.search("<code>@media (prefers-color-scheme: dark)</code>"))
        self.assertTrue(pattern.search(":root { color-scheme: dark; }"))
        page = (Path(validate_skill.__file__).resolve().parents[1] / "references" / "visual-design.html").read_text(encoding="utf-8")
        self.assertIn("深色与浅色两套主题", page)
        self.assertNotIn("用户明确要求深色时", page)
        self.assertIsNone(pattern.search(page), "the rule page declares no dark scheme itself")


if __name__ == "__main__":
    unittest.main()
