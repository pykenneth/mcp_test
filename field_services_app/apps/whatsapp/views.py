from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    WhatsAppAccount, WhatsAppTemplate, WhatsAppContact,
    WhatsAppConversation, WhatsAppMessage, WhatsAppMediaFile
)
# If serializers.py is created, uncomment this line
# from .serializers import (
#     WhatsAppAccountSerializer, WhatsAppTemplateSerializer, WhatsAppContactSerializer,
#     WhatsAppConversationSerializer, WhatsAppMessageSerializer, WhatsAppMediaFileSerializer
# )

class WhatsAppAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp Business Accounts.
    
    Provides CRUD operations for the WhatsAppAccount model.
    """
    queryset = WhatsAppAccount.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WhatsAppAccountSerializer
    permission_classes = [IsAuthenticated]

class WhatsAppTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp Templates.
    
    Provides CRUD operations for the WhatsAppTemplate model.
    """
    queryset = WhatsAppTemplate.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WhatsAppTemplateSerializer
    permission_classes = [IsAuthenticated]

class WhatsAppContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp Contacts.
    
    Provides CRUD operations for the WhatsAppContact model.
    """
    queryset = WhatsAppContact.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WhatsAppContactSerializer
    permission_classes = [IsAuthenticated]

class WhatsAppConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp Conversations.
    
    Provides CRUD operations for the WhatsAppConversation model.
    """
    queryset = WhatsAppConversation.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WhatsAppConversationSerializer
    permission_classes = [IsAuthenticated]

class WhatsAppMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp Messages.
    
    Provides CRUD operations for the WhatsAppMessage model.
    """
    queryset = WhatsAppMessage.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated]

class WhatsAppMediaFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp Media Files.
    
    Provides CRUD operations for the WhatsAppMediaFile model.
    """
    queryset = WhatsAppMediaFile.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = WhatsAppMediaFileSerializer
    permission_classes = [IsAuthenticated]
