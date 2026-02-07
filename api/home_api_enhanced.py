"""
Enhanced API views for home page dynamic functionality with admin management
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json
from playgrounds.models import Country, State, City, Playground, SportType


@require_http_methods(["GET"])
def get_popular_playgrounds(request):
    """Get popular playgrounds marked by admin - Real-time and dynamic"""
    try:
        limit = int(request.GET.get('limit', 8))
        
        # Currency symbols map
        currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'MYR': 'RM', 'SGD': 'S$',
            'INR': '₹', 'BDT': '৳', 'AUD': 'A$', 'CAD': 'C$', 'JPY': '¥',
            'CNY': '¥', 'AED': 'د.إ', 'SAR': '﷼', 'THB': '฿',
            'IDR': 'Rp', 'PHP': '₱', 'VND': '₫', 'KRW': '₩',
            'TWD': 'NT$', 'HKD': 'HK$', 'NZD': 'NZ$'
        }
        
        # Get ONLY playgrounds marked as popular by admin
        playgrounds = Playground.objects.filter(
            status='active',
            is_popular=True  # Only show playgrounds marked as popular
        ).select_related(
            'city', 'city__state', 'city__state__country'
        ).prefetch_related(
            'sport_types', 'images'
        ).annotate(
            booking_count=Count('bookings')
        ).order_by('-rating', '-booking_count')[:limit]
        
        playgrounds_data = []
        for playground in playgrounds:
            # Get image - prioritize main_image, then gallery images
            image_url = None
            if playground.main_image:
                image_url = playground.main_image.url
            else:
                first_image = playground.images.first()
                if first_image and first_image.image:
                    image_url = first_image.image.url
            
            # Get first sport type
            first_sport = playground.sport_types.first()
            sport_name = first_sport.name if first_sport else None
            sport_icon = first_sport.icon if first_sport else 'fas fa-futbol'
            
            # Location info
            location = playground.city.name if playground.city else playground.address
            
            # Get currency from playground's country
            if playground.city and playground.city.state and playground.city.state.country:
                country = playground.city.state.country
                playground_currency = country.get_currency()
                country_code = country.code
            else:
                playground_currency = playground.currency
                country_code = 'US'
            
            currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
            
            playgrounds_data.append({
                'id': playground.id,
                'name': playground.name,
                'image_url': image_url,
                'sport_type': sport_name,
                'sport_icon': sport_icon,
                'rating': float(playground.rating) if playground.rating else 0.0,
                'location': location,
                'price_per_hour': float(playground.price_per_hour) if playground.price_per_hour else None,
                'currency': playground_currency,
                'currency_symbol': currency_symbol,
                'is_popular': playground.is_popular,
                'booking_count': playground.booking_count,
                'country_code': country_code,
                'detail_url': f'/playgrounds/details/{playground.id}/'
            })
        
        return JsonResponse({
            'success': True,
            'playgrounds': playgrounds_data,
            'count': len(playgrounds_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'playgrounds': []
        }, status=500)


def is_admin_or_owner(user):
    """Check if user is admin or playground owner"""
    return user.is_staff or user.is_superuser or hasattr(user, 'playground_owner')


@require_http_methods(["GET"])
def get_states(request):
    """Get states for a country with enhanced data"""
    country_id = request.GET.get('country')
    if not country_id:
        return JsonResponse({'states': []}, safe=False)
    
    try:
        # First check if country exists
        from playgrounds.models import Country
        if not Country.objects.filter(id=country_id).exists():
            return JsonResponse({'states': []}, safe=False)
        
        states = State.objects.filter(
            country_id=country_id,
            is_active=True
        ).distinct().values('id', 'name').order_by('name')
        
        states_list = []
        for state in states:
            states_list.append({
                'id': state['id'],
                'name': state['name']
            })
        
        return JsonResponse({'states': states_list}, safe=False)
        
    except Exception as e:
        # Return fallback states if there's an error
        fallback_states = [
            {'id': 1, 'name': 'California'},
            {'id': 2, 'name': 'New York'},
            {'id': 3, 'name': 'Texas'},
            {'id': 4, 'name': 'Florida'}
        ]
        return JsonResponse({'states': fallback_states}, safe=False)


@require_http_methods(["GET"])
def get_cities(request):
    """Get cities for a state with playground counts"""
    state_id = request.GET.get('state')
    if not state_id:
        return JsonResponse({'cities': []}, safe=False)
    
    try:
        # First check if state exists
        from playgrounds.models import State
        if not State.objects.filter(id=state_id).exists():
            return JsonResponse({'cities': []}, safe=False)
        
        cities = City.objects.filter(
            state_id=state_id,
            is_active=True
        ).distinct().values('id', 'name').order_by('name')
        
        cities_list = []
        for city in cities:
            cities_list.append({
                'id': city['id'],
                'name': city['name']
            })
        
        return JsonResponse({'cities': cities_list}, safe=False)
        
    except Exception as e:
        # Return fallback cities if there's an error
        fallback_cities = [
            {'id': 1, 'name': 'Los Angeles'},
            {'id': 2, 'name': 'New York'},
            {'id': 3, 'name': 'Houston'},
            {'id': 4, 'name': 'Toronto'},
            {'id': 5, 'name': 'London'}
        ]
        return JsonResponse({'cities': fallback_cities}, safe=False)


@require_http_methods(["GET"])
def search_playgrounds(request):
    """Enhanced search playgrounds with filters and analytics"""
    try:
        # Get search parameters
        sport_id = request.GET.get('sport')
        country_id = request.GET.get('country')
        state_id = request.GET.get('state')
        city_id = request.GET.get('city')
        date = request.GET.get('date')
        price_range = request.GET.get('price_range')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 12))
        
        # Base queryset with enhanced annotations
        playgrounds = Playground.objects.filter(status='active').select_related(
            'city__state__country', 'owner'
        ).prefetch_related('sport_types', 'images')
        
        # Apply filters
        if sport_id:
            playgrounds = playgrounds.filter(sport_types__id=sport_id)
        
        if country_id:
            playgrounds = playgrounds.filter(city__state__country_id=country_id)
        
        if state_id:
            playgrounds = playgrounds.filter(city__state_id=state_id)
        
        if city_id:
            playgrounds = playgrounds.filter(city_id=city_id)
        
        # Enhanced price range filter
        if price_range:
            if price_range == '0-25':
                playgrounds = playgrounds.filter(price_per_hour__lte=25)
            elif price_range == '25-50':
                playgrounds = playgrounds.filter(price_per_hour__gte=25, price_per_hour__lte=50)
            elif price_range == '50-100':
                playgrounds = playgrounds.filter(price_per_hour__gte=50, price_per_hour__lte=100)
            elif price_range == '100+':
                playgrounds = playgrounds.filter(price_per_hour__gte=100)
        
        # Date availability filter (if provided)
        if date:
            try:
                booking_date = datetime.strptime(date, '%Y-%m-%d').date()
                # Exclude playgrounds that are fully booked on the selected date
                playgrounds = playgrounds.exclude(
                    bookings__date=booking_date,
                    bookings__status='confirmed'
                ).distinct()
            except ValueError:
                pass
        
        # Get distinct results and order
        playgrounds = playgrounds.distinct().order_by('-rating', '-total_bookings')
        
        # Pagination
        paginator = Paginator(playgrounds, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize results with proper null checking
        results = []
        for playground in page_obj:
            # Safe location building
            location_parts = []
            if playground.city:
                location_parts.append(playground.city.name)
                if playground.city.state:
                    location_parts.append(playground.city.state.name)
                    if playground.city.state.country:
                        location_parts.append(playground.city.state.country.name)
            location = ', '.join(location_parts) if location_parts else playground.address or 'Location not specified'
            
            # Safe image URL
            image_url = None
            if playground.main_image:
                image_url = playground.main_image.url
            elif playground.images.exists():
                first_img = playground.images.first()
                if first_img and first_img.image:
                    image_url = first_img.image.url
            
            result = {
                'id': playground.id,
                'name': playground.name,
                'description': (playground.description[:150] + '...') if playground.description and len(playground.description) > 150 else (playground.description or ''),
                'location': location,
                'price_per_hour': float(playground.price_per_hour) if playground.price_per_hour else 0,
                'rating': float(playground.rating) if playground.rating else 0,
                'booking_count': playground.total_bookings or 0,
                'image_url': image_url,
                'sport_types': [sport.name for sport in playground.sport_types.all()],
                'url': f'/playgrounds/details/{playground.id}/',
            }
            results.append(result)
        
        return JsonResponse({
            'success': True,
            'results': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        })
    except Exception as e:
        import traceback
        print(f"Search error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e),
            'results': [],
            'pagination': {
                'current_page': 1,
                'total_pages': 0,
                'total_count': 0,
                'has_previous': False,
                'has_next': False,
            }
        })


@require_http_methods(["GET"])  
def get_live_stats(request):
    """Get live statistics for the dashboard"""
    from django.db.models import Sum
    
    stats = {
        'total_playgrounds': Playground.objects.filter(status='active').count(),
        'total_countries': Country.objects.filter(is_active=True).count(),
        'total_bookings': 0,  # This would come from bookings model
        'active_users': 0,    # This would come from user activity
    }
    
    return JsonResponse(stats)


@login_required
@user_passes_test(is_admin_or_owner)
@require_http_methods(["GET"])
def admin_dashboard_stats(request):
    """Get admin dashboard statistics"""
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    stats = {
        'overview': {
            'total_playgrounds': Playground.objects.count(),
            'active_playgrounds': Playground.objects.filter(status='active').count(),
            'pending_playgrounds': Playground.objects.filter(status='pending').count(),
            'total_countries': Country.objects.filter(is_active=True).count(),
        },
        'recent': {
            'new_playgrounds_week': Playground.objects.filter(created_at__gte=last_week).count(),
            'new_playgrounds_month': Playground.objects.filter(created_at__gte=last_month).count(),
        },
        'popular_sports': list(
            SportType.objects.annotate(
                playground_count=Count('playgrounds')
            ).values('name', 'playground_count').order_by('-playground_count')[:5]
        ),
        'top_cities': list(
            City.objects.annotate(
                playground_count=Count('playgrounds')
            ).values('name', 'state__name', 'playground_count').order_by('-playground_count')[:10]
        )
    }
    
    return JsonResponse(stats)


@login_required
@user_passes_test(is_admin_or_owner)
@csrf_exempt
@require_http_methods(["POST"])
def quick_add_playground(request):
    """Quick add playground for admins/owners"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'city_id', 'price_per_hour', 'sport_types']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Create playground
        playground = Playground.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            city_id=data['city_id'],
            address=data.get('address', ''),
            price_per_hour=data['price_per_hour'],
            capacity=data.get('capacity', 10),
            owner=request.user,
            status='pending' if not request.user.is_staff else 'active'
        )
        
        # Add sport types
        sport_type_ids = data.get('sport_types', [])
        if sport_type_ids:
            playground.sport_types.set(sport_type_ids)
        
        return JsonResponse({
            'success': True,
            'playground_id': playground.id,
            'message': 'Playground created successfully',
            'status': playground.status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin_or_owner)
@require_http_methods(["GET"])
def manage_playgrounds(request):
    """Get playgrounds for management interface"""
    user = request.user
    page = int(request.GET.get('page', 1))
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    if user.is_staff:
        playgrounds = Playground.objects.all()
    else:
        playgrounds = Playground.objects.filter(owner=user)
    
    # Apply filters
    if status_filter != 'all':
        playgrounds = playgrounds.filter(status=status_filter)
        
    if search_query:
        playgrounds = playgrounds.filter(
            Q(name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(playgrounds.order_by('-created_at'), 10)
    page_obj = paginator.get_page(page)
    
    # Serialize results
    results = []
    for playground in page_obj:
        result = {
            'id': playground.id,
            'name': playground.name,
            'location': f"{playground.city.name}, {playground.city.state.name}",
            'status': playground.status,
            'price_per_hour': float(playground.price_per_hour),
            'created_at': playground.created_at.isoformat(),
            'sport_types': [sport.name for sport in playground.sport_types.all()],
            'can_edit': user.is_staff or playground.owner == user,
        }
        results.append(result)
    
    return JsonResponse({
        'results': results,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
        },
        'filters': {
            'status_options': [
                {'value': 'all', 'label': 'All Status'},
                {'value': 'active', 'label': 'Active'},
                {'value': 'pending', 'label': 'Pending'},
                {'value': 'inactive', 'label': 'Inactive'},
            ]
        }
    })
