"""
API endpoints for location filtering (states and cities)
Provides real-time dropdown population based on parent selection
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from playgrounds.models import State, City


@require_http_methods(["GET"])
@cache_page(300)  # Cache for 5 minutes
def get_states_by_country(request):
    """Get all states for a specific country"""
    country_id = request.GET.get('country_id')
    
    if not country_id:
        return JsonResponse({'error': 'Country ID is required'}, status=400)
    
    try:
        states = State.objects.filter(
            country_id=country_id,
            is_active=True
        ).values('id', 'name').order_by('name')
        
        return JsonResponse({
            'success': True,
            'states': list(states)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@cache_page(300)  # Cache for 5 minutes
def get_cities_by_state(request):
    """Get all cities for a specific state"""
    state_id = request.GET.get('state_id')
    
    if not state_id:
        return JsonResponse({'error': 'State ID is required'}, status=400)
    
    try:
        cities = City.objects.filter(
            state_id=state_id,
            is_active=True
        ).values('id', 'name').order_by('name')
        
        return JsonResponse({
            'success': True,
            'cities': list(cities)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@cache_page(300)  # Cache for 5 minutes
def get_all_locations(request):
    """Get countries with their states and cities for initial load"""
    try:
        from playgrounds.models import Country
        
        countries = Country.objects.filter(is_active=True).prefetch_related(
            'states__cities'
        ).values('id', 'name')
        
        return JsonResponse({
            'success': True,
            'countries': list(countries)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
