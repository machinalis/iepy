from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from iepy.models import IEDocument
from tvseries.scripts.preprocess import media_wiki_to_txt


class TestMW2TxtCreator(TestCase):
    """Tests for Media Wiki to txt creator"""

    def setUp(self):
        patcher = mock.patch.object(IEDocument, 'save')
        self.mock_save = patcher.start()
        self.addCleanup(patcher.stop)
        self.doc = IEDocument(metadata={'raw_text': 'hello world'})

    def test_simple_text_is_preserved(self):
        media_wiki_to_txt(self.doc)
        self.assertEqual(self.doc.text, 'hello world')

    def test_save_is_called(self):
        media_wiki_to_txt(self.doc)
        self.mock_save.assert_called_once_with()

    def test_with_empty_document_not_save_is_done(self):
        self.doc.metadata = {}
        media_wiki_to_txt(self.doc)
        self.assertFalse(self.mock_save.called)

    def test_directives_are_stripped_enterely(self):
        direct = "{{episodes\n|previous = Private Lives\n|next = Lockdown\n}}"
        self.doc.metadata['raw_text'] += direct
        media_wiki_to_txt(self.doc)
        self.assertEqual(self.doc.text, 'hello world')

    def test_new_lines_are_preserved(self):
        text = 'Hello\nmy\nloved\nworld.'
        self.doc.metadata['raw_text'] = text
        media_wiki_to_txt(self.doc)
        self.assertEqual(self.doc.text, text)

    def test_titles_content_is_kept_with_ending_point(self):
        title = "==Cool Stuff==\nHere it is."
        self.doc.metadata['raw_text'] = title
        media_wiki_to_txt(self.doc)
        self.assertEqual(self.doc.text, 'Cool Stuff.\nHere it is.')
