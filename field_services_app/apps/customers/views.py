from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company, Contact, Customer
# If serializers.py is created, uncomment this line
# from .serializers import CompanySerializer, ContactSerializer, CustomerSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Companies.
    
    Provides CRUD operations for the Company model.
    """
    queryset = Company.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Contacts.
    
    Provides CRUD operations for the Contact model.
    """
    queryset = Contact.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Customers.
    
    Provides CRUD operations for the Customer model.
    """
    queryset = Customer.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
