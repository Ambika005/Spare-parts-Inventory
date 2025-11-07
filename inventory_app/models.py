from django.db import models
from django.utils import timezone


class SparePart(models.Model):
    part_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    threshold = models.IntegerField(default=0)
    supplier = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_low(self):
        return self.quantity <= self.threshold

    def __str__(self):
        return f"{self.part_name} ({self.quantity})"


class AlertLog(models.Model):
    """Log of low stock email alerts sent to administrators"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('RESOLVED', 'Resolved'),
    ]
    
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='alerts')
    part_name = models.CharField(max_length=200)  # Store part name for historical record
    quantity_at_alert = models.IntegerField()
    threshold_at_alert = models.IntegerField()
    supplier = models.CharField(max_length=200, blank=True)
    alert_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    email_sent_to = models.TextField(blank=True)  # JSON string of recipient emails
    error_message = models.TextField(blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-alert_date']
        verbose_name = 'Alert Log'
        verbose_name_plural = 'Alert Logs'
    
    def __str__(self):
        return f"Alert: {self.part_name} - {self.status} ({self.alert_date.strftime('%Y-%m-%d %H:%M')})"
    
    def mark_resolved(self):
        """Mark this alert as resolved when stock is replenished"""
        self.status = 'RESOLVED'
        self.resolved_date = timezone.now()
        self.save()


class DailyAlertLog(models.Model):
    """Track daily automated email alerts to prevent duplicates"""
    
    alert_date = models.DateField(default=timezone.now)
    sent_at = models.DateTimeField(auto_now_add=True)
    low_stock_count = models.IntegerField(default=0)
    recipients = models.TextField()  # JSON string of recipient emails
    email_sent_successfully = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-alert_date']
        verbose_name = 'Daily Alert Log'
        verbose_name_plural = 'Daily Alert Logs'
        # Ensure only one alert per day
        constraints = [
            models.UniqueConstraint(fields=['alert_date'], name='unique_daily_alert')
        ]
    
    def __str__(self):
        return f"Daily Alert: {self.alert_date} - {self.low_stock_count} low stock items"
