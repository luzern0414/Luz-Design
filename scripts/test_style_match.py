import json
from pathlib import Path

import pytest

from style_match import build_match, can_design, dock_grid, infer_layout, rank_styles, session_style_errors


def test_interface_output_requires_confirmation_even_with_reading_card(tmp_path):
    cards = tmp_path / "raw/00-rules"
    cards.mkdir(parents=True)
    (cards / "reading-html.md").write_text("reading page rules", encoding="utf-8")
    assert session_style_errors(tmp_path) == []
    assert session_style_errors(tmp_path, required=True)


def test_reference_arrangement_is_evidence_not_a_fixed_grid():
    # Eight entries derive to 4 x 2; the 5 x 2 of the reference is only a hint.
    brief = "外卖金刚位 8 枚服务图标，参考 5×2 排列、中文标签、圆润 Q 版、马卡龙渐变。"

    match = build_match(brief, viewport={"width": 390, "height": 844})

    assert "5×2" in match["evidence"]["layout_hints"]
    assert match["layout"]["hard_constraints"] == []
    assert match["layout"]["grid"] != "5x2"
    assert match["layout"]["columns"] < 5
    assert match["layout"]["adaptation"]


# visual-design.html 金刚区与宫格入口, 推导示例 (screen width 375, margin 12): entries, longest label -> columns x rows.
DOCK_EXAMPLES = [(4, 4, 4, 1), (5, 4, 5, 1), (6, 4, 3, 2), (7, 4, 4, 2), (8, 4, 4, 2), (9, 4, 5, 2), (10, 4, 5, 2), (8, 5, 4, 2)]


@pytest.mark.parametrize("entries,label,columns,rows", DOCK_EXAMPLES)
def test_icon_dock_follows_the_worked_examples_of_the_rule_page(entries, label, columns, rows):
    dock = dock_grid(entries, label, 375)

    assert (dock["columns"], dock["rows"]) == (columns, rows)
    assert dock["pages"] == 1 and dock["visible_entries"] == entries


def test_icon_dock_pages_sideways_and_folds_a_thin_last_page_into_an_all_entry():
    dock = dock_grid(11, 4, 375)

    assert (dock["columns"], dock["rows"], dock["pages"]) == (5, 2, 1)
    assert dock["visible_entries"] == 9 and dock["all_entry"] is True
    full = dock_grid(25, 4, 375)
    assert full["pages"] == 3 and full["all_entry"] is False
    assert dock_grid(100, 4, 375)["pages"] == 3


def test_icon_dock_inputs_come_from_label_length_and_width():
    assert dock_grid(8, 4, 375)["columns_max"] == 5
    assert dock_grid(8, 5, 375)["columns_max"] == 4      # cellMin 78 leaves four columns
    six = dock_grid(8, 6, 375)                           # cellMin 92 leaves three columns: 5 entries and the all-entry fill two rows
    assert (six["columns_max"], six["columns"], six["rows"], six["visible_entries"], six["all_entry"]) == (3, 3, 2, 5, True)
    assert dock_grid(8, 4, 320)["page_margin"] == 12 and dock_grid(8, 4, 414)["page_margin"] == 16
    assert dock_grid(8, 9, 320)["notes"]                  # fewer than three fit: shorten the labels


def test_the_matcher_uses_the_dock_formula_on_phone_widths_only():
    brief = "外卖金刚位服务图标，中文标签"
    phone = infer_layout(brief, viewport={"width": 375, "height": 812}, content={"items": 10})
    desktop = infer_layout(brief, viewport={"width": 1440, "height": 900}, content={"items": 10})

    assert phone["grid"] == "icon-dock" and phone["regions"][0]["dock"]["columns"] == 5
    assert "dock" not in desktop["regions"][0]
    longer = infer_layout(brief, viewport={"width": 375, "height": 812}, content={"items": 8, "longest_label": 5})
    assert longer["columns"] == 4


def test_dock_command_line_prints_the_derivation(capsys):
    from style_match import main

    assert main(["--dock", "9", "4", "375"]) == 0
    assert json.loads(capsys.readouterr().out)["columns"] == 5


