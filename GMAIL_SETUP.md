# Gmail Setup Guide for Spare Parts Inventory System

This guide will help you configure Gmail SMTP for email alerts in the Spare Parts Inventory System.

## Prerequisites

- Active Gmail account
- Access to Google Account settings
- Admin access to the Django application

## Step-by-Step Setup

### 1. Enable 2-Factor Authentication

**Why it's required:** Gmail requires 2-Factor Authentication (2FA) to generate App Passwords, which are necessary for third-party applications to send emails.

1. Go to your [Google Account](https://myaccount.google.com/)
2. Click **"Security"** in the left sidebar
3. Under "Signing in to Google", click **"2-Step Verification"**
4. Click **"Get Started"** and follow the prompts
5. Choose your verification method (phone number or authenticator app)
6. Complete the setup process

### 2. Generate Gmail App Password

**Important:** You MUST use an App Password, not your regular Gmail password!

1. Still in Google Account → **Security**
2. Under "Signing in to Google", click **"App passwords"**
   - If you don't see this option, make sure 2FA is enabled first
3. You may need to enter your Gmail password again
4. In the "Select app" dropdown, choose **"Mail"**
5. In the "Select device" dropdown, choose **"Other (Custom name)"**
6. Enter a name: **"Spare Parts Inventory"**
7. Click **"Generate"**
8. **COPY the 16-character password immediately!**
   - Format: `abcd efgh ijkl mnop`
   - You won't be able to see it again
   - Remove spaces when using it

### 3. Configure Environment Variables

#### Option A: Using .env file (Recommended for Development)

1. Create a `.env` file in your project root directory (same level as `manage.py`):

```bash
# .env file
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

2. **Replace the values:**
   - `your_email@gmail.com` → Your actual Gmail address
   - `abcdefghijklmnop` → The 16-character App Password (no spaces!)

3. **Security Warning:** Add `.env` to your `.gitignore` file to prevent committing sensitive credentials:

```bash
# Add to .gitignore
.env
*.env
```

#### Option B: Environment Variables (Recommended for Production)

**Windows PowerShell:**
```powershell
$env:EMAIL_HOST_USER="your_email@gmail.com"
$env:EMAIL_HOST_PASSWORD="abcdefghijklmnop"
$env:DEFAULT_FROM_EMAIL="your_email@gmail.com"
```

**Linux/Mac:**
```bash
export EMAIL_HOST_USER="your_email@gmail.com"
export EMAIL_HOST_PASSWORD="abcdefghijklmnop"
export DEFAULT_FROM_EMAIL="your_email@gmail.com"
```

### 4. Verify settings.py Configuration

Ensure your `settings.py` file has the following configuration:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your_gmail_id@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_app_password')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
```

### 5. Install python-dotenv

If using `.env` file, install the required package:

```bash
pip install python-dotenv
```

### 6. Configure Admin Email Recipients

Email alerts are sent to users in the **Admin** group who have email addresses configured:

1. Log in to Django Admin: `http://localhost:8000/admin/`
2. Navigate to **Users**
3. For each admin user:
   - Click on the username
   - Scroll to "Personal info" section
   - Add/update the **Email address** field
   - Ensure the user is in the **Admin** group
   - Click **Save**

### 7. Restart Django Server

After configuring environment variables, restart your Django development server:

```bash
# Stop the server (Ctrl+C)
# Then start it again
python manage.py runserver
```

### 8. Test Email Configuration

1. Log in as an admin user
2. Go to **Admin Dashboard**
3. Click **"Admin Profile"** in the top navigation
4. Click **"Send Test Email"** button
5. Check your inbox for the test email

Alternatively, visit: `http://localhost:8000/test-email/`

## Troubleshooting

### Error 535: Username and Password not accepted

**Causes:**
- Using regular Gmail password instead of App Password
- App Password copied with spaces
- Typo in email address or App Password
- 2-Factor Authentication not enabled

**Solutions:**
1. Double-check you're using the **App Password**, not your regular password
2. Remove all spaces from the App Password (should be 16 characters)
3. Verify `EMAIL_HOST_USER` matches your Gmail address exactly
4. Ensure 2FA is enabled on your Gmail account
5. Generate a new App Password and try again

### Connection Refused / Timeout Errors

**Causes:**
- Firewall blocking port 587
- Network restrictions
- Internet connectivity issues

**Solutions:**
1. Check your internet connection
2. Try from a different network
3. Check firewall settings (allow outbound port 587)
4. If on corporate network, contact IT support

### Environment Variables Not Loading

**Check:**
1. `.env` file is in the project root (same directory as `manage.py`)
2. No spaces around `=` in `.env` file
3. Django server was restarted after creating/modifying `.env`
4. `python-dotenv` is installed: `pip install python-dotenv`
5. `settings.py` has:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### No Admin Email Addresses Found

**Solutions:**
1. Ensure admin users have email addresses in their profiles
2. Go to Django Admin → Users → [Select User] → Add email
3. Verify users are in the "Admin" group
4. Re-test email configuration

## Configuration Validation Checklist

Use this checklist to verify your setup:

- [ ] 2-Factor Authentication enabled on Gmail
- [ ] Gmail App Password generated
- [ ] `.env` file created with correct values
- [ ] `.env` added to `.gitignore`
- [ ] `python-dotenv` installed
- [ ] Django server restarted
- [ ] Admin users have email addresses configured
- [ ] Admin users are in "Admin" group
- [ ] Test email sent successfully

## Additional Resources

- [Google Account Settings](https://myaccount.google.com/)
- [Gmail App Passwords Help](https://support.google.com/accounts/answer/185833)
- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)

## Security Best Practices

1. **Never commit credentials to version control**
   - Always use `.env` files or environment variables
   - Add `.env` to `.gitignore`

2. **Use App Passwords, not regular passwords**
   - App Passwords are more secure
   - Can be revoked individually

3. **Rotate App Passwords periodically**
   - Generate new App Passwords every few months
   - Revoke old ones from Google Account settings

4. **Limit access to production credentials**
   - Use different App Passwords for development and production
   - Document who has access to credentials

## Need Help?

If you're still experiencing issues after following this guide:

1. Check the detailed setup guide in the application: `/gmail-setup-guide/`
2. Review error messages carefully
3. Verify all steps were completed correctly
4. Ensure your Gmail account is not restricted or suspended

## Quick Reference

### Gmail SMTP Settings

| Setting | Value |
|---------|-------|
| SMTP Server | smtp.gmail.com |
| Port | 587 |
| Encryption | TLS |
| Authentication | Required |
| Username | Your Gmail address |
| Password | App Password (16 characters) |

### Environment Variables Required

```
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

---

**Last Updated:** January 2025
