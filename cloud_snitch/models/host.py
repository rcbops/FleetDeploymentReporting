import logging

from .base import versioned_properties
from .base import SharedVersionedEntity
from .base import VersionedEntity
from .base import VersionedProperty
from .apt import AptPackageEntity
from .configfile import ConfigfileEntity
from .kernelmodule import KernelModuleEntity
from .virtualenv import VirtualenvEntity

logger = logging.getLogger(__name__)


@versioned_properties
class NameServerEntity(SharedVersionedEntity):
    """Model a name server node in the graph."""
    label = 'NameServer'
    state_label = 'NameServerState'
    properties = {
        'ip': VersionedProperty(is_identity=True)
    }


@versioned_properties
class PartitionEntity(VersionedEntity):
    """Model a partition on a device in the graph."""

    label = 'Partition'
    state_label = 'PartitionState'
    properties = {
        'name_device': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'device']
        ),
        'name': VersionedProperty(is_static=True),
        'device': VersionedProperty(is_static=True),
        'size': VersionedProperty(is_state=True),
        'start': VersionedProperty(is_state=True)
    }


@versioned_properties
class DeviceEntity(VersionedEntity):
    """Model a device node in the graph."""

    label = 'Device'
    state_label = 'DeviceState'
    properties = {
        'name_host': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'host']
        ),
        'name': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True),
        'removable': VersionedProperty(is_state=True),
        'rotational': VersionedProperty(is_state=True),
        'size': VersionedProperty(is_state=True)
    }
    children = {
        'partitions': ('HAS_PARTITION', PartitionEntity)
    }


@versioned_properties
class MountEntity(VersionedEntity):
    """Model a mount node in the graph."""

    label = 'Mount'
    state_label = 'MountState'
    properties = {
        'mount_host': VersionedProperty(
            is_identity=True,
            concat_properties=['mount', 'host']
        ),
        'mount': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True),
        'device': VersionedProperty(is_state=True),
        'size_total': VersionedProperty(is_state=True),
        'fstype': VersionedProperty(is_state=True)
    }


@versioned_properties
class InterfaceEntity(VersionedEntity):
    """Model interface nodes in the graph."""

    label = 'Interface'
    state_label = 'InterfaceState'
    properties = {
        'device_host': VersionedProperty(
            is_identity=True,
            concat_properties=['device', 'host']
        ),
        'device': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True),
        'active': VersionedProperty(is_state=True),
        'ipv4_address': VersionedProperty(is_state=True),
        'ipv6_address': VersionedProperty(is_state=True),
        'macaddress': VersionedProperty(is_state=True),
        'mtu': VersionedProperty(is_state=True, type=int),
        'promisc': VersionedProperty(is_state=True),
        'type': VersionedProperty(is_state=True)
    }


@versioned_properties
class ConfiguredInterfaceEntity(VersionedEntity):
    """Model a ConfiguredInterface in the graph."""

    label = 'ConfiguredInterface'
    state_label = 'ConfiguredInterfaceState'
    properties = {
        'device_host': VersionedProperty(
            is_identity=True,
            concat_properties=['device', 'host']
        ),
        'device': VersionedProperty(is_static=True),
        'host': VersionedProperty(is_static=True),
        'mtu': VersionedProperty(is_state=True, type=int),
        'offload_sg': VersionedProperty(is_state=True),
        'bridge_waitport': VersionedProperty(is_state=True),
        'bridge_fd': VersionedProperty(is_state=True),
        'bridge_ports': VersionedProperty(is_state=True),
        'bridge_stp': VersionedProperty(is_state=True),
        'address': VersionedProperty(is_state=True),
        'netmask': VersionedProperty(is_state=True),
        'dns_nameservers': VersionedProperty(is_state=True),
        'gateway': VersionedProperty(is_state=True)
    }


@versioned_properties
class HostEntity(VersionedEntity):
    """Model host nodes in the graph."""

    label = 'Host'
    state_label = 'HostState'

    properties = {
        'hostname_environment': VersionedProperty(
            is_identity=True,
            concat_properties=['hostname', 'environment']
        ),
        'hostname': VersionedProperty(is_static=True),
        'environment': VersionedProperty(is_static=True),

        'architecture': VersionedProperty(is_state=True),
        'bios_date': VersionedProperty(is_state=True),
        'bios_version': VersionedProperty(is_state=True),
        'default_ipv4_address': VersionedProperty(is_state=True),
        'default_ipv6_address': VersionedProperty(is_state=True),
        'kernel': VersionedProperty(is_state=True),
        'memtotal_mb': VersionedProperty(is_state=True, type=int),
        'lsb_codename': VersionedProperty(is_state=True),
        'lsb_description': VersionedProperty(is_state=True),
        'lsb_id': VersionedProperty(is_state=True),
        'lsb_major_release': VersionedProperty(is_state=True),
        'lsb_release': VersionedProperty(is_state=True),
        'fqdn': VersionedProperty(is_state=True),
        'pkg_mgr': VersionedProperty(is_state=True),
        'processor_cores': VersionedProperty(is_state=True, type=int),
        'processor_count': VersionedProperty(is_state=True, type=int),
        'processor_threads_per_core': VersionedProperty(
            is_state=True,
            type=int
        ),
        'processor_vcpus': VersionedProperty(is_state=True, type=int),
        'python_executable': VersionedProperty(is_state=True),
        'python_version': VersionedProperty(is_state=True),
        'python_type': VersionedProperty(is_state=True),
        'service_mgr': VersionedProperty(is_state=True),
        'selinux': VersionedProperty(is_state=True, type=bool),
        'ansible_version_full': VersionedProperty(is_state=True)
    }
    children = {
        'aptpackages': ('HAS_APT_PACKAGE', AptPackageEntity),
        'virtualenvs': ('HAS_VIRTUALENV', VirtualenvEntity),
        'configfiles': ('HAS_CONFIG_FILE', ConfigfileEntity),
        'nameservers': ('HAS_NAMESERVER', NameServerEntity),
        'interfaces': ('HAS_INTERFACE', InterfaceEntity),
        'kernelmodules': ('HAS_KERNEL_MODULE', KernelModuleEntity),
        'mounts': ('HAS_MOUNT', MountEntity),
        'devices': ('HAS_DEVICE', DeviceEntity),
        'configuredinterfaces': ('HAS_CONFIGURED_INTERFACE',
                                 ConfiguredInterfaceEntity)
    }
