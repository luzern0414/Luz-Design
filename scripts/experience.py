#!/usr/bin/env python3
"""Luz Design experience library: search at the start of every call, note what was learned before it ends.

experience/preferences.json  what this user wants (general, no personal data), at most 60 entries
experience/lessons.json      reusable fixes and judgements learned from failures or corrections, at most 120
experience/patterns.json     effective knowledge: 功能, 交互流程, 组件, 色彩, 字阶, 前端规则, 设计理念, 调研经验 (at most 200)
experience/sources.json      verified references (LuzCrawl captures and official specification pages)
experience/catalog.md        readable catalog generated from all files after every write

Every entry has a stable key. `note` upserts by key: the same key replaces the old statement in place and
keeps one `previous` for audit, so a topic never has two entries. Stores are capped; `prune` drops the least
valuable entries (fewest uses, then oldest confirmation) and `check` fails on duplicate keys, near-duplicate
statements, cap overflow and personal data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
EXP = SKILL_ROOT / "experience"
SOURCES = EXP / "sources.json"
PATTERNS = EXP / "patterns.json"
PREFERENCES = EXP / "preferences.json"
LESSONS = EXP / "lessons.json"
CATALOG = EXP / "catalog.md"
KINDS = ["功能", "交互流程", "组件", "色彩", "字阶", "前端规则", "设计理念", "调研经验"]
CATEGORIES = ["页面结构", "交互流程", "组件状态", "前端规则"]
STALE_DAYS = 180
CAPS = {"preference": 60, "lesson": 120, "fact": 200}
NOTE_KINDS = {"preference": "偏好", "lesson": "教训", "fact": "有效信息"}
KEY_RE = re.compile(r"^[0-9a-z一-鿿][0-9a-z一-鿿-]{1,63}$")
PRIVATE_RES = [
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "phone number"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "email address"),
    (re.compile(r"[A-Za-z]:\\Users\\|/Users/|/home/", re.I), "private path"),
    (re.compile(r"微信号|wxid_", re.I), "WeChat ID"),
    (re.compile(r"(?:api[_-]?key|secret|password|token)\s*[:=]", re.I), "credential"),
]


def load(path: Path, key: str) -> dict:
    if not path.is_file():
        return {"schema_version": "1.0", key: []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def next_id(items: list[dict], prefix: str) -> str:
    numbers = [int(i["id"].split("-")[1]) for i in items if re.fullmatch(prefix + r"-\d+", i.get("id", ""))]
    return f"{prefix}-{max(numbers, default=0) + 1:03d}"


def age_days(day: str | None) -> int | None:
    try:
        return (date.today() - date.fromisoformat(day)).days
    except (TypeError, ValueError):
        return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def today() -> str:
    return date.today().isoformat()


def normalize(text: str) -> str:
    """Comparison form of a statement: lower case, without whitespace or punctuation."""
    return re.sub(r"[\W_]+", "", (text or "").lower())


def store(kind: str) -> tuple[Path, str]:
    return {"preference": (PREFERENCES, "preferences"), "lesson": (LESSONS, "lessons"), "fact": (PATTERNS, "patterns")}[kind]


def statement(entry: dict) -> str:
    return entry.get("text") or entry.get("summary") or ""


def confirmed(entry: dict) -> str:
    return entry.get("last_confirmed") or entry.get("last_used") or entry.get("first_seen") or "0000-00-00"


# ---------------------------------------------------------------- search

def matches(entry: dict, args) -> bool:
    blob = json.dumps(entry, ensure_ascii=False)
    if args.kind and entry.get("kind") != args.kind and entry.get("category") != args.kind:
        return False
    if args.industry and not any(args.industry in x or x == "通用" for x in entry.get("industries", ["通用"])):
        return False
    if args.surface and not any(args.surface in x or x == "通用" for x in entry.get("surfaces", ["通用"])):
        return False
    return all(term in blob for term in (args.text or "").split())


def cmd_search(args) -> int:
    notes = []
    if not args.kind and not args.industry and not args.surface:
        for kind in ("preference", "lesson"):
            path, field = store(kind)
            notes += [(kind, e) for e in load(path, field)[field] if matches(e, args)]
    for kind, e in notes:
        print(f"{e['id']} [{NOTE_KINDS[kind]}] {e['key']}: {e['text']}")
    patterns = [p for p in load(PATTERNS, "patterns")["patterns"] if matches(p, args)]
    sources = [s for s in load(SOURCES, "sources")["sources"] if matches(s, args)]
    for p in patterns:
        print(f"{p['id']} [{p['kind']}] {p['title']}  ({'、'.join(p.get('surfaces', []))} · {'、'.join(p.get('industries', []))})")
        print(f"    {p.get('summary', '')}")
    for s in sources:
        age = age_days(s.get("captured_at"))
        flag = "可复用" if s.get("snapshot") and age is not None and age <= STALE_DAYS else ("仅作知识" if not s.get("snapshot") else "已过期，需重新采集")
        print(f"{s['id']} [{s['category']}] {s['title']}  {s['url']}  {s.get('captured_at')} {flag}")
    print(f"共 {len(notes)} 条偏好与教训，{len(patterns)} 条模式，{len(sources)} 条来源")
    return 0


# ---------------------------------------------------------------- note: upsert by key, bounded stores

def upsert_pattern(patterns: list[dict], entry: dict, session: str) -> bool:
    """Replace the pattern with the same key (or the same kind and title), or add it. Returns True when replaced."""
    for p in patterns:
        same_key = bool(entry.get("key")) and p.get("key") == entry["key"]
        if same_key or (p["kind"] == entry["kind"] and p["title"] == entry["title"]):
            if p.get("summary") and normalize(p["summary"]) != normalize(entry.get("summary", "")):
                p["previous"] = {"summary": p["summary"], "until": today()}
            p.update({k: v for k, v in entry.items() if k not in {"id", "sessions", "first_seen", "uses"}})
            if session not in p.setdefault("sessions", []):
                p["sessions"].append(session)
            p["uses"] = p.get("uses", 0) + 1
            p["last_used"] = today()
            return True
    entry.update({"id": next_id(patterns, "PAT"), "sessions": [session], "first_seen": today(),
                  "last_used": today(), "uses": 1})
    patterns.append(entry)
    return False


def upsert_note(items: list[dict], key: str, text: str, why: str | None, prefix: str) -> tuple[dict, bool]:
    """Replace the entry with this key in place, or add one. Returns (entry, replaced)."""
    for e in items:
        if e.get("key") == key:
            if normalize(e["text"]) != normalize(text):
                e["previous"] = {"text": e["text"], "until": today()}
            e["text"] = text
            if why:
                e["why"] = why
            e["uses"] = e.get("uses", 0) + 1
            e["last_confirmed"] = today()
            return e, True
    e = {"id": next_id(items, prefix), "key": key, "text": text, "first_seen": today(), "last_confirmed": today(), "uses": 1}
    if why:
        e["why"] = why
    items.append(e)
    return e, False


def prune_items(items: list[dict], cap: int, keep: dict | None = None) -> list[dict]:
    """Drop the least valuable entries above the cap: fewest uses first, then oldest confirmation."""
    if len(items) <= cap:
        return []
    ranked = sorted((e for e in items if e is not keep), key=lambda e: (e.get("uses", 0), confirmed(e)))
    dropped = ranked[: len(items) - cap]
    gone = {id(e) for e in dropped}
    items[:] = [e for e in items if id(e) not in gone]
    return dropped


def private_hits(text: str) -> list[str]:
    return [label for regex, label in PRIVATE_RES if regex.search(text)]


def cmd_note(args) -> int:
    key = args.key.strip().lower()
    if not KEY_RE.match(key):
        raise SystemExit("FAIL: --key must be a short kebab or Chinese slug, e.g. table-header-centred or 表头居中")
    text = " ".join(args.text.split())
    hits = private_hits(text + " " + (args.why or ""))
    if hits:
        raise SystemExit(f"FAIL: the note contains a {hits[0]}; committed stores hold general principles only")
    path, field = store(args.kind)
    doc = load(path, field)
    items = doc[field]
    if args.kind == "fact":
        category = args.category or "调研经验"
        if category not in KINDS:
            raise SystemExit(f"FAIL: --category must be one of {KINDS}")
        entry = {"key": key, "kind": category, "title": args.title or key, "summary": text,
                 "industries": args.industry.split(",") if args.industry else ["通用"], "surfaces": ["通用"], "sources": []}
        if args.why:
            entry["details"] = {"依据": args.why}
        replaced = upsert_pattern(items, entry, "note")
        target = next(p for p in items if p.get("key") == key)
    else:
        target, replaced = upsert_note(items, key, text, args.why, "PREF" if args.kind == "preference" else "LES")
    clash = [e for e in items if e is not target and normalize(statement(e)) == normalize(text)]
    if clash:
        print(f"WARN the same statement is stored under {clash[0].get('key') or clash[0].get('id')}; keep one of them")
    dropped = prune_items(items, CAPS[args.kind], keep=target)
    save(path, doc)
    render()
    print(f"{'replaced' if replaced else 'added'} {NOTE_KINDS[args.kind]} {target['id']} {key}")
    for e in dropped:
        print(f"pruned {e.get('id')} {e.get('key') or e.get('title')}")
    return 0


def cmd_prune(_args) -> int:
    total = 0
    for kind in ("preference", "lesson", "fact"):
        path, field = store(kind)
        doc = load(path, field)
        dropped = prune_items(doc[field], CAPS[kind])
        if dropped:
            save(path, doc)
        for e in dropped:
            print(f"pruned {NOTE_KINDS[kind]} {e.get('id')} {e.get('key') or e.get('title')}")
        total += len(dropped)
        stale = [e for e in doc[field] if (age_days(confirmed(e)) or 0) > STALE_DAYS]
        if stale:
            print(f"candidates, not confirmed for {STALE_DAYS} days:", ", ".join(e.get("id", "?") for e in stale))
    render()
    print(f"pruned {total} entries")
    return 0


def cmd_list(args) -> int:
    for kind in [args.kind] if args.kind else ["preference", "lesson"]:
        path, field = store(kind)
        for e in load(path, field)[field]:
            if kind == "fact" and not e.get("key"):
                continue
            print(f"{e['id']} [{NOTE_KINDS[kind]}] {e.get('key')}: {statement(e)}  (使用 {e.get('uses', 1)} 次，最近 {confirmed(e)})")
    return 0


def check_store(items: list[dict], kind: str) -> list[str]:
    errors = []
    if len(items) > CAPS[kind]:
        errors.append(f"{NOTE_KINDS[kind]} store has {len(items)} entries, cap is {CAPS[kind]}; run prune")
    keys: dict[str, str] = {}
    texts: dict[str, str] = {}
    for e in items:
        eid = e.get("id", "?")
        if kind != "fact":
            for field in ("id", "key", "text", "first_seen", "last_confirmed"):
                if not e.get(field):
                    errors.append(f"{eid} missing {field}")
            if e.get("key") and not KEY_RE.match(e["key"]):
                errors.append(f"{eid} key {e['key']!r} is not a short kebab or Chinese slug")
            for what in private_hits(statement(e) + " " + e.get("why", "")):
                errors.append(f"{eid} contains a {what}")
        key = e.get("key")
        if key:
            if key in keys:
                errors.append(f"{eid} duplicates key {key} of {keys[key]}")
            keys.setdefault(key, eid)
        norm = normalize(statement(e))
        if norm:
            if norm in texts:
                errors.append(f"{eid} repeats the statement of {texts[norm]}")
            texts.setdefault(norm, eid)
    return errors


# ---------------------------------------------------------------- add, check, render

def cmd_add(args) -> int:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    patterns_doc = load(PATTERNS, "patterns")
    sources_doc = load(SOURCES, "sources")
    for s in data.get("sources", []):
        if not any(x["url"] == s["url"] for x in sources_doc["sources"]):
            s["id"] = next_id(sources_doc["sources"], "SRC")
            sources_doc["sources"].append(s)
    save(SOURCES, sources_doc)
    for p in data.get("patterns", []):
        if p.get("kind") not in KINDS:
            raise SystemExit(f"FAIL: kind must be one of {KINDS}: {p.get('title')}")
        upsert_pattern(patterns_doc["patterns"], p, data.get("session", "manual"))
    for e in prune_items(patterns_doc["patterns"], CAPS["fact"]):
        print(f"pruned {e.get('id')} {e.get('title')}")
    save(PATTERNS, patterns_doc)
    render()
    print(f"added {len(data.get('patterns', []))} patterns, {len(data.get('sources', []))} sources")
    return 0


def check() -> list[str]:
    errors = []
    sources = load(SOURCES, "sources")["sources"]
    patterns = load(PATTERNS, "patterns")["patterns"]
    ids = {s["id"] for s in sources}
    for s in sources:
        for key in ("id", "url", "title", "category", "evidence", "borrowable", "not_copyable", "captured_at"):
            if not s.get(key):
                errors.append(f"{s.get('id')} missing {key}")
        if s.get("category") not in CATEGORIES:
            errors.append(f"{s['id']} category must be one of {CATEGORIES}")
        if [x["url"] for x in sources].count(s["url"]) > 1:
            errors.append(f"{s['id']} duplicates {s['url']}")
    titles = [(p.get("kind"), p.get("title")) for p in patterns]
    for p in patterns:
        for key in ("id", "kind", "title", "summary"):
            if not p.get(key):
                errors.append(f"{p.get('id')} missing {key}")
        if p.get("kind") not in KINDS:
            errors.append(f"{p['id']} kind must be one of {KINDS}")
        if titles.count((p.get("kind"), p.get("title"))) > 1:
            errors.append(f"{p['id']} duplicates the title {p.get('title')}")
        for ref in p.get("sources", []):
            if ref not in ids:
                errors.append(f"{p['id']} cites unknown source {ref}")
    errors += check_store(patterns, "fact")
    errors += check_store(load(PREFERENCES, "preferences")["preferences"], "preference")
    errors += check_store(load(LESSONS, "lessons")["lessons"], "lesson")
    return errors


def cmd_check(_args) -> int:
    errors = check()
    sources = load(SOURCES, "sources")["sources"]
    stale = [s["id"] for s in sources if s.get("snapshot") and (age_days(s.get("captured_at")) or 0) > STALE_DAYS]
    for e in errors:
        print("ERROR", e)
    if stale:
        print("STALE (crawl again before relying on it):", ", ".join(stale))
    counts = (f"{len(load(PREFERENCES, 'preferences')['preferences'])} preferences, {len(load(LESSONS, 'lessons')['lessons'])} lessons, "
              f"{len(load(PATTERNS, 'patterns')['patterns'])} patterns, {len(sources)} sources")
    print("FAIL" if errors else "PASS", f"experience: {counts}")
    return 1 if errors else 0


def render() -> None:
    sources = load(SOURCES, "sources")["sources"]
    patterns = load(PATTERNS, "patterns")["patterns"]
    src = {s["id"]: s for s in sources}
    lines = ["# Luz Design 经验库", "",
             "每次调用开始先读本页并运行 `py -X utf8 scripts/experience.py search`：用户偏好与教训直接照做，能复用的配色、字阶与视觉、文件规则直接沿用，只为缺口做新的调研。结束前用 `note` 按主题键写入新的偏好、教训与有效信息，同一个键覆盖旧条目。本页由 `scripts/experience.py` 生成，修改请用命令或改 JSON。", ""]
    for kind, title in (("preference", "用户偏好"), ("lesson", "教训")):
        path, field = store(kind)
        items = load(path, field)[field]
        if not items:
            continue
        lines += [f"## {title}", ""]
        for e in sorted(items, key=lambda x: x["key"]):
            why = f"（{e['why']}）" if e.get("why") else ""
            lines.append(f"- **{e['key']}**：{e['text']}{why}　使用 {e.get('uses', 1)} 次，最近 {confirmed(e)}")
        lines.append("")
    for kind in KINDS:
        group = [p for p in patterns if p["kind"] == kind]
        if not group:
            continue
        lines += [f"## {kind}", ""]
        for p in group:
            lines.append(f"### {p['id']} {p['title']}")
            lines.append(f"- 适用：{'、'.join(p.get('surfaces', []))}；行业：{'、'.join(p.get('industries', []))}；使用 {p.get('uses', 1)} 次，最近 {p.get('last_used')}")
            lines.append(f"- 要点：{p['summary']}")
            for key, value in (p.get("details") or {}).items():
                if isinstance(value, list):
                    value = "；".join(map(str, value))
                elif isinstance(value, dict):
                    value = "；".join(f"{k} {v}" for k, v in value.items())
                lines.append(f"- {key}：{value}")
            refs = [src[r] for r in p.get("sources", []) if r in src]
            if refs:
                lines.append("- 依据：" + "；".join(f"[{r['title']}]({r['url']})" for r in refs))
            lines.append("")
    lines += ["## 来源", "", "| 编号 | 类别 | 来源 | 可借鉴 | 采集日期 | 复用 |", "|---|---|---|---|---|---|"]
    for s in sources:
        age = age_days(s.get("captured_at"))
        reuse = "可复用快照" if s.get("snapshot") and age is not None and age <= STALE_DAYS else ("知识，无快照" if not s.get("snapshot") else "已过期")
        lines.append(f"| {s['id']} | {s['category']} | [{s['title']}]({s['url']}) | {s['borrowable']} | {s['captured_at']} | {reuse} |")
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="find preferences, lessons, reusable patterns and sources")
    s.add_argument("--kind", choices=KINDS + CATEGORIES)
    s.add_argument("--industry")
    s.add_argument("--surface", choices=["小程序", "后台", "移动应用", "网页", "通用"])
    s.add_argument("--text", help="space-separated keywords, all must match")
    n = sub.add_parser("note", help="upsert a preference, lesson or fact by key; the same key replaces the old statement")
    n.add_argument("--kind", required=True, choices=list(NOTE_KINDS))
    n.add_argument("--key", required=True, help="stable topic slug, e.g. table-header-centred or 表头居中")
    n.add_argument("--text", required=True, help="the general principle, not task trivia")
    n.add_argument("--why", help="reason or evidence")
    n.add_argument("--category", help="facts only: pattern kind (default 调研经验)")
    n.add_argument("--title", help="facts only: catalog title (default the key)")
    n.add_argument("--industry", help="facts only: comma-separated industries (default 通用)")
    lst = sub.add_parser("list", help="list preferences and lessons, or keyed facts with --kind fact")
    lst.add_argument("--kind", choices=list(NOTE_KINDS))
    a = sub.add_parser("add", help="add curated patterns and knowledge sources from a JSON file")
    a.add_argument("file")
    sub.add_parser("prune", help="enforce the caps and list entries not confirmed for 180 days")
    sub.add_parser("check", help="validate fields, duplicate keys and statements, caps, personal data and stale sources")
    sub.add_parser("render", help="regenerate catalog.md")
    args = parser.parse_args(argv)
    if args.cmd == "render":
        render()
        return 0
    return {"search": cmd_search, "note": cmd_note, "list": cmd_list, "add": cmd_add, "prune": cmd_prune,
            "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
