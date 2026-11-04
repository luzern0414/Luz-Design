"""audit_theme_discipline.py: the colour-discipline audit of themes.json (scale quality, one hue family, hue budget, colour-vision difference,
area and elevation discipline, dark companions) and the combination check of theme + icons + radius + depth + type scale + motion."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_theme_discipline as atd  # noqa: E402
import check_contrast as cc  # noqa: E402
import make_dark as md  # noqa: E402

DATA = atd.load_data()
SHARED = DATA["shared"]
STATUSES = set(atd.SEVERITIES)


def by_id(findings):
    return {f.id: f for f in findings}


def make_scale(hue: float = 250.0, hues: dict[int, float] | None = None) -> list[str]:
    """A hand-made 10-step scale: lightness falls evenly, chroma rises to step 6 and falls again, one hue."""
    lights = [0.96, 0.91, 0.85, 0.77, 0.67, 0.57, 0.48, 0.40, 0.32, 0.24]
    chromas = [0.03, 0.05, 0.08, 0.11, 0.14, 0.16, 0.15, 0.13, 0.11, 0.08]
    return [md.oklch_hex(lights[i], chromas[i], (hues or {}).get(i, hue)) for i in range(10)]


def good_theme(hue: float = 250.0) -> dict:
    scale = make_scale(hue)
    return {"action": scale[5], "actionPress": scale[6], "actionTint": scale[0], "canvas": "#F5F5F5", "navBg": "#FFFFFF",
            "accent": md.oklch_hex(0.62, 0.14, hue + 40), "accentTint": md.oklch_hex(0.95, 0.03, hue + 40), "scale": scale}


def audit(theme: dict, shared: dict | None = None):
    return by_id(atd.audit_theme("t", theme, shared or SHARED))


# ---- the whole library -------------------------------------------------------------------------------------------------------------------

def test_every_theme_of_the_library_is_audited_without_crashing():
    results = atd.audit_all(DATA)
    assert len(results) == len(DATA["themes"]) >= 25
    for theme_id, findings in results.items():
        assert [f.id for f in findings] == list(atd.CHECK_IDS), theme_id
        for f in findings:
            assert f.status in STATUSES and f.value and f.metric and f.threshold, (theme_id, f.id)
            if f.status in ("FAIL", "WARN"):
                assert f.fix, (theme_id, f.id)
    json.dumps({tid: [f.to_dict() for f in findings] for tid, findings in results.items()}, ensure_ascii=False)


def test_the_summary_counts_every_theme_once_per_check():
    results = atd.audit_all(DATA)
    summary = atd.summarize(results)
    assert set(summary) == set(atd.CHECK_IDS)
    for cid, counts in summary.items():
        assert sum(counts.values()) == len(results), cid


def test_the_command_line_writes_json_and_markdown_and_exits_by_fail(tmp_path, capsys):
    out_json, out_md = tmp_path / "x" / "r.json", tmp_path / "x" / "r.md"
    code = atd.main(["--json", str(out_json), "--md", str(out_md)])
    printed = capsys.readouterr().out
    report = json.loads(out_json.read_text(encoding="utf-8"))
    any_fail = any(f["status"] == "FAIL" for findings in report["themes"].values() for f in findings)
    assert code == (1 if any_fail else 0)
    assert len(report["themes"]) == len(DATA["themes"]) and set(report["summary"]) == set(atd.CHECK_IDS)
    markdown = out_md.read_text(encoding="utf-8")
    assert "| 主题 | A1 |" in markdown and "xiangcai" in markdown and "共享令牌" in markdown
    assert "A1" in printed and "xiangcai" in printed


def test_a_single_theme_and_an_unknown_theme(capsys):
    assert atd.main(["--theme", "coffee", "--quiet"]) in (0, 1)
    assert atd.main(["--theme", "no-such-theme"]) == 2
    assert "no-such-theme" in capsys.readouterr().err


def test_a_failing_theme_gives_exit_code_one(tmp_path):
    data = copy.deepcopy(DATA)
    data["themes"] = {"broken": good_theme()}
    data["themes"]["broken"]["scale"][3], data["themes"]["broken"]["scale"][4] = data["themes"]["broken"]["scale"][4], data["themes"]["broken"]["scale"][3]
    path = tmp_path / "themes.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert atd.main(["--themes-file", str(path), "--quiet"]) == 1


# ---- A / B: a disciplined and an undisciplined theme -------------------------------------------------------------------------------------

def test_a_single_hue_even_scale_passes_a1_a2_a3_and_b1():
    got = audit(good_theme())
    for cid in ("A1", "A2", "A3", "B1", "B2", "B3", "C2", "C3"):
        assert got[cid].status == "PASS", (cid, got[cid].value)


def test_a_shuffled_scale_fails_a1():
    theme = good_theme()
    theme["scale"][2], theme["scale"][7] = theme["scale"][7], theme["scale"][2]
    assert audit(theme)["A1"].status == "FAIL"


def test_two_nearly_equal_steps_and_a_jump_warn_a1():
    theme = good_theme()
    lights = [0.96, 0.95, 0.94, 0.80, 0.67, 0.57, 0.48, 0.40, 0.32, 0.24]        # steps 1-3 almost equal, then a jump of 0.14
    theme["scale"] = [md.oklch_hex(l, c, 250) for l, c in zip(lights, [0.03, 0.05, 0.08, 0.11, 0.14, 0.16, 0.15, 0.13, 0.11, 0.08])]
    got = audit(theme)["A1"]
    assert got.status == "WARN" and got.data["ratio"] > atd.A1_MAX_STEP_RATIO


def test_a_drifting_hue_in_the_scale_warns_a2():
    theme = good_theme()
    theme["scale"] = make_scale(250, hues={2: 290.0})
    got = audit(theme)["A2"]
    assert got.status == "WARN" and got.data["worst"] > atd.A2_MAX_HUE_DRIFT


def test_a_chroma_valley_warns_a3():
    theme = good_theme()
    lights = [0.96, 0.91, 0.85, 0.77, 0.67, 0.57, 0.48, 0.40, 0.32, 0.24]
    chromas = [0.03, 0.10, 0.04, 0.11, 0.14, 0.16, 0.15, 0.13, 0.11, 0.08]       # step 2 is richer than step 3
    theme["scale"] = [md.oklch_hex(lights[i], chromas[i], 250) for i in range(10)]
    assert audit(theme)["A3"].status == "WARN"


def test_press_and_tint_in_another_hue_warn_b1():
    theme = good_theme()
    theme["actionPress"] = md.oklch_hex(0.48, 0.15, 285)
    got = audit(theme)["B1"]
    assert got.status == "WARN" and got.data["worst"] > atd.B1_MAX_HUE_GAP


def test_brand_red_equal_to_danger_is_flagged_family_overlap_c2():
    theme = good_theme()
    theme["action"] = md.oklch_hex(0.52, 0.18, md.hex_to_oklch(SHARED["danger"])[2])
    got = audit(theme)["C2"]
    assert got.status in ("WARN", "FAIL") and "family-overlap" in got.tags


def test_a_moderate_overlap_is_only_an_info_c2():
    theme = good_theme()
    theme["action"] = md.oklch_hex(0.52, 0.18, md.hex_to_oklch(SHARED["danger"])[2] - 16)
    got = audit(theme)["C2"]
    assert got.status == "INFO" and "family-overlap" in got.tags


def test_tinted_text_colour_fails_b3():
    shared = copy.deepcopy(SHARED)
    shared["ink"] = md.oklch_hex(0.27, 0.09, 30)
    assert audit(good_theme(), shared)["B3"].status == "FAIL"
    assert audit(good_theme())["B3"].status == "PASS"


def test_a_pink_navigation_bar_on_a_blue_brand_warns_b2():
    theme = good_theme()
    theme["navBg"] = md.oklch_hex(0.90, 0.06, 20)
    assert audit(theme)["B2"].status == "WARN"
    theme["navBg"] = md.oklch_hex(0.95, 0.02, 250)   # same hue as the brand, low chroma
    assert audit(theme)["B2"].status == "PASS"


@pytest.mark.parametrize("offset,status,tag", [(10, "WARN", None), (40, "PASS", "analogous"), (100, "INFO", "clash"), (180, "INFO", "complementary")])
def test_c3_names_the_relation_between_brand_and_accent(offset, status, tag):
    theme = good_theme()
    theme["accent"] = md.oklch_hex(0.62, 0.14, 250 + offset)
    got = audit(theme)["C3"]
    assert got.status == status, got.value
    assert tag is None or tag in got.tags


def test_the_hue_budget_counts_extra_hues():
    theme = good_theme()
    theme["modules"] = {f"m{i}": {"tint": "#FFFFFF", "mid": "#EEEEEE", "solid": md.oklch_hex(0.5, 0.12, hue)} for i, hue in enumerate((100, 190, 300, 340))}
    got = audit(theme)["C1"]
    assert got.status == "WARN" and got.data["clusters"] > atd.C1_MAX_CLUSTERS
    assert audit(good_theme())["C1"].status == "PASS"


def test_a_neutral_brand_skips_the_hue_checks():
    theme = good_theme()
    theme.pop("scale")
    theme.update(action="#27272A", actionPress="#18181B", actionTint="#F4F4F5")
    got = audit(theme)
    assert got["B1"].status == got["C2"].status == got["C3"].status == "NA"
    assert got["A1"].status == "NA"


def test_equal_canvas_and_surface_warn_e1_and_a_missing_dark_is_not_applicable():
    theme = good_theme()
    theme["canvas"] = "#FFFFFF"
    got = audit(theme)
    assert got["E1"].status == "WARN"
    assert got["F1"].status == got["F2"].status == got["F3"].status == "NA"


def test_a_dark_brand_that_turns_into_another_colour_warns_f2_and_f3():
    theme = copy.deepcopy(DATA["themes"]["xiangcai"])
    assert {f.status for f in atd.audit_theme("xiangcai", theme, SHARED) if f.id in ("F1", "F2", "F3")} == {"PASS"}
    theme["dark"]["action"] = md.oklch_hex(0.85, 0.12, md.hex_to_oklch(theme["action"])[2])
    theme["dark"]["actionText"] = md.oklch_hex(0.85, 0.12, md.hex_to_oklch(theme["action"])[2] + 60)
    theme["dark"]["canvas"] = "#000000"
    got = by_id(atd.audit_theme("xiangcai", theme, SHARED))
    assert got["F1"].status == got["F2"].status == got["F3"].status == "WARN"


# ---- colour-vision simulation and small helpers ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", atd.D_KINDS)
@pytest.mark.parametrize("grey", ["#000000", "#404040", "#808080", "#C0C0C0", "#FFFFFF"])
def test_a_pure_grey_stays_grey_after_the_simulation(grey, kind):
    simulated = atd.simulate(grey, kind)
    assert max(abs(a - b) for a, b in zip(cc.rgb(simulated), cc.rgb(grey))) <= 2
    assert atd.chroma_of(simulated) < 0.01


def test_red_and_green_come_much_closer_for_deuteranopia_and_protanopia():
    red, green = SHARED["danger"], SHARED["success"]
    normal = atd.delta_e(red, green)
    for kind in ("protan", "deut"):
        assert atd.cvd_delta_e(red, green, kind) < 0.5 * normal, kind
    assert atd.cvd_delta_e(red, green, "tritan") > 0.5 * normal      # a tritan eye still tells red from green


def test_blue_and_yellow_come_closer_for_tritanopia():
    blue, yellow = "#2563EB", "#E8B04B"
    assert atd.cvd_delta_e(blue, yellow, "tritan") < atd.delta_e(blue, yellow)


def test_delta_e_is_zero_for_equal_colours_and_symmetric():
    assert atd.delta_e("#336699", "#336699") == pytest.approx(0, abs=1e-9)
    assert atd.delta_e("#336699", "#996633") == pytest.approx(atd.delta_e("#996633", "#336699"))
    assert atd.delta_e("#000000", "#FFFFFF") == pytest.approx(100, abs=0.5)


def test_hue_clusters_wrap_around_and_keep_equal_hues_together():
    clusters = atd.hue_clusters({"a": 350.0, "b": 5.0, "c": 100.0, "d": 100.0, "e": 250.0}, 20.0)
    assert sorted(sorted(c) for c in clusters) == [["a", "b"], ["c", "d"], ["e"]]
    assert atd.hue_clusters({}, 20.0) == []
    assert atd.hue_clusters({"x": 10.0}, 20.0) == [["x"]]
    assert len(atd.hue_clusters({"a": 0.0, "b": 25.0, "c": 50.0}, 20.0)) == 3


def test_checks_that_only_read_shared_tokens_are_marked_shared():
    got = audit(good_theme())
    assert {cid for cid, f in got.items() if f.scope == "shared"} == {"B3", "C4", "D1", "E2"}


def test_a_bad_theme_is_flagged_on_every_count_at_once():
    theme = good_theme()
    theme["scale"][1], theme["scale"][6] = theme["scale"][6], theme["scale"][1]                       # shuffled scale
    theme["action"] = md.oklch_hex(0.52, 0.18, md.hex_to_oklch(SHARED["danger"])[2])                  # brand red = danger red
    shared = copy.deepcopy(SHARED)
    shared["ink"] = md.oklch_hex(0.27, 0.09, 30)                                                       # tinted body text
    got = audit(theme, shared)
    assert got["A1"].status == "FAIL" and got["B3"].status == "FAIL"
    assert got["C2"].status == "WARN" and "family-overlap" in got["C2"].tags
    assert got["B1"].status == "WARN"                                                                  # action left the family of press / tint


# ---- combinations ------------------------------------------------------------------------------------------------------------------------

def combo(*args, **kwargs):
    return atd.check_combo("xiangcai", *args, **kwargs)


def test_line_standard_soft_passes():
    got = combo("line", "standard", "soft", "standard", "calm")
    assert got["ok"] and got["errors"] == [] and got["needs_ruling"] == []
    assert set(got) >= {"ok", "errors", "needs_ruling", "notes", "contrast"}
    assert got["contrast"]["white_on_action"] >= 4.5 and got["contrast"]["ink_on_canvas"] >= 4.5
    assert any("安静" in n for n in got["notes"])


def test_clay3d_on_controls_is_an_error():
    got = combo("clay3d", "standard", "soft", "standard", "calm", icon_roles=("controls", "entry"))
    assert not got["ok"] and any("控件" in e for e in got["errors"])


def test_clay3d_on_entry_pages_needs_a_ruling_but_is_not_an_error():
    got = combo("clay3d", "standard", "soft", "standard", "calm")
    assert got["ok"] and got["errors"] == []
    assert any("黏土质感入口图标不在现行风格矩阵允许范围内" in r for r in got["needs_ruling"])
    assert combo("clay3d", "standard", "soft", "standard", "calm", icon_roles=("empty",))["needs_ruling"] == []


def test_duotone_uses_the_tint_for_the_base_and_the_accent_for_details_and_stays_off_controls():
    got = combo("duotone", "standard", "soft", "standard", "calm")
    assert got["ok"] and any(DATA["themes"]["xiangcai"]["actionTint"] in n and DATA["themes"]["xiangcai"]["accent"] in n for n in got["notes"])
    assert "accent_on_actionTint" in got["contrast"]
    bad = combo("duotone", "standard", "soft", "standard", "calm", icon_roles=("controls",))
    assert not bad["ok"] and bad["errors"]
    assert not combo("duotone", "standard", "soft", "standard", "calm", icon_roles=("result",))["ok"]


def test_glass_on_navigation_needs_a_ruling_and_on_hero_does_not():
    nav = combo("line", "standard", "glass", "standard", "calm", glass_roles=("navigation",))
    assert nav["ok"] and any("现规则禁止控制器表面使用毛玻璃" in r for r in nav["needs_ruling"])
    hero = combo("line", "standard", "glass", "standard", "calm", glass_roles=("hero", "entry-icon"))
    assert hero["needs_ruling"] == [] and hero["contrast"]["glass_light_ink_worst"] >= atd.GLASS_MIN_CONTRAST
    assert hero["contrast"]["glass_dark_ink_worst"] >= atd.GLASS_MIN_CONTRAST
    for role in ("tabbar", "sheet", "dialog", "popover"):
        assert combo("line", "standard", "glass", "standard", "calm", glass_roles=(role,))["needs_ruling"]


def test_glass_text_contrast_below_4_5_is_an_error():
    data = copy.deepcopy(DATA)
    data["shared"]["ink"] = "#9A9A9A"                       # a pale text colour on a translucent white pane
    got = atd.check_combo("xiangcai", "line", "standard", "glass", "standard", "calm", data=data)
    assert not got["ok"] and any("glass light" in e for e in got["errors"])
    assert got["contrast"]["glass_light_ink_worst"] < atd.GLASS_MIN_CONTRAST


def test_glass_contrast_uses_the_worst_background_of_the_theme():
    measured = atd.glass_contrast(DATA["themes"]["ai-agent"], SHARED)
    assert measured["light"]["worst"] == min(measured["light"]["by_background"].values())
    assert set(measured["light"]["by_background"]) == {"#FFFFFF", "主色阶 4"} and not measured["light"]["approximated_step4"]
    assert set(measured["dark"]["by_background"]) == {"dark canvas", "dark action"}
    assert atd.glass_contrast(DATA["themes"]["coffee"], SHARED)["light"]["approximated_step4"]      # no scale: step 4 is approximated


def test_round_and_tight_radii_need_a_ruling_and_standard_does_not():
    for shape, radii in (("round", (6, 10, 16, 20)), ("tight", (2, 4, 8, 12))):
        got = combo("line", shape, "soft", "standard", "calm")
        assert got["needs_ruling"] and got["ok"], shape
        assert tuple(got["resolved"]["radii"][k] for k in ("tag", "control", "card", "dialog")) == radii
    standard = combo("line", "standard", "soft", "standard", "calm")
    assert tuple(standard["resolved"]["radii"].values()) == (4, 8, 12, 16)


def test_type_packs_allow_only_their_own_sizes_and_the_three_weights():
    assert combo("line", "standard", "soft", "standard", "calm", type_uses=[(12, 400), (16, 600), (22, 700), (28, 700)])["ok"]
    assert not combo("line", "standard", "soft", "standard", "calm", type_uses=[(15, 400)])["ok"]          # 15 is not in the scale
    assert not combo("line", "standard", "soft", "standard", "calm", type_uses=[(32, 700)])["ok"]          # 32 belongs to the admin scale only
    assert combo("line", "standard", "soft", "compact", "calm", type_uses=[(14, 400), (32, 700)])["ok"]
    assert not combo("line", "standard", "soft", "bold", "calm", type_uses=[(16, 700)])["ok"]               # 700 only from 22
    assert not combo("line", "standard", "soft", "bold", "calm", type_uses=[(18, 500)])["ok"]               # no weight 500
    assert combo("line", "standard", "soft", "bold", "calm", type_uses=[(18, 600), (22, 700)])["ok"]
    assert combo("line", "standard", "soft", "compact", "calm")["resolved"]["type"]["body"] == "14/22"


def test_motion_only_describes_the_duration_preference():
    texts = {m: combo("line", "standard", "soft", "standard", m)["notes"][-1] for m in atd.MOTIONS}
    assert len(set(texts.values())) == 3
    assert all(any(m_text in n for n in combo("line", "standard", "soft", "standard", m)["notes"]) for m, m_text in atd.MOTIONS.items())


def test_unknown_values_and_themes_are_errors():
    assert not combo("neon", "standard", "soft", "standard", "calm")["ok"]
    assert not combo("line", "square", "soft", "standard", "calm")["ok"]
    assert not combo("line", "standard", "frosted", "standard", "calm")["ok"]
    assert not combo("line", "standard", "soft", "huge", "calm")["ok"]
    assert not combo("line", "standard", "soft", "standard", "wild")["ok"]
    assert not atd.check_combo("no-such-theme", "line", "standard", "soft", "standard", "calm")["ok"]


def test_every_library_theme_accepts_the_standard_combination():
    for theme_id in DATA["themes"]:
        got = atd.check_combo(theme_id, "line", "standard", "soft", "standard", "calm")
        assert got["ok"] and got["needs_ruling"] == [], theme_id


def test_the_combination_on_the_command_line(capsys):
    assert atd.main(["--combo", "ai-agent", "line", "standard", "soft", "standard", "calm"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] and printed["errors"] == []
    assert atd.main(["--combo", "ai-agent", "clay3d", "standard", "soft", "standard", "calm", "--icon-roles", "controls,entry"]) == 1
    assert json.loads(capsys.readouterr().out)["errors"]
    assert atd.main(["--combo", "ai-agent", "line", "standard", "glass", "standard", "calm", "--glass-roles", "navigation"]) == 0
    assert json.loads(capsys.readouterr().out)["needs_ruling"]
