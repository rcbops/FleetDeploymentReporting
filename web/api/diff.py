import logging

from collections import OrderedDict
from cloud_snitch.models import registry
from neo4jdriver.query import Query

logger = logging.getLogger(__name__)
var_to_model_map = {m.lower(): m for m in registry.models}


class DiffQuery(Query):

    def __init__(self, path, identity, times, pagesize=5000):
        """Init the diff query

        :param path: Path to build a diff query around
        :type path: list
        :param identity: Starting node's identity
        :type identity: str
        :param times: Two times for comparison
        :type times: tuple
        :param pagesize: How many results to fetch at once
        :type pagesize: int
        """
        self.path = path
        self.end = self.path[-1]
        self.full_path = registry.path(self.end)
        self.t1 = times[0]
        self.t2 = times[1]
        self.identity = identity
        self.pagesize = pagesize

        self.selects = [
            '{}.{}'.format(
                self._var_from_label(m),
                registry.identity_property(m)
            ) for m in self.path
        ]

        self.params = {
            't1': self.t1,
            't2': self.t2,
            'identity': self.identity
        }

    @classmethod
    def _var_from_label(self, label):
        """Uniform label to cipher variable computation.

        :param label: A label to convert to a variable name
        :type label: str
        :returns: Converted label name
        :rtype: str
        """
        return label.lower()

    def fetch(self, page):
        """Get a page of results.

        :param page: Which page to fetch
        :type page: int
        :returns: Results from the fetch
        :rtype: list
        """
        skip = (page - 1) * self.pagesize
        q = '{} \nSKIP {}\nLIMIT {}'.format(str(self), skip, self.pagesize)
        rows = []
        for record in self._fetch(q):
            row = OrderedDict()
            for select in self.selects:
                row[select] = record[select]
            rows.append(row)
        return rows

    def fetch_all(self):
        """Fetch all pages.

        :yields: One result per match.
        :ytype: OrderedDict
        """
        page = 1
        go = True
        while go:
            rows = self.fetch(page)
            for row in rows:
                yield row
            if not rows:
                go = False
            page += 1


class DiffSideQuery(DiffQuery):
    """Models a query to find subpaths.

    Finds all paths on a 'side'. That is all paths of nodes that belong
    to one time but not the second time.

    This is used to find nodes that have been added or deleted.
    """
    def _match_clause(self):
        """Build the multistage match clause.

        Find all paths that match in t2. Then find all paths that match in t1
        that are not in t2.

        Example:
        If your path is Environment->Host->AptPackage

        MATCH
            p_t2 =
                (environment:Environment)-[:HAS_HOST]->
                (host:Host)-[:HAS_APT_PACKAGE]->
                (aptpackage:AptPackage)
        WHERE
            environment.uuid = $identity AND
            ALL (r IN RELATIONSHIPS(p_t2) WHERE r.from <= $t2 < r.to)
        WITH
            COLLECT([environment,host,aptpackage]) as t2_nodes
        MATCH
            p_t1 =
                (environment:Environment)-[:HAS_HOST]->
                (host:Host)-[:HAS_APT_PACKAGE]->
                (aptpackage:AptPackage)
        WHERE
            environment.uuid = $identity AND
            ALL (r IN RELATIONSHIPS(p_t1) WHERE r.from <= $t1 < r.to) AND
            NOT [environment,host,aptpackage] IN t2_nodes

        :returns: Major portion of cipher query
        :rtype: str
        """
        path_vars = []
        for model, _ in self.full_path:
            path_vars.append(self._var_from_label(model))
        path_vars.append(self._var_from_label(self.end))

        cipher = 'MATCH p_t2 = '
        for model, reltype in self.full_path:
            cipher += '({}:{})-[:{}]->'.format(
                self._var_from_label(model),
                model,
                reltype
            )
        cipher += '({}:{})'.format(
            self._var_from_label(self.end),
            self.end
        )

        cipher += '\nWHERE '
        cipher += '{}.{} = $identity AND '.format(
            self._var_from_label(self.path[0]),
            registry.identity_property(self.path[0])
        )
        cipher += 'ALL (r IN RELATIONSHIPS(p_t2) WHERE r.from <= $t2 < r.to)'
        cipher += '\nWITH COLLECT([{}]) as t2_nodes'.format(
            ','.join(path_vars)
        )

        cipher += '\nMATCH p_t1 = '
        for model, reltype in self.full_path:
            cipher += '({}:{})-[:{}]->'.format(
                self._var_from_label(model),
                model,
                reltype
            )
        cipher += '({}:{})'.format(
            self._var_from_label(self.end),
            self.end
        )
        cipher += '\nWHERE '
        cipher += '{}.{} = $identity AND '.format(
            self._var_from_label(self.path[0]),
            registry.identity_property(self.path[0])
        )
        cipher += 'ALL (r IN RELATIONSHIPS(p_t1) WHERE r.from <= $t1 < r.to)'
        cipher += ' AND NOT [{}] IN t2_nodes'.format(','.join(path_vars))
        return cipher

    def _return_clause(self):
        """Create the return clause of the query.

        Example:
        If the path is Environment->Host->AptPackage

        RETURN
            environment.uuid,
            host.hostname_environment,
            aptpackage.name_version

        :returns: Return clause of the query
        :rtype: str
        """
        return 'RETURN ' + ','.join(self.selects)

    def _orderby_clause(self):
        """Create the orderby clause of the query

        Example:
        If the path is Environment->Host->AptPackage

        ORDER BY
            environment.uuid,
            host.hostname_environment,
            aptpackage.name_version

        :returns: Orderby clause of the query.
        :rtype: str
        """
        return 'ORDER BY ' + ','.join(self.selects)

    def __str__(self):
        """Combine clauses into a single query.

        :returns: Combined clauses
        :rtype: str
        """
        return "\n".join([
            self._match_clause(),
            self._return_clause(),
            self._orderby_clause()
        ])


