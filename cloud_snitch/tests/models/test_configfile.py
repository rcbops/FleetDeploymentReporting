import unittest

from .base import DefinitionTestCase
from cloud_snitch.models import ConfigfileEntity


class TestConfigfileEntity(DefinitionTestCase):
    """Test the config file entity definition."""
    entity = ConfigfileEntity
    label = 'Configfile'
    state_label = 'ConfigfileState'
    identity_property = 'path_host'
    static_properties = [
        'path',
        'host',
        'name'
    ]
    state_properties = [
        'md5',
        'contents',
        'is_binary'
    ]
    concat_properties = {
        'path_host': [
            'path',
            'host'
        ]
    }

    def test_definition(self):
        """Test definition."""
        self.definition_test()
