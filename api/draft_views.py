from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from playgrounds.models import Playground
import json


@require_http_methods(["POST"])
@login_required
def save_draft_playground(request):
    """Save playground form as draft"""
    try:
        # Get form data
        data = {}
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                data[key] = value
        
        # Handle file uploads
        files = {}
        for key, file in request.FILES.items():
            files[key] = file
        
        # Create or update draft
        draft_id = request.POST.get('draft_id')
        
        if draft_id:
            # Update existing draft
            try:
                playground = Playground.objects.get(id=draft_id, owner=request.user)
                # Update fields
                for key, value in data.items():
                    if hasattr(playground, key):
                        setattr(playground, key, value)
                playground.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Draft updated successfully',
                    'draft_id': playground.id
                })
            except Playground.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Draft not found'
                })
        else:
            # Create new draft
            playground_data = {
                'owner': request.user,
                'name': data.get('name', 'Untitled Playground'),
                'description': data.get('description', ''),
                'status': 'draft'
            }
            
            # Add other fields if they exist
            if data.get('address'):
                playground_data['address'] = data['address']
            if data.get('price_per_slot'):
                try:
                    playground_data['price_per_hour'] = float(data['price_per_slot'])
                except (ValueError, TypeError):
                    pass
            
            # Set city if selected
            if data.get('city'):
                try:
                    from playgrounds.models import City
                    city = City.objects.get(id=data['city'])
                    playground_data['city'] = city
                except City.DoesNotExist:
                    pass
            
            playground = Playground.objects.create(**playground_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Draft saved successfully',
                'draft_id': playground.id
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
@login_required
def load_draft_playground(request, draft_id=None):
    """Load playground draft"""
    try:
        # If no draft_id provided, return empty response (no drafts available)
        if not draft_id:
            return JsonResponse({
                'success': True,
                'data': None,
                'message': 'No draft ID provided'
            })
            
        playground = Playground.objects.get(id=draft_id, owner=request.user, status='draft')
        
        data = {
            'name': playground.name,
            'description': playground.description,
            'address': playground.address,
            'price_per_slot': float(playground.price_per_hour) if playground.price_per_hour else None,
            'capacity': playground.capacity,
            'playground_type': playground.playground_type,
        }
        
        # Add city, state, country info
        if playground.city:
            data['city'] = playground.city.id
            data['city_name'] = playground.city.name
            if playground.city.state:
                data['state'] = playground.city.state.id
                data['state_name'] = playground.city.state.name
                if playground.city.state.country:
                    data['country'] = playground.city.state.country.id
                    data['country_name'] = playground.city.state.country.name
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Draft not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["DELETE"])
@login_required
def delete_draft_playground(request, draft_id):
    """Delete playground draft"""
    try:
        playground = Playground.objects.get(id=draft_id, owner=request.user, status='draft')
        playground.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Draft deleted successfully'
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Draft not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
