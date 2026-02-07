from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from accounts.models import User
from playgrounds.models import Playground, SportType
from bookings.models import Booking
from notifications.models import Notification


class DashboardDataAPIView(View):
    """
    Real-time dashboard data API providing dynamic data for owner dashboard
    """
    
    def get(self, request):
        user = request.user
        if not user.is_authenticated or user.user_type != 'owner':
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        # Get all user's playgrounds
        user_playgrounds = Playground.objects.filter(owner=user)
        
        # Calculate date ranges
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        # Get real-time financial metrics
        financial_data = self.get_financial_metrics(user_playgrounds, today, week_start, month_start)
        
        # Get booking analytics
        booking_data = self.get_booking_analytics(user_playgrounds, today, week_start, month_start)
        
        # Get playground performance
        playground_data = self.get_playground_performance(user_playgrounds)
        
        # Get recent activities
        activities = self.get_recent_activities(user, user_playgrounds)
        
        # Get chart data
        revenue_chart = self.get_revenue_chart_data(user_playgrounds, 30)  # Last 30 days
        booking_chart = self.get_booking_chart_data(user_playgrounds, 30)
        
        # Get notifications
        notifications = self.get_notifications(user)
        
        return JsonResponse({
            'financial': financial_data,
            'bookings': booking_data,
            'playgrounds': playground_data,
            'activities': activities,
            'charts': {
                'revenue': revenue_chart,
                'bookings': booking_chart
            },
            'notifications': notifications,
            'last_updated': timezone.now().isoformat(),
            'user_info': {
                'email': user.email,
                'name': user.get_full_name(),
                'total_playgrounds': user_playgrounds.count()
            }
        })
    
    def get_financial_metrics(self, playgrounds, today, week_start, month_start):
        """Calculate real-time financial metrics"""
        
        # Current month revenue
        current_month_revenue = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=month_start,
            booking_date__lte=today,
            payment_status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
        
        # Previous month for comparison
        prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
        prev_month_end = month_start - timedelta(days=1)
        prev_month_revenue = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=prev_month_start,
            booking_date__lte=prev_month_end,
            payment_status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
        
        # Calculate growth percentage
        if prev_month_revenue > 0:
            growth_percentage = ((current_month_revenue - prev_month_revenue) / prev_month_revenue) * 100
        else:
            growth_percentage = 100 if current_month_revenue > 0 else 0
        
        # Today's revenue
        today_revenue = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date=today,
            payment_status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
        
        # This week's revenue
        week_revenue = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=week_start,
            booking_date__lte=today,
            payment_status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
        
        # Average revenue per booking
        avg_booking_value = Booking.objects.filter(
            playground__in=playgrounds,
            payment_status='paid'
        ).aggregate(avg=Avg('final_amount'))['avg'] or Decimal('0')
        
        # Pending payments
        pending_payments = Booking.objects.filter(
            playground__in=playgrounds,
            payment_status='pending'
        ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
        
        return {
            'current_month_revenue': float(current_month_revenue),
            'previous_month_revenue': float(prev_month_revenue),
            'growth_percentage': round(float(growth_percentage), 2),
            'today_revenue': float(today_revenue),
            'week_revenue': float(week_revenue),
            'average_booking_value': float(avg_booking_value),
            'pending_payments': float(pending_payments),
            'currency': 'USD'
        }
    
    def get_booking_analytics(self, playgrounds, today, week_start, month_start):
        """Get real-time booking analytics"""
        
        # Total bookings this month
        month_bookings = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=month_start,
            booking_date__lte=today
        ).count()
        
        # Today's bookings
        today_bookings = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date=today
        ).count()
        
        # Pending bookings
        pending_bookings = Booking.objects.filter(
            playground__in=playgrounds,
            status='pending'
        ).count()
        
        # Confirmed bookings for today
        confirmed_today = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date=today,
            status='confirmed'
        ).count()
        
        # Upcoming bookings (next 7 days)
        upcoming_bookings = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=today,
            booking_date__lte=today + timedelta(days=7),
            status__in=['confirmed', 'pending']
        ).count()
        
        # Cancellation rate
        total_bookings = Booking.objects.filter(playground__in=playgrounds).count()
        cancelled_bookings = Booking.objects.filter(playground__in=playgrounds, status='cancelled').count()
        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Average occupancy rate
        total_slots = playgrounds.count() * 24 * 30  # Simplified calculation
        booked_slots = month_bookings
        occupancy_rate = (booked_slots / total_slots * 100) if total_slots > 0 else 0
        
        return {
            'month_bookings': month_bookings,
            'today_bookings': today_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_today': confirmed_today,
            'upcoming_bookings': upcoming_bookings,
            'cancellation_rate': round(cancellation_rate, 2),
            'occupancy_rate': round(occupancy_rate, 2)
        }
    
    def get_playground_performance(self, playgrounds):
        """Get individual playground performance metrics"""
        
        playground_stats = []
        
        for playground in playgrounds:
            # Get bookings for this playground
            total_bookings = playground.bookings.count()
            confirmed_bookings = playground.bookings.filter(status='confirmed').count()
            
            # Revenue from this playground
            total_revenue = playground.bookings.filter(
                payment_status='paid'
            ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
            
            # Average rating
            avg_rating = playground.bookings.filter(
                user_rating__isnull=False
            ).aggregate(avg=Avg('user_rating'))['avg'] or 0
            
            # Recent booking count (last 7 days)
            recent_bookings = playground.bookings.filter(
                booking_date__gte=timezone.now().date() - timedelta(days=7)
            ).count()
            
            playground_stats.append({
                'id': playground.id,
                'name': playground.name,
                'sport_types': [sport.name for sport in playground.sport_types.all()],
                'status': playground.status,
                'total_bookings': total_bookings,
                'confirmed_bookings': confirmed_bookings,
                'total_revenue': float(total_revenue),
                'average_rating': round(float(avg_rating), 1) if avg_rating else 0,
                'recent_bookings': recent_bookings,
                'price_per_hour': float(playground.price_per_hour),
                'city': playground.city.name if playground.city else '',
                'is_featured': playground.is_featured,
                'created_at': playground.created_at.isoformat()
            })
        
        return playground_stats
    
    def get_recent_activities(self, user, playgrounds):
        """Get recent activities and notifications"""
        
        activities = []
        
        # Recent bookings
        recent_bookings = Booking.objects.filter(
            playground__in=playgrounds
        ).order_by('-created_at')[:10]
        
        for booking in recent_bookings:
            activities.append({
                'type': 'booking',
                'title': f"New booking for {booking.playground.name}",
                'description': f"Booking by {booking.user.get_full_name()} for {booking.booking_date}",
                'timestamp': booking.created_at.isoformat(),
                'status': booking.status,
                'amount': float(booking.final_amount) if booking.final_amount else 0,
                'playground': booking.playground.name,
                'user': booking.user.get_full_name()
            })
        
        # Recent playground updates
        recent_playgrounds = playgrounds.order_by('-updated_at')[:5]
        for playground in recent_playgrounds:
            activities.append({
                'type': 'playground_update',
                'title': f"Playground updated: {playground.name}",
                'description': f"Status: {playground.get_status_display()}",
                'timestamp': playground.updated_at.isoformat(),
                'status': playground.status,
                'playground': playground.name
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activities[:15]  # Return latest 15 activities
    
    def get_revenue_chart_data(self, playgrounds, days=30):
        """Generate revenue chart data for the last N days"""
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get daily revenue data
        daily_revenue = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=start_date,
            booking_date__lte=end_date,
            payment_status='paid'
        ).values('booking_date').annotate(
            revenue=Sum('final_amount')
        ).order_by('booking_date')
        
        # Create a complete date range
        date_range = []
        revenue_data = []
        
        current_date = start_date
        revenue_dict = {item['booking_date']: float(item['revenue']) for item in daily_revenue}
        
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            revenue_data.append(revenue_dict.get(current_date, 0))
            current_date += timedelta(days=1)
        
        return {
            'labels': date_range,
            'revenue': revenue_data,
            'total': sum(revenue_data),
            'average': sum(revenue_data) / len(revenue_data) if revenue_data else 0
        }
    
    def get_booking_chart_data(self, playgrounds, days=30):
        """Generate booking chart data for the last N days"""
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get daily booking counts
        daily_bookings = Booking.objects.filter(
            playground__in=playgrounds,
            booking_date__gte=start_date,
            booking_date__lte=end_date
        ).values('booking_date').annotate(
            count=Count('id')
        ).order_by('booking_date')
        
        # Create complete date range
        date_range = []
        booking_data = []
        
        current_date = start_date
        booking_dict = {item['booking_date']: item['count'] for item in daily_bookings}
        
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            booking_data.append(booking_dict.get(current_date, 0))
            current_date += timedelta(days=1)
        
        return {
            'labels': date_range,
            'bookings': booking_data,
            'total': sum(booking_data),
            'average': sum(booking_data) / len(booking_data) if booking_data else 0
        }
    
    def get_notifications(self, user):
        """Get user notifications"""
        
        try:
            recent_notifications = Notification.objects.filter(
                user=user
            ).order_by('-created_at')[:10]
            
            notifications = []
            for notification in recent_notifications:
                notifications.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat()
                })
            
            return notifications
        except:
            # If notifications model doesn't exist, return empty list
            return []


