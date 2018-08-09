import logging

from cloud_snitch.models import registry
from neo4jdriver.connection import get_connection

logger = logging.getLogger(__name__)


class TimesQuery:
    """Class for querying the times an object tree has changed."""

    def __init__(self, label, identity):
        self.label = label
        self.identity = identity
        self.params = {'identity': identity}

    def __str__(self):
        var = self.label.lower()
        identity_prop = registry.identity_property(self.label)
        cypher = "MATCH p = ({}:{})-[*]->(other)".format(var, self.label)
        cypher += "\nWHERE {}.{} = $identity".format(var, identity_prop)
        cypher += "\nWITH relationships(p) as rels"
        cypher += "\nUNWIND rels as r"
        cypher += "\nreturn DISTINCT r.from as t"
        cypher += "\nORDER BY t DESC"
        return cypher

    def _fetch(self):
        q = str(self)
        logger.debug("Running query:\n{}".format(str(q)))
        with get_connection().session() as session:
            with session.begin_transaction() as tx:
                resp = tx.run(q, **self.params)
                return resp

    def fetch(self):
        times = [record['t'] for record in self._fetch()]
        return times
