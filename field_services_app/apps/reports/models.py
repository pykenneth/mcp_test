"""
Models for the reports app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ReportTemplate(models.Model):
    """
    Report template model for predefined report types.
    """
    
    REPORT_TYPES = (
        ('project', _('Project Report')),
        ('financial', _('Financial Report')),
        ('work_order', _('Work Order Report')),
        ('technician', _('Technician Performance')),
        ('customer', _('Customer Report')),
        ('inventory', _('Inventory Report')),
        ('timesheet', _('Timesheet Report')),
        ('expense', _('Expense Report')),
        ('billing', _('Billing Report')),
        ('custom', _('Custom Report')),
    )
    
    OUTPUT_FORMATS = (
        ('pdf', _('PDF')),
        ('xlsx', _('Excel')),
        ('csv', _('CSV')),
        ('json', _('JSON')),
        ('html', _('HTML')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    report_type = models.CharField(
        _('report type'),
        max_length=20,
        choices=REPORT_TYPES,
        default='custom'
    )
    template_code = models.CharField(_('template code'), max_length=100, unique=True)
    output_formats = models.JSONField(_('output formats'), default=list, blank=True)
    default_format = models.CharField(
        _('default format'),
        max_length=10,
        choices=OUTPUT_FORMATS,
        default='pdf'
    )
    
    # Template content
    template_file = models.FileField(_('template file'), upload_to='report_templates/', null=True, blank=True)
    template_html = models.TextField(_('template HTML'), blank=True)
    template_config = models.JSONField(_('template configuration'), default=dict, blank=True)
    
    # Permissions and access control
    is_system = models.BooleanField(_('system template'), default=False)
    is_public = models.BooleanField(_('public template'), default=False)
    restricted_to_roles = models.JSONField(_('restricted to roles'), default=list, blank=True)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_report_templates',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('report template')
        verbose_name_plural = _('report templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportParameter(models.Model):
    """
    Report parameter model for defining customizable report parameters.
    """
    
    PARAMETER_TYPES = (
        ('string', _('String')),
        ('integer', _('Integer')),
        ('decimal', _('Decimal')),
        ('boolean', _('Boolean')),
        ('date', _('Date')),
        ('datetime', _('Date and Time')),
        ('choice', _('Single Choice')),
        ('multi_choice', _('Multiple Choice')),
        ('user', _('User')),
        ('customer', _('Customer')),
        ('project', _('Project')),
        ('technician', _('Technician')),
    )
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='parameters',
        verbose_name=_('report template')
    )
    name = models.CharField(_('name'), max_length=100)
    label = models.CharField(_('label'), max_length=255)
    parameter_type = models.CharField(
        _('parameter type'),
        max_length=20,
        choices=PARAMETER_TYPES,
        default='string'
    )
    required = models.BooleanField(_('required'), default=False)
    default_value = models.CharField(_('default value'), max_length=255, blank=True)
    help_text = models.CharField(_('help text'), max_length=255, blank=True)
    placeholder = models.CharField(_('placeholder'), max_length=255, blank=True)
    order = models.PositiveIntegerField(_('order'), default=0)
    
    # For choice parameters
    choices = models.JSONField(_('choices'), default=list, blank=True)
    
    # For numeric parameters
    min_value = models.DecimalField(_('minimum value'), max_digits=15, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(_('maximum value'), max_digits=15, decimal_places=2, null=True, blank=True)
    
    # For date parameters
    min_date = models.DateField(_('minimum date'), null=True, blank=True)
    max_date = models.DateField(_('maximum date'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('report parameter')
        verbose_name_plural = _('report parameters')
        ordering = ['template', 'order']
        unique_together = ['template', 'name']
    
    def __str__(self):
        return f"{self.template.name} - {self.label}"


class SavedReport(models.Model):
    """
    Saved report model for storing generated reports.
    """
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('generating', _('Generating')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='saved_reports',
        verbose_name=_('report template')
    )
    parameters = models.JSONField(_('parameters'), default=dict, blank=True)
    output_format = models.CharField(_('output format'), max_length=10, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Report output
    file = models.FileField(_('report file'), upload_to='reports/%Y/%m/', null=True, blank=True)
    result_data = models.JSONField(_('result data'), default=dict, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Date range of the report
    date_from = models.DateField(_('date from'), null=True, blank=True)
    date_to = models.DateField(_('date to'), null=True, blank=True)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='saved_reports',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    generated_at = models.DateTimeField(_('generated at'), null=True, blank=True)
    
    # Related objects
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name=_('project')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name=_('customer')
    )
    
    class Meta:
        verbose_name = _('saved report')
        verbose_name_plural = _('saved reports')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """
    Report schedule model for scheduling report generation.
    """
    
    FREQUENCY_CHOICES = (
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    )
    
    DAY_OF_WEEK_CHOICES = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    )
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('report template')
    )
    parameters = models.JSONField(_('parameters'), default=dict, blank=True)
    output_format = models.CharField(_('output format'), max_length=10, blank=True)
    
    # Schedule configuration
    is_active = models.BooleanField(_('active'), default=True)
    frequency = models.CharField(
        _('frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='monthly'
    )
    time_of_day = models.TimeField(_('time of day'), default='08:00')
    
    # For weekly schedules
    day_of_week = models.IntegerField(
        _('day of week'),
        choices=DAY_OF_WEEK_CHOICES,
        null=True,
        blank=True
    )
    
    # For monthly/quarterly/yearly schedules
    day_of_month = models.IntegerField(_('day of month'), null=True, blank=True)
    month_of_quarter = models.IntegerField(_('month of quarter'), null=True, blank=True)
    month_of_year = models.IntegerField(_('month of year'), null=True, blank=True)
    
    # Date range configuration
    relative_date_range = models.CharField(_('relative date range'), max_length=100, blank=True)
    fixed_date_from = models.DateField(_('fixed date from'), null=True, blank=True)
    fixed_date_to = models.DateField(_('fixed date to'), null=True, blank=True)
    
    # Recipients
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='report_subscriptions',
        verbose_name=_('recipients')
    )
    additional_emails = models.TextField(_('additional emails'), blank=True, 
                                        help_text=_('Separate multiple emails with commas'))
    
    # Tracking
    last_run = models.DateTimeField(_('last run'), null=True, blank=True)
    next_run = models.DateTimeField(_('next run'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_report_schedules',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Related objects
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_schedules',
        verbose_name=_('project')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_schedules',
        verbose_name=_('customer')
    )
    
    class Meta:
        verbose_name = _('report schedule')
        verbose_name_plural = _('report schedules')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def email_recipients_list(self):
        """
        Return a list of all email recipients.
        """
        recipient_emails = [user.email for user in self.recipients.all() if user.email]
        if self.additional_emails:
            additional = [email.strip() for email in self.additional_emails.split(',') if email.strip()]
            recipient_emails.extend(additional)
        return recipient_emails


class Dashboard(models.Model):
    """
    Dashboard model for creating customizable dashboards.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    layout = models.JSONField(_('layout configuration'), default=dict, blank=True)
    is_system = models.BooleanField(_('system dashboard'), default=False)
    is_public = models.BooleanField(_('public dashboard'), default=False)
    is_default = models.BooleanField(_('default dashboard'), default=False)
    
    # Access control
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_dashboards',
        verbose_name=_('owner')
    )
    restricted_to_roles = models.JSONField(_('restricted to roles'), default=list, blank=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_dashboards',
        verbose_name=_('shared with')
    )
    
    # Tracking
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Related objects
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dashboards',
        verbose_name=_('project')
    )
    customer = models.ForeignKey(
        'customers.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dashboards',
        verbose_name=_('customer')
    )
    
    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """
    Dashboard widget model for individual data visualizations.
    """
    
    WIDGET_TYPES = (
        ('metric', _('Metric/KPI')),
        ('chart', _('Chart')),
        ('table', _('Table')),
        ('calendar', _('Calendar')),
        ('map', _('Map')),
        ('task_list', _('Task List')),
        ('news_feed', _('News Feed')),
        ('alert', _('Alert')),
        ('html', _('Custom HTML')),
    )
    
    CHART_TYPES = (
        ('line', _('Line Chart')),
        ('bar', _('Bar Chart')),
        ('pie', _('Pie Chart')),
        ('doughnut', _('Doughnut Chart')),
        ('area', _('Area Chart')),
        ('scatter', _('Scatter Plot')),
        ('bubble', _('Bubble Chart')),
        ('radar', _('Radar Chart')),
        ('heatmap', _('Heatmap')),
        ('gantt', _('Gantt Chart')),
    )
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        verbose_name=_('dashboard')
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    widget_type = models.CharField(
        _('widget type'),
        max_length=20,
        choices=WIDGET_TYPES,
        default='chart'
    )
    chart_type = models.CharField(
        _('chart type'),
        max_length=20,
        choices=CHART_TYPES,
        blank=True
    )
    
    # Widget position and size in the dashboard
    position_x = models.PositiveIntegerField(_('position x'), default=0)
    position_y = models.PositiveIntegerField(_('position y'), default=0)
    width = models.PositiveIntegerField(_('width'), default=6)  # Out of 12 for a grid system
    height = models.PositiveIntegerField(_('height'), default=4)  # In units
    
    # Widget data and configuration
    data_source = models.CharField(_('data source'), max_length=255, blank=True)
    query = models.TextField(_('query'), blank=True)
    parameters = models.JSONField(_('parameters'), default=dict, blank=True)
    configuration = models.JSONField(_('configuration'), default=dict, blank=True)
    
    # For custom HTML widgets
    html_content = models.TextField(_('HTML content'), blank=True)
    
    # Refresh settings
    auto_refresh = models.BooleanField(_('auto refresh'), default=False)
    refresh_interval = models.PositiveIntegerField(_('refresh interval (seconds)'), default=300)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_widgets',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('dashboard widget')
        verbose_name_plural = _('dashboard widgets')
        ordering = ['dashboard', 'position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class ReportMetric(models.Model):
    """
    Report metric model for defining KPIs and metrics.
    """
    
    DATA_TYPE_CHOICES = (
        ('count', _('Count')),
        ('sum', _('Sum')),
        ('average', _('Average')),
        ('min', _('Minimum')),
        ('max', _('Maximum')),
        ('formula', _('Custom Formula')),
        ('percentage', _('Percentage')),
        ('trend', _('Trend')),
    )
    
    code = models.CharField(_('code'), max_length=100, unique=True)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    data_type = models.CharField(
        _('data type'),
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='count'
    )
    
    # Metric source and calculation
    query = models.TextField(_('query'), blank=True)
    formula = models.TextField(_('formula'), blank=True)
    parameters = models.JSONField(_('parameters'), default=dict, blank=True)
    
    # Formatting
    unit = models.CharField(_('unit'), max_length=50, blank=True)
    decimal_places = models.PositiveIntegerField(_('decimal places'), default=2)
    prefix = models.CharField(_('prefix'), max_length=10, blank=True)
    suffix = models.CharField(_('suffix'), max_length=10, blank=True)
    
    # Thresholds for visual indicators
    threshold_warning = models.DecimalField(_('warning threshold'), max_digits=15, decimal_places=2, null=True, blank=True)
    threshold_danger = models.DecimalField(_('danger threshold'), max_digits=15, decimal_places=2, null=True, blank=True)
    threshold_target = models.DecimalField(_('target threshold'), max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Permissions
    is_system = models.BooleanField(_('system metric'), default=False)
    is_public = models.BooleanField(_('public metric'), default=False)
    restricted_to_roles = models.JSONField(_('restricted to roles'), default=list, blank=True)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_metrics',
        verbose_name=_('created by')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('report metric')
        verbose_name_plural = _('report metrics')
        ordering = ['name']
    
    def __str__(self):
        return self.name
