from django.db import models
from django.utils import timezone
from accounts.models import User
from playgrounds.models import Playground
from bookings.models import Booking


def default_dict():
    return {}


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_reminder', 'Booking Reminder'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed'),
        ('payment_refund', 'Payment Refunded'),
        ('playground_approved', 'Playground Approved'),
        ('playground_rejected', 'Playground Rejected'),
        ('partner_approved', 'Partner Application Approved'),
        ('partner_rejected', 'Partner Application Rejected'),
        ('review_received', 'New Review Received'),
        ('review_request', 'Review Request'),
        ('system_announcement', 'System Announcement'),
        ('maintenance_notice', 'Maintenance Notice'),
        ('promotion', 'Promotional Offer'),
        ('achievement_unlocked', 'Achievement Unlocked'),
        ('weather_alert', 'Weather Alert'),
        ('price_change', 'Price Update'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Optional related objects
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status and metadata
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data for rich notifications
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    extra_data = models.JSONField(default=default_dict, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def time_since_created(self):
        """Get human-readable time since creation"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 7:
            return f"{diff.days // 7} week{'s' if diff.days // 7 > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def get_icon_class(self):
        """Get appropriate icon class for notification type"""
        icon_map = {
            'booking_confirmed': 'fas fa-calendar-check text-green-400',
            'booking_cancelled': 'fas fa-calendar-times text-red-400',
            'booking_reminder': 'fas fa-bell text-yellow-400',
            'payment_received': 'fas fa-credit-card text-green-400',
            'payment_failed': 'fas fa-exclamation-triangle text-red-400',
            'payment_refund': 'fas fa-undo text-blue-400',
            'review_request': 'fas fa-star text-yellow-400',
            'promotion': 'fas fa-gift text-purple-400',
            'achievement_unlocked': 'fas fa-trophy text-gold-400',
            'system_announcement': 'fas fa-bullhorn text-blue-400',
            'weather_alert': 'fas fa-cloud-rain text-gray-400',
        }
        return self.icon or icon_map.get(self.notification_type, 'fas fa-info-circle text-blue-400')
    
    def get_priority_class(self):
        """Get CSS class for priority level"""
        priority_map = {
            'low': 'border-gray-500',
            'normal': 'border-blue-500',
            'high': 'border-yellow-500',
            'urgent': 'border-red-500',
        }
        return priority_map.get(self.priority, 'border-blue-500')
    
    @classmethod
    def create_booking_notification(cls, booking, notification_type, additional_message=""):
        """Create a booking-related notification"""
        messages = {
            'booking_confirmed': f'Your booking for {booking.playground.name} on {booking.booking_date} has been confirmed.',
            'booking_cancelled': f'Your booking for {booking.playground.name} on {booking.booking_date} has been cancelled.',
            'booking_reminder': f'Reminder: You have a booking at {booking.playground.name} today at {booking.start_time}.',
            'payment_received': f'Payment received for your booking at {booking.playground.name}.',
            'payment_failed': f'Payment failed for your booking at {booking.playground.name}. Please try again.',
            'payment_refund': f'Refund processed for your cancelled booking at {booking.playground.name}.',
        }
        
        title_map = {
            'booking_confirmed': 'Booking Confirmed',
            'booking_cancelled': 'Booking Cancelled',
            'booking_reminder': 'Booking Reminder',
            'payment_received': 'Payment Successful',
            'payment_failed': 'Payment Failed',
            'payment_refund': 'Refund Processed',
        }
        
        action_urls = {
            'booking_confirmed': f'/bookings/{booking.id}/',
            'booking_cancelled': '/bookings/',
            'booking_reminder': f'/bookings/{booking.id}/',
            'payment_failed': f'/bookings/{booking.id}/payment/',
        }
        
        message = messages.get(notification_type, additional_message)
        title = title_map.get(notification_type, 'Booking Update')
        action_url = action_urls.get(notification_type)
        
        # Set priority based on notification type
        priority = 'high' if notification_type in ['payment_failed', 'booking_cancelled'] else 'normal'
        
        return cls.objects.create(
            recipient=booking.user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            booking=booking,
            playground=booking.playground,
            action_url=action_url,
            action_text='View Details' if action_url else None,
        )


class Message(models.Model):
    MESSAGE_TYPES = (
        ('direct', 'Direct Message'),
        ('support', 'Support Ticket'),
        ('system', 'System Message'),
        ('broadcast', 'Broadcast Message'),
    )
    
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('archived', 'Archived'),
    )
    
    # Message participants
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_received_messages')
    
    # Message content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='direct')
    
    # Related objects
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Thread support
    thread_id = models.CharField(max_length=100, null=True, blank=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Attachments and metadata
    attachment_url = models.URLField(blank=True, null=True)
    extra_data = models.JSONField(default=default_dict, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['thread_id']),
            models.Index(fields=['message_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}: {self.subject}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = 'read'
            self.save()
    
    @property
    def time_since_created(self):
        """Get human-readable time since creation"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 7:
            return f"{diff.days // 7} week{'s' if diff.days // 7 > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def get_sender_avatar(self):
        """Get sender avatar or initials"""
        if hasattr(self.sender, 'profile') and self.sender.profile.avatar:
            return self.sender.profile.avatar.url
        return None
    
    def get_sender_initials(self):
        """Get sender initials for avatar"""
        if self.sender and self.sender.first_name and self.sender.last_name:
            return f"{self.sender.first_name[0]}{self.sender.last_name[0]}".upper()
        elif self.sender and self.sender.username:
            return self.sender.username[0].upper()
        return "U"  # Default fallback
    
    def get_message_type_icon(self):
        """Get icon class for message type"""
        icon_map = {
            'direct': 'fas fa-user text-blue-400',
            'support': 'fas fa-headset text-green-400',
            'system': 'fas fa-cog text-gray-400',
            'broadcast': 'fas fa-bullhorn text-purple-400',
        }
        return icon_map.get(self.message_type, 'fas fa-envelope text-blue-400')
    
    @classmethod
    def create_support_message(cls, user, subject, message):
        """Create a support ticket message"""
        # Get or create support user
        support_user, created = User.objects.get_or_create(
            username='support',
            defaults={
                'email': 'support@playgroundbooking.com',
                'first_name': 'Support',
                'last_name': 'Team',
                'is_staff': True,
            }
        )
        
        return cls.objects.create(
            sender=user,
            recipient=support_user,
            subject=subject,
            message=message,
            message_type='support',
        )
    
    @classmethod
    def create_booking_message(cls, booking, sender, message_text):
        """Create a booking-related message"""
        if sender == booking.user:
            # User messaging playground owner
            recipient = booking.playground.owner
            subject = f"Message about booking #{booking.booking_id}"
        else:
            # Playground owner messaging user
            recipient = booking.user
            subject = f"Update for your booking at {booking.playground.name}"
        
        return cls.objects.create(
            sender=sender,
            recipient=recipient,
            subject=subject,
            message=message_text,
            booking=booking,
            playground=booking.playground,
            message_type='direct',
        )


class SystemMessage(models.Model):
    MESSAGE_TYPES = (
        ('announcement', 'Announcement'),
        ('maintenance', 'Maintenance'),
        ('update', 'System Update'),
        ('promotion', 'Promotion'),
        ('warning', 'Warning'),
    )
    
    AUDIENCE_CHOICES = (
        ('all', 'All Users'),
        ('users', 'Regular Users Only'),
        ('owners', 'Playground Owners Only'),
        ('admins', 'Administrators Only'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='all')
    
    # Scheduling
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Display options
    is_dismissible = models.BooleanField(default=True)
    show_on_dashboard = models.BooleanField(default=True)
    show_as_popup = models.BooleanField(default=False)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"System Message: {self.title}"
    
    def is_visible_for_user(self, user):
        """Check if this message should be visible for the given user"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        if self.start_date > now:
            return False
        
        if self.end_date and self.end_date < now:
            return False
        
        if self.audience == 'all':
            return True
        elif self.audience == 'users' and user.user_type == 'user':
            return True
        elif self.audience == 'owners' and user.user_type == 'owner':
            return True
        elif self.audience == 'admins' and user.user_type == 'admin':
            return True
        
        return False


class NotificationPreference(models.Model):
    """User preferences for different types of notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_booking_confirmations = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=False)
    email_reminders = models.BooleanField(default=True)
    email_system_updates = models.BooleanField(default=True)
    
    # Push notifications (if implementing mobile app)
    push_booking_updates = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_promotions = models.BooleanField(default=False)
    push_reminders = models.BooleanField(default=True)
    
    # SMS notifications
    sms_booking_confirmations = models.BooleanField(default=False)
    sms_payment_updates = models.BooleanField(default=False)
    sms_reminders = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"


class EmailLog(models.Model):
    """Log all emails sent for tracking and debugging"""
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Related notification if applicable
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email to {self.recipient.email}: {self.subject}"
