from rest_framework import serializers
from .models import (
    Technician, 
    Specialty, 
    Certification, 
    TechnicianCertification,
    TechnicianLocation,
    TechnicianCheckIn,
    TechnicianRating,
    TechnicianCostMetrics,
    EmploymentTypeKpiReport
)


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description', 'category']


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'issuing_organization', 'description', 'validity_period']


class TechnicianCertificationSerializer(serializers.ModelSerializer):
    certification = CertificationSerializer(read_only=True)
    
    class Meta:
        model = TechnicianCertification
        fields = ['id', 'certification', 'issue_date', 'expiry_date', 'certificate_number']


class TechnicianLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianLocation
        fields = ['id', 'latitude', 'longitude', 'altitude', 'accuracy', 'timestamp', 'location_source']


class TechnicianCheckInSerializer(serializers.ModelSerializer):
    check_in_location = TechnicianLocationSerializer(read_only=True)
    check_out_location = TechnicianLocationSerializer(read_only=True)
    technician_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TechnicianCheckIn
        fields = [
            'id', 'technician', 'technician_name', 'check_in_time', 'check_out_time', 
            'check_in_location', 'check_out_location', 'site_name', 'notes', 'status',
            'is_active'
        ]
    
    def get_technician_name(self, obj):
        return obj.technician.full_name


class TechnicianRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianRating
        fields = ['id', 'technician', 'work_order', 'customer', 'rating', 'feedback', 'created_at']


class TechnicianListSerializer(serializers.ModelSerializer):
    """Serializer for listing technicians - includes basic info."""
    specialties = SpecialtySerializer(many=True, read_only=True)
    today_check_in = serializers.SerializerMethodField()
    active_assignments_count = serializers.ReadOnlyField()
    customer_rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Technician
        fields = [
            'id', 'employee_number', 'full_name', 'nickname', 'specialties', 'job_title',
            'customer_rating', 'customer_rating_display', 'phone_number', 'whatsapp_number', 
            'availability_status', 'active_assignments_count', 'today_check_in',
            'punctuality_rate', 'completion_rate', 'profile_image'
        ]
    
    def get_today_check_in(self, obj):
        """Get the technician's check-in record for today, if any."""
        from django.utils import timezone
        import datetime
        
        today = timezone.now().date()
        check_in = obj.check_ins.filter(
            check_in_time__date=today
        ).order_by('-check_in_time').first()
        
        if check_in:
            return TechnicianCheckInSerializer(check_in).data
        return None
    
    def get_customer_rating_display(self, obj):
        """Format customer rating for display (1-5 stars, one decimal place)."""
        if obj.customer_rating is None:
            return None
        return round(obj.customer_rating * 10) / 10  # Round to 1 decimal place


class TechnicianDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed technician view."""
    specialties = SpecialtySerializer(many=True, read_only=True)
    certifications = TechnicianCertificationSerializer(source='technician_certifications', many=True, read_only=True)
    today_check_in = serializers.SerializerMethodField()
    active_assignments_count = serializers.ReadOnlyField()
    total_assignments_count = serializers.ReadOnlyField()
    completed_assignments_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Technician
        fields = [
            'id', 'employee_number', 'full_name', 'nickname', 'job_title', 'email',
            'phone_number', 'whatsapp_number', 'emergency_contact', 'hire_date',
            'specialties', 'certifications', 'profile_image', 'availability_status', 
            'customer_rating', 'punctuality_rate', 'completion_rate',
            'active_assignments_count', 'total_assignments_count', 'completed_assignments_count',
            'today_check_in', 'created_at', 'updated_at'
        ]
    
    def get_today_check_in(self, obj):
        """Get the technician's check-in record for today, if any."""
        from django.utils import timezone
        import datetime
        
        today = timezone.now().date()
        check_in = obj.check_ins.filter(
            check_in_time__date=today
        ).order_by('-check_in_time').first()
        
        if check_in:
            return TechnicianCheckInSerializer(check_in).data
        return None
        

class TechnicianCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating technicians."""
    specialties = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Specialty.objects.all(),
        required=False
    )
    
    class Meta:
        model = Technician
        fields = [
            'id', 'employee_number', 'full_name', 'nickname', 'job_title', 'email',
            'phone_number', 'whatsapp_number', 'emergency_contact', 'hire_date',
            'specialties', 'profile_image', 'availability_status'
        ]
        

class TechnicianPerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for technician performance metrics."""
    technician_id = serializers.IntegerField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    on_time_arrivals = serializers.IntegerField()
    late_arrivals = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    punctuality_rate = serializers.FloatField()
    completed_tasks = serializers.IntegerField()
    incomplete_tasks = serializers.IntegerField()
    assigned_tasks = serializers.IntegerField()
    task_completion_rate = serializers.FloatField()
    completion_rate = serializers.FloatField()
    avg_task_duration = serializers.FloatField()
    avg_tasks_per_day = serializers.FloatField()
    customer_satisfaction = serializers.FloatField(allow_null=True)
    feedback_count = serializers.IntegerField()
    specialty_utilization = serializers.DictField(
        child=serializers.IntegerField()
    )


class TeamPerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for team performance metrics."""
    total_technicians = serializers.IntegerField()
    avg_punctuality_rate = serializers.FloatField()
    avg_completion_rate = serializers.FloatField()
    avg_task_completion_rate = serializers.FloatField()
    avg_customer_satisfaction = serializers.FloatField()
    avg_tasks_per_day = serializers.FloatField()
    top_specialties = serializers.ListField(
        child=serializers.CharField()
    )
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()


class CheckInRequestSerializer(serializers.Serializer):
    """Serializer for technician check-in request."""
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    accuracy = serializers.FloatField(required=False, allow_null=True)
    altitude = serializers.FloatField(required=False, allow_null=True)
    site_name = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    send_whatsapp_notification = serializers.BooleanField(default=False)


class CheckOutRequestSerializer(serializers.Serializer):
    """Serializer for technician check-out request."""
    check_in_id = serializers.IntegerField(required=True)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    accuracy = serializers.FloatField(required=False, allow_null=True)
    altitude = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    send_whatsapp_notification = serializers.BooleanField(default=False)


class TechnicianRatingRequestSerializer(serializers.Serializer):
    """Serializer for rating a technician."""
    rating = serializers.FloatField(
        min_value=0.0, 
        max_value=5.0,
        required=True
    )
    feedback = serializers.CharField(required=False, allow_blank=True)
    work_order = serializers.IntegerField(required=False, allow_null=True)


class TechnicianCostMetricsSerializer(serializers.ModelSerializer):
    """Serializer for technician cost metrics."""
    technician_name = serializers.SerializerMethodField()
    employment_type = serializers.SerializerMethodField()
    
    class Meta:
        model = TechnicianCostMetrics
        fields = [
            'id', 'technician', 'technician_name', 'employment_type', 
            'period_start', 'period_end', 'total_hours_worked',
            'total_tasks_completed', 'total_cost', 'cost_per_hour',
            'cost_per_task', 'efficiency_score', 'notes',
            'created_at', 'updated_at'
        ]
    
    def get_technician_name(self, obj):
        return obj.technician.full_name
    
    def get_employment_type(self, obj):
        return {
            'code': obj.technician.employment_type,
            'name': obj.technician.get_employment_type_display()
        }


class EmploymentTypeKpiReportSerializer(serializers.ModelSerializer):
    """Serializer for employment type KPI reports."""
    employment_type_display = serializers.SerializerMethodField()
    period_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = EmploymentTypeKpiReport
        fields = [
            'id', 'period_type', 'period_type_display', 
            'period_start', 'period_end', 'employment_type',
            'employment_type_display', 'technicians_count',
            'avg_cost_per_hour', 'avg_cost_per_task', 
            'avg_customer_rating', 'avg_completion_rate',
            'avg_punctuality_rate', 'avg_efficiency_score',
            'total_cost', 'total_tasks_completed',
            'created_at', 'updated_at'
        ]
    
    def get_employment_type_display(self, obj):
        return obj.get_employment_type_display()
    
    def get_period_type_display(self, obj):
        return obj.get_period_type_display()


class TechnicianExtendedDetailSerializer(TechnicianDetailSerializer):
    """Extended serializer that includes employment and cost details."""
    employment_type_display = serializers.SerializerMethodField()
    
    class Meta(TechnicianDetailSerializer.Meta):
        model = Technician
        fields = TechnicianDetailSerializer.Meta.fields + [
            'employment_type', 'employment_type_display', 
            'hourly_rate', 'monthly_salary', 'contract_fee',
            'tax_classification', 'payment_terms', 'benefits_package'
        ]
    
    def get_employment_type_display(self, obj):
        return obj.get_employment_type_display()
