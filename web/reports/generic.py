from cloud_snitch.models import registry
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ListField
from rest_framework.serializers import Serializer

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
            }
        ]


class GenericReport(BaseReport):

    name = "Generic"

    description = "Simple one property per column report."

    serializer_class = GenericSerializer

    def run(self):

        q = ColumnQuery(self.data['model'])
        q.time(self.data['time'])
        for column in self.data['columns']:
            q.add_column(column['model'], column['prop'])
            q.orderby(column['prop'], 'ASC', label=column['model'])

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
