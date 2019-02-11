import configparser
import logging

from collections import OrderedDict
from common.serializers import FilterSerializer
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ListField
from rest_framework.serializers import Serializer
from rest_framework.serializers import ValidationError

from neo4jdriver.query import ColumnQuery

from .base import BaseReport

logger = logging.getLogger(__name__)

FILTERABLE_MODELS = ['Environment', 'Host', 'Configfile']


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

    filters = ListField(
        child=FilterSerializer(),
        label="Filters",
        help_text="Additional filter criteria.",
        required=False
    )

    def validate(self, data):
        """Custom validation.

        Ensure filters are acting upon a filterable model.

        :param data: Data to validate
        :type data: dict
        :returns: Validated data
        :rtype: dict
        """
        model_set = set(FILTERABLE_MODELS)
        filter_errors = OrderedDict()
        for i, f in enumerate(data.get('filters', [])):
            if f['model'] not in model_set:
                filter_errors[i] = (
                    'Model {} is not one of [{}].'
                    .format(f['model'], ', '.join(FILTERABLE_MODELS))
                )
        if filter_errors:
            raise ValidationError({'filters': filter_errors})
        return data

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
            },
            {
                'name': 'filters',
                'label': self.fields['filters'].label,
                'help_text': self.fields['filters'].help_text,
                'component': 'Filter',
                'many': True,
                'models': FILTERABLE_MODELS
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

    def build_query(self):
        """Build query for the report.

        :returns: Query object
        :rtype: ColumnQuery
        """
        q = ColumnQuery('Configfile')
        q.time(self.data['time'])
        for column in self._db_columns:
            q.add_column(column['model'], column['prop'])
            q.orderby(column['prop'], 'ASC', label=column['model'])
        q.filter('name', '=', 'cinder.conf', label='Configfile')
        for f in self.data.get('filters', []):
            q.filter(f['prop'], f['operator'], f['value'], label=f['model'])
        return q

    def run(self):
        """Run the report.

        :returns: List of report rows
        :rtype: List of ordereddicts
        """
        q = self.build_query()
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
