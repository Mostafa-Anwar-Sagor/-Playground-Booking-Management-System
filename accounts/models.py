from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


def default_dict():
    return {}


def default_list():
    return []


class CustomUserManager(BaseUserManager):
    """Custom user manager for email authentication only - NO USERNAME"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Create user with email only - NO username
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPES = (
        ('user', 'Regular User'),
        ('owner', 'Playground Owner'),
        ('admin', 'Administrator'),
    )
    
    # Remove username field completely - we use email only
    username = None
    email = models.EmailField(unique=True)
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # For owner approval
    city = models.ForeignKey('playgrounds.City', on_delete=models.SET_NULL, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    # Additional fields for better user experience
    notification_settings = models.JSONField(default=default_dict, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def display_name(self):
        """Return the best display name for the user"""
        if self.first_name:
            return self.first_name
        full = f"{self.first_name} {self.last_name}".strip()
        if full:
            return full
        # Use email username part as fallback
        return self.email.split('@')[0] if self.email else 'User'
    
    def get_full_name(self):
        """Return the full name or email if name is not available"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email
    
    def get_dashboard_url(self):
        """Return the appropriate dashboard URL based on user type"""
        if self.user_type == 'admin':
            return '/admin-panel/'
        elif self.user_type == 'owner':
            return '/owner-dashboard/'
        else:
            return '/dashboard/'
    
    @property
    def playgrounds(self):
        """Get all playgrounds owned by this user"""
        try:
            from playgrounds.models import Playground
            return Playground.objects.filter(owner=self)
        except ImportError:
            return None


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    favorite_sports = models.JSONField(default=default_list, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    preferred_time_slots = models.JSONField(default=default_list, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class PartnerApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    business_address = models.TextField()
    business_phone = models.CharField(max_length=15)
    business_email = models.EmailField()
    business_license = models.ImageField(upload_to='licenses/', blank=True, null=True)
    description = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_comments = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_applications')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Partner Application - {self.business_name} by {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Store the previous status
        old_status = None
        if self.pk:
            old_status = PartnerApplication.objects.get(pk=self.pk).status
        
        super().save(*args, **kwargs)
        
        # If status changed from pending/rejected to approved, upgrade user to owner
        if old_status != 'approved' and self.status == 'approved':
            self.user.user_type = 'owner'
            self.user.save()
            
            # Create notification for user
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=self.user,
                    title='Partner Application Approved!',
                    message=f'Congratulations! Your partner application for "{self.business_name}" has been approved. You now have access to the owner dashboard.',
                    notification_type='partner_approved'
                )
            except (ImportError, Exception):
                pass  # Notifications app might not be available
        
        # If status changed to rejected, create notification
        elif old_status != 'rejected' and self.status == 'rejected':
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=self.user,
                    title='Partner Application Rejected',
                    message=f'Sorry, your partner application for "{self.business_name}" was rejected. Please check admin comments for details.',
                    notification_type='partner_rejected'
                )
            except (ImportError, Exception):
                pass  # Notifications app might not be available



# --- Partner Application Images ---
class PartnerApplicationImage(models.Model):
    application = models.ForeignKey('PartnerApplication', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='partner_applications/images/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Image for {self.application.business_name}"

# --- Partner Application Videos ---
class PartnerApplicationVideo(models.Model):
    application = models.ForeignKey(PartnerApplication, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='partner_applications/videos/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Video for {self.application.business_name}"


# --- Playground Application (Pending) ---
class PlaygroundApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    PLAYGROUND_TYPES = (
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('hybrid', 'Indoor/Outdoor'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playground_applications')
    
    # Playground data fields
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    address = models.TextField()
    city = models.ForeignKey('playgrounds.City', on_delete=models.CASCADE)
    playground_type = models.CharField(max_length=10, choices=PLAYGROUND_TYPES)
    capacity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=100, blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    rules = models.TextField(blank=True, null=True)
    sport_types = models.TextField(blank=True, null=True)  # Store as comma-separated values
    
    # Application status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_comments = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_playground_applications')
    
    # Created playground reference (when approved)
    created_playground = models.OneToOneField('playgrounds.Playground', on_delete=models.SET_NULL, null=True, blank=True, related_name='application')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Playground Application - {self.name} by {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Store the previous status to detect changes
        old_status = None
        if self.pk:
            try:
                old_status = PlaygroundApplication.objects.get(pk=self.pk).status
            except PlaygroundApplication.DoesNotExist:
                old_status = None
        
        super().save(*args, **kwargs)
        
        # Create playground immediately when application is saved (no admin approval needed)
        if not self.created_playground:
            try:
                self.create_playground()
            except Exception as e:
                # Log the error but don't break the save process
                import logging
                logging.error(f"Failed to auto-create playground for {self.name}: {str(e)}")
                # Re-raise the exception so admin knows something went wrong
                raise
    
    def create_playground(self):
        """Create the actual Playground object automatically when application is saved"""
        from playgrounds.models import Playground, SportType
        
        # Create the playground object with "pending" status for admin approval
        playground = Playground.objects.create(
            owner=self.user,
            name=self.name,
            description=self.description,
            city=self.city,
            address=self.address,
            playground_type=self.playground_type,
            capacity=self.capacity,
            size=self.size,
            price_per_hour=self.price_per_hour,
            status='pending',  # Set to pending for admin approval
            rules=self.rules,
        )
        
        # Add sport types if specified
        if self.sport_types:
            for sport in [s.strip() for s in self.sport_types.split(',') if s.strip()]:
                st, _ = SportType.objects.get_or_create(name=sport)
                playground.sport_types.add(st)
        
        # Copy images from application to playground
        for img in self.images.all():
            from playgrounds.models import PlaygroundImage
            PlaygroundImage.objects.create(
                playground=playground,
                image=img.image
            )
        
        # Link the created playground to this application
        self.created_playground = playground
        self.save(update_fields=['created_playground'])
        
        # Send notification to user about creation (pending approval)
        try:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=self.user,
                title='Playground Submitted!',
                message=f'Your playground "{self.name}" has been created and submitted for admin approval. You will be notified once approved.',
                notification_type='playground_approved'
            )
        except (ImportError, Exception):
            # If notifications fail, don't break the playground creation
            pass
            
        return playground


class PlaygroundApplicationImage(models.Model):
    application = models.ForeignKey(PlaygroundApplication, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='playground_applications/images/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Image for {self.application.name}"
