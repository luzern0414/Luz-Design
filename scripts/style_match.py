"""Infer adaptive interface layout and visual-style candidates from a brief.

The matcher treats examples such as ``5x2`` or ``three columns`` as evidence.
Only language that explicitly makes an arrangement mandatory becomes a hard
constraint.  The module intentionally uses the standard library so it can run
from a Luz-Design checkout without installing a second toolchain.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
STYLE_MATRIX_PATH = ROOT / "references" / "interface-style-matrix.json"


def _load_styles() -> list[dict[str, Any]]:
    data = json.loads(STYLE_MATRIX_PATH.read_text(encoding="utf-8"))
    return list(data.get("styles", []))


def _as_text(brief: Any) -> str:
    if isinstance(brief, str):
        return brief.strip()
    if isinstance(brief, Mapping):
        return json.dumps(brief, ensure_ascii=False, sort_keys=True)
    return str(brief or "").strip()


def _unique(items: list[Any]) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for item in items:
        marker = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
        if marker not in seen:
            seen.add(marker)
            output.append(item)
    return output


def _normalise_arrangement(raw: str) -> str:
    return re.sub(r"\s*[xX*×]\s*", "×", raw)


def _layout_hints(text: str) -> list[str]:
    hints: list[str] = []
    for match in re.finditer(r"\d{1,3}\s*[xX*×]\s*\d{1,3}", text):
        hints.append(_normalise_arrangement(match.group(0)))
    for match in re.finditer(r"\d{1,3}\s*列", text):
        hints.append(match.group(0).replace(" ", ""))
    for phrase in ("三列", "两列", "单列", "左右分栏", "纵向面板", "网格", "大图", "大幅摄影图"):
        if phrase in text:
            hints.append(phrase)
    return _unique(hints)


def _hard_arrangements(text: str, hints: list[str]) -> list[dict[str, str]]:
    hard: list[dict[str, str]] = []
    markers = ("必须", "固定", "严格使用", "不可调整", "锁定", "强制")
    for hint in hints:
        position = text.find(hint)
        if position < 0 and "×" in hint:
            position = text.find(hint.replace("×", "x"))
        context = text[max(0, position - 14) : position + len(hint) + 14] if position >= 0 else ""
        if any(marker in context for marker in markers):
            hard.append({"type": "arrangement", "value": hint, "reason": "brief explicitly makes this arrangement mandatory"})
    return hard


def _infer_intent(text: str) -> str:
    lowered = text.lower()
    if any(token in text for token in ("非对称", "指标看板", "数据看板", "dashboard")) or "dashboard" in lowered:
        return "asymmetric-dashboard"
    if any(token in text for token in ("杂志", "图文看板", "编辑式")):
        return "editorial-dashboard"
    if any(token in text for token in ("阅读", "文章", "长文", "章节")):
        return "reading-page"
    if any(token in text for token in ("运营看板", "运营数据")):
        return "operations-dashboard"
    if any(token in text for token in ("分析看板", "分析页", "分析数据", "analytics")):
        return "analytics-dashboard"
    if any(token in text for token in ("金刚位", "服务图标", "入口图标", "外卖", "服务入口")):
        return "service-icon-matrix"
    return "adaptive-content"


def _infer_relationships(text: str) -> list[str]:
    relationships: list[str] = []
    if any(token in text for token in ("非对称", "不对称", "非均等")):
        relationships.append("asymmetric")
    if any(token in text for token in ("超大数字", "核心数字", "主指标", "核心指标")):
        relationships.append("primary_metric_anchor")
    if any(token in text for token in ("辅助数据", "辅助指标", "次要指标")):
        relationships.append("supporting_metrics")
    if any(token in text for token in ("右侧", "侧边", "独立纵向", "独立信息面板", "信息面板")):
        relationships.append("independent_context_panel")
    if any(token in text for token in ("文字+大图", "文字和大图", "文图左右", "杂志")):
        relationships.append("editorial_hierarchy")
    if any(token in text for token in ("阅读", "章节", "行长", "阅读宽度")):
        relationships.append("reading_flow")
    if any(token in text for token in ("服务", "图标", "入口")):
        relationships.append("service_group")
    if "非对称" in text:
        relationships.extend(["primary_metric_anchor", "supporting_metrics", "independent_context_panel"])
    return _unique(relationships)


def _style_signals(text: str) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    lowered = text.lower()
    for style in _load_styles():
        aliases = sorted(style.get("aliases", []), key=len, reverse=True)
        for alias in aliases:
            if alias.lower() in lowered:
                signals.append({"style_id": style["id"], "signal": alias, "source": "explicit_reference"})
                break
    cue_map = {
        "gummy": ("q版", "q 弹", "马卡龙", "果冻", "软糖", "可爱", "通透"),
        "inflated-3d": ("充气", "泡泡", "膨胀", "3d", "圆润"),
        "frosted-glass": ("毛玻璃", "磨砂", "半透", "玻璃"),
        "soft-skeuomorphic": ("轻拟物", "浮雕", "光泽"),
        "rounded-line": ("线性", "粗线", "圆角线", "断线"),
        "felt": ("毛毡", "羊毛", "肌理"),
        "clay": ("黏土", "手工"),
        "flat-illustration": ("扁平插画", "平涂", "纯色"),
        "light-flat": ("轻质感", "极简扁平", "无描边"),
        "isometric-2-5d": ("2.5d", "等距", "空间感"),
    }
    for style_id, cues in cue_map.items():
        for cue in cues:
            if cue.lower() in lowered:
                if not any(item["style_id"] == style_id for item in signals):
                    signals.append({"style_id": style_id, "signal": cue, "source": "semantic_cue"})
                break
    return signals


def _motion_signals(text: str) -> list[str]:
    lowered = text.lower()
    signal_map = {
        "morph": ("morphicons", "morph", "平滑变形", "形变"),
        "hover": ("hover", "悬停", "鼠标移入"),
        "loop": ("lordicon loop", "循环动效", "循环播放"),
        "spring": ("spring physics", "弹簧物理", "弹性过渡"),
        "state": ("状态切换", "状态反馈", "选中反馈", "动态交互"),
    }
    return [name for name, aliases in signal_map.items() if any(alias.lower() in lowered for alias in aliases)]


def _interaction_for(signals: list[str]) -> dict[str, Any]:
    if "morph" in signals or "hover" in signals or "state" in signals:
        return {
            "mode": "state-transition",
            "trigger": "hover-or-state-change" if "hover" in signals else "state-change",
            "motion_signals": signals,
            "approval_required": True,
            "rules": ["动效服务于语义、状态或真实物理关系", "提供 reduced-motion 降级", "不让动效承担唯一语义"],
        }
    if "loop" in signals:
        return {
            "mode": "ambient-loop",
            "trigger": "explicit-loop-request",
            "motion_signals": signals,
            "approval_required": True,
            "rules": ["循环只用于明确的装饰或等待状态", "提供暂停或 reduced-motion 降级"],
        }
    return {
        "mode": "static-with-state-feedback",
        "trigger": "interaction-state",
        "motion_signals": signals,
        "approval_required": False,
        "rules": ["默认使用颜色、层级和图标状态反馈", "需要动效时先提出候选并确认"],
    }


def parse_brief(brief: Any) -> dict[str, Any]:
    text = _as_text(brief)
    hints = _layout_hints(text)
    count_match = re.search(r"(?<!\d)(\d{1,3})\s*(?:枚|个|项|类|种|张)", text)
    item_count = int(count_match.group(1)) if count_match else None
    return {
        "text": text,
        "layout_intent": _infer_intent(text),
        "layout_hints": hints,
        "hard_constraints": _hard_arrangements(text, hints),
        "relationships": _infer_relationships(text),
        "style_signals": _style_signals(text),
        "motion_signals": _motion_signals(text),
        "item_count": item_count,
        "theme_signals": {
            "dark_requested": "深色" in text or "黑色背景" in text,
            "light_requested": "浅色" in text or "白色背景" in text or "纯白背景" in text,
        },
    }


def _resolved_parsed(brief: Any) -> dict[str, Any]:
    if isinstance(brief, Mapping) and "layout_intent" in brief and "layout_hints" in brief:
        return dict(brief)
    return parse_brief(brief)


def _width(viewport: Mapping[str, Any] | None) -> int:
    try:
        return max(240, int((viewport or {}).get("width", 1280)))
    except (TypeError, ValueError):
        return 1280


def _content_number(content: Mapping[str, Any], keys: tuple[str, ...], default: int) -> int:
    for key in keys:
        value = content.get(key)
        if value is not None:
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                continue
    return default


def dock_grid(item_count: int, longest_label: int = 4, width: int = 375) -> dict[str, Any]:
    """Columns, rows and paging of a mini-program icon dock (visual-design.html 金刚区与宫格入口, 推导步骤).

    Inputs: entries n, longest label L in characters, screen width W (320-430).  cellMin = max(56, 12 L + 8);
    cMax = min(5, floor((W - 2m) / cellMin)) and at least 3, with m = 12 up to 375 wide and 16 beyond;
    c = the smallest column count that fits in two rows and divides n, else leaves a last row of at least half
    of c, else cMax.  More than two rows page sideways, two rows a page, at most three pages; a last page under
    half full is folded into an "all" entry so every page is full.
    """
    n = max(1, int(item_count))
    label = max(1, int(longest_label))
    w = min(430, max(320, int(width)))
    margin = 12 if w <= 375 else 16
    cell_min = max(56, label * 14 + 8)
    fit = (w - 2 * margin) // cell_min
    c_max = max(3, min(5, fit))
    notes: list[str] = []
    if fit < 3:
        notes.append("放不下 3 列：缩短文案")
    candidates = [c for c in range(3, c_max + 1) if c >= math.ceil(n / 2)]
    columns = c_max
    for c in candidates:
        if n % c == 0:
            columns = c
            break
    else:
        for c in candidates:
            if n - c * (math.ceil(n / c) - 1) >= math.ceil(c / 2):
                columns = c
                break
    rows = math.ceil(n / columns)
    pages, visible, folded = 1, n, False
    if rows > 2:
        per_page = 2 * columns
        pages = math.ceil(n / per_page)
        last = n - (pages - 1) * per_page
        if pages > 3:
            pages, folded = 3, True
        elif last * 2 < per_page:
            pages, folded = pages - 1, True
        if folded:
            visible = pages * per_page - 1
            notes.append(f"末页不足半页：{visible} 项加“全部”入口，每页满格")
        rows = 2
    return {
        "entries": n, "longest_label": label, "screen_width": w, "page_margin": margin,
        "cell_min": cell_min, "columns_max": c_max, "columns": columns, "rows": rows,
        "pages": pages, "visible_entries": visible, "all_entry": folded,
        "cell_width": round((w - 2 * margin) / columns, 1), "cell_height": 80, "notes": notes,
    }


def _adaptive_columns(width: int, item_count: int, min_card: int = 112, cap: int = 6) -> int:
    container = width - (32 if width < 600 else 96)
    gap = 16
    columns = max(1, int((container + gap) // (min_card + gap)))
    if width < 600:
        columns = min(columns, 3)
    return max(1, min(item_count or 1, columns, cap))


def infer_layout(brief: Any, viewport: Mapping[str, Any] | None = None, content: Mapping[str, Any] | None = None) -> dict[str, Any]:
    parsed = _resolved_parsed(brief)
    content = dict(content or {})
    width = _width(viewport)
    intent = parsed.get("layout_intent", "adaptive-content")
    item_count = _content_number(content, ("items", "item_count"), parsed.get("item_count") or 6)
    relationships = list(parsed.get("relationships", []))
    hard_constraints = list(parsed.get("hard_constraints", []))
    decisions: list[str] = []
    adaptation: list[dict[str, Any]] = []

    if intent == "service-icon-matrix":
        dock = None
        if width <= 430:
            label = _content_number(content, ("longest_label", "label_chars"), 4)
            dock = dock_grid(item_count, label, width)
            columns, rows, grid = dock["columns"], dock["rows"], "icon-dock"
        else:
            columns = _adaptive_columns(width, item_count, min_card=112, cap=6)
            grid = "adaptive-matrix"
            rows = math.ceil(item_count / columns) if columns else 0
        if hard_constraints:
            arrangement = re.fullmatch(r"(\d+)×(\d+)", hard_constraints[0]["value"])
            if arrangement:
                columns, rows = int(arrangement.group(1)), int(arrangement.group(2))
                grid = hard_constraints[0]["value"].replace("×", "x")
                dock = None
        regions = [{"id": "service-items", "role": "entry-icons", "columns": columns, "rows": rows}]
        main_ratio = "1:1"
        rail_position = "none"
        if dock:
            regions[0]["dock"] = dock
            decisions.append(f"金刚区按“金刚区与宫格入口”推导：{dock['entries']} 个入口、最长文案 {dock['longest_label']} 字、屏宽 {dock['screen_width']}，"
                             f"最多 {dock['columns_max']} 列，得到 {columns} 列 {rows} 行" + (f"、{dock['pages']} 页" if dock["pages"] > 1 else "")
                             + ("".join("；" + note for note in dock["notes"])))
            adaptation.append({"viewport": "narrow", "columns": columns, "pages": dock["pages"], "reason": "icon-dock formula"})
        else:
            decisions.append(f"按 {item_count} 个对象、{width}px 视口和最小卡片宽度计算 {columns} 列")
            adaptation.append({"viewport": "narrow" if width < 600 else "wide", "columns": columns, "reason": "card-fit"})
        if hard_constraints:
            decisions.append("brief 明确锁定排列，因此保留该约束；否则只保留为参考信号")
    elif intent == "asymmetric-dashboard":
        primary = _content_number(content, ("primary_metrics", "primary"), 1)
        supporting = _content_number(content, ("supporting_metrics", "supporting"), 4)
        panel_items = _content_number(content, ("panel_items", "context_items"), 4)
        if width < 680:
            columns = 1
            grid = "stacked-adaptive"
            rail_position = "collapsible"
            main_ratio = "1:1"
            regions = [
                {"id": "primary", "role": "anchor", "order": 1},
                {"id": "supporting", "role": "support", "order": 2, "items": supporting},
                {"id": "context", "role": "independent-panel", "order": 3, "collapsed": True, "items": panel_items},
            ]
            decisions.append("窄视口先保证主指标和扫描顺序，独立面板折叠到内容流")
            adaptation.append({"viewport": "narrow", "columns": 1, "rail": "collapsible", "reason": "preserve reading order"})
        else:
            columns = 12 if width >= 1100 else 8
            grid = f"{columns}-col-adaptive"
            rail_position = "right" if width >= 1100 else "bottom"
            rail_span = max(2, min(4, math.ceil(max(panel_items, 1) / 4)))
            support_span = max(2, min(5, math.ceil(max(supporting, 1) / 2)))
            main_span = max(3, columns - rail_span - support_span)
            main_ratio = f"{main_span}:{support_span + rail_span}"
            regions = [
                {"id": "primary", "role": "anchor", "span": main_span, "items": primary},
                {"id": "supporting", "role": "support", "span": support_span, "items": supporting},
                {"id": "context", "role": "independent-panel", "span": rail_span, "placement": rail_position, "items": panel_items},
            ]
            decisions.append(f"以主指标、辅助指标和信息面板的内容量分配 {columns} 列区域")
            adaptation.append({"viewport": "wide" if width >= 1100 else "medium", "columns": columns, "rail": rail_position, "reason": "content-weighted spans"})
    elif intent == "editorial-dashboard":
        images = _content_number(content, ("images", "image_count"), 6)
        if width < 680:
            columns, gallery_columns = 1, min(2, max(1, images))
            regions = [{"id": "lead", "role": "text-media-stack"}, {"id": "gallery", "role": "image-grid", "columns": gallery_columns, "items": images}]
            main_ratio, rail_position, grid = "1:1", "none", "stacked-editorial"
        else:
            columns, gallery_columns = (12 if width >= 1100 else 8), min(4, max(2, math.ceil(math.sqrt(max(images, 1)))))
            regions = [{"id": "lead", "role": "text-media-split", "span": max(4, columns // 2)}, {"id": "gallery", "role": "image-grid", "span": columns, "columns": gallery_columns, "items": images}]
            main_ratio, rail_position, grid = "5:7", "none", f"{columns}-col-editorial"
        decisions.append("根据文字量、图片数量和视口决定主图分栏与图网格列数")
        adaptation.append({"viewport": "narrow" if width < 680 else "wide", "gallery_columns": gallery_columns, "reason": "image-fit"})
    elif intent == "reading-page":
        columns, grid, main_ratio, rail_position = 1, "reading-measure", "1:1", "none"
        regions = [{"id": "article", "role": "reading-flow", "measure": "45–75ch"}]
        decisions.append("优先控制阅读宽度、章节层级和渐进披露，不用装饰性卡片填空")
        adaptation.append({"viewport": "all", "measure": "45–75ch", "reason": "reading comfort"})
    else:
        columns = _adaptive_columns(width, item_count, min_card=180, cap=6)
        grid, main_ratio, rail_position = "adaptive-content", "1:1", "none"
        regions = [{"id": "content", "role": "content-flow", "columns": columns, "items": item_count}]
        decisions.append(f"根据 {item_count} 个内容对象和最小内容宽度计算列数")
        adaptation.append({"viewport": "narrow" if width < 600 else "wide", "columns": columns, "reason": "content-fit"})

    return {
        "intent": intent,
        "grid": grid,
        "columns": columns,
        "regions": regions,
        "main_ratio": main_ratio,
        "rail_position": rail_position,
        "hard_constraints": hard_constraints,
        "relationships": relationships,
        "decisions": decisions,
        "adaptation": adaptation,
    }


def _default_style_order(intent: str) -> list[str]:
    if intent == "service-icon-matrix":
        return ["gummy", "inflated-3d", "flat-illustration", "rounded-line"]
    if intent == "asymmetric-dashboard":
        return ["light-flat", "rounded-line", "flat-illustration", "isometric-2-5d"]
    if intent == "reading-page":
        return ["light-flat", "flat-illustration", "rounded-line", "felt"]
    return ["flat-illustration", "light-flat", "rounded-line", "isometric-2-5d"]


def rank_styles(brief: Any) -> list[dict[str, Any]]:
    parsed = _resolved_parsed(brief)
    styles = {style["id"]: style for style in _load_styles()}
    scores: dict[str, float] = {style_id: 0.0 for style_id in styles}
    reasons: dict[str, list[str]] = {style_id: [] for style_id in styles}
    for signal in parsed.get("style_signals", []):
        style_id = signal["style_id"]
        if style_id in scores:
            weight = 6.0 if signal["source"] == "explicit_reference" else 3.0
            scores[style_id] += weight
            reasons[style_id].append(f"检测到“{signal['signal']}”视觉信号")
    for index, style_id in enumerate(_default_style_order(parsed.get("layout_intent", "adaptive-content"))):
        if style_id in scores:
            scores[style_id] += max(1.0, 2.5 - index * 0.5)
            reasons[style_id].append("与当前内容角色的形态和可读性相容")
    ranked = sorted(styles.values(), key=lambda style: (-scores[style["id"]], _default_style_order(parsed.get("layout_intent", "adaptive-content")).index(style["id"]) if style["id"] in _default_style_order(parsed.get("layout_intent", "adaptive-content")) else 99, style["id"]))
    output: list[dict[str, Any]] = []
    for style in ranked[:3]:
        style_id = style["id"]
        output.append({
            "id": style_id,
            "label": style["label"],
            "score": round(scores[style_id], 2),
            "reasons": reasons[style_id] or ["作为低风险起始参数，在可配置界面中结合品牌气质调整"],
            "suitable_roles": style["suitable_roles"],
            "avoid": style["avoid"],
            "accessibility_risks": style["accessibility_risks"],
            "approval_scope": style["approval_scope"],
        })
    return output


def _default_approval(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "pending",
        "candidates": [candidate["id"] for candidate in candidates],
        "selectedStyle": None,
        "scope": {"controls": "line-vector", "entryIcons": None, "metricIllustrations": None, "heroDecorations": None, "emptyState": None},
    }


def build_match(
    brief: Any,
    viewport: Mapping[str, Any] | None = None,
    content: Mapping[str, Any] | None = None,
    approval: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    parsed = parse_brief(brief)
    layout = infer_layout(parsed, viewport=viewport, content=content)
    candidates = rank_styles(parsed)
    result = {
        "schema_version": "1.0",
        "brief": parsed["text"],
        "semantic": {"intent": parsed["layout_intent"], "relationships": parsed["relationships"]},
        "evidence": {
            "layout_hints": parsed["layout_hints"],
            "style_signals": parsed["style_signals"],
            "motion_signals": parsed["motion_signals"],
            "theme_signals": parsed["theme_signals"],
        },
        "layout": layout,
        "candidates": candidates,
        "interaction": _interaction_for(parsed["motion_signals"]),
        "approval": copy.deepcopy(dict(approval)) if approval is not None else _default_approval(candidates),
    }
    return result


def can_design(match: Mapping[str, Any]) -> bool:
    """A usable candidate can be previewed; this never grants human approval.

    Formal output and Imagegen still use the separate current-research gate.
    ``approval`` is retained for old records, not an upfront generation gate.
    """
    approval = match.get("approval", {})
    if not isinstance(approval, Mapping) or approval.get("status") == "rejected":
        return False
    selected = approval.get("selectedStyle")
    candidate_ids = {candidate.get("id") for candidate in match.get("candidates", [])}
    if not candidate_ids or (selected is not None and selected not in candidate_ids):
        return False
    scope = approval.get("scope", {})
    return isinstance(scope, Mapping) and scope.get("controls") == "line-vector"


def _approval_errors(match: Mapping[str, Any]) -> list[str]:
    approval = match.get("approval", {})
    if not isinstance(approval, Mapping):
        return ["界面 approval 必须是对象"]
    status = approval.get("status", "pending")
    if status not in {"pending", "approved", "rejected", "not_requested"}:
        return ["界面 approval.status 无效"]
    if status != "approved":
        return []
    by = str(approval.get("approved_by") or approval.get("by") or "").strip()
    at = str(approval.get("approved_at") or approval.get("at") or "").strip()
    note = str(approval.get("note") or "").strip()
    errors = []
    if not by or not at or not note:
        errors.append("界面风格确认缺少审批人、时间和用户确认依据")
    if re.search(r"\b(auto|model|system|validator|script|assistant|agent|codex|ai)\b|模型|脚本|自动|智能体", by, re.I):
        errors.append("界面风格不能由模型、脚本或自动程序代替用户批准")
    if at:
        try:
            datetime.fromisoformat(at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("界面风格确认时间必须是 ISO 时间")
    selected = approval.get("selectedStyle")
    candidates = {candidate.get("id") for candidate in match.get("candidates", [])}
    scope = approval.get("scope", {})
    if not selected or selected not in candidates or not isinstance(scope, Mapping) or scope.get("controls") != "line-vector":
        errors.append("界面风格确认必须引用候选并保留 controls=line-vector")
    return errors


def _load_json(path: str | None) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else None


def session_style_errors(session: Path, *, required: bool = False) -> list[str]:
    """Validate existing legacy approval claims without blocking a draft UI.

    Configurable UI is the review artifact. No style-match record or a pending
    record is a normal state before the person returns their full parameters.
    """
    raw = Path(session) / "raw"
    path = raw / "02-visual" / "style-match.json"
    if not path.exists():
        return []
    try:
        match = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(match, Mapping):
            return ["界面风格匹配必须是 JSON 对象：raw/02-visual/style-match.json"]
        return _approval_errors(match)
    except (OSError, ValueError, TypeError, KeyError):
        return ["无法读取界面风格匹配：raw/02-visual/style-match.json"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Infer adaptive UI layout and style candidates from a brief")
    parser.add_argument("--brief", help="Natural-language design brief")
    parser.add_argument("--input", help="JSON file containing brief, viewport and content")
    parser.add_argument("--approval", help="JSON approval object or result file")
    parser.add_argument("--output", help="Write JSON result to this path")
    parser.add_argument("--session", help="Design session; inferred from LUZ_DESIGN_SESSION or the output path")
    parser.add_argument("--stage", help="Business stage; defaults to LUZ_CRAWL_STAGE or design")
    parser.add_argument("--check-design", action="store_true", help="Read-only candidate-scope check; human approval is not needed to preview")
    parser.add_argument("--dock", nargs=3, type=int, metavar=("ENTRIES", "LONGEST_LABEL", "WIDTH"),
                        help="derive a mini-program icon dock from entries, longest label (characters) and screen width, then exit")
    args = parser.parse_args(argv)
    if args.dock:
        print(json.dumps(dock_grid(*args.dock), ensure_ascii=False, indent=2))
        return 0
    payload = _load_json(args.input) or {}
    brief = args.brief or payload.get("brief", "")
    viewport = payload.get("viewport")
    content = payload.get("content")
    approval = _load_json(args.approval) if args.approval else None
    if approval and "approval" in approval:
        approval = approval["approval"]
    result = build_match(brief, viewport=viewport, content=content, approval=approval)
    errors = _approval_errors(result)
    if errors:
        print("FAIL: " + "; ".join(errors), file=sys.stderr)
        return 2
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output and not args.check_design:
        from crawl_gate import require_session_preflight
        try:
            context = require_session_preflight(args.session, args.output, stage=args.stage)
            output = Path(args.output).resolve()
            if not output.is_relative_to(context["raw"]) or output.suffix.lower() != ".json":
                raise ValueError("风格匹配结果是待核实的研究候选 JSON，必须保存在本会话 raw 中")
        except ValueError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 2
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    if args.check_design and not can_design(result):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
