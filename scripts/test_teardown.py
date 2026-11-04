import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import teardown  # noqa: E402


def browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch() if os.environ.get("LUZ_AUDIT_CHANNEL") == "chromium" else pw.chromium.launch(channel=os.environ.get("LUZ_AUDIT_CHANNEL", "msedge"))
            browser.close()
        return True
    except Exception:
        return False


# A tidy page: four font sizes, 8-multiple spacing, two radii, one shadow with a downward light, dark text on light surfaces, big targets.
NEAT = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>neat</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font:400 16px/24px "Microsoft YaHei",sans-serif;color:#1d2129;background:#f7f8fa;padding:24px}
h1{font-size:28px;line-height:40px;font-weight:600;margin-bottom:16px}
.card{background:#fff;border-radius:16px;padding:24px;margin-bottom:16px;box-shadow:0 4px 16px rgba(0,0,0,.08)}
h2{font-size:20px;line-height:32px;font-weight:600;margin-bottom:8px}
p{margin-bottom:16px}
.tip{background:#e8f0fe;border-radius:8px;padding:16px;margin-bottom:16px}
small{display:block;font-size:12px;line-height:16px;color:#4e5969;margin-bottom:16px}
button{display:block;width:100%;height:48px;border:0;border-radius:8px;background:#1d4ed8;color:#fff;font:600 16px/24px "Microsoft YaHei",sans-serif}
</style>
<h1>周末手作花艺课</h1>
<div class="card"><h2>入门体验课</h2><p>两小时学会三种基础花型，材料全部由门店提供，适合第一次接触花艺的朋友。老师会先示范，再陪你一起完成。</p><div class="tip">材料费已含在课程费用里，不需要自带任何工具，穿舒适的衣服来就好。</div><small>每周六 14:00 开课，限 8 人</small><button>立即预约</button></div>
<div class="card"><h2>进阶工作坊</h2><p>围绕季节花材做一件完整作品，老师全程一对一指导，作品可以带回家。适合已经上过入门课的同学。</p><div class="tip">完成作品后可以现场打包带走，也可以寄存在门店，下次来课时再取。</div><small>每周日 10:00 开课，限 6 人</small><button>立即预约</button></div>
<div class="card"><h2>企业团建</h2><p>十人以上可以预约专场，场地、花材和讲师都由我们安排，课程内容可以按主题定制。</p><div class="tip">人数和场地可以按需要调整，具体时间由双方商量确定下来。</div><small>提前三天预约</small><button>咨询团建</button></div>
"""


def messy_page() -> str:
    """The same kind of content with ten font sizes, seven radii, loose spacing, grey text, mixed shadows, small targets and an unguarded transition."""
    sizes = [11, 12, 13, 14, 15, 16, 18, 20, 24, 30]
    radii = ["2px", "3px", "5px", "9px", "13px", "22px", "999px"]
    gaps = [13, 7, 22, 9, 17, 11, 19, 14, 6, 21]
    weights = [300, 400, 500, 600, 700, 800, 900, 400, 500, 600]
    colors = ["#999", "#bbb", "#e91e63", "#4caf50", "#ff9800", "#2196f3", "#9c27b0", "#795548", "#aaa", "#ccc"]
    shadows = ["0 -4px 12px rgba(0,0,0,.3)", "0 6px 20px rgba(233,30,99,.4)", "0 0 8px #2196f3", "0 2px 3px rgba(0,0,0,.5)", "0 12px 40px rgba(0,0,0,.25)", "4px 4px 0 #000"]
    boxes = []
    for i in range(10):
        boxes.append(
            f"<div style=\"margin:{gaps[i]}px {gaps[(i + 3) % 10]}px;padding:{gaps[(i + 5) % 10]}px {gaps[(i + 7) % 10]}px;border-radius:{radii[i % 7]};"
            f"box-shadow:{shadows[i % 6]};background:{'#fff' if i % 2 else '#fafafa'};transition:all .3s ease-in-out\">"
            f"<span style=\"font-size:{sizes[i]}px;font-weight:{weights[i]};color:{colors[i]};font-family:{['Georgia', 'Arial', 'Courier New'][i % 3]},serif\">第 {i + 1} 段随手写的文字内容在这里</span></div>"
        )
    buttons = "".join(f"<button style=\"height:{26 + i}px;margin:{gaps[i]}px;border-radius:{radii[(i + 2) % 7]};border:1px solid #ddd;background:#fff;color:#bbb\">点我</button>" for i in range(5))
    return f"<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>messy</title><body style='margin:0;font-family:serif;background:#fff'>{''.join(boxes)}{buttons}</body>"


class PureFunctionTests(unittest.TestCase):
    def test_wcag_contrast_and_oklab(self):
        self.assertAlmostEqual(teardown.contrast((0, 0, 0), (255, 255, 255)), 21.0, places=2)
        self.assertAlmostEqual(teardown.contrast((119, 119, 119), (255, 255, 255)), 4.48, places=1)    # #777 on white is just under AA
        L, C, _ = teardown.oklch((255, 255, 255))
        self.assertAlmostEqual(L, 1.0, places=2)
        self.assertLess(C, 0.001)
        self.assertGreater(teardown.oklch((37, 99, 235))[1], 0.15)                                      # a saturated blue is far from neutral

    def test_colour_clusters_merge_near_colours_and_keep_neutrals_apart(self):
        cl = teardown.cluster_colors({(29, 33, 41): 100, (30, 33, 41): 50, (255, 255, 255): 80, (247, 248, 250): 40, (37, 99, 235): 30})
        self.assertEqual([teardown.hex_of(c["rgb"]) for c in cl][:2], ["#1d2129", "#ffffff"])
        self.assertEqual(len(cl), 4)                                       # ink, white, off-white (a card on a canvas stays two) and blue
        self.assertEqual([c["neutral"] for c in cl].count(False), 1)
        many = {(i * 20 % 256, (i * 70) % 256, (i * 130) % 256): 10 + i for i in range(40)}
        cl = teardown.cluster_colors(many)
        self.assertLessEqual(sum(1 for c in cl if not c["neutral"]), teardown.MAX_CHROMATIC)

    def test_grid_detection(self):
        eight = teardown.pick_grid(Counter({8: 10, 16: 8, 24: 5, 32: 2, 1: 5}))
        self.assertEqual((eight["base_unit"], eight["off_grid_share"]), (8, 0.0))
        four = teardown.pick_grid(Counter({4: 10, 12: 12, 16: 5, 20: 2}))
        self.assertEqual(four["base_unit"], 4)
        loose = teardown.pick_grid(Counter({13: 4, 7: 3, 22: 2, 9: 3, 17: 2, 11: 1, 8: 1}))
        self.assertIsNone(loose["base_unit"])
        self.assertGreater(loose["off_grid_share"], 0.8)

    def test_motion_values_are_read_from_lists_and_shorthand_longhands(self):
        m = teardown.analyse_motion({"td": ["0.2s", "200ms, 0.3s"], "tf": ["ease", "cubic-bezier(0.4, 0, 0.2, 1), ease"], "tp": ["opacity", "transform, opacity"], "ad": ["1s"], "af": ["linear"],
                                     "reduced": True, "unreadable": [], "rules": 3, "keyframes": 1, "running": 0})
        self.assertEqual(m["transition_durations_ms"][0], {"value": 200, "count": 2})
        self.assertEqual({d["value"] for d in m["transition_durations_ms"]}, {200, 300})
        self.assertEqual(m["transition_timing"][0], {"value": "ease", "count": 2})
        self.assertIn("cubic-bezier(0.4, 0, 0.2, 1)", [t["value"] for t in m["transition_timing"]])
        self.assertTrue(m["reduced_motion_branch"])

    def test_font_size_clusters_merge_below_one_pixel_and_name_the_body(self):
        texts = [{"fs": s, "fw": 400, "lh": s * 1.5, "fam": "sans-serif", "n": n, "col": None, "bg": (255, 255, 255), "unk": False, "a": 1, "l": 0, "r": 1, "t": 0, "b": 1, "ax": 0, "al": "l", "first": True, "dis": False, "s": "x"}
                 for s, n in ((13.6, 20), (14, 100), (15, 5), (18, 30), (30, 4))]
        ty = teardown.analyse_type(texts)
        self.assertEqual([s["px"] for s in ty["scale"]], [14, 15, 18, 30])      # 13.6 joins 14 (under 1 px apart); 15 stays its own step
        self.assertEqual(ty["body_px"], 14)


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge (or LUZ_AUDIT_CHANNEL=chromium)")
class TeardownPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.neat_file = Path(cls.tmp.name) / "neat.html"
        cls.messy_file = Path(cls.tmp.name) / "messy.html"
        cls.neat_file.write_text(NEAT, encoding="utf-8")
        cls.messy_file.write_text(messy_page(), encoding="utf-8")
        cls.neat = teardown.teardown(str(cls.neat_file), with_lint=True)
        cls.messy = teardown.teardown(str(cls.messy_file), with_lint=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_base_unit(self):
        self.assertEqual(self.neat["space"]["base_unit"], 8)
        self.assertEqual(self.neat["space"]["off_grid_share"], 0.0)
        self.assertIsNone(self.messy["space"]["base_unit"])
        self.assertGreater(self.messy["space"]["off_grid_share"], 0.5)

    def test_effective_type_scale(self):
        self.assertEqual([s["px"] for s in self.neat["type"]["scale"]], [12, 16, 20, 28])
        self.assertEqual(self.neat["type"]["body_px"], 16)
        self.assertEqual(len(self.messy["type"]["scale"]), 10)
        self.assertEqual(set(self.neat["type"]["weights"]) <= {"400", "600"}, True)

    def test_radius_values(self):
        self.assertEqual(self.neat["shape"]["radius_values"], [8, 16])
        self.assertEqual(self.neat["shape"]["radius_distinct"], 2)
        self.assertEqual(self.messy["shape"]["radius_distinct"], 7)
        self.assertIn("pill", self.messy["shape"]["radius_values"])

    def test_depth_and_colour(self):
        self.assertEqual((self.neat["depth"]["levels"], self.neat["depth"]["direction"]), (1, "down"))
        self.assertEqual(self.messy["depth"]["direction"], "mixed")
        self.assertGreater(self.neat["color"]["contrast"]["median"], 7)
        self.assertEqual(self.neat["color"]["primary"]["hex"], "#1d4ed8")
        self.assertLess(self.messy["color"]["contrast"]["min"], 4.5)

    def test_layout_and_touch(self):
        lay = self.neat["layout"]
        self.assertEqual(lay["touch"]["small"], 0)
        self.assertLessEqual(lay["align"]["strong_lines"], 3)     # the card text line and the centred button label
        self.assertTrue(0.25 <= lay["whitespace"]["ratio"] <= 0.65, lay["whitespace"])
        self.assertGreater(self.messy["layout"]["touch"]["small_share"], 0.2)

    def test_lint_flags_the_messy_page_and_leaves_the_tidy_one_alone(self):
        self.assertLessEqual(self.neat["lint"]["count"], 1, [i["metric"] for i in self.neat["lint"]["items"]])
        self.assertGreaterEqual(self.messy["lint"]["count"], 4)
        metrics = {i["metric"] for i in self.messy["lint"]["items"]}
        for needle in ("有效字阶", "圆角种类", "离网格间距比例", "阴影方向", "reduced-motion 分支"):
            self.assertIn(needle, metrics)
        for i in self.messy["lint"]["items"]:
            self.assertTrue(all(i[k] for k in ("metric", "value", "range", "why", "fix")))

    def test_token_draft(self):
        td = self.neat["token_draft"]
        self.assertEqual([t["px"] for t in td["type_scale"]], [12, 16, 20, 28])
        self.assertEqual([t["name"] for t in td["type_scale"]][1], "body")
        self.assertEqual(td["radius"], {"sm": 8, "md": 16})
        self.assertEqual(td["spacing"]["base"], 8)
        self.assertEqual(td["palette"]["primary"], "#1d4ed8")
        self.assertEqual(td["palette"]["text"]["primary"], "#1d2129")
        self.assertEqual(len(self.messy["token_draft"]["type_scale"]), 8)

    def test_meta(self):
        meta = self.neat["meta"]
        for key in ("url", "width", "height", "scheme", "date", "browser"):
            self.assertTrue(meta[key])
        self.assertEqual((meta["width"], meta["height"], meta["scheme"]), (390, 844, "light"))

    def test_dark_scheme_follows_prefers_color_scheme(self):
        page = self.tmp.name + "/dark.html"
        Path(page).write_text("<!doctype html><meta charset='utf-8'><style>body{margin:0;background:#fff;color:#111}@media (prefers-color-scheme:dark){body{background:#101418;color:#e6e8eb}}</style><p style='padding:24px'>深色测试文字</p>", encoding="utf-8")
        rep = teardown.teardown(page, scheme="dark")
        self.assertEqual(rep["meta"]["scheme"], "dark")
        self.assertEqual(rep["color"]["page_background"], "#101418")
        self.assertEqual(rep["token_draft"]["palette"]["text"]["primary"], "#e6e8eb")

    def test_a_page_without_text_still_gives_a_report(self):
        page = Path(self.tmp.name) / "blank.html"
        page.write_text("<!doctype html><meta charset='utf-8'><body style='margin:0'><div style='width:100px;height:100px;background:#2563eb;border-radius:12px'></div>", encoding="utf-8")
        rep = teardown.teardown(str(page), with_lint=True)
        self.assertEqual(rep["type"]["scale"], [])
        self.assertEqual(rep["token_draft"]["type_scale"], [])
        self.assertEqual(rep["shape"]["radius_values"], [12])
        self.assertIn("审美体检", teardown.render_md(rep))

    def test_motion_in_a_linked_style_sheet_and_in_style_attributes_is_read(self):
        (Path(self.tmp.name) / "m.css").write_text(".a{transition:opacity .2s cubic-bezier(.4,0,.2,1)}.b{animation:spin 1.2s linear infinite}@keyframes spin{to{opacity:0}}@media (prefers-reduced-motion:reduce){.a,.b{transition:none;animation:none}}", encoding="utf-8")
        page = Path(self.tmp.name) / "motion.html"
        page.write_text("<!doctype html><meta charset='utf-8'><link rel='stylesheet' href='m.css'><style>.c{transition:transform 350ms ease-out}</style><p class='a'>甲</p><p class='b'>乙</p><p style='transition:color .1s ease-in'>丙</p>", encoding="utf-8")
        mo = teardown.teardown(str(page))["motion"]
        self.assertEqual({d["value"] for d in mo["transition_durations_ms"]}, {200, 350, 100})
        self.assertEqual([d["value"] for d in mo["animation_durations_ms"]], [1200])
        self.assertTrue(mo["reduced_motion_branch"])
        self.assertEqual((mo["unreadable_sheets"], mo["keyframes"]), ([], 1))

    def test_an_app_shell_that_scrolls_inside_is_measured_whole(self):
        rows = "".join(f"<p style='margin:0;padding:16px'>第 {i} 行内容 {i}</p>" for i in range(60))
        page = self.tmp.name + "/shell.html"
        Path(page).write_text(f"<!doctype html><meta charset='utf-8'><body style='margin:0;height:100vh'><div id='scroller' style='position:absolute;inset:0;overflow-y:auto'>{rows}</div>", encoding="utf-8")
        rep = teardown.teardown(page)
        self.assertEqual(rep["meta"]["expanded_scroller"]["tag"], "div")
        self.assertGreater(rep["meta"]["measured_height"], 2000)
        self.assertGreater(rep["layout"]["density"]["chars"], 400)
        flat = teardown.teardown(page, expand=False)
        self.assertLess(flat["layout"]["density"]["chars"], rep["layout"]["density"]["chars"])


@unittest.skipUnless(browser_available(), "needs playwright and Microsoft Edge (or LUZ_AUDIT_CHANNEL=chromium)")
class TeardownCommandTests(unittest.TestCase):
    def run_cli(self, *args, env=None):
        return subprocess.run([sys.executable, "-X", "utf8", str(HERE / "teardown.py"), *args], capture_output=True, text=True, encoding="utf-8", env={**os.environ, **(env or {})})

    def test_out_md_shots_and_lint_leave_the_exit_code_at_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "messy.html"
            page.write_text(messy_page(), encoding="utf-8")
            out, md, shots = Path(tmp) / "t.json", Path(tmp) / "r.md", Path(tmp) / "shots"
            run = self.run_cli(str(page), "--lint", "--out", str(out), "--md", str(md), "--shots", str(shots))
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            for key in ("meta", "type", "color", "shape", "depth", "space", "layout", "motion", "token_draft", "lint"):
                self.assertIn(key, data)
            for key in ("type_scale", "palette", "radius", "shadow", "spacing"):
                self.assertIn(key, data["token_draft"])
            self.assertLessEqual(len(data["token_draft"]["type_scale"]), 8)
            self.assertIn("条提示", run.stdout)
            self.assertIn("为什么", run.stdout)
            text = md.read_text(encoding="utf-8")
            self.assertIn("审美体检", text)
            self.assertLess(len(text.splitlines()), 90)                                    # one screen of tables, not a dump
            self.assertTrue((shots / "first-screen.png").stat().st_size > 1000)
            self.assertTrue((shots / "full-page.png").stat().st_size > 1000)

    def test_without_out_the_json_goes_to_stdout_and_the_hints_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "neat.html"
            page.write_text(NEAT, encoding="utf-8")
            run = self.run_cli(str(page), "--width", "390", "--height", "844", "--scheme", "light")
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["meta"]["scheme"], "light")
            self.assertNotIn("lint", json.loads(run.stdout))

    def test_the_browser_canvas_replaces_pillow_when_it_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "neat.html"
            page.write_text(NEAT, encoding="utf-8")
            with_pil = self.run_cli(str(page))
            without = self.run_cli(str(page), env={"LUZ_TEARDOWN_NO_PIL": "1"})
            self.assertEqual((with_pil.returncode, without.returncode), (0, 0), without.stderr)
            a = json.loads(with_pil.stdout)["layout"]["whitespace"]["ratio"]
            b = json.loads(without.stdout)["layout"]["whitespace"]["ratio"]
            self.assertLess(abs(a - b), 0.08, (a, b))

    def test_a_missing_page_is_an_error_not_a_crash(self):
        run = self.run_cli("http://127.0.0.1:1/none.html")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("ERROR", run.stderr)


if __name__ == "__main__":
    unittest.main()
