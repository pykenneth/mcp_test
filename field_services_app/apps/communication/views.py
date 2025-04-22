from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    Conversation, ConversationParticipant, Message, 
    MessageAttachment, Notification, EmailTemplate, EmailLog
)
# If serializers.py is created, uncomment this line
# from .serializers import (
#     ConversationSerializer, ConversationParticipantSerializer, MessageSerializer,
#     MessageAttachmentSerializer, NotificationSerializer, EmailTemplateSerializer, EmailLogSerializer
# )

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Conversations.
    
    Provides CRUD operations for the Conversation model.
    """
    queryset = Conversation.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

class ConversationParticipantViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Conversation Participants.
    
    Provides CRUD operations for the ConversationParticipant model.
    """
    queryset = ConversationParticipant.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = ConversationParticipantSerializer
    permission_classes = [IsAuthenticated]

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Messages.
    
    Provides CRUD operations for the Message model.
    """
    queryset = Message.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

class MessageAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Message Attachments.
    
    Provides CRUD operations for the MessageAttachment model.
    """
    queryset = MessageAttachment.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = MessageAttachmentSerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Notifications.
    
    Provides CRUD operations for the Notification model.
    """
    queryset = Notification.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Email Templates.
    
    Provides CRUD operations for the EmailTemplate model.
    """
    queryset = EmailTemplate.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]

class EmailLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Email Logs.
    
    Provides CRUD operations for the EmailLog model.
    """
    queryset = EmailLog.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
