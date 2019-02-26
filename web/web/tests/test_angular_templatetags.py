import mock

from django.core.cache.backends.locmem import LocMemCache
from django.test import SimpleTestCase
from django.test import tag
from django.utils.safestring import SafeText
from web.templatetags import angular
from web.templatetags.angular import cached_angular_template as CAT
from web.templatetags.angular import cached_angular_templates as CATS

fake_CAT_data = ['a', 'b', 'c']
fake_list_data = [('a', None), ('b', None), ('c', None)]


class TestCachedTemplates(SimpleTestCase):
    @tag('unit')
    @mock.patch(
        'web.templatetags.angular.cached_angular_template',
        side_effect=fake_CAT_data
    )
    @mock.patch(
        'web.templatetags.angular.AngularTemplateFinder.list',
        return_value=fake_list_data
    )
    def test_render(self, m_finder, m_template):
        """Test that CATs renders CAT joined by newlines."""
        r = CATS()
        self.assertEqual("\n".join(['a', 'b', 'c']), r)
        self.assertTrue(isinstance(r, SafeText))


class FakeFinder:
    def __init__(self, paths):
        self.paths = paths

    def find(self, *args, **kwargs):
        return self.paths


class TestCachedTemplate(SimpleTestCase):
    """Test the single cached angular template tag."""
    def setUp(self):
        """Patch in a local memory cache."""
        self.locmem_cache = LocMemCache('default', {})
        self.locmem_cache.clear()
        self.patch = mock.patch.object(angular, 'cache', self.locmem_cache)
        self.patch.start()

    def tearDown(self):
        """Stop the patch."""
        self.patch.stop()

    @tag('unit')
    @mock.patch('web.templatetags.angular.finders.get_finders')
    @mock.patch(
        'builtins.open',
        new_callable=mock.mock_open,
        read_data='some_data'
    )
    def test_not_cached(self, m_file, m_get_finders):
        """Test behaviour of a template that is not cached."""
        m_get_finders.return_value = [FakeFinder(['a'])]
        key = '_angular_template_a'
        self.assertFalse(self.locmem_cache.get(key))
        html = CAT('a')
        expected = (
            '<script type="text/ng-template" id="/static/a">'
            'some_data'
            '</script>'
        )
        self.assertEqual(html, expected)
        self.assertEqual(self.locmem_cache.get(key), expected)

    @tag('unit')
    @mock.patch('web.templatetags.angular.finders.get_finders')
    @mock.patch(
        'builtins.open',
        new_callable=mock.mock_open,
        read_data='some_data'
    )
    def test_cached(self, m_file, m_get_finders):
        """Test behavior of a template that is cached."""
        m_get_finders.return_value = [FakeFinder(['a'])]
        key = '_angular_template_a'
        self.locmem_cache.add(key, 'the_data')
        html = CAT('a')
        expected = 'the_data'
        self.assertEqual(html, expected)
        self.assertEqual(self.locmem_cache.get(key), expected)
