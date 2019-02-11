import logging
import mock

from django.test import tag, TestCase

from api.serializers import DiffSerializer
from api.serializers import FilterSerializer
from api.serializers import GenericSerializer
from api.serializers import ModelSerializer
from api.serializers import PropertySerializer
from api.serializers import SearchSerializer
from api.serializers import TimesChangedSerializer

from cloud_snitch.models.base import VersionedEntity
from cloud_snitch.models.base import VersionedProperty
from cloud_snitch.models.base import versioned_properties

from common.tests.base import SerializerCase

logging.getLogger('api').setLevel(logging.ERROR)


@versioned_properties
class TestChildEntity(VersionedEntity):
    """Simple child entity for testing the model serializer."""
    label = "TestChildEntity"
    state_label = 'TestChildEntityState'
    properties = {
        'identity': VersionedProperty(is_identity=True, type=str)
    }


@versioned_properties
class TestEntity(VersionedEntity):
    """Simple entity for testing the model serializer."""
    label = 'TestEntity'
    state_label = 'TestEntityState'
    properties = {
        'identity': VersionedProperty(is_identity=True, type=str),
        'static1': VersionedProperty(is_static=True, type=int),
        'state1': VersionedProperty(is_state=True, type=float)
    }
    children = {
        'children': ('HAS_CHILD', TestChildEntity)
    }


class TestModelSerializer(TestCase):

    @tag('unit')
    @mock.patch('api.serializers.registry.properties')
    def test_serialize_single(self, m_properties):
        m_properties.return_value = ['identity', 'state1', 'static1']

        s = ModelSerializer(TestEntity)

        self.assertEqual(s.data['label'], 'TestEntity')
        self.assertEqual(s.data['state_label'], 'TestEntityState')

        # Test properties
        expected_properties = {
            'identity': {'type': 'str'},
            'static1': {'type': 'int'},
            'state1': {'type': 'float'}
        }
        for prop_name, prop_dict in expected_properties.items():
            self.assertEqual(
                s.data['properties'][prop_name]['type'],
                prop_dict['type']
            )

        # Test relationships.
        expected_children = {
            'children': {
                'rel_name': 'HAS_CHILD', 'label': 'TestChildEntity'
            }
        }
        for name, child_dict in expected_children.items():
            self.assertEqual(
                s.data['children'][name]['rel_name'],
                child_dict['rel_name']
            )
            self.assertEqual(
                s.data['children'][name]['label'],
                child_dict['label']
            )


class TestGenericSerializer(TestCase):

    @tag('unit')
    def test_serialize_single(self):
        test_obj = {'somekey': 'someval'}
        s = GenericSerializer(test_obj)
        data = s.data
        self.assertTrue(data is test_obj)

    @tag('unit')
    def test_serialize_many(self):
        test_objs = [
            {'somekey1': 'someval1'},
            {'somekey2': 'someval2'}
        ]
        data = GenericSerializer(test_objs, many=True).data
        for i, obj in enumerate(test_objs):
            self.assertTrue(obj is data[i])


class TestPropertySerializer(TestCase):

    @tag('unit')
    def test_serialize_single(self):
        props = ['prop1', 'prop2', 'prop3']
        data = PropertySerializer(props).data
        self.assertTrue(props is data['properties'])


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


