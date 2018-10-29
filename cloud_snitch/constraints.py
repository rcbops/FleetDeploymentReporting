import logging

from neo4j.v1 import GraphDatabase

from cloud_snitch import models
from cloud_snitch import settings
from cloud_snitch.cli_common import base_parser

logger = logging.getLogger(__name__)


_models = [
    models.AptPackageEntity,
    models.ConfigfileEntity,
    models.ConfiguredInterfaceEntity,
    models.DeviceEntity,
    models.EnvironmentEntity,
    models.EnvironmentLockEntity,
    models.GitRemoteEntity,
    models.GitRepoEntity,
    models.GitUntrackedFileEntity,
    models.GitUrlEntity,
    models.HostEntity,
    models.InterfaceEntity,
    models.MountEntity,
    models.NameServerEntity,
    models.PartitionEntity,
    models.PythonPackageEntity,
    models.UservarEntity,
    models.VirtualenvEntity
]


def main():
    parser = base_parser(
        description="Set up neo4j constraints for cloud snitch entities."
    )
    parser.parse_args()
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    template = 'CREATE CONSTRAINT ON (n:{label}) ASSERT n.{prop} IS UNIQUE'
    with driver.session() as session:
        with session.begin_transaction() as tx:
            for _model in _models:
                tx.run(template.format(
                    label=_model.label,
                    prop=_model.identity_property)
                )
    driver.close()


if __name__ == '__main__':
    main()
