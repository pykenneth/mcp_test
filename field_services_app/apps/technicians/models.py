from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

class Specialty(models.Model):
    """Model representing a technician specialty."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Specialty"
        verbose_name_plural = "Specialties"
        ordering = ['name']

    def __str__(self):
        return self.name


class Certification(models.Model):
    """Model representing a technician certification."""
    name = models.CharField(max_length=100)
    issuing_organization = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    validity_period = models.PositiveIntegerField(
        help_text="Validity period in months",
        blank=True, null=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Technician(models.Model):
    """Model representing a field technician."""
    AVAILABILITY_STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_assignment', 'On Assignment'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('employment_contract', 'Employment Contract'),
        ('sub_contractor', 'Sub-Contractor'),
        ('self_employed', 'Self-Employed'),
    ]
    
    # User account (optional, for technicians who have system access)
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        related_name='technician_profile', 
        null=True, 
        blank=True
    )
    
    # Required fields
    employee_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True)
    phone_number = PhoneNumberField()
    whatsapp_number = PhoneNumberField(blank=True, null=True)
    
    # Employment and Cost details
    employment_type = models.CharField(
        max_length=50,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='employment_contract',
        help_text="Type of employment relationship"
    )
    
    # Cost-related fields for KPI comparison
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hourly cost rate for this technician"
    )
    monthly_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly salary (for employment contract)"
    )
    contract_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fee per contract (for sub-contractors)"
    )
    tax_classification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Tax classification (especially for self-employed)"
    )
    payment_terms = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Payment terms for this technician"
    )
    benefits_package = models.TextField(
        blank=True,
        null=True,
        help_text="Description of benefits package (for employment contract)"
    )
    
    # Optional fields
    email = models.EmailField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='technicians/', blank=True, null=True)
    emergency_contact = models.CharField(max_length=256, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    # Many-to-many relationships
    specialties = models.ManyToManyField(Specialty, blank=True, related_name='technicians')
    certifications = models.ManyToManyField(
        Certification, 
        through='TechnicianCertification',
        blank=True, 
        related_name='technicians'
    )
    
    # Status fields
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS_CHOICES,
        default='available'
    )
    
    # Metrics fields (updated by signals or periodic tasks)
    customer_rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True
    )
    punctuality_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=0,
        help_text="Percentage of on-time arrivals"
    )
    completion_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=0,
        help_text="Percentage of tasks completed successfully"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_number']

    def __str__(self):
        return f"{self.full_name} ({self.employee_number})"
    
    @property
    def active_assignments_count(self):
        """Return the count of active assignments for this technician."""
        return self.assignments.filter(status__in=['assigned', 'in_progress']).count()
    
    @property
    def total_assignments_count(self):
        """Return the total count of assignments for this technician."""
        return self.assignments.count()
    
    @property
    def completed_assignments_count(self):
        """Return the count of completed assignments for this technician."""
        return self.assignments.filter(status='completed').count()


class TechnicianCertification(models.Model):
    """Model representing a technician's certification with expiry date."""
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name='technician_certifications')
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ['technician', 'certification', 'issue_date']
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.technician.full_name} - {self.certification.name}"


class TechnicianLocation(models.Model):
    """Model representing a technician's location at a specific time."""
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField()
    location_source = models.CharField(
        max_length=20, 
        choices=[
            ('check_in', 'Check In'),
            ('check_out', 'Check Out'),
            ('gps', 'GPS Update'),
            ('manual', 'Manual Entry'),
        ],
        default='gps'
    )
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.technician.full_name} at {self.timestamp}"


class TechnicianCheckIn(models.Model):
    """Model representing a technician's check-in/check-out record."""
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    ]
    
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name='check_ins')
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(blank=True, null=True)
    check_in_location = models.ForeignKey(
        TechnicianLocation, 
        on_delete=models.SET_NULL,
        related_name='check_in_records',
        null=True
    )
    check_out_location = models.ForeignKey(
        TechnicianLocation, 
        on_delete=models.SET_NULL,
        related_name='check_out_records',
        null=True,
        blank=True
    )
    site_name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_in')
    
    class Meta:
        ordering = ['-check_in_time']
        verbose_name = "Check In/Out"
        verbose_name_plural = "Check Ins/Outs"
    
    def __str__(self):
        return f"{self.technician.full_name} - {self.check_in_time}"
    
    @property
    def is_active(self):
        """Return True if the technician is still checked in."""
        return self.check_out_time is None


class TechnicianRating(models.Model):
    """Model representing a rating for a technician."""
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name='ratings')
    work_order = models.ForeignKey(
        'work_orders.WorkOrder', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='technician_ratings'
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='technician_ratings'
    )
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.technician.full_name} - {self.rating}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the technician's average rating
        self.update_technician_rating()
    
    def update_technician_rating(self):
        """Update the technician's average rating."""
        ratings = TechnicianRating.objects.filter(technician=self.technician)
        if ratings.exists():
            avg_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.technician.customer_rating = avg_rating
            self.technician.save(update_fields=['customer_rating'])


