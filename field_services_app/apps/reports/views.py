from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    ReportTemplate, ReportParameter, SavedReport, ReportSchedule,
    Dashboard, DashboardWidget, ReportMetric
)
# If serializers.py is created, uncomment this line
# from .serializers import (
#     ReportTemplateSerializer, ReportParameterSerializer, SavedReportSerializer,
#     ReportScheduleSerializer, DashboardSerializer, DashboardWidgetSerializer,
#     ReportMetricSerializer
# )

class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Report Templates.
    
    Provides CRUD operations for the ReportTemplate model.
    """
    queryset = ReportTemplate.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]

class ReportParameterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Report Parameters.
    
    Provides CRUD operations for the ReportParameter model.
    """
    queryset = ReportParameter.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ReportParameterSerializer
    permission_classes = [IsAuthenticated]

class SavedReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Saved Reports.
    
    Provides CRUD operations for the SavedReport model.
    """
    queryset = SavedReport.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = SavedReportSerializer
    permission_classes = [IsAuthenticated]

class ReportScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Report Schedules.
    
    Provides CRUD operations for the ReportSchedule model.
    """
    queryset = ReportSchedule.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]

class DashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Dashboards.
    
    Provides CRUD operations for the Dashboard model.
    """
    queryset = Dashboard.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]

class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Dashboard Widgets.
    
    Provides CRUD operations for the DashboardWidget model.
    """
    queryset = DashboardWidget.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]

class ReportMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Report Metrics.
    
    Provides CRUD operations for the ReportMetric model.
    """
    queryset = ReportMetric.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ReportMetricSerializer
    permission_classes = [IsAuthenticated]
