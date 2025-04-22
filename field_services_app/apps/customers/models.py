"""
Models for the customers app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """
    Company model representing customer organizations.
    """
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('prospect', _('Prospect')),
        ('former', _('Former Client')),
    )
    
    name = models.CharField(_('company name'), max_length=255)
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state_province = models.CharField(_('state/province'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    phone = models.CharField(_('phone'), max_length=30, blank=True)
    email = models.EmailField(_('email'), blank=True)
    website = models.URLField(_('website'), blank=True)
    tax_number = models.CharField(_('tax identification number'), max_length=50, blank=True)
    industry = models.CharField(_('industry'), max_length=100, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    notes = models.TextField(_('notes'), blank=True)
    account_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_companies',
        verbose_name=_('account manager')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def primary_contact(self):
        """
        Return the primary contact for this company.
        """
        return self.contacts.filter(is_primary=True).first()
    
    @property
    def active_projects_count(self):
        """
        Return the number of active projects for this company.
        """
        return self.projects.exclude(status__in=['completed', 'cancelled']).count()


class Contact(models.Model):
    """
    Contact model representing individual contacts at customer companies.
    """
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name=_('company')
    )
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    position = models.CharField(_('position'), max_length=100, blank=True)
    department = models.CharField(_('department'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=30, blank=True)
    mobile = models.CharField(_('mobile'), max_length=30, blank=True)
    is_primary = models.BooleanField(_('primary contact'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        ordering = ['company', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure only one primary contact per company.
        """
        if self.is_primary:
            # Set all other contacts for this company to not primary
            Contact.objects.filter(company=self.company, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """
        Return the contact's full name.
        """
        return f"{self.first_name} {self.last_name}"


class Customer(models.Model):
    """
    Customer model linking companies to user accounts.
    This allows tracking user-specific customer data.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('user')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='customer_users',
        verbose_name=_('company')
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        verbose_name=_('contact')
    )
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.company.name})"


class CustomerAttachment(models.Model):
    """
    File attachments for customer companies.
    """
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('company')
    )
    file = models.FileField(_('file'), upload_to='customer_attachments/')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_customer_attachments',
        verbose_name=_('uploaded by')
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('customer attachment')
        verbose_name_plural = _('customer attachments')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name