class DiffStateQuery(DiffQuery):

    def _match_clause(self):
        """Build match query.

        Should match starting at the start model and follow entity edges
        in time to the end model.

        From there, there should only be results if there are multiple
        state nodes, one for time t1 and one for time t2.

        Example:
        If the path is Environment->Host

        MATCH p_t1 = (environment:Environment)-[:HAS_HOST]->(host:Host)
        MATCH p_t2 = (environment:Environment)-[:HAS_HOST]->(host:Host)
        MATCH (host)-[r_t1_state:HAS_STATE]->(t1_state:HostState)
        MATCH (host)-[r_t2_state:HAS_STATE]->(t2_state:HostState)

        :returns: Match clause of the the query
        :rtype str:
        """
        cipher = "MATCH p_t1 = "
        for model, reltype in self.full_path:
            cipher += "({}:{})-[:{}]->".format(
                self._var_from_label(model),
                model,
                reltype
            )
        cipher += "({}:{})".format(
            self._var_from_label(self.end),
            self.end
        )

        cipher += "\nMATCH p_t2 = "
        for model, reltype in self.full_path:
            cipher += "({}:{})-[:{}]->".format(
                self._var_from_label(model),
                model,
                reltype
            )
        cipher += "({}:{})".format(
            self._var_from_label(self.end),
            self.end
        )

        # Match state on 'a' time
        cipher += (
            "\nMATCH ({})-[r_t1_state:HAS_STATE]->(t1_state:{}State)".format(
                self._var_from_label(self.end),
                self.end
            )
        )

        # Match state on 'b' time
        cipher += (
            "\nMATCH ({})-[r_t2_state:HAS_STATE]->(t2_state:{}State)".format(
                self._var_from_label(self.end),
                self.end
            )
        )
        return cipher

    def _where_clause(self):
        """Build the where clause.

        Example:
        If the path is Environment->Host

        WHERE
            environment.uuid = $identity AND
            r_t1_state.from <= $t1 < r_t1_state.to AND
            r_t2_state.from <= $t2 < r_t2_state.to AND
            t1_state <> t2_state AND
            ALL (r IN RELATIONSHIPS(p_t1) WHERE r.from <= $t1 < r.to) AND
            ALL (r in RELATIONSHIPS(p_t2) WHERE r.from <= $t2 < r.to)

        :returns: Where clause
        :rtype: str
        """
        wheres = ['{}.{} = $identity'.format(
            self._var_from_label(self.path[0]),
            registry.identity_property(self.path[0])
        )]

        wheres.append('r_t1_state.from <= $t1 < r_t1_state.to')
        wheres.append('r_t2_state.from <= $t2 < r_t2_state.to')
        wheres.append('t1_state <> t2_state')

        wheres.append(
            'ALL (r IN RELATIONSHIPS(p_t1) WHERE r.from <= $t1 < r.to)'
        )
        wheres.append(
            'ALL (r in RELATIONSHIPS(p_t2) WHERE r.from <= $t2 < r.to)'
        )

        cipher = "WHERE " + ' AND '.join(wheres)
        return cipher

    def _return_clause(self):
        """Generate return clause of the query.

        Should contain the identity property of every node in the path.

        Example:
        If the path is Environment->Host

        RETURN
            environment.uuid,
            host.hostname_environment

        :returns: Return portion of the query
        :rtype: str
        """
        return 'RETURN ' + ','.join(self.selects)

    def _orderby_clause(self):
        """Build the order by clause

        Example:
        If the path is Environment->Host

        ORDER BY
            environment.uuid,
            host.hostname_environment

        :returns: Orderby clause
        :rtype: str
        """
        return 'ORDER BY ' + ','.join(self.selects)

    def __str__(self):
        """Combine all clauses into a single query.

        :returns: Combined clauses
        :rtype: str
        """
        return "\n".join([
            self._match_clause(),
            self._where_clause(),
            self._return_clause(),
            self._orderby_clause()
        ])


