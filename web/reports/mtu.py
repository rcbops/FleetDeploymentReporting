from collections import OrderedDict
from rest_framework.serializers import IntegerField
from rest_framework.serializers import Serializer

from neo4jdriver.query import Query
from .base import BaseReport


class MTUQuery(Query):
    """Class for multipath mtu query."""

    columns = [
        'Account Name',
        'Account Number',
        'Hostname',
        'Device',
        'Running MTU',
        'Configured MTU',
        'Same MTU',
        'Is Running MTU Default',
        'Is Configured MTU Default'
    ]

    def __init__(self, time, default=1500):
        """Init the query.

        :param time: time in milliseconds since epoch.
        :type time: int
        :param default: The default mtu.
        :type default: int
        """
        self.params = {
            'time': time,
            'default': default
        }
        self._skip = None
        self._limit = None
        self._count = None

    def _match_clause(self):
        """Create the match clause of the query.

        :returns: Cipher string containing match clause.
        :rtype: str
        """
        cipher = (
            "MATCH "
            "\n\t(e:Environment)-[r_host:HAS_HOST]->(h:Host)"
            "\nMATCH "
            "\n\t(h)-[r_i:HAS_INTERFACE]->(i:Interface)"
            "-[r_is:HAS_STATE]->(is:InterfaceState)"
            "\nMATCH"
            "\n\t(h)-[r_ci]->(ci:ConfiguredInterface)"
            "-[r_cis:HAS_STATE]"
            "->(cis:ConfiguredInterfaceState)"
        )
        return cipher

    def _where_clause(self):
        """Create the where clause of the query.

        :returns: Cipher string containing where clause.
        :rtype: str
        """
        cipher = (
            "\nWHERE"
            "\n\ti.device = ci.device AND"
            "\n\t("
            "\n\t\t(toInteger(is.mtu) <> toInteger(cis.mtu)) OR "
            "\n\t\t(toInteger(is.mtu) <> $default AND cis.mtu IS NULL)"
            "\n\t) AND"
            "\n\tr_host.from <= $time < r_host.to AND"
            "\n\tr_i.from <= $time < r_i.to AND"
            "\n\tr_is.from <= $time < r_is.to AND"
            "\n\tr_ci.from <= $time < r_ci.to AND"
            "\n\tr_cis.from <= $time < r_cis.to"
        )
        return cipher

    def _return_clause(self):
        """Create the return clause of the query.

        :returns: Cipher string containing return clause.
        :rtype: str
        """
        cipher = (
            "\nRETURN"
            "\n\te.name as `Account Name`,"
            "\n\te.account_number as `Account Number`,"
            "\n\th.hostname as `Hostname`,"
            "\n\ti.device as `Device`,"
            "\n\ttoInteger(is.mtu) as `Running MTU`,"
            "\n\ttoInteger(cis.mtu) as `Configured MTU`,"
            "\n\ttoInteger(is.mtu) = toInteger(cis.mtu) as `Same MTU`,"
            "\n\ttoInteger(is.mtu) = $default as  `Is Running MTU Default`,"
            "\n\ttoInteger(cis.mtu) = $default as `Is Configured MTU Default`"
        )
        return cipher

    def _orderby_clause(self):
        """Create the order by clause of the query.

        :returns: Cipher string containing the orderby clause.
        :rtype: str
        """
        cipher = (
            "\nORDER BY"
            "\n\t`Account Name` ASC,"
            "\n\t`Account Number` ASC,"
            "\n\t`Hostname` ASC,"
            "\n\t`Device` ASC"
        )
        return cipher

    def fetch(self):
        """Execute query and return results.

        :returns: List of record rows
        :rtype: list
        """
        res = []
        for record in self._fetch(str(self)):
            r = OrderedDict()
            for k in self.columns:
                r[k] = record[k]
            res.append(r)
        return res


class MTUSerializer(Serializer):
    """Serializer for the MTUReport input parameters."""
    time = IntegerField(
        min_value=0,
        required=True,
        label='Time',
        help_text='Point of time to run report.'
    )

    def form_data(self):
        """Describes web client form associated with this serializer.

        :returns: List of dict objects
        :rtype: list
        """
        return [
            {
                'name': 'time',
                'label': self.fields['time'].label,
                'help_text': self.fields['time'].help_text,
                'required': self.fields['time'].required,
                'component': 'Time',
                'many': False
            }
        ]


class MTUReport(BaseReport):
    """Report on mtu differences on interfaces."""

    name = 'MTU'

    description = (
        'Discover cases where running mtu is different from configured '
        'mtu and instances where mtus are not 1500.'
    )

    serializer_class = MTUSerializer

    _columns = MTUQuery.columns

    _boolean_columns = [
        'Same MTU',
        'Is Running MTU Default',
        'Is Configured MTU Default'
    ]

    def clean_row(self, row):
        """Fix boolean columns resulting from null comparisons.

        Null comparisons in neo4j always result in null. This function
        looks at boolean fields and changes null to false.

        :returns: Cleaned row
        :rtype: dict
        """
        for col in self._boolean_columns:
            if row[col] is None:
                row[col] = False
        return row

    def run(self):
        """Build the query and run the report."""
        q = MTUQuery(self.data['time'], default=1500)
        rows = []
        pagesize = 5000
        page = 1
        page_rows = q.page(page, pagesize)
        while(page_rows):
            for row in page_rows:
                rows.append(self.clean_row(row))
            page += 1
            page_rows = q.page(page, pagesize)
        return rows

    def columns(self):
        """Get columns for this report.

        :returns: List of columns
        :rtype: list
        """
        return self._columns
