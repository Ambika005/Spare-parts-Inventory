# Spare Parts Inventory Monitor

A small Django app with two roles: Admin and Technician.

Quick start (Windows PowerShell):

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install requirements:

```powershell
python -m pip install -r requirements.txt
```

3. Run migrations and create a superuser:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Create Groups (Admin and Technician) and assign users to them. You can do that via Django admin at http://127.0.0.1:8000/admin/ after running the dev server.

5. Run dev server:

```powershell
python manage.py runserver
```

Notes:
- Login page is at `/` and allows selecting role (Admin or Technician). The backend checks that the authenticated user belongs to the selected role's Group (or is_staff for admins).
- Admin dashboard has CRUD for spare parts and CSV/PDF export. PDF export uses `reportlab`.
- Technician dashboard allows updating quantities and marks low-stock items.

Next steps / improvements:
- Add unit tests and automation for creating default groups during migrations.
- Implement approval workflow for technician updates.
- Add richer analytics UI (charts) and scheduled low-stock email/SMS alerts.
