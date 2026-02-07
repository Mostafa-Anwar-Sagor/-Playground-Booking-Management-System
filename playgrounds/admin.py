from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.db.models import Count, Avg, Q
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import (Country, State, City, SportType, Playground, 
                     PlaygroundImage, TimeSlot, Review)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_currency_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'currency_code')
    ordering = ('name',)
    list_editable = ('is_active',)
    
    def get_currency_display(self, obj):
        """Display currency with symbol"""
        currency_symbols = {
            'USD': '$ (USD)', 'EUR': '€ (EUR)', 'GBP': '£ (GBP)', 
            'MYR': 'RM (MYR)', 'SGD': 'S$ (SGD)', 'INR': '₹ (INR)', 
            'BDT': '৳ (BDT)', 'AUD': 'A$ (AUD)', 'CAD': 'C$ (CAD)', 
            'JPY': '¥ (JPY)', 'CNY': '¥ (CNY)', 'THB': '฿ (THB)'
        }
        currency = obj.get_currency()
        return currency_symbols.get(currency, currency)
    get_currency_display.short_description = 'Currency'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_active', 'created_at')
    list_filter = ('country', 'is_active', 'created_at')
    search_fields = ('name', 'country__name')
    ordering = ('country__name', 'name')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'get_country', 'is_active', 'created_at')
    list_filter = ('state__country', 'state', 'is_active', 'created_at')
    search_fields = ('name', 'state__name', 'state__country__name')
    ordering = ('state__country__name', 'state__name', 'name')
    
    def get_country(self, obj):
        return obj.state.country.name
    get_country.short_description = 'Country'


@admin.register(SportType)
class SportTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


class PlaygroundImageInline(admin.TabularInline):
    model = PlaygroundImage
    extra = 1


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 1


