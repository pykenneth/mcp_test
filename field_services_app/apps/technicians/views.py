from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Technician, Skill, Certification, TechnicianAvailability
# If serializers.py is created, uncomment this line
# from .serializers import TechnicianSerializer, SkillSerializer, CertificationSerializer, TechnicianAvailabilitySerializer

class TechnicianViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Technicians.
    
    Provides CRUD operations for the Technician model.
    """
    queryset = Technician.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = TechnicianSerializer
    permission_classes = [IsAuthenticated]

class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Technician Skills.
    
    Provides CRUD operations for the Skill model.
    """
    queryset = Skill.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

class CertificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Certifications.
    
    Provides CRUD operations for the Certification model.
    """
    queryset = Certification.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]

class TechnicianAvailabilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Technician Availability.
    
    Provides CRUD operations for the TechnicianAvailability model.
    """
    queryset = TechnicianAvailability.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = TechnicianAvailabilitySerializer
    permission_classes = [IsAuthenticated]
