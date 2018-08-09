from django.test import tag
from django.test import SimpleTestCase

from reports.serializers import model_field
from reports.serializers import property_field
from reports.serializers import time_field
from reports.serializers import ModelPropertySerializer
from reports.serializers import TimeRangeSerializer

from .base import SerializerCase


class TestTimeField(SimpleTestCase):
    """Test the time field."""
    @tag('unit')
    def test_required(self):
        """Test field when required is true."""
        f = time_field(required=True)
        self.assertTrue(f.required)
        self.assertEquals(0, f.min_value)

        f = time_field()
        self.assertTrue(f.required)
        self.assertEquals(0, f.min_value)

    @tag('unit')
    def test_optional(self):
        """Test field when required is false."""
        f = time_field(required=False)
        self.assertFalse(f.required)
        self.assertEquals(0, f.min_value)


class TestTimeRangeSerializer(SerializerCase):
    """Test time range serializer."""

    serializer_class = TimeRangeSerializer

    def setUp(self):
        self.data = {'start': 50, 'stop': 100}

    @tag('unit')
    def test_valid(self):
        """Test valid data."""
        self.assertValid()

    @tag('unit')
    def test_missing_start(self):
        """Test when data is missing start."""
        del self.data['start']
        self.assertInvalid()

    @tag('unit')
    def test_missing_stop(self):
        """Test when data is missing stop."""
        del self.data['stop']
        self.assertInvalid()

    @tag('unit')
    def test_stop_less_than_start(self):
        """Test when stop < start."""
        self.data['start'] = 100
        self.data['stop'] = 50
        self.assertInvalid()


class TestModelField(SimpleTestCase):
    """Test model field."""
    @tag('unit')
    def test_required(self):
        """Test when required is True."""
        f = model_field(required=True)
        self.assertTrue(f.required)

        f = model_field()
        self.assertTrue(f.required)

    @tag('unit')
    def test_optional(self):
        """Test when required is False."""
        f = model_field(required=False)
        self.assertFalse(f.required)


class TestPropertyField(SimpleTestCase):
    """Test property field."""
    @tag('unit')
    def test_required(self):
        """Test when required is true."""
        f = property_field(required=True)
        self.assertTrue(f.required)

        f = property_field()
        self.assertTrue(f.required)

    @tag('unit')
    def test_optional(self):
        """Test when required is False."""
        f = property_field(required=False)
        self.assertFalse(f.required)

    @tag('unit')
    def test_max_length(self):
        """Test max length."""
        f = property_field()
        self.assertEquals(f.max_length, 256)

        f = property_field(max_length=10)
        self.assertEquals(f.max_length, 10)


class TestModelPropertySerializer(SerializerCase):
    """Test model property serializer."""

    serializer_class = ModelPropertySerializer

    def setUp(self):
        self.data = {'model': 'Environment', 'prop': 'account_number'}

    @tag('unit')
    def test_valid(self):
        """Test valid data."""
        self.assertValid()

    @tag('unit')
    def test_missing_model(self):
        """Test when data is missing model."""
        del self.data['model']
        self.assertInvalid()

    @tag('unit')
    def test_missing_prop(self):
        """Test when data is missing property."""
        del self.data['prop']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_model(self):
        """Test when model is invalid."""
        self.data['model'] = 'MadeUpModel'
        self.assertInvalid()

    @tag('unit')
    def test_invalid_property(self):
        """Test when property is invalid."""
        self.data['prop'] = 'MadeUpProp'
        self.assertInvalid()
