from rest_framework.serializers import ChoiceField
from rest_framework.serializers import Serializer

from .cinder_volume_driver import CinderVolumeDriverReport
from .generic import GenericReport
from .git import GitReport


class Registry:
    """Convenience class for interacting with reports."""

    def __init__(self):
        """Build list of reports."""
        self.reports = [
            CinderVolumeDriverReport,
            GenericReport,
            GitReport
        ]
        # @TODO - Code to find reports from plugins.

    def list(self, sort_property='name'):
        """List reports

        Sort by name by default.
        May support sorting by other criteria in the future.
        """
        s = sorted(self.reports, key=lambda x: getattr(x, 'name'))
        return s

    def find(self, name):
        """Find a single report by name

        :param name: Name of a report
        :type name: str
        :returns: A report object on success
        :rtype: BaseReport|None
        """
        for r in self.reports:
            if r.name == name:
                return r
        else:
            return None


REGISTRY = Registry()


class ReportNameSerializer(Serializer):
    """Serializer for validating report selection."""

    report_name = ChoiceField([r.name for r in REGISTRY.list()], required=True)
