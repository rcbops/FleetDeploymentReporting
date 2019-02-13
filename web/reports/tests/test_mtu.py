from django.test import tag
from django.test import SimpleTestCase

from reports.mtu import MTUSerializer
from reports.mtu import MTUReport

from common.tests.base import SerializerCase


class TestMTUSerializer(SerializerCase):
    """Test the report serializer."""

    serializer_class = MTUSerializer

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


class TestMTUReport(SimpleTestCase):
    """Test the mtu report."""

    def test_clean_row(self):
        cols = [
            'Same MTU',
            'Is Running MTU Default',
            'Is Configured MTU Default'
        ]
        r = MTUReport({'time': 1})

        # Check that None/null is converted to false.
        s = {
            'control': 1,
            'Same MTU': None,
            'Is Running MTU Default': None,
            'Is Configured MTU Default': None
        }
        s0 = r.clean_row(s)
        for col in cols:
            self.assertTrue(s0[col] is False)
        self.assertEquals(s0['control'], 1)

        # Check that trues/false are left as is
        s = {
            'control': 1,
            'Same MTU': True,
            'Is Running MTU Default': False,
            'Is Configured MTU Default': True
        }
        s0 = r.clean_row(s)
        self.assertEquals(s0['control'], 1)
        self.assertTrue(s0['Same MTU'] is True)
        self.assertTrue(s0['Is Running MTU Default'] is False)
        self.assertTrue(s0['Is Configured MTU Default'] is True)

    def test_columns(self):
        """Test columns."""
        expected = [
            'Account Name',
            'Account Number',
            'Hostname',
            'Device',
            'Running MTU',
            'Configured MTU',
            'Same MTU',
            'Is Running MTU Default',
            'Is Configured MTU Default'
        ]

        r = MTUReport({'time': 1})
        for i, col in enumerate(r.columns()):
            self.assertEquals(expected[i], col)
