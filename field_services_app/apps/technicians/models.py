"""
Models for the technicians app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Technician(models.Model):
    """
    Technician model extending the User model with additional fields.
    """
    
    STATUS_CHOICES = (
        ('available', _('Available')),
        ('busy', _('Busy')),
        ('on_leave', _('On Leave')),
        ('inactive', _('Inactive')),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='technician_profile',
        verbose_name=_('user')
    )
    employee_id = models.CharField(_('employee ID'), max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    skills = models.ManyToManyField(
        'Skill',
        related_name='technicians',
        blank=True,
        verbose_name=_('skills')
    )
    certifications = models.ManyToManyField(
        'Certification',
        related_name='technicians',
        blank=True,
        verbose_name=_('certifications')
    )
    job_title = models.CharField(_('job title'), max_length=100, blank=True)
    department = models.CharField(_('department'), max_length=100, blank=True)
    hire_date = models.DateField(_('hire date'), null=True, blank=True)
    phone_work = models.CharField(_('work phone'), max_length=30, blank=True)
    hourly_rate = models.DecimalField(
        _('hourly rate'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('notes'), blank=True)
    current_location = models.CharField(_('current location'), max_length=255, blank=True)
    last_location_update = models.DateTimeField(_('last location update'), null=True, blank=True)
    service_area = models.CharField(_('service area'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('technician')
        verbose_name_plural = _('technicians')
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return self.user.get_full_name() or self.user.email
    
    @property
    def full_name(self):
        """
        Return the technician's full name.
        """
        return self.user.get_full_name()
    
    @property
    def email(self):
        """
        Return the technician's email.
        """
        return self.user.email
    
    @property
    def phone(self):
        """
        Return the technician's personal phone or work phone if available.
        """
        return self.user.phone or self.phone_work
    
    @property
    def active_assignments_count(self):
        """
        Return the number of active work order assignments.
        """
        return self.work_order_assignments.exclude(
            status__in=['completed', 'rejected']
        ).count()


class Skill(models.Model):
    """
    Skills that technicians can possess.
    """
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('skill')
        verbose_name_plural = _('skills')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Certification(models.Model):
    """
    Certifications that technicians can earn.
    """
    
    name = models.CharField(_('name'), max_length=100)
    issuing_authority = models.CharField(_('issuing authority'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('certification')
        verbose_name_plural = _('certifications')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TechnicianCertification(models.Model):
    """
    Specific certification instances held by technicians.
    """
    
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='technician_certifications',
        verbose_name=_('technician')
    )
    certification = models.ForeignKey(
        Certification,
        on_delete=models.CASCADE,
        related_name='technician_instances',
        verbose_name=_('certification')
    )
    certificate_number = models.CharField(_('certificate number'), max_length=100, blank=True)
    issue_date = models.DateField(_('issue date'))
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    certificate_file = models.FileField(
        _('certificate file'),
        upload_to='technician_certificates/',
        null=True,
        blank=True
    )
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('technician certification')
        verbose_name_plural = _('technician certifications')
        ordering = ['technician', 'certification', '-issue_date']
        unique_together = ['technician', 'certification', 'certificate_number']
    
    def __str__(self):
        return f"{self.technician} - {self.certification}"
    
    @property
    def is_expired(self):
        """
        Check if the certification is expired.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.expiry_date and self.expiry_date < today


class TechnicianAvailability(models.Model):
    """
    Technician availability schedule.
    """
    
    TYPE_CHOICES = (
        ('regular', _('Regular Work Schedule')),
        ('overtime', _('Overtime')),
        ('on_call', _('On-call')),
        ('unavailable', _('Unavailable')),
        ('vacation', _('Vacation')),
        ('sick_leave', _('Sick Leave')),
        ('training', _('Training')),
    )
    
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='availability_schedule',
        verbose_name=_('technician')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='regular'
    )
    start_datetime = models.DateTimeField(_('start date/time'))
    end_datetime = models.DateTimeField(_('end date/time'))
    recurrence = models.CharField(_('recurrence pattern'), max_length=255, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('technician availability')
        verbose_name_plural = _('technician availabilities')
        ordering = ['technician', 'start_datetime']
    
    def __str__(self):
        return f"{self.technician} - {self.start_datetime.date()} - {self.get_type_display()}"
    
    @property
    def duration_hours(self):
        """
        Calculate the duration in hours.
        """
        delta = self.end_datetime - self.start_datetime
        return delta.total_seconds() / 3600


class TechnicianLocation(models.Model):
    """
    Tracking of technician locations.
    """
    
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='location_history',
        verbose_name=_('technician')
    )
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6)
    accuracy = models.FloatField(_('accuracy (meters)'), null=True, blank=True)
    altitude = models.FloatField(_('altitude (meters)'), null=True, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)
    recorded_at = models.DateTimeField(_('recorded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('technician location')
        verbose_name_plural = _('technician locations')
        ordering = ['technician', '-recorded_at']
    
    def __str__(self):
        return f"{self.technician} - {self.recorded_at}"
    
    def save(self, *args, **kwargs):
        """
        Override save to update technician's current location.
        """
        super().save(*args, **kwargs)
        
        # Update the technician's current location and timestamp
        self.technician.current_location = f"{self.latitude}, {self.longitude}"
        self.technician.last_location_update = self.recorded_at
        self.technician.save(update_fields=['current_location', 'last_location_update'])
