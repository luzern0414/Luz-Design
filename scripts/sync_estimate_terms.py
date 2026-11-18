#!/usr/bin/env python3
"""Check (default) or copy scripts/estimate_terms.py into the other Luz skills, byte for byte.

``estimate_terms.py`` is the one list of words of the 预算、人日与报价政策 (who cannot be the person who supplied a price, the workday and money words, the currency
and non-currency units, the evidence prefix). Luz-Design holds the master copy. Whoever changes it must change the copies the other skills read **in the same change**:

* Luz-System   scripts/estimate_terms.py   read by features_check.py (hours only with workdays on; basis; no invented price) and hw_export.py
* Luz-Writing  scripts/estimate_terms.py   read by 09-text_check.py (a proposal carries no amount or workday unless the switch is on and the evidence is there)
* Luz-Project  scripts/estimate_terms.py   read by the client-document validators (config/documents.json estimate switches, quote.json evidence)

and update the digest test in each skill (``estimate_terms.terms_digest()`` of the copy must equal the master's; each skill keeps a test that compares them).

  py -X utf8 scripts/sync_estimate_terms.py                    report SAME, DIFF or MISSING for every copy; exit 1 when any differs
  py -X utf8 scripts/sync_estimate_terms.py --write            replace every copy that differs with this skill's file (writes into the other repos)
  py -X utf8 scripts/sync_estimate_terms.py --only Luz-System  limit either mode to the named skills (repeatable)

Whole-file copy: the file has no part that belongs to one skill. A copy that was edited by hand reports DIFF and is overwritten by ``--write``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "estimate_terms.py"
SKILL_ROOT = SOURCE.parents[1]
TARGETS = {
    "Luz-System": "scripts/estimate_terms.py",
    "Luz-Writing": "scripts/estimate_terms.py",
    "Luz-Project": "scripts/estimate_terms.py",
}


def main(argv: list[str] | None = None, skills_root: Path | None = None, source: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report which copies differ without writing (the default)")
    mode.add_argument("--write", action="store_true", help="copy this skill's estimate_terms.py into every copy that differs")
    parser.add_argument("--only", action="append", choices=sorted(TARGETS), help="limit to these skills (repeatable)")
    args = parser.parse_args(argv)
    master = (source or SOURCE).read_bytes()
    root = skills_root or SKILL_ROOT.parent
    differ = 0
    for skill, rel in TARGETS.items():
        if args.only and skill not in args.only:
            continue
        target = root / skill / rel
        if target.is_file() and target.read_bytes() == master:
            print(f"SAME {skill}")
            continue
        differ += 1
        state = "DIFF" if target.is_file() else "MISSING"
        if args.write:
            if not target.parent.is_dir():
                print(f"SKIP {skill}: {target.parent} not found")
                continue
            target.write_bytes(master)
            print(f"SYNCED {skill}: {target}")
        else:
            print(f"{state} {skill}: {target}")
    if differ and not args.write:
        print("run with --write to copy Luz-Design's estimate_terms.py into the copies that differ")
    return 1 if differ and not args.write else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
