"""The style boards, the reference-site registry, the theme library and the style matrix must agree with each other."""
import json
from pathlib import Path

import pytest

REFS = Path(__file__).resolve().parents[1] / "references"
BOARDS = json.loads((REFS / "style-boards.json").read_text(encoding="utf-8"))
THEMES = json.loads((REFS / "themes.json").read_text(encoding="utf-8"))["themes"]
MATRIX = {s["id"] for s in json.loads((REFS / "interface-style-matrix.json").read_text(encoding="utf-8"))["styles"]}
SITES = {s["id"] for s in json.loads((REFS / "reference-sites.json").read_text(encoding="utf-8"))["items"]}
DIALS = set(BOARDS["dials"])
SURFACES = {"mini", "admin", "web"}
MOTION = {"calm", "snappy", "friendly"}
PLACEHOLDERS = {"{action}", "{accent}", "{canvas}"}


@pytest.mark.parametrize("board", BOARDS["boards"], ids=lambda b: b["id"])
def test_board_is_consistent(board):
    assert board["theme"] in THEMES, f"{board['id']}: theme {board['theme']} is not in themes.json"
    assert len(board["personality"]) == 3 and len(board["anti_goals"]) == 3
    assert set(board["dials"]) == DIALS and all(0 <= v <= 10 for v in board["dials"].values())
    assert set(board["fits"]["surfaces"]) <= SURFACES
    assert board["motion"]["personality"] in MOTION
    assert set(board["matrix_styles"]) <= MATRIX, f"{board['id']}: unknown matrix style"
    assert set(board["reference_sites"]) <= SITES, f"{board['id']}: unknown reference site"
    radius = board["shape"]["radius"]
    assert set(radius) == {"tag", "control", "card", "panel"}
    block = board["imagery"]["imagegen_style_block"]
    if block:
        assert "no text" in board["imagery"]["negative"] or "text" in board["imagery"]["negative"]
        assert set(p for p in PLACEHOLDERS if p in block) <= PLACEHOLDERS


def test_board_ids_are_unique():
    ids = [b["id"] for b in BOARDS["boards"]]
    assert len(ids) == len(set(ids))


def test_non_standard_shapes_and_glass_are_flagged_for_ruling():
    for b in BOARDS["boards"]:
        r = b["shape"]["radius"]
        if (r["tag"], r["control"], r["card"], r["panel"]) != (4, 8, 12, 16):
            assert any("圆角" in x for x in b["needs_ruling"]), f"{b['id']}: a non-standard radius table needs a ruling entry"
        if b["depth"]["preset"].startswith("glass"):
            assert any("毛玻璃" in x for x in b["needs_ruling"]), f"{b['id']}: glass on controls needs a ruling entry"


def test_registry_has_status_and_no_unverified_url():
    items = json.loads((REFS / "reference-sites.json").read_text(encoding="utf-8"))["items"]
    assert len(items) >= 50
    for it in items:
        assert it["status"] in {"ok", "blocked", "login-wall", "js-rendered", "unreachable", "redirect-other"}
        assert it["url"].startswith("https://")
        assert it["verified_at"]
