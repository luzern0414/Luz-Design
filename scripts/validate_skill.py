#!/usr/bin/env python3
"""Validate the flattened Luz Design skill package and root-level sessions."""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlparse

from new_session import OUTPUT_ROOT
from validate_session import (
    SESSION_RE,
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
HTML_LINK_RE = re.compile(r'(?:href|src)="([^"]+)"')
REQUIRED = [
    ".gitignore",
    "README.md",
    "LICENSE",
    "NOTICE",
    "SKILL.md",
    "WORKFLOW.md",
    "agents/openai.yaml",
    "references/guidelines.css",
    "references/templates.txt",
    "scripts/new_session.py",
    "scripts/add_mode.py",
    "scripts/validate_session.py",
    "scripts/validate_skill.py",
    "scripts/publish.py",
    "scripts/experience.py",
    "scripts/test_session_flow.py",
    "scripts/test_experience.py",
    "scripts/test_rule_pages.py",
    "experience/sources.json",
    "experience/patterns.json",
    "experience/notes.json",
    "experience/catalog.md",
    "references/visual-design.html",
    "references/file-design.html",
    "references/ui-recipes.html",
    "references/ui-kit/commerce-kit/index.html",
    "references/themes.json",
    "references/component-libraries.json",
    "scripts/test_component_libraries.py",
    "references/prompt-image.txt",
    "scripts/check_contrast.py",
    "scripts/make_dark.py",
    "scripts/test_dark_themes.py",
    "scripts/check_document.py",
    "scripts/make_xlsx.py",
    "scripts/xlsx_metrics.py",
    "scripts/make_showcase.py",
    "scripts/showcase.py",
    "scripts/showcase_figures.py",
    "scripts/showcase_icons.py",
    "scripts/test_showcase.py",
    "scripts/test_xlsx_layout.py",
    "scripts/make_docx.py",
    "scripts/make_docx_paginated.py",
    "scripts/docx_layout.ps1",
    "scripts/context.py",
    "scripts/test_context.py",
    "references/cards.json",
    "references/ui-ownership.md",
    "scripts/sync_rule_core.py",
    "scripts/sync_md_type.py",
    "scripts/audit_palette.py",
    "scripts/audit_stability.py",
    "scripts/test_audit_stability.py",
    "scripts/test_audit_palette.py",
    "scripts/test_md_type.py",
    "references/md-type.css",
    "scripts/cut_element_sheet.py",
    "scripts/test_check_interface.py",
    "scripts/test_visual_rules.py",
    "scripts/test_audit_rules.py",
    "scripts/check_pdf.py",
    "scripts/test_check_pdf.py",
    "scripts/export_tokens.py",
    "scripts/test_export_tokens.py",
    "scripts/test_check_pptx.py",
    "scripts/test_viewport_motion.py",
    "references/design-craft.md",
    "references/token-system.md",
    "references/style-boards.json",
    "references/style-lab.template.txt",
    "references/reference-research.md",
    "references/reference-sites.json",
    "references/imagegen-playbook.md",
    "references/design-prompts.md",
    "references/motion-recipes.md",
    "scripts/make_style_lab.py",
    "scripts/teardown.py",
    "scripts/test_teardown.py",
    "scripts/audit_theme_discipline.py",
    "scripts/test_audit_theme_discipline.py",
    "scripts/test_style_boards.py",
    "references/page-patterns.json",
    "references/page-patterns.html",
    "scripts/page_pattern.py",
    "scripts/test_page_pattern.py",
    "references/component-library/README.md",
    "references/component-library/registry/index.md",
    "scripts/check_component_library.py",
    "scripts/build_component_library.py",
    "scripts/test_component_library.py",
    "references/ui-details.json",
    "references/ui-details.html",
    "scripts/check_icon_image.py",
    "scripts/test_check_icon_image.py",
    "scripts/ui_details.py",
    "scripts/test_ui_details.py",
    "references/design-path.json",
    "references/design-path.html",
    "scripts/design_path.py",
    "scripts/test_design_path.py",
    "references/prototype-reference.html",
    "references/prototype-templates/README.md",
    "references/prototype-templates/engine/ENGINE.md",
    "references/prototype-templates/engine/engine.js",
    "references/prototype-templates/engine/engine.css",
    "references/prototype-templates/engine/shell.template.html",
    "references/prototype-templates/mini/README.md",
    "references/prototype-templates/mini/build_kind.py",
    "references/prototype-templates/mini/mini.css",
    "references/prototype-templates/mini/mini.js",
    "references/prototype-templates/mini/stage.html",
    "references/prototype-templates/admin/README.md",
    "references/prototype-templates/admin/build_kind.py",
    "references/prototype-templates/admin/admin.css",
    "references/prototype-templates/admin/stage.html",
    "references/prototype-templates/admin/js/00-base.js",
    "references/prototype-templates/admin/js/90-register.js",
    "references/prototype-templates/schema/prototype.schema.json",
    "references/prototype-templates/shell/README.md",
    "references/prototype-templates/examples/generic-mini/spec.json",
    "references/prototype-templates/examples/generic-mini/README.md",
    "references/prototype-templates/examples/florist-mini/spec.json",
    "references/prototype-templates/examples/florist-mini/README.md",
    "references/prototype-templates/examples/florist-mini/content.js",
    "references/prototype-templates/examples/florist-mini/content.css",
    "references/prototype-templates/examples/florist-mini/assets/icons/3d/bouquet.webp",
    "references/prototype-templates/examples/booking-mini/spec.json",
    "references/prototype-templates/examples/booking-mini/README.md",
    "references/prototype-templates/examples/generic-admin/spec.json",
    "references/prototype-templates/examples/generic-admin/README.md",
    "references/prototype-templates/examples/generic-admin/content.js",
    "references/prototype-templates/examples/service-admin/spec.json",
    "references/prototype-templates/examples/service-admin/README.md",
    "references/prototype-templates/examples/service-admin/content.js",
    "references/prototype-templates/examples/suite-demo/suite.json",
    "references/prototype-templates/examples/suite-demo/README.md",
    "references/component-library/build.py",
    "references/component-library/src/SPEC.md",
    "references/component-library/tools/tokens.py",
    "references/component-library/tools/tokenize_colours.py",
    "references/component-library/tools/dark_audit.py",
    "references/component-library/tools/visual_regression.py",
    "references/component-library/src/taxonomy.js",
    "references/component-library/src/core-def.js",
    "references/component-library/src/core-ui.js",
    "references/component-library/src/extras.js",
    "references/component-library/src/ix.js",
    "references/component-library/src/ix.css",
    "references/component-library/src/kit.js",
    "references/component-library/src/kit.css",
    "references/component-library/src/combo.js",
    "references/component-library/src/lib.template.html",
    "references/component-library/src/blocks1.js",
    "references/component-library/src/blocks2.js",
    "references/component-library/src/blocks3.js",
    "references/component-library/src/blocks-zz-legacy-ix.js",
    "references/component-library/src/blocks-mp-basic.js",
    "references/component-library/src/blocks-mp-content.js",
    "references/component-library/src/blocks-mp-grow.js",
    "references/component-library/src/blocks-mp-trade.js",
    "references/component-library/src/blocks-ad-table.js",
    "references/component-library/src/blocks-ad-form.js",
    "references/component-library/src/blocks-ad-viz.js",
    "references/component-library/src/blocks-ad-shell.js",
    "references/component-library/src/blocks-ad-biz.js",
    "references/component-library/src/blocks-ad-comm.js",
    "references/component-library/assets/icons/flat/bag.webp",
    "references/component-library/assets/products/p0.webp",
    "scripts/build_prototype.py",
    "scripts/build_prototype_suite.py",
    "scripts/test_prototype_mini.py",
    "scripts/test_prototype_florist.py",
    "scripts/test_prototype_suite.py",
    "scripts/test_prototype_admin.py",
]
RULE_PAGES = [
    ("visual-design.html", "visual", "视觉设计规范"),
    ("file-design.html", "file", "文件设计规范"),
    ("ui-recipes.html", "recipes", "界面实现参考"),
    ("page-patterns.html", "patterns", "页面范式库"),
    ("design-path.html", "path", "设计路径与思考链"),
    ("ui-details.html", "details", "界面细节规范"),
    ("prototype-reference.html", "proto", "原型参考实现与组件模板库"),
]
TEMPLATE_NAMES = ("brief.md", "visual-board.html", "document.html", "commerce-kit.html", "approvals.json", "manifest.json",)
REFERENCE_SUBDIRS = {"ui-kit", "component-library", "prototype-templates"}   # ui-kit: 视觉实现底座（样式、行为、六种布局的可运行页面），页面本身也要过顶部结构检查
# The skill keeps four folders (agents, references, scripts, experience); sessions are outputs and live in OUTPUT_ROOT.
ALLOWED_TOP_LEVEL = {".git", ".gitignore", "LICENSE", "NOTICE", "README.md", "SKILL.md", "WORKFLOW.md", "agents", "references", "scripts", "experience"}
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


def local_targets(text: str, html: bool = False) -> list[str]:
    """Local link targets. In HTML only href and src attributes link; script and style bodies and comments are code, so
    a `](` in a prototype script is not a Markdown link. In Markdown, code spans and fences are skipped."""
    if html:
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        text = re.sub(r"(<(script|style)\b[^>]*>).*?(</\2\s*>)", r"\1\3", text, flags=re.S | re.I)
        found = HTML_LINK_RE.findall(text)
    else:
        text = re.sub(r"^(`{3,}|~{3,}).*?^\1", "", text, flags=re.S | re.M)
        text = re.sub(r"`[^`\n]+`", "", text)
        found = LINK_RE.findall(text) + HTML_LINK_RE.findall(text)
    targets = []
    for raw in found:
        target = raw.strip()
        if not target or target.startswith(("<", "'")):
            continue
        target = target.split()[0].strip("<>")
        parsed = urlparse(target)
        if parsed.scheme in {"http", "https", "mailto", "data"} or target.startswith("#"):
            continue
        clean = unquote(target.split("#", 1)[0])
        if clean:
            targets.append(clean)
    return targets


# Rule pages are Chinese prose; Latin letters are allowed only inside <code> and <kbd>
# (file names, commands, colour tokens, CSS properties), never in headings or sentences.
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


COMPONENT_SURFACES = {"admin", "website", "h5", "miniapp"}


def component_library_errors(data: dict | None = None) -> list[str]:
    """The component library registry: every library has what the rule, the audit and the prototype check read from it."""
    import re

    if data is None:
        path = ROOT / "references" / "component-libraries.json"
        if not path.is_file():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    libs = data.get("libraries")
    if not isinstance(libs, dict) or len(libs) < 8:
        return ["component-libraries.json: at least 8 libraries"]
    errors: list[str] = []
    seen_prefix: dict[tuple[str, str], str] = {}
    for key, lib in libs.items():
        where = f"component-libraries.json {key}"
        if not re.fullmatch(r"[a-z][a-z0-9-]+", key):
            errors.append(f"{where}: id must be lower-case words joined by hyphens")
        for field in ("name", "stack", "theme", "license", "docs", "fit"):
            if not str(lib.get(field, "")).strip():
                errors.append(f"{where}: missing {field}")
        # dark: how the library switches to its dark theme (visual-design.html 深色与浅色两套主题); empty means not yet checked, and darkSource says on what ground
        if not isinstance(lib.get("dark"), str):
            errors.append(f"{where}: dark must be a string (how the library goes dark; empty until checked against its documentation)")
        if not str(lib.get("darkSource", "")).strip():
            errors.append(f"{where}: missing darkSource (the ground of dark, or why it is not yet checked)")
        surfaces = lib.get("surfaces")
        if not isinstance(surfaces, list) or not surfaces or not set(surfaces) <= COMPONENT_SURFACES:
            errors.append(f"{where}: surfaces must be a non-empty list of {sorted(COMPONENT_SURFACES)}")
        prefixes = lib.get("prefix")
        # A library of this repository (luz-kit) names its component roots by an attribute (attr, data-cid) and its root classes carry no hyphen (mpcard003): its prefixes are
        # lower-case letters and digits and its docs are a path inside the repository. Every other library keeps the rule: a hyphenated prefix and an https link.
        own = "attr" in lib
        if own and not re.fullmatch(r"data-[a-z][a-z0-9-]*", str(lib.get("attr"))):
            errors.append(f"{where}: attr must be a data-* attribute name such as data-cid")
        if not isinstance(prefixes, list) or not prefixes or any(not isinstance(x, str) or not re.fullmatch(r"[a-z][a-z0-9]*" if own else r"[a-z]+-", x) for x in prefixes):
            errors.append(f"{where}: prefix must be a list of lower-case prefixes " + ("of letters and digits, such as mpcard" if own else "ending in a hyphen, such as el-"))
        docs = str(lib.get("docs", ""))
        if own and docs.startswith("references/"):
            if not (ROOT / docs).is_file():
                errors.append(f"{where}: docs points at {docs}, which does not exist in the repository")
        elif not docs.startswith("https://"):
            errors.append(f"{where}: docs must be an https link to the official documentation" + (" (or a references/ path of this repository for a library with attr)" if own else ""))
        verified = str(lib.get("verified", ""))
        if verified and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified):
            errors.append(f"{where}: verified is empty or a date YYYY-MM-DD")
        for prefix in prefixes if isinstance(prefixes, list) else []:
            for surface in surfaces if isinstance(surfaces, list) else []:
                other = seen_prefix.setdefault((prefix, surface), key)
                if other != key:
                    errors.append(f"{where}: prefix {prefix} on {surface} is already the prefix of {other}; the audit could not tell the two libraries apart")
    return errors


