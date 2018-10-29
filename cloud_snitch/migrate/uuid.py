import time

from cloud_snitch.cli_common import base_parser
from cloud_snitch.migrate.cli_uuid import get_neo4j
from cloud_snitch.models import registry
from cloud_snitch.utils import EOT

from neo4j.exceptions import DatabaseError


class Property:
    """Models a property of a label."""
    def __init__(self, label, prop):
        self.label = label
        self.property = prop

    def __str__(self):
        return '{}.{}'.format(self.label.lower(), self.property)


class IdentityChangeQuery:
    """Models a query to change the identity of nodes in a subgraph."""

    delimiter = '_'

    def __init__(self, label, identity_properties, path):
        """Init the query.

        :param label: Name of the label
        :type label: str
        :param identity_properties: Collection of properties
        :type identity_properties: tuple|list
        :param path: Path to the label(usually from the registry)
        :type path: List of label, reltype tuples
        """
        self.label = label
        self.identity_properties = identity_properties
        self.path = path

    def match_clause(self):
        """Builds the match portion of the query.

        :returns: Match clause of a statement
        :rtype: str
        """
        cipher = 'MATCH '
        for label, reltype in self.path:
            cipher += '({}:{})-[:{}]->'.format(
                self.var_from_label(label), label, reltype
            )
        cipher += '({}:{})'.format(self.var_from_label(self.label), self.label)
        return cipher

    def set_clause(self):
        """Builds the set clause of the query.

        :returns: Set clause of the query.
        :rtype: str
        """
        value = []
        for prop in self.identity_properties:
            value.append(str(prop))
        value = ' + \'_\' + '.join(value)
        cipher = 'SET {}.{} = {}'.format(
            self.var_from_label(self.label),
            registry.identity_property(self.label),
            value
        )
        return cipher

    def __str__(self):
        """Combines clauses into one string.

        :returns: Entire query
        :rtype: str
        """
        return self.match_clause() + ' ' + self.set_clause()

    @classmethod
    def var_from_label(cls, label):
        """Convenience method for referencing query variables.

        :param label: Name of the label
        :type label: str
        :returns: Transformed label name
        :rtype: str
        """
        return label.lower()


def validate_environments():
    """Check that there are no environments without uuids.

    :return: True for all environments have uuids, False otherwise
    :rtype: bool
    """
    driver = get_neo4j()
    cipher = (
        'MATCH (e:Environment) '
        'WHERE e.uuid is NULL RETURN COUNT(*) as `count`'
    )
    with driver.session() as session:
        with session.begin_transaction() as tx:
            resp = tx.run(cipher).single()
            count = resp['count']
    return count == 0


def cleanup():
    """Generate queries to clean up account number name.

    Creates a query to drop the account number name constraint.
    Creates a query to remove the account number name properties.
    """
    yield (
        "DROP CONSTRAINT ON (environment:Environment) "
        "   ASSERT environment.account_number_name IS UNIQUE;"
    )
    yield (
        "DROP CONSTRAINT ON (environmentlock:EnvironmentLock) "
        "   ASSERT environmentlock.account_number_name IS UNIQUE;"
    )
    yield "MATCH (e:Environment) SET e.account_number_name = NULL"
    yield "MATCH (e:EnvironmentLock) SET e.account_number_name = NULL"


def add_state():
    """Generate query to add the first environment state node

    Should only occur for environments that do not already have state.
    The from property of the HAS_STATE relationship should be the environment's
    created_at property. The to property should be the java end of time.

    The last_synced property of the state should by the created_at property.
    The status property should be 'migrated for uuid'.

    :returns: Cipher query to add state to stateless environments.
    :rtype: str
    """
    cipher = """
        MATCH (e:Environment) WHERE NOT (e)-[:HAS_STATE]-()
        CREATE (e)
            -[r:HAS_STATE {{to: {}, from: e.created_at}}]
            ->(firstState:EnvironmentState {{
                last_sync: e.created_at,
                status: 'migrated_for_uuid'
            }})
    """
    cipher = cipher.format(EOT)
    return cipher


def execute(query):
    """Executes an identity change query.

    :param query: Instance of an identity change query
    :type query: IdentityChangeQuery
    """
    driver = get_neo4j()
    cipher = str(query)

    with driver.session() as session:
        with session.begin_transaction() as tx:
            start = time.time()
            summary = tx.run(cipher).summary()
            changed = summary.counters.properties_set
            print(
                "\nExecuted the following query:\n{}\n"
                "Changed {} properties in {:.3f}s"
                .format(str(query), changed, time.time() - start)
            )
            print("Summary: {}".format(summary.counters))


if __name__ == '__main__':
    parser = base_parser(
        description=(
            "Migration script to convert to environment uuids. "
            "All environments must have uuids."
        )
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=2000,
        help="Number of rows to consider at a time."
    )

    parser.add_argument(
        '--cipher-only',
        action="store_true",
        default=False,
        help="Print only the cipher for migration."
    )

    args = parser.parse_args()
    # Check that all environments have uuids before migrating
    if not validate_environments():
        print(
            "There are environments without uuids. "
            "Please set uuids before migrating."
        )
        exit()

    label_tuples = [
        # 'AptPackage', # No action for apt packages
        # 'Environment', # No action for environments.
        #   will be modified separately
        # 'GitUntrackedFile', # No action for untracked files.
        # 'GitUrl', # No action for git urls
        # 'NameServer', # No action needed for name servers
        # 'PythonPackage', # No action for python packages
        (
            'Configfile',
            (
                Property('Configfile', 'path'),
                Property('Host', 'hostname_environment')
            )
        ),
        (
            'ConfiguredInterface',
            (
                Property('ConfiguredInterface', 'device'),
                Property('Host', 'hostname_environment')
            )
        ),
        (
            'Device',
            (
                Property('Device', 'name'),
                Property('Host', 'hostname_environment')
            )
        ),
        (
            'GitRemote',
            (
                Property('GitRemote', 'name'),
                Property('GitRepo', 'path_environment')
            )
        ),
        (
            'GitRepo',
            (
                Property('GitRepo', 'path'),
                Property('Environment', 'uuid')
            )
        ),
        (
            'Host',
            (
                Property('Host', 'hostname'),
                Property('Environment', 'uuid')
            )
        ),
        (
            'Interface',
            (
                Property('Interface', 'device'),
                Property('Host', 'hostname_environment')
            )
        ),
        (
            'Mount',
            (
                Property('Mount', 'mount'),
                Property('Host', 'hostname_environment')
            )
        ),
        (
            'Partition',
            (
                Property('Partition', 'name'),
                Property('device', 'name_host')
            )
        ),
        (
            'Uservar',
            (
                Property('Uservar', 'name'),
                Property('Environment', 'uuid')
            )
        ),
        (
            'Virtualenv',
            (
                Property('Virtualenv', 'path'),
                Property('Host', 'hostname_environment')
            )
        )
    ]

    label_tuples = [(l, p, registry.path(l)) for l, p in label_tuples]
    label_tuples.sort(key=lambda x: len(x[2]))
    queries = [IdentityChangeQuery(*t) for t in label_tuples]

    if args.cipher_only:
        for query in queries:
            print(query)
        for query in cleanup():
            print(query)
        print(add_state())
        exit()

    # Perform migration
    for q in queries:
        execute(q)

    # Remove account_number_name property from environments.
    # Remove constraint on account_number_name for environment
    for q in cleanup():
        try:
            execute(q)
        except DatabaseError as dbe:
            print(
                "\nFound exception {} when running the query:\n{}\n"
                .format(dbe, q)
            )

    # Finally initialize the first environment states.
    execute(add_state())
