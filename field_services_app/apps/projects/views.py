from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project, ProjectTask, ProjectMilestone
# If serializers.py is created, uncomment this line
# from .serializers import ProjectSerializer, ProjectTaskSerializer, ProjectMilestoneSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Projects.
    
    Provides CRUD operations for the Project model.
    """
    queryset = Project.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

class ProjectTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Project Tasks.
    
    Provides CRUD operations for the ProjectTask model.
    """
    queryset = ProjectTask.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]

class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Project Milestones.
    
    Provides CRUD operations for the ProjectMilestone model.
    """
    queryset = ProjectMilestone.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ProjectMilestoneSerializer
    permission_classes = [IsAuthenticated]
