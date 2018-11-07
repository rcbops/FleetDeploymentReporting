import mock

from django.test import TestCase
from django.test import tag

from cloud_snitch.models import registry
from collections import OrderedDict

from api.diff import Diff
from api.diff import DiffQuery
from api.diff import DiffSideQuery
from api.diff import DiffStateQuery
from api.diff import Identity
from api.diff import Node
from api.diff import NodeDiff


class TestIdentity(TestCase):
    """Test the identity object."""
    @tag('unit')
    def test_unmapped_label(self):
        """Test with an unknown label."""
        i = Identity('somelabel', 'someprop', 'someid')
        self.assertEqual(i.label, 'somelabel')

    @tag('unit')
    def test_mapped_label(self):
        """Test with a known label."""
        i = Identity('environment', 'someprop', 'someid')
        self.assertEqual(i.label, 'Environment')

    @tag('unit')
    def test_prop_and_id(self):
        """Test property and identity value."""
        i = Identity('environment', 'someprop', 'someid')
        self.assertEqual(i.prop, 'someprop')
        self.assertEqual(i.value, 'someid')


class TestNode(TestCase):
    """Test the node object."""
    @tag('unit')
    def test_init(self):
        """Test init of a node."""
        # Test with no flags
        n = Node('identity')
        self.assertEqual(n.identity, 'identity')
        self.assertTrue(len(n.children) == 0)
        self.assertTrue(len(n.flags) == 0)

        # Test with flags
        n = Node('identity', flags=['t1', 't1', 't2', 't2'])
        self.assertTrue(isinstance(n.flags, set))
        self.assertTrue(n.flags, set(['t1', 't2']))

    @tag('unit')
    def test_flag(self):
        """Test the flag method."""
        # Test no flags
        n = Node('identity')
        self.assertTrue(n.flags == set())

        # Test adding single non list flag
        n.flag('t1')
        self.assertTrue(n.flags == set(['t1']))

        # Test adding list of flags
        n.flag(['t2', 't3'])
        self.assertTrue(n.flags == set(['t1', 't2', 't3']))

    @tag('unit')
    def test_add_child(self):
        """Test adding a child node."""
        # Create parent and child nodes.
        parent = Node(Identity('environment', 'uuid', '12345'))
        child = Node(Identity('host', 'hostname_environment', 'some_host'))

        # Add the child to the parent.
        parent.add_child(child)
        self.assertEquals(
            parent.children[('Host', 'hostname_environment', 'some_host')],
            child
        )

        # Check dict representation of parent.
        d = parent.to_dict()
        self.assertEqual(d['model'], 'Environment')
        self.assertEqual(d['id'], '12345')
        self.assertEqual(len(d['flags']), 0)

        # Check dict representation of child.
        self.assertEqual(len(d['children']), 1)
        c = d['children'][0]
        self.assertEqual(c['model'], 'Host')
        self.assertEqual(c['id'], 'some_host')
        self.assertEqual(len(c['flags']), 0)


class TestDiffQuery(TestCase):
    @tag('unit')
    def test_init(self):
        """Test init of the base diff query class."""
        p = ['Environment', 'Host', 'AptPackage']
        q = DiffQuery(p, 'someid', (0, 1))
        self.assertEqual(q.path, p)
        self.assertEqual(q.end, 'AptPackage')
        self.assertEqual(q.t1, 0)
        self.assertEqual(q.t2, 1)
        self.assertEqual(q.identity, 'someid')
        self.assertEqual(q.pagesize, 5000)

        self.assertEqual(q.params['identity'], 'someid')
        self.assertEqual(q.params['t1'], 0)
        self.assertEqual(q.params['t2'], 1)

        self.assertEqual(q.selects[0], 'environment.uuid')
        self.assertEqual(q.selects[1], 'host.hostname_environment')
        self.assertEqual(q.selects[2], 'aptpackage.name_version')

    @tag('unit')
    @mock.patch('api.diff.DiffQuery.fetch', side_effect=[[1], [2, 3], []])
    def test_fetch_all(self, m_fetch):
        """Test that looping stops on empty results."""
        results = []
        p = ['Environment', 'Host', 'AptPackage']
        q = DiffQuery(p, 'someid', (0, 1))
        for result in q.fetch_all():
            results.append(result)
        self.assertEqual(results[0], 1)
        self.assertEqual(results[1], 2)
        self.assertEqual(results[2], 3)


