from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64
import datetime
import json
import os
import struct
import uuid
import yaml
from Crypto.Cipher import AES

try:
    from ansible.plugins.callback import CallbackBase
except ImportError:
    class CallbackBase(object):
        def __init__(self, *args, **kwargs):
            pass

# Attempt to load configuration from file
conf_file = os.environ.get(
    'CLOUD_SNITCH_CONF_FILE',
    '/etc/cloud_snitch/cloud_snitch.yml')
with open(conf_file, 'r') as f:
    settings = yaml.load(f.read())

# Merge in configuration from environment variables.
var_map = {
    'enabled': {
        'name': 'CLOUD_SNITCH_ENABLED',
        'required': False
    },
    'environment.account_number': {
        'name': 'CLOUD_SNITCH_ENVIRONMENT_ACCOUNT_NUMBER',
        'required': True
    },
    'environment.name': {
        'name': 'CLOUD_SNITCH_ENVIRONMENT_NAME',
        'required': True
    },
    'environment.uuid': {
        'name': 'CLOUD_SNITCH_ENVIRONMENT_UUID',
        'required': True,
    },
    'run_id': {
        'name': 'CLOUD_SNITCH_RUN_ID',
        'required': False
    },
    'crypt_enabled': {
        'name': 'CLOUD_SNITCH_CRYPT_ENABLED',
        'required': False
    },
    'crypt_key': {
        'name': 'CLOUD_SNITCH_CRYPT_KEY',
        'required': False
    }
}
for key, var_dict in var_map.items():
    val = os.environ.get(var_dict['name'])
    if not val and var_dict['required']:
        raise Exception('{} not set.'.format(var_dict['name']))
    settings[key] = val

DOCUMENTATION = '''
    callback: snitcher
    short_description: Gathers output from cloud snitch modules
    version_added: "2.1.6"
    description:
      - This callback dumps apt_sniffer module results to a file
      - Environment Variable CLOUD_SNITCH_ENABLED
      - Environment Variable CLOUD_SNITCH_CONF_FILE
      - Environment Variable CLOUD_SNITCH_CRYPT_ENABLED (for encryption)
      - Environment Variable CLOUD_SNITCH_CRYPT_KEY (for encryption)
      - Environment Variable CLOUD_SNITCH_RUN_ID
      - Environment Variable CLOUD_SNITCH_ENVIRONMENT_ACCOUNT_NUMBER
      - Environment Variable CLOUD_SNITCH_ENVIRONMENT_NAME
      - Environment Variable CLOUD_SNITCH_ENVIRONMENT_UUID
    requirements:
'''


class File:
    """Class for writing or reading optionally encrypted data.

    Encryption is configured via by the environment variables:
        CLOUD_SNITCH_CRYPT_ENABLED
        CLOUD_SNITCH_CRYPT_KEY
    """
    encoding = 'utf-8'
    valid_enabled = ['true', '1', 'yes']

    def __init__(self, filename):
        """Initialize the file object.

        :param filename: Filename to read from or write to
        :type filename: str
        """
        self.filename = filename

        # crypt_enabled is only true if environment var is some
        crypt_enabled = settings.get('crypt_enabled')
        crypt_enabled = crypt_enabled.lower()
        self.crypt_enabled = crypt_enabled in self.valid_enabled

        # Retrieve crypt key and base64 decode it.
        self.crypt_key = settings.get('crypt_key')
        self.crypt_key = base64.b64decode(self.crypt_key)

        if self.crypt_enabled and not self.crypt_key:
            raise Exception("Crypt is enabled but no key is configured.")

    def _pad(self, b):
        """Pad the string s to be a multiple of AES.block_size.

        :param b: Bytes to pad
        :type b: bytes
        :returns: length of b, padded bytes
        :rtype: tuple
        """
        length = len(b)
        pad_length = AES.block_size - (length % AES.block_size)
        padded = b + ("\0" * pad_length).encode(self.encoding)
        return length, padded

    def write(self, data):
        """Write data to a file.

        Will convert to bytes and will encrypt if enabled.

        :param data: String to write.
        :type data: str
        """
        # Convert data string to bytes
        data = data.encode(self.encoding)

        # Create initialization vector and cipher text if crypt enabled.
        if self.crypt_enabled:
            iv = os.urandom(AES.block_size)
            length, padded = self._pad(data)
            cipher = AES.new(self.crypt_key, AES.MODE_CBC, iv)
            data = struct.pack('<Q', length) + iv + cipher.encrypt(padded)

        # Write to file.
        with open(self.filename, 'wb') as f:
            f.write(data)

    def read(self):
        """Read data from a file.

        Will decrypt if enabled.
        Will return string.

        :returns: Data from file as string
        :rtype: str
        """
        with open(self.filename, 'rb') as f:
            if self.crypt_enabled:
                # Read original bytes length first
                length = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]

                # Read initialization vector next
                iv = f.read(AES.block_size)
                cipher = AES.new(self.crypt_key, AES.MODE_CBC, iv)

                # Read and decrypt rest of string.
                decrypted = cipher.decrypt(f.read())

                # Remove padding
                data = decrypted[:length]
            else:
                data = f.read()

            # Return decoded string.
            return data.decode(self.encoding)


