"""Topic colours for Office tables; old specs without a theme use neutral fills."""
import json
from pathlib import Path

THEMES = Path(__file__).resolve().parents[1] / "references" / "themes.json"


def table_tint(theme: str | None) -> str:
    if not theme:
        return "F4F4F5"
    themes = json.loads(THEMES.read_text(encoding="utf-8"))["themes"]
    if theme not in themes:
        raise ValueError(f"Unknown theme {theme!r}; choose a topic theme from references/themes.json")
    return themes[theme]["actionTint"].lstrip("#")
