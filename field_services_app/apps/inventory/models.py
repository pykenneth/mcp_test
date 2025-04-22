"""
Models for the inventory app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class InventoryCategory(models.Model):
    """
    Category for inventory items.
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
        verbose_name = _('inventory category')
        verbose_name_plural = _('inventory categories')
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


class InventoryItem(models.Model):
    """
    Inventory item model.
    """
    
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('discontinued', _('Discontinued')),
    )
    
    TYPE_CHOICES = (
        ('material', _('Material')),
        ('equipment', _('Equipment')),
        ('tool', _('Tool')),
        ('part', _('Part')),
        ('consumable', _('Consumable')),
        ('service', _('Service')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        verbose_name=_('category')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='material'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    sku = models.CharField(_('SKU'), max_length=50, unique=True, blank=True, null=True)
    barcode = models.CharField(_('barcode'), max_length=100, blank=True)
    unit_of_measure = models.CharField(_('unit of measure'), max_length=50, default='ea')
    purchase_price = models.DecimalField(
        _('purchase price'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    sale_price = models.DecimalField(
        _('sale price'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    min_stock_level = models.PositiveIntegerField(_('minimum stock level'), default=0)
    reorder_point = models.PositiveIntegerField(_('reorder point'), default=0)
    reorder_quantity = models.PositiveIntegerField(_('reorder quantity'), default=0)
    tax_rate = models.DecimalField(
        _('tax rate'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    weight = models.DecimalField(
        _('weight (kg)'),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    dimensions = models.CharField(_('dimensions'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    image = models.ImageField(
        _('image'),
        upload_to='inventory_images/',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_inventory_items',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('inventory item')
        verbose_name_plural = _('inventory items')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        """
        Check if the item is in stock.
        """
        return self.stock_on_hand > 0
    
    @property
    def stock_on_hand(self):
        """
        Get the current stock on hand.
        """
        return sum(
            location.quantity for location in 
            self.inventory_locations.all()
        )
    
    @property
    def needs_reordering(self):
        """
        Check if the item needs reordering.
        """
        return self.stock_on_hand <= self.reorder_point
    
    @property
    def current_value(self):
        """
        Calculate the current value of all stock.
        """
        return self.stock_on_hand * self.purchase_price


class InventoryLocation(models.Model):
    """
    Location where inventory items are stored.
    """
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)
    type = models.CharField(_('type'), max_length=50, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent location')
    )
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('inventory location')
        verbose_name_plural = _('inventory locations')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """
        Return the full location path.
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class ItemLocation(models.Model):
    """
    Junction model for inventory items at specific locations.
    """
    
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='inventory_locations',
        verbose_name=_('item')
    )
    location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_('location')
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    bin_shelf = models.CharField(_('bin/shelf'), max_length=50, blank=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('item location')
        verbose_name_plural = _('item locations')
        ordering = ['location', 'item']
        unique_together = ['item', 'location', 'bin_shelf']
    
    def __str__(self):
        return f"{self.item.name} at {self.location.name}"


class InventoryTransaction(models.Model):
    """
    Record of inventory transactions.
    """
    
    TYPE_CHOICES = (
        ('purchase', _('Purchase')),
        ('sale', _('Sale')),
        ('transfer', _('Transfer')),
        ('adjustment', _('Adjustment')),
        ('return', _('Return')),
        ('write_off', _('Write Off')),
        ('count', _('Inventory Count')),
    )
    
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_('item')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    quantity = models.IntegerField(_('quantity'))
    from_location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_transactions',
        verbose_name=_('from location')
    )
    to_location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transactions',
        verbose_name=_('to location')
    )
    unit_price = models.DecimalField(
        _('unit price'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        _('total price'),
        max_digits=14,
        decimal_places=2,
        default=0
    )
    reference = models.CharField(_('reference'), max_length=100, blank=True)
    work_order = models.ForeignKey(
        'work_orders.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_transactions',
        verbose_name=_('work order')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_transactions',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('inventory transaction')
        verbose_name_plural = _('inventory transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.item.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        """
        Override save to update the total price and adjust inventory levels.
        """
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        
        # Create the transaction record
        super().save(*args, **kwargs)
        
        # Update inventory levels based on transaction type
        self._update_inventory_levels()
    
    def _update_inventory_levels(self):
        """
        Update inventory levels based on the transaction type.
        """
        if self.type == 'purchase' and self.to_location:
            self._add_to_location(self.to_location, self.quantity)
            
        elif self.type == 'sale' and self.from_location:
            self._remove_from_location(self.from_location, self.quantity)
            
        elif self.type == 'transfer' and self.from_location and self.to_location:
            self._remove_from_location(self.from_location, self.quantity)
            self._add_to_location(self.to_location, self.quantity)
            
        elif self.type == 'adjustment':
            if self.quantity > 0 and self.to_location:
                self._add_to_location(self.to_location, self.quantity)
            elif self.quantity < 0 and self.from_location:
                self._remove_from_location(self.from_location, abs(self.quantity))
                
        elif self.type == 'return' and self.to_location:
            self._add_to_location(self.to_location, self.quantity)
            
        elif self.type == 'write_off' and self.from_location:
            self._remove_from_location(self.from_location, self.quantity)
            
        elif self.type == 'count' and self.to_location:
            # Get the current quantity at this location
            try:
                item_location = ItemLocation.objects.get(
                    item=self.item,
                    location=self.to_location
                )
                # Adjust the quantity to match the count
                adjustment = self.quantity - item_location.quantity
                if adjustment != 0:
                    item_location.quantity = self.quantity
                    item_location.save()
            except ItemLocation.DoesNotExist:
                # If the item wasn't at this location before, create a new record
                if self.quantity > 0:
                    ItemLocation.objects.create(
                        item=self.item,
                        location=self.to_location,
                        quantity=self.quantity
                    )
    
    def _add_to_location(self, location, quantity):
        """
        Add quantity to a location.
        """
        item_location, created = ItemLocation.objects.get_or_create(
            item=self.item,
            location=location,
            defaults={'quantity': 0}
        )
        item_location.quantity += quantity
        item_location.save()
    
    def _remove_from_location(self, location, quantity):
        """
        Remove quantity from a location.
        """
        try:
            item_location = ItemLocation.objects.get(
                item=self.item,
                location=location
            )
            item_location.quantity = max(0, item_location.quantity - quantity)
            item_location.save()
        except ItemLocation.DoesNotExist:
            # Cannot remove from a location where the item doesn't exist
            pass


class Supplier(models.Model):
    """
    Supplier model for inventory items.
    """
    
    name = models.CharField(_('name'), max_length=255)
    contact_person = models.CharField(_('contact person'), max_length=255, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('phone'), max_length=30, blank=True)
    address = models.TextField(_('address'), blank=True)
    website = models.URLField(_('website'), blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    payment_terms = models.CharField(_('payment terms'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ItemSupplier(models.Model):
    """
    Junction model for items and their suppliers.
    """
    
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='suppliers',
        verbose_name=_('item')
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('supplier')
    )
    supplier_part_number = models.CharField(_('supplier part number'), max_length=100, blank=True)
    supplier_description = models.TextField(_('supplier description'), blank=True)
    purchase_price = models.DecimalField(
        _('purchase price'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    lead_time_days = models.PositiveIntegerField(_('lead time (days)'), default=0)
    minimum_order_quantity = models.PositiveIntegerField(_('minimum order quantity'), default=1)
    is_preferred = models.BooleanField(_('preferred supplier'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    last_purchase_date = models.DateField(_('last purchase date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('item supplier')
        verbose_name_plural = _('item suppliers')
        ordering = ['item', '-is_preferred', 'supplier']
        unique_together = ['item', 'supplier']
    
    def __str__(self):
        return f"{self.item.name} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure only one preferred supplier per item.
        """
        if self.is_preferred:
            # Set all other suppliers for this item to not preferred
            ItemSupplier.objects.filter(
                item=self.item,
                is_preferred=True
            ).exclude(id=self.id).update(is_preferred=False)
        super().save(*args, **kwargs)
