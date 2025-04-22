from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'work_orders'

router = DefaultRouter()
router.register('', views.WorkOrderViewSet, basename='order')
router.register('items', views.WorkOrderItemViewSet, basename='item')
router.register('assignments', views.WorkOrderAssignmentViewSet, basename='assignment')

urlpatterns = [
    path('', include(router.urls)),
]
