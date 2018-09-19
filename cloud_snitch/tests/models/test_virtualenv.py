from .base import DefinitionTestCase

from cloud_snitch.models import PythonPackageEntity
from cloud_snitch.models import VirtualenvEntity


class TestPythonPackageDefinition(DefinitionTestCase):
    """Test python package definition."""
    entity = PythonPackageEntity
    label = 'PythonPackage'
    state_label = 'PythonPackageState'
    identity_property = 'name_version'
    static_properties = ['name', 'version']
    concat_properties = {
        'name_version': [
            'name',
            'version'
        ]
    }

    def test_definition(self):
        """Test the definition."""
        self.definition_test()


class TestVirtualenvDefinition(DefinitionTestCase):
    """Test virtualenv definition."""
    entity = VirtualenvEntity
    label = 'Virtualenv'
    state_label = 'VirtualenvState'
    identity_property = 'path_host'
    static_properties = [
        'path',
        'host'
    ]
    concat_properties = {
        'path_host': [
            'path',
            'host'
        ]
    }

    children = (
        ('pythonpackages', ('HAS_PYTHON_PACKAGE', PythonPackageEntity)),
    )

    def test_definition(self):
        """Test the definition."""
        self.definition_test()
