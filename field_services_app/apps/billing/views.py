from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Invoice, InvoiceItem, Payment, PricingTier, PricingItem, Expense
# If serializers.py is created, uncomment this line
# from .serializers import (
#     InvoiceSerializer, InvoiceItemSerializer, PaymentSerializer,
#     PricingTierSerializer, PricingItemSerializer, ExpenseSerializer
# )

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Invoices.
    
    Provides CRUD operations for the Invoice model.
    """
    queryset = Invoice.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

class InvoiceItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Invoice Items.
    
    Provides CRUD operations for the InvoiceItem model.
    """
    queryset = InvoiceItem.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Payments.
    
    Provides CRUD operations for the Payment model.
    """
    queryset = Payment.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

class PricingTierViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Pricing Tiers.
    
    Provides CRUD operations for the PricingTier model.
    """
    queryset = PricingTier.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = PricingTierSerializer
    permission_classes = [IsAuthenticated]

class PricingItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Pricing Items.
    
    Provides CRUD operations for the PricingItem model.
    """
    queryset = PricingItem.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = PricingItemSerializer
    permission_classes = [IsAuthenticated]

class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Expenses.
    
    Provides CRUD operations for the Expense model.
    """
    queryset = Expense.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
