from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Count, Prefetch
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Conversation, Message
from playgrounds.models import Playground
import json


@login_required
@require_GET
def conversations_list_api(request):
    """
    Get list of conversations for the current user.
    Returns conversations where user is either the customer or the playground owner.
    """
    user = request.user
    
    # Get conversations where user is a participant
    conversations = Conversation.objects.filter(
        Q(user=user) | Q(playground_owner=user),
        is_active=True
    ).select_related(
        'user', 'playground_owner', 'playground'
    ).prefetch_related(
        'messages'
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(conversations, 20)
    page_obj = paginator.get_page(page)
    
    conversations_data = []
    for conv in page_obj:
        other_user = conv.get_other_participant(user)
        last_msg = conv.last_message()
        unread_count = conv.unread_count_for_user(user)
        
        conversations_data.append({
            'id': conv.id,
            'subject': conv.subject,
            'other_user': {
                'id': other_user.id,
                'name': other_user.get_full_name() or other_user.email,
                'email': other_user.email,
                'is_owner': other_user == conv.playground_owner,
                'avatar': other_user.first_name[0].upper() if other_user.first_name else other_user.email[0].upper()
            },
            'playground': {
                'id': conv.playground.id,
                'name': conv.playground.name,
            } if conv.playground else None,
            'last_message': {
                'content': last_msg.content[:100],
                'sender_id': last_msg.sender.id,
                'created_at': last_msg.created_at.isoformat(),
                'is_read': last_msg.is_read,
            } if last_msg else None,
            'unread_count': unread_count,
            'created_at': conv.created_at.isoformat(),
            'updated_at': conv.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'conversations': conversations_data,
        'total_count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })


@login_required
@require_GET
def conversation_messages_api(request, conversation_id):
    """
    Get messages for a specific conversation.
    """
    user = request.user
    
    try:
        conversation = Conversation.objects.select_related(
            'user', 'playground_owner', 'playground'
        ).get(
            Q(id=conversation_id),
            Q(user=user) | Q(playground_owner=user)
        )
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'}, status=404)
    
    # Get messages
    messages = conversation.messages.filter(is_deleted=False).select_related('sender')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(messages, 50)
    page_obj = paginator.get_page(page)
    
    # Mark unread messages as read
    unread_messages = page_obj.object_list.filter(is_read=False).exclude(sender=user)
    for msg in unread_messages:
        msg.mark_as_read()
    
    messages_data = []
    for msg in page_obj:
        messages_data.append({
            'id': msg.id,
            'sender': {
                'id': msg.sender.id,
                'name': msg.sender.get_full_name() or msg.sender.email,
                'email': msg.sender.email,
                'avatar': msg.sender.first_name[0].upper() if msg.sender.first_name else msg.sender.email[0].upper(),
                'is_me': msg.sender == user,
            },
            'content': msg.content,
            'attachment': msg.attachment.url if msg.attachment else None,
            'is_read': msg.is_read,
            'read_at': msg.read_at.isoformat() if msg.read_at else None,
            'created_at': msg.created_at.isoformat(),
            'edited_at': msg.edited_at.isoformat() if msg.edited_at else None,
        })
    
    other_user = conversation.get_other_participant(user)
    
    return JsonResponse({
        'success': True,
        'conversation': {
            'id': conversation.id,
            'subject': conversation.subject,
            'other_user': {
                'id': other_user.id,
                'name': other_user.get_full_name() or other_user.email,
                'email': other_user.email,
                'avatar': other_user.first_name[0].upper() if other_user.first_name else other_user.email[0].upper(),
            },
            'playground': {
                'id': conversation.playground.id,
                'name': conversation.playground.name,
            } if conversation.playground else None,
        },
        'messages': messages_data,
        'total_count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })


@login_required
@require_POST
def send_message_api(request):
    """
    Send a new message in a conversation.
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Message content is required'}, status=400)
        
        # Get conversation
        conversation = Conversation.objects.get(
            Q(id=conversation_id),
            Q(user=user) | Q(playground_owner=user)
        )
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': {
                    'id': user.id,
                    'name': user.get_full_name() or user.email,
                    'email': user.email,
                    'avatar': user.first_name[0].upper() if user.first_name else user.email[0].upper(),
                    'is_me': True,
                },
                'content': message.content,
                'is_read': False,
                'created_at': message.created_at.isoformat(),
            }
        })
        
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def start_conversation_api(request):
    """
    Start a new conversation with a playground owner.
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        playground_id = data.get('playground_id')
        subject = data.get('subject', 'General Inquiry')
        initial_message = data.get('message', '').strip()
        
        if not playground_id:
            return JsonResponse({'success': False, 'error': 'Playground ID is required'}, status=400)
        
        if not initial_message:
            return JsonResponse({'success': False, 'error': 'Initial message is required'}, status=400)
        
        # Get playground
        playground = Playground.objects.select_related('owner').get(id=playground_id)
        
        if playground.owner == user:
            return JsonResponse({'success': False, 'error': 'Cannot start conversation with yourself'}, status=400)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            user=user,
            playground_owner=playground.owner,
            playground=playground,
            is_active=True
        ).first()
        
        if existing_conversation:
            # Use existing conversation
            conversation = existing_conversation
        else:
            # Create new conversation
            conversation = Conversation.objects.create(
                user=user,
                playground_owner=playground.owner,
                playground=playground,
                subject=subject
            )
        
        # Create initial message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=initial_message
        )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'message': 'Conversation started successfully'
        })
        
    except Playground.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Playground not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_GET
def unread_messages_count_api(request):
    """
    Get count of unread messages for the current user.
    """
    user = request.user
    
    # Count unread messages where user is the recipient
    unread_count = Message.objects.filter(
        Q(conversation__user=user) | Q(conversation__playground_owner=user),
        is_read=False
    ).exclude(sender=user).count()
    
    return JsonResponse({
        'success': True,
        'unread_count': unread_count
    })


@login_required
@require_POST
def mark_conversation_read_api(request, conversation_id):
    """
    Mark all messages in a conversation as read.
    """
    user = request.user
    
    try:
        conversation = Conversation.objects.get(
            Q(id=conversation_id),
            Q(user=user) | Q(playground_owner=user)
        )
        
        # Mark all unread messages as read
        unread_messages = conversation.messages.filter(is_read=False).exclude(sender=user)
        for msg in unread_messages:
            msg.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation marked as read'
        })
        
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def delete_message_api(request, message_id):
    """
    Delete a message (soft delete).
    """
    user = request.user
    
    try:
        message = Message.objects.get(id=message_id, sender=user)
        message.is_deleted = True
        message.save(update_fields=['is_deleted'])
        
        return JsonResponse({
            'success': True,
            'message': 'Message deleted successfully'
        })
        
    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found or unauthorized'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Admin APIs
