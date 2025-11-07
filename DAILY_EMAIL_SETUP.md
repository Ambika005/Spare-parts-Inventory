# 📧 Automated Daily Email Alerts - Setup Guide

## ✅ What's Been Implemented

Your Django inventory system now has **automated daily email alerts** that:

1. ✅ Check inventory every day
2. ✅ Send email listing low stock items (quantity < threshold)
3. ✅ Send "All stocks healthy" message if nothing is low
4. ✅ Prevents duplicate emails (only one per day)
5. ✅ Logs all sent emails with timestamps
6. ✅ Sends to admin users automatically

---

## 📋 Components Created

### 1. **Django Management Command**
- **File:** `inventory_app/management/commands/send_daily_stock_alert.py`
- **Purpose:** Checks inventory and sends email
- **Run manually:** `python manage.py send_daily_stock_alert`

### 2. **DailyAlertLog Model**
- **Purpose:** Tracks when daily emails are sent
- **Features:** Prevents duplicate emails on same day
- **Database:** Already migrated and ready to use

---

## 🧪 Test It Now (Manual Run)

Before setting up automation, test the command manually:

```powershell
python manage.py send_daily_stock_alert
```

**Expected Output:**
- If you have low stock items: "✅ Daily alert sent! X low stock items reported"
- If all stocks are healthy: "✅ Daily alert sent! All stocks healthy"

**Check Your Email:** `ambikaselvaraj22@gmail.com`

---

## ⚙️ Automation Options

### **Option 1: Using django-crontab (Recommended for Development)**

#### Step 1: Install django-crontab
```powershell
pip install django-crontab
```

#### Step 2: Add to settings.py
Open `inventory_monitor/settings.py` and add:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_crontab',
]

# Cron jobs configuration
CRONJOBS = [
    # Run daily at 9:00 AM
    ('0 9 * * *', 'django.core.management.call_command', ['send_daily_stock_alert']),
]
```

#### Step 3: Add the cron job
```powershell
python manage.py crontab add
```

#### Step 4: View active cron jobs
```powershell
python manage.py crontab show
```

#### Step 5: Remove cron job (if needed)
```powershell
python manage.py crontab remove
```

---

### **Option 2: Using Windows Task Scheduler (Best for Windows Production)**

#### Step 1: Create a batch file
Create `run_daily_alert.bat` in your project folder:

```batch
@echo off
cd C:\Users\shanm\Desktop\Inventory
python manage.py send_daily_stock_alert
```

#### Step 2: Open Task Scheduler
1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **"Create Basic Task"**
3. Name: "Django Daily Stock Alert"
4. Description: "Send daily inventory email"

#### Step 3: Set Trigger
- Select **"Daily"**
- Set time: **9:00 AM** (or your preferred time)
- Start date: Today

#### Step 4: Set Action
- Action: **"Start a program"**
- Program/script: Browse to `run_daily_alert.bat`
- Start in: `C:\Users\shanm\Desktop\Inventory`

#### Step 5: Finish
- Check "Open Properties dialog"
- Under "General" tab, select **"Run whether user is logged on or not"**
- Click OK and enter your Windows password

---

### **Option 3: Using Standard Cron (Linux/Mac)**

Add to crontab:
```bash
crontab -e
```

Add this line:
```bash
0 9 * * * cd /path/to/Inventory && /path/to/python manage.py send_daily_stock_alert
```

---

## 📧 Email Content Examples

### **When Low Stock Items Exist:**

```
Subject: 📦 Daily Stock Alert — November 07, 2025

Hello,

This is your daily inventory stock report for November 07, 2025.

⚠️ ATTENTION REQUIRED: 3 items below minimum threshold

Low Stock Items:
─────────────────────────────────────────────────────────
📦 Brake Pads — Quantity: 5 (Threshold: 10)
   Supplier: ABC Auto Parts

📦 Oil Filter — Quantity: 3 (Threshold: 15)
   Supplier: XYZ Suppliers

