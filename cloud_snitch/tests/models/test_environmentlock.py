from .base import DefinitionTestCase
from cloud_snitch.models import EnvironmentLockEntity


class TestEnvironmentLockEntity(DefinitionTestCase):
    """Test the environment entity definition."""
    entity = EnvironmentLockEntity
    label = 'EnvironmentLock'
    state_label = 'EnvironmentLockState'
    identity_property = 'uuid'
    static_properties = [
        'account_number',
        'name',
        'locked'
    ]

    def test_definition(self):
        """Test definition."""
        self.definition_test()
