"""The component template library: static completeness, the committed index, the build, and (with a browser) the built page.

    py -X utf8 scripts/test_component_library.py

Static tests need nothing but Python. Browser tests need playwright and Microsoft Edge and are skipped without them: they open the full build, count the
components, sweep every category at 1500 and 390 px, cycle the 8 theme colours and 4 icon styles, check the CSS of every block at run time, click through every
component by the kind of control it carries, and judge the dark appearance: the text and icon contrast of all 303 components (desktop and phone, the 8 themes,
the system-follow and the class trigger), the white panels, and the contract of the appearance switch (about two minutes in all).

The light theme is guarded by tools/visual_regression.py: ``LIB_REGRESSION_BASE=<capture dir of the light baseline>`` makes ``LightRegressionTests`` capture the
current build and compare it, component by component, with that baseline (the pictures are not in the repository; the thresholds are).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_component_library as builder  # noqa: E402
import check_component_library as check  # noqa: E402

LIB = check.LIB
sys.path.insert(0, str(LIB / "tools"))
EXPECTED_TOTAL, EXPECTED_MP, EXPECTED_AD = 303, 160, 143

# Dark contrast: the components that still fall under 4.5:1 (text) or 3:1 (large text, icons, placeholders) in the dark appearance, and why. Nothing else may.
# The test fails on a component that is not listed and on a listed one that no longer fails (delete the line).
DARK_CONTRAST_EXCEPTIONS = {
    "AD-STATE-002": "403 is a 100 px ghost numeral drawn in the theme's pale tint (--pm) on purpose: 1.4:1 in the light appearance as well; the page says the same in words",
}


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(channel="msedge").close()
        return True
    except Exception:
        return False


# ------------------------------------------------------------------------------------------------------------------------------------------------
# Static
# ------------------------------------------------------------------------------------------------------------------------------------------------


class CompleteLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = check.read_library()
        cls.report = check.check(cls.lib)

    def test_the_library_passes_its_own_check(self):
        self.assertEqual(self.report.errors, [])

    def test_the_counts_are_the_published_ones(self):
        s = self.report.stats
        self.assertEqual((s["total"], s["MP"], s["AD"]), (EXPECTED_TOTAL, EXPECTED_MP, EXPECTED_AD))
        self.assertEqual(s["legacy templates"], 52)
        self.assertEqual(len([k for k, v in s["by category"].items() if v]), 29)
        self.assertEqual(sum(s["by category"].values()), EXPECTED_TOTAL)

    def test_every_taxonomy_category_has_components_and_a_guide(self):
        have = {(c.dom, c.cat) for c in self.lib.comps}
        guides = {(g.dom, g.cat) for g in self.lib.guides}
        for dom, rows in self.lib.cats.items():
            for code, _ in rows:
                self.assertIn((dom, code), have, f"{dom}-{code} has no component")
                self.assertIn((dom, code), guides, f"{dom}-{code} has no guide")

    def test_there_are_no_silent_gaps(self):
        self.assertEqual(check.KNOWN_GAPS, {})

    def test_the_index_is_the_committed_one_byte_for_byte(self):
        self.assertEqual(builder.INDEX.read_bytes().decode("utf-8"), builder.render_index())
        text = builder.INDEX.read_text(encoding="utf-8")
        for comp in self.lib.comps:
            self.assertIn(f"| {comp.id} |", text)
        self.assertLess(len(text.encode("utf-8")), 150_000)

    def test_the_source_carries_no_private_strings(self):
        pattern = re.compile(r"skill输出|[A-Z]:\\Users|@gmail|@qq\.com|@163\.com|(?<![0-9])1[3-9][0-9]{9}(?![0-9])")
        # sample data: 13800138000 and the made-up numbers of the form 1xx000xxxxx
        sample = re.compile(r"1[3-9]\d000\d{5}|13800138000")
        for path in sorted(LIB.rglob("*")):
            if not path.is_file() or "dist" in path.relative_to(LIB).parts or path.suffix not in {".js", ".css", ".html", ".md", ".py", ".json", ".txt", ".gitignore", ""}:
                continue
            text = path.read_text(encoding="utf-8")
            for m in pattern.finditer(text):
                if sample.fullmatch(m.group(0)):
                    continue
                self.fail(f"{path.relative_to(LIB)}: {m.group(0)!r}")

    def test_the_stage_marks_every_component_root_with_its_id(self):
        core = (check.SRC / "core-ui.js").read_text(encoding="utf-8")
        self.assertIn('data-cid="${b.id}"', core)


class DarkLayerStaticTests(unittest.TestCase):
    """The colour tokens, their dark values and the CSS that carries them, read from the sources."""

    @classmethod
    def setUpClass(cls):
        import tokens

        cls.tokens = tokens
        cls.css = (check.SRC / "kit.css").read_text(encoding="utf-8")
        cls.js = (check.SRC / "kit.js").read_text(encoding="utf-8")

    def test_kit_css_and_kit_js_are_what_tools_tokens_generates(self):
        self.assertEqual(self.tokens.main(["--check"]), 0, "run py -X utf8 references/component-library/tools/tokens.py --write")

    def test_the_dark_values_pass_their_contrast_targets(self):
        self.assertEqual(self.tokens.report(), [])

    def test_the_eight_themes_of_kit_js_are_the_ones_the_table_derives_from(self):
        found = re.findall(r"\{ id: '(\w+)', name: '([^']+)', p: '(#\w+)', pd: '(#\w+)', pt: '(#\w+)', pm: '(#\w+)' \}", self.js)
        self.assertEqual([tuple(x) for x in found], [tuple(t) for t in self.tokens.THEMES_LIGHT])
        for tid, *_ in self.tokens.THEMES_LIGHT:
            self.assertIn(f"{tid}: {{ p: '", self.js)           # DARK_THEMES has all eight
            self.assertIn(f"[data-lt={tid}]{{", self.css)        # and so does the data of kit.css

    def test_the_appearance_contract_is_written_in_kit_css(self):
        for needle in (":root,.light,[data-theme=light]{color-scheme:light", "@media (prefers-color-scheme:dark){:root:not(.light):not([data-theme=light]){color-scheme:dark",
                       ".dark,[data-theme=dark]{color-scheme:dark", ":where(.dark,[data-theme=dark]) [data-lt]"):
            self.assertIn(needle, self.css)

    def test_every_variable_the_sources_use_is_defined_somewhere(self):
        defined = set(re.findall(r"(?<![\w-])(--[\w-]+)\s*:", self.css))
        used: dict[str, str] = {}
        for path in sorted(check.SRC.glob("*.js")) + [check.SRC / "ix.css", check.SRC / "lib.template.html"]:
            text = path.read_text(encoding="utf-8")
            defined |= set(re.findall(r"(?<![\w-])(--[\w-]+)\s*:", text)) | set(re.findall(r"setProperty\(\s*['\"](--[\w-]+)", text))
            for m in re.finditer(r"var\((--[\w-]+)", text):
                used.setdefault(m.group(1), path.name)
        defined |= {"--v"}  # the slider writes --v inline
        self.assertEqual({k: v for k, v in used.items() if k not in defined}, {})

    def test_tokens_cover_what_the_migration_used(self):
        names = {"--" + n for _, n, _, _ in self.tokens.table()}
        for needle in ("--card", "--soft", "--line", "--line2", "--ink", "--ink2", "--ink3", "--sh12", "--mask", "--ok", "--ok-bg", "--warn", "--warn-bg", "--danger", "--danger-bg",
                       "--neutral", "--neutral-bg", "--price", "--bg", "--ph", "--paper"):
            self.assertIn(needle, names)
        self.assertEqual(len([t for t in self.tokens.theme_rows()]), 8)

    def test_a_stage_called_dark_is_rendered_as_night_so_the_class_stays_the_switch(self):
        self.assertIn("const stageClass = (s) => (s === 'dark' ? 'night' : s)", (check.SRC / "core-def.js").read_text(encoding="utf-8"))
        self.assertIn(".st.night{", (check.SRC / "lib.template.html").read_text(encoding="utf-8"))
        self.assertNotIn(".st.dark", (check.SRC / "lib.template.html").read_text(encoding="utf-8"))

    def test_a_new_component_with_a_hard_coded_neutral_is_refused_by_the_static_check(self):
        report = check.check(check.read_library())
        self.assertEqual([e for e in report.errors if "hard-coded" in e], [])
        self.assertEqual(report.stats["hard-coded neutral or status colours"], 0)


class RegressionToolTests(unittest.TestCase):
    """The thresholds of the light regression (tools/visual_regression.py) judge what they should: nothing the eye can see passes, anti-aliasing noise does."""

    @classmethod
    def setUpClass(cls):
        import visual_regression

        cls.vr = visual_regression
        cls.tmp = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def png(self, name: str, base=(245, 246, 248), patch=None, size=(400, 300)):
        from PIL import Image

        im = Image.new("RGB", size, base)
        if patch:
            box, colour = patch
            im.paste(colour, box)
        path = self.tmp / name
        im.save(path)
        return path

    def test_identical_pictures_and_noise_pass(self):
        a = self.png("a.png")
        self.assertTrue(self.vr.judge(self.vr.image_diff(a, self.png("b.png"))))
        noisy = self.png("c.png", patch=((10, 10, 40, 40), (247, 248, 250)))   # 2 levels on a 30 px square
        self.assertTrue(self.vr.judge(self.vr.image_diff(a, noisy)))

    def test_a_visible_difference_fails(self):
        a = self.png("a2.png")
        for name, patch in (("block", ((20, 20, 120, 100), (230, 232, 236))), ("white", ((0, 0, 400, 40), (255, 255, 255)))):
            self.assertFalse(self.vr.judge(self.vr.image_diff(a, self.png(f"{name}.png", patch=patch))), name)

    def test_a_different_size_fails(self):
        d = self.vr.image_diff(self.png("s1.png"), self.png("s2.png", size=(400, 322)))
        self.assertIn("size", d)
        self.assertFalse(self.vr.judge(d))

    def test_colours_are_compared_by_value_not_by_how_the_browser_writes_them(self):
        same = self.vr.same_value
        self.assertTrue(same("rgba(255, 255, 255, 0.4)", "color(srgb 1 1 1 / 0.4)"))
        self.assertTrue(same("rgb(245, 246, 248)", "rgb(247, 248, 250)"))
        self.assertTrue(same("linear-gradient(rgba(31, 35, 41, 0), rgb(255, 255, 255))", "linear-gradient(rgba(0, 0, 0, 0), rgb(255, 255, 255))"))
        self.assertFalse(same("rgb(245, 246, 248)", "rgb(230, 232, 236)"))
        self.assertFalse(same("rgb(0, 0, 0) 0px 1px 2px", "rgb(0, 0, 0) 0px 2px 2px"))   # a shadow that moved is not the same shadow

    def test_a_moved_or_recoloured_element_is_reported(self):
        props = ["color", "backgroundColor"]
        row = lambda x, c: ["div.a", x, 0, 100, 20, c, "rgba(0, 0, 0, 0)"]   # noqa: E731
        base = {"props": props, "cards": {"X-1": [row(0, "rgb(31, 35, 41)"), row(10, "rgb(31, 35, 41)")]}}
        self.assertEqual(self.vr.compare_styles(base, {"props": props, "cards": {"X-1": [row(0, "rgb(33, 37, 43)"), row(10, "rgb(31, 35, 41)")]}}), {})
        moved = self.vr.compare_styles(base, {"props": props, "cards": {"X-1": [row(0, "rgb(31, 35, 41)"), row(160, "rgb(31, 35, 41)")]}})
        self.assertEqual(moved["X-1"]["moved_n"], 1)
        recoloured = self.vr.compare_styles(base, {"props": props, "cards": {"X-1": [row(0, "rgb(255, 255, 255)"), row(10, "rgb(31, 35, 41)")]}})
        self.assertIn("color", recoloured["X-1"]["changed"])


def fake_library(blocks: str, guide_rows: str = "") -> Path:
    """A small source directory: the real taxonomy plus one blocks file."""
    tmp = Path(tempfile.mkdtemp())
    shutil.copy(check.SRC / "taxonomy.js", tmp / "taxonomy.js")
    (tmp / "blocks-x.js").write_text(blocks + "\n" + guide_rows, encoding="utf-8")
    return tmp


def comp(cid: str, **over) -> str:
    root = cid.replace("-", "").lower()
    f = dict(name="基础数据表", style="排序", fit="订单列表", avoid="一页以内", kw="table 表格 数据表 排序 订单列表", css=f"`.{root}{{width:100%}} .{root} .a{{color:red}}`")
    f.update(over)
    return ("def({ id: '%s', name: '%s', style: '%s', fit: '%s', avoid: '%s', kw: '%s', css: %s, html: () => `<div class=\"%s\">x</div>` })\n"
            % (cid, f["name"], f["style"], f["fit"], f["avoid"], f["kw"], f["css"], root))


GUIDE = "guide('ad', 'TBL', [['场景一', '基础数据表', '原因'], ['场景二', '基础数据表', '原因'], ['场景三', '基础数据表', '原因']])\n"


def errors_of(blocks: str, guide: str = GUIDE, **kw) -> list[str]:
    tmp = fake_library(blocks, guide)
    try:
        rep = check.check(check.read_library(tmp), **kw)
        return rep.errors + [f"warning: {w}" for w in rep.warnings]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class CheckCatchesTests(unittest.TestCase):
    """The check is not a rubber stamp: each rule fails on a small library that breaks it."""

    def assertFlags(self, blocks: str, needle: str, guide: str = GUIDE, **kw):
        errs = errors_of(blocks, guide, **kw)
        self.assertTrue(any(needle in e for e in errs), (needle, errs))

    def test_a_clean_small_library_passes(self):
        errs = [e for e in errors_of(comp("AD-TBL-001") + comp("AD-TBL-002", name="勾选表")) if "no guide" not in e]
        self.assertEqual(errs, [])

    def test_duplicate_ids_gaps_and_unknown_categories(self):
        self.assertFlags(comp("AD-TBL-001") + comp("AD-TBL-001"), "used 2 times")
        self.assertFlags(comp("AD-TBL-001") + comp("AD-TBL-003", name="勾选表"), "missing 002")
        self.assertFlags(comp("AD-ZZZ-001"), "not in taxonomy")
        self.assertFlags(comp("AD-TBL-1"), "must look like")

    def test_a_declared_gap_is_allowed_and_a_stale_declaration_is_not(self):
        check.KNOWN_GAPS["AD-TBL"] = {2}
        try:
            errs = errors_of(comp("AD-TBL-001") + comp("AD-TBL-003", name="勾选表"))
            self.assertFalse(any("not continuous" in e for e in errs), errs)
            self.assertTrue(any("KNOWN_GAPS" in e for e in errors_of(comp("AD-TBL-001") + comp("AD-TBL-002", name="勾选表"))))
        finally:
            del check.KNOWN_GAPS["AD-TBL"]

    def test_selectors_must_start_with_the_block_root(self):
        self.assertFlags(comp("AD-TBL-001", css="`.adtbl001{width:1px} .on{color:red}`"), "not anchored")
        self.assertFlags(comp("AD-TBL-001", css="`.btn{width:1px}`"), "not anchored")
        self.assertFlags(comp("AD-TBL-001", css="`.adtbl002 .a{width:1px}`"), "not anchored")
        self.assertFlags(comp("AD-TBL-001", css="`@media(max-width:500px){.adtbl001 .a{width:1px} .b{width:2px}}`"), "not anchored")
        ok = errors_of(comp("AD-TBL-001", css="`.adtbl001{width:1px}.adtbl001 .a,.adtbl001:hover .b{color:#333}@keyframes spin{from{opacity:0}to{opacity:1}}`"))
        self.assertFalse(any("css" in e for e in ok), ok)

    def test_fixed_position_and_transition_all_are_refused(self):
        self.assertFlags(comp("AD-TBL-001", css="`.adtbl001{position:fixed}`"), "position:fixed")
        self.assertFlags(comp("AD-TBL-001", css="`.adtbl001{transition:all .2s}`"), "transition:all")
        ok = errors_of(comp("AD-TBL-001", css="`.adtbl001{transition:color .2s,background .2s}`"))
        self.assertFalse(any("transition" in e for e in ok), ok)

    def test_a_loud_colour_is_counted_and_dark_or_state_colours_are_not(self):
        loud = comp("AD-TBL-001", css="`.adtbl001{background:#FF2D00}`")
        self.assertFlags(loud, "saturation")                                                             # an error by default
        self.assertTrue(any(e.startswith("warning:") and "saturation" in e for e in errors_of(loud, strict_colours=False)))
        quiet = comp("AD-TBL-001", css="`.adtbl001{color:#8A5A00;background:#EAF3EE;border-color:#5a4010}`")
        self.assertFalse(any("saturation" in e for e in errors_of(quiet)))

    def test_a_hard_coded_neutral_or_status_colour_is_refused_with_its_id_and_a_token(self):
        for css, needle in (("`.adtbl001{background:#fff}`", "var(--card)"), ("`.adtbl001{background:#F2F3F5}`", "var(--soft)"), ("`.adtbl001{border:1px solid #E6E8EC}`", "var(--line2)"),
                            ("`.adtbl001{color:#5B6470}`", "var(--ink2)"), ("`.adtbl001{box-shadow:0 8px 24px rgba(31,35,41,.12)}`", "var(--sh12)"),
                            ("`.adtbl001{color:#3F7D58;background:#EAF3EE}`", "var(--ok)"), ("`.adtbl001{background:rgba(31,35,41,.38)}`", "var(--mask)"),
                            ("`.adtbl001 .a{stroke:#EEF0F3}`", "var(--n4)"), ("`.adtbl001{color:var(--pd)}`", "var(--p-text)"), ("`.adtbl001{background:var(--dg)}`", "var(--danger-fill)")):
            errs = errors_of(comp("AD-TBL-001", css=css))
            self.assertTrue(any("AD-TBL-001" in e and "hard-coded" in e and needle in e for e in errs), (css, errs))

    def test_white_text_black_shadows_accents_and_tokens_are_allowed(self):
        ok = comp("AD-TBL-001", css="`.adtbl001{background:var(--card);color:var(--ink);border:1px solid var(--line2);box-shadow:0 8px 24px var(--sh12),0 2px 4px rgba(0,0,0,.2)}"
                                    ".adtbl001 .b{background:var(--p);color:#fff}.adtbl001 .c{background:#B58A5E;color:#FFFFFF}.adtbl001 .d{color:rgba(255,255,255,.8)}`")
        self.assertEqual([e for e in errors_of(ok) if "hard-coded" in e], [])

    def test_dark_and_light_are_not_class_names_of_a_component(self):
        self.assertFlags(comp("AD-TBL-001", css="`.adtbl001 .dark{color:var(--ink)}`"), "appearance switch")
        self.assertFlags(comp("AD-TBL-001").replace('class="adtbl001"', 'class="adtbl001 light"'), "appearance switch")

    def test_field_limits(self):
        self.assertFlags(comp("AD-TBL-001", name="这是一个名字特别特别长的组件名称"), "name has")
        self.assertFlags(comp("AD-TBL-001", style="风格标签太长了吧"), "style has")
        self.assertFlags(comp("AD-TBL-001", kw="table 表格"), "kw has 2 words")
        self.assertFlags(comp("AD-TBL-001", fit=""), "fit is empty")
        self.assertFlags(comp("AD-TBL-001", avoid=""), "avoid is empty")
        self.assertFlags(comp("AD-TBL-001") + comp("AD-TBL-002"), "also the name of")

    def test_guides_exist_and_recommend_real_names(self):
        self.assertFlags(comp("AD-TBL-001"), "no guide", guide="")
        bad = "guide('ad', 'TBL', [['a', '基础数据表', 'x'], ['b', '不存在的组件', 'x'], ['c', '基础数据表', 'x']])\n"
        self.assertFlags(comp("AD-TBL-001"), "不存在的组件", guide=bad)
        short = "guide('ad', 'TBL', [['a', '基础数据表', 'x']])\n"
        self.assertFlags(comp("AD-TBL-001"), "expected 3 to 10", guide=short)
        ok = "guide('ad', 'TBL', [['a', '基础数据表 / 基础数据表', 'x'], ['b', '基础数据表 + 基础数据表', 'x'], ['c', '基础数据表 → 基础数据表', 'x']])\n"
        self.assertFalse(any("guide" in e for e in errors_of(comp("AD-TBL-001"), guide=ok)))


class LexerTests(unittest.TestCase):
    def lex(self, text):
        return check.Lexed(text)

    def test_quotes_comments_regex_and_templates_do_not_confuse_the_reader(self):
        src = ("// def({ id: 'AD-TBL-009' }) in a comment\n"
               "const re = /def\\(|'/g, s = \"def({ id: 'AD-TBL-008' })\"\n"
               "def({ id: 'AD-TBL-001', name: 'a' + 'b', css: `.x{a:${f(`.y{b:1}`)}}`, html: () => `<i>${[1, 2].map((n) => `(${n})`).join('')}</i>` })\n")
        lx = self.lex(src)
        self.assertEqual(len(list(check.calls(lx, ("def",)))), 1)

    def test_strings_are_cooked_and_interpolations_become_placeholders(self):
        lx = self.lex("const a = 'it\\'s \\u4e2d', b = `x${y}z`\n")
        texts = sorted(lit.text for lit in lx.lits.values())
        self.assertEqual(texts, ["it's 中", "x\x00z"])

    def test_a_string_concatenation_is_read_but_a_call_is_not(self):
        lx = self.lex("f('ab' + \"cd\", g('x'))")
        first, second = lx.split(lx.text.index("(") + 1, lx.close(lx.text.index("(")))
        self.assertEqual(lx.string(*first), "abcd")
        self.assertIsNone(lx.string(*second))

    def test_the_real_files_all_read_to_the_end(self):
        for path in sorted(check.SRC.glob("*.js")):
            check.Lexed(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------------------------------------------------------
# Build
# ------------------------------------------------------------------------------------------------------------------------------------------------


class BuildTests(unittest.TestCase):
    def test_a_one_file_build_has_its_components_and_a_sane_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "small.html"
            self.assertEqual(builder.main(["--files", "blocks-ad-comm.js", "--out", str(out)]), 0)
            text = out.read_text(encoding="utf-8")
            self.assertTrue("id: 'AD-COMM-001'" in text and "id: 'AD-COMM-010'" in text)
            self.assertFalse("id: 'AD-TBL-001'" in text)
            self.assertTrue("MP-CARD-001" in text)  # the 52 first-generation templates are always in
            self.assertTrue(300_000 < out.stat().st_size < 2_000_000, out.stat().st_size)
            self.assertEqual([slot for slot in builder.load_builder().SLOTS if f"/*__{slot}__*/" in text], [])  # every slot of the template is filled

    def test_the_full_build_has_every_id_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "full.html"
            self.assertEqual(builder.main(["--out", str(out)]), 0)
            text = out.read_text(encoding="utf-8")
            self.assertGreater(out.stat().st_size, 2_000_000)
            ids = [c.id for c in check.read_library().comps if not c.legacy]
            self.assertEqual(len(ids), EXPECTED_TOTAL - 52)
            for cid in ids:
                self.assertEqual(text.count(f"id: '{cid}'"), 1, cid)
            self.assertEqual([slot for slot in builder.load_builder().SLOTS if f"/*__{slot}__*/" in text], [])

    def test_the_build_script_runs_from_the_command_line(self):
        import subprocess

        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "build_component_library.py"), "--index", "--check"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual((run.returncode, run.stdout.strip()), (0, "registry/index.md: up to date"), run.stderr)


# ------------------------------------------------------------------------------------------------------------------------------------------------
# Browser
# ------------------------------------------------------------------------------------------------------------------------------------------------

EXERCISE = r"""
async (id) => {
  const root = document.querySelector('.ixr[data-id="' + id + '"]');
  const fails = [], kinds = {}, later = [];
  const note = (k) => { kinds[k] = (kinds[k] || 0) + 1; };
  const bad = (k, m) => fails.push(id + ' ' + k + ': ' + m);
  const on = (e) => e.classList.contains('on');
  const num = (v, d) => (v === undefined || v === '' || isNaN(+v) ? d : +v);
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const $ = (r, s) => [...r.querySelectorAll(s)];
  if (!root) return { fails: [id + ': no root'], kinds };

  for (const c of $(root, '[data-ix=tabs]')) {
    const ts = $(c, '[data-t]'); if (ts.length < 2) continue;
    const t = ts.find((x) => !on(x)) || ts[1]; t.click(); note('tabs');
    if (!on(t) || ts.filter(on).length !== 1) bad('tabs', 'the clicked tab is not the only one on');
    const panels = $(root, '[data-p]').filter((p) => (p.dataset.g || '') === (c.dataset.g || ''));
    if (panels.some((p) => p.dataset.p === t.dataset.t)) {
      const shown = panels.filter((p) => !p.hidden);
      if (!shown.length || shown.some((p) => p.dataset.p !== t.dataset.t)) bad('tabs', 'panel of ' + t.dataset.t + ' is not the one shown');
    }
  }
  for (const c of $(root, '[data-ix=radio]')) {
    const os = $(c, '[data-o]'); if (os.length < 2) continue;
    const t = os.find((x) => !on(x)) || os[1]; t.click(); note('radio');
    if (!on(t) || os.filter(on).length !== 1) bad('radio', 'not a single selection');
  }
  for (const c of $(root, '[data-ix=multi]')) {
    const os = $(c, '[data-o]'); const t = os.find((x) => !on(x)); if (!t) continue;
    const before = os.filter(on).length; t.click(); note('multi');
    if (before < num(c.dataset.max, 99) && !on(t)) bad('multi', 'option did not turn on');
  }
  for (const t of $(root, '[data-ix=toggle]')) {
    const before = on(t); t.click(); note('toggle');
    if (on(t) === before || t.getAttribute('aria-checked') !== String(on(t))) bad('toggle', 'state did not flip with aria-checked');
  }
  for (const c of $(root, '[data-ix=stepper]')) {
    const v = c.querySelector('[data-val]'), plus = c.querySelector('[data-d="1"]'); if (!v || !plus) continue;
    const mn = num(c.dataset.min, 0), mx = num(c.dataset.max, 99), st = num(c.dataset.step, 1), b = num(v.textContent, 0);
    plus.click(); note('stepper');
    const want = Math.max(mn, Math.min(mx, b + st));
    if (num(v.textContent, -1) !== want) bad('stepper', 'value ' + b + ' -> ' + v.textContent + ', expected ' + want);
  }
  for (const c of $(root, '[data-ix=acc]')) {
    const h = c.querySelector('[data-h]'); if (!h) continue; const it = h.closest('.ix-ai'), was = it.classList.contains('open');
    h.click(); note('acc'); if (it.classList.contains('open') === was) bad('acc', 'item did not toggle');
  }
  for (const o of $(root, '[data-open]').slice(0, 3)) {
    const ov = root.querySelector('[data-ov="' + o.dataset.open + '"]'); if (!ov) continue;
    o.click(); note('overlay'); if (!ov.classList.contains('show')) bad('overlay', o.dataset.open + ' did not open');
    const x = ov.querySelector('[data-close], .ix-mask'); if (x) { x.click(); if (ov.classList.contains('show')) bad('overlay', o.dataset.open + ' did not close'); }
  }
  for (const c of $(root, '[data-ix=dd]')) {
    const tg = c.querySelector('[data-tg]'), os = $(c, '[data-o]'); if (!tg || os.length < 2) continue;
    tg.click(); if (!c.classList.contains('open')) bad('dd', 'menu did not open');
    const o = os[1], lab = c.querySelector('[data-label]'); o.click(); note('dd');
    if ($(c, '[data-o].on').length !== 1 || c.classList.contains('open') || (lab && !lab.textContent.trim())) bad('dd', 'option not applied');  /* blocks with their own filter logic redraw the menu, so the options are read again */
  }
  for (const t of $(root, '[data-toast]').slice(0, 2)) {
    const n = $(root, '.ix-toast').length; t.click(); note('toast');
    if ($(root, '.ix-toast').length <= n) bad('toast', 'no toast for ' + t.dataset.toast);
  }
  for (const c of $(root, '[data-ix=rate]')) {
    const ns = $(c, '[data-n]'); if (ns.length < 3) continue; ns[2].click(); note('rate');
    if (ns.filter(on).length !== 3) bad('rate', 'expected 3 stars on, got ' + ns.filter(on).length);
  }
  for (const m of $(root, '[data-ix=like]')) {
    const n = m.querySelector('[data-n]'), b = n ? num(n.textContent, 0) : 0, was = on(m); m.click(); note('like');
    if (on(m) === was || (n && num(n.textContent, -1) !== Math.max(0, b + (was ? -1 : 1)))) bad('like', 'state or count wrong');
  }
  for (const tb of $(root, '[data-ix=sort]')) {
    const th = tb.querySelector('th[data-sort]'); if (!th) continue;
    th.click(); note('sort'); const first = th.getAttribute('aria-sort'); th.click();
    if (!first || th.getAttribute('aria-sort') === first) bad('sort', 'aria-sort did not change between two clicks');
  }
  for (const c of $(root, '[data-ix=checks]')) {
    const all = c.querySelector('[data-all]'), cs = $(c, '[data-c]'); if (!all || !cs.length) continue;
    if (cs.some(on) && !cs.every(on)) { all.click(); }
    if (cs.every(on)) all.click();
    all.click(); note('checks');
    if (!cs.every(on)) bad('checks', 'select all did not select every row');
    $(root, '[data-count]').forEach((e) => { if (num(e.textContent, -1) !== cs.length) bad('checks', 'count shows ' + e.textContent + ' of ' + cs.length); });
    all.click(); if (cs.some(on)) bad('checks', 'second click did not clear');
  }
  for (const c of $(root, '[data-ix=pager]')) {
    const bs = $(c, '[data-pg]'); if (bs.length < 2) continue; const t = bs.find((x) => !on(x)); t.click(); note('pager');
    if (!on(t) || bs.filter(on).length !== 1) bad('pager', 'page did not move');
  }
  for (const c of $(root, '[data-ix=tree]')) {
    const x = c.querySelector('[data-x]'); if (!x) continue; const li = x.closest('li'), was = li.classList.contains('open'); x.click(); note('tree');
    if (li.classList.contains('open') === was) bad('tree', 'node did not toggle');
  }
  for (const c of $(root, '[data-ix=steps]')) {
    const next = c.querySelector('[data-d="1"]'), sp = $(c, '.sp'); if (!next || next.disabled || sp.length < 2) continue;
    const i0 = sp.findIndex(on); next.click(); note('steps'); if (sp.findIndex(on) !== Math.min(sp.length - 1, Math.max(0, i0) + 1)) bad('steps', 'step did not advance');
  }
  for (const c of $(root, '[data-ix=cal]')) {
    const ds = $(c, '[data-day]'); if (ds.length < 3) continue; ds[2].click(); note('cal'); if (!on(ds[2])) bad('cal', 'day did not turn on');
  }
  for (const c of $(root, '[data-ix=upload]')) {
    const add = c.querySelector('[data-add]'); if (!add || add.hidden) continue; const n = $(c, '.up-i').length, mx = num(c.dataset.max, 6);
    add.click(); note('upload'); if (n < mx && $(c, '.up-i').length !== n + 1) bad('upload', 'thumbnail not added');
    const rm = c.querySelector('[data-rm]'); if (rm) { const k = $(c, '.up-i').length; rm.click(); if ($(c, '.up-i').length !== k - 1) bad('upload', 'thumbnail not removed'); }
  }
  for (const i of $(root, 'input[data-ix=search]')) {
    const list = root.querySelector(i.dataset.list); if (!list || !list.children.length) continue;
    i.value = 'zzzz-no-match'; i.dispatchEvent(new Event('input', { bubbles: true })); note('search');
    if ([...list.children].some((e) => !e.hidden)) bad('search', 'a row still shows for a text nothing contains');
    i.value = ''; i.dispatchEvent(new Event('input', { bubbles: true }));
    if ([...list.children].some((e) => e.hidden)) bad('search', 'rows stay hidden after the text is cleared');
  }
  for (const c of $(root, '[data-ix=slider]')) {
    const rt = c.querySelector('.rt'); if (!rt) continue; const r = rt.getBoundingClientRect(); if (!r.width) continue;
    rt.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, clientX: r.left + r.width * 0.75, clientY: r.top + 2, pointerType: 'mouse' }));
    document.dispatchEvent(new PointerEvent('pointerup', { bubbles: true })); note('slider');
    const v = parseFloat(c.style.getPropertyValue('--v')); if (!(v > 70 && v < 80)) bad('slider', '--v is ' + v + ' after a press at 75%');
  }
  for (const c of $(root, '[data-ix=carousel]')) {
    const next = c.querySelector('[data-d="1"]'); if (next) { next.click(); note('carousel'); later.push(() => { if ($(c, '.dots > i.on').length > 1) bad('carousel', 'more than one dot on'); }); }
  }
  for (const m of $(root, '[data-ix=remove]').slice(0, 1)) { const row = m.closest('[data-row]') || m.parentElement; m.click(); note('remove'); later.push(() => { if (row.isConnected) bad('remove', 'row still there'); }); }
  for (const m of $(root, '[data-ix=swipe] [data-del]').slice(0, 1)) { const row = m.closest('[data-ix=swipe]'); m.click(); note('swipe-delete'); later.push(() => { if (row.isConnected) bad('swipe', 'row still there'); }); }
  if (later.length) { await wait(700); later.forEach((f) => f()); }
  return { fails, kinds };
}
"""

SCOPE = r"""
(legacy) => {
  const bad = [], skip = new Set(legacy);
  for (const b of BLOCKS) {
    if (skip.has(b.id)) continue;
    const root = (b.dom + b.cat + b.id.slice(-3)).toLowerCase();
    const sheet = new CSSStyleSheet();
    try { sheet.replaceSync(b.css); } catch (e) { bad.push(b.id + ' css does not parse'); continue; }
    const seen = new Set();
    const walk = (rules) => { for (const r of rules) {
      if (r.selectorText !== undefined) r.selectorText.split(/,(?![^(]*\))/).forEach((s) => { s = s.trim();
        const ok = s.startsWith('.' + root) || s.startsWith('.ixr[data-id="' + b.id + '"]') || (s.startsWith('.ixr:has(') && s.includes(root));
        if (!ok && !seen.has(s)) { seen.add(s); bad.push(b.id + ' ' + s.slice(0, 70)); } });
      else if (r.cssRules && !(r instanceof CSSKeyframesRule)) walk(r.cssRules);
    } };
    walk(sheet.cssRules);
    const first = (() => { const d = document.createElement('div'); d.innerHTML = b.html(); return d.firstElementChild; })();
    if (!first || !first.classList.contains(root)) bad.push(b.id + ' html root is not .' + root);
  }
  return bad;
}
"""


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class BuiltLibraryTests(unittest.TestCase):
    """Opens the full build in a real browser."""

    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright

        cls.tmp = Path(tempfile.mkdtemp())
        cls.html = cls.tmp / "library.html"
        builder.main(["--out", str(cls.html)])
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(channel="msedge")
        cls.static_ids = {c.id for c in check.read_library().comps}

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def open(self, width: int, height: int = 900, path: Path | None = None, scheme: str | None = None, init: str | None = None):
        extra = {"color_scheme": scheme} if scheme else {}
        ctx = self.browser.new_context(viewport={"width": width, "height": height}, locale="zh-CN", has_touch=width < 700, **extra)
        if init:
            ctx.add_init_script(init)
        page = ctx.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append("pageerror " + str(e)[:200]))
        page.goto((path or self.html).as_uri())
        page.wait_for_function("typeof BLOCKS !== 'undefined' && document.querySelectorAll('.tc, .cmb').length > 0", timeout=15000)
        self.addCleanup(ctx.close)
        return page, errors

    def categories(self, page):
        out = []
        for dom in ("mp", "ad"):
            page.click(f'[data-dom="{dom}"]')
            out += [(dom, c) for c in page.eval_on_selector_all("[data-cat]", "(e) => e.map((x) => x.dataset.cat)")]
        return out

    def test_the_page_holds_every_component_and_loads_without_errors(self):
        page, errors = self.open(1500)
        self.assertEqual(page.evaluate("BLOCKS.length"), EXPECTED_TOTAL)
        self.assertEqual(set(page.evaluate("BLOCKS.map((b) => b.id)")), self.static_ids)
        self.assertEqual(errors, [])
        self.assertEqual(page.evaluate("window.__REGISTRY__().length"), EXPECTED_TOTAL)

    def test_the_css_of_every_block_hangs_off_its_root_at_run_time(self):
        page, errors = self.open(1500)
        legacy = [c.id for c in check.read_library().comps if c.legacy]
        bad = page.evaluate(SCOPE, legacy)
        self.assertEqual(bad, [], f"{len(bad)} problems: {bad[:12]}")
        self.assertEqual(errors, [])

    def sweep(self, width: int):
        page, errors = self.open(width)
        total = 0
        for dom, cat in self.categories(page):
            page.click(f'[data-dom="{dom}"]')
            page.click(f'[data-cat="{cat}"]')
            got = page.evaluate("""() => {
              const want = BLOCKS.filter((b) => b.dom === S.dom && b.cat === S.cat).map((b) => b.id);
              const roots = [...document.querySelectorAll('.ixr[data-id]')];
              return { want, cids: roots.map((r) => r.dataset.cid), ids: roots.map((r) => r.dataset.id), empty: roots.filter((r) => !r.children.length || r.getBoundingClientRect().height < 4).map((r) => r.dataset.id),
                       sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, guide: !!document.querySelector('.guide table') }
            }""")
            where = f"{width}px {dom}-{cat}"
            if cat == "COMBO":
                continue
            self.assertEqual(got["cids"], got["ids"], where)
            self.assertEqual(sorted(got["ids"]), sorted(got["want"]), where)
            self.assertEqual(got["empty"], [], f"{where}: empty stage")
            self.assertLessEqual(got["sw"], got["cw"] + 1, f"{where}: horizontal page scroll {got['sw']} > {got['cw']}")
            self.assertTrue(got["guide"], f"{where}: no 怎么选 table")
            total += len(got["ids"])
        self.assertEqual(total, EXPECTED_TOTAL)
        self.assertEqual(errors, [])

    def test_every_category_renders_on_the_desktop_with_a_data_cid_on_each_component(self):
        self.sweep(1500)

    def test_every_category_renders_on_a_phone_without_pushing_the_page_wide(self):
        self.sweep(390)

    def cycle(self, width: int):
        page, errors = self.open(width)
        themes = page.eval_on_selector_all("[data-theme]", "(e) => e.map((x) => x.dataset.theme)")
        icons = page.eval_on_selector_all("[data-icon]", "(e) => e.map((x) => x.dataset.icon)")
        self.assertEqual((len(themes), len(icons)), (8, 4))
        for dom, cat in (("mp", "ENT"), ("mp", "MKT"), ("mp", "MEM"), ("ad", "TBL")):
            page.click(f'[data-dom="{dom}"]')
            page.click(f'[data-cat="{cat}"]')
            for kind, values in (("theme", themes), ("icon", icons)):
                for v in values:
                    page.click(f'[data-{kind}="{v}"]')
                    state = page.evaluate("() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, p: getComputedStyle(document.getElementById('root')).getPropertyValue('--p').trim(), n: document.querySelectorAll('.ixr[data-cid]').length })")
                    self.assertLessEqual(state["sw"], state["cw"] + 1, f"{width}px {dom}-{cat} {kind} {v}")
                    self.assertTrue(state["n"] > 0 and state["p"].startswith("#"), (kind, v, state))
        self.assertEqual(errors, [])

    def test_eight_themes_and_four_icon_styles_switch_cleanly_on_the_desktop(self):
        self.cycle(1500)

    def test_eight_themes_and_four_icon_styles_switch_cleanly_on_a_phone(self):
        self.cycle(390)

    def test_every_component_reacts_to_clicks_without_errors(self):
        """Not only a sample of two or three per category: every component is clicked through (about ten seconds), by the kind of control it carries."""
        page, errors = self.open(1500)
        kinds: dict[str, int] = {}
        clicked = 0
        for dom, cat in self.categories(page):
            if cat == "COMBO":
                continue
            page.click(f'[data-dom="{dom}"]')
            page.click(f'[data-cat="{cat}"]')
            for cid in page.eval_on_selector_all(".ixr[data-id]", "(e) => e.map((x) => x.dataset.id)"):
                page.evaluate("(id) => document.querySelector('.ixr[data-id=\"' + id + '\"]').scrollIntoView({ block: 'center' })", cid)
                result = page.evaluate(EXERCISE, cid)
                self.assertEqual(result["fails"], [], f"{dom}-{cat} {cid}")
                for k, n in result["kinds"].items():
                    kinds[k] = kinds.get(k, 0) + n
                clicked += 1
        self.assertEqual(clicked, EXPECTED_TOTAL)
        self.assertGreaterEqual(len(kinds), 14, f"the clicks only reached {sorted(kinds)}")
        self.assertEqual(errors, [])

    def test_every_component_has_something_to_do(self):
        """A control hook (data-ix, data-open, data-toast) in its markup or a js hook; the two static displays are named in KNOWN_STATIC."""
        page, errors = self.open(1500)
        idle = page.evaluate("""() => BLOCKS.filter((b) => { const d = document.createElement('div'); d.innerHTML = b.html(); return !b.js && !d.querySelector('[data-ix],[data-open],[data-toast]'); }).map((b) => b.id)""")
        self.assertEqual(sorted(idle), sorted(check.KNOWN_STATIC))
        self.assertEqual(errors, [])

    def test_real_mouse_clicks_reach_the_controls(self):
        """Playwright clicks with the real pointer (the element must be visible, stable and not covered), not element.click()."""
        page, errors = self.open(1500)
        cases = [  # kind, the control, which one to press, and the state read before and after (read again: blocks that redraw their tabs or menu replace the node)
            ("tabs", "[data-ix=tabs] [data-t]", ":not(.on)", "e => e.classList.contains('on')"),
            ("toggle", "[data-ix=toggle]", "", "e => e.classList.contains('on') + e.getAttribute('aria-checked')"),
            ("radio", "[data-ix=radio] [data-o]", ":not(.on)", "e => e.classList.contains('on')"),
            ("acc", "[data-ix=acc] [data-h]", "", "e => e.closest('.ix-ai').classList.contains('open')"),
            ("like", "[data-ix=like]", "", "e => e.classList.contains('on')"),
            ("dd", "[data-ix=dd] [data-tg]", "", "e => e.closest('[data-ix=dd]').classList.contains('open')"),
        ]
        for kind, base, only, state in cases:
            found = page.evaluate("""([base, only]) => { for (const b of BLOCKS) { const d = document.createElement('div'); d.innerHTML = b.html();
                const all = [...d.querySelectorAll(base)], i = all.findIndex((e) => !only || e.matches(only)); if (i >= 0) return [b.id, i]; } }""", [base, only])
            self.assertTrue(found, kind)
            cid, nth = found
            page.evaluate("(id) => gotoId(id)", cid)
            target = page.locator(f'.ixr[data-id="{cid}"]').locator(base).nth(nth)
            before = target.evaluate(state)
            target.click(timeout=5000)
            self.assertNotEqual(target.evaluate(state), before, f"{kind} in {cid}: the state did not change after a real click")
        self.assertEqual(errors, [])

    def test_a_mouse_drag_scrolls_a_horizontal_strip(self):
        page, errors = self.open(1500)
        page.evaluate("(id) => gotoId(id)", "MP-ENT-004")
        strip = page.locator('.ixr[data-id="MP-ENT-004"] .i4')
        strip.scroll_into_view_if_needed()
        box = strip.bounding_box()
        page.mouse.move(box["x"] + box["width"] * 0.8, box["y"] + box["height"] / 2)
        page.mouse.down()
        page.mouse.move(box["x"] + box["width"] * 0.1, box["y"] + box["height"] / 2, steps=6)
        page.mouse.up()
        self.assertGreater(strip.evaluate("e => e.scrollLeft"), 10)
        self.assertEqual(errors, [])

    def test_search_and_the_index_page_carry_the_same_marks(self):
        page, errors = self.open(1500)
        page.fill("#q", "AD-TBL")
        page.wait_for_selector(".tc")
        found = page.evaluate("() => [...document.querySelectorAll('.ixr[data-id]')].every((r) => r.dataset.cid === r.dataset.id) && document.querySelectorAll('.ixr[data-id]').length")
        self.assertGreaterEqual(found, 18)
        page.fill("#q", "")
        page.click('[data-dom="idx"]')
        self.assertEqual(page.evaluate("document.querySelectorAll('#idxb tr').length"), EXPECTED_TOTAL)
        self.assertEqual(errors, [])

    def test_a_hash_goes_straight_to_a_component(self):
        page, errors = self.open(1500)
        page.goto(self.html.as_uri() + "#AD-FLOW-003")
        page.reload()
        page.wait_for_selector('.ixr[data-cid="AD-FLOW-003"]')
        self.assertEqual(errors, [])

    # ---- the dark appearance ------------------------------------------------------------------------------------------------------------------

    def categories_of_the_library(self) -> list[tuple[str, str]]:
        seen: list[tuple[str, str]] = []
        for c in check.read_library().comps:
            if (c.dom, c.cat) not in seen:
                seen.append((c.dom, c.cat))
        return seen

    def dark(self, width: int, theme: str = "rose", mode: str = "media", categories=None) -> dict:
        import dark_audit

        return dark_audit.audit(self.browser, self.html, width, theme, mode, categories)

    def assert_dark_ok(self, res: dict, where: str, whole: bool = True):
        fails = {cid: v["fails"] for cid, v in res["comps"].items() if v["fails"]}
        unexpected = sorted(set(fails) - set(DARK_CONTRAST_EXCEPTIONS))
        self.assertEqual(unexpected, [], f"{where}: " + str([(c, [(f["kind"], f["label"], f["ratio"], f["fg"], f["bg"]) for f in fails[c][:3]]) for c in unexpected[:6]]))
        if whole:
            self.assertEqual(sorted(k for k in DARK_CONTRAST_EXCEPTIONS if k not in fails), [], f"{where}: an exception that no longer fails, delete it")
            self.assertEqual(res["scanned"], EXPECTED_TOTAL, where)
        white = {cid: v["white"][:2] for cid, v in res["comps"].items() if v["white"]}
        self.assertEqual(white, {}, f"{where}: a large white panel in the dark appearance")
        self.assertEqual(res["errors"], [], where)

    def test_every_component_is_readable_in_the_dark_when_the_system_asks_for_it(self):
        """All 303 components, the desktop, the default theme, a dark system appearance and nothing else switched: text 4.5:1, large text, icons and placeholders 3:1."""
        res = self.dark(1500, "rose", "media")
        self.assert_dark_ok(res, "1500 px, system dark")
        self.assertGreater(sum(v["text"] for v in res["comps"].values()), 7000)         # the walk really reached the text
        self.assertGreater(sum(v["icons"] for v in res["comps"].values()), 1000)

    def test_the_class_switch_gives_the_same_dark_as_the_system_appearance(self):
        by_class = self.dark(1500, "rose", "class")
        self.assert_dark_ok(by_class, "1500 px, class dark")
        by_media = self.dark(1500, "rose", "media")
        self.assertEqual({k: len(v["fails"]) for k, v in by_class["comps"].items()}, {k: len(v["fails"]) for k, v in by_media["comps"].items()})

    def test_every_component_is_readable_in_the_dark_on_a_phone(self):
        self.assert_dark_ok(self.dark(390, "rose", "class"), "390 px, class dark")

    def test_the_eight_themes_are_readable_in_the_dark_on_the_desktop_and_on_a_phone(self):
        themes = [t[0] for t in __import__("tokens").THEMES_LIGHT]
        for theme in themes:
            self.assert_dark_ok(self.dark(1500, theme, "class"), f"1500 px, {theme}, dark")
        cats = self.categories_of_the_library()
        for i, theme in enumerate(themes):  # on a phone each theme takes its share of the categories; together they are the whole library
            part = [c for j, c in enumerate(cats) if j % len(themes) == i]
            self.assert_dark_ok(self.dark(390, theme, "class", part), f"390 px, {theme}, dark", whole=False)

    def test_the_light_appearance_is_still_judged_by_the_same_walk(self):
        """The control: the same audit in the light appearance finds no white-panel problem and reports the dark switch as off."""
        res = self.dark(1500, "rose", "light", [("ad", "TBL"), ("mp", "CARD")])
        self.assertGreater(res["scanned"], 20)
        self.assertEqual(res["errors"], [])

    def test_the_appearance_switch_in_the_library_page(self):
        page, errors = self.open(1500, scheme="light")
        self.assertEqual(page.eval_on_selector_all("[data-ap]", "(e) => e.map((x) => x.dataset.ap + ':' + x.getAttribute('aria-pressed'))"), ["system:true", "light:false", "dark:false"])
        page.click('[data-ap="dark"]')
        state = page.evaluate("() => ({ cls: document.documentElement.className, attr: document.documentElement.dataset.theme, store: localStorage.getItem('luz-theme'), mode: getAppearance(), card: getComputedStyle(document.getElementById('root')).getPropertyValue('--card').trim(), scheme: getComputedStyle(document.documentElement).colorScheme })")
        self.assertEqual((state["cls"], state["attr"], state["store"], state["mode"], state["scheme"]), ("dark", "dark", "dark", "dark", "dark"))
        self.assertEqual(state["card"], self.dark_card())
        self.assertEqual(page.eval_on_selector_all("[data-ap]", "(e) => e.map((x) => x.getAttribute('aria-pressed'))"), ["false", "false", "true"])
        page.reload()
        page.wait_for_function("typeof BLOCKS !== 'undefined'")
        self.assertEqual(page.evaluate("document.documentElement.className"), "dark")      # remembered, and applied before the page paints
        page.click('[data-ap="light"]')
        self.assertEqual(page.evaluate("() => [document.documentElement.className, getComputedStyle(document.getElementById('root')).getPropertyValue('--card').trim()]"), ["light", "#FFFFFF"])
        page.click('[data-ap="system"]')
        self.assertEqual(page.evaluate("() => [document.documentElement.className, document.documentElement.getAttribute('data-theme'), localStorage.getItem('luz-theme')]"), ["", None, None])
        self.assertEqual(errors, [])

    def dark_card(self) -> str:
        return {n: dk for _, n, _, dk in __import__("tokens").table()}["card"]

    def test_the_appearance_contract_for_a_class_on_any_ancestor(self):
        """A dark system follows itself, a light class forces light, a dark class forces dark, on the root or on any container, nested containers win by distance,
        data-theme works like the class, and the theme colours (applyTheme) follow the scheme of the element that carries them."""
        tk = __import__("tokens")
        table = {n: (lt, dk) for _, n, lt, dk in tk.table()}
        th = {t["id"]: t for t in tk.theme_rows()}
        scenario = r"""() => {
          const css = (el, n) => getComputedStyle(el).getPropertyValue(n).trim();
          const mk = (parent, cls, attrs) => { const d = document.createElement('div'); d.className = cls || ''; for (const k in (attrs || {})) d.setAttribute(k, attrs[k]); parent.appendChild(d); return d; };
          const read = (el) => ({ card: css(el, '--card'), p: css(el, '--p'), ptext: css(el, '--p-text'), scheme: getComputedStyle(el).colorScheme });
          const html = document.documentElement, host = mk(document.body, 'probe'), out = {};
          out.plain = read(mk(host, ''));
          const lightBox = mk(host, 'light'), darkBox = mk(host, 'dark'), attrBox = mk(host, '', { 'data-theme': 'dark' });
          out.light = read(lightBox); out.dark = read(darkBox); out.attr = read(attrBox);
          out.nestedLightInDark = read(mk(darkBox, 'light')); out.nestedDarkInLight = read(mk(lightBox, 'dark')); out.inDark = read(mk(darkBox, ''));
          const themed = mk(host, '', { 'data-lt': 'blue' }); out.blue = read(themed);
          out.blueLight = read(mk(host, 'light', { 'data-lt': 'blue' })); out.blueDark = read(mk(host, 'dark', { 'data-lt': 'blue' }));
          out.blueInDark = read(mk(mk(host, 'dark'), '', { 'data-lt': 'blue' })); out.blueInLightInDark = read(mk(mk(mk(host, 'dark'), 'light'), '', { 'data-lt': 'blue' }));
          html.classList.add('dark'); out.rootDark = read(mk(host, '')); out.rootDarkBlue = read(mk(host, '', { 'data-lt': 'blue' }));
          html.classList.remove('dark'); html.classList.add('light'); out.rootLight = read(mk(host, '')); html.classList.remove('light');
          host.remove(); return out; }"""
        for os_scheme in ("light", "dark"):
            page, errors = self.open(1500, scheme=os_scheme)
            r = page.evaluate(scenario)
            dark_os = os_scheme == "dark"
            L, D = table["card"]
            self.assertEqual(r["plain"]["card"], D if dark_os else L, f"{os_scheme} system, no class")
            self.assertEqual(r["plain"]["scheme"], "dark" if dark_os else "light")
            self.assertEqual((r["light"]["card"], r["light"]["scheme"]), (L, "light"), "a light class forces light")
            self.assertEqual((r["dark"]["card"], r["dark"]["scheme"]), (D, "dark"), "a dark class forces dark")
            self.assertEqual((r["attr"]["card"], r["attr"]["scheme"]), (D, "dark"), "data-theme=dark works like the class")
            self.assertEqual(r["nestedLightInDark"]["card"], L)
            self.assertEqual(r["nestedDarkInLight"]["card"], D)
            self.assertEqual(r["inDark"]["card"], D)
            blue = th["blue"]
            self.assertEqual(r["blueLight"]["p"].upper(), blue["light"]["p"], "a themed element that is forced light uses the light data of its theme")
            self.assertEqual(r["blueDark"]["p"].upper(), blue["dark"]["p"], "and the dark data when forced dark")
            self.assertEqual(r["blueDark"]["ptext"].upper(), blue["dark"]["text"])
            self.assertEqual(r["blueLight"]["ptext"].upper(), blue["light"]["pd"], "--p-text is --pd in the light")
            self.assertEqual(r["blueInDark"]["p"].upper(), blue["dark"]["p"], "a themed element inside a dark container is dark")
            self.assertEqual(r["blueInLightInDark"]["p"].upper(), blue["light"]["p"], "inside a light container inside a dark one it is light again")
            self.assertEqual(r["blue"]["p"].upper(), (blue["dark"]["p"] if dark_os else blue["light"]["p"]), "a themed element with no class follows the system")
            self.assertEqual(r["rootDark"]["card"], D, "a dark class on <html>")
            self.assertEqual(r["rootDarkBlue"]["p"].upper(), blue["dark"]["p"])
            self.assertEqual(r["rootLight"]["card"], L, "a light class on <html> beats a dark system")
            self.assertEqual(errors, [])

    def test_a_dark_stage_is_a_night_stage_and_never_the_appearance_class(self):
        page, errors = self.open(1500)
        stage_ids = page.evaluate("BLOCKS.filter((b) => b.stage === 'dark').map((b) => b.id)")
        self.assertEqual(len(stage_ids), 2)
        for cid in stage_ids:
            page.evaluate("(id) => gotoId(id)", cid)
            self.assertEqual(page.evaluate("(id) => document.querySelector('.ixr[data-id=\"' + id + '\"]').closest('.st').className.split(' ').includes('night')", cid), True)
            self.assertEqual(page.evaluate("document.querySelectorAll('.st.dark').length"), 0)
        self.assertEqual(errors, [])

    def test_apply_theme_and_theme_vars_keep_their_signatures_and_know_the_dark(self):
        page, errors = self.open(1500)
        got = page.evaluate("""() => { const el = document.createElement('div'); document.body.appendChild(el); applyTheme(el, 'teal');
            return { lt: el.getAttribute('data-lt'), light: themeVars('teal'), dark: themeVars('teal', 'dark'), inline: el.getAttribute('style'), ids: THEMES.map((t) => t.id), setA: typeof window.setAppearance, isDark: typeof window.isDark } }""")
        self.assertEqual(got["lt"], "teal")
        self.assertIsNone(got["inline"], "applyTheme writes no inline colours (they would pin the light values over the dark ones)")
        for key in ("--p", "--pd", "--pt", "--pm", "--ga", "--gb", "--p-rgb", "--p-text", "--p-fg"):
            self.assertIn(key, got["light"])
            self.assertIn(key, got["dark"])
        tk = __import__("tokens")
        teal = {t["id"]: t for t in tk.theme_rows()}["teal"]
        self.assertEqual((got["light"]["--p"], got["dark"]["--p"], got["dark"]["--p-text"]), (teal["light"]["p"], teal["dark"]["p"], teal["dark"]["text"]))
        self.assertEqual((got["setA"], got["isDark"]), ("function", "function"))
        self.assertEqual(errors, [])

    @unittest.skipUnless(os.environ.get("LIB_REGRESSION_BASE"), "set LIB_REGRESSION_BASE to a capture of the light baseline to compare against it")
    def test_the_light_appearance_is_unchanged_against_the_baseline(self):
        """tools/visual_regression.py: every component, desktop and phone, picture by picture and element by element, within the thresholds. Takes about two minutes."""
        import visual_regression as vr

        out = self.tmp / "light-capture"
        summary = vr.capture(self.html, out, "light")
        for width, got in summary.items():
            self.assertEqual(got["errors"], [], width)
            self.assertEqual(got["cards"], EXPECTED_TOTAL, width)
        report = vr.compare(Path(os.environ["LIB_REGRESSION_BASE"]), out)
        self.assertEqual(report["missing"], [])
        allowed = {"1500/_bar", "390/_bar"} if os.environ.get("LIB_REGRESSION_TOOLBAR_CHANGED") else set()
        self.assertEqual([k for k, _ in report["bad_images"] if k not in allowed], [], "pictures over the thresholds")
        self.assertEqual([k for k, v in report["bad_styles"] if v.get("moved_n") or v.get("count") or v.get("missing")], [], "an element that moved or went missing")
        self.assertEqual([k for k, v in report["bad_styles"]], [], "a computed colour that changed by more than the tolerance")

    def test_a_one_file_build_opens_with_the_first_generation_templates_and_its_own_file(self):
        small = self.tmp / "small.html"
        builder.main(["--files", "blocks-ad-comm.js", "--out", str(small)])
        page, errors = self.open(1500, path=small)
        self.assertEqual(page.evaluate("BLOCKS.length"), 52 + 10)
        page.click('[data-dom="ad"]')
        page.wait_for_selector('.ixr[data-cid="AD-COMM-001"]')
        self.assertEqual(errors, [])


if __name__ == "__main__":
    started = time.time()
    try:
        unittest.main(exit=False)
    finally:
        print(f"{time.time() - started:.0f} s")
