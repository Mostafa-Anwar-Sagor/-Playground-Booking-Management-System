from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


def default_list():
    return []


def default_dict():
    return {}


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)  # ISO country code
    currency_code = models.CharField(max_length=3, default='USD', help_text='Currency code (USD, EUR, GBP, etc.)')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_currency(self):
        """Get currency code for this country"""
        # Map by ISO country code
        currency_map = {
            'US': 'USD', 'GB': 'GBP', 'MY': 'MYR', 'SG': 'SGD',
            'IN': 'INR', 'BD': 'BDT', 'AU': 'AUD', 'CA': 'CAD',
            'JP': 'JPY', 'CN': 'CNY', 'AE': 'AED', 'SA': 'SAR',
            'TH': 'THB', 'ID': 'IDR', 'PH': 'PHP', 'VN': 'VND',
            'KR': 'KRW', 'TW': 'TWD', 'HK': 'HKD', 'NZ': 'NZD'
        }
        
        # Also map by country name (lowercase)
        name_currency_map = {
            'usa': 'USD', 'united states': 'USD', 'america': 'USD',
            'malaysia': 'MYR', 'singapore': 'SGD', 'india': 'INR',
            'bangladesh': 'BDT', 'australia': 'AUD', 'canada': 'CAD',
            'japan': 'JPY', 'china': 'CNY', 'uae': 'AED', 
            'united arab emirates': 'AED', 'saudi arabia': 'SAR',
            'thailand': 'THB', 'indonesia': 'IDR', 'philippines': 'PHP',
            'vietnam': 'VND', 'south korea': 'KRW', 'korea': 'KRW',
            'taiwan': 'TWD', 'hong kong': 'HKD', 'new zealand': 'NZD',
            'united kingdom': 'GBP', 'uk': 'GBP', 'england': 'GBP',
            'pakistan': 'PKR', 'turkey': 'TRY', 'egypt': 'EGP',
            'brazil': 'BRL', 'mexico': 'MXN', 'russia': 'RUB'
        }
        
        # First check by code
        if self.code and len(self.code) == 2:
            result = currency_map.get(self.code.upper())
            if result:
                return result
        
        # Then check by name
        name_lower = self.name.lower().strip()
        if name_lower in name_currency_map:
            return name_currency_map[name_lower]
        
        # Fallback to stored currency_code
        return self.currency_code or 'USD'


class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'country']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ['name', 'state']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"


