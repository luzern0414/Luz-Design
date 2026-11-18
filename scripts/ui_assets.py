"""Verify generated UI assets against the actual local Imagegen run, not a label."""
from __future__ import annotations
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path

PROGRAM = Path('D:/Codes/Imagegen/src/imagegen.py')
RUN_SCHEMA = 'luz-imagegen-run/v1'
TRANSFORM = 'proportional downscale max 1400px; WebP quality 92'
OUTPUT_FILES = ('file', 'source', 'sidecar', 'prompt', 'dry_run', 'execution')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def webp_bytes(source: Path, transform=TRANSFORM):
    if transform != TRANSFORM:
        raise ValueError('未知素材变换，不能核验生成原图与交付 WebP 的关系')
    from PIL import Image
    buffer = io.BytesIO()
    with Image.open(source) as image:
        image.load()
        image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
        image.save(buffer, 'WEBP', quality=92)
    return buffer.getvalue()


def output_bindings(files):
    return {key: sha(files[key]) for key in OUTPUT_FILES}


def verify_invocation(run, files, sidecar):
    """Bind the command and saved source, including complete pre-v1 receipts.

    Older real runs already retained argv, the dry-run payload and the saved-file
    log. Require all of them; a success flag alone is never a compatibility path.
    New runs additionally pin every output byte in the completed invocation.
    """
    if Path(run.get('program', '')).resolve() != PROGRAM.resolve() or run.get('program_sha256') != sha(PROGRAM):
        raise ValueError('Imagegen 调用程序或代码哈希不符')
    if (run.get('status') != 'complete' or any(type(run.get(key)) is not int or run[key] != 0
                                              for key in ('exit_code', 'dry_run_exit_code'))):
        raise ValueError('Imagegen 未成功执行')
    started = datetime.fromisoformat(run['started_at'])
    finished = datetime.fromisoformat(run['finished_at'])
    if started.tzinfo is None or finished.tzinfo is None or finished < started:
        raise ValueError('Imagegen 调用时间不完整或顺序错误')
    args = run.get('args')
    if (not isinstance(args, list) or not args or any(not isinstance(value, str) for value in args)
            or Path(args[0]).resolve() != PROGRAM.resolve() or len(args) % 2 != 1):
        raise ValueError('Imagegen 调用参数缺失或不是指定程序')
    options = dict(zip(args[1::2], args[2::2]))
    required = {'--prompt-file', '--ratio', '--resolution', '--quality', '--format', '--background', '--count', '--output-dir'}
    if set(options) != required or len(args) != 1 + 2 * len(required):
        raise ValueError('Imagegen 调用参数重复、缺失或包含未知选项')
    prompt, output = Path(options['--prompt-file']), Path(options['--output-dir'])
    if not prompt.is_absolute() or prompt.resolve() != files['prompt']:
        raise ValueError('Imagegen 调用未使用此素材提示词')
    if not output.is_absolute() or output.resolve() != files['invocation'].parent:
        raise ValueError('Imagegen 调用目录与回执位置不符')
    output = output.resolve()
    if any(files[key].parent != output for key in ('file', 'source', 'sidecar')):
        raise ValueError('素材原图、交付文件和回执不属于本次调用目录')
    images = sidecar.get('images')
    if not isinstance(images, list) or len(images) != 1 or not isinstance(images[0], dict):
        raise ValueError('Imagegen 回执必须包含本次调用的唯一原图')
    source_info = images[0]
    source_name = source_info.get('file')
    if (not isinstance(source_name, str) or Path(source_name).name != source_name
            or (output / source_name).resolve() != files['source'] or source_info.get('processed') is not False):
        raise ValueError('Imagegen 成功回执未绑定此未加工原图')
    for key, name in (('dry_run', 'dry-run.txt'), ('execution', 'execution.txt')):
        target = (output / name).resolve()
        if target.parent != output or not target.is_file():
            raise ValueError('缺少本次 Imagegen 调用的 ' + name)
        files[key] = target
    request = sidecar.get('request', {})
    if read(files['dry_run']) != request:
        raise ValueError('Imagegen 回执请求与本次试运行请求不一致')
    if request.get('prompt', '').strip() != files['prompt'].read_text(encoding='utf-8-sig').strip():
        raise ValueError('提示词与 Imagegen 生成回执不符')
    if (options['--count'] != '1' or type(request.get('n')) is not int or request['n'] != 1
            or options['--quality'] != 'high' or request.get('quality') != options['--quality']
            or options['--format'] != 'png' or request.get('output_format') != options['--format']
            or request.get('background') != options['--background']):
        raise ValueError('Imagegen 调用参数与回执请求不一致')
    saved = [line.removeprefix('已保存：').strip() for line in files['execution'].read_text(encoding='utf-8').splitlines()
             if line.startswith('已保存：')]
    if len(saved) != 1 or not Path(saved[0]).is_absolute() or Path(saved[0]).resolve() != files['source']:
        raise ValueError('Imagegen 执行日志未确认保存此原图')
    if 'evidence_schema' in run:
        if run['evidence_schema'] != RUN_SCHEMA or run.get('transform') != TRANSFORM or run.get('outputs') != output_bindings(files):
            raise ValueError('Imagegen 完成记录与原图、派生图或请求/执行证据哈希不符')
    elif 'outputs' in run or 'transform' in run:
        raise ValueError('Imagegen 完成记录缺少证据版本')
    return source_info


