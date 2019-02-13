from django.test import SimpleTestCase


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
