from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'documents'

router = DefaultRouter()
router.register('', views.DocumentViewSet, basename='document')
router.register('categories', views.DocumentCategoryViewSet, basename='category')
router.register('templates', views.DocumentTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
