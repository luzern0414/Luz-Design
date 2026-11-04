#!/usr/bin/env python3
"""界面细节规范（图标、背景、卡片家族）的命令行：查规则与家族、算分层与列数、生成偏离说明、渲染规则页。

    py -X utf8 scripts/ui_details.py list
    py -X utf8 scripts/ui_details.py show <规则 id | 卡片家族 id | 图标类别 id | 背景用法 id | thresholds | palette | basis | method>
    py -X utf8 scripts/ui_details.py layers [--theme <主题 id> | --all]        页面底与卡面的明度差，三层分层检查
    py -X utf8 scripts/ui_details.py grid --min 160 --gap 12 (--width 375 [--margin 12] | --content 1152)    卡片网格的列数
    py -X utf8 scripts/ui_details.py deviation <规则 id> --why … --risk … --verify … [--json]
    py -X utf8 scripts/ui_details.py render [--write | --check]                由数据文件生成规则页 references/ui-details.html

数据源是 references/ui-details.json（规则页由它渲染，渲染与否由测试核对）。规则强度三档与偏离说明字段沿用页面范式库
（references/page-patterns.json 的 method）。生成图标的颜色检查在 scripts/check_icon_image.py。
退出码：layers 有主题不达标、render --check 与数据不一致为 1；deviation 遇到 must 规则、输入有误为 2。
"""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design_path as dp  # noqa: E402  复用规则页的外壳、行内转换与表格写法

ROOT = HERE.parent
DATA_PATH = ROOT / "references" / "ui-details.json"
PAGE_PATH = ROOT / "references" / "ui-details.html"
PATTERNS_PATH = ROOT / "references" / "page-patterns.json"
THEMES_PATH = ROOT / "references" / "themes.json"
PREFIX = "details"
STRENGTH = {"must": "硬规则", "default": "默认", "hint": "建议"}
CHECK_LABEL = {"script": "脚本", "rendered": "渲染", "manual": "人工"}
BASIS_KIND = {"rule": "规则证据", "example": "实例证据", "skill": "本技能取值或内部规则", "convention": "通行做法", "uncovered": "资料未覆盖"}

_CACHE: dict[str, Any] = {}


def load(path: Path | None = None) -> dict:
    path = path or DATA_PATH
    key = str(path)
    if key not in _CACHE:
        _CACHE[key] = json.loads(path.read_text(encoding="utf-8"))
    return _CACHE[key]


def inline(text: str) -> str:
    return dp.inline(text)


def code(text: str) -> str:
    return dp.code(text)


# ---------------------------------------------------------------- 分层与列数

def srgb_to_lstar(hex_value: str) -> float:
    """CIE L*（D65，白为 100）。"""
    def lin(c: int) -> float:
        x = c / 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_value[i:i + 2], 16) for i in (1, 3, 5))
    y = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    f = y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116
    return 116 * f - 16


def layer_report(theme_id: str, data: dict | None = None) -> dict:
    """一个主题的分层核对：浅色与深色的页面底、卡面、ΔL*、是否需要发丝线、深色浮起面是否逐级变亮。"""
    data = data or load()
    lim = data["backgrounds"]["layer_check"]["thresholds"]
    themes = json.loads(THEMES_PATH.read_text(encoding="utf-8"))
    t, shared = themes["themes"][theme_id], themes["shared"]
    out: dict[str, Any] = {"theme": theme_id, "problems": []}
    for mode, canvas, surface, floor in (("light", t["canvas"], shared["surface"], lim["light_min"]),
                                          ("dark", t["dark"]["canvas"], t["dark"]["surface"], lim["dark_min"])):
        delta = srgb_to_lstar(surface) - srgb_to_lstar(canvas)
        elev = shared["elevation"] if mode == "light" else shared["dark"]["elevation"]
        needs_line = delta < lim["hairline_below"]
        out[mode] = {"canvas": canvas, "surface": surface, "delta": round(delta, 2), "needs_hairline": needs_line, "floor": floor}
        if delta < floor:
            out["problems"].append(f"{mode}：页面底 {canvas} 与卡面 {surface} 的 ΔL* {delta:.2f} 低于下限 {floor}")
        if needs_line and not elev.get("hairline"):
            out["problems"].append(f"{mode}：ΔL* {delta:.2f} 小于 {lim['hairline_below']}，但没有发丝线令牌")
    mix = list(themes["shared"]["dark"]["elevation"]["surfaceMix"].values())
    if mix != sorted(mix) or mix[0] != 0:
        out["problems"].append(f"深色 surfaceMix {mix} 不是从 0 起逐级变亮")
    return out


