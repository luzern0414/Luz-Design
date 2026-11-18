"""Formal UI admission: active UI must belong to a registered, reviewed package.

This module does not manufacture evidence or approve a design. Passive reading
documents keep their normal checks; active UI must belong to a frontend package
(scripts/frontend.py) or a component-reuse package (scripts/component_ui.py)
registered in the session manifest and verifiable from its own receipt.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import re
import stat
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

MESSAGE = ('新界面通过 scripts/frontend.py 的成熟组件与完整成品合同，或既有 scripts/component_ui.py 合同。'
           '内部原型与风格实验页不能正式生成或发布为新界面')
HTML_EXT = {'.html', '.htm', '.xhtml'}
WEB_EXT = HTML_EXT | {'.js', '.mjs', '.cjs', '.css'}
PASSIVE_EMBEDS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif'}


def reject_legacy_ui_generation(tool: str):
    raise ValueError(f'{tool}: {MESSAGE}；--check 与内部纯渲染函数仅保留只读/历史验证用途')


def _lookup_context(path: Path, session=None):
    """Locate a possible registry without making plain read-only docs need research."""
    start = Path(session).resolve() if session is not None else (path if path.is_dir() else path.parent)
    for folder in (start, *start.parents):
        if (folder / 'raw/99-delivery/MANIFEST.json').is_file():
            return {'session': folder, 'raw': folder / 'raw'}
    return None


def source_output_contract(path: Path, session=None):
    """Return the registered UI package contract for ``path``, or None for an unregistered document."""
    path = Path(path).resolve()
    from frontend import output_contract
    frontend = output_contract(path, session)
    if frontend is not None:
        return frontend
    return component_output_contract(path, session)


def _component_packages(ctx):
    raw = ctx['raw'].resolve()
    manifest = json.loads((raw / '99-delivery/MANIFEST.json').read_text(encoding='utf-8'))
    records = manifest.get('component_ui_outputs', {})
    if not isinstance(records, dict):
        raise ValueError('组件 UI 登记无效')
    for relative in records:
        if not isinstance(relative,str) or not relative or '\\' in relative or ':' in relative:
            raise ValueError('组件 UI 登记路径无效')
        parts = PurePosixPath(relative)
        package = (raw / relative).resolve()
        if parts.is_absolute() or '..' in parts.parts or package == raw or not package.is_relative_to(raw):
            raise ValueError('组件 UI 登记路径越界')
        yield package


def component_output_contract(path: Path, session=None):
    path = Path(path).resolve()
    ctx = _lookup_context(path, session)
    if ctx is None:
        return None
    candidates = [package for package in _component_packages(ctx) if path.is_relative_to(package)]
    if not candidates:
        for folder in (path.parent, *path.parent.parents):
            if not folder.is_relative_to(ctx['raw'].resolve()):
                break
            if (folder / 'luz-component-ui.json').is_file():
                raise ValueError('组件 UI 包未在当前会话登记')
        return None
    package = max(candidates,key=lambda p:len(p.parts))
    from component_ui import verify_package
    proof = verify_package(package, ctx['session'], require_audit=True)
    if path.relative_to(package).as_posix() not in proof.get('entry_files', {}).values():
        raise ValueError('该页面不是已核验的组件 UI 入口')
    return {'kind':'component-ui','package':package,'source':path,'proof':proof}


class _Probe(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = []
        self.embeds = []
        self.nodes = []
        self.stack = []
        self.stylesheets = []

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        node = {'tag': tag, 'attrs': attrs, 'text': [], 'ancestors': self.stack[:]}
        self.nodes.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)
        if tag == 'link' and 'stylesheet' in (attrs.get('rel') or '').lower().split():
            self.stylesheets.append(attrs.get('href'))
        if (any(name.startswith('data-ui-') or name == 'data-cid' for name in attrs)
                or attrs.get('data-artifact') in {'prototype', 'interface', 'website'}):
            self.active.append('product declaration')
        if tag == 'script':
            if attrs.get('src') or attrs.get('type', '').lower() not in {'application/json', 'application/ld+json', 'text/plain'}:
                self.active.append('executable script')
        if tag in {'button', 'form', 'input', 'textarea', 'select', 'canvas', 'foreignobject', 'details', 'summary'}:
            self.active.append(tag)
        if attrs.get('role', '').lower() in {'button', 'checkbox', 'combobox', 'grid', 'listbox', 'menu', 'menubar', 'radio', 'slider', 'spinbutton', 'switch', 'tablist', 'textbox', 'tree'}:
            self.active.append('interactive role')
        if 'contenteditable' in attrs and attrs['contenteditable'] != 'false':
            self.active.append('editable surface')
        for name, value in pairs:
            if name.startswith('on'):
                self.active.append('event handler')
            if isinstance(value, str) and re.match(r'\s*(?:javascript|vbscript)\s*:', value, re.I):
                self.active.append('script URL')
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.active.append('redirect')
        if tag in {'iframe', 'object', 'embed'}:
            if 'srcdoc' in attrs:
                self.active.append('inline embedded UI')
            self.embeds.append(attrs.get('data') if tag == 'object' else attrs.get('src'))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        for node in self.stack:
            node['text'].append(data)


def _text(node):
    return ' '.join(''.join(node['text']).split()).casefold()


def _toc(node):
    attrs = node['attrs']
    labels = {str(attrs.get(key) or '').strip().casefold() for key in ('id', 'aria-label')}
    labels.update((attrs.get('class') or '').casefold().split())
    return bool(labels & {'toc', 'contents', 'table-of-contents', 'table of contents', '目录', '目次'})


def _heading_for(target, nodes):
    if target['tag'] in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
        return target
    if target['tag'] not in {'section', 'article'}:
        return None
    return next((node for node in nodes if target in node['ancestors']
                 and node['tag'] in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}), None)


def _css_text(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    # CSS escapes must not conceal state selectors from a read-only check.
    return re.sub(r'\\([0-9a-fA-F]{1,6})\s?|\\([^\r\n])',
                  lambda match: chr(int(match[1], 16)) if match[1] else match[2], css).casefold()


def _read_stylesheet(target, base, seen):
    if not isinstance(target, str) or not target.strip():
        raise ValueError('阅读文档样式缺少可检查路径；' + MESSAGE)
    url = urlsplit(target)
    if url.scheme or url.netloc or not url.path:
        raise ValueError('阅读文档须使用可检查的本地样式；' + MESSAGE)
    path = (base / unquote(url.path)).resolve()
    if path in seen:
        return ''
    if len(seen) >= 32:
        raise ValueError('阅读文档样式引用过深；' + MESSAGE)
    seen.add(path)
    try:
        return _document_css(path.read_text(encoding='utf-8-sig'), path.parent, seen)
    except OSError as exc:
        raise ValueError('阅读文档样式不可检查；' + MESSAGE) from exc


def _document_css(css, base, seen):
    css = _css_text(css)
    imports = re.findall(r'@import\s+(?:url\(\s*[\'"]?([^\s\)\'"]+)[\'"]?\s*\)|[\'"]([^\'"]+)[\'"])', css)
    return css + '\n' + '\n'.join(_read_stylesheet(first or second, base, seen) for first, second in imports)


def _simple_selector_matches(selector, node):
    selector = selector.strip()
    if selector.startswith('@'):
        return False
    compound = selector
    compound = re.sub(r':{1,2}[\w-]+(?:\([^)]*\))?', '', compound)
    tag = re.match(r'^[\w-]+', compound)
    if tag and tag[0] != node['tag']:
        return False
    attrs = node['attrs']
    classes = (attrs.get('class') or '').casefold().split()
    if any(value not in classes for value in re.findall(r'\.([\w-]+)', re.sub(r'\[[^]]*\]', '', compound))):
        return False
    if any(value != (attrs.get('id') or '').casefold() for value in re.findall(r'#([\w-]+)', re.sub(r'\[[^]]*\]', '', compound))):
        return False
    for name, operator, value in re.findall(r'\[([\w-]+)\s*(?:(\^=|\$=|\*=|=)\s*[\'"]?([^\]\'"]*)[\'"]?)?\]', compound):
        actual = str(attrs.get(name) or '').casefold()
        value = value.strip()
        if name not in attrs or (operator == '=' and actual != value) or (operator == '^=' and not actual.startswith(value)) or (operator == '$=' and not actual.endswith(value)) or (operator == '*=' and value not in actual):
            return False
    return bool(compound)


def _selector_matches_anchor(selector, anchor):
    """Match ordinary descendant/child selectors against the actual document.

    A TOC's padded links must not style unrelated citations for admission. For
    sibling selectors the final link selector is checked conservatively.
    """
    parts = [part for part in re.split(r'\s+(?![^\[]*\])|[>+~](?![^\[]*\])', selector.strip()) if part]
    if not parts or not _simple_selector_matches(parts[-1], anchor):
        return False
    if re.search(r'[+~](?![^\[]*\])', selector):
        return True
    ancestors = list(reversed(anchor['ancestors']))
    for qualifier in reversed(parts[:-1]):
        found = next((index for index, node in enumerate(ancestors)
                      if _simple_selector_matches(qualifier, node)), None)
        if found is None:
            return False
        ancestors = ancestors[found + 1:]
    return True


def _reading_errors(probe, path):
    """A passive document has citation links and an actual heading-linked TOC.

    Labels alone do not prove a TOC. Product navigation, action links, and CSS
    that changes visible surfaces are UI even without JavaScript or buttons.
    Typography, table styling, and passive heading/link highlighting stay valid.
    """
    errors = []
    links = [node for node in probe.nodes if node['tag'] == 'a']
    ids = {node['attrs']['id']: node for node in probe.nodes if node['attrs'].get('id')}
    navigation = [node for node in probe.nodes if node['tag'] == 'nav'
                  or node['attrs'].get('role') == 'navigation' or _toc(node)]
    toc_links = []
    for nav in navigation:
        entries = [link for link in links if nav in link['ancestors']]
        if not _toc(nav) or not entries:
            errors.append('product navigation')
            continue
        for link in entries:
            href = link['attrs'].get('href') or ''
            target = ids.get(unquote(href[1:])) if href.startswith('#') else None
            heading = _heading_for(target, probe.nodes) if target is not None else None
            if heading is None or not _text(link) or _text(link) != _text(heading):
                errors.append('navigation is not a heading-linked table of contents')
            else:
                toc_links.append(link)
    seen = set()
    css = '\n'.join(_document_css(''.join(node['text']), path.parent, seen)
                    for node in probe.nodes if node['tag'] == 'style')
    css += '\n' + '\n'.join(_read_stylesheet(target, path.parent, seen) for target in probe.stylesheets)
    rules = re.findall(r'([^{}]+)\{([^{}]*)\}', css)
    states = r':(?:checked|target|hover|focus|focus-within|focus-visible)\b'
    surfaces = r'(?:display|visibility|opacity|content|transform|translate|scale|height|max-height|width|max-width|clip-path|pointer-events|position|inset|top|left|right|bottom|--[\w-]+)\s*:'
    for selector, declarations in rules:
        if re.search(states, selector) and re.search(surfaces, declarations):
            errors.append('CSS interactive surface')
    for link in links:
        if any(link is entry for entry in toc_links):
            continue
        attrs = link['attrs']
        labels = (attrs.get('class') or '') + ' ' + (attrs.get('id') or '')
        if re.search(r'(?:^|[\s_-])(?:btn|button|cta|action|signup|checkout)(?:$|[\s_-])', labels, re.I):
            errors.append('action link')
        if re.fullmatch(r'(?:立即(?:开通|购买|注册|订阅|体验)|免费(?:试用|体验)|开始使用|start (?:your )?(?:free )?trial(?: today)?|sign up|get started|buy now|subscribe now)[\s.!。！→]*', _text(link), re.I):
            errors.append('call to action')
        declarations = _css_text(attrs.get('style') or '')
        for selectors, values in rules:
            if any(_selector_matches_anchor(selector, link) for selector in selectors.split(',')):
                declarations += ';' + values
        if re.search(r'(?:background(?:-color)?|border(?:-color)?|box-shadow)\s*:', declarations) and re.search(r'(?:padding(?:-\w+)?\s*:|display\s*:\s*(?:inline-block|inline-flex|flex|block|grid))', declarations):
            errors.append('button-shaped link')
    return errors


def html_delivery_contract(path: Path, *, session=None, allow=None, delivery_target=None, _depth=0):
    """Admit a registered source UI or a passive reading document, never a label.

    Reading links must retain citation/TOC behavior; embedded pages receive
    their own admission check. The final destination supplies relative-link base
    when a summary is checked before publish.py moves it.
    """
    path = Path(path).resolve()
    source = source_output_contract(path, session)
    if source is not None:
        return source
    probe = _Probe()
    probe.feed(path.read_text(encoding='utf-8'))
    probe.close()
    declared = {item.strip() for group in (allow or []) for item in group.split(',') if item.strip()}
    if probe.active or declared & {'interface', 'website'} or _reading_errors(probe, path):
        raise ValueError(MESSAGE)
    if _depth > 8:
        raise ValueError('来源锁定检查拒绝循环或过深的嵌入页面')
    base = Path(delivery_target).resolve().parent if delivery_target else path.parent
    embeds = []
    for target in probe.embeds:
        if not isinstance(target, str) or not target.strip():
            raise ValueError('嵌入页面缺少可核验来源；' + MESSAGE)
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            raise ValueError('嵌入页面须引用本会话已核验来源；' + MESSAGE)
        child = (base / unquote(url.path)).resolve()
        ctx = _lookup_context(path, session)
        if ctx is None or not child.is_relative_to(ctx['raw'].resolve()) or not child.is_file():
            raise ValueError('嵌入页面来源不在当前会话 raw 或不存在；' + MESSAGE)
        if child.suffix.lower() in PASSIVE_EMBEDS:
            embeds.append({'kind': 'document-file', 'source': child})
        elif child.suffix.lower() in HTML_EXT:
            embeds.append(html_delivery_contract(child, session=ctx['session'], _depth=_depth + 1))
        else:
            raise ValueError('嵌入内容不是可核验的文档或来源界面；' + MESSAGE)
    return {'kind': 'reading', 'embedded': embeds}


def _looks_html(data):
    text = data.decode('utf-8-sig', errors='ignore').lstrip()
    text = re.sub(r'^(?:<\?xml[^>]*>\s*|<!--.*?-->\s*)+', '', text, flags=re.S)
    return bool(re.match(r'<(?:!doctype\s+html|html\b|head\b|body\b|script\b|iframe\b)', text, re.I))


def _archive_files(path):
    files = {}
    has_web = False
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            name = item.filename.replace('\\', '/')
            relative = PurePosixPath(name)
            kind = stat.S_IFMT(item.external_attr >> 16)
            if relative.is_absolute() or '..' in relative.parts or ':' in relative.parts[0] or kind == stat.S_IFLNK:
                raise ValueError('来源包压缩文件包含越界路径或符号链接')
            if item.is_dir():
                continue
            key = relative.as_posix()
            if key in files:
                raise ValueError('来源包压缩文件包含重复文件')
            digest = hashlib.sha256()
            sample = b''
            with archive.open(item) as handle:
                while chunk := handle.read(1024 * 1024):
                    if len(sample) < 8192:
                        sample += chunk[:8192 - len(sample)]
                    digest.update(chunk)
            files[key] = digest.hexdigest()
            has_web |= relative.suffix.lower() in WEB_EXT or _looks_html(sample)
    return files, has_web


def _file_hashes(package):
    values = {}
    for path in package.rglob('*'):
        if path.is_symlink():
            raise ValueError('来源包不能包含符号链接')
        if path.is_file():
            values[path.relative_to(package).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return values


def check_nonpage_delivery(path: Path, session):
    """Prevent renamed HTML and ZIP exports from bypassing the UI publish gate."""
    path = Path(path).resolve()
    with path.open('rb') as handle:
        sample = handle.read(8192)
    if path.suffix.lower() in HTML_EXT or _looks_html(sample):
        raise ValueError('HTML 页面不能改扩展名绕过发布；界面保持完整包并由汇总页链接')
    if path.suffix.lower() == '.svg':
        probe = _Probe()
        probe.feed(path.read_text(encoding='utf-8'))
        if probe.active or probe.embeds:
            raise ValueError('矢量图片不能夹带可执行界面；' + MESSAGE)
    if path.suffix.lower() != '.zip':
        return
    files, has_web = _archive_files(path)
    if not has_web:
        return
    ctx = _lookup_context(path, session)
    if ctx is None:
        raise ValueError('UI ZIP must belong to a registered session')
    variants = [files]
    roots = {PurePosixPath(name).parts[0] for name in files}
    if len(roots) == 1 and all(len(PurePosixPath(name).parts) > 1 for name in files):
        variants.append({'/'.join(PurePosixPath(name).parts[1:]): digest for name, digest in files.items()})
    from frontend import REGISTRY, member, read, verify_package as verify_frontend
    manifest = read(ctx['raw'] / '99-delivery/MANIFEST.json')
    for relative in manifest.get(REGISTRY, {}):
        package = member(ctx['raw'], relative)
        if _file_hashes(package) in variants:
            verify_frontend(package, ctx['session'], require_audit=True)
            return
    from component_ui import verify_package
    for package in _component_packages(ctx):
        if _file_hashes(package) in variants:
            verify_package(package, ctx['session'], require_audit=True)
            return
    raise ValueError('压缩包与当前会话已核验的完整界面包不一致；' + MESSAGE)
