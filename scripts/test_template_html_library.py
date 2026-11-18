"""The HTML template library: tokens follow the palette, numbers are well-formed and retrievable, built pages match their sources, the package validates."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_template_tokens as tokens  # noqa: E402
import template_registry as registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def luminance(hex_value: str) -> float:
    r, g, b = (int(hex_value.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def item(**kw) -> dict:
    return {"kind": "app", "id": "AP-HOME-001", "name": "测试", "cat": "", "page": "home", "file": "templates/app/home.html", "start": 0, "stop": 0, **kw}


def show(cid: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(Path(registry.__file__)), "show", cid], capture_output=True, text=True, encoding="utf-8")


def mix(a: str, b: str, share: float) -> str:
    """color-mix(in srgb, a share%, b)."""
    pa = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    pb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x * share + y * (1 - share)):02X}" for x, y in zip(pa, pb))


class TokensTest(unittest.TestCase):
    def test_tokens_file_is_generated_from_the_palette(self) -> None:
        self.assertEqual(tokens.OUT.read_text(encoding="utf-8"), tokens.render())

    def test_there_are_many_presets_and_each_reads_with_white_text(self) -> None:
        presets = tokens.presets()
        self.assertGreaterEqual(len(presets), 24)
        self.assertEqual(len({p["id"] for p in presets}), len(presets))
        for p in presets:
            with self.subTest(theme=p["id"]):
                self.assertRegex(p["action"], r"^#[0-9A-F]{6}$")
                self.assertGreaterEqual(contrast(p["action"], "#FFFFFF"), 4.5, "white text on the action colour")
                self.assertGreaterEqual(contrast(p["accent"], "#FFFFFF"), 4.5, "the accent reads as text too")

    def test_derived_text_and_surface_tokens_keep_their_contrast_in_every_theme(self) -> None:
        for p in tokens.presets():
            action = p["action"]
            bg, tint = mix(action, "#FAFAF9", 0.025), mix(action, "#FFFFFF", 0.07)
            ink, ink2, ink3 = mix(action, "#1D1F23", 0.06), mix(action, "#474A50", 0.07), mix(action, "#666A71", 0.07)
            with self.subTest(theme=p["id"]):
                self.assertGreaterEqual(contrast(ink, bg), 7.0, "ink on the page")
                self.assertGreaterEqual(contrast(ink2, bg), 7.0, "secondary ink on the page")
                self.assertGreaterEqual(contrast(ink3, bg), 4.5, "tertiary ink on the page")
                self.assertGreaterEqual(contrast(ink3, tint), 4.5, "tertiary ink on the tint")
                self.assertGreaterEqual(contrast(mix(action, "#000000", 0.74), tint), 4.5, "press colour on the tint")

    def test_everything_that_follows_the_brand_is_derived_in_css(self) -> None:
        css = tokens.render()
        for name in ("--action-press", "--action-tint", "--action-edge", "--bg", "--ink", "--line", "--elev-1"):
            self.assertRegex(css, rf"{name}: [^;]*color-mix\(", name)
        self.assertNotIn("rgba(74, 44, 56", css, "no colour of one fixed theme is written into the shared tokens")
        self.assertEqual(len(re.findall(r"--action: #", css)), len(tokens.presets()) + 1, "the default plus one block per preset")

    def test_font_scale_stays_above_the_floors(self) -> None:
        css = tokens.render()
        self.assertEqual(re.findall(r"--fs-xs: (\d+)px", css), ["12"])
        self.assertEqual(len(re.findall(r"font-family", css)), 0, "one font stack, declared once as --font")

    def test_the_mono_icon_filter_lives_in_the_tokens_so_posters_get_it_too(self) -> None:
        css = tokens.render()
        self.assertIn("--ic-fx", css)
        self.assertIn('img[src*="/icons/"]', css)


class RegistryTest(unittest.TestCase):
    def test_every_number_is_well_formed_unique_and_consecutive(self) -> None:
        items = registry.collect()
        self.assertGreater(len(items), 200)
        self.assertEqual(registry.problems(items), [])

    def test_both_ends_have_one_entry_file_and_their_sources(self) -> None:
        for end in ("app", "web"):
            self.assertTrue((ROOT / "templates" / end / f"{end}.html").is_file(), f"{end}.html")
            for page in ("home", "list", "orders", "mine", "agent"):
                self.assertTrue((ROOT / "templates" / end / "source" / "pages" / f"{page}.html").is_file(), f"{end}/{page}")
            self.assertTrue(list((ROOT / "templates" / end / "source" / "parts").glob("*.part")))
            self.assertEqual({p.name for p in (ROOT / "templates" / end).iterdir()}, {f"{end}.html", "source"}, "an end folder holds its single html and the sources")
        pages = {(it["kind"], it["page"]) for it in registry.collect()}
        for end in ("app", "web"):
            for page in ("components", "home", "list", "orders", "mine", "agent"):
                self.assertIn((end, page), pages)

    def test_the_component_library_covers_the_categories(self) -> None:
        cats = {end: {it["cat"] for it in registry.collect() if it["kind"] == end and it["page"] == "components"} for end in ("app", "web")}
        for code in ("BTN", "BGND", "CARD", "FORM", "DATA", "FEED", "CHAT", "MOTN"):
            self.assertIn(code, cats["app"])
            self.assertIn(code, cats["web"])
        self.assertTrue({"ENTR", "NAVI", "ROWS"} <= cats["app"])
        self.assertTrue({"LAYT", "TABL"} <= cats["web"])

    def test_posters_prompts_and_documents_are_numbered(self) -> None:
        pub = registry.public(registry.collect())
        self.assertGreaterEqual(len(pub["posters"]), 12)
        self.assertGreaterEqual(len(pub["prompts"]), 50)
        self.assertEqual({d["type"] for d in pub["documents"]}, {"word", "excel", "slides", "pdf", "reading"})
        self.assertTrue(any(d["part"] for d in pub["documents"]))

    def test_registry_files_are_current(self) -> None:
        items = registry.collect()
        self.assertEqual(registry.REGISTRY.read_text(encoding="utf-8"), registry.render_registry(items))
        self.assertEqual(registry.REGISTRY_JS.read_text(encoding="utf-8"), registry.render_registry_js(items))

    def test_show_prints_the_component_poster_prompt_and_document(self) -> None:
        run = show("AP-HOME-004")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('data-cid="AP-HOME-004"', run.stdout)
        self.assertIn("../../kit/", run.stdout)
        comp = show("AP-BTN-001")
        self.assertEqual(comp.returncode, 0, comp.stderr)
        self.assertNotIn("demo__head", comp.stdout, "a component demo hands over its stage, not the catalog card around it")
        for cid in ("PS-001", "PP-001", "DC-WD-001"):
            out = show(cid)
            self.assertEqual(out.returncode, 0, (cid, out.stderr))
            self.assertIn(cid, out.stdout)

    def test_unknown_number_is_reported(self) -> None:
        self.assertEqual(show("AP-HOME-999").returncode, 1)

    def test_problems_catch_bad_format_duplicates_and_wrong_domain(self) -> None:
        items = [item(id="AP-HOME-1"), item(id="AP-HOME-001"), item(id="AP-HOME-001"),
                 item(id="WB-HOME-002"), item(id="AP-LIST-001"), item(id="AP-HOME-003", name="x"),
                 item(id="AP-BTN-001", page="home")]
        text = "\n".join(registry.problems(items))
        self.assertIn("编号格式不对", text)
        self.assertIn("编号重复", text)
        self.assertIn("端前缀", text)
        self.assertIn("只能用域", text)
        self.assertIn("缺少中文", text)

    def test_the_component_library_rejects_page_domains_and_number_gaps(self) -> None:
        comp = dict(page="components", file="templates/app/components.html")
        text = "\n".join(registry.problems([item(id="AP-HOME-001", **comp), item(id="AP-BTN-001", **comp), item(id="AP-BTN-003", **comp)]))
        self.assertIn("只能用组件域", text)
        self.assertIn("编号不连续", text)

    def test_poster_prompt_and_document_numbers_are_checked(self) -> None:
        poster = {"kind": "poster", "id": "PS-002", "_stem_id": "PS-001", "name": "海报", "cat": "活动", "size": "1080×1440", "page": "x", "file": "f"}
        prompt = {"kind": "prompt", "id": "PP-1", "name": "提示词", "cat": "", "page": "prompts", "file": "f"}
        doc = {"kind": "document", "id": "DC-WD-P01", "name": "封面", "cat": "excel", "page": "excel", "file": "", "spec": "", "folder": "templates/documents/excel", "part": False}
        text = "\n".join(registry.problems([poster, prompt, doc]))
        self.assertIn("文件名编号", text)
        self.assertIn("提示词编号格式不对", text)
        self.assertIn("类型与目录", text)
        self.assertIn("模板与可复用块编号用错", text)

    def test_the_shared_navigation_may_repeat_across_pages_when_it_is_identical(self) -> None:
        base = item(id="AP-NAV-001", name="底部主导航", file="x")
        same = [{**base, "page": "home"}, {**base, "page": "list"}]
        self.assertEqual(registry.problems(same), [])
        other = [{**base, "page": "home"}, {**base, "page": "list", "name": "别的名称"}]
        self.assertTrue(registry.problems(other))
        self.assertEqual(len(registry.public(same)["components"]), 1)


class BuiltPagesTest(unittest.TestCase):
    """The single-file entries are built from their sources; a hand edit would be lost on the next build."""

    def test_app_and_web_entries_match_their_sources(self) -> None:
        import build_templates as bt
        for end in ("app", "web"):
            with self.subTest(end=end):
                self.assertEqual(bt.bundle_end(end), (ROOT / "templates" / end / f"{end}.html").read_text(encoding="utf-8"))

    def test_poster_entry_matches_its_sources(self) -> None:
        import build_templates as bt
        self.assertEqual(bt.bundle_poster(), (ROOT / "templates/poster/poster.html").read_text(encoding="utf-8"))

    def test_an_entry_holds_two_tabs_and_every_page_and_the_library(self) -> None:
        text = (ROOT / "templates/app/app.html").read_text(encoding="utf-8")
        for needle in ('data-tab="pages"', 'data-tab="components"', 'id="src-components"', 'id="src-page-home"', 'id="src-page-agent"', "swatches", "fxlist", "iconseg"):
            self.assertIn(needle, text, needle)
        self.assertNotIn("<\\/script><\\/script>", text, "stored pages escape their own script ends")

    def test_every_workbench_page_exists(self) -> None:
        import build_templates as bt
        for end, cfg in bt.ENDS.items():
            for pid, _name, _logic in cfg["pages"]:
                self.assertTrue((ROOT / "templates" / end / "source" / "pages" / f"{pid}.html").is_file(), pid)


class LayoutTest(unittest.TestCase):
    """templates/ holds exactly four folders; their catalog pages and generated files follow the sources."""

    def test_templates_holds_exactly_the_four_folders(self) -> None:
        self.assertEqual(sorted(p.name for p in (ROOT / "templates").iterdir()), ["app", "documents", "poster", "web"])

    def test_the_library_home_and_shared_kit_are_where_the_pages_expect_them(self) -> None:
        for path in ("index.html", "kit/tokens.css", "kit/ui.css", "kit/kit.css", "kit/ui.js", "kit/registry.js", "kit/assets/manifest.json", "references/template-registry.json"):
            self.assertTrue((ROOT / path).is_file(), path)
        for page in ("templates/app/app.html", "templates/web/web.html", "templates/poster/poster.html", "templates/documents/documents.html"):
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn("kit/tokens.css", text, page)
            self.assertNotIn("shared/", text, page)

    def test_every_page_link_into_kit_resolves(self) -> None:
        for page in list((ROOT / "templates").rglob("*.html")) + [ROOT / "index.html"]:
            if "samples" in page.parts or "reading" in page.parts:
                continue
            for target in re.findall(r'(?:href|src)="((?:\.\./)*kit/[^"#?]+)"', page.read_text(encoding="utf-8")):
                if "${" in target:  # built at run time by the page script
                    continue
                self.assertTrue((page.parent / target).resolve().is_file(), f"{page.relative_to(ROOT)} -> {target}")

    def test_the_poster_entry_lists_every_poster(self) -> None:
        text = (ROOT / "templates/poster/poster.html").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r'"id": "(PS-\d{3})"', text)), {p["id"] for p in registry.public(registry.collect())["posters"]})

    def test_generated_prompts_and_documents_files_are_current(self) -> None:
        for script, args in (("build_prompts_js.py", ["--check"]), ("build_documents_index.py", ["--check"])):
            run = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts" / script), *args], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(run.returncode, 0, script + run.stdout + run.stderr)


class AssetManifestTest(unittest.TestCase):
    def test_every_asset_is_listed_with_its_hash_and_nothing_is_unlisted(self) -> None:
        import hashlib
        folder = ROOT / "kit" / "assets"
        listed = {it["path"]: it["sha256"] for it in json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["assets"]}
        found = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and p.name != "manifest.json"}
        self.assertEqual(set(listed), found)
        for rel, sha in listed.items():
            self.assertEqual(hashlib.sha256((folder / rel).read_bytes()).hexdigest(), sha, rel)


class PackageTest(unittest.TestCase):
    def test_the_package_validates(self) -> None:
        import validate_skill
        self.assertEqual(validate_skill.main(["--package-only"]), 0)


if __name__ == "__main__":
    unittest.main()
