"""公文版式后处理：生成器暂无公文（official）版式，样例在 make_docx 的输出上按《党政机关公文格式》调整。

    py -X utf8 tools/official_post.py in.docx specs/DC-WD-005-公文.json [out.docx]

做的事（见规则卡“公文格式”）：纸张版心 156 × 225 毫米（天头 37、订口 28 毫米），正文 3 号仿宋、固定行距 29 磅（每面 22 行），
第一层黑体、第二层楷体、第三层仿宋，标题二号居中，主送机关顶格，附件说明左空二字，署名与成文日期右空，页码 4 号宋体、
数字左右各一条一字线、单页居右双页居左。不改生成器；调整后用 ``check_document.py --allow official`` 检查
（主送机关紧跟标题，检查脚本的“标题后须直接是标题”会误报，需再加 ``--allow cover``）。

spec 里的 ``official`` 块只给后处理用，make_docx 忽略它：
  {"addressee": "主送机关：", "attachment_line": "附件：…", "signature": ["署名", "成文日期"]}
"""
from __future__ import annotations

from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt


def _set_east(run, name, size):
    run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    fonts.set(qn("w:eastAsia"), name)


def apply_official(path: Path, spec: dict) -> None:
    d = docx.Document(str(path))
    info = spec["official"]
    sec = d.sections[0]
    sec.top_margin, sec.bottom_margin = Mm(37), Mm(35)
    sec.left_margin, sec.right_margin = Mm(28), Mm(26)
    sec.header_distance, sec.footer_distance = Mm(20), Mm(25)
    size = 16  # 3 号
    line = Pt(29)  # 每面 22 行
    # styles
    for style_name, east in (("Normal", "仿宋"), ("Heading 1", "黑体"), ("Heading 2", "楷体"), ("Heading 3", "仿宋")):
        st = d.styles[style_name]
        st.font.size = Pt(size)
        st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), east)
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        st.paragraph_format.line_spacing = line
        if style_name != "Normal":
            st.paragraph_format.space_before = Pt(0)
            st.paragraph_format.space_after = Pt(0)
    # numbering level fonts follow the heading levels
    numbering = d.part.numbering_part.element
    fonts = {0: "黑体", 1: "楷体", 2: "仿宋"}
    for absn in numbering.findall(qn("w:abstractNum")):
        for lvl in absn.findall(qn("w:lvl")):
            i = int(lvl.get(qn("w:ilvl")))
            rpr = lvl.find(qn("w:rPr"))
            if rpr is None or i not in fonts:
                continue
            rpr.find(qn("w:rFonts")).set(qn("w:eastAsia"), fonts[i])
            for tag in ("w:sz", "w:szCs"):
                e = rpr.find(qn(tag))
                if e is not None:
                    e.set(qn("w:val"), str(size * 2))
    east_of = {"Normal": "仿宋", "Heading 1": "黑体", "Heading 2": "楷体", "Heading 3": "仿宋", "Caption": "宋体"}
    body_start = None
    paragraphs = d.paragraphs
    title_done = False
    for p in paragraphs:
        text = p.text.strip()
        if not text:
            continue
        name = p.style.name
        if not title_done:                      # 标题：二号，居中
            title_done = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(29)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            p.paragraph_format.line_spacing = Pt(35)
            for r in p.runs:
                _set_east(r, "宋体", 22)
            continue
        if name == "Caption":
            for r in p.runs:
                _set_east(r, "宋体", 12)
            continue
        east = east_of.get(name, "仿宋")
        for r in p.runs:
            _set_east(r, east, size)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = line
        if name == "Normal":
            p.paragraph_format.first_line_indent = Pt(size * 2)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if text == info["addressee"]:           # 主送机关：顶格，末尾冒号
            p.paragraph_format.first_line_indent = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if text == info["attachment_line"]:    # 附件说明：左空二字
            p.paragraph_format.first_line_indent = Pt(size * 2)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(29)
        if text in info["signature"]:           # 署名与成文日期：日期右空四字，署名居于日期之上
            p.paragraph_format.first_line_indent = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            date_chars = len(info["signature"][1])
            if text == info["signature"][1]:
                p.paragraph_format.right_indent = Pt(size * 4)
            else:
                p.paragraph_format.right_indent = Pt(size * (4 + (date_chars - len(text)) / 2))
                p.paragraph_format.space_before = Pt(29)
        if text.startswith("附件一："):          # 仅一件附件时不写序号
            for r in p.runs:
                if r.text.startswith("附件一："):
                    r.text = r.text.replace("附件一：", "附件：", 1)
    # 表格：仿宋小四，居中的表头
    for t in d.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                    for r in p.runs:
                        _set_east(r, "仿宋", 12)
    # 页码：4 号宋体、一字线，单页居右、双页居左
    d.settings.odd_and_even_pages_header_footer = True
    footer_odd, footer_even = sec.footer, sec.even_page_footer
    for footer, align in ((footer_odd, WD_ALIGN_PARAGRAPH.RIGHT), (footer_even, WD_ALIGN_PARAGRAPH.LEFT)):
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0]
        for r in list(p.runs):
            r._r.getparent().remove(r._r)
        p.alignment = align
        p.paragraph_format.right_indent = Pt(14 * 1) if align == WD_ALIGN_PARAGRAPH.RIGHT else None
        p.paragraph_format.left_indent = Pt(14 * 1) if align == WD_ALIGN_PARAGRAPH.LEFT else None

        def run(text=None, code=None):
            r = p.add_run()
            r.font.size = Pt(14)
            r.font.name = "Times New Roman"
            fonts_ = r._element.get_or_add_rPr().get_or_add_rFonts()
            fonts_.set(qn("w:eastAsia"), "宋体")
            if text is not None:
                r.text = text
            return r

        run("— ")
        for kind, instr in (("begin", None), (None, "PAGE"), ("separate", None), (None, "1"), ("end", None)):
            r = run()
            if kind:
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), kind)
                r._r.append(fc)
            elif instr == "PAGE":
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = " PAGE "
                r._r.append(it)
            else:
                r.text = instr
        run(" —")
    d.save(str(path))


def main(argv=None) -> int:
    import argparse
    import json
    import sys
    ap = argparse.ArgumentParser(description="公文版式后处理")
    ap.add_argument("docx", type=Path)
    ap.add_argument("spec", type=Path)
    ap.add_argument("out", type=Path, nargs="?")
    args = ap.parse_args(argv)
    target = args.out or args.docx
    if args.out:
        target.write_bytes(args.docx.read_bytes())
    apply_official(target, json.loads(args.spec.read_text(encoding="utf-8-sig")))
    print("wrote", target)
    return 0


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
