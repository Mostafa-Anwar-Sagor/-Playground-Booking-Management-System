from django.contrib import admin
from .models import PaymentMethod, PlaygroundPaymentConfig, PlaygroundPaymentMethod


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method_type', 'is_active', 'is_instant', 'requires_receipt']
    list_filter = ['method_type', 'is_active', 'is_instant']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


class PlaygroundPaymentMethodInline(admin.TabularInline):
    model = PlaygroundPaymentMethod
    extra = 1


@admin.register(PlaygroundPaymentConfig)
class PlaygroundPaymentConfigAdmin(admin.ModelAdmin):
    list_display = ['playground', 'bank_name', 'mobile_banking_type', 'auto_approve_payments']
    list_filter = ['auto_approve_payments', 'mobile_banking_type']
    search_fields = ['playground__name', 'bank_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PlaygroundPaymentMethodInline]
    
    fieldsets = (
        ('Playground', {
            'fields': ('playground',)
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_name', 'account_number', 'routing_number', 'bank_qr_code'),
            'classes': ('collapse',)
        }),
        ('Mobile Banking', {
            'fields': ('mobile_banking_number', 'mobile_banking_type', 'mobile_qr_code'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('auto_approve_payments', 'payment_deadline_hours'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
