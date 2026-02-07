from django.core.management.base import BaseCommand
from django.utils import timezone
from playgrounds.models import Country, State, City, SportType, Playground
from accounts.models import User
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate database with sample data for the playground booking system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create countries
        countries_data = [
            {'name': 'United States', 'code': 'US'},
            {'name': 'United Kingdom', 'code': 'GB'},
            {'name': 'Canada', 'code': 'CA'},
            {'name': 'Australia', 'code': 'AU'},
            {'name': 'Germany', 'code': 'DE'},
            {'name': 'France', 'code': 'FR'},
            {'name': 'Japan', 'code': 'JP'},
            {'name': 'Brazil', 'code': 'BR'},
            {'name': 'India', 'code': 'IN'},
            {'name': 'Spain', 'code': 'ES'},
        ]
        
        countries = {}
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(**country_data)
            countries[country.code] = country
            if created:
                self.stdout.write(f'Created country: {country.name}')
        
        # Create states
        states_data = {
            'US': ['California', 'New York', 'Texas', 'Florida', 'Illinois'],
            'GB': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
            'CA': ['Ontario', 'Quebec', 'British Columbia', 'Alberta'],
            'AU': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia'],
            'DE': ['Bavaria', 'North Rhine-Westphalia', 'Baden-Württemberg', 'Berlin'],
            'FR': ['Île-de-France', 'Provence-Alpes-Côte d\'Azur', 'Nouvelle-Aquitaine'],
            'JP': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama'],
            'BR': ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia'],
            'IN': ['Maharashtra', 'Delhi', 'Karnataka', 'Gujarat'],
            'ES': ['Madrid', 'Catalonia', 'Andalusia', 'Valencia'],
        }
        
        states = {}
        for country_code, state_names in states_data.items():
            country = countries[country_code]
            for state_name in state_names:
                state, created = State.objects.get_or_create(
                    name=state_name,
                    country=country
                )
                states[f'{country_code}-{state_name}'] = state
                if created:
                    self.stdout.write(f'Created state: {state.name}')
        
        # Create cities
        cities_data = {
            'US-California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento'],
            'US-New York': ['New York City', 'Buffalo', 'Rochester', 'Syracuse'],
            'US-Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio'],
            'US-Florida': ['Miami', 'Orlando', 'Tampa', 'Jacksonville'],
            'GB-England': ['London', 'Manchester', 'Birmingham', 'Liverpool'],
            'CA-Ontario': ['Toronto', 'Ottawa', 'Hamilton', 'London'],
            'AU-New South Wales': ['Sydney', 'Newcastle', 'Wollongong'],
            'DE-Bavaria': ['Munich', 'Nuremberg', 'Augsburg'],
            'FR-Île-de-France': ['Paris', 'Versailles', 'Saint-Denis'],
            'JP-Tokyo': ['Tokyo', 'Shibuya', 'Shinjuku'],
            'BR-São Paulo': ['São Paulo', 'Campinas', 'Santos'],
            'IN-Maharashtra': ['Mumbai', 'Pune', 'Nagpur'],
            'ES-Madrid': ['Madrid', 'Móstoles', 'Alcalá de Henares'],
        }
        
        cities = {}
        for state_key, city_names in cities_data.items():
            if state_key in states:
                state = states[state_key]
                for city_name in city_names:
                    city, created = City.objects.get_or_create(
                        name=city_name,
                        state=state
                    )
                    cities[f'{state_key}-{city_name}'] = city
                    if created:
                        self.stdout.write(f'Created city: {city.name}')
        
        # Create sport types
        sports_data = [
            {'name': 'Football', 'icon': 'fas fa-futbol'},
            {'name': 'Basketball', 'icon': 'fas fa-basketball-ball'},
            {'name': 'Tennis', 'icon': 'fas fa-table-tennis'},
            {'name': 'Soccer', 'icon': 'fas fa-futbol'},
            {'name': 'Baseball', 'icon': 'fas fa-baseball-ball'},
            {'name': 'Cricket', 'icon': 'fas fa-bowling-ball'},
            {'name': 'Swimming', 'icon': 'fas fa-swimmer'},
            {'name': 'Volleyball', 'icon': 'fas fa-volleyball-ball'},
            {'name': 'Badminton', 'icon': 'fas fa-shuttlecock'},
            {'name': 'Boxing', 'icon': 'fas fa-fist-raised'},
            {'name': 'Running Track', 'icon': 'fas fa-running'},
            {'name': 'Golf', 'icon': 'fas fa-golf-ball'},
        ]
        
        sport_types = {}
        for sport_data in sports_data:
            sport, created = SportType.objects.get_or_create(**sport_data)
            sport_types[sport.name] = sport
            if created:
                self.stdout.write(f'Created sport type: {sport.name}')
        
        # Create sample owner users
        owner_emails = [
            'owner1@example.com', 'owner2@example.com', 'owner3@example.com',
            'owner4@example.com', 'owner5@example.com'
        ]
        
        owners = []
        for email in owner_emails:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'Owner {email.split("@")[0][-1]}',
                    'last_name': 'Smith',
                    'user_type': 'owner',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created owner: {user.email}')
            owners.append(user)
        
        # Create sample playgrounds
        playground_names = [
            'Elite Sports Center', 'Champions Arena', 'Victory Fields', 'Premier League Complex',
            'Sports Paradise', 'Athletic Excellence Hub', 'Pro Sports Facility', 'Ultimate Play Zone',
            'Mega Sports Complex', 'Golden Gate Athletics', 'Metropolitan Sports Club', 'Riverside Sports Center',
            'Sunset Sports Arena', 'City Center Athletics', 'Northside Sports Hub', 'Southpoint Recreation',
            'Eastside Elite Sports', 'Westfield Athletic Center', 'Downtown Sports Complex', 'Uptown Athletic Club',
            'Central Park Sports', 'Harbor View Athletics', 'Mountain Peak Sports', 'Valley Sports Center',
            'Lakeside Recreation', 'Oceanfront Sports Club', 'Hilltop Athletic Center', 'Riverside Elite Sports',
            'Citywide Sports Complex', 'Metropolitan Athletic Hub'
        ]
        
        descriptions = [
            'State-of-the-art sports facility with professional-grade equipment and amenities.',
            'Premium athletic center featuring modern courts and fields for all skill levels.',
            'World-class sports complex with Olympic-standard facilities and expert coaching.',
            'Professional sports venue with top-tier amenities and excellent customer service.',
            'Modern recreational facility offering the best in sports and fitness experiences.',
        ]
        
        created_playgrounds = 0
        for i, name in enumerate(playground_names):
            if cities:
                city = random.choice(list(cities.values()))
                owner = random.choice(owners)
                sport_type = random.choice(list(sport_types.values()))
                
                playground, created = Playground.objects.get_or_create(
                    name=name,
                    defaults={
                        'owner': owner,
                        'description': random.choice(descriptions),
                        'city': city,
                        'address': f'{random.randint(100, 999)} {random.choice(["Sports", "Athletic", "Recreation", "Elite"])} Avenue',
                        'price_per_hour': Decimal(random.choice([15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 100, 120])),
                        'status': 'active',
                        'is_featured': random.choice([True, False, False, False]),  # 25% chance of being featured
                        'playground_type': random.choice(['indoor', 'outdoor', 'hybrid']),
                        'capacity': random.randint(10, 100),
                        'amenities': random.choice([
                            ['parking', 'restrooms', 'wifi'],
                            ['parking', 'changing_rooms', 'equipment_rental'],
                            ['restrooms', 'lighting', 'wifi'],
                            ['parking', 'restrooms', 'changing_rooms', 'lighting'],
                            ['wifi', 'equipment_rental', 'lighting'],
                        ]),
                        'rating': Decimal(random.uniform(3.5, 5.0)),
                        'review_count': random.randint(5, 150),
                        'total_bookings': random.randint(10, 500),
                    }
                )
                
                if created:
                    # Add sport types to the playground
                    playground.sport_types.add(sport_type)
                    # Sometimes add multiple sports
                    if random.choice([True, False]):
                        additional_sport = random.choice(list(sport_types.values()))
                        playground.sport_types.add(additional_sport)
                    
                    created_playgrounds += 1
                    self.stdout.write(f'Created playground: {playground.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(countries)} countries\n'
                f'- {len(states)} states\n'
                f'- {len(cities)} cities\n'
                f'- {len(sport_types)} sport types\n'
                f'- {len(owners)} owners\n'
                f'- {created_playgrounds} playgrounds'
            )
        )
