"""Behavioral checks for category boundaries, not wording of design advice."""
import unittest
import context


class DesignRoutingTest(unittest.TestCase):
    def test_four_independent_categories(self):
        cards = context.load_json(context.CARDS_FILE, {})['cards']
        self.assertTrue({'app', 'web', 'poster', 'documents'} <= cards.keys())
        for kind in ('app', 'web', 'poster', 'documents'):
            self.assertEqual(cards[kind]['experience_scope'], kind)

    def test_topics_cannot_import_other_domain_preferences(self):
        cards = {'experience_scopes': {'shared': ['language'], 'app': ['touch'], 'documents': ['word']}}
        card = {'experience_scope': 'app'}
        self.assertTrue(context.note_in_scope({'key': 'touch'}, card, cards))
        self.assertTrue(context.note_in_scope({'key': 'language'}, card, cards))
        self.assertFalse(context.note_in_scope({'key': 'word', 'text': 'App UI 文档'}, card, cards))
        self.assertFalse(context.note_in_scope({'key': 'project-017-ui'}, card, cards))

    def test_legacy_consumers_without_scope_keep_their_behavior(self):
        self.assertTrue(context.note_in_scope({'key': 'anything'}, {}, {}))

    def test_new_scoped_notes_are_recalled_without_editing_registry(self):
        self.assertTrue(context.note_in_scope({'key':'new','scope':'ui'},{'experience_scope':'app'},{}))
        self.assertFalse(context.note_in_scope({'key':'new','scope':'documents'},{'experience_scope':'web'},{}))
        self.assertFalse(context.note_in_scope({'key':'new','scope':'project'},{'experience_scope':'app'},{}))


if __name__ == '__main__':
    unittest.main()
