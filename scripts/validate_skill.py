#!/usr/bin/env python3
"""Validate the Luz-Design skill package: rule pages, rule cards, the template library and its registries.

    py -X utf8 scripts/validate_skill.py --package-only     the skill folder only
    py -X utf8 scripts/validate_skill.py                    also the numbered sessions in the output root
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import string
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from new_session import OUTPUT_ROOT
from validate_session import (
    SESSION_RE,
    TreeBuilder,
    first,
    iter_nodes,
    meaningful_nodes,
    normalized_visible_text,
    parse_html,
    validate as validate_session,
    validate_html_top_contract,
)

ROOT = Path(__file__).resolve().parents[1]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

SCRIPTS = (
    "context.py", "experience.py", "new_session.py", "add_mode.py", "publish.py", "deliver.py", "validate_session.py",
    "validate_skill.py", "make_summary.py", "check_output_layout.py", "make_xlsx.py", "make_docx.py", "make_docx_paginated.py",
    "make_table_pdf.py", "make_showcase.py", "check_document.py", "check_pdf.py", "check_contrast.py", "check_icon_image.py",
    "template_library.py", "template_registry.py", "sync_template_tokens.py", "build_templates.py", "export_poster.py",
    "build_prompts_js.py", "build_documents_index.py", "frontend.py", "frontend_rules.py", "ui_package.py",
    "component_reuse.py", "crawl_gate.py", "design_output_gate.py", "generate_ui_assets.py", "audit_gallery.py",
)
DESIGN_DOCS = (
    "hard-rules.md", "foundation.md", "app.md", "web.md", "poster.md", "documents.md", "slides.md", "patterns.md", "components.md",
    "motion.md", "interaction-contract.md", "review.md", "sources.md",
)
LIBRARY_SHARED = ("tokens.css", "ui.css", "kit.css", "app.css", "web.css", "agent.css", "ui.js", "assets/manifest.json")
LIBRARY_FOLDERS = ("app", "web", "poster", "documents")  # templates/ holds exactly these four folders
LIBRARY_ROOT_FILES = ("index.html", "references/template-registry.json", "kit/registry.js")
LIBRARY_SHELLS = ("bundle.shell.tpl", "components.shell.tpl", "poster.wall.tpl", "documents.page.tpl")
LIBRARY_PAGES = ("home", "list", "orders", "mine", "agent")
LIBRARY_EXTRA = (
    "templates/app/app.html", "templates/web/web.html", "templates/poster/poster.html", "templates/documents/documents.html",
    *[f"templates/{end}/source/pages/{page}.html" for end in ("app", "web") for page in LIBRARY_PAGES],
    "templates/poster/README.md", "templates/poster/source/prompts/viewer.html", "templates/poster/source/prompts/prompts.json",
    "templates/poster/source/prompts/styles.json", "templates/poster/source/prompts/prompts.js", "templates/documents/README.md",
    *[f"templates/documents/{kind}/manifest.json" for kind in ("word", "excel", "slides", "pdf", "reading")],
)
REQUIRED = [
    "SKILL.md", "README.md", "LICENSE", "NOTICE", "agents/openai.yaml",
    "references/cards.json", "references/themes.json", "references/template-library.json", "references/templates.txt",
    "references/component-libraries.json", "references/component-reuse.md", "references/document-evidence.md",
    "references/session-delivery.md", "references/image-assets.md", "references/ui-ownership.md",
    "references/visual-design.html", "references/file-design.html", "references/page-patterns.html", "references/page-patterns.json",
    "references/ui-recipes.html", "references/prototype-reference.html", "references/guidelines.css", "references/md-type.css", "references/hardware-plan.template.html",
    *[f"references/design/{name}" for name in DESIGN_DOCS],
    *LIBRARY_ROOT_FILES, *LIBRARY_EXTRA,
    *[f"kit/{name}" for name in LIBRARY_SHARED],
    *[f"scripts/{name}" for name in LIBRARY_SHELLS],
    "kit/frontend/catalog.json", "kit/frontend/generated-assets.json",
    *[f"scripts/{name}" for name in SCRIPTS],
]
RULE_PAGES = [
    ("visual-design.html", "visual", "视觉设计规范"),
    ("file-design.html", "file", "文件设计规范"),
    ("ui-recipes.html", "recipes", "界面实现参考"),
    ("page-patterns.html", "patterns", "页面范式库"),
    ("prototype-reference.html", "proto", "原型参考实现与组件模板库"),
]
REFERENCE_SUBDIRS = {"design"}
ALLOWED_TOP_LEVEL = {".git", ".gitattributes", ".gitignore", "LICENSE", "NOTICE", "README.md", "SKILL.md", "index.html", "agents", "references", "scripts", "experience", "templates", "kit"}
FRONTEND_STARTERS = ("app-task", "web-workspace")
FRONTEND_TEMPLATE_FILES = {
    "kit/frontend/" + name for name in (
        "catalog.json", "generated-assets.json",
        "app-task/index.html", "app-task/style.css", "app-task/app.js",
        "web-workspace/index.html", "web-workspace/style.css", "web-workspace/app.js",
        "shared/interaction.js", "shared/interaction.css", "shared/typography.css",
        "vendor/vue.global.prod.js", "vendor/VUE-LICENSE", "vendor/vant.min.js", "vendor/vant.css", "vendor/VANT-LICENSE",
        "vendor/element-plus.js", "vendor/element-plus.css", "vendor/ELEMENT-PLUS-LICENSE",
        "artwork/customer-identities/manifest.json",
    )
}

TEMPLATE_NAMES = ("brief.md", "visual-board.html", "document.html", "approvals.json", "manifest.json", "summary.json",)

RULE_TITLES = {f: t for f, _, t in RULE_PAGES}

TITLE_SEPARATOR_RE = re.compile(r"[,，:：;；|｜/／·・、\\\-–—]")

RULE_SECTIONS = [
    "scope",
    "workflow",
    "rules",
    "platform-matrix",
    "examples",
    "output-contract",
    "quality-gates",
    "handoff",
]

INLINE_ICON_DRAWING_TAGS = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}

HUMAN_TEXT_ATTRIBUTES = (
    "aria-label",
    "alt",
    "title",
    "placeholder",
    "aria-description",
    "aria-roledescription",
    "aria-valuetext",
)

def title_contains_punctuation(value: str) -> bool:
    """Treat every Unicode punctuation mark as a title separator."""
    return bool(TITLE_SEPARATOR_RE.search(value)) or any(
        unicodedata.category(char).startswith("P") for char in value
    )

def is_linear_icon(icon) -> bool:
    """Require a self-contained, visible inline outline icon."""
    viewbox = icon.get("viewbox").strip()
    stroke_width = icon.get("stroke-width").strip()
    style = icon.get("style").lower()
    drawing_tags = {
        node.tag for node in iter_nodes(icon)
        if node.tag in INLINE_ICON_DRAWING_TAGS
    }
    try:
        stroke_width_value = float(stroke_width.removesuffix("px"))
    except ValueError:
        return False
    return (
        icon.tag == "svg"
        and icon.get("fill").strip().lower() == "none"
        and icon.get("stroke").strip().lower() == "currentcolor"
        and icon.get("aria-hidden").strip().lower() == "true"
        and icon.get("focusable").strip().lower() == "false"
        and bool(re.fullmatch(r"[-.0-9 ]{7,}", viewbox))
        and 0 < stroke_width_value <= 4
        and bool(drawing_tags)
        and not any(node.tag in {"image", "foreignobject"} for node in iter_nodes(icon))
        and not any(name in style for name in ("fill:", "stroke:"))
    )

class StaticHtmlLinks(HTMLParser):
    """Read literal src/href attributes; framework bindings are separate names."""
    def __init__(self):
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for name, value in attrs if name in {'href', 'src'} and value is not None)

    handle_startendtag = handle_starttag

def local_targets(text: str, html: bool = False) -> list[str]:
    """Local link targets. In HTML only href and src attributes link; script and style bodies and comments are code, so
    a `](` in a prototype script is not a Markdown link. In Markdown, code spans and fences are skipped."""
    if html:
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        text = re.sub(r"(<(script|style)\b[^>]*>).*?(</\2\s*>)", r"\1\3", text, flags=re.S | re.I)
        parser = StaticHtmlLinks()
        parser.feed(text)
        found = parser.targets
    else:
        text = re.sub(r"^(`{3,}|~{3,}).*?^\1", "", text, flags=re.S | re.M)
        text = re.sub(r"`[^`\n]+`", "", text)
        parser = StaticHtmlLinks()
        parser.feed(text)
        found = LINK_RE.findall(text) + parser.targets
    targets = []
    for raw in found:
        target = raw.strip()
        if not target or target.startswith(("<", "'")):
            continue
        target = target.split()[0].strip("<>")
        parsed = urlparse(target)
        if parsed.scheme in {"http", "https", "mailto", "tel", "data"} or parsed.netloc or target.startswith("#"):
            continue
        clean = unquote(parsed.path)
        if clean:
            targets.append(clean)
    return targets

LATIN_ALLOWED_TAGS = {"code", "kbd"}

def prose_text(node) -> str:
    """Visible text of a node, leaving out script, style, code and kbd elements."""
    if node.tag in {"script", "style"} | LATIN_ALLOWED_TAGS:
        return " "
    parts = [child if isinstance(child, str) else prose_text(child) for child in node.children]
    return re.sub(r"\s+", " ", "".join(parts)).strip() if node.tag == "body" else "".join(parts)

def inside_code(node) -> bool:
    while node is not None:
        if getattr(node, "tag", None) in LATIN_ALLOWED_TAGS:
            return True
        node = node.parent
    return False

def validate_rule_page(
    path: Path,
    prefix: str,
    source_count: int,
    expected_h1: str,
    errors: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    if "<!doctype html>" not in text.lower():
        errors.append(f"HTML missing doctype: {rel}")
    if not re.search(r'<link\s+rel="stylesheet"\s+href="guidelines\.css"', text, re.I):
        errors.append(f"rule page must use references/guidelines.css: {rel}")
    # a declaration `color-scheme: dark` is banned on the rule pages (documents stay light); the rule text may still name the media query prefers-color-scheme: dark
    if re.search(r"(?<!prefers-)color-scheme\s*:\s*dark", text, re.I):
        errors.append(f"dark color scheme is not allowed: {rel}")

    root_node = parse_html(path, errors)
    if root_node is None:
        return
    validate_html_top_contract(root_node, str(rel), errors)
    body = first(root_node, "body")
    if body is None:
        errors.append(f"{rel} is missing body")
        return
    visible = prose_text(body)
    latin = re.search(r"[A-Za-z]", visible)
    if latin:
        start = max(0, latin.start() - 18)
        end = min(len(visible), latin.end() + 34)
        errors.append(f"visible Latin letters outside <code>/<kbd> are not allowed in {rel}: {visible[start:end]!r}")

    for node in iter_nodes(body):
        if inside_code(node):
            continue
        for attr in HUMAN_TEXT_ATTRIBUTES:
            attr_text = (node.get(attr) or "").strip()
            if attr_text and re.search(r"[A-Za-z]", attr_text):
                errors.append(f"accessible text in {rel} contains Latin letters: {attr_text}")

    title_node = first(root_node, "title")
    browser_title = normalized_visible_text(title_node) if title_node is not None else ""
    if browser_title != expected_h1:
        errors.append(f"{rel} browser title must be exactly {expected_h1}")
    if title_contains_punctuation(browser_title):
        errors.append(f"{rel} browser title contains a separator or punctuation mark")

    h1s = [node for node in iter_nodes(body) if node.tag == "h1"]
    if len(h1s) != 1:
        errors.append(f"{rel} must have exactly one h1 outside the sidebar")
    elif normalized_visible_text(h1s[0]) != expected_h1:
        errors.append(f"{rel} h1 must be exactly {expected_h1}")
    elif title_contains_punctuation(normalized_visible_text(h1s[0])):
        errors.append(f"{rel} h1 contains a separator or punctuation mark")

    main = first(root_node, "main")
    if main is None:
        errors.append(f"{rel} is missing main")
    else:
        if main.get("aria-label").strip() != expected_h1:
            errors.append(f"{rel} main aria-label must exactly match the page title")
        children = meaningful_nodes(main.children)
        if len(children) < 2 or not hasattr(children[0], "tag") or children[0].tag != "h1":
            errors.append(f"{rel} main must begin directly with its unique h1")
        elif not hasattr(children[1], "tag") or children[1].tag != "section":
            errors.append(f"{rel} h1 must be followed directly by the first section")
        else:
            first_section_children = meaningful_nodes(children[1].children)
            if not first_section_children or not hasattr(first_section_children[0], "tag") or first_section_children[0].tag != "h2":
                errors.append(f"{rel} first section must begin directly with its h2")
            near_title_copy = normalized_visible_text(children[1])
            for banned in ("日期", "无需构建", "可直接编辑", "入口", "说明"):
                if banned in near_title_copy:
                    errors.append(f"{rel} first section contains title-adjacent copy: {banned}")

        all_section_nodes = [node for node in iter_nodes(main) if node.tag == "section"]
        for section_node in all_section_nodes:
            section_children = meaningful_nodes(section_node.children)
            section_label = section_node.get("id") or "without-id"
            if (not section_children
                    or not hasattr(section_children[0], "tag")
                    or section_children[0].tag != "h2"):
                errors.append(f"{rel} section {section_label} must begin directly with its h2")

        section_icon_count = 0
        formal_section_nodes = [
            node for node in all_section_nodes if node.get("id") in RULE_SECTIONS
        ]
        for section_node in formal_section_nodes:
            section_children = meaningful_nodes(section_node.children)
            if (not section_children
                    or not hasattr(section_children[0], "tag")
                    or section_children[0].tag != "h2"):
                continue
            section_h2 = section_children[0]
            h2_children = meaningful_nodes(section_h2.children)
            if (not h2_children
                    or not hasattr(h2_children[0], "tag")
                    or h2_children[0].tag != "svg"):
                errors.append(f"{rel} section {section_node.get('id')} h2 must begin with its linear SVG icon")
            icons = [node for node in iter_nodes(section_h2) if node.tag == "svg"]
            if len(icons) != 1:
                errors.append(
                    f"{rel} section {section_node.get('id')} h2 must contain exactly one inline linear SVG icon"
                )
            for icon in icons:
                if not is_linear_icon(icon):
                    errors.append(
                        f"{rel} section {section_node.get('id')} h2 needs a valid linear SVG icon"
                    )
                else:
                    section_icon_count += 1
        if len(formal_section_nodes) < len(RULE_SECTIONS):
            errors.append(f"{rel} must contain all eight formal sections")
        if section_icon_count < len(RULE_SECTIONS):
            errors.append(f"{rel} needs one linear icon for every formal section; found {section_icon_count}")

    ids = re.findall(r'\bid="([^"]+)"', text)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate HTML ids in {rel}: {', '.join(duplicates)}")
    for section in RULE_SECTIONS:
        if f'<section id="{section}" data-rule-id="{prefix}-{section}"' not in text:
            errors.append(f"{rel} missing stable section contract: {section}")
        if f"<!-- SECTION:{section}:START" not in text or f"<!-- SECTION:{section}:END -->" not in text:
            errors.append(f"{rel} missing section edit boundaries: {section}")

DOCUMENT_TEMPLATE_SOURCES = {
    "references/hardware-plan.template.html": ("hardware-plan", "body brand hover line md_type tab_icon tint title"),
    "templates/documents/reading/system-architecture.html": ("system-architecture", "MODULE SYSTEM_NAME TAB_ICON"),
    "templates/documents/reading/system-design.html": ("system-design", "MODULE_SECTIONS SYSTEM_NAME TAB_ICON"),
    "templates/documents/reading/writing-article.html": ("writing-article", "BODY EXTRA_CSS EXTRA_HTML ICON TITLE"),
    "templates/documents/reading/dev/tech-plan/template.html": ("dev-technical-plan", "FAVICON PLAN_NUMBER SECTIONS SHELL_CSS STATUS TASK_MODE TITLE TOKENS_CSS TOKEN_SOURCE"),
    "templates/documents/reading/dev/reference/function-catalog.template.html": ("dev-function-catalog", "FAVICON FUNCTION_COUNT MODULES MODULE_OPTIONS RESULT_POLICY SHELL_CSS TITLE TOKENS_CSS TOKEN_SOURCE"),
    "templates/documents/reading/dev/reference/standards.template.html": ("dev-standards", "BASELINES FAVICON RULE_COUNT SECTIONS SHELL_CSS TITLE TOKENS_CSS TOKEN_SOURCE"),
    "templates/documents/reading/dev/reference/knowledge.template.html": ("dev-knowledge", "FACT_ROWS FAVICON KIND_OPTIONS SHELL_CSS SOURCE_ROWS TOKENS_CSS TOKEN_SOURCE"),
}

DOCUMENT_TEMPLATE_FILES = {
    relative for relative in DOCUMENT_TEMPLATE_SOURCES if relative.startswith("templates/")
} | {"templates/documents/reading/dev/shared/luz-reading.css", "templates/documents/reading/dev/tech-plan/tokens.snapshot.json"}

def render_document_template_fixture(path: Path, text: str) -> str:
    """Resolve only registered builder slots for in-memory source validation.

    These synthetic values test the maintained shell; they are never research,
    business copy or a delivered page. Static links and structure added to a
    template remain subject to the normal checks after resolution.
    """
    from new_session import tab_icon_href

    relative = path.relative_to(ROOT).as_posix()
    _, expected = DOCUMENT_TEMPLATE_SOURCES[relative]
    hardware = relative == "references/hardware-plan.template.html"
    if hardware:
        fields = [field for _, field, _, _ in string.Formatter().parse(text) if field]
    else:
        fields = re.findall(r"\{\{([^{}]+)\}\}", text)
    if set(fields) != set(expected.split()):
        raise ValueError(f"document template slot set differs: {relative}")
    section = '<section><h2>模板结构样例</h2><p>仅用于离线源结构检查。</p></section>'
    icon = tab_icon_href("模板结构检查")
    values = {field: "模板结构样例" for field in fields}
    values.update({
        "TAB_ICON": icon, "tab_icon": icon,
        "ICON": f'<link rel="icon" href="{icon}">',
        "FAVICON": f'<link rel="icon" href="{icon}">',
        "brand": "#225f91", "hover": "#174b75", "line": "#dbe3ec", "tint": "#e6f0f8",
        "md_type": (ROOT / "references/md-type.css").read_text(encoding="utf-8"),
        "SHELL_CSS": (ROOT / "templates/documents/reading/dev/shared/luz-reading.css").read_text(encoding="utf-8"),
        "TOKENS_CSS": "--canvas:#ffffff;--ink:#202124;--accent:#225f91;",
        "EXTRA_CSS": "", "EXTRA_HTML": "", "MODULE_OPTIONS": "", "KIND_OPTIONS": "",
        "FUNCTION_COUNT": "0", "RULE_COUNT": "0", "FACT_ROWS": "", "SOURCE_ROWS": "",
        "RESULT_POLICY": "<p>模板结构样例</p>", "BASELINES": "<p>模板结构样例</p>",
        **{key: section for key in ("body", "BODY", "MODULE_SECTIONS", "SECTIONS", "MODULES")},
    })
    if hardware:
        return text.format(**values)
    return re.sub(r"\{\{([^{}]+)\}\}", lambda match: values[match.group(1)], text)

def validate_document_template_top(root, relative: str, errors: list[str]) -> None:
    """Check resolved document shells and the article's explicit copy host."""
    if relative == "templates/documents/reading/writing-article.html":
        # The established article renderer places its body in this exact
        # clipboard host. Validate its source structure, then compare heading
        # flow with the same reading contract. This does not exempt other divs
        # or any final article from its own artifact validator.
        hosts = [node for node in iter_nodes(root) if node.get("id") == "copy-area"]
        if len(hosts) != 1 or hosts[0].tag != "div" or hosts[0].parent is None or hosts[0].parent.tag != "main":
            errors.append(f"{relative} must retain its unique main copy-area host")
            return
        host = hosts[0]
        siblings = host.parent.children
        index = next(i for i, node in enumerate(siblings) if node is host)
        for child in host.children:
            if hasattr(child, "parent"):
                child.parent = host.parent
        siblings[index:index + 1] = host.children
    validate_html_top_contract(root, relative, errors)

