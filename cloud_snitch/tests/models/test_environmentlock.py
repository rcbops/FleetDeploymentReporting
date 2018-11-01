import unittest

from .base import DefinitionTestCase
from cloud_snitch.models import EnvironmentLockEntity


class TestEnvironmentEntity(DefinitionTestCase):
    """Test the environment entity definition."""
    entity = EnvironmentLockEntity
    label = 'EnvironmentLock'
    state_label = 'EnvironmentLockState'
    identity_property = 'account_number_name'
    static_properties = [
        'account_number',
        'name',
        'locked'
    ]
    concat_properties = {
        'account_number_name': [
            'account_number',
            'name'
        ]
    }

    def test_definition(self):
        """Test definition."""
        self.definition_test()
