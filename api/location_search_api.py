"""
Location-based Search API for Playground Booking System
Provides search functionality with country, state, city, and budget filters
"""

import math
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count, Avg
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from playgrounds.models import Playground, SportType, Country, State, City


class LocationBasedSearchAPI(View):
    """Location-based playground search with advanced filters"""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            # Get search parameters
            query = request.GET.get('query', '').strip()
            country = request.GET.get('country', '').strip()
            state = request.GET.get('state', '').strip()
            city = request.GET.get('city', '').strip()
            min_price = request.GET.get('min_price', '')
            max_price = request.GET.get('max_price', '')
            sport_type = request.GET.get('sport_type', '')
            date = request.GET.get('date', '')
            amenities = request.GET.getlist('amenities[]')
            rating = request.GET.get('rating', '')
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 12))

            # Start with active playgrounds
            playgrounds = Playground.objects.filter(status='active').select_related(
                'city', 'city__state', 'city__state__country'
            ).prefetch_related('sport_types')

            # Apply text search filter
            if query:
                playgrounds = playgrounds.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(address__icontains=query) |
                    Q(city__name__icontains=query) |
                    Q(city__state__name__icontains=query) |
                    Q(city__state__country__name__icontains=query)
                )

            # Apply location filters
            if country:
                playgrounds = playgrounds.filter(city__state__country__name__icontains=country)
            
            if state:
                playgrounds = playgrounds.filter(city__state__name__icontains=state)
            
            if city:
                playgrounds = playgrounds.filter(city__name__icontains=city)

            # Apply price range filter (budget filter)
            if min_price:
                try:
                    min_price_val = float(min_price)
                    playgrounds = playgrounds.filter(price_per_hour__gte=min_price_val)
                except ValueError:
                    pass

            if max_price:
                try:
                    max_price_val = float(max_price)
                    playgrounds = playgrounds.filter(price_per_hour__lte=max_price_val)
                except ValueError:
                    pass

            # Apply sport type filter
            if sport_type:
                try:
                    sport_id = int(sport_type)
                    playgrounds = playgrounds.filter(sport_types__id=sport_id)
                except (ValueError, TypeError):
                    playgrounds = playgrounds.filter(sport_types__name__icontains=sport_type)

            # Apply amenities filter
            if amenities:
                for amenity in amenities:
                    playgrounds = playgrounds.filter(amenities__contains=[amenity])

            # Apply rating filter
            if rating:
                try:
                    rating_val = float(rating)
                    playgrounds = playgrounds.filter(rating__gte=rating_val)
                except ValueError:
                    pass

            # Get total count before pagination
            total_count = playgrounds.count()

            # Apply pagination
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            playgrounds_page = playgrounds[start_index:end_index]

            # Format results
            results = []
            for playground in playgrounds_page:
                # Get sport types
                sport_types = list(playground.sport_types.values_list('name', flat=True))
                
                # Format amenities
                amenities_list = playground.amenities if playground.amenities else []
                
                # Format location
                location_parts = []
                if playground.city:
                    location_parts.append(playground.city.name)
                    if playground.city.state:
                        location_parts.append(playground.city.state.name)
                        if playground.city.state.country:
                            location_parts.append(playground.city.state.country.name)
                
                location = ", ".join(location_parts) if location_parts else playground.address

                playground_data = {
                    'id': playground.id,
                    'name': playground.name,
                    'description': playground.description[:200] + '...' if len(playground.description) > 200 else playground.description,
                    'address': playground.address,
                    'location': location,
                    'city': playground.city.name if playground.city else '',
                    'state': playground.city.state.name if playground.city and playground.city.state else '',
                    'country': playground.city.state.country.name if playground.city and playground.city.state and playground.city.state.country else '',
                    'price_per_hour': float(playground.price_per_hour),
                    'rating': float(playground.rating),
                    'review_count': playground.review_count,
                    'sport_types': sport_types,
                    'amenities': amenities_list,
                    'main_image': playground.main_image.url if playground.main_image else None,
                    'is_featured': playground.is_featured,
                    'available_slots': self.get_available_slots(playground, date),
                    'distance': None  # Can be calculated if user location is provided
                }
                results.append(playground_data)

            # Calculate pagination info
            total_pages = math.ceil(total_count / per_page)
            has_next = page < total_pages
            has_previous = page > 1

            return JsonResponse({
                'success': True,
                'results': results,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'per_page': per_page,
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'start_index': start_index + 1 if results else 0,
                    'end_index': start_index + len(results),
                    'start_page': max(1, page - 2),
                    'end_page': min(total_pages, page + 2)
                },
                'filters_applied': {
                    'query': query,
                    'country': country,
                    'state': state,
                    'city': city,
                    'min_price': min_price,
                    'max_price': max_price,
                    'sport_type': sport_type,
                    'amenities': amenities,
                    'rating': rating
                }
            })

        except Exception as e:
            print(f"Location search error: {str(e)}")  # For debugging
            return JsonResponse({
                'success': False,
                'error': f'Search failed: {str(e)}',
                'results': [],
                'pagination': {
                    'current_page': 1,
                    'total_pages': 0,
                    'total_count': 0,
                    'per_page': per_page,
                    'has_next': False,
                    'has_previous': False
                }
            })

    def get_available_slots(self, playground, date):
        """Get available time slots for a specific date"""
        if not date:
            return []
        
        try:
            # This is a simplified version - you can expand based on your booking logic
            available_slots = []
            
            # Generate example slots (9 AM to 10 PM)
            for hour in range(9, 22):
                slot = {
                    'time': f"{hour:02d}:00",
                    'available': True,  # You can check actual bookings here
                    'price': float(playground.price_per_hour)
                }
                available_slots.append(slot)
            
            return available_slots
        except:
            return []