def under(root: Path, relative: str) -> Path:
    """A package-relative path inside root; escapes, symlinks and junctions are refused."""
    import os
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"path outside the skill: {relative}")
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink() or getattr(os.path, "isjunction", lambda _p: False)(current):
            raise ValueError(f"symlink or junction in package path: {relative}")
    return root / rel


def check_registered_tree(prefix: str, registered: set[str], errors: list[str]) -> None:
    """Reject missing files, extra files, and empty unregistered directories."""
    scope = under(ROOT, prefix)
    directories = {prefix}
    for relative in registered:
        path = under(ROOT, relative)
        if not path.is_relative_to(scope):
            raise ValueError(f"Registered path outside scope {prefix}: {relative}")
        if not path.is_file():
            errors.append(f"missing registered package file: {relative}")
        directories.update(parent.relative_to(ROOT).as_posix() for parent in path.parents if parent.is_relative_to(scope))
    if not scope.is_dir():
        errors.append(f"missing registered package directory: {prefix}")
        return
    for path in scope.rglob('*'):
        relative = path.relative_to(ROOT).as_posix()
        under(ROOT, relative)  # Also rejects symlinks/junctions.
        if path.is_dir():
            if relative not in directories:
                errors.append(f"unregistered package directory: {relative}")
        elif not path.is_file() or relative not in registered:
            errors.append(f"unregistered package file: {relative}")

