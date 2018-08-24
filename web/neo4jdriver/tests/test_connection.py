import mock
import time

from django.test import tag
from django.test import TestCase

from neo4jdriver.connection import Connection

fake_neo4j_settings = {
    'uri': 'testuri',
    'username': 'testusername',
    'password': 'testpassword',
    'max_connection_lifetime': 1,
    'max_connection_pool_size': 2,
    'max_connection_age': 10
}


class TestConnection(TestCase):
    """Test the connection class."""

    @tag('unit')
    @mock.patch.dict(
        'neo4jdriver.connection.settings.NEO4J',
        fake_neo4j_settings
    )
    @mock.patch('neo4jdriver.connection.time.time', return_value=1)
    @mock.patch('neo4jdriver.connection.GraphDatabase.driver')
    def test_init(self, m_driver, m_time):
        """Test init."""
        c = Connection()
        self.assertEquals(c.uri, 'testuri')
        self.assertEquals(c.username, 'testusername')
        self.assertEquals(c.password, 'testpassword')
        self.assertEquals(c.max_connection_lifetime, 1)
        self.assertEquals(c.max_connection_pool_size, 2)
        self.assertEquals(c.start, 1)
        m_driver.assert_called_with(
            'testuri',
            auth=('testusername', 'testpassword'),
            max_connection_lifetime=1,
            max_connection_pool_size=2
        )

    @tag('unit')
    @mock.patch('neo4jdriver.connection.GraphDatabase.driver')
    def test_defaults(self, m_driver):
        """Test default optional settings."""
        c = Connection()
        self.assertEquals(c.max_connection_lifetime, 5 * 60)
        self.assertEquals(c.max_connection_pool_size, 50)

    @tag('unit')
    @mock.patch('neo4jdriver.connection.GraphDatabase.driver')
    def test_isvalid(self, m_driver):
        """Test isvalid function."""
        c = Connection()
        c.driver = None
        self.assertFalse(c.isvalid())

        c = Connection()
        c.start = 1
        self.assertFalse(c.isvalid())

        c.start = time.time()
        self.assertTrue(c.isvalid())

    @tag('unit')
    @mock.patch('neo4jdriver.connection.GraphDatabase.driver')
    def test_close(self, m_driver):
        """Test close."""
        # Test valid close
        c = Connection()
        c.close()
        self.assertTrue(c.driver is None)

        # test that nothing happens on invalid close.
        c = Connection()
        c.driver = None
        c.close()
