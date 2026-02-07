"""
Temporary Data Handler for Professional Playground Booking System
Handles saving temporary membership passes and custom slots to database when playground is created
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
import json

from playgrounds.models import Playground, DurationPass, PlaygroundSlot


@login_required
def save_temporary_data_to_playground(request, playground_id):
    """
    Save all temporary membership passes and custom slots to the newly created playground
    """
    try:
        playground = Playground.objects.get(id=playground_id)
        
        # Verify ownership
        if playground.owner != request.user and not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        saved_passes = []
        saved_slots = []
        
        # Save temporary membership passes
        if 'temporary_membership_passes' in request.session:
            for temp_pass in request.session['temporary_membership_passes']:
                try:
                    # Create real membership pass
                    duration_pass = DurationPass.objects.create(
                        playground=playground,
                        name=temp_pass['name'],
                        duration_type=temp_pass['duration_type'],
                        duration_days=int(temp_pass['duration_days']),
                        price=Decimal(str(temp_pass['price'])),
                        currency=temp_pass['currency'],
                        description=temp_pass.get('description', ''),
                        is_active=True,
                        
                        # Professional features
                        unlimited_access=temp_pass.get('unlimited_access', False),
                        equipment_included=temp_pass.get('equipment_included', False),
                        priority_booking=temp_pass.get('priority_booking', False),
                        group_discount=temp_pass.get('group_discount', False),
                        flexible_cancellation=temp_pass.get('flexible_cancellation', False),
                        tournament_access=temp_pass.get('tournament_access', False),
                        training_sessions=temp_pass.get('training_sessions', False),
                        personal_trainer=temp_pass.get('personal_trainer', False),
                        nutrition_plan=temp_pass.get('nutrition_plan', False),
                        fitness_assessment=temp_pass.get('fitness_assessment', False),
                        locker_access=temp_pass.get('locker_access', False),
                        guest_privileges=temp_pass.get('guest_privileges', False),
                        online_booking=temp_pass.get('online_booking', False),
                        mobile_app_access=temp_pass.get('mobile_app_access', False)
                    )
                    
                    saved_passes.append({
                        'temp_id': temp_pass['temp_id'],
                        'real_id': duration_pass.id,
                        'name': duration_pass.name
                    })
                    
                except Exception as e:
                    print(f"Error saving membership pass: {e}")
                    continue
            
            # Clear temporary passes from session
            del request.session['temporary_membership_passes']
        
        # Save temporary custom slots
        if 'temporary_custom_slots' in request.session:
            for temp_slot in request.session['temporary_custom_slots']:
                try:
                    # Create real custom slot
                    playground_slot = PlaygroundSlot.objects.create(
                        playground=playground,
                        slot_type=temp_slot['slot_type'],
                        start_time=temp_slot['start_time'],
                        end_time=temp_slot['end_time'],
                        price=Decimal(str(temp_slot['price'])),
                        currency=temp_slot.get('currency', 'BDT'),
                        day_of_week=temp_slot['day_of_week'],
                        is_active=temp_slot.get('is_active', True),
                        max_capacity=temp_slot.get('max_capacity', 10),
                        description=temp_slot.get('description', ''),
                        features=temp_slot.get('features', [])
                    )
                    
                    saved_slots.append({
                        'temp_id': temp_slot['temp_id'],
                        'real_id': playground_slot.id,
                        'name': f"{temp_slot['slot_type']} slot {temp_slot['start_time']}-{temp_slot['end_time']}"
                    })
                    
                except Exception as e:
                    print(f"Error saving custom slot: {e}")
                    continue
            
            # Clear temporary slots from session
            del request.session['temporary_custom_slots']
        
        # Save session changes
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Temporary data saved successfully',
            'saved_passes': saved_passes,
            'saved_slots': saved_slots,
            'total_saved': len(saved_passes) + len(saved_slots)
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Playground not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error saving temporary data'
        }, status=500)


@login_required
def get_temporary_data_summary(request):
    """
    Get summary of temporary data in session
    """
    try:
        temp_passes = request.session.get('temporary_membership_passes', [])
        temp_slots = request.session.get('temporary_custom_slots', [])
        
        return JsonResponse({
            'success': True,
            'temporary_passes': len(temp_passes),
            'temporary_slots': len(temp_slots),
            'total_temporary_items': len(temp_passes) + len(temp_slots),
            'passes': temp_passes,
            'slots': temp_slots
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required  
def clear_temporary_data(request):
    """
    Clear all temporary data from session
    """
    try:
        cleared_passes = len(request.session.get('temporary_membership_passes', []))
        cleared_slots = len(request.session.get('temporary_custom_slots', []))
        
        if 'temporary_membership_passes' in request.session:
            del request.session['temporary_membership_passes']
        if 'temporary_custom_slots' in request.session:
            del request.session['temporary_custom_slots']
            
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Temporary data cleared',
            'cleared_passes': cleared_passes,
            'cleared_slots': cleared_slots
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
