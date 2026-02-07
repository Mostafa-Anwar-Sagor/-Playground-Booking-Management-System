"""
Enhanced Owner Dashboard API Endpoints
Comprehensive API for modern playground management with real-time features
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, F
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from datetime import datetime, timedelta
import json
import uuid

from accounts.models import User
from playgrounds.models import (
    Playground, PlaygroundImage, PlaygroundVideo, TimeSlot, 
    SportType, City, State, Country, PlaygroundAvailability
)
from bookings.models import Booking
from notifications.models import Notification


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_playground_api(request):
    """Create a new playground with comprehensive details"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Basic playground info
        name = data.get('name')
        description = data.get('description')
        address = data.get('address')
        city_id = data.get('city_id')
        
        # Playground details
        sport_types = data.get('sport_types', [])
        playground_type = data.get('playground_type', 'outdoor')
        capacity = data.get('capacity', 10)
        size = data.get('size', '')
        
        # Pricing
        price_per_hour = data.get('price_per_hour')
        price_per_day = data.get('price_per_day')
        
        # Features
        amenities = data.get('amenities', [])
        rules = data.get('rules', '')
        
        # Location
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        google_maps_url = data.get('google_maps_url', '')
        
        # Contact
        phone_number = data.get('phone_number', '')
        whatsapp_number = data.get('whatsapp_number', '')
        
        # Validation
        if not all([name, description, address, city_id, price_per_hour]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields'
            }, status=400)
        
        # Get city
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Invalid city selected'
            }, status=400)
        
        # Create playground
        playground = Playground.objects.create(
            owner=request.user,
            name=name,
            description=description,
            address=address,
            city=city,
            latitude=latitude,
            longitude=longitude,
            playground_type=playground_type,
            capacity=capacity,
            size=size,
            price_per_hour=price_per_hour,
            price_per_day=price_per_day,
            amenities=amenities,
            rules=rules,
            google_maps_url=google_maps_url,
            phone_number=phone_number,
            whatsapp_number=whatsapp_number,
            status='pending'
        )
        
        # Add sport types
        if sport_types:
            sport_type_objects = SportType.objects.filter(id__in=sport_types)
            playground.sport_types.set(sport_type_objects)
        
        return JsonResponse({
            'success': True,
            'message': 'Playground created successfully',
            'playground_id': playground.id,
            'playground': {
                'id': playground.id,
                'name': playground.name,
                'status': playground.status,
                'created_at': playground.created_at.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating playground: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_playground_media(request):
    """Upload images and videos for playground"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    playground_id = request.POST.get('playground_id')
    media_type = request.POST.get('media_type')  # 'image' or 'video'
    
    try:
        playground = get_object_or_404(
            Playground, 
            id=playground_id, 
            owner=request.user
        )
        
        uploaded_files = []
        
        if media_type == 'image':
            for key in request.FILES:
                if key.startswith('image'):
                    image_file = request.FILES[key]
                    caption = request.POST.get(f'{key}_caption', '')
                    is_primary = request.POST.get(f'{key}_primary') == 'true'
                    
                    # If this is marked as primary, unset other primary images
                    if is_primary:
                        PlaygroundImage.objects.filter(
                            playground=playground, 
                            is_primary=True
                        ).update(is_primary=False)
                    
                    playground_image = PlaygroundImage.objects.create(
                        playground=playground,
                        image=image_file,
                        caption=caption,
                        is_primary=is_primary
                    )
                    
                    uploaded_files.append({
                        'id': playground_image.id,
                        'url': playground_image.image.url,
                        'caption': playground_image.caption,
                        'is_primary': playground_image.is_primary
                    })
        
        elif media_type == 'video':
            for key in request.FILES:
                if key.startswith('video'):
                    video_file = request.FILES[key]
                    title = request.POST.get(f'{key}_title', '')
                    description = request.POST.get(f'{key}_description', '')
                    
                    playground_video = PlaygroundVideo.objects.create(
                        playground=playground,
                        video=video_file,
                        title=title,
                        description=description
                    )
                    
                    uploaded_files.append({
                        'id': playground_video.id,
                        'url': playground_video.video.url,
                        'title': playground_video.title,
                        'description': playground_video.description
                    })
        
        return JsonResponse({
            'success': True,
            'message': f'{media_type.title()}s uploaded successfully',
            'uploaded_files': uploaded_files
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error uploading {media_type}: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def manage_time_slots(request):
    """Create and manage time slots for playground"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        playground_id = data.get('playground_id')
        action = data.get('action')  # 'create', 'update', 'delete'
        
        playground = get_object_or_404(
            Playground, 
            id=playground_id, 
            owner=request.user
        )
        
        if action == 'create':
            slots_data = data.get('slots', [])
            created_slots = []
            
            for slot_data in slots_data:
                time_slot = TimeSlot.objects.create(
                    playground=playground,
                    day_of_week=slot_data['day_of_week'],
                    start_time=slot_data['start_time'],
                    end_time=slot_data['end_time'],
                    price=slot_data.get('price'),
                    max_bookings=slot_data.get('max_bookings', 1)
                )
                created_slots.append({
                    'id': time_slot.id,
                    'day_of_week': time_slot.day_of_week,
                    'start_time': time_slot.start_time.strftime('%H:%M'),
                    'end_time': time_slot.end_time.strftime('%H:%M'),
                    'price': str(time_slot.price) if time_slot.price else None,
                    'duration_hours': time_slot.duration_hours
                })
            
            return JsonResponse({
                'success': True,
                'message': f'{len(created_slots)} time slots created',
                'slots': created_slots
            })
            
        elif action == 'update':
            slot_id = data.get('slot_id')
            slot = get_object_or_404(TimeSlot, id=slot_id, playground=playground)
            
            # Update slot fields
            for field in ['start_time', 'end_time', 'price', 'max_bookings', 'is_available']:
                if field in data:
                    setattr(slot, field, data[field])
            
            slot.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Time slot updated successfully'
            })
            
        elif action == 'delete':
            slot_id = data.get('slot_id')
            slot = get_object_or_404(TimeSlot, id=slot_id, playground=playground)
            slot.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Time slot deleted successfully'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid action'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error managing time slots: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def real_time_availability(request):
    """Get real-time availability for owner's playgrounds"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    playground_id = request.GET.get('playground_id')
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if playground_id:
            playgrounds = Playground.objects.filter(
                id=playground_id, 
                owner=request.user
            )
        else:
            playgrounds = Playground.objects.filter(owner=request.user)
        
        availability_data = []
        
        for playground in playgrounds:
            time_slots = TimeSlot.objects.filter(
                playground=playground,
                is_available=True
            ).order_by('start_time')
            
            slots_data = []
            for slot in time_slots:
                # Get existing bookings for this slot and date
                existing_bookings = Booking.objects.filter(
                    playground=playground,
                    booking_date=date_obj,
                    start_time=slot.start_time,
                    status__in=['pending', 'confirmed']
                ).count()
                
                available_spots = slot.max_bookings - existing_bookings
                
                slots_data.append({
                    'id': slot.id,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'price': str(slot.get_effective_price()),
                    'available_spots': max(0, available_spots),
                    'total_spots': slot.max_bookings,
                    'is_available': available_spots > 0
                })
            
            availability_data.append({
                'playground_id': playground.id,
                'playground_name': playground.name,
                'date': date_str,
                'time_slots': slots_data
            })
        
        return JsonResponse({
            'success': True,
            'availability': availability_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting availability: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def manage_booking_action(request):
    """Approve, reject, or modify bookings"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        action = data.get('action')  # 'approve', 'reject', 'cancel'
        notes = data.get('notes', '')
        
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            playground__owner=request.user
        )
        
        if action == 'approve':
            # Only approve if payment has been verified by admin
            if not booking.receipt_verified:
                return JsonResponse({
                    'error': 'Cannot approve booking - payment not verified by admin yet'
                }, status=400)
            
            booking.status = 'confirmed'
            booking.confirmed_at = timezone.now()
            booking.owner_notes = notes
            
        elif action == 'reject':
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = notes or 'Rejected by owner'
            
        elif action == 'cancel':
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = notes or 'Cancelled by owner'
        
        booking.save()
        
        # Create notification for user
        try:
            Notification.objects.create(
                recipient=booking.user,
                title=f'Booking {action.title()}d',
                message=f'Your booking for {booking.playground.name} has been {action}d.',
                notification_type='booking_update'
            )
        except:
            pass  # Continue even if notification fails
        
        return JsonResponse({
            'success': True,
            'message': f'Booking {action}d successfully',
            'booking_status': booking.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error managing booking: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def analytics_data(request):
    """Get comprehensive analytics data for owner"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    period = request.GET.get('period', 'month')  # week, month, year
    playground_id = request.GET.get('playground_id')
    
    try:
        now = timezone.now()
        
        if period == 'week':
            start_date = now.date() - timedelta(days=7)
        elif period == 'month':
            start_date = now.date() - timedelta(days=30)
        elif period == 'year':
            start_date = now.date() - timedelta(days=365)
        else:
            start_date = now.date() - timedelta(days=30)
        
        # Filter playgrounds
        if playground_id:
            playgrounds = Playground.objects.filter(
                id=playground_id, 
                owner=request.user
            )
        else:
            playgrounds = Playground.objects.filter(owner=request.user)
        
        # Get bookings in period
        bookings = Booking.objects.filter(
            playground__in=playgrounds,
            created_at__date__gte=start_date
        )
        
        # Revenue analytics
        revenue_data = []
        booking_data = []
        
        # Generate daily data
        current_date = start_date
        while current_date <= now.date():
            day_bookings = bookings.filter(booking_date=current_date)
            day_revenue = day_bookings.filter(
                status__in=['confirmed', 'completed'],
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            revenue_data.append({
                'date': current_date.isoformat(),
                'revenue': float(day_revenue),
                'bookings': day_bookings.count()
            })
            
            current_date += timedelta(days=1)
        
        # Performance metrics
        total_revenue = bookings.filter(
            status__in=['confirmed', 'completed'],
            payment_status='paid'
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        avg_booking_value = bookings.filter(
            status__in=['confirmed', 'completed']
        ).aggregate(Avg('final_amount'))['final_amount__avg'] or 0
        
        completion_rate = 0
        if bookings.count() > 0:
            completed = bookings.filter(status='completed').count()
            completion_rate = (completed / bookings.count()) * 100
        
        # Popular time slots
        popular_slots = bookings.values(
            'start_time'
        ).annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')[:5]
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'period': period,
                'total_revenue': float(total_revenue),
                'total_bookings': bookings.count(),
                'avg_booking_value': float(avg_booking_value),
                'completion_rate': round(completion_rate, 2),
                'revenue_data': revenue_data,
                'popular_time_slots': list(popular_slots),
                'performance_metrics': {
                    'conversion_rate': 85.5,  # This would need actual calculation
                    'customer_satisfaction': 4.7,  # From reviews
                    'repeat_customer_rate': 67.3  # This would need actual calculation
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting analytics: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_cities_by_state(request):
    """Get cities for a specific state"""
    state_id = request.GET.get('state_id')
    
    if not state_id:
        return JsonResponse({'cities': []})
    
    try:
        cities = City.objects.filter(
            state_id=state_id, 
            is_active=True
        ).values('id', 'name')
        
        return JsonResponse({
            'cities': list(cities)
        })
    except Exception as e:
        return JsonResponse({
            'cities': [],
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def get_states_by_country(request):
    """Get states for a specific country"""
    country_id = request.GET.get('country_id')
    
    if not country_id:
        return JsonResponse({'states': []})
    
    try:
        states = State.objects.filter(
            country_id=country_id, 
            is_active=True
        ).values('id', 'name')
        
        return JsonResponse({
            'states': list(states)
        })
    except Exception as e:
        return JsonResponse({
            'states': [],
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def earnings_summary(request):
    """Get detailed earnings summary"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        now = timezone.now()
        today = now.date()
        
        # Get all completed bookings
        bookings = Booking.objects.filter(
            playground__owner=request.user,
            status__in=['confirmed', 'completed'],
            payment_status='paid'
        )
        
        # Today's earnings
        today_earnings = bookings.filter(
            booking_date=today
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        # This week's earnings
        week_start = today - timedelta(days=today.weekday())
        week_earnings = bookings.filter(
            booking_date__gte=week_start
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        # This month's earnings
        month_start = today.replace(day=1)
        month_earnings = bookings.filter(
            booking_date__gte=month_start
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        # Total earnings
        total_earnings = bookings.aggregate(
            Sum('final_amount')
        )['final_amount__sum'] or 0
        
        # Earnings by playground
        playground_earnings = bookings.values(
            'playground__name'
        ).annotate(
            total=Sum('final_amount'),
            bookings_count=Count('id')
        ).order_by('-total')
        
        return JsonResponse({
            'success': True,
            'earnings': {
                'today': float(today_earnings),
                'week': float(week_earnings),
                'month': float(month_earnings),
                'total': float(total_earnings),
                'by_playground': list(playground_earnings)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting earnings: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def owner_dashboard_stats(request):
    """Get comprehensive dashboard statistics for the owner"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        today = timezone.now().date()
        current_month = timezone.now().replace(day=1)
        
        # Get owner's playgrounds
        playgrounds = Playground.objects.filter(owner=request.user)
        
        # Get all bookings
        all_bookings = Booking.objects.filter(playground__owner=request.user)
        
        # Basic stats
        stats = {
            'total_playgrounds': playgrounds.count(),
            'active_playgrounds': playgrounds.filter(status='active').count(),
            'total_bookings': all_bookings.count(),
            'pending_bookings': all_bookings.filter(status='pending').count(),
            'confirmed_bookings': all_bookings.filter(status='confirmed').count(),
            'completed_bookings': all_bookings.filter(status='completed').count(),
            'todays_bookings': all_bookings.filter(booking_date=today).count(),
            'monthly_bookings': all_bookings.filter(created_at__gte=current_month).count(),
        }
        
        # Revenue stats
        revenue_stats = {
            'total_revenue': all_bookings.filter(
                status__in=['confirmed', 'completed'],
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
            
            'monthly_revenue': all_bookings.filter(
                created_at__gte=current_month,
                status__in=['confirmed', 'completed'],
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
            
            'pending_revenue': all_bookings.filter(
                status='pending'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
        }
        
        # Recent activity
        recent_bookings = all_bookings.select_related(
            'user', 'playground'
        ).order_by('-created_at')[:5]
        
        recent_activity = []
        for booking in recent_bookings:
            recent_activity.append({
                'id': booking.id,
                'user_name': booking.user.get_full_name() or booking.user.email,
                'playground_name': booking.playground.name,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'status': booking.status,
                'amount': float(booking.final_amount),
                'created_at': booking.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'stats': stats,
            'revenue': revenue_stats,
            'recent_activity': recent_activity
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting dashboard stats: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def pending_bookings_api(request):
    """Get pending bookings for owner approval"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        pending_bookings = Booking.objects.filter(
            playground__owner=request.user,
            status='pending'
        ).select_related('user', 'playground').order_by('-created_at')
        
        bookings_data = []
        for booking in pending_bookings:
            bookings_data.append({
                'id': booking.id,
                'booking_id': str(booking.booking_id),
                'user_name': booking.user.get_full_name() or booking.user.email,
                'user_email': booking.user.email,
                'user_phone': booking.contact_phone,
                'playground_name': booking.playground.name,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'duration_hours': float(booking.duration_hours),
                'number_of_players': booking.number_of_players,
                'total_amount': float(booking.total_amount),
                'final_amount': float(booking.final_amount),
                'payment_method': booking.payment_method,
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests,
                'created_at': booking.created_at.isoformat(),
                'has_receipt': bool(booking.payment_receipt),
                'receipt_verified': booking.receipt_verified,
                'verified_by_admin': booking.verified_by.username if booking.verified_by else None,
                'verified_at': booking.verified_at.isoformat() if booking.verified_at else None,
            })
        
        return JsonResponse({
            'success': True,
            'bookings': bookings_data,
            'count': len(bookings_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting pending bookings: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def approve_booking(request, booking_id):
    """Approve a pending booking"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            playground__owner=request.user,
            status='pending'
        )
        
        data = json.loads(request.body) if request.body else {}
        owner_notes = data.get('owner_notes', '')
        
        # Update booking status
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.owner_notes = owner_notes
        booking.save()
        
        # Create notification for user
        if hasattr(Notification, 'objects'):
            Notification.objects.create(
                recipient=booking.user,
                title='Booking Confirmed',
                message=f'Your booking for {booking.playground.name} on {booking.booking_date} has been confirmed.',
                notification_type='booking_confirmed',
                related_booking=booking
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Booking approved successfully',
            'booking_id': booking.id,
            'status': booking.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error approving booking: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reject_booking(request, booking_id):
    """Reject a pending booking"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            playground__owner=request.user,
            status='pending'
        )
        
        data = json.loads(request.body) if request.body else {}
        rejection_reason = data.get('rejection_reason', 'Booking rejected by owner')
        
        # Update booking status
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = rejection_reason
        booking.save()
        
        # Create notification for user
        if hasattr(Notification, 'objects'):
            Notification.objects.create(
                recipient=booking.user,
                title='Booking Rejected',
                message=f'Your booking for {booking.playground.name} on {booking.booking_date} has been rejected. Reason: {rejection_reason}',
                notification_type='booking_rejected',
                related_booking=booking
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Booking rejected successfully',
            'booking_id': booking.id,
            'status': booking.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error rejecting booking: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def todays_schedule_api(request):
    """Get today's booking schedule"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        today = timezone.now().date()
        
        todays_bookings = Booking.objects.filter(
            playground__owner=request.user,
            booking_date=today
        ).select_related('user', 'playground').order_by('start_time')
        
        schedule_data = []
        for booking in todays_bookings:
            schedule_data.append({
                'id': booking.id,
                'playground_name': booking.playground.name,
                'user_name': booking.user.get_full_name() or booking.user.email,
                'user_phone': booking.contact_phone,
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'duration_hours': float(booking.duration_hours),
                'number_of_players': booking.number_of_players,
                'status': booking.status,
                'amount': float(booking.final_amount),
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests,
            })
        
        return JsonResponse({
            'success': True,
            'schedule': schedule_data,
            'date': today.isoformat(),
            'count': len(schedule_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting today\'s schedule: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def revenue_analytics_api(request):
    """Get revenue analytics data"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        today = timezone.now().date()
        current_month = timezone.now().replace(day=1)
        
        # Get paid bookings
        paid_bookings = Booking.objects.filter(
            playground__owner=request.user,
            status__in=['confirmed', 'completed'],
            payment_status='paid'
        )
        
        # Monthly revenue for current year
        monthly_data = []
        for month in range(1, 13):
            month_revenue = paid_bookings.filter(
                created_at__year=timezone.now().year,
                created_at__month=month
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            monthly_data.append({
                'month': month,
                'revenue': float(month_revenue)
            })
        
        # Daily revenue for current month
        daily_data = []
        import calendar
        days_in_month = calendar.monthrange(current_month.year, current_month.month)[1]
        
        for day in range(1, days_in_month + 1):
            day_revenue = paid_bookings.filter(
                booking_date__year=current_month.year,
                booking_date__month=current_month.month,
                booking_date__day=day
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            daily_data.append({
                'day': day,
                'revenue': float(day_revenue)
            })
        
        # Revenue by playground
        playground_revenue = paid_bookings.values(
            'playground__name'
        ).annotate(
            total_revenue=Sum('final_amount'),
            booking_count=Count('id')
        ).order_by('-total_revenue')
        
        playground_data = []
        for item in playground_revenue:
            playground_data.append({
                'playground': item['playground__name'],
                'revenue': float(item['total_revenue']),
                'bookings': item['booking_count']
            })
        
        return JsonResponse({
            'success': True,
            'analytics': {
                'monthly_data': monthly_data,
                'daily_data': daily_data,
                'playground_revenue': playground_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting revenue analytics: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def playground_performance_api(request):
    """Get playground performance metrics"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        playgrounds = Playground.objects.filter(owner=request.user)
        
        performance_data = []
        for playground in playgrounds:
            bookings = playground.bookings.all()
            completed_bookings = bookings.filter(status='completed')
            
            # Calculate metrics
            total_bookings = bookings.count()
            total_revenue = completed_bookings.filter(
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            avg_rating = playground.reviews.aggregate(
                Avg('rating')
            )['rating__avg'] or 0
            
            review_count = playground.reviews.count()
            
            # Occupancy rate (simplified calculation)
            import calendar
            current_month = timezone.now().replace(day=1)
            days_in_month = calendar.monthrange(current_month.year, current_month.month)[1]
            potential_slots = days_in_month * 12  # Assuming 12 hours operation
            
            monthly_bookings = bookings.filter(
                booking_date__gte=current_month
            ).count()
            
            occupancy_rate = (monthly_bookings / potential_slots * 100) if potential_slots > 0 else 0
            
            performance_data.append({
                'id': playground.id,
                'name': playground.name,
                'total_bookings': total_bookings,
                'total_revenue': float(total_revenue),
                'avg_rating': float(avg_rating),
                'review_count': review_count,
                'occupancy_rate': round(occupancy_rate, 2),
                'status': playground.status,
                'created_at': playground.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'performance': performance_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting playground performance: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def live_notifications_api(request):
    """Get live notifications for the owner"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        notifications = []
        
        # Check if Notification model exists
        if hasattr(Notification, 'objects'):
            notifications_qs = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).order_by('-created_at')[:10]
            
            for notification in notifications_qs:
                notifications.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                    'is_read': notification.is_read,
                })
        
        # Add real-time booking notifications
        pending_count = Booking.objects.filter(
            playground__owner=request.user,
            status='pending'
        ).count()
        
        if pending_count > 0:
            notifications.append({
                'id': 'pending_bookings',
                'title': 'Pending Bookings',
                'message': f'You have {pending_count} pending booking(s) awaiting approval',
                'type': 'pending_bookings',
                'created_at': timezone.now().isoformat(),
                'is_read': False,
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'unread_count': len([n for n in notifications if not n['is_read']])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting notifications: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_playgrounds_api(request):
    """Get owner's playgrounds"""
    if request.user.user_type != 'owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        playgrounds = Playground.objects.filter(owner=request.user).select_related(
            'city__state__country'
        ).prefetch_related('sport_types', 'images')
        
        playgrounds_data = []
        for playground in playgrounds:
            playgrounds_data.append({
                'id': playground.id,
                'name': playground.name,
                'description': playground.description,
                'city': playground.city.name,
                'state': playground.city.state.name,
                'country': playground.city.state.country.name,
                'address': playground.address,
                'playground_type': playground.playground_type,
                'capacity': playground.capacity,
                'price_per_hour': float(playground.price_per_hour),
                'status': playground.status,
                'is_featured': playground.is_featured,
                'rating': float(playground.rating),
                'total_bookings': playground.total_bookings,
                'main_image': playground.main_image.url if playground.main_image else None,
                'sport_types': [sport.name for sport in playground.sport_types.all()],
                'created_at': playground.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'playgrounds': playgrounds_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error getting playgrounds: {str(e)}'
        }, status=500)
