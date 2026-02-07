"""
URL configuration for playground_booking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from playgrounds.views_partner_register import PartnerRegisterView

# Main URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('playgrounds/', include('playgrounds.urls')),
    path('partner/register/', PartnerRegisterView.as_view(), name='partner_register'),
    path('bookings/', include('bookings.urls')),
    path('notifications/', include('notifications.urls')),
    path('earnings/', include('earnings.urls')),
    path('admin-panel/', include('adminpanel.urls')),
    path('messages/', include('messaging.urls')),
    path('api/admin/', include('adminpanel.api_urls')),
    path('api/', include('api.urls')),  # Partner Applications API enabled
    path('test-design/', TemplateView.as_view(template_name='test_design.html'), name='test_design'),
    path('test-location/', TemplateView.as_view(template_name='test_location_ui.html'), name='test_location'),
    path('test-playground-type-api/', lambda request: __import__('test_api_playground_type').test_playground_type_api(request), name='test_playground_type_api'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
