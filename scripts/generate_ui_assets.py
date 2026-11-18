"""Generate UI background/icon assets with the required local Imagegen program.

One billable request per invocation; dry-run first, never retry a timed-out run.
The review subcommand records the inspection after opening the actual image.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from ui_assets import PROGRAM, RUN_SCHEMA, TRANSFORM, output_bindings, read, sha, verify_invocation, webp_bytes


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    gen = sub.add_parser('generate')
    gen.add_argument('--session', required=True)
    gen.add_argument('--prompt-file', required=True)
    gen.add_argument('--id', required=True)
    gen.add_argument('--role', choices=['background', 'icon-sheet', 'illustration'], required=True)
    gen.add_argument('--ratio', default='1:1')
    gen.add_argument('--resolution', default='1k', choices=['1k', '2k', '4k'])
    gen.add_argument('--background', default='opaque', choices=['opaque', 'transparent'])
    gen.add_argument('--dry-run', action='store_true')
    review = sub.add_parser('review')
    review.add_argument('--session', required=True)
    review.add_argument('--id', required=True)
    review.add_argument('--note', required=True)
    args = ap.parse_args(argv)
    try:
        from crawl_gate import require_session_preflight
        ctx = require_session_preflight(args.session)
        session = ctx['session']
        raw = ctx['raw']
        manifest = raw / '02-visual/ui-assets.json'
        if args.command == 'review':
            if len(args.note.strip()) < 12:
                raise ValueError('复核说明须记实际内容、边缘/裁剪、浅深底效果与用途')
            value = read(manifest)
            item = next((x for x in value['assets'] if x['id'] == args.id), None)
            if item is None:
                raise ValueError('素材 id 不存在')
            item['review'] = {'status': 'passed', 'note': args.note.strip(), 'reviewed_at': datetime.now(timezone.utc).isoformat()}
            write(manifest, value)
            print(f'复核已记录：{args.id}')
            return 0
        if not re.fullmatch(r'[a-z][a-z0-9-]{1,40}', args.id):
            raise ValueError('id 使用 2–41 位英文小写/数字/短横线')
        prompt = Path(args.prompt_file).resolve()
        if not prompt.is_relative_to(raw.resolve()) or not prompt.is_file():
            raise ValueError('提示词必须是本会话 raw 内已保存的 UTF-8 文件')
        if len(prompt.read_text(encoding='utf-8-sig').strip()) < 100:
            raise ValueError('提示词需写明用途、主体、构图、光线、材质、配色、背景与负面约束')
        if not PROGRAM.is_file():
            raise ValueError(f'本地 Imagegen 不存在：{PROGRAM}')
        output = raw / '02-visual/generated' / args.id
        if output.exists():
            raise ValueError('该 id 已执行或结果未知；先检查已有回执，禁止自动重试同一请求')
        command = [sys.executable, '-X', 'utf8', str(PROGRAM), '--prompt-file', str(prompt), '--ratio', args.ratio,
                   '--resolution', args.resolution, '--quality', 'high', '--format', 'png', '--background', args.background,
                   '--count', '1', '--output-dir', str(output)]
        dry = subprocess.run(command + ['--dry-run'], capture_output=True, text=True, encoding='utf-8', timeout=60)
        if dry.returncode:
            raise ValueError('Imagegen dry-run 失败：' + dry.stderr[-800:])
        if args.dry_run:
            print(dry.stdout)
            return 0
        output.mkdir(parents=True)
        invocation = output / 'invocation.json'
        record = {'status': 'running', 'evidence_schema': RUN_SCHEMA, 'program': PROGRAM.as_posix(), 'program_sha256': sha(PROGRAM),
                  'args': command[3:], 'started_at': datetime.now(timezone.utc).isoformat(), 'dry_run_exit_code': dry.returncode}
        write(invocation, record)
        (output / 'dry-run.txt').write_text(dry.stdout, encoding='utf-8')
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=660)
        except subprocess.TimeoutExpired:
            record['status'] = 'unknown'
            write(invocation, record)
            raise ValueError('Imagegen 超时，状态未知；未自动重试，先核查已有服务结果')
        (output / 'execution.txt').write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
        record.update(exit_code=result.returncode, status='generated' if result.returncode == 0 else 'failed', finished_at=datetime.now(timezone.utc).isoformat())
        write(invocation, record)
        if result.returncode:
            raise ValueError(f'Imagegen 失败，执行记录：{output / "execution.txt"}')
        receipts = [p for p in output.glob('*.json') if p.name != 'invocation.json']
        if len(receipts) != 1:
            raise ValueError('未找到唯一的 Imagegen 回执')
        receipt = read(receipts[0])
        if len(receipt.get('images', [])) != 1:
            raise ValueError('服务未返回恰好一张图片；检查回执，不自动重试')
        source = (output / receipt['images'][0]['file']).resolve()
        if source.parent != output.resolve():
            raise ValueError('Imagegen 回执原图不在本次调用目录')
        dest = output / (args.id + '.webp')
        dest.write_bytes(webp_bytes(source))
        files = {'file': dest, 'source': source, 'sidecar': receipts[0], 'prompt': prompt, 'invocation': invocation,
                 'dry_run': output / 'dry-run.txt', 'execution': output / 'execution.txt'}
        record.update(status='complete', transform=TRANSFORM, outputs=output_bindings(files))
        verify_invocation(record, files, receipt)
        write(invocation, record)
        value = read(manifest) if manifest.exists() else {'schema': 'luz-imagegen-assets/v1', 'assets': []}
        if any(x.get('id') == args.id for x in value['assets']):
            raise ValueError('清单里已有相同素材 id')
        item = {'id': args.id, 'role': args.role, 'review': {'status': 'pending'}, 'transform': TRANSFORM, 'actual': receipt['images'][0], 'warnings': receipt.get('warnings', [])}
        for key, path in {'file': dest, 'source': source, 'sidecar': receipts[0], 'prompt': prompt, 'invocation': invocation}.items():
            import os
            item[key] = Path(os.path.relpath(path, manifest.parent)).as_posix()
            item[key + '_sha256'] = sha(path)
        value['assets'].append(item)
        write(manifest, value)
        print(json.dumps({'manifest': str(manifest), 'source': str(source), 'web_asset': str(dest), 'warnings': receipt.get('warnings', []), 'next': '打开实际图片复核，再 review'}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('错误：' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
