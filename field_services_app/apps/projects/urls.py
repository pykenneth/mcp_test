from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'projects'

router = DefaultRouter()
router.register('', views.ProjectViewSet, basename='project')
router.register('tasks', views.ProjectTaskViewSet, basename='task')
router.register('milestones', views.ProjectMilestoneViewSet, basename='milestone')

urlpatterns = [
    path('', include(router.urls)),
]
