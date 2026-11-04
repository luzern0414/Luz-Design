"""Read the rule card first: py -X utf8 scripts/context.py docx

Build a formatted Word document that follows file-design.html (文字文档 and 文档类型).

    py -X utf8 scripts/make_docx.py spec.json out.docx

spec.json (common keys):
{
  "type": "contract" | "proposal" | "report" | "minutes" | "general",
  "title": "健身房智能门禁采购合同",
  "theme": "fitness-gym",                        # choose the table tint for this topic; themes.json
  "sections": [                                   # body, in order
    {"heading": "合同标的", "paragraphs": ["..."], "items": ["...", "..."],
     "table": {"header": ["设备", "数量", "单价（元）"], "rows": [["人脸终端", 2, 1680]], "money_cols": [2]},
     "children": [ {"heading": "...", "paragraphs": ["..."]} ]}
  ],
  "attachments": [{"title": "设备清单", "sections": [...]}],  # optional, each starts on a new page
  "style": "paper",                               # optional, only when the user asks for 论文版式 (not for contracts)
  "number_format": "1、"                          # paper only: "1、" (default), "1." or "一、" (一、 → （一） → 1.; the default when "mono" is set)
}
contract only:
  "number": "DLKJ-2026-018",                      # 合同编号, right-aligned under the title
  "parties": [{"role": "甲方", "fields": [["名称", "..."], ["统一社会信用代码", "..."], ["地址", "..."], ["法定代表人", "..."], ["联系人及电话", "..."]]},
              {"role": "乙方", "fields": [...]}],
  "preamble": "甲乙双方根据《中华人民共和国民法典》及相关法律法规，经平等协商，就……达成如下协议：",
  "signature": [{"role": "甲方", "lines": ["（盖章）", "法定代表人或授权代表（签字）："]}, {"role": "乙方", "lines": [...]}]
minutes only:
  "meta": [["时间", "..."], ["地点", "..."], ["主持", "..."], ["参会", "..."], ["记录", "..."]]

Paragraph text may contain {{money:128000}}, which renders as “人民币 128,000.00 元（大写：壹拾贰万捌仟元整）”.
Contracts number clauses 第一条、第二条…, sub-clauses 1.1、1.2; other types number 一、（一）1.（1）.
Footer: contracts “第 X 页 共 Y 页”, other types the page number only.
A table stays on the page of the paragraph that introduces it (short tables whole, long ones with at least two rows).
Table alignment: header centred; money_cols (0-based) show 1,234.00 and align right; a column whose text wraps or runs
past 22 characters aligns left; other columns centre (file-design.html 文字文档 › 表格与图片).

paper only, for documents sent to a client (proposal, report):
  "mono": true,                                   # black text, black hairline table borders, no shading anywhere
  "cover": {"subtitle": "建设方案", "info": [["项目名称", "…"], ["版本", "V1.0"], ["日期", "2026-11-02"]]},   # own page, no header or footer
  "toc": true,                                    # own page after the cover: 目录 (Word TOC field, levels 1–2), Roman page numbers
  "toc_pages": [1, 1, 2, ...],                    # page shown for each heading (computed from a rendering; Word updates them on demand)
  "header_text": "…",                             # page header on contents and body pages, defaults to the title
  a section may use "blocks" instead of paragraphs/items/table, in the order written:
    {"p": "…"} · {"items": ["…"]} · {"sub": "二级标题"} · {"table": {"header": [...], "rows": [...], "caption": "标题", "breaks": [row index…]}}
  Tables carry a caption above them (表 N　标题, Word SEQ field); a table that runs over a page break continues under "续表 N"
  with its header row repeated (``breaks`` lists the data-row indexes where the continuation starts).

"style": "paper" follows file-design.html 文字文档 › 论文版式: A4 with 2.54 / 3.17 cm margins, 宋体 body and 黑体 headings
with Times New Roman for Latin text, title 18 pt and headings 14 / 12 pt without bold, body 12 pt at 1.5 lines,
headings numbered by Word's own list numbering (1、 or 1. / 1.1 / 1.1.1) instead of typed numbers, black text;
tables keep the ordinary light grid. The built-in check then runs with --allow paper.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from document_palette import table_tint

FONT = "微软雅黑"
INK = "262626"
LINE = "D9D9D9"
SIZES = {"title": 22, "h1": 16, "h2": 14, "h3": 12, "body": 12, "table": 10.5, "footer": 10.5}
# 论文版式 (file-design.html 文字文档 › 论文版式). 黑体 and 宋体 have no real bold, so titles and headings stay regular.
PAPER = {"body": "宋体", "head": "黑体", "latin": "Times New Roman", "ink": "000000", "margins_cm": (2.54, 3.17), "edge_cm": 1.5,
         "sizes": {"title": 18, "h1": 14, "h2": 12, "h3": 12, "body": 12, "table": 10.5, "footer": 10.5}}
# Heading numbers by Word's own list numbering: (number format, level text, what follows the number) for levels 1–3.
NUMBER_SCHEMES = {
    "1、": [("decimal", "%1、", "nothing"), ("decimal", "%1.%2", "space"), ("decimal", "%1.%2.%3", "space")],
    "1.": [("decimal", "%1.", "space"), ("decimal", "%1.%2", "space"), ("decimal", "%1.%2.%3", "space")],
    "一、": [("chineseCountingThousand", "%1、", "nothing"), ("chineseCountingThousand", "（%2）", "nothing"), ("decimal", "%3.", "space")],
}
CN = "零一二三四五六七八九"


def cn_num(n: int) -> str:
    if n <= 10:
        return "十" if n == 10 else CN[n]
    if n < 20:
        return "十" + (CN[n % 10] if n % 10 else "")
    if n < 100:
        return CN[n // 10] + "十" + (CN[n % 10] if n % 10 else "")
    return str(n)


def rmb_upper(amount: float) -> str:
    """人民币金额大写，例如 128000 → 壹拾贰万捌仟元整，100500.5 → 壹拾万零伍佰元伍角整。"""
    digits, units, bigs = "零壹贰叁肆伍陆柒捌玖", ["", "拾", "佰", "仟"], ["", "万", "亿", "万亿"]
    fen = round(amount * 100)
    yuan, jiao, cents = fen // 100, fen // 10 % 10, fen % 10
    text = ""
    if yuan:
        groups, n = [], yuan
        while n:
            groups.append(n % 10000)
            n //= 10000
        gap = False
        for gi in range(len(groups) - 1, -1, -1):
            g = groups[gi]
            if g == 0:
                gap = bool(text)
                continue
            if gap or (text and g < 1000):
                text += "零"
            part, zero = "", False
            for i in range(3, -1, -1):
                d = g // 10 ** i % 10
                if d == 0:
                    zero = bool(part)
                else:
                    if zero:
                        part += "零"
                        zero = False
                    part += digits[d] + units[i]
            text += part + bigs[gi]
            gap = False
        text += "元"
    if not jiao and not cents:
        return (text or "零元") + "整"
    if jiao:
        text += digits[jiao] + "角"
    elif yuan:
        text += "零"
    return text + (digits[cents] + "分" if cents else "整")


def money_text(match: re.Match) -> str:
    value = float(match.group(1))
    return f"人民币 {value:,.2f} 元（大写：{rmb_upper(value)}）"


def build(spec: dict, out: Path) -> Path:
    header_fill = table_tint(spec.get("theme"))
    import docx
    from docx.enum.section import WD_ORIENT, WD_SECTION  # noqa: F401
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    kind = spec.get("type", "general")
    paper = spec.get("style") == "paper" and kind != "contract"
    sizes = PAPER["sizes"] if paper else SIZES
    ink = PAPER["ink"] if paper else INK
    body_font, head_font, latin = (PAPER["body"], PAPER["head"], PAPER["latin"]) if paper else (FONT, FONT, FONT)
    head_bold = not paper
    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.54)
    sec.left_margin = sec.right_margin = Cm(PAPER["margins_cm"][1] if paper else 2.8)
    if paper:
        sec.header_distance = sec.footer_distance = Cm(PAPER["edge_cm"])
    usable = sec.page_width - sec.left_margin - sec.right_margin
    mono = bool(spec.get("mono")) and paper
    numfmt = spec.get("number_format") or ("一、" if mono else "1、")
    toc_seq = [0]
    line_color = "000000" if mono else LINE
    tcount = [0]

    def set_font(run, size, bold=False, east=None):
        run.font.name = latin
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = RGBColor.from_string(ink)
        fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            fonts.set(qn(attr), latin)
        fonts.set(qn("w:eastAsia"), east or body_font)

    # Base and heading styles carry the format, so Word's navigation pane and table of contents work.
    normal = doc.styles["Normal"]
    normal.font.name = latin
    normal.font.size = Pt(sizes["body"])
    normal.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), body_font)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)
    for level, size in ((1, sizes["h1"]), (2, sizes["h2"]), (3, sizes["h3"])):
        st = doc.styles[f"Heading {level}"]
        st.font.name = latin
        st.font.size = Pt(size)
        st.font.bold = head_bold
        st.font.italic = False
        st.font.color.rgb = RGBColor.from_string(ink)
        st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), head_font)
        st.paragraph_format.space_before = Pt((24 if paper else 18) if level == 1 else 12)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.line_spacing = 1.0 if paper else 1.5

    def element(tag, **attrs):
        e = OxmlElement(tag)
        for k, v in attrs.items():
            e.set(qn(k), v)
        return e

    def field(paragraph, code, cached="1", size=None, east=None):
        for kind_, text in (("begin", None), (None, code), ("separate", None), (None, cached), ("end", None)):
            r = paragraph.add_run()
            set_font(r, size or sizes["footer"], east=east)
            if kind_:
                fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind_); r._r.append(fc)
            elif text == code:
                it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" {code} "; r._r.append(it)
            else:
                r.text = text

    if paper:   # the built-in Caption style is blue, bold and small: make it plain black text
        cap_style = doc.styles["Caption"]
        cap_style.font.name = latin
        cap_style.font.size = Pt(sizes["table"])
        cap_style.font.bold = False
        cap_style.font.italic = False
        cap_style.font.color.rgb = RGBColor.from_string(ink)
        cap_style.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), head_font)

    # 论文版式: Word's own multilevel list numbers the three heading styles, so no number is typed into a heading.
    paper_num = None
    if paper:
        scheme = NUMBER_SCHEMES.get(numfmt, NUMBER_SCHEMES["1、"])
        numbering = doc.part.numbering_part.element
        abstract_id = max([int(a.get(qn("w:abstractNumId"))) for a in numbering.findall(qn("w:abstractNum"))], default=-1) + 1
        absn = element("w:abstractNum", **{"w:abstractNumId": str(abstract_id)})
        absn.append(element("w:multiLevelType", **{"w:val": "multilevel"}))
        for ilvl, (num_fmt, text, suffix) in enumerate(scheme):
            lvl = element("w:lvl", **{"w:ilvl": str(ilvl)})
            for child in (element("w:start", **{"w:val": "1"}), element("w:numFmt", **{"w:val": num_fmt}),
                          element("w:pStyle", **{"w:val": doc.styles[f"Heading {ilvl + 1}"].style_id}),
                          element("w:suff", **{"w:val": suffix}), element("w:lvlText", **{"w:val": text}),
                          element("w:lvlJc", **{"w:val": "left"})):
                lvl.append(child)
            ppr = element("w:pPr")
            ppr.append(element("w:ind", **{"w:left": "0", "w:firstLine": "0"}))
            lvl.append(ppr)
            rpr = element("w:rPr")
            rpr.append(element("w:rFonts", **{"w:ascii": latin, "w:hAnsi": latin, "w:eastAsia": head_font, "w:cs": latin}))
            rpr.append(element("w:b", **{"w:val": "0"}))
            half_points = str(int(sizes[f"h{ilvl + 1}"] * 2))
            rpr.append(element("w:sz", **{"w:val": half_points}))
            rpr.append(element("w:szCs", **{"w:val": half_points}))
            lvl.append(rpr)
            absn.append(lvl)
        first_num = numbering.find(qn("w:num"))          # every abstractNum precedes the num elements
        if first_num is not None:
            first_num.addprevious(absn)
        else:
            numbering.append(absn)

        def new_num(restart=False):
            num_id = max([int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))], default=0) + 1
            num = element("w:num", **{"w:numId": str(num_id)})
            num.append(element("w:abstractNumId", **{"w:val": str(abstract_id)}))
            if restart:
                override = element("w:lvlOverride", **{"w:ilvl": "0"})
                override.append(element("w:startOverride", **{"w:val": "1"}))
                num.append(override)
            numbering.append(num)
            return num_id

        paper_num = new_num()
        for level in (1, 2, 3):
            numpr = doc.styles[f"Heading {level}"].element.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = level - 1
            numpr.get_or_add_numId().val = paper_num

    def para(text="", size=None, bold=False, align=None, indent=True, style=None, after=0, east=None):
        p = doc.add_paragraph(style=style)
        if text:
            text = re.sub(r"\{\{money:([\d.]+)\}\}", money_text, str(text))
            set_font(p.add_run(text), size or sizes["body"], bold, east)
        if align:
            p.alignment = align
        if indent and kind != "contract" and not style:
            p.paragraph_format.first_line_indent = Pt((size or sizes["body"]) * 2)
        p.paragraph_format.space_after = Pt(after)
        return p

    def heading(text, level, num_id=None):
        if mono and re.search(r"[（(）)]", text):
            raise ValueError(f"a heading carries no parenthesised explanation: {text!r} (put it in the text below)")
        p = doc.add_paragraph(style=f"Heading {level}")
        run = set_font(p.add_run(text), sizes[f"h{level}"], head_bold, head_font) or p.runs[-1]
        if spec.get("toc") and level <= 2:
            toc_seq[0] += 1
            mark = toc_seq[0]
            run._r.addprevious(element("w:bookmarkStart", **{"w:id": str(mark), "w:name": f"_Toc{100000 + mark}"}))
            run._r.addnext(element("w:bookmarkEnd", **{"w:id": str(mark)}))
        if num_id and num_id != paper_num:            # attachments restart their own numbering
            numpr = p._p.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = level - 1
            numpr.get_or_add_numId().val = num_id
        return p

    def table(t, continued=False, number=None):
        header, rows = t["header"], t["rows"]
        money = set(t.get("money_cols", []))
        breaks = [b for b in sorted(t.get("breaks", [])) if 0 < b < len(rows)]
        titled = bool(t.get("caption") and paper)       # only a titled table owns a SEQ field, so only it takes a number
        if breaks and not continued:                    # a table over a page break: each piece repeats the header under 续表 N
            cut = [0] + breaks + [len(rows)]
            if titled:
                tcount[0] += 1                          # one number for the whole table; its pieces share it
                number = tcount[0]
            for k in range(len(cut) - 1):
                table({**t, "rows": rows[cut[k]:cut[k + 1]], "breaks": []}, continued=k > 0, number=number)
            return
        if titled:
            if not continued and number is None:       # 续表 never takes a number (it has no SEQ field), and neither does the first piece again
                tcount[0] += 1
                number = tcount[0]
            cap = doc.add_paragraph(style="Caption")
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.keep_with_next = True
            cap.paragraph_format.space_before, cap.paragraph_format.space_after = Pt(6), Pt(3)
            cap.paragraph_format.line_spacing = 1.0
            if continued:
                set_font(cap.add_run(f"续表 {number}"), sizes["table"], east=head_font)
            else:
                set_font(cap.add_run("表 "), sizes["table"], east=head_font)
                field(cap, "SEQ 表 \\* ARABIC", str(number), sizes["table"], head_font)
                set_font(cap.add_run("　" + t["caption"]), sizes["table"], east=head_font)
        if doc.paragraphs:                             # the introducing paragraph stays with the table
            doc.paragraphs[-1].paragraph_format.keep_with_next = True
        kept = len(rows) if len(rows) <= 8 else 2      # short tables move whole; long ones keep the header and two rows
        tb = doc.add_table(rows=1 + len(rows), cols=len(header))
        tb.alignment = WD_TABLE_ALIGNMENT.CENTER
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{edge}")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), line_color)
            borders.append(e)
        tb._tbl.tblPr.append(borders)
        # Column widths follow content (CJK counts double); cells centre vertically; a 合计 row is bold and shaded.
        def width(v):
            # 微软雅黑西文字母与数字约 0.6 个汉字宽（汉字记 2），按 1.2 估算，避免地址、编号等无空格长串被截断换行。
            return sum(2 if ord(ch) > 0x2E80 else 1.2 for ch in str(v if v is not None else ""))
        pad = 7 if paper else 4        # room for the cell margins, so a four-character name does not wrap in the first column
        weights = [min(max([width(header[c])] + [width(f"{r[c]:,.2f}" if c in money and isinstance(r[c], (int, float)) else r[c]) for r in rows]), 28) + pad
                   for c in range(len(header))]
        if t.get("widths"):                            # relative column widths written by the author (long text columns get the room)
            weights = list(t["widths"])
        tb.autofit = False
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tb._tbl.tblPr.append(layout)
        for c, w in enumerate(weights):
            tb.columns[c].width = int(usable * w / sum(weights))
            for row in tb.rows:
                row.cells[c].width = int(usable * w / sum(weights))
        # 一列只用一种对齐：金额列（money_cols）整列右对齐；其余列任一数据格超过 22 字或在本列宽内会折行，整列左对齐；否则整列居中。
        def _wraps(c):
            capacity = usable * weights[c] / sum(weights) / 12700 / sizes["table"] - 1
            return any(isinstance(v[c], str) and len(v[c]) > min(22, capacity) for v in rows if c < len(v))
        long_cols = {c for c in range(len(header)) if _wraps(c)}
        for r, values in enumerate([header] + rows):
            row = tb.rows[r]
            total_row = r > 0 and str(values[0]).strip() in ("合计", "总计", "小计")
            trpr = row._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:cantSplit"))
            if r == 0:
                trpr.append(OxmlElement("w:tblHeader"))
            for c, v in enumerate(values):
                cell = row.cells[c]
                text = f"{v:,.2f}" if (c in money and isinstance(v, (int, float)) and r) else ("" if v is None else str(v))
                cell.paragraphs[0].text = ""
                set_font(cell.paragraphs[0].add_run(text), sizes["table"], r == 0 or total_row)
                cell.paragraphs[0].paragraph_format.keep_with_next = r < kept
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                # Header centred; amounts right so digits line up; long text left; short values centred (表格对齐).
                long = r and c in long_cols and c not in money
                cell.paragraphs[0].alignment = (WD_ALIGN_PARAGRAPH.CENTER if r == 0 else WD_ALIGN_PARAGRAPH.RIGHT if c in money
                                                else WD_ALIGN_PARAGRAPH.LEFT if long else WD_ALIGN_PARAGRAPH.CENTER)
                cell.paragraphs[0].paragraph_format.line_spacing = 1.25
                if paper:
                    cell.paragraphs[0].paragraph_format.space_before = cell.paragraphs[0].paragraph_format.space_after = Pt(3)
                if (r == 0 or total_row) and not mono:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), header_fill if r == 0 else "F5F5F5")
                    cell._tc.get_or_add_tcPr().append(shd)
        para("", indent=False, after=6)

    def body(sections, depth=1, prefix="", num_id=None):
        for i, s in enumerate(sections, 1):
            if kind == "contract":
                label = f"第{cn_num(i)}条 " if depth == 1 else f"{prefix}{i} "
                child_prefix = f"{i}." if depth == 1 else f"{prefix}{i}."
            elif paper:
                label = "" if depth <= 3 else f"（{i}）"   # Word numbers levels 1–3 itself
                child_prefix = ""
            else:
                label = [f"{cn_num(i)}、", f"（{cn_num(i)}）", f"{i}.", f"（{i}）"][min(depth, 4) - 1]
                child_prefix = ""
            if s.get("heading"):
                heading(label + s["heading"], min(depth, 3), num_id)
            def add_items(items):
                for j, item in enumerate(items, 1):
                    mark = f"{child_prefix}{j} " if kind == "contract" else f"{j}. "
                    p = para(mark + re.sub(r"\{\{money:([\d.]+)\}\}", money_text, item), indent=False)
                    p.paragraph_format.left_indent = Pt(sizes["body"] * 2)
                    p.paragraph_format.first_line_indent = Pt(-sizes["body"] * (1.5 if kind != "contract" else 2))

            for text in s.get("paragraphs", []):
                p = para(text)
                if paper:
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_items(s.get("items", []))
            if s.get("table"):
                table(s["table"])
            for b in s.get("blocks", []):                  # ordered content: paragraphs, lists, sub headings and tables as written
                if "p" in b:
                    p = para(b["p"])
                    if paper:
                        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                elif "items" in b:
                    add_items(b["items"])
                elif "sub" in b:
                    heading(b["sub"], min(depth + 1, 3), num_id)
                elif "table" in b:
                    table(b["table"])
            if s.get("children"):
                body(s["children"], depth + 1, child_prefix, num_id)

    # Cover page, contents page and the three page-number runs (cover: none, contents: I II III, body: 1 2 3)
    cover = spec.get("cover") if paper else None
    header_text = spec.get("header_text") or spec["title"]

    def contents_entries():
        entries, i = [], 0
        for s in spec.get("sections", []):
            if not s.get("heading"):
                continue
            i += 1
            j = 0
            if numfmt == "一、":
                entries.append((1, f"{cn_num(i)}、{s['heading']}"))
            else:
                entries.append((1, (f"{i}、" if numfmt == "1、" else f"{i}. ") + s["heading"]))
            for b in s.get("blocks", []):
                if "sub" in b:
                    j += 1
                    entries.append((2, f"（{cn_num(j)}）{b['sub']}" if numfmt == "一、" else f"{i}.{j} {b['sub']}"))
        return entries

    def decorate(section, fmt):
        """Header: the document title over a hairline; footer: the page number, centred; numbering restarts in this section."""
        from docx.enum.text import WD_TAB_ALIGNMENT  # noqa: F401
        section.header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False
        hp = section.header.paragraphs[0]
        hp.text = ""
        border = element("w:pBdr")
        border.append(element("w:bottom", **{"w:val": "single", "w:sz": "4", "w:space": "1", "w:color": "000000"}))
        hp._p.get_or_add_pPr().append(border)
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_font(hp.add_run(header_text), sizes["footer"], east=body_font)
        fp = section.footer.paragraphs[0]
        fp.text = ""
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        field(fp, "PAGE", "1", east=body_font)
        for old in section._sectPr.findall(qn("w:pgNumType")):      # a new section copies the previous section's numbering
            section._sectPr.remove(old)
        section._sectPr.find(qn("w:pgMar")).addnext(element("w:pgNumType", **{"w:fmt": fmt, "w:start": "1"}))

    def build_cover():
        spacer = para("", indent=False)
        spacer.paragraph_format.space_before = Pt(150)
        title_size = 26 if len(spec["title"]) <= 15 else 22 if len(spec["title"]) <= 19 else 18      # 一号; 二号 and 小二 when a long title would break with one character on the second line
        para(spec["title"], title_size, False, WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=18, east=head_font)
        if cover.get("subtitle"):
            para(cover["subtitle"], 18, False, WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=96, east=head_font)     # 小二
        for label, value in cover.get("info", []):
            para(f"{label}：{value}", 14, False, WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=6)                    # 四号

    def build_contents():
        from docx.enum.style import WD_STYLE_TYPE
        from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
        para("目　录", 18, False, WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=18, east=head_font)                    # 小二
        for level in (1, 2):
            st = doc.styles.add_style(f"toc {level}", WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = doc.styles["Normal"]
            st.paragraph_format.left_indent = Pt(sizes["body"] * 2 * (level - 1))
            st.paragraph_format.line_spacing = 1.5
            st.paragraph_format.tab_stops.add_tab_stop(usable, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        pages = spec.get("toc_pages", [])
        entries = contents_entries()
        for k, (level, text) in enumerate(entries):
            p = doc.add_paragraph(style=f"toc {level}")
            if k == 0:
                for kind_ in ("begin", "instr", "separate"):
                    r = p.add_run()
                    if kind_ == "instr":
                        it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = ' TOC \\o "1-2" \\h \\z \\u '; r._r.append(it)
                    else:
                        fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind_); r._r.append(fc)
            link = OxmlElement("w:hyperlink")                 # the whole entry jumps to its heading
            link.set(qn("w:anchor"), f"_Toc{100000 + k + 1}")
            link.set(qn("w:history"), "1")
            runs = [p.add_run(text), p.add_run(), p.add_run(str(pages[k]) if k < len(pages) else "")]
            set_font(runs[0], sizes["body"], east=head_font if level == 1 else body_font)
            runs[1].add_tab()
            set_font(runs[2], sizes["body"])
            for r in runs:
                link.append(r._r)
            p._p.append(link)
            if k == len(entries) - 1:
                r = p.add_run()
                fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "end"); r._r.append(fc)

    if cover:
        build_cover()
        if spec.get("toc"):
            decorate(doc.add_section(WD_SECTION.NEW_PAGE), "lowerRoman")
            build_contents()
        decorate(doc.add_section(WD_SECTION.NEW_PAGE), "decimal")
    else:
        # Title (and contract number)
        t = para(spec["title"], sizes["title"], head_bold, WD_ALIGN_PARAGRAPH.CENTER, indent=False,
                 after=6 if kind == "contract" else (18 if paper else 12), east=head_font)
        t.paragraph_format.keep_with_next = True
    if kind == "contract" and spec.get("number"):
        para(f"合同编号：{spec['number']}", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False, after=12)
    if kind == "contract":
        for party in spec.get("parties", []):
            p = para(f"{party['role']}：{dict(party['fields']).get('名称', '')}", bold=True, indent=False)
            p.paragraph_format.space_before = Pt(6)
            for k, v in party["fields"]:
                if k != "名称":
                    para(f"{k}：{v}", indent=False)
        if spec.get("preamble"):
            p = para(spec["preamble"], indent=True)
            p.paragraph_format.first_line_indent = Pt(sizes["body"] * 2)
            p.paragraph_format.space_before = Pt(12)
    if kind == "minutes" and spec.get("meta"):
        table({"header": ["项目", "内容"], "rows": spec["meta"]})
    body(spec.get("sections", []))
    if kind == "contract" and spec.get("signature"):
        para("（以下无正文）", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=12)
        sig = spec["signature"]
        st = doc.add_table(rows=1, cols=len(sig))
        for c, party in enumerate(sig):
            cell = st.rows[0].cells[c]
            cell.paragraphs[0].text = ""
            set_font(cell.paragraphs[0].add_run(f"{party['role']}（盖章）："), sizes["body"], True)
            for line in party.get("lines", ["法定代表人或授权代表（签字）：", "日期：　　　　年　　月　　日"]):
                p = cell.add_paragraph()
                p.paragraph_format.space_before = Pt(18)
                set_font(p.add_run(line), sizes["body"])
        st.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    for att_i, att in enumerate(spec.get("attachments", []), 1):
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        para(f"附件{cn_num(att_i)}：{att['title']}", sizes["h1"], head_bold, WD_ALIGN_PARAGRAPH.LEFT, indent=False, after=12,
             east=head_font)
        body(att.get("sections", []), num_id=new_num(restart=True) if paper else None)

    # Footer: page numbers only (contracts: 第 X 页 共 Y 页); a cover document has its own header and footer per section
    if not cover:
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if kind == "contract":
            set_font(fp.add_run("第 "), sizes["footer"]); field(fp, "PAGE"); set_font(fp.add_run(" 页 共 "), sizes["footer"])
            field(fp, "NUMPAGES"); set_font(fp.add_run(" 页"), sizes["footer"])
        else:
            field(fp, "PAGE")
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def verify_output(out: Path, kind: str, allow: list[str] | None = None) -> int:
    """Run the document checker on what was just written; a builder never hands over a file that fails it."""
    import check_document
    print(f"rule card for this file: py -X utf8 scripts/context.py {kind}  (read it before writing the spec)", file=sys.stderr)
    code = check_document.main([arg for name in allow or [] for arg in ("--allow", name)] + [str(out)])
    if code:
        print(f"FAIL: {out.name} does not meet the {kind} rules above; fix the spec and build again", file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8-sig"))
    out = build(spec, Path(argv[1]))
    print("wrote", out)
    paper = spec.get("style") == "paper" and spec.get("type") != "contract"
    return verify_output(out, "docx", ["paper"] if paper else None)


if __name__ == "__main__":
    raise SystemExit(main())
