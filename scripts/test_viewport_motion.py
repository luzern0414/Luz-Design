"""check_document.py: viewport zoom and safe areas, reduced motion, faded disabled text (visual-design.html 视口、安全区与自适应写法, 动效细则)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_document as cd  # noqa: E402

from new_session import tab_icon_href  # noqa: E402

ICON = f'<link rel="icon" href="{tab_icon_href("会议助手")}">'
PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">{viewport}
<title>原型</title>{icon}<style>body{{font-size:14px;color:#2B2326}} {css}</style></head><body><h1>会议助手原型</h1><h2>首页</h2><p>本周会议</p></body></html>"""


def run(viewport: str = '<meta name="viewport" content="width=device-width, initial-scale=1">', css: str = "",
        allow: tuple[str, ...] = ("interface",)) -> tuple[list[str], list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "page.html"
        path.write_text(PAGE.format(viewport=viewport, icon=ICON, css=css), encoding="utf-8")
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


def viewport(content: str) -> str:
    return f'<meta name="viewport" content="{content}">'


class ViewportTest(unittest.TestCase):
    def test_the_standard_viewport_is_clean(self) -> None:
        errors, warnings = run()
        self.assertEqual(having(errors, "viewport"), [])
        self.assertEqual(having(warnings, "viewport"), [])

    def test_disabling_zoom_is_an_error(self) -> None:
        for content in ("width=device-width, user-scalable=no", "width=device-width, user-scalable=0",
                        "width=device-width, maximum-scale=1", "width=device-width,maximum-scale=1.5"):
            with self.subTest(content=content):
                errors, _ = run(viewport(content))
                self.assertTrue(having(errors, "viewport"), content)

    def test_limited_zoom_between_two_and_five_warns(self) -> None:
        errors, warnings = run(viewport("width=device-width, maximum-scale=3"))
        self.assertEqual(having(errors, "viewport"), [])
        self.assertTrue(having(warnings, "5x zoom"))
        errors, warnings = run(viewport("width=device-width, maximum-scale=5"))
        self.assertEqual(having(warnings, "viewport"), [])

    def test_edge_to_edge_pages_need_the_safe_area_insets(self) -> None:
        _, warnings = run(viewport("width=device-width, initial-scale=1, viewport-fit=cover"))
        self.assertTrue(having(warnings, "safe-area-inset"))
        _, warnings = run(viewport("width=device-width, initial-scale=1, viewport-fit=cover"),
                          css=".bar{position:fixed;bottom:0;padding-bottom:calc(8px + env(safe-area-inset-bottom, 0px))}")
        self.assertEqual(having(warnings, "safe-area-inset"), [])

    def test_applies_to_reading_pages_too(self) -> None:
        errors, _ = run(viewport("width=device-width, user-scalable=no"), allow=())
        self.assertTrue(having(errors, "user-scalable"))


class MotionTest(unittest.TestCase):
    def test_transitions_need_a_reduced_motion_branch_in_interfaces(self) -> None:
        _, warnings = run(css=".card{transition:box-shadow 150ms}")
        self.assertTrue(having(warnings, "prefers-reduced-motion"))
        _, warnings = run(css=".card{transition:box-shadow 150ms}@media (prefers-reduced-motion: reduce){.card{transition:none}}")
        self.assertEqual(having(warnings, "prefers-reduced-motion"), [])

    def test_smooth_scrolling_counts_as_motion(self) -> None:
        _, warnings = run(css="html{scroll-behavior:smooth}")
        self.assertTrue(having(warnings, "prefers-reduced-motion"))

    def test_no_motion_no_warning(self) -> None:
        _, warnings = run(css=".card{transition:none}.x{animation:none}")
        self.assertEqual(having(warnings, "prefers-reduced-motion"), [])

    def test_transition_all_warns(self) -> None:
        _, warnings = run(css=".card{transition:all 150ms}@media (prefers-reduced-motion: reduce){.card{transition:none}}")
        self.assertTrue(having(warnings, "transition: all"))

    def test_reading_pages_are_not_asked(self) -> None:
        _, warnings = run(css=".card{transition:box-shadow 150ms}", allow=())
        self.assertEqual(having(warnings, "prefers-reduced-motion"), [])


class DisabledTextTest(unittest.TestCase):
    def test_faded_text_on_a_disabled_control_is_measured(self) -> None:
        errors, _ = run(css="button:disabled{color:rgba(43,35,38,.38)}")
        self.assertTrue(having(errors, "color too light"))

    def test_grey_text_at_three_to_one_passes(self) -> None:
        errors, _ = run(css="button:disabled{color:#8A8A8A}")
        self.assertEqual(having(errors, "color too light"), [])

    def test_light_grey_text_fails(self) -> None:
        errors, _ = run(css="button:disabled{color:#B8B8B8}")
        self.assertTrue(having(errors, "color too light"))


if __name__ == "__main__":
    unittest.main()
