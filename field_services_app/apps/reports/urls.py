from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reports'

router = DefaultRouter()
router.register('templates', views.ReportTemplateViewSet, basename='template')
router.register('parameters', views.ReportParameterViewSet, basename='parameter')
router.register('saved', views.SavedReportViewSet, basename='saved')
router.register('schedules', views.ReportScheduleViewSet, basename='schedule')
router.register('dashboards', views.DashboardViewSet, basename='dashboard')
router.register('widgets', views.DashboardWidgetViewSet, basename='widget')
router.register('metrics', views.ReportMetricViewSet, basename='metric')

urlpatterns = [
    path('', include(router.urls)),
]