def columns(container: float, gap: float, min_width: float) -> int:
    """卡片网格的列数：向下取整（（容器宽 + 间距）÷（最小宽 + 间距）），至少 1。"""
    return max(1, math.floor((container + gap) / (min_width + gap)))


def grid_example(ex: dict) -> dict:
    container = ex["content"] if "content" in ex else ex["width"] - 2 * ex["margin"]
    n = columns(container, ex["gap"], ex["min"])
    return {"name": ex["name"], "container": container, "gap": ex["gap"], "min": ex["min"], "columns": n,
            "card_width": round((container - (n - 1) * ex["gap"]) / n, 1)}


def cmd_layers(args, data: dict) -> int:
    themes = json.loads(THEMES_PATH.read_text(encoding="utf-8"))["themes"]
    if args.theme:
        if args.theme not in themes:
            print(f"错误：主题 {args.theme} 不在 themes.json 里；可用：{', '.join(themes)}", file=sys.stderr)
            return 2
        ids = [args.theme]
    else:
        ids = list(themes)
    bad = 0
    lim = data["backgrounds"]["layer_check"]["thresholds"]
    print(f"页面底与卡面的明度差 ΔL*：浅色不低于 {lim['light_min']}，深色不低于 {lim['dark_min']}，小于 {lim['hairline_below']} 时靠发丝线承担分层（本技能取值）")
    for tid in ids:
        r = layer_report(tid, data)
        flag = "不达标" if r["problems"] else "ok"
        lt, dk = r["light"], r["dark"]
        note = " 发丝线承担" if lt["needs_hairline"] else ""
        print(f"{tid:16s} 浅色 {lt['canvas']} / {lt['surface']} ΔL* {lt['delta']:5.2f}{note}   深色 {dk['canvas']} / {dk['surface']} ΔL* {dk['delta']:5.2f}   {flag}")
        for p in r["problems"]:
            print(f"  {p}")
        bad += bool(r["problems"])
    if bad:
        print(f"ui details layers: failed, {bad} of {len(ids)} themes")
        return 1
    print("ui details layers: ok")
    return 0


