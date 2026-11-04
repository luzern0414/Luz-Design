"""The Markdown type block of reading pages (references/md-type.css): the sizes in the master match the rule pages, every sibling copy is the
same text, a page that carries the block passes check_document.py as a reading page, and in a real browser the block gives
18 / 16 px body text on desktop / phone with the headings in the specified steps."""
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_document as cd  # noqa: E402
import sync_md_type  # noqa: E402

from new_session import tab_icon_href  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "references" / "md-type.css"
FILE_DESIGN = (ROOT / "references" / "file-design.html").read_text(encoding="utf-8")
VISUAL_DESIGN = (ROOT / "references" / "visual-design.html").read_text(encoding="utf-8")
PHONE = {"body": 16, "h1": 28, "h2": 24, "h3": 20, "h4": 16, "table": 14, "code": 14, "aux": 14}
DESKTOP = {"body": 18, "h1": 36, "h2": 28, "h3": 22, "h4": 18, "table": 16, "code": 16, "aux": 14}
ICON = f'<link rel="icon" href="{tab_icon_href("规则页")}">'
PAGE = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>规则页</title>' + ICON + '<style>*{box-sizing:border-box}:root{--ink:#172033;--muted:#526071;--line:#d7e0e8;--surface:#f7f9fc;--surface-soft:#edf3f7}'
        'body{margin:0;color:var(--ink);background:#fff;font-family:"PingFang SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif}'
        'main{width:min(1040px,100%);margin:0 auto;padding:32px 16px}\n' + MASTER.read_text(encoding="utf-8") + '</style></head><body><main>'
        '<h1>规则页</h1><h2>第一节</h2><p>正文一段，说明本节的内容。</p><h3>三级标题</h3><h4>四级标题</h4><ul><li>列表项</li></ul>'
        '<table><caption>表 1 示例</caption><thead><tr><th>名称</th><th>数值</th></tr></thead><tbody><tr><td>甲</td><td>12</td></tr></tbody></table>'
        '<p><code>code</code></p><figure><img alt="图" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="><figcaption>图 1 示例</figcaption></figure>'
        '</main></body></html>')


def master_tokens() -> dict[str, dict[str, int]]:
    text = MASTER.read_text(encoding="utf-8")
    base = re.search(r":root\s*\{([^}]*)\}", text).group(1)
    desktop = re.search(r"@media \(min-width: 768px\)\s*\{\s*:root\s*\{([^}]*)\}", text).group(1)

    def sizes(block: str) -> dict[str, int]:
        return {k: int(v) for k, v in re.findall(r"--md-([a-z0-9]+):\s*(\d+)px", block)}

    phone = sizes(base)
    return {"phone": phone, "desktop": {**phone, **sizes(desktop)}}


class MasterTest(unittest.TestCase):
    def test_master_sizes_are_the_two_sets_of_the_rule_pages(self) -> None:
        tokens = master_tokens()
        for name, expected in (("phone", PHONE), ("desktop", DESKTOP)):
            for key, px in expected.items():
                self.assertEqual(tokens[name][key], px, f"{name} --md-{key}")

    def test_the_rule_pages_state_the_same_numbers(self) -> None:
        for px in (36, 28, 22, 18, 16, 14):
            self.assertIn(f"{px} 像素", FILE_DESIGN)
        self.assertIn("桌面（768 及以上）：14 · 16 · 18 · 22 · 28 · 36", VISUAL_DESIGN)
        self.assertIn("手机（小于 768）：14 · 16 · 20 · 24 · 28", VISUAL_DESIGN)

    def test_print_sizes_stay_at_or_above_the_14_pixel_floor(self) -> None:
        printed = re.search(r"@media print\s*\{\s*:root\s*\{([^}]*)\}", MASTER.read_text(encoding="utf-8")).group(1)
        for name, value in re.findall(r"--md-([a-z0-9]+):\s*([\d.]+)pt", printed):
            if name.startswith(("body", "table", "aux", "code", "h")):
                self.assertGreaterEqual(float(value) * 4 / 3, 14 - 1e-6, name)

    def test_weights_and_style_follow_the_three_weight_rule(self) -> None:
        text = MASTER.read_text(encoding="utf-8")
        weights = set(re.findall(r"font-weight:\s*(\d+)", text))
        self.assertLessEqual(weights, {"400", "600", "700"})
        self.assertNotIn("italic", text)


class SyncTest(unittest.TestCase):
    def test_the_copies_in_this_skill_and_every_present_sibling_are_the_master(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = sync_md_type.main(["--check"])
        lines = buffer.getvalue().splitlines()
        self.assertFalse([line for line in lines if line.startswith(("DIFF", "MISSING"))], "\n".join(lines))
        self.assertEqual(code, 0)


class PageCheckTest(unittest.TestCase):
    def test_a_reading_page_with_the_block_passes_check_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            path.write_text(PAGE, encoding="utf-8")
            cd.ALLOWED.clear()
            errors: list[str] = []
            warnings: list[str] = []
            try:
                cd.check_html(path, errors, warnings)
            finally:
                cd.ALLOWED.clear()
        self.assertEqual(errors, [])


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class RenderedTest(unittest.TestCase):
    PROBE = """() => { const px = (s) => parseFloat(getComputedStyle(document.querySelector(s)).fontSize);
      return { body: px('body'), h1: px('h1'), h2: px('h2'), h3: px('h3'), h4: px('h4'), table: px('td'), code: px('code'), aux: px('figcaption'),
               wide: document.documentElement.scrollWidth > innerWidth + 1 } }"""

    def measure(self, width: int) -> dict:
        from playwright.sync_api import sync_playwright

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.html"
            path.write_text(PAGE, encoding="utf-8")
            with sync_playwright() as pw:
                browser = pw.chromium.launch(channel="msedge")
                page = browser.new_page(viewport={"width": width, "height": 900})
                page.goto(path.as_uri())
                result = page.evaluate(self.PROBE)
                browser.close()
        return result

    def test_desktop_and_phone_get_their_own_sizes(self) -> None:
        for width, expected in ((1440, DESKTOP), (390, PHONE)):
            got = self.measure(width)
            self.assertFalse(got.pop("wide"), f"horizontal scroll at {width}")
            self.assertEqual({k: int(v) for k, v in got.items()}, expected, f"{width} px wide")


if __name__ == "__main__":
    unittest.main()
