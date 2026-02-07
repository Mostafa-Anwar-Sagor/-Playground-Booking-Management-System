from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
from datetime import datetime, timedelta
from playgrounds.models import Playground, Country, State, City, SportType, PlaygroundImage, TimeSlot
from accounts.models import User


@login_required
@require_http_methods(["GET"])
def get_countries(request):
    """Get all active countries"""
    try:
        countries = Country.objects.filter(is_active=True).order_by('name')
        data = {
            'countries': [
                {
                    'id': country.id,
                    'name': country.name,
                    'code': country.code
                }
                for country in countries
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_states(request):
    """Get states for a specific country"""
    try:
        country_id = request.GET.get('country')
        if not country_id:
            return JsonResponse({'error': 'Country ID is required'}, status=400)
        
        states = State.objects.filter(
            country_id=country_id, 
            is_active=True
        ).order_by('name')
        
        data = {
            'states': [
                {
                    'id': state.id,
                    'name': state.name
                }
                for state in states
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_cities(request):
    """Get cities for a specific state"""
    try:
        state_id = request.GET.get('state')
        if not state_id:
            return JsonResponse({'error': 'State ID is required'}, status=400)
        
        cities = City.objects.filter(
            state_id=state_id, 
            is_active=True
        ).order_by('name')
        
        data = {
            'cities': [
                {
                    'id': city.id,
                    'name': city.name,
                    'latitude': float(city.latitude) if city.latitude else None,
                    'longitude': float(city.longitude) if city.longitude else None
                }
                for city in cities
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_sport_types(request):
    """Get all active sport types"""
    try:
        sport_types = SportType.objects.filter(is_active=True).order_by('name')
        data = {
            'sport_types': [
                {
                    'id': sport.id,
                    'name': sport.name,
                    'icon': sport.icon,
                    'description': sport.description
                }
                for sport in sport_types
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_owner_playgrounds(request):
    """Get playgrounds owned by the current user"""
    try:
        playgrounds = Playground.objects.filter(
            owner=request.user
        ).select_related(
            'city__state__country'
        ).prefetch_related(
            'sport_types', 'images'
        ).order_by('-created_at')
        
        data = {
            'playgrounds': [
                {
                    'id': playground.id,
                    'name': playground.name,
                    'description': playground.description,
                    'status': playground.status,
                    'rating': float(playground.rating) if playground.rating else 0.0,
                    'price_per_hour': float(playground.price_per_hour),
                    'price_per_day': float(playground.price_per_day) if playground.price_per_day else None,
                    'capacity': playground.capacity,
                    'size': playground.size,
                    'playground_type': playground.playground_type,
                    'main_image': playground.main_image.url if playground.main_image else None,
                    'total_bookings': playground.total_bookings,
                    'review_count': playground.review_count,
                    'today_bookings': 0,  # Calculate from actual bookings
                    'city': {
                        'id': playground.city.id,
                        'name': playground.city.name,
                        'state': {
                            'id': playground.city.state.id,
                            'name': playground.city.state.name,
                            'country': {
                                'id': playground.city.state.country.id,
                                'name': playground.city.state.country.name
                            }
                        }
                    },
                    'sport_types': [
                        {
                            'id': sport.id,
                            'name': sport.name,
                            'icon': sport.icon
                        }
                        for sport in playground.sport_types.all()
                    ],
                    'images': [
                        {
                            'id': image.id,
                            'image': image.image.url,
                            'caption': image.caption,
                            'is_primary': image.is_primary
                        }
                        for image in playground.images.all()
                    ],
                    'amenities': playground.amenities,
                    'created_at': playground.created_at.isoformat(),
                    'updated_at': playground.updated_at.isoformat()
                }
                for playground in playgrounds
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_playground(request):
    """Create a new playground"""
    try:
        # Parse form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        city_id = request.POST.get('city')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        sport_type_id = request.POST.get('sport_type')
        playground_type = request.POST.get('playground_type')
        capacity = request.POST.get('capacity')
        size = request.POST.get('size')
        price_per_hour = request.POST.get('price_per_hour')
        price_per_day = request.POST.get('price_per_day')
        phone_number = request.POST.get('phone_number')
        whatsapp_number = request.POST.get('whatsapp_number')
        google_maps_url = request.POST.get('google_maps_url')
        amenities_json = request.POST.get('amenities')
        operating_hours_json = request.POST.get('operating_hours')  # Add operating hours
        
        # Validate required fields
        if not all([name, description, city_id, address, sport_type_id, 
                   playground_type, capacity, price_per_hour]):
            return JsonResponse({
                'error': 'Please fill all required fields'
            }, status=400)
        
        # Parse amenities
        amenities = []
        if amenities_json:
            try:
                amenities = json.loads(amenities_json)
            except json.JSONDecodeError:
                amenities = []
        
        # Parse operating hours
        operating_hours = None
        if operating_hours_json:
            try:
                operating_hours = json.loads(operating_hours_json)
            except json.JSONDecodeError:
                operating_hours = None
        
        # Get related objects
        try:
            city = City.objects.get(id=city_id)
            sport_type = SportType.objects.get(id=sport_type_id)
        except (City.DoesNotExist, SportType.DoesNotExist):
            return JsonResponse({
                'error': 'Invalid city or sport type selected'
            }, status=400)
        
        # Create playground
        playground = Playground.objects.create(
            owner=request.user,
            name=name,
            description=description,
            city=city,
            address=address,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            playground_type=playground_type,
            capacity=int(capacity),
            size=size or '',
            price_per_hour=float(price_per_hour),
            price_per_day=float(price_per_day) if price_per_day else None,
            phone_number=phone_number or '',
            whatsapp_number=whatsapp_number or '',
            google_maps_url=google_maps_url or '',
            amenities=amenities,
            operating_hours=operating_hours,  # Add operating hours to creation
            status='pending'  # Always pending for admin approval
        )
        
        # Add sport type
        playground.sport_types.add(sport_type)
        
        # Handle main image upload
        main_image = request.FILES.get('main_image')
        if main_image:
            playground.main_image = main_image
            playground.save()
        
        # Handle gallery images
        gallery_images = request.FILES.getlist('gallery_images')
        for image_file in gallery_images:
            PlaygroundImage.objects.create(
                playground=playground,
                image=image_file
            )
        
        # Generate time slots based on operating hours
        if operating_hours:
            slots_created = generate_time_slots_for_playground(playground)
            print(f"Generated {slots_created} time slots for playground: {playground.name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Playground created successfully and submitted for approval',
            'playground_id': playground.id,
            'slots_generated': bool(operating_hours)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_playground_details(request, playground_id):
    """Get detailed information about a specific playground"""
    try:
        playground = Playground.objects.select_related(
            'city__state__country', 'owner'
        ).prefetch_related(
            'sport_types', 'images'
        ).get(id=playground_id, owner=request.user)
        
        data = {
            'playground': {
                'id': playground.id,
                'name': playground.name,
                'description': playground.description,
                'status': playground.status,
                'address': playground.address,
                'latitude': float(playground.latitude) if playground.latitude else None,
                'longitude': float(playground.longitude) if playground.longitude else None,
                'rating': float(playground.rating) if playground.rating else 0.0,
                'price_per_hour': float(playground.price_per_hour),
                'price_per_day': float(playground.price_per_day) if playground.price_per_day else None,
                'capacity': playground.capacity,
                'size': playground.size,
                'playground_type': playground.playground_type,
                'phone_number': playground.phone_number,
                'whatsapp_number': playground.whatsapp_number,
                'google_maps_url': playground.google_maps_url,
                'main_image': playground.main_image.url if playground.main_image else None,
                'total_bookings': playground.total_bookings,
                'review_count': playground.review_count,
                'amenities': playground.amenities,
                'city': {
                    'id': playground.city.id,
                    'name': playground.city.name,
                    'state': {
                        'id': playground.city.state.id,
                        'name': playground.city.state.name,
                        'country': {
                            'id': playground.city.state.country.id,
                            'name': playground.city.state.country.name
                        }
                    }
                },
                'sport_types': [
                    {
                        'id': sport.id,
                        'name': sport.name,
                        'icon': sport.icon
                    }
                    for sport in playground.sport_types.all()
                ],
                'images': [
                    {
                        'id': image.id,
                        'image': image.image.url,
                        'caption': image.caption,
                        'is_primary': image.is_primary
                    }
                    for image in playground.images.all()
                ],
                'created_at': playground.created_at.isoformat(),
                'updated_at': playground.updated_at.isoformat()
            }
        }
        return JsonResponse(data)
        
    except Playground.DoesNotExist:
        return JsonResponse({'error': 'Playground not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_playground(request, playground_id):
    """Delete a playground (only if owned by current user)"""
    try:
        playground = Playground.objects.get(id=playground_id, owner=request.user)
        playground_name = playground.name
        playground.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Playground "{playground_name}" deleted successfully'
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({'error': 'Playground not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def generate_time_slots_for_playground(playground):
    """Generate TimeSlot database records based on operating hours"""
    try:
        if not playground.operating_hours:
            print("No operating hours found, cannot generate slots")
            return 0
        
        slots_created = 0
        print(f"Starting slot generation for playground: {playground.name}")
        print(f"Operating hours: {playground.operating_hours}")
        
        for day_name, hours in playground.operating_hours.items():
            if not hours.get('is_open', False):
                continue
                
            opening_time = hours.get('opening_time')
            closing_time = hours.get('closing_time')
            
            if not opening_time or not closing_time:
                continue
            
            print(f"Processing day: {day_name}, hours: {hours}")
            
            # Parse times
            try:
                opening_hour, opening_minute = map(int, opening_time.split(':'))
                closing_hour, closing_minute = map(int, closing_time.split(':'))
            except ValueError:
                print(f"Invalid time format for {day_name}")
                continue
            
            # Create datetime objects for calculation
            base_date = datetime(2023, 1, 1)  # Arbitrary date for time calculation
            opening_datetime = base_date.replace(hour=opening_hour, minute=opening_minute)
            closing_datetime = base_date.replace(hour=closing_hour, minute=closing_minute)
            
            print(f"  {day_name}: {opening_datetime.time()} - {closing_datetime.time()}")
            
            # Generate hourly slots
            current_time = opening_datetime
            while current_time < closing_datetime:
                slot_end = current_time + timedelta(hours=1)
                
                # Don't create slot if it would go beyond closing time
                if slot_end > closing_datetime:
                    slot_end = closing_datetime
                
                if current_time >= slot_end:
                    break
                
                # Create or get time slot
                time_slot, created = TimeSlot.objects.get_or_create(
                    playground=playground,
                    day_of_week=day_name,
                    start_time=current_time.time(),
                    end_time=slot_end.time(),
                    defaults={
                        'price': playground.price_per_hour,
                        'is_available': True
                    }
                )
                
                if created:
                    slots_created += 1
                    print(f"    Created slot: {current_time.time()} - {slot_end.time()}")
                
                current_time = slot_end
        
        print(f"Generated {slots_created} time slots for playground: {playground.name}")
        
        # Verify total slots in database
        total_slots = TimeSlot.objects.filter(playground=playground).count()
        print(f"Total slots in database for this playground: {total_slots}")
        
        return slots_created
        
    except Exception as e:
        print(f"Error generating time slots: {e}")
        return 0
