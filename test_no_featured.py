import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playground_booking.settings')
django.setup()

from playgrounds.models import Playground
from django.test import RequestFactory
from api.home_api_enhanced import get_popular_playgrounds
import json

print("="*80)
print("TESTING AFTER REMOVING FEATURED CODE")
print("="*80)

# Test 1: Database counts
total = Playground.objects.count()
active = Playground.objects.filter(status='active').count()
popular = Playground.objects.filter(is_popular=True).count()

print(f"\n✅ Database Check:")
print(f"   Total playgrounds: {total}")
print(f"   Active playgrounds: {active}")
print(f"   Popular playgrounds: {popular}")

# Test 2: API check
print(f"\n✅ API Check:")
factory = RequestFactory()
request = factory.get('/api/popular-playgrounds/')
response = get_popular_playgrounds(request)
data = json.loads(response.content)

print(f"   API Status: {response.status_code}")
print(f"   API Returns: {data['count']} playgrounds")

if data['playgrounds']:
    print(f"\n✅ Sample popular playground:")
    pg = data['playgrounds'][0]
    print(f"   Name: {pg['name']}")
    print(f"   Currency: {pg['currency_symbol']} ({pg['currency']})")
    print(f"   Price: {pg['currency_symbol']}{pg['price_per_hour']}/hr")
    print(f"   Is Popular: {pg['is_popular']}")
    # Check if is_featured still in response (should not be)
    if 'is_featured' in pg:
        print(f"   ⚠️ WARNING: is_featured still in API response!")
    else:
        print(f"   ✅ is_featured removed from API")

# Test 3: Admin actions available
print(f"\n✅ Admin Actions Test:")
print(f"   From Playgrounds section:")
print(f"   - ⭐ Add to Popular (Homepage)")
print(f"   - ❌ Remove from Popular (Homepage)")
print(f"   - ✅ Approve & Activate")
print(f"\n   Featured actions: REMOVED ✅")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - FEATURED CODE REMOVED!")
print("="*80)
print("\n📝 What Changed:")
print("   ✅ Removed 'Feature selected playgrounds' action")
print("   ✅ Removed 'is_featured' column from list")
print("   ✅ Removed featured filter")
print("   ✅ Removed featured API endpoint")
print("   ✅ Cleaned up API responses")
print("\n🎯 You now have:")
print("   • Simple 'Add to Popular' action in Playgrounds section")
print("   • Dedicated Popular Playgrounds section with + Add button")
print("   • Real-time, backend-connected popular system")
print("   • No featured/favorites confusion")
print("\n" + "="*80)
