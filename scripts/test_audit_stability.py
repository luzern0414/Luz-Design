"""audit_stability.py: a page that jumps, flashes or gains a scroll bar after its first frame is reported; a stable page passes."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_stability as st  # noqa: E402

HERE = Path(__file__).resolve().parent


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


def audit(html: str, *args: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "audit_stability.py"), str(page), "--settle", "1500", *args], capture_output=True, text=True, encoding="utf-8")
        return run.returncode, run.stdout


HEAD = "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><meta name='viewport' content='width=device-width, initial-scale=1'>"
STABLE = HEAD + "<style>body{margin:0;font:16px sans-serif;background:#fafafa;color:#18181b}main{padding:24px}.card{height:120px;background:#fff;margin-bottom:16px}</style><main><h1>标题</h1><div class='card'>内容</div></main>"


class PureFunctionsTest(unittest.TestCase):
    def test_summary_sums_the_shifts_and_names_the_biggest_movers(self) -> None:
        total, top = st.summarise([{"t": 100, "value": 0.04, "src": ["div.card"]}, {"t": 900, "value": 0.03, "src": ["h1."]}], since=0)
        self.assertAlmostEqual(total, 0.07)
        self.assertTrue(top[0].startswith("div.card"))
        total, _ = st.summarise([{"t": 100, "value": 0.04, "src": ["a"]}], since=500)
        self.assertEqual(total, 0)

    def test_a_jump_of_the_ground_is_a_flash_and_a_small_change_is_not(self) -> None:
        frames = [{"t": 16, "ground": 0.9, "width": 1440}, {"t": 33, "ground": 0.02, "width": 1440}]
        self.assertIn("flash", st.ground_flash(frames))
        self.assertIsNone(st.ground_flash([{"t": 16, "ground": 0.9, "width": 1440}, {"t": 33, "ground": 0.8, "width": 1440}]))
        self.assertIsNone(st.ground_flash([{"t": 16, "ground": None, "width": 1440}, {"t": 33, "ground": 0.9, "width": 1440}]))

    def test_a_changed_width_is_a_scroll_bar_jump(self) -> None:
        self.assertIn("scroll bar", st.width_jump([{"t": 16, "ground": 0.9, "width": 1440}, {"t": 33, "ground": 0.9, "width": 1425}]))
        self.assertIsNone(st.width_jump([{"t": 16, "ground": 0.9, "width": 1440}, {"t": 33, "ground": 0.9, "width": 1440}]))


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class RenderedTest(unittest.TestCase):
    def test_a_stable_page_passes_in_both_schemes(self) -> None:
        for scheme in ("light", "dark"):
            code, out = audit(STABLE, "--scheme", scheme)
            self.assertEqual((code, out.strip()), (0, "audit stability: ok"), (scheme, out))

    def test_a_banner_that_pushes_the_content_down_is_a_layout_shift(self) -> None:
        page = STABLE.replace("</main>", "</main><script>setTimeout(()=>{const b=document.createElement('div');b.style.cssText='height:360px;background:#e4f3ec';b.textContent='提示';document.querySelector('main').prepend(b)},600)</script>")
        code, out = audit(page)
        self.assertEqual(code, 1, out)
        self.assertIn("layout shift", out)

    def test_a_light_ground_before_the_dark_scheme_is_a_flash(self) -> None:
        page = HEAD + ("<style>body{margin:0;background:#fff;color:#111;font:16px sans-serif}body.dark{background:#0b0b0e;color:#eee}</style><main>内容</main>"
                       "<script>setTimeout(()=>document.body.classList.add('dark'),400)</script>")
        code, out = audit(page, "--scheme", "dark")
        self.assertEqual(code, 1, out)
        self.assertIn("flash", out)

    def test_a_scroll_bar_that_appears_after_the_first_frame_is_a_jump(self) -> None:
        page = STABLE.replace("</main>", "</main><script>setTimeout(()=>{const t=document.createElement('div');t.style.cssText='height:2400px';document.querySelector('main').append(t)},500)</script>")
        code, out = audit(page)
        self.assertEqual(code, 1, out)
        self.assertTrue("scroll bar" in out or "layout shift" in out, out)

    def test_scrollbar_gutter_stable_keeps_the_width(self) -> None:
        page = STABLE.replace("body{margin:0", "html{overflow-y:scroll}body{margin:0").replace("</main>", "</main><script>setTimeout(()=>{const t=document.createElement('div');t.style.cssText='height:2400px';document.querySelector('main').append(t)},500)</script>")
        code, out = audit(page)
        self.assertNotIn("scroll bar", out, out)


if __name__ == "__main__":
    unittest.main()
