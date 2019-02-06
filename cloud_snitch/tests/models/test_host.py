from .base import DefinitionTestCase

from cloud_snitch.models import AptPackageEntity
from cloud_snitch.models import DeviceEntity
from cloud_snitch.models import ConfigfileEntity
from cloud_snitch.models import ConfiguredInterfaceEntity
from cloud_snitch.models import HostEntity
from cloud_snitch.models import InterfaceEntity
from cloud_snitch.models import KernelModuleEntity
from cloud_snitch.models import MountEntity
from cloud_snitch.models import NameServerEntity
from cloud_snitch.models import PartitionEntity
from cloud_snitch.models import VirtualenvEntity


class TestNameServerEntity(DefinitionTestCase):
    """Test the name server entity definition."""
    entity = NameServerEntity
    label = 'NameServer'
    state_label = 'NameServerState'
    identity_property = 'ip'

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestPartitionEntity(DefinitionTestCase):
    """Test the partition entity definition."""
    entity = PartitionEntity
    label = 'Partition'
    state_label = 'PartitionState'
    identity_property = 'name_device'
    static_properties = [
        'name',
        'device'
    ]
    state_properties = [
        'size',
        'start'
    ]
    concat_properties = {
        'name_device': [
            'name',
            'device'
        ]
    }

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestDeviceEntity(DefinitionTestCase):
    """Test the device entity definition."""
    entity = DeviceEntity
    label = 'Device'
    state_label = 'DeviceState'
    identity_property = 'name_host'
    static_properties = [
        'name',
        'host',
    ]
    state_properties = [
        'removable',
        'rotational',
        'size'
    ]
    concat_properties = {
        'name_host': [
            'name',
            'host'
        ]
    }
    children = (
        ('partitions', ('HAS_PARTITION', PartitionEntity)),
    )

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestMountEntity(DefinitionTestCase):
    """Test the mount entity definition."""
    entity = MountEntity
    label = 'Mount'
    state_label = 'MountState'
    identity_property = 'mount_host'
    static_properties = [
        'mount',
        'host',
    ]
    state_properties = [
        'device',
        'size_total',
        'fstype'
    ]
    concat_properties = {
        'mount_host': [
            'mount',
            'host'
        ]
    }

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestInterfaceDefinition(DefinitionTestCase):
    """Test the interface entity definition."""
    entity = InterfaceEntity
    label = 'Interface'
    state_label = 'InterfaceState'
    identity_property = 'device_host'
    static_properties = [
        'device',
        'host'
    ]
    state_properties = [
        'active',
        'ipv4_address',
        'ipv6_address',
        'macaddress',
        'mtu',
        'promisc',
        'type'
    ]
    concat_properties = {
        'device_host': [
            'device',
            'host'
        ]
    }

    def test_definition(self):
        """Test defition."""
        self.definition_test()


class TestConfiguredInterfaceDefinition(DefinitionTestCase):
    """Test the configured interface entity definition."""

    entity = ConfiguredInterfaceEntity
    label = 'ConfiguredInterface'
    state_label = 'ConfiguredInterfaceState'
    identity_property = 'device_host'
    static_properties = [
        'device',
        'host'
    ]
    state_properties = [
        'mtu',
        'offload_sg',
        'bridge_waitport',
        'bridge_fd',
        'bridge_ports',
        'bridge_stp',
        'address',
        'netmask',
        'dns_nameservers',
        'gateway'
    ]
    concat_properties = {
        'device_host': ['device', 'host']
    }

    def test_definition(self):
        self.definition_test()


class TestHostDefinition(DefinitionTestCase):

    entity = HostEntity

    label = 'Host'
    state_label = 'HostState'

    identity_property = 'hostname_environment'
    static_properties = [
        'hostname',
        'environment'
    ]

    state_properties = [
        'architecture',
        'bios_date',
        'bios_version',
        'default_ipv4_address',
        'default_ipv6_address',
        'kernel',
        'memtotal_mb',
        'lsb_codename',
        'lsb_description',
        'lsb_id',
        'lsb_major_release',
        'lsb_release',
        'fqdn',
        'pkg_mgr',
        'processor_cores',
        'processor_count',
        'processor_threads_per_core',
        'processor_vcpus',
        'python_executable',
        'python_version',
        'python_type',
        'service_mgr',
        'selinux',
        'ansible_version_full'
    ]

    concat_properties = {
        'hostname_environment': [
            'hostname',
            'environment'
        ]
    }

    children = (
        ('aptpackages', ('HAS_APT_PACKAGE', AptPackageEntity)),
        ('virtualenvs', ('HAS_VIRTUALENV', VirtualenvEntity)),
        ('configfiles', ('HAS_CONFIG_FILE', ConfigfileEntity)),
        ('nameservers', ('HAS_NAMESERVER', NameServerEntity)),
        ('interfaces', ('HAS_INTERFACE', InterfaceEntity)),
        ('mounts', ('HAS_MOUNT', MountEntity)),
        ('devices', ('HAS_DEVICE', DeviceEntity)),
        ('kernelmodules', ('HAS_KERNEL_MODULE', KernelModuleEntity)),
        (
            'configuredinterfaces', (
                'HAS_CONFIGURED_INTERFACE',
                ConfiguredInterfaceEntity
            )
        )
    )

    def test_definition(self):
        """Test the definition."""
        self.definition_test()
