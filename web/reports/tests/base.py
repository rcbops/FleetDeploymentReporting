import logging

from django.contrib.auth.models import User
from rest_framework.test import APITestCase as RFAPITestCase

logging.getLogger('neo4j').setLevel(logging.ERROR)
logging.getLogger('api').setLevel(logging.ERROR)
logging.getLogger('api.query').setLevel(logging.ERROR)
logging.getLogger('django').setLevel(logging.ERROR)


class APITestCase(RFAPITestCase):

    credentials = {
        'username': 'testuser',
        'password': 'testpassword'
    }

    def setUp(self):
        User.objects.create_user(
            self.credentials['username'],
            password=self.credentials['password']
        )
        self.client.logout()
