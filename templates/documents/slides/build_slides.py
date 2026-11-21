"""由描述文件生成 16:9 幻灯片。先读规则卡：py -X utf8 scripts/context.py slides

    py -X utf8 build_slides.py specs/DC-SL-001-工作汇报.json samples/DC-SL-001-工作汇报.pptx
    py -X utf8 build_slides.py --all                  把 specs 里每个模板生成到 samples
    py -X utf8 build_slides.py spec.json out.pptx --theme green --strict

描述文件（JSON）：{"id","name","theme","title","slides":[{"layout": ...}]}。版式：
    cover 封面  section 章节页  bullets 要点页  two-column 双栏对比  image-text 图文页
    table 表格页  chart 图表页  quote 引言页  end 结束页  steps 流程页  stats 数据页
字段见 README.md。默认从 Luz-Design 的参考主题生成色值，可用 --tokens 指定 CSS 令牌。
字阶按规则卡：封面与大标题 40 磅，页标题 28 磅，正文 20 磅，图表与标注 18 磅，不用其他字号。
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import math
import re
import sys
import uuid
from pathlib import Path

from lxml import etree
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
DESIGN = HERE.parents[2]
SHARED = DESIGN / "kit"

FONT = "微软雅黑"
SLIDE_W, SLIDE_H = 12192000, 6858000          # 13.333 x 7.5 英寸
W_IN, H_IN = SLIDE_W / 914400, SLIDE_H / 914400
M = 0.75                                      # 页边距：不少于画面宽度 5%（0.667 英寸）
CW = W_IN - 2 * M                             # 版心宽
Y0, Y1 = 1.9, 6.3                             # 内容区上下界；页码在 Y1 之下
TITLE_PT, PAGE_PT, BODY_PT, NOTE_PT = 40, 28, 20, 18
LH = 1.32                                     # 微软雅黑单倍行高与字号之比
GAP = 0.3
PAGE_Y = 6.45                                 # 页码框上沿；框底 6.85 不超过下边距
RADIUS = 0.22                                 # 卡片圆角（英寸）

LAYOUTS = ["cover", "section", "bullets", "two-column", "image-text", "table", "chart", "quote", "end", "steps", "stats"]

PHOTO_ALT = {
    "bouquet-rose": "粉色玫瑰花束", "bouquet-tulip": "黄色郁金香花束", "bouquet-white": "白色洋桔梗花束",
    "scene-hero-pink": "粉色背景前的花束", "bg-floral": "粉色芍药与洋牡丹", "bg-green": "虚化的绿色枝叶",
    "product-rose-red": "红玫瑰花束", "product-peony-pink": "粉芍药花束", "product-sunflower": "向日葵花束",
    "product-tulip-white": "白郁金香", "product-hydrangea-blue": "蓝绣球盆栽", "product-monstera": "龟背竹盆栽",
    "product-succulent": "多肉组合盆", "product-pampas-vase": "干花花瓶摆件", "product-giftbox": "花礼盒",
}

warnings: list[str] = []
errors: list[str] = []


# ------------------------------------------------------------------ 颜色

def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def rgb_hex(rgb) -> str:
    return "%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def mix(a: str, b: str, t: float) -> str:
    """a 与 b 按 t 混合（t 为 b 的占比）。"""
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def color(value: str) -> RGBColor:
    return RGBColor.from_string(value.lstrip("#").upper())


def opaque_hex(value: str) -> str:
    if not re.fullmatch(r"#(?:[0-9a-f]{3}|[0-9a-f]{6})", value, re.I):
        raise ValueError(value)
    digits = value[1:].upper()
    return "".join(digit * 2 for digit in digits) if len(digits) == 3 else digits


def load_tokens(path: Path | None, theme: str) -> dict[str, str]:
    if path is None:
        sys.path.insert(0, str(DESIGN / "scripts"))
        from sync_template_tokens import render

        text = render(application=False)
        if theme == "orange":
            theme = "amber"
    else:
        if not path.is_file():
            sys.exit(f"找不到令牌文件 {path}")
        text = path.read_text(encoding="utf-8")
    base: dict[str, str] = {}
    themed: dict[str, dict[str, str]] = {}
    for match in re.finditer(r'(:root|\[data-theme="(\w+)"\])\s*\{(.*?)\}', text, re.S):
        values = {k: v.strip() for k, v in re.findall(r"--([\w-]+):\s*([^;]+);", match.group(3))}
        if match.group(1) == ":root":
            base.update(values)
        else:
            themed[match.group(2)] = values
    if theme not in themed:
        sys.exit(f"主题 {theme} 不存在，可选：{'、'.join(themed)}")
    merged = {**base, **themed[theme]}
    need = ["bg", "surface", "ink", "ink-2", "ink-3", "action", "action-press", "action-tint", "action-edge",
            "accent", "accent-tint", "price", "success", "success-tint", "danger", "danger-tint"]
    palette = {}
    for key in need:
        value = merged.get(key, "")
        try:
            # The shared tokens derive opaque slide colors from one named sRGB
            # color and a literal hex background. PPTX stores the resulting RGB.
            derived = re.fullmatch(r"color-mix\(in srgb,\s*var\(--([\w-]+)\)\s+(\d+(?:\.\d+)?)%,\s*(#[0-9a-f]+)\)", value, re.I)
            if derived:
                name, share, background = derived.groups()
                rgb = mix(opaque_hex(merged.get(name, "")), opaque_hex(background), 1 - float(share) / 100)
            else:
                rgb = opaque_hex(value)
        except ValueError:
            sys.exit(f"令牌 --{key} 缺少可用于幻灯片的不透明色值：{value!r}")
        palette[key.replace("-", "_")] = rgb
    palette["line"] = mix(palette["surface"], palette["ink"], 0.12)
    palette["neutral"] = mix(palette["surface"], palette["ink"], 0.07)
    return palette


# ------------------------------------------------------------------ 文字测量

_FONTS: dict[bool, ImageFont.FreeTypeFont | None] = {}


def _font(bold: bool):
    if bold not in _FONTS:
        _FONTS[bold] = None
        for name in (("msyhbd.ttc", "msyh.ttc") if bold else ("msyh.ttc",)):
            for folder in ("C:/Windows/Fonts", "/usr/share/fonts", "/Library/Fonts"):
                candidate = Path(folder) / name
                if candidate.is_file():
                    try:
                        _FONTS[bold] = ImageFont.truetype(str(candidate), 200)
                        break
                    except OSError:
                        pass
            if _FONTS[bold]:
                break
    return _FONTS[bold]


def text_width(text: str, pt: float, bold: bool = False) -> float:
    """文字宽度（英寸）。有微软雅黑字体文件时按实际字形量，没有时按汉字一个字宽、西文 0.55 估算。"""
    font = _font(bold)
    if font:
        return font.getlength(text) * pt / 200 / 72
    return sum(pt * (1.0 if ord(c) > 0x2E80 else 0.55) for c in text) / 72


NO_LINE_START = set("，。、；：！？）》」』】,.;:!?)%")


def wrap_lines(text: str, pt: float, width: float, bold: bool = False) -> int:
    """按宽度逐字折行得到行数（行首不放标点）。"""
    lines, current = 1, ""
    for ch in text:
        if text_width(current + ch, pt, bold) > width and current and ch not in NO_LINE_START:
            lines += 1
            current = ch
        else:
            current += ch
    return lines


def block_height(items: list[str], pt: float, width: float, space_after: float, bold: bool = False) -> float:
    """若干段文字的总高度（英寸）。"""
    total = 0.0
    for i, item in enumerate(items):
        total += wrap_lines(item, pt, width, bold) * pt * LH / 72
        if i < len(items) - 1:
            total += space_after / 72
    return total


# ------------------------------------------------------------------ 底层写入

def E(inches: float) -> Emu:
    return Emu(int(round(inches * 914400)))


def sub(parent, tag: str, **attrs):
    el = etree.SubElement(parent, qn(tag))
    for key, value in attrs.items():
        el.set(key, str(value))
    return el


def style_run(run, pt: float, hexcolor: str, bold: bool = False) -> None:
    font = run.font
    font.size = Pt(pt)
    font.bold = bold
    font.name = FONT
    font.color.rgb = color(hexcolor)
    rpr = run._r.get_or_add_rPr()
    rpr.set("lang", "zh-CN")
    latin = rpr.find(qn("a:latin"))
    for tag in ("a:ea", "a:cs"):
        old = rpr.find(qn(tag))
        if old is not None:
            rpr.remove(old)
    ea = etree.Element(qn("a:ea"))
    ea.set("typeface", FONT)
    cs = etree.Element(qn("a:cs"))
    cs.set("typeface", FONT)
    latin.addnext(ea)
    ea.addnext(cs)


def para_bullet(paragraph, hexcolor: str, pt: float) -> None:
    """项目符号：实心圆点，主色，随字号缩放；悬挂缩进让折行与首行对齐。"""
    ppr = paragraph._p.get_or_add_pPr()
    indent = int(0.34 * 914400)
    ppr.set("marL", str(indent))
    ppr.set("indent", str(-indent))
    clr = sub(ppr, "a:buClr")
    sub(clr, "a:srgbClr", val=hexcolor)
    sub(ppr, "a:buSzPct", val=60000)
    sub(ppr, "a:buFont", typeface=FONT)
    sub(ppr, "a:buChar", char="●")


def add_text(slide, x, y, w, h, paras, *, name: str, anchor: str = "top", inset=(0, 0, 0, 0)):
    """paras: [{"runs": [(文字, 磅, 色, 粗体)], "align", "after", "bullet"}]"""
    box = slide.shapes.add_textbox(E(x), E(y), E(w), E(h))
    box.name = name
    frame = box.text_frame
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.margin_left, frame.margin_top, frame.margin_right, frame.margin_bottom = (E(v) for v in inset)
    frame.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
    for i, para in enumerate(paras):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        paragraph.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[para.get("align", "left")]
        paragraph.line_spacing = 1.0
        if para.get("after"):
            paragraph.space_after = Pt(para["after"])
        for text, pt, hexcolor, bold in para["runs"]:
            for k, piece in enumerate(text.split("\n")):
                if k:
                    paragraph.add_line_break()
                run = paragraph.add_run()
                run.text = piece
                style_run(run, pt, hexcolor, bold)
        if para.get("bullet"):
            para_bullet(paragraph, para["bullet"], para["runs"][0][1])
    return box


def shape(slide, kind: str, x, y, w, h, fill: str | None, *, line: str | None = None, line_w: float = 0.75,
          radius: float | None = None, shadow: bool = False, name: str = "形状"):
    kinds = {"rect": MSO_SHAPE.RECTANGLE, "round": MSO_SHAPE.ROUNDED_RECTANGLE, "oval": MSO_SHAPE.OVAL}
    item = slide.shapes.add_shape(kinds[kind], E(x), E(y), E(w), E(h))
    item.name = name
    style = item._element.find(qn("p:style"))
    if style is not None:
        item._element.remove(style)               # 去掉主题自带的阴影与线条引用
    if kind == "round":
        item.adjustments[0] = min(0.5, (radius if radius is not None else RADIUS) / min(w, h))
    if fill:
        item.fill.solid()
        item.fill.fore_color.rgb = color(fill)
    else:
        item.fill.background()
    if line:
        item.line.color.rgb = color(line)
        item.line.width = Pt(line_w)
    else:
        item.line.fill.background()
    if shadow:
        sppr = item._element.spPr
        effect = sub(sppr, "a:effectLst")
        shd = sub(effect, "a:outerShdw", blurRad=190500, dist=38100, dir=5400000, algn="t", rotWithShape=0)
        clr = sub(shd, "a:srgbClr", val="4A2C38")
        sub(clr, "a:alpha", val=9000)
    # 形状里不放文字；清掉自带的空文本框属性以免被当成空标题
    return item


def card(slide, P, x, y, w, h, *, fill: str | None = None, name: str = "卡片"):
    return shape(slide, "round", x, y, w, h, fill or P["surface"], line=P["line"], radius=RADIUS, shadow=True, name=name)


def chip(slide, P, x, y, text: str, *, fill: str, ink: str, pt: float = BODY_PT, h: float = 0.52, name: str = "标签"):
    w = text_width(text, pt, True) + 0.5
    shape(slide, "round", x, y, w, h, fill, radius=h / 2, name=name + "底")
    add_text(slide, x, y, w, h, [{"runs": [(text, pt, ink, True)], "align": "center"}], name=name, anchor="middle")
    return w


def photo(slide, key: str, x, y, w, h, *, alt: str, radius: float = RADIUS, focus=(0.5, 0.5), kind: str = "round",
          name: str = "图片"):
    """裁成目标比例的实拍图，圆角；webp 转成 pptx 能读的格式。"""
    path = resolve_asset(key)
    image = Image.open(path)
    has_alpha = image.mode in ("RGBA", "LA", "P") and "transparency" in image.info or image.mode == "RGBA"
    image = image.convert("RGBA" if has_alpha else "RGB")
    iw, ih = image.size
    target = w / h
    if iw / ih > target:
        new_w = ih * target
        left = min(max(focus[0] * iw - new_w / 2, 0), iw - new_w)
        box = (left, 0, left + new_w, ih)
    else:
        new_h = iw / target
        top = min(max(focus[1] * ih - new_h / 2, 0), ih - new_h)
        box = (0, top, iw, top + new_h)
    image = image.crop(tuple(int(round(v)) for v in box))
    limit = max(int(w * 220), 200)
    if image.size[0] > limit:
        image = image.resize((limit, int(limit * image.size[1] / image.size[0])), Image.LANCZOS)
    buffer = io.BytesIO()
    if has_alpha:
        image.save(buffer, "PNG", optimize=True)
    else:
        image.save(buffer, "JPEG", quality=90, optimize=True)
    buffer.seek(0)
    pic = slide.shapes.add_picture(buffer, E(x), E(y), E(w), E(h))
    pic.name = name
    pic._element.nvPicPr.cNvPr.set("descr", alt)
    geom = pic._element.spPr.find(qn("a:prstGeom"))
    if kind == "oval":
        geom.set("prst", "ellipse")
    elif radius:
        geom.set("prst", "roundRect")
        av = geom.find(qn("a:avLst"))
        if av is None:
            av = sub(geom, "a:avLst")
        sub(av, "a:gd", name="adj", fmla=f"val {int(min(0.5, radius / min(w, h)) * 100000)}")
    return pic


def resolve_asset(key: str) -> Path:
    name = key if "/" in key else f"photo/{key}"
    path = SHARED / "assets" / (name if Path(name).suffix else name + ".webp")
    if not path.is_file():
        errors.append(f"找不到素材 {key}（{path}）")
        raise FileNotFoundError(path)
    return path


def alt_for(key: str, given: str | None) -> str:
    if given:
        return given
    base = key.split("/")[-1].rsplit(".", 1)[0]
    if base not in PHOTO_ALT:
        warnings.append(f"素材 {key} 没有替代文字，请在描述里写 alt")
    return PHOTO_ALT.get(base, "花卉实拍")


# ------------------------------------------------------------------ 母版与版式

def patch_theme(prs, P) -> None:
    part = prs.slide_master.part.part_related_by(RT.THEME)
    root = etree.fromstring(part.blob)
    a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    scheme = root.find(f".//{a}clrScheme")
    scheme.set("name", "花间集")
    colors = {"dk1": P["ink"], "lt1": P["surface"], "dk2": P["ink_2"], "lt2": P["bg"], "accent1": P["action"],
              "accent2": P["accent"], "accent3": P["action_press"], "accent4": P["success"], "accent5": P["ink_3"],
              "accent6": P["danger"], "hlink": P["action_press"], "folHlink": P["ink_3"]}
    for key, value in colors.items():
        slot = scheme.find(f"{a}{key}")
        for child in list(slot):
            slot.remove(child)
        etree.SubElement(slot, f"{a}srgbClr").set("val", value)
    fonts = root.find(f".//{a}fontScheme")
    fonts.set("name", "微软雅黑")
    for group in ("majorFont", "minorFont"):
        node = fonts.find(f"{a}{group}")
        node.find(f"{a}latin").set("typeface", FONT)
        for tag in ("ea", "cs"):
            item = node.find(f"{a}{tag}")
            item.set("typeface", FONT if tag == "ea" else "")
        for extra in node.findall(f"{a}font"):
            node.remove(extra)
    part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def set_pos(shape_, x, y, w, h) -> None:
    shape_.left, shape_.top, shape_.width, shape_.height = E(x), E(y), E(w), E(h)


def patch_master(prs, P) -> None:
    master = prs.slide_master
    csld = master._element.find(qn("p:cSld"))
    old = csld.find(qn("p:bg"))
    if old is not None:
        csld.remove(old)
    bg = etree.Element(qn("p:bg"))
    pr = sub(bg, "p:bgPr")
    fill = sub(pr, "a:solidFill")
    sub(fill, "a:schemeClr", val="bg2")
    sub(pr, "a:effectLst")
    csld.insert(0, bg)
    for ph in list(master.placeholders):
        kind = ph.placeholder_format.type
        name = str(kind)
        if "DATE" in name or "FOOTER" in name:
            ph._element.getparent().remove(ph._element)
        elif "SLIDE_NUMBER" in name:
            set_pos(ph, W_IN - M - 1.5, PAGE_Y, 1.5, 0.4)
        elif "TITLE" in name:
            set_pos(ph, M, 0.95, CW, 0.7)
        else:
            set_pos(ph, M, Y0, CW, Y1 - Y0)
    tx = master._element.find(qn("p:txStyles"))
    title = tx.find(qn("p:titleStyle")).find(qn("a:lvl1pPr"))
    title.set("algn", "l")
    rpr = title.find(qn("a:defRPr"))
    rpr.set("sz", str(PAGE_PT * 100))
    rpr.set("b", "1")
    for lvl, size in zip(range(1, 6), (BODY_PT, BODY_PT, NOTE_PT, NOTE_PT, NOTE_PT)):
        node = tx.find(qn("p:bodyStyle")).find(qn(f"a:lvl{lvl}pPr"))
        if node is not None:
            node.find(qn("a:defRPr")).set("sz", str(size * 100))


def patch_layouts(prs) -> dict[str, object]:
    wanted = {"Title Slide": "封面", "Title and Content": "标题与内容", "Section Header": "章节页", "Title Only": "仅标题"}
    for layout in list(prs.slide_layouts):
        if layout.name not in wanted:
            prs.slide_layouts.remove(layout)
    found = {}
    for layout in prs.slide_layouts:
        label = wanted[layout.name]
        layout.name = label
        found[label] = layout
        for ph in list(layout.placeholders):
            name = str(ph.placeholder_format.type)
            if "DATE" in name or "FOOTER" in name:
                ph._element.getparent().remove(ph._element)
            elif "SLIDE_NUMBER" in name:
                set_pos(ph, W_IN - M - 1.5, PAGE_Y, 1.5, 0.4)
            elif label == "封面" and "SUBTITLE" in name:
                ph._element.getparent().remove(ph._element)
            elif label == "封面":
                set_pos(ph, M, 3.2, 5.9, 0.9)
            elif label == "章节页" and "BODY" in name:
                ph._element.getparent().remove(ph._element)
            elif label == "章节页":
                set_pos(ph, M, 3.55, 5.9, 0.9)
            elif label == "标题与内容" and "OBJECT" in name:
                set_pos(ph, M, Y0, CW, Y1 - Y0)
            elif "TITLE" in name:
                set_pos(ph, M, 0.95, CW, 0.7)
    return found


# ------------------------------------------------------------------ 页面公共部分

class Deck:
    def __init__(self, spec: dict, P: dict[str, str]):
        self.spec = spec
        self.P = P
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Emu(SLIDE_W), Emu(SLIDE_H)
        patch_theme(self.prs, P)
        patch_master(self.prs, P)
        self.layouts = patch_layouts(self.prs)
        props = self.prs.core_properties
        props.title = spec.get("title") or spec.get("name", "")
        props.author = ""
        props.last_modified_by = ""
        props.comments = ""
        props.language = "zh-CN"
        props.subject = ""
        props.keywords = ""
        self.titles: dict[str, int] = {}
        now = datetime.datetime.now().replace(microsecond=0)
        props.created = props.modified = now
        props.revision = 1
        package = self.prs.part.package
        for rid, rel in list(package._rels.items()):
            if rel.reltype.endswith("/thumbnail"):
                package._rels.pop(rid)

    # 标题占位符：每页标题写在版式的标题占位符里
    def new_slide(self, layout: str, title: str, *, x=M, y=0.95, w=CW, h=0.7, pt=PAGE_PT, anchor="top", index: int = 0):
        slide = self.prs.slides.add_slide(self.layouts[layout])
        for ph in list(slide.placeholders):
            if ph.placeholder_format.type is not None and "TITLE" not in str(ph.placeholder_format.type):
                ph._element.getparent().remove(ph._element)
        holder = slide.shapes.title
        holder.name = "页标题"
        set_pos(holder, x, y, w, h)
        frame = holder.text_frame
        frame.word_wrap = True
        frame.auto_size = MSO_AUTO_SIZE.NONE
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        frame.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
        paragraph = frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.LEFT
        run = paragraph.add_run()
        run.text = title
        style_run(run, pt, self.P["ink"], True)
        if text_width(title, pt, True) > w:
            warnings.append(f"第 {index} 页标题将换行，请在放映时检查文本框高度和内容间距：{title}")
        if title in self.titles:
            warnings.append(f"第 {index} 页标题与第 {self.titles[title]} 页重复：{title}")
        self.titles.setdefault(title, index)
        return slide

    def header_bar(self, slide) -> None:
        shape(slide, "round", M, 0.78, 0.55, 0.07, self.P["action"], radius=0.035, name="标题引线")

    def page_number(self, slide, number: int) -> None:
        box = slide.shapes.add_textbox(E(W_IN - M - 1.5), E(PAGE_Y), E(1.5), E(0.4))
        # 换成真正的页码占位符，随页序自动更新
        sp = box._element
        nv = sp.find(qn("p:nvSpPr"))
        nv.find(qn("p:cNvPr")).set("name", "页码")
        nv.find(qn("p:cNvSpPr")).attrib.pop("txBox", None)
        lock = etree.SubElement(nv.find(qn("p:cNvSpPr")), qn("a:spLocks"))
        lock.set("noGrp", "1")
        ph = etree.SubElement(nv.find(qn("p:nvPr")), qn("p:ph"))
        ph.set("type", "sldNum")
        ph.set("sz", "quarter")
        ph.set("idx", "12")
        body = sp.find(qn("p:txBody"))
        for child in list(body):
            if child.tag == qn("a:p"):
                body.remove(child)
        body_pr = body.find(qn("a:bodyPr"))
        for key in list(body_pr.attrib):
            del body_pr.attrib[key]
        for child in list(body_pr):
            body_pr.remove(child)
        body_pr.set("lIns", "0"), body_pr.set("rIns", "0"), body_pr.set("tIns", "0"), body_pr.set("bIns", "0")
        body_pr.set("anchor", "ctr")
        para = etree.SubElement(body, qn("a:p"))
        ppr = sub(para, "a:pPr", algn="r")
        fld = sub(para, "a:fld", id="{%s}" % str(uuid.uuid4()).upper(), type="slidenum")
        rpr = sub(fld, "a:rPr", lang="zh-CN", sz=NOTE_PT * 100, b="0")
        fill = sub(rpr, "a:solidFill")
        sub(fill, "a:srgbClr", val=self.P["ink_3"])
        sub(rpr, "a:latin", typeface=FONT)
        sub(rpr, "a:ea", typeface=FONT)
        sub(rpr, "a:cs", typeface=FONT)
        text = etree.SubElement(fld, qn("a:t"))
        text.text = str(number)

    def finish(self, slide, number: int, *, bar: bool = True) -> None:
        if bar:
            self.header_bar(slide)
        self.page_number(slide, number)

    # ------------------------------------------------------------ 各版式

    def build(self, item: dict, number: int):
        layout = item.get("layout")
        if layout not in LAYOUTS:
            errors.append(f"第 {number} 页版式 {layout!r} 不存在，可选：{'、'.join(LAYOUTS)}")
            return
        title = item.get("title", "")
        if not title:
            errors.append(f"第 {number} 页缺少标题")
            return
        getattr(self, "layout_" + layout.replace("-", "_"))(item, title, number)

    def bullet_metrics(self, items, width, avail, pref=26):
        """要点之间的间距取不超过 pref 且能放进 avail 的最大值，返回（间距磅数，总高度英寸）。"""
        after = pref
        while after > 8 and block_height(items, BODY_PT, width - 0.34, after) > avail:
            after -= 2
        return after, block_height(items, BODY_PT, width - 0.34, after)

    def bullets_block(self, slide, x, y, w, items, *, after=14, name="要点"):
        paras = [{"runs": [(text, BODY_PT, self.P["ink"], False)], "after": after, "bullet": self.P["action"]} for text in items]
        height = block_height(items, BODY_PT, w - 0.34, after)
        add_text(slide, x, y, w, height + 0.1, paras, name=name)
        return height

    def layout_cover(self, item, title, number):
        slide = self.new_slide("封面", title, x=M, y=3.2, w=5.9, h=0.9, pt=TITLE_PT, anchor="top", index=number)
        shape(slide, "round", M, 3.0, 0.9, 0.08, self.P["action"], radius=0.04, name="标题引线")
        key = item.get("image", "scene-hero-pink")
        photo(slide, key, 7.0, 0.75, W_IN - M - 7.0, 6.0, alt=alt_for(key, item.get("alt")), radius=0.3,
              focus=tuple(item.get("focus", (0.5, 0.5))), name="封面图")

    def layout_section(self, item, title, number):
        top = 2.45
        slide = self.new_slide("章节页", title, x=M, y=top + 1.1, w=5.9, h=0.9, pt=TITLE_PT, index=number)
        badge = item.get("number", f"{number:02d}")
        shape(slide, "round", M, top, 0.9, 0.9, self.P["action"], radius=0.22, name="章节序号底")
        add_text(slide, M, top, 0.9, 0.9, [{"runs": [(badge, PAGE_PT, "FFFFFF", True)], "align": "center"}],
                 name="章节序号", anchor="middle")
        if item.get("line"):
            if wrap_lines(item["line"], BODY_PT, 5.9) > 2:
                warnings.append(f"第 {number} 页章节说明超过两行")
            add_text(slide, M, top + 2.2, 5.9, 0.9, [{"runs": [(item["line"], BODY_PT, self.P["ink_2"], False)]}], name="章节说明")
        key = item.get("image", "bg-floral")
        photo(slide, key, 7.0, 0.75, W_IN - M - 7.0, Y1 - 0.75, alt=alt_for(key, item.get("alt")), radius=0.3,
              focus=tuple(item.get("focus", (0.5, 0.5))), name="章节图")
        self.page_number(slide, number)

    def stat_card(self, slide, x, y, w, h, stat: dict, *, name="重点数据"):
        """图标、名称、数字三层，居中对齐；名称在上，数字在下。"""
        P = self.P
        card(slide, P, x, y, w, h, fill=P["action_tint"], name=name + "底")
        label = stat.get("label", "")
        value, unit = str(stat.get("value", "")), stat.get("unit", "")
        icon_h = 0.95 if stat.get("icon") else 0
        label_h = wrap_lines(label, BODY_PT, w - 0.6) * BODY_PT * LH / 72
        value_h = TITLE_PT * LH / 72
        total = icon_h + (0.2 if icon_h else 0) + label_h + 0.1 + value_h
        top = y + (h - total) / 2
        if stat.get("icon"):
            key = f"icons/3d/{stat['icon']}"
            photo(slide, key, x + w / 2 - icon_h / 2, top, icon_h, icon_h, alt=stat.get("icon_alt") or PHOTO_ALT.get(stat["icon"], f"{label}图标"),
                  radius=0, name="数据图标")
            top += icon_h + 0.2
        add_text(slide, x + 0.3, top, w - 0.6, label_h + 0.05, [{"runs": [(label, BODY_PT, P["ink_2"], False)], "align": "center"}],
                 name=name + "名称")
        runs = [(value, TITLE_PT, P["action_press"], True)]
        if unit:
            runs.append((" " + unit, BODY_PT, P["action_press"], True))
        add_text(slide, x + 0.2, top + label_h + 0.1, w - 0.4, value_h, [{"runs": runs, "align": "center"}], name=name + "数字", anchor="middle")
        return slide

    def numbered_rows(self, slide, x, y, w, h, points):
        """有先后顺序的要点：序号圆加一行文字，行与行均分卡片高度。"""
        P = self.P
        row = min(0.95, (h - 0.6) / len(points))
        top = y + (h - row * len(points)) / 2
        for i, text in enumerate(points):
            cy = top + i * row
            shape(slide, "oval", x, cy + (row - 0.58) / 2, 0.58, 0.58, P["action_tint"], line=P["action_edge"], name=f"序号{i + 1}底")
            add_text(slide, x, cy + (row - 0.58) / 2, 0.58, 0.58, [{"runs": [(str(i + 1), BODY_PT, P["action_press"], True)], "align": "center"}],
                     name=f"序号{i + 1}", anchor="middle")
            add_text(slide, x + 0.85, cy, w - 0.85, row, [{"runs": [(text, BODY_PT, P["ink"], False)]}], name=f"要点{i + 1}", anchor="middle")
            if text_width(text, BODY_PT) > w - 0.85:
                warnings.append(f"序号要点放不进一行：{text}")

    def layout_bullets(self, item, title, number):
        P = self.P
        slide = self.new_slide("仅标题", title, index=number)
        points = item.get("points", [])
        if not 1 <= len(points) <= 6:
            errors.append(f"第 {number} 页要点 {len(points)} 条，须在 1 至 6 条")
        stat, key = item.get("stat"), item.get("image")
        h = Y1 - Y0
        card_w = 7.6 if (stat or key) else CW
        text_w = card_w - 1.0
        after, height = self.bullet_metrics(points, text_w, h - 0.9)
        if height > h - 0.9:
            warnings.append(f"第 {number} 页要点区超高，请缩短要点")
        card(slide, P, M, Y0, card_w, h, name="要点卡")
        if item.get("numbered"):
            self.numbered_rows(slide, M + 0.5, Y0, text_w, h, points)
        else:
            self.bullets_block(slide, M + 0.5, Y0 + (h - height) / 2, text_w, points, after=after)
        right_x, right_w = M + card_w + 0.35, CW - card_w - 0.35
        if stat:
            self.stat_card(slide, right_x, Y0, right_w, h, stat)
        elif key:
            photo(slide, key, right_x, Y0, right_w, h, alt=alt_for(key, item.get("alt")),
                  focus=tuple(item.get("focus", (0.5, 0.5))), name="配图")
        self.finish(slide, number)

    def column_card(self, slide, x, y, w, h, head: str, points, *, tone: str, top: float, after: int, number: int, name: str):
        P = self.P
        card(slide, P, x, y, w, h, name=name + "卡")
        fill, ink = (P["neutral"], P["ink_2"]) if tone == "neutral" else (P["action_edge"], P["action_press"])
        chip_w = chip(slide, P, x + 0.45, top, head, fill=fill, ink=ink, name=name + "标签")
        if chip_w > w - 0.9:
            warnings.append(f"第 {number} 页「{head}」标签超出卡片")
        self.bullets_block(slide, x + 0.45, top + 0.52 + 0.4, w - 0.9, points, after=after, name=name + "要点")

    def layout_two_column(self, item, title, number):
        slide = self.new_slide("仅标题", title, index=number)
        left, right = item.get("left", {}), item.get("right", {})
        w = (CW - GAP) / 2
        h = Y1 - Y0
        for side in (left, right):
            if not 1 <= len(side.get("points", [])) <= 5:
                errors.append(f"第 {number} 页每栏要点须在 1 至 5 条")
        avail = h - 0.92 - 0.9
        after = min(self.bullet_metrics(side.get("points", []), w - 0.9, avail, 22)[0] for side in (left, right))
        tallest = max(block_height(side.get("points", []), BODY_PT, w - 0.9 - 0.34, after) for side in (left, right))
        if tallest > avail:
            warnings.append(f"第 {number} 页栏内要点超高，请缩短")
        top = Y0 + (h - (0.92 + tallest)) / 2
        self.column_card(slide, M, Y0, w, h, left.get("head", ""), left.get("points", []), tone="neutral", top=top, after=after, number=number, name="左栏")
        self.column_card(slide, M + w + GAP, Y0, w, h, right.get("head", ""), right.get("points", []), tone="action", top=top, after=after, number=number, name="右栏")
        self.finish(slide, number)

    def layout_image_text(self, item, title, number):
        P = self.P
        slide = self.new_slide("仅标题", title, index=number)
        side = item.get("side", "left")
        img_w, text_w = 5.7, CW - 5.7 - GAP
        h = Y1 - Y0
        points = item.get("points", [])
        if not 1 <= len(points) <= 4:
            errors.append(f"第 {number} 页图文页要点须在 1 至 4 条")
        img_x = M if side == "left" else M + text_w + GAP
        txt_x = M + img_w + GAP if side == "left" else M
        key = item.get("image", "bouquet-rose")
        photo(slide, key, img_x, Y0, img_w, h, alt=alt_for(key, item.get("alt")), focus=tuple(item.get("focus", (0.5, 0.5))), name="配图")
        if item.get("badge"):
            width = text_width(item["badge"], BODY_PT, True) + 0.6
            shape(slide, "round", img_x + 0.3, Y0 + h - 0.3 - 0.58, width, 0.58, P["surface"], radius=0.29, name="角标底")
            add_text(slide, img_x + 0.3, Y0 + h - 0.3 - 0.58, width, 0.58,
                     [{"runs": [(item["badge"], BODY_PT, P["price"], True)], "align": "center"}], name="角标", anchor="middle")
        after, height = self.bullet_metrics(points, text_w - 0.9, h - 0.92 - 0.9, 24)
        if height > h - 0.92 - 0.9:
            warnings.append(f"第 {number} 页图文页文字超高")
        card(slide, P, txt_x, Y0, text_w, h, name="文字卡")
        top = Y0 + (h - (0.92 + height)) / 2
        chip(slide, P, txt_x + 0.45, top, item.get("head", ""), fill=P["action_edge"], ink=P["action_press"], name="图文标签")
        self.bullets_block(slide, txt_x + 0.45, top + 0.92, text_w - 0.9, points, after=after)
        self.finish(slide, number)

    def layout_table(self, item, title, number):
        P = self.P
        slide = self.new_slide("仅标题", title, index=number)
        columns, rows = item.get("columns", []), item.get("rows", [])
        if not 2 <= len(columns) <= 5:
            errors.append(f"第 {number} 页表格列数须在 2 至 5 列")
        if not 1 <= len(rows) <= 6:
            errors.append(f"第 {number} 页表格行数须在 1 至 6 行")
        weights = [c.get("width", 1) for c in columns]
        inner_w = CW - 0.6
        widths = [inner_w * wgt / sum(weights) for wgt in weights]
        row_h = min(0.8, (Y1 - Y0 - 0.6) / (len(rows) + 1))
        table_h = row_h * (len(rows) + 1)
        card_h = table_h + 0.6
        y = Y0 + (Y1 - Y0 - card_h) / 2
        card(slide, P, M, y, CW, card_h, name="表格卡")
        frame = slide.shapes.add_table(len(rows) + 1, len(columns), E(M + 0.3), E(y + 0.3), E(inner_w), E(table_h))
        frame.name = "数据表"
        table = frame.table
        table.first_row = True
        table.horz_banding = False
        tbl_pr = table._tbl.tblPr
        for child in list(tbl_pr):
            tbl_pr.remove(child)                  # 去掉内置表格样式，逐格写明
        for i, wd in enumerate(widths):
            table.columns[i].width = E(wd)
        for r in range(len(rows) + 1):
            table.rows[r].height = E(row_h)
        aligns = [c.get("align", "left" if i == 0 else "center") for i, c in enumerate(columns)]
        for r in range(len(rows) + 1):
            for c in range(len(columns)):
                text = columns[c]["text"] if r == 0 else str(rows[r - 1][c])
                self.fill_cell(table.cell(r, c), text, header=(r == 0), align="center" if r == 0 else aligns[c],
                               last=(r == len(rows)), width=widths[c], where=number)
        frame._element.nvGraphicFramePr.cNvPr.set("descr", item.get("alt") or f"{title}的数据表")
        self.finish(slide, number)

    def fill_cell(self, cell, text, *, header, align, last, width, where):
        P = self.P
        cell.margin_left = cell.margin_right = E(0.14)
        cell.margin_top = cell.margin_bottom = E(0.05)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        frame = cell.text_frame
        frame.word_wrap = True
        paragraph = frame.paragraphs[0]
        paragraph.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        run = paragraph.add_run()
        run.text = text
        style_run(run, BODY_PT, P["ink"], header)
        if text_width(text, BODY_PT, header) > width - 0.28:
            warnings.append(f"第 {where} 页表格单元格放不进一行：{text}")
        tcpr = cell._tc.get_or_add_tcPr()
        for child in list(tcpr):
            tcpr.remove(child)

        def border(tag, hexcolor, pt):
            ln = sub(tcpr, tag, w=int(pt * 12700), cap="flat", cmpd="sng", algn="ctr")
            if hexcolor:
                fill = sub(ln, "a:solidFill")
                sub(fill, "a:srgbClr", val=hexcolor)
                sub(ln, "a:prstDash", val="solid")
            else:
                sub(ln, "a:noFill")
        border("a:lnL", None, 0)
        border("a:lnR", None, 0)
        border("a:lnT", None, 0)
        border("a:lnB", None if last else P["line"], 0.75)
        fill = sub(tcpr, "a:solidFill")
        sub(fill, "a:srgbClr", val=P["action_edge"] if header else P["surface"])

    def series_colors(self, count: int) -> list[str]:
        base = self.P["action"]
        ramp = [base, mix(base, "FFFFFF", 0.55), mix(base, "FFFFFF", 0.3), mix(base, "FFFFFF", 0.75), mix(base, "FFFFFF", 0.42)]
        return ramp[:count]

    def layout_chart(self, item, title, number):
        P = self.P
        slide = self.new_slide("仅标题", title, index=number)
        spec = item.get("chart", {})
        kind = spec.get("type", "column")
        stat = item.get("stat")
        h = Y1 - Y0
        chart_w = 7.7 if stat else CW
        card(slide, P, M, Y0, chart_w, h, name="图表卡")
        caption = spec.get("caption", "")
        if caption:
            add_text(slide, M + 0.4, Y0 + 0.25, chart_w - 0.8, 0.4, [{"runs": [(caption, NOTE_PT, P["ink_3"], False)]}], name="图表标注")
        top = Y0 + (0.8 if caption else 0.3)
        gx, gy, gw, gh = M + 0.3, top, chart_w - 0.6, Y0 + h - 0.25 - top
        data = CategoryChartData()
        data.categories = spec["categories"]
        series = spec["series"]
        fmt = spec.get("number_format", "General")
        for s in series:
            data.add_series(s["name"], s["values"], number_format=fmt)
        types = {"column": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED,
                 "line": XL_CHART_TYPE.LINE_MARKERS, "doughnut": XL_CHART_TYPE.DOUGHNUT, "pie": XL_CHART_TYPE.PIE}
        if kind not in types:
            errors.append(f"第 {number} 页图表类型 {kind} 不存在，可选：{'、'.join(types)}")
            return
        if len(series) > (1 if kind in ("doughnut", "pie") else 3):
            errors.append(f"第 {number} 页图表系列过多")
        frame = slide.shapes.add_chart(types[kind], E(gx), E(gy), E(gw), E(gh), data)
        frame.name = "图表"
        frame._element.nvGraphicFramePr.cNvPr.set("descr", spec.get("alt") or f"{caption or title}的图表")
        chart = frame.chart
        chart.has_title = False
        chart.font.size = Pt(NOTE_PT)
        chart.font.name = FONT
        chart.font.color.rgb = color(P["ink_2"])
        colors = self.series_colors(len(series))
        if kind in ("doughnut", "pie"):
            self.style_ring(chart, spec, colors_for_points(self, len(spec["categories"])), kind, (gw, gh))
        else:
            plot = chart.plots[0]
            plot.has_data_labels = True
            labels = plot.data_labels
            labels.font.size = Pt(NOTE_PT)
            labels.font.name = FONT
            labels.font.color.rgb = color(P["ink"])
            labels.number_format = fmt
            labels.number_format_is_linked = False
            labels.position = XL_LABEL_POSITION.OUTSIDE_END if kind in ("column", "bar") else XL_LABEL_POSITION.ABOVE
            plot.vary_by_categories = False
            value_axis, category_axis = chart.value_axis, chart.category_axis
            value_axis.visible = False
            value_axis.tick_label_position = XL_TICK_LABEL_POSITION.NONE
            value_axis.major_tick_mark = XL_TICK_MARK.NONE
            value_axis.format.line.fill.background()
            value_axis.has_major_gridlines = False
            if spec.get("max"):
                value_axis.maximum_scale = spec["max"]
            value_axis.minimum_scale = spec.get("min", 0)
            category_axis.tick_labels.font.size = Pt(NOTE_PT)
            category_axis.tick_labels.font.name = FONT
            category_axis.format.line.color.rgb = color(P["line"])
            category_axis.has_major_gridlines = False
            if kind == "bar":
                category_axis.reverse_order = True
            if kind in ("column", "bar"):
                plot.gap_width = 55
                plot.overlap = -8 if len(series) > 1 else 0
            for ser, hexcolor in zip(plot.series, colors):
                if kind == "line":
                    ser.smooth = False
                    ser.format.line.color.rgb = color(hexcolor)
                    ser.format.line.width = Pt(3)
                    ser.marker.style = XL_MARKER_STYLE.CIRCLE
                    ser.marker.size = 10
                    ser.marker.format.fill.solid()
                    ser.marker.format.fill.fore_color.rgb = color(hexcolor)
                    ser.marker.format.line.color.rgb = color(P["surface"])
                else:
                    ser.format.fill.solid()
                    ser.format.fill.fore_color.rgb = color(hexcolor)
                    ser.invert_if_negative = False
            if len(series) > 1:
                chart.has_legend = True
                chart.legend.position = XL_LEGEND_POSITION.TOP
                chart.legend.include_in_layout = False
                chart.legend.font.size = Pt(NOTE_PT)
                chart.legend.font.name = FONT
            else:
                chart.has_legend = False
        if stat:
            self.stat_card(slide, M + chart_w + 0.35, Y0, CW - chart_w - 0.35, h, stat, name="图表结论")
        self.finish(slide, number)

    def style_ring(self, chart, spec, point_colors, kind, frame_size):
        P = self.P
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.RIGHT
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(NOTE_PT)
        chart.legend.font.name = FONT
        plot = chart.plots[0]
        plot.vary_by_categories = True
        series = plot.series[0]
        n = len(spec["categories"])
        for i in range(n):
            point = series.points[i]
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = color(point_colors[i])
            point.format.line.color.rgb = color(P["surface"])
            point.format.line.width = Pt(2)
        ser = series._element
        for old in ser.findall(qn("c:dLbls")):
            ser.remove(old)
        dlbls = etree.Element(qn("c:dLbls"))
        for i in range(n):
            dark = luminance(point_colors[i]) < 0.28
            dl = sub(dlbls, "c:dLbl")
            sub(dl, "c:idx", val=i)
            sub(dl, "c:numFmt", formatCode="0%", sourceLinked=0)
            sub(sub(dl, "c:spPr"), "a:noFill")
            tx = sub(dl, "c:txPr")
            sub(tx, "a:bodyPr")
            sub(tx, "a:lstStyle")
            p = sub(tx, "a:p")
            ppr = sub(p, "a:pPr")
            rpr = sub(ppr, "a:defRPr", sz=NOTE_PT * 100, b=1)
            sub(sub(rpr, "a:solidFill"), "a:srgbClr", val="FFFFFF" if dark else P["ink"])
            sub(rpr, "a:latin", typeface=FONT)
            sub(rpr, "a:ea", typeface=FONT)
            sub(p, "a:endParaRPr", lang="zh-CN")
            for tag, val in (("showLegendKey", 0), ("showVal", 0), ("showCatName", 0), ("showSerName", 0), ("showPercent", 1), ("showBubbleSize", 0)):
                sub(dl, "c:" + tag, val=val)
        sub(dlbls, "c:numFmt", formatCode="0%", sourceLinked=0)
        for tag, val in (("showLegendKey", 0), ("showVal", 0), ("showCatName", 0), ("showSerName", 0), ("showPercent", 1), ("showBubbleSize", 0), ("showLeaderLines", 0)):
            sub(dlbls, "c:" + tag, val=val)
        ser_cat = ser.find(qn("c:cat"))
        ser_cat.addprevious(dlbls)
        if kind == "doughnut":
            hole = chart._chartSpace.xpath(".//c:holeSize")
            if hole:
                hole[0].set("val", "58")
        # 圆环居左、图例居右，按图表框尺寸手写布局，避免各软件自动排版不一致
        gw, gh = frame_size
        side = min(gh, gw * 0.5)
        plot_area = chart._chartSpace.xpath(".//c:plotArea")[0]
        old = plot_area.find(qn("c:layout"))
        if old is not None:
            plot_area.remove(old)
        layout = etree.Element(qn("c:layout"))
        manual = sub(layout, "c:manualLayout")
        for tag, val in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"), ("x", 0.02), ("y", (gh - side) / 2 / gh),
                         ("w", side / gw), ("h", side / gh)):
            sub(manual, "c:" + tag, val=val)
        plot_area.insert(0, layout)
        legend = chart._chartSpace.xpath(".//c:legend")[0]
        old = legend.find(qn("c:layout"))
        if old is not None:
            legend.remove(old)
        layout = etree.Element(qn("c:layout"))
        manual = sub(layout, "c:manualLayout")
        for tag, val in (("xMode", "edge"), ("yMode", "edge"), ("x", side / gw + 0.1), ("y", 0.25), ("w", 0.98 - side / gw - 0.1), ("h", 0.5)):
            sub(manual, "c:" + tag, val=val)
        legend.find(qn("c:legendPos")).addnext(layout)

    def layout_quote(self, item, title, number):
        P = self.P
        slide = self.new_slide("章节页", title, x=M, y=0.95, w=CW, h=0.7, pt=PAGE_PT, index=number)
        quote = item.get("quote", "")
        h = Y1 - Y0
        key = item.get("image")
        card_w = 7.7 if key else CW
        card(slide, P, M, Y0, card_w, h, name="引言卡")
        text_w = card_w - 1.4
        if "\n" not in quote:
            lines = wrap_lines(quote, TITLE_PT, text_w, True)
            if lines > 1:
                size = math.ceil(len(quote) / lines)
                quote = "\n".join(quote[i:i + size] for i in range(0, len(quote), size))
        n_lines = quote.count("\n") + 1
        if n_lines > 3 or any(text_width(part, TITLE_PT, True) > text_w for part in quote.split("\n")):
            warnings.append(f"第 {number} 页引言放不下，请缩短")
        q_h = n_lines * TITLE_PT * LH / 72
        who_h = 0.8
        who_y = Y0 + h - 0.4 - who_h
        area_top, area_bottom = Y0 + 0.4, who_y - 0.2
        q_y = area_top + (area_bottom - area_top - q_h) / 2
        shape(slide, "round", M + 0.5, q_y + 0.08, 0.09, q_h - 0.16, P["action"], radius=0.045, name="引言竖线")
        add_text(slide, M + 0.85, q_y, text_w, q_h + 0.05, [{"runs": [(quote, TITLE_PT, P["ink"], True)]}], name="引言")
        mark = item.get("mark", "marks/mark-003")
        shape(slide, "oval", M + 0.5, who_y, who_h, who_h, P["action_tint"], name="头像底")
        photo(slide, mark, M + 0.5 + 0.12, who_y + 0.12, 0.56, 0.56, alt=item.get("mark_alt", "顾客标识"), radius=0, kind="oval", name="头像")
        add_text(slide, M + 1.55, who_y, text_w - 0.7, who_h,
                 [{"runs": [(item.get("who", ""), BODY_PT, P["ink"], True)]},
                  {"runs": [(item.get("role", ""), BODY_PT, P["ink_2"], False)]}], name="出处", anchor="middle")
        if key:
            photo(slide, key, M + card_w + GAP, Y0, CW - card_w - GAP, h, alt=alt_for(key, item.get("alt")),
                  focus=tuple(item.get("focus", (0.5, 0.5))), name="配图")
        self.finish(slide, number)

    def layout_end(self, item, title, number):
        P = self.P
        points = item.get("points", [])
        if not 0 <= len(points) <= 3:
            errors.append(f"第 {number} 页结束页要点最多 3 条")
        text_x, text_w = 6.35, W_IN - M - 6.35
        after, height = self.bullet_metrics(points, text_w, 2.2, 14) if points else (14, 0)
        group = 0.08 + 0.2 + 0.9 + (0.35 + height if points else 0)
        top = 0.75 + (Y1 - 0.75 - group) / 2
        slide = self.new_slide("章节页", title, x=text_x, y=top + 0.28, w=text_w, h=0.9, pt=TITLE_PT, index=number)
        shape(slide, "round", text_x, top, 0.9, 0.08, P["action"], radius=0.04, name="标题引线")
        key = item.get("image", "bouquet-white")
        photo(slide, key, M, 0.75, 5.2, Y1 - 0.75, alt=alt_for(key, item.get("alt")), radius=0.3,
              focus=tuple(item.get("focus", (0.5, 0.5))), name="结束页图")
        if points:
            self.bullets_block(slide, text_x, top + 0.28 + 0.9 + 0.35, text_w, points, after=after)
        self.page_number(slide, number)

    def layout_steps(self, item, title, number):
        P = self.P
        slide = self.new_slide("仅标题", title, index=number)
        steps = item.get("steps", [])
        n = len(steps)
        if not 3 <= n <= 5:
            errors.append(f"第 {number} 页流程须 3 至 5 步")
            return
        w = (CW - GAP * (n - 1)) / n
        inner = w - 0.6
        heads = [s["head"] for s in steps]
        texts = [s.get("text", "") for s in steps]
        head_h = max(wrap_lines(t, BODY_PT, inner, True) for t in heads) * BODY_PT * LH / 72
        text_h = max(wrap_lines(t, BODY_PT, inner) for t in texts) * BODY_PT * LH / 72
        card_h = max(2.4, 0.45 + head_h + 0.2 + text_h + 0.45)
        if card_h > 3.1:
            warnings.append(f"第 {number} 页流程卡超高，请缩短步骤文字")
        top = Y0 + 0.05
        block = 0.62 + 0.4 + card_h
        top = Y0 + (Y1 - Y0 - block) / 2
        card_y = top + 0.62 + 0.4
        shape(slide, "rect", M + 0.31, top + 0.28, (n - 1) * (w + GAP), 0.05, P["action_edge"], name="流程线")
        for i, s in enumerate(steps):
            x = M + i * (w + GAP)
            shape(slide, "oval", x, top, 0.62, 0.62, P["action"], name=f"步骤{i + 1}底")
            add_text(slide, x, top, 0.62, 0.62, [{"runs": [(str(i + 1), BODY_PT, "FFFFFF", True)], "align": "center"}],
                     name=f"步骤{i + 1}序号", anchor="middle")
            card(slide, P, x, card_y, w, card_h, name=f"步骤{i + 1}卡")
            gy = card_y + (card_h - (head_h + 0.2 + text_h)) / 2
            add_text(slide, x + 0.3, gy, inner, head_h + 0.05, [{"runs": [(s["head"], BODY_PT, P["ink"], True)]}], name=f"步骤{i + 1}名称")
            add_text(slide, x + 0.3, gy + head_h + 0.2, inner, text_h + 0.1, [{"runs": [(s.get("text", ""), BODY_PT, P["ink_2"], False)]}],
                     name=f"步骤{i + 1}说明")
        self.finish(slide, number)

    def layout_stats(self, item, title, number):
        P = self.P
        slide = self.new_slide("仅标题", title, index=number)
        items = item.get("items", [])
        n = len(items)
        if not 2 <= n <= 4:
            errors.append(f"第 {number} 页数据页须 2 至 4 项")
            return
        w = (CW - GAP * (n - 1)) / n
        icon, label_h, value_h, chip_h = 0.9, BODY_PT * LH / 72, 0.75, 0.46
        has_delta = any(s.get("delta") for s in items)
        group = icon + 0.2 + label_h + 0.1 + value_h + ((0.2 + chip_h) if has_delta else 0)
        h = min(group + 1.1, Y1 - Y0)
        y = Y0 + (Y1 - Y0 - h) / 2
        tones = {"up": (P["success"], P["success_tint"]), "down": (P["danger"], P["danger_tint"]), "flat": (P["ink_2"], P["neutral"])}
        for i, s in enumerate(items):
            x = M + i * (w + GAP)
            card(slide, P, x, y, w, h, name=f"数据{i + 1}卡")
            top = y + (h - group) / 2
            if s.get("icon"):
                photo(slide, f"icons/3d/{s['icon']}", x + w / 2 - icon / 2, top, icon, icon,
                      alt=s.get("icon_alt") or PHOTO_ALT.get(s["icon"], f"{s['label']}图标"), radius=0, name=f"数据{i + 1}图标")
            label_y = top + icon + 0.2
            add_text(slide, x + 0.2, label_y, w - 0.4, label_h + 0.05, [{"runs": [(s["label"], BODY_PT, P["ink_2"], False)], "align": "center"}], name=f"数据{i + 1}名称")
            runs = [(str(s["value"]), TITLE_PT, P["action_press"], True)]
            if s.get("unit"):
                runs.append((" " + s["unit"], BODY_PT, P["action_press"], True))
            if text_width(str(s["value"]), TITLE_PT, True) + text_width(" " + s.get("unit", ""), BODY_PT, True) > w - 0.2:
                warnings.append(f"第 {number} 页数据「{s['label']}」放不进卡片宽度")
            add_text(slide, x + 0.1, label_y + label_h + 0.1, w - 0.2, value_h, [{"runs": runs, "align": "center"}], name=f"数据{i + 1}数字", anchor="middle")
            if s.get("delta"):
                ink, tint = tones.get(s.get("tone", "flat"), tones["flat"])
                cw = text_width(s["delta"], NOTE_PT, True) + 0.5
                chip(slide, P, x + (w - cw) / 2, label_y + label_h + 0.1 + value_h + 0.2, s["delta"], fill=tint, ink=ink, pt=NOTE_PT, h=chip_h, name=f"数据{i + 1}变化")
        self.finish(slide, number)

    def save(self, out: Path) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(out))


def luminance(hexcolor: str) -> float:
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hex_rgb(hexcolor)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def colors_for_points(deck: Deck, count: int) -> list[str]:
    base = deck.P["action"]
    steps = [0, 0.38, 0.62, 0.8, 0.9]
    return [mix(base, "FFFFFF", steps[i]) for i in range(count)]


# ------------------------------------------------------------------ 入口

def build(spec_path: Path, out: Path, theme: str | None, tokens: Path | None) -> bool:
    warnings.clear()
    errors.clear()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if "layout" in spec and "slides" not in spec:          # 可复用块：一个版式片段，生成单页预览
        spec = {"name": spec.get("name", spec_path.stem), "theme": spec.get("theme", "rose"), "slides": [spec]}
    theme = theme or spec.get("theme", "rose")
    P = load_tokens(tokens, theme)
    deck = Deck(spec, P)
    slides = spec.get("slides", [])
    if not 1 <= len(slides) <= 12:
        warnings.append(f"共 {len(slides)} 页，基础模板建议 8 至 12 页")
    if len(slides) > 1 and slides[0].get("layout") != "cover":
        warnings.append("第一页不是封面")
    for number, item in enumerate(slides, 1):
        try:
            deck.build(item, number)
        except FileNotFoundError:
            continue
    if not errors:
        deck.save(out)
    label = spec.get("name", spec_path.stem)
    print(f"{label}：{len(slides)} 页，主题 {theme} -> {out}")
    for text in warnings:
        print("  提醒", text)
    for text in errors:
        print("  错误", text)
    return not errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="由描述文件生成 16:9 幻灯片")
    parser.add_argument("spec", nargs="?", type=Path)
    parser.add_argument("out", nargs="?", type=Path)
    parser.add_argument("--all", action="store_true", help="把 specs 里每个模板生成到 samples")
    parser.add_argument("--theme", help="覆盖描述文件里的主题")
    parser.add_argument("--tokens", type=Path, help="使用指定的 CSS 令牌文件")
    parser.add_argument("--strict", action="store_true", help="提醒也算失败")
    args = parser.parse_args(argv)
    jobs: list[tuple[Path, Path]] = []
    if args.all:
        for spec in sorted((HERE / "specs").glob("DC-SL-*.json")):
            jobs.append((spec, HERE / "samples" / (spec.stem + ".pptx")))
    elif args.spec and args.out:
        jobs.append((args.spec, args.out))
    else:
        parser.error("需要 spec 与 out，或使用 --all")
    ok = True
    for spec, out in jobs:
        passed = build(spec, out, args.theme, args.tokens)
        ok = ok and passed and not (args.strict and warnings)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
