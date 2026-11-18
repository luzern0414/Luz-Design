"""Build, audit, verify and export a component-reuse UI package.

This writer admits a separate deterministic assembly with requirements, source
and exact-target template proofs. Unknown interactive HTML remains rejected.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import zipfile

import component_reuse as reuse

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = 'ui-component-output'
RECEIPT = 'luz-component-ui.json'
REGISTRY = 'component_ui_outputs'
ASSERTIONS = {'expect_text','expect_value','expect_visible','expect_hidden','expect_count'}
ACTIONS = {'click','fill','press','select'}


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)


def inside(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    reuse.need(path != root and path.is_relative_to(root), 'Component UI path escapes its session raw directory')
    return path


def system_api():
    path = ROOT.parent / 'Luz-System/scripts/ui_requirements.py'
    spec = importlib.util.spec_from_file_location('_component_requirements', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def quality_rules_api():
    path = ROOT.parent / 'Luz-Project/scripts/quality_rules.py'
    reuse.need(path.is_file(), 'Shared quality rules evaluator is unavailable')
    spec = importlib.util.spec_from_file_location('_component_quality_rules', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def validate_cases(plan, requirements):
    reuse.need(isinstance(plan,dict) and isinstance(requirements,dict),'Browser plan and requirements must be objects')
    cases = plan.get('cases')
    reuse.need(isinstance(cases,list) and cases, 'Actual browser cases are required, not passed labels')
    pages = {p['id'] for p in requirements['pages']}
    components = {c['id'] for c in requirements['components']}
    actions = {a['id'] for a in requirements['actions']}
    action_rows = {a['id']:a for a in requirements['actions']}
    journeys = {j['id']:j for j in requirements['journeys']}
    seen, covered, seen_components, seen_actions, seen_pages = set(), set(), set(), set(), set()
    for case in cases:
        reuse.need(isinstance(case,dict) and reuse.nonempty(case.get('id')) and case['id'] not in seen, 'Browser case IDs must be unique')
        seen.add(case['id'])
        reuse.need(case.get('page_id') in pages and case.get('journey_id') in journeys
                   and case.get('kind') in {'success','recovery'} and reuse.nonempty(case.get('expected')), 'Case needs page, journey, kind and an observable expected result')
        reuse.need(case['page_id'] in journeys[case['journey_id']]['page_ids'],'Case starts outside its journey pages')
        seen_pages.add(case['page_id']); covered.add((case['journey_id'],case['kind']))
        steps = case.get('steps'); reuse.need(isinstance(steps,list) and steps, 'Browser case has no executable steps')
        triggered, asserted, pending = set(), set(), set()
        for step in steps:
            reuse.need(isinstance(step,dict) and step.get('op') in ACTIONS | ASSERTIONS | {'reload'}, 'Unknown browser step')
            if step['op'] == 'reload': continue
            locator = step.get('locator')
            reuse.need(isinstance(locator,dict) and ((reuse.nonempty(locator.get('role')) and reuse.nonempty(locator.get('name')))
                       or reuse.nonempty(locator.get('label'))), 'Browser steps require semantic role/name or a control label')
            cid = step.get('component_id')
            reuse.need(cid in components, 'Browser steps must identify an actual required component')
            if step['op'] not in {'expect_hidden','expect_count'} or (step['op']=='expect_count' and type(step.get('value')) is int and step['value']>0):
                seen_components.add(cid)
            aid = step.get('action_id')
            if step['op'] in ACTIONS:
                reuse.need(aid in actions,'Every interactive browser step needs its System action')
                reuse.need(cid==action_rows[aid]['component_id'],'Action step names the wrong component')
            if aid is not None:
                reuse.need(aid in actions and aid in journeys[case['journey_id']]['action_ids'], 'Case action is outside the journey contract')
                if step['op'] in ACTIONS: triggered.add(aid); seen_actions.add(aid); pending.add(aid)
                elif step['op'] in ASSERTIONS:
                    reuse.need(aid in triggered, 'Assert the outcome after performing its action')
                    asserted.add(aid)
                    pending.discard(aid)
            if step['op'] in {'fill','press','select','expect_text','expect_value'}:
                reuse.need(isinstance(step.get('value'),str), 'Browser step requires an exact value')
            if step['op'] == 'expect_count': reuse.need(type(step.get('value')) is int and step['value'] >= 0, 'Count assertion requires an integer')
        reuse.need(not pending and triggered.issubset(asserted) and any(s.get('op') in ASSERTIONS for s in steps), 'Every performed action needs an observed result assertion after its last trigger')
        reuse.need(set(journeys[case['journey_id']]['action_ids']).issubset(triggered),'Every case must execute its complete journey')
    reuse.need(seen_actions == actions and seen_components == components and seen_pages == pages, 'Browser coverage must include every page, component and action')
    reuse.need(covered == {(j,kind) for j in journeys for kind in ('success','recovery')}, 'Each journey needs success and recovery cases')


def materialize(spec_file, session, *, context=None):
    spec_file, session = Path(spec_file).resolve(), Path(session).resolve()
    inside(spec_file,session/'raw')
    plan = reuse.read(spec_file)
    requirements_path = reuse.reference(spec_file.parent, plan.get('requirements'))
    system_api().check(requirements_path)
    requirements = reuse.read(requirements_path)
    project_contract(session,requirements_path)
    validate_cases(plan,requirements)
    research = reuse.read(context['record']) if context else None
    output = reuse.compose(plan,spec_file.parent,component_ids={c['id'] for c in requirements['components']},
                           page_ids={p['id'] for p in requirements['pages']},action_ids={a['id'] for a in requirements['actions']},research=research,session=session)
    pages = {p['id']:p for p in requirements['pages']}
    actions = {a['id'] for a in requirements['actions']}
    for page in plan['pages']:
        reuse.need({m['component_id'] for m in page['mounts']} == set(pages[page['id']]['component_ids']), 'Composed page components differ from the System contract')
    for binding in plan.get('bindings',[]):
        reuse.need(set(binding['action_ids']).issubset(actions), 'Binding refers to an unknown System action')
        inside(reuse.reference(spec_file.parent,binding),session/'raw')
    _, inputs = reuse.sources(plan,spec_file.parent,research=research,session=session)
    inputs += [spec_file,requirements_path,Path(__file__),ROOT/'scripts/component_reuse.py',
               ROOT/'scripts/component_ui_browser.py',ROOT.parent/'Luz-System/scripts/ui_requirements.py']
    inputs += [reuse.reference(spec_file.parent,b) for b in plan.get('bindings',[])]
    inputs += [reuse.reference(spec_file.parent,b['review_ref']) for b in plan.get('bindings',[])]
    if any('composition' in page for page in plan['pages']):
        from component_composition import input_files
        inputs += input_files(plan, spec_file.parent)
        inputs.append(ROOT/'scripts/component_composition.py')
    if context: inputs.append(Path(context['record']))
    return plan,output,list(dict.fromkeys(inputs))


def project_contract(session,requirements):
    manifest_file=Path(session)/'raw/99-delivery/MANIFEST.json'
    link=reuse.read(manifest_file).get('project') if manifest_file.is_file() else None
    if not link: return None
    state=link.get('state_root') if isinstance(link,dict) else link
    reuse.need(reuse.nonempty(state),'Project UI requires its explicit state root')
    cli=ROOT.parent/'Luz-Project/scripts/project_ui_requirements.py'
    result=subprocess.run([sys.executable,'-X','utf8',str(cli),state,str(requirements)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    reuse.need(result.returncode==0,'Project requirements are not approved/current: '+(result.stdout+result.stderr)[-1800:])
    return json.loads(result.stdout)


def tree(package):
    result = {}
    for path in Path(package).rglob('*'):
        reuse.need(not path.is_symlink(), 'UI packages cannot contain symlinks')
        if path.is_file() and path != Path(package)/RECEIPT:
            result[path.relative_to(package).as_posix()] = reuse.digest(path)
    return result


def build(spec_file,session,package):
    from crawl_gate import require_session_preflight, record_template_output
    session,package=Path(session).resolve(),Path(package).resolve()
    inside(package,session/'raw')
    context=require_session_preflight(session,output=package,stage='design')
    plan,outputs,inputs=materialize(spec_file,session,context=context)
    from template_library import require_selected
    for page in plan['pages']:
        require_selected(context['template_root'],'luz-design',context['stage'],package/page['entry'],IDENTIFIER)
    reuse.need(not package.exists(), 'Use a new package revision; do not overwrite an existing reviewed package')
    # No output directory exists until all research, requirements, sources,
    # specific manual grants, cases and exact template targets have passed.
    for name,data in outputs.items():
        path=inside(package/name,package);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    receipt={'schema':'luz-component-ui-build/1','mode':'component-reuse','session':str(session),
             'spec':str(Path(spec_file).resolve()),'template_id':IDENTIFIER,
             'files':tree(package),'inputs':[{'path':str(p.resolve()),'sha256':reuse.digest(p)} for p in inputs],
             'entrypoints':[p['entry'] for p in plan['pages']]}
    receipt['project_requirements']=project_contract(session,reuse.reference(Path(spec_file).parent,plan['requirements']))
    write(package/RECEIPT,receipt)
    manifest_file=session/'raw/99-delivery/MANIFEST.json';manifest=reuse.read(manifest_file)
    manifest.setdefault(REGISTRY,{})[package.relative_to(session/'raw').as_posix()]={'receipt_sha256':reuse.digest(package/RECEIPT),'audit':None}
    write(manifest_file,manifest)
    for page in plan['pages']:
        record_template_output(context,package/page['entry'],IDENTIFIER,generator='Luz-Design/scripts/component_ui.py:build')
    return {'package':str(package),'entrypoints':receipt['entrypoints'],'audit':'required'}


def check_quality_review(review,plan,report,receipt_hash,report_hash,base):
    """Bind review and rule assessment to current evidence; observations still need judgment."""
    reuse.need(isinstance(review,dict) and review.get('schema')=='luz-ui-quality-review/1'
               and reuse.nonempty(review.get('reviewer')) and review.get('receipt_sha256')==receipt_hash
               and review.get('browser_report_sha256')==report_hash and review.get('blocking_findings')==[]
               and reuse.nonempty(review.get('consistency')), 'Current whole-UI review is missing, stale or has blocking findings')
    axes=review.get('axes')
    reuse.need(isinstance(axes,dict) and set(axes)=={'UX','DX','AX'}, 'Review all three of UX, DX and Agent Experience')
    for axis,value in axes.items():
        reuse.need(isinstance(value,dict) and reuse.nonempty(value.get('finding'))
                   and isinstance(value.get('evidence'),list) and value['evidence'],f'{axis} needs observations and real evidence')
        for ref in value['evidence']: reuse.reference(base,ref)
    page_for_case={c['id']:c['page_id'] for c in plan['cases']}
    screenshots={(page_for_case[r['id']],r['width'],r['screenshot']['sha256']) for r in report['cases']}
    observations=review.get('observations');reuse.need(isinstance(observations,list),'Review needs current rendered page observations')
    observed=set()
    for row in observations:
        reuse.need(isinstance(row,dict) and reuse.nonempty(row.get('finding'))
                   and (row.get('page_id'),row.get('width'),row.get('screenshot_sha256')) in screenshots,
                   'Review observation does not match a current rendered page')
        observed.add((row['page_id'],row['width']))
    reuse.need(observed=={(p['id'],w) for p in plan['pages'] for w in plan['framework']['breakpoints']},
               'Whole-UI review must inspect every page at every target viewport')
    assessment_ref=review.get('quality_assessment')
    reuse.need(isinstance(assessment_ref,dict) and reuse.nonempty(assessment_ref.get('path'))
               and reuse.nonempty(assessment_ref.get('sha256')), 'Current quality assessment needs a path and hash')
    assessment_file=reuse.reference(base,assessment_ref)
    assessment=reuse.read(assessment_file)
    reuse.need(isinstance(assessment,dict) and assessment.get('scope')=={'owner':'luz-design','stage':'design'},
               'Quality assessment scope must be exactly luz-design/design')
    reuse.need(assessment.get('receipt_sha256')==receipt_hash and assessment.get('browser_report_sha256')==report_hash,
               'Quality assessment is stale; bind the current receipt and browser report')
    quality=quality_rules_api()
    catalog=quality.read(quality.CATALOG)
    errors=quality.check_assessment(assessment,catalog,quality.digest(quality.CATALOG),assessment_file.parent)
    reuse.need(not errors,'Quality rule assessment failed: '+'; '.join(errors))


def verify_package(package,session,require_audit=True,require_review=True):
    from crawl_gate import require_session_preflight
    from template_library import require_selected
    package,session=Path(package).resolve(),Path(session).resolve()
    inside(package,session/'raw');receipt_file=package/RECEIPT;receipt=reuse.read(receipt_file)
    reuse.need(receipt.get('schema')=='luz-component-ui-build/1' and receipt.get('mode')=='component-reuse'
               and receipt.get('session')==str(session) and receipt.get('template_id')==IDENTIFIER,'UI receipt belongs to another contract or session')
    context=require_session_preflight(session,output=package,stage='design')
    plan,output,inputs=materialize(receipt['spec'],session,context=context)
    reuse.need(receipt.get('project_requirements')==project_contract(session,reuse.reference(Path(receipt['spec']).parent,plan['requirements'])),
               'Approved architecture or effective feature scope changed since UI build')
    expected={name:__import__('hashlib').sha256(data).hexdigest() for name,data in output.items()}
    reuse.need(tree(package)==expected==receipt.get('files'),'UI output differs from deterministic source assembly')
    actual_inputs=[{'path':str(p.resolve()),'sha256':reuse.digest(p)} for p in inputs]
    reuse.need(actual_inputs==receipt.get('inputs'),'UI inputs, requirements, permissions, evidence or verifier changed')
    entries=[p['entry'] for p in plan['pages']]
    reuse.need(receipt.get('entrypoints')==entries,'UI entrypoint receipt changed')
    for entry in entries:
        require_selected(context['template_root'],'luz-design',context['stage'],package/entry,IDENTIFIER,phase='post')
    manifest=reuse.read(session/'raw/99-delivery/MANIFEST.json')
    record=manifest.get(REGISTRY,{}).get(package.relative_to(session/'raw').as_posix(),{})
    reuse.need(record.get('receipt_sha256')==reuse.digest(receipt_file),'UI build is not registered or its receipt changed')
    if require_audit:
        audit=record.get('audit');reuse.need(isinstance(audit,dict),'Current browser audit is required')
        audit_file=inside(audit.get('path',''),session/'raw')
        reuse.need(reuse.digest(audit_file)==audit.get('sha256'),'Browser audit changed')
        from component_ui_browser import check_report
        check_report(reuse.read(audit_file),plan,package,session)
        if require_review:
            review_ref=record.get('quality_review')
            review_file=reuse.reference(session,review_ref)
            inside(review_file,session/'raw')
            check_quality_review(reuse.read(review_file),plan,reuse.read(audit_file),reuse.digest(receipt_file),reuse.digest(audit_file),review_file.parent)
    return {'mode':'component-reuse','template_id':IDENTIFIER,'receipt':receipt,
            'receipt_file':str(receipt_file),'entrypoints':entries,'entry_files':{x:x for x in entries},
            'requirements':plan['requirements'],'spec':receipt['spec'],'scope':'web-prototype; no native or live-backend acceptance implied'}


def audit(package,session):
    proof=verify_package(package,session,require_audit=False)
    from component_ui_browser import run
    plan=reuse.read(proof['spec'])
    report=run(plan,Path(package).resolve(),Path(session).resolve())
    out=Path(session)/'raw/99-delivery'/('component-audit-'+reuse.digest(Path(package)/RECEIPT)[:16]+'.json')
    write(out,report)
    reuse.need(not report['errors'],'Browser audit failed; inspect '+str(out))
    manifest_file=Path(session)/'raw/99-delivery/MANIFEST.json';manifest=reuse.read(manifest_file)
    key=Path(package).resolve().relative_to((Path(session)/'raw').resolve()).as_posix()
    manifest[REGISTRY][key]['audit']={'path':str(out.resolve()),'sha256':reuse.digest(out)}
    manifest[REGISTRY][key]['quality_review']=None
    write(manifest_file,manifest)
    return {'report':str(out),'cases':len(report['cases']),'errors':[]}


def review_package(package,session,review_file):
    proof=verify_package(package,session,require_review=False)
    session=Path(session).resolve();package=Path(package).resolve()
    review_file=inside(review_file,session/'raw')
    manifest_file=session/'raw/99-delivery/MANIFEST.json';manifest=reuse.read(manifest_file)
    record=manifest[REGISTRY][package.relative_to(session/'raw').as_posix()]
    audit_file=Path(record['audit']['path'])
    check_quality_review(reuse.read(review_file),reuse.read(proof['spec']),reuse.read(audit_file),
                         reuse.digest(package/RECEIPT),reuse.digest(audit_file),review_file.parent)
    record['quality_review']={'path':str(review_file),'sha256':reuse.digest(review_file)}
    write(manifest_file,manifest)
    return {'review':str(review_file),'sha256':reuse.digest(review_file),'scope':'Evidence-bound review; human approvals remain separate'}


def export(package,session,out):
    verify_package(package,session)
    out=inside(out,Path(session)/'raw');reuse.need(out.suffix.lower()=='.zip' and not out.exists(),'Export needs a new ZIP destination')
    reuse.need(not out.is_relative_to(Path(package).resolve()),'Export must be outside its source package')
    from crawl_gate import require_session_preflight,record_template_output
    context=require_session_preflight(session,output=out,stage='design',template_id=IDENTIFIER)
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(Path(package).rglob('*')):
            if path.is_file(): archive.write(path,path.relative_to(package).as_posix())
    record_template_output(context,out,IDENTIFIER,generator='Luz-Design/scripts/component_ui.py:export')
    return {'path':str(out),'sha256':reuse.digest(out)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','check','audit','review','export'])
    parser.add_argument('path');parser.add_argument('--session',required=True);parser.add_argument('--out');parser.add_argument('--file')
    args=parser.parse_args()
    try:
        if args.action in {'build','export'}: reuse.need(args.out,'This action needs --out')
        if args.action=='build': result=build(args.path,args.session,args.out)
        elif args.action=='check': result=verify_package(args.path,args.session)
        elif args.action=='audit': result=audit(args.path,args.session)
        elif args.action=='review':
            reuse.need(args.file,'Review needs --file with actual review observations')
            result=review_package(args.path,args.session,args.file)
        else: result=export(args.path,args.session,args.out)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 1

if __name__=='__main__': raise SystemExit(main())
