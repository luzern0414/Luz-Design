#!/usr/bin/env python3
"""原型生成器：规格 JSON（加可选内容模块）→ 单文件 HTML。

    py -X utf8 scripts/build_prototype.py <spec.json> [--out FILE] [--content content.js] [--check]

``--check`` 只校验不构建。校验只查结构与引用关系，不查行业内容，也不要求任何固定的页面、模块或入口（购物车、订单、搜索……都不是必填）：
规格引用了不存在的页面、标签栏页面不存在、back/done/go 指向不存在的页面、go/replace 指向标签栏页面、二级页放进标签栏、孤岛页面（从标签进不去）、
同一页同一目的地多个入口、组件编号不在库里、流程引用不存在的页面、缺逻辑字段，逐类中文报错。构建时先做同样的校验，有错就不出文件。输出默认在
``references/prototype-templates/dist/<规格目录名>.html``（该目录被 .gitignore 忽略，生成物不入库）。

结构与接口见 references/prototype-templates/engine/ENGINE.md：共用引擎在 engine/，每种 kind 在 <kind>/build_kind.py 里提供
``build(spec, ctx) -> dict``（css、js、stage_html、可选 head），可选 ``check(spec, ctx) -> list[str]`` 与 ``TABS_KEY``。
组件库嵌入靠组件编号 → 源文件的静态索引：只带规格与内容模块里用到的 blocks-*.js（连文件头一起带）和实际存在的素材。
"""
from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TEMPLATES = REPO / "references" / "prototype-templates"
ENGINE = TEMPLATES / "engine"
LIBRARY = REPO / "references" / "component-library"
SCHEMA = TEMPLATES / "schema" / "prototype.schema.json"
sys.path.insert(0, str(HERE))

CID_RE = re.compile(r"\b((?:MP|AD)-[A-Z]+-\d{3})\b")
ICON_STYLES = ("3d", "real", "flat")
LOGIC_REQUIRED = ("from", "back", "done", "primary", "rules")
NAV_KEYS = ("go", "replace", "tab", "sheet")


# ------------------------------------------------------------------ 组件编号 → 源文件的静态索引

def component_index(library: Path = LIBRARY) -> dict[str, str]:
    """编号 → 源文件名。blocks-*.js 里 ``id: 'XX-YYY-NNN'`` 逐个登记；旧 52 个编号来自 taxonomy.js 的 LEGACY 表，对应 blocks1-3.js。"""
    src = library / "src"
    index: dict[str, str] = {}
    for f in sorted(src.glob("blocks-*.js")):
        for m in re.finditer(r"\bid:\s*'((?:MP|AD)-[A-Z]+-\d{3})'", f.read_text(encoding="utf-8")):
            index.setdefault(m.group(1), f.name)
    tax = (src / "taxonomy.js").read_text(encoding="utf-8")
    legacy = tax[tax.index("const LEGACY = {"):]
    legacy = legacy[: legacy.index("\n}")]
    for cid in re.findall(r"'((?:MP|AD)-[A-Z]+-\d{3})'", legacy):
        index.setdefault(cid, "blocks1.js")
    return index


def library_themes(library: Path = LIBRARY) -> dict[str, dict[str, str]]:
    kit = (library / "src" / "kit.js").read_text(encoding="utf-8")
    return {m.group(1): {"name": m.group(2), "p": m.group(3)} for m in re.finditer(r"\{\s*id:\s*'(\w+)',\s*name:\s*'([^']+)',\s*p:\s*'(#[0-9A-Fa-f]{6})'", kit)}


# ------------------------------------------------------------------ JSON Schema（有 jsonschema 用它，否则用内置子集）

def _type_ok(value: Any, t: str) -> bool:
    return {
        "object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str), "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool), "number": isinstance(value, (int, float)) and not isinstance(value, bool), "null": value is None,
    }[t]