@login_required
@require_GET
def admin_conversations_api(request):
    """
    Get all conversations for admin monitoring.
    Only accessible to staff/admin users.
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get filter parameters
    flagged_only = request.GET.get('flagged', 'false').lower() == 'true'
    search = request.GET.get('search', '').strip()
    
    conversations = Conversation.objects.all().select_related(
        'user', 'playground_owner', 'playground'
    ).annotate(
        message_count=Count('messages'),
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    if flagged_only:
        conversations = conversations.filter(flagged_for_review=True)
    
    if search:
        conversations = conversations.filter(
            Q(user__email__icontains=search) |
            Q(playground_owner__email__icontains=search) |
            Q(playground__name__icontains=search) |
            Q(subject__icontains=search)
        )
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(conversations, 20)
    page_obj = paginator.get_page(page)
    
    conversations_data = []
    for conv in page_obj:
        last_msg = conv.last_message()
        
        conversations_data.append({
            'id': conv.id,
            'subject': conv.subject,
            'user': {
                'id': conv.user.id,
                'email': conv.user.email,
                'name': conv.user.get_full_name() or conv.user.email,
            },
            'playground_owner': {
                'id': conv.playground_owner.id,
                'email': conv.playground_owner.email,
                'name': conv.playground_owner.get_full_name() or conv.playground_owner.email,
            },
            'playground': {
                'id': conv.playground.id,
                'name': conv.playground.name,
            } if conv.playground else None,
            'message_count': conv.message_count,
            'last_message': {
                'content': last_msg.content[:100],
                'created_at': last_msg.created_at.isoformat(),
            } if last_msg else None,
            'flagged_for_review': conv.flagged_for_review,
            'admin_notes': conv.admin_notes,
            'is_active': conv.is_active,
            'created_at': conv.created_at.isoformat(),
            'updated_at': conv.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'conversations': conversations_data,
        'total_count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })
