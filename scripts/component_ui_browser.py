"""Execute the declared UI journeys in Edge and retain current render evidence.

This proves observed prototype behavior only. It cannot establish source
licensing, production integration, subjective quality or human authorization.
"""
from __future__ import annotations
from pathlib import Path
import contextlib
import math
import struct
import threading
import time
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import unquote,urlsplit,quote
import component_reuse as reuse

APPLICATION_RULES = Path(__file__).with_name("application_state_rules.js")
RENDER_TIMEOUT_MS = 10000


class _Static(SimpleHTTPRequestHandler):
    """Serve the package folder read-only under /output/ on a loopback port."""
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args): pass

    def translate_path(self, path):
        parts = unquote(urlsplit(path).path).lstrip('/').split('/')
        root = self.server.mount
        if len(parts) < 2 or parts[0] != 'output' or any(p in {'..', '.'} or chr(92) in p for p in parts):
            return str(root / '__not_found__')
        target = root.joinpath(*parts[1:]).resolve()
        return str(target if target.is_relative_to(root) else root / '__not_found__')


@contextlib.contextmanager
def serve(source: Path, output: Path):
    server = ThreadingHTTPServer(('127.0.0.1', 0), _Static)
    server.mount = output.resolve()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try: yield f'http://127.0.0.1:{server.server_address[1]}'
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3)

RENDER_STABLE_MS = 300

# Observe the upstream runtime. Do not finish/cancel animations, change styles,
# or treat Playwright's opacity-insensitive visibility as rendered evidence.
RENDER_STATE = r"""() => {
 const active=document.getAnimations().filter(a=>a.pending || a.playState==='running');
 const ongoing=active.filter(a=>a.effect && a.effect.getComputedTiming().endTime===Infinity);
 const movingRoots=ongoing.map(a=>a.effect.target).filter(e=>e instanceof Element);
 // Ongoing cosmetic animation may keep painting. Its stable surrounding
 // layout and the explicit visible targets are still measured separately.
 const elements = [...document.querySelectorAll('body, body *')].filter(e => !['SCRIPT','STYLE','TEMPLATE','NOSCRIPT'].includes(e.tagName) && !movingRoots.some(root=>root===e || root.contains(e)));
 const styles = ['display','visibility','opacity','transform','filter','color','background-color','font-family','font-size','font-weight','line-height','border-color','box-shadow'];
 const boxes = elements.map(e => { const s=getComputedStyle(e),r=e.getBoundingClientRect();
  return [e.tagName,[r.x,r.y,r.width,r.height],styles.map(p=>s.getPropertyValue(p)),e.childElementCount ? null : e.textContent]; });
 const images = [...document.images].filter(e => { const r=e.getBoundingClientRect(),s=getComputedStyle(e);
  return r.width>0 && r.height>0 && s.display!=='none' && s.visibility!=='hidden'; });
 return {fonts:document.fonts.status,
  active_animations:active.length-ongoing.length,ongoing_animations:ongoing.length,
  pending_images:images.filter(e=>!e.complete).length,
  broken_images:images.filter(e=>e.complete && e.currentSrc && e.naturalWidth===0).length,
  boxes:[...boxes,['document',document.documentElement.scrollWidth,document.documentElement.scrollHeight]]};
}"""

RENDER_TARGETS = r"""els => els.map(e => {
 const ownStyle=getComputedStyle(e);
 let opacity=1,shown=ownStyle.visibility!=='hidden' && ownStyle.visibility!=='collapse';
 let scaleX=1,scaleY=1;
 for(let p=e;p;p=p.parentElement){ const s=getComputedStyle(p); opacity*=Number(s.opacity);
  shown=shown && s.display!=='none';
  if(s.transform!=='none'){const m=new DOMMatrixReadOnly(s.transform);
   scaleX*=Math.hypot(m.m11,m.m12,m.m13);scaleY*=Math.hypot(m.m21,m.m22,m.m23);} }
 const r=e.getBoundingClientRect();
 const round=(n,d)=>Math.round(n*d)/d;
 const visualCycle=document.getAnimations().some(a=>{
  if(!a.effect || a.effect.getComputedTiming().endTime!==Infinity || !(a.pending || a.playState==='running'))return false;
  const root=a.effect.target;
  return root instanceof Element && (root===e || root.contains(e)) && a.effect.getKeyframes().some(k=>
   (k.opacity!==undefined && Number(k.opacity)<=0) || ['hidden','collapse'].includes(k.visibility) || k.display==='none');
 });
 return {shown:shown && r.width>0 && r.height>0,effective_opacity:opacity,visibility_cycle:visualCycle,
  layout:[round(r.x+r.width/2,100),round(r.y+r.height/2,100),e.offsetWidth ?? r.width,e.offsetHeight ?? r.height,round(scaleX,10000),round(scaleY,10000)]};
})"""


def wait_render_ready(page, locators=()):
    """Require loaded resources, settled finite animation and stable targets.

    A condition poll has a bounded deadline. Permanent transparent expected
    content and a runtime that never settles fail instead of producing a pass.
    Ongoing animation is observed, not disabled; a stable spinner can remain.
    Locator checks happen at the assertion's state, not after later actions
    that may intentionally hide or replace that content.
    """
    started=time.monotonic();changed_at=started;previous=None;samples=0;last=None
    while (time.monotonic()-started)*1000 < RENDER_TIMEOUT_MS:
        state=page.evaluate(RENDER_STATE)
        targets=[locator.evaluate_all(RENDER_TARGETS) for locator in locators]
        fingerprint=reuse.stable({'boxes':state.pop('boxes'),'targets':targets})
        now=time.monotonic();samples+=1
        last={**state,'visible_target_count':len(targets),
              'visibility_cycle_targets':sum(any(row['visibility_cycle'] for row in rows) for rows in targets),'effective_opacities':
              [rows[0]['effective_opacity'] if len(rows)==1 else None for rows in targets]}
        ready=(state['fonts']=='loaded' and state['active_animations']==0
               and state['pending_images']==0 and state['broken_images']==0
               and all(len(rows)==1 and rows[0]['shown'] and rows[0]['effective_opacity']>0 and not rows[0]['visibility_cycle'] for rows in targets))
        if not ready or fingerprint!=previous:
            changed_at=now;previous=fingerprint
        if ready and (now-changed_at)*1000 >= RENDER_STABLE_MS:
            return {'status':'ready',**last,'stable_ms':int((now-changed_at)*1000),
                    'observed_ms':int((now-started)*1000),'samples':samples}
        page.wait_for_timeout(50)
    raise ValueError(f'Render readiness timed out after {RENDER_TIMEOUT_MS}ms: {last}')


def _final_visible_specs(steps):
    visible={}
    for step in steps:
        op=step['op']
        if op in {'reload','click','fill','press','select'}: visible.clear()
        elif op=='expect_visible': visible[reuse.stable(step['locator'])]=step['locator']
        elif op=='expect_hidden' or (op=='expect_count' and step['value']==0):
            visible.pop(reuse.stable(step['locator']),None)
    return list(visible.values())


def _locator(page,spec):
    if spec.get('label'): return page.get_by_label(spec['label'],exact=True)
    options = {'name':spec['name'], 'exact':True}
    for state in ('checked', 'pressed', 'selected'):
        if state in spec:
            reuse.need(type(spec[state]) is bool, 'Locator state must be a boolean')
            options[state] = spec[state]
    return page.get_by_role(spec['role'],**options)


