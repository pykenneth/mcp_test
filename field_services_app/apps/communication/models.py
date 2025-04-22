"""
Models for the communication app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    """
    Conversation model for group or direct messaging.
    """
    
    TYPE_CHOICES = (
        ('direct', _('Direct Message')),
        ('group', _('Group Chat')),
        ('project', _('Project Chat')),
        ('work_order', _('Work Order Chat')),
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='direct'
    )
    title = models.CharField(_('title'), max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_conversations',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Related objects
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name=_('project')
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name=_('work order')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name=_('customer')
    )
    
    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.type == 'direct':
            participants = self.participants.all()
            return f"Chat between {' and '.join([p.user.get_full_name() for p in participants])}"
        elif self.type == 'project' and self.project:
            return f"Project: {self.project.name}"
        elif self.type == 'work_order' and self.work_order:
            return f"Work Order: {self.work_order.title}"
        else:
            return f"Conversation #{self.id}"
    
    @property
    def participant_count(self):
        """
        Return the number of participants in the conversation.
        """
        return self.participants.count()
    
    @property
    def last_message(self):
        """
        Return the last message in the conversation.
        """
        return self.messages.order_by('-sent_at').first()


class ConversationParticipant(models.Model):
    """
    Junction model for conversation participants.
    """
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_('conversation')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('user')
    )
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    is_admin = models.BooleanField(_('admin'), default=False)
    last_read_at = models.DateTimeField(_('last read at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('conversation participant')
        verbose_name_plural = _('conversation participants')
        ordering = ['conversation', 'joined_at']
        unique_together = ['conversation', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.conversation}"
    
    @property
    def unread_count(self):
        """
        Return the number of unread messages.
        """
        if not self.last_read_at:
            return self.conversation.messages.count()
        return self.conversation.messages.filter(sent_at__gt=self.last_read_at).count()


class Message(models.Model):
    """
    Message model for conversations.
    """
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversation')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_messages',
        verbose_name=_('sender')
    )
    content = models.TextField(_('content'))
    sent_at = models.DateTimeField(_('sent at'), auto_now_add=True)
    is_system_message = models.BooleanField(_('system message'), default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('reply to')
    )
    
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['conversation', 'sent_at']
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name() if self.sender else 'System'} at {self.sent_at}"
    
    def save(self, *args, **kwargs):
        """
        Override save to update conversation updated_at.
        """
        super().save(*args, **kwargs)
        # Update conversation last modified time
        self.conversation.updated_at = self.sent_at
        self.conversation.save(update_fields=['updated_at'])


class MessageAttachment(models.Model):
    """
    Attachment model for message attachments.
    """
    
    TYPE_CHOICES = (
        ('image', _('Image')),
        ('file', _('File')),
        ('audio', _('Audio')),
        ('video', _('Video')),
        ('location', _('Location')),
        ('contact', _('Contact')),
    )
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('message')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='file'
    )
    file = models.FileField(_('file'), upload_to='message_attachments/%Y/%m/', null=True, blank=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    content_type = models.CharField(_('content type'), max_length=100, blank=True)
    size = models.PositiveIntegerField(_('size (bytes)'), default=0)
    width = models.PositiveIntegerField(_('width'), null=True, blank=True)
    height = models.PositiveIntegerField(_('height'), null=True, blank=True)
    duration = models.PositiveIntegerField(_('duration (seconds)'), null=True, blank=True)
    thumbnail = models.ImageField(_('thumbnail'), upload_to='message_thumbnails/%Y/%m/', null=True, blank=True)
    
    # For location attachments
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        verbose_name = _('message attachment')
        verbose_name_plural = _('message attachments')
    
    def __str__(self):
        return f"{self.get_type_display()} attachment for message {self.message.id}"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate file size.
        """
        if self.file:
            self.size = self.file.size
            self.name = self.name or self.file.name
        super().save(*args, **kwargs)


class Notification(models.Model):
    """
    Notification model for system notifications.
    """
    
    TYPE_CHOICES = (
        ('info', _('Information')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('task_assigned', _('Task Assigned')),
        ('task_completed', _('Task Completed')),
        ('work_order_assigned', _('Work Order Assigned')),
        ('work_order_status', _('Work Order Status')),
        ('message', _('New Message')),
        ('document', _('Document Update')),
        ('schedule', _('Schedule Update')),
        ('inventory', _('Inventory Alert')),
        ('system', _('System')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('user')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='info'
    )
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    is_read = models.BooleanField(_('read'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)
    
    # Optional related objects
    url = models.CharField(_('URL'), max_length=255, blank=True)
    data = models.JSONField(_('data'), default=dict, blank=True)
    
    # Content type relations
    content_type = models.CharField(_('content type'), max_length=50, blank=True)
    object_id = models.PositiveIntegerField(_('object ID'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} for {self.user.get_full_name()}"
    
    def mark_as_read(self):
        """
        Mark the notification as read.
        """
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class EmailTemplate(models.Model):
    """
    Email template model for sending formatted emails.
    """
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    subject = models.CharField(_('subject'), max_length=255)
    html_content = models.TextField(_('HTML content'))
    text_content = models.TextField(_('text content'), blank=True)
    variables = models.TextField(
        _('template variables'),
        blank=True,
        help_text=_('Variables defined with {{variable_name}} format')
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_email_templates',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EmailLog(models.Model):
    """
    Email log for tracking sent emails.
    """
    
    STATUS_CHOICES = (
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('opened', _('Opened')),
        ('clicked', _('Clicked')),
        ('bounced', _('Bounced')),
        ('failed', _('Failed')),
    )
    
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails',
        verbose_name=_('template')
    )
    recipient_email = models.EmailField(_('recipient email'))
    recipient_name = models.CharField(_('recipient name'), max_length=255, blank=True)
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'), blank=True)
    sender_email = models.EmailField(_('sender email'))
    sender_name = models.CharField(_('sender name'), max_length=255, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent'
    )
    sent_at = models.DateTimeField(_('sent at'), auto_now_add=True)
    opened_at = models.DateTimeField(_('opened at'), null=True, blank=True)
    clicked_at = models.DateTimeField(_('clicked at'), null=True, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Related objects
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_emails',
        verbose_name=_('user')
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails',
        verbose_name=_('project')
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails',
        verbose_name=_('work order')
    )
    
    class Meta:
        verbose_name = _('email log')
        verbose_name_plural = _('email logs')
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.subject}"
