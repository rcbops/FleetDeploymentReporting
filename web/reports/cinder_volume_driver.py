import configparser
import logging

from collections import OrderedDict
from rest_framework.serializers import IntegerField
from rest_framework.serializers import Serializer

from neo4jdriver.query import ColumnQuery

from .base import BaseReport

logger = logging.getLogger(__name__)


def parse_contents(contents):
    """Parse contents of a cinder.conf ini file.

    :param contents: Contents of a cinder.conf file
    :type contents: str
    :returns: Sorted list of (section, volume driver) tuples
    :rtype: list
    """
    p = configparser.ConfigParser()
    tuples = []

    p.read_string(contents)
    for section in p.sections():
        if 'volume_driver' in p[section]:
            tuples.append((section.lower(), p[section]['volume_driver']))
    return sorted(tuples)


class VolumeDriverSerializer(Serializer):
    """Serializer for volume driver report."""

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


class CinderVolumeDriverReport(BaseReport):

    name = "CinderVolumeDriver"

    description = "List volume drivers located in cinder.conf."

    serializer_class = VolumeDriverSerializer

    _db_columns = [
        {'model': 'Environment', 'prop': 'name'},
        {'model': 'Environment', 'prop': 'account_number'},
        {'model': 'Host', 'prop': 'hostname'},
        {'model': 'Configfile', 'prop': 'name'},
        {'model': 'Configfile', 'prop': 'contents'}
    ]

    _output_columns = [
        {'model': 'Environment', 'prop': 'name'},
        {'model': 'Environment', 'prop': 'account_number'},
        {'model': 'Host', 'prop': 'hostname'},
        {'model': 'Configfile', 'prop': 'name'},
    ]

    def _record_from_row(self, row, section, driver):
        """Create a result record from row, section, and driver.
        """
        d = OrderedDict()
        for column in self._output_columns:
            key = '{}.{}'.format(column['model'], column['prop'])
            d[key] = row[key]
        d['section'] = section
        d['driver'] = driver
        return d

    def run(self):
        """Run the report.

        :returns: List of report rows
        :rtype: List of ordereddicts
        """
        q = ColumnQuery('Configfile')
        q.time(self.data['time'])
        for column in self._db_columns:
            q.add_column(column['model'], column['prop'])
            q.orderby(column['prop'], 'ASC', label=column['model'])
        q.filter('name', '=', 'cinder.conf', label='Configfile')

        records = []
        pagesize = 500
        page = 1
        page_rows = q.page(page, pagesize)
        while(page_rows):
            for row in page_rows:
                for s, d in parse_contents(row['Configfile.contents']):
                    records.append(self._record_from_row(row, s, d))
            page += 1
            page_rows = q.page(page, pagesize)

        return records

    def columns(self):
        """Gets columns for this report. useful for csv serialization.

        :returns: Compute list of columns
        :rtype: list
        """
        cols = []
        for c in self._output_columns:
            cols.append('{}.{}'.format(c['model'], c['prop']))
        cols.append('section')
        cols.append('driver')
        return cols
