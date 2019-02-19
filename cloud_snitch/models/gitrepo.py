import logging

from .base import versioned_properties
from .base import SharedVersionedEntity
from .base import VersionedEntity
from .base import VersionedProperty

logger = logging.getLogger(__name__)


@versioned_properties
class GitUntrackedFileEntity(SharedVersionedEntity):
    """Models an untracked file in a gitrepo."""

    label = 'GitUntrackedFile'
    state_label = 'GitUntrackedFileState'
    properties = {
        'path': VersionedProperty(is_identity=True)
    }


@versioned_properties
class GitUrlEntity(SharedVersionedEntity):
    """Models a git repo url."""

    label = 'GitUrl'
    state_label = 'GitUrlState'
    properties = {
        'url': VersionedProperty(is_identity=True)
    }


@versioned_properties
class GitRemoteEntity(VersionedEntity):
    """Models a git repo remote."""

    label = 'GitRemote'
    state_label = 'GitRemoteState'
    properties = {
        'name_repo': VersionedProperty(
            is_identity=True,
            concat_properties=['name', 'repo']
        ),
        'name': VersionedProperty(is_static=True),
        'repo': VersionedProperty(is_static=True)
    }
    children = {
        'urls': ('HAS_GIT_URL', GitUrlEntity)
    }


@versioned_properties
class GitRepoEntity(VersionedEntity):
    """Models a git repo."""

    label = 'GitRepo'
    state_label = 'GitRepoState'
    properties = {
        'path_environment': VersionedProperty(
            is_identity=True,
            concat_properties=['path', 'environment']
        ),
        'path': VersionedProperty(is_static=True),
        'environment': VersionedProperty(is_static=True),
        'active_branch_name': VersionedProperty(is_state=True),
        'head_sha': VersionedProperty(is_state=True),
        'is_detached': VersionedProperty(is_state=True, type=bool),
        'working_tree_dirty': VersionedProperty(is_state=True, type=bool),
        'working_tree_diff_md5': VersionedProperty(is_state=True),
        'merge_base_name': VersionedProperty(is_state=True),
        'merge_base_diff_md5': VersionedProperty(is_state=True)
    }

    children = {
        'untrackedfiles': ('HAS_UNTRACKED_FILE', GitUntrackedFileEntity),
        'remotes': ('HAS_GIT_REMOTE', GitRemoteEntity)
    }
