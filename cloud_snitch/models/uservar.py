import logging

from .base import versioned_properties
from .base import VersionedEntity
from .base import VersionedProperty

logger = logging.getLogger(__name__)


@versioned_properties
class UservarEntity(VersionedEntity):
    """Models a user variable."""
    label = 'Uservar'
    state_label = 'UservarState'
    properties = {
        'name_environment': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'environment']
        ),
        'name': VersionedProperty(is_static=True),
        'environment': VersionedProperty(is_static=True),
        'value': VersionedProperty(is_state=True)
    }
