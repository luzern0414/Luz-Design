"""Build editable frontends from mature components; verify bytes and real review evidence.

init app-task|web-workspace --session S --stage design
init existing --source DIST --sources SOURCES.json --entry index.html --session S --stage design
seal PACKAGE --session S
review PACKAGE --session S --file REVIEW.json
check PACKAGE --session S

Review records contain bundle_sha256, reviewer, observations [{viewport, finding,
screenshot:{path,sha256}}], interactions [{action,result,evidence:{path,sha256}}],
component_usage, limitations and blocking_findings. These records must be written
after actual observation, never manufactured by this script.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path, PurePosixPath
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'kit/frontend'
RECEIPT = 'luz-frontend.json'
REGISTRY = 'frontend_outputs'
HARD_RULES = ROOT / 'references/design/hard-rules.md'
QUALITY_RULES = ROOT.parent / 'Luz-Project/scripts/quality_rules.py'
REVIEW_RULES = frozenset({'form_page_and_notice_boundary','tab_ownership','hover_focus_hints',
    'in_place_edit','append_business_history','on_demand_form_actions',
    'meaningful_data_views','chart_missing_values','chart_touch_keyboard_values',
    'stable_unique_identities','adjacent_result_or_detail_page','restore_origin_context',
    'inline_wheel_manual_commit','bounded_business_period','role_owned_targets',
    'complete_period_data','no_duplicate_metrics','white_ui_backgrounds','graphical_avatars','no_text_icons'})


def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stable(d): return hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def need(v,message):
    if not v: raise ValueError(message)


def quality_module():
    need(QUALITY_RULES.is_file(),'Central quality rules runtime is required')
    spec=importlib.util.spec_from_file_location('luz_design_quality_rules',QUALITY_RULES)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def validate_quality(p,r,value):
    refs={}
    for key in ('browser_report','quality_assessment'):
        ref=value.get(key,{})
        path=member(p,ref.get('path')) if ref.get('path') else None
        need(path and path.is_file() and digest(path)==ref.get('sha256'),'Missing or changed '+key)
        refs[key]=path
    assessment=read(refs['quality_assessment'])
    need(assessment.get('scope')=={'owner':'luz-design','stage':'demo' if r.get('stage')=='demo' else 'design'},'Quality assessment has wrong owner/stage')
    need(assessment.get('receipt_sha256')==digest(Path(p)/RECEIPT),'Quality assessment describes a different sealed receipt')
    need(assessment.get('browser_report_sha256')==digest(refs['browser_report']),'Quality assessment describes a different browser report')
    report=read(refs['browser_report'])
    need(report.get('bundle_sha256')==r['bundle_sha256'],'Browser report describes different build bytes')
    need(report.get('observations') and report.get('limitations') is not None,'Browser report needs actual observations and limitations')
    q=quality_module()
    errors=q.check_assessment(assessment,q.read(q.CATALOG),q.digest(q.CATALOG),refs['quality_assessment'].parent)
    need(not errors,'Quality assessment failed: '+'; '.join(errors))


def member(root, name):
    need(isinstance(name,str) and name and '\\' not in name and ':' not in name,'Invalid relative member')
    rel=PurePosixPath(name)
    need(not rel.is_absolute() and '..' not in rel.parts and name==rel.as_posix(),'Unsafe package path')
    need(all(part not in {'.',''} and not part.endswith((' ','.')) and not re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?',part) for part in rel.parts),'Non-portable package member')
    p=Path(root)/name
    need(p.resolve().is_relative_to(Path(root).resolve()) and not p.is_symlink(),'Package member escapes root')
    return p


def tree(package, exclude_review=True):
    result={}
    for p in sorted(Path(package).rglob('*')):
        need(not p.is_symlink() and p.resolve().is_relative_to(Path(package).resolve()),'Linked members are not portable package members')
        if p.is_file():
            rel=p.relative_to(package).as_posix()
            if not exclude_review or (rel not in {RECEIPT,'review.json'} and not rel.startswith('evidence/')):
                result[rel]=digest(p)
    return result


def verify_sources(package):
    records=read(Path(package)/'component-sources.json')
    need(isinstance(records,list) and records,'Declare actual reused components')
    for c in records:
        need(all(isinstance(c.get(k),str) and c[k].strip() for k in ['name','version','source','usage']), 'Component needs name, version, source and actual usage')
        need(c['source'].startswith('https://'),'Component source must identify its public origin')
        need(c.get('files') and c.get('license') in c['files'],'Retain component code and license files')
        for name,sha in c['files'].items():
            p=member(package,name)
            need(p.is_file() and digest(p)==sha,'Component source bytes changed: '+name)
        need(any(not n.endswith('LICENSE') and n!=c['license'] for n in c['files']),'A license alone is not component reuse')
    return records


def verify_assets(package, *, optional=False):
    """Verify the provenance and actual bytes of each bundled image."""
    p=Path(package)
    manifest=p/'generated-assets.json'
    if optional and not manifest.is_file():
        return {'assets': []}
    data=read(manifest)
    schema = data.get('schema')
    need(schema in {'luz-generated-assets/1', 'luz-generated-assets/2'} and data.get('generator'),
         'Generated image provenance is required')
    sources=data.get('sources',[]);ids={s.get('id') for s in sources}
    need(sources and None not in ids and len(ids)==len(sources),'Generated sources must have unique IDs')
    for source in sources:
        if schema == 'luz-generated-assets/1':
            files = source.get('files', {})
            for suffix in ('original.png','response.json','invocation.json','prompt.txt'):
                need(any(name.endswith(suffix) for name in files), 'Retain original image, response, request and prompt')
            for name, expected in files.items():
                file = member(p, name)
                need(file.is_file() and digest(file) == expected, 'Generated source bytes changed: ' + name)
        else:
            original = source.get('original_sha256')
            need(isinstance(original, str) and re.fullmatch(r'[0-9a-f]{64}', original),
                 'Generated source needs the archived original SHA-256')
    assets=data.get('assets',[])
    need(bool(assets),'A generated asset receipt needs at least one asset')
    need(len({a.get('path') for a in assets})==len(assets),'Duplicate generated asset path')
    for asset in assets:
        need(asset.get('source_id') in ids and asset.get('operation'),'Derived asset needs source and transformation')
        f=member(p,asset.get('path'));need(f.is_file() and digest(f)==asset.get('sha256'),'Generated asset bytes changed: '+str(f))
        from PIL import Image
        with Image.open(f) as im:need(min(im.size)>0,'Invalid generated image')
    return data


def verify_build(package, receipt):
    if receipt.get('kind') != 'existing': return
    p=Path(package); value=read(p/'build-record.json')
    need(value.get('command') and value.get('toolchain') and value.get('exit_code')==0,'Existing build needs its actual command, toolchain and successful exit code')
    sources=value.get('source_files')
    need(isinstance(sources,dict) and value.get('lockfile') in sources and len(sources)>1,'Include editable sources and the dependency lockfile')
    for name,sha in sources.items():
        need(name.startswith('project-source/'),'Editable sources belong in project-source')
        path=member(p,name);need(path.is_file() and digest(path)==sha,'Source or lockfile changed: '+name)
    log=value.get('log',{});path=member(p,log.get('path'))
    need(path.is_file() and path.stat().st_size>0 and digest(path)==log.get('sha256'),'Include the original build log')


def requirements_contract(package,session):
    p=Path(package);s=Path(session)
    manifest=read(s/'raw/99-delivery/MANIFEST.json')
    requirements=p/'ui-requirements.json'
    if not manifest.get('project') and not requirements.is_file(): return None
    need(requirements.is_file(),'Project frontend requires its current ui-requirements.json')
    from component_ui import project_contract, system_api
    system_api().check(requirements)
    return {'sha256':digest(requirements),'project':project_contract(s,requirements)}


def context(package,session,stage):
    from crawl_gate import require_session_preflight
    s=Path(session).resolve();p=Path(package).resolve()
    need(p!=s/'raw' and p.is_relative_to(s/'raw'),'Frontend package must be inside this session raw')
    return require_session_preflight(s,output=p,stage=stage)


def init(kind,session,stage,*,source=None,sources=None,entry='index.html',name=None,requirements=None):
    from template_library import select
    s=Path(session).resolve();p=s/'raw/04-ui'/(name or kind)
    need(not p.exists(),'Output exists; edit and seal it instead of overwriting')
    member(p,entry)
    need(entry not in {RECEIPT,'review.json'} and not entry.startswith('evidence/'),'Entry cannot be review metadata')
    ctx=context(p,s,stage)
    identifier='frontend-'+kind
    select(s,'luz-design',stage,identifier,(p/entry).relative_to(s).as_posix())
    if kind=='existing':
        need(source and sources,'Existing build requires --source and --sources')
        source=Path(source).resolve()
        need(source.is_dir() and not p.is_relative_to(source),'Source must be a separate completed build directory')
        tree(source)  # Reject unsafe members before copying.
        shutil.copytree(source,p)
        shutil.copy2(sources,p/'component-sources.json')
    else:
        catalog=read(TEMPLATES/'catalog.json')
        spec=catalog[kind]
        shutil.copytree(TEMPLATES/kind,p)
        shutil.copytree(TEMPLATES/'shared',p/'shared')
        shutil.copytree(TEMPLATES/'artwork', p/'artwork', ignore=shutil.ignore_patterns('provenance'))
        shutil.copy2(TEMPLATES/'generated-assets.json',p/'generated-assets.json')
        (p/'vendor').mkdir()
        components=[]
        for dep in spec['dependencies']:
            for f,h in dep['files'].items():
                src=TEMPLATES/'vendor'/f
                need(src.is_file() and digest(src)==h,'Pinned runtime changed: '+f)
                shutil.copy2(src,p/'vendor'/f)
            components.append({**dep,'files':{'vendor/'+f:h for f,h in dep['files'].items()},'license':'vendor/'+dep['license']})
        write(p/'component-sources.json',components)
        (p/'RUN.md').write_text('# 运行\n\n在本目录运行 python -m http.server 5190 --bind 127.0.0.1，然后打开 http://127.0.0.1:5190/。依赖本地提供。源码在 index.html、style.css、app.js；vendor 保留运行时及许可证。\n\n数据为演示数据，修改保存在本浏览器 localStorage，未连接生产服务。修改后重新封存和验证。使用现代浏览器；尚未验收原生 App 或真实移动设备。\n',encoding='utf-8')
    if requirements:shutil.copy2(requirements,p/'ui-requirements.json')
    need((p/entry).is_file(),'Entry not found')
    receipt={'schema':'luz-frontend/1','mode':'component-reuse','kind':kind,'session':str(s),'stage':stage,'template_id':identifier,'entries':[entry]}
    write(p/RECEIPT,receipt)
    return seal(p,s)


def seal(package,session):
    from template_library import record_output
    p=Path(package).resolve();s=Path(session).resolve();r=read(p/RECEIPT)
    need(r.get('schema')=='luz-frontend/1' and r.get('session')==str(s),'Wrong session or package schema')
    context(p,s,r['stage']);verify_sources(p);verify_assets(p,optional=r.get('kind')=='existing');verify_build(p,r)
    from frontend_rules import source_issues
    need(not source_issues(p),'Frontend hard-rule violations: '+str(source_issues(p)))
    r['hard_rules_sha256']=digest(HARD_RULES)
    r['requirements']=requirements_contract(p,s)
    need(r.get('entries'),'Declare entry files')
    for e in r['entries']:need(member(p,e).is_file(),'Missing entry: '+e)
    r['files']=tree(p);r['bundle_sha256']=stable(r['files']);r.pop('review_sha256',None);r.pop('evidence_files',None)
    write(p/RECEIPT,r)
    registry=s/'raw/99-delivery/MANIFEST.json';m=read(registry)
    m.setdefault(REGISTRY,{})[p.relative_to(s/'raw').as_posix()]={'receipt_sha256':digest(p/RECEIPT)}
    write(registry,m)
    for e in r['entries']:record_output(s,'luz-design',r['stage'],p/e,r['template_id'],generator='Luz-Design/scripts/frontend.py:seal')
    return {'package':str(p),'entries':r['entries'],'bundle_sha256':r['bundle_sha256'],'review_required':True}


def validate_review(p,r,value):
    need(value.get('bundle_sha256')==r['bundle_sha256'],'Review describes different build bytes')
    need(isinstance(value.get('reviewer'),str) and value['reviewer'].strip(),'Review needs a reviewer')
    need(value.get('blocking_findings')==[],'Resolve blocking findings before delivery')
    need(value.get('component_usage') and isinstance(value.get('limitations'),list),'Describe actual component use and validation limits')
    from application_review import check_states
    check_states(value.get('application_states'), r, read(member(p,value['browser_report']['path'])).get('journeys'))
    rules=value.get('hard_rules',{})
    need(rules.get('sha256')==r.get('hard_rules_sha256')==digest(HARD_RULES),'Hard rules changed; re-seal and re-review')
    need(REVIEW_RULES <= set(rules.get('reviewed',[])) and rules.get('violations')==[], 'Complete the visual and semantic hard-rule review')
    loaded=set(value.get('loaded_assets',[]))
    assets=verify_assets(p,optional=r.get('kind')=='existing')['assets']
    if assets:
        need(any(a['path'] in loaded for a in assets),'Browser review must identify actually loaded generated assets')
    if r.get('requirements'):
        requirements=read(Path(p)/'ui-requirements.json')
        for group,field in [('pages','page_ids'),('actions','action_ids'),('journeys','journey_ids')]:
            expected={x['id'] for x in requirements.get(group,[])}
            covered={x for row in value.get('interactions',[]) for x in row.get('covers',{}).get(field,[])}
            need(expected<=covered,'Review does not cover required '+group)
    for key,fields in [('observations',['viewport','finding','screenshot']),('interactions',['action','result','evidence'])]:
        rows=value.get(key)
        need(isinstance(rows,list) and rows,'Missing actual '+key)
        for row in rows:
            need(all(row.get(k) for k in fields),'Incomplete '+key)
            evidence=row[fields[-1]]
            path=member(p,evidence.get('path'))
            need(path.is_file() and digest(path)==evidence.get('sha256'),'Changed/missing review evidence')
            if key=='observations':
                need(path.suffix.lower() in {'.png','.jpg','.jpeg','.webp'},'Visual review requires an image')
                from PIL import Image
                with Image.open(path) as im:need(min(im.size)>=200,'Screenshot is too small to inspect a page')
    axes=value.get('experience_axes',{})
    need(set(axes)=={'UX','AX','DX'},'Review must separately verify UX, AX and DX')
    for axis,row in axes.items():
        need(row.get('status')=='verified' and isinstance(row.get('observed'),str) and row['observed'].strip()
             and isinstance(row.get('limitations'),list),axis+': record actual outcome and limitations')
        refs=row.get('evidence',[])
        need(isinstance(refs,list) and refs,axis+': missing actual evidence')
        for ref in refs:
            path=member(p,ref.get('path'))
            need(path.is_file() and digest(path)==ref.get('sha256'),axis+': changed/missing experience evidence')
    validate_quality(p,r,value)


def verify_package(package,session,require_audit=True):
    from template_library import require_selected
    p=Path(package).resolve();s=Path(session).resolve();r=read(p/RECEIPT)
    need(r.get('schema')=='luz-frontend/1' and r.get('session')==str(s),'Wrong frontend package/session')
    from ui_package import mode
    need(mode(p)=='frontend','Conflicting package receipts')
    context(p,s,r['stage'])
    m=read(s/'raw/99-delivery/MANIFEST.json')
    registration=m.get(REGISTRY,{}).get(p.relative_to(s/'raw').as_posix(),{})
    need(registration.get('receipt_sha256')==digest(p/RECEIPT),'Package is not registered with current bytes')
    need(r.get('files')==tree(p) and r.get('bundle_sha256')==stable(r['files']),'Build changed; seal and re-review')
    verify_sources(p);verify_assets(p,optional=r.get('kind')=='existing');verify_build(p,r)
    need(r.get('hard_rules_sha256')==digest(HARD_RULES),'Hard rules changed; re-seal and re-review')
    from frontend_rules import source_issues
    need(not source_issues(p),'Frontend hard-rule violations: '+str(source_issues(p)))
    need(r.get('requirements')==requirements_contract(p,s),'Requirements changed; seal and re-review')
    for e in r['entries']:require_selected(s,'luz-design',r['stage'],member(p,e),r['template_id'],phase='post')
    if require_audit:
        need((p/'review.json').is_file() and registration.get('review_sha256')==digest(p/'review.json'),'Current visual and interaction review required')
        validate_review(p,r,read(p/'review.json'))
        need(registration.get('evidence_files')==tree(p/'evidence',False),'Review evidence files changed')
    return {'package':str(p),'template_id':r['template_id'],'entry_files':{str(i):e for i,e in enumerate(r['entries'])},'bundle_sha256':r['bundle_sha256'],'receipt':r}


def review(package,session,file):
    p=Path(package).resolve();s=Path(session).resolve()
    proof=verify_package(p,s,require_audit=False);value=read(file)
    def copy_evidence(ref,base):
        need(isinstance(ref,dict) and ref.get('path'),'Missing evidence reference')
        src=Path(ref['path']);src=src if src.is_absolute() else Path(base)/src
        need(src.resolve().is_relative_to(s/'raw'),'Review evidence must be inside this session raw')
        need(src.is_file() and digest(src)==ref.get('sha256'),'Review evidence was not the recorded file')
        dst=p/'evidence'/(digest(src)[:16]+src.suffix.lower());dst.parent.mkdir(exist_ok=True)
        if src.resolve()!=dst.resolve():shutil.copy2(src,dst)
        return {'path':dst.relative_to(p).as_posix(),'sha256':digest(dst)}
    # Evidence may be collected outside the build; copy its original bytes into the portable package.
    for kind,key in [('observations','screenshot'),('interactions','evidence')]:
        for row in value.get(kind,[]):
            ref=row[key];src=Path(ref['path']);src=src if src.is_absolute() else Path(file).resolve().parent/src
            need(src.resolve().is_relative_to(s/'raw'),'Review evidence must be inside this session raw')
            need(src.is_file() and digest(src)==ref.get('sha256'),'Review evidence was not the recorded file')
            dst=p/'evidence'/(digest(src)[:16]+src.suffix.lower());dst.parent.mkdir(exist_ok=True)
            if src.resolve()!=dst.resolve():shutil.copy2(src,dst)
            row[key]={'path':dst.relative_to(p).as_posix(),'sha256':digest(dst)}
    for row in value.get('experience_axes',{}).values():
        for ref in row.get('evidence',[]):
            src=Path(ref['path']);src=src if src.is_absolute() else Path(file).resolve().parent/src
            need(src.resolve().is_relative_to(s/'raw'),'Experience evidence must be inside this session raw')
            need(src.is_file() and digest(src)==ref.get('sha256'),'Experience evidence was not the recorded file')
            dst=p/'evidence'/(digest(src)[:16]+src.suffix.lower());dst.parent.mkdir(exist_ok=True)
            if src.resolve()!=dst.resolve():shutil.copy2(src,dst)
            ref.update(path=dst.relative_to(p).as_posix(),sha256=digest(dst))
    need(value.get('browser_report') and value.get('quality_assessment'),'Review needs browser_report and quality_assessment')
    value['browser_report']=copy_evidence(value['browser_report'],Path(file).resolve().parent)
    from application_review import audit_journeys
    reviewed_report=read(member(p,value['browser_report']['path']))
    value['application_states']=audit_journeys(p,proof['receipt'],reviewed_report.get('journeys'))
    quality_ref=value['quality_assessment'];quality_source=Path(quality_ref['path'])
    if not quality_source.is_absolute():quality_source=Path(file).resolve().parent/quality_source
    need(quality_source.resolve().is_relative_to(s/'raw') and quality_source.is_file() and digest(quality_source)==quality_ref.get('sha256'),'Quality evidence was not the recorded file')
    assessment=read(quality_source)
    for row in assessment.get('rows',[]):
        for ref in row.get('evidence',[]):
            copied=copy_evidence(ref,quality_source.parent)
            ref.update(path=Path(copied['path']).name,sha256=copied['sha256'])
    # Keep the sealed receipt immutable: quality and browser evidence bind its real bytes.
    quality_dst=p/'evidence/quality-assessment.json';write(quality_dst,assessment)
    value['quality_assessment']={'path':quality_dst.relative_to(p).as_posix(),'sha256':digest(quality_dst)}
    r=proof['receipt'];validate_review(p,r,value);write(p/'review.json',value)
    file=s/'raw/99-delivery/MANIFEST.json';m=read(file);entry=m[REGISTRY][p.relative_to(s/'raw').as_posix()]
    entry.update(review_sha256=digest(p/'review.json'),evidence_files=tree(p/'evidence',False));write(file,m)
    return verify_package(p,s)


def output_contract(path,session=None):
    from ui_entry_policy import _lookup_context
    path=Path(path).resolve();ctx=_lookup_context(path,session)
    if not ctx:return None
    raw=ctx['raw'];m=read(raw/'99-delivery/MANIFEST.json')
    for name in m.get(REGISTRY,{}):
        p=member(raw,name).resolve()
        if path.is_relative_to(p):
            proof=verify_package(p,ctx['session'])
            need(path.relative_to(p).as_posix() in proof['entry_files'].values(),'Not a reviewed frontend entry')
            return {'kind':'frontend-ui','source':path,'package':p,'proof':proof}
    return None


def export(package,session,out):
    proof=verify_package(package,session);p=Path(package).resolve();out=Path(out).resolve()
    need(not out.exists() and not out.is_relative_to(p),'Export must be new and outside the package')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(p.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(p).as_posix())
    return {'file':str(out),'sha256':digest(out),'bundle_sha256':proof['bundle_sha256']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['init','seal','review','check','export'])
    parser.add_argument('target');parser.add_argument('--session',required=True);parser.add_argument('--stage',default='design')
    parser.add_argument('--source');parser.add_argument('--sources');parser.add_argument('--entry',default='index.html');parser.add_argument('--name');parser.add_argument('--file');parser.add_argument('--out');parser.add_argument('--requirements')
    a=parser.parse_args()
    try:
        if a.action=='init':r=init(a.target,a.session,a.stage,source=a.source,sources=a.sources,entry=a.entry,name=a.name,requirements=a.requirements)
        elif a.action=='seal':r=seal(a.target,a.session)
        elif a.action=='review':need(a.file,'review requires --file');r=review(a.target,a.session,a.file)
        elif a.action=='export':need(a.out,'export requires --out');r=export(a.target,a.session,a.out)
        else:r=verify_package(a.target,a.session)
        print(json.dumps({k:v for k,v in r.items() if k!='receipt'},ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
