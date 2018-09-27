import mock
import unittest

from cloud_snitch.exc import ConversionError
from cloud_snitch.exc import ModelNotFoundError
from cloud_snitch.exc import PropertyNotFoundError

from cloud_snitch.models.base import VersionedProperty
from cloud_snitch.models.utils import prep_val
from cloud_snitch.models.utils import string_to_bool


class TestStringToBool(unittest.TestCase):
    def test_empty_string(self):
        """Test that the empty string returns False."""
        self.assertFalse(string_to_bool(''))

    def test_non_standard_text(self):
        """Test that unexpected strings are True."""
        self.assertTrue(string_to_bool('anythingelse'))

    def test_trues(self):
        """Test that true, TRUE, yes, YES are true."""
        self.assertTrue(string_to_bool('true'))
        self.assertTrue(string_to_bool('TRUE'))
        self.assertTrue(string_to_bool('yes'))
        self.assertTrue(string_to_bool('YES'))

    def test_falses(self):
        """Test that false, FALSE, no, No are false."""
        self.assertFalse(string_to_bool('false'))
        self.assertFalse(string_to_bool('FALSE'))
        self.assertFalse(string_to_bool('no'))
        self.assertFalse(string_to_bool('NO'))


class TestPrepVal(unittest.TestCase):

    def test_invalid_model(self):
        """Test that ModelNotFoundError is raised."""
        # Test with raise_for_error=True
        with self.assertRaises(ModelNotFoundError):
            prep_val('m', 'p', 'somevalue', raise_for_error=True)

        # Test without raise_for_error(should still raise for this error.)
        with self.assertRaises(ModelNotFoundError):
            prep_val('m', 'p', 'somevalue', raise_for_error=False)

    @mock.patch('cloud_snitch.models.utils.registry')
    def test_invalid_property(self, m_registry):
        """Test that PropertyNotFoundError is raised."""
        m_model = mock.Mock()
        m_model.properties = {
            'test_prop': VersionedProperty(is_static=True, type=int)
        }

        m_registry.models = mock.MagicMock()
        m_registry.models.get = mock.Mock(return_value=m_model)

        # Test with raise for error
        with self.assertRaises(PropertyNotFoundError):
            prep_val('m', 'p', 42, raise_for_error=True)

        # Test without raise for error(should still raise for this error.)
        with self.assertRaises(PropertyNotFoundError):
            prep_val('m', 'p', 42, raise_for_error=False)

    @mock.patch('cloud_snitch.models.utils.registry')
    def test_conversion_error(self, m_registry):
        """Test that PropertyNotFoundError is raised."""
        m_model = mock.Mock()
        m_model.properties = {
            'test_prop': VersionedProperty(is_static=True, type=int)
        }
        m_registry.models = mock.MagicMock()
        m_registry.models.get = mock.Mock(return_value=m_model)

        # Try converting incompatible string to int with raise_for_error
        with self.assertRaises(ConversionError):
            prep_val('m', 'test_prop', '42x', raise_for_error=True)

        # Try converting incompatible string to int without raise_for_error
        new_val = prep_val('m', 'test_prop', '42x', raise_for_error=False)
        self.assertEqual(new_val, '42x')

    @mock.patch('cloud_snitch.models.utils.registry')
    def test_string_to_types(self, m_registry):
        m_model = mock.Mock()
        m_model.properties = {
            'test_int': VersionedProperty(is_static=True, type=int),
            'test_float': VersionedProperty(is_static=True, type=float),
            'test_str': VersionedProperty(is_static=True, type=str)
        }
        m_registry.models = mock.MagicMock()
        m_registry.models.get = mock.Mock(return_value=m_model)

        # Test valid int
        new_val = prep_val('m', 'test_int', '42')
        self.assertEqual(new_val, 42)
        self.assertTrue(isinstance(new_val, int))

        # Test valid float
        new_val = prep_val('m', 'test_float', '0.42')
        self.assertEqual(new_val, 0.42)
        self.assertTrue(isinstance(new_val, float))

        # Test valid string
        new_val = prep_val('m', 'test_str', 'somestr')
        self.assertEqual(new_val, 'somestr')
        self.assertTrue(isinstance(new_val, str))

    @mock.patch('cloud_snitch.models.utils.registry')
    def test_string_to_bool(self, m_registry):
        m_model = mock.Mock()
        m_model.properties = {
            'test_bool': VersionedProperty(is_static=True, type=bool)
        }
        m_registry.models = mock.MagicMock()
        m_registry.models.get = mock.Mock(return_value=m_model)

        # Test false
        self.assertFalse(prep_val('m', 'test_bool', 'false'))
        self.assertFalse(prep_val('m', 'test_bool', 'FALSE'))
        self.assertFalse(prep_val('m', 'test_bool', 'no'))
        self.assertFalse(prep_val('m', 'test_bool', 'NO'))

        # Test true
        self.assertTrue(prep_val('m', 'test_bool', 'true'))
        self.assertTrue(prep_val('m', 'test_bool', 'TRUE'))
        self.assertTrue(prep_val('m', 'test_bool', 'yes'))
        self.assertTrue(prep_val('m', 'test_bool', 'YES'))
