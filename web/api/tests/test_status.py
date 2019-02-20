import mock

from api.status import cache as cache_status
from api.status import neo4j as neo4j_status
from api.status import combined as combined_status
from django.test import SimpleTestCase
from django.test import tag
from neo4jdriver.tests.test_query import FakeConnection
from neo4jdriver.tests.test_query import FakeRecords


class TestCacheStatus(SimpleTestCase):

    @tag('unit')
    @mock.patch('api.status.django_cache.add')
    @mock.patch('api.status.django_cache.get')
    def test_good(self, m_get, m_add):
        m_get.return_value = 'test_cache_val'
        r = cache_status()
        self.assertTrue(r['status'])

    @tag('unit')
    @mock.patch('api.status.django_cache.add')
    @mock.patch('api.status.django_cache.get')
    def test_bad(self, m_get, m_add):
        m_get.return_value = 'a_bad_val'
        r = cache_status()
        self.assertFalse(r['status'])


class TestNeo4jStatus(SimpleTestCase):
    @tag('unit')
    @mock.patch('api.status.get_connection')
    def test_good(self, m_connection):
        data = FakeRecords()
        data.append({
            'type': 'store_size',
            'row': 'total',
            'value': 10
        })
        m_connection.return_value = FakeConnection([data])
        r = neo4j_status()
        self.assertTrue(r['status'])
        self.assertEqual(r['stats']['store_size']['total'], 10)

    @tag('unit')
    @mock.patch('api.status.get_connection')
    def test_bad(self, m_connection):
        m_connection.side_effect = Exception('this should fail')
        r = neo4j_status()
        self.assertTrue(r['status'] is False)


class TestCombinedStatus(SimpleTestCase):
    @tag('unit')
    @mock.patch('api.status.cache')
    @mock.patch('api.status.neo4j')
    def test_all_good(self, m_neo4j, m_cache):
        m_neo4j.return_value = {'status': True}
        m_neo4j.__name__ = 'neo4j'
        m_cache.return_value = {'status': True}
        m_cache.__name__ = 'cache'
        healthy, status = combined_status()
        self.assertTrue(healthy)

    @tag('unit')
    @mock.patch('api.status.cache')
    @mock.patch('api.status.neo4j')
    def test_some_bad(self, m_neo4j, m_cache):
        m_neo4j.return_value = {'status': False}
        m_neo4j.__name__ = 'neo4j'
        m_cache.return_value = {'status': True}
        m_cache.__name__ = 'cache'
        healthy, status = combined_status()
        self.assertFalse(healthy)
        m_neo4j.return_value = {'status': True}
        m_cache.return_value = {'status': False}
        healthy, status = combined_status()
        self.assertFalse(healthy)

    @tag('unit')
    @mock.patch('api.status.cache')
    @mock.patch('api.status.neo4j')
    def test_all_bad(self, m_neo4j, m_cache):
        m_neo4j.return_value = {'status': False}
        m_neo4j.__name__ = 'neo4j'
        m_cache.return_value = {'status': False}
        m_cache.__name__ = 'cache'
        healthy, status = combined_status()
        self.assertFalse(healthy)
