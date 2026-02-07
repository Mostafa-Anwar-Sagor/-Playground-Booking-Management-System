from django.urls import path
from .partner_applications import PartnerApplicationAPIView, PartnerApplicationDetailAPIView
from .currency_api import DynamicCurrencyAPI, detect_user_currency
from .booking_calculation_api import BookingCalculationAPI
from .home_api_enhanced import (
    admin_dashboard_stats, quick_add_playground, manage_playgrounds,
    get_states, get_cities, search_playgrounds, get_live_stats,
    get_popular_playgrounds
)
from .enhanced_owner_api import (
    create_playground_api, upload_playground_media, manage_time_slots,
    real_time_availability, manage_booking_action, analytics_data,
    get_cities_by_state, get_states_by_country, earnings_summary,
    owner_dashboard_stats, pending_bookings_api, approve_booking, reject_booking,
    todays_schedule_api, revenue_analytics_api, playground_performance_api,
    live_notifications_api, get_playgrounds_api
)
from .playground_management import (
    get_countries, get_states as get_states_pm, get_cities as get_cities_pm, 
    get_sport_types, get_owner_playgrounds, create_playground, 
    get_playground_details, delete_playground
)

from .search_api import (
    PlaygroundSearchAPI, SearchSuggestionsAPI, SportsAPI, FacilitiesAPI,
    ReverseGeocodeAPI, SaveSearchAPI
)
from .location_search_api import (
    LocationBasedSearchAPI, LocationDataAPI, SearchSuggestionsAPI as LocationSearchSuggestionsAPI
)
from .playground_api import (
    PlaygroundAPIView, PlaygroundDetailAPIView, BookingRequestAPIView,
    CountriesAPIView, StatesAPIView, CitiesAPIView, SportTypesAPIView, 
    PlaygroundTypesAPIView, available_slots_api, playground_preview_api
)
from .dynamic_data_views import (
    get_countries as dynamic_get_countries, get_states as dynamic_get_states,
    get_cities as dynamic_get_cities, get_sport_types as dynamic_get_sport_types,
    get_playground_types, get_form_data
)
from .dashboard_api import (
    dashboard_data, dashboard_activity, bookings_list, 
    playgrounds_sports, playgrounds_facilities, notifications_count,
    playground_stats, booking_count
)
from .draft_views import (
    save_draft_playground, load_draft_playground, delete_draft_playground
)
from .dynamic_time_slots import (
    generate_dynamic_time_slots, add_custom_slot, get_playground_availability
)
from .realtime_stats_api import get_realtime_stats
from .location_filter_api import (
    get_states_by_country as filter_get_states_by_country,
    get_cities_by_state as filter_get_cities_by_state,
    get_all_locations
)

# Professional Backend APIs
from .professional_slots_api import (
    professional_custom_slots_api, get_slot_types, get_currencies, get_today_slots, get_public_playground_details
)
from .membership_passes_api import (
    membership_passes_api, purchase_membership_pass, get_duration_types, calculate_pass_pricing
)
from .temporary_data_handler import (
    save_temporary_data_to_playground, get_temporary_data_summary, clear_temporary_data
)
from .sport_types_api import (
    get_sport_types as advanced_get_sport_types, get_sport_details,
    get_sport_availability, calculate_sport_pricing
)
from .professional_media_api import (
    upload_cover_images, upload_gallery_images, save_video_data,
    save_virtual_tour_data, get_media_data, delete_media_item, sync_status
)

app_name = 'api'