def session_sweep(output_root: Path, strict: bool = False, details: bool = False) -> tuple[list[str], list[str], int]:
    """(errors, notes, number of sessions) of the sessions in the output root.

    A session created under the output layout (MANIFEST.json output_standard) is validated and its findings fail the run. An
    older session (two-digit number, several deliverables in the root, no summary page, no manifest) stays as it is: its
    findings are notes, in full with `details`, otherwise one line with the count."""
    from check_output_layout import LEGACY_NAME
    from validate_session import read_manifest, uses_output_standard
    errors: list[str] = []
    notes: list[str] = []
    older: list[str] = []
    skipped: list[str] = []
    count = findings = 0
    for session in sorted(path for path in output_root.iterdir() if path.is_dir()) if output_root.is_dir() else []:
        if not (SESSION_RE.match(session.name) or LEGACY_NAME.match(session.name)):
            skipped.append(session.name)
            continue
        count += 1
        hints: list[str] = []
        found = validate_session(session, strict=strict, notes=hints)
        if uses_output_standard(read_manifest(session)):
            errors.extend(f"{session.name}: {error}" for error in found)
            notes.extend(f"{session.name}: {hint}" for hint in hints)
            continue
        older.append(session.name)
        findings += len(found) + len(hints)
        if details:
            notes.extend(f"{session.name}: {message}" for message in found + hints)
    if older:
        notes.insert(0, f"{len(older)} older session(s) kept as they are, {findings} finding(s) not enforced (--legacy-details lists them)")
    if skipped:
        notes.insert(0, f"not numbered session folders, not validated: {', '.join(skipped)}")
    return errors, notes, count

