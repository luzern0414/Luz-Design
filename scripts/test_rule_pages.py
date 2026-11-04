"""Rule pages are Chinese prose: Latin letters are allowed only inside <code> and <kbd>."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_skill as vs  # noqa: E402

PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>视觉设计规范</title></head>
<body><main aria-label="视觉设计规范"><h1>视觉设计规范</h1><section>{body}</section></main></body></html>"""


def latin_errors(body: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        saved = vs.ROOT
        vs.ROOT = Path(tmp)
        try:
            path = Path(tmp) / "page.html"
            path.write_text(PAGE.format(body=body), encoding="utf-8")
            errors: list[str] = []
            vs.validate_rule_page(path, "visual", 0, "视觉设计规范", errors)
        finally:
            vs.ROOT = saved
    return [e for e in errors if "Latin" in e]


class RulePageLatinTest(unittest.TestCase):
    def test_code_and_kbd_may_hold_latin(self) -> None:
        body = '<p>运行 <code>py -X utf8 scripts/check_document.py</code>，按 <kbd>Ctrl</kbd> 加 <kbd>S</kbd> 保存。</p>'
        self.assertEqual(latin_errors(body), [])

    def test_attributes_inside_code_are_allowed(self) -> None:
        self.assertEqual(latin_errors('<p>令牌 <code title="brand-6">品牌色</code></p>'), [])

    def test_latin_in_prose_headings_and_strong_is_refused(self) -> None:
        for body in ("<p>主色用 brand 色</p>", "<h2>Colour</h2>", "<p><strong>WCAG</strong> 对比度</p>",
                     "<p>表格<span>OK</span></p>"):
            with self.subTest(body=body):
                self.assertTrue(latin_errors(body))

    def test_latin_in_accessible_text_outside_code_is_refused(self) -> None:
        self.assertTrue(latin_errors('<p><span aria-label="icon">图标</span></p>'))


class UiOwnershipTest(unittest.TestCase):
    """references/ui-ownership.md is the one statement of what Luz-System decides and what Luz-Design decides."""

    ROOT = Path(__file__).resolve().parents[1]

    def test_the_page_exists_is_registered_and_linked_from_skill_md(self) -> None:
        self.assertTrue((self.ROOT / "references" / "ui-ownership.md").is_file())
        self.assertIn("references/ui-ownership.md", vs.REQUIRED)
        skill = (self.ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("](references/ui-ownership.md)", skill)

    def test_the_sections_other_skills_point_to_exist_in_the_visual_rules(self) -> None:
        page = (self.ROOT / "references" / "visual-design.html").read_text(encoding="utf-8")
        for name in ("界面组件的外观", "同类元素外观一致", "界面配图与丰富度", "前端排布的推导", "各端视觉参数"):
            with self.subTest(section=name):
                self.assertEqual(page.count(f"<h4>{name}</h4>"), 1)
        for name in ("列表变更的动效", "卡片与切换控件的动效"):
            with self.subTest(section=name):
                self.assertEqual(page.count(f"<h5>{name}</h5>"), 1)

    def test_every_interface_card_states_the_line_design_does_not_cross(self) -> None:
        import json
        cards = json.loads((self.ROOT / "references" / "cards.json").read_text(encoding="utf-8"))["cards"]
        for kind in ("interface-visual", "interface-components", "interface-layout", "interface-pattern",
                     "interface-motion", "interface-icons", "interface-recipes", "design-direction", "design-path", "page-patterns",
                     "prototype-reference"):
            with self.subTest(card=kind):
                lines = cards[kind]["tools"] + cards[kind]["checks"]
                self.assertTrue(any("ui-ownership.md" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
