#!/usr/bin/env python3
"""Check (default) or copy the code blocks the Luz skills share, byte for byte.

Luz-Design holds the master copy of two blocks; edit them here only, then copy them with --write:

  rule-card core   scripts/context.py, between the "shared rule-card core" marker lines
                   → Luz-System, Luz-Dev scripts/context.py and Luz-Writing scripts/06-context.py
  notes store      scripts/experience.py, between the "notes store" marker lines
                   → Luz-System scripts/experience.py, Luz-Dev scripts/record_experience.py, Luz-Writing scripts/04-experience.py

  py -X utf8 scripts/sync_rule_core.py            report SAME or DIFF for every sibling copy; exit 1 when any differs
  py -X utf8 scripts/sync_rule_core.py --write    replace each sibling's block with this one (writes into the other repos)

Only the text between the marker lines is replaced; each skill keeps its own docstring, commands and data. A copy keeps
its own line endings.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve()
SKILL_ROOT = SOURCE.parents[1]
START = b"# ---- shared rule-card core"
END = b"# ---- end of shared rule-card core"
TARGETS = {
    "Luz-System": "scripts/context.py",
    "Luz-Dev": "scripts/context.py",
    "Luz-Writing": "scripts/06-context.py",
}
BLOCKS = (
    ("rule-card core", "scripts/context.py", START, END, TARGETS),
    ("notes store", "scripts/experience.py",
     b"# ---------------------------------------------------------------- notes store",
     b"# ---------------------------------------------------------------- end of notes store",
     {"Luz-System": "scripts/experience.py", "Luz-Dev": "scripts/record_experience.py", "Luz-Writing": "scripts/04-experience.py"}),
)


def core(data: bytes, start: bytes = START, end: bytes = END) -> tuple[int, int]:
    first = data.index(start)
    last = data.index(end)
    last = data.index(b"\n", last) + 1
    return first, last


def unix(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report which copies differ without writing (the default)")
    mode.add_argument("--write", action="store_true", help="copy this skill's blocks into every sibling that differs")
    args = parser.parse_args(argv)
    differ = 0
    for name, master, start, end, targets in BLOCKS:
        source = (SKILL_ROOT / master).read_bytes()
        s0, s1 = core(source, start, end)
        block = unix(source[s0:s1])
        for skill, rel in targets.items():
            target = SKILL_ROOT.parent / skill / rel
            if not target.is_file():
                print(f"SKIP {skill} {name}: {target} not found")
                continue
            data = target.read_bytes()
            t0, t1 = core(data, start, end)
            if unix(data[t0:t1]) == block:
                print(f"SAME {skill} {name}")
                continue
            differ += 1
            if args.write:
                copy = block.replace(b"\n", b"\r\n") if b"\r\n" in data else block
                target.write_bytes(data[:t0] + copy + data[t1:])
                print(f"SYNCED {skill} {name}: {target}")
            else:
                print(f"DIFF {skill} {name}: {target}")
    if differ and not args.write:
        print("run with --write to copy the Luz-Design blocks into the copies that differ")
    return 1 if differ and not args.write else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
