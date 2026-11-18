#!/usr/bin/env python3
"""Check the poster prompt library and write prompts.js for the viewer page.

The viewer (templates/poster/source/prompts/viewer.html) cannot fetch a local json file, so it loads
window.LZ_PROMPTS from prompts.js. This script reads prompts.json and styles.json, runs the checks below,
and only then writes prompts.js.

  py -X utf8 scripts/build_prompts_js.py            check, then write prompts.js
  py -X utf8 scripts/build_prompts_js.py --check    check only; also fails when prompts.js is out of date
  py -X utf8 scripts/build_prompts_js.py --dir <folder>

Checks: ids PP-001.. continuous and unique; every field present and well-typed; name 4-12 Chinese characters;
category, role, ratio, resolution, background and format in their allowed sets; the eight slot labels in order
(Purpose, Subject, Composition, Lighting, Material, Color, Background and output, Avoid); the Avoid line is last and
equals the negative text; the referenced style block (lighting, material, color rule) and negative group appear
verbatim in the prompt; element sheets list exactly 16 numbered objects on a transparent 1:1 sheet; placeholders
are only {{primary}} and {{secondary}}; result and source files exist; verified entries equal their source text.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[1] / "templates" / "poster" / "source" / "prompts"

FIELDS = {
    "id": str, "name": str, "category": str, "use": str, "role": str, "ratio": str, "resolution": str, "background": str,
    "format": str, "prompt": str, "negative": str, "style_ref": list, "negative_ref": str, "checks": list, "verified": bool,
    "result": str, "source": str, "notes": str,
}
ROLES = {"background", "icon-sheet", "illustration", "photo", "poster"}
RATIOS = {"1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2"}  # the ratios the local Imagegen accepts
RESOLUTIONS = {"1k", "2k", "4k"}
BACKGROUNDS = {"opaque", "transparent"}
FORMATS = {"png", "webp", "jpeg"}
SLOTS = [("Purpose:", "用途与位置"), ("Subject:", "主体"), ("Composition:", "构图与镜头"), ("Lighting:", "光线"),
         ("Material:", "材质"), ("Color:", "色彩"), ("Background and output:", "背景与输出"), ("Avoid:", "负面约束")]
PLACEHOLDER = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
HAN = re.compile(r"[一-鿿]")
VAGUE = re.compile(r"\b(beautiful|stunning|gorgeous|amazing|breathtaking|masterpiece|high-end|luxurious|trending on)\b", re.I)
STYLE_OF = re.compile(r"in the style of|artstation|octane|unreal engine|by greg|by artist", re.I)
BRANDS = re.compile(r"\b(apple|nike|adidas|starbucks|ikea|lego|disney|kodak|leica|canon|nikon|sony|samsung|pantone|hasselblad|polaroid|instagram|pinterest|tesla|muji|chanel|dior)\b", re.I)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(folder: Path):
    errors: list[str] = []
    warns: list[str] = []
    data = load(folder / "prompts.json")
    styles_doc = load(folder / "styles.json")
    rows = data.get("prompts", [])
    categories = [c["name"] for c in data.get("categories", [])]
    styles = {s["id"]: s for s in styles_doc.get("styles", [])}
    negatives = {n["id"]: n for n in styles_doc.get("negatives", [])}

    # themes
    themes = styles_doc.get("themes", [])
    if len(themes) < 8:
        errors.append(f"主题色少于 8 个（{len(themes)}）")
    for t in themes:
        for k in ("key", "name", "en", "hex", "secondary_name", "secondary_en", "secondary_hex"):
            if not t.get(k):
                errors.append(f"主题 {t.get('key')} 缺字段 {k}")
        for k in ("hex", "secondary_hex"):
            if not re.fullmatch(r"#[0-9A-Fa-f]{6}", t.get(k, "")):
                errors.append(f"主题 {t.get('key')} 的 {k} 不是 #RRGGBB")

    # style blocks and negative groups
    for i, sid in enumerate(sorted(styles), 1):
        if sid != f"ST-{i:03d}":
            errors.append(f"风格块编号不连续：{sid}，应为 ST-{i:03d}")
            break
    for i, nid in enumerate(sorted(negatives), 1):
        if nid != f"NG-{i:03d}":
            errors.append(f"负面约束编号不连续：{nid}，应为 NG-{i:03d}")
            break
    if len(styles) < 8:
        errors.append(f"风格块少于 8 个（{len(styles)}）")
    if len(negatives) < 4:
        errors.append(f"负面约束少于 4 组（{len(negatives)}）")
    for s in styles.values():
        for k in ("name", "kind", "use", "lighting", "material", "color_rule"):
            if not s.get(k):
                errors.append(f"{s['id']} 缺字段 {k}")
    for n in negatives.values():
        for k in ("name", "use", "text"):
            if not n.get(k):
                errors.append(f"{n['id']} 缺字段 {k}")

    # ids
    ids = [r.get("id", "") for r in rows]
    for i, rid in enumerate(ids, 1):
        if rid != f"PP-{i:03d}":
            errors.append(f"编号不连续或格式不对：第 {i} 条是 {rid or '空'}，应为 PP-{i:03d}")
            break
    if len(set(ids)) != len(ids):
        errors.append("编号有重复：" + ", ".join(k for k, v in Counter(ids).items() if v > 1))

    used_styles: Counter = Counter()
    used_negs: Counter = Counter()
    for r in rows:
        rid = r.get("id", "?")
        bad = False
        for k, typ in FIELDS.items():
            if k not in r:
                errors.append(f"{rid} 缺字段 {k}")
                bad = True
            elif not isinstance(r[k], typ):
                errors.append(f"{rid} 字段 {k} 类型应为 {typ.__name__}")
                bad = True
        if bad:
            continue
        extra = set(r) - set(FIELDS)
        if extra:
            warns.append(f"{rid} 有未登记的字段 {sorted(extra)}")
        name = r["name"]
        if not (4 <= len(name) <= 12) or len(HAN.findall(name)) != len(name):
            errors.append(f"{rid} 名称须为 4–12 个汉字：{name}")
        if r["category"] not in categories:
            errors.append(f"{rid} 分类不在清单里：{r['category']}")
        if r["role"] not in ROLES:
            errors.append(f"{rid} role 不合法：{r['role']}")
        if r["ratio"] not in RATIOS:
            errors.append(f"{rid} ratio 不合法：{r['ratio']}")
        if r["resolution"] not in RESOLUTIONS:
            errors.append(f"{rid} resolution 不合法：{r['resolution']}")
        if r["background"] not in BACKGROUNDS:
            errors.append(f"{rid} background 不合法：{r['background']}")
        if r["format"] not in FORMATS:
            errors.append(f"{rid} format 不合法：{r['format']}")
        if r["background"] == "transparent" and r["format"] == "jpeg":
            errors.append(f"{rid} 透明背景不能用 jpeg")
        if r["background"] == "transparent" and r["role"] not in {"icon-sheet", "illustration"}:
            warns.append(f"{rid} 透明背景一般只给 icon-sheet 或 illustration")
        if not r["use"].strip() or not r["notes"].strip():
            errors.append(f"{rid} use 与 notes 不能为空")
        if len(r["checks"]) < 2 or not all(isinstance(c, str) and c.strip() for c in r["checks"]):
            errors.append(f"{rid} checks 至少 2 条非空要点")

        prompt = r["prompt"]
        negative = r["negative"]
        for m in PLACEHOLDER.finditer(prompt):
            if m.group(1) not in {"primary", "secondary"}:
                errors.append(f"{rid} 占位符只能是 {{{{primary}}}} 或 {{{{secondary}}}}：{m.group(0)}")
        if HAN.search(prompt):
            errors.append(f"{rid} 提示词必须是英文，含有汉字")
        if len(prompt) < 100:
            errors.append(f"{rid} 提示词过短（生成器要求不少于 100 字符）")
        if len(prompt) > 3500:
            warns.append(f"{rid} 提示词超过 3500 字符")
        if "no text" not in negative.lower():
            errors.append(f"{rid} 负面约束里没有 no text")
        if not prompt.rstrip().endswith(negative.rstrip()):
            errors.append(f"{rid} 负面约束没有写在提示词末尾")
        if r["negative_ref"] not in negatives:
            errors.append(f"{rid} negative_ref 不存在：{r['negative_ref']}")
        else:
            used_negs[r["negative_ref"]] += 1
        if not r["style_ref"]:
            errors.append(f"{rid} style_ref 不能为空")
        for sid in r["style_ref"]:
            if sid not in styles:
                errors.append(f"{rid} style_ref 不存在：{sid}")
            else:
                used_styles[sid] += 1

        if r["verified"]:
            if not r["source"]:
                errors.append(f"{rid} 已验证条目必须写 source")
            else:
                src = folder / r["source"]
                if not src.is_file():
                    errors.append(f"{rid} source 文件不存在：{r['source']}")
                elif src.read_text(encoding="utf-8").strip() != prompt.strip():
                    errors.append(f"{rid} 已验证提示词与 {r['source']} 原文不一致")
            if not r["result"]:
                errors.append(f"{rid} 已验证条目必须有成品图 result")
        else:
            if r["source"]:
                warns.append(f"{rid} 未验证条目不需要 source")
            lines = [ln for ln in prompt.split("\n") if ln.strip()]
            positions = []
            for label, zh in SLOTS:
                idx = next((i for i, ln in enumerate(lines) if ln.startswith(label)), -1)
                if idx < 0:
                    errors.append(f"{rid} 缺槽位 {label}（{zh}）")
                positions.append(idx)
            found = [p for p in positions if p >= 0]
            if found != sorted(found):
                errors.append(f"{rid} 八个槽位的顺序不对")
            if lines and not lines[-1].startswith("Avoid:"):
                errors.append(f"{rid} 最后一行必须是 Avoid:")
            elif lines and lines[-1] != "Avoid: " + negative:
                errors.append(f"{rid} Avoid 行与 negative 不一致")
            out_line = next((ln for ln in lines if ln.startswith("Background and output:")), "")
            if f"Output: {r['ratio']}, {r['resolution']}" not in out_line:
                errors.append(f"{rid} 输出行没有写明 Output: {r['ratio']}, {r['resolution']}")
            if r["background"] not in out_line.lower() and not (r["background"] == "transparent" and "transparent" in out_line.lower()):
                errors.append(f"{rid} 输出行没有写明 {r['background']} 背景")
            for sid in r["style_ref"]:
                s = styles.get(sid)
                if not s:
                    continue
                for key, label in (("lighting", "Lighting:"), ("material", "Material:"), ("color_rule", "Color:")):
                    line = next((ln for ln in lines if ln.startswith(label)), "")
                    if s[key] not in line:
                        errors.append(f"{rid} 的 {label} 行没有原文复用 {sid} 的 {key}")
            ng = negatives.get(r["negative_ref"])
            if ng and not negative.startswith(ng["text"]):
                errors.append(f"{rid} 的负面约束没有以 {ng['id']} 原文开头")
            if VAGUE.search(prompt):
                errors.append(f"{rid} 含有“好看、精美”一类空泛词：{VAGUE.search(prompt).group(0)}")
            if STYLE_OF.search(prompt) or BRANDS.search(prompt):
                errors.append(f"{rid} 不写品牌名与艺术家风格：{(STYLE_OF.search(prompt) or BRANDS.search(prompt)).group(0)}")
            if r["role"] == "icon-sheet":
                subject = next((ln for ln in lines if ln.startswith("Subject:")), "")
                nums = [int(x) for x in re.findall(r"\((\d{1,2})\)", subject)]
                if nums != list(range(1, 17)):
                    errors.append(f"{rid} 拼板主体必须按 (1) 到 (16) 列出 16 个物件，现为 {len(nums)} 个")
                if "4x4" not in prompt:
                    errors.append(f"{rid} 拼板提示词缺少 4x4 布局句")
                if r["ratio"] != "1:1" or r["background"] != "transparent":
                    errors.append(f"{rid} 拼板必须是 1:1 透明底")
                if r["resolution"] == "1k":
                    warns.append(f"{rid} 拼板建议 2k 以上")
            if r["role"] == "poster" and "copy" not in prompt.lower():
                warns.append(f"{rid} 海报提示词没有写文案留白区")

        if r["result"]:
            if not (folder / r["result"]).resolve().is_file():
                errors.append(f"{rid} 成品图不存在：{r['result']}")
            if not r["verified"]:
                warns.append(f"{rid} 有成品图但未标记已验证")

    for sid, s in styles.items():
        if used_styles[sid] == 0:
            warns.append(f"{sid} 没有被任何提示词引用")
    for nid in negatives:
        if used_negs[nid] == 0:
            warns.append(f"{nid} 没有被任何提示词引用")
    for c in categories:
        if not any(r.get("category") == c for r in rows):
            errors.append(f"分类 {c} 下没有提示词")
    names = [r.get("name") for r in rows]
    for k, v in Counter(names).items():
        if v > 1:
            errors.append(f"名称重复：{k}")
    texts = [r.get("prompt") for r in rows]
    if len(set(texts)) != len(texts):
        errors.append("有完全相同的提示词")
    return data, styles_doc, errors, warns, used_styles, used_negs


def render(data, styles_doc) -> str:
    payload = {
        "version": data.get("version", 1),
        "categories": data["categories"],
        "themes": styles_doc["themes"],
        "styles": styles_doc["styles"],
        "negatives": styles_doc["negatives"],
        "prompts": data["prompts"],
    }
    return ("/* 由 scripts/build_prompts_js.py 从 prompts.json 与 styles.json 生成，不手改 */\n"
            "window.LZ_PROMPTS = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(DEFAULT_DIR), help="提示词库目录，默认 templates/poster/source/prompts")
    ap.add_argument("--check", action="store_true", help="只检查，不写文件；prompts.js 过期也算失败")
    args = ap.parse_args(argv)
    folder = Path(args.dir).resolve()
    data, styles_doc, errors, warns, used_styles, used_negs = check(folder)
    rows = data.get("prompts", [])
    counts = Counter(r.get("category") for r in rows)
    print(f"提示词 {len(rows)} 条，风格块 {len(styles_doc.get('styles', []))} 个，负面约束 {len(styles_doc.get('negatives', []))} 组，已验证 {sum(1 for r in rows if r.get('verified'))} 条")
    for c in data.get("categories", []):
        ids = [r["id"] for r in rows if r.get("category") == c["name"]]
        if ids:
            print(f"  {c['name']}：{counts[c['name']]} 条（{ids[0]}–{ids[-1]}）")
    print("  风格块引用：" + "，".join(f"{k}×{used_styles[k]}" for k in sorted(used_styles)))
    print("  负面约束引用：" + "，".join(f"{k}×{used_negs[k]}" for k in sorted(used_negs)))
    for w in warns:
        print("警告", w)
    for e in errors:
        print("错误", e)
    if errors:
        print(f"检查未通过：{len(errors)} 个错误")
        return 1
    text = render(data, styles_doc)
    target = folder / "prompts.js"
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != text:
            print("错误 prompts.js 不存在或已过期，运行不带 --check 的命令重新生成")
            return 1
        print("检查通过，prompts.js 是最新的")
        return 0
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"检查通过，已写入 {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
