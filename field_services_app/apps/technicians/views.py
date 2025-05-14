from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from apps.users.permissions import IsAdmin, IsManager, IsTechnician
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q, F, ExpressionWrapper, fields
from datetime import datetime, timedelta

from .models import (
    Technician, 
    Specialty,
    Certification,
    TechnicianCheckIn,
    TechnicianLocation,
    TechnicianRating,
    TechnicianCostMetrics,
    EmploymentTypeKpiReport
)
from .serializers import (
    TechnicianListSerializer,
    TechnicianDetailSerializer,
    TechnicianCreateUpdateSerializer,
    TechnicianExtendedDetailSerializer,
    SpecialtySerializer,
    CertificationSerializer,
    TechnicianCheckInSerializer,
    TechnicianLocationSerializer,
    TechnicianRatingSerializer,
    TechnicianPerformanceMetricsSerializer,
    TeamPerformanceMetricsSerializer,
    CheckInRequestSerializer,
    CheckOutRequestSerializer,
    TechnicianRatingRequestSerializer,
    TechnicianCostMetricsSerializer,
    EmploymentTypeKpiReportSerializer
)

class TechnicianViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing technician information."""
    queryset = Technician.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Override permissions based on action:
        - Admin can do everything
        - Managers can view all, create, update, but not delete
        - Technicians can only view their own profile and limited listings
        """
        if self.action in ['destroy']:
            permission_classes = [IsAdmin]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAdmin | IsManager]
        elif self.action in ['list', 'retrieve', 'available', 'team_performance']:
            permission_classes = [IsAuthenticated]
        else:
            # Other detail actions
            permission_classes = [IsAdmin | IsManager]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # If user is technician, only show their own record
        if hasattr(user, 'technician_profile') and not user.is_staff:
            queryset = queryset.filter(id=user.technician_profile.id)
            
        # Apply filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['availability_status', 'specialties']
    search_fields = ['employee_number', 'full_name', 'nickname', 'email', 'specialties__name']
    ordering_fields = ['employee_number', 'full_name', 'customer_rating', 'punctuality_rate', 'completion_rate']
    ordering = ['employee_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TechnicianListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TechnicianCreateUpdateSerializer
        return TechnicianDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by specialty if provided
        specialty = self.request.query_params.get('specialty', None)
        if specialty:
            queryset = queryset.filter(specialties__name__icontains=specialty)
        
        # Filter by minimum rating if provided
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            try:
                min_rating_val = float(min_rating)
                queryset = queryset.filter(customer_rating__gte=min_rating_val)
            except (ValueError, TypeError):
                pass
                
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available technicians."""
        technicians = self.get_queryset().filter(availability_status='available')
        serializer = TechnicianListSerializer(technicians, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """Get all work orders assigned to a technician."""
        technician = self.get_object()
        work_orders = technician.assignments.all().order_by('-created_at')
        
        # Import here to avoid circular import
        from apps.work_orders.serializers import WorkOrderListSerializer
        serializer = WorkOrderListSerializer(work_orders, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        """Get location history for a technician."""
        technician = self.get_object()
        
        # Parse query params for date filtering
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        locations = technician.locations.all()
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
                locations = locations.filter(timestamp__gte=start_date)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
                locations = locations.filter(timestamp__lte=end_date)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = TechnicianLocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a technician."""
        technician = self.get_object()
        serializer = CheckInRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create location record
        location = TechnicianLocation.objects.create(
            technician=technician,
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            accuracy=serializer.validated_data.get('accuracy'),
            altitude=serializer.validated_data.get('altitude'),
            timestamp=timezone.now(),
            location_source='check_in'
        )
        
        # Create check-in record
        check_in = TechnicianCheckIn.objects.create(
            technician=technician,
            check_in_time=timezone.now(),
            check_in_location=location,
            site_name=serializer.validated_data.get('site_name', ''),
            notes=serializer.validated_data.get('notes', ''),
            status='checked_in'
        )
        
        # Send WhatsApp notification if requested
        if serializer.validated_data.get('send_whatsapp_notification', False) and technician.whatsapp_number:
            self._send_whatsapp_notification(
                technician,
                f"Check-in registered for {technician.full_name} at {check_in.check_in_time.strftime('%H:%M')}."
            )
        
        result_serializer = TechnicianCheckInSerializer(check_in)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Check out a technician."""
        technician = self.get_object()
        serializer = CheckOutRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the check-in record
        try:
            check_in = TechnicianCheckIn.objects.get(
                id=serializer.validated_data['check_in_id'],
                technician=technician
            )
        except TechnicianCheckIn.DoesNotExist:
            return Response(
                {"error": "Check-in record not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already checked out
        if check_in.check_out_time is not None:
            return Response(
                {"error": "Technician has already checked out from this check-in"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create location record if coordinates provided
        check_out_location = None
        if 'latitude' in serializer.validated_data and 'longitude' in serializer.validated_data:
            check_out_location = TechnicianLocation.objects.create(
                technician=technician,
                latitude=serializer.validated_data['latitude'],
                longitude=serializer.validated_data['longitude'],
                accuracy=serializer.validated_data.get('accuracy'),
                altitude=serializer.validated_data.get('altitude'),
                timestamp=timezone.now(),
                location_source='check_out'
            )
        
        # Update check-in record
        check_in.check_out_time = timezone.now()
        check_in.check_out_location = check_out_location
        check_in.notes = (check_in.notes or '') + '\n\n' + (serializer.validated_data.get('notes', '') or '')
        check_in.status = 'checked_out'
        check_in.save()
        
        # Send WhatsApp notification if requested
        if serializer.validated_data.get('send_whatsapp_notification', False) and technician.whatsapp_number:
            self._send_whatsapp_notification(
                technician,
                f"Check-out registered for {technician.full_name} at {check_in.check_out_time.strftime('%H:%M')}."
            )
        
        result_serializer = TechnicianCheckInSerializer(check_in)
        return Response(result_serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_task(self, request, pk=None):
        """Assign a task to a technician."""
        technician = self.get_object()
        task_id = request.data.get('task_id')
        
        if not task_id:
            return Response(
                {"error": "task_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular import
        from apps.work_orders.models import WorkOrderTask
        
        try:
            task = WorkOrderTask.objects.get(id=task_id)
            task.assigned_technician = technician
            task.status = 'assigned'
            task.save()
            
            # Import here to avoid circular import
            from apps.work_orders.serializers import WorkOrderTaskSerializer
            
            return Response(WorkOrderTaskSerializer(task).data)
        except WorkOrderTask.DoesNotExist:
            return Response(
                {"error": "Task not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def unassign_task(self, request, pk=None):
        """Unassign a task from a technician."""
        technician = self.get_object()
        task_id = request.data.get('task_id')
        
        if not task_id:
            return Response(
                {"error": "task_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular import
        from apps.work_orders.models import WorkOrderTask
        
        try:
            task = WorkOrderTask.objects.get(id=task_id, assigned_technician=technician)
            task.assigned_technician = None
            task.status = 'unassigned'
            task.save()
            
            # Import here to avoid circular import
            from apps.work_orders.serializers import WorkOrderTaskSerializer
            
            return Response(WorkOrderTaskSerializer(task).data)
        except WorkOrderTask.DoesNotExist:
            return Response(
                {"error": "Task not found or not assigned to this technician"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks assigned to a technician."""
        technician = self.get_object()
        
        # Import here to avoid circular import
        from apps.work_orders.models import WorkOrderTask
        from apps.work_orders.serializers import WorkOrderTaskSerializer
        
        tasks = WorkOrderTask.objects.filter(assigned_technician=technician)
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            tasks = tasks.filter(status=status_param)
        
        serializer = WorkOrderTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get availability information for a technician."""
        technician = self.get_object()
        date_str = request.query_params.get('date')
        
        if date_str:
            try:
                target_date = datetime.fromisoformat(date_str).date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = timezone.now().date()
        
        # Get work assignments for the day
        from apps.work_orders.models import WorkOrderTask
        
        assignments = WorkOrderTask.objects.filter(
            assigned_technician=technician,
            scheduled_date=target_date
        ).order_by('scheduled_start_time')
        
        # Import here to avoid circular import
        from apps.work_orders.serializers import WorkOrderTaskSerializer
        
        # Get check-in records for the day
        check_ins = TechnicianCheckIn.objects.filter(
            technician=technician,
            check_in_time__date=target_date
        ).order_by('check_in_time')
        
        # Construct availability slots
        availability_data = {
            'technician_id': technician.id,
            'technician_name': technician.full_name,
            'date': target_date.isoformat(),
            'availability_status': technician.availability_status,
            'assignments': WorkOrderTaskSerializer(assignments, many=True).data,
            'check_ins': TechnicianCheckInSerializer(check_ins, many=True).data,
        }
        
        return Response(availability_data)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get performance metrics for a technician."""
        technician = self.get_object()
        
        # Parse query params
        period_type = request.query_params.get('period_type', 'monthly')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Validate and parse dates
        end_date = timezone.now().date()
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str).date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate start date based on period type if not provided
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if period_type == 'daily':
                start_date = end_date - timedelta(days=1)
            elif period_type == 'weekly':
                start_date = end_date - timedelta(weeks=1)
            elif period_type == 'monthly':
                start_date = end_date - timedelta(days=30)
            elif period_type == 'quarterly':
                start_date = end_date - timedelta(days=90)
            elif period_type == 'yearly':
                start_date = end_date - timedelta(days=365)
            elif period_type == 'custom':
                # Custom requires explicit start_date
                return Response(
                    {"error": "start_date is required for custom period_type"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Invalid period_type. Choose from daily, weekly, monthly, quarterly, yearly, custom"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get relevant data for calculations
        from apps.work_orders.models import WorkOrderTask
        
        # Punctuality metrics
        assignments = WorkOrderTask.objects.filter(
            assigned_technician=technician,
            scheduled_date__gte=start_date,
            scheduled_date__lte=end_date,
            status__in=['completed', 'in_progress', 'assigned']
        )
        
        total_assignments = assignments.count()
        on_time_arrivals = assignments.filter(actual_start_time__lte=F('scheduled_start_time')).count()
        
        # Task completion metrics
        completed_tasks = assignments.filter(status='completed').count()
        incomplete_tasks = total_assignments - completed_tasks
        
        # Customer satisfaction
        ratings = TechnicianRating.objects.filter(
            technician=technician,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        feedback_count = ratings.count()
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        
        # Calculate rates
        punctuality_rate = (on_time_arrivals / total_assignments * 100) if total_assignments > 0 else 0
        task_completion_rate = (completed_tasks / total_assignments * 100) if total_assignments > 0 else 0
        
        # Calculate average tasks per day
        days_in_period = (end_date - start_date).days + 1
        avg_tasks_per_day = total_assignments / days_in_period if days_in_period > 0 else 0
        
        # Calculate specialty utilization
        specialty_counts = {}
        for assignment in assignments:
            for task_type in assignment.work_order.work_types.all():
                if task_type.name in specialty_counts:
                    specialty_counts[task_type.name] += 1
                else:
                    specialty_counts[task_type.name] = 1
        
        # Prepare metrics data
        metrics_data = {
            'technician_id': technician.id,
            'period_start': datetime.combine(start_date, datetime.min.time()).isoformat(),
            'period_end': datetime.combine(end_date, datetime.max.time()).isoformat(),
            'on_time_arrivals': on_time_arrivals,
            'late_arrivals': total_assignments - on_time_arrivals,
            'total_assignments': total_assignments,
            'punctuality_rate': punctuality_rate,
            'completed_tasks': completed_tasks,
            'incomplete_tasks': incomplete_tasks,
            'assigned_tasks': total_assignments,
            'task_completion_rate': task_completion_rate,
            'completion_rate': task_completion_rate,  # Same as task completion rate in this context
            'avg_task_duration': 0,  # Placeholder, would require additional calculation
            'avg_tasks_per_day': avg_tasks_per_day,
            'customer_satisfaction': avg_rating,
            'feedback_count': feedback_count,
            'specialty_utilization': specialty_counts
        }
        
        serializer = TechnicianPerformanceMetricsSerializer(metrics_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a technician."""
        technician = self.get_object()
        serializer = TechnicianRatingRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create rating
        rating = TechnicianRating.objects.create(
            technician=technician,
            rating=serializer.validated_data['rating'],
            feedback=serializer.validated_data.get('feedback', '')
        )
        
        # Associate with work order if provided
        work_order_id = serializer.validated_data.get('work_order')
        if work_order_id:
            from apps.work_orders.models import WorkOrder
            try:
                work_order = WorkOrder.objects.get(id=work_order_id)
                rating.work_order = work_order
                rating.customer = work_order.customer
                rating.save()
            except WorkOrder.DoesNotExist:
                pass
        
        rating_serializer = TechnicianRatingSerializer(rating)
        return Response(rating_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def team_performance(self, request):
        """Get team performance metrics."""
        # Parse query params
        period_type = request.query_params.get('period_type', 'monthly')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        # Validate and parse dates
        end_date = timezone.now().date()
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str).date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate start date based on period type if not provided
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if period_type == 'daily':
                start_date = end_date - timedelta(days=1)
            elif period_type == 'weekly':
                start_date = end_date - timedelta(weeks=1)
            elif period_type == 'monthly':
                start_date = end_date - timedelta(days=30)
            elif period_type == 'quarterly':
                start_date = end_date - timedelta(days=90)
            elif period_type == 'yearly':
                start_date = end_date - timedelta(days=365)
            elif period_type == 'custom':
                # Custom requires explicit start_date
                return Response(
                    {"error": "start_date is required for custom period_type"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "Invalid period_type. Choose from daily, weekly, monthly, quarterly, yearly, custom"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get active technicians
        active_technicians = Technician.objects.filter(
            availability_status__in=['available', 'on_assignment']
        )
        
        total_technicians = active_technicians.count()
        
        # Calculate team averages
        avg_punctuality = active_technicians.aggregate(Avg('punctuality_rate'))['punctuality_rate__avg'] or 0
        avg_completion = active_technicians.aggregate(Avg('completion_rate'))['completion_rate__avg'] or 0
        avg_customer_satisfaction = active_technicians.filter(
            customer_rating__isnull=False
        ).aggregate(Avg('customer_rating'))['customer_rating__avg'] or 0
        
        # Get top specialties
        from django.db.models import Count
        top_specialties = Specialty.objects.annotate(
            technician_count=Count('technicians')
        ).order_by('-technician_count')[:5].values_list('name', flat=True)
        
        # Prepare metrics data
        metrics_data = {
            'total_technicians': total_technicians,
            'avg_punctuality_rate': avg_punctuality,
            'avg_completion_rate': avg_completion,
            'avg_task_completion_rate': avg_completion,  # Same as completion rate in this context
            'avg_customer_satisfaction': avg_customer_satisfaction,
            'avg_tasks_per_day': 4.2,  # Placeholder, would require additional calculation
            'top_specialties': list(top_specialties),
            'period_start': datetime.combine(start_date, datetime.min.time()).isoformat(),
            'period_end': datetime.combine(end_date, datetime.max.time()).isoformat()
        }
        
        serializer = TeamPerformanceMetricsSerializer(metrics_data)
        return Response(serializer.data)
    
    def _send_whatsapp_notification(self, technician, message):
        """Helper method to send WhatsApp notification."""
        # This would integrate with WhatsApp API
        # For now, just log the message
        print(f"WhatsApp notification would be sent to {technician.whatsapp_number}: {message}")
        return True


class SpecialtyViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing specialties."""
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    
    def get_permissions(self):
        """
        Override permissions based on action:
        - Admin and managers can create, update, and delete
        - Everyone can view
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category']
    ordering = ['name']


class CertificationViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing certifications."""
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    
    def get_permissions(self):
        """
        Override permissions based on action:
        - Admin and managers can create, update, and delete
        - Everyone can view
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'issuing_organization', 'description']
    ordering_fields = ['name', 'issuing_organization']
    ordering = ['name']


class TechnicianCostMetricsViewSet(viewsets.ModelViewSet):
    """ViewSet for technician cost metrics."""
    queryset = TechnicianCostMetrics.objects.all()
    serializer_class = TechnicianCostMetricsSerializer
    
    def get_permissions(self):
        """
        Override permissions based on action:
        - Admin and managers can perform all actions
        - Regular users and technicians can only view their own data or listing
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'record_metrics']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter cost metrics based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # If user is admin or manager, show all metrics
        if user.is_staff or hasattr(user, 'manager_profile'):
            return queryset
            
        # If user is technician, only show their own metrics
        if hasattr(user, 'technician_profile'):
            return queryset.filter(technician__id=user.technician_profile.id)
            
        # Default: empty queryset for regular users without specific roles
        return TechnicianCostMetrics.objects.none()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['technician', 'period_start', 'period_end']
    ordering_fields = ['period_end', 'cost_per_hour', 'cost_per_task', 'efficiency_score']
    ordering = ['-period_end']
    
    @action(detail=False, methods=['get'])
    def by_technician(self, request):
        """Get cost metrics for a specific technician."""
        technician_id = request.query_params.get('technician_id')
        if not technician_id:
            return Response(
                {"error": "technician_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            technician = Technician.objects.get(id=technician_id)
        except Technician.DoesNotExist:
            return Response(
                {"error": "Technician not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        metrics = self.get_queryset().filter(technician=technician)
        
        # Apply period filtering if provided
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        
        if period_start:
            try:
                start_date = datetime.fromisoformat(period_start).date()
                metrics = metrics.filter(period_start__gte=start_date)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid period_start format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if period_end:
            try:
                end_date = datetime.fromisoformat(period_end).date()
                metrics = metrics.filter(period_end__lte=end_date)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid period_end format. Use ISO format (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def record_metrics(self, request):
        """Record cost metrics for a technician."""
        technician_id = request.data.get('technician_id')
        if not technician_id:
            return Response(
                {"error": "technician_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            technician = Technician.objects.get(id=technician_id)
        except Technician.DoesNotExist:
            return Response(
                {"error": "Technician not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Required fields
        required_fields = ['period_start', 'period_end', 'total_hours_worked', 
                          'total_tasks_completed', 'total_cost']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {"error": f"{field} is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Parse dates
        try:
            period_start = datetime.fromisoformat(request.data['period_start']).date()
            period_end = datetime.fromisoformat(request.data['period_end']).date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update metrics
        metrics, created = TechnicianCostMetrics.objects.update_or_create(
            technician=technician,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'total_hours_worked': request.data['total_hours_worked'],
                'total_tasks_completed': request.data['total_tasks_completed'],
                'total_cost': request.data['total_cost'],
                'notes': request.data.get('notes', '')
            }
        )
        
        # Calculate KPIs
        metrics.calculate_kpis()
        
        serializer = self.get_serializer(metrics)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class EmploymentTypeKpiReportViewSet(viewsets.ModelViewSet):
    """ViewSet for employment type KPI reports."""
    queryset = EmploymentTypeKpiReport.objects.all()
    serializer_class = EmploymentTypeKpiReportSerializer
    
    def get_permissions(self):
        """
        Override permissions based on action:
        - Admin and managers can perform all actions
        - Only admin and managers can generate reports and modify data
        - Regular users can only view reports
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'generate']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employment_type', 'period_type', 'period_start', 'period_end']
    ordering_fields = ['period_end', 'avg_cost_per_hour', 'avg_cost_per_task', 
                      'avg_customer_rating', 'avg_efficiency_score']
    ordering = ['-period_end', 'employment_type']
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate KPI reports for all employment types."""
        # Required fields
        required_fields = ['period_type', 'period_start', 'period_end']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {"error": f"{field} is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        period_type = request.data['period_type']
        if period_type not in dict(EmploymentTypeKpiReport.PERIOD_TYPE_CHOICES):
            return Response(
                {"error": "Invalid period_type. Choose from 'monthly', 'quarterly', 'yearly'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        try:
            period_start = datetime.fromisoformat(request.data['period_start']).date()
            period_end = datetime.fromisoformat(request.data['period_end']).date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate reports
        reports = EmploymentTypeKpiReport.generate_report(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end
        )
        
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """Compare KPI reports by employment type for a specific period."""
        # Required query parameters
        period_type = request.query_params.get('period_type', 'monthly')
        if period_type not in dict(EmploymentTypeKpiReport.PERIOD_TYPE_CHOICES):
            return Response(
                {"error": "Invalid period_type. Choose from 'monthly', 'quarterly', 'yearly'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        period_start = request.query_params.get('period_start')
        period_end = request.query_params.get('period_end')
        
        if not period_start or not period_end:
            return Response(
                {"error": "Both period_start and period_end are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.fromisoformat(period_start).date()
            end_date = datetime.fromisoformat(period_end).date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get reports for the period
        reports = self.get_queryset().filter(
            period_type=period_type,
            period_start=start_date,
            period_end=end_date
        )
        
        if not reports.exists():
            return Response(
                {"error": "No reports found for the specified period"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
