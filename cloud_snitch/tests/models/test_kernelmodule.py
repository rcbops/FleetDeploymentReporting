from .base import DefinitionTestCase

from cloud_snitch.models import KernelModuleEntity
from cloud_snitch.models import KernelModuleParameterEntity


class TestKernelModuleDefinition(DefinitionTestCase):
    """Test kernel module definition."""
    entity = KernelModuleEntity
    label = 'KernelModule'
    state_label = 'KernelModuleState'
    identity_property = 'name_host'
    static_properties = ['name', 'host']
    concat_properties = {
        'name_host': [
            'name',
            'host'
        ]
    }

    children = (
        ('parameters', ('HAS_PARAMETER', KernelModuleParameterEntity)),
    )

    def test_definition(self):
        """Test the definition."""
        self.definition_test()


class TestKernelModuleParameterDefinition(DefinitionTestCase):
    """Test kernel module parameter definition."""
    entity = KernelModuleParameterEntity
    label = 'KernelModuleParameter'
    state_label = 'KernelModuleParameterState'
    identity_property = 'name_value'
    static_properties = [
        'name',
        'value'
    ]
    concat_properties = {
        'name_value': [
            'name',
            'value'
        ]
    }

    def test_definition(self):
        """Test the definition."""
        self.definition_test()
