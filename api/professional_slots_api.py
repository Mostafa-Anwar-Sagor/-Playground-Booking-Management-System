from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from playgrounds.models import Playground, TimeSlot, PlaygroundSlot, DurationPass
from bookings.models import Booking

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_today_slots(request, playground_id):
    """
    Get available slots for a playground with 12-hour format and dynamic currency
    Supports date parameter for dynamic date selection
    """
    try:
        playground = get_object_or_404(Playground, id=playground_id)
        
        # Get date from query parameter or use today
        date_param = request.GET.get('date')
        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d')
            except ValueError:
                target_date = timezone.now()
        else:
            target_date = timezone.now()
        
        current_day = target_date.strftime('%A').lower()
        
        # Get ALL regular slots for the specified date - completely dynamic based on what user created
        regular_slots = TimeSlot.objects.filter(
            playground=playground,
            day_of_week=current_day,
            is_available=True
        ).order_by('start_time')
        
        # Note: Custom slots are handled separately in the professional_custom_slots_api
        # and should NOT be included in today's regular slots
        
        # Get playground currency info
        playground_currency = getattr(playground, 'currency', 'BDT')
        currency_symbol = {
            'BDT': '৳',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'MYR': 'RM',  # Malaysian Ringgit
            'SGD': 'S$',  # Singapore Dollar
            'THB': '฿',   # Thai Baht
            'IDR': 'Rp',  # Indonesian Rupiah
            'PHP': '₱',   # Philippine Peso
            'VND': '₫',   # Vietnamese Dong
            'KRW': '₩',   # South Korean Won
            'JPY': '¥',   # Japanese Yen
            'CNY': '¥',   # Chinese Yuan
            'AUD': 'A$',  # Australian Dollar
            'CAD': 'C$',  # Canadian Dollar
            'CHF': 'CHF', # Swiss Franc
            'SEK': 'kr',  # Swedish Krona
            'NOK': 'kr',  # Norwegian Krone
            'DKK': 'kr',  # Danish Krone
            'PLN': 'zł',  # Polish Złoty
            'CZK': 'Kč',  # Czech Koruna
            'HUF': 'Ft',  # Hungarian Forint
            'RUB': '₽',   # Russian Ruble
            'TRY': '₺',   # Turkish Lira
            'ZAR': 'R',   # South African Rand
            'BRL': 'R$',  # Brazilian Real
            'MXN': '$',   # Mexican Peso
            'ARS': '$',   # Argentine Peso
            'CLP': '$',   # Chilean Peso
            'COP': '$',   # Colombian Peso
            'PEN': 'S/',  # Peruvian Sol
            'UYU': '$U',  # Uruguayan Peso
            'EGP': 'E£',  # Egyptian Pound
            'SAR': '﷼',   # Saudi Riyal
            'AED': 'د.إ',  # UAE Dirham
            'QAR': '﷼',   # Qatari Riyal
            'KWD': 'د.ك',  # Kuwaiti Dinar
            'BHD': '.د.ب', # Bahraini Dinar
            'OMR': '﷼',   # Omani Rial
            'JOD': 'د.ا',  # Jordanian Dinar
            'LBP': 'ل.ل',  # Lebanese Pound
            'ILS': '₪',   # Israeli Shekel
            'PKR': '₨',   # Pakistani Rupee
            'LKR': '₨',   # Sri Lankan Rupee
            'NPR': '₨',   # Nepalese Rupee
            'BTN': 'Nu.', # Bhutanese Ngultrum
            'MVR': 'Rf',  # Maldivian Rufiyaa
            'AFN': '؋',   # Afghan Afghani
            'IRR': '﷼',   # Iranian Rial
            'IQD': 'ع.د',  # Iraqi Dinar
            'KZT': '₸',   # Kazakhstani Tenge
            'UZS': 'лв',  # Uzbekistani Som
            'TJS': 'SM',  # Tajikistani Somoni
            'KGS': 'лв',  # Kyrgyzstani Som
            'TMT': 'T',   # Turkmenistani Manat
            'AZN': '₼',   # Azerbaijani Manat
            'GEL': '₾',   # Georgian Lari
            'AMD': '֏',   # Armenian Dram
            'BGN': 'лв',  # Bulgarian Lev
            'RON': 'lei', # Romanian Leu
            'HRK': 'kn',  # Croatian Kuna
            'RSD': 'дин', # Serbian Dinar
            'BAM': 'KM',  # Bosnia and Herzegovina Convertible Mark
            'MKD': 'ден', # Macedonian Denar
            'ALL': 'L',   # Albanian Lek
            'EUR': '€',   # Euro (used by many European countries)
        }.get(playground_currency, '৳')
        
        # Format regular slots with real-time booking status
        regular_slots_data = []
        for slot in regular_slots:
            # Convert to 12-hour format
            start_time_12h = slot.start_time.strftime('%I:%M %p')
            end_time_12h = slot.end_time.strftime('%I:%M %p')
            
            # Check if this slot is booked for the target date
            existing_bookings = Booking.objects.filter(
                playground=playground,
                booking_date=target_date.date(),
                start_time=slot.start_time,
                end_time=slot.end_time,
                status__in=['confirmed', 'pending']  # Consider both confirmed and pending as booked
            ).exists()
            
            # Get effective price and use playground currency
            effective_price = slot.get_effective_price()
            
            # Determine if slot can be booked (not booked and available)
            is_available = slot.is_available and not existing_bookings
            
            regular_slots_data.append({
                'id': slot.id,
                'type': 'regular',
                'day': slot.get_day_of_week_display(),
                'start_time': start_time_12h,
                'end_time': end_time_12h,
                'start_time_24h': slot.start_time.strftime('%H:%M'),
                'end_time_24h': slot.end_time.strftime('%H:%M'),
                'price': float(effective_price),
                'currency': playground_currency,
                'currency_symbol': currency_symbol,
                'formatted_price': f"{currency_symbol} {effective_price}",
                'duration_hours': slot.duration_hours,
                'max_bookings': slot.max_bookings,
                'is_available': is_available,
                'is_booked': existing_bookings,
                'booking_status': 'booked' if existing_bookings else 'available',
                'can_book': is_available
            })
        
        response_data = {
            'success': True,
            'playground_id': playground_id,
            'playground_name': playground.name,
            'selected_date': target_date.strftime('%Y-%m-%d'),
            'selected_day': current_day.title(),
            'current_time': timezone.now().strftime('%I:%M %p'),
            'currency': playground_currency,
            'currency_symbol': currency_symbol,
            'regular_slots': regular_slots_data,
            'total_slots': len(regular_slots_data),
            'has_slots': len(regular_slots_data) > 0
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching today's slots: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch today\'s slots'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def professional_custom_slots_api(request, playground_id):
    """
    Get all custom slots for a playground from database, checking for booking conflicts on selected date
    """
    try:
        playground = get_object_or_404(Playground, id=playground_id)
        
        # Get the selected date from query parameters
        from datetime import datetime, date
        selected_date_str = request.GET.get('date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()
        
        # Get all custom slots
        custom_slots = PlaygroundSlot.objects.filter(
            playground=playground,
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        # Import Booking model for conflict checking
        from bookings.models import Booking
        
        # Format custom slots and check for booking conflicts
        slots_data = []
        for slot in custom_slots:
            # Convert to 12-hour format
            start_time_12h = slot.start_time.strftime('%I:%M %p')
            end_time_12h = slot.end_time.strftime('%I:%M %p')
            
            # Check if this custom slot is already booked on the selected date
            # Look for bookings that indicate custom slot booking and match the slot ID
            # Support both JSON format and old text format
            from django.db.models import Q
            existing_bookings = Booking.objects.filter(
                playground=playground,
                booking_date=selected_date,
                status__in=['confirmed', 'pending']
            ).filter(
                Q(special_requests__icontains=f'Custom Slot Booking (ID: {slot.id})') |  # Old text format
                Q(special_requests__icontains=f'"custom_slot_id": "{slot.id}"') |        # JSON format with space
                Q(special_requests__icontains=f'"custom_slot_id":"{slot.id}"') |         # JSON format without space  
                Q(special_requests__icontains=f'"slot_id": "{slot.id}"') |               # Alternative JSON field with space
                Q(special_requests__icontains=f'"slot_id":"{slot.id}"')                  # Alternative JSON field without space
            )
            
            # Also check for any booking that overlaps with this slot's time on this date
            time_conflicts = Booking.objects.filter(
                playground=playground,
                booking_date=selected_date,
                status__in=['confirmed', 'pending'],
                start_time__lt=slot.end_time,
                end_time__gt=slot.start_time
            )
            
            is_booked = existing_bookings.exists() or time_conflicts.exists()
            
            slots_data.append({
                'id': slot.id,
                'slot_type': slot.get_slot_type_display(),
                'day': slot.get_day_of_week_display(),
                'day_key': slot.day_of_week,
                'start_time': start_time_12h,
                'end_time': end_time_12h,
                'start_time_24h': slot.start_time.strftime('%H:%M'),
                'end_time_24h': slot.end_time.strftime('%H:%M'),
                'price': float(slot.price),
                'currency': slot.currency,
                'formatted_price': f"{slot.currency} {slot.price}",
                'duration_hours': slot.duration_hours,
                'max_capacity': slot.max_capacity,
                'description': slot.description,
                'features': slot.features,
                'is_active': slot.is_active and not is_booked,  # Mark as inactive if booked
                'is_booked': is_booked,
                'can_book': not is_booked,
                'selected_date': selected_date_str,
                'created_at': slot.created_at.isoformat(),
                'updated_at': slot.updated_at.isoformat()
            })
        
        response_data = {
            'success': True,
            'playground_id': playground_id,
            'playground_name': playground.name,
            'custom_slots': slots_data,
            'total_slots': len(slots_data)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching custom slots: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch custom slots'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_slot_types(request):
    """
    Get available slot types
    """
    try:
        slot_types = [
            {'value': 'regular', 'label': 'Regular'},
            {'value': 'premium', 'label': 'Premium'},
            {'value': 'vip', 'label': 'VIP'}
        ]
        
        return JsonResponse({
            'success': True,
            'slot_types': slot_types
        })
        
    except Exception as e:
        logger.error(f"Error fetching slot types: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_currencies(request):
    """
    Get available currencies
    """
    try:
        currencies = [
            {'code': 'BDT', 'name': 'Bangladeshi Taka', 'symbol': '৳'},
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'}
        ]
        
        return JsonResponse({
            'success': True,
            'currencies': currencies
        })
        
    except Exception as e:
        logger.error(f"Error fetching currencies: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_public_playground_details(request, playground_id):
    """
    Get public playground details for checkout and booking purposes
    This endpoint doesn't require ownership - any user can view playground details
    """
    try:
        playground = get_object_or_404(
            Playground.objects.select_related('city__state__country', 'owner')
                               .prefetch_related('sport_types', 'images'),
            id=playground_id
        )
        
        # Get playground currency info
        playground_currency = getattr(playground, 'currency', 'BDT')
        currency_symbol = {
            'BDT': '৳',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'MYR': 'RM',
            'SGD': 'S$',
            'THB': '฿',
            'IDR': 'Rp',
            'PHP': '₱',
            'VND': '₫',
        }.get(playground_currency, '৳')
        
        # Prepare amenities list
        amenities_list = []
        if playground.amenities:
            if isinstance(playground.amenities, str):
                import json
                try:
                    amenities_data = json.loads(playground.amenities)
                    if isinstance(amenities_data, list):
                        amenities_list = amenities_data
                except:
                    amenities_list = playground.amenities.split(',') if playground.amenities else []
            elif isinstance(playground.amenities, list):
                amenities_list = playground.amenities
        
        data = {
            'success': True,
            'playground_id': playground.id,
            'id': playground.id,
            'name': playground.name,
            'description': playground.description or '',
            'address': playground.address or '',
            'latitude': float(playground.latitude) if playground.latitude else None,
            'longitude': float(playground.longitude) if playground.longitude else None,
            'rating': float(playground.rating) if playground.rating else 0.0,
            'price_per_hour': float(playground.price_per_hour),
            'price_per_day': float(playground.price_per_day) if playground.price_per_day else None,
            'capacity': playground.capacity or 0,
            'size': playground.size or '',
            'playground_type': playground.playground_type or '',
            'phone_number': playground.phone_number or '',
            'whatsapp_number': playground.whatsapp_number or '',
            'google_maps_url': playground.google_maps_url or '',
            'main_image': playground.main_image.url if playground.main_image else None,
            'total_bookings': playground.total_bookings or 0,
            'review_count': playground.review_count or 0,
            'amenities': amenities_list,
            'currency': playground_currency,
            'currency_symbol': currency_symbol,
            'owner': {
                'id': playground.owner.id,
                'username': playground.owner.username,
                'first_name': playground.owner.first_name or '',
                'last_name': playground.owner.last_name or '',
            },
            'location': {
                'city': playground.city.name if playground.city else '',
                'state': playground.city.state.name if playground.city and playground.city.state else '',
                'country': playground.city.state.country.name if playground.city and playground.city.state and playground.city.state.country else '',
            },
            'sport_types': [
                {
                    'id': sport.id,
                    'name': sport.name,
                    'description': sport.description or ''
                }
                for sport in playground.sport_types.all()
            ],
            'images': [
                {
                    'id': img.id,
                    'image': img.image.url,
                    'caption': img.caption or '',
                    'is_primary': img.is_primary
                }
                for img in playground.images.all()
            ],
            
            # Dynamic configuration values
            'configuration': {
                'custom_slot_hour': playground.custom_pricing.get('custom_slot_hour', 23) if playground.custom_pricing else 23,
                'membership_pass_hour': playground.custom_pricing.get('membership_pass_hour', 22) if playground.custom_pricing else 22,
                'default_custom_duration': playground.custom_pricing.get('default_custom_duration', 2) if playground.custom_pricing else 2,
                'default_slot_duration': playground.custom_pricing.get('default_slot_duration', 60) if playground.custom_pricing else 60,
                'max_advance_booking_days': playground.advance_booking_days or 30,
                'auto_approval': playground.auto_approval,
                'instant_booking': playground.instant_booking
            }
        }
        
        logger.info(f"Successfully fetched public playground details for ID: {playground_id}")
        return JsonResponse(data)
        
    except Playground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Playground not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching public playground details: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
