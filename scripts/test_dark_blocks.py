"""check_document.py and the dark theme (visual-design.html 深色与浅色两套主题): a product front-end carries a light and a dark theme, so the dark fills and
color-scheme: dark inside a dark block are the theme, not a violation; the same fills in the default theme still are; a reading page stays light; a product
page with no dark block gets a warning."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_document as cd  # noqa: E402
from new_session import tab_icon_href  # noqa: E402

ICON = f'<link rel="icon" href="{tab_icon_href("门店后台")}">'
PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>门店后台</title>{icon}<style>body{{font-size:14px;color:#2B2326;background:#fff}} {css}</style></head>
<body><main><h1>门店后台</h1><section><h2>概况</h2><div class="card"><p class="muted">今日营收</p></div></section></main></body></html>"""

DARK_FILL = ".card{background:#272020;padding:16px;height:80px;color:#F5EFEA}"
SELECTORS = ('@media (prefers-color-scheme: dark){{ .card{{background:#272020;padding:16px;height:80px}} }}',
             ':root[data-theme="dark"] .card{{background:#272020;padding:16px;height:80px}}',
             ':root[data-theme=dark] .card{{background:#272020;padding:16px;height:80px}}',
             'html.dark .card{{background:#272020;padding:16px;height:80px}}',
             ':root.dark .card{{background:#272020;padding:16px;height:80px}}',
             '.dark .card{{background:#272020;padding:16px;height:80px}}',
             '[data-scheme="dark"] .card{{background:#272020;padding:16px;height:80px}}',
             '[data-scheme=dark] .card{{background:#272020;padding:16px;height:80px}}',
             'html[data-theme="dark"] .card, :root[data-theme="dark"] .card{{background:#272020;padding:16px;height:80px}}',
             '@media (prefers-color-scheme: dark) and (min-width: 700px){{ .card{{background:#272020;padding:16px;height:80px}} }}')


def run(css: str, allow: tuple[str, ...] = ("interface",)) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "page.html"
        path.write_text(PAGE.format(icon=ICON, css=css), encoding="utf-8")
        cd.ALLOWED.clear()
        cd.ALLOWED.update(allow)
        errors: list[str] = []
        warnings: list[str] = []
        try:
            cd.check_html(path, errors, warnings)
        finally:
            cd.ALLOWED.clear()
    return errors, warnings


def having(items: list[str], word: str) -> list[str]:
    return [i for i in items if word in i]


FILL = "dark or saturated fill"
SCHEME = "color scheme"
NO_BLOCK = "no dark theme block"


class DarkBlockTest(unittest.TestCase):
    def test_dark_fills_inside_a_dark_block_pass_whatever_the_writing(self) -> None:
        for template in SELECTORS:
            for allow in (("interface",), ("interface", "website")):   # --allow website implies interface (main adds it)
                with self.subTest(css=template, allow=allow):
                    errors, warnings = run(template.format(), allow)
                    self.assertFalse(having(errors, FILL), errors)
                    self.assertFalse(having(warnings, NO_BLOCK), warnings)

    def test_the_same_fill_in_the_default_theme_still_fails(self) -> None:
        for css in (DARK_FILL,
                    DARK_FILL + "@media (prefers-color-scheme: dark){ .card{background:#272020} }",
                    ':root:not([data-theme="dark"]) .card{background:#272020;padding:16px;height:80px}',
                    ".card.dark{background:#272020;padding:16px;height:80px}",
                    '@media (prefers-color-scheme: light){ .card{background:#272020;padding:16px;height:80px} }',
                    '@media not (prefers-color-scheme: dark){ .card{background:#272020;padding:16px;height:80px} }'):
            with self.subTest(css=css):
                self.assertTrue(having(run(css)[0], FILL))

    def test_dark_fill_next_to_a_dark_block_is_judged_per_rule(self) -> None:
        css = ".card{background:#272020;padding:16px;height:80px}@media (prefers-color-scheme: dark){ .card{background:#272020;padding:16px;height:80px} }"
        self.assertEqual(len(having(run(css)[0], FILL)), 1, "only the default theme's rule")

    def test_a_dark_ancestor_class_means_the_first_compound_only(self) -> None:
        self.assertTrue(cd.dark_selector("html.dark .card"))
        self.assertTrue(cd.dark_selector(".dark .card, :root.dark a"))
        self.assertTrue(cd.dark_selector('[data-scheme="dark"]'))
        self.assertFalse(cd.dark_selector(".card.dark"))
        self.assertFalse(cd.dark_selector(".dark-card"))
        self.assertFalse(cd.dark_selector(":root, :root[data-theme=dark]"), "a group with a default selector is a default rule")
        self.assertFalse(cd.dark_selector(':root:not([data-theme="dark"])'))
        self.assertEqual(cd.dark_media_spans("@media (prefers-color-scheme: light){a{b:c}}"), [])
        self.assertEqual(len(cd.dark_media_spans("@media (prefers-color-scheme: dark){a{b:c}} @media print{x{y:z}}")), 1)


