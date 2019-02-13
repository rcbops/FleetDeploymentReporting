from common.tests.base import SerializerCase
from django.test import tag
from django.test import SimpleTestCase
from reports.generic import GenericReport
from reports.generic import GenericSerializer


class TestGenericSerializer(SerializerCase):
    """Test cases for Generic report serializer."""

    serializer_class = GenericSerializer

    def setUp(self):
        """Set up base data to pass to serializer.

        Each case should modify this test a specific condition.
        """
        self.data = {
            'time': 1,
            'model': 'Environment',
            'columns': [
                {
                    'model': 'Environment',
                    'prop': 'account_number'
                }
            ],
            'filters': [
                {
                    'model': 'Environment',
                    'prop': 'name',
                    'operator': 'CONTAINS',
                    'value': 'james'
                }
            ]
        }

    @tag('unit')
    def test_valid(self):
        """Test that the base set of data is valid."""
        self.assertValid()

    @tag('unit')
    def test_missing_time(self):
        """Test that time is required."""
        del self.data['time']
        self.assertInvalid()

    @tag('unit')
    def test_non_integer_time(self):
        """Test that time must be an integer."""
        self.data['time'] = ' atring'
        self.assertInvalid()

    @tag('unit')
    def test_default_model(self):
        """Test that model defaults to 'Environment'"""
        del self.data['model']
        self.assertValid()
        self.assertEquals(
            self.serializer.validated_data['model'],
            'Environment'
        )

    @tag('unit')
    def test_invalid_model(self):
        """Test a model selection not in the registry of models."""
        self.data['model'] = 'notamodel'
        self.assertInvalid()

    @tag('unit')
    def test_no_columns(self):
        """Test missing columns and an empty column list."""
        # Test missing columns
        del self.data['columns']
        self.assertInvalid()

        # Test empty column list
        self.data['columns'] = []
        self.assertInvalid()

    @tag('unit')
    def test_column_missing_parts(self):
        self.data['columns'][0] = {'prop': 'someprop'}
        self.assertInvalid()

        self.data['columns'][0] = {'model': 'Environment'}
        self.assertInvalid()

    @tag('unit')
    def test_column_invalid_model(self):
        self.data['columns'][0] = {
            'model': 'notadmodel',
            'prop': 'aprop'
        }
        self.assertInvalid()

        self.data['columns'][0] = {
            'model': 'Environment',
            'prop': 'notaprop'
        }
        self.assertInvalid()

    @tag('unit')
    def test_column_model_not_in_path(self):
        self.data['columns'][0] = {
            'model': 'Host',
            'prop': 'hostname'
        }
        self.assertInvalid()

    @tag('unit')
    def test_no_filters(self):
        self.data['filters'] = []
        self.assertValid()

    @tag('unit')
    def test_invalid_filter_operator(self):
        self.data['filters'][0]['operator'] = 'notanop'
        self.assertInvalid()

    @tag('unit')
    def test_invalid_filter_property(self):
        self.data['filters'][0]['prop'] = 'notaprop'
        self.assertInvalid()

    @tag('unit')
    def test_filter_model_not_in_path(self):
        self.data['filters'][0]['model'] = 'PythonPackage'
        self.data['filters'][0]['prop'] = 'name'
        self.assertInvalid()


class TestGenericReport(SimpleTestCase):
    """Test the generic report

    @TODO - Need to mock column query and determine that the query
    is built correctly.
    """

    def setUp(self):
        self.params = {
            'time': 1,
            'model': 'Environment',
            'columns': [
                {
                    'model': 'Environment',
                    'prop': 'name',
                },
                {
                    'model': 'Environment',
                    'prop': 'account_number',
                }
            ],
            'filters': [
                {
                    'model': 'Environment',
                    'prop': 'name',
                    'operator': 'CONTAINS',
                    'value': 'james'
                }
            ]
        }

    @tag('unit')
    def test_columns(self):
        """Test columns from parameters"""
        r = GenericReport(self.params)
        cols = r.columns()
        self.assertEquals(cols[0], 'Environment.name')
        self.assertEquals(cols[1], 'Environment.account_number')

    @tag('unit')
    def test_filters(self):
        """Test that filters affect query."""
        r = GenericReport(self.params)
        q_str = str(r.build_query())
        self.assertTrue('environment.name CONTAINS $filterval0' in q_str)
