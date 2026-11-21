"""Verified, exact-output handoff for public Design document writers.

Other skills may reuse the generators after their own Crawl and template gates.
They pass a context issued here, bound to the selected final artifact and one
raw working output. A dictionary or an environment skip flag cannot grant it.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
_TOKEN = object()
_MODULES = {}


def _load(name, path):
    path = Path(path).resolve()
    if path not in _MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ValueError(f"无法加载正式输出门禁: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[path] = module
    return _MODULES[path]


def _crawl():
    root = Path(os.environ.get("LUZ_CRAWL_ROOT") or HERE.parents[1] / "Luz-Crawl")
    return _load("_luz_document_api_crawl", root / "scripts" / "crawl_preflight.py")


def _library():
    # Use the canonical Design module even when a caller has its own module
    # named crawl_gate or template_library already imported.
    return _load("_luz_document_api_templates", HERE / "template_library.py")


class VerifiedOutputContext:
    __slots__ = ("_binding",)

    def __init__(self, binding, *, _token=None):
        if _token is not _TOKEN:
            raise ValueError("上下文必须由 verified_output_context 核验后创建")
        object.__setattr__(self, "_binding", tuple(binding))

    def __setattr__(self, name, value):
        raise AttributeError("VerifiedOutputContext is immutable")

    @property
    def evidence_root(self):
        return self._binding[0]

    @property
    def caller(self):
        return self._binding[1]

    @property
    def stage(self):
        return self._binding[2]

    @property
    def template_target(self):
        return self._binding[3]

    @property
    def template_id(self):
        return self._binding[4]

    @property
    def output(self):
        return self._binding[5]

    @property
    def template_root(self):
        return self._binding[6]


def _check(root, caller, stage, target, template_id, output, template_root=None):
    module = _crawl()
    if caller not in module.CALLERS:
        raise ValueError("正式输出上下文的 caller 无效")
    if not isinstance(stage, str) or not stage.strip():
        raise ValueError("正式输出上下文必须使用显式 stage")
    root = Path(root).resolve()
    state = module.state_root(root)
    evidence_caller, approved = caller, False
    if state is not None:
        root = Path(state).resolve()
        manifest = json.loads((root / "project.json").read_text(encoding="utf-8-sig"))
        item = next((item for item in manifest.get("stages", []) if item.get("id") == stage), None)
        if not isinstance(item, dict) or item.get("owner") not in module.CALLERS:
            raise ValueError(f"正式输出上下文没有对应的真实项目阶段: {stage}")
        if caller == "luz-project":
            evidence_caller = item["owner"]
        elif manifest.get("workflow") == "commercial-v1" and caller in item.get("contributors", []):
            evidence_caller = module.stage_evidence_caller(root, caller, stage)
        elif item["owner"] != caller:
            raise ValueError(f"正式输出上下文不能借用其他技能的项目阶段: {stage}")
        approved = item.get("status") in {"approved", "completed"}
    errors = module.validate_preflight(root, evidence_caller, stage)
    if approved:
        # The existing project rule waives age only after stage approval.
        errors = [error for error in errors if "检索记录超过七天" not in error]
    if errors:
        raise ValueError("Crawl 前置检索: " + "; ".join(errors))
    target, output = Path(target).resolve(), Path(output).resolve()
    template_root = Path(template_root).resolve() if template_root is not None else root
    if template_root != root:
        if caller != "luz-design":
            raise ValueError("只有真实关联的 Design 会话可以单独保存模板记录")
        gate = _load("_luz_design_document_api_session", HERE / "crawl_gate.py")
        _, resolved = gate._context(template_root, target, stage=stage)
        if resolved["evidence_root"] != root or resolved["template_root"] != template_root:
            raise ValueError("Design 模板记录与本阶段证据或输出位置不属于同一会话")
    _library().require_selected(template_root, caller, stage, target, template_id)
    if output != target:
        raw = template_root if template_root == root and state is not None else template_root / "raw"
        if output == raw or not output.is_relative_to(raw):
            raise ValueError("已核验上下文的工作输出必须在本次会话或项目状态根 raw 过程目录内")
    return root, caller, stage, target, template_id, output, template_root


def verified_output_context(evidence_root, caller, stage, template_target, template_id, *, working_output=None, template_root=None):
    """Validate current evidence/selection and bind one specific output.

    A working DOCX/XLSX may live in raw while its selected final PDF/XLSX is
    elsewhere. Its caller still copies, checks and records the final artifact.
    This never creates evidence, selects a template or records approval.
    """
    binding = _check(evidence_root, caller, stage, template_target, template_id,
                     working_output if working_output is not None else template_target, template_root)
    return VerifiedOutputContext(binding, _token=_TOKEN)


def require_output_context(output, template_id, *, context=None, session=None, stage=None):
    """Recheck a scoped handoff, or obtain the writer's own Design gate."""
    output = Path(output).resolve()
    if context is None:
        gate = _load("_luz_design_document_api_session", HERE / "crawl_gate.py")
        stage = stage or os.environ.get("LUZ_CRAWL_STAGE")
        resolved = gate.require_session_preflight(session, output, stage=stage, template_id=template_id)
        return verified_output_context(resolved["evidence_root"], resolved["caller"], resolved["stage"], output, template_id,
                                       template_root=resolved["template_root"])
    if not isinstance(context, VerifiedOutputContext):
        raise ValueError("context 必须是经过 verified_output_context 核验的上下文")
    if context.output != output or context.template_id != template_id:
        raise ValueError("已核验上下文与本次输出位置或模板不一致")
    _check(*context._binding)
    return context


def record_rendered_output(context, output, template_id, *, generator):
    """Bind generated bytes; format checks and approval remain separate."""
    context = require_output_context(output, template_id, context=context)
    if context.template_target == Path(output).resolve():
        return _library().record_output(context.template_root, context.caller, context.stage,
                                        output, template_id, generator=generator)
    # A raw working source is not the selected final deliverable. The owning
    # skill records that target after its checked copy/export has succeeded.
    return None
