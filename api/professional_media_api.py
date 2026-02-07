"""
Professional Media Gallery API for Playground Management
Handles cover images, gallery images, videos, and virtual tours with real-time backend integration
"""

import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from playgrounds.models import Playground, PlaygroundImage, PlaygroundVideo
import uuid
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def add_cors_headers(response):
    """Add CORS headers to response"""
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Authorization'
    return response

@csrf_exempt
def sync_status(request):
    """Get sync status and media data for real-time backend connectivity"""
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        return add_cors_headers(response)
    
    if request.method == 'GET':
        try:
            playground_id = request.GET.get('playground_id')
            
            response_data = {
                'success': True,
                'server_time': timezone.now().isoformat(),
                'sync_status': 'connected',
                'playground_id': playground_id
            }
            
            if playground_id and playground_id != 'new':
                # Get existing playground media
                try:
                    playground = Playground.objects.get(id=playground_id)
                    
                    # Get cover images
                    cover_images = PlaygroundImage.objects.filter(
                        playground=playground, 
                        is_primary=True
                    ).values('id', 'image', 'created_at')
                    
                    # Get gallery images
                    gallery_images = PlaygroundImage.objects.filter(
                        playground=playground, 
                        is_primary=False
                    ).values('id', 'image', 'caption', 'created_at')
                    
                    # Get videos
                    gallery_videos = PlaygroundVideo.objects.filter(
                        playground=playground
                    ).values('id', 'video', 'title', 'description', 'created_at')
                    
                    response_data.update({
                        'coverImages': list(cover_images),
                        'galleryImages': list(gallery_images),
                        'galleryVideos': list(gallery_videos),
                        'media_count': {
                            'cover_images': len(cover_images),
                            'gallery_images': len(gallery_images),
                            'videos': len(gallery_videos)
                        }
                    })
                    
                except Playground.DoesNotExist:
                    response_data.update({
                        'coverImages': [],
                        'galleryImages': [],
                        'galleryVideos': [],
                        'media_count': {
                            'cover_images': 0,
                            'gallery_images': 0,
                            'videos': 0
                        }
                    })
            else:
                # New playground - no existing media
                response_data.update({
                    'coverImages': [],
                    'galleryImages': [],
                    'galleryVideos': [],
                    'media_count': {
                        'cover_images': 0,
                        'gallery_images': 0,
                        'videos': 0
                    }
                })
            
            logger.info(f"Sync status requested for playground: {playground_id}")
            response = JsonResponse(response_data)
            return add_cors_headers(response)
            
        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            response = JsonResponse({
                'success': False,
                'error': str(e),
                'sync_status': 'error',
                'message': 'Failed to get sync status'
            }, status=500)
            return add_cors_headers(response)
    
    response = JsonResponse({'error': 'Only GET method allowed'}, status=405)
    return add_cors_headers(response)

