import uuid

from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host

__metaclass__ = type

DOCUMENTATION = '''
    vars: run_vars
    version_added: "2.4"
    short_description: Generates a unique id per run
    description:
        - Generates a uuid
        - Vars are provided as run_id
'''

CACHE = {}


class VarsModule(BaseVarsPlugin):

    def get_vars(self, loader, path, things, cache=False):
        """Generates uuid to identity a run."""
        data = {}

        if not isinstance(things, list):
            things = [things]

        for thing in things:
            prefix = 'host_' if isinstance(thing, Host) else 'group_'
            key = prefix + thing.name
            run_id = CACHE.get(key)
            if run_id is None:
                run_id = str(uuid.uuid4())
                CACHE[key] = run_id
            data.update(run_id=run_id)
        return data
