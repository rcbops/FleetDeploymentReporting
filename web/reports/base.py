from .exc import MissingSerializerClassError

from rest_framework.exceptions import ValidationError


class BaseReport:

    # Name of the report as it would appear in a drop down
    name = "Base Report"

    # Description of the report - will be a blurb on
    # ui form
    description = "Provide short user friendly description"

    # Class for a serializer to validate report parameters.
    serializer_class = None

    def __init__(self, data):
        """Init the report with input data from request.

        :param data: Data from request
        :type data: dict
        """
        if not self.serializer_class:
            raise MissingSerializerClassError(self.__class__)

        serialized = self.serializer_class(data=data)
        if not serialized.is_valid():
            raise ValidationError(serialized.errors)

        self.data = serialized.validated_data

    @classmethod
    def form_data(cls):
        """Return data needed for web client to construct form.

        :returns: List of dict objects
        :rtype: list
        """
        data = {
            'name': cls.name,
            'description': cls.description,
            'form_data': []
        }
        if cls.serializer_class:
            data['form_data'] = cls.serializer_class().form_data()
        return data

    def run(self):
        """Do the report.

        :returns: List of rows
        :rtype: list
        """
        return []

    def columns(self):
        """Compute list of columns for the report.

        :returns: List of columns
        :rtype: list
        """
        return []