def test_explicit_mandatory_arrangement_is_the_exception_that_becomes_a_constraint():
    match = build_match("必须固定 5×2 排列的服务图标", viewport={"width": 390, "height": 844}, content={"items": 10})

    assert match["layout"]["hard_constraints"][0]["value"] == "5×2"
    assert match["layout"]["grid"] == "5x2"
    assert match["layout"]["columns"] == 5
    assert match["layout"]["regions"][0]["rows"] == 2


def test_asymmetric_dashboard_keeps_relationship_without_freezing_placement():
    brief = "非对称指标看板：超大核心数字、辅助指标、右侧独立纵向信息面板，深浅主题布局保持一致。"

    match = build_match(
        brief,
        viewport={"width": 1440, "height": 900},
        content={"primary_metrics": 1, "supporting_metrics": 6, "panel_items": 8},
    )

    relationships = match["semantic"]["relationships"]
    assert "asymmetric" in relationships
    assert "primary_metric_anchor" in relationships
    assert "independent_context_panel" in relationships
    assert match["layout"]["regions"]
    assert match["layout"]["grid"] != "2x2"
    assert match["layout"]["rail_position"] in {"right", "bottom", "collapsible"}
    assert match["layout"]["decisions"]


def test_named_asymmetric_dashboard_supplies_its_required_relationships():
    match = build_match("非对称指标看板")

    assert {
        "asymmetric",
        "primary_metric_anchor",
        "supporting_metrics",
        "independent_context_panel",
    }.issubset(match["semantic"]["relationships"])


def test_layout_reacts_to_viewport_and_content():
    brief = "图文服务入口，优先展示高频服务，次要服务可继续浏览。"
    desktop = infer_layout(brief, viewport={"width": 1440, "height": 900}, content={"items": 7})
    mobile = infer_layout(brief, viewport={"width": 390, "height": 844}, content={"items": 7})

    assert desktop["columns"] > mobile["columns"]
    assert desktop["regions"] != mobile["regions"] or desktop["main_ratio"] != mobile["main_ratio"]
    assert desktop["adaptation"] and mobile["adaptation"]


def test_style_candidates_explain_reference_signals_without_becoming_commands():
    brief = "圆润 Q 版服务图标，参考毛玻璃、软糖和轻拟物，要求清晰、统一、可读。"

    candidates = rank_styles(brief)

    assert 2 <= len(candidates) <= 3
    assert all(candidate["reasons"] for candidate in candidates)
    assert all("fixed" not in reason.lower() for candidate in candidates for reason in candidate["reasons"])


def test_motion_references_become_stateful_interaction_evidence():
    match = build_match("参考 MorphIcons 的 SVG 平滑变形和 Lordicon 的 hover 触发动态交互图标。")

    assert "morph" in match["evidence"]["motion_signals"]
    assert "hover" in match["evidence"]["motion_signals"]
    assert match["interaction"]["mode"] == "state-transition"
    assert match["interaction"]["trigger"] == "hover-or-state-change"
    assert match["interaction"]["approval_required"] is True


def test_pending_approval_blocks_design_until_scope_is_confirmed():
    match = build_match("阅读型产品首页，强调清晰层级和轻量插画。")

    assert match["approval"]["status"] == "pending"
    assert can_design(match) is False

    approved = dict(match)
    approved["approval"] = {
        "status": "approved",
        "selectedStyle": match["candidates"][0]["id"],
        "scope": {
            "controls": "line-vector",
            "entryIcons": match["candidates"][0]["id"],
            "heroDecorations": match["candidates"][0]["id"],
        },
    }
    assert can_design(approved) is True


def test_style_matrix_is_discoverable_and_has_reference_boundaries():
    matrix_path = Path(__file__).parents[1] / "references" / "interface-style-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    assert len(matrix["styles"]) >= 10
    for style in matrix["styles"]:
        assert style["id"]
        assert style["signals"]
        assert style["suitable_roles"]
        assert style["avoid"]
        assert style["approval_scope"]



def test_candidate_styles_never_claim_the_control_icons():
    matrix_path = Path(__file__).parents[1] / "references" / "interface-style-matrix.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    for style in matrix["styles"]:
        assert "control-icons" not in style["suitable_roles"], style["id"]
        assert "control-icons" in style["avoid"], style["id"]
        assert set(style["approval_scope"]) <= {"entryIcons", "metricIllustrations", "heroDecorations", "emptyState"}, style["id"]
