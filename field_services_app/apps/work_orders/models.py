"""
Models for the work_orders app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class WorkOrder(models.Model):
    """
    Work order model representing a service request or job.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('invoiced', _('Invoiced')),
        ('paid', _('Paid')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    
    TYPE_CHOICES = (
        ('installation', _('Installation')),
        ('maintenance', _('Maintenance')),
        ('repair', _('Repair')),
        ('inspection', _('Inspection')),
        ('design', _('Design')),
        ('consultation', _('Consultation')),
        ('other', _('Other')),
    )
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='work_orders',
        verbose_name=_('project')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.CASCADE,
        related_name='work_orders',
        verbose_name=_('customer')
    )
    contact = models.ForeignKey(
        'customers.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name=_('contact')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='installation'
    )
    location = models.CharField(_('location'), max_length=255, blank=True)
    scheduled_start = models.DateTimeField(_('scheduled start'), null=True, blank=True)
    scheduled_end = models.DateTimeField(_('scheduled end'), null=True, blank=True)
    actual_start = models.DateTimeField(_('actual start'), null=True, blank=True)
    actual_end = models.DateTimeField(_('actual end'), null=True, blank=True)
    estimated_duration = models.PositiveIntegerField(
        _('estimated duration (minutes)'),
        default=0,
        help_text=_('Estimated duration in minutes')
    )
    estimated_cost = models.DecimalField(
        _('estimated cost'),
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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_work_orders',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('work order')
        verbose_name_plural = _('work orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def is_overdue(self):
        """
        Check if the work order is overdue.
        """
        from django.utils import timezone
        now = timezone.now()
        return (
            self.scheduled_end and 
            now > self.scheduled_end and 
            self.status not in ['completed', 'cancelled', 'invoiced', 'paid']
        )
    
    @property
    def duration(self):
        """
        Calculate the actual duration of the work order in minutes.
        """
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return 0
    
    @property
    def assigned_technicians(self):
        """
        Return a list of technicians assigned to this work order.
        """
        return [assignment.technician for assignment in self.assignments.all()]


class WorkOrderItem(models.Model):
    """
    Items (materials, services, etc.) included in a work order.
    """
    
    TYPE_CHOICES = (
        ('material', _('Material')),
        ('labor', _('Labor')),
        ('equipment', _('Equipment')),
        ('service', _('Service')),
        ('fee', _('Fee')),
        ('other', _('Other')),
    )
    
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('work order')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='material'
    )
    item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_order_items',
        verbose_name=_('inventory item')
    )
    description = models.CharField(_('description'), max_length=255)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(_('total price'), max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('work order item')
        verbose_name_plural = _('work order items')
        ordering = ['work_order', 'type', 'description']
    
    def __str__(self):
        return f"{self.description} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate total price.
        """
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class WorkOrderAssignment(models.Model):
    """
    Assignment of technicians to work orders.
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
    )
    
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('work order')
    )
    technician = models.ForeignKey(
        'technicians.Technician',
        on_delete=models.CASCADE,
        related_name='work_order_assignments',
        verbose_name=_('technician')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_work_orders',
        verbose_name=_('assigned by')
    )
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    accepted_at = models.DateTimeField(_('accepted at'), null=True, blank=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('work order assignment')
        verbose_name_plural = _('work order assignments')
        ordering = ['work_order', 'assigned_at']
        unique_together = ['work_order', 'technician']
    
    def __str__(self):
        return f"{self.work_order.title} - {self.technician.user.get_full_name()}"


class WorkOrderStatus(models.Model):
    """
    History of work order status changes for audit purposes.
    """
    
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('work order')
    )
    status = models.CharField(_('status'), max_length=20, choices=WorkOrder.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='work_order_status_changes',
        verbose_name=_('changed by')
    )
    changed_at = models.DateTimeField(_('changed at'), auto_now_add=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('work order status')
        verbose_name_plural = _('work order statuses')
        ordering = ['work_order', '-changed_at']
    
    def __str__(self):
        return f"{self.work_order.title} - {self.get_status_display()}"


class WorkOrderAttachment(models.Model):
    """
    File attachments for work orders.
    """
    
    TYPE_CHOICES = (
        ('photo', _('Photo')),
        ('document', _('Document')),
        ('contract', _('Contract')),
        ('invoice', _('Invoice')),
        ('other', _('Other')),
    )
    
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('work order')
    )
    file = models.FileField(_('file'), upload_to='work_order_attachments/')
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='photo'
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_work_order_attachments',
        verbose_name=_('uploaded by')
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('work order attachment')
        verbose_name_plural = _('work order attachments')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name


class WorkOrderSignature(models.Model):
    """
    Digital signatures for completed work orders.
    """
    
    TYPE_CHOICES = (
        ('technician', _('Technician')),
        ('customer', _('Customer')),
        ('supervisor', _('Supervisor')),
        ('inspector', _('Inspector')),
    )
    
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='signatures',
        verbose_name=_('work order')
    )
    signature_image = models.ImageField(_('signature'), upload_to='work_order_signatures/')
    signer_name = models.CharField(_('signer name'), max_length=255)
    signer_title = models.CharField(_('signer title'), max_length=255, blank=True)
    signer_type = models.CharField(
        _('signer type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='customer'
    )
    signed_at = models.DateTimeField(_('signed at'), auto_now_add=True)
    notes = models.TextField(_('notes'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('work order signature')
        verbose_name_plural = _('work order signatures')
        ordering = ['work_order', '-signed_at']
    
    def __str__(self):
        return f"{self.signer_name} ({self.get_signer_type_display()})"


class WorkOrderNote(models.Model):
    """
    Notes related to work orders.
    """
    
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('work order')
    )
    content = models.TextField(_('content'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='work_order_notes',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('work order note')
        verbose_name_plural = _('work order notes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.work_order.title}"
