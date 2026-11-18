"""audit_palette.py: a page keeps the hue of its theme and the shared status hues; a decorative extra hue or a letter avatar is reported."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_palette as ap  # noqa: E402

HERE = Path(__file__).resolve().parent


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


def audit(body: str, theme: str = "b2b-graphite", *extra: str) -> tuple[int, str]:
    html = f"<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><body style='margin:0;background:#fafafa;color:#18181b;font:16px sans-serif'>{body}</body></html>"
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "audit_palette.py"), str(page), "--theme", theme, *extra], capture_output=True, text=True, encoding="utf-8")
        return run.returncode, run.stdout


class HueTest(unittest.TestCase):
    def test_graphite_allows_its_blue_and_the_status_hues_only(self) -> None:
        hues = ap.theme_hues("b2b-graphite")
        self.assertTrue(hues)
        blue = ap.hue_of((0x25, 0x63, 0xEB))[0]
        self.assertLessEqual(min(ap.hue_gap(blue, h) for h in hues), ap.HUE_TOLERANCE)
        purple = ap.hue_of((0x6D, 0x28, 0xD9))[0]
        self.assertGreater(min(ap.hue_gap(purple, h) for h in hues), ap.HUE_TOLERANCE)

    def test_neutrals_and_near_white_are_not_hues(self) -> None:
        for rgb in ((24, 24, 27), (250, 250, 250), (113, 113, 122), (255, 255, 255)):
            self.assertFalse(ap.is_chromatic(rgb), rgb)

    def test_the_tints_and_shades_of_a_theme_hue_pass(self) -> None:
        got = ap.off_theme([["bg", 0xEF, 0xF6, 0xFF, 5000, "div.card"], ["text", 0x1D, 0x4E, 0xD8, 100, "a."]], ap.theme_hues("b2b-graphite"))
        self.assertEqual(got, {})

    def test_dark_grounds_are_hues_from_lightness_002_and_light_ones_from_006(self) -> None:
        tinted = (14, 10, 18)                     # a violet-tinted near-black ground: saturated, lightness 0.055
        self.assertFalse(ap.is_chromatic(tinted))
        self.assertTrue(ap.is_chromatic(tinted, "dark"))
        self.assertFalse(ap.is_chromatic((24, 24, 27), "dark"), "a zinc grey stays a neutral in the dark scheme too")
        self.assertFalse(ap.is_chromatic((236, 236, 240), "dark"))
        self.assertTrue(ap.is_chromatic((60, 16, 16), "dark") and ap.is_chromatic((60, 16, 16)))

    def test_the_dark_hue_budget_adds_the_dark_mapping_of_the_theme(self) -> None:
        data = {"shared": {"danger": "#c93644", "dark": {"danger": "#ff898a"}},
                "themes": {"t": {"action": "#2563eb", "dark": {"action": "#e0a030", "actionText": "#ffd27a"}}}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "themes.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            light = ap.theme_hues("t", path)
            dark = ap.theme_hues("t", path, "dark")
        orange = ap.hue_of((0xE0, 0xA0, 0x30))[0]
        self.assertGreater(min(ap.hue_gap(orange, h) for h in light), ap.HUE_TOLERANCE)
        self.assertLessEqual(min(ap.hue_gap(orange, h) for h in dark), ap.HUE_TOLERANCE)
        self.assertEqual(len(dark), len(light) + 3)

    def test_the_real_dark_mapping_of_graphite_keeps_its_hue_budget(self) -> None:
        hues = ap.theme_hues("b2b-graphite", scheme="dark")
        for rgb in ((0x60, 0xA5, 0xFA), (0x17, 0x25, 0x54), (0xFF, 0x89, 0x8A)):
            self.assertLessEqual(min(ap.hue_gap(ap.hue_of(rgb)[0], h) for h in hues), ap.HUE_TOLERANCE, rgb)


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class RenderedTest(unittest.TestCase):
    def test_a_page_with_the_theme_hue_and_status_colours_passes(self) -> None:
        code, out = audit("<p style='color:#2563eb'>链接</p><span style='background:#e4f3ec;color:#18794e;padding:2px 8px'>成功</span><div style='background:#27272a;color:#fff;padding:8px'>主按钮</div>")
        self.assertEqual((code, out.strip()), (0, "audit palette: ok"), out)

    def test_decorative_purple_bars_are_reported(self) -> None:
        code, out = audit("<div style='height:12px;width:300px;background:#6d28d9'></div><div style='height:12px;width:200px;background:#86198f'></div>")
        self.assertEqual(code, 1)
        self.assertIn("not a hue of theme b2b-graphite", out)

    def test_a_letter_avatar_is_reported_even_in_the_themes_own_hue(self) -> None:
        code, out = audit("<span class='avatar' style='display:inline-grid;place-items:center;width:32px;height:32px;border-radius:50%;background:#eff6ff;color:#2563eb'>周</span>")
        self.assertEqual(code, 1)
        self.assertIn("letter avatar", out)

    def test_an_icon_avatar_passes(self) -> None:
        code, out = audit("<span class='avatar' style='display:inline-grid;place-items:center;width:32px;height:32px;border-radius:50%;background:#f4f4f5'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#52525b' stroke-width='2'><circle cx='12' cy='8' r='4'/></svg></span>")
        self.assertEqual((code, out.strip()), (0, "audit palette: ok"), out)

    def test_the_unknown_theme_is_an_error(self) -> None:
        code, _ = audit("<p>x</p>", "no-such-theme")
        self.assertNotEqual(code, 0)


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class StageRampTest(unittest.TestCase):
    """The ordered-progress ramp (visual-design.html 有序进度状态的色阶) is the one chromatic exception: its own --stage tokens on data-stage elements."""

    RAMP = ":root{--stage-1:#5a6f7a;--stage-2:#48637b;--stage-4:#3c4679;--stage-5:#3f3674;--stage-6:#43236b}"

    def page(self, body: str) -> str:
        return f"<style>{self.RAMP}</style>{body}"

    def test_the_ramp_colours_on_stage_elements_are_not_an_off_theme_hue(self) -> None:
        body = ("<p><span data-stage-set='depth' data-stage='5' data-stage-n='5' style='color:#43236b'>后续跟进</span></p>"
                "<p><span data-stage-set='depth' data-stage='3' data-stage-n='5' style='color:#3c4679'>二轮</span></p>"
                "<div data-stage-set='depth' data-stage='5' data-stage-n='5' style='color:#43236b'>后续跟进 <i style='display:block;height:12px;width:200px;background:currentColor'></i></div>")
        code, out = audit(self.page(body))
        self.assertEqual((code, out.strip()), (0, "audit palette: ok"), out)

    def test_the_same_purple_anywhere_else_is_still_reported(self) -> None:
        code, out = audit(self.page("<p style='color:#43236b'>不是色阶的紫色文字</p>"))
        self.assertEqual(code, 1)
        self.assertIn("not a hue of theme b2b-graphite", out)

    def test_a_stage_element_in_a_colour_that_is_not_a_stage_token_is_reported(self) -> None:
        code, out = audit(self.page("<p data-stage-set='depth' data-stage='5' data-stage-n='5' style='color:#6d28d9'>后续跟进</p>"))
        self.assertEqual(code, 1)
        self.assertIn("not a hue of theme b2b-graphite", out)

    def test_a_page_without_stage_tokens_gets_no_exception(self) -> None:
        code, out = audit("<p data-stage-set='depth' data-stage='5' style='color:#43236b'>后续跟进</p>")
        self.assertEqual(code, 1)


DUAL = ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><style>:root{color-scheme:light dark}body{margin:0;background:#fafafa;color:#18181b;font:16px sans-serif}"
        ".chip{display:inline-block;padding:2px 8px;background:#eff6ff;color:#2563eb}"
        "@media (prefers-color-scheme: dark){body{background:#09090b;color:#e4e4e7}.chip{background:#172554;color:#60a5fa}%s}"
        "%s</style><body><span class='chip'>链接</span><div class='bar' style='height:12px;width:300px'></div></body></html>")


def audit_html(html: str, *extra: str, theme: str = "b2b-graphite") -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "audit_palette.py"), str(page), "--theme", theme, *extra], capture_output=True, text=True, encoding="utf-8")
        return run.returncode, run.stdout


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class DarkSchemeTest(unittest.TestCase):
    def test_a_page_with_both_themes_keeps_the_budget_in_both(self) -> None:
        for scheme in ("light", "dark"):
            code, out = audit_html(DUAL % ("", ""), "--scheme", scheme)
            self.assertEqual((code, out.strip()), (0, "audit palette: ok"), (scheme, out))
        self.assertEqual(audit_html(DUAL % ("", ""))[1].strip(), "audit palette: ok", "light is the default")

    def test_a_decorative_hue_that_only_the_dark_theme_adds_is_found_in_the_dark_scheme(self) -> None:
        page = DUAL % (".bar{background:#8b5cf6}", "")
        self.assertEqual(audit_html(page, "--scheme", "light")[1].strip(), "audit palette: ok")
        code, out = audit_html(page, "--scheme", "dark")
        self.assertEqual(code, 1)
        self.assertIn("not a hue of theme b2b-graphite", out)

    def test_colours_written_in_oklch_and_color_mix_are_read(self) -> None:
        page = DUAL % ("", ".bar{background:oklch(0.55 0.2 305)}")
        for scheme in ("light", "dark"):
            code, out = audit_html(page, "--scheme", scheme)
            self.assertEqual(code, 1, out)
            self.assertIn("not a hue of theme", out)
        mixed = DUAL % ("", ".bar{background:color-mix(in oklch, red 50%, blue)}")
        self.assertEqual(audit_html(mixed)[0], 1)

    def test_a_tinted_near_black_ground_is_a_hue_in_the_dark_scheme(self) -> None:
        page = DUAL % (".bar{background:#0e0a12}", "")
        self.assertEqual(audit_html(page, "--scheme", "dark")[0], 1, "violet-tinted ground is not a hue of graphite")
        own = DUAL % (".bar{background:#0d1017}", "")
        self.assertEqual(audit_html(own, "--scheme", "dark")[1].strip(), "audit palette: ok", "a blue-tinted ground is graphite's own blue")

    def test_a_page_that_switches_by_attribute_or_class(self) -> None:
        css = ":root[data-theme='dark'] .bar{background:#8b5cf6}html.dark .bar{background:#8b5cf6}"
        page = DUAL % ("", css)
        self.assertEqual(audit_html(page, "--scheme", "dark")[1].strip(), "audit palette: ok", "nothing switches it on")
        for flag, value in (("--dark-attr", "data-theme=dark"), ("--dark-class", "dark")):
            code, out = audit_html(page, "--scheme", "dark", flag, value)
            self.assertEqual(code, 1, (flag, out))
            self.assertIn("not a hue of theme", out)
        self.assertEqual(audit_html(page, "--scheme", "light", "--dark-attr", "data-theme=dark")[1].strip(), "audit palette: ok", "the switch is for --scheme dark only")


if __name__ == "__main__":
    unittest.main()
