from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'communication'

router = DefaultRouter()
router.register('conversations', views.ConversationViewSet, basename='conversation')
router.register('participants', views.ConversationParticipantViewSet, basename='participant')
router.register('messages', views.MessageViewSet, basename='message')
router.register('attachments', views.MessageAttachmentViewSet, basename='attachment')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('email-templates', views.EmailTemplateViewSet, basename='email-template')
router.register('email-logs', views.EmailLogViewSet, basename='email-log')

urlpatterns = [
    path('', include(router.urls)),
]
