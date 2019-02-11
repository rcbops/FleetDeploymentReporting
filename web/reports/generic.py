from collections import OrderedDict
from cloud_snitch.models import registry
from common.serializers import FilterSerializer
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ListField
from rest_framework.serializers import Serializer
from rest_framework.serializers import ValidationError

from neo4jdriver.query import ColumnQuery

from .base import BaseReport
from .serializers import ModelPropertySerializer

_models = [m.label for m in registry.models.values()]


class GenericSerializer(Serializer):

    time = IntegerField(
        min_value=0,
        required=True,
        label='Time',
        help_text='Point of time to run report.'
    )

    model = ChoiceField(
        _models,
        label="Model",
        default='Environment',
        help_text=(
            "Please select an end model to pull from. You can create columns "
            "from any model in the path to this model."
        )
    )

    columns = ListField(
        child=ModelPropertySerializer(),
        min_length=1,
        label='Columns',
        help_text='Please choose each column to be listed in the report.'
    )

    filters = ListField(
        child=FilterSerializer(),
        label="Filters",
        help_text="Additional filter criteria.",
        required=False
    )

    def validate(self, data):
        """Custom validation.

        Ensure that all columns are properties to models in the path
        to the chosen model.

        Ensure that all filters are on properties to models in the path
        to the chosen model.

        :param data: Data to validate
        :type data: dict
        """
        model_set = set([t[0] for t in registry.path(data['model'])])
        model_set.add(data['model'])

        column_errors = OrderedDict()
        for i, c in enumerate(data.get('columns', [])):
            if c['model'] not in model_set:
                column_errors[i] = (
                    'Model {} is not in path of {}'
                    .format(c['model'], data['model'])
                )
        if column_errors:
            raise ValidationError({'columns': column_errors})

        filter_errors = OrderedDict()
        for i, f in enumerate(data.get('filters', [])):
            if f['model'] not in model_set:
                filter_errors[i] = (
                    'Model {} not in path of {}'
                    .format(f['model'], data['model'])
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
                'name': 'model',
                'label': self.fields['model'].label,
                'help_text': self.fields['model'].help_text,
                'required': self.fields['model'].required,
                'default': self.fields['model'].default,
                'component': 'Model'
            },
            {
                'name': 'columns',
                'label': self.fields['columns'].label,
                'help_text': self.fields['columns'].help_text,
                'min_length': self.fields['columns'].min_length,
                'component': 'ModelProperty',
                'many': True,
                'watches': 'model'
            },
            {
                'name': 'filters',
                'label': self.fields['filters'].label,
                'help_text': self.fields['filters'].help_text,
                'component': 'Filter',
                'many': True,
                'watches': 'model'
            }
        ]


class GenericReport(BaseReport):

    name = "Generic"

    description = "Simple one property per column report."

    serializer_class = GenericSerializer

    def build_query(self):
        """Builds and returns query for the report without paging.

        :returns: Query object
        :rtype: ColumnQuery
        """
        q = ColumnQuery(self.data['model'])
        q.time(self.data['time'])
        for column in self.data['columns']:
            q.add_column(column['model'], column['prop'])
            q.orderby(column['prop'], 'ASC', label=column['model'])
        for f in self.data.get('filters', []):
            q.filter(f['prop'], f['operator'], f['value'], label=f['model'])
        return q

    def run(self):
        """Run the report and return results.

        :returns: The report data
        :rtype: list
        """
        q = self.build_query()
        rows = []
        pagesize = 5000
        page = 1
        page_rows = q.page(page, pagesize)
        while(page_rows):
            rows += page_rows
            page += 1
            page_rows = q.page(page, pagesize)

        return rows

    def columns(self):
        """Gets columns for this report. useful for csv serialization.

        :returns: Compute list of columns
        :rtype: list
        """
        cols = []
        for c in self.data['columns']:
            cols.append('{}.{}'.format(c['model'], c['prop']))
        return cols
