from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'

router = DefaultRouter()
router.register('items', views.InventoryItemViewSet, basename='item')

urlpatterns = [
    path('', include(router.urls)),
]
