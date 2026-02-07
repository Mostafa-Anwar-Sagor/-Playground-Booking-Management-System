"""
Professional Membership Passes API for Playground Booking System
Handles dynamic, real-time membership pass creation, management, and purchases
Designed for leagues, gyms, and professional playground owners
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from django.db.models import Q
from decimal import Decimal
import json
from datetime import datetime, timedelta

from playgrounds.models import Playground, DurationPass, PassPurchase, SportType
from accounts.models import User


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def membership_passes_api(request, playground_id=None, pass_id=None):
    """
    Professional Membership Passes API
    GET: Retrieve membership passes
    POST: Create new membership pass (supports temporary creation without playground)
    PUT: Update existing membership pass
    DELETE: Delete membership pass
    """
    
    if request.method == 'GET':
        return get_membership_passes(request, playground_id, pass_id)
    elif request.method == 'POST':
        return create_membership_pass(request, playground_id)
    elif request.method == 'PUT':
        return update_membership_pass(request, pass_id)
    elif request.method == 'DELETE':
        return delete_membership_pass(request, pass_id)


def get_membership_passes(request, playground_id=None, pass_id=None):
    """
    Get membership passes with professional filtering and booking conflict checking
    """
    try:
        if pass_id:
            # Get specific pass
            pass_obj = get_object_or_404(DurationPass, id=pass_id)
            return JsonResponse({
                'success': True,
                'pass': format_pass_data(pass_obj),
                'message': 'Pass retrieved successfully'
            })
        
        # Get passes for playground
        playground = get_object_or_404(Playground, id=playground_id) if playground_id else None
        
        # Build query
        passes_query = DurationPass.objects.filter(is_active=True)
        if playground:
            passes_query = passes_query.filter(playground=playground)
        
        # Apply filters
        sport_type = request.GET.get('sport_type')
        duration_type = request.GET.get('duration_type')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        if sport_type:
            passes_query = passes_query.filter(sport_types__contains=[sport_type])
        if duration_type:
            passes_query = passes_query.filter(duration_type=duration_type)
        if min_price:
            passes_query = passes_query.filter(price__gte=Decimal(min_price))
        if max_price:
            passes_query = passes_query.filter(price__lte=Decimal(max_price))
        
        # Get date parameter for booking conflict checking
        check_date = request.GET.get('date')
        
        # Get passes with statistics and booking status
        passes = []
        total_revenue = 0
        active_purchases = 0
        
        for pass_obj in passes_query.order_by('duration_days', 'price'):
            pass_data = format_pass_data(pass_obj)
            
            # Add purchase statistics
            purchases = PassPurchase.objects.filter(duration_pass=pass_obj)
            pass_data['statistics'] = {
                'total_purchases': purchases.count(),
                'active_purchases': purchases.filter(status='active').count(),
                'total_revenue': float(purchases.aggregate(
                    total=models.Sum('total_amount'))['total'] or 0),
                'popularity_score': min(100, purchases.count() * 10)
            }
            
            # Check if this pass is already booked for the selected date
            pass_data['is_booked'] = False
            pass_data['can_book'] = True
            
            if check_date and playground:
                from bookings.models import Booking
                from datetime import datetime
                
                try:
                    # Parse the date
                    date_obj = datetime.strptime(check_date, '%Y-%m-%d').date()
                    
                    # Check for existing bookings on this date for this membership pass
                    # We use the unique time slot pattern (22:XX) for membership passes
                    # Check for both pass_id formats (with and without spaces)
                    # Use dynamic hour configuration from playground custom_pricing or default
                    membership_hour = 22  # default
                    if playground.custom_pricing and isinstance(playground.custom_pricing, dict):
                        membership_hour = playground.custom_pricing.get('membership_pass_hour', 22)
                    existing_bookings = Booking.objects.filter(
                        playground=playground,
                        booking_date=date_obj,
                        start_time__hour=membership_hour  # Dynamic membership pass hour
                    ).filter(
                        Q(special_requests__icontains=f'"pass_id": "{pass_obj.id}"') |  # with space
                        Q(special_requests__icontains=f'"pass_id":"{pass_obj.id}"') |   # without space
                        Q(special_requests__icontains=f'"membership_pass_id": "{pass_obj.id}"') |  # alternative field with space
                        Q(special_requests__icontains=f'"membership_pass_id":"{pass_obj.id}"')     # alternative field without space
                    )
                    
                    if existing_bookings.exists():
                        pass_data['is_booked'] = True
                        pass_data['can_book'] = False
                
                except ValueError:
                    # Invalid date format, skip booking check
                    pass
            
            passes.append(pass_data)
            total_revenue += pass_data['statistics']['total_revenue']
            active_purchases += pass_data['statistics']['active_purchases']
        
        return JsonResponse({
            'success': True,
            'passes': passes,
            'summary': {
                'total_passes': len(passes),
                'total_revenue': total_revenue,
                'active_purchases': active_purchases,
                'average_price': sum(p['price'] for p in passes) / len(passes) if passes else 0
            },
            'message': f'Retrieved {len(passes)} membership passes'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error retrieving membership passes'
        }, status=500)


def create_temporary_membership_pass(request, data):
    """
    Create temporary membership pass during playground setup
    Stores pass data in session until playground is created
    """
    try:
        # Validate required fields for temporary pass
        required_fields = ['name', 'duration_type', 'duration_days', 'price', 'currency']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}',
                    'message': 'Please provide all required information'
                }, status=400)
        
        # Store temporary pass data in session
        if 'temporary_membership_passes' not in request.session:
            request.session['temporary_membership_passes'] = []
        
        # Generate temporary ID for frontend tracking
        temp_id = f"temp_{len(request.session['temporary_membership_passes']) + 1}"
        
        temp_pass_data = {
            'temp_id': temp_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'duration_type': data['duration_type'],
            'duration_days': int(data['duration_days']),
            'price': float(data['price']),
            'currency': data['currency'],
            
            # Professional features
            'unlimited_access': data.get('unlimited_access', False),
            'equipment_included': data.get('equipment_included', False),
            'priority_booking': data.get('priority_booking', False),
            'group_discount': data.get('group_discount', False),
            'flexible_cancellation': data.get('flexible_cancellation', False),
            'tournament_access': data.get('tournament_access', False),
            'training_sessions': data.get('training_sessions', False),
            'personal_trainer': data.get('personal_trainer', False),
            'nutrition_plan': data.get('nutrition_plan', False),
            'fitness_assessment': data.get('fitness_assessment', False),
            'locker_access': data.get('locker_access', False),
            'guest_privileges': data.get('guest_privileges', False),
            'online_booking': data.get('online_booking', False),
            'mobile_app_access': data.get('mobile_app_access', False),
            'created_at': timezone.now().isoformat()
        }
        
        request.session['temporary_membership_passes'].append(temp_pass_data)
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'pass': temp_pass_data,
            'message': 'Temporary membership pass created successfully',
            'is_temporary': True
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to create temporary membership pass'
        }, status=500)


@login_required
def create_membership_pass(request, playground_id=None):
    """
    Create professional membership pass with league features
    Supports temporary pass creation during playground setup
    """
    try:
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Handle FormData
            data = {}
            for key, value in request.POST.items():
                data[key] = value
        
        # Handle temporary pass creation (during playground setup)
        if not playground_id and data.get('is_temporary', False):
            return create_temporary_membership_pass(request, data)
        
        # If no playground_id in URL, check if it's in the FormData
        if not playground_id and 'playground_id' in data:
            playground_id = data['playground_id']
        
        # If still no playground_id, assume this is a temporary creation
        if not playground_id:
            if data.get('is_temporary', True):  # Default to temporary if no playground_id
                return create_temporary_membership_pass(request, data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing playground_id',
                    'message': 'Playground ID is required for permanent pass creation'
                }, status=400)
            
        playground = get_object_or_404(Playground, id=playground_id)
        
        # Verify ownership or admin access
        if playground.owner != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied',
                'message': 'You do not have permission to create passes for this playground'
            }, status=403)
        
        # Validate required fields
        required_fields = ['name', 'duration_type', 'duration_days', 'price', 'currency']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}',
                    'message': 'Please provide all required information'
                }, status=400)
        
        # Professional features and validation
        features = data.get('features', [])
        if data.get('league_friendly', False):
            features.extend([
                'Team booking discounts',
                'Coach privileges',
                'Tournament access',
                'Group management tools',
                'League scheduling priority'
            ])
        
        if data.get('professional_features', False):
            features.extend([
                'Priority booking',
                'Equipment included',
                'Guest privileges',
                'Flexible rescheduling',
                'Multi-location access'
            ])
        
        # Create the pass
        duration_pass = DurationPass.objects.create(
            playground=playground,
            name=data['name'],
            duration_type=data['duration_type'],
            duration_days=int(data['duration_days']),
            price=Decimal(str(data['price'])),
            currency=data['currency'],
            description=data.get('description', ''),
            features=list(set(features)),  # Remove duplicates
            sport_types=data.get('sport_types', []),
            access_pattern=data.get('access_pattern', 'unlimited'),
            peak_access=data.get('peak_access', False),
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'pass': format_pass_data(duration_pass),
            'message': f'Professional membership pass "{duration_pass.name}" created successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data',
            'message': 'Please provide valid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error creating membership pass'
        }, status=500)


@login_required
def update_membership_pass(request, pass_id):
    """
    Update existing membership pass
    """
    try:
        duration_pass = get_object_or_404(DurationPass, id=pass_id)
        
        # Verify ownership or admin access
        if duration_pass.playground.owner != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied',
                'message': 'You do not have permission to update this pass'
            }, status=403)
        
        data = json.loads(request.body)
        
        # Update fields
        updatable_fields = [
            'name', 'description', 'price', 'features', 'sport_types',
            'access_pattern', 'peak_access', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'price':
                    setattr(duration_pass, field, Decimal(str(data[field])))
                else:
                    setattr(duration_pass, field, data[field])
        
        duration_pass.save()
        
        return JsonResponse({
            'success': True,
            'pass': format_pass_data(duration_pass),
            'message': f'Membership pass "{duration_pass.name}" updated successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data',
            'message': 'Please provide valid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error updating membership pass'
        }, status=500)


@login_required
def delete_membership_pass(request, pass_id):
    """
    Delete membership pass (soft delete)
    """
    try:
        duration_pass = get_object_or_404(DurationPass, id=pass_id)
        
        # Verify ownership or admin access
        if duration_pass.playground.owner != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied',
                'message': 'You do not have permission to delete this pass'
            }, status=403)
        
        # Check for active purchases
        active_purchases = PassPurchase.objects.filter(
            duration_pass=duration_pass,
            status='active'
        ).count()
        
        if active_purchases > 0:
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete pass with active purchases',
                'message': f'This pass has {active_purchases} active purchases. Please wait for them to expire or cancel them first.'
            }, status=400)
        
        # Soft delete
        duration_pass.is_active = False
        duration_pass.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Membership pass "{duration_pass.name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error deleting membership pass'
        }, status=500)


def format_pass_data(duration_pass):
    """
    Format pass data for API response
    """
    return {
        'id': duration_pass.id,
        'name': duration_pass.name,
        'duration_type': duration_pass.duration_type,
        'duration_days': duration_pass.duration_days,
        'price': float(duration_pass.price),
        'currency': duration_pass.currency,
        'description': duration_pass.description,
        'features': duration_pass.features,
        'sport_types': duration_pass.sport_types,
        'access_pattern': duration_pass.access_pattern,
        'peak_access': duration_pass.peak_access,
        'is_active': duration_pass.is_active,
        'playground_id': duration_pass.playground.id,
        'playground_name': duration_pass.playground.name,
        'price_per_day': float(duration_pass.price_per_day),
        'discount_percentage': duration_pass.discount_percentage,
        'created_at': duration_pass.created_at.isoformat(),
        'updated_at': duration_pass.updated_at.isoformat(),
        'professional_features': {
            'league_friendly': 'Team booking discounts' in duration_pass.features,
            'equipment_included': 'Equipment included' in duration_pass.features,
            'priority_booking': 'Priority booking' in duration_pass.features,
            'guest_privileges': 'Guest privileges' in duration_pass.features,
            'coach_access': 'Coach privileges' in duration_pass.features
        }
    }


@csrf_exempt
@require_http_methods(["POST"])
def purchase_membership_pass(request, pass_id):
    """
    Purchase a membership pass
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'message': 'Please log in to purchase a membership pass'
            }, status=401)
        
        duration_pass = get_object_or_404(DurationPass, id=pass_id, is_active=True)
        data = json.loads(request.body) if request.body else {}
        
        # Calculate dates
        start_date = timezone.now().date()
        if 'start_date' in data:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(days=duration_pass.duration_days)
        
        # Create purchase
        purchase = PassPurchase.objects.create(
            duration_pass=duration_pass,
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            total_amount=duration_pass.price,
            currency=duration_pass.currency,
            status='active',  # Would be 'pending' until payment is confirmed
            payment_status='completed'  # Would be handled by payment gateway
        )
        
        return JsonResponse({
            'success': True,
            'purchase': {
                'id': purchase.id,
                'pass_name': duration_pass.name,
                'start_date': purchase.start_date.isoformat(),
                'end_date': purchase.end_date.isoformat(),
                'total_amount': float(purchase.total_amount),
                'currency': purchase.currency,
                'status': purchase.status
            },
            'message': f'Successfully purchased "{duration_pass.name}" membership pass!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data',
            'message': 'Please provide valid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error purchasing membership pass'
        }, status=500)


