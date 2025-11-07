"""
Django management command to send daily stock alert emails
Run with: python manage.py send_daily_stock_alert
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from inventory_app.models import SparePart, DailyAlertLog
from inventory_app.services import AlertService
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send daily stock alert email to admins'

    def handle(self, *args, **options):
        """
        Check inventory and send daily stock summary email
        """
        try:
            # Get current date
            today = timezone.now().date()
            current_date = timezone.now().strftime('%B %d, %Y')
            
            # Check if alert already sent today
            if DailyAlertLog.objects.filter(alert_date=today).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ Daily alert already sent for {current_date}. Skipping.'
                    )
                )
                logger.info(f'Daily alert already sent for {today}')
                return
            
            # Get all low stock items (quantity < threshold)
            low_stock_parts = SparePart.objects.filter(
                quantity__lt=F('threshold')
            ).order_by('part_name')
            
            low_stock_count = low_stock_parts.count()
            
            # Get admin email addresses
            recipients = AlertService._get_admin_email_addresses()
            
            if not recipients:
                self.stdout.write(self.style.ERROR('No admin email addresses found!'))
                logger.error('No admin email addresses configured for daily alerts')
                
                # Log failed attempt
                DailyAlertLog.objects.create(
                    alert_date=today,
                    low_stock_count=low_stock_count,
                    recipients=json.dumps([]),
                    email_sent_successfully=False,
                    error_message='No admin email addresses configured'
                )
                return
            
            # Prepare email content
            subject = f'📦 Daily Stock Alert — {current_date}'
            
            if low_stock_count > 0:
                # Build email body with low stock items
                message_lines = [
                    'Hello,',
                    '',
                    f'This is your daily inventory stock report for {current_date}.',
                    '',
                    f'⚠️ ATTENTION REQUIRED: {low_stock_count} item{"s" if low_stock_count > 1 else ""} below minimum threshold',
                    '',
                    'Low Stock Items:',
                    '─────────────────────────────────────────────────────────',
                ]
                
                for part in low_stock_parts:
                    message_lines.append(
                        f'📦 {part.part_name} — Quantity: {part.quantity} (Threshold: {part.threshold})'
                    )
                    if part.supplier:
                        message_lines.append(f'   Supplier: {part.supplier}')
                    message_lines.append('')
                
                message_lines.extend([
                    '─────────────────────────────────────────────────────────',
                    '',
                    'Action Required:',
                    '• Review these items in your inventory dashboard',
                    '• Contact suppliers for restocking',
                    '• Prioritize critical parts for immediate ordering',
                    '',
                    '---',
                    'This is an automated daily report from Spare Parts Inventory System.',
                    f'Sent to: {", ".join(recipients)}',
                ])
                
                message = '\n'.join(message_lines)
                
            else:
                # All stocks are healthy
                message = f"""
Hello,

This is your daily inventory stock report for {current_date}.

✅ All stock levels are healthy today ✅

No items are currently below their minimum threshold levels.
All spare parts inventory is adequately stocked.

Current Status:
• Total parts in inventory: {SparePart.objects.count()}
• Low stock items: 0
• Status: All systems normal

---
This is an automated daily report from Spare Parts Inventory System.
Sent to: {", ".join(recipients)}
                """.strip()
            
            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            # Log successful send
            DailyAlertLog.objects.create(
                alert_date=today,
                low_stock_count=low_stock_count,
                recipients=json.dumps(recipients),
                email_sent_successfully=True
            )
            
            # Log success
            if low_stock_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Daily alert sent! {low_stock_count} low stock items reported to {len(recipients)} admin(s)'
                    )
                )
                logger.info(f'Daily stock alert sent: {low_stock_count} low stock items')
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Daily alert sent! All stocks healthy. Email sent to {len(recipients)} admin(s)'
                    )
                )
                logger.info('Daily stock alert sent: All stocks healthy')
            
        except Exception as e:
            error_msg = f'Failed to send daily stock alert: {str(e)}'
            self.stdout.write(self.style.ERROR(f'❌ {error_msg}'))
            logger.error(error_msg)
            
            # Log failed attempt
            try:
                DailyAlertLog.objects.create(
                    alert_date=timezone.now().date(),
                    low_stock_count=low_stock_count if 'low_stock_count' in locals() else 0,
                    recipients=json.dumps(recipients if 'recipients' in locals() else []),
                    email_sent_successfully=False,
                    error_message=str(e)
                )
            except Exception:
                pass
            
            raise
