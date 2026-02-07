
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from accounts.models import PartnerApplication
from bookings.models import Booking

# Create your views here.

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access these views"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'admin'
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to access this page.")
        return super().handle_no_permission()

class PartnerApplicationListView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/partner_applications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_applications = PartnerApplication.objects.select_related('user').prefetch_related('images', 'videos').all().order_by('-created_at')
        context['all_partner_applications'] = all_applications
        
        # Add statistics
        context['pending_count'] = all_applications.filter(status='pending').count()
        context['approved_count'] = all_applications.filter(status='approved').count()
        context['rejected_count'] = all_applications.filter(status='rejected').count()
        context['total_count'] = all_applications.count()
        
        # Add approved owners with additional statistics
        approved_applications = all_applications.filter(status='approved')
        context['active_owners'] = approved_applications
        
        return context

    def post(self, request, *args, **kwargs):
        from django.http import JsonResponse
        from django.contrib import messages
        import json
        
        app_id = request.POST.get('application_id')
        action = request.POST.get('action')
        
        if not app_id:
            return JsonResponse({'success': False, 'message': 'Invalid request - missing application ID.'})
            
        try:
            app = PartnerApplication.objects.select_related('user').get(id=app_id)
        except PartnerApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found.'})
        
        if action == 'approve':
            if app.status != 'pending':
                return JsonResponse({'success': False, 'message': 'Only pending applications can be approved.'})
            
            # Update application status
            app.status = 'approved'
            app.approved_by = request.user
            app.save(update_fields=['status', 'approved_by'])
            
            # Promote user to owner - they'll have both user and owner capabilities
            app.user.user_type = 'owner'
            app.user.is_approved = True
            app.user.save(update_fields=['user_type', 'is_approved'])
            
            # Create notification for the user
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=app.user,
                    title='🎉 Partner Application Approved!',
                    message=f'Congratulations! Your partner application for "{app.business_name}" has been approved. You now have access to the owner dashboard and can manage playgrounds.',
                    notification_type='partner_approved'
                )
            except ImportError:
                pass  # Notifications not available
            
            return JsonResponse({
                'success': True, 
                'message': f'🎉 Application approved successfully! {app.user.get_full_name() or app.user.email} is now a verified partner/owner with full access to the owner dashboard.',
                'new_status': 'approved'
            })
            
        elif action == 'reject':
            if app.status != 'pending':
                return JsonResponse({'success': False, 'message': 'Only pending applications can be rejected.'})
            
            app.status = 'rejected'
            app.save(update_fields=['status'])
            
            # Create notification for the user
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=app.user,
                    title='❌ Partner Application Rejected',
                    message=f'Unfortunately, your partner application for "{app.business_name}" has been rejected. Please check the admin comments for more details or contact support for clarification.',
                    notification_type='partner_rejected'
                )
            except ImportError:
                pass  # Notifications not available
            
            return JsonResponse({
                'success': True, 
                'message': f'Application rejected. User has been notified with detailed feedback.',
                'new_status': 'rejected'
            })
            
        elif action == 'update_comments':
            comments = request.POST.get('comments', '').strip()
            app.admin_comments = comments
            app.save(update_fields=['admin_comments'])
            return JsonResponse({'success': True, 'message': 'Admin comments updated successfully.'})
            
        elif action == 'suspend_owner':
            if app.status == 'approved':
                app.user.is_approved = False
                app.user.save(update_fields=['is_approved'])
                return JsonResponse({'success': True, 'message': f'{app.business_name} has been suspended.'})
            else:
                return JsonResponse({'success': False, 'message': 'Can only suspend approved owners.'})
        
        elif action == 'reactivate_owner':
            if app.status == 'approved':
                app.user.is_approved = True
                app.user.save(update_fields=['is_approved'])
                return JsonResponse({'success': True, 'message': f'{app.business_name} has been reactivated.'})
            else:
                return JsonResponse({'success': False, 'message': 'Can only reactivate approved owners.'})
            
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action.'})
        
        return JsonResponse({'success': False, 'message': 'Unknown error occurred.'})

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Comprehensive Admin Dashboard - Single unified panel"""
    template_name = 'dashboard/admin_panel_full.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Admin Panel'
        return context

class UserManagementView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/users.html'

class PlaygroundManagementView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/playgrounds.html'

class BookingManagementView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/bookings.html'

class AnalyticsView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/analytics.html'

class PlatformSettingsView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/settings.html'

class PartnerApplicationManagementView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show pending applications for approval/reject
        context['partner_applications'] = PartnerApplication.objects.select_related('user').filter(status='pending').order_by('-created_at')
        # Debug: show all applications for troubleshooting
        context['all_partner_applications'] = PartnerApplication.objects.all().order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        from django.http import JsonResponse
        app_id = request.POST.get('application_id')
        action = request.POST.get('action')
        if not app_id or action not in ['approve', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid request.'})
        try:
            app = PartnerApplication.objects.select_related('user').get(id=app_id)
        except PartnerApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found.'})
        if action == 'approve':
            app.status = 'approved'
            app.approved_by = request.user
            app.save()
            app.user.user_type = 'owner'
            app.user.save()
            return JsonResponse({'success': True, 'message': 'Application approved and user promoted to owner.'})
        elif action == 'reject':
            app.status = 'rejected'
            app.save()
            return JsonResponse({'success': True, 'message': 'Application rejected.'})
        
        return JsonResponse({'success': False, 'message': 'Invalid action.'})


class PaymentVerificationView(AdminRequiredMixin, TemplateView):
    """Admin view for payment verification management"""
    template_name = 'admin/payment_verification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all bookings with payment receipts pending verification
        pending_payments = Booking.objects.filter(
            payment_receipt__isnull=False,
            receipt_verified=False
        ).select_related('user', 'playground', 'playground__owner').order_by('-created_at')
        
        # Get verified payments for reference
        verified_payments = Booking.objects.filter(
            receipt_verified=True
        ).select_related('user', 'playground', 'verified_by').order_by('-verified_at')[:20]
        
        context['pending_payments'] = pending_payments
        context['verified_payments'] = verified_payments
        context['pending_count'] = pending_payments.count()
        context['total_revenue_pending'] = sum(booking.final_amount for booking in pending_payments)
        
        return context
    
    def post(self, request, *args, **kwargs):
        from django.http import JsonResponse
        import json
        
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            action = data.get('action')  # 'verify' or 'reject'
            
            booking = Booking.objects.get(id=booking_id)
            
            if action == 'verify':
                booking.receipt_verified = True
                booking.payment_status = 'paid'
                booking.verified_by = request.user
                booking.verified_at = timezone.now()
                booking.save()
                return JsonResponse({'success': True, 'message': 'Payment verified successfully.'})
            
            elif action == 'reject':
                booking.receipt_verified = False
                booking.payment_status = 'pending'
                booking.verified_by = None
                booking.verified_at = None
                booking.save()
                return JsonResponse({'success': True, 'message': 'Payment rejected successfully.'})
            
            return JsonResponse({'success': False, 'message': 'Invalid action.'})
            
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Booking not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            return JsonResponse({'success': True, 'message': 'Application rejected.'})
