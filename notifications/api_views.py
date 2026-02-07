from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import json

from .models import Notification, Message, SystemMessage, NotificationPreference
from accounts.models import User
from bookings.models import Booking


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get notifications for the current user with pagination and filtering"""
    try:
        user = request.user
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        notification_type = request.GET.get('type', '')
        is_read = request.GET.get('is_read', '')
        priority = request.GET.get('priority', '')

        # Build query
        queryset = Notification.objects.filter(recipient=user)
        
        # Apply filters
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if is_read:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Exclude expired notifications
        queryset = queryset.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        
        # Order by priority and creation date
        queryset = queryset.order_by(
            '-priority',  # urgent, high, normal, low
            '-created_at'
        )
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        notifications_page = paginator.get_page(page)
        
        # Serialize notifications
        notifications_data = []
        for notification in notifications_page:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'time_since_created': notification.time_since_created,
                'icon_class': notification.get_icon_class(),
                'priority_class': notification.get_priority_class(),
                'action_url': notification.action_url,
                'action_text': notification.action_text,
                'booking_id': notification.booking.id if notification.booking else None,
                'playground_name': notification.playground.name if notification.playground else None,
                'created_at': notification.created_at.isoformat(),
            })
        
        # Get notification counts
        total_count = queryset.count()
        unread_count = queryset.filter(is_read=False).count()
        
        # Get counts by type
        type_counts = queryset.values('notification_type').annotate(count=Count('id'))
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'pagination': {
                'current_page': notifications_page.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_next': notifications_page.has_next(),
                'has_previous': notifications_page.has_previous(),
            },
            'stats': {
                'total_count': total_count,
                'unread_count': unread_count,
                'type_counts': list(type_counts),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    try:
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        
        count = unread_notifications.count()
        
        # Bulk update
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notifications marked as read'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_messages(request):
    """Get messages for the current user with pagination and filtering"""
    try:
        user = request.user
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        message_type = request.GET.get('type', '')
        is_read = request.GET.get('is_read', '')
        thread_id = request.GET.get('thread_id', '')

        # Build query - get both sent and received messages
        queryset = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )
        
        # Apply filters
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        if is_read:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        
        # Order by creation date
        queryset = queryset.order_by('-created_at')
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        messages_page = paginator.get_page(page)
        
        # Serialize messages
        messages_data = []
        for message in messages_page:
            is_sender = message.sender == user
            other_user = message.recipient if is_sender else message.sender
            
            # Safe attribute access
            sender_username = message.sender.username if message.sender else 'Unknown'
            sender_first_name = message.sender.first_name if message.sender else ''
            sender_last_name = message.sender.last_name if message.sender else ''
            sender_full_name = f"{sender_first_name} {sender_last_name}".strip() if sender_first_name or sender_last_name else sender_username
            
            recipient_username = message.recipient.username if message.recipient else 'Unknown'
            recipient_first_name = message.recipient.first_name if message.recipient else ''
            recipient_last_name = message.recipient.last_name if message.recipient else ''
            recipient_full_name = f"{recipient_first_name} {recipient_last_name}".strip() if recipient_first_name or recipient_last_name else recipient_username
            
            other_user_username = other_user.username if other_user else 'Unknown'
            other_user_first_name = other_user.first_name if other_user else ''
            other_user_last_name = other_user.last_name if other_user else ''
            other_user_full_name = f"{other_user_first_name} {other_user_last_name}".strip() if other_user_first_name or other_user_last_name else other_user_username
            other_user_initials = other_user_username[0].upper() if other_user_username else 'U'
            
            messages_data.append({
                'id': message.id,
                'subject': message.subject or 'No Subject',
                'message': message.message or '',
                'message_type': message.message_type,
                'status': message.status,
                'is_read': message.is_read,
                'is_sender': is_sender,
                'time_since_created': message.time_since_created,
                'message_type_icon': message.get_message_type_icon(),
                'thread_id': message.thread_id or '',
                'attachment_url': message.attachment_url or '',
                'sender': {
                    'id': message.sender.id if message.sender else 0,
                    'username': sender_username,
                    'full_name': sender_full_name,
                    'initials': message.get_sender_initials(),
                    'avatar_url': message.get_sender_avatar(),
                },
                'recipient': {
                    'id': message.recipient.id if message.recipient else 0,
                    'username': recipient_username,
                    'full_name': recipient_full_name,
                },
                'other_user': {
                    'id': other_user.id if other_user else 0,
                    'username': other_user_username,
                    'full_name': other_user_full_name,
                    'initials': other_user_initials,
                },
                'booking_id': message.booking.id if message.booking else None,
                'playground_name': message.playground.name if message.playground else None,
                'created_at': message.created_at.isoformat(),
            })
        
        # Get message counts
        total_count = queryset.count()
        unread_count = queryset.filter(recipient=user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'pagination': {
                'current_page': messages_page.number,
                'total_pages': paginator.num_pages,
                'total_count': total_count,
                'has_next': messages_page.has_next(),
                'has_previous': messages_page.has_previous(),
            },
            'stats': {
                'total_count': total_count,
                'unread_count': unread_count,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_message(request):
    """Send a new message"""
    try:
        data = json.loads(request.body)
        
        recipient_id = data.get('recipient_id')
        subject = data.get('subject', '').strip()
        message_text = data.get('message', '').strip()
        message_type = data.get('message_type', 'direct')
        booking_id = data.get('booking_id')
        playground_id = data.get('playground_id')
        thread_id = data.get('thread_id')
        parent_message_id = data.get('parent_message_id')
        
        if not recipient_id or not subject or not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Recipient, subject, and message are required'
            }, status=400)
        
        # Get recipient
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Get related objects if provided
        booking = None
        playground = None
        parent_message = None
        
        if booking_id:
            booking = get_object_or_404(Booking, id=booking_id)
            playground = booking.playground
        elif playground_id:
            from playgrounds.models import Playground
            playground = get_object_or_404(Playground, id=playground_id)
        
        if parent_message_id:
            parent_message = get_object_or_404(Message, id=parent_message_id)
            thread_id = parent_message.thread_id or f"thread_{parent_message.id}"
        
        # Generate thread ID if not provided
        if not thread_id:
            thread_id = f"thread_{timezone.now().timestamp()}"
        
        # Create message
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            message=message_text,
            message_type=message_type,
            booking=booking,
            playground=playground,
            thread_id=thread_id,
            parent_message=parent_message,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': message.id,
            'thread_id': thread_id,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_message_read(request, message_id):
    """Mark a specific message as read"""
    try:
        message = get_object_or_404(
            Message, 
            id=message_id, 
            recipient=request.user
        )
        
        message.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Message marked as read'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """Get message conversations grouped by users"""
    try:
        user = request.user
        
        # Get latest message from each conversation
        conversations = []
        
        # Find all users the current user has conversed with
        message_users = set()
        
        # Users who sent messages to current user
        senders = Message.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
        message_users.update(senders)
        
        # Users who received messages from current user
        recipients = Message.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
        message_users.update(recipients)
        
        # Get conversation data for each user
        for other_user_id in message_users:
            try:
                other_user = User.objects.get(id=other_user_id)
                
                # Get latest message in conversation
                latest_message = Message.objects.filter(
                    Q(sender=user, recipient=other_user) |
                    Q(sender=other_user, recipient=user)
                ).order_by('-created_at').first()
                
                if latest_message:
                    # Count unread messages from other user
                    unread_count = Message.objects.filter(
                        sender=other_user,
                        recipient=user,
                        is_read=False
                    ).count()
                    
                    # Safe attribute access
                    other_user_first_name = other_user.first_name or ''
                    other_user_last_name = other_user.last_name or ''
                    other_user_full_name = f"{other_user_first_name} {other_user_last_name}".strip()
                    if not other_user_full_name:
                        other_user_full_name = other_user.username or 'Unknown User'
                    other_user_initials = (other_user.username or 'U')[0].upper()
                    
                    message_text = (latest_message.message or '')[:100]
                    if len(latest_message.message or '') > 100:
                        message_text += '...'
                    
                    conversations.append({
                        'other_user': {
                            'id': other_user.id,
                            'username': other_user.username or 'Unknown',
                            'full_name': other_user_full_name,
                            'initials': other_user_initials,
                        },
                        'latest_message': {
                            'id': latest_message.id,
                            'subject': latest_message.subject or 'No Subject',
                            'message': message_text,
                            'time_since_created': latest_message.time_since_created,
                            'is_sender': latest_message.sender == user,
                            'created_at': latest_message.created_at.isoformat(),
                        },
                        'unread_count': unread_count,
                    })
            except User.DoesNotExist:
                continue  # Skip if user doesn't exist anymore
        
        # Sort by latest message time
        conversations.sort(key=lambda x: x['latest_message']['created_at'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'conversations': conversations,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_system_messages(request):
    """Get system messages visible to the current user"""
    try:
        user = request.user
        
        system_messages = SystemMessage.objects.filter(
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        )
        
        # Filter by audience
        visible_messages = []
        for msg in system_messages:
            if msg.is_visible_for_user(user):
                visible_messages.append({
                    'id': msg.id,
                    'title': msg.title,
                    'content': msg.content,
                    'message_type': msg.message_type,
                    'audience': msg.audience,
                    'is_dismissible': msg.is_dismissible,
                    'show_on_dashboard': msg.show_on_dashboard,
                    'show_as_popup': msg.show_as_popup,
                    'created_at': msg.created_at.isoformat(),
                })
        
        return JsonResponse({
            'success': True,
            'system_messages': visible_messages,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_notification_stats(request):
    """Get notification and message statistics for dashboard"""
    try:
        user = request.user
        
        # Notification stats
        total_notifications = Notification.objects.filter(recipient=user).count()
        unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()
        
        # Recent notifications (last 7 days)
        week_ago = timezone.now() - timezone.timedelta(days=7)
        recent_notifications = Notification.objects.filter(
            recipient=user,
            created_at__gte=week_ago
        ).count()
        
        # Message stats
        total_messages = Message.objects.filter(recipient=user).count()
        unread_messages = Message.objects.filter(recipient=user, is_read=False).count()
        
        # Recent messages (last 7 days)
        recent_messages = Message.objects.filter(
            recipient=user,
            created_at__gte=week_ago
        ).count()
        
        # Notification types breakdown
        notification_types = Notification.objects.filter(
            recipient=user
        ).values('notification_type').annotate(count=Count('id')).order_by('-count')
        
        return JsonResponse({
            'success': True,
            'stats': {
                'notifications': {
                    'total': total_notifications,
                    'unread': unread_notifications,
                    'recent': recent_notifications,
                    'types': list(notification_types),
                },
                'messages': {
                    'total': total_messages,
                    'unread': unread_messages,
                    'recent': recent_messages,
                },
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
