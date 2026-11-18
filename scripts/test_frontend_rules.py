import tempfile
import unittest
from pathlib import Path
from frontend_rules import source_issues


class InteractionPolicyTests(unittest.TestCase):
    def scan(self, text, **options):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'index.html').write_text(text, encoding='utf-8')
            return source_issues(tmp, **options)

    def test_visual_preferences_do_not_block_an_owned_source(self):
        source = '<button>查看今天的记录</button><svg aria-hidden="true"></svg>'
        self.assertEqual(self.scan(source), [])
        self.assertEqual([item['rule'] for item in self.scan(source, include_suggestions=True)],
                         ['forbidden-copy'])

    def test_warning_with_no_business_input_is_allowed(self):
        self.assertEqual(self.scan('<el-dialog role="alertdialog" aria-label="操作警告"><p>操作未保存</p><button>取消</button><button>确认</button></el-dialog>'), [])

    def test_warning_marker_cannot_hide_a_form(self):
        self.assertTrue(self.scan('<el-dialog role="alertdialog"><el-input v-model="name"></el-input><button>保存</button></el-dialog>'))

    def test_directional_panel_is_not_a_warning_exception(self):
        self.assertTrue(self.scan('<el-drawer role="alertdialog">操作失败</el-drawer>'))

    def test_component_confirm_method_is_not_a_dialog(self):
        self.assertEqual(self.scan('<script>picker.value.confirm(); showNotify("已保存")</script>'), [])

    def test_horizontal_numeric_input_is_rejected(self):
        self.assertTrue(self.scan('<input type="range" aria-label="数量">'))

    def test_specific_business_dates_are_allowed_without_legalizing_unrelated_dates(self):
        self.assertEqual(self.scan('<el-input type="date" data-business-date aria-label="记录日期"></el-input>'), [])
        self.assertEqual(self.scan('<van-date-picker data-business-date></van-date-picker>'), [])
        self.assertTrue(self.scan('<input type="date">'))
        self.assertTrue(self.scan('<input type="datetime-local" data-business-date>'))

    def test_unclassified_dialog_still_requires_review(self):
        self.assertTrue(self.scan('<dialog open>设置</dialog>'))

    def test_documented_component_title_is_not_native_tooltip(self):
        self.assertEqual(self.scan('<van-tab :title="line.name"></van-tab>'), [])
        self.assertTrue(self.scan('<button :title="line.name">操作</button>'))
        self.assertTrue(self.scan('<other-widget title="说明"></other-widget>'))


if __name__ == '__main__':
    unittest.main()