class ColorSchemeTest(unittest.TestCase):
    def test_color_scheme_dark_inside_a_dark_block_is_the_theme(self) -> None:
        for css in ("@media (prefers-color-scheme: dark){ :root{color-scheme:dark} }",
                    ':root[data-theme="dark"]{color-scheme:dark}',
                    "html.dark{color-scheme: dark}",
                    ':root{color-scheme:light dark}@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){color-scheme:dark} }'):
            with self.subTest(css=css):
                self.assertFalse(having(run(css)[0], SCHEME))

    def test_color_scheme_dark_in_the_default_theme_fails(self) -> None:
        for css in (":root{color-scheme:dark}", "html{color-scheme: dark}", "body{color-scheme:dark;color:#2B2326}"):
            with self.subTest(css=css):
                errors, _ = run(css)
                self.assertTrue(having(errors, "declared in the default (light) theme"), errors)

    def test_light_and_follow_system_declarations_are_fine(self) -> None:
        for css in (":root{color-scheme:light}", ":root{color-scheme:light dark}", ":root{color-scheme:only light}"):
            with self.subTest(css=css):
                self.assertFalse(having(run(css)[0], SCHEME))

    def test_allow_dark_keeps_its_old_meaning(self) -> None:
        errors, warnings = run(":root{color-scheme:dark}" + DARK_FILL, ("interface", "dark"))
        self.assertFalse(having(errors, SCHEME))
        self.assertFalse(having(errors, FILL))
        self.assertFalse(having(warnings, NO_BLOCK), "a page the user asked to be dark is not asked for a second theme")


class ReadingPageTest(unittest.TestCase):
    def test_a_reading_page_stays_light(self) -> None:
        for css in ("@media (prefers-color-scheme: dark){ :root{color-scheme:dark} }", ":root{color-scheme:dark}",
                    "@media (prefers-color-scheme: dark){ body{background:#111} }"):
            with self.subTest(css=css):
                self.assertTrue(having(run(css, ())[0], "dark color scheme declared"))

    def test_dark_fill_behind_a_dark_selector_still_fails_on_a_reading_page(self) -> None:
        errors, warnings = run(':root[data-theme="dark"] .card{background:#272020;padding:16px;height:80px}', ())
        self.assertTrue(having(errors, FILL))
        self.assertFalse(having(warnings, NO_BLOCK), "reading pages are not asked for a dark theme")

    def test_allow_dark_on_a_reading_page_is_unchanged(self) -> None:
        errors, _ = run("@media (prefers-color-scheme: dark){ :root{color-scheme:dark} }", ("dark",))
        self.assertFalse(having(errors, "dark color scheme declared"))


class MissingDarkBlockTest(unittest.TestCase):
    def test_a_product_page_without_a_dark_block_gets_a_warning_not_an_error(self) -> None:
        for allow in (("interface",), ("interface", "website")):
            with self.subTest(allow=allow):
                errors, warnings = run(".card{background:#fff;padding:16px}", allow)
                self.assertTrue(having(warnings, NO_BLOCK), warnings)
                self.assertFalse(having(errors, NO_BLOCK))
                text = having(warnings, NO_BLOCK)[0]
                self.assertIn("audit_rendered.py --scheme dark", text)
                self.assertIn("深色与浅色两套主题", text)

    def test_any_dark_block_silences_it(self) -> None:
        for css in ("@media (prefers-color-scheme: dark){ :root{--bg:#121212} }", ':root[data-theme="dark"]{--bg:#121212}', "html.dark{--bg:#121212}"):
            with self.subTest(css=css):
                self.assertFalse(having(run(css)[1], NO_BLOCK))

    def test_reading_pages_are_not_asked(self) -> None:
        self.assertFalse(having(run(".card{padding:16px}", ())[1], NO_BLOCK))


