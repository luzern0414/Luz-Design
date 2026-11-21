from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

RULES = Path(__file__).with_name('application_state_rules.js').read_text(encoding='utf8')
INTERACTION_RULES = Path(__file__).with_name('audit_ui_rules.js').read_text(encoding='utf8')


@pytest.fixture(scope='module')
def page():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge',headless=True)
        yield browser.new_page(viewport={'width':1100,'height':800})
        browser.close()


def scan(page, html):
    page.set_content('<html><style>body,main,nav,aside{background:#fff}body{margin:0;color:#222}label{display:block}</style><body>'+html+'</body></html>')
    return {row['rule'] for row in page.evaluate(RULES)}


@pytest.mark.parametrize('html,rule',[
    ('<button style="background:#eefaf1">完成</button>','green-interface-color'),
    ('<span style="color:teal">状态</span>','green-interface-color'),
    ('<button style="background:linear-gradient(20deg,#fff,mediumseagreen)">提交</button>','green-interface-color'),
    ('<svg><path stroke="green" d="M2 2 L40 40"/></svg>','green-interface-color'),
    ('<svg><defs><linearGradient id="g"><stop stop-color="green"/></linearGradient></defs><rect fill="url(#g)" width="50" height="50"/></svg>','green-interface-color'),
    ('<canvas id="c"></canvas><script>let ctx=c.getContext("2d");ctx.fillStyle="teal";ctx.fillRect(0,0,200,120)</script>','green-interface-color'),
    ('<div style="position:fixed;bottom:0;width:100%;height:48%;z-index:5"><input aria-label="数量"></div>','business-or-edge-overlay'),
    ('<div style="position:fixed;right:0;top:0;width:400px;height:100%"><p>订单详情</p></div>','business-or-edge-overlay'),
    ('<dialog open style="position:fixed;inset:0;margin:auto"><form><input></form></dialog>','business-or-edge-overlay'),
    ('<button aria-controls="bar" aria-expanded="true">导航</button><aside id="bar" style="position:fixed;left:0;top:0;height:100%;width:240px"><nav><button>订单</button></nav></aside>','business-or-edge-overlay'),
    ('<span class="avatar">YM</span>','graphical-avatar-required'),
    ('<span class="icon">★</span>','text-icon'),
    ('<main style="background:#f7f8fd"><h1>订单</h1></main>','nonwhite-background'),
    ('<style>body:before{content:"";position:fixed;inset:0;background:#ddeaff}</style><button>进入</button>','nonwhite-background'),
])
def test_blocked_state(page,html,rule):
    assert rule in scan(page,html)


@pytest.mark.parametrize('html',[
    '<aside id="sidebar" style="position:fixed;left:0;top:0;height:100%;width:220px"><nav><button>订单</button></nav></aside><main style="margin-left:220px">发运</main>',
    '<main><h1>新建订单</h1><form><label>数量<input type="number"></label><button>提交</button></form></main>',
    '<button style="background:#1656b2;color:white">保存</button><span class="avatar"><svg width="24" height="24"><path d="M1 2L10 9" stroke="#456"/></svg></span>',
    '<button role="combobox" aria-controls="choices" aria-expanded="true" style="height:28px">仓库</button><ul role="listbox" id="choices" popover style="position:absolute;inset:auto;margin:0;top:28px;left:0"><li role="option">华东</li></ul><script>choices.showPopover()</script>',
    '<button onclick="document.querySelector(\'main\').innerHTML=\'<h1>详情</h1>\'">打开</button><main>详细单据</main>',
    '<img alt="田野" data-product-image src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'30\' height=\'30\'%3E%3Crect fill=\'green\' width=\'30\' height=\'30\'/%3E%3C/svg%3E">',
])
def test_allowed_state(page,html):
    assert scan(page,html)==set()


