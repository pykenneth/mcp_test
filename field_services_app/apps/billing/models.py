"""
Models for the billing app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Invoice(models.Model):
    """
    Invoice model for billing customers.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('partial', _('Partially Paid')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('void', _('Void')),
    )
    
    # Invoice identification
    number = models.CharField(_('invoice number'), max_length=50, unique=True)
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    
    # Related models
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('customer')
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('project')
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('work order')
    )
    
    # Customer details
    billing_contact = models.ForeignKey(
        'customers.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('billing contact')
    )
    billing_address = models.TextField(_('billing address'), blank=True)
    shipping_address = models.TextField(_('shipping address'), blank=True)
    
    # Dates
    issue_date = models.DateField(_('issue date'), null=True, blank=True)
    due_date = models.DateField(_('due date'), null=True, blank=True)
    payment_date = models.DateField(_('payment date'), null=True, blank=True)
    
    # Financial details
    currency = models.CharField(_('currency'), max_length=3, default='HKD')
    tax_percent = models.DecimalField(_('tax percentage'), max_digits=5, decimal_places=2, default=0)
    discount_percent = models.DecimalField(_('discount percentage'), max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('discount amount'), max_digits=14, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(_('shipping amount'), max_digits=14, decimal_places=2, default=0)
    subtotal = models.DecimalField(_('subtotal'), max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(_('amount paid'), max_digits=14, decimal_places=2, default=0)
    amount_due = models.DecimalField(_('amount due'), max_digits=14, decimal_places=2, default=0)
    
    # Meta information
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField(_('notes'), blank=True)
    terms = models.TextField(_('terms and conditions'), blank=True)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # File attachment
    pdf_file = models.FileField(_('PDF file'), upload_to='invoices/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        ordering = ['-issue_date', '-number']
    
    def __str__(self):
        return f"Invoice #{self.number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate totals.
        """
        # Calculate subtotal from line items
        if self.id:  # Only if the invoice already exists
            self.subtotal = sum(item.total for item in self.line_items.all())
            
            # Calculate tax amount
            self.tax_amount = self.subtotal * (self.tax_percent / 100)
            
            # Calculate discount amount if using percentage
            if self.discount_percent > 0:
                self.discount_amount = self.subtotal * (self.discount_percent / 100)
            
            # Calculate total
            self.total = self.subtotal + self.tax_amount + self.shipping_amount - self.discount_amount
            
            # Calculate amount due
            self.amount_due = self.total - self.amount_paid
            
            # Update status based on payments
            if self.amount_due <= 0:
                self.status = 'paid'
            elif self.amount_paid > 0:
                self.status = 'partial'
            
            # Check if overdue
            from django.utils import timezone
            today = timezone.now().date()
            if self.due_date and today > self.due_date and self.amount_due > 0:
                self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    @property
    def is_paid(self):
        """
        Check if the invoice is fully paid.
        """
        return self.amount_due <= 0
    
    @property
    def is_overdue(self):
        """
        Check if the invoice is overdue.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.due_date and today > self.due_date and self.amount_due > 0
    
    @property
    def payment_status_display(self):
        """
        Return a display string for the payment status.
        """
        if self.is_paid:
            return _('Paid')
        elif self.amount_paid > 0:
            return _('Partially Paid ({:.1f}%)').format((self.amount_paid / self.total) * 100)
        else:
            return _('Unpaid')


class InvoiceItem(models.Model):
    """
    Line item for invoices.
    """
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='line_items',
        verbose_name=_('invoice')
    )
    description = models.CharField(_('description'), max_length=255)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=14, decimal_places=2, default=0)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    
    # Optional relations
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_items',
        verbose_name=_('inventory item')
    )
    work_order_item = models.ForeignKey(
        'work_orders.WorkOrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_items',
        verbose_name=_('work order item')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('invoice item')
        verbose_name_plural = _('invoice items')
        ordering = ['invoice', 'id']
    
    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.unit_price})"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate total.
        """
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update invoice totals
        if self.invoice:
            self.invoice.save()


class Payment(models.Model):
    """
    Payment model for recording customer payments.
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('cancelled', _('Cancelled')),
    )
    
    METHOD_CHOICES = (
        ('cash', _('Cash')),
        ('check', _('Check')),
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('online_payment', _('Online Payment')),
        ('paypal', _('PayPal')),
        ('alipay', _('Alipay')),
        ('wechat_pay', _('WeChat Pay')),
        ('other', _('Other')),
    )
    
    number = models.CharField(_('payment number'), max_length=50, unique=True)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('invoice')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('customer')
    )
    date = models.DateField(_('payment date'))
    amount = models.DecimalField(_('amount'), max_digits=14, decimal_places=2)
    method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=METHOD_CHOICES,
        default='bank_transfer'
    )
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed'
    )
    
    # Payment details
    check_number = models.CharField(_('check number'), max_length=100, blank=True)
    transaction_id = models.CharField(_('transaction ID'), max_length=255, blank=True)
    payment_gateway = models.CharField(_('payment gateway'), max_length=100, blank=True)
    
    # Tracking
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments',
        verbose_name=_('recorded by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"Payment #{self.number} - {self.amount} {self.invoice.currency}"
    
    def save(self, *args, **kwargs):
        """
        Override save to update invoice payment amounts.
        """
        super().save(*args, **kwargs)
        
        # Update invoice amount paid and status
        if self.invoice and self.status == 'completed':
            # Recalculate total payments for this invoice
            completed_payments = Payment.objects.filter(
                invoice=self.invoice,
                status='completed'
            )
            self.invoice.amount_paid = sum(payment.amount for payment in completed_payments)
            self.invoice.amount_due = self.invoice.total - self.invoice.amount_paid
            
            # Update invoice status based on payment
            if self.invoice.amount_due <= 0:
                self.invoice.status = 'paid'
            elif self.invoice.amount_paid > 0:
                self.invoice.status = 'partial'
            
            self.invoice.save(update_fields=['amount_paid', 'amount_due', 'status'])


class PricingTier(models.Model):
    """
    Pricing tier for different customer segments.
    """
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    discount_percent = models.DecimalField(_('discount percentage'), max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(_('active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('pricing tier')
        verbose_name_plural = _('pricing tiers')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PricingItem(models.Model):
    """
    Pricing information for inventory items or services.
    """
    
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.CASCADE,
        related_name='pricing',
        verbose_name=_('inventory item')
    )
    pricing_tier = models.ForeignKey(
        PricingTier,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('pricing tier')
    )
    price = models.DecimalField(_('price'), max_digits=14, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='HKD')
    is_active = models.BooleanField(_('active'), default=True)
    
    effective_from = models.DateField(_('effective from'), null=True, blank=True)
    effective_to = models.DateField(_('effective to'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('pricing item')
        verbose_name_plural = _('pricing items')
        ordering = ['inventory_item', 'pricing_tier']
        unique_together = ['inventory_item', 'pricing_tier']
    
    def __str__(self):
        return f"{self.inventory_item.name} - {self.pricing_tier.name} - {self.price} {self.currency}"
    
    @property
    def is_current(self):
        """
        Check if the pricing is currently effective.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.is_active and
            (not self.effective_from or self.effective_from <= today) and
            (not self.effective_to or self.effective_to >= today)
        )


class Expense(models.Model):
    """
    Expense model for tracking business expenses.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
        ('reimbursed', _('Reimbursed')),
    )
    
    CATEGORY_CHOICES = (
        ('materials', _('Materials')),
        ('equipment', _('Equipment')),
        ('travel', _('Travel')),
        ('accommodation', _('Accommodation')),
        ('meals', _('Meals')),
        ('vehicle', _('Vehicle')),
        ('office', _('Office Supplies')),
        ('utilities', _('Utilities')),
        ('rent', _('Rent')),
        ('services', _('Services')),
        ('fees', _('Fees')),
        ('taxes', _('Taxes')),
        ('insurance', _('Insurance')),
        ('other', _('Other')),
    )
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    date = models.DateField(_('expense date'))
    amount = models.DecimalField(_('amount'), max_digits=14, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='HKD')
    tax_amount = models.DecimalField(_('tax amount'), max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('total amount'), max_digits=14, decimal_places=2)
    
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Related models
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name=_('project')
    )
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name=_('work order')
    )
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name=_('supplier')
    )
    
    # Tracking
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_expenses',
        verbose_name=_('submitted by')
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses',
        verbose_name=_('approved by')
    )
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    paid_at = models.DateTimeField(_('paid at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # References
    receipt_number = models.CharField(_('receipt number'), max_length=100, blank=True)
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    
    # Receipt file
    receipt = models.FileField(_('receipt'), upload_to='expense_receipts/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.total_amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate the total amount.
        """
        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)
