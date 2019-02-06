import logging

from .base import BaseSnitcher
from cloud_snitch.models import KernelModuleEntity
from cloud_snitch.models import KernelModuleParameterEntity
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.models import HostEntity

logger = logging.getLogger(__name__)


class KernelModuleSnitcher(BaseSnitcher):
    """Models path host -> kernelmodule -> kernel_module_parameter."""

    file_pattern = '^kernelmodules_(?P<hostname>.*).json$'

    def _update_kernel_module(self, session, host, km_name, km_dict):
        """Updates kernelmodule -> parameter subgraph.

        :param session: neo4j driver session
        :type session: neo4j.v1.session.BoltSession
        :param host: Host object containing kernel modules
        :type host: HostEntity
        :param km_name: kernel module name
        :type km_name: str
        :param km_dict: kernel module properties
        :type km_dict: dict
        :returns: KernelModule object or None for no action
        :rtype: KernelModuleEntity|None
        """
        km = KernelModuleEntity(host=host.identity, name=km_name)
        km.update(session, self.time_in_ms)

        params = []
        for param_name, param_value in km_dict.get('parameters', {}).items():
            param = KernelModuleParameterEntity(
                name=param_name,
                value=param_value
            )
            param.update(session, self.time_in_ms)
            params.append(param)

        km.parameters.update(session, params, self.time_in_ms)
        return km

    def _snitch(self, session):
        """Update the kernel modules subgraph.

        :param session: neo4j driver session
        :type session: neo4j.v1.session.BoltSession
        """
        env = EnvironmentEntity(uuid=self.run.environment_uuid)

        for hostname, filename in self._find_host_tuples(self.file_pattern):
            kms = []

            # Find host in graph, continue if host not found.
            host = HostEntity(hostname=hostname, environment=env.identity)
            host = HostEntity.find(session, host.identity)
            if host is None:
                logger.warning(
                    'Unable to locate host entity {}'.format(hostname)
                )
                continue

            # Read data from file
            km_data = self.run.get_object(filename).get('data', {})

            # Iterate over package maps
            for km_name, km_dict in km_data.items():
                km = self._update_kernel_module(
                    session,
                    host,
                    km_name,
                    km_dict
                )
                if km is not None:
                    kms.append(km)
            host.kernelmodules.update(session, kms, self.time_in_ms)
