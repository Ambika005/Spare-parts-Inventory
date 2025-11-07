# 🔐 LOGIN CREDENTIALS - Inventory Management System

## Test Users Available

### 👨‍💼 ADMIN USERS (Full Access)

1. **Admin Account**
   - Username: `admin`
   - Password: `admin123`
   - Role: Select **Admin** at login
   - Access: Full admin dashboard, all features

2. **Ambika Account**
   - Username: `Ambika`
   - Password: `password123`
   - Role: Select **Admin** at login
   - Access: Full admin dashboard, all features

---

### 🔧 TECHNICIAN USERS (Limited Access)

1. **Tech Account**
   - Username: `tech`
   - Password: `tech123`
   - Role: Select **Technician** at login
   - Access: View inventory, update quantities

2. **Technician Account**
   - Username: `technician`
   - Password: (You need to set this - see below)
   - Role: Select **Technician** at login
   - Access: View inventory, update quantities

---

## 🚀 How to Login

1. Go to: http://127.0.0.1:8000/
2. Enter **Username**
3. Enter **Password**
4. Select **Role** (Admin or Technician)
5. Click **Login**

---

## ⚠️ Troubleshooting "Invalid Credentials" Error

If you get "Invalid credentials" error, it means:

### ❌ Common Issues:
1. **Wrong password** - Passwords are case-sensitive
2. **Wrong username** - Usernames are case-sensitive
3. **User doesn't exist** - Use one of the accounts above
4. **Account is inactive** - All accounts above are active

### ✅ Quick Solutions:

#### Solution 1: Use Test Accounts
Just use the accounts listed above with exact credentials.

#### Solution 2: Reset Any User's Password
Run this command (replace USERNAME and NEWPASSWORD):
```bash
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='USERNAME'); u.set_password('NEWPASSWORD'); u.save(); print('Password reset!')"
```

Example:
```bash
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='technician'); u.set_password('tech123'); u.save(); print('Password reset!')"
```

#### Solution 3: Create New User
Run the setup script again:
```bash
python create_test_users.py
```

#### Solution 4: Create User via Django Admin
1. Start server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with superuser (admin/admin123)
4. Create new user manually

---

## 🔧 User Management Commands

### List All Users
```bash
python manage.py shell -c "from django.contrib.auth.models import User; [print(f'{u.username} - Active: {u.is_active}') for u in User.objects.all()]"
```

### Create New Admin User
```bash
python manage.py createsuperuser
```

### Reset Password for Specific User
```bash
python manage.py changepassword USERNAME
```

---

## 📝 Notes

- **Admin Role**: Can access admin dashboard, add/edit/delete parts, import/export, manage email alerts
- **Technician Role**: Can view inventory, update quantities only
- **Passwords**: All test passwords are simple for testing only
- **Production**: Change all passwords before deploying to production!

---

## 🎯 Quick Test

Try these credentials right now:

```
Username: admin
Password: admin123
Role: Admin
```

Should work immediately! ✅

---

**Last Updated**: November 7, 2025
**Status**: All accounts active and ready to use
