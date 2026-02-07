from django.urls import path
from . import views
from . import dashboard_api
from . import unified_dashboard

app_name = 'accounts'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    
    # Unified Dashboard (routes to appropriate dashboard based on role)
    path('my-dashboard/', unified_dashboard.unified_dashboard, name='my_dashboard'),
    
    # Dashboards
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),  # Main user dashboard
    path('user-dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('owner-dashboard/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # New comprehensive dashboards
    path('admin-panel/', unified_dashboard.admin_panel_dashboard, name='admin_panel'),
    path('owner-panel/', unified_dashboard.owner_panel_dashboard, name='owner_panel'),
    
    # Dashboard API endpoints
    path('api/dashboard/data/', dashboard_api.dashboard_data_api, name='dashboard_data_api'),
    path('api/dashboard/activity/<int:days>/', dashboard_api.dashboard_activity_api, name='dashboard_activity_api'),
    path('api/dashboard/notifications/', dashboard_api.dashboard_notifications_api, name='dashboard_notifications_api'),
    path('api/user-stats/', dashboard_api.user_stats_api, name='user_stats_api'),
    
    # Bookings API endpoints
    path('api/bookings/list/', views.bookings_list_api, name='bookings_list_api'),
    
    # Partner Application
    path('become-partner/', views.BecomePartnerView.as_view(), name='become_partner'),
    path('partner-application/', views.PartnerApplicationView.as_view(), name='partner_application'),
    
    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('notifications-settings/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    
    # Static pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('refund-policy/', views.RefundPolicyView.as_view(), name='refund_policy'),
]
