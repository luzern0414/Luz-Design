#!/usr/bin/env python3
"""Check (default) or copy the Markdown type block of references/md-type.css into the other Luz skills, byte for byte.

Reading pages in every skill (rule pages, reports, architecture and design documents, hardware lists, article templates) share one
text hierarchy: body, six heading levels, lists, quotes, tables, captions and code, in two size sets (phone under 768 px, desktop from
768 px). Luz-Design holds the master in references/md-type.css; each other stylesheet carries the same block between the two marker
comments `luz-md-type:start` and `luz-md-type:end`. Edit the master only, then copy it with --write; the skills' validators fail while
a copy differs.

  py -X utf8 scripts/sync_md_type.py            report SAME or DIFF for every copy; exit 1 when any differs or a marker is missing
  py -X utf8 scripts/sync_md_type.py --write    replace each copy with the master (writes into the other repos)
  py -X utf8 scripts/sync_md_type.py --only Luz-Dev [--write]    only one skill's copies

A target is either a "block" (the text between the markers inside the skill's own stylesheet or page) or a "file" (a whole copy of
md-type.css that a generator reads at run time). A block target without markers is reported MISSING: put the two marker comments
where the block belongs (after the page's resets, before its component rules), then run --write.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve()
SKILL_ROOT = SOURCE.parents[1]
MASTER = SKILL_ROOT / "references" / "md-type.css"
CRLF = chr(13) + chr(10)
LF = chr(10)
START = "/* luz-md-type:start"
END = "/* luz-md-type:end */"
# (skill, path inside the skill, kind)
TARGETS = [
    ("Luz-Design", "references/guidelines.css", "block"),
    ("Luz-Design", "references/templates.txt", "block"),
    ("Luz-System", "references/guidelines.css", "block"),
    ("Luz-System", "references/md-type.css", "file"),
    ("Luz-System", "references/templates.txt", "block"),
    ("Luz-Dev", "assets/shared/luz-reading.css", "block"),
    ("Luz-Crawl", "lib/formal-report.css", "block"),
    ("Luz-Writing", "assets/01-article-template.html", "block"),
    ("Luz-Project", "scripts/reading_style.py", "block"),
    # 汇总页生成器：每个技能一份同样的脚本，样式块随母本同步
    ("Luz-Design", "scripts/make_summary.py", "block"),
    ("Luz-System", "scripts/make_summary.py", "block"),
    ("Luz-Dev", "scripts/make_summary.py", "block"),
    ("Luz-Crawl", "scripts/make_summary.py", "block"),
    ("Luz-Writing", "scripts/make_summary.py", "block"),
    ("Luz-Ops", "scripts/make_summary.py", "block"),
    ("Luz-Project", "scripts/make_summary.py", "block"),
]


def read(path: Path) -> tuple[str, bool]:
    """The text with LF line ends, and whether the file used CRLF (so a write keeps the file's own line ends)."""
    raw = path.read_bytes().decode("utf-8")
    return raw.replace(CRLF, LF), CRLF in raw


def write(path: Path, text: str, crlf: bool) -> None:
    path.write_bytes((text.replace(LF, CRLF) if crlf else text).encode("utf-8"))


def blocks_of(text: str) -> list[tuple[int, int]]:
    """Every marker pair of a file, in order (a templates file can hold the block twice, once per page skeleton)."""
    found, at = [], 0
    while True:
        start = text.find(START, at)
        if start < 0:
            return found
        end = text.find(END, start)
        if end < 0:
            return found
        found.append((start, end + len(END)))
        at = end + len(END)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report which copies differ without writing (the default)")
    mode.add_argument("--write", action="store_true", help="copy the master into every copy that differs")
    parser.add_argument("--only", action="append", default=[], metavar="SKILL", help="limit to one skill, e.g. Luz-Dev (repeatable)")
    args = parser.parse_args(argv)
    master_text, _ = read(MASTER)
    span = (blocks_of(master_text) or [None])[0]
    if span is None:
        print(f"ERROR master {MASTER} has no luz-md-type markers")
        return 1
    block = master_text[span[0]:span[1]]
    bad = 0
    missing = 0
    for skill, rel, kind in TARGETS:
        if args.only and skill not in args.only:
            continue
        target = SKILL_ROOT.parent / skill / rel
        label = f"{skill}/{rel}"
        if not target.is_file():
            if kind == "file" and args.write:
                write(target, master_text, False)
                print(f"SYNCED {label}: created")
                continue
            print(f"SKIP {label}: not found")
            continue
        text, crlf = read(target)
        if kind == "file":
            if text == master_text:
                print(f"SAME {label}")
            else:
                bad += 1
                if args.write:
                    write(target, master_text, crlf)
                    print(f"SYNCED {label}")
                else:
                    print(f"DIFF {label}")
            continue
        found = blocks_of(text)
        if not found:
            missing += 1
            print(f"MISSING {label}: no luz-md-type markers")
            continue
        if all(text[a:b] == block for a, b in found):
            print(f"SAME {label}" + (f" ({len(found)} blocks)" if len(found) > 1 else ""))
            continue
        bad += 1
        if args.write:
            for a, b in reversed(found):
                text = text[:a] + block + text[b:]
            write(target, text, crlf)
            print(f"SYNCED {label}")
        else:
            print(f"DIFF {label}")
    if bad and not args.write:
        print("Run py -X utf8 scripts/sync_md_type.py --write after editing references/md-type.css, or add the markers where a MISSING target belongs.")
    return 1 if missing or (bad and not args.write) else 0


if __name__ == "__main__":
    sys.exit(main())
