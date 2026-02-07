from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Main booking dashboard and views
    path('', views.booking_dashboard, name='booking_dashboard'),
    path('dashboard/', views.booking_dashboard, name='booking_dashboard_alt'),
    path('checkout/<int:playground_id>/', views.checkout, name='checkout'),
    path('test-checkout/<int:playground_id>/', views.test_checkout, name='test_checkout'),  # NO LOGIN REQUIRED
    path('create/<int:playground_id>/', views.create_booking, name='create_booking'),
    path('<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/', views.booking_detail_by_id, name='booking_detail_by_id'),
    path('history/', views.booking_history, name='booking_history'),
    
    # Booking actions (UUID-based)
    path('cancel/<uuid:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('reschedule/<uuid:booking_id>/', views.reschedule_booking, name='reschedule_booking'),
    path('upload-receipt/<uuid:booking_id>/', views.upload_payment_receipt, name='upload_receipt'),
    
    # Booking actions (Integer ID-based for compatibility)
    path('cancel-id/<int:booking_id>/', views.cancel_booking_by_id, name='cancel_booking_by_id'),
    path('reschedule-id/<int:booking_id>/', views.reschedule_booking_by_id, name='reschedule_booking_by_id'),
    
    # API endpoints for real-time functionality
    path('api/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('api/booking-stats/', views.get_booking_stats, name='get_booking_stats'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
    path('api/payment-page/<int:playground_id>/', views.get_payment_page, name='get_payment_page'),
    path('api/create-booking/', views.create_booking_api, name='create_booking_api'),
    
    # Legacy booking process (for compatibility)
    path('book/<int:playground_id>/', views.BookPlaygroundView.as_view(), name='book_playground'),
    path('create/<int:playground_id>/', views.create_booking, name='create_booking_with_id'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail_legacy'),
    path('confirm/<uuid:booking_id>/', views.ConfirmBookingView.as_view(), name='confirm_booking'),
    path('payment/<uuid:booking_id>/', views.PaymentView.as_view(), name='payment'),
    # path('success/<uuid:booking_id>/', views.BookingSuccessView.as_view(), name='booking_success'), # Removed - using dynamic success flow
    
    # User bookings (legacy)
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('details/<uuid:booking_id>/', views.BookingDetailView.as_view(), name='booking_detail_legacy_alt'),
    path('cancel-legacy/<uuid:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking_legacy'),
    
    # Reviews
    path('review/<uuid:booking_id>/', views.AddReviewView.as_view(), name='add_review'),
    
    # AJAX endpoints (legacy)
    path('ajax/get-time-slots/', views.get_time_slots, name='ajax_get_time_slots'),
    path('ajax/calculate-price/', views.calculate_price, name='ajax_calculate_price'),
]
