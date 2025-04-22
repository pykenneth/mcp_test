"""
Models for the training app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TrainingCourse(models.Model):
    """
    Training course model for organizing training content.
    """
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    
    DIFFICULTY_CHOICES = (
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    )
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    summary = models.TextField(_('summary'), blank=True)
    learning_objectives = models.TextField(_('learning objectives'), blank=True)
    prerequisites = models.TextField(_('prerequisites'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    difficulty = models.CharField(
        _('difficulty'),
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='intermediate'
    )
    duration_minutes = models.PositiveIntegerField(_('duration (minutes)'), default=60)
    is_required = models.BooleanField(_('required course'), default=False)
    category = models.CharField(_('category'), max_length=100, blank=True)
    tags = models.CharField(_('tags'), max_length=255, blank=True)
    
    # Image and branding
    featured_image = models.ImageField(_('featured image'), upload_to='training/courses/', null=True, blank=True)
    
    # Access control
    is_public = models.BooleanField(_('public'), default=False)
    restricted_to_roles = models.JSONField(_('restricted to roles'), default=list, blank=True)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_courses',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    # Certification
    certificate_available = models.BooleanField(_('certificate available'), default=False)
    certificate_template = models.FileField(_('certificate template'), upload_to='training/certificates/', null=True, blank=True)
    passing_score = models.PositiveIntegerField(_('passing score (%)'), default=80)
    
    class Meta:
        verbose_name = _('training course')
        verbose_name_plural = _('training courses')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def modules_count(self):
        """
        Return the number of modules in the course.
        """
        return self.modules.count()
    
    @property
    def total_duration(self):
        """
        Return the total duration of all modules in the course in minutes.
        """
        return sum(module.duration_minutes for module in self.modules.all())


class TrainingModule(models.Model):
    """
    Training module model for organizing course content.
    """
    
    TYPE_CHOICES = (
        ('video', _('Video')),
        ('document', _('Document')),
        ('presentation', _('Presentation')),
        ('quiz', _('Quiz')),
        ('interactive', _('Interactive')),
        ('assignment', _('Assignment')),
        ('webinar', _('Webinar')),
        ('assessment', _('Assessment')),
    )
    
    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name=_('course')
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='video'
    )
    content = models.TextField(_('content'), blank=True)
    order = models.PositiveIntegerField(_('order'), default=0)
    duration_minutes = models.PositiveIntegerField(_('duration (minutes)'), default=10)
    is_required = models.BooleanField(_('required module'), default=True)
    
    # Module files
    file = models.FileField(_('file'), upload_to='training/modules/', null=True, blank=True)
    video_url = models.URLField(_('video URL'), blank=True)
    external_link = models.URLField(_('external link'), blank=True)
    
    # Tracking
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('training module')
        verbose_name_plural = _('training modules')
        ordering = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Quiz(models.Model):
    """
    Quiz model for assessments.
    """
    
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name=_('module')
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    time_limit_minutes = models.PositiveIntegerField(_('time limit (minutes)'), default=0)
    passing_score = models.PositiveIntegerField(_('passing score (%)'), default=80)
    max_attempts = models.PositiveIntegerField(_('maximum attempts'), default=3)
    randomize_questions = models.BooleanField(_('randomize questions'), default=False)
    show_correct_answers = models.BooleanField(_('show correct answers'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('quiz')
        verbose_name_plural = _('quizzes')
        ordering = ['module', 'title']
    
    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"
    
    @property
    def questions_count(self):
        """
        Return the number of questions in the quiz.
        """
        return self.questions.count()


class QuizQuestion(models.Model):
    """
    Quiz question model.
    """
    
    TYPE_CHOICES = (
        ('multiple_choice', _('Multiple Choice')),
        ('true_false', _('True/False')),
        ('short_answer', _('Short Answer')),
        ('essay', _('Essay')),
        ('matching', _('Matching')),
        ('fill_blank', _('Fill in the Blank')),
    )
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('quiz')
    )
    question_text = models.TextField(_('question text'))
    question_type = models.CharField(
        _('question type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='multiple_choice'
    )
    explanation = models.TextField(_('explanation'), blank=True)
    points = models.PositiveIntegerField(_('points'), default=1)
    order = models.PositiveIntegerField(_('order'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('quiz question')
        verbose_name_plural = _('quiz questions')
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Question {self.order + 1}"


class QuizAnswer(models.Model):
    """
    Quiz answer model for multiple-choice and other question types.
    """
    
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('question')
    )
    answer_text = models.CharField(_('answer text'), max_length=255)
    is_correct = models.BooleanField(_('correct answer'), default=False)
    order = models.PositiveIntegerField(_('order'), default=0)
    
    class Meta:
        verbose_name = _('quiz answer')
        verbose_name_plural = _('quiz answers')
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question} - Answer {self.order + 1}"


class UserCourseEnrollment(models.Model):
    """
    User enrollment in a training course.
    """
    
    STATUS_CHOICES = (
        ('enrolled', _('Enrolled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('expired', _('Expired')),
        ('withdrawn', _('Withdrawn')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name=_('user')
    )
    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('course')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled'
    )
    progress_percent = models.PositiveIntegerField(_('progress (%)'), default=0)
    score = models.PositiveIntegerField(_('score (%)'), null=True, blank=True)
    is_certified = models.BooleanField(_('certified'), default=False)
    
    # Dates
    enrolled_at = models.DateTimeField(_('enrolled at'), auto_now_add=True)
    last_accessed_at = models.DateTimeField(_('last accessed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    due_date = models.DateField(_('due date'), null=True, blank=True)
    
    # Tracking
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrolled_users',
        verbose_name=_('enrolled by')
    )
    notes = models.TextField(_('notes'), blank=True)
    
    # Certificate
    certificate_issued_at = models.DateTimeField(_('certificate issued at'), null=True, blank=True)
    certificate_file = models.FileField(_('certificate file'), upload_to='training/user_certificates/', null=True, blank=True)
    certificate_number = models.CharField(_('certificate number'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('user course enrollment')
        verbose_name_plural = _('user course enrollments')
        ordering = ['-enrolled_at']
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"
    
    @property
    def is_overdue(self):
        """
        Check if the enrollment is overdue.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.due_date and 
            today > self.due_date and 
            self.status not in ['completed', 'failed', 'expired', 'withdrawn']
        )
    
    @property
    def days_until_due(self):
        """
        Calculate the number of days until the enrollment is due.
        """
        if not self.due_date:
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        delta = self.due_date - today
        return delta.days


