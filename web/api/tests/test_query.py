import mock

from django.test import tag, TestCase

from api.query import TimesQuery


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


class TestTimesQuery(TestCase):

    @tag('unit')
    def test_query_str_and_params(self):
        label = 'Environment'
        id_ = 'someid'
        expected = (
            "MATCH p = (environment:Environment)-[*]->(other)"
            "\nWHERE environment.account_number_name = $identity"
            "\nWITH relationships(p) as rels"
            "\nUNWIND rels as r"
            "\nreturn DISTINCT r.from as t"
            "\nORDER BY t DESC"
        )
        q = TimesQuery(label, id_)
        self.assertEquals(str(q), expected)
        self.assertEquals(q.params['identity'], id_)

    @tag('unit')
    @mock.patch('api.query.get_connection')
    def test_fetch(self, m_connection):
        data = [[{'t': 1}, {'t': 2}, {'t': 3}]]
        m_connection.return_value = FakeConnection(data)
        q = TimesQuery('Environment', 'someid')
        self.assertListEqual([1, 2, 3], q.fetch())

        data = [[]]
        m_connection.return_value = FakeConnection(data)
        self.assertListEqual([], q.fetch())
