import yaml

from cloud_snitch import settings
from cloud_snitch.cli_common import base_parser

from neo4j.v1 import GraphDatabase


def get_neo4j():
    """Get instance of neo4j.

    :returns: Instance of graph database driver
    :rtype: GraphDatabase.driver
    """
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    return driver


def display(row):
    """Simple display function for a an environment.

    Prints uuid, account_number, and name

    :param row: Neo4j record
    :type row: ?
    """
    print("{} {} {}".format(
        row['uuid'],
        row['account_number'],
        row['name'])
    )


def list_all(args):
    """List all uuid, account_number, name for all environments.

    :param args: argparser namespace
    :type args: namespace.
    """
    driver = get_neo4j()
    with driver.session() as session:

        cipher = "MATCH (e:Environment)"

        if (args.missing):
            cipher += ' WHERE e.uuid IS NULL'

        cipher += (
            " RETURN"
            "   e.uuid AS `uuid`,"
            "   e.account_number AS `account_number`,"
            "   e.name AS `name` ORDER BY "
        )
        if args.sort == 'uuid':
            cipher += "`uuid`"
        else:
            cipher += "`name`"
        with session.begin_transaction() as tx:
            rows = tx.run(cipher)
            for row in rows:
                display(row)


def show_one(args):
    """Show uuid, name, and account number for one environment.

    :param args: argparser namespace
    :type args: namespace
    """
    driver = get_neo4j()
    params = {}

    cipher = "MATCH (e:Environment) WHERE "

    if args.uuid:
        params['uuid'] = args.uuid
        cipher += "e.uuid = $uuid"
    else:
        if not args.account_number or not args.name:
            print(
                "Account number and name must be provided "
                "if not using a uuid."
            )
            exit()

        params['account_number'] = args.account_number
        params['name'] = args.name
        cipher += "e.account_number = $account_number AND e.name = $name"

    cipher += (
        " RETURN e.uuid AS `uuid`, "
        "e.account_number AS `account_number`, "
        "e.name AS `name`"
    )

    count = 0
    with driver.session() as session:
        with session.begin_transaction() as tx:
            rows = tx.run(cipher, **params)
            for row in rows:
                display(row)
                count += 1
            if not count:
                print("No matches found.")


def set_uuid(account_number, name, uuid):
    """Set uuid for an environment located by account number and name.

    :param args: Argparser namespace
    :type args: namespace
    """
    if not account_number or not name:
        print("Account number and name are required.")

    driver = get_neo4j()
    params = dict(account_number=account_number, name=name)

    with driver.session() as session:
        with session.begin_transaction() as tx:
            # Find an environment by account number and name
            cipher = (
                'MATCH (e:Environment) WHERE e.name = $name '
                'AND e.account_number = $account_number '
                'RETURN e.uuid as `uuid` LIMIT 1'
            )
            row = tx.run(cipher, **params).single()
            if not row:
                print(
                    (
                        "Unable to locate an environment with account number "
                        "{} and name {}."
                    ).format(account_number, name)
                )
                return

            # Check that uuid is not already present
            if row['uuid'] is not None:
                print(
                    (
                        "Environment with account number {} and name {} "
                        "already has uuid {}"
                    ).format(account_number, name, row['uuid'])
                )
                return

            # If not present, set the uuid
            cipher = (
                'MATCH (e:Environment) '
                'WHERE '
                '  e.name = $name AND '
                '  e.account_number = $account_number '
                'MATCH (el:EnvironmentLock) '
                'WHERE '
                '  el.name = $name AND '
                '  el.account_number = $account_number '
                'SET e.uuid = $uuid, el.uuid = $uuid'
            )
            params['uuid'] = uuid
            result = tx.run(cipher, **params)
            print(
                "Changed {} properties."
                .format(result.summary().counters.properties_set)
            )


def set_one_uuid(args):
    """Set one uuid for an environment.

    :param args: Argparse namespace object with account_number, name, and uuid
    :type args: namespace
    """
    set_uuid(args.account_number, args.name, args.uuid)


def set_uuids_from_yaml(args):
    """Set uuids from a yaml mapping. Useful for migration to uuids.

    :param args: Argparse namespace object with filename
    :type args: namespace
    """
    with open(args.filename, 'r') as f:
        mapping = yaml.safe_load(f)

    for uuid, envdict in mapping.items():
        print("{} {} ==> {}".format(
            envdict['account_number'], envdict['name'], uuid
        ))
        if not args.list:
            set_uuid(str(envdict['account_number']), envdict['name'], uuid)
            print("")


def main():
    parser = base_parser(
        description=(
            "Tools for adding/viewing uuids on environments in preparation "
            "for migration from account_number_name to uuid."
        )
    )

    subparsers = parser.add_subparsers()

    # Parser for listing all environments.
    show_parser = subparsers.add_parser('list', help="List environments.")
    show_parser.add_argument(
        '--sort', '-s',
        help='Sort by uuid|account_number and name',
        choices=['uuid', 'name'],
        default='name'
    )
    show_parser.add_argument('--missing', action='store_true', default=False)
    show_parser.set_defaults(func=list_all)

    # Parser for show one environment
    get_parser = subparsers.add_parser('show', help="Show one environment.")
    get_parser.add_argument('--uuid', type=str, help="uuid of environment.")
    get_parser.add_argument(
        '--account-number',
        type=str,
        help="account_number of the environment."
    )
    get_parser.add_argument(
        '--name',
        type=str,
        help="Name of the environment."
    )
    get_parser.set_defaults(func=show_one)

    # Parser for setting a single uuid
    set_uuid_parser = subparsers.add_parser(
        'set-uuid',
        help=(
            "Set uuid on an environment. "
            "Locate environment by account number and name."
        )
    )
    set_uuid_parser.add_argument(
        '--account-number',
        type=str,
        help="account_number of the environment."
    )
    set_uuid_parser.add_argument(
        '--name',
        type=str,
        help="Name of the environment."
    )
    set_uuid_parser.add_argument(
        'uuid',
        type=str
    )
    set_uuid_parser.set_defaults(func=set_one_uuid)

    # Parser for setting multiple uuids.
    set_uuids_parser = subparsers.add_parser(
        'set-uuids',
        help=(
            "Set uuids for multiple environments. "
            "Mapping is provided via a yaml file."
        )
    )
    set_uuids_parser.add_argument(
        'filename',
        type=str,
        help="Location to yaml file containing mapping."
    )
    set_uuids_parser.add_argument(
        '--list',
        action="store_true",
        default=False,
        help="Examine yaml contents."
    )
    set_uuids_parser.set_defaults(func=set_uuids_from_yaml)

    # Run subcommand
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
