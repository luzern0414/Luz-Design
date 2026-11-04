#!/usr/bin/env python3
"""多系统外壳：一份文档里“前端架构”页签加每个系统或设备端一个页签，每个页签只放一个可交互原型。

    py -X utf8 scripts/build_prototype_suite.py <suite.json> --out <文档.html> [--inline] [--number-from N]
    py -X utf8 scripts/build_prototype_suite.py <suite.json> --check                       只校验，不写任何文件
    py -X utf8 scripts/build_prototype_suite.py <suite.json> --out <文档.html> --project-tabs <tabs.json>

suite.json（结构见 references/prototype-templates/shell/README.md）：

    title         文档标题
    overview      结论，一两句话，不超过 150 字
    architecture  “前端架构”页签：{"sections": [{"title", "blocks": [...]}]}，块有 text、list、table（带表题）、layers（分层图）、sub、note、code
    checks        可选：再加一个“检查与差异”页签（同 architecture 的写法），放在最后
    systems[]     每个系统或设备端一个页签：name（页签名）、surface（miniapp/h5/admin/website）、kind（phone/wide，不写则按 surface 定）、
                  spec（原型规格，由本脚本调用 build_prototype.py 构建）或 file（已构建好的 html）二选一、library（默认 luz-kit）、title、height

页签规则同 Luz-Project 的 02-前端界面设计：页签 = 前端架构 + 每个系统/设备端一个（有“检查与差异”时放最后）；系统页签里只有一个原型框
（标题栏有“重新载入”“在新窗口打开”），路径和页面清单只写在“前端架构”里；页签名不能重复，不同页签不能用同一个原型文件，小程序的原型只能是 phone。
默认用 iframe 引用输出目录里的原型文件（切到那个页签才加载）；--inline 把原型以 srcdoc 嵌进文档，得到真正的单文件。键盘左右键切换、
地址 #tab=1 直达、打印时全部展开、深浅外观随系统、手机宽度下页签条可横向滚动。

退出码：0 通过，1 校验或构建未通过，2 读不了 suite.json。
"""
from __future__ import annotations

import argparse
import contextlib
import html
import io
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TEMPLATES = REPO / "references" / "prototype-templates"
sys.path.insert(0, str(HERE))
import build_prototype as bp  # noqa: E402  只读复用：规格 → 单文件 HTML

ARCH_TAB = "前端架构"
CHECK_TAB = "检查与差异"
DEFAULT_LIBRARY = "luz-kit"
SURFACE_LABEL = {"miniapp": "小程序", "h5": "手机网页", "admin": "管理后台", "website": "网站"}
SURFACE_OF_KIND = {"phone": ("miniapp", "h5"), "wide": ("admin", "website")}      # 与 Luz-Project 的 SURFACE_OF_KIND 同口径
DEFAULT_KIND = {"miniapp": "phone", "h5": "phone", "admin": "wide", "website": "wide"}
KIND_LABEL = {"phone": "手机", "wide": "电脑"}
VIEW_OF_SPEC_KIND = {"mini": "phone", "admin": "wide"}                           # 规格用哪个模板，决定原型是手机还是电脑
PROJECT_SURFACE = {"miniapp": "miniprogram", "h5": "web-admin", "admin": "web-admin", "website": "website"}   # Luz-Project 02 文档里页签的 surface
PROJECT_DOCS_DIR = "docs/02-产品开发"
DEFAULT_HEIGHT = {"phone": 900, "wide": 860}
PROTO_MIN_BYTES = 120_000                                                         # Luz-Project 的“只有框架没有内容”下限
PROTO_MARKERS = {"没有“减少动态效果”分支": ("prefers-reduced-motion",), "没有对话框（原生 dialog 或带 role=dialog 的容器）": ("showModal", "role: 'dialog'"),
                 "没有场景配置面板": ("UI.demo(", "K.panel(")}
PLACEHOLDER = re.compile(r"待补充|待完善|待填写|示例文字|（略）|\(略\)|\bTODO\b|\bTBD\b|\bXXX\b", re.I)
TOP_KEYS = {"title", "overview", "architecture", "checks", "systems"}
SYSTEM_KEYS = {"name", "surface", "kind", "spec", "file", "library", "title", "height"}
BLOCK_TYPES = {"text", "list", "bullets", "table", "layers", "figure", "sub", "note", "code"}
E = html.escape


# ------------------------------------------------------------------ 读与校验

def component_libraries() -> dict[str, Any]:
    return json.loads((REPO / "references" / "component-libraries.json").read_text(encoding="utf-8"))["libraries"]


