from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class IsRpcRacker(IsAuthenticated):
    """Permission class for rpc rackers.

    User must be authenticated and must have at least one
    of a configured set of groups.
    """
    # Get set of rpc_groups from config.
    rpc_groups = set(getattr(settings, 'RAXAUTH_RPC_GROUPS', []))

    def has_permission(self, request, view):
        """Check that user is authenticated and has at least one group.

        :returns: Whether or not the user is authenticated and has a group
        :rtype: bool
        """
        authenticated = super(IsRpcRacker, self).has_permission(request, view)
        user_groups = getattr(request.user, 'roles', set())
        if not isinstance(user_groups, set):
            user_groups = set(user_groups)
        return authenticated and bool(self.rpc_groups & user_groups)
