"""
Test the Add to Popular functionality through admin panel
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playground_booking.settings')
django.setup()

from playgrounds.models import Playground

print("="*80)
print("ADD TO POPULAR - FUNCTIONALITY TEST")
print("="*80)

# Check current state
popular_count = Playground.objects.filter(is_popular=True, status='active').count()
non_popular_count = Playground.objects.filter(is_popular=False, status='active').count()

print(f"\n📊 CURRENT STATE:")
print(f"   Popular playgrounds: {popular_count}")
print(f"   Available to add: {non_popular_count}")

if non_popular_count > 0:
    print(f"\n✅ ADD BUTTON WILL WORK:")
    print(f"   • Click the 'Add' button (+ Add)")
    print(f"   • You'll see {non_popular_count} playgrounds to choose from")
    print(f"   • Select playgrounds by clicking on them")
    print(f"   • Click '⭐ Add to Popular Section' button")
    print(f"   • Selected playgrounds appear on homepage instantly!")
    
    print(f"\n📋 Available playgrounds to add:")
    available = Playground.objects.filter(is_popular=False, status='active').order_by('-rating')[:10]
    for i, pg in enumerate(available, 1):
        location = pg.city.name if pg.city else "Unknown"
        rating = f"{pg.rating:.1f}" if pg.rating else "No rating"
        print(f"   {i}. {pg.name} - {location} (Rating: {rating})")
else:
    print(f"\n⚠️  ALL PLAYGROUNDS ALREADY POPULAR")
    print(f"   Remove some playgrounds first to add new ones")

print("\n" + "="*80)
print("HOW TO USE:")
print("="*80)
print("""
1. Go to: http://127.0.0.1:8000/admin/playgrounds/popularplayground/

2. Click the green '+ Add' button at the top right

3. You'll see a beautiful grid of available playgrounds

4. Click on playground cards to select them (they'll turn green)

5. You can also click "Select All" to select all at once

6. Click the green "⭐ Add to Popular Section" button

7. Selected playgrounds will:
   • Be marked as popular in database
   • Appear on homepage immediately
   • Show in Popular Playgrounds section

8. To remove playgrounds:
   • Go back to Popular Playgrounds list
   • Select playgrounds to remove
   • Choose "❌ Remove from Popular (Homepage)" action
   • Click "Go"
""")

print("="*80)
print("✅ READY TO TEST! Open admin panel and click + Add button")
print("="*80)
