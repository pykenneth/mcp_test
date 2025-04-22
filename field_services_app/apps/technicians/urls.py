from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'technicians'

router = DefaultRouter()
router.register('', views.TechnicianViewSet, basename='technician')
router.register('skills', views.SkillViewSet, basename='skill')
router.register('certifications', views.CertificationViewSet, basename='certification')
router.register('availability', views.TechnicianAvailabilityViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
]
