"""Reviewed Vue/Vant composition of existing controls and semantic containers.

This is a structural diagnostic, not an HTML/JavaScript security sandbox.
The binding and whole-page reviews still check behavior and source suitability.
"""
from html.parser import HTMLParser
import html
import re

CONTAINERS = set('main section article header footer nav aside div span p h1 h2 h3 h4 ul ol li dl dt dd strong b small em time label img br hr template'.split())
CONTROLS = {'van-' + name for name in (
    'config-provider button cell cell-group radio radio-group grid grid-item popup '
    'dialog tabbar tabbar-item calendar tag icon divider empty nav-bar space form '
    'field row col skeleton loading notice-bar steps step') .split()}
INTERACTIVE_ROLES = set('button link checkbox radio switch slider tab menuitem textbox combobox option'.split())


class TemplateParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = set()
        self.regions = {}
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in CONTAINERS | CONTROLS:
            raise ValueError('Unsupported composition element: ' + tag)
        attributes = dict(attrs)
        for key, value in attrs:
            if key in {'v-html', 'is', ':is', 'v-bind:is', 'srcdoc', 'v-bind', 'v-on'} or '[' in key or key.startswith('on'):
                raise ValueError('Markup injection or opaque attributes are not component configuration')
            if key in {'src', 'href'} and value and re.match(r'(?:[a-z]+:|//)', value, re.I):
                raise ValueError('Composition assets must use verified local paths')
        if tag in CONTAINERS:
            if any(k.startswith(('@', 'v-on:')) for k in attributes):
                raise ValueError('Use an existing control for event handling')
            if (attributes.get('role') in INTERACTIVE_ROLES or 'contenteditable' in attributes
                    or any(k in attributes for k in ('tabindex', ':tabindex', 'v-bind:tabindex', ':role', 'v-bind:role'))):
                raise ValueError('Grouping cannot implement a handwritten control')
        active = {region for _, region in self.stack if region}
        region = attributes.get('data-component-id')
        if region:
            active.add(region)
            self.regions.setdefault(region, set())
        if tag in CONTROLS:
            self.tags.add(tag)
            for item in active:
                self.regions.setdefault(item, set()).add(tag)
        if tag not in {'img', 'br', 'hr'}:
            self.stack.append((tag, region))

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            raise ValueError('Composition tags must be balanced: ' + tag)
        self.stack.pop()


def parse_template(value):
    parser = TemplateParser()
    parser.feed(value)
    parser.close()
    if parser.stack:
        raise ValueError('Composition contains unclosed tags')
    return parser


def validate_template(value):
    return parse_template(value).tags


def input_files(plan, base):
    import component_reuse as reuse
    files = []
    for page in plan.get('pages', []):
        config = page.get('composition')
        if config:
            files += [reuse.reference(base, config[key]) for key in ('template', 'style', 'layout', 'review')]
    for item in plan.get('visual_assets', []):
        files += [reuse.reference(base, item[key]) for key in ('image', 'prompt', 'generation')]
    return files


def render(page, plan, resources, base):
    import component_reuse as reuse
    config = page['composition']
    reuse.need(plan['framework'].get('assembly') == 'vue-vant', 'Explicit Vue/Vant assembly required')
    paths = {key: reuse.reference(base, config[key]) for key in ('template', 'style', 'layout', 'review')}
    review = reuse.read(paths['review'])
    reuse.need(review.get('schema') == 'luz-ui-composition-review/1'
               and review.get('scope') == 'existing-control-composition'
               and reuse.nonempty(review.get('reviewer')) and review.get('findings') == []
               and review.get('files') == {key: reuse.digest(paths[key]) for key in ('template', 'style', 'layout')},
               'Composition needs a current review of source, layout and styling scope')
    body = paths['template'].read_text(encoding='utf-8')
    parsed = parse_template(body)
    used = set()
    for mount in page['mounts']:
        cid = mount.get('component_id')
        tags = mount.get('tags')
        reuse.need(cid in resources and isinstance(tags, list) and tags
                   and set(tags) == parsed.regions.get(cid), 'Component mapping must match its actual control region')
        reuse.need(resources[cid]['record'].get('component_tags') is not None
                   and set(tags).issubset(resources[cid]['record']['component_tags']), 'Control tags are not declared by the verified resource')
        used.add(cid)
    reuse.need(set(parsed.regions) == used, 'Unmapped composition region')
    reuse.need(parsed.tags.issubset(set().union(*(set(resources[cid]['record']['component_tags']) for cid in used))),
               'Composition contains controls without a verified source mapping')
    style = paths['style'].read_text(encoding='utf-8')
    reuse.need(not re.search(r'@import|url\s*\(|</style', style, re.I), 'Composition CSS must not load unverified assets')
    assets = {a['output']: a for a in plan.get('assets', [])}
    runtime = config.get('runtime')
    reuse.need(isinstance(runtime, dict) and set(runtime) == {'vue', 'vant', 'css'}, 'Declare pinned Vue/Vant runtime assets')
    for key, target in runtime.items():
        reuse.need(target in assets and assets[target]['resource'] in resources, 'Runtime must be a verified source asset')
        row = resources[assets[target]['resource']]['record']
        expected = 'vue' if key == 'vue' else 'vant'
        reuse.need(row.get('package') == expected and row.get('version') == config.get('versions', {}).get(expected),
                   'Runtime package version does not match composition')
    binding = config.get('binding')
    reuse.need(binding in {item['output'] for item in plan.get('bindings', [])}, 'Composition needs its reviewed data/action binding')
    esc = lambda value: html.escape(str(value), quote=True)
    value = (f'<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
             f'<title>{esc(config.get("title", "UI"))}</title>'
             f'<link rel="icon" href="{esc(config["icon"])}">'
             f'<link rel="stylesheet" href="{esc(runtime["css"])}">'
             f'<style>{style}</style></head><body><div id="app" v-cloak>{body}</div>'
             f'<script src="{esc(runtime["vue"])}"></script><script src="{esc(runtime["vant"])}"></script>'
             f'<script src="{esc(binding)}"></script></body></html>\n')
    reuse.need(config['icon'] in assets, 'Favicon must be a verified asset')
    return value, used
