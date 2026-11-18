"""Behavior checks for the editable frontend package boundary (isolated fixtures)."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import frontend as f


class FrontendTests(unittest.TestCase):
    def setUp(self):
        # Test files are fixtures, never human visual-acceptance evidence.
        output=Path(os.environ.get('LUZ_DESIGN_TEST_OUTPUT',tempfile.gettempdir()))/'luz-design-tests'
        output.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=output)
        self.addCleanup(self.tmp.cleanup)
        self.s=Path(self.tmp.name).resolve();(self.s/'raw/99-delivery').mkdir(parents=True)
        f.write(self.s/'raw/99-delivery/MANIFEST.json',{})
        for target in ['template_library.select','template_library.record_output','template_library.require_selected']:
            mock=patch(target);mock.start();self.addCleanup(mock.stop)
        gate=patch('crawl_gate.require_session_preflight',return_value={'session':self.s,'raw':self.s/'raw'})
        gate.start();self.addCleanup(gate.stop)
        self.p=Path(f.init('app-task',self.s,'design')['package'])

    def reviewed(self):
        from PIL import Image
        image=self.s/'raw/fixture.png';Image.new('RGB',(240,300),'white').save(image)
        log=self.s/'raw/fixture.txt';log.write_text('Synthetic test fixture; not product acceptance.',encoding='utf-8')
        receipt=f.read(self.p/f.RECEIPT)
        browser=self.s/'raw/browser-fixture.json'
        f.write(browser,{'bundle_sha256':receipt['bundle_sha256'],'observations':['Synthetic contract fixture only'],'limitations':['Not product evidence']})
        q=f.quality_module();assessment=q.plan(q.read(q.CATALOG),q.digest(q.CATALOG),'luz-design','design')
        assessment.update(receipt_sha256=f.digest(self.p/f.RECEIPT),browser_report_sha256=f.digest(browser))
        for row in assessment['rows']:
            row.update(status='not-applicable',reason='Synthetic validator unit fixture; no product claim',reviewer='unit-test-fixture')
        quality=self.s/'raw/quality-fixture.json';f.write(quality,assessment)
        data={'bundle_sha256':receipt['bundle_sha256'],'reviewer':'unit-test-fixture',
              'browser_report':{'path':str(browser),'sha256':f.digest(browser)},
              'quality_assessment':{'path':str(quality),'sha256':f.digest(quality)},
              'blocking_findings':[],'component_usage':['fixture'],'limitations':['synthetic fixture'],
              'hard_rules':{'sha256':f.digest(f.HARD_RULES),'violations':[],'reviewed':sorted(f.REVIEW_RULES)},
              'loaded_assets':['artwork/list.webp','artwork/pattern.webp'],
              'experience_axes':{axis:{'status':'verified','observed':'Synthetic contract fixture only','limitations':['Not product evidence'],'evidence':[{'path':str(log),'sha256':f.digest(log)}]} for axis in ('UX','AX','DX')},
              'observations':[{'viewport':'fixture','finding':'fixture only','screenshot':{'path':str(image),'sha256':f.digest(image)}}],
              'interactions':[{'action':'fixture','result':'fixture','evidence':{'path':str(log),'sha256':f.digest(log)}}]}
        source=self.s/'raw/review-input.json';f.write(source,data)
        f.review(self.p,self.s,source)
        return source

    def test_paths_stay_inside_package(self):
        for name in ['../outside','a/../../outside','C:/outside','/outside','a\\outside','NUL','a/CON.txt','a.']:
            with self.subTest(name=name),self.assertRaises(ValueError):f.member(self.p,name)
        self.assertEqual(f.member(self.p,'app.js'),self.p/'app.js')

    def test_review_required_and_edit_invalidates_it(self):
        with self.assertRaisesRegex(ValueError,'review required'):f.verify_package(self.p,self.s)
        self.reviewed();f.verify_package(self.p,self.s)
        with (self.p/'app.js').open('a',encoding='utf-8') as handle:handle.write('\n// local change\n')
        with self.assertRaisesRegex(ValueError,'Build changed'):f.verify_package(self.p,self.s)
        f.seal(self.p,self.s)
        with self.assertRaisesRegex(ValueError,'review required'):f.verify_package(self.p,self.s)

    def test_component_bytes_are_checked_before_sealing(self):
        (self.p/'vendor/vant.min.js').write_text('changed runtime',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'source bytes changed'):f.seal(self.p,self.s)

    def test_missing_or_changed_evidence_rejected(self):
        source=self.reviewed();data=f.read(source);data['observations'][0]['screenshot']['sha256']='wrong'
        f.write(source,data)
        with self.assertRaisesRegex(ValueError,'recorded file'):f.review(self.p,self.s,source)
        proof=f.read(self.p/'review.json');(self.p/proof['interactions'][0]['evidence']['path']).write_text('altered')
        with self.assertRaisesRegex(ValueError,'review evidence'):f.verify_package(self.p,self.s)

    def test_zip_and_html_use_same_registered_build(self):
        import ui_package
        from ui_entry_policy import check_nonpage_delivery,html_delivery_contract
        self.reviewed()
        self.assertEqual(ui_package.mode(self.p),'frontend')
        self.assertEqual(html_delivery_contract(self.p/'index.html',session=self.s)['kind'],'frontend-ui')
        out=self.s/'raw/app.zip';ui_package.export_package(self.p,session=self.s,out=out)
        check_nonpage_delivery(out,self.s)
        import zipfile
        with zipfile.ZipFile(out,'a') as archive:archive.writestr('extra.js','unexpected')
        with self.assertRaises(ValueError):check_nonpage_delivery(out,self.s)

    def test_conflicting_receipt_is_not_an_escape_hatch(self):
        import ui_package
        (self.p/'luz-component-ui.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'exactly one'):ui_package.mode(self.p)
        with self.assertRaisesRegex(ValueError,'exactly one'):f.verify_package(self.p,self.s,False)

    def test_existing_build_requires_sources_and_build_log(self):
        with self.assertRaises(FileNotFoundError):f.verify_build(self.p,{'kind':'existing'})
        f.write(self.p/'build-record.json',{'command':'npm run build','toolchain':'node fixture','exit_code':0,'source_files':{}})
        with self.assertRaisesRegex(ValueError,'editable sources'):f.verify_build(self.p,{'kind':'existing'})

    def test_linked_project_cannot_omit_requirements(self):
        f.write(self.s/'raw/99-delivery/MANIFEST.json',{'project':{'state_root':'fixture'}})
        with self.assertRaisesRegex(ValueError,'ui-requirements'):f.seal(self.p,self.s)

    def test_generated_assets_cannot_be_omitted_or_changed(self):
        asset=self.p/'artwork/list.webp';asset.write_bytes(b'not a generated image')
        with self.assertRaisesRegex(ValueError,'asset bytes changed'):f.seal(self.p,self.s)

    def test_overlay_cannot_return_after_review(self):
        with (self.p/'index.html').open('a',encoding='utf-8') as out:out.write('<dialog open>设置</dialog>')
        with self.assertRaisesRegex(ValueError,'hard-rule violations'):f.seal(self.p,self.s)

    def test_rule_changes_invalidate_existing_review(self):
        self.reviewed()
        changed=self.s/'changed-rules.md';changed.write_text('A new user correction',encoding='utf-8')
        with patch.object(f,'HARD_RULES',changed):
            with self.assertRaisesRegex(ValueError,'Hard rules changed'):f.verify_package(self.p,self.s)

    def test_calling_imagegen_without_loading_assets_is_not_enough(self):
        source=self.reviewed();value=f.read(source);value['loaded_assets']=[];f.write(source,value)
        with self.assertRaisesRegex(ValueError,'actually loaded'):f.review(self.p,self.s,source)

    def test_missing_axis_cannot_be_hidden_by_a_visual_pass(self):
        source=self.reviewed();value=f.read(source);del value['experience_axes']['AX'];f.write(source,value)
        with self.assertRaisesRegex(ValueError,'separately verify'):f.review(self.p,self.s,source)

    def test_axis_without_executed_evidence_cannot_pass(self):
        source=self.reviewed();value=f.read(source);value['experience_axes']['DX']['evidence']=[];f.write(source,value)
        with self.assertRaisesRegex(ValueError,'missing actual evidence'):f.review(self.p,self.s,source)

    def test_quality_report_cannot_be_omitted(self):
        source=self.reviewed();value=f.read(source);del value['quality_assessment'];f.write(source,value)
        with self.assertRaisesRegex(ValueError,'quality_assessment'):f.review(self.p,self.s,source)

    def test_quality_report_must_describe_current_receipt_and_stage(self):
        source=self.reviewed();value=f.read(source);path=Path(value['quality_assessment']['path'])
        assessment=f.read(path);assessment['receipt_sha256']='old-build';f.write(path,assessment)
        value['quality_assessment']['sha256']=f.digest(path);f.write(source,value)
        with self.assertRaisesRegex(ValueError,'different sealed receipt'):f.review(self.p,self.s,source)
        assessment['receipt_sha256']=f.digest(self.p/f.RECEIPT);assessment['scope']['stage']='verification';f.write(path,assessment)
        value['quality_assessment']['sha256']=f.digest(path);f.write(source,value)
        with self.assertRaisesRegex(ValueError,'wrong owner/stage'):f.review(self.p,self.s,source)

    def test_review_does_not_rewrite_sealed_receipt(self):
        before=(self.p/f.RECEIPT).read_bytes();self.reviewed()
        self.assertEqual((self.p/f.RECEIPT).read_bytes(),before)

    def test_blocking_quality_pending_cannot_pass(self):
        source=self.reviewed();value=f.read(source);path=Path(value['quality_assessment']['path'])
        assessment=f.read(path);assessment['rows'][0]['status']='pending';f.write(path,assessment)
        value['quality_assessment']['sha256']=f.digest(path);f.write(source,value)
        with self.assertRaisesRegex(ValueError,'blocking pending'):f.review(self.p,self.s,source)


if __name__=='__main__':unittest.main()
