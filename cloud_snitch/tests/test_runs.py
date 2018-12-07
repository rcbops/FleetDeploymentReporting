import base64
import datetime
import io
import json
import mock
import os
import pytz
import struct
import unittest

from cloud_snitch.exc import ArchiveObjectError
from cloud_snitch.exc import InvalidKeyError
from cloud_snitch.exc import RunInvalidError
from cloud_snitch.runs import Run
from cloud_snitch.runs import RunArchive
from Crypto.Cipher import AES


class FakeTarFile:

    def _pad(self, b):
        """Pad the string s to be a multiple of AES.block_size.

        :param b: Bytes to pad
        :type b: bytes
        :returns: length of b, padded bytes
        :rtype: tuple
        """
        length = len(b)
        pad_length = AES.block_size - (length % AES.block_size)
        padded = b + ("\0" * pad_length).encode('utf-8')
        return length, padded

    def contents(self, data):
        """Write contents to file like object and return value.

        :param data: Object to write
        :type data: dict
        :returns: encoded written data
        :rtype: bytes
        """
        s = io.BytesIO()
        data = json.dumps(data).encode('utf-8')
        if self.key:
            iv = os.urandom(AES.block_size)
            length, padded = self._pad(data)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            data = struct.pack('<Q', length) + iv + cipher.encrypt(padded)
        s.write(data)
        return s.getvalue()

    def fake_file(self, i):
        """Create a fake file with i as the value for the key value.

        :param i: Fake value
        :type i: int
        :returns: encoded(optionally encrypted) bytes
        :rtype: bytes
        """
        return self.contents({'value': i})

    def add_file(self, filename, data):
        new_contents = self.contents(data)
        if filename not in self.member_names:
            self.member_names.append(filename)
        self.member_files[filename] = new_contents

    def __init__(self, key=None):
        """Init the fake tar file."""
        self.member_names = []
        self.member_files = {}
        self.key = key
        if self.key:
            self.key = base64.b64decode(key)

        for i in range(10):
            name = '/some/path/file_{}'.format(i)
            self.member_names.append(name)
            self.member_files[name] = self.fake_file(i)

    def getnames(self):
        """Return names of member files.

        :returns: Names of member files
        :rtype: list
        """
        return self.member_names

    def extractfile(self, filename):
        """Get a file like object for matching file.

        :param filename: Name of memeber file
        :type filename: str
        :returns: File like object to read from
        :rtype: io.BytesIO
        """
        return io.BytesIO(self.member_files[filename])

    def close(self):
        """Empty method to simulate closing a tarfile."""
        pass


class TestRunArchive(unittest.TestCase):
    """Test the RunArchive class."""

    def test_invalid_key(self):
        """Assert that InvalidKeyError is raised."""
        key = {'hint': 'i am not a string'}
        with self.assertRaises(InvalidKeyError):
            RunArchive('somefile', key=key)

    @mock.patch('cloud_snitch.runs.tarfile.open', return_value=FakeTarFile())
    def test_file_names(self, m_tarfile):
        """Assert that run filemap contains only the tail of filenames."""
        ra = RunArchive('somefile')
        for i in range(10):
            name = 'file_{}'.format(i)
            self.assertTrue(name in ra.filemap)
        self.assertEqual(len(ra.filemap), 10)

    @mock.patch('cloud_snitch.runs.tarfile.open')
    def test_read_unencrypted(self, m_tarfile):
        """Test that reading unencrypted archive works."""
        m_tarfile.return_value = FakeTarFile(key=None)
        ra = RunArchive('somefile', key=None)
        for i in range(10):
            obj = ra.read('file_{}'.format(i))
            self.assertEqual(obj.get('value'), i)

    @mock.patch('cloud_snitch.runs.tarfile.open')
    def test_read_encrypted(self, m_tarfile):
        """Test that reading encrypted archive works."""
        key = base64.b64encode(('a' * 32).encode('utf-8'))
        m_tarfile.return_value = FakeTarFile(key=key)
        ra = RunArchive('somefile', key=key)
        for i in range(10):
            obj = ra.read('file_{}'.format(i))
            self.assertEqual(obj.get('value'), i)

    @mock.patch('cloud_snitch.runs.tarfile.open')
    def test_read_wrong_key(self, m_tarfile):
        """Test that reading encrypted archive with wrong key fails."""
        right_key = base64.b64encode(('a' * 32).encode('utf-8'))
        wrong_key = base64.b64encode(('b' * 32).encode('utf-8'))
        m_tarfile.return_value = FakeTarFile(key=right_key)
        ra = RunArchive('somefile', key=wrong_key)
        with self.assertRaises(ArchiveObjectError):
            ra.read('file_0')


class TestRun(unittest.TestCase):

    def setUp(self):
        """Set up some basic run data."""
        self.key = base64.b64encode(('a' * 32).encode('utf-8'))
        self.run_data = {
            'environment': {
                'account_number': '12345',
                'name': 'test_name',
                'uuid': 'test_uuid'
            },
            'status': 'test_status'
        }
        self.fake_tarfile = FakeTarFile(key=self.key)
        self.fake_tarfile.add_file('run_data.json', self.run_data)

    @mock.patch('cloud_snitch.runs.tarfile.open')
    def test_run_data_properties(self, m_tarfile):
        """Test run property decorated method."""
        m_tarfile.return_value = self.fake_tarfile

        # Test without time values
        r = Run('somepath', key=self.key)
        self.assertEqual(r.environment_account_number, '12345')
        self.assertEqual(r.environment_name, 'test_name')
        self.assertEqual(r.environment_uuid, 'test_uuid')
        self.assertEqual(r.status, 'test_status')
        self.assertTrue(r.synced is None)
        self.assertTrue(r.completed is None)

        filenames = r.filenames
        for i in range(10):
            self.assertTrue('file_{}'.format(i) in filenames)
        self.assertTrue('run_data.json' in filenames)
        self.assertEqual(len(filenames), 11)

        # Test with bad time values
        self.run_data['completed'] = 'notatimestring'
        self.run_data['synced'] = 'alsonotatimestring'
        self.fake_tarfile.add_file('run_data.json', self.run_data)
        r = Run('somepath', key=self.key)
        self.assertTrue(r.synced is None)
        self.assertTrue(r.completed is None)

        # Test with correct time values
        t = datetime.datetime.utcnow()
        t = t.replace(tzinfo=pytz.utc)
        self.run_data['completed'] = t.isoformat()
        self.run_data['synced'] = t.isoformat()
        self.fake_tarfile.add_file('run_data.json', self.run_data)
        r = Run('somepath', key=self.key)
        self.assertEqual(r.synced, t.replace(microsecond=0))
        self.assertTrue(r.completed, t.replace(microsecond=0))

    @mock.patch('cloud_snitch.runs.tarfile.open')
    def test_get_object(self, m_tarfile):
        """Test getting an object from the run."""
        m_tarfile.return_value = self.fake_tarfile
        r = Run('somepath', key=self.key)
        for i in range(10):
            obj = r.get_object('file_{}'.format(i))
            self.assertEqual(obj['value'], i)

    def test_non_existent_path(self):
        """Test that trying to open an archive that doesnt exist fails."""
        with self.assertRaises(RunInvalidError):
            Run('/path/to/a/file/that/doesnt/exist')
