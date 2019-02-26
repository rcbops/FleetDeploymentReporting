import mock

from django.test import SimpleTestCase
from django.test import tag
from web.finders import AngularTemplateFinder


class FakeStorage:
    def __init__(self, *args, exists=True):
        self._exists = exists
        self.location = ''

    def set_exists(self, exists):
        self._exists = exists

    def exists(self, *args, **kwargs):
        return self._exists


class TestAngularTemplateFinder(SimpleTestCase):
    """Test the AngularTemplateFinder class."""
    def setUp(self):
        self.old_storage_class = AngularTemplateFinder.storage_class
        AngularTemplateFinder.storage_class = FakeStorage
        self.file_list = [
            'not/web/html',
            'web/html/some/path/a.html',
            'web/html/some/path/b.js',
            'web/html/some/path/c.html'
        ]

    def tearDown(self):
        AngularTemplateFinder.storage_class = self.old_storage_class

    @tag('unit')
    @mock.patch('web.finders.utils.get_files')
    @mock.patch('web.finders.os.path.isdir')
    def test_list(self, m_isdir, m_get_files):
        """Tests that only the correct html files are yielded."""
        m_get_files.return_value = self.file_list
        atf = AngularTemplateFinder()
        r = list(atf.list(None))
        self.assertEqual(len(r), 2)
        for path, _ in r:
            self.assertTrue(path.startswith('web/html'))
            self.assertTrue(path.endswith('.html'))

    @tag('unit')
    @mock.patch('web.finders.utils.get_files')
    @mock.patch('web.finders.os.path.isdir')
    def test_not_exists(self, m_isdir, m_get_files):
        """Tests that nothing is yielded when storage does not exist."""
        m_get_files.return_value = self.file_list
        atf = AngularTemplateFinder()
        atf.storage.set_exists(False)
        r = list(atf.list(None))
        self.assertEqual(len(r), 0)
