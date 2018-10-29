from .base import DefinitionTestCase
from cloud_snitch.models import EnvironmentEntity
from cloud_snitch.models import GitRepoEntity
from cloud_snitch.models import HostEntity
from cloud_snitch.models import UservarEntity


class TestEnvironmentEntity(DefinitionTestCase):
    """Test the environment entity definition."""
    entity = EnvironmentEntity
    label = 'Environment'
    state_label = 'EnvironmentState'
    identity_property = 'uuid'
    static_properties = [
        'account_number',
        'name'
    ]
    state_properties = [
        'last_sync',
        'status'
    ]
    children = (
        ('hosts', ('HAS_HOST', HostEntity)),
        ('gitrepos', ('HAS_GIT_REPO', GitRepoEntity)),
        ('uservars', ('HAS_USERVAR', UservarEntity))
    )

    def test_definition(self):
        """Test definition."""
        self.definition_test()