def validate_assets(path: Path, session: Path | None = None):
    errors, resolved = [], []
    try:
        value = read(path)
        if value.get('schema') != 'luz-imagegen-assets/v1' or not value.get('assets'):
            return [], ['缺少实际 Imagegen 素材清单']
        allowed = (session / 'raw').resolve() if session else path.parent.resolve()
        if session and not path.resolve().is_relative_to(allowed):
            raise ValueError('素材清单须位于本会话 raw 中')
        session_start = None
        if session:
            session_manifest = read(allowed / '99-delivery/MANIFEST.json')
            session_start = datetime.fromisoformat(session_manifest['created_at'])
        seen = set()
        for item in value['assets']:
            aid = item.get('id')
            if not isinstance(aid, str) or aid in seen:
                errors.append('素材 id 缺失或重复')
                continue
            seen.add(aid)
            files = {}
            for key in ('file', 'source', 'sidecar', 'prompt', 'invocation'):
                candidate = (path.parent / item[key]).resolve()
                if not candidate.is_relative_to(allowed):
                    raise ValueError(f'{aid}: {key} 不在本会话 raw 中')
                if not candidate.is_file() or sha(candidate) != item.get(key + '_sha256'):
                    raise ValueError(f'{aid}: {key} 缺失或哈希不匹配')
                files[key] = candidate
            sidecar, run = read(files['sidecar']), read(files['invocation'])
            if session_start and datetime.fromisoformat(run['started_at']) < session_start:
                errors.append(f'{aid}: 旧会话生成记录不能代替本次 Imagegen 调用')
            source_info = verify_invocation(run, files, sidecar)
            if item.get('actual') != source_info:
                errors.append(f'{aid}: 素材实际信息与生成回执不符')
            if files['file'].read_bytes() != webp_bytes(files['source'], item.get('transform')):
                errors.append(f'{aid}: 交付 WebP 不能由记录的原图和变换精确重建')
            if item.get('role') not in {'background', 'icon-sheet', 'illustration', 'icon'}:
                errors.append(f'{aid}: 素材角色无效')
            if item.get('review', {}).get('status') != 'passed' or not item.get('review', {}).get('note'):
                errors.append(f'{aid}: 尚未完成目视复核')
            from PIL import Image
            for key in ('file', 'source'):
                with Image.open(files[key]) as im:
                    if key == 'source' and source_info and source_info.get('source_size') != f'{im.width}x{im.height}':
                        errors.append(f'{aid}: 原图实际尺寸与回执不符')
                    if key == 'source' and source_info.get('source_format', '').lower() != im.format.lower():
                        errors.append(f'{aid}: 原图实际格式与回执不符')
                    im.verify()
            resolved.append({**item, '_files': files})
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        errors.append(f'Imagegen 素材证据无效：{exc}')
    return resolved, errors
