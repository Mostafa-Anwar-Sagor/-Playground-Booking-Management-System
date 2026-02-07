from django.urls import path
from . import views, api_views

app_name = 'notifications'

urlpatterns = [
    # Web views
    path('', views.NotificationListView.as_view(), name='notification_list'),
    
    # API endpoints for notifications
    path('api/notifications/', api_views.get_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', api_views.mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', api_views.mark_all_notifications_read, name='api_mark_all_read'),
    path('api/notifications/stats/', api_views.get_notification_stats, name='api_notification_stats'),
    
    # API endpoints for messages
    path('api/messages/', api_views.get_messages, name='api_messages'),
    path('api/messages/<int:message_id>/read/', api_views.mark_message_read, name='api_mark_message_read'),
    path('api/messages/send/', api_views.send_message, name='api_send_message'),
    path('api/messages/conversations/', api_views.get_conversations, name='api_conversations'),
    
    # API endpoints for system messages
    path('api/system-messages/', api_views.get_system_messages, name='api_system_messages'),
]
