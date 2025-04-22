"""
Models for the WhatsApp integration app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class WhatsAppAccount(models.Model):
    """
    WhatsApp Business Account configuration.
    """
    
    name = models.CharField(_('account name'), max_length=100)
    phone_number = models.CharField(_('phone number'), max_length=20, unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Twilio/WhatsApp Business API credentials
    twilio_account_sid = models.CharField(_('Twilio Account SID'), max_length=255, blank=True)
    twilio_auth_token = models.CharField(_('Twilio Auth Token'), max_length=255, blank=True)
    
    # Optional display settings
    display_name = models.CharField(_('display name'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    profile_image = models.ImageField(
        _('profile image'), 
        upload_to='whatsapp_profiles/',
        null=True,
        blank=True
    )
    
    # Webhook configuration
    webhook_url = models.URLField(_('webhook URL'), blank=True)
    webhook_secret = models.CharField(_('webhook secret'), max_length=255, blank=True)
    
    # Notification settings
    notify_new_messages = models.BooleanField(_('notify new messages'), default=True)
    notification_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='whatsapp_notifications',
        verbose_name=_('notification users')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('WhatsApp account')
        verbose_name_plural = _('WhatsApp accounts')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class WhatsAppTemplate(models.Model):
    """
    WhatsApp message templates for pre-approved business messaging.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('disabled', _('Disabled')),
    )
    
    CATEGORY_CHOICES = (
        ('account_update', _('Account Update')),
        ('alert_update', _('Alert Update')),
        ('appointment_update', _('Appointment Update')),
        ('auto_reply', _('Auto Reply')),
        ('issue_resolution', _('Issue Resolution')),
        ('payment_update', _('Payment Update')),
        ('personal_finance_update', _('Personal Finance Update')),
        ('reservation_update', _('Reservation Update')),
        ('shipping_update', _('Shipping Update')),
        ('ticket_update', _('Ticket Update')),
        ('transportation_update', _('Transportation Update')),
        ('other', _('Other')),
    )
    
    LANGUAGE_CHOICES = (
        ('en', _('English')),
        ('zh_HK', _('Hong Kong Cantonese')),
        ('zh_TW', _('Traditional Chinese')),
        ('zh_CN', _('Simplified Chinese')),
    )
    
    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name=_('WhatsApp account')
    )
    name = models.CharField(_('template name'), max_length=100)
    category = models.CharField(
        _('category'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    language = models.CharField(
        _('language'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en'
    )
    content = models.TextField(
        _('content'),
        help_text=_('Template content with {{variable}} placeholders')
    )
    sample_values = models.JSONField(_('sample values'), default=dict, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    twilio_template_sid = models.CharField(_('Twilio template SID'), max_length=255, blank=True)
    header_type = models.CharField(
        _('header type'),
        max_length=20,
        choices=(
            ('none', _('None')),
            ('text', _('Text')),
            ('image', _('Image')),
            ('document', _('Document')),
            ('video', _('Video')),
        ),
        default='none'
    )
    header_text = models.CharField(_('header text'), max_length=255, blank=True)
    footer_text = models.CharField(_('footer text'), max_length=255, blank=True)
    buttons = models.JSONField(_('buttons'), default=list, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_whatsapp_templates',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('WhatsApp template')
        verbose_name_plural = _('WhatsApp templates')
        ordering = ['account', 'name']
        unique_together = ['account', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"


class WhatsAppContact(models.Model):
    """
    WhatsApp contact model representing customers or contacts on WhatsApp.
    """
    
    phone_number = models.CharField(_('phone number'), max_length=20, unique=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_opted_in = models.BooleanField(_('opted in'), default=False)
    opt_in_date = models.DateTimeField(_('opt-in date'), null=True, blank=True)
    last_contacted = models.DateTimeField(_('last contacted'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Related models
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_contacts',
        verbose_name=_('user')
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_contacts',
        verbose_name=_('customer')
    )
    contact = models.ForeignKey(
        'customers.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_contacts',
        verbose_name=_('contact')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('WhatsApp contact')
        verbose_name_plural = _('WhatsApp contacts')
        ordering = ['name', 'phone_number']
    
    def __str__(self):
        if self.name:
            return f"{self.name} ({self.phone_number})"
        return self.phone_number


class WhatsAppConversation(models.Model):
    """
    WhatsApp conversation model representing a thread of messages.
    """
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('closed', _('Closed')),
        ('archived', _('Archived')),
    )
    
    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('WhatsApp account')
    )
    contact = models.ForeignKey(
        WhatsAppContact,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('contact')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    title = models.CharField(_('title'), max_length=255, blank=True)
    initiated_by = models.CharField(
        _('initiated by'),
        max_length=20,
        choices=(
            ('business', _('Business')),
            ('customer', _('Customer')),
        ),
        default='business'
    )
    
    # Session tracking (WhatsApp has 24-hour session windows)
    last_message_at = models.DateTimeField(_('last message at'), null=True, blank=True)
    session_expires_at = models.DateTimeField(_('session expires at'), null=True, blank=True)
    
    # Related objects
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_conversations',
        verbose_name=_('project')
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_conversations',
        verbose_name=_('work order')
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_whatsapp_conversations',
        verbose_name=_('assigned to')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('WhatsApp conversation')
        verbose_name_plural = _('WhatsApp conversations')
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        if self.title:
            return self.title
        return f"Conversation with {self.contact}"
    
    @property
    def is_in_session(self):
        """
        Check if the conversation is within the 24-hour session window.
        """
        from django.utils import timezone
        now = timezone.now()
        return self.session_expires_at and self.session_expires_at > now
    
    @property
    def message_count(self):
        """
        Return the number of messages in the conversation.
        """
        return self.messages.count()


class WhatsAppMessage(models.Model):
    """
    WhatsApp message model.
    """
    
    STATUS_CHOICES = (
        ('queued', _('Queued')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('read', _('Read')),
        ('failed', _('Failed')),
        ('received', _('Received')),
    )
    
    TYPE_CHOICES = (
        ('text', _('Text')),
        ('image', _('Image')),
        ('document', _('Document')),
        ('audio', _('Audio')),
        ('video', _('Video')),
        ('location', _('Location')),
        ('contact', _('Contact')),
        ('template', _('Template')),
        ('interactive', _('Interactive')),
        ('reaction', _('Reaction')),
        ('sticker', _('Sticker')),
        ('button', _('Button')),
        ('system', _('System')),
    )
    
    conversation = models.ForeignKey(
        WhatsAppConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversation')
    )
    message_id = models.CharField(_('message ID'), max_length=255, blank=True)
    direction = models.CharField(
        _('direction'),
        max_length=10,
        choices=(
            ('inbound', _('Inbound')),
            ('outbound', _('Outbound')),
        )
    )
    message_type = models.CharField(
        _('message type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(_('content'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )
    
    # For template messages
    template = models.ForeignKey(
        WhatsAppTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name=_('template')
    )
    template_variables = models.JSONField(_('template variables'), default=dict, blank=True)
    
    # For media messages
    media_url = models.URLField(_('media URL'), blank=True)
    media_id = models.CharField(_('media ID'), max_length=255, blank=True)
    media_mime_type = models.CharField(_('media MIME type'), max_length=100, blank=True)
    
    # For location messages
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    
    # For interactive messages
    interactive_type = models.CharField(_('interactive type'), max_length=50, blank=True)
    interactive_data = models.JSONField(_('interactive data'), default=dict, blank=True)
    
    # Tracking
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_whatsapp_messages',
        verbose_name=_('sent by')
    )
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Related to specific objects
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_messages',
        verbose_name=_('work order')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('WhatsApp message')
        verbose_name_plural = _('WhatsApp messages')
        ordering = ['conversation', 'created_at']
    
    def __str__(self):
        return f"{self.get_direction_display()} {self.get_message_type_display()} message ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """
        Override save to update conversation's last_message_at.
        """
        is_new = self.id is None
        super().save(*args, **kwargs)
        
        if is_new or self.status != self._loaded_values.get('status', None):
            from django.utils import timezone
            now = timezone.now()
            
            # Update conversation timestamp
            if self.direction == 'inbound' or (self.direction == 'outbound' and self.status == 'sent'):
                self.conversation.last_message_at = now
                
                # Set session expiry to 24 hours from now for new messages
                if self.direction == 'inbound':
                    from datetime import timedelta
                    self.conversation.session_expires_at = now + timedelta(hours=24)
                
                self.conversation.save(update_fields=['last_message_at', 'session_expires_at'])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original values for comparison in save method
        self._loaded_values = {
            'status': self.status,
        }


class WhatsAppMediaFile(models.Model):
    """
    WhatsApp media file model for storing media files locally.
    """
    
    message = models.ForeignKey(
        WhatsAppMessage,
        on_delete=models.CASCADE,
        related_name='media_files',
        verbose_name=_('message')
    )
    file = models.FileField(_('file'), upload_to='whatsapp_media/%Y/%m/')
    media_type = models.CharField(_('media type'), max_length=50)
    media_id = models.CharField(_('media ID'), max_length=255, blank=True)
    mime_type = models.CharField(_('MIME type'), max_length=100, blank=True)
    file_name = models.CharField(_('file name'), max_length=255, blank=True)
    file_size = models.PositiveIntegerField(_('file size (bytes)'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('WhatsApp media file')
        verbose_name_plural = _('WhatsApp media files')
    
    def __str__(self):
        return f"{self.media_type} media for message {self.message.id}"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate file size.
        """
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class WhatsAppWebhookLog(models.Model):
    """
    Log of incoming webhook events from the WhatsApp API.
    """
    
    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='webhook_logs',
        verbose_name=_('WhatsApp account')
    )
    event_type = models.CharField(_('event type'), max_length=100)
    event_id = models.CharField(_('event ID'), max_length=255, blank=True)
    payload = models.JSONField(_('payload'))
    processed = models.BooleanField(_('processed'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    
    received_at = models.DateTimeField(_('received at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('WhatsApp webhook log')
        verbose_name_plural = _('WhatsApp webhook logs')
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.event_type} webhook at {self.received_at}"
