import mock
import unittest
import sys

from io import StringIO

from cloud_snitch.terminate import parser
from cloud_snitch.terminate import set_to_until_zero


class TestArgParser(unittest.TestCase):

    def setUp(self):
        self.old_stream = sys.stderr
        self.stream = StringIO()
        sys.stderr = self.stream

    def tearDown(self):
        sys.stderr = self.old_stream
        self.stream.close()

    @mock.patch('cloud_snitch.utils.milliseconds_now')
    def test_defaults(self, m_now):
        """Test default arguments."""
        m_now.return_value = 1
        args = ['test_uuid']
        args = parser.parse_args(args)
        self.assertEqual(args.uuid, 'test_uuid')
        self.assertFalse(args.skip)
        self.assertTrue(isinstance(args.time, int))
        self.assertTrue(args.time > 0)
        self.assertEqual(args.limit, 2000)

    def test_non_defaults(self):
        """Test non default arguments."""
        # Test with -s option
        args = ['test_uuid', '-s']
        args = parser.parse_args(args)
        self.assertTrue(args.skip)

        # Test with --skip option
        args = ['test_uuid', '--skip']
        args = parser.parse_args(args)
        self.assertTrue(args.skip)

        # Test --time option
        args = ['test_uuid', '--time', '33']
        args = parser.parse_args(args)
        self.assertEqual(args.time, 33)

        # Test non integer --time option
        args = ['test_uuid', '--time', 'notaint']
        with self.assertRaises(SystemExit):
            parser.parse_args(args)

        # Test --limit option
        args = ['test_uuid', '--limit', '100']
        args = parser.parse_args(args)
        self.assertEqual(args.limit, 100)

        # Test non integer --limit option
        args = ['test_uuid', '--limit', 'notaint']
        with self.assertRaises(SystemExit):
            parser.parse_args(args)


class LoopStopperError(Exception):
    pass


class FakeResult(dict):
    def __init__(self, changed):
        self['changed'] = changed

    def single(self):
        return self


class FakeTransaction:

    def __init__(self, data, error_after=2):
        self.data = data
        self.error_after = error_after
        self.calls = 0
        self.query = None
        self.params = None

    def begin_transaction(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def run(self, query, **params):
        self.calls += 1
        if self.calls > self.error_after:
            raise LoopStopperError("Stopping a loop")
        self.query = query
        self.params = params
        return self.data[self.calls - 1]


class FakeEnvironment:
    def __init__(self, uuid='test_uuid'):
        self.uuid = uuid


class TestSetToUntilZero(unittest.TestCase):
    """Test delete_until_zero function."""

    def test_cipher_params(self):
        """Test that cipher query params are created."""
        env = FakeEnvironment()

        fake_tx = FakeTransaction([FakeResult(1)], error_after=1)
        session = mock.Mock()
        session.begin_transaction = mock.Mock()
        session.begin_transaction.return_value = fake_tx

        with self.assertRaises(LoopStopperError):
            set_to_until_zero(session, env, 1, limit=5)

        self.assertEqual(fake_tx.params['limit'], 5)
        self.assertEqual(fake_tx.params['time'], 1)
        self.assertEqual(fake_tx.params['uuid'], env.uuid)

    def test_loop_termination(self):
        """Test that loop terminates when deleted count from query is 0."""
        env = FakeEnvironment()
        fake_results = [
            FakeResult(10),
            FakeResult(5),
            FakeResult(1),
            FakeResult(0)
        ]
        fake_tx = FakeTransaction(fake_results, error_after=10)
        session = mock.Mock()
        session.begin_transaction = mock.Mock()
        session.begin_transaction.return_value = fake_tx

        changed = set_to_until_zero(session, env, 1, limit=5)
        self.assertEqual(changed, 16)