class SportType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Font awesome icon class
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class PlaygroundType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Emoji or icon class
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Amenity(models.Model):
    AMENITY_TYPES = (
        ('free', 'Free'),
        ('paid', 'Paid'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    amenity_type = models.CharField(max_length=10, choices=AMENITY_TYPES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Playground(models.Model):
    PLAYGROUND_TYPES = (
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('hybrid', 'Indoor/Outdoor'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('pending', 'Pending Approval'),
        ('draft', 'Draft'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playgrounds')
    name = models.CharField(max_length=200)
    description = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='playgrounds')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Playground details
    sport_types = models.ManyToManyField(SportType, related_name='playgrounds')
    playground_type = models.CharField(max_length=10, choices=PLAYGROUND_TYPES, default='outdoor')
    capacity = models.PositiveIntegerField(help_text="Maximum number of players")
    size = models.CharField(max_length=100, help_text="e.g., '40x20 meters'", blank=True)
    
    # Pricing and Payment
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='BDT', help_text="Currency code (e.g., BDT, USD, EUR)")
    custom_pricing = models.JSONField(default=default_dict, blank=True, null=True, 
                                     help_text="Custom pricing for different time slots or days")
    
    # Payment Methods
    payment_methods = models.JSONField(default=default_dict, blank=True, null=True,
                                      help_text="Available payment methods and details")
    bank_details = models.JSONField(default=default_dict, blank=True, null=True,
                                   help_text="Bank account details for payments")
    qr_code_image = models.ImageField(upload_to='playgrounds/qr_codes/', blank=True, null=True,
                                     help_text="QR code for digital payments")
    
    # Availability Settings
    operating_hours = models.JSONField(default=default_dict, blank=True, null=True,
                                      help_text="Daily operating hours")
    available_days = models.JSONField(default=default_list, blank=True, null=True,
                                     help_text="Available days of the week")
    slot_templates = models.JSONField(default=default_list, blank=True, null=True,
                                     help_text="Time slot templates")
    advance_booking_days = models.PositiveIntegerField(default=30,
                                                      help_text="How many days in advance can users book")
    
    # Google Maps Integration
    google_maps_url = models.URLField(blank=True, null=True, help_text="Google Maps location URL")
    google_maps_embed_url = models.URLField(blank=True, null=True, help_text="Google Maps embed URL")
    
    # Communication Settings
    enable_chat = models.BooleanField(default=True, help_text="Allow chat with users")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Booking Management
    auto_approval = models.BooleanField(default=False, help_text="Automatically approve bookings")
    cancellation_policy = models.TextField(blank=True, help_text="Cancellation policy")
    refund_policy = models.TextField(blank=True, help_text="Refund policy")
    
    # Real-time Features
    live_availability = models.BooleanField(default=True, help_text="Show real-time availability")
    instant_booking = models.BooleanField(default=True, help_text="Allow instant booking")
    
    # Features and amenities
    amenities = models.JSONField(default=default_list, blank=True, null=True, help_text="List of amenities like parking, washroom, etc.")
    playground_amenities = models.ManyToManyField(Amenity, blank=True, related_name='playgrounds', help_text="Dynamic amenities with pricing")
    rules = models.TextField(blank=True, help_text="Playground rules and regulations")
    
    # Images
    main_image = models.ImageField(upload_to='playgrounds/main/', blank=True, null=True)
    
    # Status and approval
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False, help_text='Mark as popular to show on homepage')
    
    # Analytics
    total_bookings = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def get_sport_types_display(self):
        return ", ".join([sport.name for sport in self.sport_types.all()])
    
    @property
    def average_rating(self):
        return self.rating
    
    def update_rating(self):
        """Update the average rating based on reviews"""
        reviews = self.reviews.all()
        if reviews:
            total_rating = sum([review.rating for review in reviews])
            self.rating = total_rating / len(reviews)
            self.review_count = len(reviews)
            self.save()


class PlaygroundImage(models.Model):
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='playgrounds/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Image for {self.playground.name}"


class TimeSlot(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Override default price
    is_available = models.BooleanField(default=True)
    max_bookings = models.PositiveIntegerField(default=1, help_text="Number of simultaneous bookings allowed")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['playground', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.playground.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    
    @property
    def duration_hours(self):
        """Calculate duration in hours"""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        if end < start:  # Handle overnight slots
            end += timedelta(days=1)
        return (end - start).total_seconds() / 3600
    
    def get_effective_price(self):
        """Get the effective price for this slot"""
        return self.price if self.price else self.playground.price_per_hour


class Review(models.Model):
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['playground', 'user', 'booking']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.playground.name} - {self.rating}★"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='favorited_by')
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'playground']
    
    def __str__(self):
        return f"{self.user.username} favorited {self.playground.name}"


class PlaygroundVideo(models.Model):
    """Model for playground videos"""
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='playgrounds/videos/')
    thumbnail = models.ImageField(upload_to='playgrounds/video_thumbnails/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Video for {self.playground.name}"


class PlaygroundChat(models.Model):
    """Model for chat between playground owners and users"""
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='chats')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playground_chats')
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='chats/attachments/', blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat: {self.playground.name} - {self.user.email}"


class PlaygroundAnalytics(models.Model):
    """Model for tracking playground analytics"""
    playground = models.OneToOneField(Playground, on_delete=models.CASCADE, related_name='analytics')
    total_views = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    peak_hours = models.JSONField(default=default_dict, blank=True, null=True)
    popular_days = models.JSONField(default=default_dict, blank=True, null=True)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics: {self.playground.name}"


class PlaygroundAvailability(models.Model):
    """Model for real-time availability tracking"""
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='availability')
    available_spots = models.PositiveIntegerField(default=1)
    total_spots = models.PositiveIntegerField(default=1)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['playground', 'date', 'time_slot']
        ordering = ['date', 'time_slot__start_time']
    
    def __str__(self):
        return f"{self.playground.name} - {self.date} - {self.time_slot}"
    
    @property
    def is_available(self):
        return not self.is_blocked and self.available_spots > 0


class PlaygroundSlot(models.Model):
    """Professional model for custom playground slots"""
    SLOT_TYPES = [
        ('regular', 'Regular'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='custom_slots')
    slot_type = models.CharField(max_length=20, choices=SLOT_TYPES, default='regular')
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    max_capacity = models.PositiveIntegerField(default=10)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['playground', 'day_of_week', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.playground.name} - {self.get_slot_type_display()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    
    @property
    def duration_hours(self):
        """Calculate slot duration in hours"""
        from datetime import datetime, time
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600


class DurationPass(models.Model):
    """Professional model for duration passes"""
    DURATION_TYPES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    playground = models.ForeignKey(Playground, on_delete=models.CASCADE, related_name='duration_passes')
    name = models.CharField(max_length=200)
    duration_type = models.CharField(max_length=20, choices=DURATION_TYPES)
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    sport_types = models.JSONField(default=list, blank=True)
    access_pattern = models.CharField(max_length=50, default='unlimited')
    peak_access = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['duration_days', 'price']
    
    def __str__(self):
        return f"{self.playground.name} - {self.name} ({self.duration_days} days)"
    
    @property
    def price_per_day(self):
        """Calculate price per day"""
        return self.price / self.duration_days if self.duration_days > 0 else 0
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage compared to daily rates"""
        # This would need to be calculated based on playground's daily rates
        if self.duration_type == 'weekly':
            return 10
        elif self.duration_type == 'monthly':
            return 25
        return 5


class SlotBooking(models.Model):
    """Professional model for slot bookings"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    slot = models.ForeignKey(PlaygroundSlot, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slot_bookings')
    booking_date = models.DateField()
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    participants = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    special_requests = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-booking_date', '-created_at']
        unique_together = ['slot', 'user', 'booking_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.slot} - {self.booking_date}"


class PassPurchase(models.Model):
    """Professional model for duration pass purchases"""
    PURCHASE_STATUS = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    duration_pass = models.ForeignKey(DurationPass, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pass_purchases')
    purchase_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=PURCHASE_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    payment_status = models.CharField(max_length=20, default='pending')
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.duration_pass.name} - {self.start_date} to {self.end_date}"
    
    @property
    def is_active(self):
        """Check if pass is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.status == 'active' and 
                self.start_date <= today <= self.end_date)
    
    @property
    def days_remaining(self):
        """Calculate remaining days"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date > today:
            return (self.end_date - today).days
        return 0