def cmd_grid(args, data: dict) -> int:
    if args.content is None and args.width is None:
        for ex in data["cards"]["grid"]["examples"]:
            g = grid_example(ex)
            print(f"{g['name']}：容器 {g['container']}，间距 {g['gap']}，最小宽 {g['min']} → {g['columns']} 列，卡宽 {g['card_width']}")
        return 0
    container = args.content if args.content is not None else args.width - 2 * args.margin
    n = columns(container, args.gap, args.min)
    width = (container - (n - 1) * args.gap) / n
    print(f"容器 {container:g}，间距 {args.gap:g}，最小卡宽 {args.min:g} → {n} 列，卡宽 {width:.1f}（repeat(auto-fill, minmax({args.min:g}px, 1fr))）")
    if width < args.min:
        print("注意：只有 1 列且容器比最小卡宽还窄，最小卡宽取大了；按最窄屏重新推导", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- 偏离说明

def rule_of(rule_id: str) -> tuple[str, str] | None:
    for r in load()["rules"]:
        if r["id"] == rule_id:
            return r["strength"], r["text"]
    return dp.rule_of(rule_id)


def make_deviation(rule_id: str, why: str, risk: str, verify: str) -> tuple[dict, list[str]]:
    missing = [k for k, v in (("why", why), ("risk", risk), ("verify", verify)) if not v.strip()]
    if missing:
        raise ValueError("偏离说明缺 " + "、".join(missing))
    found = rule_of(rule_id)
    notes: list[str] = []
    if found:
        level, text = found
    else:
        level, text = "default", ""
        notes.append(f"规则 {rule_id} 不在界面细节规范、页面范式库和设计路径里，按 default 记录；请确认它的出处与强度")
    if level == "must":
        raise ValueError(f"{rule_id} 是 must 规则，不许偏离，只能退回系统技能或换一种做法")
    if level == "hint":
        notes.append(f"{rule_id} 是 hint 级建议，按情境取舍，不必写偏离说明；仍按下面格式记录")
    return {"rule": rule_id, "strength": level, "rule_text": text, "why": why.strip(), "risk": risk.strip(), "verify": verify.strip()}, notes


def cmd_deviation(args, data: dict) -> int:
    try:
        d, notes = make_deviation(args.rule, args.why, args.risk, args.verify)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2
    for n in notes:
        print(f"注意：{n}", file=sys.stderr)
    if args.json:
        print(json.dumps({k: d[k] for k in ("rule", "why", "risk", "verify")}, ensure_ascii=False, indent=2))
    else:
        print(dp.format_deviation(d))
    return 0


# ---------------------------------------------------------------- 查询

def families(data: dict) -> list[dict]:
    return data["cards"]["families"]


def all_ids(data: dict) -> dict[str, tuple[str, Any]]:
    ids: dict[str, tuple[str, Any]] = {}
    for r in data["rules"]:
        ids[r["id"]] = ("规则", r)
    for f in families(data):
        ids[f["id"]] = ("卡片家族", f)
    for s in data["icons"]["systems"]:
        ids[s["id"]] = ("图标类别", s)
    for b in data["backgrounds"]["items"]:
        ids[b["id"]] = ("背景用法", b)
    for b in data["backgrounds"]["layers"]:
        ids[b["id"]] = ("背景分层", b)
    return ids


def plain(text: str) -> str:
    return text.replace("`", "")


def show_rule(r: dict) -> list[str]:
    lines = [f"{r['id']}（{r['strength']}，{r['scope']}，检查：{r['check']}{'，' + r['tool'] if r.get('tool') else ''}）", f"  {r['text']}", "  证据："]
    lines += [f"    [{e['kind']}] {e['ref']}" + (f"：{e['note']}" if e.get("note") else "") for e in r["evidence"]]
    return lines


def show_family(f: dict) -> list[str]:
    mw = f["min_width"]
    mini = "通栏" if mw.get("mini") is None else mw["mini"]
    lines = [f"{f['id']} {f['name']}：主角 {f['role']}；用途 {f['purpose']}",
             f"  对应范式：{'、'.join(f['paradigms'])}；页面：{'、'.join(f['pages']) or '无'}",
             "  字段与顺序：" + " → ".join(f["fields"]),
             f"  去重：{f['dedup']}", f"  图：{f['image']}", f"  点击与操作：{f['actions']}",
             "  状态：" + "；".join(f["states"]), f"  最小卡宽：网页 {mw['web']}，小程序 {mini}",
             "  不要：" + "；".join(f["avoid"]), "  选用前要问：", *[f"    - {q}" for q in f["think"]],
             f"  可以有个性：{f['innovation_room']}"]
    return lines


def show_item(kind: str, item: dict) -> list[str]:
    lines = [f"{item['id']}（{kind}）{item.get('name', '')}"]
    for key, label in (("use", "用在哪里"), ("where", "用在哪里"), ("light", "浅色"), ("dark", "深色"), ("grid", "尺寸与线宽"), ("colour", "颜色来源"), ("tone", "单双色"),
                       ("count", "数量上限"), ("produce", "怎么得到"), ("check", "怎么查"), ("rule", "要点"), ("how", "做法"), ("strength", "强度")):
        if key in item:
            lines.append(f"  {label}：{item[key]}")
    if item.get("think"):
        lines += ["  选用前要问：", *[f"    - {q}" for q in item["think"]]]
    if item.get("innovation_room"):
        lines.append(f"  可以有个性：{item['innovation_room']}")
    return lines


def cmd_list(args, data: dict) -> int:
    print("界面细节规范：图标、背景、卡片家族。强度三档沿用页面范式库；渲染规则页用 render。")
    print("\n图标类别：", "、".join(s["id"] for s in data["icons"]["systems"]))
    print("背景分层：", "、".join(b["id"] for b in data["backgrounds"]["layers"]))
    print("背景用法：", "、".join(b["id"] for b in data["backgrounds"]["items"]))
    print("卡片家族：", "、".join(f["id"] for f in families(data)))
    by_scope: dict[str, list[dict]] = {}
    for r in data["rules"]:
        by_scope.setdefault(r["scope"], []).append(r)
    for scope, rules in by_scope.items():
        print(f"\n规则（{scope}，{len(rules)} 条）：")
        for r in rules:
            print(f"  {r['id']:36s} {r['strength']:8s} {CHECK_LABEL[r['check']]}")
    print("\n其他：show thresholds、palette、basis、method")
    return 0


def cmd_show(args, data: dict) -> int:
    key = args.id
    ids = all_ids(data)
    if key in ids:
        kind, item = ids[key]
        lines = show_rule(item) if kind == "规则" else show_family(item) if kind == "卡片家族" else show_item(kind, item)
    elif key == "thresholds":
        c = data["icons"]["colour"]
        lines = [c["metric"]["status"], c["metric"]["space"], *["  " + p for p in c["metric"]["pixels"]], c["metric"]["stats"]]
        lines += [f"  {t['name']} 不超过 {t['limit']}（{t['flag']}）：{t['fix']}" for t in c["thresholds"]]
        lines += [c["dark_note"], c["control_note"], c["svg_note"], "校准办法：", *[f"  {i}. {s}" for i, s in enumerate(c["calibration"], 1)]]
    elif key == "palette":
        c = data["icons"]["colour"]["palette"]
        lines = [c["intro"], *[f"  {r['role']}：浅色 {r['light']}；深色 {r['dark']}" for r in c["rows"]], c["cap"], c["status"]]
        p = data["icons"]["colour"]["prompt"]
        lines += ["", p["label"], p["text"], p["note"]]
    elif key == "basis":
        lines = [f"[{BASIS_KIND[b['kind']]}] {b['item']}：{b['note']}" for b in data["basis"]]
    elif key == "method":
        pp = json.loads(PATTERNS_PATH.read_text(encoding="utf-8"))["method"]
        lines = [pp["principle"], "规则强度：", *[f"  {k}：{v}" for k, v in pp["strength"].items()], "偏离说明写法：", *[f"  {k}：{v}" for k, v in pp["deviation_format"].items()]]
    else:
        print(f"错误：没有 {key}；用 list 看全部", file=sys.stderr)
        return 2
    print("\n".join(plain(x) for x in lines))
    return 0


# ---------------------------------------------------------------- 规则页渲染

def pre(text: str) -> str:
    return f"<pre><code>{html.escape(text, quote=False)}</code></pre>"


def rules_table(data: dict, scope: str) -> str:
    rows = []
    for r in data["rules"]:
        if r["scope"] != scope:
            continue
        rows.append([code(r["id"]) + "<br>" + code(r["strength"]), inline(r["text"]), CHECK_LABEL[r["check"]]])
    return dp.table(["规则与强度", "要求", "检查"], rows)


def think_table(items: list[dict], label: str = "name") -> str:
    rows = [[inline(i[label]), dp.numbered([inline(q) for q in i["think"]]), inline(i["innovation_room"])] for i in items]
    return dp.table(["类别", "选用前要问的问题", "可以有个性的地方"], rows)


def icons_html(data: dict) -> str:
    ic = data["icons"]
    c = ic["colour"]
    sys_rows = [[f"{inline(s['name'])}<br>{code(s['id'])}",
                 inline(f"用在：{s['where']}。尺寸：{s['grid']}。颜色：{s['colour']}。数量：{s['count']}。得到：{s['produce']}。"),
                 dp.numbered([inline(q) for q in s["think"]]), inline(s["innovation_room"])] for s in ic["systems"]]
    thr_rows = [[inline(t["name"]), f"不超过 {t['limit']:g}" if t["id"] != "hot_share" else f"不超过 {t['limit']:.0%}", inline(t["flag"]), inline(t["fix"])] for t in c["thresholds"]]
    pal = c["palette"]
    pal_rows = [[inline(r["role"]), inline(r["light"]), inline(r["dark"])] for r in pal["rows"]]
    tune_rows = [[inline(t["symptom"]), inline(t["move"]), inline(t["check"])] for t in c["tuning"]]
    mistake_rows = [[inline(m["symptom"]), inline(m["cause"]), inline(m["fix"])] for m in ic["mistakes"]]
    prompt = c["prompt"]
    return "\n".join([
        "<h3>二、图标</h3>",
        "<h4>图标体系：三类各有各的规则</h4>",
        dp.table(["类别", "规则", "选用前要问的问题", "可以有个性的地方"], sys_rows),
        "<h4>颜色与饱和度阈值</h4>",
        f"<p>{inline(c['metric']['space'])}统计范围：{inline('；'.join(c['metric']['pixels']))}。{inline(c['metric']['stats'])}</p>",
        dp.table(["指标", "起始上限（本技能取值）", "命令行参数", "超限怎么修"], thr_rows),
        f"<p>{inline(c['metric']['scope'])}{inline(c['metric']['status'])}</p>",
        f"<p>{inline(c['control_note'])}{inline(c['svg_note'])}</p>",
        "<h4>图标色板与提示词</h4>",
        f"<p>{inline(pal['intro'])}</p>",
        dp.table(["色板", "浅色", "深色"], pal_rows),
        f"<p>{inline(pal['cap'])}{inline(pal['status'])}</p>",
        f"<p>{inline(prompt['label'])}：</p>",
        pre(prompt["text"]),
        f"<p>{inline(prompt['note'])}</p>",
        "<h4>校准：用户说还是太艳或太淡时改哪个数</h4>",
        dp.ol([inline(s) for s in c["calibration"]]),
        dp.table(["症状", "先动哪个数", "再看"], tune_rows),
        f"<p>{inline(c['sample'])}</p>",
        "<h4>图标常见失误</h4>",
        dp.table(["症状", "原因", "怎么修"], mistake_rows),
        "<h4>图标规则</h4>",
        rules_table(data, "icons"),
    ])


def backgrounds_html(data: dict) -> str:
    bg = data["backgrounds"]
    lc = bg["layer_check"]
    layer_rows = [[f"{inline(l['name'])}", inline(l["use"]), inline(l["light"]), inline(l["dark"])] for l in bg["layers"]]
    item_rows = [[inline(i["name"]) + "<br>" + code(i["id"]) + "<br>" + code(i["strength"]), inline(i["rule"] + "。" + i["how"]),
                  dp.numbered([inline(q) for q in i["think"]]), inline(i["innovation_room"])] for i in bg["items"]]
    return "\n".join([
        "<h3>三、背景</h3>",
        "<h4>三层分层，全取令牌</h4>",
        dp.table(["层", "用在哪里", "浅色", "深色"], layer_rows),
        "<h4>分层检查量</h4>",
        f"<p>{inline(lc['measure'] + lc['text'] + lc['observed'] + lc['status'] + lc['command'])}</p>",
        "<h4>五类用法</h4>",
        dp.table(["用法", "要点与做法", "选用前要问的问题", "可以有个性的地方"], item_rows),
        "<h4>背景规则</h4>",
        rules_table(data, "backgrounds"),
    ])


def card_row(f: dict) -> list[str]:
    mw = f["min_width"]
    mini = "通栏" if mw.get("mini") is None else str(mw["mini"])
    head = f"{inline(f['name'])}<br>{code(f['id'])}<br>主角：{inline(f['role'])}<br>范式：{'、'.join(code(p) for p in f['paradigms'])}<br>最小宽：网页 {mw['web']}，小程序 {mini}"
    body = (f"字段：{inline(' → '.join(f['fields']))}。去重：{inline(f['dedup'])}。<br>图：{inline(f['image'])}。<br>点击：{inline(f['actions'])}。<br>"
            f"状态：{inline('；'.join(f['states']))}。<br>不要：{inline(f['avoid'][0])}。")
    return [head, body, dp.numbered([inline(q) for q in f["think"]]), inline(f["innovation_room"])]


def cards_html(data: dict) -> str:
    cd = data["cards"]
    fit, grid = cd["fit"], cd["grid"]
    ex_rows = []
    for e in grid["examples"]:
        g = grid_example(e)
        ex_rows.append([inline(g["name"]), f"{g['container']:g}", f"{g['gap']:g}", f"{g['min']:g}", f"{g['columns']}"])
    return "\n".join([
        "<h3>四、卡片家族</h3>",
        "<h4>先判断该不该用卡片</h4>",
        f"<p>适合：{inline(fit['use_when'])}。不适合：{inline(fit['avoid_when'])}。代价：{inline(fit['cost'])}。整卡可点、点击区与悬停的行为见系统技能规则卡 {code('interaction-patterns')}。</p>",
        "<h4>九个家族</h4>",
        dp.table(["家族", "字段、图、点击、状态", "选用前要问的问题", "可以有个性的地方"], [card_row(f) for f in cd["families"]]),
        "<h4>栅格怎么排</h4>",
        f"<p>{inline(grid['formula'])}。{inline(grid['mini_note'])}命令：{code('ui_details.py grid --min 160 --gap 12 --width 375')}。</p>",
        dp.table(["例", "容器宽", "间距", "最小宽", "列数"], ex_rows),
        "<h4>卡片规则</h4>",
        rules_table(data, "cards"),
    ])


def sections_html(data: dict) -> dict[str, str]:
    pg = data["page"]
    own = data["ownership"]
    own_rows = [[inline(r["topic"]), inline(r["system"]), inline(r["design"])] for r in own["rows"]]
    chain_rows = [[inline(name), dp.numbered([inline(s) for s in data["think_chains"][key]])] for key, name in (("icons", "图标"), ("backgrounds", "背景"), ("cards", "卡片"))]
    basis_rows = [[inline(b["item"]), BASIS_KIND[b["kind"]], inline(b["note"])] for b in data["basis"]]
    rules = "\n".join([
        "<h3>一、先分清功能和视觉</h3>",
        f"<p>{inline(own['text'])}</p>",
        icons_html(data),
        backgrounds_html(data),
        cards_html(data),
        "<h3>五、怎么用</h3>",
        dp.ul([inline(u) for u in pg["usage"]]),
        dp.table(["思考链", "按这个次序问"], chain_rows),
        "<h4>方法规则</h4>",
        rules_table(data, "method"),
        "<h4>依据与资料没覆盖的地方</h4>",
        dp.table(["条目", "性质", "备注"], basis_rows),
    ])
    mrows = [[inline(m["surface"]), inline(m["icons"]), inline(m["bg"]), inline(m["cards"])] for m in pg["matrix"]]
    ex_rows = [[inline(e["title"]) + "<br>问：" + inline(e["ask"]), inline(e["do"]), inline(e["result"])] for e in pg["examples"]]
    return {
        "scope": f"<p>{inline(pg['scope'])}</p>",
        "workflow": dp.ol([inline(w) for w in pg["workflow"]]),
        "rules": rules,
        "platform-matrix": dp.table(["端", "图标", "背景", "卡片"], mrows),
        "examples": dp.table(["样本", "怎么做", "得到什么"], ex_rows),
        "output-contract": dp.ul([inline(o) for o in pg["output"]]),
        "quality-gates": dp.ul([inline(g) for g in pg["gates"]]) + f"\n<p>命令：{inline(pg['gate_commands'])}</p>",
        "handoff": dp.ul([inline(h) for h in pg["handoff"]]),
    }


def render_html(data: dict | None = None) -> str:
    data = data or load()
    title = data["title"]
    body = sections_html(data)
    parts = ["<!doctype html>", '<html lang="zh-CN">', "<head>", '  <meta charset="utf-8">',
             '  <meta name="viewport" content="width=device-width, initial-scale=1">', f"  <title>{title}</title>",
             f'  <link rel="icon" href="{dp.FAVICON}">', '  <link rel="stylesheet" href="guidelines.css">', "</head>", "<body>",
             f'<main id="main" aria-label="{title}">', f"    <h1>{title}</h1>"]
    for sid, name, icon in dp.SECTIONS:
        parts += [f"<!-- SECTION:{sid}:START id={sid} data-rule-id={PREFIX}-{sid} -->",
                  f'<section id="{sid}" data-rule-id="{PREFIX}-{sid}" aria-labelledby="{sid}-heading">',
                  f'<h2 id="{sid}-heading" class="section-heading">{dp.SVG_OPEN}{icon}</svg><span>{name}</span></h2>',
                  body[sid], "</section>", f"<!-- SECTION:{sid}:END -->", ""]
    parts += ["</main>", "</body>", "</html>", ""]
    return "\n".join(parts)


def cmd_render(args, data: dict) -> int:
    text = render_html(data)
    if args.check:
        same = PAGE_PATH.is_file() and PAGE_PATH.read_text(encoding="utf-8") == text
        print("规则页与数据一致" if same else "规则页与 ui-details.json 不一致：运行 render --write")
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
    sub.add_parser("list", help="类别、家族与全部规则")
    s = sub.add_parser("show", help="一条规则、一个家族、一个类别，或 thresholds、palette、basis、method")
    s.add_argument("id")
    s = sub.add_parser("layers", help="页面底与卡面的明度差，三层分层检查")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--theme")
    g.add_argument("--all", action="store_true")
    s = sub.add_parser("grid", help="卡片网格的列数")
    s.add_argument("--min", type=float, default=160, help="最小卡宽")
    s.add_argument("--gap", type=float, default=12)
    s.add_argument("--width", type=float, help="屏宽（再减两侧页边距）")
    s.add_argument("--margin", type=float, default=12, help="页边距，默认 12")
    s.add_argument("--content", type=float, help="直接给容器宽")
    s = sub.add_parser("deviation", help="标准格式的偏离说明；must 规则拒绝")
    s.add_argument("rule")
    s.add_argument("--why", required=True)
    s.add_argument("--risk", required=True)
    s.add_argument("--verify", required=True)
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("render", help="由数据文件生成规则页")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    data = load()
    return {"list": cmd_list, "show": cmd_show, "layers": cmd_layers, "grid": cmd_grid, "deviation": cmd_deviation, "render": cmd_render}[args.cmd](args, data)


if __name__ == "__main__":
    sys.exit(main())