class FileHandler:

    def __init__(self, writedir):
        """Init the file handler

        :param writedir: Directory to write to
        :type writedir: str
        """
        self.basedir = writedir
        if self.basedir is None:
            raise Exception("No data directory configured.")

        self._doc = {
            'environment': {
                'account_number': settings.get('environment.account_number'),
                'name': settings.get('environment.name'),
                'uuid': settings.get('environment.uuid')
            }
        }

    def _save(self):
        """Save contents of _doc to file.

        Data is encoded as json.
        """
        data = json.dumps(self._doc)
        f = File(self._outfile_name)
        f.write(data)

    def handle(self, doctype, host, result):
        """Writes payload as json to file.

        Stores md5 of json. Used to determine if change
        has occurred.

        Filenames will be:
            <doctype>_<host>.json, <doctype>_<host>.json


        :param doctype: Type of the document.
        :type doctype: str
        :param host: The host
        :type host: str
        :param result: The output result from ansible task
        :type result: dict
        """
        outfile_name = '{}_{}.json'.format(doctype, host)
        self._outfile_name = os.path.join(self.basedir, outfile_name)
        self._doc['host'] = host
        self._doc['data'] = result.get('payload', {})
        self._save()


class SingleFileHandler(FileHandler):

    filename_prefix = 'single'

    def handle(self, doctype, host, result):
        """Handles a a single file output from a snitch.

        Should only be called on one host. The execution will happen
        on the deployment host.

        Stored files will be:
            <filename_prefix>.json, <filename_prefix>.md5

        :param doctype: Type of document
        :type doctype: str
        :param host: Unused
        :type host: str
        :param result: Result of task|action
        :type result: dict
        """
        outfile_name = '{}.json'.format(self.filename_prefix)
        self._outfile_name = os.path.join(self.basedir, outfile_name)
        self._doc['data'] = result.get('payload', {})
        self._save()


class GitFileHandler(SingleFileHandler):
    filename_prefix = 'gitrepos'


class UservarsHandler(SingleFileHandler):
    filename_prefix = 'uservars'


TARGET_DOCTYPES = [
    'configuredinterface',
    'dpkg_list',
    'facts',
    'file_dict',
    'gitrepos',
    'kernelmodules',
    'pip_list',
    'uservars'
]

DOCTYPE_HANDLERS = {
    'configuredinterface': FileHandler,
    'dpkg_list': FileHandler,
    'facts': FileHandler,
    'file_dict': FileHandler,
    'gitrepos': GitFileHandler,
    'kernelmodules': FileHandler,
    'pip_list': FileHandler,
    'uservars': UservarsHandler,
}


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_NAME = 'snitcher'

    TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

    def __init__(self, display=None):
        """Enables or disables plugin based on environment."""
        super(CallbackModule, self).__init__(display)
        self.basedir = settings.get('data_dir')
        if settings.get('enabled'):
            self.disabled = False
            if not self.basedir:
                raise Exception("No data directory configured.")
        else:
            self.disabled = True

    def runner_on_ok(self, host, result):
        """Runs on every task completion.

        Handles data emissions from task completions.

        :param host: Host name
        :type host: str
        :param result: Result from task
        :type result: dict
        """
        doctype = result.get('doctype')
        if doctype not in TARGET_DOCTYPES:
            return
        handler = DOCTYPE_HANDLERS.get(doctype, FileHandler)
        handler(self.dirpath).handle(doctype, host, result)

    def _run_data_filename(self):
        """Compute filename of run data.

        :returns: Name of the file
        :rtype: str
        """
        return os.path.join(self.dirpath, 'run_data.json')

    def _write_run_data(self, data):
        """Writes information about the run.

        :param data: Data to save
        :type data: dict
        """
        f = File(self._run_data_filename())
        f.write(json.dumps(data))

    def _read_run_data(self):
        """Read information about the run

        :returns: Loaded data
        :rtype: dict
        """
        text = File(self._run_data_filename()).read()
        return json.loads(text)

    def playbook_on_start(self):
        """Start new directory."""
        # Name the new directory according to run id
        now = datetime.datetime.utcnow()
        run_id = settings.get('run_id') or str(uuid.uuid4())
        self.dirpath = os.path.join(self.basedir, run_id)

        # Create the new directory
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)

        # Saved some stats
        self._write_run_data({
            'status': 'running',
            'started': now.isoformat(),
            'environment': {
                'account_number': settings.get('environment.account_number'),
                'name': settings.get('environment.name'),
                'uuid': settings.get('environment.uuid')
            }
        })

    def playbook_on_stats(self, stats):
        """Used as a on_playbook_end."""
        now = datetime.datetime.utcnow()

        # Get saved data
        data = self._read_run_data()

        # Update data and then save it
        data['status'] = 'finished'
        data['completed'] = now.isoformat()
        self._write_run_data(data)
