"""文件模板库索引：读 templates/documents/*/manifest.json，检查后写 templates/documents/documents.html。

    py -X utf8 scripts/build_documents_index.py              检查并写出 registry.js，有错误时不写、退出码 1
    py -X utf8 scripts/build_documents_index.py --check      只检查
    py -X utf8 scripts/build_documents_index.py --partial    某类还没写 manifest 时跳过它（只在编写途中用）

检查内容：
  类型      目录名与 manifest.type 一致，五类 word excel slides pdf reading 各有一份 manifest
  编号      模板 DC-<WD|XL|SL|PD|RD>-NNN，可复用块 DC-<…>-PNN；全库唯一；序号从 001（P01）起连续（有缺号只提醒）
  命名      naming 与 file 的扩展名一致；file 必须是 samples/<编号>-<名称>.<扩展名>，spec 必须是 specs/<编号>-<名称>.json
  文件      file、spec、parts 的 file、可选的 preview 都存在且在本类目录内
  字段      use、generator 非空，checks 与 fields 是列表
  复用块    used_in 里的编号存在且属于同一类；没有被任何模板使用的块只提醒
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "templates" / "documents"

# 目录名 -> (编号代码, 默认标题, 扩展名)
TYPES = {
    "word": ("WD", "文字文档", "docx"),
    "excel": ("XL", "表格文件", "xlsx"),
    "slides": ("SL", "幻灯片", "pptx"),
    "pdf": ("PD", "PDF", "pdf"),
    "reading": ("RD", "阅读网页", "html"),
}
ILLEGAL_NAME = re.compile(r'[\\/:*?"<>|\s]')

errors: list[str] = []
warnings: list[str] = []


def err(where: str, text: str) -> None:
    errors.append(f"{where}：{text}")


def warn(where: str, text: str) -> None:
    warnings.append(f"{where}：{text}")


def inside(base: Path, relative: str) -> Path | None:
    """relative 解析后必须仍在 base 里面。"""
    target = (base / relative).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    return target


def check_type(folder: str, partial: bool):
    code, default_title, ext = TYPES[folder]
    base = DOCS / folder
    manifest_path = base / "manifest.json"
    where = f"{folder}/manifest.json"
    if not manifest_path.is_file():
        (warn if partial else err)(where, "缺少 manifest.json")
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        err(where, f"不是合法 JSON：{exc}")
        return None
    if data.get("type") != folder:
        err(where, f"type 是 {data.get('type')!r}，应为 {folder!r}")
    title = data.get("title") or default_title
    naming = data.get("naming", "")
    if not re.fullmatch(rf"DC-{code}-三位序号-中文名\.{ext}", naming):
        err(where, f"naming 应为 DC-{code}-三位序号-中文名.{ext}，现为 {naming!r}")
    items, parts = data.get("items"), data.get("parts", [])
    if not isinstance(items, list):
        err(where, "items 必须是列表")
        return None
    if not isinstance(parts, list):
        err(where, "parts 必须是列表")
        parts = []
    if not items:
        warn(where, "items 为空")

    id_re = re.compile(rf"DC-{code}-(\d{{3}})")
    seen: set[str] = set()
    numbers: list[int] = []
    out_items = []
    for index, item in enumerate(items, 1):
        item_id = item.get("id", "")
        label = f"{folder} 第 {index} 个模板 {item_id or '（无编号）'}"
        match = id_re.fullmatch(item_id)
        if not match:
            err(label, f"编号格式应为 DC-{code}-NNN（三位数字）")
        elif item_id in seen:
            err(label, "编号重复")
        else:
            numbers.append(int(match.group(1)))
        seen.add(item_id)
        name = item.get("name", "")
        if not name:
            err(label, "缺少 name")
        elif ILLEGAL_NAME.search(name):
            err(label, f"name 含空白或不能进文件名的字符：{name!r}")
        for key in ("use", "generator"):
            if not str(item.get(key, "")).strip():
                err(label, f"缺少 {key}")
        for key in ("checks", "fields"):
            if not isinstance(item.get(key), list) or not item.get(key):
                err(label, f"{key} 必须是非空列表")
        for key, folder_name, suffix in (("file", "samples", ext), ("spec", "specs", "json")):
            value = item.get(key, "")
            if not value:
                err(label, f"缺少 {key}")
                continue
            expected = f"{folder_name}/{item_id}-{name}.{suffix}"
            if value != expected:
                err(label, f"{key} 应为 {expected}，现为 {value}")
            target = inside(base, value)
            if target is None:
                err(label, f"{key} 指到类目录之外：{value}")
            elif not target.is_file():
                err(label, f"{key} 指向的文件不存在：{value}")
        preview = item.get("preview")
        if preview:
            target = inside(base, preview)
            if target is None or not target.is_file():
                err(label, f"preview 指向的文件不存在：{preview}")
        out_items.append(item)
    if numbers and sorted(numbers) != list(range(1, max(numbers) + 1)):
        missing = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
        warn(where, f"模板序号有缺号：{', '.join(f'{n:03d}' for n in missing)}")

    part_re = re.compile(rf"DC-{code}-P(\d{{2}})")
    part_seen: set[str] = set()
    part_numbers: list[int] = []
    used: set[str] = set()
    out_parts = []
    for index, part in enumerate(parts, 1):
        part_id = part.get("id", "")
        label = f"{folder} 第 {index} 个复用块 {part_id or '（无编号）'}"
        match = part_re.fullmatch(part_id)
        if not match:
            err(label, f"编号格式应为 DC-{code}-PNN（两位数字）")
        elif part_id in part_seen:
            err(label, "编号重复")
        else:
            part_numbers.append(int(match.group(1)))
        part_seen.add(part_id)
        if not part.get("name"):
            err(label, "缺少 name")
        value = part.get("file", "")
        target = inside(base, value) if value else None
        if not value:
            err(label, "缺少 file")
        elif target is None:
            err(label, f"file 指到类目录之外：{value}")
        elif not target.is_file():
            err(label, f"file 指向的文件不存在：{value}")
        elif not target.name.startswith(f"{part_id}-"):
            err(label, f"文件名应以 {part_id}- 开头：{target.name}")
        users = part.get("used_in")
        if not isinstance(users, list):
            err(label, "used_in 必须是列表")
            users = []
        for user in users:
            if user not in seen:
                err(label, f"used_in 里的 {user} 不是本类的模板编号")
            used.add(user)
        if not users:
            warn(label, "没有被任何模板使用")
        out_parts.append(part)
    if part_numbers and sorted(part_numbers) != list(range(1, max(part_numbers) + 1)):
        missing = sorted(set(range(1, max(part_numbers) + 1)) - set(part_numbers))
        warn(where, f"复用块序号有缺号：{', '.join(f'P{n:02d}' for n in missing)}")

    return {
        "type": folder, "code": code, "title": title, "dir": folder, "naming": naming, "ext": ext,
        "items": out_items, "parts": out_parts,
    }


def collect(partial: bool = False) -> list[dict] | None:
    """Check every manifest; the checked types, or None when there are errors."""
    types = []
    for folder in TYPES:
        result = check_type(folder, partial)
        if result is not None:
            types.append(result)
    all_ids = [i["id"] for t in types for i in t["items"]] + [p["id"] for t in types for p in t["parts"]]
    for dup in sorted({x for x in all_ids if all_ids.count(x) > 1}):
        err("全库", f"编号 {dup} 出现在多处")
    for text in warnings:
        print("提醒", text)
    for text in errors:
        print("错误", text)
    total_items = sum(len(t["items"]) for t in types)
    total_parts = sum(len(t["parts"]) for t in types)
    print(f"{len(types)} 类，{total_items} 个模板，{total_parts} 个复用块；{len(errors)} 个错误，{len(warnings)} 个提醒")
    return None if errors else types


def build() -> int:
    """Write templates/documents/documents.html (through build_templates, which owns the single-file shell)."""
    types = collect()
    if types is None:
        print("未通过，没有写 documents.html")
        return 1
    import build_templates
    build_templates.write_documents(types)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="文件模板库：检查 manifest，写 documents.html")
    parser.add_argument("--check", action="store_true", help="只检查，不写 documents.html")
    parser.add_argument("--partial", action="store_true", help="缺 manifest 的类型只提醒（编写途中用）")
    args = parser.parse_args(argv)
    if args.check:
        types = collect(args.partial)
        if types is None:
            return 1
        print("通过")
        return 0
    return build()


if __name__ == "__main__":
    sys.exit(main())
