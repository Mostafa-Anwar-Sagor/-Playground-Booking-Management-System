from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, UserProfile, PartnerApplication


class EmailAuthenticationForm(AuthenticationForm):
    """Custom authentication form that uses email instead of username"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')  # Django uses 'username' field name
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,  # Our USERNAME_FIELD is email
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Please enter a correct email and password.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with email and additional fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field from the form
        if 'username' in self.fields:
            del self.fields['username']
        
        # Add CSS classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        # Create user without calling super().save() to avoid username issues
        user = User(
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            user_type='user'
        )
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'favorite_sports', 'emergency_contact', 'preferred_time_slots']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact number'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Handle JSON fields as text areas for now
        self.fields['favorite_sports'].widget = forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'e.g., Football, Basketball, Tennis'
        })
        self.fields['preferred_time_slots'].widget = forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'e.g., Morning, Evening'
        })


class PartnerApplicationForm(forms.ModelForm):
    """Form for playground owners to apply for partnership"""
    class Meta:
        model = PartnerApplication
        fields = ['business_name', 'business_address', 'business_phone', 'business_email', 'business_license', 'description', 'experience_years']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your business name'}),
            'business_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Complete business address'}),
            'business_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business phone number'}),
            'business_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Business email address'}),
            'business_license': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your business and playground facilities'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Years of experience'}),
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
