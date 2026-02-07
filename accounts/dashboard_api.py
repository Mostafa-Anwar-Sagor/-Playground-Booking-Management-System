from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from bookings.models import Booking
from playgrounds.models import Playground
from accounts.models import User

# Try to import notifications model
try:
    from notifications.models import Notification
except ImportError:
    Notification = None


@login_required
@require_http_methods(["GET"])
def dashboard_data_api(request):
    """API endpoint for dynamic dashboard data"""
    user = request.user
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Get user bookings
    user_bookings = Booking.objects.filter(user=user)
    
    # Calculate statistics
    total_bookings = user_bookings.count()
    last_week_bookings = user_bookings.filter(created_at__gte=last_week).count()
    booking_change = ((last_week_bookings - (total_bookings - last_week_bookings)) / max(1, total_bookings - last_week_bookings)) * 100 if total_bookings > last_week_bookings else 0
    
    total_hours = user_bookings.aggregate(total=Sum('duration_hours'))['total'] or 0
    last_month_hours = user_bookings.filter(created_at__gte=last_month).aggregate(total=Sum('duration_hours'))['total'] or 0
    hours_change = ((last_month_hours - (total_hours - last_month_hours)) / max(1, total_hours - last_month_hours)) * 100 if total_hours > last_month_hours else 0
    
    total_spent = user_bookings.filter(payment_status='paid').aggregate(total=Sum('final_amount'))['total'] or 0
    month_spent = user_bookings.filter(payment_status='paid', created_at__gte=last_month).aggregate(total=Sum('final_amount'))['total'] or 0
    
    # Get favorite sport
    favorite_sport_data = user_bookings.values('playground__sport_types__name').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    favorite_sport = favorite_sport_data['playground__sport_types__name'] if favorite_sport_data and favorite_sport_data['playground__sport_types__name'] else 'None'
    sport_percentage = (favorite_sport_data['count'] / max(1, total_bookings)) * 100 if favorite_sport_data else 0
    
    # Check if requesting all bookings
    all_bookings_param = request.GET.get('all', 'false').lower() == 'true'
    
    if all_bookings_param:
        # Get ALL bookings for bookings page
        all_bookings_list = user_bookings.select_related('playground').order_by('-booking_date', '-start_time')
    else:
        # Get upcoming bookings for dashboard
        all_bookings_list = user_bookings.filter(
            booking_date__gte=today,
            status__in=['pending', 'confirmed']
        ).select_related('playground').order_by('booking_date', 'start_time')[:5]
    
    # Get nearby playgrounds
    nearby_playgrounds = Playground.objects.filter(
        status='active'
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).select_related('city').prefetch_related('sport_types', 'images')[:6]
    
    # Get sports preferences
    sports_data = user_bookings.values('playground__sport_types__name').annotate(
        count=Count('id')
    ).exclude(playground__sport_types__name__isnull=True).order_by('-count')
    
    total_sport_bookings = sum(sport['count'] for sport in sports_data)
    sports_preferences = [
        {
            'name': sport['playground__sport_types__name'] or 'Other',
            'percentage': round((sport['count'] / max(1, total_sport_bookings)) * 100, 1)
        }
        for sport in sports_data[:5] if sport['playground__sport_types__name']
    ]
    
    # If no sports data, add a default entry
    if not sports_preferences:
        sports_preferences = [{'name': 'No Data', 'percentage': 100}]
    
    return JsonResponse({
        'success': True,
        'data': {
            'total_bookings': total_bookings,
            'booking_change': round(booking_change, 1),
            'total_hours': float(total_hours),
            'hours_change': round(hours_change, 1),
            'favorite_sport': favorite_sport,
            'sport_percentage': round(sport_percentage, 1),
            'total_spent': float(total_spent),
            'month_spent': float(month_spent)
        },
        'bookings': [
            {
                'id': booking.id,
                'booking_id': str(booking.booking_id) if hasattr(booking, 'booking_id') else str(booking.id),
                'playground_name': booking.playground.name,
                'playground_id': booking.playground.id,
                'playground_address': booking.playground.address if hasattr(booking.playground, 'address') else '',
                'playground_image': booking.playground.images.first().image.url if booking.playground.images.exists() else None,
                'sport': ', '.join([st.name for st in booking.playground.sport_types.all()]) or 'Various Sports',
                'date': booking.booking_date.strftime('%b %d, %Y'),
                'date_raw': booking.booking_date.strftime('%Y-%m-%d'),
                'time': f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}",
                'start_time': booking.start_time.strftime('%I:%M %p'),
                'end_time': booking.end_time.strftime('%I:%M %p'),
                'duration': f"{booking.duration_hours} hour{'s' if booking.duration_hours != 1 else ''}" if hasattr(booking, 'duration_hours') else '2 hours',
                'status': booking.status.title(),
                'status_raw': booking.status,
                'amount': float(booking.final_amount),
                'payment_status': booking.payment_status if hasattr(booking, 'payment_status') else 'pending',
                'has_receipt': bool(booking.payment_receipt) if hasattr(booking, 'payment_receipt') else False,
                'receipt_verified': booking.receipt_verified if hasattr(booking, 'receipt_verified') else False,
                'verified_by_admin': booking.verified_by.username if hasattr(booking, 'verified_by') and booking.verified_by else None,
                'verified_at': booking.verified_at.strftime('%b %d, %Y at %I:%M %p') if hasattr(booking, 'verified_at') and booking.verified_at else None,
                'number_of_players': booking.number_of_players if hasattr(booking, 'number_of_players') else 0,
                'special_requests': booking.special_requests if hasattr(booking, 'special_requests') else '',
                'created_at': booking.created_at.strftime('%b %d, %Y at %I:%M %p') if hasattr(booking, 'created_at') and booking.created_at else None
            }
            for booking in all_bookings_list
        ],
        'playgrounds': [
            {
                'id': playground.id,
                'name': playground.name,
                'sport': ', '.join([st.name for st in playground.sport_types.all()]) or 'Various Sports',
                'distance': round(2.5, 1),  # You can implement actual distance calculation
                'rating': round(playground.avg_rating or 4.0, 1),
                'reviews': playground.review_count or 0,
                'image': playground.images.first().image.url if playground.images.exists() else None
            }
            for playground in nearby_playgrounds
        ],
        'sports_preferences': sports_preferences
    })


