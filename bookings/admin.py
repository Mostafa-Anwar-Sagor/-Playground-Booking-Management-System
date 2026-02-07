from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Booking
from accounts.models import User
from playgrounds.models import Playground


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for managing bookings
    """
    
    # List display configuration
    list_display = [
        'booking_id_short',
        'user_info',
        'playground_info', 
        'booking_date',
        'time_slot',
        'duration_hours',
        'total_amount_display',
        'status_badge',
        'payment_status_badge',
        'created_at_short',
        'actions_column'
    ]
    
    # Filters
    list_filter = [
        'status',
        'payment_status',
        'booking_date',
        'created_at',
        'playground__name',
        'playground__city',
        'payment_method',
        'is_recurring',
        'auto_approved'
    ]
    
    # Search functionality
    search_fields = [
        'booking_id',
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'playground__name',
        'contact_phone',
        'playground__address'
    ]
    
    # Ordering
    ordering = ['-created_at']
    
    # Date hierarchy
    date_hierarchy = 'booking_date'
    
    # Fields to display in detail view
    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_id',
                'status',
                'payment_status',
                'auto_approved'
            ),
            'classes': ('wide',)
        }),
        ('Customer Details', {
            'fields': (
                'user',
                'contact_phone',
                'number_of_players'
            ),
            'classes': ('wide',)
        }),
        ('Booking Details', {
            'fields': (
                'playground',
                'booking_date',
                'start_time',
                'end_time',
                'duration_hours'
            ),
            'classes': ('wide',)
        }),
        ('Pricing', {
            'fields': (
                'price_per_hour',
                'total_amount',
                'discount_amount',
                'final_amount'
            ),
            'classes': ('wide',)
        }),
        ('Payment', {
            'fields': (
                'payment_method',
                'payment_reference',
                'payment_receipt',
                'receipt_verified',
                'verified_by',
                'verified_at'
            ),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': (
                'special_requests',
                'owner_notes',
                'user_rating',
                'user_feedback'
            ),
            'classes': ('wide', 'collapse')
        }),
        ('Recurring Booking', {
            'fields': (
                'is_recurring',
                'recurring_pattern'
            ),
            'classes': ('wide', 'collapse')
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'booked_at',
                'confirmed_at',
                'cancelled_at',
                'cancellation_reason'
            ),
            'classes': ('wide', 'collapse')
        })
    )
    
    # Read-only fields
    readonly_fields = [
        'booking_id',
        'created_at',
        'updated_at',
        'booked_at',
        'verified_by',
        'verified_at'
    ]
    
    def verify_payments(self, request, queryset):
        """Admin action to verify selected payment receipts"""
        from django.utils import timezone
        updated = 0
        for booking in queryset:
            if booking.payment_receipt and not booking.receipt_verified:
                booking.receipt_verified = True
                booking.payment_status = 'paid'
                booking.verified_by = request.user
                booking.verified_at = timezone.now()
                booking.save()
                updated += 1
        
        self.message_user(request, f'Successfully verified {updated} payment(s).')
    verify_payments.short_description = "Verify selected payment receipts"
    
    def reject_payments(self, request, queryset):
        """Admin action to reject selected payment receipts"""
        updated = 0
        for booking in queryset:
            if booking.payment_receipt and booking.receipt_verified:
                booking.receipt_verified = False
                booking.payment_status = 'pending'
                booking.verified_by = None
                booking.verified_at = None
                booking.save()
                updated += 1
        
        self.message_user(request, f'Successfully rejected {updated} payment(s).')
    reject_payments.short_description = "Reject selected payment receipts"
    
    # Items per page
    list_per_page = 25
    
    # Enable actions - combined all admin actions
    actions = ['verify_payments', 'reject_payments', 'confirm_bookings', 'cancel_bookings', 'mark_as_completed', 'mark_payment_as_paid']
    
    # Custom methods for display
    def booking_id_short(self, obj):
        """Display shortened booking ID"""
        return str(obj.booking_id)[:8] + '...'
    booking_id_short.short_description = 'Booking ID'
    booking_id_short.admin_order_field = 'booking_id'
    
    def user_info(self, obj):
        """Display user information with link"""
        user_url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</a>',
            user_url,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'Customer'
    user_info.admin_order_field = 'user__username'
    
    def playground_info(self, obj):
        """Display playground information with link"""
        playground_url = reverse('admin:playgrounds_playground_change', args=[obj.playground.id])
        return format_html(
            '<a href="{}" style="text-decoration: none;">'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</a>',
            playground_url,
            obj.playground.name,
            obj.playground.address[:50] + '...' if len(obj.playground.address) > 50 else obj.playground.address
        )
    playground_info.short_description = 'Playground'
    playground_info.admin_order_field = 'playground__name'
    
    def time_slot(self, obj):
        """Display time slot"""
        return format_html(
            '<strong>{}</strong><br>'
            '<small style="color: #666;">to {}</small>',
            obj.start_time.strftime('%I:%M %p'),
            obj.end_time.strftime('%I:%M %p')
        )
    time_slot.short_description = 'Time'
    time_slot.admin_order_field = 'start_time'
    
    def total_amount_display(self, obj):
        """Display total amount with currency"""
        return format_html(
            '<strong style="color: #2e7d32;">${}</strong>',
            obj.final_amount
        )
    total_amount_display.short_description = 'Amount'
    total_amount_display.admin_order_field = 'final_amount'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#ff9800',
            'confirmed': '#4caf50',
            'completed': '#2196f3',
            'cancelled': '#f44336',
            'no_show': '#9e9e9e'
        }
        color = colors.get(obj.status, '#9e9e9e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def payment_status_badge(self, obj):
        """Display payment status with colored badge"""
        colors = {
            'pending': '#ff9800',
            'paid': '#4caf50',
            'failed': '#f44336',
            'refunded': '#9c27b0'
        }
        color = colors.get(obj.payment_status, '#9e9e9e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display().upper()
        )
    payment_status_badge.short_description = 'Payment'
    payment_status_badge.admin_order_field = 'payment_status'
    
    def created_at_short(self, obj):
        """Display creation date in short format"""
        return obj.created_at.strftime('%m/%d/%y %I:%M %p')
    created_at_short.short_description = 'Created'
    created_at_short.admin_order_field = 'created_at'
    
    def actions_column(self, obj):
        """Display action buttons"""
        actions = []
        
        # View booking detail
        detail_url = f"/bookings/{obj.booking_id}/"
        actions.append(f'<a href="{detail_url}" target="_blank" title="View Booking" style="margin-right: 5px;">👁️</a>')
        
        # Email user
        mailto_url = f"mailto:{obj.user.email}?subject=Booking {obj.booking_id}"
        actions.append(f'<a href="{mailto_url}" title="Email Customer" style="margin-right: 5px;">📧</a>')
        
        # Phone number (if available)
        if obj.contact_phone:
            phone_url = f"tel:{obj.contact_phone}"
            actions.append(f'<a href="{phone_url}" title="Call Customer" style="margin-right: 5px;">📞</a>')
        
        return format_html(''.join(actions))
    actions_column.short_description = 'Actions'
    
    # Custom actions
    def confirm_bookings(self, request, queryset):
        """Confirm selected bookings"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} bookings were confirmed.')
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        """Cancel selected bookings"""
        updated = queryset.exclude(status__in=['completed', 'cancelled']).update(status='cancelled')
        self.message_user(request, f'{updated} bookings were cancelled.')
    cancel_bookings.short_description = "Cancel selected bookings"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected bookings as completed"""
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f'{updated} bookings were marked as completed.')
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_payment_as_paid(self, request, queryset):
        """Mark payment as paid for selected bookings"""
        updated = queryset.filter(payment_status='pending').update(payment_status='paid')
        self.message_user(request, f'{updated} payments were marked as paid.')
    mark_payment_as_paid.short_description = "Mark payment as paid"
    
    # Override get_queryset for optimization
    def get_queryset(self, request):
        """Optimize queries with select_related and prefetch_related"""
        return super().get_queryset(request).select_related(
            'user', 'playground', 'playground__city'
        ).prefetch_related(
            'playground__owner'
        )
    
    # Custom view methods
    def changelist_view(self, request, extra_context=None):
        """Add statistics to the changelist view"""
        extra_context = extra_context or {}
        
        # Get booking statistics
        total_bookings = Booking.objects.count()
        total_revenue = Booking.objects.filter(
            payment_status='paid'
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        
        extra_context.update({
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
        })
        
        return super().changelist_view(request, extra_context)


# Register the admin with custom configuration
# admin.site.register(Booking, BookingAdmin) - Already registered with decorator