class TestSearchSerializer(SerializerCase):

    serializer_class = SearchSerializer

    def setUp(self):
        self.data = {
            'model': 'Environment',
            'time': 1,
            'identity': 'someid',
            'filters': [{
                'model': 'Environment',
                'prop': 'account_number',
                'operator': '=',
                'value': 'someval'
            }],
            'orders': [{
                'model': 'Environment',
                'prop': 'account_number',
                'direction': 'asc'
            }],
            'page': 2,
            'pagesize': 10,
            'index': 15
        }

    @tag('unit')
    def test_valid(self):
        self.assertValid()

    @tag('unit')
    def test_missing_model(self):
        del self.data['model']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_model(self):
        self.data['model'] = 'somerandommodel'
        self.assertInvalid()

    @tag('unit')
    def test_negative_time(self):
        self.data['time'] = -1
        self.assertInvalid()

    @tag('unit')
    def test_missing_time(self):
        """Test time not provided. Should be valid."""
        del self.data['time']
        self.assertValid()

    @tag('unit')
    def test_identity_too_long(self):
        self.data['identity'] = 't' * 257
        self.assertInvalid()

    @tag('unit')
    def test_missing_identity(self):
        """Test identity not provided. Should be valid."""
        del self.data['identity']
        self.assertValid()

    @tag('unit')
    def test_missing_filters(self):
        """Test without filters. Should be valid."""
        del self.data['filters']
        self.assertValid()

    @tag('unit')
    def test_nonlist_filters(self):
        self.data['filters'] = 'afilter'
        self.assertInvalid()

    @tag('unit')
    def test_emptylist_filters(self):
        self.data['filters'] = []
        self.assertValid()

    @tag('unit')
    def test_filters_with_invalid_prop(self):
        self.data['filters'] = [{
            'model': 'Environment',
            'prop': 'somerandomprop',
            'operator': '=',
            'value': 'someval'
        }]
        self.assertInvalid()

    @tag('unit')
    def test_missing_orders(self):
        del self.data['orders']
        self.assertValid()

    @tag('unit')
    def test_emptylist_orders(self):
        self.data['orders'] = []
        self.assertValid()

    @tag('unit')
    def test_nonlist_orders(self):
        self.data['orders'] = 'anorder'
        self.assertInvalid()

    @tag('unit')
    def test_orders_with_invalid_prop(self):
        self.data['orders'] = [{
            'model': 'Environment',
            'prop': 'somerandomprop',
            'order': 'asc'
        }]
        self.assertInvalid()

    @tag('unit')
    def test_missing_page(self):
        del self.data['page']
        self.assertValid()
        self.assertEquals(self.serializer.validated_data['page'], 1)

    @tag('unit')
    def test_invalid_page(self):
        self.data['page'] = -1
        self.assertInvalid()

    @tag('unit')
    def test_missing_pagesize(self):
        del self.data['pagesize']
        self.assertValid()
        self.assertEquals(self.serializer.validated_data['pagesize'], 500)

    @tag('unit')
    def test_missing_index(self):
        del self.data['index']
        self.assertValid()

    @tag('unit')
    def test_invalid_index(self):
        self.data['index'] = -1
        self.assertInvalid()


class TestTimesChangedSerializer(SerializerCase):

    serializer_class = TimesChangedSerializer

    def setUp(self):
        self.data = {
            'model': 'Environment',
            'identity': 'someid',
            'time': 1
        }

    @tag('unit')
    def test_valid(self):
        self.assertValid()

    @tag('unit')
    def test_missing_model(self):
        del self.data['model']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_model(self):
        self.data['model'] = 'somerandommodel'
        self.assertInvalid()

    @tag('unit')
    def test_missing_identity(self):
        del self.data['identity']
        self.assertInvalid()

    @tag('unit')
    def test_identity_too_long(self):
        self.data['identity'] = 't' * 257
        self.assertInvalid()

    @tag('unit')
    def test_missing_time(self):
        del self.data['time']
        self.assertValid()

    @tag('unit')
    def test_invalid_time(self):
        self.data['time'] = -1
        self.assertInvalid()


class TestDiffSerializer(SerializerCase):

    serializer_class = DiffSerializer

    def setUp(self):
        self.data = {
            'model': 'Environment',
            'identity': 'someid',
            'left_time': 10,
            'right_time': 20
        }

    @tag('unit')
    def test_valid(self):
        self.assertValid()

    @tag('unit')
    def test_missing_model(self):
        del self.data['model']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_model(self):
        self.data['model'] = 'somerandommodel'
        self.assertInvalid()

    @tag('unit')
    def test_missing_identity(self):
        del self.data['identity']
        self.assertInvalid()

    @tag('unit')
    def test_identity_too_long(self):
        self.data['identity'] = 't' * 257
        self.assertInvalid()

    @tag('unit')
    def test_missing_left_time(self):
        del self.data['left_time']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_left_time(self):
        self.data['left_time'] = -1
        self.assertInvalid()

    @tag('unit')
    def test_missing_right_time(self):
        del self.data['right_time']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_right_time(self):
        self.data['right_time'] = -1
        self.assertInvalid()
