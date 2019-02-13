import logging

from cloud_snitch.models import registry
from common.serializers import FilterSerializer
from common.serializers import OrderSerializer
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import CharField
from rest_framework.serializers import IntegerField
from rest_framework.serializers import ListField
from rest_framework.serializers import ValidationError

logger = logging.getLogger(__name__)


class ModelSerializer(BaseSerializer):
    """Serializer for Models."""
    def to_representation(self, model):
        """Get dict repr

        :param model: VersionedEntity to represent
        :type model: class
        :returns: Dict representation
        :rtype: dict
        """
        # Assemble list of properties.
        properties = {}
        for prop in registry.properties(model.label):
            properties[prop] = {
                'type': model.properties.get(prop).type.__name__
            }

        # Assemble child relationships
        children = {}
        for name, childtuple in model.children.items():
            children[name] = {
                'rel_name': childtuple[0],
                'label': childtuple[1].label
            }

        return {
            'label': model.label,
            'state_label': model.state_label,
            'properties': properties,
            'identity': model.identity_property,
            'children': children
        }


class GenericSerializer(BaseSerializer):
    """Generic serializer for dicts"""
    def to_representation(self, obj):
        """Get dict repr

        :param obj: Dict to represent
        :type obj: dict
        :returns: Dict representation
        :rtype: dict
        """
        return obj


class PropertySerializer(BaseSerializer):
    """Serializer for list of properties."""
    def to_representation(self, obj):
        """Dict representation.

        :param obj: List of properties
        :type obj: list
        :returns: Dict representation
        :rtype dict
        """
        return dict(properties=obj)


class SearchSerializer(Serializer):
    """Serializer for search queries."""
    model = ChoiceField([m.label for m in registry.models.values()])
    time = IntegerField(min_value=0, required=False)
    identity = CharField(max_length=256, required=False)
    filters = ListField(child=FilterSerializer(), required=False)
    orders = ListField(child=OrderSerializer(), required=False)

    page = IntegerField(min_value=0, required=False, default=1)
    pagesize = IntegerField(min_value=1, required=False, default=500)
    index = IntegerField(min_value=0, required=False)

    def validate(self, data):
        model_set = set([t[0] for t in registry.path(data['model'])])
        model_set.add(data['model'])

        for f in data.get('filters', []):
            # Make sure filter model is in path of search model
            if f['model'] not in model_set:
                raise ValidationError(
                    'Model {} not in path of {}'
                    .format(f['model'], data['model'])
                )

        for o in data.get('orders', []):
            # Make sure order model is in path of search model
            if o['model'] not in model_set:
                raise ValidationError(
                    'Model {} not in path of {}'
                    .format(o['model'], data['model'])
                )

        return data


class TimesChangedSerializer(Serializer):
    """Serializer for detailed query of one object."""
    model = ChoiceField([m.label for m in registry.models.values()])
    identity = CharField(max_length=256, required=True)
    time = IntegerField(min_value=0, required=False)


class DiffSerializer(Serializer):
    """Serializer for requesting diff structure."""
    model = ChoiceField([m.label for m in registry.models.values()])
    identity = CharField(max_length=256, required=True)
    left_time = IntegerField(min_value=0, required=True)
    right_time = IntegerField(min_value=0, required=True)
