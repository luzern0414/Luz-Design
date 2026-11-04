"""后台模板（admin）的生成器插件：scripts/build_prototype.py 通过 ``check(spec, ctx)`` 与 ``build(spec, ctx)`` 取到要嵌进共用外壳的各段。

约定见 references/prototype-templates/engine/ENGINE.md 第十一节。这里只有机制：侧栏、顶栏、多标签页、面包屑、列表 / 表单 / 设置 / 工作台 / 结果 / 居中面板的画法；
没有任何行业内容，也不规定后台必须有哪些菜单、页面或组件（菜单、页面清单、字段、数据、文案都由项目的功能说明和规格决定）。校验只查结构：
引用是否成立（页面、标签、角色、组件编号存在）、入口规则（分组、面包屑、居中面板）、控件规则（图标、外露筛选数量、分页档位）。
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABS_KEY = "nav"
DARK_MODE = "tokens"
DEFAULT_MARK = "<rect x='5' y='6' width='22' height='20' rx='4'/><path d='M5 12h22M12 12v14'/>"

PAGE_TYPES = {"tab", "sub", "sheet", "result"}
CONTENT_KEYS = ("list", "dashboard", "form", "settings", "detail", "result", "blocks", "custom")
PAGE_KEYS = {
    "id", "name", "type", "tab", "roles", "scenes", "links", "logic", "base", "baseArg", "offline", "title", "crumb", "actions", "empty", "layout",
    "blocks", "custom", "args", "titleNew", "maskClose", "list", "dashboard", "form", "settings", "detail", "result", "header", "footer", "nav", "light", "headerBg", "tabbar",
}
COLUMN_TYPES = {"text", "long", "num", "money", "status", "tag", "date", "datetime", "person", "thumb", "switch", "two", "rating"}
FIELD_TYPES = {"text", "textarea", "number", "money", "select", "radio", "switch", "tags", "images", "slider", "date", "ro"}
SECTION_KINDS = {"trend", "donut", "rank", "todo", "feed", "agenda"}
SETTING_TYPES = {"switch", "number", "radio"}
PAGE_SIZES = {10, 20, 50, 100}
MAX_EXPOSED_FILTERS = 4
NAV_KEYS = ("go", "sheet", "tab", "act", "toast", "back", "export")

# 各功能用到的库组件编号（只带这些组件所在的 blocks-*.js，名字出现在右栏“本页组件”里）
BASE_CIDS = ["AD-NAV-001", "AD-NAV-002", "AD-NAV-003", "AD-NAV-004", "AD-NAV-005", "AD-NAV-006", "AD-NAV-007", "AD-NAV-011", "AD-NAV-012", "AD-NAV-013",
             "AD-FB-001", "AD-FB-002", "AD-FB-003", "AD-FB-004", "AD-FB-009", "AD-STATE-001", "AD-STATE-002", "AD-STATE-003", "AD-STATE-004", "AD-STATE-006"]
FEATURE_CIDS = {
    "list": ["AD-TBL-001", "AD-TBL-002", "AD-TBL-003", "AD-FLT-002", "AD-FLT-006", "AD-FLT-010"],
    "form": ["AD-FORM-002", "AD-FORM-008"],
    "dashboard": ["AD-DATA-001", "AD-DATA-005", "AD-DATA-007", "AD-CHART-001", "AD-CHART-005", "AD-CTRL-006", "AD-FLOW-009", "AD-FLOW-005"],
    "settings": ["AD-PAGE-005", "AD-MGMT-007"],
}


def line_icons(library: Path) -> set[str]:
    """库里线性图标的名字（kit.js / extras.js / 各 blocks 文件顶部的 Object.assign(LINE, …)）。只用来提示拼错的图标名。"""
    names: set[str] = set()
    for f in [library / "src" / "kit.js", library / "src" / "extras.js", *sorted((library / "src").glob("blocks-*.js"))]:
        if f.is_file():
            names |= set(re.findall(r"(?:^|[\s,{])([a-z][a-z0-9_]*):\s*'<(?:path|circle|rect|g|ellipse|line|polyline|polygon)", f.read_text(encoding="utf-8")))
    return names


def _targets(where: str, a: dict, pages: dict, tab_ids: set, errs: list[str]) -> None:
    """一个动作描述（按钮 / 行操作 / 结果页按钮）里的跳转目标必须存在，且类型对得上。"""
    if a.get("go"):
        pg = pages.get(str(a["go"]).split(":")[0])
        if pg is None:
            errs.append(f"{where}：规格引用了不存在的页面「{a['go']}」（go）")
        elif pg.get("type") == "tab":
            errs.append(f"{where}：go 的目标「{pg['id']}」是侧栏一级页，不能压栈，请改用 tab（侧栏标签只由侧栏和标签页切换）")
        elif pg.get("type") == "sheet":
            errs.append(f"{where}：go 的目标「{pg['id']}」是居中面板，请改用 sheet")
    if a.get("sheet"):
        pg = pages.get(str(a["sheet"]).split(":")[0])
        if pg is None:
            errs.append(f"{where}：规格引用了不存在的页面「{a['sheet']}」（sheet）")
        elif pg.get("type") != "sheet":
            errs.append(f"{where}：sheet 的目标「{pg['id']}」不是居中面板页（类型是 {pg.get('type')}）")
    if a.get("tab") and a["tab"] not in tab_ids:
        errs.append(f"{where}：规格引用了不存在的侧栏标签「{a['tab']}」（tab 要写 nav 里的 id，不是页面 id）")


def check(spec: dict, ctx) -> list[str]:
    """后台自己的规格检查：只查结构（引用、入口、控件规则），不查行业内容。"""
    out: list[str] = []
    pages = {p["id"]: p for p in spec["pages"]}
    nav = spec.get("nav") or []
    leaves = nav_leaves(nav)
    tab_ids = {t.get("id") for t in leaves}
    nav_by_page = {t.get("page"): t for t in leaves}
    roles = {r["id"] for r in spec.get("roles") or []}
    data = spec.get("data") or {}
    icons = line_icons(getattr(ctx, "library_dir", HERE.parent.parent / "component-library"))

    # --- 侧栏菜单：带 page 的是标签；不带 page、带 children 的是分组节点。
    #     分组节点没有图标 = 分组标题（子项是一级项，要带线性图标）；有图标 = 手风琴父项（子项不放图标）。
    #     分组只在组内有两项及以上时使用；分组名不与组内唯一一项同名；最多三级（分组标题不算层级）。
    def visible(nodes):
        return [n for n in nodes or [] if not n.get("hidden")]

    def check_nodes(nodes: list, level: int) -> None:
        for n in nodes or []:
            name = n.get("name")
            if n.get("group"):
                out.append(f"侧栏项「{name}」写了 group：后台用分组节点（带 children、不带 page 的项）表示分组，不用扁平的 group 字段")
            if n.get("page") and n.get("children"):
                out.append(f"侧栏项「{name}」既有 page 又有 children：有子项的项只负责展开收起，需要概览页时把“概览”放在子项的第一位")
            if n.get("children") and not n.get("page"):
                kids = visible(n["children"])
                section = not n.get("icon")
                if len(kids) < 2 and not n.get("hidden"):
                    if len(kids) == 1 and kids[0].get("name") == name:
                        out.append(f"侧栏分组「{name}」下只有一项「{name}」且与分组同名：取消分组，把菜单项直接放在侧栏里")
                    else:
                        out.append(f"侧栏分组「{name}」下只有 {len(kids)} 项：分组只在组内有两项及以上时使用，只有一项就取消分组，直接放菜单项")
                child_level = level if section else level + 1
                if child_level > 3:
                    out.append(f"侧栏「{name}」的子项超过三级：最多三级（分组标题不算层级），把低频页合并，或把类型变成列表筛选")
                    continue
                check_nodes(n["children"], child_level)
            elif n.get("page") and not n.get("hidden"):
                if level == 1:
                    if not n.get("icon"):
                        out.append(f"侧栏菜单「{name}」没写 icon：每个一级菜单项前面要有线性图标")
                    elif icons and n["icon"] not in icons:
                        out.append(f"警告：侧栏菜单「{name}」的图标名「{n['icon']}」不在库的线性图标里（拼写对吗？）")
                elif n.get("icon"):
                    out.append(f"侧栏菜单「{name}」是二、三级项，不放图标：只有一级项带线性图标（去掉 icon）")

    check_nodes(nav, 1)
    if len(visible(nav)) > 12:
        out.append("警告：侧栏一级菜单超过 12 项，按业务域分组，或把低频页收进“更多”")

    # --- 页面
    for p in spec["pages"]:
        pid, typ = p["id"], p.get("type")
        if typ == "panel":
            out.append(f"页面「{pid}」的类型 panel 在后台里不单独使用：居中面板请写 type: sheet 并加 layout: center（详情、编辑、确认一律居中悬浮，不用右侧抽屉）")
            continue
        if typ not in PAGE_TYPES:
            out.append(f"页面「{pid}」的类型「{typ}」不对，后台只有 {'、'.join(sorted(PAGE_TYPES))}")
        has = [k for k in CONTENT_KEYS if p.get(k)]
        if not has:
            out.append(f"页面「{pid}」没有内容：list / dashboard / form / settings / detail / result / blocks / custom 至少写一个")
        if typ == "sheet":
            if p.get("layout") not in (None, "center"):
                out.append(f"居中面板页「{pid}」的 layout 是「{p['layout']}」：后台的详情、编辑、确认一律居中悬浮，不从底部或右侧滑出，请写 center 或不写")
            if not any(k in has for k in ("detail", "form", "blocks", "custom")):
                out.append(f"居中面板页「{pid}」要有 detail、form、blocks 或 custom 之一")
        if typ != "sheet" and p.get("detail"):
            out.append(f"页面「{pid}」写了 detail，但详情内容只能放在居中面板页（type: sheet）里")
        if typ == "tab":
            tabn = nav_by_page.get(pid) or {}
            if p.get("crumb") or p.get("breadcrumb"):
                out.append(f"一级页「{pid}」不能放面包屑：面包屑只在二级页、子页和结果页出现，一级菜单页不放")
            if p.get("title") and tabn and p["title"].strip() == str(tabn.get("name", "")).strip():
                out.append(f"一级页「{pid}」的 title「{p['title']}」与侧栏高亮项同名：高亮菜单已经说明了本页，内容区顶部不再放同名大标题（去掉 title）")
        if typ in ("sub", "result") and not p.get("tab"):
            out.append(f"页面「{pid}」没写 tab：二级页和结果页要说明属于哪个侧栏标签（面包屑的上级）")
        unknown = sorted(set(p) - PAGE_KEYS)
        if unknown:
            out.append(f"警告：页面「{pid}」有后台模板不认识的字段：{'、'.join(unknown)}（拼写对吗？）")
        for area in ("blocks",):
            for i, it in enumerate(p.get(area) or []):
                if not isinstance(it, dict) or not any(k in it for k in ("cid", "custom", "gap", "heading")):
                    out.append(f"页面「{pid}」{area}[{i}] 要写 cid（组件编号）、custom（内容模块里的渲染函数）、gap（间距）或 heading（小标题）之一")

        # 页面顶部操作：最多 1 个主按钮 + 2 个次按钮，每个都带图标，目标存在
        acts = p.get("actions") or []
        if len(acts) > 3:
            out.append(f"页面「{pid}」顶部操作有 {len(acts)} 个：最多 1 个主按钮加 2 个次按钮，其余收进“更多”或放进行内")
        if sum(1 for a in acts if a.get("kind") == "primary") > 1:
            out.append(f"页面「{pid}」有多个主按钮：一屏只放一个主按钮")
        for a in acts:
            w = f"页面「{pid}」的操作「{a.get('label')}」"
            if not a.get("label"):
                out.append(f"页面「{pid}」有操作没写 label")
            if not a.get("icon"):
                out.append(f"{w}没写 icon：页面与卡片上的功能按钮前面要有线性图标")
            elif icons and a["icon"] not in icons:
                out.append(f"警告：{w}的图标名「{a['icon']}」不在库的线性图标里")
            if not any(a.get(k) for k in NAV_KEYS):
                out.append(f"{w}没有去处：go / sheet / tab / act / toast / back / export 至少写一个")
            _targets(w, a, pages, tab_ids, out)

        if p.get("list"):
            _check_list(p, pages, tab_ids, data, out, icons)
        if p.get("dashboard"):
            _check_dashboard(p, pages, tab_ids, out)
        if p.get("form"):
            _check_form(p, data, out)
        if p.get("settings"):
            _check_settings(p, data, out)
        if p.get("detail"):
            D = p["detail"]
            if not D.get("data"):
                out.append(f"详情面板「{pid}」没写 detail.data（记录所在的数据路径）")
            for a in D.get("actions") or []:
                if not a.get("label") or not a.get("id"):
                    out.append(f"详情面板「{pid}」有动作没写 id 或 label")
                _targets(f"详情面板「{pid}」的动作「{a.get('label')}」", a, pages, tab_ids, out)
        if p.get("result"):
            R = p["result"]
            if not R.get("title"):
                out.append(f"结果页「{pid}」没写 result.title")
            for a in R.get("actions") or []:
                _targets(f"结果页「{pid}」的按钮「{a.get('label')}」", a, pages, tab_ids, out)
            if not R.get("actions"):
                out.append(f"结果页「{pid}」没有下一步按钮：结果页至少给“返回列表”这类一个去处，不能让用户无路可走")

    # --- 外壳数据（顶层 shell 并进 data.shell）：通知的跳转目标要存在；noticePage、profilePage 由生成器检查
    sh = {**(data.get("shell") or {}), **(spec.get("shell") or {})}
    for n in sh.get("notices") or []:
        if n.get("go") and n["go"] not in pages:
            out.append(f"规格引用了不存在的页面「{n['go']}」（通知「{n.get('title')}」的 go）")
    # --- 同一页里的模块标识（场景面板“模块显示”用）不能重复
    for p in spec["pages"]:
        ids = [it.get("id") for it in p.get("blocks") or [] if isinstance(it, dict) and it.get("id")]
        ids += [s.get("id") for s in (p.get("dashboard") or {}).get("sections") or [] if s.get("id")]
        for i in {x for x in ids if ids.count(x) > 1}:
            out.append(f"页面「{p['id']}」里的模块 id「{i}」重复了：同一页内模块 id 不能重复（场景面板“模块显示”按它认模块）")
    return out


def _check_list(p: dict, pages: dict, tab_ids: set, data: dict, out: list[str], icons: set) -> None:
    pid, L = p["id"], p["list"]
    w = f"列表页「{pid}」"
    if not L.get("data"):
        out.append(f"{w}没写 list.data（数据所在的路径）")
    cs = L.get("columns") or []
    if not cs:
        out.append(f"{w}没有 columns")
    keys = [c.get("key") for c in cs]
    for k in {x for x in keys if keys.count(x) > 1}:
        out.append(f"{w}的列「{k}」重复了")
    for c in cs:
        if not c.get("key") or not c.get("label"):
            out.append(f"{w}有列没写 key 或 label")
        if c.get("type", "text") not in COLUMN_TYPES:
            out.append(f"{w}的列「{c.get('label')}」类型「{c.get('type')}」不认识（可用：{'、'.join(sorted(COLUMN_TYPES))}）")
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(c.get("label", ""))):
            out.append(f"{w}的列表头「{c.get('label')}」是英文字段名：表头和导出里不出现英文字段名，写中文业务名")
        m = c.get("map") or (c.get("key") if c.get("type") == "status" else None)
        if m and isinstance(m, str) and data and m not in (data.get("maps") or {}):
            out.append(f"{w}的列「{c.get('label')}」引用了不存在的状态映射「{m}」（data.maps.{m}）")
    if len([c for c in cs if not c.get("hide")]) < 2:
        out.append(f"{w}可见的列少于 2 列")
    F = L.get("filters") or {}
    exposed = (1 if F.get("search") else 0) + len(F.get("primary") or [])
    if exposed > MAX_EXPOSED_FILTERS:
        out.append(f"{w}外露筛选有 {exposed} 个：最多 {MAX_EXPOSED_FILTERS} 个（搜索框加 2–3 个最常用条件），其余放进 filters.more（“更多筛选”）")
    for f in (F.get("primary") or []) + (F.get("more") or []):
        opts = f.get("options")
        if isinstance(opts, str) and data and opts not in (data.get("options") or {}):
            out.append(f"{w}的筛选「{f.get('label')}」引用了不存在的选项表「{opts}」（data.options.{opts}）")
    T = L.get("tabs")
    if T:
        mp = (data.get("maps") or {}).get(T.get("map") or T.get("key"))
        if data and mp is None:
            out.append(f"{w}的状态标签引用了不存在的状态映射「{T.get('map') or T.get('key')}」（data.maps）")
        elif mp is not None:
            for v in list(T.get("order") or []) + list(T.get("more") or []):
                if v not in mp:
                    out.append(f"{w}的状态标签「{v}」不在状态映射里")
        if T.get("default") not in (None, "__all") and T["default"] not in (T.get("order") or []) + (T.get("more") or []):
            out.append(f"{w}的默认状态标签「{T['default']}」不在 tabs.order / tabs.more 里")
        if not T.get("default") and T.get("order"):
            out.append(f"警告：{w}没写默认状态标签：列表打开时应显示最需要处理的子集，“全部”放在可选项里")
    if L.get("pageSize") and L["pageSize"] not in PAGE_SIZES:
        out.append(f"{w}的 pageSize {L['pageSize']} 不在可选档位 10 / 20 / 50 / 100 里（默认 20）")
    for a in (L.get("rowActions") or []) + (L.get("moreActions") or []) + (L.get("bulk") or []):
        if not a.get("id") or not a.get("label"):
            out.append(f"{w}有行操作或批量操作没写 id 或 label")
            continue
        if a.get("icon") and a in (L.get("rowActions") or []):
            out.append(f"{w}的行操作「{a['label']}」带了图标：行内文字操作不加图标（图标只给页面与卡片上的功能按钮）")
        if not any(a.get(k) for k in ("sheet", "go", "tab", "act", "patch", "append", "inc", "close")):
            out.append(f"{w}的操作「{a['label']}」没有动作：sheet / go / tab / act / patch / inc 至少写一个")
        _targets(f"{w}的操作「{a['label']}」", a, {k: v for k, v in pages.items()}, tab_ids, out)
    if len(L.get("rowActions") or []) > 3:
        out.append(f"{w}外露的行操作超过 3 个：最常用的两个文字操作外露，其余放进 moreActions（“更多”）")
    for c in cs:
        if c.get("type") == "switch" and not c.get("key"):
            out.append(f"{w}的开关列没写 key")


def _check_dashboard(p: dict, pages: dict, tab_ids: set, out: list[str]) -> None:
    pid, D = p["id"], p["dashboard"]
    w = f"工作台「{pid}」"
    ks = D.get("kpis") or []
    if len(ks) > 9:
        out.append(f"{w}的指标卡有 {len(ks)} 张：单屏 5–9 个模块，指标卡不要超过 9 张")
    ids = [k.get("id") for k in ks]
    for k in ks:
        if not k.get("id") or not k.get("label") or not k.get("calc"):
            out.append(f"{w}有指标卡没写 id、label 或 calc")
            continue
        c = k["calc"]
        if c.get("op") not in ("sum", "avg", "last", "ratio") or not c.get("src"):
            out.append(f"{w}的指标「{k['label']}」calc 要写 op（sum / avg / last / ratio）和 src")
        if c.get("op") == "ratio" and not (c.get("num") and c.get("den")):
            out.append(f"{w}的指标「{k['label']}」是比率，要写 num 和 den")
        if c.get("op") != "ratio" and not c.get("field"):
            out.append(f"{w}的指标「{k['label']}」calc 缺 field")
    for i in {x for x in ids if ids.count(x) > 1}:
        out.append(f"{w}的指标 id「{i}」重复了")
    for a in D.get("alerts") or []:
        if a.get("kpi") not in ids:
            out.append(f"{w}的预警「{a.get('id')}」引用了不存在的指标「{a.get('kpi')}」")
        if a.get("tab") and a["tab"] not in tab_ids:
            out.append(f"{w}的预警「{a.get('id')}」引用了不存在的侧栏标签「{a['tab']}」")
    for i, S in enumerate(D.get("sections") or []):
        if S.get("kind") not in SECTION_KINDS:
            out.append(f"{w}的模块 {i + 1} 类型「{S.get('kind')}」不认识（可用：{'、'.join(sorted(SECTION_KINDS))}）")
            continue
        if S["kind"] == "todo":
            for t in S.get("items") or []:
                if t.get("tab") and t["tab"] not in tab_ids:
                    out.append(f"{w}的待办「{t.get('label')}」引用了不存在的侧栏标签「{t['tab']}」")
                if t.get("sheet") and (t["sheet"] not in pages or pages[t["sheet"]].get("type") != "sheet"):
                    out.append(f"{w}的待办「{t.get('label')}」引用了不存在的居中面板「{t['sheet']}」")
        if S["kind"] == "trend" and not S.get("metrics"):
            out.append(f"{w}的趋势图「{S.get('title')}」没写 metrics")
        if S["kind"] in ("feed",):
            for r in []:
                pass
        if not S.get("title"):
            out.append(f"{w}的模块 {i + 1} 没写 title")


def _check_form(p: dict, data: dict, out: list[str]) -> None:
    pid, F = p["id"], p["form"]
    w = f"表单「{pid}」"
    fs = [f for s in F.get("sections") or [] for f in s.get("fields") or []]
    if not fs:
        out.append(f"{w}没有字段")
    keys = [f.get("key") for f in fs]
    for k in {x for x in keys if keys.count(x) > 1}:
        out.append(f"{w}的字段「{k}」重复了")
    for f in fs:
        if not f.get("key") or not f.get("label"):
            out.append(f"{w}有字段没写 key 或 label")
        if f.get("type", "text") not in FIELD_TYPES:
            out.append(f"{w}的字段「{f.get('label')}」类型「{f.get('type')}」不认识（可用：{'、'.join(sorted(FIELD_TYPES))}）")
        if f.get("type") in ("select", "radio") and not f.get("options"):
            out.append(f"{w}的字段「{f.get('label')}」是选择类，要写 options")
        if isinstance(f.get("options"), str) and data and f["options"] not in (data.get("options") or {}):
            out.append(f"{w}的字段「{f.get('label')}」引用了不存在的选项表「{f['options']}」（data.options.{f['options']}）")
    if not F.get("submit"):
        out.append(f"{w}没写 submit（保存按钮、结果提示、保存后去哪）")
    elif F["submit"].get("then") not in (None, "back", "close", "stay"):
        out.append(f"{w}的 submit.then 只能是 back / close / stay")


def _check_settings(p: dict, data: dict, out: list[str]) -> None:
    pid, S = p["id"], p["settings"]
    w = f"设置页「{pid}」"
    if not S.get("data") or not S.get("groups"):
        out.append(f"{w}要写 settings.data 和 settings.groups")
        return
    keys: list[str] = []
    for g in S["groups"]:
        for sec in g.get("sections") or []:
            for it in sec.get("items") or []:
                keys.append(it.get("key"))
                if it.get("type") not in SETTING_TYPES:
                    out.append(f"{w}的设置项「{it.get('label')}」类型「{it.get('type')}」不对（可用：{'、'.join(sorted(SETTING_TYPES))}）")
                if not it.get("impact"):
                    out.append(f"{w}的设置项「{it.get('label')}」没写 impact：每项写一句影响说明")
                if it.get("type") == "radio" and not it.get("options"):
                    out.append(f"{w}的设置项「{it.get('label')}」是单选，要写 options（中文选项名，不显示代码值）")
                if it.get("type") == "number" and "default" not in it:
                    out.append(f"{w}的设置项「{it.get('label')}」没写 default（用于恢复默认）")
    for k in {x for x in keys if keys.count(x) > 1}:
        out.append(f"{w}的设置项 key「{k}」重复了")


def nav_leaves(nodes: list, out: list | None = None) -> list:
    """侧栏里所有带 page 的节点（标签），不含分组节点。"""
    out = [] if out is None else out
    for n in nodes or []:
        if n.get("page"):
            out.append(n)
        nav_leaves(n.get("children"), out)
    return out


def edges(page: dict, spec: dict) -> list[str]:
    """这一页产生、但不在 blocks 覆盖里的跳转（list 行操作与批量操作、页面顶部操作、工作台待办与预警、表单保存后去哪、详情动作、结果页按钮）。
    生成器把它并进孤岛检查；只报存在的页面，不存在的由 check() 报错。"""
    pages = {p["id"]: p for p in spec["pages"]}
    tab_pages = {n["id"]: n["page"] for n in nav_leaves(spec.get("nav") or [])}
    out: list[str] = []

    def add(a: dict) -> None:
        for k in ("go", "sheet"):
            v = a.get(k)
            if isinstance(v, str) and v.split(":")[0] in pages:
                out.append(v)
        if a.get("tab") in tab_pages:
            out.append(tab_pages[a["tab"]])

    for a in page.get("actions") or []:
        add(a)
    L = page.get("list") or {}
    for a in (L.get("rowActions") or []) + (L.get("moreActions") or []) + (L.get("bulk") or []):
        add(a)
    D = page.get("dashboard") or {}
    for s in D.get("sections") or []:
        for t in s.get("items") or []:
            add(t)
    for a in D.get("alerts") or []:
        add(a)
    sub = (page.get("form") or {}).get("submit") or {}
    for k in ("thenNew", "go"):
        if sub.get(k) in pages:
            out.append(sub[k])
    for a in (page.get("detail") or {}).get("actions") or []:
        add(a)
    for a in (page.get("result") or {}).get("actions") or []:
        add(a)
    return out


def used_features(spec: dict) -> set[str]:
    feats: set[str] = set()
    for p in spec["pages"]:
        for k in ("list", "form", "dashboard", "settings"):
            if p.get(k):
                feats.add(k)
    return feats


def build(spec: dict, ctx) -> dict:
    parts = sorted((HERE / "js").glob("*.js"))
    js = "\n".join(f"/* ---- {f.name} ---- */\n" + f.read_text(encoding="utf-8") for f in parts)
    cids = list(BASE_CIDS)
    for feat in used_features(spec):
        cids += FEATURE_CIDS[feat]
    return {
        "css": (HERE / "admin.css").read_text(encoding="utf-8"),
        "js": js,
        "stage_html": (HERE / "stage.html").read_text(encoding="utf-8"),
        "cids": sorted(set(cids)),
        "head": "",
    }