def _texts(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [t for v in value.values() for t in _texts(v)]
    if isinstance(value, list):
        return [t for v in value for t in _texts(v)]
    return []


def _norm_block(b: dict[str, Any]) -> dict[str, Any]:
    """别名：bullets 即 list，figure + kind=layers 即 layers（与 Luz-Project 的块写法互通）。"""
    if b.get("type") == "bullets":
        return {**b, "type": "list"}
    if b.get("type") == "figure" and b.get("kind") == "layers":
        return {**b, "type": "layers"}
    return b


def block_errors(where: str, b: Any) -> list[str]:
    if not isinstance(b, dict):
        return [f"{where}有不是对象的块"]
    kind = b.get("type")
    if kind not in BLOCK_TYPES:
        return [f"{where}的块类型无效：{kind!r}（可用 text、list、table、layers、sub、note、code）"]
    if kind == "figure" and b.get("kind") != "layers":
        return [f"{where}的图只支持分层图（layers）；步骤图、时序图、关系图请用表格说明，或写进 Luz-Project 的文档"]
    b = _norm_block(b)
    kind = b["type"]
    out: list[str] = []
    if kind in {"text", "sub", "note", "code"}:
        if not str(b.get("text", "")).strip():
            out.append(f"{where}有空的 {kind} 块")
    elif kind == "list":
        items = b.get("items")
        if not isinstance(items, list) or not items or any(not str(i).strip() for i in items):
            out.append(f"{where}的列表为空或有空项")
    elif kind == "table":
        cols, rows = b.get("columns"), b.get("rows")
        if not str(b.get("caption", "")).strip():
            out.append(f"{where}有没有表题的表（表题写在 caption 里，显示为“表 N　名称”）")
        if not isinstance(cols, list) or not cols or not isinstance(rows, list) or not rows:
            out.append(f"{where}的表「{b.get('caption', '')}」缺表头或没有行")
        else:
            for r in rows:
                if not isinstance(r, list) or len(r) != len(cols):
                    out.append(f"{where}的表「{b.get('caption', '')}」有列数与表头不符的行")
                    break
                if any(str(c).strip() == "" for c in r):
                    out.append(f"{where}的表「{b.get('caption', '')}」有空单元格（没有内容写“—”）")
                    break
    elif kind == "layers":
        rows = b.get("rows")
        if not str(b.get("caption", "")).strip():
            out.append(f"{where}有没有图题的分层图")
        if not isinstance(rows, list) or len(rows) < 2:
            out.append(f"{where}的分层图至少两层")
        else:
            for r in rows:
                nodes = r.get("nodes") if isinstance(r, dict) else None
                if not isinstance(r, dict) or not str(r.get("label", "")).strip() or not isinstance(nodes, list) or not nodes \
                        or any(not isinstance(n, dict) or not str(n.get("name", "")).strip() for n in nodes):
                    out.append(f"{where}的分层图每层要有 label 和至少一个带 name 的节点")
                    break
            for link in b.get("links", []):
                if not isinstance(link, dict) or not isinstance(link.get("after"), int) or not 0 <= link["after"] < len(rows) - 1:
                    out.append(f"{where}的分层图的 links 要写 after（层序号，从 0 起，不含最后一层）")
                    break
    return out


def section_errors(where: str, group: Any) -> list[str]:
    if not isinstance(group, dict) or not isinstance(group.get("sections"), list) or not group["sections"]:
        return [f"{where}要写成 {{\"sections\": [{{\"title\", \"blocks\"}}]}}，至少一节"]
    out: list[str] = []
    for key in set(group) - {"sections"}:
        out.append(f"{where}多余的字段「{key}」（拼写对吗？）")
    for s in group["sections"]:
        if not isinstance(s, dict) or not str(s.get("title", "")).strip():
            out.append(f"{where}有没有标题的章节")
            continue
        if not isinstance(s.get("blocks"), list) or not s["blocks"]:
            out.append(f"{where}的章节「{s['title']}」没有内容块")
            continue
        for b in s["blocks"]:
            out += block_errors(f"{where}的章节「{s['title']}」", b)
    return out


def _real(path: Path) -> str:
    return os.path.normcase(os.path.realpath(path))


def validate(suite: Any, base: Path) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    """返回（错误，警告，解析后的系统清单）。只查结构与引用关系，不构建原型。"""
    errors: list[str] = []
    warnings: list[str] = []
    systems: list[dict[str, Any]] = []
    if not isinstance(suite, dict):
        return ["suite.json 的最外层要是一个对象"], warnings, systems
    for key in sorted(set(suite) - TOP_KEYS):
        errors.append(f"suite.json 多余的字段「{key}」（拼写对吗？可用 {'、'.join(sorted(TOP_KEYS))}）")
    if not str(suite.get("title", "")).strip():
        errors.append("suite.json 要写 title（文档标题）")
    overview = str(suite.get("overview", "")).strip()
    if not overview:
        errors.append("suite.json 要写 overview（结论，一两句话）")
    elif len(overview) > 150:
        errors.append(f"overview 要在 150 字以内（现在 {len(overview)} 字）：结论只说这份文档的结论和适用范围")
    errors += section_errors("architecture（前端架构页签）", suite.get("architecture"))
    if "checks" in suite:
        errors += section_errors(f"checks（{CHECK_TAB}页签）", suite["checks"])
    if PLACEHOLDER.search("\n".join(_texts({k: suite.get(k) for k in ("title", "overview", "architecture", "checks")}))):
        errors.append("文档里含占位或待办字样（待补充、TODO、示例文字等）：确实没做的事写成现状和影响，不留占位")

    raw = suite.get("systems")
    if not isinstance(raw, list) or not raw:
        errors.append("systems 要是一个列表，至少一个系统或设备端（每个一个页签）")
        return errors, warnings, systems
    libs = component_libraries()
    names: dict[str, int] = {}
    files: dict[str, str] = {}
    for i, s in enumerate(raw):
        if not isinstance(s, dict):
            errors.append(f"systems[{i}] 要是一个对象")
            continue
        name = str(s.get("name", "")).strip()
        label = f"系统「{name}」" if name else f"systems[{i}]"
        for key in sorted(set(s) - SYSTEM_KEYS):
            errors.append(f"{label}多余的字段「{key}」（拼写对吗？可用 {'、'.join(sorted(SYSTEM_KEYS))}）")
        if not name:
            errors.append(f"{label}要写 name（页签名，也是前端的名字）")
        elif name in (ARCH_TAB, CHECK_TAB):
            errors.append(f"页签名「{name}」被前端架构页签占用，换一个系统自己的名字")
        elif name in names:
            errors.append(f"页签重名：「{name}」在 systems[{names[name]}] 和 systems[{i}] 各出现一次，每个系统或设备端一个页签、名字不能重复")
        names.setdefault(name, i)
        surface = s.get("surface")
        if surface not in SURFACE_LABEL:
            errors.append(f"{label}的 surface 要写 {'、'.join(SURFACE_LABEL)} 之一（现在是 {surface!r}）")
        kind = s.get("kind", DEFAULT_KIND.get(surface))
        if kind not in SURFACE_OF_KIND:
            errors.append(f"{label}的 kind 只能是 phone 或 wide（现在是 {kind!r}）")
        elif surface in SURFACE_LABEL and surface not in SURFACE_OF_KIND[kind]:
            hint = "小程序的原型只能是 phone" if surface == "miniapp" else f"{SURFACE_LABEL[surface]}对应的是 {DEFAULT_KIND[surface]}"
            errors.append(f"{label}的 kind（{kind}）与 surface（{surface}）不匹配：{hint}；phone 对应 {'、'.join(SURFACE_OF_KIND['phone'])}，wide 对应 {'、'.join(SURFACE_OF_KIND['wide'])}")
        library = str(s.get("library", DEFAULT_LIBRARY))
        lib = libs.get(library)
        if lib is None:
            errors.append(f"{label}的 library「{library}」不在组件库注册表（references/component-libraries.json）里：{'、'.join(libs)}")
        elif kind in SURFACE_OF_KIND and not set(lib["surfaces"]) & set(SURFACE_OF_KIND[kind]):
            errors.append(f"{label}是 {kind} 端，组件库 {library} 适用于 {'、'.join(lib['surfaces'])}，换一个适合这一端的库")
        height = s.get("height")
        if height is not None and (not isinstance(height, int) or isinstance(height, bool) or not 400 <= height <= 2400):
            errors.append(f"{label}的 height 要是 400 到 2400 之间的整数（像素）")
        has_spec, has_file = bool(str(s.get("spec", "")).strip()), bool(str(s.get("file", "")).strip())
        info: dict[str, Any] = {"index": len(systems), "name": name, "surface": surface, "kind": kind if kind in SURFACE_OF_KIND else None, "library": library,
                                "title": str(s.get("title", "")).strip() or f"{name}原型", "height": height, "source": None, "path": None}
        if not has_spec and not has_file:
            errors.append(f"{label}没有原型：写 spec（原型规格 json，由本脚本构建）或 file（已构建好的 html）")
        elif has_spec and has_file:
            errors.append(f"{label}同时写了 spec 和 file：一个页签只有一个原型，二选一")
        else:
            info["source"] = "spec" if has_spec else "file"
            path = (base / str(s["spec" if has_spec else "file"])).resolve()
            info["path"] = path
            if not path.is_file():
                errors.append(f"{label}的{'原型规格' if has_spec else '原型文件'}不存在：{s['spec' if has_spec else 'file']}")
            else:
                if has_file and path.suffix.lower() != ".html":
                    errors.append(f"{label}的 file 要是 .html 文件：{s['file']}")
                key = _real(path)
                if key in files:
                    errors.append(f"页签「{files[key]}」与「{name}」用了同一个原型{'文件' if has_file else '规格'}（{path.name}）：每个页签各有自己的原型，不同设备端也各开一个页签")
                else:
                    files[key] = name
                if has_spec:
                    try:
                        spec_kind = json.loads(path.read_text(encoding="utf-8")).get("kind")
                    except (OSError, ValueError, AttributeError) as exc:
                        errors.append(f"{label}的原型规格读不了：{exc}")
                        spec_kind = None
                    view = VIEW_OF_SPEC_KIND.get(spec_kind)
                    if view and info["kind"] and view != info["kind"]:
                        errors.append(f"{label}的规格用 {spec_kind} 模板，原型是 {view} 端，kind 不能写 {info['kind']}（页签的 kind 要和规格的模板一致）")
        systems.append(info)
    arch_text = "\n".join(_texts(suite.get("architecture")))
    for info in systems:
        if info["name"] and info["name"] not in arch_text:
            warnings.append(f"前端架构里没有提到「{info['name']}」：页面地图和路由与权限要覆盖每个系统，路径和页面清单只写在前端架构页签")
    return errors, warnings, systems


# ------------------------------------------------------------------ 构建原型（调用 build_prototype.py，报错原样带出）

def run_build(spec_path: Path, out: Path, check_only: bool) -> tuple[int, str]:
    buf = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code = bp.build(spec_path, out, None, check_only)
    except SystemExit as exc:
        code = 1
        if exc.code not in (None, 0):
            buf.write(str(exc.code))
    except Exception as exc:  # noqa: BLE001  生成器自己的异常也要带出来，不吞
        code = 1
        buf.write(f"{type(exc).__name__}：{exc}")
    return code, buf.getvalue().strip()


def proto_warnings(text: str) -> list[str]:
    out = []
    if len(text.encode("utf-8")) < PROTO_MIN_BYTES:
        out.append(f"文件小于 {PROTO_MIN_BYTES // 1000} KB，Luz-Project 会判为只有框架没有内容")
    out += [why for why, options in PROTO_MARKERS.items() if not any(o in text for o in options)]
    return out


def proto_filename(info: dict[str, Any], number_from: int) -> str:
    safe = re.sub(r'[\\/:*?"<>|\s]+', "-", info["name"]).strip("-.") or f"系统{info['index'] + 1}"
    return f"{number_from + info['index']:02d}-{safe}{'' if safe.endswith('原型') else '原型'}.html"


# ------------------------------------------------------------------ 渲染

LIGHT = {"bg": "#fbfbfa", "card": "#ffffff", "tint": "#f1f3f1", "line": "#d9ddd9", "ink": "#1b2420", "ink2": "#505b56", "brand": "#2d6a5a"}
DARK = {"bg": "#111413", "card": "#181c1a", "tint": "#202523", "line": "#323a36", "ink": "#e7ebe9", "ink2": "#a6b1ad", "brand": "#79bda9"}


def _tokens(values: dict[str, str]) -> str:
    return "".join(f"--{k}:{v};" for k, v in values.items())


SHELL_CSS = """
:root{color-scheme:light;{{LIGHT}}--muted:var(--ink2);--surface:var(--tint);--surface-soft:var(--tint);--line:var(--line)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;{{DARK}}}}
:root[data-theme="dark"]{color-scheme:dark;{{DARK}}}
*,*::before,*::after{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif}
main.doc{max-width:1280px;margin:0 auto;padding:32px 24px 72px}
main.doc>h1{margin-top:0}
a{color:var(--ink)}
.notice{margin:0 0 16px;padding:12px 16px;border-radius:8px;background:var(--tint);color:var(--ink)}
.tabs{position:sticky;top:0;z-index:5;display:flex;flex-wrap:nowrap;gap:4px;margin:32px 0 0;overflow-x:auto;overflow-y:hidden;background:var(--bg);border-bottom:1px solid var(--line);scrollbar-width:thin}
.tabs button{flex:none;min-height:44px;padding:0 18px;border:0;border-bottom:3px solid transparent;background:none;color:var(--ink);font:inherit;font-size:var(--md-body);line-height:1.4;white-space:nowrap;cursor:pointer}
.tabs button[aria-selected=true]{border-bottom-color:var(--brand);font-weight:600}
.tabs button:hover{background:var(--tint)}
.tabs button:focus-visible{outline:2px solid var(--ink);outline-offset:-2px}
.tabpanel{padding-top:8px;min-width:0}
.tabpanel[hidden]{display:none}
.tabpanel>:first-child{margin-top:24px}
.print-title{display:none}
.tcap{margin:24px 0 8px;font-size:var(--md-aux);line-height:1.6}
.twrap{max-width:100%;margin:0 0 20px;overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
.twrap:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.tbl{width:100%;border-collapse:collapse}
.tbl th,.tbl td{padding:10px 16px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;overflow-wrap:anywhere}
.tbl thead th{background:var(--tint);white-space:nowrap}
.tbl tbody tr:last-child td{border-bottom:0}
figure.fig{margin:20px 0}
figure.fig figcaption{margin-top:8px;text-align:left}
.layers{list-style:none;margin:0;padding:0;max-width:none}
.layers>li{margin:0}
.layer{display:grid;grid-template-columns:7em minmax(0,1fr);gap:12px;align-items:center;padding:12px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.layer-label{font-weight:600}
.nodes{list-style:none;margin:0;padding:0;max-width:none;display:flex;flex-wrap:wrap;gap:10px}
.nodes>li{flex:1 1 12em;min-width:0;margin:0;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--tint)}
.nodes strong{display:block;font-weight:600}
.nodes span{display:block;font-size:var(--md-aux);line-height:1.6;color:var(--ink2)}
.layer-link{display:flex;align-items:center;justify-content:center;gap:12px;min-height:48px;color:var(--ink2)}
.layer-link .ar{position:relative;width:0;height:30px;border-left:2px solid var(--ink2)}
.layer-link .ar::after{content:"";position:absolute;left:50%;bottom:-1px;transform:translateX(-50%);border:6px solid transparent;border-top:8px solid var(--ink2);border-bottom:0}
.layer-link span.lbl{font-size:var(--md-aux);line-height:1.6}
.proto{margin:16px 0 18px;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--card)}
.proto-bar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 12px;padding:10px 16px;border-bottom:1px solid var(--line);background:var(--tint)}
.proto-bar strong{font-weight:600;min-width:0;overflow-wrap:anywhere}
.proto-act{display:flex;flex-wrap:wrap;gap:8px}
.proto-act a,.proto-act button{display:inline-flex;align-items:center;min-height:40px;padding:0 14px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font:inherit;font-size:var(--md-table);text-decoration:none;cursor:pointer}
.proto-act a:hover,.proto-act button:hover{background:var(--tint)}
.proto-act a:focus-visible,.proto-act button:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.proto iframe{display:block;width:100%;max-width:100%;height:min(var(--proto-h,860px),max(560px,calc(100vh - 150px)));border:0;background:var(--tint)}
@media (max-width:767px){main.doc{padding:24px 16px 56px}.layer{grid-template-columns:minmax(0,1fr)}.tabs button{padding:0 14px}.tbl th,.tbl td{min-width:6em;overflow-wrap:normal}}
@media print{.tabs{display:none}.tabpanel[hidden]{display:block!important}.print-title{display:block}.proto-act{display:none}.proto,.layer,.twrap{break-inside:avoid}.proto iframe{height:var(--proto-h,860px)}}
""".replace("{{LIGHT}}", _tokens(LIGHT)).replace("{{DARK}}", _tokens(DARK))

SHELL_JS = """(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tabs [role=tab]'));
  function fill(f){
    if(f.getAttribute('src')||f.hasAttribute('srcdoc'))return;
    if(f.dataset.srcdoc!==undefined)f.srcdoc=f.dataset.srcdoc;
    else if(f.dataset.src)f.src=f.dataset.src;
  }
  function activate(i,focus){
    tabs.forEach(function(t,k){
      var on=k===i;
      t.setAttribute('aria-selected',on?'true':'false');
      t.tabIndex=on?0:-1;
      var p=document.getElementById(t.getAttribute('aria-controls'));
      if(p){p.hidden=!on;if(on)p.querySelectorAll('iframe').forEach(fill);}
    });
    if(focus)tabs[i].focus();
    tabs[i].scrollIntoView({block:'nearest',inline:'nearest'});
  }
  function fromHash(){var m=/#tab=(\\d+)/.exec(location.hash);return m&&tabs[+m[1]]?+m[1]:null;}
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(){activate(i);try{history.replaceState(null,'','#tab='+i);}catch(_){}});
    t.addEventListener('keydown',function(e){
      var n=null;
      if(e.key==='ArrowRight')n=(i+1)%tabs.length;else if(e.key==='ArrowLeft')n=(i-1+tabs.length)%tabs.length;
      else if(e.key==='Home')n=0;else if(e.key==='End')n=tabs.length-1;
      if(n!==null){e.preventDefault();activate(n,true);try{history.replaceState(null,'','#tab='+n);}catch(_){}}
    });
  });
  document.addEventListener('click',function(e){
    var r=e.target.closest('[data-reload]');
    if(r){
      var f=document.getElementById(r.getAttribute('data-reload'));
      if(f){var n=f.cloneNode(false);n.removeAttribute('src');n.removeAttribute('srcdoc');f.replaceWith(n);fill(n);}
      return;
    }
    var o=e.target.closest('[data-open]');
    if(o){
      var g=document.getElementById(o.getAttribute('data-open'));
      if(g&&g.dataset.srcdoc!==undefined){window.open(URL.createObjectURL(new Blob([g.dataset.srcdoc],{type:'text/html'})),'_blank');}
    }
  });
  window.addEventListener('hashchange',function(){var i=fromHash();if(i!==null)activate(i);});
  window.addEventListener('beforeprint',function(){document.querySelectorAll('.tabpanel iframe').forEach(fill);});
  var first=fromHash();
  activate(first===null?0:first);
})();"""


def _inline(text: Any) -> str:
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", E(str(text)))


def _attr(text: str) -> str:
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


class Renderer:
    def __init__(self) -> None:
        self.tables = 0
        self.figures = 0

    def table(self, b: dict[str, Any]) -> str:
        self.tables += 1
        head = "".join(f'<th scope="col">{_inline(c)}</th>' for c in b["columns"])
        body = "".join("<tr>" + "".join(f"<td>{_inline(c).replace(chr(10), '<br>')}</td>" for c in row) + "</tr>" for row in b["rows"])
        cap = f"表 {self.tables}　{b['caption']}"
        width = max(24, 8 * len(b["columns"]))
        return (f'<div class="tcap">{E(cap)}</div><div class="twrap" role="region" aria-label="{_attr(cap)}" tabindex="0">'
                f'<table class="tbl" data-pagination="none" style="min-width:{width}em"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')

    def layers(self, b: dict[str, Any]) -> str:
        self.figures += 1
        links = {int(l["after"]): str(l.get("label", "")) for l in b.get("links", [])}
        parts: list[str] = []
        for i, row in enumerate(b["rows"]):
            nodes = "".join(f"<li><strong>{_inline(n['name'])}</strong>" + (f"<span>{_inline(n['note'])}</span>" if n.get("note") else "") + "</li>" for n in row["nodes"])
            parts.append(f'<li><div class="layer"><div class="layer-label">{_inline(row["label"])}</div><ul class="nodes">{nodes}</ul></div></li>')
            if i < len(b["rows"]) - 1:
                label = f'<span class="lbl">{_inline(links[i])}</span>' if links.get(i) else ""
                parts.append(f'<li class="layer-link" aria-hidden="true"><span class="ar"></span>{label}</li>')
        return f'<figure class="fig"><ol class="layers">{"".join(parts)}</ol><figcaption>图 {self.figures}　{E(b["caption"])}</figcaption></figure>'

    def block(self, b: dict[str, Any]) -> str:
        b = _norm_block(b)
        kind = b["type"]
        if kind == "text":
            return f"<p>{_inline(b['text'])}</p>"
        if kind == "note":
            return f'<p class="notice">{_inline(b["text"])}</p>'
        if kind == "sub":
            return f"<h3>{_inline(b['text'])}</h3>"
        if kind == "code":
            return f'<pre class="code">{E(b["text"])}</pre>'
        if kind == "list":
            return "<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in b["items"]) + "</ul>"
        if kind == "table":
            return self.table(b)
        return self.layers(b)

    def sections(self, group: dict[str, Any], extra: str = "") -> str:
        return "".join(f"<h2>{_inline(s['title'])}</h2>" + "".join(self.block(b) for b in s["blocks"]) for s in group["sections"]) + extra


def md_type_css() -> str:
    path = REPO / "references" / "md-type.css"
    if not path.is_file():
        raise SystemExit(f"找不到阅读页字阶 {path.relative_to(REPO)}（桌面正文 18、手机 16，母本在 Luz-Design）")
    return path.read_text(encoding="utf-8")


def favicon() -> str:
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='#f1f3f1'/>"
           "<g fill='none' stroke='#2d6a5a' stroke-width='2.5' stroke-linecap='round'><path d='M8 11h16M8 16h10M8 21h13'/></g></svg>")
    return "data:image/svg+xml," + quote(svg, safe="/:=,;'()- ")


