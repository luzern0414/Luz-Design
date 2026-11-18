"""Evidence citations and limitations are content, not decorative process metadata."""
import unittest
import check_document


class EvidenceContentTests(unittest.TestCase):
    def test_references_and_source_attribution_are_allowed(self):
        for text in ['参考来源', '数据来源', '数据来源：官方年度报告，第 3 章。', '信息来源：已公开的接口文档。',
                     '部分获取：仅审阅 page.pdf 小节，其余内容未验证。', '适用版本：3.1']:
            errors = []
            check_document.check_text(text, 'content', errors)
            check_document.check_heading(text, 'heading', errors)
            self.assertEqual(errors, [], text)

    def test_internal_collection_statistics_still_are_process_metadata(self):
        errors = []
        check_document.check_text('来源统计：采集 123 个来源', 'content', errors)
        self.assertTrue(any('source metadata' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
