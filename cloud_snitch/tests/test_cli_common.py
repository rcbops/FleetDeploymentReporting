import mock
import sys
import unittest

from io import StringIO

from cloud_snitch.cli_common import base_parser
from cloud_snitch.cli_common import confirm_env_action
from cloud_snitch.cli_common import find_environment
from cloud_snitch.exc import EnvironmentNotFoundError


class TestBaseParser(unittest.TestCase):
    """Test the base parser.  The base parser adds a common version action."""

    def setUp(self):
        self.old_stream = sys.stdout
        self.stream = StringIO()
        sys.stdout = self.stream

    def tearDown(self):
        sys.stdout = self.old_stream
        self.stream.close()

    def test_base_parser(self):
        """Test behaviour of default options."""
        parser = base_parser(description='test_description')
        self.assertEqual(parser.description, 'test_description')
        with self.assertRaises(SystemExit):
            parser.parse_args(['-v'])


class TestFindEnvironment(unittest.TestCase):

    @mock.patch(
        'cloud_snitch.remove.EnvironmentEntity.find',
        return_value=None
    )
    def test_find_no_match(self, m_find):
        """Test that error is raised on no match."""
        with self.assertRaises(EnvironmentNotFoundError):
            find_environment('session', '12345', 'test')

    @mock.patch(
        'cloud_snitch.remove.EnvironmentEntity.find',
        return_value='testenv'
    )
    def test_find(self, m_find):
        """Test that value from find_environment is returned on success."""
        env = find_environment('session', '12345', 'test')
        self.assertEqual(env, 'testenv')


class TestConfirmEnvAction(unittest.TestCase):
    """Test the confirm_env_action function."""

    @mock.patch('builtins.input')
    def test_skip_true(self, m_input):
        """Test that input is skipped when skip is true."""
        confirmed = confirm_env_action(
            '12345',
            'test_name',
            'test_msg',
            skip=True
        )
        m_input.assert_not_called()
        self.assertTrue(confirmed)

    @mock.patch('builtins.input', side_effect=['y'])
    def test_skip_default(self, m_input):
        """Test default behavior of skip(which is false)."""
        confirmed = confirm_env_action('12345', 'test', 'test_msg')
        m_input.assert_called_once_with('test_msg (y/n) --> ')
        self.assertTrue(confirmed)

    @mock.patch('builtins.input')
    def test_loop_until_valid(self, m_input):
        """Test loop until valid input."""
        m_input.side_effect = ['a', 'b', 'c', 'Y']
        confirmed = confirm_env_action('12345', 'test', 'test_msg')
        self.assertTrue(confirmed)

        m_input.side_effect = ['a', 'b', 'c', 'y']
        confirmed = confirm_env_action('12345', 'test', 'test_msg')
        self.assertTrue(confirmed)

        m_input.side_effect = ['a', 'b', 'c', 'N']
        confirmed = confirm_env_action('12345', 'test', 'test_msg')
        self.assertFalse(confirmed)

        m_input.side_effect = ['a', 'b', 'c', 'n']
        confirmed = confirm_env_action('12345', 'test', 'test_msg')
        self.assertFalse(confirmed)
