from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    TrainingCourse, TrainingModule, Quiz, QuizQuestion, 
    UserCourseEnrollment, UserModuleProgress, QuizAttempt
)
# If serializers.py is created, uncomment this line
# from .serializers import (
#     TrainingCourseSerializer, TrainingModuleSerializer, QuizSerializer, QuizQuestionSerializer,
#     UserCourseEnrollmentSerializer, UserModuleProgressSerializer, QuizAttemptSerializer
# )

class TrainingCourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Training Courses.
    
    Provides CRUD operations for the TrainingCourse model.
    """
    queryset = TrainingCourse.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = TrainingCourseSerializer
    permission_classes = [IsAuthenticated]

class TrainingModuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Training Modules.
    
    Provides CRUD operations for the TrainingModule model.
    """
    queryset = TrainingModule.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = TrainingModuleSerializer
    permission_classes = [IsAuthenticated]

class QuizViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Quizzes.
    
    Provides CRUD operations for the Quiz model.
    """
    queryset = Quiz.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

class QuizQuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Quiz Questions.
    
    Provides CRUD operations for the QuizQuestion model.
    """
    queryset = QuizQuestion.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = QuizQuestionSerializer
    permission_classes = [IsAuthenticated]

class UserCourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for User Course Enrollments.
    
    Provides CRUD operations for the UserCourseEnrollment model.
    """
    queryset = UserCourseEnrollment.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = UserCourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]

class UserModuleProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for User Module Progress.
    
    Provides CRUD operations for the UserModuleProgress model.
    """
    queryset = UserModuleProgress.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = UserModuleProgressSerializer
    permission_classes = [IsAuthenticated]

class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Quiz Attempts.
    
    Provides CRUD operations for the QuizAttempt model.
    """
    queryset = QuizAttempt.objects.all()
    # When serializer is created, uncomment this line
    # serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
