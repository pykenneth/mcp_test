from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Document, DocumentCategory, DocumentTemplate
# If serializers.py is created, uncomment this line
# from .serializers import DocumentSerializer, DocumentCategorySerializer, DocumentTemplateSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Documents.
    
    Provides CRUD operations for the Document model.
    """
    queryset = Document.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Document Categories.
    
    Provides CRUD operations for the DocumentCategory model.
    """
    queryset = DocumentCategory.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = DocumentCategorySerializer
    permission_classes = [IsAuthenticated]

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Document Templates.
    
    Provides CRUD operations for the DocumentTemplate model.
    """
    queryset = DocumentTemplate.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
