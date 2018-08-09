import mock

from collections import OrderedDict
from django.test import tag
from rest_framework import status

from .base import APITestCase


class FakeReport:
    """Fake report to return some dummy data."""

    def __init__(self, data):
        """Does nothing."""
        pass

    def run(self):
        """Run some dummy data."""
        d = OrderedDict()
        d['keya'] = 'value1'
        d['keyb'] = 'value2'
        return [d]


class TestReportsViewSet(APITestCase):
    """Test the reports view set."""

    @tag('unit')
    def test_reports_list_without_auth(self):
        """Test hitting /api/reports/ without auth"""
        resp = self.client.get('/api/reports/')
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    @tag('unit')
    @mock.patch('reports.registry.Registry.list', return_value=[])
    def test_reports_list_with_auth(self, m_registry_list):
        """Test hitting /api/reports/ with auth"""
        self.client.login(**self.credentials)
        resp = self.client.get('/api/reports/')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertTrue(isinstance(data, list))

    @tag('unit')
    def test_reports_detail_without_auth(self):
        """Test hitting /api/reports/Generic/ without auth."""
        resp = self.client.get('/api/reports/Generic/')
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    @tag('unit')
    def test_reports_detail_with_auth(self):
        """Test hitting /api/reports/Generic with auth."""
        self.client.login(**self.credentials)
        resp = self.client.get('/api/reports/Generic/')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEquals(data.get('name'), 'Generic')

    @tag('unit')
    def test_reports_detail_not_found(self):
        """Test hitting /api/reports/NotAReport."""
        self.client.login(**self.credentials)
        resp = self.client.get('/api/reports/NotAReport/')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    @tag('unit')
    def test_reports_run_without_auth(self):
        """Test hitting /api/reports/run/ without auth."""
        resp = self.client.post('/api/reports/run/')
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    @tag('unit')
    def test_reports_run_bad_data(self):
        """Test hitting /api/reports/run/ with bad data."""
        self.client.login(**self.credentials)
        data = {}
        resp = self.client.post('/api/reports/run/', data=data)
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @tag('unit')
    @mock.patch('reports.views.report_registry.find', return_value=FakeReport)
    def test_reports_run_bad_report(self, m_registry):
        """Test hitting /api/reports/run/ with good data."""
        self.client.login(**self.credentials)
        data = {
            'report_name': 'Generic',
            'model': 'Environment',
            'columns': [
                {
                    'model': 'Environment',
                    'prop': 'account_number'
                }
            ]
        }
        resp = self.client.post('/api/reports/run/', data=data)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        result = resp.json()
        self.assertEquals(result[0]['keya'], 'value1')
        self.assertEquals(result[0]['keyb'], 'value2')
