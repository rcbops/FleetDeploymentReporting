class MissingSerializerClassError(Exception):
    def __init__(self, report_class):
        msg = (
            'Report {} is missing a serializer class.'
            .format(report_class.name)
        )
        super(MissingSerializerClassError, self).__init__(msg)