urlpatterns = [
    # Partner Applications API
    path('partner-applications/', PartnerApplicationAPIView.as_view(), name='partner_applications_api'),
    path('partner-applications/<int:app_id>/<str:action>/', PartnerApplicationDetailAPIView.as_view(), name='partner_application_action'),
    path('partner-applications/<int:app_id>/', PartnerApplicationDetailAPIView.as_view(), name='partner_application_detail'),
    
    # Home page API endpoints
    path('states/', get_states, name='get_states'),
    path('cities/', get_cities, name='get_cities'),
    path('search-playgrounds/', search_playgrounds, name='search_playgrounds'),
    path('live-stats/', get_live_stats, name='live_stats'),
    path('popular-playgrounds/', get_popular_playgrounds, name='popular_playgrounds'),
    path('realtime-stats/', get_realtime_stats, name='realtime_stats'),
    
    # Location Filter API for search dropdowns
    path('filter/states/', filter_get_states_by_country, name='filter_states_by_country'),
    path('filter/cities/', filter_get_cities_by_state, name='filter_cities_by_state'),
    path('filter/locations/', get_all_locations, name='filter_all_locations'),
    
    # Location-based Search API endpoints
    path('location-search/', LocationBasedSearchAPI.as_view(), name='location_search'),
    path('location-data/', LocationDataAPI.as_view(), name='location_data'),
    path('location-suggestions/', LocationSearchSuggestionsAPI.as_view(), name='location_suggestions'),
    
    # Enhanced Admin/Owner Management APIs
    path('admin/dashboard-stats/', admin_dashboard_stats, name='admin_dashboard_stats'),
    path('admin/quick-add-playground/', quick_add_playground, name='quick_add_playground'),
    path('admin/manage-playgrounds/', manage_playgrounds, name='manage_playgrounds'),
    
    # Owner Dashboard API endpoints
    path('owner/dashboard-stats/', owner_dashboard_stats, name='owner_dashboard_stats'),
    path('owner/pending-bookings/', pending_bookings_api, name='pending_bookings_api'),
    path('owner/approve-booking/<int:booking_id>/', approve_booking, name='approve_booking'),
    path('owner/reject-booking/<int:booking_id>/', reject_booking, name='reject_booking'),
    path('owner/todays-schedule/', todays_schedule_api, name='todays_schedule_api'),
    path('owner/revenue-analytics/', revenue_analytics_api, name='revenue_analytics_api'),
    path('owner/playground-performance/', playground_performance_api, name='playground_performance_api'),
    path('owner/notifications/', live_notifications_api, name='live_notifications_api'),
    
    # Enhanced Owner API endpoints
    path('owner/create-playground/', create_playground_api, name='create_playground_api'),
    path('owner/upload-media/', upload_playground_media, name='upload_playground_media'),
    path('owner/manage-time-slots/', manage_time_slots, name='manage_time_slots'),
    path('owner/real-time-availability/', real_time_availability, name='real_time_availability'),
    path('owner/manage-booking/', manage_booking_action, name='manage_booking_action'),
    path('owner/analytics/', analytics_data, name='analytics_data'),
    path('owner/earnings/', earnings_summary, name='earnings_summary'),
    path('owner/playgrounds/', get_playgrounds_api, name='get_playgrounds_api'),
    
    # Location APIs
    path('states-by-country/', get_states_by_country, name='get_states_by_country'),
    path('cities-by-state/', get_cities_by_state, name='get_cities_by_state'),
    
    # New Playground Management APIs
    path('countries/', get_countries, name='get_countries'),
    path('states/', get_states_pm, name='get_states_pm'),
    path('cities/', get_cities_pm, name='get_cities_pm'),
    path('sport-types/', get_sport_types, name='get_sport_types'),
    path('owner-playgrounds/', get_owner_playgrounds, name='get_owner_playgrounds'),
    path('create-playground/', create_playground, name='create_playground'),
    path('playground/<int:playground_id>/', get_public_playground_details, name='get_public_playground_details'),
    path('playground/<int:playground_id>/delete/', delete_playground, name='delete_playground'),
    
    # Advanced Professional Sport Types API
    path('sport-types/advanced/', advanced_get_sport_types, name='advanced_sport_types'),
    path('sport-types/advanced/<str:sport_id>/', get_sport_details, name='advanced_sport_details'),
    path('sport-types/advanced/<str:sport_id>/availability/', get_sport_availability, name='advanced_sport_availability'),
    path('sport-types/pricing/calculate/', calculate_sport_pricing, name='advanced_sport_pricing'),
    
    # Enhanced Playground Management API (v2)
    path('v2/playgrounds/', PlaygroundAPIView.as_view(), name='playground_list_v2'),
    path('v2/playgrounds/<int:playground_id>/', PlaygroundDetailAPIView.as_view(), name='playground_detail_v2'),
    path('v2/booking-requests/', BookingRequestAPIView.as_view(), name='booking_requests_v2'),
    
    # Enhanced Utility APIs (v2)
    path('v2/countries/', CountriesAPIView.as_view(), name='countries_v2'),
    path('v2/states/', StatesAPIView.as_view(), name='states_v2'),
    path('v2/cities/', CitiesAPIView.as_view(), name='cities_v2'),
    path('v2/sport-types/', SportTypesAPIView.as_view(), name='sport_types_v2'),
    path('v2/playground-types/', PlaygroundTypesAPIView.as_view(), name='playground_types_v2'),
    path('v2/available-slots/', available_slots_api, name='available_slots_v2'),
    
    # Simple playgrounds endpoint
    path('playgrounds/', get_owner_playgrounds, name='playgrounds_api'),
    path('playgrounds/preview/', playground_preview_api, name='playground_preview'),
    
    # Playground-specific endpoints
    path('playground/<int:playground_id>/sports/', playgrounds_sports, name='playground_sports'),
    path('playground/<int:playground_id>/facilities/', playgrounds_facilities, name='playground_facilities'),
    
    # Advanced Search APIs
    path('playgrounds/search/', PlaygroundSearchAPI.as_view(), name='playground_search'),
    path('playgrounds/suggestions/', SearchSuggestionsAPI.as_view(), name='search_suggestions'),
    path('playgrounds/sports/', SportsAPI.as_view(), name='sports_list'),
    path('playgrounds/facilities/', FacilitiesAPI.as_view(), name='facilities_list'),
    path('playgrounds/reverse-geocode/', ReverseGeocodeAPI.as_view(), name='reverse_geocode'),
    path('playgrounds/save-search/', SaveSearchAPI.as_view(), name='save_search'),
    
    # 🚀 NEW DASHBOARD API ENDPOINTS - FIXED
    path('dashboard/data/', dashboard_data, name='dashboard_data'),
    path('dashboard/activity/<int:days>/', dashboard_activity, name='dashboard_activity'),
    path('bookings/list/', bookings_list, name='bookings_list'),
    path('playgrounds/sports/', playgrounds_sports, name='api_playgrounds_sports'),
    path('playgrounds/facilities/', playgrounds_facilities, name='api_playgrounds_facilities'),
    path('notifications/count/', notifications_count, name='notifications_count'),
    
    # 📊 PLAYGROUND STATISTICS ENDPOINTS
    path('dashboard/playground-stats/<int:playground_id>/', playground_stats, name='playground_stats'),
    path('bookings/count/<int:playground_id>/', booking_count, name='booking_count'),
    
    # MISSING ENDPOINTS - FIXED TO PREVENT 404 ERRORS
    path('user/stats/', dashboard_data, name='user_stats'),  # Redirect to dashboard_data
    path('dashboard-stats/', dashboard_data, name='dashboard_stats'),  # Redirect to dashboard_data
    
    # 🎯 DYNAMIC FORM DATA API ENDPOINTS
    path('dynamic/countries/', dynamic_get_countries, name='dynamic_countries'),
    path('dynamic/states/', dynamic_get_states, name='dynamic_states'),
    path('dynamic/cities/', dynamic_get_cities, name='dynamic_cities'),
    path('dynamic/sport-types/', dynamic_get_sport_types, name='dynamic_sport_types'),
    path('dynamic/playground-types/', get_playground_types, name='dynamic_playground_types'),
    path('dynamic/form-data/', get_form_data, name='dynamic_form_data'),
    
    # 💾 DRAFT MANAGEMENT API ENDPOINTS
    path('drafts/save/', save_draft_playground, name='save_draft'),
    path('drafts/<int:draft_id>/load/', load_draft_playground, name='load_draft'),
    path('drafts/<int:draft_id>/delete/', delete_draft_playground, name='delete_draft'),
    
    # 💰 DYNAMIC CURRENCY API ENDPOINTS
    path('currency/', DynamicCurrencyAPI.as_view(), name='dynamic_currency_api'),
    path('currency/detect/', detect_user_currency, name='detect_user_currency'),
    
    # 🧮 BOOKING CALCULATION API ENDPOINTS
    path('booking-calculation/', BookingCalculationAPI.as_view(), name='booking_calculation'),
    
    # ⏰ DYNAMIC TIME SLOTS API ENDPOINTS
    path('time-slots/generate/', generate_dynamic_time_slots, name='generate_time_slots'),
    path('time-slots/generate-daywise/', generate_dynamic_time_slots, name='generate_daywise_time_slots'),
    path('time-slots/add-custom/', add_custom_slot, name='add_custom_slot'),
    path('time-slots/<str:slot_id>/delete/', add_custom_slot, name='delete_time_slot'),
    path('time-slots/availability/', get_playground_availability, name='playground_availability'),
    
    # 🎯 PROFESSIONAL CUSTOM SLOTS API ENDPOINTS  
    path('professional-slots/', professional_custom_slots_api, name='professional_custom_slots'),
    path('professional-slots/<int:playground_id>/', professional_custom_slots_api, name='professional_custom_slots_playground'),
    path('professional-slots/<int:slot_id>/', professional_custom_slots_api, name='professional_custom_slots_detail'),
    path('slot-types/', get_slot_types, name='get_slot_types'),
    path('currencies/', get_currencies, name='get_currencies'),
    
    # Dynamic Today's Slots API
    path('today-slots/<int:playground_id>/', get_today_slots, name='get_today_slots'),
    
    # Custom Slots API (alias for professional slots)
    path('custom-slots/<int:playground_id>/', professional_custom_slots_api, name='custom_slots_playground'),
    
    # 🎫 PROFESSIONAL MEMBERSHIP PASSES API ENDPOINTS
    path('membership-passes/', membership_passes_api, name='membership_passes_api'),
    path('membership-passes/<int:playground_id>/', membership_passes_api, name='membership_passes_playground'),
    path('membership-passes/<int:playground_id>/<int:pass_id>/', membership_passes_api, name='membership_passes_detail'),
    path('membership-passes/<int:pass_id>/purchase/', purchase_membership_pass, name='purchase_membership_pass'),
    
    # 🎫 PROFESSIONAL DURATION PASSES API ENDPOINTS
    path('duration-passes/', membership_passes_api, name='duration_passes_api'),
    path('duration-passes/<int:pass_id>/', membership_passes_api, name='duration_passes_detail'),
    path('duration-types/', get_duration_types, name='get_duration_types'),
    path('calculate-pricing/', calculate_pass_pricing, name='calculate_pass_pricing'),
    
    # 💾 TEMPORARY DATA MANAGEMENT API ENDPOINTS
    path('temporary-data/save/<int:playground_id>/', save_temporary_data_to_playground, name='save_temporary_data'),
    path('temporary-data/summary/', get_temporary_data_summary, name='temporary_data_summary'),
    path('temporary-data/clear/', clear_temporary_data, name='clear_temporary_data'),
    
    # Professional Media Gallery APIs
    path('media/upload-cover-images/', upload_cover_images, name='upload_cover_images'),
    path('media/upload-gallery-images/', upload_gallery_images, name='upload_gallery_images'),
    path('media/save-video-data/', save_video_data, name='save_video_data'),
    path('media/save-virtual-tour/', save_virtual_tour_data, name='save_virtual_tour_data'),
    path('media/get-data/', get_media_data, name='get_media_data'),
    path('media/get-data/<int:playground_id>/', get_media_data, name='get_media_data_with_id'),
    path('media/delete/<str:item_type>/<int:item_id>/', delete_media_item, name='delete_media_item'),
    path('media/sync-status/', sync_status, name='sync_status'),
    
    # ✅ MISSING MEDIA ENDPOINTS (Professional Implementation)
    path('media/get-cover-images/', get_media_data, name='get_cover_images'),
    path('media/get-gallery-images/', get_media_data, name='get_gallery_images'),
    path('load-draft-playground/', load_draft_playground, name='load_draft_playground'),
    path('load-draft-playground/<int:draft_id>/', load_draft_playground, name='load_draft_playground_with_id'),
]
