#!/usr/bin/env python3
"""Build the single-file entry of each template folder.

  py -X utf8 scripts/build_templates.py [app|web|poster|documents|all]

  templates/app/app.html        tabs 整页模板 | 组件库      sources: templates/app/source/pages/*.html and source/parts/*.part
  templates/web/web.html        the same for the web back office
  templates/poster/poster.html  tabs 海报模板 | 提示词库     sources: templates/poster/source/templates/PS-*.html and source/prompts/
  templates/documents/documents.html   the catalog of the five document types (data: templates/documents/*/manifest.json)

The built files are generated: edit the sources and build again, never the built file. Pages and the component library are stored verbatim in
<script type="text/html"> blocks and mounted into iframes on demand, so one file holds everything and the pages keep their own CSS and JS.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import sync_template_tokens as tokens  # noqa: E402

T = ROOT / "templates"
EFFECTS = [("glow", "柔光"), ("none", "无"), ("dots", "点阵"), ("grid", "网格"), ("lines", "斜纹"), ("rings", "同心圆"), ("petal", "花瓣"), ("leaf", "叶片"), ("wave", "波纹")]
CID = re.compile(r'data-cid="([A-Z]{2}-[A-Z]{3,4}-\d{3})"')
TAG_NAME = re.compile(r'<[^>]*\bdata-cid="(?P<id>[^"]+)"[^>]*\bdata-name="(?P<name>[^"]*)"')

ENDS = {
    "app": dict(title="移动端模板", css="app", body="app-body", col=380, device="phone", pages=[
        ("home", "首页", [("来源", "底部主导航首页；其他页面点首页标签回到这里"), ("主操作", "金刚入口进入对应分类；点横幅或商品进入列表；领取礼券后整块收起"),
                         ("返回", "首页是一级页面，没有返回；系统返回退出应用"), ("完成后", "领取礼券后提示已领取；加购后提示已加入购物车，停留在本页")]),
        ("list", "列表", [("来源", "首页入口或底部主导航分类标签"), ("主操作", "搜索、分类、排序与价格筛选；点行展开规格；点图进入商品详情；详情页底部加购"),
                         ("返回", "详情页返回列表并保留筛选与滚动位置"), ("完成后", "加购后提示并更新购物车数；筛选无结果显示空态，可一键清空条件")]),
        ("orders", "订单", [("来源", "底部主导航订单标签，或我的页订单入口"), ("主操作", "按状态分段切换；点订单进入详情；详情里查看物流、收货与金额，申请售后进入独立填写页"),
                           ("返回", "售后填写页返回订单详情；详情返回订单列表并保留状态分段"), ("完成后", "提交售后后回到订单详情，状态区更新为售后处理中")]),
        ("mine", "我的", [("来源", "底部主导航我的标签"), ("主操作", "点昵称原位改名；地址列表设为默认或进入新建地址页；偏好开关即点即存"),
                         ("返回", "新建地址页返回我的页，未保存时用居中确认框询问"), ("完成后", "保存地址后回到我的页，地址列表出现新地址并提示已保存")]),
        ("agent", "智能体", [("来源", "底部主导航助手标签"), ("主操作", "输入问题或点建议问法；回答按流式输出，可停止；涉及改动时出现审批确认卡"),
                           ("返回", "历史会话页返回当前对话；排队中的提问显示排队标签，可撤回"), ("完成后", "回答结束保留产物文件卡；审批通过后任务状态行更新结果")]),
    ]),
    "web": dict(title="网页后台模板", css="web", body="web-body", col=520, cols={"BTN": 420, "CARD": 430, "MOTN": 430, "FEED": 460}, device="desktop", pages=[
        ("home", "工作台", [("来源", "左侧主导航工作台，登录后默认进入"), ("主操作", "看核心指标与趋势；切换图表周期；待处理事项进入对应列表"),
                          ("返回", "工作台是一级页面，没有返回"), ("完成后", "处理待办后事项从列表消失，指标随之更新")]),
        ("list", "列表", [("来源", "左侧主导航列表；工作台待办跳入时带筛选"), ("主操作", "状态分段、表头筛选与排序；勾选后批量操作；点行右侧出现关联详情；新建进入独立填写页"),
                         ("返回", "新建填写页返回列表并保留筛选与页码"), ("完成后", "保存后回到列表，新记录在首行并提示已保存；删除前居中确认")]),
        ("orders", "订单", [("来源", "左侧主导航订单"), ("主操作", "状态分段与导出；行内展开看明细；点订单号进入独立详情"),
                           ("返回", "详情返回订单列表并保留状态与页码"), ("完成后", "导出完成提示文件已生成；改状态后行内状态标签即时更新")]),
        ("mine", "我的", [("来源", "左侧主导航底部我的"), ("主操作", "资料原位改名；偏好开关即点即存；修改密码进入独立填写页"),
                         ("返回", "修改密码页返回我的，未保存时居中确认"), ("完成后", "改密后要求重新登录的提示放在确认框里")]),
        ("agent", "智能体", [("来源", "左侧主导航助手"), ("主操作", "输入问题或点建议问法；流式回答可停止；右侧看过程与产物引用；涉及改动时出现审批确认卡"),
                           ("返回", "会话历史切换会话，当前会话内容保留"), ("完成后", "回答结束保留产物结果卡；加载失败显示重试态")]),
    ]),
}


# ---- helpers ------------------------------------------------------------------------------------------------------------------
def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    print(f"written {path.relative_to(ROOT)} ({len(text) // 1024} KB)")


def stash(text: str) -> str:
    """Raw html inside <script type="text/html">: only the end-script sequence needs escaping."""
    return text.replace("</script", "<\\/script")


def embed_path(text: str) -> str:
    """Sources sit four folders below the repo root, the built file three: links into kit/ lose one level."""
    return text.replace("../../../../kit/", "../../kit/")


GOTO = ("<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;"
        "var m=(a.getAttribute('href')||'').match(/^(?:\\.\\/)?([a-z]+)\\.html(?:[#?].*)?$/);if(m){e.preventDefault();parent.postMessage({lz:'goto',page:m[1]},'*');}});</script>")


def page_for_bundle(text: str) -> str:
    text = embed_path(text)
    return text.replace("</body>", GOTO + "\n</body>", 1)


def split_part(text: str):
    m = re.match(r"\s*<!--\s*cat:\s*([A-Z]{3,4})\s*\|\s*(.+?)\s*-->", text)
    if not m:
        raise ValueError("a part must start with <!-- cat: CODE | 标题 -->")
    code, title = m.group(1), m.group(2)
    body = text[m.end():]
    styles = re.findall(r"<style>.*?</style>", body, re.S)
    scripts = re.findall(r"<script>.*?</script>", body, re.S)
    for block in styles + scripts:
        body = body.replace(block, "")
    return code, title, body.strip(), styles, scripts


def components_html(end: str) -> str:
    cfg = ENDS[end]
    shell = read(HERE / "components.shell.tpl")
    sections, pills, styles, scripts, seen = [], [], [], [], {}
    total = 0
    for path in sorted((T / end / "source" / "parts").glob("*.part")):
        code, title, body, st, sc = split_part(read(path))
        ids = CID.findall(body)
        prefix = "AP" if end == "app" else "WB"
        for i in ids:
            if i in seen:
                raise SystemExit(f"duplicate {i}: {path.name} and {seen[i]}")
            if not i.startswith(f"{prefix}-{code}-"):
                raise SystemExit(f"{path.name}: ids must start with {prefix}-{code}-: {i}")
            seen[i] = path.name
        total += len(ids)
        col = cfg.get("cols", {}).get(code)
        style = f' style="--col: {col}px"' if col else ""
        sections.append(f'<section class="cat" id="cat-{code.lower()}" data-cat="{code}"{style}>\n<div class="cat__head"><h2>{title}</h2><span>{len(ids)} 个组件</span></div>\n<div class="gallery">\n{body}\n</div>\n</section>')
        pills.append((code, title, len(ids)))
        styles += st
        scripts += sc
    pill_html = f'<button class="pill" data-cat="all" aria-pressed="true">全部 <small>{total}</small></button>' + "".join(
        f'<button class="pill" data-cat="{c}" aria-pressed="false">{t} <small>{n}</small></button>' for c, t, n in pills)
    out = (shell.replace("@TITLE@", cfg["title"] + "组件库").replace("@END_CSS@", cfg["css"]).replace("@BODY_CLASS@", cfg["body"]).replace("@COL@", str(cfg["col"]))
           .replace("@PILLS@", pill_html).replace("@PARTS@", "\n".join(sections)).replace("@PART_STYLES@", "\n".join(styles)).replace("@PART_SCRIPTS@", "\n".join(scripts)))
    return out


def ids_of(path: Path) -> list[dict]:
    found, seen = [], set()
    for m in TAG_NAME.finditer(read(path)):
        if m.group("id") not in seen and "-NAV-" not in m.group("id"):
            seen.add(m.group("id"))
            found.append({"id": m.group("id"), "name": m.group("name")})
    return found


def shell_config(key: str, tabs: list[str], **extra) -> dict:
    return {"key": key, "theme": tokens.DEFAULT, "tabs": tabs, "presets": [{"id": p["id"], "name": p["name"], "action": p["action"]} for p in tokens.presets()],
            "effects": [{"id": i, "name": n} for i, n in EFFECTS], **extra}


def render_shell(title: str, tabs: list[tuple[str, str]], panels: str, sources: dict[str, str], config: dict) -> str:
    shell = read(HERE / "bundle.shell.tpl")
    if config.get("workbench"):
        shell = shell.replace('<html lang="zh-CN"', '<html lang="zh-CN" data-ui-workbench', 1)
        shell = shell.replace('data-bg="glow"', 'data-theme="navy" data-bg="none"', 1)
    one = len(tabs) == 1
    tab_html = "".join(f'<button class="tabs__item" data-tab="{i}" aria-selected="false">{n}</button>' for i, n in tabs)
    source_html = "\n".join(f'<script type="text/html" id="src-{k}">{stash(v)}</script>' for k, v in sources.items())
    shell = shell.replace('<nav class="tabs" id="tabs"', '<nav class="tabs" id="tabs"' + (' hidden' if one else ''))
    return (shell.replace("@TITLE@", title).replace("@TABS@", tab_html).replace("@PANELS@", panels).replace("@SOURCES@", source_html)
            .replace("@CONFIG@", json.dumps(config, ensure_ascii=False)))


# ---- app and web -------------------------------------------------------------------------------------------------------------
def bundle_end(end: str) -> str:
    cfg = ENDS[end]
    pages, sources = [], {"components": embed_path(components_html(end))}
    for pid, name, logic in cfg["pages"]:
        path = T / end / "source" / "pages" / f"{pid}.html"
        sources[f"page-{pid}"] = page_for_bundle(read(path))
        pages.append({"id": pid, "name": name, "logic": logic, "ids": ids_of(path)})
    panels = (f'<section class="panel" id="panel-pages"><div class="wb"><aside class="wb__side"><nav class="nav" id="nav" aria-label="完整页面"></nav></aside>'
              f'<div class="wb__stage"><div class="frame frame--{cfg["device"]}" id="frame"></div></div><aside class="wb__info" id="info"></aside></div></section>\n'
              f'<section class="panel" id="panel-components"><div class="host" data-src="components" data-label="组件库"></div></section>')
    config = shell_config(end, ["pages", "components"], theme="navy", background="none",
                          workbench="pages", device=cfg["device"], pages=pages)
    return render_shell(cfg["title"], [("pages", "整页模板"), ("components", "组件库")], panels, sources, config)


def build_end(end: str) -> None:
    write(T / end / f"{end}.html", bundle_end(end))


# ---- poster ------------------------------------------------------------------------------------------------------------------
def poster_items() -> list[dict]:
    items = []
    for p in sorted((T / "poster" / "source" / "templates").glob("PS-*.html")):
        head = read(p)
        m = re.search(r"<[^>]*\bdata-cid=\"(PS-\d{3})\"[^>]*>", head)
        attrs = m.group(0) if m else ""
        get = lambda k: (re.search(k + r'="([^"]*)"', attrs) or [None, ""])[1]
        size = get("data-size")
        w, h = (re.findall(r"\d+", size.split("（")[0])[:2] + ["1080", "1440"])[:2]
        items.append({"id": m.group(1) if m else p.name[:6], "name": get("data-name"), "use": get("data-use"), "size": size, "w": int(w), "h": int(h),
                      "file": "source/templates/" + p.name})
    return items


def bundle_poster() -> str:
    items = poster_items()
    wall = embed_path(read(HERE / "poster.wall.tpl")).replace("@ITEMS@", json.dumps(items, ensure_ascii=False))
    viewer_dir = T / "poster" / "source" / "prompts"
    viewer = embed_path(read(viewer_dir / "viewer.html"))
    for js in re.findall(r'<script src="([^"]+\.js)"></script>', viewer):
        if (viewer_dir / js).is_file():
            viewer = viewer.replace(f'<script src="{js}"></script>', "<script>" + embed_path(read(viewer_dir / js)).replace("</script", "<\\/script") + "</script>")
    panels = ('<section class="panel" id="panel-wall"><div class="host" data-src="wall" data-label="海报模板"></div></section>\n'
              '<section class="panel" id="panel-prompts"><div class="host" data-src="prompts" data-label="提示词库"></div></section>')
    config = shell_config("poster", ["wall", "prompts"])
    return render_shell("海报模板", [("wall", "海报模板"), ("prompts", "提示词库")], panels, {"wall": wall, "prompts": viewer}, config)


def build_poster() -> None:
    write(T / "poster" / "poster.html", bundle_poster())


def bundle_documents(types: list[dict]) -> str:
    page = read(HERE / "documents.page.tpl").replace("@DATA@", "window.LZ_DOCS = " + json.dumps({"types": types}, ensure_ascii=False) + ";")
    panels = '<section class="panel" id="panel-docs"><div class="host" data-src="docs" data-label="文件模板"></div></section>'
    return render_shell("文件模板", [("docs", "文件模板")], panels, {"docs": page}, shell_config("documents", ["docs"]))


def write_documents(types: list[dict]) -> None:
    write(T / "documents" / "documents.html", bundle_documents(types))


def build_documents() -> None:
    import build_documents_index
    if build_documents_index.build():
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", nargs="?", default="all", choices=["app", "web", "poster", "documents", "all"])
    args = ap.parse_args()
    if args.what in ("app", "all"):
        build_end("app")
    if args.what in ("web", "all"):
        build_end("web")
    if args.what in ("poster", "all"):
        build_poster()
    if args.what in ("documents", "all"):
        build_documents()
    return 0


if __name__ == "__main__":
    sys.exit(main())
