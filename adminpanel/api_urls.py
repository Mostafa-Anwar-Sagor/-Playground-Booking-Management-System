from django.urls import path
from . import api_views

app_name = 'adminpanel_api'

urlpatterns = [
    # Existing endpoints
    path('partner-applications/', api_views.PartnerApplicationAPIView.as_view(), name='partner_applications_api'),
    path('partner-applications/<int:app_id>/', api_views.PartnerApplicationDetailAPIView.as_view(), name='partner_application_detail_api'),
    path('owners/', api_views.ActiveOwnersAPIView.as_view(), name='active_owners_api'),
    path('owner/<int:owner_id>/update/', api_views.OwnerUpdateAPIView.as_view(), name='owner_update_api'),
    path('analytics/', api_views.AnalyticsAPIView.as_view(), name='analytics_api'),
    
    # New comprehensive admin endpoints
    path('stats/', api_views.admin_stats_api, name='admin_stats'),
    path('users/', api_views.admin_users_list_api, name='admin_users'),
    path('bookings/', api_views.admin_bookings_list_api, name='admin_bookings'),
    path('playgrounds/', api_views.admin_playgrounds_list_api, name='admin_playgrounds'),
    path('payments/pending/', api_views.admin_pending_payments_api, name='admin_pending_payments'),
    path('payments/verify/', api_views.admin_verify_payment_api, name='admin_verify_payment'),
    path('users/manage/', api_views.admin_manage_user_api, name='admin_manage_user'),
    path('playgrounds/manage/', api_views.admin_manage_playground_api, name='admin_manage_playground'),
]

