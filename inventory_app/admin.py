from django.contrib import admin
from .models import SparePart, AlertLog


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('part_name', 'quantity', 'threshold', 'supplier', 'updated_at', 'is_low')
    list_filter = ('supplier', 'updated_at')
    search_fields = ('part_name', 'supplier')
    ordering = ('part_name',)
    
    def is_low(self, obj):
        return obj.is_low()
    is_low.boolean = True
    is_low.short_description = 'Low Stock'


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ('part_name', 'status', 'quantity_at_alert', 'threshold_at_alert', 'alert_date', 'resolved_date')
    list_filter = ('status', 'alert_date', 'resolved_date')
    search_fields = ('part_name', 'spare_part__part_name')
    readonly_fields = ('alert_date', 'resolved_date')
    ordering = ('-alert_date',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('spare_part', 'part_name', 'status')
        }),
        ('Stock Details', {
            'fields': ('quantity_at_alert', 'threshold_at_alert', 'supplier')
        }),
        ('Email Details', {
            'fields': ('email_sent_to', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('alert_date', 'resolved_date')
        }),
    )
