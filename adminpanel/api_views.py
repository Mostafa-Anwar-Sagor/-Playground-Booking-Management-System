from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from accounts.models import PartnerApplication, User


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access these views"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'admin'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to access this page.")
        return super().handle_no_permission()


class PartnerApplicationAPIView(AdminRequiredMixin, View):
    """API view for partner applications with real-time data"""
    
    def get(self, request):
        # Get query parameters
        status_filter = request.GET.get('status', '')
        search_query = request.GET.get('search', '')
        country_filter = request.GET.get('country', '')
        date_filter = request.GET.get('date_range', '')
        
        # Base queryset
        applications = PartnerApplication.objects.select_related('user').prefetch_related('images', 'videos').all()
        
        # Apply filters
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        if search_query:
            applications = applications.filter(
                Q(business_name__icontains=search_query) |
                Q(business_email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        if country_filter:
            applications = applications.filter(business_address__icontains=country_filter)
        
        # Date filtering
        if date_filter:
            now = timezone.now()
            if date_filter == 'today':
                applications = applications.filter(created_at__date=now.date())
            elif date_filter == 'week':
                week_ago = now - timedelta(days=7)
                applications = applications.filter(created_at__gte=week_ago)
            elif date_filter == 'month':
                month_ago = now - timedelta(days=30)
                applications = applications.filter(created_at__gte=month_ago)
            elif date_filter == 'quarter':
                quarter_ago = now - timedelta(days=90)
                applications = applications.filter(created_at__gte=quarter_ago)
        
        # Serialize data
        applications_data = []
        for app in applications.order_by('-created_at'):
            applications_data.append({
                'id': app.id,
                'business_name': app.business_name,
                'business_email': app.business_email,
                'business_phone': app.business_phone,
                'business_address': app.business_address,
                'description': app.description,
                'experience_years': app.experience_years,
                'status': app.status,
                'created_at': app.created_at.isoformat(),
                'updated_at': app.updated_at.isoformat(),
                'admin_comments': app.admin_comments or '',
                'owner_name': app.user.get_full_name(),
                'owner_email': app.user.email,
                'owner_phone': getattr(app.user, 'phone_number', '') or '',
                'owner_address': getattr(app.user, 'address', '') or '',
                'business_license': app.business_license.url if app.business_license else None,
                'images': [{'url': img.image.url, 'name': img.image.name} for img in app.images.all()],
                'videos': [{'url': vid.video.url, 'name': vid.video.name} for vid in app.videos.all()],
                'is_suspended': not getattr(app.user, 'is_approved', True),
            })
        
        return JsonResponse({
            'success': True,
            'applications': applications_data,
            'total_count': len(applications_data)
        })


class PartnerApplicationDetailAPIView(AdminRequiredMixin, View):
    """API view for individual partner application details"""
    
    def get(self, request, app_id):
        try:
            app = PartnerApplication.objects.select_related('user').prefetch_related('images', 'videos').get(id=app_id)
        except PartnerApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found.'})
        
        app_data = {
            'id': app.id,
            'business_name': app.business_name,
            'business_email': app.business_email,
            'business_phone': app.business_phone,
            'business_address': app.business_address,
            'description': app.description,
            'experience_years': app.experience_years,
            'status': app.status,
            'created_at': app.created_at.isoformat(),
            'updated_at': app.updated_at.isoformat(),
            'admin_comments': app.admin_comments or '',
            'owner_name': app.user.get_full_name(),
            'owner_email': app.user.email,
            'owner_phone': getattr(app.user, 'phone_number', '') or '',
            'owner_address': getattr(app.user, 'address', '') or '',
            'business_license': app.business_license.url if app.business_license else None,
            'images': [{'url': img.image.url, 'name': img.image.name} for img in app.images.all()],
            'videos': [{'url': vid.video.url, 'name': vid.video.name} for vid in app.videos.all()],
            'is_suspended': not getattr(app.user, 'is_approved', True),
        }
        
        return JsonResponse({
            'success': True,
            'application': app_data
        })


class ActiveOwnersAPIView(AdminRequiredMixin, View):
    """API view for active owners management"""
    
    def get(self, request):
        search_query = request.GET.get('search', '')
        
        # Get approved applications (active owners)
        owners_query = PartnerApplication.objects.filter(status='approved').select_related('user')
        
        if search_query:
            owners_query = owners_query.filter(
                Q(business_name__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        owners_data = []
        for app in owners_query.order_by('-created_at'):
            # Get playground count for this owner
            playground_count = 0
            try:
                from playgrounds.models import Playground
                playground_count = Playground.objects.filter(owner=app.user).count()
            except ImportError:
                pass
            
            # Get booking count for this owner
            booking_count = 0
            try:
                from bookings.models import Booking
                from playgrounds.models import Playground
                owner_playgrounds = Playground.objects.filter(owner=app.user)
                booking_count = Booking.objects.filter(playground__in=owner_playgrounds).count()
            except ImportError:
                pass
            
            owners_data.append({
                'id': app.id,
                'business_name': app.business_name,
                'business_email': app.business_email,
                'business_phone': app.business_phone,
                'owner_name': app.user.get_full_name(),
                'owner_email': app.user.email,
                'owner_phone': getattr(app.user, 'phone_number', '') or '',
                'status': app.status,
                'created_at': app.created_at.isoformat(),
                'playgrounds_count': playground_count,
                'total_bookings': booking_count,
                'is_suspended': not getattr(app.user, 'is_approved', True),
            })
        
        return JsonResponse({
            'success': True,
            'owners': owners_data,
            'total_count': len(owners_data)
        })


class AnalyticsAPIView(AdminRequiredMixin, View):
    """API view for analytics and reporting"""
    
    def get(self, request):
        # Get statistics
        total_applications = PartnerApplication.objects.count()
        pending_applications = PartnerApplication.objects.filter(status='pending').count()
        approved_applications = PartnerApplication.objects.filter(status='approved').count()
        rejected_applications = PartnerApplication.objects.filter(status='rejected').count()
        
        # Get monthly trends (last 6 months)
        now = timezone.now()
        monthly_data = []
        months = []
        
        for i in range(6):
            month_start = now.replace(day=1) - timedelta(days=30 * i)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end - timedelta(days=month_end.day)
            
            month_applications = PartnerApplication.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            months.insert(0, month_start.strftime('%b'))
            monthly_data.insert(0, month_applications)
        
        # Get country distribution
        country_data = {}
        applications = PartnerApplication.objects.all()
        
        for app in applications:
            # Extract country from address (simple approach)
            address = app.business_address.lower()
            if 'bangladesh' in address or 'dhaka' in address:
                country = 'Bangladesh'
            elif 'india' in address:
                country = 'India'
            elif 'pakistan' in address:
                country = 'Pakistan'
            elif 'usa' in address or 'america' in address:
                country = 'USA'
            elif 'uk' in address or 'britain' in address:
                country = 'UK'
            else:
                country = 'Other'
            
            country_data[country] = country_data.get(country, 0) + 1
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total': total_applications,
                'pending': pending_applications,
                'approved': approved_applications,
                'rejected': rejected_applications
            },
            'monthly_trends': {
                'labels': months,
                'data': monthly_data
            },
            'status_distribution': {
                'labels': ['Pending', 'Approved', 'Rejected'],
                'data': [pending_applications, approved_applications, rejected_applications]
            },
            'country_distribution': country_data
        })


class OwnerUpdateAPIView(AdminRequiredMixin, View):
    """API view for updating owner information"""
    
    def post(self, request, owner_id):
        try:
            # Get the partner application
            application = PartnerApplication.objects.get(id=owner_id, status='approved')
            
            # Parse the request data
            data = json.loads(request.body)
            
            # Update application fields
            application.business_name = data.get('business_name', application.business_name)
            application.business_phone = data.get('phone', application.business_phone)
            application.business_address = data.get('address', application.business_address)
            application.description = data.get('description', application.description)
            
            # Update user fields if contact_person is provided
            if 'contact_person' in data and data['contact_person']:
                user = application.user
                name_parts = data['contact_person'].strip().split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                else:
                    user.last_name = ''
                
                # Update phone and address if provided
                if 'phone' in data:
                    user.phone_number = data['phone']
                if 'address' in data:
                    user.address = data['address']
                
                user.save()
            
            application.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Owner information updated successfully',
                'owner': {
                    'id': application.id,
                    'business_name': application.business_name,
                    'contact_person': f"{application.user.first_name} {application.user.last_name}".strip(),
                    'phone': application.business_phone,
                    'address': application.business_address,
                    'description': application.description,
                }
            })
            
        except PartnerApplication.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Owner not found or not approved'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating owner: {str(e)}'
            }, status=500)


