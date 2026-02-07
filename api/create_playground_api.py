from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from playgrounds.models import Playground, City, SportType
from accounts.models import User

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CreatePlaygroundView(View):
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['name', 'location', 'price']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'error': f'{field.title()} is required'
                    }, status=400)
            
            # Check if user is a playground owner
            if not hasattr(request.user, 'user_type') or request.user.user_type != 'owner':
                return JsonResponse({
                    'success': False,
                    'error': 'Only playground owners can create playgrounds'
                }, status=403)
            
            # Get or create default city (we'll improve this later)
            city, created = City.objects.get_or_create(
                name='Default City',
                defaults={
                    'state_id': 1,  # Assuming we have at least one state
                    'latitude': 0.0,
                    'longitude': 0.0
                }
            )
            
            # Create playground with pending status
            playground = Playground.objects.create(
                owner=request.user,
                name=data['name'],
                description=data.get('description', ''),
                city=city,
                address=data['location'],
                price_per_hour=float(data['price']),
                capacity=10,  # Default capacity
                status='pending',  # Set to pending for admin approval
            )
            
            # Add default sport type if none exists
            default_sport, created = SportType.objects.get_or_create(
                name='General',
                defaults={'description': 'General playground activities'}
            )
            playground.sport_types.add(default_sport)
            
            return JsonResponse({
                'success': True,
                'message': 'Playground created successfully and sent for admin approval',
                'playground': {
                    'id': playground.id,
                    'name': playground.name,
                    'description': playground.description,
                    'location': playground.address,
                    'price': str(playground.price_per_hour),
                    'status': playground.status,
                    'created_at': playground.created_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)

# Function-based view for simpler usage
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_playground_api(request):
    view = CreatePlaygroundView()
    return view.post(request)
