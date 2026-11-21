"""stage_ramp.py: the ordered-progress colour ramp (visual-design.html 有序进度状态的色阶) is generated, pinned in themes.json, exported as tokens and audited on a rendered page."""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_contrast as cc  # noqa: E402
import export_tokens as et  # noqa: E402
import stage_ramp as sr  # noqa: E402

DATA = json.loads(sr.THEMES.read_text(encoding="utf-8"))
PAGE = (HERE.parent / "references" / "visual-design.html").read_text(encoding="utf-8")


def quiet(func, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = func(*args)
    return code, out.getvalue()


class PositionsTest(unittest.TestCase):
    def test_n_states_take_n_evenly_spaced_stops(self) -> None:
        self.assertEqual(sr.positions(1), [])
        self.assertEqual(sr.positions(2), [1, 6])
        self.assertEqual(sr.positions(3), [1, 4, 6])
        self.assertEqual(sr.positions(4), [1, 3, 4, 6])
        self.assertEqual(sr.positions(5), [1, 2, 4, 5, 6])
        self.assertEqual(sr.positions(6), [1, 2, 3, 4, 5, 6])

    def test_more_than_six_states_share_six_tiers_in_order(self) -> None:
        for n in range(7, 13):
            with self.subTest(n=n):
                t = sr.tiers(n)
                self.assertEqual(len(t), n)
                self.assertEqual(t, sorted(t))
                self.assertEqual(sorted(set(t)), [1, 2, 3, 4, 5, 6])
        with self.assertRaises(ValueError):
            sr.positions(7)

    def test_colours_follow_the_position_not_the_name(self) -> None:
        ramp = DATA["themes"]["b2b-graphite"]["stage"]["light"]
        five = [ramp[p - 1] for p in sr.positions(5)]
        self.assertEqual(len(set(five)), 5)
        self.assertEqual(five[0], ramp[0])
        self.assertEqual(five[-1], ramp[-1])


class ThemesTest(unittest.TestCase):
    def test_every_theme_carries_the_ramp_the_algorithm_makes(self) -> None:
        for theme_id in DATA["themes"]:
            with self.subTest(theme=theme_id):
                self.assertEqual(DATA["themes"][theme_id].get("stage"), sr.theme_ramp(theme_id, DATA))

    def test_every_theme_passes_every_rule_in_both_modes(self) -> None:
        for theme_id, theme in DATA["themes"].items():
            with self.subTest(theme=theme_id):
                failed = [(label, note) for label, ok, note in sr.theme_rules(theme_id, theme, DATA["shared"], DATA) if not ok]
                self.assertEqual(failed, [])

    def test_ramp_is_in_order_in_light_and_dark(self) -> None:
        for theme_id, theme in DATA["themes"].items():
            light = [sr.oklch(c) for c in theme["stage"]["light"]]
            dark = [sr.oklch(c) for c in theme["stage"]["dark"]]
            with self.subTest(theme=theme_id):
                self.assertTrue(all(b[0] <= a[0] + 0.006 for a, b in zip(light, light[1:])), "light: later stops are deeper")
                self.assertTrue(all(b[0] >= a[0] - 0.006 for a, b in zip(dark, dark[1:])), "dark: later stops are brighter")
                self.assertTrue(all(b[1] >= a[1] - 0.006 for a, b in zip(light, light[1:])), "light: chroma climbs")
                self.assertTrue(all(b[1] >= a[1] - 0.006 for a, b in zip(dark, dark[1:])), "dark: chroma climbs")
                self.assertLessEqual(max(c[1] for c in light + dark), sr.MAX_CHROMA + sr.CHROMA_TOLERANCE)

    def test_stage_is_not_a_status_colour(self) -> None:
        # the saturated end of the ramp keeps its distance from success, warning and danger text colours (visual-design.html 与语义状态色的边界)
        shared = DATA["shared"]
        for theme_id, theme in DATA["themes"].items():
            for mode, status in (("light", shared), ("dark", shared["dark"])):
                for hex_ in theme["stage"][mode][2:]:
                    hue = sr.oklch(hex_)[2]
                    for name in ("success", "warning", "danger", "price"):
                        gap = sr.circular_distance(hue, sr.oklch(status[name])[2])
                        with self.subTest(theme=theme_id, mode=mode, stop=hex_, status=name):
                            self.assertGreaterEqual(gap, 25)

    def test_check_contrast_runs_the_stage_rules(self) -> None:
        code, out = quiet(cc.main, [])
        self.assertEqual(code, 0, out[-600:])
        self.assertIn("stage light stage-1", out)
        self.assertIn("stage dark stage-6", out)

    def test_a_theme_without_a_stage_fails(self) -> None:
        theme = dict(DATA["themes"]["b2b-graphite"])
        theme.pop("stage")
        rules = sr.theme_rules("b2b-graphite", theme, DATA["shared"], DATA)
        self.assertFalse(rules[0][1])


class CheckTest(unittest.TestCase):
    GOOD = DATA["themes"]["b2b-graphite"]["stage"]["light"]

    def run_check(self, colours, bg="#FFFFFF", *flags):
        return quiet(sr.main, ["check", "--colors", ",".join(colours), "--bg", bg, *flags])

    def test_the_theme_ramp_passes(self) -> None:
        code, out = self.run_check(self.GOOD, "#FFFFFF,#FAFAFA", "--tint", "--cvd")
        self.assertEqual(code, 0, out)

    def test_same_hue_with_only_lightness_changed_is_too_close(self) -> None:
        # a one-hue ramp that only gets lighter and darker, four stops squeezed into the 4.5:1 band
        close = ["#5A6F7A", "#586D78", "#566B76", "#546974"]
        code, out = self.run_check(close)
        self.assertEqual(code, 1)
        self.assertIn("相邻色差", out)

    def test_reversed_order_fails_the_progression(self) -> None:
        code, out = self.run_check(list(reversed(self.GOOD)))
        self.assertEqual(code, 1)
        self.assertIn("彩度不递减", out)
        self.assertIn("明度不增", out)

    def test_a_pale_stop_fails_the_text_contrast(self) -> None:
        pale = list(self.GOOD)
        pale[0] = "#A9B8C0"
        code, out = self.run_check(pale)
        self.assertEqual(code, 1)
        self.assertIn("stage-1", out)
        self.assertIn("FAIL", out)

    def test_an_over_saturated_stop_fails_the_chroma_cap(self) -> None:
        loud = list(self.GOOD)
        loud[-1] = "#4B00C8"
        code, out = self.run_check(loud)
        self.assertEqual(code, 1)
        self.assertIn("彩度不超过", out)

    def test_a_rainbow_is_not_a_ramp(self) -> None:
        rainbow = ["#B3261E", "#A15C00", "#18794E", "#2F5F8A", "#6A3FA0"]
        code, out = self.run_check(rainbow)
        self.assertEqual(code, 1)

    def test_dark_mode_flips_the_lightness_direction(self) -> None:
        dark = DATA["themes"]["b2b-graphite"]["stage"]["dark"]
        grounds = ",".join(sr.grounds("b2b-graphite", DATA, "dark").values())
        self.assertEqual(self.run_check(dark, grounds, "--mode", "dark")[0], 0)
        self.assertEqual(self.run_check(dark, grounds, "--mode", "light")[0], 1)

    def test_make_prints_the_subset_and_json(self) -> None:
        code, out = quiet(sr.main, ["make", "--theme", "b2b-graphite", "--n", "3", "--json"])
        self.assertEqual(code, 0)
        doc = json.loads(out)
        self.assertEqual(doc["positions"], [1, 4, 6])
        self.assertEqual([x["color"] for x in doc["light"]], [self.GOOD[0], self.GOOD[3], self.GOOD[5]])
        self.assertEqual(len(doc["dark"]), 3)
        self.assertEqual(quiet(sr.main, ["make", "--theme", "nope"])[0], 2)

    def test_themes_command_reports_agreement(self) -> None:
        code, out = quiet(sr.main, ["themes", "--check"])
        self.assertEqual(code, 0)
        self.assertNotIn("不一致", out)


class TokensTest(unittest.TestCase):
    def test_every_theme_exports_the_stage_and_its_tints_in_both_modes(self) -> None:
        for theme_id, theme in DATA["themes"].items():
            doc = et.build(theme_id, DATA, surface='reference')
            with self.subTest(theme=theme_id):
                self.assertEqual(et.check_tokens(doc), [])
                for i in range(6):
                    tok = doc["color"]["stage"][str(i + 1)]
                    self.assertEqual(tok["$value"]["hex"].upper(), theme["stage"]["light"][i].upper())
                    self.assertEqual(tok["$extensions"]["mode"]["dark"]["hex"].upper(), theme["stage"]["dark"][i].upper())
                    tint = doc["color"]["stage-tint"][str(i + 1)]
                    self.assertEqual(tint["$value"]["hex"].upper(), sr.tint_of(theme["stage"]["light"][i], "light", DATA["shared"]["surface"]).upper())
                    self.assertIn("dark", tint["$extensions"]["mode"])

    def test_check_tokens_catches_a_stage_that_fails_contrast_or_order(self) -> None:
        doc = et.build('b2b-graphite', DATA, surface='reference')
        pale = json.loads(json.dumps(doc))
        pale["color"]["stage"]["1"]["$value"] = et.to_color("#B7C4CB")
        errors = et.check_tokens(pale)
        self.assertTrue(any("stage-1" in e and "light" in e for e in errors), errors)
        flipped = json.loads(json.dumps(doc))
        for i in range(1, 7):
            flipped["color"]["stage"][str(i)]["$extensions"]["mode"]["dark"] = et.to_color(DATA["themes"]["b2b-graphite"]["stage"]["dark"][6 - i])
        errors = et.check_tokens(flipped)
        self.assertTrue(any("dark" in e and "明度" in e for e in errors), errors)

    def test_light_only_export_carries_the_light_ramp_alone(self) -> None:
        doc = et.build("b2b-graphite", DATA, with_dark=False,surface='reference')
        self.assertNotIn("$extensions", doc["color"]["stage"]["1"])
        self.assertEqual(et.check_tokens(doc), [])


class AuditItemsTest(unittest.TestCase):
    RAMP = DATA["themes"]["b2b-graphite"]["stage"]["light"]

    def items(self, n=5, text="状态", colour=None, pos=None):
        want = sr.positions(n)
        out = []
        for p in range(1, n + 1):
            out.append({"set": "depth", "pos": p, "n": n, "color": (colour or {}).get(p, self.RAMP[want[p - 1] - 1]), "text": text, "label": f"[depth {p}]"})
        return out

    def test_a_clean_set_passes_with_and_without_tokens(self) -> None:
        self.assertEqual(sr.audit_items(self.items(), self.RAMP), [])
        self.assertEqual(sr.audit_items(self.items(), None), [])
        self.assertEqual(sr.audit_items([], self.RAMP), [])

    def test_missing_label_same_colour_and_reversed_order_are_reported(self) -> None:
        self.assertTrue(any("文字标签" in e for e in sr.audit_items(self.items(text=""), self.RAMP)))
        same = self.items(colour={2: self.RAMP[0]})
        self.assertTrue(any("颜色相同" in e for e in sr.audit_items(same, None)))
        swapped = self.items(colour={1: self.RAMP[5], 5: self.RAMP[0]})
        errors = sr.audit_items(swapped, None)
        self.assertTrue(any("彩度反而下降" in e or "明度走向" in e for e in errors), errors)

    def test_one_position_with_two_colours_is_reported(self) -> None:
        items = self.items() + [{"set": "depth", "pos": 2, "n": 5, "color": "#123456", "text": "状态", "label": "[depth 2 again]"}]
        self.assertTrue(any("同一取值同一颜色" in e for e in sr.audit_items(items, None)))

    def test_a_colour_that_is_not_the_stop_of_its_position_is_reported(self) -> None:
        wrong = self.items(colour={3: self.RAMP[2]})     # position 3 of 5 should take stop 4
        self.assertTrue(any("不是色阶令牌的对应一级" in e for e in sr.audit_items(wrong, self.RAMP)))

    def test_dark_scheme_wants_brighter_later_stops(self) -> None:
        dark = DATA["themes"]["b2b-graphite"]["stage"]["dark"]
        items = [{"set": "depth", "pos": p, "n": 5, "color": dark[sr.positions(5)[p - 1] - 1], "text": "状态", "label": f"[depth {p}]"} for p in range(1, 6)]
        self.assertEqual(sr.audit_items(items, dark, "dark"), [])
        self.assertNotEqual(sr.audit_items(items, None, "light"), [])


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
        run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "audit_rendered.py"), str(page), *args], capture_output=True, text=True, encoding="utf-8")
        return run.returncode, run.stdout


