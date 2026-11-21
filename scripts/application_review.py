"""Replay local frontend journeys against the shared application-state rules."""
from pathlib import Path
from urllib.parse import quote, urlsplit

from component_ui_browser import APPLICATION_RULES, _locator, serve, wait_render_ready

INTERACTION_RULES = APPLICATION_RULES.with_name('audit_ui_rules.js')


def journeys_for(receipt, journeys):
    from frontend import need
    if journeys is None and receipt['kind'] in {'app-task', 'web-workspace'}:
        # Shipped templates have a known public journey. A customized package may supply its own.
        navigation_role = 'tab' if receipt['kind'] == 'app-task' else 'button'
        journeys = [{'entry': receipt['entries'][0], 'width': width, 'steps': [
            {'op':'click', 'role':navigation_role, 'name':'完成'},
            {'op':'click', 'role':navigation_role, 'name':'待办'},
            {'op':'click', 'role':'button', 'name':'新建任务'},
            {'op':'click', 'role':'button', 'name':'取消'}]} for width in (390, 1280)]
    need(isinstance(journeys,list) and journeys,'浏览器报告需提供 journeys：入口、实测视口和可重放的业务操作')
    for row in journeys:
        need(isinstance(row,dict) and row.get('entry') in receipt['entries']
             and type(row.get('width')) is int and row['width']>0 and isinstance(row.get('steps'),list)
             and row['steps'],'应用走查需指定有效入口、视口和业务步骤')
    need(set(receipt['entries'])=={r['entry'] for r in journeys},'应用走查需覆盖已登记的入口')
    return journeys


def check_states(value, receipt, journeys):
    from frontend import digest, need, stable
    plan=journeys_for(receipt, journeys)
    need(isinstance(value,dict) and value.get('rules_sha256')==digest(APPLICATION_RULES)
         and value.get('interaction_rules_sha256')==digest(INTERACTION_RULES)
         and value.get('bundle_sha256')==receipt['bundle_sha256'] and value.get('journeys_sha256')==stable(plan)
         and value.get('checked')==[1+len(r['steps']) for r in plan], '应用状态检查已过期，请按现有成品重新走查')


def audit_journeys(package, receipt, journeys):
    from frontend import digest, need, stable
    from playwright.sync_api import sync_playwright
    plan=journeys_for(receipt, journeys)
    source=APPLICATION_RULES.read_text(encoding='utf8')
    interaction=INTERACTION_RULES.read_text(encoding='utf8')
    def inspect(page, label):
        wait_render_ready(page)
        issues=page.evaluate(source)
        issues.extend(item for item in page.locator('html').evaluate(interaction, [])['violations']
                      if item['rule']=='tab-landing-header-copy')
        need(not issues, f'{label} 的应用成品检查失败：{issues[:8]}')
    with serve(package,package) as base, sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge',headless=True)
        try:
            for row in plan:
                context=browser.new_context(viewport={'width':row['width'],'height':844},reduced_motion='reduce')
                context.route('**/*', lambda req: req.continue_() if urlsplit(req.request.url).netloc==urlsplit(base).netloc else req.abort())
                page=context.new_page()
                page.set_default_timeout(5000)
                try:
                    page.goto(base+'/output/'+quote(row['entry'],safe='/'),wait_until='load')
                    inspect(page,row['entry'])
                    for step in row['steps']:
                        op=step.get('op')
                        need(op in {'click','fill','select','press','hover','focus'},'不支持的应用走查动作')
                        loc=_locator(page,step)
                        if op=='select':loc.select_option(step['value'])
                        elif op in {'fill','press'}:getattr(loc,op)(step['value'])
                        else:getattr(loc,op)()
                        inspect(page,step.get('name') or step.get('label'))
                finally:context.close()
        finally:browser.close()
    return {'rules_sha256':digest(APPLICATION_RULES),'bundle_sha256':receipt['bundle_sha256'],
            'interaction_rules_sha256':digest(INTERACTION_RULES),
            'journeys_sha256':stable(plan),'checked':[1+len(r['steps']) for r in plan]}
