"""
Management command to create demo data for testing the owner dashboard
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal

from accounts.models import User
from playgrounds.models import Playground, SportType, Country, State, City
from bookings.models import Booking
from payments.models import PaymentMethod, PlaygroundPaymentConfig


class Command(BaseCommand):
    help = 'Create demo data for testing the owner dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Create or get owner user
        owner, created = User.objects.get_or_create(
            email='owner@test.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Owner',
                'user_type': 'owner',
                'is_active': True
            }
        )
        if created:
            owner.set_password('password123')
            owner.save()
            self.stdout.write(f'Created owner user: {owner.email}')
        
        # Create or get customer user
        customer, created = User.objects.get_or_create(
            email='customer@test.com',
            defaults={
                'first_name': 'Jane',
                'last_name': 'Customer',
                'user_type': 'customer',
                'is_active': True
            }
        )
        if created:
            customer.set_password('password123')
            customer.save()
            self.stdout.write(f'Created customer user: {customer.email}')
        
        # Create location data if not exists
        country, _ = Country.objects.get_or_create(
            name='Bangladesh',
            defaults={'code': 'BD'}
        )
        
        state, _ = State.objects.get_or_create(
            name='Dhaka',
            country=country
        )
        
        city, _ = City.objects.get_or_create(
            name='Dhaka',
            state=state
        )
        
        # Create sport types
        football, _ = SportType.objects.get_or_create(
            name='Football',
            defaults={'is_active': True}
        )
        
        basketball, _ = SportType.objects.get_or_create(
            name='Basketball', 
            defaults={'is_active': True}
        )
        
        # Create demo playgrounds
        playground_data = [
            {
                'name': 'Green Valley Football Ground',
                'description': 'Premium football ground with natural grass',
                'address': '123 Green Valley, Dhaka',
                'capacity': 22,
                'price_per_hour': Decimal('50.00'),
                'status': 'active',
                'sport_type': football
            },
            {
                'name': 'City Basketball Court',
                'description': 'Indoor basketball court with wooden flooring',
                'address': '456 City Center, Dhaka',
                'capacity': 10,
                'price_per_hour': Decimal('30.00'),
                'status': 'active',
                'sport_type': basketball
            }
        ]
        
        playgrounds = []
        for data in playground_data:
            sport_type = data.pop('sport_type')
            playground, created = Playground.objects.get_or_create(
                name=data['name'],
                owner=owner,
                city=city,
                defaults=data
            )
            if created:
                playground.sport_types.add(sport_type)
                self.stdout.write(f'Created playground: {playground.name}')
            playgrounds.append(playground)
        
        # Create payment methods
        payment_methods_data = [
            {
                'name': 'Bkash',
                'method_type': 'mobile_banking',
                'instructions': 'Send money to 01XXXXXXXXX and upload screenshot',
                'is_active': True,
                'requires_receipt': True
            },
            {
                'name': 'Dutch Bangla Bank',
                'method_type': 'bank_transfer',
                'instructions': 'Transfer to Account: 1234567890 and upload receipt',
                'is_active': True,
                'requires_receipt': True
            }
        ]
        
        for data in payment_methods_data:
            PaymentMethod.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
        
        # Create demo bookings
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        booking_data = [
            {
                'playground': playgrounds[0],
                'user': customer,
                'booking_date': today,
                'start_time': time(14, 0),  # 2 PM
                'end_time': time(16, 0),    # 4 PM
                'duration_hours': Decimal('2.0'),
                'price_per_hour': Decimal('50.00'),
                'total_amount': Decimal('100.00'),
                'final_amount': Decimal('100.00'),
                'status': 'pending',
                'payment_status': 'pending',
                'contact_phone': '01700000000',
                'payment_method': 'Bkash'
            },
            {
                'playground': playgrounds[1],
                'user': customer,
                'booking_date': tomorrow,
                'start_time': time(10, 0),  # 10 AM
                'end_time': time(12, 0),    # 12 PM
                'duration_hours': Decimal('2.0'),
                'price_per_hour': Decimal('30.00'),
                'total_amount': Decimal('60.00'),
                'final_amount': Decimal('60.00'),
                'status': 'confirmed',
                'payment_status': 'paid',
                'contact_phone': '01700000000',
                'payment_method': 'Bank Transfer'
            },
            {
                'playground': playgrounds[0],
                'user': customer,
                'booking_date': yesterday,
                'start_time': time(18, 0),  # 6 PM
                'end_time': time(20, 0),    # 8 PM
                'duration_hours': Decimal('2.0'),
                'price_per_hour': Decimal('50.00'),
                'total_amount': Decimal('100.00'),
                'final_amount': Decimal('100.00'),
                'status': 'completed',
                'payment_status': 'paid',
                'contact_phone': '01700000000',
                'payment_method': 'Bkash'
            }
        ]
        
        for data in booking_data:
            booking, created = Booking.objects.get_or_create(
                playground=data['playground'],
                booking_date=data['booking_date'],
                start_time=data['start_time'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created booking: {booking.booking_id}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created demo data!')
        )
        self.stdout.write(f'Owner login: {owner.email} / password123')
        self.stdout.write(f'Customer login: {customer.email} / password123')