class TestDiffSideQuery(TestCase):
    """Tests the diff side query class."""

    @tag('unit')
    def test_query_generation(self):
        path = ['Environment', 'Host', 'AptPackage']
        identity = 'syncuuidtest'
        times = (
            0,
            1
        )
        q = DiffSideQuery(path, identity, times)
        expected = (
            "MATCH p_t2 = (environment:Environment)-[:HAS_HOST]->"
            "(host:Host)-[:HAS_APT_PACKAGE]->(aptpackage:AptPackage)"
            "\nWHERE environment.uuid = $identity AND "
            "ALL (r IN RELATIONSHIPS(p_t2) WHERE r.from <= $t2 < r.to)"
            "\nWITH COLLECT([environment,host,aptpackage]) as t2_nodes"
            "\nMATCH p_t1 = (environment:Environment)-[:HAS_HOST]->"
            "(host:Host)-[:HAS_APT_PACKAGE]->(aptpackage:AptPackage)"
            "\nWHERE environment.uuid = $identity AND "
            "ALL (r IN RELATIONSHIPS(p_t1) WHERE r.from <= $t1 < r.to) AND "
            "NOT [environment,host,aptpackage] IN t2_nodes"
            "\nRETURN environment.uuid,host.hostname_environment,"
            "aptpackage.name_version"
            "\nORDER BY environment.uuid,host.hostname_environment,"
            "aptpackage.name_version"
        )
        self.assertEqual(str(q), expected)

    @tag('unit')
    def test_params(self):
        """Test query params."""
        path = ['Environment', 'Host', 'AptPackage']
        identity = 'syncuuidtest'
        times = (
            0,
            1
        )
        q = DiffSideQuery(path, identity, times)
        self.assertEqual(q.params['t1'], 0)
        self.assertEqual(q.params['t2'], 1)
        self.assertEqual(q.params['identity'], identity)


class TestDiffStateQuery(TestCase):
    """Tests the diff state query class."""
    @tag('unit')
    def test_query_generation(self):
        path = ['Environment', 'Host']
        identity = 'syncuuidtest'
        times = (
            0,
            1
        )
        q = DiffStateQuery(path, identity, times)
        expected = (
            "MATCH p_t1 = (environment:Environment)-[:HAS_HOST]->(host:Host)"
            "\nMATCH p_t2 = (environment:Environment)-[:HAS_HOST]->(host:Host)"
            "\nMATCH (host)-[r_t1_state:HAS_STATE]->(t1_state:HostState)"
            "\nMATCH (host)-[r_t2_state:HAS_STATE]->(t2_state:HostState)"
            "\nWHERE environment.uuid = $identity AND "
            "r_t1_state.from <= $t1 < r_t1_state.to AND "
            "r_t2_state.from <= $t2 < r_t2_state.to AND "
            "t1_state <> t2_state AND "
            "ALL (r IN RELATIONSHIPS(p_t1) WHERE r.from <= $t1 < r.to) AND "
            "ALL (r in RELATIONSHIPS(p_t2) WHERE r.from <= $t2 < r.to)"
            "\nRETURN environment.uuid,host.hostname_environment"
            "\nORDER BY environment.uuid,host.hostname_environment"
        )
        self.assertEqual(str(q), expected)

    @tag('unit')
    def test_params(self):
        """Test query params."""
        path = ['Environment', 'Host']
        identity = 'syncuuidtest'
        times = (
            0,
            1
        )
        q = DiffStateQuery(path, identity, times)
        self.assertEqual(q.params['t1'], 0)
        self.assertEqual(q.params['t2'], 1)
        self.assertEqual(q.params['identity'], 'syncuuidtest')


class TestDiff(TestCase):
    """Test the diff class."""

    @tag('unit')
    @mock.patch('api.diff.DiffSideQuery')
    @mock.patch('api.diff.DiffStateQuery')
    def test_init(self, m_state, m_side):

        m_state.fetch_all.return_value = []
        m_side.fetch_all.return_value = []

        model = 'Environment'
        identity = 'someid'
        d = Diff(model, identity, 0, 1)

        self.assertEqual(d.model, model)
        self.assertEqual(d.identity, identity)
        self.assertEqual(d.t1, 0)
        self.assertEqual(d.t2, 1)

        # Assert that queries are called on increasing length paths only.
        l_path = 0
        for call in m_side.call_args_list:
            path = call[0][0]
            self.assertTrue(len(path) >= l_path)
            l_path = max(l_path, len(path))

        # Assert that state queries are ignored for stateless models.
        stateless = set()
        for m in registry.models:
            if not registry.state_properties(m):
                stateless.add(m)
        for call in m_state.call_args_list:
            path = call[0][0]
            self.assertFalse(path[-1] in stateless)

    @tag('unit')
    @mock.patch('api.diff.DiffSideQuery')
    @mock.patch('api.diff.DiffStateQuery')
    def test_add_child(self, m_state, m_side):
        m_state.fetch_all.return_value = []
        m_side.fetch_all.return_value = []
        m_node = mock.Mock()
        m_node.identity.hash_key = ('Environment', 'uuid', 'someid')

        model = 'Environment'
        identity = 'someid'
        d = Diff(model, identity, 0, 1)

        d.add_child(m_node)
        self.assertEqual(d.children[('Environment', 'uuid', 'someid')], m_node)

    @tag('unit')
    @mock.patch('api.diff.DiffSideQuery')
    @mock.patch('api.diff.DiffStateQuery')
    def test_feed(self, m_state, m_side):
        m_state.fetch_all.return_value = []
        m_side.fetch_all.return_value = []

        model = 'Environment'
        identity = 'someid'
        d = Diff(model, identity, 0, 1)

        row = OrderedDict()
        row['environment.uuid'] = 'e_uuid'
        row['host.hostname_environment'] = 'h_hostname'
        row['aptpackage.name_version'] = 'a_name'

        d.feed(row, ['t1'])
        current = d.children[('Environment', 'uuid', 'e_uuid')]
        self.assertEqual(current.identity.label, 'Environment')
        self.assertEqual(current.identity.prop, 'uuid')
        self.assertEqual(current.identity.value, 'e_uuid')
        self.assertTrue(len(current.flags) == 0)

        current = current.children[
            ('Host', 'hostname_environment', 'h_hostname')
        ]
        self.assertEqual(current.identity.label, 'Host')
        self.assertEqual(current.identity.prop, 'hostname_environment')
        self.assertEqual(current.identity.value, 'h_hostname')
        self.assertTrue(len(current.flags) == 0)

        current = current.children[('AptPackage', 'name_version', 'a_name')]
        self.assertEqual(current.identity.label, 'AptPackage')
        self.assertEqual(current.identity.prop, 'name_version')
        self.assertEqual(current.identity.value, 'a_name')
        self.assertEqual(current.flags, set(['t1']))


