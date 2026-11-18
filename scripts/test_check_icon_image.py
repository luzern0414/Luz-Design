"""check_icon_image.py：生成图标的饱和度检查。图像都由 Pillow 现场生成，不依赖任何外部文件。

    py -X utf8 scripts/test_check_icon_image.py
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_icon_image as cii  # noqa: E402

THEMES = json.loads((HERE.parent / "references" / "themes.json").read_text(encoding="utf-8"))["themes"]

# 粉彩图标的三个颜色：浅底块、同色相的图形面、同色相的线稿
BASE, FACE, LINE = (254, 233, 221, 255), (255, 187, 150, 255), (214, 130, 96, 255)
# 深色版的两组颜色：都低于绝对阈值；一组比浅色版更饱和，一组更柔和
# 深色版按彩度 C（V x S）度量：LOUDER 的均值 S 超 0.45（按 S 度量会被拦），按 C 度量过绝对上限，但 P90 的 C 比浅色版（0.412）高出一截
DARK_LOUDER = ((100, 60, 50, 255), (225, 130, 90, 255), (255, 160, 120, 255))
DARK_SOFTER = ((52, 46, 44, 255), (120, 100, 92, 255), (200, 170, 150, 255))


def icon(base=BASE, face=FACE, line=LINE, size=96, background=None) -> Image.Image:
    """透明底的色块图标：圆角底块、一个图形面、一条线稿。background 给出时铺一层不透明底。"""
    img = Image.new("RGBA", (size, size), background or (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, size - 7, size - 7), radius=14, fill=base)
    d.ellipse((size * 0.28, size * 0.28, size * 0.72, size * 0.72), fill=face)
    d.line((size * 0.3, size * 0.5, size * 0.7, size * 0.5), fill=line, width=3)
    return img


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = cii.main(argv)
        except SystemExit as e:  # argparse 报错
            code = int(e.code or 0)
    return code, out.getvalue(), err.getvalue()


class MetricsTest(unittest.TestCase):
    def test_hsv_saturation_is_the_picker_value(self) -> None:
        self.assertAlmostEqual(cii.hsv_of((255, 0, 0))[1], 1.0)
        self.assertAlmostEqual(cii.hsv_of((255, 128, 128))[1], 0.498, places=2)
        self.assertAlmostEqual(cii.hsv_of((128, 128, 128))[1], 0.0)

    def test_pastel_icon_has_low_metrics(self) -> None:
        m = cii.analyze_image(icon())
        self.assertLess(m.mean, 0.45)
        self.assertLess(m.p90, 0.65)
        self.assertEqual(m.hot_share, 0.0)
        self.assertEqual(len(m.hues), 1)

    def test_loud_icon_has_high_metrics(self) -> None:
        m = cii.analyze_image(icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)))
        self.assertGreater(m.mean, 0.9)
        self.assertGreater(m.hot_share, 0.9)

    def test_near_white_and_near_black_pixels_are_not_counted(self) -> None:
        plain = cii.analyze_image(icon())
        for background in ((255, 255, 255, 255), (250, 248, 246, 255), (10, 10, 10, 255), (30, 20, 20, 255)):
            m = cii.analyze_image(icon(background=background))
            self.assertAlmostEqual(m.mean, plain.mean, places=9, msg=background)
            self.assertAlmostEqual(m.p90, plain.p90, places=9, msg=background)
            self.assertEqual(m.counted, plain.counted, background)

    def test_near_white_with_visible_tint_is_counted(self) -> None:
        # S 为 0.08 的浅粉底算数：近白只指 V 不低于 0.97 且 S 不高于 0.05
        m = cii.analyze_image(icon(background=(255, 235, 235, 255)))
        self.assertGreater(m.counted, cii.analyze_image(icon()).counted)

    def test_transparent_pixels_are_not_counted(self) -> None:
        img = icon()
        ImageDraw.Draw(img).rectangle((0, 0, 20, 20), fill=(255, 0, 0, 0))     # 全透明的纯红
        ImageDraw.Draw(img).rectangle((70, 0, 90, 5), fill=(255, 0, 0, 100))   # 透明度 100，低于 128
        m = cii.analyze_image(img)
        plain = cii.analyze_image(icon())
        self.assertAlmostEqual(m.mean, plain.mean, places=2)
        self.assertEqual(m.hot_share, 0.0)
        opaque = icon()
        ImageDraw.Draw(opaque).rectangle((0, 0, 20, 20), fill=(255, 0, 0, 255))
        self.assertGreater(cii.analyze_image(opaque).hot_share, 0.0)

    def test_fully_neutral_images_have_nothing_to_count(self) -> None:
        for img in (Image.new("RGBA", (32, 32), (0, 0, 0, 0)), Image.new("RGB", (32, 32), (255, 255, 255)), Image.new("RGB", (32, 32), (8, 8, 8))):
            m = cii.analyze_image(img)
            self.assertEqual(m.counted, 0)
            self.assertEqual(m.mean, 0)

    def test_hue_families_merge_neighbours_but_not_chains(self) -> None:
        def swatches(hues: list[float], s=0.5, v=0.9) -> Image.Image:
            import colorsys
            img = Image.new("RGB", (30 * len(hues), 30))
            d = ImageDraw.Draw(img)
            for i, h in enumerate(hues):
                rgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h / 360, s, v))
                d.rectangle((30 * i, 0, 30 * i + 29, 29), fill=rgb)
            return img
        self.assertEqual(len(cii.analyze_image(swatches([25, 45])).hues), 1)            # 橙与金是邻近色
        self.assertEqual(len(cii.analyze_image(swatches([25, 200])).hues), 2)
        self.assertEqual(len(cii.analyze_image(swatches([0, 120, 240])).hues), 3)
        self.assertGreater(len(cii.analyze_image(swatches(list(range(0, 360, 20)))).hues), 3)   # 彩虹不会并成一个

    def test_small_hue_specks_do_not_count(self) -> None:
        img = Image.new("RGB", (100, 100), (255, 187, 150))
        ImageDraw.Draw(img).rectangle((0, 0, 9, 9), fill=(120, 190, 255))   # 约 1% 的蓝点
        self.assertEqual(len(cii.analyze_image(img).hues), 1)

    @unittest.skipIf(cii.np is None, "没有 numpy")
    def test_numpy_and_pure_python_paths_agree(self) -> None:
        for img in (icon(), icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)), icon(background=(255, 255, 255, 255))):
            a, b = cii.analyze_image(img, use_numpy=True), cii.analyze_image(img, use_numpy=False)
            self.assertAlmostEqual(a.mean, b.mean, places=9)
            self.assertAlmostEqual(a.p90, b.p90, places=9)
            self.assertAlmostEqual(a.hot_share, b.hot_share, places=9)
            self.assertEqual(a.hues, b.hues)
            self.assertEqual(a.counted, b.counted)

    def test_works_without_numpy(self) -> None:
        saved = cii.np
        cii.np = None
        try:
            m = cii.analyze_image(icon())
            self.assertLess(m.mean, 0.45)
            code, out, _ = run([str(HERE / "no-such.png"), "--no-numpy"])
            self.assertEqual(code, 2)
        finally:
            cii.np = saved

    def test_large_images_are_reduced_without_new_colours(self) -> None:
        big = icon(size=1200)
        small = icon(size=96)
        a, b = cii.analyze_image(big), cii.analyze_image(small)
        self.assertLess(abs(a.mean - b.mean), 0.03)
        self.assertEqual(len(a.hues), len(b.hues))


class CommandTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def save(self, name: str, img: Image.Image) -> Path:
        path = self.dir / name
        img.save(path)
        return path

    def test_no_numpy_flag_gives_the_same_verdict(self) -> None:
        path = self.save("p.png", icon())
        bad = self.save("b.png", icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)))
        self.assertEqual(run([str(path), "--no-numpy"])[0], 0)
        self.assertEqual(run([str(bad), "--no-numpy"])[0], 1)
        a = json.loads(run([str(bad), "--json"])[1].rsplit("check icon image", 1)[0])
        b = json.loads(run([str(bad), "--json", "--no-numpy"])[1].rsplit("check icon image", 1)[0])
        self.assertEqual(a[0]["mean"], b[0]["mean"])
        self.assertEqual(a[0]["p90"], b[0]["p90"])

    def test_pastel_icon_passes_in_every_format(self) -> None:
        for name in ("a.png", "a.webp"):
            code, out, _ = run([str(self.save(name, icon()))])
            self.assertEqual(code, 0, out)
            self.assertIn("check icon image: ok", out)
        jpg = self.dir / "a.jpg"
        icon(background=(255, 255, 255, 255)).convert("RGB").save(jpg, quality=95)
        code, out, _ = run([str(jpg)])
        self.assertEqual(code, 0, out)

    def test_loud_icon_fails_and_names_the_exceeded_limits(self) -> None:
        path = self.save("loud.png", icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)))
        code, out, _ = run([str(path)])
        self.assertEqual(code, 1)
        for flag in ("--max-mean", "--p90", "--hot-share"):
            self.assertIn(flag, out)
        self.assertNotIn("check icon image: ok", out)
        self.assertIn("均值S", out)       # 失败时仍然打印指标，便于校准

    def test_only_the_exceeded_limit_is_named(self) -> None:
        # 三个色相各占三分之一，每个都不艳：只有“色相个数”超限
        import colorsys
        img = Image.new("RGB", (90, 30))
        d = ImageDraw.Draw(img)
        for i, h in enumerate((0, 120, 240)):
            rgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h / 360, 0.4, 0.9))
            d.rectangle((30 * i, 0, 30 * i + 29, 29), fill=rgb)
        code, out, _ = run([str(self.save("three.png", img))])
        self.assertEqual(code, 1)
        self.assertIn("--max-hues", out)
        for flag in ("--max-mean", "--p90", "--hot-share"):
            self.assertNotIn(flag, out)

    def test_limits_can_be_overridden(self) -> None:
        path = self.save("loud.png", icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)))
        code, out, _ = run([str(path), "--max-mean", "1", "--p90", "1", "--hot-share", "100%", "--max-hues", "9"])
        self.assertEqual(code, 0, out)
        # 只放开一项，其余照旧
        code, out, _ = run([str(path), "--max-mean", "1"])
        self.assertEqual(code, 1)
        self.assertNotIn("（--max-mean）", out)
        self.assertIn("--p90", out)

    def test_hot_share_accepts_fraction_and_percent(self) -> None:
        self.assertAlmostEqual(cii.parse_share("3%"), 0.03)
        self.assertAlmostEqual(cii.parse_share("0.03"), 0.03)
        with self.assertRaises(Exception):
            cii.parse_share("5")

    def test_tighter_limit_makes_a_passing_icon_fail(self) -> None:
        path = self.save("p.png", icon())
        self.assertEqual(run([str(path)])[0], 0)
        code, out, _ = run([str(path), "--max-mean", "0.05"])
        self.assertEqual(code, 1)
        self.assertIn("--max-mean", out)

    def test_directory_batch(self) -> None:
        self.save("good.png", icon())
        self.save("bad.png", icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)))
        code, out, _ = run([str(self.dir)])
        self.assertEqual(code, 1)
        self.assertIn("good.png", out)
        self.assertIn("bad.png", out)
        self.assertIn("1 of 2", out)
        code, out, _ = run([str(self.dir), "--quiet"])
        self.assertNotIn("good.png", out)
        self.assertIn("bad.png", out)
        (self.dir / "bad.png").unlink()
        code, out, _ = run([str(self.dir)])
        self.assertEqual(code, 0)
        self.assertIn("check icon image: ok", out)

    def test_directory_recursion(self) -> None:
        sub = self.dir / "sub"
        sub.mkdir()
        icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)).save(sub / "deep.png")
        self.save("top.png", icon())
        self.assertEqual(run([str(self.dir)])[0], 0)
        self.assertEqual(run([str(self.dir), "-r"])[0], 1)

    def test_json_output(self) -> None:
        path = self.save("p.png", icon())
        code, out, _ = run([str(path), "--json"])
        data = json.loads(out.rsplit("check icon image", 1)[0])
        self.assertEqual(code, 0)
        self.assertTrue(data[0]["ok"])
        self.assertEqual(set(data[0]) >= {"mean", "p90", "hot_share", "hues", "counted"}, True)

    # ------------------------------------------------ 深色版

    def test_dark_version_more_saturated_than_light_is_flagged(self) -> None:
        self.save("home.png", icon())
        # 深色版仍低于绝对阈值，但比浅色版更饱和
        self.save("home-dark.png", icon(*DARK_LOUDER))
        code, out, _ = run([str(self.dir / "home-dark.png")])
        self.assertEqual(code, 1, out)
        self.assertIn("深色版比浅色版更饱和", out)
        self.assertIn("对照浅色版", out)
        self.assertNotIn("（--max-mean）", out)         # 只因为比浅色版更艳，没有超绝对上限

    def test_dark_versions_are_measured_by_chroma_not_saturation(self) -> None:
        # 深色底色的 S 天生偏高：同一张图按 S 度量超 0.45，按深色版的彩度 C 度量就过了
        path = self.save("night.png", icon(*DARK_LOUDER))
        code, out, _ = run([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("（--max-mean）", out)
        code, out, _ = run([str(path), "--dark"])
        self.assertEqual(code, 0, out)
        self.assertIn("彩度", out)
        self.assertIn("没有找到对应的浅色版", out)

    def test_dark_version_softer_than_light_passes(self) -> None:
        self.save("home.png", icon())
        self.save("home.dark.png", icon(*DARK_SOFTER))
        code, out, _ = run([str(self.dir / "home.dark.png")])
        self.assertEqual(code, 0, out)

    def test_dark_flag_with_explicit_light_file(self) -> None:
        light = self.save("a.png", icon())
        dark = self.save("b.png", icon(*DARK_LOUDER))
        code, out, _ = run([str(dark), "--dark", "--light", str(light)])
        self.assertEqual(code, 1)
        self.assertIn("深色版比浅色版更饱和", out)
        code, out, _ = run([str(dark), "--dark"])      # 没有浅色版：按阈值判并提示
        self.assertEqual(code, 0)
        self.assertIn("没有找到对应的浅色版", out)

    def test_batch_directory_pairs_dark_versions_automatically(self) -> None:
        self.save("x.png", icon())
        self.save("x_dark.png", icon(*DARK_LOUDER))
        code, out, _ = run([str(self.dir)])
        self.assertEqual(code, 1)
        self.assertIn("深色版比浅色版更饱和", out)

    # ------------------------------------------------ SVG

    def svg(self, name: str, body: str, extra: str = "") -> Path:
        path = self.dir / name
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {extra}>{body}</svg>', encoding="utf-8")
        return path

    def test_svg_control_icon_with_current_color_passes(self) -> None:
        path = self.svg("search.svg", '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>', 'fill="none" stroke="currentColor" stroke-width="2"')
        code, out, _ = run([str(path), "--theme", "xiangcai"])
        self.assertEqual(code, 0, out)
        self.assertIn("控件图标", out)

    def test_svg_control_icon_must_use_token_colours(self) -> None:
        action = THEMES["xiangcai"]["action"]
        ok = self.svg("ok.svg", '<path d="M4 4h16"/>', f'fill="none" stroke="{action}" stroke-width="2"')
        code, out, _ = run([str(ok), "--theme", "xiangcai"])
        self.assertEqual(code, 0, out)
        self.assertIn("currentColor", out)           # 提示改用 currentColor
        bad = self.svg("bad.svg", '<path d="M4 4h16"/>', 'fill="none" stroke="#12AB34" stroke-width="2"')
        code, out, _ = run([str(bad), "--theme", "xiangcai"])
        self.assertEqual(code, 1)
        self.assertIn("令牌以外", out)
        code, out, _ = run([str(bad)])                # 没给主题：只报告，不判
        self.assertEqual(code, 0)
        self.assertIn("--theme", out)

    def test_svg_control_icon_does_not_look_at_saturation(self) -> None:
        action = THEMES["fitness-gym"]["action"]       # S 约 0.94，作为令牌色完全可以
        path = self.svg("s.svg", '<path d="M4 4h16"/>', f'fill="none" stroke="{action}"')
        self.assertEqual(run([str(path), "--theme", "fitness-gym"])[0], 0)

    def test_svg_control_icon_is_single_colour(self) -> None:
        a, b = THEMES["xiangcai"]["action"], THEMES["xiangcai"]["accent"]
        path = self.svg("two.svg", f'<path d="M4 4h16" stroke="{a}"/><path d="M4 8h16" stroke="{b}"/>', 'fill="none"')
        code, out, _ = run([str(path), "--theme", "xiangcai", "--kind", "control"])
        self.assertEqual(code, 1)
        self.assertIn("单色", out)

    def test_svg_block_icon_with_loud_custom_colours_fails(self) -> None:
        path = self.svg("loud.svg", '<rect width="24" height="24" fill="#FF3B00"/><path d="M4 4h16" stroke="#00AAFF" stroke-width="2"/>')
        code, out, _ = run([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("--hot-share", out)

    def test_svg_block_icon_with_pastel_colours_passes(self) -> None:
        path = self.svg("soft.svg", '<rect width="24" height="24" fill="#FFE9DD"/><circle cx="12" cy="12" r="6" fill="#FFBB96"/><path d="M6 12h12" stroke="#D68260" stroke-width="2"/>')
        code, out, _ = run([str(path)])
        self.assertEqual(code, 0, out)

    def test_svg_block_icon_theme_tokens_are_not_judged_by_saturation(self) -> None:
        t = THEMES["xiangcai"]
        body = (f'<rect width="24" height="24" fill="{t["actionTint"]}"/>'
                f'<path d="M4 4h16" stroke="{t["action"]}"/><path d="M4 8h16" stroke="{t["action"]}"/><path d="M4 12h16" stroke="{t["action"]}"/>')
        path = self.svg("tok.svg", body)
        self.assertEqual(run([str(path)])[0], 1)                                  # 不给主题：品牌阶描边 S 约 0.73，超 P90
        code, out, _ = run([str(path), "--theme", "xiangcai"])                    # 给了主题：令牌色不计饱和度
        self.assertEqual(code, 0, out)
        self.assertIn("令牌色", out)

    def test_svg_inline_style_and_named_colours_are_read(self) -> None:
        path = self.svg("style.svg", '<rect width="24" height="24" style="fill:#FF3B00;stroke:none"/><circle r="4" fill="rgb(255, 0, 0)"/>')
        code, out, _ = run([str(path)])
        self.assertEqual(code, 1)
        path2 = self.svg("named.svg", '<rect width="24" height="24" fill="red"/>')
        self.assertEqual(run([str(path2)])[0], 1)
        path3 = self.svg("none.svg", '<rect width="24" height="24" fill="none" stroke="white"/><path stroke="black" fill="url(#g)"/>')
        self.assertEqual(run([str(path3)])[0], 0)

    def test_svg_style_block_colours_are_read(self) -> None:
        path = self.svg("block.svg", '<style>.a{fill:#FF3B00}.b{stroke:#00AAFF}</style><rect class="a" width="24" height="24"/><path class="b" d="M4 4h16"/>')
        code, out, _ = run([str(path)])
        self.assertEqual(code, 1)
        self.assertIn("--hot-share", out)

    def test_svg_dark_pair(self) -> None:
        self.svg("m.svg", '<rect width="24" height="24" fill="#FFE9DD"/><circle r="6" fill="#FFBB96"/>')
        self.svg("m-dark.svg", '<rect width="24" height="24" fill="#5A2A1C"/><circle r="6" fill="#C0562F"/>')
        code, out, _ = run([str(self.dir / "m-dark.svg")])
        self.assertEqual(code, 1)
        self.assertIn("深色版比浅色版更饱和", out)

    # ------------------------------------------------ 输入有误

    def test_input_errors_exit_2(self) -> None:
        self.assertEqual(run([str(self.dir / "nothing.png")])[0], 2)
        self.assertEqual(run([str(self.dir)])[0], 2)            # 空目录
        bad = self.dir / "fake.png"
        bad.write_text("not an image", encoding="utf-8")
        self.assertEqual(run([str(bad)])[0], 2)
        good = self.save("g.png", icon())
        code, _, err = run([str(good), "--theme", "no-such-theme"])
        self.assertEqual(code, 2)
        self.assertIn("themes.json", err)
        self.save("h.png", icon())
        self.assertEqual(run([str(good), str(self.dir / "h.png"), "--light", str(good)])[0], 2)
        self.assertEqual(run([str(good), "--dark", "--light", str(self.dir / "missing.png")])[0], 2)

    def test_raster_cannot_be_a_control_icon(self) -> None:
        code, out, _ = run([str(self.save("c.png", icon())), "--kind", "control"])
        self.assertEqual(code, 1)
        self.assertIn("SVG", out)

    def test_runs_as_a_script_and_reports_exit_codes(self) -> None:
        good = self.save("g.png", icon())
        bad = self.save("b.png", icon((255, 60, 0, 255), (255, 30, 0, 255), (200, 0, 0, 255)))
        r = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "check_icon_image.py"), str(good)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0)
        self.assertIn("check icon image: ok", r.stdout)
        r = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "check_icon_image.py"), str(bad)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("均值S", r.stdout)


class PaletteTest(unittest.TestCase):
    def test_every_theme_gets_a_palette_that_passes_its_own_check(self) -> None:
        for tid in THEMES:
            p = cii.icon_palette(tid)
            light = {r["role"]: r for r in p["light"]}
            self.assertEqual(light["底块"]["hex"], THEMES[tid]["actionTint"], tid)
            self.assertGreaterEqual(light["线稿"]["contrast_to_base"], 3.0, tid)       # 线稿对底块 3:1
            for role in ("次层", "图形", "线稿"):
                self.assertLessEqual(light[role]["s"], 0.65 + 1e-9, (tid, role))
            self.assertEqual({r["role"] for r in p["dark"]}, {"底块", "次层", "图形", "线稿"})
            self.assertEqual({r["role"]: r["hex"] for r in p["dark"]}["图形"], THEMES[tid]["dark"]["actionText"])

    def test_icons_drawn_with_the_palette_pass_in_light_and_dark(self) -> None:
        def draw(rows) -> Image.Image:
            by = {r["role"]: tuple(cii.rgb_of_hex(r["hex"])) + (255,) for r in rows}
            return icon(by["底块"], by["次层"], by["线稿"], size=96)
        with tempfile.TemporaryDirectory() as tmp:
            for tid in THEMES:
                p = cii.icon_palette(tid)
                a = Path(tmp) / f"{tid}.png"
                b = Path(tmp) / f"{tid}-dark.png"
                draw(p["light"]).save(a)
                draw(p["dark"]).save(b)
            code, out, _ = run([tmp])
            self.assertEqual(code, 0, out)

    def test_palette_command(self) -> None:
        code, out, _ = run(["--palette", "fitness-gym"])
        self.assertEqual(code, 0)
        self.assertIn(THEMES["fitness-gym"]["actionTint"], out)
        self.assertIn("深色", out)
        self.assertEqual(run(["--palette", "nope"])[0], 2)
        self.assertEqual(run([])[0], 2)


class TemplateIconAssetsTest(unittest.TestCase):
    """模板库的彩色实心入口图标 kit/assets/solid：全部要通过默认阈值，换回高饱和原图或放进没压过饱和度的新图，这里会报错。
    2026-11-05 校准：按 S 乘系数压到均值约 0.42、P90 不超过 0.62 后全过；阈值未动。"""

    ICONS = HERE.parent / "kit" / "assets" / "solid"

    def files(self) -> list[Path]:
        return sorted(self.ICONS.glob("*.webp"))

    def test_every_template_icon_passes_the_default_thresholds(self) -> None:
        self.assertGreaterEqual(len(self.files()), 12, "模板库的彩色实心业务图标应不少于 12 个")
        code, out, _ = run([str(self.ICONS), "-r"])
        self.assertEqual(code, 0, out)
        self.assertIn("check icon image: ok", out)
        self.assertNotIn("超限", out)

    def test_template_icons_are_judged_with_the_unchanged_default_limits(self) -> None:
        # 样板图通过靠压低图标饱和度，不靠放宽阈值：默认上限仍是视觉规范里写的数
        self.assertEqual((cii.DEFAULTS["max_mean"], cii.DEFAULTS["p90"], cii.DEFAULTS["hot_share"], cii.DEFAULTS["hot_s"], cii.DEFAULTS["max_hues"]),
                         (0.45, 0.65, 0.03, 0.80, 2))

    def test_icons_are_square_webp_with_a_transparent_background(self) -> None:
        for path in self.files():
            with Image.open(path) as im:
                im.load()
                self.assertEqual(im.format, "WEBP", path.name)
                self.assertEqual(im.size[0], im.size[1], str(path))
                alpha = im.convert("RGBA").getchannel("A")
                low, high = alpha.getextrema()
                self.assertEqual(low, 0, f"{path}：透明底被改掉了")
                self.assertGreaterEqual(high, 128, str(path))

    def test_template_icons_are_judged_on_the_icon_pixels_not_the_background(self) -> None:
        # 度量只统计不透明像素：透明底占了一部分，统计像素应少于总像素，且图标没有退化成中性色
        for path in self.files():
            with Image.open(path) as im:
                m = cii.analyze_image(im)
            self.assertGreater(m.counted, 5000, str(path))
            self.assertLess(m.counted, m.total * 0.9, str(path))


class ThemeTokenTest(unittest.TestCase):
    def test_theme_colours_cover_light_dark_and_shared(self) -> None:
        colours = cii.load_theme_colors("xiangcai")
        t = THEMES["xiangcai"]
        for hexv in (t["action"], t["actionTint"], t["dark"]["actionText"], t["dark"]["surface"]):
            self.assertIn(tuple(int(hexv[i:i + 2], 16) for i in (1, 3, 5)), colours, hexv)
        self.assertIn((0x2B, 0x23, 0x26), colours)    # shared.ink
        with self.assertRaises(KeyError):
            cii.load_theme_colors("nope")

    def test_every_theme_loads(self) -> None:
        for tid in THEMES:
            self.assertGreater(len(cii.load_theme_colors(tid)), 20, tid)


class IconSetsTest(unittest.TestCase):
    """soften_icon_image.py brings icons inside the limits and a folder of icons to a few hues; the template icon set stays inside the limits.
    入口图标按“不同入口用不同低饱和主色”区分，所以模板库的图标只按单个图标的阈值验收，不要求整组不超过 3 个色相。"""

    ROOT = HERE.parent / "kit" / "assets"
    SETS = {
        "solid icons": ROOT / "solid",
    }

    @staticmethod
    def disc(hue: float, s: float = 1.0, v: float = 0.9, size: int = 60) -> Image.Image:
        import colorsys
        r, g, b = (round(c * 255) for c in colorsys.hsv_to_rgb(hue / 360, s, v))
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((6, 6, size - 6, size - 6), fill=(r, g, b, 255))
        return im

    def test_a_saturated_icon_is_softened_inside_the_limits_with_hue_value_and_alpha_unchanged(self) -> None:
        import numpy as np
        import soften_icon_image as si
        im = self.disc(8)
        self.assertFalse(si.inside(cii.analyze_image(im), si.targets(0.03)))
        k = si.fit(im, "PNG", si.targets(0.03))
        self.assertLess(k, 1.0)
        out = si.transform(im, k)
        self.assertTrue(si.inside(cii.analyze_image(out), si.targets(0.03)))
        a, b = np.asarray(im).astype(float), np.asarray(out).astype(float)
        self.assertTrue((a[..., 3] == b[..., 3]).all(), "alpha is not touched")
        ha, _, va = si.rgb_to_hsv(a[..., :3] / 255)
        hb, _, vb = si.rgb_to_hsv(b[..., :3] / 255)
        mask = a[..., 3] > 0
        self.assertLess(abs(va - vb)[mask].max(), 0.01, "lightness is not touched")
        self.assertLess(abs(((ha - hb) + 180) % 360 - 180)[mask].max(), 3, "hue is not touched")

    def test_an_icon_that_already_passes_is_left_alone(self) -> None:
        import soften_icon_image as si
        self.assertEqual(si.fit(self.disc(210, s=0.3, v=0.9), "PNG", si.targets(0.03)), 1.0)

    def test_the_hues_of_a_folder_are_pooled_and_snapped_to_the_wanted_number(self) -> None:
        import soften_icon_image as si
        images = [self.disc(h, s=0.5) for h in (5, 65, 125, 185, 245, 305)]
        self.assertGreater(len(si.set_hue_families(images)), 3)
        centres = si.hue_centres(images, 3)
        self.assertEqual(len(centres), 3)
        snapped = [si.transform(im, 1.0, centres) for im in images]
        self.assertLessEqual(len(si.set_hue_families(snapped)), 3)

    def test_every_icon_set_passes_the_limits(self) -> None:
        import soften_icon_image as si
        for name, folder in self.SETS.items():
            with self.subTest(set=name):
                files = sorted(folder.glob("*.webp"))
                self.assertGreaterEqual(len(files), 6, f"{name}: icons missing in {folder}")
                for f in files:
                    m = cii.analyze_image(si.load(f))
                    self.assertTrue(m.mean <= cii.DEFAULTS["max_mean"] and m.p90 <= cii.DEFAULTS["p90"] and m.hot_share <= cii.DEFAULTS["hot_share"]
                                    and len(m.hues) <= cii.DEFAULTS["max_hues"], f"{f.name}: mean {m.mean:.2f} p90 {m.p90:.2f} hot {m.hot_share:.1%} hues {len(m.hues)}")


if __name__ == "__main__":
    unittest.main()