def validate_schema(value: Any, schema: dict, root: dict, path: str = "$") -> list[str]:
    """JSON Schema 子集：$ref(本地)、type、enum、const、required、properties、additionalProperties、items、minItems、maxItems、pattern、minLength、minimum、maximum、oneOf、anyOf、allOf、if/then、uniqueItems。"""
    errs: list[str] = []
    if "$ref" in schema:
        node: Any = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return validate_schema(value, node, root, path)
    for sub in schema.get("allOf", []):
        errs += validate_schema(value, sub, root, path)
    if "if" in schema and not validate_schema(value, schema["if"], root, path) and "then" in schema:
        errs += validate_schema(value, schema["then"], root, path)
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(value, t) for t in types):
            return [f"{path}：类型应为 {' 或 '.join(types)}，实际是 {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}：应为固定值「{schema['const']}」，实际是「{value}」")
    if "enum" in schema and value not in schema["enum"]:
        hint = (schema.get("x-enumHints") or {}).get(str(value))
        errs.append(f"{path}：「{value}」不在允许的取值里（{' / '.join(map(str, schema['enum']))}）" + (f"；{hint}" if hint else ""))
    for key, check in (("anyOf", any), ("oneOf", lambda it: sum(1 for _ in it) == 1)):
        if key in schema:
            ok = [not validate_schema(value, s, root, path) for s in schema[key]]
            if not (check(ok) if key == "anyOf" else sum(ok) == 1):
                errs.append(f"{path}：不符合任何一种允许的写法（{key}）")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}：「{value}」格式不对（要求 {schema['pattern']}）")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}：不能为空" if schema["minLength"] == 1 else f"{path}：至少 {schema['minLength']} 个字符")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}：不能小于 {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}：不能大于 {schema['maximum']}")
    if isinstance(value, dict):
        for r in schema.get("required", []):
            if r not in value:
                errs.append(f"{path}：缺少必填字段「{r}」")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errs += validate_schema(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}：多余的字段「{k}」（拼写对吗？）")
            elif isinstance(schema.get("additionalProperties"), dict):
                errs += validate_schema(v, schema["additionalProperties"], root, f"{path}.{k}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errs.append(f"{path}：至少 {schema['minItems']} 项")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errs.append(f"{path}：最多 {schema['maxItems']} 项")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True, ensure_ascii=False) for x in value}) != len(value):
            errs.append(f"{path}：有重复项")
        if "items" in schema:
            for i, v in enumerate(value):
                errs += validate_schema(v, schema["items"], root, f"{path}[{i}]")
    return errs


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ 规格里的跳转与入口

def split_target(value: Any) -> tuple[str, str]:
    s = str(value)
    head, _, arg = s.partition(":")
    return head, arg


def action_edges(steps: Any, out: list[tuple[str, str]]) -> None:
    """声明式动作里的导航步骤：[(kind, target)]。"""
    for st in steps or []:
        if not isinstance(st, dict) or not st:
            continue
        k, v = next(iter(st.items()))
        if k in NAV_KEYS:
            out.append((k, split_target(v)[0]))
        elif k == "done" and v not in (True, None):
            out.append(("done", str(v)))
        elif k == "branch" and isinstance(v, dict):
            for arm in list((v.get("cases") or {}).values()) + [v.get("default") or []]:
                action_edges(arm, out)


def block_lists(page: dict) -> list[tuple[str, list]]:
    return [(k, page[k]) for k in ("blocks", "header", "footer") if isinstance(page.get(k), list)]


def page_entries(page: dict) -> list[dict]:
    """页面声明的入口：{where, kind(go|replace|tab|sheet|act), target, all(是否 @* 全部匹配的列表行)}。"""
    out: list[dict] = []
    for area, lst in block_lists(page):
        for i, it in enumerate(lst):
            if not isinstance(it, dict):
                continue
            for k in (*NAV_KEYS, "act"):
                if isinstance(it.get(k), dict):
                    for sel, val in it[k].items():
                        tgt = str(val) if k == "act" else str(val)
                        out.append({"where": f"{area}[{i}] {it.get('cid') or it.get('custom') or ''} {k}「{sel}」", "kind": k, "target": tgt, "all": sel.endswith("@*")})
    return out


def collect(spec: dict) -> dict:
    """汇总规格里所有页面引用，给校验用。edges[pid] = 该页能到的页面 id 集合（只算真实声明的跳转）。"""
    pages = {p["id"]: p for p in spec.get("pages", []) if isinstance(p, dict) and "id" in p}
    actions = spec.get("actions") or {}
    nodes = flatten_tabs(spec.get(tabs_key(spec), []))
    tabs = [t for t in nodes if t.get("page")]  # 带 page 的才是标签；没有 page 的是分组节点
    tab_pages = {t.get("page") for t in tabs}
    tab_ids = {t.get("id") for t in tabs}
    act_targets: dict[str, list[tuple[str, str]]] = {}
    for name, steps in actions.items():
        lst: list[tuple[str, str]] = []
        action_edges(steps, lst)
        act_targets[name] = lst
    return {"pages": pages, "tabs": tabs, "nodes": nodes, "tab_pages": tab_pages, "tab_ids": tab_ids, "act_targets": act_targets}


def tabs_key(spec: dict) -> str:
    return "nav" if spec.get("kind") == "admin" else "tabbar"


def flatten_tabs(lst: list, out: list | None = None) -> list:
    out = [] if out is None else out
    for t in lst or []:
        if isinstance(t, dict):
            out.append(t)
            flatten_tabs(t.get("children"), out)
    return out


def used_cids(spec: dict, content_text: str) -> set[str]:
    found: set[str] = set(CID_RE.findall(json.dumps(spec, ensure_ascii=False)))
    found |= set(CID_RE.findall(content_text))
    return found


def check_spec(spec: dict, content_text: str = "", kind_mod: Any = None, ctx: Any = None, library: Path = LIBRARY) -> tuple[list[str], list[str]]:
    """共用检查，返回 (错误, 警告)。"""
    errs: list[str] = []
    warns: list[str] = []
    schema = load_schema()
    errs += validate_schema(spec, schema, schema)
    if errs:
        return errs, warns  # 结构不对时后面的检查没有意义
    c = collect(spec)
    pages, tab_ids, tab_pages, act_targets = c["pages"], c["tab_ids"], c["tab_pages"], c["act_targets"]
    ids = [p["id"] for p in spec["pages"]]
    for pid in sorted({i for i in ids if ids.count(i) > 1}):
        errs.append(f"页面 id「{pid}」重复了，每个页面的 id 必须唯一")
    index = component_index(library)

    # --- 标签栏 / 菜单
    key = tabs_key(spec)
    tabs = c["tabs"]
    if not tabs:
        errs.append(f"规格里没有「{key}」：引擎靠标签切换一级页，至少要有一个标签（只有一个页面也放进去）")
    seen_tab: set[str] = set()
    for i, t in enumerate(c["nodes"]):
        if t.get("id") in seen_tab:
            errs.append(f"{key} 里有两项的 id 都是「{t.get('id')}」，id 必须唯一")
        seen_tab.add(t.get("id"))
        if not t.get("page"):
            if not t.get("children"):
                errs.append(f"{key} 里的「{t.get('name') or t.get('id')}」既没有 page 也没有 children：分组节点必须有子项，标签必须有 page")
            continue
        pg = pages.get(t.get("page"))
        if pg is None:
            errs.append(f"{key} 里的「{t.get('name') or t.get('id')}」指向的页面「{t.get('page')}」不存在")
        elif pg.get("type") != "tab":
            errs.append(f"二级页不能出现在{('标签栏' if key == 'tabbar' else '侧栏菜单')}里：「{t.get('name') or t.get('id')}」指向的页面「{pg['id']}」类型是 {pg.get('type')}，应为一级页（tab）")
    for p in spec["pages"]:
        if p.get("type") == "tab" and p["id"] not in tab_pages:
            errs.append(f"一级页「{p['id']}」不在{('标签栏' if key == 'tabbar' else '侧栏菜单')}里（一级页只能由标签切换进入）")
        if p.get("type") != "tab" and p.get("tab") and p["tab"] not in tab_ids:
            errs.append(f"页面「{p['id']}」的 tab「{p['tab']}」不存在")
        elif p.get("type") != "tab" and not p.get("tab"):
            warns.append(f"页面「{p['id']}」没写 tab（所属标签），目录里会归到「其他」")
        for r in p.get("roles") or []:
            if r not in {x["id"] for x in spec.get("roles") or []}:
                errs.append(f"页面「{p['id']}」的 roles 里的角色「{r}」没有在 roles[] 里定义")

    # --- 组件编号
    for cid in sorted(used_cids(spec, content_text)):
        if cid not in index:
            where = [f"页面「{p['id']}」" for p in spec["pages"] if cid in json.dumps(p, ensure_ascii=False)]
            errs.append(f"组件编号「{cid}」不在组件库里{('（' + '、'.join(where[:3]) + '）') if where else '（内容模块里）'}")

    # --- 跳转目标
    def need_page(where: str, kind: str, target: str) -> None:
        if kind == "tab":
            if target not in tab_ids:
                if target in pages:
                    errs.append(f"{where}：tab 的目标「{target}」是页面 id，不是标签 id（标签：{'、'.join(sorted(map(str, tab_ids)))}）")
                else:
                    errs.append(f"{where}：tab 的目标标签「{target}」不存在")
            return
        pg = pages.get(target)
        if pg is None:
            errs.append(f"{where}：{kind} 指向的页面「{target}」不存在")
        elif kind in ("go", "replace") and pg.get("type") == "tab":
            errs.append(f"{where}：{kind} 的目标「{target}」是标签栏页面，不能压栈，请改用 tab（对应微信的 switchTab）")
        elif kind == "sheet" and pg.get("type") != "sheet":
            errs.append(f"{where}：sheet 的目标「{target}」不是弹层页（类型是 {pg.get('type')}）")

    for p in spec["pages"]:
        for e in page_entries(p):
            if e["kind"] == "act":
                if e["target"].split(":")[0] not in (spec.get("actions") or {}) and not content_text:
                    warns.append(f"页面「{p['id']}」{e['where']}：动作「{e['target']}」没有在 actions 里定义，也没有内容模块")
                continue
            need_page(f"页面「{p['id']}」{e['where']}", e["kind"], split_target(e["target"])[0])
        for ln in p.get("links") or []:
            tgt = split_target(ln)[0]
            if tgt not in pages and tgt not in tab_ids:
                errs.append(f"页面「{p['id']}」的 links 指向的页面「{ln}」不存在")
        lg = p.get("logic") or {}
        for field in ("back", "done"):
            v = lg.get(field)
            if isinstance(v, dict) and v.get("to") not in (None, "origin", "tab") and v["to"] not in pages:
                errs.append(f"页面「{p['id']}」logic.{field}.to 指向的页面「{v['to']}」不存在")
        for src in (lg.get("from") or {}).get("pages", []) if isinstance(lg.get("from"), dict) else []:
            if src not in pages:
                errs.append(f"页面「{p['id']}」logic.from.pages 里的页面「{src}」不存在")
        missing = [f for f in LOGIC_REQUIRED if f not in lg or lg[f] in ("", None, [])]
        if missing:
            errs.append(f"页面「{p['id']}」缺逻辑字段：{'、'.join('logic.' + m for m in missing)}（来源、返回、完成后、主操作、规则都要写，没有就写“无”）")
        ids_seen: dict[str, str] = {}
        for area, lst in block_lists(p):
            for i, it in enumerate(lst):
                mid = it.get("id") if isinstance(it, dict) else None
                if mid and mid in ids_seen:
                    errs.append(f"页面「{p['id']}」里模块标识「{mid}」重复了（{ids_seen[mid]} 与 {area}[{i}]），“模块显示”开关靠它区分模块")
                elif mid:
                    ids_seen[mid] = f"{area}[{i}]"
        if p.get("base") and p["base"] not in pages:
            errs.append(f"弹层页「{p['id']}」的 base「{p['base']}」不存在")
        empty = p.get("empty") or {}
        if empty.get("go") and empty["go"] not in pages:
            errs.append(f"页面「{p['id']}」的 empty.go 指向的页面「{empty['go']}」不存在")
        for sid in p.get("scenes") or []:
            if sid not in {s["id"] for s in spec.get("scenes") or []}:
                errs.append(f"页面「{p['id']}」的 scenes 里的场景「{sid}」没有在 scenes[] 里定义")
        if (p.get("custom") or any(isinstance(it, dict) and it.get("custom") for _, l in block_lists(p) for it in l)) and not p.get("links") and not content_text:
            warns.append(f"页面「{p['id']}」用了 custom 但没有内容模块")

    scene_ids = {s["id"] for s in spec.get("scenes") or []}
    role_ids = {r["id"] for r in spec.get("roles") or []}
    for name, steps in (spec.get("actions") or {}).items():
        lst: list[tuple[str, str]] = []
        action_edges(steps, lst)
        for kind, target in lst:
            if kind == "done":
                if target not in {f["id"] for f in spec.get("flows") or []}:
                    errs.append(f"动作「{name}」的 done 指向的流程「{target}」不存在")
            else:
                need_page(f"动作「{name}」", kind, target)
        _walk_steps(name, steps, scene_ids, role_ids, errs)
    for k in ("noticePage", "profilePage"):
        ref = (spec.get("shell") or {}).get(k)
        if ref and ref not in pages:
            errs.append(f"shell.{k} 指向的页面「{ref}」不存在")
    for r in spec.get("roles") or []:
        if r.get("deniedGo") and r["deniedGo"] not in pages:
            errs.append(f"角色「{r['id']}」的 deniedGo 指向的页面「{r['deniedGo']}」不存在")

    # --- 流程
    for f in spec.get("flows") or []:
        for pid in [f.get("start"), *(f.get("steps") or [])]:
            if pid and pid not in pages:
                errs.append(f"流程「{f['id']}」引用的页面「{pid}」不存在")
        if f.get("done") not in (None, "origin") and f["done"] not in pages:
            errs.append(f"流程「{f['id']}」的 done「{f['done']}」不存在（写 origin 或页面 id）")
        if f.get("start") and f.get("steps") and f["start"] not in f["steps"]:
            warns.append(f"流程「{f['id']}」的起点「{f['start']}」不在 steps 里")
    for g in spec.get("directory") or []:
        for ref in g.get("pages", []):
            if split_target(ref)[0] not in pages:
                errs.append(f"目录分组「{g.get('group')}」里的页面「{ref}」不存在")
    for s in spec.get("scenes") or []:
        vals = [o["v"] for o in s.get("options", [])]
        if s.get("default") is not None and s["default"] not in vals:
            errs.append(f"场景「{s['id']}」的默认值「{s['default']}」不在选项里")
        for pid in s.get("pages") or []:
            if pid not in pages:
                errs.append(f"场景「{s['id']}」的 pages 里的页面「{pid}」不存在")

    # --- kind 自己报出的页面之间的跳转边（kind 的 edges(page, spec) 钩子；list 行操作、工作台待办这类不在 blocks 覆盖里的跳转）
    kind_edges: dict[str, list[dict]] = {}
    if kind_mod is not None and hasattr(kind_mod, "edges"):
        for pid, p in pages.items():
            for ed in kind_mod.edges(p, spec) or []:
                ed = {"target": ed} if isinstance(ed, str) else dict(ed)
                tgt = split_target(ed.get("target", ""))[0]
                if tgt not in pages and tgt not in tab_ids:
                    errs.append(f"页面「{pid}」：kind 报出的跳转目标「{ed.get('target')}」不存在")
                    continue
                kind_edges.setdefault(pid, []).append(ed)
    # --- 孤岛页面：从标签页出发，沿声明的跳转到不了
    edges: dict[str, set[str]] = {pid: set() for pid in pages}
    for pid, p in pages.items():
        for e in page_entries(p):
            if e["kind"] == "act":
                for kind, target in act_targets.get(e["target"].split(":")[0], []):
                    if target in pages:
                        edges[pid].add(target)
            elif e["kind"] == "tab":
                tp = next((t.get("page") for t in c["tabs"] if t.get("id") == split_target(e["target"])[0]), None)
                if tp:
                    edges[pid].add(tp)
            else:
                edges[pid].add(split_target(e["target"])[0])
        for ln in p.get("links") or []:
            tgt = split_target(ln)[0]
            edges[pid].add(tgt if tgt in pages else next((t.get("page") for t in c["tabs"] if t.get("id") == tgt), tgt))
        for ed in kind_edges.get(pid, []):
            tgt = split_target(ed["target"])[0]
            edges[pid].add(tgt if tgt in pages else next((t.get("page") for t in c["tabs"] if t.get("id") == tgt), tgt))
        empty = p.get("empty") or {}
        if empty.get("go"):
            edges[pid].add(empty["go"])
    for r in spec.get("roles") or []:
        if r.get("deniedGo"):
            for pid, p in pages.items():
                if p.get("roles"):
                    edges[pid].add(r["deniedGo"])
    reach: set[str] = set()
    queue = deque(t.get("page") for t in c["tabs"] if t.get("page") in pages)
    while queue:
        cur = queue.popleft()
        if cur in reach:
            continue
        reach.add(cur)
        queue.extend(x for x in edges.get(cur, ()) if x in pages and x not in reach)
    for pid in pages:
        if pid not in reach:
            errs.append(f"孤岛页面「{pid}」（{pages[pid].get('name', '')}）：从任何标签页出发都到不了，没有入口。给它加入口，或者在来源页的 links 里声明跳转")

    # --- 同一页同一目的地多个入口（复用 page_pattern.find_duplicates）
    try:
        import page_pattern  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        page_pattern = None
    for pid, p in pages.items():
        items = []
        for e in page_entries(p):
            if e["kind"] == "act" or e["all"]:
                continue
            target = e["target"] if e["kind"] != "tab" else "tab:" + e["target"]
            items.append({"name": e["where"], "target": target, "zone": "other", "rowId": None, "nested": False, "rowText": ""})
            if p.get("type") == "tab" and e["kind"] == "tab" and e["target"] in tab_ids:
                errs.append(f"页面「{pid}」{e['where']}：标签栏已经有「{e['target']}」的入口，不要在页内重复")
        for ed in kind_edges.get(pid, []):
            if ed.get("dup"):  # kind 声明“这条边是一个入口”时才参与重复判定（列表每行的同名操作不算）
                items.append({"name": ed.get("name") or f"{pid} 的入口", "target": ed["target"], "zone": "other", "rowId": None, "nested": False, "rowText": ""})
        if page_pattern is not None:
            problems, _ = page_pattern.find_duplicates(items)
        else:
            seen: dict[str, list[dict]] = {}
            for it in items:
                seen.setdefault(it["target"], []).append(it)
            problems = [{"target": k, "count": len(v), "where": [i["name"] for i in v]} for k, v in seen.items() if len(v) > 1]
        for pr in problems:
            errs.append(f"页面「{pid}」同一目的地「{pr['target']}」有 {pr['count']} 个入口（{'；'.join(pr['where'])}），一页一个目的地只留一个入口")

    if kind_mod is not None and hasattr(kind_mod, "check"):
        for m in kind_mod.check(spec, ctx) or []:
            (warns if m.startswith("警告：") else errs).append(m)
    return errs, warns


def _walk_steps(name: str, steps: Any, scene_ids: set, role_ids: set, errs: list[str]) -> None:
    for st in steps or []:
        if not isinstance(st, dict) or not st:
            continue
        k, v = next(iter(st.items()))
        if k == "scene" and isinstance(v, dict) and v.get("id") not in scene_ids and v.get("id") != "view":
            errs.append(f"动作「{name}」设置的场景「{v.get('id')}」没有在 scenes[] 里定义")
        elif k == "role" and v not in role_ids:
            errs.append(f"动作「{name}」切换的角色「{v}」没有在 roles[] 里定义")
        elif k == "branch" and isinstance(v, dict):
            if v.get("scene") and v["scene"] not in scene_ids:
                errs.append(f"动作「{name}」的 branch 读的场景「{v['scene']}」没有在 scenes[] 里定义")
            for arm in list((v.get("cases") or {}).values()) + [v.get("default") or []]:
                _walk_steps(name, arm, scene_ids, role_ids, errs)


# ------------------------------------------------------------------ 构建

class Ctx:
    def __init__(self, spec: dict, spec_path: Path, kind_dir: Path, index: dict[str, str]):
        self.spec, self.spec_path, self.kind_dir = spec, spec_path, kind_dir
        self.engine_dir, self.library_dir, self.index = ENGINE, LIBRARY, index
        self.warnings: list[str] = []

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_kind(kind: str) -> Any:
    path = TEMPLATES / kind / "build_kind.py"
    if not path.is_file():
        raise SystemExit(f"没有「{kind}」模板：找不到 {path.relative_to(REPO)}")
    spec = importlib.util.spec_from_file_location(f"build_kind_{kind}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def data_uri(path: Path) -> str:
    mime = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def assets_js(spec: dict, spec_path: Path, library: Path = LIBRARY) -> str:
    """库素材 + 规格 assets.dir 里的素材（同名覆盖，多出的追加）。assets.bgKeys 限定背景图集合。"""
    base = library / "assets"
    icons: dict[str, dict[str, str]] = {s: {} for s in ICON_STYLES}
    prod: dict[int, str] = {}
    bg: dict[str, str] = {}
    layers = [base]
    cfg = spec.get("assets") or {}
    if cfg.get("dir"):
        layer = (spec_path.parent / cfg["dir"]).resolve()
        if not layer.is_dir():
            raise SystemExit(f"assets.dir 不存在：{layer}")
        layers.append(layer)
    for layer in layers:
        for s in ICON_STYLES:
            for f in sorted((layer / "icons" / s).glob("*.*")) if (layer / "icons" / s).is_dir() else []:
                icons[s][f.stem] = data_uri(f)
        for f in sorted((layer / "products").glob("p*.*")) if (layer / "products").is_dir() else []:
            if f.stem[1:].isdigit():
                prod[int(f.stem[1:])] = data_uri(f)
        for f in sorted((layer / "bg").glob("*.*")) if (layer / "bg").is_dir() else []:
            bg[f.stem] = data_uri(f)
    if cfg.get("bgKeys"):
        bg = {k: bg[k] for k in cfg["bgKeys"] if k in bg}
    prods = [prod[i] for i in sorted(prod)]
    return "const ASSETS=" + json.dumps({"icons": icons, "prod": prods, "bg": bg}, ensure_ascii=False, separators=(",", ":"))


LIB_EXPORTS = (
    "BLOCKS, GUIDES, THEMES, themeVars, applyTheme, mixc, ASSETS, LINE, sv, lineSvg, icon, tileHTML, IC, ICS, ICON_STYLES, ICON_LABEL, ICON_NAMES, "
    "critter, P, prod, priceHTML, IX, NAMES, ORDER_ROWS, PRODUCTS, SKUS, setAppearance, getAppearance, isDark, APPEARANCES, "
    "setIconStyle(v) { ICON_STYLE = v }, get iconStyle() { return ICON_STYLE }"
)


def lib_js(spec: dict, spec_path: Path, cids: set[str], index: dict[str, str], library: Path = LIBRARY) -> tuple[str, list[str]]:
    """把组件库封进一个 IIFE（LIB）。只带用到的 blocks-*.js；blocks1-3 与核心总是带。"""
    src = library / "src"
    read = lambda n: (src / n).read_text(encoding="utf-8")  # noqa: E731
    files = sorted({index[c] for c in cids if c in index and index[c] != "blocks1.js"})
    legacy_used = any(index.get(c) == "blocks1.js" for c in cids)
    if legacy_used:
        files = sorted(set(files) | {"blocks-zz-legacy-ix.js"})
    extra = ";\n".join(read(f) for f in files)
    legacy = "\n".join(read(f) for f in ("blocks1.js", "blocks2.js", "blocks3.js"))
    code = "\n".join([assets_js(spec, spec_path, library), read("kit.js"), read("taxonomy.js"), read("core-def.js"), read("extras.js"), read("ix.js"), legacy + ";\n" + extra])
    return "const LIB = (() => {\n" + code + "\nreturn { " + LIB_EXPORTS + " }\n})()", files


def demote_h1_markup(text: str) -> tuple[str, int]:
    """整个文档只留外壳里的一个 h1：嵌进来的 JS（内容模块、库、kind 运行时）里写的 ``<h1 …>…</h1>`` 降成 ``<h2 data-h1 …>…</h2>``。
    外观不变：引擎 CSS 里 ``h2[data-h1]`` 沿用 h1 的默认字号（零特异性），内容 CSS 里的 ``h1`` 选择器同步改写（见 demote_h1_css）。"""
    n = len(re.findall(r"<h1(?=[\s>/])", text))
    text = re.sub(r"<h1(?=[\s>/])", "<h2 data-h1", text)
    return re.sub(r"</h1>", "</h2>", text), n


def demote_h1_css(text: str) -> tuple[str, int]:
    """CSS 里的 ``h1`` 选择器改成 ``h2:where([data-h1])``：:where 的特异性为 0，所以整条选择器的特异性与原来的 ``h1`` 相同，层叠结果不变。注释里的不动。"""
    count = 0
    parts = re.split(r"(/\*.*?\*/)", text, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i], k = re.subn(r"(?<![\w\-.#\[\"'])h1(?![\w\-])(?=[\s,{:.>+~\[)]|$)", "h2:where([data-h1])", parts[i])
        count += k
    return "".join(parts), count


def js_literal(spec: dict) -> str:
    text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"))
    return text.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def favicon(spec: dict, mark: str, library: Path = LIBRARY) -> str:
    themes = library_themes(library)
    color = themes.get((spec.get("theme") or {}).get("id", "rose"), {"p": "#A85D79"})["p"]
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='9' fill='#F4F4F5'/>"
           f"<g fill='none' stroke='{color}' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>{mark}</g></svg>")
    return "data:image/svg+xml," + quote(svg, safe="/:=,;'()- ")


def build(spec_path: Path, out: Path, content_path: Path | None = None, check_only: bool = False) -> int:
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"读不了规格 {spec_path}：{exc}", file=sys.stderr)
        return 2
    if content_path is None and isinstance(spec, dict) and spec.get("content"):
        content_path = (spec_path.parent / spec["content"]).resolve()
    content = content_path.read_text(encoding="utf-8") if content_path and content_path.is_file() else ""
    if content_path and not content_path.is_file():
        print(f"内容模块不存在：{content_path}", file=sys.stderr)
        return 2
    kind = spec.get("kind") if isinstance(spec, dict) else None
    if kind not in ("mini", "admin"):
        print(f"规格的 kind 要写 mini 或 admin（现在是 {kind!r}）", file=sys.stderr)
        return 1
    index = component_index()
    mod = load_kind(kind)
    ctx = Ctx(spec, spec_path, TEMPLATES / kind, index)
    errs, warns = check_spec(spec, content, mod, ctx)
    for w in warns:
        print("警告：" + w.removeprefix("警告："))
    if errs:
        for e in errs:
            print("错误：" + e)
        print(f"校验未通过：{len(errs)} 处错误")
        return 1
    print(f"规格校验通过：{len(spec['pages'])} 个页面，{len(warns)} 条警告")
    if check_only:
        return 0

    if spec.get("shell"):  # 顶层 shell 并进 data.shell（运行时从 data.shell 读；同名键以 data.shell 为准）
        data_shell = spec.setdefault("data", {}).setdefault("shell", {})
        for k, v in spec["shell"].items():
            data_shell.setdefault(k, v)
    seg = mod.build(spec, ctx)
    cids = used_cids(spec, content) | set(seg.get("cids", []))
    lib, files = lib_js(spec, spec_path, cids, index)
    # 同一时刻整个文档只有一个 h1（外壳里的产品名）：嵌进来的内容模块、库、kind 的 <h1> 降成 <h2 data-h1>，外观不变
    lib, n_lib = demote_h1_markup(lib)
    seg["js"], n_kind = demote_h1_markup(seg.get("js", ""))
    content, n_content = demote_h1_markup(content)
    seg["css"], n_kcss = demote_h1_css(seg.get("css", ""))
    shell = (ENGINE / "shell.template.html").read_text(encoding="utf-8")
    meta = spec["meta"]
    content_css_path = content_path.with_suffix(".css") if content_path else None
    content_css = content_css_path.read_text(encoding="utf-8") if content_css_path and content_css_path.is_file() else ""
    content_css, n_ccss = demote_h1_css(content_css)
    for label, n in (("组件库", n_lib), ("kind 运行时", n_kind), ("内容模块", n_content), ("kind 样式", n_kcss), ("内容样式", n_ccss)):
        if n:
            ctx.warn(f"{label}里有 {n} 处 h1，已降为 h2[data-h1]（整个文档只留外壳的一个 h1，外观不变）")
    slots = {
        "KIT_CSS": (LIBRARY / "src" / "kit.css").read_text(encoding="utf-8"), "IX_CSS": (LIBRARY / "src" / "ix.css").read_text(encoding="utf-8"),
        "ENGINE_CSS": (ENGINE / "engine.css").read_text(encoding="utf-8"), "KIND_CSS": seg.get("css", ""), "CONTENT_CSS": content_css,
        "STAGE_HTML": seg.get("stage_html", ""), "LIB_JS": lib, "ENGINE_JS": (ENGINE / "engine.js").read_text(encoding="utf-8"),
        "KIND_JS": ";(function (K, LIB) {\n" + seg.get("js", "") + "\n})(K, LIB)", "SPEC_JSON": js_literal(spec),
        "CONTENT_JS": (";(function (K, LIB) {\n" + content + "\n})(K, LIB)") if content else "",
    }
    mark = meta.get("mark") or getattr(mod, "DEFAULT_MARK", "<circle cx='16' cy='16' r='9'/>")
    tokens = {
        "LANG": meta.get("lang", "zh-CN"), "TITLE": meta["title"], "SUBTITLE": meta.get("subtitle", ""), "VERSION": meta.get("version", ""), "KIND": kind,
        "DARKMODE": "tokens", "MARK": mark, "FAVICON": favicon(spec, mark), "HEAD": seg.get("head", ""),
    }
    page = shell
    for k, v in tokens.items():
        page = page.replace("{{" + k + "}}", str(v).replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;") if k in ("TITLE", "SUBTITLE", "VERSION") else str(v))
    for k, v in slots.items():
        page = page.replace(f"/*__{k}__*/", v)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out}  {round(out.stat().st_size / 1024)} KB  组件库文件：{['blocks1-3.js'] + files}")
    for w in ctx.warnings:
        print("警告：" + w)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="规格 JSON")
    ap.add_argument("--out", help="输出 HTML（默认 references/prototype-templates/dist/<规格所在目录名>.html）")
    ap.add_argument("--content", help="内容模块 JS（默认取规格里的 content 字段）")
    ap.add_argument("--check", action="store_true", help="只校验不构建")
    a = ap.parse_args(argv)
    spec_path = Path(a.spec).resolve()
    out = Path(a.out) if a.out else TEMPLATES / "dist" / f"{spec_path.parent.name}.html"
    return build(spec_path, out, Path(a.content).resolve() if a.content else None, a.check)


if __name__ == "__main__":
    raise SystemExit(main())
