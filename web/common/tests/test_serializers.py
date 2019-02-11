import logging

from django.test import tag
from common.serializers import FilterSerializer
from common.serializers import OrderSerializer
from common.tests.base import SerializerCase

logging.getLogger('api').setLevel(logging.ERROR)


class TestFilterSerializer(SerializerCase):

    serializer_class = FilterSerializer

    def setUp(self):
        self.data = {
            'model': 'Environment',
            'prop': ' account_number',
            'operator': '=',
            'value': 'test_val'
        }

    @tag('unit')
    def test_valid(self):
        self.assertValid()

    @tag('unit')
    def test_invalid_model(self):
        self.data['model'] = 'somerandommodel'
        self.assertInvalid()

    @tag('unit')
    def test_missing_model(self):
        del self.data['model']
        self.assertInvalid()

    @tag('unit')
    def test_property_too_long(self):
        self.data['prop'] = 't' * 300
        self.assertInvalid()

    @tag('unit')
    def test_property_missing(self):
        del self.data['prop']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_property(self):
        self.data['prop'] = 'somerandomproperty'
        self.assertInvalid()

    @tag('unit')
    def test_invalid_operator(self):
        self.data['operator'] = 'abc'
        self.assertInvalid()

    @tag('unit')
    def test_missing_operator(self):
        del self.data['operator']
        self.assertInvalid()

    @tag('unit')
    def test_value_too_long(self):
        self.data['value'] = 't' * 257
        self.assertInvalid()

    @tag('unit')
    def test_missing_value(self):
        del self.data['value']
        self.assertInvalid()


class TestOrderSerializer(SerializerCase):

    serializer_class = OrderSerializer

    def setUp(self):
        self.data = {
            'model': 'Environment',
            'prop': 'account_number',
            'direction': 'asc'
        }

    @tag('unit')
    def test_valid(self):
        self.assertValid()

    @tag('unit')
    def test_invalid_model(self):
        self.data['model'] = 'somerandommodel'
        self.assertInvalid()

    @tag('unit')
    def test_missing_model(self):
        del self.data['model']
        self.assertInvalid()

    @tag('unit')
    def test_non_slug_prop(self):
        self.data['prop'] = '    a      b '
        self.assertInvalid()

    @tag('unit')
    def test_invalid_prop(self):
        self.data['prop'] = 'somerandomprop'
        self.assertInvalid()

    @tag('unit')
    def test_missing_prop(self):
        del self.data['prop']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_direction(self):
        self.data['direction'] = 'dasc'
        self.assertInvalid()

    @tag('unit')
    def test_missing_direction(self):
        del self.data['direction']
        self.assertInvalid()
