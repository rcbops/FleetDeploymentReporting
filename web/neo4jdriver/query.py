import logging

from cloud_snitch.models import registry
from cloud_snitch import utils
from collections import OrderedDict

from .exceptions import InvalidLabelError
from .exceptions import InvalidPropertyError

from .connection import get_connection

logger = logging.getLogger(__name__)


def _model_state(model_name):
    return '{}_state'.format(model_name)


class Query:

    def __init__(self, label):
        """Init the query

        :param label: Name of the model, label of the node
        :type label: str
        """
        self.label = label

        # Params to be passed to neo
        self.params = {}

        self._count = None

        # List of relationship time conditions
        self.time_wheres = []

        # List of filter conditions
        self.filter_count = 0
        self.filter_wheres = []

        self.matches = []
        self.rels = []
        self.state_matches = []

        self.return_labels = []

        self.start_path()
        self.time(utils.milliseconds_now())

        # List of order by property and direction tuples
        self._orderby = []

        self._skip = None
        self._limit = None

    def time(self, timestamp):
        """Update the time parameter

        :param timestamp: New timestamp
        :type timestamp: int
        :returns: Modified self
        :rtype: Query
        """
        if timestamp is None:
            timestamp = utils.milliseconds_now()
        self.params['time'] = timestamp
        return self

    def start_path(self):
        """Create matching path of query."""
        # Find path to model
        datapath = registry.path(self.label) or []

        self.matches = []
        self.rels = []
        self.state_matches = []

        for i, pathtuple in enumerate(datapath):
            label, relname = pathtuple
            self.matches.append((
                label.lower, label, '({}:{})'.format(label.lower(), label)
            ))
            self.rels.append((
                'r{}'.format(i), relname, '-[r{}:{}]->'.format(i, relname)
            ))

            if registry.state_properties(label):
                self.state_matches.append(label)

            self.addreturn(label)

        self.matches.append((
            self.label.lower(),
            self.label,
            '({}:{})'.format(self.label.lower(), self.label)
        ))
        if registry.state_properties(self.label):
            self.state_matches.append(self.label)

        self.return_labels.append(self.label)
        return self

    def identity(self, identity):
        """Add condition to search by identity

        :param identity: Identity to search for
        :type identity: str
        :returns: Modified self
        :rtype: Query
        """
        if identity is None:
            return self

        model = registry.models[self.label]
        return self.filter(model.identity_property, '=', identity)

    def filter(self, prop, operator, value, label=None):
        """Add a filter.

        :param prop: Name of the property
        :type prop: str
        :param operator: Operator to use
        :type operator: str
        :param value: Value to filter
        :type value: str
        :param model: Optional label that has prop. Defaults to self.label
        :type model: str
        """
        if label is None:
            label = self.label

        valid_properties = registry.properties(label)
        if not valid_properties:
            raise InvalidLabelError(label)

        if prop not in registry.properties(label):
            raise InvalidPropertyError(prop, label)

        if prop in registry.state_properties(label):
            label = '{}_state'.format(label)

        condition = '{}.{} {} {}'.format(
            label.lower(),
            prop,
            operator,
            '$filterval{}'.format(self.filter_count)
        )
        self.filter_wheres.append(condition)

        self.params['filterval{}'.format(self.filter_count)] = value
        self.filter_count += 1
        return self

    def addreturn(self, label):
        """Optionally return additional labels in current label's path.

        :param label: Label in parent path
        :type label: str
        :returns: Modified self
        :rtype: Query
        """

        model = registry.models.get(label)

        # Ensure model exists
        if model is None:
            raise InvalidLabelError(label)

        # Ensure model is in parent path
        datapath = registry.path(self.label)
        if label not in ([p[0] for p in datapath]) and label != self.label:
            raise InvalidLabelError(label)

        # Add tuple to return list
        if label not in self.return_labels:
            self.return_labels.append(label)
        return self

    def orderby(self, prop, direction, label=None):
        """Add to orderby clause

        :param prop: Property to order by
        :type prop: str
        :param direction: Order direction (ASC or DESC)
        :type direction: str
        :param label: Label with the property. Defaults to target label.
            Can be target label or label in parent path
        :type label: str
        """
        # Default label to target label
        if label is None:
            label = self.label

        # Make sure label is valid
        model = registry.models.get(label)
        if model is None:
            raise InvalidLabelError(label)

        # Make sure property is valid
        if prop not in registry.properties(label):
            raise InvalidPropertyError(label, prop)

        # Check if property is part of the state of the model
        if prop in registry.state_properties(label):
            varname = '{}_state'.format(label.lower())
        else:
            varname = label.lower()

        self._orderby.append((varname, prop, direction))

    def skip(self, n):
        """Set number of records to skip.

        :param n: Number of records to skip
        :type n: int
        """
        self._skip = n

    def limit(self, n):
        """Set number of records to limit result set to

        :param n: Number of records to limit to
        :type n: int
        """
        self._limit = n

    def _match_clause(self):
        """Create match clause(s)

        :returns: MATCH clause(s)
        :rtype: str
        """
        cypher = 'MATCH '
        for i in range(len(self.rels)):
            cypher += self.matches[i][2] + self.rels[i][2]
        if not self.rels:
            cypher += self.matches[0][2]
        else:
            cypher += self.matches[len(self.rels)][2]

        for label in self.state_matches:
            cypher += ' \nMATCH ({})-[r_{}:HAS_STATE]->({}:{})'.format(
                label.lower(),
                '{}_state'.format(label.lower()),
                '{}_state'.format(label.lower()),
                registry.models[label].state_label
            )
        return cypher

    def _where_clause(self):
        """Create where clause.

        :returns: WHERE clause
        :rtype: str
        """
        cypher = ' \nWHERE '

        # Add conditions for wheres
        conditions = [] + self.filter_wheres

        # Add time conditions for path
        for relvar, relname, relstr in self.rels:
            conditions.append(
                '{}.from <= $time < {}.to'.format(relvar, relvar)
            )

        # Add time conditions for states
        for state_match in self.state_matches:
            conditions.append(
                'r_{}_state.from <= $time < r_{}_state.to'.format(
                    state_match.lower(),
                    state_match.lower()
                )
            )

        # If there are no conditions, return empty string
        if len(conditions) == 0:
            return ''

        cypher += ' AND '.join(conditions)
        return cypher

    def _return_clause(self):
        """Create return clause of query.

        :returns: Return clause of query
        :rtype: str
        """
        # Return clause
        cypher = ' \nRETURN '
        returns = []
        for label in self.return_labels:
            returns.append(label.lower())
            model = registry.models[label]
            if model.state_properties:
                returns.append('{}_state'.format(label.lower()))
        cypher += ', '.join(r for r in returns)
        return cypher

    def _orderby_clause(self):
        """Create order by clause.

        :returns: ORDER BY clause
        :rtype: str
        """
        cypher = ' \nORDER BY '

        # Default to ordering by identity property
        ob = []
        if not self._orderby:
            self.orderby(
                registry.identity_property(self.label),
                'ASC',
                label=self.label
            )
        for ob_varname, ob_prop, ob_dir in self._orderby:
            ob.append('{}.{} {}'.format(ob_varname, ob_prop, ob_dir))
        cypher += ', '.join(ob)
        return cypher

    def _skip_clause(self):
        """Create the skip clause

        :returns: SKIP clause
        :rtype: str
        """
        if self._skip is None:
            return ""
        else:
            return " \nSKIP {}".format(self._skip)

    def _limit_clause(self):
        """Create the limit clause

        :returns: LIMIT clause
        :rtype: str
        """
        if self._limit is None:
            return ""
        else:
            return " \nLIMIT {}".format(self._limit)

    def count(self):
        """Counts total number of records without skip and orderby.

        Useful for pagination.

        :returns: Total number of records in the query
        :rtype: int
        """
        if self._count is not None:
            return self._count

        query_str = \
            self._match_clause() + \
            self._where_clause() + \
            ' \nRETURN DISTINCT count(*) as total'
        resp = self._fetch(query_str)
        record = resp.single()
        self._count = record['total']
        return self._count

    def __str__(self):
        """Create the cypher query

        :returns: Cypher query string
        :rtype: str
        """
        return \
            self._match_clause() + \
            self._where_clause() + \
            self._return_clause() + \
            self._orderby_clause() + \
            self._skip_clause() + \
            self._limit_clause()

    def _fetch(self, query_str=None):
        if query_str is None:
            query_str = str(self)

        logger.debug("Running query:")
        logger.debug(query_str)

        with get_connection().session() as session:
            with session.begin_transaction() as tx:
                resp = tx.run(query_str, **self.params)
                return resp

    def fetch(self):
        resp = self._fetch(str(self))
        rows = []
        for record in resp:
            row = {}
            for label in self.return_labels:
                obj = {}
                for key, value in record[label.lower()].items():
                    obj[key] = value
                if registry.state_properties(label):
                    state_key = '{}_state'.format(label.lower())
                    for key, value in record[state_key].items():
                        obj[key] = value
                row[label] = obj
            rows.append(row)
        return rows

    def page(self, page=1, pagesize=100, index=None):
        if index is not None:
            skip = max(index - 1, 0)
        else:
            skip = (page - 1) * pagesize
        self.skip(skip)
        self.limit(pagesize)
        return self.fetch()


