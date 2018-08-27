import logging

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from rest_framework.test import APITestCase as RFAPITestCase

logging.getLogger('neo4j').setLevel(logging.ERROR)
logging.getLogger('api').setLevel(logging.ERROR)
logging.getLogger('api.query').setLevel(logging.ERROR)
logging.getLogger('django').setLevel(logging.ERROR)


class SerializerCase(SimpleTestCase):
    """Base Class for testing deserialization."""

    def deserialize(self):
        self.serializer = self.serializer_class(data=self.data)

    def assertValid(self):
        self.deserialize()
        self.assertTrue(self.serializer.is_valid())

    def assertInvalid(self):
        self.deserialize()
        self.assertFalse(self.serializer.is_valid())


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
