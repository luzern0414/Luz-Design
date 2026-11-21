#!/usr/bin/env python3
"""Number registry of the template library: app, web, poster, prompts, documents.

Every reusable thing carries a number that is read from the files themselves, so the registry cannot drift:

  App / Web   data-cid="AP-BTN-001" / "WB-TABL-003" in templates/<end>/source/pages/*.html and source/parts/*.part
  海报        templates/poster/source/templates/PS-001-名称.html, data-cid="PS-001" on the canvas
  提示词      templates/poster/source/prompts/prompts.json, id "PP-001"
  文件        templates/documents/<word|excel|slides|pdf|reading>/manifest.json, id "DC-WD-001"; parts "DC-WD-P01"
  PPT 原版    templates/documents/slides/originals/manifest.json, id "DC-SL-O001"

  py -X utf8 scripts/template_registry.py list [--kind app|web|poster|prompt|document] [--cat BTN] [--page home] [--query 词]
  py -X utf8 scripts/template_registry.py show AP-BTN-004        print the component's HTML and the page-local CSS it needs
  py -X utf8 scripts/template_registry.py show PS-003            print the poster's file, size, use and how to take it
  py -X utf8 scripts/template_registry.py show PP-012            print the prompt text and its parameters
  py -X utf8 scripts/template_registry.py show DC-WD-002         print the document template, spec, sample, generator and checks
  py -X utf8 scripts/template_registry.py check                  ids unique, well-formed, domain matches the folder
  py -X utf8 scripts/template_registry.py write [--check]        refresh references/template-registry.json and kit/registry.js

Numbers are never renumbered or reused once issued; a new item takes the next free number of its domain.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
REGISTRY = ROOT / "references" / "template-registry.json"
REGISTRY_JS = ROOT / "kit" / "registry.js"  # the same list for the index pages, which cannot fetch a local json file
ENDS = {"app": "AP", "web": "WB"}
PAGE_DOMAINS = {"HOME": "首页", "LIST": "列表", "ORDR": "订单", "MINE": "我的", "AGNT": "智能体", "NAV": "导航"}
COMPONENT_DOMAINS = {
    "BTN": "按钮", "BGND": "背景", "CARD": "卡片", "ENTR": "入口", "NAVI": "导航组件", "FORM": "表单", "ROWS": "列表行",
    "DATA": "数据与图表", "FEED": "反馈与状态", "CHAT": "智能体", "MOTN": "动效", "LAYT": "布局壳", "TABL": "表格",
}
DOMAINS = {**PAGE_DOMAINS, **COMPONENT_DOMAINS}
PAGE_OF = {"home": "HOME", "list": "LIST", "orders": "ORDR", "mine": "MINE", "agent": "AGNT"}
DOC_TYPES = {"word": "WD", "excel": "XL", "slides": "SL", "pdf": "PD", "reading": "RD"}
ID_RE = re.compile(r"^(AP|WB)-([A-Z]{3,4})-(\d{3})$")
PS_RE = re.compile(r"^PS-(\d{3})$")
PP_RE = re.compile(r"^PP-(\d{3})$")
DC_RE = re.compile(r"^DC-(WD|XL|SL|PD|RD)-(\d{3}|P\d{2}|O\d{3})$")
TAG_RE = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*?)(/?)>")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
CJK = re.compile(r"[一-鿿]")


def attr(attrs: str, name: str) -> str | None:
    m = re.search(r'(?<![\w-])' + re.escape(name) + r'\s*=\s*"([^"]*)"', attrs)
    return m.group(1) if m else None


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


# ---- App / Web ---------------------------------------------------------------------------------------------------------
def html_pages() -> list[Path]:
    """Sources of both ends: the five full pages and the component-library parts (templates/<end>/source/pages and source/parts)."""
    return sorted(p for end in ENDS for sub, pat in (("pages", "*.html"), ("parts", "*.part")) for p in (TEMPLATES / end / "source" / sub).glob(pat))


def element_end(text: str, start_match: re.Match) -> int:
    """Index just after the closing tag that matches start_match."""
    name = start_match.group(2).lower()
    depth = 0
    for m in TAG_RE.finditer(text, start_match.start()):
        tag = m.group(2).lower()
        if tag != name:
            continue
        if m.group(1):
            depth -= 1
            if depth == 0:
                return m.end()
        elif not m.group(4) and tag not in VOID:
            depth += 1
    return len(text)


def html_items(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    found = []
    for m in TAG_RE.finditer(text):
        if m.group(1):
            continue
        cid = attr(m.group(3), "data-cid")
        if cid is None:
            continue
        mm = ID_RE.match(cid)
        end = path.parents[2].name
        found.append({
            "kind": end, "id": cid, "name": attr(m.group(3), "data-name") or "",
            "cat": mm.group(2) if mm else "", "page": "components" if path.suffix == ".part" else path.stem, "file": rel(path),
            "start": m.start(), "stop": element_end(text, m),
        })
    return found


# ---- Poster ------------------------------------------------------------------------------------------------------------
def poster_items() -> list[dict]:
    items = []
    for p in sorted((TEMPLATES / "poster" / "source" / "templates").glob("PS-*.html")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"<[^>]*\bdata-cid=\"(PS-\d{3})\"[^>]*>", text)
        attrs = m.group(0) if m else ""
        items.append({
            "kind": "poster", "id": m.group(1) if m else "", "name": attr(attrs, "data-name") or "", "cat": attr(attrs, "data-use") or "",
            "size": attr(attrs, "data-size") or "", "page": p.stem, "file": rel(p), "_stem_id": p.name[:6],
        })
    return items


# ---- Prompts -----------------------------------------------------------------------------------------------------------
def prompt_items() -> list[dict]:
    path = TEMPLATES / "poster" / "source" / "prompts" / "prompts.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["prompts"] if isinstance(data, dict) else data
    return [{
        "kind": "prompt", "id": r.get("id", ""), "name": r.get("name", ""), "cat": r.get("category", ""), "use": r.get("use", ""),
        "role": r.get("role", ""), "ratio": r.get("ratio", ""), "resolution": r.get("resolution", ""),
        "page": "prompts", "file": rel(path), "_row": r,
    } for r in rows]


# ---- Documents ---------------------------------------------------------------------------------------------------------
def document_items() -> list[dict]:
    items = []
    for folder in sorted((TEMPLATES / "documents").glob("*/manifest.json")):
        data = json.loads(folder.read_text(encoding="utf-8"))
        typ = folder.parent.name
        for r in data.get("items", []):
            items.append({"kind": "document", "id": r.get("id", ""), "name": r.get("name", ""), "cat": typ, "use": r.get("use", ""),
                          "page": typ, "file": r.get("file", ""), "spec": r.get("spec", ""), "folder": rel(folder.parent), "_row": r, "part": False})
        for r in data.get("parts", []):
            items.append({"kind": "document", "id": r.get("id", ""), "name": r.get("name", ""), "cat": typ, "use": "",
                          "page": typ, "file": r.get("file", ""), "spec": "", "folder": rel(folder.parent), "_row": r, "part": True})
    manifest = TEMPLATES / "documents" / "slides" / "originals" / "manifest.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for r in data["items"]:
            items.append({"kind": "document", "id": r["id"], "name": r["name"], "cat": "slides", "use": r["use"],
                          "page": "slides", "file": r["file"], "spec": "", "folder": rel(manifest.parents[1]), "_row": r,
                          "part": False, "original": True, "category": r["category"], "source": r["source"],
                          "publisher": data["publishers"][r["provider"]]})
    return items


def collect() -> list[dict]:
    items: list[dict] = []
    for p in html_pages():
        items.extend(html_items(p))
    items.extend(poster_items())
    items.extend(prompt_items())
    items.extend(document_items())
    return items


# ---- Checks ------------------------------------------------------------------------------------------------------------
def problems(items: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    names: dict[str, tuple[str, str]] = {}
    for it in items:
        cid, kind = it["id"], it["kind"]
        where = it["file"] or it["page"]
        if kind in ENDS:
            m = ID_RE.match(cid)
            if not m:
                errors.append(f"{where}: 编号格式不对 {cid}（应为 AP-BTN-001）")
                continue
            end, domain, _ = m.groups()
            if ENDS[kind] != end:
                errors.append(f"{where}: {cid} 的端前缀与目录 {kind} 不一致")
            if domain not in DOMAINS:
                errors.append(f"{where}: {cid} 的域 {domain} 未定义")
            expected = PAGE_OF.get(it["page"])
            if expected and domain not in {expected, "NAV"}:
                errors.append(f"{where}: {cid} 在 {it['page']} 页里只能用域 {expected} 或 NAV")
            if it["page"] == "components" and domain in PAGE_DOMAINS:
                errors.append(f"{where}: {cid} 组件库里只能用组件域，不用页面域 {domain}")
            if cid in seen:
                # 每页都带同一个主导航：NAV 域允许跨页重复，但同一编号的名称必须一致
                if domain == "NAV" and kind == names[cid][1] and it["name"] == names[cid][0]:
                    continue
                errors.append(f"{where}: 编号重复 {cid}（另见 {seen[cid]}）")
            seen[cid], names[cid] = where, (it["name"], kind)
            if not CJK.search(it["name"]):
                errors.append(f"{where}: {cid} 缺少中文 data-name")
        elif kind == "poster":
            if not PS_RE.match(cid):
                errors.append(f"{where}: 海报画布缺少 data-cid=\"PS-001\" 形式的编号")
                continue
            if it["_stem_id"] != cid:
                errors.append(f"{where}: 文件名编号 {it['_stem_id']} 与 data-cid {cid} 不一致")
            if not re.match(r"^\d+[×x]\d+$", it["size"]) and not re.match(r"^\d+(\.\d+)?[×x]\d+(\.\d+)?mm$", it["size"]):
                errors.append(f"{where}: {cid} 缺少 data-size（如 1080×1440 或 210×297mm）")
            if not CJK.search(it["name"]) or not it["cat"]:
                errors.append(f"{where}: {cid} 缺少中文 data-name 或 data-use")
            if cid in seen:
                errors.append(f"{where}: 编号重复 {cid}（另见 {seen[cid]}）")
            seen[cid] = where
        elif kind == "prompt":
            if not PP_RE.match(cid):
                errors.append(f"{where}: 提示词编号格式不对 {cid}（应为 PP-001）")
                continue
            if cid in seen:
                errors.append(f"{where}: 编号重复 {cid}")
            seen[cid] = where
            if not CJK.search(it["name"]):
                errors.append(f"{where}: {cid} 缺少中文名称")
        elif kind == "document":
            m = DC_RE.match(cid)
            if not m:
                errors.append(f"{it['folder']}: 文件编号格式不对 {cid}（应为 DC-WD-001、DC-WD-P01 或 DC-SL-O001）")
                continue
            if DOC_TYPES.get(it["cat"]) != m.group(1):
                errors.append(f"{it['folder']}: {cid} 的类型与目录 {it['cat']} 不一致")
            if it["part"] != m.group(2).startswith("P"):
                errors.append(f"{it['folder']}: {cid} 的模板与可复用块编号用错（块用 P01 形式）")
            if bool(it.get("original")) != m.group(2).startswith("O") or (it.get("original") and m.group(1) != "SL"):
                errors.append(f"{it['folder']}: {cid} 的原版模板编号应为 DC-SL-ONNN")
            if cid in seen:
                errors.append(f"{it['folder']}: 编号重复 {cid}（另见 {seen[cid]}）")
            seen[cid] = it["folder"]
            if not CJK.search(it["name"]):
                errors.append(f"{it['folder']}: {cid} 缺少中文名称")
            for key in ("file", "spec"):
                if it[key] and not it.get("original") and not (ROOT / it["folder"] / it[key]).is_file():
                    errors.append(f"{it['folder']}: {cid} 的 {key} 文件不存在 {it[key]}")
    errors.extend(gaps(items))
    return errors


def gaps(items: list[dict]) -> list[str]:
    """Numbers inside one domain are consecutive from 001: a gap means something was deleted or renumbered."""
    out: list[str] = []
    buckets: dict[str, list[int]] = {}
    for it in items:
        cid, kind = it["id"], it["kind"]
        if kind in ENDS and ID_RE.match(cid) and it["page"] == "components":
            m = ID_RE.match(cid)
            buckets.setdefault(f"{m.group(1)}-{m.group(2)}", []).append(int(m.group(3)))
        elif kind == "poster" and PS_RE.match(cid):
            buckets.setdefault("PS", []).append(int(cid[3:]))
        elif kind == "prompt" and PP_RE.match(cid):
            buckets.setdefault("PP", []).append(int(cid[3:]))
        elif kind == "document" and DC_RE.match(cid) and not it["part"] and cid[6:].isdigit():
            buckets.setdefault(cid[:5], []).append(int(cid[6:]))
    for key, nums in sorted(buckets.items()):
        nums.sort()
        missing = [n for n in range(1, nums[-1] + 1) if n not in set(nums)]
        if missing:
            out.append(f"{key}: 编号不连续，缺 {', '.join(f'{n:03d}' for n in missing[:8])}")
    return out


# ---- Registry ----------------------------------------------------------------------------------------------------------
def public(items: list[dict]) -> dict:
    """Every number once; the navigation repeated on each page keeps the first page that carries it."""
    out: dict[str, list[dict]] = {"components": [], "posters": [], "prompts": [], "documents": []}
    seen: set[str] = set()
    for it in sorted(items, key=lambda x: (x["id"], x["page"])):
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        base = {"id": it["id"], "name": it["name"], "cat": it["cat"], "file": it["file"]}
        if it["kind"] in ENDS:
            out["components"].append({**base, "end": it["kind"], "page": it["page"],
                                      "catName": DOMAINS.get(it["cat"], "")})
        elif it["kind"] == "poster":
            out["posters"].append({**base, "size": it["size"], "use": it["cat"]})
        elif it["kind"] == "prompt":
            out["prompts"].append({**base, "use": it["use"], "role": it["role"], "ratio": it["ratio"], "resolution": it["resolution"]})
        else:
            row = {**base, "type": it["cat"], "use": it["use"], "spec": it["spec"], "part": it["part"], "folder": it["folder"]}
            if it.get("original"):
                row.update(original=True, category=it["category"], source=it["source"], publisher=it["publisher"]["name"])
            out["documents"].append(row)
    return out


def render_registry(items: list[dict]) -> str:
    data = {"note": "由 scripts/template_registry.py write 生成，不手改；编号发出后不改不复用", **public(items)}
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def render_registry_js(items: list[dict]) -> str:
    return "window.LZ_REGISTRY = " + json.dumps(public(items), ensure_ascii=False) + ";" + chr(10)


# ---- Commands ----------------------------------------------------------------------------------------------------------
def local_css(text: str, snippet: str) -> str:
    classes = set(re.findall(r'class="([^"]+)"', snippet))
    names = {c for group in classes for c in group.split()}
    style = "\n".join(re.findall(r"<style>(.*?)</style>", text, re.S))
    style = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
    picked = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", style):
        # 只取选择器里全部类都出现在片段中的规则，避免带进别处组件的样式
        for one in sel.split(","):
            used = re.findall(r"\.([\w-]+)", one)
            if used and all(u in names for u in used):
                picked.append(f"{one.strip()} {{{body.rstrip()} }}")
                break
    return "\n".join(picked)


def stage_of(snippet: str) -> str:
    """A components.html demo is a card with a head and a stage: hand over the stage, which is the component itself."""
    m = re.search(r'<div class="demo__stage[^"]*">', snippet)
    if not m:
        return snippet
    start = m.end()
    depth, pos = 1, start
    for t in TAG_RE.finditer(snippet, start):
        if t.group(2).lower() != "div":
            continue
        depth += -1 if t.group(1) else (0 if t.group(4) else 1)
        if depth == 0:
            return snippet[start:t.start()].strip("\n")
        pos = t.end()
    return snippet[start:pos]


def cmd_list(args) -> int:
    rows = []
    for it in sorted(collect(), key=lambda x: x["id"]):
        if args.kind and it["kind"] != args.kind:
            continue
        if args.cat and it["cat"] != args.cat:
            continue
        if args.page and it["page"] != args.page:
            continue
        terms = " ".join((it["id"], it["name"], it.get("use", ""), it.get("category", ""), it.get("publisher", {}).get("name", "")))
        if args.query and args.query.lower() not in terms.lower():
            continue
        rows.append(it)
    for it in rows:
        extra = f"  {it['size']}" if it["kind"] == "poster" else ""
        print(f"{it['id']}  {it['name']}{extra}  ({it['file']})")
    print(f"共 {len(rows)} 个")
    return 0


def show_html(it: dict) -> None:
    path = ROOT / it["file"]
    text = path.read_text(encoding="utf-8")
    snippet = text[it["start"]:it["stop"]]
    body = stage_of(snippet) if it["page"] == "components" else snippet
    print(f"<!-- {it['id']} {it['name']}  来自 {it['file']} -->")
    if it["page"] == "components" and it["cat"] == "BGND":
        print("<!-- 历史背景样例。前端复用时将表面设为 #FFFFFF，移除彩色背景和渐变。 -->")
    print(body)
    css = local_css(text, body)  # for a component demo the stage, so the catalog card's own rules stay out
    shared = "tokens.css ui.css kit.css " + ("app.css" if it["kind"] == "app" else "web.css") + (" agent.css" if it["cat"] in {"CHAT", "AGNT"} or "agent" in snippet else "") + "，脚本 ui.js"
    print(f"\n<!-- 共用：仓库根 kit/ 下的 {shared}（页面里写成 ../../kit/） -->")
    if css:
        print("<!-- 组件专属样式 -->\n<style>\n" + css + "\n</style>")


def show_other(it: dict) -> None:
    if it["kind"] == "poster":
        print(f"{it['id']}  {it['name']}\n文件  {it['file']}\n尺寸  {it['size']}\n用途  {it['cat']}")
        print("取用  复制该 html 到成品目录，改画布里的文字与素材引用；?theme=rose 换主题色；导出 py -X utf8 scripts/export_poster.py <html> <out.png|pdf>")
    elif it["kind"] == "prompt":
        r = it["_row"]
        print(f"{it['id']}  {it['name']}  [{r.get('category', '')}]  {r.get('role', '')}  {r.get('ratio', '')}  {r.get('resolution', '')}  {r.get('background', '')}")
        print(f"用途  {r.get('use', '')}\n\n{r.get('prompt', '')}\n\n负面约束  {r.get('negative', '')}")
        for c in r.get("checks", []):
            print(f"复核  {c}")
    elif it.get("original"):
        r, publisher = it["_row"], it["publisher"]
        path = ROOT / it["folder"] / it["file"]
        print(f"{it['id']}  {it['name']}  {r['ratio']} · {r['slides']} 页 · {r['layouts']} 个版式")
        print(f"用途  {it['use']}")
        print(f"原件  {path}" if path.is_file() else f"原件  从发布页下载 {r['original_name']}")
        print(f"发布  {publisher['name']}  {it['source']}")
        print(f"授权  {publisher['credits']}  {publisher['license_url']}")
    else:
        r = it["_row"]
        print(f"{it['id']}  {it['name']}  ({it['folder']})")
        for key in ("use", "file", "spec", "generator", "used_in"):
            if r.get(key):
                print(f"{key}  {r[key]}")
        for key in ("fields", "checks"):
            for v in r.get(key, []):
                print(f"{key}  {v}")


def cmd_show(args) -> int:
    for it in collect():
        if it["id"] == args.id:
            (show_html if it["kind"] in ENDS else show_other)(it)
            return 0
    print(f"没有编号 {args.id}；先运行 template_registry.py list")
    return 1


def cmd_check(_args) -> int:
    items = collect()
    errors = problems(items)
    for e in errors:
        print("ERROR", e)
    print(f"{'通过' if not errors else '失败'}：{len(public(items)['components'])} 个界面组件、{len(public(items)['posters'])} 个海报、"
          f"{len(public(items)['prompts'])} 条提示词、{len(public(items)['documents'])} 个文件模板与块")
    return 1 if errors else 0


def cmd_write(args) -> int:
    items = collect()
    errors = problems(items)
    if errors:
        for e in errors:
            print("ERROR", e)
        return 1
    text, js = render_registry(items), render_registry_js(items)
    if args.check:
        stale = [f.name for f, want in ((REGISTRY, text), (REGISTRY_JS, js)) if not f.is_file() or f.read_text(encoding="utf-8") != want]
        if stale:
            print(f"{'、'.join(stale)} 已过期，运行 template_registry.py write")
            return 1
        print("registry.json 与 registry.js 同模板文件一致")
        return 0
    REGISTRY.write_text(text, encoding="utf-8")
    REGISTRY_JS.write_text(js, encoding="utf-8")
    pub = public(items)
    print(f"写入 {rel(REGISTRY)} 与 {rel(REGISTRY_JS)}：" + "、".join(f"{k} {len(v)}" for k, v in pub.items()))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("--kind", choices=["app", "web", "poster", "prompt", "document"])
    p.add_argument("--cat")
    p.add_argument("--page")
    p.add_argument("--query")
    p.set_defaults(fn=cmd_list)
    p = sub.add_parser("show")
    p.add_argument("id")
    p.set_defaults(fn=cmd_show)
    p = sub.add_parser("check")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("write")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_write)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