class ColumnQuery(Query):
    """Query for returning individual properties instead of objects."""

    def __init__(self, label):
        """Init the column query."""
        super(ColumnQuery, self).__init__(label)
        self._columns = OrderedDict()

    def add_column(self, model, prop, name=None):
        """Add a column to return.

        Verify model is in path and prop belongs to model.
        Add a column tuple. These will be used in the return clause.

        :param model: Name of the model
        :type model: str
        :param prop: Name of the property belonging to the model.
        :type prop: str
        :param name: Optional name of the column
            instead of model.prop, the column name can be custom.
            RETURN model.prop vs RETURN model.prop AS custom
        :type name: str
        """
        datapath = [p[0] for p in (registry.path(self.label) or [])]
        datapath += [self.label]

        if model not in datapath and model != self.label:
            raise InvalidLabelError(model)

        if prop not in registry.properties(model):
            raise InvalidPropertyError(prop, model)

        key = '{}.{}'.format(model, prop)

        if prop in registry.state_properties(model):
            model = _model_state(model)

        if name is not None:
            key = name

        self._columns[key] = '{}.{}'.format(model.lower(), prop)
        return self

    def _return_clause(self):
        """Create return clause of query.

        Generated from requested columns.

        :returns: Return clause of query.
        :rtype: str
        """
        cypher = '\nRETURN '

        parts = []
        for name, model_dot_prop in self._columns.items():
            part = '{} AS `{}`'.format(model_dot_prop, name)
            parts.append(part)
        cypher += ', '.join(parts)
        return cypher

    def fetch(self):
        """Execute query and return results.

        :returns: List of record rows
        :rtype: list
        """
        res = []
        for record in self._fetch(str(self)):
            r = OrderedDict()
            for k in self._columns:
                r[k] = record[k]
            res.append(r)
        return res
