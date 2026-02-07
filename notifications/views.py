from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from .models import Notification, Message


class NotificationListView(LoginRequiredMixin, TemplateView):
    template_name = 'notifications/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get notification statistics
        notifications = user.notifications.all()
        context['total_notifications'] = notifications.count()
        context['unread_count'] = notifications.filter(is_read=False).count()
        context['today_count'] = notifications.filter(created_at__date=timezone.now().date()).count()
        
        return context


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Get paginated notifications for the current user"""
    user = request.user
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    notification_type = request.GET.get('type', '')
    priority = request.GET.get('priority', '')
    unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
    
    # Build query
    notifications = user.notifications.all()
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if priority:
        notifications = notifications.filter(priority=priority)
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    # Paginate
    paginator = Paginator(notifications, per_page)
    page_obj = paginator.get_page(page)
    
    # Serialize notifications
    notifications_data = []
    for notification in page_obj:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'time_since': notification.time_since_created,
            'icon_class': notification.get_icon_class(),
            'priority_class': notification.get_priority_class(),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
            'booking_id': notification.booking.id if notification.booking else None,
            'playground_name': notification.playground.name if notification.playground else None,
        })
    
    # Get notification statistics
    stats = {
        'total': notifications.count(),
        'unread': notifications.filter(is_read=False).count(),
        'today': notifications.filter(created_at__date=timezone.now().date()).count(),
        'this_week': notifications.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
    }
    
    return Response({
        'notifications': notifications_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        },
        'stats': stats,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'read_at': notification.read_at.isoformat() if notification.read_at else None,
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    try:
        unread_notifications = request.user.notifications.filter(is_read=False)
        count = unread_notifications.count()
        
        # Bulk update
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': f'Marked {count} notifications as read',
            'count': count,
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """Get paginated messages for the current user"""
    user = request.user
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    message_type = request.GET.get('type', '')
    unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
    
    # Get messages where user is sender or recipient
    messages = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).distinct()
    
    if message_type:
        messages = messages.filter(message_type=message_type)
    
    if unread_only:
        messages = messages.filter(recipient=user, is_read=False)
    
    # Paginate
    paginator = Paginator(messages, per_page)
    page_obj = paginator.get_page(page)
    
    # Serialize messages
    messages_data = []
    for message in page_obj:
        # Determine if current user is sender or recipient
        is_sender = message.sender == user
        other_user = message.recipient if is_sender else message.sender
        
        messages_data.append({
            'id': message.id,
            'subject': message.subject,
            'message': message.message,
            'message_type': message.message_type,
            'status': message.status,
            'is_read': message.is_read,
            'is_sender': is_sender,
            'created_at': message.created_at.isoformat(),
            'time_since': message.time_since_created,
            'icon_class': message.get_message_type_icon(),
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'first_name': other_user.first_name,
                'last_name': other_user.last_name,
                'initials': message.get_sender_initials() if not is_sender else f"{other_user.first_name[0] if other_user.first_name else ''}{other_user.last_name[0] if other_user.last_name else ''}".upper() or other_user.username[0].upper(),
                'avatar': message.get_sender_avatar() if not is_sender else None,
            },
            'booking_id': message.booking.id if message.booking else None,
            'playground_name': message.playground.name if message.playground else None,
            'thread_id': message.thread_id,
            'reply_count': message.replies.count() if hasattr(message, 'replies') else 0,
        })
    
    # Get message statistics
    stats = {
        'total': messages.count(),
        'unread': messages.filter(recipient=user, is_read=False).count(),
        'sent': messages.filter(sender=user).count(),
        'received': messages.filter(recipient=user).count(),
        'support_tickets': messages.filter(message_type='support').count(),
    }
    
    return Response({
        'messages': messages_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        },
        'stats': stats,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_read(request, message_id):
    """Mark a specific message as read"""
    try:
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Message marked as read',
            'read_at': message.read_at.isoformat() if message.read_at else None,
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Send a new message"""
    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        subject = data.get('subject')
        message_text = data.get('message')
        message_type = data.get('message_type', 'direct')
        booking_id = data.get('booking_id')
        
        if not recipient_id or not subject or not message_text:
            return Response({
                'success': False,
                'error': 'Recipient, subject, and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Create message
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            message=message_text,
            message_type=message_type,
            booking_id=booking_id if booking_id else None,
        )
        
        return Response({
            'success': True,
            'message_id': message.id,
            'message': 'Message sent successfully',
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_stats(request):
    """Get notification statistics for dashboard"""
    user = request.user
    now = timezone.now()
    
    stats = {
        'total_notifications': user.notifications.count(),
        'unread_notifications': user.notifications.filter(is_read=False).count(),
        'today_notifications': user.notifications.filter(created_at__date=now.date()).count(),
        'this_week_notifications': user.notifications.filter(created_at__gte=now - timezone.timedelta(days=7)).count(),
        'urgent_notifications': user.notifications.filter(priority='urgent', is_read=False).count(),
        
        'total_messages': Message.objects.filter(Q(sender=user) | Q(recipient=user)).count(),
        'unread_messages': user.received_messages.filter(is_read=False).count(),
        'sent_messages': user.sent_messages.count(),
        'support_tickets': Message.objects.filter(
            Q(sender=user, message_type='support') | Q(recipient=user, message_type='support')
        ).count(),
    }
    
    # Recent activity (last 7 days)
    recent_notifications = user.notifications.filter(
        created_at__gte=now - timezone.timedelta(days=7)
    ).values('notification_type').annotate(count=Count('id'))
    
    stats['recent_activity'] = list(recent_notifications)
    
    return Response(stats)
