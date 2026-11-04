#!/usr/bin/env python3
"""页面范式库的命令行：查范式、按功能清单生成首页方案、检查重复入口。

    py -X utf8 scripts/page_pattern.py list [paradigms|types|pages|rules|zones]
    py -X utf8 scripts/page_pattern.py show <id>            范式、应用类型、页面、规则、区域的完整说明（含选它前要问的问题与创新空间）；show method 看思考方法
    py -X utf8 scripts/page_pattern.py recommend --type ecommerce [--functions 9] [--tabs 4] [--width 375]
    py -X utf8 scripts/page_pattern.py brief --features features.json --entrances entrances.json --type ecommerce --out brief.json
    py -X utf8 scripts/page_pattern.py plan --brief brief.json [--out spec.json]
    py -X utf8 scripts/page_pattern.py check spec.json
    py -X utf8 scripts/page_pattern.py check-page page.html [--hash "#/home"] [--width 390] [--role home|mine|other]

数据源是 references/page-patterns.json（页面规则页 references/page-patterns.html 由它而来）。入口表格式见该文件的 entrances_schema，
或运行 show entrances。职责划分：System 决定功能与入口归属，本工具只决定首页的模块、顺序与去重，不增删 System 已批准的入口。
退出码：check 与 check-page 发现违反时为 1；输入有误为 2。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_PATH = ROOT / "references" / "page-patterns.json"
sys.path.insert(0, str(HERE))

from style_match import dock_grid  # noqa: E402

TYPES9 = ["context", "search", "task", "status", "account", "order", "marketing", "content", "tool"]
CATEGORIES = ["core", "info", "marketing", "aux"]
ENTRIES = ["tab", "home", "mine", "context", "in-page"]
FREQS = ["high", "mid", "low"]
TYPE_PRIORITY = {"context": 0, "search": 1, "status": 2, "order": 3, "task": 4, "marketing": 5, "content": 6, "account": 7, "tool": 8}
FEED_IDS = {"feed", "two-column-card-grid", "masonry", "single-column-list"}
HOME_ORDER = ["search-header", "notice-bar", "status-card", "member-card-hero", "banner-carousel", "workbench", "entry-cards",
              "dock-grid", "horizontal-scroller", "feed", "secondary-links"]
MODULE_ZONE = {"search-header": "header-context", "notice-bar": "feed", "status-card": "status-card", "member-card-hero": "status-card",
               "banner-carousel": "banner", "workbench": "dock", "entry-cards": "dock", "dock-grid": "dock",
               "horizontal-scroller": "marketing", "feed": "feed", "two-column-card-grid": "feed", "masonry": "feed",
               "single-column-list": "feed", "secondary-links": "in-page"}
KIND_LABEL = {"rule": "规则证据", "example": "实例证据", "user": "用户要求", "convention": "惯例", "skill": "技能内部规则或本技能取值"}
ACCOUNT_WORDS = ["会员", "收藏", "优惠券", "积分", "储值", "地址", "设置", "客服", "发票", "钱包"]
ORDER_WORDS = ["全部订单", "我的订单", "待付款", "待发货", "待收货", "待评价", "售后"]
CONTEXT_WORDS = ["选择门店", "切换门店", "配送方式", "切换城市", "定位"]

_CACHE: dict[str, Any] = {}


# ---------------------------------------------------------------- 数据

def load(path: Path | None = None) -> dict:
    path = path or DATA_PATH
    key = str(path)
    if key not in _CACHE:
        _CACHE[key] = json.loads(path.read_text(encoding="utf-8"))
    return _CACHE[key]


def by_id(items: list[dict]) -> dict[str, dict]:
    return {i["id"]: i for i in items}


def norm_dest(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"", "#", "none", "null"}:
        return ""
    return text.rstrip("/") if len(text) > 1 else text


def find_density(data: dict, key: str, default: Any = None) -> Any:
    item = data["density"]["home"].get(key)
    return item["value"] if isinstance(item, dict) else default


# ---------------------------------------------------------------- 输出

def src_label(data: dict, ref: str) -> str:
    base = ref.split("#")[0]
    src = data["sources"].get(base)
    if not src:
        return ref
    title = src["title"] if len(src["title"]) <= 40 else src["title"][:40] + "…"
    return f"{ref}（{title}）"


def fmt_evidence(data: dict, evs: list[dict], indent: str = "    ") -> list[str]:
    lines = []
    for e in evs:
        note = f"：{e['note']}" if e.get("note") else ""
        lines.append(f"{indent}[{KIND_LABEL.get(e['kind'], e['kind'])}] {src_label(data, e['ref'])}{note}")
    return lines


def show_paradigm(data: dict, p: dict) -> list[str]:
    alias = f"（别名：{'、'.join(p['aliases'])}）" if p.get("aliases") else ""
    out = [f"范式 {p['id']}  {p['name']}{alias}", f"  族：{p['family']}  角色：{p['role']}{'（也可作整页骨架）' if p.get('can_be_skeleton') and p['role'] != 'page-skeleton' else ''}  置信度：{p['confidence']}",
           f"  概要：{p['summary']}", f"  结构：{p['structure']}", "  参数："]
    for q in p["params"]:
        out.append(f"    - [{q['strength']}] {q['name']}：{q['value']}")
        out += fmt_evidence(data, q["evidence"], "        ")
    out.append(f"  适合的应用类型：{'、'.join(p['fits'])}")
    out.append("  不适合 / 避免：")
    out += [f"    - {x}" for x in p["avoid"]]
    out.append("  组件（五个库）：")
    for lib, items in p["components"].items():
        out.append(f"    {lib}：{'；'.join(items)}")
    if p["perf"]:
        out.append("  性能：" + "；".join(p["perf"]))
    out.append(f"  可组合：{'、'.join(p['combine_with'])}")
    out.append("  选它前要问的问题：")
    out += [f"    {i}. {q}" for i, q in enumerate(p["think"], 1)]
    out.append(f"  给创新留的空间：{p['innovation_room']}")
    out.append("  证据：")
    out += fmt_evidence(data, p["evidence"])
    return out


def show_page(data: dict, p: dict) -> list[str]:
    out = [f"页面 {p['id']}  {p['name']}  置信度：{p['confidence']}", f"  适用类型：{'、'.join(p['applies_to'])}", f"  职责：{p['purpose']}"]
    if p.get("order_basis"):
        out.append(f"  区块顺序依据：{p['order_basis']}")
    out.append("  区块顺序：")
    for b in p["blocks"]:
        comps = "；".join(f"{k}：{v}" for k, v in b["components"].items())
        out.append(f"    {b['order']}. {b['id']}（{b['paradigm']}，{'必有' if b['required'] else '按需'}）{b['notes']}" + (f"  组件：{comps}" if comps else ""))
    out.append("  怎么选：")
    out += [f"    - [{r['strength']}] 当{r['when']}，则{r['then']}" for r in p["choose_rules"]]
    out.append("  去重：")
    out += [f"    - {x}" for x in p["dedup_rules"]]
    out.append("  状态：" + "；".join(f"{k}：{v}" for k, v in p["states"].items()))
    out.append("  自适应：" + "；".join(p["adaptive"]))
    out.append("  常见错误：" + "；".join(p["antipatterns"]))
    out.append("  需要 System 提供：" + "；".join(p["needs_from_system"]))
    out.append("  设计这一页前要问：")
    out += [f"    {i}. {q}" for i, q in enumerate(p["think"], 1)]
    out.append(f"  给创新留的空间：{p['innovation_room']}")
    out.append("  证据：")
    out += fmt_evidence(data, p["evidence"])
    return out


def show_type(data: dict, t: dict) -> list[str]:
    h = t["home"]
    out = [f"应用类型 {t['id']}  {t['name']}  置信度：{t['confidence']}", f"  例子：{t['examples']}",
           f"  标签栏：{t['tab_bar']['count_hint']} 项，典型：{'、'.join(t['tab_bar']['typical'])}",
           f"  首页骨架：{h['skeleton']}  首页推荐模块顺序：{' → '.join(h['modules'])}", f"  有数据才出现的模块：{'、'.join(h['optional'])}",
           f"  首屏模块上限：{h['first_screen_max']}", f"  说明：{h['notes']}", "  不要：" + "；".join(t["avoid"]), "  随情境调整："]
    out += [f"    - {v}" for v in t["variations"]]
    out.append("  证据：")
    out += fmt_evidence(data, t["evidence"])
    return out


def show_rule(data: dict, r: dict) -> list[str]:
    out = [f"规则 {r['id']}  [{r['strength']}]  检查：{r['check']}{'+' + '+'.join(r['check_also']) if r.get('check_also') else ''}  范围：{r['scope']}  置信度：{r['confidence']}", f"  {r['text']}"]
    if r.get("exceptions"):
        out.append("  例外：" + "；".join(r["exceptions"]))
    out.append("  证据：")
    out += fmt_evidence(data, r["evidence"])
    return out


def show_zone(data: dict, z: dict) -> list[str]:
    out = [f"区域 {z['id']}  {z['name']}", f"  允许的功能类型：{'、'.join(z['allowed_function_types'])}", f"  上限：{json.dumps(z['caps'], ensure_ascii=False)}",
           f"  相关规则：{'、'.join(z['rules'])}", f"  说明：{z['notes']}"]
    return out


def show_ftype(data: dict, f: dict) -> list[str]:
    return [f"功能类型 {f['id']}  {f['name']}", f"  例子：{f['examples']}", f"  默认区域：{f['default_zone']}", f"  首页：{f['home']}",
            f"  能进金刚区：{'能（多个并列高频才用）' if f['dock_allowed'] else '不能'}", *( [f"  备注：{f['note']}"] if f.get("note") else [])]


def show_method(data: dict) -> list[str]:
    m = data["method"]
    out = [m["principle"], "思考步骤："]
    out += [f"  {s['n']}. {s['name']}：{s['do']}" for s in m["steps"]]
    out.append("精简五问：")
    out += [f"  {i}. {q}" for i, q in enumerate(m["five_questions"], 1)]
    out.append("规则强度：" + "；".join(f"{k}：{v}" for k, v in m["strength"].items()))
    out.append("偏离说明写法：" + "；".join(f"{k}：{v}" for k, v in m["deviation_format"].items()))
    out.append("证据类别：" + "；".join(f"{k}：{v}" for k, v in m["evidence_kinds"].items()))
    return out


def show_entrances(data: dict) -> list[str]:
    s = data["entrances_schema"]
    out = [s["description"], s["file"], "字段："]
    out += [f"  {k}：{v}" for k, v in s["fields"].items()]
    out.append("标签栏项：" + "；".join(f"{k}：{v}" for k, v in s["tabbar_item"].items()))
    out.append("示例：")
    out.append(json.dumps(s["example"], ensure_ascii=False, indent=1))
    return out


def cmd_list(args, data: dict) -> int:
    what = args.what or "all"
    show_all = what == "all"
    if show_all or what == "paradigms":
        print(f"范式 {len(data['paradigms'])} 个：")
        for p in data["paradigms"]:
            print(f"  {p['id']:24s} {p['name']:12s} {p['family']:12s} {p['role']:14s} 置信度 {p['confidence']}")
    if show_all or what == "types":
        print(f"应用类型 {len(data['app_types'])} 个：")
        for t in data["app_types"]:
            print(f"  {t['id']:24s} {t['name']:16s} 标签栏 {t['tab_bar']['count_hint']:10s} 置信度 {t['confidence']}")
    if show_all or what == "pages":
        print(f"页面 {len(data['pages'])} 个：")
        for p in data["pages"]:
            print(f"  {p['id']:24s} {p['name']:16s} 置信度 {p['confidence']}")
    if show_all or what == "rules":
        print(f"规则 {len(data['rules'])} 条：")
        for r in data["rules"]:
            print(f"  [{r['strength']:7s}] {r['id']:38s} 检查：{r['check']:9s} {r['text'][:46]}")
    if show_all or what == "zones":
        print(f"入口区域 {len(data['entry_zones'])} 个：")
        for z in data["entry_zones"]:
            print(f"  {z['id']:16s} {z['name']:12s} 允许：{'、'.join(z['allowed_function_types'])}")
    return 0


def cmd_show(args, data: dict) -> int:
    key = args.id.strip()
    if key == "method":
        print("\n".join(show_method(data)))
        return 0
    if key in ("entrances", "entrances_schema"):
        print("\n".join(show_entrances(data)))
        return 0
    kind = None
    if ":" in key:
        kind, key = key.split(":", 1)
    groups = [("paradigm", data["paradigms"], show_paradigm), ("type", data["app_types"], show_type), ("page", data["pages"], show_page),
              ("rule", data["rules"], show_rule), ("zone", data["entry_zones"], show_zone), ("function", data["function_types"], show_ftype)]
    hits = 0
    for name, items, fn in groups:
        if kind and kind != name:
            continue
        for item in items:
            if item["id"] == key or key in item.get("aliases", []) or item.get("name") == key:
                if hits:
                    print()
                print("\n".join(fn(data, item)))
                hits += 1
    if not hits:
        print(f"没有 id 为 {args.id} 的范式、类型、页面、规则、区域或功能类型；先运行 list。", file=sys.stderr)
        return 2
    return 0


# ---------------------------------------------------------------- recommend

def label_len(name: str) -> int:
    return max(1, len(str(name).strip()))


def dock_advice(n: int, longest: int, width: int, data: dict) -> dict:
    dmin, dmax = find_density(data, "dock_items_min", 5), find_density(data, "dock_items_max", 10)
    if n < dmin:
        return {"use_dock": False, "reason": f"并列核心入口只有 {n} 个，不足 {dmin} 个：不用金刚栅格，{'用入口大卡' if n else '首页不设入口区'}（凑不满就不凑）"}
    layout = dock_grid(n, longest, width)
    reason = f"{n} 个入口、最长文案 {longest} 字、屏宽 {width}：{layout['columns']} 列 {layout['rows']} 行，{layout['pages']} 页，可见 {layout['visible_entries']} 项" + ("（含“全部”入口）" if layout["all_entry"] else "")
    if n > dmax:
        reason += f"；超过本技能默认的一页 {dmax} 项，请确认它们真的都是并列高频核心，否则删减（偏离要写偏离说明）"
    return {"use_dock": True, "layout": layout, "reason": reason}


def recommend(data: dict, type_id: str, functions: int | None, tabs: int | None, width: int, label_chars: int) -> dict:
    types = by_id(data["app_types"])
    if type_id not in types:
        raise SystemExit(f"未知应用类型 {type_id}；可选：{'、'.join(types)}")
    t = types[type_id]
    out: dict[str, Any] = {"type": type_id, "name": t["name"], "skeleton": t["home"]["skeleton"], "modules": list(t["home"]["modules"]),
                           "optional": t["home"]["optional"], "first_screen_max": t["home"]["first_screen_max"], "tab_bar": t["tab_bar"],
                           "notes": t["home"]["notes"], "avoid": t["avoid"], "variations": t["variations"], "confidence": t["confidence"]}
    out["dock"] = dock_advice(functions, label_chars, width, data) if functions is not None else None
    policy = t["home"].get("dock_policy", "optional")
    if functions is not None:
        if out["dock"]["use_dock"]:
            if policy == "avoid":
                out["dock"]["reason"] += f"；但应用类型 {t['name']} 通常不用金刚栅格，请先核对这些入口是不是真的并列高频核心"
            elif "dock-grid" not in out["modules"]:
                at = next((i for i, m in enumerate(out["modules"]) if m in ("horizontal-scroller", "feed", "two-column-card-grid", "masonry")), len(out["modules"]))
                out["modules"].insert(at, "dock-grid")
        else:
            out["modules"] = [("entry-cards" if functions else None) if m == "dock-grid" else m for m in out["modules"]]
            out["modules"] = [m for m in out["modules"] if m]
            if functions and "entry-cards" not in out["modules"]:
                at = next((i for i, m in enumerate(out["modules"]) if m in ("horizontal-scroller", "feed", "two-column-card-grid", "masonry", "single-column-list")), len(out["modules"]))
                out["modules"].insert(at, "entry-cards")
    tabs_note = None
    if tabs is not None:
        lo, hi, sug = (data["density"]["tabbar"][k]["value"] for k in ("items_min", "items_max", "items_suggest_max"))
        if tabs < lo or tabs > hi:
            tabs_note = f"标签栏 {tabs} 项不在 {lo}–{hi} 项范围内（微信小程序设计指南）：退回 System"
        elif tabs > sug:
            tabs_note = f"标签栏 {tabs} 项：建议不超过 {sug} 项，5 项要有理由（hint）"
        else:
            tabs_note = f"标签栏 {tabs} 项：在范围内"
    out["tabs_note"] = tabs_note
    return out


def print_recommend(r: dict) -> None:
    print(f"应用类型：{r['name']}（{r['type']}，置信度 {r['confidence']}）")
    print(f"标签栏：提示 {r['tab_bar']['count_hint']}，典型 {'、'.join(r['tab_bar']['typical'])}" + (f"；{r['tabs_note']}" if r["tabs_note"] else ""))
    print(f"首页骨架：{r['skeleton']}，首屏模块不超过 {r['first_screen_max']} 个")
    print("推荐模块顺序（带 ? 的有数据才出现）：")
    for i, m in enumerate(r["modules"], 1):
        print(f"  {i}. {m}{'?' if m in r['optional'] else ''}")
    if r["dock"]:
        print(f"金刚区：{r['dock']['reason']}")
    print(f"理由：{r['notes']}")
    print("不要：" + "；".join(r["avoid"]))
    print("随情境调整：")
    for v in r["variations"]:
        print(f"  - {v}")
    print("提示：以上是起点不是答案；每个范式用 show <id> 看“选它前要问的问题”，再按真实入口表 brief 与 plan。")


# ---------------------------------------------------------------- brief

def validate_entrances(rows: list[dict]) -> tuple[list[dict], list[str]]:
    errors, out, seen = [], [], set()
    for i, raw in enumerate(rows, 1):
        where = f"entrances[{i}] {raw.get('fn', '?')}"
        row = {k: raw.get(k) for k in ("fn", "name", "type", "category", "entry", "destination", "freq")}
        for k in ("fn", "name", "type", "category", "entry", "destination", "freq"):
            if row[k] in (None, ""):
                errors.append(f"{where} 缺 {k}")
        for k, allowed in (("type", TYPES9), ("category", CATEGORIES), ("entry", ENTRIES), ("freq", FREQS)):
            if row[k] not in (None, "") and row[k] not in allowed:
                errors.append(f"{where} 的 {k}={row[k]} 不在 {allowed}")
        if row["fn"] in seen:
            errors.append(f"{where} 的 fn 重复；一个功能一行")
        seen.add(row["fn"])
        for k in ("image", "limited", "summary"):
            if raw.get(k):
                row[k] = True
        out.append(row)
    return out, errors


def make_brief(features: dict | None, entrances_doc: dict, type_id: str, data: dict, width: int = 375) -> dict:
    types = by_id(data["app_types"])
    if type_id not in types:
        raise SystemExit(f"未知应用类型 {type_id}；可选：{'、'.join(types)}")
    t = types[type_id]
    rows, errors = validate_entrances(entrances_doc.get("entrances", []))
    if errors:
        raise SystemExit("入口表有误（格式见 show entrances）：\n  " + "\n  ".join(errors))
    tabbar = entrances_doc.get("tabbar")
    if not tabbar:
        tabbar = [{"name": r["name"], "destination": r["destination"]} for r in rows if r["entry"] == "tab"]
    warnings: list[str] = []
    brief_features: dict[str, Any] = {"total": 0, "frontend": 0, "modules": []}
    unmapped: list[dict] = []
    if features:
        fl = features.get("features", [])
        modules = {m["id"]: m["name"] for m in features.get("modules", [])}
        front = [f for f in fl if str(f.get("surface", "")).lower() not in {"web-admin", "admin", "platform", "backend", "agent"}]
        known = {f["id"] for f in fl}
        mapped = {r["fn"] for r in rows}
        brief_features = {"total": len(fl), "frontend": len(front),
                          "modules": [{"id": mid, "name": name, "count": sum(1 for f in front if f.get("module") == mid)} for mid, name in modules.items()]}
        unmapped = [{"fn": f["id"], "name": f["name"]} for f in front if f["id"] not in mapped]
        for r in rows:
            if r["fn"] not in known:
                warnings.append(f"入口表的 {r['fn']} 不在功能清单里：请 System 核对")
        if unmapped:
            warnings.append(f"功能清单里有 {len(unmapped)} 个前台功能没有入口行（可能是页内功能，也可能漏了）：请 System 确认，Design 不自行补入口")
    types_present = {r["type"] for r in rows}
    constraints = {k: find_density(data, k) for k in ("first_screen_modules_max", "page_modules_max", "dock_items_min", "dock_items_max", "dock_pages_max",
                                                    "marketing_modules_max", "banner_frames_max", "status_cards_max", "header_context_items_max", "scroller_items_max")}
    constraints["first_screen_modules_max"] = t["home"]["first_screen_max"]
    constraints["tabbar_items"] = [data["density"]["tabbar"]["items_min"]["value"], data["density"]["tabbar"]["items_max"]["value"]]
    think = list(data["method"]["five_questions"]) + [f"该类型不建议：{x}" for x in t["avoid"]] + [f"可随情境调整：{x}" for x in t["variations"]]
    for m in t["home"]["modules"]:
        think.append(f"选 {m} 前先问：show {m}")
    brief = {"version": 1, "created": date.today().isoformat(), "type": type_id, "type_name": t["name"], "width": width,
             "features": brief_features, "entrances": rows, "tabbar": tabbar, "tab_count": len(tabbar), "unmapped_features": unmapped,
             "type_modules": t["home"]["modules"], "type_optional": t["home"]["optional"], "constraints": constraints,
             "entrance_types_present": sorted(types_present, key=TYPE_PRIORITY.get), "think": think, "warnings": warnings,
             "record_in_brief": "BRIEF 写明采用的规则（rules 的 id）、被偏离的规则与偏离说明、本次沉淀；输出的 spec 与 brief 一并保存"}
    return brief


# ---------------------------------------------------------------- plan

def order_key(mod_id: str, type_modules: list[str]) -> float:
    if mod_id in type_modules:
        return type_modules.index(mod_id) * 10
    if mod_id in HOME_ORDER:
        for earlier in reversed(HOME_ORDER[:HOME_ORDER.index(mod_id)]):
            if earlier in type_modules:
                return type_modules.index(earlier) * 10 + 5
    return -1


WHY = {"context": "全局上下文，放顶部上下文栏", "search": "搜索放顶部，不占金刚区", "status": "状态与待办：首页状态卡，只显示进行中的一条",
       "marketing": "营销：放营销位，同一活动一个位置，同屏不超过 2 个模块", "content": "内容与公告：公告栏或信息流", "task": "核心任务：并列高频的进核心位"}


def item_of(e: dict, zone: str, **extra) -> dict:
    d = {"fn": e["fn"], "name": e["name"], "type": e["type"], "destination": e["destination"], "zone": zone, "freq": e["freq"], "why": WHY.get(e["type"], "")}
    d.update(extra)
    return d


def make_plan(brief: dict, data: dict, width: int | None = None) -> dict:
    types = by_id(data["app_types"])
    t = types[brief["type"]]
    width = width or brief.get("width", 375)
    tab = brief["tabbar"]
    tab_dests = {norm_dest(x.get("destination")) for x in tab} - {""}
    tab_names = {x["name"] for x in tab}
    rows = sorted(enumerate(brief["entrances"]), key=lambda p: (TYPE_PRIORITY.get(p[1]["type"], 9), p[0]))
    cmax = {k: brief["constraints"].get(k) or find_density(data, k) for k in ("header_context_items_max", "status_cards_max", "banner_frames_max", "scroller_items_max", "dock_items_max", "dock_items_min")}
    workbench = "workbench" in t["home"]["modules"]
    rejected: list[dict] = []
    warnings: list[str] = []
    seen: dict[str, dict] = {}
    buckets: dict[str, list] = {k: [] for k in ("context", "search", "status", "summary", "market", "task", "low", "notice", "content")}

    def reject(e: dict, code: str, reason: str, goes_to: str, kind: str = "routed") -> None:
        rejected.append({"fn": e["fn"], "name": e["name"], "type": e["type"], "destination": e["destination"], "code": code,
                         "kind": kind, "reason": reason, "goes_to": goes_to})

    def take(e: dict) -> bool:
        d = norm_dest(e["destination"])
        if d and d in seen:
            first = seen[d]
            reject(e, "duplicate-destination", f"同目的地重复：只留“{first['name']}”（{first['fn']}）", "已在首页另一处", "dropped")
            return False
        if d:
            seen[d] = e
        return True

    for _, e in rows:
        d, t9 = norm_dest(e["destination"]), e["type"]
        if d == "home":
            reject(e, "is-home", "目的地就是首页本身", "首页", "dropped")
            continue
        if e["entry"] == "tab" or (d and d in tab_dests) or e["name"] in tab_names:
            reject(e, "tab-duplicate", "与标签栏重复：标签栏已有该目的地，首页不再放入口", "标签栏", "dropped")
            continue
        if t9 == "account" or e["entry"] == "mine" and t9 != "order":
            if t9 == "account" and e.get("summary") and not buckets["summary"]:
                buckets["summary"].append({"fn": e["fn"], "name": f"{e['name']}状态摘要", "type": "account", "destination": "", "zone": "status-card",
                                           "freq": e["freq"], "summary": True, "entrance": False, "why": "账户类：首页只放一条状态摘要，不另设入口"})
            reject(e, "account", f"{e['name']}：账户与个人资产类，归我的" + ("（首页只放一条状态摘要，不另设入口）" if t9 == "account" and e.get("summary") else ""), "mine-list")
            continue
        if t9 == "tool":
            reject(e, "tool", f"{e['name']}：低频工具与合规类，归我的或二级页", "mine-list")
            continue
        if e["entry"] == "in-page":
            reject(e, "in-page", f"{e['name']}：System 归属为页内入口，首页不放", "in-page")
            continue
        if t9 == "context" or e["entry"] == "context":
            if len(buckets["context"]) >= cmax["header_context_items_max"]:
                reject(e, "header-overflow", f"上下文栏已满 {cmax['header_context_items_max']} 项：合并或收进门店选择页", "门店选择页")
            elif take(e):
                buckets["context"].append(item_of(e, "header-context"))
            continue
        if t9 == "search":
            if buckets["search"]:
                reject(e, "search-duplicate", "首页只有一个搜索框", "已在顶部搜索", "dropped")
            elif take(e):
                buckets["search"].append(item_of(e, "search"))
            continue
        if t9 == "order":
            if e["entry"] == "home":
                if any(i.get("state_card") and i["type"] == "order" for i in buckets["status"]):
                    reject(e, "order-state-card-once", "订单：首页只出一张进行中状态卡", "已有状态卡", "dropped")
                elif take(e):
                    reject(e, "order", f"{e['name']}：订单类，首页只出进行中订单的状态卡，不放全部订单入口（已改成状态卡）", "status-card（进行中状态卡）", "routed")
                    buckets["status"].append(item_of(e, "status-card", name="进行中订单", state_card=True, why="订单：首页只出进行中状态卡"))
            else:
                reject(e, "order", f"{e['name']}：订单类，归订单标签或我的订单卡；首页只出进行中订单的状态卡（须 System 另给一行 status 类入口）", "订单标签或我的")
            continue
        if t9 == "status":
            if len(buckets["status"]) >= cmax["status_cards_max"]:
                reject(e, "status-overflow", f"状态卡已满 {cmax['status_cards_max']} 张：只显示最紧急的，其余在所属列表页", "所属列表页")
            elif take(e):
                buckets["status"].append(item_of(e, "status-card", state_card=True))
            continue
        if t9 == "marketing":
            if take(e):
                buckets["market"].append(item_of(e, "marketing", image=bool(e.get("image")), limited=bool(e.get("limited"))))
            continue
        if t9 == "content":
            if take(e):
                key = "notice" if re.search(r"公告|通知|须知", e["name"]) else "content"
                buckets[key].append(item_of(e, "feed"))
            continue
        if t9 == "task":
            if e["freq"] == "low":
                if take(e):
                    buckets["low"].append(item_of(e, "in-page"))
                    warnings.append(f"[tool-in-mine-or-inpage] 低频入口上首页：{e['name']}（{e['fn']}）暂放次要入口行，建议退回 System 改归我的或页内")
            elif take(e):
                buckets["task"].append(item_of(e, "dock"))
            continue
        warnings.append(f"{e['fn']} 的类型 {t9} 没有对应的首页区域，已忽略")

    modules: dict[str, dict] = {}

    def add(mod_id: str, items: list, **extra) -> None:
        if items:
            modules[mod_id] = {"id": mod_id, "paradigm": mod_id, "zone": MODULE_ZONE.get(mod_id, "feed"), "items": items, **extra}

    header = buckets["context"] + buckets["search"]
    add("search-header", header)
    add("notice-bar", buckets["notice"][:1])
    for extra_notice in buckets["notice"][1:]:
        reject({"fn": extra_notice["fn"], "name": extra_notice["name"], "type": "content", "destination": extra_notice["destination"]}, "notice-overflow", "公告栏只有一个", "公告栏", "dropped")
    if buckets["summary"] and "member-card-hero" in t["home"]["modules"]:
        add("member-card-hero", buckets["summary"])
        add("status-card", buckets["status"])
    else:
        add("status-card", buckets["status"] + buckets["summary"])

    # 营销：轮播（有图，至多 3 帧）加横滑（其余，至多 6 项），合计不超过 2 个模块
    prio = {"high": 0, "mid": 1, "low": 2}
    market = sorted(buckets["market"], key=lambda i: (not i["limited"], not i["image"], prio.get(i["freq"], 3)))
    banner = [i for i in market if i["image"]][:cmax["banner_frames_max"]]
    strip = [i for i in market if i not in banner][:cmax["scroller_items_max"]]
    over = [i for i in market if i not in banner and i not in strip]
    for i in banner:
        i["zone"] = "banner"
    add("banner-carousel", banner)
    add("horizontal-scroller", strip)
    for i in over:
        reject({"fn": i["fn"], "name": i["name"], "type": "marketing", "destination": i["destination"]}, "marketing-overflow",
               "营销入口超出首页承载量（轮播 3 帧加横滑 6 项）：放营销页或由后台开关", "营销页或后台开关")
    if over:
        warnings.append(f"[marketing-max-two] 营销入口多于首页承载量，{len(over)} 项未上首页；同一活动只占一个位置")

    # 核心任务：工作台、金刚栅格或入口大卡
    tasks = sorted(buckets["task"], key=lambda i: prio.get(i["freq"], 3))
    n = len(tasks)
    if tasks:
        if workbench:
            add("workbench", tasks[:8], role="quick")
            for e in tasks[8:]:
                reject({"fn": e["fn"], "name": e["name"], "type": "task", "destination": e["destination"]}, "workbench-overflow", "工作台快捷操作最多 8 个", "页内")
        elif n >= cmax["dock_items_min"]:
            if t["home"].get("dock_policy") == "avoid":
                warnings.append(f"[no-fill-dock] 应用类型 {t['name']} 不建议金刚栅格，请核对这 {n} 个入口是否都是并列高频核心")
            keep = tasks[:cmax["dock_items_max"]]
            for e in tasks[cmax["dock_items_max"]:]:
                e["zone"] = "in-page"
                buckets["low"].append(e)
                warnings.append(f"[dock-count-cap] {e['name']}（{e['fn']}）超出金刚区一页上限，暂放次要入口行")
            longest = max(label_len(i["name"]) for i in keep)
            layout = dock_grid(len(keep), longest, width)
            add("dock-grid", keep, layout=layout, longest_label=longest)
        else:
            add("entry-cards", tasks)
            warnings.append(f"[no-fill-dock] 并列核心入口 {n} 个，不足 {cmax['dock_items_min']} 个：用入口大卡，不硬凑金刚栅格")
    add("secondary-links", buckets["low"])

    feed_id = next((m for m in t["home"]["modules"] if m in FEED_IDS), "feed")
    add(feed_id, buckets["content"])
    if len(buckets["content"]) > 1:
        warnings.append("[feed-visible-reason-and-escape] 内容类入口多于 1 个：信息流只保留一个模块，请核对它们是不是同一条流的分类")

    # 类型提示
    if brief["type"] in ("enterprise-internal", "b2b-quote-ticket") and ("banner-carousel" in modules or "horizontal-scroller" in modules):
        warnings.append(f"应用类型 {t['name']} 通常没有营销位，请核对这些入口的归属")

    type_modules = list(t["home"]["modules"])
    ordered = sorted(modules.values(), key=lambda m: order_key(m["id"], type_modules))
    first_max = brief["constraints"].get("first_screen_modules_max") or t["home"]["first_screen_max"]
    for idx, m in enumerate(ordered):
        m["order"] = idx + 1
        m["first_screen"] = idx < first_max
    body = [m for m in ordered if m["id"] != "search-header"]
    if body and body[0]["zone"] in ("banner", "marketing") and any(m["id"] in ("status-card", "dock-grid", "entry-cards", "workbench") for m in body[1:]):
        warnings.append("[first-module-answers-return-task] 首屏第一个主体模块是营销位，而后面有状态卡或核心入口：核对用户回来最先做的事是不是营销")
    if len(ordered) > (brief["constraints"].get("page_modules_max") or 8):
        warnings.append(f"[page-modules-max] 整页 {len(ordered)} 个模块，超过默认 {brief['constraints'].get('page_modules_max') or 8}：删减或写偏离说明")
    tab_count = len(tab)
    if tab_count and (tab_count < 2 or tab_count > 5):
        warnings.append(f"[tabbar-count-2-to-5] 标签栏 {tab_count} 项不在 2–5 项：退回 System")
    elif tab_count > 4:
        warnings.append(f"[tabbar-prefer-4] 标签栏 {tab_count} 项：建议不超过 4 项，5 项要有理由")
    elif not tab_count:
        warnings.append("入口表没有标签栏信息：无法核对与标签栏的重复，请补 tabbar")

    rej_by_fn = {r["fn"]: r for r in rejected}
    placed = {i["fn"]: (m["id"], i.get("why", "")) for m in ordered for i in m["items"] if not i.get("summary")}
    ledger = []
    for e in brief["entrances"]:
        if e["fn"] in rej_by_fn:
            r = rej_by_fn[e["fn"]]
            ledger.append({"fn": e["fn"], "name": e["name"], "to": r["goes_to"], "reason": r["reason"], "kind": r["kind"]})
        elif e["fn"] in placed:
            ledger.append({"fn": e["fn"], "name": e["name"], "to": placed[e["fn"]][0], "reason": placed[e["fn"]][1], "kind": "placed"})
    spec = {"version": 1, "type": brief["type"], "type_name": t["name"], "width": width, "skeleton": t["home"]["skeleton"],
            "first_screen_max": first_max, "tabbar": {"count": tab_count, "items": tab}, "modules": ordered, "ledger": ledger, "rejected": rejected,
            "warnings": warnings, "deviations": [], "rules_checked": [r["id"] for r in data["rules"] if r["check"] == "script" or "script" in r.get("check_also", [])]}
    return spec


def print_plan(spec: dict) -> None:
    print(f"首页方案：{spec['type_name']}（{spec['type']}），屏宽 {spec['width']}，标签栏 {spec['tabbar']['count']} 项，首屏模块不超过 {spec['first_screen_max']} 个")
    for m in spec["modules"]:
        names = "、".join(i["name"] for i in m["items"])
        mark = "首屏" if m["first_screen"] else "次屏"
        extra = ""
        if m.get("layout"):
            lay = m["layout"]
            extra = f"  金刚：{lay['columns']} 列 {lay['rows']} 行 {lay['pages']} 页"
        print(f"  {m['order']}. {m['id']}（{mark}）：{names}{extra}")
    if spec.get("ledger"):
        print("每个功能的去向：")
        for r in spec["ledger"]:
            tag = {"placed": "上首页", "routed": "归别处", "dropped": "去重丢弃"}[r["kind"]]
            print(f"  - {r['name']}（{r['fn']}）→ {r['to']}［{tag}］{r['reason']}")
    if spec["warnings"]:
        print("告警：")
        for w in spec["warnings"]:
            print(f"  ! {w}")
    print("下一步：写 BRIEF（采用的规则、偏离说明、本次沉淀），用 check 检查本 spec，做成页面后用 check-page 渲染检查。")


# ---------------------------------------------------------------- check

def check_spec(spec: dict, data: dict) -> list[dict]:
    rules = by_id(data["rules"])
    findings: list[dict] = []
    devs = {d.get("rule"): d for d in spec.get("deviations", [])}

    def add(rule_id: str, message: str, level: str | None = None) -> None:
        strength = rules[rule_id]["strength"] if rule_id in rules else "must"
        level = level or ("error" if strength in ("must", "default") else "warn")
        dev = devs.get(rule_id)
        if strength == "default" and dev is not None:
            missing = [k for k in ("why", "risk", "verify") if not str(dev.get(k, "")).strip()]
            if missing:
                findings.append({"level": "error", "rule": rule_id, "message": f"偏离说明不完整，缺 {'、'.join(missing)}；{message}"})
            else:
                findings.append({"level": "deviated", "rule": rule_id, "message": f"已偏离（{dev['why']}）：{message}"})
            return
        if strength == "must" and dev is not None:
            findings.append({"level": "error", "rule": "deviation-note-required", "message": f"{rule_id} 是 must 规则，不许偏离，只能退回 System"})
        findings.append({"level": level, "rule": rule_id, "message": message})

    modules = spec.get("modules", [])
    tab = spec.get("tabbar", {}).get("items", [])
    tab_dests = {norm_dest(x.get("destination")) for x in tab} - {""}
    tab_names = {x.get("name") for x in tab}
    where: dict[str, list[str]] = {}
    names: dict[str, list[str]] = {}
    summaries = 0
    for m in modules:
        for i in m.get("items", []):
            zone = i.get("zone") or m.get("zone")
            t9 = i.get("type")
            label = f"{m['id']} 的“{i.get('name')}”（{i.get('fn')}）"
            d = norm_dest(i.get("destination"))
            if d:
                where.setdefault(d, []).append(label)
            if i.get("name"):
                names.setdefault(i["name"], []).append(label)
            if t9 == "context" and zone != "header-context":
                add("context-in-header-only", f"全局上下文放在了 {zone}：{label}")
            if t9 == "search" and zone != "search":
                add("search-top-not-dock", f"搜索放在了 {zone}：{label}")
            if t9 == "account":
                if i.get("summary") and i.get("entrance") is False and not d:
                    summaries += 1
                else:
                    add("account-in-mine-only", f"账户类入口出现在首页：{label}")
            if t9 == "order" and not (zone == "status-card" and i.get("state_card")):
                add("order-home-state-card-only", f"订单类不是进行中状态卡：{label}")
            if t9 == "tool":
                add("tool-in-mine-or-inpage", f"低频工具与合规类上了首页：{label}")
            if zone == "dock" and t9 != "task":
                add("dock-core-parallel-only", f"金刚区里有 {t9} 类入口：{label}")
            if zone == "dock" and (d in tab_dests or i.get("name") in tab_names):
                add("dock-no-tabbar-dup", f"金刚区入口与标签栏重复：{label}")
            elif d and d in tab_dests:
                add("one-destination-once", f"{label} 与标签栏同目的地 {i.get('destination')}")
    if summaries > 1:
        add("account-in-mine-only", f"首页账户类状态摘要有 {summaries} 条，最多 1 条")
    for d, places in where.items():
        if len(places) > 1:
            add("one-destination-once", f"目的地 {d} 在首页出现 {len(places)} 次：" + "；".join(places))
    for name, places in names.items():
        if len(places) > 1:
            dests = {norm_dest(i.get("destination")) for m in modules for i in m.get("items", []) if i.get("name") == name}
            if len(dests) > 1:
                add("one-destination-once", f"同名入口“{name}”出现 {len(places)} 次且目的地不同：" + "；".join(places), "warn")
    market_modules = [m for m in modules if m.get("zone") in ("banner", "marketing")]
    if len(market_modules) > data["density"]["home"]["marketing_modules_max"]["value"]:
        add("marketing-max-two", f"首页营销模块 {len(market_modules)} 个，超过 2 个：" + "、".join(m["id"] for m in market_modules))
    banner = next((m for m in modules if m["id"] == "banner-carousel"), None)
    if banner and len(banner["items"]) > data["density"]["home"]["banner_frames_max"]["value"]:
        add("carousel-frames-and-pause", f"轮播 {len(banner['items'])} 帧，超过 {data['density']['home']['banner_frames_max']['value']} 帧")
    dock = next((m for m in modules if m["id"] == "dock-grid"), None)
    if dock:
        n = len(dock["items"])
        dmin, dmax = data["density"]["home"]["dock_items_min"]["value"], data["density"]["home"]["dock_items_max"]["value"]
        if n < dmin:
            add("no-fill-dock", f"金刚区只有 {n} 个入口，不足 {dmin} 个：改用入口大卡")
        if n > dmax:
            add("dock-count-cap", f"金刚区 {n} 个入口，超过一页 {dmax} 个")
        lay = dock.get("layout")
        if lay:
            longest = dock.get("longest_label") or max(label_len(i.get("name", "")) for i in dock["items"])
            want = dock_grid(n, longest, spec.get("width", 375))
            if (lay.get("columns"), lay.get("rows"), lay.get("pages")) != (want["columns"], want["rows"], want["pages"]):
                add("dock-layout-by-formula", f"金刚区 {lay.get('columns')} 列 {lay.get('rows')} 行 {lay.get('pages')} 页，公式给出 {want['columns']} 列 {want['rows']} 行 {want['pages']} 页（{n} 项、最长 {longest} 字、屏宽 {spec.get('width', 375)}）")
        else:
            add("dock-layout-by-formula", "金刚区没有写 layout，无法核对公式", "warn")
    first = [m for m in modules if m.get("first_screen")]
    limit = spec.get("first_screen_max") or data["density"]["home"]["first_screen_modules_max"]["value"]
    if len(first) > limit:
        add("first-screen-modules-max", f"首屏模块 {len(first)} 个，超过 {limit} 个：" + "、".join(m["id"] for m in first))
    page_max = data["density"]["home"]["page_modules_max"]["value"]
    if len(modules) > page_max:
        add("page-modules-max", f"整页模块 {len(modules)} 个，超过 {page_max} 个")
    cnt = spec.get("tabbar", {}).get("count", len(tab))
    if cnt and (cnt < data["density"]["tabbar"]["items_min"]["value"] or cnt > data["density"]["tabbar"]["items_max"]["value"]):
        add("tabbar-count-2-to-5", f"标签栏 {cnt} 项不在 2–5 项：退回 System")
    elif cnt > data["density"]["tabbar"]["items_suggest_max"]["value"]:
        add("tabbar-prefer-4", f"标签栏 {cnt} 项，建议不超过 4 项", "warn")
    elif not cnt:
        findings.append({"level": "warn", "rule": "dock-no-tabbar-dup", "message": "spec 没有标签栏信息，无法核对与标签栏的重复"})
    return findings


def print_findings(findings: list[dict], label: str) -> int:
    errors = [f for f in findings if f["level"] == "error"]
    for f in findings:
        tag = {"error": "ERROR", "warn": "WARN ", "deviated": "DEVIATED"}[f["level"]]
        print(f"{tag} [{f['rule']}] {f['message']}")
    if errors:
        print(f"{label}: {len(errors)} 处违反")
        return 1
    print(f"{label}: ok")
    return 0


# ---------------------------------------------------------------- check-page

CLICKABLES = """() => {
  const SEL = 'a[href], button, [role="button"], [role="tab"], [role="link"], [role="menuitem"], [onclick], [data-href], [data-url], [data-route], [data-path], [data-target], input[type="button"], input[type="submit"], summary';
  const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
  const visible = (el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
  const nameOf = (el) => {
    const al = norm(el.getAttribute('aria-label')); if (al) return al;
    const lb = el.getAttribute('aria-labelledby');
    if (lb) { const t = norm(lb.split(/\\s+/).map((id) => (document.getElementById(id) || {}).textContent || '').join(' ')); if (t) return t; }
    const tx = norm(el.innerText || el.textContent); if (tx) return tx;
    const img = el.querySelector('img[alt]'); if (img && norm(img.alt)) return norm(img.alt);
    const svg = el.querySelector('svg title'); if (svg && norm(svg.textContent)) return norm(svg.textContent);
    return norm(el.getAttribute('title') || el.value || '');
  };
  const targetOf = (el) => {
    let t = el.getAttribute('href');
    if (t === null || t === '' || t === '#' || /^javascript:/i.test(t)) t = '';
    if (!t) for (const k of ['data-href', 'data-url', 'data-route', 'data-path', 'data-target']) { const v = el.getAttribute(k); if (v) { t = v; break; } }
    if (!t) { const oc = el.getAttribute('onclick') || ''; const m = oc.match(/(?:location(?:\\.hash|\\.href)?\\s*=|navigateTo|switchTab|redirectTo|navigate|go|open)\\s*\\(?\\s*['"]([^'"]+)['"]/); if (m) t = m[1]; }
    if (t && !t.startsWith('#') && !/^[a-z]+:/i.test(t)) { try { const u = new URL(t, location.href); t = u.pathname + u.search + u.hash; } catch (e) {} }
    return t;
  };
  const cleanCls = (el) => [...el.classList].filter((c) => !/^(active|selected|current|on|is-|checked|cur)/i.test(c)).sort().join('.');
  const sig = (el) => el.tagName + '.' + cleanCls(el) + '/' + el.children.length;
  const rowOf = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const p = n.parentElement; if (!p) break;
      const same = [...p.children].filter((c) => sig(c) === sig(n));
      if (same.length >= 2) return n;
    }
    return null;
  };
  const uid = new Map(); let nextId = 1;
  const id = (el) => { if (!uid.has(el)) uid.set(el, nextId++); return uid.get(el); };
  // 面包屑是导航路径，不是入口：容器的无障碍名称、类名或 id 带 breadcrumb / crumb / 面包屑，或标了 BreadcrumbList
  const CRUMB = '[aria-label*="面包屑"], [aria-label*="breadcrumb" i], [class*="breadcrumb" i], [class*="crumb" i], [id*="crumb" i], [itemtype*="BreadcrumbList" i]';
  const all = [...document.querySelectorAll(SEL)].filter(visible);
  const set = new Set(all);
  const items = [];
  for (const el of all) {
    const name = nameOf(el), target = targetOf(el);
    if (!name && !target) continue;
    let dup = false;
    for (let a = el.parentElement; a; a = a.parentElement) { if (set.has(a) && targetOf(a) === target && nameOf(a) === name) { dup = true; break; } }
    if (dup) continue;
    const row = rowOf(el);
    const r = el.getBoundingClientRect();
    items.push({ id: id(el), tag: el.tagName.toLowerCase(), role: el.getAttribute('role') || '', name, target, cls: cleanCls(el).slice(0, 60), crumb: !!el.closest(CRUMB),
      nested: !!row && row !== el, isRow: row === el, rowParent: row && row.parentElement ? id(row.parentElement) : 0, rowId: row ? id(row) : 0,
      rowText: row ? norm(row.innerText || row.textContent) : '', x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) });
  }
  // 标签栏：底部固定或类名像标签栏，里面有 2–6 个可点元素
  const clickInside = (c) => items.filter((i) => { const e = [...uid.entries()].find(([, v]) => v === i.id); return e && c.contains(e[0]); });
  const tabbars = [];
  const cands = [...document.querySelectorAll('nav, [role="tablist"], [class*="tabbar" i], [class*="tab-bar" i], [class*="bottom-nav" i], [class*="bottomnav" i], [id*="tabbar" i], [id*="tab-bar" i], body *')]
    .filter((c) => { const cs = getComputedStyle(c); const r = c.getBoundingClientRect();
      const named = /tab-?bar|bottom-?nav|footer-?nav|tabs-bottom/i.test(c.className + ' ' + c.id);
      const pinned = (cs.position === 'fixed' || cs.position === 'sticky') && r.bottom >= innerHeight - 2 && r.width >= innerWidth * 0.7 && r.height < 140;
      return (named && r.bottom >= innerHeight * 0.6 || pinned) && r.width > 0; });
  for (const c of cands) { const inside = clickInside(c); if (inside.length >= 2 && inside.length <= 6) tabbars.push({ box: c, ids: inside.map((i) => i.id) }); }
  const tabIds = new Set(); const tabGroups = [];
  for (const g of tabbars) { if (g.ids.every((i) => tabIds.has(i))) continue; g.ids.forEach((i) => tabIds.add(i)); tabGroups.push(g.ids); }
  // 金刚区或宫格：4 个以上等宽兄弟，文字短，带图标，至少两个在同一行
  const docks = []; const dockIds = new Set();
  for (const c of document.querySelectorAll('div, ul, section, nav, ol')) {
    const kids = [...c.children]; if (kids.length < 4 || kids.length > 24) continue;
    const found = kids.map((k) => items.find((i) => { const e = [...uid.entries()].find(([, v]) => v === i.id); return e && (e[0] === k || k.contains(e[0])); })).filter(Boolean);
    if (found.length < 4 || found.length < kids.length * 0.8) continue;
    if (found.some((i) => tabIds.has(i.id))) continue;
    if (!kids.every((k) => norm(k.innerText || k.textContent).length <= 8)) continue;
    if (!kids.every((k) => k.querySelector('img, svg, i, [class*="icon" i], [class*="ico" i]') || /[\\u{1F300}-\\u{1FAFF}\\u2600-\\u27BF]/u.test(k.textContent))) continue;
    const tops = found.map((i) => i.y); if (new Set(tops.map((y) => Math.round(y / 8))).size === tops.length) continue;
    const key = found.map((i) => i.id).join(','); if (docks.some((d) => d.key === key)) continue;
    docks.push({ key, ids: found.map((i) => i.id) }); found.forEach((i) => dockIds.add(i.id));
  }
  items.forEach((i) => { i.zone = tabIds.has(i.id) ? 'tabbar' : (dockIds.has(i.id) ? 'dock' : 'other'); });
  return { items, tabGroups, docks: docks.map((d) => d.ids), viewport: [innerWidth, innerHeight] };
}"""


def entrances_of(items: list[dict]) -> list[dict]:
    """面包屑是导航路径，不是入口：不进重复检查（面包屑与侧栏、页内按钮、卡片同目的地都不报）。侧栏项与页内按钮、卡片同目的地仍然要报。"""
    return [i for i in items if not i.get("crumb")]


def find_duplicates(items: list[dict]) -> tuple[list[dict], int]:
    """按目的地（没有目的地时按名称）归并；列表里每张卡的同名操作（嵌在重复的同构行里、行里还有别的内容）不算重复；面包屑不算入口。"""
    items = entrances_of(items)
    groups: dict[str, list[dict]] = {}
    for i in items:
        target = norm_dest(i.get("target"))
        key = f"to:{target}" if target else (f"name:{i['name']}" if i.get("name") else "")
        if key:
            groups.setdefault(key, []).append(i)
    problems, ignored = [], 0
    for key, members in groups.items():
        if len(members) < 2:
            continue
        rows = {m.get("rowId") for m in members}
        repeated_items = all(m.get("nested") and len(m.get("rowText", "")) > len(m.get("name", "")) + 2 for m in members) and len(rows) == len(members)
        if repeated_items:
            ignored += len(members)
            continue
        problems.append({"kind": "重复目的地" if key.startswith("to:") else "重复的同名入口", "target": key.split(":", 1)[1],
                         "count": len(members), "names": sorted({m["name"] for m in members if m.get("name")}),
                         "where": [f"{m.get('zone', 'other')}「{m.get('name') or m.get('tag')}」" for m in members]})
    return problems, ignored


def dock_findings(items: list[dict], role: str = "home") -> list[dict]:
    items = entrances_of(items)
    tabs = [i for i in items if i.get("zone") == "tabbar"]
    docks = [i for i in items if i.get("zone") == "dock"]
    tab_names = {i["name"] for i in tabs if i.get("name")}
    tab_targets = {norm_dest(i.get("target")) for i in tabs} - {""}
    out = []
    for d in docks:
        name, target = d.get("name", ""), norm_dest(d.get("target"))
        if name in tab_names or (target and target in tab_targets):
            out.append({"kind": "金刚或宫格里有标签栏同名项", "name": name, "target": d.get("target", "")})
        if role != "home":
            continue
        for label, words in (("账户类", ACCOUNT_WORDS), ("订单类", ORDER_WORDS), ("上下文类", CONTEXT_WORDS)):
            hit = next((w for w in words if w in name), None)
            if hit:
                out.append({"kind": f"金刚区里有{label}入口（应归{'我的' if label != '上下文类' else '顶部上下文栏'}）", "name": name, "keyword": hit, "target": d.get("target", "")})
    return out


def open_browser(pw):
    last = None
    for kw in ({"channel": "msedge"}, {}):
        try:
            return pw.chromium.launch(ignore_default_args=["--hide-scrollbars"], **kw)
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise RuntimeError(f"没有可用的浏览器（需要 Microsoft Edge 或 Playwright 的 Chromium）：{last}")


def collect_page(source: str, hashes: list[str], width: int, settle: int) -> list[tuple[str, dict]]:
    """每个 hash 各取一次可点击元素；不给 hash 就取页面本身。返回 [(hash, 快照)]。"""
    from playwright.sync_api import sync_playwright
    url = source if re.match(r"^(file|https?)://", source) else Path(source).resolve().as_uri()
    snaps: list[tuple[str, dict]] = []
    with sync_playwright() as pw:
        browser = open_browser(pw)
        try:
            context = browser.new_context(viewport={"width": width, "height": 844}, locale="zh-CN")
            page = context.new_page()
            page.goto(url)
            page.wait_for_timeout(settle)
            for h in hashes or [""]:
                if h:
                    page.evaluate("(h) => { location.hash = h }", h)
                    page.wait_for_timeout(settle)
                snaps.append((h, page.evaluate(CLICKABLES)))
        finally:
            browser.close()
    return snaps


def cmd_check_page(args) -> int:
    try:
        snaps = collect_page(args.page, args.hash, args.width, args.settle)
    except RuntimeError as exc:
        print(f"check page: {exc}", file=sys.stderr)
        return 2
    problems: list[dict] = []
    for h, snap in snaps:
        items = snap["items"]
        dups, ignored = find_duplicates(items)
        found = list(dups) + dock_findings(items, args.role)
        if h:
            for f in found:
                f["hash"] = h
        problems += found
        if args.verbose:
            print(f"{h or '页面'}：可点击元素 {len(items)} 个，标签栏 {len(snap['tabGroups'])} 处，宫格 {len(snap['docks'])} 处，列表行内的同构操作忽略 {ignored} 个，面包屑里的 {sum(1 for i in items if i.get('crumb'))} 个不算入口", file=sys.stderr)
    if problems:
        print(json.dumps(problems, ensure_ascii=False, indent=1))
        return 1
    print("check page: ok")
    return 0


# ---------------------------------------------------------------- main

def read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"读不了 {path}：{exc}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="列出范式、类型、页面、规则、区域")
    s.add_argument("what", nargs="?", choices=["paradigms", "types", "pages", "rules", "zones", "all"])
    s = sub.add_parser("show", help="完整说明；id 可写 kind:id（paradigm、type、page、rule、zone、function），method 看思考方法，entrances 看入口表格式")
    s.add_argument("id")
    s = sub.add_parser("recommend", help="按应用类型给首页推荐模块序列与金刚区列行")
    s.add_argument("--type", required=True)
    s.add_argument("--functions", type=int, help="并列高频核心入口的数量")
    s.add_argument("--tabs", type=int, help="标签栏项数")
    s.add_argument("--width", type=int, default=375)
    s.add_argument("--label-chars", type=int, default=4, help="入口最长文案字数")
    s = sub.add_parser("brief", help="功能清单加入口表合成首页简报")
    s.add_argument("--features")
    s.add_argument("--entrances", required=True)
    s.add_argument("--type", required=True)
    s.add_argument("--width", type=int, default=375)
    s.add_argument("--out", required=True)
    s = sub.add_parser("plan", help="按区域规则把功能分配到首页，输出方案 spec")
    s.add_argument("--brief", required=True)
    s.add_argument("--out")
    s.add_argument("--width", type=int)
    s = sub.add_parser("check", help="对方案 spec 做硬规则检查")
    s.add_argument("spec")
    s = sub.add_parser("check-page", help="用真实浏览器检查页面里的重复入口与宫格内容")
    s.add_argument("page")
    s.add_argument("--hash", action="append", default=[])
    s.add_argument("--width", type=int, default=390)
    s.add_argument("--role", choices=["home", "mine", "other"], default="home", help="home 额外检查金刚区的账户类、订单类、上下文类入口；mine 与 other 只查重复")
    s.add_argument("--settle", type=int, default=1200)
    s.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    data = load()
    if args.cmd == "list":
        return cmd_list(args, data)
    if args.cmd == "show":
        return cmd_show(args, data)
    if args.cmd == "recommend":
        print_recommend(recommend(data, args.type, args.functions, args.tabs, args.width, args.label_chars))
        return 0
    if args.cmd == "brief":
        brief = make_brief(read_json(args.features) if args.features else None, read_json(args.entrances), args.type, data, args.width)
        Path(args.out).write_text(json.dumps(brief, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"简报已写入 {args.out}：入口 {len(brief['entrances'])} 个，标签栏 {brief['tab_count']} 项")
        for w in brief["warnings"]:
            print(f"  ! {w}")
        return 0
    if args.cmd == "plan":
        spec = make_plan(read_json(args.brief), data, args.width)
        print_plan(spec)
        if args.out:
            Path(args.out).write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"方案已写入 {args.out}")
        return 0
    if args.cmd == "check":
        return print_findings(check_spec(read_json(args.spec), data), "page pattern check")
    if args.cmd == "check-page":
        return cmd_check_page(args)
    return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
