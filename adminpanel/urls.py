from django.urls import path

from . import views
from . import api_views

app_name = 'adminpanel'

urlpatterns = [
    # Main Admin Dashboard - Single unified panel
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # API Endpoints for Admin Panel
    path('api/stats/', api_views.admin_stats_api, name='admin_stats'),
    path('api/users/', api_views.admin_users_list_api, name='admin_users'),
    path('api/bookings/', api_views.admin_bookings_list_api, name='admin_bookings'),
    path('api/playgrounds/', api_views.admin_playgrounds_list_api, name='admin_playgrounds'),
    path('api/payments/pending/', api_views.admin_pending_payments_api, name='admin_pending_payments'),
    path('api/payments/verify/', api_views.admin_verify_payment_api, name='admin_verify_payment'),
    path('api/users/manage/', api_views.admin_manage_user_api, name='admin_manage_user'),
    path('api/playgrounds/manage/', api_views.admin_manage_playground_api, name='admin_manage_playground'),
    path('api/partner-applications/', api_views.PartnerApplicationAPIView.as_view(), name='partner_applications_api'),
    path('api/partner-applications/<int:app_id>/', api_views.PartnerApplicationDetailAPIView.as_view(), name='partner_application_detail_api'),
]
