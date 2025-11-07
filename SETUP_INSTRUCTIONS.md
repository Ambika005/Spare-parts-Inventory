# 📧 QUICK START: Gmail Setup for Email Alerts

## ✅ What You Need to Do

### Step 1: Edit the .env File (Already Created!)

I've created a `.env` file at: `C:\Users\shanm\Desktop\Inventory\.env`

**Open this file and replace these 3 values:**

```
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

**Example:**
```
EMAIL_HOST_USER=john.doe@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=john.doe@gmail.com
```

---

### Step 2: Get Your Gmail App Password

#### 2a. Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Click **"2-Step Verification"**
3. Follow the setup wizard
4. Use your phone or authenticator app

#### 2b. Generate App Password
1. Still in Security settings
2. Scroll down to **"App passwords"** (appears AFTER enabling 2FA)
3. Click **"App passwords"**
4. You may need to sign in again
5. Select:
   - **App:** Mail
   - **Device:** Other (Custom name)
6. Enter name: **"Spare Parts Inventory"**
7. Click **"Generate"**
8. **COPY THE 16-CHARACTER PASSWORD** (it looks like: abcd efgh ijkl mnop)
9. **Remove the spaces** when pasting into .env file

---

### Step 3: Update Your .env File

1. Open: `C:\Users\shanm\Desktop\Inventory\.env`
2. Replace `your_email@gmail.com` with YOUR Gmail address (in 2 places)
3. Replace `your_16_character_app_password` with the App Password you just generated
4. Save the file

**Your .env should look like:**
```
EMAIL_HOST_USER=yourname@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=yourname@gmail.com
```

---

### Step 4: Restart Django Server

**Stop the server:**
- Press `Ctrl + C` in the terminal running Django

**Start it again:**
```powershell
python manage.py runserver
```

---

### Step 5: Test Email Configuration

1. Open your browser: http://localhost:8000/
2. Login as admin
3. Click **"Test Email"** button
4. Click **"Send Test Email"**
5. Check your inbox! ✉️

---

## 🔧 Troubleshooting

### Still getting "535 Username and Password not accepted"?

✅ **Checklist:**
- [ ] 2-Factor Authentication is enabled on Gmail
- [ ] App Password was generated (not using regular password)
- [ ] App Password has NO SPACES (should be 16 characters)
- [ ] Email address in .env is correct
- [ ] Django server was restarted after editing .env
- [ ] .env file is in the correct location (same folder as manage.py)

### Need More Help?

Visit the comprehensive guide in your app:
- http://localhost:8000/gmail-setup-guide/

Or open the documentation:
- `C:\Users\shanm\Desktop\Inventory\GMAIL_SETUP.md`

---

## 📝 Quick Reference

| What | Where |
|------|-------|
| Edit .env file | `C:\Users\shanm\Desktop\Inventory\.env` |
| Gmail Security Settings | https://myaccount.google.com/security |
| App Passwords | https://myaccount.google.com/apppasswords |
| Test Email Page | http://localhost:8000/test-email/ |
| Gmail Setup Guide | http://localhost:8000/gmail-setup-guide/ |

---

## 🎯 Current Status

✅ `.env` file created
✅ `python-dotenv` installed
✅ Gmail setup guide available
✅ Enhanced error messages enabled

🔴 **TODO:** 
1. Enable 2FA on your Gmail
2. Generate App Password
3. Update .env file
4. Restart Django server
5. Test email!

---

**Need help?** The app now shows detailed error messages with troubleshooting tips!