def render(suite: dict[str, Any], systems: list[dict[str, Any]], docs: dict[int, dict[str, str]], inline: bool) -> str:
    """docs[i] 是第 i 个系统的 {"src": 相对地址} 或 {"srcdoc": 原型全文}。"""
    r = Renderer()
    labels = [ARCH_TAB] + [s["name"] for s in systems] + ([CHECK_TAB] if suite.get("checks") else [])
    rows = [[s["name"], SURFACE_LABEL[s["surface"]], KIND_LABEL[s["kind"]], s["library"], "内嵌（单文件）" if inline else docs[s["index"]]["name"]] for s in systems]
    table = {"type": "table", "caption": "各页签对应的使用端、设备端、组件库和原型文件", "columns": ["页签", "使用端", "设备端", "组件库", "原型文件"], "rows": rows}
    panels = [r.sections(suite["architecture"], "<h2>页签与原型</h2>" + r.table(table))]
    for s in systems:
        fid = f"proto-{s['index'] + 1}"
        height = s["height"] or DEFAULT_HEIGHT[s["kind"]]
        doc = docs[s["index"]]
        if inline:
            data = f'data-srcdoc="{_attr(doc["srcdoc"])}"'
            opener = f'<button type="button" data-open="{fid}">在新窗口打开</button>'
        else:
            data = f'data-src="{_attr(doc["src"])}"'
            opener = f'<a href="{_attr(doc["src"])}" target="_blank" rel="noopener">在新窗口打开</a>'
        panels.append(f'<h2 class="print-title">{E(s["name"])}</h2><div class="proto {s["kind"]}" role="group" aria-label="{_attr(s["title"])}" style="--proto-h:{height}px">'
                      f'<div class="proto-bar"><strong>{E(s["title"])}</strong><span class="proto-act"><button type="button" data-reload="{fid}">重新载入</button>{opener}</span></div>'
                      f'<iframe id="{fid}" {data} title="{_attr(s["title"])}" height="{height}">当前浏览器不能内嵌页面，请用“在新窗口打开”。</iframe></div>')
    if suite.get("checks"):
        panels.append(r.sections(suite["checks"]))
    tabs = "".join(f'<button type="button" role="tab" id="st-t{i}" aria-controls="st-p{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{E(l)}</button>'
                   for i, l in enumerate(labels))
    body = "".join(f'<div role="tabpanel" id="st-p{i}" aria-labelledby="st-t{i}" class="tabpanel"{"" if i == 0 else " hidden"}>{p}</div>' for i, p in enumerate(panels))
    title = str(suite["title"])
    return (f'<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="color-scheme" content="light dark"><title>{E(title)}</title><link rel="icon" href="{favicon()}">'
            f'<style>{md_type_css()}{SHELL_CSS}</style></head><body><main class="doc"><h1>{E(title)}</h1><h2>结论</h2><p>{_inline(suite["overview"])}</p>'
            f'<div class="tabs" role="tablist" aria-label="系统页签">{tabs}</div>{body}</main><script>{SHELL_JS}</script></body></html>\n')


