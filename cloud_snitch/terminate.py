"""Quick module for terminating relationships for an environment."""
import logging
import pprint
import time

from cloud_snitch import settings
from cloud_snitch import utils
from cloud_snitch.cli_common import base_parser
from cloud_snitch.cli_common import confirm_env_action
from cloud_snitch.cli_common import find_environment
from cloud_snitch.lock import lock_environment
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.models import registry
from cloud_snitch.exc import EnvironmentNotFoundError
from neo4j.v1 import GraphDatabase

logger = logging.getLogger(__name__)

parser = base_parser(
    description=(
        "Terminate an environment. Mark ending time on all relationships "
        "stemming from the environment."
    )
)

parser.add_argument(
    'account_number',
    type=str,
    help='Account number of customer environment to terminate.'
)

parser.add_argument(
    'name',
    type=str,
    help='Name of customer environment to terminate.'
)

parser.add_argument(
    '-s', '--skip',
    action='store_true',
    help='Skip interactive confirmation.'
)

parser.add_argument(
    '--time',
    type=int,
    help="Optional timestamp in ms. Defaults to utc now.",
    default=utils.milliseconds_now()
)

parser.add_argument(
    '--limit',
    type=int,
    help="Optional number of paths to consider at a time. Defaults to 2000.",
    default=2000
)


def set_to_until_zero(session, env, time, limit=2000):
    """Set current relationships' to attributes to time.

    Runs in a loop until there are no more current relationships.

    :param session: Neo4j driver session.
    :type session: neo4j.v1.session.BoltSession
    :param env: Instance of environment entity.
    :type env: EnvironmentEntity
    :param time: Timestamp in ms.
    :type time: int
    :param limit: Number of items to delete at a time.
        When deleting nodes with large numbers of relationships,
        consider making this smaller.
    :type limit: int
    :return: The number of changed relationships.
    :rtype: int
    """
    params = {
        'time': time,
        'limit': limit,
        'EOT': utils.EOT,
        'account_number_name': env.account_number_name
    }
    total_changed = 0
    changed = 1

    # Alter query for deleting in chunks
    cipher = (
        "MATCH p = "
        "(e:Environment {account_number_name: $account_number_name})-[*]->(o)\n"  # noqa E501
        "WHERE ANY(rel in relationships(p) where rel.to = $EOT)\n"
        "WITH filter(rel in relationships(p) where rel.to = $EOT) "
        "as rels LIMIT $limit\n"
        "UNWIND rels as r\n"
        "SET r.to = $time\n"
        "RETURN count(*) as changed\n"
    )
    # Keep going until 0.
    while changed > 0:
        with session.begin_transaction() as tx:
            resp = tx.run(cipher, **params)
            changed = resp.single()['changed']
            total_changed += changed
    return total_changed


def terminate(account_number, name, new_time, limit, skip=False):
    """Remove all data associated with an environment."""
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    with driver.session() as session:
        # Attempt to locate environment by account number and name
        env = find_environment(session, account_number, name)

        # If found, confirm termination
        msg = (
            'Confirming termination of environment with account '
            'number \'{}\' and name \'{}\''
            .format(account_number, name)
        )
        confirmed = confirm_env_action(account_number, name, msg, skip=skip)
        if not confirmed:
            logger.info("Termination unconfirmed...cancelling.")
            exit(0)

        # Acquire lock and and terminate
        start = time.time()
        with lock_environment(driver, env.account_number, env.name):

            logger.debug("Acquired the lock.!!!")

            # Match relation ships with to property set to java end of time.
            # And bulk update until 0 matches.
            changed = set_to_until_zero(session, env, new_time, limit=limit)

            logger.info(
                "Terminated {} relationships at {}.".format(changed, new_time)
            )

        logger.info(
            "Completed termination in {:.3f}s".format(time.time() - start)
        )


def main():
    """Entry point for the console script."""
    args = parser.parse_args()
    terminate(
        args.account_number,
        args.name,
        args.time,
        args.limit,
        skip=args.skip
    )


if __name__ == '__main__':
    main()
