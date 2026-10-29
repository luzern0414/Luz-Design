#!/usr/bin/env python3
"""Check (default) or copy the shared rule-card core of scripts/context.py into the other Luz skills, byte for byte.

Luz-Design holds the master copy of the code between the two "shared rule-card core" marker lines. Edit it here only,
then copy it into Luz-System, Luz-Dev and Luz-Writing with --write; their own validators fail while a copy differs.

  py -X utf8 scripts/sync_rule_core.py            report SAME or DIFF for every sibling copy; exit 1 when any differs
  py -X utf8 scripts/sync_rule_core.py --write    replace each sibling's core with this one (writes into the other repos)

Only the text between the two marker lines is replaced; each skill keeps its own docstring and cards.json.
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


def core(data: bytes) -> tuple[int, int]:
    start = data.index(START)
    end = data.index(END)
    end = data.index(b"\n", end) + 1
    return start, end


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report which copies differ without writing (the default)")
    mode.add_argument("--write", action="store_true", help="copy this skill's core into every sibling that differs")
    args = parser.parse_args(argv)
    source = (SKILL_ROOT / "scripts" / "context.py").read_bytes()
    s0, s1 = core(source)
    block = source[s0:s1]
    differ = 0
    for skill, rel in TARGETS.items():
        target = SKILL_ROOT.parent / skill / rel
        if not target.is_file():
            print(f"SKIP {skill}: {target} not found")
            continue
        data = target.read_bytes()
        t0, t1 = core(data)
        if data[t0:t1] == block:
            print(f"SAME {skill}")
            continue
        differ += 1
        if args.write:
            target.write_bytes(data[:t0] + block + data[t1:])
            print(f"SYNCED {skill}: {target}")
        else:
            print(f"DIFF {skill}: {target}")
    if differ and not args.write:
        print("run with --write to copy the Luz-Design core into the copies that differ")
    return 1 if differ and not args.write else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
