from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, Case, When
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date, time
import json

from playgrounds.models import (
    Playground, TimeSlot, PlaygroundImage, Review, 
    Country, State, City, SportType
)
from bookings.models import Booking
from accounts.models import User


# Enhanced API Views for Dynamic Playground Management

@method_decorator(csrf_exempt, name='dispatch')
class PlaygroundAPIView(View):
    """
    Comprehensive API for playground management with real-time features
    """
    
    def get(self, request):
        """Get playgrounds with advanced filtering and real-time data"""
        try:
            user = request.user
            
            # Query parameters
            status = request.GET.get('status', 'all')
            search = request.GET.get('search', '')
            city_id = request.GET.get('city')
            sport_type_id = request.GET.get('sport_type')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            
            # Base queryset with optimized queries
            queryset = Playground.objects.select_related(
                'city__state__country', 'owner'
            ).prefetch_related(
                'sport_types', 'images', 'bookings', 'reviews'
            )
            
            # Filter by owner if not admin
            if not user.is_staff:
                queryset = queryset.filter(owner=user)
            
            # Apply filters
            if status != 'all':
                queryset = queryset.filter(status=status)
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search) |
                    Q(city__name__icontains=search)
                )
            
            if city_id:
                queryset = queryset.filter(city_id=city_id)
            
            if sport_type_id:
                queryset = queryset.filter(sport_types__id=sport_type_id)
            
            # Add real-time statistics
            queryset = queryset.annotate(
                total_bookings_count=Count('bookings'),
                avg_rating=Avg('reviews__rating'),
                total_revenue=Sum('bookings__final_amount'),
                pending_bookings_count=Count(
                    'bookings', 
                    filter=Q(bookings__status='pending')
                )
            )
            
            # Pagination
            paginator = Paginator(queryset, page_size)
            playgrounds_page = paginator.get_page(page)
            
            # Serialize data with real-time information
            playgrounds_data = []
            for playground in playgrounds_page:
                # Get real-time availability for today
                today = date.today()
                available_slots_today = self.get_available_slots_count(playground, today)
                
                # Get recent activity
                recent_bookings = playground.bookings.filter(
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count()
                
                playground_data = {
                    'id': playground.id,
                    'name': playground.name,
                    'description': playground.description,
                    'status': playground.status,
                    'playground_type': playground.playground_type,
                    'price_per_hour': str(playground.price_per_hour),
                    'capacity': playground.capacity,
                    'size': playground.size,
                    'rating': float(playground.avg_rating or 0),
                    'review_count': playground.review_count,
                    'total_bookings': playground.total_bookings_count or 0,
                    'pending_bookings': playground.pending_bookings_count or 0,
                    'total_revenue': float(playground.total_revenue or 0),
                    'recent_activity': recent_bookings,
                    'available_slots_today': available_slots_today,
                    
                    # Location information
                    'city': {
                        'id': playground.city.id,
                        'name': playground.city.name,
                        'state': playground.city.state.name,
                        'country': playground.city.state.country.name,
                    },
                    
                    # Sport types
                    'sport_types': [
                        {
                            'id': sport.id,
                            'name': sport.name,
                            'icon': sport.icon
                        }
                        for sport in playground.sport_types.all()
                    ],
                    
                    # Images
                    'main_image': playground.main_image.url if playground.main_image else None,
                    'gallery_images': [
                        {
                            'id': img.id,
                            'url': img.image.url,
                            'caption': img.caption,
                            'is_primary': img.is_primary
                        }
                        for img in playground.images.all()[:6]  # Limit for performance
                    ],
                    
                    # Real-time features
                    'live_availability': playground.live_availability,
                    'instant_booking': playground.instant_booking,
                    'auto_approval': playground.auto_approval,
                    
                    # Timestamps
                    'created_at': playground.created_at.isoformat(),
                    'updated_at': playground.updated_at.isoformat(),
                }
                
                playgrounds_data.append(playground_data)
            
            return JsonResponse({
                'success': True,
                'playgrounds': playgrounds_data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': playgrounds_page.has_next(),
                    'has_previous': playgrounds_page.has_previous(),
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Create new playground with comprehensive validation"""
        try:
            # Parse JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            # Create playground instance
            playground = Playground(
                owner=request.user,
                name=data.get('name'),
                description=data.get('description'),
                city_id=data.get('city'),
                address=data.get('address'),
                playground_type=data.get('playground_type', 'outdoor'),
                capacity=int(data.get('capacity', 10)),
                size=data.get('size', ''),
                price_per_hour=float(data.get('price_per_hour', 0)),
                price_per_day=float(data.get('price_per_day', 0)) if data.get('price_per_day') else None,
                phone_number=data.get('phone_number', ''),
                whatsapp_number=data.get('whatsapp_number', ''),
                auto_approval=data.get('auto_approval', False),
                live_availability=data.get('live_availability', True),
                instant_booking=data.get('instant_booking', True),
                advance_booking_days=int(data.get('advance_booking_days', 30)),
                rules=data.get('rules', ''),
                cancellation_policy=data.get('cancellation_policy', ''),
                refund_policy=data.get('refund_policy', ''),
            )
            
            # Parse JSON fields
            if data.get('operating_hours'):
                playground.operating_hours = json.loads(data.get('operating_hours')) if isinstance(data.get('operating_hours'), str) else data.get('operating_hours')
            
            if data.get('amenities'):
                playground.amenities = json.loads(data.get('amenities')) if isinstance(data.get('amenities'), str) else data.get('amenities')
            
            if data.get('payment_methods'):
                playground.payment_methods = json.loads(data.get('payment_methods')) if isinstance(data.get('payment_methods'), str) else data.get('payment_methods')
            
            if data.get('bank_details'):
                playground.bank_details = json.loads(data.get('bank_details')) if isinstance(data.get('bank_details'), str) else data.get('bank_details')
            
            # Set status to pending for approval
            playground.status = 'pending'
            playground.save()
            
            # Add sport types
            if data.get('sport_types'):
                sport_type_ids = data.get('sport_types')
                if isinstance(sport_type_ids, str):
                    sport_type_ids = json.loads(sport_type_ids)
                playground.sport_types.set(sport_type_ids)
            
            # Generate time slots based on operating hours
            self.generate_time_slots(playground)
            
            return JsonResponse({
                'success': True,
                'message': 'Playground created successfully and submitted for approval',
                'playground_id': playground.id,
                'status': playground.status
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    def get_available_slots_count(self, playground, date_obj):
        """Get count of available slots for a specific date"""
        try:
            day_name = date_obj.strftime('%A').lower()
            
            # Get operating hours for the day
            operating_hours = playground.operating_hours or {}
            day_hours = operating_hours.get(day_name)
            
            if not day_hours or not day_hours.get('active', True):
                return 0
            
            # Get time slots for the day
            time_slots = playground.time_slots.filter(
                day_of_week=day_name,
                is_available=True
            )
            
            available_count = 0
            for slot in time_slots:
                # Check if slot is already booked
                existing_bookings = Booking.objects.filter(
                    playground=playground,
                    booking_date=date_obj,
                    start_time=slot.start_time,
                    status__in=['confirmed', 'pending']
                ).count()
                
                if existing_bookings < slot.max_bookings:
                    available_count += 1
            
            return available_count
            
        except Exception:
            return 0
    
    def generate_time_slots(self, playground):
        """Generate time slots based on operating hours"""
        try:
            operating_hours = playground.operating_hours or {}
            
            for day, hours in operating_hours.items():
                if hours.get('active', True) and hours.get('open') and hours.get('close'):
                    start_time = datetime.strptime(hours['open'], '%H:%M').time()
                    end_time = datetime.strptime(hours['close'], '%H:%M').time()
                    
                    # Generate hourly slots
                    current_time = datetime.combine(date.today(), start_time)
                    end_datetime = datetime.combine(date.today(), end_time)
                    
                    if end_datetime <= current_time:  # Next day closing
                        end_datetime += timedelta(days=1)
                    
                    while current_time < end_datetime:
                        slot_end = current_time + timedelta(hours=1)
                        
                        # Don't create slot if it goes beyond closing time
                        if slot_end > end_datetime:
                            break
                        
                        TimeSlot.objects.get_or_create(
                            playground=playground,
                            day_of_week=day,
                            start_time=current_time.time(),
                            end_time=slot_end.time(),
                            defaults={
                                'price': playground.price_per_hour,
                                'is_available': True,
                                'max_bookings': 1
                            }
                        )
                        
                        current_time = slot_end
                        
        except Exception as e:
            print(f"Error generating time slots: {e}")


@method_decorator(csrf_exempt, name='dispatch')
class PlaygroundDetailAPIView(View):
    """
    Detailed playground view with comprehensive information and real-time data
    """
    
    def get(self, request, playground_id):
        """Get detailed playground information"""
        try:
            playground = get_object_or_404(
                Playground.objects.select_related(
                    'city__state__country', 'owner'
                ).prefetch_related(
                    'sport_types', 'images', 'time_slots', 'reviews__user'
                ),
                id=playground_id
            )
            
            # Check permissions
            if not request.user.is_staff and playground.owner != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied'
                }, status=403)
            
            # Get real-time statistics
            today = date.today()
            this_week_start = today - timedelta(days=today.weekday())
            this_month_start = today.replace(day=1)
            
            # Booking statistics
            total_bookings = playground.bookings.count()
            pending_bookings = playground.bookings.filter(status='pending').count()
            confirmed_bookings = playground.bookings.filter(status='confirmed').count()
            
            # Revenue statistics
            total_revenue = playground.bookings.filter(
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            this_month_revenue = playground.bookings.filter(
                booking_date__gte=this_month_start,
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            # Get available time slots for next 7 days
            available_slots = []
            for i in range(7):
                check_date = today + timedelta(days=i)
                day_name = check_date.strftime('%A').lower()
                
                day_slots = []
                for slot in playground.time_slots.filter(day_of_week=day_name, is_available=True):
                    # Check availability
                    booked_count = playground.bookings.filter(
                        booking_date=check_date,
                        start_time=slot.start_time,
                        status__in=['confirmed', 'pending']
                    ).count()
                    
                    is_available = booked_count < slot.max_bookings
                    
                    day_slots.append({
                        'id': slot.id,
                        'start_time': slot.start_time.strftime('%H:%M'),
                        'end_time': slot.end_time.strftime('%H:%M'),
                        'price': str(slot.get_effective_price()),
                        'is_available': is_available,
                        'booked_count': booked_count,
                        'max_bookings': slot.max_bookings
                    })
                
                available_slots.append({
                    'date': check_date.isoformat(),
                    'day_name': check_date.strftime('%A'),
                    'slots': day_slots
                })
            
            # Recent reviews
            recent_reviews = []
            for review in playground.reviews.order_by('-created_at')[:5]:
                recent_reviews.append({
                    'id': review.id,
                    'user_name': review.user.get_full_name() or review.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                })
            
            # Detailed playground data
            playground_data = {
                'id': playground.id,
                'name': playground.name,
                'description': playground.description,
                'status': playground.status,
                'playground_type': playground.playground_type,
                'capacity': playground.capacity,
                'size': playground.size,
                'address': playground.address,
                'latitude': str(playground.latitude) if playground.latitude else None,
                'longitude': str(playground.longitude) if playground.longitude else None,
                
                # Pricing
                'price_per_hour': str(playground.price_per_hour),
                'price_per_day': str(playground.price_per_day) if playground.price_per_day else None,
                'custom_pricing': playground.custom_pricing or {},
                
                # Location
                'city': {
                    'id': playground.city.id,
                    'name': playground.city.name,
                    'state': playground.city.state.name,
                    'country': playground.city.state.country.name,
                },
                
                # Contact
                'phone_number': playground.phone_number,
                'whatsapp_number': playground.whatsapp_number,
                
                # Sport types
                'sport_types': [
                    {
                        'id': sport.id,
                        'name': sport.name,
                        'icon': sport.icon
                    }
                    for sport in playground.sport_types.all()
                ],
                
                # Images with full gallery
                'main_image': playground.main_image.url if playground.main_image else None,
                'gallery_images': [
                    {
                        'id': img.id,
                        'url': img.image.url,
                        'caption': img.caption,
                        'is_primary': img.is_primary
                    }
                    for img in playground.images.all()
                ],
                
                # Features and policies
                'amenities': playground.amenities or [],
                'rules': playground.rules,
                'cancellation_policy': playground.cancellation_policy,
                'refund_policy': playground.refund_policy,
                
                # Booking settings
                'operating_hours': playground.operating_hours or {},
                'auto_approval': playground.auto_approval,
                'live_availability': playground.live_availability,
                'instant_booking': playground.instant_booking,
                'advance_booking_days': playground.advance_booking_days,
                
                # Payment methods
                'payment_methods': playground.payment_methods or {},
                'bank_details': playground.bank_details or {},
                'qr_code_image': playground.qr_code_image.url if playground.qr_code_image else None,
                
                # Statistics
                'statistics': {
                    'total_bookings': total_bookings,
                    'pending_bookings': pending_bookings,
                    'confirmed_bookings': confirmed_bookings,
                    'total_revenue': float(total_revenue),
                    'this_month_revenue': float(this_month_revenue),
                    'average_rating': float(playground.rating),
                    'review_count': playground.review_count,
                },
                
                # Real-time data
                'available_slots': available_slots,
                'recent_reviews': recent_reviews,
                
                # Timestamps
                'created_at': playground.created_at.isoformat(),
                'updated_at': playground.updated_at.isoformat(),
            }
            
            return JsonResponse({
                'success': True,
                'playground': playground_data,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BookingRequestAPIView(View):
    """
    API for managing booking requests with real-time updates
    """
    
    def get(self, request):
        """Get booking requests for playground owner"""
        try:
            user = request.user
            
            # Query parameters
            status = request.GET.get('status', 'all')
            playground_id = request.GET.get('playground')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            # Base queryset
            queryset = Booking.objects.select_related(
                'user', 'playground'
            ).filter(playground__owner=user)
            
            # Apply filters
            if status != 'all':
                queryset = queryset.filter(status=status)
            
            if playground_id:
                queryset = queryset.filter(playground_id=playground_id)
            
            # Order by priority (pending first, then by date)
            queryset = queryset.order_by(
                Case(
                    When(status='pending', then=0),
                    When(status='confirmed', then=1),
                    default=2
                ),
                '-created_at'
            )
            
            # Pagination
            paginator = Paginator(queryset, page_size)
            bookings_page = paginator.get_page(page)
            
            # Serialize booking data
            bookings_data = []
            for booking in bookings_page:
                booking_data = {
                    'id': booking.id,
                    'booking_id': str(booking.booking_id),
                    'status': booking.status,
                    'payment_status': booking.payment_status,
                    
                    # User information
                    'user': {
                        'id': booking.user.id,
                        'name': booking.user.get_full_name() or booking.user.username,
                        'email': booking.user.email,
                        'phone': booking.contact_phone,
                    },
                    
                    # Playground information
                    'playground': {
                        'id': booking.playground.id,
                        'name': booking.playground.name,
                        'image': booking.playground.main_image.url if booking.playground.main_image else None,
                    },
                    
                    # Booking details
                    'booking_date': booking.booking_date.isoformat(),
                    'start_time': booking.start_time.strftime('%H:%M'),
                    'end_time': booking.end_time.strftime('%H:%M'),
                    'duration_hours': float(booking.duration_hours),
                    'number_of_players': booking.number_of_players,
                    'special_requests': booking.special_requests,
                    
                    # Pricing
                    'price_per_hour': str(booking.price_per_hour),
                    'total_amount': str(booking.total_amount),
                    'discount_amount': str(booking.discount_amount),
                    'final_amount': str(booking.final_amount),
                    
                    # Payment information
                    'payment_method': booking.payment_method,
                    'payment_reference': booking.payment_reference,
                    'payment_receipt': booking.payment_receipt.url if booking.payment_receipt else None,
                    'receipt_verified': booking.receipt_verified,
                    'verified_by_admin': booking.verified_by.username if booking.verified_by else None,
                    'verified_at': booking.verified_at.isoformat() if booking.verified_at else None,
                    
                    # Additional details
                    'auto_approved': booking.auto_approved,
                    'owner_notes': booking.owner_notes,
                    'is_upcoming': booking.is_upcoming,
                    'is_past': booking.is_past,
                    
                    # Timestamps
                    'booked_at': booking.booked_at.isoformat(),
                    'confirmed_at': booking.confirmed_at.isoformat() if booking.confirmed_at else None,
                    'cancelled_at': booking.cancelled_at.isoformat() if booking.cancelled_at else None,
                    'updated_at': booking.updated_at.isoformat(),
                }
                
                bookings_data.append(booking_data)
            
            # Get summary statistics
            summary = {
                'total_pending': queryset.filter(status='pending').count(),
                'total_confirmed': queryset.filter(status='confirmed').count(),
                'total_completed': queryset.filter(status='completed').count(),
                'total_cancelled': queryset.filter(status='cancelled').count(),
                'today_bookings': queryset.filter(booking_date=date.today()).count(),
                'this_week_revenue': queryset.filter(
                    booking_date__gte=date.today() - timedelta(days=7),
                    payment_status='paid'
                ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
            }
            
            return JsonResponse({
                'success': True,
                'bookings': bookings_data,
                'summary': summary,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': bookings_page.has_next(),
                    'has_previous': bookings_page.has_previous(),
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Handle booking approval/rejection actions"""
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            action = data.get('action')  # 'approve', 'reject'
            notes = data.get('notes', '')
            
            booking = get_object_or_404(
                Booking,
                id=booking_id,
                playground__owner=request.user
            )
            
            if action == 'approve':
                booking.status = 'confirmed'
                booking.confirmed_at = timezone.now()
                booking.owner_notes = notes
                message = 'Booking approved successfully'
                
            elif action == 'reject':
                booking.status = 'cancelled'
                booking.cancelled_at = timezone.now()
                booking.cancellation_reason = notes
                booking.owner_notes = notes
                message = 'Booking rejected successfully'
                
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                }, status=400)
            
            booking.save()
            
            return JsonResponse({
                'success': True,
                'message': message,
                'booking': {
                    'id': booking.id,
                    'status': booking.status,
                    'confirmed_at': booking.confirmed_at.isoformat() if booking.confirmed_at else None,
                    'cancelled_at': booking.cancelled_at.isoformat() if booking.cancelled_at else None,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# Utility API Views for Dynamic Data

class CountriesAPIView(View):
    """API for countries data"""
    
    def get(self, request):
        countries = Country.objects.filter(is_active=True).order_by('name')
        countries_data = [
            {
                'id': country.id,
                'name': country.name,
                'code': country.code
            }
            for country in countries
        ]
        
        return JsonResponse({
            'success': True,
            'countries': countries_data
        })


class StatesAPIView(View):
    """API for states data"""
    
    def get(self, request):
        country_id = request.GET.get('country_id')
        if not country_id:
            return JsonResponse({
                'success': False,
                'error': 'Country ID is required'
            }, status=400)
        
        states = State.objects.filter(
            country_id=country_id,
            is_active=True
        ).order_by('name')
        
        states_data = [
            {
                'id': state.id,
                'name': state.name
            }
            for state in states
        ]
        
        return JsonResponse({
            'success': True,
            'states': states_data
        })


class CitiesAPIView(View):
    """API for cities data"""
    
    def get(self, request):
        state_id = request.GET.get('state_id')
        if not state_id:
            return JsonResponse({
                'success': False,
                'error': 'State ID is required'
            }, status=400)
        
        cities = City.objects.filter(
            state_id=state_id,
            is_active=True
        ).order_by('name')
        
        cities_data = [
            {
                'id': city.id,
                'name': city.name
            }
            for city in cities
        ]
        
        return JsonResponse({
            'success': True,
            'cities': cities_data
        })


class SportTypesAPIView(View):
    """API for sport types data"""
    
    def get(self, request):
        sport_types = SportType.objects.filter(is_active=True).order_by('name')
        sport_types_data = [
            {
                'id': sport.id,
                'name': sport.name,
                'icon': sport.icon,
                'description': sport.description
            }
            for sport in sport_types
        ]
        
        return JsonResponse({
            'success': True,
            'sport_types': sport_types_data
        })


class PlaygroundTypesAPIView(View):
    """API for playground types data"""
    
    def get(self, request):
        # Define playground types based on the model choices
        playground_types = [
            {'value': 'indoor', 'label': 'Indoor'},
            {'value': 'outdoor', 'label': 'Outdoor'},
            {'value': 'covered', 'label': 'Covered'},
            {'value': 'semi_covered', 'label': 'Semi Covered'},
        ]
        
        return JsonResponse({
            'success': True,
            'playground_types': playground_types
        })


@csrf_exempt
def available_slots_api(request):
    """Get available time slots for a playground on a specific date"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)
    
    try:
        playground_id = request.GET.get('playground_id')
        date_str = request.GET.get('date')
        duration = request.GET.get('duration', 1)
        
        if not playground_id or not date_str:
            return JsonResponse({
                'error': 'playground_id and date parameters are required'
            }, status=400)
        
        # Get playground
        try:
            playground = Playground.objects.get(id=playground_id)
        except Playground.DoesNotExist:
            return JsonResponse({'error': 'Playground not found'}, status=404)
        
        # Parse date
        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Convert duration to int
        try:
            duration_hours = int(duration)
        except ValueError:
            return JsonResponse({'error': 'Invalid duration format'}, status=400)
        
        # Check if date is in the past
        if booking_date < date.today():
            return JsonResponse({'error': 'Cannot book for past dates'}, status=400)
        
        # Get operating hours (simplified version)
        open_time = time(6, 0)  # Default 6 AM
        close_time = time(23, 0)  # Default 11 PM
        
        # Generate time slots
        current_time = open_time
        slot_duration = timedelta(hours=duration_hours)
        slots = []
        
        while current_time < close_time:
            slot_end_time = (datetime.combine(date.today(), current_time) + slot_duration).time()
            
            # Check if slot end time is within operating hours
            if slot_end_time > close_time:
                break
            
            # Check for existing bookings
            from bookings.models import Booking
            existing_bookings = Booking.objects.filter(
                playground=playground,
                booking_date=booking_date,
                status__in=['pending', 'confirmed'],
                start_time__lt=slot_end_time,
                end_time__gt=current_time
            ).count()
            
            # Check if current time has passed (for today's bookings)
            is_available = True
            if booking_date == date.today():
                from django.utils import timezone
                now = timezone.now().time()
                if current_time <= now:
                    is_available = False
            
            # Check booking limit
            if existing_bookings >= 1:  # One booking per slot
                is_available = False
            
            slots.append({
                'start_time': current_time.strftime('%H:%M'),
                'end_time': slot_end_time.strftime('%H:%M'),
                'available': is_available,
                'existing_bookings': existing_bookings
            })
            
            # Move to next slot (1 hour increments)
            current_time = (datetime.combine(date.today(), current_time) + timedelta(hours=1)).time()
        
        return JsonResponse({
            'success': True,
            'slots': slots,
            'playground_name': playground.name,
            'date': date_str,
            'duration_hours': duration_hours
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error getting available slots: {str(e)}'
        }, status=500)


@csrf_exempt
def playground_preview_api(request):
    """Generate playground preview data for form validation"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Extract form data
        name = data.get('name', 'Preview Playground')
        playground_type = data.get('playground_type', 'outdoor')
        description = data.get('description', '')
        capacity = int(data.get('capacity', 10))
        price_per_hour = float(data.get('price_per_hour', 25.0))
        sport_types = data.get('sport_types', [])
        
        # Generate preview response
        preview_data = {
            'name': name,
            'type': playground_type,
            'description': description[:100] + '...' if len(description) > 100 else description,
            'capacity': capacity,
            'hourly_rate': price_per_hour,
            'sports_count': len(sport_types) if sport_types else 0,
            'estimated_daily_revenue': price_per_hour * 8,  # 8 hours average
            'estimated_monthly_revenue': price_per_hour * 8 * 30,
            'popularity_score': min(90, (capacity * 2) + (len(sport_types) * 5) + (price_per_hour if price_per_hour < 50 else 50)),
            'preview_url': f'/playground/preview/{name.lower().replace(" ", "-")}/',
            'status': 'preview'
        }
        
        return JsonResponse({
            'success': True,
            'preview': preview_data,
            'message': 'Preview generated successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Preview generation failed: {str(e)}'}, status=500)
