# ⏰ **WHEN YOU'LL RECEIVE AUTOMATIC EMAILS**

## 📧 Email Schedule Summary

Once configured, you will receive:
- **Daily emails at 9:00 AM** (or your chosen time)
- **365 emails per year** (one every day)
- **Subject:** `📦 Daily Stock Alert — [Current Date]`
- **Content:** List of low stock items OR "All stocks healthy" message

---

## 🪟 **Setup for Windows (BEST METHOD)**

Since you're on Windows, use **Windows Task Scheduler** (django-crontab doesn't work on Windows).

### **Step-by-Step Setup:**

#### **Step 1: Test the Command First**

Before automating, verify it works manually:

```powershell
python manage.py send_daily_stock_alert
```

✅ **Expected:** You should receive an email within seconds at `ambikaselvaraj22@gmail.com`

---

#### **Step 2: Create Windows Task Scheduler Job**

1. **Open Task Scheduler:**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create Basic Task:**
   - Click **"Create Basic Task"** in the right panel
   - Name: `Django Daily Stock Alert`
   - Description: `Send daily inventory stock report email`
   - Click **Next**

3. **Set Trigger (When to run):**
   - Select: **"Daily"**
   - Click **Next**
   - Start date: Select today's date
   - **Start time: 9:00 AM** (or your preferred time)
   - Recur every: **1 days**
   - Click **Next**

4. **Set Action (What to run):**
   - Select: **"Start a program"**
   - Click **Next**
   - Program/script: **Browse** to: `C:\Users\shanm\Desktop\Inventory\run_daily_alert.bat`
   - Start in: `C:\Users\shanm\Desktop\Inventory`
   - Click **Next**

5. **Finish Setup:**
   - Check: **"Open the Properties dialog for this task when I click Finish"**
   - Click **Finish**

6. **Configure Additional Settings:**
   - In the Properties dialog:
   - **General tab:**
     - Select: **"Run whether user is logged on or not"**
     - Check: **"Run with highest privileges"**
   - **Conditions tab:**
     - Uncheck: **"Start the task only if the computer is on AC power"**
   - **Settings tab:**
     - Check: **"Run task as soon as possible after a scheduled start is missed"**
   - Click **OK**
   - Enter your Windows password when prompted

---

#### **Step 3: Test the Scheduled Task**

1. In Task Scheduler, find your task: `Django Daily Stock Alert`
2. Right-click → **Run**
3. Check your email inbox: `ambikaselvaraj22@gmail.com`

✅ **If you receive the email, automation is working!**

---

## ⏰ **When Will Emails Be Sent?**

### **Default Schedule:**
- **Time:** 9:00 AM every day
- **Frequency:** Daily (7 days a week)
- **Timezone:** Your local computer time

### **You'll Receive Email:**
- ✅ Monday 9:00 AM
- ✅ Tuesday 9:00 AM
- ✅ Wednesday 9:00 AM
- ✅ Thursday 9:00 AM
- ✅ Friday 9:00 AM
- ✅ Saturday 9:00 AM
- ✅ Sunday 9:00 AM

### **Customization Options:**

**Change Time:**
- Edit the task → Triggers → Change start time
- Example: Set to 6:00 PM for evening reports

**Change Frequency:**
- Weekdays only: In Triggers, click "New" → Select "Weekly" → Check Mon-Fri only
- Twice daily: Create two tasks (one at 9:00 AM, one at 6:00 PM)
- Every 12 hours: Triggers → Advanced → Repeat every 12 hours

---

## 📊 **What You'll Receive**

### **Example 1: When Items Are Low Stock**

```
From: ambikaselvaraj22@gmail.com
To: ambikaselvaraj22@gmail.com
Subject: 📦 Daily Stock Alert — November 08, 2025

Hello,

This is your daily inventory stock report for November 08, 2025.

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

### **Example 2: When All Stocks Are Healthy**

```
From: ambikaselvaraj22@gmail.com
To: ambikaselvaraj22@gmail.com
Subject: 📦 Daily Stock Alert — November 08, 2025

Hello,

This is your daily inventory stock report for November 08, 2025.

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

## 🔍 **Verify It's Working**

### **Check Task Scheduler:**
1. Open Task Scheduler
2. Find: `Django Daily Stock Alert`
3. Look at:
   - **Last Run Time:** Should show execution time
   - **Last Run Result:** Should be `(0x0)` = Success
   - **Next Run Time:** Shows when it will run next

### **Check Email Logs:**

```powershell
python manage.py shell
```

```python
from inventory_app.models import DailyAlertLog

# View recent daily alerts
for log in DailyAlertLog.objects.all()[:7]:
    print(f"{log.alert_date}: {log.low_stock_count} low stock")
    print(f"   Success: {log.email_sent_successfully}")
```

### **Check Log File:**

Open: `C:\Users\shanm\Desktop\Inventory\daily_alert_log.txt`

This file logs every execution with timestamp.

---

## ⚠️ **Important Notes**

### **Email Frequency:**
- **Only ONE email per day** (duplicate prevention built-in)
- Even if you manually run the command multiple times, only one email is sent per day
- Resets at midnight for the next day's email

### **Computer Must Be On:**
- Windows Task Scheduler requires your computer to be running
- If computer is off at 9:00 AM, the task will run when you turn it on (if configured in Settings)

### **Django Server Doesn't Need to Run:**
- The scheduled task runs independently
- Django server at `http://localhost:8000` does NOT need to be running
- Only the database and Python environment are needed

---

## 🎯 **Quick Summary**

| Question | Answer |
|----------|--------|
| **When will I receive emails?** | Every day at 9:00 AM (your local time) |
| **How many per day?** | Exactly 1 email per day |
| **What if stocks are healthy?** | You still get an email saying "All stocks healthy" |
| **Does Django need to run?** | No, Task Scheduler runs it independently |
| **Can I change the time?** | Yes, edit the scheduled task |
| **Weekdays only?** | Yes, configure in Task Scheduler triggers |
| **Can I test it now?** | Yes! Right-click task → Run |

---

## 🚀 **Next Steps**

1. ✅ Test manually first:
   ```powershell
   python manage.py send_daily_stock_alert
   ```

2. ✅ Set up Windows Task Scheduler (follow steps above)

3. ✅ Test the scheduled task (right-click → Run)

4. ✅ Wait until tomorrow at 9:00 AM to confirm automatic execution

5. ✅ Check your email inbox daily!

---

## 📧 **Expected Timeline**

- **Today:** Set up Task Scheduler
- **Tomorrow at 9:00 AM:** First automatic email arrives
- **Every day at 9:00 AM:** Ongoing automatic emails
- **Forever:** Continues until you disable the task

---

**You're all set! Tomorrow at 9:00 AM, you'll receive your first automatic email!** 🎉

**To verify it's working:** Check Task Scheduler's "Last Run Time" tomorrow after 9:00 AM.