@csrf_exempt
def get_duration_types(request):
    """
    Get available duration types for membership passes
    """
    try:
        duration_types = [
            {
                'id': 'daily',
                'name': 'Daily Pass',
                'description': 'Valid for 1 day',
                'duration_days': 1
            },
            {
                'id': 'weekly',
                'name': 'Weekly Pass',
                'description': 'Valid for 7 days',
                'duration_days': 7
            },
            {
                'id': 'monthly',
                'name': 'Monthly Pass',
                'description': 'Valid for 30 days',
                'duration_days': 30
            },
            {
                'id': 'quarterly',
                'name': 'Quarterly Pass',
                'description': 'Valid for 90 days',
                'duration_days': 90
            },
            {
                'id': 'annual',
                'name': 'Annual Pass',
                'description': 'Valid for 365 days',
                'duration_days': 365
            }
        ]
        
        return JsonResponse({
            'success': True,
            'duration_types': duration_types
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def calculate_pass_pricing(request):
    """
    Calculate dynamic pricing for membership passes based on duration and features
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            duration_days = data.get('duration_days', 1)
            base_price = Decimal(str(data.get('base_price', 10)))
            features = data.get('features', [])
            sport_type = data.get('sport_type', 'general')
            
            # Base pricing calculation
            if duration_days == 1:
                multiplier = Decimal('1.0')
            elif duration_days == 7:
                multiplier = Decimal('6.5')  # 7.5% discount
            elif duration_days == 30:
                multiplier = Decimal('25.0')  # 16.7% discount
            elif duration_days == 90:
                multiplier = Decimal('70.0')  # 22.2% discount
            elif duration_days == 365:
                multiplier = Decimal('300.0')  # 17.8% discount
            else:
                multiplier = Decimal(str(duration_days)) * Decimal('0.95')  # 5% bulk discount
            
            calculated_price = base_price * multiplier
            
            # Features pricing
            feature_costs = {
                'equipment': Decimal('5.0'),
                'coaching': Decimal('15.0'),
                'refreshments': Decimal('3.0'),
                'video_analysis': Decimal('10.0'),
                'first_aid': Decimal('2.0'),
                'premium_location': Decimal('8.0')
            }
            
            total_feature_cost = sum(feature_costs.get(feature, Decimal('0')) for feature in features)
            total_feature_cost *= multiplier  # Apply duration multiplier to features
            
            final_price = calculated_price + total_feature_cost
            
            return JsonResponse({
                'success': True,
                'pricing': {
                    'base_price': float(base_price),
                    'duration_days': duration_days,
                    'duration_multiplier': float(multiplier),
                    'base_total': float(calculated_price),
                    'feature_cost': float(total_feature_cost),
                    'final_price': float(final_price),
                    'savings': float((base_price * duration_days) - final_price) if duration_days > 1 else 0,
                    'features': features
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)
            
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