def stage_page(overrides: dict[str, str] | None = None, labels: bool = True, tokens: bool = True) -> str:
    ramp = DATA["themes"]["b2b-graphite"]["stage"]["light"]
    root = ":root{" + "".join(f"--stage-{i + 1}:{c};" for i, c in enumerate(ramp)) + "}" if tokens else ""
    names = ["初次建联", "面谈拜访", "二轮", "三轮", "后续跟进"]
    spans = []
    for pos, name in enumerate(names, 1):
        css = (overrides or {}).get(str(pos), f"color:var(--stage-{sr.positions(5)[pos - 1]})")
        if not labels:
            css += ";display:inline-block;width:8px;height:8px;background:currentColor"      # a bare colour dot with no text beside it
        spans.append(f"<li><span data-stage-set='depth' data-stage='{pos}' data-stage-n='5' style='{css}'>{name if labels else ''}</span></li>")
    return ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>t</title><style>body{font:400 14px/22px sans-serif;color:#1d2129;background:#fff}"
            f"{root}li{{list-style:none}}</style><h1 style='font-size:22px;font-weight:700'>客户</h1><ul>{''.join(spans)}</ul>")


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class RenderedAuditTest(unittest.TestCase):
    def test_a_ramp_page_passes(self) -> None:
        code, out = audit(stage_page())
        self.assertEqual((code, out.strip()), (0, "audit: ok"))

    def test_a_page_without_stage_attributes_is_not_checked_for_stages(self) -> None:
        plain = stage_page().replace("data-stage-set", "data-x").replace("data-stage=", "data-y=")
        self.assertEqual(audit(plain)[0], 0)

    def test_two_positions_with_one_colour_fail(self) -> None:
        code, out = audit(stage_page({"2": "color:var(--stage-1)"}))
        self.assertEqual(code, 1)
        self.assertIn("颜色相同", out)

    def test_a_colour_off_the_ramp_fails(self) -> None:
        code, out = audit(stage_page({"3": "color:#B3261E"}))
        self.assertEqual(code, 1)
        self.assertIn("不是色阶令牌的对应一级", out)

    def test_a_state_without_text_fails(self) -> None:
        code, out = audit(stage_page(labels=False))
        self.assertEqual(code, 1)
        self.assertIn("文字标签", out)

    def test_dark_scheme_uses_the_dark_ramp(self) -> None:
        dark = DATA["themes"]["b2b-graphite"]["stage"]["dark"]
        page = stage_page().replace("background:#fff", "background:#18181B;color:#F5EFEA")
        page = page.replace(":root{", ":root{" + "".join(f"--stage-{i + 1}:{c};" for i, c in enumerate(dark)) + "}:root.x{", 1)
        code, out = audit(page, "--scheme", "dark")
        self.assertEqual((code, out.strip()), (0, "audit: ok"), out)