class LocationDataAPI(View):
    """Get countries, states, and cities for location filters"""
    
    def get(self, request):
        try:
            # Check for country_id parameter (for getting states)
            country_id = request.GET.get('country_id')
            # Check for state_id parameter (for getting cities)
            state_id = request.GET.get('state_id')
            
            if country_id:
                # Return states for the given country
                states = State.objects.filter(
                    country_id=country_id,
                    cities__playgrounds__status='active'
                ).distinct().order_by('name')
                
                return JsonResponse({
                    'success': True,
                    'states': [
                        {
                            'id': state.id,
                            'name': state.name
                        }
                        for state in states
                    ]
                })
            
            elif state_id:
                # Return cities for the given state
                cities = City.objects.filter(
                    state_id=state_id,
                    playgrounds__status='active'
                ).distinct().order_by('name')
                
                return JsonResponse({
                    'success': True,
                    'cities': [
                        {
                            'id': city.id,
                            'name': city.name
                        }
                        for city in cities
                    ]
                })
            
            else:
                # Return all countries (default behavior)
                countries = Country.objects.filter(
                    states__cities__playgrounds__status='active'
                ).distinct().order_by('name')
                
                # If no countries found with playgrounds, return all countries
                if not countries.exists():
                    countries = Country.objects.all().order_by('name')
                
                return JsonResponse({
                    'success': True,
                    'countries': [
                        {
                            'id': country.id,
                            'name': country.name,
                            'code': getattr(country, 'code', '')
                        }
                        for country in countries
                    ]
                })
            
        except Exception as e:
            print(f"LocationDataAPI error: {str(e)}")  # For debugging
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class SearchSuggestionsAPI(View):
    """Get search suggestions for autocomplete"""
    
    def get(self, request):
        try:
            query = request.GET.get('query', '').strip()
            
            if len(query) < 2:
                return JsonResponse({
                    'success': True,
                    'suggestions': []
                })
            
            # Get playground suggestions
            playgrounds = Playground.objects.filter(
                name__icontains=query,
                status='active'
            )[:5]
            
            # Get location suggestions
            countries = Country.objects.filter(name__icontains=query)[:3]
            states = State.objects.filter(name__icontains=query)[:3]
            cities = City.objects.filter(name__icontains=query)[:5]
            
            suggestions = []
            
            # Add playground suggestions
            for playground in playgrounds:
                suggestions.append({
                    'type': 'playground',
                    'text': playground.name,
                    'location': f"{playground.city.name if playground.city else ''}, {playground.city.state.name if playground.city and playground.city.state else ''}",
                    'id': playground.id
                })
            
            # Add location suggestions
            for country in countries:
                suggestions.append({
                    'type': 'country',
                    'text': country.name,
                    'location': 'Country',
                    'id': country.id
                })
            
            for state in states:
                suggestions.append({
                    'type': 'state',
                    'text': state.name,
                    'location': f"{state.country.name if state.country else ''}",
                    'id': state.id
                })
            
            for city in cities:
                suggestions.append({
                    'type': 'city',
                    'text': city.name,
                    'location': f"{city.state.name if city.state else ''}, {city.state.country.name if city.state and city.state.country else ''}",
                    'id': city.id
                })
            
            return JsonResponse({
                'success': True,
                'suggestions': suggestions[:10]  # Limit to 10 suggestions
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'suggestions': []
            })