class TechnicianCostMetrics(models.Model):
    """Model for tracking cost-related KPIs for comparing employment types."""
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name='cost_metrics')
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Cost metrics
    total_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tasks_completed = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Derived KPIs (calculated and stored for reporting efficiency)
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_task = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    efficiency_score = models.FloatField(null=True, blank=True)
    
    # Additional context
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end']
        unique_together = ['technician', 'period_start', 'period_end']
        verbose_name = "Technician Cost Metrics"
        verbose_name_plural = "Technician Cost Metrics"
    
    def __str__(self):
        return f"{self.technician.full_name} - {self.period_start} to {self.period_end}"
    
    def calculate_kpis(self):
        """Calculate derived KPIs based on raw metrics."""
        if self.total_hours_worked > 0:
            self.cost_per_hour = self.total_cost / self.total_hours_worked
        
        if self.total_tasks_completed > 0:
            self.cost_per_task = self.total_cost / self.total_tasks_completed
        
        # Efficiency score calculation (custom formula)
        # Higher score means better efficiency
        if self.total_hours_worked > 0 and self.total_tasks_completed > 0:
            tasks_per_hour = self.total_tasks_completed / self.total_hours_worked
            customer_rating_factor = self.technician.customer_rating or 3.0  # Default to mid-range if no rating
            completion_rate_factor = self.technician.completion_rate / 100 if self.technician.completion_rate else 0.5
            
            # Weighted formula that balances productivity, quality, and reliability
            self.efficiency_score = (
                (tasks_per_hour * 0.4) +
                ((customer_rating_factor / 5) * 0.3) +
                (completion_rate_factor * 0.3)
            ) * 100  # Scale to 0-100 range
        
        self.save(update_fields=['cost_per_hour', 'cost_per_task', 'efficiency_score'])
    
    def save(self, *args, **kwargs):
        """Override save method to ensure KPIs are calculated."""
        # First save to get an ID if it's a new record
        super().save(*args, **kwargs)
        
        # Calculate KPIs if not part of the current save operation
        update_fields = kwargs.get('update_fields', [])
        if 'cost_per_hour' not in update_fields and 'cost_per_task' not in update_fields and 'efficiency_score' not in update_fields:
            self.calculate_kpis()


class EmploymentTypeKpiReport(models.Model):
    """Model for aggregated KPI reports by employment type, used for comparison."""
    PERIOD_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    employment_type = models.CharField(max_length=50, choices=Technician.EMPLOYMENT_TYPE_CHOICES)
    
    # Aggregated metrics
    technicians_count = models.PositiveIntegerField(default=0)
    avg_cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    avg_cost_per_task = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    avg_customer_rating = models.FloatField(null=True, blank=True)
    avg_completion_rate = models.FloatField(null=True, blank=True)
    avg_punctuality_rate = models.FloatField(null=True, blank=True)
    avg_efficiency_score = models.FloatField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tasks_completed = models.PositiveIntegerField(default=0)
    
    # Additional context
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_end', 'employment_type']
        unique_together = ['period_type', 'period_start', 'period_end', 'employment_type']
        verbose_name = "Employment Type KPI Report"
        verbose_name_plural = "Employment Type KPI Reports"
    
    def __str__(self):
        period_desc = f"{self.get_period_type_display()}: {self.period_start} to {self.period_end}"
        return f"{self.get_employment_type_display()} - {period_desc}"
    
    @classmethod
    def generate_report(cls, period_type, period_start, period_end):
        """Generate KPI reports for all employment types for the given period."""
        from django.db.models import Avg, Sum, Count
        
        for emp_type, _ in Technician.EMPLOYMENT_TYPE_CHOICES:
            # Get all technicians of this employment type
            technicians = Technician.objects.filter(employment_type=emp_type)
            technicians_count = technicians.count()
            
            if technicians_count == 0:
                continue
            
            # Get cost metrics for the period
            cost_metrics = TechnicianCostMetrics.objects.filter(
                technician__employment_type=emp_type,
                period_start__gte=period_start,
                period_end__lte=period_end
            )
            
            # Calculate aggregated metrics
            metrics_data = cost_metrics.aggregate(
                avg_cost_per_hour=Avg('cost_per_hour'),
                avg_cost_per_task=Avg('cost_per_task'),
                avg_efficiency_score=Avg('efficiency_score'),
                total_cost=Sum('total_cost'),
                total_tasks=Sum('total_tasks_completed')
            )
            
            # Get technician performance metrics
            technician_metrics = technicians.aggregate(
                avg_customer_rating=Avg('customer_rating'),
                avg_completion_rate=Avg('completion_rate'),
                avg_punctuality_rate=Avg('punctuality_rate')
            )
            
            # Create or update the report
            report, created = cls.objects.update_or_create(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                employment_type=emp_type,
                defaults={
                    'technicians_count': technicians_count,
                    'avg_cost_per_hour': metrics_data['avg_cost_per_hour'],
                    'avg_cost_per_task': metrics_data['avg_cost_per_task'],
                    'avg_efficiency_score': metrics_data['avg_efficiency_score'],
                    'total_cost': metrics_data['total_cost'] or 0,
                    'total_tasks_completed': metrics_data['total_tasks'] or 0,
                    'avg_customer_rating': technician_metrics['avg_customer_rating'],
                    'avg_completion_rate': technician_metrics['avg_completion_rate'],
                    'avg_punctuality_rate': technician_metrics['avg_punctuality_rate'],
                }
            )
            
        return cls.objects.filter(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end
        )
