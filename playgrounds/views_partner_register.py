from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
from playgrounds.models import Playground, PlaygroundImage, SportType, City, State, Country
from accounts.models import User, PartnerApplication, PlaygroundApplication, PlaygroundApplicationImage
from django.core.files.storage import default_storage
from django.conf import settings

class PartnerRegisterView(View):
    template_name = 'pages/partner_register.html'

    @method_decorator(login_required)
    def get(self, request):
        countries = Country.objects.filter(is_active=True).order_by('name')
        states = State.objects.filter(is_active=True).select_related('country').order_by('name')
        cities = City.objects.filter(is_active=True).select_related('state', 'state__country').order_by('name')
        
        # Check for existing partner application
        partner_app = PartnerApplication.objects.filter(user=request.user).first()
        app_status = None
        if partner_app:
            app_status = partner_app.status
        return render(request, self.template_name, {
            'countries': countries,
            'states': states,
            'cities': cities,
            'partner_app_status': app_status,
            'partner_app': partner_app
        })

    @method_decorator(login_required)
    def post(self, request):
        owner = request.user
        # Check for existing application
        partner_app = PartnerApplication.objects.filter(user=owner).first()
        
        # If pending, block resubmission (but allow approved partners to add more playgrounds)
        if partner_app and partner_app.status == 'pending':
            messages.warning(request, 'You have already submitted a partner application. Please wait for admin approval before submitting again.')
            return redirect('partner_register')
        
        # If no partner application exists or if rejected, require new application
        create_new_application = False
        if not partner_app or partner_app.status == 'rejected':
            create_new_application = True

        # Collect form data
        name = request.POST.get('playground_name')
        playground_type = request.POST.get('playground_type')
        sport_types = request.POST.get('sport_types')
        address = request.POST.get('address')
        country_id = request.POST.get('country')
        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        google_map = request.POST.get('google_map')
        
        # Convert and validate numeric fields
        try:
            capacity = int(request.POST.get('capacity', 1)) if request.POST.get('capacity') else 1
            price_per_hour = float(request.POST.get('price_per_hour', 0)) if request.POST.get('price_per_hour') else 0.0
        except (ValueError, TypeError):
            messages.error(request, "Please provide valid numeric values for capacity and price.")
            return redirect('partner_register')
        
        size = request.POST.get('size', '')
        description = request.POST.get('description', '')
        rules = request.POST.get('rules', '')
        gallery = request.FILES.getlist('gallery')
        videos = request.FILES.getlist('videos')
        
        # Basic validation
        if not name or not playground_type or not address:
            messages.error(request, "Please fill in all required fields (name, type, and address).")
            return redirect('partner_register')
            
        if capacity <= 0:
            messages.error(request, "Capacity must be greater than 0.")
            return redirect('partner_register')
            
        if price_per_hour < 0:
            messages.error(request, "Price per hour cannot be negative.")
            return redirect('partner_register')

        # Get city/state/country objects
        city = City.objects.filter(id=city_id).first()
        if not city:
            messages.error(request, "Invalid city selection.")
            countries = Country.objects.filter(is_active=True).order_by('name')
            return render(request, self.template_name, {'countries': countries})

        # Create or update partner application only if needed
        if create_new_application:
            if partner_app and partner_app.status == 'rejected':
                # Update existing rejected application
                partner_app.business_name = name
                partner_app.business_address = address
                partner_app.business_phone = owner.phone_number or ''
                partner_app.business_email = owner.email
                partner_app.description = description
                partner_app.status = 'pending'
                partner_app.admin_comments = ''
                partner_app.save()
            else:
                # Create new partner application
                partner_app = PartnerApplication.objects.create(
                    user=owner,
                    business_name=name,
                    business_address=address,
                    business_phone=owner.phone_number or '',
                    business_email=owner.email,
                    description=description,
                    status='pending',
                )

        # Always create a new PlaygroundApplication for each submission
        # The playground will be created automatically when this is saved
        playground_app = PlaygroundApplication.objects.create(
            user=owner,
            name=name,
            description=description,
            city=city,
            address=address,
            playground_type=playground_type,
            capacity=capacity,
            size=size or '',
            price_per_hour=price_per_hour,
            rules=rules or '',
            sport_types=sport_types or '',  # Store as comma-separated string
            status='pending',  # Keep pending for admin approval
        )
        
        # Gallery images (max 6) - store in PlaygroundApplicationImage
        for i, img in enumerate(gallery):
            if i >= 6:
                break
            PlaygroundApplicationImage.objects.create(application=playground_app, image=img)
        # TODO: Handle videos (if you have a model for them)
        
        # Success message - playground created and pending approval
        messages.success(request, f'Your playground "{name}" has been submitted successfully and is pending admin approval!')
        
        return redirect('partner_register')
