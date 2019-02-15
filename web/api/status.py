import logging

from django.core.cache import cache as django_cache
from neo4jdriver.connection import get_connection

logger = logging.getLogger(__name__)

STATUS_QUERY = """
CALL dbms.queryJmx("org.neo4j:instance=kernel#0,name=Store file sizes")
    YIELD attributes
    WITH KEYS(attributes) AS k, attributes
    UNWIND k AS `row`
    RETURN
        "store_size" AS `type`,
        `row`,
        attributes[row]["value"] as `value`
    ORDER BY `row`

UNION ALL

CALL dbms.queryJmx("org.neo4j:instance=kernel#0,name=Primitive count")
    YIELD attributes
    WITH KEYS(attributes) AS k, attributes
    UNWIND k AS `row`
    RETURN
        "id_allocation" as `type`,
         `row`,
         attributes[row]["value"] as `value`
    ORDER BY `row`
"""


def cache():
    """Tests that a value can be retrieved from cache.

    :returns: Dictionary indicating results. {'status': True}
    :rtype: dict
    """
    key = 'test_cache_key'
    val = 'test_cache_val'
    result = dict(status=None)
    try:
        django_cache.add(key, val, 3600)
        cache_val = django_cache.get(key)
        if cache_val == val:
            result['status'] = True
    except Exception as e:
        result['status'] = False
    return result


def neo4j():
    """Tests that neo4j is queryable.

    Also requests stats from neo4j.

    :returns: Dictionary indicating results.
    :rtype: dict
    """
    result = dict(status=None, stats={})
    try:
        with get_connection().session() as session:
            with session.begin_transaction() as tx:
                resp = tx.run(STATUS_QUERY)
                for row in resp:
                    d = result['stats'].setdefault(row['type'], {})
                    d[row['row']] = row['value']
        result['status'] = True
    except Exception:
        result['status'] = False
    return result


def combined():
    """Runs all status checks.

    Returns a tuple of (true/false, stats dict)
    True indicates all status good.

    :returns: Status tuple
    :rtype: tuple
    """
    stats = {}
    for func in [cache, neo4j]:
        stats.update({func.__name__: func()})
    return (
        all([d.get('status') for d in stats.values()]),
        stats
    )
