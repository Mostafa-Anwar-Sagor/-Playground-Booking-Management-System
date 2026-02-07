from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.views.generic import TemplateView
from datetime import datetime, date, timedelta
import json
import uuid
import re
from decimal import Decimal

from .models import Booking
from playgrounds.models import Playground, TimeSlot
from accounts.models import User
from payments.models import PaymentMethod, PlaygroundPaymentConfig, PlaygroundPaymentMethod


@login_required
def booking_dashboard(request):
    """
    Comprehensive booking dashboard for users to manage their bookings
    """
    user = request.user
    
    # Get user's bookings with statistics
    bookings = Booking.objects.filter(user=user).select_related('playground').order_by('-created_at')
    
    # Statistics
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    completed_bookings = bookings.filter(status='completed').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    
    # Upcoming bookings
    upcoming_bookings = bookings.filter(
        booking_date__gte=date.today(),
        status__in=['confirmed', 'pending']
    ).order_by('booking_date', 'start_time')[:5]
    
    # Recent bookings
    recent_bookings = bookings.order_by('-created_at')[:10]
    
    # Total amount spent
    total_spent = bookings.filter(
        payment_status='paid'
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    
    context = {
        'bookings': recent_bookings,
        'upcoming_bookings': upcoming_bookings,
        'stats': {
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_spent': total_spent,
        }
    }
    
    return render(request, 'bookings/booking_dashboard.html', context)


@login_required
def checkout(request, playground_id):
    """
    Display checkout form for playground booking
    """
    playground = get_object_or_404(Playground, id=playground_id, status='active')
    
    # Generate context data
    today = date.today()
    max_date = today + timedelta(days=30)
    player_range = range(1, playground.capacity + 1)
    
    context = {
        'playground': playground,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
        'player_range': player_range,
    }
    
    return render(request, 'bookings/checkout.html', context)


def test_checkout(request, playground_id):
    """
    TEST VERSION: Display checkout form for playground booking (NO LOGIN REQUIRED)
    Use this for development/testing when authentication is causing issues
    """
    playground = get_object_or_404(Playground, id=playground_id, status='active')
    
    # Generate context data
    today = date.today()
    max_date = today + timedelta(days=30)
    player_range = range(1, playground.capacity + 1)
    
    context = {
        'playground': playground,
        'today': today.isoformat(),
        'max_date': max_date.isoformat(),
        'player_range': player_range,
    }
    
    return render(request, 'bookings/checkout.html', context)


@login_required
def create_booking(request, playground_id):
    """
    Create a new booking for a playground
    """
    playground = get_object_or_404(Playground, id=playground_id, status='active')
    
    if request.method == 'POST':
        # Handle booking creation (original functionality)
        try:
            # Parse booking data
            booking_date = datetime.strptime(request.POST.get('booking_date'), '%Y-%m-%d').date()
            
            # Debug time parsing
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            print(f"🕐 Debug time parsing: start_time='{start_time_str}', end_time='{end_time_str}'")
            
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            # Calculate duration
            start_datetime = datetime.combine(booking_date, start_time)
            end_datetime = datetime.combine(booking_date, end_time)
            duration = (end_datetime - start_datetime).total_seconds() / 3600
            
            # Check availability
            existing_bookings = Booking.objects.filter(
                playground=playground,
                booking_date=booking_date,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=['confirmed', 'pending']
            ).count()
            
            if existing_bookings > 0:
                messages.error(request, 'This time slot is already booked. Please choose another time.')
                return redirect('playgrounds:playground_detail', pk=playground.id)
            
            # Calculate pricing - Convert duration to Decimal to avoid type errors
            base_price = playground.price_per_hour * Decimal(str(duration))
            discount_amount = Decimal('0.00')
            final_amount = base_price - discount_amount
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                playground=playground,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                duration_hours=duration,
                number_of_players=int(request.POST.get('number_of_players', 1)),
                special_requests=request.POST.get('special_requests', ''),
                contact_phone=request.POST.get('contact_phone', ''),
                
                # Pricing
                price_per_hour=playground.price_per_hour,
                total_amount=base_price,
                discount_amount=discount_amount,
                final_amount=final_amount,
                
                # Payment
                payment_method=request.POST.get('payment_method', 'cash'),
                
                # Status
                status='confirmed' if playground.auto_approval else 'pending',
            )
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'booking_id': str(booking.id),
                    'message': f'Booking created successfully! Your booking ID is {booking.booking_id}'
                })
            
            messages.success(request, f'Booking created successfully! Your booking ID is {booking.booking_id}')
            return redirect('bookings:booking_detail', booking_id=booking.id)
            
        except ValueError as e:
            error_msg = f'Time format error: {str(e)}. Received start_time: "{request.POST.get("start_time")}", end_time: "{request.POST.get("end_time")}"'
            print(f"❌ ValueError in create_booking: {error_msg}")
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'details': 'Time format must be HH:MM (24-hour format)'
                })
            
            messages.error(request, error_msg)
            return redirect('playgrounds:playground_detail', pk=playground.id)
            
        except Exception as e:
            error_msg = f'Error creating booking: {str(e)}'
            print(f"❌ Exception in create_booking: {error_msg}")
            print(f"POST data: {dict(request.POST)}")
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'details': 'Please check your form data and try again.'
                })
            
            messages.error(request, error_msg)
            return redirect('playgrounds:playground_detail', pk=playground.id)
    
    # GET request - show booking form
    context = {
        'playground': playground,
        'today': date.today(),
        'max_date': date.today() + timedelta(days=30),
    }
    
    return render(request, 'bookings/create_booking.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    Display detailed information about a specific booking using UUID
    """
    booking = get_object_or_404(
        Booking.objects.select_related('playground', 'user'),
        booking_id=booking_id  # Use UUID field
    )
    
    # Check permissions
    if booking.user != request.user and booking.playground.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('bookings:booking_dashboard')
    
    # Extract amenities from special_requests JSON
    import json
    selected_amenities = []
    try:
        if booking.special_requests:
            print(f"🔍 DEBUG booking_detail: Raw special_requests: {booking.special_requests}")
            
            # Try to parse JSON
            try:
                special_data = json.loads(booking.special_requests) if isinstance(booking.special_requests, str) else booking.special_requests
                print(f"🔍 DEBUG booking_detail: Parsed special_data: {special_data}")
                raw_amenities = special_data.get('selected_amenities', [])
                print(f"🔍 DEBUG booking_detail: Raw amenities from JSON: {raw_amenities}")
            except (json.JSONDecodeError, TypeError):
                print(f"⚠️ DEBUG: Failed to parse special_requests as JSON, trying as plain text")
                special_data = {}
                raw_amenities = []
            
            # If we got valid amenities from JSON, format them
            if raw_amenities and isinstance(raw_amenities, list):
                formatted_amenities = []
                for amenity in raw_amenities:
                    # If amenity is already a dict with required fields, use it directly
                    if isinstance(amenity, dict) and 'name' in amenity:
                        formatted_amenities.append(amenity)
                        print(f"✅ DEBUG: Added amenity dict: {amenity.get('name')}")
                    # If it's just an ID or string, try to fetch from playground amenities
                    elif isinstance(amenity, (str, int)):
                        # Try to get amenity details from playground's JSON amenities
                        playground_amenities = booking.playground.amenities or []
                        for pa in playground_amenities:
                            if isinstance(pa, dict) and (pa.get('id') == amenity or pa.get('name') == amenity):
                                formatted_amenities.append(pa)
                                print(f"✅ DEBUG: Found and added amenity from playground: {pa.get('name')}")
                                break
                selected_amenities = formatted_amenities
            
            # FALLBACK: If no amenities found in JSON, try to extract from booking summary in special_requests
            # This handles old bookings where amenities weren't saved properly
            if not selected_amenities:
                print(f"⚠️ DEBUG: No amenities in JSON, checking special_requests text for clues...")
                # Check if special_requests contains amenity information as plain text
                special_text = str(booking.special_requests).lower()
                playground_amenities = booking.playground.amenities or []
                
                # Try to match amenity names from playground to text in special_requests
                for pa in playground_amenities:
                    if isinstance(pa, dict) and 'name' in pa:
                        amenity_name = pa.get('name', '').lower()
                        # Check if amenity name appears in the special requests text
                        if amenity_name and amenity_name in special_text:
                            selected_amenities.append(pa)
                            print(f"✅ DEBUG: Found amenity from text match: {pa.get('name')}")
                
                print(f"🔍 DEBUG: Found {len(selected_amenities)} amenities from text matching")
            
            print(f"🎯 DEBUG booking_detail: Final amenities to display: {selected_amenities}")
            print(f"🎯 DEBUG booking_detail: Number of amenities: {len(selected_amenities)}")
    except Exception as e:
        print(f"❌ DEBUG booking_detail: Unexpected error parsing amenities: {e}")
        import traceback
        traceback.print_exc()
        selected_amenities = []
    
    # Get currency symbol from playground's currency
    from django.conf import settings
    
    # Currency mapping for symbols
    currency_symbols = {
        'BDT': '৳',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'MYR': 'RM',
        'SGD': 'S$',
    }
    
    # Get playground's currency or fallback to settings
    playground_currency = booking.playground.currency if hasattr(booking.playground, 'currency') else getattr(settings, 'CURRENCY', 'BDT')
    currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
    
    print(f"💰 DEBUG booking_detail: Playground currency: {playground_currency}")
    print(f"💰 DEBUG booking_detail: Currency symbol: {currency_symbol}")
    
    context = {
        'booking': booking,
        'can_cancel': booking.can_be_cancelled(),
        'can_reschedule': booking.can_be_rescheduled(),
        'is_owner': booking.playground.owner == request.user,
        'is_user': booking.user == request.user,
        'amenities': selected_amenities,  # Pass selected amenities to template
        'currency_symbol': currency_symbol,
        'currency_code': playground_currency,
    }
    
    print(f"💰 DEBUG booking_detail: Context currency_symbol: {context['currency_symbol']}")
    
    return render(request, 'bookings/booking_detail.html', context)


@login_required  
def booking_detail_by_id(request, booking_id):
    """
    Display detailed information about a specific booking using integer ID
    """
    booking = get_object_or_404(
        Booking.objects.select_related('playground', 'user'),
        id=booking_id  # Use integer ID
    )
    
    # Check permissions
    if booking.user != request.user and booking.playground.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('bookings:booking_dashboard')
    
    # Import settings for currency
    from django.conf import settings
    from django.utils import timezone
    import qrcode
    from io import BytesIO
    import base64
    
    # Currency mapping for symbols
    currency_symbols = {
        'BDT': '৳',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'MYR': 'RM',
        'SGD': 'S$',
    }
    
    # Get playground's currency or fallback to settings
    playground_currency = booking.playground.currency if hasattr(booking.playground, 'currency') else getattr(settings, 'CURRENCY', 'BDT')
    playground_currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
    
    # Generate QR Code for booking verification
    # QR contains: booking_id, verification URL
    qr_data = f"{request.build_absolute_uri('/bookings/verify/')}?booking_id={booking.booking_id}&playground_id={booking.playground.id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Parse special_requests JSON for slot details
    import json
    slot_details = {}
    selected_amenities = []
    try:
        if booking.special_requests:
            raw_slot_details = json.loads(booking.special_requests) if isinstance(booking.special_requests, str) else booking.special_requests
            # Format the slot details for display
            slot_details = {
                'booking_type': raw_slot_details.get('booking_type', '').replace('_', ' ').title() if raw_slot_details.get('booking_type') else '',
                'slot_type': raw_slot_details.get('slot_type', '').replace('_', ' ').title() if raw_slot_details.get('slot_type') else '',
                'time_slot_type': raw_slot_details.get('time_slot_type', '').replace('_', ' ').title() if raw_slot_details.get('time_slot_type') else '',
                'pass_name': raw_slot_details.get('pass_name', ''),
                'pass_duration_type': raw_slot_details.get('pass_duration_type', '').replace('_', ' ').title() if raw_slot_details.get('pass_duration_type') else '',
                'pass_duration_days': raw_slot_details.get('pass_duration_days', ''),
                'slot_name': raw_slot_details.get('slot_name', ''),
            }
            # EXTRACT SELECTED AMENITIES FROM SPECIAL_REQUESTS
            raw_amenities = raw_slot_details.get('selected_amenities', [])
            
            # Ensure amenities have the proper structure for template
            if raw_amenities and isinstance(raw_amenities, list):
                formatted_amenities = []
                for amenity in raw_amenities:
                    # If amenity is already a dict with required fields, use it directly
                    if isinstance(amenity, dict) and 'name' in amenity:
                        formatted_amenities.append(amenity)
                    # If it's just an ID or string, try to fetch from playground amenities
                    elif isinstance(amenity, (str, int)):
                        # Try to get amenity details from playground's JSON amenities
                        playground_amenities = booking.playground.amenities or []
                        for pa in playground_amenities:
                            if isinstance(pa, dict) and (pa.get('id') == amenity or pa.get('name') == amenity):
                                formatted_amenities.append(pa)
                                break
                selected_amenities = formatted_amenities
            
            # FALLBACK: If no amenities found, try text matching
            if not selected_amenities:
                special_text = str(booking.special_requests).lower()
                playground_amenities = booking.playground.amenities or []
                for pa in playground_amenities:
                    if isinstance(pa, dict) and 'name' in pa:
                        amenity_name = pa.get('name', '').lower()
                        if amenity_name and amenity_name in special_text:
                            selected_amenities.append(pa)
    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        print(f"⚠️ DEBUG booking_detail_by_id: Error parsing special_requests: {e}")
        slot_details = {}
        selected_amenities = []
    
    context = {
        'booking': booking,
        'can_cancel': booking.can_be_cancelled(),
        'can_reschedule': booking.can_be_rescheduled(),  
        'is_owner': booking.playground.owner == request.user,
        'is_user': booking.user == request.user,
        'currency_symbol': playground_currency_symbol,
        'currency_code': playground_currency,
        'today': timezone.now().date(),
        'current_datetime': timezone.now(),
        'amenities': selected_amenities,  # CHANGED: Use selected amenities from booking, not all playground amenities
        'playground_amenities_json': booking.playground.amenities,
        'booking_age': (timezone.now() - booking.created_at).days if booking.created_at else 0,
        'qr_code': qr_code_base64,
        'verification_url': qr_data,
        'slot_details': slot_details,
        # Brand & Theme Configuration
        'brand_colors': getattr(settings, 'BRAND_COLORS', {}),
        'business_name': getattr(settings, 'BUSINESS_NAME', 'PlayGround Booking'),
        'brand_logo': getattr(settings, 'BRAND_LOGO', '/static/images/logo.png'),
        'company_info': {
            'name': getattr(settings, 'COMPANY_NAME', 'Playground Booking System'),
            'address': getattr(settings, 'COMPANY_ADDRESS', ''),
            'phone': getattr(settings, 'COMPANY_PHONE', ''),
            'email': getattr(settings, 'COMPANY_EMAIL', 'support@playground.com'),
        },
        # Dynamic UI Text Configuration
        'ui_text': getattr(settings, 'UI_TEXT', {}),
    }
    
    return render(request, 'bookings/booking_detail.html', context)


@login_required
@csrf_exempt
def cancel_booking(request, booking_id):
    """
    Cancel a booking with proper validation and refund handling
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id)
        
        # Check permissions
        if booking.user != request.user and booking.playground.owner != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        # Check if booking can be cancelled
        if not booking.can_be_cancelled():
            return JsonResponse({'success': False, 'error': 'This booking cannot be cancelled'})
        
        # Parse cancellation data
        data = json.loads(request.body) if request.body else {}
        cancellation_reason = data.get('reason', 'User cancelled')
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = cancellation_reason
        
        # Handle refund logic based on cancellation policy
        refund_amount = booking.calculate_refund_amount()
        booking.refund_amount = refund_amount
        booking.refund_status = 'pending' if refund_amount > 0 else 'not_applicable'
        
        booking.save()
        
        print(f"✅ CANCEL: Booking {booking.booking_id} cancelled successfully")
        print(f"✅ CANCEL: Status: {booking.status}, Refund: {refund_amount}")
        print(f"✅ CANCEL: Slot now available: {booking.playground.name} - {booking.booking_date} {booking.start_time}-{booking.end_time}")
        
        return JsonResponse({
            'success': True,
            'message': 'Booking cancelled successfully',
            'refund_amount': float(refund_amount) if refund_amount else 0,
            'status': booking.status
        })
        
    except Exception as e:
        print(f"❌ CANCEL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def cancel_booking_by_id(request, booking_id):
    """
    Cancel a booking using integer ID with proper validation and refund handling
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check permissions
        if booking.user != request.user and booking.playground.owner != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        # Check if booking can be cancelled
        if not booking.can_be_cancelled():
            return JsonResponse({'success': False, 'error': 'This booking cannot be cancelled'})
        
        # Parse cancellation data
        data = json.loads(request.body) if request.body else {}
        cancellation_reason = data.get('reason', 'User cancelled')
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = cancellation_reason
        
        # Handle refund logic based on cancellation policy
        refund_amount = booking.calculate_refund_amount()
        booking.refund_amount = refund_amount
        booking.refund_status = 'pending' if refund_amount > 0 else 'not_applicable'
        
        booking.save()
        
        print(f"✅ CANCEL BY ID: Booking #{booking.id} cancelled successfully")
        print(f"✅ CANCEL BY ID: Status: {booking.status}, Refund: {refund_amount}")
        print(f"✅ CANCEL BY ID: Slot now available: {booking.playground.name} - {booking.booking_date} {booking.start_time}-{booking.end_time}")
        
        return JsonResponse({
            'success': True,
            'message': 'Booking cancelled successfully',
            'refund_amount': float(refund_amount) if refund_amount else 0,
            'status': booking.status
        })
        
    except Exception as e:
        print(f"❌ CANCEL BY ID ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def get_available_slots(request, playground_id):
    """
    Get available time slots for a playground on a specific date with real-time validation
    """
    playground = get_object_or_404(Playground, id=playground_id)
    booking_date = request.GET.get('date')
    
    if not booking_date:
        return JsonResponse({'success': False, 'error': 'Date is required'})
    
    try:
        date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        day_name = date_obj.strftime('%A').lower()
        
        # Get operating hours for the day
        operating_hours = playground.operating_hours or {}
        day_hours = operating_hours.get(day_name)
        
        if not day_hours or not day_hours.get('active', True):
            return JsonResponse({
                'success': True,
                'slots': [],
                'message': 'Playground is closed on this day'
            })
        
        # Get all time slots for the day
        time_slots = playground.time_slots.filter(
            day_of_week=day_name,
            is_available=True
        ).order_by('start_time')
        
        available_slots = []
        current_time = timezone.now().time()
        
        for slot in time_slots:
            # Check if slot is already booked
            existing_bookings = Booking.objects.filter(
                playground=playground,
                booking_date=date_obj,
                start_time__lt=slot.end_time,
                end_time__gt=slot.start_time,
                status__in=['confirmed', 'pending']
            ).count()
            
            is_available = existing_bookings < slot.max_bookings
            
            # Check if slot is in the past
            if date_obj == date.today() and slot.start_time <= current_time:
                is_available = False
            
            # Check if date is too far in advance
            if date_obj > date.today() + timedelta(days=playground.advance_booking_days):
                is_available = False
            
            available_slots.append({
                'id': slot.id,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'price': float(slot.get_effective_price()),
                'is_available': is_available,
                'booked_count': existing_bookings,
                'max_bookings': slot.max_bookings,
                'reason': 'past_time' if date_obj == date.today() and slot.start_time <= current_time else 
                         'too_far' if date_obj > date.today() + timedelta(days=playground.advance_booking_days) else
                         'booked' if existing_bookings >= slot.max_bookings else None
            })
        
        return JsonResponse({
            'success': True,
            'slots': available_slots,
            'operating_hours': day_hours,
            'playground': {
                'name': playground.name,
                'price_per_hour': float(playground.price_per_hour),
                'auto_approval': playground.auto_approval,
                'instant_booking': playground.instant_booking
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def upload_payment_receipt(request, booking_id):
    """
    Upload payment receipt for a booking
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST' and request.FILES.get('receipt'):
        try:
            booking.payment_receipt = request.FILES['receipt']
            booking.payment_status = 'receipt_uploaded'
            booking.payment_reference = request.POST.get('reference', '')
            booking.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Payment receipt uploaded successfully. It will be verified by the playground owner.',
                'receipt_url': booking.payment_receipt.url if booking.payment_receipt else None
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request or no file provided'})


@login_required
def booking_history(request):
    """
    Display user's booking history with filters and pagination
    """
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    playground_filter = request.GET.get('playground')
    
    # Base queryset
    bookings = Booking.objects.filter(user=user).select_related('playground')
    
    # Apply filters
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    
    if date_from:
        bookings = bookings.filter(booking_date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
    
    if date_to:
        bookings = bookings.filter(booking_date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
    
    if playground_filter:
        bookings = bookings.filter(playground__name__icontains=playground_filter)
    
    # Order by date
    bookings = bookings.order_by('-booking_date', '-start_time')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'playground_filter': playground_filter,
    }
    
    return render(request, 'bookings/booking_history.html', context)


# Original template views for compatibility
class BookPlaygroundView(TemplateView):
    template_name = 'booking/book.html'

class ConfirmBookingView(TemplateView):
    template_name = 'booking/confirm.html'

class PaymentView(TemplateView):
    template_name = 'bookings/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')
        try:
            booking = Booking.objects.select_related('playground', 'user').get(booking_id=booking_id)
            context['booking'] = booking
            # Bank details for payment
            context['bank_number'] = '64676465464616'
        except Booking.DoesNotExist:
            context['error'] = 'Booking not found'
        return context

@require_http_methods(["GET"])
def get_payment_page(request, playground_id):
    """
    API endpoint to get payment page data with dynamic payment methods
    """
    try:
        playground = get_object_or_404(Playground, id=playground_id)
        
        # Get payment configuration for this playground
        try:
            payment_config = PlaygroundPaymentConfig.objects.get(playground=playground)
        except PlaygroundPaymentConfig.DoesNotExist:
            # Create default payment config if none exists
            payment_config = PlaygroundPaymentConfig.objects.create(
                playground=playground,
                bank_name="Default Bank",
                account_name=playground.name,
                account_number="1234567890"
            )
        
        # Get active payment methods for this playground
        payment_methods = []
        playground_methods = PlaygroundPaymentMethod.objects.filter(
            playground_config=payment_config,
            is_enabled=True,
            payment_method__is_active=True
        ).select_related('payment_method')
        
        for pm in playground_methods:
            method = pm.payment_method
            payment_methods.append({
                'id': method.method_type,
                'name': method.name,
                'icon': get_payment_icon(method.method_type),
                'instructions': pm.custom_instructions or method.instructions,
                'requires_receipt': method.requires_receipt,
                'is_instant': method.is_instant,
                'processing_fee': float(pm.processing_fee_percentage)
            })
        
        # If no payment methods configured, add default ones
        if not payment_methods:
            payment_methods = [
                {'id': 'bank_transfer', 'name': 'Bank Transfer', 'icon': 'fas fa-university', 'instructions': 'Transfer to our bank account', 'requires_receipt': True, 'is_instant': False, 'processing_fee': 0.0},
                {'id': 'cash_on_delivery', 'name': 'Cash Payment', 'icon': 'fas fa-money-bill-wave', 'instructions': 'Pay at the venue', 'requires_receipt': False, 'is_instant': True, 'processing_fee': 0.0},
            ]
        
        # Prepare bank details
        bank_details = None
        if payment_config.bank_name:
            bank_details = {
                'account_number': payment_config.account_number,
                'bank_name': payment_config.bank_name,
                'account_name': payment_config.account_name,
                'routing_number': payment_config.routing_number,
                'mobile_banking_number': payment_config.mobile_banking_number,
                'mobile_banking_type': payment_config.mobile_banking_type,
            }
        
        return JsonResponse({
            'success': True,
            'playground': {
                'id': playground.id,
                'name': playground.name,
                'currency': playground.currency,
            },
            'payment_methods': payment_methods,
            'bank_details': bank_details,
            'payment_config': {
                'auto_approve': payment_config.auto_approve_payments,
                'deadline_hours': payment_config.payment_deadline_hours,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_payment_icon(method_type):
    """Get appropriate icon for payment method type"""
    icons = {
        'bank_transfer': 'fas fa-university',
        'mobile_banking': 'fas fa-mobile-alt',
        'digital_wallet': 'fas fa-wallet',
        'cash_on_delivery': 'fas fa-money-bill-wave',
    }
    return icons.get(method_type, 'fas fa-credit-card')

# BookingSuccessView removed - success flow now handled dynamically in checkout.html without page redirects

class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/booking_history.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Bookings'
        return context

class BookingDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/booking_detail.html'
    login_url = '/login/'

class CancelBookingView(TemplateView):
    template_name = 'booking/cancel.html'

class AddReviewView(TemplateView):
    template_name = 'booking/add_review.html'

@csrf_exempt
def get_time_slots(request):
    """Legacy function - now redirects to new API"""
    playground_id = request.GET.get('playground_id')
    date_param = request.GET.get('date')
    
    if playground_id and date_param:
        return get_available_slots(request, playground_id)
    
    return JsonResponse({'slots': []})

@csrf_exempt
def calculate_price(request):
    """Calculate booking price dynamically with amenities, membership passes, and custom slots"""
    
    # Import required models at function start to avoid scope issues
    from playgrounds.models import Amenity
    
    try:
        from playgrounds.models import DurationPass as MembershipPass
    except ImportError:
        MembershipPass = None  # Handle case where model doesn't exist
    
    try:
        playground_id = request.GET.get('playground_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        date_param = request.GET.get('date')
        
        # NEW: Get additional parameters for comprehensive calculation
        amenity_ids = request.GET.get('amenity_ids', '')
        membership_pass_id = request.GET.get('membership_pass_id')
        custom_slot_id = request.GET.get('custom_slot_id')
        custom_slot_time = request.GET.get('custom_slot_time')
        booking_types = request.GET.get('booking_types', '')
        
        if not playground_id:
            return JsonResponse({'success': False, 'error': 'Playground ID required'})
        
        playground = get_object_or_404(Playground, id=playground_id)
        
        # Helper function to convert time format
        def convert_time_format(time_str):
            """Convert time string to 24-hour format if it contains AM/PM"""
            time_str = time_str.strip()
            
            # If already in 24-hour format, return as is
            if not any(x in time_str.upper() for x in ['AM', 'PM']):
                return time_str
            
            # Parse 12-hour format
            match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str.upper())
            if not match:
                return time_str  # Return original if parsing fails
            
            hours, minutes, period = match.groups()
            hours = int(hours)
            
            if period == 'AM' and hours == 12:
                hours = 0
            elif period == 'PM' and hours != 12:
                hours += 12
            
            return f"{hours:02d}:{minutes}"

        # Initialize calculations
        base_price = Decimal('0.00')
        amenity_fees = Decimal('0.00')
        total_duration = 0
        
        # ✅ CRITICAL FIX: Handle custom slot pricing FIRST (takes priority)
        if custom_slot_id and custom_slot_time:
            print(f"🔍 Processing custom slot: ID={custom_slot_id}, Time={custom_slot_time}")
            
            # Custom slots are not DB records - use hardcoded pricing for now
            # TODO: Make this configurable in playground settings
            base_price = Decimal('25.00')  # Custom slot price
            print(f"✅ Custom slot pricing applied: RM {base_price}")
            
            # Parse duration from custom slot time if available
            if ' - ' in custom_slot_time:
                time_parts = custom_slot_time.split(' - ')
                if len(time_parts) == 2:
                    start_time = convert_time_format(time_parts[0])
                    end_time = convert_time_format(time_parts[1])
                    
                    start_dt = datetime.strptime(start_time, '%H:%M').time()
                    end_dt = datetime.strptime(end_time, '%H:%M').time()
                    
                    start_datetime = datetime.combine(date.today(), start_dt)
                    end_datetime = datetime.combine(date.today(), end_dt)
                    
                    if end_datetime <= start_datetime:
                        end_datetime += timedelta(days=1)
                    
                    total_duration = (end_datetime - start_datetime).total_seconds() / 3600
        
        # Calculate base price based on time slots (ONLY if not custom slot)
        if not custom_slot_id and start_time and end_time:
            # Convert time formats
            start_time = convert_time_format(start_time)
            end_time = convert_time_format(end_time)
            
            # Calculate duration
            start_dt = datetime.strptime(start_time, '%H:%M').time()
            end_dt = datetime.strptime(end_time, '%H:%M').time()
            
            start_datetime = datetime.combine(date.today(), start_dt)
            end_datetime = datetime.combine(date.today(), end_dt)
            
            if end_datetime <= start_datetime:
                end_datetime += timedelta(days=1)
            
            total_duration = (end_datetime - start_datetime).total_seconds() / 3600
            
            # Calculate base price using playground's rate
            price_per_hour = playground.price_per_hour
            base_price = price_per_hour * Decimal(str(total_duration))
            print(f"✅ Regular slot calculation: Duration={total_duration}h, Rate={price_per_hour}, Price={base_price}")
        
        # Handle membership pass pricing
        if membership_pass_id and MembershipPass:
            try:
                membership_pass = MembershipPass.objects.get(id=membership_pass_id)
                # For membership passes, we might have different pricing logic
                # For now, add the pass price to the base calculation
                base_price += membership_pass.price
                print(f"✅ Membership pass added: ID={membership_pass_id}, Price={membership_pass.price}")
            except MembershipPass.DoesNotExist:
                print(f"❌ Membership pass not found: ID={membership_pass_id}")
            except Exception as e:
                print(f"❌ Error processing membership pass: {e}")
        
        # Calculate amenity fees with simplified approach for JSON amenities
        if amenity_ids:
            amenity_id_list = []
            json_amenity_fees = Decimal('0.00')
            
            # Get playground amenities (JSON data) for fallback
            playground_amenities = []
            try:
                if hasattr(playground, 'amenities') and playground.amenities:
                    playground_amenities = playground.amenities if isinstance(playground.amenities, list) else []
            except:
                pass
            
            for id_str in amenity_ids.split(','):
                id_str = id_str.strip()
                if id_str:
                    try:
                        # Try to convert to integer for DB amenities
                        amenity_id = int(id_str)
                        amenity_id_list.append(amenity_id)
                    except ValueError:
                        # Handle generated IDs for JSON amenities (like 'p_professionalcoaching_0')
                        print(f"Processing JSON amenity ID: {id_str}")
                        
                        # Extract info from generated ID - simplified approach
                        if '_' in id_str:
                            parts = id_str.split('_')
                            if len(parts) >= 3:
                                try:
                                    index = int(parts[2])
                                    # Get amenity by index from playground amenities
                                    if 0 <= index < len(playground_amenities):
                                        amenity = playground_amenities[index]
                                        amenity_price_str = amenity.get('price')
                                        
                                        # Handle both None (free) and string prices
                                        if amenity_price_str is not None:
                                            try:
                                                amenity_price = float(amenity_price_str)
                                                json_amenity_fees += Decimal(str(amenity_price))
                                                print(f"✅ Found JSON amenity by index {index}: {amenity.get('name')} - RM {amenity_price}")
                                            except (ValueError, TypeError):
                                                print(f"⚠️ Invalid price format for amenity {index}: {amenity_price_str}")
                                        else:
                                            print(f"🆓 Free amenity {index}: {amenity.get('name')} - RM 0")
                                except (ValueError, IndexError) as e:
                                    print(f"❌ Could not process amenity ID: {id_str} - Error: {e}")
                                    continue
            
            # Get DB amenities if any
            if amenity_id_list:
                amenities = Amenity.objects.filter(id__in=amenity_id_list)
                db_amenity_fees = sum(amenity.price for amenity in amenities)
                amenity_fees = db_amenity_fees + json_amenity_fees
                print(f"DB amenity fees: {db_amenity_fees}, JSON amenity fees: {json_amenity_fees}")
            else:
                amenity_fees = json_amenity_fees
                
            print(f"Total calculated amenity fees: {amenity_fees} for IDs: {amenity_ids}")
        
        # Calculate final totals
        discount_amount = Decimal('0.00')  # Can add discount logic here
        subtotal = base_price - discount_amount
        total_with_amenities = subtotal + amenity_fees
        
        return JsonResponse({
            'success': True,
            'subtotal': float(subtotal),  # ✅ Match frontend expectations
            'total_amount': float(total_with_amenities),  # ✅ Match frontend expectations
            'amenity_fees': float(amenity_fees), 
            'discount_amount': float(discount_amount),
            'duration': total_duration,  # ✅ Add duration field that frontend expects
            'duration_hours': total_duration,
            'price_per_hour': float(playground.price_per_hour),
            'currency': playground.currency,
            'slot_type': 'custom' if custom_slot_id else 'regular',  # ✅ Add slot type
            'breakdown': {
                'subtotal': float(subtotal),
                'amenities': float(amenity_fees),
                'total': float(total_with_amenities)
            }
        })
        
    except Exception as e:
        print(f"Error in calculate_price: {e}")  # For debugging
        return JsonResponse({'success': False, 'error': str(e)})


def booking_history(request):
    """Display user's booking history with filtering and pagination"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date', 'all')
    
    # Base queryset
    bookings = Booking.objects.filter(user=request.user).select_related(
        'playground', 'playground__city', 'playground__city__state'
    ).order_by('-booked_at')
    
    # Apply filters
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    
    if date_filter == 'upcoming':
        bookings = bookings.filter(booking_date__gte=timezone.now().date())
    elif date_filter == 'past':
        bookings = bookings.filter(booking_date__lt=timezone.now().date())
    elif date_filter == 'this_month':
        now = timezone.now()
        bookings = bookings.filter(
            booking_date__year=now.year,
            booking_date__month=now.month
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'total_bookings': bookings.count(),
    }
    
    return render(request, 'bookings/booking_history.html', context)


def reschedule_booking(request, booking_id):
    """Handle booking rescheduling"""
    try:
        booking = Booking.objects.get(
            booking_id=booking_id,
            user=request.user
        )
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect('bookings:booking_dashboard')
    
    # Check if rescheduling is allowed
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "This booking cannot be rescheduled.")
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    # Check if it's not too late to reschedule
    # Make the booking datetime timezone-aware to match timezone.now()
    booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
    
    # Check if the datetime is naive (no timezone info) and make it aware
    if booking_datetime.tzinfo is None:
        booking_datetime = timezone.make_aware(booking_datetime, timezone.get_current_timezone())
    
    hours_until_booking = (booking_datetime - timezone.now()).total_seconds() / 3600
    
    if hours_until_booking < 2:
        messages.error(request, "Cannot reschedule booking less than 2 hours before start time.")
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        try:
            new_date = request.POST.get('new_date')
            new_start_time = request.POST.get('new_start_time')
            new_end_time = request.POST.get('new_end_time')
            
            # Validate new slot availability
            new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
            new_start_time_obj = datetime.strptime(new_start_time, '%H:%M').time()
            new_end_time_obj = datetime.strptime(new_end_time, '%H:%M').time()
            
            # Check for conflicts
            conflicts = Booking.objects.filter(
                playground=booking.playground,
                booking_date=new_date_obj,
                status__in=['confirmed', 'pending'],
                start_time__lt=new_end_time_obj,
                end_time__gt=new_start_time_obj
            ).exclude(id=booking.id)
            
            if conflicts.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'The selected time slot is not available.'
                })
            
            # Update booking
            booking.booking_date = new_date_obj
            booking.start_time = new_start_time_obj
            booking.end_time = new_end_time_obj
            booking.save()
            
            # Get currency symbol from playground's currency
            from django.conf import settings
            
            # Currency mapping for symbols
            currency_symbols = {
                'BDT': '৳',
                'USD': '$',
                'EUR': '€',
                'GBP': '£',
                'INR': '₹',
                'JPY': '¥',
                'CNY': '¥',
                'AUD': 'A$',
                'CAD': 'C$',
                'CHF': 'CHF',
                'MYR': 'RM',
                'SGD': 'S$',
            }
            
            # Get playground's currency or fallback to settings
            playground_currency = booking.playground.currency if hasattr(booking.playground, 'currency') else getattr(settings, 'CURRENCY', 'BDT')
            currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
            
            print(f"💰 DEBUG: Playground currency: {playground_currency}")
            print(f"💰 DEBUG: Currency symbol: {currency_symbol}")
            
            response_data = {
                'success': True,
                'message': 'Booking rescheduled successfully.',
                'currency_symbol': currency_symbol,
                'currency_code': playground_currency,
                'total_amount': str(booking.total_amount),
                'booking_id': str(booking.booking_id)
            }
            print(f"💰 DEBUG: Reschedule response data: {response_data}")
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to reschedule booking: {str(e)}'
            })
    
    # Get currency symbol from playground's currency
    from django.conf import settings
    
    # Currency mapping for symbols
    currency_symbols = {
        'BDT': '৳',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'MYR': 'RM',
        'SGD': 'S$',
    }
    
    # Get playground's currency or fallback to settings
    playground_currency = booking.playground.currency if hasattr(booking.playground, 'currency') else getattr(settings, 'CURRENCY', 'BDT')
    currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
    
    context = {
        'booking': booking,
        'today': timezone.now().date(),
        'currency_symbol': currency_symbol,
        'currency_code': playground_currency,
    }
    
    return render(request, 'bookings/reschedule_booking.html', context)


def reschedule_booking_by_id(request, booking_id):
    """Handle booking rescheduling using integer ID"""
    try:
        booking = Booking.objects.get(
            id=booking_id,
            user=request.user
        )
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect('bookings:booking_dashboard')
    
    # Check if rescheduling is allowed
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "This booking cannot be rescheduled.")
        return redirect('bookings:booking_detail_by_id', booking_id=booking_id)
    
    # Check if it's not too late to reschedule
    hours_until_booking = (
        datetime.combine(booking.booking_date, booking.start_time) - 
        timezone.now()
    ).total_seconds() / 3600
    
    if hours_until_booking < 2:
        messages.error(request, "Cannot reschedule booking less than 2 hours before start time.")
        return redirect('bookings:booking_detail_by_id', booking_id=booking_id)
    
    if request.method == 'POST':
        try:
            new_date = request.POST.get('new_date')
            new_start_time = request.POST.get('new_start_time')
            new_end_time = request.POST.get('new_end_time')
            
            # Validate new slot availability
            new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
            new_start_time_obj = datetime.strptime(new_start_time, '%H:%M').time()
            new_end_time_obj = datetime.strptime(new_end_time, '%H:%M').time()
            
            # Check for conflicts
            conflicts = Booking.objects.filter(
                playground=booking.playground,
                booking_date=new_date_obj,
                status__in=['confirmed', 'pending'],
                start_time__lt=new_end_time_obj,
                end_time__gt=new_start_time_obj
            ).exclude(id=booking.id)
            
            if conflicts.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'The selected time slot is not available.'
                })
            
            # Update booking
            booking.booking_date = new_date_obj
            booking.start_time = new_start_time_obj
            booking.end_time = new_end_time_obj
            booking.save()
            
            # Get currency symbol from playground's currency
            from django.conf import settings
            
            # Currency mapping for symbols
            currency_symbols = {
                'BDT': '৳',
                'USD': '$',
                'EUR': '€',
                'GBP': '£',
                'INR': '₹',
                'JPY': '¥',
                'CNY': '¥',
                'AUD': 'A$',
                'CAD': 'C$',
                'CHF': 'CHF',
                'MYR': 'RM',
                'SGD': 'S$',
            }
            
            # Get playground's currency or fallback to settings
            playground_currency = booking.playground.currency if hasattr(booking.playground, 'currency') else getattr(settings, 'CURRENCY', 'BDT')
            currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
            
            return JsonResponse({
                'success': True,
                'message': 'Booking rescheduled successfully.',
                'currency_symbol': currency_symbol,
                'currency_code': playground_currency,
                'total_amount': str(booking.total_amount),
                'booking_id': booking.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to reschedule booking: {str(e)}'
            })
    
    # Get currency symbol from playground's currency
    from django.conf import settings
    
    # Currency mapping for symbols
    currency_symbols = {
        'BDT': '৳',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'MYR': 'RM',
        'SGD': 'S$',
    }
    
    # Get playground's currency or fallback to settings
    playground_currency = booking.playground.currency if hasattr(booking.playground, 'currency') else getattr(settings, 'CURRENCY', 'BDT')
    currency_symbol = currency_symbols.get(playground_currency, playground_currency + ' ')
    
    context = {
        'booking': booking,
        'currency_symbol': currency_symbol,
        'currency_code': playground_currency,
    }
    
    return render(request, 'bookings/reschedule_booking.html', context)


def get_booking_stats(request):
    """Get booking statistics for dashboard"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    user_bookings = Booking.objects.filter(user=request.user)
    
    stats = {
        'total_bookings': user_bookings.count(),
        'pending_bookings': user_bookings.filter(status='pending').count(),
        'confirmed_bookings': user_bookings.filter(status='confirmed').count(),
        'completed_bookings': user_bookings.filter(status='completed').count(),
        'cancelled_bookings': user_bookings.filter(status='cancelled').count(),
        'upcoming_bookings': user_bookings.filter(
            booking_date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).count(),
        'total_spent': user_bookings.filter(
            payment_status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or 0,
    }
    
    # Recent bookings
    recent_bookings = user_bookings.select_related(
        'playground', 'playground__city'
    ).order_by('-booked_at')[:5]
    
    stats['recent_bookings'] = [
        {
            'id': str(booking.booking_id),
            'playground_name': booking.playground.name,
            'date': booking.booking_date.strftime('%Y-%m-%d'),
            'time': f"{booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}",
            'status': booking.status,
            'amount': str(booking.final_amount),
        }
        for booking in recent_bookings
    ]
    
    return JsonResponse(stats)


@csrf_exempt
@require_http_methods(["POST"])
def create_booking_api(request):
    """
    API endpoint to create a new booking with payment and receipt handling
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)
        
        # Handle both JSON and FormData requests
        if request.content_type and 'application/json' in request.content_type:
            # JSON request
            try:
                data = json.loads(request.body.decode('utf-8'))
            except UnicodeDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Unable to decode request body. Please check your data encoding.'
                }, status=400)
        else:
            # FormData request (with file uploads)
            data = dict(request.POST)
            # Convert lists to single values
            for key, value in data.items():
                if isinstance(value, list) and len(value) == 1:
                    data[key] = value[0]
        
        playground_id = data.get('playground_id')
        booking_date = data.get('booking_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        number_of_players = data.get('number_of_players')
        total_amount = data.get('total_amount')
        payment_method = data.get('payment_method')
        
        # Get booking type information for proper storage
        booking_type = data.get('booking_type', 'regular')
        custom_slot_id = data.get('custom_slot_id')
        membership_pass_id = data.get('membership_pass_id')
        
        # Validate required fields
        if not all([playground_id, booking_date, start_time, end_time, number_of_players, total_amount, payment_method]):
            missing_fields = []
            if not playground_id: missing_fields.append('playground_id')
            if not booking_date: missing_fields.append('booking_date')
            if not start_time: missing_fields.append('start_time')
            if not end_time: missing_fields.append('end_time')
            if not number_of_players: missing_fields.append('number_of_players')
            if not total_amount: missing_fields.append('total_amount')
            if not payment_method: missing_fields.append('payment_method')
            
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        # Get playground
        playground = get_object_or_404(Playground, id=playground_id)
        
        # Parse date and time
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        
        # Check for conflicts
        conflicts = Booking.objects.filter(
            playground=playground,
            booking_date=booking_date_obj,
            status__in=['confirmed', 'pending'],
            start_time__lt=end_time_obj,
            end_time__gt=start_time_obj
        )
        
        if conflicts.exists():
            return JsonResponse({
                'success': False,
                'error': 'Time slot is no longer available'
            }, status=409)
        
        # Calculate duration for additional fields
        # Check if custom duration is provided (for custom slots/membership passes)
        custom_duration = data.get('duration_hours')
        if custom_duration:
            try:
                duration_hours = float(custom_duration)
            except (ValueError, TypeError):
                duration_hours = 1.0  # Default fallback
        else:
            # Calculate from time difference for regular slots
            start_datetime = datetime.combine(booking_date_obj, start_time_obj)
            end_datetime = datetime.combine(booking_date_obj, end_time_obj)
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
        
        # Parse selected amenities from request data
        # If coming from FormData, selected_amenities will be a JSON string that needs parsing
        selected_amenities = data.get('selected_amenities', [])
        print(f"🔍 DEBUG: Raw selected_amenities from request: {selected_amenities}")
        print(f"🔍 DEBUG: Type of selected_amenities: {type(selected_amenities)}")
        
        if isinstance(selected_amenities, str):
            try:
                selected_amenities = json.loads(selected_amenities) if selected_amenities else []
                print(f"✅ DEBUG: Parsed amenities from JSON string: {selected_amenities}")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"❌ DEBUG: Failed to parse amenities JSON: {e}")
                print(f"❌ DEBUG: Corrupted string received: {repr(selected_amenities[:100])}")
                
                # ⚠️ EMERGENCY FALLBACK: If string looks like "[object Object]", try to parse from amenity_ids
                if '[object Object]' in selected_amenities:
                    print(f"⚠️ DEBUG: Detected corrupted [object Object] string - browser cache issue!")
                    print(f"⚠️ DEBUG: User needs to clear browser cache or use incognito window")
                    print(f"⚠️ DEBUG: JavaScript fix is NOT loading due to aggressive browser caching")
                
                selected_amenities = []
        
        print(f"🎯 DEBUG: Final selected_amenities to save: {selected_amenities}")
        print(f"🎯 DEBUG: Number of amenities: {len(selected_amenities) if isinstance(selected_amenities, list) else 0}")
        
        # Prepare structured booking information
        booking_info = {
            'booking_type': booking_type,
            'slot_type': data.get('slot_type', 'regular'),
            'time_slot_type': data.get('time_slot_type', 'regular_slot'),
            'selected_amenities': selected_amenities,  # SAVE AMENITIES TO DATABASE
        }
        
        # Add type-specific information
        if booking_type == 'custom_slot' and custom_slot_id:
            booking_info.update({
                'custom_slot_id': custom_slot_id,
                'slot_id': custom_slot_id,
                'custom_slot_name': data.get('custom_slot_name', ''),
                'actual_time': data.get('custom_slot_actual_time', ''),
                'custom_slot_duration': data.get('custom_slot_duration', duration_hours)
            })
        elif booking_type == 'membership_pass' and membership_pass_id:
            booking_info.update({
                'membership_pass_id': membership_pass_id,
                'pass_id': membership_pass_id,
                'pass_name': data.get('membership_pass_name', ''),
                'pass_duration_type': data.get('pass_duration_type', ''),
                'pass_duration_days': data.get('pass_duration_days', '')
            })
            
        # Store as JSON for easy retrieval
        import json as json_module
        special_requests_text = json_module.dumps(booking_info)

        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            playground=playground,
            booking_date=booking_date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            duration_hours=duration_hours,
            number_of_players=int(number_of_players),
            total_amount=Decimal(str(total_amount)),
            final_amount=Decimal(str(total_amount)),
            price_per_hour=playground.price_per_hour,
            payment_method=payment_method,
            special_requests=special_requests_text,
            status='pending',
            payment_status='pending'
        )
        
        # Handle receipt upload for bank transfers
        if request.FILES.get('receipt'):
            booking.payment_receipt = request.FILES['receipt']
            booking.payment_status = 'receipt_uploaded'
            booking.save()
        
        # Auto-approve based on payment method
        if payment_method == 'cash_on_delivery':
            booking.status = 'confirmed'
            booking.payment_status = 'pending_cash'
            booking.save()
        elif payment_method in ['bank_transfer', 'mobile_banking'] and request.FILES.get('receipt'):
            booking.status = 'confirmed'
            booking.payment_status = 'receipt_uploaded'
            booking.save()
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'message': 'Booking created successfully! Your reservation has been confirmed.',
            'redirect_url': f'/bookings/{booking.id}/',
            'booking_detail_url': f'/bookings/{booking.id}/',
            'booking_dashboard_url': '/bookings/',
            'booking': {
                'id': booking.id,
                'booking_id': booking.booking_id,
                'playground_name': playground.name,
                'date': booking_date,
                'start_time': start_time,
                'end_time': end_time,
                'amount': float(total_amount),
                'status': booking.status,
                'payment_status': booking.payment_status,
                'duration_hours': duration_hours,
                'number_of_players': int(number_of_players),
                'payment_method': payment_method,
                'booking_type': booking_type,
                'slot_type': data.get('slot_type', 'regular'),
                'special_requests': special_requests_text,
                # Add custom slot information if applicable
                'custom_slot_name': data.get('custom_slot_name', '') if booking_type == 'custom_slot' else None,
                'custom_slot_id': custom_slot_id if booking_type == 'custom_slot' else None,
                # Add membership pass information if applicable
                'membership_pass_name': data.get('membership_pass_name', '') if booking_type == 'membership_pass' else None,
                'membership_pass_id': membership_pass_id if booking_type == 'membership_pass' else None,
                'pass_duration_days': data.get('pass_duration_days', '') if booking_type == 'membership_pass' else None,
                'pass_duration_type': data.get('pass_duration_type', '') if booking_type == 'membership_pass' else None,
                # Add amenities if present
                'selected_amenities': data.get('selected_amenities', [])
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format. Please check your request data.'
        }, status=400)
    except UnicodeDecodeError as e:
        return JsonResponse({
            'success': False,
            'error': f'Text encoding error: {str(e)}. Please ensure your data is properly encoded.'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)
