from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import User, UserProfile, PartnerApplication, PlaygroundApplication, PlaygroundApplicationImage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'user_type', 'bookings_count', 'is_verified', 'is_approved', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_approved', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'profile_picture')}),
        ('Location', {'fields': ('city',)}),
        ('Account Type', {'fields': ('user_type',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('is_verified', 'is_approved')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'email', 'first_name', 'last_name')
        }),
    )
    
    def full_name(self, obj):
        """Display full name"""
        return obj.get_full_name() or obj.username
    full_name.short_description = 'Name'
    full_name.admin_order_field = 'first_name'
    
    def bookings_count(self, obj):
        """Display booking count with link to bookings"""
        from bookings.models import Booking
        count = Booking.objects.filter(user=obj).count()
        if count > 0:
            url = reverse('admin:bookings_booking_changelist') + f'?user__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #2e7d32; font-weight: bold;">{} booking{}</a>',
                url,
                count,
                's' if count != 1 else ''
            )
        return '0 bookings'
    bookings_count.short_description = 'Bookings'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('city')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'emergency_contact', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio')
    list_filter = ('created_at',)


@admin.register(PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'status', 'get_playgrounds_count', 'created_at', 'approved_by')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'business_name', 'business_email')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_playgrounds_count(self, obj):
        """Show how many playgrounds this partner has registered"""
        from playgrounds.models import Playground
        count = Playground.objects.filter(owner=obj.user).count()
        return f"{count} playgrounds"
    get_playgrounds_count.short_description = 'Registered Playgrounds'
    
    fieldsets = (
        ('Applicant Info', {
            'fields': ('user', 'status', 'approved_by')
        }),
        ('Business Details', {
            'fields': ('business_name', 'business_address', 'business_phone', 'business_email', 'business_license')
        }),
        ('Additional Info', {
            'fields': ('description', 'experience_years', 'admin_comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_applications', 'reject_applications']
    
    def approve_applications(self, request, queryset):
        """Approve partner applications and their pending playgrounds"""
        for application in queryset:
            application.status = 'approved'
            application.approved_by = request.user
            application.save()
            
            # Change user type to owner
            application.user.user_type = 'owner'
            application.user.is_approved = True
            application.user.save()
            
            # Auto-approve all pending playgrounds for this partner
            from playgrounds.models import Playground
            pending_playgrounds = Playground.objects.filter(
                owner=application.user, 
                status='pending'
            )
            approved_count = pending_playgrounds.update(status='active', is_verified=True)
            
            # Send success message
            self.message_user(request, 
                f"✅ {application.business_name} approved! "
                f"User promoted to partner and {approved_count} playgrounds activated."
            )
        
        self.message_user(request, f"🎉 {queryset.count()} partner applications approved successfully!")
    
    def reject_applications(self, request, queryset):
        """Reject partner applications and their playgrounds"""
        for application in queryset:
            # Reject associated playgrounds
            from playgrounds.models import Playground
            rejected_playgrounds = Playground.objects.filter(
                owner=application.user,
                status='pending'
            ).update(status='inactive')
            
            application.status = 'rejected'
            application.save()
            
            self.message_user(request, 
                f"❌ {application.business_name} rejected. "
                f"{rejected_playgrounds} playgrounds deactivated."
            )
        self.message_user(request, f"{queryset.count()} applications rejected.")
    
    approve_applications.short_description = "Approve selected applications"
    reject_applications.short_description = "Reject selected applications"


class PlaygroundApplicationImageInline(admin.TabularInline):
    model = PlaygroundApplicationImage
    extra = 0
    readonly_fields = ('uploaded_at',)


@admin.register(PlaygroundApplication)
class PlaygroundApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'city', 'playground_type', 'price_per_hour', 'status', 'created_at', 'approved_by')
    list_filter = ('status', 'playground_type', 'created_at', 'updated_at', 'city__state__country')
    search_fields = ('name', 'user__email', 'user__first_name', 'user__last_name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at', 'created_playground')
    inlines = [PlaygroundApplicationImageInline]
    
    fieldsets = (
        ('Application Info', {
            'fields': ('user', 'status', 'approved_by', 'created_playground')
        }),
        ('Playground Details', {
            'fields': ('name', 'description', 'playground_type', 'capacity', 'size', 'price_per_hour')
        }),
        ('Location', {
            'fields': ('city', 'address')
        }),
        ('Additional Info', {
            'fields': ('sport_types', 'rules', 'admin_comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_playground_applications', 'reject_playground_applications']
    
    def approve_playground_applications(self, request, queryset):
        """Approve playground applications and create actual playgrounds"""
        approved_count = 0
        created_count = 0
        error_count = 0
        
        for application in queryset.filter(status='pending'):
            try:
                # Approve the application (this triggers automatic playground creation)
                application.status = 'approved'
                application.approved_by = request.user
                application.save()  # This should trigger automatic playground creation
                
                # Verify playground was created automatically
                application.refresh_from_db()
                if application.created_playground:
                    approved_count += 1
                    created_count += 1
                    self.message_user(request, 
                        f"✅ '{application.name}' approved! Playground auto-created (ID: {application.created_playground.id})"
                    )
                else:
                    # Manual fallback creation if automatic failed
                    playground = self._manual_create_playground(application)
                    
                    application.created_playground = playground
                    application.save(update_fields=['created_playground'])
                    
                    approved_count += 1
                    created_count += 1
                    self.message_user(request, 
                        f"✅ '{application.name}' approved! Playground manually created (ID: {playground.id})"
                    )
                
            except Exception as e:
                error_count += 1
                self.message_user(request, 
                    f"❌ Error approving '{application.name}': {str(e)}", 
                    level='ERROR'
                )
        
        if approved_count > 0:
            self.message_user(request, f"🎉 {approved_count} applications approved, {created_count} playgrounds created!")
        if error_count > 0:
            self.message_user(request, f"⚠️ {error_count} applications had errors", level='WARNING')
        if approved_count == 0 and error_count == 0:
            self.message_user(request, "No pending applications to approve.")
    
    def _manual_create_playground(self, application):
        """Manual playground creation fallback"""
        from playgrounds.models import Playground, SportType, PlaygroundImage
        
        playground = Playground.objects.create(
            owner=application.user,
            name=application.name,
            description=application.description or '',
            city=application.city,
            address=application.address,
            playground_type=application.playground_type,
            capacity=application.capacity,
            size=application.size or '',
            price_per_hour=application.price_per_hour,
            status='active',
            rules=application.rules or '',
        )
        
        # Add sport types
        if application.sport_types:
            for sport in [s.strip() for s in application.sport_types.split(',') if s.strip()]:
                st, _ = SportType.objects.get_or_create(name=sport)
                playground.sport_types.add(st)
        
        # Copy images from application to playground
        for img in application.images.all():
            PlaygroundImage.objects.create(
                playground=playground,
                image=img.image
            )
        
        # Send notification
        try:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=application.user,
                title='Playground Approved!',
                message=f'Your playground "{application.name}" has been approved and is now active.',
                notification_type='playground_approved'
            )
        except Exception:
            pass
            
        return playground
    
    def reject_playground_applications(self, request, queryset):
        """Reject playground applications"""
        rejected_count = queryset.filter(status='pending').update(status='rejected')
        
        if rejected_count > 0:
            self.message_user(request, f"❌ {rejected_count} playground applications rejected.")
        else:
            self.message_user(request, "No pending applications to reject.")
    
    approve_playground_applications.short_description = "Approve selected playground applications"
    reject_playground_applications.short_description = "Reject selected playground applications"
