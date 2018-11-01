import mock

from django.test import tag
from django.test import TestCase

from neo4jdriver.exceptions import InvalidLabelError
from neo4jdriver.exceptions import InvalidPropertyError
from neo4jdriver.query import ColumnQuery
from neo4jdriver.query import Query

from . import base  # noqa f401


class FakeRecords(list):

    def single(self):
        return self[0]


class FakeDataset:

    def __init__(self, data):
        self.data = data
        self.count = 0

    def get_data(self):
        res = self.data[self.count]
        self.count += 1
        return res


class FakeTransaction:

    def __init__(self, data):
        self.data = data

    def begin_transaction(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def run(self, query, **params):
        return self.data.get_data()


class FakeSession:

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return FakeTransaction(self.data)

    def __exit__(self, *args):
        pass


class FakeConnection:

    def __init__(self, data):
        self.data = FakeDataset(data)

    def session(self):
        return FakeSession(self.data)


class TestQuery(TestCase):
    """
    RETURN environment
    ORDER BY environment.account_number_name ASC
    """

    @tag('unit')
    def test_match_root_label(self):
        """Test match clause targeted at a root level model."""
        q = Query('Environment')
        expected = "MATCH (environment:Environment)"
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_match_with_state(self):
        """Test match clause including a model with state."""
        q = Query('Host')
        expected = (
            "MATCH (environment:Environment)-[r0:HAS_HOST]->(host:Host) "
            "\nMATCH (host)-[r_host_state:HAS_STATE]->(host_state:HostState)"
        )
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_return_root_label(self):
        """Test return clause targeted at a root level model."""
        q = Query('Environment')
        expected = "RETURN environment"
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_return_with_state(self):
        """Test return clause that should include state."""
        q = Query('Host')
        expected = 'RETURN environment, host, host_state'
        self.assertTrue(expected in str(q))

    @tag('unit')
    @mock.patch('neo4jdriver.query.utils.milliseconds_now', return_value=10)
    def test_default_time(self, m_now):
        """Test that default time parameter."""
        q = Query('Environment')
        self.assertEquals(q.params['time'], 10)
        q = Query('Environment')
        q.time(None)
        self.assertEquals(q.params['time'], 10)

    @tag('unit')
    def test_provided_time(self):
        """Test that providing a time changes the query params."""
        q = Query('Environment')
        q.time(3)
        self.assertEquals(q.params['time'], 3)

    @tag('unit')
    def test_orderby_default(self):
        """Test default orderby clause."""
        q = Query('Environment')
        expected = "ORDER BY environment.account_number_name ASC"
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_orderby_no_label(self):
        """Test a single nondefault orderby"""
        q = Query('Environment')
        q.orderby('account_number', 'DESC')
        expected = "ORDER BY environment.account_number DESC"
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_orderby_invalid_property(self):
        """Test that orderby raises InvalidPropertyError"""
        q = Query('Environment')
        with self.assertRaises(InvalidPropertyError):
            q.orderby('invalidproperty', 'ASC')

    @tag('unit')
    def test_orderby_invalid_label(self):
        """Test that orderby raises InvalidLabelError"""
        q = Query('Environment')
        with self.assertRaises(InvalidLabelError):
            q.orderby('aproperty', 'DESC', label='invalidlabel')

    @tag('unit')
    def test_orderby_multiple(self):
        """Test multiple orderby statements."""
        q = Query('Environment')
        q.orderby('account_number', 'ASC', label='Environment')
        q.orderby('name', 'DESC', label='Environment')
        expected = (
            "ORDER BY environment.account_number ASC, "
            "environment.name DESC"
        )
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_orderby_state_property(self):
        """Test orderby on a state property."""
        q = Query('Host')
        q.orderby('kernel', 'DESC', label='Host')
        expected = 'ORDER BY host_state.kernel DESC'
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_limit_none(self):
        """Test query where no limit has been set."""
        q = Query('Environment')
        self.assertFalse('LIMIT' in str(q))

    @tag('unit')
    def test_limit(self):
        """Test query where a limit as been set."""
        q = Query('Environment')
        q.limit(5)
        q.limit(10)
        self.assertTrue('LIMIT 10' in str(q))

    @tag('unit')
    def test_skip_none(self):
        """Test query where no skip has been set."""
        q = Query('Environment')
        self.assertFalse('SKIP' in str(q))

    @tag('unit')
    def test_skip(self):
        """Test query where skip has been set."""
        q = Query('Environment')
        q.skip(5)
        q.skip(10)
        self.assertTrue('SKIP 10' in str(q))

    @tag('unit')
    def test_filter_without_label(self):
        """Test filtering using default label."""
        q = Query('Host')
        q.filter('hostname', '=', 'somehostname')
        expected = 'WHERE host.hostname = $filterval0'
        self.assertTrue(expected in str(q))
        self.assertEquals(q.params['filterval0'], 'somehostname')

    @tag('unit')
    @mock.patch('neo4jdriver.query.prep_val')
    def test_filter_calls_prep_val(self, m_prep):
        q = Query('Host')
        q.filter('processor_cores', '=', '42')
        m_prep.assert_called_once_with(
            'Host',
            'processor_cores',
            '42',
            raise_for_error=False
        )

    @tag('unit')
    def test_filter_with_label(self):
        """Test filtering with a non default label."""
        q = Query('Host')
        q.filter('account_number', '=', 'somenumber', label='Environment')
        expected = 'WHERE environment.account_number = $filterval0'
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_filter_invalid_label(self):
        """Test filtering with invalid label."""
        q = Query('Host')
        with self.assertRaises(InvalidLabelError):
            q.filter('someprop', 'someop', 'someval', label='InvalidLabel')

    @tag('unit')
    def test_filter_invalid_prop(self):
        """Test filtering with invalid property."""
        q = Query('Host')
        with self.assertRaises(InvalidPropertyError):
            q.filter('someinvalidprop', 'someop', 'someval')

    @tag('unit')
    def test_multiple_filters(self):
        """Tests more than one filters."""
        q = Query('Host')
        q.filter('hostname', '=', 'somehostname')
        q.filter('kernel', '=', 'somekernel')
        expected = (
            'WHERE host.hostname = $filterval0 AND '
            'host_state.kernel = $filterval1'
        )
        self.assertTrue(expected in str(q))

    @tag('unit')
    def test_rel_filters(self):
        """Test adding time filters on relationships."""
        q = Query('Virtualenv')
        expected = (
            "r0.from <= $time < r0.to AND r1.from <= $time < r1.to "
            "AND r_host_state.from <= $time < r_host_state.to"
        )
        self.assertTrue(expected in str(q))

    @tag('unit')
    @mock.patch('neo4jdriver.query.get_connection')
    def test_count(self, m_connection):
        """Tests counting number of results."""
        data = FakeRecords()
        data.append({'total': 13})
        data = [data]
        m_connection.return_value = FakeConnection(data)
        q = Query('Environment')
        self.assertEquals(q.count(), 13)

    @tag('unit')
    @mock.patch('neo4jdriver.query.Query.fetch')
    def test_page_defaults(self, m_fetch):
        """Test default arguments to page() method."""
        q = Query('Environment')
        q.page()

        expected = 'SKIP 0'
        self.assertTrue(expected in str(q))
        expected = 'LIMIT 100'
        self.assertTrue(expected in str(q))

    @tag('unit')
    @mock.patch('neo4jdriver.query.get_connection')
    def test_page_with_page(self, m_fetch):
        """Test providing page with a page and a size."""
        q = Query('Environment')
        q.page(page=3, pagesize=500)
        expected = "SKIP 1000"
        self.assertTrue(expected in str(q))
        expected = "LIMIT 500"
        self.assertTrue(expected in str(q))

    @tag('unit')
    @mock.patch('neo4jdriver.query.get_connection')
    def test_page_with_index(self, m_fetch):
        """Test providing page an index and a size."""
        q = Query('Environment')
        q.page(index=3, pagesize=500)
        expected = "SKIP 2"
        self.assertTrue(expected in str(q))
        expected = "LIMIT 500"
        self.assertTrue(expected in str(q))

    @tag('unit')
    @mock.patch('neo4jdriver.query.get_connection')
    def test_page_with_negative_index(self, m_fetch):
        """Test providing page with a negative index and a size."""
        q = Query('Environment')
        q.page(index=-10, pagesize=500)
        expected = "SKIP 0"
        self.assertTrue(expected in str(q))
        expected = "LIMIT 500"
        self.assertTrue(expected in str(q))


class TestColumnQuery(TestCase):
    """Test the column query."""

    @tag('unit')
    def test_add_column_invalid_model(self):
        """Test that adding a column with invalid model fails."""
        q = ColumnQuery('Environment')
        with self.assertRaises(InvalidLabelError):
            q.add_column('NotAModel', 'someprop')

    @tag('unit')
    def test_add_column_model_not_in_datapath(self):
        """Test that adding a valid model that is not in the datapath fails"""
        q = ColumnQuery('Environment')
        with self.assertRaises(InvalidLabelError):
            q.add_column('AptPackage', 'name')

    @tag('unit')
    def test_add_column_invalid_property(self):
        """Test that adding a column with invalid property fails."""
        q = ColumnQuery('Environment')
        with self.assertRaises(InvalidPropertyError):
            q.add_column('Environment', 'notaprop')

    @tag('unit')
    def test_adding_valid_column(self):
        """Test that adding a valid column works."""
        q = ColumnQuery('Environment')
        q.add_column('Environment', 'name')
        q.add_column('Environment', 'account_number', name='the_number')

    @tag('unit')
    def test_query_format(self):
        """Test that query string matches formatting."""
        q = ColumnQuery('Host')
        q.add_column('Environment', 'account_number')
        q.add_column('Host', 'kernel', 'kernel')
        expected = (
            "MATCH (environment:Environment)-[r0:HAS_HOST]->(host:Host) "
            "\nMATCH (host)-[r_host_state:HAS_STATE]->(host_state:HostState) "
            "\nWHERE r0.from <= $time < r0.to AND "
            "r_host_state.from <= $time < r_host_state.to"
            "\nRETURN environment.account_number AS"
            " `Environment.account_number`,"
            " host_state.kernel AS `kernel` "
            "\nORDER BY host.hostname_environment ASC"
        )
        self.assertEquals(expected, str(q))
