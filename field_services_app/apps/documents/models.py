"""
Models for the documents app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DocumentCategory(models.Model):
    """
    Category model for document organization.
    """
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent category')
    )
    
    class Meta:
        verbose_name = _('document category')
        verbose_name_plural = _('document categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """
        Return the full category path.
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Document(models.Model):
    """
    Document model for storing document metadata and files.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('review', _('Under Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('archived', _('Archived')),
        ('expired', _('Expired')),
    )
    
    TYPE_CHOICES = (
        ('contract', _('Contract')),
        ('specification', _('Specification')),
        ('drawing', _('Drawing')),
        ('permit', _('Permit')),
        ('certificate', _('Certificate')),
        ('report', _('Report')),
        ('invoice', _('Invoice')),
        ('proposal', _('Proposal')),
        ('checklist', _('Checklist')),
        ('manual', _('Manual')),
        ('photo', _('Photo')),
        ('other', _('Other')),
    )
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('category')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='other'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    file = models.FileField(_('file'), upload_to='documents/%Y/%m/')
    file_size = models.PositiveIntegerField(_('file size (bytes)'), default=0)
    file_type = models.CharField(_('file type'), max_length=50, blank=True)
    version = models.CharField(_('version'), max_length=50, default='1.0')
    reference_number = models.CharField(_('reference number'), max_length=100, blank=True)
    effective_date = models.DateField(_('effective date'), null=True, blank=True)
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    tags = models.CharField(_('tags'), max_length=255, blank=True)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('project')
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('work order')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('customer')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_documents',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate file size and type.
        """
        if self.file:
            self.file_size = self.file.size
            self.file_type = self.file.name.split('.')[-1].lower() if '.' in self.file.name else ''
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """
        Check if the document is expired.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.expiry_date and self.expiry_date < today


class DocumentVersion(models.Model):
    """
    Document version history.
    """
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('document')
    )
    version_number = models.CharField(_('version number'), max_length=50)
    file = models.FileField(_('file'), upload_to='document_versions/%Y/%m/')
    file_size = models.PositiveIntegerField(_('file size (bytes)'), default=0)
    change_summary = models.TextField(_('change summary'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_document_versions',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('document version')
        verbose_name_plural = _('document versions')
        ordering = ['document', '-created_at']
        unique_together = ['document', 'version_number']
    
    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate file size.
        """
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class DocumentPermission(models.Model):
    """
    Access permissions for documents.
    """
    
    PERMISSION_CHOICES = (
        ('view', _('View')),
        ('edit', _('Edit')),
        ('delete', _('Delete')),
        ('approve', _('Approve')),
    )
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name=_('document')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_permissions',
        verbose_name=_('user')
    )
    permission = models.CharField(
        _('permission'),
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='view'
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_document_permissions',
        verbose_name=_('granted by')
    )
    granted_at = models.DateTimeField(_('granted at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('document permission')
        verbose_name_plural = _('document permissions')
        ordering = ['document', 'user', 'permission']
        unique_together = ['document', 'user', 'permission']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.document.title} - {self.get_permission_display()}"


class DocumentComment(models.Model):
    """
    Comments on documents.
    """
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('document')
    )
    content = models.TextField(_('content'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_comments',
        verbose_name=_('author')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('document comment')
        verbose_name_plural = _('document comments')
        ordering = ['document', '-created_at']
    
    def __str__(self):
        return f"Comment on {self.document.title} by {self.author.get_full_name()}"


class DocumentRequest(models.Model):
    """
    Document requests for approvals, reviews, etc.
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    )
    
    TYPE_CHOICES = (
        ('approval', _('Approval')),
        ('review', _('Review')),
        ('signature', _('Signature')),
        ('other', _('Other')),
    )
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name=_('document')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='approval'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_document_actions',
        verbose_name=_('requested by')
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_document_actions',
        verbose_name=_('assigned to')
    )
    message = models.TextField(_('message'), blank=True)
    due_date = models.DateField(_('due date'), null=True, blank=True)
    requested_at = models.DateTimeField(_('requested at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    response_message = models.TextField(_('response message'), blank=True)
    
    class Meta:
        verbose_name = _('document request')
        verbose_name_plural = _('document requests')
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.get_type_display()} request for {self.document.title}"


class DocumentTemplate(models.Model):
    """
    Reusable document templates.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates',
        verbose_name=_('category')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Document.TYPE_CHOICES,
        default='other'
    )
    file = models.FileField(_('file'), upload_to='document_templates/')
    variables = models.TextField(
        _('template variables'),
        blank=True,
        help_text=_('Variables defined with {variable_name} format')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_document_templates',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('document template')
        verbose_name_plural = _('document templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name
