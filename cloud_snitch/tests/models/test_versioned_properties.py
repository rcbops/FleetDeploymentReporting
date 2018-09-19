import unittest

from cloud_snitch.exc import EntityDefinitionError
from cloud_snitch.models.base import versioned_properties
from cloud_snitch.models.base import VersionedEntity
from cloud_snitch.models.base import VersionedProperty


class TestEntityDecorator(unittest.TestCase):
    """Test the entity decorator."""

    def test_valid(self):
        """Test decorating a valid entity."""
        @versioned_properties
        class Entity(VersionedEntity):
            properties = {
                'test_id': VersionedProperty(is_identity=True),
                'test_static': VersionedProperty(is_static=True),
                'test_state': VersionedProperty(is_state=True),
                'test_concat': VersionedProperty(
                    is_static=True,
                    concat_properties=['test_state', 'test_static']
                )
            }

        self.assertEqual(Entity.identity_property, 'test_id')
        self.assertTrue('test_static' in Entity.static_properties)
        self.assertTrue('test_concat' in Entity.static_properties)
        self.assertTrue('test_state' in Entity.state_properties)
        self.assertEqual(
            Entity.concat_properties['test_concat'][0],
            'test_state'
        )
        self.assertEqual(
            Entity.concat_properties['test_concat'][1],
            'test_static'
        )

    def test_multiple_identity_properties(self):
        """Test exception from multiple identity properties."""
        with self.assertRaises(EntityDefinitionError):
            @versioned_properties
            class Entity(VersionedEntity):
                properties = {
                    'identity_1': VersionedProperty(is_identity=True),
                    'identity_2': VersionedProperty(is_identity=True)
                }

    def test_no_identity_property(self):
        """Test exception from no identity property."""
        with self.assertRaises(EntityDefinitionError):
            @versioned_properties
            class Entity(VersionedEntity):
                properties = {
                    'test_static': VersionedProperty(is_static=True),
                    'test_state': VersionedProperty(is_state=True)
                }

    def test_invalid_property(self):
        """Test exception from invalid property."""
        with self.assertRaises(EntityDefinitionError):
            @versioned_properties
            class Entity(VersionedEntity):
                properties = {
                    'test_static': VersionedProperty(
                        is_static=True,
                        is_state=True
                    )
                }

    def test_multple_static_and_state_properties(self):
        """Test entity with multiple static and state properties."""
        @versioned_properties
        class Entity(VersionedEntity):
            properties = {
                'test_identity': VersionedProperty(is_identity=True),
                'test_static_1': VersionedProperty(is_static=True),
                'test_state_1': VersionedProperty(is_state=True),
                'test_static_2': VersionedProperty(is_static=True),
                'test_state_2': VersionedProperty(is_state=True)
            }
        self.assertTrue('test_static_1' in Entity.static_properties)
        self.assertTrue('test_static_2' in Entity.static_properties)
        self.assertTrue('test_state_1' in Entity.state_properties)
        self.assertTrue('test_state_2' in Entity.state_properties)