def project_tabs(systems: list[dict[str, Any]], number_from: int) -> list[dict[str, Any]]:
    """Luz-Project 02-前端界面设计 的 tabs 里前端页签那几项（prototype 块的 file、title、kind、library，不带 caption、try、source）。"""
    tabs = []
    for s in systems:
        block: dict[str, Any] = {"type": "prototype", "file": f"{PROJECT_DOCS_DIR}/{proto_filename(s, number_from)}", "title": s["title"], "kind": s["kind"], "library": s["library"]}
        if s["height"]:
            block["height"] = s["height"]
        tabs.append({"title": s["name"], "layout": "frontend", "surface": PROJECT_SURFACE[s["surface"]], "sections": [{"title": s["name"], "blocks": [block]}]})
    return tabs


# ------------------------------------------------------------------ 主流程

def build_suite(suite_path: Path, out: Path | None, inline: bool, check_only: bool, number_from: int, tabs_out: Path | None) -> int:
    try:
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"读不了 {suite_path}：{exc}", file=sys.stderr)
        return 2
    base = suite_path.parent
    errors, warnings, systems = validate(suite, base)
    # 规格先逐个校验（不写文件），报错原样带出 build_prototype.py 的输出
    for s in systems:
        if s["source"] == "spec" and s["path"] and s["path"].is_file():
            code, text = run_build(s["path"], Path(os.devnull), True)
            warnings += [f"系统「{s['name']}」：{line.removeprefix('警告：')}" for line in text.splitlines() if line.startswith("警告：")]
            if code:
                errors.append(f"系统「{s['name']}」的原型规格构建失败（{s['path'].name}），build_prototype.py 报：\n{text}")
    for w in warnings:
        print("警告：" + w)
    if errors:
        for e in errors:
            print("错误：" + e)
        print(f"校验未通过：{len(errors)} 处错误")
        return 1
    labels = len(systems) + 1 + (1 if suite.get("checks") else 0)
    if check_only:
        print(f"外壳校验通过：{labels} 个页签（{ARCH_TAB} + {len(systems)} 个系统{'，' + CHECK_TAB if suite.get('checks') else ''}），{len(warnings)} 条警告")
        return 0

    assert out is not None
    out = out.resolve()
    out_dir = out.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    docs: dict[int, dict[str, str]] = {}
    taken: set[str] = set()
    with tempfile.TemporaryDirectory() as tmp:
        for s in systems:
            name = proto_filename(s, number_from)
            if s["source"] == "spec":
                target = (Path(tmp) / name) if inline else (out_dir / name)
                code, text = run_build(s["path"], target, False)
                if code:
                    print(f"错误：系统「{s['name']}」的原型构建失败：\n{text}")
                    return 1
                built = target
            else:
                built = s["path"]
                if not inline and not built.is_relative_to(out_dir):
                    name = built.name
                    if name in taken or (name in {proto_filename(x, number_from) for x in systems} and name != proto_filename(s, number_from)):
                        print(f"错误：系统「{s['name']}」的原型文件名 {name} 与别的页签的原型重名，会互相覆盖：改一下文件名")
                        return 1
                    if _real(out_dir / name) != _real(built):
                        shutil.copyfile(built, out_dir / name)
                        print(f"复制 {built} → {out_dir / name}（iframe 引用的原型文件要和文档放在一起）")
                    built = out_dir / name
            taken.add(name)
            text = built.read_text(encoding="utf-8")
            warnings_p = proto_warnings(text)
            for w in warnings_p:
                print(f"警告：系统「{s['name']}」的原型{w}")
            if inline:
                docs[s["index"]] = {"srcdoc": text, "name": name}
            else:
                rel = os.path.relpath(built, out_dir).replace(os.sep, "/")
                docs[s["index"]] = {"src": quote(rel, safe="/"), "name": rel}
        page = render(suite, systems, docs, inline)
    out.write_text(page, encoding="utf-8")
    print(f"{out}  {round(out.stat().st_size / 1024)} KB  {labels} 个页签（{ARCH_TAB} + {len(systems)} 个系统），"
          f"{'内嵌 srcdoc，单文件' if inline else 'iframe 引用同目录的原型文件'}")
    if tabs_out:
        tabs_out.parent.mkdir(parents=True, exist_ok=True)
        tabs_out.write_text(json.dumps(project_tabs(systems, number_from), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{tabs_out}  Luz-Project 02 文档的前端页签（prototype 块的 file 指向 {PROJECT_DOCS_DIR}/，把原型文件放到那里）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("suite", help="suite.json")
    ap.add_argument("--out", help="输出 HTML（默认 references/prototype-templates/dist/<suite 所在目录名>/<目录名>.html）")
    ap.add_argument("--inline", action="store_true", help="把原型以 srcdoc 嵌进文档，得到真正的单文件")
    ap.add_argument("--check", action="store_true", help="只校验，不写任何文件")
    ap.add_argument("--number-from", type=int, default=1, help="原型文件名的起始序号（NN-系统名原型.html），默认 1；放进 Luz-Project 的 docs/02-产品开发/ 时用 3")
    ap.add_argument("--project-tabs", help="另存一份 Luz-Project 02 文档里前端页签的 JSON（prototype 块的 file、title、kind、library）")
    a = ap.parse_args(argv)
    suite_path = Path(a.suite).resolve()
    out = Path(a.out) if a.out else TEMPLATES / "dist" / suite_path.parent.name / f"{suite_path.parent.name}.html"
    return build_suite(suite_path, None if a.check else out, a.inline, a.check, a.number_from, Path(a.project_tabs) if a.project_tabs else None)


if __name__ == "__main__":
    raise SystemExit(main())
