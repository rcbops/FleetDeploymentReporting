"""
Collection of common code shared between console scripts.
"""
import argparse
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.exc import EnvironmentNotFoundError

from cloud_snitch.meta import version


def base_parser(**kwargs):
    """Creates a base argument parser that includes version as an option.

    Console scripts should add to this parser to share version functionality.

    :returns: Instance of an argument parser.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(**kwargs)
    parser.add_argument(
        '-v', '--version',
        help='Display version and exit.',
        action='version',
        version='%(prog)s {}'.format(version)
    )
    return parser


def confirm_env_action(account_number, name, msg, skip=False):
    """Confirm an action on an environment.

    :param account number: Account number of environment
    :type account number: str
    :param name: Name of the environment
    :type name: str
    :param msg: Message to display when asking for input.
    :type msg: str
    :param skip: Whether or not to skip bypass
    :type skip: bool
    :returns: Whether or not remove is confirmed.
    :rtype: bool
    """
    confirmed = skip
    if not confirmed:
        msg = '{} (y/n) --> '.format(msg)
        resp = ''
        while (resp != 'y' and resp != 'n'):
            resp = input(msg).lower()
        confirmed = (resp == 'y')
    return confirmed


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
