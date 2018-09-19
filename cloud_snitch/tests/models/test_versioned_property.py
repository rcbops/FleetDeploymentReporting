import unittest

from cloud_snitch.models.base import VersionedProperty


class TestVersionedProperty(unittest.TestCase):

    def test_default(self):
        """Test default values with no kwargs."""
        prop = VersionedProperty()
        self.assertTrue(prop.type is str)
        self.assertTrue(prop.concat_properties is None)
        self.assertFalse(prop.is_concat)
        self.assertFalse(prop.is_static)
        self.assertFalse(prop.is_state)
        self.assertFalse(prop.is_identity)

    def test_static_state_and_identity(self):
        """Test that property is invalid when set to all."""
        prop = VersionedProperty(
            is_static=True,
            is_state=True,
            is_identity=True
        )
        self.assertFalse(prop.is_valid())

    def test_static(self):
        """Test a static property."""
        prop = VersionedProperty(is_static=True)
        self.assertTrue(prop.is_static)
        self.assertTrue(prop.is_valid())

        # Test that a static and a state property is invalid
        prop = VersionedProperty(is_static=True, is_state=True)
        self.assertTrue(prop.is_static)
        self.assertTrue(prop.is_state)
        self.assertFalse(prop.is_valid())

        # Test that a static and a state property is invalid
        prop = VersionedProperty(is_static=True, is_identity=True)
        self.assertTrue(prop.is_static)
        self.assertTrue(prop.is_identity)
        self.assertFalse(prop.is_valid())

    def test_state(self):
        """Test a state property."""
        prop = VersionedProperty(is_state=True)
        self.assertTrue(prop.is_state)
        self.assertTrue(prop.is_valid())

        # Test that a state and a static property is invalid
        prop = VersionedProperty(is_state=True, is_static=True)
        self.assertTrue(prop.is_state)
        self.assertTrue(prop.is_static)
        self.assertFalse(prop.is_valid())

        # Test that a state and a static property is invalid
        prop = VersionedProperty(is_state=True, is_identity=True)
        self.assertTrue(prop.is_state)
        self.assertTrue(prop.is_identity)
        self.assertFalse(prop.is_valid())

    def test_identity(self):
        """Test an identity property."""
        prop = VersionedProperty(is_identity=True)
        self.assertTrue(prop.is_identity)
        self.assertTrue(prop.is_valid())

        # Test that an identity and a static property is invalid
        prop = VersionedProperty(is_identity=True, is_static=True)
        self.assertTrue(prop.is_identity)
        self.assertTrue(prop.is_static)
        self.assertFalse(prop.is_valid())

        # Test that an identity and a state property is invalid
        prop = VersionedProperty(is_identity=True, is_state=True)
        self.assertTrue(prop.is_identity)
        self.assertTrue(prop.is_state)
        self.assertFalse(prop.is_valid())
