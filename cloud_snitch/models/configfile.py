import logging

from .base import versioned_properties
from .base import VersionedEntity
from .base import VersionedProperty

logger = logging.getLogger(__name__)


@versioned_properties
class ConfigfileEntity(VersionedEntity):
    """Model a configuration file in the graph."""

    label = 'Configfile'
    state_label = 'ConfigfileState'
    properties = {
        'path_host': VersionedProperty(
            is_identity=True,
            concat_properties=['path', 'host']
        ),
        'path': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True),
        'name': VersionedProperty(is_static=True),
        'md5': VersionedProperty(is_state=True),
        'contents': VersionedProperty(is_state=True),
        'is_binary': VersionedProperty(is_state=True)
    }
