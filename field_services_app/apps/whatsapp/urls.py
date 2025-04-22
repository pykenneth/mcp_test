from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'whatsapp'

router = DefaultRouter()
router.register('accounts', views.WhatsAppAccountViewSet, basename='account')
router.register('templates', views.WhatsAppTemplateViewSet, basename='template')
router.register('contacts', views.WhatsAppContactViewSet, basename='contact')
router.register('conversations', views.WhatsAppConversationViewSet, basename='conversation')
router.register('messages', views.WhatsAppMessageViewSet, basename='message')
router.register('media-files', views.WhatsAppMediaFileViewSet, basename='media-file')

urlpatterns = [
    path('', include(router.urls)),
]
