import base64
import os

from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host

__metaclass__ = type

DOCUMENTATION = '''
    vars: crypto_vars
    version_added: "2.4"
    short_description: Generates random one time use crypto keys
    description:
        - Generates 256 bit AES keys that are base64 encoded.
        - Vars are provided as crypto_aes_key/
'''

KEY_SIZE = 32
CACHE = {}


class VarsModule(BaseVarsPlugin):

    def gen_key(self):
        """Generate base64 encoded AES key."""
        return base64.b64encode(os.urandom(KEY_SIZE)).decode('utf-8')

    def get_vars(self, loader, path, things, cache=False):
        """Generates crypto key."""
        data = {}
        if not isinstance(things, list):
            things = [things]

        for thing in things:
            prefix = 'host_' if isinstance(thing, Host) else 'group_'
            cache_key = prefix + thing.name
            crypt_key = CACHE.get(cache_key)
            if crypt_key is None:
                crypt_key = self.gen_key()
                CACHE[cache_key] = crypt_key
            data.update(crypto_aes_key=crypt_key)
        return data
