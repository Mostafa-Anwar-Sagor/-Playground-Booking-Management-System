"""
Payment Methods models for admin-only management
Only admins can create and manage payment methods
"""

from django.db import models
from django.utils import timezone
from playgrounds.models import Playground


class PaymentMethod(models.Model):
    """Admin-managed payment methods available system-wide"""
    METHOD_TYPES = (
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_banking', 'Mobile Banking'),
        ('digital_wallet', 'Digital Wallet'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )
    
    name = models.CharField(max_length=100, help_text="e.g., 'Bkash', 'Nagad', 'Dutch Bangla Bank'")
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    logo = models.ImageField(upload_to='payment_methods/logos/', blank=True, null=True)
    
    # Instructions for users
    instructions = models.TextField(help_text="Instructions for users on how to pay")
    
    # Configuration fields
    is_active = models.BooleanField(default=True)
    is_instant = models.BooleanField(default=False, help_text="Instant verification possible")
    requires_receipt = models.BooleanField(default=True, help_text="Requires payment receipt upload")
    
    # Admin only fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"


class PlaygroundPaymentConfig(models.Model):
    """Configuration of which payment methods each playground accepts"""
    playground = models.OneToOneField(Playground, on_delete=models.CASCADE, related_name='payment_config')
    
    # Admin assigns available payment methods to each playground
    available_methods = models.ManyToManyField(PaymentMethod, through='PlaygroundPaymentMethod')
    
    # Bank details (set by admin for each playground)
    bank_name = models.CharField(max_length=100, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    routing_number = models.CharField(max_length=20, blank=True)
    
    # Mobile banking details (set by admin)
    mobile_banking_number = models.CharField(max_length=20, blank=True)
    mobile_banking_type = models.CharField(max_length=50, blank=True, help_text="e.g., Bkash, Nagad")
    
    # QR codes (uploaded by admin)
    bank_qr_code = models.ImageField(upload_to='payment_qr/bank/', blank=True, null=True)
    mobile_qr_code = models.ImageField(upload_to='payment_qr/mobile/', blank=True, null=True)
    
    # Settings
    auto_approve_payments = models.BooleanField(default=False, help_text="Auto-approve payments for trusted playgrounds")
    payment_deadline_hours = models.PositiveIntegerField(default=24, help_text="Hours to complete payment after booking")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment Config - {self.playground.name}"


class PlaygroundPaymentMethod(models.Model):
    """Through model for playground-specific payment method configuration"""
    playground_config = models.ForeignKey(PlaygroundPaymentConfig, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    
    # Playground-specific settings for this payment method
    is_enabled = models.BooleanField(default=True)
    custom_instructions = models.TextField(blank=True, help_text="Playground-specific instructions")
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['playground_config', 'payment_method']
    
    def __str__(self):
        return f"{self.playground_config.playground.name} - {self.payment_method.name}"
