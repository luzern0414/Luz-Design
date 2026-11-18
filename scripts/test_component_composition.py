"""Behavior boundaries for reviewed controls and generated visual asset records.

Image files and provider metadata below are synthetic unit-test fixtures. They
are never presented as actual Imagegen outputs or reviewed product interfaces.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

import component_reuse as reuse
from component_composition import validate_template

class CompositionTests(unittest.TestCase):
    def test_existing_controls_and_native_slots_are_composable(self):
        tags=validate_template('<main><van-radio-group v-model="choice"><van-radio name="a"><span>上午</span></van-radio></van-radio-group><van-button @click="submit">确认</van-button></main>')
        self.assertEqual(tags,{'van-radio-group','van-radio','van-button'})

    def test_custom_control_needs_a_different_contract(self):
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            validate_template('<custom-time-picker></custom-time-picker>')

    def test_markup_injection_is_not_configuration(self):
        for body in ['<div v-html="markup"></div>','<component :is="kind"></component>','<script>doSomething()</script>']:
            with self.subTest(body=body),self.assertRaises(ValueError):validate_template(body)

    def test_grouping_cannot_hide_a_handwritten_control(self):
        for body in ['<div role="button" @click="go">Go</div>','<button>Go</button>','<div tabindex="0" @keydown="choose">A</div>']:
            with self.subTest(body=body),self.assertRaises(ValueError):validate_template(body)

    def test_native_semantics_and_labels_survive(self):
        self.assertEqual(validate_template('<section aria-label="预约摘要"><h2>预约时间</h2><p role="status">已确认</p><van-button aria-label="修改预约">修改</van-button></section>'),{'van-button'})


class CompositionBuildTests(unittest.TestCase):
    """Exercise the real compose path with small, explicitly synthetic sources."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='luz-composition-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.write('license.txt', 'Synthetic test fixture; no upstream library is bundled.')
        self.write('vue.js', '// Synthetic Vue source fixture.\n')
        self.write('vant.js', '// Synthetic Vant source fixture.\n')
        self.write('vant.css', '.van-button { display: inline-block; }\n')
        self.write('icon.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write('layout.json', {'main_action': 'submit', 'fixture': True})
        self.write('style.css', 'main { color: #123; }')
        self.write('binding.js', 'window.fixture = { submit() { return true; } };')
        self.write('binding-review.json', {
            'schema': 'luz-ui-binding-review/1',
            'scope': 'existing-component-binding',
            'reviewer': 'synthetic unit-test fixture',
            'findings': [],
            'file_sha256': reuse.digest(self.base / 'binding.js'),
            'action_ids': ['submit'],
        })
        self.config = {
            'title': 'Composition test fixture',
            'runtime': {'vue': 'vendor/vue.js', 'vant': 'vendor/vant.js', 'css': 'vendor/vant.css'},
            'versions': {'vue': '3.fixture', 'vant': '4.fixture'},
            'binding': 'binding.js',
            'icon': 'vendor/icon.svg',
        }
        self.plan = {
            'schema': reuse.SCHEMA,
            'mode': 'component-reuse',
            'framework': {
                'name': 'Synthetic fixture', 'version': '1', 'assembly': 'vue-vant',
                'shell_resource': 'actions', 'layout': 'One action and image',
                'token_policy': 'Fixture tokens', 'decision': 'Exercise actual validator',
                'breakpoints': [390, 1280],
            },
            'quality': {'UX': 'Observable action', 'DX': 'Bound inputs', 'AX': 'Named action'},
            'local_searches': [{
                'id': 'fixture', 'query': 'Synthetic fixtures',
                'result': 'Selected test sources', 'roots': [str(self.base)],
                'candidates': [{'ref': str(self.base), 'reason': 'Synthetic test source', 'decision': 'selected'}],
            }],
            'resources': [
                self.resource('vue-runtime', 'vue', '3.fixture', ['vue.js']),
                self.resource('actions', 'vant', '4.fixture', ['vant.js', 'vant.css', 'icon.svg']),
            ],
            'pages': [{
                'id': 'main', 'entry': 'index.html', 'composition': self.config,
                'mounts': [{'component_id': 'actions', 'tags': ['van-button']}],
            }],
            'assets': [
                {'resource': 'vue-runtime', 'file': 'vue.js', 'output': 'vendor/vue.js'},
                {'resource': 'actions', 'file': 'vant.js', 'output': 'vendor/vant.js'},
                {'resource': 'actions', 'file': 'vant.css', 'output': 'vendor/vant.css'},
                {'resource': 'actions', 'file': 'icon.svg', 'output': 'vendor/icon.svg'},
            ],
            'bindings': [{
                **self.ref('binding.js'), 'output': 'binding.js', 'purpose': 'Connect fixture action',
                'action_ids': ['submit'], 'review_ref': self.ref('binding-review.json'),
            }],
        }
        self.plan['resources'][1]['component_tags'] = ['van-button']
        self.set_body(self.body())

    def write(self, name, value):
        path = self.base / name
        path.write_text(json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value,
                        encoding='utf-8')
        return path

    def ref(self, name):
        return {'path': name, 'sha256': reuse.digest(self.base / name)}

    def resource(self, resource_id, package, version, names):
        return {
            'id': resource_id, 'origin': 'local', 'version': version, 'package': package,
            'selection_reason': 'Synthetic test input', 'local_search_ids': ['fixture'],
            'files': [self.ref(name) for name in names], 'license': self.ref('license.txt'),
        }

    @staticmethod
    def body(extra=''):
        return ('<main><section data-component-id="actions">'
                '<van-button @click="submit">Confirm</van-button></section>' + extra + '</main>')

    def set_body(self, body):
        self.write('template.html', body)
        for key, name in [('template', 'template.html'), ('style', 'style.css'), ('layout', 'layout.json')]:
            self.config[key] = self.ref(name)
        self.write('composition-review.json', {
            'schema': 'luz-ui-composition-review/1', 'scope': 'existing-control-composition',
            'reviewer': 'synthetic unit-test fixture', 'findings': [],
            'files': {key: self.config[key]['sha256'] for key in ('template', 'style', 'layout')},
        })
        self.config['review'] = self.ref('composition-review.json')

    def compose(self):
        return reuse.compose(self.plan, self.base, component_ids={'actions'},
                             page_ids={'main'}, action_ids={'submit'})

    def add_visual(self, markup='<img src="assets/hero.png" alt="Synthetic fixture graphic">'):
        Image.new('RGB', (8, 4), (120, 160, 180)).save(self.base / 'hero.png')
        self.write('prompt.txt', 'Synthetic unit-test image; not an actual provider request.')
        self.metadata = {
            'created_at': '2026-11-07 12:00:00',
            'request': {'model': 'synthetic-fixture-model',
                        'prompt': (self.base / 'prompt.txt').read_text(encoding='utf-8')},
            'images': [{'file': 'hero.png', 'processed': False, 'size': '8x4', 'format': 'png'}],
        }
        self.visual = {
            'output': 'assets/hero.png', 'origin': 'imagegen', 'use': 'Synthetic fixture illustration',
            'image': self.ref('hero.png'), 'prompt': self.ref('prompt.txt'),
        }
        self.set_metadata(self.metadata)
        self.plan['visual_assets'] = [self.visual]
        self.set_body(self.body(markup))

    def set_metadata(self, value):
        self.write('generation.json', value)
        self.visual['generation'] = self.ref('generation.json')

    def test_existing_brand_maintenance_does_not_require_new_visual_assets(self):
        output = self.compose()
        self.assertIn(b'<van-button @click="submit">Confirm</van-button>', output['index.html'])
        self.assertNotIn('assets/hero.png', output)

    def test_changed_template_requires_a_current_review(self):
        self.write('template.html', self.body('<p>Changed after review</p>'))
        self.config['template'] = self.ref('template.html')
        with self.assertRaisesRegex(ValueError, 'current review'):
            self.compose()

    def test_region_mapping_must_match_actual_controls(self):
        self.plan['pages'][0]['mounts'][0]['tags'] = ['van-radio']
        with self.assertRaisesRegex(ValueError, 'actual control region'):
            self.compose()

    def test_declared_component_cannot_claim_a_control_missing_from_its_source(self):
        self.plan['resources'][1]['component_tags'] = ['van-cell']
        with self.assertRaisesRegex(ValueError, 'not declared'):
            self.compose()

    def test_runtime_version_must_match_the_verified_source(self):
        self.config['versions']['vue'] = '3.other'
        with self.assertRaisesRegex(ValueError, 'version does not match'):
            self.compose()

    def test_remote_static_asset_is_rejected(self):
        self.set_body(self.body('<img src="https://example.invalid/image.png">'))
        with self.assertRaisesRegex(ValueError, 'verified local paths'):
            self.compose()

    def test_valid_visual_is_copied_without_becoming_component_source(self):
        self.add_visual()
        output = self.compose()
        self.assertEqual(output['assets/hero.png'], (self.base / 'hero.png').read_bytes())
        self.assertEqual({name for name in output if name.startswith('licenses/')},
                         {'licenses/vue-runtime.txt', 'licenses/actions.txt'})
        self.assertIn(b'src="assets/hero.png"', output['index.html'])

    def test_imagegen_is_not_a_component_source_origin(self):
        self.plan['resources'][1]['origin'] = 'imagegen'
        with self.assertRaisesRegex(ValueError, 'Unknown component origin'):
            self.compose()

    def test_empty_generation_record_is_rejected(self):
        self.add_visual()
        self.set_metadata({})
        with self.assertRaisesRegex(ValueError, 'Generation record'):
            self.compose()

    def test_generation_prompt_must_match_the_retained_prompt(self):
        self.add_visual()
        self.metadata['request']['prompt'] = 'A different request'
        self.set_metadata(self.metadata)
        with self.assertRaisesRegex(ValueError, 'Generation record'):
            self.compose()

    def test_native_image_record_must_match_file_dimensions_and_format(self):
        self.add_visual()
        for key, value in [('file', 'other.png'), ('size', '40x40'), ('format', 'jpeg'), ('processed', True)]:
            with self.subTest(key=key):
                metadata = copy.deepcopy(self.metadata)
                metadata['images'][0][key] = value
                self.set_metadata(metadata)
                with self.assertRaisesRegex(ValueError, 'native image record'):
                    self.compose()

    def test_replaced_native_image_fails_its_recorded_hash(self):
        self.add_visual()
        Image.new('RGB', (8, 4), (255, 0, 0)).save(self.base / 'hero.png')
        with self.assertRaisesRegex(ValueError, 'Source hash changed'):
            self.compose()

    def test_visual_without_any_ui_reference_is_rejected(self):
        self.add_visual(markup='')
        with self.assertRaisesRegex(ValueError, 'not referenced'):
            self.compose()

    def test_comment_only_reference_is_not_actual_asset_adoption(self):
        self.add_visual(markup='<!-- Planned but never rendered: assets/hero.png -->')
        with self.assertRaisesRegex(ValueError, 'not referenced'):
            self.compose()

    def test_different_asset_name_is_not_an_exact_ui_reference(self):
        self.add_visual(markup='<img src="assets/hero.png.backup" alt="A different file">')
        with self.assertRaisesRegex(ValueError, 'not referenced'):
            self.compose()

if __name__=='__main__':unittest.main()
