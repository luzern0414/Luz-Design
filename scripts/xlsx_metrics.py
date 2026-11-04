"""Shared sizing rules for spreadsheets: the builder uses them to size, the checker to prove nothing is clipped.

Excel never grows a row to fit wrapped text that was written by a library, so a row height that is a little too small hides
the last line. Both sides therefore use the same conservative estimate: CJK characters count 2 units, everything else 1;
a column of width W (in units of the Normal style's digit, which is the body font) shows about W - 2.5 units of text per line (cell padding), 2 units less per indent level; Latin words
that do not fit move whole to the next line, so capacity is reduced by 6 %; one line of 12 pt Microsoft YaHei needs about
1.5 x the size in points, plus 0.6 x the size of padding (10 pt text: 21 pt for one line, 36 pt for two). Explicit line breaks always start a new line.
"""
from __future__ import annotations

import math
import unicodedata

LINE_RATIO = 1.5
PAD_RATIO = 0.6
MIN_ROW_RATIO = 2.1
PADDING_UNITS = 2.5
WORD_LOSS = 0.94


def display_width(value) -> int:
    if value is None:
        return 0
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(value))


def capacity(width_units: float, indent: int = 0) -> float:
    return max(4.0, (width_units - PADDING_UNITS - 2 * indent) * WORD_LOSS)


def wrapped_lines(text, width_units: float, indent: int = 0) -> int:
    if text in (None, ""):
        return 1
    cap = capacity(width_units, indent)
    return sum(max(1, math.ceil(display_width(part) / cap)) for part in str(text).split("\n"))


def row_height(lines: int, size: float = 10) -> float:
    """Row height in points for ``lines`` lines of ``size`` pt Microsoft YaHei: 15 pt a line at 10 pt plus 6 pt, never under 21 pt."""
    return max(round(MIN_ROW_RATIO * size), round(LINE_RATIO * size) * lines + round(PAD_RATIO * size))


def is_numeric_type(kind: str) -> bool:
    return kind in {"money", "number", "decimal", "days", "percent", "date"}