class PlaygroundListAPIView(View):
    """API for real-time playground data"""
    
    def get(self, request):
        user = request.user
        if not user.is_authenticated or user.user_type != 'owner':
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        playgrounds = Playground.objects.filter(owner=user).select_related('city__state__country')
        
        playground_data = []
        for playground in playgrounds:
            # Calculate real-time metrics
            total_bookings = playground.bookings.count()
            active_bookings = playground.bookings.filter(
                booking_date=timezone.now().date(),
                status__in=['confirmed', 'pending']
            ).count()
            
            monthly_revenue = playground.bookings.filter(
                booking_date__gte=timezone.now().date().replace(day=1),
                payment_status='paid'
            ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0')
            
            playground_data.append({
                'id': playground.id,
                'name': playground.name,
                'sport_types': [sport.name for sport in playground.sport_types.all()],
                'status': playground.status,
                'city': playground.city.name if playground.city else '',
                'price_per_hour': float(playground.price_per_hour),
                'capacity': playground.capacity,
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'monthly_revenue': float(monthly_revenue),
                'rating': float(playground.rating),
                'is_featured': playground.is_featured,
                'is_verified': playground.is_verified,
                'created_at': playground.created_at.isoformat()
            })
        
        return JsonResponse({
            'playgrounds': playground_data,
            'total_count': len(playground_data),
            'last_updated': timezone.now().isoformat()
        })


class BookingRequestsAPIView(View):
    """API for real-time booking requests"""
    
    def get(self, request):
        user = request.user
        if not user.is_authenticated or user.user_type != 'owner':
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        user_playgrounds = Playground.objects.filter(owner=user)
        
        # Get booking requests with filters
        status_filter = request.GET.get('status', 'all')
        date_filter = request.GET.get('date', 'all')
        
        bookings = Booking.objects.filter(playground__in=user_playgrounds)
        
        if status_filter != 'all':
            bookings = bookings.filter(status=status_filter)
        
        if date_filter == 'today':
            bookings = bookings.filter(booking_date=timezone.now().date())
        elif date_filter == 'upcoming':
            bookings = bookings.filter(booking_date__gte=timezone.now().date())
        
        bookings = bookings.order_by('-created_at')[:50]  # Limit to 50 recent bookings
        
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'id': str(booking.booking_id),
                'user_name': booking.user.get_full_name(),
                'user_email': booking.user.email,
                'playground_name': booking.playground.name,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'duration_hours': float(booking.duration_hours),
                'final_amount': float(booking.final_amount),
                'status': booking.status,
                'payment_status': booking.payment_status,
                'contact_phone': booking.contact_phone,
                'special_requests': booking.special_requests,
                'created_at': booking.created_at.isoformat(),
                'is_upcoming': booking.is_upcoming,
                'is_past': booking.is_past
            })
        
        return JsonResponse({
            'bookings': booking_data,
            'total_count': len(booking_data),
            'last_updated': timezone.now().isoformat()
        })
