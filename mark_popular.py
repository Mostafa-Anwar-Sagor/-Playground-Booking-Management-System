import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playground_booking.settings')
django.setup()

from playgrounds.models import Playground

# Mark top 5 playgrounds as popular
print("=" * 80)
print("MARKING TOP PLAYGROUNDS AS POPULAR")
print("=" * 80)

playgrounds = Playground.objects.filter(status='active').order_by('-rating')[:5]
print(f"\nFound {playgrounds.count()} top-rated playgrounds")
print("\nMarking as POPULAR:")

for p in playgrounds:
    p.is_popular = True
    p.save()
    location = p.city.name if p.city else "N/A"
    print(f"  ⭐ {p.name}")
    print(f"     Rating: {p.rating}")
    print(f"     Location: {location}")
    print()

print("\n" + "=" * 80)
print("VERIFICATION - All Popular Playgrounds:")
print("=" * 80)

popular = Playground.objects.filter(is_popular=True, status='active').select_related('city__state__country')
print(f"\nTotal Popular: {popular.count()}")

for i, p in enumerate(popular, 1):
    country = p.city.state.country if (p.city and p.city.state and p.city.state.country) else None
    currency = country.get_currency() if country else 'N/A'
    
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'MYR': 'RM', 'SGD': 'S$',
        'INR': '₹', 'BDT': '৳', 'AUD': 'A$', 'CAD': 'C$'
    }
    symbol = symbols.get(currency, currency)
    
    print(f"\n{i}. {p.name}")
    print(f"   Location: {p.city.name if p.city else 'N/A'}, {country.name if country else 'N/A'}")
    print(f"   Price: {symbol}{p.price_per_hour}/hour")
    print(f"   Rating: {p.rating if p.rating else 'Not rated'}")

print("\n✅ These playgrounds will now appear on the homepage!")
print("=" * 80)
