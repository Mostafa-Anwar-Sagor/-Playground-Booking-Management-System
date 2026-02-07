from django.db import models
from django.utils import timezone
from django.db.models import Sum, Q
from accounts.models import User
from playgrounds.models import Playground
from bookings.models import Booking
from decimal import Decimal


def default_dict():
    return {}


def default_list():
    return []


class OwnerEarnings(models.Model):
    """Track earnings for each playground owner"""
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='earnings')
    
    # Total earnings
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    
    # Current month
    current_month_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_month_bookings = models.PositiveIntegerField(default=0)
    
    # Previous month for comparison
    previous_month_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    previous_month_bookings = models.PositiveIntegerField(default=0)
    
    # Platform fees and commissions
    total_platform_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    
    # Improvement fund
    improvement_fund_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    improvement_fund_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment info
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    mobile_banking_number = models.CharField(max_length=15, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Earnings for {self.owner.username} - ${self.total_earnings}"
    
    @property
    def month_over_month_growth(self):
        """Calculate month-over-month growth percentage"""
        if self.previous_month_earnings == 0:
            return 100 if self.current_month_earnings > 0 else 0
        
        growth = ((self.current_month_earnings - self.previous_month_earnings) / self.previous_month_earnings) * 100
        return round(growth, 2)
    
    @property
    def net_earnings(self):
        """Calculate net earnings after platform fees"""
        return self.total_earnings - self.total_platform_fees
    
    def calculate_platform_fee(self, booking_amount):
        """Calculate platform fee for a booking"""
        return (booking_amount * self.platform_fee_percentage) / 100
    
    def add_booking_earnings(self, booking):
        """Add earnings from a new booking"""
        platform_fee = self.calculate_platform_fee(booking.final_amount)
        net_amount = booking.final_amount - platform_fee
        
        # Update totals
        self.total_earnings += net_amount
        self.total_bookings += 1
        self.total_platform_fees += platform_fee
        
        # Update current month
        from datetime import date
        if booking.booking_date.month == date.today().month:
            self.current_month_earnings += net_amount
            self.current_month_bookings += 1
        
        # Add to improvement fund (2% of net earnings)
        improvement_contribution = net_amount * Decimal('0.02')
        self.improvement_fund_balance += improvement_contribution
        
        self.save()
        
        # Create earnings record
        EarningsRecord.objects.create(
            owner=self.owner,
            booking=booking,
            gross_amount=booking.final_amount,
            platform_fee=platform_fee,
            net_amount=net_amount,
            improvement_fund_contribution=improvement_contribution
        )


class EarningsRecord(models.Model):
    """Individual earnings record for each booking"""
    RECORD_TYPES = (
        ('booking', 'Booking Revenue'),
        ('adjustment', 'Manual Adjustment'),
        ('refund', 'Refund'),
        ('bonus', 'Performance Bonus'),
        ('penalty', 'Penalty'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings_records')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='booking')
    description = models.CharField(max_length=200, blank=True)
    
    # Financial details
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    improvement_fund_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_earnings')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Earnings Record - {self.owner.username} - ${self.net_amount}"


class PayoutRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payout_requests')
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment details
    payment_method = models.CharField(max_length=50)  # bank_transfer, mobile_banking, etc.
    account_details = models.JSONField(default=default_dict)  # Bank account or mobile banking details
    
    # Status and processing
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    # Processing information
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payouts')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payouts')
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    requested_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Payout Request - {self.owner.username} - ${self.requested_amount}"
    
    def approve(self, approved_by_user):
        """Approve the payout request"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
    
    def process(self, processed_by_user, transaction_ref=None):
        """Mark payout as processed"""
        self.status = 'processed'
        self.processed_by = processed_by_user
        self.processed_at = timezone.now()
        if transaction_ref:
            self.transaction_reference = transaction_ref
        self.save()
        
        # Deduct from owner's earnings
        try:
            earnings = self.owner.earnings
            earnings.total_earnings -= self.requested_amount
            earnings.save()
        except OwnerEarnings.DoesNotExist:
            pass


class ImprovementFund(models.Model):
    """Track improvement fund usage by playground owners"""
    FUND_TYPES = (
        ('maintenance', 'Maintenance & Repairs'),
        ('equipment', 'Equipment Purchase'),
        ('upgrade', 'Facility Upgrade'),
        ('marketing', 'Marketing & Promotion'),
        ('training', 'Staff Training'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='improvement_requests')
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='improvement_funds')
    
    # Request details
    fund_type = models.CharField(max_length=20, choices=FUND_TYPES)
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    justification = models.TextField()
    
    # Supporting documents
    supporting_documents = models.JSONField(default=default_list, blank=True)  # List of document URLs
    estimated_completion_date = models.DateField(null=True, blank=True)
    
    # Approval and processing
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='requested')
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admin_comments = models.TextField(blank=True, null=True)
    
    # Processing info
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_improvements')
    disbursed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disbursed_improvements')
    
    # Timestamps
    requested_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Improvement Fund - {self.playground.name} - ${self.requested_amount}"


class PerformanceMetrics(models.Model):
    """Monthly performance metrics for playground owners"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Period
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    
    # Booking metrics
    total_bookings = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    
    # Customer metrics
    unique_customers = models.PositiveIntegerField(default=0)
    repeat_customers = models.PositiveIntegerField(default=0)
    customer_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # Average rating
    
    # Operational metrics
    cancellation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    no_show_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    response_time_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['owner', 'playground', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"Performance Metrics - {self.playground.name} - {self.year}/{self.month}"
