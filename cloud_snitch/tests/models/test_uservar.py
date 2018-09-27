from .base import DefinitionTestCase

from cloud_snitch.models import UservarEntity


class TestUservarDefinition(DefinitionTestCase):
    """Test uservar definition."""
    entity = UservarEntity
    label = 'Uservar'
    state_label = 'UservarState'
    identity_property = 'name_environment'
    static_properties = [
        'name',
        'environment'
    ]
    state_properties = [
        'value'
    ]
    concat_properties = {
        'name_environment': [
            'name',
            'environment'
        ]
    }

    def test_definition(self):
        """Test the definition."""
        self.definition_test()
