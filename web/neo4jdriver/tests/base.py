import logging

logging.getLogger('neo4j').setLevel(logging.ERROR)
logging.getLogger('api').setLevel(logging.ERROR)
logging.getLogger('api.query').setLevel(logging.ERROR)
logging.getLogger('django').setLevel(logging.ERROR)
