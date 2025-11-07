"""
Email Alert Service for Low Stock Notifications
"""
import json
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import SparePart, AlertLog

logger = logging.getLogger(__name__)


class AlertService:
    """Service class for handling low stock email alerts"""
    
    @staticmethod
    def check_and_send_alert(spare_part):
        """
        Check if a spare part needs an alert and send it if necessary.
        Prevents duplicate alerts by checking recent alert history.
        
        Args:
            spare_part (SparePart): The spare part to check
            
        Returns:
            bool: True if alert was sent, False otherwise
        """
        if not spare_part.is_low():
            # Part is not low stock, resolve any existing pending alerts
            AlertService._resolve_alerts_for_part(spare_part)
            return False
        
        # Check if we already have a recent unresolved alert for this part
        recent_alert = AlertLog.objects.filter(
            spare_part=spare_part,
            status__in=['PENDING', 'SENT']
        ).first()
        
        if recent_alert:
            logger.info(f"Skipping duplicate alert for {spare_part.part_name}")
            return False
        
        # Create alert log entry
        alert_log = AlertLog.objects.create(
            spare_part=spare_part,
            part_name=spare_part.part_name,
            quantity_at_alert=spare_part.quantity,
            threshold_at_alert=spare_part.threshold,
            supplier=spare_part.supplier,
        )
        
        # Send the email alert
        success = AlertService._send_low_stock_email(spare_part, alert_log)
        
        if success:
            alert_log.status = 'SENT'
            alert_log.email_sent_to = json.dumps(settings.ALERT_RECIPIENTS)
        else:
            alert_log.status = 'FAILED'
            
        alert_log.save()
        return success
    
    @staticmethod
    def _get_admin_email_addresses():
        """
        Get email addresses of all users in the Admin group
        
        Returns:
            list: List of admin email addresses
        """
        from django.contrib.auth.models import Group, User
        
        try:
            admin_group = Group.objects.get(name='Admin')
            admin_users = admin_group.user_set.filter(is_active=True, email__isnull=False).exclude(email='')
            
            admin_emails = [user.email for user in admin_users if user.email]
            
            # Fallback to superusers if no admin group emails found
            if not admin_emails:
                superuser_emails = User.objects.filter(
                    is_superuser=True, 
                    is_active=True, 
                    email__isnull=False
                ).exclude(email='').values_list('email', flat=True)
                admin_emails = list(superuser_emails)
            
            # Final fallback to settings if no user emails found
            if not admin_emails:
                admin_emails = getattr(settings, 'ALERT_RECIPIENTS', ['admin@company.com'])
            
            return admin_emails
            
        except Group.DoesNotExist:
            logger.warning("Admin group not found, using superuser emails")
            superuser_emails = User.objects.filter(
                is_superuser=True, 
                is_active=True, 
                email__isnull=False
            ).exclude(email='').values_list('email', flat=True)
            return list(superuser_emails) if superuser_emails else getattr(settings, 'ALERT_RECIPIENTS', ['admin@company.com'])

    @staticmethod
    def _send_low_stock_email(spare_part, alert_log):
        """
        Send low stock email notification
        
        Args:
            spare_part (SparePart): The spare part that's low on stock
            alert_log (AlertLog): The alert log entry
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            subject = f"⚠ Low Stock Alert: {spare_part.part_name}"
            
            # Email body content
            message = f"""
URGENT: LOW STOCK ALERT

