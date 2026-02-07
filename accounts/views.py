from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
# Function-based logout view
from django.urls import reverse
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, View, ListView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.views import LoginView
import json

from .models import User, UserProfile, PartnerApplication
# Import additional models for enhanced home page
from playgrounds.models import Playground, SportType, Country, State, City
from bookings.models import Booking

# Try to import notifications model, handle if it doesn't exist
try:
    from notifications.models import Notification
except ImportError:
    Notification = None

# Add Avg to existing import
from django.db.models import Q, Count, Sum, Avg

# User dashboard view for normal users with dynamic data
class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/user_dashboard.html'
    login_url = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect owners and admins to their respective dashboards"""
        if request.user.is_authenticated:
            if request.user.user_type == 'owner':
                from django.contrib import messages
                messages.info(request, 'You have been redirected to the Owner Dashboard.')
                return redirect('accounts:owner_dashboard')
            elif request.user.user_type == 'admin':
                from django.contrib import messages
                messages.info(request, 'You have been redirected to the Admin Panel.')
                return redirect('adminpanel:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's booking statistics
        user_bookings = Booking.objects.filter(user=user)
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # Calculate stats
        total_bookings = user_bookings.count()
        total_hours = user_bookings.aggregate(
            total=Sum('duration_hours')
        )['total'] or 0
        total_spent = user_bookings.filter(
            payment_status='paid'
        ).aggregate(
            total=Sum('final_amount')
        )['total'] or 0
        
        # Get favorite sport
        favorite_sport_data = user_bookings.values(
            'playground__sport_types__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        favorite_sport = favorite_sport_data['playground__sport_types__name'] if favorite_sport_data and favorite_sport_data['playground__sport_types__name'] else 'None'
        
        # Get upcoming bookings
        upcoming_bookings = user_bookings.filter(
            booking_date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('booking_date', 'start_time')[:5]
        
        # Get nearby playgrounds (assuming user has location or default to all)
        nearby_playgrounds = Playground.objects.filter(
            status='active'
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:6]
        
        context.update({
            'user': user,
            'total_bookings': total_bookings,
            'total_hours': float(total_hours),
            'total_spent': float(total_spent),
            'favorite_sport': favorite_sport,
            'upcoming_bookings': upcoming_bookings,
            'nearby_playgrounds': nearby_playgrounds,
        })
        
        return context
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
# Function-based logout view
from django.urls import reverse
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, View, ListView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.views import LoginView
import json

from .models import User, UserProfile, PartnerApplication
from .forms import CustomUserCreationForm, EmailAuthenticationForm, UserUpdateForm, PartnerApplicationForm
from playgrounds.models import Playground, City, Country, State
from bookings.models import Booking
from notifications.models import Notification


class CustomLoginView(LoginView):
    """Custom login view using email authentication"""
    form_class = EmailAuthenticationForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def dispatch(self, request, *args, **kwargs):
        # If user is already authenticated, redirect them
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'admin':
            return reverse('adminpanel:admin_dashboard')
        elif user.user_type == 'owner':
            return reverse('accounts:owner_dashboard')
        else:
            return reverse('accounts:dashboard')


class HomeView(TemplateView):
    """Enhanced landing page with featured playgrounds, search, and dynamic content"""
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured playgrounds with images and ratings
        featured_playgrounds = Playground.objects.filter(
            status='active', 
            is_featured=True
        ).select_related(
            'city__state__country', 'owner'
        ).prefetch_related(
            'sport_types', 'images'
        )[:8]
        
        context['featured_playgrounds'] = featured_playgrounds
        
        # Hero images from playgrounds with images (for dynamic hero slider)
        hero_playgrounds = Playground.objects.filter(
            status='active'
        ).prefetch_related('images').exclude(
            main_image=''
        )[:10]
        
        hero_images = []
        for pg in hero_playgrounds:
            if pg.main_image:
                hero_images.append(pg.main_image.url)
            elif pg.images.exists():
                first_img = pg.images.first()
                if first_img and first_img.image:
                    hero_images.append(first_img.image.url)
        
        # If no playground images, use defaults
        if not hero_images:
            hero_images = [
                'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=1280&h=720&fit=crop',
                'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1280&h=720&fit=crop',
                'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=1280&h=720&fit=crop',
                'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1280&h=720&fit=crop',
            ]
        
        context['hero_images'] = hero_images[:4]  # Limit to 4 hero images
        
        # All countries for search dropdown
        context['countries'] = Country.objects.filter(
            is_active=True,
            states__cities__playgrounds__status='active'
        ).distinct().order_by('name')
        
        # Popular sport types with playground counts
        context['sport_types'] = SportType.objects.filter(
            is_active=True,
            playgrounds__status='active'
        ).annotate(
            facilities_count=Count('playgrounds', distinct=True)
        ).distinct().order_by('-facilities_count')
        
        # Popular sports for display section
        context['popular_sports'] = SportType.objects.filter(
            is_active=True,
            playgrounds__status='active'
        ).annotate(
            facilities_count=Count('playgrounds', distinct=True)
        ).distinct().order_by('-facilities_count')[:12]
        
        # Available countries with playground counts for moving cards
        context['available_countries'] = Country.objects.filter(
            is_active=True,
            states__cities__playgrounds__status='active'
        ).annotate(
            playground_count=Count('states__cities__playgrounds', distinct=True)
        ).distinct().order_by('-playground_count')
        
        # Add popular cities for each country
        for country in context['available_countries']:
            country.popular_cities = City.objects.filter(
                state__country=country,
                playgrounds__status='active'
            ).annotate(
                playground_count=Count('playgrounds')
            ).order_by('-playground_count')[:5]
        
        # Statistics for counters
        context['total_users'] = User.objects.filter(user_type='user', is_active=True).count()
        context['total_playgrounds'] = Playground.objects.filter(status='active').count()
        context['total_bookings'] = Booking.objects.filter(status='completed').count()
        context['total_countries'] = Country.objects.filter(
            is_active=True,
            states__cities__playgrounds__status='active'
        ).distinct().count()
        
        # Today's date for minimum date validation
        context['today'] = timezone.now().date().isoformat()
        
        return context


class LoginView(View):
    """User login view using email authentication"""
    template_name = 'auth/login.html'
    
    def get(self, request):
        # Ensure CSRF cookie is set for AJAX
        from django.middleware.csrf import get_token
        get_token(request)
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        form = EmailAuthenticationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember_me = request.POST.get('remember_me')
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login_ip'])
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Welcome back, {user.first_name or user.email}!',
                    'redirect_url': user.get_dashboard_url()
                })
            else:
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                return redirect(user.get_dashboard_url())
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid email or password.'
                })
            else:
                # Don't add messages.error since form errors will be displayed
                return render(request, self.template_name, {'form': form})
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SignupView(View):
    """User registration view using email authentication"""
    template_name = 'auth/signup.html'
    
    def get(self, request):
        # Ensure CSRF cookie is set for AJAX
        from django.middleware.csrf import get_token
        get_token(request)
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        form = CustomUserCreationForm()
        context = {
            'form': form,
            'cities': City.objects.filter(is_active=True).select_related('state', 'state__country')
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            try:
                # Get city if provided
                city_id = request.POST.get('city')
                city = None
                if city_id:
                    city = City.objects.get(id=city_id)
                
                # Create user
                user = form.save(commit=False)
                user.city = city
                user.save()
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Account created successfully! Welcome to PlayGround Booking.',
                        'redirect_url': reverse('accounts:login')
                    })
                else:
                    # Login user for non-AJAX requests
                    login(request, user)
                    messages.success(request, 'Account created successfully! Welcome to PlayGround Booking.')
                    return redirect('accounts:dashboard')
                    
            except Exception as e:
                error_message = 'An error occurred while creating your account. Please try again.'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    })
                else:
                    messages.error(request, error_message)
        else:
            # Form has validation errors
            if is_ajax:
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = field_errors[0] if field_errors else ''
                
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': errors
                })
        
        # If form is invalid or error occurred (non-AJAX)
        context = {
            'form': form,
            'cities': City.objects.filter(is_active=True).select_related('state', 'state__country')
        }
        return render(request, self.template_name, context)
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            # Recent bookings - with error handling
            context['recent_bookings'] = Booking.objects.filter(
                user=user
            ).select_related('playground', 'playground__city').order_by('-created_at')[:5]
        except Exception:
            context['recent_bookings'] = []
        
        try:
            # Upcoming bookings - with error handling  
            context['upcoming_bookings'] = Booking.objects.filter(
                user=user,
                booking_date__gte=timezone.now().date(),
                status__in=['confirmed', 'pending']
            ).select_related('playground', 'playground__city').order_by('booking_date', 'start_time')[:5]
        except Exception:
            context['upcoming_bookings'] = []
        
        try:
            # Favorite playgrounds - with error handling
            context['favorite_playgrounds'] = user.favorites.select_related(
                'playground', 'playground__city'
            ).order_by('-created_at')[:6]
        except Exception:
            context['favorite_playgrounds'] = []
        
        # Basic user info (always available)
        context['user_info'] = {
            'name': user.get_full_name() or user.email,
            'email': user.email,
            'user_type': user.user_type,
            'date_joined': user.date_joined,
        }
        
        # Simple booking stats - with error handling
        try:
            context['booking_stats'] = {
                'total_bookings': Booking.objects.filter(user=user).count(),
                'completed_bookings': Booking.objects.filter(user=user, status='completed').count(),
                'pending_bookings': Booking.objects.filter(user=user, status='pending').count(),
                'total_spent': Booking.objects.filter(
                    user=user, 
                    status='completed', 
                    payment_status='paid'
                ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
            }
        except Exception:
            # If there's an error with bookings, show default stats
            context['booking_stats'] = {
                'total_bookings': 0,
                'completed_bookings': 0,
                'pending_bookings': 0,
                'total_spent': 0,
            }
        
        try:
            # Recent notifications - with error handling
            context['recent_notifications'] = Notification.objects.filter(
                recipient=user
            ).order_by('-created_at')[:5]
        except Exception:
            context['recent_notifications'] = []
        
        return context


class OwnerDashboardView(LoginRequiredMixin, TemplateView):
    """Enhanced Playground owner dashboard with comprehensive analytics and real-time data"""
    template_name = 'dashboard/owner_dashboard.html'
    login_url = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access the owner dashboard.')
            return redirect('accounts:login')
        if not hasattr(request.user, 'user_type') or request.user.user_type not in ['owner', 'admin']:
            messages.info(request, 'This dashboard is for playground owners only.')
            return redirect('accounts:dashboard')
        if request.user.user_type == 'admin':
            return redirect('adminpanel:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # For the dynamic dashboard, we only need basic context
        # The real data will be loaded via AJAX calls to our dynamic API
        context.update({
            'user': user,
        })
        
        return context
        
        # Quick actions data
        context['quick_stats'] = {
            'bookings_today': context['todays_bookings'].count(),
            'revenue_today': context['todays_bookings'].filter(
                status__in=['confirmed', 'completed'],
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
            'active_customers': all_bookings.filter(
                created_at__gte=today - timedelta(days=30)
            ).values('user').distinct().count(),
            'completion_rate': self.calculate_completion_rate(all_bookings),
        }
        
        # Add additional context for new template
        from django.db import models
        
        # Calculate monthly bookings and revenue
        current_month = timezone.now().replace(day=1)
        monthly_bookings = all_bookings.filter(created_at__gte=current_month)
        monthly_revenue = monthly_bookings.filter(
            status__in=['confirmed', 'completed']
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0
        
        # Get pending bookings with payment receipts
        pending_bookings = all_bookings.filter(
            status='pending'
        )
        
        context.update({
            'total_playgrounds': playgrounds.count(),
            'active_playgrounds': playgrounds.filter(status='approved').count(),
            'bookings_count': monthly_bookings.count(),
            'pending_approvals': pending_bookings.count(),
            'avg_rating': playgrounds.aggregate(avg=models.Avg('rating'))['avg'] or 0,
            'total_reviews': sum(pg.reviews.count() for pg in playgrounds) if playgrounds.exists() and hasattr(playgrounds.first(), 'reviews') else 0,
            'monthly_revenue': monthly_revenue,
            'playgrounds': playgrounds.annotate(
                bookings_count=models.Count('bookings')
            ),
            'pending_bookings_list': pending_bookings[:5],
            'todays_bookings': all_bookings.filter(booking_date=today).order_by('start_time')[:10],
        })
        
        return context
    
    def calculate_occupancy_rate(self, playgrounds, today):
        """Calculate average occupancy rate across all playgrounds"""
        total_slots = 0
        booked_slots = 0
        
        for playground in playgrounds:
            # Assuming 12 hours operation (8 AM to 8 PM)
            daily_slots = 12
            total_slots += daily_slots
            
            # Count today's bookings for this playground
            todays_bookings = playground.bookings.filter(
                booking_date=today,
                status__in=['confirmed', 'completed']
            ).count()
            
            booked_slots += todays_bookings
        
        return (booked_slots / total_slots * 100) if total_slots > 0 else 0
    
    def calculate_revenue_growth(self, user, current_month, current_year):
        """Calculate revenue growth compared to last month"""
        current_revenue = Booking.objects.filter(
            playground__owner=user,
            created_at__month=current_month,
            created_at__year=current_year,
            status__in=['confirmed', 'completed'],
            payment_status='paid'
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        # Previous month calculation
        if current_month == 1:
            prev_month, prev_year = 12, current_year - 1
        else:
            prev_month, prev_year = current_month - 1, current_year
        
        prev_revenue = Booking.objects.filter(
            playground__owner=user,
            created_at__month=prev_month,
            created_at__year=prev_year,
            status__in=['confirmed', 'completed'],
            payment_status='paid'
        ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        
        if prev_revenue > 0:
            growth = ((current_revenue - prev_revenue) / prev_revenue) * 100
            return round(growth, 1)
        return 0
    
    def calculate_completion_rate(self, bookings):
        """Calculate booking completion rate"""
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status='completed').count()
        
        return (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
    
    def get_weekly_booking_data(self, user, week_start, week_end):
        """Get daily booking data for the current week"""
        daily_data = []
        current_date = week_start
        
        while current_date <= week_end:
            bookings_count = Booking.objects.filter(
                playground__owner=user,
                booking_date=current_date
            ).count()
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.strftime('%a'),
                'bookings': bookings_count
            })
            current_date += timedelta(days=1)
        
        return daily_data
    
    def get_monthly_revenue_data(self, user, current_year):
        """Get monthly revenue data for the current year"""
        monthly_data = []
        
        for month in range(1, 13):
            revenue = Booking.objects.filter(
                playground__owner=user,
                created_at__month=month,
                created_at__year=current_year,
                status__in=['confirmed', 'completed'],
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            
            monthly_data.append({
                'month': month,
                'month_name': datetime(current_year, month, 1).strftime('%b'),
                'revenue': float(revenue)
            })
        
        return monthly_data


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """Admin dashboard with platform overview"""
    template_name = 'dashboard/admin_dashboard.html'
    login_url = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff and request.user.user_type != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Platform overview stats
        context['platform_stats'] = {
            'total_users': User.objects.filter(user_type='user').count(),
            'total_owners': User.objects.filter(user_type='owner').count(),
            'total_playgrounds': Playground.objects.count(),
            'active_playgrounds': Playground.objects.filter(status='active').count(),
            'pending_playgrounds': Playground.objects.filter(status='pending').count(),
            'total_bookings': Booking.objects.count(),
            'today_bookings': Booking.objects.filter(created_at__date=timezone.now().date()).count(),
            'total_revenue': Booking.objects.filter(
                status='completed', 
                payment_status='paid'
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0,
        }
        
        # Recent activities
        context['recent_users'] = User.objects.filter(
            user_type='user'
        ).order_by('-date_joined')[:5]
        
        context['recent_partner_applications'] = PartnerApplication.objects.filter(
            status='pending'
        ).select_related('user').order_by('-created_at')[:5]
        
        context['recent_playgrounds'] = Playground.objects.filter(
            status='pending'
        ).select_related('owner', 'city').order_by('-created_at')[:5]
        
        context['recent_bookings'] = Booking.objects.select_related(
            'user', 'playground'
        ).order_by('-created_at')[:10]
        
        return context


class BecomePartnerView(TemplateView):
    """Become partner information page"""
    template_name = 'pages/become_partner.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PartnerApplicationView(LoginRequiredMixin, View):
    """Partner application form"""
    template_name = 'forms/partner_application.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        # Check if user already has an application
        try:
            application = PartnerApplication.objects.get(user=request.user)
            return render(request, 'forms/application_status.html', {'application': application})
        except PartnerApplication.DoesNotExist:
            pass
        
        return render(request, self.template_name)
    
    def post(self, request):
        # Check if user already has an application
        if PartnerApplication.objects.filter(user=request.user).exists():
            messages.error(request, 'You have already submitted a partner application.')
            return redirect('accounts:partner_application')
        
        # Extract form data
        business_name = request.POST.get('business_name')
        business_address = request.POST.get('business_address')
        business_phone = request.POST.get('business_phone')
        business_email = request.POST.get('business_email')
        description = request.POST.get('description')
        experience_years = request.POST.get('experience_years', 0)
        business_license = request.FILES.get('business_license')
        
        # Validation
        if not all([business_name, business_address, business_phone, business_email, description]):
            messages.error(request, 'All required fields must be filled.')
            return render(request, self.template_name)
        
        try:
            experience_years = int(experience_years)
        except (ValueError, TypeError):
            experience_years = 0
        
        # Create application
        PartnerApplication.objects.create(
            user=request.user,
            business_name=business_name,
            business_address=business_address,
            business_phone=business_phone,
            business_email=business_email,
            description=description,
            experience_years=experience_years,
            business_license=business_license
        )
        
        messages.success(request, 'Your partner application has been submitted successfully! We will review it within 2-3 business days.')
        return redirect('accounts:partner_application')


# Static page views
class AboutView(TemplateView):
    template_name = 'pages/about.html'

class ContactView(TemplateView):
    template_name = 'pages/contact.html'

class HelpView(TemplateView):
    template_name = 'pages/help.html'

class FAQView(TemplateView):
    template_name = 'pages/faq.html'

class PrivacyView(TemplateView):
    template_name = 'pages/privacy.html'

class TermsView(TemplateView):
    template_name = 'pages/terms.html'

class RefundPolicyView(TemplateView):
    template_name = 'pages/refund_policy.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/profile.html'
    login_url = 'accounts:login'

class EditProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/edit_profile.html'
    login_url = 'accounts:login'

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/settings.html'
    login_url = 'accounts:login'

class NotificationSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/notification_settings.html'
    login_url = 'accounts:login'


class DashboardDataAPIView(LoginRequiredMixin, View):
    """API endpoint for dashboard data"""
    
    def get(self, request):
        try:
            user = request.user
            
            # Get dashboard data
            context = {
                'total_bookings': 0,
                'active_bookings': 0,
                'favorite_playgrounds': 0,
                'unread_notifications': 0,
                'upcoming_bookings': [],
                'recent_bookings': [],
                'recent_notifications': []
            }
            
            # Try to get booking data
            try:
                total_bookings = Booking.objects.filter(user=user).count()
                active_bookings = Booking.objects.filter(
                    user=user, 
                    date__gte=timezone.now().date(),
                    status__in=['confirmed', 'pending']
                ).count()
                
                context.update({
                    'total_bookings': total_bookings,
                    'active_bookings': active_bookings
                })
                
                # Get recent bookings
                recent_bookings = Booking.objects.filter(user=user).order_by('-created_at')[:5]
                context['recent_bookings'] = [
                    {
                        'id': booking.id,
                        'playground_name': booking.playground.name if booking.playground else 'Unknown',
                        'date': booking.date.strftime('%Y-%m-%d') if booking.date else '',
                        'status': booking.status,
                    }
                    for booking in recent_bookings
                ]
                
            except Exception as e:
                print(f"Error getting bookings: {e}")
            
            # Try to get notification data
            try:
                unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()
                context['unread_notifications'] = unread_notifications
                
                # Get recent notifications
                recent_notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]
                context['recent_notifications'] = [
                    {
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
                    }
                    for notification in recent_notifications
                ]
                
            except Exception as e:
                print(f"Error getting notifications: {e}")
            
            # Try to get favorite playgrounds
            try:
                if hasattr(user, 'userprofile'):
                    favorite_playgrounds = user.userprofile.favorite_playgrounds.count()
                    context['favorite_playgrounds'] = favorite_playgrounds
            except Exception as e:
                print(f"Error getting favorites: {e}")
            
            return JsonResponse({
                'success': True,
                'data': context
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@login_required
def bookings_list_api(request):
    """
    API view to get user's bookings with filtering, pagination, and real-time data
    """
    try:
        user = request.user
        page = int(request.GET.get('page', 1))
        status_filter = request.GET.get('status', '')
        time_filter = request.GET.get('time_filter', '')
        search = request.GET.get('search', '')
        tab = request.GET.get('tab', 'all')
        page_size = 10

        # Base queryset
        bookings = Booking.objects.filter(user=user).select_related('playground').order_by('-created_at')
        
        # Apply tab filter
        today = timezone.now().date()
        if tab == 'upcoming':
            bookings = bookings.filter(booking_date__gte=today, status__in=['pending', 'confirmed'])
        elif tab == 'completed':
            bookings = bookings.filter(status='completed')
        elif tab == 'cancelled':
            bookings = bookings.filter(status='cancelled')
        
        # Apply status filter
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        # Apply time filter
        if time_filter:
            if time_filter == 'upcoming':
                bookings = bookings.filter(booking_date__gte=today)
            elif time_filter == 'past':
                bookings = bookings.filter(booking_date__lt=today)
            elif time_filter == 'this_week':
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                bookings = bookings.filter(booking_date__range=[week_start, week_end])
            elif time_filter == 'this_month':
                bookings = bookings.filter(booking_date__year=today.year, booking_date__month=today.month)
            elif time_filter == 'last_month':
                last_month = today.replace(day=1) - timedelta(days=1)
                bookings = bookings.filter(booking_date__year=last_month.year, booking_date__month=last_month.month)
        
        # Apply search filter
        if search:
            bookings = bookings.filter(
                Q(playground__name__icontains=search) |
                Q(playground__sports__name__icontains=search) |
                Q(booking_id__icontains=search)
            )
        
        # Count totals before pagination
        total_count = Booking.objects.filter(user=user).count()
        filtered_count = bookings.count()
        
        # Pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_bookings = bookings[start_index:end_index]
        
        # Calculate pagination info
        total_pages = (filtered_count + page_size - 1) // page_size
        has_previous = page > 1
        has_next = page < total_pages
        
        # Format bookings data
        bookings_data = []
        for booking in paginated_bookings:
            # Determine available actions
            can_cancel = booking.status in ['pending', 'confirmed'] and booking.booking_date >= today
            can_reschedule = booking.status in ['pending', 'confirmed'] and booking.booking_date >= today
            can_review = booking.status == 'completed' and not hasattr(booking, 'review')
            
            bookings_data.append({
                'id': booking.id,
                'booking_id': str(booking.booking_id)[:8].upper(),
                'playground_name': booking.playground.name,
                'sport': booking.playground.sports.first().name if booking.playground.sports.exists() else 'General',
                'location': f"{booking.playground.city.name}, {booking.playground.state.name}" if booking.playground.city else booking.playground.address,
                'booking_date': booking.booking_date.strftime('%b %d, %Y'),
                'start_time': booking.start_time.strftime('%I:%M %p'),
                'end_time': booking.end_time.strftime('%I:%M %p'),
                'duration': float(booking.duration_hours),
                'final_amount': float(booking.final_amount),
                'status': booking.status,
                'payment_status': booking.payment_status,
                'created_at': booking.created_at.strftime('%b %d, %Y'),
                'can_cancel': can_cancel,
                'can_reschedule': can_reschedule,
                'can_review': can_review
            })
        
        # Calculate statistics
        all_bookings = Booking.objects.filter(user=user)
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        stats = {
            'total_bookings': all_bookings.count(),
            'upcoming': all_bookings.filter(booking_date__gte=today, status__in=['pending', 'confirmed']).count(),
            'completed': all_bookings.filter(status='completed').count(),
            'total_spent': float(all_bookings.filter(payment_status='paid').aggregate(Sum('final_amount'))['final_amount__sum'] or 0),
            'spent_this_month': float(all_bookings.filter(
                payment_status='paid',
                booking_date__gte=this_month
            ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0),
            'bookings_change': 0  # Calculate percentage change if needed
        }
        
        # Calculate bookings change percentage
        this_month_count = all_bookings.filter(booking_date__gte=this_month).count()
        last_month_count = all_bookings.filter(
            booking_date__gte=last_month,
            booking_date__lt=this_month
        ).count()
        
        if last_month_count > 0:
            stats['bookings_change'] = round(((this_month_count - last_month_count) / last_month_count) * 100, 1)
        
        return JsonResponse({
            'success': True,
            'bookings': bookings_data,
            'stats': stats,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'has_previous': has_previous,
                'has_next': has_next,
                'start_index': start_index + 1 if bookings_data else 0,
                'end_index': start_index + len(bookings_data),
                'total_count': filtered_count,
                'start_page': max(1, page - 2),
                'end_page': min(total_pages, page + 2)
            },
            'total_count': total_count,
            'filtered_count': filtered_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
