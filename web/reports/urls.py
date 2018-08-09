from .views import ReportViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ReportViewSet, base_name='reports')

urlpatterns = router.urls