Part Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Part Name: {spare_part.part_name}
Current Quantity: {spare_part.quantity}
Minimum Threshold: {spare_part.threshold}
Supplier Name: {spare_part.supplier or 'Not specified'}
Last Updated: {spare_part.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

SUGGESTED ACTION:
Please restock this item as soon as possible.

Alert Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alert ID: {alert_log.id}
Alert Time: {alert_log.alert_date.strftime('%Y-%m-%d %H:%M:%S')}

This is an automated message from the Spare Parts Inventory System.
Please do not reply to this email.
            """.strip()
            
            # Get recipient list from admin users
            recipients = AlertService._get_admin_email_addresses()
            
            if not recipients:
                logger.error("No admin email addresses found for sending alerts")
                alert_log.error_message = "No admin email addresses configured"
                alert_log.save()
                return False
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            logger.info(f"Low stock alert sent successfully for {spare_part.part_name} to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            error_msg = f"Failed to send email alert for {spare_part.part_name}: {str(e)}"
            logger.error(error_msg)
            alert_log.error_message = str(e)
            alert_log.save()
            return False
    
    @staticmethod
    def _resolve_alerts_for_part(spare_part):
        """
        Mark all pending/sent alerts as resolved for a part that's no longer low stock
        
        Args:
            spare_part (SparePart): The spare part that's been restocked
        """
        unresolved_alerts = AlertLog.objects.filter(
            spare_part=spare_part,
            status__in=['PENDING', 'SENT']
        )
        
        for alert in unresolved_alerts:
            alert.mark_resolved()
            logger.info(f"Resolved alert {alert.id} for {spare_part.part_name}")
    
    @staticmethod
    def get_active_alerts():
        """
        Get all active (unresolved) alerts
        
        Returns:
            QuerySet: Active AlertLog entries
        """
        return AlertLog.objects.filter(
            status__in=['PENDING', 'SENT']
        ).select_related('spare_part')
    
    @staticmethod
    def get_recent_alerts(days=7):
        """
        Get recent alerts within specified days
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            QuerySet: Recent AlertLog entries
        """
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return AlertLog.objects.filter(
            alert_date__gte=cutoff_date
        ).select_related('spare_part')
    
    @staticmethod
    def test_email_configuration():
        """
        Test email configuration by sending a test email
        
        Returns:
            tuple: (success: bool, message: str, recipients: list)
        """
        try:
            # Check basic configuration first
            config_issues = AlertService._validate_email_configuration()
            if config_issues:
                return False, f"Configuration issues found: {'; '.join(config_issues)}", []
            
            # Get admin email addresses
            recipients = AlertService._get_admin_email_addresses()
            
            if not recipients:
                return False, "No admin email addresses found. Please ensure admin users have email addresses configured.", []
            
            test_subject = "Test Email - Spare Parts Inventory System"
            test_message = """
This is a test email from the Spare Parts Inventory System.

If you receive this message, your email configuration is working correctly.

Email Configuration Details:
- Host: {host}
- Port: {port}
- TLS: {tls}
- From: {from_email}
- Recipients: {recipients}

Timestamp: {timestamp}

Note: This test email was sent to all active admin users with configured email addresses.
            """.format(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                tls=settings.EMAIL_USE_TLS,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipients=', '.join(recipients),
                timestamp=timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            ).strip()
            
            send_mail(
                subject=test_subject,
                message=test_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            return True, f"Test email sent successfully to {len(recipients)} admin(s)!", recipients
            
        except Exception as e:
            error_message = AlertService._parse_email_error(str(e))
            return False, error_message, []
    
    @staticmethod
    def _validate_email_configuration():
        """
        Validate email configuration settings
        
        Returns:
            list: List of configuration issues found
        """
        issues = []
        
        # Check if EMAIL_HOST_USER is configured
        if not getattr(settings, 'EMAIL_HOST_USER', None) or settings.EMAIL_HOST_USER in ['your_gmail_id@gmail.com', '']:
            issues.append("EMAIL_HOST_USER not configured properly")
        
        # Check if EMAIL_HOST_PASSWORD is configured
        if not getattr(settings, 'EMAIL_HOST_PASSWORD', None) or settings.EMAIL_HOST_PASSWORD in ['your_app_password', '']:
            issues.append("EMAIL_HOST_PASSWORD not configured properly")
        
        # Check if DEFAULT_FROM_EMAIL is configured
        if not getattr(settings, 'DEFAULT_FROM_EMAIL', None):
            issues.append("DEFAULT_FROM_EMAIL not configured")
        
        return issues
    
    @staticmethod
    def _parse_email_error(error_str):
        """
        Parse email errors and provide user-friendly messages
        
        Args:
            error_str (str): The original error message
            
        Returns:
            str: User-friendly error message with troubleshooting tips
        """
        error_lower = error_str.lower()
        
        if '535' in error_str and 'username and password not accepted' in error_lower:
            return """Gmail Authentication Failed! 

Common solutions:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate a Gmail App Password (not your regular password)
3. Use the App Password in EMAIL_HOST_PASSWORD environment variable
4. Make sure EMAIL_HOST_USER is your full Gmail address

Steps to create App Password:
• Go to Google Account settings → Security → 2-Step Verification → App passwords
• Generate a new app password for 'Mail'
• Use this 16-character password (no spaces) as EMAIL_HOST_PASSWORD

Original error: """ + error_str
        
        elif 'connection refused' in error_lower or 'network' in error_lower:
            return f"Network connection failed. Check your internet connection and firewall settings. Original error: {error_str}"
        
        elif 'timeout' in error_lower:
            return f"Connection timeout. This might be due to network issues or Gmail server problems. Original error: {error_str}"
        
        elif 'authentication failed' in error_lower:
            return f"Gmail authentication failed. Please check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings. Original error: {error_str}"
        
        else:
            return f"Email configuration error: {error_str}"