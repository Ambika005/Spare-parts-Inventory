"""
Quick script to create or reset test users for the Inventory System
Run this from the project directory: python create_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_monitor.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_test_users():
    print("=" * 60)
    print("INVENTORY SYSTEM - USER SETUP")
    print("=" * 60)
    
    # Create Groups if they don't exist
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    tech_group, _ = Group.objects.get_or_create(name='Technician')
    print(f"✓ Groups created: Admin, Technician\n")
    
    # Admin User
    print("Creating/Updating Admin User...")
    admin_username = 'admin'
    admin_password = 'admin123'
    
    admin_user, created = User.objects.get_or_create(username=admin_username)
    admin_user.set_password(admin_password)
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.email = 'admin@inventory.com'
    admin_user.save()
    admin_user.groups.add(admin_group)
    
    if created:
        print(f"  ✓ Created new admin user")
    else:
        print(f"  ✓ Updated existing admin user")
    print(f"  Username: {admin_username}")
    print(f"  Password: {admin_password}")
    print(f"  Role: Admin\n")
    
    # Technician User
    print("Creating/Updating Technician User...")
    tech_username = 'tech'
    tech_password = 'tech123'
    
    tech_user, created = User.objects.get_or_create(username=tech_username)
    tech_user.set_password(tech_password)
    tech_user.is_staff = False
    tech_user.is_superuser = False
    tech_user.is_active = True
    tech_user.email = 'tech@inventory.com'
    tech_user.save()
    tech_user.groups.add(tech_group)
    
    if created:
        print(f"  ✓ Created new technician user")
    else:
        print(f"  ✓ Updated existing technician user")
    print(f"  Username: {tech_username}")
    print(f"  Password: {tech_password}")
    print(f"  Role: Technician\n")
    
    # Update existing users
    print("Checking existing users...")
    for user in User.objects.all():
        if user.username not in [admin_username, tech_username]:
            # Make sure user is active
            if not user.is_active:
                user.is_active = True
                user.save()
                print(f"  ✓ Activated user: {user.username}")
            else:
                print(f"  ✓ User '{user.username}' is active")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nYou can now login with:")
    print(f"\n  ADMIN ACCESS:")
    print(f"    Username: {admin_username}")
    print(f"    Password: {admin_password}")
    print(f"    Role: Select 'Admin' at login")
    print(f"\n  TECHNICIAN ACCESS:")
    print(f"    Username: {tech_username}")
    print(f"    Password: {tech_password}")
    print(f"    Role: Select 'Technician' at login")
    print(f"\n  OR use any existing user with role 'Technician'")
    print("\n" + "=" * 60)
    
    # List all users
    print("\nAll Users in Database:")
    print("-" * 60)
    for user in User.objects.all():
        groups_str = ", ".join([g.name for g in user.groups.all()]) or "No groups"
        status = "Active" if user.is_active else "Inactive"
        staff = "Staff" if user.is_staff else "Regular"
        print(f"  • {user.username:15} | {status:8} | {staff:8} | Groups: {groups_str}")
    print("=" * 60)

if __name__ == '__main__':
    create_test_users()
