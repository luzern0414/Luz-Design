#!/usr/bin/env python3
"""Validate a Luz Design session workspace without third-party dependencies.

Luz Design sessions are either standalone visual work (mode `visual`, session kind `standalone_poster`) or document
layout (mode `document`). System design, architecture, module scope, product UI, prototypes and hardware belong to
Luz-System, which keeps its own session engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

SESSION_RE = re.compile(r"^(\d{3,})-(.+)$")
# A session folder holds exactly one final deliverable named after the folder (.html, .xlsx or .docx), plus raw/
# with every working file: brief, prompts, references, generated images, document sources, approvals and manifest.
RAW_DIR = "raw"
FINAL_SUFFIXES = (".html", ".xlsx", ".docx")
PUBLISHABLE_STAGES = ("visual", "document")


def work_dir(folder: Path) -> Path:
    return folder / RAW_DIR


def final_html(folder: Path) -> Path:
    return folder / f"{folder.name}.html"
SESSION_ID_RE = re.compile(r"^SES-(\d{3,})$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HTML_LINK_RE = re.compile(r'(?:href|src)="([^"]+)"')
DELIVERABLE_ID_RE = re.compile(r"^(?:VIS|REF|DOC)-[A-Z0-9-]+$")
ASSUMPTION_ID_RE = re.compile(r"^ASSUME-\d{3,}$")
VALID_STATUS = {"draft", "review", "approved", "superseded"}
VALID_MODES = {"visual", "document"}
SESSION_KINDS = {"general", "standalone_poster"}
# Modes and session kinds that older sessions may name but that belong to another skill.
OTHER_SKILL = "Luz-System"
OTHER_SKILL_MODES = {"system", "prototype", "hardware"}
VALID_APPROVAL_STATUS = {"pending", "approved", "rejected", "not_requested"}
VALID_POSTER_STATUS = {"requested", "approved", "rejected", "not_requested"}
ADVICE_RE = re.compile(r"(下一步建议|建议增加|推荐模块|建议你|建议使用|可以考虑|可考虑|不妨|或许|也许)")
# Same task words new_session.py accepts for a standalone poster title.
POSTER_TASK_RE = re.compile(r"海报|poster|主视觉|品牌视觉|宣传图|视觉方向|活动视觉|封面|KV", re.I)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
VISUAL_PATH = "02-visual/visual-board.html"
DOCUMENT_PATH = "03-documents/document.html"
MODE_DIRS = {"visual": "02-visual", "document": "03-documents"}
MODE_REQUIRED = {
    "visual": [VISUAL_PATH],
    "document": [DOCUMENT_PATH],
}
# APPROVALS.json and MANIFEST.json: schema 3.0 knows only the stages Luz Design owns.
SCHEMA_VERSION = "3.0"
# Schema 2.0 files (written before the split) also carry system stages; they are read and those stages ignored.
LEGACY_SCHEMA_VERSION = "2.0"
STAGE_PATHS = {"visual": VISUAL_PATH, "document": DOCUMENT_PATH}
LEGACY_SYSTEM_STAGES = ("module_scope", "research", "architecture", "system_design", "prototype")
# Folders of the old system engine; a Luz Design session never contains them.
SYSTEM_DIRS = ("01-system", "03-prototype", "04-hardware")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SMALL_ELEMENT_TOKENS = (".mark", ".icon", ".avatar", ".badge", ".pill", ".status", ".chip", ".tag", ".logo", ".corner",
                        ".coin", ".dot", ".kk", ".steps", ".copy i", ".check", ".box", "::before", "::after", "button", "input", "svg",
                        # data marks: checkbox fills, check marks, progress and ranking bar fills, heat-map cells
                        ".cbox", "-mark", "bar i", ".bar-fill", ".rb i", ".heat i", ".progress i")


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None]
    parent: Node | None = None
    children: list[Node | str] = field(default_factory=list)

    def get(self, name: str, default: str = "") -> str:
        value = self.attrs.get(name)
        return value if value is not None else default


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {key.lower(): value for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if node.tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {key.lower(): value for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def parse_html(path: Path, errors: list[str]) -> Node | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"non-UTF-8 HTML in {path.name}: {exc}")
        return None
    if not re.search(r"<!doctype\s+html>", text, re.I):
        errors.append(f"HTML missing doctype: {path.name}")
    builder = TreeBuilder()
    try:
        builder.feed(text)
        builder.close()
    except Exception as exc:  # HTMLParser raises on malformed declarations.
        errors.append(f"invalid HTML in {path.name}: {exc}")
        return None
    return builder.root


def iter_nodes(node: Node) -> Iterable[Node]:
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from iter_nodes(child)


def text_content(node: Node) -> str:
    if node.tag in {"script", "style"}:
        return ""
    parts = []
    for child in node.children:
        parts.append(child if isinstance(child, str) else text_content(child))
    return "".join(parts)


def normalized_visible_text(node: Node) -> str:
    return re.sub(r"\s+", " ", text_content(node)).strip()


def first(root: Node, tag: str, classes: set[str] | None = None) -> Node | None:
    for node in iter_nodes(root):
        classes_value = set(node.get("class").split())
        if node.tag == tag and (classes is None or classes & classes_value):
            return node
    return None


def meaningful_nodes(children: list[Node | str]) -> list[Node | str]:
    return [
        child for child in children
        if isinstance(child, Node) or child.strip()
    ]


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing {path.name}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.name}: {exc}")
    return None


def local_links(text: str) -> list[str]:
    targets = LINK_RE.findall(text) + HTML_LINK_RE.findall(text)
    result = []
    for raw in targets:
        target = raw.strip()
        if target.startswith(("<", "'")):
            continue
        target = target.split()[0].strip("<>")
        parsed = urlparse(target)
        if parsed.scheme in {"http", "https", "mailto", "tel", "data"} or target.startswith("#"):
            continue
        result.append(unquote(target.split("#", 1)[0]))
    return [item for item in result if item]


def parse_iso_datetime(value, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty ISO-8601 timestamp")
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be a valid ISO-8601 timestamp")
        return False
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def session_artifact(session: Path, value: str | None, errors: list[str], label: str) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} artifact_path must be a non-empty relative path")
        return None
    path = Path(value)
    if path.is_absolute():
        errors.append(f"{label} artifact_path must stay inside the session")
        return None
    resolved = (session / path).resolve()
    try:
        resolved.relative_to(session.resolve())
    except ValueError:
        errors.append(f"{label} artifact_path escapes the session")
        return None
    if not resolved.is_file():
        errors.append(f"{label} artifact_path does not exist: {value}")
    return resolved


def validate_approval_record(session: Path, name: str, item: object, errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"APPROVALS.json {name} must be an object")
        return
    status = item.get("status")
    if status not in VALID_APPROVAL_STATUS:
        errors.append(f"APPROVALS.json {name}.status is invalid")
    for key in ("artifact_path", "artifact_sha256", "approved_at", "approved_by", "note"):
        if key not in item:
            errors.append(f"APPROVALS.json {name} missing {key}")
    if status != "approved":
        return
    approved_by = str(item.get("approved_by") or "").strip()
    if not approved_by:
        errors.append(f"APPROVALS.json {name} approval needs approved_by")
    elif approved_by.casefold() in {"auto", "model", "system", "validator", "script"}:
        errors.append(f"APPROVALS.json {name} cannot be approved by an automatic actor")
    parse_iso_datetime(item.get("approved_at"), f"APPROVALS.json {name}.approved_at", errors)
    artifact = session_artifact(session, item.get("artifact_path"), errors, name)
    approved_hash = str(item.get("artifact_sha256") or "")
    if not SHA256_RE.fullmatch(approved_hash):
        errors.append(f"APPROVALS.json {name}.artifact_sha256 must be a lowercase SHA-256 digest")
    elif artifact and artifact.is_file() and sha256_file(artifact) != approved_hash:
        errors.append(f"APPROVALS.json {name} artifact hash differs from the approved file; downstream work is blocked")


def validate_approvals(session: Path, errors: list[str]) -> dict | None:
    path = session / "99-delivery" / "APPROVALS.json"
    approvals = load_json(path, errors)
    if approvals is None:
        return None
    if not isinstance(approvals, dict):
        errors.append("APPROVALS.json must contain an object")
        return None
    version = approvals.get("schema_version")
    if version == SCHEMA_VERSION:
        required = {"schema_version", *STAGE_PATHS, "standalone_poster"}
        stray = [name for name in LEGACY_SYSTEM_STAGES if name in approvals]
        if stray:
            errors.append(f"APPROVALS.json {SCHEMA_VERSION} must not contain system stages ({', '.join(stray)}); they belong to {OTHER_SKILL}")
    elif version == LEGACY_SCHEMA_VERSION:
        # Pre-split ledgers carry module_scope, architecture, system_design and prototype records. They are ignored
        # while unused; an approved one means the session is system work and belongs to Luz-System.
        required = {"schema_version", "visual", "standalone_poster"}
        for name in LEGACY_SYSTEM_STAGES:
            item = approvals.get(name)
            if isinstance(item, dict) and item.get("status") == "approved":
                errors.append(f"APPROVALS.json {name} is approved; system stages belong to {OTHER_SKILL}, not Luz-Design")
    else:
        required = {"schema_version", *STAGE_PATHS, "standalone_poster"}
        errors.append(f"APPROVALS.json schema_version must be {SCHEMA_VERSION} (legacy {LEGACY_SCHEMA_VERSION} is still accepted)")
    missing = sorted(required - set(approvals))
    if missing:
        errors.append("APPROVALS.json missing: " + ", ".join(missing))

    for name in STAGE_PATHS:
        if name in approvals:
            validate_approval_record(session, name, approvals.get(name), errors)
    standalone = approvals.get("standalone_poster", {})
    if not isinstance(standalone, dict):
        errors.append("APPROVALS.json standalone_poster must be an object")
    else:
        if standalone.get("status") not in VALID_POSTER_STATUS:
            errors.append("APPROVALS.json standalone_poster.status is invalid")
        if standalone.get("status") == "approved":
            if not str(standalone.get("approved_by") or "").strip():
                errors.append("APPROVALS.json standalone_poster approval needs approved_by")
            parse_iso_datetime(standalone.get("approved_at"), "APPROVALS.json standalone_poster.approved_at", errors)
    return approvals


def css_text(root: Node) -> str:
    chunks = []
    for node in iter_nodes(root):
        if node.tag == "style":
            chunks.append(text_content_direct(node))
        style = node.get("style")
        if style:
            chunks.append(style)
    return "\n".join(chunks)


def text_content_direct(node: Node) -> str:
    return "".join(child for child in node.children if isinstance(child, str))


def css_variables(style: str) -> dict[str, str]:
    return {match.group(1): match.group(2).strip() for match in re.finditer(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;}{]+)", style)}


def resolve_css_value(value: str, variables: dict[str, str], seen: set[str] | None = None) -> str:
    seen = set() if seen is None else seen
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in seen or name not in variables:
            return ""
        seen.add(name)
        value = variables[name]
        value = re.sub(r"var\((--[A-Za-z0-9_-]+)(?:\s*,\s*([^\)]+))?\)", lambda inner: inner.group(2) if inner.group(1) not in variables and inner.group(2) else resolve_css_value("var(" + inner.group(1) + ")", variables, seen), value)
        return resolve_css_value(value, variables, seen.copy())
    return re.sub(r"var\((--[A-Za-z0-9_-]+)(?:\s*,\s*([^\)]+))?\)", replace, value)


def parse_color_tokens(value: str) -> list[tuple[int, int, int]]:
    colors: list[tuple[int, int, int]] = []
    for raw in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", value):
        raw = raw[1:]
        if len(raw) == 3:
            raw = "".join(ch * 2 for ch in raw)
        colors.append(tuple(int(raw[i:i + 2], 16) for i in (0, 2, 4)))
    for match in re.finditer(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*[,/]\s*([\d.]+)(%?))?", value, re.I):
        alpha = match.group(4)
        if alpha is not None:
            # Translucent scrims and shadows (alpha below 0.5) are overlays, not dark surfaces.
            opacity = float(alpha) / (100 if match.group(5) else 1)
            if opacity < 0.5:
                continue
        colors.append(tuple(max(0, min(255, int(match.group(i)))) for i in (1, 2, 3)))
    if re.search(r"\bwhite\b", value, re.I):
        colors.append((255, 255, 255))
    return colors


def relative_luminance(color: tuple[int, int, int]) -> float:
    values = [value / 255 for value in color]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def size_violations(style: str, min_px: float = 14.0) -> list[str]:
    variables = css_variables(style)
    findings = []
    declarations = []
    for match in re.finditer(r"(?:font-size|font)\s*:\s*([^;}{]+)", style, re.I):
        declarations.append(("declaration", match.group(1)))
    for match in re.finditer(r"""font-size\s*=\s*["']([^"']+)""", style, re.I):
        declarations.append(("attribute", match.group(1)))
    for kind, raw in declarations:
        value = resolve_css_value(raw, variables)
        for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(px|rem|em|%)", value, re.I):
            number = float(match.group(1))
            unit = match.group(2).lower()
            minimum = min_px if unit == "px" else min_px / 16 if unit in {"rem", "em"} else min_px / 16 * 100
            if number < minimum:
                findings.append(f"font size {match.group(0)} is below {min_px:g}px in a {kind}")
    return findings


def validate_html_top_contract(root: Node, label: str, errors: list[str]) -> None:
    body = first(root, "body")
    if body is None:
        errors.append(f"{label} is missing body")
        return
    h1s = [node for node in iter_nodes(body) if node.tag == "h1"]
    if len(h1s) != 1:
        errors.append(f"{label} must contain exactly one visible h1")
        return
    h1 = h1s[0]

    def first_visible_content(container: Node) -> Node | str | None:
        for child in container.children:
            if isinstance(child, str):
                if child.strip():
                    return child
                continue
            if child.tag in {"script", "style", "template"}:
                continue
            if child.tag == "h1":
                return child
            direct_text = " ".join(part for part in child.children if isinstance(part, str)).strip()
            has_visible_descendant = any(
                node.tag not in {"script", "style", "template"} and normalized_visible_text(node)
                for node in iter_nodes(child)
            )
            if child.tag in {"main", "article", "div"} and not direct_text and has_visible_descendant:
                result = first_visible_content(child)
                if result is not None:
                    return result
            if normalized_visible_text(child) or child.tag in {"header", "aside", "nav", "section", "img", "button"}:
                return child
        return None

    first_content = first_visible_content(body)
    if first_content is not h1:
        tag = first_content.tag if isinstance(first_content, Node) else "text"
        errors.append(f"{label} has visible content before its unique h1: {tag}")
    parent = h1.parent
    if parent is None:
        errors.append(f"{label} h1 has no parent container")
        return
    siblings = meaningful_nodes(parent.children)
    try:
        index = next(i for i, item in enumerate(siblings) if item is h1)
    except StopIteration:
        errors.append(f"{label} h1 is not in normal document order")
        return
    if index != 0:
        errors.append(f"{label} h1 must be the first visible child of its content container")
    if index + 1 >= len(siblings) or not isinstance(siblings[index + 1], Node) or siblings[index + 1].tag != "section":
        errors.append(f"{label} h1 must be followed directly by the first section")
        return
    first_section = siblings[index + 1]
    section_first = first_visible_content(first_section)
    if not isinstance(section_first, Node) or section_first.tag != "h2":
        errors.append(f"{label} first section must begin with h2 and no title-adjacent copy")
    for node in iter_nodes(body):
        if node.tag != "h2":
            continue
        title = normalized_visible_text(node)
        if re.search(r"来源记录|数据来源|采集日期|证据状态", title):
            errors.append(f"{label} must keep source, capture date, and evidence status outside delivery HTML")


def validate_light_html(path: Path, errors: list[str], min_px: float = 14.0) -> Node | None:
    root = parse_html(path, errors)
    if root is None:
        return None
    validate_html_top_contract(root, path.name, errors)
    body = first(root, "body")
    if body is None:
        errors.append(f"{path.name} is missing body")
        return root
    style = css_text(root)
    if re.search(r"color-scheme\s*:\s*dark", style, re.I):
        errors.append(f"{path.name} must use a light color scheme")
    for finding in size_violations(style, min_px):
        errors.append(f"{path.name}: {finding}")
    variables = css_variables(style)
    for match in re.finditer(r"background(?:-color)?\s*:\s*([^;}{]+)", style, re.I):
        resolved = resolve_css_value(match.group(1), variables)
        dark = [color for color in parse_color_tokens(resolved) if relative_luminance(color) < 0.25]
        if dark:
            opening = style.rfind("{", 0, match.start())
            selector = style[style.rfind("}", 0, opening) + 1:opening].split("@media")[-1] if opening >= 0 else ""
            selector = selector.strip().casefold()
            # Solid colour is allowed on elements smaller than a line of text (visual-design.html, 配色): marks, icons,
            # avatars, badges, chips, tags, logos, corner labels, step pills, coins, pseudo-element bars and controls.
            small_control = any(token in selector for token in SMALL_ELEMENT_TOKENS)
            if not small_control:
                errors.append(f"{path.name} contains a dark background color: {match.group(1).strip()}")
    body_rules = []
    for match in re.finditer(r"(?:(?:html|body)(?:\s*,\s*(?:html|body))?)\s*\{([^{}]*)\}", style, re.I):
        body_rules.append(match.group(1))
    light_backgrounds = []
    for rule in body_rules:
        for match in re.finditer(r"background(?:-color)?\s*:\s*([^;}{]+)", rule, re.I):
            resolved = resolve_css_value(match.group(1), variables)
            light_backgrounds.extend(relative_luminance(color) for color in parse_color_tokens(resolved))
    if light_backgrounds and max(light_backgrounds) < 0.7:
        errors.append(f"{path.name} body background must be white or light")
    visible = normalized_visible_text(body)
    advice = ADVICE_RE.search(visible)
    if advice:
        errors.append(f"{path.name} contains unrequested advisory copy: {advice.group(0)}")
    return root


def poster_brief_has_evidence(session: Path) -> bool:
    path = session / "BRIEF.md"
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    for line in text.splitlines():
        match = re.match(r"^\s*-\s*(Session|Request summary|Primary outcome|Task description):\s*(.+?)\s*$", line, re.I)
        if match and POSTER_TASK_RE.search(match.group(2)):
            return True
    return False


def validate_stage_artifact(path: Path, artifact: str, errors: list[str]) -> None:
    root = validate_light_html(path, errors)
    if root is None:
        return
    main = first(root, "main")
    if main is None or main.get("data-artifact") != artifact:
        errors.append(f'{path.name} must declare data-artifact="{artifact}"')


def validate_session_root(folder: Path, errors: list[str]) -> None:
    finals = {f"{folder.name}{suffix}" for suffix in FINAL_SUFFIXES}
    present = []
    for item in folder.iterdir():
        if item.name == RAW_DIR:
            continue
        if item.name in finals and item.is_file():
            present.append(item.name)
            continue
        errors.append(
            f"session folder may only contain one final deliverable ({folder.name}.html, .xlsx or .docx) "
            f"and {RAW_DIR}/; found {item.name}"
        )
    if len(present) > 1:
        errors.append("session folder holds more than one final deliverable: " + ", ".join(sorted(present)))


def validate(session: Path, strict: bool = False) -> list[str]:
    errors: list[str] = []
    if not session.is_dir():
        return [f"session folder does not exist: {session}"]
    folder = session
    session = work_dir(folder)
    validate_session_root(folder, errors)
    if not session.is_dir():
        return errors + [f"missing {RAW_DIR}/ working folder"]
    match = SESSION_RE.match(folder.name)
    if not match:
        errors.append("session folder must start with a zero-padded number and a title")
    if not (session / "BRIEF.md").is_file():
        errors.append("missing BRIEF.md")
    if not (session / "99-delivery").is_dir():
        errors.append("missing 99-delivery/")
    for name in SYSTEM_DIRS:
        if (session / name).exists():
            errors.append(f"{name}/ is system work and belongs to {OTHER_SKILL}, not a Luz Design session")

    manifest = load_json(session / "99-delivery" / "MANIFEST.json", errors)
    approvals = validate_approvals(session, errors)
    if not (session / "99-delivery" / "APPROVALS.json").is_file():
        errors.append("missing APPROVALS.json")

    if manifest:
        required = {"schema_version", "session_id", "sequence", "folder", "title", "created_at", "session_kind", "status", "modes", "approvals_file", "stages", "deliverables", "assumptions", "verification", "notes"}
        missing = sorted(required - set(manifest))
        if missing:
            errors.append("MANIFEST.json missing: " + ", ".join(missing))
        version = manifest.get("schema_version")
        legacy = version == LEGACY_SCHEMA_VERSION
        if version not in {SCHEMA_VERSION, LEGACY_SCHEMA_VERSION}:
            errors.append(f"MANIFEST.json schema_version must be {SCHEMA_VERSION} (legacy {LEGACY_SCHEMA_VERSION} is still accepted)")
        if manifest.get("status") not in VALID_STATUS:
            errors.append("MANIFEST.json has an invalid status")
        session_kind = manifest.get("session_kind")
        if session_kind == "system":
            errors.append(f"system sessions belong to {OTHER_SKILL}, not Luz-Design")
        elif session_kind not in SESSION_KINDS:
            errors.append("MANIFEST.json has an invalid session_kind")
        poster_session = session_kind == "standalone_poster"
        if manifest.get("folder") != folder.name:
            errors.append("MANIFEST.json folder does not match directory name")
        final = final_html(folder)
        record = manifest.get("final") or {}
        if final.is_file():
            source = session / str(record.get("source", ""))
            actual = sha256_file(final)
            if not record:
                errors.append(f"{final.name} exists but MANIFEST.json has no final record; publish it with scripts/publish.py")
            elif record.get("sha256") != actual:
                errors.append(f"{final.name} differs from its published hash; republish it with scripts/publish.py")
            elif not source.is_file() or sha256_file(source) != actual:
                errors.append(f"{final.name} no longer matches its source {record.get('source')}; republish it")
        elif record:
            errors.append(f"MANIFEST.json records a final HTML but {final.name} is missing")
        expected_title = folder.name.split("-", 1)[1] if "-" in folder.name else ""
        if expected_title and manifest.get("title") != expected_title:
            errors.append("MANIFEST.json title differs from the folder title")
        sid = SESSION_ID_RE.match(str(manifest.get("session_id", "")))
        if not sid:
            errors.append("MANIFEST.json session_id must match SES-NNN")
        elif match:
            expected_sequence = int(match.group(1))
            if int(sid.group(1)) != expected_sequence:
                errors.append("MANIFEST.json session_id sequence differs from folder sequence")
            if manifest.get("sequence") != expected_sequence:
                errors.append("MANIFEST.json sequence differs from folder sequence")
        try:
            datetime.fromisoformat(str(manifest.get("created_at", "")))
        except ValueError:
            errors.append("MANIFEST.json created_at must be ISO-8601")
        if manifest.get("approvals_file") != "99-delivery/APPROVALS.json":
            errors.append("MANIFEST.json approvals_file must be 99-delivery/APPROVALS.json")
        modes = manifest.get("modes", [])
        if not isinstance(modes, list) or len(modes) != len(set(modes)):
            errors.append("MANIFEST.json modes must be a unique list")
            modes = []
        elsewhere = sorted(set(modes) & OTHER_SKILL_MODES)
        if elsewhere:
            errors.append(f"{', '.join(elsewhere)} mode belongs to {OTHER_SKILL}, not Luz-Design")
        unknown = set(modes) - VALID_MODES - OTHER_SKILL_MODES
        if unknown:
            errors.append("unknown modes: " + ", ".join(sorted(unknown)))
        if "visual" in modes and not poster_session:
            errors.append(f"visual mode is standalone visual work and needs session kind standalone_poster; product visuals belong to {OTHER_SKILL}")

        stages = manifest.get("stages", {})
        if not isinstance(stages, dict):
            errors.append("MANIFEST.json stages must be an object")
            stages = {}
        else:
            # Legacy 2.0 manifests list the system stages too; only the visual stage existed then and is checked.
            expected_stages = {"visual"} if legacy else set(STAGE_PATHS)
            missing_stages = sorted(expected_stages - set(stages))
            if missing_stages:
                errors.append("MANIFEST.json stages missing: " + ", ".join(missing_stages))
            if not legacy:
                stray = [name for name in stages if name not in STAGE_PATHS]
                if stray:
                    errors.append(f"MANIFEST.json {SCHEMA_VERSION} stages may only be {', '.join(STAGE_PATHS)}; found " + ", ".join(stray))
            for name, expected_path in STAGE_PATHS.items():
                item = stages.get(name)
                if not isinstance(item, dict):
                    if name in stages:
                        errors.append(f"MANIFEST.json stages.{name} must be an object")
                    continue
                if item.get("path") != expected_path:
                    errors.append(f"MANIFEST.json stages.{name}.path must be {expected_path}")
                if "sha256" not in item or "approval" not in item:
                    errors.append(f"MANIFEST.json stages.{name} needs sha256 and approval")
                staged_hash = item.get("sha256")
                if staged_hash not in {None, ""}:
                    if not SHA256_RE.fullmatch(str(staged_hash)):
                        errors.append(f"MANIFEST.json stages.{name}.sha256 is invalid")
                    else:
                        artifact = session / expected_path
                        if artifact.is_file() and sha256_file(artifact) != staged_hash:
                            errors.append(f"MANIFEST.json stages.{name} hash differs from the artifact")

        for mode in modes:
            mode_dir = MODE_DIRS.get(mode)
            if mode_dir and not (session / mode_dir).is_dir():
                errors.append(f"{mode} mode is declared but {mode_dir}/ is missing")
            for rel in MODE_REQUIRED.get(mode, []):
                if not (session / rel).is_file():
                    errors.append(f"{mode} mode missing required file: {rel}")

        deliverables = manifest.get("deliverables", [])
        if not isinstance(deliverables, list):
            errors.append("MANIFEST.json deliverables must be a list")
            deliverables = []
        ids = set()
        per_mode = {mode: 0 for mode in VALID_MODES}
        for index, item in enumerate(deliverables, 1):
            if not isinstance(item, dict):
                errors.append(f"deliverable {index} must be an object")
                continue
            required_item = {"id", "title", "mode", "path", "format", "status"}
            missing_item = sorted(required_item - set(item))
            if missing_item:
                errors.append(f"deliverable {index} missing: {', '.join(missing_item)}")
                continue
            if not DELIVERABLE_ID_RE.match(str(item["id"])):
                errors.append(f"deliverable {index} has invalid id")
            if item["id"] in ids:
                errors.append(f"duplicate deliverable id: {item['id']}")
            ids.add(item["id"])
            if item.get("mode") not in VALID_MODES:
                errors.append(f"deliverable {index} has invalid mode")
            else:
                per_mode[item["mode"]] += 1
            if item.get("status") not in VALID_STATUS:
                errors.append(f"deliverable {index} has invalid status")
            rel = Path(str(item.get("path", "")))
            if rel.is_absolute():
                errors.append(f"deliverable {index} path must be relative: {rel}")
            else:
                resolved = (session / rel).resolve()
                try:
                    resolved.relative_to(session.resolve())
                except ValueError:
                    errors.append(f"deliverable {index} path escapes session: {rel}")
                else:
                    if not resolved.exists():
                        errors.append(f"deliverable {index} path does not exist: {rel}")

        assumptions = manifest.get("assumptions", [])
        if not isinstance(assumptions, list):
            errors.append("MANIFEST.json assumptions must be a list")
            assumptions = []
        assume_ids = set()
        for index, item in enumerate(assumptions, 1):
            if not isinstance(item, dict):
                errors.append(f"assumption {index} must be an object")
                continue
            if not ASSUMPTION_ID_RE.match(str(item.get("id", ""))):
                errors.append(f"assumption {index} has invalid id")
            if item.get("id") in assume_ids:
                errors.append(f"duplicate assumption id: {item.get('id')}")
            assume_ids.add(item.get("id"))
            if item.get("status") not in {"open", "resolved", "accepted"}:
                errors.append(f"assumption {index} has invalid status")
            if not str(item.get("text", "")).strip():
                errors.append(f"assumption {index} has empty text")
        verification = manifest.get("verification", [])
        if not isinstance(verification, list):
            errors.append("MANIFEST.json verification must be a list")
            verification = []
        for index, item in enumerate(verification, 1):
            if not isinstance(item, dict):
                errors.append(f"verification {index} must be an object")
                continue
            if item.get("result") not in {"pass", "fail", "pending"}:
                errors.append(f"verification {index} has invalid result")
            if not str(item.get("check", "")).strip():
                errors.append(f"verification {index} has empty check")

        def approved(name: str) -> bool:
            item = approvals.get(name) if approvals else None
            return isinstance(item, dict) and item.get("status") == "approved"

        if approved("visual") and not (session / VISUAL_PATH).is_file():
            errors.append(f"approved visual requires {VISUAL_PATH}")
        if (session / VISUAL_PATH).is_file():
            validate_stage_artifact(session / VISUAL_PATH, "visual-board", errors)
        if (session / DOCUMENT_PATH).is_file():
            validate_stage_artifact(session / DOCUMENT_PATH, "document", errors)
        if (session / "02-visual").exists() and not poster_session:
            errors.append(f"visual artifacts belong to a standalone poster session; product visuals belong to {OTHER_SKILL}")
        if poster_session and not poster_brief_has_evidence(session):
            errors.append("standalone poster BRIEF must record an explicit user poster task")
        for mode, mode_dir in MODE_DIRS.items():
            if (session / mode_dir).exists() and mode not in modes:
                errors.append(f"{mode} artifacts exist but {mode} mode is not declared")

        if strict:
            if manifest.get("status") == "draft":
                errors.append("strict: draft session cannot be handed off or published")
            if not verification:
                errors.append("strict: at least one verification record is required")
            for mode in modes:
                if per_mode.get(mode, 0) == 0:
                    errors.append(f"strict: no deliverable is recorded for {mode} mode")
            if any(item.get("result") != "pass" for item in verification if isinstance(item, dict)):
                errors.append("strict: every verification result must be pass")
            for name in modes:
                item = stages.get(name) if isinstance(stages, dict) else None
                if name in STAGE_PATHS and not (isinstance(item, dict) and item.get("sha256")):
                    errors.append(f"strict: MANIFEST.json stages.{name}.sha256 is required")
            if manifest.get("status") == "approved":
                open_items = [item for item in assumptions if isinstance(item, dict) and item.get("status") == "open"]
                if open_items:
                    errors.append("strict: approved session still has open assumptions")
                if any(item.get("status") != "approved" for item in deliverables if isinstance(item, dict)):
                    errors.append("strict: approved session contains non-approved deliverables")
                for name in modes:
                    if name in STAGE_PATHS and not approved(name):
                        errors.append(f"strict: approved session lacks {name} approval")

    for path in session.rglob("*.html"):
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        validate_light_html(path, errors)
    for path in session.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".html"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 text file: {path.relative_to(session)}")
            continue
        for target in local_links(text):
            if not (path.parent / target).resolve().exists():
                errors.append(f"broken local link in {path.relative_to(session)}: {target}")
    if strict:
        brief = session / "BRIEF.md"
        if brief.is_file() and len(brief.read_text(encoding="utf-8").strip()) < 200:
            errors.append("strict: BRIEF.md is not sufficiently completed")
        for path in session.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if re.search(r"\b(?:TODO|TBD|FIXME)\b", text):
                errors.append(f"strict: unresolved marker in {path.relative_to(session)}")
    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Luz Design session.")
    parser.add_argument("session", help="Path to the numbered session folder")
    parser.add_argument("--strict", "--strict-production", dest="strict", action="store_true",
                        help="Require a handed-off session: verification records, deliverables, approvals and hashes")
    args = parser.parse_args(argv)
    session = Path(args.session).resolve()
    errors = validate(session, strict=args.strict)
    if errors:
        print(f"FAIL: {len(errors)} issue(s)")
        for error in errors:
            print("ERROR", error)
        return 1
    print(f"PASS ({'strict' if args.strict else 'session'}): session is valid: {session}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
