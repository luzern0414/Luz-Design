"""Offline fixtures test evidence rejection; they never claim a real Imagegen request."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from ui_assets import sha, validate_assets


class ImageEvidenceContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.session = Path(self.temp.name)
        self.folder = self.session / 'raw/02-visual'
        self.folder.mkdir(parents=True)
        (self.session / 'raw/99-delivery').mkdir()
        self.write(self.session / 'raw/99-delivery/MANIFEST.json', {'created_at': '2026-11-06T00:00:00+00:00'})
        self.prompt = 'Offline fixture only: test an archived image and receipt without any network call.'
        (self.folder / 'prompt.txt').write_text(self.prompt, encoding='utf-8')
        Image.new('RGB', (16, 16), '#eeeeee').save(self.folder / 'source.png')
        Image.new('RGB', (16, 16), '#eeeeee').save(self.folder / 'asset.webp', quality=92)
        program = Path('D:/Codes/Imagegen/src/imagegen.py')
        self.run = {'program': program.as_posix(), 'program_sha256': sha(program),
                    'started_at': '2026-11-06T01:00:00+00:00', 'finished_at': '2026-11-06T01:00:01+00:00',
                    'status': 'complete', 'exit_code': 0, 'dry_run_exit_code': 0,
                    'args': [str(program), '--prompt-file', str(self.folder / 'prompt.txt'),
                             '--ratio', '1:1', '--resolution', '1k', '--quality', 'high', '--format', 'png',
                             '--background', 'opaque', '--count', '1', '--output-dir', str(self.folder)]}
        request = {'model': 'offline-fixture', 'prompt': self.prompt, 'size': '1024x1024',
                   'quality': 'high', 'n': 1, 'output_format': 'png', 'background': 'opaque'}
        self.sidecar = {'request': request,
                        'images': [{'file': 'source.png', 'processed': False, 'source_size': '16x16',
                                    'source_format': 'png', 'size': '16x16', 'format': 'png'}]}
        self.write(self.folder / 'run.json', self.run)
        self.write(self.folder / 'receipt.json', self.sidecar)
        self.write(self.folder / 'dry-run.txt', request)
        (self.folder / 'execution.txt').write_text('已保存：' + str((self.folder / 'source.png').resolve()) + '\n', encoding='utf-8')
        self.item = {'id': 'test-fixture', 'role': 'background',
                     'transform': 'proportional downscale max 1400px; WebP quality 92',
                     'actual': copy.deepcopy(self.sidecar['images'][0]),
                     'review': {'status': 'passed', 'note': 'Fixture review; not an actual generated business asset.'}}
        for key, name in {'file': 'asset.webp', 'source': 'source.png', 'prompt': 'prompt.txt',
                          'sidecar': 'receipt.json', 'invocation': 'run.json'}.items():
            self.item[key] = name
            self.item[key + '_sha256'] = sha(self.folder / name)
        self.manifest = self.folder / 'ui-assets.json'
        self.save_manifest()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')

    def save_manifest(self):
        self.write(self.manifest, {'schema': 'luz-imagegen-assets/v1', 'assets': [self.item]})

    def check_errors(self):
        return validate_assets(self.manifest, self.session)[1]

    def save_run(self, value):
        self.write(self.folder / 'run.json', value)
        self.item['invocation_sha256'] = sha(self.folder / 'run.json')
        self.save_manifest()

    def completed_outputs(self):
        names = {'file': 'asset.webp', 'source': 'source.png', 'sidecar': 'receipt.json',
                 'prompt': 'prompt.txt', 'dry_run': 'dry-run.txt', 'execution': 'execution.txt'}
        return {key: sha(self.folder / name) for key, name in names.items()}

    def test_unmodified_offline_fixture_passes_contract(self):
        self.assertEqual(self.check_errors(), [])

    def test_changed_image_bytes_rejected(self):
        (self.folder / 'asset.webp').write_bytes(b'changed after review')
        self.assertTrue(self.check_errors())

    def test_rehashed_unrelated_webp_cannot_reuse_generated_source(self):
        Image.new('RGB', (16, 16), '#ff00ff').save(self.folder / 'asset.webp', quality=92)
        self.item['file_sha256'] = sha(self.folder / 'asset.webp')
        self.save_manifest()
        self.assertTrue(self.check_errors())

    def test_unknown_transform_cannot_authorize_arbitrary_webp(self):
        self.item['transform'] = 'arbitrary repaint after generation'
        self.save_manifest()
        self.assertTrue(self.check_errors())

    def test_invocation_prompt_output_and_program_arguments_are_bound(self):
        variants = []
        for name, replacement in (('--prompt-file', str(self.folder / 'unrelated-prompt.txt')),
                                  ('--output-dir', str(self.folder / 'other-run'))):
            run = copy.deepcopy(self.run)
            run['args'][run['args'].index(name) + 1] = replacement
            variants.append(run)
        run = copy.deepcopy(self.run)
        run['args'][0] = 'D:/unrelated/imagegen.py'
        variants.append(run)
        for run in variants:
            with self.subTest(args=run['args']):
                self.save_run(run)
                self.assertTrue(self.check_errors())

    def test_changed_program_digest_cannot_reuse_success_status(self):
        self.save_run({**self.run, 'program_sha256': '0' * 64})
        self.assertTrue(self.check_errors())

    def test_duplicate_or_missing_invocation_arguments_are_rejected(self):
        for args in (self.run['args'] + ['--prompt-file', str(self.folder / 'prompt.txt')],
                     [self.run['args'][0]], self.run['args'] + ['--dry-run']):
            with self.subTest(args=args):
                self.save_run({**self.run, 'args': args})
                self.assertTrue(self.check_errors())

    def test_success_log_must_name_the_same_source(self):
        (self.folder / 'execution.txt').write_text('已保存：' + str(self.folder / 'unrelated.png'), encoding='utf-8')
        self.assertTrue(self.check_errors())

    def test_success_log_and_dry_run_are_required(self):
        for name in ('execution.txt', 'dry-run.txt'):
            path = self.folder / name
            previous = path.read_bytes()
            path.unlink()
            try:
                self.assertTrue(self.check_errors(), name)
            finally:
                path.write_bytes(previous)

    def test_same_named_source_cannot_be_taken_from_another_run_folder(self):
        other = self.folder / 'other-run'
        other.mkdir()
        (other / 'source.png').write_bytes((self.folder / 'source.png').read_bytes())
        self.item['source'] = 'other-run/source.png'
        self.save_manifest()
        self.assertTrue(self.check_errors())

    def test_receipt_request_and_output_count_are_bound(self):
        variants = [
            {**self.sidecar, 'request': {**self.sidecar['request'], 'quality': 'low'}},
            {**self.sidecar, 'images': self.sidecar['images'] * 2},
        ]
        for value in variants:
            with self.subTest(value=value):
                self.write(self.folder / 'receipt.json', value)
                self.item['sidecar_sha256'] = sha(self.folder / 'receipt.json')
                self.save_manifest()
                self.assertTrue(self.check_errors())

    def test_new_completion_binds_source_and_derivative_hashes(self):
        run = {**self.run, 'evidence_schema': 'luz-imagegen-run/v1',
               'transform': self.item['transform'], 'outputs': self.completed_outputs()}
        self.save_run(run)
        self.assertEqual(self.check_errors(), [])
        Image.new('RGB', (16, 16), '#ff00ff').save(self.folder / 'source.png')
        Image.new('RGB', (16, 16), '#ff00ff').save(self.folder / 'asset.webp', quality=92)
        self.item['source_sha256'] = sha(self.folder / 'source.png')
        self.item['file_sha256'] = sha(self.folder / 'asset.webp')
        self.save_manifest()
        self.assertTrue(self.check_errors())

    def test_new_completion_cannot_omit_its_outputs(self):
        self.save_run({**self.run, 'evidence_schema': 'luz-imagegen-run/v1'})
        self.assertTrue(self.check_errors())

    def test_same_hash_outside_current_raw_rejected(self):
        target = self.session / 'outside.webp'
        target.write_bytes((self.folder / 'asset.webp').read_bytes())
        self.item['file'] = '../../outside.webp'
        self.save_manifest()
        self.assertTrue(self.check_errors())

    def test_failed_or_previous_session_execution_rejected_even_with_updated_hash(self):
        for patch in ({'status': 'failed', 'exit_code': 1},
                      {'started_at': '2026-11-05T01:00:00+00:00'},
                      {'program': 'D:/some-other-generator.py'}):
            with self.subTest(patch=patch):
                self.write(self.folder / 'run.json', {**self.run, **patch})
                self.item['invocation_sha256'] = sha(self.folder / 'run.json')
                self.save_manifest()
                self.assertTrue(self.check_errors())

    def test_receipt_prompt_source_and_dimensions_are_bound(self):
        variants = [
            {**self.sidecar, 'request': {'prompt': 'Unrelated request'}},
            {**self.sidecar, 'images': [{'file': 'different.png', 'processed': False, 'source_size': '16x16'}]},
            {**self.sidecar, 'images': [{'file': 'source.png', 'processed': True, 'source_size': '16x16'}]},
            {**self.sidecar, 'images': [{'file': 'source.png', 'processed': False, 'source_size': '64x64'}]},
        ]
        for value in variants:
            with self.subTest(value=value):
                self.write(self.folder / 'receipt.json', value)
                self.item['sidecar_sha256'] = sha(self.folder / 'receipt.json')
                self.save_manifest()
                self.assertTrue(self.check_errors())

    def test_unreviewed_asset_rejected(self):
        self.item['review'] = {'status': 'pending'}
        self.save_manifest()
        self.assertTrue(self.check_errors())

    def test_generate_records_verifiable_completion_without_network(self):
        import generate_ui_assets as generator
        prompt = self.folder / 'generation-prompt.txt'
        prompt.write_text('Offline fixture only. ' * 12, encoding='utf-8')
        payload = {**self.sidecar['request'], 'prompt': prompt.read_text(encoding='utf-8')}

        def local_process(command, **kwargs):
            if '--dry-run' in command:
                return subprocess.CompletedProcess(command, 0, json.dumps(payload), '')
            output = Path(command[command.index('--output-dir') + 1])
            source = output / 'fixture-source.png'
            Image.new('RGB', (16, 16), '#eeeeee').save(source)
            self.write(output / 'fixture-receipt.json', {'request': payload, 'warnings': [],
                'images': [{**self.sidecar['images'][0], 'file': source.name}]})
            return subprocess.CompletedProcess(command, 0, '已保存：' + str(source.resolve()), '')

        context = {'session': self.session, 'raw': self.session / 'raw'}
        with patch('crawl_gate.require_session_preflight', return_value=context), patch.object(generator.subprocess, 'run', side_effect=local_process) as invoked:
            result = generator.main(['generate', '--session', str(self.session), '--prompt-file', str(prompt),
                                     '--id', 'new-fixture', '--role', 'background'])
            self.assertEqual(result, 0)
            self.assertEqual(invoked.call_count, 2)
            value = json.loads(self.manifest.read_text(encoding='utf-8'))
            item = next(asset for asset in value['assets'] if asset['id'] == 'new-fixture')
            run = json.loads((self.manifest.parent / item['invocation']).read_text(encoding='utf-8'))
            self.assertEqual(run.get('evidence_schema'), 'luz-imagegen-run/v1')
            self.assertEqual(run['status'], 'complete')
            for key in ('source', 'file', 'sidecar', 'prompt'):
                self.assertEqual(run['outputs'][key], item[key + '_sha256'])
            self.assertEqual(generator.main(['review', '--session', str(self.session), '--id', 'new-fixture',
                                             '--note', 'Offline fixture review only; no real generation request.']), 0)
        self.assertEqual(self.check_errors(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
