from django.urls import path
from . import api_views, views

app_name = 'messaging'

urlpatterns = [
    # Page Views
    path('', views.messages_page, name='messages_page'),
    
    # Conversation APIs
    path('api/conversations/', api_views.conversations_list_api, name='conversations_list_api'),
    path('api/conversations/<int:conversation_id>/messages/', api_views.conversation_messages_api, name='conversation_messages_api'),
    path('api/conversations/<int:conversation_id>/mark-read/', api_views.mark_conversation_read_api, name='mark_conversation_read_api'),
    
    # Message APIs
    path('api/messages/send/', api_views.send_message_api, name='send_message_api'),
    path('api/messages/<int:message_id>/delete/', api_views.delete_message_api, name='delete_message_api'),
    path('api/messages/unread-count/', api_views.unread_messages_count_api, name='unread_messages_count_api'),
    
    # Start conversation
    path('api/conversations/start/', api_views.start_conversation_api, name='start_conversation_api'),
    
    # Admin APIs
    path('api/admin/conversations/', api_views.admin_conversations_api, name='admin_conversations_api'),
]
