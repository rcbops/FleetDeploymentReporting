import logging

from .base import versioned_properties
from .base import SharedVersionedEntity
from .base import VersionedProperty

logger = logging.getLogger(__name__)


@versioned_properties
class AptPackageEntity(SharedVersionedEntity):
    """Model apt package nodes in the graph."""

    label = 'AptPackage'
    state_label = 'AptPackageState'

    properties = {
        'name_version': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'version']
        ),
        'name': VersionedProperty(is_static=True),
        'version': VersionedProperty(is_static=True),
    }
