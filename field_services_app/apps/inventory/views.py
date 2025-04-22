from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import InventoryItem
# If serializers.py is created, uncomment this line
# from .serializers import InventoryItemSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Inventory items.
    
    Provides CRUD operations for the InventoryItem model.
    """
    queryset = InventoryItem.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
