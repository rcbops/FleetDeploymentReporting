import base64
import json
import logging
import os
import struct
import tarfile

from cloud_snitch import utils
from cloud_snitch.exc import ArchiveObjectError
from cloud_snitch.exc import InvalidKeyError
from cloud_snitch.exc import RunAlreadySyncedError
from cloud_snitch.exc import RunInvalidError
from cloud_snitch.exc import RunInvalidStatusError

from Crypto.Cipher import AES

logger = logging.getLogger(__name__)


_CURRENT_RUN = None


class RunArchive:
    """Class for reading optionally encrypted run data json files.

    The archive must be .tar.gz

    """
    encoding = 'utf-8'

    def __init__(self, filename, key=None, mode='r:gz'):
        """Initialize the file object.

        :param filename: Filename of archive
        :type filename: str
        :param key: Base64 encoded AES 256 key
        :type key: str
        :param mode: Tarfile read mode (r:gz, r:*, etc)
        :type mode: string
        """
        self.filename = filename

        # Prepare key if provided.
        self.key = key
        if self.key is not None:
            try:
                self.key = base64.b64decode(self.key)
            except Exception:
                raise InvalidKeyError()

        self.mode = mode
        self.filemap = {}

        # Build the file map
        tf = None
        try:
            tf = tarfile.open(self.filename, self.mode)
            for name in tf.getnames():
                _, tail = os.path.split(name)
                self.filemap[tail] = name
        finally:
            if tf:
                tf.close()

    def read(self, membername):
        """Read data from a file.

        Will decrypt if enabled.
        Will return string.

        :returns: Unserialized json object
        :rtype: dict
        """
        tf = None
        try:
            fullname = self.filemap.get(membername, '')
            tf = tarfile.open(self.filename, self.mode)
            f = tf.extractfile(fullname)
            if self.key:
                # Read original bytes length first
                length = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]

                # Read initialization vector next
                iv = f.read(AES.block_size)
                cipher = AES.new(self.key, AES.MODE_CBC, iv)

                # Read and decrypt rest of string.
                decrypted = cipher.decrypt(f.read())

                # Remove padding
                data = decrypted[:length]
            else:
                data = f.read()

            # Return decoded string.
            return json.loads(data.decode(self.encoding))

        except ValueError:
            raise ArchiveObjectError(membername)

        finally:
            if tf:
                tf.close()


class Run:
    """Models a running of the collection of data."""

    def __init__(self, path, key=None):
        """Inits the run

        :param path: Path on disk that contains the run
        :type path: str
        :param key: Encryption key to encrypt and decrypt run data
        :type key: base64 encoded AES256 key.
        """
        self.path = path
        try:
            self.archive = RunArchive(self.path, key=key)
            self.run_data = self._read_data()
        except FileNotFoundError:
            raise RunInvalidError(self.path)
        except IOError:
            raise RunInvalidError(self.path)
        except ValueError:
            raise RunInvalidError(self.path)
        self._completed = None

    @property
    def filenames(self):
        """List names of files in the run archive.

        :returns: List of tails of all filenames in the archive.
        :rtype: list
        """
        return self.archive.filemap.keys()

    def _read_data(self):
        """Reads run data.

        :returns: Run data loaded from file.
        :rtype: dict
        """
        return self.get_object('run_data.json')

    def get_object(self, filename):
        """Get deserialized json object from a file in the run.

        :param filename: Name of the file containing the object.
        :type filename: str
        :returns: The object if it exists or None
        :rtype: Dict|None
        """
        return self.archive.read(filename)

    @property
    def completed(self):
        """Get completed datetime

        :returns: The completed datetime str
        :rtype: str|None
        """
        if self._completed is None:
            try:
                raw = self.run_data.get('completed')
                self._completed = utils.strtodatetime(raw)
            except Exception:
                self._completed = None
        return self._completed

    @property
    def synced(self):
        """Get synced datetime

        :returns: The synced datetime
        :rtype: datetime
        """
        synced = self.run_data.get('synced')
        if synced is not None:
            try:
                synced = utils.strtodatetime(synced)
            except Exception:
                synced = None
        return synced

    @property
    def status(self):
        """Get status of the run.

        Status should be 'finished' before it can be synced.

        :returns: Status of the run
        :rtype: str
        """
        return self.run_data.get('status')

    @property
    def environment_account_number(self):
        """Get account number associated with the run.

        :returns: Account number
        :rtype: str
        """
        return self.run_data.get('environment', {}).get('account_number')

    @property
    def environment_name(self):
        """Get name of the environment.

        :returns: Name of the environment.
        :rtype: str
        """
        return self.run_data.get('environment', {}).get('name')

    @property
    def environment_uuid(self):
        """Get the uuid of the environment.

        :returns: Uuid of the environment.
        :rtype: str
        """
        return self.run_data.get('environment', {}).get('uuid')

    def update(self):
        """Reload data from disk."""
        self.run_data = self._read_data()

    def start(self):
        """Execution hook for start of a run."""
        self.update()
        if self.status != 'finished':
            raise RunInvalidStatusError(self)
        if self.run_data.get('synced') is not None:
            raise RunAlreadySyncedError(self)

    def finish(self):
        """Execute hook for successful sync."""
        pass

    def error(self):
        """Execute hook for unsuccessful sync."""
        pass


def set_current(run):
    """Set the current run

    :param run: Run instance object
    :type run: Run
    """
    global _CURRENT_RUN
    _CURRENT_RUN = run


def get_current():
    """Get the current run

    Used for context purposes.

    :returns: Current run instance
    :rtype: Run
    """
    return _CURRENT_RUN


def unset_current():
    """Unset the current run."""
    set_current(None)
