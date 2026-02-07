from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal
from rest_framework.views import APIView
import json
import uuid
import os
from .models import (
    Country, State, City, SportType, Playground, TimeSlot, 
    PlaygroundImage, PlaygroundVideo, PlaygroundAvailability,
    PlaygroundType, Amenity
)

class CountriesAPIView(View):
    """API to get all active countries"""
    def get(self, request):
        countries = Country.objects.filter(is_active=True).values('id', 'name', 'code')
        return JsonResponse({
            'success': True,
            'countries': list(countries)
        })

class StatesAPIView(View):
    """API to get states for a specific country"""
    def get(self, request, country_id=None):
        # Support both URL parameter and query parameter
        if country_id is None:
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

class CitiesAPIView(View):
    """API to get cities for a specific state"""
    def get(self, request, state_id=None):
        # Support both URL parameter and query parameter
        if state_id is None:
            state_id = request.GET.get('state_id')
            
        if not state_id:
            return JsonResponse({
                'success': False,
                'error': 'State ID is required'
            })
            
        cities = City.objects.filter(
            state_id=state_id, 
            is_active=True
        ).values('id', 'name', 'latitude', 'longitude')
        return JsonResponse({
            'success': True,
            'cities': list(cities)
        })

class SportTypesAPIView(View):
    """API to get all active sport types"""
    def get(self, request):
        sport_types = SportType.objects.filter(is_active=True).values(
            'id', 'name', 'icon', 'description'
        )
        return JsonResponse({
            'success': True,
            'sport_types': list(sport_types)
        })

