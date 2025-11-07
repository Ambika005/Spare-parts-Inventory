"""
List all users in the database with their credentials info
Run: python list_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_monitor.settings')
django.setup()

from django.contrib.auth.models import User, Group

print("=" * 80)
print("CURRENT LOGIN CREDENTIALS - Inventory Management System")
print("=" * 80)
print()

users = User.objects.all().order_by('username')

if users.count() == 0:
    print("❌ No users found in database!")
else:
    print(f"📊 Total Users: {users.count()}\n")
    
    for i, user in enumerate(users, 1):
        groups = list(user.groups.values_list('name', flat=True))
        
        print(f"👤 USER #{i}: {user.username}")
        print(f"   {'─' * 70}")
        print(f"   Status      : {'✅ Active' if user.is_active else '❌ Inactive'}")
        print(f"   Staff       : {'✅ Yes' if user.is_staff else '❌ No'}")
        print(f"   Superuser   : {'✅ Yes' if user.is_superuser else '❌ No'}")
        print(f"   Email       : {user.email or '(not set)'}")
        print(f"   Groups/Roles: {', '.join(groups) if groups else '(no groups assigned)'}")
        print(f"   Password    : {'✅ Set (hashed)' if user.has_usable_password() else '❌ Not set'}")
        print()

print("=" * 80)
print("KNOWN TEST ACCOUNT CREDENTIALS")
print("=" * 80)
print()

# Check if test accounts exist and show their credentials
test_accounts = {
    'admin': {
        'password': 'admin123',
        'role': 'Admin',
        'description': 'Full administrator access'
    },
    'tech': {
        'password': 'tech123',
        'role': 'Technician',
        'description': 'Technician with update permissions'
    },
    'Ambika': {
        'password': 'password123',
        'role': 'Admin',
        'description': 'Administrator account'
    },
    'technician': {
        'password': '(needs to be set)',
        'role': 'Technician',
        'description': 'Technician account - password not confirmed'
    }
}

for username, creds in test_accounts.items():
    user_exists = User.objects.filter(username=username).exists()
    if user_exists:
        user = User.objects.get(username=username)
        print(f"✅ Account: {username}")
        print(f"   Password: {creds['password']}")
        print(f"   Role    : {creds['role']}")
        print(f"   Status  : {'Active' if user.is_active else 'INACTIVE'}")
        print(f"   Note    : {creds['description']}")
        print()

print("=" * 80)
print("HOW TO LOGIN")
print("=" * 80)
print()
print("1. Go to: http://127.0.0.1:8000/")
print("2. Enter one of the usernames above")
print("3. Enter the corresponding password")
print("4. Select the role (Admin or Technician)")
print("5. Click Login")
print()
print("💡 Recommended for testing:")
print("   Username: admin")
print("   Password: admin123")
print("   Role: Admin")
print()
print("=" * 80)

# Show all available groups
print("\n📋 AVAILABLE GROUPS/ROLES:")
print("=" * 80)
groups = Group.objects.all()
if groups:
    for group in groups:
        member_count = group.user_set.count()
        print(f"   • {group.name}: {member_count} member(s)")
else:
    print("   (No groups created yet)")
print("=" * 80)
