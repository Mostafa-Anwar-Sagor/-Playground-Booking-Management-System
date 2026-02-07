"""
Test Script - Create test users for Admin and Owner dashboards
Run with: python manage.py shell < create_test_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playground_booking.settings')
django.setup()

from accounts.models import User, PartnerApplication

def create_test_users():
    print("=" * 60)
    print("Creating Test Users for Dashboard Testing")
    print("=" * 60)
    
    # 1. Create Admin User
    admin_email = "admin@playgroundhub.com"
    admin_password = "Admin@123"
    
    admin, created = User.objects.get_or_create(
        email=admin_email,
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    if created:
        admin.set_password(admin_password)
        admin.save()
        print(f"✅ Created Admin User:")
    else:
        admin.set_password(admin_password)
        admin.user_type = 'admin'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f"✅ Updated Admin User:")
    
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    print(f"   Dashboard: /admin-panel/")
    print()
    
    # 2. Create Owner User
    owner_email = "owner@playgroundhub.com"
    owner_password = "Owner@123"
    
    owner, created = User.objects.get_or_create(
        email=owner_email,
        defaults={
            'first_name': 'Owner',
            'last_name': 'User',
            'user_type': 'owner',
            'is_active': True,
        }
    )
    if created:
        owner.set_password(owner_password)
        owner.save()
        print(f"✅ Created Owner User:")
    else:
        owner.set_password(owner_password)
        owner.user_type = 'owner'
        owner.save()
        print(f"✅ Updated Owner User:")
    
    print(f"   Email: {owner_email}")
    print(f"   Password: {owner_password}")
    print(f"   Dashboard: /owner-dashboard/")
    print()
    
    # 3. Create Regular User
    user_email = "user@playgroundhub.com"
    user_password = "User@123"
    
    user, created = User.objects.get_or_create(
        email=user_email,
        defaults={
            'first_name': 'Regular',
            'last_name': 'User',
            'user_type': 'user',
            'is_active': True,
        }
    )
    if created:
        user.set_password(user_password)
        user.save()
        print(f"✅ Created Regular User:")
    else:
        user.set_password(user_password)
        user.user_type = 'user'
        user.save()
        print(f"✅ Updated Regular User:")
    
    print(f"   Email: {user_email}")
    print(f"   Password: {user_password}")
    print(f"   Dashboard: /dashboard/")
    print()
    
    # 4. Create a Pending Partner Application for the regular user
    user2_email = "pending@playgroundhub.com"
    user2_password = "Pending@123"
    
    user2, created = User.objects.get_or_create(
        email=user2_email,
        defaults={
            'first_name': 'Pending',
            'last_name': 'Owner',
            'user_type': 'user',
            'is_active': True,
        }
    )
    user2.set_password(user2_password)
    user2.save()
    
    # Create partner application
    app, app_created = PartnerApplication.objects.get_or_create(
        user=user2,
        defaults={
            'business_name': 'Test Sports Complex',
            'business_address': '123 Sports Street, City',
            'business_phone': '+1234567890',
            'business_email': user2_email,
            'description': 'A premium sports facility with multiple playgrounds.',
            'experience_years': 5,
            'status': 'pending',
        }
    )
    
    if app_created:
        print(f"✅ Created Pending Partner Application:")
    else:
        print(f"✅ Pending Partner Application exists:")
    
    print(f"   User Email: {user2_email}")
    print(f"   Password: {user2_password}")
    print(f"   Business: {app.business_name}")
    print(f"   Status: {app.status}")
    print()
    
    print("=" * 60)
    print("TEST CREDENTIALS SUMMARY")
    print("=" * 60)
    print()
    print("🔐 ADMIN LOGIN:")
    print(f"   URL: http://127.0.0.1:8000/login/")
    print(f"   Email: admin@playgroundhub.com")
    print(f"   Password: Admin@123")
    print(f"   Dashboard: http://127.0.0.1:8000/admin-panel/")
    print()
    print("🏟️ OWNER LOGIN:")
    print(f"   URL: http://127.0.0.1:8000/login/")
    print(f"   Email: owner@playgroundhub.com")
    print(f"   Password: Owner@123")
    print(f"   Dashboard: http://127.0.0.1:8000/owner-dashboard/")
    print()
    print("👤 REGULAR USER LOGIN:")
    print(f"   URL: http://127.0.0.1:8000/login/")
    print(f"   Email: user@playgroundhub.com")
    print(f"   Password: User@123")
    print(f"   Dashboard: http://127.0.0.1:8000/dashboard/")
    print()
    print("=" * 60)
    
if __name__ == '__main__':
    create_test_users()
