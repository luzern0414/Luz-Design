#!/usr/bin/env python3
"""Check a delivered HTML, XLSX, DOCX, PPTX, or Markdown file against rules/file-design.html.

The checks follow the problem families in references/design-standards.html (删除测试 and 问题的同类判断), not a fixed
word list. The patterns still catch only common wordings, so a clean run is necessary, not sufficient:
the deletion test must be applied to every visible element by hand as well.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# (pattern, family, short_only). short_only patterns fire only in short blocks (<= 80 characters), where
# metadata lines live, so the same words quoted inside long body text are not reported.
FAMILY_PATTERNS = [
    (r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?Z?", "timestamp", True),
    (r"(?:生成|更新|修改|编制|导出|发布)(?:于|时间|日期)|最后(?:更新|修改)|由.{1,12}(?:生成|整理|撰写|编制|制作)|"
     r"版本[号:：]|编制人|制表人|审核人|作者[:：]|阅读(?:时长|时间)|字数[:：]|智能生成|人工智能生成|提示词|"
     r"Generated|Last updated|Created by|Powered by|Author:", "production metadata", False),
    (r"数据来源|信息来源|来源[:：]|去重来源|来源(?:统计|数量|索引|目录)|\d+\s*个(?:来源|官方页面|网页|链接)|官方页面|"
     r"采集(?:日期|时间|状态|范围)|证据(?:部分|状态|等级)|部分获取|(?:资料|信息|来源|数据|内容|事实)(?:已核验|核验通过|校验通过|已校验)|哈希|SHA-?256|"
     r"以官方(?:信息|公告)?为准|信息可能(?:不完整|有误|存在)|免责声明", "source metadata", False),
    (r"(?<![A-Za-z])raw/|单页\s*HTML|单页总结|本文件|[A-Za-z]:\\\S+|输出目录|源文件目录", "file metadata", False),
    (r"Design reference|设计参考|Luz Design|Admin SPEC|参考.{0,8}(?:规范|主题)(?:设计|制作)|"
     r"基于.{1,10}(?:主题|模板)(?:生成|制作)?|遵循.{1,12}规范", "design declaration", True),
    (r"本(?:报告|文档|文章|文|页面|页|节|章|表|图|部分|幻灯片|演示)(?:将|主要|旨在|用于|展示|介绍|列出|汇总|总结|说明|包含|分为|梳理)|"
     r"以下(?:是|为|内容|表格|列出|几点)|如下(?:表|图)?所示|如上所述|下面我们|我们来看|综上所述|总结一下|总而言之",
     "self-reference", False),
    (r"请注意|点击(?:展开|查看|这里|下方|此处)|向下滚动|阅读指南|使用方法[:：]|建议先(?:阅读|看)|详见下[页文]|"
     r"返回顶部|回到顶部", "reading guidance", False),
    (r"仅供参考|仅(?:作|为)示意|以实际为准|如需.{0,12}请|下一步(?:建议|计划|行动)|后续(?:可以|建议|可考虑)|可根据实际情况|建议(?:您|你|后续|进一步)|"
     r"欢迎(?:反馈|联系|交流|指正)|如有(?:疑问|问题|需要)", "advisory copy", False),
    (r"根据您的(?:要求|需求)|已为您|为您(?:整理|生成|准备|撰写)|希望(?:对您|能)?有(?:所)?帮助|以下为您|^好的[，,。]",
     "chat residue", False),
    (r"\bTODO\b|\bTBD\b|FIXME|lorem ipsum|\bXXX\b", "placeholder", False),
    (r"待补充|待完善|待填写|示例数据|占位文字|（略）|\(略\)", "placeholder", True),
    (r"全网最|最全|史上最|高质量(?:报告|内容|文档)|权威(?:指南|报告)|深度(?:好文|解析)|震撼", "self-evaluation", False),
]
FAMILY_PATTERNS = [(re.compile(p, re.I | re.M), family, short) for p, family, short in FAMILY_PATTERNS]
FAMILIES = sorted({family for _, family, _ in FAMILY_PATTERNS} | {"note", "emoji"})
NOTE_PREFIX = re.compile(r"^\s*(?:说明|注|注意|提示|备注|补充|温馨提示|小贴士|注意事项|建议|Tips?|PS|Note)\s*[:：]", re.I)
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿⭐⭕■-◿]")
# Unrequested accessory sections (file-design.html, 同类问题 for documents and slides).
ACCESSORY_HEADING = re.compile(
    r"^(?:\S{0,4}[、.．]?\s*)?(?:摘要|前言|序言|编写(?:说明|目的)|阅读(?:指南|说明)|使用说明|修订记录|版本(?:信息|记录|历史)|"
    r"更新(?:记录|日志)|免责声明|致谢|术语表|关于本(?:文档|报告|文)|本章小结|小结|参考来源|数据来源|附录说明)$")
FILLER_SLIDE = re.compile(r"^(?:目录|议程|大纲|内容提要|谢谢|感谢|谢谢观看|感谢聆听|问答|答疑|结束|结语|关于我们|附录|Q\s*&\s*A|Thanks?|Agenda)[!！。]*$", re.I)
GRAPHIC_SELECTOR = re.compile(r"svg|\.icon|frame|illustration|\.empty|chart|star|\.kk|\.logo|face|ring|scan", re.I)
DARK_SMALL_SELECTOR = re.compile(r"\.(?:dot|icon|legend|bar|badge|pill|status|progress|chip|tag|logo|corner|coins?|kk|steps|mark|avatar|check|box|ring|scan|cbox|heat|rb)\b|-(?:mark|bar)\b|\.copy i|::?(?:before|after|marker)|svg|button|input", re.I)
# Filled controls in their active state: primary and danger buttons, checked switches and boxes, selected options.
ACTIVE_CONTROL_SELECTOR = re.compile(r"primary|danger|aria-checked=.?true|aria-pressed=.?true|\.on\b|ck-mark", re.I)
ALLOWED: set[str] = set()


def FLOOR_PX() -> float:
    """Reading pages keep 14px; interface prototypes (--allow interface) use the 12px annotation step."""
    return 12.0 if "interface" in ALLOWED else 14.0


# One shared scale for the function list, mini-program and admin of a product deliverable (design-standards.html, 字阶).
INTERFACE_SCALE = {12, 14, 16, 18, 22, 28, 32}
# Websites add the first-screen title steps (website-design.html, 六、视觉基础): 40 on desktop, 48 for a brand home page.
WEBSITE_SCALE = INTERFACE_SCALE | {40, 48}


def luminance(rgb: tuple[int, int, int]) -> float:
    def channel(value: int) -> float:
        v = value / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value[-6:]
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def parse_colors(value: str) -> list[tuple[int, int, int]]:
    colors = []
    for hex_value in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", value):
        if len(hex_value) == 3:
            hex_value = "".join(c * 2 for c in hex_value)
        colors.append(hex_rgb(hex_value))
    for match in re.finditer(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)(?:[ ,/]+([\d.]+%?))?", value):
        alpha = match.group(4)
        if alpha:
            a = float(alpha.rstrip("%")) / (100 if alpha.endswith("%") else 1)
            if a < 0.5:
                continue
        colors.append(tuple(int(match.group(i)) for i in (1, 2, 3)))
    return colors


def check_text(text: str, where: str, errors: list[str]) -> None:
    for pattern, family, short_only in FAMILY_PATTERNS:
        if family in ALLOWED or (short_only and len(text) > 80):
            continue
        match = pattern.search(text)
        if match:
            errors.append(f"{where}: banned {family}: {match.group(0)!r}")
    if "note" not in ALLOWED and NOTE_PREFIX.search(text):
        errors.append(f"{where}: note or advice prefix: {text.strip()[:40]!r}")
    if "emoji" not in ALLOWED and EMOJI.search(text):
        errors.append(f"{where}: emoji or decorative symbol: {EMOJI.search(text).group(0)!r}")


def check_heading(text: str, where: str, errors: list[str]) -> None:
    if "accessory" not in ALLOWED and ACCESSORY_HEADING.match(text.strip()):
        errors.append(f"{where}: unrequested accessory section {text.strip()!r} (pass --allow accessory if the user asked for it)")


# ---------------------------------------------------------------- HTML

class Outline(HTMLParser):
    """Collect visible text blocks in document order with their nearest block tag and ancestors."""

    HIDDEN = {"script", "style", "template", "head", "title", "noscript"}
    VOID = {"br", "img", "meta", "link", "input", "hr", "source", "wbr", "col", "path", "circle", "rect",
            "line", "polyline", "polygon", "ellipse", "use"}
    BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "div", "span", "a", "figcaption",
              "caption", "summary", "dt", "dd", "header", "nav", "aside", "footer", "time", "strong", "em",
              "small", "label", "button", "section", "article", "main", "blockquote", "pre", "code"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.blocks: list[tuple[str, str, tuple[str, ...], bool]] = []
        self.styles: list[str] = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in self.VOID:
            if attrs.get("style"):
                self.styles.append("x{" + attrs["style"] + "}")
            return
        hidden = (
            tag in self.HIDDEN
            or "hidden" in attrs
            or (attrs.get("aria-hidden") or "").lower() == "true"
            or bool(re.search(r"display\s*:\s*none", attrs.get("style") or "", re.I))
        )
        # Verbatim third-party text (captured pages, comments, citations) is marked with data-quoted or <blockquote>.
        quoted = "data-quoted" in attrs or tag in {"blockquote", "q"} or bool(self.stack and self.stack[-1][2])
        self.stack.append((tag, hidden or bool(self.stack and self.stack[-1][1]), quoted))
        if tag == "style":
            self.in_style = True
        if attrs.get("style"):
            self.styles.append("x{" + attrs["style"] + "}")

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
            return
        if not data.strip() or (self.stack and self.stack[-1][1]):
            return
        tag = next((t for t, _, _ in reversed(self.stack) if t in self.BLOCKS), "text")
        quoted = bool(self.stack and self.stack[-1][2])
        self.blocks.append((tag, " ".join(data.split()), tuple(t for t, _, _ in self.stack), quoted))


def is_scrim(value: str) -> bool:
    """A photo scrim: every stop is black or white with alpha, or transparent."""
    stops = re.findall(r"#[0-9a-f]{3,8}\b|rgba?\([^)]*\)|\btransparent\b|var\([^)]*\)", value, re.I)
    return bool(stops) and all(re.fullmatch(r"transparent|rgba\(\s*(?:0\s*,\s*0\s*,\s*0|255\s*,\s*255\s*,\s*255)\s*,[^)]*\)", x.strip(), re.I) for x in stops)


def is_hard_stop(value: str) -> bool:
    """A hard-stop fill such as a slider track: two consecutive stops share one position."""
    positions = re.findall(r"\s(\d+(?:\.\d+)?%|var\([^)]*\))\s*(?=[,)])", value)
    return any(a == b for a, b in zip(positions, positions[1:]))


def check_html(path: Path, errors: list[str], warnings: list[str]) -> None:
    source = path.read_text(encoding="utf-8")
    outline = Outline()
    outline.feed(source)
    blocks = outline.blocks
    if not blocks:
        errors.append("no visible text")
        return
    if blocks[0][0] != "h1":
        errors.append(f"first visible text is not the h1 title: <{blocks[0][0]}> {blocks[0][1][:40]!r}")
    h1_count = len(re.findall(r"<h1[\s>]", source, re.I))
    if h1_count != 1:
        errors.append(f"expected exactly one h1, found {h1_count}")
    tags = [block[0] for block in blocks]
    if "h1" in tags:
        after = tags.index("h1") + 1
        while after < len(tags) and tags[after] == "h1":
            after += 1
        if after < len(tags) and "h2" in tags and tags[after] != "h2":
            errors.append(f"text between the h1 and the first h2: {blocks[after][1][:40]!r}")

    shell_reported: set[str] = set()
    for tag, text, ancestors, quoted in blocks:
        where = f"<{tag}>"
        if not quoted:
            check_text(text, where, errors)
            if tag in {"h2", "h3", "h4"}:
                check_heading(text, where, errors)
        in_content = any(a in {"article", "section"} for a in ancestors)
        shell = next((a for a in ancestors if a in {"nav", "aside"} or (a in {"header", "footer"} and not in_content)), None)
        if shell and "shell" not in ALLOWED and shell not in shell_reported:
            shell_reported.add(shell)
            errors.append(f"application shell <{shell}> in a document: {text[:30]!r}")
    for index, (tag, text, _, _) in enumerate(blocks[:-2]):
        nxt_tag, nxt_text, _, _ = blocks[index + 1]
        if tag in {"h2", "h3"} and nxt_tag == "p" and len(nxt_text) <= 40 and blocks[index + 2][0] in {"table", "th", "td", "li", "h3", "h4", "div"}:
            warnings.append(f"possible explanatory line under heading {text[:20]!r}: {nxt_text!r}")

    css = "\n".join(outline.styles)
    variables = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+)", css))

    def resolve(value: str, depth: int = 0) -> str:
        if depth > 8:
            return value
        return re.sub(r"var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)",
                      lambda m: resolve(variables.get(m.group(1), m.group(2) or ""), depth + 1), value)

    if re.search(r"color-scheme\s*:\s*dark|prefers-color-scheme\s*:\s*dark", css, re.I) and "dark" not in ALLOWED:
        errors.append("dark color scheme declared")
    families: set[str] = set()
    icon_strokes: set[str] = set()
    for rule in re.finditer(r"([^{}]*)\{([^{}]*)\}", css):
        selector, body = rule.group(1).strip(), rule.group(2)
        for decl in re.finditer(r"(?:^|;)\s*font-size\s*:\s*([^;]+)", body, re.I):
            value = resolve(decl.group(1))
            for number, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(px|rem|em|pt)\b", value, re.I):
                if float(number) * {"px": 1, "rem": 16, "em": 16, "pt": 4 / 3}[unit.lower()] < FLOOR_PX():
                    errors.append(f"font size below {FLOOR_PX():g}px in {selector[:40]!r}: {decl.group(1).strip()}")
                elif "interface" in ALLOWED and unit.lower() == "px" and "calc" not in value and float(number) not in (WEBSITE_SCALE if "website" in ALLOWED else INTERFACE_SCALE):
                    errors.append(f"font size off the product type scale 12/14/16/18/22/28/32 in {selector[:40]!r}: {decl.group(1).strip()}")
        if "interface" in ALLOWED and re.search(r"drawer|side-?panel|slide-?over", selector, re.I) and not re.search(r"menu|nav", selector, re.I):
            # Details and forms float in the centre; only navigation may slide in from the side (design-standards.html, 浮层与反馈).
            errors.append(f"side drawer for content in {selector[:40]!r}: use a centred floating panel")
        if "interface" in ALLOWED:
            # Product deliverables use two weights only and no tracking (design-standards.html, 字体).
            for decl in re.finditer(r"(?:^|;)\s*font-weight\s*:\s*([^;]+)", body, re.I):
                if decl.group(1).strip().lower() not in {"400", "600", "normal", "inherit"}:
                    errors.append(f"font weight outside 400/600 in {selector[:40]!r}: {decl.group(1).strip()}")
            for decl in re.finditer(r"(?:^|;)\s*letter-spacing\s*:\s*([^;]+)", body, re.I):
                if decl.group(1).strip().lower() not in {"0", "normal", "0px", "inherit"}:
                    errors.append(f"letter spacing in {selector[:40]!r}: {decl.group(1).strip()}")
        if re.search(r"(?:^|;)\s*font-style\s*:\s*(?:italic|oblique)", body, re.I):
            errors.append(f"italic text in {selector[:40]!r}: Chinese has no true italic")
        for decl in re.finditer(r"(?:^|;)\s*font\s*:\s*([^;]+)", body, re.I):
            size = re.search(r"(\d+(?:\.\d+)?)px", resolve(decl.group(1)))
            if size and float(size.group(1)) < FLOOR_PX():
                errors.append(f"font size below {FLOOR_PX():g}px in {selector[:40]!r}: {decl.group(1).strip()[:30]}")
        for decl in re.finditer(r"(?:^|;)\s*(?:font-family|font)\s*:\s*([^;]+)", body, re.I):
            family = resolve(decl.group(1))
            # In the font shorthand the family list follows the size (and optional /line-height).
            family_list = re.sub(r"^.*?\d+(?:\.\d+)?(?:px|pt|em|rem|%)(?:\s*/\s*[\d.]+\w*)?\s+", "", family.strip()) \
                if decl.group(0).lower().lstrip("; ").startswith("font:") else family
            token = family_list.split(",")[0].strip().strip("\"'").strip()
            first = "" if not token or token.lower() in {"inherit", "initial", "unset"} or token.startswith("var(") \
                or re.fullmatch(r"[\d.]+\w*", token) else token
            if first and not re.search(r"mono|consol|courier|code", family, re.I) and not re.search(r"\b(?:pre|code|kbd|samp)\b", selector):
                families.add(first.lower())
        for decl in re.finditer(r"(?:^|;)\s*background(?:-color|-image)?\s*:\s*([^;]+)", body, re.I):
            value = resolve(decl.group(1))
            small = DARK_SMALL_SELECTOR.search(selector)
            # Flat style everywhere (design-standards.html, 扁平线性风格): no decorative gradients. Interfaces may keep a
            # black-alpha scrim over a photo, a hard-stop fill (sliders, progress) and skeleton shimmer.
            if re.search(r"gradient", value, re.I):
                if "interface" not in ALLOWED:
                    if not small:
                        errors.append(f"gradient background in {selector[:40]!r}")
                elif not (is_scrim(value) or is_hard_stop(value) or re.search(r"\bsk\b|\.ask\b|skeleton|shimmer", selector, re.I)):
                    errors.append(f"decorative gradient in {selector[:40]!r}: use one flat colour (扁平线性风格)")
            for color in parse_colors(value):
                lum = luminance(color)
                if lum < 0.6 and not small and "dark" not in ALLOWED:
                    errors.append(f"dark or saturated fill in {selector[:40]!r}: {decl.group(1).strip()[:30]} (luminance {lum:.2f})")
                elif ("interface" in ALLOWED and 0.3 < lum < 0.7 and ACTIVE_CONTROL_SELECTOR.search(selector)
                      and not re.search(r"::?(?:before|after)|-thumb|:disabled|:hover", selector)
                      and (1.05 / (lum + 0.05)) < 3.0):
                    # A coloured control fill that is neither a pale container nor a solid step fails WCAG 1.4.11 (3:1)
                    # and reads as washed-out (design-standards.html, 配色: 官方色板取阶).
                    errors.append(f"washed-out control fill in {selector[:40]!r}: {decl.group(1).strip()[:30]} ({1.05 / (lum + 0.05):.1f}:1 against white, needs 3:1 or a pale container)")
            if ("interface" in ALLOWED and re.search(r"gradient", value, re.I) and re.search(r"primary|danger", selector, re.I)
                    and not re.search(r"::?(?:before|after)|-thumb|prob", selector)):
                # Design systems fill buttons with one flat palette step (Ant Design, TDesign, Material 3).
                errors.append(f"gradient on control in {selector[:40]!r}: use one flat palette step")
        own_bg = [c for m in re.finditer(r"(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)", body, re.I) for c in parse_colors(resolve(m.group(1)))]
        backdrop = own_bg[0] if own_bg else (255, 255, 255)
        # Text on a transparent layer sits over imagery or a parent surface we cannot see here; skip it.
        transparent_layer = bool(re.search(r"background(?:-color)?\s*:\s*(?:transparent|none)\b", body, re.I))
        # Text needs 4.5:1; graphics (icons, frames, illustrations) and disabled controls need 3:1.
        minimum = 3.0 if GRAPHIC_SELECTOR.search(selector) or ":disabled" in selector else 4.5
        for decl in (() if transparent_layer else re.finditer(r"(?:^|;)\s*color\s*:\s*([^;]+)", body, re.I)):
            for color in parse_colors(resolve(decl.group(1))):
                lighter, darker = sorted((luminance(color), luminance(backdrop)), reverse=True)
                contrast = (lighter + 0.05) / (darker + 0.05)
                if contrast < minimum:
                    errors.append(f"color too light in {selector[:40]!r}: {decl.group(1).strip()} ({contrast:.1f}:1, needs {minimum:g}:1)")
        for decl in re.finditer(r"(?:^|;)\s*(?:box-shadow|text-shadow)\s*:\s*([^;]+)", body, re.I):
            blur = re.findall(r"(\d+)px", decl.group(1))
            if len(blur) >= 3 and int(blur[2]) > 24:
                warnings.append(f"heavy shadow in {selector[:40]!r}: {decl.group(1).strip()[:30]}")
        if "interface" in ALLOWED:
            # Flat interface (design-standards.html, 扁平线性风格; Ant Design shadow levels, Material 3 elevation):
            # cards take the lowest neutral shadow, overlays one level higher; no bevels, glows, glass or blobs.
            overlay = re.search(r"modal|dialog|pop|toast|tip|drop|sheet|layer|confirm|drawer|menu|float|picker|lightbox|panel", selector, re.I)
            for decl in re.finditer(r"(?:^|;)\s*box-shadow\s*:\s*([^;]+)", body, re.I):
                value = resolve(decl.group(1))
                for part in re.split(r",(?![^(]*\))", value):
                    lengths = re.sub(r"(?:rgba?|hsla?|var)\([^)]*\)|#[0-9a-f]{3,8}\b|\binset\b", " ", part, flags=re.I)
                    nums = [float(n) for n in re.findall(r"(-?\d*\.?\d+)(?:px)?\b", lengths)]
                    if part.strip().startswith("inset") and len(nums) >= 2 and nums[1] != 0:
                        errors.append(f"bevel shadow in {selector[:40]!r}: {part.strip()[:30]} (flat style has no raised or sunken buttons)")
                    elif len(nums) >= 3 and nums[0] == 0 and nums[1] == 0 and nums[2] >= 8 and not part.strip().startswith("inset"):
                        errors.append(f"glow in {selector[:40]!r}: {part.strip()[:30]}")
                    elif len(nums) >= 3 and nums[2] > 12 and not overlay:
                        errors.append(f"heavy card shadow in {selector[:40]!r}: {part.strip()[:30]} (cards use the lowest elevation)")
            if re.search(r"(?:^|;)\s*(?:-webkit-)?backdrop-filter\s*:\s*[^;]*blur", body, re.I):
                errors.append(f"glass blur in {selector[:40]!r}: flat surfaces are opaque")
            if re.search(r"(?:^|;)\s*border-radius\s*:\s*[^;]*\d+%\s+\d+%[^;]*", body, re.I):
                errors.append(f"organic blob shape in {selector[:40]!r}")
            if re.search(r"\.icon\b|svg\.fi\b|\bfi\b", selector) and not re.search(r"chart|check|box|avatar|art\b", selector):
                for decl in re.finditer(r"(?:^|;)\s*stroke-width\s*:\s*([\d.]+)", body, re.I):
                    icon_strokes.add(decl.group(1))
    if len(families) > 1:
        errors.append(f"more than one font family: {sorted(families)}")
    # One typeface everywhere (design-standards.html 字体与字号): the canonical stack is
    # "PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif; a page may lead with any of those three.
    allowed_first = {"pingfang sc", "microsoft yahei", "noto sans sc", "苹方", "微软雅黑", "思源黑体", "system-ui", "sans-serif", "inherit"}
    for family in sorted(families - allowed_first):
        errors.append(f"font family {family!r} is not the shared Chinese sans stack (PingFang SC / Microsoft YaHei / Noto Sans SC)")
    # Sizes outside <style>: inline style attributes, SVG text attributes and sizes written into scripts.
    style_text = re.sub(r"\s+", "", "\n".join(outline.styles))
    for number, unit in re.findall(r"font-size\s*[:=]\s*[\"']?\s*(\d+(?:\.\d+)?)(px)?(?![\d.]*(?:pt|em|rem|%))", source, re.I):
        if float(number) < FLOOR_PX() and f"font-size:{number}" not in style_text:
            errors.append(f"font size {number}{unit or ''} below {FLOOR_PX():g}px in an inline style, SVG attribute or script")
            break
    for family in sorted({f.strip().strip("'\"").lower() for f in re.findall(r"font-family\s*=\s*[\"']([^\"',]+)", source, re.I)} - allowed_first):
        errors.append(f"SVG font-family {family!r} differs from the shared stack")
    # One object, one icon (design-standards.html 图形：一套线性图标): the same pictogram must not label two
    # different things. Short glyphs (arrows, close, plus, check) are controls, not pictograms, and are skipped.
    if "interface" in ALLOWED or "website" in ALLOWED:
        meaning: dict[str, set[str]] = {}
        for m in re.finditer(r"<svg\b[^>]*>(.*?)</svg>\s*(?:<[^>]+>\s*)*([^<>{}'\"+]{2,16})", source, re.S):
            drawing = re.sub(r"\s+", "", m.group(1))
            if len(drawing) < 60 or "<text" in drawing:
                continue
            label = re.sub(r"[\d\s·（）()¥%、，,.]+", "", m.group(2))
            if len(label) >= 2:
                meaning.setdefault(drawing, set()).add(label)
        for drawing, labels in meaning.items():
            distinct = {l for l in labels if not any(l != o and (l in o or o in l) for o in labels)}
            if len(distinct) > 1:
                errors.append(f"one icon labels different things: {sorted(distinct)[:4]}; give each object its own icon")
    # Elements the browser renders in italic by default must be reset to normal when they carry text.
    italic_tags = sorted({t.lower() for t, inner in re.findall(r"<(i|em|cite|var|dfn|address)\b[^>]*>([^<]*)</\1>", source, re.I) if inner.strip()})
    resets = re.findall(r"([^{}]*)\{[^{}]*font-style\s*:\s*normal[^{}]*\}", css, re.I)
    for tag in italic_tags:
        if not any(re.search(rf"(?:^|[\s,>+~(]){tag}\b|(?:^|[\s,])\*(?:[\s,]|$)", sel) for sel in resets):
            errors.append(f"<{tag}> renders italic by default; reset it with font-style: normal")
    radii = {v for v in re.findall(r"border-radius\s*:\s*(\d+)px", css) if v not in {"0", "999", "9999", "50"}}
    if len(radii) > 3:
        warnings.append(f"inconsistent corner radii: {sorted(radii, key=int)}")
    if "interface" in ALLOWED:
        if len(icon_strokes) > 1:
            errors.append(f"mixed icon stroke widths {sorted(icon_strokes)}: one icon set, one stroke width (扁平线性风格)")
        for m in re.finditer(r"<(linearGradient|radialGradient)\b", source):
            errors.append(f"<{m.group(1)}> in an interface graphic: icons, charts and illustrations are flat")
        for m in re.finditer(r"<img\b[^>]*class=[\"'][^\"']*\b(?:i3|icon|ico)\b", source, re.I):
            errors.append(f"raster icon {m.group(0)[:50]!r}: draw icons as one set of line vectors")
        # Default avatars are cartoon animals or a line icon, never initials, a surname or any other text (design-standards.html, 头像).
        for m in re.finditer(r"class=[\"'][^\"']*\bavatar\b[^\"']*[\"'][^>]*>\s*([^<\s'][^<]{0,5}?)\s*<", source, re.I):
            errors.append(f"text inside avatar: {m.group(1)!r}; use a cartoon avatar or a line icon")
        for m in re.finditer(r"avatar[^\n]{0,80}?(?:\[0\]|charAt\(0\)|slice\(0,\s*[12]\)|substr(?:ing)?\(0,\s*[12]\)|\.(?:name|nick\w*|user\w*)\b[^\n]{0,6}?(?:\[0\]|\.slice))", source, re.I):
            errors.append(f"initials or text used as avatar: {m.group(0)[:60]!r}")
    if not re.search(r"<html[^>]+lang=", source, re.I):
        warnings.append("missing lang attribute")
    if not re.search(r"name=[\"']viewport", source, re.I):
        warnings.append("missing viewport meta")


# ---------------------------------------------------------------- XLSX

def check_xlsx(path: Path, errors: list[str], warnings: list[str]) -> None:
    try:
        import openpyxl
    except ImportError:
        errors.append("openpyxl is required: py -m pip install openpyxl")
        return
    book = openpyxl.load_workbook(path)
    sheets = book.worksheets
    if len(sheets) > 1 and "multi-sheet" not in ALLOWED:
        errors.append(f"{len(sheets)} worksheets; only one is allowed unless the user asked for more ({', '.join(s.title for s in sheets)})")
    fonts: set[str] = set()
    sizes: set[float] = set()
    for sheet in sheets:
        where = f"[{sheet.title}]"
        if re.fullmatch(r"(?:Sheet|工作表)\d*", sheet.title, re.I):
            errors.append(f"{where} default sheet name; name it after the content")
        if sheet.sheet_state != "visible":
            errors.append(f"{where} hidden worksheet")
        if getattr(sheet, "_images", None) or getattr(sheet, "_charts", None):
            if "chart" not in ALLOWED:
                errors.append(f"{where} images or charts the user did not ask for (pass --allow chart if requested)")
        rows = [[c for c in row if c.value not in (None, "")] for row in sheet.iter_rows()]
        while rows and not rows[-1]:
            rows.pop()
        if not rows or not rows[0]:
            errors.append(f"{where} row 1 must hold the title")
            continue
        if len(rows[0]) != 1 or rows[0][0].column != 1:
            errors.append(f"{where} row 1 must contain only the title in A1")
        header_index = next((i for i, r in enumerate(rows[1:], 1) if len(r) >= 2), None)
        if header_index is None:
            errors.append(f"{where} no header row found")
            continue
        for i in range(1, header_index):
            if rows[i]:
                errors.append(f"{where} row {i + 1} sits between the title and the header: {str(rows[i][0].value)[:30]!r}")
        header = rows[header_index]
        header_values = [str(c.value).strip() for c in header]
        last_col = max(c.column for c in header)
        first_col = min(c.column for c in header)
        # Everything must sit inside the data rectangle: title, header, data, section titles, totals.
        for i in range(header_index + 1, len(rows)):
            row = rows[i]
            if not row:
                continue
            outside = [c for c in row if c.column > last_col or c.column < first_col]
            for cell in outside:
                errors.append(f"{where}{cell.coordinate} content outside the data table: {str(cell.value)[:30]!r}")
            inside = [c for c in row if c not in outside]
            # A row that continues a vertically merged group cell is a data row, not a lone note.
            in_group = any(m.min_row > 1 and m.min_row < inside[0].row <= m.max_row for m in sheet.merged_cells.ranges) if inside else False
            if len(inside) == 1 and isinstance(inside[0].value, str) and len(header) > 1 and not in_group:
                following = next((r for r in rows[i + 1:] if r), None)
                is_section = following is not None and [str(c.value).strip() for c in following] == header_values
                if not is_section:
                    errors.append(f"{where}{inside[0].coordinate} single text cell inside or below the table "
                                  f"(note, legend, unit or conclusion?): {inside[0].value[:30]!r}")
        title_size = rows[0][0].font.sz or 11
        for row in rows:
            for cell in row:
                if isinstance(cell.value, str):
                    check_text(cell.value, f"{where}{cell.coordinate}", errors)
                fonts.add((cell.font.name or "").lower())
                size = float(cell.font.sz or 11)
                sizes.add(size)
                if size < 12:
                    errors.append(f"{where}{cell.coordinate} font {size:g}pt is below 12pt")
                if size > title_size:
                    errors.append(f"{where}{cell.coordinate} is larger than the title")
                fill = cell.fill
                if fill is not None and fill.fill_type == "solid":
                    rgb = getattr(fill.fgColor, "rgb", None)
                    if isinstance(rgb, str) and re.fullmatch(r"[0-9A-Fa-f]{8}", rgb) and luminance(hex_rgb(rgb)) < 0.6:
                        errors.append(f"{where}{cell.coordinate} dark fill #{rgb[2:]}")
                color = getattr(cell.font.color, "rgb", None) if cell.font.color is not None else None
                if isinstance(color, str) and re.fullmatch(r"[0-9A-Fa-f]{8}", color):
                    contrast = 1.05 / (luminance(hex_rgb(color)) + 0.05)
                    if contrast < 4.5:
                        errors.append(f"{where}{cell.coordinate} font color too light #{color[2:]}")
        if not header[0].font.b:
            warnings.append(f"{where} header row is not bold")
        data_rows = len(rows) - header_index - 1
        if data_rows > 20 and not sheet.freeze_panes:
            errors.append(f"{where} freeze the header row")
        has_vertical_merges = any(m.min_row > 1 and m.max_row > m.min_row for m in sheet.merged_cells.ranges)
        if data_rows > 20 and not sheet.auto_filter.ref and not has_vertical_merges:
            warnings.append(f"{where} no filter on a table longer than 20 rows")
        if not any(d.width not in (None, 13.0) for d in sheet.column_dimensions.values()):
            errors.append(f"{where} column widths were not set")
        # Merging (file-design.html, 表格文件): the title spans the table; inside the data a cell may only merge
        # vertically to group equal consecutive values of one column; horizontal layout merges are not allowed
        # except a label spanning the merged group columns on a total row.
        header_row = header[0].row
        merged_cover: set[tuple[int, int]] = set()
        for merged in sheet.merged_cells.ranges:
            for r in range(merged.min_row, merged.max_row + 1):
                for c in range(merged.min_col, merged.max_col + 1):
                    merged_cover.add((r, c))
            if merged.min_row == 1:
                continue
            if merged.min_col != merged.max_col and merged.min_row == merged.max_row and merged.min_row > header_row:
                label = sheet.cell(merged.min_row, merged.min_col).value
                # The row's first-column label may itself be a vertical merge (合计 over two summary rows).
                row_label = sheet.cell(merged.min_row, first_col).value
                for other in sheet.merged_cells.ranges:
                    if other.min_col <= first_col <= other.max_col and other.min_row <= merged.min_row <= other.max_row:
                        row_label = sheet.cell(other.min_row, other.min_col).value
                if not any(isinstance(v, str) and re.search(r"合计|总计|小计", v) for v in (label, row_label)):
                    errors.append(f"{where} horizontal merge in the data area: {merged.coord}")
            elif merged.min_col != merged.max_col:
                errors.append(f"{where} block merge in the data area: {merged.coord}")
        # No sequence-number column: the data identifies itself.
        for cell in header:
            if re.fullmatch(r"\s*(?:序号|行号|序|No\.?|#)\s*", str(cell.value), re.I):
                errors.append(f"{where}{cell.coordinate} sequence-number column {cell.value!r}; write the data itself")
        data_cells = [r for r in rows[header_index + 1:] if r]
        first_col_values = [r[0].value for r in data_cells if r[0].column == first_col]
        if len(first_col_values) >= 3 and all(isinstance(v, int) for v in first_col_values) \
                and first_col_values == list(range(first_col_values[0], first_col_values[0] + len(first_col_values))):
            errors.append(f"{where} first column is a running number; remove the sequence column")
        # Same text repeated down a grouping column must be merged, not written on every row.
        grouping = True
        for col in range(first_col, last_col + 1):
            values = [(r, sheet.cell(r, col).value) for r in range(header_row + 1, sheet.max_row + 1)]
            filled = [v for _, v in values if v not in (None, "")]
            if not filled or sum(isinstance(v, str) for v in filled) * 2 < len(filled):
                continue  # numbers and sequence columns neither group nor break grouping
            run_found = any(
                isinstance(v, str) and v.strip() not in ("", "—", "-") and v == values[i + 1][1]
                and (r, col) not in merged_cover and (values[i + 1][0], col) not in merged_cover
                for i, (r, v) in enumerate(values[:-1])
            )
            is_group_col = any((r, col) in merged_cover for r, _ in values) or run_found
            if run_found and grouping:
                errors.append(f"{where} column {sheet.cell(header_row, col).value!r} repeats the same text on consecutive rows; merge those cells vertically")
            if not is_group_col:
                grouping = False
        header_fill = header[0].fill
        if header_fill is None or header_fill.fill_type != "solid":
            warnings.append(f"{where} header row has no light fill")
        for row in sheet.iter_rows():
            for cell in row:
                if cell.comment:
                    errors.append(f"{where}{cell.coordinate} cell comment")
        hidden_cols = [k for k, d in sheet.column_dimensions.items() if d.hidden]
        hidden_rows = [k for k, d in sheet.row_dimensions.items() if d.hidden]
        if hidden_cols or hidden_rows:
            errors.append(f"{where} hidden rows or columns: {hidden_cols + hidden_rows}")
        if not sheet.print_area:
            warnings.append(f"{where} print area not set")
    if len(fonts) > 1:
        errors.append(f"more than one font family: {sorted(fonts)}")
    if len(sizes) > 4:
        errors.append(f"more than four font sizes: {sorted(sizes)}")


# ---------------------------------------------------------------- DOCX

def check_docx(path: Path, errors: list[str], warnings: list[str]) -> None:
    try:
        import docx
        from docx.oxml.ns import qn
    except ImportError:
        errors.append("python-docx is required: py -m pip install python-docx")
        return
    document = docx.Document(str(path))
    paragraphs = [p for p in document.paragraphs if p.text.strip()]
    if not paragraphs:
        errors.append("document has no text")
        return

    def is_heading(paragraph) -> bool:
        name = (paragraph.style.name or "").lower()
        return "heading" in name or "title" in name or "标题" in name

    first = paragraphs[0]
    if not is_heading(first):
        sizes = [r.font.size.pt for r in first.runs if r.font.size]
        body = [r.font.size.pt for p in paragraphs[1:6] for r in p.runs if r.font.size]
        if not sizes or (body and max(sizes) <= max(body)):
            errors.append(f"first paragraph is not a title: {first.text[:40]!r}")
    if len(paragraphs) > 1 and not re.search(r"合同|协议", first.text) and not is_heading(paragraphs[1]) and not all(r.bold for r in paragraphs[1].runs if r.text.strip()):
        errors.append(f"text between the title and the first heading: {paragraphs[1].text[:40]!r}")
    families: set[str] = set()
    for paragraph in paragraphs:
        check_text(paragraph.text, "paragraph", errors)
        if is_heading(paragraph):
            check_heading(paragraph.text, "heading", errors)
        for run in paragraph.runs:
            if run.font.size and run.font.size.pt < 10.5:
                errors.append(f"font {run.font.size.pt:g}pt below 10.5pt (五号): {run.text[:20]!r}")
            r_fonts = run._element.rPr.rFonts if run._element.rPr is not None else None
            east = r_fonts.get(qn("w:eastAsia")) if r_fonts is not None else None
            for name in (run.font.name, east):
                if name:
                    families.add(name.lower())
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                check_text(cell.text, "table cell", errors)
    if len(families) > 2:
        errors.append(f"more than one font family: {sorted(families)}")
    # Document types (file-design.html, 按文档类型).
    full_text = "\n".join([p.text for p in document.paragraphs] + [c.text for t in document.tables for r in t.rows for c in r.cells])
    for m in re.finditer(r"【[^】]{0,12}】|[×xX]{2,}|待定|待补充|请填写|TBD", full_text):
        errors.append(f"placeholder left in the document: {m.group(0)!r}")
        break
    if re.search(r"合同|协议", first.text):
        if len(set(re.findall(r"^\s*([甲乙丙丁]方|买方|卖方|出租方|承租方|委托方|受托方)\s*[（(：:]", full_text, re.M))) < 2:
            errors.append("contract: party information for each party (甲方 / 乙方 名称、代码、住所、代表人、联系方式) is missing")
        if not re.search(r"盖章|签字|签章", full_text):
            errors.append("contract: signature block (盖章 / 签字 / 日期) is missing")
        footer_xml = "".join(s.footer._element.xml for s in document.sections)
        if "NUMPAGES" not in footer_xml:
            errors.append("contract: footer needs “第 X 页 共 Y 页” (PAGE and NUMPAGES fields)")
        if re.search(r"(?:人民币|¥|￥)\s*[\d,]{4,}", full_text) and "大写" not in full_text:
            errors.append("contract: amounts need the capitalised form (大写)")
    body_xml = document.element.body.xml
    if "<w:txbxContent" in body_xml:
        errors.append("text boxes used for layout or side notes")
    for section in document.sections:
        header = " ".join(p.text for p in section.header.paragraphs).strip()
        if header and "header" not in ALLOWED:
            errors.append(f"header text the user did not ask for: {header[:40]!r}")
        footer = " ".join(p.text for p in section.footer.paragraphs).strip()
        if footer and not re.fullmatch(r"[\d\s第页共/\-—]*", footer) and "header" not in ALLOWED:
            errors.append(f"footer holds more than a page number: {footer[:40]!r}")


# ---------------------------------------------------------------- PPTX

def check_pptx(path: Path, errors: list[str], warnings: list[str]) -> None:
    try:
        from pptx import Presentation
        from pptx.util import Emu
    except ImportError:
        errors.append("python-pptx is required: py -m pip install python-pptx")
        return
    deck = Presentation(str(path))
    slide_area = deck.slide_width * deck.slide_height
    families: set[str] = set()
    for number, slide in enumerate(deck.slides, 1):
        where = f"slide {number}"
        fill = slide.background.fill if slide.background is not None else None
        try:
            if fill is not None and fill.type == 1 and luminance(hex_rgb(str(fill.fore_color.rgb))) < 0.6 and "dark" not in ALLOWED:
                errors.append(f"{where}: dark slide background #{fill.fore_color.rgb}")
        except (AttributeError, TypeError, ValueError):
            pass
        texts = []
        for shape in slide.shapes:
            try:
                if shape.fill.type == 1 and shape.width * shape.height > slide_area * 0.1 and luminance(hex_rgb(str(shape.fill.fore_color.rgb))) < 0.6 and "dark" not in ALLOWED:
                    errors.append(f"{where}: large dark shape #{shape.fill.fore_color.rgb}")
            except (AttributeError, TypeError, ValueError):
                pass
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                text = "".join(run.text for run in paragraph.runs).strip()
                if not text:
                    continue
                texts.append(text)
                check_text(text, where, errors)
                for run in paragraph.runs:
                    if run.font.size is not None and Emu(run.font.size).pt < 16:
                        errors.append(f"{where}: font {Emu(run.font.size).pt:g}pt below 16pt: {run.text[:20]!r}")
                    if run.font.name:
                        families.add(run.font.name.lower())
        if not texts:
            errors.append(f"{where}: slide carries no text conclusion")
            continue
        title = slide.shapes.title.text_frame.text.strip() if slide.shapes.title is not None and slide.shapes.title.has_text_frame else texts[0]
        if number == 1 and title != texts[0]:
            errors.append(f"{where}: the first line of the cover is not the title: {texts[0][:30]!r}")
        if "accessory" not in ALLOWED and FILLER_SLIDE.match(title):
            errors.append(f"{where}: filler slide {title!r} (pass --allow accessory if the user asked for it)")
        if number == 1 and len(texts) > 1 and "cover" not in ALLOWED:
            errors.append(f"{where}: cover holds more than the title: {texts[1][:30]!r}")
    if len(families) > 1:
        errors.append(f"more than one font family: {sorted(families)}")


# ---------------------------------------------------------------- Markdown

def check_markdown(path: Path, errors: list[str], warnings: list[str]) -> None:
    lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()]
    content = [(i, line) for i, line in enumerate(lines, 1) if line.strip()]
    if not content:
        errors.append("empty file")
        return
    if not re.match(r"#\s+\S", content[0][1]):
        errors.append(f"line {content[0][0]} must be '# title': {content[0][1][:40]!r}")
    if any(re.match(r"##\s", line) for _, line in content) and len(content) > 1 and not re.match(r"##\s", content[1][1]):
        errors.append(f"line {content[1][0]}: text between the title and the first section: {content[1][1][:40]!r}")
    for number, line in content:
        check_text(line, f"line {number}", errors)
        heading = re.match(r"#{2,4}\s+(.*)", line)
        if heading:
            check_heading(heading.group(1), f"line {number}", errors)
        if line.startswith(">"):
            errors.append(f"line {number}: blockquote used as a side note")
        if re.search(r"!\[[^\]]*\]\([^)]*(?:shields\.io|badge)", line, re.I) or line.strip() in {"[TOC]", "[toc]"}:
            errors.append(f"line {number}: badge or generated table of contents")
    rules = sum(1 for _, line in content if re.fullmatch(r"\s*(?:-{3,}|\*{3,})\s*", line))
    if rules > 2:
        warnings.append(f"{rules} horizontal rules used as decoration")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--allow", action="append", default=[], metavar="KIND",
                        help="interface (prototype pages using interface type scales; add website for a website prototype with 40/48 first-screen titles), or only for items the user explicitly asked for: multi-sheet, chart, accessory, cover, header, "
                             "shell, dark, note, emoji, or a text family (" + ", ".join(FAMILIES) + ")")
    parser.add_argument("--allow-multi-sheet", action="store_true", help="same as --allow multi-sheet")
    args = parser.parse_args(argv)
    ALLOWED.clear()
    ALLOWED.update(kind.strip() for value in args.allow for kind in value.split(","))
    if args.allow_multi_sheet:
        ALLOWED.add("multi-sheet")
    failed = False
    for path in args.files:
        errors: list[str] = []
        warnings: list[str] = []
        suffix = path.suffix.lower()
        if not path.is_file():
            errors.append("file not found")
        elif suffix in {".html", ".htm"}:
            check_html(path, errors, warnings)
        elif suffix in {".xlsx", ".xlsm"}:
            check_xlsx(path, errors, warnings)
        elif suffix == ".docx":
            check_docx(path, errors, warnings)
        elif suffix == ".pptx":
            check_pptx(path, errors, warnings)
        elif suffix in {".md", ".markdown"}:
            check_markdown(path, errors, warnings)
        else:
            errors.append(f"unsupported format {suffix}; review it manually against rules/file-design.html")
        status = "FAIL" if errors else "PASS"
        print(f"{status}: {path} ({len(errors)} error(s), {len(warnings)} warning(s))")
        for item in errors:
            print("  ERROR", item)
        for item in warnings:
            print("  WARN ", item)
        failed |= bool(errors)
    if not failed:
        print("Automated checks passed. Apply the deletion test to every visible element before delivery.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
