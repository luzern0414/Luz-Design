#!/usr/bin/env python3
"""设计路径与思考链的命令行：查阶段与思考工具、生成可粘进 BRIEF 的检查表、生成标准格式的偏离说明。

    py -X utf8 scripts/design_path.py list
    py -X utf8 scripts/design_path.py show <P0..P9 | 思考工具 id | 总原则 id | order | floor | deviation | signature | example | surfaces | project | basis>
    py -X utf8 scripts/design_path.py checklist [--surface miniprogram|admin|website|agent] [--format md|json] [--detail]
    py -X utf8 scripts/design_path.py deviation <规则 id> --why … --risk … --verify … [--strength default|hint] [--json]
    py -X utf8 scripts/design_path.py render [--write | --check]       由数据文件生成规则页 references/design-path.html

数据源是 references/design-path.json（规则页 references/design-path.html 由它渲染而来，渲染与否由测试核对）。
规则强度三档与偏离说明字段沿用页面范式库（references/page-patterns.json 的 method）。
退出码：deviation 遇到 must 规则为 2；render --check 发现规则页与数据不一致为 1；输入有误为 2。
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_PATH = ROOT / "references" / "design-path.json"
PAGE_PATH = ROOT / "references" / "design-path.html"
PATTERNS_PATH = ROOT / "references" / "page-patterns.json"
SURFACES = ["miniprogram", "admin", "website", "agent"]
STRENGTH = {"must": "硬规则", "default": "默认", "hint": "建议"}
BASIS_KIND = {"internal": "技能内部规则", "convention": "通行做法", "pending": "待外部资料核对"}

_CACHE: dict[str, Any] = {}


def load(path: Path | None = None) -> dict:
    path = path or DATA_PATH
    key = str(path)
    if key not in _CACHE:
        _CACHE[key] = json.loads(path.read_text(encoding="utf-8"))
    return _CACHE[key]


def plain(text: str) -> str:
    return text.replace("`", "")


def resolve_pp(ref: str) -> Any:
    """pp:method.five_questions 之类的引用，取页面范式库里对应的值。"""
    node: Any = load(PATTERNS_PATH)
    for part in ref.removeprefix("pp:").split("."):
        node = node[part]
    return node


def steps_of(tool: dict) -> list[str]:
    return list(tool["steps"]) if "steps" in tool else list(resolve_pp(tool["steps_from"]))


def all_ids(data: dict) -> dict[str, tuple[str, dict]]:
    ids: dict[str, tuple[str, dict]] = {}
    for kind, items in (("phase", data["phases"]), ("tool", data["thinking_tools"]), ("principle", data["principles"])):
        for item in items:
            ids[item["id"].lower()] = (kind, item)
    return ids


def rule_of(rule_id: str) -> tuple[str, str] | None:
    """规则 id 的 (强度, 原文)：先找页面范式库，再找本路径的总原则与底线。"""
    for r in load(PATTERNS_PATH)["rules"]:
        if r["id"] == rule_id:
            return r["strength"], r["text"]
    data = load()
    for p in data["principles"]:
        if p["id"] == rule_id:
            return p["strength"], p["text"]
    for f in data["hard_floor"]:
        if f["id"] == rule_id:
            return "must", f["text"]
    return None


# ---------------------------------------------------------------- 文字输出

def fmt_ref(ref: str) -> str:
    kind, _, val = ref.partition(":")
    return {
        "card": f"规则卡 {val}（context.py {val}）",
        "script": f"scripts/{val}",
        "file": val,
        "ext": val,
        "out": f"{val}（会话文件）",
        "pp": f"页面范式库 {val}",
    }.get(kind, ref)


def show_phase(p: dict) -> list[str]:
    out = [f"{p['id']} {p['name']}", f"  目的：{plain(p['purpose'])}", "  读：" + "；".join(p["inputs"]), "  思考链："]
    out += [f"    {i}. {plain(c)}" for i, c in enumerate(p["chain"], 1)]
    out.append("  做什么：")
    out += [f"    - {plain(a['do'])}  ->  {fmt_ref(a['tool'])}" for a in p["actions"]]
    out.append("  产出：")
    out += [f"    - {o['file']}：{plain(o['what'])}" for o in p["outputs"]]
    out.append("  检查：")
    out += [f"    - {plain(c)}" for c in p["checks"]]
    out += [f"    $ {c}" for c in p["commands"]]
    out.append("  可偏离处：")
    out += [f"    - {plain(c)}" for c in p["may_deviate"]]
    out.append(f"  交给下一阶段：{plain(p['handoff'])}")
    if p.get("pending_refs"):
        out.append("  待补位置：" + "；".join(f"{r['slot']}（{r['ref']}，{r['status']}）" for r in p["pending_refs"]))
    out.append("  常见失误：")
    out += [f"    - 症状：{x['symptom']}；原因：{x['cause']}；怎么修：{x['fix']}" for x in p["pitfalls"]]
    return out


def show_tool(t: dict) -> list[str]:
    out = [f"{t['id']} {t['name']}", f"  何时用：{plain(t['when'])}", "  怎么用："]
    out += [f"    {i}. {plain(s)}" for i, s in enumerate(steps_of(t), 1)]
    if t.get("example"):
        out.append(f"  例：{plain(t['example'])}")
    return out


def show_special(data: dict, key: str) -> list[str] | None:
    if key in ("order", "decision-order"):
        out = ["冲突裁决顺序（靠前的赢）："]
        out += [f"  {i}. {k}：{data['decision_notes'][k]}" for i, k in enumerate(data["decision_order"], 1)]
        return out
    if key == "floor":
        return ["七条底线（must，不偏离）："] + [f"  {i}. {f['id']}：{f['text']}" for i, f in enumerate(data["hard_floor"], 1)]
    if key == "deviation":
        d = data["deviation_template"]
        return ["偏离说明字段：" + "、".join(d["fields"]), "示例：" + d["example"], "生成：design_path.py deviation <规则 id> --why … --risk … --verify …"]
    if key == "signature":
        s = data["signature_budget"]
        return [s["rule"], "例："] + [f"  - {e}" for e in s["examples"]] + ["不算记忆点：" + "；".join(s["not_signature"])]
    if key == "example":
        w = data["worked_example"]
        out = [plain(w["brief"])]
        for s in w["steps"]:
            out.append(f"{s['phase']}  问：{s['ask']}\n      答：{s['answer']}")
            if s["deviation"] != "—":
                out.append(f"      偏离：{s['deviation']}")
        return out
    if key == "surfaces":
        out: list[str] = []
        for sid in SURFACES:
            s = data["surfaces"][sid]
            out.append(f"{sid}（{s['name']}）")
            out += [f"  {ph}：{plain(txt)}" for ph, txt in s["phase_notes"].items()]
        return out
    if key == "project":
        m = data["project_mode"]
        out = [f"项目模式阶段：{m['stage']}", "读："] + [f"  - {plain(x)}" for x in m["reads"]]
        out += ["写："] + [f"  - {plain(x)}" for x in m["writes"]]
        out += ["各阶段落进前端界面设计文档的哪些类："] + [f"  - {x['phase']}：{x['doc']}" for x in m["phase_to_doc"]]
        return out + ["停下来问人："] + [f"  - {plain(x)}" for x in m["stop_points"]]
    if key == "basis":
        return [f"[{BASIS_KIND[b['kind']]}] {b['item']}：{plain(b['note'])}" for b in data["basis"]]
    return None


def cmd_list(args, data: dict) -> int:
    print(f"设计路径：{len(data['phases'])} 个阶段")
    for p in data["phases"]:
        print(f"  {p['id']}  {p['name']:<10} 产出 {p['outputs'][0]['file']}")
    print(f"思考工具：{len(data['thinking_tools'])} 个")
    for t in data["thinking_tools"]:
        print(f"  {t['id']:<16} {t['name']:<10} {plain(t['when'])}")
    counts = {k: sum(1 for p in data["principles"] if p["strength"] == k) for k in STRENGTH}
    print(f"总原则：{len(data['principles'])} 条（" + "、".join(f"{k} {n}" for k, n in counts.items()) + "）：" + "、".join(p["id"] for p in data["principles"]))
    print("冲突裁决顺序：" + " > ".join(data["decision_order"]))
    pend = [r["slot"] for p in data["phases"] for r in p.get("pending_refs", [])]
    if pend:
        print("待补位置（细则规则页写入后回填）：" + "、".join(pend))
    print("show 可查：阶段、工具、总原则 id，或 order / floor / deviation / signature / example / surfaces / project / basis")
    return 0


def cmd_show(args, data: dict) -> int:
    key = args.id.strip()
    found = all_ids(data).get(key.lower())
    if found is None:
        for kind, items in (("phase", data["phases"]), ("tool", data["thinking_tools"])):
            for item in items:
                if item["name"] == key:
                    found = (kind, item)
    if found is not None:
        kind, item = found
        lines = show_phase(item) if kind == "phase" else show_tool(item) if kind == "tool" else [
            f"{item['id']}（{STRENGTH[item['strength']]}，{item['strength']}）：{plain(item['text'])}"]
        if kind == "principle" and item["id"] == "hard-floor":
            lines += show_special(data, "floor") or []
        print("\n".join(lines))
        return 0
    lines = show_special(data, key.lower())
    if lines is None:
        print(f"没有 {key}；先运行 list", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


# ---------------------------------------------------------------- 检查表

def checklist_rows(data: dict) -> list[dict]:
    return [{"phase": p["id"], "name": p["name"], "outputs": [o["file"] for o in p["outputs"]],
             "checks": p["commands"] or [plain(c) for c in p["checks"]], "done": False, "deviation": ""} for p in data["phases"]]


def cmd_checklist(args, data: dict) -> int:
    rows = checklist_rows(data)
    surface = data["surfaces"].get(args.surface) if args.surface else None
    if args.format == "json":
        print(json.dumps({"surface": args.surface, "rows": rows,
                          "surface_notes": surface["phase_notes"] if surface else {}}, ensure_ascii=False, indent=2))
        return 0
    title = "## 设计路径检查表" + (f"（{surface['name']}）" if surface else "")
    out = [title, "",
           "每阶段结束勾一次；偏离列写规则 id，并用 `py -X utf8 scripts/design_path.py deviation <规则 id> --why … --risk … --verify …` 生成偏离说明。", "",
           "| 阶段 | 产出 | 检查 | 完成 | 偏离说明 |", "|---|---|---|---|---|"]
    for r in rows:
        outs = "<br>".join(f"`{o}`" for o in r["outputs"])
        checks = "<br>".join(f"`{c}`" if c.startswith(("py ", "python ", "node ")) else c for c in r["checks"])
        out.append(f"| {r['phase']} {r['name']} | {outs} | {checks} | [ ] | — |")
    if args.detail:
        out += ["", "### 逐项检查", ""]
        out += [f"- [ ] {p['id']}：{plain(c)}" for p in data["phases"] for c in p["checks"]]
    if surface:
        out += ["", f"### 本端注意（{surface['name']}）", ""]
        out += [f"- {ph}：{plain(txt)}" for ph, txt in surface["phase_notes"].items()]
    out += ["", "### 本次沉淀（提示）", "",
            "结束前用 `py -X utf8 scripts/experience.py note --kind preference|lesson|fact --key … --text …` 写入：用户新说的偏好、规则纠正、有效或失败的做法、调研来源与范围；key 列进 BRIEF 的“本次沉淀”。"]
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------- 偏离说明

def make_deviation(rule_id: str, why: str, risk: str, verify: str, strength: str | None = None) -> tuple[dict, list[str]]:
    """返回 (偏离说明字典, 提示)；must 规则或字段为空时抛 ValueError。"""
    missing = [k for k, v in (("why", why), ("risk", risk), ("verify", verify)) if not v.strip()]
    if missing:
        raise ValueError("偏离说明缺 " + "、".join(missing))
    found = rule_of(rule_id)
    notes: list[str] = []
    if found:
        level, text = found
    else:
        level, text = strength or "default", ""
        notes.append(f"规则 {rule_id} 不在页面范式库和本路径的总原则里，按 {level} 记录；请确认它的出处与强度")
    if strength and found and strength != level:
        notes.append(f"{rule_id} 的强度是 {level}，忽略 --strength {strength}")
    if level == "must":
        raise ValueError(f"{rule_id} 是 must 规则，不许偏离，只能退回系统技能或换一种做法")
    if level == "hint":
        notes.append(f"{rule_id} 是 hint 级建议，按情境取舍，不必写偏离说明；仍按下面格式记录")
    return {"rule": rule_id, "strength": level, "rule_text": text, "why": why.strip(), "risk": risk.strip(), "verify": verify.strip()}, notes


def format_deviation(d: dict) -> str:
    head = f"规则：{d['rule']}（{d['strength']}）" + (f"：{d['rule_text']}" if d["rule_text"] else "")
    return "\n".join(["偏离说明", f"- {head}", f"- 为什么偏离：{d['why']}", f"- 风险：{d['risk']}", f"- 怎么验证：{d['verify']}"])


def cmd_deviation(args, data: dict) -> int:
    try:
        d, notes = make_deviation(args.rule, args.why, args.risk, args.verify, args.strength)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2
    for n in notes:
        print(f"注意：{n}", file=sys.stderr)
    if args.json:
        print(json.dumps({k: d[k] for k in ("rule", "why", "risk", "verify")}, ensure_ascii=False, indent=2))
    else:
        print(format_deviation(d))
    return 0


# ---------------------------------------------------------------- 规则页渲染

SECTIONS = [
    ("scope", "适用范围", '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><circle cx="12" cy="12" r="3"/>'),
    ("workflow", "工作流程", '<circle cx="6" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="M8 6h5a3 3 0 0 1 3 3v1M16 18h-5a3 3 0 0 1-3-3v-1"/><path d="m13 8 3 2 3-2M11 16l-3-2-3 2"/>'),
    ("rules", "核心规则", '<path d="M12 3 5 6v5c0 4.5 2.8 7.8 7 10 4.2-2.2 7-5.5 7-10V6l-7-3Z"/><path d="m9 12 2 2 4-5"/>'),
    ("platform-matrix", "平台矩阵", '<rect x="3" y="4" width="7" height="6" rx="1"/><rect x="14" y="4" width="7" height="6" rx="1"/><rect x="3" y="14" width="7" height="6" rx="1"/><rect x="14" y="14" width="7" height="6" rx="1"/>'),
    ("examples", "案例样本", '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m4 17 5-5 3 3 2-2 6 6"/>'),
    ("output-contract", "输出契约", '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5M9 12h6M9 16h6"/>'),
    ("quality-gates", "质量门禁", '<path d="M4 7h5M15 7h5M9 7a3 3 0 1 0 6 0 3 3 0 0 0-6 0ZM4 17h10M18 17h2M14 14a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/>'),
    ("handoff", "交接规则", '<path d="M4 7h12M13 4l3 3-3 3M20 17H8M11 14l-3 3 3 3"/>'),
]
SVG_OPEN = ('<svg class="icon-linear section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23E6F0F7'/%3E"
           "%3Cg fill='none' stroke='%23205B88' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='9' cy='9' r='2.5'/%3E"
           "%3Ccircle cx='23' cy='25' r='2.5'/%3E%3Cpath d='M11.5 9H18a4 4 0 0 1 0 8h-4a4 4 0 0 0 0 8h6.5'/%3E%3C/g%3E%3C/svg%3E")


LATIN_RUN = re.compile(r"(?<![A-Za-z0-9_])(?:--?)?[A-Za-z][A-Za-z0-9_\-]*(?:[./][A-Za-z0-9_\-]+)*")


def inline(text: str) -> str:
    """反引号包住的是代码；正文里其余连续的拉丁字母（编号、英文名、字段名）自动包成代码，规则页正文不留裸拉丁字母。"""
    out = []
    for part in re.split(r"(`[^`]*`)", text):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            out.append(f"<code>{html.escape(part[1:-1], quote=False)}</code>")
        else:
            pos = 0
            for m in LATIN_RUN.finditer(part):
                out.append(html.escape(part[pos:m.start()], quote=False))
                out.append(f"<code>{html.escape(m.group(0), quote=False)}</code>")
                pos = m.end()
            out.append(html.escape(part[pos:], quote=False))
    result = "".join(out)
    stray = re.search(r"[A-Za-z]", re.sub(r"<code>.*?</code>", "", result).replace("&lt;", "").replace("&gt;", "").replace("&amp;", ""))
    if stray:
        raise ValueError(f"规则页正文里有没包进代码的拉丁字母：{text[max(0, stray.start() - 12):stray.start() + 20]!r}")
    return result


def code(text: str) -> str:
    return f"<code>{html.escape(text, quote=False)}</code>"


def ref_html(ref: str) -> str:
    kind, _, val = ref.partition(":")
    if kind == "card":
        return f"规则卡 {code(val)}"
    if kind == "pp":
        return f"范式库 {code(val)}"
    if kind == "ext":
        first, _, rest = val.partition(" ")
        return code(Path(first).name + (" " + rest if rest else ""))
    return code(val.removeprefix("references/").removeprefix("raw/"))


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(items: list[str]) -> str:
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def numbered(items: list[str]) -> str:
    """表格单元格里的清单：编号加换行，不用列表标签（规则卡把单元格压成一行，列表标签的分隔会丢）。"""
    return "<br>".join(f"{i}. {item}" for i, item in enumerate(items, 1))


def table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>\n" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>\n{body}</tbody></table></div>'


def phase_html(p: dict) -> str:
    rows = [
        ("目的", inline(p["purpose"])),
        ("思考链", numbered([inline(c) for c in p["chain"]])),
        ("按序做", " → ".join(ref_html(a["tool"]) for a in p["actions"])),
        ("产出", numbered([f"{code(o['file'].removeprefix('raw/'))}：{inline(o['what'])}" for o in p["outputs"]])),
        ("检查", numbered([inline(c) for c in p["checks"]])),
        ("可偏离处", numbered([inline(c) for c in p["may_deviate"]])),
    ]
    body = "".join(f"<tr><th scope=\"row\">{k}</th><td>{v}</td></tr>\n" for k, v in rows)
    return f'<h4>{code(p["id"])} {inline(p["name"])}</h4>\n<div class="table-wrap"><table><tbody>\n{body}</tbody></table></div>'


def tool_row(t: dict) -> list[str]:
    steps = numbered([inline(s) for s in steps_of(t)])
    example = f"<br>例：{inline(t['example'])}" if t.get("example") and t.get("show_example") else ""
    return [f"{code(t['id'])}<br>{inline(t['name'])}<br>何时：{inline(t['when'])}", steps + example]


def sections_html(data: dict) -> dict[str, str]:
    pg = data["page"]
    phases = data["phases"]
    floor = "<br>" + numbered([inline(f["text"]) for f in data["hard_floor"]])
    prin_rows = []
    for pr in data["principles"]:
        cell = inline(pr["text"]) + (floor if pr["id"] == "hard-floor" else "")
        prin_rows.append([code(pr["id"]) + "<br>" + code(pr["strength"]), cell])
    order = "，".join(data["decision_order"])
    pit_rows = [[code(p["id"]), inline(x["symptom"]), inline(x["cause"]), inline(x["fix"])] for p in phases for x in p["pitfalls"]]
    basis_rows = [[inline(b["item"]), BASIS_KIND[b["kind"]], inline(b["note"])] for b in data["basis"]]
    rules = "\n".join([
        "<h3>一、怎么用这条路径</h3>",
        ul([inline(u) for u in pg["usage"]]),
        table(["编号与强度", "要求"], prin_rows),
        f"<p>两个做法冲突时的裁决顺序，靠前的赢：{inline(order)}。逐层含义和用法见思考工具 {code('conflict-order')}。</p>",
        "<h3>二、十个阶段</h3>",
        "\n".join(phase_html(p) for p in phases),
        "<h3>三、思考工具</h3>",
        table(["工具", "怎么用"], [tool_row(t) for t in data["thinking_tools"]]),
        "<h3>四、常见失误</h3>",
        table(["阶段", "症状", "原因", "怎么修"], pit_rows),
        "<h3>五、方法依据</h3>",
        table(["条目", "性质", "备注"], basis_rows),
    ])
    workflow = "\n".join([
        "<p>" + " → ".join(f"{code(p['id'])} {inline(p['name'])}" for p in phases) + "</p>",
        ul([inline(n) for n in pg["workflow_notes"]]),
    ])
    used = [p for p in phases if any(p["id"] in data["surfaces"][s]["phase_notes"] for s in SURFACES)]
    matrix_rows = [[f"{code(p['id'])} {inline(p['name'])}"] + [inline(data["surfaces"][s]["phase_notes"].get(p["id"], "—")) for s in SURFACES] for p in used]
    matrix = table(["阶段"] + [data["surfaces"][s]["name"] for s in SURFACES], matrix_rows)
    ex = data["worked_example"]
    ex_rows = [[code(s["phase"]) + "<br>" + inline(s["ask"]), inline(s["answer"]), inline(s["deviation"])] for s in ex["steps"]]
    examples = f"<p>{inline(ex['brief'])}</p>\n" + table(["阶段与问", "怎么答，得出什么", "偏离范式处"], ex_rows)
    pm = data["project_mode"]
    handoff = "\n".join([
        ul([inline(h) for h in pg["handoff"]]),
        f"<h3>项目模式（阶段 {code(pm['stage'])}）</h3>",
        "<p>读：</p>", ul([inline(x) for x in pm["reads"]]),
        "<p>写：</p>", ul([inline(x) for x in pm["writes"]]),
        table(["阶段", "落进前端界面设计文档的哪些类"], [[inline(x["phase"]), inline(x["doc"])] for x in pm["phase_to_doc"]]),
        "<p>停下来问人：</p>", ul([inline(x) for x in pm["stop_points"]]),
    ])
    gates = ul([inline(g) for g in pg["quality_gates"]]) + f"\n<p>命令：{inline(pg['gate_commands'])}</p>"
    return {"scope": f"<p>{inline(pg['scope'])}</p>", "workflow": workflow, "rules": rules, "platform-matrix": matrix,
            "examples": examples, "output-contract": ul([inline(c) for c in pg["output_contract"]]), "quality-gates": gates, "handoff": handoff}


def render_html(data: dict | None = None) -> str:
    data = data or load()
    title = data["title"]
    body = sections_html(data)
    parts = ["<!doctype html>", '<html lang="zh-CN">', "<head>", '  <meta charset="utf-8">',
             '  <meta name="viewport" content="width=device-width, initial-scale=1">', f"  <title>{title}</title>",
             f'  <link rel="icon" href="{FAVICON}">', '  <link rel="stylesheet" href="guidelines.css">', "</head>", "<body>",
             f'<main id="main" aria-label="{title}">', f"    <h1>{title}</h1>"]
    for sid, name, icon in SECTIONS:
        parts += [f"<!-- SECTION:{sid}:START id={sid} data-rule-id=path-{sid} -->",
                  f'<section id="{sid}" data-rule-id="path-{sid}" aria-labelledby="{sid}-heading">',
                  f'<h2 id="{sid}-heading" class="section-heading">{SVG_OPEN}{icon}</svg><span>{name}</span></h2>',
                  body[sid], "</section>", f"<!-- SECTION:{sid}:END -->", ""]
    parts += ["</main>", "</body>", "</html>", ""]
    return "\n".join(parts)


def cmd_render(args, data: dict) -> int:
    text = render_html(data)
    if args.check:
        same = PAGE_PATH.is_file() and PAGE_PATH.read_text(encoding="utf-8") == text
        print("规则页与数据一致" if same else "规则页与 design-path.json 不一致：运行 render --write")
        return 0 if same else 1
    if args.write:
        PAGE_PATH.write_text(text, encoding="utf-8", newline="\n")
        print(f"已写 {PAGE_PATH}（{len(text.encode('utf-8'))} 字节）")
    else:
        sys.stdout.write(text)
    return 0


# ---------------------------------------------------------------- 入口

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="阶段、思考工具、总原则、待补位置")
    s = sub.add_parser("show", help="一个阶段、工具、原则，或 order、floor、deviation、signature、example、surfaces、project、basis")
    s.add_argument("id")
    s = sub.add_parser("checklist", help="可粘进 BRIEF 的检查表，每阶段一行")
    s.add_argument("--surface", choices=SURFACES)
    s.add_argument("--format", choices=["md", "json"], default="md")
    s.add_argument("--detail", action="store_true", help="另列逐项检查（每条检查一个勾选框）")
    s = sub.add_parser("deviation", help="标准格式的偏离说明；must 规则拒绝")
    s.add_argument("rule")
    s.add_argument("--why", required=True)
    s.add_argument("--risk", required=True)
    s.add_argument("--verify", required=True)
    s.add_argument("--strength", choices=["default", "hint"], help="规则不在库里时的强度，默认 default")
    s.add_argument("--json", action="store_true", help="输出 spec.json 里 deviations 的一项")
    s = sub.add_parser("render", help="由数据文件生成规则页")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    data = load()
    return {"list": cmd_list, "show": cmd_show, "checklist": cmd_checklist, "deviation": cmd_deviation, "render": cmd_render}[args.cmd](args, data)


if __name__ == "__main__":
    sys.exit(main())