@login_required
@require_http_methods(["GET"])
def dashboard_activity_api(request, days):
    """API endpoint for activity chart data"""
    user = request.user
    days = int(days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Generate date range
    date_range = [start_date + timedelta(days=x) for x in range(days)]
    
    # Get booking counts per day
    bookings_by_day = {}
    user_bookings = Booking.objects.filter(
        user=user,
        created_at__date__range=[start_date, end_date]
    ).values('created_at__date').annotate(count=Count('id'))
    
    for booking in user_bookings:
        bookings_by_day[booking['created_at__date']] = booking['count']
    
    # Format data for chart
    labels = []
    values = []
    
    for date in date_range:
        if days <= 7:
            labels.append(date.strftime('%a'))
        elif days <= 30:
            labels.append(date.strftime('%m/%d'))
        else:
            labels.append(date.strftime('%b %d'))
        
        values.append(bookings_by_day.get(date, 0))
    
    return JsonResponse({
        'success': True,
        'labels': labels,
        'values': values
    })


@login_required
@require_http_methods(["GET"])
def dashboard_notifications_api(request):
    """API endpoint for user notifications"""
    user = request.user
    
    # Get recent notifications (you might have a notifications model)
    notifications = []
    
    # Check for upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        user=user,
        booking_date=timezone.now().date() + timedelta(days=1),
        status='confirmed'
    ).count()
    
    if upcoming_bookings > 0:
        notifications.append({
            'type': 'info',
            'message': f'You have {upcoming_bookings} booking(s) tomorrow',
            'time': 'now'
        })
    
    # Check for pending payments
    pending_payments = Booking.objects.filter(
        user=user,
        payment_status='pending',
        status='confirmed'
    ).count()
    
    if pending_payments > 0:
        notifications.append({
            'type': 'warning',
            'message': f'{pending_payments} booking(s) require payment',
            'time': 'now'
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notifications[:10]  # Limit to 10 notifications
    })


@login_required
@require_http_methods(["GET"])
def user_stats_api(request):
    """API endpoint for navbar user statistics"""
    try:
        user = request.user
        today = timezone.now().date()
        
        # Get bookings count
        bookings_count = Booking.objects.filter(
            user=user,
            booking_date__gte=today,
            status__in=['pending', 'confirmed']
        ).count()
        
        # Get notifications count (if notifications app is available)
        notifications_count = 0
        if Notification:
            try:
                notifications_count = Notification.objects.filter(
                    user=user,
                    is_read=False
                ).count()
            except Exception:
                pass
        
        # Get messages count (placeholder - implement based on your messaging system)
        messages_count = 0
        
        # Return stats
        return JsonResponse({
            'success': True,
            'stats': {
                'bookings': bookings_count,
                'notifications': notifications_count,
                'messages': messages_count
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'stats': {
                'bookings': 0,
                'notifications': 0,
                'messages': 0
            }
        }, status=200)  # Return 200 to prevent frontend errors
