from .base import DefinitionTestCase
from cloud_snitch.models import GitRemoteEntity
from cloud_snitch.models import GitRepoEntity
from cloud_snitch.models import GitUntrackedFileEntity
from cloud_snitch.models import GitUrlEntity


class TestGitUntrackedFileEntity(DefinitionTestCase):
    """Test the git untracked file entity definition."""
    entity = GitUntrackedFileEntity
    label = 'GitUntrackedFile'
    state_label = 'GitUntrackedFileState'
    identity_property = 'path'

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestGitUrlEntity(DefinitionTestCase):
    """Test the git url entity definition."""
    entity = GitUrlEntity
    label = 'GitUrl'
    state_label = 'GitUrlState'
    identity_property = 'url'

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestGitRemoteEntity(DefinitionTestCase):
    """Test the git remote entity definition."""
    entity = GitRemoteEntity
    label = 'GitRemote'
    state_label = 'GitRemoteState'
    identity_property = 'name_repo'
    static_properties = [
        'name',
        'repo'
    ]
    concat_properties = {
        'name_repo': [
            'name',
            'repo'
        ]
    }
    children = (
        ('urls', ('HAS_GIT_URL', GitUrlEntity)),
    )

    def test_definition(self):
        """Test definition."""
        self.definition_test()


class TestGitRepoEntity(DefinitionTestCase):
    """Test the git repo entity definition."""
    entity = GitRepoEntity
    label = 'GitRepo'
    state_label = 'GitRepoState'
    identity_property = 'path_environment'
    static_properties = [
        'path',
        'environment'
    ]
    state_properties = [
        'active_branch_name',
        'head_sha',
        'is_detached',
        'working_tree_dirty',
        'working_tree_diff_md5',
        'merge_base_name',
        'merge_base_diff_md5'
    ]
    concat_properties = {
        'path_environment': [
            'path',
            'environment'
        ]
    }
    children = (
        ('untrackedfiles', ('HAS_UNTRACKED_FILE', GitUntrackedFileEntity)),
        ('remotes', ('HAS_GIT_REMOTE', GitRemoteEntity))
    )

    def test_definition(self):
        """Test definition."""
        self.definition_test()
