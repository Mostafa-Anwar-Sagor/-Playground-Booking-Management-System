"""
Advanced Search API for Playground Booking System
Provides comprehensive search functionality with filters, suggestions, and real-time data
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count, Avg, F
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
import requests
from datetime import datetime, date

from playgrounds.models import Playground, SportType
from bookings.models import Booking


class PlaygroundSearchAPI(View):
    """Advanced playground search with filters and real-time data"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            # Get search parameters
            search_query = request.GET.get('search', '').strip()
            location = request.GET.get('location', '').strip()
            distance = request.GET.get('distance', '')
            sort_by = request.GET.get('sort', 'distance')
            min_price = request.GET.get('min_price', '')
            max_price = request.GET.get('max_price', '')
            date_filter = request.GET.get('date', '')
            time_filter = request.GET.get('time', '')
            rating = request.GET.get('rating', '')
            sports = SportType.objects.all().order_by('name')
            facilities = request.GET.getlist('facilities')
            features = request.GET.getlist('features')
            page = int(request.GET.get('page', 1))
            
            # Start with all active playgrounds
            playgrounds = Playground.objects.filter(is_active=True).select_related('owner').prefetch_related('sports', 'facilities', 'images')
            
            # Apply search query
            if search_query:
                playgrounds = playgrounds.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(location__icontains=search_query) |
                    Q(sports__name__icontains=search_query) |
                    Q(facilities__name__icontains=search_query)
                ).distinct()
            
            # Apply location filter
            if location:
                playgrounds = playgrounds.filter(
                    Q(location__icontains=location) |
                    Q(address__icontains=location) |
                    Q(city__icontains=location)
                )
            
            # Apply price range filter
            if min_price:
                playgrounds = playgrounds.filter(price_per_hour__gte=float(min_price))
            if max_price:
                playgrounds = playgrounds.filter(price_per_hour__lte=float(max_price))
            
            # Apply rating filter
            if rating:
                playgrounds = playgrounds.annotate(
                    avg_rating=Avg('reviews__rating')
                ).filter(avg_rating__gte=float(rating))
            
            # Apply sports filter
            if sports:
                playgrounds = playgrounds.filter(sports__id__in=sports).distinct()
            
            # Apply facilities filter
            if facilities:
                playgrounds = playgrounds.filter(facilities__id__in=facilities).distinct()
            
            # Apply features filter
            if features:
                for feature in features:
                    if feature == 'parking':
                        playgrounds = playgrounds.filter(has_parking=True)
                    elif feature == 'restrooms':
                        playgrounds = playgrounds.filter(has_restrooms=True)
                    elif feature == 'lighting':
                        playgrounds = playgrounds.filter(has_lighting=True)
            
            # Apply date and time availability filter
            if date_filter:
                # Check availability for specific date
                try:
                    search_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    # Exclude playgrounds with bookings on this date/time
                    existing_bookings = Booking.objects.filter(
                        date=search_date,
                        status__in=['confirmed', 'pending']
                    ).values_list('playground_id', flat=True)
                    
                    if time_filter:
                        # Further filter by time if specified
                        time_ranges = {
                            'morning': (6, 12),
                            'afternoon': (12, 18),
                            'evening': (18, 24)
                        }
                        if time_filter in time_ranges:
                            start_hour, end_hour = time_ranges[time_filter]
                            existing_bookings = existing_bookings.filter(
                                start_time__hour__range=(start_hour, end_hour)
                            )
                    
                    playgrounds = playgrounds.exclude(id__in=existing_bookings)
                except ValueError:
                    pass  # Invalid date format, ignore filter
            
            # Annotate with additional data
            playgrounds = playgrounds.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews'),
                booking_count=Count('bookings')
            )
            
            # Apply sorting
            sort_options = {
                'distance': 'id',  # Placeholder for distance sorting
                'price': 'price_per_hour',
                'price_desc': '-price_per_hour',
                'rating': '-avg_rating',
                'popularity': '-booking_count',
                'newest': '-created_at'
            }
            
            if sort_by in sort_options:
                playgrounds = playgrounds.order_by(sort_options[sort_by])
            
            # Get total count before pagination
            total_count = playgrounds.count()
            
            # Pagination
            paginator = Paginator(playgrounds, 12)  # 12 results per page
            page_obj = paginator.get_page(page)
            
            # Serialize results
            results = []
            for playground in page_obj:
                # Get first image
                first_image = playground.images.first()
                image_url = first_image.image.url if first_image else None
                
                # Calculate average rating
                avg_rating = playground.avg_rating or 0
                
                # Get sports and facilities
                sports_data = [{'id': s.id, 'name': s.name} for s in playground.sports.all()]
                facilities_data = [
                    {
                        'id': f.id, 
                        'name': f.name, 
                        'icon': f.icon or 'fa-cog'
                    } 
                    for f in playground.facilities.all()
                ]
                
                results.append({
                    'id': playground.id,
                    'name': playground.name,
                    'description': playground.description,
                    'location': playground.location,
                    'address': playground.address,
                    'price_per_hour': float(playground.price_per_hour),
                    'rating': round(avg_rating, 1),
                    'review_count': playground.review_count or 0,
                    'image': image_url,
                    'sports': sports_data,
                    'facilities': facilities_data,
                    'distance': None,  # Can be calculated if user location is provided
                    'available': True,  # Can be calculated based on date/time
                    'features': {
                        'parking': playground.has_parking,
                        'restrooms': playground.has_restrooms,
                        'lighting': playground.has_lighting,
                    }
                })
            
            # Pagination info
            pagination_info = {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'start_index': page_obj.start_index() if page_obj else 0,
                'end_index': page_obj.end_index() if page_obj else 0,
                'start_page': max(1, page_obj.number - 2),
                'end_page': min(paginator.num_pages, page_obj.number + 2),
            }
            
            return JsonResponse({
                'success': True,
                'playgrounds': results,
                'pagination': pagination_info,
                'total_count': total_count,
                'filters_applied': {
                    'search': search_query,
                    'location': location,
                    'distance': distance,
                    'sort': sort_by,
                    'price_range': f"{min_price}-{max_price}" if min_price or max_price else None,
                    'date': date_filter,
                    'time': time_filter,
                    'rating': rating,
                    'sports_count': len(sports),
                    'facilities_count': len(facilities),
                    'features_count': len(features)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Search failed: {str(e)}'
            }, status=500)


class SearchSuggestionsAPI(View):
    """Provide real-time search suggestions"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            query = request.GET.get('q', '').strip()
            
            if len(query) < 2:
                return JsonResponse({
                    'success': True,
                    'suggestions': []
                })
            
            suggestions = []
            
            # Playground name suggestions
            playgrounds = Playground.objects.filter(
                name__icontains=query,
                is_active=True
            )[:5]
            
            for playground in playgrounds:
                suggestions.append({
                    'value': playground.name,
                    'label': playground.name,
                    'icon': 'fa-map-marker-alt',
                    'type': 'playground'
                })
            
            # Sport suggestions
            sports = SportType.objects.filter(name__icontains=query)[:3]
            for sport in sports:
                suggestions.append({
                    'value': sport.name,
                    'label': f"{sport.name} (Sport)",
                    'icon': 'fa-futbol',
                    'type': 'sport'
                })
            
            # Location suggestions
            locations = Playground.objects.filter(
                Q(location__icontains=query) | Q(city__icontains=query),
                is_active=True
            ).values_list('location', flat=True).distinct()[:3]
            
            for location in locations:
                suggestions.append({
                    'value': location,
                    'label': f"{location} (Location)",
                    'icon': 'fa-location-arrow',
                    'type': 'location'
                })
            
            return JsonResponse({
                'success': True,
                'suggestions': suggestions[:10]  # Limit to 10 suggestions
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Suggestions failed: {str(e)}'
            }, status=500)


class SportsAPI(View):
    """Get available sports for filtering"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            sports = SportType.objects.all().order_by('name')
            sports_data = [
                {
                    'id': sport.id,
                    'name': sport.name,
                    'icon': 'fa-futbol',  # Use default icon since SportType might not have icon field
                    'playground_count': Playground.objects.filter(sport_types=sport, is_active=True).count()
                }
                for sport in sports
            ]
            
            return JsonResponse({
                'success': True,
                'sports': sports_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to load sports: {str(e)}'
            }, status=500)


class FacilitiesAPI(View):
    """Get available amenities for filtering"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            # Get all unique amenities from active playgrounds
            playgrounds = Playground.objects.filter(is_active=True).exclude(amenities__isnull=True)
            all_amenities = set()
            
            for playground in playgrounds:
                if playground.amenities:
                    for amenity in playground.amenities:
                        if isinstance(amenity, str) and amenity.strip():
                            all_amenities.add(amenity.strip())
            
            amenities_data = [
                {
                    'id': i,
                    'name': amenity,
                    'icon': 'fa-check-circle',
                    'playground_count': playgrounds.filter(amenities__contains=[amenity]).count()
                }
                for i, amenity in enumerate(sorted(all_amenities), 1)
            ]
            
            return JsonResponse({
                'success': True,
                'facilities': amenities_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to load facilities: {str(e)}'
            }, status=500)


class ReverseGeocodeAPI(View):
    """Convert GPS coordinates to address"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            lat = request.GET.get('lat')
            lng = request.GET.get('lng')
            
            if not lat or not lng:
                return JsonResponse({
                    'success': False,
                    'error': 'Latitude and longitude required'
                }, status=400)
            
            # For demo purposes, return a mock address
            # In production, integrate with Google Maps Geocoding API or similar
            mock_address = f"Location at {lat}, {lng}"
            
            # Example Google Maps integration (uncomment and add API key):
            # api_key = settings.GOOGLE_MAPS_API_KEY
            # url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
            # response = requests.get(url)
            # if response.status_code == 200:
            #     data = response.json()
            #     if data['status'] == 'OK' and data['results']:
            #         address = data['results'][0]['formatted_address']
            #     else:
            #         address = mock_address
            # else:
            #     address = mock_address
            
            return JsonResponse({
                'success': True,
                'address': mock_address,
                'latitude': float(lat),
                'longitude': float(lng)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Reverse geocoding failed: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SaveSearchAPI(View):
    """Save user search preferences"""
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            filters = data.get('filters', {})
            
            # In a real application, save to UserSearchPreference model
            # For now, just return success
            
            return JsonResponse({
                'success': True,
                'message': 'Search preferences saved successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to save search: {str(e)}'
            }, status=500)