@method_decorator(csrf_exempt, name='dispatch')
class GenerateTimeSlotsAPIView(View):
    """API to generate time slots based on parameters"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            start_time = datetime.strptime(data.get('start_time', '06:00'), '%H:%M').time()
            end_time = datetime.strptime(data.get('end_time', '22:00'), '%H:%M').time()
            slot_duration = int(data.get('slot_duration', 60))  # minutes
            break_duration = int(data.get('break_duration', 15))  # minutes between slots
            selected_days = data.get('selected_days', [])
            
            if not selected_days:
                return JsonResponse({
                    'success': False,
                    'error': 'Please select at least one day'
                })
            
            slots = []
            
            for day in selected_days:
                current_time = datetime.combine(datetime.today(), start_time)
                end_datetime = datetime.combine(datetime.today(), end_time)
                
                while current_time < end_datetime:
                    slot_end = current_time + timedelta(minutes=slot_duration)
                    
                    if slot_end.time() <= end_time:
                        slots.append({
                            'day': day,
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': slot_end.strftime('%H:%M'),
                            'duration': slot_duration,
                            'break_duration': break_duration,
                            'id': f"{day}_{current_time.strftime('%H%M')}_{slot_end.strftime('%H%M')}",
                            'price': 0  # Will be calculated based on base hourly rate
                        })
                    
                    # Add break time before next slot
                    current_time = slot_end + timedelta(minutes=break_duration)
            
            return JsonResponse({
                'success': True,
                'slots': slots,
                'total_slots': len(slots),
                'days_count': len(selected_days),
                'message': f'Generated {len(slots)} slots across {len(selected_days)} days'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error generating slots: {str(e)}'
            })

@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadAPIView(LoginRequiredMixin, View):
    """API for uploading images with preview"""
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('image')
            image_type = request.POST.get('type', 'gallery')  # 'cover', 'gallery'
            
            if not uploaded_file:
                return JsonResponse({
                    'success': False,
                    'error': 'No image file provided'
                })
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if uploaded_file.content_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid file type. Only JPEG, PNG, and WebP are allowed.'
                })
            
            # Validate file size (max 5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': 'File size too large. Maximum 5MB allowed.'
                })
            
            # Generate unique filename
            file_extension = uploaded_file.name.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Save file
            file_path = f"temp_uploads/{image_type}/{unique_filename}"
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            
            return JsonResponse({
                'success': True,
                'file_path': saved_path,
                'file_url': default_storage.url(saved_path),
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'temp_id': str(uuid.uuid4())
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class LocationAPIView(View):
    """Legacy API for location data - kept for compatibility"""
    
    def get(self, request):
        action = request.GET.get('action')
        
        if action == 'countries':
            countries = Country.objects.filter(is_active=True).values('id', 'name', 'code')
            return JsonResponse({'countries': list(countries)})
        
        elif action == 'states':
            country_id = request.GET.get('country_id')
            if country_id:
                states = State.objects.filter(
                    country_id=country_id, 
                    is_active=True
                ).values('id', 'name')
                return JsonResponse({'states': list(states)})
        
        elif action == 'cities':
            state_id = request.GET.get('state_id')
            if state_id:
                cities = City.objects.filter(
                    state_id=state_id, 
                    is_active=True
                ).values('id', 'name', 'latitude', 'longitude')
                return JsonResponse({'cities': list(cities)})
        
        elif action == 'sports':
            sports = SportType.objects.filter(is_active=True).values('id', 'name', 'icon', 'description')
            return JsonResponse({'sports': list(sports)})
        
        return JsonResponse({'error': 'Invalid action'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class CurrencyAPIView(View):
    """API for currency and settings data"""
    
    def get(self, request):
        # Default currency settings - this will be configurable from admin panel later
        currency_data = {
            'success': True,
            'default_currency': 'USD',
            'symbol': '$',
            'position': 'before',  # before or after the amount
            'decimal_places': 2,
            'thousands_separator': ',',
            'decimal_separator': '.',
            'supported_currencies': [
                {'code': 'USD', 'symbol': '$', 'name': 'US Dollar'},
                {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
                {'code': 'GBP', 'symbol': '£', 'name': 'British Pound'},
                {'code': 'BDT', 'symbol': '৳', 'name': 'Bangladeshi Taka'},
                {'code': 'INR', 'symbol': '₹', 'name': 'Indian Rupee'},
                {'code': 'CAD', 'symbol': 'C$', 'name': 'Canadian Dollar'},
                {'code': 'AUD', 'symbol': 'A$', 'name': 'Australian Dollar'},
            ]
        }
        return JsonResponse(currency_data)


@method_decorator(csrf_exempt, name='dispatch')
class SaveDraftAPIView(LoginRequiredMixin, View):
    """API to save form drafts for auto-save functionality"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # For now, store in session (can be moved to database later)
            request.session['playground_draft'] = {
                'form_data': data,
                'saved_at': timezone.now().isoformat(),
                'current_step': data.get('current_step', 1)
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Draft saved successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class PlaygroundPreviewAPIView(View):
    """API for generating playground preview data"""
    
    def post(self, request):
        try:
            # Handle both form data and JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = dict(request.POST)
                # Convert single-item lists to values
                for key, value in data.items():
                    if isinstance(value, list) and len(value) == 1:
                        data[key] = value[0]
            
            # Safely get numeric values with defaults
            price_per_hour = float(data.get('price_per_hour', 0) or 0)
            capacity = int(data.get('capacity', 1) or 1)
            
            # Validate required fields
            playground_name = data.get('name', '').strip()
            if not playground_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Playground name is required'
                })
            
            # Estimate daily bookings (assuming 60% occupancy)
            operating_hours = 16  # Default 6 AM to 10 PM
            estimated_daily_bookings = operating_hours * 0.6
            daily_revenue = price_per_hour * estimated_daily_bookings
            monthly_revenue = daily_revenue * 30
            
            # Calculate completeness percentage
            required_fields = ['name', 'description', 'address', 'price_per_hour', 'capacity']
            completed_fields = sum(1 for field in required_fields if data.get(field))
            completeness = (completed_fields / len(required_fields)) * 100
            
            # Count facilities
            amenities = data.get('amenities', [])
            facility_count = len(amenities) if isinstance(amenities, list) else 0
            
            preview_data = {
                'daily_revenue': round(daily_revenue, 2),
                'monthly_revenue': round(monthly_revenue, 2),
                'completeness': round(completeness),
                'facility_count': facility_count,
                'estimated_bookings': round(estimated_daily_bookings),
                'preview_html': self.generate_preview_html(data)
            }
            
            return JsonResponse(preview_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def generate_preview_html(self, data):
        """Generate HTML preview of the playground"""
        name = data.get('name', 'Playground Name')
        description = data.get('description', 'No description provided')
        price = data.get('price_per_hour', 0)
        capacity = data.get('capacity', 0)
        sport_types = data.get('sport_types', [])
        playground_type = data.get('playground_type', 'outdoor')
        
        sport_badges = ''
        if sport_types:
            for sport in sport_types:
                sport_badges += f'<span class="bg-emerald-500/20 text-emerald-300 px-2 py-1 rounded-full text-xs">{sport}</span>'
        
        html = f"""
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-600">
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h3 class="text-xl font-bold text-white">{name}</h3>
                    <p class="text-gray-400 capitalize">{playground_type} Playground</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold text-emerald-400">${price}/hr</div>
                    <div class="text-gray-400 text-sm">Up to {capacity} players</div>
                </div>
            </div>
            
            <p class="text-gray-300 text-sm mb-4">{description[:100]}...</p>
            
            <div class="flex flex-wrap gap-2 mb-4">
                {sport_badges}
            </div>
            
            <div class="flex items-center justify-between pt-4 border-t border-gray-600">
                <div class="flex items-center gap-4">
                    <span class="text-emerald-400"><i class="fas fa-star"></i> New</span>
                    <span class="text-gray-400"><i class="fas fa-users"></i> 0 bookings</span>
                </div>
                <button class="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg transition-colors">
                    Preview Booking
                </button>
            </div>
        </div>
        """
        return html

@method_decorator(csrf_exempt, name='dispatch')
class AmenitiesAPIView(View):
    """API for managing playground amenities/facilities"""
    
    def get(self, request):
        """Get amenities - either all available amenities or specific playground amenities"""
        try:
            playground_id = request.GET.get('playground_id')
            
            if playground_id:
                # Get specific playground amenities
                try:
                    from .models import Playground
                    playground = Playground.objects.get(id=playground_id)
                    
                    # Parse the amenities JSON field
                    amenities_list = []
                    if playground.amenities:
                        if isinstance(playground.amenities, list):
                            amenities_list = playground.amenities
                        elif isinstance(playground.amenities, str):
                            import json
                            try:
                                amenities_list = json.loads(playground.amenities)
                            except json.JSONDecodeError:
                                amenities_list = []
                    
                    # Format amenities for display
                    formatted_amenities = []
                    for amenity in amenities_list:
                        if isinstance(amenity, dict):
                            formatted_amenities.append({
                                'id': amenity.get('name', '').lower().replace(' ', '_'),
                                'name': amenity.get('name', 'Unknown Amenity'),
                                'description': amenity.get('description', ''),
                                'type': amenity.get('type', 'free'),
                                'price': amenity.get('price'),
                                'icon': amenity.get('icon', '⭐'),
                                'category': 'custom' if amenity.get('type') == 'paid' else 'basic'
                            })
                        elif isinstance(amenity, str):
                            # Handle simple string amenities
                            formatted_amenities.append({
                                'id': amenity.lower().replace(' ', '_'),
                                'name': amenity,
                                'description': '',
                                'type': 'free',
                                'price': None,
                                'icon': self.get_default_icon(amenity),
                                'category': 'basic'
                            })
                    
                    return JsonResponse({
                        'success': True,
                        'amenities': formatted_amenities,
                        'playground_id': playground_id,
                        'total_count': len(formatted_amenities)
                    })
                    
                except Playground.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Playground not found'
                    }, status=404)
            
            # Default amenities categories that playground owners can choose from
            amenities_data = {
                'facility_groups': [
                    {
                        'id': 'basic_facilities',
                        'name': '🏢 Basic Facilities',
                        'amenities': [
                            {'id': 'changing_rooms', 'name': '🚿 Changing Rooms & Lockers', 'description': 'Clean changing rooms with secure lockers'},
                            {'id': 'restrooms', 'name': '🚻 Clean Restroom Facilities', 'description': 'Well-maintained restroom facilities'},
                            {'id': 'first_aid', 'name': '🏥 First Aid Station', 'description': 'On-site first aid station with trained staff'},
                            {'id': 'drinking_water', 'name': '💧 Drinking Water', 'description': 'Clean drinking water stations'},
                        ]
                    },
                    {
                        'id': 'convenience',
                        'name': '🛒 Convenience',
                        'amenities': [
                            {'id': 'parking', 'name': '🚗 Free Parking', 'description': 'Complimentary parking spaces for visitors'},
                            {'id': 'food_court', 'name': '🍕 Food Court & Refreshments', 'description': 'On-site dining and refreshment options'},
                            {'id': 'wifi', 'name': '📶 Free WiFi', 'description': 'High-speed internet access'},
                            {'id': 'valet_parking', 'name': '🚘 Valet Parking', 'description': 'Premium valet parking service'},
                        ]
                    },
                    {
                        'id': 'equipment',
                        'name': '⚙️ Equipment & Technology',
                        'amenities': [
                            {'id': 'lighting', 'name': '💡 Professional Lighting', 'description': 'High-quality lighting for evening play'},
                            {'id': 'scoreboard', 'name': '📊 Electronic Scoreboard', 'description': 'Digital scoreboard system'},
                            {'id': 'sound', 'name': '🔊 Professional Sound System', 'description': 'High-quality audio system'},
                            {'id': 'air_conditioning', 'name': '❄️ Air Conditioning', 'description': 'Climate-controlled environment'},
                        ]
                    },
                    {
                        'id': 'safety_security',
                        'name': '🛡️ Safety & Security',
                        'amenities': [
                            {'id': 'security', 'name': '🔒 24/7 Security', 'description': 'Round-the-clock security services'},
                            {'id': 'accessibility', 'name': '♿ Wheelchair Accessible', 'description': 'Fully accessible for people with disabilities'},
                            {'id': 'cctv', 'name': '📹 CCTV Surveillance', 'description': 'Comprehensive security camera coverage'},
                            {'id': 'emergency_exits', 'name': '🚪 Emergency Exits', 'description': 'Clearly marked emergency exit routes'},
                        ]
                    },
                    {
                        'id': 'services',
                        'name': '🎯 Professional Services',
                        'amenities': [
                            {'id': 'equipment_rental', 'name': '⚽ Equipment Rental', 'description': 'Sports equipment available for rent'},
                            {'id': 'coaching', 'name': '👨‍🏫 Professional Coaching', 'description': 'Certified coaches available for training'},
                            {'id': 'referee', 'name': '🦓 Referee Services', 'description': 'Professional referees for competitive games'},
                            {'id': 'photography', 'name': '📸 Photography Services', 'description': 'Professional event photography'},
                        ]
                    },
                    {
                        'id': 'premium',
                        'name': '✨ Premium Features',
                        'amenities': [
                            {'id': 'vip_lounge', 'name': '👑 VIP Lounge', 'description': 'Exclusive lounge area for premium guests'},
                            {'id': 'spa_services', 'name': '🧖‍♀️ Spa & Wellness', 'description': 'Relaxation and wellness services'},
                            {'id': 'conference_room', 'name': '🏢 Conference Facilities', 'description': 'Meeting rooms for corporate events'},
                            {'id': 'live_streaming', 'name': '📺 Live Streaming Setup', 'description': 'Professional streaming equipment'},
                        ]
                    }
                ]
            }
            
            return JsonResponse({
                'success': True,
                'amenities': amenities_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Allow playground owners to create custom amenities"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            category = data.get('category', 'custom')
            icon = data.get('icon', '🎯')
            amenity_type = data.get('type', 'free')
            price = float(data.get('price', 0)) if data.get('price') else 0
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'Amenity name is required'
                })
            
            # Validate price for paid amenities
            if amenity_type == 'paid' and price <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Price must be greater than 0 for paid amenities'
                })
            
            # Create amenity in database if user is authenticated
            if request.user.is_authenticated:
                try:
                    # Create custom amenity
                    custom_amenity = Amenity.objects.create(
                        name=f"{icon} {name}" if icon else name,
                        description=description,
                        icon=icon,
                        amenity_type=amenity_type,
                        price=price,
                        is_active=True
                    )
                    
                    amenity_data = {
                        'id': f"custom_{custom_amenity.id}",
                        'name': custom_amenity.name,
                        'description': custom_amenity.description,
                        'category': category,
                        'type': amenity_type,
                        'price': float(custom_amenity.price),
                        'icon': icon,
                        'is_custom': True,
                        'created_by': request.user.id,
                        'created_at': custom_amenity.created_at.isoformat()
                    }
                    
                    return JsonResponse({
                        'success': True,
                        'amenity': amenity_data,
                        'message': 'Custom amenity created successfully!'
                    })
                    
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Database error: {str(e)}'
                    }, status=500)
            
            else:
                # For non-authenticated users, store in session temporarily
                if 'custom_amenities' not in request.session:
                    request.session['custom_amenities'] = []
                
                custom_amenity = {
                    'id': f"temp_custom_{len(request.session['custom_amenities']) + 1}",
                    'name': f"{icon} {name}" if icon else name,
                    'description': description,
                    'category': category,
                    'type': amenity_type,
                    'price': price,
                    'icon': icon,
                    'is_custom': True,
                    'created_by': None,
                    'created_at': timezone.now().isoformat()
                }
                
                request.session['custom_amenities'].append(custom_amenity)
                request.session.modified = True
                
                return JsonResponse({
                    'success': True,
                    'amenity': custom_amenity,
                    'message': 'Custom amenity created successfully!'
                })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def get_default_icon(self, amenity_name):
        """Get default icon for amenity based on name"""
        name = amenity_name.lower()
        icon_map = {
            'wifi': '📶',
            'parking': '🚗',
            'restroom': '🚻',
            'toilet': '🚻',
            'lighting': '💡',
            'light': '💡',
            'security': '🛡️',
            'equipment': '⚽',
            'locker': '🔒',
            'shower': '🚿',
            'cafeteria': '🍽️',
            'food': '🍽️',
            'first aid': '🏥',
            'medical': '🏥',
            'water': '💧',
            'drink': '💧',
            'air conditioning': '❄️',
            'ac': '❄️',
            'sound': '🔊',
            'audio': '🔊',
            'scoreboard': '📊',
            'score': '📊',
            'changing': '🚿',
            'change': '🚿'
        }
        
        for keyword, icon in icon_map.items():
            if keyword in name:
                return icon
        
        return '⭐'  # Default icon

