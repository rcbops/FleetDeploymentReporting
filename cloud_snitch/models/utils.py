from cloud_snitch.exc import ConversionError
from cloud_snitch.exc import ModelNotFoundError
from cloud_snitch.exc import PropertyNotFoundError
from cloud_snitch.models import registry

_falses = set(['false', 'no'])


def string_to_bool(value):
    if not value:
        return False

    if value.lower() in _falses:
        return False

    return True


SPECIAL_CONVERSIONS = {
    str: {
        bool: string_to_bool
    }
}


def prep_val(model_name, prop_name, value, raise_for_error=True):
    """Try to convert value to a datatype to match the property.

    :param model_name: Name of the model or label
    :type model_name: str
    :param prop_name: Name of the property
    :type prop_name: str
    :param value: Value to prepare
    :type value: str
    :param raise_for_error: Raise an exception on conversion error.
        If set to false, the original value will be returned.
        Errors for missing models or properties will always be raised.
    :type raise_for_error: bool
    :returns: Converted value
    :rtype: type of property
    """
    # Get model object
    model = registry.models.get(model_name)
    if model is None:
        raise ModelNotFoundError(model_name)

    # Get property type
    try:
        t = model.properties[prop_name].type
    except KeyError:
        raise PropertyNotFoundError(model_name, prop_name)

    # If value is already the desired type, do nothing.
    if isinstance(value, t):
        return value

    # Look for a special conversion
    try:
        conversion = SPECIAL_CONVERSIONS[type(value)][t]
    except KeyError:
        conversion = t

    # Attempt simple conversion.
    try:
        new_val = conversion(value)
    except Exception:
        if raise_for_error:
            raise ConversionError(value, t)
        new_val = value

    # Return the new value.
    return new_val
