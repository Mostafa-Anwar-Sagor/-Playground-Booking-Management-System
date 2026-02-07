from django.urls import path
from . import api_views

app_name = 'playground_api'

urlpatterns = [
    # Location APIs
    path('api/countries/', api_views.CountriesAPIView.as_view(), name='countries'),
    path('api/states/<int:country_id>/', api_views.StatesAPIView.as_view(), name='states'),
    path('api/cities/<int:state_id>/', api_views.CitiesAPIView.as_view(), name='cities'),
    
    # Playground & Sport Types APIs
    path('api/playground-types/', api_views.PlaygroundTypesAPIView.as_view(), name='playground_types'),
    path('api/sport-types/', api_views.SportTypesAPIView.as_view(), name='sport_types'),
    
    # Amenities API
    path('api/amenities/', api_views.AmenitiesAPIView.as_view(), name='amenities'),
    
    # Time Slots APIs
    path('api/time-slots/generate/', api_views.GenerateTimeSlotsAPIView.as_view(), name='generate_time_slots'),
    path('api/time-slots/validate/', api_views.ValidateTimeSlotsAPIView.as_view(), name='validate_time_slots'),
    path('api/time-slots/availability/', api_views.CheckAvailabilityAPIView.as_view(), name='check_availability'),
    
    # Form Preview & Validation APIs
    path('api/preview/', api_views.PlaygroundPreviewAPIView.as_view(), name='playground_preview'),
    path('api/validate-field/', api_views.ValidateFieldAPIView.as_view(), name='validate_field'),
    path('api/check-name-availability/', api_views.CheckNameAvailabilityAPIView.as_view(), name='check_name_availability'),
    
    # Media Upload APIs
    path('api/upload-image/', api_views.ImageUploadAPIView.as_view(), name='upload_image'),
    path('api/upload-video/', api_views.VideoUploadAPIView.as_view(), name='upload_video'),
    
    # Draft Management APIs
    path('api/save-draft/', api_views.SaveDraftAPIView.as_view(), name='save_draft'),
    path('api/load-draft/', api_views.LoadDraftAPIView.as_view(), name='load_draft'),
    
    # Legacy/Utility APIs
    path('api/location/', api_views.LocationAPIView.as_view(), name='location'),
    path('api/currency/', api_views.CurrencyAPIView.as_view(), name='currency'),
]
