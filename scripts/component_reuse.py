"""Deterministic composition of sourced templates and components.

No file is written here. A source declaration is not proof of suitability or
human consent: source relevance and the quoted human record need review too.
The formal writer additionally requires the current Crawl/template contracts.
"""
from __future__ import annotations
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit
import zipfile

SCHEMA = 'luz-component-reuse/1'
INERT_CONTENT = {'script','style','template','noscript','textarea','title','xmp','iframe','noembed','noframes','plaintext'}
NON_COMPONENT = INERT_CONTENT | {'html','head','body','meta','link','base'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def need(value, message):
    if not value: raise ValueError(message)


def member(value):
    need(nonempty(value), 'Output member must be a nonempty path')
    path = PurePosixPath(value)
    need(not path.is_absolute() and '..' not in path.parts and ':' not in value and '\\' not in value
         and path.as_posix() == value and value not in {'.', 'luz-component-ui.json'}, 'Output path traversal or reserved member')
    return value


def reference(base, value):
    need(isinstance(value, dict) and nonempty(value.get('path')), 'File reference needs path and hash')
    path = Path(value['path'])
    path = (path if path.is_absolute() else Path(base) / path).resolve()
    need(path.is_file() and not path.is_symlink(), f'Source file missing: {path}')
    need(digest(path) == value.get('sha256'), f'Source hash changed: {path}')
    return path


def approval(resource, base, *, session=None):
    """Check a specific exception BEFORE writing its new component code.

    The human conversation reference must be verified by the invoking agent;
    this validator binds scope and detects drift, it cannot authenticate humans.
    """
    need(isinstance(resource.get('exception'), dict), 'Manual component requires specific human approval / 批准')
    exception = resource['exception']
    request_path = reference(base, exception.get('request'))
    grant_path = reference(base, exception.get('approval'))
    request, grant = read(request_path), read(grant_path)
    need(request.get('schema') == 'luz-component-exception/1', 'Unknown exception request schema')
    for key in ('component_id', 'behavior', 'reason', 'risks', 'acceptance'):
        need(nonempty(request.get(key)), f'Exception request missing {key}')
    need(isinstance(request.get('scope'), dict) and bool(request['scope']), 'Human approval requires an explicit scope')
    need(request['component_id'] == resource['id'] and request.get('scope') == resource.get('scope'), 'Human approval scope changed')
    need(isinstance(request.get('files'), list) and request['files'], 'Exception needs exact proposed files')
    need(isinstance(request.get('rejected_candidates'), list) and request['rejected_candidates'], 'Exception needs search and rejection evidence')
    for row in request['rejected_candidates']:
        need(isinstance(row, dict) and nonempty(row.get('ref')) and nonempty(row.get('reason'))
             and row.get('origin') in {'local','online'}, 'Rejected candidates need source and reason')
    need({r['origin'] for r in request['rejected_candidates']} == {'local','online'}, 'Search local and online before requesting manual work')
    need(grant.get('schema') == 'luz-component-approval/1' and grant.get('actor') == 'user'
         and grant.get('decision') == 'approved' and grant.get('request_sha256') == digest(request_path)
         and nonempty(grant.get('quote')) and nonempty(grant.get('interaction_ref')), 'Missing human approval bound to this exact request')
    if session is not None:
        need(Path(str(grant.get('session', ''))).resolve() == Path(session).resolve(), 'Human approval belongs to a different session')
    allowed = {str((Path(base) / p).resolve()) for p in request['files'] if nonempty(p)}
    actual = {str((Path(base) / r['path']).resolve()) for r in resource.get('files', [])}
    need(actual and actual.issubset(allowed), 'Component files exceed approved scope')
    return [request_path, grant_path]


def _online(resource, base, paths, research):
    need(isinstance(research, dict) and research.get('status') == 'complete'
         and research.get('schema_version') == 2 and research.get('caller') == 'luz-design'
         and research.get('stage') == 'design', 'Online reuse requires the current completed Design stage Crawl record')
    sources = {s['id']: s for s in research.get('sources', [])}
    ids = resource.get('crawl_source_ids')
    need(isinstance(ids, list) and ids and all(isinstance(i,str) and i in sources for i in ids), 'Online component needs current Crawl source IDs')
    acquisition_path = reference(base, resource.get('acquisition'))
    acquisition = read(acquisition_path)
    need(acquisition.get('schema') == 'luz-component-acquisition/1' and nonempty(acquisition.get('revision')),
         'Online component needs immutable upstream acquisition details')
    url = acquisition.get('source_url')
    need(any(str(sources[i]['url']).rstrip('/') == str(url).rstrip('/') for i in ids), 'Acquisition source was not read in this stage')
    need(urlsplit(str(acquisition.get('download_url'))).scheme == 'https', 'Acquisition needs the actual HTTPS download URL')
    archive_path = reference(base, acquisition.get('archive'))
    need(zipfile.is_zipfile(archive_path), 'Online source must retain its original ZIP archive')
    files = acquisition.get('files')
    need(isinstance(files, list) and files, 'Acquisition needs original member mapping')
    with zipfile.ZipFile(archive_path) as archive:
        need(len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate upstream ZIP members')
        mapping = {}
        for file in files:
            path = reference(base, file)
            original = file.get('member')
            member(original)
            need(hashlib.sha256(archive.read(original)).hexdigest() == digest(path), 'Source file differs from acquired upstream archive')
            mapping[path] = original
    need(set(paths).issubset(mapping), 'All component code and license files must match the acquired upstream archive')
    return [acquisition_path, archive_path]


def sources(plan, base, *, research=None, session=None):
    searches = plan.get('local_searches')
    need(isinstance(searches, list) and searches, 'Search the local library before component selection')
    search_ids, search_rows = set(), {}
    for row in searches:
        need(isinstance(row, dict) and nonempty(row.get('id')) and row['id'] not in search_ids
             and nonempty(row.get('query')) and nonempty(row.get('result')), 'Local searches need unique IDs, queries and actual results')
        need(isinstance(row.get('roots'), list) and row['roots'] and all(Path(p).is_dir() for p in row['roots']), 'Local search roots must exist')
        need(isinstance(row.get('candidates'), list), 'Local search needs candidates or an explained empty result')
        for candidate in row['candidates']:
            need(isinstance(candidate, dict) and nonempty(candidate.get('ref')) and nonempty(candidate.get('reason'))
                 and candidate.get('decision') in {'selected','rejected'}, 'Candidate selection needs a reason')
        search_ids.add(row['id'])
        search_rows[row['id']] = row
    resources, inputs = {}, []
    rows = plan.get('resources')
    need(isinstance(rows, list) and rows, 'Component resources cannot be empty')
    for row in rows:
        need(isinstance(row, dict) and nonempty(row.get('id')) and row['id'] not in resources, 'Resource IDs must be unique')
        need(row.get('origin') in {'local','online','manual'}, 'Unknown component origin')
        for field in ('version', 'selection_reason'):
            need(nonempty(row.get(field)), f'Resource {row["id"]} needs {field}')
        lookups = row.get('local_search_ids')
        need(isinstance(lookups, list) and lookups and all(i in search_ids for i in lookups), 'Resource must map to actual local search results')
        if row['origin'] == 'manual': inputs += approval(row, base, session=session)
        files = row.get('files')
        need(isinstance(files, list) and files, 'A URL, index or screenshot is not reusable component code')
        actual = {}
        for file in files:
            path = reference(base, file)
            key = file['path']
            need(key not in actual, 'Duplicate component source file')
            actual[key] = path; inputs.append(path)
        license_file = reference(base, row.get('license')); inputs.append(license_file)
        if row['origin'] == 'local':
            selected = [(Path(base)/candidate['ref']).resolve() for key in lookups
                        for candidate in search_rows[key]['candidates'] if candidate['decision']=='selected']
            need(all(any(p==s or (s.is_dir() and p.is_relative_to(s)) for s in selected) for p in actual.values()),
                 'Selected local files must match the recorded local search candidates')
        if row['origin'] == 'online': inputs += _online(row, base, [*actual.values(),license_file], research)
        resources[row['id']] = {'record':row, 'files':actual, 'license':license_file}
    return resources, list(dict.fromkeys(inputs))


def fragment(ref, resources):
    need(isinstance(ref, dict), 'Template or fragment reference missing')
    resource = resources.get(ref.get('resource'))
    need(resource is not None and ref.get('file') in resource['files'], 'Template or fragment is not in the verified source files')
    value = resource['files'][ref['file']].read_text(encoding='utf-8-sig')
    if 'start' in ref or 'end' in ref:
        start, end = ref.get('start'), ref.get('end')
        need(nonempty(start) and nonempty(end) and value.count(start) == 1 and value.count(end) == 1, 'Fragment boundaries must identify one exact source region')
        first = value.index(start) + len(start); last = value.index(end)
        need(last > first, 'Fragment boundaries are reversed')
        value = value[first:last]
    need(value.strip(), 'Empty source fragment')
    return value


class _HTMLSpans(HTMLParser):
    """Locate data without treating attributes, code or comments as UI text."""
    def __init__(self, value):
        super().__init__(convert_charrefs=False)
        self.value=value; self.stack=[]; self.spans=[]; self.elements=0
        self.offsets=[0]
        for line in value.splitlines(keepends=True): self.offsets.append(self.offsets[-1]+len(line))
    def handle_starttag(self,tag,attrs):
        if tag not in NON_COMPONENT and not any(t in INERT_CONTENT for t,a in self.stack): self.elements+=1
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append((tag,dict(attrs)))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag: del self.stack[i:]; break
    def handle_data(self,data):
        row,col=self.getpos();start=self.offsets[row-1]+col
        self.spans.append((start,start+len(data),self.stack[:]))


def _html_spans(value):
    parser=_HTMLSpans(value);parser.feed(value);parser.close();return parser


def visual_is_referenced(target, output):
    """Require an actual static image element, not a comment or JS string.

    Dynamic image construction is outside this composition contract; browser
    review additionally confirms the image loaded and is visible where intended.
    """
    class Images(HTMLParser):
        def __init__(self):
            super().__init__(); self.found = False
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'img' and attrs.get('src') == target:
                self.found = True
            if tag in {'img', 'source'} and any(part.strip().split()[0] == target
                    for part in attrs.get('srcset', '').split(',') if part.strip()):
                self.found = True
    for name, data in output.items():
        if Path(name).suffix == '.html':
            parser = Images(); parser.feed(data.decode('utf-8')); parser.close()
            if parser.found: return True
    return False


def _mount_position(value,index):
    prefix=value[:index]
    need(prefix.rfind('<!--')<=prefix.rfind('-->'), 'Component mount is inside a comment')
    parser=_HTMLSpans(prefix);parser.feed(prefix)
    need(not parser.rawdata and not any(t in INERT_CONTENT for t,a in parser.stack),
         'Component mount is not an active HTML content position')


def _adapt(value,target,change):
    kind,before=change.get('kind'),change.get('before')
    need(nonempty(before), 'Adaptation needs an exact original value')
    suffix=Path(target).suffix.lower()
    if kind=='text':
        need(suffix=='.html' and isinstance(change.get('value'),str) and '<' not in before and '>' not in before,
             'Text adaptations only replace HTML text nodes, never attributes, code or licenses')
        spans=[(a,b) for a,b,stack in _html_spans(value).spans if not any(t in {'script','style','template','noscript'} for t,attrs in stack)]
        after=html.escape(change['value'],quote=True)
    elif kind=='color':
        after=change.get('value');token=change.get('token')
        need(isinstance(after,str) and re.fullmatch(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})',before)
             and re.fullmatch(r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})',after), 'Color adaptation must replace literal colors')
        need(nonempty(token) and re.fullmatch(r'--[a-zA-Z][\w-]*',token), 'Color adaptation needs the shared CSS token name')
        regions=[(0,len(value))] if suffix=='.css' else [(a,b) for a,b,stack in _html_spans(value).spans if stack and stack[-1][0]=='style'] if suffix=='.html' else []
        spans=[]
        for a,b in regions:
            for match in re.finditer(re.escape(token)+r'\s*:\s*('+re.escape(before)+r')(?=\s*[;}])',value[a:b]):
                spans.append((a+match.start(1),a+match.end(1)))
    elif kind=='data':
        json.loads(before)
        spans=[(0,len(value))] if suffix=='.json' else [(a,b) for a,b,stack in _html_spans(value).spans
                  if stack and stack[-1][0]=='script' and stack[-1][1].get('type')=='application/json'] if suffix=='.html' else []
        after=json.dumps(change.get('value'),ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        for a,b in spans: json.loads(value[a:b])
    else:
        raise ValueError('Only text, color or chart/configuration data adaptations are supported')
    matches=[]
    for a,b in spans:
        matches += [(a+m.start(),a+m.end(),a,b) for m in re.finditer(re.escape(before),value[a:b])]
    need(len(matches)==1,'Adaptation must identify exactly one value in its permitted content context')
    first,last,a,b=matches[0]
    result=value[:first]+after+value[last:]
    if kind=='data': json.loads(value[a:first]+after+value[last:b])
    return result


def compose(plan, base, *, component_ids, page_ids, action_ids=None, research=None, session=None):
    """Produce deterministic bytes; every page shell and component is sourced."""
    need(isinstance(plan, dict) and plan.get('schema') == SCHEMA and plan.get('mode') == 'component-reuse', 'Unknown component reuse schema or mode')
    framework = plan.get('framework')
    need(isinstance(framework, dict), 'Define the unified framework before selecting components')
    for field in ('name','version','shell_resource','layout','token_policy','decision'):
        need(nonempty(framework.get(field)), f'Framework needs {field}')
    widths = framework.get('breakpoints')
    need(isinstance(widths, list) and len(widths) >= 2 and all(type(w) is int and 240 <= w <= 7680 for w in widths)
         and len(set(widths)) == len(widths), 'Declare distinct target viewport widths')
    quality = plan.get('quality')
    need(isinstance(quality, dict) and all(nonempty(quality.get(k)) for k in ('UX','DX','AX')), 'Explain the observable UX/DX/AX outcome of this design')
    resources, _ = sources(plan, base, research=research, session=session)
    for resource in resources.values():
        row=resource['record']
        if row['origin']=='manual':
            scope=row['scope']
            need(isinstance(scope.get('page_ids'),list) and scope['page_ids']
                 and set(scope['page_ids']).issubset(page_ids)
                 and isinstance(scope.get('action_ids'),list)
                 and action_ids is not None and set(scope['action_ids']).issubset(action_ids),
                 'Manual approval scope must name current System pages and actions')
    need(framework['shell_resource'] in resources, 'Unified shell must use a verified resource')
    need(set(component_ids).issubset(resources), 'Requirements include unselected components')
    output, seen_pages, used = {}, set(), set()
    pages = plan.get('pages')
    need(isinstance(pages, list) and pages, 'Pages cannot be empty')
    for page in pages:
        need(isinstance(page, dict) and page.get('id') in page_ids and page['id'] not in seen_pages, 'Unknown or duplicate page ID')
        seen_pages.add(page['id'])
        entry = member(page.get('entry')); need(entry.endswith('.html') and entry not in output, 'Page entry must be a unique HTML member')
        if 'composition' in page:
            from component_composition import render
            value, mounted = render(page, plan, resources, base)
            need(mounted.issubset(component_ids), 'Composition refers to an unknown requirement component')
            used.update(mounted)
            output[entry] = value.encode('utf-8')
            continue
        template = page.get('template')
        need(isinstance(template, dict) and template.get('resource') == framework['shell_resource'], 'Pages must use the declared unified framework source')
        value = fragment(template, resources)
        mounts = page.get('mounts')
        need(isinstance(mounts, list), 'Page mounts must be explicit')
        for mount in mounts:
            need(isinstance(mount, dict) and mount.get('component_id') in component_ids, 'Mount must map to a required component')
            ref = mount.get('fragment')
            need(isinstance(ref, dict) and ref.get('resource') == mount['component_id'], 'Mount cannot substitute an unrelated component source')
            selected=resources[mount['component_id']]['record']
            if selected['origin']=='manual':
                need(page['id'] in selected['scope']['page_ids'], 'Manual component is used outside its approved page scope')
            slot = mount.get('slot')
            need(nonempty(slot) and value.count(slot) == 1, 'Mount needs one real slot in the sourced shell')
            _mount_position(value,value.index(slot))
            piece=fragment(ref,resources)
            need(_html_spans(piece).elements>0,'A reference text or comment is not an actual UI component')
            value = value.replace(slot, piece, 1); used.add(mount['component_id'])
        output[entry] = value.encode('utf-8')
    need(seen_pages == set(page_ids) and used == set(component_ids), 'Every required page and component must actually be composed')
    for asset in plan.get('assets', []):
        source = resources.get(asset.get('resource'))
        need(source and asset.get('file') in source['files'], 'Asset is not a verified source file')
        target = member(asset.get('output')); need(target not in output, 'Output collision')
        output[target] = source['files'][asset['file']].read_bytes()
    for item in plan.get('bindings', []):
        # Wiring is traceable JS, never an escape hatch for unsourced markup.
        target = member(item.get('output'))
        need(Path(target).suffix in {'.js','.mjs'} and target not in output, 'Bindings may only supply unique JavaScript modules')
        need(nonempty(item.get('purpose')) and isinstance(item.get('action_ids'), list) and item['action_ids']
             and action_ids is not None and set(item['action_ids']).issubset(action_ids), 'Bindings require known System action mappings')
        binding_path=reference(base,item)
        review_path=reference(base,item.get('review_ref'));review=read(review_path)
        need(review.get('schema')=='luz-ui-binding-review/1' and review.get('scope')=='existing-component-binding'
             and nonempty(review.get('reviewer')) and review.get('findings')==[]
             and review.get('file_sha256')==digest(binding_path) and review.get('action_ids')==item['action_ids'],
             'Binding requires a current review of its existing-component-only scope')
        code=binding_path.read_text(encoding='utf-8')
        # This is a diagnostic guard, not a JavaScript sandbox. The required
        # source review remains responsible for indirect/computed behavior.
        need(not re.search(r'\b(?:createElement|createElementNS|insertAdjacentHTML|DOMParser|eval|Function)\s*\(|\b(?:innerHTML|outerHTML)\s*(?:=|\+=)|document\s*\.\s*write\s*\(',code),
             'Bindings cannot manufacture controls or execute generated markup; use a sourced or specifically approved component')
        output[target] = code.encode('utf-8')
    for item in plan.get('visual_assets', []):
        # Generated bitmap art has separate provenance from executable controls.
        target = member(item.get('output'))
        need(target not in output and Path(target).suffix.lower() in {'.png','.jpg','.jpeg','.webp'}, 'Visual asset must be a unique bitmap')
        image = reference(base,item.get('image'))
        prompt = reference(base,item.get('prompt'))
        generation = reference(base,item.get('generation'))
        need(nonempty(item.get('use')) and item.get('origin')=='imagegen' and prompt.read_text(encoding='utf-8').strip(),
             'Generated art requires its actual purpose, prompt and generation record')
        from PIL import Image
        with Image.open(image) as img: img.verify()
        metadata=read(generation)
        need(isinstance(metadata,dict) and nonempty(metadata.get('created_at'))
             and isinstance(metadata.get('request'),dict)
             and nonempty(metadata['request'].get('model'))
             and metadata['request'].get('prompt')==prompt.read_text(encoding='utf-8').strip()
             and isinstance(metadata.get('images'),list), 'Generation record must bind the actual prompt and model response')
        with Image.open(image) as img:
            size=f'{img.width}x{img.height}'; actual_format=img.format.lower()
        matching=[row for row in metadata['images'] if row.get('file')==image.name]
        need(len(matching)==1 and matching[0].get('processed') is False
             and matching[0].get('size')==size and matching[0].get('format')==actual_format,
             'Generated bitmap must match its retained native image record')
        need(visual_is_referenced(target, output), 'Generated image is not referenced by a static UI image element')
        output[target] = image.read_bytes()
    for rid, source in resources.items():
        need(re.fullmatch(r'[A-Za-z0-9_-]+', rid), 'Resource ID must be a safe identifier')
        name = f'licenses/{rid}.txt'; need(name not in output, 'License output collision')
        output[name] = source['license'].read_bytes()
    for change in plan.get('adaptations', []):
        target = change.get('file'); need(target in output, 'Adaptation target is not a generated file')
        value = output[target].decode('utf-8')
        output[target] = _adapt(value,target,change).encode('utf-8')
    return output