class DarkValuesTest(unittest.TestCase):
    """The dark theme's tokens are read with the dark values, and its text is judged on a dark ground."""

    TOKENS = ":root{--surface:#FFFFFF;--ink3:#6F6266}@media (prefers-color-scheme: dark){ :root{--surface:#272020;--ink3:#ADA5A3} }"

    def test_light_rules_do_not_see_the_dark_tokens(self) -> None:
        errors, _ = run(self.TOKENS + ".card{background:var(--surface);color:var(--ink3);padding:16px;height:80px}")
        self.assertFalse(having(errors, FILL), errors)
        self.assertFalse(having(errors, "too light"), errors)

    def test_dark_rules_see_the_dark_tokens(self) -> None:
        css = self.TOKENS + "@media (prefers-color-scheme: dark){ .card{background:var(--surface);color:var(--ink3);padding:16px;height:80px} }"
        errors, _ = run(css)
        self.assertFalse(having(errors, FILL), errors)
        self.assertFalse(having(errors, "too light"), errors)

    def test_light_text_without_its_own_ground_is_judged_on_the_dark_ground(self) -> None:
        dark = "@media (prefers-color-scheme: dark){ .muted{color:#ADA5A3} }"
        self.assertFalse(having(run(dark)[0], "too light"))
        self.assertTrue(having(run(".muted{color:#ADA5A3}")[0], "too light"), "the same grey on the light page is too light")
        faint = "@media (prefers-color-scheme: dark){ .muted{color:#4A4242} }"
        self.assertTrue(having(run(faint)[0], "too light"), "a dark grey on the dark ground fails")

    def test_the_dark_ground_comes_from_the_dark_page_token(self) -> None:
        css = "@media (prefers-color-scheme: dark){ :root{--bg:#3A3434} .muted{color:#8C8484} }"
        self.assertTrue(having(run(css)[0], "too light"), "the page token is lighter than near-black, so the grey is judged on it")

    def test_dark_shadows_may_be_deeper(self) -> None:
        shadow = ".card{box-shadow:0 8px 16px rgba(0,0,0,.44),0 24px 48px rgba(0,0,0,.4)}"
        self.assertFalse(having(run("@media (prefers-color-scheme: dark){ " + shadow + " }")[1], "dark shadow"))
        self.assertTrue(having(run(shadow)[1], "dark shadow"))

    def test_a_light_control_fill_in_a_dark_block_is_not_washed_out(self) -> None:
        css = "@media (prefers-color-scheme: dark){ .btn-primary{background:#E4E4E7;color:#18181B} }"
        self.assertFalse(having(run(css)[0], "washed-out"))

    def test_a_linked_local_style_sheet_with_a_dark_block_counts_as_the_dark_theme(self) -> None:
        sheet = "@media (prefers-color-scheme: dark){ :root:not([data-theme=\"light\"]){ color-scheme: dark; --bg: #121212 } }"
        page = PAGE.replace("<style>", '<link rel="stylesheet" href="shared/ui.css"><style>')
        for body, expected in ((sheet, False), (".card{background:#fff}", True)):
            with tempfile.TemporaryDirectory() as tmp:
                (Path(tmp) / "shared").mkdir()
                (Path(tmp) / "shared" / "ui.css").write_text(body, encoding="utf-8")
                path = Path(tmp) / "page.html"
                path.write_text(page.format(icon=ICON, css=""), encoding="utf-8")
                cd.ALLOWED.clear()
                cd.ALLOWED.update(("interface",))
                errors: list[str] = []
                warnings: list[str] = []
                try:
                    cd.check_html(path, errors, warnings)
                finally:
                    cd.ALLOWED.clear()
                self.assertEqual(bool(having(warnings, "no dark theme block")), expected, (body, warnings))


if __name__ == "__main__":
    unittest.main()
