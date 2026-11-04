"""小程序模板（mini）的生成器插件：scripts/build_prototype.py 通过 ``build(spec, ctx)`` 取到要嵌进共用外壳的各段。

约定见 references/prototype-templates/engine/ENGINE.md 第十一节。这里只有机制：手机框、状态栏、导航栏、标签栏、状态页和头部背景；
没有任何行业内容，行业内容在规格与内容模块里。
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
TABS_KEY = "tabbar"
DARK_MODE = "tokens"
DEFAULT_MARK = "<rect x='9' y='4.5' width='14' height='23' rx='3.5'/><path d='M14 23.5h4'/>"

PAGE_TYPES = {"tab", "sub", "sheet", "result"}
PAGE_KEYS = {
    "id", "name", "type", "tab", "roles", "scenes", "links", "logic", "base", "baseArg", "offline",
    "title", "nav", "light", "headerBg", "tabbar", "noBack", "scroll", "maskClose", "blocks", "header", "footer", "custom", "args", "layout", "empty",
}


def check(spec: dict, ctx) -> list[str]:
    """mini 自己的规格检查：页面类型、页面有内容、只有一级页能画标签栏、弹层页不要导航栏相关字段。"""
    out: list[str] = []
    for p in spec["pages"]:
        pid = p["id"]
        if p.get("type") not in PAGE_TYPES:
            out.append(f"页面「{pid}」的类型「{p.get('type')}」不对，mini 只有 {'、'.join(sorted(PAGE_TYPES))}")
        if not p.get("blocks") and not p.get("custom"):
            out.append(f"页面「{pid}」没有内容：blocks 和 custom 至少写一个")
        if p.get("type") == "sheet" and (p.get("nav") or p.get("headerBg")):
            out.append(f"警告：弹层页「{pid}」写了 nav / headerBg，弹层不画导航栏和头部背景，会被忽略")
        if p.get("type") != "tab" and p.get("tabbar") is True:
            out.append(f"页面「{pid}」不是一级页，二级页不显示标签栏（去掉 tabbar 字段）")
        unknown = sorted(set(p) - PAGE_KEYS)
        if unknown:
            out.append(f"警告：页面「{pid}」有 mini 不认识的字段：{'、'.join(unknown)}（拼写对吗？）")
        for area in ("blocks", "header", "footer"):
            for i, it in enumerate(p.get(area) or []):
                if not isinstance(it, dict) or not any(k in it for k in ("cid", "custom", "gap", "heading")):
                    out.append(f"页面「{pid}」{area}[{i}] 要写 cid（组件编号）、custom（内容模块里的渲染函数）、gap（间距）或 heading（小标题）之一")
    for i, t in enumerate(spec.get("tabbar", [])):
        if not t.get("icon"):
            out.append(f"tabbar[{i}]「{t.get('name')}」没写 icon（LIB.LINE 里的线性图标名）")
    return out


def build(spec: dict, ctx) -> dict:
    d = {"width": 390, "height": 800}
    d.update(spec.get("device") or {})
    stage = (HERE / "stage.html").read_text(encoding="utf-8")
    stage = stage.replace('id="ptPhone"', f'id="ptPhone" style="width:{int(d["width"])}px;height:{int(d["height"])}px"')
    return {
        "css": (HERE / "mini.css").read_text(encoding="utf-8"),
        "js": (HERE / "mini.js").read_text(encoding="utf-8"),
        "stage_html": stage,
        "cids": [],
    }
