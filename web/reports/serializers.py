from cloud_snitch.models import registry
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import Serializer
from rest_framework.serializers import SlugField
from rest_framework.serializers import ValidationError


# Model fields present a choice of available models
_models = [m.label for m in registry.models.values()]


class ReportSerializer(BaseSerializer):
    """Serializer for information about reports."""

    def to_representation(self, obj):
        """Calls form_data method of the object."""
        return obj.form_data()


class ReportDataSerializer(BaseSerializer):
    """Serializer for report data."""

    def to_representation(self, obj):
        """Serializes a dict.

        :param obj: Object that represents a row in a report.
        :type obj: obj
        """
        return obj


def time_field(required=True):
    """Returns an integer field appropriate for millisecond timestamps.

    :param required: Is the field required?
    :type required: bool
    :returns: IntegerField
    :rtype: IntegerField
    """
    return IntegerField(min_value=0, required=required)


class TimeRangeSerializer(Serializer):
    """Simple serializer for a time range field.

    Both start and stop are required. To make this optional,
    Nest with a:
        <fieldname> = TimeRangeSerializer(required=False)
    """
    start = time_field(required=True)
    stop = time_field(required=True)

    def validate(self, data):
        """Custom validation

        Stop should be greater than start

        :param data: Data to validate
        :type data: dict
        """
        start = data.get('start')
        stop = data.get('stop')
        if start and stop and start > stop:
            raise ValidationError(
                'Stop time {} is not greater than {}'
                .format(data['stop'], data['start'])
            )
        return data


def model_field(required=True):
    """Returns a choice field where choices are models.

    :param required: Is the field required?
    :type required: bool
    :return: ChoiceField
    :rtype: ChoiceField
    """
    return ChoiceField(_models, required=required)


def property_field(max_length=256, required=True):
    """Returns a property field.

    :param max_length: Max length of field
    :type max_length: int
    :param required: Is this field required?
    :type required: bool
    :return: SlugField
    :rtype: SlugField
    """
    return SlugField(max_length=max_length, required=required)


class ModelPropertySerializer(Serializer):
    """A combination of model and property.

    Includes custom validation to ensure that prop is a property of
    model.

    To make this optional, nest with a:
    <fieldname> = ModelPropertySerializer(required=False)
    """
    model = model_field(required=True)
    prop = property_field(required=True)

    def validate(self, data):
        """Custom validation.

        Model should be a model listed with the registry.
        Prop should be a property of the model.

        :param data: Data to validate
        :type data: dict
        """
        if data['model'] not in _models:
            raise ValidationError(
                'Model {} is not a valid model.'.format(data['model'])
            )

        if data['prop'] not in registry.properties(data['model']):
            raise ValidationError(
                '{} is not a valid property of model {}'
                .format(data['prop'], data['model'])
            )
        return data
