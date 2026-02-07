from django.urls import path, include
from . import views
from .api_views import (
    LocationAPIView, CurrencyAPIView, PlaygroundPreviewAPIView,
    CountriesAPIView, StatesAPIView, CitiesAPIView, SportTypesAPIView,
    GenerateTimeSlotsAPIView, ImageUploadAPIView, SaveDraftAPIView, 
    AmenitiesAPIView, PlaygroundTypesAPIView, ValidateTimeSlotsAPIView,
    CheckAvailabilityAPIView, ValidateFieldAPIView, CheckNameAvailabilityAPIView,
    VideoUploadAPIView, LoadDraftAPIView, SubmissionAPIView
)

app_name = 'playgrounds'

urlpatterns = [
    # Search and listing
    path('', views.PlaygroundListView.as_view(), name='playground_search'),
    path('search/', views.PlaygroundSearchView.as_view(), name='search'),
    path('details/<int:pk>/', views.PlaygroundDetailView.as_view(), name='playground_detail'),
    
    # Owner playground management
    path('my-playgrounds/', views.MyPlaygroundsView.as_view(), name='my_playgrounds'),
    path('add/', views.AddPlaygroundView.as_view(), name='add_playground'),
    path('edit/<int:pk>/', views.EditPlaygroundView.as_view(), name='edit_playground'),
    path('manage/<int:pk>/', views.ManagePlaygroundView.as_view(), name='manage_playground'),
    
    # Complete API endpoints for dynamic form functionality
    path('api/location/', LocationAPIView.as_view(), name='api_location'),
    path('api/currency/', CurrencyAPIView.as_view(), name='api_currency'),
    path('api/preview/', PlaygroundPreviewAPIView.as_view(), name='api_preview'),
    
    # Location APIs
    path('api/countries/', CountriesAPIView.as_view(), name='api_countries'),
    path('api/states/<int:country_id>/', StatesAPIView.as_view(), name='api_states'),
    path('api/cities/<int:state_id>/', CitiesAPIView.as_view(), name='api_cities'),
    
    # Playground & Sport Types APIs
    path('api/playground-types/', PlaygroundTypesAPIView.as_view(), name='api_playground_types'),
    path('api/sport-types/', SportTypesAPIView.as_view(), name='api_sport_types'),
    
    # Amenities API
    path('api/amenities/', AmenitiesAPIView.as_view(), name='api_amenities'),
    
    # Time Slots APIs
    path('api/time-slots/generate/', GenerateTimeSlotsAPIView.as_view(), name='api_generate_time_slots'),
    path('api/time-slots/validate/', ValidateTimeSlotsAPIView.as_view(), name='api_validate_time_slots'),
    path('api/time-slots/availability/', CheckAvailabilityAPIView.as_view(), name='api_check_availability'),
    
    # Slots and booking APIs  
    path('api/slots-by-date/', views.load_slots_by_date, name='api_slots_by_date'),
    path('api/membership-passes/', views.load_membership_passes, name='api_membership_passes'),
    path('api/custom-slots/', views.load_custom_slots, name='api_custom_slots'),
    path('api/amenities/', views.load_amenities, name='api_amenities'),
    path('api/booking-info/', views.load_booking_info, name='api_booking_info'),
    
    # Form Validation APIs
    path('api/validate-field/', ValidateFieldAPIView.as_view(), name='api_validate_field'),
    path('api/check-name-availability/', CheckNameAvailabilityAPIView.as_view(), name='api_check_name_availability'),
    
    # Media Upload APIs
    path('api/upload-image/', ImageUploadAPIView.as_view(), name='api_upload_image'),
    path('api/upload-video/', VideoUploadAPIView.as_view(), name='api_upload_video'),
    
    # Draft Management APIs
    path('api/save-draft/', SaveDraftAPIView.as_view(), name='api_save_draft'),
    path('api/load-draft/', LoadDraftAPIView.as_view(), name='api_load_draft'),
    
    # Enhanced Submission API
    path('api/submit/', SubmissionAPIView.as_view(), name='api_submit'),
    
    # Legacy AJAX endpoints (keeping for compatibility)
    path('ajax/get-states/', views.get_states, name='ajax_get_states'),
    path('ajax/get-cities/', views.get_cities, name='ajax_get_cities'),
    path('ajax/check-availability/', views.check_availability, name='ajax_check_availability'),

    # Partner registration
    path('register/', __import__('playgrounds.views_partner_register').views_partner_register.PartnerRegisterView.as_view(), name='partner_register'),
]
