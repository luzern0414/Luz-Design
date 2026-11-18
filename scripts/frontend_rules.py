"""Scan owned HTML/JS for interaction problems and optional design review hints."""
import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    'edge-panel': re.compile(r'<\s*(?:el-drawer|van-popup|van-action-sheet)\b',re.I),
    'input-dialog': re.compile(r'(?<![.\w])prompt\s*\(',re.I),
    'horizontal-number-input': re.compile(r'<\s*(?:el-slider|van-slider)\b|\btype\s*=\s*[\"\']range[\"\']',re.I),
    'date-control': re.compile(r'<\s*(?:el-date-picker|van-date-picker|van-calendar)\b|\btype\s*=\s*[\"\']date(?:time-local)?[\"\']|\.toLocaleDateString\s*\(',re.I),
    'forbidden-copy': re.compile(r'今天|本地演示|演示数据|仅供参考|下一步建议'),
    'character-icon': re.compile(r'[☰☷☆★⚙＋➕]'),
}
SUGGESTION_RULES = frozenset({'forbidden-copy', 'character-icon'})

TITLE_ATTRIBUTE = re.compile(r'(?<![-\w])(?::|v-bind:)?title\s*=\s*[\"\']', re.I)
OPENING_TAG = re.compile(r'<\s*([a-z][\w-]*)\b([^<>]*?)>', re.I | re.S)

def title_issues(text):
    # Vant Tab's documented title prop labels its tab; it is not an HTML tooltip.
    # Other component title props are not exempted without checking rendered output.
    for tag in OPENING_TAG.finditer(text):
        if tag.group(1).lower() == 'van-tab':
            continue
        for hit in TITLE_ATTRIBUTE.finditer(tag.group(2)):
            yield 'native-title-tooltip', tag.start(2) + hit.start(), hit.group()

DIALOG = re.compile(r'<\s*(dialog|el-dialog|van-dialog)\b([^>]*)>(.*?)</\s*\1\s*>', re.I|re.S)
BUSINESS_INPUT = re.compile(r'<\s*(?:form|el-form|van-form|input|el-input(?:-number)?|van-field|textarea|select|ui-wheel-field)\b|contenteditable|<\s*(?:dialog|el-dialog|van-dialog)\b', re.I)

def overlay_issues(text):
    """A warning label alone is insufficient; inspect its actual contained controls.

    Dynamic slots require the rendered audit and behavior review, not a static pass.
    """
    spans=[]
    for hit in DIALOG.finditer(text):
        spans.append((hit.start(),hit.end()))
        attrs,body=hit.group(2),hit.group(3)
        warning=bool(re.search(r'\brole\s*=\s*[\"\']alertdialog[\"\']',attrs,re.I))
        if not warning or BUSINESS_INPUT.search(body):
            yield 'business-or-unclassified-dialog',hit.start(),hit.group(0)[:90]
    for hit in re.finditer(r'<\s*(?:dialog|el-dialog|van-dialog)\b',text,re.I):
        if not any(start<=hit.start()<end for start,end in spans):
            yield 'unclassified-dialog',hit.start(),hit.group(0)

def source_issues(package, *, include_suggestions=False):
    package=Path(package)
    root=package/'project-source' if (package/'project-source').is_dir() else package
    declared=package/'component-sources.json'
    dependencies={}
    if declared.is_file():
        dependencies={name for record in json.loads(declared.read_text(encoding='utf-8-sig')) for name in record.get('files',{})}
    issues=[]
    for p in sorted(root.rglob('*')):
        if p.suffix.lower() not in {'.html','.js','.jsx','.tsx','.vue'}:continue
        rel=p.relative_to(root)
        if p.relative_to(package).as_posix() in dependencies:continue
        if any(x in {'vendor','node_modules','evidence','provenance'} for x in rel.parts):continue
        text=p.read_text(encoding='utf-8-sig')
        for rule,offset,match in [*overlay_issues(text), *title_issues(text)]:
            issues.append({'rule':rule,'file':rel.as_posix(),'line':text.count('\n',0,offset)+1,'match':match})
        for rule,pattern in PATTERNS.items():
            if rule in SUGGESTION_RULES and not include_suggestions:
                continue
            for hit in pattern.finditer(text):
                if rule=='date-control':
                    tag=next((tag for tag in OPENING_TAG.finditer(text) if tag.start()<=hit.start()<tag.end()),None)
                    if tag and re.search(r'\bdata-business-date\b',tag.group(2)) and 'datetime-local' not in tag.group(2):
                        # A specific business date is permitted; its rendered scope is audited separately.
                        continue
                issues.append({'rule':rule,'file':rel.as_posix(),'line':text.count('\n',0,hit.start())+1,'match':hit.group()})
    return issues

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package');a=p.parse_args()
    findings = source_issues(a.package, include_suggestions=True)
    issues = [item for item in findings if item['rule'] not in SUGGESTION_RULES]
    suggestions = [item for item in findings if item['rule'] in SUGGESTION_RULES]
    print(json.dumps({'ok': not issues, 'violations': issues, 'suggestions': suggestions,
                      'limits': 'Review rendered images, text, layout and business behavior separately.'},
                     ensure_ascii=False, indent=2))
    raise SystemExit(bool(issues))
