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


# ---- the UI kit: references/ui-kit/ui.css carries the dark theme of a product front end -----------------------------------------------------
KIT = Path(__file__).resolve().parents[1] / "references" / "ui-kit"


def block_after(css: str, opener: str) -> str:
    """The body of the first {...} that follows opener (braces balanced)."""
    start = css.index(opener)
    open_at = css.index("{", start)
    depth, i = 0, open_at
    while True:
        depth += (css[i] == "{") - (css[i] == "}")
        if depth == 0:
            return css[open_at + 1:i]
        i += 1


def declarations(body: str) -> dict[str, str]:
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return {m.group(1): re.sub(r"\s+", " ", m.group(2)).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body)}


def oklch_value(value: str, hue: float, chroma: float) -> str:
    """One `oklch(L C H)` custom-property value as a hex colour; var(--brand-h/--brand-c) and calc(var(--brand-c) * k) are filled in."""
    value = re.sub(r"calc\(var\(--brand-c\)\s*\*\s*([\d.]+)\)", lambda m: str(chroma * float(m.group(1))), value)
    value = value.replace("var(--brand-c)", str(chroma)).replace("var(--brand-h)", str(hue))
    lightness, c, h = (float(x) for x in re.fullmatch(r"oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)", value.strip()).groups())
    return md.oklch_hex(lightness, c, h)


def mix_oklab(base: str, other: str, percent: float) -> str:
    l1, c1, h1 = md.hex_to_oklch(base)
    l2, c2, h2 = md.hex_to_oklch(other)
    import math
    a = (1 - percent / 100) * c1 * math.cos(math.radians(h1)) + percent / 100 * c2 * math.cos(math.radians(h2))
    b = (1 - percent / 100) * c1 * math.sin(math.radians(h1)) + percent / 100 * c2 * math.sin(math.radians(h2))
    return md.oklch_hex((1 - percent / 100) * l1 + percent / 100 * l2, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


class UiKitDarkTest(unittest.TestCase):
    CSS = (KIT / "ui.css").read_text(encoding="utf-8")

    def test_the_system_block_and_the_manual_block_declare_the_same_tokens(self) -> None:
        media = declarations(block_after(self.CSS[self.CSS.index("@media (prefers-color-scheme: dark)"):], ":root:not([data-theme=\"light\"])"))
        manual = declarations(block_after(self.CSS, ":root[data-theme=\"dark\"] {"))
        self.assertGreater(len(media), 30)
        self.assertEqual(media, manual)
        self.assertIn("color-scheme: dark", self.CSS)
        self.assertIn(":root[data-theme=\"light\"] { color-scheme: light; }", self.CSS)

    def test_dark_palette_passes_at_every_brand_hue(self) -> None:
        dark = declarations(block_after(self.CSS, ":root[data-theme=\"dark\"] {"))
        for hue in range(0, 360, 30):
            for chroma in (0.04, 0.085, 0.12):
                with self.subTest(hue=hue, chroma=chroma):
                    col = {k: oklch_value(v, hue, chroma) for k, v in dark.items() if v.startswith("oklch(") and "/" not in v}
                    grounds = {k: col[k] for k in ("--bg", "--surface", "--surface-2", "--surface-3")}
                    grounds["--raise-4"] = mix_oklab(col["--surface"], "#FFFFFF", 11)
                    for token, floor in (("--text-1", 7.0), ("--text-2", 4.5), ("--text-3", 4.5)):
                        worst = min(cc.contrast(col[token], g) for g in grounds.values())
                        self.assertGreaterEqual(worst, floor, token)
                    brand_grounds = {**grounds, "--brand-soft": col["--brand-soft"]}
                    self.assertGreaterEqual(min(cc.contrast(col["--brand-ink"], g) for g in brand_grounds.values()), 4.5, "--brand-ink")
                    self.assertGreaterEqual(cc.contrast("#FFFFFF", col["--brand"]), 4.5, "white on --brand")
                    self.assertGreaterEqual(cc.contrast("#FFFFFF", col["--bad"]), 4.5, "white on --bad")
                    self.assertGreaterEqual(cc.contrast(col["--brand"], col["--surface"]), 3.0, "--brand on the card face")
                    self.assertGreaterEqual(cc.contrast(col["--line"], col["--surface"]), 1.2, "--line on the card face")
                    for name in ("ok", "warn", "bad", "info"):
                        self.assertGreaterEqual(min(cc.contrast(col[f"--{name}-ink"], g) for g in (*grounds.values(), col[f"--{name}-soft"])), 4.5, f"--{name}-ink")
                        self.assertGreaterEqual(cc.contrast(col[f"--{name}"], col["--surface"]), 3.0, f"--{name} on the card face")

    def test_surfaces_climb_with_height(self) -> None:
        dark = declarations(block_after(self.CSS, ":root[data-theme=\"dark\"] {"))
        col = {k: oklch_value(v, 165, 0.085) for k, v in dark.items() if v.startswith("oklch(") and "/" not in v}
        ladder = [col["--bg"], col["--surface"], col["--surface-2"], col["--surface-3"]]
        self.assertTrue(all(cc.luminance(a) < cc.luminance(b) for a, b in zip(ladder, ladder[1:])))
        self.assertTrue(all(f"--raise-{n}" in dark for n in (2, 3, 4)))
        self.assertIn("--raise-4: var(--surface)", self.CSS, "light: a raised surface is the white card face")

    def test_raised_components_use_the_raised_surfaces(self) -> None:
        for needle in ("dialog.dlg { margin: auto; border: 0; padding: 0; background: var(--raise-4)", "[popover].menu {", "background: var(--raise-3)"):
            self.assertIn(needle, self.CSS)
        self.assertIn("background: var(--scrim)", self.CSS)

    def test_every_layout_page_has_the_head_script_and_the_three_way_control(self) -> None:
        pages = sorted((KIT / "layouts").glob("*.html"))
        self.assertEqual(len(pages), 6)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=page.name):
                self.assertIn("window.luzTheme", text)
                self.assertLess(text.index("window.luzTheme"), text.index('href="../ui.css"'), "the script runs before the style sheet")
                self.assertIn("UI.appearance(", text)
                self.assertNotRegex(text, r"color-scheme\s*:\s*dark")

    def test_the_demo_panel_and_the_control_offer_the_three_modes(self) -> None:
        js = (KIT / "ui.js").read_text(encoding="utf-8")
        self.assertIn("[['system', '跟随系统'], ['light', '浅色'], ['dark', '深色']]", js)
        self.assertIn("group('外观'", js)
        self.assertIn("'aria-label': '外观'", js)
        self.assertIn("role: 'radiogroup'", js)


