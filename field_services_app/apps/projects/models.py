"""
Models for the projects app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Project(models.Model):
    """
    Project model representing a fit-out project.
    """
    
    STATUS_CHOICES = (
        ('planning', _('Planning')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
        ('cancelled', _('Cancelled')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    company = models.ForeignKey(
        'customers.Company',
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_('company')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    location = models.CharField(_('location'), max_length=255)
    budget = models.DecimalField(
        _('budget'),
        max_digits=14,
        decimal_places=2,
        default=0
    )
    actual_cost = models.DecimalField(
        _('actual cost'),
        max_digits=14,
        decimal_places=2,
        default=0
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects',
        verbose_name=_('project manager')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def progress(self):
        """
        Calculate project progress based on completed tasks.
        """
        tasks = self.tasks.all()
        if not tasks:
            return 0
        
        completed_tasks = tasks.filter(status='completed').count()
        return (completed_tasks / tasks.count()) * 100
    
    @property
    def is_overdue(self):
        """
        Check if the project is overdue.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.end_date < today and self.status not in ['completed', 'cancelled']


class ProjectTask(MPTTModel):
    """
    Task model for projects with hierarchical structure using MPTT.
    """
    
    STATUS_CHOICES = (
        ('to_do', _('To Do')),
        ('in_progress', _('In Progress')),
        ('review', _('In Review')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('project')
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent task')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='to_do'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name=_('assigned to')
    )
    start_date = models.DateField(_('start date'), null=True, blank=True)
    due_date = models.DateField(_('due date'), null=True, blank=True)
    estimated_hours = models.DecimalField(
        _('estimated hours'),
        max_digits=8,
        decimal_places=2,
        default=0
    )
    actual_hours = models.DecimalField(
        _('actual hours'),
        max_digits=8,
        decimal_places=2,
        default=0
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('project task')
        verbose_name_plural = _('project tasks')
        ordering = ['priority', 'due_date']
    
    class MPTTMeta:
        order_insertion_by = ['title']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """
        Check if the task is overdue.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.due_date and self.due_date < today and self.status not in ['completed', 'cancelled']


class ProjectAttachment(models.Model):
    """
    File attachments for projects.
    """
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('project')
    )
    file = models.FileField(_('file'), upload_to='project_attachments/')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_project_attachments',
        verbose_name=_('uploaded by')
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('project attachment')
        verbose_name_plural = _('project attachments')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name


class ProjectNote(models.Model):
    """
    Notes for projects.
    """
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('project')
    )
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='project_notes',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('project note')
        verbose_name_plural = _('project notes')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ProjectMilestone(models.Model):
    """
    Milestones for projects.
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('delayed', _('Delayed')),
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name=_('project')
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateField(_('due date'))
    completion_date = models.DateField(_('completion date'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_milestones',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('project milestone')
        verbose_name_plural = _('project milestones')
        ordering = ['due_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """
        Check if the milestone is overdue.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.due_date < today and self.status not in ['completed']