def is_build_template(path: Path) -> bool:
    """Pages under the component library and the prototype templates are build templates with slot markers, not rule pages."""
    parts = path.relative_to(ROOT).parts
    return len(parts) > 2 and parts[0] == "references" and parts[1] in {"component-library", "prototype-templates"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the flattened Luz Design skill and root-level sessions.")
    parser.add_argument("--strict-production", action="store_true", help="Validate every session as handed off (strict session structure)")
    parser.add_argument("--package-only", action="store_true", help="Validate only the skill package, not the sessions in the output root")
    args = parser.parse_args(argv)
    errors: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")
    errors += component_library_errors()
    for item in ROOT.iterdir():
        if item.name not in ALLOWED_TOP_LEVEL and item.name not in {"__pycache__", ".pytest_cache"}:
            errors.append(f"unexpected top-level item in the skill: {item.name} (the skill keeps only LICENSE, NOTICE, README.md, SKILL.md, WORKFLOW.md, agents, references, scripts, experience)")
    for item in (ROOT / "references").iterdir() if (ROOT / "references").is_dir() else []:
        if item.is_dir() and item.name not in REFERENCE_SUBDIRS:
            errors.append(f"references must stay flat: {item.name}/")

    skill = ROOT / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        normalized = text.replace("\r\n", "\n")
        if not normalized.startswith("---\n"):
            errors.append("SKILL.md must start with YAML frontmatter")
        if "\nname: luz-design" not in normalized:
            errors.append("SKILL.md name must be luz-design")
        if "description:" not in text:
            errors.append("SKILL.md description is missing")
        if re.search(r"\b(?:TODO|TBD|FIXME)\b", text):
            errors.append("SKILL.md contains an unfinished marker")
        for expected in [f"references/{f}" for f, _, _ in RULE_PAGES]:
            if expected not in text:
                errors.append(f"SKILL.md missing route: {expected}")
        # The invocation protocol is the first section and starts from the rule card (scripts/context.py).
        sections = re.findall(r"(?m)^## (.+)$", normalized)
        if not sections or not sections[0].startswith("调用协议"):
            errors.append("SKILL.md must open with the section 调用协议 (invocation protocol) before any other section")
        protocol_text = normalized.split("\n## ", 2)[1] if "\n## " in normalized else ""
        if "scripts/context.py" not in protocol_text:
            errors.append("SKILL.md 调用协议 must start from scripts/context.py (the rule card)")
        # Agents choose skills from the parsed frontmatter; an unquoted ": " inside the description breaks it silently.
        try:
            import yaml
            front = yaml.safe_load(normalized.split("---", 2)[1])
            if not isinstance(front, dict) or not isinstance(front.get("description"), str):
                errors.append("SKILL.md frontmatter does not parse to a name and a description string")
        except ImportError:
            if re.search(r"(?m)^description: [^\n]*: ", normalized):
                errors.append("SKILL.md description contains ': ' which breaks YAML; use a dash instead")
        except Exception as exc:
            errors.append(f"SKILL.md frontmatter is not valid YAML: {exc}")
        description = re.search(r"(?m)^description: (.+)$", normalized)
        # The description is for choosing a skill; the mandatory invocation protocol
        # above is checked in the first body section, where agents execute it.
        if len(description.group(1) if description else "") > 1024:
            errors.append("SKILL.md description exceeds 1024 characters")

    json_files = ["references/themes.json", "references/cards.json"]
    for rel in json_files:
        path = ROOT / rel
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON in {rel}: {exc}")

    for file_name, prefix, title in RULE_PAGES:
        validate_rule_page(ROOT / "references" / file_name, prefix, 0, title, errors)
    # Every rule card resolves to existing rule-page sections, so renaming a heading cannot silently empty a card.
    import context
    errors.extend(f"rule card: {e}" for e in context.check_cards())
    # The rule-card core is shared byte for byte with the sibling Luz skills present on this machine.
    import io
    import contextlib
    import sync_rule_core
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        drift = sync_rule_core.main(["--check"])
    if drift:
        errors.extend("rule-card core differs from Luz-Design: " + line[5:] for line in buffer.getvalue().splitlines() if line.startswith("DIFF"))
    # The Markdown type block of reading pages is shared text too: every copy that exists on this machine equals references/md-type.css.
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
        icon_style = re.search(r"\.icon-linear\s*\{([^}]*)\}", css_body, re.S)
        if not icon_style:
            errors.append("rule stylesheet is missing .icon-linear")
        else:
            icon_rules = icon_style.group(1)
            for token in ("width:", "height:", "fill:none", "stroke:currentcolor"):
                compact = re.sub(r"\s+", "", icon_rules).lower()
                if token not in compact:
                    errors.append(f"rule stylesheet icon style missing {token}")
        # every h2 rule counts: the Markdown type block (its h2 is the first one) and the page's own h2 that aligns the icon
        heading_rules = " ".join(m.group(1) for m in re.finditer(r"(?<![\w.-])h2\s*\{([^}]*)\}", css_body, re.S))
        compact_heading = re.sub(r"\s+", "", heading_rules).lower()
        if "display:flex" not in compact_heading or "align-items:center" not in compact_heading:
            errors.append("rule stylesheet must align h2 icons and text vertically")

    for path in ROOT.rglob("*"):
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".html"}:
            text = path.read_text(encoding="utf-8")
            if path.suffix.lower() == ".html" and is_build_template(path):
                continue   # build templates and partials carry slot markers; the generated pages are checked by the template tests
            for target in local_targets(text, html=path.suffix.lower() == ".html"):
                if not (path.parent / target).resolve().exists():
                    errors.append(f"broken local link in {path.relative_to(ROOT)}: {target}")
            if path.suffix.lower() == ".html" and "<!doctype html>" not in text.lower():
                errors.append(f"HTML missing doctype: {path.relative_to(ROOT)}")
            if path.suffix.lower() == ".html" and re.search(r"(?<!prefers-)color-scheme\s*:\s*dark", text, re.I):
                errors.append(f"dark color scheme is not allowed: {path.relative_to(ROOT)}")
            if path.suffix.lower() == ".html" and "{{" not in text and not is_build_template(path):
                root = parse_html(path, errors)
                if root is not None:
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
    for name in ("approvals.json", "manifest.json"):
        if name in templates:
            try:
                json.loads(templates[name])
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON in template {name}: {exc}")
    for name in ("visual-board.html", "document.html"):
        for value in re.findall(r"font-size:\s*([0-9.]+)px", templates.get(name, "")):
            if float(value) < 14:
                errors.append(f"{name} contains a font size below 14px")
    for name, artifact in (("visual-board.html", "visual-board"), ("document.html", "document")):
        if name in templates and f'data-artifact="{artifact}"' not in templates[name]:
            errors.append(f"{name} must declare its artifact type")
    # Schema 3.0 ledgers carry only Luz Design stages; system stages belong to Luz-System.
    from validate_session import LEGACY_SYSTEM_STAGES, SCHEMA_VERSION, STAGE_PATHS
    for name in ("approvals.json", "manifest.json"):
        try:
            data = json.loads(templates.get(name, "{}"))
        except json.JSONDecodeError:
            continue
        if data.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"template {name} schema_version must be {SCHEMA_VERSION}")
        keys = set(data.get("stages", {})) if name == "manifest.json" else set(data) - {"schema_version", "standalone_poster"}
        if keys != set(STAGE_PATHS) or keys & set(LEGACY_SYSTEM_STAGES):
            errors.append(f"template {name} stages must be exactly: {', '.join(STAGE_PATHS)}")

    from experience import check as check_experience
    errors.extend(f"experience: {e}" for e in check_experience())
    # Sibling skills cut rule text from these pages by heading path; renaming a heading here must not empty their cards.
    errors.extend(sibling_card_errors())

    # The package result comes first, then the sessions in the output root (outputs, not part of the package).
    if errors:
        print(f"PACKAGE FAIL: {len(errors)} issue(s) in the skill package")
        for error in errors:
            print("ERROR", error)
    else:
        print(f"PACKAGE PASS: Luz Design skill package with {len(REQUIRED)} required files and {len(RULE_PAGES)} rule pages")
    if args.package_only:
        return 1 if errors else 0

    sessions = [path for path in OUTPUT_ROOT.iterdir() if path.is_dir() and SESSION_RE.match(path.name)] if OUTPUT_ROOT.is_dir() else []
    session_errors = [
        f"{session.name}: {error}"
        for session in sorted(sessions)
        for error in validate_session(session, strict=args.strict_production)
    ]
    if errors or session_errors:
        if session_errors:
            print(f"SESSIONS FAIL: {len(session_errors)} issue(s) in {OUTPUT_ROOT}")
            for error in session_errors:
                print("ERROR", error)
        print(f"FAIL: {len(errors) + len(session_errors)} issue(s) ({len(errors)} package, {len(session_errors)} sessions)")
        return 1
    if not Path("D:/Codes/Imagegen/src/imagegen.py").is_file():
        print("WARN: Imagegen was not found at D:\\Codes\\Imagegen")
    session_label = f"{len(sessions)} production session(s)" if args.strict_production else f"{len(sessions)} session(s)"
    validation_label = "sessions strictly validated" if args.strict_production else "sessions structurally validated"
    print(
        f"PASS: Luz Design skill validated with {len(REQUIRED)} required files, "
        f"{session_label}, {len(RULE_PAGES)} rule pages, and {validation_label}"
    )
    return 0


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


if __name__ == "__main__":
    raise SystemExit(main())
