from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TechnicianViewSet,
    SpecialtyViewSet,
    CertificationViewSet,
    TechnicianCostMetricsViewSet,
    EmploymentTypeKpiReportViewSet
)

router = DefaultRouter()
router.register(r'technicians', TechnicianViewSet)
router.register(r'specialties', SpecialtyViewSet)
router.register(r'certifications', CertificationViewSet)
router.register(r'cost-metrics', TechnicianCostMetricsViewSet)
router.register(r'employment-kpi', EmploymentTypeKpiReportViewSet)

app_name = 'technicians'

urlpatterns = [
    path('', include(router.urls)),
]
