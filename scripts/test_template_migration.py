"""Offline byte-preserving migration fixtures; never business acceptance evidence."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import template_library as library


def selected_project(tmp_path):
    old, new = tmp_path / 'legacy', tmp_path / 'session' / 'raw'
    old.mkdir()
    (old / 'project.json').write_text(json.dumps({'deliver_root': str(old)}), encoding='utf-8')
    target = old / 'raw' / '00-crawl' / 'luz-project-requirements.html'
    library.select(old, 'luz-project', 'requirements', 'reading-html', str(target))
    target.parent.mkdir(parents=True)
    target.write_text(library.render_reading('Offline fixture', '<section><h2>Evidence</h2><p>Fixture only.</p></section>'), encoding='utf-8')
    library.record_output(old, 'luz-project', 'requirements', target, 'reading-html', generator='offline fixture renderer')
    moves = [(old / 'project.json', new / 'project.json'),
             (old / '00-design', new / '00-design'),
             (old / 'raw' / '00-crawl', new / '00-crawl')]
    return old, new, target, moves


def move_files(moves):
    for source, target in moves:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))


def migrated_project(tmp_path):
    old, new, target, moves = selected_project(tmp_path)
    prepared = library.prepare_output_migration(old, new, moves)
    record = library._record_path(old, 'luz-project', 'requirements')
    original_record = record.read_bytes()
    move_files(moves)
    receipt = library.record_output_migration(prepared)
    moved_target = new / '00-crawl' / target.name
    return old, new, moved_target, receipt, original_record


def test_migration_preserves_record_and_verifies_exact_moved_bytes(tmp_path):
    old, new, target, receipt, original_record = migrated_project(tmp_path)
    assert receipt.is_relative_to(new / '00-design' / 'migrations')
    assert library._record_path(new, 'luz-project', 'requirements').read_bytes() == original_record
    item = library.require_selected(new, 'luz-project', 'requirements', target, 'reading-html', phase='post')
    assert Path(item['output']['path']).is_relative_to(old)
    assert Path(item['output']['path']) != target


def test_migration_never_authorizes_a_new_generation_or_record_rewrite(tmp_path):
    _, new, target, _, original_record = migrated_project(tmp_path)
    with pytest.raises(ValueError, match='准确输出位置|迁移'):
        library.require_selected(new, 'luz-project', 'requirements', target, 'reading-html')
    with pytest.raises(ValueError, match='准确输出位置|迁移'):
        library.record_output(new, 'luz-project', 'requirements', target, 'reading-html', generator='re-render')
    assert library._record_path(new, 'luz-project', 'requirements').read_bytes() == original_record


def test_new_selection_can_authorize_later_generation_without_borrowing_the_receipt(tmp_path):
    _, new, target, _, _ = migrated_project(tmp_path)
    library.select(new, 'luz-project', 'requirements', 'reading-html', str(target))
    library.require_selected(new, 'luz-project', 'requirements', target, 'reading-html')
    target.write_text(library.render_reading('New offline fixture', '<p>New fixture.</p>'), encoding='utf-8')
    library.record_output(new, 'luz-project', 'requirements', target, 'reading-html', generator='new offline fixture renderer')
    library.require_selected(new, 'luz-project', 'requirements', target, 'reading-html', phase='post')


def test_same_relative_selection_stays_read_only_after_root_migration(tmp_path):
    old, new, target, moves = selected_project(tmp_path)
    record_path = library._record_path(old, 'luz-project', 'requirements')
    value = library.read(record_path)
    value['template_uses'][0]['applies_to'] = 'raw/00-crawl/' + target.name
    record_path.write_text(json.dumps(value), encoding='utf-8')
    # Preserve the raw/ prefix in this explicit move so relative keys still match.
    moves[2] = (moves[2][0], new / 'raw' / '00-crawl')
    prepared = library.prepare_output_migration(old, new, moves)
    move_files(moves)
    library.record_output_migration(prepared)
    moved_target = new / 'raw' / '00-crawl' / target.name
    library.require_selected(new, 'luz-project', 'requirements', moved_target, 'reading-html', phase='post')
    with pytest.raises(ValueError, match='迁移'):
        library.require_selected(new, 'luz-project', 'requirements', moved_target, 'reading-html')


@pytest.mark.parametrize('changed', [False, True])
def test_check_cli_validates_the_moved_bytes_against_the_original_record(tmp_path, changed):
    _, new, target, _, _ = migrated_project(tmp_path)
    if changed:
        target.write_bytes(b'changed')
    result = subprocess.run([sys.executable, '-X', 'utf8', str(Path(library.__file__)), 'check',
                             str(library._record_path(new, 'luz-project', 'requirements'))],
                            text=True, encoding='utf-8', capture_output=True)
    assert result.returncode == int(changed), result.stdout + result.stderr
    assert json.loads(result.stdout)['ok'] is not changed


@pytest.mark.parametrize('condition', ['output', 'record', 'snapshot', 'receipt', 'other-stage', 'other-target'])
def test_migration_cannot_hide_changed_evidence_or_expand_binding(tmp_path, condition):
    _, new, target, receipt, _ = migrated_project(tmp_path)
    if condition == 'output':
        target.write_bytes(b'changed')
    elif condition == 'record':
        record = library._record_path(new, 'luz-project', 'requirements')
        record.write_bytes(record.read_bytes() + b' ')
    elif condition == 'snapshot':
        record = library.read(library._record_path(new, 'luz-project', 'requirements'))
        snapshot = new / '00-design' / record['template_uses'][0]['snapshots'][0]['path']
        snapshot.write_bytes(snapshot.read_bytes() + b' ')
    elif condition == 'receipt':
        value = library.read(receipt)
        value['bindings'][0]['output_sha256'] = '0' * 64
        receipt.write_text(json.dumps(value), encoding='utf-8')
    elif condition == 'other-stage':
        with pytest.raises(ValueError):
            library.require_selected(new, 'luz-project', 'proposal', target, 'reading-html', phase='post')
        return
    else:
        changed_target = target.with_name('same-name-copy.html')
        shutil.copyfile(target, changed_target)
        target = changed_target
    with pytest.raises(ValueError):
        library.require_selected(new, 'luz-project', 'requirements', target, 'reading-html', phase='post')


def test_prepare_is_read_only_and_rejects_an_unrecorded_or_tampered_original(tmp_path):
    old, new, target, moves = selected_project(tmp_path)
    before = {p.relative_to(old).as_posix(): p.read_bytes() for p in old.rglob('*') if p.is_file()}
    library.prepare_output_migration(old, new, moves)
    assert not new.exists()
    assert before == {p.relative_to(old).as_posix(): p.read_bytes() for p in old.rglob('*') if p.is_file()}
    target.write_bytes(b'changed')
    with pytest.raises(ValueError):
        library.prepare_output_migration(old, new, moves)


def test_changed_between_prepare_and_move_is_rejected_without_writing_receipt(tmp_path):
    old, new, target, moves = selected_project(tmp_path)
    prepared = library.prepare_output_migration(old, new, moves)
    target.write_bytes(b'changed during move')
    move_files(moves)
    with pytest.raises(ValueError):
        library.record_output_migration(prepared)
    assert not (new / '00-design' / 'migrations').exists()


def test_missing_record_move_and_paths_outside_the_two_roots_are_rejected(tmp_path):
    old, new, target, moves = selected_project(tmp_path)
    for invalid in (moves[:1] + moves[2:], moves + [(target, tmp_path / 'outside.html')]):
        with pytest.raises(ValueError):
            library.prepare_output_migration(old, new, invalid)


def test_no_template_outputs_returns_no_receipt(tmp_path):
    old, new = tmp_path / 'legacy', tmp_path / 'session' / 'raw'
    old.mkdir()
    (old / 'project.json').write_text('{}', encoding='utf-8')
    prepared = library.prepare_output_migration(old, new, [])
    assert prepared['bindings'] == []
    assert library.record_output_migration(prepared) is None
    assert not new.exists()
