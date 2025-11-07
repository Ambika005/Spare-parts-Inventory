"""
Test script to verify import functionality works correctly
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_monitor.settings')
django.setup()

from inventory_app.models import SparePart

def test_import_functionality():
    print("Testing Import Functionality")
    print("=" * 40)
    
    # Check current parts count
    initial_count = SparePart.objects.count()
    print(f"Initial parts count: {initial_count}")
    
    # Display first few parts
    print("\nCurrent parts in database:")
    for part in SparePart.objects.all()[:10]:
        print(f"  - {part.part_name}: {part.quantity} (threshold: {part.threshold})")
    
    print(f"\nTotal parts in database: {SparePart.objects.count()}")
    print(f"Low stock parts: {SparePart.objects.filter(quantity__lte=django.db.models.F('threshold')).count()}")

if __name__ == "__main__":
    test_import_functionality()