@csrf_exempt
def upload_cover_images(request):
    """Upload and process cover images for slider with CORS support"""
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        return add_cors_headers(response)
    
    if request.method == 'GET':
        # Handle GET requests for endpoint testing
        response = JsonResponse({
            'endpoint': 'upload_cover_images',
            'methods': ['POST'],
            'description': 'Upload cover images for playground slider',
            'status': 'available'
        })
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'error': 'Only POST method allowed', 'allowed_methods': ['POST', 'GET', 'OPTIONS']}, status=405)
        return add_cors_headers(response)
    
    try:
        # Get playground ID (can be null for new playgrounds)
        playground_id = request.POST.get('playground_id')
        slider_config = json.loads(request.POST.get('slider_config', '{}'))
        
        uploaded_images = []
        
        # Handle multiple field name patterns for compatibility
        for key in request.FILES:
            if key.startswith('cover_image') or key == 'cover_images':
                image_file = request.FILES[key]
                
                # Validate image
                if not validate_image_file(image_file):
                    logger.warning(f"Invalid image file skipped: {image_file.name}")
                    continue
                
                try:
                    # Process and save image
                    processed_image = process_cover_image(image_file)
                    
                    if playground_id:
                        # Save to existing playground
                        playground = get_object_or_404(Playground, id=playground_id)
                        playground_image = PlaygroundImage.objects.create(
                            playground=playground,
                            image=processed_image,
                            is_primary=(len(uploaded_images) == 0),  # First image is primary
                        )
                        
                        uploaded_images.append({
                            'id': playground_image.id,
                            'url': playground_image.image.url,
                            'name': image_file.name,
                            'size': image_file.size,
                            'type': image_file.content_type,
                            'is_primary': playground_image.is_primary,
                            'order_index': getattr(playground_image, 'order_index', len(uploaded_images)),
                            'uploaded_at': playground_image.created_at.isoformat()
                        })
                        logger.info(f"Cover image saved to database: {image_file.name}")
                    else:
                        # Save to temporary storage for new playgrounds
                        temp_path = save_temp_image(processed_image, 'cover', image_file.name)
                        uploaded_images.append({
                            'id': f"temp_{uuid.uuid4()}",
                            'url': temp_path,
                            'name': image_file.name,
                            'size': image_file.size,
                            'type': image_file.content_type,
                            'is_primary': (len(uploaded_images) == 0),
                            'order_index': len(uploaded_images),
                            'is_temporary': True,
                            'uploaded_at': timezone.now().isoformat()
                        })
                        logger.info(f"Cover image saved temporarily: {image_file.name}")
                        
                except Exception as img_error:
                    logger.error(f"Error processing cover image {image_file.name}: {str(img_error)}")
                    continue
        
        response_data = {
            'success': True,
            'images': uploaded_images,
            'total_count': len(uploaded_images),
            'slider_config': slider_config,
            'message': f'{len(uploaded_images)} cover images uploaded successfully',
            'playground_id': playground_id
        }
        
        logger.info(f"Cover images upload completed: {len(uploaded_images)} images processed")
        response = JsonResponse(response_data)
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error uploading cover images: {str(e)}")
        response = JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to upload cover images'
        }, status=500)
        return add_cors_headers(response)

@csrf_exempt
@csrf_exempt
def upload_gallery_images(request):
    """Upload and process gallery images with CORS support"""
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        return add_cors_headers(response)
    
    if request.method == 'GET':
        # Handle GET requests for endpoint testing
        response = JsonResponse({
            'endpoint': 'upload_gallery_images',
            'methods': ['POST'],
            'description': 'Upload gallery images for playground',
            'status': 'available'
        })
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'error': 'Only POST method allowed', 'allowed_methods': ['POST', 'GET', 'OPTIONS']}, status=405)
        return add_cors_headers(response)
    
    try:
        playground_id = request.POST.get('playground_id')
        
        uploaded_images = []
        
        # Handle multiple field name patterns for compatibility
        for key in request.FILES:
            if key.startswith('gallery_image') or key == 'gallery_images':
                image_file = request.FILES[key]
                
                # Validate image
                if not validate_image_file(image_file):
                    logger.warning(f"Invalid gallery image file skipped: {image_file.name}")
                    continue
                
                try:
                    # Process and save image
                    processed_image = process_gallery_image(image_file)
                    caption = request.POST.get('caption', '')
                    
                    if playground_id:
                        # Save to existing playground
                        playground = get_object_or_404(Playground, id=playground_id)
                        playground_image = PlaygroundImage.objects.create(
                            playground=playground,
                            image=processed_image,
                            caption=caption,
                            is_primary=False,
                        )
                        
                        uploaded_images.append({
                            'id': playground_image.id,
                            'url': playground_image.image.url,
                            'name': image_file.name,
                            'size': image_file.size,
                            'type': image_file.content_type,
                            'caption': caption,
                            'uploaded_at': playground_image.created_at.isoformat()
                        })
                        logger.info(f"Gallery image saved to database: {image_file.name}")
                    else:
                        # Save to temporary storage
                        temp_path = save_temp_image(processed_image, 'gallery', image_file.name)
                        uploaded_images.append({
                            'id': f"temp_{uuid.uuid4()}",
                            'url': temp_path,
                            'name': image_file.name,
                            'size': image_file.size,
                            'type': image_file.content_type,
                            'order_index': len(uploaded_images),
                            'is_temporary': True,
                            'caption': caption,
                            'uploaded_at': timezone.now().isoformat()
                        })
                        logger.info(f"Gallery image saved temporarily: {image_file.name}")
                        
                except Exception as img_error:
                    logger.error(f"Error processing gallery image {image_file.name}: {str(img_error)}")
                    continue
        
        response_data = {
            'success': True,
            'images': uploaded_images,
            'total_count': len(uploaded_images),
            'message': f'{len(uploaded_images)} gallery images uploaded successfully',
            'playground_id': playground_id
        }
        
        logger.info(f"Gallery images upload completed: {len(uploaded_images)} images processed")
        response = JsonResponse(response_data)
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error uploading gallery images: {str(e)}")
        response = JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to upload gallery images'
        }, status=500)
        return add_cors_headers(response)

@csrf_exempt
def save_video_data(request):
    """Save video URL and metadata with CORS support"""
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        return add_cors_headers(response)
    
    if request.method == 'GET':
        # Handle GET requests for endpoint testing
        response = JsonResponse({
            'endpoint': 'save_video_data',
            'methods': ['POST'],
            'description': 'Save video URL and metadata',
            'status': 'available'
        })
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'error': 'Only POST method allowed', 'allowed_methods': ['POST', 'GET', 'OPTIONS']}, status=405)
        return add_cors_headers(response)
    
    try:
        playground_id = request.POST.get('playground_id')
        video_url = request.POST.get('video_url')
        video_type = request.POST.get('video_type', 'youtube')
        video_id = request.POST.get('video_id')
        
        video_data = {
            'url': video_url,
            'type': video_type,
            'video_id': video_id,
            'upload_timestamp': timezone.now().isoformat()
        }
        
        if playground_id:
            # Save to existing playground
            playground = get_object_or_404(Playground, id=playground_id)
            
            # Update or create video record
            playground_video, created = PlaygroundVideo.objects.update_or_create(
                playground=playground,
                video_type='drone',
                defaults={
                    'video_url': video_url,
                    'title': 'Drone/Aerial View',
                    'description': 'Aerial view of the playground',
                    'metadata': json.dumps(video_data)
                }
            )
            
            response = JsonResponse({
                'success': True,
                'video': {
                    'id': playground_video.id,
                    'url': playground_video.video_url,
                    'type': video_type,
                    'video_id': video_id
                },
                'message': 'Video saved successfully'
            })
            return add_cors_headers(response)
        else:
            # Save to session for new playgrounds
            if 'temp_video_data' not in request.session:
                request.session['temp_video_data'] = {}
            
            request.session['temp_video_data']['drone_video'] = video_data
            request.session.modified = True
            
            response = JsonResponse({
                'success': True,
                'video': video_data,
                'is_temporary': True,
                'message': 'Video data saved temporarily'
            })
            return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error saving video data: {str(e)}")
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)

@csrf_exempt
def save_virtual_tour_data(request):
    """Save virtual tour URL and metadata with CORS support"""
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        return add_cors_headers(response)
    
    if request.method == 'GET':
        # Handle GET requests for endpoint testing
        response = JsonResponse({
            'endpoint': 'save_virtual_tour_data',
            'methods': ['POST'],
            'description': 'Save virtual tour URL and metadata',
            'status': 'available'
        })
        return add_cors_headers(response)
    
    if request.method != 'POST':
        response = JsonResponse({'error': 'Only POST method allowed', 'allowed_methods': ['POST', 'GET', 'OPTIONS']}, status=405)
        return add_cors_headers(response)
    
    try:
        playground_id = request.POST.get('playground_id')
        tour_url = request.POST.get('tour_url')
        tour_provider = request.POST.get('tour_provider')
        
        tour_data = {
            'url': tour_url,
            'provider': tour_provider,
            'upload_timestamp': timezone.now().isoformat()
        }
        
        if playground_id:
            # Save to existing playground
            playground = get_object_or_404(Playground, id=playground_id)
            
            # Update playground model with virtual tour data
            playground.virtual_tour_url = tour_url
            playground.virtual_tour_provider = tour_provider
            playground.save()
            
            response = JsonResponse({
                'success': True,
                'tour': tour_data,
                'message': 'Virtual tour saved successfully'
            })
            return add_cors_headers(response)
        else:
            # Save to session for new playgrounds
            if 'temp_virtual_tour' not in request.session:
                request.session['temp_virtual_tour'] = {}
            
            request.session['temp_virtual_tour'] = tour_data
            request.session.modified = True
            
            response = JsonResponse({
                'success': True,
                'tour': tour_data,
                'is_temporary': True,
                'message': 'Virtual tour data saved temporarily'
            })
            return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error saving virtual tour data: {str(e)}")
        response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        return add_cors_headers(response)

