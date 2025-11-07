from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('spare/add/', views.sparepart_add, name='spare_add'),
    path('spare/<int:pk>/edit/', views.sparepart_edit, name='spare_edit'),
    path('spare/<int:pk>/delete/', views.sparepart_delete, name='spare_delete'),
    path('spare/<int:pk>/update_quantity/', views.sparepart_update_quantity, name='spare_update_quantity'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/low-stock-csv/', views.export_low_stock_csv, name='export_low_stock_csv'),
    path('import/spare-parts/', views.import_spare_parts, name='import_spare_parts'),
    path('test-email/', views.test_email, name='test_email'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('gmail-setup-guide/', views.gmail_setup_guide, name='gmail_setup_guide'),
    path('send-low-stock-email/', views.send_low_stock_email, name='send_low_stock_email'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]