def run(plan,package,session):
    from playwright.sync_api import sync_playwright,expect
    from component_ui import RECEIPT
    package,session=Path(package).resolve(),Path(session).resolve()
    receipt_hash=reuse.digest(package/RECEIPT)
    folder=session/'raw/02-visual'/('components-'+receipt_hash[:16])
    folder.mkdir(parents=True,exist_ok=True)
    application_rules=APPLICATION_RULES.read_text(encoding="utf8")
    entries={p['id']:p['entry'] for p in plan['pages']}
    report={'schema':'luz-component-browser/1','package':str(package),'receipt_sha256':receipt_hash,
            'auditor_sha256':reuse.digest(__file__),'application_rules_sha256':reuse.digest(APPLICATION_RULES),'plan_sha256':reuse.stable(plan),
            'browser':'chromium/msedge','cases':[],'errors':[],
            'scope':'Isolated local web prototype. No external API, native platform or production service is accepted.'}
    with serve(package,package) as base,sync_playwright() as playwright:
        browser=playwright.chromium.launch(channel='msedge',headless=True)
        try:
            for width in plan['framework']['breakpoints']:
                for case in plan['cases']:
                    context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
                    # Reused upstream components must not call a real service
                    # merely because a prototype journey is being exercised.
                    context.route('**/*',lambda route: route.continue_() if urlsplit(route.request.url).netloc==urlsplit(base).netloc else route.abort())
                    page=context.new_page();page.set_default_timeout(10000)
                    item={'id':case['id'],'width':width,'steps':[],'errors':[]}
                    page.on('pageerror',lambda error,row=item:row['errors'].append(str(error)))
                    page.on('response',lambda response,row=item:row['errors'].append(f'HTTP {response.status}: {response.url}') if response.status>=400 and not response.url.endswith('/favicon.ico') else None)
                    page.on('requestfailed',lambda request,row=item:row['errors'].append('Resource failed: '+request.url))
                    try:
                        page.goto(base+'/output/'+quote(entries[case['page_id']],safe='/'),wait_until='load')
                        wait_render_ready(page)
                        reuse.need(not (issues := page.evaluate(application_rules)), f"Initial application state: {issues}")
                        for index,step in enumerate(case['steps']):
                            op=step['op']
                            reuse.need(op in {'reload','click','fill','press','select','expect_text','expect_value','expect_visible','expect_hidden','expect_count'},'Unknown browser operation')
                            if op=='reload':
                                page.reload(wait_until='load')
                                wait_render_ready(page)
                            else:
                                locator=_locator(page,step['locator'])
                                if op=='click': locator.click()
                                elif op=='fill': locator.fill(step['value'])
                                elif op=='press': locator.press(step['value'])
                                elif op=='select': locator.select_option(step['value'])
                                elif op=='expect_text': expect(locator).to_have_text(step['value'])
                                elif op=='expect_value': expect(locator).to_have_value(step['value'])
                                elif op=='expect_visible':
                                    expect(locator).to_be_visible()
                                    wait_render_ready(page,[locator])
                                elif op=='expect_hidden': expect(locator).to_be_hidden()
                                elif op=='expect_count': expect(locator).to_have_count(step['value'])
                            if op in {'click','fill','press','select','reload'}:
                                wait_render_ready(page)
                                reuse.need(not (issues := page.evaluate(application_rules)), f"Application state after {op}: {issues}")
                            item['steps'].append({'index':index,'op':op,'action_id':step.get('action_id'),'component_id':step.get('component_id'),'completed':True})
                        item['render_ready']=wait_render_ready(page,[_locator(page,s) for s in _final_visible_specs(case['steps'])])
                        overflow=page.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')
                        item['horizontal_overflow']=overflow
                        if overflow>1: item['errors'].append(f'Document overflows viewport by {overflow}px')
                    except Exception as exc:
                        item['errors'].append(f'{type(exc).__name__}: {exc}')
                    finally:
                        image=folder/f'{len(report["cases"]):04d}-{width}.png'
                        try:
                            page.screenshot(path=str(image),full_page=True)
                            item['screenshot']={'path':str(image),'sha256':reuse.digest(image)}
                            item['semantic_snapshot']=page.locator('body').aria_snapshot()
                        except Exception as exc:
                            item['errors'].append(f'Evidence capture: {exc}')
                        report['cases'].append(item)
                        report['errors'] += [f'{case["id"]}@{width}: {e}' for e in item['errors']]
                        context.close()
        finally: browser.close()
    return report


def check_report(report,plan,package,session):
    from component_ui import RECEIPT,inside
    reuse.need(isinstance(report,dict) and report.get('schema')=='luz-component-browser/1'
               and report.get('browser')=='chromium/msedge'
               and report.get('package')==str(Path(package).resolve())
               and report.get('receipt_sha256')==reuse.digest(Path(package)/RECEIPT)
               and report.get('plan_sha256')==reuse.stable(plan)
               and report.get('auditor_sha256')==reuse.digest(__file__)
               and report.get('application_rules_sha256')==reuse.digest(APPLICATION_RULES)
               and report.get('errors')==[], 'Current browser report does not match the package, plan or auditor')
    cases={c['id']:c for c in plan['cases']}
    expected={(identifier,width) for identifier in cases for width in plan['framework']['breakpoints']}
    seen=set()
    reuse.need(isinstance(report.get('cases'),list),'Browser cases must be an array')
    for row in report.get('cases',[]):
        reuse.need(isinstance(row,dict) and type(row.get('width')) is int,'Browser case must have an integer viewport')
        key=(row.get('id'),row.get('width'))
        reuse.need(key in expected and key not in seen and row.get('errors')==[],'Missing, duplicate or failed browser case')
        seen.add(key)
        steps=cases[row['id']]['steps']
        expected_steps=[{'index':i,'op':s['op'],'action_id':s.get('action_id'),'component_id':s.get('component_id'),'completed':True} for i,s in enumerate(steps)]
        reuse.need(row.get('steps')==expected_steps and all(s.get('completed') is True for s in row['steps']),'Browser case did not execute every declared step')
        ready=row.get('render_ready')
        target_count=len(_final_visible_specs(steps))
        reuse.need(isinstance(ready,dict) and ready.get('status')=='ready' and ready.get('fonts')=='loaded'
                   and all(type(ready.get(k)) is int and ready[k]==0 for k in ('active_animations','pending_images','broken_images','visibility_cycle_targets'))
                   and type(ready.get('ongoing_animations')) is int and ready['ongoing_animations']>=0
                   and type(ready.get('visible_target_count')) is int and ready['visible_target_count']==target_count
                   and isinstance(ready.get('effective_opacities'),list) and len(ready['effective_opacities'])==target_count
                   and all(type(x) in (int,float) and math.isfinite(x) and 0<x<=1 for x in ready['effective_opacities'])
                   and type(ready.get('stable_ms')) is int and ready['stable_ms']>=RENDER_STABLE_MS
                   and type(ready.get('observed_ms')) is int and ready['stable_ms']<=ready['observed_ms']<=RENDER_TIMEOUT_MS
                   and type(ready.get('samples')) is int and ready['samples']>=2,
                   'Browser render readiness evidence is missing or incomplete')
        reuse.need(type(row.get('horizontal_overflow')) in (int,float) and math.isfinite(row['horizontal_overflow']) and 0<=row['horizontal_overflow']<=1
                   and reuse.nonempty(row.get('semantic_snapshot')), 'Browser layout or semantic evidence is missing')
        image=row.get('screenshot');reuse.need(isinstance(image,dict),'Browser screenshot is missing')
        path=inside(image.get('path',''),Path(session)/'raw')
        reuse.need(path.suffix=='.png' and reuse.digest(path)==image.get('sha256'),'Browser screenshot missing or changed')
        header=path.read_bytes()[:24]
        reuse.need(len(header)==24 and header[:8]==b'\x89PNG\r\n\x1a\n' and header[12:16]==b'IHDR'
                   and struct.unpack('>II',header[16:24])[0]==row['width'], 'Screenshot is not a PNG for this viewport')
    reuse.need(seen==expected,'Browser coverage is incomplete')