class CommerceKitSkeletonTest(unittest.TestCase):
    """references/templates.txt carries commerce-kit.html, the skeleton of a trade and marketing interface (moved here from Luz-System):
    a product interface, so it ships both themes and the 跟随系统 / 浅色 / 深色 switch, and keeps its own type scale. The page that says how its effects
    are drawn is references/ui-recipes.html; the finished example is references/ui-kit/commerce-kit/."""

    ROOT = Path(__file__).resolve().parents[1]

    def skeleton(self) -> str:
        from new_session import read_template
        return read_template(self.ROOT, "commerce-kit.html")

    def test_the_skeleton_carries_both_themes_and_the_switch(self) -> None:
        text = self.skeleton()
        self.assertIn("@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"])", text)
        self.assertIn(':root[data-theme="dark"]{color-scheme:dark', text)
        self.assertIn(':root[data-theme="light"]{color-scheme:light}', text)
        self.assertIn('role="radiogroup" aria-label="外观"', text)
        self.assertEqual(len(re.findall(r'<button type="button" role="radio"', text)), 3)
        for label in ("跟随系统", "浅色", "深色"):
            self.assertIn(f">{label}</button>", text)
        self.assertIn('"luz-theme"', text)
        self.assertIn("window.luzTheme", text)
        # the script runs before the style sheet, and the storage is guarded
        self.assertLess(text.index("luz-theme"), text.index("<style>"))
        self.assertRegex(text, r"try \{[^}]*localStorage")

    def test_the_two_blocks_hold_the_same_variables(self) -> None:
        text = self.skeleton()
        media = re.search(r'@media \(prefers-color-scheme:dark\)\{:root:not\(\[data-theme="light"\]\)\{(.*?)\}\}', text, re.S).group(1)
        attr = re.search(r':root\[data-theme="dark"\]\{(.*?)\}', text, re.S).group(1)
        self.assertEqual(media, attr)

    def test_dark_values_are_the_theme_library_values(self) -> None:
        text = self.skeleton().lower()
        coffee = DATA["themes"]["coffee"]["dark"]
        for key in ("canvas", "surface", "action", "actionText", "actionTint", "accent", "accentTint", "line"):
            self.assertIn(coffee[key].lower(), text, key)
        self.assertIn(DATA["shared"]["dark"]["dangerFill"].lower(), text, "price fills use dangerFill in the dark")

    def test_a_product_skeleton_keeps_its_own_type_scale(self) -> None:
        self.assertNotIn("luz-md-type:start", self.skeleton())

    def test_the_page_the_card_and_the_example_are_in_place(self) -> None:
        import validate_skill
        self.assertIn(("ui-recipes.html", "recipes", "界面实现参考"), validate_skill.RULE_PAGES)
        self.assertIn("references/ui-recipes.html", validate_skill.REQUIRED)
        example = self.ROOT / "references" / "ui-kit" / "commerce-kit"
        self.assertTrue((example / "index.html").is_file())
        self.assertTrue((example / "screenshot-home.png").is_file())
        self.assertGreaterEqual(len(list((example / "assets").glob("*.webp"))), 10)
        import context
        card = context.load_json(context.CARDS_FILE, {})["cards"]["interface-recipes"]
        self.assertIn("ui-recipes.html", [s["page"] for s in card["sections"]])
        self.assertTrue(any("ui-ownership.md" in line for line in card["tools"] + card["checks"]))


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
