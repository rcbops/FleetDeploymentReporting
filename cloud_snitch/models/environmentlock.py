import logging

from .base import versioned_properties
from .base import VersionedEntity
from .base import VersionedProperty
from cloud_snitch import utils
from cloud_snitch.exc import EnvironmentLockedError

logger = logging.getLogger(__name__)


@versioned_properties
class EnvironmentLockEntity(VersionedEntity):
    """Model an environment lock in the graph.

    A lock on an environment exists if the locked property for an
    environmentlock node is not null.
    """

    label = 'EnvironmentLock'
    state_label = 'EnvironmentLockState'
    properties = {
        'uuid': VersionedProperty(is_identity=True),
        'account_number': VersionedProperty(is_static=True),
        'name': VersionedProperty(is_static=True),
        'locked': VersionedProperty(is_static=True, type=int)
    }

    @classmethod
    def lock(cls, session, uuid, account_number, name):
        """Locks an environment with matching uuid.

        Lock is obtained in a single transaction.

        :param session: neo4j driver session
        :type session: neo4j.v1.session.BoltSession
        :param uuid: Environment uuid.
        :type uuid: str
        :param account_number: Account number
        :type account_number: str
        :param name: Name of the environment.
        :type name: str
        :returns: The time of the lock in milliseconds. This will be
            used as the key to release the lock
        :rtype: int
        """
        lock_time = utils.milliseconds_now()
        with session.begin_transaction() as tx:
            instance = cls.find_transaction(tx, uuid)
            if instance is None:
                # No node found, create the node
                instance = cls(
                    uuid=uuid,
                    account_number=account_number,
                    name=name,
                    locked=lock_time
                )
                instance._update(tx, lock_time)
            elif instance.locked == 0:
                instance.locked = lock_time
                instance._update(tx, lock_time)
            else:
                # Raise exception. The node exists and locked is not none
                raise EnvironmentLockedError(instance)
        return lock_time

    @classmethod
    def release(cls, session, uuid, key):
        """Releases the lock on an environment.

        :param session: neo4j driver session
        :type session: neo4j.v1.session.BoltSession
        :param account_number: Environment account number
        :type account_number: str
        :param name: Environment name
        :type name: str
        :param key: Time of the lock in milliseconds
        :type key: int
        :returns: True for lock released or no action, False otherwise
        :rtype: bool
        """
        release_time = utils.milliseconds_now()
        with session.begin_transaction() as tx:
            instance = cls.find_transaction(tx, uuid)

            # Check for empty result
            if instance is None:
                # No node found, no instance to unlock
                return True

            # Check for instance is locked
            elif instance.locked:
                # If the instance is locked, the key must match the lock time
                if key == instance.locked:
                    instance.locked = 0
                    instance._update(tx, release_time)
                    return True
                # If the key does not match then do not release lock
                else:
                    return False

            # Nothing to release if this far
            return True