def sibling_card_errors() -> list[str]:
    """Rule cards of sibling skills that cut sections from this skill's rule pages must still resolve."""
    import context
    errors: list[str] = []
    own = (ROOT / "references").resolve()
    for skill in ("Luz-System", "Luz-Dev", "Luz-Writing"):
        cards_file = ROOT.parent / skill / "references" / "cards.json"
        if not cards_file.is_file():
            continue
        try:
            cards = json.loads(cards_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        specs = [("always", s) for s in cards.get("always", [])]
        specs += [(kind, s) for kind, card in cards.get("cards", {}).items() for s in card.get("sections", [])]
        for kind, spec in specs:
            root = spec.get("root")
            if not root or Path(root).resolve() != own:
                continue
            page = own / spec["page"]
            try:
                if not page.is_file() or not context.section_text(page, spec["path"]):
                    errors.append(f"{skill} card {kind}: empty or missing section {spec['page']} › {' › '.join(spec['path'])}")
            except KeyError as exc:
                errors.append(f"{skill} card {kind} cites a heading this skill no longer has: {exc}")
    return errors


def design_reference_files() -> set[str]:
    docs = {"references/design/" + name for name in DESIGN_DOCS}
    docs |= {p.relative_to(ROOT).as_posix() for p in (ROOT / "references/design/licenses").glob("*.txt")}
    return docs


def frontend_artwork_files() -> set[str]:
    """Ship the rendered artwork and validate it with generated-assets.json."""
    out = set()
    folder = ROOT / "kit/frontend/artwork"
    if folder.is_dir():
        out |= {p.relative_to(ROOT).as_posix() for p in folder.rglob("*") if p.is_file()}
    return out


def library_files() -> set[str]:
    """Every file of the four template folders (app, web, poster, documents)."""
    files = set()
    for sub in LIBRARY_FOLDERS:
        folder = ROOT / "templates" / sub
        if folder.is_dir():
            files |= {p.relative_to(ROOT).as_posix() for p in folder.rglob("*") if p.is_file()}
    return files


def kit_files() -> set[str]:
    """kit/: the shared styles, script and assets of the library, plus the runnable frontend starters."""
    files = {p.relative_to(ROOT).as_posix() for p in (ROOT / "kit").glob("*") if p.is_file()}
    assets = ROOT / "kit/assets"
    if assets.is_dir():
        files |= {p.relative_to(ROOT).as_posix() for p in assets.rglob("*") if p.is_file()}
    return files | FRONTEND_TEMPLATE_FILES | frontend_artwork_files()


def package_frontend_scopes(errors):
    check_registered_tree("references/design", design_reference_files(), errors)
    from frontend import read, digest, member, verify_assets, TEMPLATES
    try:
        verify_assets(TEMPLATES)
        for kind, spec in read(TEMPLATES / "catalog.json").items():
            if kind not in FRONTEND_STARTERS:
                raise ValueError("Unregistered frontend starter: " + kind)
            for dependency in spec["dependencies"]:
                for name, expected in dependency["files"].items():
                    if digest(member(TEMPLATES / "vendor", name)) != expected:
                        raise ValueError("Runtime source differs: " + name)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append("frontend runtime: " + str(exc))
    return {f"kit/frontend/{kind}/index.html": "frontend-template" for kind in FRONTEND_STARTERS}


def package_template_library(errors):
    """The HTML template library: tokens follow themes.json, ids are well-formed, assets match their manifest, rules hold."""
    import sync_template_tokens
    import template_registry
    import frontend_rules
    if sync_template_tokens.OUT.is_file() and sync_template_tokens.OUT.read_text(encoding="utf-8") != sync_template_tokens.render():
        errors.append("kit/tokens.css differs from references/themes.json; run scripts/sync_template_tokens.py")
    items = template_registry.collect()
    errors.extend(template_registry.problems(items))
    for registry, want in ((ROOT / "references/template-registry.json", template_registry.render_registry(items)),
                           (ROOT / "kit/registry.js", template_registry.render_registry_js(items))):
        if registry.is_file() and registry.read_text(encoding="utf-8") != want:
            errors.append(f"{registry.relative_to(ROOT).as_posix()} is stale; run scripts/template_registry.py write")
    manifest = ROOT / "kit/assets/manifest.json"
    listed = set()
    if manifest.is_file():
        try:
            for item in json.loads(manifest.read_text(encoding="utf-8"))["assets"]:
                path = manifest.parent / item["path"]
                listed.add(path.relative_to(ROOT).as_posix())
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                    errors.append(f"asset differs from kit/assets/manifest.json: {item['path']}")
        except (KeyError, ValueError, OSError) as exc:
            errors.append(f"asset manifest: {exc}")
    assets = ROOT / "kit/assets"
    for path in assets.rglob("*") if assets.is_dir() else []:
        relative = path.relative_to(ROOT).as_posix()
        if path.is_file() and path.name != "manifest.json" and relative not in listed:
            errors.append(f"asset not listed in kit/assets/manifest.json: {path.relative_to(assets).as_posix()}")
    for sub in LIBRARY_FOLDERS:
        folder = ROOT / "templates" / sub
        if folder.is_dir():
            for violation in frontend_rules.source_issues(folder):
                errors.append(f"template rule {violation['rule']}: {sub}/{violation['file']}:{violation['line']} {violation['match']}")
    for violation in frontend_rules.source_issues(ROOT / "kit"):
        if not violation["file"].startswith("frontend/"):  # the starters are checked with their own catalog
            errors.append(f"kit rule {violation['rule']}: kit/{violation['file']}:{violation['line']} {violation['match']}")
    policies = {}
    # every page of the four folders is an interface of the library; the reading samples keep the reading contract and the
    # registered document templates keep their own
    for sub in LIBRARY_FOLDERS:
        for page in (ROOT / "templates" / sub).rglob("*.html"):
            relative = page.relative_to(ROOT).as_posix()
            if "samples" not in page.parts and relative not in DOCUMENT_TEMPLATE_SOURCES:
                policies[relative] = "ui-template"
    policies["index.html"] = "ui-template"
    return policies


def package_document_template_scopes(errors: list[str]) -> dict[str, str]:
    """Enumerate exact document sources; a catalog cannot exempt extra HTML."""
    policies = {}
    registered = DOCUMENT_TEMPLATE_FILES | library_files()
    check_registered_tree("templates", registered, errors)
    check_registered_tree("kit", kit_files(), errors)
    names = sorted(p.name for p in (ROOT / "templates").iterdir())
    if names != sorted(LIBRARY_FOLDERS):
        errors.append(f"templates/ must hold exactly the four folders {', '.join(sorted(LIBRARY_FOLDERS))}; found {', '.join(names)}")
    try:
        catalog = json.loads((ROOT / "references/template-library.json").read_text(encoding="utf-8"))["templates"]
        if not isinstance(catalog, dict):
            raise ValueError("templates must be an object")
        for relative, (identifier, _) in DOCUMENT_TEMPLATE_SOURCES.items():
            if not (ROOT / relative).is_file():
                errors.append(f"missing registered document template source: {relative}")
                continue
            if relative not in catalog.get(identifier, {}).get("files", []):
                errors.append(f"document template source not registered in {identifier}: {relative}")
                continue
            policies[relative] = "document-template"
        for identifier, entry in catalog.items():
            for relative in entry.get("files", []):
                if not (ROOT / relative).is_file():
                    errors.append(f"template {identifier} lists a missing file: {relative}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"document template catalog: {exc}")
    return policies


def check_skill_md(errors: list[str]) -> None:
    skill = ROOT / "SKILL.md"
    if not skill.is_file():
        return
    text = skill.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
    if "\nname: luz-design" not in normalized:
        errors.append("SKILL.md name must be luz-design")
    if re.search(r"\b(?:TODO|TBD|FIXME)\b", text):
        errors.append("SKILL.md contains an unfinished marker")
    for expected in [f"references/design/{kind}.md" for kind in ("app", "web", "poster", "documents")]:
        if expected not in text:
            errors.append(f"SKILL.md missing route: {expected}")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
        if not target.startswith(("http", "mailto")) and not (ROOT / target).resolve().exists() and not (ROOT.parent / target.replace("../", "", 1)).exists():
            errors.append(f"SKILL.md links to a missing file: {target}")
    sections = re.findall(r"(?m)^## (.+)$", normalized)
    if not sections or not sections[0].startswith("调用协议"):
        errors.append("SKILL.md must open with the section 调用协议 (invocation protocol) before any other section")
    protocol_text = normalized.split("\n## ", 2)[1] if "\n## " in normalized else ""
    if "scripts/context.py" not in protocol_text:
        errors.append("SKILL.md 调用协议 must start from scripts/context.py (the rule card)")
    try:
        import yaml
        front = yaml.safe_load(normalized.split("---", 2)[1])
        if not isinstance(front, dict) or not isinstance(front.get("description"), str):
            errors.append("SKILL.md frontmatter does not parse to a name and a description string")
        elif len(front["description"]) > 1024:
            errors.append("SKILL.md description exceeds 1024 characters")
    except ImportError:
        if re.search(r"(?m)^description: [^\n]*: ", normalized):
            errors.append("SKILL.md description contains ': ' which breaks YAML; use a dash instead")
    except Exception as exc:
        errors.append(f"SKILL.md frontmatter is not valid YAML: {exc}")


def check_markdown_links(errors: list[str]) -> None:
    for path in sorted((ROOT / "references").rglob("*.md")) + [ROOT / "README.md"]:
        text = path.read_text(encoding="utf-8")
        for target in local_targets(text, html=False):
            if not (path.parent / target).resolve().exists():
                errors.append(f"broken local link in {path.relative_to(ROOT)}: {target}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Luz Design skill and root-level sessions.")
    parser.add_argument("--strict-production", action="store_true", help="Validate every session as handed off (strict session structure)")
    parser.add_argument("--package-only", action="store_true", help="Validate only the skill package, not the sessions in the output root")
    parser.add_argument("--legacy-details", action="store_true", help="List every finding of the older sessions (they are notes, never errors)")
    args = parser.parse_args(argv)
    errors: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for item in ROOT.iterdir():
        if item.name not in ALLOWED_TOP_LEVEL and item.name not in {"__pycache__", ".pytest_cache", ".playwright-cli"}:
            errors.append(f"unexpected top-level item in the skill: {item.name}")
    for item in (ROOT / "references").iterdir() if (ROOT / "references").is_dir() else []:
        if item.is_dir() and item.name not in REFERENCE_SUBDIRS:
            errors.append(f"references must stay flat: {item.name}/")
    html_policies: dict[str, str] = {}
    html_policies.update(package_frontend_scopes(errors))
    html_policies.update(package_document_template_scopes(errors))
    html_policies.update(package_template_library(errors))
    check_skill_md(errors)
    check_markdown_links(errors)
    for rel in ("references/themes.json", "references/cards.json", "references/template-library.json", "references/component-libraries.json", "references/template-registry.json"):
        path = ROOT / rel
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON in {rel}: {exc}")
    for file_name, prefix, title in RULE_PAGES:
        validate_rule_page(ROOT / "references" / file_name, prefix, 0, title, errors)
    import context
    errors.extend(f"rule card: {e}" for e in context.check_cards())
    import io
    import contextlib
    import sync_rule_core
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        drift = sync_rule_core.main(["--check"])
    if drift:
        errors.extend("rule-card core differs from Luz-Design: " + line[5:] for line in buffer.getvalue().splitlines() if line.startswith("DIFF"))
    import sync_md_type
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        sync_md_type.main(["--check"])
    errors.extend("reading-page type block (md-type.css): " + line for line in buffer.getvalue().splitlines() if line.startswith(("DIFF", "MISSING")))
    head = (ROOT / "references" / "templates.txt").read_text(encoding="utf-8").splitlines()[:4]
    if not any("context.py" in line for line in head):
        errors.append("references/templates.txt must say at the top that templates are skeletons and point to scripts/context.py")

    guidelines_css = ROOT / "references/guidelines.css"
    if guidelines_css.is_file():
        css_body = guidelines_css.read_text(encoding="utf-8")
        for value in re.findall(r"(?:font-size|font)\s*:\s*[^;{}]*?([0-9.]+)px", css_body):
            if float(value) < 14:
                errors.append(f"rule stylesheet contains a font size below 14px: {value}px")

    for path in ROOT.rglob("*"):
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".html"}:
            text = path.read_text(encoding="utf-8")
            relative = path.relative_to(ROOT).as_posix()
            policy = html_policies.get(relative, "reading")
            if policy == "document-template":
                try:
                    text = render_document_template_fixture(path, text)
                except (KeyError, ValueError, OSError) as exc:
                    errors.append(str(exc))
                    continue
            for target in local_targets(text, html=path.suffix.lower() == ".html"):
                if policy == "frontend-template" and (target.startswith(("vendor/", "artwork/", "shared/")) or target == "icon.svg"):
                    if "kit/frontend/" + target not in FRONTEND_TEMPLATE_FILES | frontend_artwork_files():
                        errors.append(f"unregistered frontend assembly asset: {target}")
                    continue
                if not (path.parent / target).resolve().exists():
                    errors.append(f"broken local link in {path.relative_to(ROOT)}: {target}")
            if path.suffix.lower() == ".html" and "<!doctype html>" not in text.lower():
                errors.append(f"HTML missing doctype: {path.relative_to(ROOT)}")
            if path.suffix.lower() == ".html" and policy in {"reading", "document-template"}:
                if re.search(r"(?<!prefers-)color-scheme\s*:\s*dark", text, re.I):
                    errors.append(f"dark color scheme is not allowed: {path.relative_to(ROOT)}")
                if policy == "document-template":
                    parser = TreeBuilder()
                    parser.feed(text)
                    parser.close()
                    root = parser.root
                else:
                    root = parse_html(path, errors)
                if root is not None:
                    if policy == "document-template":
                        validate_document_template_top(root, relative, errors)
                    else:
                        validate_html_top_contract(root, str(path.relative_to(ROOT)), errors)

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json", ".py", ".html", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"(?<![A-Za-z0-9-])sk-(?:proj-)?[A-Za-z0-9_]{20,}", text):
            errors.append(f"possible API key in {path.relative_to(ROOT)}")

    from new_session import read_template
    templates: dict[str, str] = {}
    for name in TEMPLATE_NAMES:
        try:
            templates[name] = read_template(ROOT, name)
        except (KeyError, OSError) as exc:
            errors.append(str(exc))
    for name in ("approvals.json", "manifest.json", "summary.json"):
        if name in templates:
            try:
                json.loads(templates[name])
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON in template {name}: {exc}")
    from validate_session import LEGACY_SYSTEM_STAGES, OUTPUT_STANDARD, SCHEMA_VERSION, STAGE_PATHS
    for name in ("approvals.json", "manifest.json"):
        try:
            data = json.loads(templates.get(name, "{}"))
        except json.JSONDecodeError:
            continue
        if data.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"template {name} schema_version must be {SCHEMA_VERSION}")
        if name == "manifest.json" and data.get("output_standard") != OUTPUT_STANDARD:
            errors.append(f"template manifest.json output_standard must be {OUTPUT_STANDARD}")
        keys = set(data.get("stages", {})) if name == "manifest.json" else set(data) - {"schema_version", "standalone_poster"}
        if keys != set(STAGE_PATHS) or keys & set(LEGACY_SYSTEM_STAGES):
            errors.append(f"template {name} stages must be exactly: {', '.join(STAGE_PATHS)}")

    from experience import check as check_experience
    errors.extend(f"experience: {e}" for e in check_experience())
    errors.extend(sibling_card_errors())

    if errors:
        print(f"PACKAGE FAIL: {len(errors)} issue(s) in the skill package")
        for error in errors:
            print("ERROR", error)
    else:
        print(f"PACKAGE PASS: Luz Design skill package with {len(REQUIRED)} required files and {len(RULE_PAGES)} rule pages")
    if args.package_only:
        return 1 if errors else 0

    session_errors, session_notes, session_count = session_sweep(OUTPUT_ROOT, args.strict_production, args.legacy_details)
    for note in session_notes:
        print("NOTE", note)
    if errors or session_errors:
        if session_errors:
            print(f"SESSIONS FAIL: {len(session_errors)} issue(s) in {OUTPUT_ROOT}")
            for error in session_errors:
                print("ERROR", error)
        print(f"FAIL: {len(errors) + len(session_errors)} issue(s) ({len(errors)} package, {len(session_errors)} sessions)")
        return 1
    if not Path("D:/Codes/Imagegen/src/imagegen.py").is_file():
        print("WARN: Imagegen was not found at D:\\Codes\\Imagegen")
    print(f"PASS: Luz Design skill validated with {len(REQUIRED)} required files, {session_count} session(s), {len(RULE_PAGES)} rule pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
