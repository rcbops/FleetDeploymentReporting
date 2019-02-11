from django.test import tag
from django.test import SimpleTestCase

from reports.registry import Registry
from reports.registry import ReportNameSerializer

from common.tests.base import SerializerCase


def fake_report_class(**kwargs):

    class Fake:
        pass

    for key, value in kwargs.items():
        setattr(Fake, key, value)

    return Fake


class TestReportNameSerializer(SerializerCase):
    """Test the report name serializer."""

    serializer_class = ReportNameSerializer

    def setUp(self):
        self.data = {'report_name': 'Generic'}

    @tag('unit')
    def test_valid(self):
        """Test valid input."""
        self.assertValid()

    @tag('unit')
    def test_missing_report_name(self):
        """Test missing report_name."""
        del self.data['report_name']
        self.assertInvalid()

    @tag('unit')
    def test_invalid_report_name(self):
        """Test invalid report name."""
        self.data['report_name'] = 'notareport'
        self.assertInvalid()


class TestRegistry(SimpleTestCase):
    """Test the registry object."""

    def setUp(self):
        self.r = Registry()
        self.r.reports = [
            fake_report_class(name='ReportB'),
            fake_report_class(name='ReportA'),
            fake_report_class(name='ReportC')
        ]

    @tag('unit')
    def test_list(self):
        """Test that returned list should be sorted by name."""
        expected = [
            'ReportA',
            'ReportB',
            'ReportC'
        ]
        for i, cls in enumerate(self.r.list()):
            self.assertEquals(expected[i], cls.name)

    @tag('unit')
    def test_list_invalid_sort_property(self):
        """Test what happens when invalid sort property is provided."""
        self.r.list(sort_property='invalid')

    @tag('unit')
    def test_find_exists(self):
        """Test existing report found."""
        c = self.r.find('ReportA')
        self.assertEquals(c.name, 'ReportA')

    @tag('unit')
    def test_find_not_exists(self):
        """Test that finding a non existing report returns None."""
        c = self.r.find('ReportD')
        self.assertTrue(c is None)