# ===== NEW COMPREHENSIVE ADMIN API ENDPOINTS =====
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Avg
from django.shortcuts import get_object_or_404

from playgrounds.models import Playground
from bookings.models import Booking


def admin_required(view_func):
    """Decorator to ensure only admin users can access"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'admin':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def admin_stats_api(request):
    """Get comprehensive admin dashboard statistics"""
    today = timezone.now().date()
    this_month_start = timezone.now().replace(day=1).date()
    
    total_users = User.objects.count()
    new_users_this_month = User.objects.filter(date_joined__gte=this_month_start).count()
    total_owners = User.objects.filter(user_type='owner').count()
    total_customers = User.objects.filter(user_type='customer').count()
    
    total_playgrounds = Playground.objects.count()
    active_playgrounds = Playground.objects.filter(status='active').count()
    
    all_bookings = Booking.objects.all()
    total_bookings = all_bookings.count()
    today_bookings = all_bookings.filter(created_at__date=today).count()
    confirmed_bookings = all_bookings.filter(status='confirmed').count()
    pending_bookings = all_bookings.filter(status='pending').count()
    
    paid_bookings = all_bookings.filter(payment_status='paid')
    pending_payments = all_bookings.filter(
        payment_receipt__isnull=False,
        receipt_verified=False
    ).count()
    
    total_revenue = paid_bookings.aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    this_month_revenue = paid_bookings.filter(
        created_at__gte=this_month_start
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    
    last_month_start = (timezone.now().replace(day=1) - timedelta(days=1)).replace(day=1).date()
    last_month_revenue = paid_bookings.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    
    revenue_growth = 0
    if last_month_revenue > 0:
        revenue_growth = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    pending_applications = PartnerApplication.objects.filter(status='pending').count()
    
    return JsonResponse({
        'users': {
            'total': total_users,
            'new_this_month': new_users_this_month,
            'owners': total_owners,
            'customers': total_customers
        },
        'playgrounds': {
            'total': total_playgrounds,
            'active': active_playgrounds,
            'pending': total_playgrounds - active_playgrounds
        },
        'bookings': {
            'total': total_bookings,
            'today': today_bookings,
            'confirmed': confirmed_bookings,
            'pending': pending_bookings
        },
        'payments': {
            'pending_verification': pending_payments,
            'total_revenue': float(total_revenue),
            'this_month_revenue': float(this_month_revenue),
            'revenue_growth': round(revenue_growth, 2)
        },
        'applications': {
            'pending': pending_applications
        }
    })


@login_required
@admin_required
def admin_users_list_api(request):
    """Get all users with pagination"""
    users = User.objects.all().order_by('-date_joined')
    
    user_type = request.GET.get('type')
    search = request.GET.get('search', '')
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users_data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.get_full_name(),
        'user_type': user.user_type,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    } for user in users[:100]]
    
    return JsonResponse({'users': users_data, 'count': users.count()})


@login_required
@admin_required
def admin_bookings_list_api(request):
    """Get all bookings for admin management"""
    bookings = Booking.objects.select_related('user', 'playground', 'verified_by').all()
    
    status = request.GET.get('status')
    payment_status = request.GET.get('payment_status')
    
    if status:
        bookings = bookings.filter(status=status)
    
    if payment_status:
        bookings = bookings.filter(payment_status=payment_status)
    
    bookings_data = [{
        'id': booking.id,
        'booking_id': str(booking.booking_id)[:8],
        'user': booking.user.username,
        'playground': booking.playground.name,
        'date': booking.booking_date.strftime('%Y-%m-%d'),
        'time': f"{booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}",
        'status': booking.status,
        'payment_status': booking.payment_status,
        'amount': float(booking.final_amount),
        'has_receipt': bool(booking.payment_receipt),
        'receipt_verified': booking.receipt_verified,
        'verified_by': booking.verified_by.username if booking.verified_by else None
    } for booking in bookings.order_by('-created_at')[:100]]
    
    return JsonResponse({'bookings': bookings_data, 'count': bookings.count()})


@login_required
@admin_required
def admin_playgrounds_list_api(request):
    """Get all playgrounds for admin management"""
    playgrounds = Playground.objects.select_related('owner', 'city').all()
    
    status_filter = request.GET.get('status')
    
    if status_filter:
        playgrounds = playgrounds.filter(status=status_filter)
    
    playgrounds_data = [{
        'id': pg.id,
        'name': pg.name,
        'owner': pg.owner.username,
        'city': pg.city.name if pg.city else 'N/A',
        'status': pg.status,
        'is_active': pg.status == 'active',
        'price': float(pg.price_per_hour),
        'bookings': pg.bookings.count()
    } for pg in playgrounds.order_by('-id')[:100]]
    
    return JsonResponse({'playgrounds': playgrounds_data, 'count': playgrounds.count()})


@login_required
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_verify_payment_api(request):
    """Admin verify payment receipt"""
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        action = data.get('action')
        
        booking = get_object_or_404(Booking, id=booking_id)
        
        if action == 'verify':
            booking.receipt_verified = True
            booking.payment_status = 'paid'
            booking.verified_by = request.user
            booking.verified_at = timezone.now()
            booking.save()
            return JsonResponse({'success': True, 'message': 'Payment verified'})
        
        elif action == 'reject':
            booking.receipt_verified = False
            booking.payment_status = 'pending'
            booking.verified_by = None
            booking.verified_at = None
            booking.save()
            return JsonResponse({'success': True, 'message': 'Payment rejected'})
        
        return JsonResponse({'error': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@admin_required
def admin_pending_payments_api(request):
    """Get all pending payment verifications"""
    pending = Booking.objects.filter(
        payment_receipt__isnull=False,
        receipt_verified=False
    ).select_related('user', 'playground').order_by('-created_at')
    
    payments_data = [{
        'id': booking.id,
        'booking_id': str(booking.booking_id)[:8],
        'user': booking.user.username,
        'playground': booking.playground.name,
        'date': booking.booking_date.strftime('%Y-%m-%d'),
        'amount': float(booking.final_amount),
        'receipt_url': booking.payment_receipt.url if booking.payment_receipt else None
    } for booking in pending]
    
    return JsonResponse({
        'payments': payments_data,
        'count': len(payments_data),
        'total_amount': sum(p['amount'] for p in payments_data)
    })


@login_required
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_manage_user_api(request):
    """Admin manage user"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')
        
        user = get_object_or_404(User, id=user_id)
        
        if action == 'activate':
            user.is_active = True
            user.save()
            return JsonResponse({'success': True, 'message': f'{user.username} activated'})
        
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            return JsonResponse({'success': True, 'message': f'{user.username} deactivated'})
        
        elif action == 'change_type':
            new_type = data.get('user_type')
            if new_type in ['customer', 'owner', 'admin']:
                user.user_type = new_type
                user.save()
                return JsonResponse({'success': True, 'message': f'Type changed to {new_type}'})
        
        return JsonResponse({'error': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def admin_manage_playground_api(request):
    """Admin manage playground"""
    try:
        data = json.loads(request.body)
        playground_id = data.get('playground_id')
        action = data.get('action')
        
        playground = get_object_or_404(Playground, id=playground_id)
        
        if action == 'activate':
            playground.status = 'active'
            playground.save()
            return JsonResponse({'success': True, 'message': f'{playground.name} activated'})
        
        elif action == 'deactivate':
            playground.status = 'inactive'
            playground.save()
            return JsonResponse({'success': True, 'message': f'{playground.name} deactivated'})
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

