"""Markdown 报告转便携式文档：Markdown 来源 → 阅读页 HTML（references/md-type.css 的文字层级 + 主题浅色）→ Edge 导出带书签与页码的 PDF → check_pdf 核对。

技能的生成器目前没有 Markdown 到 PDF 的入口，本脚本只供文件模板库的样例使用，只依赖技能 scripts 里已有的模块
（check_document、check_pdf、make_table_pdf 的主题取色与导出函数、showcase 的表格列对齐），不改它们。

    py -X utf8 tools/md_to_pdf.py specs/DC-PD-004-报告.json out.pdf [--work 过程目录]

spec.json:
{
  "title": "花间集母亲节活动复盘报告",     # 与 Markdown 第一行一致
  "theme": "florist",                      # 必填：按主题选色，themes.json
  "keep_together": ["花礼盒", "配送员"],     # 可选：行业词表，防止分词器把这些词拆到两行
  "source": "DC-PD-004-报告.md"            # 相对 spec 所在目录
}

Markdown 范围（check_document 的 Markdown 规则）：第一行是 “# 主标题”，之后直接是 “## 章节”；标题最多三级；
表格不超过 6 列，表格前一行写 “表 N　标题” 即成为表题；列表最多两层；不用引用块。
正式交付前仍须按规则卡走前置检索与模板选择登记。
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_CANDIDATES = [Path(os.environ["LUZ_DESIGN_SCRIPTS"])] if os.environ.get("LUZ_DESIGN_SCRIPTS") else []
_CANDIDATES += [HERE.parents[3] / "scripts", Path(r"D:/Codes/Luz-Design/scripts")]
SCRIPTS = next(p for p in _CANDIDATES if (p / "make_table_pdf.py").is_file())
sys.path.insert(0, str(SCRIPTS))

import check_document  # noqa: E402
import make_table_pdf as T  # noqa: E402
import showcase  # noqa: E402

E = html.escape
MASTER = SCRIPTS.parent / "references" / "md-type.css"


def md_type_block() -> str:
    text = MASTER.read_text(encoding="utf-8")
    start = text.index("/* luz-md-type:start")
    end = text.index("/* luz-md-type:end */") + len("/* luz-md-type:end */")
    return text[start:end]


COLLECT: list[str] | None = None


def inline(text: str) -> str:
    """Escaped text with **bold**; Chinese breaks only between words (segmented once, see segment_words)."""
    out = []
    for k, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not part:
            continue
        if COLLECT is not None:
            COLLECT.append(part)
        piece = T.words(part)
        out.append(f"<strong>{piece}</strong>" if k % 2 else piece)
    return "".join(out)


def segment_words(md: str, terms: list[str]) -> None:
    """Split every text run into words with the browser's segmenter (T.segment), protecting the domain words in ``terms``."""
    global COLLECT
    COLLECT = []
    convert(md)
    runs, COLLECT = sorted(set(COLLECT)), None
    T.WORDS.clear()
    try:
        T.segment(runs, terms)
    except Exception as exc:          # no browser: ordinary CJK line breaking
        print("word segmentation skipped:", exc)


def parse_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    cells = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    return cells[0], [r for i, r in enumerate(cells) if i >= 2]


def convert(md: str) -> tuple[str, str]:
    """Markdown text -> (title, body html). Headings, paragraphs, lists (two levels), pipe tables with an optional caption line."""
    lines = md.splitlines()
    body, title, i = [], "", 0
    pending_caption = None
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"(#{1,4})\s+(.*)", ln)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1 and not title:
                title = text
            body.append(f"<h{level}>{inline(text)}</h{level}>")
            i += 1
            continue
        if ln.lstrip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            header, rows = parse_table(block)
            body.append(table_html(header, rows, pending_caption))
            pending_caption = None
            continue
        if re.match(r"\s*([-*]|\d+\.)\s+", ln):
            items = []
            while i < len(lines) and re.match(r"\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(lines[i])
                i += 1
            body.append(list_html(items))
            continue
        # paragraph (a "表 N　标题" line directly before a table is its caption)
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,4}\s|\s*\||\s*([-*]|\d+\.)\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        text = "".join(para)
        nxt = next((l for l in lines[i:] if l.strip()), "")
        if re.match(r"表\s*\d+", text) and nxt.lstrip().startswith("|"):
            pending_caption = text
        else:
            body.append(f"<p>{inline(text)}</p>")
    return title, "\n".join(body)


