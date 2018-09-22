import mock

from django.test import tag
from django.test import SimpleTestCase

from reports.git import GitReport
from reports.git import GitSerializer

from .base import SerializerCase


class TestGitSerializer(SerializerCase):
    """Test the git serializer"""

    serializer_class = GitSerializer

    def setUp(self):
        """Patch urls returned from neo4j query."""
        self.data = {
            'time': 1,
            'url': 'https://git.openstack.org/openstack/openstack-ansible'
        }
        self.patcher = mock.patch('reports.git.GitSerializer.git_urls')
        self.mock_git_urls = self.patcher.start()
        self.mock_git_urls.return_value = [
            'https://git.openstack.org/openstack/openstack-ansible',
            'https://repoa',
            'https://repob'
        ]

    def tearDown(self):
        """Stop the patch on test end."""
        self.patcher.stop()

    @tag('unit')
    def test_valid(self):
        """Test valid input."""
        self.assertValid()

    @tag('unit')
    def test_missing_time(self):
        """Test time is required."""
        del self.data['time']
        self.assertInvalid()

    @tag('unit')
    def test_non_integer_time(self):
        """Test Non integer value for time."""
        self.data['time'] = 'somestr'
        self.assertInvalid()

    @tag('unit')
    def test_default_url(self):
        """Test that url defaults to:

        https://git.openstack.org/openstack/openstack-ansible
        """
        del self.data['url']
        self.assertValid()
        self.assertEquals(
            self.serializer.validated_data['url'],
            'https://git.openstack.org/openstack/openstack-ansible'
        )

    @tag('unit')
    def test_invalid_url(self):
        """Test invalid choice for url."""
        self.data['url'] = 'notarepo'
        self.assertInvalid()


class TestGitReport(SimpleTestCase):
    """Test the git report.

    @TODO - Mock the column query and test that a query is built correctly.
    """

    def setUp(self):
        """Patch git url returned from neo4j."""
        self.params = {
            'time': 1534172356 * 1000,
            'url': 'https://git.openstack.org/openstack/openstack-ansible',
        }
        self.patcher = mock.patch('reports.git.GitSerializer.git_urls')
        self.mock_git_urls = self.patcher.start()
        self.mock_git_urls.return_value = [
            'https://git.openstack.org/openstack/openstack-ansible',
            'https://repoa',
            'https://repob'
        ]

    def tearDown(self):
        """Stop the patch on test end."""
        self.patcher.stop()

    @tag('unit')
    def test_columns(self):
        """Test columns of report."""
        expected = [
            'Environment.name',
            'Environment.account_number',
            'GitRepo.path',
            'GitRepo.merge_base_name',
            'GitUrl.url'
        ]
        r = GitReport(self.params)
        for i, col in enumerate(r.columns()):
            self.assertEquals(expected[i], col)
