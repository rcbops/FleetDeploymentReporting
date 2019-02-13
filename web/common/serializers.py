from cloud_snitch.models import registry
from neo4jdriver.const import OPERATORS
from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import SlugField
from rest_framework.serializers import ValidationError

INVALID_PROP_STR = '{} is not a valid property of {}'


class FilterSerializer(Serializer):
    """Serializer for filters on a query"""
    model = ChoiceField([m.label for m in registry.models.values()])
    prop = SlugField(max_length=256, required=True)
    operator = ChoiceField(OPERATORS, required=True)
    value = CharField(max_length=256, required=True)

    def validate(self, data):
        """Custom validation.

        Ensure prop is a property of the select model.

        :param data: Data to validate
        :type data: dict
        """
        if data['prop'] not in registry.properties(data['model']):
            raise ValidationError({
                'prop': INVALID_PROP_STR.format(data['prop'], data['model'])
            })
        return data


class OrderSerializer(Serializer):
    """Serializer for order by on a query."""
    model = ChoiceField([m.label for m in registry.models.values()])
    prop = SlugField(max_length=256, required=True)
    direction = ChoiceField(['asc', 'desc'])

    def validate(self, data):
        """Custom validation.

        Ensure prop is a property of model.

        :param data: Data to validate
        :type data: dict
        """
        if data['prop'] not in registry.properties(data['model']):
            raise ValidationError({
                'prop': INVALID_PROP_STR.format(data['prop'], data['model'])
            })
        return data
