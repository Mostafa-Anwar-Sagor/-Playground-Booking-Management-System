from django.db import models
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from accounts.models import User
from playgrounds.models import Playground, City, State, Country
from bookings.models import Booking
from earnings.models import OwnerEarnings


def default_dict():
    return {}


def default_list():
    return []


class PlatformSettings(models.Model):
    """Global platform settings that admins can configure"""
    SETTING_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('email', 'Email'),
        ('url', 'URL'),
    )
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=10, choices=SETTING_TYPES, default='text')
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)  # Can be accessed by frontend
    
    category = models.CharField(max_length=50, default='general')  # general, payment, notification, etc.
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    def get_typed_value(self):
        """Return value in correct type"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.setting_type == 'number':
            try:
                if '.' in self.value:
                    return float(self.value)
                return int(self.value)
            except ValueError:
                return 0
        elif self.setting_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        return self.value


class PlatformAnalytics(models.Model):
    """Store daily analytics data for the platform"""
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_owners = models.PositiveIntegerField(default=0)
    new_owners = models.PositiveIntegerField(default=0)
    
    # Playground metrics
    total_playgrounds = models.PositiveIntegerField(default=0)
    new_playgrounds = models.PositiveIntegerField(default=0)
    active_playgrounds = models.PositiveIntegerField(default=0)
    
    # Booking metrics
    total_bookings = models.PositiveIntegerField(default=0)
    new_bookings = models.PositiveIntegerField(default=0)
    confirmed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    owner_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Performance metrics
    average_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Platform Analytics"
    
    def __str__(self):
        return f"Analytics for {self.date}"
    
    @classmethod
    def generate_daily_analytics(cls, date=None):
        """Generate analytics data for a specific date"""
        if date is None:
            date = timezone.now().date()
        
        # Get or create analytics record
        analytics, created = cls.objects.get_or_create(date=date)
        
        # Calculate user metrics
        analytics.total_users = User.objects.count()
        analytics.new_users = User.objects.filter(date_joined__date=date).count()
        analytics.active_users = User.objects.filter(last_login__date=date).count()
        analytics.total_owners = User.objects.filter(user_type='owner').count()
        analytics.new_owners = User.objects.filter(user_type='owner', date_joined__date=date).count()
        
        # Calculate playground metrics
        analytics.total_playgrounds = Playground.objects.count()
        analytics.new_playgrounds = Playground.objects.filter(created_at__date=date).count()
        analytics.active_playgrounds = Playground.objects.filter(status='active').count()
        
        # Calculate booking metrics
        bookings_on_date = Booking.objects.filter(created_at__date=date)
        analytics.total_bookings = Booking.objects.count()
        analytics.new_bookings = bookings_on_date.count()
        analytics.confirmed_bookings = bookings_on_date.filter(status='confirmed').count()
        analytics.cancelled_bookings = bookings_on_date.filter(status='cancelled').count()
        analytics.completed_bookings = bookings_on_date.filter(status='completed').count()
        
        # Calculate revenue metrics
        completed_bookings = Booking.objects.filter(
            status='completed',
            payment_status='paid'
        )
        
        total_revenue = completed_bookings.aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        analytics.total_revenue = total_revenue
        analytics.platform_revenue = total_revenue * 0.1  # 10% platform fee
        analytics.owner_revenue = total_revenue * 0.9
        
        # Calculate performance metrics
        if completed_bookings.exists():
            analytics.average_booking_value = completed_bookings.aggregate(
                Avg('final_amount')
            )['final_amount__avg'] or 0
        
        # Average rating across all playgrounds
        avg_rating = Playground.objects.aggregate(Avg('rating'))['rating__avg']
        analytics.average_rating = avg_rating or 0
        
        analytics.save()
        return analytics


class AdminActivity(models.Model):
    """Log all admin activities for audit trail"""
    ACTIVITY_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('suspend', 'Suspend'),
        ('activate', 'Activate'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    )
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=500)
    
    # Related object information
    object_type = models.CharField(max_length=50, blank=True)  # User, Playground, Booking, etc.
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_repr = models.CharField(max_length=200, blank=True)
    
    # Request information
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Additional data
    extra_data = models.JSONField(default=default_dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Admin Activities"
    
    def __str__(self):
        return f"{self.admin.username} - {self.activity_type} - {self.description}"


class SystemHealth(models.Model):
    """Monitor system health and performance"""
    HEALTH_STATUS = (
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('maintenance', 'Maintenance'),
    )
    
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=15, choices=HEALTH_STATUS, default='healthy')
    
    # System metrics
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    memory_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    disk_usage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Database metrics
    db_connections = models.PositiveIntegerField(default=0)
    db_query_time = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    
    # Application metrics
    active_sessions = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    response_time = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    
    # Additional metrics
    redis_status = models.BooleanField(default=True)
    celery_status = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "System Health"
    
    def __str__(self):
        return f"System Health - {self.timestamp} - {self.status}"


class DataBackup(models.Model):
    """Track database backups"""
    BACKUP_TYPES = (
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('emergency', 'Emergency'),
    )
    
    STATUS_CHOICES = (
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    backup_type = models.CharField(max_length=15, choices=BACKUP_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='running')
    
    # Backup details
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # Size in bytes
    compression_type = models.CharField(max_length=20, default='gzip')
    
    # Tables included
    tables_included = models.JSONField(default=default_list, blank=True)
    records_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    # Initiated by
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Backup - {self.backup_type} - {self.started_at} - {self.status}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0


class FeatureFlag(models.Model):
    """Control feature rollouts and A/B testing"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    
    # Rollout control
    rollout_percentage = models.PositiveIntegerField(default=100, help_text="Percentage of users who see this feature")
    target_user_types = models.JSONField(default=default_list, blank=True, help_text="List of user types: ['user', 'owner', 'admin']")
    
    # A/B Testing
    variants = models.JSONField(default=default_dict, blank=True, help_text="Feature variants for A/B testing")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feature: {self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    def is_enabled_for_user(self, user):
        """Check if feature is enabled for a specific user"""
        if not self.is_active:
            return False
        
        # Check user type targeting
        if self.target_user_types and user.user_type not in self.target_user_types:
            return False
        
        # Check rollout percentage
        if self.rollout_percentage < 100:
            # Use user ID for consistent rollout
            user_hash = hash(f"{user.id}{self.name}") % 100
            return user_hash < self.rollout_percentage
        
        return True
