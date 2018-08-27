class InvalidLabelError(Exception):
    def __init__(self, label):
        """Init the error.

        :param label: Label
        :type label: str
        """
        msg = 'Invalid label \'{}\'.'.format(label)
        super(InvalidLabelError, self).__init__(msg)


class InvalidPropertyError(Exception):
    def __init__(self, label, prop):
        """Init the error.

        :param label: Label
        :type label: str
        :param prop: Property name
        :type prop: str
        """
        msg = 'Invalid property \'{}\' on \'{}\''.format(label, prop)
        super(InvalidPropertyError, self).__init__(msg)