def test_selected_tab_landing_content_after_click(page):
    page.set_content("""
      <nav role="tablist">
        <button role="tab" aria-selected="true" aria-controls="tasks">待办</button>
        <button role="tab" aria-selected="false" aria-controls="kb">知识库</button>
      </nav>
      <main>
        <section id="tasks" role="tabpanel"><button>新建任务</button></section>
        <section id="kb" role="tabpanel" aria-label="知识库" hidden>
          <header><h1>知识库管理</h1><p>在这里统一管理资料</p></header>
          <input type="search" aria-label="搜索资料"><button>新建知识库</button>
          <article><h2>采购合同</h2></article>
        </section>
      </main>
      <script>
        const tabs = [...document.querySelectorAll('[role=tab]')];
        for (const tab of tabs) tab.onclick = () => {
          for (const item of tabs) {
            item.setAttribute('aria-selected', String(item === tab));
            document.getElementById(item.getAttribute('aria-controls')).hidden = item !== tab;
          }
        };
      </script>
    """)

    def findings():
        return [item['text'] for item in page.locator('html').evaluate(INTERACTION_RULES, [])['violations']
                if item['rule'] == 'tab-landing-header-copy']

    assert findings() == []
    page.get_by_role('tab', name='知识库').click()
    assert findings() == ['知识库管理', '在这里统一管理资料']
    page.locator('#kb header').evaluate('header => header.remove()')
    assert page.get_by_role('searchbox', name='搜索资料').is_visible()
    assert page.get_by_role('button', name='新建知识库').is_visible()
    assert findings() == []


@pytest.mark.parametrize('kind,cases', [
    ('app', [
        ('AP-FEED-027','.fedx-gv__th','.fedx-vw','[data-x]'),
        ('AP-FEED-028','[data-list] [data-k]','[data-scrim]','[data-x]'),
    ]),
    ('web', [
        ('WB-CARD-042','.wb-cd-pv__th','.wb-cd-pv__mask','[data-act=close]'),
        ('WB-FEED-022','#fb-dg-list [data-i]','#fb-dg-mask','[data-close]'),
    ]),
])
def test_shipped_gallery_routes(page,kind,cases):
    root=Path(__file__).resolve().parents[1]
    page.goto((root/'templates'/kind/(kind+'.html')).as_uri())
    page.locator('[data-tab=components]').click()
    frame=page.frame_locator('#panel-components iframe')
    for component,entry,details,back in cases:
        frame.locator('#q').fill(component)
        sample=frame.locator(f'[data-cid="{component}"]')
        trigger=sample.locator(entry).first
        view=sample.locator(details)
        trigger.click()
        assert view.is_visible() and not trigger.is_visible()
        assert view.evaluate("el=>!['fixed','absolute'].includes(getComputedStyle(el).position)")
        assert view.locator('[role=dialog],dialog,[aria-modal=true]').count()==0
        view.locator(back).click()
        assert trigger.is_visible() and not view.is_visible()

@pytest.mark.parametrize('vendor,classes', [
    ('element-plus','el-button el-button--success'),
    ('vant','van-button van-button--success van-button--normal'),
])
def test_framework_success_states(page,vendor,classes):
    kit=Path(__file__).resolve().parents[1]/'kit/frontend'
    vendor_css=(kit/'vendor'/f'{vendor}.css').read_text(encoding='utf8')
    interaction=(kit/'shared'/'interaction.css').read_text(encoding='utf8')
    palette=(kit/'shared'/'pastel-300.css').read_text(encoding='utf8')
    interaction=interaction.replace('@import url("pastel-300.css");',palette)
    page.set_content(f'<html lang="zh"><head><style>{vendor_css}\n{interaction}</style></head>'
                     f'<body><main><button class="{classes}">提交成功</button></main></body></html>')
    button=page.get_by_role('button',name='提交成功')
    for action in (None,button.hover,button.focus):
        if action:
            action()
        assert page.evaluate(RULES)==[]
