import json
import logging

from .base import BaseSnitcher
from cloud_snitch.models import ConfiguredInterfaceEntity
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.models import HostEntity

logger = logging.getLogger(__name__)


class ConfiguredInterfaceSnitcher(BaseSnitcher):
    """Models path host -> configuredinterface"""

    file_pattern = '^configuredinterface_(?P<hostname>.*).json$'

    def _update_host(self, session, hostname, filename):
        """Update configuredinterfaces for a host.

        :param session: neo4j driver session
        :type session: neo4j.v1.session.BoltSession
        :param hostname: Name of the host
        :type hostname: str
        :param filename: Name of file
        :type filename: str
        """
        # Extract config and environment data.
        with open(filename, 'r') as f:
            data = json.loads(f.read())
            envdict = data.get('environment', {})
            env = EnvironmentEntity(
                account_number=envdict.get('account_number'),
                name=envdict.get('name')
            )
            configdata = data.get('data', {})

        # Find parent host object - return early if not exists.
        host = HostEntity(hostname=hostname, environment=env.identity)
        host = HostEntity.find(session, host.identity)
        if host is None:
            logger.warning('Unable to locate host {}'.format(hostname))
            return

        # Iterate over configration files in the host's directory
        interfaces = []
        for device, metadata in configdata.items():
            interfacekwargs = {
                'device': device,
                'host': host.identity
            }
            for key, val in metadata.items():
                if '-' in key:
                    # neo4j properties don't allow -
                    # dns-nameservers, offline-sg
                    key = key.replace('-', '_')
                interfacekwargs[key] = val

            interface = ConfiguredInterfaceEntity(**interfacekwargs)
            interface.update(session, self.time_in_ms)
            interfaces.append(interface)
        # Update host -> configuredinterfaces relationships.
        host.configuredinterfaces.update(session, interfaces, self.time_in_ms)

    def _snitch(self, session):
        """Update the apt part of the graph..

        :param session: neo4j driver session
        :type session: neo4j.v1.session.BoltSession
        """
        for hostname, filename in self._find_host_tuples(self.file_pattern):
            self._update_host(session, hostname, filename)