@method_decorator(csrf_exempt, name='dispatch')
class PlaygroundTypesAPIView(View):
    """API to get playground types"""
    def get(self, request):
        try:
            playground_types = PlaygroundType.objects.filter(is_active=True).values(
                'id', 'name', 'icon', 'description'
            )
            
            return JsonResponse({
                'success': True,
                'playground_types': list(playground_types)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ValidateTimeSlotsAPIView(View):
    """API to validate time slots"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            slots = data.get('slots', [])
            playground_id = data.get('playground_id')
            
            # Validate each slot
            validated_slots = []
            errors = []
            
            for slot in slots:
                slot_errors = []
                
                # Validate time format
                try:
                    start_time = datetime.strptime(slot.get('start_time', ''), '%H:%M').time()
                    end_time = datetime.strptime(slot.get('end_time', ''), '%H:%M').time()
                    
                    if start_time >= end_time:
                        slot_errors.append('End time must be after start time')
                        
                except ValueError:
                    slot_errors.append('Invalid time format')
                
                # Check for overlapping slots
                for existing_slot in validated_slots:
                    existing_start = datetime.strptime(existing_slot['start_time'], '%H:%M').time()
                    existing_end = datetime.strptime(existing_slot['end_time'], '%H:%M').time()
                    
                    if (start_time < existing_end and end_time > existing_start):
                        slot_errors.append('Time slot overlaps with another slot')
                        break
                
                if slot_errors:
                    errors.extend(slot_errors)
                else:
                    validated_slots.append(slot)
            
            return JsonResponse({
                'success': len(errors) == 0,
                'validated_slots': validated_slots,
                'errors': errors,
                'total_slots': len(validated_slots)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class CheckAvailabilityAPIView(View):
    """API to check real-time availability of time slots"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            playground_id = data.get('playground_id')
            date = data.get('date')
            time_slots = data.get('time_slots', [])
            
            if not playground_id or not date:
                return JsonResponse({
                    'success': False,
                    'error': 'Playground ID and date are required'
                })
            
            # Convert date string to date object
            check_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Get existing bookings for this date
            from bookings.models import Booking
            existing_bookings = Booking.objects.filter(
                playground_id=playground_id,
                date=check_date,
                status__in=['confirmed', 'pending']
            ).values('start_time', 'end_time')
            
            # Check availability for each slot
            available_slots = []
            
            for slot in time_slots:
                start_time = datetime.strptime(slot.get('start_time', ''), '%H:%M').time()
                end_time = datetime.strptime(slot.get('end_time', ''), '%H:%M').time()
                
                is_available = True
                for booking in existing_bookings:
                    if (start_time < booking['end_time'] and end_time > booking['start_time']):
                        is_available = False
                        break
                
                slot_data = {
                    'start_time': slot.get('start_time'),
                    'end_time': slot.get('end_time'),
                    'available': is_available,
                    'price': slot.get('price', 0),
                    'id': slot.get('id', f"{slot.get('start_time')}_{slot.get('end_time')}")
                }
                
                available_slots.append(slot_data)
            
            return JsonResponse({
                'success': True,
                'date': date,
                'playground_id': playground_id,
                'slots': available_slots,
                'total_available': sum(1 for slot in available_slots if slot['available'])
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class VideoUploadAPIView(LoginRequiredMixin, View):
    """API for validating and processing video URLs"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            video_url = data.get('video_url', '').strip()
            
            if not video_url:
                return JsonResponse({
                    'success': False,
                    'error': 'Video URL is required'
                })
            
            # Validate YouTube URL and extract video ID
            import re
            youtube_patterns = [
                r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
                r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
                r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)'
            ]
            
            video_id = None
            for pattern in youtube_patterns:
                match = re.search(pattern, video_url)
                if match:
                    video_id = match.group(1)
                    break
            
            if not video_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid YouTube URL format'
                })
            
            # Generate embed URL
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            return JsonResponse({
                'success': True,
                'video_id': video_id,
                'embed_url': embed_url,
                'thumbnail_url': thumbnail_url,
                'original_url': video_url
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class ValidateFieldAPIView(View):
    """API for real-time field validation"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            field_name = data.get('field_name')
            field_value = data.get('field_value')
            
            errors = []
            
            if field_name == 'name':
                if not field_value or len(field_value.strip()) < 3:
                    errors.append('Playground name must be at least 3 characters long')
                elif len(field_value) > 200:
                    errors.append('Playground name cannot exceed 200 characters')
                    
            elif field_name == 'description':
                if not field_value or len(field_value.strip()) < 50:
                    errors.append('Description must be at least 50 characters long')
                elif len(field_value) > 2000:
                    errors.append('Description cannot exceed 2000 characters')
                    
            elif field_name == 'price_per_hour':
                try:
                    price = float(field_value)
                    if price <= 0:
                        errors.append('Price must be greater than 0')
                    elif price > 1000:
                        errors.append('Price seems unusually high. Please verify.')
                except (ValueError, TypeError):
                    errors.append('Please enter a valid price')
                    
            elif field_name == 'capacity':
                try:
                    capacity = int(field_value)
                    if capacity <= 0:
                        errors.append('Capacity must be greater than 0')
                    elif capacity > 1000:
                        errors.append('Capacity seems unusually high. Please verify.')
                except (ValueError, TypeError):
                    errors.append('Please enter a valid capacity number')
            
            return JsonResponse({
                'success': len(errors) == 0,
                'errors': errors,
                'field_name': field_name
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class CheckNameAvailabilityAPIView(View):
    """API to check playground name availability"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            city_id = data.get('city_id')
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'Name is required'
                })
            
            # Check if playground with same name exists in same city
            existing_playground = Playground.objects.filter(
                name__iexact=name,
                city_id=city_id
            ).exists()
            
            is_available = not existing_playground
            
            return JsonResponse({
                'success': True,
                'available': is_available,
                'message': 'Name is available' if is_available else 'A playground with this name already exists in this city'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')  
class LoadDraftAPIView(LoginRequiredMixin, View):
    """API to load saved draft data"""
    def get(self, request):
        try:
            draft_data = request.session.get('playground_draft')
            
            if not draft_data:
                return JsonResponse({
                    'success': False,
                    'message': 'No draft found'
                })
            
            return JsonResponse({
                'success': True,
                'draft': draft_data,
                'has_draft': True
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class PlaygroundTypesAPIView(View):
    """API to get all active playground types"""
    def get(self, request):
        try:
            playground_types = PlaygroundType.objects.filter(is_active=True).values(
                'id', 'name', 'icon', 'description'
            )
            return JsonResponse({
                'success': True,
                'playground_types': list(playground_types)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class ValidateTimeSlotsAPIView(View):
    """API to validate generated time slots"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            time_slots = data.get('time_slots', [])
            
            if not time_slots:
                return JsonResponse({
                    'success': False,
                    'error': 'No time slots provided'
                })
            
            # Validate each slot
            validated_slots = []
            conflicts = []
            
            for slot in time_slots:
                # Check for overlapping slots
                start_time = slot.get('start_time')
                end_time = slot.get('end_time')
                
                # Basic validation
                if not start_time or not end_time:
                    conflicts.append(f"Invalid time slot: {slot}")
                    continue
                
                validated_slots.append(slot)
            
            return JsonResponse({
                'success': True,
                'validated_slots': validated_slots,
                'conflicts': conflicts,
                'total_valid': len(validated_slots)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class CheckAvailabilityAPIView(View):
    """API to check real-time availability for time slots"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            date = data.get('date')
            playground_id = data.get('playground_id')
            time_slots = data.get('time_slots', [])
            
            if not date or not time_slots:
                return JsonResponse({
                    'success': False,
                    'error': 'Date and time slots are required'
                })
            
            # For preview mode, simulate availability
            if playground_id == 'preview':
                availability_slots = []
                for slot in time_slots:
                    # Simulate some slots as booked for demo
                    import random
                    is_available = random.choice([True, True, True, False])  # 75% available
                    
                    availability_slots.append({
                        'id': slot.get('id'),
                        'start_time': slot.get('start_time'),
                        'end_time': slot.get('end_time'),
                        'price': slot.get('price', 25.00),
                        'available': is_available
                    })
                
                return JsonResponse({
                    'success': True,
                    'slots': availability_slots,
                    'date': date
                })
            
            # For actual playgrounds, check database
            # This would check against actual bookings
            return JsonResponse({
                'success': True,
                'slots': [],
                'message': 'Real-time availability checking not yet implemented for live playgrounds'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@method_decorator(csrf_exempt, name='dispatch')
class PlaygroundCreateAPIView(LoginRequiredMixin, View):
    """API to create a new playground"""
    def post(self, request):
        try:
            # Get form data
            name = request.POST.get('name')
            description = request.POST.get('description')
            playground_type = request.POST.get('playground_type')
            capacity = request.POST.get('capacity')
            price_per_hour = request.POST.get('price_per_hour')
            
            # Location data
            country = request.POST.get('country')
            state = request.POST.get('state')
            city = request.POST.get('city')
            address = request.POST.get('address')
            
            # Time and booking settings
            opening_time = request.POST.get('opening_time')
            closing_time = request.POST.get('closing_time')
            advance_booking_days = request.POST.get('advance_booking_days', 30)
            
            # JSON data
            time_slots_json = request.POST.get('time_slots', '[]')
            cover_images_json = request.POST.get('cover_images', '[]')
            gallery_images_json = request.POST.get('gallery_images', '[]')
            selected_amenities_json = request.POST.get('selected_amenities', '[]')
            
            # Parse JSON data
            try:
                time_slots = json.loads(time_slots_json)
                cover_images = json.loads(cover_images_json)
                gallery_images = json.loads(gallery_images_json)
                selected_amenities = json.loads(selected_amenities_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data provided'
                })
            
            # Validate required fields
            if not all([name, description, playground_type, capacity, price_per_hour, city, address]):
                return JsonResponse({
                    'success': False,
                    'error': 'All required fields must be filled',
                    'errors': {
                        'name': ['Name is required'] if not name else [],
                        'description': ['Description is required'] if not description else [],
                        'playground_type': ['Playground type is required'] if not playground_type else [],
                        'capacity': ['Capacity is required'] if not capacity else [],
                        'price_per_hour': ['Price per hour is required'] if not price_per_hour else [],
                        'city': ['City is required'] if not city else [],
                        'address': ['Address is required'] if not address else [],
                    }
                })
            
            # Get city object
            try:
                city_obj = City.objects.get(id=city)
            except City.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid city selected'
                })
            
            # Create playground
            playground = Playground.objects.create(
                owner=request.user,
                name=name,
                description=description,
                playground_type=playground_type,
                capacity=int(capacity),
                price_per_hour=float(price_per_hour),
                city=city_obj,
                address=address,
                advance_booking_days=int(advance_booking_days),
                operating_hours={
                    'opening_time': opening_time,
                    'closing_time': closing_time
                },
                slot_templates=time_slots,
                amenities=selected_amenities,
                status='pending'  # Pending admin approval
            )
            
            # Add sport types if provided
            sport_types = request.POST.getlist('sport_types')
            if sport_types:
                playground.sport_types.set(sport_types)
            
            # Save images
            if cover_images:
                for img_data in cover_images:
                    if img_data.get('success') and img_data.get('file_path'):
                        PlaygroundImage.objects.create(
                            playground=playground,
                            image=img_data['file_path'],
                            image_type='cover',
                            is_main=cover_images.index(img_data) == 0
                        )
            
            if gallery_images:
                for img_data in gallery_images:
                    if img_data.get('success') and img_data.get('file_path'):
                        PlaygroundImage.objects.create(
                            playground=playground,
                            image=img_data['file_path'],
                            image_type='gallery'
                        )
            
            # Create time slots
            for slot_data in time_slots:
                TimeSlot.objects.create(
                    playground=playground,
                    day_of_week=slot_data.get('day', 'monday'),
                    start_time=slot_data.get('start_time'),
                    end_time=slot_data.get('end_time'),
                    price=slot_data.get('price', playground.price_per_hour),
                    is_active=True
                )
            
            # Clear draft from session
            if 'playground_draft' in request.session:
                del request.session['playground_draft']
            
            return JsonResponse({
                'success': True,
                'message': 'Playground submitted successfully for admin approval',
                'playground_id': playground.id,
                'status': 'pending'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error creating playground: {str(e)}'
            })

@method_decorator(csrf_exempt, name='dispatch')
class ClearDraftAPIView(LoginRequiredMixin, View):
    """API to clear saved draft"""
    def post(self, request):
        try:
            if 'playground_draft' in request.session:
                del request.session['playground_draft']
            
            return JsonResponse({
                'success': True,
                'message': 'Draft cleared successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class PricingCalculatorAPIView(View):
    """API view for calculating optimal pricing and revenue projections"""
    
    @method_decorator(csrf_exempt, name='dispatch')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse JSON data from request body
            if hasattr(request, 'body') and request.body:
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.POST.dict()
            
            # Get pricing data from request
            hourly_price = Decimal(data.get('hourly_price', 0))
            daily_price = Decimal(data.get('daily_price', 0))
            weekly_price = Decimal(data.get('weekly_price', 0))
            monthly_price = Decimal(data.get('monthly_price', 0))
            currency = data.get('currency', 'USD')
            capacity = int(data.get('capacity', 10))
            
            # Calculate smart defaults if any price is missing
            if hourly_price and not daily_price:
                daily_price = hourly_price * 8  # 8 hours = 1 day
            if hourly_price and not weekly_price:
                weekly_price = hourly_price * 50  # 50 hours = 1 week (7 days * ~7 hours)
            if hourly_price and not monthly_price:
                monthly_price = hourly_price * 200  # 200 hours = 1 month
                
            # Calculate utilization rates for each period
            utilization_rates = {
                'hourly': 0.60,  # 60% utilization for hourly bookings
                'daily': 0.70,   # 70% utilization for daily bookings
                'weekly': 0.80,  # 80% utilization for weekly bookings
                'monthly': 0.90  # 90% utilization for monthly bookings
            }
            
            # Calculate booking distribution (percentage of each booking type)
            booking_distribution = {
                'hourly': 0.60,   # 60% of bookings are hourly
                'daily': 0.25,    # 25% of bookings are daily
                'weekly': 0.10,   # 10% of bookings are weekly
                'monthly': 0.05   # 5% of bookings are monthly
            }
            
            # Calculate monthly revenue projections
            monthly_hours = 30 * 12  # 12 hours per day average
            monthly_revenue = {
                'hourly': hourly_price * monthly_hours * utilization_rates['hourly'] * booking_distribution['hourly'],
                'daily': daily_price * 30 * utilization_rates['daily'] * booking_distribution['daily'],
                'weekly': weekly_price * 4 * utilization_rates['weekly'] * booking_distribution['weekly'],
                'monthly': monthly_price * utilization_rates['monthly'] * booking_distribution['monthly']
            }
            
            total_monthly_revenue = sum(monthly_revenue.values())
            
            # Calculate pricing recommendations
            recommendations = []
            
            # Check if pricing is competitive
            if hourly_price < 15:
                recommendations.append({
                    'type': 'warning',
                    'message': f'Hourly rate of {currency}{hourly_price} may be too low. Consider pricing between {currency}15-{currency}30 per hour.'
                })
            elif hourly_price > 100:
                recommendations.append({
                    'type': 'warning',
                    'message': f'Hourly rate of {currency}{hourly_price} may be too high. Consider market research for your area.'
                })
            
            # Suggest discounts for longer bookings
            if daily_price >= hourly_price * 8:
                discount_suggestion = hourly_price * 8 * 0.8  # 20% discount
                recommendations.append({
                    'type': 'suggestion',
                    'message': f'Consider offering daily rate at {currency}{discount_suggestion:.2f} (20% discount) to encourage longer bookings.'
                })
                
            if weekly_price >= daily_price * 7:
                weekly_discount_suggestion = daily_price * 7 * 0.75  # 25% discount
                recommendations.append({
                    'type': 'suggestion',
                    'message': f'Consider offering weekly rate at {currency}{weekly_discount_suggestion:.2f} (25% discount) to encourage weekly bookings.'
                })
            
            # Calculate capacity utilization impact
            capacity_factor = min(capacity / 10, 2.0)  # Scale factor based on capacity
            adjusted_revenue = {
                period: revenue * capacity_factor
                for period, revenue in monthly_revenue.items()
            }
            
            return JsonResponse({
                'success': True,
                'data': {
                    'pricing': {
                        'hourly': float(hourly_price),
                        'daily': float(daily_price),
                        'weekly': float(weekly_price),
                        'monthly': float(monthly_price),
                        'currency': currency
                    },
                    'revenue_projections': {
                        'monthly_breakdown': {
                            period: float(revenue) for period, revenue in monthly_revenue.items()
                        },
                        'total_monthly': float(total_monthly_revenue),
                        'capacity_adjusted': {
                            period: float(revenue) for period, revenue in adjusted_revenue.items()
                        },
                        'total_capacity_adjusted': float(sum(adjusted_revenue.values()))
                    },
                    'utilization_rates': utilization_rates,
                    'booking_distribution': booking_distribution,
                    'recommendations': recommendations,
                    'smart_defaults': {
                        'daily_suggested': float(hourly_price * 8 * 0.8) if hourly_price else 0,
                        'weekly_suggested': float(hourly_price * 50 * 0.75) if hourly_price else 0,
                        'monthly_suggested': float(hourly_price * 200 * 0.7) if hourly_price else 0
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Pricing calculation error: {str(e)}'
            })


class CustomOfferAPIView(View):
    """API view for managing custom offers and packages"""
    
    @method_decorator(csrf_exempt, name='dispatch')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse JSON data from request body
            if hasattr(request, 'body') and request.body:
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.POST.dict()
                
            # Get offer data from request
            offer_type = data.get('offer_type', 'percentage')
            discount_value = Decimal(data.get('discount_value', 0))
            valid_from = data.get('valid_from')
            valid_until = data.get('valid_until')
            conditions = data.get('conditions', {})
            
            # Validate offer data
            if offer_type not in ['percentage', 'fixed', 'package']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid offer type. Must be percentage, fixed, or package.'
                })
                
            if discount_value <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Discount value must be greater than 0.'
                })
                
            # Calculate offer impact
            impact_analysis = {
                'estimated_bookings_increase': 0,
                'revenue_impact': 0,
                'recommended_duration': 'limited_time'
            }
            
            if offer_type == 'percentage':
                if discount_value > 50:
                    impact_analysis['warning'] = 'High discount percentage may significantly impact revenue.'
                impact_analysis['estimated_bookings_increase'] = min(discount_value * 2, 100)  # Max 100% increase
                
            elif offer_type == 'fixed':
                impact_analysis['estimated_bookings_increase'] = min(discount_value, 50)  # Max 50% increase
                
            # Generate offer recommendations
            recommendations = []
            
            if discount_value > 30:
                recommendations.append({
                    'type': 'warning',
                    'message': 'High discount may attract price-sensitive customers but impact profitability.'
                })
                
            if not valid_until:
                recommendations.append({
                    'type': 'suggestion',
                    'message': 'Consider setting an end date to create urgency.'
                })
                
            return JsonResponse({
                'success': True,
                'data': {
                    'offer_validation': {
                        'is_valid': True,
                        'type': offer_type,
                        'discount_value': float(discount_value)
                    },
                    'impact_analysis': impact_analysis,
                    'recommendations': recommendations,
                    'suggested_conditions': {
                        'min_booking_duration': '2_hours',
                        'applicable_periods': ['off_peak', 'weekdays'],
                        'max_uses_per_customer': 5
                    }
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Custom offer error: {str(e)}'
            })


@method_decorator(csrf_exempt, name='dispatch')
class TimeSlotAvailabilityAPIView(View):
    """API for real-time time slot availability checking"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            playground_id = data.get('playground_id')
            date_str = data.get('date')
            is_new_playground = data.get('is_new_playground', True)
            
            if not date_str:
                return JsonResponse({
                    'success': False,
                    'error': 'Date is required'
                })
            
            # Parse the date
            try:
                check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                })
            
            # For new playgrounds, all slots should be available
            if is_new_playground or not playground_id:
                # Generate default available slots for new playground
                available_slots = []
                for hour in range(6, 22):  # 6 AM to 10 PM
                    start_time = time(hour, 0)
                    end_time = time(hour + 1, 0) if hour < 21 else time(22, 0)
                    
                    available_slots.append({
                        'id': f'slot_{hour}',
                        'start_time': start_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'is_available': True,
                        'is_booked': False,
                        'booking_count': 0,
                        'price': 25.0,  # Default price
                        'tier': 'regular' if hour < 18 else 'peak' if hour < 21 else 'premium'
                    })
                
                return JsonResponse({
                    'success': True,
                    'slots': available_slots,
                    'date': date_str,
                    'is_new_playground': True
                })
            
            # For existing playgrounds, check actual availability
            try:
                playground = Playground.objects.get(id=playground_id)
            except Playground.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Playground not found'
                })
            
            # Get time slots for this playground
            time_slots = TimeSlot.objects.filter(
                playground=playground,
                is_active=True
            ).order_by('start_time')
            
            # Check bookings for the specific date
            from bookings.models import Booking  # Import here to avoid circular imports
            
            slot_availability = []
            for slot in time_slots:
                # Count bookings for this slot on the specific date
                booking_count = Booking.objects.filter(
                    playground=playground,
                    date=check_date,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    status__in=['confirmed', 'pending']
                ).count()
                
                # Check if slot is available (not fully booked)
                max_capacity = playground.capacity or 1
                is_available = booking_count < max_capacity
                
                slot_availability.append({
                    'id': slot.id,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'is_available': is_available,
                    'is_booked': not is_available,
                    'booking_count': booking_count,
                    'max_capacity': max_capacity,
                    'price': float(slot.price),
                    'tier': slot.tier if hasattr(slot, 'tier') else 'regular'
                })
            
            return JsonResponse({
                'success': True,
                'slots': slot_availability,
                'date': date_str,
                'playground_id': playground_id,
                'is_new_playground': False
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class SubmissionAPIView(LoginRequiredMixin, View):
    """Enhanced playground submission API with pending status"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['name', 'description', 'price', 'capacity', 'country', 'state', 'city']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                })
            
            # Create playground with pending status
            playground_data = {
                'name': data['name'],
                'description': data['description'],
                'owner': request.user,
                'price_per_hour': Decimal(str(data['price'])),
                'capacity': int(data['capacity']),
                'country_id': data['country'],
                'state_id': data['state'],
                'city_id': data['city'],
                'address': data.get('address', ''),
                'status': 'pending',  # Set status to pending for admin approval
                'created_at': timezone.now(),
                'updated_at': timezone.now(),
            }
            
            # Add playground type if provided
            if data.get('playgroundType'):
                playground_data['playground_type_id'] = data['playgroundType']
            
            # Create the playground
            playground = Playground.objects.create(**playground_data)
            
            # Add sports/activities
            if data.get('sports'):
                sport_ids = [sport['id'] for sport in data['sports'] if sport.get('id')]
                playground.sport_types.set(sport_ids)
            
            # Add amenities
            if data.get('amenities'):
                for amenity in data['amenities']:
                    if amenity.get('name'):
                        amenity_obj, created = Amenity.objects.get_or_create(
                            name=amenity['name'],
                            defaults={
                                'description': amenity.get('description', ''),
                                'category': amenity.get('category', 'custom'),
                                'icon': amenity.get('icon', '⭐')
                            }
                        )
                        playground.amenities.add(amenity_obj)
            
            # Add time slots
            if data.get('timeSlots'):
                for slot_data in data['timeSlots']:
                    try:
                        start_time = datetime.strptime(slot_data['start'], '%H:%M').time()
                        end_time = datetime.strptime(slot_data['end'], '%H:%M').time()
                        
                        TimeSlot.objects.create(
                            playground=playground,
                            start_time=start_time,
                            end_time=end_time,
                            price=playground.price_per_hour,  # Default to base price
                            is_available=True
                        )
                    except (ValueError, KeyError) as e:
                        continue  # Skip invalid time slots
            
            # Generate playground ID for response
            playground_id = f"PG{playground.id}{timezone.now().strftime('%Y%m%d')}"
            
            # Send notification email to admin (optional)
            try:
                self.notify_admin_new_submission(playground)
            except Exception as e:
                pass  # Don't fail if notification fails
            
            return JsonResponse({
                'success': True,
                'message': 'Playground submitted successfully for review',
                'playgroundId': playground_id,
                'status': 'pending',
                'redirectUrl': f'/playgrounds/my-playgrounds/'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Submission failed: {str(e)}'
            })
    
    def notify_admin_new_submission(self, playground):
        """Send notification to admin about new playground submission"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f'New Playground Submission: {playground.name}'
            message = f"""
            A new playground has been submitted for review:
            
            Name: {playground.name}
            Owner: {playground.owner.get_full_name() or playground.owner.username}
            Location: {playground.city.name}, {playground.state.name}, {playground.country.name}
            Submitted: {playground.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}
            
            Please review and approve/reject this submission in the admin panel.
            """
            
            admin_emails = [settings.DEFAULT_FROM_EMAIL]  # Add admin emails here
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True
            )
        except Exception as e:
            pass  # Don't fail if email notification fails
 
