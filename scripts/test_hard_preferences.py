import unittest
from experience import new_notes_doc, upsert_note, NOTE_CAPS


class ProtectedPreferencesTests(unittest.TestCase):
    def test_capacity_pruning_keeps_explicit_hard_rules(self):
        doc=new_notes_doc()
        upsert_note(doc,'preference','strict-visible-design-rules','用户硬性规定',on='2026-01-01')
        for i in range(NOTE_CAPS['preference']):
            upsert_note(doc,'preference',f'normal-{i}',f'其它偏好内容编号{i}',on='2026-11-08')
        self.assertEqual(len(doc['notes']),NOTE_CAPS['preference'])
        self.assertTrue(any(n['key']=='strict-visible-design-rules' for n in doc['notes']))


if __name__=='__main__':unittest.main()
