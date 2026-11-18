"""Formal UI admission is source-backed; these fixtures are never delivery evidence."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest

import ui_entry_policy as policy
from test_crawl_gate import ready_session




def write_page(session, name='reading.html', source=None):
    path = session / 'raw' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source or '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>交付结果</title></head><body><main data-artifact="document"><h1>交付结果</h1><section><h2>成果</h2><p>原稿与核验结果。</p></section></main></body></html>', encoding='utf-8')
    return path




def test_passive_reading_summary_and_code_examples_stay_documents(tmp_path):
    session = ready_session(tmp_path)
    page = write_page(session)
    assert policy.html_delivery_contract(page, session=session)['kind'] == 'reading'
    page.write_text(page.read_text(encoding='utf-8').replace('</section>', '<pre><code>&lt;button onclick="go()"&gt;示例&lt;/button&gt;</code></pre><a href="raw/history.html">历史记录</a></section>'), encoding='utf-8')
    assert policy.html_delivery_contract(page, session=session)['kind'] == 'reading'


@pytest.mark.parametrize('source', [
    '''<!doctype html><html><head><style>
    body{font-family:system-ui} nav{display:flex;gap:24px}
    .start{display:inline-block;padding:12px 24px;background:#1769aa;color:white}
    </style></head><body><nav><a href="features.html">功能</a><a href="pricing.html">价格</a></nav>
    <main><h1>团队订单管理</h1><section><h2>从接单到履约</h2><p>让团队更快处理订单。</p>
    <a class="start" href="signup.html">立即开通</a></section></main></body></html>''',
    '''<html><body><h1>订单服务</h1><nav aria-label="主导航">
    <a href="#features">功能</a><a href="#pricing">价格</a></nav>
    <section id="features"><h2>功能</h2><p>接收与分配订单。</p></section>
    <section id="pricing"><h2>价格</h2><p>每月订阅。</p></section></body></html>''',
    '''<html><body><main><h1>团队订单管理</h1><p>快速开始处理门店订单。</p>
    <a href="/signup">Start your free trial</a></main></body></html>''',
    '''<html><head><style>a[href="signup.html"]{display:inline-flex;padding:16px;
    background:#1261a0;color:white;border-radius:8px}</style></head>
    <body><h1>订单服务</h1><a href="signup.html">继续</a></body></html>''',
    '''<html><head><style>.drawer{display:none}.drawer:target{display:block}</style></head>
    <body><h1>订单服务</h1><a href="#drawer">打开菜单</a><div id="drawer" class="drawer">
    <a href="orders.html">订单</a><a href="#">关闭</a></div></body></html>''',
    '''<html><head><style>.submenu{visibility:hidden}nav:hover .submenu{visibility:visible}</style></head>
    <body><h1>订单服务</h1><div class="menu">服务<div class="submenu">
    <a href="orders.html">订单</a></div></div></body></html>''',
    '''<html><head><style>.panel{display:none}.panel:target{display:block}</style></head><body>
    <h1>系统能力</h1><nav aria-label="目录"><a href="#reports">报表</a></nav>
    <section id="reports" class="panel"><h2>报表</h2><p>查看门店统计。</p></section></body></html>''',
])
def test_static_product_navigation_ctas_and_css_ui_need_source_admission(tmp_path, source):
    page = tmp_path / 'landing.html'
    page.write_text(source, encoding='utf-8')
    with pytest.raises(ValueError, match='frontend.py|component_ui.py'):
        policy.html_delivery_contract(page)


def test_real_reading_toc_tables_and_citations_remain_documents(tmp_path):
    page = tmp_path / 'research.html'
    page.write_text('''<!doctype html><html><head><style>
    body{font-family:system-ui}main{max-width:760px;margin:auto}table{border-collapse:collapse}
    h2:target{background:#e9f2f5}nav a:hover{color:#1261a0}
    </style></head><body><main><h1>门店订单调研</h1>
    <nav aria-label="目录"><ol><li><a href="#scope">研究范围</a></li>
    <li><a href="#findings">调研结论</a></li></ol></nav>
    <section id="scope"><h2>研究范围</h2><p>调查三家门店。
    <a href="https://example.org/methodology">调查方法 [1]</a></p></section>
    <section><h2 id="findings">调研结论</h2><table><caption>表 1 结果</caption>
    <thead><tr><th>门店</th><th>发现</th></tr></thead><tbody><tr><td>一店</td>
    <td><a href="raw/interview.md">访谈记录</a></td></tr></tbody></table>
    <pre><code>&lt;input type="checkbox"&gt; 示例，不是界面</code></pre>
    </section></main></body></html>''', encoding='utf-8')
    assert policy.html_delivery_contract(page)['kind'] == 'reading'


def test_document_label_cannot_turn_product_links_into_a_table_of_contents(tmp_path):
    page = tmp_path / 'fake-toc.html'
    page.write_text('''<html><body><main data-artifact="document"><h1>说明</h1>
    <nav aria-label="目录"><a href="signup.html">开通</a><a href="#missing">功能</a></nav>
    <section id="features"><h2>功能</h2><p>管理订单。</p></section></main></body></html>''', encoding='utf-8')
    with pytest.raises(ValueError, match='frontend.py|component_ui.py'):
        policy.html_delivery_contract(page)


def test_supported_summary_and_article_skeletons_keep_reading_admission(tmp_path):
    from make_summary import render
    page = tmp_path / 'summary.html'
    page.write_text(render({'title': '核验结果', 'sections': [{'title': '成果', 'text': '本次核验已记录。',
                    'table': {'caption': '表 1 清单', 'columns': ['文件', '用途'], 'rows': [['report.pdf', '留档']]}}]}), encoding='utf-8')
    assert policy.html_delivery_contract(page)['kind'] == 'reading'
    template = (Path(__file__).resolve().parents[1] / 'templates/documents/reading/writing-article.html').read_text(encoding='utf-8')
    template = template.replace('{{TITLE}}', '门店访谈').replace('{{ICON}}', '').replace('{{EXTRA_CSS}}', '')
    template = template.replace('{{EXTRA_HTML}}', '').replace('{{BODY}}', '<h2>调查范围</h2><p>访谈记录与来源。</p>')
    page.write_text(template, encoding='utf-8')
    assert policy.html_delivery_contract(page)['kind'] == 'reading'


def test_reading_toc_can_link_to_a_get_started_heading_and_plain_citations(tmp_path):
    page = tmp_path / 'guide.html'
    page.write_text('''<html><head><style>.toc a{display:block;padding:8px;background:#eef3f5}</style></head>
    <body><h1>调查使用指南</h1><nav class="toc"><a href="#start">开始使用</a></nav>
    <section id="start"><h2>开始使用</h2><p>先阅读
    <a href="https://example.org/docs/signup">Sign up API reference</a>。
    所有表单示例均为资料引用。</p></section></body></html>''', encoding='utf-8')
    assert policy.html_delivery_contract(page)['kind'] == 'reading'


@pytest.mark.parametrize('stylesheet', [
    '.sheet{display:none}.sheet:target{display:block}',
    r'.sheet{display:none}.sheet:\74 arget{display:block}',
    '.sheet{display:var(--open,none)}.sheet:target{--open:block}',
    '@import "controls.css";',
])
def test_linked_css_cannot_hide_an_interactive_surface(tmp_path, stylesheet):
    page = tmp_path / 'page.html'
    page.write_text('''<html><head><link rel="stylesheet" href="page.css"></head><body>
    <h1>说明</h1><a href="#sheet">查看内容</a><div class="sheet" id="sheet">订单入口</div>
    </body></html>''', encoding='utf-8')
    (tmp_path / 'page.css').write_text(stylesheet, encoding='utf-8')
    (tmp_path / 'controls.css').write_text('.sheet:target{display:block}', encoding='utf-8')
    with pytest.raises(ValueError, match='frontend.py|component_ui.py'):
        policy.html_delivery_contract(page)


def test_native_disclosure_navigation_is_ui_without_a_script_or_form(tmp_path):
    page = tmp_path / 'page.html'
    page.write_text('''<html><body><h1>门店服务</h1><details><summary>服务菜单</summary>
    <a href="orders.html">订单</a><a href="billing.html">账单</a></details></body></html>''', encoding='utf-8')
    with pytest.raises(ValueError, match='frontend.py|component_ui.py'):
        policy.html_delivery_contract(page)


@pytest.mark.parametrize('snippet', [
    '<script>document.body.innerHTML="product"</script>',
    '<script src="app.js"></script>',
    '<button>自造组件</button>',
    '<div role="button">自造控件</div>',
    '<form><input name="name"></form>',
    '<a href="jav&#97;script:go()">进入</a>',
    '<div onclick="go()">进入</div>',
    '<iframe srcdoc="&lt;button&gt;界面&lt;/button&gt;"></iframe>',
    '<iframe src="data:text/html,ui"></iframe>',
    '<object data="app.html"></object>',
    '<meta http-equiv="refresh" content="0;url=ui.html">',
    '<main data-ui-runtime="vant"></main>',
    '<section data-cid="MP-BASE-001">内部组件</section>',
])
def test_unregistered_active_ui_cannot_become_a_reading_page_by_removing_markers(tmp_path, snippet):
    session = ready_session(tmp_path)
    page = write_page(session, source=f'<!doctype html><html><body><h1>说明</h1>{snippet}</body></html>')
    with pytest.raises(ValueError, match='frontend.py|component_ui.py'):
        policy.html_delivery_contract(page, session=session)


def test_declaring_an_interface_requires_admission_even_without_runtime_markers(tmp_path):
    session = ready_session(tmp_path)
    with pytest.raises(ValueError, match='frontend.py|界面包|component_ui.py'):
        policy.html_delivery_contract(write_page(session), session=session, allow=['interface'])






















def test_html_renamed_as_markdown_cannot_bypass_nonpage_delivery(tmp_path):
    session = ready_session(tmp_path)
    page = write_page(session, 'renamed.md', '<!doctype html><html><body><button>界面</button></body></html>')
    from deliver import deliver
    with pytest.raises(ValueError, match='HTML|页面|来源'):
        deliver(session, page)
    assert not (session / 'renamed.md').exists()


def test_zip_cannot_smuggle_an_unregistered_ui(tmp_path):
    session = ready_session(tmp_path)
    archive = session / 'raw' / 'legacy.zip'
    with zipfile.ZipFile(archive, 'w') as zipped:
        zipped.writestr('site/index.html', '<html><body><button>旧界面</button></body></html>')
        zipped.writestr('site/app.js', 'alert(1)')
    from deliver import deliver
    with pytest.raises(ValueError, match='frontend.py|界面包|component_ui.py'):
        deliver(session, archive)
    assert not (session / archive.name).exists()




def test_non_ui_archive_and_passive_image_delivery_are_unaffected(tmp_path):
    session = ready_session(tmp_path)
    archive = session / 'raw' / 'documents.zip'
    with zipfile.ZipFile(archive, 'w') as zipped:
        zipped.writestr('readme.md', '# 使用说明\n本文没有界面代码。')
    policy.check_nonpage_delivery(archive, session)
    image = session / 'raw' / 'mark.svg'
    image.write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4"/></svg>', encoding='utf-8')
    policy.check_nonpage_delivery(image, session)
