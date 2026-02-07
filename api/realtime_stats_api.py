"""
Real-time Statistics API for Homepage
Provides live statistics data for counters
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db.models import Count
from accounts.models import User
from playgrounds.models import Playground, Country
from bookings.models import Booking


@require_http_methods(["GET"])
@cache_page(60)  # Cache for 1 minute
def get_realtime_stats(request):
    """
    Get real-time statistics for homepage counters
    Cached for 1 minute to reduce database load
    """
    try:
        # Get statistics
        total_users = User.objects.filter(user_type='user', is_active=True).count()
        total_playgrounds = Playground.objects.filter(status='active').count()
        total_bookings = Booking.objects.filter(status='completed').count()
        total_countries = Country.objects.filter(
            is_active=True,
            states__cities__playgrounds__status='active'
        ).distinct().count()
        
        # Return statistics
        return JsonResponse({
            'success': True,
            'data': {
                'total_users': total_users,
                'total_playgrounds': total_playgrounds,
                'total_bookings': total_bookings,
                'total_countries': total_countries
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
