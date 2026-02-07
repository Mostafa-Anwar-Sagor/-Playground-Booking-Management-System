from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from accounts.models import PartnerApplication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access these views"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'admin'

@method_decorator(csrf_exempt, name='dispatch')
class PartnerApplicationAPIView(AdminRequiredMixin, View):
    """API view for partner applications management"""
    
    def get(self, request, *args, **kwargs):
        """Get all partner applications with media"""
        try:
            applications = PartnerApplication.objects.select_related('user').prefetch_related('images', 'videos').all().order_by('-created_at')
            
            applications_data = []
            for app in applications:
                app_data = {
                    'id': app.id,
                    'full_name': app.user.get_full_name() or app.user.email,
                    'email': app.business_email or app.user.email,
                    'phone_number': app.business_phone,
                    'address': app.business_address,
                    'playground_name': app.business_name,
                    'playground_address': app.business_address,
                    'playground_type': 'Mixed Sports',  # Default since not in model
                    'playground_size': f"{app.experience_years} years experience",  # Using experience as size proxy
                    'playground_description': app.description or 'No description provided',
                    'business_description': app.description or 'No description provided',
                    'status': app.status,
                    'created_at': app.created_at.isoformat(),
                    'admin_comments': app.admin_comments or '',
                    'images': [{'id': img.id, 'url': img.image.url} for img in app.images.all()],
                    'videos': [{'id': vid.id, 'url': vid.video.url} for vid in app.videos.all()],
                }
                applications_data.append(app_data)
            
            # Get approved owners
            approved_owners = [app for app in applications_data if app['status'] in ['active', 'approved']]
            
            return JsonResponse({
                'success': True,
                'applications': applications_data,
                'approved_owners': approved_owners,
                'stats': {
                    'total': len(applications_data),
                    'pending': len([app for app in applications_data if app['status'] == 'pending']),
                    'approved': len([app for app in applications_data if app['status'] in ['active', 'approved']]),
                    'rejected': len([app for app in applications_data if app['status'] == 'rejected']),
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request, *args, **kwargs):
        """Handle application actions (approve/reject/delete)"""
        try:
            data = json.loads(request.body) if request.body else {}
            app_id = data.get('application_id') or request.POST.get('application_id')
            action = data.get('action') or request.POST.get('action')
            
            if not app_id:
                return JsonResponse({'success': False, 'message': 'Application ID is required'}, status=400)
            
            try:
                app = PartnerApplication.objects.select_related('user').get(id=app_id)
            except PartnerApplication.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Application not found'}, status=404)
            
            if action == 'approve':
                if app.status != 'pending':
                    return JsonResponse({'success': False, 'message': 'Only pending applications can be approved'}, status=400)
                
                app.status = 'active'
                app.approved_by = request.user
                app.save(update_fields=['status', 'approved_by'])
                
                # Promote user to owner
                app.user.user_type = 'owner'
                app.user.is_approved = True
                app.user.save(update_fields=['user_type', 'is_approved'])
                
                # Find and activate any pending playgrounds for this user
                playground_id = None
                try:
                    from accounts.models import PlaygroundApplication
                    from playgrounds.models import Playground
                    
                    # Get all playground applications for this user
                    playground_apps = PlaygroundApplication.objects.filter(user=app.user, status='pending')
                    activated_playgrounds = []
                    
                    for pg_app in playground_apps:
                        if pg_app.created_playground and pg_app.created_playground.status == 'pending':
                            # Activate the playground
                            playground = pg_app.created_playground
                            playground.status = 'active'
                            playground.is_verified = True
                            playground.save(update_fields=['status', 'is_verified'])
                            activated_playgrounds.append(playground.id)
                            playground_id = playground.id  # Return the first one
                            
                            # Send playground approval notification
                            try:
                                from notifications.models import Notification
                                Notification.objects.create(
                                    recipient=app.user,
                                    title='🏟️ Playground Activated!',
                                    message=f'Your playground "{playground.name}" has been activated and is now available for bookings!',
                                    notification_type='playground_approved'
                                )
                            except ImportError:
                                pass
                    
                    if activated_playgrounds:
                        print(f"Activated {len(activated_playgrounds)} playgrounds: {activated_playgrounds}")
                    
                except ImportError:
                    pass  # PlaygroundApplication might not be available
                
                # Create partner approval notification
                try:
                    from notifications.models import Notification
                    Notification.objects.create(
                        recipient=app.user,
                        title='🎉 Partner Application Approved!',
                        message=f'Congratulations! Your partner application for "{app.business_name}" has been approved.',
                        notification_type='partner_approved'
                    )
                except ImportError:
                    pass
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Application approved successfully!',
                    'new_status': 'active',
                    'playground_id': playground_id  # Include playground ID for frontend
                })
            
            elif action == 'reject':
                if app.status != 'pending':
                    return JsonResponse({'success': False, 'message': 'Only pending applications can be rejected'}, status=400)
                
                app.status = 'rejected'
                app.save(update_fields=['status'])
                
                # Create notification
                try:
                    from notifications.models import Notification
                    Notification.objects.create(
                        recipient=app.user,
                        title='❌ Partner Application Rejected',
                        message=f'Your partner application for "{app.business_name}" has been rejected.',
                        notification_type='partner_rejected'
                    )
                except ImportError:
                    pass
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Application rejected successfully!',
                    'new_status': 'rejected'
                })
            
            elif action == 'delete':
                app.delete()
                return JsonResponse({
                    'success': True, 
                    'message': 'Application deleted successfully!'
                })
            
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PartnerApplicationDetailAPIView(AdminRequiredMixin, View):
    """API view for individual partner application operations"""
    
    def post(self, request, app_id, action):
        """Handle specific application actions"""
        try:
            app = PartnerApplication.objects.select_related('user').get(id=app_id)
        except PartnerApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found'}, status=404)
        
        if action == 'approve':
            if app.status != 'pending':
                return JsonResponse({'success': False, 'message': 'Only pending applications can be approved'}, status=400)
            
            app.status = 'approved'
            app.approved_by = request.user
            app.save(update_fields=['status', 'approved_by'])
            
            # Promote user to owner
            app.user.user_type = 'owner'
            app.user.is_approved = True
            app.user.save(update_fields=['user_type', 'is_approved'])
            
            # Find and activate any pending playgrounds for this user
            playground_id = None
            try:
                from accounts.models import PlaygroundApplication
                from playgrounds.models import Playground
                
                # Get all playground applications for this user
                playground_apps = PlaygroundApplication.objects.filter(user=app.user, status='pending')
                activated_playgrounds = []
                
                for pg_app in playground_apps:
                    if pg_app.created_playground and pg_app.created_playground.status == 'pending':
                        # Activate the playground
                        playground = pg_app.created_playground
                        playground.status = 'active'
                        playground.is_verified = True
                        playground.save(update_fields=['status', 'is_verified'])
                        activated_playgrounds.append(playground.id)
                        playground_id = playground.id  # Return the first one
                        
                        # Send playground approval notification
                        try:
                            from notifications.models import Notification
                            Notification.objects.create(
                                recipient=app.user,
                                title='🏟️ Playground Activated!',
                                message=f'Your playground "{playground.name}" has been activated and is now available for bookings!',
                                notification_type='playground_approved'
                            )
                        except ImportError:
                            pass
                
                if activated_playgrounds:
                    print(f"Activated {len(activated_playgrounds)} playgrounds: {activated_playgrounds}")
                
            except ImportError:
                pass  # PlaygroundApplication might not be available
            
            # Create partner approval notification
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=app.user,
                    title='🎉 Partner Application Approved!',
                    message=f'Congratulations! Your partner application for "{app.business_name}" has been approved.',
                    notification_type='partner_approved'
                )
            except ImportError:
                pass
            
            return JsonResponse({
                'success': True, 
                'message': 'Application approved successfully!',
                'new_status': 'approved',
                'playground_id': playground_id  # Include playground ID for frontend
            })
        
        elif action == 'reject':
            if app.status != 'pending':
                return JsonResponse({'success': False, 'message': 'Only pending applications can be rejected'}, status=400)
            
            app.status = 'rejected'
            app.save(update_fields=['status'])
            
            return JsonResponse({
                'success': True, 
                'message': 'Application rejected successfully!',
                'new_status': 'rejected'
            })
        
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)
    
    def delete(self, request, app_id):
        """Delete an application"""
        try:
            app = PartnerApplication.objects.get(id=app_id)
            app.delete()
            return JsonResponse({
                'success': True, 
                'message': 'Application deleted successfully!'
            })
        except PartnerApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found'}, status=404)