@admin.register(Playground)
class PlaygroundAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'playground_type', 'status', 'get_currency_display', 'price_per_hour', 'rating', 'is_popular', 'total_bookings_display', 'created_at')
    list_filter = ('status', 'playground_type', 'city__state__country', 'city__state', 'is_popular', 'is_verified', 'created_at')
    search_fields = ('name', 'owner__email', 'owner__first_name', 'owner__last_name', 'city__name', 'description')
    ordering = ('-is_popular', '-rating', '-created_at')
    list_editable = ('status', 'is_popular')
    actions = ['mark_as_popular', 'unmark_as_popular', 'approve_playgrounds']
    
    def get_currency_display(self, obj):
        """Display currency based on country"""
        currency_map = {
            'US': 'USD ($)', 'GB': 'GBP (£)', 'MY': 'MYR (RM)', 'SG': 'SGD (S$)',
            'IN': 'INR (₹)', 'BD': 'BDT (৳)', 'AU': 'AUD (A$)', 'CA': 'CAD (C$)',
            'JP': 'JPY (¥)', 'CN': 'CNY (¥)', 'AE': 'AED (د.إ)', 'TH': 'THB (฿)'
        }
        if obj.city and obj.city.state and obj.city.state.country:
            code = obj.city.state.country.code
            return currency_map.get(code, obj.currency)
        return obj.currency
    get_currency_display.short_description = 'Currency'
    
    def is_popular_badge(self, obj):
        """Display popular status with badge"""
        if obj.is_popular:
            return format_html(
                '<span style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 4px 10px; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);">⭐ POPULAR</span>'
            )
        return format_html(
            '<span style="color: #9ca3af; font-size: 12px;">Not popular</span>'
        )
    is_popular_badge.short_description = 'Homepage Status'
    is_popular_badge.admin_order_field = 'is_popular'
    
    def get_owner_email(self, obj):
        """Display owner's email for easier contact"""
        return obj.owner.email
    get_owner_email.short_description = 'Owner Email'
    
    def total_bookings_display(self, obj):
        """Display total bookings with link to bookings"""
        from bookings.models import Booking
        count = Booking.objects.filter(playground=obj).count()
        if count > 0:
            url = reverse('admin:bookings_booking_changelist') + f'?playground__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #2e7d32; font-weight: bold;">{} booking{}</a>',
                url,
                count,
                's' if count != 1 else ''
            )
        return '0 bookings'
    total_bookings_display.short_description = 'Bookings'
    total_bookings_display.admin_order_field = 'total_bookings'
    
    # Admin actions
    def mark_as_popular(self, request, queryset):
        """Mark selected playgrounds as popular (will appear on homepage)"""
        # Only mark active playgrounds
        active_queryset = queryset.filter(status='active')
        updated = active_queryset.update(is_popular=True)
        
        if updated > 0:
            self.message_user(
                request, 
                f'✅ {updated} playground(s) marked as POPULAR and will now appear on the homepage!',
                messages.SUCCESS
            )
        
        inactive_count = queryset.exclude(status='active').count()
        if inactive_count > 0:
            self.message_user(
                request,
                f'⚠️ {inactive_count} playground(s) skipped (only active playgrounds can be popular)',
                messages.WARNING
            )
    mark_as_popular.short_description = '⭐ Add to Popular (Homepage)'
    
    def unmark_as_popular(self, request, queryset):
        """Remove popular status from selected playgrounds"""
        updated = queryset.update(is_popular=False)
        self.message_user(
            request, 
            f'❌ {updated} playground(s) removed from popular section. They will no longer appear on homepage.',
            messages.SUCCESS
        )
    unmark_as_popular.short_description = '❌ Remove from Popular (Homepage)'
    
    inlines = [PlaygroundImageInline, TimeSlotInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'name', 'description', 'city', 'address')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Details', {
            'fields': ('sport_types', 'playground_type', 'capacity', 'size')
        }),
        ('Pricing', {
            'fields': ('price_per_hour', 'price_per_day')
        }),
        ('Features', {
            'fields': ('amenities', 'rules', 'main_image')
        }),
        ('Status', {
            'fields': ('status', 'is_popular', 'is_verified')
        }),
        ('Analytics', {
            'fields': ('total_bookings', 'rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('total_bookings', 'rating', 'review_count')
    filter_horizontal = ('sport_types',)
    
    # Override the duplicate actions list from below
    def get_actions(self, request):
        """Get available admin actions"""
        actions = super().get_actions(request)
        # Remove default delete action if needed
        return actions
    
    def approve_playgrounds(self, request, queryset):
        """Approve selected playgrounds"""
        approved_count = 0
        for playground in queryset.filter(status='pending'):
            playground.status = 'active'
            playground.is_verified = True
            playground.save()
            approved_count += 1
            
            # Send notification to playground owner
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=playground.owner,
                    title='Playground Approved!',
                    message=f'Your playground "{playground.name}" has been approved and is now active for bookings!',
                    notification_type='playground_approved'
                )
            except (ImportError, Exception):
                pass  # Notifications app might not be available
        
        self.message_user(request, f"✅ {approved_count} playgrounds approved and activated.")
    approve_playgrounds.short_description = "✅ Approve & Activate"
    
    def reject_playgrounds(self, request, queryset):
        """Reject selected playgrounds"""
        rejected_count = 0
        for playground in queryset.filter(status='pending'):
            playground.status = 'inactive'
            playground.save()
            rejected_count += 1
            
            # Send notification to playground owner
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=playground.owner,
                    title='Playground Rejected',
                    message=f'Sorry, your playground "{playground.name}" was not approved. Please contact admin for details.',
                    notification_type='playground_rejected'
                )
            except (ImportError, Exception):
                pass  # Notifications app might not be available
        
        self.message_user(request, f"❌ {rejected_count} playgrounds rejected and deactivated.")
    reject_playgrounds.short_description = "❌ Reject Playgrounds"
    
    def bulk_approve_new_playgrounds(self, request, queryset):
        """Bulk approve all pending playgrounds from approved partners"""
        pending_playgrounds = queryset.filter(status='pending')
        approved_count = 0
        
        for playground in pending_playgrounds:
            # Check if owner has approved partner application
            from accounts.models import PartnerApplication
            partner_app = PartnerApplication.objects.filter(
                user=playground.owner, 
                status='approved'
            ).first()
            
            if partner_app:
                playground.status = 'active'
                playground.is_verified = True
                playground.save()
                approved_count += 1
        
        self.message_user(request, f"🚀 {approved_count} playgrounds auto-approved from verified partners.")
    bulk_approve_new_playgrounds.short_description = "🚀 Auto-approve (Verified Partners)"
    
    def save_model(self, request, obj, form, change):
        """Handle status changes made directly in the admin form"""
        if change:  # Only for existing objects
            # Get the original object to compare status
            try:
                original = Playground.objects.get(pk=obj.pk)
                old_status = original.status
                new_status = obj.status
                
                # Save the object first
                super().save_model(request, obj, form, change)
                
                # Handle status changes and send notifications
                if old_status != new_status:
                    if new_status == 'active' and old_status == 'pending':
                        # Playground was approved
                        obj.is_verified = True
                        obj.save(update_fields=['is_verified'])
                        
                        # Send approval notification
                        try:
                            from notifications.models import Notification
                            Notification.objects.create(
                                recipient=obj.owner,
                                title='Playground Approved!',
                                message=f'Your playground "{obj.name}" has been approved and is now active for bookings!',
                                notification_type='playground_approved'
                            )
                        except (ImportError, Exception):
                            pass
                        
                        try:
                            self.message_user(request, f"✅ Playground '{obj.name}' approved and notification sent to owner.")
                        except:
                            pass  # Messages might not be available in tests
                    
                    elif new_status == 'inactive' and old_status in ['pending', 'active']:
                        # Playground was rejected/deactivated
                        obj.is_verified = False
                        obj.save(update_fields=['is_verified'])
                        
                        # Send rejection notification
                        try:
                            from notifications.models import Notification
                            Notification.objects.create(
                                recipient=obj.owner,
                                title='Playground Status Changed',
                                message=f'Your playground "{obj.name}" status has been changed to inactive. Please contact admin for details.',
                                notification_type='playground_rejected'
                            )
                        except (ImportError, Exception):
                            pass
                        
                        try:
                            self.message_user(request, f"❌ Playground '{obj.name}' deactivated and notification sent to owner.")
                        except:
                            pass  # Messages might not be available in tests
                
            except Playground.DoesNotExist:
                # Original object not found, just save normally
                super().save_model(request, obj, form, change)
        else:
            # New object, save normally
            super().save_model(request, obj, form, change)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('playground', 'day_of_week', 'start_time', 'end_time', 'price', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'playground__city')
    search_fields = ('playground__name', 'playground__owner__email', 'playground__owner__first_name')
    ordering = ('playground', 'day_of_week', 'start_time')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('playground', 'user', 'rating', 'is_approved', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_featured', 'created_at')
    search_fields = ('playground__name', 'user__email', 'user__first_name', 'user__last_name', 'comment')
    ordering = ('-created_at',)
    
    actions = ['approve_reviews', 'feature_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    
    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} reviews featured.")
    
    approve_reviews.short_description = "Approve selected reviews"
    feature_reviews.short_description = "Feature selected reviews"


# Custom Admin for Popular Playgrounds Management
class PopularPlaygroundAdmin(admin.ModelAdmin):
    """
    Dedicated admin interface for managing popular playgrounds shown on homepage.
    This allows admins to easily control which playgrounds appear in the "Most Popular Playgrounds" section.
    """
    
    def get_model_perms(self, request):
        """
        Return permissions to make this appear in admin but use the same model as Playground.
        """
        return {
            'add': True,  # Enable add button
            'change': True,
            'delete': False,
            'view': True
        }
    
    def get_urls(self):
        """Add custom URL for adding playgrounds to popular"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('add-to-popular/', self.admin_site.admin_view(self.add_to_popular_view), name='playgrounds_popularplayground_add'),
        ]
        return custom_urls + urls
    
    def add_to_popular_view(self, request):
        """Custom view to add playgrounds to popular section"""
        if request.method == 'POST':
            playground_ids = request.POST.getlist('playgrounds')
            if playground_ids:
                updated = Playground.objects.filter(
                    id__in=playground_ids,
                    status='active'
                ).update(is_popular=True)
                
                self.message_user(
                    request,
                    f'✅ {updated} playground(s) added to Popular section and will appear on homepage!',
                    messages.SUCCESS
                )
                return HttpResponseRedirect('../')
            else:
                self.message_user(
                    request,
                    '⚠️ Please select at least one playground.',
                    messages.WARNING
                )
        
        # Get non-popular playgrounds
        available_playgrounds = Playground.objects.filter(
            status='active',
            is_popular=False
        ).select_related('city__state__country', 'owner').order_by('-rating', 'name')
        
        context = {
            'title': 'Add Playgrounds to Popular Section',
            'available_playgrounds': available_playgrounds,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
        }
        
        return render(request, 'admin/playgrounds/add_to_popular.html', context)
    
    def get_queryset(self, request):
        """Only show popular playgrounds"""
        qs = super().get_queryset(request)
        return qs.filter(is_popular=True, status='active').select_related('owner', 'city__state__country')
    
    list_display = (
        'popular_badge',
        'name',
        'owner_info',
        'location_display',
        'get_currency_display',
        'price_per_hour',
        'rating_display',
        'bookings_display',
        'quick_actions'
    )
    
    list_filter = ('city__state__country', 'city__state', 'playground_type', 'rating')
    search_fields = ('name', 'owner__email', 'city__name', 'description')
    ordering = ('-rating', '-total_bookings', 'name')
    
    actions = ['remove_from_popular']
    
    # Custom display methods
    def popular_badge(self, obj):
        return format_html(
            '<div style="text-align: center;"><span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 11px; display: inline-block;">⭐ POPULAR</span></div>'
        )
    popular_badge.short_description = 'Status'
    
    def owner_info(self, obj):
        return format_html(
            '<div style="line-height: 1.4;"><strong>{}</strong><br><span style="color: #6b7280; font-size: 11px;">{}</span></div>',
            obj.owner.get_full_name() or obj.owner.email,
            obj.owner.email
        )
    owner_info.short_description = 'Owner'
    
    def location_display(self, obj):
        if obj.city and obj.city.state and obj.city.state.country:
            return format_html(
                '<div style="line-height: 1.4;"><strong>{}</strong><br><span style="color: #6b7280; font-size: 11px;">{}, {}</span></div>',
                obj.city.name,
                obj.city.state.name,
                obj.city.state.country.name
            )
        return '-'
    location_display.short_description = 'Location'
    
    def get_currency_display(self, obj):
        """Display currency based on country"""
        currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'MYR': 'RM', 'SGD': 'S$',
            'INR': '₹', 'BDT': '৳', 'AUD': 'A$', 'CAD': 'C$', 'JPY': '¥',
            'CNY': '¥', 'AED': 'د.إ', 'THB': '฿'
        }
        if obj.city and obj.city.state and obj.city.state.country:
            currency_code = obj.city.state.country.get_currency()
            symbol = currency_symbols.get(currency_code, currency_code)
            return format_html(
                '<span style="font-weight: 600;">{}</span>',
                symbol
            )
        return obj.currency
    get_currency_display.short_description = 'Currency'
    
    def rating_display(self, obj):
        if obj.rating:
            stars = '⭐' * int(obj.rating)
            rating_str = f'{obj.rating:.1f}'
            return format_html(
                '<div style="line-height: 1.4;"><span style="font-size: 14px;">{}</span><br><span style="color: #6b7280; font-size: 11px;">{} / 5.0</span></div>',
                stars,
                rating_str
            )
        return format_html('<span style="color: #9ca3af;">No rating</span>')
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'
    
    def bookings_display(self, obj):
        from bookings.models import Booking
        count = Booking.objects.filter(playground=obj).count()
        if count > 0:
            plural = 's' if count != 1 else ''
            return format_html(
                '<span style="background: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">{} booking{}</span>',
                count,
                plural
            )
        return format_html('<span style="color: #9ca3af;">0 bookings</span>')
    bookings_display.short_description = 'Bookings'
    
    def quick_actions(self, obj):
        edit_url = reverse('admin:playgrounds_playground_change', args=[obj.pk])
        view_url = f'/playgrounds/{obj.pk}/'
        return format_html(
            '<div style="display: flex; gap: 4px;">'
            '<a href="{}" style="background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 500;">Edit</a>'
            '<a href="{}" target="_blank" style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 500;">View</a>'
            '</div>',
            edit_url,
            view_url
        )
    quick_actions.short_description = 'Actions'
    
    # Admin actions
    def remove_from_popular(self, request, queryset):
        """Remove selected playgrounds from popular section"""
        updated = queryset.update(is_popular=False)
        self.message_user(
            request,
            f'{updated} playground(s) removed from popular section. They will no longer appear on the homepage.',
            messages.SUCCESS
        )
    remove_from_popular.short_description = '❌ Remove from Popular (Homepage)'
    
    def has_add_permission(self, request):
        """Enable custom add view"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Disable delete - use 'Remove from Popular' action instead"""
        return False
    
    class Meta:
        verbose_name = "Popular Playground (Homepage)"
        verbose_name_plural = "Popular Playgrounds (Homepage)"


# Register the PopularPlaygroundAdmin with a proxy model
class PopularPlayground(Playground):
    class Meta:
        proxy = True
        verbose_name = "Popular Playground (Homepage)"
        verbose_name_plural = "⭐ Popular Playgrounds (Homepage)"


admin.site.register(PopularPlayground, PopularPlaygroundAdmin)


# Favorite model removed - Use Playground.is_featured and Playground.is_popular instead
# Admins can mark playgrounds as featured/popular directly in the Playground admin
