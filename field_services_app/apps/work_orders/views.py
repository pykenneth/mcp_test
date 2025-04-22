from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import WorkOrder, WorkOrderItem, WorkOrderAssignment
# If serializers.py is created, uncomment this line
# from .serializers import WorkOrderSerializer, WorkOrderItemSerializer, WorkOrderAssignmentSerializer

class WorkOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Work Orders.
    
    Provides CRUD operations for the WorkOrder model.
    """
    queryset = WorkOrder.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated]

class WorkOrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Work Order Items.
    
    Provides CRUD operations for the WorkOrderItem model.
    """
    queryset = WorkOrderItem.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WorkOrderItemSerializer
    permission_classes = [IsAuthenticated]

class WorkOrderAssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Work Order Assignments.
    
    Provides CRUD operations for the WorkOrderAssignment model.
    """
    queryset = WorkOrderAssignment.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WorkOrderAssignmentSerializer
    permission_classes = [IsAuthenticated]