class Identity:
    """Models entire identity of a node."""
    def __init__(self, label, prop, identity):
        """Init the identity

        :param label: Label of the node.
        :type label: str
        :param prop: Name of the identity property of the node
        :type prop: str
        :param identity: Value of the identity property of the node
        :type identity: str
        """
        self.label = var_to_model_map.get(label, label)
        self.prop = prop
        self.value = identity

    @property
    def hash_key(self):
        """Returns a key to use for hashmaps.

        Key is a 3 tuple with literals for value, prop, and value

        :returns: Hashable tuple
        :rtype: tuple
        """
        return (self.label, self.prop, self.value)


class Node:
    """Models a node in the diff graph."""
    def __init__(self, identity, flags=None):
        """Init the node

        :param identity: Identity object for the node
        :type identity: Identity
        :param flags: Flags for the node.
            Should be a list containing any of ['t1', 't2']
            A node with only a flag of 't1' was present in t1
            A node with only a flag of 't2' was present in t2
            A node with both 't1' and 't2' was changed from t1 to t2
            A node with neither 't1' or 't2' was unmodified but is part
                of the path to a modified node.
        :type flags: List
        """
        self.identity = identity
        self.children = {}
        self.flags = set(flags or [])

    def flag(self, flags):
        """Set additional flags for the node.

        :param flags: List of additional flags.
        :type flags: list
        """
        if not isinstance(flags, list):
            flags = [flags]
        for flag in flags:
            self.flags.add(flag)

    def add_child(self, child_node):
        """Add a relationship from this node to a child node.

        :param child_node: Descendent of this node. There is a path of length
            one from this node to the child node.
        :type child_node: Node
        """
        self.children[child_node.identity.hash_key] = child_node

    def to_dict(self):
        """Creates a dictionary representation of this node.

        Representation will be serializable.

        :returns: Serializable dictionary
        :rtype: dict
        """
        return {
            'model': self.identity.label,
            'id': self.identity.value,
            'flags': list(self.flags),
            'children': [
                c.to_dict() for c in sorted(
                    self.children.values(),
                    key=lambda x: x.identity.hash_key
                )
            ]
        }


