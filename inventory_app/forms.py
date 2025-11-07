from django import forms
from .models import SparePart
import os


class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['part_name', 'quantity', 'threshold', 'supplier']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter part name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier name'}),
        }


class LoginRoleForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    role = forms.ChoiceField(
        choices=[('admin', 'Admin'), ('technician', 'Technician')], 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class ImportSparePartsForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls,.json',
            'help_text': 'Upload CSV, Excel, or JSON file with spare parts data'
        }),
        help_text='Supported formats: CSV (.csv), Excel (.xlsx, .xls), JSON (.json)'
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Get file extension
            name, ext = os.path.splitext(file.name.lower())
            valid_extensions = ['.csv', '.xlsx', '.xls', '.json']
            
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid file format. Please upload one of these formats: {", ".join(valid_extensions)}'
                )
            
            # Check file size (max 10MB for Excel files)
            max_size = 10 * 1024 * 1024 if ext in ['.xlsx', '.xls'] else 5 * 1024 * 1024
            if file.size > max_size:
                max_mb = 10 if ext in ['.xlsx', '.xls'] else 5
                raise forms.ValidationError(f'File size must be less than {max_mb}MB.')
        
        return file


class AdminProfileForm(forms.Form):
    """Form for admin users to update their profile information"""
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