def list_html(items: list[str]) -> str:
    ordered = bool(re.match(r"\s*\d+\.", items[0]))
    tag = "ol" if ordered else "ul"
    out, depth = [f"<{tag}>"], 0
    for ln in items:
        indent = len(ln) - len(ln.lstrip())
        text = re.sub(r"^\s*([-*]|\d+\.)\s+", "", ln)
        if indent >= 2 and depth == 0:
            out.append(f"<{tag}>")
            depth = 1
        elif indent < 2 and depth == 1:
            out.append(f"</{tag}>")
            depth = 0
        out.append(f"<li>{inline(text)}</li>")
    if depth:
        out.append(f"</{tag}>")
    out.append(f"</{tag}>")
    return "".join(out)


def table_html(header: list[str], rows: list[list[str]], caption: str | None) -> str:
    align = showcase.column_alignments(header, rows)
    cls = {"l": "l", "c": "c", "r": "r"}
    head = "".join(f'<th scope="col" class="{cls[a]}">{E(h)}</th>' for h, a in zip(header, align))
    body = []
    for r in rows:
        total = r[0].strip() in ("合计", "总计", "小计")
        cells = "".join(f'<td class="{cls[a]}">{inline(c)}</td>' for c, a in zip(r, align))
        body.append(f'<tr class="total">{cells}</tr>' if total else f"<tr>{cells}</tr>")
    cap = f"<caption>{inline(caption)}</caption>" if caption else ""
    return f'<div class="tw"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def page(title: str, theme: str, body: str) -> str:
    t = T.theme_tokens(theme)
    css = f"""
{md_type_block()}
:root {{ color-scheme: light; --line: {t['line']}; --ink: {t['ink']}; --muted: {t['ink2']}; --head: {t['head']}; --head-ink: {t['headInk']}; --press: {t['lead']}; }}
@page {{ size: A4; margin: 18mm 18mm 20mm; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #fff; color: var(--ink); font-family: "Microsoft YaHei"; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
main {{ max-width: 174mm; margin: 0 auto; padding: 32px 24px 48px; }}
h1, h2, h3 {{ color: var(--ink); break-after: avoid; }}
h2 {{ border-bottom-color: var(--line); }}
h3 {{ color: var(--press); }}
ul, ol, p {{ max-width: none; }}
.tw {{ margin: 0 0 20px; break-inside: avoid; }}
table {{ width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
caption {{ caption-side: top; text-align: center; color: var(--muted); }}
th, td {{ padding: 8px 14px; vertical-align: middle; border-bottom: 1px solid var(--line); }}
thead th {{ background: var(--head); color: var(--head-ink); text-align: center; font-weight: 600; }}
tbody tr:last-child td {{ border-bottom: 0; }}
td.c {{ text-align: center; }} td.l {{ text-align: left; }} td.r {{ text-align: right; padding-right: 28px; white-space: nowrap; font-variant-numeric: tabular-nums; }}
thead th {{ white-space: nowrap; }}
tr.total td {{ font-weight: 600; background: #FAFAFA; }}
td, th, p, li {{ word-break: keep-all; text-wrap: pretty; }}
@media screen {{ main {{ margin: 32px auto; }} }}
"""
    return (f'<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{E(title)}</title>\n<link rel="icon" href="{T.icon(t)}">\n<style>{css}</style>\n</head>\n<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n')


def export_pdf(src: Path, pdf: Path, ink2: str) -> None:
    from playwright.sync_api import sync_playwright
    footer = (f'<div style="width:100%;text-align:center;font-size:12px;color:{ink2};font-family:\'Microsoft YaHei\'">'
              f'<span class="pageNumber"></span></div>')
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch()
        pg = browser.new_page()
        pg.goto(src.resolve().as_uri())
        pg.wait_for_load_state("networkidle")
        pg.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True, outline=True, tagged=True,
               display_header_footer=True, header_template="<div></div>", footer_template=footer)
        browser.close()


def build(spec_path: Path, pdf: Path, work: Path | None = None) -> int:
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    source = (spec_path.parent / spec["source"]).resolve()
    work = work or pdf.parent
    work.mkdir(parents=True, exist_ok=True)
    rc = check_document.main([str(source)])
    md = source.read_text(encoding="utf-8")
    segment_words(md, spec.get("keep_together", []))
    title, body = convert(md)
    if title != spec.get("title", title):
        print("WARN spec title differs from the Markdown title")
    src = work / (pdf.stem + ".html")
    src.write_text(page(title, spec["theme"], body), encoding="utf-8")
    rc |= check_document.main([str(src)])
    export_pdf(src, pdf, T.theme_tokens(spec["theme"])["ink2"])
    errors = T.check_pdf(pdf, spec.get("max_pages"))
    for e in errors:
        print("ERROR", e)
    return int(bool(rc or errors))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec", type=Path)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--work", type=Path, help="过程文件（HTML 与总览图）目录，默认与 PDF 同目录")
    args = ap.parse_args(argv)
    return build(args.spec, args.pdf, args.work)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
