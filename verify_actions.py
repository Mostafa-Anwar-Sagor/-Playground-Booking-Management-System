import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playground_booking.settings')
django.setup()

from playgrounds.admin import PlaygroundAdmin
from playgrounds.models import Playground

print("="*80)
print("VERIFYING PLAYGROUND ADMIN ACTIONS")
print("="*80)

# Get the admin class
admin_instance = PlaygroundAdmin(Playground, None)

# Get all actions
print("\n✅ Available Actions in Playground Admin:")
print("-"*80)

# List all method names that end with certain patterns or are in actions
action_methods = [method for method in dir(admin_instance) if not method.startswith('_')]
actions_list = []

# Check the actions attribute
if hasattr(admin_instance, 'actions'):
    print(f"\nDefined in 'actions' list: {admin_instance.actions}")

# Find action methods
for attr_name in action_methods:
    attr = getattr(admin_instance, attr_name)
    if callable(attr) and hasattr(attr, 'short_description'):
        actions_list.append({
            'method': attr_name,
            'description': attr.short_description
        })

print(f"\n📋 Action Methods with Descriptions:")
print("-"*80)
for action in actions_list:
    print(f"   {action['description']}")
    print(f"      Method: {action['method']}")
    print()

# Check popular-related actions specifically
print("\n⭐ Popular Playground Actions:")
print("-"*80)
popular_actions = [a for a in actions_list if 'popular' in a['method'].lower()]
for action in popular_actions:
    print(f"   ✅ {action['description']} ({action['method']})")

if not popular_actions:
    print("   ⚠️ No popular actions found!")

# Verify the methods exist
print("\n🔍 Method Verification:")
print("-"*80)
methods_to_check = ['mark_as_popular', 'unmark_as_popular', 'approve_playgrounds']
for method_name in methods_to_check:
    if hasattr(admin_instance, method_name):
        method = getattr(admin_instance, method_name)
        desc = getattr(method, 'short_description', 'No description')
        print(f"   ✅ {method_name}: {desc}")
    else:
        print(f"   ❌ {method_name}: NOT FOUND")

print("\n" + "="*80)
print("✅ VERIFICATION COMPLETE")
print("="*80)
print("\n📝 Expected Actions in Admin Dropdown:")
print("   1. ⭐ Add to Popular (Homepage)")
print("   2. ❌ Remove from Popular (Homepage)")
print("   3. ✅ Approve & Activate")
print("   4. ❌ Reject Playgrounds")
print("   5. 🚀 Auto-approve (Verified Partners)")
print("\n" + "="*80)
