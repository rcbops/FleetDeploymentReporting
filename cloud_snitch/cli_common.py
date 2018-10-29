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


def confirm_env_action(msg, skip=False):
    """Confirm an action on an environment.

    :param env: Environment object
    :type env: EnvironmentEntity
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


def find_environment(session, uuid):
    """Find an environment by uuid.

    :param session: neo4j driver session
    :type session: neo4j.v1.session.BoltSession
    :param uuid: UUID of the environment
    :type uuid: str
    :returns: Environment entity
    :rtype: EnvironmentEntity
    """
    env = EnvironmentEntity.find(session, uuid)
    if env is None:
        raise EnvironmentNotFoundError(uuid)
    return env
