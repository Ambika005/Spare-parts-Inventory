from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import F
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from .models import SparePart
from .forms import SparePartForm, LoginRoleForm, ImportSparePartsForm, AdminProfileForm
from .services import AlertService
import csv
import json
from io import BytesIO, StringIO
from reportlab.pdfgen import canvas
import os
import pandas as pd
from django.db import transaction


def is_admin(user):
    return user.groups.filter(name='Admin').exists() or user.is_staff


def is_technician(user):
    return user.groups.filter(name='Technician').exists()


def login_view(request):
    if request.method == 'POST':
        form = LoginRoleForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                # check role membership
                if role == 'admin' and is_admin(user):
                    login(request, user)
                    return redirect('admin_dashboard')
                if role == 'technician':
                    # Allow any authenticated user to login as technician
                    login(request, user)
                    return redirect('technician_dashboard')
                messages.error(request, 'User does not have the selected role.')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginRoleForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    parts = SparePart.objects.all().order_by('part_name')
    total_parts = parts.count()
    low_stock = parts.filter(quantity__lte=F('threshold')).count()
    well_stocked = total_parts - low_stock
    
    # Get alert information
    active_alerts = AlertService.get_active_alerts()
    recent_alerts = AlertService.get_recent_alerts(days=3)
    
    # Get unique suppliers for filter
    suppliers = SparePart.objects.values_list('supplier', flat=True).distinct().exclude(supplier='')
    
    return render(request, 'admin_dashboard.html', {
        'parts': parts, 
        'total_parts': total_parts,
        'low_stock': low_stock, 
        'well_stocked': well_stocked,
        'active_alerts': active_alerts,
        'recent_alerts': recent_alerts,
        'alert_count': active_alerts.count(),
        'suppliers': suppliers,
    })


@login_required
def technician_dashboard(request):
    parts = SparePart.objects.all().order_by('part_name')
    total_parts = parts.count()
    low = [p for p in parts if p.is_low()]
    low_stock_count = len(low)
    well_stocked = total_parts - low_stock_count
    
    # Get recent alert information (technicians can see recent alerts but not manage them)
    recent_alerts = AlertService.get_recent_alerts(days=1)
    
    return render(request, 'technician_dashboard.html', {
        'parts': parts, 
        'total_parts': total_parts,
        'low_parts': low, 
        'low_stock_count': low_stock_count,
        'well_stocked': well_stocked,
        'recent_alerts': recent_alerts
    })


@login_required
@user_passes_test(is_admin)
def sparepart_add(request):
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        if form.is_valid():
            spare_part = form.save()
            messages.success(request, 'Spare part added')
            
            # Check and send low stock alert if needed
            if AlertService.check_and_send_alert(spare_part):
                messages.warning(request, f'Low stock alert sent for {spare_part.part_name}')
            
            return redirect('admin_dashboard')
    else:
        form = SparePartForm()
    return render(request, 'sparepart_form.html', {'form': form, 'action': 'Add'})


