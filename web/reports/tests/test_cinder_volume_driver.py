from django.test import tag
from django.test import SimpleTestCase

from reports.cinder_volume_driver import parse_contents
from reports.cinder_volume_driver import CinderVolumeDriverReport as Report
from reports.cinder_volume_driver import VolumeDriverSerializer

from .base import SerializerCase


class TestParseContents(SimpleTestCase):
    """Test volume driver and section are parsed correctly from ini string."""

    @tag('unit')
    def test_parse(self):
        """Test that paring an ini file for volume driver and section."""

        expected = [
            ('sectionb', 'driverb'),
            ('sectionc', 'driverc')
        ]
        test = ('[sectiona]\n'
                'not_a_volume driver = somevalue\n'
                '[sectionb]\n'
                'volume_driver = driverb\n'
                '[sectionc]\n'
                'volume_driver = driverc')
        tuples = parse_contents(test)
        for i, tup in enumerate(tuples):
            section, driver = tup
            self.assertEquals(expected[i][0], section)
            self.assertEquals(expected[i][1], driver)


class TestVolumeDriverSerializer(SerializerCase):
    """Test the report serializer."""

    serializer_class = VolumeDriverSerializer

    def setUp(self):
        """Set up starting inputs"""
        self.data = {'time': 1}

    @tag('unit')
    def test_valid(self):
        """Test valid input."""
        self.assertValid()

    @tag('unit')
    def test_missing_time(self):
        """Test that time is required."""
        del self.data['time']
        self.assertInvalid()

    @tag('unit')
    def test_non_integer_time(self):
        """Test that time must be an integer."""
        self.data['time'] = 'somestr'
        self.assertInvalid()


class TestCinderVolumeDriverReport(SimpleTestCase):
    """Test the cinder volume driver report.

    @TODO - Mock column query and verify the query is being built correctly.
    """

    def setUp(self):
        self.params = {'time': 1}

    @tag('unit')
    def test_columns(self):
        """Test that output columns are correct."""
        expected = [
            'Environment.name',
            'Environment.account_number',
            'Host.hostname',
            'Configfile.name',
            'section',
            'driver'
        ]

        r = Report(self.params)
        for i, col in enumerate(r.columns()):
            self.assertEquals(expected[i], col)
