from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'training'

router = DefaultRouter()
router.register('courses', views.TrainingCourseViewSet, basename='course')
router.register('modules', views.TrainingModuleViewSet, basename='module')
router.register('quizzes', views.QuizViewSet, basename='quiz')
router.register('questions', views.QuizQuestionViewSet, basename='question')
router.register('enrollments', views.UserCourseEnrollmentViewSet, basename='enrollment')
router.register('progress', views.UserModuleProgressViewSet, basename='progress')
router.register('attempts', views.QuizAttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]
