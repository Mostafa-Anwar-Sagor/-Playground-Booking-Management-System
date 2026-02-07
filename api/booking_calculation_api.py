from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from decimal import Decimal
from playgrounds.models import Playground, Amenity

@method_decorator(csrf_exempt, name='dispatch')
class BookingCalculationAPI(View):
    """
    Dynamic booking calculation API
    Calculates subtotal, amenity fees, and total based on real-time selections
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Extract parameters
            playground_id = data.get('playground_id')
            slot_type = data.get('slot_type', 'regular')
            selected_slots = data.get('selected_slots', [])
            selected_amenities = data.get('selected_amenities', [])
            custom_slot = data.get('custom_slot')
            membership_pass = data.get('membership_pass')
            
            # Get playground
            try:
                playground = Playground.objects.get(id=playground_id)
            except Playground.DoesNotExist:
                return JsonResponse({'error': 'Playground not found'}, status=404)
            
            # Initialize calculations
            subtotal = Decimal('0.00')
            amenity_fees = Decimal('0.00')
            breakdown = {}
            
            # Calculate subtotal based on slot type
            if slot_type == 'regular':
                # Regular slots calculation
                slot_count = len(selected_slots)
                slot_price = Decimal(str(playground.price_per_hour))
                subtotal = slot_price * slot_count
                
                breakdown['slot_type'] = 'Regular'
                breakdown['slot_count'] = slot_count
                breakdown['price_per_hour'] = float(slot_price)
                breakdown['slots_total'] = float(subtotal)
                
            elif slot_type == 'custom':
                # Custom slot calculation
                if custom_slot:
                    duration = Decimal(str(custom_slot.get('duration', 2)))
                    slot_price = Decimal(str(playground.price_per_hour))
                    subtotal = slot_price * duration
                    
                    breakdown['slot_type'] = 'Custom'
                    breakdown['duration'] = float(duration)
                    breakdown['price_per_hour'] = float(slot_price)
                    breakdown['slots_total'] = float(subtotal)
                
            elif slot_type == 'membership':
                # Membership pass calculation
                if membership_pass:
                    subtotal = Decimal(str(membership_pass.get('price', 0)))
                    
                    breakdown['slot_type'] = 'Membership'
                    breakdown['membership_name'] = membership_pass.get('name', '')
                    breakdown['membership_price'] = float(subtotal)
            
            # Calculate amenity fees
            if selected_amenities:
                amenity_ids = [amenity.get('id') for amenity in selected_amenities if amenity.get('id')]
                amenity_breakdown = []
                
                for amenity_data in selected_amenities:
                    amenity_id = amenity_data.get('id')
                    if amenity_id:
                        try:
                            amenity = Amenity.objects.get(id=amenity_id)
                            amenity_price = Decimal(str(amenity.price))
                            amenity_fees += amenity_price
                            
                            amenity_breakdown.append({
                                'id': amenity.id,
                                'name': amenity.name,
                                'price': float(amenity_price)
                            })
                        except Amenity.DoesNotExist:
                            continue
                
                breakdown['amenities'] = amenity_breakdown
                breakdown['amenity_fees'] = float(amenity_fees)
            
            # Calculate total
            total = subtotal + amenity_fees
            
            # Prepare response
            response_data = {
                'success': True,
                'playground': {
                    'id': playground.id,
                    'name': playground.name,
                    'currency': playground.currency,
                    'price_per_hour': float(playground.price_per_hour)
                },
                'calculation': {
                    'subtotal': float(subtotal),
                    'amenity_fees': float(amenity_fees),
                    'total': float(total),
                    'currency': playground.currency
                },
                'breakdown': breakdown
            }
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
