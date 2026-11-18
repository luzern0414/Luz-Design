#!/usr/bin/env python3
"""导出海报模板为 PNG 或 PDF。

用法：
  py -X utf8 scripts/export_poster.py <poster.html> <out.png|out.pdf> [--scale 2] [--theme rose] [--bleed]

- 以 ?export=1 加载，去掉预览缩放与外框，画布大小取自 data-size（像素）。
- PNG 按 --scale 放大导出；PDF 按画布尺寸只出一页。
- --theme 取 rose coral orange green teal blue purple graphite，默认沿用海报自己的主题。
- --bleed 只用于带出血的印刷版（课程招生、招聘招募）：画布外扩三毫米出血，导出尺寸以实际画布为准。
依赖：python 的 playwright 与本机 Edge。
"""
import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

THEMES = ['rose', 'coral', 'orange', 'green', 'teal', 'blue', 'purple', 'graphite']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('poster', help='海报 html 文件')
    ap.add_argument('out', help='输出文件，.png 或 .pdf')
    ap.add_argument('--scale', type=float, default=2, help='PNG 放大倍数，默认 2')
    ap.add_argument('--theme', choices=THEMES, help='主题色')
    ap.add_argument('--bleed', action='store_true', help='导出带三毫米出血的印刷版')
    ap.add_argument('--wait', type=int, default=600, help='加载后等待毫秒数，默认 600')
    a = ap.parse_args()

    src = Path(a.poster).resolve()
    out = Path(a.out).resolve()
    if not src.is_file():
        sys.exit(f'找不到海报文件 {src}')
    ext = out.suffix.lower()
    if ext not in ('.png', '.pdf'):
        sys.exit('输出文件必须是 .png 或 .pdf')
    out.parent.mkdir(parents=True, exist_ok=True)

    query = ['export=1']
    if a.theme:
        query.append('theme=' + a.theme)
    if a.bleed:
        query.append('bleed=1')
    url = src.as_uri() + '?' + '&'.join(query)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge')
        ctx = browser.new_context(viewport={'width': 1200, 'height': 900},
                                  device_scale_factor=a.scale if ext == '.png' else 1)
        page = ctx.new_page()
        problems = []
        page.on('console', lambda m: problems.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: problems.append(f'pageerror: {e}'))
        page.on('requestfailed', lambda r: problems.append(f'requestfailed: {r.url}'))
        page.goto(url)
        page.wait_for_selector('[data-cid]')
        size = page.evaluate("document.querySelector('[data-cid]').dataset.size")
        m = re.match(r'(\d+)\s*[×x]\s*(\d+)$', size or '')
        if not m:
            sys.exit(f'data-size 格式不对：{size}')
        w, h = int(m.group(1)), int(m.group(2))
        # 先按 data-size 放大视口，再以实际画布为准（出血版会比 data-size 略大）
        page.set_viewport_size({'width': w + 64, 'height': h + 64})
        page.evaluate('document.fonts && document.fonts.ready')
        page.wait_for_function("Array.from(document.images).every(i => i.complete)")
        page.wait_for_timeout(a.wait)
        box = page.evaluate("(() => { const r = document.querySelector('[data-cid]').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()")
        cw, ch = box[2], box[3]
        if ext == '.png':
            page.screenshot(path=str(out), clip={'x': box[0], 'y': box[1], 'width': cw, 'height': ch})
        else:
            page.pdf(path=str(out), width=f'{cw:.2f}px', height=f'{ch:.2f}px', print_background=True,
                     prefer_css_page_size=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'},
                     page_ranges='1')
        browser.close()

    for line in problems:
        print('提示', line)
    print(f'已导出 {out}  画布 {cw:.0f}×{ch:.0f} 像素' + (f'  放大 {a.scale} 倍' if ext == '.png' else ''))


if __name__ == '__main__':
    main()