📦 Air Filter — Quantity: 2 (Threshold: 8)

─────────────────────────────────────────────────────────

Action Required:
• Review these items in your inventory dashboard
• Contact suppliers for restocking
• Prioritize critical parts for immediate ordering

---
This is an automated daily report from Spare Parts Inventory System.
Sent to: ambikaselvaraj22@gmail.com
```

### **When All Stocks Are Healthy:**

```
Subject: 📦 Daily Stock Alert — November 07, 2025

Hello,

This is your daily inventory stock report for November 07, 2025.

✅ All stock levels are healthy today ✅

No items are currently below their minimum threshold levels.
All spare parts inventory is adequately stocked.

Current Status:
• Total parts in inventory: 25
• Low stock items: 0
• Status: All systems normal

---
This is an automated daily report from Spare Parts Inventory System.
Sent to: ambikaselvaraj22@gmail.com
```

---

## 🔧 Customization Options

### **Change Email Time**

Edit the cron schedule:
- `0 9 * * *` = 9:00 AM daily
- `0 18 * * *` = 6:00 PM daily
- `30 8 * * *` = 8:30 AM daily
- `0 9 * * 1-5` = 9:00 AM weekdays only

### **Change Email Recipients**

The system automatically sends to all users in the "Admin" group who have email addresses configured.

To add more recipients:
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Users → Select user
3. Add email address
4. Add to "Admin" group

---

## 📊 View Email Logs

Check when emails were sent:

```python
python manage.py shell
```

```python
from inventory_app.models import DailyAlertLog

# View all daily alerts
for log in DailyAlertLog.objects.all():
    print(f"{log.alert_date}: {log.low_stock_count} low stock items")
    print(f"   Sent: {log.email_sent_successfully}")
    print(f"   Recipients: {log.recipients}")
    print()
```

Or view in Django Admin:
`http://localhost:8000/admin/inventory_app/dailyalertlog/`

---

## 🔍 Troubleshooting

### **"Daily alert already sent for today"**
- This is normal! It prevents duplicate emails
- The system only sends one email per day
- To test again, wait until tomorrow OR delete today's log:

```python
python manage.py shell
```

```python
from inventory_app.models import DailyAlertLog
from django.utils import timezone

# Delete today's log (for testing only!)
DailyAlertLog.objects.filter(alert_date=timezone.now().date()).delete()
```

### **"No admin email addresses found"**
- Add email to admin user in Django Admin
- Ensure user is in "Admin" group
- Check `.env` file has EMAIL_HOST_USER configured

### **Email not sending**
- Test Gmail configuration: `http://localhost:8000/send-low-stock-email/`
- Check `.env` file has correct App Password (no spaces!)
- Restart Django server after changing `.env`

---

## ✅ Quick Start Checklist

- [ ] Test manually: `python manage.py send_daily_stock_alert`
- [ ] Check email inbox for the daily report
- [ ] Choose automation method (django-crontab or Task Scheduler)
- [ ] Set up daily schedule (9:00 AM recommended)
- [ ] Verify automation is working tomorrow
- [ ] Add email addresses to other admin users if needed

---

## 📝 Important Notes

1. **One Email Per Day:** The system prevents duplicate emails on the same day
2. **Admin Recipients:** Only users in "Admin" group with email addresses receive alerts
3. **Low Stock Definition:** Items where `quantity < threshold`
4. **Healthy Stock Message:** Sent even when no items are low stock
5. **Email Logging:** All sent emails are tracked in `DailyAlertLog` model

---

## 🎯 Summary

✅ **Automated daily email system is ready!**

- Checks inventory daily
- Lists all low stock items OR confirms healthy stocks
- Prevents duplicate emails
- Logs all activity
- Sends to admin users automatically

**Test it now:**
```powershell
python manage.py send_daily_stock_alert
```

Then check your email at: **ambikaselvaraj22@gmail.com** 📧

---

**Need help?** Review the troubleshooting section or test the Gmail configuration first!
