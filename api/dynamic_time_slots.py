from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def generate_dynamic_time_slots(request):
    """
    Generate dynamic time slots based on playground configuration
    """
    try:
        data = json.loads(request.body)
        
        # Check if this is day-wise generation (new format)
        if 'day_wise_hours' in data:
            return generate_daywise_time_slots(request)
        
        # Extract parameters for legacy format
        start_time = data.get('start_time', '09:00')
        end_time = data.get('end_time', '21:00')
        slot_duration = int(data.get('slot_duration', 60))  # minutes
        break_duration = int(data.get('break_duration', 15))  # minutes
        selected_days = data.get('selected_days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        base_price = float(data.get('base_price', 25.0))
        playground_type = data.get('playground_type', 'football')
        
        # Extract currency parameters (CRITICAL FIX)
        currency_code = data.get('currency_code', 'USD')
        currency_symbol = data.get('currency_symbol', '$')
        currency_decimal_places = int(data.get('currency_decimal_places', 2))
        
        # Generate slots for each selected day
        all_slots = []
        slot_id_counter = 1
        
        # Day mapping
        day_mapping = {
            'monday': 'Monday',
            'tuesday': 'Tuesday', 
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday',
            'sunday': 'Sunday'
        }
        
        for day_key in selected_days:
            day_name = day_mapping.get(day_key, day_key.capitalize())
            
            # Parse start and end times
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            # Create datetime objects for calculation
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            
            current_dt = start_dt
            
            while current_dt < end_dt:
                # Calculate slot end time
                slot_end_dt = current_dt + timedelta(minutes=slot_duration)
                
                # Break if slot would exceed end time - FIX: Allow slots that end exactly at closing time
                if slot_end_dt > end_dt:
                    break
                
                # Remove automatic peak/premium pricing - owner will set these manually
                pricing_tier = 'regular'
                price_multiplier = 1.0
                
                # Calculate final price (only regular pricing for auto-generated slots)
                final_price = base_price * price_multiplier
                
                # Format price with currency decimal places
                formatted_price = f"{final_price:.{currency_decimal_places}f}"
                
                # Create slot object
                slot = {
                    'id': f'{day_key}_{slot_id_counter}',
                    'day': day_name,
                    'day_key': day_key,
                    'start_time': current_dt.strftime('%H:%M'),
                    'end_time': slot_end_dt.strftime('%H:%M'),
                    'duration_minutes': slot_duration,
                    'price': round(final_price, currency_decimal_places),
                    'base_price': base_price,
                    'pricing_tier': pricing_tier,
                    'price_multiplier': price_multiplier,
                    'is_available': True,
                    'type': 'auto_generated',
                    'playground_type': playground_type,
                    'created_at': datetime.now().isoformat(),
                    # Currency data (CRITICAL ADDITION)
                    'currency_code': currency_code,
                    'currency_symbol': currency_symbol,
                    'currency_decimal_places': currency_decimal_places,
                    'formatted_price': formatted_price
                }
                
                all_slots.append(slot)
                slot_id_counter += 1
                
                # Move to next slot (including break time)
                current_dt = slot_end_dt + timedelta(minutes=break_duration)
        
        # Calculate summary statistics
        total_slots = len(all_slots)
        daily_revenue = sum(slot['price'] for slot in all_slots if slot['day_key'] == selected_days[0]) if selected_days else 0
        weekly_revenue = daily_revenue * len(selected_days)
        monthly_revenue = weekly_revenue * 4.33  # Average weeks per month
        
        # Group slots by day for organized display
        slots_by_day = {}
        for slot in all_slots:
            day_name = slot['day']
            if day_name not in slots_by_day:
                slots_by_day[day_name] = []
            slots_by_day[day_name].append(slot)
        
        response_data = {
            'success': True,
            'message': f'Generated {total_slots} dynamic time slots',
            'slots': all_slots,
            'slots_by_day': slots_by_day,
            'summary': {
                'total_slots': total_slots,
                'days_count': len(selected_days),
                'daily_revenue': round(daily_revenue, 2),
                'weekly_revenue': round(weekly_revenue, 2),
                'monthly_revenue': round(monthly_revenue, 2),
                'slot_duration': slot_duration,
                'break_duration': break_duration,
                'pricing_tiers': {
                    'regular': base_price,
                    'peak': round(base_price * 1.5, 2),
                    'premium': round(base_price * 2.0, 2)
                }
            },
            'configuration': {
                'start_time': start_time,
                'end_time': end_time,
                'slot_duration': slot_duration,
                'break_duration': break_duration,
                'selected_days': selected_days,
                'base_price': base_price,
                'playground_type': playground_type
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error generating dynamic time slots: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to generate time slots: {str(e)}',
            'message': 'Please check your input parameters and try again.'
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def add_custom_slot(request):
    """
    Add a custom time slot with dynamic pricing and real-time backend integration
    """
    try:
        data = json.loads(request.body)
        
        # Handle both delete and add operations
        action = data.get('action', 'add')
        
        if action == 'delete':
            slot_id = data.get('slot_id')
            return JsonResponse({
                'success': True,
                'message': f'Slot {slot_id} deleted successfully',
                'action': 'delete',
                'slot_id': slot_id
            })
        
        # Extract custom slot data for add operation
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        day = data.get('day', 'monday')
        day_name = data.get('day_name', day.capitalize())
        pricing_tier = data.get('pricing_tier', 'standard')
        custom_price = data.get('custom_price')
        base_price = float(data.get('base_price', 25.0))
        playground_type = data.get('playground_type', 'football')
        duration_minutes = int(data.get('duration_minutes', 60))
        
        # Extract currency parameters (CRITICAL FIX)
        currency_code = data.get('currency_code', 'USD')
        currency_symbol = data.get('currency_symbol', '$')
        currency_decimal_places = int(data.get('currency_decimal_places', 2))
        
        # Validate required fields
        if not all([start_time, end_time, day]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: start_time, end_time, day'
            }, status=400)
        
        # Calculate price based on tier
        if pricing_tier == 'custom' and custom_price:
            final_price = float(custom_price)
        elif pricing_tier == 'peak':
            final_price = base_price * 1.5
        elif pricing_tier == 'premium':
            final_price = base_price * 2.0
        else:  # standard
            final_price = base_price
        
        # Generate unique slot ID
        slot_id = f"custom_{day}_{start_time.replace(':', '')}_{end_time.replace(':', '')}_{int(datetime.now().timestamp())}"
        
        # Create custom slot object
        custom_slot = {
            'id': slot_id,
            'day': day_name,
            'day_key': day.lower(),
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': duration_minutes,
            'price': round(final_price, currency_decimal_places),
            'base_price': base_price,
            'pricing_tier': pricing_tier,
            'price_multiplier': round(final_price / base_price, 2),
            'is_available': True,
            'type': 'custom_created',
            'playground_type': playground_type,
            'currency_code': currency_code,
            'currency_symbol': currency_symbol,
            'currency_decimal_places': currency_decimal_places,
            'formatted_price': f"{final_price:.{currency_decimal_places}f}",
            'created_at': datetime.now().isoformat(),
            'is_custom': True
        }
        
        response_data = {
            'success': True,
            'message': f'Custom {pricing_tier} slot created successfully',
            'slot': custom_slot,
            'action': 'add',
            'pricing_info': {
                'tier': pricing_tier,
                'multiplier': round(final_price / base_price, 2),
                'currency': currency_code,
                'base_price': base_price,
                'final_price': round(final_price, 2)
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error adding custom slot: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to add custom slot: {str(e)}',
            'message': 'Please check your slot configuration and try again.'
        }, status=400)
        
        if not start_time or not end_time:
            return JsonResponse({
                'success': False,
                'error': 'Start time and end time are required'
            }, status=400)
        
        # Validate time format
        try:
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            
            if start_dt >= end_dt:
                return JsonResponse({
                    'success': False,
                    'error': 'End time must be after start time'
                }, status=400)
                
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid time format. Use HH:MM format'
            }, status=400)
        
        # Calculate duration
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        # Calculate price based on tier
        if pricing_tier == 'custom' and custom_price:
            final_price = float(custom_price)
            price_multiplier = final_price / base_price if base_price > 0 else 1.0
        elif pricing_tier == 'peak':
            final_price = base_price * 1.5
            price_multiplier = 1.5
        elif pricing_tier == 'premium':
            final_price = base_price * 2.0
            price_multiplier = 2.0
        else:  # regular
            final_price = base_price
            price_multiplier = 1.0
        
        # Create custom slot
        custom_slot = {
            'id': f'custom_{int(datetime.now().timestamp())}',
            'day': day.capitalize(),
            'day_key': day.lower(),
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': duration_minutes,
            'price': round(final_price, 2),
            'base_price': base_price,
            'pricing_tier': pricing_tier,
            'price_multiplier': price_multiplier,
            'is_available': True,
            'type': 'custom',
            'playground_type': playground_type,
            'created_at': datetime.now().isoformat(),
            'is_custom': True
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Custom {pricing_tier} slot added successfully',
            'slot': custom_slot,
            'summary': {
                'duration': f'{duration_minutes} minutes',
                'price': f'${final_price:.2f}',
                'tier': pricing_tier,
                'multiplier': f'{price_multiplier}x'
            }
        })
        
    except Exception as e:
        logger.error(f"Error adding custom slot: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to add custom slot: {str(e)}'
        }, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_playground_availability(request):
    """
    Get real-time availability for playground slots
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            playground_id = data.get('playground_id')
            date = data.get('date')
        else:
            playground_id = request.GET.get('playground_id')
            date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Simulate real-time availability (in real implementation, check database)
        availability_data = {
            'success': True,
            'date': date,
            'playground_id': playground_id,
            'available_slots': [],
            'booked_slots': [],
            'blocked_slots': [],
            'last_updated': datetime.now().isoformat()
        }
        
        # Generate sample availability data
        hours = range(9, 22)  # 9 AM to 9 PM
        for hour in hours:
            slot_time = f'{hour:02d}:00'
            # Simulate some slots being booked (every 3rd slot)
            is_available = hour % 3 != 0
            
            slot_data = {
                'time': slot_time,
                'is_available': is_available,
                'price': 25.0 if hour < 18 else 37.5,  # Peak pricing after 6 PM
                'duration': 60
            }
            
            if is_available:
                availability_data['available_slots'].append(slot_data)
            else:
                availability_data['booked_slots'].append(slot_data)
        
        return JsonResponse(availability_data)
        
    except Exception as e:
        logger.error(f"Error getting playground availability: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to get availability: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def generate_daywise_time_slots(request):
    """
    Generate time slots with individual day-wise hours
    """
    try:
        data = json.loads(request.body)
        
        # Extract day-wise parameters
        day_wise_hours = data.get('day_wise_hours', [])
        slot_duration = int(data.get('slot_duration', 60))  # minutes
        break_duration = int(data.get('break_duration', 15))  # minutes
        base_price = float(data.get('base_price', 25.0))
        playground_type = data.get('playground_type', 'football')
        
        # Extract currency parameters (CRITICAL FIX)
        currency_code = data.get('currency_code', 'USD')
        currency_symbol = data.get('currency_symbol', '$')
        currency_decimal_places = int(data.get('currency_decimal_places', 2))
        
        if not day_wise_hours:
            return JsonResponse({
                'success': False,
                'error': 'No day-wise hours provided'
            }, status=400)
        
        # Generate slots for each day with individual times
        all_slots = []
        slot_id_counter = 1
        
        for day_info in day_wise_hours:
            day_key = day_info.get('day', '').lower()
            day_name = day_info.get('day_name', day_key.capitalize())
            open_time = day_info.get('open_time', '09:00')
            close_time = day_info.get('close_time', '21:00')
            
            # Parse start and end times for this specific day
            start_hour, start_minute = map(int, open_time.split(':'))
            end_hour, end_minute = map(int, close_time.split(':'))
            
            # Create datetime objects for calculation
            start_dt = datetime.strptime(open_time, '%H:%M')
            end_dt = datetime.strptime(close_time, '%H:%M')
            
            current_dt = start_dt
            
            while current_dt < end_dt:
                # Calculate slot end time
                slot_end_dt = current_dt + timedelta(minutes=slot_duration)
                
                # Break if slot would exceed end time
                if slot_end_dt > end_dt:
                    break
                
                # Format price with currency decimal places
                formatted_price = f"{base_price:.{currency_decimal_places}f}"
                
                # Create slot object with individual day times and currency data
                slot = {
                    'id': f'{day_key}_{slot_id_counter}',
                    'day': day_name,
                    'day_key': day_key,
                    'start_time': current_dt.strftime('%H:%M'),
                    'end_time': slot_end_dt.strftime('%H:%M'),
                    'duration_minutes': slot_duration,
                    'price': round(base_price, currency_decimal_places),
                    'base_price': base_price,
                    'pricing_tier': 'regular',
                    'price_multiplier': 1.0,
                    'is_available': True,
                    'type': 'daywise_generated',
                    'playground_type': playground_type,
                    'created_at': datetime.now().isoformat(),
                    # Currency data (CRITICAL ADDITION)
                    'currency_code': currency_code,
                    'currency_symbol': currency_symbol,
                    'currency_decimal_places': currency_decimal_places,
                    'formatted_price': formatted_price
                }
                
                all_slots.append(slot)
                slot_id_counter += 1
                
                # Move to next slot (including break time)
                current_dt = slot_end_dt + timedelta(minutes=break_duration)
        
        # Calculate summary statistics
        total_slots = len(all_slots)
        daily_avg_revenue = sum(slot['price'] for slot in all_slots) / len(day_wise_hours) if day_wise_hours else 0
        weekly_revenue = daily_avg_revenue * len(day_wise_hours)
        monthly_revenue = weekly_revenue * 4.33  # Average weeks per month
        
        # Group slots by day for organized display
        slots_by_day = {}
        for slot in all_slots:
            day_name = slot['day']
            if day_name not in slots_by_day:
                slots_by_day[day_name] = []
            slots_by_day[day_name].append(slot)
        
        response_data = {
            'success': True,
            'message': f'Generated {total_slots} dynamic time slots with {currency_code} currency',
            'slots': all_slots,
            'slots_by_day': slots_by_day,
            'summary': {
                'total_slots': total_slots,
                'days_count': len(day_wise_hours),
                'daily_revenue': round(daily_avg_revenue, currency_decimal_places),
                'weekly_revenue': round(weekly_revenue, currency_decimal_places),
                'monthly_revenue': round(monthly_revenue, currency_decimal_places),
                'slot_duration': slot_duration,
                'break_duration': break_duration,
                'pricing_tiers': {
                    'regular': round(base_price, currency_decimal_places),
                    'peak': round(base_price * 1.5, currency_decimal_places),
                    'premium': round(base_price * 2.0, currency_decimal_places)
                }
            },
            'currency': {
                'code': currency_code,
                'symbol': currency_symbol,
                'decimal_places': currency_decimal_places
            },
            'configuration': {
                'day_wise_hours': day_wise_hours,
                'slot_duration': slot_duration,
                'break_duration': break_duration,
                'base_price': base_price,
                'playground_type': playground_type,
                'currency_code': currency_code,
                'currency_symbol': currency_symbol
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error generating daywise time slots: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to generate daywise slots: {str(e)}',
            'message': 'Please check your day-wise hours and try again.'
        }, status=400)
