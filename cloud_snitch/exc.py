class PropertyAlreadyExistsError(Exception):
    """Error for duplicate properties on the same model."""
    def __init__(self, label, prop):
        """Init the error.

        :param label: Name of the model
        :type label: str
        :param prop: Name of the property
        :type prop: str
        """
        msg = (
            'Cannot create property {} as it already exists on model {}'
            .format(prop, label)
        )
        super(PropertyAlreadyExistsError, self).__init__(msg)


class EntityDefinitionError(Exception):
    """Error for problems defining an entity."""
    pass


class RunInvalidError(Exception):
    """Error for a directory in the data directory that isn't a run."""
    def __init__(self, path):
        """Init the error.

        :param path: Path of invalid directory
        :type path: str
        """
        msg = 'Directory {} is not a valid run.'.format(path)
        super(RunInvalidError, self).__init__(msg)


class RunAlreadySyncedError(Exception):
    """Error for a run that is already synced."""
    def __init__(self, run):
        """Init the error.

        :param run: Run instance
        :type run: cloud_snitch.runs.Run
        """
        msg = 'Run at path {} is already synced.'.format(run.path)
        super(RunAlreadySyncedError, self).__init__(msg)


class RunInvalidStatusError(Exception):
    """Error for trying to slurp a run that is not in finished status."""
    def __init__(self, run):
        """Init the error.

        :param run: Run instance
        :type run: cloud_snitch.runs.Run
        """
        msg = 'Run at path {} is in {} status'.format(run.path, run.status)
        super(RunInvalidStatusError, self).__init__(msg)


class RunContainsOldDataError(Exception):
    """Error for slurping a run with older data than what is in neo4j."""
    def __init__(self, run, last_update):
        """Init the error.

        :param run: Run instance,
        :type run: cloud_snitch.runs.Run
        :param last_update: Last update time of environment
        :type last_update: datetime.datetime
        """
        msg = 'Run at path {} is older than the last update of {}'.format(
            run.path,
            last_update.isoformat()
        )
        super(RunContainsOldDataError, self).__init__(msg)


class EnvironmentLockedError(Exception):
    """Error for environment being locked in database."""
    def __init__(self, instance):
        """Init the error.

        :param instance: Instance of environment lock entity
        :type instance: cloud_snitch.models.EnvironmentLockEntity
        """
        msg = 'Environment {}: {} is locked.'.format(
            instance.account_number,
            instance.name
        )
        super(EnvironmentLockedError, self).__init__(msg)


class MaxRetriesExceededError(Exception):
    """Error for maximum number of retries for an update."""
    def __init__(self):
        msg = 'Maximum number of retries has been reached.'
        super(MaxRetriesExceededError, self).__init__(msg)


class EnvironmentNotFoundError(Exception):
    """Error for environment not found."""
    def __init__(self, uuid):
        msg = ('Unable to locate environment with uuid \'{}\'.').format(uuid)
        super(EnvironmentNotFoundError, self).__init__(msg)


class ConversionError(Exception):
    """Error for invalid conversion."""
    def __init__(self, old_val, new_type):
        """Init the error.

        :param old_val: Old value to convert
        :type old_val: object
        :param new_type: New type to convert old value to
        :type new_type: class
        """
        msg = (
            'Unable to convert value \'{}\' to \'{}\'.'
            .format(old_val, new_type)
        )
        super(ConversionError, self).__init__(msg)


class ModelNotFoundError(Exception):
    """Error for trying to get a model not in the registry."""
    def __init__(self, model_name):
        """Init the error.

        :param model_name: Name of the model.
        :type model_name: str
        """
        msg = 'Model \'{}\' not found.'.format(model_name)
        super(ModelNotFoundError, self).__init__(msg)


class PropertyNotFoundError(Exception):
    """Error for property not existing on a model."""
    def __init__(self, model_name, property_name):
        """Init the error.

        :param model_name: Name of the model
        :type model_name: str
        :param property_name: Name of the property
        :type property_name: str
        """
        msg = (
            'Property \'{}\' not found on model \'{}\'.'
            .format(property_name, model_name)
        )
        super(PropertyNotFoundError, self).__init__(msg)
