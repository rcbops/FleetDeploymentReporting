"""Quick module for generating fake data from real data."""
import argparse
import logging
import pprint

from cloud_snitch import settings
from cloud_snitch.lock import lock_environment
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.models import registry
from cloud_snitch.exc import EnvironmentNotFoundError
from neo4j.v1 import GraphDatabase

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Remove customer data."
)

parser.add_argument(
    'account_number',
    type=str,
    help='Account number of customer environment to remove.'
)

parser.add_argument(
    'name',
    type=str,
    help='Name of customer environment to remove.'
)

parser.add_argument(
    '-s', '--skip',
    action='store_true',
    help='Skip interactive confirmation.'
)


def find_environment(session, account_number, name):
    """Find an environment by account number and name.

    :param session: neo4j driver session
    :type session: neo4j.v1.session.BoltSession
    :param account number: Account number of environment
    :type account number: str
    :param name: Name of the environment
    :type name: str
    :returns: Environment entity
    :rtype: EnvironmentEntity
    """
    env = EnvironmentEntity.find(session, '{}-{}'.format(account_number, name))
    if env is None:
        raise EnvironmentNotFoundError(account_number, name)
    return env


def confirm(account_number, name, skip=False):
    """Confirm delete unless skipped.

    :param account number: Account number of environment
    :type account number: str
    :param name: Name of the environment
    :type name: str
    :param skip: Whether or not to skip bypass
    :type skip: bool
    :returns: Whether or not remove is confirmed.
    :rtype: bool
    """
    confirmed = skip
    if not confirmed:
        resp = ''
        msg = (
            'Confirming deletion of environment with account number \'{}\' '
            'and name \'{}\' (y/n) --> '
        ).format(account_number, name)

        while (resp != 'y' and resp != 'n'):
            resp = input(msg).lower()

        confirmed = (resp == 'y')
    return confirmed


def delete_until_zero(session, match, params=None, limit=2000):
    """Delete chunks of matches until no matches.

    Deletes in chunks of limit.

    :param session: Neo4j driver session.
    :type session: neo4j.v1.session.BoltSession
    :param match: Match query clause of a neo4j query
    :type match: str
    :param params: Neo4j query parameters.
    :type params: dict|None
    :param limit: Number of items to delete at a time.
        When deleting nodes with large numbers of relationships,
        consider making this smaller.
    :type limit: int
    :return: The number of deleted nodes.
    :rtype: int
    """
    if params is None:
        params = {}

    total_deleted = 0
    deleted = 1

    # Alter query for deleting in chunks
    cipher = [
        match,
        'WITH n LIMIT {}'.format(limit),
        'DETACH DELETE n',
        'RETURN count(*) as `deleted`'
    ]
    cipher = ' '.join(cipher)

    # Keep going until 0.
    while deleted > 0:
        with session.begin_transaction() as tx:
            resp = tx.run(cipher, **params)
            deleted = resp.single()['deleted']
            total_deleted += deleted
    return total_deleted


def prune(session, env, path, stats):
    """Prune the leaves at the end of the path.

    First prune state leaves
    Then prune leaves
    Only if the type of leaf is not shared.

    :param session: Neo4j driver session
    :type session: neo4j.v1.session.BoltSession
    :param env: Environment to remove
    :type env: EnvironmentEntity
    :param path: List of labels indicating path.
    :type path: list
    :param stats: Dictionary of deleted node counts.
    :type stats: dict
    :returns: Updated deleted node counts.
        (This is changed by reference but also returned.)
    :rtype: dict
    """
    leaf = path[-1]

    # Do nothing if the leaf is shared.
    if registry.is_shared(leaf):
        stats[leaf] = None
        return stats

    # Set up some reusable pieces
    where = 'WHERE e.account_number_name = $account_number_name'
    params = {'account_number_name': env.account_number_name}

    # First detach and delete state nodes.
    if registry.state_properties(leaf):
        match = (
            'MATCH (e:Environment)-[*]->(:{})-[:HAS_STATE]->(n:{}State)'
            'WHERE e.account_number_name = $account_number_name'
        ).format(leaf, leaf)
        deleted = delete_until_zero(session, match, params=params, limit=5000)
        stats['{}State'.format(leaf)] = deleted

    # Then detach and delete identity nodes
    if leaf != 'Environment':
        match = (
            'MATCH (e:Environment)-[*]->(n:{})'
            'WHERE e.account_number_name = $account_number_name'
        ).format(leaf)
    else:
        # Environment is a special case.
        # There are no paths from environment to self
        match = (
            'MATCH (n:Environment)'
            'WHERE n.account_number_name = $account_number_name'
        )

    deleted = delete_until_zero(session, match, params=params, limit=5000)
    stats[leaf] = deleted
    return stats


def remove(account_number, name, skip=False):
    """Remove all data associated with an environment."""
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    with driver.session() as session:
        # Attempt to locate environment by account number and name
        env = find_environment(session, account_number, name)

        # If found, confirm deletion
        confirmed = confirm(account_number, name, skip=skip)
        if not confirmed:
            logger.info("Removal unconfirmed...cancelling.")
            exit(0)

        # Acquire lock and delete
        with lock_environment(driver, env.account_number, env.name):

            logger.debug("Acquired the lock.!!!")
            # get all paths
            paths = []
            for label, model in registry.models.items():
                path = [l for l, r in registry.path(label)]
                path.append(label)
                paths.append(path)

            paths.sort(key=lambda x: len(x))
            logger.debug(pprint.pformat(paths))

            stats = {}
            for path in reversed(paths):
                prune(session, env, path, stats)

            logger.info(
                "Deleted node counts by type:\n{}"
                .format(pprint.pformat(stats))
            )


def main():
    args = parser.parse_args()
    remove(args.account_number, args.name, skip=args.skip)


if __name__ == '__main__':
    main()
