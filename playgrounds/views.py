from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, View
from django.db.models import Q, Avg, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.conf import settings
from .models import Playground, SportType, Country, State, City, PlaygroundImage
from api.currency_api import DynamicCurrencyAPI

# Create your views here.

class PlaygroundListView(ListView):
    model = Playground
    template_name = 'playground/list.html'
    context_object_name = 'playgrounds'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Playground.objects.filter(status='active').select_related(
            'city__state__country', 'owner'
        ).prefetch_related('sport_types', 'images')
        
        # Apply filters
        sport_id = self.request.GET.get('sport')
        country_id = self.request.GET.get('country')
        state_id = self.request.GET.get('state')
        city_id = self.request.GET.get('city')
        price_range = self.request.GET.get('price')
        search_query = self.request.GET.get('q')
        
        if sport_id:
            queryset = queryset.filter(sport_types__id=sport_id)
        
        if country_id:
            queryset = queryset.filter(city__state__country_id=country_id)
        
        if state_id:
            queryset = queryset.filter(city__state_id=state_id)
        
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        
        if price_range:
            if price_range == '0-25':
                queryset = queryset.filter(price_per_hour__lte=25)
            elif price_range == '25-50':
                queryset = queryset.filter(price_per_hour__gte=25, price_per_hour__lte=50)
            elif price_range == '50-100':
                queryset = queryset.filter(price_per_hour__gte=50, price_per_hour__lte=100)
            elif price_range == '100+':
                queryset = queryset.filter(price_per_hour__gte=100)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(city__name__icontains=search_query) |
                Q(city__state__name__icontains=search_query) |
                Q(city__state__country__name__icontains=search_query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sport_types'] = SportType.objects.filter(is_active=True)
        context['countries'] = Country.objects.filter(is_active=True)
        
        # Add currency information for each playground
        currency_api = DynamicCurrencyAPI()
        playgrounds_with_currency = []
        
        for playground in context['playgrounds']:
            # Get currency based on playground's country
            country_name = playground.city.state.country.name.lower()
            currency_code = self._get_currency_code_for_country(country_name)
            currency_data = currency_api.CURRENCY_DATABASE.get(currency_code, currency_api.CURRENCY_DATABASE['USD'])
            
            # Add currency info to playground object
            playground.currency = {
                'code': currency_code,
                'symbol': currency_data['symbol'],
                'name': currency_data['name'],
                'decimal_places': currency_data['decimal_places']
            }
            playgrounds_with_currency.append(playground)
        
        context['playgrounds'] = playgrounds_with_currency
        
        # Preserve filter values with names for display
        state_id = self.request.GET.get('state', '')
        city_id = self.request.GET.get('city', '')
        
        state_name = ''
        city_name = ''
        
        if state_id:
            try:
                state = State.objects.get(id=state_id)
                state_name = state.name
            except State.DoesNotExist:
                pass
        
        if city_id:
            try:
                city = City.objects.get(id=city_id)
                city_name = city.name
            except City.DoesNotExist:
                pass
        
        context['current_filters'] = {
            'sport': self.request.GET.get('sport', ''),
            'country': self.request.GET.get('country', ''),
            'state': state_id,
            'state_name': state_name,
            'city': city_id,
            'city_name': city_name,
            'price': self.request.GET.get('price', ''),
            'q': self.request.GET.get('q', ''),
        }
        
        return context
    
    def _get_currency_code_for_country(self, country_name):
        """Map country names to currency codes"""
        country_currency_map = {
            'malaysia': 'MYR',
            'singapore': 'SGD', 
            'indonesia': 'IDR',
            'thailand': 'THB',
            'united states': 'USD',
            'usa': 'USD',
            'united kingdom': 'GBP',
            'uk': 'GBP',
            'britain': 'GBP',
            'england': 'GBP',
            'canada': 'CAD',
            'australia': 'AUD',
            'india': 'INR',
            'bangladesh': 'BDT',
            'china': 'CNY',
            'japan': 'JPY',
            'south korea': 'KRW',
            'korea': 'KRW',
            'pakistan': 'PKR',
            'philippines': 'PHP',
            'vietnam': 'VND',
            'brazil': 'BRL',
            'mexico': 'MXN',
            'russia': 'RUB',
            'turkey': 'TRY',
            'egypt': 'EGP',
            'south africa': 'ZAR',
            'switzerland': 'CHF',
            'sweden': 'SEK',
            'norway': 'NOK',
            'denmark': 'DKK',
            'euro': 'EUR',
            'germany': 'EUR',
            'france': 'EUR',
            'italy': 'EUR',
            'spain': 'EUR',
            'netherlands': 'EUR',
            'belgium': 'EUR',
            'austria': 'EUR',
            'portugal': 'EUR',
            'ireland': 'EUR',
            'finland': 'EUR',
            'greece': 'EUR'
        }
        return country_currency_map.get(country_name, 'USD')

class PlaygroundSearchView(TemplateView):
    template_name = 'playground/search.html'

class PlaygroundDetailView(TemplateView):
    template_name = 'playground/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playground_id = kwargs.get('pk')
        
        try:
            # Get the playground with all related data
            playground = Playground.objects.select_related(
                'city__state__country', 'owner'
            ).prefetch_related(
                'sport_types', 'images', 'custom_slots', 'time_slots', 'playground_amenities', 'duration_passes'
            ).get(id=playground_id)
            
            context['playground'] = playground
            context['today'] = timezone.now().date()
            context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
            
            # Add JavaScript-safe playground data
            context['playground_data'] = json.dumps({
                'id': playground.id,
                'phoneNumber': playground.phone_number,
                'exists': True
            })
            
            # Remove static slots - using dynamic slots from database
            # Dynamic slots are now handled in template through playground.custom_slots.all and playground.time_slots.all
            context['available_slots'] = []  # Empty as we're using dynamic data
            
        except Playground.DoesNotExist:
            context['playground'] = None
            context['available_slots'] = []
            context['today'] = timezone.now().date()
            
            # Add JavaScript-safe playground data for non-existent playground
            context['playground_data'] = json.dumps({
                'id': None,
                'phoneNumber': None,
                'exists': False
            })
            
        return context

class MyPlaygroundsView(LoginRequiredMixin, TemplateView):
    template_name = 'playground/my_playgrounds.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get playgrounds owned by the current user
        context['playgrounds'] = Playground.objects.filter(owner=self.request.user).order_by('-created_at')
        return context

class AddPlaygroundView(LoginRequiredMixin, View):
    template_name = 'playground/add.html'
    
    def get(self, request):
        context = {
            'sport_types': SportType.objects.filter(is_active=True),
            'countries': Country.objects.filter(is_active=True),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        try:
            # Debug: Print form data
            print("Enhanced form data received:")
            for key, value in request.POST.items():
                print(f"  {key}: {value}")
            
            # Get selected city from the new dropdown system
            city_id = request.POST.get('city')
            selected_city = None
            
            if city_id:
                try:
                    selected_city = City.objects.get(id=city_id)
                except City.DoesNotExist:
                    pass
            
            # Fallback to default city if not selected
            if not selected_city:
                default_city = City.objects.filter(name__icontains='New York').first()
                if not default_city:
                    default_city = City.objects.first()
                selected_city = default_city
            
            if not selected_city:
                messages.error(request, 'No cities available. Please contact administrator.')
                return redirect('playgrounds:add_playground')
            
            # Get playground type from the new radio buttons
            playground_type = request.POST.get('playground_type', 'outdoor')
            if playground_type not in ['indoor', 'outdoor', 'hybrid']:
                playground_type = 'outdoor'
            
            # Create enhanced playground instance
            playground = Playground(
                owner=request.user,
                name=request.POST.get('name', '').strip(),
                description=request.POST.get('description', '').strip(),
                capacity=int(request.POST.get('capacity', 0)),
                price_per_hour=float(request.POST.get('price_per_hour', 0)),
                address=request.POST.get('address', '').strip(),
                city=selected_city,
                playground_type=playground_type,
                status='pending',  # Set to pending approval for admin review
                # Enhanced fields
                phone_number=request.POST.get('contact_phone', '').strip(),
                google_maps_url=request.POST.get('google_maps_url', '').strip()
            )
            
            # Validate required fields
            if not playground.name:
                messages.error(request, 'Playground name is required.')
                return redirect('playgrounds:add_playground')
            
            if not playground.description:
                messages.error(request, 'Description is required.')
                return redirect('playgrounds:add_playground')
            
            if playground.capacity <= 0:
                messages.error(request, 'Capacity must be greater than 0.')
                return redirect('playgrounds:add_playground')
            
            if playground.price_per_hour <= 0:
                messages.error(request, 'Price per hour must be greater than 0.')
                return redirect('playgrounds:add_playground')
            
            if not playground.address:
                messages.error(request, 'Address is required.')
                return redirect('playgrounds:add_playground')
            
            # Handle sport types (multiple selection)
            sport_type_ids = request.POST.getlist('sport_types')
            if not sport_type_ids:
                messages.error(request, 'Please select at least one sport type.')
                return redirect('playgrounds:add_playground')
            
            # Handle operating hours
            opening_time = request.POST.get('opening_time', '06:00')
            closing_time = request.POST.get('closing_time', '22:00')
            
            # Store operating hours in the operating_hours JSON field
            operating_hours = {}
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                operating_hours[day] = {
                    'opening_time': opening_time,
                    'closing_time': closing_time,
                    'is_open': True
                }
            playground.operating_hours = operating_hours
            
            # Handle amenities/facilities
            amenities = request.POST.getlist('amenities')
            playground.amenities = amenities if amenities else []
            
            # Generate time slots based on operating hours
            slot_templates = []
            if opening_time and closing_time:
                from datetime import datetime, timedelta
                
                start_time = datetime.strptime(opening_time, '%H:%M')
                end_time = datetime.strptime(closing_time, '%H:%M')
                
                current_time = start_time
                while current_time < end_time:
                    next_time = current_time + timedelta(hours=1)
                    if next_time <= end_time:
                        slot_templates.append({
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': next_time.strftime('%H:%M'),
                            'price': float(playground.price_per_hour),
                            'available': True
                        })
                    current_time = next_time
            
            playground.slot_templates = slot_templates
            
            # Save playground first
            playground.save()
            
            # Handle sport types (many-to-many relationship)
            if sport_type_ids:
                sport_types = SportType.objects.filter(id__in=sport_type_ids)
                playground.sport_types.set(sport_types)
            
            # Generate actual database records for time slots
            self.generate_time_slots_for_playground(playground)
            
            # Convert temporary session data to actual database records
            self.save_temporary_data_to_playground(request, playground)
            
            # Handle image uploads
            uploaded_images = request.FILES.getlist('images')
            for index, image_file in enumerate(uploaded_images):
                playground_image = PlaygroundImage(
                    playground=playground,
                    image=image_file,
                    is_primary=(index == 0)  # First image is primary
                )
                playground_image.save()
            
            # Set main image if images were uploaded
            if uploaded_images:
                playground.main_image = playground.images.filter(is_primary=True).first().image
                playground.save()
            
            print(f"Playground created successfully: {playground.name}")
            messages.success(request, f'Playground "{playground.name}" has been created and is pending approval!')
            
            # Redirect to dashboard
            return redirect('accounts:dashboard')
            
        except ValueError as e:
            print(f"ValueError in playground creation: {e}")
            messages.error(request, 'Invalid data provided. Please check your inputs.')
            return redirect('playgrounds:add_playground')
        except Exception as e:
            print(f"Error creating playground: {e}")
            messages.error(request, 'An error occurred while creating the playground. Please try again.')
            return redirect('playgrounds:add_playground')
            
            if contact_phone:
                playground.phone_number = contact_phone
            if contact_email:
                # Store in payment_methods or create a separate field
                playground.payment_methods = playground.payment_methods or {}
                playground.payment_methods['contact_email'] = contact_email
            
            # Save the playground
            playground.save()
            
            # Handle facilities
            facilities = request.POST.getlist('facilities')
            if facilities:
                playground.amenities = facilities
                playground.save()
            
            # Handle time slots
            time_slots = request.POST.getlist('time_slots')
            if time_slots:
                playground.slot_templates = time_slots
                playground.save()
            
            # Handle file uploads (main images)
            main_images = request.FILES.getlist('images')
            for i, image_file in enumerate(main_images):
                if i == 0:  # First image as main image
                    playground.main_image = image_file
                    playground.save()
                
                # Create PlaygroundImage for all images
                PlaygroundImage.objects.create(
                    playground=playground,
                    image=image_file,
                    is_primary=(i == 0)
                )
            
            # Handle gallery images
            gallery_images = request.FILES.getlist('additional_images')
            for image_file in gallery_images:
                PlaygroundImage.objects.create(
                    playground=playground,
                    image=image_file,
                    is_primary=False
                )
            
            messages.success(request, f'🎉 Playground "{playground.name}" has been successfully submitted for admin approval! You will be notified once it\'s reviewed.')
            
            # Log the creation for debugging
            print(f"Playground created: {playground.name} (ID: {playground.id}) by user {request.user.username}")
            
            return redirect('accounts:dashboard')  # Redirect to user dashboard
            
        except ValueError as e:
            messages.error(request, f'Invalid input: Please check your numeric values.')
            return redirect('playgrounds:add_playground')
        except Exception as e:
            messages.error(request, f'An error occurred while creating your playground. Please try again.')
            return redirect('playgrounds:add_playground')

    def generate_time_slots_for_playground(self, playground):
        """Generate TimeSlot database records based on operating hours"""
        try:
            from .models import TimeSlot
            from datetime import datetime, timedelta, date
            
            print(f"Starting slot generation for playground: {playground.name}")
            operating_hours = playground.operating_hours or {}
            print(f"Operating hours: {operating_hours}")
            
            if not operating_hours:
                print("No operating hours found, cannot generate slots")
                return
            
            slots_created = 0
            
            for day, hours in operating_hours.items():
                print(f"Processing day: {day}, hours: {hours}")
                
                if hours.get('is_open', True) and hours.get('opening_time') and hours.get('closing_time'):
                    try:
                        start_time = datetime.strptime(hours['opening_time'], '%H:%M').time()
                        end_time = datetime.strptime(hours['closing_time'], '%H:%M').time()
                        
                        print(f"  {day}: {start_time} - {end_time}")
                        
                        # Generate hourly slots
                        current_time = datetime.combine(date.today(), start_time)
                        end_datetime = datetime.combine(date.today(), end_time)
                        
                        if end_datetime <= current_time:  # Next day closing
                            end_datetime += timedelta(days=1)
                        
                        while current_time < end_datetime:
                            slot_end = current_time + timedelta(hours=1)
                            
                            # Don't create slot if it goes beyond closing time
                            if slot_end > end_datetime:
                                break
                            
                            time_slot, created = TimeSlot.objects.get_or_create(
                                playground=playground,
                                day_of_week=day,
                                start_time=current_time.time(),
                                end_time=slot_end.time(),
                                defaults={
                                    'price': playground.price_per_hour,
                                    'is_available': True,
                                    'max_bookings': 1
                                }
                            )
                            
                            if created:
                                slots_created += 1
                                print(f"    Created slot: {current_time.time()} - {slot_end.time()}")
                            
                            current_time = slot_end
                            
                    except Exception as day_error:
                        print(f"Error processing day {day}: {day_error}")
                        continue
                        
            print(f"Generated {slots_created} time slots for playground: {playground.name}")
            
            # Verify slots were created
            total_slots = TimeSlot.objects.filter(playground=playground).count()
            print(f"Total slots in database for this playground: {total_slots}")
                        
        except Exception as e:
            print(f"Error generating time slots: {e}")
            import traceback
            traceback.print_exc()
    
    def save_temporary_data_to_playground(self, request, playground):
        """Convert temporary session data to actual database records"""
        try:
            from .models import DurationPass, PlaygroundSlot
            from decimal import Decimal
            
            print(f"Saving temporary data for playground: {playground.name}")
            print(f"Session keys: {list(request.session.keys())}")
            
            saved_passes = []
            saved_slots = []
            
            # Save temporary membership passes
            if 'temporary_membership_passes' in request.session:
                temp_passes = request.session['temporary_membership_passes']
                print(f"Found {len(temp_passes)} temporary membership passes")
                
                for temp_pass in temp_passes:
                    try:
                        print(f"Creating membership pass: {temp_pass.get('name', 'Unknown')}")
                        
                        # Create real membership pass
                        duration_pass = DurationPass.objects.create(
                            playground=playground,
                            name=temp_pass['name'],
                            duration_type=temp_pass['duration_type'],
                            duration_days=int(temp_pass['duration_days']),
                            price=Decimal(str(temp_pass['price'])),
                            currency=temp_pass.get('currency', 'BDT'),
                            description=temp_pass.get('description', ''),
                            features=temp_pass.get('features', []),
                            sport_types=temp_pass.get('sport_types', []),
                            access_pattern=temp_pass.get('access_pattern', 'unlimited'),
                            peak_access=temp_pass.get('peak_access', False),
                            is_active=True
                        )
                        
                        saved_passes.append(duration_pass.name)
                        print(f"Successfully created membership pass: {duration_pass.name}")
                        
                    except Exception as e:
                        print(f"Error saving membership pass {temp_pass.get('name', 'Unknown')}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                # Clear temporary passes from session
                del request.session['temporary_membership_passes']
                print("Cleared temporary membership passes from session")
            else:
                print("No temporary membership passes found in session")
            
            # Save temporary custom slots
            if 'temporary_custom_slots' in request.session:
                temp_slots = request.session['temporary_custom_slots']
                print(f"Found {len(temp_slots)} temporary custom slots")
                
                for temp_slot in temp_slots:
                    try:
                        print(f"Creating custom slot: {temp_slot.get('name', 'Unknown')}")
                        
                        # Create real custom slot
                        playground_slot = PlaygroundSlot.objects.create(
                            playground=playground,
                            slot_type=temp_slot['slot_type'],
                            start_time=temp_slot['start_time'],
                            end_time=temp_slot['end_time'],
                            price=Decimal(str(temp_slot['price'])),
                            currency=temp_slot.get('currency', 'BDT'),
                            day_of_week=temp_slot.get('day_of_week', 'monday'),  # Default to monday since it's required
                            is_active=temp_slot.get('is_active', True),
                            max_capacity=temp_slot.get('max_capacity', 10),
                            description=temp_slot.get('description', ''),
                            features=temp_slot.get('features', [])
                        )
                        
                        slot_name = f"{playground_slot.get_slot_type_display()} Slot"
                        saved_slots.append(slot_name)
                        print(f"Successfully created custom slot: {slot_name}")
                        
                    except Exception as e:
                        print(f"Error saving custom slot {temp_slot.get('name', 'Unknown')}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                # Clear temporary slots from session
                del request.session['temporary_custom_slots']
                print("Cleared temporary custom slots from session")
            else:
                print("No temporary custom slots found in session")
            
            print(f"Successfully saved {len(saved_passes)} membership passes and {len(saved_slots)} custom slots")
            
        except Exception as e:
            print(f"Error in save_temporary_data_to_playground: {e}")
            import traceback
            traceback.print_exc()
            
            # Save session changes
            request.session.modified = True
            
            if saved_passes or saved_slots:
                print(f"Saved temporary data for {playground.name}: {len(saved_passes)} passes, {len(saved_slots)} custom slots")
            
        except Exception as e:
            print(f"Error saving temporary data: {e}")

class EditPlaygroundView(TemplateView):
    template_name = 'playground/edit.html'

class ManagePlaygroundView(TemplateView):
    template_name = 'playground/manage.html'

def get_states(request):
    from django.http import JsonResponse
    country_id = request.GET.get('country_id')
    from playgrounds.models import State
    states = State.objects.filter(country_id=country_id, is_active=True).order_by('name')
    state_list = [{'id': s.id, 'name': s.name} for s in states]
    return JsonResponse({'states': state_list})

def get_cities(request):
    from django.http import JsonResponse
    state_id = request.GET.get('state_id')
    from playgrounds.models import City
    cities = City.objects.filter(state_id=state_id, is_active=True).order_by('name')
    city_list = [{'id': c.id, 'name': c.name} for c in cities]
    return JsonResponse({'cities': city_list})

def check_availability(request):
    from django.http import JsonResponse
    return JsonResponse({'available': True})

def load_slots_by_date(request):
    """Load available time slots for a specific playground and date from database"""
    if request.method == 'GET':
        playground_id = request.GET.get('playground_id')
        date_str = request.GET.get('date')
        
        try:
            from .models import TimeSlot, SlotBooking
            import calendar
            from datetime import datetime
            
            playground = Playground.objects.get(id=playground_id)
            
            # Parse the date
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
            day_name = calendar.day_name[selected_date.weekday()].lower()
            
            # Get actual time slots from database for this day
            time_slots = TimeSlot.objects.filter(
                playground=playground,
                day_of_week=day_name,
                is_available=True
            ).order_by('start_time')
            
            slots = []
            
            if time_slots.exists():
                # Use actual database slots with both day and date filtering
                for slot in time_slots:
                    # For TimeSlot, we'll assume all are available for now
                    # In a real system, you'd have a separate TimeSlotBooking model
                    is_booked = False  # TODO: Implement proper TimeSlot booking check
                    
                    # Use slot-specific price if available, otherwise use playground base price
                    slot_price = slot.price if slot.price else playground.price_per_hour
                    
                    # Calculate duration manually if duration_hours property doesn't exist
                    try:
                        duration = slot.duration_hours
                    except:
                        from datetime import datetime, timedelta
                        start = datetime.combine(selected_date, slot.start_time)
                        end = datetime.combine(selected_date, slot.end_time)
                        if end < start:  # Next day
                            end += timedelta(days=1)
                        duration = (end - start).total_seconds() / 3600
                    
                    slots.append({
                        'id': slot.id,
                        'start_time': slot.start_time.strftime('%H:%M'),
                        'end_time': slot.end_time.strftime('%H:%M'),
                        'price': float(slot_price),
                        'currency': 'BDT',  # Default currency
                        'status': 'booked' if is_booked else 'available',
                        'duration_hours': duration,
                        'max_bookings': slot.max_bookings,
                        'slot_type': 'regular'
                    })
            else:
                # No slots in database - generate default slots for this day
                # This handles playgrounds created before slot system was implemented
                default_slots = [
                    {'start_time': '09:00', 'end_time': '10:00'},
                    {'start_time': '10:00', 'end_time': '11:00'},
                    {'start_time': '11:00', 'end_time': '12:00'},
                    {'start_time': '12:00', 'end_time': '13:00'},
                    {'start_time': '14:00', 'end_time': '15:00'},
                    {'start_time': '15:00', 'end_time': '16:00'},
                    {'start_time': '16:00', 'end_time': '17:00'},
                    {'start_time': '17:00', 'end_time': '18:00'},
                    {'start_time': '18:00', 'end_time': '19:00'},
                    {'start_time': '19:00', 'end_time': '20:00'},
                ]
                
                # Generate default slots with date-based booking simulation
                import random
                random.seed(str(selected_date) + str(playground.id))  # Consistent seed
                
                for i, default_slot in enumerate(default_slots):
                    start_time_obj = datetime.strptime(default_slot['start_time'], '%H:%M').time()
                    end_time_obj = datetime.strptime(default_slot['end_time'], '%H:%M').time()
                    
                    # For default slots, simulate some bookings for demo (30% chance)
                    # In a real system, you'd check against actual booking records
                    is_booked = random.random() < 0.3
                    
                    slots.append({
                        'id': f'default_{i}',
                        'start_time': default_slot['start_time'],
                        'end_time': default_slot['end_time'],
                        'price': float(playground.price_per_hour),
                        'currency': 'BDT',
                        'status': 'booked' if is_booked else 'available',
                        'duration_hours': 1.0,
                        'max_bookings': 1,
                        'slot_type': 'default'
                    })

            return JsonResponse({
                'success': True,
                'slots': slots,
                'date': date_str,
                'day_name': day_name.title(),
                'playground_currency': 'BDT',  # Default currency
                'total_slots': len(slots),
                'source': 'database' if time_slots.exists() else 'default'
            })
            
        except Playground.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Playground not found'
            })
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid date format'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })

def load_membership_passes(request):
    """Load membership passes for a playground from database"""
    if request.method == 'GET':
        playground_id = request.GET.get('playground_id')
        
        try:
            from .models import DurationPass
            
            playground = Playground.objects.get(id=playground_id)
            
            # Get actual duration passes from database
            duration_passes = DurationPass.objects.filter(
                playground=playground,
                is_active=True
            ).order_by('duration_days', 'price')
            
            passes = []
            for pass_obj in duration_passes:
                # Icon mapping based on duration type
                icon_map = {
                    'weekly': '🎫',
                    'monthly': '👑',
                    'custom': '⭐'
                }
                
                passes.append({
                    'id': str(pass_obj.id),
                    'name': pass_obj.name,
                    'price': float(pass_obj.price),
                    'currency': pass_obj.currency,
                    'duration': f"{pass_obj.duration_days} days",
                    'duration_type': pass_obj.duration_type,
                    'icon': icon_map.get(pass_obj.duration_type, '🎟️'),
                    'description': pass_obj.description,
                    'features': pass_obj.features,
                    'sport_types': pass_obj.sport_types,
                    'access_pattern': pass_obj.access_pattern,
                    'peak_access': pass_obj.peak_access,
                    'price_per_day': float(pass_obj.price_per_day),
                    'discount_percentage': pass_obj.discount_percentage
                })
            
            return JsonResponse({
                'success': True,
                'passes': passes,
                'playground_currency': 'BDT',
                'total_passes': len(passes)
            })
            
        except Playground.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Playground not found'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })

def load_custom_slots(request):
    """Load custom slots for a playground from database"""
    if request.method == 'GET':
        playground_id = request.GET.get('playground_id')
        
        try:
            from .models import PlaygroundSlot
            
            playground = Playground.objects.get(id=playground_id)
            
            # Get actual custom slots from database
            custom_slots = PlaygroundSlot.objects.filter(
                playground=playground,
                is_active=True
            ).order_by('slot_type', 'start_time')
            
            slots = []
            for slot in custom_slots:
                # Icon mapping based on slot type
                icon_map = {
                    'regular': '⏰',
                    'premium': '⭐',
                    'vip': '👑'
                }
                
                slots.append({
                    'id': str(slot.id),
                    'name': f"{slot.get_slot_type_display()} Slot",
                    'price': float(slot.price),
                    'currency': slot.currency,
                    'description': slot.description or f"{slot.get_slot_type_display()} experience",
                    'icon': icon_map.get(slot.slot_type, '⚙️'),
                    'slot_type': slot.slot_type,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'day_of_week': slot.get_day_of_week_display(),
                    'max_capacity': slot.max_capacity,
                    'features': slot.features,
                    'duration_hours': slot.duration_hours
                })
            
            return JsonResponse({
                'success': True,
                'slots': slots,
                'playground_currency': 'BDT',
                'total_slots': len(slots)
            })
            
        except Playground.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Playground not found'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })

def load_amenities(request):
    """Load amenities for a playground from real data"""
    if request.method == 'GET':
        playground_id = request.GET.get('playground_id')
        
        try:
            playground = Playground.objects.get(id=playground_id)
            
            # Get real amenities from the playground's amenities field
            amenities = []
            if playground.amenities:
                for amenity_data in playground.amenities:
                    # Handle potential typo in field name
                    amenity_name = amenity_data.get('name') or amenity_data.get('naame', 'Unknown')
                    amenities.append({
                        'name': amenity_name,
                        'description': amenity_data.get('description', ''),
                        'icon': amenity_data.get('icon', '⭐'),
                        'type': amenity_data.get('type', 'free'),
                        'price': amenity_data.get('price')
                    })
            
            return JsonResponse({
                'success': True,
                'amenities': amenities,
                'total_amenities': len(amenities)
            })
            
        except Playground.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Playground not found'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })

def load_booking_info(request):
    """Load booking information for a playground"""
    if request.method == 'GET':
        playground_id = request.GET.get('playground_id')
        
        try:
            playground = Playground.objects.get(id=playground_id)
            
            # Calculate booking information
            booking_info = {
                'base_rate': float(playground.price_per_hour),
                'regular_price': float(playground.price_per_hour),
                'membership_price': 500000,
                'custom_price': 1000,
                'max_capacity': playground.capacity,
                'recommended_capacity': max(1, playground.capacity - 4),
                'advance_booking_hours': 24
            }
            
            payment_methods = [
                {
                    'name': 'Credit Card',
                    'icon': '💳'
                },
                {
                    'name': 'Mobile Payment',
                    'icon': '📱'
                },
                {
                    'name': 'Cash',
                    'icon': '💰'
                }
            ]
            
            return JsonResponse({
                'success': True,
                'booking_info': booking_info,
                'payment_methods': payment_methods
            })
            
        except Playground.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Playground not found'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })
