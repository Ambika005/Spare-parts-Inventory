"""
Test Email Alert System
Run this script to test the email alert functionality
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_monitor.settings')
django.setup()

from inventory_app.models import SparePart, AlertLog
from inventory_app.services import AlertService

def demo_alert_system():
    print("=" * 60)
    print("SPARE PARTS INVENTORY - EMAIL ALERT SYSTEM DEMO")
    print("=" * 60)
    
    # Create a sample low stock part for demonstration
    test_part, created = SparePart.objects.get_or_create(
        part_name="Demo Test Bearing",
        defaults={
            'quantity': 2,
            'threshold': 10,
            'supplier': 'Test Supplier Corp'
        }
    )
    
    if created:
        print(f"✓ Created test part: {test_part.part_name}")
    else:
        print(f"✓ Using existing test part: {test_part.part_name}")
    
    print(f"  - Current Quantity: {test_part.quantity}")
    print(f"  - Threshold: {test_part.threshold}")
    print(f"  - Is Low Stock: {test_part.is_low()}")
    
    # Test the alert system
    print("\n" + "-" * 40)
    print("TESTING ALERT SYSTEM")
    print("-" * 40)
    
    if test_part.is_low():
        alert_sent = AlertService.check_and_send_alert(test_part)
        if alert_sent:
            print("✓ Email alert would be sent (if email is configured)")
        else:
            print("ℹ Alert not sent (duplicate prevention or not low stock)")
    else:
        print("ℹ Part is not low stock, no alert needed")
    
    # Show alert logs
    print("\n" + "-" * 40)
    print("ALERT LOG HISTORY")
    print("-" * 40)
    
    alerts = AlertLog.objects.filter(spare_part=test_part).order_by('-alert_date')
    
    if alerts.exists():
        for alert in alerts[:3]:  # Show last 3 alerts
            print(f"• {alert.alert_date.strftime('%Y-%m-%d %H:%M')} - {alert.get_status_display()}")
            print(f"  Qty: {alert.quantity_at_alert}, Threshold: {alert.threshold_at_alert}")
    else:
        print("No alert history found for this part")
    
    # Test email configuration (without actually sending)
    print("\n" + "-" * 40)
    print("EMAIL CONFIGURATION STATUS")
    print("-" * 40)
    
    from django.conf import settings
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"TLS Enabled: {settings.EMAIL_USE_TLS}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Alert Recipients: {getattr(settings, 'ALERT_RECIPIENTS', ['Not configured'])}")
    
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS:")
    print("=" * 60)
    print("1. Set environment variables:")
    print("   EMAIL_HOST_USER=your_gmail@gmail.com")
    print("   EMAIL_HOST_PASSWORD=your_gmail_app_password")
    print("")
    print("2. Update ALERT_RECIPIENTS in settings.py with real email addresses")
    print("")
    print("3. Test email by visiting: http://127.0.0.1:8000/test-email/")
    print("")
    print("4. Create/update spare parts through the web interface")
    print("   to trigger automatic low stock alerts")
    print("=" * 60)

if __name__ == "__main__":
    demo_alert_system()