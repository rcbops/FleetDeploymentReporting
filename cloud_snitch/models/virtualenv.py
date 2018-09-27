import logging

from .base import versioned_properties
from .base import SharedVersionedEntity
from .base import VersionedEntity
from .base import VersionedProperty

logger = logging.getLogger(__name__)


@versioned_properties
class PythonPackageEntity(SharedVersionedEntity):
    """Model pythonpackage nodes in the graph."""
    label = 'PythonPackage'
    state_label = 'PythonPackageState'
    properties = {
        'name_version': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'version']
        ),
        'name': VersionedProperty(is_static=True),
        'version': VersionedProperty(is_static=True)
    }


@versioned_properties
class VirtualenvEntity(VersionedEntity):
    """Model virtualenv nodes in the graph."""
    label = 'Virtualenv'
    state_label = 'VirtualenvState'
    properties = {
        'path_host': VersionedProperty(
            is_identity=True,
            concat_properties=['path', 'host']
        ),
        'path': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True)
    }
    children = {
        'pythonpackages': ('HAS_PYTHON_PACKAGE', PythonPackageEntity)
    }