class Diff:
    """Models a graph that is a diff of two objects."""

    def add_child(self, child_node):
        """Add a child node to the diff.

        Any child added here will be a root of the diff.

        This should only occur one or zero times.

        :param child_node: Root node to add
        :type childr_node: Node
        """
        self.children[child_node.identity.hash_key] = child_node

    def feed(self, row, flags):
        """Feed one row of a diff query to the diff structure.

        Will create additional nodes and paths where they do no exist.

        :param row: Query result row
        :type row: OrderedDict
        :param flags: List of flags
        :type flags: list
        """
        if not isinstance(flags, list):
            flags = [flags]

        # Start with a pseudo node of self
        current = self

        # Only add flags to end nodes. Start counter
        count = 0

        # Iterate over each part of the row
        for label_dot_prop, value in row.items():
            count += 1
            label, prop = label_dot_prop.split('.', 1)
            identity = Identity(label, prop, value)

            # Check for existing node - create node if not existing
            node = current.children.get(identity.hash_key)
            if node is None:
                node = Node(identity)
                current.add_child(node)

            # Add flags to end node
            if count == len(row):
                node.flag(flags)
            current = node

    def to_dict(self):
        """Create serializable dictionary representation of diff structure.

        :returns: Serializable dictionary
        :rtype: dict
        """
        for node in self.children.values():
            return node.to_dict()
        else:
            return {}

    def __init__(self, model, identity, t1, t2):
        """Init the diff

        :param model: Type|Label of the root node
        :type model: str
        :param identity: Identity of the root node
        :type identity: str
        :param t1: First timestamp in milliseconds
        :type t1: int
        :param t2: Second timestamp in milliseconds
        :type t2: int
        """
        self.model = model
        self.identity = identity
        self.t1 = t1
        self.t2 = t2

        self.children = {}

        # Get list of paths
        paths = registry.forest.paths_from(self.model)
        paths.append([self.model])
        paths = sorted(paths, key=lambda x: len(x))

        for p in paths:
            q = DiffSideQuery(p, identity, (t1, t2))
            for row in q.fetch_all():
                self.feed(row, 't1')

            q = DiffSideQuery(p, identity, (t2, t1))
            for row in q.fetch_all():
                self.feed(row, 't2')

            if registry.state_properties(p[-1]):
                q = DiffStateQuery(p, identity, (t1, t2))
                for row in q.fetch_all():
                    self.feed(row, ['t1', 't2'])


class NodeDiff(Query):

    def __init__(self, model, identity, t1, t2):
        """Init the NodeDiff

        :param model: Type of the node
        :type model: str
        :param identity: Identity of the node
        :type identity: str
        :param t1: A time in milliseconds
        :type t1: int
        :param t2: A time in milliseconds
        :type t2: int
        """
        self.model = model
        self.t1 = t1
        self.t2 = t2
        self.full_path = registry.path(self.model)
        self.params = {'identity': identity}

        self.node_t1 = self.node_at_time(self.t1)
        self.node_t2 = self.node_at_time(self.t2)

    def to_list(self):
        """Create a list of serialized properties.

        :returns: List of properties. Each property is an object with:
            name, t1, and t2 where t1 and t2 are values at t1 and t2.
        :rtype: list
        """
        result_list = []

        # Gather list of all properties and then sort by property name
        props = sorted(list(
            set(self.node_t1.keys()) |
            set(self.node_t2.keys())
        ))
        for prop in props:
            result_list.append({
                'name': prop,
                't1': self.node_t1.get(prop),
                't2': self.node_t2.get(prop)
            })
        return result_list

    def node_at_time(self, t):
        """Get a node from the database at time t.

        :param t: A time in milliseconds
        :type t: int
        :returns: A dictionary of properties
        :rtype: dict
        """
        var_models = []
        rels = []
        returns = ['n']
        for model, reltype in self.full_path:
            var_models.append((model.lower(), model))
            rels.append(reltype)
        var_models.append(('n', self.model))

        if registry.state_properties(self.model):
            var_models.append(('ns', registry.models[self.model].state_label))
            rels.append('HAS_STATE')
            returns.append('ns')

        cipher = 'MATCH p = ({}:{})'.format(var_models[0][0], var_models[0][1])

        for var_model, rel in zip(var_models[1:], rels):
            var, model = var_model
            cipher += '-[:{}]->({}:{})'.format(rel, var, model)

        cipher += (
            ' WHERE ALL (r IN RELATIONSHIPS(p) WHERE r.from <= $t < r.to) AND'
        )
        cipher += (
            ' n.{} = $identity'.format(registry.identity_property(self.model))
        )
        cipher += ' RETURN ' + ','.join(returns) + ' LIMIT 1'

        self.params['t'] = t

        record = self._fetch(cipher).single()
        if record is None:
            node = {}
        else:
            node = {k: v for k, v in record['n'].items()}
            if 'ns' in record:
                for k, v in record['ns'].items():
                    node[k] = v
        return node