WALK_SWITCH = """def walk(page, scan):
    out = [('light', scan())]
    page.evaluate("document.documentElement.classList.add('dk')")
    page.wait_for_timeout(150)
    return out + [('after the switch to dark', scan())]
"""


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge")
class WalkThatSwitchesTheThemeTest(unittest.TestCase):
    """A walk may switch the page to its dark theme after it was opened in the light scheme: the ramp's direction is judged on what the scan really shows."""

    def test_a_scan_after_a_switch_to_dark_is_judged_on_the_dark_ramp(self) -> None:
        light = DATA["themes"]["b2b-graphite"]["stage"]["light"]
        dark = DATA["themes"]["b2b-graphite"]["stage"]["dark"]
        page = stage_page().replace(":root{", ":root{" + "".join(f"--stage-{i + 1}:{c};" for i, c in enumerate(light)) + "}:root.x{", 1)
        page = page.replace("</style>", "html.dk{" + "".join(f"--stage-{i + 1}:{c};" for i, c in enumerate(dark)) + "}html.dk body{background:#18181B;color:#F5EFEA}</style>", 1)
        with tempfile.TemporaryDirectory() as tmp:
            html, walk = Path(tmp) / "page.html", Path(tmp) / "walk.py"
            html.write_text(page, encoding="utf-8")
            walk.write_text(WALK_SWITCH, encoding="utf-8")
            run = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "audit_rendered.py"), str(html), "--walk", str(walk)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual((run.returncode, run.stdout.strip()), (0, "audit: ok"), run.stdout)


class RulePageTest(unittest.TestCase):
    def test_the_rule_page_states_the_numbers_the_script_uses(self) -> None:
        self.assertIn("有序进度状态的色阶", PAGE)
        for needle in (f"{sr.MIN_DE:g}", f"{sr.MAX_CHROMA:g}", f"{sr.ARC:g}", "stage_ramp.py", "data-stage-set", "--stage-1", "WCAG 1.4.1"):
            self.assertIn(needle, PAGE, needle)


if __name__ == "__main__":
    unittest.main()
