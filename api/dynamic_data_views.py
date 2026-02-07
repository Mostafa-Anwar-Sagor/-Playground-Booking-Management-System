from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from playgrounds.models import Country, State, City, SportType
import json


@require_http_methods(["GET"])
def get_countries(request):
    """Get all active countries"""
    countries = Country.objects.filter(is_active=True).values('id', 'name', 'code')
    return JsonResponse({
        'success': True,
        'countries': list(countries)
    })


@require_http_methods(["GET"])
def get_states(request):
    """Get states by country"""
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse({
            'success': False,
            'error': 'Country ID is required'
        })
    
    states = State.objects.filter(
        country_id=country_id, 
        is_active=True
    ).values('id', 'name')
    
    return JsonResponse({
        'success': True,
        'states': list(states)
    })


@require_http_methods(["GET"])
def get_cities(request):
    """Get cities by state"""
    state_id = request.GET.get('state_id') or request.GET.get('state')
    
    if state_id:
        # Get cities for specific state
        cities = City.objects.filter(
            state_id=state_id, 
            is_active=True
        ).values('id', 'name', 'latitude', 'longitude')
    else:
        # For testing purposes, return first 10 cities if no state specified
        cities = City.objects.filter(
            is_active=True
        )[:10].values('id', 'name', 'latitude', 'longitude')
    
    return JsonResponse({
        'success': True,
        'cities': list(cities)
    })


@require_http_methods(["GET"])
def get_sport_types(request):
    """Get all active sport types"""
    sports = SportType.objects.filter(is_active=True).values(
        'id', 'name', 'icon', 'description'
    )
    
    return JsonResponse({
        'success': True,
        'sports': list(sports)
    })


@require_http_methods(["GET"])
def get_playground_types(request):
    """Get all active playground types from the PlaygroundType model"""
    from playgrounds.models import PlaygroundType
    
    playground_types = PlaygroundType.objects.filter(is_active=True).values(
        'id', 'name', 'description', 'icon'
    )
    
    return JsonResponse({
        'success': True,
        'playground_types': list(playground_types)
    })


@require_http_methods(["GET"])
def get_form_data(request):
    """Get all form data in one request"""
    from playgrounds.models import PlaygroundType
    
    countries = list(Country.objects.filter(is_active=True).values('id', 'name', 'code'))
    sports = list(SportType.objects.filter(is_active=True).values('id', 'name', 'icon', 'description'))
    playground_types = list(PlaygroundType.objects.filter(is_active=True).values('id', 'name', 'description', 'icon'))
    
    return JsonResponse({
        'success': True,
        'data': {
            'countries': countries,
            'sports': sports,
            'playground_types': playground_types,
            'environment_types': [
                {'value': 'indoor', 'label': 'Indoor', 'icon': '🏢'},
                {'value': 'outdoor', 'label': 'Outdoor', 'icon': '🌳'},
                {'value': 'hybrid', 'label': 'Indoor/Outdoor', 'icon': '🔄'}
            ]
        }
    })