class UserModuleProgress(models.Model):
    """
    User progress on a specific module.
    """
    
    STATUS_CHOICES = (
        ('not_started', _('Not Started')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
    )
    
    enrollment = models.ForeignKey(
        UserCourseEnrollment,
        on_delete=models.CASCADE,
        related_name='module_progress',
        verbose_name=_('enrollment')
    )
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('module')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    progress_percent = models.PositiveIntegerField(_('progress (%)'), default=0)
    time_spent_seconds = models.PositiveIntegerField(_('time spent (seconds)'), default=0)
    
    # Dates
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    last_accessed_at = models.DateTimeField(_('last accessed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('user module progress')
        verbose_name_plural = _('user module progress')
        ordering = ['enrollment', 'module__order']
        unique_together = ['enrollment', 'module']
    
    def __str__(self):
        return f"{self.enrollment.user.get_full_name()} - {self.module.title}"
    
    @property
    def formatted_time_spent(self):
        """
        Return the time spent in a human-readable format.
        """
        minutes, seconds = divmod(self.time_spent_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class QuizAttempt(models.Model):
    """
    User attempt at a quiz.
    """
    
    STATUS_CHOICES = (
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('timed_out', _('Timed Out')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name=_('user')
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('quiz')
    )
    module_progress = models.ForeignKey(
        UserModuleProgress,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name=_('module progress')
    )
    attempt_number = models.PositiveIntegerField(_('attempt number'), default=1)
    score = models.PositiveIntegerField(_('score (%)'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    passed = models.BooleanField(_('passed'), default=False)
    
    # Timing
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(_('time spent (seconds)'), default=0)
    
    class Meta:
        verbose_name = _('quiz attempt')
        verbose_name_plural = _('quiz attempts')
        ordering = ['user', 'quiz', '-attempt_number']
        unique_together = ['user', 'quiz', 'attempt_number']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.quiz.title} - Attempt {self.attempt_number}"
    
    def calculate_score(self):
        """
        Calculate the quiz score based on the answers.
        """
        if self.status != 'completed':
            return None
        
        total_points = sum(q.points for q in self.quiz.questions.all())
        if total_points == 0:
            return 0
        
        earned_points = sum(a.points_earned for a in self.answers.all())
        score_percent = int((earned_points / total_points) * 100)
        
        self.score = score_percent
        self.passed = score_percent >= self.quiz.passing_score
        self.save(update_fields=['score', 'passed'])
        
        return score_percent


class QuizAnswerResponse(models.Model):
    """
    User response to a quiz question.
    """
    
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('attempt')
    )
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('question')
    )
    selected_answers = models.ManyToManyField(
        QuizAnswer,
        related_name='responses',
        verbose_name=_('selected answers'),
        blank=True
    )
    text_response = models.TextField(_('text response'), blank=True)
    is_correct = models.BooleanField(_('correct'), default=False)
    points_earned = models.PositiveIntegerField(_('points earned'), default=0)
    feedback = models.TextField(_('feedback'), blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('quiz answer response')
        verbose_name_plural = _('quiz answer responses')
        ordering = ['attempt', 'question']
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt} - {self.question}"
