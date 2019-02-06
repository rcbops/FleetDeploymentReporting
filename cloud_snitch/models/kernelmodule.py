import logging

from .base import versioned_properties
from .base import VersionedEntity
from .base import SharedVersionedEntity
from .base import VersionedProperty

logger = logging.getLogger(__name__)


@versioned_properties
class KernelModuleParameterEntity(SharedVersionedEntity):
    """Model a unique parameter name and value pair."""

    label = 'KernelModuleParameter'
    state_label = 'KernelModuleParameterState'

    properties = {
        'name_value': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'value']
        ),
        'name': VersionedProperty(is_static=True),
        'value': VersionedProperty(is_static=True)
    }


@versioned_properties
class KernelModuleEntity(VersionedEntity):
    """Model kernel module nodes in the graph."""

    label = 'KernelModule'
    state_label = 'KernelModuleState'

    properties = {
        'name_host': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'host']
        ),
        'name': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True)
    }

    children = {
        'parameters': ('HAS_PARAMETER', KernelModuleParameterEntity)
    }
