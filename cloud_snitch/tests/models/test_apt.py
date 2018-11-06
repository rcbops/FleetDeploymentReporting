from .base import DefinitionTestCase

from cloud_snitch.models import AptPackageEntity


class TestAptPackageEntity(DefinitionTestCase):
    """Test the apt package entity definition."""
    entity = AptPackageEntity
    label = 'AptPackage'
    state_label = 'AptPackageState'
    identity_property = 'name_version'
    static_properties = [
        'name',
        'version'
    ]
    concat_properties = {
        'name_version': [
            'name',
            'version'
        ]
    }

    def test_definition(self):
        """Test definition."""
        self.definition_test()
