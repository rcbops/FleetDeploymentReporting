import mock

from django.test import TestCase
from django.test import tag
from raxauth.permissions import IsRpcRacker


TEST_GROUPS = set(['group_1', 'group_2', 'group_3'])


class FakeUser:
    def __init__(self, is_authenticated, roles=None):
        self.is_authenticated = is_authenticated
        if roles is None:
            roles = set()
        self.roles = roles


class FakeRequest:
    def __init__(self, user):
        self.user = user


class TestIsRpcRacker(TestCase):
    """Test IsRpcRacker permission class."""
    @tag('unit')
    def test_not_authenticated(self):
        """Test a user that has not authenticated."""
        req = FakeRequest(FakeUser(False))
        self.assertFalse(IsRpcRacker().has_permission(req, None))

    @tag('unit')
    @mock.patch('raxauth.permissions.IsRpcRacker.rpc_groups', new=TEST_GROUPS)
    def test_authenticated_but_not_rpc(self):
        """Test a user that authenticates but is missing a group."""
        req = FakeRequest(FakeUser(True))
        self.assertFalse(IsRpcRacker().has_permission(req, None))

    @tag('unit')
    @mock.patch('raxauth.permissions.IsRpcRacker.rpc_groups', new=TEST_GROUPS)
    def test_authenticated_and_rpc(self):
        """Test a user that authenticates and has the group."""
        # Test one of the three
        req = FakeRequest(FakeUser(True, roles=['group_5', 'group_1']))
        self.assertTrue(IsRpcRacker().has_permission(req, None))

        # Test another of the three
        req = FakeRequest(FakeUser(True, roles=['group_10', 'group_3']))
        self.assertTrue(IsRpcRacker().has_permission(req, None))

        # Test multiple of the three
        req = FakeRequest(FakeUser(True, roles=['group_1', 'group_2']))
        self.assertTrue(IsRpcRacker().has_permission(req, None))