class TestNodeDiff(TestCase):

    @tag('unit')
    @mock.patch('api.diff.NodeDiff.node_at_time', side_effect=['n1', 'n2'])
    def test_init(self, m_node_at_time):
        """Test NodeDiff init."""
        model = 'Host'
        identity = 'someid'
        t1 = 0
        t2 = 1
        d = NodeDiff(model, identity, t1, t2)

        self.assertEqual(d.model, model)
        self.assertEqual(d.t1, t1)
        self.assertEqual(d.t2, t2)
        self.assertEqual(d.params['identity'], identity)
        self.assertEqual(d.node_t1, 'n1')
        self.assertEqual(d.node_t2, 'n2')

    @tag('unit')
    @mock.patch('api.diff.NodeDiff.node_at_time')
    def test_to_list(self, m_node_at_time):
        """Test NodeDiff to_list()."""
        n1 = OrderedDict()
        n1['prop_b'] = 'value_2'
        n1['prop_a'] = 'value_1'

        n2 = OrderedDict()
        n2['prop_b'] = 'value_3'
        n2['prop_c'] = 'value_4'

        m_node_at_time.side_effect = [n1, n2]

        model = 'Host'
        identity = 'someid'
        t1 = 0
        t2 = 1
        d = NodeDiff(model, identity, t1, t2)

        d_list = d.to_list()
        self.assertEqual(d_list[0]['name'], 'prop_a')
        self.assertEqual(d_list[0]['t1'], 'value_1')
        self.assertTrue(d_list[0]['t2'] is None)

        self.assertEqual(d_list[1]['name'], 'prop_b')
        self.assertEqual(d_list[1]['t1'], 'value_2')
        self.assertEqual(d_list[1]['t2'], 'value_3')

        self.assertEqual(d_list[2]['name'], 'prop_c')
        self.assertTrue(d_list[2]['t1'] is None)
        self.assertEqual(d_list[2]['t2'], 'value_4')

    @tag('unit')
    @mock.patch('api.diff.NodeDiff._fetch')
    def test_node_at_time(self, m_fetch):

        class FakeResult:
            def single(self):
                return {
                    'n': {
                        'prop_a': 'value_a',
                        'prop_b': 'value_b'
                    },
                    'ns': {
                        'prop_c': 'value_c',
                        'prop_d': 'value_d'
                    }
                }

        m_fetch.return_value = FakeResult()

        model = 'Host'
        identity = 'someid'
        t1 = 0
        t2 = 1
        d = NodeDiff(model, identity, t1, t2)

        n = d.node_at_time(0)
        self.assertEqual(n['prop_a'], 'value_a')
        self.assertEqual(n['prop_b'], 'value_b')
        self.assertEqual(n['prop_c'], 'value_c')
        self.assertEqual(n['prop_d'], 'value_d')

        expected = (
            "MATCH p = (environment:Environment)-[:HAS_HOST]->"
            "(n:Host)-[:HAS_STATE]->(ns:HostState) WHERE "
            "ALL (r IN RELATIONSHIPS(p) WHERE r.from <= $t < r.to) AND "
            "n.hostname_environment = $identity RETURN n,ns LIMIT 1"
        )
        self.assertEqual(expected, m_fetch.call_args_list[0][0][0])
