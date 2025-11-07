@echo off
REM Daily Stock Alert Batch Script
REM This script runs the Django management command to send daily email alerts

cd /d C:\Users\shanm\Desktop\Inventory
python manage.py send_daily_stock_alert

REM Optional: Log the execution
echo Daily alert executed at %date% %time% >> daily_alert_log.txt