@require_http_methods(["GET"])
def get_media_data(request, playground_id=None):
    """Get all media data for a playground"""
    try:
        if playground_id:
            playground = get_object_or_404(Playground, id=playground_id)
            
            # Get cover images (primary images)
            cover_images = PlaygroundImage.objects.filter(
                playground=playground,
                is_primary=True
            )
            
            # Get gallery images
            gallery_images = PlaygroundImage.objects.filter(
                playground=playground,
                is_primary=False
            )
            
            # Get video data
            videos = PlaygroundVideo.objects.filter(playground=playground)
            
            return JsonResponse({
                'success': True,
                'cover_images': [
                    {
                        'id': img.id,
                        'url': img.image.url,
                        'is_primary': img.is_primary,
                        'caption': img.caption,
                    } for img in cover_images
                ],
                'gallery_images': [
                    {
                        'id': img.id,
                        'url': img.image.url,
                        'caption': img.caption,
                    } for img in gallery_images
                ],
                'videos': [
                    {
                        'id': video.id,
                        'url': video.video_url,
                        'type': video.video_type,
                        'title': video.title,
                        'metadata': json.loads(video.metadata or '{}')
                    } for video in videos
                ],
                'virtual_tour': {
                    'url': getattr(playground, 'virtual_tour_url', ''),
                    'provider': getattr(playground, 'virtual_tour_provider', '')
                }
            })
        else:
            # Get temporary data from session
            temp_video = request.session.get('temp_video_data', {})
            temp_tour = request.session.get('temp_virtual_tour', {})
            
            return JsonResponse({
                'success': True,
                'cover_images': [],
                'gallery_images': [],
                'videos': [temp_video.get('drone_video', {})] if temp_video else [],
                'virtual_tour': temp_tour,
                'is_temporary': True
            })
            
    except Exception as e:
        logger.error(f"Error getting media data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_media_item(request, item_type, item_id):
    """Delete a specific media item"""
    try:
        if item_type == 'cover' or item_type == 'gallery':
            image = get_object_or_404(PlaygroundImage, id=item_id)
            
            # Delete file from storage
            if image.image:
                default_storage.delete(image.image.name)
            
            image.delete()
            
        elif item_type == 'video':
            video = get_object_or_404(PlaygroundVideo, id=item_id)
            video.delete()
            
        return JsonResponse({
            'success': True,
            'message': f'{item_type} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting media item: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Helper functions

def validate_image_file(image_file):
    """Validate uploaded image file"""
    # Check file size (max 10MB)
    if image_file.size > 10 * 1024 * 1024:
        return False
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return False
    
    return True

def process_cover_image(image_file):
    """Process cover image for optimal display"""
    try:
        # Open image with PIL
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize for cover slider (max 1920x1080)
        max_width, max_height = 1920, 1080
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save processed image
        from io import BytesIO
        output = BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return ContentFile(output.read(), name=f"cover_{uuid.uuid4()}.jpg")
        
    except Exception as e:
        logger.error(f"Error processing cover image: {str(e)}")
        return image_file

def process_gallery_image(image_file):
    """Process gallery image for optimal display"""
    try:
        # Open image with PIL
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize for gallery (max 1200x800)
        max_width, max_height = 1200, 800
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save processed image
        from io import BytesIO
        output = BytesIO()
        image.save(output, format='JPEG', quality=80, optimize=True)
        output.seek(0)
        
        return ContentFile(output.read(), name=f"gallery_{uuid.uuid4()}.jpg")
        
    except Exception as e:
        logger.error(f"Error processing gallery image: {str(e)}")
        return image_file

def save_temp_image(image_file, image_type, original_name):
    """Save image to temporary storage"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save file
        filename = f"{image_type}_{uuid.uuid4()}_{original_name}"
        file_path = default_storage.save(f"temp_uploads/{filename}", image_file)
        
        # Return URL
        return default_storage.url(file_path)
        
    except Exception as e:
        logger.error(f"Error saving temp image: {str(e)}")
        return ""