@login_required
@user_passes_test(is_admin)
def sparepart_edit(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        form = SparePartForm(request.POST, instance=part)
        if form.is_valid():
            updated_part = form.save()
            messages.success(request, 'Spare part updated')
            
            # Check and send low stock alert if needed
            if AlertService.check_and_send_alert(updated_part):
                messages.warning(request, f'Low stock alert sent for {updated_part.part_name}')
            
            return redirect('admin_dashboard')
    else:
        form = SparePartForm(instance=part)
    return render(request, 'sparepart_form.html', {'form': form, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin)
def sparepart_delete(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        part.delete()
        messages.success(request, 'Spare part deleted')
        return redirect('admin_dashboard')
    return render(request, 'sparepart_form.html', {'form': None, 'action': 'Delete', 'part': part})


@login_required
def sparepart_update_quantity(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        qty = int(request.POST.get('quantity', part.quantity))
        old_quantity = part.quantity
        
        if action == 'use':
            part.quantity = max(0, part.quantity - qty)
            messages.success(request, f'Marked {qty} as used')
        elif action == 'restock':
            part.quantity = part.quantity + qty
            messages.success(request, f'Added {qty} to stock')
        elif action == 'set':
            part.quantity = qty
            messages.success(request, 'Quantity updated')
        
        part.save()
        
        # Check and send low stock alert if needed
        if part.quantity != old_quantity:
            if AlertService.check_and_send_alert(part):
                messages.warning(request, f'Low stock alert sent for {part.part_name}')
        
        return redirect('technician_dashboard')
    return render(request, 'sparepart_form.html', {'form': None, 'action': 'Update Quantity', 'part': part})


@login_required
@user_passes_test(is_admin)
def export_csv(request):
    parts = SparePart.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spareparts.csv"'
    writer = csv.writer(response)
    writer.writerow(['Part Name', 'Quantity', 'Threshold', 'Supplier', 'Updated At'])
    for p in parts:
        writer.writerow([p.part_name, p.quantity, p.threshold, p.supplier, p.updated_at])
    return response


@login_required
@user_passes_test(is_admin)
def export_low_stock_csv(request):
    """
    Export a CSV with only low stock items (quantity < threshold).
    File name: low_stock_items.csv
    Columns: Part Name, Quantity, Threshold, Supplier
    """
    # Use F expression to compare quantity and threshold at the DB level
    low_parts = SparePart.objects.filter(quantity__lt=F('threshold')).order_by('part_name')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="low_stock_items.csv"'
    writer = csv.writer(response)
    writer.writerow(['Part Name', 'Quantity', 'Threshold', 'Supplier'])
    for p in low_parts:
        writer.writerow([p.part_name, p.quantity, p.threshold, p.supplier])
    return response


@login_required
@user_passes_test(is_admin)
def import_spare_parts(request):
    """
    Import spare parts from CSV, Excel, or JSON file.
    Expected columns: Part Name, Quantity, Threshold, Supplier
    """
    if request.method == 'POST':
        form = ImportSparePartsForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            try:
                # Determine file type
                name, ext = os.path.splitext(file.name.lower())
                
                # Parse data based on file type
                data_rows = []
                
                if ext == '.csv':
                    # Handle CSV files with multiple encodings
                    try:
                        file_content = file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        file.seek(0)
                        try:
                            file_content = file.read().decode('latin-1')
                        except:
                            file.seek(0)
                            file_content = file.read().decode('cp1252')
                    
                    csv_data = StringIO(file_content)
                    # Try different delimiters
                    try:
                        reader = csv.DictReader(csv_data)
                        data_rows = list(reader)
                    except:
                        csv_data.seek(0)
                        reader = csv.DictReader(csv_data, delimiter=';')
                        data_rows = list(reader)
                    
                elif ext in ['.xlsx', '.xls', '.xlsm']:
                    # Handle Excel files using pandas
                    try:
                        df = pd.read_excel(file, engine='openpyxl' if ext in ['.xlsx', '.xlsm'] else 'xlrd')
                    except:
                        # Try without specifying engine
                        file.seek(0)
                        df = pd.read_excel(file)
                    
                    # Convert DataFrame to list of dictionaries
                    data_rows = df.to_dict('records')
                    
                elif ext == '.json':
                    # Handle JSON files
                    file_content = file.read().decode('utf-8')
                    json_data = json.loads(file_content)
                    
                    # Support both array of objects and single object with array
                    if isinstance(json_data, dict) and 'parts' in json_data:
                        data_rows = json_data['parts']
                    elif isinstance(json_data, dict) and 'data' in json_data:
                        data_rows = json_data['data']
                    elif isinstance(json_data, list):
                        data_rows = json_data
                    else:
                        messages.error(request, 'JSON format not recognized. Expected array of objects or object with "parts"/"data" array.')
                        return render(request, 'import_spare_parts.html', {'form': form})
                
                elif ext == '.txt':
                    # Handle tab-separated or pipe-separated text files
                    file_content = file.read().decode('utf-8')
                    txt_data = StringIO(file_content)
                    
                    # Try tab-separated first, then pipe-separated
                    try:
                        reader = csv.DictReader(txt_data, delimiter='\t')
                        data_rows = list(reader)
                    except:
                        txt_data.seek(0)
                        reader = csv.DictReader(txt_data, delimiter='|')
                        data_rows = list(reader)
                        
                else:
                    messages.error(request, f'Unsupported file format: {ext}. Supported formats: CSV, Excel (.xlsx, .xls), JSON, TXT')
                    return render(request, 'import_spare_parts.html', {'form': form})
                
                if not data_rows:
                    messages.warning(request, 'No data found in the uploaded file.')
                    return render(request, 'import_spare_parts.html', {'form': form})
                
                # Normalize column names (case-insensitive matching with multiple variations)
                expected_columns = {
                    'part name': ['part name', 'partname', 'part', 'name', 'item', 'product'],
                    'quantity': ['quantity', 'qty', 'stock', 'amount', 'count'],
                    'threshold': ['threshold', 'min', 'minimum', 'reorder', 'reorder point', 'min stock'],
                    'supplier': ['supplier', 'vendor', 'manufacturer', 'source']
                }
                
                # Get column names from first row
                if data_rows:
                    first_row = data_rows[0]
                    actual_columns = {str(col).lower().strip(): col for col in first_row.keys()}
                    
                    # Check for required columns and create mapping
                    column_mapping = {}
                    missing_columns = []
                    
                    for field, variations in expected_columns.items():
                        found = False
                        for variation in variations:
                            if variation in actual_columns:
                                column_mapping[field] = actual_columns[variation]
                                found = True
                                break
                        if not found:
                            # Only mark as missing if it's truly required (part name and quantity are essential)
                            if field in ['part name', 'quantity']:
                                missing_columns.append(field)
                    
                    if missing_columns:
                        available_cols = list(first_row.keys())
                        messages.error(request, 
                            f'Missing required columns: {", ".join(missing_columns)}. '
                            f'Available columns: {", ".join(available_cols)}. '
                            f'Required: Part Name, Quantity. Optional: Threshold, Supplier.')
                        return render(request, 'import_spare_parts.html', {'form': form})
                
                # Process and import data
                imported_count = 0
                updated_count = 0
                skipped_count = 0
                errors = []
                
                with transaction.atomic():  # Use database transaction for consistency
                    for index, row in enumerate(data_rows):
                        row_number = index + 2  # Account for header row
                        try:
                            # Extract data using column mapping with fallbacks
                            part_name = str(row.get(column_mapping.get('part name', 'part name'), '')).strip()
                            quantity_raw = row.get(column_mapping.get('quantity', 'quantity'), 0)
                            threshold_raw = row.get(column_mapping.get('threshold', 'threshold'), 10)  # Default threshold
                            supplier_raw = row.get(column_mapping.get('supplier', 'supplier'), '')
                            
                            # Skip empty rows
                            if not part_name or part_name.lower() in ['', 'nan', 'none', 'null']:
                                skipped_count += 1
                                continue
                            
                            # Convert to integers, handling pandas NaN and various formats
                            try:
                                if pd.isna(quantity_raw) or quantity_raw == '':
                                    quantity = 0
                                else:
                                    # Remove commas and convert
                                    quantity_str = str(quantity_raw).replace(',', '').strip()
                                    quantity = int(float(quantity_str))
                                    
                                if pd.isna(threshold_raw) or threshold_raw == '':
                                    threshold = 10  # Default threshold
                                else:
                                    threshold_str = str(threshold_raw).replace(',', '').strip()
                                    threshold = int(float(threshold_str))
                                    
                            except (ValueError, TypeError) as e:
                                errors.append(f'Row {row_number}: Invalid number format - {str(e)}')
                                continue
                            
                            # Validate data
                            if quantity < 0 or threshold < 0:
                                errors.append(f'Row {row_number}: Quantity and threshold must be non-negative')
                                continue
                            
                            # Handle supplier field
                            supplier = str(supplier_raw).strip() if supplier_raw and not pd.isna(supplier_raw) else ''
                            if supplier.lower() in ['nan', 'none', 'null']:
                                supplier = ''
                            
                            # Create or update spare part
                            spare_part, created = SparePart.objects.get_or_create(
                                part_name=part_name,
                                defaults={
                                    'quantity': quantity,
                                    'threshold': threshold,
                                    'supplier': supplier
                                }
                            )
                            
                            if created:
                                imported_count += 1
                            else:
                                # Update existing part
                                spare_part.quantity = quantity
                                spare_part.threshold = threshold
                                if supplier:  # Only update supplier if provided
                                    spare_part.supplier = supplier
                                spare_part.save()
                                updated_count += 1
                            
                            # Check and send low stock alert if needed
                            AlertService.check_and_send_alert(spare_part)
                        
                        except Exception as e:
                            errors.append(f'Row {row_number}: Error - {str(e)}')
                            continue
                
                # Display results
                if imported_count > 0 or updated_count > 0:
                    success_msg = f'✅ Import completed! {imported_count} new parts added, {updated_count} parts updated'
                    if skipped_count > 0:
                        success_msg += f', {skipped_count} rows skipped (empty)'
                    messages.success(request, success_msg)
                else:
                    messages.warning(request, '⚠️ No parts were imported. Please check your file format and data.')
                
                if errors:
                    error_msg = f'⚠️ {len(errors)} errors: ' + '; '.join(errors[:3])
                    if len(errors) > 3:
                        error_msg += f' ... and {len(errors) - 3} more.'
                    messages.warning(request, error_msg)
                
                return redirect('admin_dashboard')
                
            except json.JSONDecodeError as e:
                messages.error(request, f'❌ Invalid JSON format: {str(e)}')
                return render(request, 'import_spare_parts.html', {'form': form})
            except pd.errors.ParserError as e:
                messages.error(request, f'❌ Error parsing file: {str(e)}')
                return render(request, 'import_spare_parts.html', {'form': form})
            except Exception as e:
                messages.error(request, f'❌ Error processing file: {str(e)}. Please ensure the file contains "Part Name" and "Quantity" columns.')
                return render(request, 'import_spare_parts.html', {'form': form})
    else:
        form = ImportSparePartsForm()
    
    return render(request, 'import_spare_parts.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def test_email(request):
    """Test email configuration by sending a test email"""
    admin_emails = AlertService._get_admin_email_addresses()
    
    if request.method == 'POST':
        success, message, recipients = AlertService.test_email_configuration()
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('admin_dashboard')
    
    # Show test email form with current recipients
    context = {
        'admin_emails': admin_emails,
        'email_configured': bool(admin_emails)
    }
    return render(request, 'test_email.html', context)


@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    """Admin profile management for email configuration"""
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            messages.success(request, 'Profile updated successfully! You will now receive email alerts.')
            return redirect('admin_dashboard')
    else:
        form = AdminProfileForm(user=request.user)
    
    return render(request, 'admin_profile.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def export_pdf(request):
    parts = SparePart.objects.all()
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont('Helvetica', 12)
    y = 800
    p.drawString(40, y, 'Spare Parts Report')
    y -= 30
    for part in parts:
        line = f"{part.part_name} - Qty: {part.quantity} - Threshold: {part.threshold} - Supplier: {part.supplier}"
        p.drawString(40, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
@user_passes_test(is_admin)
def gmail_setup_guide(request):
    """Display Gmail setup guide"""
    # Get current email configuration for display
    email_config = {
        'host': getattr(settings, 'EMAIL_HOST', None),
        'port': getattr(settings, 'EMAIL_PORT', None),
        'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
        'host_user': getattr(settings, 'EMAIL_HOST_USER', None),
        'host_password': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
    }
    
    context = {
        'email_config': email_config
    }
    
    return render(request, 'gmail_setup_guide.html', context)


def send_low_stock_email(request):
    """
    Simple view to send a low stock alert email directly
    No authentication required for easy testing
    """
    try:
        from django.core.mail import send_mail
        
        # Hardcoded recipient email
        recipient_email = 'ambikaselvaraj22@gmail.com'
        
        # Email content
        subject = '🔔 Low Stock Alert - Spare Parts Inventory'
        message = """
Hello!

This is an important alert from your Spare Parts Inventory System.

⚠️ URGENT ATTENTION REQUIRED ⚠️

There are 42 low stock items in the inventory requiring attention.

These items have fallen below their minimum threshold levels and need immediate restocking to avoid potential shortages.

Action Required:
• Review the low stock items in the inventory dashboard
• Contact suppliers for urgent restocking
• Prioritize critical spare parts for immediate ordering

Please log in to the inventory system to view the complete list of low stock items and take necessary action.

---
This is an automated alert from Spare Parts Inventory System.
Sent to: ambikaselvaraj22@gmail.com

If you receive this email, your Gmail SMTP configuration is working correctly! ✅
        """
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        # Success response
        return HttpResponse("""
        <html>
        <head>
            <title>Email Sent Successfully!</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .success-box {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                .checkmark {
                    font-size: 80px;
                    color: #28a745;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                .email {
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                    color: #333;
                }
                .btn {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }
                .btn:hover {
                    background: #764ba2;
                }
            </style>
        </head>
        <body>
            <div class="success-box">
                <div class="checkmark">✅</div>
                <h1>Email Sent Successfully!</h1>
                <p>A low stock alert email has been sent to:</p>
                <div class="email">ambikaselvaraj22@gmail.com</div>
                <p>Check your inbox to verify the email was received.</p>
                <p><small>If you don't see it, check your spam folder.</small></p>
                <a href="/admin_dashboard/" class="btn">Back to Dashboard</a>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        # Error response with helpful message
        error_msg = str(e)
        return HttpResponse(f"""
        <html>
        <head>
            <title>Email Failed</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                }}
                .error-box {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 600px;
                }}
                .error-icon {{
                    font-size: 80px;
                    color: #dc3545;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #dc3545;
                    margin-bottom: 20px;
                }}
                .error-details {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #dc3545;
                    margin: 20px 0;
                    text-align: left;
                    font-family: monospace;
                    font-size: 14px;
                    color: #333;
                }}
                .help-text {{
                    color: #666;
                    margin-top: 20px;
                    line-height: 1.6;
                }}
                .btn {{
                    display: inline-block;
                    margin: 10px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }}
                .btn:hover {{
                    background: #764ba2;
                }}
                .btn-secondary {{
                    background: #6c757d;
                }}
                .btn-secondary:hover {{
                    background: #5a6268;
                }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <div class="error-icon">❌</div>
                <h1>Failed to Send Email</h1>
                <div class="error-details">{error_msg}</div>
                <div class="help-text">
                    <strong>Common Solutions:</strong><br>
                    ✓ Make sure you've added your Gmail App Password to the .env file<br>
                    ✓ Restart Django server after updating .env file<br>
                    ✓ Enable 2-Factor Authentication on Gmail<br>
                    ✓ Generate App Password from Google Account settings<br>
                </div>
                <div>
                    <a href="/gmail-setup-guide/" class="btn">Gmail Setup Guide</a>
                    <a href="/admin_dashboard/" class="btn btn-secondary">Back to Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """)


@login_required
@user_passes_test(is_admin)
def chart_data_api(request):
    """API endpoint to get chart data in JSON format for dynamic filtering"""
    from django.http import JsonResponse
    
    supplier_filter = request.GET.get('supplier', 'all')
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    parts = SparePart.objects.all()
    
    # Apply filters
    if supplier_filter and supplier_filter != 'all':
        parts = parts.filter(supplier=supplier_filter)
    
    if status_filter == 'low':
        parts = parts.filter(quantity__lt=F('threshold'))
    elif status_filter == 'normal':
        parts = parts.filter(quantity__gte=F('threshold'))
    
    # Prepare data for charts
    parts_list = list(parts.values('part_name', 'quantity', 'threshold', 'supplier'))
    
    # Calculate supplier stats
    from django.db.models import Sum, Count
    supplier_stats = parts.values('supplier').annotate(
        total_quantity=Sum('quantity'),
        part_count=Count('id')
    ).order_by('-total_quantity')
    
    # Calculate KPIs
    total_parts = parts.count()
    low_stock_count = parts.filter(quantity__lt=F('threshold')).count()
    suppliers_count = parts.values('supplier').distinct().count()
    
    data = {
        'parts': parts_list,
        'supplier_stats': list(supplier_stats),
        'kpis': {
            'total_parts': total_parts,
            'low_stock': low_stock_count,
            'well_stocked': total_parts - low_stock_count,
            'suppliers_count': suppliers_count,
            'health_percentage': round((total_parts - low_stock_count) / total_parts * 100 if total_parts > 0 else 0, 1)
        }
    }
    
    return JsonResponse(data)
