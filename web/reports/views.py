import logging

from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .registry import REGISTRY as report_registry
from .registry import ReportNameSerializer

from .serializers import ReportDataSerializer
from .serializers import ReportSerializer

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):

    def list(self, request):
        """Get a list of reports."""
        serializer = ReportSerializer(report_registry.list(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get a specific report."""
        report = report_registry.find(pk)
        if report is None:
            raise Http404()
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    @list_route(methods=['post'])
    def run(self, request):
        """Run a report."""
        # First validate request report exists
        s = ReportNameSerializer(data=request.data)
        if not s.is_valid():
            raise ValidationError(s.errors)

        # Get an instance of the report class or 404
        report_name = s.validated_data.get('report_name')
        report_class = report_registry.find(report_name)
        if not report_class:
            logger.error("Unable to locate report: {}".format(report_name))
            raise Http404()

        # This will raise a validationerror if report parameters are invalid
        report = report_class(request.data)

        # Save columns for renderer context
        self.columns = report.columns()

        # Run report and serialize the result
        s = ReportDataSerializer(report.run())
        return Response(s.data)

    def get_renderer_context(self):
        """Add column ordering to renderer context for csvs."""
        context = super().get_renderer_context()
        columns = getattr(self, 'columns', None)
        if columns is not None:
            context['header'] = columns
        return context
