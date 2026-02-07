from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from accounts.models import User
from playgrounds.models import Playground, TimeSlot
import uuid


def default_dict():
    return {}


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    # Basic booking info
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='bookings')
    
    # Date and time
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Pricing
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Additional details
    number_of_players = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_details = models.JSONField(default=default_dict, blank=True, null=True)
    payment_receipt = models.ImageField(upload_to='payment_receipts/', blank=True, null=True, 
                                       help_text="Upload payment receipt for admin verification")
    receipt_verified = models.BooleanField(default=False, help_text="Admin verification of payment receipt")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='verified_bookings', 
                                  help_text="Admin who verified the payment")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="When the payment was verified")
    
    # Advanced features
    is_recurring = models.BooleanField(default=False)
    recurring_pattern = models.JSONField(default=default_dict, blank=True, null=True)
    auto_approved = models.BooleanField(default=False)
    owner_notes = models.TextField(blank=True, null=True)
    user_rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    user_feedback = models.TextField(blank=True, null=True)
    
    # Booking metadata
    booked_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Refund information
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_status = models.CharField(max_length=20, default='not_applicable',
                                    choices=[
                                        ('not_applicable', 'Not Applicable'),
                                        ('pending', 'Pending'),
                                        ('processed', 'Processed'),
                                        ('completed', 'Completed'),
                                    ])
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # System fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['playground', 'booking_date', 'start_time', 'end_time']
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.playground.name} on {self.booking_date}"
    
    @property
    def is_upcoming(self):
        from datetime import datetime
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        # Make booking_datetime timezone-aware
        booking_datetime = timezone.make_aware(booking_datetime)
        return booking_datetime > timezone.now()
    
    @property
    def is_past(self):
        from datetime import datetime
        booking_datetime = datetime.combine(self.booking_date, self.end_time)
        # Make booking_datetime timezone-aware
        booking_datetime = timezone.make_aware(booking_datetime)
        return booking_datetime < timezone.now()
    
    def can_cancel(self):
        """Check if booking can be cancelled (24 hours before start time)"""
        from datetime import datetime, timedelta
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        # Make booking_datetime timezone-aware
        booking_datetime = timezone.make_aware(booking_datetime)
        return booking_datetime > timezone.now() + timedelta(hours=24)
    
    def calculate_total(self):
        """Calculate total amount based on duration and price"""
        self.total_amount = self.duration_hours * self.price_per_hour
        self.final_amount = self.total_amount - self.discount_amount
        return self.final_amount
    
    def confirm_booking(self):
        """Confirm the booking"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()
    
    def cancel_booking(self, reason=None):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        if reason:
            self.cancellation_reason = reason
        self.save()
    
    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.can_cancel() and self.status in ['pending', 'confirmed']
    
    def can_be_rescheduled(self):
        """Check if booking can be rescheduled"""
        from datetime import datetime, timedelta
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        booking_datetime = timezone.make_aware(booking_datetime)
        return (
            booking_datetime > timezone.now() + timedelta(hours=12) and 
            self.status in ['pending', 'confirmed']
        )
    
    def calculate_refund_amount(self):
        """
        Calculate refund amount based on cancellation policy
        - More than 48 hours before: 100% refund
        - 24-48 hours before: 50% refund
        - Less than 24 hours: No refund
        """
        from datetime import datetime, timedelta
        from decimal import Decimal
        
        # Make sure booking hasn't already passed
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        booking_datetime = timezone.make_aware(booking_datetime)
        
        if booking_datetime <= timezone.now():
            return Decimal('0')  # No refund for past bookings
        
        hours_until_booking = (booking_datetime - timezone.now()).total_seconds() / 3600
        
        # Refund policy based on hours until booking
        if hours_until_booking >= 48:
            # Full refund (100%)
            return self.final_amount
        elif hours_until_booking >= 24:
            # Partial refund (50%)
            return self.final_amount * Decimal('0.5')
        else:
            # No refund
            return Decimal('0')


class BookingPayment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('mobile', 'Mobile Banking'),
        ('online', 'Online Payment'),
        ('wallet', 'Digital Wallet'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_gateway = models.CharField(max_length=50, blank=True)
    
    # Payment status tracking
    is_successful = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_details = models.JSONField(default=default_dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for Booking {self.booking.booking_id} - ${self.amount}"


class BookingHistory(models.Model):
    """Track all changes made to a booking"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=50)  # created, confirmed, cancelled, modified
    old_status = models.CharField(max_length=15, blank=True)
    new_status = models.CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Booking histories"
    
    def __str__(self):
        return f"Booking {self.booking.booking_id} - {self.change_type} at {self.created_at}"


class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Usage limits
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Applicable to
    applicable_playgrounds = models.ManyToManyField(Playground, blank=True)
    applicable_users = models.ManyToManyField(User, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Coupon {self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '$'}"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            self.used_count < self.max_uses
        )
    
    def calculate_discount(self, amount):
        """Calculate discount amount for given booking amount"""
        if not self.is_valid() or amount < self.minimum_amount:
            return 0
        
        if self.discount_type == 'percentage':
            return min(amount * (self.discount_value / 100), amount)
        else:
            return min(self.discount_value, amount)


class BookingCoupon(models.Model):
    """Track coupon usage per booking"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='coupon_usage')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='bookings')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Coupon {self.coupon.code} used for Booking {self.booking.booking_id}"
