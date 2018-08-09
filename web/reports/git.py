from rest_framework.serializers import ChoiceField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import Serializer

from neo4jdriver.query import ColumnQuery

from .base import BaseReport


class GitSerializer(Serializer):

    time = IntegerField(
        min_value=0,
        required=True,
        label='Time',
        help_text='Point of time to run report.'
    )

    url = ChoiceField(
        [],
        label='Git URL',
        default='https://git.openstack.org/openstack/openstack-ansible',
        help_text='Please select a git url.'
    )

    def __init__(self, *args, **kwargs):
        """Init the serializer with updated list of git urls."""
        self.fields['url'].choices = self.git_urls()
        super(GitSerializer, self).__init__(*args, **kwargs)

    def git_urls(self):
        """Build list of selectable git urls.

        :returns: All git urls
        :rtype: list
        """
        q = ColumnQuery('GitUrl')
        q.add_column('GitUrl', 'url', 'url')
        q.orderby('url', 'ASC', label='GitUrl')
        urls = []

        page = 1
        pagesize = 1000
        page_rows = q.page(page, pagesize)
        while(page_rows):
            for row in page_rows:
                urls.append(row['url'])
            page += 1
            page_rows = q.page(page, pagesize)
        return urls

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
                'name': 'url',
                'label': self.fields['url'].label,
                'help_text': self.fields['url'].help_text,
                'required': self.fields['url'].required,
                'default': self.fields['url'].default,
                'component': 'Select',
                'choices': self.fields['url'].choices
            },
        ]


class GitReport(BaseReport):

    name = "Git"

    description = "List merge base and paths for selected git url."

    serializer_class = GitSerializer

    _columns = [
        {'model': 'Environment', 'prop': 'name'},
        {'model': 'Environment', 'prop': 'account_number'},
        {'model': 'GitRepo', 'prop': 'path'},
        {'model': 'GitRepo', 'prop': 'merge_base_name'},
        {'model': 'GitUrl', 'prop': 'url'}
    ]

    def run(self):

        q = ColumnQuery('GitUrl')
        q.time(self.data['time'])
        for column in self._columns:
            q.add_column(column['model'], column['prop'])
            q.orderby(column['prop'], 'ASC', label=column['model'])
        q.filter('url', '=', self.data['url'], label='GitUrl')

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
        for c in self._columns:
            cols.append('{}.{}'.format(c['model'], c['prop']))
        return cols
