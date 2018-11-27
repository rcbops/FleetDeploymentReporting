"""Quick module for running snitchers.

Expect this to change into something configured by yaml.
Snitchers will also probably become python entry points.
"""
import logging
import time

from cloud_snitch.snitchers.apt import AptSnitcher
from cloud_snitch.snitchers.configfile import ConfigfileSnitcher
from cloud_snitch.snitchers.environment import EnvironmentSnitcher
from cloud_snitch.snitchers.git import GitSnitcher
from cloud_snitch.snitchers.host import HostSnitcher
from cloud_snitch.snitchers.pip import PipSnitcher
from cloud_snitch.snitchers.uservars import UservarsSnitcher
from cloud_snitch.snitchers.configuredinterface import \
    ConfiguredInterfaceSnitcher

from cloud_snitch import runs
from cloud_snitch import utils
from cloud_snitch.cli_common import base_parser
from cloud_snitch.driver import DriverContext
from cloud_snitch.exc import RunContainsOldDataError
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.lock import lock_environment

logger = logging.getLogger(__name__)


parser = base_parser(
    description="Ingest collected snitch data to neo4j."
)
parser.add_argument(
    'path',
    help='Path or archived collection run.'
)
parser.add_argument(
    '--key',
    help='Base64 encoded 256 bit AES key. For testing/debug only.'
)


def check_run_time(driver, run):
    """Prevent a run from updating an environment.

    Protects an environment with newer data from a run with older data.

    :param driver: Neo4J database driver instance
    :type driver: neo4j.v1.GraphDatabase.driver
    :param run: Date run instance
    :type run: cloud_snitch.runs.Run
    """
    # Check to see if run data is new
    with driver.session() as session:
        e = EnvironmentEntity.find(session, run.environment_uuid)

        # If the environment exists, check its last update
        if e is not None:
            last_update = utils.utcdatetime(e.last_update(session) or 0)
            logger.debug(
                "Comparing {} to {}".format(run.completed, last_update)
            )
            if run.completed <= last_update:
                raise RunContainsOldDataError(run, last_update)


def consume(driver, run):
    """Consumes data in a run.

    :param run: Run to consume
    :type run: runs.Run
    """
    snitchers = [
        EnvironmentSnitcher(driver, run),
        GitSnitcher(driver, run),
        HostSnitcher(driver, run),
        ConfigfileSnitcher(driver, run),
        PipSnitcher(driver, run),
        AptSnitcher(driver, run),
        UservarsSnitcher(driver, run),
        ConfiguredInterfaceSnitcher(driver, run)
    ]
    for snitcher in snitchers:
        snitcher.snitch()


def sync_run(driver, run):
    """Syncs an individuals run.

    :param run: Run to sync
    :type run: runs.Run
    """
    check_run_time(driver, run)
    run.start()
    logger.info("Starting collection on {}".format(run.path))
    consume(driver, run)
    logger.info("Run completion time: {}".format(
        utils.milliseconds(run.completed)
    ))
    run.finish()


def sync_single(path, key=None):
    """Used to sync a single discrete set of run data.

    :param path: Path to run data
    :type path: str
    :param key: Encryption/Decryption base 64 encoded key
    :type key: str
    """
    with DriverContext() as driver:
        run = runs.Run(path, key=key)
        env = EnvironmentEntity(
            uuid=run.environment_uuid,
            name=run.environment_name,
            account_number=run.environment_account_number
        )
        with lock_environment(driver, env):
            sync_run(driver, run)


def main():
    start = time.time()
    args = parser.parse_args()

    try:
        sync_single(args.path, key=args.key)
    except Exception:
        logger.exception('Could not sync.')
    finally:
        logger.info("Finished in {:.3f} seconds".format(time.time() - start))


if __name__ == '__main__':
    main()
