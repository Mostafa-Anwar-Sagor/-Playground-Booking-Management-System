from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
import json

from bookings.models import Booking
from playgrounds.models import Playground
from notifications.models import Notification
from accounts.models import User

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_data(request):
    """
    Get dashboard data for the current user
    """
    try:
        # For testing - get first user or create sample data
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        if not user:
            # Return sample data if no users exist
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_bookings': 0,
                    'booking_change': 0,
                    'total_hours': 0,
                    'hours_change': 0,
                    'favorite_sport': 'None',
                    'sport_percentage': 0,
                    'total_spent': 0,
                    'month_spent': 0
                },
                'upcoming_bookings': [],
                'nearby_playgrounds': [],
                'sports_data': [],
                'user': {
                    'name': 'Guest User',
                    'email': 'guest@example.com'
                }
            })
            
        now = timezone.now()
        
        # Get user bookings
        user_bookings = Booking.objects.filter(user=user)
        
        # Calculate stats
        total_bookings = user_bookings.count()
        
        # Bookings this week
        week_start = now - timedelta(days=7)
        bookings_this_week = user_bookings.filter(created_at__gte=week_start).count()
        
        # Calculate total hours played
        completed_bookings = user_bookings.filter(status='completed')
        total_hours = completed_bookings.count()  # Assuming 1 hour per booking
        
        # Hours this month
        month_start = now.replace(day=1)
        hours_this_month = completed_bookings.filter(created_at__gte=month_start).count()
        
        # Favorite sport (most booked sport type)
        favorite_sport = "None"
        # Get favorite sport (simplified for now)
        favorite_sport = 'Football'  # Default
        sport_count = total_bookings
        
        # Calculate percentage of favorite sport
        sport_percentage = 100 if total_bookings > 0 else 0
        
        # Calculate total spent
        total_spent = user_bookings.filter(
            status__in=['completed', 'confirmed']
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # This month spending
        month_spent = user_bookings.filter(
            status__in=['completed', 'confirmed'],
            created_at__gte=month_start
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Get upcoming bookings
        upcoming_bookings = user_bookings.filter(
            status__in=['pending', 'confirmed'],
            booking_date__gte=now.date()
        ).order_by('booking_date', 'start_time')[:5]
        
        upcoming_bookings_data = []
        for booking in upcoming_bookings:
            upcoming_bookings_data.append({
                'id': booking.id,
                'playground_name': booking.playground.name if booking.playground else 'Unknown',
                'sport_type': booking.playground.get_sport_types_display() if booking.playground else 'Unknown',
                'date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else '',
                'time': f"{booking.start_time}-{booking.end_time}" if booking.start_time and booking.end_time else 'TBD',
                'status': booking.status,
                'amount': float(booking.total_amount) if booking.total_amount else 0
            })
        
        # Get nearby playgrounds (simplified - just get recent ones)
        nearby_playgrounds = Playground.objects.filter(status='active')[:6]
        
        playgrounds_data = []
        for playground in nearby_playgrounds:
            playgrounds_data.append({
                'id': playground.id,
                'name': playground.name,
                'sport_type': playground.get_sport_types_display(),
                'location': f"{playground.city.name}, {playground.city.state.name}" if playground.city else 'Location TBD',
                'rating': 4.5,  # Default rating for now
                'price_per_hour': float(playground.price_per_hour) if playground.price_per_hour else 0,
                'image_url': playground.images.first().image.url if playground.images.exists() else '/static/images/default-playground.jpg'
            })
        
        # Sports distribution data (simplified)
        sports_data = [
            {'sport': 'Football', 'bookings': 15, 'percentage': 60},
            {'sport': 'Basketball', 'bookings': 8, 'percentage': 32},
            {'sport': 'Tennis', 'bookings': 2, 'percentage': 8}
        ]
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_bookings': total_bookings,
                'booking_change': bookings_this_week,
                'total_hours': total_hours,
                'hours_change': hours_this_month,
                'favorite_sport': favorite_sport,
                'sport_percentage': round(sport_percentage, 1),
                'total_spent': float(total_spent),
                'month_spent': float(month_spent)
            },
            'upcoming_bookings': upcoming_bookings_data,
            'nearby_playgrounds': playgrounds_data,
            'sports_data': sports_data,
            'user': {
                'name': user.get_full_name() or user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt 
@require_http_methods(["GET"])
def dashboard_activity(request, days=7):
    """
    Get activity data for charts
    """
    try:
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        if not user:
            # Return sample data
            activity_data = []
            for i in range(int(days)):
                date = timezone.now() - timedelta(days=int(days)-i-1)
                activity_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'bookings': 0,
                    'day': date.strftime('%a')
                })
            
            return JsonResponse({
                'success': True,
                'activity_data': activity_data,
                'total_period_bookings': 0
            })
            
        now = timezone.now()
        start_date = now - timedelta(days=int(days))
        
        # Get bookings for the period
        bookings = Booking.objects.filter(
            user=user,
            created_at__gte=start_date
        ).order_by('created_at')
        
        # Group by day
        activity_data = []
        for i in range(int(days)):
            date = start_date + timedelta(days=i)
            day_bookings = bookings.filter(
                created_at__date=date.date()
            ).count()
            
            activity_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'bookings': day_bookings,
                'day': date.strftime('%a')
            })
        
        return JsonResponse({
            'success': True,
            'activity_data': activity_data,
            'total_period_bookings': bookings.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def bookings_list(request):
    """
    Get user's bookings with filtering
    """
    try:
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        if not user:
            return JsonResponse({
                'success': True,
                'bookings': [],
                'total_count': 0
            })
        page = int(request.GET.get('page', 1))
        status = request.GET.get('status', '')
        time_filter = request.GET.get('time_filter', '')
        search = request.GET.get('search', '')
        tab = request.GET.get('tab', 'all')
        
        bookings_query = Booking.objects.filter(user=user)
        
        # Apply filters
        if status:
            bookings_query = bookings_query.filter(status=status)
            
        if time_filter == 'upcoming':
            bookings_query = bookings_query.filter(booking_date__gte=timezone.now().date())
        elif time_filter == 'past':
            bookings_query = bookings_query.filter(booking_date__lt=timezone.now().date())
        elif time_filter == 'this_week':
            week_start = timezone.now() - timedelta(days=7)
            bookings_query = bookings_query.filter(created_at__gte=week_start)
        elif time_filter == 'this_month':
            month_start = timezone.now().replace(day=1)
            bookings_query = bookings_query.filter(created_at__gte=month_start)
        elif time_filter == 'last_month':
            last_month = timezone.now().replace(day=1) - timedelta(days=1)
            last_month_start = last_month.replace(day=1)
            bookings_query = bookings_query.filter(created_at__gte=last_month_start, created_at__lt=timezone.now().replace(day=1))
            
        if search:
            bookings_query = bookings_query.filter(
                Q(playground__name__icontains=search)
            )
            
        if tab != 'all':
            if tab == 'upcoming':
                bookings_query = bookings_query.filter(
                    status__in=['pending', 'confirmed'],
                    booking_date__gte=timezone.now().date()
                )
            elif tab == 'completed':
                bookings_query = bookings_query.filter(status='completed')
            elif tab == 'cancelled':
                bookings_query = bookings_query.filter(status='cancelled')
        
        # Order by date
        bookings_query = bookings_query.order_by('-booking_date', '-created_at')
        
        # Pagination
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page
        total_count = bookings_query.count()
        bookings = bookings_query[start:end]
        
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'playground_name': booking.playground.name if booking.playground else 'Unknown',
                'sport_type': booking.playground.get_sport_types_display() if booking.playground else 'Unknown',
                'date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else '',
                'time': f"{booking.start_time}-{booking.end_time}" if booking.start_time and booking.end_time else 'TBD',
                'status': booking.status,
                'amount': float(booking.total_amount) if booking.total_amount else 0,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M') if booking.created_at else '',
                'can_cancel': booking.status in ['pending', 'confirmed'] and booking.booking_date and booking.booking_date >= timezone.now().date()
            })
        
        # Calculate stats
        all_bookings = Booking.objects.filter(user=user)
        stats = {
            'total_bookings': all_bookings.count(),
            'upcoming': all_bookings.filter(
                status__in=['pending', 'confirmed'],
                booking_date__gte=timezone.now().date()
            ).count(),
            'completed': all_bookings.filter(status='completed').count(),
            'total_spent': float(all_bookings.filter(
                status__in=['completed', 'confirmed']
            ).aggregate(total=Sum('total_amount'))['total'] or 0)
        }
        
        return JsonResponse({
            'success': True,
            'bookings': bookings_data,
            'stats': stats,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + per_page - 1) // per_page,
                'has_next': end < total_count,
                'has_previous': page > 1,
                'total_count': total_count
            },
            'total_count': total_count,
            'filtered_count': bookings_query.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def playgrounds_sports(request):
    """
    Get available sports types
    """
    try:
        # Return sample sports for now
        sports_list = ['Football', 'Basketball', 'Tennis', 'Volleyball', 'Cricket']
        
        return JsonResponse({
            'success': True,
            'sports': sports_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def playgrounds_facilities(request):
    """
    Get available facilities
    """
    try:
        # Basic facilities for now
        facilities = [
            'Parking', 'Changing Rooms', 'Restrooms', 'Water Fountain',
            'Lighting', 'Equipment Rental', 'Scoreboard', 'Seating',
            'Food Court', 'First Aid', 'Lockers', 'Shower'
        ]
        
        return JsonResponse({
            'success': True,
            'facilities': facilities
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def notifications_count(request):
    """
    Get unread notifications count
    """
    try:
        if request.user.is_authenticated:
            count = Notification.objects.filter(
                recipient=request.user, 
                is_read=False
            ).count()
        else:
            count = 0
            
        return JsonResponse({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': True,
            'count': 0
        })

@csrf_exempt
@require_http_methods(["GET"])
def playground_stats(request, playground_id):
    """
    Get statistics for a specific playground
    """
    try:
        playground = Playground.objects.get(id=playground_id)
        
        # Get total bookings for this playground
        total_bookings = Booking.objects.filter(playground=playground).count()
        
        # Get bookings for this month
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_bookings = Booking.objects.filter(
            playground=playground,
            created_at__gte=start_of_month
        ).count()
        
        # Get today's bookings
        today_bookings = Booking.objects.filter(
            playground=playground,
            created_at__date=now.date()
        ).count()
        
        return JsonResponse({
            'success': True,
            'playground_id': playground_id,
            'total_bookings': total_bookings,
            'month_bookings': month_bookings,
            'today_bookings': today_bookings,
            'playground_name': playground.name
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Playground not found',
            'total_bookings': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'total_bookings': 0
        })

@csrf_exempt
@require_http_methods(["GET"])
def booking_count(request, playground_id):
    """
    Simple endpoint to get just the booking count for a playground
    """
    try:
        playground = Playground.objects.get(id=playground_id)
        count = Booking.objects.filter(playground=playground).count()
        
        return JsonResponse({
            'success': True,
            'count': count,
            'playground_id': playground_id
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'count': 0,
            'error': 'Playground not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'count': 0,
            'error': str(e)
        })
